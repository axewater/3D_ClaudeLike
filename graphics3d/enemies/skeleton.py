"""
Skeleton 3D model - Undead bone creature

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import math
import random


def create_skeleton_3d(position: Vec3, enemy_color: ursina_color) -> Entity:
    """
    Create a 3D skeleton model

    Args:
        position: 3D world position
        enemy_color: Base color for the skeleton (white/bone)

    Returns:
        Entity: Skeleton model with all child entities
    """
    # Container entity (invisible parent)
    skeleton = Entity(position=position)

    bone_color = enemy_color  # White/bone color

    # Ribcage/torso (cube)
    torso = Entity(
        model='cube',
        color=bone_color,
        scale=(0.35, 0.5, 0.25),
        parent=skeleton,
        position=(0, 0.5, 0)
    )

    # Pelvis (smaller cube)
    pelvis = Entity(
        model='cube',
        color=bone_color,
        scale=(0.3, 0.2, 0.2),
        parent=skeleton,
        position=(0, 0.2, 0)
    )

    # Skull (sphere)
    skull = Entity(
        model='sphere',
        color=bone_color,
        scale=0.28,
        parent=skeleton,
        position=(0, 0.9, 0)
    )

    # Black eye sockets (left)
    left_socket = Entity(
        model='cube',
        color=ursina_color.rgb(0, 0, 0),
        scale=(0.08, 0.08, 0.05),
        parent=skull,
        position=(-0.1, 0.05, 0.15)
    )

    # Right eye socket
    right_socket = Entity(
        model='cube',
        color=ursina_color.rgb(0, 0, 0),
        scale=(0.08, 0.08, 0.05),
        parent=skull,
        position=(0.1, 0.05, 0.15)
    )

    # Glowing red eyes in sockets (spooky)
    left_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 50, 50),
        scale=0.04,
        parent=skull,
        position=(-0.1, 0.05, 0.18),
        unlit=True  # Emissive
    )

    right_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 50, 50),
        scale=0.04,
        parent=skull,
        position=(0.1, 0.05, 0.18),
        unlit=True
    )

    # Jaw (separate from skull)
    jaw = Entity(
        model='cube',
        color=bone_color,
        scale=(0.2, 0.08, 0.12),
        parent=skull,
        position=(0, -0.18, 0.05)
    )

    # Left arm (upper)
    left_arm_upper = Entity(
        model='cube',
        color=bone_color,
        scale=(0.08, 0.3, 0.08),
        parent=torso,
        position=(-0.25, 0.15, 0),
        rotation=(0, 0, 10)
    )

    # Left arm (lower)
    left_arm_lower = Entity(
        model='cube',
        color=bone_color,
        scale=(0.08, 0.25, 0.08),
        parent=left_arm_upper,
        position=(0, -0.28, 0),
        rotation=(0, 0, -5)
    )

    # Right arm (upper)
    right_arm_upper = Entity(
        model='cube',
        color=bone_color,
        scale=(0.08, 0.3, 0.08),
        parent=torso,
        position=(0.25, 0.15, 0),
        rotation=(0, 0, -10)
    )

    # Right arm (lower)
    right_arm_lower = Entity(
        model='cube',
        color=bone_color,
        scale=(0.08, 0.25, 0.08),
        parent=right_arm_upper,
        position=(0, -0.28, 0),
        rotation=(0, 0, 5)
    )

    # Left leg (upper)
    left_leg_upper = Entity(
        model='cube',
        color=bone_color,
        scale=(0.1, 0.3, 0.1),
        parent=pelvis,
        position=(-0.1, -0.25, 0)
    )

    # Left leg (lower)
    left_leg_lower = Entity(
        model='cube',
        color=bone_color,
        scale=(0.1, 0.25, 0.1),
        parent=left_leg_upper,
        position=(0, -0.28, 0)
    )

    # Right leg (upper)
    right_leg_upper = Entity(
        model='cube',
        color=bone_color,
        scale=(0.1, 0.3, 0.1),
        parent=pelvis,
        position=(0.1, -0.25, 0)
    )

    # Right leg (lower)
    right_leg_lower = Entity(
        model='cube',
        color=bone_color,
        scale=(0.1, 0.25, 0.1),
        parent=right_leg_upper,
        position=(0, -0.28, 0)
    )

    # Store animation state and references
    skeleton.idle_time = 0.0
    skeleton.torso_ref = torso
    skeleton.skull_ref = skull
    skeleton.jaw_ref = jaw
    skeleton.rattle_offset_x = random.uniform(-0.5, 0.5)
    skeleton.rattle_offset_y = random.uniform(-0.5, 0.5)

    return skeleton


def update_skeleton_animation(skeleton: Entity, dt: float):
    """
    Update skeleton idle animation (rattling/jittery movement)

    Args:
        skeleton: Skeleton entity to animate
        dt: Delta time since last frame
    """
    skeleton.idle_time += dt

    # Rattle animation (high frequency jitter)
    # Frequency: 10 Hz (very shaky/jittery)
    rattle_x = math.sin(skeleton.idle_time * 10.0 + skeleton.rattle_offset_x) * 0.01
    rattle_y = math.sin(skeleton.idle_time * 12.0 + skeleton.rattle_offset_y) * 0.01

    # Apply rattle to torso (body shaking)
    if hasattr(skeleton, 'torso_ref'):
        skeleton.torso_ref.x = rattle_x
        skeleton.torso_ref.y = 0.5 + rattle_y

    # Skull bobbing (separate from rattle)
    skull_bob = math.sin(skeleton.idle_time * 1.5) * 0.02

    if hasattr(skeleton, 'skull_ref'):
        skeleton.skull_ref.y = 0.9 + skull_bob

    # Jaw chatter (open/close slightly)
    if hasattr(skeleton, 'jaw_ref'):
        jaw_open = abs(math.sin(skeleton.idle_time * 8.0)) * 0.03
        skeleton.jaw_ref.y = -0.18 - jaw_open
