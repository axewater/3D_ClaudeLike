"""
Creature library package.

Provides tools for organizing creature creations into enemy packs.
"""

from .interpolator import (
    interpolate_value,
    interpolate_parameters,
    get_interpolated_parameters_for_level,
    calculate_interpolation_factor
)

__all__ = [
    'interpolate_value',
    'interpolate_parameters',
    'get_interpolated_parameters_for_level',
    'calculate_interpolation_factor'
]
