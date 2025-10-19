"""
Fog of War Texture Generation

Generates animated fog textures for unexplored areas with:
- Grey/white cloud-like base
- Purple and black circles swirling around
- Clear, large features (visible at distance)
- Designed for UV scrolling animation
"""

import random
import math
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


def generate_cloud_noise(size: int, scale: float = 50.0) -> np.ndarray:
    """
    Generate cloud-like noise pattern using simple fractal noise.

    Args:
        size: Image size (square)
        scale: Noise scale (lower = larger features)

    Returns:
        2D numpy array with noise values (0-1)
    """
    # Create coordinate grids
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)

    # Create multiple octaves of simple noise for fractal effect
    noise = np.zeros((size, size))

    for octave in range(4):
        freq = 2 ** octave
        amp = 1.0 / (2 ** octave)

        # Simple sine/cosine based noise (fast, no external deps)
        noise_layer = (
            np.sin(X * freq * scale + random.random() * 10) *
            np.cos(Y * freq * scale + random.random() * 10) *
            amp
        )
        noise += noise_layer

    # Normalize to 0-1
    noise = (noise - noise.min()) / (noise.max() - noise.min())

    return noise


def draw_swirl_circle(draw: ImageDraw.ImageDraw, cx: float, cy: float,
                      radius: float, color: Tuple[int, int, int, int],
                      num_tendrils: int = 8):
    """
    Draw a circle with swirling tendrils emanating from it.

    Args:
        draw: PIL ImageDraw object
        cx, cy: Center position
        radius: Circle radius
        color: RGBA color tuple
        num_tendrils: Number of swirling tendrils
    """
    # Draw main circle (solid core)
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=color,
        outline=None
    )

    # Draw softer outer glow
    glow_radius = radius * 1.5
    glow_color = color[:3] + (int(color[3] * 0.4),)
    draw.ellipse(
        [cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius],
        fill=glow_color,
        outline=None
    )

    # Draw swirling tendrils
    for i in range(num_tendrils):
        angle_start = (2 * math.pi * i) / num_tendrils + random.uniform(-0.3, 0.3)

        # Each tendril is a curved line of decreasing circles
        num_segments = random.randint(5, 10)
        for seg in range(num_segments):
            t = seg / num_segments

            # Spiral outward with curve
            spiral_radius = radius + (radius * 2 * t)
            spiral_angle = angle_start + (t * math.pi * 0.5)  # Curve amount

            seg_x = cx + spiral_radius * math.cos(spiral_angle)
            seg_y = cy + spiral_radius * math.sin(spiral_angle)
            seg_size = radius * 0.3 * (1.0 - t * 0.7)

            # Fade out tendril
            seg_color = color[:3] + (int(color[3] * (1.0 - t * 0.8)),)

            draw.ellipse(
                [seg_x - seg_size, seg_y - seg_size,
                 seg_x + seg_size, seg_y + seg_size],
                fill=seg_color,
                outline=None
            )


def create_radial_gradient_mask(size: int, falloff: float = 0.8) -> np.ndarray:
    """
    Create a radial alpha gradient mask for fog edges.

    Center is fully opaque (1.0), edges fade to transparent (0.0).

    Args:
        size: Image size (square)
        falloff: Falloff curve power (higher = sharper edge, lower = softer)

    Returns:
        2D numpy array with alpha values (0-1)
    """
    center = size / 2
    y, x = np.ogrid[:size, :size]

    # Calculate distance from center for each pixel
    # Normalize to 0-1 range (0 at center, 1 at corners)
    dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)
    max_dist = np.sqrt(2) * center  # Distance to corner
    normalized_dist = dist_from_center / max_dist

    # Apply falloff curve (1.0 at center, 0.0 at edges)
    # Use power curve for smooth but visible falloff
    alpha_mask = np.clip(1.0 - (normalized_dist ** falloff), 0.0, 1.0)

    return alpha_mask


