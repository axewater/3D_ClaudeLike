"""
Settings screen with volume controls
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSlider
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import constants as c
from audio import get_audio_manager


class SettingsScreen(QWidget):
    """Settings screen with volume controls"""
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: rgb({c.COLOR_PANEL_BG.red()}, {c.COLOR_PANEL_BG.green()}, {c.COLOR_PANEL_BG.blue()});")

        # Get audio manager
        self.audio_manager = get_audio_manager()

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        # Title
        title = QLabel("SETTINGS")
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); padding: 20px;")
        layout.addWidget(title)

        # Settings container
        settings_container = QFrame()
        settings_container.setStyleSheet(f"""
            QFrame {{
                background-color: rgb(45, 45, 50);
                border: 2px solid rgb(80, 80, 90);
                border-radius: 15px;
                padding: 30px;
            }}
        """)
        settings_container.setFixedWidth(600)

        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(30)

        # Music Volume
        music_label = QLabel("Music Volume")
        music_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        music_label.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); border: none;")
        settings_layout.addWidget(music_label)

        music_slider_container = QHBoxLayout()
        self.music_slider = QSlider(Qt.Orientation.Horizontal)
        self.music_slider.setMinimum(0)
        self.music_slider.setMaximum(100)
        self.music_slider.setValue(int(self.audio_manager.music_volume * 100))
        self.music_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: rgb(60, 60, 70);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: rgb(150, 100, 255);
                border: 2px solid rgb(100, 50, 200);
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: rgb(180, 130, 255);
            }
        """)
        self.music_slider.valueChanged.connect(self._on_music_volume_changed)

        self.music_value_label = QLabel(f"{self.music_slider.value()}%")
        self.music_value_label.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.music_value_label.setFixedWidth(60)
        self.music_value_label.setStyleSheet("color: rgb(200, 200, 200); border: none;")

        music_slider_container.addWidget(self.music_slider)
        music_slider_container.addWidget(self.music_value_label)
        settings_layout.addLayout(music_slider_container)

        # SFX Volume
        sfx_label = QLabel("Sound Effects Volume")
        sfx_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        sfx_label.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); border: none;")
        settings_layout.addWidget(sfx_label)

        sfx_slider_container = QHBoxLayout()
        self.sfx_slider = QSlider(Qt.Orientation.Horizontal)
        self.sfx_slider.setMinimum(0)
        self.sfx_slider.setMaximum(100)
        self.sfx_slider.setValue(int(self.audio_manager.sfx_volume * 100))
        self.sfx_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: rgb(60, 60, 70);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: rgb(100, 200, 255);
                border: 2px solid rgb(50, 150, 200);
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: rgb(130, 220, 255);
            }
        """)
        self.sfx_slider.valueChanged.connect(self._on_sfx_volume_changed)

        self.sfx_value_label = QLabel(f"{self.sfx_slider.value()}%")
        self.sfx_value_label.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.sfx_value_label.setFixedWidth(60)
        self.sfx_value_label.setStyleSheet("color: rgb(200, 200, 200); border: none;")

        sfx_slider_container.addWidget(self.sfx_slider)
        sfx_slider_container.addWidget(self.sfx_value_label)
        settings_layout.addLayout(sfx_slider_container)

        settings_container.setLayout(settings_layout)
        layout.addWidget(settings_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        back_button.setFixedSize(300, 60)
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(80, 80, 100);
                color: rgb(220, 220, 220);
                border: 3px solid rgb(100, 100, 120);
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 130);
                border: 3px solid rgb(150, 150, 180);
            }
        """)
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _on_music_volume_changed(self, value):
        """Handle music volume slider change"""
        volume = value / 100.0
        self.audio_manager.set_music_volume(volume)
        self.music_value_label.setText(f"{value}%")

    def _on_sfx_volume_changed(self, value):
        """Handle SFX volume slider change"""
        volume = value / 100.0
        self.audio_manager.set_sfx_volume(volume)
        self.sfx_value_label.setText(f"{value}%")

        # Play a test sound
        if value > 0:
            self.audio_manager.play_ui_select()

    def _on_back_clicked(self):
        """Handle back button click"""
        self.audio_manager.play_ui_select()
        self.back_clicked.emit()
