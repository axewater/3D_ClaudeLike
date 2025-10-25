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
        self.max_lifetime = 1.0

        # Create custom "!" symbol from primitives (text scaling unreliable)
        # Container entity for animation
        self.entity = Entity(
            position=(0, 2.5, 0),  # Above enemy
            parent=enemy_entity
        )

        # Vertical bar (tall thin rectangle)
        self.bar = Entity(
            model='cube',
            color=ursina_color.rgb(1, 1, 0),  # Bright yellow
            scale=(0.175, 0.6, 0.175),  # Thin width/depth, tall height (50% of original)
            position=(0, 0.25, 0),  # Offset up from container (raised to avoid clipping)
            parent=self.entity,
            billboard=True,
            unlit=True  # Emissive glow
        )

        # Dot (small sphere at bottom)
        self.dot = Entity(
            model='sphere',
            color=ursina_color.rgb(1, 1, 0),  # Bright yellow
            scale=0.175,  # Match bar thickness (50% of original)
            position=(0, -0.3, 0),  # Below the bar
            parent=self.entity,
            billboard=True,
            unlit=True  # Emissive glow
        )

    def update(self, dt: float) -> bool:
        """Update alert"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Bounce animation with rumble effect
        bounce = abs(math.sin(self.lifetime * 8.0)) * 0.3

        # Add rumble/shake to x and z for dramatic effect
        rumble_intensity = 0.15
        rumble_x = random.uniform(-rumble_intensity, rumble_intensity)
        rumble_z = random.uniform(-rumble_intensity, rumble_intensity)

        self.entity.y = 2.5 + bounce
        self.entity.x = rumble_x
        self.entity.z = rumble_z

        return True

    def destroy(self):
        """Clean up all entities"""
        # Destroy child entities first
        if hasattr(self, 'bar') and self.bar:
            destroy(self.bar)
            self.bar = None
        if hasattr(self, 'dot') and self.dot:
            destroy(self.dot)
            self.dot = None
        # Destroy container
        if self.entity:
            destroy(self.entity)
            self.entity = None


class LevelTitleCard3D:
    """Large centered title card for level transitions"""

    def __init__(self, level_number: int):
        """
        Create level title card with dramatic effects

        Args:
            level_number: The level number to display
        """
        self.level_number = level_number
        self.lifetime = 0.0
        self.max_lifetime = 2.3  # 2-2.5 seconds

        # Create centered text entity in screen space
        self.entity = Text(
            text=f"Entering the Dungeon - Level {level_number}",
            position=(0, 0),  # Center of screen
            scale=2.5,  # Large text
            color=ursina_color.white,
            origin=(0, 0),  # Center origin
            billboard=False,  # Not billboard - this is screen-space UI
            parent=camera.ui  # Attach to camera UI for screen-space rendering
        )

        # Animation properties
        self.base_scale = 2.5
        self.color_phase = 0.0  # For color shifting

    def update(self, dt: float) -> bool:
        """
        Update title card animation

        Returns:
            False when animation is complete
        """
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Calculate animation progress (0.0 to 1.0)
        progress = self.lifetime / self.max_lifetime

        # Scale up effect: gradually grows larger
        scale_factor = 1.0 + (progress * 0.5)  # Grows to 150% of original size
        self.entity.scale = self.base_scale * scale_factor

        # Glow pulse effect: pulsing brightness
        pulse = math.sin(self.lifetime * 3.0) * 0.3 + 0.7  # Oscillates 0.4-1.0

        # Color shift: white → gold → transparent
        if progress < 0.3:
            # First 30%: Stay white with pulse
            r, g, b = 1.0, 1.0, 1.0
        elif progress < 0.6:
            # Middle 30%: Shift to gold
            shift = (progress - 0.3) / 0.3  # 0.0 to 1.0
            r = 1.0
            g = 1.0 - (shift * 0.15)  # 1.0 → 0.85
            b = 1.0 - (shift * 0.35)  # 1.0 → 0.65
        else:
            # Last 40%: Gold color maintained
            r, g, b = 1.0, 0.85, 0.65

        # Apply pulse to brightness
        r *= pulse
        g *= pulse
        b *= pulse

        # Fade out in last 40% of lifetime
        fade_start = self.max_lifetime * 0.6
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            alpha = 1.0 - fade_progress
        else:
            alpha = 1.0

        # Apply final color with alpha
        self.entity.color = ursina_color.rgba(r, g, b, alpha)

        return True

    def destroy(self):
        """Clean up"""
        if self.entity:
            destroy(self.entity)
            self.entity = None


class StairsGlowParticle3D(Particle3D):
    """Ethereal transparent particle for stairs glow effect"""

    def update(self, dt: float) -> bool:
        """Update with enhanced transparency"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply velocity (no gravity for stairs particles)
        self.entity.position += self.velocity * dt

        # Fade out with enhanced transparency (max 40% opacity)
        progress = self.lifetime / self.max_lifetime
        alpha = (1.0 - progress) * 0.4  # Scale down to 40% max opacity

        # Update color with alpha
        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True


