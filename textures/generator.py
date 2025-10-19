"""
Base classes and utilities for procedural texture generation.

This module provides the foundation for all texture generators,
including base classes, utility functions, and compositing tools.
"""
import random
from typing import Optional
from PIL import Image, ImageDraw, ImageChops, ImageEnhance
import numpy as np


class TextureGenerator:
    """Base class for all texture generators.

    Provides a common interface for generating procedural textures
    using PIL/Pillow. Subclasses should override the generate() method.

    Args:
        size: Texture size in pixels (power of 2 recommended)

    Example:
        class MyGenerator(TextureGenerator):
            def generate(self):
                self.draw.rectangle([0, 0, self.size, self.size], fill=(255, 0, 0))
                return self.image
    """

    def __init__(self, size: int = 256):
        """Initialize texture generator with given size.

        Args:
            size: Texture dimensions (width and height in pixels)
        """
        self.size = size
        self.image = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def generate(self) -> Image.Image:
        """Generate and return PIL Image.

        This method should be overridden by subclasses to implement
        specific texture generation logic.

        Returns:
            PIL Image object with RGBA format

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def to_ursina_texture(self):
        """Convert generated image to Ursina Texture object.

        This is a convenience method for Ursina Engine integration.
        The Texture class accepts PIL Image objects directly.

        Returns:
            ursina.Texture object wrapping the generated image

        Example:
            generator = MyGenerator(256)
            texture = generator.to_ursina_texture()
            entity = Entity(model='cube', texture=texture)
        """
        from ursina import Texture
        return Texture(self.generate())


class RandomSeed:
    """Context manager for reproducible random number generation.

    This allows texture generation to be deterministic when needed,
    which is useful for testing, caching, and ensuring consistent results.

    Args:
        seed: Random seed value (integer)

    Example:
        # Generate identical textures with same seed
        with RandomSeed(12345):
            texture1 = generate_brick_pattern()
        with RandomSeed(12345):
            texture2 = generate_brick_pattern()
        # texture1 and texture2 are identical
    """

    def __init__(self, seed: int):
        """Initialize random seed context manager.

        Args:
            seed: Seed value for random number generator
        """
        self.seed = seed
        self.old_state = None

    def __enter__(self):
        """Save current random state and set new seed."""
        self.old_state = random.getstate()
        random.seed(self.seed)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore previous random state."""
        if self.old_state is not None:
            random.setstate(self.old_state)


def blend_images(base: Image.Image, overlay: Image.Image,
                 mode: str = 'multiply', alpha: float = 1.0) -> Image.Image:
    """Blend two PIL images using various composition modes.

    This is the PIL equivalent of QPainter's composition modes.
    Useful for layering effects like moss, weathering, and lighting.

    Args:
        base: Base image (background layer)
        overlay: Overlay image (foreground layer)
        mode: Blending mode - 'multiply', 'add', 'screen', 'overlay', or 'alpha'
        alpha: Opacity of overlay layer (0.0 to 1.0)

    Returns:
        Blended PIL Image

    Example:
        brick = generate_brick_pattern()
        moss = generate_moss_overlay()
        result = blend_images(brick, moss, mode='multiply', alpha=0.8)
    """
    # Ensure images are same size
    if base.size != overlay.size:
        overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)

    # Convert to RGBA if needed
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # Apply alpha to overlay
    if alpha < 1.0:
        overlay = overlay.copy()
        overlay.putalpha(int(255 * alpha))

    # Apply blending mode
    if mode == 'multiply':
        # Multiply blend (darkens)
        return ImageChops.multiply(base, overlay)
    elif mode == 'add':
        # Additive blend (lightens)
        return ImageChops.add(base, overlay)
    elif mode == 'screen':
        # Screen blend (lightens, less harsh than add)
        return ImageChops.screen(base, overlay)
    elif mode == 'overlay':
        # Overlay blend (combines multiply and screen)
        return ImageChops.overlay(base, overlay)
    elif mode == 'alpha':
        # Simple alpha compositing (default PIL behavior)
        return Image.alpha_composite(base, overlay)
    else:
        raise ValueError(f"Unknown blend mode: {mode}")


