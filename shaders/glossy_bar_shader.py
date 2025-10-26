"""
Glossy Bar Shader for UI Elements

Creates a professional glossy/reflective appearance for UI bars (HP, XP, etc.)
with a vertical gradient that has a bright highlight at the center and darkens
toward the top and bottom edges.

Features:
- Vertical gradient with center highlight
- Customizable base color
- Edge darkening for depth
- Smooth transitions using smoothstep
- Perfect for modern HUD designs
"""

from ursina import Shader


def create_glossy_bar_shader(highlight_intensity=1.5, edge_darkening=0.5, wave_enabled=True):
    """
    Create a glossy bar shader with vertical gradient, center highlight, and animated wave edges.

    Args:
        highlight_intensity: Brightness multiplier for center highlight (default 1.5)
                           Higher = brighter center, Lower = more subtle
        edge_darkening: Darkness factor for edges (0.0-1.0, default 0.5)
                       Higher = darker edges, Lower = more subtle
        wave_enabled: Enable animated wave distortion on edges (default True)

    Returns:
        Shader: Ursina shader object with glossy gradient effect

    Example:
        # Create shader
        shader = create_glossy_bar_shader(highlight_intensity=1.6, edge_darkening=0.6)

        # Apply to bar entity
        bar_fill.shader = shader
        bar_fill.color = color.rgb(0.3, 1.0, 0.3)  # Green

        # Update time uniform each frame for animation
        bar_fill.set_shader_input('time', time.time())
    """

    # Vertex shader - pass UV coordinates to fragment shader
    vertex_shader = '''
    #version 150

    uniform mat4 p3d_ModelViewProjectionMatrix;

    in vec4 p3d_Vertex;
    in vec2 p3d_MultiTexCoord0;
    in vec4 p3d_Color;

    out vec2 vUV;
    out vec4 vColor;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

        // Pass UV coordinates (for gradient calculation)
        vUV = p3d_MultiTexCoord0;

        // Pass vertex color (base color)
        vColor = p3d_Color;
    }
    '''

    # Fragment shader - create glossy gradient with animated wave edges
    wave_code = '''
        // Animated wave distortion on edges (slowed down 36x from original - ultra slow)
        float wave = sin(vUV.x * 8.0 + time * 0.0835) * 0.02;  // Ultra subtle, ultra slow wave
        float edgeWave = wave * smoothstep(0.4, 0.5, distFromCenter);  // Only affect edges
        brightness += edgeWave;
    ''' if wave_enabled else ''

    fragment_shader = f'''
    #version 150

    uniform vec4 p3d_ColorScale;
    uniform float time;  // Time uniform for animation

    in vec2 vUV;
    in vec4 vColor;

    out vec4 fragColor;

    // Shader parameters
    const float highlight_intensity = {highlight_intensity};
    const float edge_darkening = {edge_darkening};

    void main() {{
        // Get vertical position (0.0 at bottom, 1.0 at top)
        float yPos = vUV.y;

        // Create vertical gradient with highlight at center (0.5)
        // Distance from center: 0.0 at center, 0.5 at edges
        float distFromCenter = abs(yPos - 0.5);

        // Create highlight falloff (bright at center, dark at edges)
        // smoothstep creates smooth transition
        float highlightFactor = 1.0 - smoothstep(0.0, 0.5, distFromCenter);

        // Apply highlight intensity
        float brightness = 1.0 + (highlightFactor * (highlight_intensity - 1.0));

        // Apply edge darkening
        float edgeDarkness = 1.0 - (distFromCenter * 2.0 * edge_darkening);
        brightness *= edgeDarkness;

        {wave_code}

        // Apply base color with brightness modulation
        vec3 baseColor = vColor.rgb * p3d_ColorScale.rgb;
        vec3 finalColor = baseColor * brightness;

        // Preserve alpha
        float finalAlpha = vColor.a * p3d_ColorScale.a;

        // Output final glossy color
        fragColor = vec4(finalColor, finalAlpha);
    }}
    '''

    try:
        shader = Shader(
            vertex=vertex_shader,
            fragment=fragment_shader,
            name='glossy_bar_shader'
        )
        return shader
    except Exception as e:
        print(f"WARNING: Failed to create glossy bar shader: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_hp_bar_shader():
    """
    Preset: HP bar glossy shader with strong highlight and moderate darkening.
    Perfect for health bars that need to stand out.
    """
    return create_glossy_bar_shader(highlight_intensity=1.6, edge_darkening=0.6)


def create_xp_bar_shader():
    """
    Preset: XP bar glossy shader with subtle highlight and gentle darkening.
    Perfect for progress bars that should be less prominent.
    """
    return create_glossy_bar_shader(highlight_intensity=1.4, edge_darkening=0.5)


__all__ = [
    'create_glossy_bar_shader',
    'create_hp_bar_shader',
    'create_xp_bar_shader'
]
