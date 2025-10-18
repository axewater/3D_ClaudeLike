"""
Ring item renderer
"""
from PyQt6.QtGui import QPainter, QPen, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPointF
import constants as c
from graphics.utils import draw_gem, draw_rune, draw_metallic_gradient, draw_sparkle
import math


def draw_ring(painter: QPainter, center_x: int, center_y: int, tile_size: int, color: QColor, rarity: str):
    """Draw ring with rarity-based details"""
    ring_size = tile_size // 3

    # Determine ring material and details based on rarity
    if rarity == c.RARITY_COMMON:
        band_color = QColor(100, 100, 100)  # Iron
        gem_color = QColor(150, 150, 150)  # Dull stone
        gem_cut = "round"
        gem_size = 8
        has_filigree = False
        has_accent_gems = False
        has_runes = False
        gem_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        band_color = QColor(180, 140, 80)  # Bronze
        gem_color = color.lighter(120)
        gem_cut = "oval"
        gem_size = 10
        has_filigree = False
        has_accent_gems = False
        has_runes = False
        gem_glow = False
    elif rarity == c.RARITY_RARE:
        band_color = QColor(192, 192, 192)  # Silver
        gem_color = color.lighter(130)
        gem_cut = "emerald"
        gem_size = 12
        has_filigree = True
        has_accent_gems = False
        has_runes = False
        gem_glow = True
        glow_color = color
    elif rarity == c.RARITY_EPIC:
        band_color = QColor(220, 180, 100)  # Gold
        gem_color = QColor(200, 100, 255)
        gem_cut = "star"
        gem_size = 14
        has_filigree = True
        has_accent_gems = True
        has_runes = False
        gem_glow = True
        glow_color = QColor(200, 100, 255)
    else:  # LEGENDARY
        band_color = QColor(255, 215, 0)  # Pure gold
        gem_color = QColor(100, 200, 255)
        gem_cut = "star"
        gem_size = 16
        has_filigree = True
        has_accent_gems = True
        has_runes = True
        gem_glow = True
        glow_color = QColor(100, 200, 255)

    # Ring viewed at an angle (perspective)
    band_width = ring_size
    band_height = ring_size // 3

    # Gem glow for rare+
    if gem_glow:
        gem_glow_grad = QRadialGradient(center_x, center_y - ring_size // 4, ring_size)
        gem_glow_grad.setColorAt(0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 100))
        gem_glow_grad.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 50))
        gem_glow_grad.setColorAt(1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        painter.setBrush(gem_glow_grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - ring_size, center_y - ring_size,
                           ring_size * 2, ring_size * 2)

    # Band with metallic gradient (ellipse for perspective)
    band_gradient = draw_metallic_gradient(band_color, center_x - band_width // 2, center_y,
                                          center_x + band_width // 2, center_y + band_height)
    painter.setBrush(band_gradient)
    painter.setPen(QPen(band_color.darker(150), 2))

    # Outer ellipse (band outer edge)
    painter.drawEllipse(center_x - band_width // 2, center_y,
                       band_width, band_height)

    # Inner ellipse (band inner edge) - slightly smaller
    inner_width = band_width - 8
    inner_height = band_height - 4
    painter.setBrush(QColor(40, 40, 40))
    painter.setPen(QPen(band_color.darker(180), 1))
    painter.drawEllipse(center_x - inner_width // 2, center_y + 2,
                       inner_width, inner_height)

    # Filigree pattern on band for rare+
    if has_filigree:
        painter.setPen(QPen(band_color.lighter(140), 1))
        # Draw ornate pattern on band
        for i in range(5):
            angle = i * math.pi / 2.5
            x1 = center_x + (band_width // 2 - 4) * math.cos(angle)
            y1 = center_y + band_height // 2 + (band_height // 2 - 2) * math.sin(angle)
            painter.drawPoint(int(x1), int(y1))

        # Decorative lines
        painter.drawArc(center_x - band_width // 2 + 2, center_y + 1,
                       band_width - 4, band_height - 2, 0, 180 * 16)

    # Band top section with highlight
    top_band_gradient = draw_metallic_gradient(band_color, center_x - band_width // 2,
                                               center_y - ring_size // 3,
                                               center_x + band_width // 2,
                                               center_y + ring_size // 6)
    painter.setBrush(top_band_gradient)
    painter.setPen(QPen(band_color.darker(140), 2))

    # Top band sections (sides)
    left_band = [
        QPointF(center_x - band_width // 2, center_y + band_height // 2),
        QPointF(center_x - band_width // 3, center_y - ring_size // 6),
        QPointF(center_x - band_width // 4, center_y - ring_size // 6),
        QPointF(center_x - band_width // 2 + 4, center_y + band_height // 2),
    ]
    painter.drawPolygon(left_band)

    right_band = [
        QPointF(center_x + band_width // 2, center_y + band_height // 2),
        QPointF(center_x + band_width // 3, center_y - ring_size // 6),
        QPointF(center_x + band_width // 4, center_y - ring_size // 6),
        QPointF(center_x + band_width // 2 - 4, center_y + band_height // 2),
    ]
    painter.drawPolygon(right_band)

    # Gem setting (prongs)
    setting_color = band_color.lighter(110)
    painter.setBrush(setting_color)
    painter.setPen(QPen(setting_color.darker(130), 1))

    # Top setting platform
    setting_width = gem_size + 4
    painter.drawEllipse(center_x - setting_width // 2, center_y - ring_size // 4 - 2,
                       setting_width, 4)

    # Prongs
    prong_positions = [
        (-gem_size // 2 - 1, 0), (gem_size // 2 + 1, 0),
        (0, -gem_size // 2 - 1), (0, gem_size // 2 + 1)
    ]
    for px, py in prong_positions:
        painter.drawLine(center_x + px, center_y - ring_size // 4,
                       center_x + px, center_y - ring_size // 4 - 3)

    # Main gemstone
    draw_gem(painter, center_x, center_y - ring_size // 4, gem_size, gem_color, gem_cut)

    # Accent gems for epic+
    if has_accent_gems:
        accent_size = 4
        accent_color = gem_color.lighter(120)
        # Two small gems on band
        draw_gem(painter, center_x - band_width // 4, center_y - ring_size // 12,
                accent_size, accent_color, "round")
        draw_gem(painter, center_x + band_width // 4, center_y - ring_size // 12,
                accent_size, accent_color, "round")

    # Runes on band for legendary
    if has_runes:
        rune_color = QColor(100, 200, 255)
        draw_rune(painter, center_x - band_width // 3, center_y + band_height // 3,
                 tile_size // 24, rune_color, "circle")
        draw_rune(painter, center_x + band_width // 3, center_y + band_height // 3,
                 tile_size // 24, rune_color, "circle")

    # Sparkles for legendary
    if rarity == c.RARITY_LEGENDARY:
        # Orbiting sparkles
        for i in range(3):
            angle = i * 2 * math.pi / 3
            sx = center_x + ring_size * 0.6 * math.cos(angle)
            sy = center_y - ring_size // 4 + ring_size * 0.3 * math.sin(angle)
            draw_sparkle(painter, sx, sy, tile_size // 24, QColor(200, 230, 255))
