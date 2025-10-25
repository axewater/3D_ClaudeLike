"""
Eye model - eyeball with pupil and random blinking animation.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from ..shaders import get_shader_for_scale


class Eye:
    """An eye with eyeball and pupil that blinks randomly."""

    def __init__(self, position, size, eyeball_color=(1.0, 1.0, 1.0),
                 pupil_color=(0.0, 0.0, 0.0), parent=None, toon_shader=None, toon_shader_lite=None):
        """
        Create an eye at the given position.

        Args:
            position: Vec3 position on body surface
            size: Base size of eyeball (pupil scaled proportionally)
            eyeball_color: RGB tuple for eyeball color (default white)
            pupil_color: RGB tuple for pupil color (default black)
            parent: Parent entity
            toon_shader: Full toon shader instance
            toon_shader_lite: Lite toon shader for small eyes (performance optimization)
        """
        self.position = position
        self.base_size = size
        self.eyeball_color = eyeball_color
        self.pupil_color = pupil_color
        self.parent = parent
        self.toon_shader = toon_shader
        self.toon_shader_lite = toon_shader_lite

        # Blink animation state
        self.blink_state = 'idle'  # 'idle', 'closing', 'opening'
        self.blink_start_time = 0
        self.next_blink_time = self._schedule_next_blink()

        # Calculate direction from origin to eye position (surface normal)
        self.surface_normal = position.normalized() if position.length() > 0.001 else Vec3(0, 0, 1)

        # Create eyeball sphere with appropriate shader based on size
        eyeball_params = {
            'model': 'sphere',
            'color': color.rgb(*[int(c * 255) for c in eyeball_color]),
            'position': position,
            'scale': size,
            'parent': parent
        }
        # Choose shader based on eyeball size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(size, toon_shader, toon_shader_lite)
            eyeball_params['shader'] = chosen_shader
        elif toon_shader is not None:
            eyeball_params['shader'] = toon_shader
        self.eyeball = Entity(**eyeball_params)

        # Create pupil sphere (smaller, positioned slightly forward along surface normal)
        pupil_size = size * 0.4  # Pupil is 40% of eyeball size
        pupil_offset = self.surface_normal * (size * 0.5)  # Position on front of eyeball
        pupil_params = {
            'model': 'sphere',
            'color': color.rgb(*[int(c * 255) for c in pupil_color]),
            'position': position + pupil_offset,
            'scale': pupil_size,
            'parent': parent
        }
        # Choose shader based on pupil size (LOD optimization)
        if toon_shader is not None and toon_shader_lite is not None:
            chosen_shader = get_shader_for_scale(pupil_size, toon_shader, toon_shader_lite)
            pupil_params['shader'] = chosen_shader
        elif toon_shader is not None:
            pupil_params['shader'] = toon_shader
        self.pupil = Entity(**pupil_params)

        # Store base positions for animation
        self.eyeball_base_position = position
        self.pupil_base_position = position + pupil_offset

    def _schedule_next_blink(self):
        """Schedule the next blink at a random interval."""
        from ..core.constants import EYE_BLINK_INTERVAL_MIN, EYE_BLINK_INTERVAL_MAX
        import time
        interval = random.uniform(EYE_BLINK_INTERVAL_MIN, EYE_BLINK_INTERVAL_MAX)
        return time.time() + interval

    def update_animation(self, time):
        """
        Update eye animation (blinking).

        Args:
            time: Current animation time (seconds)
        """
        from ..core.constants import EYE_BLINK_DURATION

        # Check if it's time to blink
        current_time = time if hasattr(time, '__float__') else 0
        import time as time_module
        real_time = time_module.time()

        # State machine for blinking
        if self.blink_state == 'idle':
            # Check if it's time to start a blink
            if real_time >= self.next_blink_time:
                self.blink_state = 'closing'
                self.blink_start_time = real_time

        elif self.blink_state == 'closing':
            # Calculate blink progress (0-1 over half of blink duration)
            elapsed = real_time - self.blink_start_time
            close_duration = EYE_BLINK_DURATION / 2

            if elapsed < close_duration:
                # Ease-in-out closing
                t = elapsed / close_duration
                ease_t = t * t * (3 - 2 * t)  # Smoothstep
                # Scale Y down from 1.0 to 0.1
                scale_y = 1.0 - (0.9 * ease_t)

                # Apply scale (keep X and Z at base size)
                self.eyeball.scale = Vec3(self.base_size, self.base_size * scale_y, self.base_size)
                pupil_size = self.base_size * 0.4
                self.pupil.scale = Vec3(pupil_size, pupil_size * scale_y, pupil_size)
            else:
                # Transition to opening
                self.blink_state = 'opening'
                # Fully closed position
                self.eyeball.scale = Vec3(self.base_size, self.base_size * 0.1, self.base_size)
                pupil_size = self.base_size * 0.4
                self.pupil.scale = Vec3(pupil_size, pupil_size * 0.1, pupil_size)

        elif self.blink_state == 'opening':
            # Calculate blink progress (0-1 over half of blink duration)
            elapsed = real_time - self.blink_start_time - (EYE_BLINK_DURATION / 2)
            open_duration = EYE_BLINK_DURATION / 2

            if elapsed < open_duration:
                # Ease-in-out opening
                t = elapsed / open_duration
                ease_t = t * t * (3 - 2 * t)  # Smoothstep
                # Scale Y up from 0.1 to 1.0
                scale_y = 0.1 + (0.9 * ease_t)

                # Apply scale
                self.eyeball.scale = Vec3(self.base_size, self.base_size * scale_y, self.base_size)
                pupil_size = self.base_size * 0.4
                self.pupil.scale = Vec3(pupil_size, pupil_size * scale_y, pupil_size)
            else:
                # Blink complete, return to idle
                self.blink_state = 'idle'
                self.eyeball.scale = Vec3(self.base_size, self.base_size, self.base_size)
                pupil_size = self.base_size * 0.4
                self.pupil.scale = Vec3(pupil_size, pupil_size, pupil_size)
                # Schedule next blink
                self.next_blink_time = self._schedule_next_blink()

    def destroy(self):
        """Remove eyeball and pupil entities."""
        if self.eyeball:
            destroy(self.eyeball)
        if self.pupil:
            destroy(self.pupil)
