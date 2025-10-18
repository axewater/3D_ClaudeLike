"""
Organic Effects - Moss Generation (Phase 3)

This module generates organic moss growth patterns with:
- Dense moss base covering top of texture
- Irregular wavy bottom edges
- Draping tendrils growing downward
- Organic patches with satellite clusters
- Color variation in greens
- Spreading veins and speckles

Ported from: ui/screens/title_screen_3d.py:303-567
- _draw_organic_moss_patch (lines 303-415)
- _draw_dense_moss_base (lines 417-491)
- _generate_moss_overlay (lines 493-567)
"""

import random
import math
from typing import List, Tuple
from PIL import Image, ImageDraw


# Moss color palette (varied dark greens with some yellow-green)
MOSS_COLORS = [
    (40, 80, 35),   # Dark green
    (35, 75, 30),   # Darker green
    (45, 85, 40),   # Medium green
    (30, 70, 25),   # Deep green
    (50, 90, 35),   # Lighter green
    (45, 75, 25),   # Olive green
]


def draw_moss_patch(draw: ImageDraw.ImageDraw, x: float, y: float,
                   size: float, moss_color: Tuple[int, int, int, int],
                   draping: bool = False):
    """Draw organic moss patch with irregular edges and spreading patterns.

    Creates a complex organic-looking moss patch with:
    - Irregular polygon main shape
    - Multiple opacity layers for depth
    - Satellite clusters (spreading moss)
    - Thin tendrils/veins
    - Tiny speckles for organic texture

    Args:
        draw: PIL ImageDraw object
        x, y: Center position of patch
        size: Base radius
        moss_color: RGBA color tuple
        draping: If True, tendrils grow primarily downward for draping effect

    Reference:
        Ported from ui/screens/title_screen_3d.py:303-415
    """
    # Main irregular blob shape (using polygon)
    num_points = random.randint(8, 16)
    points = []
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        # Vary the radius randomly for irregular edges
        radius_var = random.uniform(0.5, 1.0)
        radius = size * radius_var

        # Add some wobble to the angle
        angle_wobble = random.uniform(-0.3, 0.3)
        px = x + radius * math.cos(angle + angle_wobble)
        py = y + radius * math.sin(angle + angle_wobble)
        points.append((px, py))

    # Draw main patch with multiple opacity layers for depth
    # Outer layer (lighter, more transparent)
    outer_color = moss_color[:3] + (int(moss_color[3] * 0.4),)
    draw.polygon(points, fill=outer_color, outline=None)

    # Inner layer (darker, more opaque) - slightly smaller
    inner_points = []
    for px, py in points:
        # Move point toward center
        dx = px - x
        dy = py - y
        inner_points.append((x + dx * 0.6, y + dy * 0.6))

    inner_color = moss_color
    draw.polygon(inner_points, fill=inner_color, outline=None)

    # Add small satellite clusters around main patch (moss spreading)
    num_satellites = random.randint(2, 5)
    for _ in range(num_satellites):
        # Position near main patch
        sat_angle = random.uniform(0, 2 * math.pi)
        sat_dist = size * random.uniform(0.8, 1.5)
        sat_x = x + sat_dist * math.cos(sat_angle)
        sat_y = y + sat_dist * math.sin(sat_angle)
        sat_size = size * random.uniform(0.2, 0.4)

        # Draw small irregular cluster
        sat_points = []
        for i in range(random.randint(5, 8)):
            angle = (2 * math.pi * i) / 8
            radius = sat_size * random.uniform(0.6, 1.0)
            px = sat_x + radius * math.cos(angle)
            py = sat_y + radius * math.sin(angle)
            sat_points.append((px, py))

        sat_color = moss_color[:3] + (int(moss_color[3] * 0.6),)
        draw.polygon(sat_points, fill=sat_color, outline=None)

    # Add thin tendrils/veins (spreading growth)
    if draping:
        # More tendrils, longer, and biased downward for draping effect
        num_tendrils = random.randint(3, 6)
    else:
        num_tendrils = random.randint(1, 3)

    for _ in range(num_tendrils):
        if draping:
            # Bias tendril angle downward (between 45° and 135° from horizontal, pointing down)
            tendril_angle = random.uniform(math.pi * 0.25, math.pi * 0.75)
            tendril_length = size * random.uniform(2.0, 4.0)  # Much longer for draping
        else:
            tendril_angle = random.uniform(0, 2 * math.pi)
            tendril_length = size * random.uniform(1.2, 2.0)

        # Draw tendril as a series of small circles getting smaller
        tendril_color = moss_color[:3] + (int(moss_color[3] * 0.5),)

        num_segments = random.randint(4, 8) if draping else random.randint(3, 6)
        for seg in range(num_segments):
            t = seg / num_segments
            # Add some curve/wobble to tendril
            curve = math.sin(t * math.pi) * size * 0.3
            seg_x = x + (tendril_length * t) * math.cos(tendril_angle) + curve * math.sin(tendril_angle)
            seg_y = y + (tendril_length * t) * math.sin(tendril_angle) - curve * math.cos(tendril_angle)
            seg_size = size * 0.15 * (1.0 - t * 0.7)  # Get smaller toward end

            # Draw ellipse for tendril segment
            draw.ellipse(
                [seg_x - seg_size, seg_y - seg_size, seg_x + seg_size, seg_y + seg_size],
                fill=tendril_color,
                outline=None
            )

    # Add tiny speckles for organic texture
    num_speckles = random.randint(5, 15)
    speckle_color = moss_color[:3] + (int(moss_color[3] * 0.7),)

    for _ in range(num_speckles):
        speckle_x = x + random.uniform(-size * 1.5, size * 1.5)
        speckle_y = y + random.uniform(-size * 1.5, size * 1.5)
        speckle_size = random.uniform(1, 3)

        draw.ellipse(
            [speckle_x - speckle_size, speckle_y - speckle_size,
             speckle_x + speckle_size, speckle_y + speckle_size],
            fill=speckle_color,
            outline=None
        )


