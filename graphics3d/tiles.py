"""
3D tile rendering for dungeon generation

Converts 2D tile grid into 3D meshes using Ursina Engine.
"""

from typing import Tuple
from ursina import Entity, color as ursina_color
import constants as c
from graphics3d.utils import world_to_3d_position, rgb_to_ursina_color
from textures import get_moss_stone_texture, get_brick_texture
from shaders import create_corner_shadow_shader, create_toon_normal_shader


# ===== CACHED PROCEDURAL TEXTURES =====
# Generate these once at module load for performance
# Supports disk caching for faster startup on subsequent launches

import os
from textures import RandomSeed
from textures.organic import generate_moss_stone_texture, generate_moss_overlay, generate_ceiling_texture
from textures.bricks import generate_brick_pattern, generate_normal_map_from_brick_texture
from textures.weathering import add_weathering
from ursina import Texture


def generate_all_textures():
    """
    Generate all biome textures procedurally.

    Returns:
        Tuple of (wall_textures, normal_maps, floor_textures, ceiling_textures)
        and (wall_images, normal_map_images, floor_images, ceiling_images) for caching
    """
    print("Generating procedural biome textures (AAA quality - 1024px, 4 variants per biome)...")

    # Seeds for deterministic variation
    wall_seeds = [12345, 67890, 24680, 13579]
    floor_seeds = [11111, 22222, 33333, 44444]
    ceiling_seeds = [55555, 66666, 77777, 88888]

    # Define biome-specific texture parameters
    biome_wall_configs = {
        c.BIOME_DUNGEON: {'moss_density': 'medium', 'base_darkness': 1.0, 'name': 'Dungeon (mossy stone)'},
        c.BIOME_CATACOMBS: {'moss_density': 'none', 'base_darkness': 0.5, 'name': 'Catacombs (bone-white brick)'},
        c.BIOME_CAVES: {'moss_density': 'light', 'base_darkness': 1.2, 'name': 'Caves (dark earthy stone)'},
        c.BIOME_HELL: {'moss_density': 'none', 'base_darkness': 1.5, 'name': 'Hell (charred black brick)'},
        c.BIOME_ABYSS: {'moss_density': 'none', 'base_darkness': 1.3, 'name': 'Abyss (alien dark stone)'},
    }

    biome_floor_configs = {
        c.BIOME_DUNGEON: {'moss_density': 'light', 'base_darkness': 0.8},
        c.BIOME_CATACOMBS: {'moss_density': 'none', 'base_darkness': 0.4},
        c.BIOME_CAVES: {'moss_density': 'medium', 'base_darkness': 1.0},
        c.BIOME_HELL: {'moss_density': 'none', 'base_darkness': 1.4},
        c.BIOME_ABYSS: {'moss_density': 'none', 'base_darkness': 1.2},
    }

    biome_ceiling_configs = {
        c.BIOME_DUNGEON: {'moisture_level': 'medium'},
        c.BIOME_CATACOMBS: {'moisture_level': 'dry'},
        c.BIOME_CAVES: {'moisture_level': 'heavy'},
        c.BIOME_HELL: {'moisture_level': 'dry'},
        c.BIOME_ABYSS: {'moisture_level': 'dry'},
    }

    # Generate wall textures
    wall_textures = {}
    wall_images = {}  # Store PIL images for caching
    for biome, config in biome_wall_configs.items():
        print(f"  - Generating {config['name']} wall variants...")
        wall_textures[biome] = []
        wall_images[biome] = []
        for i, seed in enumerate(wall_seeds):
            with RandomSeed(seed):
                if config['moss_density'] == 'none':
                    brick_pil = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
                    wall_pil = add_weathering(brick_pil, intensity=1.0)
                else:
                    wall_pil = generate_moss_stone_texture(
                        size=1024,
                        moss_density=config['moss_density'],
                        base_darkness=config['base_darkness']
                    )
                wall_images[biome].append(wall_pil)
                wall_textures[biome].append(Texture(wall_pil))

    print(f"  ✓ {len(wall_textures)} biome wall sets generated ({sum(len(v) for v in wall_textures.values())} total textures)")

    # Generate normal maps
    normal_maps = {}
    normal_map_images = {}
    for biome, config in biome_wall_configs.items():
        normal_maps[biome] = []
        normal_map_images[biome] = []
        for i, seed in enumerate(wall_seeds):
            with RandomSeed(seed):
                brick_pil = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
                normal_map_pil = generate_normal_map_from_brick_texture(brick_pil, strength=8.0)
                normal_map_images[biome].append(normal_map_pil)
                normal_maps[biome].append(Texture(normal_map_pil))

    print(f"  ✓ {len(normal_maps)} biome normal map sets generated ({sum(len(v) for v in normal_maps.values())} total maps)")

    # Generate floor textures
    floor_textures = {}
    floor_images = {}
    for biome, config in biome_floor_configs.items():
        floor_textures[biome] = []
        floor_images[biome] = []
        for i, seed in enumerate(floor_seeds):
            with RandomSeed(seed):
                floor_brick = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
                if config['moss_density'] == 'none':
                    floor_pil = add_weathering(floor_brick, intensity=0.8)
                else:
                    floor_pil = generate_moss_overlay(floor_brick, density=config['moss_density'])
                floor_images[biome].append(floor_pil)
                floor_textures[biome].append(Texture(floor_pil))

    print(f"  ✓ {len(floor_textures)} biome floor sets generated ({sum(len(v) for v in floor_textures.values())} total textures)")

    # Generate ceiling textures
    ceiling_textures = {}
    ceiling_images = {}
    for biome, config in biome_ceiling_configs.items():
        ceiling_textures[biome] = []
        ceiling_images[biome] = []
        for i, seed in enumerate(ceiling_seeds):
            with RandomSeed(seed):
                ceiling_pil = generate_ceiling_texture(size=1024, moisture_level=config['moisture_level'])
                ceiling_images[biome].append(ceiling_pil)
                ceiling_textures[biome].append(Texture(ceiling_pil))

    print(f"  ✓ {len(ceiling_textures)} biome ceiling sets generated ({sum(len(v) for v in ceiling_textures.values())} total textures)")

    return (wall_textures, normal_maps, floor_textures, ceiling_textures,
            wall_images, normal_map_images, floor_images, ceiling_images)


