"""
StarfishCreature model - radial symmetry creature with articulated arms.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from ..core.curves import bezier_curve
from ..core.constants import GOLDEN_RATIO, GOLDEN_ANGLE
from ..shaders import create_toon_shader


class StarfishArm:
    """Single articulated arm made of connected spheres."""

    def __init__(self, central_body_position, arm_index, total_arms,
                 arm_segments, base_thickness, central_body_size, base_color,
                 parent, toon_shader=None, curl_factor=0.3):
        """
        Create a starfish arm.

        Args:
            central_body_position: Vec3 position of central body
            arm_index: Index of this arm (0 to total_arms-1)
            total_arms: Total number of arms on starfish
            arm_segments: Number of segments in this arm
            base_thickness: Thickness of arm at base (scaled down by golden ratio)
            central_body_size: Size of central body (for anchor positioning)
            base_color: RGB tuple for arm color
            parent: Parent entity (scene root)
            toon_shader: Optional toon shader to apply
            curl_factor: How much arm curves (0-1, higher = more curl)
        """
        self.central_body_position = central_body_position
        self.arm_index = arm_index
        self.total_arms = total_arms
        self.arm_segments = arm_segments
        self.base_color = base_color
        self.curl_factor = curl_factor
        self.spheres = []
        self.connector_tubes = []
        self.curve_points = []

        # Calculate arm angle in radial pattern (360 / total_arms degrees per arm)
        self.angle = (arm_index / total_arms) * math.pi * 2

        # Random phase offset for animation variation
        self.animation_phase_offset = random.random() * math.pi * 2

        # Generate arm curve using Bezier
        self._generate_arm_curve(central_body_size, base_thickness, parent, toon_shader)

    def _generate_arm_curve(self, central_body_size, base_thickness, parent, toon_shader):
        """Generate arm as chain of spheres using Bezier curve."""
        # Calculate arm direction based on radial angle
        direction_x = math.cos(self.angle)
        direction_z = math.sin(self.angle)

        # Anchor point on central body surface
        anchor_offset = (central_body_size / 2) * 0.9
        anchor = self.central_body_position + Vec3(
            direction_x * anchor_offset,
            0,
            direction_z * anchor_offset
        )

        # Target point (arm tip) - extends outward with curl
        arm_length = 2.0  # Total arm length
        # Apply curl: higher curl_factor means tip curls more (lower Y)
        tip_y_offset = -0.3 - (self.curl_factor * 0.5)
        target = self.central_body_position + Vec3(
            direction_x * arm_length,
            tip_y_offset,
            direction_z * arm_length
        )

        # Generate Bezier curve for arm shape (smooth outward curve)
        # Use curl_factor to control curvature
        control_strength = 0.3 + (self.curl_factor * 0.2)
        self.curve_points = bezier_curve(
            anchor, target, self.arm_segments,
            control_strength=control_strength
        )

        # Create spheres at curve points
        for i in range(self.arm_segments):
            position = self.curve_points[i]

            # Size decreases by golden ratio toward tip
            size = base_thickness / (GOLDEN_RATIO ** i)
            size = max(size, 0.1)  # Minimum size

            # Color variation (darker toward tip)
            color_factor = 1.0 - (i / self.arm_segments) * 0.3
            sphere_color = (
                self.base_color[0] * color_factor,
                self.base_color[1] * color_factor,
                self.base_color[2] * color_factor
            )

            # Create sphere entity
            sphere_params = {
                'model': 'sphere',
                'color': color.rgb(*sphere_color),
                'scale': size,
                'position': position,
                'parent': parent
            }

            if toon_shader is not None:
                sphere_params['shader'] = toon_shader

            sphere = Entity(**sphere_params)
            sphere.base_position = position  # Store for animation
            sphere.segment_index = i
            self.spheres.append(sphere)

            # Create connector tube to previous sphere
            if i > 0:
                self._create_connector_tube(
                    self.spheres[i - 1], sphere,
                    sphere_color, parent, toon_shader
                )

    def _create_connector_tube(self, sphere1, sphere2, tube_color, parent, toon_shader):
        """Create tube connecting two spheres."""
        # Calculate tube position, rotation, and length
        midpoint = (sphere1.position + sphere2.position) / 2
        length = (sphere2.position - sphere1.position).length()

        # Tube radius (average of both sphere sizes)
        avg_size = (sphere1.scale_x + sphere2.scale_x) / 2
        tube_radius = avg_size * 0.3

        # Create tube entity (using cube stretched along Y axis)
        tube_params = {
            'model': 'cube',
            'color': color.rgb(*tube_color),
            'position': midpoint,
            'scale': (tube_radius, length / 2, tube_radius),
            'parent': parent
        }

        if toon_shader is not None:
            tube_params['shader'] = toon_shader

        tube = Entity(**tube_params)

        # Orient tube from sphere1 to sphere2
        tube.look_at(sphere1, axis=Vec3.up)

        # Store base transform for animation
        tube.base_position = midpoint
        tube.sphere1 = sphere1
        tube.sphere2 = sphere2

        self.connector_tubes.append(tube)

    def _update_connector_tube_transform(self, tube):
        """Update connector tube position to follow animated spheres."""
        # Recalculate midpoint
        midpoint = (tube.sphere1.position + tube.sphere2.position) / 2
        tube.position = midpoint

        # Recalculate length
        length = (tube.sphere2.position - tube.sphere1.position).length()
        tube.scale_y = length / 2

        # Update rotation
        tube.look_at(tube.sphere1, axis=Vec3.up)

    def update_animation(self, time, anim_speed, pulse_amount,
                        is_attacking=False, attack_progress=0.0, camera_position=None):
        """
        Update arm animation.

        Args:
            time: Current animation time
            anim_speed: Animation speed multiplier
            pulse_amount: Pulse intensity
            is_attacking: Whether attack is in progress
            attack_progress: Attack animation progress (0-1)
            camera_position: Camera position for attack targeting
        """
        if is_attacking and attack_progress < 1.0:
            # Attack animation: curl inward → snap outward
            if attack_progress < 0.3:
                # Curl inward phase (0.0 - 0.3)
                phase_t = attack_progress / 0.3
                ease_t = phase_t * phase_t  # Ease-in quad

                # Pull spheres inward toward central body
                for sphere in self.spheres:
                    i = sphere.segment_index
                    segment_t = i / max(self.arm_segments, 1)

                    # Inward pull increases toward tip
                    pull_strength = ease_t * segment_t * 0.4
                    direction_to_center = (self.central_body_position - sphere.base_position).normalized()
                    offset = direction_to_center * pull_strength

                    sphere.position = sphere.base_position + offset

            elif attack_progress < 0.7:
                # Snap outward phase (0.3 - 0.7)
                phase_t = (attack_progress - 0.3) / 0.4
                ease_t = 1.0 - (1.0 - phase_t) ** 3  # Ease-out cubic

                # Calculate outward direction (away from center)
                direction_x = math.cos(self.angle)
                direction_z = math.sin(self.angle)
                outward_direction = Vec3(direction_x, 0, direction_z)

                for sphere in self.spheres:
                    i = sphere.segment_index
                    segment_t = i / max(self.arm_segments, 1)

                    # Outward snap increases toward tip
                    snap_strength = ease_t * segment_t * 0.8
                    offset = outward_direction * snap_strength

                    sphere.position = sphere.base_position + offset

            else:
                # Return phase (0.7 - 1.0)
                phase_t = (attack_progress - 0.7) / 0.3
                ease_t = 1.0 - (1.0 - phase_t) ** 2  # Ease-out quad

                # Return to base positions
                for sphere in self.spheres:
                    i = sphere.segment_index
                    segment_t = i / max(self.arm_segments, 1)

                    # Interpolate back to base
                    direction_x = math.cos(self.angle)
                    direction_z = math.sin(self.angle)
                    outward_direction = Vec3(direction_x, 0, direction_z)
                    snap_offset = outward_direction * segment_t * 0.8
                    current_offset = snap_offset * (1.0 - ease_t)

                    sphere.position = sphere.base_position + current_offset

        else:
            # Idle animation: wave undulation along arm
            for sphere in self.spheres:
                i = sphere.segment_index
                segment_t = i / max(self.arm_segments, 1)

                # Wave motion with phase offset for variation
                phase = time * anim_speed + self.animation_phase_offset + i * 0.4

                # Multi-frequency wave (like tentacles)
                wave_offset_y = (
                    math.sin(phase) * 0.6 +
                    math.sin(phase * 1.5) * 0.3 +
                    math.cos(phase * 0.8) * 0.1
                ) * pulse_amount * segment_t * 2.0

                # Slight lateral sway
                wave_offset_x = math.sin(phase * 0.7) * pulse_amount * segment_t * 0.5
                wave_offset_z = math.cos(phase * 0.7) * pulse_amount * segment_t * 0.5

                # Apply animation offset
                sphere.position = sphere.base_position + Vec3(wave_offset_x, wave_offset_y, wave_offset_z)

        # Update all connector tubes to follow spheres
        for tube in self.connector_tubes:
            self._update_connector_tube_transform(tube)

    def destroy(self):
        """Cleanup arm entities."""
        for sphere in self.spheres:
            destroy(sphere)
        for tube in self.connector_tubes:
            destroy(tube)
        self.spheres.clear()
        self.connector_tubes.clear()


class StarfishCreature:
    """Creature with radial symmetry and articulated arms."""

    def __init__(self, num_arms=5, arm_segments=6, central_body_size=0.8,
                 arm_base_thickness=0.4, starfish_color=(0.9, 0.5, 0.3),
                 curl_factor=0.3, anim_speed=1.5, pulse_amount=0.06):
        """
        Create a starfish creature.

        Args:
            num_arms: Number of arms (5-8)
            arm_segments: Segments per arm (4-10)
            central_body_size: Size of central body sphere (0.4-1.5)
            arm_base_thickness: Base thickness of arms (0.2-0.6)
            starfish_color: Base color (RGB tuple 0-1)
            curl_factor: Arm curvature amount (0-0.8)
            anim_speed: Animation speed
            pulse_amount: Pulse intensity
        """
        # Create root entity
        self.root = Entity(position=(0, 0, 0))
        self.arms = []

        # Store parameters
        self.num_arms = num_arms
        self.arm_segments = arm_segments
        self.central_body_size = central_body_size
        self.arm_base_thickness = arm_base_thickness
        self.starfish_color = starfish_color
        self.curl_factor = curl_factor
        self.anim_speed = anim_speed
        self.pulse_amount = pulse_amount

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0

        # Create toon shader (shared across all parts)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in StarfishCreature, using default rendering")

        # Generate creature
        self._generate_starfish()

    def _generate_starfish(self):
        """Generate central body and arms."""
        # Clear existing arms
        for arm in self.arms:
            arm.destroy()
        self.arms.clear()

        # Destroy central body if exists
        if hasattr(self, 'central_body'):
            destroy(self.central_body)

        # Create central body sphere
        central_position = Vec3(0, 0, 0)

        body_params = {
            'model': 'sphere',
            'color': color.rgb(*self.starfish_color),
            'scale': self.central_body_size,
            'position': central_position,
            'parent': self.root
        }

        if self.toon_shader is not None:
            body_params['shader'] = self.toon_shader

        self.central_body = Entity(**body_params)
        self.central_body.base_scale = self.central_body_size

        # Create arms in radial pattern
        for i in range(self.num_arms):
            # Slight color variation per arm
            hue_offset = i * 0.05
            arm_color = (
                min(1.0, self.starfish_color[0] + hue_offset * 0.2),
                self.starfish_color[1],
                max(0.0, self.starfish_color[2] - hue_offset * 0.1)
            )

            arm = StarfishArm(
                central_body_position=central_position,
                arm_index=i,
                total_arms=self.num_arms,
                arm_segments=self.arm_segments,
                base_thickness=self.arm_base_thickness,
                central_body_size=self.central_body_size,
                base_color=arm_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                curl_factor=self.curl_factor
            )

            self.arms.append(arm)

    def rebuild(self, num_arms, arm_segments, central_body_size, arm_base_thickness,
                starfish_color, curl_factor, anim_speed, pulse_amount):
        """
        Rebuild starfish with new parameters.

        Args:
            num_arms: Number of arms
            arm_segments: Segments per arm
            central_body_size: Central body size
            arm_base_thickness: Arm thickness
            starfish_color: Base color
            curl_factor: Arm curvature
            anim_speed: Animation speed
            pulse_amount: Pulse intensity
        """
        self.num_arms = num_arms
        self.arm_segments = arm_segments
        self.central_body_size = central_body_size
        self.arm_base_thickness = arm_base_thickness
        self.starfish_color = starfish_color
        self.curl_factor = curl_factor
        self.anim_speed = anim_speed
        self.pulse_amount = pulse_amount

        # Regenerate creature
        self._generate_starfish()

    def start_attack(self, camera_position):
        """Start attack animation."""
        self.is_attacking = True
        self.attack_start_time = 0

    def start_attack_2(self, camera_position):
        """Start attack 2 animation (same as attack 1 for starfish)."""
        self.start_attack(camera_position)

    def update_animation(self, time, camera_position=None):
        """
        Update starfish animation.

        Args:
            time: Current animation time
            camera_position: Optional camera position for attack targeting
        """
        # Handle attack state
        attack_progress = 0.0
        if self.is_attacking:
            # Initialize attack start time on first frame
            if self.attack_start_time == 0:
                self.attack_start_time = time

            # Calculate attack progress
            from ..core.constants import STARFISH_ATTACK_DURATION
            attack_elapsed = time - self.attack_start_time
            attack_progress = min(attack_elapsed / STARFISH_ATTACK_DURATION, 1.0)

            if attack_progress >= 1.0:
                # Attack complete
                self.is_attacking = False
                self.attack_start_time = 0

        # Pulse central body
        pulse_wave = math.sin(time * self.anim_speed * 1.2)
        scale_pulse = self.central_body.base_scale * (1.0 + self.pulse_amount * pulse_wave)
        self.central_body.scale = scale_pulse

        # Animate all arms
        for arm in self.arms:
            arm.update_animation(
                time=time,
                anim_speed=self.anim_speed,
                pulse_amount=self.pulse_amount,
                is_attacking=self.is_attacking,
                attack_progress=attack_progress,
                camera_position=camera_position
            )

    def destroy(self):
        """Cleanup all entities."""
        for arm in self.arms:
            arm.destroy()
        if hasattr(self, 'central_body'):
            destroy(self.central_body)
        destroy(self.root)
