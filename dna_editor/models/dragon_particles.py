"""
Dragon particle effects - fire breath particles for attack animations.
"""

from ursina import Entity, Vec3, color, destroy


class FireParticle:
    """Single fire particle for dragon breath effect."""

    def __init__(self, position, velocity, lifetime, particle_color, parent, toon_shader=None):
        """
        Create a fire particle.

        Args:
            position: Vec3 starting position
            velocity: Vec3 velocity vector
            lifetime: Particle lifespan in seconds
            particle_color: RGB tuple (0-1) for particle color
            parent: Parent entity
            toon_shader: Optional toon shader
        """
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = velocity
        self.initial_color = particle_color

        # Create sphere entity
        particle_params = {
            'model': 'sphere',
            'color': color.rgb(*particle_color),
            'position': position,
            'scale': 0.15,  # Start small
            'parent': parent
        }

        if toon_shader is not None:
            particle_params['shader'] = toon_shader

        self.entity = Entity(**particle_params)
        self.base_scale = 0.15

    def update(self, dt):
        """
        Update particle position and appearance.

        Args:
            dt: Time delta in seconds

        Returns:
            True if particle is still alive, False if expired
        """
        self.age += dt

        # Check if expired
        if self.age >= self.lifetime:
            return False

        # Move particle
        self.entity.position += self.velocity * dt

        # Calculate fade/shrink factor (0 at start, 1 at end)
        fade_t = self.age / self.lifetime

        # Fade alpha (brightest at 0.3, then fade out)
        if fade_t < 0.3:
            # Brighten from 0.5 to 1.0
            alpha_factor = 0.5 + (fade_t / 0.3) * 0.5
        else:
            # Fade from 1.0 to 0
            alpha_factor = 1.0 - ((fade_t - 0.3) / 0.7)

        # Shrink over time (starts at 1.0, shrinks to 0.3)
        scale_factor = 1.0 - (fade_t * 0.7)
        self.entity.scale = self.base_scale * scale_factor

        # Color shift from yellow/orange to red to black
        if fade_t < 0.5:
            # Yellow/orange to red
            blend = fade_t / 0.5
            r = self.initial_color[0]
            g = self.initial_color[1] * (1.0 - blend * 0.5)
            b = self.initial_color[2] * (1.0 - blend)
        else:
            # Red to dark red/black
            blend = (fade_t - 0.5) / 0.5
            r = self.initial_color[0] * (1.0 - blend * 0.6)
            g = 0
            b = 0

        # Apply color with alpha
        self.entity.color = color.rgba(r * alpha_factor, g * alpha_factor, b * alpha_factor, alpha_factor)

        return True  # Still alive

    def destroy(self):
        """Cleanup particle entity."""
        destroy(self.entity)
