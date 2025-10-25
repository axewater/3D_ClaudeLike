"""
3D Main Menu Screen

Main menu with navigation options.
Uses Ursina for 3D rendering and UI.
"""

from ursina import Entity, camera, color, Text, Button, Vec3
import constants as c
from audio import get_audio_manager
from ui.widgets.dungeon_button_3d import DungeonButton


class MainMenu3D(Entity):
    """
    3D main menu screen.

    Options:
    - New Game -> Class Selection
    - How to Play -> Info dialog
    - Settings -> Settings screen
    - Quit -> Exit application
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # UI elements
        self.ui_elements = []
        self.buttons = []
        self.how_to_play_panel = None
        self.showing_how_to_play = False

        # Initialize
        self._create_ui()

        # Initially hidden
        self.enabled = False

    def _create_ui(self):
        """Create UI overlay elements"""
        # Title
        self.title = Text(
            text="CLAUDE-LIKE",
            position=(0, 0.38),
            origin=(0, 0),
            scale=3.5,
            color=color.rgb(0.784, 0.706, 1.0),  # (200, 180, 255)
            parent=camera.ui
        )
        self.ui_elements.append(self.title)

        # Subtitle
        self.subtitle = Text(
            text="A Roguelike Adventure",
            position=(0, 0.28),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.588, 0.588, 0.706),  # (150, 150, 180)
            parent=camera.ui
        )
        self.ui_elements.append(self.subtitle)

        # Menu buttons (dungeon-styled)
        button_y_start = 0.08
        button_spacing = 0.13  # Slightly more spacing
        button_width = 0.35  # Slightly wider
        button_height = 0.09  # Slightly taller

        # New Game button
        self.new_game_button = DungeonButton(
            text="NEW GAME",
            scale=(button_width, button_height),
            position=(0, button_y_start),
            parent=camera.ui,
            on_click=self._on_new_game
        )
        self.buttons.append(self.new_game_button)
        self.ui_elements.append(self.new_game_button)

        # How to Play button
        self.how_to_play_button = DungeonButton(
            text="HOW TO PLAY",
            scale=(button_width, button_height),
            position=(0, button_y_start - button_spacing),
            parent=camera.ui,
            on_click=self._on_how_to_play
        )
        self.buttons.append(self.how_to_play_button)
        self.ui_elements.append(self.how_to_play_button)

        # Settings button
        self.settings_button = DungeonButton(
            text="SETTINGS",
            scale=(button_width, button_height),
            position=(0, button_y_start - button_spacing * 2),
            parent=camera.ui,
            on_click=self._on_settings
        )
        self.buttons.append(self.settings_button)
        self.ui_elements.append(self.settings_button)

        # Quit button
        self.quit_button = DungeonButton(
            text="QUIT",
            scale=(button_width, button_height),
            position=(0, button_y_start - button_spacing * 3),
            parent=camera.ui,
            on_click=self._on_quit
        )
        self.buttons.append(self.quit_button)
        self.ui_elements.append(self.quit_button)

    def _on_new_game(self):
        """Handle New Game button click"""
        self.audio.play_ui_select()

        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.CLASS_SELECTION)

    def _on_how_to_play(self):
        """Handle How to Play button click"""
        self.audio.play_ui_select()

        if not self.showing_how_to_play:
            self._show_how_to_play_panel()
        else:
            self._hide_how_to_play_panel()

    def _show_how_to_play_panel(self):
        """Show How to Play information panel"""
        self.showing_how_to_play = True

        # Hide main menu buttons while panel is open
        for button in self.buttons:
            button.enabled = False

        # Hide title and subtitle
        self.title.enabled = False
        self.subtitle.enabled = False

        # Dim background overlay (furthest back)
        self.how_to_play_bg = Entity(
            model='quad',
            color=(0, 0, 0, 200/255),
            scale=(100, 100),
            position=(0, 0, 0.5),  # Positive z = behind everything
            parent=camera.ui,
            collider=None  # Prevent blocking mouse input
        )

        # Panel background (in middle)
        panel_bg = Entity(
            model='quad',
            color=color.rgb(0.157, 0.157, 0.176),  # (40, 40, 45)
            scale=(1.4, 1.6),
            position=(0, 0, 0.4),  # Positive z = behind text
            parent=camera.ui,
            collider=None  # Prevent blocking mouse input
        )

        # Title (in front) - smaller and higher
        title = Text(
            text="HOW TO PLAY",
            position=(0, 0.42, -0.2),  # Moved down from 0.68
            origin=(0, 0),
            scale=2.0,  # Reduced from 2.5
            color=color.rgb(0.863, 0.863, 0.902),  # (220, 220, 230)
            parent=camera.ui
        )

        # Objective (centered, above columns)
        objective = Text(
            text="OBJECTIVE: Conquer all 25 levels!",
            position=(0, 0.30, -0.2),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0.863, 0.784, 0.627),  # Golden color
            parent=camera.ui
        )

        # Left column - CONTROLS & GAMEPLAY
        left_column = [
            ("CONTROLS:", True),
            ("WASD / Arrows - Move", False),
            ("1/2/3 - Use abilities", False),
            ("Left/Right - Rotate camera", False),
            ("ESC - Pause menu", False),
            ("", False),
            ("GAMEPLAY:", True),
            ("• Fight enemies for XP", False),
            ("• Collect equipment", False),
            ("• Find purple stairs", False),
            ("• Potions restore HP", False),
        ]

        # Right column - TIPS
        right_column = [
            ("TIPS:", True),
            ("• Choose class wisely", False),
            ("• Env changes every 5 levels", False),
            ("• Higher level = better loot", False),
            ("• Use abilities strategically", False),
            ("• Watch your HP!", False),
        ]

        # Create left column text
        instruction_entities = []
        line_y = 0.18
        line_spacing = 0.05
        x_left = -0.50

        for line, is_header in left_column:
            if line == "":
                line_y -= line_spacing * 0.5
                continue

            text_entity = Text(
                text=line,
                position=(x_left, line_y, -0.2),
                origin=(0, 0),
                scale=1.0 if is_header else 0.85,
                color=color.rgb(0.863, 0.863, 0.902) if is_header else color.rgb(0.784, 0.784, 0.824),
                parent=camera.ui
            )
            instruction_entities.append(text_entity)
            line_y -= line_spacing

        # Create right column text
        line_y = 0.18
        x_right = 0.02

        for line, is_header in right_column:
            if line == "":
                line_y -= line_spacing * 0.5
                continue

            text_entity = Text(
                text=line,
                position=(x_right, line_y, -0.2),
                origin=(0, 0),
                scale=1.0 if is_header else 0.85,
                color=color.rgb(0.863, 0.863, 0.902) if is_header else color.rgb(0.784, 0.784, 0.824),
                parent=camera.ui
            )
            instruction_entities.append(text_entity)
            line_y -= line_spacing

        # Close button (dungeon-styled) - needs to be even more in front
        close_button = DungeonButton(
            text="CLOSE",
            scale=(0.30, 0.10),  # Slightly larger for visibility
            position=(0, -0.45, -0.3),  # Moved up from -0.60
            parent=camera.ui,
            on_click=self._hide_how_to_play_panel
        )

        # Store references for cleanup
        self.how_to_play_panel = [
            self.how_to_play_bg,
            panel_bg,
            title,
            objective,
            close_button
        ] + instruction_entities


    def _hide_how_to_play_panel(self):
        """Hide How to Play panel"""
        if self.how_to_play_panel:
            from ursina import destroy
            for entity in self.how_to_play_panel:
                entity.enabled = False
                # Destroy to prevent memory leak
                destroy(entity)
            self.how_to_play_panel = None

        self.showing_how_to_play = False

        # Show main menu buttons again
        for button in self.buttons:
            button.enabled = True

        # Show title and subtitle again
        self.title.enabled = True
        self.subtitle.enabled = True

    def _on_settings(self):
        """Handle Settings button click"""
        self.audio.play_ui_select()

        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.SETTINGS)

    def _on_quit(self):
        """Handle Quit button click"""
        self.audio.play_ui_select()
        self.screen_manager.quit_game()

    def update(self):
        """Update method (currently unused but required by Ursina Entity)"""
        if not self.enabled:
            return

    def show(self):
        """Show the main menu"""
        self.enabled = True

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Reset camera position (in case it was moved)
        camera.position = Vec3(0, 0, 0)
        camera.rotation = Vec3(0, 0, 0)


    def hide(self):
        """Hide the main menu"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        # Hide how-to-play panel if showing
        if self.showing_how_to_play:
            self._hide_how_to_play_panel()

