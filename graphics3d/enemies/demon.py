"""
Demon 3D model - Infernal winged creature

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color, Mesh
import math


def create_demon_3d(position: Vec3, enemy_color: ursina_color) -> Entity:
    """
    Create a 3D demon model

    Args:
        position: 3D world position
        enemy_color: Base color for the demon (purple/dark red)

    Returns:
        Entity: Demon model with all child entities
    """
    # Container entity (invisible parent)
    demon = Entity(position=position)

    # Muscular humanoid body
    body = Entity(
        model='cube',
        color=enemy_color,
        scale=(0.4, 0.65, 0.35),
        parent=demon,
        position=(0, 0.6, 0)
    )

    # Head with menacing features
    head = Entity(
        model='sphere',
        color=enemy_color.tint(0.1),
        scale=0.32,
        parent=demon,
        position=(0, 1.05, 0)
    )

    # Glowing red demon eyes (intense)
    left_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 0, 0),
        scale=0.08,
        parent=head,
        position=(-0.1, 0.05, 0.18),
        unlit=True  # Emissive glow
    )

    right_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 0, 0),
        scale=0.08,
        parent=head,
        position=(0.1, 0.05, 0.18),
        unlit=True
    )

    # Curved horns pointing up and back
    # Left horn
    left_horn = Entity(
        model='cube',
        color=ursina_color.rgb(40, 20, 20),
        scale=(0.08, 0.3, 0.08),
        parent=head,
        position=(-0.15, 0.2, -0.05),
        rotation=(30, 0, -15)
    )

    # Right horn
    right_horn = Entity(
        model='cube',
        color=ursina_color.rgb(40, 20, 20),
        scale=(0.08, 0.3, 0.08),
        parent=head,
        position=(0.15, 0.2, -0.05),
        rotation=(30, 0, 15)
    )

    # Left wing (triangular shape using cube stretched and rotated)
    left_wing = Entity(
        model='cube',
        color=enemy_color.tint(-0.3),
        scale=(0.6, 0.02, 0.35),
        parent=body,
        position=(-0.4, 0.2, -0.1),
        rotation=(0, 30, 0),
        alpha=0.9  # Slightly translucent membrane
    )

    # Left wing frame/bone (darker outline)
    left_wing_bone = Entity(
        model='cube',
        color=enemy_color.tint(-0.5),
        scale=(0.62, 0.01, 0.05),
        parent=left_wing,
        position=(0, 0, 0)
    )

    # Right wing
    right_wing = Entity(
        model='cube',
        color=enemy_color.tint(-0.3),
        scale=(0.6, 0.02, 0.35),
        parent=body,
        position=(0.4, 0.2, -0.1),
        rotation=(0, -30, 0),
        alpha=0.9
    )

    # Right wing frame/bone
    right_wing_bone = Entity(
        model='cube',
        color=enemy_color.tint(-0.5),
        scale=(0.62, 0.01, 0.05),
        parent=right_wing,
        position=(0, 0, 0)
    )

    # Clawed arms
    left_arm = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.12, 0.45, 0.12),
        parent=body,
        position=(-0.3, 0.1, 0),
        rotation=(0, 0, 20)
    )

    right_arm = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.12, 0.45, 0.12),
        parent=body,
        position=(0.3, 0.1, 0),
        rotation=(0, 0, -20)
    )

    # Legs
    left_leg = Entity(
        model='cube',
        color=enemy_color.tint(-0.1),
        scale=(0.15, 0.5, 0.15),
        parent=demon,
        position=(-0.12, 0.15, 0)
    )

    right_leg = Entity(
        model='cube',
        color=enemy_color.tint(-0.1),
        scale=(0.15, 0.5, 0.15),
        parent=demon,
        position=(0.12, 0.15, 0)
    )

    # Store animation state and references
    demon.idle_time = 0.0
    demon.left_wing_ref = left_wing
    demon.right_wing_ref = right_wing

    return demon


def update_demon_animation(demon: Entity, dt: float):
    """
    Update demon idle animation (wing flapping)

    Args:
        demon: Demon entity to animate
        dt: Delta time since last frame
    """
    demon.idle_time += dt

    # Wing flap animation (slow ominous flapping)
    # Frequency: 1.2 Hz
    flap_angle = math.sin(demon.idle_time * 1.2) * 20.0  # ±20 degrees

    if hasattr(demon, 'left_wing_ref'):
        # Left wing rotates up/down
        base_rotation_y = 30
        demon.left_wing_ref.rotation_y = base_rotation_y + flap_angle

    if hasattr(demon, 'right_wing_ref'):
        # Right wing rotates opposite direction
        base_rotation_y = -30
        demon.right_wing_ref.rotation_y = base_rotation_y - flap_angle
