"""
Dungeon-Styled Button Widget for Ursina 3D

Custom button with stone/dungeon aesthetic - inherits from Button.
"""

from ursina import Button, Entity, color, mouse, time as ursina_time, destroy


class DungeonButton(Button):
    """
    Custom dungeon-styled button widget.

    Inherits from Ursina's Button class to get working input handling,
    then adds dungeon-themed styling with border and hover effects.
    """

    def __init__(self, text="", position=(0, 0), scale=(0.3, 0.08),
                 on_click=None, parent=None, **kwargs):
        """
        Create a dungeon-styled button.

        Args:
            text: Button text
            position: (x, y) position in UI space
            scale: (width, height) button size
            on_click: Callback function when clicked
            parent: Parent entity (usually camera.ui)
        """
        # Colors (dungeon theme) - use normalized 0-1 values
        self.color_bg = color.rgb(0.196, 0.188, 0.176)  # Dark stone (50, 48, 45)
        self.color_border = color.rgb(0.255, 0.235, 0.216)  # Brown border (65, 60, 55)
        self.color_border_hover = color.rgb(0.471, 0.392, 0.706)  # Purple glow (120, 100, 180)
        self.color_text = color.rgb(0.863, 0.863, 0.902)  # Light text (220, 220, 230)

        # Store scale for border sizing
        self.base_scale = scale

        # Initialize Button with dungeon styling
        super().__init__(
            text=text,
            position=position,
            scale=scale,
            color=self.color_bg,
            parent=parent,
            on_click=on_click,
            text_scale=1.8,  # Make text larger and readable
            eternal=True,
            **kwargs
        )

        # Override Button's default text color
        self.text_entity.color = self.color_text

        # Create border (behind button) - parented to button so it hides automatically
        border_width = scale[0] + 0.016
        border_height = scale[1] + 0.016

        self.border = Entity(
            parent=self,
            model='quad',
            scale=(border_width, border_height),
            position=(0, 0, 0.01),  # Relative to button, slightly behind
            color=self.color_border,
            eternal=True
        )

        # Animation state
        self.hover_progress = 0.0  # 0 to 1
        self.press_offset = 0.0
        self.was_hovered = False

        print(f"[DungeonButton] Created '{text}' - bg color: {self.color_bg}, text color: {self.color_text}")

    def update(self):
        """Update hover animations (Button handles input automatically)"""
        if not self.enabled:
            return

        # Detect hover state changes
        if self.hovered and not self.was_hovered:
            self._on_hover_enter()
            self.was_hovered = True
        elif not self.hovered and self.was_hovered:
            self._on_hover_exit()
            self.was_hovered = False

        # Animate hover effect
        dt = ursina_time.dt
        target_hover = 1.0 if self.hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * 8 * dt

        # Apply hover effects
        self._update_hover_visuals()

    def _on_hover_enter(self):
        """Called when mouse enters button"""
        # Play hover sound
        try:
            from audio import get_audio_manager
            audio = get_audio_manager()
            audio.play_ui_hover()
        except:
            pass

    def _on_hover_exit(self):
        """Called when mouse leaves button"""
        pass

    def _update_hover_visuals(self):
        """Update visual appearance based on hover state"""
        # Interpolate border color (brown -> purple)
        t = self.hover_progress
        border_r = self.color_border.r + (self.color_border_hover.r - self.color_border.r) * t
        border_g = self.color_border.g + (self.color_border_hover.g - self.color_border.g) * t
        border_b = self.color_border.b + (self.color_border_hover.b - self.color_border.b) * t

        # Apply color to border (values already in 0-1 range)
        self.border.color = color.rgb(border_r, border_g, border_b)

        # Slight scale up on hover
        scale_mult = 1.0 + (0.05 * self.hover_progress)
        border_w = (self.base_scale[0] + 0.016) * scale_mult
        border_h = (self.base_scale[1] + 0.016) * scale_mult
        self.border.scale = (border_w, border_h)

        # Scale button (Button handles its own scale)
        btn_w = self.base_scale[0] * scale_mult
        btn_h = self.base_scale[1] * scale_mult
        self.scale = (btn_w, btn_h)

        # Note: Press offset handled by Button's built-in pressed state

    def destroy_button(self):
        """Clean up button entities"""
        if self.border:
            destroy(self.border)
        # Button class handles its own cleanup
        destroy(self)


def create_dungeon_button(text, position, scale=(0.32, 0.08), on_click=None, parent=None):
    """
    Helper function to create a dungeon-styled button.

    Args:
        text: Button text
        position: (x, y) position in UI space
        scale: (width, height) button size
        on_click: Callback function when clicked
        parent: Parent entity (usually camera.ui)

    Returns:
        DungeonButton instance
    """
    return DungeonButton(
        text=text,
        position=position,
        scale=scale,
        on_click=on_click,
        parent=parent
    )
