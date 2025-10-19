"""
Corner Shadow Shader for Ambient Occlusion Effect

Applies dramatic corner darkening to floor and ceiling tiles.
Creates gradient from bright center (1.0) to ultra-dark corners (0.15).

Used for atmospheric depth and horror-game aesthetic.
"""

from ursina import Shader


def create_corner_shadow_shader(intensity: float = 0.85) -> Shader:
    """
    Create fragment shader that darkens tile corners for ambient occlusion effect.

    The shader calculates distance from UV coordinates to the nearest edge,
    then applies a power curve to create dramatic falloff. Result is multiplied
    with the base texture color.

    Args:
        intensity: Shadow darkness (0.0 = no effect, 1.0 = maximum darkness)
                  0.85 creates ultra-dark corners (0.15 brightness)
                  0.70 creates dark corners (0.25 brightness)
                  0.50 creates moderate corners (0.4 brightness)

    Returns:
        Ursina Shader object ready to apply to Entity

    Example:
        shader = create_corner_shadow_shader(intensity=0.85)
        floor_entity.shader = shader
    """

    # Vertex shader (standard pass-through)
    vertex_shader = """
    #version 140

    in vec4 p3d_Vertex;
    in vec2 p3d_MultiTexCoord0;
    out vec2 texcoord;

    uniform mat4 p3d_ModelViewProjectionMatrix;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        texcoord = p3d_MultiTexCoord0;
    }
    """

    # Fragment shader with corner darkening logic
    fragment_shader = f"""
    #version 140

    uniform sampler2D p3d_Texture0;
    in vec2 texcoord;
    out vec4 fragColor;

    const float intensity = {intensity};
    const float min_brightness = 0.15;  // Ultra-dark corners (15% brightness)
    const float max_brightness = 1.0;   // Full brightness at center

    void main() {{
        // Sample base texture color
        vec4 texColor = texture(p3d_Texture0, texcoord);

        // Calculate distance from UV coord to nearest edge
        // texcoord ranges from (0,0) at corner to (1,1) at opposite corner
        // We want (0.5, 0.5) to be the brightest point
        vec2 centered = abs(texcoord - vec2(0.5, 0.5));

        // Distance to nearest edge (0.0 at edges, 0.5 at center)
        float dist_to_edge = min(centered.x, centered.y);

        // Normalize to 0-1 range (0 at edge, 1 at center)
        float normalized = dist_to_edge * 2.0;

        // Apply power curve for dramatic falloff
        // Higher intensity = darker corners
        // pow(normalized, exponent) where exponent = 1.0 - intensity
        // intensity=0.85 -> exponent=0.15 -> very steep curve = very dark corners
        float darkening = pow(normalized, 1.0 - intensity);

        // Map to brightness range (min_brightness at corners, max at center)
        float brightness = min_brightness + (darkening * (max_brightness - min_brightness));

        // Apply darkening to RGB channels only (preserve alpha)
        fragColor = vec4(texColor.rgb * brightness, texColor.a);
    }}
    """

    return Shader(
        vertex=vertex_shader,
        fragment=fragment_shader,
        name='corner_shadow'
    )


__all__ = ['create_corner_shadow_shader']