# Load or generate textures based on cache availability
from graphics3d.texture_cache import cache_exists, load_texture_cache, save_texture_cache

regenerate_flag = os.environ.get('REGENERATE_TEXTURES', '0') == '1'

if cache_exists() and not regenerate_flag:
    # Load from cache for fast startup
    WALL_TEXTURES, WALL_NORMAL_MAPS, FLOOR_TEXTURES, CEILING_TEXTURES = load_texture_cache()
else:
    # Generate textures (first launch or forced regeneration)
    if regenerate_flag:
        print("--regenerate-textures flag detected, forcing texture regeneration...")
    (WALL_TEXTURES, WALL_NORMAL_MAPS, FLOOR_TEXTURES, CEILING_TEXTURES,
     wall_images, normal_map_images, floor_images, ceiling_images) = generate_all_textures()

    # Save to cache for next time
    save_texture_cache(wall_images, normal_map_images, floor_images, ceiling_images)

    print("✓ Procedural textures generated and cached")

# ===== CACHED SHADERS =====
# Generate shaders once for all tiles

# Corner shadow shader for floors/ceilings
print("Creating corner shadow shader for ambient occlusion...")
CORNER_SHADOW_SHADER = create_corner_shadow_shader(intensity=c.CORNER_SHADOW_INTENSITY)
print(f"✓ Corner shadow shader created (intensity={c.CORNER_SHADOW_INTENSITY})")

# Toon shader for walls (cartoon depth effect with exaggerated normals)
print("Creating toon shader for cartoon depth effect...")
TOON_NORMAL_SHADER = create_toon_normal_shader(
    num_bands=4,
    rim_intensity=0.4,
    outline_thickness=1.0,
    outline_threshold=0.4
)
print("✓ Toon shader created (4 bands, rim lighting, comic book outlines enabled)")


