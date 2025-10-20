"""
Data models for creature library and enemy pack management.

This module defines the core data structures for:
- Creation: Individual creature presets saved from the DNA editor
- EnemyMapping: Assignment of a creation to an enemy type with level range
- EnemyPack: Complete collection of enemy mappings for all enemy types

These classes provide JSON serialization/deserialization for persistence.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class Creation:
    """
    Represents a saved creature preset from the DNA editor.

    Creations are neutral - they contain only creature type and parameters,
    without any enemy or level associations (that's defined in the library).
    """

    def __init__(self, name: str, creature_type: str, parameters: Dict[str, Any]):
        """
        Args:
            name: Human-readable name for this creation
            creature_type: One of: 'tentacle', 'blob', 'polyp', 'starfish', 'medusa', 'dragon'
            parameters: Dictionary of creature-specific DNA parameters
        """
        self.name = name
        self.creature_type = creature_type
        self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "creature_type": self.creature_type,
            "parameters": self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Creation':
        """Create Creation from dictionary (JSON deserialization)."""
        return cls(
            name=data["name"],
            creature_type=data["creature_type"],
            parameters=data["parameters"]
        )

    def save_to_file(self, file_path: Path) -> None:
        """Save this creation to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'Creation':
        """Load a creation from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self):
        return f"Creation(name='{self.name}', type='{self.creature_type}')"


class EnemyMapping:
    """
    Represents a level range assignment of a creation to an enemy type.

    Each mapping specifies which creature to use for a specific enemy type
    across a range of dungeon levels, with parameter interpolation support.
    """

    def __init__(self,
                 level_range: Tuple[int, int],
                 creature_type: str,
                 parameters: Dict[str, Any],
                 creation_name: Optional[str] = None):
        """
        Args:
            level_range: (start_level, end_level) tuple, e.g., (1, 5)
            creature_type: Which creature model to use
            parameters: Creature DNA parameters for this level range
            creation_name: Optional reference to source creation name
        """
        self.level_range = level_range
        self.creature_type = creature_type
        self.parameters = parameters
        self.creation_name = creation_name

        # Validation
        if not (1 <= level_range[0] <= level_range[1] <= 25):
            raise ValueError(f"Invalid level range: {level_range}. Must be between 1-25.")

    @property
    def start_level(self) -> int:
        return self.level_range[0]

    @property
    def end_level(self) -> int:
        return self.level_range[1]

    def contains_level(self, level: int) -> bool:
        """Check if this mapping covers the given level."""
        return self.start_level <= level <= self.end_level

    def overlaps_with(self, other: 'EnemyMapping') -> bool:
        """Check if this mapping overlaps with another mapping."""
        return not (self.end_level < other.start_level or self.start_level > other.end_level)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "level_range": list(self.level_range),
            "creature_type": self.creature_type,
            "parameters": self.parameters
        }
        if self.creation_name:
            data["creation_name"] = self.creation_name
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnemyMapping':
        """Create EnemyMapping from dictionary (JSON deserialization)."""
        return cls(
            level_range=tuple(data["level_range"]),
            creature_type=data["creature_type"],
            parameters=data["parameters"],
            creation_name=data.get("creation_name")
        )

    def __repr__(self):
        return f"EnemyMapping(levels {self.level_range[0]}-{self.level_range[1]}, {self.creature_type})"


class EnemyPack:
    """
    Complete enemy pack containing all enemy type mappings.

    This is the top-level data structure that gets saved/loaded as JSON files.
    It defines the complete enemy appearance configuration for all levels.
    """

    # Valid enemy type names (from game constants)
    VALID_ENEMY_TYPES = [
        "ENEMY_STARTLE",  # Starfish creature
        "ENEMY_SLIME",    # Blob creature
        "ENEMY_SKELETON", # Polyp creature
        "ENEMY_ORC",      # Tentacle creature
        "ENEMY_DEMON",    # Medusa creature
        "ENEMY_DRAGON"    # Dragon creature
    ]

    # Valid creature types (from DNA editor)
    VALID_CREATURE_TYPES = [
        "starfish",
        "blob",
        "polyp",
        "tentacle",
        "medusa",
        "dragon"
    ]

    def __init__(self, pack_name: str, version: str = "1.0"):
        """
        Args:
            pack_name: Human-readable name for this enemy pack
            version: Pack format version (for future compatibility)
        """
        self.pack_name = pack_name
        self.version = version
        # Dictionary: enemy_type -> list of EnemyMapping objects
        self.enemies: Dict[str, List[EnemyMapping]] = {
            enemy_type: [] for enemy_type in self.VALID_ENEMY_TYPES
        }

    def add_mapping(self, enemy_type: str, mapping: EnemyMapping) -> None:
        """
        Add a mapping to an enemy type.

        Args:
            enemy_type: One of VALID_ENEMY_TYPES
            mapping: EnemyMapping to add

        Raises:
            ValueError: If enemy_type is invalid or mapping overlaps with existing
        """
        if enemy_type not in self.VALID_ENEMY_TYPES:
            raise ValueError(f"Invalid enemy type: {enemy_type}")

        # Check for overlaps
        for existing in self.enemies[enemy_type]:
            if existing.overlaps_with(mapping):
                raise ValueError(
                    f"Mapping {mapping} overlaps with existing mapping {existing}"
                )

        self.enemies[enemy_type].append(mapping)
        # Keep sorted by level range start
        self.enemies[enemy_type].sort(key=lambda m: m.start_level)

    def remove_mapping(self, enemy_type: str, mapping: EnemyMapping) -> None:
        """Remove a mapping from an enemy type."""
        if enemy_type in self.enemies:
            self.enemies[enemy_type].remove(mapping)

    def get_mapping_for_level(self, enemy_type: str, level: int) -> Optional[EnemyMapping]:
        """
        Get the mapping that covers a specific level for an enemy type.

        Args:
            enemy_type: Enemy type to query
            level: Dungeon level (1-25)

        Returns:
            EnemyMapping if found, None otherwise
        """
        if enemy_type not in self.enemies:
            return None

        for mapping in self.enemies[enemy_type]:
            if mapping.contains_level(level):
                return mapping
        return None

    def get_all_mappings(self, enemy_type: str) -> List[EnemyMapping]:
        """Get all mappings for an enemy type."""
        return self.enemies.get(enemy_type, [])

    def validate(self) -> List[str]:
        """
        Validate the enemy pack configuration.

        Returns:
            List of warning messages. Empty list if valid.

        Note:
            Empty mappings are allowed - the game will use default procedural
            generation for unconfigured enemies/levels.
        """
        warnings = []

        # Game spawn level ranges for validation context
        ENEMY_SPAWN_RANGES = {
            "ENEMY_STARTLE": (1, 5),
            "ENEMY_SLIME": (1, 5),
            "ENEMY_SKELETON": (2, 14),
            "ENEMY_ORC": (4, 19),
            "ENEMY_DEMON": (6, 25),
            "ENEMY_DRAGON": (10, 25)
        }

        for enemy_type in self.VALID_ENEMY_TYPES:
            mappings = self.enemies[enemy_type]

            if not mappings:
                # Empty mappings are OK - just inform the user
                warnings.append(
                    f"{enemy_type}: No mappings defined (will use default generation)"
                )
                continue

            # Get spawn range for this enemy
            spawn_range = ENEMY_SPAWN_RANGES.get(enemy_type, (1, 25))
            spawn_start, spawn_end = spawn_range

            # Check for gaps in level coverage (only within spawn range)
            covered_levels = set()
            for mapping in mappings:
                for level in range(mapping.start_level, mapping.end_level + 1):
                    covered_levels.add(level)

            # Only check for missing levels within the enemy's actual spawn range
            expected_levels = set(range(spawn_start, spawn_end + 1))
            missing_levels = expected_levels - covered_levels

            if missing_levels:
                warnings.append(
                    f"{enemy_type}: Partial coverage in spawn range {spawn_start}-{spawn_end}. "
                    f"Missing levels: {sorted(missing_levels)} (will use default generation)"
                )

            # Warn if mappings are outside spawn range
            for mapping in mappings:
                if mapping.start_level < spawn_start or mapping.end_level > spawn_end:
                    warnings.append(
                        f"{enemy_type}: Mapping {mapping.start_level}-{mapping.end_level} "
                        f"extends outside spawn range {spawn_start}-{spawn_end}"
                    )

            # Validate creature types
            for mapping in mappings:
                if mapping.creature_type not in self.VALID_CREATURE_TYPES:
                    warnings.append(
                        f"{enemy_type}: Invalid creature type '{mapping.creature_type}'"
                    )

        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pack_name": self.pack_name,
            "version": self.version,
            "enemies": {
                enemy_type: [mapping.to_dict() for mapping in mappings]
                for enemy_type, mappings in self.enemies.items()
                if mappings  # Only include enemies with mappings
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnemyPack':
        """Create EnemyPack from dictionary (JSON deserialization)."""
        pack = cls(
            pack_name=data["pack_name"],
            version=data.get("version", "1.0")
        )

        for enemy_type, mappings_data in data.get("enemies", {}).items():
            if enemy_type in cls.VALID_ENEMY_TYPES:
                for mapping_data in mappings_data:
                    mapping = EnemyMapping.from_dict(mapping_data)
                    # Skip validation on load (allow loading of packs with warnings)
                    pack.enemies[enemy_type].append(mapping)
                pack.enemies[enemy_type].sort(key=lambda m: m.start_level)

        return pack

    def save_to_file(self, file_path: Path) -> None:
        """Save this enemy pack to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'EnemyPack':
        """Load an enemy pack from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self):
        total_mappings = sum(len(mappings) for mappings in self.enemies.values())
        return f"EnemyPack(name='{self.pack_name}', {total_mappings} mappings)"


# Utility functions

def list_creations(creations_dir: Path) -> List[Creation]:
    """
    Load all creation files from a directory.

    Args:
        creations_dir: Path to directory containing creation JSON files

    Returns:
        List of Creation objects
    """
    creations = []
    if not creations_dir.exists():
        return creations

    for file_path in creations_dir.glob("*.json"):
        try:
            creation = Creation.load_from_file(file_path)
            creations.append(creation)
        except Exception as e:
            print(f"Warning: Failed to load creation from {file_path}: {e}")

    return creations


def list_enemy_packs(packs_dir: Path) -> List[EnemyPack]:
    """
    Load all enemy pack files from a directory.

    Args:
        packs_dir: Path to directory containing enemy pack JSON files

    Returns:
        List of EnemyPack objects
    """
    packs = []
    if not packs_dir.exists():
        return packs

    for file_path in packs_dir.glob("*.json"):
        try:
            pack = EnemyPack.load_from_file(file_path)
            packs.append(pack)
        except Exception as e:
            print(f"Warning: Failed to load enemy pack from {file_path}: {e}")

    return packs
