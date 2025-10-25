"""
StarfishCreature model - radial symmetry creature with articulated arms.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from .tentacle import Tentacle
from .eye import Eye
from ..core.curves import bezier_curve
from ..core.constants import GOLDEN_RATIO, GOLDEN_ANGLE
from ..shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale


class StarfishArm:
    """Single multi-jointed spider leg with rigid segments and visible joints."""

    def __init__(self, central_body_position, arm_index, total_arms,
                 arm_segments, base_thickness, central_body_size, base_color,
                 parent, toon_shader=None, toon_shader_lite=None, curl_factor=0.3):
        """
        Create a spider-like leg.

        Args:
            central_body_position: Vec3 position of central body
            arm_index: Index of this leg (0 to total_arms-1)
            total_arms: Total number of legs on starfish
            arm_segments: Number of segments in this leg (affects leg proportions)
            base_thickness: Thickness of leg at base
            central_body_size: Size of central body (for anchor positioning)
            base_color: RGB tuple for leg color
            parent: Parent entity (scene root)
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small spheres (performance optimization)
            curl_factor: Affects leg reach/extension (0-1, higher = longer reach)
        """
        self.central_body_position = central_body_position
        self.arm_index = arm_index
        self.total_arms = total_arms
        self.arm_segments = arm_segments
        self.base_color = base_color
        self.curl_factor = curl_factor
        self.toon_shader = toon_shader
        self.toon_shader_lite = toon_shader_lite

        # Leg components
        self.leg_segments = []  # Cylinder segments (femur, tibia, tarsus)
        self.joints = []  # Joint spheres (hip, knee, ankle)
        self.joint_positions = []  # Calculated joint positions

        # Calculate leg angle in radial pattern (360 / total_arms degrees per leg)
        self.angle = (arm_index / total_arms) * math.pi * 2

        # Random phase offset for animation variation
        self.animation_phase_offset = random.random() * math.pi * 2

        # Generate spider leg using mathematical joint positioning
        self._generate_spider_leg(central_body_size, base_thickness, parent)

    def _generate_spider_leg(self, central_body_size, base_thickness, parent):
        """Generate multi-jointed spider leg using mathematical positioning."""
        # Calculate leg direction based on radial angle
        direction_x = math.cos(self.angle)
        direction_z = math.sin(self.angle)

        # === CALCULATE LEG PATH ===
        # Total leg reach influenced by curl_factor
        leg_reach = 1.2 + (self.curl_factor * 0.5)
        leg_height = 2.0 + (self.curl_factor * 0.4)  # Total vertical drop

        # === GENERATE JOINT POSITIONS ===
        # Create arm_segments joints distributed along the leg path
        # Leg path: starts at body, extends outward and downward
        self.joint_positions = []

        hip_offset = (central_body_size / 2) * 0.9

        for i in range(self.arm_segments):
            # Progress along leg (0.0 at hip, 1.0 at foot)
            t = i / max(self.arm_segments - 1, 1)

            # Outward distance: starts at hip, extends to leg_reach
            outward = hip_offset + (leg_reach * t)

            # Downward curve: slight outward arc then straight down
            # Early segments (femur/thigh): gentle downward slope
            # Later segments (tibia/foot): steeper downward
            if t < 0.4:
                # Upper leg: gentle slope
                down = (leg_height * t * 0.3)
            else:
                # Lower leg: steeper drop
                down = (leg_height * 0.3 * 0.4) + (leg_height * (t - 0.4) * 1.3)

            joint_pos = self.central_body_position + Vec3(
                direction_x * outward,
                -down,
                direction_z * outward
            )
            self.joint_positions.append(joint_pos)

        # === CREATE LEG SEGMENTS ===
        # Connect consecutive joints with thin cylinders
        for i in range(len(self.joint_positions) - 1):
            start_joint = self.joint_positions[i]
            end_joint = self.joint_positions[i + 1]

            # Thickness decreases along leg (thinner toward foot)
            segment_t = i / max(len(self.joint_positions) - 2, 1)
            thickness = base_thickness * (0.25 - segment_t * 0.1)  # MUCH thinner: 0.25 → 0.15
            thickness = max(thickness, 0.05)

            # Color darkens slightly along leg
            color_factor = 1.0 - (segment_t * 0.2)
            segment_color = tuple(c * color_factor for c in self.base_color)

            self._create_leg_segment(start_joint, end_joint, thickness, segment_color, parent)

        # === CREATE JOINT SPHERES ===
        # Joints cover the connections between segments (hide any gaps)
        for i, joint_pos in enumerate(self.joint_positions):
            # Joint size matches segment thickness at this position
            joint_t = i / max(len(self.joint_positions) - 1, 1)
            joint_size = base_thickness * (0.3 - joint_t * 0.12)  # Slightly larger than segments to cover gaps
            joint_size = max(joint_size, 0.06)

            # Joints are darker than leg segments
            joint_color = tuple(c * 0.7 for c in self.base_color)

            joint_params = {
                'model': 'sphere',
                'color': color.rgb(*joint_color),
                'scale': joint_size,
                'position': joint_pos,
                'parent': parent
            }

            # Choose shader based on joint size (LOD optimization)
            if self.toon_shader is not None and self.toon_shader_lite is not None:
                chosen_shader = get_shader_for_scale(joint_size, self.toon_shader, self.toon_shader_lite)
                joint_params['shader'] = chosen_shader
            elif self.toon_shader is not None:
                joint_params['shader'] = self.toon_shader

            joint = Entity(**joint_params)
            joint.base_position = joint_pos
            joint.joint_index = i
            self.joints.append(joint)

    def _create_leg_segment(self, start_pos, end_pos, thickness, segment_color, parent):
        """Create cylindrical leg segment between two joints."""
        # Calculate segment position, rotation, and length
        midpoint = (start_pos + end_pos) / 2
        length = (end_pos - start_pos).length()

        # Create cylinder entity (using cube stretched along Y axis) with appropriate shader
        segment_params = {
            'model': 'cube',
            'color': color.rgb(*segment_color),
            'position': midpoint,
            'scale': (thickness, length / 2, thickness),
            'parent': parent
        }

        # Choose shader based on thickness (LOD optimization)
        if self.toon_shader is not None and self.toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(thickness, self.toon_shader, self.toon_shader_lite)
            segment_params['shader'] = chosen_shader
        elif self.toon_shader is not None:
            segment_params['shader'] = self.toon_shader

        segment = Entity(**segment_params)

        # Orient segment from start to end
        segment.look_at(start_pos, axis=Vec3.up)

        # Store base transform for potential animation
        segment.base_position = midpoint
        segment.base_scale = segment.scale
        segment.start_joint = start_pos
        segment.end_joint = end_pos

        self.leg_segments.append(segment)

    def update_animation(self, time, anim_speed, pulse_amount,
                        is_attacking=False, attack_progress=0.0, camera_position=None):
        """
        Update leg animation.

        Args:
            time: Current animation time
            anim_speed: Animation speed multiplier
            pulse_amount: Pulse intensity
            is_attacking: Whether attack is in progress
            attack_progress: Attack animation progress (0-1)
            camera_position: Camera position for attack targeting
        """
        if is_attacking and attack_progress < 1.0:
            # Attack animation: lift legs then stomp down
            if attack_progress < 0.3:
                # Lift phase (0.0 - 0.3)
                phase_t = attack_progress / 0.3
                ease_t = phase_t * phase_t  # Ease-in quad

                # Lift all joints upward slightly
                lift_amount = ease_t * 0.3

                for joint in self.joints:
                    joint.position = joint.base_position + Vec3(0, lift_amount, 0)

            elif attack_progress < 0.5:
                # Stomp down phase (0.3 - 0.5)
                phase_t = (attack_progress - 0.3) / 0.2
                ease_t = 1.0 - (1.0 - phase_t) ** 3  # Ease-out cubic (fast stomp)

                # Return to base with slight overshoot
                lift_amount = 0.3 * (1.0 - ease_t)
                overshoot = -0.1 * ease_t * (1.0 - ease_t) * 4  # Bounce effect

                for joint in self.joints:
                    joint.position = joint.base_position + Vec3(0, lift_amount + overshoot, 0)

            else:
                # Settle phase (0.5 - 1.0) - return to rest
                phase_t = (attack_progress - 0.5) / 0.5
                ease_t = 1.0 - (1.0 - phase_t) ** 2  # Ease-out quad

                # Interpolate back to base positions
                for joint in self.joints:
                    # Any remaining offset gradually returns to zero
                    joint.position = joint.base_position

        else:
            # Idle: STATIC - legs remain rigid (no waving animation)
            # Legs stay at base positions for creepy spider look
            for joint in self.joints:
                joint.position = joint.base_position

    def destroy(self):
        """Cleanup leg entities."""
        for segment in self.leg_segments:
            destroy(segment)
        for joint in self.joints:
            destroy(joint)
        self.leg_segments.clear()
        self.joints.clear()
        self.joint_positions.clear()


class StarfishCreature:
    """Spider-like creature with radial symmetry and multi-jointed legs."""

    def __init__(self, num_arms=5, arm_segments=6, central_body_size=0.8,
                 arm_base_thickness=0.4, starfish_color=(0.9, 0.5, 0.3),
                 curl_factor=0.3, anim_speed=1.5, pulse_amount=0.06):
        """
        Create a starfish creature with spider-like legs.

        Args:
            num_arms: Number of legs (4-8)
            arm_segments: Affects leg proportions (4-10)
            central_body_size: Size of central body sphere (0.4-1.5)
            arm_base_thickness: Base thickness of legs (0.2-0.6)
            starfish_color: Base color (RGB tuple 0-1)
            curl_factor: Leg reach/extension amount (0-0.8)
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

        # Eye stalk (tentacle with eye at tip)
        self.eye_stalk = None
        self.eye_stalk_eye = None
        self.eye_stalk_segments = 12
        self.eye_stalk_thickness = 0.15
        self.eye_size = 0.25

        # Create toon shaders (shared across all parts)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in StarfishCreature, using default rendering")

        self.toon_shader_lite = create_toon_shader_lite()
        if self.toon_shader_lite is None:
            print("WARNING: Lite toon shader creation failed in StarfishCreature, will use full shader")

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

        # Choose shader based on body size (LOD optimization)
        if self.toon_shader is not None and self.toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(self.central_body_size, self.toon_shader, self.toon_shader_lite)
            body_params['shader'] = chosen_shader
        elif self.toon_shader is not None:
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
                toon_shader_lite=self.toon_shader_lite,
                curl_factor=self.curl_factor
            )

            self.arms.append(arm)

        # Create eye stalk (upward tentacle with eye)
        self._create_eye_stalk()

    def _create_eye_stalk(self):
        """Create upward-pointing tentacle with eye at tip from center of body."""
        # Destroy existing eye stalk if it exists
        if self.eye_stalk is not None:
            self.eye_stalk.destroy()
            self.eye_stalk = None
        if self.eye_stalk_eye is not None:
            self.eye_stalk_eye.destroy()
            self.eye_stalk_eye = None

        # Anchor point: exact center of central body
        central_position = Vec3(0, 0, 0)
        anchor_point = central_position

        # Target point: curve upward then forward (periscope/question-mark shape)
        # Eye stalk height based on central body size (about 1.5x body radius)
        stalk_height = self.central_body_size * 1.5
        forward_bend = stalk_height * 0.5  # Bend forward 50% of height
        # Forward is negative Z direction
        target_point = central_position + Vec3(0, stalk_height, -forward_bend)

        # Calculate alternate/complementary color from main body
        # Use color inversion with slight adjustment for visual appeal
        r, g, b = self.starfish_color
        stalk_color = (
            1.0 - r * 0.7,  # Partial inversion
            1.0 - g * 0.7,
            1.0 - b * 0.7
        )

        # Create tentacle using Fourier algorithm for organic sway
        # Use fewer waves and lower amplitude for subtle "looking around" motion
        algorithm_params = {
            'num_waves': 2,
            'amplitude': 0.1
        }

        self.eye_stalk = Tentacle(
            parent=self.root,
            anchor=anchor_point,
            target=target_point,
            segments=self.eye_stalk_segments,
            algorithm='fourier',
            color_rgb=stalk_color,
            algorithm_params=algorithm_params,
            thickness_base=self.eye_stalk_thickness,
            taper_factor=0.7,  # Strong taper toward tip
            branch_depth=0,  # No branches
            branch_count=0,
            current_depth=0,
            toon_shader=self.toon_shader,
            toon_shader_lite=self.toon_shader_lite
        )

        # Create eye at tentacle tip
        if len(self.eye_stalk.segments) > 0:
            tip_segment = self.eye_stalk.segments[-1]
            tip_position = tip_segment.position

            # Eye colors: use lighter/contrasting colors
            eyeball_color = (0.95, 0.95, 0.85)  # Off-white
            pupil_color = (0.0, 0.0, 0.0)  # Black

            self.eye_stalk_eye = Eye(
                position=tip_position,
                size=self.eye_size,
                eyeball_color=eyeball_color,
                pupil_color=pupil_color,
                parent=self.root,
                toon_shader=self.toon_shader,
                toon_shader_lite=self.toon_shader_lite
            )

    def get_bottom_extent(self):
        """
        Calculate the lowest Y coordinate of the creature (foot tip position).

        Returns:
            float: Absolute Y position of the lowest point (foot tips)
        """
        # Foot tip calculation based on leg joint positions
        # This mirrors the calculation in StarfishArm._generate_spider_leg()

        # Calculate total leg height (vertical drop from hip to foot)
        leg_height = 2.0 + (self.curl_factor * 0.4)

        # The last joint (foot tip) is at t=1.0 on the leg path
        # Calculate its downward position using the same formula
        t = 1.0  # Foot tip is at the end

        # Upper leg portion (t < 0.4): gentle slope
        down_upper = leg_height * 0.4 * 0.3

        # Lower leg portion (t >= 0.4): steeper drop
        down_lower = leg_height * (t - 0.4) * 1.3

        foot_down = down_upper + down_lower

        # Return negative Y (since foot extends downward from center at Y=0)
        return -foot_down

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

        # Animate eye stalk tentacle
        if self.eye_stalk is not None:
            # Animate tentacle with idle motion (no attack animation for eye stalk)
            self.eye_stalk.update_animation(
                time=time,
                anim_speed=self.anim_speed * 0.8,  # Slightly slower for subtle motion
                wave_amplitude=0.08  # Gentle sway
            )

            # Update eye position to follow tentacle tip (like medusa pattern)
            if self.eye_stalk_eye is not None and len(self.eye_stalk.segments) > 0:
                # Get tip segment position
                tip_segment = self.eye_stalk.segments[-1]
                tip_position = tip_segment.position

                # Eye always looks forward (negative Z direction)
                forward_direction = Vec3(0, 0, -1)

                # Update eyeball position to tip
                self.eye_stalk_eye.eyeball.position = tip_position

                # Calculate pupil offset in forward direction
                pupil_offset = forward_direction * (self.eye_stalk_eye.base_size * 0.5)
                self.eye_stalk_eye.pupil.position = tip_position + pupil_offset

                # Update base positions for animation
                self.eye_stalk_eye.eyeball_base_position = tip_position
                self.eye_stalk_eye.pupil_base_position = tip_position + pupil_offset

                # Animate eye (blinking)
                self.eye_stalk_eye.update_animation(time)

    def destroy(self):
        """Cleanup all entities."""
        for arm in self.arms:
            arm.destroy()
        if hasattr(self, 'central_body'):
            destroy(self.central_body)
        if self.eye_stalk is not None:
            self.eye_stalk.destroy()
        if self.eye_stalk_eye is not None:
            self.eye_stalk_eye.destroy()
        destroy(self.root)
