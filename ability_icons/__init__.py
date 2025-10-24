"""
Procedural Ability Icon Generation System

This package provides a complete system for generating animated ability icons
for the roguelike game. Icons are procedurally generated using PIL and cached
to disk for fast loading on subsequent runs.

Usage:
    from ability_icons import generate_all_ability_frames

    # Generate all ability animations (returns dict of PIL Images)
    ability_frames = generate_all_ability_frames()

    # Access specific ability frames
    fireball_frames = ability_frames["Fireball"]  # List of 8 frames

Features:
- 6 unique abilities with distinct visual styles
- 8-frame animations (loopable)
- 256x256 resolution optimized for UI display
- Deterministic generation using seeds
- Combines swirling energy, elemental symbols, and particle effects

Architecture:
- generator.py: Base infrastructure and utilities
- effects.py: Animated effects (vortexes, particles, etc.)
- symbols.py: Elemental symbols (fire, ice, etc.)
- animations.py: Complete ability animation generation
"""

# Public API
from ability_icons.animations import (
    generate_all_ability_frames,
    generate_fireball_frames,
    generate_frost_nova_frames,
    generate_heal_frames,
    generate_dash_frames,
    generate_shadow_step_frames,
    generate_whirlwind_frames,
    ICON_SIZE,
    TOTAL_FRAMES
)

__all__ = [
    'generate_all_ability_frames',
    'generate_fireball_frames',
    'generate_frost_nova_frames',
    'generate_heal_frames',
    'generate_dash_frames',
    'generate_shadow_step_frames',
    'generate_whirlwind_frames',
    'ICON_SIZE',
    'TOTAL_FRAMES',
]

__version__ = '1.0.0'
