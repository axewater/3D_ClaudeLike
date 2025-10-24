"""
3D mode entry point using Ursina Engine

This module provides the main game loop for 3D rendering mode.
All game logic remains in game.py - this only handles visualization and input.
"""

from ursina import Ursina, Entity, camera, held_keys, time as ursina_time, color, window, Vec3, mouse
import constants as c
from game import Game
from renderer3d import Renderer3D
from animations3d import Particle3D
from ui3d_manager import UI3DManager
from animation_interface import AnimationManagerInterface
from particle_types import Particle
from logger import get_logger

log = get_logger()


class ParticleListWrapper:
    """
    Wrapper for particles list that converts neutral Particle objects to 3D when appended.
    This allows game.py footstep code to continue using direct append.
    """
    def __init__(self, anim_manager_3d):
        self.anim_3d = anim_manager_3d

    def append(self, particle):
        """Convert neutral particle to 3D and add to 3D particle list"""
        # Extract particle properties
        # Position needs to be converted from pixel coords to grid coords
        # The particle uses pixel coordinates (center_x, center_y)
        # We need to convert back to grid coords

        # Calculate grid position from pixel coords
        grid_x = particle.x / c.TILE_SIZE
        grid_y = particle.y / c.TILE_SIZE

        # Convert to 3D position
        from graphics3d.utils import world_to_3d_position
        pos_3d = world_to_3d_position(int(grid_x), int(grid_y), 0.3)  # Near ground

        # Convert velocity (pixel velocity to world units/sec)
        velocity_3d = Vec3(
            particle.vx * 0.1,  # Scale down
            particle.vy * -0.1,  # Invert Y and scale
            0  # No Z velocity
        )

        # Color is already RGB tuple (0-1 range)
        color_rgb = particle.color

        # Convert size (pixel size to world units)
        size_3d = particle.size * 0.02  # Scale down

        # Create 3D particle
        particle_3d = Particle3D(
            pos_3d,
            velocity_3d,
            color_rgb,
            size=size_3d,
            lifetime=particle.max_lifetime,
            particle_type="circle",
            apply_gravity=particle.apply_gravity
        )

        # Add to 3D particles list
        self.anim_3d.particles.append(particle_3d)


class AnimationManager3DProxy(AnimationManagerInterface):
    """
    Proxy for AnimationManager3D that implements the neutral animation interface.
    Receives RGB tuples from game.py and forwards to 3D animation system.
    """
    def __init__(self, anim_manager_3d, enemy_entities_dict):
        self.anim_3d = anim_manager_3d
        self.enemy_entities = enemy_entities_dict  # Reference to renderer's enemy dict
        # Create a wrapper for particles list that converts neutral particles to 3D
        self._particle_list_wrapper = ParticleListWrapper(self.anim_3d)

    @property
    def particles(self):
        """Expose particles list for direct append (used by footstep code)"""
        return self._particle_list_wrapper

    def add_flash_effect(self, x, y, color=None):
        """Disabled in 3D - the white flash effect looks jarring in first-person"""
        # Blood particles and sound effects still play via separate methods
        pass

    def add_particle_burst(self, x, y, color, count=8, particle_type="square"):
        """Color is already RGB tuple (0-1 range)"""
        self.anim_3d.add_particle_burst(x, y, color, count, particle_type)

    def add_blood_splatter(self, x, y):
        """Blood red RGB tuple"""
        rgb = (0.7, 0.0, 0.0)
        self.anim_3d.add_particle_burst(x, y, rgb, count=12, particle_type="circle")

    def add_heal_sparkles(self, x, y):
        """Green heal sparkles"""
        self.anim_3d.add_heal_sparkles(x, y)

    def add_screen_shake(self, intensity=5.0, duration=0.2):
        """Screen shake effect"""
        self.anim_3d.add_screen_shake(intensity, duration)

    def add_directional_impact(self, x, y, from_x, from_y, color, count=10, is_crit=False):
        """Color is already RGB tuple (0-1 range)"""
        self.anim_3d.add_directional_impact(x, y, from_x, from_y, color, count, is_crit)

    def add_trail(self, x, y, color, trail_type="fade"):
        """Color is already RGB tuple (0-1 range)"""
        from animations3d import TrailEffect3D
        self.anim_3d.trails.append(TrailEffect3D(x, y, color, trail_type))

    def add_ability_trail(self, x, y, color, ability_type):
        """Color is already RGB tuple (0-1 range)"""
        self.anim_3d.add_ability_trail(x, y, color, ability_type)

    def add_ambient_particles(self, count=1):
        """Disabled in 3D first-person mode (can't see outside dungeon)"""
        if c.ENABLE_AMBIENT_PARTICLES_3D:
            self.anim_3d.add_ambient_particles(count)

    def add_fog_particles(self, count=1):
        """Disabled in 3D first-person mode (can't see outside dungeon)"""
        if c.ENABLE_AMBIENT_PARTICLES_3D:
            self.anim_3d.add_ambient_particles(count)

    def add_alert_particle(self, enemy):
        """Alert particle above enemy"""
        # Get enemy's 3D model entity from renderer's tracking dict
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            enemy_model = self.enemy_entities[enemy_id]['model']
            self.anim_3d.add_alert_particle(enemy_model)

    def add_death_burst(self, x, y, enemy_type):
        """Death burst effect for enemy type"""
        self.anim_3d.add_death_burst(x, y, enemy_type)

    def add_level_title(self, level_number):
        """Add level entry title card"""
        self.anim_3d.add_level_title(level_number)

    def update(self, dt):
        """Animation manager is updated in renderer, not here"""
        pass

    def clear_all(self):
        """Clear all active animations"""
        self.anim_3d.clear_all()