class GlitterParticle3D(Particle3D):
    """Twinkling glitter particle for stairs sparkle effect with tornado spiral motion"""

    def __init__(self, position: Vec3, velocity: Vec3, color_rgb: tuple,
                 size: float = 0.035, lifetime: float = 2.0, center_pos: Vec3 = None):
        """
        Create a glitter particle with twinkling effect and tornado spiral

        Args:
            position: Starting 3D position
            velocity: Velocity vector (x, y, z)
            color_rgb: RGB color tuple (0-1 range)
            size: Particle size in world units
            lifetime: How long particle lasts (seconds)
            center_pos: Center position for orbital tornado rotation
        """
        super().__init__(position, velocity, color_rgb, size, lifetime,
                        particle_type="star", apply_gravity=False)

        # Twinkle properties (ULTRA FAST for sparkly effect)
        self.base_size = size
        self.twinkle_speed = random.uniform(20.0, 35.0)  # VERY fast twinkling
        self.twinkle_phase = random.uniform(0, 6.28)  # Random starting phase
        self.rotation_speed = random.uniform(120, 300)  # Faster self-rotation for sparkle

        # Tornado spiral orbital rotation properties
        self.center_pos = Vec3(center_pos) if center_pos else Vec3(position)
        self.orbital_speed = random.uniform(1.2, 2.5)  # Radians per second (tornado rotation)
        self.orbit_angle = random.uniform(0, 6.28)  # Starting angle in orbit

        # Calculate initial radius from center
        dx = position.x - self.center_pos.x
        dz = position.z - self.center_pos.z
        self.orbit_radius = math.sqrt(dx * dx + dz * dz)

    def update(self, dt: float) -> bool:
        """Update with twinkling, rotation, and tornado spiral effects"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply upward velocity (vertical motion)
        self.entity.position.y += self.velocity.y * dt

        # Apply tornado spiral orbital rotation around center point
        self.orbit_angle += self.orbital_speed * dt
        # Calculate new X and Z based on circular orbit (helix/tornado motion)
        self.entity.position.x = self.center_pos.x + math.cos(self.orbit_angle) * self.orbit_radius
        self.entity.position.z = self.center_pos.z + math.sin(self.orbit_angle) * self.orbit_radius
        # Update center Y position to follow upward motion
        self.center_pos.y += self.velocity.y * dt

        # Apply self-rotation for sparkle effect (particle spinning on own axis)
        self.entity.rotation_z += self.rotation_speed * dt

        # Ultra-sparkly twinkle effect: dramatic pulse size using sine wave
        self.twinkle_phase += dt * self.twinkle_speed
        twinkle = (math.sin(self.twinkle_phase) + 1.0) / 2.0  # 0.0 to 1.0
        size_multiplier = 0.25 + (twinkle * 0.3)  # Size varies 25%-55% (MUCH SMALLER!)

        # Fade out in last 30% of lifetime
        progress = self.lifetime / self.max_lifetime
        if progress > 0.7:
            fade_progress = (progress - 0.7) / 0.3
            alpha = (1.0 - fade_progress) * 0.9  # Fade from 90% to 0% (brighter for glow)
        else:
            alpha = 0.9  # Even brighter for ultra-glow visibility

        # Apply size and alpha
        self.entity.scale = self.base_size * size_multiplier
        self.entity.color = ursina_color.rgba(*self.color_rgb, alpha)

        return True


class StairsGlowEffect3D:
    """Ascending particle beam effect for dungeon exit stairs"""

    def __init__(self, grid_x: int, grid_y: int):
        """
        Create a continuous ascending particle beam effect for stairs

        Args:
            grid_x, grid_y: Grid position of the stairs
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.spawn_timer = 0.0
        self.spawn_interval = 0.12  # Spawn particles every 120ms (slower spawn rate)
        self.particles: List[StairsGlowParticle3D] = []

        # Glow colors (purple/bubble colors - mystical and ethereal)
        self.glow_colors = [
            (0.7, 0.5, 0.9),   # Soft purple
            (0.6, 0.4, 0.8),   # Deep purple
            (0.8, 0.6, 1.0),   # Light lavender
            (0.5, 0.7, 0.9),   # Purple-blue (bubble-like)
        ]

        # Second particle stream: glitter sparkles
        self.glitter_spawn_timer = 0.0
        self.glitter_spawn_interval = 0.25  # Spawn glitter every 250ms (less frequent)
        self.glitter_particles: List[GlitterParticle3D] = []

        # Ultra-bright glitter colors (0-255 RGB scale for maximum glow!)
        # Using ursina_color.rgb() which expects 0-255 integer values
        self.glitter_colors = [
            (255, 215, 0),    # Ultra-bright gold
            (255, 255, 255),  # Maximum white glow
            (255, 255, 200),  # Bright warm yellow glow
            (245, 245, 255),  # Bright silver shimmer
        ]

    def update(self, dt: float):
        """
        Update effect and spawn new particles

        Args:
            dt: Delta time since last update
        """
        # Update main particle stream (purple glow)
        self.spawn_timer += dt

        # Spawn new glow particles at regular intervals
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_particle()

        # Update existing glow particles
        for particle in self.particles[:]:
            if not particle.update(dt):
                particle.destroy()
                self.particles.remove(particle)

        # Update glitter particle stream (gold/white sparkles)
        self.glitter_spawn_timer += dt

        # Spawn new glitter particles at regular intervals
        if self.glitter_spawn_timer >= self.glitter_spawn_interval:
            self.glitter_spawn_timer = 0.0
            self._spawn_glitter_particle()

        # Update existing glitter particles
        for particle in self.glitter_particles[:]:
            if not particle.update(dt):
                particle.destroy()
                self.glitter_particles.remove(particle)

    def _spawn_particle(self):
        """Spawn a single ascending particle"""
        # Start position (on the stairs surface)
        base_pos = world_to_3d_position(self.grid_x, self.grid_y, 0.1)

        # Add random horizontal offset for column width
        offset_x = random.uniform(-0.25, 0.25)
        offset_z = random.uniform(-0.25, 0.25)
        pos = Vec3(base_pos[0] + offset_x, base_pos[1], base_pos[2] + offset_z)

        # Upward velocity with slight random sway (slower, more mysterious)
        velocity = Vec3(
            random.uniform(-0.08, 0.08),  # Gentle horizontal drift
            random.uniform(0.6, 0.9),     # Slow upward float
            random.uniform(-0.08, 0.08)   # Gentle horizontal drift
        )

        # Random color from glow palette
        color = random.choice(self.glow_colors)

        # Size and lifetime variations (smaller particles, longer life for slow rise)
        size = random.uniform(0.03, 0.06)
        lifetime = random.uniform(2.5, 3.5)

        # Create particle (no gravity, so it floats upward)
        particle = StairsGlowParticle3D(
            position=pos,
            velocity=velocity,
            color_rgb=color,
            size=size,
            lifetime=lifetime,
            particle_type="circle",
            apply_gravity=False  # No gravity - pure upward motion
        )

        self.particles.append(particle)

    def _spawn_glitter_particle(self):
        """Spawn a single twinkling glitter particle with tornado spiral motion"""
        # Start position (on the stairs surface, slightly higher for visibility)
        base_pos = world_to_3d_position(self.grid_x, self.grid_y, 0.15)
        # Center position for tornado spiral rotation
        center_pos = Vec3(base_pos[0], base_pos[1], base_pos[2])

        # Add random horizontal offset for sparkle spread (initial radius from center)
        offset_x = random.uniform(-0.3, 0.3)
        offset_z = random.uniform(-0.3, 0.3)
        pos = Vec3(base_pos[0] + offset_x, base_pos[1], base_pos[2] + offset_z)

        # Pure upward velocity (tornado orbital rotation handles horizontal motion)
        velocity = Vec3(
            0.0,                          # No horizontal drift - orbital rotation does this
            random.uniform(0.8, 1.2),     # Faster upward motion for dramatic rise
            0.0                           # No horizontal drift - orbital rotation does this
        )

        # Random ultra-bright color from glitter palette
        color = random.choice(self.glitter_colors)

        # Size and lifetime variations (smaller particles for delicate sparkle)
        size = random.uniform(0.02, 0.05)
        lifetime = random.uniform(1.5, 2.5)

        # Create glitter particle (with tornado spiral, twinkling, and ultra-glow)
        particle = GlitterParticle3D(
            position=pos,
            velocity=velocity,
            color_rgb=color,
            size=size,
            lifetime=lifetime,
            center_pos=center_pos  # Enable tornado spiral motion
        )

        self.glitter_particles.append(particle)

    def destroy(self):
        """Clean up all particles"""
        for particle in self.particles:
            particle.destroy()
        self.particles.clear()

        for particle in self.glitter_particles:
            particle.destroy()
        self.glitter_particles.clear()


