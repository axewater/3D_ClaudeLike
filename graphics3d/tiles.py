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
print("Generating procedural biome textures (AAA quality - 1024px, 4 variants per biome)...")

# Wall: Generate 4 variants for EACH biome with distinct visual styles
from textures import RandomSeed
from textures.organic import generate_moss_stone_texture, generate_moss_overlay
from textures.bricks import generate_brick_pattern
from ursina import Texture

# Wall textures organized by biome
WALL_TEXTURES = {}
wall_seeds = [12345, 67890, 24680, 13579]

# Define biome-specific texture parameters
biome_wall_configs = {
    c.BIOME_DUNGEON: {'moss_density': 'medium', 'base_darkness': 1.0, 'name': 'Dungeon (mossy stone)'},
    c.BIOME_CATACOMBS: {'moss_density': 'none', 'base_darkness': 0.5, 'name': 'Catacombs (bone-white brick)'},
    c.BIOME_CAVES: {'moss_density': 'light', 'base_darkness': 1.2, 'name': 'Caves (dark earthy stone)'},
    c.BIOME_HELL: {'moss_density': 'none', 'base_darkness': 1.5, 'name': 'Hell (charred black brick)'},
    c.BIOME_ABYSS: {'moss_density': 'none', 'base_darkness': 1.3, 'name': 'Abyss (alien dark stone)'},
}

for biome, config in biome_wall_configs.items():
    print(f"  - Generating {config['name']} wall variants...")
    WALL_TEXTURES[biome] = []
    for i, seed in enumerate(wall_seeds):
        with RandomSeed(seed):
            if config['moss_density'] == 'none':
                # No moss - just weathered brick
                from textures.weathering import add_weathering
                brick_pil = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
                wall_pil = add_weathering(brick_pil, intensity=1.0)
            else:
                wall_pil = generate_moss_stone_texture(
                    size=1024,
                    moss_density=config['moss_density'],
                    base_darkness=config['base_darkness']
                )
            WALL_TEXTURES[biome].append(Texture(wall_pil))

print(f"  ✓ {len(WALL_TEXTURES)} biome wall sets generated ({sum(len(v) for v in WALL_TEXTURES.values())} total textures)")

# Normal Maps: Generate 4 variants for bump mapping per biome
# Use brick base ONLY (no moss) since moss doesn't affect surface geometry
from textures.bricks import generate_normal_map_from_brick_texture

WALL_NORMAL_MAPS = {}
for biome, config in biome_wall_configs.items():
    WALL_NORMAL_MAPS[biome] = []
    for i, seed in enumerate(wall_seeds):
        with RandomSeed(seed):
            # Generate brick base WITHOUT moss overlay
            # Normal maps represent actual geometry depth, not color variation
            brick_pil = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
            # EXTREME strength for cartoon effect (8.0 = super exaggerated depth)
            normal_map_pil = generate_normal_map_from_brick_texture(brick_pil, strength=8.0)
            WALL_NORMAL_MAPS[biome].append(Texture(normal_map_pil))

print(f"  ✓ {len(WALL_NORMAL_MAPS)} biome normal map sets generated ({sum(len(v) for v in WALL_NORMAL_MAPS.values())} total maps)")

# Floor: Generate 4 variants for EACH biome
FLOOR_TEXTURES = {}
floor_seeds = [11111, 22222, 33333, 44444]

biome_floor_configs = {
    c.BIOME_DUNGEON: {'moss_density': 'light', 'base_darkness': 0.8},
    c.BIOME_CATACOMBS: {'moss_density': 'none', 'base_darkness': 0.4},
    c.BIOME_CAVES: {'moss_density': 'medium', 'base_darkness': 1.0},
    c.BIOME_HELL: {'moss_density': 'none', 'base_darkness': 1.4},
    c.BIOME_ABYSS: {'moss_density': 'none', 'base_darkness': 1.2},
}