class GameCoordinator(Entity):
    """
    Coordinates between screen manager and game initialization.
    Watches for class selection and initializes the game when ready.
    """
    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_initialized = False

    def update(self):
        """Check if we need to initialize a new game"""
        # Check if a class was selected
        if hasattr(self.screen_manager, 'selected_class') and not self.game_initialized:
            class_type = self.screen_manager.selected_class
            log.info(f"Initializing game with class: {class_type}", "coordinator")

            # Create game instance
            game = Game()
            game.selected_class = class_type
            game.start_new_game()

            # Create 3D renderer
            renderer = Renderer3D(game)
            renderer.render_dungeon()
            renderer.render_entities()

            # Store renderer reference in game for attack animations
            game.renderer = renderer

            # Play dungeon entrance voice AFTER rendering is complete
            # This prevents overlap with the class selection voice
            game.audio_manager.play_voice('dungeon_entrance', volume=0.9)

            # Replace 2D animation manager with 3D proxy
            game.anim_manager = AnimationManager3DProxy(renderer.animation_manager, renderer.enemy_entities)
            log.debug("3D particle system connected", "coordinator")

            # Create UI manager
            ui_manager = UI3DManager(game)
            log.debug("UI3D system initialized", "coordinator")

            # Connect game messages to UI combat log
            game.message_callback = ui_manager.add_message
            log.debug("Game message callback connected to UI", "coordinator")

            # Create game controller
            controller = GameController(game, renderer, ui_manager, self.screen_manager)
            self.screen_manager.set_game_controller(controller)

            # Clear selected_class to prevent re-initialization
            del self.screen_manager.selected_class
            self.game_initialized = True

            # Change to game screen
            from ui.screens.screen_manager_3d import ScreenState
            self.screen_manager.change_screen(ScreenState.GAME)

            log.info(f"Game started - Class: {class_type.title()}, Level: {game.current_level}, HP: {game.player.hp}/{game.player.max_hp}", "coordinator")


