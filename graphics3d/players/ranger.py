"""
Ranger 3D Model - Nature-themed archer with bow and quiver

Creates a procedurally generated 3D ranger model using Ursina primitives.
Features: Bow, quiver, arrows, forest colors, balanced proportions
"""

from ursina import Entity, Vec3, color


def create_ranger_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    """
    Create a 3D ranger character model.

    Args:
        position: Vec3 position for the model
        scale: Vec3 scale for the model

    Returns:
        Entity: Parent entity containing all model parts
    """
    # Create parent entity to hold all parts
    ranger = Entity(position=position, scale=scale)

    # Body (balanced build in green/brown)
    body = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(100/255, 200/255, 100/255),  # Forest green
        scale=(0.4, 0.6, 0.28),
        position=(0, 0, 0)
    )

    # Head
    head = Entity(
        parent=ranger,
        model='sphere',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.22, 0.22, 0.22),
        position=(0, 0.48, 0)
    )

    # Hood/cap (archer's cap)
    cap = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(80/255, 140/255, 70/255),  # Dark green
        scale=(0.25, 0.12, 0.25),
        position=(0, 0.58, 0)
    )

    # Feather in cap
    feather = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(180/255, 50/255, 50/255),  # Red feather
        scale=(0.03, 0.15, 0.03),
        position=(0.12, 0.65, 0),
        rotation=(0, 0, -30)
    )

    # Leather chest armor (vest)
    chest_armor = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(100/255, 70/255, 40/255),  # Brown leather
        scale=(0.42, 0.5, 0.3),
        position=(0, 0.05, 0.01)
    )

    # Left arm (holding bow)
    left_arm = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 180/255, 90/255),
        scale=(0.13, 0.45, 0.13),
        position=(-0.3, 0, 0),
        rotation=(0, 0, -30)  # Extended to hold bow
    )

    # Left hand (gripping bow)
    left_hand = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.11, 0.13, 0.11),
        position=(-0.42, -0.25, 0)
    )

    # Left arm bracer (leather forearm guard)
    left_bracer = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 65/255, 40/255),  # Dark leather
        scale=(0.14, 0.25, 0.14),
        position=(-0.35, -0.15, 0)
    )

    # Right arm (drawing string)
    right_arm = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 180/255, 90/255),
        scale=(0.13, 0.45, 0.13),
        position=(0.3, 0.05, 0),
        rotation=(0, 0, 30)
    )

    # Right hand (drawing string)
    right_hand = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.11, 0.13, 0.11),
        position=(0.41, 0.27, 0)
    )

    # Right arm bracer (leather forearm guard)
    right_bracer = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 65/255, 40/255),  # Dark leather
        scale=(0.14, 0.25, 0.14),
        position=(0.35, 0.13, 0)
    )

    # Bow (curved wooden arc)
    bow_upper = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(120/255, 80/255, 40/255),  # Brown wood
        scale=(0.06, 0.5, 0.06),
        position=(-0.4, 0.3, 0),
        rotation=(0, 0, -15)  # Curved
    )

    # Upper bow limb tip (recurve)
    bow_tip_upper = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(100/255, 70/255, 35/255),  # Darker wood
        scale=(0.08, 0.1, 0.08),
        position=(-0.45, 0.55, 0),
        rotation=(0, 0, -30)
    )

    bow_lower = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(120/255, 80/255, 40/255),
        scale=(0.06, 0.5, 0.06),
        position=(-0.4, -0.3, 0),
        rotation=(0, 0, 15)  # Curved opposite
    )

    # Lower bow limb tip (recurve)
    bow_tip_lower = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(100/255, 70/255, 35/255),  # Darker wood
        scale=(0.08, 0.1, 0.08),
        position=(-0.45, -0.55, 0),
        rotation=(0, 0, 30)
    )

    # Bow grip/handle (leather wrapped)
    bow_grip = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(80/255, 60/255, 40/255),  # Dark leather
        scale=(0.09, 0.2, 0.09),
        position=(-0.4, 0, 0)
    )

    # Bowstring (thin line)
    bowstring = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(220/255, 220/255, 200/255),  # Light string
        scale=(0.02, 0.8, 0.02),
        position=(-0.35, 0, 0)
    )

    # Quiver (on back)
    quiver = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(100/255, 70/255, 40/255),  # Brown leather
        scale=(0.15, 0.5, 0.15),
        position=(0.15, 0.1, -0.2),
        rotation=(0, 0, -15)  # Angled on back
    )

    # Quiver strap (across chest)
    quiver_strap = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 65/255, 40/255),  # Dark leather strap
        scale=(0.08, 0.6, 0.05),
        position=(-0.15, 0.15, 0.02),
        rotation=(0, 0, 45)  # Diagonal across chest
    )

    # Arrows in quiver (3 visible)
    for i in range(3):
        arrow_shaft = Entity(
            parent=ranger,
            model='cube',
            color=color.rgb(140/255, 100/255, 60/255),  # Wood shaft
            scale=(0.03, 0.3, 0.03),
            position=(0.12 + i * 0.04, 0.45, -0.2),
            rotation=(0, 0, -15)
        )

        # Arrow tip (pointed metal)
        arrow_tip = Entity(
            parent=ranger,
            model='cube',
            color=color.rgb(180/255, 180/255, 190/255),  # Steel
            scale=(0.04, 0.08, 0.04),
            position=(0.12 + i * 0.04, 0.32, -0.2),
            rotation=(0, 0, -15)
        )

        arrow_fletching = Entity(
            parent=ranger,
            model='cube',
            color=color.rgb(200/255, 50/255, 50/255) if i == 1 else color.rgb(100/255, 150/255, 50/255),  # Red or green
            scale=(0.08, 0.08, 0.02),
            position=(0.12 + i * 0.04, 0.55, -0.2),
            rotation=(0, 0, -15)
        )

    # Legs
    left_leg = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 70/255, 50/255),  # Brown pants
        scale=(0.17, 0.5, 0.17),
        position=(-0.13, -0.6, 0)
    )

    right_leg = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 70/255, 50/255),
        scale=(0.17, 0.5, 0.17),
        position=(0.13, -0.6, 0)
    )

    # Belt
    belt = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(80/255, 60/255, 40/255),  # Leather belt
        scale=(0.42, 0.08, 0.3),
        position=(0, -0.3, 0)
    )

    # Belt pouch
    pouch = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(90/255, 70/255, 50/255),
        scale=(0.12, 0.1, 0.12),
        position=(0.2, -0.35, 0)
    )

    # Boots
    left_boot = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(70/255, 50/255, 30/255),  # Dark brown leather
        scale=(0.2, 0.15, 0.25),
        position=(-0.13, -0.9, 0.02)
    )

    # Left boot buckle
    left_boot_buckle = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(120/255, 110/255, 100/255),  # Metal buckle
        scale=(0.06, 0.06, 0.08),
        position=(-0.13, -0.85, 0.08)
    )

    right_boot = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(70/255, 50/255, 30/255),
        scale=(0.2, 0.15, 0.25),
        position=(0.13, -0.9, 0.02)
    )

    # Right boot buckle
    right_boot_buckle = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(120/255, 110/255, 100/255),  # Metal buckle
        scale=(0.06, 0.06, 0.08),
        position=(0.13, -0.85, 0.08)
    )

    # Cloak (draped over shoulders and back)
    cloak = Entity(
        parent=ranger,
        model='cube',
        color=color.rgb(80/255, 120/255, 70/255),  # Forest green
        scale=(0.45, 0.5, 0.08),
        position=(0, 0, -0.25)
    )

    return ranger


__all__ = ['create_ranger_model']