def draw_dense_moss_base(draw: ImageDraw.ImageDraw, width: int, height: int,
                         moss_colors: List[Tuple[int, int, int]]):
    """Draw a dense moss layer covering the entire top of the texture.

    Creates a multi-layered moss coverage at the top with:
    - Irregular wavy bottom edge (15-25% of height)
    - Multiple layers for depth
    - Texture variation with small patches

    Args:
        draw: PIL ImageDraw object
        width: Texture width
        height: Texture height
        moss_colors: List of RGB color tuples to choose from

    Reference:
        Ported from ui/screens/title_screen_3d.py:417-491
    """
    # Define the top coverage area (10-18% of height for AAA subtlety)
    base_coverage = random.uniform(0.10, 0.18)
    base_height = int(height * base_coverage)

    # Create irregular wavy bottom edge using multiple points
    num_edge_points = 20
    edge_points = []

    # Start from top-left, go across top, then create wavy bottom edge
    edge_points.append((0, 0))
    edge_points.append((width, 0))

    # Create wavy bottom edge from right to left
    for i in range(num_edge_points, -1, -1):
        edge_x = (i / num_edge_points) * width
        # Wavy variation in the bottom edge (reduced for less draping)
        wave_offset = random.uniform(0.7, 1.15)
        edge_y = base_height * wave_offset + math.sin(i * 0.5) * base_height * 0.2
        edge_points.append((edge_x, edge_y))

    # Close the polygon
    edge_points.append((0, 0))

    # Draw multiple layers for depth and texture variation
    # Layer 1: Darkest base layer (full coverage)
    dark_moss = random.choice(moss_colors[:3])  # Use darker greens
    dark_moss_rgba = dark_moss + (180,)
    draw.polygon(edge_points, fill=dark_moss_rgba, outline=None)

    # Layer 2: Medium layer with slightly smaller coverage for depth
    medium_points = []
    medium_points.append((0, 0))
    medium_points.append((width, 0))
    for i in range(num_edge_points, -1, -1):
        edge_x = (i / num_edge_points) * width
        wave_offset = random.uniform(0.6, 1.1)
        edge_y = base_height * wave_offset * 0.85 + math.sin(i * 0.7) * base_height * 0.15
        medium_points.append((edge_x, edge_y))
    medium_points.append((0, 0))

    medium_moss = random.choice(moss_colors[2:5] if len(moss_colors) >= 5 else moss_colors)
    medium_moss_rgba = medium_moss + (160,)
    draw.polygon(medium_points, fill=medium_moss_rgba, outline=None)

    # Layer 3: Add texture variation on top with small patches
    for _ in range(30):
        patch_x = random.randint(0, width)
        patch_y = random.randint(0, int(base_height * 1.2))
        patch_size = random.randint(5, 20)

        texture_moss = random.choice(moss_colors)
        texture_moss_rgba = texture_moss + (random.randint(100, 180),)

        # Small irregular blob
        num_points = random.randint(6, 10)
        blob_points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = patch_size * random.uniform(0.6, 1.0)
            px = patch_x + radius * math.cos(angle)
            py = patch_y + radius * math.sin(angle)
            blob_points.append((px, py))

        draw.polygon(blob_points, fill=texture_moss_rgba, outline=None)


