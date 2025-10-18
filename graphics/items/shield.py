"""
Shield item renderer
"""
from PyQt6.QtGui import QPainter, QPen, QRadialGradient, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF
import constants as c
from graphics.utils import draw_gem, draw_rune, draw_metallic_gradient, draw_sparkle


def draw_shield(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, rarity: str):
    """Draw shield with rarity-based details"""
    shield_size = tile_size // 2

    # Determine shield material and details based on rarity
    if rarity == c.RARITY_COMMON:
        shield_color = color.darker(110)
        rim_color = QColor(100, 100, 100)
        has_emblem = False
        has_gems = False
        has_runes = False
        studs = True
    elif rarity == c.RARITY_UNCOMMON:
        shield_color = color
        rim_color = QColor(180, 140, 80)  # Brass
        has_emblem = True
        emblem_type = "cross"
        has_gems = False
        has_runes = False
        studs = True
    elif rarity == c.RARITY_RARE:
        shield_color = color.lighter(110)
        rim_color = QColor(192, 192, 192)  # Silver
        has_emblem = True
        emblem_type = "star"
        has_gems = True
        gem_count = 4
        has_runes = False
        studs = False
    elif rarity == c.RARITY_EPIC:
        shield_color = color.lighter(120)
        rim_color = QColor(220, 180, 100)  # Gold
        has_emblem = True
        emblem_type = "spiral"
        has_gems = True
        gem_count = 4
        has_runes = True
        studs = False
    else:  # LEGENDARY
        shield_color = color.lighter(130)
        rim_color = QColor(255, 215, 0)
        has_emblem = True
        emblem_type = "star"
        has_gems = True
        gem_count = 5
        has_runes = True
        studs = False

    # Shield body - kite shape
    shield_gradient = draw_metallic_gradient(shield_color, center_x - shield_size // 2,
                                            center_y - shield_size // 2, center_x + shield_size // 2,
                                            center_y + shield_size // 2)
    painter.setBrush(shield_gradient)
    painter.setPen(QPen(shield_color.darker(140), 2))

    shield_points = [
        QPointF(center_x, center_y - shield_size * 0.65),
        QPointF(center_x + shield_size * 0.5, center_y - shield_size * 0.3),
        QPointF(center_x + shield_size * 0.5, center_y + shield_size * 0.2),
        QPointF(center_x, center_y + shield_size * 0.65),
        QPointF(center_x - shield_size * 0.5, center_y + shield_size * 0.2),
        QPointF(center_x - shield_size * 0.5, center_y - shield_size * 0.3),
    ]
    painter.drawPolygon(shield_points)

    # Metal studs for common/uncommon
    if studs:
        painter.setBrush(rim_color)
        painter.setPen(QPen(rim_color.darker(130), 1))
        stud_positions = [
            (0, -shield_size * 0.5), (shield_size * 0.35, -shield_size * 0.2),
            (shield_size * 0.35, shield_size * 0.1), (0, shield_size * 0.5),
            (-shield_size * 0.35, shield_size * 0.1), (-shield_size * 0.35, -shield_size * 0.2)
        ]
        for sx, sy in stud_positions:
            painter.drawEllipse(int(center_x + sx - 3), int(center_y + sy - 3), 6, 6)

    # Decorative rim
    rim_gradient = draw_metallic_gradient(rim_color, center_x - shield_size // 2, center_y,
                                         center_x + shield_size // 2, center_y)
    painter.setBrush(rim_gradient)
    painter.setPen(QPen(rim_color.darker(150), 2))

    # Rim border
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        painter.setPen(QPen(rim_color, 4))
        path = QPainterPath()
        path.moveTo(shield_points[0])
        for p in shield_points[1:]:
            path.lineTo(p)
        path.closeSubpath()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    # Shield boss (center piece)
    boss_size = shield_size // 3
    boss_gradient = QRadialGradient(center_x, center_y, boss_size // 2)
    boss_gradient.setColorAt(0, rim_color.lighter(140))
    boss_gradient.setColorAt(0.5, rim_color)
    boss_gradient.setColorAt(1, rim_color.darker(120))

    painter.setBrush(boss_gradient)
    painter.setPen(QPen(rim_color.darker(150), 2))
    painter.drawEllipse(center_x - boss_size // 2, center_y - boss_size // 2, boss_size, boss_size)

    # Emblem on boss
    if has_emblem:
        emblem_color = rim_color.lighter(150)
        draw_rune(painter, center_x, center_y, boss_size // 3, emblem_color, emblem_type)

    # Corner gems for rare+
    if has_gems:
        gem_positions = [
            (0, -shield_size * 0.5),
            (shield_size * 0.35, -shield_size * 0.15),
            (shield_size * 0.35, shield_size * 0.15),
            (-shield_size * 0.35, shield_size * 0.15),
            (-shield_size * 0.35, -shield_size * 0.15),
        ]
        gem_color = color.lighter(150)
        for i in range(min(gem_count, len(gem_positions))):
            gx, gy = gem_positions[i]
            draw_gem(painter, center_x + gx, center_y + gy, 6, gem_color, "round")

    # Runes around edge for epic+
    if has_runes:
        rune_color = QColor(150, 100, 255) if rarity == c.RARITY_EPIC else QColor(100, 200, 255)
        rune_positions = [
            (shield_size * 0.25, -shield_size * 0.4),
            (shield_size * 0.25, shield_size * 0.1),
            (-shield_size * 0.25, shield_size * 0.1),
            (-shield_size * 0.25, -shield_size * 0.4),
        ]
        for rx, ry in rune_positions:
            draw_rune(painter, center_x + rx, center_y + ry, tile_size // 20, rune_color, "circle")

    # Energy field for legendary
    if rarity == c.RARITY_LEGENDARY:
        field = QRadialGradient(center_x, center_y, shield_size)
        field.setColorAt(0, QColor(100, 200, 255, 0))
        field.setColorAt(0.7, QColor(100, 200, 255, 40))
        field.setColorAt(1, QColor(100, 200, 255, 0))
        painter.setBrush(field)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - shield_size, center_y - shield_size,
                           shield_size * 2, shield_size * 2)
        draw_sparkle(painter, center_x + shield_size * 0.4, center_y - shield_size * 0.3,
                    tile_size // 18, QColor(200, 230, 255))
