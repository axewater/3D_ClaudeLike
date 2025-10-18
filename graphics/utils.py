"""
Graphics utility functions
"""
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QRadialGradient, QPen, QPainterPath
from PyQt6.QtCore import Qt, QPoint, QPointF
import math


def apply_fog_color(color: QColor, alpha: float) -> QColor:
    """
    Darken color for fog of war effect on explored but not visible tiles.

    Args:
        color: Base color to darken
        alpha: Brightness factor (0.0 = black, 1.0 = original)

    Returns:
        Darkened QColor
    """
    return QColor(
        int(color.red() * alpha),
        int(color.green() * alpha),
        int(color.blue() * alpha)
    )


def draw_gem(painter: QPainter, x: float, y: float, size: int, color: QColor, cut_style: str = "round"):
    """
    Draw a gemstone with various cut styles.

    Args:
        painter: QPainter instance
        x: Center x coordinate
        y: Center y coordinate
        size: Gem diameter
        color: Gem base color
        cut_style: "round", "oval", "emerald", "star", "diamond"
    """
    painter.save()

    if cut_style == "round":
        # Round brilliant cut with facets
        gradient = QRadialGradient(x, y, size / 2)
        gradient.setColorAt(0, QColor(255, 255, 255, 220))
        gradient.setColorAt(0.3, color.lighter(160))
        gradient.setColorAt(0.7, color)
        gradient.setColorAt(1, color.darker(130))

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawEllipse(int(x - size/2), int(y - size/2), size, size)

        # Facet highlights
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        painter.drawArc(int(x - size/4), int(y - size/4), int(size/2), int(size/2), 45 * 16, 90 * 16)

    elif cut_style == "oval":
        # Oval cut
        gradient = QRadialGradient(x, y, size / 2)
        gradient.setColorAt(0, QColor(255, 255, 255, 200))
        gradient.setColorAt(0.4, color.lighter(150))
        gradient.setColorAt(0.8, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(140), 1))
        painter.drawEllipse(int(x - size/2), int(y - size/3), size, int(size * 0.7))

    elif cut_style == "emerald":
        # Emerald/rectangular step cut
        path = QPainterPath()
        half = size / 2
        # Octagonal shape
        points = [
            QPointF(x - half * 0.6, y - half),
            QPointF(x + half * 0.6, y - half),
            QPointF(x + half, y - half * 0.4),
            QPointF(x + half, y + half * 0.4),
            QPointF(x + half * 0.6, y + half),
            QPointF(x - half * 0.6, y + half),
            QPointF(x - half, y + half * 0.4),
            QPointF(x - half, y - half * 0.4),
        ]

        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.closeSubpath()

        gradient = QLinearGradient(x - half, y - half, x + half, y + half)
        gradient.setColorAt(0, color.lighter(140))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawPath(path)

        # Step facets
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
        painter.drawLine(int(x - half * 0.4), int(y - half * 0.6),
                        int(x + half * 0.4), int(y - half * 0.6))

    elif cut_style == "star":
        # Star cut with triangular facets
        path = QPainterPath()
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            radius = size / 2 if i % 2 == 0 else size / 3
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append(QPointF(px, py))

        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.closeSubpath()

        gradient = QRadialGradient(x, y, size / 2)
        gradient.setColorAt(0, QColor(255, 255, 255, 240))
        gradient.setColorAt(0.4, color.lighter(170))
        gradient.setColorAt(0.8, color)
        gradient.setColorAt(1, color.darker(130))

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(160), 1))
        painter.drawPath(path)

    elif cut_style == "diamond":
        # Classic diamond cut (side view)
        half = size / 2
        points = [
            QPointF(x, y - half),
            QPointF(x + half, y),
            QPointF(x, y + half),
            QPointF(x - half, y),
        ]

        gradient = QLinearGradient(x, y - half, x, y + half)
        gradient.setColorAt(0, color.lighter(160))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 220))
        gradient.setColorAt(1, color)

        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawPolygon(points)

        # Inner facet lines
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        painter.drawLine(int(x - half * 0.5), int(y), int(x + half * 0.5), int(y))

    painter.restore()


