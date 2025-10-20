"""
Parameter interpolation system for creature library.

This module provides smooth interpolation between creature parameter sets
for level ranges in enemy packs. When a level falls between two defined
ranges, parameters are blended intelligently based on their type.
"""

from typing import Dict, Any, Tuple
import math


def interpolate_value(value1: Any, value2: Any, factor: float) -> Any:
    """
    Interpolate between two values based on factor.

    Args:
        value1: First value (at factor 0.0)
        value2: Second value (at factor 1.0)
        factor: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    # Handle numeric types
    if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        result = value1 + (value2 - value1) * factor

        # If both inputs are ints, round result (for discrete params like num_tentacles)
        if isinstance(value1, int) and isinstance(value2, int):
            return int(round(result))
        return result

    # Handle tuple/list (e.g., RGB colors)
    if isinstance(value1, (tuple, list)) and isinstance(value2, (tuple, list)):
        if len(value1) != len(value2):
            # Mismatched lengths, use closest
            return value1 if factor < 0.5 else value2

        interpolated = []
        for v1, v2 in zip(value1, value2):
            interpolated.append(interpolate_value(v1, v2, factor))

        # Preserve type (tuple vs list)
        return type(value1)(interpolated)

    # Handle dict (e.g., algorithm_params)
    if isinstance(value1, dict) and isinstance(value2, dict):
        result = {}
        # Get all keys from both dicts
        all_keys = set(value1.keys()) | set(value2.keys())

        for key in all_keys:
            if key in value1 and key in value2:
                # Both have this key, interpolate
                result[key] = interpolate_value(value1[key], value2[key], factor)
            elif key in value1:
                # Only in first dict
                result[key] = value1[key]
            else:
                # Only in second dict
                result[key] = value2[key]

        return result

    # Handle string/other types - pick closest
    if isinstance(value1, str) and isinstance(value2, str):
        return value1 if factor < 0.5 else value2

    # Default: return closest value
    return value1 if factor < 0.5 else value2


def interpolate_parameters(params1: Dict[str, Any],
                           params2: Dict[str, Any],
                           factor: float) -> Dict[str, Any]:
    """
    Interpolate between two parameter dictionaries.

    Args:
        params1: First parameter set (at factor 0.0)
        params2: Second parameter set (at factor 1.0)
        factor: Interpolation factor (0.0 to 1.0), clamped to [0, 1]

    Returns:
        Interpolated parameter dictionary

    Examples:
        >>> p1 = {'num_tentacles': 2, 'color': (0.5, 0.3, 0.7)}
        >>> p2 = {'num_tentacles': 8, 'color': (0.9, 0.1, 0.3)}
        >>> interpolate_parameters(p1, p2, 0.5)
        {'num_tentacles': 5, 'color': (0.7, 0.2, 0.5)}
    """
    # Clamp factor to [0, 1]
    factor = max(0.0, min(1.0, factor))

    result = {}

    # Get all keys from both dicts
    all_keys = set(params1.keys()) | set(params2.keys())

    for key in all_keys:
        if key in params1 and key in params2:
            # Both dicts have this parameter, interpolate
            result[key] = interpolate_value(params1[key], params2[key], factor)
        elif key in params1:
            # Only in first dict, use as-is
            result[key] = params1[key]
        else:
            # Only in second dict, use as-is
            result[key] = params2[key]

    return result


def get_interpolated_parameters_for_level(mappings: list,
                                          level: int) -> Dict[str, Any]:
    """
    Get interpolated parameters for a specific level from a list of mappings.

    This function handles three cases:
    1. Level falls within a mapping range - return exact parameters
    2. Level falls between two ranges - interpolate between boundary params
    3. Level is outside all ranges - return closest range parameters

    Args:
        mappings: List of EnemyMapping objects (should be sorted by level)
        level: Dungeon level (1-25)

    Returns:
        Parameter dictionary for the requested level

    Raises:
        ValueError: If mappings list is empty
    """
    if not mappings:
        raise ValueError("Mappings list is empty")

    # Clamp level to valid range
    level = max(1, min(25, level))

    # Sort mappings by start level
    sorted_mappings = sorted(mappings, key=lambda m: m.start_level)

    # Check if level falls within any mapping
    for mapping in sorted_mappings:
        if mapping.contains_level(level):
            # Exact match - return parameters as-is
            return mapping.parameters.copy()

    # Level is between ranges or outside - find closest ranges
    prev_mapping = None
    next_mapping = None

    for i, mapping in enumerate(sorted_mappings):
        if mapping.end_level < level:
            # This mapping is before our level
            prev_mapping = mapping
        elif mapping.start_level > level:
            # This mapping is after our level
            next_mapping = mapping
            break

    # Case 1: Level is before all mappings
    if prev_mapping is None:
        return sorted_mappings[0].parameters.copy()

    # Case 2: Level is after all mappings
    if next_mapping is None:
        return sorted_mappings[-1].parameters.copy()

    # Case 3: Level is between two mappings - interpolate
    # Calculate interpolation factor based on gap between ranges
    gap_start = prev_mapping.end_level + 1
    gap_end = next_mapping.start_level - 1
    gap_size = gap_end - gap_start + 1

    if gap_size <= 0:
        # No gap (adjacent or overlapping ranges), use closest
        return prev_mapping.parameters.copy()

    # Where in the gap is our level?
    position_in_gap = level - gap_start
    factor = position_in_gap / gap_size

    return interpolate_parameters(
        prev_mapping.parameters,
        next_mapping.parameters,
        factor
    )


def calculate_interpolation_factor(level: int,
                                   range1: Tuple[int, int],
                                   range2: Tuple[int, int]) -> float:
    """
    Calculate interpolation factor for a level between two ranges.

    Args:
        level: Current level
        range1: First level range (start, end)
        range2: Second level range (start, end)

    Returns:
        Interpolation factor (0.0 = use range1, 1.0 = use range2)

    Examples:
        >>> calculate_interpolation_factor(8, (1, 5), (11, 15))
        0.5  # Level 8 is halfway between ranges
    """
    # If level is in first range, factor = 0
    if range1[0] <= level <= range1[1]:
        return 0.0

    # If level is in second range, factor = 1
    if range2[0] <= level <= range2[1]:
        return 1.0

    # Calculate gap between ranges
    gap_start = range1[1] + 1
    gap_end = range2[0] - 1
    gap_size = gap_end - gap_start + 1

    if gap_size <= 0:
        # Ranges overlap or adjacent
        return 0.5

    # Position within gap
    position = level - gap_start
    return max(0.0, min(1.0, position / gap_size))


# Example usage and testing
if __name__ == '__main__':
    # Test basic interpolation
    p1 = {
        'num_tentacles': 2,
        'segments_per_tentacle': 8,
        'thickness_base': 0.2,
        'tentacle_color': (0.6, 0.3, 0.7),
        'algorithm': 'bezier'
    }

    p2 = {
        'num_tentacles': 12,
        'segments_per_tentacle': 18,
        'thickness_base': 0.35,
        'tentacle_color': (0.9, 0.1, 0.3),
        'algorithm': 'fourier'
    }

    # Test 0% (should be p1)
    result = interpolate_parameters(p1, p2, 0.0)
    print("0% interpolation:")
    print(result)
    print()

    # Test 50% (should be halfway)
    result = interpolate_parameters(p1, p2, 0.5)
    print("50% interpolation:")
    print(result)
    print()

    # Test 100% (should be p2)
    result = interpolate_parameters(p1, p2, 1.0)
    print("100% interpolation:")
    print(result)
    print()

    # Test with actual mappings
    from models.library_data import EnemyMapping

    mapping1 = EnemyMapping(
        level_range=(1, 5),
        creature_type='tentacle',
        parameters=p1
    )

    mapping2 = EnemyMapping(
        level_range=(11, 15),
        creature_type='tentacle',
        parameters=p2
    )

    # Test level in range
    print("Level 3 (in range 1-5):")
    result = get_interpolated_parameters_for_level([mapping1, mapping2], 3)
    print(f"num_tentacles: {result['num_tentacles']}")
    print()

    # Test level between ranges
    print("Level 8 (between ranges):")
    result = get_interpolated_parameters_for_level([mapping1, mapping2], 8)
    print(f"num_tentacles: {result['num_tentacles']} (should be ~7)")
    print(f"thickness_base: {result['thickness_base']:.2f}")
    print()

    # Test level after all ranges
    print("Level 20 (after all ranges):")
    result = get_interpolated_parameters_for_level([mapping1, mapping2], 20)
    print(f"num_tentacles: {result['num_tentacles']} (should be 12)")