class GameController(Entity):
    """
    Main game controller using Ursina Entity pattern.
    Ursina automatically calls update() on all Entity subclasses.
    """
    def __init__(self, game, renderer, ui_manager, screen_manager=None):
        super().__init__()
        self.game = game
        self.renderer = renderer
        self.ui_manager = ui_manager
        self.screen_manager = screen_manager

        # Input cooldown to prevent holding keys
        self.move_cooldown = 0.0
        self.move_cooldown_time = 0.15  # Seconds between moves

        # Ability input cooldown (prevent rapid key presses)
        self.ability_cooldown = 0.0
        self.ability_cooldown_time = 0.2  # Seconds between ability key presses

        # First-person camera rotation
        self.camera_yaw = 0.0  # Current yaw in degrees (0 = North, 90 = East, 180 = South, 270 = West)
        self.target_camera_yaw = 0.0  # Target yaw for smooth interpolation

        # First-person camera pitch (vertical tilt)
        self.camera_pitch = c.DEFAULT_CAMERA_PITCH  # Current pitch in degrees (negative = looking down)
        self.target_camera_pitch = c.DEFAULT_CAMERA_PITCH  # Target pitch for smooth interpolation

        # Track if game is over
        self.game_over_displayed = False

        # Paused state (for pause menu)
        self.paused = False

        # Debug: Frame counter
        self.frame_count = 0

        # Track previous key states (for detecting key press vs hold)
        self.prev_key_states = {
            '1': False, '2': False, '3': False,
            'escape': False, 'left mouse down': False,
            'left arrow': False, 'right arrow': False,
            'f1': False,  # Debug: reveal map
            'f2': False   # Debug: skip level
        }

        log.debug("GameController initialized (First-Person Mode)", "controller")

    def update(self):
        """Update function called every frame by Ursina"""
        dt = ursina_time.dt
        self.frame_count += 1

        # Heartbeat logging (DEBUG only, reduced frequency)
        if c.HEARTBEAT_INTERVAL_FRAMES > 0 and self.frame_count % c.HEARTBEAT_INTERVAL_FRAMES == 0:
            log.debug(f"Frame {self.frame_count} | dt={dt:.4f} | FPS={1/dt:.1f}", "heartbeat")

        self.move_cooldown -= dt
        self.ability_cooldown -= dt

        # Update camera rotation (smooth interpolation)
        self._update_camera_rotation(dt)

        # Update camera pitch (smooth interpolation)
        self._update_camera_pitch(dt)

        # Handle camera rotation input (arrow keys)
        self._handle_camera_rotation()

        # Handle debug keys (F1)
        self._handle_debug_input()

        # Handle ability input and targeting
        self._handle_ability_input()

        # Skip game logic if paused
        if self.paused:
            return

        # Check for game over or victory
        if self.game.game_over or self.game.victory:
            if not self.game_over_displayed:
                if self.game.victory:
                    log.info("VICTORY! You conquered all 25 levels!", "game")
                else:
                    log.info("GAME OVER! You were defeated.", "game")
                log.info(f"Final Level: {self.game.current_level}, Final XP: {self.game.player.xp}", "game")
                self.game_over_displayed = True

                # Trigger screen transition if screen manager available
                if self.screen_manager:
                    stats = {
                        'level': self.game.current_level,
                        'xp': self.game.player.xp,
                        'enemies_defeated': getattr(self.game, 'enemies_defeated', 0)
                    }

                    if self.game.victory:
                        self.screen_manager.show_victory(stats)
                    else:
                        death_reason = "You were defeated"
                        # Try to get more specific death reason
                        if hasattr(self.game, 'last_attacker'):
                            death_reason = f"Slain by {self.game.last_attacker}"
                        self.screen_manager.show_game_over(stats, death_reason)
            return

        # Handle movement input (only if cooldown expired)
        if self.move_cooldown <= 0:
            moved = False
            new_x, new_y = self.game.player.x, self.game.player.y
            direction = ""

            # First-person directional movement (relative to camera yaw)
            if c.USE_FIRST_PERSON:
                # Get movement offset based on camera direction
                offset_x, offset_y = 0, 0

                if held_keys['w']:
                    # Move forward in camera direction
                    offset_x, offset_y = self._get_forward_offset()
                    moved = True
                    direction = "FORWARD"

                elif held_keys['s']:
                    # Move backward
                    back_x, back_y = self._get_forward_offset()
                    offset_x, offset_y = -back_x, -back_y
                    moved = True
                    direction = "BACKWARD"

                elif held_keys['a']:
                    # Strafe left
                    offset_x, offset_y = self._get_left_offset()
                    moved = True
                    direction = "STRAFE LEFT"

                elif held_keys['d']:
                    # Strafe right
                    right_x, right_y = self._get_left_offset()
                    offset_x, offset_y = -right_x, -right_y
                    moved = True
                    direction = "STRAFE RIGHT"

                # Arrow Up/Down also move forward/backward
                elif held_keys['up arrow']:
                    offset_x, offset_y = self._get_forward_offset()
                    moved = True
                    direction = "FORWARD (arrow)"

                elif held_keys['down arrow']:
                    back_x, back_y = self._get_forward_offset()
                    offset_x, offset_y = -back_x, -back_y
                    moved = True
                    direction = "BACKWARD (arrow)"

                if moved:
                    new_x = self.game.player.x + offset_x
                    new_y = self.game.player.y + offset_y

            else:
                # Third-person: absolute grid movement (legacy)
                if held_keys['w'] or held_keys['up arrow']:
                    new_x, new_y = self.game.player.x, self.game.player.y - 1
                    moved = True
                    direction = "UP"

                elif held_keys['s'] or held_keys['down arrow']:
                    new_x, new_y = self.game.player.x, self.game.player.y + 1
                    moved = True
                    direction = "DOWN"

                elif held_keys['a'] or held_keys['left arrow']:
                    new_x, new_y = self.game.player.x - 1, self.game.player.y
                    moved = True
                    direction = "LEFT"

                elif held_keys['d'] or held_keys['right arrow']:
                    new_x, new_y = self.game.player.x + 1, self.game.player.y
                    moved = True
                    direction = "RIGHT"

            if moved:
                log.debug(f"{direction} | Yaw: {int(self.camera_yaw)}° | Target: ({new_x}, {new_y})", "input")

            # Attempt move
            if moved:
                # Try to move player via game logic
                if self.game.dungeon.is_walkable(new_x, new_y):
                    # Check for enemy at target position
                    target_enemy = None
                    for enemy in self.game.enemies:
                        if enemy.x == new_x and enemy.y == new_y:
                            target_enemy = enemy
                            break

                    if target_enemy:
                        # Attack enemy
                        log.debug(f"Attacking {target_enemy.enemy_type} at ({new_x}, {new_y})", "combat")
                        self.game._player_attack(target_enemy)
                        self.game._enemy_turn()
                        self.game._reduce_ability_cooldowns()
                    else:
                        # Move player
                        old_pos = (self.game.player.x, self.game.player.y)
                        self.game.player.start_move(new_x, new_y)
                        self.game.update_camera()
                        self.game.update_fov()
                        log.debug(f"Player moved: {old_pos} → ({self.game.player.x}, {self.game.player.y})", "movement")

                        # Check for item pickup
                        self.game._check_item_pickup()

                        # Check for stairs
                        if self.game.dungeon.get_tile(new_x, new_y) == c.TILE_STAIRS:
                            log.info(f"Descending to level {self.game.current_level + 1}...", "game")
                            self.game._descend_stairs()
                            # Re-render dungeon after descending
                            self.renderer.render_dungeon()

                        # Enemy turn
                        self.game._enemy_turn()

                        # Reduce ability cooldowns
                        self.game._reduce_ability_cooldowns()

                    self.move_cooldown = self.move_cooldown_time  # Reset cooldown
                else:
                    log.debug(f"Cannot move to ({new_x}, {new_y}) - blocked", "movement")

        # Update game animations
        self.game.update(dt)

        # Update renderer
        self.renderer.update(dt)

        # Update UI (with camera yaw for minimap)
        self.ui_manager.update(dt, self.camera_yaw)

        # Debug player position (DEBUG only, configurable interval)
        if c.PLAYER_POSITION_INTERVAL_FRAMES > 0 and self.frame_count % c.PLAYER_POSITION_INTERVAL_FRAMES == 0:
            log.debug(f"Player: ({self.game.player.x}, {self.game.player.y}) | "
                      f"HP: {self.game.player.hp}/{self.game.player.max_hp} | "
                      f"Level: {self.game.current_level} | "
                      f"Enemies: {len(self.game.enemies)}", "debug")

    def _handle_debug_input(self):
        """Handle debug key inputs (F1 to reveal map, F2 to skip level)"""
        # F1 key - Reveal entire map (debug)
        if held_keys['f1'] and not self.prev_key_states['f1']:
            if self.game.visibility_map:
                self.game.visibility_map.reveal_all()
                self.game.add_message("DEBUG: Map fully revealed!", "event")
                log.info("Full map revealed (F1)", "debug")
            self.prev_key_states['f1'] = True
        elif not held_keys['f1']:
            self.prev_key_states['f1'] = False

        # F2 key - Skip to next level (debug)
        if held_keys['f2'] and not self.prev_key_states['f2']:
            # Use debug skip method (doesn't play sounds)
            self.game.debug_skip_level()

            # Rebuild dungeon renderer (clears old geometry and fog)
            self.renderer.render_dungeon()

            log.info(f"Skipped to level {self.game.current_level} (F2)", "debug")
            self.prev_key_states['f2'] = True
        elif not held_keys['f2']:
            self.prev_key_states['f2'] = False

    def _handle_ability_input(self):
        """Handle ability input (1/2/3 keys) and targeting"""
        targeting_system = self.ui_manager.targeting_system

        # ESC key - cancel targeting OR open pause menu
        if held_keys['escape'] and not self.prev_key_states['escape']:
            if targeting_system.mode == targeting_system.MODE_TARGETING:
                # Cancel targeting
                targeting_system.cancel_targeting()
                log.debug("Targeting cancelled", "input")
            elif self.screen_manager and not self.paused:
                # Open pause menu (only if not already paused)
                log.debug("Opening pause menu", "input")
                from ui.screens.screen_manager_3d import ScreenState
                self.screen_manager.change_screen(ScreenState.PAUSE)
            self.prev_key_states['escape'] = True
        elif not held_keys['escape']:
            self.prev_key_states['escape'] = False

        # Mouse left click - confirm target (only when targeting)
        if mouse.left and not self.prev_key_states['left mouse down']:
            if targeting_system.mode == targeting_system.MODE_TARGETING:
                success = targeting_system.confirm_target()
                if success:
                    log.debug("Ability executed successfully", "ability")
            self.prev_key_states['left mouse down'] = True
        elif not mouse.left:
            self.prev_key_states['left mouse down'] = False

        # Don't handle ability keys if already targeting
        if targeting_system.mode == targeting_system.MODE_TARGETING:
            return

        # Only handle ability keys if cooldown expired
        if self.ability_cooldown > 0:
            return

        # 1/2/3 keys - select ability
        ability_keys = {'1': 0, '2': 1, '3': 2}

        for key, ability_index in ability_keys.items():
            key_pressed = held_keys[key] and not self.prev_key_states[key]

            if key_pressed:
                if not self.game.player or ability_index >= len(self.game.player.abilities):
                    continue

                ability = self.game.player.abilities[ability_index]

                # Check if ability is ready
                if not ability.is_ready():
                    self.ui_manager.add_message(f"{ability.name} is on cooldown ({int(ability.current_cooldown)}s remaining)", "event")
                    log.debug(f"{ability.name} on cooldown", "ability")
                    self.prev_key_states[key] = True
                    continue

                # Check if ability needs targeting
                targeting_abilities = ["Fireball", "Dash", "Shadow Step"]

                if ability.name in targeting_abilities:
                    # Enter targeting mode
                    targeting_system.start_targeting(ability_index)
                    log.debug(f"Entered targeting mode for {ability.name}", "ability")
                else:
                    # Use ability immediately (self-cast abilities)
                    # Note: use_ability() returns bool only, message is handled internally
                    success = self.game.use_ability(ability_index, self.game.player.x, self.game.player.y)

                    if success:
                        log.debug(f"Used {ability.name}", "ability")
                    else:
                        log.debug(f"Failed to use {ability.name}", "ability")

                self.ability_cooldown = self.ability_cooldown_time
                self.prev_key_states[key] = True

            elif not held_keys[key]:
                self.prev_key_states[key] = False

    def _update_camera_rotation(self, dt):
        """Smoothly interpolate camera rotation towards target yaw"""
        if self.camera_yaw != self.target_camera_yaw:
            # Calculate shortest rotation direction
            angle_diff = (self.target_camera_yaw - self.camera_yaw + 180) % 360 - 180

            # Interpolate
            rotation_step = c.CAMERA_ROTATION_SPEED * dt * 60  # Scale by dt and normalize for 60fps
            if abs(angle_diff) < rotation_step:
                self.camera_yaw = self.target_camera_yaw
            else:
                self.camera_yaw += rotation_step * (1 if angle_diff > 0 else -1)

            # Normalize to 0-360
            self.camera_yaw = self.camera_yaw % 360

            # Update renderer camera
            self.renderer.camera_yaw = self.camera_yaw

    def _update_camera_pitch(self, dt):
        """Smoothly interpolate camera pitch to focus on enemy directly in front"""
        # Check if there's an enemy in the tile directly ahead
        enemy_pos = self.renderer.find_enemy_in_front(self.camera_yaw)

        # Set target pitch
        if enemy_pos:
            # Enemy directly in front - tilt down to focus on it
            self.target_camera_pitch = c.ENEMY_FOCUS_PITCH
        else:
            # No enemy - look straight ahead
            self.target_camera_pitch = c.DEFAULT_CAMERA_PITCH

        # Smooth interpolation
        if abs(self.camera_pitch - self.target_camera_pitch) > 0.1:
            pitch_diff = self.target_camera_pitch - self.camera_pitch
            pitch_step = c.CAMERA_PITCH_SPEED * dt * 60  # Scale by dt and normalize for 60fps

            if abs(pitch_diff) < pitch_step:
                self.camera_pitch = self.target_camera_pitch
            else:
                self.camera_pitch += pitch_step * (1 if pitch_diff > 0 else -1)

            # Update renderer camera pitch
            self.renderer.camera_pitch = self.camera_pitch

    def _handle_camera_rotation(self):
        """Handle arrow key camera rotation input"""
        # Arrow Left - Rotate left (counterclockwise)
        if held_keys['left arrow'] and not self.prev_key_states['left arrow']:
            self.target_camera_yaw = (self.target_camera_yaw - 90) % 360
            log.debug(f"Rotating left to {self.target_camera_yaw}°", "camera")
            self.prev_key_states['left arrow'] = True
        elif not held_keys['left arrow']:
            self.prev_key_states['left arrow'] = False

        # Arrow Right - Rotate right (clockwise)
        if held_keys['right arrow'] and not self.prev_key_states['right arrow']:
            self.target_camera_yaw = (self.target_camera_yaw + 90) % 360
            log.debug(f"Rotating right to {self.target_camera_yaw}°", "camera")
            self.prev_key_states['right arrow'] = True
        elif not held_keys['right arrow']:
            self.prev_key_states['right arrow'] = False

    def _get_forward_offset(self):
        """Get grid offset for moving forward based on camera yaw"""
        # Round yaw to nearest 90° for grid-aligned movement
        yaw = round(self.camera_yaw / 90) * 90 % 360

        # Map yaw to grid offsets
        # Camera rotation_y in Ursina: 0° = +Z (South), 90° = +X (East), 180° = -Z (North), 270° = -X (West)
        # Grid coordinates: +Y = South, +X = East, -Y = North, -X = West
        # 3D coordinates: +Z = South (+Y grid), +X = East (+X grid), -Z = North (-Y grid), -X = West (-X grid)
        direction_map = {
            0: (0, 1),     # South (+Y grid, +Z in 3D)
            90: (1, 0),    # East (+X grid, +X in 3D)
            180: (0, -1),  # North (-Y grid, -Z in 3D)
            270: (-1, 0),  # West (-X grid, -X in 3D)
        }

        return direction_map.get(yaw, (0, 1))  # Default to South

    def _get_left_offset(self):
        """Get grid offset for strafing left based on camera yaw"""
        # Left is 90° counterclockwise from forward
        left_yaw = (self.camera_yaw - 90) % 360
        yaw = round(left_yaw / 90) * 90 % 360

        direction_map = {
            0: (0, 1),     # South (+Y grid, +Z in 3D)
            90: (1, 0),    # East (+X grid, +X in 3D)
            180: (0, -1),  # North (-Y grid, -Z in 3D)
            270: (-1, 0),  # West (-X grid, -X in 3D)
        }

        return direction_map.get(yaw, (-1, 0))  # Default to West


