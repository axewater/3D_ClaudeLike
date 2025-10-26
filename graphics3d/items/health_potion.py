"""
Health Potion 3D model - Healing consumable

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
from core import constants as c
from graphics3d.utils import rgb_to_ursina_color

from graphics3d.shader_manager import get_shader_manager

# Import radial gradient shader for glow effects
from shaders.radial_gradient_shader import create_soft_glow_shader


def create_health_potion_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D health potion model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Health potion 3D model
    """
    # Container entity (invisible parent)
    potion = Entity(position=position)

    # Get shader manager instance
    shader_mgr = get_shader_manager()

    # Create radial gradient shader for glow effects (soft glow preset for potions)
    radial_glow_shader = create_soft_glow_shader()

    # Rarity-based colors for liquid and glow
    if rarity == c.RARITY_COMMON:
        liquid_color = rgb_to_ursina_color(255, 50, 100)  # Bright magenta/red
        glow_color = liquid_color
        glow_alpha = 0.5
        has_strong_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        liquid_color = rgb_to_ursina_color(255, 100, 50)  # Bright orange/red
        glow_color = liquid_color
        glow_alpha = 0.55
        has_strong_glow = False
    elif rarity == c.RARITY_RARE:
        liquid_color = rgb_to_ursina_color(50, 200, 255)  # Bright cyan/blue
        glow_color = liquid_color
        glow_alpha = 0.6
        has_strong_glow = False
    elif rarity == c.RARITY_EPIC:
        liquid_color = rgb_to_ursina_color(200, 50, 255)  # Bright purple
        glow_color = rgb_to_ursina_color(220, 100, 255)
        glow_alpha = 0.65
        has_strong_glow = True
    else:  # LEGENDARY
        liquid_color = rgb_to_ursina_color(255, 215, 50)  # Golden
        glow_color = rgb_to_ursina_color(255, 230, 100)
        glow_alpha = 0.7
        has_strong_glow = True

    bottle_color = rgb_to_ursina_color(180, 220, 255)  # Light blue glass
    cork_color = rgb_to_ursina_color(120, 80, 40)  # Brown cork

    # Glowing aura around potion
    glow = Entity(
        model='sphere',
        color=glow_color,
        scale=0.25,
        parent=potion,
        position=(0, 0, 0),
        alpha=glow_alpha,
        unlit=True,
        shader=radial_glow_shader
    )

    # Additional strong glow for epic/legendary
    if has_strong_glow:
        outer_glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.35,
            parent=potion,
            position=(0, 0, 0),
            alpha=0.4,
            unlit=True,
            shader=radial_glow_shader
        )

    # Bottle (transparent cylinder/cube)
    bottle_shader = shader_mgr.get_shader_for_scale(0.25)
    bottle = Entity(
        model='cube',
        color=bottle_color,
        scale=(0.12, 0.25, 0.12),
        parent=potion,
        position=(0, 0, 0),
        alpha=0.6,  # Semi-transparent glass
        shader=bottle_shader
    )

    # Liquid inside (larger, brighter sphere - 3x original size)
    liquid = Entity(
        model='sphere',
        color=liquid_color,
        scale=(0.3, 0.54, 0.3),
        parent=bottle,
        position=(0, -0.02, 0),
        alpha=0.8,
        unlit=True  # Emissive
    )

    # Cork/stopper on top
    cork_shader = shader_mgr.get_shader_for_scale(0.08)
    cork = Entity(
        model='cube',
        color=cork_color,
        scale=(0.08, 0.06, 0.08),
        parent=potion,
        position=(0, 0.16, 0),
        shader=cork_shader
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
