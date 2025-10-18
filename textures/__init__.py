"""
Procedural Texture Generation System

This module provides a clean API for generating procedural textures
using PIL/Pillow, designed for integration with Ursina Engine.

Port of the stunning procedural textures from ui/screens/title_screen_3d.py
(which uses QPainter) to PIL for use throughout the 3D game.

Quick Start:
    from textures import get_brick_texture, get_moss_stone_texture

    # Get a textured Ursina Texture
    wall_texture = get_moss_stone_texture(size=256, moss_density='heavy')
    entity = Entity(model='cube', texture=wall_texture)

Phases:
    Phase 1: Infrastructure - Base classes and utilities ✓
    Phase 2 (Current): Brick patterns ✓
    Phase 3 (Next): Organic effects (moss, weathering)
    Phase 4: Carved text/symbols
    Phase 5: Ursina integration and optimization
"""

from typing import Optional
from PIL import Image

# Export base classes and utilities
from .generator import (
    TextureGenerator,
    RandomSeed,
    blend_images,
    add_noise,
    darken_image,
    adjust_saturation
)

__all__ = [
    # Base classes
    'TextureGenerator',
    'RandomSeed',
    # Utilities
    'blend_images',
    'add_noise',
    'darken_image',
    'adjust_saturation',
    # Public API (texture generators)
    'get_brick_texture',
    'get_moss_stone_texture',
    'get_carved_texture',
    'get_weathered_texture',
    'get_ceiling_texture',
    'get_fog_of_war_texture',
]


# Public API - Texture Generation Functions
# These are stubs that will be implemented in later phases

def get_brick_texture(size: int = 256, darkness: float = 1.0):
    """Get brick pattern texture for Ursina.

    Generates a procedural brick wall texture with mortar lines,
    color variation, and realistic cracks.

    Args:
        size: Texture size in pixels (power of 2 recommended)
        darkness: Brightness multiplier (0.0 = black, 1.0 = normal, >1.0 = brighter)

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        wall = Entity(model='cube', texture=get_brick_texture(256, darkness=0.8))

    See Also:
        Reference implementation: ui/screens/title_screen_3d.py:238-284
    """
    from .bricks import generate_brick_pattern
    from ursina import Texture

    # Generate PIL image
    brick_image = generate_brick_pattern(size=size, darkness=darkness)

    # Convert to Ursina texture
    return Texture(brick_image)


def get_moss_stone_texture(size: int = 256, moss_density: str = 'heavy'):
    """Get moss-covered stone texture for Ursina.

    Generates a brick base with organic moss growth, including:
    - Dense moss coverage at top with irregular edges
    - Draping tendrils growing downward
    - Organic patches with satellite clusters
    - Color variation for realism

    Args:
        size: Texture size in pixels (power of 2 recommended)
        moss_density: Coverage amount - 'light', 'medium', or 'heavy'

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        dungeon_wall = Entity(
            model='cube',
            texture=get_moss_stone_texture(256, moss_density='heavy')
        )

    See Also:
        Reference implementation: ui/screens/title_screen_3d.py:303-567
    """
    from .organic import generate_moss_stone_texture
    from ursina import Texture

    # Generate PIL image
    moss_image = generate_moss_stone_texture(size=size, moss_density=moss_density)

    # Convert to Ursina texture
    return Texture(moss_image)


def get_carved_texture(char: str, size: int = 256, bg: str = 'moss_stone'):
    """Get texture with carved character/symbol.

    Generates a 3-layer carved effect (shadow, highlight, main) giving
    the illusion of depth, as if the character is carved into stone.

    Args:
        char: Single character to carve (letter, number, or symbol)
        size: Texture size in pixels (power of 2 recommended)
        bg: Background texture - 'moss_stone', 'brick', or 'plain'

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        letter_tile = Entity(
            model='cube',
            texture=get_carved_texture('A', size=256, bg='moss_stone')
        )

    Raises:
        NotImplementedError: Coming in Phase 4

    See Also:
        Reference implementation: ui/screens/title_screen_3d.py:592-651
    """
    raise NotImplementedError(
        "Carved textures coming in Phase 4!\n"
        "This will port the carved letter generation from title_screen_3d.py:592-651"
    )


def get_weathered_texture(size: int = 256, intensity: float = 1.0,
                          base_color: Optional[tuple] = None):
    """Get weathered/aged texture with stains and marks.

    Adds age marks, dark stains, and discoloration to create
    worn, ancient-looking surfaces.

    Args:
        size: Texture size in pixels (power of 2 recommended)
        intensity: Weathering strength (0.0 = none, 1.0 = heavy)
        base_color: Optional base color as (R, G, B) tuple, uses stone gray if None

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        aged_item = Entity(
            model='sphere',
            texture=get_weathered_texture(256, intensity=0.6)
        )

    See Also:
        Reference implementation: ui/screens/title_screen_3d.py:285-301
    """
    from .weathering import add_weathering
    from ursina import Texture

    # Default to stone gray if no base color specified
    if base_color is None:
        base_color = (100, 95, 90)  # Stone gray

    # Create base texture with solid color
    base_image = Image.new('RGBA', (size, size), base_color + (255,))

    # Apply weathering effects
    weathered_image = add_weathering(base_image, intensity=intensity)

    # Convert to Ursina texture
    return Texture(weathered_image)


def get_ceiling_texture(size: int = 256, moisture_level: str = 'medium'):
    """Get dungeon ceiling texture with hanging moss and water damage.

    Generates a realistic ceiling with:
    - Dark weathered stone base
    - Sparse hanging moss strands
    - Water stains and mineral deposits
    - Overall darker tone (less light reaches ceiling)

    Args:
        size: Texture size in pixels (power of 2 recommended)
        moisture_level: Water damage amount - 'low', 'medium', or 'high'

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        ceiling = Entity(
            model='plane',
            texture=get_ceiling_texture(256, moisture_level='high'),
            rotation_x=180  # Flip to face downward
        )
    """
    from .organic import generate_ceiling_texture
    from ursina import Texture

    # Generate PIL image
    ceiling_image = generate_ceiling_texture(size=size, moisture_level=moisture_level)

    # Convert to Ursina texture
    return Texture(ceiling_image)


def get_fog_of_war_texture(size: int = 512):
    """Get animated fog-of-war texture for unexplored areas.

    Generates a procedural fog texture with:
    - Grey/white cloud-like base
    - Purple and black swirling circles
    - Large, clear features visible at distance
    - Designed for UV scrolling animation

    Args:
        size: Texture size in pixels (512+ recommended for clarity)

    Returns:
        ursina.Texture object ready for use with Entity

    Example:
        fog_plane = Entity(
            model='plane',
            texture=get_fog_of_war_texture(512),
            alpha=0.7,
            position=(x, 0.1, y)  # Slightly above floor
        )
    """
    from .fog_of_war import get_fog_of_war_texture as _get_fog
    return _get_fog(size=size)


# Version info
__version__ = '0.2.0-phase2'
__author__ = 'Claude-Like Roguelike Project'
