"""
Main window orchestrating all screens and game flow
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
                               QDialog, QVBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeyEvent
import time

import constants as c
from game import Game
from audio import get_audio_manager
from ui.screens.title_screen_3d import TitleScreen3D
from ui.screens.main_menu import MainMenuScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.class_selection import ClassSelectionScreen
from ui.screens.victory_screen import VictoryScreen
from ui.widgets.game_widget import GameWidget
from ui.widgets.stats_panel import StatsPanel


class MainWindow(QMainWindow):
    """Main game window"""
    def __init__(self):
        super().__init__()
        self.game = Game()

        self.setWindowTitle("Claude-Like")
        self.setFixedSize(c.WINDOW_WIDTH, c.WINDOW_HEIGHT)

        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()

        # Title screen (shown first) - 3D OpenGL version
        self.title_screen = TitleScreen3D()
        self.title_screen.continue_pressed.connect(self.on_title_continue)
        self.stacked_widget.addWidget(self.title_screen)

        # Main menu screen
        self.main_menu = MainMenuScreen()
        self.main_menu.new_game_clicked.connect(self.on_new_game)
        self.main_menu.how_to_play_clicked.connect(self.on_how_to_play)
        self.main_menu.settings_clicked.connect(self.on_settings)
        self.main_menu.quit_clicked.connect(self.close)
        self.stacked_widget.addWidget(self.main_menu)

        # Settings screen
        self.settings_screen = SettingsScreen()
        self.settings_screen.back_clicked.connect(self.on_settings_back)
        self.stacked_widget.addWidget(self.settings_screen)

        # Class selection screen
        self.class_selection = ClassSelectionScreen()
        self.class_selection.class_selected.connect(self.on_class_selected)
        self.class_selection.back_clicked.connect(self.on_class_back)
        self.stacked_widget.addWidget(self.class_selection)

        # Game screen
        self.game_screen = QWidget()
        game_layout = QHBoxLayout()

        self.game_widget = GameWidget(self.game)
        game_layout.addWidget(self.game_widget)

        self.stats_panel = StatsPanel(self.game)
        game_layout.addWidget(self.stats_panel)

        # Wire up the combat log callback
        self.game.message_callback = self.stats_panel.add_message_to_log

        self.game_screen.setLayout(game_layout)
        self.stacked_widget.addWidget(self.game_screen)

        # Victory screen
        self.victory_screen = VictoryScreen()
        self.victory_screen.return_to_menu.connect(self.on_victory_return_to_menu)
        self.stacked_widget.addWidget(self.victory_screen)

        # Set stacked widget as central widget
        self.setCentralWidget(self.stacked_widget)

        # Time tracking for animations
        self.last_time = time.time()

        # Update timer - faster for smooth animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(16)  # ~60 FPS

        # Track previous screen for settings navigation
        self.previous_screen = None

        # Start background music on title screen
        audio = get_audio_manager()
        audio.start_background_music()

    def on_title_continue(self):
        """Handle title screen continue"""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def on_new_game(self):
        """Handle New Game from main menu"""
        self.stacked_widget.setCurrentWidget(self.class_selection)

    def on_class_back(self):
        """Handle back from class selection"""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def on_settings(self):
        """Handle Settings from main menu"""
        self.previous_screen = self.main_menu
        self.stacked_widget.setCurrentWidget(self.settings_screen)

    def on_settings_back(self):
        """Handle back from settings"""
        # Return to previous screen (main menu or game)
        if self.previous_screen:
            self.stacked_widget.setCurrentWidget(self.previous_screen)
            # Restore focus to game widget if returning to game
            if self.previous_screen == self.game_screen:
                self.game_widget.setFocus()
        else:
            self.stacked_widget.setCurrentWidget(self.main_menu)

    def on_how_to_play(self):
        """Show How to Play dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("How to Play")
        dialog.setModal(True)
        dialog.setFixedSize(600, 500)
        dialog.setStyleSheet(f"background-color: rgb({c.COLOR_PANEL_BG.red()}, {c.COLOR_PANEL_BG.green()}, {c.COLOR_PANEL_BG.blue()});")

        layout = QVBoxLayout()

        # Title
        title = QLabel("HOW TO PLAY")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); padding: 15px;")
        layout.addWidget(title)

        # Instructions
        instructions = """
        <p style='color: rgb(200, 200, 200); font-size: 12pt; line-height: 1.8;'>
        <b>OBJECTIVE:</b><br/>
        Conquer all 25 levels of the dungeon! Defeat enemies, collect loot, and descend through 5 unique biomes to achieve victory!<br/><br/>

        <b>CONTROLS:</b><br/>
        • <b>WASD / Arrow Keys</b> - Move your character<br/>
        • <b>Click</b> - Move to location (pathfinding)<br/>
        • <b>Bump into enemies</b> - Attack them<br/>
        • <b>1, 2, 3</b> - Use abilities (class-specific)<br/>
        • <b>ESC</b> - Pause menu (Resume/Settings/Main Menu)<br/>
        • <b>R</b> - Restart game<br/>
        • <b>Q</b> - Quit<br/><br/>

        <b>GAMEPLAY:</b><br/>
        • Fight enemies to gain XP and level up<br/>
        • Collect equipment to boost your stats<br/>
        • Find the stairs (purple) to descend to the next level<br/>
        • Health potions restore HP immediately<br/>
        • Abilities have cooldowns (shown in turns)<br/><br/>

        <b>TIPS:</b><br/>
        • Choose your class wisely - each has unique abilities<br/>
        • The environment changes every 5 levels (Dungeon → Catacombs → Caves → Hell → Abyss)<br/>
        • Higher dungeon levels have better loot but stronger enemies<br/>
        • Equipment rarity affects stat bonuses (Common → Legendary)<br/>
        • Complete all 25 levels to achieve victory!<br/>
        </p>
        """

        info_label = QLabel(instructions)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        info_label.setStyleSheet("padding: 10px;")
        layout.addWidget(info_label)

        # Close button
        close_btn = QPushButton("Got it!")
        close_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(100, 100, 255);
                color: rgb(255, 255, 255);
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(130, 130, 255);
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def show_pause_menu(self):
        """Show pause menu during gameplay"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Paused")
        dialog.setModal(True)
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(f"background-color: rgb({c.COLOR_PANEL_BG.red()}, {c.COLOR_PANEL_BG.green()}, {c.COLOR_PANEL_BG.blue()});")

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = QLabel("PAUSED")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); padding: 20px;")
        layout.addWidget(title)

        # Resume button
        resume_btn = QPushButton("Resume")
        resume_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        resume_btn.setFixedHeight(50)
        resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        resume_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(100, 150, 255);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(80, 120, 200);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(130, 170, 255);
            }
        """)
        resume_btn.clicked.connect(dialog.accept)
        layout.addWidget(resume_btn)

        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        settings_btn.setFixedHeight(50)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(100, 100, 150);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 80, 120);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(120, 120, 170);
            }
        """)
        def open_settings():
            dialog.accept()
            self.previous_screen = self.game_screen
            self.stacked_widget.setCurrentWidget(self.settings_screen)
        settings_btn.clicked.connect(open_settings)
        layout.addWidget(settings_btn)

        # Main Menu button
        main_menu_btn = QPushButton("Main Menu")
        main_menu_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_menu_btn.setFixedHeight(50)
        main_menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        main_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(150, 80, 80);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(120, 60, 60);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(170, 100, 100);
            }
        """)
        def go_to_main_menu():
            dialog.accept()
            self.stacked_widget.setCurrentWidget(self.main_menu)
        main_menu_btn.clicked.connect(go_to_main_menu)
        layout.addWidget(main_menu_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def on_class_selected(self, class_type: str):
        """Handle class selection"""
        self.game.selected_class = class_type
        self.game.start_new_game()
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.game_widget.setFocus()

    def on_victory_return_to_menu(self):
        """Handle return to menu from victory screen"""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def update_display(self):
        """Update game display"""
        # Calculate delta time
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Update game state
        self.game.update(dt)

        # Update animations
        self.game.anim_manager.update(dt)

        # Check for victory condition
        if self.game.victory and self.stacked_widget.currentWidget() != self.victory_screen:
            self.stacked_widget.setCurrentWidget(self.victory_screen)
            return

        # Update display
        self.game_widget.update()
        self.stats_panel.update_stats()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key presses"""
        key = event.key()

        # ESC to cancel targeting mode or show pause menu
        if key == Qt.Key.Key_Escape:
            # First priority: cancel targeting mode if active
            if self.game_widget.targeting_mode:
                self.game_widget.targeting_mode = False
                self.game_widget.targeting_ability_index = None
                self.update_display()
                return

            # Otherwise: show pause menu if in game
            if self.stacked_widget.currentWidget() == self.game_screen and not self.game.game_over:
                self.show_pause_menu()
                return

        # Debug commands (F1, F2, F3)
        if key == Qt.Key.Key_F1:
            # F1: Reveal entire map
            if self.game.visibility_map:
                self.game.visibility_map.reveal_all()
                self.game.add_message("DEBUG: Map fully revealed!", "event")
                print("🗺️  DEBUG: Full map revealed")
            self.update_display()
            return
        elif key == Qt.Key.Key_F2:
            # F2: Toggle enemy FOV debug display
            if not hasattr(self.game_widget, 'debug_show_enemy_fov'):
                self.game_widget.debug_show_enemy_fov = False
            self.game_widget.debug_show_enemy_fov = not self.game_widget.debug_show_enemy_fov
            status = "ON" if self.game_widget.debug_show_enemy_fov else "OFF"
            self.game.add_message(f"DEBUG: Enemy FOV display {status}", "event")
            print(f"👁️  DEBUG: Enemy FOV display {status}")
            self.update_display()
            return
        elif key == Qt.Key.Key_F3:
            # F3: Skip to next level
            if not self.game.game_over and not self.game.victory:
                self.game.debug_skip_level()
                print(f"⏭️  DEBUG: Skipped to level {self.game.current_level}")
            self.update_display()
            return

        # Abilities (keys 1, 2, 3)
        if key == Qt.Key.Key_1:
            self.game.use_ability(0)
            self.update_display()
            return
        elif key == Qt.Key.Key_2:
            self.game.use_ability(1)
            self.update_display()
            return
        elif key == Qt.Key.Key_3:
            self.game.use_ability(2)
            self.update_display()
            return

        # Movement
        dx, dy = 0, 0
        if key in (Qt.Key.Key_W, Qt.Key.Key_Up):
            dy = -1
        elif key in (Qt.Key.Key_S, Qt.Key.Key_Down):
            dy = 1
        elif key in (Qt.Key.Key_A, Qt.Key.Key_Left):
            dx = -1
        elif key in (Qt.Key.Key_D, Qt.Key.Key_Right):
            dx = 1
        elif key == Qt.Key.Key_R:
            # Restart game - go back to main menu
            self.stacked_widget.setCurrentWidget(self.main_menu)
            return
        elif key == Qt.Key.Key_T:
            # Test taunt (debug feature)
            print("🎮 Test taunt key pressed!")
            audio = get_audio_manager()
            audio.play_voice_taunt()
            return
        elif key == Qt.Key.Key_Q:
            # Quit
            self.close()
            return

        if dx != 0 or dy != 0:
            self.game.player_move(dx, dy)

        # Update display after movement
        self.update_display()

    def closeEvent(self, event):
        """Handle window close event - cleanup audio"""
        print("🚪 Closing window...")

        # Shutdown audio manager to stop all sounds
        audio = get_audio_manager()
        audio.shutdown()

        # Accept the close event
        event.accept()
        print("✓ Window closed")
