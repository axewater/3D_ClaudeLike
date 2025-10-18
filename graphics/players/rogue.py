"""
Rogue class renderer - Stealthy assassin with dual daggers and shadow wisps
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_rogue(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw rogue with dual daggers and shadow effects"""
    # ROGUE - Stealthy assassin with dual daggers

    # Detect if this is selection screen (large tile size)
    is_selection_screen = tile_size > 128

    if is_selection_screen:
        # ENHANCED ANIMATIONS for character selection (4x scale)
        # Dagger flip/twirl cycle
        dagger_spin_cycle = idle_time * 0.8  # Spin cycle
        left_dagger_angle = (dagger_spin_cycle * 180) % 360  # Left dagger rotation
        right_dagger_angle = ((dagger_spin_cycle + 0.5) * 180) % 360  # Right dagger offset

        # Stealth pose cycle - deep crouch to standing
        crouch_cycle = math.sin(idle_time * 0.4) * tile_size * 0.15
        crouch_shift = crouch_cycle

        # Shadow wisps more dramatic
        wisp_drift_speed = 0.9 + math.sin(idle_time * 0.5) * 0.5
        wisp_size_var = 1.0 + math.sin(idle_time * 0.7) * 0.6  # Larger variation
        wisp_count_mult = 1.5  # More wisps

        # Eye glow more intense
        eye_pulse = int(abs(math.sin(idle_time * 2.0)) * 100)

        # Head scan more dramatic
        head_scan = math.sin(idle_time * 0.4) * 8
    else:
        # NORMAL ANIMATIONS for gameplay
        crouch_shift = math.sin(idle_time * 1.5) * 4
        wisp_drift_speed = 1.2 + math.sin(idle_time * 0.8) * 0.4
        wisp_size_var = 1.0 + math.sin(idle_time * 1.1) * 0.3
        eye_pulse = int(abs(math.sin(idle_time * 2.5)) * 60)
        head_scan = math.sin(idle_time * 0.6) * 2
        left_dagger_angle = 0
        right_dagger_angle = 0
        wisp_count_mult = 1.0

    # Legs (agile stance)
    leg_color = QColor(40, 40, 45)
    painter.setBrush(leg_color)
    painter.setPen(QPen(leg_color.darker(120), 1))
    # Left leg (forward)
    painter.drawRect(center_x - tile_size // 6, center_y + tile_size // 12,
                    tile_size // 10, tile_size // 4)
    # Right leg (back)
    painter.drawRect(center_x + tile_size // 12, center_y + tile_size // 8,
                    tile_size // 10, tile_size // 5)

    # Cloak (flowing behind)
    cloak_gradient = QLinearGradient(center_x, center_y - tile_size // 8,
                                     center_x, center_y + tile_size // 3)
    cloak_gradient.setColorAt(0, color.darker(110))
    cloak_gradient.setColorAt(1, color.darker(140))
    painter.setBrush(cloak_gradient)
    painter.setPen(QPen(color.darker(160), 2))
    cloak_points = [
        QPoint(center_x - tile_size // 6, center_y - tile_size // 12),
        QPoint(center_x - tile_size // 4, center_y + tile_size // 8),
        QPoint(center_x - tile_size // 5, center_y + tile_size // 3),
        QPoint(center_x + tile_size // 6, center_y + tile_size // 3),
        QPoint(center_x + tile_size // 5, center_y + tile_size // 8),
        QPoint(center_x + tile_size // 6, center_y - tile_size // 12),
    ]
    painter.drawPolygon(cloak_points)

    # Body (lean, dark outfit)
    body_color = QColor(50, 45, 60)
    painter.setBrush(body_color)
    painter.setPen(QPen(body_color.darker(120), 1))
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 10,
                       tile_size // 3, tile_size // 3)

    # Belt with pouches
    painter.setBrush(QColor(80, 60, 40))
    painter.drawRect(center_x - tile_size // 6, center_y + tile_size // 12,
                    tile_size // 3, tile_size // 20)

    # Left dagger
    painter.setBrush(QColor(200, 200, 210))
    painter.setPen(QPen(QColor(160, 160, 170), 2))
    left_blade = [
        QPoint(center_x - tile_size // 4, center_y - tile_size // 12),
        QPoint(center_x - tile_size // 6, center_y - tile_size // 10),
        QPoint(center_x - tile_size // 5, center_y + tile_size // 10),
        QPoint(center_x - tile_size // 4 - 2, center_y + tile_size // 12),
    ]
    painter.drawPolygon(left_blade)

    # Right dagger
    right_blade = [
        QPoint(center_x + tile_size // 4, center_y),
        QPoint(center_x + tile_size // 5, center_y + 2),
        QPoint(center_x + tile_size // 6, center_y + tile_size // 6),
        QPoint(center_x + tile_size // 5, center_y + tile_size // 6 + 2),
    ]
    painter.drawPolygon(right_blade)

    # Dagger hilts
    painter.setBrush(QColor(60, 40, 80))
    painter.drawRect(center_x - tile_size // 4, center_y + tile_size // 12,
                    tile_size // 16, tile_size // 12)
    painter.drawRect(center_x + tile_size // 6, center_y + tile_size // 6,
                    tile_size // 16, tile_size // 12)

    # Hood (concealing face)
    hood_gradient = QRadialGradient(center_x, center_y - tile_size // 5, tile_size // 4)
    hood_gradient.setColorAt(0, color)
    hood_gradient.setColorAt(1, color.darker(140))
    painter.setBrush(hood_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawEllipse(center_x - tile_size // 5, center_y - tile_size // 3,
                       tile_size * 2 // 5, tile_size * 2 // 5)

    # Face shadow (mostly hidden)
    painter.setBrush(QColor(0, 0, 0, 200))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 8, center_y - tile_size // 6,
                       tile_size // 4, tile_size // 5)

    # Glowing eyes (purple/dangerous) with pulse
    eye_alpha = 220 - eye_pulse
    painter.setBrush(QColor(180, 100, 255, eye_alpha))
    painter.drawEllipse(center_x - tile_size // 16 + int(head_scan), center_y - tile_size // 7 + int(crouch_shift), 3, 3)
    painter.drawEllipse(center_x + tile_size // 16 - 3 + int(head_scan), center_y - tile_size // 7 + int(crouch_shift), 3, 3)

    # Shadow wisps effect with drift and size variation
    wisp_color = QColor(color.red(), color.green(), color.blue(), 80)
    painter.setBrush(wisp_color)
    wisp_count = int(3 * wisp_count_mult)
    for i in range(wisp_count):
        angle = (i * 2 * math.pi / wisp_count) + (idle_time * wisp_drift_speed)
        wisp_x = center_x + int(tile_size // 4 * math.cos(angle))
        wisp_y = center_y + int(tile_size // 5 * math.sin(angle))
        wisp_width = int(4 * wisp_size_var)
        wisp_height = int(6 * wisp_size_var)
        painter.drawEllipse(wisp_x - wisp_width // 2, wisp_y - wisp_height // 2, wisp_width, wisp_height)
