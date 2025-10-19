"""
Weathering Effects (Phase 3)

This module adds age and wear to textures with:
- Dark stains and spots
- Discoloration patches
- Age marks and erosion
- Variable opacity for realism

Ported from: ui/screens/title_screen_3d.py:285-301 (_add_weathering)
"""

import random
from typing import Optional
from PIL import Image, ImageDraw


def add_weathering(image: Image.Image, intensity: float = 1.0) -> Image.Image:
    """Add age marks, stains, and discoloration to an image.

    Creates multiply-blended dark spots to simulate age, moisture damage,
    and organic staining. The weathering effect darkens affected areas.

    Args:
        image: Input PIL Image to weather (must be RGBA)
        intensity: Weathering strength (0.0 = none, 1.0 = normal, >1.0 = heavy)

    Returns:
        Image with weathering effects applied

    Example:
        >>> brick = generate_brick_pattern()
        >>> aged = add_weathering(brick, intensity=0.8)
        >>> aged.save('aged_brick.png')

    Reference:
        Ported from ui/screens/title_screen_3d.py:285-301
    """
    if intensity <= 0:
        return image

    # Work on a copy
    weathered = image.copy()
    draw = ImageDraw.Draw(weathered, 'RGBA')

    # Calculate number of stains based on intensity
    num_stains = int(15 * intensity)

    # Draw random dark spots and stains
    for _ in range(num_stains):
        x = random.randint(0, image.width)
        y = random.randint(0, image.height)
        size = random.randint(8, 25)
        opacity = random.randint(30, 80)

        # Dark brownish-gray stain color
        stain_color = (50, 45, 40, opacity)

        # Draw elliptical stain
        draw.ellipse(
            [x - size // 2, y - size // 2, x + size // 2, y + size // 2],
            fill=stain_color,
            outline=None
        )

    # Blend using multiply mode (darkens)
    from textures.generator import blend_images
    result = blend_images(image, weathered, mode='multiply', alpha=1.0)

    return result


def add_stains(image: Image.Image, num_stains: int = 15,
               stain_color: Optional[tuple] = None) -> Image.Image:
    """Add dark organic stains to surface.

    This is a more controlled version of weathering that allows
    specifying exact stain count and color.

    Args:
        image: Input PIL Image
        num_stains: Number of stain patches to add
        stain_color: Optional (R, G, B, A) tuple for stains, uses dark brown if None

    Returns:
        Image with stains added

    Example:
        >>> brick = generate_brick_pattern()
        >>> stained = add_stains(brick, num_stains=20, stain_color=(30, 30, 30, 60))
    """
    if num_stains <= 0:
        return image

    # Work on a copy
    stained = image.copy()
    draw = ImageDraw.Draw(stained, 'RGBA')

    # Default stain color (dark brownish-gray)
    if stain_color is None:
        stain_color = (50, 45, 40, 60)

    # Draw stains
    for _ in range(num_stains):
        x = random.randint(0, image.width)
        y = random.randint(0, image.height)
        size = random.randint(8, 25)

        # Vary opacity per stain
        color_with_alpha = stain_color[:3] + (random.randint(30, 80),)

        draw.ellipse(
            [x - size // 2, y - size // 2, x + size // 2, y + size // 2],
            fill=color_with_alpha,
            outline=None
        )

    # Blend using multiply mode
    from textures.generator import blend_images
    result = blend_images(image, stained, mode='multiply', alpha=1.0)

    return result


def add_age_marks(image: Image.Image, num_marks: int = 10) -> Image.Image:
    """Add subtle age marks and discoloration.

    Adds lighter, more subtle weathering than stains.
    Good for general aging without heavy damage.

    Args:
        image: Input PIL Image
        num_marks: Number of age marks to add

    Returns:
        Image with age marks
    """
    if num_marks <= 0:
        return image

    aged = image.copy()
    draw = ImageDraw.Draw(aged, 'RGBA')

    for _ in range(num_marks):
        x = random.randint(0, image.width)
        y = random.randint(0, image.height)
        size = random.randint(15, 40)
        opacity = random.randint(15, 35)  # More subtle

        # Lighter discoloration (grayish)
        mark_color = (80, 75, 70, opacity)

        draw.ellipse(
            [x - size // 2, y - size // 2, x + size // 2, y + size // 2],
            fill=mark_color,
            outline=None
        )

    # Lighter blend
    from textures.generator import blend_images
    result = blend_images(image, aged, mode='multiply', alpha=0.7)

    return result


def add_water_stains(image: Image.Image, num_stains: int = 20) -> Image.Image:
    """Add water damage stains (moisture seepage and dripping).

    Creates realistic water damage with:
    - Dark brownish stains from mineral deposits
    - Slight vertical streaking (water runs down)
    - Variable opacity for depth

    Args:
        image: Input PIL Image
        num_stains: Number of water stain patches to add

    Returns:
        Image with water stains

    Example:
        >>> ceiling = generate_brick_pattern()
        >>> wet_ceiling = add_water_stains(ceiling, num_stains=25)
    """
    if num_stains <= 0:
        return image

    stained = image.copy()
    draw = ImageDraw.Draw(stained, 'RGBA')

    for _ in range(num_stains):
        x = random.randint(0, image.width)
        y = random.randint(0, image.height // 2)  # More likely at top

        # Size varies (water stains spread irregularly)
        width = random.randint(10, 30)
        height = random.randint(15, 50)  # Taller than wide (dripping effect)

        opacity = random.randint(20, 70)

        # Water stain colors (brownish from minerals, rust, mold)
        stain_colors = [
            (60, 55, 40),   # Brown
            (50, 45, 35),   # Dark brown
            (55, 60, 45),   # Greenish brown (mold)
            (70, 50, 40),   # Rust brown
        ]
        stain_rgb = random.choice(stain_colors)
        stain_color = stain_rgb + (opacity,)

        # Draw elongated ellipse (vertical streaking)
        draw.ellipse(
            [x - width // 2, y, x + width // 2, y + height],
            fill=stain_color,
            outline=None
        )

        # Add small drip at bottom (30% chance)
        if random.random() < 0.3:
            drip_length = random.randint(5, 15)
            drip_y = y + height
            drip_width = width // 3

            draw.ellipse(
                [x - drip_width // 2, drip_y,
                 x + drip_width // 2, drip_y + drip_length],
                fill=stain_color,
                outline=None
            )

    # Blend using multiply mode
    from textures.generator import blend_images
    result = blend_images(image, stained, mode='multiply', alpha=1.0)

    return result
