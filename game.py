"""
Main game logic for Claude-Like
"""
import random
from typing import List, Optional, Tuple
import constants as c
from entities import Player, Enemy, Item
from dungeon import Dungeon
from animation_interface import AnimationManagerInterface
from particle_types import Particle
from abilities import CLASS_ABILITIES
from audio import get_audio_manager
from fov import calculate_fov
from visibility import VisibilityMap
import combat
from logger import get_logger

log = get_logger()


class Game:
    """Main game state"""
    def __init__(self):
        self.player: Optional[Player] = None
        self.dungeon: Optional[Dungeon] = None
        self.enemies: List[Enemy] = []
        self.items: List[Item] = []
        self.current_level = 1
        self.game_over = False
        self.victory = False
        self.messages: List[Tuple[str, str]] = []  # (message, type)
        self.max_messages = 15
        # Animation manager will be injected by main_3d.py
        self.anim_manager: Optional[AnimationManagerInterface] = None
        self.audio_manager = get_audio_manager()
        self.selected_class = c.CLASS_WARRIOR  # Default class
        self.ambient_timer = 0.0  # Timer for spawning ambient particles
        self.camera_x = 0  # Camera position (top-left of viewport in world coords)
        self.camera_y = 0
        self.message_callback = None  # Callback for visual combat log
        self.visibility_map: Optional[VisibilityMap] = None  # Field of view / fog of war
        self.fog_timer = 0.0  # Timer for spawning fog particles

    def update_camera(self):
        """Center camera on player with boundary clamping"""
        if not self.player:
            return

        # Center camera on player
        self.camera_x = self.player.x - c.VIEWPORT_WIDTH // 2
        self.camera_y = self.player.y - c.VIEWPORT_HEIGHT // 2

        # Clamp to dungeon boundaries
        self.camera_x = max(0, min(self.camera_x, c.GRID_WIDTH - c.VIEWPORT_WIDTH))
        self.camera_y = max(0, min(self.camera_y, c.GRID_HEIGHT - c.VIEWPORT_HEIGHT))

    def start_new_game(self):
        """Start a new game"""
        self.current_level = 1
        self.game_over = False
        self.victory = False
        self.messages = []
        self._generate_level()
        self.add_message("Welcome to Claude-Like! Descend the dungeon and defeat enemies.", "event")
        self.add_message("Use WASD or Arrow Keys to move. Bump into enemies to attack.", "event")

        # Start background music
        self.audio_manager.start_background_music()

    def _generate_level(self):
        """Generate a new dungeon level"""
        # Determine biome based on current level
        biome = c.get_biome_for_level(self.current_level)
        self.dungeon = Dungeon(c.GRID_WIDTH, c.GRID_HEIGHT, biome)
        start_x, start_y = self.dungeon.generate()

        # Create player or move to new level
        if self.player is None:
            self.player = Player(start_x, start_y, self.selected_class)
            # Assign class-specific abilities
            self.player.abilities = CLASS_ABILITIES.get(self.selected_class, [])
        else:
            self.player.set_pos(start_x, start_y)

        # Initialize or reset visibility map for new level
        if self.visibility_map is None:
            self.visibility_map = VisibilityMap(c.GRID_WIDTH, c.GRID_HEIGHT)
        else:
            self.visibility_map.reset()

        # Update camera to center on player
        self.update_camera()

        # Spawn enemies
        self._spawn_enemies()

        # Spawn items
        self._spawn_items()

        # Update field of view
        self.update_fov()

        self.add_message(f"Entered dungeon level {self.current_level}.", "event")

    def _spawn_enemies(self):
        """Spawn enemies on current level"""
        self.enemies = []
        self.rooms_with_enemies = set()  # Track rooms that have enemies
        level_modifier = 1.0 + (self.current_level - 1) * 0.15

        num_enemies = min(20, c.ENEMIES_PER_LEVEL_BASE + self.current_level)

        for _ in range(num_enemies):
            # Choose enemy type based on level (balanced progression with 6 enemy types)
            if self.current_level == 1:
                # Early intro: Goblin 80%, Slime 20%
                enemy_types = [c.ENEMY_GOBLIN] * 8 + [c.ENEMY_SLIME] * 2
            elif self.current_level <= 3:
                # Gradual difficulty: Goblin 50%, Slime 30%, Skeleton 20%
                enemy_types = [c.ENEMY_GOBLIN] * 5 + [c.ENEMY_SLIME] * 3 + [c.ENEMY_SKELETON] * 2
            elif self.current_level <= 5:
                # Mid-game variety: Goblin 20%, Slime 20%, Skeleton 40%, Orc 20%
                enemy_types = [c.ENEMY_GOBLIN] * 2 + [c.ENEMY_SLIME] * 2 + [c.ENEMY_SKELETON] * 4 + [c.ENEMY_ORC] * 2
            elif self.current_level <= 9:
                # Challenging mix: Skeleton 25%, Orc 35%, Demon 40%
                enemy_types = [c.ENEMY_SKELETON] * 25 + [c.ENEMY_ORC] * 35 + [c.ENEMY_DEMON] * 40
            elif self.current_level <= 14:
                # Dragons introduced: Skeleton 10%, Orc 20%, Demon 60%, Dragon 10%
                enemy_types = [c.ENEMY_SKELETON] * 1 + [c.ENEMY_ORC] * 2 + [c.ENEMY_DEMON] * 6 + [c.ENEMY_DRAGON] * 1
            elif self.current_level <= 19:
                # Dragons common: Orc 10%, Demon 50%, Dragon 40%
                enemy_types = [c.ENEMY_ORC] * 1 + [c.ENEMY_DEMON] * 5 + [c.ENEMY_DRAGON] * 4
            else:
                # End-game gauntlet (20+): Demon 50%, Dragon 50%
                enemy_types = [c.ENEMY_DEMON] * 1 + [c.ENEMY_DRAGON] * 1

            enemy_type = random.choice(enemy_types)
            x, y = self._get_spawn_position()

            # Determine which room the enemy spawned in
            starting_room = self.dungeon.get_room_at(x, y)

            enemy = Enemy(x, y, enemy_type, level_modifier, starting_room)
            self.enemies.append(enemy)

            # Track rooms with enemies
            if starting_room is not None:
                self.rooms_with_enemies.add(starting_room)

    def _spawn_items(self):
        """Spawn items on current level"""
        self.items = []

        # Regular item spawning
        for _ in range(c.ITEMS_PER_LEVEL):
            # Choose item type
            item_types = [c.ITEM_HEALTH_POTION, c.ITEM_SWORD, c.ITEM_SHIELD, c.ITEM_BOOTS, c.ITEM_RING, c.ITEM_GOLD_COIN]
            weights = [5, 3, 2, 2, 2, 10]  # Gold coins most common (score tracking)
            item_type = random.choices(item_types, weights=weights)[0]

            # Determine rarity based on dungeon level
            rarity = self._determine_item_rarity()

            # Generate random affixes for rare+ items
            affixes = {}
            if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
                affixes = self._generate_item_affixes(rarity)

            x, y = self._get_spawn_position()
            item = Item(x, y, item_type, rarity, affixes)
            self.items.append(item)

        # Spawn treasure chests in rooms with enemies (as rewards)
        if hasattr(self, 'rooms_with_enemies') and self.rooms_with_enemies:
            # Spawn 1-2 chests per level in enemy rooms
            num_chests = min(2, max(1, len(self.rooms_with_enemies) // 3))

            # Select random rooms with enemies
            rooms_for_chests = random.sample(list(self.rooms_with_enemies),
                                            min(num_chests, len(self.rooms_with_enemies)))

            for room in rooms_for_chests:
                # Spawn chest in random position within this room
                x, y = room.get_random_point()

                # Ensure position is not occupied
                attempts = 0
                while self._is_position_occupied(x, y) and attempts < 10:
                    x, y = room.get_random_point()
                    attempts += 1

                # Determine rarity (chests use same rarity system)
                rarity = self._determine_item_rarity()

                chest = Item(x, y, c.ITEM_TREASURE_CHEST, rarity, {})
                self.items.append(chest)

    def _determine_item_rarity(self) -> str:
        """Determine item rarity based on dungeon level"""
        # Higher levels have better drop rates
        level_factor = min(self.current_level / 10, 1.0)

        rarities = [
            c.RARITY_COMMON,
            c.RARITY_UNCOMMON,
            c.RARITY_RARE,
            c.RARITY_EPIC,
            c.RARITY_LEGENDARY
        ]

        # Weights adjusted by dungeon level
        weights = [
            max(60 - level_factor * 40, 20),  # Common: 60% -> 20%
            30 + level_factor * 10,            # Uncommon: 30% -> 40%
            8 + level_factor * 20,             # Rare: 8% -> 28%
            2 + level_factor * 12,             # Epic: 2% -> 14%
            level_factor * 5                   # Legendary: 0% -> 5%
        ]

        return random.choices(rarities, weights=weights)[0]

    def _generate_item_affixes(self, rarity: str) -> dict:
        """Generate random stat affixes for an item"""
        affixes = {}
        num_affixes = {
            c.RARITY_RARE: 1,
            c.RARITY_EPIC: 2,
            c.RARITY_LEGENDARY: 3
        }.get(rarity, 0)

        possible_stats = ["attack", "defense", "hp"]
        selected_stats = random.sample(possible_stats, min(num_affixes, len(possible_stats)))

        for stat in selected_stats:
            if stat == "hp":
                affixes["hp"] = random.randint(5, 15)
            else:
                affixes[stat] = random.randint(1, 5)

        return affixes

    def _get_spawn_position(self) -> Tuple[int, int]:
        """Get a valid spawn position away from player"""
        attempts = 0
        while attempts < 50:
            x, y = self.dungeon.get_random_floor_position()

            # Check distance from player
            if self.player:
                dist = abs(x - self.player.x) + abs(y - self.player.y)
                if dist > 5:  # Spawn at least 5 tiles away
                    # Check not occupied
                    if not self._is_position_occupied(x, y):
                        return (x, y)

            attempts += 1

        # Fallback
        return self.dungeon.get_random_floor_position()

    def _is_position_occupied(self, x: int, y: int) -> bool:
        """Check if position is occupied by entity"""
        if self.player and self.player.x == x and self.player.y == y:
            return True

        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return True

        return False

    def player_move(self, dx: int, dy: int) -> bool:
        """
        Attempt to move player.
        Returns True if turn was consumed.
        """
        if self.game_over or not self.player:
            return False

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # Check if trying to attack enemy
        enemy = self._get_enemy_at(new_x, new_y)
        if enemy:
            self._player_attack(enemy)
            self._enemy_turn()
            self._reduce_ability_cooldowns()
            return True

        # Check if walkable
        if not self.dungeon.is_walkable(new_x, new_y):
            return False

        # Check for stairs
        if self.dungeon.get_tile(new_x, new_y) == c.TILE_STAIRS:
            self.player.start_move(new_x, new_y)
            self.update_camera()
            self.update_fov()
            self._descend_stairs()
            return True

        # Move player with animation
        self.player.start_move(new_x, new_y)
        self.update_camera()
        self.update_fov()

        # Play footstep sound
        self.audio_manager.play_footstep(position=(new_x, new_y),
                                        player_position=(new_x, new_y))

        # Check for item pickup
        self._check_item_pickup()

        # Enemy turn
        self._enemy_turn()

        # Reduce ability cooldowns
        self._reduce_ability_cooldowns()

        return True

    def use_ability(self, ability_index: int, target_x: int = None, target_y: int = None) -> bool:
        """
        Use an ability. Returns True if turn was consumed.
        """
        if self.game_over or not self.player:
            return False

        if ability_index < 0 or ability_index >= len(self.player.abilities):
            return False

        ability = self.player.abilities[ability_index]

        # Use player position as default target
        if target_x is None or target_y is None:
            target_x = self.player.x
            target_y = self.player.y

        # Use ability
        success, message = ability.use(self.player, (target_x, target_y), self)
        self.add_message(message, "event" if success else "damage")

        if success:
            # Enemy turn
            self._enemy_turn()
            # Reduce ability cooldowns
            self._reduce_ability_cooldowns()

        return success

    def _reduce_ability_cooldowns(self):
        """Reduce all ability cooldowns by 1"""
        for ability in self.player.abilities:
            ability.reduce_cooldown()

    def _player_attack(self, enemy: Enemy):
        """Player attacks enemy"""
        # Check if this is a backstab (Rogue attacking enemy that can't see them)
        is_backstab = False
        if self.player.class_type == c.CLASS_ROGUE:
            # Calculate enemy's FOV to see if they can see player
            enemy_fov = calculate_fov(self.dungeon, enemy.x, enemy.y, enemy.vision_radius)
            can_enemy_see_player = (self.player.x, self.player.y) in enemy_fov
            is_backstab = not can_enemy_see_player

        message, enemy_died, xp, was_backstab = combat.player_attack_enemy(self.player, enemy, is_backstab)
        damage = combat.calculate_damage(self.player.attack, enemy.defense)

        # Apply backstab multiplier to displayed damage
        if was_backstab:
            damage = int(damage * c.BACKSTAB_DAMAGE_MULTIPLIER)

        # Check if crit (rogue has crit chance)
        is_crit = hasattr(self.player, 'crit_chance') and random.random() < getattr(self.player, 'crit_chance', 0)

        # Play attack sound
        attack_strength = 'heavy' if damage > 15 else 'medium' if damage > 8 else 'light'
        self.audio_manager.play_attack_sound(attack_strength)

        # Play hit sound with positional audio
        self.audio_manager.play_hit_sound(is_crit, position=(enemy.x, enemy.y),
                                         player_position=(self.player.x, self.player.y))

        # Create animations (using RGB tuples instead of QColor)
        # Directional impact particles (spray away from player)
        # Backstab uses purple, crit uses gold, normal uses red
        if was_backstab:
            impact_color = c.COLOR_BACKSTAB_RGB  # Purple for backstab
        elif is_crit:
            impact_color = c.COLOR_CRITICAL_HIT_RGB  # Gold for crit
        else:
            impact_color = c.COLOR_NORMAL_HIT_RGB  # Red for normal

        self.anim_manager.add_directional_impact(
            enemy.x, enemy.y,
            self.player.x, self.player.y,
            impact_color, count=20 if (was_backstab or is_crit) else 12, is_crit=(is_crit or was_backstab)
        )

        self.anim_manager.add_floating_text(enemy.x, enemy.y, str(damage),
                                           c.COLOR_DAMAGE_TAKEN_RGB if not is_crit else c.COLOR_DAMAGE_CRIT_RGB,
                                           is_crit=is_crit)
        self.anim_manager.add_flash_effect(enemy.x, enemy.y, c.COLOR_FLASH_RGB)

        if enemy_died:
            # Enhanced death effect with enemy-specific particles
            self.anim_manager.add_death_burst(enemy.x, enemy.y, enemy.enemy_type)
            self.anim_manager.add_screen_shake(4.0, 0.2)

            # Play enemy death sound
            self.audio_manager.play_enemy_death(enemy.enemy_type, position=(enemy.x, enemy.y),
                                               player_position=(self.player.x, self.player.y))

        # Use more specific event types for better visual feedback
        if enemy_died:
            self.add_message(message, "kill")
        elif was_backstab:
            self.add_message(message, "crit")
        elif is_crit:
            self.add_message(message, "crit")
        else:
            self.add_message(message, "player_attack")

        if enemy_died:
            self.enemies.remove(enemy)
            leveled_up = self.player.gain_xp(xp)
            if leveled_up:
                self.add_message(f"Level up! You are now level {self.player.level}!", "levelup")
                self.anim_manager.add_heal_sparkles(self.player.x, self.player.y)
                self.audio_manager.play_levelup()

    def _enemy_turn(self):
        """Process enemy turns"""
        if self.game_over:
            return

        for enemy in self.enemies[:]:  # Copy list to allow modification
            # Reduce status effects
            enemy.reduce_status_effects()

            # Get AI action (pass game reference for line of sight checks)
            dx, dy = enemy.get_ai_action(self.player.get_pos(), self.dungeon, self)

            # Check if enemy just spotted player (trigger alert)
            if enemy.just_spotted_player:
                self.anim_manager.add_alert_particle(enemy)
                enemy.just_spotted_player = False  # Reset flag

            new_x = enemy.x + dx
            new_y = enemy.y + dy

            # Check if attacking player
            if new_x == self.player.x and new_y == self.player.y:
                message, player_died = combat.enemy_attack_player(enemy, self.player)
                damage = combat.calculate_damage(enemy.attack, self.player.defense)

                # Trigger attack animation (3D renderer)
                if hasattr(self, 'renderer') and self.renderer:
                    enemy_id = id(enemy)
                    self.renderer.trigger_enemy_attack(enemy_id)

                # Play enemy attack sound
                attack_strength = 'heavy' if damage > 12 else 'medium' if damage > 6 else 'light'
                self.audio_manager.play_attack_sound(attack_strength)

                # Play hit sound on player
                self.audio_manager.play_hit_sound(False, position=(self.player.x, self.player.y),
                                                 player_position=(self.player.x, self.player.y))

                # Create animations
                # Directional impact particles (spray away from enemy)
                self.anim_manager.add_directional_impact(
                    self.player.x, self.player.y,
                    enemy.x, enemy.y,
                    c.COLOR_DEATH_RGB, count=10
                )

                self.anim_manager.add_floating_text(self.player.x, self.player.y, str(damage), c.COLOR_DEATH_RGB)
                self.anim_manager.add_flash_effect(self.player.x, self.player.y, c.COLOR_DAMAGE_TAKEN_RGB)

                if player_died:
                    self.anim_manager.add_screen_shake(8.0, 0.3)
                    self.audio_manager.play_gameover()
                self.add_message(message, "enemy_attack")

                if player_died:
                    self.game_over = True
                    self.add_message("GAME OVER! Press R to restart.", "death")
                    return

            # Move if walkable and not occupied
            elif self.dungeon.is_walkable(new_x, new_y):
                if not self._is_position_occupied(new_x, new_y):
                    enemy.start_move(new_x, new_y)

    def _check_item_pickup(self):
        """Check if player is on item and pick it up"""
        for item in self.items[:]:
            if item.x == self.player.x and item.y == self.player.y:
                self.player.add_item(item)
                self.items.remove(item)

                # Determine message type based on item
                if item.item_type == c.ITEM_HEALTH_POTION:
                    msg_type = "potion"
                    self.anim_manager.add_heal_sparkles(self.player.x, self.player.y)
                    # Play potion sound
                    self.audio_manager.play_potion()
                elif item.item_type == c.ITEM_GOLD_COIN:
                    msg_type = "gold"
                    # Play coin sound
                    self.audio_manager.play_coin()
                elif item.item_type == c.ITEM_TREASURE_CHEST:
                    msg_type = "gold"  # Use gold message type for treasure
                    # Play coin sound (could add special treasure sound later)
                    self.audio_manager.play_coin()
                    # Add particle burst for treasure
                    self.anim_manager.add_particle_burst(self.player.x, self.player.y,
                                                        c.COLOR_GOLD_SPARKLE_RGB, count=12, particle_type="star")
                else:
                    # Use rarity-based event type for loot
                    if item.rarity in [c.RARITY_LEGENDARY, c.RARITY_EPIC]:
                        msg_type = "loot_legendary"
                    elif item.rarity == c.RARITY_RARE:
                        msg_type = "loot_rare"
                    else:
                        msg_type = "loot"

                    self.anim_manager.add_particle_burst(self.player.x, self.player.y,
                                                        c.COLOR_GOLD_SPARKLE_RGB, count=6, particle_type="star")
                    # Play item pickup sound based on rarity
                    self.audio_manager.play_item_pickup(item.rarity)
                    # Play equip sound
                    self.audio_manager.play_equip()

                # Display appropriate message
                if item.item_type == c.ITEM_GOLD_COIN:
                    # Calculate gold amount for message
                    base_value = c.ITEM_EFFECTS[c.ITEM_GOLD_COIN]["gold_value"]
                    rarity_multipliers = {
                        c.RARITY_COMMON: 1,
                        c.RARITY_UNCOMMON: 2,
                        c.RARITY_RARE: 5,
                        c.RARITY_EPIC: 10,
                        c.RARITY_LEGENDARY: 25
                    }
                    multiplier = rarity_multipliers.get(item.rarity, 1)
                    gold_amount = base_value * multiplier
                    self.add_message(f"Picked up {gold_amount} gold!", msg_type)
                elif item.item_type == c.ITEM_TREASURE_CHEST:
                    # Calculate gold amount for treasure chest
                    base_value = c.ITEM_EFFECTS[c.ITEM_TREASURE_CHEST]["gold_value"]
                    rarity_multipliers = {
                        c.RARITY_COMMON: 1,
                        c.RARITY_UNCOMMON: 2,
                        c.RARITY_RARE: 5,
                        c.RARITY_EPIC: 10,
                        c.RARITY_LEGENDARY: 25
                    }
                    multiplier = rarity_multipliers.get(item.rarity, 1)
                    gold_amount = base_value * multiplier
                    self.add_message(f"Found treasure chest with {gold_amount} gold!", msg_type)
                else:
                    self.add_message(f"Picked up {item.get_name()}!", msg_type)

    def _descend_stairs(self):
        """Descend to next level"""
        # Check if player has completed the final level
        if self.current_level >= c.MAX_LEVEL:
            self.victory = True
            self.add_message("You have conquered the dungeon! VICTORY!", "event")
            # Play victory sound (we'll add this to audio manager if it exists)
            # self.audio_manager.play_victory()
            return

        self.current_level += 1
        self.add_message(f"Descending to level {self.current_level}...", "stairs")

        # Play stairs sound
        self.audio_manager.play_stairs()

        # Announce biome change every 5 levels
        if self.current_level in [6, 11, 16, 21]:
            biome = c.get_biome_for_level(self.current_level)
            biome_names = {
                c.BIOME_CATACOMBS: "the Catacombs",
                c.BIOME_CAVES: "the Caves",
                c.BIOME_HELL: "the Infernal Depths",
                c.BIOME_ABYSS: "the Abyss",
            }
            if biome in biome_names:
                self.add_message(f"You enter {biome_names[biome]}...", "event")

        self._generate_level()

    def debug_skip_level(self):
        """Debug: Skip to next level"""
        # Check if already at max level
        if self.current_level >= c.MAX_LEVEL:
            self.victory = True
            self.add_message("DEBUG: Skipped to victory!", "event")
            return

        self.current_level += 1
        self.add_message(f"DEBUG: Skipped to level {self.current_level}", "event")

        # Announce biome change every 5 levels
        if self.current_level in [6, 11, 16, 21]:
            biome = c.get_biome_for_level(self.current_level)
            biome_names = {
                c.BIOME_CATACOMBS: "the Catacombs",
                c.BIOME_CAVES: "the Caves",
                c.BIOME_HELL: "the Infernal Depths",
                c.BIOME_ABYSS: "the Abyss",
            }
            if biome in biome_names:
                self.add_message(f"You enter {biome_names[biome]}...", "event")

        self._generate_level()

    def _get_enemy_at(self, x: int, y: int) -> Optional[Enemy]:
        """Get enemy at position"""
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy
        return None

    def update_fov(self):
        """
        Update field of view based on player position.
        Should be called after player movement or level generation.
        """
        if not self.player or not self.dungeon or not self.visibility_map:
            return

        # Calculate vision radius (Rogue gets bonus)
        vision_radius = c.PLAYER_VISION_RADIUS
        if self.player.class_type == c.CLASS_ROGUE:
            vision_radius += c.ROGUE_VISION_BONUS

        # Calculate visible tiles from player position
        visible_tiles = calculate_fov(
            self.dungeon,
            self.player.x,
            self.player.y,
            vision_radius
        )

        # Update visibility map
        self.visibility_map.update_visibility(visible_tiles)

    def has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Check if there's a clear line of sight between two points (no walls).
        Uses Bresenham's line algorithm.
        """
        # Get all points along the line
        points = self._bresenham_line(x1, y1, x2, y2)

        # Check if any point (except start and end) is a wall
        for i, (x, y) in enumerate(points):
            # Skip the start and end points
            if i == 0 or i == len(points) - 1:
                continue

            # Check if this point is a wall
            if not self.dungeon.is_walkable(x, y):
                return False

        return True

    def _bresenham_line(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """
        Get all points along a line using Bresenham's algorithm.
        Returns list of (x, y) tuples.
        """
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1

        while True:
            points.append((x, y))

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    def update(self, dt: float):
        """Update game state (called every frame)"""
        # Update entity animations
        if self.player:
            self.player.update(dt)

        for enemy in self.enemies:
            enemy.update(dt)

        for item in self.items:
            item.update(dt)

        # Spawn fog particles for atmosphere in dark areas
        self.fog_timer += dt
        if self.fog_timer >= 0.2:  # Every 0.2 seconds (faster spawning)
            self.fog_timer = 0.0
            # Spawn 2-4 fog particles (more particles)
            self.anim_manager.add_fog_particles(count=random.randint(2, 4))

        # Spawn ambient particles periodically
        self.ambient_timer += dt
        if self.ambient_timer >= 0.5:  # Every 0.5 seconds
            self.ambient_timer = 0.0
            # Spawn 2-4 ambient particles
            self.anim_manager.add_ambient_particles(count=random.randint(2, 4))

        # Spawn footstep particles during movement
        if self.player and self.player.is_moving:
            self._spawn_footstep_particles()

        # Update music intensity based on nearby enemies
        if self.player:
            # Count enemies within 8 tiles
            enemies_nearby = sum(1 for enemy in self.enemies
                               if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) <= 8)

            # Check if in recent combat (simple heuristic)
            in_combat = len(self.messages) > 0 and self.messages[-1][1] == "damage"

            self.audio_manager.update_music_intensity(enemies_nearby, in_combat)

    def _spawn_footstep_particles(self):
        """Spawn footstep particles based on walk cycle"""
        if not self.player:
            return

        # Spawn particles at specific points in the bob cycle (when foot touches ground)
        # Footstep happens when bob is at bottom of sine wave
        import math
        bob_speed = self.player._get_bob_speed()
        phase = (self.player.move_progress * math.pi * bob_speed) % (2 * math.pi)

        # Check if we're at a "step" moment (bottom of bob cycle)
        # We want to spawn when crossing certain phase thresholds
        step_threshold = 0.2  # Tolerance for detecting step moment

        # Check for step moments (bottom of sine waves at pi/2 and 3pi/2 for each cycle)
        cycles = int(self.player.move_progress * bob_speed)
        current_cycle_progress = (self.player.move_progress * bob_speed) % 1.0

        # Step happens at ~0.25 and ~0.75 of each cycle
        is_step_moment = (abs(current_cycle_progress - 0.25) < step_threshold or
                         abs(current_cycle_progress - 0.75) < step_threshold)

        # Only spawn if we haven't spawned recently (debounce)
        if not hasattr(self, '_last_footstep_phase'):
            self._last_footstep_phase = -1.0

        phase_diff = abs(self.player.move_progress - self._last_footstep_phase)

        if is_step_moment and phase_diff > 0.15:  # Minimum time between footsteps
            self._last_footstep_phase = self.player.move_progress
            self._create_footstep_particles()

    def _create_footstep_particles(self):
        """Create actual footstep particle burst"""
        if not self.player:
            return

        # Get class-specific particle style (using RGB tuples)
        if self.player.class_type == c.CLASS_WARRIOR:
            # Heavy dust cloud
            color = c.COLOR_BIOME_DUNGEON_RGB
            count = 6
            size_range = (2, 5)
        elif self.player.class_type == c.CLASS_MAGE:
            # Magical sparkles
            color = c.COLOR_BIOME_CATACOMBS_RGB
            count = 4
            size_range = (1, 3)
        elif self.player.class_type == c.CLASS_ROGUE:
            # Minimal, stealthy
            color = c.COLOR_BIOME_CAVES_RGB
            count = 2
            size_range = (1, 2)
        elif self.player.class_type == c.CLASS_RANGER:
            # Small leaves/dust
            color = c.COLOR_BIOME_HELL_RGB
            count = 4
            size_range = (1, 3)
        else:
            color = c.COLOR_BIOME_ABYSS_RGB
            count = 3
            size_range = (2, 4)

        # Spawn particles at player's display position
        display_x, display_y = self.player.get_display_pos()

        # Convert to pixel coordinates
        center_x = display_x * c.TILE_SIZE + c.TILE_SIZE / 2
        center_y = (display_y + 0.3) * c.TILE_SIZE + c.TILE_SIZE / 2  # Offset to feet
        for _ in range(count):
            # Spread particles horizontally
            offset_x = random.uniform(-c.TILE_SIZE / 4, c.TILE_SIZE / 4)
            offset_y = random.uniform(-c.TILE_SIZE / 8, c.TILE_SIZE / 8)

            # Small upward and outward velocity
            vx = random.uniform(-1, 1)
            vy = random.uniform(-0.5, -0.1)  # Slight upward

            size = random.uniform(*size_range)
            lifetime = random.uniform(0.2, 0.4)

            particle = Particle(
                center_x + offset_x,
                center_y + offset_y,
                vx, vy,
                color,
                size=size,
                lifetime=lifetime,
                particle_type="circle",
                apply_gravity=False
            )
            self.anim_manager.particles.append(particle)

    def add_message(self, message: str, msg_type: str = "event"):
        """Add message to message log with type for color coding"""
        self.messages.append((message, msg_type))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

        # Also send to visual combat log if callback is set
        if self.message_callback:
            self.message_callback(message, msg_type)

    def get_entity_at(self, x: int, y: int):
        """Get entity at position for rendering"""
        if self.player and self.player.x == x and self.player.y == y:
            return self.player

        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy

        for item in self.items:
            if item.x == x and item.y == y:
                return item

        return None
