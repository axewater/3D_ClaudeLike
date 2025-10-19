"""
PolypCreature model - segmented spine creature with spheres and tentacles.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .tentacle import Tentacle
from ..core.curves import bezier_curve, fourier_curve
from ..core.constants import (
    GOLDEN_RATIO, GOLDEN_ANGLE,
    DEFAULT_TENTACLE_COLOR, DEFAULT_ALGORITHM
)
from ..shaders import create_toon_shader


class PolypSphere:
    """Single sphere in the polyp chain with tentacles."""

    def __init__(self, position, size, base_color, parent, toon_shader=None,
                 sphere_index=0, parent_sphere=None):
        """
        Create a polyp sphere.

        Args:
            position: Vec3 position in world space
            size: Sphere radius
            base_color: RGB tuple (0-1)
            parent: Parent entity (scene root)
            toon_shader: Optional toon shader to apply
            sphere_index: Index in chain (0 = root)
            parent_sphere: Reference to parent PolypSphere (None for root)
        """
        self.original_position = position
        self.base_position = position
        self.size = size
        self.base_color = base_color
        self.sphere_index = sphere_index
        self.parent_sphere = parent_sphere
        self.tentacles = []
        self.connector_tube = None

        # Create sphere entity with toon shader
        sphere_color = color.rgb(*base_color)
        entity_params = {
            'model': 'sphere',
            'color': sphere_color,
            'scale': size,
            'position': position,
            'parent': parent
        }

        if toon_shader is not None:
            entity_params['shader'] = toon_shader

        self.entity = Entity(**entity_params)

        # Create connector tube if this sphere has a parent
        if parent_sphere is not None:
            self._create_connector_tube(parent, base_color, toon_shader)

    def _create_connector_tube(self, scene_parent, base_color, toon_shader):
        """Create tube connecting this sphere to its parent sphere."""
        # Calculate tube radius (average of both sphere sizes)
        avg_size = (self.size + self.parent_sphere.size) / 2
        tube_radius = avg_size * 0.25  # 25% of average size

        # Calculate initial position, rotation, and length
        midpoint = (self.original_position + self.parent_sphere.original_position) / 2
        length = (self.original_position - self.parent_sphere.original_position).length()

        # Create tube color (same as sphere)
        tube_color = color.rgb(*base_color)

        # Create tube entity
        tube_params = {
            'model': 'cube',
            'color': tube_color,
            'position': midpoint,
            'scale': (tube_radius, length / 2, tube_radius),
            'parent': scene_parent
        }

        if toon_shader is not None:
            tube_params['shader'] = toon_shader

        self.connector_tube = Entity(**tube_params)

        # Point the tube from parent to child
        self.connector_tube.look_at(self.parent_sphere.entity, axis=Vec3.up)

    def _update_connector_tube_transform(self):
        """Update connector tube position to follow animated spheres."""
        if self.connector_tube is None or self.parent_sphere is None:
            return

        # Recalculate midpoint between current positions
        midpoint = (self.entity.position + self.parent_sphere.entity.position) / 2
        self.connector_tube.position = midpoint

        # Recalculate length
        length = (self.entity.position - self.parent_sphere.entity.position).length()
        self.connector_tube.scale_y = length / 2

        # Update rotation to point from parent to child
        self.connector_tube.look_at(self.parent_sphere.entity, axis=Vec3.up)

    def create_tentacles(self, num_tentacles, segments_per_tentacle, algorithm,
                        algorithm_params, thickness_base, taper_factor,
                        scene_parent, toon_shader):
        """
        Create tentacles attached to this sphere's lower hemisphere.

        Args:
            num_tentacles: Number of tentacles for this sphere
            segments_per_tentacle: Segments per tentacle
            algorithm: 'bezier' or 'fourier'
            algorithm_params: Algorithm-specific parameters
            thickness_base: Base tentacle thickness
            taper_factor: Tentacle taper factor
            scene_parent: Parent entity for tentacles
            toon_shader: Toon shader instance
        """
        # Clear existing tentacles
        for tentacle in self.tentacles:
            tentacle.destroy()
        self.tentacles.clear()

        # Use Fibonacci sphere distribution on lower hemisphere only
        for i in range(num_tentacles):
            # Fibonacci sphere distribution (biased toward lower hemisphere)
            # Y coordinate: -0.9 to -0.2 (mostly downward)
            y_normalized = -0.9 + (i / max(num_tentacles - 1, 1)) * 0.7

            # Radius at this Y level (on unit sphere)
            radius_at_y = math.sqrt(max(0, 1 - y_normalized * y_normalized))

            # Angle using golden ratio for natural spiral
            angle = i * GOLDEN_ANGLE

            # Convert to Cartesian coordinates
            x_normalized = radius_at_y * math.cos(angle)
            z_normalized = radius_at_y * math.sin(angle)

            # Scale by sphere size and position on sphere surface
            anchor = self.original_position + Vec3(
                x_normalized * self.size * 0.9,
                y_normalized * self.size * 0.9,
                z_normalized * self.size * 0.9
            )

            # Target position (hanging down and outward from anchor)
            target_distance = self.size * 2.0  # Tentacle length proportional to sphere size
            target = anchor + Vec3(
                x_normalized * target_distance * 0.5,
                y_normalized * self.size - target_distance * 1.5,
                z_normalized * target_distance * 0.5
            )

            # Color variation per tentacle
            hue_offset = i * 0.08
            r, g, b = self.base_color
            tentacle_color = (
                min(1.0, r + hue_offset * 0.3),
                g,
                max(0.0, b - hue_offset * 0.2)
            )

            # Create tentacle
            tentacle = Tentacle(
                parent=scene_parent,
                anchor=anchor,
                target=target,
                segments=segments_per_tentacle,
                algorithm=algorithm,
                color_rgb=tentacle_color,
                algorithm_params=algorithm_params,
                thickness_base=thickness_base,
                taper_factor=taper_factor,
                branch_depth=0,  # No branching for polyp tentacles
                branch_count=0,
                current_depth=0,
                toon_shader=toon_shader
            )

            self.tentacles.append(tentacle)

    def update_animation(self, time, anim_speed, pulse_amount, sphere_phase_offset,
                        is_attacking=False, attack_progress=0.0, camera_position=None):
        """
        Update sphere and tentacle animations.

        Args:
            time: Current animation time
            anim_speed: Animation speed
            pulse_amount: Pulse intensity
            sphere_phase_offset: Phase offset for wave motion along spine
            is_attacking: Whether attack is in progress
            attack_progress: Attack animation progress (0-1)
            camera_position: Camera position for attack targeting
        """
        if is_attacking and attack_progress < 1.0:
            # Attack animation: whip forward toward camera
            if camera_position is not None:
                # Calculate direction to camera
                direction_to_camera = (camera_position - self.original_position).normalized()

                # Wind-up (0.0 - 0.2): Pull back
                # Strike (0.2 - 0.6): Lash forward
                # Return (0.6 - 1.0): Ease back
                if attack_progress < 0.2:
                    # Wind-up phase
                    phase_t = attack_progress / 0.2
                    ease_t = phase_t * phase_t
                    offset = -direction_to_camera * 0.3 * ease_t * (self.sphere_index + 1) / 5
                elif attack_progress < 0.6:
                    # Strike phase
                    phase_t = (attack_progress - 0.2) / 0.4
                    ease_t = 1.0 - math.pow(1.0 - phase_t, 3)
                    strike_distance = 1.5 * (self.sphere_index + 1) / 5
                    offset = direction_to_camera * strike_distance * ease_t - direction_to_camera * 0.3
                else:
                    # Return phase
                    phase_t = (attack_progress - 0.6) / 0.4
                    ease_t = 1.0 - math.pow(1.0 - phase_t, 3)
                    strike_distance = 1.5 * (self.sphere_index + 1) / 5
                    remaining_offset = direction_to_camera * strike_distance * 0.4 - direction_to_camera * 0.3
                    offset = remaining_offset * (1.0 - ease_t)

                # Apply offset with sphere index multiplier (tip moves more)
                self.entity.position = self.base_position + offset

                # Pulse scale during strike
                if 0.2 <= attack_progress < 0.6:
                    scale_pulse = 1.0 + pulse_amount * 0.5 * ease_t
                else:
                    scale_pulse = 1.0
                self.entity.scale = self.size * scale_pulse
        else:
            # Idle animation: wave pulse along spine
            pulse_wave = math.sin(time * anim_speed + sphere_phase_offset)
            scale_pulse = 1.0 + pulse_amount * pulse_wave * 0.5
            self.entity.scale = self.size * scale_pulse

            # Gentle sway
            sway_x = math.sin(time * anim_speed * 0.5 + sphere_phase_offset) * 0.05
            sway_z = math.cos(time * anim_speed * 0.5 + sphere_phase_offset * 1.3) * 0.05
            self.entity.position = self.base_position + Vec3(sway_x, 0, sway_z)

        # Update connector tube
        self._update_connector_tube_transform()

        # Animate tentacles
        for tentacle in self.tentacles:
            if is_attacking:
                tentacle.update_animation(
                    time, anim_speed, 0.05,
                    is_attacking=True,
                    attack_start_time=time - attack_progress * 1.2,
                    camera_position=camera_position
                )
            else:
                tentacle.update_animation(time, anim_speed, 0.05)

    def destroy(self):
        """Cleanup sphere entity, connector tube, and tentacles."""
        for tentacle in self.tentacles:
            tentacle.destroy()
        if self.connector_tube is not None:
            destroy(self.connector_tube)
        destroy(self.entity)


class PolypCreature:
    """Creature made of segmented spine with spheres and tentacles."""

    def __init__(self, num_spheres=4, algorithm='bezier', algorithm_params=None,
                 base_sphere_size=0.8, tentacles_per_sphere=(8, 6, 5, 4),
                 segments_per_tentacle=12, thickness_base=0.2, taper_factor=0.6,
                 spine_color=(0.6, 0.3, 0.7), curve_intensity=0.4,
                 anim_speed=2.0, pulse_amount=0.08):
        """
        Create a polyp chain creature.

        Args:
            num_spheres: Number of spheres in chain (3-5)
            algorithm: Spine curve algorithm ('bezier' or 'fourier')
            algorithm_params: Algorithm-specific parameters for tentacles
            base_sphere_size: Size of root sphere (others scale by golden ratio)
            tentacles_per_sphere: Tuple of tentacle counts per sphere (or single int)
            segments_per_tentacle: Segments per tentacle
            thickness_base: Base tentacle thickness
            taper_factor: Tentacle taper factor
            spine_color: Base color for spine (RGB tuple 0-1)
            curve_intensity: How much the spine curves (0-1)
            anim_speed: Animation speed
            pulse_amount: Pulse intensity
        """
        # Create root entity
        self.root = Entity(position=(0, 0, 0))
        self.spheres = []
        self.curve_points = []

        # Store parameters
        self.num_spheres = num_spheres
        self.spine_algorithm = algorithm
        self.tentacle_algorithm = algorithm
        self.algorithm_params = algorithm_params or {}
        self.base_sphere_size = base_sphere_size
        self.tentacles_per_sphere = tentacles_per_sphere if isinstance(tentacles_per_sphere, (list, tuple)) else [tentacles_per_sphere] * num_spheres
        self.segments_per_tentacle = segments_per_tentacle
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor
        self.spine_color = spine_color
        self.curve_intensity = curve_intensity
        self.anim_speed = anim_speed
        self.pulse_amount = pulse_amount

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0

        # Create toon shader (shared across all parts)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in PolypCreature, using default rendering")

        # Generate creature
        self._generate_spine()

    def _generate_spine(self):
        """Generate spine curve and spheres with tentacles."""
        # Clear existing spheres
        for sphere in self.spheres:
            sphere.destroy()
        self.spheres.clear()

        # Generate spine curve (vertical S-curve or droop)
        start_point = Vec3(0, 0.5, 0)  # Top of spine
        end_point = Vec3(0, -1.5, 0)  # Bottom of spine

        # Add curve intensity for more interesting spine shapes
        if self.spine_algorithm == 'bezier':
            # Use bezier with control points offset for S-curve
            self.curve_points = bezier_curve(
                start_point, end_point, self.num_spheres,
                control_strength=self.curve_intensity
            )
        else:
            # Use fourier for wavy spine
            self.curve_points = fourier_curve(
                start_point, end_point, self.num_spheres,
                num_waves=2,
                amplitude=self.curve_intensity * 0.3
            )

        # Create spheres at curve points
        for i in range(self.num_spheres):
            position = self.curve_points[i]

            # Size decreases by golden ratio
            size = self.base_sphere_size / (GOLDEN_RATIO ** i)

            # Color variation along spine (darker toward tip)
            color_factor = 1.0 - (i / self.num_spheres) * 0.3
            sphere_color = (
                self.spine_color[0] * color_factor,
                self.spine_color[1] * color_factor,
                self.spine_color[2] * color_factor
            )

            # Create sphere
            parent_sphere = self.spheres[i - 1] if i > 0 else None
            sphere = PolypSphere(
                position=position,
                size=size,
                base_color=sphere_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                sphere_index=i,
                parent_sphere=parent_sphere
            )

            self.spheres.append(sphere)

            # Create tentacles for this sphere
            num_tentacles = self.tentacles_per_sphere[i] if i < len(self.tentacles_per_sphere) else 4

            # Use the configured segments_per_tentacle parameter
            sphere.create_tentacles(
                num_tentacles=num_tentacles,
                segments_per_tentacle=self.segments_per_tentacle,
                algorithm=self.tentacle_algorithm,
                algorithm_params=self.algorithm_params,
                thickness_base=self.thickness_base / (1 + i * 0.2),  # Thinner tentacles on smaller spheres
                taper_factor=self.taper_factor,
                scene_parent=self.root,
                toon_shader=self.toon_shader
            )

    def rebuild(self, num_spheres, algorithm, algorithm_params, base_sphere_size,
                tentacles_per_sphere, segments_per_tentacle, thickness_base, taper_factor,
                spine_color, curve_intensity, anim_speed, pulse_amount):
        """
        Rebuild polyp with new parameters.

        Args:
            num_spheres: Number of spheres in chain
            algorithm: Curve algorithm
            algorithm_params: Algorithm parameters
            base_sphere_size: Root sphere size
            tentacles_per_sphere: Tentacle count per sphere
            segments_per_tentacle: Segments per tentacle
            thickness_base: Base tentacle thickness
            taper_factor: Tentacle taper
            spine_color: Base color
            curve_intensity: Spine curve amount
            anim_speed: Animation speed
            pulse_amount: Pulse intensity
        """
        self.num_spheres = num_spheres
        self.spine_algorithm = algorithm
        self.tentacle_algorithm = algorithm
        self.algorithm_params = algorithm_params
        self.base_sphere_size = base_sphere_size
        self.tentacles_per_sphere = tentacles_per_sphere if isinstance(tentacles_per_sphere, (list, tuple)) else [tentacles_per_sphere] * num_spheres
        self.segments_per_tentacle = segments_per_tentacle
        self.thickness_base = thickness_base
        self.taper_factor = taper_factor
        self.spine_color = spine_color
        self.curve_intensity = curve_intensity
        self.anim_speed = anim_speed
        self.pulse_amount = pulse_amount

        # Regenerate spine
        self._generate_spine()

    def start_attack(self, camera_position):
        """Start attack animation."""
        self.is_attacking = True
        self.attack_start_time = 0

    def start_attack_2(self, camera_position):
        """Start attack 2 animation (same as attack 1 for polyp)."""
        self.start_attack(camera_position)

    def update_animation(self, time, camera_position=None):
        """
        Update polyp animation.

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
            attack_elapsed = time - self.attack_start_time
            attack_duration = 1.2
            attack_progress = min(attack_elapsed / attack_duration, 1.0)

            if attack_progress >= 1.0:
                # Attack complete
                self.is_attacking = False
                self.attack_start_time = 0

        # Animate spheres with wave pattern along spine
        for i, sphere in enumerate(self.spheres):
            # Phase offset for wave propagation (root → tip)
            phase_offset = i * (math.pi * 2 / len(self.spheres))

            sphere.update_animation(
                time=time,
                anim_speed=self.anim_speed,
                pulse_amount=self.pulse_amount,
                sphere_phase_offset=phase_offset,
                is_attacking=self.is_attacking,
                attack_progress=attack_progress,
                camera_position=camera_position
            )

    def destroy(self):
        """Cleanup all sphere entities."""
        for sphere in self.spheres:
            sphere.destroy()
        destroy(self.root)