def add_noise(image: Image.Image, intensity: float = 0.1,
              noise_type: str = 'uniform') -> Image.Image:
    """Add random noise to an image for texture variation.

    This adds subtle variation to make procedural textures look
    more organic and less "computer-generated".

    Args:
        image: Input PIL Image to add noise to
        intensity: Noise strength (0.0 to 1.0, typical 0.05-0.2)
        noise_type: 'uniform' for even noise, 'gaussian' for natural noise

    Returns:
        Image with added noise

    Example:
        brick = generate_brick_pattern()
        noisy_brick = add_noise(brick, intensity=0.1)
    """
    # Convert to numpy array for efficient processing
    img_array = np.array(image)

    # Generate noise based on type
    if noise_type == 'uniform':
        noise = np.random.uniform(-intensity * 255, intensity * 255, img_array.shape)
    elif noise_type == 'gaussian':
        noise = np.random.normal(0, intensity * 255, img_array.shape)
    else:
        raise ValueError(f"Unknown noise type: {noise_type}")

    # Add noise to RGB channels only (preserve alpha)
    noisy = img_array.astype(np.float32)
    if img_array.shape[2] == 4:  # RGBA
        noisy[:, :, :3] += noise[:, :, :3]
    else:  # RGB
        noisy += noise

    # Clip to valid range and convert back
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)

    return Image.fromarray(noisy)


