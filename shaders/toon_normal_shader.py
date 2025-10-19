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


def create_toon_normal_shader(num_bands: int = 4, rim_intensity: float = 0.3) -> Shader:
    """
    Create toon/cell shading shader with normal mapping support.

    This shader quantizes lighting into discrete bands (like anime/cartoon shading)
    while using normal maps to calculate realistic surface orientation.
    The result is dramatic 3D depth with a stylized, non-photorealistic look.

    Args:
        num_bands: Number of lighting steps (3 = minimal, 4 = standard, 5 = smooth)
                   Default 4 creates: deep shadow, shadow, mid-tone, highlight
        rim_intensity: Strength of rim lighting on edges (0.0 = off, 0.5 = strong)
                       Default 0.3 adds subtle edge highlights

    Returns:
        Ursina Shader object ready to apply to Entity

    Example:
        shader = create_toon_normal_shader(num_bands=4, rim_intensity=0.3)
        wall_entity.shader = shader

    Lighting Bands (num_bands=4):
        - Band 0: Deep shadow (0.0-0.25) - BLACK (mortar grooves)
        - Band 1: Shadow (0.25-0.5) - DARK GRAY (brick recesses)
        - Band 2: Mid-tone (0.5-0.75) - MEDIUM (brick faces)
        - Band 3: Highlight (0.75-1.0) - BRIGHT (brick edges)
    """

    # Vertex shader - transforms normals and calculates world position
    vertex_shader = """
    #version 140

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
    #version 140

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
