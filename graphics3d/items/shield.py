"""
Shield 3D model - Defense armor with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color


def create_shield_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D shield model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Shield 3D model
    """
    # Container entity (invisible parent)
    shield = Entity(position=position)

    # Rarity-based colors
    if rarity == c.RARITY_COMMON:
        face_color = rgb_to_ursina_color(120, 90, 60)  # Wooden brown
        rim_color = rgb_to_ursina_color(80, 60, 40)  # Dark brown
        boss_color = rgb_to_ursina_color(140, 140, 140)  # Iron
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        face_color = rgb_to_ursina_color(140, 140, 150)  # Steel gray
        rim_color = rgb_to_ursina_color(100, 100, 110)  # Dark steel
        boss_color = rgb_to_ursina_color(180, 140, 80)  # Brass
        has_glow = False
    elif rarity == c.RARITY_RARE:
        face_color = rgb_to_ursina_color(150, 180, 255)  # Blue steel
        rim_color = rgb_to_ursina_color(100, 130, 200)  # Dark blue
        boss_color = rgb_to_ursina_color(192, 192, 192)  # Silver
        has_glow = False
    elif rarity == c.RARITY_EPIC:
        face_color = rgb_to_ursina_color(200, 100, 255)  # Purple
        rim_color = rgb_to_ursina_color(150, 50, 200)  # Dark purple
        boss_color = rgb_to_ursina_color(220, 180, 100)  # Gold
        has_glow = True
        glow_color = rgb_to_ursina_color(200, 100, 255)
    else:  # LEGENDARY
        face_color = rgb_to_ursina_color(255, 215, 0)  # Gold
        rim_color = rgb_to_ursina_color(200, 160, 0)  # Dark gold
        boss_color = rgb_to_ursina_color(100, 200, 255)  # Bright cyan
        has_glow = True
        glow_color = rgb_to_ursina_color(100, 200, 255)

    # Glow effect for epic/legendary
    if has_glow:
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.35,
            parent=shield,
            position=(0, 0, 0),
            alpha=0.3,
            unlit=True
        )

    # Shield face (flattened rounded cube)
    face = Entity(
        model='cube',
        color=face_color,
        scale=(0.28, 0.35, 0.08),
        parent=shield,
        position=(0, 0, 0)
    )

    # Shield rim/border (slightly larger, darker)
    rim = Entity(
        model='cube',
        color=rim_color,
        scale=(0.3, 0.37, 0.06),
        parent=shield,
        position=(0, 0, -0.01)
    )

    # Boss (center decorative sphere)
    boss = Entity(
        model='sphere',
        color=boss_color,
        scale=0.1,
        parent=face,
        position=(0, 0, 0.05)
    )

    # Decorative studs/rivets for higher rarities
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        stud_positions = [
            (-0.1, 0.15, 0.04),
            (0.1, 0.15, 0.04),
            (-0.1, -0.15, 0.04),
            (0.1, -0.15, 0.04),
        ]
        for pos in stud_positions:
            stud = Entity(
                model='sphere',
                color=boss_color.tint(-0.2),
                scale=0.03,
                parent=face,
                position=pos
            )

    # Store animation state
    shield.float_time = 0.0
    shield.rotation_speed = 50.0

    return shield
