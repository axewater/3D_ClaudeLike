"""
Shader library for post-processing effects

This package contains GLSL shaders for camera and rendering effects.
"""

from .barrel_distortion import create_barrel_distortion_shader
from .corner_shadow import create_corner_shadow_shader
from .toon_normal_shader import create_toon_normal_shader
from .radial_shadow import create_radial_shadow_shader

__all__ = ['create_barrel_distortion_shader', 'create_corner_shadow_shader', 'create_toon_normal_shader', 'create_radial_shadow_shader']
