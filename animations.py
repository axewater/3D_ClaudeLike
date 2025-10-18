"""
Animation and visual effects system for Claude-Like
"""
import random
import math
from typing import List, Tuple
from PyQt6.QtGui import QColor
import constants as c


class FloatingText:
    """Floating damage/heal numbers that rise and fade"""
    def __init__(self, x: int, y: int, text: str, color: QColor, is_crit: bool = False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.is_crit = is_crit

        # Animation properties
        self.offset_y = 0.0
        self.lifetime = 0.0
        self.max_lifetime = 1.0 if not is_crit else 1.2  # Crits last longer
        self.alpha = 255

        # Random drift
        self.drift_x = random.uniform(-0.3, 0.3)

    def update(self, dt: float) -> bool:
        """Update animation. Returns False when animation is complete"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Rise up
        self.offset_y -= 1.5 * dt

        # Fade out in last 30% of lifetime
        fade_start = self.max_lifetime * 0.7
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            self.alpha = int(255 * (1.0 - fade_progress))

        return True


class FlashEffect:
    """Flash entity white/red when hit"""
    def __init__(self, x: int, y: int, color: QColor, duration: float = 0.15):
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.lifetime = 0.0
        self.alpha = 200

    def update(self, dt: float) -> bool:
        """Update animation. Returns False when complete"""
        self.lifetime += dt

        if self.lifetime >= self.duration:
            return False

        # Fade out
        progress = self.lifetime / self.duration
        self.alpha = int(200 * (1.0 - progress))

        return True


class Particle:
    """Generic particle for blood, sparks, explosions, etc."""
    def __init__(self, x: float, y: float, vx: float, vy: float, color: QColor,
                 size: float = 3.0, lifetime: float = 0.5, particle_type: str = "square",
                 apply_gravity: bool = True):
        self.x = x
        self.y = y
        self.vx = vx  # Velocity X
        self.vy = vy  # Velocity Y
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = 0.0
        self.alpha = 255
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
        self.alpha = int(255 * (1.0 - progress))

        return True


class DirectionalParticle(Particle):
    """Particle that sprays in a specific direction (for impacts)"""
    def __init__(self, x: float, y: float, direction_x: float, direction_y: float,
                 color: QColor, speed: float = 5.0, size: float = 4.0,
                 lifetime: float = 0.4, particle_type: str = "square"):
        # Calculate velocity from direction and speed
        vx = direction_x * speed
        vy = direction_y * speed
        super().__init__(x, y, vx, vy, color, size, lifetime, particle_type, apply_gravity=False)

        # Directional particles fade faster and slow down
        self.friction = 0.95

    def update(self, dt: float) -> bool:
        """Update with friction to slow down"""
        if not super().update(dt):
            return False

        # Apply friction
        self.vx *= self.friction
        self.vy *= self.friction

        return True


class TrailEffect:
    """Trail effect that follows moving entities or abilities"""
    def __init__(self, x: int, y: int, color: QColor, trail_type: str = "fade"):
        self.x = x
        self.y = y
        self.color = color
        self.trail_type = trail_type  # "fade", "sparkle", "smoke"
        self.lifetime = 0.0
        self.max_lifetime = 0.3
        self.alpha = 180
        self.size = 8.0

    def update(self, dt: float) -> bool:
        """Update trail. Returns False when dead"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Fade out and shrink
        progress = self.lifetime / self.max_lifetime
        self.alpha = int(180 * (1.0 - progress))
        self.size = 8.0 * (1.0 - progress * 0.5)

        return True


class AmbientParticle:
    """Subtle floating particles for atmosphere"""
    def __init__(self, x: float, y: float, color: QColor):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 0.0
        self.max_lifetime = random.uniform(3.0, 6.0)
        self.alpha = random.randint(30, 80)
        self.size = random.uniform(1.5, 3.0)

        # Slow drift
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, -0.1)  # Mostly upward

        # Gentle wave motion
        self.wave_offset = random.uniform(0, 6.28)
        self.wave_amplitude = random.uniform(0.1, 0.3)
        self.wave_speed = random.uniform(1.0, 2.0)

    def update(self, dt: float) -> bool:
        """Update ambient particle. Returns False when dead"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Apply drift
        self.x += self.vx * dt * 10
        self.y += self.vy * dt * 10

        # Add wave motion
        self.x += self.wave_amplitude * dt * 10 * random.uniform(-1, 1)

        # Gentle fade in/out
        progress = self.lifetime / self.max_lifetime
        if progress < 0.2:
            # Fade in
            fade_progress = progress / 0.2
            self.alpha = int(self.alpha * fade_progress)
        elif progress > 0.8:
            # Fade out
            fade_progress = (progress - 0.8) / 0.2
            self.alpha = int(self.alpha * (1.0 - fade_progress))

        return True


class FogParticle:
    """
    Atmospheric fog/smoke particles for unexplored areas and out-of-bounds.
    Creates mysterious, drifting atmosphere in the darkness.
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

        # Fog appearance - lighter gray/blue smoke for visibility on black
        # Add variation for visual interest
        gray_value = random.randint(70, 110)  # Much lighter than before
        blue_tint = random.randint(5, 20)  # Slight blue tint
        self.color = QColor(gray_value, gray_value, gray_value + blue_tint)

        self.size = random.uniform(40, 80)  # Larger, more billowy clouds
        self.base_alpha = random.randint(40, 80)  # More visible but still translucent
        self.alpha = self.base_alpha

        # Slow drifting motion
        self.vx = random.uniform(-8, 8)  # Slightly faster drift
        self.vy = random.uniform(-5, 5)  # Slight vertical drift

        # Pulsing/breathing effect
        self.pulse_time = random.uniform(0, 6.28)  # Random start phase
        self.pulse_speed = random.uniform(0.5, 1.2)  # Faster pulsing

        # Lifetime (fog persists longer than regular particles)
        self.lifetime = 0.0
        self.max_lifetime = random.uniform(10.0, 18.0)  # Even longer lifetime

    def update(self, dt: float) -> bool:
        """Update fog particle. Returns False when dead"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Drift slowly
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Pulsing alpha (breathing effect)
        self.pulse_time += dt
        pulse = 0.5 + 0.5 * math.sin(self.pulse_time * self.pulse_speed)
        self.alpha = int(self.base_alpha * pulse)

        # Fade out in last 20% of lifetime
        fade_start = self.max_lifetime * 0.8
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            self.alpha = int(self.alpha * (1.0 - fade_progress))

        return True


class ScreenShake:
    """Screen shake effect"""
    def __init__(self, intensity: float = 5.0, duration: float = 0.2):
        self.intensity = intensity
        self.duration = duration
        self.lifetime = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def update(self, dt: float) -> bool:
        """Update shake. Returns False when complete"""
        self.lifetime += dt

        if self.lifetime >= self.duration:
            self.offset_x = 0
            self.offset_y = 0
            return False

        # Diminishing shake
        progress = self.lifetime / self.duration
        current_intensity = self.intensity * (1.0 - progress)

        self.offset_x = random.randint(-int(current_intensity), int(current_intensity))
        self.offset_y = random.randint(-int(current_intensity), int(current_intensity))

        return True


class AlertParticle:
    """
    Alert indicator shown when enemy spots player.
    Shows "!" above enemy head with bounce animation.
    Follows the enemy as they move.
    """
    def __init__(self, enemy):
        self.enemy = enemy  # Reference to enemy to follow
        self.color = QColor(255, 220, 50)  # Bright yellow
        self.lifetime = 0.0
        self.max_lifetime = 0.5  # Display for 0.5 seconds
        self.bounce_offset = 0.0

    def update(self, dt: float) -> bool:
        """Update alert. Returns False when complete"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Bouncing animation using sine wave
        import math
        bounce_speed = 8.0  # Fast bounce
        self.bounce_offset = abs(math.sin(self.lifetime * bounce_speed)) * 0.3

        return True


