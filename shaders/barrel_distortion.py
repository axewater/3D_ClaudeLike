"""
Barrel Distortion Post-Processing Shader

Applies a subtle fisheye/barrel distortion effect to the camera view.
This creates a more immersive first-person perspective by slightly
warping the edges of the screen, mimicking real camera lenses.

The effect uses polynomial UV coordinate distortion based on radial
distance from the screen center.
"""

from ursina import Shader


def create_barrel_distortion_shader(strength: float = 0.1) -> Shader:
    """
    Create a barrel distortion post-processing shader

    Args:
        strength: Distortion strength (0.0 = none, 0.1 = subtle, 0.3 = strong)
                 Recommended: 0.08-0.15 for natural FPS feel

    Returns:
        Ursina Shader object ready to apply to camera

    Usage:
        shader = create_barrel_distortion_shader(strength=0.1)
        camera.shader = shader
    """

    # GLSL Fragment Shader
    # This shader distorts UV coordinates based on distance from center
    fragment_shader = f"""
    #version 150

    uniform sampler2D p3d_Texture0;
    in vec2 texcoord;
    out vec4 fragColor;

    const float distortionStrength = {strength};

    void main() {{
        // Get texture coordinates centered at (0, 0)
        vec2 centered = texcoord - vec2(0.5, 0.5);

        // Calculate squared distance from center (0-1 range at corners)
        float r2 = dot(centered, centered);

        // Apply polynomial barrel distortion
        // Formula: distortedPos = pos * (1 + strength * r^2)
        // This creates outward warp at edges (barrel distortion)
        float distortionFactor = 1.0 + distortionStrength * r2;

        // Calculate distorted UV coordinates
        vec2 distorted = vec2(0.5, 0.5) + centered * distortionFactor;

        // Clamp to valid texture range (prevent sampling outside bounds)
        distorted = clamp(distorted, 0.0, 1.0);

        // Sample the rendered scene at distorted coordinates
        fragColor = texture(p3d_Texture0, distorted);
    }}
    """

    # Vertex Shader (passthrough - no modification needed)
    vertex_shader = """
    #version 150

    in vec4 p3d_Vertex;
    in vec2 p3d_MultiTexCoord0;

    out vec2 texcoord;

    uniform mat4 p3d_ModelViewProjectionMatrix;

    void main() {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        texcoord = p3d_MultiTexCoord0;
    }
    """

    # Create and return Ursina shader
    return Shader(
        vertex=vertex_shader,
        fragment=fragment_shader,
        name='barrel_distortion'
    )


__all__ = ['create_barrel_distortion_shader']
