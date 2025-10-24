"""
3D Settings Screen

Settings screen with volume controls for music and sound effects.
Uses Ursina UI elements.
"""

from ursina import Entity, camera, color, Text, Button, Slider, time as ursina_time
import constants as c
from audio import get_audio_manager
from ui.widgets.dungeon_button_3d import DungeonButton


class Settings3D(Entity):
    """
    Settings screen with volume controls.

    Features:
    - Music volume slider
    - SFX volume slider
    - Back button (returns to previous screen)
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # UI elements
        self.ui_elements = []

        # Slider references
        self.music_slider = None
        self.sfx_slider = None
        self.particle_slider = None
        self.music_value_text = None
        self.sfx_value_text = None
        self.particle_value_text = None

        # Track previous screen for navigation
        self.previous_screen = None

        # Initialize
        self._create_ui()

        # Initially hidden
        self.enabled = False

    def _create_ui(self):
        """Create UI overlay elements"""
        # Background overlay (semi-transparent dark) - furthest back
        bg = Entity(
            model='quad',
            color=(0.05, 0.05, 0.15, 0.95),
            scale=(100, 100),
            position=(0, 0, 0.9),  # Positive z = behind everything
            parent=camera.ui,
            collider=None  # Prevent blocking mouse input
        )
        self.ui_elements.append(bg)

        # Title - in front
        title = Text(
            text="SETTINGS",
            position=(0, 0.40, -0.2),  # Negative z = in front
            origin=(0, 0),
            scale=1.75,  # Reduced from 3.5
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(title)

        # Settings panel background - middle layer (taller for 3 sliders)
        panel_bg = Entity(
            model='quad',
            color=color.rgb(0.176, 0.176, 0.196),
            scale=(0.65, 0.65),  # Reduced from (1.2, 1.15)
            position=(0, 0.02, 0.8),  # Adjusted position
            parent=camera.ui,
            collider=None  # Prevent blocking mouse input
        )
        self.ui_elements.append(panel_bg)

        # Music Volume Section
        music_label = Text(
            text="Music Volume",
            position=(0, 0.26, -0.1),  # Centered, closer to top
            origin=(0, 0),  # Center origin
            scale=0.9,  # Reduced from 1.8
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(music_label)

        # Music slider
        self.music_slider = Slider(
            min=0, max=100,
            default=int(self.audio.music_volume * 100),
            step=1,
            height=0.025,  # Reduced from 0.05
            width=0.35,  # Reduced from 0.65
            position=(-0.19, 0.20, -0.1),  # Adjusted position
            parent=camera.ui,
            text=False,  # Disable built-in value display
            on_value_changed=self._on_music_volume_changed
        )
        # Dungeon-styled slider colors
        self.music_slider.knob.color = color.rgb(0.588, 0.392, 1.0)  # Purple knob
        self.music_slider.knob.scale *= 1.3  # Larger knob
        self.music_slider.bg.color = color.rgb(0.157, 0.149, 0.137)  # Darker stone background
        self.ui_elements.append(self.music_slider)

        # Music value display
        self.music_value_text = Text(
            text=f"{int(self.audio.music_volume * 100)}%",
            position=(0.20, 0.20, -0.1),  # To the right of slider
            origin=(-1, 0),  # Left origin for consistent spacing
            scale=1.0,  # Reduced from 2.0
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(self.music_value_text)

        # SFX Volume Section
        sfx_label = Text(
            text="Sound Effects Volume",
            position=(0, 0.10, -0.1),  # Centered
            origin=(0, 0),  # Center origin
            scale=0.9,  # Reduced from 1.8
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(sfx_label)

        # SFX slider
        self.sfx_slider = Slider(
            min=0, max=100,
            default=int(self.audio.sfx_volume * 100),
            step=1,
            height=0.025,  # Reduced from 0.05
            width=0.35,  # Reduced from 0.65
            position=(-0.19, 0.04, -0.1),  # Adjusted position
            parent=camera.ui,
            text=False,  # Disable built-in value display
            on_value_changed=self._on_sfx_volume_changed
        )
        # Dungeon-styled slider colors
        self.sfx_slider.knob.color = color.rgb(0.392, 0.784, 1.0)  # Blue knob
        self.sfx_slider.knob.scale *= 1.3  # Larger knob
        self.sfx_slider.bg.color = color.rgb(0.157, 0.149, 0.137)  # Darker stone background
        self.ui_elements.append(self.sfx_slider)

        # SFX value display
        self.sfx_value_text = Text(
            text=f"{int(self.audio.sfx_volume * 100)}%",
            position=(0.20, 0.04, -0.1),  # To the right of slider
            origin=(-1, 0),  # Left origin for consistent spacing
            scale=1.0,  # Reduced from 2.0
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(self.sfx_value_text)

        # Particle Density Section
        particle_label = Text(
            text="Particle Effects",
            position=(0, -0.06, -0.1),  # Centered
            origin=(0, 0),  # Center origin
            scale=0.9,  # Reduced from 1.8
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(particle_label)

        # Particle density slider (0-100, representing 0.0 to 1.0)
        self.particle_slider = Slider(
            min=0, max=100,
            default=int(c.PARTICLE_DENSITY * 100),
            step=5,  # Step by 5% for easier control
            height=0.025,  # Reduced from 0.05
            width=0.35,  # Reduced from 0.65
            position=(-0.19, -0.12, -0.1),  # Adjusted position
            parent=camera.ui,
            text=False,  # Disable built-in value display
            on_value_changed=self._on_particle_density_changed
        )
        # Dungeon-styled slider colors
        self.particle_slider.knob.color = color.rgb(1.0, 0.588, 0.392)  # Orange knob
        self.particle_slider.knob.scale *= 1.3  # Larger knob
        self.particle_slider.bg.color = color.rgb(0.157, 0.149, 0.137)  # Darker stone background
        self.ui_elements.append(self.particle_slider)

        # Particle value display
        self.particle_value_text = Text(
            text=f"{int(c.PARTICLE_DENSITY * 100)}%",
            position=(0.20, -0.12, -0.1),  # To the right of slider
            origin=(-1, 0),  # Left origin for consistent spacing
            scale=1.0,  # Reduced from 2.0
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(self.particle_value_text)

        # Back button (dungeon-styled) - moved down to accommodate new slider
        self.back_button = DungeonButton(
            text="BACK",
            scale=(0.20, 0.06),  # Reduced from (0.35, 0.10)
            position=(0, -0.24, -0.1),  # Adjusted position
            parent=camera.ui,
            on_click=self._on_back
        )
        self.ui_elements.append(self.back_button)

    def _on_music_volume_changed(self):
        """Handle music volume slider change"""
        value = int(self.music_slider.value)
        volume = value / 100.0
        self.audio.set_music_volume(volume)
        self.music_value_text.text = f"{value}%"
        print(f"[Settings] Music volume: {value}%")

    def _on_sfx_volume_changed(self):
        """Handle SFX volume slider change"""
        value = int(self.sfx_slider.value)
        volume = value / 100.0
        self.audio.set_sfx_volume(volume)
        self.sfx_value_text.text = f"{value}%"

        # Play a test sound (if volume > 0)
        if value > 0:
            self.audio.play_ui_select()

        print(f"[Settings] SFX volume: {value}%")

    def _on_particle_density_changed(self):
        """Handle particle density slider change"""
        value = int(self.particle_slider.value)
        density = value / 100.0
        c.PARTICLE_DENSITY = density
        self.particle_value_text.text = f"{value}%"

        # Play a test sound
        self.audio.play_ui_select()

        print(f"[Settings] Particle density: {value}% ({density:.2f})")

    def _on_back(self):
        """Handle back button click"""
        self.audio.play_ui_select()
        print("[Settings] Back clicked")

        # Return to previous screen
        if self.previous_screen:
            self.screen_manager.change_screen(self.previous_screen)
        else:
            # Default: return to main menu
            from ui.screens.screen_manager_3d import ScreenState
            self.screen_manager.change_screen(ScreenState.MAIN_MENU)

    def set_previous_screen(self, screen_state):
        """Set the screen to return to when Back is clicked"""
        self.previous_screen = screen_state

    def update(self):
        """Update (currently no animations)"""
        if not self.enabled:
            return
        # No active animations for settings screen
        pass

    def show(self):
        """Show the settings screen"""
        self.enabled = True

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Update slider values to current settings
        self.music_slider.value = int(self.audio.music_volume * 100)
        self.sfx_slider.value = int(self.audio.sfx_volume * 100)
        self.particle_slider.value = int(c.PARTICLE_DENSITY * 100)
        self.music_value_text.text = f"{int(self.audio.music_volume * 100)}%"
        self.sfx_value_text.text = f"{int(self.audio.sfx_volume * 100)}%"
        self.particle_value_text.text = f"{int(c.PARTICLE_DENSITY * 100)}%"

        print("[Settings] Settings screen shown")
        print(f"[Settings] UI elements enabled: {len(self.ui_elements)}")
        print(f"[Settings] Title position: {self.ui_elements[1].position if len(self.ui_elements) > 1 else 'N/A'}")

    def hide(self):
        """Hide the settings screen"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        print("[Settings] Settings screen hidden")
