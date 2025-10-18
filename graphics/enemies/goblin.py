"""
Goblin enemy renderer - Wicked Trickster with hunched posture
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint, QRect
import math


def draw_goblin(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw goblin with fast, twitchy idle animations"""
    # Idle animations - Fast, twitchy, nervous
    ear_twitch = math.sin(idle_time * 8.0) * 3  # Rapid ear movement
    head_dart = math.sin(idle_time * 3.5) * 4  # Nervous head darting
    eye_flicker = int(abs(math.sin(idle_time * 6.0)) * 40)  # Eye intensity flicker
    posture_shift = math.sin(idle_time * 2.2) * 2  # Jittery body movement
    teeth_chatter = int(abs(math.sin(idle_time * 10.0)))  # Rapid teeth movement

    # Hunched body (smaller, lower)
    body_gradient = QLinearGradient(center_x, center_y,
                                    center_x, center_y + tile_size // 3)
    body_gradient.setColorAt(0, color.lighter(110))
    body_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(body_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x - tile_size // 6, center_y + tile_size // 12,
                       tile_size // 3, tile_size // 4)

    # Tattered loincloth
    loincloth_color = color.darker(140)
    painter.setBrush(loincloth_color)
    painter.setPen(Qt.PenStyle.NoPen)
    loincloth = [
        QPoint(center_x - tile_size // 8, center_y + tile_size // 8),
        QPoint(center_x - tile_size // 6, center_y + tile_size // 3),
        QPoint(center_x - tile_size // 12, center_y + tile_size // 3 - 2),
        QPoint(center_x, center_y + tile_size // 4),
        QPoint(center_x + tile_size // 12, center_y + tile_size // 3 - 2),
        QPoint(center_x + tile_size // 6, center_y + tile_size // 3),
        QPoint(center_x + tile_size // 8, center_y + tile_size // 8),
    ]
    painter.drawPolygon(loincloth)

    # Hunched oversized head
    head_gradient = QRadialGradient(center_x, center_y - tile_size // 8, tile_size // 3)
    head_gradient.setColorAt(0, color.lighter(120))
    head_gradient.setColorAt(0.7, color)
    head_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(head_gradient)
    painter.setPen(QPen(color.darker(140), 2))
    painter.drawEllipse(center_x - tile_size // 4, center_y - tile_size // 3,
                       tile_size // 2, tile_size * 2 // 5)

    # Warty skin details (dark spots)
    painter.setBrush(color.darker(180))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 6, 3, 3)
    painter.drawEllipse(center_x + tile_size // 8, center_y - tile_size // 5, 2, 2)
    painter.drawEllipse(center_x - tile_size // 12, center_y - tile_size // 8, 2, 2)

    # Large bat-like ears (signature feature) with twitch
    ear_color = color.darker(110)
    painter.setBrush(ear_color)
    painter.setPen(QPen(color.darker(150), 1))
    ear_offset = int(ear_twitch)
    # Left ear
    left_ear = [
        QPoint(center_x - tile_size // 5 + int(head_dart), center_y - tile_size // 4 + int(posture_shift)),
        QPoint(center_x - tile_size // 3 + int(head_dart) + ear_offset, center_y - tile_size // 3 + int(posture_shift) - ear_offset),
        QPoint(center_x - tile_size // 4 + int(head_dart), center_y - tile_size // 6 + int(posture_shift)),
    ]
    painter.drawPolygon(left_ear)
    # Right ear
    right_ear = [
        QPoint(center_x + tile_size // 5 + int(head_dart), center_y - tile_size // 4 + int(posture_shift)),
        QPoint(center_x + tile_size // 3 + int(head_dart) - ear_offset, center_y - tile_size // 3 + int(posture_shift) - ear_offset),
        QPoint(center_x + tile_size // 4 + int(head_dart), center_y - tile_size // 6 + int(posture_shift)),
    ]
    painter.drawPolygon(right_ear)

    # Inner ear detail
    painter.setBrush(color.darker(140))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 4, center_y - tile_size // 5, 4, 6)
    painter.drawEllipse(center_x + tile_size // 5, center_y - tile_size // 5, 4, 6)

    # Crude weapon (club in right hand/arm)
    painter.setBrush(QColor(80, 60, 40))
    painter.setPen(QPen(QColor(60, 40, 20), 2))
    # Club handle
    painter.drawLine(center_x + tile_size // 5, center_y,
                    center_x + tile_size // 3, center_y - tile_size // 6)
    # Club head
    painter.drawEllipse(center_x + tile_size // 3 - 4, center_y - tile_size // 5,
                       8, 8)

    # Clawed left arm/hand
    painter.setPen(QPen(color.darker(130), 2))
    painter.drawLine(center_x - tile_size // 6, center_y,
                    center_x - tile_size // 4, center_y + tile_size // 12)
    # Claws
    painter.setPen(QPen(QColor(100, 100, 80), 1))
    for i in range(3):
        claw_x = center_x - tile_size // 4 + i * 2
        claw_y = center_y + tile_size // 12
        painter.drawLine(claw_x, claw_y, claw_x - 1, claw_y + 3)

    # Wicked grin with sharp teeth
    painter.setPen(QPen(QColor(0, 0, 0, 200), 2))
    painter.setBrush(QColor(40, 20, 20))
    # Mouth
    mouth_rect = QRect(center_x - tile_size // 8, center_y - tile_size // 20,
                      tile_size // 4, tile_size // 12)
    painter.drawArc(mouth_rect, 0, -180 * 16)  # Evil grin arc
    # Sharp teeth
    painter.setPen(QPen(QColor(220, 220, 200), 1))
    for i in range(5):
        tooth_x = center_x - tile_size // 10 + i * 4
        painter.drawLine(tooth_x, center_y - tile_size // 20,
                       tooth_x, center_y + tile_size // 30)

    # Glowing yellow menacing eyes with flicker
    eye_brightness = 230 - eye_flicker
    painter.setBrush(QColor(255, eye_brightness, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 10 + int(head_dart), center_y - tile_size // 8 + int(posture_shift), 5, 6)
    painter.drawEllipse(center_x + tile_size // 10 - 5 + int(head_dart), center_y - tile_size // 8 + int(posture_shift), 5, 6)
    # Eye glow with flicker
    glow_alpha = 180 - eye_flicker
    eye_glow = QRadialGradient(center_x - tile_size // 12 + int(head_dart), center_y - tile_size // 9 + int(posture_shift), 4)
    eye_glow.setColorAt(0, QColor(255, 255, 150, glow_alpha))
    eye_glow.setColorAt(1, QColor(255, eye_brightness, 0, 0))
    painter.setBrush(eye_glow)
    painter.drawEllipse(center_x - tile_size // 10 - 3 + int(head_dart), center_y - tile_size // 8 - 3 + int(posture_shift), 11, 12)
    eye_glow.setCenter(center_x + tile_size // 12 + int(head_dart), center_y - tile_size // 9 + int(posture_shift))
    painter.setBrush(eye_glow)
    painter.drawEllipse(center_x + tile_size // 10 - 8 + int(head_dart), center_y - tile_size // 8 - 3 + int(posture_shift), 11, 12)
