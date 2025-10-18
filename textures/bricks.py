"""
Brick Pattern Generation (Phase 2)

This module generates procedural brick wall textures with:
- Brick pattern with mortar lines (running bond pattern)
- Staggered rows for realism
- Color variation per brick
- Realistic cracks
- Darkness/brightness control

Ported from: ui/screens/title_screen_3d.py:238-284 (_draw_brick_pattern)
"""

import random
from typing import Tuple
from PIL import Image, ImageDraw


def generate_brick_pattern(size: int = 256, darkness: float = 1.0) -> Image.Image:
    """Generate brick pattern with mortar lines.

    Creates a realistic brick wall texture with:
    - Running bond pattern (staggered rows)
    - Individual brick color variation
    - Mortar lines between bricks
    - Hairline cracks on brick surfaces
    - Adjustable brightness via darkness parameter

    Args:
        size: Texture size in pixels (will be square, power of 2 recommended)
        darkness: Brightness multiplier (0.0 = black, 1.0 = normal, <1.0 = darker)

    Returns:
        PIL Image with RGBA brick pattern

    Example:
        >>> brick = generate_brick_pattern(256, darkness=0.8)
        >>> brick.save('brick_texture.png')

    Reference:
        Ported from ui/screens/title_screen_3d.py:238-284
    """
    # Brick colors (varied gray-brown tones)
    brick_base = (65, 60, 55)
    mortar_color = (95, 90, 85, 255)

    # Create image filled with mortar color
    image = Image.new('RGBA', (size, size), color=mortar_color)
    draw = ImageDraw.Draw(image)

    # Brick dimensions
    brick_height = size // 4
    brick_width = size // 3
    mortar_size = 3

    # Draw bricks in 4 rows
    for row in range(4):
        y = row * brick_height

        # Stagger every other row (running bond pattern)
        offset = (brick_width // 2) if row % 2 == 1 else 0

        # Draw bricks across the row (extra columns for wrap-around)
        for col in range(-1, 4):
            x = col * brick_width + offset

            # Create color variation for this brick
            variation = random.randint(-8, 8)
            brick_color = (
                max(0, min(255, brick_base[0] + variation)),
                max(0, min(255, brick_base[1] + variation)),
                max(0, min(255, brick_base[2] + variation)),
                255
            )

            # Draw brick (leaving mortar gaps)
            brick_rect = [
                x + mortar_size,
                y + mortar_size,
                x + brick_width - mortar_size,
                y + brick_height - mortar_size
            ]
            draw.rectangle(brick_rect, fill=brick_color)

            # Add cracks for texture (2 per brick)
            crack_color = (
                max(0, brick_base[0] - 15),
                max(0, brick_base[1] - 15),
                max(0, brick_base[2] - 15),
                255
            )

            for _ in range(2):
                # Random crack position within brick
                crack_x = x + random.randint(mortar_size, brick_width - mortar_size)
                crack_y = y + random.randint(mortar_size, brick_height - mortar_size)
                crack_len = random.randint(5, 15)
                crack_offset_y = random.randint(-3, 3)

                # Draw hairline crack
                draw.line(
                    [crack_x, crack_y, crack_x + crack_len, crack_y + crack_offset_y],
                    fill=crack_color,
                    width=1
                )

    # Apply darkness multiplier if needed
    if darkness != 1.0:
        from textures.generator import darken_image
        image = darken_image(image, factor=darkness)

    return image


def _draw_single_brick(draw: ImageDraw.ImageDraw, x: int, y: int,
                       width: int, height: int, base_color: Tuple[int, int, int],
                       mortar_size: int = 3):
    """Draw a single brick with color variation and cracks.

    Helper function for more complex brick patterns.

    Args:
        draw: PIL ImageDraw object
        x, y: Top-left corner of brick
        width, height: Brick dimensions
        base_color: Base RGB color tuple
        mortar_size: Gap size for mortar
    """
    # Color variation
    variation = random.randint(-8, 8)
    brick_color = (
        max(0, min(255, base_color[0] + variation)),
        max(0, min(255, base_color[1] + variation)),
        max(0, min(255, base_color[2] + variation)),
        255
    )

    # Draw brick
    brick_rect = [
        x + mortar_size,
        y + mortar_size,
        x + width - mortar_size,
        y + height - mortar_size
    ]
    draw.rectangle(brick_rect, fill=brick_color)

    # Add cracks
    crack_color = (
        max(0, base_color[0] - 15),
        max(0, base_color[1] - 15),
        max(0, base_color[2] - 15),
        255
    )

    for _ in range(2):
        crack_x = x + random.randint(mortar_size, width - mortar_size)
        crack_y = y + random.randint(mortar_size, height - mortar_size)
        crack_len = random.randint(5, 15)
        crack_offset_y = random.randint(-3, 3)

        draw.line(
            [crack_x, crack_y, crack_x + crack_len, crack_y + crack_offset_y],
            fill=crack_color,
            width=1
        )
