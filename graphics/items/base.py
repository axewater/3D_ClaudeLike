"""
Common utilities for item rendering
"""
from PyQt6.QtGui import QPainter, QRadialGradient, QColor
from PyQt6.QtCore import Qt


def draw_item_shadow(painter: QPainter, center_x: int, center_y: int, tile_size: int):
    """Draw a drop shadow beneath an item"""
    shadow_color = QColor(0, 0, 0, 60)
    painter.setBrush(shadow_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 4 + 2, center_y - tile_size // 4 + 2,
                        tile_size // 2, tile_size // 2)


def draw_rarity_glow(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor):
    """Draw a rarity-based glow effect around an item"""
    gradient = QRadialGradient(center_x, center_y, tile_size // 2)
    gradient.setColorAt(0, color.lighter(130))
    gradient.setColorAt(0.7, color)
    gradient.setColorAt(1, QColor(0, 0, 0, 0))
    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - tile_size // 2, center_y - tile_size // 2,
                        tile_size, tile_size)
