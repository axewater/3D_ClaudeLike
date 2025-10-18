"""
Main menu screen with star tunnel background and navigation options
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *

import time
import math
import random

import constants as c
from audio import get_audio_manager


class MainMenuScreen(QOpenGLWidget):
    """Main menu screen with star tunnel background and navigation options"""
    new_game_clicked = pyqtSignal()
    how_to_play_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Star tunnel state
        self.stars = []
        self.time_elapsed = 0.0
        self.last_time = time.time()

        # UI elements (created after OpenGL init)
        self.ui_widget = None
        self.buttons = []

        # Timer for animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Audio
        self.audio = get_audio_manager()

    def _init_stars(self):
        """Initialize star tunnel with 800-1000 stars in cylindrical distribution"""
        num_stars = random.randint(800, 1000)

        for _ in range(num_stars):
            # Cylindrical distribution for tunnel effect
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, 18)  # Max radius from center

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = random.uniform(-60, -5)  # Depth range

            # Rotation angle for spiral effect
            rotation_angle = random.uniform(0, 360)

            # Speed varies per star
            speed = random.uniform(0.8, 1.5)

            self.stars.append({
                'x': x, 'y': y, 'z': z,
                'angle': rotation_angle,
                'speed': speed,
                'size': 1.0,
                'base_x': x,  # Remember original radius position
                'base_y': y
            })

    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Background color (dark blue-purple like title screen)
        glClearColor(0.05, 0.05, 0.15, 1.0)

        # Initialize stars
        self._init_stars()

        # Create UI overlay
        self.setup_ui()

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Set up perspective projection
        aspect = w / h if h > 0 else 1
        gluPerspective(45, aspect, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the 3D scene and 2D overlay"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Position camera
        gluLookAt(
            0, 0, 8,  # Camera position
            0, 0, 0,  # Look at origin
            0, 1, 0   # Up vector
        )

        # Draw star tunnel
        self._draw_starfield()

        # Draw 2D UI overlay
        self._draw_ui_overlay()

    def _draw_starfield(self):
        """Draw animated rotating star tunnel"""
        glDisable(GL_LIGHTING)
        glEnable(GL_POINT_SMOOTH)  # Anti-aliased points

        for star in self.stars:
            # Apply rotation around Z-axis for spiral effect
            angle_rad = math.radians(star['angle'])
            radius = math.sqrt(star['base_x']**2 + star['base_y']**2)
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            z = star['z']

            # Calculate depth factor (0 = far, 1 = near)
            depth_factor = (z + 60) / 55
            depth_factor = max(0, min(1, depth_factor))

            # Size based on depth (closer = bigger)
            size = 1.0 + depth_factor * 3.5
            glPointSize(size)

            # Color: Blue-white gradient based on depth and twinkle
            twinkle = 0.5 + 0.5 * math.sin(self.time_elapsed * 3 + star['angle'])
            base_brightness = 0.3 + depth_factor * 0.5 + twinkle * 0.2

            r = base_brightness * (0.7 + depth_factor * 0.3)
            g = base_brightness * (0.7 + depth_factor * 0.3)
            b = base_brightness * (0.9 + depth_factor * 0.1)

            glBegin(GL_POINTS)
            glColor4f(r, g, b, 0.8 + depth_factor * 0.2)
            glVertex3f(x, y, z)
            glEnd()

            # Draw motion blur trail for close, fast stars
            if depth_factor > 0.6 and star['speed'] > 1.2:
                trail_length = depth_factor * 2.0
                trail_alpha = depth_factor * 0.3

                glBegin(GL_LINES)
                glColor4f(r, g, b, trail_alpha)
                glVertex3f(x, y, z)
                glVertex3f(x, y, z - trail_length)
                glEnd()

        glDisable(GL_POINT_SMOOTH)

    def _draw_ui_overlay(self):
        """Draw 2D UI overlay (title and buttons)"""
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Note: Actual buttons are rendered by Qt widget overlay
        # This is just for any custom OpenGL UI elements if needed

        glEnable(GL_DEPTH_TEST)

        # Restore 3D projection
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def setup_ui(self):
        """Setup the UI overlay with buttons"""
        # Create a transparent overlay widget for buttons
        self.ui_widget = QWidget(self)
        self.ui_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui_widget.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Title
        title = QLabel("CLAUDE-LIKE")
        title.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: rgb(200, 180, 255);
            padding: 40px;
        """)
        layout.addWidget(title)

        # Menu buttons
        button_width = 400
        button_height = 70

        # New Game button
        new_game_btn = self._create_menu_button("New Game", button_width, button_height)
        new_game_btn.clicked.connect(self._on_new_game)
        layout.addWidget(new_game_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons.append(new_game_btn)

        # How to Play button
        how_to_btn = self._create_menu_button("How to Play", button_width, button_height)
        how_to_btn.clicked.connect(self._on_how_to_play)
        layout.addWidget(how_to_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons.append(how_to_btn)

        # Settings button
        settings_btn = self._create_menu_button("Settings", button_width, button_height)
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons.append(settings_btn)

        # Quit button
        quit_btn = self._create_menu_button("Quit", button_width, button_height)
        quit_btn.clicked.connect(self._on_quit)
        layout.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons.append(quit_btn)

        self.ui_widget.setLayout(layout)

    def _create_menu_button(self, text: str, width: int, height: int) -> QPushButton:
        """Create a dungeon-themed stone button"""
        button = QPushButton(text)
        button.setFixedSize(width, height)
        button.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Install event filter for hover sound
        button.installEventFilter(self)

        # Dungeon stone/brick theme
        button.setStyleSheet("""
            QPushButton {
                background-color: rgb(50, 48, 45);
                color: rgb(180, 180, 190);
                border: 5px solid rgb(65, 60, 55);
                border-radius: 8px;
                padding: 18px;
            }
            QPushButton:hover {
                background-color: rgb(60, 58, 55);
                color: rgb(210, 190, 255);
                border: 5px solid rgb(120, 100, 180);
            }
            QPushButton:pressed {
                background-color: rgb(45, 43, 40);
                color: rgb(170, 150, 200);
                border: 5px solid rgb(100, 80, 150);
            }
        """)

        return button

    def eventFilter(self, obj, event):
        """Filter events to detect hover for sound"""
        if isinstance(obj, QPushButton) and event.type() == event.Type.Enter:
            self.audio.play_ui_hover()
        return super().eventFilter(obj, event)

    def _on_new_game(self):
        """Handle New Game click"""
        self.audio.play_ui_select()
        self.new_game_clicked.emit()

    def _on_how_to_play(self):
        """Handle How to Play click"""
        self.audio.play_ui_select()
        self.how_to_play_clicked.emit()

    def _on_settings(self):
        """Handle Settings click"""
        self.audio.play_ui_select()
        self.settings_clicked.emit()

    def _on_quit(self):
        """Handle Quit click"""
        self.audio.play_ui_select()
        self.quit_clicked.emit()

    def update_animation(self):
        """Update star tunnel animation"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time_elapsed += dt

        # Update star tunnel - move toward camera and rotate
        for star in self.stars:
            # Move toward camera
            star['z'] += dt * star['speed'] * 25

            # Rotate around Z-axis for spiral effect
            star['angle'] += dt * 30  # Degrees per second

            # Respawn star at back when it reaches camera
            if star['z'] > -1:
                star['z'] = -60
                # Randomize position slightly on respawn
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 18)
                star['base_x'] = radius * math.cos(angle)
                star['base_y'] = radius * math.sin(angle)
                star['angle'] = random.uniform(0, 360)
                star['speed'] = random.uniform(0.8, 1.5)

        self.update()

    def resizeEvent(self, event):
        """Handle resize to update UI widget"""
        super().resizeEvent(event)
        if self.ui_widget:
            self.ui_widget.setGeometry(0, 0, self.width(), self.height())