def generate_fog_texture(size: int = 512, seed: int = None) -> Image.Image:
    """
    Generate animated fog-of-war texture with clouds and swirling circles.

    Creates a texture with:
    - Grey/white cloud base
    - Purple and black circles with swirling tendrils
    - Large, clear features visible at distance
    - Radial alpha gradient for natural edge bleeding

    Args:
        size: Texture size (power of 2 recommended, 512+ for clarity)
        seed: Random seed for reproducibility

    Returns:
        PIL Image with RGBA fog texture (transparent edges)

    Example:
        >>> fog = generate_fog_texture(512)
        >>> fog.save('fog_of_war.png')
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # 1. Generate cloud-like base
    cloud_noise = generate_cloud_noise(size, scale=15.0)

    # Convert noise to grey/white clouds (lighter = more cloudy)
    cloud_base = (cloud_noise * 100 + 155).astype(np.uint8)  # 155-255 range (light grey to white)

    # Create base image
    base_image = Image.new('RGBA', (size, size), (60, 55, 70, 255))  # Dark purple-grey base

    # Add clouds as alpha-blended layer
    cloud_layer = Image.new('RGBA', (size, size))
    for y in range(size):
        for x in range(size):
            brightness = cloud_base[y, x]
            # White clouds with transparency based on noise
            alpha = int(brightness * 0.3)  # Semi-transparent
            cloud_layer.putpixel((x, y), (200, 200, 220, alpha))

    # Apply gaussian blur for soft clouds
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(radius=size // 40))

    # Composite clouds onto base
    result = Image.alpha_composite(base_image, cloud_layer)

    # 2. Add swirling circles overlay
    circle_overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle_overlay)

    # Purple circles (8-12 large ones)
    num_purple = random.randint(8, 12)
    for _ in range(num_purple):
        cx = random.randint(-size // 4, size + size // 4)  # Allow overflow for tiling
        cy = random.randint(-size // 4, size + size // 4)
        radius = random.randint(size // 15, size // 8)  # Large circles (30-60px for 512)
        opacity = random.randint(80, 140)

        # Purple color with variation
        purple = (
            random.randint(100, 160),  # R
            random.randint(40, 100),   # G
            random.randint(150, 220),  # B
            opacity
        )

        draw_swirl_circle(draw, cx, cy, radius, purple, num_tendrils=random.randint(4, 8))

    # Black circles (6-10 medium ones)
    num_black = random.randint(6, 10)
    for _ in range(num_black):
        cx = random.randint(-size // 4, size + size // 4)
        cy = random.randint(-size // 4, size + size // 4)
        radius = random.randint(size // 20, size // 12)  # Medium circles (25-40px for 512)
        opacity = random.randint(100, 160)

        # Black/dark purple color
        black = (
            random.randint(10, 40),
            random.randint(5, 30),
            random.randint(20, 50),
            opacity
        )

        draw_swirl_circle(draw, cx, cy, radius, black, num_tendrils=random.randint(3, 6))

    # Apply slight blur to circles for ethereal effect
    circle_overlay = circle_overlay.filter(ImageFilter.GaussianBlur(radius=size // 80))

    # Composite circles onto result
    result = Image.alpha_composite(result, circle_overlay)

    # 3. Add final subtle noise for texture
    result_array = np.array(result)
    noise = np.random.normal(0, 5, result_array.shape).astype(np.int16)
    result_array = np.clip(result_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    result = Image.fromarray(result_array)

    # 4. Apply radial alpha gradient for edge bleeding
    # This allows oversized fog cubes to naturally fade into adjacent tiles
    alpha_mask = create_radial_gradient_mask(size, falloff=0.6)  # Soft falloff

    # Multiply existing alpha channel by gradient mask
    result_array = np.array(result)
    result_array[:, :, 3] = (result_array[:, :, 3] * alpha_mask).astype(np.uint8)
    result = Image.fromarray(result_array)

    return result


def get_fog_of_war_texture(size: int = 512) -> 'Texture':
    """
    Get fog-of-war texture for Ursina Engine.

    Generates a procedural fog texture with swirling purple/black circles
    on a grey/white cloud base. Designed for UV animation.

    Args:
        size: Texture size (512+ recommended for clarity at distance)

    Returns:
        Ursina Texture object

    Example:
        >>> from ursina import Entity
        >>> fog_texture = get_fog_of_war_texture(512)
        >>> fog_plane = Entity(model='plane', texture=fog_texture, alpha=0.7)
    """
    from ursina import Texture

    # Generate fog texture (use deterministic seed for consistency across tiles)
    fog_image = generate_fog_texture(size=size, seed=42)

    return Texture(fog_image)


if __name__ == '__main__':
    # Test texture generation
    print("Generating fog-of-war texture...")
    fog = generate_fog_texture(512)
    fog.save('/tmp/fog_test.png')
    print("✓ Saved test texture to /tmp/fog_test.png")
