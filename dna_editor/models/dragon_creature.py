"""
DragonCreature model - Space Harrier inspired segmented flying serpent.
Chain of spheres forming a snake-like body with smooth weaving/bobbing animation.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .eye import Eye
from ..core.curves import bezier_curve


class FireParticle:
    """Single fire particle for dragon breath effect."""

    def __init__(self, position, velocity, lifetime, particle_color, parent, toon_shader=None):
        """
        Create a fire particle.

        Args:
            position: Vec3 starting position
            velocity: Vec3 velocity vector
            lifetime: Particle lifespan in seconds
            particle_color: RGB tuple (0-1) for particle color
            parent: Parent entity
            toon_shader: Optional toon shader
        """
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = velocity
        self.initial_color = particle_color

        # Create sphere entity
        particle_params = {
            'model': 'sphere',
            'color': color.rgb(*particle_color),
            'position': position,
            'scale': 0.15,  # Start small
            'parent': parent
        }

        if toon_shader is not None:
            particle_params['shader'] = toon_shader

        self.entity = Entity(**particle_params)
        self.base_scale = 0.15

    def update(self, dt):
        """
        Update particle position and appearance.

        Args:
            dt: Time delta in seconds

        Returns:
            True if particle is still alive, False if expired
        """
        self.age += dt

        # Check if expired
        if self.age >= self.lifetime:
            return False

        # Move particle
        self.entity.position += self.velocity * dt

        # Calculate fade/shrink factor (0 at start, 1 at end)
        fade_t = self.age / self.lifetime

        # Fade alpha (brightest at 0.3, then fade out)
        if fade_t < 0.3:
            # Brighten from 0.5 to 1.0
            alpha_factor = 0.5 + (fade_t / 0.3) * 0.5
        else:
            # Fade from 1.0 to 0
            alpha_factor = 1.0 - ((fade_t - 0.3) / 0.7)

        # Shrink over time (starts at 1.0, shrinks to 0.3)
        scale_factor = 1.0 - (fade_t * 0.7)
        self.entity.scale = self.base_scale * scale_factor

        # Color shift from yellow/orange to red to black
        if fade_t < 0.5:
            # Yellow/orange to red
            blend = fade_t / 0.5
            r = self.initial_color[0]
            g = self.initial_color[1] * (1.0 - blend * 0.5)
            b = self.initial_color[2] * (1.0 - blend)
        else:
            # Red to dark red/black
            blend = (fade_t - 0.5) / 0.5
            r = self.initial_color[0] * (1.0 - blend * 0.6)
            g = 0
            b = 0

        # Apply color with alpha
        self.entity.color = color.rgba(r * alpha_factor, g * alpha_factor, b * alpha_factor, alpha_factor)

        return True  # Still alive

    def destroy(self):
        """Cleanup particle entity."""
        destroy(self.entity)


class DragonSegment:
    """Single segment (sphere) in the dragon body with connector tube to previous segment."""

    def __init__(self, segment_index, total_segments, position, size,
                 segment_color, parent, toon_shader=None, previous_segment=None):
        """
        Create a dragon segment.

        Args:
            segment_index: Index of this segment (0 = head, increasing toward tail)
            total_segments: Total number of segments in dragon
            position: Vec3 position in world space
            size: Sphere scale
            segment_color: RGB tuple (0-1) for this segment
            parent: Parent entity (scene root)
            toon_shader: Optional toon shader to apply
            previous_segment: Reference to previous DragonSegment (None for head)
        """
        self.segment_index = segment_index
        self.total_segments = total_segments
        self.base_position = position
        self.size = size
        self.segment_color = segment_color
        self.previous_segment = previous_segment
        self.connector_tube = None

        # Create sphere entity
        sphere_params = {
            'model': 'sphere',
            'color': color.rgb(*segment_color),
            'scale': size,
            'position': position,
            'parent': parent
        }

        if toon_shader is not None:
            sphere_params['shader'] = toon_shader

        self.entity = Entity(**sphere_params)

        # Create connector tube to previous segment (if not head)
        if previous_segment is not None:
            self._create_connector_tube(parent, segment_color, toon_shader)

    def _create_connector_tube(self, scene_parent, tube_color, toon_shader):
        """Create tube connecting this segment to previous segment."""
        if self.previous_segment is None:
            return

        # Calculate tube position, rotation, and length
        midpoint = (self.entity.position + self.previous_segment.entity.position) / 2
        length = (self.entity.position - self.previous_segment.entity.position).length()

        # Tube radius (average of both segment sizes)
        avg_size = (self.size + self.previous_segment.size) / 2
        tube_radius = avg_size * 0.4  # Thicker tubes for dragon body

        # Create tube entity (stretched cube along Y axis)
        tube_params = {
            'model': 'cube',
            'color': color.rgb(*tube_color),
            'position': midpoint,
            'scale': (tube_radius, length / 2, tube_radius),
            'parent': scene_parent
        }

        if toon_shader is not None:
            tube_params['shader'] = toon_shader

        self.connector_tube = Entity(**tube_params)

        # Orient tube from previous to current segment
        self.connector_tube.look_at(self.previous_segment.entity, axis=Vec3.up)

    def update_connector_tube(self):
        """Update connector tube position to follow animated segments."""
        if self.connector_tube is None or self.previous_segment is None:
            return

        # Recalculate midpoint
        midpoint = (self.entity.position + self.previous_segment.entity.position) / 2
        self.connector_tube.position = midpoint

        # Recalculate length
        length = (self.entity.position - self.previous_segment.entity.position).length()
        self.connector_tube.scale_y = length / 2

        # Update rotation
        self.connector_tube.look_at(self.previous_segment.entity, axis=Vec3.up)

    def destroy(self):
        """Cleanup segment entities."""
        if self.connector_tube is not None:
            destroy(self.connector_tube)
        destroy(self.entity)


class DragonHorn:
    """Rigid curved horn extending from dragon's head, using Bezier curves and sphere chains."""

    def __init__(self, anchor_point, target_point, num_segments, base_thickness,
                 horn_color, parent, toon_shader=None):
        """
        Create a dragon horn.

        Args:
            anchor_point: Vec3 starting position (on head surface)
            target_point: Vec3 ending position (horn tip)
            num_segments: Number of spheres along horn (typically 3)
            base_thickness: Thickness at anchor point (tapers to tip using golden ratio)
            horn_color: RGB tuple (0-1) for horn
            parent: Parent entity
            toon_shader: Optional toon shader
        """
        self.anchor_point = anchor_point
        self.target_point = target_point
        self.num_segments = num_segments
        self.base_thickness = base_thickness
        self.horn_color = horn_color

        # Generate horn curve using Bezier (rigid curve for horns)
        # Use lower control_strength for more rigid, less wavy horns
        curve_points = bezier_curve(
            anchor=anchor_point,
            target=target_point,
            num_points=num_segments,
            control_strength=0.25  # Rigid curve for horns
        )

        # Create sphere chain with golden ratio tapering
        self.spheres = []
        self.tubes = []
        self.base_positions = []  # Store for animation

        # Golden ratio for tapering
        PHI = 1.618033988749895

        for i, point in enumerate(curve_points):
            # Calculate size with golden ratio taper (thick base → thin tip)
            t = i / max(num_segments - 1, 1)
            # Golden taper: 1.0 at base → 1/PHI² at tip
            taper_factor = 1.0 - (t * (1.0 - 1.0 / (PHI ** 2)))
            sphere_size = base_thickness * taper_factor

            # Create sphere
            sphere_params = {
                'model': 'sphere',
                'color': color.rgb(*horn_color),
                'position': point,
                'scale': sphere_size,
                'parent': parent
            }

            if toon_shader is not None:
                sphere_params['shader'] = toon_shader

            sphere = Entity(**sphere_params)
            self.spheres.append(sphere)
            self.base_positions.append(Vec3(point))

            # Create connector tube to previous sphere
            if i > 0:
                prev_sphere = self.spheres[i - 1]
                midpoint = (sphere.position + prev_sphere.position) / 2
                length = (sphere.position - prev_sphere.position).length()

                # Tube radius (average of both sphere sizes)
                avg_size = (sphere_size + prev_sphere.scale[0]) / 2
                tube_radius = avg_size * 0.7  # Thick tubes for solid horns

                tube_params = {
                    'model': 'cube',
                    'color': color.rgb(*horn_color),
                    'position': midpoint,
                    'scale': (tube_radius, length / 2, tube_radius),
                    'parent': parent
                }

                if toon_shader is not None:
                    tube_params['shader'] = toon_shader

                tube = Entity(**tube_params)
                tube.look_at(prev_sphere, axis=Vec3.up)
                self.tubes.append(tube)

    def update_animation(self, time, head_position):
        """
        Update horn animation (minimal movement - horns are rigid).

        Args:
            time: Current animation time
            head_position: Current position of dragon's head (to track)
        """
        # Calculate head offset from initial anchor point
        head_offset = head_position - self.anchor_point

        # Horns move rigidly with head (no sway like whiskers)
        for i, sphere in enumerate(self.spheres):
            # Base position follows head movement exactly
            sphere.position = self.base_positions[i] + head_offset

            # Update connector tubes
            if i > 0:
                tube = self.tubes[i - 1]
                prev_sphere = self.spheres[i - 1]

                # Recalculate tube position and orientation
                midpoint = (sphere.position + prev_sphere.position) / 2
                tube.position = midpoint

                length = (sphere.position - prev_sphere.position).length()
                tube.scale_y = length / 2

                tube.look_at(prev_sphere, axis=Vec3.up)

    def destroy(self):
        """Cleanup horn entities."""
        for sphere in self.spheres:
            destroy(sphere)
        for tube in self.tubes:
            destroy(tube)


