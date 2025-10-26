"""
Stats Panels - Top-left and top-right HUD panels

Top-left: Player stats (HP/XP bars, class/level, gold)
Top-right: Equipment display
"""

from typing import Optional
from ursina import Entity, Text, color
from core import constants as c
from shaders.glossy_bar_shader import create_hp_bar_shader, create_xp_bar_shader


class StatsPanel:
    """Top-left panel with player stats (HP/XP bars, class/level, gold)"""

    def __init__(self, parent: Optional[Entity], pos_x: float = -0.85, pos_y: float = 0.45):
        """
        Initialize stats panel

        Args:
            parent: Parent entity (camera.ui)
            pos_x: Panel X position
            pos_y: Panel Y position
        """
        self.parent = parent
        self.pos_x = pos_x
        self.pos_y = pos_y

        panel_width = 0.50
        panel_height = 0.30

        # UI elements
        self.panel: Optional[Entity] = None
        self.class_level_text: Optional[Text] = None

        # HP Bar elements
        self.hp_bar_shadow: Optional[Entity] = None
        self.hp_bar_outer_frame: Optional[Entity] = None
        self.hp_bar_bg: Optional[Entity] = None
        self.hp_bar_fill: Optional[Entity] = None
        self.hp_bar_inner_glow: Optional[Entity] = None
        self.hp_text: Optional[Text] = None

        # XP Bar elements
        self.xp_bar_shadow: Optional[Entity] = None
        self.xp_bar_outer_frame: Optional[Entity] = None
        self.xp_bar_bg: Optional[Entity] = None
        self.xp_bar_fill: Optional[Entity] = None
        self.xp_bar_inner_glow: Optional[Entity] = None
        self.xp_text: Optional[Text] = None

        self.gold_text: Optional[Text] = None

        # Create UI
        self._create_panel(panel_width, panel_height)
        self._create_class_level()
        self._create_hp_bar()
        self._create_xp_bar()
        self._create_gold_counter()

    def _create_panel(self, panel_width: float, panel_height: float):
        """Create background panel"""
        # Background panel with rounded appearance (darker blue, more opaque)
        self.panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),
            position=(self.pos_x, self.pos_y, 10),
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),
            position=(self.pos_x + 0.002, self.pos_y - 0.002, 9),
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

    def _create_class_level(self):
        """Create class and level text"""
        self.class_level_text = Text(
            text="Warrior - Level 1",
            parent=self.parent,
            position=(self.pos_x + 0.01, self.pos_y - 0.03, -10),
            scale=1.2,
            color=color.rgb(0.3, 1.0, 1.0),  # Cyan
            origin=(-0.5, 0.5),
            eternal=True
        )

    def _create_hp_bar(self):
        """Create HP bar with glossy shader"""
        hp_bar_y = self.pos_y - 0.09
        bar_width = 0.38
        bar_height = 0.04
        shadow_offset = 0.008

        # Drop shadow (furthest back)
        self.hp_bar_shadow = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.0, 0.0, 0.0, 0.8),
            position=(self.pos_x + 0.01 + shadow_offset, hp_bar_y - shadow_offset, 6),
            scale=(bar_width + 0.01, bar_height + 0.005),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Outer frame (metallic tech border)
        self.hp_bar_outer_frame = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.3, 0.5, 0.7, 0.9),
            position=(self.pos_x + 0.01, hp_bar_y, 5.5),
            scale=(bar_width + 0.01, bar_height + 0.008),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.hp_bar_bg = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.1, 0.1, 0.1, 0.9),
            position=(self.pos_x + 0.01, hp_bar_y, 5),
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Bar fill with glossy shader
        self.hp_bar_fill = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgb(0.3, 1.0, 0.3),  # Bright green
            position=(self.pos_x + 0.01, hp_bar_y, 4),
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )
        # Apply glossy shader to bar fill
        hp_shader = create_hp_bar_shader()
        if hp_shader:
            self.hp_bar_fill.shader = hp_shader

        # Inner glow (bright border inside bar)
        self.hp_bar_inner_glow = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.3, 1.0, 0.3, 0.4),
            position=(self.pos_x + 0.01, hp_bar_y, 3),
            scale=(bar_width - 0.005, bar_height - 0.005),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.hp_text = Text(
            text="100/100 HP",
            parent=self.parent,
            position=(self.pos_x + 0.01, hp_bar_y - 0.055, -10),
            scale=1.0,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

    def _create_xp_bar(self):
        """Create XP bar with glossy shader"""
        xp_bar_y = self.pos_y - 0.17
        bar_width = 0.38
        bar_height = 0.04
        shadow_offset = 0.008

        # Drop shadow (furthest back)
        self.xp_bar_shadow = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.0, 0.0, 0.0, 0.8),
            position=(self.pos_x + 0.01 + shadow_offset, xp_bar_y - shadow_offset, 6),
            scale=(bar_width + 0.01, bar_height + 0.005),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Outer frame (metallic tech border)
        self.xp_bar_outer_frame = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.3, 0.5, 0.7, 0.9),
            position=(self.pos_x + 0.01, xp_bar_y, 5.5),
            scale=(bar_width + 0.01, bar_height + 0.008),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.xp_bar_bg = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.1, 0.1, 0.1, 0.9),
            position=(self.pos_x + 0.01, xp_bar_y, 5),
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Bar fill with glossy shader
        self.xp_bar_fill = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgb(1.0, 0.85, 0.0),  # Gold
            position=(self.pos_x + 0.01, xp_bar_y, 4),
            scale=(bar_width, bar_height),
            origin=(-0.5, 0.5),
            eternal=True
        )
        # Apply glossy shader to bar fill
        xp_shader = create_xp_bar_shader()
        if xp_shader:
            self.xp_bar_fill.shader = xp_shader

        # Inner glow (bright border inside bar)
        self.xp_bar_inner_glow = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(1.0, 0.85, 0.0, 0.4),
            position=(self.pos_x + 0.01, xp_bar_y, 3),
            scale=(bar_width - 0.005, bar_height - 0.005),
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.xp_text = Text(
            text="0/100 XP",
            parent=self.parent,
            position=(self.pos_x + 0.01, xp_bar_y - 0.055, -10),
            scale=1.0,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

    def _create_gold_counter(self):
        """Create gold counter text"""
        gold_y = self.pos_y - 0.27
        self.gold_text = Text(
            text="Gold: 0",
            parent=self.parent,
            position=(self.pos_x + 0.01, gold_y, -10),
            scale=1.2,
            color=color.rgb(1.0, 0.84, 0.0),  # Gold color
            origin=(-0.5, 0.5),
            eternal=True
        )


class EquipmentPanel:
    """Top-right panel with equipment display"""

    def __init__(self, parent: Optional[Entity], pos_x: float = 0.35, pos_y: float = 0.45):
        """
        Initialize equipment panel

        Args:
            parent: Parent entity (camera.ui)
            pos_x: Panel X position
            pos_y: Panel Y position
        """
        self.parent = parent
        self.pos_x = pos_x
        self.pos_y = pos_y

        panel_width = 0.50
        panel_height = 0.28

        # UI elements
        self.panel: Optional[Entity] = None
        self.weapon_text: Optional[Text] = None
        self.armor_text: Optional[Text] = None
        self.accessory_text: Optional[Text] = None
        self.boots_text: Optional[Text] = None

        # Create UI
        self._create_panel(panel_width, panel_height)
        self._create_equipment_slots()

    def _create_panel(self, panel_width: float, panel_height: float):
        """Create background panel"""
        # Background panel
        self.panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, 0.90),
            position=(self.pos_x, self.pos_y, 10),
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Inner border for "visor" effect
        Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.2, 0.4, 0.6, 0.4),
            position=(self.pos_x + 0.002, self.pos_y - 0.002, 9),
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

    def _create_equipment_slots(self):
        """Create equipment slot text elements (2x2 grid)"""
        line_height = 0.055
        col_offset = 0.22
        start_y = self.pos_y - 0.04

        # Column 1: Weapon & Armor
        self.weapon_text = Text(
            text="ATK None",
            parent=self.parent,
            position=(self.pos_x + 0.01, start_y, -10),
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.armor_text = Text(
            text="DEF None",
            parent=self.parent,
            position=(self.pos_x + 0.01, start_y - line_height, -10),
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Column 2: Accessory & Boots
        self.accessory_text = Text(
            text="ACC None",
            parent=self.parent,
            position=(self.pos_x + 0.01 + col_offset, start_y, -10),
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )

        self.boots_text = Text(
            text="BOT None",
            parent=self.parent,
            position=(self.pos_x + 0.01 + col_offset, start_y - line_height, -10),
            scale=0.9,
            color=color.white,
            origin=(-0.5, 0.5),
            eternal=True
        )
