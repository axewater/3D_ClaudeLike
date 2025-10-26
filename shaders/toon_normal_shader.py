"""
Toon/Cell Shading Shader with Normal Mapping

Combines exaggerated normal mapping with cartoon-style stepped lighting
to create dramatic 3D depth with a stylized aesthetic.

Features:
- 4-level quantized lighting (deep shadow, shadow, mid-tone, highlight)
- Normal map support for brick depth perception
- Rim lighting on edges for extra pop
- Deep black mortar grooves
- Cartoon/anime aesthetic
"""

from ursina import Shader


def create_toon_normal_shader(num_bands: int = 4, rim_intensity: float = 0.3,
                             outline_thickness: float = 1.0, outline_threshold: float = 0.4) -> Shader:
    """
    Create toon/cell shading shader with normal mapping support and comic book outlines.

    This shader quantizes lighting into discrete bands (like anime/cartoon shading)
    while using normal maps to calculate realistic surface orientation.
    Edge detection adds thick black outlines at brick boundaries for a comic book look.
    The result is dramatic 3D depth with a stylized, non-photorealistic look.

    Args:
        num_bands: Number of lighting steps (3 = minimal, 4 = standard, 5 = smooth)
                   Default 4 creates: deep shadow, shadow, mid-tone, highlight
        rim_intensity: Strength of rim lighting on edges (0.0 = off, 0.5 = strong)
                       Default 0.3 adds subtle edge highlights
        outline_thickness: Width of comic book outlines (0.5 = thin, 1.0 = standard, 2.0 = thick)
                          Default 1.0 provides balanced comic book look
        outline_threshold: Edge detection sensitivity (0.2 = busy, 0.4 = balanced, 0.6 = minimal)
                          Default 0.4 detects brick/mortar boundaries

    Returns:
        Ursina Shader object ready to apply to Entity

    Example:
        shader = create_toon_normal_shader(num_bands=4, rim_intensity=0.3,
                                          outline_thickness=1.0, outline_threshold=0.4)
        wall_entity.shader = shader

    Lighting Bands (num_bands=4):
        - Band 0: Deep shadow (0.0-0.25) - BLACK (mortar grooves)
        - Band 1: Shadow (0.25-0.5) - DARK GRAY (brick recesses)
        - Band 2: Mid-tone (0.5-0.75) - MEDIUM (brick faces)
        - Band 3: Highlight (0.75-1.0) - BRIGHT (brick edges)

    Comic Book Outlines:
        Uses Sobel edge detection on normal map to draw black outlines
        wherever brick edges meet mortar joints.
    """

    # Vertex shader - transforms normals and calculates world position
    vertex_shader = """
    #version 150

    // Input attributes
    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec2 p3d_MultiTexCoord0;
    in vec4 p3d_Tangent;  // For normal mapping TBN matrix

    // Output to fragment shader
    out vec2 texcoord;
    out vec3 world_normal;
    out vec3 world_pos;
    out vec3 view_dir;
    out mat3 TBN;  // Tangent-Bitangent-Normal matrix for normal mapping

    // Uniforms
    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;
    uniform mat3 p3d_NormalMatrix;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        texcoord = p3d_MultiTexCoord0;

        // Calculate world space position
        world_pos = (p3d_ModelMatrix * p3d_Vertex).xyz;

        // Transform normal to world space
        world_normal = normalize(p3d_NormalMatrix * p3d_Normal);

        // Calculate TBN matrix for normal mapping
        vec3 T = normalize(p3d_NormalMatrix * p3d_Tangent.xyz);
        vec3 N = world_normal;
        vec3 B = cross(N, T) * p3d_Tangent.w;  // Tangent.w encodes handedness
        TBN = mat3(T, B, N);

        // View direction for rim lighting (camera position assumed at origin)
        view_dir = normalize(-world_pos);
    }
    """

    # Fragment shader - toon shading with normal mapping
    fragment_shader = f"""
    #version 150

    // Input from vertex shader
    in vec2 texcoord;
    in vec3 world_normal;
    in vec3 world_pos;
    in vec3 view_dir;
    in mat3 TBN;

    // Output color
    out vec4 fragColor;

    // Textures
    uniform sampler2D p3d_Texture0;  // Base color texture
    uniform sampler2D p3d_Texture1;  // Normal map (if present)

    // Lighting parameters (hardcoded directional light for dungeon)
    const vec3 light_dir = normalize(vec3(0.5, 1.0, 0.3));  // Top-right lighting
    const vec3 light_color = vec3(1.0, 1.0, 1.0);
    const vec3 ambient_color = vec3(0.3, 0.3, 0.35);  // Slight blue ambient

    // Toon shading parameters
    const int num_bands = {num_bands};
    const float rim_intensity = {rim_intensity};

    // Comic book outline parameters
    const float outline_thickness = {outline_thickness};
    const float outline_threshold = {outline_threshold};
    const vec3 outline_color = vec3(0.0, 0.0, 0.0);  // Black outlines

    void main() {{
        // Sample base texture color
        vec4 base_color = texture(p3d_Texture0, texcoord);

        // Sample normal map and convert from [0,1] to [-1,1]
        vec3 normal_map = texture(p3d_Texture1, texcoord).rgb;
        normal_map = normalize(normal_map * 2.0 - 1.0);

        // Transform normal from tangent space to world space using TBN matrix
        vec3 normal = normalize(TBN * normal_map);

        // Calculate diffuse lighting (N dot L)
        float diffuse = max(0.0, dot(normal, light_dir));

        // TOON SHADING: Quantize diffuse into discrete bands
        float band_step = 1.0 / float(num_bands);
        float toon_diffuse = floor(diffuse / band_step) * band_step;

        // Make first band (deep shadow) extra dark for mortar grooves
        if (toon_diffuse < band_step) {{
            toon_diffuse *= 0.3;  // Deep black for mortar
        }}

        // Calculate final diffuse color
        vec3 diffuse_light = light_color * toon_diffuse;

        // RIM LIGHTING: Highlight edges facing away from camera
        float rim = 1.0 - max(0.0, dot(view_dir, normal));
        rim = pow(rim, 3.0);  // Sharpen the rim
        vec3 rim_light = vec3(rim) * rim_intensity;

        // Combine lighting
        vec3 final_light = ambient_color + diffuse_light + rim_light;

        // Apply lighting to base color
        vec3 final_color = base_color.rgb * final_light;

        // ===== COMIC BOOK OUTLINES (Sobel Edge Detection) =====
        // Calculate UV offset for sampling neighboring pixels
        // Assumes 1024x1024 texture; adjust if needed
        float texel_size = 1.0 / 1024.0;
        float offset = texel_size * outline_thickness;

        // Sample 9 neighboring normal map pixels in 3x3 grid
        // Layout:  NW  N  NE
        //          W   C  E
        //          SW  S  SE
        vec3 n_nw = texture(p3d_Texture1, texcoord + vec2(-offset,  offset)).rgb;
        vec3 n_n  = texture(p3d_Texture1, texcoord + vec2(0.0,      offset)).rgb;
        vec3 n_ne = texture(p3d_Texture1, texcoord + vec2( offset,  offset)).rgb;
        vec3 n_w  = texture(p3d_Texture1, texcoord + vec2(-offset,  0.0)).rgb;
        vec3 n_c  = texture(p3d_Texture1, texcoord).rgb;  // Center (already sampled above)
        vec3 n_e  = texture(p3d_Texture1, texcoord + vec2( offset,  0.0)).rgb;
        vec3 n_sw = texture(p3d_Texture1, texcoord + vec2(-offset, -offset)).rgb;
        vec3 n_s  = texture(p3d_Texture1, texcoord + vec2(0.0,     -offset)).rgb;
        vec3 n_se = texture(p3d_Texture1, texcoord + vec2( offset, -offset)).rgb;

        // Apply Sobel operator to detect edges in normal map
        // Horizontal kernel: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        vec3 sobel_h = -n_nw + n_ne - 2.0*n_w + 2.0*n_e - n_sw + n_se;

        // Vertical kernel: [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        vec3 sobel_v = -n_nw - 2.0*n_n - n_ne + n_sw + 2.0*n_s + n_se;

        // Calculate edge magnitude (gradient strength)
        // Use length of gradient vector for each RGB channel, then average
        float edge_strength = length(sobel_h) + length(sobel_v);
        edge_strength /= 2.0;  // Normalize

        // Apply threshold to create sharp outline
        float edge = smoothstep(outline_threshold - 0.05, outline_threshold + 0.05, edge_strength);

        // Mix between toon-shaded color and outline color
        final_color = mix(final_color, outline_color, edge);

        // Output with original alpha
        fragColor = vec4(final_color, base_color.a);
    }}
    """

    return Shader(
        vertex=vertex_shader,
        fragment=fragment_shader,
        name='toon_normal_mapping'
    )


__all__ = ['create_toon_normal_shader']
