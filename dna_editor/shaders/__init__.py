"""
Shader module for DNA Editor.

Provides custom shaders for stylized rendering.
"""

from .toon_shader import create_toon_shader, create_toon_shader_lite

# Size threshold for shader LOD (Level of Detail)
# Spheres with scale < this value use the lite shader for better performance
SHADER_LOD_THRESHOLD = 0.25


def get_shader_for_scale(scale, full_shader, lite_shader):
    """
    Select appropriate shader based on sphere scale for performance optimization.

    Args:
        scale: Sphere scale value (float or Vec3)
        full_shader: Enhanced toon shader instance
        lite_shader: Simplified toon shader instance

    Returns:
        Shader instance appropriate for the given scale
    """
    # Handle Vec3 scale (take the largest component)
    if hasattr(scale, '__iter__'):
        scale_value = max(abs(s) for s in scale)
    else:
        scale_value = abs(scale)

    # Choose shader based on threshold
    return full_shader if scale_value >= SHADER_LOD_THRESHOLD else lite_shader


__all__ = ['create_toon_shader', 'create_toon_shader_lite', 'get_shader_for_scale', 'SHADER_LOD_THRESHOLD']
