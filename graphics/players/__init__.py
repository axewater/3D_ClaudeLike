"""
Player rendering module - dispatches to specific class renderers
"""
from PyQt6.QtGui import QPainter, QColor
import constants as c

from .base import draw_player_shadow, setup_player_transform, cleanup_player_transform
from .warrior import draw_warrior
from .mage import draw_mage
from .rogue import draw_rogue
from .ranger import draw_ranger


def draw_player(painter: QPainter, x: float, y: float, tile_size: int, color: QColor,
                class_type: str, facing_direction: tuple = (0, 1), idle_time: float = 0.0):
    """
    Draw player character based on class with directional facing and idle animations.

    This is the main entry point for player rendering. It handles common setup
    (shadow, transform) and delegates to specific class renderers.

    Args:
        painter: QPainter object for drawing
        x: Grid x-coordinate
        y: Grid y-coordinate
        tile_size: Size of each tile in pixels
        color: Base color for the player class
        class_type: Type of class (warrior, mage, rogue, ranger)
        facing_direction: Tuple (dx, dy) indicating which way player is facing
        idle_time: Time value for idle animations
    """
    center_x = int(x * tile_size + tile_size // 2)
    center_y = int(y * tile_size + tile_size // 2)

    # Setup transform and draw shadow
    setup_player_transform(painter, center_x, facing_direction)
    draw_player_shadow(painter, center_x, center_y, tile_size)

    # Dispatch to appropriate class renderer
    if class_type == c.CLASS_WARRIOR:
        draw_warrior(painter, center_x, center_y, tile_size, color, idle_time)
    elif class_type == c.CLASS_MAGE:
        draw_mage(painter, center_x, center_y, tile_size, color, idle_time)
    elif class_type == c.CLASS_ROGUE:
        draw_rogue(painter, center_x, center_y, tile_size, color, idle_time)
    elif class_type == c.CLASS_RANGER:
        draw_ranger(painter, center_x, center_y, tile_size, color, idle_time)

    # Clean up transform
    cleanup_player_transform(painter)


# Export the main function
__all__ = ['draw_player']
