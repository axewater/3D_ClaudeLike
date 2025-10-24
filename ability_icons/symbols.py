"""
Elemental symbols for ability icons (fire, ice, healing, etc.).

This module provides functions to draw iconic symbols that represent
different ability types and elements.
"""
import math
from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter
from ability_icons.generator import draw_star


def draw_flame_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple, outline_color: tuple = None):
    """Draw stylized flame symbol.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (height)
        color: Fill color (R, G, B) or (R, G, B, A)
        outline_color: Optional outline color
    """
    # Flame shape as irregular teardrop
    # Bottom point
    bottom = (center[0], center[1] + size // 2)
    # Top point
    top = (center[0], center[1] - size // 2)

    # Create flame outline with bezier-like curves
    coords = []

    # Left side curve (bottom to top)
    for i in range(20):
        t = i / 20.0
        # Parametric curve: bulges out on left
        x = center[0] - size * 0.3 * math.sin(t * math.pi) * (1 - t * 0.5)
        y = center[1] + size * 0.5 - t * size
        coords.append((x, y))

    # Right side curve (top to bottom)
    for i in range(20):
        t = i / 20.0
        # Parametric curve: bulges out on right
        x = center[0] + size * 0.3 * math.sin(t * math.pi) * (1 - t * 0.5)
        y = center[1] - size * 0.5 + t * size
        coords.append((x, y))

    # Draw filled flame
    draw.polygon(coords, fill=color, outline=outline_color)

    # Inner flame (smaller, brighter)
    inner_coords = []
    for i in range(20):
        t = i / 20.0
        x = center[0] - size * 0.15 * math.sin(t * math.pi) * (1 - t * 0.5)
        y = center[1] + size * 0.3 - t * size * 0.6
        inner_coords.append((x, y))

    for i in range(20):
        t = i / 20.0
        x = center[0] + size * 0.15 * math.sin(t * math.pi) * (1 - t * 0.5)
        y = center[1] - size * 0.3 + t * size * 0.6
        inner_coords.append((x, y))

    # Brighter inner flame
    if len(color) == 4:
        inner_color = tuple(min(255, int(c * 1.3)) for c in color[:3]) + (color[3],)
    else:
        inner_color = tuple(min(255, int(c * 1.3)) for c in color)

    draw.polygon(inner_coords, fill=inner_color)


def draw_snowflake_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                         size: int, color: tuple, rotation: float = 0):
    """Draw snowflake symbol with 6 arms.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (diameter)
        color: Line color (R, G, B) or (R, G, B, A)
        rotation: Rotation angle in degrees
    """
    radius = size // 2
    line_width = max(2, size // 20)

    # 6 main arms (60 degrees apart)
    for i in range(6):
        angle = math.radians(i * 60 + rotation)

        # Main arm
        end_x = center[0] + radius * math.cos(angle)
        end_y = center[1] + radius * math.sin(angle)
        draw.line([center, (end_x, end_y)], fill=color, width=line_width)

        # Side branches (3 per arm)
        for branch_dist in [0.33, 0.5, 0.67]:
            branch_x = center[0] + radius * branch_dist * math.cos(angle)
            branch_y = center[1] + radius * branch_dist * math.sin(angle)

            # Two branches at 45 degrees
            branch_length = radius * 0.2 * branch_dist
            for branch_angle_offset in [-45, 45]:
                branch_angle = angle + math.radians(branch_angle_offset)
                branch_end_x = branch_x + branch_length * math.cos(branch_angle)
                branch_end_y = branch_y + branch_length * math.sin(branch_angle)
                draw.line([(branch_x, branch_y), (branch_end_x, branch_end_y)],
                         fill=color, width=max(1, line_width - 1))

    # Center circle
    center_radius = size * 0.08
    draw.ellipse([center[0] - center_radius, center[1] - center_radius,
                  center[0] + center_radius, center[1] + center_radius],
                 fill=color)


def draw_heart_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple, outline_color: tuple = None):
    """Draw heart symbol for healing abilities.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (height)
        color: Fill color (R, G, B) or (R, G, B, A)
        outline_color: Optional outline color
    """
    # Heart shape made from two circles and a triangle
    radius = size // 4

    # Top two circles
    left_circle_center = (center[0] - radius // 2, center[1] - size // 4)
    right_circle_center = (center[0] + radius // 2, center[1] - size // 4)

    draw.ellipse([left_circle_center[0] - radius, left_circle_center[1] - radius,
                  left_circle_center[0] + radius, left_circle_center[1] + radius],
                 fill=color, outline=outline_color)

    draw.ellipse([right_circle_center[0] - radius, right_circle_center[1] - radius,
                  right_circle_center[0] + radius, right_circle_center[1] + radius],
                 fill=color, outline=outline_color)

    # Bottom triangle
    triangle_points = [
        (center[0] - size // 2, center[1] - size // 6),
        (center[0] + size // 2, center[1] - size // 6),
        (center[0], center[1] + size // 2)
    ]

    draw.polygon(triangle_points, fill=color, outline=outline_color)


def draw_cross_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple):
    """Draw medical cross symbol.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size
        color: Fill color (R, G, B) or (R, G, B, A)
    """
    arm_width = size // 4
    arm_length = size // 2

    # Horizontal bar
    draw.rectangle([center[0] - arm_length, center[1] - arm_width,
                   center[0] + arm_length, center[1] + arm_width],
                  fill=color)

    # Vertical bar
    draw.rectangle([center[0] - arm_width, center[1] - arm_length,
                   center[0] + arm_width, center[1] + arm_length],
                  fill=color)


def draw_arrow_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple, angle: float = 0):
    """Draw arrow symbol pointing in specified direction.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (length)
        color: Fill color (R, G, B) or (R, G, B, A)
        angle: Arrow direction in degrees (0 = right, 90 = down)
    """
    angle_rad = math.radians(angle)

    # Arrow shaft
    shaft_length = size * 0.6
    shaft_width = size * 0.1

    # Arrow head
    head_length = size * 0.4
    head_width = size * 0.3

    # Calculate points (pointing right, then rotate)
    points = [
        # Shaft
        (-shaft_length / 2, -shaft_width / 2),
        (shaft_length / 2 - head_length, -shaft_width / 2),
        # Head top
        (shaft_length / 2 - head_length, -head_width / 2),
        (shaft_length / 2, 0),  # Tip
        (shaft_length / 2 - head_length, head_width / 2),
        # Head bottom
        (shaft_length / 2 - head_length, shaft_width / 2),
        # Shaft bottom
        (-shaft_length / 2, shaft_width / 2),
    ]

    # Rotate and translate points
    rotated_points = []
    for px, py in points:
        # Rotate
        rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
        ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
        # Translate to center
        rotated_points.append((center[0] + rx, center[1] + ry))

    draw.polygon(rotated_points, fill=color)


def draw_skull_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple):
    """Draw simplified skull symbol for shadow/death abilities.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size
        color: Fill color (R, G, B) or (R, G, B, A)
    """
    # Skull (rounded rectangle for simplicity)
    skull_width = size * 0.6
    skull_height = size * 0.5

    draw.ellipse([center[0] - skull_width / 2, center[1] - skull_height / 2,
                  center[0] + skull_width / 2, center[1] + skull_height / 2],
                 fill=color)

    # Eye sockets (dark circles)
    eye_radius = size * 0.08
    eye_y = center[1] - size * 0.1

    # Left eye
    draw.ellipse([center[0] - size * 0.2 - eye_radius, eye_y - eye_radius,
                  center[0] - size * 0.2 + eye_radius, eye_y + eye_radius],
                 fill=(0, 0, 0, 255))

    # Right eye
    draw.ellipse([center[0] + size * 0.2 - eye_radius, eye_y - eye_radius,
                  center[0] + size * 0.2 + eye_radius, eye_y + eye_radius],
                 fill=(0, 0, 0, 255))

    # Nose (small triangle)
    nose_size = size * 0.1
    nose_y = center[1] + size * 0.05
    draw.polygon([
        (center[0], nose_y - nose_size),
        (center[0] - nose_size * 0.6, nose_y + nose_size),
        (center[0] + nose_size * 0.6, nose_y + nose_size)
    ], fill=(0, 0, 0, 255))


def draw_blade_symbol(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple, rotation: float = 0):
    """Draw spinning blade/sword symbol.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size
        color: Fill color (R, G, B) or (R, G, B, A)
        rotation: Rotation angle in degrees
    """
    # Draw as elongated diamond (blade shape)
    angle_rad = math.radians(rotation)

    blade_length = size * 0.8
    blade_width = size * 0.15

    # Four points of blade
    points = [
        (blade_length / 2, 0),  # Tip
        (0, blade_width / 2),   # Side
        (-blade_length / 2, 0), # Base
        (0, -blade_width / 2),  # Other side
    ]

    # Rotate and translate
    rotated_points = []
    for px, py in points:
        rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
        ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
        rotated_points.append((center[0] + rx, center[1] + ry))

    draw.polygon(rotated_points, fill=color)


def draw_lightning_bolt(draw: ImageDraw.Draw, center: Tuple[int, int],
                       size: int, color: tuple):
    """Draw lightning bolt symbol.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (height)
        color: Fill color (R, G, B) or (R, G, B, A)
    """
    # Zigzag lightning shape
    points = [
        (center[0] + size * 0.1, center[1] - size * 0.5),  # Top
        (center[0] + size * 0.2, center[1] - size * 0.1),  # Right mid
        (center[0] + size * 0.4, center[1]),               # Right kink
        (center[0], center[1] + size * 0.1),               # Center
        (center[0] - size * 0.2, center[1] + size * 0.5),  # Bottom left
        (center[0] - size * 0.1, center[1] + size * 0.2),  # Left mid
        (center[0] - size * 0.3, center[1]),               # Left kink
    ]

    draw.polygon(points, fill=color)


def draw_magic_circle(draw: ImageDraw.Draw, center: Tuple[int, int],
                     size: int, color: tuple, rotation: float = 0,
                     complexity: int = 2):
    """Draw arcane magic circle with geometric patterns.

    Args:
        draw: PIL ImageDraw object
        center: Center point (x, y)
        size: Symbol size (diameter)
        color: Line color (R, G, B) or (R, G, B, A)
        rotation: Rotation angle in degrees
        complexity: Detail level (1-3)
    """
    radius = size // 2
    line_width = max(2, size // 40)

    # Outer circle
    draw.ellipse([center[0] - radius, center[1] - radius,
                  center[0] + radius, center[1] + radius],
                 outline=color, width=line_width)

    # Inner circle
    inner_radius = radius * 0.7
    draw.ellipse([center[0] - inner_radius, center[1] - inner_radius,
                  center[0] + inner_radius, center[1] + inner_radius],
                 outline=color, width=line_width)

    # Geometric star pattern
    num_points = 5 if complexity == 1 else 6 if complexity == 2 else 8
    star_radius = inner_radius * 0.9

    for i in range(num_points):
        angle = math.radians(i * (360 / num_points) + rotation)
        x = center[0] + star_radius * math.cos(angle)
        y = center[1] + star_radius * math.sin(angle)

        # Connect to opposite point
        opp_idx = (i + num_points // 2) % num_points
        opp_angle = math.radians(opp_idx * (360 / num_points) + rotation)
        opp_x = center[0] + star_radius * math.cos(opp_angle)
        opp_y = center[1] + star_radius * math.sin(opp_angle)

        draw.line([(x, y), (opp_x, opp_y)], fill=color, width=line_width)

    # Center dot
    center_radius = size * 0.05
    draw.ellipse([center[0] - center_radius, center[1] - center_radius,
                  center[0] + center_radius, center[1] + center_radius],
                 fill=color)


def create_symbol_image(symbol_name: str, size: int, color: tuple,
                       rotation: float = 0, **kwargs) -> Image.Image:
    """Create symbol as standalone image.

    Args:
        symbol_name: Symbol type ('flame', 'snowflake', 'heart', 'cross', 'arrow',
                                  'skull', 'blade', 'lightning', 'magic_circle')
        size: Image size (square)
        color: Symbol color (R, G, B) or (R, G, B, A)
        rotation: Rotation angle in degrees
        **kwargs: Additional symbol-specific arguments

    Returns:
        PIL Image with symbol
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)
    symbol_size = int(size * 0.6)

    if symbol_name == 'flame':
        draw_flame_symbol(draw, center, symbol_size, color, kwargs.get('outline_color'))
    elif symbol_name == 'snowflake':
        draw_snowflake_symbol(draw, center, symbol_size, color, rotation)
    elif symbol_name == 'heart':
        draw_heart_symbol(draw, center, symbol_size, color, kwargs.get('outline_color'))
    elif symbol_name == 'cross':
        draw_cross_symbol(draw, center, symbol_size, color)
    elif symbol_name == 'arrow':
        draw_arrow_symbol(draw, center, symbol_size, color, rotation)
    elif symbol_name == 'skull':
        draw_skull_symbol(draw, center, symbol_size, color)
    elif symbol_name == 'blade':
        draw_blade_symbol(draw, center, symbol_size, color, rotation)
    elif symbol_name == 'lightning':
        draw_lightning_bolt(draw, center, symbol_size, color)
    elif symbol_name == 'magic_circle':
        complexity = kwargs.get('complexity', 2)
        draw_magic_circle(draw, center, symbol_size, color, rotation, complexity)
    else:
        raise ValueError(f"Unknown symbol: {symbol_name}")

    return image