class AnimationManager3D:
    """Manages all 3D animations and effects"""

    def __init__(self):
        """Initialize animation manager"""
        self.particles: List[Particle3D] = []
        self.directional_particles: List[DirectionalParticle3D] = []
        self.flash_effects: List[FlashEffect3D] = []
        self.trails: List[TrailEffect3D] = []
        self.ambient_particles: List[AmbientParticle3D] = []
        self.alert_particles: List[AlertParticle3D] = []
        self.stairs_glow_effects: List[StairsGlowEffect3D] = []
        self.screen_shake: Optional[ScreenShake3D] = None
        self.level_titles: List[LevelTitleCard3D] = []

    def add_flash_effect(self, grid_x: int, grid_y: int, color_rgb: tuple = None):
        """Add hit flash effect"""
        if color_rgb is None:
            color_rgb = (1, 1, 1)
        self.flash_effects.append(FlashEffect3D(grid_x, grid_y, color_rgb))

    def add_particle_burst(self, grid_x: int, grid_y: int, color_rgb: tuple,
                          count: int = 8, particle_type: str = "square"):
        """Create burst of particles"""
        pos = Vec3(*world_to_3d_position(grid_x, grid_y, 0.5))

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
        pos = Vec3(*world_to_3d_position(grid_x, grid_y, 0.5))

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
        pos = Vec3(*world_to_3d_position(grid_x, grid_y, 0.5))

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
        pos = Vec3(*world_to_3d_position(grid_x, grid_y, 0.5))

        # Different colors/patterns per enemy type
        if enemy_type == c.ENEMY_STARTLE:
            color = (0.4, 0.86, 0.31)
            count = int(20 * c.PARTICLE_DENSITY)
            particle_type = "circle"
        elif enemy_type == c.ENEMY_SKELETON:
            color = (0.86, 0.86, 0.86)
            count = int(25 * c.PARTICLE_DENSITY)
            particle_type = "square"
        elif enemy_type == c.ENEMY_DRAGON:
            color = (1.0, 0.59, 0.0)
            count = int(40 * c.PARTICLE_DENSITY)
            particle_type = "star"
        else:
            color = (0.8, 0.8, 0.8)
            count = int(15 * c.PARTICLE_DENSITY)
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
        self.add_particle_burst(grid_x, grid_y, heal_color, count=int(8 * c.PARTICLE_DENSITY), particle_type="star")

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

    def add_level_title(self, level_number: int):
        """Add level entry title card"""
        self.level_titles.append(LevelTitleCard3D(level_number))

    def add_stairs_glow_effect(self, grid_x: int, grid_y: int):
        """
        Add continuous ascending particle beam effect for stairs

        Args:
            grid_x, grid_y: Grid position of stairs tile
        """
        self.stairs_glow_effects.append(StairsGlowEffect3D(grid_x, grid_y))

    def clear_stairs_glow_effects(self):
        """Clear all stairs glow effects (called when switching levels)"""
        for effect in self.stairs_glow_effects:
            effect.destroy()
        self.stairs_glow_effects.clear()

    def update(self, dt: float):
        """Update all animations"""
        # Update and remove dead particles
        self.particles = [p for p in self.particles if p.update(dt) or not p.destroy()]
        self.directional_particles = [p for p in self.directional_particles if p.update(dt) or not p.destroy()]
        self.flash_effects = [f for f in self.flash_effects if f.update(dt) or not f.destroy()]
        self.trails = [t for t in self.trails if t.update(dt) or not t.destroy()]
        self.ambient_particles = [p for p in self.ambient_particles if p.update(dt) or not p.destroy()]
        self.alert_particles = [a for a in self.alert_particles if a.update(dt) or not a.destroy()]
        self.level_titles = [t for t in self.level_titles if t.update(dt) or not t.destroy()]

        # Update stairs glow effects (continuous, never removed)
        for effect in self.stairs_glow_effects:
            effect.update(dt)

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
        for f in self.flash_effects:
            f.destroy()
        for t in self.trails:
            t.destroy()
        for p in self.ambient_particles:
            p.destroy()
        for a in self.alert_particles:
            a.destroy()
        for t in self.level_titles:
            t.destroy()
        for e in self.stairs_glow_effects:
            e.destroy()

        # Clear lists
        self.particles.clear()
        self.directional_particles.clear()
        self.flash_effects.clear()
        self.trails.clear()
        self.ambient_particles.clear()
        self.alert_particles.clear()
        self.level_titles.clear()
        self.stairs_glow_effects.clear()
        self.screen_shake = None
