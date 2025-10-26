"""
Boots 3D model - Footwear equipment with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
from core import constants as c
from graphics3d.utils import rgb_to_ursina_color

from graphics3d.shader_manager import get_shader_manager


def create_boots_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D boots model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Boots 3D model
    """
    # Get shader manager instance
    shader_mgr = get_shader_manager()

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
    sole_shader = shader_mgr.get_shader_for_scale(0.22)
    left_sole = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.025, 0.22),
        parent=left_boot_container,
        position=(0, 0, 0),
        shader=sole_shader
    )

    # Heel - raised back section
    heel_shader = shader_mgr.get_shader_for_scale(0.11)
    left_heel = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.05, 0.08),
        parent=left_boot_container,
        position=(0, 0.025, -0.09),
        shader=heel_shader
    )

    # Main foot section - body of boot
    foot_shader = shader_mgr.get_shader_for_scale(0.2)
    left_foot = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.12, 0.2),
        parent=left_boot_container,
        position=(0, 0.08, 0),
        shader=foot_shader
    )

    # Toe cap - rounded front (sphere for smooth look)
    toe_shader = shader_mgr.get_shader_for_scale(0.11)
    left_toe = Entity(
        model='sphere',
        color=boot_color.tint(-0.05),
        scale=(0.09, 0.1, 0.11),
        parent=left_boot_container,
        position=(0, 0.06, 0.13),
        shader=toe_shader
    )

    # Ankle section - slightly wider upper boot
    ankle_shader = shader_mgr.get_shader_for_scale(0.18)
    left_ankle = Entity(
        model='cube',
        color=boot_color,
        scale=(0.11, 0.1, 0.18),
        parent=left_boot_container,
        position=(0, 0.19, 0),
        shader=ankle_shader
    )

    # Shaft - tall section going up the calf
    shaft_shader = shader_mgr.get_shader_for_scale(0.16)
    left_shaft = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.08, 0.16),
        parent=left_boot_container,
        position=(0, 0.28, 0),
        rotation=(0, 0, 2),  # Slight tilt outward
        shader=shaft_shader
    )

    # Fold/Cuff at top - folded leather look
    cuff_shader = shader_mgr.get_shader_for_scale(0.17)
    left_cuff = Entity(
        model='sphere',
        color=boot_color.tint(0.1),
        scale=(0.11, 0.04, 0.17),
        parent=left_boot_container,
        position=(0, 0.34, 0),
        shader=cuff_shader
    )

    # ====== RIGHT BOOT ======
    right_boot_container = Entity(parent=boots, position=(0.1, -0.1, 0), rotation=(0, 5, 0))

    # Sole (reuse sole_shader from left boot)
    right_sole = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.025, 0.22),
        parent=right_boot_container,
        position=(0, 0, 0),
        shader=sole_shader
    )

    # Heel (reuse heel_shader from left boot)
    right_heel = Entity(
        model='cube',
        color=boot_color.tint(-0.3),
        scale=(0.11, 0.05, 0.08),
        parent=right_boot_container,
        position=(0, 0.025, -0.09),
        shader=heel_shader
    )

    # Main foot section (reuse foot_shader from left boot)
    right_foot = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.12, 0.2),
        parent=right_boot_container,
        position=(0, 0.08, 0),
        shader=foot_shader
    )

    # Toe cap (reuse toe_shader from left boot)
    right_toe = Entity(
        model='sphere',
        color=boot_color.tint(-0.05),
        scale=(0.09, 0.1, 0.11),
        parent=right_boot_container,
        position=(0, 0.06, 0.13),
        shader=toe_shader
    )

    # Ankle section (reuse ankle_shader from left boot)
    right_ankle = Entity(
        model='cube',
        color=boot_color,
        scale=(0.11, 0.1, 0.18),
        parent=right_boot_container,
        position=(0, 0.19, 0),
        shader=ankle_shader
    )

    # Shaft (reuse shaft_shader from left boot)
    right_shaft = Entity(
        model='cube',
        color=boot_color,
        scale=(0.1, 0.08, 0.16),
        parent=right_boot_container,
        position=(0, 0.28, 0),
        rotation=(0, 0, -2),  # Slight tilt outward
        shader=shaft_shader
    )

    # Fold/Cuff at top (reuse cuff_shader from left boot)
    right_cuff = Entity(
        model='sphere',
        color=boot_color.tint(0.1),
        scale=(0.11, 0.04, 0.17),
        parent=right_boot_container,
        position=(0, 0.34, 0),
        shader=cuff_shader
    )

    # ====== DECORATIVE DETAILS ======
    # Laces/Straps for uncommon+
    if rarity != c.RARITY_COMMON:
        # Shader for small strap details
        strap_shader = shader_mgr.get_shader_for_scale(0.015)

        # Left boot laces (3 straps down the front)
        for i in range(3):
            strap_y = 0.12 + (i * 0.06)
            left_strap = Entity(
                model='cube',
                color=accent_color,
                scale=(0.11, 0.015, 0.015),
                parent=left_boot_container,
                position=(0, strap_y, 0.1),
                shader=strap_shader
            )

        # Right boot laces
        for i in range(3):
            strap_y = 0.12 + (i * 0.06)
            right_strap = Entity(
                model='cube',
                color=accent_color,
                scale=(0.11, 0.015, 0.015),
                parent=right_boot_container,
                position=(0, strap_y, 0.1),
                shader=strap_shader
            )

    # Buckle accent for rare+
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        # Shader for small buckle details
        buckle_shader = shader_mgr.get_shader_for_scale(0.04)

        # Left buckle
        left_buckle = Entity(
            model='cube',
            color=accent_color,
            scale=(0.04, 0.04, 0.02),
            parent=left_boot_container,
            position=(0, 0.18, 0.11),
            shader=buckle_shader
        )

        # Right buckle
        right_buckle = Entity(
            model='cube',
            color=accent_color,
            scale=(0.04, 0.04, 0.02),
            parent=right_boot_container,
            position=(0, 0.18, 0.11),
            shader=buckle_shader
        )

    # Store animation state
    boots.float_time = 0.0
    boots.rotation_speed = 50.0

    return boots
