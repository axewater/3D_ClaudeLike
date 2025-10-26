"""
Sword 3D model - Melee weapon with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
from core import constants as c
from graphics3d.utils import rgb_to_ursina_color
from graphics3d.shader_manager import get_shader_manager
from graphics3d.rarity_palette import RarityPalette

# Import radial gradient shader for glow effects
import sys
from pathlib import Path

# Add project root to path for radial gradient shader import
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shaders.radial_gradient_shader import create_energy_orb_shader


def create_sword_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D sword model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Sword 3D model
    """
    # Container entity (invisible parent)
    sword = Entity(position=position)

    # Get shader manager instance
    shader_mgr = get_shader_manager()

    # Create radial gradient shader for glow effects
    radial_glow_shader = create_energy_orb_shader()

    # Get rarity-based colors from palette
    colors = RarityPalette.get_ursina_colors('sword', rarity)
    blade_color = colors.get('blade')
    crossguard_color = colors.get('crossguard')
    handle_color = colors.get('handle')
    has_glow = colors.get('has_glow', False)
    glow_color = colors.get('glow')

    # Blade glow for epic/legendary (outer sphere)
    if has_glow:
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.35,
            parent=sword,
            position=(0, 0.3, 0),
            alpha=0.5,  # Increased from 0.3 - shader will create gradient
            unlit=True,
            shader=radial_glow_shader
        )

    # Blade (vertical stretched cube)
    blade_shader = shader_mgr.get_shader_for_scale(0.45)
    blade = Entity(
        model='cube',
        color=blade_color,
        scale=(0.05, 0.45, 0.12),
        parent=sword,
        position=(0, 0.3, 0),
        shader=blade_shader
    )

    # Blade edge highlight (thin lighter cube on front)
    blade_edge_shader = shader_mgr.get_shader_for_scale(0.45)
    blade_edge = Entity(
        model='cube',
        color=blade_color.tint(0.3),
        scale=(0.02, 0.45, 0.13),
        parent=blade,
        position=(0, 0, 0),
        shader=blade_edge_shader
    )

    # Crossguard (horizontal rectangle)
    crossguard_shader = shader_mgr.get_shader_for_scale(0.25)
    crossguard = Entity(
        model='cube',
        color=crossguard_color,
        scale=(0.25, 0.04, 0.05),
        parent=sword,
        position=(0, 0.05, 0),
        shader=crossguard_shader
    )

    # Handle (vertical cylinder/cube)
    handle_shader = shader_mgr.get_shader_for_scale(0.15)
    handle = Entity(
        model='cube',
        color=handle_color,
        scale=(0.05, 0.15, 0.05),
        parent=sword,
        position=(0, -0.08, 0),
        shader=handle_shader
    )

    # Pommel (sphere at bottom)
    pommel_shader = shader_mgr.get_shader_for_scale(0.06)
    pommel = Entity(
        model='sphere',
        color=crossguard_color,
        scale=0.06,
        parent=sword,
        position=(0, -0.18, 0),
        shader=pommel_shader
    )

    # Gem on pommel for rare+ (small colored sphere)
    gem_color = colors.get('gem')
    if gem_color:
        gem_shader = shader_mgr.get_shader_for_scale(0.04)
        gem = Entity(
            model='sphere',
            color=gem_color,
            scale=0.04,
            parent=pommel,
            position=(0, 0, 0),
            unlit=True,  # Emissive gem
            shader=gem_shader
        )

    # Store animation state
    sword.float_time = 0.0
    sword.rotation_speed = 50.0  # Degrees per second

    return sword
