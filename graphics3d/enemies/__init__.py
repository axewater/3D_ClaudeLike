"""
3D enemy model rendering package

DNA creature factory for procedurally generated enemies with animations and health bars.
All enemies use the DNA editor system for level-scaled complexity.
"""

from graphics3d.enemies.base import (
    create_enemy_model_3d,
    update_enemy_animation,
    create_health_bar_billboard,
    update_health_bar,
)

__all__ = [
    'create_enemy_model_3d',
    'update_enemy_animation',
    'create_health_bar_billboard',
    'update_health_bar',
]
