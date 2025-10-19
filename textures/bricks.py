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


def _apply_curved_gradient_to_rect(image: Image.Image, x: int, y: int,
                                   width: int, height: int, gradient: list):
    """Apply gradient with curved/beveled edges for organic mortar look.

    Adds sine wave curvature to brick edges to create rounded/beveled appearance
    instead of sharp geometric transitions.

    Args:
        image: PIL Image to modify
        x, y: Top-left corner of rectangle
        width, height: Rectangle dimensions
        gradient: List of RGBA color tuples
    """
    import math
    pixels = image.load()
    gradient_len = len(gradient)

    # Apply gradient from all edges with curvature
    for dy in range(height):
        for dx in range(width):
            # Calculate distance from edge (minimum of all 4 edges)
            dist_from_edge = min(dx, dy, width - dx - 1, height - dy - 1)

            if dist_from_edge < gradient_len:
                # Add sine wave curvature for organic rounded edges
                # This makes mortar joints appear curved/beveled instead of straight
                t = dist_from_edge / gradient_len  # 0.0 at edge, 1.0 at center

                # Apply ease-in-out curve (sine wave for smooth rounding)
                curved_t = math.sin(t * math.pi / 2)  # Smooth S-curve
                curved_dist = int(curved_t * gradient_len)
                curved_dist = min(curved_dist, gradient_len - 1)

                px = x + dx
                py = y + dy
                if 0 <= px < image.width and 0 <= py < image.height:
                    pixels[px, py] = gradient[curved_dist]


def generate_brick_pattern(size: int = 1024, darkness: float = 1.0) -> Image.Image:
    """Generate brick pattern with smooth gradient mortar joints (AAA Quality).

    Creates a realistic brick wall texture with:
    - Running bond pattern (staggered rows)
    - Individual brick color variation
    - Smooth gradient mortar joints (simulates recessed depth)
    - 4-zone gradients: mortar core → shadow → brick edge → brick face
    - Hairline cracks on brick surfaces
    - Adjustable brightness via darkness parameter

    Args:
        size: Texture size in pixels (1024 recommended for AAA quality, power of 2)
        darkness: Brightness multiplier (0.0 = black, 1.0 = normal, <1.0 = darker)

    Returns:
        PIL Image with RGBA brick pattern

    Example:
        brick = generate_brick_pattern(1024, darkness=0.8)
        brick.save('brick_texture.png')

    Technical Details:
        - At 1024px: 341×256px bricks, 16px mortar joints
        - Gradient zones (16px): 6px core + 3px shadow + 3px edge + 4px face
        - Uses numpy-based smooth gradients for depth simulation
    """
    from textures.generator import create_depth_gradient, apply_gradient_to_rect

    # Brick colors (varied gray-brown tones)
    brick_base = (65, 60, 55)
    mortar_color = (95, 90, 85)

    # Mortar width scales with texture size
    # At 1024px: 16px mortar (prominent gradients)
    # At 512px: 8px mortar (scaled down)
    mortar_size = max(8, int(size * 0.015625))  # 16px at 1024, 8px at 512

    # Create image filled with mortar color
    image = Image.new('RGBA', (size, size), color=mortar_color + (255,))
    draw = ImageDraw.Draw(image)

    # Brick dimensions
    brick_height = size // 4
    brick_width = size // 3

    # Pre-generate depth gradient for mortar joints
    # This gradient simulates recessed mortar with shadow zones
    gradient = create_depth_gradient(mortar_color, brick_base, mortar_size, shadow_factor=0.6)

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
                max(0, min(255, brick_base[2] + variation))
            )

            # Generate per-brick gradient (with color variation)
            brick_gradient = create_depth_gradient(mortar_color, brick_color, mortar_size, shadow_factor=0.6)

            # Define brick area (full area including gradient zones)
            brick_x = x
            brick_y = y
            brick_w = brick_width
            brick_h = brick_height

            # Apply curved gradients from all 4 edges inward
            # This creates the depth effect: mortar → shadow → edge → brick face
            # Using curved gradient for organic rounded/beveled appearance
            _apply_curved_gradient_to_rect(image, brick_x, brick_y, brick_w, brick_h,
                                          brick_gradient)

            # Add cracks for texture (2-3 per brick, scaled to size)
            crack_color = (
                max(0, brick_color[0] - 15),
                max(0, brick_color[1] - 15),
                max(0, brick_color[2] - 15),
                255
            )

            num_cracks = random.randint(2, 3)
            for _ in range(num_cracks):
                # Random crack position within brick interior (avoid gradient zones)
                crack_margin = mortar_size + 5
                crack_x = x + random.randint(crack_margin, brick_width - crack_margin)
                crack_y = y + random.randint(crack_margin, brick_height - crack_margin)
                crack_len = random.randint(int(size * 0.01), int(size * 0.025))  # Scale with resolution
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


