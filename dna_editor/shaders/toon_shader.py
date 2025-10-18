"""
Toon/Cel-shading shader for stylized 3D rendering.

Creates discrete lighting bands for a cartoon/anime aesthetic.
"""

from ursina import Shader


def create_toon_shader():
    """
    Create a toon shader with 4 discrete lighting bands.

    Uses a simplified approach with fixed directional lighting that works
    reliably across different Ursina/Panda3D versions.

    Returns:
        Shader: Ursina shader object with toon lighting
    """

    # Vertex shader - standard transformation using only guaranteed uniforms
    vertex_shader = '''
    #version 140

    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat3 p3d_NormalMatrix;

    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec4 p3d_Color;

    out vec3 vNormal;
    out vec4 vColor;

    void main() {
        // Transform vertex position
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

        // Transform normal to view space
        vNormal = normalize(p3d_NormalMatrix * p3d_Normal);

        // Pass vertex color
        vColor = p3d_Color;
    }
    '''

    # Fragment shader - simplified toon lighting with fixed light direction
    fragment_shader = '''
    #version 140

    uniform vec4 p3d_ColorScale;

    in vec3 vNormal;
    in vec4 vColor;

    out vec4 fragColor;

    void main() {
        vec3 normal = normalize(vNormal);
        vec3 baseColor = vColor.rgb * p3d_ColorScale.rgb;

        // Fixed key light direction in view space (from top-right-front)
        // In view space, camera looks down -Z, Y is up, X is right
        vec3 keyLightDir = normalize(vec3(0.5, 0.7, 0.5));
        float keyIntensity = max(dot(normal, keyLightDir), 0.0);

        // Fill light from left side
        vec3 fillLightDir = normalize(vec3(-0.4, 0.2, 0.3));
        float fillIntensity = max(dot(normal, fillLightDir), 0.0) * 0.5;

        // Rim light from back-top
        vec3 rimLightDir = normalize(vec3(-0.2, 0.5, -0.8));
        float rimIntensity = max(dot(normal, rimLightDir), 0.0) * 0.4;

        // Combine all lighting
        float totalIntensity = keyIntensity + fillIntensity + rimIntensity;

        // TOON SHADING: Quantize intensity into discrete bands
        // 4 lighting bands for clear cel-shading effect
        float toonIntensity;
        if (totalIntensity > 0.8) {
            toonIntensity = 1.0;      // Full bright (highlight)
        } else if (totalIntensity > 0.5) {
            toonIntensity = 0.7;      // Medium (lit area)
        } else if (totalIntensity > 0.25) {
            toonIntensity = 0.45;     // Dark (transition to shadow)
        } else {
            toonIntensity = 0.25;     // Shadow (darkest)
        }

        // Add ambient light (prevents pure black shadows)
        float ambient = 0.25;
        float finalIntensity = ambient + (toonIntensity * (1.0 - ambient));

        // Apply lighting to base color
        vec3 finalColor = baseColor * finalIntensity;

        // Output final color
        fragColor = vec4(finalColor, vColor.a * p3d_ColorScale.a);
    }
    '''

    try:
        shader = Shader(
            vertex=vertex_shader,
            fragment=fragment_shader,
            name='toon_shader'
        )
        return shader
    except Exception as e:
        print(f"WARNING: Failed to create toon shader: {e}")
        import traceback
        traceback.print_exc()
        return None
