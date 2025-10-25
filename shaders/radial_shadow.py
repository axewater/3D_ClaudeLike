"""
Radial Shadow Shader for Creature Contact Shadows

Creates soft circular shadows with smooth radial falloff from center to edge.
Used for player and enemy shadows on the ground.

Visual effect (top-down view):
    ░░░░░░░░░
    ░▒▒▒▒▒▒░
    ░▒▓▓▓▒░
    ░▒▒▒▒▒░
    ░░░░░░░

Dark at center, smoothly fades to transparent at edges.
"""

from ursina import Shader


def create_radial_shadow_shader(max_alpha: float = 0.5, falloff_power: float = 2.0) -> Shader:
    """
    Create a shader for circular shadows with smooth radial falloff.

    Args:
        max_alpha: Maximum opacity at center (0.0 = invisible, 1.0 = opaque)
                   0.5 = moderately dark shadow
                   0.7 = darker shadow
        falloff_power: Controls how quickly shadow fades (higher = sharper edge)
                      1.0 = linear falloff
                      2.0 = quadratic falloff (softer center, sharper edge)
                      3.0 = cubic falloff (very sharp edge)

    Returns:
        Ursina Shader object ready to apply to Entity

    Example:
        shader = create_radial_shadow_shader(max_alpha=0.5, falloff_power=2.0)
        shadow_entity = Entity(model='circle', color=color.black)
        shadow_entity.shader = shader
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

    # Fragment shader with radial falloff
    fragment_shader = f"""
    #version 140

    uniform vec4 p3d_ColorScale;  // Base color (typically black)
    in vec2 texcoord;
    out vec4 fragColor;

    const float max_alpha = {max_alpha};
    const float falloff_power = {falloff_power};

    void main() {{
        // Calculate distance from center (0.5, 0.5)
        vec2 center = vec2(0.5, 0.5);
        float dist = distance(texcoord, center);

        // Normalize distance (0.0 at center, 1.0 at edge of circle)
        // Circle radius is 0.5 in texture space
        float normalized_dist = dist / 0.5;

        // Clamp to [0, 1] range
        normalized_dist = clamp(normalized_dist, 0.0, 1.0);

        // Apply falloff curve (inverted so center is opaque, edge is transparent)
        float alpha = max_alpha * (1.0 - pow(normalized_dist, falloff_power));

        // Apply to base color (preserve RGB, modulate alpha)
        fragColor = vec4(p3d_ColorScale.rgb, alpha);
    }}
    """

    return Shader(
        vertex=vertex_shader,
        fragment=fragment_shader,
        name='radial_shadow'
    )


__all__ = ['create_radial_shadow_shader']