def generate_moss_overlay(base_image: Image.Image, density: str = 'heavy') -> Image.Image:
    """Add organic moss growth to existing texture.

    Creates a complete moss overlay with:
    - Dense base layer at top
    - Draping patches extending downward
    - Main organic patches
    - Small clusters along draping paths

    Args:
        base_image: PIL Image to add moss to
        density: Coverage amount - 'light', 'medium', or 'heavy'

    Returns:
        Image with moss overlay applied

    Example:
        >>> brick = generate_brick_pattern()
        >>> mossy = generate_moss_overlay(brick, density='heavy')

    Reference:
        Ported from ui/screens/title_screen_3d.py:493-567
    """
    # Create a transparent overlay for moss
    moss_overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(moss_overlay)

    width = base_image.width
    height = base_image.height

    # Adjust amounts based on density (REDUCED for AAA subtlety)
    if density == 'light':
        num_draping = random.randint(2, 4)
        num_patches = random.randint(1, 3)
        num_small = random.randint(3, 6)
    elif density == 'medium':
        num_draping = random.randint(4, 7)
        num_patches = random.randint(2, 4)
        num_small = random.randint(5, 10)
    else:  # heavy
        num_draping = random.randint(6, 10)
        num_patches = random.randint(3, 6)
        num_small = random.randint(8, 15)

    # 1. Draw dense moss base layer covering entire top
    if density in ('medium', 'heavy'):
        draw_dense_moss_base(draw, width, height, MOSS_COLORS)

    # 2. Draw draping organic moss patches extending from top (ONLY top 15%)
    for _ in range(num_draping):
        # Start ONLY at very top for gravity effect
        moss_x = random.randint(-10, width + 10)
        moss_y = random.randint(0, int(height * 0.15))  # Only top 15%
        moss_size = random.randint(20, 60)
        opacity = random.randint(140, 220)

        moss_rgb = random.choice(MOSS_COLORS)
        moss_color = moss_rgb + (opacity,)

        # Draw patch with emphasis on vertical draping
        draw_moss_patch(draw, moss_x, moss_y, moss_size, moss_color, draping=True)

    # 3. Add main organic moss patches (ONLY top 20%, not 50%)
    for _ in range(num_patches):
        moss_x = random.randint(-10, width + 10)
        moss_y = random.randint(0, int(height * 0.20))  # Only top 20%
        moss_size = random.randint(15, 50)
        opacity = random.randint(120, 200)

        moss_rgb = random.choice(MOSS_COLORS)
        moss_color = moss_rgb + (opacity,)

        draw_moss_patch(draw, moss_x, moss_y, moss_size, moss_color, draping=False)

    # 4. Add smaller moss clusters (ONLY top 25%, not 70%)
    for _ in range(num_small):
        moss_x = random.randint(0, width)
        moss_y = random.randint(0, int(height * 0.25))  # Only top 25%
        moss_size = random.randint(5, 15)
        opacity = random.randint(80, 160)

        moss_rgb = random.choice(MOSS_COLORS)
        moss_color = moss_rgb + (opacity,)

        # Draw simple irregular blob for small clusters
        num_points = random.randint(6, 10)
        cluster_points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = moss_size * random.uniform(0.6, 1.0)
            px = moss_x + radius * math.cos(angle)
            py = moss_y + radius * math.sin(angle)
            cluster_points.append((px, py))

        draw.polygon(cluster_points, fill=moss_color, outline=None)

    # Composite moss overlay onto base image
    result = Image.alpha_composite(base_image.convert('RGBA'), moss_overlay)

    return result


def generate_moss_stone_texture(size: int = 256, moss_density: str = 'heavy',
                                base_darkness: float = 1.0) -> Image.Image:
    """Generate complete moss-covered stone texture.

    Combines brick base with organic moss growth for a complete
    dungeon wall texture.

    Args:
        size: Texture size (power of 2 recommended)
        moss_density: 'light', 'medium', or 'heavy'
        base_darkness: Brightness of underlying bricks (0.0-1.0)

    Returns:
        PIL Image with moss-covered stone

    Example:
        >>> wall_texture = generate_moss_stone_texture(256, moss_density='heavy')
        >>> wall_texture.save('dungeon_wall.png')
    """
    from textures.bricks import generate_brick_pattern
    from textures.weathering import add_weathering

    # Generate brick base
    brick_base = generate_brick_pattern(size=size, darkness=base_darkness)

    # Add weathering
    weathered = add_weathering(brick_base, intensity=1.0)

    # Add moss overlay
    mossy = generate_moss_overlay(weathered, density=moss_density)

    return mossy


