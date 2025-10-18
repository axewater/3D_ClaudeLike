"""
Boots item renderer
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPointF
import constants as c
from graphics.utils import draw_gem


def draw_boots(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, rarity: str):
    """Draw boots with rarity-based details"""
    boot_width = tile_size // 5
    boot_height = tile_size // 3

    # Determine boot material and details based on rarity
    if rarity == c.RARITY_COMMON:
        boot_color = QColor(101, 67, 33)  # Brown leather
        trim_color = QColor(70, 45, 20)
        has_buckles = False
        has_gems = False
        has_wings = False
        has_runes = False
        worn = True
    elif rarity == c.RARITY_UNCOMMON:
        boot_color = QColor(120, 80, 40)  # Better leather
        trim_color = QColor(180, 140, 80)  # Brass
        has_buckles = True
        has_gems = False
        has_wings = False
        has_runes = False
        worn = False
    elif rarity == c.RARITY_RARE:
        boot_color = QColor(80, 60, 40)  # Fine leather
        trim_color = QColor(192, 192, 192)  # Silver
        has_buckles = True
        has_gems = True
        has_wings = True
        wing_style = "small"
        has_runes = False
        worn = False
    elif rarity == c.RARITY_EPIC:
        boot_color = QColor(60, 40, 60)  # Enchanted leather
        trim_color = QColor(220, 180, 100)  # Gold
        has_buckles = True
        has_gems = True
        has_wings = True
        wing_style = "large"
        has_runes = True
        worn = False
    else:  # LEGENDARY
        boot_color = QColor(40, 60, 80)  # Magical material
        trim_color = QColor(255, 215, 0)
        has_buckles = True
        has_gems = True
        has_wings = True
        wing_style = "ethereal"
        has_runes = True
        worn = False

    # Function to draw a single boot
    def draw_boot(boot_x):
        # Boot body with gradient
        boot_gradient = QLinearGradient(boot_x, center_y - boot_height // 2,
                                       boot_x + boot_width, center_y + boot_height // 2)
        boot_gradient.setColorAt(0, boot_color.lighter(120))
        boot_gradient.setColorAt(0.5, boot_color)
        boot_gradient.setColorAt(1, boot_color.darker(120))

        painter.setBrush(boot_gradient)
        painter.setPen(QPen(trim_color, 2))
        painter.drawRoundedRect(boot_x, center_y - boot_height // 2,
                               boot_width, boot_height, 3, 3)

        # Sole
        painter.setBrush(trim_color.darker(130))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(boot_x, center_y + boot_height // 2 - 3, boot_width, 3)

        # Toe cap
        painter.setBrush(trim_color)
        painter.drawRoundedRect(boot_x, center_y + boot_height // 4,
                               boot_width, boot_height // 5, 2, 2)

        # Decorative stitching
        painter.setPen(QPen(boot_color.lighter(130), 1))
        painter.drawLine(boot_x + 2, center_y - boot_height // 4,
                       boot_x + boot_width - 2, center_y - boot_height // 4)

        # Buckles vs Laces
        if has_buckles:
            # Metal buckles
            painter.setBrush(trim_color)
            painter.setPen(QPen(trim_color.darker(130), 1))
            for i in range(2):
                buckle_y = center_y - boot_height // 6 + i * boot_height // 4
                painter.drawRect(boot_x + boot_width // 4, buckle_y, boot_width // 2, 3)
                painter.drawRect(boot_x + boot_width // 3, buckle_y - 1, 3, 5)
        else:
            # Simple laces
            painter.setPen(QPen(QColor(240, 230, 140), 1))
            for i in range(3):
                lace_y = center_y - boot_height // 8 + i * boot_height // 5
                painter.drawLine(boot_x + 3, lace_y, boot_x + boot_width - 3, lace_y)

        # Wear marks for common
        if worn:
            painter.setPen(QPen(boot_color.darker(140), 1))
            for i in range(2):
                wx = boot_x + boot_width // 4 + i * boot_width // 3
                painter.drawLine(wx, center_y, wx + boot_width // 8, center_y + 2)

        # Gems on toe for rare+
        if has_gems:
            gem_color = color.lighter(140)
            draw_gem(painter, boot_x + boot_width // 2, center_y + boot_height // 3,
                    4, gem_color, "round")

        # Glowing seams for epic+
        if has_runes:
            rune_color = QColor(150, 100, 255) if rarity == c.RARITY_EPIC else QColor(100, 200, 255)
            painter.setPen(QPen(rune_color, 1))
            painter.drawLine(boot_x + 2, center_y - boot_height // 3,
                           boot_x + 2, center_y + boot_height // 3)

        # Wing decorations for rare+
        if has_wings:
            wing_color = trim_color if wing_style == "small" else QColor(200, 220, 255, 180)
            wing_base_x = boot_x + boot_width
            wing_base_y = center_y

            if wing_style == "small":
                # Small decorative wing
                wing_points = [
                    QPointF(wing_base_x, wing_base_y),
                    QPointF(wing_base_x + boot_width // 4, wing_base_y - boot_height // 6),
                    QPointF(wing_base_x + boot_width // 3, wing_base_y),
                    QPointF(wing_base_x + boot_width // 4, wing_base_y + boot_height // 8),
                ]
                painter.setBrush(wing_color)
                painter.setPen(QPen(wing_color.darker(120), 1))
                painter.drawPolygon(wing_points)
            elif wing_style == "large":
                # Larger wing with feathers
                wing_points = [
                    QPointF(wing_base_x, wing_base_y),
                    QPointF(wing_base_x + boot_width // 3, wing_base_y - boot_height // 4),
                    QPointF(wing_base_x + boot_width // 2, wing_base_y - boot_height // 6),
                    QPointF(wing_base_x + boot_width // 2, wing_base_y + boot_height // 8),
                    QPointF(wing_base_x + boot_width // 3, wing_base_y + boot_height // 5),
                ]
                painter.setBrush(QColor(220, 180, 100))
                painter.setPen(QPen(QColor(180, 140, 60), 1))
                painter.drawPolygon(wing_points)
                # Feather details
                painter.setPen(QPen(QColor(200, 160, 80), 1))
                painter.drawLine(int(wing_base_x + boot_width // 6), int(wing_base_y - boot_height // 8),
                               int(wing_base_x + boot_width // 3), int(wing_base_y - boot_height // 5))
            else:  # ethereal
                # Magical ethereal wings
                for offset in range(3):
                    alpha = 100 - offset * 30
                    glow_color = QColor(100, 200, 255, alpha)
                    wing_points = [
                        QPointF(wing_base_x, wing_base_y),
                        QPointF(wing_base_x + boot_width // 2 + offset * 2, wing_base_y - boot_height // 3),
                        QPointF(wing_base_x + boot_width // 2 + offset * 3, wing_base_y),
                        QPointF(wing_base_x + boot_width // 2 + offset * 2, wing_base_y + boot_height // 4),
                    ]
                    painter.setBrush(glow_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawPolygon(wing_points)

    # Draw both boots
    draw_boot(center_x - tile_size // 4)
    draw_boot(center_x + tile_size // 20)

    # Legendary trail effect
    if rarity == c.RARITY_LEGENDARY:
        # Magical footprint glow
        trail = QRadialGradient(center_x, center_y + boot_height // 2, tile_size // 4)
        trail.setColorAt(0, QColor(100, 200, 255, 80))
        trail.setColorAt(0.5, QColor(100, 200, 255, 40))
        trail.setColorAt(1, QColor(100, 200, 255, 0))
        painter.setBrush(trail)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - tile_size // 4, center_y + boot_height // 3,
                           tile_size // 2, tile_size // 6)
        from graphics.utils import draw_sparkle
        draw_sparkle(painter, center_x + tile_size // 6, center_y - boot_height // 4,
                    tile_size // 20, QColor(200, 230, 255))
