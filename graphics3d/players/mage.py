"""
Mage 3D Model - Magical spellcaster with staff and robes

Creates a procedurally generated 3D mage model using Ursina primitives.
Features: Flowing robes, magical staff, arcane orb, slim proportions
"""

from ursina import Entity, Vec3, color


def create_mage_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    """
    Create a 3D mage character model.

    Args:
        position: Vec3 position for the model
        scale: Vec3 scale for the model

    Returns:
        Entity: Parent entity containing all model parts
    """
    # Create parent entity to hold all parts
    mage = Entity(position=position, scale=scale)

    # Body (slim torso in robes)
    body = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(100/255, 150/255, 255/255),  # Purple-blue robes
        scale=(0.4, 0.7, 0.3),
        position=(0, 0, 0)
    )

    # Robe bottom (wider at base)
    robe_bottom = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(80/255, 120/255, 220/255),  # Darker purple
        scale=(0.5, 0.3, 0.4),
        position=(0, -0.5, 0)
    )

    # Head
    head = Entity(
        parent=mage,
        model='sphere',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.22, 0.22, 0.22),
        position=(0, 0.5, 0)
    )

    # Wizard hat (tall and pointed)
    hat_base = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(60/255, 40/255, 120/255),  # Dark purple
        scale=(0.3, 0.08, 0.3),
        position=(0, 0.63, 0)
    )

    hat_cone = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(70/255, 50/255, 140/255),  # Purple
        scale=(0.15, 0.5, 0.15),
        position=(0, 0.9, 0)
    )

    # Wizard hat ornament (star)
    hat_star = Entity(
        parent=mage,
        model='sphere',
        color=color.rgb(255/255, 215/255, 0/255),  # Gold
        scale=(0.08, 0.08, 0.08),
        position=(0, 1.15, 0)
    )

    # Left arm (holding staff)
    left_arm = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(100/255, 150/255, 255/255),
        scale=(0.12, 0.45, 0.12),
        position=(-0.3, -0.1, 0)
    )

    # Left hand (gripping staff)
    left_hand = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.1, 0.12, 0.1),
        position=(-0.3, -0.4, 0)
    )

    # Right arm (casting)
    right_arm = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(100/255, 150/255, 255/255),
        scale=(0.12, 0.45, 0.12),
        position=(0.3, 0, 0.1),
        rotation=(0, 0, 45)  # Extended for casting
    )

    # Right hand (casting gesture)
    right_hand = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(200/255, 160/255, 130/255),  # Skin tone
        scale=(0.1, 0.12, 0.1),
        position=(0.42, 0.25, 0.15),
        rotation=(0, 0, 45)
    )

    # Magical staff (long wooden pole)
    staff_shaft = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(120/255, 80/255, 40/255),  # Brown wood
        scale=(0.06, 1.2, 0.06),
        position=(-0.35, 0, 0)
    )

    # Staff wrapping (leather grip)
    staff_wrap_1 = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(80/255, 60/255, 40/255),  # Dark leather
        scale=(0.07, 0.08, 0.07),
        position=(-0.35, -0.3, 0)
    )

    staff_wrap_2 = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(80/255, 60/255, 40/255),  # Dark leather
        scale=(0.07, 0.08, 0.07),
        position=(-0.35, 0.2, 0)
    )

    # Staff orb (glowing at top)
    staff_orb = Entity(
        parent=mage,
        model='sphere',
        color=color.rgb(150/255, 100/255, 255/255),  # Purple glow
        scale=(0.15, 0.15, 0.15),
        position=(-0.35, 0.6, 0)
    )

    # Crystal settings (4 small crystals around orb)
    for i in range(4):
        angle = i * 90
        import math
        x_offset = math.cos(math.radians(angle)) * 0.18
        z_offset = math.sin(math.radians(angle)) * 0.18
        crystal = Entity(
            parent=mage,
            model='cube',
            color=color.rgb(180/255, 120/255, 255/255),  # Purple crystal
            scale=(0.05, 0.08, 0.05),
            position=(-0.35 + x_offset, 0.6, z_offset),
            rotation=(0, angle, 0)
        )

    # Staff orb inner glow
    orb_glow = Entity(
        parent=mage,
        model='sphere',
        color=color.rgb(200/255, 150/255, 255/255),  # Bright purple
        scale=(0.08, 0.08, 0.08),
        position=(-0.35, 0.6, 0)
    )

    # Floating spell book (optional detail)
    book = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(150/255, 120/255, 80/255),  # Leather bound
        scale=(0.15, 0.2, 0.12),
        position=(0.25, 0.4, 0.2),
        rotation=(30, -20, 10)  # Floating and tilted
    )

    # Book glow (magical)
    book_glow = Entity(
        parent=mage,
        model='cube',
        color=color.rgba(150/255, 200/255, 255/255, 0.5),  # Blue glow
        scale=(0.18, 0.23, 0.15),
        position=(0.25, 0.4, 0.2),
        rotation=(30, -20, 10)
    )

    # Belt/sash
    belt = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(120/255, 100/255, 50/255),  # Gold/brown
        scale=(0.42, 0.08, 0.32),
        position=(0, -0.3, 0)
    )

    # Spell component pouch (left hip)
    spell_pouch = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(80/255, 60/255, 100/255),  # Purple pouch
        scale=(0.12, 0.15, 0.12),
        position=(-0.2, -0.4, 0)
    )

    # Scroll case (right hip)
    scroll_case = Entity(
        parent=mage,
        model='cube',
        color=color.rgb(140/255, 120/255, 80/255),  # Leather tube
        scale=(0.08, 0.25, 0.08),
        position=(0.2, -0.4, 0)
    )

    return mage


__all__ = ['create_mage_model']