for biome, config in biome_floor_configs.items():
    FLOOR_TEXTURES[biome] = []
    for i, seed in enumerate(floor_seeds):
        with RandomSeed(seed):
            floor_brick = generate_brick_pattern(size=1024, darkness=config['base_darkness'])
            if config['moss_density'] == 'none':
                from textures.weathering import add_weathering
                floor_pil = add_weathering(floor_brick, intensity=0.8)
            else:
                floor_pil = generate_moss_overlay(floor_brick, density=config['moss_density'])
            FLOOR_TEXTURES[biome].append(Texture(floor_pil))

print(f"  ✓ {len(FLOOR_TEXTURES)} biome floor sets generated ({sum(len(v) for v in FLOOR_TEXTURES.values())} total textures)")

# Ceiling: Generate 4 variants for EACH biome
from textures.organic import generate_ceiling_texture
CEILING_TEXTURES = {}
ceiling_seeds = [55555, 66666, 77777, 88888]

biome_ceiling_configs = {
    c.BIOME_DUNGEON: {'moisture_level': 'medium'},
    c.BIOME_CATACOMBS: {'moisture_level': 'dry'},
    c.BIOME_CAVES: {'moisture_level': 'heavy'},
    c.BIOME_HELL: {'moisture_level': 'dry'},
    c.BIOME_ABYSS: {'moisture_level': 'dry'},
}

for biome, config in biome_ceiling_configs.items():
    CEILING_TEXTURES[biome] = []
    for i, seed in enumerate(ceiling_seeds):
        with RandomSeed(seed):
            ceiling_pil = generate_ceiling_texture(size=1024, moisture_level=config['moisture_level'])
            CEILING_TEXTURES[biome].append(Texture(ceiling_pil))

print(f"  ✓ {len(CEILING_TEXTURES)} biome ceiling sets generated ({sum(len(v) for v in CEILING_TEXTURES.values())} total textures)")

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


def create_floor_mesh(x: int, y: int, biome: str, biome_color):
    """
    Create a 3D floor tile mesh with procedural biome-specific texture

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome tint

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

    # Apply corner shadow shader for dramatic ambient occlusion
    floor_entity.shader = CORNER_SHADOW_SHADER

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


def create_stairs_mesh(x: int, y: int, biome_color):
    """
    Create a 3D staircase mesh

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome_color: RGB tuple (0-1 floats) for the biome

    Returns:
        Ursina Entity representing stairs going down
    """
    pos = world_to_3d_position(x, y, 0.2)

    # Convert color tuple to ursina color (multiply by 255 for 0-255 integer range)
    if isinstance(biome_color, tuple) and len(biome_color) == 3:
        stairs_color = ursina_color.rgb(biome_color[0] * 255, biome_color[1] * 255, biome_color[2] * 255)
    else:
        # Fallback to default stairs color
        stairs_color = ursina_color.rgb(c.COLOR_STAIRS_RGB[0] * 255, c.COLOR_STAIRS_RGB[1] * 255, c.COLOR_STAIRS_RGB[2] * 255)

    # Brighten stairs to make them stand out
    bright_color = ursina_color.rgb(
        min(255, stairs_color.r * 255 * 1.5),
        min(255, stairs_color.g * 255 * 1.5),
        min(255, stairs_color.b * 255 * 1.5)
    )

    # Simple stairs: cube with glow effect
    return Entity(
        model='cube',
        position=pos,
        scale=(0.8, 0.4, 0.8),
        color=bright_color,
        texture='white_cube'
    )


def create_ceiling_mesh(x: int, y: int, biome: str, biome_color):
    """
    Create a 3D ceiling tile mesh with procedural biome-specific texture

    Args:
        x: Grid X position
        y: Grid Y position (becomes Z in 3D space)
        biome: Biome name (e.g., c.BIOME_DUNGEON, c.BIOME_CATACOMBS, etc.)
        biome_color: RGB tuple (0-1 floats) for the biome tint

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

    # Apply corner shadow shader for dramatic ambient occlusion
    ceiling_entity.shader = CORNER_SHADOW_SHADER

    return ceiling_entity
