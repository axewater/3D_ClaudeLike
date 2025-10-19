"""
Verlet integration physics system for blob creatures.

Implements soft-body physics using:
- Verlet integration (position-based velocity)
- Distance constraints (maintain parent-child connections)
- Iterative constraint solver
- Simple floor collision
"""

from ursina import Vec3
import math


class PhysicsParticle:
    """Single physics particle using Verlet integration."""

    def __init__(self, position, mass=1.0, radius=0.3):
        """
        Create a physics particle.

        Args:
            position: Vec3 initial position
            mass: Particle mass (affects gravity)
            radius: Collision radius (for floor collision)
        """
        self.position = Vec3(*position)
        self.old_position = Vec3(*position)
        self.mass = mass
        self.radius = radius
        self.pinned = False  # If True, particle doesn't move

    def integrate(self, dt, gravity, damping):
        """
        Integrate particle position using Verlet integration.

        Args:
            dt: Time step
            gravity: Vec3 gravity acceleration
            damping: Velocity damping factor (0.98 = 2% loss per frame)
        """
        if self.pinned:
            return

        # Calculate velocity from position difference (Verlet)
        velocity = (self.position - self.old_position) * damping

        # Store current position for next frame
        self.old_position = self.position

        # Update position: pos += vel + gravity * dt^2
        self.position += velocity + gravity * dt * dt

    def collide_floor(self, floor_y, restitution, friction):
        """
        Handle collision with floor plane.

        Args:
            floor_y: Y coordinate of floor
            restitution: Bounce factor (0-1, where 0.4 = 40% energy retained)
            friction: Horizontal friction multiplier (0.9 = 10% loss)
        """
        if self.pinned:
            return

        # Check if particle penetrates floor
        if self.position.y - self.radius < floor_y:
            # Move particle above floor
            self.position.y = floor_y + self.radius

            # Apply bounce (modify velocity by reflecting through floor)
            velocity = self.position - self.old_position
            if velocity.y < 0:  # Moving downward
                # Reflect Y velocity with energy loss
                self.old_position.y = self.position.y + velocity.y * restitution

                # Apply friction to horizontal motion
                self.old_position.x = self.position.x - velocity.x * friction
                self.old_position.z = self.position.z - velocity.z * friction


class DistanceConstraint:
    """Distance constraint between two particles."""

    def __init__(self, particle_a, particle_b, rest_length):
        """
        Create distance constraint.

        Args:
            particle_a: First PhysicsParticle
            particle_b: Second PhysicsParticle
            rest_length: Target distance to maintain
        """
        self.particle_a = particle_a
        self.particle_b = particle_b
        self.rest_length = rest_length

    def solve(self, stiffness):
        """
        Iteratively solve constraint by moving particles closer/farther.

        Args:
            stiffness: How much to correct (0-1, where 0.5 = move 50% toward target)
        """
        # Calculate current distance
        delta = self.particle_b.position - self.particle_a.position
        distance = delta.length()

        if distance < 0.001:  # Avoid division by zero
            return

        # Calculate correction amount
        direction = delta / distance
        diff = (distance - self.rest_length) / distance
        offset = direction * diff * stiffness

        # Move particles (distribute correction based on pinned state)
        if not self.particle_a.pinned and not self.particle_b.pinned:
            # Both free: split correction 50/50
            self.particle_a.position += offset * 0.5
            self.particle_b.position -= offset * 0.5
        elif not self.particle_a.pinned:
            # Only A free: A moves 100%
            self.particle_a.position += offset
        elif not self.particle_b.pinned:
            # Only B free: B moves 100%
            self.particle_b.position -= offset


class VerletPhysics:
    """Main Verlet physics engine."""

    def __init__(self, particles, constraints, gravity, damping, floor_y,
                 constraint_stiffness, constraint_iterations, floor_restitution=0.4,
                 floor_friction=0.9):
        """
        Create physics engine.

        Args:
            particles: List of PhysicsParticle objects
            constraints: List of DistanceConstraint objects
            gravity: Vec3 gravity acceleration
            damping: Velocity damping (0.98 = 2% loss)
            floor_y: Floor plane Y coordinate
            constraint_stiffness: How rigid constraints are (0-1)
            constraint_iterations: Solver passes per step (more = stiffer)
            floor_restitution: Bounce factor (0.4 = 40% energy)
            floor_friction: Horizontal friction (0.9 = 10% loss)
        """
        self.particles = particles
        self.constraints = constraints
        self.gravity = gravity
        self.damping = damping
        self.floor_y = floor_y
        self.constraint_stiffness = constraint_stiffness
        self.constraint_iterations = constraint_iterations
        self.floor_restitution = floor_restitution
        self.floor_friction = floor_friction

    def step(self, dt):
        """
        Advance physics simulation by one time step.

        Args:
            dt: Time step (usually 1/60 for 60Hz)
        """
        # 1. Integrate all particles (apply gravity, update positions)
        for particle in self.particles:
            particle.integrate(dt, self.gravity, self.damping)

        # 2. Solve constraints (multiple iterations for stability)
        for _ in range(self.constraint_iterations):
            for constraint in self.constraints:
                constraint.solve(self.constraint_stiffness)

        # 3. Handle collisions with floor
        for particle in self.particles:
            particle.collide_floor(self.floor_y, self.floor_restitution, self.floor_friction)
