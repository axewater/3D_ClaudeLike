"""
3D Pause Menu

Appears when ESC is pressed during gameplay.
"""

from ursina import Entity, camera, color, Text, Button, held_keys
from audio import get_audio_manager
from ui.widgets.dungeon_button_3d import DungeonButton


class PauseMenu3D(Entity):
    """
    Pause menu overlay (does not replace current screen).

    Shows:
    - "PAUSED" title
    - Options: Resume, Restart, Settings, Main Menu, Quit
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # UI elements
        self.ui_elements = []

        # Track ESC key state to prevent rapid toggling
        self.esc_pressed = False

        # Initialize
        self._create_ui()

        # Initially hidden
        self.enabled = False

    def _create_ui(self):
        """Create UI elements"""
        # Title "PAUSED"
        title = Text(
            text="PAUSED",
            position=(0, 0.35),
            origin=(0, 0),
            scale=4.0,
            color=color.rgb(0.863, 0.863, 0.902),
            parent=camera.ui
        )
        self.ui_elements.append(title)

        # Hint text
        hint = Text(
            text="Press ESC to Resume",
            position=(0, 0.23),
            origin=(0, 0),
            scale=1.3,
            color=color.rgb(0.588, 0.588, 0.667),
            parent=camera.ui
        )
        self.ui_elements.append(hint)

        # Buttons (dungeon-styled)
        button_y = 0.08
        button_spacing = 0.12  # Slightly more spacing
        button_width = 0.32
        button_height = 0.09

        self.resume_button = DungeonButton(
            text="RESUME",
            scale=(button_width, button_height),
            position=(0, button_y),
            parent=camera.ui,
            on_click=self._resume
        )
        self.ui_elements.append(self.resume_button)

        self.restart_button = DungeonButton(
            text="RESTART",
            scale=(button_width, button_height),
            position=(0, button_y - button_spacing),
            parent=camera.ui,
            on_click=self._restart
        )
        self.ui_elements.append(self.restart_button)

        self.settings_button = DungeonButton(
            text="SETTINGS",
            scale=(button_width, button_height),
            position=(0, button_y - button_spacing * 2),
            parent=camera.ui,
            on_click=self._settings
        )
        self.ui_elements.append(self.settings_button)

        self.main_menu_button = DungeonButton(
            text="MAIN MENU",
            scale=(button_width, button_height),
            position=(0, button_y - button_spacing * 3),
            parent=camera.ui,
            on_click=self._main_menu
        )
        self.ui_elements.append(self.main_menu_button)

        self.quit_button = DungeonButton(
            text="QUIT",
            scale=(button_width, button_height),
            position=(0, button_y - button_spacing * 4),
            parent=camera.ui,
            on_click=self._quit
        )
        self.ui_elements.append(self.quit_button)

    def _resume(self):
        """Resume game"""
        self.audio.play_ui_select()
        print("[PauseMenu] Resume clicked")
        self.screen_manager.resume_from_pause()

    def _restart(self):
        """Restart game (return to class selection)"""
        self.audio.play_ui_select()
        print("[PauseMenu] Restart clicked")
        # First resume from pause, then change to class selection
        self.screen_manager.resume_from_pause()
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.CLASS_SELECTION)

    def _settings(self):
        """Open settings"""
        self.audio.play_ui_select()
        print("[PauseMenu] Settings clicked")
        # First resume from pause, then change to settings
        self.screen_manager.resume_from_pause()
        from ui.screens.screen_manager_3d import ScreenState
        # Set previous state as GAME so settings knows to return to pause menu context
        self.screen_manager.change_screen(ScreenState.SETTINGS)

    def _main_menu(self):
        """Return to main menu"""
        self.audio.play_ui_select()
        print("[PauseMenu] Main Menu clicked")
        # First resume from pause, then change to main menu
        self.screen_manager.resume_from_pause()
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.MAIN_MENU)

    def _quit(self):
        """Quit the game"""
        self.audio.play_ui_select()
        print("[PauseMenu] Quit clicked")
        self.screen_manager.quit_game()

    def update(self):
        """Handle input for resuming"""
        if not self.enabled:
            return

        # ESC key resumes game
        if held_keys['escape']:
            if not self.esc_pressed:
                self.esc_pressed = True
                self._resume()
        else:
            self.esc_pressed = False

    def show(self):
        """Show the pause menu"""
        self.enabled = True

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Set ESC as pressed to prevent immediate closing from the same ESC press that opened the menu
        self.esc_pressed = True

        # Play pause sound
        self.audio.play_ui_select()

        print("[PauseMenu] Pause menu shown")

    def hide(self):
        """Hide the pause menu"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        print("[PauseMenu] Pause menu hidden")
