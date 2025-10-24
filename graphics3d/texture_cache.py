"""
Texture Cache System

Caches procedurally generated biome textures to disk for faster startup.
Saves PIL images as PNG files and loads them on subsequent launches.
"""

import os
from pathlib import Path
from typing import Dict, List
from PIL import Image
from ursina import Texture
import constants as c


# Cache directory structure
CACHE_ROOT = Path("ursina_cache/textures")
CACHE_SUBDIRS = {
    'walls': CACHE_ROOT / "walls",
    'normal_maps': CACHE_ROOT / "normal_maps",
    'floors': CACHE_ROOT / "floors",
    'ceilings': CACHE_ROOT / "ceilings",
}

# Biome name mapping (constants -> filename-safe names)
BIOME_NAMES = {
    c.BIOME_DUNGEON: "dungeon",
    c.BIOME_CATACOMBS: "catacombs",
    c.BIOME_CAVES: "caves",
    c.BIOME_HELL: "hell",
    c.BIOME_ABYSS: "abyss",
}


def cache_exists() -> bool:
    """
    Check if texture cache exists and is complete.

    Returns:
        True if all 80 expected texture files are present, False otherwise
    """
    # Check if cache directories exist
    for cache_dir in CACHE_SUBDIRS.values():
        if not cache_dir.exists():
            return False

    # Check if all expected files exist (5 biomes × 4 variants = 20 per category)
    expected_count = 20
    for cache_dir in CACHE_SUBDIRS.values():
        files = list(cache_dir.glob("*.png"))
        if len(files) != expected_count:
            return False

    return True


def get_cache_filename(cache_type: str, biome: str, variant_idx: int) -> Path:
    """
    Get cache filename for a specific texture.

    Args:
        cache_type: Type of texture ('walls', 'normal_maps', 'floors', 'ceilings')
        biome: Biome constant (e.g., c.BIOME_DUNGEON)
        variant_idx: Variant index (0-3)

    Returns:
        Path to cache file
    """
    biome_name = BIOME_NAMES.get(biome, "unknown")
    cache_dir = CACHE_SUBDIRS[cache_type]
    return cache_dir / f"{biome_name}_{variant_idx}.png"


def save_texture_cache(
    wall_images: Dict[str, List[Image.Image]],
    normal_map_images: Dict[str, List[Image.Image]],
    floor_images: Dict[str, List[Image.Image]],
    ceiling_images: Dict[str, List[Image.Image]]
):
    """
    Save all procedurally generated textures to disk cache.

    Args:
        wall_images: Dict[biome -> List[PIL.Image]] for wall textures
        normal_map_images: Dict[biome -> List[PIL.Image]] for normal maps
        floor_images: Dict[biome -> List[PIL.Image]] for floor textures
        ceiling_images: Dict[biome -> List[PIL.Image]] for ceiling textures
    """
    print("Saving texture cache to disk...")

    # Create cache directories
    for cache_dir in CACHE_SUBDIRS.values():
        cache_dir.mkdir(parents=True, exist_ok=True)

    # Save wall textures
    for biome, images in wall_images.items():
        for i, img in enumerate(images):
            cache_path = get_cache_filename('walls', biome, i)
            img.save(cache_path, 'PNG')

    # Save normal maps
    for biome, images in normal_map_images.items():
        for i, img in enumerate(images):
            cache_path = get_cache_filename('normal_maps', biome, i)
            img.save(cache_path, 'PNG')

    # Save floor textures
    for biome, images in floor_images.items():
        for i, img in enumerate(images):
            cache_path = get_cache_filename('floors', biome, i)
            img.save(cache_path, 'PNG')

    # Save ceiling textures
    for biome, images in ceiling_images.items():
        for i, img in enumerate(images):
            cache_path = get_cache_filename('ceilings', biome, i)
            img.save(cache_path, 'PNG')



def load_texture_cache() -> tuple:
    """
    Load all textures from disk cache.

    Returns:
        Tuple of (wall_textures, normal_maps, floor_textures, ceiling_textures)
        Each is a Dict[biome -> List[Texture]] ready for use in tiles.py
    """
    # Load wall textures
    wall_textures = {}
    for biome in BIOME_NAMES.keys():
        wall_textures[biome] = []
        for i in range(4):  # 4 variants per biome
            cache_path = get_cache_filename('walls', biome, i)
            pil_image = Image.open(cache_path)
            wall_textures[biome].append(Texture(pil_image))

    # Load normal maps
    normal_maps = {}
    for biome in BIOME_NAMES.keys():
        normal_maps[biome] = []
        for i in range(4):
            cache_path = get_cache_filename('normal_maps', biome, i)
            pil_image = Image.open(cache_path)
            normal_maps[biome].append(Texture(pil_image))

    # Load floor textures
    floor_textures = {}
    for biome in BIOME_NAMES.keys():
        floor_textures[biome] = []
        for i in range(4):
            cache_path = get_cache_filename('floors', biome, i)
            pil_image = Image.open(cache_path)
            floor_textures[biome].append(Texture(pil_image))

    # Load ceiling textures
    ceiling_textures = {}
    for biome in BIOME_NAMES.keys():
        ceiling_textures[biome] = []
        for i in range(4):
            cache_path = get_cache_filename('ceilings', biome, i)
            pil_image = Image.open(cache_path)
            ceiling_textures[biome].append(Texture(pil_image))

    return wall_textures, normal_maps, floor_textures, ceiling_textures
