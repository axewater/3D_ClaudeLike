"""
TentacleCreature model - creature with body and tentacles.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .tentacle import Tentacle
from .eye import Eye
from ..core.constants import BODY_COLOR, BODY_SCALE, BODY_PULSE_AMOUNT, BODY_PULSE_SPEED
from ..shaders import create_toon_shader


class TentacleCreature:
    """Creature with body and tentacles."""

    def __init__(self, num_tentacles=2, segments_per_tentacle=12, algorithm='bezier',
                 algorithm_params=None, thickness_base=0.25, taper_factor=0.6,
                 branch_depth=0, branch_count=1, body_scale=1.2, tentacle_color=(0.6, 0.3, 0.7),
                 hue_shift=0.1, anim_speed=2.0, wave_amplitude=0.05, pulse_speed=1.5, pulse_amount=0.05,
                 num_eyes=3, eye_size_min=0.1, eye_size_max=0.25,
                 eyeball_color=(1.0, 1.0, 1.0), pupil_color=(0.0, 0.0, 0.0)):
        """
        Create a tentacle creature.

        Args:
            num_tentacles: Number of tentacles
            segments_per_tentacle: Segments per tentacle
            algorithm: 'bezier' or 'fourier'
            algorithm_params: Dict of algorithm parameters
            thickness_base: Base thickness of tentacles
            taper_factor: Taper factor for tentacles
            branch_depth: Maximum branching depth
            branch_count: Number of child branches per tentacle
            body_scale: Body sphere scale
            tentacle_color: Base tentacle color (RGB tuple 0-1)
            hue_shift: Color variation between tentacles
            anim_speed: Animation wave speed
            wave_amplitude: Wave motion intensity
            pulse_speed: Body pulse breathing speed
            pulse_amount: Body pulse expansion amount
            num_eyes: Number of eyes on upper hemisphere
            eye_size_min: Minimum eye size
            eye_size_max: Maximum eye size
            eyeball_color: Eyeball color (RGB tuple 0-1)
            pupil_color: Pupil color (RGB tuple 0-1)
        """
        # Create root entity (no parent = defaults to scene)
        self.root = Entity(position=(0, 0, 0))
        self.tentacles = []
        self.eyes = []
        self.algorithm = algorithm
        self.algorithm_params = algorithm_params or {}
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor
        self.branch_depth = branch_depth
        self.branch_count = branch_count

        # Store appearance and animation parameters
        self.body_scale = body_scale
        self.tentacle_color = tentacle_color
        self.hue_shift = hue_shift
        self.anim_speed = anim_speed
        self.wave_amplitude = wave_amplitude
        self.pulse_speed = pulse_speed
        self.pulse_amount = pulse_amount

        # Store eye parameters
        self.num_eyes = num_eyes
        self.eye_size_min = eye_size_min
        self.eye_size_max = eye_size_max
        self.eyeball_color = eyeball_color
        self.pupil_color = pupil_color

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_camera_position = None

        # Exploration animation state (coordinated tentacle reaching)
        self.exploration_target = Vec3(0, -2, 0)  # Current shared goal position
        self.reaching_tentacle_indices = set()  # Which tentacles are currently reaching
        self.exploration_state = 'idle'  # 'idle', 'reaching', or 'returning'
        self.exploration_phase_start_time = 0  # When current phase started

        # Create toon shader (shared across all creature parts)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in TentacleCreature, using default rendering")

        # Create body (use dynamic scale and color with toon shader)
        # Body color matches tentacle base color
        # Only apply shader if it was created successfully
        body_params = {
            'model': 'sphere',
            'color': color.rgb(*tentacle_color),
            'scale': body_scale,
            'parent': self.root
        }
        if self.toon_shader is not None:
            body_params['shader'] = self.toon_shader

        self.body = Entity(**body_params)

        # Generate tentacles and eyes
        self.rebuild(num_tentacles, segments_per_tentacle, algorithm,
                    algorithm_params, thickness_base, taper_factor, branch_depth, branch_count,
                    num_eyes, eye_size_min, eye_size_max, eyeball_color, pupil_color)

    def rebuild(self, num_tentacles, segments_per_tentacle, algorithm,
                algorithm_params=None, thickness_base=0.25, taper_factor=0.6,
                branch_depth=0, branch_count=1, num_eyes=3, eye_size_min=0.1, eye_size_max=0.25,
                eyeball_color=(1.0, 1.0, 1.0), pupil_color=(0.0, 0.0, 0.0)):
        """Rebuild tentacles and eyes with new parameters."""
        # Clear existing tentacles
        for tentacle in self.tentacles:
            tentacle.destroy()
        self.tentacles.clear()

        # Clear existing eyes
        for eye in self.eyes:
            eye.destroy()
        self.eyes.clear()

        # Reset exploration state when rebuilding
        self.exploration_state = 'idle'
        self.reaching_tentacle_indices = set()
        self.exploration_phase_start_time = 0

        self.algorithm = algorithm
        self.algorithm_params = algorithm_params or {}
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor
        self.branch_depth = branch_depth
        self.branch_count = branch_count

        # Store eye parameters
        self.num_eyes = num_eyes
        self.eye_size_min = eye_size_min
        self.eye_size_max = eye_size_max
        self.eyeball_color = eyeball_color
        self.pupil_color = pupil_color

        # Create new tentacles with Fibonacci sphere distribution
        body_radius = self.body.scale_x / 2

        # Golden angle in radians (for natural spiral distribution)
        GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~137.508 degrees

        for i in range(num_tentacles):
            # Fibonacci sphere distribution (biased toward lower hemisphere)
            # This creates a natural, organic spread like sunflower seeds

            # Y coordinate (biased toward bottom -0.8 to 0.2 range)
            y_normalized = -0.8 + (i / max(num_tentacles - 1, 1)) * 1.0

            # Radius at this Y level (on unit sphere)
            radius_at_y = math.sqrt(1 - y_normalized * y_normalized)

            # Angle using golden ratio for natural spiral
            angle = i * GOLDEN_ANGLE

            # Convert to Cartesian coordinates
            x_normalized = radius_at_y * math.cos(angle)
            z_normalized = radius_at_y * math.sin(angle)

            # Scale by body radius and position on body surface
            anchor = Vec3(
                x_normalized * body_radius * 0.85,
                y_normalized * body_radius * 0.95,
                z_normalized * body_radius * 0.85
            )

            # Target position (hanging down and outward from anchor)
            target_distance = 1.5
            target = Vec3(
                x_normalized * target_distance,
                y_normalized * body_radius - 2.0,  # Hang down
                z_normalized * target_distance
            )

            # Color variation per tentacle (use dynamic colors)
            hue_offset = i * self.hue_shift
            r, g, b = self.tentacle_color
            tentacle_color = (
                min(1.0, r + hue_offset * 0.5),
                g,
                max(0.0, b - hue_offset * 0.3)
            )

            # Create tentacle with dynamic parameters (including branching and shared shader)
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
                branch_depth=branch_depth,
                branch_count=branch_count,
                current_depth=0,  # Main tentacles start at depth 0
                toon_shader=self.toon_shader  # Share shader instance across all tentacles
            )

            self.tentacles.append(tentacle)

        # Create eyes on upper hemisphere using Fibonacci sphere distribution
        body_radius = self.body.scale_x / 2

        # Golden angle in radians (for natural spiral distribution)
        GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~137.508 degrees

        for i in range(num_eyes):
            # Fibonacci sphere distribution (biased toward upper hemisphere)
            # Y coordinate (upper hemisphere: 0.2 to 0.8 range)
            y_normalized = 0.2 + (i / max(num_eyes - 1, 1) if num_eyes > 1 else 0) * 0.6

            # Radius at this Y level (on unit sphere)
            radius_at_y = math.sqrt(max(0, 1 - y_normalized * y_normalized))

            # Angle using golden ratio for natural spiral
            angle = i * GOLDEN_ANGLE

            # Convert to Cartesian coordinates
            x_normalized = radius_at_y * math.cos(angle)
            z_normalized = radius_at_y * math.sin(angle)

            # Scale by body radius and position on body surface
            position = Vec3(
                x_normalized * body_radius * 0.95,
                y_normalized * body_radius * 0.95,
                z_normalized * body_radius * 0.95
            )

            # Random size within range
            eye_size = random.uniform(eye_size_min, eye_size_max)

            # Create eye with dynamic parameters and shared shader
            eye = Eye(
                position=position,
                size=eye_size,
                eyeball_color=eyeball_color,
                pupil_color=pupil_color,
                parent=self.root,
                toon_shader=self.toon_shader
            )

            self.eyes.append(eye)

    def start_attack(self, camera_position):
        """
        Start attack animation.

        Args:
            camera_position: Vec3 position of camera (attack target)
        """
        self.is_attacking = True
        self.attack_start_time = 0  # Will be set on first update
        self.attack_camera_position = camera_position

    def update_animation(self, time, camera_position=None):
        """Update creature animations."""
        # Import attack and exploration constants
        from ..core.constants import (
            ATTACK_DURATION,
            EXPLORATION_REACH_DURATION, EXPLORATION_RETURN_DURATION, EXPLORATION_IDLE_GAP,
            EXPLORATION_TENTACLE_RATIO, EXPLORATION_TARGET_MIN_RADIUS, EXPLORATION_TARGET_MAX_RADIUS
        )
        import random

        # Handle attack state
        if self.is_attacking:
            # Initialize attack start time on first frame
            if self.attack_start_time == 0:
                self.attack_start_time = time

            # Check if attack is complete
            attack_elapsed = time - self.attack_start_time
            if attack_elapsed >= ATTACK_DURATION:
                self.is_attacking = False
                self.attack_start_time = 0
                self.attack_camera_position = None

        # Handle exploration state (only when not attacking)
        reach_progress = 0.0
        if not self.is_attacking:
            # Initialize exploration phase start time on first frame
            if self.exploration_phase_start_time == 0:
                self.exploration_phase_start_time = time

            # Calculate elapsed time in current phase
            phase_elapsed = time - self.exploration_phase_start_time

            # State machine for exploration animation
            if self.exploration_state == 'idle':
                # Idle gap between cycles
                if phase_elapsed >= EXPLORATION_IDLE_GAP:
                    # Transition to reaching: select tentacles and generate target
                    num_tentacles = len(self.tentacles)
                    if num_tentacles > 0:
                        # Select 25-40% of tentacles
                        min_reaching = max(1, int(num_tentacles * EXPLORATION_TENTACLE_RATIO[0]))
                        max_reaching = max(1, int(num_tentacles * EXPLORATION_TENTACLE_RATIO[1]))
                        num_reaching = random.randint(min_reaching, max_reaching)

                        # Randomly select tentacles
                        self.reaching_tentacle_indices = set(random.sample(range(num_tentacles), num_reaching))

                        # Generate random target in spherical shell
                        theta = random.random() * math.pi * 2  # Horizontal angle (0-360)
                        phi = random.random() * math.pi * 2  # Vertical angle (0-360)
                        radius = EXPLORATION_TARGET_MIN_RADIUS + random.random() * (
                            EXPLORATION_TARGET_MAX_RADIUS - EXPLORATION_TARGET_MIN_RADIUS
                        )

                        self.exploration_target = Vec3(
                            radius * math.sin(phi) * math.cos(theta),
                            radius * math.cos(phi),
                            radius * math.sin(phi) * math.sin(theta)
                        )

                        # Transition to reaching state
                        self.exploration_state = 'reaching'
                        self.exploration_phase_start_time = time
                        reach_progress = 0.0

            elif self.exploration_state == 'reaching':
                # Reaching phase
                reach_progress = min(phase_elapsed / EXPLORATION_REACH_DURATION, 1.0)

                if phase_elapsed >= EXPLORATION_REACH_DURATION:
                    # Transition to returning
                    self.exploration_state = 'returning'
                    self.exploration_phase_start_time = time
                    reach_progress = 0.0

            elif self.exploration_state == 'returning':
                # Spring-back phase
                reach_progress = min(phase_elapsed / EXPLORATION_RETURN_DURATION, 1.0)

                if phase_elapsed >= EXPLORATION_RETURN_DURATION:
                    # Transition to idle
                    self.exploration_state = 'idle'
                    self.reaching_tentacle_indices = set()
                    self.exploration_phase_start_time = time

        # Pulse body (use dynamic parameters)
        scale_pulse = self.body_scale + math.sin(time * self.pulse_speed) * self.pulse_amount
        self.body.scale = scale_pulse

        # Animate eyes (blinking)
        for eye in self.eyes:
            eye.update_animation(time)

        # Animate tentacles (pass animation, attack, and exploration parameters)
        for idx, tentacle in enumerate(self.tentacles):
            # Check if this tentacle is currently reaching
            is_reaching = idx in self.reaching_tentacle_indices

            if self.is_attacking:
                # All tentacles attack together
                tentacle.update_animation(
                    time, self.anim_speed, self.wave_amplitude,
                    is_attacking=True,
                    attack_start_time=self.attack_start_time,
                    camera_position=self.attack_camera_position or camera_position
                )
            else:
                # Normal idle animation (with optional exploration reaching)
                tentacle.update_animation(
                    time, self.anim_speed, self.wave_amplitude,
                    is_reaching=is_reaching,
                    reach_target=self.exploration_target,
                    reach_state=self.exploration_state,
                    reach_progress=reach_progress
                )

    def destroy(self):
        """Cleanup all entities."""
        for tentacle in self.tentacles:
            tentacle.destroy()
        for eye in self.eyes:
            eye.destroy()
        # Properly destroy the root and all children
        destroy(self.root)