class DragonSpike:
    """Sharp spike extending upward from dragon's back (one per body segment)."""

    def __init__(self, anchor_point, segment_size, spike_color, parent, toon_shader=None, segment_index=0, total_segments=1):
        """
        Create a dragon spine spike.

        Args:
            anchor_point: Vec3 starting position (on segment top)
            segment_size: Size of the parent segment (for proportional sizing)
            spike_color: RGB tuple (0-1) for spike
            parent: Parent entity
            toon_shader: Optional toon shader
            segment_index: Index of this segment along body (0=head, higher=tail)
            total_segments: Total number of body segments (for tail tapering)
        """
        self.anchor_point = anchor_point
        self.segment_size = segment_size
        self.spike_color = spike_color

        # Golden ratio for sizing
        PHI = 1.618033988749895

        # Calculate tail taper: spikes get smaller toward the tail
        # segment_index 1 (first body segment) = 1.0, last segment = 0.3
        if total_segments > 1:
            tail_taper = 1.0 - (segment_index / total_segments) * 0.7
        else:
            tail_taper = 1.0

        # Spike dimensions (proportional to segment size, with tail taper)
        spike_base_thickness = (segment_size / (PHI ** 3)) * tail_taper  # Smaller base
        spike_length = (segment_size * 0.8) * tail_taper  # Shorter spikes

        # Create a single tapered pyramid/cone spike
        # Use a stretched cube that tapers from base to tip
        spike_params = {
            'model': 'cube',
            'color': color.rgb(*spike_color),
            'position': anchor_point + Vec3(0, spike_length / 2, 0),
            'scale': (spike_base_thickness, spike_length, spike_base_thickness),
            'parent': parent
        }

        if toon_shader is not None:
            spike_params['shader'] = toon_shader

        self.spike = Entity(**spike_params)

        # Apply tapering by scaling the top vertices smaller (simulated with nested cube)
        # Create a smaller cube at the tip to create taper effect
        tip_size = spike_base_thickness * 0.2  # Sharp tip
        tip_params = {
            'model': 'cube',
            'color': color.rgb(*spike_color),
            'position': anchor_point + Vec3(0, spike_length * 0.95, 0),
            'scale': (tip_size, spike_length * 0.1, tip_size),
            'parent': parent
        }

        if toon_shader is not None:
            tip_params['shader'] = toon_shader

        self.tip = Entity(**tip_params)

        # Store base position for animation
        self.base_position = Vec3(anchor_point)

    def update_animation(self, time, segment_position):
        """
        Update spike animation (rigid - follows segment exactly).

        Args:
            time: Current animation time
            segment_position: Current position of parent segment (to track)
        """
        # Calculate segment offset from initial anchor point
        segment_offset = segment_position - self.base_position

        # Spikes move rigidly with segment (no independent motion)
        self.spike.position = self.spike.position + segment_offset
        self.tip.position = self.tip.position + segment_offset

        # Update base position to new location
        self.base_position = segment_position

    def destroy(self):
        """Cleanup spike entities."""
        destroy(self.spike)
        destroy(self.tip)


