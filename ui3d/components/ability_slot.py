"""
Ability Slot Widget

Single ability slot with animated icon, cooldown visualization, and hotkey display.
"""

import os
from typing import Optional
from ursina import Entity, Text, color, Vec2


# ===== ABILITY ICON TEXTURE LOADING =====
# Load or generate ability icon textures (similar to tiles.py pattern)
def _load_ability_icon_textures():
    """Load ability icon textures from cache or generate if missing."""
    import graphics3d.ability_icon_cache as icon_cache

    regenerate_flag = os.environ.get('REGENERATE_ABILITY_ICONS', '0') == '1'

    if icon_cache.cache_exists() and not regenerate_flag:
        # Load from cache (fast)
        print("Loading ability icons from cache...")
        return icon_cache.load_icon_cache()
    else:
        # Generate textures (first launch or forced regeneration)
        print("Generating ability icon textures...")
        from ability_icons import generate_all_ability_frames
        from ursina import Texture

        # Generate frames as PIL Images
        ability_frames_images = generate_all_ability_frames()

        # Convert to Ursina Textures
        ability_textures = {}
        for ability_name, frames in ability_frames_images.items():
            textures = [Texture(frame) for frame in frames]
            ability_textures[ability_name] = textures

        # Save to cache for next time
        icon_cache.save_icon_cache(ability_frames_images)

        print(f"✓ Generated {len(ability_textures)} ability icon animations")
        return ability_textures


# Module-level texture dictionary (loaded once at import time)
ABILITY_ICON_TEXTURES = _load_ability_icon_textures()


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

        # Animation state
        self.current_frame = 0
        self.frame_time = 0.0
        self.frame_duration = 0.1  # 10 FPS animation
        self.total_frames = 8

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

        # Icon background (textured quad for animated ability icon)
        self.icon_bg = Entity(
            parent=parent,
            model='quad',
            texture=None,  # Will be set when ability is assigned
            color=color.white,  # Use white to show texture colors properly
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
                self.icon_bg.texture = None
                self.icon_bg.color = color.white
                self.cooldown_overlay.visible = False
                self.cooldown_text.visible = False
                self._last_ability_name = None
                self._last_is_ready = None
                self._last_cooldown_remaining = -1
            return

        # Update ability name and set texture
        if ability.name != self._last_ability_name:
            self.ability_name_text.text = ability.name

            # Set animated texture from cache
            if ability.name in ABILITY_ICON_TEXTURES:
                textures = ABILITY_ICON_TEXTURES[ability.name]
                if textures:
                    self.icon_bg.texture = textures[self.current_frame]
            else:
                # Fallback to colored quad if texture not found
                ability_color = self.ABILITY_COLORS.get(ability.name, (0.5, 0.5, 0.5))
                self.icon_bg.color = color.rgb(*ability_color)

            self._last_ability_name = ability.name

        # Update cooldown state with enhanced visuals
        is_ready = ability.is_ready()
        cooldown_remaining = int(ability.current_cooldown) + 1 if not is_ready else 0

        if is_ready != self._last_is_ready or cooldown_remaining != self._last_cooldown_remaining:
            if is_ready:
                # Ability ready - full brightness
                self.cooldown_overlay.visible = False
                self.cooldown_text.visible = False

                # Make ability name and hotkey brighter when ready
                self.ability_name_text.color = color.white
                self.hotkey_text.color = color.rgb(1.0, 0.9, 0.2)  # Bright gold

                # Full brightness for textured icon
                self.icon_bg.color = color.white
            else:
                # Ability on cooldown - dim with gray tint
                self.cooldown_overlay.visible = True
                self.cooldown_text.visible = True
                self.cooldown_text.text = f"{cooldown_remaining}"

                # Dim ability name and hotkey when on cooldown
                self.ability_name_text.color = color.rgba(0.6, 0.6, 0.6, 1)  # Gray
                self.hotkey_text.color = color.rgba(0.6, 0.6, 0.4, 1)  # Dim gold

                # Scale overlay based on cooldown progress (fills from bottom)
                cooldown_percent = ability.current_cooldown / ability.max_cooldown
                self.cooldown_overlay.scale_y = self.slot_size * 0.88 * cooldown_percent

                # Dim textured icon by tinting gray
                self.icon_bg.color = color.rgb(0.4, 0.4, 0.4)

            self._last_is_ready = is_ready
            self._last_cooldown_remaining = cooldown_remaining

    def update_animation(self, dt: float, ability):
        """Update icon animation frame.

        Args:
            dt: Delta time since last frame
            ability: Current ability (to get textures)
        """
        if not ability or ability.name not in ABILITY_ICON_TEXTURES:
            return

        # Update frame timer
        self.frame_time += dt

        if self.frame_time >= self.frame_duration:
            # Advance to next frame
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.frame_time = 0.0

            # Update texture
            textures = ABILITY_ICON_TEXTURES[ability.name]
            if textures and len(textures) > self.current_frame:
                self.icon_bg.texture = textures[self.current_frame]

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
