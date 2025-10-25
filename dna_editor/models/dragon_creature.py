"""
DragonCreature model - Space Harrier inspired segmented flying serpent.
Chain of spheres forming a snake-like body with smooth weaving/bobbing animation.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .eye import Eye
from .dragon_particles import FireParticle
from .dragon_components import DragonSegment, DragonHorn, DragonSpike, DragonWhisker


class DragonCreature:
    """Space Harrier inspired dragon - segmented serpent with weaving/bobbing motion."""

    def __init__(self, num_segments=15, segment_thickness=0.3, taper_factor=0.6,
                 head_scale=3.0, body_color=(200, 40, 40), head_color=(255, 200, 50),
                 weave_amplitude=0.5, bob_amplitude=0.3, anim_speed=1.5,
                 num_eyes=2, eye_size=0.15, eyeball_color=(255, 200, 50), pupil_color=(20, 0, 0),
                 mouth_size=0.25, mouth_color=(20, 0, 0),
                 num_whiskers_per_side=2, whisker_segments=4, whisker_thickness=0.05,
                 spine_spike_color=(100, 20, 20)):
        """
        Create a dragon creature.

        Args:
            num_segments: Number of body segments (5-30)
            segment_thickness: Base segment size (0.1-0.8)
            taper_factor: Size reduction toward tail (0.0-0.9, higher = more taper)
            head_scale: Head size multiplier (1.0-3.5)
            body_color: RGB tuple for body (0-255 range - Ursina compat)
            head_color: RGB tuple for head (0-255 range)
            weave_amplitude: Side-to-side motion intensity (0.0-1.0)
            bob_amplitude: Up-down motion intensity (0.0-1.0)
            anim_speed: Animation speed multiplier (0.5-5.0)
            num_eyes: Number of eyes on head (0-8)
            eye_size: Size of each eye (0.05-0.3)
            eyeball_color: RGB tuple for eyeball (0-255 range)
            pupil_color: RGB tuple for pupil (0-255 range)
            mouth_size: Size of mouth cavity sphere (0.1-0.5)
            mouth_color: RGB tuple for mouth cavity (0-255 range)
            num_whiskers_per_side: Number of whiskers on each side (0-3)
            whisker_segments: Segments per whisker (3-6)
            whisker_thickness: Base whisker thickness (0.03-0.08)
            spine_spike_color: RGB tuple for spine spikes (0-255 range)
        """
        # Create root entity
        self.root = Entity(position=(0, 0, 0))
        self.segments = []
        self.eyes = []
        self.eye_offsets = []  # Vec3 offsets from head center for each eye
        self.whiskers = []  # Dragon whiskers
        self.horns = []  # Dragon horns
        self.spikes = []  # Spine spikes (one per body segment)
        self.mouth_sphere = None
        self.fire_particles = []  # Active fire particles

        # Store parameters
        self.num_segments = num_segments
        self.segment_thickness = segment_thickness
        self.taper_factor = taper_factor
        self.head_scale = head_scale
        # Convert RGB 0-255 to 0-1 for Ursina
        self.body_color = (body_color[0] / 255.0, body_color[1] / 255.0, body_color[2] / 255.0)
        self.head_color = (head_color[0] / 255.0, head_color[1] / 255.0, head_color[2] / 255.0)
        self.weave_amplitude = weave_amplitude
        self.bob_amplitude = bob_amplitude
        self.anim_speed = anim_speed
        self.num_eyes = num_eyes
        self.eye_size = eye_size
        self.eyeball_color = (eyeball_color[0] / 255.0, eyeball_color[1] / 255.0, eyeball_color[2] / 255.0)
        self.pupil_color = (pupil_color[0] / 255.0, pupil_color[1] / 255.0, pupil_color[2] / 255.0)
        self.mouth_size = mouth_size
        self.mouth_color = (mouth_color[0] / 255.0, mouth_color[1] / 255.0, mouth_color[2] / 255.0)
        self.num_whiskers_per_side = num_whiskers_per_side
        self.whisker_segments = whisker_segments
        self.whisker_thickness = whisker_thickness
        self.spine_spike_color = (spine_spike_color[0] / 255.0, spine_spike_color[1] / 255.0, spine_spike_color[2] / 255.0)

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0

        # Random phase offset for organic variation
        self.phase_offset = random.random() * math.pi * 2

        # Create toon shaders (shared across all parts)
        from ..shaders import create_toon_shader, create_toon_shader_lite
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in DragonCreature, using default rendering")

        self.toon_shader_lite = create_toon_shader_lite()
        if self.toon_shader_lite is None:
            print("WARNING: Lite toon shader creation failed in DragonCreature, will use full shader")

        # Generate dragon body
        self._generate_dragon()

    def _generate_dragon(self):
        """Generate dragon body as chain of spheres."""
        # Clear existing segments
        for segment in self.segments:
            segment.destroy()
        self.segments.clear()

        # Dragon layout: horizontal chain extending forward
        # Segments arranged along +Z axis (head at origin, tail extends forward)
        segment_spacing = self.segment_thickness * 1.8  # Spacing between segment centers

        # Elevation (floating/hovering effect)
        base_elevation = 1.0

        previous_segment = None

        # Golden ratio for natural tapering
        PHI = 1.618033988749895

        for i in range(self.num_segments):
            # Calculate position along chain
            # Head (i=0) at front, tail (i=max) at front
            z_offset = i * segment_spacing
            x_offset = 0  # No initial X offset (weaving happens in animation)
            y_offset = base_elevation  # Floating height

            position = Vec3(x_offset, y_offset, z_offset)

            # Calculate size with golden ratio tapering
            # Head is largest, body tapers using golden ratio
            if i == 0:
                # Head segment
                segment_size = self.segment_thickness * self.head_scale
            else:
                # Body segments: golden ratio tapering from head to tail
                # Each segment is smaller than the previous by a factor approaching 1/PHI
                # taper_factor controls how aggressively we apply the golden taper

                # Start from head size and apply golden ratio reduction
                # Use blend between full taper (PHI reduction) and no taper (constant size)
                # taper_factor=0 → no tapering (constant size)
                # taper_factor=1 → full golden ratio tapering

                # Calculate the "ideal" size if we were purely using golden ratio
                # Starting from head size: head_size / (PHI ^ i)
                head_size = self.segment_thickness * self.head_scale
                golden_size = head_size / (PHI ** i)

                # Blend between head size (no taper) and golden size (full taper)
                segment_size = head_size * (1.0 - self.taper_factor) + golden_size * self.taper_factor

                # Apply minimum size constraint
                segment_size = max(segment_size, 0.1)  # Minimum size

            # Color: head uses head_color, body uses body_color with gradient
            if i == 0:
                segment_color = self.head_color
            else:
                # Gradual transition from head_color to body_color over first few segments
                if i < 3:
                    blend = i / 3.0
                    segment_color = (
                        self.head_color[0] * (1 - blend) + self.body_color[0] * blend,
                        self.head_color[1] * (1 - blend) + self.body_color[1] * blend,
                        self.head_color[2] * (1 - blend) + self.body_color[2] * blend
                    )
                else:
                    # Slight darkening toward tail for depth
                    darkness_factor = 1.0 - (i / self.num_segments) * 0.3
                    segment_color = (
                        self.body_color[0] * darkness_factor,
                        self.body_color[1] * darkness_factor,
                        self.body_color[2] * darkness_factor
                    )

            # Create segment with shared shaders
            segment = DragonSegment(
                segment_index=i,
                total_segments=self.num_segments,
                position=position,
                size=segment_size,
                segment_color=segment_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                toon_shader_lite=self.toon_shader_lite,
                previous_segment=previous_segment
            )

            self.segments.append(segment)
            previous_segment = segment

        # Create eyes on head segment
        self._create_eyes()

        # Create mouth on head segment
        self._create_mouth()

        # Create whiskers on head segment
        self._create_whiskers()

        # Create horns on head segment
        self._create_horns()

        # Create spine spikes on body segments
        self._create_spines()

    def _create_eyes(self):
        """Create eyes on the dragon's head segment."""
        # Clear existing eyes and offsets
        for eye in self.eyes:
            eye.destroy()
        self.eyes.clear()
        self.eye_offsets.clear()

        if self.num_eyes == 0 or len(self.segments) == 0:
            return

        # Get head segment (first segment)
        head_segment = self.segments[0]
        head_position = head_segment.base_position
        # Ursina sphere: scale=X means radius=X/2 (default sphere has diameter 1)
        head_radius = head_segment.size / 2

        # Position eyes on the front of the head sphere using proper spherical coordinates
        # Dragon faces in -Z direction (forward)
        # Adjust eye elevation based on mouth size to prevent overlap
        # Larger mouths push eyes higher on the head
        eye_elevation_adjustment = self.mouth_size * 0.3  # 0-0.15 for mouth_size 0-0.5

        for i in range(self.num_eyes):
            if self.num_eyes == 1:
                # Single eye: center of head front, elevated above mouth
                # Spherical coords: theta=0 (front), phi adjusted for mouth
                theta = 0  # Azimuthal angle (around Y axis)
                phi = math.pi / 2 - eye_elevation_adjustment  # Elevated based on mouth size
            elif self.num_eyes == 2:
                # Two eyes: symmetrical left/right on front of head
                # Position at ±30° from center, elevated above mouth
                theta = (math.pi / 6) if i == 0 else (-math.pi / 6)  # ±30° left/right
                phi = math.pi * 0.45 - eye_elevation_adjustment  # Elevated based on mouth size
            else:
                # Multiple eyes: distribute in a ring on front hemisphere
                # Ring around the front of the head, elevated above mouth
                ring_angle = (i / self.num_eyes) * math.pi * 2  # 0 to 360°
                # Position eyes in a cone pointing forward
                theta = math.sin(ring_angle) * (math.pi / 4)  # ±45° max
                phi = math.pi / 2 - math.cos(ring_angle) * (math.pi / 6) - eye_elevation_adjustment

            # Convert spherical to Cartesian coordinates on unit sphere
            # Standard spherical coordinates: x = sin(phi)*cos(theta), y = cos(phi), z = sin(phi)*sin(theta)
            # But we want front to be -Z, so we rotate the coordinate system
            x_normalized = math.sin(phi) * math.sin(theta)  # Left/right
            y_normalized = math.cos(phi)  # Up/down
            z_normalized = -math.sin(phi) * math.cos(theta)  # Front/back (negative for front)

            # Calculate eye offset from head center (0.9 to keep eyes slightly inside sphere edge)
            eye_offset = Vec3(
                x_normalized * head_radius * 0.9,
                y_normalized * head_radius * 0.9,
                z_normalized * head_radius * 0.9
            )
            eye_position = head_position + eye_offset

            # Create eye with shared shaders
            eye = Eye(
                position=eye_position,
                size=self.eye_size,
                eyeball_color=self.eyeball_color,
                pupil_color=self.pupil_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                toon_shader_lite=self.toon_shader_lite
            )

            self.eyes.append(eye)
            self.eye_offsets.append(eye_offset)  # Store offset for animation updates

    def _create_mouth(self):
        """Create mouth cavity sphere on the dragon's head segment."""
        # Destroy existing mouth if it exists
        if self.mouth_sphere is not None:
            destroy(self.mouth_sphere)
            self.mouth_sphere = None

        if len(self.segments) == 0:
            return

        # Get head segment
        head_segment = self.segments[0]
        head_position = head_segment.base_position
        head_radius = head_segment.size / 2

        # Position mouth at front center of head (where snout would be)
        # Mouth faces -Z direction (forward)
        mouth_offset_z = -head_radius * 0.7  # 70% forward on head
        mouth_offset_y = -head_radius * 0.2  # Slightly below center (bottom jaw area)

        mouth_position = head_position + Vec3(0, mouth_offset_y, mouth_offset_z)

        # Calculate mouth size relative to head
        mouth_scale = self.mouth_size * head_radius * 2.0

        # Create dark mouth cavity sphere
        mouth_params = {
            'model': 'sphere',
            'color': color.rgb(*self.mouth_color),
            'position': mouth_position,
            'scale': mouth_scale,
            'parent': self.root
        }

        if self.toon_shader is not None:
            mouth_params['shader'] = self.toon_shader

        self.mouth_sphere = Entity(**mouth_params)
        # Store base scale for animation
        self.mouth_sphere.base_scale = mouth_scale
        self.mouth_sphere.base_position = mouth_position

    def _create_whiskers(self):
        """Create whiskers on the dragon's head segment (lower front sides)."""
        # Clear existing whiskers
        for whisker in self.whiskers:
            whisker.destroy()
        self.whiskers.clear()

        if self.num_whiskers_per_side == 0 or len(self.segments) == 0:
            return

        # Get head segment
        head_segment = self.segments[0]
        head_position = head_segment.base_position
        head_radius = head_segment.size / 2

        # Whisker color: slightly darker than head
        whisker_color = (
            self.head_color[0] * 0.9,
            self.head_color[1] * 0.9,
            self.head_color[2] * 0.9
        )

        # Golden angle for natural spacing of multiple whiskers
        from ..core.constants import GOLDEN_ANGLE

        # Create whiskers on both sides (left and right)
        for side_idx, side_sign in enumerate([1, -1]):  # 1 = left, -1 = right
            for whisker_idx in range(self.num_whiskers_per_side):
                # Calculate anchor position using spherical coordinates
                # Lower jaw area: phi = 100-110 degrees (below equator)
                # Side spread: theta = 40-70 degrees using golden angle

                if self.num_whiskers_per_side == 1:
                    # Single whisker: center of side
                    theta_degrees = 55  # Middle of 40-70 range
                else:
                    # Multiple whiskers: golden angle distribution
                    # Spread from 40° to 70° (30° range)
                    base_theta = 40
                    theta_range = 30
                    golden_offset = (whisker_idx * GOLDEN_ANGLE * 180 / math.pi) % theta_range
                    theta_degrees = base_theta + golden_offset

                # Convert to radians
                theta = math.radians(theta_degrees) * side_sign
                phi = math.radians(105)  # Lower face (105° from +Y axis)

                # Convert spherical to Cartesian on head surface
                x_normalized = math.sin(phi) * math.sin(theta)
                y_normalized = math.cos(phi)
                z_normalized = -math.sin(phi) * math.cos(theta)

                # Anchor point on head surface
                anchor_offset = Vec3(
                    x_normalized * head_radius * 0.85,
                    y_normalized * head_radius * 0.85,
                    z_normalized * head_radius * 0.85
                )
                anchor_point = head_position + anchor_offset

                # Calculate target point (whisker tip)
                # Extends downward, backward, and slightly outward
                target_offset = Vec3(
                    x_normalized * 0.4,  # Outward following anchor direction
                    -0.6,  # Downward
                    0.4   # Backward (positive Z in dragon coords)
                )
                target_point = anchor_point + target_offset

                # Random phase for animation variety
                phase_offset = random.random() * math.pi * 2

                # Create whisker with shared shaders
                whisker = DragonWhisker(
                    anchor_point=anchor_point,
                    target_point=target_point,
                    num_segments=self.whisker_segments,
                    base_thickness=self.whisker_thickness,
                    whisker_color=whisker_color,
                    parent=self.root,
                    toon_shader=self.toon_shader,
                    toon_shader_lite=self.toon_shader_lite,
                    phase_offset=phase_offset
                )

                self.whiskers.append(whisker)

    def _create_horns(self):
        """Create horns on the dragon's head segment (top sides, pointing backward and upward)."""
        # Clear existing horns
        for horn in self.horns:
            horn.destroy()
        self.horns.clear()

        if len(self.segments) == 0:
            return

        # Get head segment
        head_segment = self.segments[0]
        head_position = head_segment.base_position
        head_radius = head_segment.size / 2

        # Horn color: slightly darker than head for contrast
        horn_color = (
            self.head_color[0] * 0.85,
            self.head_color[1] * 0.85,
            self.head_color[2] * 0.85
        )

        # Golden ratio for sizing
        PHI = 1.618033988749895

        # Horn base thickness relative to head size (using golden ratio)
        horn_base_thickness = head_radius / PHI  # ≈ 0.618 of head radius

        # Create 2 horns (left and right) positioned on top-sides of head
        for side_idx, side_sign in enumerate([1, -1]):  # 1 = left, -1 = right
            # Horn position using spherical coordinates
            # Top-side of head: theta = ±60° from center (left/right)
            #                   phi = 30° from top (upper sides)
            theta_degrees = 60 * side_sign  # 60° left or right
            phi_degrees = 30  # 30° from top (upper head)

            # Convert to radians
            theta = math.radians(theta_degrees)
            phi = math.radians(phi_degrees)

            # Convert spherical to Cartesian on head surface
            x_normalized = math.sin(phi) * math.sin(theta)
            y_normalized = math.cos(phi)  # Positive Y is up
            z_normalized = -math.sin(phi) * math.cos(theta)  # Negative Z is forward

            # Anchor point on head surface
            anchor_offset = Vec3(
                x_normalized * head_radius * 0.90,
                y_normalized * head_radius * 0.90,
                z_normalized * head_radius * 0.90
            )
            anchor_point = head_position + anchor_offset

            # Calculate target point (horn tip)
            # Horns curve backward and upward from anchor
            # Use golden ratio for horn length
            horn_length = head_radius * PHI  # Length proportional to head size

            # Target direction: upward and backward
            target_direction = Vec3(
                x_normalized * 0.3,  # Slight outward flare
                0.8,  # Mostly upward
                0.6  # Backward (positive Z in dragon coords)
            ).normalized()

            target_point = anchor_point + target_direction * horn_length

            # Create horn with 3 segments and shared shaders
            horn = DragonHorn(
                anchor_point=anchor_point,
                target_point=target_point,
                num_segments=3,  # As requested: 3 segments
                base_thickness=horn_base_thickness,
                horn_color=horn_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                toon_shader_lite=self.toon_shader_lite
            )

            self.horns.append(horn)

    def _create_spines(self):
        """Create spine spikes along dragon's back (one per body segment, excluding head)."""
        # Clear existing spikes
        for spike in self.spikes:
            spike.destroy()
        self.spikes.clear()

        if len(self.segments) <= 1:  # Need at least 2 segments (head + 1 body)
            return

        total_segments = len(self.segments)

        # Create one spike per body segment (skip head segment at i=0)
        for i in range(1, len(self.segments)):
            segment = self.segments[i]
            segment_position = segment.base_position
            segment_size = segment.size

            # Anchor point on top of segment (positive Y direction)
            # Position spike at segment's top surface
            anchor_offset = Vec3(0, segment_size / 2, 0)
            anchor_point = segment_position + anchor_offset

            # Create spike with tail tapering and shared shaders
            spike = DragonSpike(
                anchor_point=anchor_point,
                segment_size=segment_size,
                spike_color=self.spine_spike_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                toon_shader_lite=self.toon_shader_lite,
                segment_index=i,
                total_segments=total_segments
            )

            self.spikes.append(spike)

    def rebuild(self, num_segments, segment_thickness, taper_factor, head_scale,
                body_color, head_color, weave_amplitude, bob_amplitude, anim_speed,
                num_eyes=2, eye_size=0.15, eyeball_color=(255, 200, 50), pupil_color=(20, 0, 0),
                mouth_size=0.25, mouth_color=(20, 0, 0),
                num_whiskers_per_side=2, whisker_segments=4, whisker_thickness=0.05,
                spine_spike_color=(100, 20, 20)):
        """
        Rebuild dragon with new parameters.

        Args:
            num_segments: Number of segments
            segment_thickness: Base thickness
            taper_factor: Tail tapering amount
            head_scale: Head size multiplier
            body_color: Body RGB (0-255)
            head_color: Head RGB (0-255)
            weave_amplitude: Weaving intensity
            bob_amplitude: Bobbing intensity
            anim_speed: Animation speed
            num_eyes: Number of eyes on head (0-8)
            eye_size: Size of each eye (0.05-0.3)
            eyeball_color: Eyeball RGB (0-255)
            pupil_color: Pupil RGB (0-255)
            mouth_size: Size of mouth cavity sphere (0.1-0.5)
            mouth_color: Mouth cavity RGB (0-255)
            num_whiskers_per_side: Number of whiskers on each side (0-3)
            whisker_segments: Segments per whisker (3-6)
            whisker_thickness: Base whisker thickness (0.03-0.08)
            spine_spike_color: RGB tuple for spine spikes (0-255 range)
        """
        self.num_segments = num_segments
        self.segment_thickness = segment_thickness
        self.taper_factor = taper_factor
        self.head_scale = head_scale
        self.body_color = (body_color[0] / 255.0, body_color[1] / 255.0, body_color[2] / 255.0)
        self.head_color = (head_color[0] / 255.0, head_color[1] / 255.0, head_color[2] / 255.0)
        self.weave_amplitude = weave_amplitude
        self.bob_amplitude = bob_amplitude
        self.anim_speed = anim_speed
        self.num_eyes = num_eyes
        self.eye_size = eye_size
        self.eyeball_color = (eyeball_color[0] / 255.0, eyeball_color[1] / 255.0, eyeball_color[2] / 255.0)
        self.pupil_color = (pupil_color[0] / 255.0, pupil_color[1] / 255.0, pupil_color[2] / 255.0)
        self.mouth_size = mouth_size
        self.mouth_color = (mouth_color[0] / 255.0, mouth_color[1] / 255.0, mouth_color[2] / 255.0)
        self.num_whiskers_per_side = num_whiskers_per_side
        self.whisker_segments = whisker_segments
        self.whisker_thickness = whisker_thickness
        self.spine_spike_color = (spine_spike_color[0] / 255.0, spine_spike_color[1] / 255.0, spine_spike_color[2] / 255.0)

        # Regenerate dragon
        self._generate_dragon()

    def start_attack(self, camera_position):
        """Start attack animation (coil + strike)."""
        self.is_attacking = True
        self.attack_start_time = 0

    def update_animation(self, time, camera_position=None):
        """
        Update dragon animation with weaving/bobbing motion.

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
            from ..core.constants import DRAGON_ATTACK_DURATION
            attack_elapsed = time - self.attack_start_time
            attack_progress = min(attack_elapsed / DRAGON_ATTACK_DURATION, 1.0)

            if attack_progress >= 1.0:
                # Attack complete
                self.is_attacking = False
                self.attack_start_time = 0

        # Animate each segment
        for segment in self.segments:
            i = segment.segment_index

            if self.is_attacking and attack_progress < 1.0:
                # Attack animation: coil inward → strike forward
                if attack_progress < 0.4:
                    # Coil phase (0.0 - 0.4): compress segments together
                    phase_t = attack_progress / 0.4
                    ease_t = phase_t * phase_t  # Ease-in

                    # Pull segments toward head (Z moves toward 0)
                    coil_offset_z = (segment.base_position.z * 0.5) * ease_t
                    # Add spiral motion during coil
                    spiral_x = math.sin(i * 0.5 + time * 3) * 0.3 * ease_t
                    spiral_y = math.cos(i * 0.5 + time * 3) * 0.2 * ease_t

                    segment.entity.position = segment.base_position + Vec3(
                        spiral_x,
                        spiral_y,
                        -coil_offset_z
                    )

                elif attack_progress < 0.7:
                    # Strike phase (0.4 - 0.7): extend forward rapidly
                    phase_t = (attack_progress - 0.4) / 0.3
                    ease_t = 1.0 - (1.0 - phase_t) ** 3  # Ease-out cubic

                    # Extend forward (positive Z direction)
                    strike_offset_z = ease_t * 2.0
                    # Segments follow in wave
                    wave_delay = i * 0.1
                    delayed_t = max(0, ease_t - wave_delay)

                    segment.entity.position = segment.base_position + Vec3(
                        0,
                        0,
                        strike_offset_z * delayed_t
                    )

                else:
                    # Return phase (0.7 - 1.0): snap back to original positions
                    phase_t = (attack_progress - 0.7) / 0.3
                    ease_t = 1.0 - (1.0 - phase_t) ** 2  # Ease-out quad

                    # Interpolate back to base position
                    strike_offset_z = 2.0 * (1.0 - ease_t)
                    segment.entity.position = segment.base_position + Vec3(0, 0, strike_offset_z)

            else:
                # Idle animation: weaving (X) and bobbing (Y) waves
                # Head stays stable, motion increases toward tail

                # Position along body (0 = head, 1 = tail tip)
                body_t = i / max(self.num_segments - 1, 1)

                # Motion multiplier: head barely moves, tail moves fully
                # Using quadratic curve: head (0) = 0.0, mid = 0.5, tail (1) = 1.5
                motion_multiplier = body_t ** 1.8 * 1.5

                # Wave propagates along body (each segment phase-delayed)
                wave_phase = time * self.anim_speed + self.phase_offset + i * 0.3

                # Weaving (left-right motion)
                weave_offset_x = math.sin(wave_phase) * self.weave_amplitude * 0.8
                # Additional secondary wave for organic motion
                weave_offset_x += math.sin(wave_phase * 1.5 + 1.0) * self.weave_amplitude * 0.3

                # Bobbing (up-down motion)
                bob_offset_y = math.cos(wave_phase * 1.2) * self.bob_amplitude * 0.5
                # Secondary bob wave
                bob_offset_y += math.sin(wave_phase * 0.7 - 0.5) * self.bob_amplitude * 0.2

                # Apply motion multiplier (head stays stable, tail whips)
                weave_offset_x *= motion_multiplier
                bob_offset_y *= motion_multiplier

                # Head floating: slow, gentle up-down motion for head and front segments
                # Inverse of motion_multiplier - strong at head, fades toward tail
                head_float_strength = (1.0 - body_t) ** 2  # Strong at head, zero at tail
                head_float_y = math.sin(time * 0.8 + self.phase_offset) * 0.15 * head_float_strength

                # Apply animation offset
                segment.entity.position = segment.base_position + Vec3(
                    weave_offset_x,
                    bob_offset_y + head_float_y,
                    0
                )

            # Update connector tube to follow segment
            segment.update_connector_tube()

        # Update eye positions to follow head movement
        if len(self.segments) > 0 and len(self.eyes) > 0 and len(self.eye_offsets) > 0:
            head_segment = self.segments[0]
            head_position = head_segment.base_position
            head_anim_offset = head_segment.entity.position - head_segment.base_position

            for i, (eye, eye_offset) in enumerate(zip(self.eyes, self.eye_offsets)):
                # Calculate animated eye position using stored offset
                animated_eye_position = head_position + eye_offset + head_anim_offset

                # Update eyeball position
                eye.eyeball.position = animated_eye_position
                eye.eyeball_base_position = animated_eye_position

                # Calculate surface normal from offset vector (points outward from head center)
                surface_normal = eye_offset.normalized()
                pupil_offset = surface_normal * (eye.base_size * 0.5)
                eye.pupil.position = animated_eye_position + pupil_offset
                eye.pupil_base_position = animated_eye_position + pupil_offset

                # Update eye animation (blinking)
                eye.update_animation(time)

        # Update mouth position and animation
        if self.mouth_sphere is not None and len(self.segments) > 0:
            head_segment = self.segments[0]
            head_anim_offset = head_segment.entity.position - head_segment.base_position

            # Update mouth position to follow head
            self.mouth_sphere.position = self.mouth_sphere.base_position + head_anim_offset

            # Animate mouth scale during attack
            if self.is_attacking and attack_progress < 1.0:
                if attack_progress < 0.4:
                    # Coil phase: mouth stays closed
                    self.mouth_sphere.scale = self.mouth_sphere.base_scale
                elif attack_progress < 0.7:
                    # Strike phase: mouth opens (scale up)
                    phase_t = (attack_progress - 0.4) / 0.3
                    ease_t = 1.0 - (1.0 - phase_t) ** 2  # Ease-out quad for snap open
                    mouth_open_scale = self.mouth_sphere.base_scale * (1.0 + ease_t * 1.2)  # Opens to 2.2x size
                    self.mouth_sphere.scale = mouth_open_scale
                else:
                    # Return phase: mouth closes (scale back down)
                    phase_t = (attack_progress - 0.7) / 0.3
                    ease_t = phase_t * phase_t  # Ease-in quad for slow close
                    mouth_open_scale = self.mouth_sphere.base_scale * (1.0 + (1.0 - ease_t) * 1.2)
                    self.mouth_sphere.scale = mouth_open_scale
            else:
                # Idle: mouth stays at base size
                self.mouth_sphere.scale = self.mouth_sphere.base_scale

        # Update whisker positions and animation
        if len(self.whiskers) > 0 and len(self.segments) > 0:
            head_segment = self.segments[0]
            # Get current head position (including animation offset)
            current_head_position = head_segment.entity.position

            for whisker in self.whiskers:
                whisker.update_animation(time, current_head_position)

        # Update horn positions to follow head movement
        if len(self.horns) > 0 and len(self.segments) > 0:
            head_segment = self.segments[0]
            # Get current head position (including animation offset)
            current_head_position = head_segment.entity.position

            for horn in self.horns:
                horn.update_animation(time, current_head_position)

        # Update spine spike positions to follow body segment movement
        if len(self.spikes) > 0 and len(self.segments) > 1:
            # Each spike corresponds to a body segment (skip head at i=0)
            for i, spike in enumerate(self.spikes):
                # Spike i corresponds to segment i+1 (since we skip the head)
                segment_index = i + 1
                if segment_index < len(self.segments):
                    segment = self.segments[segment_index]
                    # Get current segment position (including animation offset)
                    current_segment_position = segment.entity.position
                    spike.update_animation(time, current_segment_position)

        # Update and spawn fire particles during attack strike phase
        if self.is_attacking and attack_progress >= 0.4 and attack_progress < 0.7:
            # Spawn fire particles during strike phase (peak spawning at 0.5-0.6)
            phase_t = (attack_progress - 0.4) / 0.3

            # Spawn rate peaks in middle of strike
            spawn_intensity = 1.0 - abs(phase_t - 0.5) * 2  # 0 at edges, 1 at center

            # Spawn 0-5 particles per frame based on intensity
            if random.random() < spawn_intensity * 0.8:  # 80% chance at peak
                num_particles = random.randint(2, 5)

                for _ in range(num_particles):
                    if self.mouth_sphere is not None and len(self.segments) > 0:
                        # Spawn particle at mouth position
                        spawn_position = Vec3(self.mouth_sphere.position)

                        # Calculate forward direction (dragon faces -Z)
                        forward_dir = Vec3(0, 0, -1)

                        # Use golden angle for natural cone distribution
                        from ..core.constants import GOLDEN_ANGLE
                        particle_index = len(self.fire_particles)
                        spiral_angle = particle_index * GOLDEN_ANGLE

                        # Cone spread (30 degrees max)
                        cone_radius = random.uniform(0.0, 0.5)  # 0-0.5 radians (~28 degrees)
                        cone_x = math.cos(spiral_angle) * cone_radius
                        cone_y = math.sin(spiral_angle) * cone_radius

                        # Calculate velocity with cone spread
                        velocity_magnitude = random.uniform(3.0, 5.0)
                        velocity = Vec3(
                            forward_dir.x + cone_x,
                            forward_dir.y + cone_y,
                            forward_dir.z
                        ).normalized() * velocity_magnitude

                        # Fire particle color (bright yellow-orange)
                        particle_color = (
                            1.0,  # Full red
                            random.uniform(0.6, 0.9),  # Orange-yellow
                            random.uniform(0.0, 0.2)   # Minimal blue
                        )

                        # Create particle
                        lifetime = random.uniform(0.4, 0.8)
                        particle = FireParticle(
                            position=spawn_position,
                            velocity=velocity,
                            lifetime=lifetime,
                            particle_color=particle_color,
                            parent=self.root,
                            toon_shader=self.toon_shader
                        )

                        self.fire_particles.append(particle)

        # Update all fire particles
        particles_to_remove = []
        dt = 0.016  # Assume 60 FPS (~16ms per frame)

        for i, particle in enumerate(self.fire_particles):
            still_alive = particle.update(dt)
            if not still_alive:
                particles_to_remove.append(i)

        # Remove dead particles (iterate backwards to avoid index issues)
        for i in reversed(particles_to_remove):
            self.fire_particles[i].destroy()
            del self.fire_particles[i]

    def destroy(self):
        """Cleanup all entities."""
        for segment in self.segments:
            segment.destroy()
        for eye in self.eyes:
            eye.destroy()
        for whisker in self.whiskers:
            whisker.destroy()
        for horn in self.horns:
            horn.destroy()
        for spike in self.spikes:
            spike.destroy()
        if self.mouth_sphere is not None:
            destroy(self.mouth_sphere)
        for particle in self.fire_particles:
            particle.destroy()
        self.fire_particles.clear()
        destroy(self.root)
