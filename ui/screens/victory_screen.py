"""
Victory screen shown when player completes all 25 levels
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont
import time
import math

from audio import get_audio_manager
from animations import AnimationManager


class VictoryScreen(QWidget):
    """Animated victory screen with celebration effects"""
    return_to_menu = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: rgb(15, 10, 25);")

        # Animation manager for particles
        self.anim_manager = AnimationManager()
        self.time_elapsed = 0.0
        self.last_time = time.time()

        # Pulse animation for title
        self.title_pulse = 0.0

        # Fade animation for prompt
        self.prompt_fade = 0.0

        # Timer for animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Spawn initial celebration particles
        for _ in range(50):
            self.anim_manager.add_ambient_particles(count=1)

    def update_animation(self):
        """Update animations"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        self.time_elapsed += dt

        # Update animations
        self.anim_manager.update(dt)

        # Spawn celebration particles periodically
        if len(self.anim_manager.ambient_particles) < 80:
            self.anim_manager.add_ambient_particles(count=3)

        # Update pulse animation (faster pulse for victory)
        self.title_pulse = math.sin(self.time_elapsed * 3.0) * 0.5 + 0.5

        # Update prompt fade
        self.prompt_fade = math.sin(self.time_elapsed * 4.0) * 0.5 + 0.5

        self.update()

    def paintEvent(self, event):
        """Paint the victory screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background gradient (golden/purple theme)
        for y in range(self.height()):
            progress = y / self.height()
            r = int(15 + progress * 30)
            g = int(10 + progress * 20)
            b = int(25 + progress * 50)
            painter.setPen(QColor(r, g, b))
            painter.drawLine(0, y, self.width(), y)

        # Draw celebration particles (golden and purple)
        for particle in self.anim_manager.ambient_particles:
            # Override particle color for victory theme
            hue_shift = int(self.time_elapsed * 50 + particle.x)
            if hue_shift % 3 == 0:
                color = QColor(255, 215, 0, particle.alpha)  # Gold
            elif hue_shift % 3 == 1:
                color = QColor(180, 100, 255, particle.alpha)  # Purple
            else:
                color = QColor(255, 150, 200, particle.alpha)  # Pink

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(particle.x - particle.size / 2),
                              int(particle.y - particle.size / 2),
                              int(particle.size), int(particle.size))

        # Draw glowing "VICTORY!" title
        title_y = self.height() // 3

        # Glow effect (multiple layers)
        glow_intensity = int(self.title_pulse * 150)
        for i in range(8, 0, -1):
            glow_alpha = glow_intensity - (i * 15)
            if glow_alpha > 0:
                glow_color = QColor(255, 215, 0, glow_alpha)
                painter.setPen(glow_color)
                painter.setFont(QFont("Arial", 72 + i * 2, QFont.Weight.Bold))
                painter.drawText(0, title_y - i, self.width(), 120,
                               Qt.AlignmentFlag.AlignCenter, "VICTORY!")

        # Main title
        title_brightness = int(220 + self.title_pulse * 35)
        title_color = QColor(255, title_brightness, int(title_brightness * 0.6))
        painter.setPen(title_color)
        painter.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        painter.drawText(0, title_y, self.width(), 120,
                        Qt.AlignmentFlag.AlignCenter, "VICTORY!")

        # Subtitle
        subtitle_y = title_y + 100
        painter.setPen(QColor(200, 180, 220))
        painter.setFont(QFont("Arial", 22, QFont.Weight.Normal))
        painter.drawText(0, subtitle_y, self.width(), 40,
                        Qt.AlignmentFlag.AlignCenter, "You have conquered all 25 levels!")

        # Congratulations message
        congrats_y = subtitle_y + 60
        painter.setPen(QColor(180, 160, 200))
        painter.setFont(QFont("Arial", 18, QFont.Weight.Normal))
        painter.drawText(0, congrats_y, self.width(), 30,
                        Qt.AlignmentFlag.AlignCenter, "The dungeon has been conquered!")

        stats_y = congrats_y + 80
        painter.setPen(QColor(160, 140, 180))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(0, stats_y, self.width(), 25,
                        Qt.AlignmentFlag.AlignCenter, "All enemies defeated")
        painter.drawText(0, stats_y + 30, self.width(), 25,
                        Qt.AlignmentFlag.AlignCenter, "All biomes explored")

        # "Press Any Key" prompt with fade
        prompt_y = self.height() - 120
        prompt_alpha = int(180 + self.prompt_fade * 75)
        prompt_color = QColor(255, 215, 0, prompt_alpha)
        painter.setPen(prompt_color)
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(0, prompt_y, self.width(), 40,
                        Qt.AlignmentFlag.AlignCenter, "Press Any Key to Return to Menu")

        # Credits
        painter.setPen(QColor(100, 90, 110))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, self.height() - 20, "Claude-Like - A Roguelike Adventure")

    def keyPressEvent(self, event):
        """Handle any key press to return to menu"""
        audio = get_audio_manager()
        audio.play_ui_select()
        self.return_to_menu.emit()
