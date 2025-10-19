"""
Boots 3D model - Footwear equipment with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color


def create_boots_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D boots model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Boots 3D model
    """
    # Container entity (invisible parent)
    boots = Entity(position=position)

    # Rarity-based colors and materials
    if rarity == c.RARITY_COMMON:
        boot_color = rgb_to_ursina_color(100, 60, 30)  # Brown leather
        accent_color = rgb_to_ursina_color(80, 50, 25)  # Dark brown
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        boot_color = rgb_to_ursina_color(80, 80, 90)  # Gray leather
        accent_color = rgb_to_ursina_color(120, 120, 130)  # Light gray
        has_glow = False
    elif rarity == c.RARITY_RARE:
        boot_color = rgb_to_ursina_color(100, 130, 200)  # Blue leather
        accent_color = rgb_to_ursina_color(150, 150, 150)  # Silver buckles
        has_glow = False
    elif rarity == c.RARITY_EPIC:
        boot_color = rgb_to_ursina_color(150, 50, 200)  # Purple
        accent_color = rgb_to_ursina_color(220, 180, 100)  # Gold buckles
        has_glow = True
        glow_color = rgb_to_ursina_color(200, 100, 255)
    else:  # LEGENDARY
        boot_color = rgb_to_ursina_color(50, 50, 80)  # Dark mythic
        accent_color = rgb_to_ursina_color(255, 215, 0)  # Bright gold
        has_glow = True
        glow_color = rgb_to_ursina_color(100, 200, 255)

    # Glow for epic/legendary
    if has_glow:
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.35,
            parent=boots,
            position=(0, 0, 0),
            alpha=0.3,
            unlit=True
        )

    # ====== LEFT BOOT ======
    left_boot_container = Entity(parent=boots, position=(-0.1, -0.1, 0), rotation=(0, -5, 0))

    # Sole - dark rubber/leather bottom
    left_sole = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.025, 0.22),
        parent=left_boot_container,
        position=(0, 0, 0)
    )

    # Heel - raised back section
    left_heel = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.05, 0.08),
        parent=left_boot_container,
        position=(0, 0.025, -0.09)
    )

    # Main foot section - body of boot
    left_foot = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.12, 0.2),
        parent=left_boot_container,
        position=(0, 0.08, 0)
    )

    # Toe cap - rounded front (sphere for smooth look)
    left_toe = Entity(
        model='sphere',
        color=boot_color.tint(-0.05),
        scale=(0.09, 0.1, 0.11),
        parent=left_boot_container,
        position=(0, 0.06, 0.13)
    )

    # Ankle section - slightly wider upper boot
    left_ankle = Entity(
        model='cube',
        color=boot_color,
        scale=(0.11, 0.1, 0.18),
        parent=left_boot_container,
        position=(0, 0.19, 0)
    )

    # Shaft - tall section going up the calf
    left_shaft = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.08, 0.16),
        parent=left_boot_container,
        position=(0, 0.28, 0),
        rotation=(0, 0, 2)  # Slight tilt outward
    )

    # Fold/Cuff at top - folded leather look
    left_cuff = Entity(
        model='sphere',
        color=boot_color.tint(0.1),
        scale=(0.11, 0.04, 0.17),
        parent=left_boot_container,
        position=(0, 0.34, 0)
    )

    # ====== RIGHT BOOT ======
    right_boot_container = Entity(parent=boots, position=(0.1, -0.1, 0), rotation=(0, 5, 0))

    # Sole
    right_sole = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.025, 0.22),
        parent=right_boot_container,
        position=(0, 0, 0)
    )

    # Heel
    right_heel = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.05, 0.08),
        parent=right_boot_container,
        position=(0, 0.025, -0.09)
    )

    # Main foot section
    right_foot = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.12, 0.2),
        parent=right_boot_container,
        position=(0, 0.08, 0)
    )

    # Toe cap
    right_toe = Entity(
        model='sphere',
        color=boot_color.tint(-0.05),
        scale=(0.09, 0.1, 0.11),
        parent=right_boot_container,
        position=(0, 0.06, 0.13)
    )

    # Ankle section
    right_ankle = Entity(
        model='cube',
        color=boot_color,
        scale=(0.11, 0.1, 0.18),
        parent=right_boot_container,
        position=(0, 0.19, 0)
    )

    # Shaft
    right_shaft = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.08, 0.16),
        parent=right_boot_container,
        position=(0, 0.28, 0),
        rotation=(0, 0, -2)  # Slight tilt outward
    )

    # Fold/Cuff at top
    right_cuff = Entity(
        model='sphere',
        color=boot_color.tint(0.1),
        scale=(0.11, 0.04, 0.17),
        parent=right_boot_container,
        position=(0, 0.34, 0)
    )

    # ====== DECORATIVE DETAILS ======
    # Laces/Straps for uncommon+
    if rarity != c.RARITY_COMMON:
        # Left boot laces (3 straps down the front)
        for i in range(3):
            strap_y = 0.12 + (i * 0.06)
            left_strap = Entity(
                model='cube',
                color=accent_color,
                scale=(0.11, 0.015, 0.015),
                parent=left_boot_container,
                position=(0, strap_y, 0.1)
            )

        # Right boot laces
        for i in range(3):
            strap_y = 0.12 + (i * 0.06)
            right_strap = Entity(
                model='cube',
                color=accent_color,
                scale=(0.11, 0.015, 0.015),
                parent=right_boot_container,
                position=(0, strap_y, 0.1)
            )

    # Buckle accent for rare+
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        # Left buckle
        left_buckle = Entity(
            model='cube',
            color=accent_color,
            scale=(0.04, 0.04, 0.02),
            parent=left_boot_container,
            position=(0, 0.18, 0.11)
        )

        # Right buckle
        right_buckle = Entity(
            model='cube',
            color=accent_color,
            scale=(0.04, 0.04, 0.02),
            parent=right_boot_container,
            position=(0, 0.18, 0.11)
        )

    # Store animation state
    boots.float_time = 0.0
    boots.rotation_speed = 50.0

    return boots