def create_floor_mesh(x: int, y: int, biome: str, biome_color,
                      has_wall_north: bool = False, has_wall_south: bool = False,
                      has_wall_east: bool = False, has_wall_west: bool = False):
    """
    Create a 3D floor tile mesh with procedural biome-specific texture

    Applies edge-based ambient occlusion shadows only at edges adjacent to walls,
    creating realistic corner darkening where walls meet the floor.

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome tint
        has_wall_north: True if there's a wall at y-1 (north/back edge)
        has_wall_south: True if there's a wall at y+1 (south/front edge)
        has_wall_east: True if there's a wall at x+1 (east/right edge)
        has_wall_west: True if there's a wall at x-1 (west/left edge)

    Returns:
        Ursina Entity representing the floor tile
    """
    pos = world_to_3d_position(x, y, 0)

    # Convert color tuple to ursina color (multiply by 255 for 0-255 integer range)
    if isinstance(biome_color, tuple) and len(biome_color) == 3:
        floor_color = ursina_color.rgb(biome_color[0] * 255, biome_color[1] * 255, biome_color[2] * 255)
    else:
        # Fallback to default floor color
        floor_color = ursina_color.rgb(c.COLOR_FLOOR_RGB[0] * 255, c.COLOR_FLOOR_RGB[1] * 255, c.COLOR_FLOOR_RGB[2] * 255)

    # Apply moderate tint to preserve biome identity while showing texture detail
    # 30% white + 70% biome color (matches wall tinting)
    floor_tint = ursina_color.rgb(
        min(255, 0.3 * 255 + floor_color.r * 255 * 0.7),
        min(255, 0.3 * 255 + floor_color.g * 255 * 0.7),
        min(255, 0.3 * 255 + floor_color.b * 255 * 0.7)
    )

    # Select texture variant based on biome AND position (deterministic hash)
    # This breaks repetition while being deterministic
    biome_textures = FLOOR_TEXTURES.get(biome, FLOOR_TEXTURES[c.BIOME_DUNGEON])
    variant_idx = (x * 7 + y * 13) % len(biome_textures)
    floor_texture = biome_textures[variant_idx]

    # Create floor entity
    floor_entity = Entity(
        model='plane',
        position=pos,
        scale=(1, 1, 1),
        color=floor_tint,  # Biome-specific tint
        texture=floor_texture,  # Select from 4 variants
        collider=None  # No collision for floors
    )

    # Apply corner shadow shader for edge-based ambient occlusion
    floor_entity.shader = CORNER_SHADOW_SHADER

    # Pass wall adjacency info to shader (only darken edges where walls exist)
    floor_entity.set_shader_input('has_wall_north', 1.0 if has_wall_north else 0.0)
    floor_entity.set_shader_input('has_wall_south', 1.0 if has_wall_south else 0.0)
    floor_entity.set_shader_input('has_wall_east', 1.0 if has_wall_east else 0.0)
    floor_entity.set_shader_input('has_wall_west', 1.0 if has_wall_west else 0.0)

    return floor_entity


def create_wall_mesh(x: int, y: int, biome: str, biome_color, height: float = None):
    """
    Create a 3D wall tile mesh with procedural biome-specific texture

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome tint
        height: Wall height in world units (defaults to c.WALL_HEIGHT)

    Returns:
        Ursina Entity representing the wall tile
    """
    if height is None:
        height = c.WALL_HEIGHT

    pos = world_to_3d_position(x, y, height / 2)

    # Convert color tuple to ursina color (multiply by 255 for 0-255 integer range)
    if isinstance(biome_color, tuple) and len(biome_color) == 3:
        wall_color = ursina_color.rgb(biome_color[0] * 255, biome_color[1] * 255, biome_color[2] * 255)
    else:
        # Fallback to default wall color
        wall_color = ursina_color.rgb(c.COLOR_WALL_RGB[0] * 255, c.COLOR_WALL_RGB[1] * 255, c.COLOR_WALL_RGB[2] * 255)

    # Apply moderate tint to preserve biome identity while showing texture detail
    # 30% white + 70% biome color
    wall_tint = ursina_color.rgb(
        min(255, 0.3 * 255 + wall_color.r * 255 * 0.7),
        min(255, 0.3 * 255 + wall_color.g * 255 * 0.7),
        min(255, 0.3 * 255 + wall_color.b * 255 * 0.7)
    )

    # Select texture variant based on biome AND position (deterministic hash)
    # This breaks repetition while being deterministic
    biome_textures = WALL_TEXTURES.get(biome, WALL_TEXTURES[c.BIOME_DUNGEON])
    biome_normal_maps = WALL_NORMAL_MAPS.get(biome, WALL_NORMAL_MAPS[c.BIOME_DUNGEON])
    variant_idx = (x * 7 + y * 13) % len(biome_textures)
    wall_texture = biome_textures[variant_idx]
    normal_map = biome_normal_maps[variant_idx]

    # Create wall entity with procedural moss-covered stone texture
    wall_entity = Entity(
        model='cube',
        position=pos,
        scale=(1, height, 1),
        color=wall_tint,  # Biome-specific tint
        texture=wall_texture,  # Select from 4 variants
        collider='box'  # Walls have collision
    )

    # Apply normal map to second texture stage for bump mapping
    # This works with our toon shader to create cartoon depth effect
    from panda3d.core import TextureStage
    ts = TextureStage('normal')
    ts.setMode(TextureStage.MNormal)
    # Extract underlying Panda3D texture from Ursina wrapper
    panda_normal_map = normal_map._texture if hasattr(normal_map, '_texture') else normal_map
    wall_entity.model.setTexture(ts, panda_normal_map)

    # Apply toon shader for cartoon/cell shading effect
    # This creates stepped lighting with deep black mortar grooves
    wall_entity.shader = TOON_NORMAL_SHADER

    return wall_entity


