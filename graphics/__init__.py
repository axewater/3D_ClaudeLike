"""
Graphics rendering package for Claude-Like

This package contains all rendering functions organized by category.
Exports all functions for backward compatibility with the original graphics.py module.
"""

# Import utility functions
from graphics.utils import apply_fog_color

# Import tile rendering functions
from graphics.tiles import (
    draw_wall_tile,
    draw_floor_tile,
    draw_stairs_tile,
)

# Import entity rendering functions
from graphics.players import draw_player  # Now imports from players/ package
from graphics.enemies import draw_enemy  # Now imports from enemies/ package
from graphics.items import draw_item  # Now imports from items/ package

# Import ability icon rendering functions
from graphics.ability_icons import (
    draw_ability_fireball,
    draw_ability_dash,
    draw_ability_healing,
    draw_ability_frost,
    draw_ability_whirlwind,
    draw_ability_shadow,
)

# Export all for backward compatibility
__all__ = [
    # Utilities
    'apply_fog_color',
    # Tiles
    'draw_wall_tile',
    'draw_floor_tile',
    'draw_stairs_tile',
    # Entities
    'draw_player',
    'draw_enemy',
    'draw_item',
    # Ability icons
    'draw_ability_fireball',
    'draw_ability_dash',
    'draw_ability_healing',
    'draw_ability_frost',
    'draw_ability_whirlwind',
    'draw_ability_shadow',
]
