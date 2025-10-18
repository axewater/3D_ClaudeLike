"""
Ranger class renderer - Nature archer with bow, quiver, and floating leaves
"""
from PyQt6.QtGui import QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint, QRect
import math


def draw_ranger(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, idle_time: float):
    """Draw ranger with bow and arrow and nature effects"""
    # RANGER - Nature archer with bow and quiver

    # Detect if this is selection screen (large tile size)
    is_selection_screen = tile_size > 128

    if is_selection_screen:
        # ENHANCED ANIMATIONS for character selection (4x scale)
        # Bow draw cycle (3 second cycle)
        draw_cycle = idle_time * 0.6  # Slow cycle
        draw_phase = draw_cycle % 2.0  # 0 to 2 seconds

        if draw_phase < 0.7:  # Idle/ready
            bow_draw = 0
            arrow_pull = 0
        elif draw_phase < 1.2:  # Drawing bow
            progress = (draw_phase - 0.7) / 0.5
            bow_draw = progress
            arrow_pull = int(tile_size * 0.15 * progress)
        elif draw_phase < 1.6:  # Holding drawn
            bow_draw = 1.0
            arrow_pull = int(tile_size * 0.15)
        else:  # Release and return
            progress = (draw_phase - 1.6) / 0.4
            bow_draw = 1.0 - progress
            arrow_pull = int(tile_size * 0.15 * (1 - progress))

        # Stance shift - hunter's crouch
        stance_shift = math.sin(idle_time * 0.4) * tile_size * 0.08

        # Leaves swirl faster and larger
        leaf_orbit_speed = 1.2 + math.sin(idle_time * 0.3) * 0.4
        leaf_radius_mult = 1.3 + math.sin(idle_time * 0.5) * 0.3

        # Head scanning
        head_turn = math.sin(idle_time * 0.5) * 10

        # Breathing
        breathing = math.sin(idle_time * 0.7) * 6
    else:
        # NORMAL ANIMATIONS for gameplay
        bow_adjust = math.sin(idle_time * 1.0) * 2
        leaf_orbit_speed = 0.8 + math.sin(idle_time * 0.5) * 0.2
        head_turn = math.sin(idle_time * 0.7) * 3
        breathing = math.sin(idle_time * 0.9) * 2
        bow_draw = 0
        arrow_pull = 0
        stance_shift = 0
        leaf_radius_mult = 1.0

    # Legs (balanced stance)
    leg_color = QColor(80, 100, 70)
    painter.setBrush(leg_color)
    painter.setPen(QPen(leg_color.darker(120), 1))
    # Left leg
    painter.drawRect(center_x - tile_size // 7, center_y + tile_size // 10,
                    tile_size // 9, tile_size // 4)
    # Right leg
    painter.drawRect(center_x + tile_size // 14, center_y + tile_size // 10,
                    tile_size // 9, tile_size // 4)

    # Quiver on back
    painter.setBrush(QColor(100, 70, 40))
    painter.setPen(QPen(QColor(70, 50, 30), 2))
    painter.drawRect(center_x + tile_size // 6, center_y - tile_size // 12,
                    tile_size // 10, tile_size // 4)

    # Arrow fletching (3 arrows in quiver)
    painter.setPen(QPen(QColor(200, 180, 140), 1))
    for i in range(3):
        x_off = i * 2 - 2
        painter.drawLine(center_x + tile_size // 6 + x_off, center_y - tile_size // 12,
                       center_x + tile_size // 6 + x_off, center_y - tile_size // 8)

    # Body (leather armor)
    body_gradient = QLinearGradient(center_x - tile_size // 5, center_y - tile_size // 10,
                                    center_x + tile_size // 5, center_y + tile_size // 10)
    body_gradient.setColorAt(0, color.darker(110))
    body_gradient.setColorAt(0.5, color)
    body_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(body_gradient)
    painter.setPen(QPen(color.darker(130), 2))
    painter.drawEllipse(center_x - tile_size // 5, center_y - tile_size // 12,
                       tile_size * 2 // 5, tile_size // 3)

    # Leather strap across chest
    painter.setPen(QPen(QColor(100, 70, 40), 2))
    painter.drawLine(center_x - tile_size // 6, center_y - tile_size // 12,
                    center_x + tile_size // 5, center_y + tile_size // 10)

    # Bow (held ready)
    bow_wood = QColor(120, 80, 40)
    painter.setPen(QPen(bow_wood, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    # Bow curve
    bow_rect = QRect(center_x - tile_size // 3, center_y - tile_size // 4,
                    tile_size // 3, tile_size // 2)
    painter.drawArc(bow_rect, 20 * 16, 320 * 16)

    # Bowstring - curved when drawn
    painter.setPen(QPen(QColor(200, 190, 180), 2))
    if is_selection_screen and bow_draw > 0:
        # Draw curved string when bow is drawn
        string_pull_x = center_x - tile_size // 6 - int(arrow_pull * 0.8)
        painter.drawLine(center_x - tile_size // 6, center_y - tile_size // 5,
                       string_pull_x, center_y)
        painter.drawLine(string_pull_x, center_y,
                       center_x - tile_size // 6, center_y + tile_size // 6)
    else:
        # Straight string when not drawn
        painter.drawLine(center_x - tile_size // 6, center_y - tile_size // 5,
                       center_x - tile_size // 6, center_y + tile_size // 6)

    # Nocked arrow with bow draw animation
    painter.setBrush(QColor(139, 90, 43))
    painter.setPen(QPen(QColor(100, 60, 30), 1))
    # Arrow shaft - pulled back when drawing
    arrow_start_x = center_x - tile_size // 6 - arrow_pull
    arrow_end_x = center_x - tile_size // 3 - 2
    painter.drawLine(arrow_start_x, center_y,
                    arrow_end_x, center_y)
    # Arrowhead
    arrow_head = [
        QPoint(arrow_end_x, center_y),
        QPoint(center_x - tile_size // 4, center_y - 2),
        QPoint(center_x - tile_size // 4, center_y + 2),
    ]
    painter.setBrush(QColor(180, 180, 190))
    painter.drawPolygon(arrow_head)

    # Head with hood/bandana
    head_gradient = QRadialGradient(center_x, center_y - tile_size // 5, tile_size // 5)
    head_gradient.setColorAt(0, color.lighter(120))
    head_gradient.setColorAt(1, color.darker(110))
    painter.setBrush(head_gradient)
    painter.setPen(QPen(color.darker(130), 2))
    painter.drawEllipse(center_x - tile_size // 6, center_y - tile_size // 3,
                       tile_size // 3, tile_size // 3)

    # Bandana/headband
    painter.setBrush(color.darker(120))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(center_x - tile_size // 6, center_y - tile_size // 5,
                    tile_size // 3, tile_size // 16)

    # Face (partial visible)
    painter.setBrush(QColor(220, 180, 150))
    painter.drawEllipse(center_x - tile_size // 12, center_y - tile_size // 8,
                       tile_size // 6, tile_size // 7)

    # Eyes (focused)
    painter.setBrush(QColor(80, 60, 40))
    painter.drawEllipse(center_x - tile_size // 20, center_y - tile_size // 10, 2, 2)
    painter.drawEllipse(center_x + tile_size // 30, center_y - tile_size // 10, 2, 2)

    # Nature leaves floating nearby with drift
    leaf_color = QColor(120, 200, 100, 160)
    painter.setBrush(leaf_color)
    painter.setPen(Qt.PenStyle.NoPen)
    leaf_count = 2 if not is_selection_screen else 4  # More leaves in selection
    for i in range(leaf_count):
        angle = (i * 2 * math.pi / leaf_count) + (idle_time * leaf_orbit_speed)
        leaf_x = center_x + int(tile_size // 3 * leaf_radius_mult * math.cos(angle))
        leaf_y = center_y + int(tile_size // 4 * leaf_radius_mult * math.sin(angle)) + int(breathing)
        # Small leaf shape
        leaf_points = [
            QPoint(leaf_x, leaf_y - 4),
            QPoint(leaf_x + 3, leaf_y),
            QPoint(leaf_x, leaf_y + 4),
            QPoint(leaf_x - 2, leaf_y),
        ]
        painter.drawPolygon(leaf_points)
