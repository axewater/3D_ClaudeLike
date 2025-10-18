"""
Base utilities for 3D enemy model rendering

Shared functions for all enemy models.
"""

from ursina import Entity, Vec3, Text, color as ursina_color
import constants as c
from graphics3d.utils import qcolor_to_ursina_color, world_to_3d_position


def create_enemy_model_3d(enemy_type: str, position: Vec3) -> Entity:
    """
    Factory function to create enemy 3D models

    Args:
        enemy_type: Enemy type string (goblin, slime, skeleton, etc.)
        position: 3D world position

    Returns:
        Entity: Enemy 3D model
    """
    # Import enemy model creators
    from graphics3d.enemies.goblin import create_goblin_3d
    from graphics3d.enemies.slime import create_slime_3d
    from graphics3d.enemies.skeleton import create_skeleton_3d
    from graphics3d.enemies.orc import create_orc_3d
    from graphics3d.enemies.demon import create_demon_3d
    from graphics3d.enemies.dragon import create_dragon_3d

    # Get enemy color from constants
    enemy_colors = {
        c.ENEMY_GOBLIN: c.COLOR_ENEMY_GOBLIN,
        c.ENEMY_SLIME: c.COLOR_ENEMY_SLIME,
        c.ENEMY_SKELETON: c.COLOR_ENEMY_SKELETON,
        c.ENEMY_ORC: c.COLOR_ENEMY_ORC,
        c.ENEMY_DEMON: c.COLOR_ENEMY_DEMON,
        c.ENEMY_DRAGON: c.COLOR_ENEMY_DRAGON,
    }

    qcolor = enemy_colors.get(enemy_type, c.COLOR_ENEMY_GOBLIN)
    enemy_color = qcolor_to_ursina_color(qcolor)

    # Create model based on type
    if enemy_type == c.ENEMY_GOBLIN:
        return create_goblin_3d(position, enemy_color)
    elif enemy_type == c.ENEMY_SLIME:
        return create_slime_3d(position, enemy_color)
    elif enemy_type == c.ENEMY_SKELETON:
        return create_skeleton_3d(position, enemy_color)
    elif enemy_type == c.ENEMY_ORC:
        return create_orc_3d(position, enemy_color)
    elif enemy_type == c.ENEMY_DEMON:
        return create_demon_3d(position, enemy_color)
    elif enemy_type == c.ENEMY_DRAGON:
        return create_dragon_3d(position, enemy_color)
    else:
        # Fallback: generic cube
        return Entity(
            model='cube',
            color=enemy_color,
            scale=0.5,
            position=position
        )


def update_enemy_animation(enemy_entity: Entity, enemy_type: str, dt: float):
    """
    Update enemy idle animation based on type

    Args:
        enemy_entity: Enemy entity to animate
        enemy_type: Enemy type string
        dt: Delta time since last frame
    """
    # Import animation updaters
    from graphics3d.enemies.goblin import update_goblin_animation
    from graphics3d.enemies.slime import update_slime_animation
    from graphics3d.enemies.skeleton import update_skeleton_animation
    from graphics3d.enemies.orc import update_orc_animation
    from graphics3d.enemies.demon import update_demon_animation
    from graphics3d.enemies.dragon import update_dragon_animation

    # Route to appropriate animation function
    if enemy_type == c.ENEMY_GOBLIN:
        update_goblin_animation(enemy_entity, dt)
    elif enemy_type == c.ENEMY_SLIME:
        update_slime_animation(enemy_entity, dt)
    elif enemy_type == c.ENEMY_SKELETON:
        update_skeleton_animation(enemy_entity, dt)
    elif enemy_type == c.ENEMY_ORC:
        update_orc_animation(enemy_entity, dt)
    elif enemy_type == c.ENEMY_DEMON:
        update_demon_animation(enemy_entity, dt)
    elif enemy_type == c.ENEMY_DRAGON:
        update_dragon_animation(enemy_entity, dt)


def create_health_bar_billboard(hp_percentage: float) -> Entity:
    """
    Create a 3D health bar billboard above enemy

    Args:
        hp_percentage: Health percentage (0.0-1.0)

    Returns:
        Ursina Text entity representing the health bar
    """
    # Calculate filled vs empty portions (10 blocks total)
    filled = max(0, min(10, int(hp_percentage * 10)))
    empty = 10 - filled

    # Bar text using ASCII characters (# for filled, - for empty)
    bar_text = "#" * filled + "-" * empty

    # Determine color based on HP percentage
    if hp_percentage > 0.6:
        bar_color = ursina_color.rgb(80, 200, 120)  # Green
    elif hp_percentage > 0.3:
        bar_color = ursina_color.rgb(255, 193, 7)  # Yellow
    else:
        bar_color = ursina_color.rgb(244, 67, 54)  # Red

    # Create billboard text entity
    health_bar = Text(
        text=bar_text,
        scale=c.HEALTH_BAR_SCALE,  # Now 2.0 for better readability
        color=bar_color,
        origin=(0, 0),
        billboard=True,  # Always faces camera
        position=(0, c.HEALTH_BAR_OFFSET_Y, 0)  # Above enemy
    )

    return health_bar


def update_health_bar(health_bar: Entity, hp_percentage: float):
    """
    Update health bar text and color

    Args:
        health_bar: Health bar entity to update
        hp_percentage: New health percentage (0.0-1.0)
    """
    # Calculate filled vs empty portions
    filled = max(0, min(10, int(hp_percentage * 10)))
    empty = 10 - filled

    # Update text (# for filled, - for empty)
    health_bar.text = "#" * filled + "-" * empty

    # Update color
    if hp_percentage > 0.6:
        health_bar.color = ursina_color.rgb(80, 200, 120)  # Green
    elif hp_percentage > 0.3:
        health_bar.color = ursina_color.rgb(255, 193, 7)  # Yellow
    else:
        health_bar.color = ursina_color.rgb(244, 67, 54)  # Red
