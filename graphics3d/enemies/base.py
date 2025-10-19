"""
Base utilities for 3D enemy model rendering

Shared functions for all enemy models.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import world_to_3d_position


def create_enemy_model_3d(enemy_type: str, position: Vec3, dungeon_level: int = 1, use_dna_creatures: bool = True):
    """
    Factory function to create enemy 3D models

    Args:
        enemy_type: Enemy type string (goblin, slime, skeleton, etc.)
        position: 3D world position
        dungeon_level: Dungeon depth (1-25) for DNA creature scaling
        use_dna_creatures: If True, use DNA editor creatures; if False, use legacy models

    Returns:
        Entity or Creature: Enemy 3D model (returns creature object for DNA, Entity for legacy)
    """
    # DNA CREATURES: Use procedural creatures from DNA editor with level scaling
    if use_dna_creatures:
        try:
            from graphics3d.enemies.creature_factory import create_dna_creature
            creature = create_dna_creature(enemy_type, position, dungeon_level)
            return creature
        except Exception as e:
            print(f"⚠ DNA creature creation failed, falling back to legacy: {e}")
            # Fall through to legacy models below

    # LEGACY MODELS: Original procedural models (no level scaling)
    # Import enemy model creators
    from graphics3d.enemies.goblin import create_goblin_3d
    from graphics3d.enemies.slime import create_slime_3d
    from graphics3d.enemies.skeleton import create_skeleton_3d
    from graphics3d.enemies.orc import create_orc_3d
    from graphics3d.enemies.demon import create_demon_3d
    from graphics3d.enemies.dragon import create_dragon_3d

    # Get enemy color from constants (RGB tuples)
    enemy_colors_rgb = {
        c.ENEMY_GOBLIN: c.COLOR_ENEMY_GOBLIN_RGB,
        c.ENEMY_SLIME: c.COLOR_ENEMY_SLIME_RGB,
        c.ENEMY_SKELETON: c.COLOR_ENEMY_SKELETON_RGB,
        c.ENEMY_ORC: c.COLOR_ENEMY_ORC_RGB,
        c.ENEMY_DEMON: c.COLOR_ENEMY_DEMON_RGB,
        c.ENEMY_DRAGON: c.COLOR_ENEMY_DRAGON_RGB,
    }

    rgb_tuple = enemy_colors_rgb.get(enemy_type, c.COLOR_ENEMY_GOBLIN_RGB)
    enemy_color = ursina_color.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

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


def update_enemy_animation(enemy_entity, enemy_type: str, dt: float, camera_position=None):
    """
    Update enemy idle animation based on type

    Args:
        enemy_entity: Enemy entity or creature to animate
        enemy_type: Enemy type string
        dt: Delta time since last frame
        camera_position: Optional Vec3 camera position (for DNA creatures)
    """
    # Check if this is a DNA creature (has update_animation method)
    if hasattr(enemy_entity, 'update_animation'):
        # DNA Creature - call its update_animation method
        import time
        try:
            enemy_entity.update_animation(time.time(), camera_position)
        except Exception as e:
            print(f"⚠ DNA creature animation error: {e}")
        return

    # LEGACY MODELS: Use old animation system
    # Check if this is a proper legacy model (has required attributes)
    # Fallback entities from failed creature creation won't have these
    if not hasattr(enemy_entity, 'idle_time'):
        # Skip animation for fallback entities (simple cubes from failed creature creation)
        return

    # Import animation updaters
    from graphics3d.enemies.goblin import update_goblin_animation
    from graphics3d.enemies.slime import update_slime_animation
    from graphics3d.enemies.skeleton import update_skeleton_animation
    from graphics3d.enemies.orc import update_orc_animation
    from graphics3d.enemies.demon import update_demon_animation
    from graphics3d.enemies.dragon import update_dragon_animation

    # Route to appropriate animation function
    try:
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
    except Exception as e:
        print(f"⚠ Legacy animation error for {enemy_type}: {e}")


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
