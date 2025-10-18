"""
Helmet HUD 3D Widget

A unified, immersive HUD design that resembles looking through a futuristic helmet visor.
All UI elements are consolidated into corner panels and bottom displays for minimal viewport obstruction.
"""

from typing import Optional, List
from ursina import Entity, Text, color, Vec2
from game import Game
import constants as c
from ui3d.minimap_3d import MiniMap3D


class CombatLogEntry:
    """Single combat log entry with fade effect"""
    def __init__(self, message: str, msg_type: str, lifetime: float = 5.0):
        self.message = message
        self.msg_type = msg_type
        self.lifetime = lifetime
        self.age = 0.0
        self.text_entity: Optional[Text] = None


class HelmetHUD3D:
    """
    Unified Helmet HUD - all UI in one cohesive design

    Layout:
    ╭─ TOP-LEFT ────╮                    ╭─ TOP-RIGHT ──────╮
    │ Warrior Lv5   │                    │ ATK Sword  DEF Armor  │
    │ ████ 120/150HP│                    │ ACC Ring  BOT Boots  │
    │ ███ 450/1000XP│                    │                  │
    ╰───────────────╯                    ╰──────────────────╯

                [3D GAME VIEWPORT]

    ╭─ COMBAT & ITEMS ────────────────────────────────────╮
    │ • You hit Goblin for 15 dmg                         │
    │ • Iron Sword nearby (2 tiles) +5 ATK               │
    ╰─────────────────────────────────────────────────────╯

    [Fire][Heal][Dash]           ATK 12 DEF 5 D:12 MAP 30%
     [1]   [2]   [3]
    """

    # Color mapping for item rarities (RGB tuples, 0-1 range)
    RARITY_COLORS = {
        c.RARITY_COMMON: (0.7, 0.7, 0.7),      # Gray
        c.RARITY_UNCOMMON: (0.4, 0.8, 0.4),    # Green
        c.RARITY_RARE: (0.4, 0.6, 1.0),        # Blue
        c.RARITY_EPIC: (0.8, 0.4, 1.0),        # Purple
        c.RARITY_LEGENDARY: (1.0, 0.7, 0.0),   # Orange/Gold
    }

    # Message type colors for combat log
    MESSAGE_COLORS = {
        "damage": (1.0, 0.5, 0.5),    # Red
        "heal": (0.5, 1.0, 0.5),      # Green
        "loot": (1.0, 0.9, 0.3),      # Gold
        "event": (0.7, 0.7, 0.7),     # Gray
        "level_up": (0.3, 1.0, 1.0),  # Cyan
    }

    def __init__(self, game: Game, parent: Optional[Entity] = None):
        """
        Initialize Helmet HUD

        Args:
            game: Game instance
            parent: Parent entity (camera.ui)
        """
        self.game = game
        self.parent = parent

        # Combat log entries
        self.combat_log_entries: List[CombatLogEntry] = []
        self.MAX_LOG_ENTRIES = 5

        # ===== TOP-LEFT PANEL (Player Stats) =====
        self.top_left_panel: Optional[Entity] = None
        self.class_level_text: Optional[Text] = None
        self.hp_bar_bg: Optional[Entity] = None
        self.hp_bar_fill: Optional[Entity] = None
        self.hp_text: Optional[Text] = None
        self.xp_bar_bg: Optional[Entity] = None
        self.xp_bar_fill: Optional[Entity] = None
        self.xp_text: Optional[Text] = None
        self.gold_text: Optional[Text] = None

        # ===== TOP-RIGHT PANEL (Equipment) =====
        self.top_right_panel: Optional[Entity] = None
        self.weapon_text: Optional[Text] = None
        self.armor_text: Optional[Text] = None
        self.accessory_text: Optional[Text] = None
        self.boots_text: Optional[Text] = None

        # ===== BOTTOM-CENTER PANEL (Combat Log + Nearby Items) =====
        self.bottom_center_panel: Optional[Entity] = None
        self.log_title: Optional[Text] = None
        # Combat log entries created dynamically

        # ===== BOTTOM-LEFT (Abilities) =====
        self.bottom_left_panel: Optional[Entity] = None
        self.ability_slots: List['AbilitySlot'] = []

        # ===== BOTTOM-RIGHT (Quick Stats) =====
        self.attack_text: Optional[Text] = None
        self.defense_text: Optional[Text] = None
        self.depth_text: Optional[Text] = None
        self.exploration_text: Optional[Text] = None
        self.stealth_text: Optional[Text] = None

        # ===== MINIMAP =====
        self.minimap: Optional[MiniMap3D] = None

        # Cached values for conditional updates
        self._last_hp = 0
        self._last_max_hp = 0
        self._last_xp = 0
        self._last_xp_to_next = 0
        self._last_level = 0
        self._last_gold = 0
        self._last_weapon = None
        self._last_armor = None
        self._last_accessory = None
        self._last_boots = None
        self._last_attack = 0
        self._last_defense = 0
        self._last_depth = 0
        self._last_exploration = 0.0
        self._last_stealth_status = ""

        # Create all UI elements
        self._create_ui()

        print("✓ HelmetHUD3D initialized (unified HUD design)")

    def _create_ui(self):
        """Create all HUD elements"""
        self._create_top_left_panel()
        self._create_top_right_panel()
        self._create_bottom_center_panel()
        self._create_bottom_left_abilities()
        self._create_bottom_right_stats()
        self._create_minimap()

    # ========== TOP-LEFT PANEL (Player Stats) ==========
    def _create_top_left_panel(self):
        """Create top-left corner panel with player stats"""
        pos_x = -0.85
        pos_y = 0.45
        panel_width = 0.50  # Increased from 0.40 to fit larger numbers
        panel_height = 0.30  # Increased from 0.28

        # Background panel with rounded appearance (darker blue, more opaque)
        self.top_left_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),  # More opaque
            position=(pos_x, pos_y, 10),  # Far back z-level (behind text)
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),  # Slightly more visible
            position=(pos_x + 0.002, pos_y - 0.002, 9),  # In front of background
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Class and Level
        self.class_level_text = Text(
            text="Warrior - Level 1",
            parent=self.parent,
            position=(pos_x + 0.01, pos_y - 0.03, -10),  # Low z-level (in front)
            scale=1.2,
            color=color.rgb(0.3, 1.0, 1.0),  # Cyan
            origin=(-0.5, 0.5),
            eternal=True
        )

        # HP Bar
        hp_bar_y = pos_y - 0.09
        bar_width = 0.38  # Increased from 0.30 to accommodate larger numbers
        bar_height = 0.04

        self.hp_bar_bg = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.1, 0.1, 0.1, 0.9),  # More opaque
            position=(pos_x + 0.01, hp_bar_y, 5),  # Behind fill
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.hp_bar_fill = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgb(0.3, 1.0, 0.3),  # Bright green
            position=(pos_x + 0.01, hp_bar_y, 4),  # In front of bg
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.hp_text = Text(
            text="100/100 HP",
            parent=self.parent,
            position=(pos_x + 0.01, hp_bar_y - 0.055, -10),  # Low z-level (in front)
            scale=1.0,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        # XP Bar
        xp_bar_y = pos_y - 0.17  # Adjusted for new spacing

        self.xp_bar_bg = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.1, 0.1, 0.1, 0.9),  # More opaque
            position=(pos_x + 0.01, xp_bar_y, 5),  # Behind fill
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.xp_bar_fill = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgb(1.0, 0.85, 0.0),  # Gold
            position=(pos_x + 0.01, xp_bar_y, 4),  # In front of bg
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.xp_text = Text(
            text="0/100 XP",
            parent=self.parent,
            position=(pos_x + 0.01, xp_bar_y - 0.055, -10),  # Low z-level (in front)
            scale=1.0,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Gold counter (below XP bar)
        gold_y = xp_bar_y - 0.10
        self.gold_text = Text(
            text="Gold: 0",
            parent=self.parent,
            position=(pos_x + 0.01, gold_y, -10),
            scale=1.2,  # Larger to emphasize score
            color=color.rgb(1.0, 0.84, 0.0),  # Gold color
            origin=(-0.5, 0.5),
            eternal=True
        )

    # ========== TOP-RIGHT PANEL (Equipment) ==========
    def _create_top_right_panel(self):
        """Create top-right corner panel with equipment"""
        pos_x = 0.35
        pos_y = 0.45
        panel_width = 0.50
        panel_height = 0.28

        # Background panel
        self.top_right_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),  # More opaque
            position=(pos_x, pos_y, 10),  # Far back z-level (behind text)
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),  # Slightly more visible
            position=(pos_x + 0.002, pos_y - 0.002, 9),  # In front of background
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Equipment slots (2x2 grid layout) - moved up since no title
        line_height = 0.055
        col_offset = 0.22
        start_y = pos_y - 0.04  # Start higher without title

        # Column 1: Weapon & Armor
        self.weapon_text = Text(
            text="ATK None",
            parent=self.parent,
            position=(pos_x + 0.01, start_y, -10),  # Low z-level (in front)
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.armor_text = Text(
            text="DEF None",
            parent=self.parent,
            position=(pos_x + 0.01, start_y - line_height, -10),  # Low z-level (in front)
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Column 2: Accessory & Boots
        self.accessory_text = Text(
            text="ACC None",
            parent=self.parent,
            position=(pos_x + 0.01 + col_offset, start_y, -10),  # Low z-level (in front)
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.boots_text = Text(
            text="BOT None",
            parent=self.parent,
            position=(pos_x + 0.01 + col_offset, start_y - line_height, -10),  # Low z-level (in front)
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

    # ========== BOTTOM-CENTER PANEL (Combat Log + Nearby Items) ==========
    def _create_bottom_center_panel(self):
        """Create bottom-center panel for combat log and nearby items"""
        pos_x = -0.40
        pos_y = -0.30
        panel_width = 0.80
        panel_height = 0.18

        # Background panel
        self.bottom_center_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),  # More opaque
            position=(pos_x, pos_y, 10),  # Far back z-level (behind text)
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),  # Slightly more visible
            position=(pos_x + 0.002, pos_y - 0.002, 9),  # In front of background
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Title
        self.log_title = Text(
            text="[COMBAT LOG]",
            parent=self.parent,
            position=(pos_x + 0.01, pos_y - 0.02, -10),  # Low z-level (in front), uses updated pos_x
            scale=0.9,
            color=color.rgb(0.3, 1.0, 1.0),  # Cyan
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Combat log entries created dynamically in add_message()

    # ========== BOTTOM-LEFT (Abilities) ==========
    def _create_bottom_left_abilities(self):
        """Create bottom-left ability slots with background panel"""
        pos_x = -0.85
        pos_y = -0.30  # Aligned with combat log and minimap level
        panel_width = 0.40  # Wider to fit slots properly
        panel_height = 0.16  # Smaller height

        # Background panel (matching other HUD sections)
        self.bottom_left_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),  # More opaque
            position=(pos_x, pos_y, 10),  # Far back z-level (behind text)
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),  # Slightly more visible
            position=(pos_x + 0.002, pos_y - 0.002, 9),  # In front of background
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Create ability slots - properly centered within panel
        slot_size = 0.09
        num_slots = 3

        # Calculate equal spacing around and between slots
        total_slot_width = num_slots * slot_size
        total_spacing = panel_width - total_slot_width
        single_spacing = total_spacing / (num_slots + 1)  # Space before, between, and after slots

        # First slot starts at panel left edge + one spacing + half slot size (for center)
        start_x = pos_x + single_spacing + (slot_size / 2)
        start_y = pos_y - 0.08  # Adjusted for smaller panel
        slot_spacing = slot_size + single_spacing  # Distance between slot centers

        for i in range(3):
            slot_x = start_x + (i * slot_spacing)
            slot = AbilitySlot(
                ability_index=i,
                parent=self.parent,
                position=Vec2(slot_x, start_y),
                slot_size=slot_size
            )
            self.ability_slots.append(slot)

    # ========== BOTTOM-RIGHT (Quick Stats) ==========
    def _create_bottom_right_stats(self):
        """Create bottom-right quick stats display"""
        pos_x = 0.35
        pos_y = -0.75
        line_height = 0.045

        # Attack
        self.attack_text = Text(
            text="ATK 10",
            parent=self.parent,
            position=(pos_x, pos_y, -10),  # Low z-level (in front)
            scale=1.1,
            color=color.rgb(1.0, 0.5, 0.5),  # Red
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Defense
        self.defense_text = Text(
            text="DEF 5",
            parent=self.parent,
            position=(pos_x + 0.12, pos_y, -10),  # Low z-level (in front)
            scale=1.1,
            color=color.rgb(0.5, 0.8, 1.0),  # Blue
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Depth
        self.depth_text = Text(
            text="D:1",
            parent=self.parent,
            position=(pos_x + 0.24, pos_y, -10),  # Low z-level (in front)
            scale=1.1,
            color=color.rgb(1.0, 0.9, 0.3),  # Gold
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Exploration
        self.exploration_text = Text(
            text="MAP 0%",
            parent=self.parent,
            position=(pos_x + 0.40, pos_y, -10),  # Low z-level (in front)
            scale=1.1,
            color=color.rgb(0.5, 1.0, 0.5),  # Green
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Stealth (Rogue only)
        self.stealth_text = Text(
            text="",
            parent=self.parent,
            position=(pos_x, pos_y - line_height, -10),  # Low z-level (in front)
            scale=1.0,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

    # ========== MINIMAP ==========
    def _create_minimap(self):
        """Create minimap widget"""
        if c.MINIMAP_ENABLED:
            self.minimap = MiniMap3D(
                game=self.game,
                parent=self.parent,
                mode=c.MINIMAP_MODE
            )

    # ========== UPDATE METHODS ==========
    def update(self, dt: float, camera_yaw: float = 0.0):
        """Update all HUD elements

        Args:
            dt: Delta time
            camera_yaw: Camera yaw in degrees (for minimap orientation)
        """
        if not self.game.player:
            return

        self._update_player_stats()
        self._update_equipment()
        self._update_abilities()
        self._update_quick_stats()
        self._update_combat_log(dt)
        self._update_nearby_items()

        # Update minimap
        if self.minimap:
            self.minimap.update(dt, camera_yaw)

    def _update_player_stats(self):
        """Update top-left player stats panel"""
        player = self.game.player

        # Class and level
        if player.level != self._last_level:
            class_name = player.get_class_name()
            self.class_level_text.text = f"{class_name} - Level {player.level}"
            self._last_level = player.level

        # HP bar
        if player.hp != self._last_hp or player.max_hp != self._last_max_hp:
            hp_percent = player.hp / player.max_hp if player.max_hp > 0 else 0
            self.hp_bar_fill.scale_x = 0.38 * hp_percent  # Updated to match new bar width

            # Color code based on HP percentage
            if hp_percent > 0.6:
                self.hp_bar_fill.color = color.rgb(0.3, 1.0, 0.3)  # Green
            elif hp_percent > 0.3:
                self.hp_bar_fill.color = color.rgb(1.0, 0.9, 0.0)  # Yellow
            else:
                self.hp_bar_fill.color = color.rgb(1.0, 0.3, 0.3)  # Red

            self.hp_text.text = f"{player.hp}/{player.max_hp} HP"
            self._last_hp = player.hp
            self._last_max_hp = player.max_hp

        # XP bar
        if player.xp != self._last_xp or player.xp_to_next_level != self._last_xp_to_next:
            xp_percent = player.xp / player.xp_to_next_level if player.xp_to_next_level > 0 else 0
            self.xp_bar_fill.scale_x = 0.38 * xp_percent  # Updated to match new bar width
            self.xp_text.text = f"{player.xp}/{player.xp_to_next_level} XP"
            self._last_xp = player.xp
            self._last_xp_to_next = player.xp_to_next_level

        # Gold counter
        if player.gold != self._last_gold:
            self.gold_text.text = f"Gold: {player.gold}"
            self._last_gold = player.gold

    def _update_equipment(self):
        """Update top-right equipment panel"""
        player = self.game.player

        # Weapon
        weapon = player.equipment[c.SLOT_WEAPON]
        if weapon != self._last_weapon:
            if weapon:
                name = weapon.get_name()
                item_color = self.RARITY_COLORS.get(weapon.rarity, (1, 1, 1))
                self.weapon_text.text = f"ATK {name}"
                self.weapon_text.color = color.rgb(*item_color)
            else:
                self.weapon_text.text = "ATK None"
                self.weapon_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_weapon = weapon

        # Armor
        armor = player.equipment[c.SLOT_ARMOR]
        if armor != self._last_armor:
            if armor:
                name = armor.get_name()
                item_color = self.RARITY_COLORS.get(armor.rarity, (1, 1, 1))
                self.armor_text.text = f"DEF {name}"
                self.armor_text.color = color.rgb(*item_color)
            else:
                self.armor_text.text = "DEF None"
                self.armor_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_armor = armor

        # Accessory
        accessory = player.equipment[c.SLOT_ACCESSORY]
        if accessory != self._last_accessory:
            if accessory:
                name = accessory.get_name()
                item_color = self.RARITY_COLORS.get(accessory.rarity, (1, 1, 1))
                self.accessory_text.text = f"ACC {name}"
                self.accessory_text.color = color.rgb(*item_color)
            else:
                self.accessory_text.text = "ACC None"
                self.accessory_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_accessory = accessory

        # Boots
        boots = player.equipment[c.SLOT_BOOTS]
        if boots != self._last_boots:
            if boots:
                name = boots.get_name()
                item_color = self.RARITY_COLORS.get(boots.rarity, (1, 1, 1))
                self.boots_text.text = f"BOT {name}"
                self.boots_text.color = color.rgb(*item_color)
            else:
                self.boots_text.text = "BOT None"
                self.boots_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_boots = boots

    def _update_abilities(self):
        """Update bottom-left ability slots"""
        if not self.game.player or not self.game.player.abilities:
            return

        for i, slot in enumerate(self.ability_slots):
            if i < len(self.game.player.abilities):
                ability = self.game.player.abilities[i]
                slot.update_ability(ability)
            else:
                slot.update_ability(None)

    def _update_quick_stats(self):
        """Update bottom-right quick stats"""
        player = self.game.player

        # Attack
        if player.attack != self._last_attack:
            self.attack_text.text = f"ATK {player.attack}"
            self._last_attack = player.attack

        # Defense
        if player.defense != self._last_defense:
            self.defense_text.text = f"DEF {player.defense}"
            self._last_defense = player.defense

        # Depth
        if self.game.current_level != self._last_depth:
            self.depth_text.text = f"D:{self.game.current_level}"
            self._last_depth = self.game.current_level

        # Exploration
        exploration_percent = self._calculate_exploration_percentage()
        if abs(exploration_percent - self._last_exploration) > 0.1:
            self.exploration_text.text = f"MAP {exploration_percent:.0f}%"
            self._last_exploration = exploration_percent

        # Stealth (Rogue only)
        if player.class_type == c.CLASS_ROGUE:
            stealth_status = self._get_stealth_status()
            if stealth_status != self._last_stealth_status:
                self.stealth_text.text = stealth_status
                if "HIDDEN" in stealth_status:
                    self.stealth_text.color = color.green
                else:
                    self.stealth_text.color = color.red
                self._last_stealth_status = stealth_status
        else:
            if self._last_stealth_status != "":
                self.stealth_text.text = ""
                self._last_stealth_status = ""

    def _update_combat_log(self, dt: float):
        """Update combat log with fade effects"""
        # Age all entries
        for entry in self.combat_log_entries:
            entry.age += dt

        # Remove expired entries
        expired = [e for e in self.combat_log_entries if e.age > e.lifetime]
        for entry in expired:
            if entry.text_entity:
                entry.text_entity.disable()
            self.combat_log_entries.remove(entry)

        # Update positions and fade
        pos_x = -0.39
        pos_y = -0.36
        line_height = 0.030

        for i, entry in enumerate(self.combat_log_entries):
            if entry.text_entity:
                y_pos = pos_y - (i * line_height)  # FIXED: Subtract to go downward
                entry.text_entity.position = (pos_x, y_pos, -10)  # Low z-level (in front)

                # Fade effect
                alpha = 1.0 - (entry.age / entry.lifetime)
                msg_color = self.MESSAGE_COLORS.get(entry.msg_type, (0.7, 0.7, 0.7))
                entry.text_entity.color = color.rgba(*msg_color, alpha)

    def _update_nearby_items(self):
        """Update nearby items in combat log area (shows below combat messages)"""
        pass

    def add_message(self, message: str, msg_type: str = "event"):
        """Add a message to the combat log"""
        # Remove oldest if at max capacity
        if len(self.combat_log_entries) >= self.MAX_LOG_ENTRIES:
            oldest = self.combat_log_entries.pop(0)
            if oldest.text_entity:
                oldest.text_entity.disable()

        # Create new entry
        entry = CombatLogEntry(message, msg_type, lifetime=5.0)
        msg_color = self.MESSAGE_COLORS.get(msg_type, (0.7, 0.7, 0.7))

        # Create text entity
        entry.text_entity = Text(
            text=f"• {message}",
            parent=self.parent,
            position=(-0.39, -0.36, -10),  # Low z-level (in front), will be repositioned in update
            scale=0.9,
            color=color.rgba(*msg_color, 1.0),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.combat_log_entries.append(entry)

    # ========== HELPER METHODS ==========
    def _calculate_exploration_percentage(self) -> float:
        """Calculate percentage of dungeon explored"""
        if not self.game.visibility_map or not self.game.dungeon:
            return 0.0

        explored_count = self.game.visibility_map.count_explored()

        total_floor_tiles = sum(
            1 for y in range(self.game.dungeon.height)
            for x in range(self.game.dungeon.width)
            if self.game.dungeon.is_walkable(x, y) or
               self.game.dungeon.get_tile(x, y) == c.TILE_STAIRS
        )

        if total_floor_tiles > 0:
            return (explored_count / total_floor_tiles) * 100
        return 0.0

    def _get_stealth_status(self) -> str:
        """Get stealth status for Rogue"""
        if not self.game.player or not self.game.dungeon:
            return ""

        enemies_detecting = self._count_enemies_detecting_player()

        if enemies_detecting == 0:
            return "🔇 HIDDEN"
        else:
            return f"⚠ DETECTED ({enemies_detecting})"

    def _count_enemies_detecting_player(self) -> int:
        """Count how many enemies can see the player"""
        if not self.game.player or not self.game.dungeon:
            return 0

        count = 0
        from fov import calculate_fov

        for enemy in self.game.enemies:
            enemy_fov = calculate_fov(
                self.game.dungeon,
                enemy.x,
                enemy.y,
                enemy.vision_radius
            )

            if (self.game.player.x, self.game.player.y) in enemy_fov:
                count += 1

        return count

    def cleanup(self):
        """Clean up all HUD elements"""
        # Clean up combat log entries
        for entry in self.combat_log_entries:
            if entry.text_entity:
                entry.text_entity.disable()
        self.combat_log_entries.clear()

        # Clean up ability slots
        for slot in self.ability_slots:
            slot.cleanup()
        self.ability_slots.clear()

        # Clean up minimap
        if self.minimap:
            self.minimap.cleanup()
            self.minimap = None

        # All other entities will be cleaned up automatically
        # since they're parented to camera.ui

        print("✓ HelmetHUD3D cleaned up")


class AbilitySlot:
    """Single ability slot with cooldown visualization"""

    # Ability colors (for icon background)
    ABILITY_COLORS = {
        "Fireball": (1.0, 0.5, 0.0),      # Orange
        "Frost Nova": (0.3, 0.7, 1.0),    # Cyan
        "Heal": (0.3, 1.0, 0.5),          # Green
        "Dash": (0.7, 0.3, 1.0),          # Purple
        "Shadow Step": (0.5, 0.5, 0.5),   # Gray
        "Whirlwind": (1.0, 0.3, 0.3),     # Red
    }

    def __init__(
        self,
        ability_index: int,
        parent: Optional[Entity],
        position: Vec2,
        slot_size: float = 0.12
    ):
        self.ability_index = ability_index
        self.position = position
        self.slot_size = slot_size

        # UI elements
        self.background: Optional[Entity] = None
        self.icon_bg: Optional[Entity] = None
        self.cooldown_overlay: Optional[Entity] = None
        self.ability_name_text: Optional[Text] = None
        self.hotkey_text: Optional[Text] = None
        self.cooldown_text: Optional[Text] = None

        # Cached values
        self._last_ability_name = None
        self._last_is_ready = None
        self._last_cooldown_remaining = -1

        self._create_ui(parent)

    def _create_ui(self, parent: Entity):
        """Create slot UI elements with improved visibility"""
        # Background border (outermost)
        self.background = Entity(
            parent=parent,
            model='quad',
            color=color.rgba(0.15, 0.15, 0.2, 0.95),  # More opaque, slightly lighter
            position=(self.position.x, self.position.y, 10),  # Far back (behind everything)
            scale=(self.slot_size, self.slot_size),
            origin=(0, 0),
            eternal=True
        )

        # Icon background (ability color)
        self.icon_bg = Entity(
            parent=parent,
            model='quad',
            color=color.rgb(0.3, 0.3, 0.3),  # Gray until ability assigned
            position=(self.position.x, self.position.y, 9),  # In front of background
            scale=(self.slot_size * 0.88, self.slot_size * 0.88),
            origin=(0, 0),
            eternal=True
        )

        # Cooldown overlay (covers icon when on cooldown)
        self.cooldown_overlay = Entity(
            parent=parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.75),  # Darker for better contrast
            position=(self.position.x, self.position.y, 8),  # In front of icon
            scale=(self.slot_size * 0.88, self.slot_size * 0.88),
            origin=(0, 0),
            visible=False,
            eternal=True
        )

        # Ability name (above slot) - compact size
        self.ability_name_text = Text(
            text="",
            parent=parent,
            position=(self.position.x, self.position.y + self.slot_size * 0.6, -10),  # In front of all
            scale=0.55,  # Smaller for compact layout
            color=color.white,
            origin=(0, 0),
            eternal=True
        )

        # Hotkey label (bottom of slot) - compact but readable
        hotkey_number = self.ability_index + 1
        self.hotkey_text = Text(
            text=f"[{hotkey_number}]",
            parent=parent,
            position=(self.position.x, self.position.y - self.slot_size * 0.6, -10),  # In front of all
            scale=0.7,  # Smaller for compact layout
            color=color.rgb(1.0, 0.9, 0.2),  # Brighter gold
            origin=(0, 0),
            eternal=True
        )

        # Cooldown timer text (center of slot when on cooldown)
        self.cooldown_text = Text(
            text="",
            parent=parent,
            position=(self.position.x, self.position.y, -10),  # In front of all
            scale=0.9,  # Smaller for compact slots
            color=color.white,
            origin=(0, 0),
            visible=False,
            eternal=True
        )

    def update_ability(self, ability):
        """Update slot with ability data and visual feedback"""
        if not ability:
            if self._last_ability_name is not None:
                self.ability_name_text.text = ""
                self.icon_bg.color = color.rgb(0.3, 0.3, 0.3)
                self.cooldown_overlay.visible = False
                self.cooldown_text.visible = False
                self._last_ability_name = None
                self._last_is_ready = None
                self._last_cooldown_remaining = -1
            return

        # Update ability name and color
        if ability.name != self._last_ability_name:
            self.ability_name_text.text = ability.name
            ability_color = self.ABILITY_COLORS.get(ability.name, (0.5, 0.5, 0.5))
            self.icon_bg.color = color.rgb(*ability_color)
            self._last_ability_name = ability.name

        # Update cooldown state with enhanced visuals
        is_ready = ability.is_ready()
        cooldown_remaining = int(ability.current_cooldown) + 1 if not is_ready else 0

        if is_ready != self._last_is_ready or cooldown_remaining != self._last_cooldown_remaining:
            if is_ready:
                # Ability ready - brighten colors
                self.cooldown_overlay.visible = False
                self.cooldown_text.visible = False

                # Make ability name and hotkey brighter when ready
                self.ability_name_text.color = color.white
                self.hotkey_text.color = color.rgb(1.0, 0.9, 0.2)  # Bright gold

                # Brighten icon background
                ability_color = self.ABILITY_COLORS.get(ability.name, (0.5, 0.5, 0.5))
                self.icon_bg.color = color.rgb(*ability_color)
            else:
                # Ability on cooldown - dim colors
                self.cooldown_overlay.visible = True
                self.cooldown_text.visible = True
                self.cooldown_text.text = f"{cooldown_remaining}"

                # Dim ability name and hotkey when on cooldown
                self.ability_name_text.color = color.rgba(0.6, 0.6, 0.6, 1)  # Gray
                self.hotkey_text.color = color.rgba(0.6, 0.6, 0.4, 1)  # Dim gold

                # Scale overlay based on cooldown progress (fills from bottom)
                cooldown_percent = ability.current_cooldown / ability.max_cooldown
                self.cooldown_overlay.scale_y = self.slot_size * 0.88 * cooldown_percent

                # Dim icon background
                ability_color = self.ABILITY_COLORS.get(ability.name, (0.5, 0.5, 0.5))
                self.icon_bg.color = color.rgb(
                    ability_color[0] * 0.4,
                    ability_color[1] * 0.4,
                    ability_color[2] * 0.4
                )

            self._last_is_ready = is_ready
            self._last_cooldown_remaining = cooldown_remaining

    def cleanup(self):
        """Clean up slot UI elements"""
        elements = [
            self.background,
            self.icon_bg,
            self.cooldown_overlay,
            self.ability_name_text,
            self.hotkey_text,
            self.cooldown_text
        ]

        for element in elements:
            if element:
                element.disable()
