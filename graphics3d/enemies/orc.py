"""
Orc 3D model - Large brutish warrior

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import math


def create_orc_3d(position: Vec3, enemy_color: ursina_color) -> Entity:
    """
    Create a 3D orc model

    Args:
        position: 3D world position
        enemy_color: Base color for the orc (dark green)

    Returns:
        Entity: Orc model with all child entities
    """
    # Container entity (invisible parent)
    orc = Entity(position=position)

    # Large bulky body
    body = Entity(
        model='cube',
        color=enemy_color,
        scale=(0.5, 0.7, 0.4),
        parent=orc,
        position=(0, 0.5, 0)
    )

    # Dark leather/metal armor overlay on torso
    armor = Entity(
        model='cube',
        color=enemy_color.tint(-0.3),
        scale=(0.48, 0.5, 0.38),
        parent=body,
        position=(0, 0.1, 0)
    )

    # Large head
    head = Entity(
        model='sphere',
        color=enemy_color.tint(0.1),
        scale=0.35,
        parent=orc,
        position=(0, 1.0, 0)
    )

    # Protruding tusks (white cones)
    # Left tusk
    left_tusk = Entity(
        model='cube',
        color=ursina_color.rgb(240, 235, 220),
        scale=(0.05, 0.15, 0.05),
        parent=head,
        position=(-0.08, -0.1, 0.18),
        rotation=(30, 0, -10)
    )

    # Right tusk
    right_tusk = Entity(
        model='cube',
        color=ursina_color.rgb(240, 235, 220),
        scale=(0.05, 0.15, 0.05),
        parent=head,
        position=(0.08, -0.1, 0.18),
        rotation=(30, 0, 10)
    )

    # Angry red eyes
    left_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(200, 0, 0),
        scale=0.06,
        parent=head,
        position=(-0.1, 0.05, 0.18),
        unlit=True
    )

    right_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(200, 0, 0),
        scale=0.06,
        parent=head,
        position=(0.1, 0.05, 0.18),
        unlit=True
    )

    # Thick muscular arms
    left_arm = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.15, 0.5, 0.15),
        parent=body,
        position=(-0.35, 0.1, 0),
        rotation=(0, 0, 15)
    )

    right_arm = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.15, 0.5, 0.15),
        parent=body,
        position=(0.35, 0.1, 0),
        rotation=(0, 0, -15)
    )

    # Large axe weapon (in right hand)
    axe_handle = Entity(
        model='cube',
        color=ursina_color.rgb(80, 50, 30),
        scale=(0.06, 0.45, 0.06),
        parent=right_arm,
        position=(0, -0.3, 0.1),
        rotation=(45, 0, 0)
    )

    # Axe head (gray metal)
    axe_head = Entity(
        model='cube',
        color=ursina_color.rgb(120, 120, 130),
        scale=(0.25, 0.15, 0.05),
        parent=axe_handle,
        position=(0, 0.3, 0)
    )

    # Axe blade edge (darker)
    axe_blade = Entity(
        model='cube',
        color=ursina_color.rgb(80, 80, 90),
        scale=(0.28, 0.02, 0.02),
        parent=axe_head,
        position=(0, 0.08, 0)
    )

    # Legs
    left_leg = Entity(
        model='cube',
        color=enemy_color.tint(-0.1),
        scale=(0.18, 0.45, 0.18),
        parent=orc,
        position=(-0.15, 0.05, 0)
    )

    right_leg = Entity(
        model='cube',
        color=enemy_color.tint(-0.1),
        scale=(0.18, 0.45, 0.18),
        parent=orc,
        position=(0.15, 0.05, 0)
    )

    # Store animation state and references
    orc.idle_time = 0.0
    orc.body_ref = body
    orc.armor_ref = armor
    orc.base_scale = 0.7

    return orc


def update_orc_animation(orc: Entity, dt: float):
    """
    Update orc idle animation (heavy breathing, imposing presence)

    Args:
        orc: Orc entity to animate
        dt: Delta time since last frame
    """
    orc.idle_time += dt

    # Heavy breathing (slow scale pulse)
    # Frequency: 0.8 Hz (slow, heavy breaths)
    breath_factor = math.sin(orc.idle_time * 0.8) * 0.04

    if hasattr(orc, 'body_ref'):
        # Body expands/contracts with breathing
        new_scale_y = orc.base_scale + breath_factor
        orc.body_ref.scale_y = new_scale_y

    # Armor scales with body
    if hasattr(orc, 'armor_ref'):
        armor_scale = 0.5 + breath_factor
        orc.armor_ref.scale_y = armor_scale
