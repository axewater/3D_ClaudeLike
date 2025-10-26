"""
Gold Coin 3D model - Collectible currency/score item

Procedurally generated 3D model using Ursina primitives.
Gold coins spin rapidly to attract attention.

Features:
- Proper cylinder geometry for realistic circular shape
- Procedurally generated coin texture with embossed designs
- Toon shader for cel-shaded appearance
"""

from ursina import Entity, Vec3, Texture, Mesh
from PIL import Image, ImageDraw, ImageFont
import constants as c
from graphics3d.utils import rgb_to_ursina_color
import random
import math

# Import toon shader system
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add dna_editor to path
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.insert(0, dna_editor_path)

from dna_editor.shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale


def generate_coin_mesh(radius=0.2, height=0.04, segments=32):
    """
    Generate a procedural cylinder mesh for coin geometry using parametric equations.

    Creates a cylinder with:
    - Smooth circular side wall
    - Top circular cap (flat face for texture)
    - Bottom circular cap (flat face for texture)
    - Proper normals for lighting
    - Radial UV coordinates for circular texture mapping

    Args:
        radius: Coin radius (default 0.2)
        height: Coin thickness/height (default 0.04 - thin like a real coin)
        segments: Number of segments around circumference (default 32 for smoothness)

    Returns:
        Mesh: Ursina Mesh object with cylinder geometry
    """
    vertices = []
    triangles = []
    normals = []
    uvs = []

    half_height = height / 2.0

    # Generate vertices around circumference (for side wall and caps)
    for i in range(segments + 1):
        theta = (i / segments) * 2 * math.pi
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        x = radius * cos_theta
        z = radius * sin_theta

        # Bottom vertices (for side wall)
        vertices.append(Vec3(x, -half_height, z))
        normals.append(Vec3(cos_theta, 0, sin_theta).normalized())  # Outward normal
        uvs.append((i / segments, 0))  # UV wraps around

        # Top vertices (for side wall)
        vertices.append(Vec3(x, half_height, z))
        normals.append(Vec3(cos_theta, 0, sin_theta).normalized())  # Outward normal
        uvs.append((i / segments, 1))

    # Generate triangles for side wall (two triangles per segment)
    for i in range(segments):
        bottom_current = i * 2
        top_current = i * 2 + 1
        bottom_next = (i + 1) * 2
        top_next = (i + 1) * 2 + 1

        # Triangle 1 (bottom-left to top-right)
        triangles.append((bottom_current, top_current, bottom_next))

        # Triangle 2 (top-left to top-right to bottom-right)
        triangles.append((top_current, top_next, bottom_next))

    # === TOP CAP (circular disc at y = half_height) ===
    top_cap_start = len(vertices)

    # Center vertex for top cap
    vertices.append(Vec3(0, half_height, 0))
    normals.append(Vec3(0, 1, 0))  # Normal points up
    uvs.append((0.5, 0.5))  # Center of texture

    # Edge vertices for top cap (with radial UV coordinates)
    for i in range(segments + 1):
        theta = (i / segments) * 2 * math.pi
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        x = radius * cos_theta
        z = radius * sin_theta

        vertices.append(Vec3(x, half_height, z))
        normals.append(Vec3(0, 1, 0))  # Normal points up

        # Radial UV coordinates (center = 0.5, 0.5)
        u = 0.5 + 0.5 * cos_theta
        v = 0.5 + 0.5 * sin_theta
        uvs.append((u, v))

    # Generate triangles for top cap (fan from center)
    for i in range(segments):
        center_idx = top_cap_start
        current_edge = top_cap_start + 1 + i
        next_edge = top_cap_start + 1 + (i + 1)

        triangles.append((center_idx, current_edge, next_edge))

    # === BOTTOM CAP (circular disc at y = -half_height) ===
    bottom_cap_start = len(vertices)

    # Center vertex for bottom cap
    vertices.append(Vec3(0, -half_height, 0))
    normals.append(Vec3(0, -1, 0))  # Normal points down
    uvs.append((0.5, 0.5))  # Center of texture

    # Edge vertices for bottom cap (with radial UV coordinates)
    for i in range(segments + 1):
        theta = (i / segments) * 2 * math.pi
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        x = radius * cos_theta
        z = radius * sin_theta

        vertices.append(Vec3(x, -half_height, z))
        normals.append(Vec3(0, -1, 0))  # Normal points down

        # Radial UV coordinates (center = 0.5, 0.5)
        u = 0.5 + 0.5 * cos_theta
        v = 0.5 + 0.5 * sin_theta
        uvs.append((u, v))

    # Generate triangles for bottom cap (fan from center, reversed winding)
    for i in range(segments):
        center_idx = bottom_cap_start
        current_edge = bottom_cap_start + 1 + i
        next_edge = bottom_cap_start + 1 + (i + 1)

        # Reverse winding order for bottom face (normals point down)
        triangles.append((center_idx, next_edge, current_edge))

    return Mesh(vertices=vertices, triangles=triangles, normals=normals, uvs=uvs)