def draw_hanging_moss(draw: ImageDraw.ImageDraw, x: float, y_start: float,
                      max_height: float, moss_color: Tuple[int, int, int, int]):
    """Draw hanging moss strand draping downward from ceiling.

    Creates sparse, vine-like moss growth hanging from the ceiling with:
    - Long tendrils extending downward
    - Natural curve/sway
    - Thinning toward the end
    - No satellite clusters (ceiling moss doesn't spread)

    Args:
        draw: PIL ImageDraw object
        x: Horizontal position where moss hangs from
        y_start: Top position (ceiling surface)
        max_height: Maximum length the strand can hang
        moss_color: RGBA color tuple

    Reference:
        Adapted from draw_moss_patch draping tendrils
    """
    # Single long hanging strand
    strand_length = random.uniform(max_height * 0.3, max_height * 0.8)
    num_segments = random.randint(6, 12)

    # Add some horizontal sway
    sway_amount = random.uniform(-0.2, 0.2)

    for seg in range(num_segments):
        t = seg / num_segments

        # Vertical position (downward)
        seg_y = y_start + (strand_length * t)

        # Horizontal sway (sine wave for natural curve)
        sway = math.sin(t * math.pi * 2) * strand_length * sway_amount
        seg_x = x + sway

        # Thickness decreases toward bottom
        seg_size = random.uniform(1.5, 3.5) * (1.0 - t * 0.6)

        # Opacity decreases slightly toward bottom
        segment_color = moss_color[:3] + (int(moss_color[3] * (1.0 - t * 0.3)),)

        # Draw ellipse for strand segment
        draw.ellipse(
            [seg_x - seg_size, seg_y - seg_size,
             seg_x + seg_size, seg_y + seg_size],
            fill=segment_color,
            outline=None
        )

    # Add a few small "drips" at the end
    if random.random() < 0.3:  # 30% chance of drips
        drip_y = y_start + strand_length
        drip_x = x + math.sin(num_segments * 0.5) * strand_length * sway_amount

        for _ in range(random.randint(1, 3)):
            drip_y += random.uniform(2, 5)
            drip_size = random.uniform(0.8, 1.5)
            drip_color = moss_color[:3] + (int(moss_color[3] * 0.5),)

            draw.ellipse(
                [drip_x - drip_size, drip_y - drip_size,
                 drip_x + drip_size, drip_y + drip_size],
                fill=drip_color,
                outline=None
            )


def generate_ceiling_texture(size: int = 256, moisture_level: str = 'medium') -> Image.Image:
    """Generate dungeon ceiling texture with hanging moss and water damage.

    Creates a realistic ceiling with:
    - Dark weathered stone base
    - Sparse hanging moss strands
    - Water stains and mineral deposits
    - Heavy age marks and cracks
    - Overall darker tone (less light reaches ceiling)

    Args:
        size: Texture size (power of 2 recommended)
        moisture_level: Water damage amount - 'low', 'medium', or 'high'

    Returns:
        PIL Image of dungeon ceiling

    Example:
        >>> ceiling = generate_ceiling_texture(256, moisture_level='high')
        >>> ceiling.save('dungeon_ceiling.png')
    """
    from textures.bricks import generate_brick_pattern
    from textures.weathering import add_weathering, add_water_stains
    from textures.generator import darken_image

    # Generate dark brick base (ceilings are darker than walls)
    brick_base = generate_brick_pattern(size=size, darkness=0.6)

    # Add heavy weathering (water damage from moisture seepage)
    intensity = {'low': 1.0, 'medium': 1.5, 'high': 2.0}.get(moisture_level, 1.5)
    weathered = add_weathering(brick_base, intensity=intensity)

    # Add water stains (moisture dripping down)
    water_stained = add_water_stains(weathered, num_stains={'low': 10, 'medium': 20, 'high': 35}.get(moisture_level, 20))

    # Create overlay for hanging moss
    moss_overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(moss_overlay)

    # Determine number of hanging moss strands based on moisture
    num_strands = {'low': random.randint(3, 6),
                   'medium': random.randint(6, 10),
                   'high': random.randint(10, 15)}.get(moisture_level, 8)

    # Draw sparse hanging moss strands from ceiling
    for _ in range(num_strands):
        x = random.randint(0, size)
        y_start = 0  # Start from ceiling (top of texture)
        max_length = size * 0.4  # Hang down up to 40% of texture height

        opacity = random.randint(100, 180)
        moss_rgb = random.choice(MOSS_COLORS)
        moss_color = moss_rgb + (opacity,)

        draw_hanging_moss(draw, x, y_start, max_length, moss_color)

    # Composite moss onto ceiling
    result = Image.alpha_composite(water_stained.convert('RGBA'), moss_overlay)

    # Final darkening (ceilings receive less light)
    result = darken_image(result, factor=0.85)

    return result
