"""
Enemy rendering module - dispatches to specific enemy renderers
"""
from PyQt6.QtGui import QPainter, QColor
import constants as c

from .base import draw_shadow, setup_transform, cleanup_transform
from .goblin import draw_goblin
from .slime import draw_slime
from .skeleton import draw_skeleton
from .orc import draw_orc
from .demon import draw_demon
from .dragon import draw_dragon


def draw_enemy(painter: QPainter, x: float, y: float, tile_size: int, color: QColor,
               enemy_type: str, facing_direction: tuple = (0, 1), idle_time: float = 0.0):
    """
    Draw enemy based on type with directional facing and idle animations.

    This is the main entry point for enemy rendering. It handles common setup
    (shadow, transform) and delegates to specific enemy renderers.

    Args:
        painter: QPainter object for drawing
        x: Grid x-coordinate
        y: Grid y-coordinate
        tile_size: Size of each tile in pixels
        color: Base color for the enemy
        enemy_type: Type of enemy (goblin, slime, skeleton, orc, demon, dragon)
        facing_direction: Tuple (dx, dy) indicating which way enemy is facing
        idle_time: Time value for idle animations
    """
    center_x = int(x * tile_size + tile_size // 2)
    center_y = int(y * tile_size + tile_size // 2)

    # Setup transform and draw shadow
    setup_transform(painter, center_x, facing_direction)
    draw_shadow(painter, center_x, center_y, tile_size)

    # Dispatch to appropriate enemy renderer
    if enemy_type == c.ENEMY_GOBLIN:
        draw_goblin(painter, center_x, center_y, tile_size, color, idle_time)
    elif enemy_type == c.ENEMY_SLIME:
        draw_slime(painter, center_x, center_y, tile_size, color, idle_time)
    elif enemy_type == c.ENEMY_SKELETON:
        draw_skeleton(painter, center_x, center_y, tile_size, color, idle_time)
    elif enemy_type == c.ENEMY_ORC:
        draw_orc(painter, center_x, center_y, tile_size, color, idle_time)
    elif enemy_type == c.ENEMY_DEMON:
        draw_demon(painter, center_x, center_y, tile_size, color, idle_time)
    elif enemy_type == c.ENEMY_DRAGON:
        draw_dragon(painter, center_x, center_y, tile_size, color, idle_time)

    # Clean up transform
    cleanup_transform(painter)


# Export the main function
__all__ = ['draw_enemy']
