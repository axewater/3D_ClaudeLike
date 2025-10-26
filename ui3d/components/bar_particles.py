"""
Bar Particle Effects

Ultra-realistic bubble particles with shader effects for HP/XP bars.
"""

import time
import random
import math
from typing import Optional, List
from ursina import Entity, color
from shaders.bubble_shader import create_bubble_shader


# Module-level bubble shader (created once, reused for all bubbles)
BUBBLE_SHADER = create_bubble_shader()
if BUBBLE_SHADER:
    print("✓ Bubble shader loaded for HUD particles")


class BubbleParticle:
    """Ultra-realistic bubble particle with shader effects"""
    def __init__(self, start_pos: tuple, bar_color: tuple, parent: Entity):
        """
        Create a bubble particle with advanced visual effects

        Args:
            start_pos: (x, y) starting position in screen space
            bar_color: (r, g, b) color tuple
            parent: Parent entity for the bubble
        """
        self.lifetime = random.uniform(1.0, 2.0)  # Shorter lifetime - dissipate faster
        self.age = 0.0
        # ULTRA slow floating - 10% of previous speed, stays close to surface
        self.velocity_y = random.uniform(0.0002, 0.0004)  # 10% of previous - barely rises
        self.velocity_x = random.uniform(0.00008, 0.00018)  # 10% of previous - minimal outward drift

        # Smaller bubbles for surface effect
        self.base_size = random.uniform(0.004, 0.012)  # Smaller (was 0.005-0.020)

        # Pulsation parameters - gentle, slow breathing effect
        self.pulse_speed = random.uniform(0.5, 1.0)  # Ultra slow pulsation for gentle effect
        self.pulse_amplitude = random.uniform(0.10, 0.18)  # ±10-18% size variation (subtle)

        # Wave oscillation parameters (for side-to-side sway while drifting outward)
        self.wave_speed = random.uniform(1.0, 2.0)  # Oscillation frequency
        self.wave_amplitude = random.uniform(0.00003, 0.00008)  # 10% of previous - minimal sway

        # Color variation (±10% jitter on spawn)
        color_jitter = 0.1
        varied_color = (
            max(0.0, min(1.0, bar_color[0] + random.uniform(-color_jitter, color_jitter))),
            max(0.0, min(1.0, bar_color[1] + random.uniform(-color_jitter, color_jitter))),
            max(0.0, min(1.0, bar_color[2] + random.uniform(-color_jitter, color_jitter)))
        )

        # Store original color for calculations (avoid reading from modified entity color)
        self.original_color = varied_color

        # Create visual entity with SPHERE model
        self.entity = Entity(
            parent=parent,
            model='sphere',  # Circular! (was 'quad')
            color=color.rgba(*varied_color, 0.8),  # Higher initial alpha (was 0.6)
            position=(start_pos[0], start_pos[1], 2),  # In front of bar
            scale=(self.base_size, self.base_size),
            origin=(0, 0),
            eternal=True
        )

        # Apply cached bubble shader (reuse, don't create new)
        if BUBBLE_SHADER:
            self.entity.shader = BUBBLE_SHADER
            # Initialize shader uniforms
            self.entity.set_shader_input('time', time.time())
            self.entity.set_shader_input('age_factor', 0.0)
            self.entity.set_shader_input('shimmer_speed', random.uniform(1.5, 2.5))

    def update(self, dt: float) -> bool:
        """
        Update bubble particle with pulsation and advanced effects

        Args:
            dt: Delta time

        Returns:
            bool: True if particle is still alive, False if expired
        """
        self.age += dt

        # Check if particle is dead (early exit)
        if self.age >= self.lifetime:
            return False

        # Update position (slower movement with wave oscillation)
        self.entity.y += self.velocity_y * dt * 60  # Scale by 60 for frame-rate independence

        # Base rightward drift + wave oscillation for natural sway
        wave_offset = math.sin(self.age * self.wave_speed) * self.wave_amplitude * dt * 60
        self.entity.x += (self.velocity_x + wave_offset) * dt * 60

        # Calculate age factor (0.0 to 1.0) - clamp to prevent complex numbers
        age_factor = max(0.0, min(1.0, self.age / self.lifetime))

        # === PULSATING SIZE ANIMATION ===
        pulse = 1.0 + math.sin(self.age * self.pulse_speed) * self.pulse_amplitude

        # Grow slightly then shrink quickly (bubble pop effect)
        if age_factor < 0.3:
            # First 30% of life: grow slightly
            scale_factor = 1.0 + (age_factor / 0.3) * 0.2  # Grow to 120%
        else:
            # Last 70% of life: shrink rapidly
            fade_progress = (age_factor - 0.3) / 0.7
            scale_factor = 1.2 * max(0.0, 1.0 - fade_progress)  # Shrink from 120% to 0%

        # Combine pulsation with lifetime scaling
        final_size = max(0.001, self.base_size * scale_factor * pulse)  # Prevent zero/negative
        self.entity.scale = (final_size, final_size)

        # === QUICK FADE OUT (very fast dissipation - tomato soup effect) ===
        # Cubic fade for rapid disappearance (safe from complex numbers)
        alpha = 0.8 * pow(max(0.0, 1.0 - age_factor), 3.5)

        # === COLOR SHIFTING (toward brighter/white over lifetime) ===
        # Blend toward a lighter version of the color (use original color, not modified)
        base_r, base_g, base_b = self.original_color
        bright_factor = age_factor * 0.3  # Shift 30% toward white
        shifted_r = base_r + (1.0 - base_r) * bright_factor
        shifted_g = base_g + (1.0 - base_g) * bright_factor
        shifted_b = base_b + (1.0 - base_b) * bright_factor

        # Clamp values to valid range [0, 1]
        shifted_r = max(0.0, min(1.0, shifted_r))
        shifted_g = max(0.0, min(1.0, shifted_g))
        shifted_b = max(0.0, min(1.0, shifted_b))
        alpha = max(0.0, min(1.0, alpha))

        self.entity.color = color.rgba(shifted_r, shifted_g, shifted_b, alpha)

        # === UPDATE SHADER UNIFORMS ===
        if hasattr(self.entity, 'shader') and self.entity.shader:
            self.entity.set_shader_input('time', time.time())
            self.entity.set_shader_input('age_factor', age_factor)

        return True  # Particle is alive (we returned False early if dead)

    def cleanup(self):
        """Remove particle entity"""
        if self.entity:
            self.entity.disable()
            self.entity = None


