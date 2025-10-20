"""
Base utilities for 3D enemy model rendering

DNA creature factory and animation handling.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import world_to_3d_position


def create_enemy_model_3d(enemy_type: str, position: Vec3, dungeon_level: int = 1):
    """
    Factory function to create DNA creature enemies

    Args:
        enemy_type: Enemy type string (startle, slime, skeleton, orc, demon, dragon)
        position: 3D world position
        dungeon_level: Dungeon depth (1-25) for creature scaling

    Returns:
        Creature: DNA creature instance with procedural 3D model
    """
    try:
        from graphics3d.enemies.creature_factory import create_dna_creature
        creature = create_dna_creature(enemy_type, position, dungeon_level)
        return creature
    except Exception as e:
        # Fallback to simple cube if DNA creature creation fails
        print(f"⚠ DNA creature creation failed for {enemy_type}: {e}")
        import traceback
        traceback.print_exc()

        # Get enemy color from constants (RGB tuples 0-1 range)
        enemy_colors_rgb = {
            c.ENEMY_STARTLE: c.COLOR_ENEMY_STARTLE_RGB,
            c.ENEMY_SLIME: c.COLOR_ENEMY_SLIME_RGB,
            c.ENEMY_SKELETON: c.COLOR_ENEMY_SKELETON_RGB,
            c.ENEMY_ORC: c.COLOR_ENEMY_ORC_RGB,
            c.ENEMY_DEMON: c.COLOR_ENEMY_DEMON_RGB,
            c.ENEMY_DRAGON: c.COLOR_ENEMY_DRAGON_RGB,
        }

        rgb_tuple = enemy_colors_rgb.get(enemy_type, c.COLOR_ENEMY_STARTLE_RGB)
        fallback_color = ursina_color.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

        return Entity(
            model='cube',
            color=fallback_color,
            scale=0.5,
            position=position
        )


def update_enemy_animation(enemy_entity, enemy_type: str, dt: float, camera_position=None):
    """
    Update enemy idle animation

    Args:
        enemy_entity: DNA creature to animate
        enemy_type: Enemy type string (for logging only)
        dt: Delta time since last frame
        camera_position: Optional Vec3 camera position (for creature look-at)
    """
    # Check if this is a DNA creature (has update_animation method)
    if hasattr(enemy_entity, 'update_animation'):
        # DNA Creature - call its update_animation method
        import time
        try:
            enemy_entity.update_animation(time.time(), camera_position)
        except Exception as e:
            print(f"⚠ DNA creature animation error for {enemy_type}: {e}")
    # else: Fallback cube entities don't need animation


def create_health_bar_billboard(hp_percentage: float) -> Entity:
    """
    Create a 3D graphical health bar billboard above enemy

    Args:
        hp_percentage: Health percentage (0.0-1.0)

    Returns:
        Ursina Entity containing background and fill bar (graphical, not ASCII)
    """
    # Bar dimensions
    bar_width = 0.8
    bar_height = 0.1

    # Determine color based on HP percentage (0-1 float scale for Entity colors)
    if hp_percentage > 0.6:
        bar_color = ursina_color.rgb(0.31, 0.78, 0.47)  # Green (80, 200, 120 / 255)
    elif hp_percentage > 0.3:
        bar_color = ursina_color.rgb(1.0, 0.76, 0.03)  # Yellow (255, 193, 7 / 255)
    else:
        bar_color = ursina_color.rgb(0.96, 0.26, 0.21)  # Red (244, 67, 54 / 255)

    # Create parent container entity
    health_bar_container = Entity(
        position=(0, c.HEALTH_BAR_OFFSET_Y, 0),  # Above enemy
        billboard=True  # Always faces camera
    )

    # Background bar (dark gray)
    health_bar_bg = Entity(
        parent=health_bar_container,
        model='quad',
        color=ursina_color.rgb(0.12, 0.12, 0.12),  # Dark gray (30, 30, 30 / 255)
        scale=(bar_width, bar_height),
        position=(0, 0, 0.01),  # Slightly behind fill
        origin=(0, 0)
    )

    # Fill bar (colored, scales with HP)
    health_bar_fill = Entity(
        parent=health_bar_container,
        model='quad',
        color=bar_color,
        scale=(bar_width * hp_percentage, bar_height),  # Scale by HP
        position=(-bar_width / 2, 0, 0),  # Align left edge with background's left edge
        origin=(-0.5, 0)  # Left-aligned origin
    )

    # Store references in container for easy access during updates
    health_bar_container.background = health_bar_bg
    health_bar_container.fill = health_bar_fill
    health_bar_container.max_width = bar_width  # Store max width for updates

    return health_bar_container


def update_health_bar(health_bar: Entity, hp_percentage: float):
    """
    Update graphical health bar fill and color

    Args:
        health_bar: Health bar container entity (with fill and background)
        hp_percentage: New health percentage (0.0-1.0)
    """
    # Determine color based on HP percentage (0-1 float scale for Entity colors)
    if hp_percentage > 0.6:
        bar_color = ursina_color.rgb(0.31, 0.78, 0.47)  # Green (80, 200, 120 / 255)
    elif hp_percentage > 0.3:
        bar_color = ursina_color.rgb(1.0, 0.76, 0.03)  # Yellow (255, 193, 7 / 255)
    else:
        bar_color = ursina_color.rgb(0.96, 0.26, 0.21)  # Red (244, 67, 54 / 255)

    # Update fill bar scale and color
    if hasattr(health_bar, 'fill'):
        max_width = health_bar.max_width
        health_bar.fill.scale_x = max_width * hp_percentage
        # Position stays constant - only scale changes
        health_bar.fill.color = bar_color
