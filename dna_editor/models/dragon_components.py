"""
Dragon body components - reusable parts for building dragon creatures.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from ..core.curves import bezier_curve
from ..shaders import get_shader_for_scale


class DragonSegment:
    """Single segment (sphere) in the dragon body with connector tube to previous segment."""

    def __init__(self, segment_index, total_segments, position, size,
                 segment_color, parent, toon_shader=None, toon_shader_lite=None, previous_segment=None):
        """
        Create a dragon segment.

        Args:
            segment_index: Index of this segment (0 = head, increasing toward tail)
            total_segments: Total number of segments in dragon
            position: Vec3 position in world space
            size: Sphere scale
            segment_color: RGB tuple (0-1) for this segment
            parent: Parent entity (scene root)
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small spheres (performance optimization)
            previous_segment: Reference to previous DragonSegment (None for head)
        """
        self.segment_index = segment_index
        self.total_segments = total_segments
        self.base_position = position
        self.size = size
        self.segment_color = segment_color
        self.previous_segment = previous_segment
        self.connector_tube = None

        # Create sphere entity with appropriate shader based on size
        sphere_params = {
            'model': 'sphere',
            'color': color.rgb(*segment_color),
            'scale': size,
            'position': position,
            'parent': parent
        }

        # Choose shader based on size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(size, toon_shader, toon_shader_lite)
            sphere_params['shader'] = chosen_shader
        elif toon_shader is not None:
            sphere_params['shader'] = toon_shader

        self.entity = Entity(**sphere_params)

        # Create connector tube to previous segment (if not head)
        if previous_segment is not None:
            self._create_connector_tube(parent, segment_color, toon_shader, toon_shader_lite)

    def _create_connector_tube(self, scene_parent, tube_color, toon_shader, toon_shader_lite):
        """Create tube connecting this segment to previous segment."""
        if self.previous_segment is None:
            return

        # Calculate tube position, rotation, and length
        midpoint = (self.entity.position + self.previous_segment.entity.position) / 2
        length = (self.entity.position - self.previous_segment.entity.position).length()

        # Tube radius (average of both segment sizes)
        avg_size = (self.size + self.previous_segment.size) / 2
        tube_radius = avg_size * 0.4  # Thicker tubes for dragon body

        # Create tube entity (stretched cube along Y axis) with appropriate shader
        tube_params = {
            'model': 'cube',
            'color': color.rgb(*tube_color),
            'position': midpoint,
            'scale': (tube_radius, length / 2, tube_radius),
            'parent': scene_parent
        }

        # Choose shader based on tube size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(tube_radius, toon_shader, toon_shader_lite)
            tube_params['shader'] = chosen_shader
        elif toon_shader is not None:
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
                 horn_color, parent, toon_shader=None, toon_shader_lite=None):
        """
        Create a dragon horn.

        Args:
            anchor_point: Vec3 starting position (on head surface)
            target_point: Vec3 ending position (horn tip)
            num_segments: Number of spheres along horn (typically 3)
            base_thickness: Thickness at anchor point (tapers to tip using golden ratio)
            horn_color: RGB tuple (0-1) for horn
            parent: Parent entity
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small spheres (performance optimization)
        """
        self.anchor_point = anchor_point
        self.target_point = target_point
        self.num_segments = num_segments
        self.base_thickness = base_thickness
        self.horn_color = horn_color
        self.toon_shader = toon_shader
        self.toon_shader_lite = toon_shader_lite

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

            # Create sphere with appropriate shader
            sphere_params = {
                'model': 'sphere',
                'color': color.rgb(*horn_color),
                'position': point,
                'scale': sphere_size,
                'parent': parent
            }

            # Choose shader based on size (LOD optimization)
            if toon_shader is not None and toon_shader_lite is not None:
                chosen_shader = get_shader_for_scale(sphere_size, toon_shader, toon_shader_lite)
                sphere_params['shader'] = chosen_shader
            elif toon_shader is not None:
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

                # Choose shader based on tube size (LOD optimization)
                if toon_shader is not None and toon_shader_lite is not None:
                    chosen_shader = get_shader_for_scale(tube_radius, toon_shader, toon_shader_lite)
                    tube_params['shader'] = chosen_shader
                elif toon_shader is not None:
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

    def __init__(self, anchor_point, segment_size, spike_color, parent, toon_shader=None, toon_shader_lite=None, segment_index=0, total_segments=1):
        """
        Create a dragon spine spike.

        Args:
            anchor_point: Vec3 starting position (on segment top)
            segment_size: Size of the parent segment (for proportional sizing)
            spike_color: RGB tuple (0-1) for spike
            parent: Parent entity
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small cubes (performance optimization)
            segment_index: Index of this segment along body (0=head, higher=tail)
            total_segments: Total number of body segments (for tail tapering)
        """
        self.anchor_point = anchor_point
        self.segment_size = segment_size
        self.spike_color = spike_color
        self.toon_shader = toon_shader
        self.toon_shader_lite = toon_shader_lite

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

        # Create a single tapered pyramid/cone spike with appropriate shader
        # Use a stretched cube that tapers from base to tip
        spike_params = {
            'model': 'cube',
            'color': color.rgb(*spike_color),
            'position': anchor_point + Vec3(0, spike_length / 2, 0),
            'scale': (spike_base_thickness, spike_length, spike_base_thickness),
            'parent': parent
        }

        # Choose shader based on size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(spike_base_thickness, toon_shader, toon_shader_lite)
            spike_params['shader'] = chosen_shader
        elif toon_shader is not None:
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

        # Choose shader based on tip size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(tip_size, toon_shader, toon_shader_lite)
            tip_params['shader'] = chosen_shader
        elif toon_shader is not None:
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
                 whisker_color, parent, toon_shader=None, toon_shader_lite=None, phase_offset=0):
        """
        Create a dragon whisker.

        Args:
            anchor_point: Vec3 starting position (on head surface)
            target_point: Vec3 ending position (whisker tip)
            num_segments: Number of spheres along whisker (3-6)
            base_thickness: Thickness at anchor point (tapers to tip)
            whisker_color: RGB tuple (0-1) for whisker
            parent: Parent entity
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small spheres (performance optimization)
            phase_offset: Random phase for animation variation
        """
        self.anchor_point = anchor_point
        self.target_point = target_point
        self.num_segments = num_segments
        self.base_thickness = base_thickness
        self.whisker_color = whisker_color
        self.toon_shader = toon_shader
        self.toon_shader_lite = toon_shader_lite
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

            # Create sphere with appropriate shader
            sphere_params = {
                'model': 'sphere',
                'color': color.rgb(*whisker_color),
                'position': point,
                'scale': sphere_size,
                'parent': parent
            }

            # Choose shader based on size (LOD optimization)
            if toon_shader is not None and toon_shader_lite is not None:
                chosen_shader = get_shader_for_scale(sphere_size, toon_shader, toon_shader_lite)
                sphere_params['shader'] = chosen_shader
            elif toon_shader is not None:
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

                # Choose shader based on tube size (LOD optimization)
                if toon_shader is not None and toon_shader_lite is not None:
                    chosen_shader = get_shader_for_scale(tube_radius, toon_shader, toon_shader_lite)
                    tube_params['shader'] = chosen_shader
                elif toon_shader is not None:
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
