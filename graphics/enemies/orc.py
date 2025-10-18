"""
Orc enemy renderer - Muscular Brute Warrior
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_orc(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw orc with heavy, powerful idle animations"""
    # Idle animations - Heavy, powerful movements
    breath_expansion = abs(math.sin(idle_time * 0.7)) * 3  # Chest breathing
    axe_sway = math.sin(idle_time * 1.0) * 5  # Axe weight sway
    muscle_flex = abs(math.sin(idle_time * 0.5)) * 2  # Muscle tension
    nostril_flare = int(abs(math.sin(idle_time * 0.8)) * 2)  # Angry breathing

    # Muscular torso (large and imposing)
    torso_gradient = QLinearGradient(center_x, center_y - tile_size // 12,
                                     center_x, center_y + tile_size // 4)
    torso_gradient.setColorAt(0, color.lighter(115))
    torso_gradient.setColorAt(0.5, color)
    torso_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(torso_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    torso_width = tile_size // 3 + int(breath_expansion)
    painter.drawEllipse(center_x - torso_width // 2, center_y - tile_size // 12,
                       torso_width, tile_size // 3)

    # Armor plates on shoulders
    armor_color = QColor(60, 50, 40)
    painter.setBrush(armor_color)
    painter.setPen(QPen(QColor(40, 30, 20), 2))
    # Left shoulder plate
    left_plate = [
        QPoint(center_x - tile_size // 4, center_y - tile_size // 12),
        QPoint(center_x - tile_size // 3, center_y - tile_size // 8),
        QPoint(center_x - tile_size // 4, center_y),
    ]
    painter.drawPolygon(left_plate)
    # Right shoulder plate
    right_plate = [
        QPoint(center_x + tile_size // 4, center_y - tile_size // 12),
        QPoint(center_x + tile_size // 3, center_y - tile_size // 8),
        QPoint(center_x + tile_size // 4, center_y),
    ]
    painter.drawPolygon(right_plate)

    # Spikes on armor
    painter.setBrush(QColor(80, 70, 60))
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(2):
        spike_x = center_x - tile_size // 3 + i * tile_size * 2 // 3
        spike = [
            QPoint(spike_x, center_y - tile_size // 8),
            QPoint(spike_x - 3, center_y - tile_size // 5),
            QPoint(spike_x + 3, center_y - tile_size // 5),
        ]
        painter.drawPolygon(spike)

    # Muscular arms
    painter.setPen(QPen(color.darker(130), 4))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    # Right arm (holding axe)
    painter.drawLine(center_x + tile_size // 6, center_y,
                    center_x + tile_size // 3, center_y - tile_size // 10)
    # Left arm
    painter.drawLine(center_x - tile_size // 6, center_y,
                    center_x - tile_size // 4, center_y + tile_size // 12)

    # Muscle definition lines
    painter.setPen(QPen(color.darker(160), 1))
    painter.drawLine(center_x + tile_size // 6, center_y,
                    center_x + tile_size // 5, center_y - tile_size // 20)

    # Large battle axe
    axe_x = center_x + tile_size // 3
    axe_y = center_y - tile_size // 10 + int(axe_sway)

    # Axe handle (wooden)
    painter.setBrush(QColor(80, 60, 40))
    painter.setPen(QPen(QColor(60, 40, 20), 2))
    painter.drawLine(axe_x, axe_y, axe_x - 2, axe_y - tile_size // 6)

    # Axe blade (metal)
    axe_gradient = QLinearGradient(axe_x, axe_y - tile_size // 6,
                                   axe_x + tile_size // 8, axe_y - tile_size // 6)
    axe_gradient.setColorAt(0, QColor(140, 140, 140))
    axe_gradient.setColorAt(0.5, QColor(180, 180, 180))
    axe_gradient.setColorAt(1, QColor(120, 120, 120))
    painter.setBrush(axe_gradient)
    painter.setPen(QPen(QColor(80, 80, 80), 2))
    axe_blade = [
        QPoint(axe_x - 2, axe_y - tile_size // 6),
        QPoint(axe_x + tile_size // 8, axe_y - tile_size // 5),
        QPoint(axe_x + tile_size // 7, axe_y - tile_size // 6 + 4),
        QPoint(axe_x - 2, axe_y - tile_size // 6 + 2),
    ]
    painter.drawPolygon(axe_blade)

    # Large orc head
    head_gradient = QRadialGradient(center_x, center_y - tile_size // 4, tile_size // 4)
    head_gradient.setColorAt(0, color.lighter(120))
    head_gradient.setColorAt(0.7, color)
    head_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(head_gradient)
    painter.setPen(QPen(color.darker(140), 2))
    painter.drawEllipse(center_x - tile_size // 5, center_y - tile_size * 2 // 5,
                       tile_size * 2 // 5, tile_size // 3)

    # War paint stripes
    painter.setPen(QPen(QColor(180, 40, 40), 2))
    for i in range(2):
        paint_y = center_y - tile_size // 3 + i * tile_size // 12
        painter.drawLine(center_x - tile_size // 6, paint_y,
                       center_x + tile_size // 6, paint_y)

    # Prominent tusks
    painter.setBrush(QColor(220, 220, 200))
    painter.setPen(QPen(QColor(180, 180, 160), 2))
    # Left tusk
    left_tusk = [
        QPoint(center_x - tile_size // 10, center_y - tile_size // 8),
        QPoint(center_x - tile_size // 8, center_y - tile_size // 6),
        QPoint(center_x - tile_size // 12, center_y - tile_size // 12),
    ]
    painter.drawPolygon(left_tusk)
    # Right tusk
    right_tusk = [
        QPoint(center_x + tile_size // 10, center_y - tile_size // 8),
        QPoint(center_x + tile_size // 8, center_y - tile_size // 6),
        QPoint(center_x + tile_size // 12, center_y - tile_size // 12),
    ]
    painter.drawPolygon(right_tusk)

    # Fierce eyes
    painter.setBrush(QColor(255, 220, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 10, center_y - tile_size // 4,
                       6, 7)
    painter.drawEllipse(center_x + tile_size // 20, center_y - tile_size // 4,
                       6, 7)
    # Pupils
    painter.setBrush(QColor(0, 0, 0))
    painter.drawEllipse(center_x - tile_size // 10 + 2, center_y - tile_size // 4 + 2,
                       3, 4)
    painter.drawEllipse(center_x + tile_size // 20 + 2, center_y - tile_size // 4 + 2,
                       3, 4)

    # Angry brow ridge
    painter.setPen(QPen(color.darker(160), 2))
    painter.drawLine(center_x - tile_size // 8, center_y - tile_size // 3,
                    center_x - tile_size // 12, center_y - tile_size // 4)
    painter.drawLine(center_x + tile_size // 8, center_y - tile_size // 3,
                    center_x + tile_size // 12, center_y - tile_size // 4)

    # Flared nostrils
    painter.setBrush(QColor(0, 0, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    nostril_size = 3 + nostril_flare
    painter.drawEllipse(center_x - tile_size // 16, center_y - tile_size // 7,
                       nostril_size, 4)
    painter.drawEllipse(center_x + tile_size // 32, center_y - tile_size // 7,
                       nostril_size, 4)
