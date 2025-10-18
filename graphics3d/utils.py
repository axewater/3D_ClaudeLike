"""
Shared 3D rendering utilities

Common functions for procedural 3D model generation, materials, and effects.
"""

from typing import Tuple
from ursina import Vec3, color as ursina_color
from PyQt6.QtGui import QColor


def create_gradient_material(base_color: Tuple[int, int, int], brightness: float = 1.0):
    """
    Create a gradient material for entities

    Args:
        base_color: RGB color tuple (0-255)
        brightness: Brightness multiplier

    Returns:
        Ursina color object
    """
    return rgb_to_ursina_color(base_color[0], base_color[1], base_color[2])


def create_metallic_material(base_color: Tuple[int, int, int], metallic: float = 0.8):
    """
    Create a metallic material for weapons/armor

    Args:
        base_color: RGB color tuple (0-255)
        metallic: Metallic factor (0.0-1.0)

    Returns:
        Ursina material
    """
    r, g, b = base_color
    brightness = 1.0 + (metallic * 0.3)
    return rgb_to_ursina_color(
        min(255, int(r * brightness)),
        min(255, int(g * brightness)),
        min(255, int(b * brightness))
    )


def create_glow_effect(entity, color: Tuple[int, int, int], intensity: float = 0.5):
    """
    Add a glow effect to an entity

    Args:
        entity: Ursina Entity to apply glow to
        color: RGB glow color
        intensity: Glow intensity
    """
    glow_color = rgb_to_ursina_color(
        min(255, int(color[0] * (1 + intensity))),
        min(255, int(color[1] * (1 + intensity))),
        min(255, int(color[2] * (1 + intensity)))
    )
    entity.color = glow_color


def world_to_3d_position(grid_x: int, grid_y: int, height: float = 0.0) -> Tuple[float, float, float]:
    """
    Convert 2D grid coordinates to 3D world position

    Args:
        grid_x: X position in 2D grid
        grid_y: Y position in 2D grid
        height: Height/elevation in 3D space

    Returns:
        (x, y, z) tuple for 3D position
        - X: horizontal (same as grid X)
        - Y: vertical (height)
        - Z: depth (grid Y becomes Z)
    """
    return (float(grid_x), height, float(grid_y))


def rgb_to_ursina_color(r: int, g: int, b: int):
    """
    Convert RGB (0-255) to Ursina color (0-1)

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        Ursina color object
    """
    return ursina_color.rgb(r / 255.0, g / 255.0, b / 255.0)


def qcolor_to_ursina_color(qcolor: QColor):
    """
    Convert PyQt6 QColor to Ursina color

    Args:
        qcolor: QColor object

    Returns:
        Ursina color object
    """
    return rgb_to_ursina_color(qcolor.red(), qcolor.green(), qcolor.blue())
