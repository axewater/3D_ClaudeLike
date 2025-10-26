"""
Treasure Chest 3D model - High-value collectible currency item

Procedurally generated 3D model using Ursina primitives.
Treasure chests contain gold piles and award 10x the value of gold coins.
"""

from ursina import Entity, Vec3
import constants as c
from graphics3d.utils import rgb_to_ursina_color

# Import toon shader system
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add dna_editor to path
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.insert(0, dna_editor_path)

from dna_editor.shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale


def create_treasure_chest_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D treasure chest model with rarity-based gold pile appearance

    Args:
        position: 3D world position
        rarity: Item rarity (affects gold color and value)

    Returns:
        Entity: Treasure chest 3D model
    """
    # Create toon shader instances (shared across all chest components)
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Container entity (invisible parent)
    chest = Entity(position=position)

    # Rarity-based gold colors (same as coins)
    if rarity == c.RARITY_COMMON:
        gold_color = rgb_to_ursina_color(255, 215, 0)  # Standard gold
        shine_color = rgb_to_ursina_color(255, 235, 100)  # Bright center
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        gold_color = rgb_to_ursina_color(255, 225, 50)  # Brighter gold
        shine_color = rgb_to_ursina_color(255, 245, 150)
        has_glow = False
    elif rarity == c.RARITY_RARE:
        gold_color = rgb_to_ursina_color(255, 235, 100)  # Very bright gold
        shine_color = rgb_to_ursina_color(255, 255, 200)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)
    elif rarity == c.RARITY_EPIC:
        gold_color = rgb_to_ursina_color(255, 200, 255)  # Golden magenta
        shine_color = rgb_to_ursina_color(255, 230, 255)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 150, 255)
    else:  # LEGENDARY
        gold_color = rgb_to_ursina_color(255, 255, 255)  # Brilliant white gold
        shine_color = rgb_to_ursina_color(255, 255, 255)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)

    # Glow for rare+ chests
    if has_glow:
        glow = Entity(
            model='cube',
            color=glow_color,
            scale=(0.5, 0.3, 0.4),
            parent=chest,
            position=(0, 0, 0),
            alpha=0.4,
            unlit=True
        )

    # Outer chest box (brown rectangle)
    brown_color = rgb_to_ursina_color(139, 90, 43)  # Brown (0-255 scale)
    chest_shader = get_shader_for_scale(0.25, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    chest_outer = Entity(
        model='cube',
        color=brown_color,
        scale=(0.4, 0.25, 0.3),  # Wide, short, deep box
        parent=chest,
        position=(0, 0, 0),
        shader=chest_shader
    )

    # Inner empty space (black rectangle) - slightly smaller and raised
    black_color = rgb_to_ursina_color(20, 20, 20)  # Dark gray/black
    chest_inner = Entity(
        model='cube',
        color=black_color,
        scale=(0.36, 0.15, 0.26),  # Slightly smaller than outer
        parent=chest,
        position=(0, 0.08, 0),  # Raised up to show opening
        unlit=True
    )

    # Gold pile - multiple small flattened spheres on top
    # Front row - 3 coins
    gold_positions = [
        (-0.1, 0.15, 0.05),  # Left front
        (0.0, 0.15, 0.05),   # Center front
        (0.1, 0.15, 0.05),   # Right front
        # Back row - 2 coins
        (-0.05, 0.18, -0.05), # Left back (higher)
        (0.05, 0.18, -0.05),  # Right back (higher)
    ]

    # Create shader for gold coins (using lite shader for small objects)
    gold_coin_shader = get_shader_for_scale(0.02, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

    for pos in gold_positions:
        # Main gold coin
        gold_coin = Entity(
            model='sphere',
            color=gold_color,
            scale=(0.08, 0.02, 0.08),  # Wide and very flat (squashed)
            parent=chest,
            position=pos,
            shader=gold_coin_shader
        )

        # Shine on each coin (keep unlit - no shader)
        gold_shine = Entity(
            model='sphere',
            color=shine_color,
            scale=(0.05, 0.025, 0.05),  # Smaller bright spot
            parent=chest,
            position=pos,
            unlit=True
        )

    # Store animation state
    chest.float_time = 0.0
    chest.rotation_speed = 30.0  # Slow rotation to show it's a chest

    return chest
