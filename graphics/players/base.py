"""
Common utilities for player rendering
"""
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


def draw_player_shadow(painter: QPainter, center_x: int, center_y: int, tile_size: int):
    """Draw an enhanced drop shadow beneath player character"""
    shadow_color = QColor(0, 0, 0, 100)
    painter.setBrush(shadow_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 2 + 3, center_y + tile_size // 4,
                        tile_size - 6, tile_size // 6)


def setup_player_transform(painter: QPainter, center_x: int, facing_direction: tuple):
    """
    Setup horizontal flip transformation if player is facing left.
    Always saves painter state for cleanup.

    Args:
        painter: QPainter object
        center_x: Center x coordinate
        facing_direction: Tuple (dx, dy) indicating which way player is facing

    Returns:
        bool: True if horizontal flip was applied
    """
    facing_dx, facing_dy = facing_direction
    flip_horizontal = facing_dx < 0

    # Save painter state
    painter.save()

    # Apply horizontal flip if facing left
    if flip_horizontal:
        painter.translate(center_x * 2, 0)
        painter.scale(-1, 1)
        return True

    return False


def cleanup_player_transform(painter: QPainter):
    """Restore painter state after transform"""
    painter.restore()
