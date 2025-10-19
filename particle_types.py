"""
Neutral particle data structures shared between 2D and 3D rendering
These use tuples for colors instead of PyQt6 QColor to avoid dependencies
"""
from typing import Tuple

# Type alias for RGB color tuples (values 0-1 for 3D compatibility)
ColorRGB = Tuple[float, float, float]


class Particle:
    """Generic particle for blood, sparks, explosions, etc.

    This is a neutral data structure that works with both 2D and 3D rendering.
    Color is stored as RGB tuple (0-1 range) instead of QColor.
    """
    def __init__(self, x: float, y: float, vx: float, vy: float, color: ColorRGB,
                 size: float = 3.0, lifetime: float = 0.5, particle_type: str = "square",
                 apply_gravity: bool = True):
        self.x = x
        self.y = y
        self.vx = vx  # Velocity X
        self.vy = vy  # Velocity Y
        self.color = color  # RGB tuple (0-1 range)
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = 0.0
        self.alpha = 1.0  # 0-1 range instead of 0-255
        self.particle_type = particle_type  # "square", "circle", "star"
        self.apply_gravity = apply_gravity

    def update(self, dt: float) -> bool:
        """Update particle physics. Returns False when dead"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply velocity
        self.x += self.vx * dt * 30
        self.y += self.vy * dt * 30

        # Apply gravity (for blood splatter)
        if self.apply_gravity:
            self.vy += 0.5 * dt * 30

        # Fade out
        progress = self.lifetime / self.max_lifetime
        self.alpha = 1.0 - progress

        return True
