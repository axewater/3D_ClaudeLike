"""
Warrior class renderer - Simple armored fighter with sword
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_warrior(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw warrior with simple armor and sword"""
    # Simple breathing animation
    breathing = math.sin(idle_time * 1.2) * 3
    sway = math.sin(idle_time * 0.8) * 2

    # Legs
    leg_color = QColor(80, 70, 60)
    painter.setBrush(leg_color)
    painter.setPen(QPen(leg_color.darker(120), 2))
    # Left leg
    painter.drawRect(center_x - tile_size // 6, center_y + tile_size // 12,
                    tile_size // 8, tile_size // 4)
    # Right leg
    painter.drawRect(center_x + tile_size // 12, center_y + tile_size // 12,
                    tile_size // 8, tile_size // 4)

    # Body/torso with armor
    body_gradient = QLinearGradient(center_x - tile_size // 4, center_y - tile_size // 8,
                                    center_x + tile_size // 4, center_y + tile_size // 10)
    body_gradient.setColorAt(0, color.lighter(110))
    body_gradient.setColorAt(0.5, color)
    body_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(body_gradient)
    painter.setPen(QPen(color.darker(140), 2))
    painter.drawEllipse(center_x - tile_size // 4, center_y - tile_size // 8 + int(breathing),
                       tile_size // 2, tile_size // 3)

    # Belt
    painter.setBrush(QColor(60, 50, 40))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(center_x - tile_size // 4, center_y + tile_size // 12,
                    tile_size // 2, tile_size // 15)

    # Left arm
    arm_color = color.darker(110)
    painter.setBrush(arm_color)
    painter.setPen(QPen(arm_color.darker(120), 1))
    painter.drawEllipse(center_x - tile_size // 3, center_y - tile_size // 20,
                       tile_size // 8, tile_size // 4)

    # Right arm (holding sword)
    painter.drawEllipse(center_x + tile_size // 5, center_y - tile_size // 20,
                       tile_size // 8, tile_size // 4)

    # Sword (longsword)
    sword_x = center_x + tile_size // 4 + int(sway)
    sword_y = center_y

    # Blade (longer and wider)
    blade_gradient = QLinearGradient(sword_x, sword_y - tile_size // 2, sword_x + 2, sword_y + tile_size // 8)
    blade_gradient.setColorAt(0, QColor(200, 200, 210))
    blade_gradient.setColorAt(0.5, QColor(160, 160, 170))
    blade_gradient.setColorAt(1, QColor(140, 140, 150))
    painter.setBrush(blade_gradient)
    painter.setPen(QPen(QColor(120, 120, 130), 2))

    blade_points = [
        QPoint(sword_x, sword_y - tile_size // 2),  # Tip
        QPoint(sword_x - tile_size // 16, sword_y + tile_size // 10),  # Left edge
        QPoint(sword_x + tile_size // 16, sword_y + tile_size // 10),  # Right edge
    ]
    painter.drawPolygon(blade_points)

    # Hilt
    painter.setBrush(QColor(100, 80, 50))
    painter.drawRect(sword_x - tile_size // 20, sword_y + tile_size // 10,
                    tile_size // 10, tile_size // 8)

    # Guard (crossguard)
    painter.drawRect(sword_x - tile_size // 8, sword_y + tile_size // 10,
                    tile_size // 4, tile_size // 25)

    # Head
    head_gradient = QRadialGradient(center_x, center_y - tile_size // 4, tile_size // 6)
    head_color = QColor(200, 160, 130)
    head_gradient.setColorAt(0, head_color.lighter(110))
    head_gradient.setColorAt(1, head_color)
    painter.setBrush(head_gradient)
    painter.setPen(QPen(head_color.darker(120), 2))
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 3,
                       tile_size // 3, tile_size // 3)

    # Metal helmet
    metal_color = QColor(140, 140, 150)

    # Helmet base (covers top of head)
    helmet_gradient = QLinearGradient(center_x - tile_size // 6, center_y - tile_size // 2,
                                     center_x + tile_size // 6, center_y - tile_size // 6)
    helmet_gradient.setColorAt(0, metal_color.darker(110))
    helmet_gradient.setColorAt(0.5, metal_color.lighter(120))
    helmet_gradient.setColorAt(1, metal_color.darker(110))
    painter.setBrush(helmet_gradient)
    painter.setPen(QPen(metal_color.darker(140), 2))

    # Helmet top (rounded rectangle)
    painter.drawRect(center_x - tile_size // 6, center_y - tile_size // 2 + tile_size // 20,
                    tile_size // 3, tile_size // 5)

    # Helmet sides (cheek guards)
    painter.drawRect(center_x - tile_size // 6, center_y - tile_size // 4,
                    tile_size // 20, tile_size // 12)
    painter.drawRect(center_x + tile_size // 6 - tile_size // 20, center_y - tile_size // 4,
                    tile_size // 20, tile_size // 12)

    # Visor slit (horizontal)
    painter.setBrush(QColor(20, 20, 20))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(center_x - tile_size // 8, center_y - tile_size // 5,
                    tile_size // 4, tile_size // 30)

    # Nose guard (vertical center piece)
    painter.setBrush(metal_color)
    painter.setPen(QPen(metal_color.darker(130), 1))
    painter.drawRect(center_x - tile_size // 40, center_y - tile_size // 4,
                    tile_size // 20, tile_size // 8)
