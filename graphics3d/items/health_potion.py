"""
Health Potion 3D model - Healing consumable

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color


def create_health_potion_3d(position: Vec3) -> Entity:
    """
    Create a 3D health potion model

    Args:
        position: 3D world position

    Returns:
        Entity: Health potion 3D model
    """
    # Container entity (invisible parent)
    potion = Entity(position=position)

    # Potion colors (red/magenta healing liquid)
    liquid_color = rgb_to_ursina_color(255, 50, 100)  # Bright magenta/red
    bottle_color = rgb_to_ursina_color(180, 220, 255)  # Light blue glass
    cork_color = rgb_to_ursina_color(120, 80, 40)  # Brown cork

    # Glowing aura around potion
    glow = Entity(
        model='sphere',
        color=liquid_color,
        scale=0.25,
        parent=potion,
        position=(0, 0, 0),
        alpha=0.4,
        unlit=True
    )

    # Bottle (transparent cylinder/cube)
    bottle = Entity(
        model='cube',
        color=bottle_color,
        scale=(0.12, 0.25, 0.12),
        parent=potion,
        position=(0, 0, 0),
        alpha=0.6  # Semi-transparent glass
    )

    # Liquid inside (smaller, brighter sphere)
    liquid = Entity(
        model='sphere',
        color=liquid_color,
        scale=(0.1, 0.18, 0.1),
        parent=bottle,
        position=(0, -0.02, 0),
        alpha=0.8,
        unlit=True  # Emissive
    )

    # Cork/stopper on top
    cork = Entity(
        model='cube',
        color=cork_color,
        scale=(0.08, 0.06, 0.08),
        parent=potion,
        position=(0, 0.16, 0)
    )

    # Small sparkle particles for visual flair (tiny spheres)
    sparkle1 = Entity(
        model='sphere',
        color=rgb_to_ursina_color(255, 255, 200),
        scale=0.02,
        parent=liquid,
        position=(0.04, 0.06, 0.04),
        unlit=True
    )

    sparkle2 = Entity(
        model='sphere',
        color=rgb_to_ursina_color(255, 200, 255),
        scale=0.015,
        parent=liquid,
        position=(-0.03, -0.04, 0.03),
        unlit=True
    )

    # Store animation state
    potion.float_time = 0.0
    potion.rotation_speed = 40.0  # Slower rotation

    return potion