def main_3d():
    """Main entry point for 3D mode"""

    # Suppress Panda3D and Ursina startup logs
    from panda3d.core import loadPrcFileData
    loadPrcFileData("", "notify-level error")  # Only show errors, not info/warnings
    loadPrcFileData("", "default-directnotify-level error")

    # Create Ursina app
    app = Ursina(
        title="Claude-Like 3D",
        borderless=False,
        fullscreen=False,
        development_mode=False  # Set to True for debug info
    )

    # Set window resolution to Full HD for better performance
    window.size = (1920, 1080)
    window.position = (100, 50)  # Offset from top-left so title bar is accessible
    log.debug("Window resolution set to 1920x1080, positioned at (100, 50)", "main")

    # Set background color (dark blue, matching 2D title screen)
    window.color = color.rgb(0.05, 0.05, 0.15)
    log.debug("Window background set to dark blue", "main")

    # Initialize screen manager
    from ui.screens.screen_manager_3d import ScreenManager3D, ScreenState
    screen_manager = ScreenManager3D()
    log.debug("Screen manager initialized", "main")

    # Create game coordinator (handles game initialization after class selection)
    coordinator = GameCoordinator(screen_manager)
    log.debug("Game coordinator initialized", "main")

    # Create an entity that updates screen manager each frame
    class ScreenManagerUpdater(Entity):
        def __init__(self, sm):
            super().__init__()
            self.sm = sm
        def update(self):
            self.sm.update(ursina_time.dt)

    updater = ScreenManagerUpdater(screen_manager)

    # Start with main menu screen
    screen_manager.change_screen(ScreenState.MAIN_MENU)

    # Run Ursina app loop
    app.run()


if __name__ == "__main__":
    main_3d()
