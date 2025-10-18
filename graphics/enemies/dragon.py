"""
Dragon enemy renderer - Ancient Wyrm (larger, more imposing)
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_dragon(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw dragon with slow, majestic idle animations (1.3x scale)"""
    scale_factor = 1.3

    # Idle animations - Slow, majestic, powerful
    wing_flutter = math.sin(idle_time * 0.8) * 8  # Slow wing movement
    tail_sway = math.sin(idle_time * 0.6) * 10  # Tail drift
    breath_pulse = int(abs(math.sin(idle_time * 1.5)) * 60)  # Fire glow pulse
    smoke_intensity = abs(math.sin(idle_time * 1.0))  # Smoke wisp pulse
    body_breathing = math.sin(idle_time * 0.5) * 3  # Deep breathing

    # Detailed wings with membrane veins (behind body)
    wing_gradient = QLinearGradient(center_x - int(tile_size * 0.5 * scale_factor),
                                    center_y - int(tile_size * 0.3 * scale_factor),
                                    center_x - int(tile_size * 0.2 * scale_factor),
                                    center_y + int(tile_size * 0.1 * scale_factor))
    wing_gradient.setColorAt(0, color.darker(130))
    wing_gradient.setColorAt(0.5, color.darker(110))
    wing_gradient.setColorAt(1, color.darker(140))
    painter.setBrush(wing_gradient)
    painter.setPen(QPen(color.darker(160), 2))

    # Left wing (spread) with flutter
    wing_offset = int(wing_flutter)
    left_wing = [
        QPoint(center_x - int(tile_size * 0.15 * scale_factor), center_y + int(body_breathing)),
        QPoint(center_x - int(tile_size * 0.5 * scale_factor) - wing_offset, center_y - int(tile_size * 0.35 * scale_factor) - wing_offset),
        QPoint(center_x - int(tile_size * 0.45 * scale_factor) - wing_offset // 2, center_y - int(tile_size * 0.15 * scale_factor)),
        QPoint(center_x - int(tile_size * 0.35 * scale_factor), center_y + int(tile_size * 0.1 * scale_factor) + int(body_breathing)),
    ]
    painter.drawPolygon(left_wing)

    # Right wing (spread) with flutter
    right_wing = [
        QPoint(center_x + int(tile_size * 0.15 * scale_factor), center_y + int(body_breathing)),
        QPoint(center_x + int(tile_size * 0.5 * scale_factor) + wing_offset, center_y - int(tile_size * 0.35 * scale_factor) - wing_offset),
        QPoint(center_x + int(tile_size * 0.45 * scale_factor) + wing_offset // 2, center_y - int(tile_size * 0.15 * scale_factor)),
        QPoint(center_x + int(tile_size * 0.35 * scale_factor), center_y + int(tile_size * 0.1 * scale_factor) + int(body_breathing)),
    ]
    painter.drawPolygon(right_wing)

    # Wing membrane veins
    painter.setPen(QPen(color.darker(180), 1))
    painter.drawLine(center_x - int(tile_size * 0.15 * scale_factor), center_y,
                    center_x - int(tile_size * 0.45 * scale_factor), center_y - int(tile_size * 0.25 * scale_factor))
    painter.drawLine(center_x + int(tile_size * 0.15 * scale_factor), center_y,
                    center_x + int(tile_size * 0.45 * scale_factor), center_y - int(tile_size * 0.25 * scale_factor))

    # Wing talons/claws
    painter.setPen(QPen(color.darker(170), 2))
    painter.drawLine(center_x - int(tile_size * 0.5 * scale_factor), center_y - int(tile_size * 0.35 * scale_factor),
                    center_x - int(tile_size * 0.52 * scale_factor), center_y - int(tile_size * 0.4 * scale_factor))
    painter.drawLine(center_x + int(tile_size * 0.5 * scale_factor), center_y - int(tile_size * 0.35 * scale_factor),
                    center_x + int(tile_size * 0.52 * scale_factor), center_y - int(tile_size * 0.4 * scale_factor))

    # Main body with scale gradient
    body_gradient = QLinearGradient(center_x, center_y - int(tile_size * 0.2 * scale_factor),
                                    center_x, center_y + int(tile_size * 0.25 * scale_factor))
    body_gradient.setColorAt(0, color.lighter(115))
    body_gradient.setColorAt(0.5, color)
    body_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(body_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x - int(tile_size * 0.25 * scale_factor),
                       center_y - int(tile_size * 0.15 * scale_factor),
                       int(tile_size * 0.5 * scale_factor),
                       int(tile_size * 0.4 * scale_factor))

    # Underbelly scales (lighter)
    underbelly_gradient = QLinearGradient(center_x, center_y,
                                          center_x, center_y + int(tile_size * 0.2 * scale_factor))
    underbelly_gradient.setColorAt(0, color.lighter(140))
    underbelly_gradient.setColorAt(1, color.lighter(120))
    painter.setBrush(underbelly_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - int(tile_size * 0.15 * scale_factor),
                       center_y - int(tile_size * 0.05 * scale_factor),
                       int(tile_size * 0.3 * scale_factor),
                       int(tile_size * 0.25 * scale_factor))

    # Scale pattern on body (diamond shapes)
    painter.setPen(QPen(color.darker(140), 1))
    for row in range(3):
        for col in range(4):
            scale_x = center_x - int(tile_size * 0.15 * scale_factor) + col * int(8 * scale_factor)
            scale_y = center_y - int(tile_size * 0.08 * scale_factor) + row * int(6 * scale_factor)
            offset = (row % 2) * int(4 * scale_factor)
            scale_diamond = [
                QPoint(scale_x + offset, scale_y - 2),
                QPoint(scale_x + offset + 3, scale_y),
                QPoint(scale_x + offset, scale_y + 2),
                QPoint(scale_x + offset - 3, scale_y),
            ]
            painter.drawPolygon(scale_diamond)

    # Spined tail with barbs and sway
    painter.setPen(QPen(color.darker(130), 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    # Tail curve with sway
    tail_sway_offset = int(tail_sway)
    tail_end_x = center_x - int(tile_size * 0.4 * scale_factor) + tail_sway_offset
    tail_end_y = center_y + int(tile_size * 0.3 * scale_factor)
    painter.drawLine(center_x - int(tile_size * 0.2 * scale_factor), center_y + int(tile_size * 0.15 * scale_factor) + int(body_breathing),
                    tail_end_x, tail_end_y)
    # Tail spikes with sway
    painter.setBrush(color.darker(140))
    painter.setPen(QPen(color.darker(170), 1))
    for i in range(3):
        spike_sway_amount = tail_sway_offset * (i + 1) // 3  # Progressive sway along tail
        spike_x = center_x - int(tile_size * 0.2 * scale_factor) - i * int(7 * scale_factor) + spike_sway_amount
        spike_y = center_y + int(tile_size * 0.15 * scale_factor) + i * int(5 * scale_factor) + int(body_breathing)
        spike = [
            QPoint(spike_x, spike_y),
            QPoint(spike_x - int(3 * scale_factor), spike_y - int(6 * scale_factor)),
            QPoint(spike_x + int(2 * scale_factor), spike_y - int(4 * scale_factor)),
        ]
        painter.drawPolygon(spike)

    # Serpentine neck
    neck_gradient = QLinearGradient(center_x + int(tile_size * 0.1 * scale_factor), center_y - int(tile_size * 0.1 * scale_factor),
                                    center_x + int(tile_size * 0.3 * scale_factor), center_y - int(tile_size * 0.35 * scale_factor))
    neck_gradient.setColorAt(0, color)
    neck_gradient.setColorAt(1, color.lighter(110))
    painter.setBrush(neck_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    # Neck segments (3 curved sections)
    for i in range(3):
        seg_x = center_x + int(tile_size * 0.15 * scale_factor) + i * int(6 * scale_factor)
        seg_y = center_y - int(tile_size * 0.15 * scale_factor) - i * int(8 * scale_factor)
        painter.drawEllipse(seg_x - int(5 * scale_factor), seg_y,
                           int(10 * scale_factor), int(8 * scale_factor))

    # Dragon head (detailed)
    head_gradient = QRadialGradient(center_x + int(tile_size * 0.32 * scale_factor),
                                    center_y - int(tile_size * 0.38 * scale_factor),
                                    int(tile_size * 0.18 * scale_factor))
    head_gradient.setColorAt(0, color.lighter(120))
    head_gradient.setColorAt(0.7, color)
    head_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(head_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x + int(tile_size * 0.22 * scale_factor),
                       center_y - int(tile_size * 0.45 * scale_factor),
                       int(tile_size * 0.2 * scale_factor),
                       int(tile_size * 0.15 * scale_factor))

    # Crown of horns on head
    painter.setBrush(color.darker(130))
    painter.setPen(QPen(color.darker(170), 2))
    for i in range(3):
        horn_x = center_x + int(tile_size * 0.24 * scale_factor) + i * int(4 * scale_factor)
        horn_y = center_y - int(tile_size * 0.45 * scale_factor)
        horn = [
            QPoint(horn_x, horn_y),
            QPoint(horn_x - int(2 * scale_factor), horn_y - int(6 * scale_factor)),
            QPoint(horn_x + int(2 * scale_factor), horn_y - int(5 * scale_factor)),
        ]
        painter.drawPolygon(horn)

    # Fierce reptilian eye with slit pupil
    painter.setBrush(QColor(255, 200, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x + int(tile_size * 0.28 * scale_factor),
                       center_y - int(tile_size * 0.4 * scale_factor),
                       int(6 * scale_factor), int(5 * scale_factor))
    # Slit pupil
    painter.setBrush(QColor(0, 0, 0))
    painter.drawRect(center_x + int(tile_size * 0.3 * scale_factor),
                    center_y - int(tile_size * 0.4 * scale_factor),
                    int(2 * scale_factor), int(5 * scale_factor))

    # Open maw with fangs
    painter.setBrush(QColor(60, 20, 20))
    painter.setPen(QPen(QColor(0, 0, 0), 1))
    maw_points = [
        QPoint(center_x + int(tile_size * 0.4 * scale_factor), center_y - int(tile_size * 0.38 * scale_factor)),
        QPoint(center_x + int(tile_size * 0.42 * scale_factor), center_y - int(tile_size * 0.35 * scale_factor)),
        QPoint(center_x + int(tile_size * 0.38 * scale_factor), center_y - int(tile_size * 0.33 * scale_factor)),
    ]
    painter.drawPolygon(maw_points)

    # Sharp fangs
    painter.setBrush(QColor(240, 240, 230))
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(3):
        fang_x = center_x + int(tile_size * 0.38 * scale_factor) + i * int(2 * scale_factor)
        fang = [
            QPoint(fang_x, center_y - int(tile_size * 0.36 * scale_factor)),
            QPoint(fang_x - 1, center_y - int(tile_size * 0.33 * scale_factor)),
            QPoint(fang_x + 1, center_y - int(tile_size * 0.33 * scale_factor)),
        ]
        painter.drawPolygon(fang)

    # Smoke wisps from nostrils with pulse
    nostril_x = center_x + int(tile_size * 0.38 * scale_factor)
    nostril_y = center_y - int(tile_size * 0.4 * scale_factor)
    for i in range(3):
        smoke_alpha = int(150 * smoke_intensity)
        smoke_gradient = QRadialGradient(nostril_x + i * int(3 * scale_factor),
                                        nostril_y - i * int(4 * scale_factor),
                                        int(4 * scale_factor))
        smoke_gradient.setColorAt(0, QColor(100, 100, 100, smoke_alpha))
        smoke_gradient.setColorAt(1, QColor(80, 80, 80, 0))
        painter.setBrush(smoke_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(nostril_x + i * int(2 * scale_factor) - int(4 * scale_factor),
                           nostril_y - i * int(4 * scale_factor) - int(4 * scale_factor),
                           int(8 * scale_factor), int(8 * scale_factor))

    # Fire breath glow (enhanced) with pulse
    fire_gradient = QRadialGradient(center_x + int(tile_size * 0.45 * scale_factor),
                                    center_y - int(tile_size * 0.35 * scale_factor),
                                    int(tile_size * 0.15 * scale_factor))
    fire_gradient.setColorAt(0, QColor(255, 255, 200, 240))
    fire_gradient.setColorAt(0.3, QColor(255, 180 + breath_pulse, 0, 200))
    fire_gradient.setColorAt(0.6, QColor(255, 100 + breath_pulse, 0, 120 + breath_pulse // 2))
    fire_gradient.setColorAt(1, QColor(255, 60, 0, 0))
    painter.setBrush(fire_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    fire_size = int(tile_size * 0.15 * scale_factor * (1.0 + smoke_intensity * 0.2))
    painter.drawEllipse(center_x + int(tile_size * 0.38 * scale_factor),
                       center_y - int(tile_size * 0.4 * scale_factor),
                       fire_size,
                       fire_size)
