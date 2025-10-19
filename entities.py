"""
Entity classes for Claude-Like
"""
from typing import Tuple, List
import constants as c


class Entity:
    """Base entity class with animation support"""
    def __init__(self, x: int, y: int, entity_type: str):
        # Grid position (logical, integer)
        self.x = x
        self.y = y
        self.entity_type = entity_type

        # Animation fields
        self.display_x = float(x)  # Visual position (interpolated)
        self.display_y = float(y)
        self.facing_direction = (0, 1)  # (dx, dy) - default facing down
        self.is_moving = False
        self.move_progress = 0.0  # 0.0 to 1.0
        self.move_duration = 0.2  # Seconds to complete movement
        self.move_start_x = float(x)
        self.move_start_y = float(y)
        self.move_target_x = float(x)
        self.move_target_y = float(y)
        self.idle_time = 0.0  # For idle breathing animation
        self.bob_offset = 0.0  # Vertical offset for walk bob

    def get_pos(self) -> Tuple[int, int]:
        """Get entity grid position"""
        return (self.x, self.y)

    def get_display_pos(self) -> Tuple[float, float]:
        """Get entity visual position with bob offset"""
        return (self.display_x, self.display_y + self.bob_offset)

    def set_pos(self, x: int, y: int):
        """Set entity position and immediately update display position"""
        self.x = x
        self.y = y
        self.display_x = float(x)
        self.display_y = float(y)
        self.is_moving = False
        self.move_progress = 1.0

    def start_move(self, target_x: int, target_y: int):
        """Start movement animation to target position"""
        # Update facing direction
        dx = target_x - self.x
        dy = target_y - self.y
        if dx != 0 or dy != 0:
            self.facing_direction = (dx, dy)

        # Update logical position immediately (for game logic)
        self.x = target_x
        self.y = target_y

        # Set up animation
        self.move_start_x = self.display_x
        self.move_start_y = self.display_y
        self.move_target_x = float(target_x)
        self.move_target_y = float(target_y)
        self.move_progress = 0.0
        self.is_moving = True

    def update(self, dt: float):
        """Update entity animations"""
        if self.is_moving:
            # Update movement progress
            self.move_progress += dt / self.move_duration
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.is_moving = False
                self.display_x = self.move_target_x
                self.display_y = self.move_target_y
                self.bob_offset = 0.0
            else:
                # Smooth interpolation (ease-out)
                t = self.move_progress
                smooth_t = 1.0 - (1.0 - t) * (1.0 - t)  # Ease-out quad

                # Lerp position
                self.display_x = self.move_start_x + (self.move_target_x - self.move_start_x) * smooth_t
                self.display_y = self.move_start_y + (self.move_target_y - self.move_start_y) * smooth_t

                # Calculate walking bob (sine wave)
                import math
                bob_amplitude = self._get_bob_amplitude()
                bob_speed = self._get_bob_speed()
                self.bob_offset = math.sin(self.move_progress * math.pi * bob_speed) * bob_amplitude
        else:
            # Idle breathing animation
            import math
            self.idle_time += dt
            idle_amplitude = 0.03  # Very subtle
            self.bob_offset = math.sin(self.idle_time * 0.8) * idle_amplitude

    def _get_bob_amplitude(self) -> float:
        """Get bob amplitude based on entity type - override in subclasses"""
        return 0.15  # Default bob height

    def _get_bob_speed(self) -> float:
        """Get bob speed (cycles per move) - override in subclasses"""
        return 2.0  # 2 full bobs per movement


