"""
Screen Manager for 3D Mode

Manages screen states and transitions for the 3D game mode.
Handles: Title, Menu, Class Selection, Game, Victory, Game Over, and Pause screens.
"""

from enum import Enum
from typing import Optional, Callable
from ursina import Entity, camera, window, destroy, time as ursina_time


class ScreenState(Enum):
    """Screen states for the 3D game"""
    TITLE = "title"
    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    CLASS_SELECTION = "class_selection"
    GAME = "game"
    VICTORY = "victory"
    GAME_OVER = "game_over"
    PAUSE = "pause"  # Overlay state


class ScreenManager3D:
    """
    Manages screen transitions and state for 3D mode.

    Screens can be:
    - Full screens (replace current content)
    - Overlay screens (pause menu, settings)
    """

    def __init__(self):
        self.current_state = ScreenState.TITLE
        self.previous_state = None  # For returning from pause/overlay

        # Screen instances (lazy loaded)
        self.title_screen = None
        self.main_menu = None
        self.settings_screen = None
        self.class_selection = None
        self.game_controller = None
        self.victory_screen = None
        self.game_over_screen = None
        self.pause_menu = None

        # Transition state
        self.transitioning = False
        self.transition_progress = 0.0
        self.transition_duration = 0.3  # Seconds
        self.transition_callback = None  # Called when transition completes
        self.screen_switched = False  # Track if screen switch happened during transition

        # Fade overlay for transitions
        self.fade_overlay = None

        print("✓ ScreenManager3D initialized")

    def change_screen(self, new_state: ScreenState, callback: Optional[Callable] = None):
        """
        Change to a new screen with fade transition.

        Args:
            new_state: Target screen state
            callback: Optional function to call after transition completes
        """
        if self.transitioning:
            print(f"[ScreenManager] Already transitioning, ignoring request to {new_state}")
            return

        print(f"[ScreenManager] Changing screen: {self.current_state} → {new_state}")

        # Special handling for pause (overlay, not transition)
        if new_state == ScreenState.PAUSE:
            self._show_pause_overlay()
            return

        # Start transition
        self.transitioning = True
        self.transition_progress = 0.0
        self.transition_callback = callback
        self.previous_state = self.current_state
        self.screen_switched = False  # Reset flag

        # Fade out current screen, then fade in new screen
        self._start_fade_out(new_state)

    def _start_fade_out(self, target_state: ScreenState):
        """Start fade out animation"""
        # Create fade overlay if it doesn't exist
        if not self.fade_overlay:
            self.fade_overlay = Entity(
                model='quad',
                color=(0, 0, 0, 0),  # RGBA - Start transparent
                scale=(100, 100),  # Large enough to cover screen
                position=(0, 0, -0.1),  # In front of everything
                parent=camera.ui,
                enabled=False
            )

        self.fade_overlay.enabled = True
        self.fade_overlay.color = (0, 0, 0, 0)  # Start transparent

        # Store target state for when fade completes
        self._target_state = target_state

    def update(self, dt: float):
        """Update transition animations"""
        if not self.transitioning:
            return

        self.transition_progress += dt / self.transition_duration

        # Switch screen when we cross the midpoint (progress >= 1.0), but only once
        if self.transition_progress >= 1.0 and not self.screen_switched:
            self._switch_to_new_screen(self._target_state)
            self.screen_switched = True
            print(f"[ScreenManager] Screen switched → {self.current_state}")

        # Complete transition when fade in is done (progress >= 2.0)
        if self.transition_progress >= 2.0:
            # Transition complete
            self.transitioning = False
            self.transition_progress = 0.0
            self.screen_switched = False
            if self.fade_overlay:
                self.fade_overlay.enabled = False

            # Call callback if provided
            if self.transition_callback:
                self.transition_callback()
                self.transition_callback = None

            print(f"[ScreenManager] Transition complete → {self.current_state}")

        # Update fade overlay alpha
        if self.transition_progress < 1.0:
            # Fade out (0 → 1)
            alpha = min(self.transition_progress, 1.0)
        else:
            # Fade in (1 → 0)
            alpha = max(2.0 - self.transition_progress, 0.0)

        if self.fade_overlay:
            self.fade_overlay.color = (0, 0, 0, alpha)

    def _switch_to_new_screen(self, new_state: ScreenState):
        """
        Clean up current screen and initialize new screen.
        Called at the midpoint of transition (screen is fully black).
        """
        # Clean up previous screen
        self._cleanup_current_screen()

        # Update state
        self.current_state = new_state

        # Initialize new screen
        self._initialize_screen(new_state)

    def _cleanup_current_screen(self):
        """Clean up/hide current screen"""
        if self.current_state == ScreenState.TITLE:
            if self.title_screen:
                self.title_screen.hide()

        elif self.current_state == ScreenState.MAIN_MENU:
            if self.main_menu:
                self.main_menu.hide()

        elif self.current_state == ScreenState.SETTINGS:
            if self.settings_screen:
                self.settings_screen.hide()

        elif self.current_state == ScreenState.CLASS_SELECTION:
            if self.class_selection:
                self.class_selection.hide()

        elif self.current_state == ScreenState.GAME:
            if self.game_controller:
                # Pause/hide game (don't destroy, might resume)
                self.game_controller.enabled = False

        elif self.current_state == ScreenState.VICTORY:
            if self.victory_screen:
                self.victory_screen.hide()

        elif self.current_state == ScreenState.GAME_OVER:
            if self.game_over_screen:
                self.game_over_screen.hide()

    def _initialize_screen(self, state: ScreenState):
        """Initialize/show target screen"""
        if state == ScreenState.TITLE:
            # Import here to avoid circular imports
            from ui.screens.title_screen_3d import TitleScreen3D
            if not self.title_screen:
                # Create PyQt6 title screen
                # Note: This will need special integration with Ursina
                print("[ScreenManager] Title screen needs PyQt6 integration")
                # For now, skip to main menu
                self.change_screen(ScreenState.MAIN_MENU)
            else:
                self.title_screen.show()

        elif state == ScreenState.MAIN_MENU:
            # Import here to avoid circular imports
            from ui.screens.main_menu_3d import MainMenu3D
            if not self.main_menu:
                self.main_menu = MainMenu3D(self)
            self.main_menu.show()

        elif state == ScreenState.SETTINGS:
            # Import here to avoid circular imports
            from ui.screens.settings_screen_3d import Settings3D
            if not self.settings_screen:
                self.settings_screen = Settings3D(self)
            # Set previous screen so Back button works
            self.settings_screen.set_previous_screen(self.previous_state)
            self.settings_screen.show()

        elif state == ScreenState.CLASS_SELECTION:
            if not self.class_selection:
                # Create class selection screen
                from ui.screens.class_selection_3d import ClassSelection3D
                self.class_selection = ClassSelection3D(self)
            self.class_selection.show()

        elif state == ScreenState.GAME:
            if self.game_controller:
                # Resume existing game
                self.game_controller.enabled = True
            else:
                # Start new game (should be initialized externally)
                print("[ScreenManager] Game controller should be set externally")

        elif state == ScreenState.VICTORY:
            if not self.victory_screen:
                from ui.screens.victory_screen_3d import VictoryScreen3D
                self.victory_screen = VictoryScreen3D(self)
            self.victory_screen.show()

        elif state == ScreenState.GAME_OVER:
            if not self.game_over_screen:
                from ui.screens.game_over_3d import GameOverScreen3D
                self.game_over_screen = GameOverScreen3D(self)
            self.game_over_screen.show()

    def _show_pause_overlay(self):
        """Show pause menu as overlay (doesn't replace current screen)"""
        if not self.pause_menu:
            from ui.screens.pause_menu_3d import PauseMenu3D
            self.pause_menu = PauseMenu3D(self)

        self.previous_state = self.current_state
        self.current_state = ScreenState.PAUSE
        self.pause_menu.show()

        # Pause game controller if active
        if self.game_controller:
            self.game_controller.paused = True
            # Hide game UI to prevent layering issues with pause menu
            if hasattr(self.game_controller, 'ui_manager') and self.game_controller.ui_manager:
                self.game_controller.ui_manager.set_visibility(False)

        print(f"[ScreenManager] Paused (previous state: {self.previous_state})")

    def resume_from_pause(self):
        """Resume from pause menu"""
        if self.current_state != ScreenState.PAUSE:
            print("[ScreenManager] Not paused, cannot resume")
            return

        if self.pause_menu:
            self.pause_menu.hide()

        # Resume game controller
        if self.game_controller:
            # Show game UI again
            if hasattr(self.game_controller, 'ui_manager') and self.game_controller.ui_manager:
                self.game_controller.ui_manager.set_visibility(True)
            self.game_controller.paused = False

        # Restore previous state
        self.current_state = self.previous_state
        self.previous_state = None

        print(f"[ScreenManager] Resumed to {self.current_state}")

    def set_game_controller(self, controller):
        """Set the game controller instance (called from main_3d.py)"""
        self.game_controller = controller
        print("[ScreenManager] Game controller registered")

    def show_victory(self, stats: dict):
        """Show victory screen with stats"""
        if self.victory_screen:
            self.victory_screen.set_stats(stats)
        self.change_screen(ScreenState.VICTORY)

    def show_game_over(self, stats: dict, death_reason: str):
        """Show game over screen with stats and death reason"""
        if self.game_over_screen:
            self.game_over_screen.set_stats(stats, death_reason)
        self.change_screen(ScreenState.GAME_OVER)

    def start_game_with_class(self, class_type: str):
        """Start game with selected class (called from class selection)"""
        print(f"[ScreenManager] Starting game with class: {class_type}")
        self.selected_class = class_type

    def quit_game(self):
        """Quit the application"""
        print("[ScreenManager] Quitting game")
        from ursina import application
        application.quit()
