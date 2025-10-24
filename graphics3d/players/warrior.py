"""
Warrior 3D Model - Simple armored fighter

Creates a simple 3D warrior model using Ursina primitives.
Features: Basic armor, ready stance
"""

from ursina import Entity, Vec3, color


def create_warrior_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    """
    Create a 3D warrior character model.

    Args:
        position: Vec3 position for the model
        scale: Vec3 scale for the model

    Returns:
        Entity: Parent entity containing all model parts
    """
    warrior = Entity(position=position, scale=scale)

    # Color palette (using 0-1 scale with /255 division)
    red_tunic = color.rgb(190/255, 50/255, 35/255)
    steel = color.rgb(140/255, 145/255, 155/255)
    dark_steel = color.rgb(90/255, 95/255, 105/255)
    skin = color.rgb(210/255, 170/255, 140/255)
    leather = color.rgb(110/255, 85/255, 50/255)
    pants = color.rgb(70/255, 60/255, 50/255)
    royal_blue = color.rgb(40/255, 90/255, 160/255)

    # ========== BODY ==========
    body = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.4, 0.6, 0.28),
        position=(0, 0, 0)
    )

    # Chest armor
    chest_plate = Entity(
        parent=warrior,
        model='cube',
        color=steel,
        scale=(0.42, 0.5, 0.05),
        position=(0, 0.05, 0.15)
    )

    # ========== HEAD ==========
    head = Entity(
        parent=warrior,
        model='sphere',
        color=skin,
        scale=(0.22, 0.22, 0.22),
        position=(0, 0.5, 0)
    )

    # Helmet (copied from rogue design)
    helmet = Entity(
        parent=warrior,
        model='cube',
        color=steel,
        scale=(0.28, 0.25, 0.28),
        position=(0, 0.55, -0.02)
    )

    # Helmet visor (face guard)
    helmet_visor = Entity(
        parent=warrior,
        model='cube',
        color=dark_steel,
        scale=(0.22, 0.12, 0.05),
        position=(0, 0.48, 0.1)
    )

    # ========== SHOULDERS ==========
    left_pauldron = Entity(
        parent=warrior,
        model='sphere',
        color=steel,
        scale=(0.2, 0.15, 0.2),
        position=(-0.32, 0.28, 0)
    )

    right_pauldron = Entity(
        parent=warrior,
        model='sphere',
        color=steel,
        scale=(0.2, 0.15, 0.2),
        position=(0.32, 0.28, 0)
    )

    # ========== LEFT ARM ==========
    left_arm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.14, 0.5, 0.14),
        position=(-0.32, -0.05, 0)
    )

    left_hand = Entity(
        parent=warrior,
        model='cube',
        color=skin,
        scale=(0.12, 0.12, 0.12),
        position=(-0.32, -0.35, 0)
    )

    # ========== SHIELD ==========
    # Shield base
    shield = Entity(
        parent=warrior,
        model='cube',
        color=royal_blue,
        scale=(0.32, 0.42, 0.06),
        position=(-0.38, -0.35, 0.12)
    )

    # Shield boss (center)
    shield_boss = Entity(
        parent=warrior,
        model='sphere',
        color=steel,
        scale=(0.1, 0.1, 0.05),
        position=(-0.38, -0.35, 0.16)
    )

    # ========== RIGHT ARM ==========
    right_arm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.14, 0.5, 0.14),
        position=(0.32, -0.05, 0)
    )

    right_hand = Entity(
        parent=warrior,
        model='cube',
        color=skin,
        scale=(0.12, 0.12, 0.12),
        position=(0.32, -0.35, 0)
    )

    # ========== BELT ==========
    belt = Entity(
        parent=warrior,
        model='cube',
        color=leather,
        scale=(0.42, 0.08, 0.3),
        position=(0, -0.32, 0)
    )

    # ========== LEGS ==========
    # Left leg
    left_leg = Entity(
        parent=warrior,
        model='cube',
        color=pants,
        scale=(0.18, 0.6, 0.18),
        position=(-0.12, -0.75, 0)
    )

    left_boot = Entity(
        parent=warrior,
        model='cube',
        color=leather,
        scale=(0.18, 0.14, 0.22),
        position=(-0.12, -1.12, 0.02)
    )

    # Right leg
    right_leg = Entity(
        parent=warrior,
        model='cube',
        color=pants,
        scale=(0.18, 0.6, 0.18),
        position=(0.12, -0.75, 0)
    )

    right_boot = Entity(
        parent=warrior,
        model='cube',
        color=leather,
        scale=(0.18, 0.14, 0.22),
        position=(0.12, -1.12, 0.02)
    )

    # Rotate 180 degrees to face forward
    warrior.rotation_y = 270

    return warrior


__all__ = ['create_warrior_model']
