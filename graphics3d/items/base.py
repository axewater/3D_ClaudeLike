"""
Base utilities for 3D item model rendering

Shared functions for all item models.
"""

from ursina import Entity, Vec3
import math
import constants as c


def create_item_model_3d(item_type: str, rarity: str, position: Vec3) -> Entity:
    """
    Factory function to create item 3D models

    Args:
        item_type: Item type string (sword, shield, health_potion, boots, ring)
        rarity: Item rarity (common, uncommon, rare, epic, legendary)
        position: 3D world position

    Returns:
        Entity: Item 3D model
    """
    # Import item model creators
    from graphics3d.items.sword import create_sword_3d
    from graphics3d.items.shield import create_shield_3d
    from graphics3d.items.health_potion import create_health_potion_3d
    from graphics3d.items.boots import create_boots_3d
    from graphics3d.items.ring import create_ring_3d
    from graphics3d.items.gold_coin import create_gold_coin_3d
    from graphics3d.items.treasure_chest import create_treasure_chest_3d

    # Create model based on type
    if item_type == c.ITEM_SWORD:
        return create_sword_3d(position, rarity)
    elif item_type == c.ITEM_SHIELD:
        return create_shield_3d(position, rarity)
    elif item_type == c.ITEM_HEALTH_POTION:
        return create_health_potion_3d(position, rarity)
    elif item_type == c.ITEM_BOOTS:
        return create_boots_3d(position, rarity)
    elif item_type == c.ITEM_RING:
        return create_ring_3d(position, rarity)
    elif item_type == c.ITEM_GOLD_COIN:
        return create_gold_coin_3d(position, rarity)
    elif item_type == c.ITEM_TREASURE_CHEST:
        return create_treasure_chest_3d(position, rarity)
    else:
        # Fallback: generic cube
        from ursina import color as ursina_color
        from graphics3d.utils import rgb_to_ursina_color
        return Entity(
            model='cube',
            color=rgb_to_ursina_color(255, 215, 0),  # Gold
            scale=0.3,
            position=position
        )


def update_item_animation(item_entity: Entity, dt: float):
    """
    Update item floating and rotation animations

    Args:
        item_entity: Item entity to animate
        dt: Delta time since last frame
    """
    if not hasattr(item_entity, 'float_time'):
        item_entity.float_time = 0.0

    item_entity.float_time += dt

    # Floating animation (up and down)
    float_height = math.sin(item_entity.float_time * 2.0) * 0.15
    base_y = 0.5  # Base height off ground
    item_entity.y = base_y + float_height

    # Rotation animation (spin around Y axis)
    if hasattr(item_entity, 'rotation_speed'):
        rotation_speed = item_entity.rotation_speed
    else:
        rotation_speed = 50.0  # Default 50 degrees/second

    item_entity.rotation_y = (item_entity.rotation_y + rotation_speed * dt) % 360


def get_rarity_color_ursina(rarity: str):
    """
    Get Ursina color for item rarity

    Args:
        rarity: Item rarity string

    Returns:
        Ursina color object
    """
    from ursina import color as ursina_color

    rarity_colors_rgb = {
        c.RARITY_COMMON: c.COLOR_RARITY_COMMON_RGB,
        c.RARITY_UNCOMMON: c.COLOR_RARITY_UNCOMMON_RGB,
        c.RARITY_RARE: c.COLOR_RARITY_RARE_RGB,
        c.RARITY_EPIC: c.COLOR_RARITY_EPIC_RGB,
        c.RARITY_LEGENDARY: c.COLOR_RARITY_LEGENDARY_RGB,
    }

    rgb_tuple = rarity_colors_rgb.get(rarity, c.COLOR_RARITY_COMMON_RGB)
    return ursina_color.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
