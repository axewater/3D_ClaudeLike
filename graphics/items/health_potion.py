"""
Health Potion item renderer
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QColor
from PyQt6.QtCore import Qt
import constants as c
from graphics.utils import draw_rune, draw_sparkle


def draw_health_potion(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, rarity: str):
    """Draw health potion with rarity-based details"""
    bottle_width = tile_size // 3
    bottle_height = int(tile_size * 0.4)
    neck_width = tile_size // 6
    neck_height = tile_size // 8

    # Determine liquid color based on rarity
    if rarity == c.RARITY_COMMON:
        liquid_color = QColor(220, 50, 50)
        liquid_top = QColor(255, 80, 80)
    elif rarity == c.RARITY_UNCOMMON:
        liquid_color = QColor(80, 220, 100)
        liquid_top = QColor(120, 255, 140)
    elif rarity == c.RARITY_RARE:
        liquid_color = QColor(80, 120, 255)
        liquid_top = QColor(140, 180, 255)
    elif rarity == c.RARITY_EPIC:
        liquid_color = QColor(200, 80, 255)
        liquid_top = QColor(240, 140, 255)
    else:  # LEGENDARY
        liquid_color = QColor(255, 180, 0)
        liquid_top = QColor(255, 220, 100)

    # Bottle body with gradient
    bottle_gradient = QLinearGradient(center_x - bottle_width // 2, center_y - bottle_height // 2,
                                     center_x + bottle_width // 2, center_y + bottle_height // 2)
    bottle_gradient.setColorAt(0, QColor(200, 220, 240, 100))
    bottle_gradient.setColorAt(0.5, QColor(180, 200, 220, 120))
    bottle_gradient.setColorAt(1, QColor(160, 180, 200, 140))

    painter.setBrush(bottle_gradient)
    painter.setPen(QPen(QColor(140, 160, 180), 2))
    painter.drawRoundedRect(center_x - bottle_width // 2, center_y - bottle_height // 2,
                           bottle_width, bottle_height, 4, 4)

    # Liquid with gradient (swirling effect)
    liquid_gradient = QLinearGradient(center_x, center_y - bottle_height // 2 + 2,
                                     center_x, center_y + bottle_height // 2 - 2)
    liquid_gradient.setColorAt(0, liquid_top)
    liquid_gradient.setColorAt(0.6, liquid_color)
    liquid_gradient.setColorAt(1, liquid_color.darker(120))

    painter.setBrush(liquid_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(center_x - bottle_width // 2 + 3, center_y - bottle_height // 2 + 3,
                           bottle_width - 6, bottle_height - 6, 3, 3)

    # Bubbles for uncommon+
    if rarity in [c.RARITY_UNCOMMON, c.RARITY_RARE]:
        painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawEllipse(center_x - tile_size // 16, center_y, 4, 4)
        painter.drawEllipse(center_x + tile_size // 20, center_y - tile_size // 16, 3, 3)
    elif rarity in [c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        # More bubbles
        painter.setBrush(QColor(255, 255, 255, 120))
        for i, (bx, by, bs) in enumerate([(0, 0, 4), (tile_size // 20, -tile_size // 20, 3),
                                          (-tile_size // 24, tile_size // 24, 3)]):
            painter.drawEllipse(center_x + bx - bs // 2, center_y + by - bs // 2, bs, bs)

    # Bottle neck
    neck_gradient = QLinearGradient(center_x - neck_width // 2, center_y - bottle_height // 2,
                                   center_x + neck_width // 2, center_y - bottle_height // 2 - neck_height)
    neck_gradient.setColorAt(0, QColor(180, 200, 220, 120))
    neck_gradient.setColorAt(1, QColor(200, 220, 240, 100))

    painter.setBrush(neck_gradient)
    painter.setPen(QPen(QColor(140, 160, 180), 2))
    painter.drawRect(center_x - neck_width // 2, center_y - bottle_height // 2 - neck_height,
                    neck_width, neck_height)

    # Cork with rarity-based detail
    cork_color = QColor(139, 90, 43) if rarity == c.RARITY_COMMON else QColor(180, 140, 90)
    painter.setBrush(cork_color)
    painter.setPen(QPen(cork_color.darker(130), 1))
    cork_height = tile_size // 12
    painter.drawRoundedRect(center_x - tile_size // 10, center_y - bottle_height // 2 - neck_height - cork_height,
                           tile_size // 5, cork_height, 2, 2)

    # Wax seal for rare+
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        seal_color = QColor(180, 30, 30) if rarity == c.RARITY_RARE else QColor(200, 150, 0)
        painter.setBrush(seal_color)
        painter.setPen(Qt.PenStyle.NoPen)
        # Wax drip
        painter.drawEllipse(center_x - tile_size // 12, center_y - bottle_height // 2 - neck_height - 2,
                           tile_size // 6, 4)

    # Rune on bottle for epic+
    if rarity == c.RARITY_EPIC:
        draw_rune(painter, center_x, center_y, tile_size // 12, QColor(200, 100, 255), "circle")
    elif rarity == c.RARITY_LEGENDARY:
        draw_rune(painter, center_x, center_y, tile_size // 10, QColor(255, 215, 0), "star")
        # Extra sparkles
        draw_sparkle(painter, center_x + tile_size // 5, center_y - tile_size // 6, tile_size // 16,
                    QColor(255, 255, 200))

    # Glass highlights (all rarities)
    painter.setBrush(QColor(255, 255, 255, 180))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - bottle_width // 4, center_y - bottle_height // 3, 4, 8)
    painter.drawEllipse(center_x - bottle_width // 3, center_y, 3, 4)
