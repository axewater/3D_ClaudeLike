"""
3D Animation and visual effects system for Claude-Like

This module provides 3D particle effects, floating text, and other visual effects
using Ursina Engine billboards and entities.
"""

import random
import math
from typing import List, Optional
from ursina import Entity, Vec3, color as ursina_color, Text, camera, destroy
from graphics3d.utils import world_to_3d_position, rgb_to_ursina_color
import constants as c


class Particle3D:
    """3D particle using billboard sprites"""

    def __init__(self, position: Vec3, velocity: Vec3, color_rgb: tuple,
                 size: float = 0.1, lifetime: float = 0.5,
                 particle_type: str = "square", apply_gravity: bool = True):
        """
        Create a 3D particle

        Args:
            position: Starting 3D position
            velocity: Velocity vector (x, y, z)
            color_rgb: RGB color tuple (0-1 range)
            size: Particle size in world units
            lifetime: How long particle lasts (seconds)
            particle_type: "square", "circle", or "star"
            apply_gravity: Whether to apply gravity
        """
        self.velocity = Vec3(velocity)
        self.color_rgb = color_rgb
        self.max_lifetime = lifetime
        self.lifetime = 0.0
        self.apply_gravity = apply_gravity

        # Create billboard entity (always faces camera)
        # Use different models based on particle type
        if particle_type == "circle":
            model = 'sphere'
        elif particle_type == "star":
            model = 'cube'  # Will rotate for star effect
        else:
            model = 'cube'

        self.entity = Entity(
            model=model,
            color=ursina_color.rgb(*color_rgb),
            scale=size,
            position=position,
            billboard=True,  # Always face camera
            unlit=True  # Emissive, not affected by lighting
        )

        # Store original scale for star rotation
        self.base_scale = size
        if particle_type == "star":
            self.entity.rotation_z = random.uniform(0, 360)

    def update(self, dt: float) -> bool:
        """
        Update particle physics

        Returns:
            False when particle should be destroyed
        """
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply velocity
        self.entity.position += self.velocity * dt

        # Apply gravity
        if self.apply_gravity:
            self.velocity.y -= 9.8 * dt  # Gravity constant

        # Fade out
        progress = self.lifetime / self.max_lifetime
        alpha = 1.0 - progress

        # Update color with alpha
        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True

    def destroy(self):
        """Clean up the entity"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class DirectionalParticle3D(Particle3D):
    """Particle that sprays in a specific direction with friction"""

    def __init__(self, position: Vec3, direction: Vec3, color_rgb: tuple,
                 speed: float = 5.0, size: float = 0.1,
                 lifetime: float = 0.4, particle_type: str = "square"):
        """
        Create a directional spray particle

        Args:
            position: Starting position
            direction: Direction vector (normalized)
            color_rgb: RGB color tuple
            speed: Initial speed
            size: Particle size
            lifetime: How long particle lasts
            particle_type: Visual style
        """
        # Calculate velocity from direction and speed
        velocity = direction.normalized() * speed

        super().__init__(position, velocity, color_rgb, size, lifetime,
                        particle_type, apply_gravity=False)

        # Directional particles have friction
        self.friction = 0.95

    def update(self, dt: float) -> bool:
        """Update with friction"""
        if not super().update(dt):
            return False

        # Apply friction to slow down
        self.velocity *= self.friction

        return True


class FloatingText3D:
    """Billboard text that floats upward and fades"""

    def __init__(self, grid_x: int, grid_y: int, text: str, color_rgb: tuple,
                 is_crit: bool = False):
        """
        Create floating damage/heal text

        Args:
            grid_x, grid_y: Grid position
            text: Text to display
            color_rgb: RGB color tuple
            is_crit: If true, text is larger and lasts longer
        """
        self.text = text
        self.color_rgb = color_rgb
        self.is_crit = is_crit

        # Position slightly above the grid position
        pos = world_to_3d_position(grid_x, grid_y, 1.0)

        # Create billboard text
        scale = 2.0 if is_crit else 1.0
        self.entity = Text(
            text=text,
            position=pos,
            scale=scale,
            color=ursina_color.rgb(*color_rgb),
            billboard=True,
            origin=(0, 0)
        )

        # Animation properties
        self.lifetime = 0.0
        self.max_lifetime = 1.2 if is_crit else 1.0
        self.rise_speed = 1.0 if is_crit else 1.5
        self.drift_x = random.uniform(-0.3, 0.3)

    def update(self, dt: float) -> bool:
        """Update animation"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Rise up
        self.entity.y += self.rise_speed * dt
        self.entity.x += self.drift_x * dt

        # Fade out in last 30% of lifetime
        fade_start = self.max_lifetime * 0.7
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            alpha = 1.0 - fade_progress
            self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class FlashEffect3D:
    """Entity flash/glow effect (overlay on entity)"""

    def __init__(self, grid_x: int, grid_y: int, color_rgb: tuple,
                 duration: float = 0.15):
        """
        Create a flash effect

        Args:
            grid_x, grid_y: Grid position
            color_rgb: Flash color
            duration: How long flash lasts
        """
        self.color_rgb = color_rgb
        self.duration = duration
        self.lifetime = 0.0

        # Create a glowing overlay cube
        pos = world_to_3d_position(grid_x, grid_y, 0.5)
        self.entity = Entity(
            model='cube',
            color=ursina_color.rgb(*color_rgb),
            scale=(0.8, 0.8, 0.8),
            position=pos,
            unlit=True,
            alpha=0.8
        )

    def update(self, dt: float) -> bool:
        """Update flash"""
        self.lifetime += dt

        if self.lifetime >= self.duration:
            return False

        # Fade out
        progress = self.lifetime / self.duration
        alpha = 0.8 * (1.0 - progress)
        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class TrailEffect3D:
    """Trail effect that follows abilities/projectiles"""

    def __init__(self, grid_x: int, grid_y: int, color_rgb: tuple,
                 trail_type: str = "fade"):
        """
        Create a trail effect

        Args:
            grid_x, grid_y: Grid position
            color_rgb: Trail color
            trail_type: "fade", "sparkle", or "smoke"
        """
        self.color_rgb = color_rgb
        self.trail_type = trail_type
        self.lifetime = 0.0
        self.max_lifetime = 0.3

        # Create billboard sprite
        pos = world_to_3d_position(grid_x, grid_y, 0.5)

        # Trail size based on type
        if trail_type == "smoke":
            size = 0.4
        elif trail_type == "sparkle":
            size = 0.2
        else:
            size = 0.3

        self.entity = Entity(
            model='cube',
            color=ursina_color.rgb(*color_rgb),
            scale=size,
            position=pos,
            billboard=True,
            unlit=True
        )

        self.base_size = size

    def update(self, dt: float) -> bool:
        """Update trail"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Fade out and shrink
        progress = self.lifetime / self.max_lifetime
        alpha = 1.0 - progress
        size = self.base_size * (1.0 - progress * 0.5)

        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)
        self.entity.scale = size

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class AmbientParticle3D:
    """Atmospheric floating particle"""

    def __init__(self, world_x: float, world_y: float, world_z: float, color_rgb: tuple):
        """
        Create ambient particle

        Args:
            world_x, world_y, world_z: World position
            color_rgb: Particle color
        """
        self.color_rgb = color_rgb
        self.lifetime = 0.0
        self.max_lifetime = random.uniform(3.0, 6.0)

        # Create billboard particle
        size = random.uniform(0.05, 0.15)
        alpha = random.uniform(0.3, 0.6)

        self.entity = Entity(
            model='sphere',
            color=ursina_color.rgba(*color_rgb, alpha),
            scale=size,
            position=(world_x, world_y, world_z),
            billboard=True,
            unlit=True
        )

        # Drift motion
        self.velocity = Vec3(
            random.uniform(-0.3, 0.3),
            random.uniform(-0.1, 0.5),  # Mostly upward
            random.uniform(-0.3, 0.3)
        )

        # Wave motion
        self.wave_offset = random.uniform(0, 6.28)
        self.wave_amplitude = random.uniform(0.1, 0.3)
        self.wave_speed = random.uniform(1.0, 2.0)
        self.base_alpha = alpha

    def update(self, dt: float) -> bool:
        """Update ambient particle"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply drift
        self.entity.position += self.velocity * dt

        # Add wave motion
        self.wave_offset += dt * self.wave_speed
        wave = math.sin(self.wave_offset) * self.wave_amplitude
        self.entity.x += wave * dt

        # Gentle fade in/out
        progress = self.lifetime / self.max_lifetime
        if progress < 0.2:
            # Fade in
            alpha = self.base_alpha * (progress / 0.2)
        elif progress > 0.8:
            # Fade out
            alpha = self.base_alpha * ((1.0 - progress) / 0.2)
        else:
            alpha = self.base_alpha

        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class ScreenShake3D:
    """Camera shake effect for 3D"""

    def __init__(self, intensity: float = 5.0, duration: float = 0.2):
        """
        Create screen shake

        Args:
            intensity: Shake magnitude
            duration: How long to shake
        """
        self.intensity = intensity
        self.duration = duration
        self.lifetime = 0.0
        self.offset = Vec3(0, 0, 0)

    def update(self, dt: float) -> bool:
        """Update shake"""
        self.lifetime += dt

        if self.lifetime >= self.duration:
            self.offset = Vec3(0, 0, 0)
            return False

        # Diminishing shake
        progress = self.lifetime / self.duration
        current_intensity = self.intensity * (1.0 - progress)

        # Random offset
        self.offset = Vec3(
            random.uniform(-current_intensity, current_intensity) * 0.1,
            random.uniform(-current_intensity, current_intensity) * 0.1,
            random.uniform(-current_intensity, current_intensity) * 0.1
        )

        return True

    def get_offset(self) -> Vec3:
        """Get current shake offset"""
        return self.offset


