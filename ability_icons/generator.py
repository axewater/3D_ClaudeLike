"""
Base infrastructure for procedural ability icon generation.

This module provides utilities specifically for generating animated ability icons,
building on the foundation from textures.generator.
"""
import math
import random
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Import utilities from texture generator (avoid duplication)
from textures.generator import (
    TextureGenerator, RandomSeed, blend_images, add_noise,
    blend_colors, ease_in_out, create_linear_gradient_1d
)


class IconGenerator(TextureGenerator):
    """Base class for ability icon generation.

    Extends TextureGenerator with icon-specific methods like
    radial gradients, rotation, and circular masking.

    Args:
        size: Icon size in pixels (typically 256x256)
    """

    def __init__(self, size: int = 256):
        super().__init__(size)
        self.center = (size // 2, size // 2)

    def apply_circular_mask(self, image: Image.Image, feather: int = 10) -> Image.Image:
        """Apply circular mask with feathered edges.

        Args:
            image: Input PIL Image
            feather: Edge softness in pixels (0 = hard edge)

        Returns:
            Masked image with transparent corners
        """
        mask = Image.new('L', (self.size, self.size), 0)
        draw = ImageDraw.Draw(mask)

        # Draw filled circle
        radius = self.size // 2 - 2
        draw.ellipse([self.center[0] - radius, self.center[1] - radius,
                      self.center[0] + radius, self.center[1] + radius],
                     fill=255)

        # Apply gaussian blur for feathering
        if feather > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(feather))

        # Apply mask to image
        result = image.copy()
        result.putalpha(mask)

        return result


def create_radial_gradient(center: Tuple[int, int], radius: int,
                           color1: tuple, color2: tuple,
                           size: int = 256, curve: str = 'linear') -> Image.Image:
    """Create radial gradient from center to edge.

    Args:
        center: Center point (x, y)
        radius: Gradient radius in pixels
        color1: Center color (R, G, B) or (R, G, B, A)
        color2: Edge color (R, G, B) or (R, G, B, A)
        size: Image size (square)
        curve: 'linear', 'ease', or 'exponential'

    Returns:
        PIL Image with radial gradient
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = image.load()

    for y in range(size):
        for x in range(size):
            # Calculate distance from center
            dx = x - center[0]
            dy = y - center[1]
            dist = math.sqrt(dx * dx + dy * dy)

            # Normalize to 0-1
            t = min(1.0, dist / radius)

            # Apply curve
            if curve == 'ease':
                t = ease_in_out(t)
            elif curve == 'exponential':
                t = t * t  # Quadratic falloff

            # Blend colors
            color = blend_colors(color1, color2, t)
            pixels[x, y] = color + (255,) if len(color) == 3 else color

    return image


def rotate_image(image: Image.Image, angle: float, expand: bool = False) -> Image.Image:
    """Rotate image around center.

    Args:
        image: PIL Image to rotate
        angle: Rotation angle in degrees (positive = counter-clockwise)
        expand: If True, expand image to fit rotated content

    Returns:
        Rotated image
    """
    return image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=expand)


def draw_glow(draw: ImageDraw.Draw, center: Tuple[int, int],
              radius: int, color: tuple, intensity: float = 1.0):
    """Draw glowing sphere/orb effect.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        radius: Glow radius
        color: Glow color (R, G, B)
        intensity: Brightness multiplier (0.0 to 1.0)
    """
    # Multiple layers for soft glow
    num_layers = 5
    for i in range(num_layers):
        layer_radius = radius * (1.0 - i / num_layers)
        layer_alpha = int(255 * intensity * (1.0 - i / num_layers) * 0.6)
        layer_color = color + (layer_alpha,)

        draw.ellipse([center[0] - layer_radius, center[1] - layer_radius,
                      center[0] + layer_radius, center[1] + layer_radius],
                     fill=layer_color)


def draw_star(draw: ImageDraw.Draw, center: Tuple[int, int],
              outer_radius: int, inner_radius: int,
              points: int, color: tuple, rotation: float = 0):
    """Draw star shape.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        outer_radius: Distance to star points
        inner_radius: Distance to inner vertices
        points: Number of star points
        color: Fill color (R, G, B) or (R, G, B, A)
        rotation: Rotation angle in degrees
    """
    coords = []
    angle_step = 360.0 / points

    for i in range(points * 2):
        angle = math.radians(i * angle_step / 2 + rotation)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        coords.append((x, y))

    draw.polygon(coords, fill=color)


def draw_spiral(draw: ImageDraw.Draw, center: Tuple[int, int],
                start_radius: float, end_radius: float,
                turns: float, segments: int,
                color: tuple, width: int = 3,
                rotation_offset: float = 0):
    """Draw spiral curve from center outward.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        start_radius: Starting radius (center)
        end_radius: Ending radius (outer)
        turns: Number of complete revolutions
        segments: Number of line segments (higher = smoother)
        color: Line color (R, G, B) or (R, G, B, A)
        width: Line width in pixels
        rotation_offset: Starting angle in degrees
    """
    coords = []

    for i in range(segments):
        t = i / (segments - 1)
        angle = math.radians(t * turns * 360 + rotation_offset)
        radius = start_radius + (end_radius - start_radius) * t

        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        coords.append((x, y))

    # Draw line segments
    for i in range(len(coords) - 1):
        draw.line([coords[i], coords[i + 1]], fill=color, width=width)


def create_particle_field(size: int, num_particles: int,
                          color_range: Tuple[tuple, tuple],
                          min_size: int = 2, max_size: int = 8,
                          distribution: str = 'random') -> Image.Image:
    """Generate particle field for magical effects.

    Args:
        size: Image size (square)
        num_particles: Number of particles to generate
        color_range: (min_color, max_color) tuples for random colors
        min_size: Minimum particle radius
        max_size: Maximum particle radius
        distribution: 'random', 'center' (concentrated), or 'edge' (outer ring)

    Returns:
        PIL Image with particle field
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    for _ in range(num_particles):
        # Determine position based on distribution
        if distribution == 'center':
            # Gaussian distribution around center
            distance = abs(random.gauss(0, size / 6))
            angle = random.uniform(0, 2 * math.pi)
            x = center[0] + distance * math.cos(angle)
            y = center[1] + distance * math.sin(angle)
        elif distribution == 'edge':
            # Ring distribution
            distance = random.uniform(size * 0.3, size * 0.5)
            angle = random.uniform(0, 2 * math.pi)
            x = center[0] + distance * math.cos(angle)
            y = center[1] + distance * math.sin(angle)
        else:  # random
            x = random.uniform(0, size)
            y = random.uniform(0, size)

        # Random particle size
        particle_size = random.uniform(min_size, max_size)

        # Random color in range
        color = tuple(
            random.randint(color_range[0][i], color_range[1][i])
            for i in range(3)
        )
        alpha = random.randint(150, 255)

        # Draw particle as circle
        draw.ellipse([x - particle_size, y - particle_size,
                      x + particle_size, y + particle_size],
                     fill=color + (alpha,))

    return image


