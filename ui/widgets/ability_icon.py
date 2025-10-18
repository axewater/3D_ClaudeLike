"""
Circular graphical ability icon widget with visual effects
"""
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath

import constants as c
import graphics as gfx


class AbilityIcon(QWidget):
    """Beautiful circular ability icon with visual feedback"""
    ability_clicked = pyqtSignal(int)  # Emits ability index

    def __init__(self, ability_index: int):
        super().__init__()
        self.ability_index = ability_index
        self.ability_name = ""
        self.ability_description = ""
        self.is_ready = False
        self.current_cooldown = 0
        self.max_cooldown = 1

        # Visual states
        self.is_hovered = False
        self.is_pressed = False
        self.glow_phase = 0.0  # For pulsing animation

        # Setup widget
        self.setFixedSize(c.ABILITY_ICON_SIZE, c.ABILITY_ICON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        # Animation timer for glow pulse
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self._update_glow)
        self.glow_timer.start(50)  # 20 FPS for glow animation

    def _update_glow(self):
        """Update glow pulse animation"""
        if self.is_ready:
            self.glow_phase += 0.1
            if self.glow_phase > 6.28:  # 2 * pi
                self.glow_phase = 0
            self.update()

    def set_ability_state(self, name: str, description: str, is_ready: bool,
                         current_cooldown: int, max_cooldown: int):
        """Update ability state and appearance"""
        self.ability_name = name
        self.ability_description = description
        self.is_ready = is_ready
        self.current_cooldown = current_cooldown
        self.max_cooldown = max_cooldown
        self.update()

    def paintEvent(self, event):
        """Custom painting for circular icon"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 6

        # Background circle
        painter.setBrush(c.COLOR_SECTION_BG)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw ability-specific graphics
        painter.save()

        # Create circular clipping path for the icon graphics
        clip_path = QPainterPath()
        clip_path.addEllipse(center_x - radius + 3, center_y - radius + 3,
                            (radius - 3) * 2, (radius - 3) * 2)
        painter.setClipPath(clip_path)

        # Draw the ability icon based on name
        icon_size = int(radius * 1.6)
        if not self.is_ready:
            # Grayscale effect for cooldown - reduce saturation
            painter.setOpacity(0.4)

        self._draw_ability_graphic(painter, center_x, center_y, icon_size)
        painter.restore()

        # Cooldown overlay
        if not self.is_ready:
            self._draw_cooldown_overlay(painter, center_x, center_y, radius)

            # Cooldown number
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(painter.font())
            font = painter.font()
            font.setPixelSize(18)
            font.setBold(True)
            painter.setFont(font)

            cd_text = str(self.current_cooldown)
            painter.drawText(QRect(0, 0, self.width(), self.height()),
                           Qt.AlignmentFlag.AlignCenter, cd_text)

        # Border and glow
        if self.is_ready:
            # Pulsing glow when ready
            import math
            glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
            glow_color = QColor(c.COLOR_ABILITY_READY_GLOW.red(),
                               c.COLOR_ABILITY_READY_GLOW.green(),
                               c.COLOR_ABILITY_READY_GLOW.blue(),
                               int(150 * glow_intensity))

            # Outer glow
            for i in range(3):
                glow_radius = radius + 2 + i
                pen_width = 2 - i
                painter.setPen(QPen(glow_color, pen_width))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center_x - glow_radius, center_y - glow_radius,
                                   glow_radius * 2, glow_radius * 2)

            # Main border
            border_color = c.COLOR_ABILITY_READY_GLOW if self.is_hovered else c.COLOR_ABILITY_BORDER
            painter.setPen(QPen(border_color, 3))
        else:
            # Dim border when on cooldown
            painter.setPen(QPen(c.COLOR_ABILITY_BORDER.darker(150), 2))

        # Hover effect
        if self.is_hovered and self.is_ready:
            painter.setPen(QPen(c.COLOR_ABILITY_HOVER_BORDER, 3))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Press effect (scale down)
        if self.is_pressed:
            painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
            painter.drawEllipse(center_x - radius + 2, center_y - radius + 2,
                               (radius - 2) * 2, (radius - 2) * 2)

        # Hotkey badge in bottom-right
        self._draw_hotkey_badge(painter, center_x, center_y, radius)

    def _draw_ability_graphic(self, painter: QPainter, center_x: int, center_y: int, size: int):
        """Draw the ability-specific graphic"""
        # Map ability name to drawing function
        ability_graphics = {
            "Fireball": gfx.draw_ability_fireball,
            "Dash": gfx.draw_ability_dash,
            "Healing Touch": gfx.draw_ability_healing,
            "Frost Nova": gfx.draw_ability_frost,
            "Whirlwind": gfx.draw_ability_whirlwind,
            "Shadow Step": gfx.draw_ability_shadow,
        }

        draw_func = ability_graphics.get(self.ability_name)
        if draw_func:
            draw_func(painter, center_x, center_y, size)
        else:
            # Default: generic orb
            gradient = QRadialGradient(center_x, center_y, size // 2)
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(1, QColor(100, 100, 100))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - size // 2, center_y - size // 2, size, size)

    def _draw_cooldown_overlay(self, painter: QPainter, center_x: int, center_y: int, radius: int):
        """Draw pie-chart style cooldown indicator"""
        if self.max_cooldown <= 0:
            return

        # Dark overlay
        painter.setBrush(c.COLOR_ABILITY_COOLDOWN_OVERLAY)
        painter.setPen(Qt.PenStyle.NoPen)

        # Calculate cooldown percentage
        cooldown_percent = self.current_cooldown / self.max_cooldown

        # Draw pie slice showing cooldown remaining
        start_angle = 90 * 16  # Start at top (90 degrees)
        span_angle = -int(360 * 16 * cooldown_percent)  # Negative for clockwise

        painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2,
                       start_angle, span_angle)

    def _draw_hotkey_badge(self, painter: QPainter, center_x: int, center_y: int, radius: int):
        """Draw hotkey number badge in corner"""
        badge_size = 18
        badge_x = center_x + radius - badge_size // 2
        badge_y = center_y + radius - badge_size // 2

        # Badge background
        painter.setBrush(QColor(40, 40, 50, 220))
        painter.setPen(QPen(QColor(100, 100, 110), 1))
        painter.drawEllipse(badge_x - badge_size // 2, badge_y - badge_size // 2,
                           badge_size, badge_size)

        # Hotkey number
        painter.setPen(QColor(220, 220, 230))
        font = painter.font()
        font.setPixelSize(12)
        font.setBold(True)
        painter.setFont(font)

        hotkey = str(self.ability_index + 1)
        painter.drawText(QRect(badge_x - badge_size // 2, badge_y - badge_size // 2,
                              badge_size, badge_size),
                        Qt.AlignmentFlag.AlignCenter, hotkey)

    def enterEvent(self, event):
        """Mouse enters widget"""
        self.is_hovered = True
        self.update()

        # Show tooltip with ability info
        if self.ability_name:
            tooltip = (f"<div style='color: white; background-color: rgba(30, 30, 35, 240); "
                      f"padding: 4px; border: 1px solid #555;'>"
                      f"<b style='color: #ffd43b;'>{self.ability_name}</b><br/>"
                      f"<span style='color: #ddd;'>{self.ability_description}</span>")
            if not self.is_ready:
                tooltip += f"<br/><span style='color: #ff6b6b;'>Cooldown: {self.current_cooldown}</span>"
            tooltip += "</div>"
            QToolTip.showText(self.mapToGlobal(QPoint(0, -30)), tooltip, self)

    def leaveEvent(self, event):
        """Mouse leaves widget"""
        self.is_hovered = False
        self.update()
        QToolTip.hideText()

    def mousePressEvent(self, event):
        """Mouse button pressed"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.update()

    def mouseReleaseEvent(self, event):
        """Mouse button released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = False
            self.update()

            # Emit click signal if hovering
            if self.is_hovered:
                self.ability_clicked.emit(self.ability_index)