def darken_image(image: Image.Image, factor: float = 0.7) -> Image.Image:
    """Darken an image by multiplying brightness.

    Useful for creating darker texture variants (e.g., shadowed bricks).

    Args:
        image: Input PIL Image
        factor: Darkness multiplier (0.0 = black, 1.0 = unchanged)

    Returns:
        Darkened image

    Example:
        normal_brick = generate_brick_pattern()
        dark_brick = darken_image(normal_brick, factor=0.7)
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_saturation(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """Adjust color saturation of an image.

    Args:
        image: Input PIL Image
        factor: Saturation multiplier (0.0 = grayscale, 1.0 = unchanged, >1.0 = more vibrant)

    Returns:
        Image with adjusted saturation

    Example:
        moss = generate_moss_overlay()
        vibrant_moss = adjust_saturation(moss, factor=1.3)
    """
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


# ===== GRADIENT GENERATION UTILITIES (AAA Quality) =====

def blend_colors(color1: tuple, color2: tuple, alpha: float) -> tuple:
    """Blend two RGB(A) colors with linear interpolation.

    Args:
        color1: First color as (R, G, B) or (R, G, B, A)
        color2: Second color as (R, G, B) or (R, G, B, A)
        alpha: Blend factor (0.0 = color1, 1.0 = color2)

    Returns:
        Blended color tuple (same format as inputs)

    Example:
        mortar = (95, 90, 85)
        brick = (65, 60, 55)
        transition = blend_colors(mortar, brick, 0.5)
        # Returns (80, 75, 70) - halfway between
    """
    # Ensure alpha is in valid range
    alpha = max(0.0, min(1.0, alpha))

    # Blend RGB channels
    r = int(color1[0] * (1 - alpha) + color2[0] * alpha)
    g = int(color1[1] * (1 - alpha) + color2[1] * alpha)
    b = int(color1[2] * (1 - alpha) + color2[2] * alpha)

    # Handle alpha channel if present
    if len(color1) == 4 and len(color2) == 4:
        a = int(color1[3] * (1 - alpha) + color2[3] * alpha)
        return (r, g, b, a)

    return (r, g, b)


def ease_in_out(t: float) -> float:
    """Smooth ease-in-out interpolation curve.

    Creates a smooth S-curve for more natural gradients
    (slow start, fast middle, slow end).

    Args:
        t: Input value (0.0 to 1.0)

    Returns:
        Eased value (0.0 to 1.0)

    Example:
        ease_in_out(0.0)  # Returns 0.0 (slow start)
        ease_in_out(0.5)  # Returns 0.5 (fast middle)
        ease_in_out(1.0)  # Returns 1.0 (slow end)
    """
    # Cubic ease-in-out: 3t² - 2t³
    return t * t * (3.0 - 2.0 * t)


def create_linear_gradient_1d(color1: tuple, color2: tuple,
                               steps: int, curve: str = 'linear') -> list:
    """Create 1D gradient array between two colors.

    Args:
        color1: Start color (R, G, B) or (R, G, B, A)
        color2: End color (R, G, B) or (R, G, B, A)
        steps: Number of gradient steps
        curve: Interpolation curve - 'linear' or 'ease'

    Returns:
        List of color tuples (length = steps)

    Example:
        gradient = create_linear_gradient_1d((95, 90, 85), (65, 60, 55), 10)
        # Returns 10 colors smoothly transitioning from mortar to brick
    """
    gradient = []

    for i in range(steps):
        t = i / max(1, steps - 1)  # Normalize to 0.0-1.0

        # Apply easing curve if requested
        if curve == 'ease':
            t = ease_in_out(t)

        # Blend colors
        color = blend_colors(color1, color2, t)
        gradient.append(color)

    return gradient


def create_depth_gradient(mortar_color: tuple, brick_color: tuple,
                          width: int, shadow_factor: float = 0.7) -> list:
    """Create gradient simulating recessed mortar depth.

    Generates a 4-zone gradient:
    1. Mortar core (lightest)
    2. Shadow zone (darkest - simulates recess)
    3. Brick edge (medium - weathered/beveled)
    4. Brick face (full color)

    Args:
        mortar_color: Mortar base color (R, G, B)
        brick_color: Brick base color (R, G, B)
        width: Total gradient width in pixels
        shadow_factor: Shadow darkness (0.0-1.0, lower = darker)

    Returns:
        List of RGBA color tuples (length = width)

    Example:
        gradient = create_depth_gradient((95, 90, 85), (65, 60, 55), 16)
        # Returns 16 colors: mortar → shadow → edge → brick
    """
    # Calculate zone widths (total = width)
    # 40% mortar core, 20% shadow, 20% edge bevel, 20% brick face
    mortar_width = max(1, int(width * 0.40))
    shadow_width = max(1, int(width * 0.20))
    edge_width = max(1, int(width * 0.20))
    face_width = width - mortar_width - shadow_width - edge_width

    # Define zone colors
    shadow_color = tuple(int(c * shadow_factor) for c in brick_color)  # Darken brick color
    edge_color = tuple(int((brick_color[i] + shadow_color[i]) / 2) for i in range(3))  # Midpoint

    gradient = []

    # Zone 1: Mortar core (flat color)
    for _ in range(mortar_width):
        gradient.append(mortar_color + (255,))

    # Zone 2: Mortar → Shadow (linear transition)
    shadow_gradient = create_linear_gradient_1d(mortar_color, shadow_color, shadow_width, curve='ease')
    for color in shadow_gradient:
        gradient.append(color + (255,))

    # Zone 3: Shadow → Brick edge (linear transition with easing)
    edge_gradient = create_linear_gradient_1d(shadow_color, edge_color, edge_width, curve='ease')
    for color in edge_gradient:
        gradient.append(color + (255,))

    # Zone 4: Edge → Brick face (linear transition)
    face_gradient = create_linear_gradient_1d(edge_color, brick_color, face_width, curve='linear')
    for color in face_gradient:
        gradient.append(color + (255,))

    return gradient


def apply_gradient_to_rect(image: Image.Image, x: int, y: int,
                           width: int, height: int,
                           gradient: list, direction: str = 'horizontal'):
    """Apply a gradient to a rectangular region of an image.

    Args:
        image: PIL Image to modify (RGBA)
        x, y: Top-left corner of rectangle
        width, height: Rectangle dimensions
        gradient: List of RGBA color tuples
        direction: 'horizontal', 'vertical', or 'both'

    Note:
        Modifies image in-place using pixel access.
    """
    pixels = image.load()
    gradient_len = len(gradient)

    if direction == 'horizontal':
        # Apply gradient left to right
        for dy in range(height):
            for dx in range(width):
                if dx < gradient_len:
                    px = x + dx
                    py = y + dy
                    if 0 <= px < image.width and 0 <= py < image.height:
                        pixels[px, py] = gradient[dx]

    elif direction == 'vertical':
        # Apply gradient top to bottom
        for dy in range(height):
            for dx in range(width):
                if dy < gradient_len:
                    px = x + dx
                    py = y + dy
                    if 0 <= px < image.width and 0 <= py < image.height:
                        pixels[px, py] = gradient[dy]

    elif direction == 'both':
        # Apply gradient from all edges (border effect)
        for dy in range(height):
            for dx in range(width):
                # Calculate distance from edge (minimum of all 4 edges)
                dist_from_edge = min(dx, dy, width - dx - 1, height - dy - 1)

                if dist_from_edge < gradient_len:
                    px = x + dx
                    py = y + dy
                    if 0 <= px < image.width and 0 <= py < image.height:
                        pixels[px, py] = gradient[dist_from_edge]
