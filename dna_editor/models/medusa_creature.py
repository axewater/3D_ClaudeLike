"""
MedusaCreature model - creature with central body and tentacles with eyes on tips.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .tentacle import Tentacle
from .eye import Eye
from ..core.constants import GOLDEN_ANGLE
from ..shaders import create_toon_shader


class MedusaCreature:
    """Medusa creature with eyes on tentacle tips instead of body."""

    def __init__(self, num_tentacles=8, segments_per_tentacle=16, algorithm='fourier',
                 algorithm_params=None, thickness_base=0.25, taper_factor=0.6,
                 body_scale=1.0, tentacle_color=(0.4, 0.2, 0.6),
                 hue_shift=0.08, anim_speed=1.5, wave_amplitude=0.08, pulse_speed=1.2, pulse_amount=0.06,
                 eye_size=0.18, eyeball_color=(1.0, 0.95, 0.85), pupil_color=(0.1, 0.0, 0.2)):
        """
        Create a Medusa creature with eyes on tentacle tips.

        Args:
            num_tentacles: Number of tentacles (4-12)
            segments_per_tentacle: Segments per tentacle (12-20 for long flowing tentacles)
            algorithm: 'bezier' or 'fourier' (fourier recommended for organic look)
            algorithm_params: Dict of algorithm parameters
            thickness_base: Base thickness of tentacles
            taper_factor: Taper factor for tentacles (0.7-0.9 for gradual taper)
            body_scale: Body sphere scale
            tentacle_color: Base tentacle color (RGB tuple 0-1)
            hue_shift: Color variation between tentacles
            anim_speed: Animation wave speed
            wave_amplitude: Wave motion intensity
            pulse_speed: Body pulse breathing speed
            pulse_amount: Body pulse expansion amount
            eye_size: Size of eyes on tentacle tips
            eyeball_color: Eyeball color (RGB tuple 0-1)
            pupil_color: Pupil color (RGB tuple 0-1)
        """
        # Create root entity
        self.root = Entity(position=(0, 0, 0))
        self.tentacles = []
        self.tentacle_tip_eyes = []  # Eyes attached to tentacle tips
        self.algorithm = algorithm
        self.algorithm_params = algorithm_params or {}
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor

        # Store appearance and animation parameters
        self.body_scale = body_scale
        self.tentacle_color = tentacle_color
        self.hue_shift = hue_shift
        self.anim_speed = anim_speed
        self.wave_amplitude = wave_amplitude
        self.pulse_speed = pulse_speed
        self.pulse_amount = pulse_amount
        self.eye_size = eye_size
        self.eyeball_color = eyeball_color
        self.pupil_color = pupil_color

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_camera_position = None

        # Create toon shader (shared across all parts)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in MedusaCreature, using default rendering")

        # Create central body sphere (match TentacleCreature color handling)
        body_params = {
            'model': 'sphere',
            'color': color.rgb(*tentacle_color),
            'scale': body_scale,
            'parent': self.root
        }
        if self.toon_shader is not None:
            body_params['shader'] = self.toon_shader

        self.body = Entity(**body_params)

        # Generate tentacles and tip eyes
        self.rebuild(num_tentacles, segments_per_tentacle, algorithm,
                    algorithm_params, thickness_base, taper_factor,
                    eye_size, eyeball_color, pupil_color)

    def rebuild(self, num_tentacles, segments_per_tentacle, algorithm,
                algorithm_params=None, thickness_base=0.25, taper_factor=0.6,
                eye_size=0.18, eyeball_color=(1.0, 0.95, 0.85), pupil_color=(0.1, 0.0, 0.2)):
        """Rebuild tentacles and tip eyes with new parameters."""
        # Clear existing tentacles
        for tentacle in self.tentacles:
            tentacle.destroy()
        self.tentacles.clear()

        # Clear existing tip eyes
        for eye in self.tentacle_tip_eyes:
            eye.destroy()
        self.tentacle_tip_eyes.clear()

        self.algorithm = algorithm
        self.algorithm_params = algorithm_params or {}
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor
        self.eye_size = eye_size
        self.eyeball_color = eyeball_color
        self.pupil_color = pupil_color

        # Create tentacles with Fibonacci sphere distribution
        body_radius = self.body.scale_x / 2

        for i in range(num_tentacles):
            # Fibonacci sphere distribution (top hemisphere - medusa tentacles pointing upward)
            # Y coordinate: 0.0 to 1.0 (top hemisphere only)
            y_normalized = 0.0 + (i / max(num_tentacles - 1, 1)) * 1.0

            # Clamp to sphere bounds
            y_normalized = max(-1.0, min(1.0, y_normalized))

            # Radius at this Y level (on unit sphere)
            radius_at_y = math.sqrt(max(0, 1 - y_normalized * y_normalized))

            # Angle using golden ratio for natural spiral
            angle = i * GOLDEN_ANGLE

            # Convert to Cartesian coordinates
            x_normalized = radius_at_y * math.cos(angle)
            z_normalized = radius_at_y * math.sin(angle)

            # Scale by body radius and position on body surface
            anchor = Vec3(
                x_normalized * body_radius * 0.90,
                y_normalized * body_radius * 0.90,
                z_normalized * body_radius * 0.90
            )

            # Target position (flowing outward and upward from anchor)
            # Medusa tentacles are shorter to show eyes on tips
            target_distance = 0.625  # 25% of original length
            target = Vec3(
                x_normalized * target_distance * 1.2,
                y_normalized * body_radius + 0.625,  # Flow upward (25% of original)
                z_normalized * target_distance * 1.2
            )

            # Color variation per tentacle
            hue_offset = i * self.hue_shift
            r, g, b = self.tentacle_color
            tentacle_color = (
                min(1.0, r + hue_offset * 0.4),
                g,
                max(0.0, b - hue_offset * 0.3)
            )

            # Create tentacle
            tentacle = Tentacle(
                parent=self.root,
                anchor=anchor,
                target=target,
                segments=segments_per_tentacle,
                algorithm=algorithm,
                color_rgb=tentacle_color,
                algorithm_params=self.algorithm_params,
                thickness_base=thickness_base,
                taper_factor=taper_factor,
                branch_depth=0,  # No branches for medusa (eyes are the feature)
                branch_count=0,
                current_depth=0,
                toon_shader=self.toon_shader
            )

            self.tentacles.append(tentacle)

            # Create eye at tentacle tip
            # Tip position is the last segment position
            if len(tentacle.segments) > 0:
                tip_segment = tentacle.segments[-1]
                tip_position = tip_segment.position

                # Calculate direction from body to tip (for eye orientation)
                tip_direction = (tip_position - anchor).normalized()

                # Create eye at tip
                eye = Eye(
                    position=tip_position,
                    size=eye_size,
                    eyeball_color=eyeball_color,
                    pupil_color=pupil_color,
                    parent=self.root,
                    toon_shader=self.toon_shader
                )

                self.tentacle_tip_eyes.append(eye)

    def start_attack(self, camera_position):
        """
        Start attack animation (all tentacles lash out).

        Args:
            camera_position: Vec3 position of camera (attack target)
        """
        self.is_attacking = True
        self.attack_start_time = 0  # Will be set on first update
        self.attack_camera_position = camera_position

    def start_attack_2(self, camera_position):
        """
        Start attack 2 animation (same as attack 1 for medusa).

        Args:
            camera_position: Vec3 position of camera (attack target)
        """
        self.start_attack(camera_position)

    def update_animation(self, time, camera_position=None):
        """Update creature animations."""
        # Handle attack state
        if self.is_attacking:
            # Initialize attack start time on first frame
            if self.attack_start_time == 0:
                self.attack_start_time = time

            # Check if attack is complete
            attack_elapsed = time - self.attack_start_time
            attack_duration = 1.2
            if attack_elapsed >= attack_duration:
                self.is_attacking = False
                self.attack_start_time = 0
                self.attack_camera_position = None

        # Pulse body
        scale_pulse = self.body_scale + math.sin(time * self.pulse_speed) * self.pulse_amount
        self.body.scale = scale_pulse

        # Animate tentacles
        for idx, tentacle in enumerate(self.tentacles):
            if self.is_attacking:
                # Attack animation
                tentacle.update_animation(
                    time, self.anim_speed, self.wave_amplitude,
                    is_attacking=True,
                    attack_start_time=self.attack_start_time,
                    camera_position=self.attack_camera_position or camera_position
                )
            else:
                # Normal idle animation (slow, flowing, hypnotic)
                tentacle.update_animation(
                    time, self.anim_speed, self.wave_amplitude
                )

        # Update eye positions to follow tentacle tips
        for idx, (tentacle, eye) in enumerate(zip(self.tentacles, self.tentacle_tip_eyes)):
            if len(tentacle.segments) > 0:
                # Get tip segment position
                tip_segment = tentacle.segments[-1]
                tip_position = tip_segment.position

                # Calculate direction from body center to tip (for eye orientation)
                tip_direction = (tip_position - Vec3(0, 0, 0)).normalized()

                # Update eyeball position to tip
                eye.eyeball.position = tip_position

                # Calculate pupil offset along tip direction
                pupil_offset = tip_direction * (eye.base_size * 0.5)
                eye.pupil.position = tip_position + pupil_offset

                # Update base positions for animation
                eye.eyeball_base_position = tip_position
                eye.pupil_base_position = tip_position + pupil_offset

        # Animate eyes (blinking)
        for eye in self.tentacle_tip_eyes:
            eye.update_animation(time)

    def destroy(self):
        """Cleanup all entities."""
        for tentacle in self.tentacles:
            tentacle.destroy()
        for eye in self.tentacle_tip_eyes:
            eye.destroy()
        destroy(self.root)
