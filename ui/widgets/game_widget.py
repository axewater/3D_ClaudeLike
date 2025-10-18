"""
Main game rendering widget with mouse interaction and A* pathfinding
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPolygon
import heapq

import constants as c
from game import Game
import graphics as gfx


class GameWidget(QWidget):
    """Widget for rendering the game grid"""
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.setFixedSize(c.VIEWPORT_WIDTH * c.TILE_SIZE, c.VIEWPORT_HEIGHT * c.TILE_SIZE)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(f"background-color: rgb({c.COLOR_FLOOR.red()}, {c.COLOR_FLOOR.green()}, {c.COLOR_FLOOR.blue()});")

        # Mouse tracking for hover effects
        self.setMouseTracking(True)
        self.hover_world_x = None
        self.hover_world_y = None

        # Ability targeting mode
        self.targeting_mode = False
        self.targeting_ability_index = None

    def paintEvent(self, event):
        """Render the game grid"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.game.dungeon:
            return

        # Apply screen shake offset
        shake_x, shake_y = self.game.anim_manager.get_screen_offset()
        painter.translate(shake_x, shake_y)

        # Fill entire viewport with black background (for out-of-bounds areas and fog of war)
        painter.fillRect(0, 0,
                        c.VIEWPORT_WIDTH * c.TILE_SIZE,
                        c.VIEWPORT_HEIGHT * c.TILE_SIZE,
                        QColor(0, 0, 0))

        # Draw fog particles (atmospheric smoke layer in darkness)
        from PyQt6.QtGui import QRadialGradient
        for fog in self.game.anim_manager.fog_particles:
            # Fog particles use screen pixel coordinates (not world coords)
            # They float across the viewport regardless of camera position

            # Only draw if within viewport (with margin)
            if not (-fog.size <= fog.x < c.VIEWPORT_WIDTH * c.TILE_SIZE + fog.size and
                    -fog.size <= fog.y < c.VIEWPORT_HEIGHT * c.TILE_SIZE + fog.size):
                continue

            # Create soft, blurred fog with radial gradient
            gradient = QRadialGradient(fog.x, fog.y, fog.size / 2)
            fog_color_center = QColor(fog.color.red(), fog.color.green(),
                                     fog.color.blue(), fog.alpha)
            fog_color_edge = QColor(fog.color.red(), fog.color.green(),
                                   fog.color.blue(), 0)  # Fade to transparent

            gradient.setColorAt(0, fog_color_center)
            gradient.setColorAt(1, fog_color_edge)

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(fog.x - fog.size / 2),
                              int(fog.y - fog.size / 2),
                              int(fog.size), int(fog.size))

        # Draw tiles with graphics (only visible viewport)
        for screen_y in range(c.VIEWPORT_HEIGHT):
            for screen_x in range(c.VIEWPORT_WIDTH):
                # Convert screen coords to world coords
                world_x = screen_x + self.game.camera_x
                world_y = screen_y + self.game.camera_y

                # Check bounds
                if not (0 <= world_x < c.GRID_WIDTH and 0 <= world_y < c.GRID_HEIGHT):
                    continue

                # Check visibility state
                if self.game.visibility_map:
                    vis_state = self.game.visibility_map.get_state(world_x, world_y)
                else:
                    vis_state = c.VISIBILITY_VISIBLE  # Fallback if no visibility map

                # Skip unexplored tiles (pure black / fog of war)
                if vis_state == c.VISIBILITY_UNEXPLORED:
                    continue

                tile = self.game.dungeon.get_tile(world_x, world_y)

                # Determine if we should apply fog (explored but not visible)
                apply_fog = (vis_state == c.VISIBILITY_EXPLORED)

                # Get current biome for tile rendering
                biome = self.game.dungeon.biome if self.game.dungeon else c.BIOME_DUNGEON

                if tile == c.TILE_WALL:
                    if apply_fog:
                        self._draw_fogged_wall(painter, screen_x, screen_y)
                    else:
                        gfx.draw_wall_tile(painter, screen_x, screen_y, c.TILE_SIZE, biome)
                elif tile == c.TILE_FLOOR:
                    if apply_fog:
                        self._draw_fogged_floor(painter, screen_x, screen_y)
                    else:
                        gfx.draw_floor_tile(painter, screen_x, screen_y, c.TILE_SIZE, biome)
                elif tile == c.TILE_STAIRS:
                    if apply_fog:
                        self._draw_fogged_floor(painter, screen_x, screen_y)
                        self._draw_fogged_stairs(painter, screen_x, screen_y)
                    else:
                        gfx.draw_floor_tile(painter, screen_x, screen_y, c.TILE_SIZE, biome)  # Draw floor underneath
                        gfx.draw_stairs_tile(painter, screen_x, screen_y, c.TILE_SIZE, biome)

        # Draw entities with graphics using display positions
        # Collect all entities to draw
        entities_to_draw = []

        # Add items (draw first, bottom layer) - only if visible
        for item in self.game.items:
            # Only show items in visible tiles
            if self.game.visibility_map and not self.game.visibility_map.is_visible(item.x, item.y):
                continue
            display_x, display_y = item.get_display_pos()
            entities_to_draw.append((item, display_x, display_y, 0))  # Priority 0 (bottom)

        # Add enemies (middle layer) - only if visible
        for enemy in self.game.enemies:
            # Only show enemies in visible tiles
            if self.game.visibility_map and not self.game.visibility_map.is_visible(enemy.x, enemy.y):
                continue
            display_x, display_y = enemy.get_display_pos()
            entities_to_draw.append((enemy, display_x, display_y, 1))  # Priority 1

        # Add player (top layer) - always visible
        if self.game.player:
            display_x, display_y = self.game.player.get_display_pos()
            entities_to_draw.append((self.game.player, display_x, display_y, 2))  # Priority 2 (top)

        # Sort by y position for proper depth, then by priority
        entities_to_draw.sort(key=lambda e: (e[2], e[3]))

        # Draw each entity at its display position
        for entity, display_x, display_y, _ in entities_to_draw:
            # Convert world display coords to screen coords
            screen_x = display_x - self.game.camera_x
            screen_y = display_y - self.game.camera_y

            # Only draw if visible (with some margin for bob animation)
            if not (-1 <= screen_x < c.VIEWPORT_WIDTH + 1 and -1 <= screen_y < c.VIEWPORT_HEIGHT + 1):
                continue

            color = self._get_entity_color(entity)

            if entity.entity_type == c.ENTITY_PLAYER:
                gfx.draw_player(painter, screen_x, screen_y, c.TILE_SIZE, color, entity.class_type, entity.facing_direction, entity.idle_time)
            elif entity.entity_type == c.ENTITY_ENEMY:
                gfx.draw_enemy(painter, screen_x, screen_y, c.TILE_SIZE, color, entity.enemy_type, entity.facing_direction, entity.idle_time)
            elif entity.entity_type == c.ENTITY_ITEM:
                gfx.draw_item(painter, screen_x, screen_y, c.TILE_SIZE, color, entity.item_type, entity.rarity)

        # Draw enemy health bars
        self._draw_enemy_health_bars(painter)

        # Draw flash effects (before other animations)
        for flash in self.game.anim_manager.flash_effects:
            # Convert to screen coords
            screen_x = flash.x - self.game.camera_x
            screen_y = flash.y - self.game.camera_y

            # Only draw if visible
            if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
                continue

            flash_color = QColor(flash.color.red(), flash.color.green(), flash.color.blue(), flash.alpha)
            painter.fillRect(
                screen_x * c.TILE_SIZE,
                screen_y * c.TILE_SIZE,
                c.TILE_SIZE,
                c.TILE_SIZE,
                flash_color
            )

        # Draw ambient particles (background layer)
        for particle in self.game.anim_manager.ambient_particles:
            # Convert pixel coords to screen space
            screen_pixel_x = particle.x - (self.game.camera_x * c.TILE_SIZE)
            screen_pixel_y = particle.y - (self.game.camera_y * c.TILE_SIZE)

            # Only draw if within viewport bounds
            if not (0 <= screen_pixel_x < c.VIEWPORT_WIDTH * c.TILE_SIZE and
                    0 <= screen_pixel_y < c.VIEWPORT_HEIGHT * c.TILE_SIZE):
                continue

            particle_color = QColor(particle.color.red(), particle.color.green(),
                                   particle.color.blue(), particle.alpha)
            painter.setBrush(particle_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(screen_pixel_x - particle.size / 2),
                              int(screen_pixel_y - particle.size / 2),
                              int(particle.size), int(particle.size))

        # Draw trail effects
        for trail in self.game.anim_manager.trails:
            # Convert to screen coords
            screen_x = trail.x - self.game.camera_x
            screen_y = trail.y - self.game.camera_y

            # Only draw if visible
            if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
                continue

            trail_color = QColor(trail.color.red(), trail.color.green(),
                               trail.color.blue(), trail.alpha)
            painter.setBrush(trail_color)
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw as fading circle
            painter.drawEllipse(int(screen_x * c.TILE_SIZE + c.TILE_SIZE / 2 - trail.size / 2),
                              int(screen_y * c.TILE_SIZE + c.TILE_SIZE / 2 - trail.size / 2),
                              int(trail.size), int(trail.size))

        # Draw regular particles
        for particle in self.game.anim_manager.particles:
            # Convert pixel coords to screen space
            screen_pixel_x = particle.x - (self.game.camera_x * c.TILE_SIZE)
            screen_pixel_y = particle.y - (self.game.camera_y * c.TILE_SIZE)

            # Only draw if within viewport bounds
            if not (0 <= screen_pixel_x < c.VIEWPORT_WIDTH * c.TILE_SIZE and
                    0 <= screen_pixel_y < c.VIEWPORT_HEIGHT * c.TILE_SIZE):
                continue

            particle_color = QColor(particle.color.red(), particle.color.green(),
                                   particle.color.blue(), particle.alpha)
            painter.setBrush(particle_color)
            painter.setPen(Qt.PenStyle.NoPen)

            if particle.particle_type == "circle":
                painter.drawEllipse(int(screen_pixel_x - particle.size / 2),
                                  int(screen_pixel_y - particle.size / 2),
                                  int(particle.size), int(particle.size))
            else:  # square or star
                painter.fillRect(int(screen_pixel_x - particle.size / 2),
                               int(screen_pixel_y - particle.size / 2),
                               int(particle.size), int(particle.size),
                               particle_color)

        # Draw directional particles
        for particle in self.game.anim_manager.directional_particles:
            # Convert pixel coords to screen space
            screen_pixel_x = particle.x - (self.game.camera_x * c.TILE_SIZE)
            screen_pixel_y = particle.y - (self.game.camera_y * c.TILE_SIZE)

            # Only draw if within viewport bounds
            if not (0 <= screen_pixel_x < c.VIEWPORT_WIDTH * c.TILE_SIZE and
                    0 <= screen_pixel_y < c.VIEWPORT_HEIGHT * c.TILE_SIZE):
                continue

            particle_color = QColor(particle.color.red(), particle.color.green(),
                                   particle.color.blue(), particle.alpha)
            painter.setBrush(particle_color)
            painter.setPen(Qt.PenStyle.NoPen)

            if particle.particle_type == "circle":
                painter.drawEllipse(int(screen_pixel_x - particle.size / 2),
                                  int(screen_pixel_y - particle.size / 2),
                                  int(particle.size), int(particle.size))
            else:
                painter.fillRect(int(screen_pixel_x - particle.size / 2),
                               int(screen_pixel_y - particle.size / 2),
                               int(particle.size), int(particle.size),
                               particle_color)

        # Draw floating text
        text_font = QFont("Arial", 14, QFont.Weight.Bold)
        for ftext in self.game.anim_manager.floating_texts:
            # Convert to screen coords
            screen_x = ftext.x - self.game.camera_x
            screen_y = ftext.y - self.game.camera_y

            # Only draw if visible
            if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
                continue

            if ftext.is_crit:
                text_font.setPointSize(18)
            else:
                text_font.setPointSize(14)

            painter.setFont(text_font)
            text_color = QColor(ftext.color.red(), ftext.color.green(),
                              ftext.color.blue(), ftext.alpha)
            painter.setPen(text_color)

            # Calculate position
            text_x = screen_x * c.TILE_SIZE + c.TILE_SIZE // 2
            text_y = screen_y * c.TILE_SIZE + int(ftext.offset_y * c.TILE_SIZE)

            painter.drawText(int(text_x - 20), int(text_y - 10), 40, 20,
                           Qt.AlignmentFlag.AlignCenter, ftext.text)

        # Draw alert particles (!) above enemies when they spot player
        alert_font = QFont("Arial", 28, QFont.Weight.Bold)
        for alert in self.game.anim_manager.alert_particles:
            # Get enemy's current position (follows enemy as they move)
            enemy = alert.enemy

            # Only draw if enemy tile is visible
            if self.game.visibility_map and not self.game.visibility_map.is_visible(enemy.x, enemy.y):
                continue

            # Convert to screen coords using enemy's current position
            screen_x = enemy.x - self.game.camera_x
            screen_y = enemy.y - self.game.camera_y

            # Only draw if visible
            if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
                continue

            painter.setFont(alert_font)
            alert_color = QColor(alert.color.red(), alert.color.green(),
                                alert.color.blue(), 255)
            painter.setPen(alert_color)

            # Position above enemy with bounce offset
            text_x = screen_x * c.TILE_SIZE + c.TILE_SIZE // 2
            text_y = screen_y * c.TILE_SIZE - int(alert.bounce_offset * c.TILE_SIZE)

            # Draw "!" with shadow for visibility
            painter.setPen(QColor(0, 0, 0, 200))  # Shadow
            painter.drawText(int(text_x - 12), int(text_y - 12), 24, 30,
                           Qt.AlignmentFlag.AlignCenter, "!")
            painter.setPen(alert_color)  # Main color
            painter.drawText(int(text_x - 10), int(text_y - 10), 20, 30,
                           Qt.AlignmentFlag.AlignCenter, "!")

        # Draw ability range indicator if in targeting mode
        if self.targeting_mode and self.targeting_ability_index is not None:
            self._draw_ability_range(painter)

        # Draw debug enemy FOV overlay (F2)
        if hasattr(self, 'debug_show_enemy_fov') and self.debug_show_enemy_fov:
            self._draw_enemy_fov_debug(painter)

        # Draw hover highlight (before game over overlay)
        if self.hover_world_x is not None and self.hover_world_y is not None:
            self._draw_hover_highlight(painter)

        # Draw game over overlay
        if self.game.game_over:
            # Reset transform for overlay
            painter.resetTransform()
            self._draw_game_over_overlay(painter)

    def _get_entity_color(self, entity) -> QColor:
        """Get color for entity"""
        if entity.entity_type == c.ENTITY_PLAYER:
            # Use class-specific color
            class_colors = {
                c.CLASS_WARRIOR: c.COLOR_CLASS_WARRIOR,
                c.CLASS_MAGE: c.COLOR_CLASS_MAGE,
                c.CLASS_ROGUE: c.COLOR_CLASS_ROGUE,
                c.CLASS_RANGER: c.COLOR_CLASS_RANGER,
            }
            return class_colors.get(entity.class_type, c.COLOR_PLAYER)
        elif entity.entity_type == c.ENTITY_ENEMY:
            if entity.enemy_type == c.ENEMY_GOBLIN:
                return c.COLOR_ENEMY_GOBLIN
            elif entity.enemy_type == c.ENEMY_SLIME:
                return c.COLOR_ENEMY_SLIME
            elif entity.enemy_type == c.ENEMY_SKELETON:
                return c.COLOR_ENEMY_SKELETON
            elif entity.enemy_type == c.ENEMY_ORC:
                return c.COLOR_ENEMY_ORC
            elif entity.enemy_type == c.ENEMY_DEMON:
                return c.COLOR_ENEMY_DEMON
            elif entity.enemy_type == c.ENEMY_DRAGON:
                return c.COLOR_ENEMY_DRAGON
        elif entity.entity_type == c.ENTITY_ITEM:
            # Use rarity color for items
            rarity_colors = {
                c.RARITY_COMMON: c.COLOR_RARITY_COMMON,
                c.RARITY_UNCOMMON: c.COLOR_RARITY_UNCOMMON,
                c.RARITY_RARE: c.COLOR_RARITY_RARE,
                c.RARITY_EPIC: c.COLOR_RARITY_EPIC,
                c.RARITY_LEGENDARY: c.COLOR_RARITY_LEGENDARY,
            }
            return rarity_colors.get(entity.rarity, c.COLOR_ITEM_POTION)
        return QColor(255, 255, 255)

    def _draw_enemy_health_bars(self, painter: QPainter):
        """Draw health bars below enemies at their display positions"""
        # Reset painter state to prevent brush/pen contamination from previous rendering
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.PenStyle.NoPen)

        for enemy in self.game.enemies:
            # Only show health bars for visible enemies
            if self.game.visibility_map and not self.game.visibility_map.is_visible(enemy.x, enemy.y):
                continue

            # Get display position (includes bob offset)
            display_x, display_y = enemy.get_display_pos()

            # Convert world display coords to screen coords
            screen_x = display_x - self.game.camera_x
            screen_y = display_y - self.game.camera_y

            # Only draw if enemy is visible in viewport (with margin)
            if not (-1 <= screen_x < c.VIEWPORT_WIDTH + 1 and -1 <= screen_y < c.VIEWPORT_HEIGHT + 1):
                continue

            # Calculate bar dimensions
            bar_width = c.TILE_SIZE - 4
            bar_height = 3
            bar_x = int(screen_x * c.TILE_SIZE + 2)
            bar_y = int(screen_y * c.TILE_SIZE + c.TILE_SIZE - 5)

            # Draw background
            painter.fillRect(bar_x, bar_y, bar_width, bar_height, c.COLOR_ENEMY_HP_BAR_BG)

            # Draw health
            hp_percent = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
            health_width = int(bar_width * hp_percent)

            if health_width > 0:
                painter.fillRect(bar_x, bar_y, health_width, bar_height, c.COLOR_ENEMY_HP_BAR)

            # Draw border
            painter.setPen(c.COLOR_ENEMY_HP_BAR_BORDER)
            painter.drawRect(bar_x, bar_y, bar_width, bar_height)

    def _draw_ability_range(self, painter: QPainter):
        """Draw ability range/area indicator when in targeting mode"""
        if not self.game.player or self.targeting_ability_index >= len(self.game.player.abilities):
            return

        ability = self.game.player.abilities[self.targeting_ability_index]
        player_x, player_y = self.game.player.x, self.game.player.y

        # Define range and area based on ability type
        range_color = QColor(100, 150, 255, 60)
        area_color = QColor(255, 100, 100, 80)

        # Ability-specific range visualization
        if ability.name == "Fireball":
            # Show max range and AOE area
            max_range = 8  # Fireball can be cast far
            radius = 1

            # Show range circles
            for y in range(c.GRID_HEIGHT):
                for x in range(c.GRID_WIDTH):
                    dist = abs(x - player_x) + abs(y - player_y)
                    if dist <= max_range:
                        screen_x = x - self.game.camera_x
                        screen_y = y - self.game.camera_y
                        if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                            painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                           c.TILE_SIZE, c.TILE_SIZE, range_color)

            # Show AOE at cursor position
            if self.hover_world_x is not None and self.hover_world_y is not None:
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        aoe_x = self.hover_world_x + dx
                        aoe_y = self.hover_world_y + dy
                        screen_x = aoe_x - self.game.camera_x
                        screen_y = aoe_y - self.game.camera_y
                        if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                            painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                           c.TILE_SIZE, c.TILE_SIZE, area_color)

        elif ability.name == "Dash":
            # Show max dash range
            max_distance = 4
            for y in range(c.GRID_HEIGHT):
                for x in range(c.GRID_WIDTH):
                    dist = abs(x - player_x) + abs(y - player_y)
                    if dist <= max_distance and self.game.dungeon.is_walkable(x, y):
                        screen_x = x - self.game.camera_x
                        screen_y = y - self.game.camera_y
                        if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                            painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                           c.TILE_SIZE, c.TILE_SIZE, QColor(150, 200, 255, 80))

        elif ability.name == "Shadow Step":
            # Show enemy targets
            for enemy in self.game.enemies:
                # Check if there's a valid position behind enemy
                dx = enemy.x - player_x
                dy = enemy.y - player_y
                behind_x = enemy.x + (1 if dx > 0 else -1 if dx < 0 else 0)
                behind_y = enemy.y + (1 if dy > 0 else -1 if dy < 0 else 0)

                valid = self.game.dungeon.is_walkable(behind_x, behind_y)
                color = QColor(180, 100, 255, 100) if valid else QColor(100, 100, 100, 50)

                screen_x = enemy.x - self.game.camera_x
                screen_y = enemy.y - self.game.camera_y
                if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                    painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                   c.TILE_SIZE, c.TILE_SIZE, color)

        elif ability.name == "Frost Nova":
            # Show radius around player
            radius = 2
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) <= radius:
                        nova_x = player_x + dx
                        nova_y = player_y + dy
                        screen_x = nova_x - self.game.camera_x
                        screen_y = nova_y - self.game.camera_y
                        if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                            painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                           c.TILE_SIZE, c.TILE_SIZE, QColor(150, 220, 255, 80))

        elif ability.name == "Whirlwind":
            # Show adjacent tiles
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx != 0 or dy != 0:
                        whirl_x = player_x + dx
                        whirl_y = player_y + dy
                        screen_x = whirl_x - self.game.camera_x
                        screen_y = whirl_y - self.game.camera_y
                        if 0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT:
                            painter.fillRect(screen_x * c.TILE_SIZE, screen_y * c.TILE_SIZE,
                                           c.TILE_SIZE, c.TILE_SIZE, QColor(255, 150, 150, 80))

    def _draw_hover_highlight(self, painter: QPainter):
        """Draw hover highlight on the tile under cursor"""
        # Convert world coords to screen coords
        screen_x = self.hover_world_x - self.game.camera_x
        screen_y = self.hover_world_y - self.game.camera_y

        # Only draw if visible in viewport
        if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
            return

        # Determine highlight color based on what's at the tile
        highlight_color, can_interact = self._get_hover_color()

        if can_interact:
            # Draw highlight border
            painter.setPen(highlight_color)
            for i in range(3):  # Draw multiple borders for glow effect
                alpha = 255 - (i * 60)
                glow_color = QColor(highlight_color.red(), highlight_color.green(),
                                   highlight_color.blue(), alpha)
                painter.setPen(glow_color)
                offset = i * 2
                painter.drawRect(
                    screen_x * c.TILE_SIZE - offset,
                    screen_y * c.TILE_SIZE - offset,
                    c.TILE_SIZE + offset * 2 - 1,
                    c.TILE_SIZE + offset * 2 - 1
                )

            # Fill with semi-transparent color
            fill_color = QColor(highlight_color.red(), highlight_color.green(),
                               highlight_color.blue(), 40)
            painter.fillRect(
                screen_x * c.TILE_SIZE,
                screen_y * c.TILE_SIZE,
                c.TILE_SIZE,
                c.TILE_SIZE,
                fill_color
            )

    def _get_hover_color(self) -> tuple:
        """Get hover highlight color based on tile content. Returns (color, can_interact)"""
        if not self.game.player or self.game.game_over:
            return (QColor(100, 100, 100), False)

        x, y = self.hover_world_x, self.hover_world_y

        # Check if player is hovering over themselves
        if x == self.game.player.x and y == self.game.player.y:
            return (QColor(100, 200, 255), False)  # Blue, but no interaction

        # Check for enemy (attack)
        entity = self.game.get_entity_at(x, y)
        if entity and entity.entity_type == c.ENTITY_ENEMY:
            # Check if adjacent
            if abs(x - self.game.player.x) + abs(y - self.game.player.y) == 1:
                return (QColor(255, 80, 80), True)  # Red - attack
            else:
                return (QColor(255, 150, 80), False)  # Orange - out of range

        # Check for item
        if entity and entity.entity_type == c.ENTITY_ITEM:
            return (QColor(255, 215, 0), True)  # Gold - pickup

        # Check for stairs
        if self.game.dungeon and self.game.dungeon.get_tile(x, y) == c.TILE_STAIRS:
            return (QColor(180, 100, 255), True)  # Purple - descend

        # Check if walkable
        if self.game.dungeon and self.game.dungeon.is_walkable(x, y):
            return (QColor(100, 220, 100), True)  # Green - move

        # Wall or unwalkable
        return (QColor(100, 100, 100), False)  # Gray - blocked

    def _find_path_step(self, start_x: int, start_y: int, goal_x: int, goal_y: int):
        """
        A* pathfinding to find the next step towards goal.
        Returns (dx, dy) for the next move, or (0, 0) if no path.
        """
        # Simple heuristic (Manhattan distance)
        def heuristic(x, y):
            return abs(x - goal_x) + abs(y - goal_y)

        # Priority queue: (f_score, counter, x, y)
        counter = 0
        open_set = [(heuristic(start_x, start_y), counter, start_x, start_y)]
        counter += 1

        # Track where we came from
        came_from = {}

        # Cost from start
        g_score = {(start_x, start_y): 0}

        # Visited set
        visited = set()

        while open_set:
            _, _, current_x, current_y = heapq.heappop(open_set)

            # Skip if already visited
            if (current_x, current_y) in visited:
                continue
            visited.add((current_x, current_y))

            # Reached goal
            if current_x == goal_x and current_y == goal_y:
                # Reconstruct path to find first step
                path = []
                cx, cy = current_x, current_y
                while (cx, cy) in came_from:
                    path.append((cx, cy))
                    cx, cy = came_from[(cx, cy)]

                if len(path) >= 1:
                    # Get the first step after start
                    next_x, next_y = path[-1]
                    return (next_x - start_x, next_y - start_y)
                else:
                    return (0, 0)

            # Explore neighbors (4-directional)
            current_g = g_score[(current_x, current_y)]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = current_x + dx, current_y + dy

                # Check if walkable
                if not self.game.dungeon.is_walkable(nx, ny):
                    continue

                # Skip if occupied by enemy (unless it's the goal - attacking)
                if (nx, ny) != (goal_x, goal_y):
                    entity = self.game.get_entity_at(nx, ny)
                    if entity and entity.entity_type == c.ENTITY_ENEMY:
                        continue

                tentative_g = current_g + 1

                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = (current_x, current_y)
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + heuristic(nx, ny)
                    heapq.heappush(open_set, (f_score, counter, nx, ny))
                    counter += 1

        # No path found
        return (0, 0)

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        # Convert mouse position to world coordinates
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        screen_x = mouse_x // c.TILE_SIZE
        screen_y = mouse_y // c.TILE_SIZE

        self.hover_world_x = screen_x + self.game.camera_x
        self.hover_world_y = screen_y + self.game.camera_y

        # Trigger repaint for hover effect
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse clicks for movement and interaction"""
        if self.game.game_over or not self.game.player:
            return

        # Get world coordinates of click
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        screen_x = mouse_x // c.TILE_SIZE
        screen_y = mouse_y // c.TILE_SIZE

        world_x = screen_x + self.game.camera_x
        world_y = screen_y + self.game.camera_y

        # Handle targeting mode
        if self.targeting_mode and event.button() == Qt.MouseButton.LeftButton:
            # Use ability at target position
            self.game.use_ability(self.targeting_ability_index, world_x, world_y)
            self.targeting_mode = False
            self.targeting_ability_index = None
            self.update()
            return

        # Cancel targeting with right click
        if self.targeting_mode and event.button() == Qt.MouseButton.RightButton:
            self.targeting_mode = False
            self.targeting_ability_index = None
            self.update()
            return

        # Normal movement/interaction (left click only)
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Don't do anything if clicking on player
        if world_x == self.game.player.x and world_y == self.game.player.y:
            return

        # Use A* pathfinding to find next step
        dx, dy = self._find_path_step(
            self.game.player.x, self.game.player.y,
            world_x, world_y
        )

        # If pathfinding found a valid move, execute it
        if dx != 0 or dy != 0:
            self.game.player_move(dx, dy)

        # Update display
        self.update()

    def _draw_game_over_overlay(self, painter: QPainter):
        """Draw game over overlay with enhanced visuals"""
        # Dark overlay with gradient effect
        overlay_color = QColor(0, 0, 0, 200)
        painter.fillRect(0, 0, self.width(), self.height(), overlay_color)

        # Draw decorative border
        border_color = QColor(255, 60, 60, 100)
        painter.setPen(border_color)
        painter.drawRect(40, 40, self.width() - 80, self.height() - 80)

        # Game over title with shadow
        title_y = self.height() // 2 - 150

        # Shadow
        painter.setPen(QColor(0, 0, 0, 150))
        painter.setFont(QFont("Arial", 56, QFont.Weight.Bold))
        painter.drawText(2, title_y + 2, self.width(), 80,
                        Qt.AlignmentFlag.AlignCenter, "GAME OVER")

        # Main title
        painter.setPen(QColor(255, 80, 80))
        painter.drawText(0, title_y, self.width(), 80,
                        Qt.AlignmentFlag.AlignCenter, "GAME OVER")

        # Stats summary with better formatting
        if self.game.player:
            stats_y = self.height() // 2 - 40

            # Class and level
            painter.setPen(c.COLOR_TEXT_LIGHT)
            painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            painter.drawText(0, stats_y, self.width(), 30,
                           Qt.AlignmentFlag.AlignCenter,
                           f"{self.game.player.get_class_name()} - Level {self.game.player.level}")

            # Dungeon depth
            painter.setFont(QFont("Arial", 16))
            painter.setPen(QColor(180, 180, 200))
            painter.drawText(0, stats_y + 40, self.width(), 25,
                           Qt.AlignmentFlag.AlignCenter,
                           f"Reached Dungeon Level {self.game.current_level}")

            # Stats box
            box_y = stats_y + 80
            painter.setPen(QColor(100, 100, 120))
            painter.drawRect(self.width() // 2 - 120, box_y, 240, 60)

            # Stats text
            painter.setPen(QColor(220, 220, 220))
            painter.setFont(QFont("Courier New", 14, QFont.Weight.Bold))

            # Attack
            painter.drawText(self.width() // 2 - 110, box_y + 25, 100, 20,
                           Qt.AlignmentFlag.AlignLeft, f"ATK: {self.game.player.attack}")

            # Defense
            painter.drawText(self.width() // 2 + 10, box_y + 25, 100, 20,
                           Qt.AlignmentFlag.AlignLeft, f"DEF: {self.game.player.defense}")

            # HP
            painter.drawText(self.width() // 2 - 110, box_y + 50, 220, 20,
                           Qt.AlignmentFlag.AlignCenter, f"Max HP: {self.game.player.max_hp}")

        # Restart instruction with highlight
        restart_y = self.height() // 2 + 180
        painter.setPen(QColor(100, 200, 255))
        painter.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        painter.drawText(0, restart_y, self.width(), 40,
                        Qt.AlignmentFlag.AlignCenter, "Press R to Restart")

    def _draw_fogged_wall(self, painter, screen_x: int, screen_y: int):
        """Draw a darkened wall tile for explored but not visible areas"""
        # Draw a simple darkened version of the wall
        fog_color = gfx.apply_fog_color(c.COLOR_WALL, c.EXPLORED_TILE_ALPHA)
        painter.fillRect(
            screen_x * c.TILE_SIZE,
            screen_y * c.TILE_SIZE,
            c.TILE_SIZE,
            c.TILE_SIZE,
            fog_color
        )

    def _draw_fogged_floor(self, painter, screen_x: int, screen_y: int):
        """Draw a darkened floor tile for explored but not visible areas"""
        # Draw a simple darkened version of the floor
        fog_color = gfx.apply_fog_color(c.COLOR_FLOOR, c.EXPLORED_TILE_ALPHA)
        painter.fillRect(
            screen_x * c.TILE_SIZE,
            screen_y * c.TILE_SIZE,
            c.TILE_SIZE,
            c.TILE_SIZE,
            fog_color
        )

    def _draw_fogged_stairs(self, painter, screen_x: int, screen_y: int):
        """Draw darkened stairs for explored but not visible areas"""
        painter.save()  # Save painter state to prevent color leaking to other tiles

        # Draw a simple darkened version of the stairs
        fog_color = gfx.apply_fog_color(c.COLOR_STAIRS, c.EXPLORED_TILE_ALPHA)
        # Draw simple stairs indicator (chevron)
        painter.setPen(fog_color)
        painter.setBrush(fog_color)

        center_x = screen_x * c.TILE_SIZE + c.TILE_SIZE // 2
        center_y = screen_y * c.TILE_SIZE + c.TILE_SIZE // 2
        size = c.TILE_SIZE // 4

        # Simple chevron pointing down
        points = QPolygon([
            QPoint(center_x - size, center_y - size // 2),
            QPoint(center_x, center_y + size // 2),
            QPoint(center_x + size, center_y - size // 2)
        ])
        painter.drawPolygon(points)

        painter.restore()  # Restore painter state

    def _draw_enemy_fov_debug(self, painter):
        """Draw enemy FOV ranges for debugging (F2)"""
        from fov import calculate_fov

        # Draw FOV for each enemy with semi-transparent red overlay
        for enemy in self.game.enemies:
            # Calculate enemy's FOV
            enemy_fov = calculate_fov(
                self.game.dungeon,
                enemy.x,
                enemy.y,
                enemy.vision_radius
            )

            # Draw each visible tile in enemy FOV
            for tile_x, tile_y in enemy_fov:
                # Convert to screen coords
                screen_x = tile_x - self.game.camera_x
                screen_y = tile_y - self.game.camera_y

                # Only draw if in viewport
                if not (0 <= screen_x < c.VIEWPORT_WIDTH and 0 <= screen_y < c.VIEWPORT_HEIGHT):
                    continue

                # Semi-transparent red overlay
                debug_color = QColor(255, 100, 100, 40)
                painter.fillRect(
                    screen_x * c.TILE_SIZE,
                    screen_y * c.TILE_SIZE,
                    c.TILE_SIZE,
                    c.TILE_SIZE,
                    debug_color
                )

            # Draw enemy vision radius circle
            enemy_screen_x = enemy.x - self.game.camera_x
            enemy_screen_y = enemy.y - self.game.camera_y

            if 0 <= enemy_screen_x < c.VIEWPORT_WIDTH and 0 <= enemy_screen_y < c.VIEWPORT_HEIGHT:
                painter.setPen(QColor(255, 50, 50, 150))
                center_pixel_x = int((enemy_screen_x + 0.5) * c.TILE_SIZE)
                center_pixel_y = int((enemy_screen_y + 0.5) * c.TILE_SIZE)
                radius_pixels = enemy.vision_radius * c.TILE_SIZE

                painter.drawEllipse(
                    center_pixel_x - radius_pixels,
                    center_pixel_y - radius_pixels,
                    radius_pixels * 2,
                    radius_pixels * 2
                )
