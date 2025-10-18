"""
3D UI overlay module for Ursina-based 3D mode

This module provides UI widgets for the 3D mode using a unified Helmet HUD design:
- HelmetHUD3D: Unified, immersive HUD design consolidating all UI elements
  - Player stats (HP, XP, level, class, gold)
  - Equipment display (weapon, armor, accessory, boots)
  - Combat log with nearby items
  - Ability bar with cooldown indicators
  - Bottom status bar (attack, defense, depth, exploration)
- MiniMap3D: Miniature dungeon map with FOV visualization
- TargetingSystem: Mouse-based ability targeting
"""

from ui3d.helmet_hud import HelmetHUD3D
from ui3d.minimap_3d import MiniMap3D
from ui3d.targeting import TargetingSystem

__all__ = [
    'HelmetHUD3D',
    'MiniMap3D',
    'TargetingSystem',
]
