"""
Skeleton enemy renderer - Risen Undead Warrior with full body
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint
import math


def draw_skeleton(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw skeleton with eerie, undead idle animations"""
    # Idle animations - Eerie, undead movements
    wisp_orbit_speed = 1.0 + math.sin(idle_time * 0.6) * 0.3  # Spectral wisps speed
    soul_fire_flicker = int(abs(math.sin(idle_time * 3.0)) * 50)  # Eyes flicker
    bone_rattle = math.sin(idle_time * 5.0) * 1  # Subtle shake
    jaw_movement = abs(math.sin(idle_time * 1.5)) * 3  # Jaw hang open/close
    sword_sway = math.sin(idle_time * 1.2) * 4  # Sword tip drift

    # Spectral aura/wispy energy around skeleton with orbit speed
    for i in range(6):
        angle = (i * math.pi / 3) + (idle_time * wisp_orbit_speed)
        wisp_dist = tile_size // 3
        wisp_x = center_x + int(wisp_dist * math.cos(angle)) + int(bone_rattle)
        wisp_y = center_y + int(wisp_dist * math.sin(angle)) + int(bone_rattle)

        wisp_gradient = QRadialGradient(wisp_x, wisp_y, tile_size // 12)
        wisp_gradient.setColorAt(0, QColor(100, 255, 200, 100))
        wisp_gradient.setColorAt(1, QColor(100, 255, 200, 0))
        painter.setBrush(wisp_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(wisp_x - tile_size // 12, wisp_y - tile_size // 12,
                           tile_size // 6, tile_size // 6)

    # Ribcage with individual ribs
    painter.setBrush(color)
    painter.setPen(QPen(color.darker(130), 2))
    # Ribcage oval
    painter.drawEllipse(center_x - tile_size // 5, center_y + tile_size // 12,
                       tile_size * 2 // 5, tile_size // 3)
    # Individual ribs
    painter.setPen(QPen(color.darker(150), 2))
    for i in range(4):
        rib_y = center_y + tile_size // 12 + i * 6
        rib_width = tile_size // 5 - i * 4
        painter.drawArc(center_x - rib_width, rib_y,
                       rib_width * 2, 8, 0, 180 * 16)

    # Spine (vertebrae)
    painter.setPen(QPen(color.darker(120), 3))
    spine_top = center_y - tile_size // 12
    spine_bottom = center_y + tile_size // 3
    painter.drawLine(center_x, spine_top, center_x, spine_bottom)
    # Vertebrae bumps
    painter.setBrush(color.darker(110))
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(5):
        vert_y = spine_top + i * 8
        painter.drawEllipse(center_x - 3, vert_y, 6, 4)

    # Tattered cape/armor remnants
    cape_gradient = QLinearGradient(center_x, center_y,
                                    center_x, center_y + tile_size // 3)
    cape_gradient.setColorAt(0, QColor(60, 50, 80, 180))
    cape_gradient.setColorAt(1, QColor(40, 30, 60, 100))
    painter.setBrush(cape_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    # Tattered cape shape
    cape = [
        QPoint(center_x - tile_size // 6, center_y - tile_size // 12),
        QPoint(center_x - tile_size // 4, center_y + tile_size // 6),
        QPoint(center_x - tile_size // 5, center_y + tile_size // 4),
        QPoint(center_x + tile_size // 5, center_y + tile_size // 4),
        QPoint(center_x + tile_size // 4, center_y + tile_size // 6),
        QPoint(center_x + tile_size // 6, center_y - tile_size // 12),
    ]
    painter.drawPolygon(cape)

    # Bony arms with weapon
    painter.setPen(QPen(color.darker(120), 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    # Right arm holding weapon (extended)
    painter.drawLine(center_x + tile_size // 8, center_y,
                    center_x + tile_size // 4, center_y - tile_size // 12)
    painter.drawLine(center_x + tile_size // 4, center_y - tile_size // 12,
                    center_x + tile_size // 3, center_y - tile_size // 6)

    # Bony hand/fingers
    painter.setPen(QPen(color.darker(130), 2))
    for i in range(3):
        finger_x = center_x + tile_size // 3 + i
        painter.drawLine(finger_x, center_y - tile_size // 6,
                       finger_x + 1, center_y - tile_size // 5)

    # Rusted sword
    sword_gradient = QLinearGradient(center_x + tile_size // 3, center_y - tile_size // 4,
                                     center_x + tile_size // 3, center_y + tile_size // 8)
    sword_gradient.setColorAt(0, QColor(160, 140, 120))
    sword_gradient.setColorAt(1, QColor(100, 80, 60))
    painter.setBrush(sword_gradient)
    painter.setPen(QPen(QColor(80, 60, 40), 2))
    # Blade
    sword_blade = [
        QPoint(center_x + tile_size // 3 - 2, center_y - tile_size // 4),
        QPoint(center_x + tile_size // 3 + 2, center_y - tile_size // 4),
        QPoint(center_x + tile_size // 3 + 1, center_y + tile_size // 12),
        QPoint(center_x + tile_size // 3 - 1, center_y + tile_size // 12),
    ]
    painter.drawPolygon(sword_blade)

    # Left arm (hanging down)
    painter.setPen(QPen(color.darker(120), 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(center_x - tile_size // 8, center_y,
                    center_x - tile_size // 5, center_y + tile_size // 8)

    # Skull (larger, more detailed)
    skull_gradient = QRadialGradient(center_x, center_y - tile_size // 5, tile_size // 4)
    skull_gradient.setColorAt(0, color.lighter(110))
    skull_gradient.setColorAt(0.8, color)
    skull_gradient.setColorAt(1, color.darker(120))
    painter.setBrush(skull_gradient)
    painter.setPen(QPen(color.darker(130), 2))
    painter.drawRoundedRect(center_x - tile_size // 4, center_y - tile_size * 2 // 5,
                           tile_size // 2, tile_size * 2 // 5, 6, 6)

    # Bone cracks on skull
    painter.setPen(QPen(color.darker(180), 1))
    painter.drawLine(center_x - tile_size // 10, center_y - tile_size // 3,
                    center_x + tile_size // 20, center_y - tile_size // 5)
    painter.drawLine(center_x + tile_size // 12, center_y - tile_size // 4,
                    center_x + tile_size // 6, center_y - tile_size // 6)

    # Eye sockets (deep and dark)
    painter.setBrush(QColor(0, 0, 0, 220))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 4,
                       tile_size // 10, tile_size // 8)
    painter.drawEllipse(center_x + tile_size // 12, center_y - tile_size // 4,
                       tile_size // 10, tile_size // 8)

    # Soul-fire eyes (glowing cyan/green) with flicker
    fire_intensity = 150 + soul_fire_flicker
    soul_fire_gradient = QRadialGradient(center_x - tile_size // 8, center_y - tile_size // 5, 4)
    soul_fire_gradient.setColorAt(0, QColor(fire_intensity, 255, 200))
    soul_fire_gradient.setColorAt(0.5, QColor(100 + soul_fire_flicker // 2, 255, 180))
    soul_fire_gradient.setColorAt(1, QColor(50, 200, 150, 0))
    painter.setBrush(soul_fire_gradient)
    painter.drawEllipse(center_x - tile_size // 7 + int(bone_rattle), center_y - tile_size // 5, 6, 8)

    soul_fire_gradient.setCenter(center_x + tile_size // 7, center_y - tile_size // 5)
    painter.setBrush(soul_fire_gradient)
    painter.drawEllipse(center_x + tile_size // 10 + int(bone_rattle), center_y - tile_size // 5, 6, 8)

    # Nasal cavity (triangular)
    painter.setBrush(QColor(0, 0, 0, 200))
    nose = [
        QPoint(center_x, center_y - tile_size // 10),
        QPoint(center_x - tile_size // 16, center_y - tile_size // 30),
        QPoint(center_x + tile_size // 16, center_y - tile_size // 30),
    ]
    painter.drawPolygon(nose)

    # Teeth (detailed) with jaw movement
    painter.setPen(QPen(QColor(0, 0, 0, 200), 1))
    jaw_offset = int(jaw_movement)
    for i in range(-3, 4):
        x_pos = center_x + i * tile_size // 16 + int(bone_rattle)
        painter.drawLine(x_pos, center_y + int(bone_rattle),
                       x_pos, center_y + tile_size // 16 + jaw_offset)

    # Ancient helmet/crown remnants
    painter.setBrush(QColor(80, 70, 60, 180))
    painter.setPen(QPen(QColor(60, 50, 40), 2))
    helmet = [
        QPoint(center_x - tile_size // 5, center_y - tile_size // 3),
        QPoint(center_x - tile_size // 4, center_y - tile_size // 2),
        QPoint(center_x, center_y - tile_size * 2 // 5),
        QPoint(center_x + tile_size // 4, center_y - tile_size // 2),
        QPoint(center_x + tile_size // 5, center_y - tile_size // 3),
    ]
    painter.drawPolygon(helmet)