def create_vortex_mask(size: int, center: Tuple[int, int],
                       inner_radius: float, outer_radius: float,
                       twist: float = 0.5) -> Image.Image:
    """Create vortex/swirl mask for distortion effects.

    Args:
        size: Image size (square)
        center: Center point (x, y)
        inner_radius: Inner void radius (normalized 0-1)
        outer_radius: Outer edge radius (normalized 0-1)
        twist: Twist strength (0 = no twist, 1 = heavy twist)

    Returns:
        PIL Image grayscale mask (0-255)
    """
    mask = Image.new('L', (size, size), 0)
    pixels = mask.load()

    max_radius = size / 2

    for y in range(size):
        for x in range(size):
            dx = x - center[0]
            dy = y - center[1]
            distance = math.sqrt(dx * dx + dy * dy) / max_radius

            # Normalize to inner-outer range
            if distance < inner_radius:
                intensity = 0
            elif distance > outer_radius:
                intensity = 0
            else:
                t = (distance - inner_radius) / (outer_radius - inner_radius)
                intensity = int(255 * (1.0 - t))

            pixels[x, y] = intensity

    return mask


def apply_motion_blur(image: Image.Image, angle: float, distance: int) -> Image.Image:
    """Apply directional motion blur effect.

    Args:
        image: Input PIL Image
        angle: Blur direction in degrees (0 = right, 90 = down)
        distance: Blur distance in pixels

    Returns:
        Blurred image
    """
    # Create motion blur kernel
    kernel_size = distance * 2 + 1
    kernel = np.zeros((kernel_size, kernel_size))

    # Draw line through kernel center
    angle_rad = math.radians(angle)
    for i in range(-distance, distance + 1):
        x = int(distance + i * math.cos(angle_rad))
        y = int(distance + i * math.sin(angle_rad))
        if 0 <= x < kernel_size and 0 <= y < kernel_size:
            kernel[y, x] = 1

    # Normalize kernel
    kernel = kernel / np.sum(kernel)

    # Apply convolution (PIL doesn't support this directly, use numpy)
    img_array = np.array(image)
    result_array = np.zeros_like(img_array)

    # Convolve each channel
    from scipy.ndimage import convolve
    for c in range(min(3, img_array.shape[2])):  # RGB only
        result_array[:, :, c] = convolve(img_array[:, :, c], kernel, mode='constant')

    # Preserve alpha channel
    if img_array.shape[2] == 4:
        result_array[:, :, 3] = img_array[:, :, 3]

    return Image.fromarray(result_array.astype(np.uint8))
