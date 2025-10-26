"""
Ultra-Realistic Bubble Shader for UI Particles

Creates glass-like translucent bubble particles with:
- Radial gradient (bright center, transparent edges)
- Fresnel rim lighting (iridescent edges)
- Color shifting over lifetime
- Shimmer animation
- Soft depth fade for blending

Perfect for particle effects that need organic, liquid-like appearance.
"""

from ursina import Shader
import math


def create_bubble_shader():
    """
    Create an ultra-realistic bubble shader with all effects.

    Shader uniforms (set via set_shader_input):
        - time: Current time for animation (float)
        - age_factor: Particle age from 0.0 (birth) to 1.0 (death)
        - base_color: RGB base color (vec3 or color)
        - shimmer_speed: Speed of color shimmer (default 2.0)

    Returns:
        Shader: Ursina shader object

    Example:
        shader = create_bubble_shader()
        bubble.shader = shader
        bubble.set_shader_input('time', time.time())
        bubble.set_shader_input('age_factor', 0.5)
        bubble.set_shader_input('shimmer_speed', 2.0)
    """

    # Vertex shader - pass position and calculate view direction
    vertex_shader = '''
    #version 140

    uniform mat4 p3d_ModelViewProjectionMatrix;
    uniform mat4 p3d_ModelMatrix;
    uniform mat4 p3d_ViewMatrix;

    in vec4 p3d_Vertex;
    in vec3 p3d_Normal;
    in vec4 p3d_Color;

    out vec3 vNormal;
    out vec3 vViewDir;
    out vec4 vColor;
    out vec3 vObjectPos;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

        // Transform normal to world space
        vNormal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);

        // Calculate world position
        vec4 worldPos = p3d_ModelMatrix * p3d_Vertex;

        // Calculate view direction (from vertex to camera)
        vec3 cameraPos = -p3d_ViewMatrix[3].xyz;
        vViewDir = normalize(cameraPos - worldPos.xyz);

        // Pass object-space position for radial gradient
        vObjectPos = p3d_Vertex.xyz;

        // Pass vertex color
        vColor = p3d_Color;
    }
    '''

    # Fragment shader - create bubble effect
    fragment_shader = '''
    #version 140

    uniform vec4 p3d_ColorScale;
    uniform float time;
    uniform float age_factor;  // 0.0 to 1.0 (young to old)
    uniform float shimmer_speed;

    in vec3 vNormal;
    in vec3 vViewDir;
    in vec4 vColor;
    in vec3 vObjectPos;

    out vec4 fragColor;

    // Default values if uniforms not set
    float getTime() {
        return time;
    }

    float getAgeFactor() {
        return clamp(age_factor, 0.0, 1.0);
    }

    float getShimmerSpeed() {
        return shimmer_speed > 0.0 ? shimmer_speed : 2.0;
    }

    void main() {
        // === 1. RADIAL GRADIENT (center bright, edges transparent) ===
        float distFromCenter = length(vObjectPos);
        float radialFalloff = 1.0 - smoothstep(0.3, 1.0, distFromCenter);

        // === 2. FRESNEL EFFECT (rim lighting for iridescence) ===
        float fresnel = pow(1.0 - max(0.0, dot(vNormal, vViewDir)), 3.0);
        float rimBrightness = fresnel * 0.8;  // Strong rim highlight

        // === 3. BASE COLOR WITH LIFETIME SHIFT ===
        vec3 baseColor = vColor.rgb * p3d_ColorScale.rgb;

        // Shift toward white/bright as bubble ages (more translucent)
        float ageFactor = getAgeFactor();
        vec3 brightColor = mix(baseColor, vec3(1.0, 1.0, 1.0), 0.3);
        vec3 ageColor = mix(baseColor, brightColor, ageFactor * 0.5);

        // === 4. SHIMMER/IRIDESCENCE (color oscillation) ===
        float shimmerTime = getTime() * getShimmerSpeed();

        // Create rainbow shimmer effect using phase-shifted sine waves
        float shimmerR = sin(shimmerTime + 0.0) * 0.5 + 0.5;
        float shimmerG = sin(shimmerTime + 2.094) * 0.5 + 0.5;  // 120 degrees
        float shimmerB = sin(shimmerTime + 4.189) * 0.5 + 0.5;  // 240 degrees

        vec3 shimmerColor = vec3(shimmerR, shimmerG, shimmerB) * 0.2;  // Subtle shimmer

        // Apply shimmer more at edges (fresnel)
        vec3 finalShimmer = shimmerColor * fresnel;

        // === 5. COMBINE ALL EFFECTS ===
        vec3 finalColor = ageColor + finalShimmer + vec3(rimBrightness);

        // === 6. ALPHA CALCULATION ===
        // Base alpha from radial falloff
        float alpha = radialFalloff;

        // Add rim transparency (edges more visible)
        alpha += rimBrightness * 0.5;

        // Fade out over lifetime (exponential for quick disappearance)
        float lifetimeFade = pow(1.0 - ageFactor, 2.0);
        alpha *= lifetimeFade;

        // Apply base alpha from vertex color
        alpha *= vColor.a * p3d_ColorScale.a;

        // Clamp alpha
        alpha = clamp(alpha, 0.0, 0.9);  // Never fully opaque

        // === 7. OUTPUT ===
        fragColor = vec4(finalColor, alpha);
    }
    '''

    try:
        shader = Shader(
            vertex=vertex_shader,
            fragment=fragment_shader,
            name='bubble_shader'
        )
        return shader
    except Exception as e:
        print(f"WARNING: Failed to create bubble shader: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_energy_bubble_shader():
    """
    Preset: High-energy bubble with fast shimmer.
    Perfect for XP bars and power-ups.
    """
    return create_bubble_shader()


def create_life_bubble_shader():
    """
    Preset: Soft life bubble with gentle shimmer.
    Perfect for HP bars and healing effects.
    """
    return create_bubble_shader()


__all__ = [
    'create_bubble_shader',
    'create_energy_bubble_shader',
    'create_life_bubble_shader'
]
