"""
Radial Gradient Shader for Glow Spheres

Creates a smooth radial gradient from opaque center to transparent edges.
Perfect for magical glow effects, energy orbs, and force fields.

Features:
- Radial alpha falloff (center = opaque, edge = transparent)
- Smooth gradient using distance from center
- Customizable falloff curve
- Preserves base color and lighting
"""

from ursina import Shader


def create_radial_gradient_shader(falloff_start=0.3, falloff_end=1.0, intensity=1.0):
    """
    Create a radial gradient shader with alpha falloff from center to edge.

    Args:
        falloff_start: Distance from center where fade begins (0.0-1.0)
                      Default 0.3 = solid center for inner 30%
        falloff_end: Distance where fully transparent (0.0-1.0)
                    Default 1.0 = fade completes at sphere edge
        intensity: Overall brightness multiplier (0.0-2.0)
                  Default 1.0 = normal brightness

    Returns:
        Shader: Ursina shader object with radial gradient

    Example:
        # Soft glow with large solid center
        shader = create_radial_gradient_shader(falloff_start=0.4, falloff_end=1.0)

        # Sharp energy orb with small solid center
        shader = create_radial_gradient_shader(falloff_start=0.1, falloff_end=0.8)
    """

    # Vertex shader - pass object-space position to fragment shader
    vertex_shader = '''
    #version 150

    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;

    in vec4 p3d_Vertex;
    in vec4 p3d_Color;

    out vec4 vColor;
    out vec3 vObjectPos;  // Position in object space (for distance calculation)

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

        // Pass vertex color
        vColor = p3d_Color;

        // Pass object-space position (before transforms)
        // For a sphere, this is perfect for radial distance calculation
        vObjectPos = p3d_Vertex.xyz;
    }
    '''

    # Fragment shader - calculate radial distance and apply alpha falloff
    fragment_shader = f'''
    #version 150

    uniform vec4 p3d_ColorScale;

    in vec4 vColor;
    in vec3 vObjectPos;

    out vec4 fragColor;

    // Shader parameters
    const float falloff_start = {falloff_start};
    const float falloff_end = {falloff_end};
    const float intensity = {intensity};

    void main() {{
        // Calculate distance from center of sphere (origin in object space)
        // For a unit sphere, distance ranges from 0.0 (center) to 1.0 (surface)
        float distFromCenter = length(vObjectPos);

        // Calculate alpha based on distance
        // smoothstep creates a smooth Hermite interpolation between two values
        // Returns 0.0 at falloff_start, 1.0 at falloff_end
        float alphaFalloff = 1.0 - smoothstep(falloff_start, falloff_end, distFromCenter);

        // Apply base color and intensity
        vec3 baseColor = vColor.rgb * p3d_ColorScale.rgb * intensity;

        // Combine base alpha with radial falloff
        float finalAlpha = vColor.a * p3d_ColorScale.a * alphaFalloff;

        // Output final color with radial alpha gradient
        fragColor = vec4(baseColor, finalAlpha);
    }}
    '''

    try:
        shader = Shader(
            vertex=vertex_shader,
            fragment=fragment_shader,
            name='radial_gradient_shader'
        )
        return shader
    except Exception as e:
        print(f"WARNING: Failed to create radial gradient shader: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_soft_glow_shader():
    """
    Preset: Soft magical glow with large solid center.
    Perfect for potion auras and ambient magic effects.
    """
    return create_radial_gradient_shader(falloff_start=0.4, falloff_end=1.0, intensity=1.2)


def create_energy_orb_shader():
    """
    Preset: Bright energy orb with sharp edges.
    Perfect for sword/shield epic/legendary glows.
    """
    return create_radial_gradient_shader(falloff_start=0.2, falloff_end=0.9, intensity=1.5)


def create_force_field_shader():
    """
    Preset: Diffuse force field with very soft edges.
    Perfect for shields and protective barriers.
    """
    return create_radial_gradient_shader(falloff_start=0.5, falloff_end=1.0, intensity=0.8)


__all__ = [
    'create_radial_gradient_shader',
    'create_soft_glow_shader',
    'create_energy_orb_shader',
    'create_force_field_shader'
]
