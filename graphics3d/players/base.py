"""
Base utilities for 3D player model rendering

Shared functions for all player class models.
"""


def apply_idle_animation(entity, idle_time: float):
    """
    Apply breathing/bobbing idle animation to player model

    Args:
        entity: Ursina Entity to animate
        idle_time: Current idle time for animation cycle
    """
    pass


def apply_walk_animation(entity, walk_progress: float):
    """
    Apply walking animation to player model

    Args:
        entity: Ursina Entity to animate
        walk_progress: Progress of walk cycle (0.0-1.0)
    """
    pass


def apply_attack_animation(entity, attack_progress: float):
    """
    Apply attack animation to player model

    Args:
        entity: Ursina Entity to animate
        attack_progress: Progress of attack animation (0.0-1.0)
    """
    pass


def set_facing_direction(entity, direction_x: float, direction_y: float):
    """
    Rotate player model to face a direction

    Args:
        entity: Ursina Entity to rotate
        direction_x: X component of facing direction
        direction_y: Y component of facing direction (becomes Z in 3D)
    """
    pass