class AnimationManager:
    """Manages all active animations and effects"""
    def __init__(self):
        self.floating_texts: List[FloatingText] = []
        self.flash_effects: List[FlashEffect] = []
        self.particles: List[Particle] = []
        self.directional_particles: List[DirectionalParticle] = []
        self.trails: List[TrailEffect] = []
        self.ambient_particles: List[AmbientParticle] = []
        self.fog_particles: List[FogParticle] = []
        self.alert_particles: List[AlertParticle] = []
        self.screen_shake: ScreenShake = None
        self.last_update_time = 0.0

    def add_floating_text(self, x: int, y: int, text: str, color: QColor, is_crit: bool = False):
        """Add floating damage/heal text"""
        self.floating_texts.append(FloatingText(x, y, text, color, is_crit))

    def add_flash_effect(self, x: int, y: int, color: QColor = None):
        """Add hit flash effect"""
        if color is None:
            color = QColor(255, 255, 255)
        self.flash_effects.append(FlashEffect(x, y, color))

    def add_particle_burst(self, x: int, y: int, color: QColor, count: int = 8,
                          particle_type: str = "square"):
        """Create burst of particles"""
        center_x = x * c.TILE_SIZE + c.TILE_SIZE / 2
        center_y = y * c.TILE_SIZE + c.TILE_SIZE / 2

        for _ in range(count):
            # Random direction
            angle = random.uniform(0, 3.14159 * 2)
            speed = random.uniform(2, 6)
            vx = speed * (angle % 3.14159) / 3.14159
            vy = speed * (angle / 3.14159) - speed

            lifetime = random.uniform(0.3, 0.7)
            size = random.uniform(2, 5)

            self.particles.append(
                Particle(center_x, center_y, vx, vy, color, size, lifetime, particle_type)
            )

    def add_blood_splatter(self, x: int, y: int):
        """Create blood splatter effect"""
        blood_color = QColor(180, 0, 0)
        self.add_particle_burst(x, y, blood_color, count=12, particle_type="circle")

    def add_heal_sparkles(self, x: int, y: int):
        """Create healing sparkle effect"""
        heal_color = QColor(100, 255, 100)
        self.add_particle_burst(x, y, heal_color, count=8, particle_type="star")

    def add_screen_shake(self, intensity: float = 5.0, duration: float = 0.2):
        """Add screen shake effect"""
        self.screen_shake = ScreenShake(intensity, duration)

    def add_directional_impact(self, x: int, y: int, from_x: int, from_y: int,
                               color: QColor, count: int = 10, is_crit: bool = False):
        """Create directional particle burst (sprays away from attacker)"""
        center_x = x * c.TILE_SIZE + c.TILE_SIZE / 2
        center_y = y * c.TILE_SIZE + c.TILE_SIZE / 2

        # Calculate direction (away from attacker)
        dx = x - from_x
        dy = y - from_y
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            dx /= length
            dy /= length
        else:
            dx, dy = 1, 0

        # Create particles spraying in direction
        for _ in range(count):
            # Add spread to direction
            spread = 0.6  # How much particles spread out
            angle_offset = random.uniform(-spread, spread)
            import math
            base_angle = math.atan2(dy, dx)
            final_angle = base_angle + angle_offset

            dir_x = math.cos(final_angle)
            dir_y = math.sin(final_angle)

            speed = random.uniform(4, 8) if not is_crit else random.uniform(6, 12)
            size = random.uniform(3, 6) if not is_crit else random.uniform(5, 9)

            self.directional_particles.append(
                DirectionalParticle(center_x, center_y, dir_x, dir_y, color,
                                  speed=speed, size=size, particle_type="circle")
            )

    def add_trail(self, x: int, y: int, color: QColor, trail_type: str = "fade"):
        """Add trail effect at position"""
        self.trails.append(TrailEffect(x, y, color, trail_type))

    def add_ability_trail(self, x: int, y: int, color: QColor, ability_type: str):
        """Add ability-specific trail effect"""
        center_x = x * c.TILE_SIZE + c.TILE_SIZE / 2
        center_y = y * c.TILE_SIZE + c.TILE_SIZE / 2

        if ability_type == "fireball":
            # Burning trail
            for _ in range(3):
                offset_x = random.uniform(-c.TILE_SIZE / 4, c.TILE_SIZE / 4)
                offset_y = random.uniform(-c.TILE_SIZE / 4, c.TILE_SIZE / 4)
                fire_color = QColor(255, random.randint(100, 200), 0)
                self.particles.append(
                    Particle(center_x + offset_x, center_y + offset_y,
                           random.uniform(-1, 1), random.uniform(-1, 1),
                           fire_color, size=random.uniform(4, 7),
                           lifetime=0.4, particle_type="circle", apply_gravity=False)
                )
        elif ability_type == "ice":
            # Ice crystals
            for _ in range(2):
                offset_x = random.uniform(-c.TILE_SIZE / 3, c.TILE_SIZE / 3)
                offset_y = random.uniform(-c.TILE_SIZE / 3, c.TILE_SIZE / 3)
                ice_color = QColor(150, 200, 255, 200)
                self.particles.append(
                    Particle(center_x + offset_x, center_y + offset_y,
                           0, random.uniform(0.5, 1.5),
                           ice_color, size=random.uniform(2, 4),
                           lifetime=0.5, particle_type="star", apply_gravity=False)
                )
        elif ability_type == "dash":
            # Speed lines
            self.trails.append(TrailEffect(x, y, color, "fade"))

    def add_ambient_particles(self, count: int = 1):
        """Add ambient atmospheric particles"""
        for _ in range(count):
            # Random position across the screen
            x = random.uniform(0, c.VIEWPORT_WIDTH * c.TILE_SIZE)
            y = random.uniform(0, c.VIEWPORT_HEIGHT * c.TILE_SIZE)

            # Subtle dust color
            dust_color = QColor(180, 180, 200)

            self.ambient_particles.append(AmbientParticle(x, y, dust_color))

    def add_fog_particles(self, count: int = 1):
        """
        Add fog particles for atmospheric effect in darkness.
        These create mysterious drifting smoke in unexplored/out-of-bounds areas.
        """
        for _ in range(count):
            # Spawn across entire viewport plus some margin for smooth entry
            x = random.uniform(-c.TILE_SIZE, c.VIEWPORT_WIDTH * c.TILE_SIZE + c.TILE_SIZE)
            y = random.uniform(-c.TILE_SIZE, c.VIEWPORT_HEIGHT * c.TILE_SIZE + c.TILE_SIZE)
            self.fog_particles.append(FogParticle(x, y))

    def add_alert_particle(self, enemy):
        """
        Add alert indicator above enemy when they spot the player.
        Shows "!" with bounce animation that follows the enemy.

        Args:
            enemy: Enemy entity reference (alert will follow this enemy)
        """
        self.alert_particles.append(AlertParticle(enemy))

    def add_death_burst(self, x: int, y: int, enemy_type: str):
        """Create dramatic death particle burst based on enemy type"""
        center_x = x * c.TILE_SIZE + c.TILE_SIZE / 2
        center_y = y * c.TILE_SIZE + c.TILE_SIZE / 2

        # Different colors/patterns per enemy type
        if enemy_type == c.ENEMY_GOBLIN:
            color = QColor(100, 220, 80)
            count = 20
            particle_type = "circle"
        elif enemy_type == c.ENEMY_SKELETON:
            color = QColor(220, 220, 220)
            count = 25
            particle_type = "square"
        elif enemy_type == c.ENEMY_DRAGON:
            color = QColor(255, 150, 0)
            count = 40  # More dramatic for boss
            particle_type = "star"
        else:
            color = QColor(200, 200, 200)
            count = 15
            particle_type = "circle"

        # Create burst
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(3, 9)
            import math
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)

            size = random.uniform(2, 6)
            lifetime = random.uniform(0.5, 1.0)

            self.particles.append(
                Particle(center_x, center_y, vx, vy, color,
                       size=size, lifetime=lifetime, particle_type=particle_type,
                       apply_gravity=True)
            )

    def update(self, dt: float):
        """Update all animations"""
        # Update floating texts
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

        # Update flash effects
        self.flash_effects = [fe for fe in self.flash_effects if fe.update(dt)]

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update directional particles
        self.directional_particles = [p for p in self.directional_particles if p.update(dt)]

        # Update trails
        self.trails = [t for t in self.trails if t.update(dt)]

        # Update ambient particles
        self.ambient_particles = [p for p in self.ambient_particles if p.update(dt)]

        # Update fog particles
        self.fog_particles = [p for p in self.fog_particles if p.update(dt)]

        # Update alert particles
        self.alert_particles = [a for a in self.alert_particles if a.update(dt)]

        # Update screen shake
        if self.screen_shake:
            if not self.screen_shake.update(dt):
                self.screen_shake = None

    def get_screen_offset(self) -> Tuple[int, int]:
        """Get current screen shake offset"""
        if self.screen_shake:
            return (self.screen_shake.offset_x, self.screen_shake.offset_y)
        return (0, 0)

    def clear_all(self):
        """Clear all active animations"""
        self.floating_texts.clear()
        self.flash_effects.clear()
        self.particles.clear()
        self.directional_particles.clear()
        self.trails.clear()
        self.ambient_particles.clear()
        self.fog_particles.clear()
        self.alert_particles.clear()
        self.screen_shake = None