def generate_normal_map_from_brick_texture(brick_pil: Image.Image, strength: float = 2.0) -> Image.Image:
    """Generate normal map from brick texture for bump mapping.

    Converts a brick pattern texture into a normal map by:
    1. Converting to grayscale (luminance represents height)
    2. Computing gradients using Sobel edge detection
    3. Converting gradients to surface normals
    4. Encoding normals as RGB values

    The resulting normal map works with Panda3D's auto shader generator
    to create realistic lighting with recessed mortar joints.

    Args:
        brick_pil: Input brick texture (PIL Image)
        strength: Normal strength multiplier (higher = more pronounced depth)
                  Default 2.0 gives visible but realistic bump effect
                  Range: 1.0 (subtle) to 4.0 (extreme)

    Returns:
        PIL Image in RGB mode with encoded normal vectors
        - Red channel: X normal component (left/right surface tilt)
        - Green channel: Y normal component (up/down surface tilt)
        - Blue channel: Z normal component (facing camera)

    Technical Details:
        - Normals are computed as: N = normalize([-∂z/∂x, -∂z/∂y, 1])
        - Encoded to RGB: (N + 1.0) * 0.5 * 255
        - Flat surfaces appear as (128, 128, 255) - blue/purple tint
        - Recessed mortar has normals pointing inward (darker red/green)
        - Raised brick edges have normals pointing outward (brighter red/green)

    Example:
        >>> brick = generate_brick_pattern(1024)
        >>> normal_map = generate_normal_map_from_brick_texture(brick, strength=2.0)
        >>> normal_map.save('brick_normals.png')  # Should look purple/blue
    """
    from scipy.ndimage import sobel
    import numpy as np

    # Convert to grayscale numpy array (luminance = height)
    # Brighter pixels = higher surfaces (brick faces)
    # Darker pixels = lower surfaces (mortar joints)
    gray = np.array(brick_pil.convert('L'), dtype=np.float32)

    # Apply Sobel operator to detect edges/gradients
    # These gradients represent the rate of height change
    sobel_x = sobel(gray, axis=1) * strength  # Horizontal gradient (∂z/∂x)
    sobel_y = sobel(gray, axis=0) * strength  # Vertical gradient (∂z/∂y)

    # Compute surface normals from gradients
    # Normal vector points perpendicular to the surface
    # Formula: N = [-∂z/∂x, -∂z/∂y, 1] (negated for correct lighting direction)
    normals = np.zeros((*gray.shape, 3), dtype=np.float32)
    normals[:, :, 0] = -sobel_x  # X component (tilt left/right)
    normals[:, :, 1] = -sobel_y  # Y component (tilt up/down)
    normals[:, :, 2] = 1.0       # Z component (always pointing toward camera)

    # Normalize vectors to unit length
    # This ensures consistent lighting intensity regardless of slope
    norm = np.sqrt(np.sum(normals**2, axis=2, keepdims=True))
    normals = normals / (norm + 1e-6)  # Add epsilon to prevent division by zero

    # Encode normals to RGB color space
    # Map from [-1, 1] range to [0, 255] range
    # Neutral normal (0, 0, 1) becomes (128, 128, 255) = purple/blue
    normal_map = ((normals + 1.0) * 0.5 * 255).astype(np.uint8)

    return Image.fromarray(normal_map, mode='RGB')
