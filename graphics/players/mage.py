"""
Mage class renderer - Robed spellcaster with floating orbs and staff
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_mage(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw mage with floating orbs and mystical staff"""
    # MAGE - Robed spellcaster with floating orbs

    # Detect if this is selection screen (large tile size)
    is_selection_screen = tile_size > 128

    if is_selection_screen:
        # ENHANCED ANIMATIONS for character selection (4x scale)
        # Staff spinning/twirling
        staff_rotation = (idle_time * 60) % 360  # Slow 360 rotation
        staff_float = math.sin(idle_time * 0.8) * tile_size * 0.08

        # Orb constellation - larger spiral pattern
        orb_spiral_radius = 1.0 + math.sin(idle_time * 0.4) * 0.3  # Pulsing radius
        orb_speed_variation = 0.7 + math.sin(idle_time * 0.3) * 0.3  # Variable speed

        # Arcane energy in hands
        hand_glow = int(abs(math.sin(idle_time * 2.5)) * 60)

        # Robe billowing
        robe_sway = math.sin(idle_time * 0.5) * 12
        robe_billow = abs(math.sin(idle_time * 0.6)) * 8

        # Staff pulse more dramatic
        staff_pulse = int(abs(math.sin(idle_time * 1.8)) * 80)
        rune_glow = int(abs(math.sin(idle_time * 1.2)) * 60)
    else:
        # NORMAL ANIMATIONS for gameplay
        orb_speed_variation = 1.0 + math.sin(idle_time * 0.5) * 0.3
        staff_pulse = int(abs(math.sin(idle_time * 2.0)) * 50)
        robe_sway = math.sin(idle_time * 0.7) * 3
        rune_glow = int(abs(math.sin(idle_time * 1.5)) * 40)
        staff_rotation = 0
        staff_float = 0
        orb_spiral_radius = 1.0
        hand_glow = 0
        robe_billow = 0

    # Robe bottom (flowing) with sway and billow
    robe_offset = int(robe_sway)
    robe_width_offset = int(robe_billow)
    robe_points = [
        QPoint(center_x + robe_offset, center_y + tile_size // 10),
        QPoint(center_x - tile_size // 3 + robe_offset - robe_width_offset, center_y + tile_size // 3),
        QPoint(center_x + tile_size // 3 + robe_offset + robe_width_offset, center_y + tile_size // 3),
    ]
    robe_gradient = QLinearGradient(center_x, center_y,
                                    center_x, center_y + tile_size // 3)
    robe_gradient.setColorAt(0, color)
    robe_gradient.setColorAt(1, color.darker(130))
    painter.setBrush(robe_gradient)
    painter.setPen(QPen(color.darker(150), 2))
    painter.drawPolygon(robe_points)

    # Robe body
    painter.drawEllipse(center_x - tile_size // 4, center_y - tile_size // 8,
                       tile_size // 2, tile_size * 2 // 5)

    # Belt/sash
    painter.setBrush(color.darker(140))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(center_x - tile_size // 4, center_y + tile_size // 20,
                    tile_size // 2, tile_size // 15)

    # Staff (left hand)
    painter.setPen(QPen(QColor(139, 90, 43), 3))
    painter.drawLine(center_x - tile_size // 4, center_y - tile_size // 8,
                    center_x - tile_size // 3, center_y - tile_size // 2)

    # Staff orb (glowing) with pulse
    orb_gradient = QRadialGradient(center_x - tile_size // 3, center_y - tile_size // 2,
                                   tile_size // 8)
    orb_gradient.setColorAt(0, QColor(255, 255, 255, 240))
    orb_gradient.setColorAt(0.4, color.lighter(160 + staff_pulse))
    orb_gradient.setColorAt(1, color.lighter(100 + staff_pulse // 2))
    painter.setBrush(orb_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 3 - tile_size // 12,
                       center_y - tile_size // 2 - tile_size // 12,
                       tile_size // 6, tile_size // 6)

    # Floating magical orbs (3 orbiting) with speed variation and spiral
    for i in range(3):
        angle = (i * 2 * math.pi / 3) + (math.pi / 4) + (idle_time * orb_speed_variation)
        orb_x = center_x + int(tile_size // 3 * orb_spiral_radius * math.cos(angle))
        orb_y = center_y + int(tile_size // 4 * orb_spiral_radius * math.sin(angle))

        # Orb glow
        mini_gradient = QRadialGradient(orb_x, orb_y, tile_size // 12)
        mini_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        mini_gradient.setColorAt(0.5, color.lighter(140))
        mini_gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(mini_gradient)
        painter.drawEllipse(orb_x - tile_size // 12, orb_y - tile_size // 12,
                           tile_size // 6, tile_size // 6)

    # Hood
    hood_gradient = QRadialGradient(center_x, center_y - tile_size // 4, tile_size // 4)
    hood_gradient.setColorAt(0, color.lighter(110))
    hood_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(hood_gradient)
    painter.setPen(QPen(color.darker(140), 2))
    # Hood shape
    hood_points = [
        QPoint(center_x, center_y - tile_size // 3),
        QPoint(center_x - tile_size // 4, center_y - tile_size // 6),
        QPoint(center_x - tile_size // 5, center_y - tile_size // 12),
        QPoint(center_x + tile_size // 5, center_y - tile_size // 12),
        QPoint(center_x + tile_size // 4, center_y - tile_size // 6),
    ]
    painter.drawPolygon(hood_points)

    # Glowing eyes under hood
    painter.setBrush(color.lighter(180))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 12, center_y - tile_size // 6, 3, 4)
    painter.drawEllipse(center_x + tile_size // 12 - 3, center_y - tile_size // 6, 3, 4)

    # Mystical rune on robe with pulsing glow
    rune_brightness = 160 + rune_glow
    painter.setPen(QPen(color.lighter(rune_brightness), 2))
    painter.drawLine(center_x - tile_size // 16 + robe_offset, center_y,
                    center_x + tile_size // 16 + robe_offset, center_y)
    painter.drawLine(center_x + robe_offset, center_y - tile_size // 16,
                    center_x + robe_offset, center_y + tile_size // 16)
