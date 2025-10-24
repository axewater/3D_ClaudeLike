"""
Edge-Based Corner Shadow Shader for Realistic Ambient Occlusion

Applies dramatic darkening ONLY at floor/ceiling edges that are adjacent to walls,
creating realistic ambient occlusion where walls meet horizontal surfaces.

Unlike traditional vignette effects that darken all 4 corners uniformly, this shader
detects which edges have walls and only darkens those specific edges, producing
much more realistic and spatially-accurate shadows.

Example visual (top-down view of floor tile):

    Wall present (N)           No walls
    ┌─────────────┐           ┌─────────────┐
    │▓▓▓▓▓▓▓▓▓▓▓▓▓│           │             │
    │░░░░░░░░░░░░░│           │             │
    │             │    vs     │      ☀     │
    │             │           │             │
    └─────────────┘           └─────────────┘
    (Shadow at N edge)        (No shadows)

Used for atmospheric depth and horror-game aesthetic.
"""

from ursina import Shader


def create_corner_shadow_shader(intensity: float = 0.85) -> Shader:
    """
    Create fragment shader that darkens tile edges ONLY where walls meet the floor.

    This creates realistic ambient occlusion by darkening only the edges adjacent
    to walls, not all 4 edges uniformly. The shader accepts uniforms indicating
    which edges have walls (North/South/East/West) and only darkens those edges.

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
        # Set which edges have walls (0.0 = no wall, 1.0 = wall present)
        floor_entity.set_shader_input('has_wall_north', 1.0)
        floor_entity.set_shader_input('has_wall_south', 0.0)
        floor_entity.set_shader_input('has_wall_east', 1.0)
        floor_entity.set_shader_input('has_wall_west', 0.0)
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

    # Fragment shader with edge-specific darkening logic
    fragment_shader = f"""
    #version 140

    uniform sampler2D p3d_Texture0;
    uniform float has_wall_north;  // 1.0 if wall at +Y (top edge), 0.0 otherwise
    uniform float has_wall_south;  // 1.0 if wall at -Y (bottom edge), 0.0 otherwise
    uniform float has_wall_east;   // 1.0 if wall at +X (right edge), 0.0 otherwise
    uniform float has_wall_west;   // 1.0 if wall at -X (left edge), 0.0 otherwise

    in vec2 texcoord;
    out vec4 fragColor;

    const float intensity = {intensity};
    const float min_brightness = 0.15;  // Ultra-dark at wall edges (15% brightness)
    const float max_brightness = 1.0;   // Full brightness away from walls
    const float shadow_width = 0.3;     // How far shadow extends from edge (0-0.5)

    void main() {{
        // Sample base texture color
        vec4 texColor = texture(p3d_Texture0, texcoord);

        // Start at full brightness
        float brightness = max_brightness;

        // Calculate distance from each edge (0.0 at edge, 1.0 at opposite edge)
        float dist_north = texcoord.y;         // Distance from top edge (v=0)
        float dist_south = 1.0 - texcoord.y;   // Distance from bottom edge (v=1)
        float dist_east = 1.0 - texcoord.x;    // Distance from right edge (u=1)
        float dist_west = texcoord.x;          // Distance from left edge (u=0)

        // For each wall edge, calculate shadow contribution
        // Only darken if wall is present (has_wall_* == 1.0)

        // North wall (top edge, v=0)
        if (has_wall_north > 0.5) {{
            float edge_factor = clamp(dist_north / shadow_width, 0.0, 1.0);
            float shadow = pow(edge_factor, 1.0 - intensity);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // South wall (bottom edge, v=1)
        if (has_wall_south > 0.5) {{
            float edge_factor = clamp(dist_south / shadow_width, 0.0, 1.0);
            float shadow = pow(edge_factor, 1.0 - intensity);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // East wall (right edge, u=1)
        if (has_wall_east > 0.5) {{
            float edge_factor = clamp(dist_east / shadow_width, 0.0, 1.0);
            float shadow = pow(edge_factor, 1.0 - intensity);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // West wall (left edge, u=0)
        if (has_wall_west > 0.5) {{
            float edge_factor = clamp(dist_west / shadow_width, 0.0, 1.0);
            float shadow = pow(edge_factor, 1.0 - intensity);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

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
