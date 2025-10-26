"""
3D Settings Screen

Advanced settings screen with tabbed interface for organizing options.
Categories: Audio, Graphics, Display
Uses Ursina UI elements.
"""

from ursina import Entity, camera, color, Text, Button, Slider, window, time as ursina_time
from core import constants as c
from audio import get_audio_manager
from ui.widgets.dungeon_button_3d import DungeonButton
from core.settings import save_current_settings


class Settings3D(Entity):
    """
    Advanced settings screen with tabbed interface.

    Features:
    - Tab navigation (Audio, Graphics, Display)
    - Audio tab: Music and SFX volume sliders
    - Graphics tab: Particle density slider
    - Display tab: Fullscreen toggle
    - Back button (returns to previous screen)
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # UI elements (common across all tabs)
        self.ui_elements = []

        # Tab-specific UI elements (organized by tab name)
        self.tab_elements = {
            'audio': [],
            'graphics': [],
            'display': []
        }

        # Current active tab
        self.active_tab = 'audio'

        # Widget references
        self.music_slider = None
        self.sfx_slider = None
        self.particle_slider = None
        self.fullscreen_button = None
        self.music_value_text = None
        self.sfx_value_text = None
        self.particle_value_text = None
        self.fullscreen_status_text = None

        # Tab button references
        self.tab_buttons = {}

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
            position=(0, 0.42, -0.2),  # Negative z = in front
            origin=(0, 0),
            scale=1.75,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(title)

        # Settings panel background - middle layer
        panel_bg = Entity(
            model='quad',
            color=color.rgb(0.176, 0.176, 0.196),
            scale=(0.75, 0.72),  # Wider and taller for tabs
            position=(0, 0.0, 0.8),
            parent=camera.ui,
            collider=None  # Prevent blocking mouse input
        )
        self.ui_elements.append(panel_bg)

        # Tab buttons (at the top of the panel)
        tab_names = ['AUDIO', 'GRAPHICS', 'DISPLAY']
        tab_keys = ['audio', 'graphics', 'display']
        tab_x_positions = [-0.23, 0, 0.23]

        for i, (name, key, x_pos) in enumerate(zip(tab_names, tab_keys, tab_x_positions)):
            tab_btn = DungeonButton(
                text=name,
                scale=(0.18, 0.05),
                position=(x_pos, 0.32, -0.1),
                parent=camera.ui,
                on_click=lambda k=key: self._switch_tab(k)
            )
            self.ui_elements.append(tab_btn)
            self.tab_buttons[key] = tab_btn

        # Create tab-specific content
        self._create_audio_tab()
        self._create_graphics_tab()
        self._create_display_tab()

        # Back button (dungeon-styled) - always visible
        self.back_button = DungeonButton(
            text="BACK",
            scale=(0.20, 0.06),
            position=(0, -0.32, -0.1),
            parent=camera.ui,
            on_click=self._on_back
        )
        self.ui_elements.append(self.back_button)

    def _create_audio_tab(self):
        """Create Audio tab content (music & SFX volume)"""
        # Music Volume Section
        music_label = Text(
            text="Music Volume",
            position=(0, 0.20, -0.1),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['audio'].append(music_label)

        # Music slider
        self.music_slider = Slider(
            min=0, max=100,
            default=int(self.audio.music_volume * 100),
            step=1,
            height=0.025,
            width=0.35,
            position=(-0.19, 0.14, -0.1),
            parent=camera.ui,
            text=False,
            on_value_changed=self._on_music_volume_changed
        )
        # Dungeon-styled slider colors
        self.music_slider.knob.color = color.rgb(0.588, 0.392, 1.0)  # Purple knob
        self.music_slider.knob.scale *= 1.3
        self.music_slider.bg.color = color.rgb(0.157, 0.149, 0.137)
        self.tab_elements['audio'].append(self.music_slider)

        # Music value display
        self.music_value_text = Text(
            text=f"{int(self.audio.music_volume * 100)}%",
            position=(0.20, 0.14, -0.1),
            origin=(-1, 0),
            scale=1.0,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['audio'].append(self.music_value_text)

        # SFX Volume Section
        sfx_label = Text(
            text="Sound Effects Volume",
            position=(0, 0.02, -0.1),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['audio'].append(sfx_label)

        # SFX slider
        self.sfx_slider = Slider(
            min=0, max=100,
            default=int(self.audio.sfx_volume * 100),
            step=1,
            height=0.025,
            width=0.35,
            position=(-0.19, -0.04, -0.1),
            parent=camera.ui,
            text=False,
            on_value_changed=self._on_sfx_volume_changed
        )
        # Dungeon-styled slider colors
        self.sfx_slider.knob.color = color.rgb(0.392, 0.784, 1.0)  # Blue knob
        self.sfx_slider.knob.scale *= 1.3
        self.sfx_slider.bg.color = color.rgb(0.157, 0.149, 0.137)
        self.tab_elements['audio'].append(self.sfx_slider)

        # SFX value display
        self.sfx_value_text = Text(
            text=f"{int(self.audio.sfx_volume * 100)}%",
            position=(0.20, -0.04, -0.1),
            origin=(-1, 0),
            scale=1.0,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['audio'].append(self.sfx_value_text)

    def _create_graphics_tab(self):
        """Create Graphics tab content (particle density)"""
        # Particle Density Section
        particle_label = Text(
            text="Particle Effects Density",
            position=(0, 0.20, -0.1),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['graphics'].append(particle_label)

        # Info text
        particle_info = Text(
            text="Lower values improve performance",
            position=(0, 0.15, -0.1),
            origin=(0, 0),
            scale=0.6,
            color=color.rgb(0.7, 0.7, 0.75),
            parent=camera.ui
        )
        self.tab_elements['graphics'].append(particle_info)

        # Particle density slider (0-100, representing 0.0 to 1.0)
        self.particle_slider = Slider(
            min=0, max=100,
            default=int(c.PARTICLE_DENSITY * 100),
            step=5,  # Step by 5% for easier control
            height=0.025,
            width=0.35,
            position=(-0.19, 0.08, -0.1),
            parent=camera.ui,
            text=False,
            on_value_changed=self._on_particle_density_changed
        )
        # Dungeon-styled slider colors
        self.particle_slider.knob.color = color.rgb(1.0, 0.588, 0.392)  # Orange knob
        self.particle_slider.knob.scale *= 1.3
        self.particle_slider.bg.color = color.rgb(0.157, 0.149, 0.137)
        self.tab_elements['graphics'].append(self.particle_slider)

        # Particle value display
        self.particle_value_text = Text(
            text=f"{int(c.PARTICLE_DENSITY * 100)}%",
            position=(0.20, 0.08, -0.1),
            origin=(-1, 0),
            scale=1.0,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['graphics'].append(self.particle_value_text)

    def _create_display_tab(self):
        """Create Display tab content (fullscreen toggle)"""
        # Fullscreen Section
        fullscreen_label = Text(
            text="Display Mode",
            position=(0, 0.20, -0.1),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['display'].append(fullscreen_label)

        # Info text
        fullscreen_info = Text(
            text="Fullscreen: Auto-detect native resolution",
            position=(0, 0.15, -0.1),
            origin=(0, 0),
            scale=0.6,
            color=color.rgb(0.7, 0.7, 0.75),
            parent=camera.ui
        )
        self.tab_elements['display'].append(fullscreen_info)

        # Windowed mode info
        windowed_info = Text(
            text="Windowed: Fixed 1920x1080",
            position=(0, 0.10, -0.1),
            origin=(0, 0),
            scale=0.6,
            color=color.rgb(0.7, 0.7, 0.75),
            parent=camera.ui
        )
        self.tab_elements['display'].append(windowed_info)

        # Fullscreen toggle button
        self.fullscreen_button = DungeonButton(
            text="TOGGLE FULLSCREEN",
            scale=(0.30, 0.06),
            position=(0, 0.0, -0.1),
            parent=camera.ui,
            on_click=self._on_fullscreen_toggle
        )
        self.tab_elements['display'].append(self.fullscreen_button)

        # Status display
        status = "FULLSCREEN" if c.FULLSCREEN else "WINDOWED"
        self.fullscreen_status_text = Text(
            text=f"Current: {status}",
            position=(0, -0.08, -0.1),
            origin=(0, 0),
            scale=0.8,
            color=color.rgb(0.588, 0.392, 1.0) if c.FULLSCREEN else color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.tab_elements['display'].append(self.fullscreen_status_text)

        # Restart note
        restart_note = Text(
            text="Changes take effect on next game restart",
            position=(0, -0.16, -0.1),
            origin=(0, 0),
            scale=0.55,
            color=color.rgb(1.0, 0.8, 0.4),
            parent=camera.ui
        )
        self.tab_elements['display'].append(restart_note)

    def _switch_tab(self, tab_name):
        """Switch to a different tab"""
        if tab_name == self.active_tab:
            return  # Already on this tab

        self.audio.play_ui_select()

        # Hide current tab elements
        for element in self.tab_elements[self.active_tab]:
            element.enabled = False

        # Update active tab
        self.active_tab = tab_name

        # Show new tab elements
        for element in self.tab_elements[tab_name]:
            element.enabled = True

        # Update tab button visuals (highlight active tab)
        self._update_tab_button_visuals()

        print(f"[Settings] Switched to {tab_name} tab")

    def _update_tab_button_visuals(self):
        """Update tab button colors to show active tab"""
        active_color = color.rgb(0.588, 0.392, 1.0)  # Purple for active
        inactive_color = color.rgb(0.196, 0.188, 0.176)  # Dark stone for inactive

        for tab_key, button in self.tab_buttons.items():
            if tab_key == self.active_tab:
                button.color = active_color
            else:
                button.color = inactive_color

    def _on_music_volume_changed(self):
        """Handle music volume slider change"""
        value = int(self.music_slider.value)
        volume = value / 100.0
        self.audio.set_music_volume(volume)
        self.music_value_text.text = f"{value}%"
        print(f"[Settings] Music volume: {value}%")

        # Save settings to file
        save_current_settings()

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

        # Save settings to file
        save_current_settings()

    def _on_particle_density_changed(self):
        """Handle particle density slider change"""
        value = int(self.particle_slider.value)
        density = value / 100.0
        c.PARTICLE_DENSITY = density
        self.particle_value_text.text = f"{value}%"

        # Play a test sound
        self.audio.play_ui_select()

        print(f"[Settings] Particle density: {value}% ({density:.2f})")

        # Save settings to file
        save_current_settings()

    def _on_fullscreen_toggle(self):
        """Handle fullscreen toggle button click"""
        self.audio.play_ui_select()

        # Toggle fullscreen setting
        c.FULLSCREEN = not c.FULLSCREEN

        # Update status text
        status = "FULLSCREEN" if c.FULLSCREEN else "WINDOWED"
        self.fullscreen_status_text.text = f"Current: {status}"
        self.fullscreen_status_text.color = color.rgb(0.588, 0.392, 1.0) if c.FULLSCREEN else color.rgb(0.863, 0.863, 0.902)

        print(f"[Settings] Fullscreen toggled: {c.FULLSCREEN}")
        print("[Settings] Restart game for changes to take effect")

        # Save settings to file
        save_current_settings()

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

        # Show all common UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Show only active tab's elements
        for tab_name, elements in self.tab_elements.items():
            for element in elements:
                element.enabled = (tab_name == self.active_tab)

        # Update tab button visuals
        self._update_tab_button_visuals()

        # Update slider values to current settings
        self.music_slider.value = int(self.audio.music_volume * 100)
        self.sfx_slider.value = int(self.audio.sfx_volume * 100)
        self.particle_slider.value = int(c.PARTICLE_DENSITY * 100)
        self.music_value_text.text = f"{int(self.audio.music_volume * 100)}%"
        self.sfx_value_text.text = f"{int(self.audio.sfx_volume * 100)}%"
        self.particle_value_text.text = f"{int(c.PARTICLE_DENSITY * 100)}%"

        # Update fullscreen status
        status = "FULLSCREEN" if c.FULLSCREEN else "WINDOWED"
        self.fullscreen_status_text.text = f"Current: {status}"
        self.fullscreen_status_text.color = color.rgb(0.588, 0.392, 1.0) if c.FULLSCREEN else color.rgb(0.863, 0.863, 0.902)

        print("[Settings] Settings screen shown")
        print(f"[Settings] Active tab: {self.active_tab}")

    def hide(self):
        """Hide the settings screen"""
        self.enabled = False

        # Hide all UI elements (common + all tabs)
        for element in self.ui_elements:
            element.enabled = False

        for tab_name, elements in self.tab_elements.items():
            for element in elements:
                element.enabled = False

        print("[Settings] Settings screen hidden")
