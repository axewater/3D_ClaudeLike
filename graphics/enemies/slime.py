"""
Slime enemy renderer - Gelatinous Blob with translucent body
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_slime(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw slime with pulsing, organic idle animations"""
    # Idle animations - Pulsing, organic movements
    body_pulse = math.sin(idle_time * 1.2) * 4  # Body size pulsing
    nucleus_drift_x = math.sin(idle_time * 0.8) * 3  # Nucleus floating
    nucleus_drift_y = math.cos(idle_time * 0.6) * 2
    bubble_float = idle_time * 20  # Bubbles rising
    membrane_ripple = abs(math.sin(idle_time * 2.0)) * 2  # Surface tension

    # Main gelatinous body (translucent)
    body_size = tile_size // 2 + int(body_pulse)
    body_gradient = QRadialGradient(center_x, center_y, body_size)
    body_gradient.setColorAt(0, color.lighter(130))
    body_gradient.setColorAt(0.5, color)
    body_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(body_gradient)
    painter.setPen(QPen(color.darker(140), 2))
    painter.drawEllipse(center_x - body_size // 2, center_y - body_size // 2,
                       body_size, body_size)

    # Inner translucent layer
    inner_size = int(body_size * 0.7)
    inner_gradient = QRadialGradient(center_x, center_y, inner_size)
    inner_gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100))
    inner_gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 30))
    painter.setBrush(inner_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - inner_size // 2, center_y - inner_size // 2,
                       inner_size, inner_size)

    # Nucleus core (glowing center)
    nucleus_x = center_x + int(nucleus_drift_x)
    nucleus_y = center_y + int(nucleus_drift_y)
    nucleus_gradient = QRadialGradient(nucleus_x, nucleus_y, tile_size // 6)
    nucleus_gradient.setColorAt(0, QColor(150, 255, 220, 220))
    nucleus_gradient.setColorAt(0.6, color.lighter(150))
    nucleus_gradient.setColorAt(1, color)
    painter.setBrush(nucleus_gradient)
    painter.setPen(QPen(QColor(100, 200, 180), 1))
    painter.drawEllipse(nucleus_x - tile_size // 8, nucleus_y - tile_size // 8,
                       tile_size // 4, tile_size // 4)

    # Nucleus detail (inner darker spot)
    painter.setBrush(QColor(60, 150, 130))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(nucleus_x - tile_size // 16, nucleus_y - tile_size // 16,
                       tile_size // 8, tile_size // 8)

    # Surface bubbles (floating upward)
    painter.setBrush(QColor(200, 255, 240, 120))
    painter.setPen(QPen(QColor(150, 220, 200, 180), 1))
    for i in range(4):
        bubble_phase = (bubble_float + i * 50) % 100
        bubble_x = center_x + int(math.sin(i * 1.5 + idle_time) * tile_size // 4)
        bubble_y = center_y + tile_size // 4 - int(bubble_phase * tile_size // 100)
        bubble_size = 3 + int(bubble_phase / 25)  # Bubbles grow as they rise
        if bubble_y > center_y - body_size // 2:  # Only show bubbles inside body
            painter.drawEllipse(bubble_x - bubble_size // 2, bubble_y - bubble_size // 2,
                               bubble_size, bubble_size)

    # Pseudopod tendrils at base (3 reaching down)
    painter.setBrush(color.darker(110))
    painter.setPen(QPen(color.darker(140), 2))
    for i in range(-1, 2):
        tendril_x_offset = i * tile_size // 6
        tendril_sway = math.sin(idle_time * 1.5 + i) * 3
        tendril_points = [
            QPoint(center_x + tendril_x_offset, center_y + body_size // 3),
            QPoint(center_x + tendril_x_offset + int(tendril_sway), center_y + body_size // 2),
            QPoint(center_x + tendril_x_offset + int(tendril_sway * 1.5), center_y + body_size // 2 + 4),
        ]
        for j in range(len(tendril_points) - 1):
            painter.drawLine(tendril_points[j], tendril_points[j + 1])

    # Outer membrane ripple effect
    ripple_alpha = 80 + int(membrane_ripple * 20)
    painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), ripple_alpha), 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center_x - body_size // 2 - 2, center_y - body_size // 2 - 2,
                       body_size + 4, body_size + 4)
