"""
Ability icon rendering functions
"""
from PyQt6.QtGui import QPainter, QPen, QLinearGradient, QRadialGradient, QColor
from PyQt6.QtCore import Qt, QPoint, QPointF
import constants as c
import math


def draw_ability_fireball(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a fireball ability icon with flames and heat"""
    radius = size // 2

    # Outer flame glow
    outer_gradient = QRadialGradient(center_x, center_y, radius * 0.9)
    outer_gradient.setColorAt(0, c.COLOR_ABILITY_FIREBALL.lighter(140))
    outer_gradient.setColorAt(0.4, c.COLOR_ABILITY_FIREBALL)
    outer_gradient.setColorAt(0.7, c.COLOR_ABILITY_FIREBALL_SECONDARY)
    outer_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_FIREBALL_SECONDARY.red(),
                                        c.COLOR_ABILITY_FIREBALL_SECONDARY.green(),
                                        c.COLOR_ABILITY_FIREBALL_SECONDARY.blue(), 0))
    painter.setBrush(outer_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Core fire orb
    core_gradient = QRadialGradient(center_x - radius * 0.15, center_y - radius * 0.15, radius * 0.6)
    core_gradient.setColorAt(0, QColor(255, 255, 200))
    core_gradient.setColorAt(0.3, QColor(255, 200, 80))
    core_gradient.setColorAt(0.7, c.COLOR_ABILITY_FIREBALL)
    core_gradient.setColorAt(1, c.COLOR_ABILITY_FIREBALL_SECONDARY)
    painter.setBrush(core_gradient)
    painter.drawEllipse(center_x - int(radius * 0.6), center_y - int(radius * 0.6),
                       int(radius * 1.2), int(radius * 1.2))

    # Flame wisps
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(6):
        angle = (i * math.pi / 3) + math.pi / 6
        wisp_dist = radius * 0.7
        wisp_x = center_x + int(wisp_dist * math.cos(angle))
        wisp_y = center_y + int(wisp_dist * math.sin(angle))

        wisp_gradient = QRadialGradient(wisp_x, wisp_y, radius * 0.15)
        wisp_gradient.setColorAt(0, QColor(255, 150, 50, 200))
        wisp_gradient.setColorAt(1, QColor(255, 80, 0, 0))
        painter.setBrush(wisp_gradient)
        painter.drawEllipse(wisp_x - int(radius * 0.15), wisp_y - int(radius * 0.15),
                           int(radius * 0.3), int(radius * 0.3))


def draw_ability_dash(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a dash/teleport ability icon with speed lines"""
    radius = size // 2

    # Electric blue glow
    glow_gradient = QRadialGradient(center_x, center_y, radius)
    glow_gradient.setColorAt(0, c.COLOR_ABILITY_DASH.lighter(150))
    glow_gradient.setColorAt(0.5, c.COLOR_ABILITY_DASH)
    glow_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_DASH.red(),
                                       c.COLOR_ABILITY_DASH.green(),
                                       c.COLOR_ABILITY_DASH.blue(), 0))
    painter.setBrush(glow_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Speed lines/lightning bolts
    painter.setPen(QPen(c.COLOR_ABILITY_DASH_SECONDARY, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    for i in range(8):
        angle = i * math.pi / 4
        # Inner point
        inner_x = center_x + int(radius * 0.3 * math.cos(angle))
        inner_y = center_y + int(radius * 0.3 * math.sin(angle))
        # Outer point
        outer_x = center_x + int(radius * 0.8 * math.cos(angle))
        outer_y = center_y + int(radius * 0.8 * math.sin(angle))

        painter.drawLine(inner_x, inner_y, outer_x, outer_y)

    # Central lightning core
    core_gradient = QRadialGradient(center_x, center_y, radius * 0.35)
    core_gradient.setColorAt(0, QColor(255, 255, 255))
    core_gradient.setColorAt(0.6, c.COLOR_ABILITY_DASH_SECONDARY)
    core_gradient.setColorAt(1, c.COLOR_ABILITY_DASH)
    painter.setBrush(core_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - int(radius * 0.35), center_y - int(radius * 0.35),
                       int(radius * 0.7), int(radius * 0.7))


def draw_ability_healing(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a healing ability icon with a glowing heart/cross"""
    radius = size // 2

    # Healing green glow
    glow_gradient = QRadialGradient(center_x, center_y, radius)
    glow_gradient.setColorAt(0, c.COLOR_ABILITY_HEALING_SECONDARY)
    glow_gradient.setColorAt(0.5, c.COLOR_ABILITY_HEALING)
    glow_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_HEALING.red(),
                                       c.COLOR_ABILITY_HEALING.green(),
                                       c.COLOR_ABILITY_HEALING.blue(), 0))
    painter.setBrush(glow_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Medical cross
    cross_size = radius * 0.7
    cross_thickness = radius * 0.25

    cross_gradient = QLinearGradient(center_x, center_y - cross_size, center_x, center_y + cross_size)
    cross_gradient.setColorAt(0, QColor(255, 255, 255))
    cross_gradient.setColorAt(0.5, c.COLOR_ABILITY_HEALING_SECONDARY)
    cross_gradient.setColorAt(1, c.COLOR_ABILITY_HEALING)

    painter.setBrush(cross_gradient)
    painter.setPen(QPen(c.COLOR_ABILITY_HEALING.darker(120), 2))

    # Vertical bar
    painter.drawRoundedRect(int(center_x - cross_thickness / 2), int(center_y - cross_size),
                           int(cross_thickness), int(cross_size * 2), 3, 3)

    # Horizontal bar
    painter.drawRoundedRect(int(center_x - cross_size), int(center_y - cross_thickness / 2),
                           int(cross_size * 2), int(cross_thickness), 3, 3)

    # Sparkles around the cross
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(4):
        angle = (i * math.pi / 2) + math.pi / 4
        sparkle_dist = radius * 0.7
        sparkle_x = center_x + int(sparkle_dist * math.cos(angle))
        sparkle_y = center_y + int(sparkle_dist * math.sin(angle))

        sparkle_points = [
            QPoint(sparkle_x, sparkle_y - 4),
            QPoint(sparkle_x + 1, sparkle_y - 1),
            QPoint(sparkle_x + 4, sparkle_y),
            QPoint(sparkle_x + 1, sparkle_y + 1),
            QPoint(sparkle_x, sparkle_y + 4),
            QPoint(sparkle_x - 1, sparkle_y + 1),
            QPoint(sparkle_x - 4, sparkle_y),
            QPoint(sparkle_x - 1, sparkle_y - 1),
        ]
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawPolygon(sparkle_points)


def draw_ability_frost(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a frost nova ability icon with ice crystals"""
    radius = size // 2

    # Ice blue glow
    glow_gradient = QRadialGradient(center_x, center_y, radius)
    glow_gradient.setColorAt(0, c.COLOR_ABILITY_FROST_SECONDARY)
    glow_gradient.setColorAt(0.5, c.COLOR_ABILITY_FROST)
    glow_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_FROST.red(),
                                       c.COLOR_ABILITY_FROST.green(),
                                       c.COLOR_ABILITY_FROST.blue(), 0))
    painter.setBrush(glow_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Snowflake/ice crystal pattern
    ice_color = c.COLOR_ABILITY_FROST_SECONDARY
    painter.setPen(QPen(ice_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

    # 6 main spokes of snowflake
    for i in range(6):
        angle = i * math.pi / 3
        end_x = center_x + int(radius * 0.7 * math.cos(angle))
        end_y = center_y + int(radius * 0.7 * math.sin(angle))
        painter.drawLine(center_x, center_y, end_x, end_y)

        # Branches on each spoke
        branch_dist = radius * 0.45
        branch_x = center_x + int(branch_dist * math.cos(angle))
        branch_y = center_y + int(branch_dist * math.sin(angle))

        # Left branch
        branch_angle_l = angle - math.pi / 6
        branch_end_l_x = branch_x + int(radius * 0.25 * math.cos(branch_angle_l))
        branch_end_l_y = branch_y + int(radius * 0.25 * math.sin(branch_angle_l))
        painter.drawLine(branch_x, branch_y, branch_end_l_x, branch_end_l_y)

        # Right branch
        branch_angle_r = angle + math.pi / 6
        branch_end_r_x = branch_x + int(radius * 0.25 * math.cos(branch_angle_r))
        branch_end_r_y = branch_y + int(radius * 0.25 * math.sin(branch_angle_r))
        painter.drawLine(branch_x, branch_y, branch_end_r_x, branch_end_r_y)

    # Central ice crystal
    painter.setBrush(QColor(255, 255, 255, 220))
    painter.setPen(QPen(c.COLOR_ABILITY_FROST, 2))
    painter.drawEllipse(center_x - int(radius * 0.2), center_y - int(radius * 0.2),
                       int(radius * 0.4), int(radius * 0.4))


def draw_ability_whirlwind(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a whirlwind ability icon with spinning blades"""
    radius = size // 2

    # Red energy glow
    glow_gradient = QRadialGradient(center_x, center_y, radius)
    glow_gradient.setColorAt(0, c.COLOR_ABILITY_WHIRLWIND_SECONDARY)
    glow_gradient.setColorAt(0.5, c.COLOR_ABILITY_WHIRLWIND)
    glow_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_WHIRLWIND.red(),
                                       c.COLOR_ABILITY_WHIRLWIND.green(),
                                       c.COLOR_ABILITY_WHIRLWIND.blue(), 0))
    painter.setBrush(glow_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Spinning blade arcs
    painter.setPen(Qt.PenStyle.NoPen)

    for i in range(4):
        angle = i * math.pi / 2

        # Create curved blade shape
        blade_points = []
        arc_radius = radius * 0.7

        # Blade path
        for j in range(8):
            t = j / 7.0
            blade_angle = angle + (t * math.pi / 3) - math.pi / 6
            blade_dist = arc_radius * (0.4 + t * 0.4)

            blade_x = center_x + int(blade_dist * math.cos(blade_angle))
            blade_y = center_y + int(blade_dist * math.sin(blade_angle))
            blade_points.append(QPoint(blade_x, blade_y))

        # Create the blade gradient
        blade_gradient = QLinearGradient(QPointF(blade_points[0]), QPointF(blade_points[-1]))
        blade_gradient.setColorAt(0, QColor(200, 200, 220, 250))
        blade_gradient.setColorAt(0.5, QColor(220, 220, 230))
        blade_gradient.setColorAt(1, QColor(180, 180, 200, 100))

        painter.setBrush(blade_gradient)
        painter.setPen(QPen(QColor(150, 150, 160), 2))
        painter.drawPolygon(blade_points)

    # Central hub
    hub_gradient = QRadialGradient(center_x, center_y, radius * 0.25)
    hub_gradient.setColorAt(0, QColor(255, 255, 255))
    hub_gradient.setColorAt(0.6, c.COLOR_ABILITY_WHIRLWIND_SECONDARY)
    hub_gradient.setColorAt(1, c.COLOR_ABILITY_WHIRLWIND)
    painter.setBrush(hub_gradient)
    painter.setPen(QPen(c.COLOR_ABILITY_WHIRLWIND.darker(120), 2))
    painter.drawEllipse(center_x - int(radius * 0.25), center_y - int(radius * 0.25),
                       int(radius * 0.5), int(radius * 0.5))


def draw_ability_shadow(painter: QPainter, center_x: int, center_y: int, size: int):
    """Draw a shadow step ability icon with dagger and smoke"""
    radius = size // 2

    # Dark purple/shadow glow
    glow_gradient = QRadialGradient(center_x, center_y, radius)
    glow_gradient.setColorAt(0, c.COLOR_ABILITY_SHADOW.lighter(130))
    glow_gradient.setColorAt(0.5, c.COLOR_ABILITY_SHADOW)
    glow_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_SHADOW_SECONDARY.red(),
                                       c.COLOR_ABILITY_SHADOW_SECONDARY.green(),
                                       c.COLOR_ABILITY_SHADOW_SECONDARY.blue(), 0))
    painter.setBrush(glow_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_x - radius, center_y - radius, size, size)

    # Shadow wisps/smoke
    for i in range(5):
        angle = (i * 2 * math.pi / 5) + math.pi / 10
        wisp_dist = radius * 0.6
        wisp_x = center_x + int(wisp_dist * math.cos(angle))
        wisp_y = center_y + int(wisp_dist * math.sin(angle))

        wisp_gradient = QRadialGradient(wisp_x, wisp_y, radius * 0.2)
        wisp_gradient.setColorAt(0, QColor(c.COLOR_ABILITY_SHADOW.red(),
                                           c.COLOR_ABILITY_SHADOW.green(),
                                           c.COLOR_ABILITY_SHADOW.blue(), 180))
        wisp_gradient.setColorAt(1, QColor(c.COLOR_ABILITY_SHADOW_SECONDARY.red(),
                                           c.COLOR_ABILITY_SHADOW_SECONDARY.green(),
                                           c.COLOR_ABILITY_SHADOW_SECONDARY.blue(), 0))
        painter.setBrush(wisp_gradient)
        painter.drawEllipse(wisp_x - int(radius * 0.2), wisp_y - int(radius * 0.2),
                           int(radius * 0.4), int(radius * 0.4))

    # Dagger in center
    dagger_length = radius * 0.8
    dagger_width = radius * 0.15

    # Dagger blade (angled)
    blade_gradient = QLinearGradient(center_x - dagger_width, center_y - dagger_length // 2,
                                     center_x + dagger_width, center_y + dagger_length // 2)
    blade_gradient.setColorAt(0, QColor(200, 200, 220))
    blade_gradient.setColorAt(0.5, QColor(220, 220, 240))
    blade_gradient.setColorAt(1, QColor(180, 180, 200))

    painter.setBrush(blade_gradient)
    painter.setPen(QPen(QColor(150, 150, 170), 2))

    blade_points = [
        QPoint(center_x, int(center_y - dagger_length // 2)),
        QPoint(int(center_x + dagger_width), int(center_y - dagger_length // 4)),
        QPoint(int(center_x + dagger_width // 2), int(center_y + dagger_length // 4)),
        QPoint(int(center_x - dagger_width // 2), int(center_y + dagger_length // 4)),
    ]
    painter.drawPolygon(blade_points)

    # Dagger hilt
    painter.setBrush(c.COLOR_ABILITY_SHADOW.darker(110))
    painter.drawRoundedRect(int(center_x - dagger_width), int(center_y + dagger_length // 4),
                           int(dagger_width * 2), int(dagger_length // 3), 2, 2)

    # Gleam on blade
    painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
    painter.drawLine(center_x, int(center_y - dagger_length // 2.5),
                    int(center_x + dagger_width // 2), int(center_y - dagger_length // 6))
