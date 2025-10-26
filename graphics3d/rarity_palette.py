"""
Color palettes for different item types and rarities.

Centralizes rarity-based color schemes to eliminate duplication across item files.
"""

from core import constants as c
from graphics3d.utils import rgb_to_ursina_color


class RarityPalette:
    """
    Centralized color palettes for items by type and rarity.

    Each item type has a dictionary mapping rarity levels to color component dictionaries.
    Colors are stored as RGB tuples (0-255 scale) and converted to Ursina colors on demand.
    """

    # Sword color palettes
    SWORD_COLORS = {
        c.RARITY_COMMON: {
            'blade': (160, 160, 160),  # Iron gray
            'crossguard': (100, 100, 100),  # Dark gray
            'handle': (100, 60, 30),  # Brown leather
            'gem': None,
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'blade': (180, 180, 180),  # Steel
            'crossguard': (180, 140, 80),  # Brass
            'handle': (80, 50, 30),  # Dark leather
            'gem': None,
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'blade': (200, 200, 210),  # Silver steel
            'crossguard': (192, 192, 192),  # Silver
            'handle': (100, 50, 50),  # Red leather
            'gem': (100, 150, 255),  # Blue gem
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'blade': (210, 210, 220),  # Bright steel
            'crossguard': (220, 180, 100),  # Gold
            'handle': (80, 40, 80),  # Purple
            'gem': (200, 50, 255),  # Purple gem
            'has_glow': True,
            'glow': (150, 100, 255),  # Purple glow
        },
        c.RARITY_LEGENDARY: {
            'blade': (220, 220, 240),  # Radiant steel
            'crossguard': (255, 215, 0),  # Bright gold
            'handle': (50, 20, 20),  # Black leather
            'gem': (100, 255, 255),  # Cyan gem
            'has_glow': True,
            'glow': (100, 200, 255),  # Cyan glow
        },
    }

    # Shield color palettes
    SHIELD_COLORS = {
        c.RARITY_COMMON: {
            'face': (120, 90, 60),  # Wooden brown
            'rim': (80, 60, 40),  # Dark brown
            'boss': (140, 140, 140),  # Iron
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'face': (140, 140, 150),  # Steel gray
            'rim': (100, 100, 110),  # Dark steel
            'boss': (180, 140, 80),  # Brass
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'face': (150, 180, 255),  # Blue steel
            'rim': (100, 130, 200),  # Dark blue
            'boss': (192, 192, 192),  # Silver
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'face': (200, 100, 255),  # Purple
            'rim': (150, 50, 200),  # Dark purple
            'boss': (220, 180, 100),  # Gold
            'has_glow': True,
            'glow': (200, 100, 255),
        },
        c.RARITY_LEGENDARY: {
            'face': (255, 215, 0),  # Gold
            'rim': (200, 160, 0),  # Dark gold
            'boss': (100, 200, 255),  # Bright cyan
            'has_glow': True,
            'glow': (100, 200, 255),
        },
    }

    # Boots color palettes
    BOOTS_COLORS = {
        c.RARITY_COMMON: {
            'boot': (100, 60, 30),  # Brown leather
            'accent': (80, 50, 25),  # Dark brown
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'boot': (80, 80, 90),  # Gray leather
            'accent': (120, 120, 130),  # Light gray
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'boot': (100, 130, 200),  # Blue leather
            'accent': (150, 150, 150),  # Silver buckles
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'boot': (150, 50, 200),  # Purple
            'accent': (220, 180, 100),  # Gold buckles
            'has_glow': True,
            'glow': (200, 100, 255),
        },
        c.RARITY_LEGENDARY: {
            'boot': (50, 50, 80),  # Dark mythic
            'accent': (255, 215, 0),  # Bright gold
            'has_glow': True,
            'glow': (100, 200, 255),
        },
    }

    # Ring color palettes
    RING_COLORS = {
        c.RARITY_COMMON: {
            'band': (140, 140, 140),  # Iron
            'gem': (100, 100, 120),  # Dull gray gem
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'band': (180, 140, 80),  # Brass
            'gem': (100, 150, 100),  # Green gem
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'band': (192, 192, 192),  # Silver
            'gem': (100, 150, 255),  # Blue gem
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'band': (220, 180, 100),  # Gold
            'gem': (200, 50, 255),  # Purple gem
            'has_glow': True,
            'glow': (200, 100, 255),
        },
        c.RARITY_LEGENDARY: {
            'band': (255, 215, 0),  # Bright gold
            'gem': (100, 255, 255),  # Cyan gem
            'has_glow': True,
            'glow': (100, 200, 255),
        },
    }

    # Health potion color palettes
    POTION_COLORS = {
        c.RARITY_COMMON: {
            'glass': (200, 200, 210),  # Clear glass
            'liquid': (200, 50, 50),  # Red (health)
            'cork': (100, 60, 30),  # Brown cork
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'glass': (220, 220, 230),  # Clearer glass
            'liquid': (255, 70, 70),  # Brighter red
            'cork': (80, 50, 30),  # Dark cork
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'glass': (230, 230, 240),  # Crystal glass
            'liquid': (255, 100, 100),  # Vibrant red
            'cork': (192, 192, 192),  # Silver cap
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'glass': (240, 240, 250),  # Perfect glass
            'liquid': (255, 50, 150),  # Magenta
            'cork': (220, 180, 100),  # Gold cap
            'has_glow': True,
            'glow': (255, 100, 200),
        },
        c.RARITY_LEGENDARY: {
            'glass': (250, 250, 255),  # Flawless crystal
            'liquid': (100, 255, 255),  # Cyan elixir
            'cork': (255, 215, 0),  # Bright gold cap
            'has_glow': True,
            'glow': (100, 200, 255),
        },
    }

    # Gold coin color palettes
    COIN_COLORS = {
        c.RARITY_COMMON: {
            'coin': (200, 160, 60),  # Copper
            'rim': (150, 120, 40),  # Dark copper
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'coin': (192, 192, 192),  # Silver
            'rim': (140, 140, 140),  # Dark silver
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'coin': (255, 215, 0),  # Gold
            'rim': (200, 160, 0),  # Dark gold
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'coin': (255, 100, 255),  # Magical purple
            'rim': (200, 50, 200),  # Dark purple
            'has_glow': True,
            'glow': (255, 150, 255),
        },
        c.RARITY_LEGENDARY: {
            'coin': (100, 255, 255),  # Ethereal cyan
            'rim': (50, 200, 200),  # Dark cyan
            'has_glow': True,
            'glow': (150, 255, 255),
        },
    }

    # Treasure chest color palettes
    CHEST_COLORS = {
        c.RARITY_COMMON: {
            'wood': (100, 60, 30),  # Brown wood
            'metal': (140, 140, 140),  # Iron bands
            'lock': (100, 100, 100),  # Iron lock
            'has_glow': False,
        },
        c.RARITY_UNCOMMON: {
            'wood': (120, 80, 40),  # Richer brown
            'metal': (180, 140, 80),  # Brass bands
            'lock': (180, 140, 80),  # Brass lock
            'has_glow': False,
        },
        c.RARITY_RARE: {
            'wood': (80, 50, 30),  # Dark wood
            'metal': (192, 192, 192),  # Silver bands
            'lock': (192, 192, 192),  # Silver lock
            'has_glow': False,
        },
        c.RARITY_EPIC: {
            'wood': (60, 30, 50),  # Purple-tinted wood
            'metal': (220, 180, 100),  # Gold bands
            'lock': (200, 50, 255),  # Magical purple lock
            'has_glow': True,
            'glow': (200, 100, 255),
        },
        c.RARITY_LEGENDARY: {
            'wood': (40, 40, 60),  # Mythic dark wood
            'metal': (255, 215, 0),  # Bright gold bands
            'lock': (100, 255, 255),  # Cyan magical lock
            'has_glow': True,
            'glow': (100, 200, 255),
        },
    }

    @staticmethod
    def get_colors(item_type: str, rarity: str) -> dict:
        """
        Get color palette for item type and rarity (as RGB tuples).

        Args:
            item_type: Item type ('sword', 'shield', 'boots', 'ring', 'potion', 'coin', 'chest')
            rarity: Rarity constant (c.RARITY_COMMON, c.RARITY_UNCOMMON, etc.)

        Returns:
            Dictionary of color names to RGB tuples (0-255 scale)
            Returns empty dict if item_type or rarity not found
        """
        palette_name = f'{item_type.upper()}_COLORS'
        palette = getattr(RarityPalette, palette_name, {})
        return palette.get(rarity, {})

    @staticmethod
    def get_ursina_colors(item_type: str, rarity: str) -> dict:
        """
        Get color palette for item type and rarity (as Ursina color objects).

        Args:
            item_type: Item type ('sword', 'shield', 'boots', 'ring', 'potion', 'coin', 'chest')
            rarity: Rarity constant (c.RARITY_COMMON, c.RARITY_UNCOMMON, etc.)

        Returns:
            Dictionary of color names to Ursina color objects
            Returns empty dict if item_type or rarity not found
        """
        rgb_colors = RarityPalette.get_colors(item_type, rarity)
        ursina_colors = {}

        for name, rgb in rgb_colors.items():
            # Skip non-color fields (has_glow, etc.)
            if name == 'has_glow':
                ursina_colors[name] = rgb  # Keep boolean as-is
            elif rgb is None:
                ursina_colors[name] = None  # Keep None as-is
            else:
                # Convert RGB tuple to Ursina color
                ursina_colors[name] = rgb_to_ursina_color(*rgb)

        return ursina_colors
