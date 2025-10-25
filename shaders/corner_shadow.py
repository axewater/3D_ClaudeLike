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
    // Cardinal direction walls (N/S/E/W)
    uniform float has_wall_north;  // 1.0 if wall at +Y (top edge), 0.0 otherwise
    uniform float has_wall_south;  // 1.0 if wall at -Y (bottom edge), 0.0 otherwise
    uniform float has_wall_east;   // 1.0 if wall at +X (right edge), 0.0 otherwise
    uniform float has_wall_west;   // 1.0 if wall at -X (left edge), 0.0 otherwise
    // Diagonal direction walls (NE/NW/SE/SW) for convex corners
    uniform float has_wall_ne;     // 1.0 if wall at (+X, -Y) (northeast diagonal), 0.0 otherwise
    uniform float has_wall_nw;     // 1.0 if wall at (-X, -Y) (northwest diagonal), 0.0 otherwise
    uniform float has_wall_se;     // 1.0 if wall at (+X, +Y) (southeast diagonal), 0.0 otherwise
    uniform float has_wall_sw;     // 1.0 if wall at (-X, +Y) (southwest diagonal), 0.0 otherwise

    in vec2 texcoord;
    out vec4 fragColor;

    const float intensity = {intensity};
    const float min_brightness = 0.35;  // Subtle shadow at wall edges (35% brightness)
    const float corner_brightness = 0.25;  // Slightly darker at corners (25% brightness)
    const float max_brightness = 1.0;   // Full brightness away from walls
    const float shadow_width = 0.35;     // How far shadow extends from edge (wider spread)
    const float falloff_power = 1.8;    // Gentle falloff curve (lower = softer)

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

        // Track which walls are present for corner detection
        bool has_north = has_wall_north > 0.5;
        bool has_south = has_wall_south > 0.5;
        bool has_east = has_wall_east > 0.5;
        bool has_west = has_wall_west > 0.5;
        bool has_ne = has_wall_ne > 0.5;
        bool has_nw = has_wall_nw > 0.5;
        bool has_se = has_wall_se > 0.5;
        bool has_sw = has_wall_sw > 0.5;

        // For each wall edge, calculate shadow contribution with smooth S-curve falloff
        // Only darken if wall is present (has_wall_* == 1.0)

        // North wall (top edge, v=0)
        if (has_north) {{
            float edge_factor = smoothstep(0.0, shadow_width, dist_north);  // S-curve for smooth ease
            float shadow = pow(edge_factor, falloff_power);  // Gentle falloff
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // South wall (bottom edge, v=1)
        if (has_south) {{
            float edge_factor = smoothstep(0.0, shadow_width, dist_south);
            float shadow = pow(edge_factor, falloff_power);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // East wall (right edge, u=1)
        if (has_east) {{
            float edge_factor = smoothstep(0.0, shadow_width, dist_east);
            float shadow = pow(edge_factor, falloff_power);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // West wall (left edge, u=0)
        if (has_west) {{
            float edge_factor = smoothstep(0.0, shadow_width, dist_west);
            float shadow = pow(edge_factor, falloff_power);
            brightness = min(brightness, min_brightness + shadow * (max_brightness - min_brightness));
        }}

        // ===== CORNER-CORNER INTERACTIONS =====
        // Apply extra darkening at corners where two walls meet
        // Uses smooth radial blending instead of min() to avoid harsh diagonal lines

        // Northwest corner (north + west walls)
        if (has_north && has_west) {{
            // Use radial distance for smooth circular falloff (no harsh diagonal)
            float corner_dist = sqrt(dist_north * dist_north + dist_west * dist_west) / 1.414;  // Normalize by sqrt(2)
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);  // S-curve for smooth transition
            corner_factor = pow(corner_factor, falloff_power * 1.2);  // Gentler power (1.2 instead of 1.5)
            brightness = min(brightness, corner_brightness + corner_factor * (max_brightness - corner_brightness));
        }}

        // Northeast corner (north + east walls)
        if (has_north && has_east) {{
            float corner_dist = sqrt(dist_north * dist_north + dist_east * dist_east) / 1.414;
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power * 1.2);
            brightness = min(brightness, corner_brightness + corner_factor * (max_brightness - corner_brightness));
        }}

        // Southwest corner (south + west walls)
        if (has_south && has_west) {{
            float corner_dist = sqrt(dist_south * dist_south + dist_west * dist_west) / 1.414;
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power * 1.2);
            brightness = min(brightness, corner_brightness + corner_factor * (max_brightness - corner_brightness));
        }}

        // Southeast corner (south + east walls)
        if (has_south && has_east) {{
            float corner_dist = sqrt(dist_south * dist_south + dist_east * dist_east) / 1.414;
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power * 1.2);
            brightness = min(brightness, corner_brightness + corner_factor * (max_brightness - corner_brightness));
        }}

        // ===== CONVEX CORNER SHADOWS (OUTWARD-FACING CORNERS) =====
        // Apply shadows at diagonal walls where NO adjacent cardinal walls exist
        // Use max() of two edge distances to create L-shaped shadow that blends with wall edges
        // (e.g., if wall is at NE diagonal, shadow appears in NE corner of this tile)

        // NE diagonal wall -> shadow in NE corner (this corner touches the protruding wall)
        if (has_ne && !has_north && !has_east) {{
            // Use max distance to create L-shaped shadow matching wall edge shadows
            float corner_dist = max(dist_north, dist_east);
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power);  // Same falloff as edges
            brightness = min(brightness, min_brightness + corner_factor * (max_brightness - min_brightness));
        }}

        // NW diagonal wall -> shadow in NW corner (this corner touches the protruding wall)
        if (has_nw && !has_north && !has_west) {{
            float corner_dist = max(dist_north, dist_west);
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power);  // Same falloff as edges
            brightness = min(brightness, min_brightness + corner_factor * (max_brightness - min_brightness));
        }}

        // SE diagonal wall -> shadow in SE corner (this corner touches the protruding wall)
        if (has_se && !has_south && !has_east) {{
            float corner_dist = max(dist_south, dist_east);
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power);  // Same falloff as edges
            brightness = min(brightness, min_brightness + corner_factor * (max_brightness - min_brightness));
        }}

        // SW diagonal wall -> shadow in SW corner (this corner touches the protruding wall)
        if (has_sw && !has_south && !has_west) {{
            float corner_dist = max(dist_south, dist_west);
            float corner_factor = smoothstep(0.0, shadow_width, corner_dist);
            corner_factor = pow(corner_factor, falloff_power);  // Same falloff as edges
            brightness = min(brightness, min_brightness + corner_factor * (max_brightness - min_brightness));
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
