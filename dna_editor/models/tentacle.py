"""
Tentacle model - a single tentacle made of connected segments.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from ..core.curves import bezier_curve, fourier_curve
from ..core.constants import (
    GOLDEN_RATIO, GOLDEN_ANGLE,
    TOON_CONTACT_SHADOW_SIZE, TOON_CONTACT_SHADOW_OPACITY
)
from ..shaders import create_toon_shader


class Tentacle:
    """A single tentacle made of connected segments."""

    def __init__(self, parent, anchor, target, segments, algorithm, color_rgb,
                 algorithm_params, thickness_base=0.25, taper_factor=0.6,
                 branch_depth=0, branch_count=1, current_depth=0, toon_shader=None):
        """
        Create a tentacle from anchor to target point.

        Args:
            parent: Parent entity to attach segments to
            anchor: Vec3 start point
            target: Vec3 end point
            segments: Number of segments
            algorithm: 'bezier' or 'fourier'
            color_rgb: RGB tuple for tentacle color
            algorithm_params: Dict of algorithm-specific parameters
            thickness_base: Base thickness of tentacle
            taper_factor: How much to taper toward tip (0-1)
            branch_depth: Maximum branching depth (0 = no branches)
            branch_count: Number of child branches per tentacle
            current_depth: Current depth in recursion (internal)
            toon_shader: Toon shader instance (created once, shared across tentacles)
        """
        self.parent = parent
        self.anchor = anchor
        self.target = target
        self.segments = []
        self.shadow_spheres = []  # Contact shadow spheres at joints
        self.children = []  # Child tentacles (branches)
        self.algorithm = algorithm
        self.color_rgb = color_rgb
        self.branch_depth = branch_depth
        self.branch_count = branch_count
        self.current_depth = current_depth
        self.segment_distances = []  # Original distance between consecutive segments

        # Generate unique random phase offset for this tentacle (for animation variation)
        self.animation_phase_offset = random.random() * math.pi * 2

        # Get or create toon shader (create once, share across all tentacles)
        if toon_shader is not None:
            self.toon_shader = toon_shader
        else:
            self.toon_shader = create_toon_shader()
            if self.toon_shader is None:
                print("WARNING: Toon shader creation failed, using default rendering")

        # Generate curve points based on algorithm with dynamic parameters
        if algorithm == 'bezier':
            curve_points = bezier_curve(
                anchor, target, segments + 1,
                control_strength=algorithm_params.get('control_strength', 0.4)
            )
        else:  # fourier
            curve_points = fourier_curve(
                anchor, target, segments + 1,
                num_waves=int(algorithm_params.get('num_waves', 3)),
                amplitude=algorithm_params.get('amplitude', 0.15)
            )

        # Create segments along the curve
        for i in range(segments):
            p1 = curve_points[i]
            p2 = curve_points[i + 1]

            # Calculate segment position (midpoint) and length
            seg_pos = (p1 + p2) / 2
            seg_dir = (p2 - p1).normalized()
            seg_length = (p2 - p1).length()

            # Store original distance between this segment center and next segment center
            # (for constraint solver)
            if i < segments - 1:
                p3 = curve_points[i + 2]
                next_seg_pos = (p2 + p3) / 2
                distance = (next_seg_pos - seg_pos).length()
                self.segment_distances.append(distance)

            # Calculate thickness (taper from base to tip) with dynamic parameters
            thickness = thickness_base * (1.0 - i / segments * taper_factor)

            # Create segment as sphere with toon shader
            # Only apply shader if it was created successfully
            entity_params = {
                'model': 'sphere',
                'color': color.rgb(*color_rgb),
                'position': seg_pos,
                'scale': thickness,
                'parent': parent
            }
            if self.toon_shader is not None:
                entity_params['shader'] = self.toon_shader

            segment = Entity(**entity_params)

            # Store for animation
            segment.base_position = seg_pos
            segment.segment_index = i
            segment.total_segments = segments

            self.segments.append(segment)

            # Add contact shadow sphere at the joint (p2) between this and next segment
            # Skip for the last segment (no joint after it)
            if i < segments - 1:
                # Shadow sphere is smaller and darker (use constants for easy tuning)
                shadow_size = thickness * TOON_CONTACT_SHADOW_SIZE
                shadow_opacity = TOON_CONTACT_SHADOW_OPACITY

                shadow = Entity(
                    model='sphere',
                    color=color.rgba(0, 0, 0, shadow_opacity),
                    position=p2,  # Place at joint point
                    scale=shadow_size,
                    parent=parent,
                    unlit=True  # Don't apply lighting to shadows
                )

                # Store for cleanup
                shadow.base_position = p2
                shadow.segment_index = i
                self.shadow_spheres.append(shadow)

        # Create child branches if depth allows
        self.curve_points = curve_points  # Store for branch positioning
        if current_depth < branch_depth and branch_count > 0:
            self._create_branches(algorithm, algorithm_params, thickness_base, taper_factor)

    def _create_branches(self, algorithm, algorithm_params, thickness_base, taper_factor):
        """Create child branches using Fibonacci-based positioning."""
        num_points = len(self.curve_points)

        # Golden ratio positions along tentacle (e.g., 0.382, 0.618 for 2 branches)
        # Use inverse golden ratio (φ - 1 ≈ 0.618) for natural spacing
        phi_inverse = GOLDEN_RATIO - 1  # ≈ 0.618

        for i in range(self.branch_count):
            # Position along parent tentacle using golden ratio intervals
            # Start at 0.382 (1 - φ⁻¹) to avoid branching too early
            t = 0.382 + (i / max(self.branch_count, 1)) * 0.5  # Spread between 0.382 and 0.882
            point_index = int(t * (num_points - 1))
            point_index = max(1, min(point_index, num_points - 2))  # Avoid endpoints

            # Branch anchor at this point on parent curve
            branch_anchor = self.curve_points[point_index]

            # Calculate branch direction using golden angle rotation
            # Get parent direction at this point
            parent_dir = (self.curve_points[point_index + 1] -
                         self.curve_points[point_index]).normalized()

            # Create perpendicular vectors for branch offset
            up = Vec3(0, 1, 0)
            if abs(parent_dir.y) > 0.99:
                up = Vec3(1, 0, 0)

            # Rotate using golden angle for natural spiral
            rotation_angle = i * GOLDEN_ANGLE
            right = parent_dir.cross(up).normalized()
            up = right.cross(parent_dir).normalized()

            # Branch direction: blend parent direction with perpendicular offset
            branch_offset = (right * math.cos(rotation_angle) +
                           up * math.sin(rotation_angle)) * 0.7
            branch_dir = (parent_dir * 0.5 + branch_offset).normalized()

            # Branch length scaled by golden ratio
            parent_length = (self.target - self.anchor).length()
            branch_length = parent_length / GOLDEN_RATIO

            # Branch target position
            branch_target = branch_anchor + branch_dir * branch_length

            # Scale thickness by golden ratio
            child_thickness = thickness_base / GOLDEN_RATIO

            # Color variation for branches (slightly different hue)
            hue_shift = 0.05 * (i + self.current_depth)
            child_color = (
                min(1.0, self.color_rgb[0] + hue_shift),
                self.color_rgb[1],
                max(0.0, self.color_rgb[2] - hue_shift * 0.5)
            )

            # Create child tentacle (recursively, share shader instance)
            child = Tentacle(
                parent=self.parent,
                anchor=branch_anchor,
                target=branch_target,
                segments=len(self.segments),  # Same segment count
                algorithm=algorithm,
                color_rgb=child_color,
                algorithm_params=algorithm_params,
                thickness_base=child_thickness,
                taper_factor=taper_factor,
                branch_depth=self.branch_depth,
                branch_count=self.branch_count,
                current_depth=self.current_depth + 1,  # Increment depth
                toon_shader=self.toon_shader  # Share shader instance
            )

            self.children.append(child)

    def update_animation(self, time, anim_speed=2.0, wave_amplitude=0.05,
                         is_attacking=False, attack_start_time=0, camera_position=None,
                         is_attacking_2=False, is_selected_for_attack_2=False, attack_2_start_time=0,
                         is_reaching=False, reach_target=None, reach_state='idle', reach_progress=0.0):
        """
        Animate tentacle with wave motion, attack animation, or exploration reaching.

        Args:
            time: Current animation time
            anim_speed: Speed of wave motion
            wave_amplitude: Base amplitude of wave motion
            is_attacking: Whether tentacle is in attack mode (Attack 1 - all tentacles)
            attack_start_time: Time when attack started
            is_attacking_2: Whether creature is in Attack 2 mode (single tentacle)
            is_selected_for_attack_2: Whether THIS tentacle is the attacking one for Attack 2
            attack_2_start_time: Time when Attack 2 started
            camera_position: Camera position for targeting (Vec3)
            is_reaching: Whether tentacle is reaching for exploration target
            reach_target: Vec3 exploration target position
            reach_state: 'idle', 'reaching', or 'returning'
            reach_progress: Progress through current reach phase (0-1)
        """
        # If Attack 1, use whip attack animation
        if is_attacking and camera_position is not None:
            self._apply_attack_animation(time, attack_start_time, camera_position, anim_speed, wave_amplitude)
            # Apply constraints to keep tentacle anchored and segments connected
            self._apply_segment_constraints()
            return

        # If Attack 2, only the selected tentacle slashes (others idle)
        if is_attacking_2 and is_selected_for_attack_2 and camera_position is not None:
            self._apply_single_tentacle_slash(time, attack_2_start_time, camera_position, anim_speed, wave_amplitude)
            # Apply constraints to keep tentacle anchored and segments connected
            self._apply_segment_constraints()
            return

        # Otherwise, use normal idle animation with multi-frequency 3D wave motion
        for segment in self.segments:
            i = segment.segment_index
            n = segment.total_segments

            # Per-tentacle phase offset for variation (prevents all tentacles moving in sync)
            # Use stored random offset generated at creation
            tentacle_phase = self.animation_phase_offset

            # Multi-frequency waves (like Fourier series)
            # Primary wave - main motion
            phase1 = time * anim_speed + i * 0.3 + tentacle_phase
            # Secondary wave - slower, adds complexity
            phase2 = time * anim_speed * 0.5 + i * 0.15
            # Tertiary wave - faster, adds subtle detail
            phase3 = time * anim_speed * 2.0 + i * 0.6

            # Non-linear amplitude (quadratic - tips move MORE dramatically)
            # Using power of 1.5 for smooth but noticeable increase
            amplitude = wave_amplitude * ((i / max(n, 1)) ** 1.5)

            # 3D offsets with multiple frequencies
            # Each axis gets a blend of different frequencies (60% primary, 30% secondary, 10% tertiary)
            offset_x = (math.sin(phase1) * 0.6 +
                       math.sin(phase2) * 0.3 +
                       math.sin(phase3) * 0.1) * amplitude

            offset_y = (math.cos(phase1 * 1.3) * 0.6 +
                       math.cos(phase2 * 1.5) * 0.3 +
                       math.cos(phase3 * 0.9) * 0.1) * amplitude

            # NEW: Z-axis motion for forward/back drifting
            offset_z = (math.sin(phase1 * 0.8) * 0.4 +
                       math.cos(phase2 * 1.2) * 0.2 +
                       math.sin(phase3 * 1.1) * 0.1) * amplitude

            # Add slow spiral rotation around tentacle axis (creates gentle twist)
            spiral_angle = time * 0.5 + i * 0.2 + tentacle_phase
            twist_radius = amplitude * 0.3
            offset_x += math.cos(spiral_angle) * twist_radius
            offset_y += math.sin(spiral_angle) * twist_radius

            # Base wave offset
            wave_offset = Vec3(offset_x, offset_y, offset_z)

            # If this tentacle is reaching, add reaching offset
            if is_reaching and reach_target is not None:
                from ..core.constants import EXPLORATION_REACH_STRENGTH

                # Calculate direction to shared target from this segment's base position
                direction_to_target = (reach_target - segment.base_position).normalized()

                # Reaching strength increases toward tip (quadratic for dramatic tip movement)
                reach_influence = ((i / max(n, 1)) ** 1.2)

                # Calculate reach offset based on state and progress
                if reach_state == 'reaching':
                    # Smooth ease-out curve (starts fast, slows at end)
                    ease_t = 1.0 - (1.0 - reach_progress) ** 2
                    reach_distance = EXPLORATION_REACH_STRENGTH * ease_t * reach_influence
                elif reach_state == 'returning':
                    # Fast spring-back with cubic easing (fast return)
                    ease_t = 1.0 - (1.0 - reach_progress) ** 3
                    reach_distance = EXPLORATION_REACH_STRENGTH * (1.0 - ease_t) * reach_influence
                else:
                    reach_distance = 0.0

                reach_offset = direction_to_target * reach_distance

                # Blend: 70% reach + 30% base wave motion (keeps tentacle alive during reach)
                segment.position = segment.base_position + reach_offset + wave_offset * 0.3
            else:
                # Normal idle animation (100% wave motion)
                segment.position = segment.base_position + wave_offset

        # Animate shadow spheres (follow their base positions with same multi-frequency 3D wave motion)
        for shadow in self.shadow_spheres:
            i = shadow.segment_index
            n = len(self.segments)

            # Per-tentacle phase offset (same as segments)
            tentacle_phase = self.animation_phase_offset

            # Multi-frequency waves (same as segments)
            phase1 = time * anim_speed + i * 0.3 + tentacle_phase
            phase2 = time * anim_speed * 0.5 + i * 0.15
            phase3 = time * anim_speed * 2.0 + i * 0.6

            # Non-linear amplitude
            amplitude = wave_amplitude * ((i / max(n, 1)) ** 1.5)

            # 3D offsets with multiple frequencies
            offset_x = (math.sin(phase1) * 0.6 +
                       math.sin(phase2) * 0.3 +
                       math.sin(phase3) * 0.1) * amplitude

            offset_y = (math.cos(phase1 * 1.3) * 0.6 +
                       math.cos(phase2 * 1.5) * 0.3 +
                       math.cos(phase3 * 0.9) * 0.1) * amplitude

            offset_z = (math.sin(phase1 * 0.8) * 0.4 +
                       math.cos(phase2 * 1.2) * 0.2 +
                       math.sin(phase3 * 1.1) * 0.1) * amplitude

            # Add spiral rotation
            spiral_angle = time * 0.5 + i * 0.2 + tentacle_phase
            twist_radius = amplitude * 0.3
            offset_x += math.cos(spiral_angle) * twist_radius
            offset_y += math.sin(spiral_angle) * twist_radius

            # Base wave offset
            wave_offset = Vec3(offset_x, offset_y, offset_z)

            # If this tentacle is reaching, add reaching offset to shadows too
            if is_reaching and reach_target is not None:
                from ..core.constants import EXPLORATION_REACH_STRENGTH

                # Calculate direction to shared target
                direction_to_target = (reach_target - shadow.base_position).normalized()

                # Reaching strength increases toward tip
                reach_influence = ((i / max(n, 1)) ** 1.2)

                # Calculate reach offset based on state and progress
                if reach_state == 'reaching':
                    ease_t = 1.0 - (1.0 - reach_progress) ** 2
                    reach_distance = EXPLORATION_REACH_STRENGTH * ease_t * reach_influence
                elif reach_state == 'returning':
                    ease_t = 1.0 - (1.0 - reach_progress) ** 3
                    reach_distance = EXPLORATION_REACH_STRENGTH * (1.0 - ease_t) * reach_influence
                else:
                    reach_distance = 0.0

                reach_offset = direction_to_target * reach_distance

                # Blend: 70% reach + 30% base wave
                shadow.position = shadow.base_position + reach_offset + wave_offset * 0.3
            else:
                # Normal idle animation
                shadow.position = shadow.base_position + wave_offset

        # Animate child branches (pass all parameters through, including attack and exploration state)
        for child in self.children:
            child.update_animation(
                time, anim_speed, wave_amplitude,
                is_attacking, attack_start_time, camera_position,
                is_attacking_2, is_selected_for_attack_2, attack_2_start_time,
                is_reaching, reach_target, reach_state, reach_progress
            )

        # Apply distance constraints to keep segments connected
        # This is called once per tentacle and handles child branches recursively
        self._apply_segment_constraints()

    def _apply_attack_animation(self, time, attack_start_time, camera_position, anim_speed, wave_amplitude):
        """
        Apply whip-like attack animation with exponential acceleration and helical curl.

        Uses advanced mathematics:
        - Traveling wave with exponential amplitude growth
        - Distance-based dynamic stretching
        - Helical curl motion (spiral slash)
        - Phase-based timing (wind-up, strike, follow-through, return)
        """
        from ..core.constants import (
            ATTACK_DURATION, ATTACK_WIND_UP_END, ATTACK_STRIKE_END, ATTACK_FOLLOW_END,
            WHIP_SPEED, WHIP_ACCELERATION, WHIP_AMPLITUDE,
            STRETCH_THRESHOLD, STRETCH_MULTIPLIER, STRETCH_MAX,
            CURL_INTENSITY, CURL_SPEED, CURL_TWIST_FACTOR,
            WIND_UP_DISTANCE
        )

        # Scale attack constants with creature's animation parameters
        # This makes UI sliders affect the attack animation
        scaled_whip_speed = WHIP_SPEED * (anim_speed / 2.0)  # Scales with "Wave Speed" slider
        scaled_whip_amplitude = WHIP_AMPLITUDE * (wave_amplitude / 0.05)  # Scales with "Wave Intensity" slider
        scaled_curl_speed = CURL_SPEED * (anim_speed / 2.0)  # Faster curl with faster animation

        # Calculate attack elapsed time (normalized 0-1)
        attack_elapsed = time - attack_start_time
        attack_t = min(attack_elapsed / ATTACK_DURATION, 1.0)

        # Calculate direction and distance from anchor to camera
        anchor_to_camera = camera_position - self.anchor
        distance_to_camera = anchor_to_camera.length()
        direction_to_camera = anchor_to_camera.normalized() if distance_to_camera > 0.001 else Vec3(0, 0, -1)

        # Calculate stretch factor based on distance (far tentacles stretch more)
        stretch_factor = 1.0
        if distance_to_camera > STRETCH_THRESHOLD:
            excess_distance = distance_to_camera - STRETCH_THRESHOLD
            stretch_factor = 1.0 + (excess_distance * STRETCH_MULTIPLIER)
            stretch_factor = min(stretch_factor, STRETCH_MAX)

        # Determine attack phase and calculate phase-specific motion
        if attack_t < ATTACK_WIND_UP_END / ATTACK_DURATION:
            # Phase 1: Wind-up (pull back)
            phase_t = attack_t / (ATTACK_WIND_UP_END / ATTACK_DURATION)
            # Smooth ease-in using cubic
            ease_t = phase_t * phase_t * (3 - 2 * phase_t)
            base_offset = -direction_to_camera * WIND_UP_DISTANCE * ease_t
            whip_intensity = 0.1  # Minimal whip during wind-up

        elif attack_t < ATTACK_STRIKE_END / ATTACK_DURATION:
            # Phase 2: Strike (explosive forward motion)
            phase_t = (attack_t - ATTACK_WIND_UP_END / ATTACK_DURATION) / ((ATTACK_STRIKE_END - ATTACK_WIND_UP_END) / ATTACK_DURATION)
            # Exponential ease-out for explosive strike
            ease_t = 1.0 - math.pow(1.0 - phase_t, 3)
            strike_distance = 1.5 * stretch_factor
            base_offset = direction_to_camera * strike_distance * ease_t - direction_to_camera * WIND_UP_DISTANCE
            whip_intensity = 2.0 * ease_t  # Increase whip intensity during strike

        elif attack_t < ATTACK_FOLLOW_END / ATTACK_DURATION:
            # Phase 3: Follow-through (continue with decay)
            phase_t = (attack_t - ATTACK_STRIKE_END / ATTACK_DURATION) / ((ATTACK_FOLLOW_END - ATTACK_STRIKE_END) / ATTACK_DURATION)
            strike_distance = 1.5 * stretch_factor
            base_offset = direction_to_camera * strike_distance * (1.0 - phase_t * 0.3) - direction_to_camera * WIND_UP_DISTANCE
            whip_intensity = 2.0 * (1.0 - phase_t)  # Decay whip intensity

        else:
            # Phase 4: Return (ease back to idle)
            phase_t = (attack_t - ATTACK_FOLLOW_END / ATTACK_DURATION) / ((ATTACK_DURATION - ATTACK_FOLLOW_END) / ATTACK_DURATION)
            # Smooth ease-out using cubic
            ease_t = 1.0 - math.pow(1.0 - phase_t, 3)
            strike_distance = 1.5 * stretch_factor
            remaining_offset = direction_to_camera * strike_distance * 0.7 - direction_to_camera * WIND_UP_DISTANCE
            base_offset = remaining_offset * (1.0 - ease_t)
            whip_intensity = 0.0  # No whip during return

        # Create perpendicular vectors for curl motion
        up = Vec3(0, 1, 0)
        if abs(direction_to_camera.y) > 0.99:
            up = Vec3(1, 0, 0)
        right = direction_to_camera.cross(up).normalized()
        up = right.cross(direction_to_camera).normalized()

        # Animate segments with whip wave and helical curl
        for segment in self.segments:
            i = segment.segment_index
            n = segment.total_segments

            # Normalized segment position (0 at base, 1 at tip)
            segment_t = i / max(n, 1)

            # Whip wave: Traveling wave with exponential amplitude growth
            # Formula: A * exp(k*t) * sin(ω*time - phase*i)
            wave_phase = scaled_whip_speed * attack_elapsed - (i * 0.5)
            # Exponential amplitude increases toward tip (whip acceleration effect)
            amplitude = scaled_whip_amplitude * whip_intensity * math.exp(WHIP_ACCELERATION * segment_t)
            whip_offset_x = amplitude * math.sin(wave_phase)
            whip_offset_y = amplitude * math.cos(wave_phase * 1.3)

            # Helical curl: Spiral motion increases toward tip
            # Radius increases quadratically (tip curls more)
            curl_radius = CURL_INTENSITY * (segment_t * segment_t)
            # Angle advances with time and segment index
            curl_angle = scaled_curl_speed * attack_elapsed + segment_t * CURL_TWIST_FACTOR * math.pi * 2
            curl_offset_x = curl_radius * math.cos(curl_angle) * whip_intensity
            curl_offset_y = curl_radius * math.sin(curl_angle) * whip_intensity

            # Combine all offsets
            # Scale perpendicular motion by sqrt(segment_t) to reduce base wiggle while keeping tip dynamic
            perp_scale = math.sqrt(segment_t) if segment_t > 0 else 0
            total_offset = (
                base_offset * segment_t +  # Base strike motion (increases toward tip)
                right * (whip_offset_x + curl_offset_x) * perp_scale +  # Perpendicular motion (scaled)
                up * (whip_offset_y + curl_offset_y) * perp_scale  # Perpendicular motion (scaled)
            )

            # Apply to segment with blend from idle animation
            idle_offset_x = math.sin(time * anim_speed + i * 0.3) * wave_amplitude * (i / n)
            idle_offset_y = math.cos(time * anim_speed * 1.3 + i * 0.3) * wave_amplitude * (i / n)
            idle_offset = Vec3(idle_offset_x, idle_offset_y, 0)

            # Blend attack and idle (attack dominates during attack, blend back during return)
            blend_factor = 1.0 if attack_t < 0.8 else (1.0 - (attack_t - 0.8) / 0.2)
            final_offset = total_offset * blend_factor + idle_offset * (1.0 - blend_factor)

            segment.position = segment.base_position + final_offset

        # Animate shadow spheres (same motion as segments)
        for shadow in self.shadow_spheres:
            i = shadow.segment_index
            n = len(self.segments)
            segment_t = i / max(n, 1)

            # Apply same whip wave (using scaled values)
            wave_phase = scaled_whip_speed * attack_elapsed - (i * 0.5)
            amplitude = scaled_whip_amplitude * whip_intensity * math.exp(WHIP_ACCELERATION * segment_t)
            whip_offset_x = amplitude * math.sin(wave_phase)
            whip_offset_y = amplitude * math.cos(wave_phase * 1.3)

            # Apply same curl (using scaled values)
            curl_radius = CURL_INTENSITY * (segment_t * segment_t)
            curl_angle = scaled_curl_speed * attack_elapsed + segment_t * CURL_TWIST_FACTOR * math.pi * 2
            curl_offset_x = curl_radius * math.cos(curl_angle) * whip_intensity
            curl_offset_y = curl_radius * math.sin(curl_angle) * whip_intensity

            # Combine offsets
            # Scale perpendicular motion by sqrt(segment_t) to reduce base wiggle
            perp_scale = math.sqrt(segment_t) if segment_t > 0 else 0
            total_offset = (
                base_offset * segment_t +
                right * (whip_offset_x + curl_offset_x) * perp_scale +
                up * (whip_offset_y + curl_offset_y) * perp_scale
            )

            # Blend with idle
            idle_offset_x = math.sin(time * anim_speed + i * 0.3) * wave_amplitude * (i / n)
            idle_offset_y = math.cos(time * anim_speed * 1.3 + i * 0.3) * wave_amplitude * (i / n)
            idle_offset = Vec3(idle_offset_x, idle_offset_y, 0)

            blend_factor = 1.0 if attack_t < 0.8 else (1.0 - (attack_t - 0.8) / 0.2)
            final_offset = total_offset * blend_factor + idle_offset * (1.0 - blend_factor)

            shadow.position = shadow.base_position + final_offset

        # Animate child branches (pass attack state through recursively)
        for child in self.children:
            child.update_animation(
                time, anim_speed, wave_amplitude,
                is_attacking=True,
                attack_start_time=attack_start_time,
                camera_position=camera_position,
                is_attacking_2=False,
                is_selected_for_attack_2=False,
                attack_2_start_time=0
            )

    def _apply_single_tentacle_slash(self, time, attack_start_time, camera_position, anim_speed, wave_amplitude):
        """
        Apply single tentacle slash animation (Attack 2 - more subtle).

        Simpler than whip attack:
        - Only 3 phases (wind-up, slash, return)
        - Direct slash motion (no exponential acceleration)
        - Minimal curl (no helical spiral)
        - No distance-based stretching
        - Shorter duration (0.6s vs 1.2s)
        """
        from ..core.constants import (
            ATTACK_2_DURATION, ATTACK_2_WIND_UP_END, ATTACK_2_SLASH_END, ATTACK_2_RETURN_END,
            ATTACK_2_SPEED, ATTACK_2_AMPLITUDE, ATTACK_2_CURL_INTENSITY,
            WIND_UP_DISTANCE
        )

        # Scale attack constants with creature's animation parameters
        scaled_slash_speed = ATTACK_2_SPEED * (anim_speed / 2.0)
        scaled_slash_amplitude = ATTACK_2_AMPLITUDE * (wave_amplitude / 0.05)

        # Calculate attack elapsed time (normalized 0-1)
        attack_elapsed = time - attack_start_time
        attack_t = min(attack_elapsed / ATTACK_2_DURATION, 1.0)

        # Calculate direction and distance from anchor to camera
        anchor_to_camera = camera_position - self.anchor
        distance_to_camera = anchor_to_camera.length()
        direction_to_camera = anchor_to_camera.normalized() if distance_to_camera > 0.001 else Vec3(0, 0, -1)

        # Calculate upward direction for wind-up (lift tentacle up like raising an arm)
        up_direction = Vec3(0, 1, 0)

        # Determine attack phase and calculate phase-specific motion
        if attack_t < ATTACK_2_WIND_UP_END / ATTACK_2_DURATION:
            # Phase 1: Wind-up - LIFT UP dramatically (like raising arm to strike)
            phase_t = attack_t / (ATTACK_2_WIND_UP_END / ATTACK_2_DURATION)
            # Smooth ease-in with extra snap at end
            ease_t = phase_t * phase_t * (3 - 2 * phase_t)

            # Pull back slightly AND lift up significantly
            pullback = -direction_to_camera * WIND_UP_DISTANCE * ease_t
            lift_up = up_direction * 1.2 * ease_t  # Lift 1.2 units upward
            base_offset = pullback + lift_up
            slash_intensity = 0.2

        elif attack_t < ATTACK_2_SLASH_END / ATTACK_2_DURATION:
            # Phase 2: SLASH - Really lash out toward camera aggressively
            phase_t = (attack_t - ATTACK_2_WIND_UP_END / ATTACK_2_DURATION) / ((ATTACK_2_SLASH_END - ATTACK_2_WIND_UP_END) / ATTACK_2_DURATION)
            # Explosive ease-out (fast start, slow end)
            ease_t = 1.0 - (1.0 - phase_t) ** 3

            # Much more aggressive slash distance
            slash_distance = 2.0  # Increased from 1.2 to 2.0

            # Start position: up and back
            wind_up_offset = -direction_to_camera * WIND_UP_DISTANCE + up_direction * 1.2

            # End position: far forward toward camera and down (slashing arc)
            slash_offset = direction_to_camera * slash_distance + up_direction * (-0.3 * ease_t)  # Arc downward as it slashes

            base_offset = wind_up_offset + slash_offset * ease_t
            slash_intensity = 2.5 * ease_t  # Increased from 1.5 to 2.5

        else:
            # Phase 3: Return (quick return to idle)
            phase_t = (attack_t - ATTACK_2_SLASH_END / ATTACK_2_DURATION) / ((ATTACK_2_RETURN_END - ATTACK_2_SLASH_END) / ATTACK_2_DURATION)
            # Fast ease-out
            ease_t = 1.0 - (1.0 - phase_t) ** 2
            slash_distance = 2.0
            # Return from full extension
            remaining_offset = direction_to_camera * slash_distance - direction_to_camera * WIND_UP_DISTANCE + up_direction * (-0.3)
            base_offset = remaining_offset * (1.0 - ease_t)
            slash_intensity = 0.0

        # Create perpendicular vectors for slash motion
        up = Vec3(0, 1, 0)
        if abs(direction_to_camera.y) > 0.99:
            up = Vec3(1, 0, 0)
        right = direction_to_camera.cross(up).normalized()
        up = right.cross(direction_to_camera).normalized()

        # Animate segments with simple wave and minimal curl
        for segment in self.segments:
            i = segment.segment_index
            n = segment.total_segments

            # Normalized segment position (0 at base, 1 at tip)
            segment_t = i / max(n, 1)

            # Simple traveling wave (no exponential growth)
            wave_phase = scaled_slash_speed * attack_elapsed - (i * 0.5)
            amplitude = scaled_slash_amplitude * slash_intensity * segment_t  # Linear increase toward tip
            slash_offset_x = amplitude * math.sin(wave_phase)
            slash_offset_y = amplitude * math.cos(wave_phase * 1.2)

            # Minimal curl (much less than whip attack)
            curl_radius = ATTACK_2_CURL_INTENSITY * segment_t
            curl_angle = scaled_slash_speed * 0.5 * attack_elapsed + segment_t * math.pi
            curl_offset_x = curl_radius * math.cos(curl_angle) * slash_intensity
            curl_offset_y = curl_radius * math.sin(curl_angle) * slash_intensity

            # Combine all offsets
            perp_scale = math.sqrt(segment_t) if segment_t > 0 else 0
            total_offset = (
                base_offset * segment_t +  # Base slash motion
                right * (slash_offset_x + curl_offset_x) * perp_scale +
                up * (slash_offset_y + curl_offset_y) * perp_scale
            )

            # Apply to segment with blend from idle animation
            idle_offset_x = math.sin(time * anim_speed + i * 0.3) * wave_amplitude * (i / n)
            idle_offset_y = math.cos(time * anim_speed * 1.3 + i * 0.3) * wave_amplitude * (i / n)
            idle_offset = Vec3(idle_offset_x, idle_offset_y, 0)

            # Blend attack and idle (attack dominates during slash, blend back during return)
            blend_factor = 1.0 if attack_t < 0.7 else (1.0 - (attack_t - 0.7) / 0.3)
            final_offset = total_offset * blend_factor + idle_offset * (1.0 - blend_factor)

            segment.position = segment.base_position + final_offset

        # Animate shadow spheres (same motion as segments)
        for shadow in self.shadow_spheres:
            i = shadow.segment_index
            n = len(self.segments)
            segment_t = i / max(n, 1)

            # Apply same wave
            wave_phase = scaled_slash_speed * attack_elapsed - (i * 0.5)
            amplitude = scaled_slash_amplitude * slash_intensity * segment_t
            slash_offset_x = amplitude * math.sin(wave_phase)
            slash_offset_y = amplitude * math.cos(wave_phase * 1.2)

            # Apply same curl
            curl_radius = ATTACK_2_CURL_INTENSITY * segment_t
            curl_angle = scaled_slash_speed * 0.5 * attack_elapsed + segment_t * math.pi
            curl_offset_x = curl_radius * math.cos(curl_angle) * slash_intensity
            curl_offset_y = curl_radius * math.sin(curl_angle) * slash_intensity

            # Combine offsets
            perp_scale = math.sqrt(segment_t) if segment_t > 0 else 0
            total_offset = (
                base_offset * segment_t +
                right * (slash_offset_x + curl_offset_x) * perp_scale +
                up * (slash_offset_y + curl_offset_y) * perp_scale
            )

            # Blend with idle
            idle_offset_x = math.sin(time * anim_speed + i * 0.3) * wave_amplitude * (i / n)
            idle_offset_y = math.cos(time * anim_speed * 1.3 + i * 0.3) * wave_amplitude * (i / n)
            idle_offset = Vec3(idle_offset_x, idle_offset_y, 0)

            blend_factor = 1.0 if attack_t < 0.7 else (1.0 - (attack_t - 0.7) / 0.3)
            final_offset = total_offset * blend_factor + idle_offset * (1.0 - blend_factor)

            shadow.position = shadow.base_position + final_offset

        # Animate child branches (pass attack 2 state through recursively)
        for child in self.children:
            child.update_animation(
                time, anim_speed, wave_amplitude,
                is_attacking=False,
                attack_start_time=0,
                camera_position=camera_position,
                is_attacking_2=True,
                is_selected_for_attack_2=True,
                attack_2_start_time=attack_start_time
            )

    def _apply_segment_constraints(self):
        """
        Apply distance constraints to keep segments connected.

        Ensures segments never stretch too far apart or compress too close.
        Iterates from base to tip, adjusting each segment to stay within
        distance bounds of the previous segment.
        """
        from ..core.constants import (
            SEGMENT_STRETCH_MAX, SEGMENT_COMPRESS_MIN, CONSTRAINT_ITERATIONS
        )

        # FIRST: Anchor the base segment to the body (critical!)
        if len(self.segments) > 0:
            # Keep first segment anchored at its original base position
            # This prevents tentacle from detaching from body during attack
            self.segments[0].position = self.segments[0].base_position

        # Run multiple iterations for stability (like Verlet integration)
        for iteration in range(CONSTRAINT_ITERATIONS):
            # Re-anchor first segment each iteration (in case later segments pull it)
            if len(self.segments) > 0:
                self.segments[0].position = self.segments[0].base_position

            # Iterate through segments base-to-tip (skip first segment - it's anchored)
            for i in range(1, len(self.segments)):
                current_segment = self.segments[i]
                previous_segment = self.segments[i - 1]

                # Get original distance between these segments
                if i - 1 < len(self.segment_distances):
                    original_distance = self.segment_distances[i - 1]
                else:
                    # Fallback if distances not stored (shouldn't happen)
                    continue

                # Calculate current distance
                current_pos = current_segment.position
                previous_pos = previous_segment.position
                current_distance_vec = current_pos - previous_pos
                current_distance = current_distance_vec.length()

                # Check if distance exceeds bounds
                max_distance = original_distance * SEGMENT_STRETCH_MAX
                min_distance = original_distance * SEGMENT_COMPRESS_MIN

                # If too far apart, pull closer
                if current_distance > max_distance:
                    # Calculate how much to move (pull back)
                    excess = current_distance - max_distance
                    direction = current_distance_vec.normalized()
                    # Move segment back toward previous segment
                    current_segment.position = previous_pos + direction * max_distance

                # If too close, push apart
                elif current_distance < min_distance and current_distance > 0.001:
                    # Calculate how much to move (push away)
                    deficit = min_distance - current_distance
                    direction = current_distance_vec.normalized()
                    # Move segment away from previous segment
                    current_segment.position = previous_pos + direction * min_distance

        # Apply same constraints to shadow spheres (they follow segments)
        # Anchor first shadow sphere too
        if len(self.shadow_spheres) > 0:
            self.shadow_spheres[0].position = self.shadow_spheres[0].base_position

        for iteration in range(CONSTRAINT_ITERATIONS):
            # Re-anchor first shadow each iteration
            if len(self.shadow_spheres) > 0:
                self.shadow_spheres[0].position = self.shadow_spheres[0].base_position

            for i in range(1, len(self.shadow_spheres)):
                current_shadow = self.shadow_spheres[i]
                previous_shadow = self.shadow_spheres[i - 1]

                if i - 1 < len(self.segment_distances):
                    original_distance = self.segment_distances[i - 1]
                else:
                    continue

                current_pos = current_shadow.position
                previous_pos = previous_shadow.position
                current_distance_vec = current_pos - previous_pos
                current_distance = current_distance_vec.length()

                max_distance = original_distance * SEGMENT_STRETCH_MAX
                min_distance = original_distance * SEGMENT_COMPRESS_MIN

                if current_distance > max_distance:
                    direction = current_distance_vec.normalized()
                    current_shadow.position = previous_pos + direction * max_distance

                elif current_distance < min_distance and current_distance > 0.001:
                    direction = current_distance_vec.normalized()
                    current_shadow.position = previous_pos + direction * min_distance

        # Note: Child branches are constrained by their own update_animation calls
        # No need to recurse here since update_animation already handles tree traversal

    def destroy(self):
        """Remove all segment entities, shadow spheres, and child branches."""
        # Destroy child branches first (recursive)
        for child in self.children:
            child.destroy()
        self.children.clear()

        # Destroy segments
        for segment in self.segments:
            destroy(segment)
        self.segments.clear()

        # Destroy shadow spheres
        for shadow in self.shadow_spheres:
            destroy(shadow)
        self.shadow_spheres.clear()
