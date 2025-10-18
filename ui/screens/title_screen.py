"""
Title screen with animated particles and glowing text
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont
import time
import math

from audio import get_audio_manager
from animations import AnimationManager


class TitleScreen(QWidget):
    """Animated title screen with particles"""
    continue_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(f"background-color: rgb(20, 20, 25);")

        # Animation manager for particles
        self.anim_manager = AnimationManager()
        self.time_elapsed = 0.0
        self.last_time = time.time()

        # Pulse animation for title
        self.title_pulse = 0.0

        # Fade animation for "Press Any Key"
        self.prompt_fade = 0.0

        # Timer for animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Spawn initial particles
        for _ in range(30):
            self.anim_manager.add_ambient_particles(count=1)

    def update_animation(self):
        """Update animations"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        self.time_elapsed += dt

        # Update animations
        self.anim_manager.update(dt)

        # Spawn ambient particles periodically
        if len(self.anim_manager.ambient_particles) < 40:
            self.anim_manager.add_ambient_particles(count=2)

        # Update pulse animation (sine wave for smooth pulsing)
        self.title_pulse = math.sin(self.time_elapsed * 2.0) * 0.5 + 0.5

        # Update prompt fade (slower sine wave)
        self.prompt_fade = math.sin(self.time_elapsed * 3.0) * 0.5 + 0.5

        self.update()

    def paintEvent(self, event):
        """Paint the title screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background gradient
        for y in range(self.height()):
            progress = y / self.height()
            r = int(20 + progress * 15)
            g = int(20 + progress * 15)
            b = int(25 + progress * 20)
            painter.setPen(QColor(r, g, b))
            painter.drawLine(0, y, self.width(), y)

        # Draw ambient particles
        for particle in self.anim_manager.ambient_particles:
            particle_color = QColor(particle.color.red(), particle.color.green(),
                                   particle.color.blue(), particle.alpha)
            painter.setBrush(particle_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(particle.x - particle.size / 2),
                              int(particle.y - particle.size / 2),
                              int(particle.size), int(particle.size))

        # Draw glowing title - "DUNGEON DELVER"
        title_y = self.height() // 3

        # Glow effect (multiple layers)
        glow_intensity = int(self.title_pulse * 100)
        for i in range(5, 0, -1):
            glow_alpha = glow_intensity - (i * 15)
            if glow_alpha > 0:
                glow_color = QColor(150, 100, 255, glow_alpha)
                painter.setPen(glow_color)
                painter.setFont(QFont("Arial", 56 + i * 2, QFont.Weight.Bold))
                painter.drawText(0, title_y - i, self.width(), 100,
                               Qt.AlignmentFlag.AlignCenter, "DUNGEON DELVER")

        # Main title
        title_brightness = int(200 + self.title_pulse * 55)
        title_color = QColor(title_brightness, int(title_brightness * 0.7), 255)
        painter.setPen(title_color)
        painter.setFont(QFont("Arial", 56, QFont.Weight.Bold))
        painter.drawText(0, title_y, self.width(), 100,
                        Qt.AlignmentFlag.AlignCenter, "DUNGEON DELVER")

        # Subtitle
        subtitle_y = title_y + 90
        painter.setPen(QColor(150, 150, 160))
        painter.setFont(QFont("Arial", 18, QFont.Weight.Normal))
        painter.drawText(0, subtitle_y, self.width(), 30,
                        Qt.AlignmentFlag.AlignCenter, "A Roguelike Adventure")

        # "Press Any Key" prompt with fade
        prompt_y = self.height() - 150
        prompt_alpha = int(150 + self.prompt_fade * 105)
        prompt_color = QColor(200, 200, 210, prompt_alpha)
        painter.setPen(prompt_color)
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(0, prompt_y, self.width(), 40,
                        Qt.AlignmentFlag.AlignCenter, "Press Any Key to Continue")

        # Version info
        painter.setPen(QColor(100, 100, 110))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, self.height() - 20, "v1.0.0")

    def keyPressEvent(self, event):
        """Handle any key press to continue"""
        audio = get_audio_manager()
        audio.play_ui_select()
        self.continue_pressed.emit()
