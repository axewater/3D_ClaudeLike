"""
Enemy Model Cache System

Caches procedurally generated enemy creature DNA parameters to disk for faster startup.
Saves creation parameters as JSON files and loads them on subsequent game sessions.

This system works in conjunction with the enemy pack system to cache the interpolated
DNA parameters for each unique enemy type + creation combination.

Cache Structure:
    ursina_cache/enemy_models/
    └── my_first_pack/
        ├── ENEMY_STARTLE_starfish_small.json
        ├── ENEMY_STARTLE_starfish_mediumz.json
        ├── ENEMY_SLIME_blob_simple.json
        └── ... (one file per unique creation)

Performance:
    - First run (no cache): Full DNA generation (~50-200ms per enemy type)
    - Subsequent runs (with cache): Quick JSON load (~5-10ms per enemy type)
    - ~10-20x speedup after initial generation
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

# Cache directory structure
CACHE_ROOT = Path("ursina_cache/enemy_models")


def ensure_cache_directory(pack_name: str) -> Path:
    """
    Create cache directory for a specific enemy pack.

    Args:
        pack_name: Name of the enemy pack (e.g., "my_first_pack")

    Returns:
        Path to the pack's cache directory
    """
    pack_dir = CACHE_ROOT / sanitize_pack_name(pack_name)
    pack_dir.mkdir(parents=True, exist_ok=True)
    return pack_dir


def sanitize_pack_name(pack_name: str) -> str:
    """
    Convert pack name to safe directory name.

    Args:
        pack_name: Enemy pack name

    Returns:
        Filesystem-safe name
    """
    # Remove extension if present
    if pack_name.endswith('.json'):
        pack_name = pack_name[:-5]

    # Convert to safe filename
    safe_name = "".join(
        c if c.isalnum() or c in ('_', '-') else '_'
        for c in pack_name
    )
    return safe_name.lower()


def get_cache_key(enemy_type: str, creation_name: str) -> str:
    """
    Generate cache key for a specific enemy+creation combination.

    Args:
        enemy_type: Enemy type constant (e.g., "ENEMY_STARTLE")
        creation_name: Creation name from library (e.g., "Starfish Small")

    Returns:
        Cache key string (filesystem-safe)
    """
    # Sanitize creation name
    safe_creation = "".join(
        c if c.isalnum() or c in ('_', '-') else '_'
        for c in creation_name
    )
    safe_creation = safe_creation.lower()

    return f"{enemy_type}_{safe_creation}"


def get_cache_filename(pack_name: str, enemy_type: str, creation_name: str) -> Path:
    """
    Get cache file path for a specific enemy model.

    Args:
        pack_name: Enemy pack name
        enemy_type: Enemy type constant
        creation_name: Creation name from library

    Returns:
        Path to cache file
    """
    pack_dir = CACHE_ROOT / sanitize_pack_name(pack_name)
    cache_key = get_cache_key(enemy_type, creation_name)
    return pack_dir / f"{cache_key}.json"


def cache_exists(pack_name: str, enemy_type: str, creation_name: str) -> bool:
    """
    Check if cached model data exists for specific enemy.

    Args:
        pack_name: Enemy pack name
        enemy_type: Enemy type constant
        creation_name: Creation name from library

    Returns:
        True if cache file exists
    """
    cache_file = get_cache_filename(pack_name, enemy_type, creation_name)
    return cache_file.exists()


def pack_cache_exists(pack_name: str) -> bool:
    """
    Check if any cache exists for a specific pack.

    Args:
        pack_name: Enemy pack name

    Returns:
        True if pack cache directory exists and has files
    """
    pack_dir = CACHE_ROOT / sanitize_pack_name(pack_name)
    if not pack_dir.exists():
        return False

    # Check if directory has any .json files
    json_files = list(pack_dir.glob("*.json"))
    return len(json_files) > 0


def save_model_to_cache(pack_name: str, enemy_type: str, creation_name: str,
                        creature_type: str, dna_parameters: Dict[str, Any]):
    """
    Save enemy model DNA parameters to cache.

    Args:
        pack_name: Enemy pack name
        enemy_type: Enemy type constant
        creation_name: Creation name from library
        creature_type: Creature type (e.g., "tentacle", "blob", "starfish")
        dna_parameters: Dictionary of DNA parameters for creature generation
    """
    ensure_cache_directory(pack_name)
    cache_file = get_cache_filename(pack_name, enemy_type, creation_name)

    cache_data = {
        "enemy_type": enemy_type,
        "creation_name": creation_name,
        "creature_type": creature_type,
        "dna_parameters": dna_parameters
    }

    with open(cache_file, 'w') as f:
        json.dump(cache_data, f, indent=2)

    print(f"✓ Cached {enemy_type}/{creation_name} to {cache_file.name}")


def load_model_from_cache(pack_name: str, enemy_type: str, creation_name: str) -> Optional[Dict[str, Any]]:
    """
    Load enemy model DNA parameters from cache.

    Args:
        pack_name: Enemy pack name
        enemy_type: Enemy type constant
        creation_name: Creation name from library

    Returns:
        Dict with 'creature_type' and 'dna_parameters' keys, or None if not cached
    """
    cache_file = get_cache_filename(pack_name, enemy_type, creation_name)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        return {
            "creature_type": cache_data["creature_type"],
            "dna_parameters": cache_data["dna_parameters"]
        }

    except Exception as e:
        print(f"⚠ Failed to load cache for {enemy_type}/{creation_name}: {e}")
        return None


def clear_pack_cache(pack_name: str):
    """
    Delete all cached models for a specific enemy pack.

    Args:
        pack_name: Enemy pack name
    """
    pack_dir = CACHE_ROOT / sanitize_pack_name(pack_name)

    if not pack_dir.exists():
        return

    deleted_count = 0
    for cache_file in pack_dir.glob("*.json"):
        cache_file.unlink()
        deleted_count += 1

    # Remove empty directory
    if deleted_count > 0:
        try:
            pack_dir.rmdir()
        except OSError:
            pass  # Directory not empty, leave it

    print(f"✓ Cleared {deleted_count} cached models for pack '{pack_name}'")


def clear_all_cache():
    """Delete all cached enemy models for all packs."""
    if not CACHE_ROOT.exists():
        return

    total_deleted = 0

    for pack_dir in CACHE_ROOT.iterdir():
        if pack_dir.is_dir():
            for cache_file in pack_dir.glob("*.json"):
                cache_file.unlink()
                total_deleted += 1

            # Remove empty pack directory
            try:
                pack_dir.rmdir()
            except OSError:
                pass

    print(f"✓ Cleared all enemy model cache ({total_deleted} files)")


def get_cache_info() -> Dict[str, Any]:
    """
    Get information about the cache state.

    Returns:
        Dictionary with cache statistics:
        {
            "exists": bool,
            "directory": str,
            "total_files": int,
            "packs": {pack_name: file_count, ...}
        }
    """
    info = {
        "exists": CACHE_ROOT.exists(),
        "directory": str(CACHE_ROOT),
        "total_files": 0,
        "packs": {}
    }

    if not CACHE_ROOT.exists():
        return info

    for pack_dir in CACHE_ROOT.iterdir():
        if pack_dir.is_dir():
            json_files = list(pack_dir.glob("*.json"))
            file_count = len(json_files)
            if file_count > 0:
                info["packs"][pack_dir.name] = file_count
                info["total_files"] += file_count

    return info


# Example usage
if __name__ == '__main__':
    print("Enemy Model Cache System")
    print("=" * 50)

    # Get cache info
    info = get_cache_info()
    print(f"\nCache directory: {info['directory']}")
    print(f"Cache exists: {info['exists']}")
    print(f"Total cached models: {info['total_files']}")

    if info['packs']:
        print("\nCached packs:")
        for pack_name, count in info['packs'].items():
            print(f"  - {pack_name}: {count} models")
    else:
        print("\nNo cached models found.")
