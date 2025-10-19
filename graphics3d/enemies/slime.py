"""
Slime 3D model - Gelatinous blob creature

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import math


def create_slime_3d(position: Vec3, enemy_color: ursina_color) -> Entity:
    """
    Create a 3D slime model with enhanced gelatinous appearance

    Args:
        position: 3D world position
        enemy_color: Base color for the slime (cyan/teal)

    Returns:
        Entity: Slime model with all child entities
    """
    # Container entity (invisible parent)
    slime = Entity(position=position)

    # ENHANCEMENT #1: Multi-layer gelatinous appearance
    # Outer rim layer (bright rim lighting effect)
    outer_rim = Entity(
        model='sphere',
        color=enemy_color.tint(0.4),
        scale=(0.53, 0.48, 0.53),  # Slightly larger than body
        parent=slime,
        position=(0, 0.3, 0),
        alpha=0.3  # Very transparent for rim glow
    )

    # Main body (semi-transparent sphere)
    body = Entity(
        model='sphere',
        color=enemy_color,
        scale=(0.5, 0.45, 0.5),  # Slightly flattened sphere
        parent=slime,
        position=(0, 0.3, 0),
        alpha=0.75  # Slightly more transparent for depth
    )

    # Middle layer (slightly darker for depth)
    middle_layer = Entity(
        model='sphere',
        color=enemy_color.tint(-0.2),
        scale=0.35,
        parent=body,
        position=(0, 0, 0),
        alpha=0.5
    )

    # Inner core (glowing darker sphere inside)
    core = Entity(
        model='sphere',
        color=enemy_color.tint(-0.4),
        scale=0.25,
        parent=body,
        position=(0, 0, 0),
        alpha=0.7,
        unlit=True  # Glowing core
    )

    # Surface highlights (wet shiny look) - 5 small bright spots
    highlight_color = ursina_color.rgb(255, 255, 255)
    highlight_positions = [
        (0.15, 0.15, 0.18),
        (-0.1, 0.12, 0.2),
        (0.08, -0.08, 0.22),
        (-0.18, -0.05, 0.15),
        (0.02, 0.2, 0.19)
    ]

    highlights = []
    for pos in highlight_positions:
        highlight = Entity(
            model='sphere',
            color=highlight_color,
            scale=0.04,
            parent=body,
            position=pos,
            alpha=0.8,
            unlit=True  # Bright reflection spots
        )
        highlights.append(highlight)

    # Small bubbles/nuclei floating inside (3 small spheres)
    bubble1 = Entity(
        model='sphere',
        color=enemy_color.tint(0.3),
        scale=0.08,
        parent=body,
        position=(0.1, 0.05, 0.08),
        alpha=0.7
    )

    bubble2 = Entity(
        model='sphere',
        color=enemy_color.tint(0.3),
        scale=0.06,
        parent=body,
        position=(-0.12, -0.05, -0.05),
        alpha=0.7
    )

    bubble3 = Entity(
        model='sphere',
        color=enemy_color.tint(0.3),
        scale=0.05,
        parent=body,
        position=(0.05, -0.1, 0.1),
        alpha=0.7
    )

    # ENHANCEMENT #2: Proper eye structure with glow
    # Left eye assembly
    # Sclera (white outer part)
    left_eye_white = Entity(
        model='sphere',
        color=ursina_color.rgb(240, 240, 240),
        scale=0.09,
        parent=body,
        position=(-0.12, 0.08, 0.2),
        alpha=0.95
    )

    # Iris (colored middle part) - teal/cyan colored with billboard
    left_eye_iris = Entity(
        model='sphere',
        color=enemy_color.tint(-0.5),
        scale=0.06,
        parent=left_eye_white,
        position=(0, 0, 0.02),
        alpha=0.9,
        unlit=True,  # Glowing iris
        billboard=True  # Always faces camera
    )

    # Pupil (black center) - also billboard for tracking effect
    left_eye_pupil = Entity(
        model='sphere',
        color=ursina_color.rgb(10, 10, 10),
        scale=0.35,
        parent=left_eye_iris,
        position=(0, 0, 0.01),
        billboard=True  # Always faces camera
    )

    # Right eye assembly
    right_eye_white = Entity(
        model='sphere',
        color=ursina_color.rgb(240, 240, 240),
        scale=0.09,
        parent=body,
        position=(0.12, 0.08, 0.2),
        alpha=0.95
    )

    right_eye_iris = Entity(
        model='sphere',
        color=enemy_color.tint(-0.5),
        scale=0.06,
        parent=right_eye_white,
        position=(0, 0, 0.02),
        alpha=0.9,
        unlit=True,  # Glowing iris
        billboard=True  # Always faces camera
    )

    right_eye_pupil = Entity(
        model='sphere',
        color=ursina_color.rgb(10, 10, 10),
        scale=0.35,
        parent=right_eye_iris,
        position=(0, 0, 0.01),
        billboard=True  # Always faces camera
    )

    # Store animation state and references
    slime.idle_time = 0.0
    slime.body_ref = body
    slime.core_ref = core
    slime.base_scale_y = 0.45
    slime.base_scale_xz = 0.5

    # Store bubble references for individual pulsing
    slime.bubble1_ref = bubble1
    slime.bubble2_ref = bubble2
    slime.bubble3_ref = bubble3
    slime.bubble1_base_scale = 0.08
    slime.bubble2_base_scale = 0.06
    slime.bubble3_base_scale = 0.05

    # Store highlight references
    slime.highlights = highlights

    return slime


def update_slime_animation(slime: Entity, dt: float):
    """
    Update slime idle animation with enhanced movement

    ENHANCEMENT #3: Rotation, bubble pulsing, and surface ripples

    Args:
        slime: Slime entity to animate
        dt: Delta time since last frame
    """
    slime.idle_time += dt

    # Squish animation (vertical scale oscillation)
    # Frequency: 2 Hz (gentle wobble)
    squish_factor = math.sin(slime.idle_time * 2.0) * 0.15

    if hasattr(slime, 'body_ref'):
        # Squish: scale Y goes from 0.3 to 0.6 (compress/expand)
        new_scale_y = slime.base_scale_y + squish_factor
        # Inverse scale X/Z to maintain volume (squash & stretch)
        inverse_scale_xz = slime.base_scale_xz + (0.1 * -squish_factor)

        # ENHANCEMENT: Add surface ripples (X/Z axis variation)
        ripple_x = math.sin(slime.idle_time * 2.3) * 0.04  # Slightly different frequency
        ripple_z = math.cos(slime.idle_time * 2.7) * 0.04  # Different phase

        slime.body_ref.scale_y = new_scale_y
        slime.body_ref.scale_x = inverse_scale_xz + ripple_x
        slime.body_ref.scale_z = inverse_scale_xz + ripple_z

        # ENHANCEMENT: Slow continuous rotation
        rotation_speed = 15.0  # 15 degrees per second
        slime.body_ref.rotation_y += rotation_speed * dt

    # Core pulses slightly (breathing effect)
    if hasattr(slime, 'core_ref'):
        core_pulse = math.sin(slime.idle_time * 1.5) * 0.03
        slime.core_ref.scale = 0.25 + core_pulse

    # ENHANCEMENT: Individual bubble pulsing at different rates
    if hasattr(slime, 'bubble1_ref'):
        # Bubble 1: Fast pulse
        bubble1_pulse = math.sin(slime.idle_time * 3.0) * 0.02
        slime.bubble1_ref.scale = slime.bubble1_base_scale + bubble1_pulse

    if hasattr(slime, 'bubble2_ref'):
        # Bubble 2: Medium pulse, different phase
        bubble2_pulse = math.sin(slime.idle_time * 2.2 + 1.5) * 0.015
        slime.bubble2_ref.scale = slime.bubble2_base_scale + bubble2_pulse

    if hasattr(slime, 'bubble3_ref'):
        # Bubble 3: Slow pulse, different phase
        bubble3_pulse = math.sin(slime.idle_time * 1.8 + 3.0) * 0.012
        slime.bubble3_ref.scale = slime.bubble3_base_scale + bubble3_pulse

    # ENHANCEMENT: Subtle highlight flickering (shimmering wet surface)
    if hasattr(slime, 'highlights'):
        for i, highlight in enumerate(slime.highlights):
            # Each highlight flickers at slightly different rate
            flicker = math.sin(slime.idle_time * 4.0 + i * 0.8) * 0.2 + 0.6
            highlight.alpha = flicker
