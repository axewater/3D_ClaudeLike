"""
Dragon 3D model - Massive winged serpent

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import math


def create_dragon_3d(position: Vec3, enemy_color: ursina_color) -> Entity:
    """
    Create a 3D dragon model

    Args:
        position: 3D world position
        enemy_color: Base color for the dragon (red)

    Returns:
        Entity: Dragon model with all child entities
    """
    # Container entity (invisible parent)
    dragon = Entity(position=position)

    # Elongated serpentine body (main torso)
    body = Entity(
        model='cube',
        color=enemy_color,
        scale=(0.6, 0.7, 0.5),
        parent=dragon,
        position=(0, 0.6, 0)
    )

    # Neck (connecting head to body)
    neck = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.25, 0.4, 0.25),
        parent=body,
        position=(0, 0.45, 0.15),
        rotation=(-20, 0, 0)
    )

    # Large reptilian head (pyramid-like)
    head = Entity(
        model='cube',
        color=enemy_color.tint(0.1),
        scale=(0.35, 0.35, 0.45),
        parent=neck,
        position=(0, 0.3, 0.1)
    )

    # Snout (elongated front)
    snout = Entity(
        model='cube',
        color=enemy_color.tint(-0.05),
        scale=(0.2, 0.15, 0.25),
        parent=head,
        position=(0, -0.05, 0.3)
    )

    # Fierce glowing yellow/orange eyes
    left_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 180, 0),
        scale=0.1,
        parent=head,
        position=(-0.12, 0.08, 0.25),
        unlit=True  # Emissive glow
    )

    right_eye = Entity(
        model='sphere',
        color=ursina_color.rgb(255, 180, 0),
        scale=0.1,
        parent=head,
        position=(0.12, 0.08, 0.25),
        unlit=True
    )

    # Sharp teeth (small white cones along jaw)
    for i in range(4):
        tooth_left = Entity(
            model='cube',
            color=ursina_color.rgb(240, 240, 220),
            scale=(0.04, 0.08, 0.04),
            parent=snout,
            position=(-0.08 + i * 0.05, -0.08, 0.15),
            rotation=(20, 0, 0)
        )
        tooth_right = Entity(
            model='cube',
            color=ursina_color.rgb(240, 240, 220),
            scale=(0.04, 0.08, 0.04),
            parent=snout,
            position=(0.08 - i * 0.05, -0.08, 0.15),
            rotation=(20, 0, 0)
        )

    # Horns/spikes on head
    left_horn = Entity(
        model='cube',
        color=ursina_color.rgb(100, 50, 50),
        scale=(0.08, 0.25, 0.08),
        parent=head,
        position=(-0.15, 0.2, 0),
        rotation=(10, 0, -20)
    )

    right_horn = Entity(
        model='cube',
        color=ursina_color.rgb(100, 50, 50),
        scale=(0.08, 0.25, 0.08),
        parent=head,
        position=(0.15, 0.2, 0),
        rotation=(10, 0, 20)
    )

    # Massive wings
    # Left wing (large triangular membrane)
    left_wing = Entity(
        model='cube',
        color=enemy_color.tint(-0.2),
        scale=(0.9, 0.03, 0.6),
        parent=body,
        position=(-0.6, 0.2, 0),
        rotation=(0, 20, -10),
        alpha=0.85
    )

    # Left wing bones/frame
    left_wing_bone1 = Entity(
        model='cube',
        color=enemy_color.tint(-0.4),
        scale=(0.9, 0.02, 0.06),
        parent=left_wing,
        position=(0, 0, 0)
    )

    left_wing_bone2 = Entity(
        model='cube',
        color=enemy_color.tint(-0.4),
        scale=(0.8, 0.02, 0.06),
        parent=left_wing,
        position=(0, 0, -0.15),
        rotation=(0, -10, 0)
    )

    # Right wing
    right_wing = Entity(
        model='cube',
        color=enemy_color.tint(-0.2),
        scale=(0.9, 0.03, 0.6),
        parent=body,
        position=(0.6, 0.2, 0),
        rotation=(0, -20, 10),
        alpha=0.85
    )

    # Right wing bones/frame
    right_wing_bone1 = Entity(
        model='cube',
        color=enemy_color.tint(-0.4),
        scale=(0.9, 0.02, 0.06),
        parent=right_wing,
        position=(0, 0, 0)
    )

    right_wing_bone2 = Entity(
        model='cube',
        color=enemy_color.tint(-0.4),
        scale=(0.8, 0.02, 0.06),
        parent=right_wing,
        position=(0, 0, -0.15),
        rotation=(0, 10, 0)
    )

    # Segmented tail (series of shrinking cubes)
    tail_segments = []
    tail_length = 5
    for i in range(tail_length):
        scale_factor = 1.0 - (i * 0.15)  # Shrink as we go back
        segment = Entity(
            model='cube',
            color=enemy_color.tint(-i * 0.05),
            scale=(0.2 * scale_factor, 0.2 * scale_factor, 0.25),
            parent=tail_segments[i-1] if i > 0 else body,
            position=(0, -0.05 * i, -0.3 if i == 0 else -0.25),
            rotation=(5 * i, 0, 0) if i > 0 else (0, 0, 0)
        )
        tail_segments.append(segment)

    # Tail spike at the end
    tail_spike = Entity(
        model='cube',
        color=ursina_color.rgb(100, 50, 50),
        scale=(0.1, 0.15, 0.1),
        parent=tail_segments[-1],
        position=(0, 0, -0.15),
        rotation=(30, 0, 0)
    )

    # Powerful legs
    left_leg_front = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.18, 0.45, 0.18),
        parent=body,
        position=(-0.25, -0.4, 0.1)
    )

    right_leg_front = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.18, 0.45, 0.18),
        parent=body,
        position=(0.25, -0.4, 0.1)
    )

    left_leg_back = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.18, 0.45, 0.18),
        parent=body,
        position=(-0.25, -0.4, -0.15)
    )

    right_leg_back = Entity(
        model='cube',
        color=enemy_color.tint(0.05),
        scale=(0.18, 0.45, 0.18),
        parent=body,
        position=(0.25, -0.4, -0.15)
    )

    # Store animation state and references
    dragon.idle_time = 0.0
    dragon.left_wing_ref = left_wing
    dragon.right_wing_ref = right_wing
    dragon.tail_segments_ref = tail_segments
    dragon.neck_ref = neck

    return dragon


def update_dragon_animation(dragon: Entity, dt: float):
    """
    Update dragon idle animation (wing spread + tail sway + breathing)

    Args:
        dragon: Dragon entity to animate
        dt: Delta time since last frame
    """
    dragon.idle_time += dt

    # Wing spreading (slow majestic flaps)
    # Frequency: 0.6 Hz (very slow, powerful)
    wing_spread = math.sin(dragon.idle_time * 0.6) * 15.0  # ±15 degrees

    if hasattr(dragon, 'left_wing_ref'):
        base_rotation_y = 20
        dragon.left_wing_ref.rotation_y = base_rotation_y + wing_spread
        dragon.left_wing_ref.rotation_z = -10 + (wing_spread * 0.3)

    if hasattr(dragon, 'right_wing_ref'):
        base_rotation_y = -20
        dragon.right_wing_ref.rotation_y = base_rotation_y - wing_spread
        dragon.right_wing_ref.rotation_z = 10 - (wing_spread * 0.3)

    # Tail sway (serpentine movement)
    if hasattr(dragon, 'tail_segments_ref'):
        for i, segment in enumerate(dragon.tail_segments_ref):
            # Each segment sways with increasing amplitude and phase shift
            sway_offset = i * 0.3  # Phase shift for wave propagation
            sway_angle = math.sin(dragon.idle_time * 1.5 + sway_offset) * (8.0 + i * 2.0)
            segment.rotation_y = sway_angle

    # Neck breathing (subtle up/down)
    if hasattr(dragon, 'neck_ref'):
        neck_bob = math.sin(dragon.idle_time * 0.8) * 2.0
        dragon.neck_ref.rotation_x = -20 + neck_bob
