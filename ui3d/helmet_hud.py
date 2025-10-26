"""
Helmet HUD 3D Widget

A unified, immersive HUD design that resembles looking through a futuristic helmet visor.
All UI elements are consolidated into corner panels and bottom displays for minimal viewport obstruction.
"""

import time
from typing import Optional, List
from ursina import Entity, Text, color, Vec2
from game_logic.game import Game
from core import constants as c
from ui3d.minimap_3d import MiniMap3D
from ui3d.components.bar_particles import BarBubbleSystem
from ui3d.components.ability_slot import AbilitySlot
from ui3d.components.combat_log import CombatLogEntry
from ui3d.panels.stats_panels import StatsPanel, EquipmentPanel



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

        # ===== PANELS (using component modules) =====
        self.stats_panel: Optional[StatsPanel] = None
        self.equipment_panel: Optional[EquipmentPanel] = None

        # ===== BOTTOM-CENTER PANEL (Combat Log + Nearby Items) =====
        self.bottom_center_panel: Optional[Entity] = None
        self.log_title: Optional[Text] = None

        # ===== BOTTOM-LEFT (Abilities) =====
        self.bottom_left_panel: Optional[Entity] = None
        self.ability_slots: List[AbilitySlot] = []

        # ===== BOTTOM-RIGHT (Quick Stats) =====
        self.attack_text: Optional[Text] = None
        self.defense_text: Optional[Text] = None
        self.depth_text: Optional[Text] = None
        self.exploration_text: Optional[Text] = None
        self.stealth_text: Optional[Text] = None

        # ===== MINIMAP =====
        self.minimap: Optional[MiniMap3D] = None

        # ===== BUBBLE PARTICLE SYSTEMS =====
        self.hp_bubble_system: Optional[BarBubbleSystem] = None
        self.xp_bubble_system: Optional[BarBubbleSystem] = None

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
        self._create_top_panels()
        self._create_bottom_center_panel()
        self._create_bottom_left_abilities()
        self._create_bottom_right_stats()
        self._create_minimap()
        self._create_bubble_systems()    # ========== TOP PANELS ==========
    def _create_top_panels(self):
        """Create top-left and top-right panels"""
        self.stats_panel = StatsPanel(parent=self.parent)
        self.equipment_panel = EquipmentPanel(parent=self.parent)



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

    # ========== BUBBLE PARTICLE SYSTEMS ==========
    def _create_bubble_systems(self):
        """Create bubble particle systems for HP and XP bars"""
        # HP bar bubbles (start with green)
        self.hp_bubble_system = BarBubbleSystem(
            parent=self.parent,
            bar_color=(0.3, 1.0, 0.3)  # Green
        )

        # XP bar bubbles (gold)
        self.xp_bubble_system = BarBubbleSystem(
            parent=self.parent,
            bar_color=(1.0, 0.85, 0.0)  # Gold
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

        # Update shader time uniforms for wave animation
        current_time = time.time()
        if self.stats_panel.hp_bar_fill and hasattr(self.stats_panel.hp_bar_fill, 'shader') and self.stats_panel.hp_bar_fill.shader:
            self.stats_panel.hp_bar_fill.set_shader_input('time', current_time)
        if self.stats_panel.xp_bar_fill and hasattr(self.stats_panel.xp_bar_fill, 'shader') and self.stats_panel.xp_bar_fill.shader:
            self.stats_panel.xp_bar_fill.set_shader_input('time', current_time)

        self._update_player_stats()
        self._update_equipment()
        self._update_abilities(dt)
        self._update_quick_stats()
        self._update_combat_log(dt)
        self._update_nearby_items()

        # Update minimap
        if self.minimap:
            self.minimap.update(dt, camera_yaw)

        # Update bubble particle systems
        if self.hp_bubble_system:
            self.hp_bubble_system.update(dt)
        if self.xp_bubble_system:
            self.xp_bubble_system.update(dt)

    def _update_player_stats(self):
        """Update top-left player stats panel"""
        player = self.game.player

        # Class and level
        if player.level != self._last_level:
            class_name = player.get_class_name()
            self.stats_panel.class_level_text.text = f"{class_name} - Level {player.level}"
            self._last_level = player.level

        # HP bar
        if player.hp != self._last_hp or player.max_hp != self._last_max_hp:
            hp_percent = player.hp / player.max_hp if player.max_hp > 0 else 0
            self.stats_panel.hp_bar_fill.scale_x = 0.38 * hp_percent  # Updated to match new bar width
            # Also scale inner glow to match fill
            self.stats_panel.hp_bar_inner_glow.scale_x = (0.38 - 0.005) * hp_percent

            # Color code based on HP percentage (update both fill and glow)
            if hp_percent > 0.6:
                bar_color = color.rgb(0.3, 1.0, 0.3)  # Green
                glow_color = color.rgba(0.3, 1.0, 0.3, 0.4)  # Green glow
                bubble_color = (0.3, 1.0, 0.3)
            elif hp_percent > 0.3:
                bar_color = color.rgb(1.0, 0.9, 0.0)  # Yellow
                glow_color = color.rgba(1.0, 0.9, 0.0, 0.4)  # Yellow glow
                bubble_color = (1.0, 0.9, 0.0)
            else:
                bar_color = color.rgb(1.0, 0.3, 0.3)  # Red
                glow_color = color.rgba(1.0, 0.3, 0.3, 0.4)  # Red glow
                bubble_color = (1.0, 0.3, 0.3)

            self.stats_panel.hp_bar_fill.color = bar_color
            self.stats_panel.hp_bar_inner_glow.color = glow_color

            # Update bubble system color and position
            if self.hp_bubble_system:
                self.hp_bubble_system.set_color(bubble_color)
                # Calculate bar end position (bar starts at -0.84, width is 0.38 * hp_percent)
                bar_start_x = -0.84
                bar_end_x = bar_start_x + (0.38 * hp_percent)
                bar_y = 0.36  # hp_bar_y from creation
                self.hp_bubble_system.set_bar_end_position(bar_end_x, bar_y)

            self.stats_panel.hp_text.text = f"{player.hp}/{player.max_hp} HP"
            self._last_hp = player.hp
            self._last_max_hp = player.max_hp

        # XP bar
        if player.xp != self._last_xp or player.xp_to_next_level != self._last_xp_to_next:
            xp_percent = player.xp / player.xp_to_next_level if player.xp_to_next_level > 0 else 0
            self.stats_panel.xp_bar_fill.scale_x = 0.38 * xp_percent  # Updated to match new bar width
            # Also scale inner glow to match fill
            self.stats_panel.xp_bar_inner_glow.scale_x = (0.38 - 0.005) * xp_percent

            # Update bubble system position
            if self.xp_bubble_system:
                # Calculate bar end position (bar starts at -0.84, width is 0.38 * xp_percent)
                bar_start_x = -0.84
                bar_end_x = bar_start_x + (0.38 * xp_percent)
                bar_y = 0.28  # xp_bar_y from creation
                self.xp_bubble_system.set_bar_end_position(bar_end_x, bar_y)

            self.stats_panel.xp_text.text = f"{player.xp}/{player.xp_to_next_level} XP"
            self._last_xp = player.xp
            self._last_xp_to_next = player.xp_to_next_level

        # Gold counter
        if player.gold != self._last_gold:
            self.stats_panel.gold_text.text = f"Gold: {player.gold}"
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
                self.equipment_panel.weapon_text.text = f"ATK {name}"
                self.equipment_panel.weapon_text.color = color.rgb(*item_color)
            else:
                self.equipment_panel.weapon_text.text = "ATK None"
                self.equipment_panel.weapon_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_weapon = weapon

        # Armor
        armor = player.equipment[c.SLOT_ARMOR]
        if armor != self._last_armor:
            if armor:
                name = armor.get_name()
                item_color = self.RARITY_COLORS.get(armor.rarity, (1, 1, 1))
                self.equipment_panel.armor_text.text = f"DEF {name}"
                self.equipment_panel.armor_text.color = color.rgb(*item_color)
            else:
                self.equipment_panel.armor_text.text = "DEF None"
                self.equipment_panel.armor_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_armor = armor

        # Accessory
        accessory = player.equipment[c.SLOT_ACCESSORY]
        if accessory != self._last_accessory:
            if accessory:
                name = accessory.get_name()
                item_color = self.RARITY_COLORS.get(accessory.rarity, (1, 1, 1))
                self.equipment_panel.accessory_text.text = f"ACC {name}"
                self.equipment_panel.accessory_text.color = color.rgb(*item_color)
            else:
                self.equipment_panel.accessory_text.text = "ACC None"
                self.equipment_panel.accessory_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_accessory = accessory

        # Boots
        boots = player.equipment[c.SLOT_BOOTS]
        if boots != self._last_boots:
            if boots:
                name = boots.get_name()
                item_color = self.RARITY_COLORS.get(boots.rarity, (1, 1, 1))
                self.equipment_panel.boots_text.text = f"BOT {name}"
                self.equipment_panel.boots_text.color = color.rgb(*item_color)
            else:
                self.equipment_panel.boots_text.text = "BOT None"
                self.equipment_panel.boots_text.color = color.rgba(0.5, 0.5, 0.5, 1)
            self._last_boots = boots

    def _update_abilities(self, dt: float):
        """Update bottom-left ability slots"""
        if not self.game.player or not self.game.player.abilities:
            return

        for i, slot in enumerate(self.ability_slots):
            if i < len(self.game.player.abilities):
                ability = self.game.player.abilities[i]
                slot.update_ability(ability)
                slot.update_animation(dt, ability)
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

        # Clean up bubble systems
        if self.hp_bubble_system:
            self.hp_bubble_system.cleanup()
            self.hp_bubble_system = None
        if self.xp_bubble_system:
            self.xp_bubble_system.cleanup()
            self.xp_bubble_system = None

        # All other entities will be cleaned up automatically
        # since they're parented to camera.ui

        print("✓ HelmetHUD3D cleaned up")
