"""
Tile rendering functions for dungeon elements with biome support
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import QRect, QPointF, Qt
import constants as c


def draw_wall_tile(painter: QPainter, x: int, y: int, tile_size: int, biome: str = c.BIOME_DUNGEON):
    """Draw a wall tile with biome-specific style"""
    # Get biome-specific color
    base_color = c.BIOME_COLORS[biome]["wall"]

    # Create brick pattern
    brick_rect = QRect(x * tile_size, y * tile_size, tile_size, tile_size)

    # Biome-specific rendering
    if biome == c.BIOME_DUNGEON:
        # Stone brick wall with mortar
        gradient = QLinearGradient(x * tile_size, y * tile_size,
                                    (x + 1) * tile_size, (y + 1) * tile_size)
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(130))
        painter.fillRect(brick_rect, gradient)

        # Draw mortar lines for brick effect
        painter.setPen(QPen(base_color.darker(160), 1))
        offset = (y % 2) * (tile_size // 2)
        mid_y = y * tile_size + tile_size // 2
        painter.drawLine(x * tile_size, mid_y, (x + 1) * tile_size, mid_y)
        mid_x = x * tile_size + tile_size // 2 + offset
        if mid_x < (x + 1) * tile_size:
            painter.drawLine(mid_x, y * tile_size, mid_x, (y + 1) * tile_size)

    elif biome == c.BIOME_CATACOMBS:
        # Bone/skull wall pattern
        painter.fillRect(brick_rect, base_color)
        painter.setPen(QPen(base_color.lighter(130), 2))
        # Draw bone-like cracks
        painter.drawLine(x * tile_size + tile_size // 3, y * tile_size,
                        x * tile_size + tile_size // 3, (y + 1) * tile_size)
        painter.drawLine(x * tile_size, y * tile_size + tile_size // 2,
                        (x + 1) * tile_size, y * tile_size + tile_size // 2)

    elif biome == c.BIOME_CAVES:
        # Natural rock with irregular texture
        gradient = QRadialGradient(QPointF(x * tile_size + tile_size * 0.3,
                                           y * tile_size + tile_size * 0.3), tile_size * 0.8)
        gradient.setColorAt(0, base_color.lighter(115))
        gradient.setColorAt(1, base_color.darker(120))
        painter.fillRect(brick_rect, gradient)
        # Rocky texture lines
        painter.setPen(QPen(base_color.darker(140), 1))
        for i in range(3):
            y_offset = (i + 1) * tile_size // 4
            painter.drawLine(x * tile_size, y * tile_size + y_offset,
                           (x + 1) * tile_size, y * tile_size + y_offset)

    elif biome == c.BIOME_HELL:
        # Dark stone with lava cracks
        painter.fillRect(brick_rect, base_color)
        # Lava glow effect
        gradient = QRadialGradient(QPointF(x * tile_size + tile_size / 2,
                                           y * tile_size + tile_size / 2), tile_size * 0.4)
        gradient.setColorAt(0, QColor(255, 80, 0, 80))
        gradient.setColorAt(1, QColor(255, 0, 0, 0))
        painter.fillRect(brick_rect, gradient)
        # Lava crack lines
        painter.setPen(QPen(QColor(255, 100, 50, 180), 1))
        painter.drawLine(x * tile_size, y * tile_size + tile_size // 2,
                        (x + 1) * tile_size, y * tile_size + tile_size // 2)

    elif biome == c.BIOME_ABYSS:
        # Void-like ethereal walls
        gradient = QLinearGradient(x * tile_size, y * tile_size,
                                    (x + 1) * tile_size, (y + 1) * tile_size)
        gradient.setColorAt(0, base_color.lighter(130))
        gradient.setColorAt(0.5, base_color)
        gradient.setColorAt(1, base_color.darker(140))
        painter.fillRect(brick_rect, gradient)
        # Ethereal purple glow
        painter.setPen(QPen(QColor(180, 120, 255, 100), 1))
        painter.drawRect(x * tile_size + 2, y * tile_size + 2,
                        tile_size - 4, tile_size - 4)

    # Dark outline for all biomes
    painter.setPen(QPen(QColor(20, 20, 25), 1))
    painter.drawRect(x * tile_size, y * tile_size, tile_size - 1, tile_size - 1)


def draw_floor_tile(painter: QPainter, x: int, y: int, tile_size: int, biome: str = c.BIOME_DUNGEON):
    """Draw a floor tile with biome-specific style"""
    # Get biome-specific color
    base_color = c.BIOME_COLORS[biome]["floor"]

    # Alternating floor pattern
    is_dark = (x + y) % 2 == 0
    if is_dark:
        tile_color = base_color.darker(105)
    else:
        tile_color = base_color.lighter(105)

    painter.fillRect(x * tile_size, y * tile_size, tile_size, tile_size, tile_color)

    # Biome-specific floor details
    if biome == c.BIOME_CATACOMBS:
        # Dusty scattered bone fragments
        if (x * 7 + y * 13) % 11 == 0:
            painter.setPen(QPen(QColor(200, 190, 180, 120), 1))
            painter.drawLine(x * tile_size + 5, y * tile_size + 5,
                           x * tile_size + 10, y * tile_size + 8)

    elif biome == c.BIOME_CAVES:
        # Moss/dirt patches
        if (x * 5 + y * 7) % 9 == 0:
            painter.setBrush(QColor(60, 80, 50, 80))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawEllipse(x * tile_size + 8, y * tile_size + 8, 6, 6)

    elif biome == c.BIOME_HELL:
        # Lava cracks
        if (x * 3 + y * 11) % 13 == 0:
            painter.setPen(QPen(QColor(255, 100, 50, 150), 1))
            painter.drawLine(x * tile_size, y * tile_size + tile_size // 2,
                           (x + 1) * tile_size, y * tile_size + tile_size // 2)

    elif biome == c.BIOME_ABYSS:
        # Void particles/stars
        if (x * 11 + y * 3) % 17 == 0:
            painter.setBrush(QColor(180, 120, 255, 180))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawEllipse(x * tile_size + 12, y * tile_size + 12, 2, 2)

    # Subtle border
    painter.setPen(QPen(base_color.darker(115), 1))
    painter.drawRect(x * tile_size, y * tile_size, tile_size - 1, tile_size - 1)


def draw_stairs_tile(painter: QPainter, x: int, y: int, tile_size: int, biome: str = c.BIOME_DUNGEON):
    """Draw glowing stairs with biome-specific style"""
    # Get biome-specific color
    base_color = c.BIOME_COLORS[biome]["stairs"]

    # Glowing radial gradient background
    center = QPointF(x * tile_size + tile_size / 2, y * tile_size + tile_size / 2)
    gradient = QRadialGradient(center, tile_size * 0.7)
    gradient.setColorAt(0, base_color.lighter(150))
    gradient.setColorAt(0.5, base_color)
    gradient.setColorAt(1, base_color.darker(120))

    painter.fillRect(x * tile_size, y * tile_size, tile_size, tile_size, gradient)

    # Draw stair steps
    painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
    step_height = tile_size // 5
    for i in range(4):
        y_pos = y * tile_size + (i + 1) * step_height
        x_start = x * tile_size + i * 3
        x_end = (x + 1) * tile_size - i * 3
        painter.drawLine(x_start, y_pos, x_end, y_pos)
