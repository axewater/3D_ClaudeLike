"""
Sword item renderer
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF
import constants as c
from graphics.utils import draw_gem, draw_rune, draw_metallic_gradient, draw_sparkle


def draw_sword(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, rarity: str):
    """Draw sword with rarity-based details"""
    blade_length = tile_size // 2
    blade_width = tile_size // 6

    # Determine blade material and color based on rarity
    if rarity == c.RARITY_COMMON:
        blade_base = QColor(160, 160, 160)  # Iron
        crossguard_color = QColor(100, 100, 100)
        has_gem = False
        has_runes = False
        blade_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        blade_base = QColor(180, 180, 180)  # Steel
        crossguard_color = QColor(180, 140, 80)  # Brass
        has_gem = False
        has_runes = False
        blade_glow = False
    elif rarity == c.RARITY_RARE:
        blade_base = QColor(200, 200, 210)  # Silver steel
        crossguard_color = QColor(192, 192, 192)
        has_gem = True
        has_runes = False
        blade_glow = False
    elif rarity == c.RARITY_EPIC:
        blade_base = QColor(210, 210, 220)
        crossguard_color = QColor(220, 180, 100)  # Gold
        has_gem = True
        has_runes = True
        blade_glow = True
        glow_color = QColor(150, 100, 255)
    else:  # LEGENDARY
        blade_base = QColor(220, 220, 240)
        crossguard_color = QColor(255, 215, 0)
        has_gem = True
        has_runes = True
        blade_glow = True
        glow_color = QColor(100, 200, 255)

    # Blade glow for epic+
    if blade_glow:
        glow = QRadialGradient(center_x, center_y - blade_length // 4, blade_length)
        glow.setColorAt(0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 100))
        glow.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 40))
        glow.setColorAt(1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - blade_length, center_y - blade_length,
                           blade_length * 2, blade_length * 2)

    # Blade with metallic gradient
    blade_gradient = draw_metallic_gradient(blade_base, center_x - blade_width // 2,
                                           center_y - blade_length, center_x + blade_width // 2,
                                           center_y)
    painter.setBrush(blade_gradient)
    painter.setPen(QPen(blade_base.darker(150), 2))

    # Blade shape with point
    blade_points = [
        QPointF(center_x, center_y - blade_length),
        QPointF(center_x + blade_width // 2, center_y - blade_length + blade_width),
        QPointF(center_x + blade_width // 3, center_y + tile_size // 10),
        QPointF(center_x - blade_width // 3, center_y + tile_size // 10),
        QPointF(center_x - blade_width // 2, center_y - blade_length + blade_width),
    ]
    painter.drawPolygon(blade_points)

    # Fuller (groove down center)
    painter.setPen(QPen(blade_base.darker(110), 1))
    painter.drawLine(center_x, center_y - blade_length + blade_width + 2,
                    center_x, center_y + tile_size // 12)

    # Runes on blade for epic+
    if has_runes:
        rune_color = QColor(150, 100, 255) if rarity == c.RARITY_EPIC else QColor(100, 200, 255)
        draw_rune(painter, center_x, center_y - blade_length // 2, tile_size // 16, rune_color, "cross")
        if rarity == c.RARITY_LEGENDARY:
            draw_rune(painter, center_x, center_y - blade_length // 4, tile_size // 16, rune_color, "circle")

    # Crossguard with ornate design
    crossguard_y = center_y + tile_size // 10
    crossguard_gradient = draw_metallic_gradient(crossguard_color, center_x - tile_size // 4,
                                                 crossguard_y, center_x + tile_size // 4, crossguard_y + tile_size // 12)
    painter.setBrush(crossguard_gradient)
    painter.setPen(QPen(crossguard_color.darker(140), 2))

    if rarity in [c.RARITY_COMMON, c.RARITY_UNCOMMON]:
        # Simple crossguard
        painter.drawRect(center_x - tile_size // 4, crossguard_y, tile_size // 2, tile_size // 12)
    else:
        # Ornate curved crossguard
        path = QPainterPath()
        path.moveTo(center_x - tile_size // 4, crossguard_y + tile_size // 24)
        path.quadTo(center_x - tile_size // 5, crossguard_y - tile_size // 48,
                   center_x, crossguard_y + tile_size // 24)
        path.quadTo(center_x + tile_size // 5, crossguard_y + tile_size // 16,
                   center_x + tile_size // 4, crossguard_y + tile_size // 24)
        path.lineTo(center_x + tile_size // 4, crossguard_y + tile_size // 12)
        path.lineTo(center_x - tile_size // 4, crossguard_y + tile_size // 12)
        path.closeSubpath()
        painter.drawPath(path)

    # Handle
    handle_y = crossguard_y + tile_size // 12
    handle_height = tile_size // 5
    handle_color = QColor(100, 60, 30) if rarity == c.RARITY_COMMON else QColor(80, 40, 20)
    handle_gradient = QLinearGradient(center_x - tile_size // 12, handle_y,
                                     center_x + tile_size // 12, handle_y + handle_height)
    handle_gradient.setColorAt(0, handle_color.lighter(120))
    handle_gradient.setColorAt(0.5, handle_color)
    handle_gradient.setColorAt(1, handle_color.darker(110))

    painter.setBrush(handle_gradient)
    painter.setPen(QPen(handle_color.darker(130), 1))
    painter.drawRoundedRect(center_x - tile_size // 12, handle_y, tile_size // 6, handle_height, 2, 2)

    # Wrapped grip lines
    painter.setPen(QPen(handle_color.darker(150), 1))
    for i in range(3):
        y = handle_y + (i + 1) * handle_height // 4
        painter.drawLine(center_x - tile_size // 12, y, center_x + tile_size // 12, y)

    # Pommel with gem for rare+
    pommel_y = handle_y + handle_height
    painter.setBrush(crossguard_gradient)
    painter.setPen(QPen(crossguard_color.darker(130), 1))
    painter.drawEllipse(center_x - tile_size // 10, pommel_y, tile_size // 5, tile_size // 10)

    if has_gem:
        gem_color = color if rarity == c.RARITY_RARE else QColor(200, 50, 255)
        gem_size = 6 if rarity == c.RARITY_RARE else 8
        cut = "round" if rarity == c.RARITY_RARE else "star"
        draw_gem(painter, center_x, pommel_y + tile_size // 20, gem_size, gem_color, cut)

    # Blade gleam/highlight
    painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
    painter.drawLine(center_x + blade_width // 6, center_y - blade_length + blade_width,
                    center_x + blade_width // 8, center_y - tile_size // 16)

    # Legendary sparkles
    if rarity == c.RARITY_LEGENDARY:
        draw_sparkle(painter, center_x - blade_width // 4, center_y - blade_length * 2 // 3,
                    tile_size // 20, QColor(200, 230, 255))
