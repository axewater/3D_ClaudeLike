"""
Sword 3D model - Melee weapon with rarity variants

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

    # Create toon shader instances (shared across all sword components)
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Create radial gradient shader for glow effects
    radial_glow_shader = create_energy_orb_shader()

    # Rarity-based colors
    if rarity == c.RARITY_COMMON:
        blade_color = rgb_to_ursina_color(160, 160, 160)  # Iron gray
        crossguard_color = rgb_to_ursina_color(100, 100, 100)  # Dark gray
        handle_color = rgb_to_ursina_color(100, 60, 30)  # Brown leather
        has_glow = False
        glow_color = None
    elif rarity == c.RARITY_UNCOMMON:
        blade_color = rgb_to_ursina_color(180, 180, 180)  # Steel
        crossguard_color = rgb_to_ursina_color(180, 140, 80)  # Brass
        handle_color = rgb_to_ursina_color(80, 50, 30)  # Dark leather
        has_glow = False
        glow_color = None
    elif rarity == c.RARITY_RARE:
        blade_color = rgb_to_ursina_color(200, 200, 210)  # Silver steel
        crossguard_color = rgb_to_ursina_color(192, 192, 192)  # Silver
        handle_color = rgb_to_ursina_color(100, 50, 50)  # Red leather
        has_glow = False
        glow_color = None
    elif rarity == c.RARITY_EPIC:
        blade_color = rgb_to_ursina_color(210, 210, 220)  # Bright steel
        crossguard_color = rgb_to_ursina_color(220, 180, 100)  # Gold
        handle_color = rgb_to_ursina_color(80, 40, 80)  # Purple
        has_glow = True
        glow_color = rgb_to_ursina_color(150, 100, 255)  # Purple glow
    else:  # LEGENDARY
        blade_color = rgb_to_ursina_color(220, 220, 240)  # Radiant steel
        crossguard_color = rgb_to_ursina_color(255, 215, 0)  # Bright gold
        handle_color = rgb_to_ursina_color(50, 20, 20)  # Black leather
        has_glow = True
        glow_color = rgb_to_ursina_color(100, 200, 255)  # Cyan glow

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
    blade_shader = get_shader_for_scale(0.45, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    blade = Entity(
        model='cube',
        color=blade_color,
        scale=(0.05, 0.45, 0.12),
        parent=sword,
        position=(0, 0.3, 0),
        shader=blade_shader
    )

    # Blade edge highlight (thin lighter cube on front)
    blade_edge_shader = get_shader_for_scale(0.45, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    blade_edge = Entity(
        model='cube',
        color=blade_color.tint(0.3),
        scale=(0.02, 0.45, 0.13),
        parent=blade,
        position=(0, 0, 0),
        shader=blade_edge_shader
    )

    # Crossguard (horizontal rectangle)
    crossguard_shader = get_shader_for_scale(0.25, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    crossguard = Entity(
        model='cube',
        color=crossguard_color,
        scale=(0.25, 0.04, 0.05),
        parent=sword,
        position=(0, 0.05, 0),
        shader=crossguard_shader
    )

    # Handle (vertical cylinder/cube)
    handle_shader = get_shader_for_scale(0.15, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    handle = Entity(
        model='cube',
        color=handle_color,
        scale=(0.05, 0.15, 0.05),
        parent=sword,
        position=(0, -0.08, 0),
        shader=handle_shader
    )

    # Pommel (sphere at bottom)
    pommel_shader = get_shader_for_scale(0.06, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    pommel = Entity(
        model='sphere',
        color=crossguard_color,
        scale=0.06,
        parent=sword,
        position=(0, -0.18, 0),
        shader=pommel_shader
    )

    # Gem on pommel for rare+ (small colored sphere)
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        gem_colors = {
            c.RARITY_RARE: rgb_to_ursina_color(100, 150, 255),  # Blue gem
            c.RARITY_EPIC: rgb_to_ursina_color(200, 50, 255),   # Purple gem
            c.RARITY_LEGENDARY: rgb_to_ursina_color(100, 255, 255),  # Cyan gem
        }
        gem_shader = get_shader_for_scale(0.04, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
        gem = Entity(
            model='sphere',
            color=gem_colors.get(rarity, ursina_color.white),
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