def generate_coin_texture(coin_color_rgb: tuple, rarity: str, size: int = 256) -> Image.Image:
    """
    Generate procedural texture for coin faces with embossed designs.

    Creates a circular coin texture with:
    - Outer rim/border
    - Central emblem/symbol (varies by rarity)
    - Subtle radial lines for metallic look
    - Color variation and detail

    Args:
        coin_color_rgb: Base color as RGB tuple (0-255 scale)
        rarity: Item rarity (affects symbol complexity)
        size: Texture size in pixels (default 256)

    Returns:
        PIL Image with RGBA coin texture
    """
    # Create circular coin texture
    image = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    center = size // 2
    radius = size // 2 - 2

    # Draw main coin circle (solid fill)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=coin_color_rgb + (255,),
        outline=None
    )

    # Outer rim - darker border
    rim_color = tuple(max(0, c - 30) for c in coin_color_rgb)
    rim_width = max(3, size // 32)
    for i in range(rim_width):
        r = radius - i
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=None,
            outline=rim_color + (255,),
            width=1
        )

    # Inner rim - brighter highlight
    highlight_color = tuple(min(255, c + 40) for c in coin_color_rgb)
    inner_rim_radius = radius - rim_width * 2
    for i in range(2):
        r = inner_rim_radius - i
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=None,
            outline=highlight_color + (255,),
            width=1
        )

    # Draw radial lines for metallic texture (subtle)
    num_lines = 24 + (len(rarity) * 4)  # More lines for rarer coins
    for i in range(num_lines):
        angle = (i / num_lines) * 2 * math.pi
        start_r = inner_rim_radius - 10
        end_r = radius - rim_width - 5

        x1 = center + int(math.cos(angle) * start_r)
        y1 = center + int(math.sin(angle) * start_r)
        x2 = center + int(math.cos(angle) * end_r)
        y2 = center + int(math.sin(angle) * end_r)

        line_color = tuple(min(255, c + 10) for c in coin_color_rgb)
        draw.line([x1, y1, x2, y2], fill=line_color + (128,), width=1)

    # Central emblem varies by rarity
    emblem_radius = size // 6

    if rarity == c.RARITY_COMMON:
        # Simple dot
        draw.ellipse(
            [center - emblem_radius, center - emblem_radius,
             center + emblem_radius, center + emblem_radius],
            fill=highlight_color + (255,)
        )
    elif rarity == c.RARITY_UNCOMMON:
        # Diamond shape
        points = [
            (center, center - emblem_radius),
            (center + emblem_radius, center),
            (center, center + emblem_radius),
            (center - emblem_radius, center)
        ]
        draw.polygon(points, fill=highlight_color + (255,))
    elif rarity == c.RARITY_RARE:
        # Star (5 points)
        points = []
        for i in range(10):
            angle = (i / 10) * 2 * math.pi - math.pi / 2
            r = emblem_radius if i % 2 == 0 else emblem_radius // 2
            x = center + int(math.cos(angle) * r)
            y = center + int(math.sin(angle) * r)
            points.append((x, y))
        draw.polygon(points, fill=highlight_color + (255,))
    elif rarity == c.RARITY_EPIC:
        # Crown/gear shape (8 points)
        points = []
        for i in range(16):
            angle = (i / 16) * 2 * math.pi
            r = emblem_radius if i % 2 == 0 else emblem_radius * 0.7
            x = center + int(math.cos(angle) * r)
            y = center + int(math.sin(angle) * r)
            points.append((x, y))
        draw.polygon(points, fill=highlight_color + (255,))
    else:  # LEGENDARY
        # Complex sun/star burst (16 points)
        points = []
        for i in range(32):
            angle = (i / 32) * 2 * math.pi
            r = emblem_radius if i % 2 == 0 else emblem_radius * 0.6
            x = center + int(math.cos(angle) * r)
            y = center + int(math.sin(angle) * r)
            points.append((x, y))
        draw.polygon(points, fill=highlight_color + (255,))

        # Add inner circle for legendary
        inner_circle_r = emblem_radius // 3
        draw.ellipse(
            [center - inner_circle_r, center - inner_circle_r,
             center + inner_circle_r, center + inner_circle_r],
            fill=coin_color_rgb + (255,)
        )

    return image


