"""
Gold Coin 3D model - Collectible currency/score item

Procedurally generated 3D model using Ursina primitives.
Gold coins spin rapidly to attract attention.

Features:
- Proper cylinder geometry for realistic circular shape
- 3D embossed emblems (dot, diamond, star, crown, sunburst)
- Toon shader for cel-shaded appearance
- Physically raised geometry on both coin faces
"""

from ursina import Entity, Vec3, Mesh
import constants as c
from graphics3d.utils import rgb_to_ursina_color
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


def generate_star_emblem_mesh(points=5, outer_radius=0.04, inner_radius=0.02, extrude_depth=0.01):
    """
    Generate a 3D extruded star emblem mesh with variable point count.

    Args:
        points: Number of star points (5=star, 8=crown, 16=sunburst)
        outer_radius: Distance from center to star points
        inner_radius: Distance from center to valleys between points
        extrude_depth: How much the star extrudes from the surface

    Returns:
        Mesh: 3D star emblem
    """
    vertices = []
    triangles = []
    normals = []

    # Center vertex at base (on coin surface)
    base_center_idx = len(vertices)
    vertices.append(Vec3(0, 0, 0))
    normals.append(Vec3(0, 0, -1))  # Point down into coin

    # Center vertex at top (extruded peak)
    top_center_idx = len(vertices)
    vertices.append(Vec3(0, extrude_depth, 0))
    normals.append(Vec3(0, 1, 0))  # Point up

    # Generate star points (alternating outer/inner radii)
    base_vertices = []
    for i in range(points * 2):
        angle = (i / (points * 2)) * 2 * math.pi - math.pi / 2
        radius = outer_radius if i % 2 == 0 else inner_radius

        x = radius * math.cos(angle)
        z = radius * math.sin(angle)

        # Base vertex (on coin surface)
        base_idx = len(vertices)
        vertices.append(Vec3(x, 0, z))
        base_vertices.append(base_idx)

        # Calculate outward normal for side faces
        normal = Vec3(x, 0, z).normalized()
        normals.append(normal)

        # Top vertex (extruded)
        top_idx = len(vertices)
        vertices.append(Vec3(x, extrude_depth, z))
        normals.append(normal)

        # Create side wall triangles (quad = 2 triangles)
        if i > 0:
            prev_base = base_vertices[i - 1]
            prev_top = base_vertices[i - 1] + 1
            curr_base = base_idx
            curr_top = top_idx

            # Triangle 1: base -> next_base -> top
            triangles.append((prev_base, curr_base, prev_top))
            # Triangle 2: next_base -> next_top -> top
            triangles.append((curr_base, curr_top, prev_top))

    # Close the loop (connect last to first)
    first_base = base_vertices[0]
    first_top = first_base + 1
    last_base = base_vertices[-1]
    last_top = last_base + 1
    triangles.append((last_base, first_base, last_top))
    triangles.append((first_base, first_top, last_top))

    # Create bottom face (star shape on coin surface)
    for i in range(len(base_vertices)):
        curr = base_vertices[i]
        next_v = base_vertices[(i + 1) % len(base_vertices)]
        triangles.append((base_center_idx, next_v, curr))

    # Create top face (star shape at extruded peak)
    top_vertices = [v + 1 for v in base_vertices]  # Top vertices are +1 from base
    for i in range(len(top_vertices)):
        curr = top_vertices[i]
        next_v = top_vertices[(i + 1) % len(top_vertices)]
        triangles.append((top_center_idx, curr, next_v))

    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def generate_diamond_emblem_mesh(size=0.04, height=0.015):
    """
    Generate a 4-sided pyramid (diamond) emblem.

    Args:
        size: Base size of the diamond
        height: Height of the pyramid peak

    Returns:
        Mesh: 3D diamond emblem
    """
    vertices = []
    triangles = []
    normals = []

    # Base vertices (4 corners of square)
    base_vertices = [
        Vec3(-size, 0, 0),      # Left
        Vec3(0, 0, -size),      # Front
        Vec3(size, 0, 0),       # Right
        Vec3(0, 0, size),       # Back
    ]

    # Center of base
    center_base = Vec3(0, 0, 0)

    # Peak of pyramid
    peak = Vec3(0, height, 0)

    # Add base center
    center_idx = 0
    vertices.append(center_base)
    normals.append(Vec3(0, -1, 0))

    # Add peak
    peak_idx = 1
    vertices.append(peak)
    normals.append(Vec3(0, 1, 0))

    # Add base vertices and create triangular faces
    base_indices = []
    for i, v in enumerate(base_vertices):
        idx = len(vertices)
        base_indices.append(idx)
        vertices.append(v)

        # Normal points outward and up
        normal = Vec3(v.x, height/2, v.z).normalized()
        normals.append(normal)

    # Create pyramid faces (4 triangles from peak to base edges)
    for i in range(4):
        curr = base_indices[i]
        next_v = base_indices[(i + 1) % 4]
        triangles.append((peak_idx, curr, next_v))

    # Create base face (4 triangles from center to base edges)
    for i in range(4):
        curr = base_indices[i]
        next_v = base_indices[(i + 1) % 4]
        triangles.append((center_idx, next_v, curr))

    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def generate_dot_emblem_mesh(radius=0.03, height=0.01, segments=12):
    """
    Generate a simple raised hemisphere (dot) emblem.

    Args:
        radius: Radius of the hemisphere
        height: Height of the hemisphere
        segments: Number of segments for smoothness

    Returns:
        Mesh: 3D hemisphere emblem
    """
    vertices = []
    triangles = []
    normals = []

    # Center point at base
    center_idx = 0
    vertices.append(Vec3(0, 0, 0))
    normals.append(Vec3(0, -1, 0))

    # Peak point
    peak_idx = 1
    vertices.append(Vec3(0, height, 0))
    normals.append(Vec3(0, 1, 0))

    # Generate circular base ring
    base_indices = []
    for i in range(segments):
        angle = (i / segments) * 2 * math.pi
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)

        idx = len(vertices)
        base_indices.append(idx)
        vertices.append(Vec3(x, 0, z))

        # Normal points outward
        normal = Vec3(x, height, z).normalized()
        normals.append(normal)

    # Create side faces (triangles from peak to base ring)
    for i in range(segments):
        curr = base_indices[i]
        next_v = base_indices[(i + 1) % segments]
        triangles.append((peak_idx, curr, next_v))

    # Create base face (triangles from center to base ring)
    for i in range(segments):
        curr = base_indices[i]
        next_v = base_indices[(i + 1) % segments]
        triangles.append((center_idx, next_v, curr))

    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def generate_coin_mesh(radius=0.2, height=0.08, segments=32):
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
        height: Coin thickness/height (default 0.08 for good visibility)
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
    # IMPORTANT: Counter-clockwise winding from outside view for correct normals
    for i in range(segments):
        bottom_current = i * 2
        top_current = i * 2 + 1
        bottom_next = (i + 1) * 2
        top_next = (i + 1) * 2 + 1

        # Triangle 1 (lower-left triangle of quad, counter-clockwise from outside)
        triangles.append((bottom_current, bottom_next, top_current))

        # Triangle 2 (upper-right triangle of quad, counter-clockwise from outside)
        triangles.append((bottom_next, top_next, top_current))

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


