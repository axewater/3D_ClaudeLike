"""
Common utilities for enemy rendering
"""
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


def draw_shadow(painter: QPainter, center_x: int, center_y: int, tile_size: int):
    """Draw a drop shadow beneath an enemy"""
    shadow_color = QColor(0, 0, 0, 80)
    painter.setBrush(shadow_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 3 + 2, center_y - tile_size // 3 + 3,
                        tile_size * 2 // 3, tile_size * 2 // 3)


def setup_transform(painter: QPainter, center_x: int, facing_direction: tuple):
    """
    Setup horizontal flip transformation if enemy is facing left.
    Returns whether flip was applied (for cleanup).
    """
    facing_dx, facing_dy = facing_direction
    flip_horizontal = facing_dx < 0

    if flip_horizontal:
        painter.save()
        painter.translate(center_x * 2, 0)
        painter.scale(-1, 1)
        return True
    else:
        painter.save()
        return False


def cleanup_transform(painter: QPainter):
    """Restore painter state after transform"""
    painter.restore()