def create_stairs_mesh(x: int, y: int, biome: str, biome_color):
    """
    Create traditional dungeon stairs descending straight down into darkness

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome

    Returns:
        Ursina Entity representing stairs descending into darkness
    """
    pos = world_to_3d_position(x, y, 0)

    # Convert color tuple to ursina color (multiply by 255 for 0-255 integer range)
    if isinstance(biome_color, tuple) and len(biome_color) == 3:
        stairs_color = ursina_color.rgb(biome_color[0] * 255, biome_color[1] * 255, biome_color[2] * 255)
    else:
        # Fallback to default stairs color
        stairs_color = ursina_color.rgb(c.COLOR_STAIRS_RGB[0] * 255, c.COLOR_STAIRS_RGB[1] * 255, c.COLOR_STAIRS_RGB[2] * 255)

    # Get floor texture for this biome (same as floor tiles)
    biome_textures = FLOOR_TEXTURES.get(biome, FLOOR_TEXTURES[c.BIOME_DUNGEON])
    variant_idx = (x * 7 + y * 13) % len(biome_textures)
    floor_texture = biome_textures[variant_idx]

    # Apply moderate tint to preserve biome identity (same as floor tinting)
    floor_tint = ursina_color.rgb(
        min(255, 0.3 * 255 + stairs_color.r * 255 * 0.7),
        min(255, 0.3 * 255 + stairs_color.g * 255 * 0.7),
        min(255, 0.3 * 255 + stairs_color.b * 255 * 0.7)
    )

    # Parent entity to hold all stair components
    stair_group = Entity(position=pos)

    # Create 6 descending steps going straight down (north direction)
    num_steps = 6
    step_depth = 0.15  # How far forward each step goes
    step_height = 0.15  # How much each step descends
    step_width = 0.7   # Width of the step tread
    support_size = 0.12  # Size of support blocks on ends

    for i in range(num_steps):
        # Calculate position (steps go forward/north and down)
        step_z = -i * step_depth  # Move forward (negative Z)
        step_y = -i * step_height  # Move down (negative Y)

        # Fade to darkness as steps descend (0.0 = bright at top, 1.0 = dark at bottom)
        darkness_factor = i / (num_steps - 1)

        # Calculate step color tint (darkens progressively)
        # Start with biome tint and darken it
        step_color = ursina_color.rgb(
            max(10, floor_tint.r * 255 * (1.0 - darkness_factor * 0.85)),
            max(10, floor_tint.g * 255 * (1.0 - darkness_factor * 0.85)),
            max(10, floor_tint.b * 255 * (1.0 - darkness_factor * 0.85))
        )

        # Main step tread (horizontal walking surface) with floor texture
        step_tread = Entity(
            parent=stair_group,
            model='cube',
            position=(0, step_y, step_z),
            scale=(step_width, 0.05, step_depth),  # Thin horizontal slab
            color=step_color,
            texture=floor_texture,  # Apply floor texture
            collider=None
        )
        step_tread.shader = CORNER_SHADOW_SHADER
        # Set shader inputs (no walls for stair geometry, so no edge darkening)
        step_tread.set_shader_input('has_wall_north', 0.0)
        step_tread.set_shader_input('has_wall_south', 0.0)
        step_tread.set_shader_input('has_wall_east', 0.0)
        step_tread.set_shader_input('has_wall_west', 0.0)

        # Left support block (end of step) with floor texture
        left_support = Entity(
            parent=stair_group,
            model='cube',
            position=(-step_width/2 + support_size/2, step_y - support_size/2, step_z),
            scale=(support_size, support_size, step_depth),
            color=step_color,
            texture=floor_texture,  # Apply floor texture
            collider=None
        )
        left_support.shader = CORNER_SHADOW_SHADER
        # Set shader inputs (no walls for stair geometry, so no edge darkening)
        left_support.set_shader_input('has_wall_north', 0.0)
        left_support.set_shader_input('has_wall_south', 0.0)
        left_support.set_shader_input('has_wall_east', 0.0)
        left_support.set_shader_input('has_wall_west', 0.0)

        # Right support block (end of step) with floor texture
        right_support = Entity(
            parent=stair_group,
            model='cube',
            position=(step_width/2 - support_size/2, step_y - support_size/2, step_z),
            scale=(support_size, support_size, step_depth),
            color=step_color,
            texture=floor_texture,  # Apply floor texture
            collider=None
        )
        right_support.shader = CORNER_SHADOW_SHADER
        # Set shader inputs (no walls for stair geometry, so no edge darkening)
        right_support.set_shader_input('has_wall_north', 0.0)
        right_support.set_shader_input('has_wall_south', 0.0)
        right_support.set_shader_input('has_wall_east', 0.0)
        right_support.set_shader_input('has_wall_west', 0.0)

    return stair_group