def create_gold_coin_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D gold coin model with rarity-based appearance

    Uses proper cylinder geometry with 3D embossed emblems
    and toon shading for a high-quality cel-shaded coin.

    Emblems by rarity:
    - Common: Raised dot (hemisphere)
    - Uncommon: Diamond pyramid (4-sided)
    - Rare: 5-pointed star
    - Epic: 8-pointed crown/gear
    - Legendary: 16-pointed sunburst

    Args:
        position: 3D world position
        rarity: Item rarity (affects gold color, emblem, and glow)

    Returns:
        Entity: Gold coin 3D model with embossed emblems on both faces
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

    # Generate procedural coin meshes (cylinder geometry)
    # Using thicker coins for better visibility (height 0.08 vs radius 0.2 = 2.5:1 ratio)
    coin_mesh = generate_coin_mesh(radius=0.2, height=0.08, segments=32)
    edge_mesh = generate_coin_mesh(radius=0.21, height=0.09, segments=32)

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
        shader=coin_shader
    )

    # Create 3D embossed emblems based on rarity (2x larger for visibility)
    emblem_color = rgb_to_ursina_color(*tuple(min(255, c + 30) for c in coin_color_rgb))  # Slightly brighter
    emblem_shader = get_shader_for_scale(0.08, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

    if rarity == c.RARITY_COMMON:
        # Simple raised dot (2x size)
        emblem_mesh = generate_dot_emblem_mesh(radius=0.06, height=0.02, segments=12)
    elif rarity == c.RARITY_UNCOMMON:
        # Diamond pyramid (2x size)
        emblem_mesh = generate_diamond_emblem_mesh(size=0.08, height=0.03)
    elif rarity == c.RARITY_RARE:
        # 5-pointed star (2x size)
        emblem_mesh = generate_star_emblem_mesh(points=5, outer_radius=0.09, inner_radius=0.04, extrude_depth=0.024)
    elif rarity == c.RARITY_EPIC:
        # 8-pointed crown/gear (2x size)
        emblem_mesh = generate_star_emblem_mesh(points=8, outer_radius=0.10, inner_radius=0.05, extrude_depth=0.03)
    else:  # LEGENDARY
        # 16-pointed sunburst (2x size)
        emblem_mesh = generate_star_emblem_mesh(points=16, outer_radius=0.11, inner_radius=0.06, extrude_depth=0.036)

    # Add emblem to FRONT face (coin rotated 90° on X, so Z+ is front)
    # Emblem positioned at front of coin face
    front_emblem = Entity(
        model=emblem_mesh,
        color=emblem_color,
        parent=coin,
        position=(0, 0, 0.045),  # Slightly in front of coin face
        rotation=(90, 0, 0),  # Match coin rotation
        shader=emblem_shader
    )

    # Add emblem to BACK face
    # Rotate 180° to flip emblem to face outward on back side
    back_emblem = Entity(
        model=emblem_mesh,
        color=emblem_color,
        parent=coin,
        position=(0, 0, -0.045),  # Slightly behind coin face
        rotation=(90, 180, 0),  # Match coin rotation + flip 180°
        shader=emblem_shader
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
