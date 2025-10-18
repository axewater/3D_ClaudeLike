"""
Demon enemy renderer - Horned Fiend with dark aura
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint, QRect
import math


def draw_demon(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw demon with menacing, supernatural idle animations"""
    # Idle animations - Menacing, supernatural movements
    wing_beat = math.sin(idle_time * 1.5) * 6  # Wing flapping
    tail_lash = math.sin(idle_time * 2.0) * 8  # Aggressive tail movement
    aura_pulse = abs(math.sin(idle_time * 1.2))  # Dark energy pulse
    eye_glow = int(abs(math.sin(idle_time * 3.0)) * 80)  # Eye intensity
    claw_flex = abs(math.sin(idle_time * 1.8)) * 2  # Claw opening/closing

    # Dark aura (behind body)
    for ring in range(3):
        ring_radius = tile_size // 3 + ring * 8 + int(aura_pulse * 10)
        aura_alpha = int(40 * (1.0 - ring / 3) * aura_pulse)
        aura_gradient = QRadialGradient(center_x, center_y, ring_radius)
        aura_gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), aura_alpha))
        aura_gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(aura_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - ring_radius, center_y - ring_radius,
                           ring_radius * 2, ring_radius * 2)

    # Bat wings (behind body, spread wide)
    wing_gradient = QLinearGradient(center_x - tile_size // 3, center_y,
                                    center_x - tile_size // 6, center_y + tile_size // 6)
    wing_gradient.setColorAt(0, color.darker(140))
    wing_gradient.setColorAt(0.5, color.darker(110))
    wing_gradient.setColorAt(1, color.darker(130))
    painter.setBrush(wing_gradient)
    painter.setPen(QPen(color.darker(170), 2))

    # Left wing with beat
    left_wing_offset = int(wing_beat)
    left_wing = [
        QPoint(center_x - tile_size // 8, center_y),
        QPoint(center_x - tile_size // 3, center_y - tile_size // 6 - left_wing_offset),
        QPoint(center_x - tile_size // 4, center_y - tile_size // 12),
        QPoint(center_x - tile_size // 6, center_y + tile_size // 12),
    ]
    painter.drawPolygon(left_wing)

    # Right wing with beat
    right_wing = [
        QPoint(center_x + tile_size // 8, center_y),
        QPoint(center_x + tile_size // 3, center_y - tile_size // 6 - left_wing_offset),
        QPoint(center_x + tile_size // 4, center_y - tile_size // 12),
        QPoint(center_x + tile_size // 6, center_y + tile_size // 12),
    ]
    painter.drawPolygon(right_wing)

    # Wing membranes (veins)
    painter.setPen(QPen(color.darker(180), 1))
    painter.drawLine(center_x - tile_size // 8, center_y,
                    center_x - tile_size // 3, center_y - tile_size // 6)
    painter.drawLine(center_x + tile_size // 8, center_y,
                    center_x + tile_size // 3, center_y - tile_size // 6)

    # Muscular torso (leaner than orc)
    torso_gradient = QRadialGradient(center_x, center_y, tile_size // 4)
    torso_gradient.setColorAt(0, color.lighter(120))
    torso_gradient.setColorAt(0.6, color)
    torso_gradient.setColorAt(1, color.darker(130))
    painter.setBrush(torso_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 12,
                       tile_size // 3, tile_size // 3)

    # Clawed arms (menacing pose)
    painter.setPen(QPen(color.darker(140), 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    # Left arm raised
    painter.drawLine(center_x - tile_size // 8, center_y,
                    center_x - tile_size // 4, center_y - tile_size // 8)
    # Right arm raised
    painter.drawLine(center_x + tile_size // 8, center_y,
                    center_x + tile_size // 4, center_y - tile_size // 8)

    # Sharp claws (both hands)
    painter.setPen(QPen(QColor(200, 200, 180), 2))
    for hand_x in [center_x - tile_size // 4, center_x + tile_size // 4]:
        hand_y = center_y - tile_size // 8
        for i in range(3):
            claw_offset = (i - 1) * 3
            painter.drawLine(hand_x + claw_offset, hand_y,
                           hand_x + claw_offset + int(claw_flex), hand_y - 5)

    # Barbed tail (behind, curling)
    tail_x = center_x + int(tail_lash)
    tail_gradient = QLinearGradient(center_x, center_y + tile_size // 6,
                                    tail_x, center_y + tile_size // 3)
    tail_gradient.setColorAt(0, color)
    tail_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(tail_gradient)
    painter.setPen(QPen(color.darker(150), 3))
    # Tail curve
    tail_points = [
        QPoint(center_x, center_y + tile_size // 6),
        QPoint(center_x + int(tail_lash * 0.5), center_y + tile_size // 4),
        QPoint(tail_x, center_y + tile_size // 3),
    ]
    for i in range(len(tail_points) - 1):
        painter.drawLine(tail_points[i], tail_points[i + 1])

    # Tail barb (spear tip)
    painter.setBrush(QColor(180, 60, 80))
    painter.setPen(QPen(QColor(140, 40, 60), 2))
    barb = [
        QPoint(tail_x, center_y + tile_size // 3),
        QPoint(tail_x - 4, center_y + tile_size // 3 + 6),
        QPoint(tail_x + 4, center_y + tile_size // 3 + 6),
    ]
    painter.drawPolygon(barb)

    # Demonic head (angular and sinister)
    head_gradient = QRadialGradient(center_x, center_y - tile_size // 4, tile_size // 5)
    head_gradient.setColorAt(0, color.lighter(125))
    head_gradient.setColorAt(0.7, color)
    head_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(head_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size * 2 // 5,
                       tile_size // 3, tile_size // 3)

    # Curved horns
    painter.setBrush(QColor(60, 40, 50))
    painter.setPen(QPen(QColor(40, 20, 30), 2))
    # Left horn
    left_horn = [
        QPoint(center_x - tile_size // 8, center_y - tile_size // 3),
        QPoint(center_x - tile_size // 5, center_y - tile_size // 2),
        QPoint(center_x - tile_size // 7, center_y - tile_size * 2 // 5),
    ]
    painter.drawPolygon(left_horn)
    # Right horn
    right_horn = [
        QPoint(center_x + tile_size // 8, center_y - tile_size // 3),
        QPoint(center_x + tile_size // 5, center_y - tile_size // 2),
        QPoint(center_x + tile_size // 7, center_y - tile_size * 2 // 5),
    ]
    painter.drawPolygon(right_horn)

    # Horn ridges
    painter.setPen(QPen(QColor(80, 60, 70), 1))
    for i in range(2):
        painter.drawLine(center_x - tile_size // 8, center_y - tile_size // 3 - i * 4,
                       center_x - tile_size // 6, center_y - tile_size * 2 // 5 - i * 4)
        painter.drawLine(center_x + tile_size // 8, center_y - tile_size // 3 - i * 4,
                       center_x + tile_size // 6, center_y - tile_size * 2 // 5 - i * 4)

    # Glowing red eyes
    eye_brightness = 200 + eye_glow
    eye_gradient = QRadialGradient(center_x - tile_size // 12, center_y - tile_size // 4, 6)
    eye_gradient.setColorAt(0, QColor(255, eye_brightness, 100))
    eye_gradient.setColorAt(0.5, QColor(255, 100, 0))
    eye_gradient.setColorAt(1, QColor(200, 50, 0, 0))
    painter.setBrush(eye_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 10, center_y - tile_size // 4,
                       7, 8)
    painter.drawEllipse(center_x + tile_size // 20, center_y - tile_size // 4,
                       7, 8)

    # Evil grin with fangs
    painter.setPen(QPen(QColor(0, 0, 0, 200), 2))
    painter.setBrush(QColor(40, 10, 20))
    mouth_rect = QRect(center_x - tile_size // 10, center_y - tile_size // 12,
                      tile_size // 5, tile_size // 12)
    painter.drawArc(mouth_rect, 0, -180 * 16)
    # Fangs
    painter.setPen(QPen(QColor(240, 240, 220), 1))
    for i in [0, 3]:
        fang_x = center_x - tile_size // 12 + i * 6
        painter.drawLine(fang_x, center_y - tile_size // 12,
                       fang_x, center_y - tile_size // 20)
