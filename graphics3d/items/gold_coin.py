"""
Gold Coin 3D model - Collectible currency/score item

Procedurally generated 3D model using Ursina primitives.
Gold coins spin rapidly to attract attention.
"""

from ursina import Entity, Vec3
import constants as c
from graphics3d.utils import rgb_to_ursina_color


def create_gold_coin_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D gold coin model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (affects gold color and value)

    Returns:
        Entity: Gold coin 3D model
    """
    # Container entity (invisible parent)
    coin = Entity(position=position)

    # Rarity-based colors
    # Common: Regular gold
    # Higher rarities: Brighter, shinier gold colors
    if rarity == c.RARITY_COMMON:
        coin_color = rgb_to_ursina_color(255, 215, 0)  # Standard gold
        shine_color = rgb_to_ursina_color(255, 235, 100)  # Bright center
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        coin_color = rgb_to_ursina_color(255, 225, 50)  # Brighter gold
        shine_color = rgb_to_ursina_color(255, 245, 150)
        has_glow = False
    elif rarity == c.RARITY_RARE:
        coin_color = rgb_to_ursina_color(255, 235, 100)  # Very bright gold
        shine_color = rgb_to_ursina_color(255, 255, 200)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)
    elif rarity == c.RARITY_EPIC:
        coin_color = rgb_to_ursina_color(255, 200, 255)  # Golden magenta
        shine_color = rgb_to_ursina_color(255, 230, 255)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 150, 255)
    else:  # LEGENDARY
        coin_color = rgb_to_ursina_color(255, 255, 255)  # Brilliant white gold
        shine_color = rgb_to_ursina_color(255, 255, 255)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)

    # Glow for rare+ coins
    if has_glow:
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.35,
            parent=coin,
            position=(0, 0, 0),
            alpha=0.5,
            unlit=True
        )

    # Main coin disc (flattened sphere - wide and thin)
    coin_disc = Entity(
        model='sphere',
        color=coin_color,
        scale=(0.2, 0.04, 0.2),  # Wide (X/Z) and very thin (Y)
        parent=coin,
        position=(0, 0, 0)
    )

    # Embossed center detail (smaller, brighter sphere for shine)
    emboss = Entity(
        model='sphere',
        color=shine_color,
        scale=(0.12, 0.05, 0.12),  # Smaller than main disc
        parent=coin,
        position=(0, 0, 0),
        unlit=True  # Emissive shine
    )

    # Edge ring (thin torus effect using flattened sphere ring)
    # Creates a raised edge around the coin
    edge_ring = Entity(
        model='sphere',
        color=coin_color,
        scale=(0.22, 0.03, 0.22),  # Slightly larger and thinner
        parent=coin,
        position=(0, 0, 0),
        alpha=0.7
    )

    # Store animation state
    coin.float_time = 0.0
    coin.rotation_speed = 120.0  # Fast spin to make it obvious it's rotating

    return coin