def draw_rune(painter: QPainter, x: float, y: float, size: int, color: QColor, rune_type: str = "circle"):
    """
    Draw a glowing magical rune.

    Args:
        painter: QPainter instance
        x: Center x coordinate
        y: Center y coordinate
        size: Rune size
        color: Rune glow color
        rune_type: "circle", "triangle", "star", "spiral", "cross"
    """
    painter.save()

    # Glow effect
    glow = QRadialGradient(x, y, size)
    glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 150))
    glow.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 80))
    glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
    painter.setBrush(glow)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(int(x - size), int(y - size), size * 2, size * 2)

    # Rune symbol
    painter.setPen(QPen(color.lighter(150), 2))

    if rune_type == "circle":
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(x - size/2), int(y - size/2), size, size)
        painter.drawPoint(int(x), int(y))

    elif rune_type == "triangle":
        half = size / 2
        points = [
            QPointF(x, y - half),
            QPointF(x + half, y + half),
            QPointF(x - half, y + half),
        ]
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(points)

    elif rune_type == "star":
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(4):
            angle = i * math.pi / 2
            x1 = x + (size / 2) * math.cos(angle)
            y1 = y + (size / 2) * math.sin(angle)
            x2 = x - (size / 2) * math.cos(angle)
            y2 = y - (size / 2) * math.sin(angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    elif rune_type == "spiral":
        path = QPainterPath()
        path.moveTo(x, y)
        for i in range(20):
            angle = i * math.pi / 4
            radius = (i / 20) * size / 2
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            path.lineTo(px, py)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    elif rune_type == "cross":
        half = size / 2
        painter.drawLine(int(x), int(y - half), int(x), int(y + half))
        painter.drawLine(int(x - half), int(y), int(x + half), int(y))

    painter.restore()


def draw_metallic_gradient(base_color: QColor, x1: float, y1: float, x2: float, y2: float, light_intensity: float = 1.3) -> QLinearGradient:
    """
    Create a metallic gradient for realistic metal rendering.

    Args:
        base_color: Metal base color
        x1, y1: Gradient start point
        x2, y2: Gradient end point
        light_intensity: How much to lighten highlights (default 1.3)

    Returns:
        QLinearGradient with metallic appearance
    """
    gradient = QLinearGradient(x1, y1, x2, y2)
    gradient.setColorAt(0, base_color.lighter(int(140 * light_intensity)))
    gradient.setColorAt(0.2, base_color.lighter(int(120 * light_intensity)))
    gradient.setColorAt(0.5, base_color)
    gradient.setColorAt(0.8, base_color.darker(120))
    gradient.setColorAt(1, base_color.darker(150))
    return gradient


def draw_sparkle(painter: QPainter, x: float, y: float, size: int, color: QColor):
    """
    Draw a multi-pointed sparkle/twinkle effect.

    Args:
        painter: QPainter instance
        x: Center x coordinate
        y: Center y coordinate
        size: Sparkle size
        color: Sparkle color
    """
    painter.save()

    # Central bright point
    painter.setPen(Qt.PenStyle.NoPen)
    gradient = QRadialGradient(x, y, size)
    gradient.setColorAt(0, QColor(255, 255, 255, 255))
    gradient.setColorAt(0.3, color)
    gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
    painter.setBrush(gradient)
    painter.drawEllipse(int(x - size/2), int(y - size/2), size, size)

    # Four-pointed star rays
    painter.setPen(QPen(color, 2))
    painter.drawLine(int(x - size), int(y), int(x + size), int(y))
    painter.drawLine(int(x), int(y - size), int(x), int(y + size))

    # Diagonal rays (smaller)
    half = size * 0.7
    painter.setPen(QPen(color, 1))
    painter.drawLine(int(x - half), int(y - half), int(x + half), int(y + half))
    painter.drawLine(int(x - half), int(y + half), int(x + half), int(y - half))

    painter.restore()


def draw_ornamental_border(painter: QPainter, points: list, thickness: int, rarity: str):
    """
    Draw decorative borders/filigree based on rarity.

    Args:
        painter: QPainter instance
        points: List of QPoint/QPointF defining the border path
        thickness: Border line thickness
        rarity: Rarity tier ("common", "uncommon", "rare", "epic", "legendary")
    """
    import constants as c

    painter.save()

    if rarity == c.RARITY_COMMON:
        # Simple solid border
        painter.setPen(QPen(QColor(100, 100, 100), thickness))
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

    elif rarity == c.RARITY_UNCOMMON:
        # Double line border
        painter.setPen(QPen(QColor(120, 160, 120), thickness))
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

    elif rarity == c.RARITY_RARE:
        # Dashed decorative border
        pen = QPen(QColor(100, 150, 255), thickness)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

    elif rarity == c.RARITY_EPIC:
        # Glowing border
        painter.setPen(QPen(QColor(200, 100, 255, 200), thickness + 2))
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

        painter.setPen(QPen(QColor(255, 200, 255), thickness))
        painter.drawPath(path)

    elif rarity == c.RARITY_LEGENDARY:
        # Multi-layer glowing border
        for i in range(3):
            alpha = 255 - i * 70
            width = thickness + (2 - i) * 2
            painter.setPen(QPen(QColor(255, 215, 0, alpha), width))
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            painter.drawPath(path)

    painter.restore()
