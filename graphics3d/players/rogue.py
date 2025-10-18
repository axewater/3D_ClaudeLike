"""
Rogue 3D Model - Stealthy assassin with daggers and hood

Creates a procedurally generated 3D rogue model using Ursina primitives.
Features: Dark clothing, dual daggers, hood, lean proportions
"""

from ursina import Entity, Vec3, color


def create_rogue_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    """
    Create a 3D rogue character model.

    Args:
        position: Vec3 position for the model
        scale: Vec3 scale for the model

    Returns:
        Entity: Parent entity containing all model parts
    """
    # Create parent entity to hold all parts
    rogue = Entity(position=position, scale=scale)

    # Body (lean torso in dark leather)
    body = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(80/255, 80/255, 80/255),  # Dark gray leather
        scale=(0.35, 0.6, 0.25),
        position=(0, 0, 0)
    )

    # Head
    head = Entity(
        parent=rogue,
        model='sphere',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.2, 0.2, 0.2),
        position=(0, 0.45, 0)
    )

    # Hood (dark, covering head)
    hood = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(50/255, 50/255, 60/255),  # Very dark
        scale=(0.28, 0.25, 0.28),
        position=(0, 0.55, -0.02)
    )

    # Hood shadow (face concealment)
    hood_shadow = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(20/255, 20/255, 25/255),  # Nearly black
        scale=(0.22, 0.12, 0.05),
        position=(0, 0.48, 0.1)
    )

    # Leather chest armor (under cloak)
    chest_armor = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 50/255, 45/255),  # Dark leather
        scale=(0.37, 0.5, 0.27),
        position=(0, 0.05, 0.01)
    )

    # Left arm (holding dagger)
    left_arm = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(70/255, 70/255, 75/255),
        scale=(0.12, 0.45, 0.12),
        position=(-0.28, -0.05, 0),
        rotation=(0, 0, -20)  # Slightly angled
    )

    # Left hand (gripping dagger)
    left_hand = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.1, 0.12, 0.1),
        position=(-0.32, -0.3, 0.05)
    )

    # Left arm bracer (leather with buckle)
    left_bracer = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(50/255, 45/255, 50/255),  # Dark leather
        scale=(0.13, 0.2, 0.13),
        position=(-0.28, -0.2, 0)
    )

    # Left bracer buckle
    left_buckle = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(80/255, 80/255, 85/255),  # Metal
        scale=(0.06, 0.06, 0.06),
        position=(-0.28, -0.2, 0.08)
    )

    # Right arm (holding dagger)
    right_arm = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(70/255, 70/255, 75/255),
        scale=(0.12, 0.45, 0.12),
        position=(0.28, -0.05, 0),
        rotation=(0, 0, 20)  # Slightly angled
    )

    # Right hand (gripping dagger)
    right_hand = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.1, 0.12, 0.1),
        position=(0.32, -0.3, 0.05)
    )

    # Right arm bracer (leather with buckle)
    right_bracer = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(50/255, 45/255, 50/255),  # Dark leather
        scale=(0.13, 0.2, 0.13),
        position=(0.28, -0.2, 0)
    )

    # Right bracer buckle
    right_buckle = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(80/255, 80/255, 85/255),  # Metal
        scale=(0.06, 0.06, 0.06),
        position=(0.28, -0.2, 0.08)
    )

    # Left dagger (blade)
    left_dagger = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(150/255, 150/255, 160/255),  # Steel
        scale=(0.05, 0.35, 0.05),
        position=(-0.35, -0.25, 0.15),
        rotation=(-30, 0, 0)  # Pointed forward
    )

    # Left dagger crossguard
    left_crossguard = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(100/255, 100/255, 110/255),  # Dark steel
        scale=(0.15, 0.04, 0.08),
        position=(-0.35, -0.35, 0.12),
        rotation=(-30, 0, 0)
    )

    # Left dagger hilt
    left_hilt = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(40/255, 40/255, 45/255),  # Black leather
        scale=(0.08, 0.12, 0.08),
        position=(-0.35, -0.4, 0.1),
        rotation=(-30, 0, 0)
    )

    # Right dagger (blade)
    right_dagger = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(150/255, 150/255, 160/255),  # Steel
        scale=(0.05, 0.35, 0.05),
        position=(0.35, -0.25, 0.15),
        rotation=(-30, 0, 0)  # Pointed forward
    )

    # Right dagger crossguard
    right_crossguard = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(100/255, 100/255, 110/255),  # Dark steel
        scale=(0.15, 0.04, 0.08),
        position=(0.35, -0.35, 0.12),
        rotation=(-30, 0, 0)
    )

    # Right dagger hilt
    right_hilt = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(40/255, 40/255, 45/255),  # Black leather
        scale=(0.08, 0.12, 0.08),
        position=(0.35, -0.4, 0.1),
        rotation=(-30, 0, 0)
    )

    # Legs (lean and agile)
    left_leg = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 60/255, 65/255),  # Dark pants
        scale=(0.15, 0.5, 0.15),
        position=(-0.12, -0.6, 0)
    )

    right_leg = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 60/255, 65/255),
        scale=(0.15, 0.5, 0.15),
        position=(0.12, -0.6, 0)
    )

    # Belt with pouches
    belt = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(50/255, 45/255, 40/255),  # Dark leather
        scale=(0.38, 0.08, 0.27),
        position=(0, -0.3, 0)
    )

    # Pouch (left side)
    pouch_1 = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 50/255, 45/255),
        scale=(0.12, 0.12, 0.12),
        position=(-0.25, -0.35, 0)
    )

    # Pouch 2 (right side)
    pouch_2 = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 50/255, 45/255),
        scale=(0.1, 0.1, 0.1),
        position=(0.2, -0.35, 0)
    )

    # Lockpick pouch (small, center)
    lockpick_pouch = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(50/255, 40/255, 40/255),  # Darker
        scale=(0.08, 0.08, 0.08),
        position=(0, -0.36, 0.05)
    )

    # Throwing knife 1 (left hip)
    throwing_knife_1 = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(140/255, 140/255, 150/255),  # Steel
        scale=(0.04, 0.15, 0.04),
        position=(-0.15, -0.4, 0.08)
    )

    # Throwing knife 2 (right hip)
    throwing_knife_2 = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(140/255, 140/255, 150/255),  # Steel
        scale=(0.04, 0.15, 0.04),
        position=(0.12, -0.4, 0.08)
    )

    # Boots with straps
    left_boot = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(40/255, 35/255, 40/255),  # Very dark
        scale=(0.17, 0.15, 0.22),
        position=(-0.12, -0.9, 0.02)
    )

    # Left boot strap
    left_boot_strap = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 55/255, 50/255),  # Dark leather
        scale=(0.18, 0.04, 0.08),
        position=(-0.12, -0.88, 0.08)
    )

    right_boot = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(40/255, 35/255, 40/255),  # Very dark
        scale=(0.17, 0.15, 0.22),
        position=(0.12, -0.9, 0.02)
    )

    # Right boot strap
    right_boot_strap = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(60/255, 55/255, 50/255),  # Dark leather
        scale=(0.18, 0.04, 0.08),
        position=(0.12, -0.88, 0.08)
    )

    # Cloak/cape (segmented for flow)
    # Upper cape
    cape_upper = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(40/255, 40/255, 50/255),  # Very dark blue-gray
        scale=(0.38, 0.25, 0.05),
        position=(0, 0.15, -0.18)
    )

    # Middle cape
    cape_middle = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(38/255, 38/255, 48/255),  # Slightly darker
        scale=(0.36, 0.25, 0.06),
        position=(0, -0.1, -0.2)
    )

    # Lower cape (flowing)
    cape_lower = Entity(
        parent=rogue,
        model='cube',
        color=color.rgb(35/255, 35/255, 45/255),  # Darkest
        scale=(0.34, 0.25, 0.07),
        position=(0, -0.35, -0.22)
    )

    return rogue


__all__ = ['create_rogue_model']