class Player(Entity):
    """Player entity"""
    def __init__(self, x: int, y: int, class_type: str = c.CLASS_WARRIOR):
        super().__init__(x, y, c.ENTITY_PLAYER)
        self.class_type = class_type

        # Set class-specific stats
        stats = c.CLASS_STATS[class_type]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.base_attack = stats["attack"]
        self.base_defense = stats["defense"]

        # Class-specific attributes
        self.crit_chance = stats.get("crit_chance", 0.0)  # Rogue has crit chance
        self.dodge_chance = 0.15 if class_type == c.CLASS_ROGUE else 0.0  # Rogue can dodge

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50
        self.inventory = []
        self.gold = 0  # Track gold collected as score

        # Equipment slots
        self.equipment = {
            c.SLOT_WEAPON: None,
            c.SLOT_ARMOR: None,
            c.SLOT_ACCESSORY: None,
            c.SLOT_BOOTS: None,
        }

        # Abilities - will be set by game after creation
        self.abilities: List = []

    @property
    def attack(self) -> int:
        """Total attack including bonuses from equipment"""
        bonus = 0
        # Get bonus from weapon
        if self.equipment[c.SLOT_WEAPON]:
            bonus += self.equipment[c.SLOT_WEAPON].get_stat_bonus("attack")
        # Get bonus from accessories
        if self.equipment[c.SLOT_ACCESSORY]:
            bonus += self.equipment[c.SLOT_ACCESSORY].get_stat_bonus("attack")
        return self.base_attack + bonus

    @property
    def defense(self) -> int:
        """Total defense including bonuses from equipment"""
        bonus = 0
        # Get bonus from armor
        if self.equipment[c.SLOT_ARMOR]:
            bonus += self.equipment[c.SLOT_ARMOR].get_stat_bonus("defense")
        # Get bonus from boots
        if self.equipment[c.SLOT_BOOTS]:
            bonus += self.equipment[c.SLOT_BOOTS].get_stat_bonus("defense")
        # Get bonus from accessories
        if self.equipment[c.SLOT_ACCESSORY]:
            bonus += self.equipment[c.SLOT_ACCESSORY].get_stat_bonus("defense")
        return self.base_defense + bonus

    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if still alive"""
        self.hp = max(0, self.hp - damage)
        return self.hp > 0

    def heal(self, amount: int):
        """Heal HP"""
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount: int) -> bool:
        """Gain XP, return True if leveled up"""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            return True
        return False

    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.xp = 0
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)

        # Increase stats
        self.max_hp += 35
        self.hp = self.max_hp  # Full heal on level up
        self.base_attack += 7
        self.base_defense += 3

    def add_item(self, item: 'Item'):
        """Add item to inventory and apply effects"""
        # Consumables are used immediately
        if item.item_type == c.ITEM_HEALTH_POTION:
            self.heal(c.ITEM_EFFECTS[c.ITEM_HEALTH_POTION]["heal"])
            return  # Don't add to inventory

        # Gold coins add to score
        if item.item_type == c.ITEM_GOLD_COIN:
            base_value = c.ITEM_EFFECTS[c.ITEM_GOLD_COIN]["gold_value"]
            # Rarity multiplier: common=1, uncommon=2, rare=5, epic=10, legendary=25
            rarity_multipliers = {
                c.RARITY_COMMON: 1,
                c.RARITY_UNCOMMON: 2,
                c.RARITY_RARE: 5,
                c.RARITY_EPIC: 10,
                c.RARITY_LEGENDARY: 25
            }
            multiplier = rarity_multipliers.get(item.rarity, 1)
            gold_amount = base_value * multiplier
            self.gold += gold_amount
            return  # Don't add to inventory

        # Treasure chests add 10x gold to score
        if item.item_type == c.ITEM_TREASURE_CHEST:
            base_value = c.ITEM_EFFECTS[c.ITEM_TREASURE_CHEST]["gold_value"]
            # Rarity multiplier: common=1, uncommon=2, rare=5, epic=10, legendary=25
            rarity_multipliers = {
                c.RARITY_COMMON: 1,
                c.RARITY_UNCOMMON: 2,
                c.RARITY_RARE: 5,
                c.RARITY_EPIC: 10,
                c.RARITY_LEGENDARY: 25
            }
            multiplier = rarity_multipliers.get(item.rarity, 1)
            gold_amount = base_value * multiplier
            self.gold += gold_amount
            return  # Don't add to inventory

        # Equipment is automatically equipped
        if item.item_type in c.EQUIPMENT_TYPES:
            slot = c.EQUIPMENT_TYPES[item.item_type]
            # Unequip old item if exists
            if self.equipment[slot]:
                self.inventory.append(self.equipment[slot])
            # Equip new item
            self.equipment[slot] = item
        else:
            # Add to inventory
            self.inventory.append(item)

    def equip_item(self, item: 'Item') -> bool:
        """Equip an item from inventory. Returns True if successful"""
        if item not in self.inventory:
            return False

        if item.item_type not in c.EQUIPMENT_TYPES:
            return False

        slot = c.EQUIPMENT_TYPES[item.item_type]

        # Unequip old item
        if self.equipment[slot]:
            self.inventory.append(self.equipment[slot])

        # Equip new item
        self.inventory.remove(item)
        self.equipment[slot] = item
        return True

    def get_class_name(self) -> str:
        """Get display name for class"""
        names = {
            c.CLASS_WARRIOR: "Warrior",
            c.CLASS_MAGE: "Mage",
            c.CLASS_ROGUE: "Rogue",
            c.CLASS_RANGER: "Ranger",
        }
        return names.get(self.class_type, "Unknown")

    def _get_bob_amplitude(self) -> float:
        """Get bob amplitude based on class"""
        amplitudes = {
            c.CLASS_WARRIOR: 0.20,  # Heavy stomping
            c.CLASS_MAGE: 0.08,     # Floating glide
            c.CLASS_ROGUE: 0.12,    # Stealthy, subtle
            c.CLASS_RANGER: 0.15,   # Natural stride
        }
        return amplitudes.get(self.class_type, 0.15)

    def _get_bob_speed(self) -> float:
        """Get bob speed based on class"""
        speeds = {
            c.CLASS_WARRIOR: 1.5,   # Slow, heavy steps
            c.CLASS_MAGE: 2.5,      # Smooth, floating
            c.CLASS_ROGUE: 3.0,     # Quick, light steps
            c.CLASS_RANGER: 2.0,    # Balanced pace
        }
        return speeds.get(self.class_type, 2.0)


class Enemy(Entity):
    """Enemy entity"""
    def __init__(self, x: int, y: int, enemy_type: str, level_modifier: float = 1.0, starting_room=None):
        super().__init__(x, y, c.ENTITY_ENEMY)
        self.enemy_type = enemy_type

        # Get base stats and apply level modifier
        stats = c.ENEMY_STATS[enemy_type]
        self.max_hp = int(stats["hp"] * level_modifier)
        self.hp = self.max_hp
        self.attack = int(stats["attack"] * level_modifier)
        self.defense = int(stats["defense"] * level_modifier)
        self.xp_reward = int(stats["xp"] * level_modifier)

        # Status effects
        self.frozen_turns = 0

        # AI state for patrol/chase behavior
        self.starting_room = starting_room  # Room object where enemy spawned
        self.ai_state = "patrol"  # "patrol", "chase", or "search"
        self.has_seen_player = False  # Once true, enemy stays aggressive

        # Vision and tracking
        self.vision_radius = c.ENEMY_VISION_RADIUS  # How far enemy can see
        self.last_known_player_pos = None  # Last position where player was seen
        self.turns_since_seen_player = 0  # Counter for losing track
        self.search_turns_max = 5  # Give up search after this many turns
        self.just_spotted_player = False  # Flag for triggering alert animation

    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if still alive"""
        self.hp = max(0, self.hp - damage)
        return self.hp > 0

    def get_ai_action(self, player_pos: Tuple[int, int], dungeon_map, game=None) -> Tuple[int, int]:
        """
        Determine next move based on AI with FOV-aware patrol/chase/search behavior.

        States:
        - patrol: Stay in starting room, haven't seen player
        - chase: Can see player, move toward them
        - search: Lost sight, move to last known position
        """
        # Check if frozen
        if self.frozen_turns > 0:
            return (0, 0)  # Can't move when frozen

        # Calculate if player is in FOV (uses shadowcasting)
        can_see_player = False
        if game:
            # Adjust vision radius for Rogue (harder to detect)
            if hasattr(game.player, 'class_type') and game.player.class_type == c.CLASS_ROGUE:
                self.vision_radius = c.ENEMY_VISION_VS_ROGUE
            else:
                self.vision_radius = c.ENEMY_VISION_RADIUS

            # Calculate enemy's FOV
            from fov import calculate_fov
            enemy_fov = calculate_fov(dungeon_map, self.x, self.y, self.vision_radius)

            # Check if player is in FOV
            can_see_player = (player_pos[0], player_pos[1]) in enemy_fov

        # AI state machine based on vision
        if can_see_player:
            # STATE: CHASE - We can see the player
            # Detect if we just spotted them (transition from patrol/search to chase)
            if self.ai_state != "chase":
                self.just_spotted_player = True  # Trigger alert!

            self.ai_state = "chase"
            self.has_seen_player = True
            self.last_known_player_pos = player_pos
            self.turns_since_seen_player = 0
            return self._chase_player(player_pos)

        elif self.has_seen_player and self.last_known_player_pos is not None:
            # STATE: SEARCH - We've seen player before but lost sight
            self.turns_since_seen_player += 1

            if self.turns_since_seen_player >= self.search_turns_max:
                # Give up search, return to patrol
                self.ai_state = "patrol"
                self.last_known_player_pos = None
                self.turns_since_seen_player = 0
                return self._patrol_room()
            else:
                # Continue searching
                self.ai_state = "search"
                return self._search_last_position()

        else:
            # STATE: PATROL - Never seen player or gave up searching
            self.ai_state = "patrol"
            return self._patrol_room()

    def _chase_player(self, player_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Move towards player"""
        dx = 0 if self.x == player_pos[0] else (1 if player_pos[0] > self.x else -1)
        dy = 0 if self.y == player_pos[1] else (1 if player_pos[1] > self.y else -1)

        # Prefer horizontal or vertical movement (not diagonal)
        if abs(self.x - player_pos[0]) > abs(self.y - player_pos[1]):
            return (dx, 0)
        else:
            return (0, dy)

    def _search_last_position(self) -> Tuple[int, int]:
        """
        Move toward last known player position.
        Uses same logic as chase but targets last_known_player_pos.
        """
        if self.last_known_player_pos is None:
            return (0, 0)

        target_x, target_y = self.last_known_player_pos

        # If we've reached the last known position, give up
        if self.x == target_x and self.y == target_y:
            self.turns_since_seen_player = self.search_turns_max  # Force give up
            return (0, 0)

        # Move toward last known position
        dx = 0 if self.x == target_x else (1 if target_x > self.x else -1)
        dy = 0 if self.y == target_y else (1 if target_y > self.y else -1)

        # Prefer horizontal or vertical movement
        if abs(self.x - target_x) > abs(self.y - target_y):
            return (dx, 0)
        else:
            return (0, dy)

    def _random_move(self) -> Tuple[int, int]:
        """Move randomly"""
        import random
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
        return random.choice(moves)

    def _patrol_room(self) -> Tuple[int, int]:
        """
        Move randomly within starting room boundaries.
        If no starting room, fallback to random movement.
        """
        import random

        if not self.starting_room:
            return self._random_move()

        # Try to find a valid move within the room
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
        valid_moves = []

        for dx, dy in moves:
            new_x = self.x + dx
            new_y = self.y + dy

            # Check if new position is within starting room
            if (self.starting_room.x <= new_x < self.starting_room.x + self.starting_room.width and
                self.starting_room.y <= new_y < self.starting_room.y + self.starting_room.height):
                valid_moves.append((dx, dy))

        # If we have valid moves, choose one; otherwise stay still
        if valid_moves:
            return random.choice(valid_moves)
        else:
            return (0, 0)

    def reduce_status_effects(self):
        """Reduce duration of status effects"""
        if self.frozen_turns > 0:
            self.frozen_turns -= 1

    def _get_bob_amplitude(self) -> float:
        """Get bob amplitude based on enemy type"""
        amplitudes = {
            c.ENEMY_GOBLIN: 0.18,    # Quick, jittery
            c.ENEMY_SKELETON: 0.14,  # Rattling, uneven
            c.ENEMY_DRAGON: 0.25,    # Heavy, imposing
        }
        return amplitudes.get(self.enemy_type, 0.15)

    def _get_bob_speed(self) -> float:
        """Get bob speed based on enemy type"""
        speeds = {
            c.ENEMY_GOBLIN: 3.5,     # Fast, nervous movement
            c.ENEMY_SKELETON: 2.2,   # Jerky, unnatural
            c.ENEMY_DRAGON: 1.2,     # Slow, powerful
        }
        return speeds.get(self.enemy_type, 2.0)


class Item(Entity):
    """Item entity"""
    def __init__(self, x: int, y: int, item_type: str, rarity: str = "common", affixes: dict = None):
        super().__init__(x, y, c.ENTITY_ITEM)
        self.item_type = item_type
        self.rarity = rarity  # common, uncommon, rare, epic, legendary
        self.affixes = affixes or {}  # Additional stat modifiers

    def get_stat_bonus(self, stat_name: str) -> int:
        """Get bonus for a specific stat"""
        # Base bonus from item effects
        base_bonus = c.ITEM_EFFECTS.get(self.item_type, {}).get(stat_name, 0)

        # Additional bonus from affixes
        affix_bonus = self.affixes.get(stat_name, 0)

        # Rarity multiplier
        rarity_mult = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0,
        }.get(self.rarity, 1.0)

        return int((base_bonus + affix_bonus) * rarity_mult)

    def get_name(self) -> str:
        """Get item display name"""
        base_names = {
            c.ITEM_HEALTH_POTION: "Health Potion",
            c.ITEM_SWORD: "Sword",
            c.ITEM_SHIELD: "Shield",
            c.ITEM_BOOTS: "Boots",
            c.ITEM_RING: "Ring",
        }
        base_name = base_names.get(self.item_type, "Unknown Item")

        # Add rarity prefix for non-common items
        if self.rarity != "common":
            rarity_name = self.rarity.capitalize()
            base_name = f"{rarity_name} {base_name}"

        return base_name