def create_ceiling_mesh(x: int, y: int, biome: str, biome_color,
                        has_wall_north: bool = False, has_wall_south: bool = False,
                        has_wall_east: bool = False, has_wall_west: bool = False):
    """
    Create a 3D ceiling tile mesh with procedural biome-specific texture

    Applies edge-based ambient occlusion shadows only at edges adjacent to walls,
    creating realistic corner darkening where walls meet the ceiling.

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome tint
        has_wall_north: True if there's a wall at y-1 (north/back edge)
        has_wall_south: True if there's a wall at y+1 (south/front edge)
        has_wall_east: True if there's a wall at x+1 (east/right edge)
        has_wall_west: True if there's a wall at x-1 (west/left edge)

    Returns:
        Ursina Entity representing the ceiling tile
    """
    # Position ceiling at top of walls
    pos = world_to_3d_position(x, y, c.WALL_HEIGHT)

    # Convert color tuple to ursina color (multiply by 255 for 0-255 integer range)
    if isinstance(biome_color, tuple) and len(biome_color) == 3:
        ceiling_color = ursina_color.rgb(biome_color[0] * 255, biome_color[1] * 255, biome_color[2] * 255)
    else:
        # Fallback to default wall color (ceiling uses wall biome color)
        ceiling_color = ursina_color.rgb(c.COLOR_WALL_RGB[0] * 255, c.COLOR_WALL_RGB[1] * 255, c.COLOR_WALL_RGB[2] * 255)

    # Apply moderate tint to preserve biome identity while showing texture detail
    # 30% white + 70% biome color (matches wall/floor tinting)
    ceiling_tint = ursina_color.rgb(
        min(255, 0.3 * 255 + ceiling_color.r * 255 * 0.7),
        min(255, 0.3 * 255 + ceiling_color.g * 255 * 0.7),
        min(255, 0.3 * 255 + ceiling_color.b * 255 * 0.7)
    )

    # Select texture variant based on biome AND position (deterministic hash)
    # This breaks repetition while being deterministic
    biome_textures = CEILING_TEXTURES.get(biome, CEILING_TEXTURES[c.BIOME_DUNGEON])
    variant_idx = (x * 7 + y * 13) % len(biome_textures)
    ceiling_texture = biome_textures[variant_idx]

    # Create ceiling plane facing downward
    ceiling_entity = Entity(
        model='plane',
        position=pos,
        scale=(1, 1, 1),
        color=ceiling_tint,  # Biome-specific tint
        texture=ceiling_texture,  # Select from 4 variants
        rotation_x=180,  # Flip to face downward
        collider=None  # No collision for ceilings
    )

    # Apply corner shadow shader for edge-based ambient occlusion
    ceiling_entity.shader = CORNER_SHADOW_SHADER

    # Pass wall adjacency info to shader (only darken edges where walls exist)
    ceiling_entity.set_shader_input('has_wall_north', 1.0 if has_wall_north else 0.0)
    ceiling_entity.set_shader_input('has_wall_south', 1.0 if has_wall_south else 0.0)
    ceiling_entity.set_shader_input('has_wall_east', 1.0 if has_wall_east else 0.0)
    ceiling_entity.set_shader_input('has_wall_west', 1.0 if has_wall_west else 0.0)

    return ceiling_entity
