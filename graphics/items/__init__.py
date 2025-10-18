"""
Item rendering module - dispatches to specific item renderers
"""
from PyQt6.QtGui import QPainter, QPen, QRadialGradient, QColor
from PyQt6.QtCore import Qt
import constants as c

from .base import draw_item_shadow, draw_rarity_glow
from .health_potion import draw_health_potion
from .sword import draw_sword
from .shield import draw_shield
from .boots import draw_boots
from .ring import draw_ring


def draw_item(painter: QPainter, x: float, y: float, tile_size: int, color: QColor, item_type: str, rarity: str = c.RARITY_COMMON):
    """
    Draw item based on type with rarity-based details.

    This is the main entry point for item rendering. It handles common setup
    (shadow, rarity glow) and delegates to specific item renderers.

    Args:
        painter: QPainter object for drawing
        x: Grid x-coordinate
        y: Grid y-coordinate
        tile_size: Size of each tile in pixels
        color: Base color for the item
        item_type: Type of item (health_potion, sword, shield, boots, ring)
        rarity: Item rarity (common, uncommon, rare, epic, legendary)
    """
    center_x = int(x * tile_size + tile_size // 2)
    center_y = int(y * tile_size + tile_size // 2)

    # Draw common elements
    draw_item_shadow(painter, center_x, center_y, tile_size)
    draw_rarity_glow(painter, center_x, center_y, tile_size, color)

    # Dispatch to appropriate item renderer
    if item_type == c.ITEM_HEALTH_POTION:
        draw_health_potion(painter, center_x, center_y, tile_size, color, rarity)
    elif item_type == c.ITEM_SWORD:
        draw_sword(painter, center_x, center_y, tile_size, color, rarity)
    elif item_type == c.ITEM_SHIELD:
        draw_shield(painter, center_x, center_y, tile_size, color, rarity)
    elif item_type == c.ITEM_BOOTS:
        draw_boots(painter, center_x, center_y, tile_size, color, rarity)
    elif item_type == c.ITEM_RING:
        draw_ring(painter, center_x, center_y, tile_size, color, rarity)
    else:
        # Generic item (glowing orb)
        gradient = QRadialGradient(center_x, center_y, tile_size // 4)
        gradient.setColorAt(0, QColor(255, 255, 255, 200))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(150), 2))
        painter.drawEllipse(center_x - tile_size // 4, center_y - tile_size // 4,
                           tile_size // 2, tile_size // 2)


# Export the main function
__all__ = ['draw_item']