def create_gold_coin_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D gold coin model with rarity-based appearance

    Uses proper cylinder geometry with procedurally generated textures
    and toon shading for a high-quality cel-shaded coin.

    Args:
        position: 3D world position
        rarity: Item rarity (affects gold color and value)

    Returns:
        Entity: Gold coin 3D model
    """
    # Create toon shader instances
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Container entity (invisible parent)
    coin = Entity(position=position)

    # Rarity-based colors (RGB 0-255 for texture generation)
    if rarity == c.RARITY_COMMON:
        coin_color_rgb = (255, 215, 0)  # Standard gold
        coin_color = rgb_to_ursina_color(*coin_color_rgb)
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        coin_color_rgb = (255, 225, 50)  # Brighter gold
        coin_color = rgb_to_ursina_color(*coin_color_rgb)
        has_glow = False
    elif rarity == c.RARITY_RARE:
        coin_color_rgb = (255, 235, 100)  # Very bright gold
        coin_color = rgb_to_ursina_color(*coin_color_rgb)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)
    elif rarity == c.RARITY_EPIC:
        coin_color_rgb = (255, 200, 255)  # Golden magenta
        coin_color = rgb_to_ursina_color(*coin_color_rgb)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 150, 255)
    else:  # LEGENDARY
        coin_color_rgb = (255, 255, 255)  # Brilliant white gold
        coin_color = rgb_to_ursina_color(*coin_color_rgb)
        has_glow = True
        glow_color = rgb_to_ursina_color(255, 215, 0)

    # Glow for rare+ coins (unlit, no shader)
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

    # Generate procedural coin texture
    coin_texture_pil = generate_coin_texture(coin_color_rgb, rarity, size=256)
    coin_texture = Texture(coin_texture_pil)

    # Generate procedural coin meshes (cylinder geometry)
    coin_mesh = generate_coin_mesh(radius=0.2, height=0.04, segments=32)
    edge_mesh = generate_coin_mesh(radius=0.21, height=0.045, segments=32)

    # Main coin body - procedural cylinder with flat circular faces
    # Cylinder is oriented vertically by default (Y-axis)
    # We rotate it 90° around X to make it stand like a coin
    coin_shader = get_shader_for_scale(0.2, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

    coin_disc = Entity(
        model=coin_mesh,
        color=coin_color,
        parent=coin,
        position=(0, 0, 0),
        rotation=(90, 0, 0),  # Rotate to stand upright
        texture=coin_texture,
        shader=coin_shader
    )

    # Edge ring - slightly larger cylinder for raised rim effect
    edge_color = rgb_to_ursina_color(*tuple(max(0, c - 20) for c in coin_color_rgb))
    edge_shader = get_shader_for_scale(0.21, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

    edge_ring = Entity(
        model=edge_mesh,
        color=edge_color,
        parent=coin,
        position=(0, 0, 0),
        rotation=(90, 0, 0),
        shader=edge_shader
    )

    # Store animation state
    coin.float_time = 0.0
    coin.rotation_speed = 120.0  # Fast spin to make it obvious it's rotating

    return coin
