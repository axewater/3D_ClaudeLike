"""
Ring 3D model - Accessory equipment with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, Mesh, color as ursina_color
import math
import constants as c
from graphics3d.utils import rgb_to_ursina_color

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


def generate_torus_mesh(major_radius=0.12, minor_radius=0.035,
                        segments_major=18, segments_minor=12):
    """
    Generate a procedural torus (donut) mesh using parametric equations

    Args:
        major_radius: Distance from center to tube center (R)
        minor_radius: Tube thickness/radius (r)
        segments_major: Number of segments around major circle
        segments_minor: Number of segments around minor (tube) circle

    Returns:
        Mesh: Ursina Mesh object with torus geometry
    """
    vertices = []
    triangles = []
    normals = []

    R = major_radius
    r = minor_radius

    # Generate vertices using parametric torus equations
    for i in range(segments_major + 1):
        u = (i / segments_major) * 2 * math.pi

        for j in range(segments_minor + 1):
            v = (j / segments_minor) * 2 * math.pi

            # Parametric torus equations
            x = (R + r * math.cos(v)) * math.cos(u)
            y = r * math.sin(v)
            z = (R + r * math.cos(v)) * math.sin(u)

            vertices.append(Vec3(x, y, z))

            # Normal vector (perpendicular to torus surface)
            nx = math.cos(v) * math.cos(u)
            ny = math.sin(v)
            nz = math.cos(v) * math.sin(u)
            normals.append(Vec3(nx, ny, nz).normalized())

    # Generate triangle indices (two triangles per quad)
    for i in range(segments_major):
        for j in range(segments_minor):
            # Current quad corners
            current = i * (segments_minor + 1) + j
            next_row = (i + 1) * (segments_minor + 1) + j

            # Triangle 1
            triangles.append((current, next_row, current + 1))

            # Triangle 2
            triangles.append((current + 1, next_row, next_row + 1))

    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def create_ring_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D ring model with rarity-based appearance

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Ring 3D model
    """
    # Create toon shader instances (shared across all ring components)
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Container entity (invisible parent)
    # Rotate 270 degrees on X axis to stand ring upright with gem on top
    # (90 would make it upright but gem below, so flip 180 more = 270 total)
    ring = Entity(position=position, rotation_x=270)

    # Rarity-based colors and gem types
    if rarity == c.RARITY_COMMON:
        band_color = rgb_to_ursina_color(140, 140, 140)  # Iron/silver
        gem_color = None  # No gem
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        band_color = rgb_to_ursina_color(180, 140, 80)  # Brass/bronze
        gem_color = rgb_to_ursina_color(100, 200, 100)  # Green gem
        has_glow = False
    elif rarity == c.RARITY_RARE:
        band_color = rgb_to_ursina_color(192, 192, 192)  # Silver
        gem_color = rgb_to_ursina_color(100, 150, 255)  # Blue gem
        has_glow = False
    elif rarity == c.RARITY_EPIC:
        band_color = rgb_to_ursina_color(220, 180, 100)  # Gold
        gem_color = rgb_to_ursina_color(200, 50, 255)  # Purple gem
        has_glow = True
        glow_color = rgb_to_ursina_color(200, 100, 255)
    else:  # LEGENDARY
        band_color = rgb_to_ursina_color(255, 215, 0)  # Bright gold
        gem_color = rgb_to_ursina_color(100, 255, 255)  # Cyan gem
        has_glow = True
        glow_color = rgb_to_ursina_color(100, 200, 255)

    # Glow for epic/legendary
    if has_glow:
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=0.25,
            parent=ring,
            position=(0, 0, 0),
            alpha=0.4,
            unlit=True
        )

    # Ring band - smooth torus mesh (donut shape)
    torus_mesh = generate_torus_mesh(
        major_radius=0.12,  # Ring outer radius
        minor_radius=0.035,  # Tube thickness
        segments_major=18,  # Segments around major circle (smoothness)
        segments_minor=12   # Segments around tube (roundness)
    )

    # Create ring band entity with torus mesh
    # Use minor_radius (0.035) for LOD selection (thickness of tube)
    band_shader = get_shader_for_scale(0.035, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    band = Entity(
        model=torus_mesh,
        color=band_color,
        parent=ring,
        position=(0, 0, 0),
        shader=band_shader
    )

    # Gem on top (if has gem)
    if gem_color:
        # Position gem at top of upright ring in LOCAL coordinates
        # After rotation_x=90: local Z becomes global Y (up direction)
        # Ring band outer edge: R + r = 0.155
        # Setting cube (Z-size 0.04): center at Z = 0.155 + 0.02 = 0.175
        # Gem sphere (radius 0.04): center at Z = 0.175 + 0.02 + 0.04 = 0.235
        gem = Entity(
            model='sphere',
            color=gem_color,
            scale=0.08,
            parent=ring,
            position=(0, 0, 0.235),  # Local Z → Global Y (top of ring)
            unlit=True  # Emissive gem
        )

        # Gem setting/prongs - connects gem to ring band
        setting_shader = get_shader_for_scale(0.03, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
        gem_setting = Entity(
            model='cube',
            color=band_color,
            scale=(0.04, 0.03, 0.04),
            parent=ring,
            position=(0, 0, 0.175),  # Local Z → Global Y
            shader=setting_shader
        )

    # Store animation state
    ring.float_time = 0.0
    ring.rotation_speed = 60.0  # Faster rotation to show ring shape

    return ring
