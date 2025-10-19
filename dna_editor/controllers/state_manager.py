"""
State manager - handles undo/redo history.
"""

import copy
from ..core.constants import MAX_HISTORY_SIZE


class StateManager:
    """Manages undo/redo history for editor state."""

    def __init__(self):
        """Initialize state manager."""
        self.history = []
        self.history_index = -1
        self.max_history = MAX_HISTORY_SIZE

    def save_state(self, creature_type='tentacle',
                   # Tentacle parameters
                   num_tentacles=2, segments=12, algorithm='bezier', params=None,
                   thickness_base=0.25, taper_factor=0.6, branch_depth=0, branch_count=1,
                   body_scale=1.2, tentacle_color=(0.6, 0.3, 0.7), hue_shift=0.1,
                   anim_speed=2.0, wave_amplitude=0.05, pulse_speed=1.5, pulse_amount=0.05,
                   num_eyes=3, eye_size_min=0.1, eye_size_max=0.25,
                   eyeball_color=(1.0, 1.0, 1.0), pupil_color=(0.0, 0.0, 0.0),
                   # Blob parameters
                   blob_branch_depth=2, blob_branch_count=2, cube_size_min=0.3, cube_size_max=0.8,
                   cube_spacing=1.2, blob_color=(0.2, 0.8, 0.4), blob_transparency=0.7,
                   jiggle_speed=2.0, blob_pulse_amount=0.1,
                   # Polyp parameters
                   num_spheres=4, base_sphere_size=0.8, polyp_color=(0.6, 0.3, 0.7),
                   curve_intensity=0.4, polyp_tentacles_per_sphere=6, polyp_segments=12,
                   # Starfish parameters
                   num_arms=5, arm_segments=6, central_body_size=0.8, arm_base_thickness=0.4,
                   starfish_color=(0.9, 0.5, 0.3), curl_factor=0.3, starfish_anim_speed=1.5,
                   starfish_pulse_amount=0.06,
                   # Dragon parameters
                   dragon_segments=15, dragon_thickness=0.3, dragon_taper=0.6,
                   dragon_head_scale=3.0, dragon_body_color=(200, 40, 40),
                   dragon_head_color=(255, 200, 50), dragon_weave_amplitude=0.5,
                   dragon_bob_amplitude=0.3, dragon_anim_speed=1.5,
                   dragon_num_eyes=2, dragon_eye_size=0.15,
                   dragon_eyeball_color=(255, 200, 50), dragon_pupil_color=(20, 0, 0),
                   dragon_mouth_size=0.25, dragon_mouth_color=(20, 0, 0),
                   dragon_num_whiskers_per_side=2, dragon_whisker_segments=4,
                   dragon_whisker_thickness=0.05):
        """
        Save current state to history.

        Args:
            creature_type: 'tentacle', 'blob', or 'polyp'
            [Tentacle parameters]
            num_tentacles: Number of tentacles
            segments: Segments per tentacle
            algorithm: Current algorithm
            params: Algorithm parameters dict
            thickness_base: Base thickness
            taper_factor: Taper factor
            branch_depth: Branching depth (tentacles)
            branch_count: Number of branches per tentacle
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
            [Blob parameters]
            blob_branch_depth: Branching depth (blob cubes)
            blob_branch_count: Branches per level (blob cubes)
            cube_size_min: Minimum cube size
            cube_size_max: Maximum cube size
            cube_spacing: Cube spacing
            blob_color: Blob color (RGB tuple 0-1)
            blob_transparency: Transparency (0-1)
            jiggle_speed: Jiggle animation speed
            blob_pulse_amount: Pulse intensity
            [Polyp parameters]
            num_spheres: Number of spheres in spine
            base_sphere_size: Size of root sphere
            polyp_color: Spine/tentacle color (RGB tuple 0-1)
            curve_intensity: Spine curve amount (0-1)
            polyp_tentacles_per_sphere: Number of tentacles per sphere
            polyp_segments: Segments per tentacle (length)
            [Starfish parameters]
            num_arms: Number of arms (5-8)
            arm_segments: Segments per arm (4-10)
            central_body_size: Size of central body sphere (0.4-1.5)
            arm_base_thickness: Base thickness of arms (0.2-0.6)
            starfish_color: Base color (RGB tuple 0-1)
            curl_factor: Arm curvature amount (0-0.8)
            starfish_anim_speed: Animation speed
            starfish_pulse_amount: Pulse intensity
        """
        state = {
            'creature_type': creature_type,
            # Tentacle parameters
            'num_tentacles': num_tentacles,
            'segments': segments,
            'algorithm': algorithm,
            'params': copy.deepcopy(params) if params else {},
            'thickness_base': thickness_base,
            'taper_factor': taper_factor,
            'branch_depth': branch_depth,
            'branch_count': branch_count,
            'body_scale': body_scale,
            'tentacle_color': tentacle_color,
            'hue_shift': hue_shift,
            'anim_speed': anim_speed,
            'wave_amplitude': wave_amplitude,
            'pulse_speed': pulse_speed,
            'pulse_amount': pulse_amount,
            'num_eyes': num_eyes,
            'eye_size_min': eye_size_min,
            'eye_size_max': eye_size_max,
            'eyeball_color': eyeball_color,
            'pupil_color': pupil_color,
            # Blob parameters
            'blob_branch_depth': blob_branch_depth,
            'blob_branch_count': blob_branch_count,
            'cube_size_min': cube_size_min,
            'cube_size_max': cube_size_max,
            'cube_spacing': cube_spacing,
            'blob_color': blob_color,
            'blob_transparency': blob_transparency,
            'jiggle_speed': jiggle_speed,
            'blob_pulse_amount': blob_pulse_amount,
            # Polyp parameters
            'num_spheres': num_spheres,
            'base_sphere_size': base_sphere_size,
            'polyp_color': polyp_color,
            'curve_intensity': curve_intensity,
            'polyp_tentacles_per_sphere': polyp_tentacles_per_sphere,
            'polyp_segments': polyp_segments,
            # Starfish parameters
            'num_arms': num_arms,
            'arm_segments': arm_segments,
            'central_body_size': central_body_size,
            'arm_base_thickness': arm_base_thickness,
            'starfish_color': starfish_color,
            'curl_factor': curl_factor,
            'starfish_anim_speed': starfish_anim_speed,
            'starfish_pulse_amount': starfish_pulse_amount,
            # Dragon parameters
            'dragon_segments': dragon_segments,
            'dragon_thickness': dragon_thickness,
            'dragon_taper': dragon_taper,
            'dragon_head_scale': dragon_head_scale,
            'dragon_body_color': dragon_body_color,
            'dragon_head_color': dragon_head_color,
            'dragon_weave_amplitude': dragon_weave_amplitude,
            'dragon_bob_amplitude': dragon_bob_amplitude,
            'dragon_anim_speed': dragon_anim_speed,
            'dragon_num_eyes': dragon_num_eyes,
            'dragon_eye_size': dragon_eye_size,
            'dragon_eyeball_color': dragon_eyeball_color,
            'dragon_pupil_color': dragon_pupil_color,
            'dragon_mouth_size': dragon_mouth_size,
            'dragon_mouth_color': dragon_mouth_color,
            'dragon_num_whiskers_per_side': dragon_num_whiskers_per_side,
            'dragon_whisker_segments': dragon_whisker_segments,
            'dragon_whisker_thickness': dragon_whisker_thickness
        }

        # Clear future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        # Add new state
        self.history.append(state)

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1

    def undo(self):
        """
        Undo to previous state.

        Returns:
            Previous state dict or None if can't undo
        """
        if self.history_index > 0:
            self.history_index -= 1
            return self._get_current_state()
        return None

    def redo(self):
        """
        Redo to next state.

        Returns:
            Next state dict or None if can't redo
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self._get_current_state()
        return None

    def _get_current_state(self):
        """Get current state with deep copy of params."""
        state = self.history[self.history_index]

        return {
            'creature_type': state.get('creature_type', 'tentacle'),
            # Tentacle parameters
            'num_tentacles': state.get('num_tentacles', 2),
            'segments': state.get('segments', 12),
            'algorithm': state.get('algorithm', 'bezier'),
            'params': copy.deepcopy(state.get('params', {})),
            'thickness_base': state.get('thickness_base', 0.25),
            'taper_factor': state.get('taper_factor', 0.6),
            'branch_depth': state.get('branch_depth', 0),
            'branch_count': state.get('branch_count', 1),
            'body_scale': state.get('body_scale', 1.2),
            'tentacle_color': state.get('tentacle_color', (0.6, 0.3, 0.7)),
            'hue_shift': state.get('hue_shift', 0.1),
            'anim_speed': state.get('anim_speed', 2.0),
            'wave_amplitude': state.get('wave_amplitude', 0.05),
            'pulse_speed': state.get('pulse_speed', 1.5),
            'pulse_amount': state.get('pulse_amount', 0.05),
            'num_eyes': state.get('num_eyes', 3),
            'eye_size_min': state.get('eye_size_min', 0.1),
            'eye_size_max': state.get('eye_size_max', 0.25),
            'eyeball_color': state.get('eyeball_color', (1.0, 1.0, 1.0)),
            'pupil_color': state.get('pupil_color', (0.0, 0.0, 0.0)),
            # Blob parameters
            'blob_branch_depth': state.get('blob_branch_depth', 2),
            'blob_branch_count': state.get('blob_branch_count', 2),
            'cube_size_min': state.get('cube_size_min', 0.3),
            'cube_size_max': state.get('cube_size_max', 0.8),
            'cube_spacing': state.get('cube_spacing', 1.2),
            'blob_color': state.get('blob_color', (0.2, 0.8, 0.4)),
            'blob_transparency': state.get('blob_transparency', 0.7),
            'jiggle_speed': state.get('jiggle_speed', 2.0),
            'blob_pulse_amount': state.get('blob_pulse_amount', 0.1),
            # Polyp parameters
            'num_spheres': state.get('num_spheres', 4),
            'base_sphere_size': state.get('base_sphere_size', 0.8),
            'polyp_color': state.get('polyp_color', (0.6, 0.3, 0.7)),
            'curve_intensity': state.get('curve_intensity', 0.4),
            'polyp_tentacles_per_sphere': state.get('polyp_tentacles_per_sphere', 6),
            'polyp_segments': state.get('polyp_segments', 12),
            # Starfish parameters
            'num_arms': state.get('num_arms', 5),
            'arm_segments': state.get('arm_segments', 6),
            'central_body_size': state.get('central_body_size', 0.8),
            'arm_base_thickness': state.get('arm_base_thickness', 0.4),
            'starfish_color': state.get('starfish_color', (0.9, 0.5, 0.3)),
            'curl_factor': state.get('curl_factor', 0.3),
            'starfish_anim_speed': state.get('starfish_anim_speed', 1.5),
            'starfish_pulse_amount': state.get('starfish_pulse_amount', 0.06),
            # Dragon parameters
            'dragon_segments': state.get('dragon_segments', 15),
            'dragon_thickness': state.get('dragon_thickness', 0.3),
            'dragon_taper': state.get('dragon_taper', 0.6),
            'dragon_head_scale': state.get('dragon_head_scale', 3.0),
            'dragon_body_color': state.get('dragon_body_color', (200, 40, 40)),
            'dragon_head_color': state.get('dragon_head_color', (255, 200, 50)),
            'dragon_weave_amplitude': state.get('dragon_weave_amplitude', 0.5),
            'dragon_bob_amplitude': state.get('dragon_bob_amplitude', 0.3),
            'dragon_anim_speed': state.get('dragon_anim_speed', 1.5),
            'dragon_num_eyes': state.get('dragon_num_eyes', 2),
            'dragon_eye_size': state.get('dragon_eye_size', 0.15),
            'dragon_eyeball_color': state.get('dragon_eyeball_color', (255, 200, 50)),
            'dragon_pupil_color': state.get('dragon_pupil_color', (20, 0, 0)),
            'dragon_mouth_size': state.get('dragon_mouth_size', 0.25),
            'dragon_mouth_color': state.get('dragon_mouth_color', (20, 0, 0)),
            'dragon_num_whiskers_per_side': state.get('dragon_num_whiskers_per_side', 2),
            'dragon_whisker_segments': state.get('dragon_whisker_segments', 4),
            'dragon_whisker_thickness': state.get('dragon_whisker_thickness', 0.05)
        }

    def can_undo(self):
        """Check if undo is available."""
        return self.history_index > 0

    def can_redo(self):
        """Check if redo is available."""
        return self.history_index < len(self.history) - 1