class AlertParticle3D:
    """Alert indicator above enemy (billboard "!")"""

    def __init__(self, enemy_entity: Entity):
        """
        Create alert particle

        Args:
            enemy_entity: Enemy model entity to follow
        """
        self.enemy_entity = enemy_entity
        self.lifetime = 0.0
        self.max_lifetime = 0.5

        # Create "!" text billboard
        self.entity = Text(
            text="!",
            position=(0, 1.5, 0),  # Above enemy
            scale=2.0,
            color=ursina_color.rgb(1, 0.86, 0.2),  # Yellow
            billboard=True,
            parent=enemy_entity  # Attach to enemy
        )

    def update(self, dt: float) -> bool:
        """Update alert"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Bounce animation
        bounce = abs(math.sin(self.lifetime * 8.0)) * 0.3
        self.entity.y = 1.5 + bounce

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class AnimationManager3D:
    """Manages all 3D animations and effects"""

    def __init__(self):
        """Initialize animation manager"""
        self.particles: List[Particle3D] = []
        self.directional_particles: List[DirectionalParticle3D] = []
        self.floating_texts: List[FloatingText3D] = []
        self.flash_effects: List[FlashEffect3D] = []
        self.trails: List[TrailEffect3D] = []
        self.ambient_particles: List[AmbientParticle3D] = []
        self.alert_particles: List[AlertParticle3D] = []
        self.screen_shake: Optional[ScreenShake3D] = None

    def add_floating_text(self, grid_x: int, grid_y: int, text: str,
                         color_rgb: tuple, is_crit: bool = False):
        """Add floating damage/heal text"""
        self.floating_texts.append(FloatingText3D(grid_x, grid_y, text, color_rgb, is_crit))

    def add_flash_effect(self, grid_x: int, grid_y: int, color_rgb: tuple = None):
        """Add hit flash effect"""
        if color_rgb is None:
            color_rgb = (1, 1, 1)
        self.flash_effects.append(FlashEffect3D(grid_x, grid_y, color_rgb))

    def add_particle_burst(self, grid_x: int, grid_y: int, color_rgb: tuple,
                          count: int = 8, particle_type: str = "square"):
        """Create burst of particles"""
        pos = world_to_3d_position(grid_x, grid_y, 0.5)

        for _ in range(count):
            # Random direction
            angle = random.uniform(0, math.pi * 2)
            elevation = random.uniform(-0.5, 0.5)

            direction = Vec3(
                math.cos(angle),
                elevation,
                math.sin(angle)
            )

            speed = random.uniform(2, 6)
            velocity = direction * speed

            size = random.uniform(0.05, 0.15)
            lifetime = random.uniform(0.3, 0.7)

            particle = Particle3D(pos, velocity, color_rgb, size, lifetime, particle_type)
            self.particles.append(particle)

    def add_directional_impact(self, grid_x: int, grid_y: int, from_x: int, from_y: int,
                              color_rgb: tuple, count: int = 10, is_crit: bool = False):
        """Create directional particle spray (away from attacker)"""
        pos = world_to_3d_position(grid_x, grid_y, 0.5)

        # Calculate direction (away from attacker)
        dx = grid_x - from_x
        dy = grid_y - from_y
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            dx /= length
            dy /= length
        else:
            dx, dy = 1, 0

        # Create spray particles
        for _ in range(count):
            # Add spread to direction
            spread = 0.6
            angle_offset = random.uniform(-spread, spread)
            base_angle = math.atan2(dy, dx)
            final_angle = base_angle + angle_offset

            direction = Vec3(
                math.cos(final_angle),
                random.uniform(-0.2, 0.5),  # Some upward motion
                math.sin(final_angle)
            )

            speed = random.uniform(6, 12) if is_crit else random.uniform(4, 8)
            size = random.uniform(0.1, 0.2) if is_crit else random.uniform(0.05, 0.15)

            particle = DirectionalParticle3D(
                pos, direction, color_rgb,
                speed=speed, size=size,
                particle_type="circle"
            )
            self.directional_particles.append(particle)

    def add_ability_trail(self, grid_x: int, grid_y: int, color_rgb: tuple,
                         ability_type: str):
        """Add ability-specific trail effect"""
        pos = world_to_3d_position(grid_x, grid_y, 0.5)

        if ability_type == "fireball":
            # Fire particles
            for _ in range(3):
                offset = Vec3(
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3)
                )
                fire_color = (1.0, random.uniform(0.4, 0.8), 0.0)
                particle = Particle3D(
                    pos + offset,
                    Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)),
                    fire_color,
                    size=random.uniform(0.1, 0.2),
                    lifetime=0.4,
                    particle_type="circle",
                    apply_gravity=False
                )
                self.particles.append(particle)

        elif ability_type == "ice":
            # Ice crystals
            for _ in range(2):
                offset = Vec3(
                    random.uniform(-0.4, 0.4),
                    random.uniform(-0.4, 0.4),
                    random.uniform(-0.4, 0.4)
                )
                ice_color = (0.6, 0.8, 1.0)
                particle = Particle3D(
                    pos + offset,
                    Vec3(0, random.uniform(0.5, 1.5), 0),
                    ice_color,
                    size=random.uniform(0.08, 0.12),
                    lifetime=0.5,
                    particle_type="star",
                    apply_gravity=False
                )
                self.particles.append(particle)

        elif ability_type == "dash":
            # Speed lines trail
            self.trails.append(TrailEffect3D(grid_x, grid_y, color_rgb, "fade"))

    def add_death_burst(self, grid_x: int, grid_y: int, enemy_type: str):
        """Create dramatic death particle burst"""
        pos = world_to_3d_position(grid_x, grid_y, 0.5)

        # Different colors/patterns per enemy type
        if enemy_type == c.ENEMY_STARTLE:
            color = (0.4, 0.86, 0.31)
            count = 20
            particle_type = "circle"
        elif enemy_type == c.ENEMY_SKELETON:
            color = (0.86, 0.86, 0.86)
            count = 25
            particle_type = "square"
        elif enemy_type == c.ENEMY_DRAGON:
            color = (1.0, 0.59, 0.0)
            count = 40
            particle_type = "star"
        else:
            color = (0.8, 0.8, 0.8)
            count = 15
            particle_type = "circle"

        # Create burst
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            elevation = random.uniform(-0.5, 1.0)
            speed = random.uniform(3, 9)

            direction = Vec3(
                math.cos(angle),
                elevation,
                math.sin(angle)
            )

            velocity = direction * speed
            size = random.uniform(0.05, 0.15)
            lifetime = random.uniform(0.5, 1.0)

            particle = Particle3D(pos, velocity, color, size, lifetime,
                                particle_type, apply_gravity=True)
            self.particles.append(particle)

    def add_heal_sparkles(self, grid_x: int, grid_y: int):
        """Create healing sparkle effect"""
        heal_color = (0.4, 1.0, 0.4)
        self.add_particle_burst(grid_x, grid_y, heal_color, count=8, particle_type="star")

    def add_screen_shake(self, intensity: float = 5.0, duration: float = 0.2):
        """Add screen shake effect"""
        self.screen_shake = ScreenShake3D(intensity, duration)

    def add_alert_particle(self, enemy_entity: Entity):
        """Add alert indicator above enemy"""
        self.alert_particles.append(AlertParticle3D(enemy_entity))

    def add_ambient_particles(self, count: int = 1):
        """Add ambient atmospheric particles"""
        for _ in range(count):
            # Spawn in random world position
            world_x = random.uniform(0, c.GRID_WIDTH)
            world_z = random.uniform(0, c.GRID_HEIGHT)
            world_y = random.uniform(0.5, 3.0)

            dust_color = (0.7, 0.7, 0.78)
            self.ambient_particles.append(
                AmbientParticle3D(world_x, world_y, world_z, dust_color)
            )

    def update(self, dt: float):
        """Update all animations"""
        # Update and remove dead particles
        self.particles = [p for p in self.particles if p.update(dt) or not p.destroy()]
        self.directional_particles = [p for p in self.directional_particles if p.update(dt) or not p.destroy()]
        self.floating_texts = [t for t in self.floating_texts if t.update(dt) or not t.destroy()]
        self.flash_effects = [f for f in self.flash_effects if f.update(dt) or not f.destroy()]
        self.trails = [t for t in self.trails if t.update(dt) or not t.destroy()]
        self.ambient_particles = [p for p in self.ambient_particles if p.update(dt) or not p.destroy()]
        self.alert_particles = [a for a in self.alert_particles if a.update(dt) or not a.destroy()]

        # Enforce particle count limit for performance
        total_particles = len(self.particles) + len(self.directional_particles)
        if total_particles > c.MAX_PARTICLES:
            # Remove oldest particles first (from the front of the list)
            excess = total_particles - c.MAX_PARTICLES

            if excess <= len(self.particles):
                # Remove from regular particles
                for p in self.particles[:excess]:
                    p.destroy()
                self.particles = self.particles[excess:]
            else:
                # Remove all regular particles, then from directional
                for p in self.particles:
                    p.destroy()
                self.particles.clear()

                remaining_excess = excess - len(self.particles)
                for p in self.directional_particles[:remaining_excess]:
                    p.destroy()
                self.directional_particles = self.directional_particles[remaining_excess:]

        # Update screen shake
        if self.screen_shake:
            if not self.screen_shake.update(dt):
                self.screen_shake = None

    def get_screen_shake_offset(self) -> Vec3:
        """Get current screen shake offset"""
        if self.screen_shake:
            return self.screen_shake.get_offset()
        return Vec3(0, 0, 0)

    def clear_all(self):
        """Clear all active animations"""
        # Destroy all entities
        for p in self.particles:
            p.destroy()
        for p in self.directional_particles:
            p.destroy()
        for t in self.floating_texts:
            t.destroy()
        for f in self.flash_effects:
            f.destroy()
        for t in self.trails:
            t.destroy()
        for p in self.ambient_particles:
            p.destroy()
        for a in self.alert_particles:
            a.destroy()

        # Clear lists
        self.particles.clear()
        self.directional_particles.clear()
        self.floating_texts.clear()
        self.flash_effects.clear()
        self.trails.clear()
        self.ambient_particles.clear()
        self.alert_particles.clear()
        self.screen_shake = None