class BarBubbleSystem:
    """Manages bubble particles for a single bar"""
    def __init__(self, parent: Entity, bar_color: tuple):
        """
        Initialize bubble system

        Args:
            parent: Parent entity for particles
            bar_color: (r, g, b) color for particles
        """
        self.parent = parent
        self.bar_color = bar_color
        self.particles: List[BubbleParticle] = []
        self.spawn_timer = 0.0
        self.spawn_rate = 0.1  # Spawn every 0.1 seconds (more frequent for surface bubbling)
        self.bubbles_per_spawn = (2, 4)  # Spawn 2-4 bubbles per event (more bubbles, stay near surface)
        self.enabled = True
        self.bar_end_pos = (0, 0)  # Will be updated each frame

    def set_bar_end_position(self, x: float, y: float):
        """Update the position where bubbles spawn (end of bar)"""
        self.bar_end_pos = (x, y)

    def set_color(self, bar_color: tuple):
        """Update bubble color (when bar color changes)"""
        self.bar_color = bar_color

    def update(self, dt: float):
        """Update all particles and spawn new ones"""
        if not self.enabled:
            return

        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Remove dead particles
        for p in [p for p in self.particles if p.age >= p.lifetime]:
            p.cleanup()

        # Spawn new particles (BURST spawning for bubble surface effect)
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0.0
            # Spawn 1-2 bubbles per event for gentle floating effect
            num_bubbles = random.randint(self.bubbles_per_spawn[0], self.bubbles_per_spawn[1])
            for _ in range(num_bubbles):
                # Focused spawn area at bar end
                spawn_x = self.bar_end_pos[0] + random.uniform(-0.003, 0.003)
                spawn_y = self.bar_end_pos[1] + random.uniform(-0.006, 0.006)
                particle = BubbleParticle((spawn_x, spawn_y), self.bar_color, self.parent)
                self.particles.append(particle)

        # Limit particle count (increased for more surface coverage)
        if len(self.particles) > 50:
            oldest = self.particles.pop(0)
            oldest.cleanup()

    def cleanup(self):
        """Clean up all particles"""
        for particle in self.particles:
            particle.cleanup()
        self.particles.clear()