class DragonWhisker:
    """Thin curved whisker extending from dragon's head, using Bezier curves and sphere chains."""

    def __init__(self, anchor_point, target_point, num_segments, base_thickness,
                 whisker_color, parent, toon_shader=None, phase_offset=0):
        """
        Create a dragon whisker.

        Args:
            anchor_point: Vec3 starting position (on head surface)
            target_point: Vec3 ending position (whisker tip)
            num_segments: Number of spheres along whisker (3-6)
            base_thickness: Thickness at anchor point (tapers to tip)
            whisker_color: RGB tuple (0-1) for whisker
            parent: Parent entity
            toon_shader: Optional toon shader
            phase_offset: Random phase for animation variation
        """
        self.anchor_point = anchor_point
        self.target_point = target_point
        self.num_segments = num_segments
        self.base_thickness = base_thickness
        self.whisker_color = whisker_color
        self.phase_offset = phase_offset

        # Generate whisker curve using Bezier
        # control_strength maps to curve_intensity (0.2-0.6 range)
        from ..core.constants import DRAGON_WHISKER_CURVE_INTENSITY
        curve_points = bezier_curve(
            anchor=anchor_point,
            target=target_point,
            num_points=num_segments,
            control_strength=DRAGON_WHISKER_CURVE_INTENSITY
        )

        # Create sphere chain with golden ratio tapering
        self.spheres = []
        self.tubes = []
        self.base_positions = []  # Store for animation

        # Golden ratio for tapering
        PHI = 1.618033988749895

        for i, point in enumerate(curve_points):
            # Calculate size with golden ratio taper (thick base → thin tip)
            t = i / max(num_segments - 1, 1)
            # Golden taper: 1.0 at base → 1/PHI² at tip
            taper_factor = 1.0 - (t * (1.0 - 1.0 / (PHI ** 2)))
            sphere_size = base_thickness * taper_factor

            # Create sphere
            sphere_params = {
                'model': 'sphere',
                'color': color.rgb(*whisker_color),
                'position': point,
                'scale': sphere_size,
                'parent': parent
            }

            if toon_shader is not None:
                sphere_params['shader'] = toon_shader

            sphere = Entity(**sphere_params)
            self.spheres.append(sphere)
            self.base_positions.append(Vec3(point))

            # Create connector tube to previous sphere
            if i > 0:
                prev_sphere = self.spheres[i - 1]
                midpoint = (sphere.position + prev_sphere.position) / 2
                length = (sphere.position - prev_sphere.position).length()

                # Tube radius (average of both sphere sizes)
                avg_size = (sphere_size + prev_sphere.scale[0]) / 2
                tube_radius = avg_size * 0.6  # Thinner tubes for whiskers

                tube_params = {
                    'model': 'cube',
                    'color': color.rgb(*whisker_color),
                    'position': midpoint,
                    'scale': (tube_radius, length / 2, tube_radius),
                    'parent': parent
                }

                if toon_shader is not None:
                    tube_params['shader'] = toon_shader

                tube = Entity(**tube_params)
                tube.look_at(prev_sphere, axis=Vec3.up)
                self.tubes.append(tube)

    def update_animation(self, time, head_position):
        """
        Update whisker animation with gentle sway.

        Args:
            time: Current animation time
            head_position: Current position of dragon's head (to track)
        """
        # Calculate head offset from initial anchor point
        head_offset = head_position - self.anchor_point

        for i, sphere in enumerate(self.spheres):
            # Base position follows head movement
            base_pos = self.base_positions[i] + head_offset

            # Sway animation - increases toward tip
            t = i / max(len(self.spheres) - 1, 1)  # 0 at base, 1 at tip
            sway_amplitude = 0.04 * t  # Tip sways more (0 at base → 0.04 at tip)

            # Gentle wave motion with phase offset for variety
            wave_phase = time * 1.2 + self.phase_offset
            sway_x = math.sin(wave_phase + i * 0.3) * sway_amplitude
            sway_y = math.cos(wave_phase * 1.3 + i * 0.4) * sway_amplitude

            # Apply sway
            sphere.position = base_pos + Vec3(sway_x, sway_y, 0)

            # Update connector tubes
            if i > 0:
                tube = self.tubes[i - 1]
                prev_sphere = self.spheres[i - 1]

                # Recalculate tube position and orientation
                midpoint = (sphere.position + prev_sphere.position) / 2
                tube.position = midpoint

                length = (sphere.position - prev_sphere.position).length()
                tube.scale_y = length / 2

                tube.look_at(prev_sphere, axis=Vec3.up)

    def destroy(self):
        """Cleanup whisker entities."""
        for sphere in self.spheres:
            destroy(sphere)
        for tube in self.tubes:
            destroy(tube)


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

        # Create toon shader (shared across all parts)
        from ..shaders import create_toon_shader
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in DragonCreature, using default rendering")

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

            # Create segment
            segment = DragonSegment(
                segment_index=i,
                total_segments=self.num_segments,
                position=position,
                size=segment_size,
                segment_color=segment_color,
                parent=self.root,
                toon_shader=self.toon_shader,
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

            # Create eye
            eye = Eye(
                position=eye_position,
                size=self.eye_size,
                eyeball_color=self.eyeball_color,
                pupil_color=self.pupil_color,
                parent=self.root,
                toon_shader=self.toon_shader
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

                # Create whisker
                whisker = DragonWhisker(
                    anchor_point=anchor_point,
                    target_point=target_point,
                    num_segments=self.whisker_segments,
                    base_thickness=self.whisker_thickness,
                    whisker_color=whisker_color,
                    parent=self.root,
                    toon_shader=self.toon_shader,
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

            # Create horn with 3 segments
            horn = DragonHorn(
                anchor_point=anchor_point,
                target_point=target_point,
                num_segments=3,  # As requested: 3 segments
                base_thickness=horn_base_thickness,
                horn_color=horn_color,
                parent=self.root,
                toon_shader=self.toon_shader
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

            # Create spike with tail tapering
            spike = DragonSpike(
                anchor_point=anchor_point,
                segment_size=segment_size,
                spike_color=self.spine_spike_color,
                parent=self.root,
                toon_shader=self.toon_shader,
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

    def start_attack_2(self, camera_position):
        """Start attack 2 animation (same as attack 1 for dragon)."""
        self.start_attack(camera_position)

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
