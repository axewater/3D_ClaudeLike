"""
Health Potion 3D model - Healing consumable

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color

# Import toon shader system
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add dna_editor to path (after project root)
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.append(dna_editor_path)

from dna_editor.shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale

# Import radial gradient shader for glow effects
from shaders.radial_gradient_shader import create_soft_glow_shader


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

    # Create toon shader instances (shared across solid components only)
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Create radial gradient shader for glow effects (soft glow preset for potions)
    radial_glow_shader = create_soft_glow_shader()

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
        alpha=0.6,  # Increased from 0.4 - shader will create gradient
        unlit=True,
        shader=radial_glow_shader
    )

    # Bottle (transparent cylinder/cube)
    bottle_shader = get_shader_for_scale(0.25, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    bottle = Entity(
        model='cube',
        color=bottle_color,
        scale=(0.12, 0.25, 0.12),
        parent=potion,
        position=(0, 0, 0),
        alpha=0.6,  # Semi-transparent glass
        shader=bottle_shader
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
    cork_shader = get_shader_for_scale(0.08, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
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
