"""
Ursina renderer - manages 3D creature rendering in separate window.

Handles Ursina initialization, scene creation, and creature management
without Qt widget dependencies.
"""

from PyQt6.QtCore import QTimer
import sys
import os
from PIL import Image
import numpy as np


def create_radial_gradient_texture(size=256, max_opacity=200, falloff_power=2):
    """
    Create a circular gradient texture (black center, transparent edges).

    Args:
        size: Texture resolution (size x size pixels)
        max_opacity: Maximum opacity at center (0-255)
        falloff_power: Gradient curve (1=linear, 2=quadratic, 3=cubic)

    Returns:
        PIL Image with RGBA channels
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = np.array(img)

    center = size / 2
    max_dist = center  # Radius to edge

    for y in range(size):
        for x in range(size):
            # Distance from center
            dist = ((x - center)**2 + (y - center)**2)**0.5

            # Normalize to 0-1, inverted (center=1, edge=0)
            if dist <= max_dist:
                alpha = 1 - (dist / max_dist)
                # Apply easing curve for softer falloff
                alpha = alpha ** falloff_power
                pixels[y, x] = [0, 0, 0, int(alpha * max_opacity)]
            else:
                pixels[y, x] = [0, 0, 0, 0]

    return Image.fromarray(pixels)


class UrsinaRenderer:
    """Manages Ursina 3D rendering in separate window."""

    def __init__(self):
        """Initialize Ursina renderer."""
        self.creature = None
        self.ursina_app = None
        self.animation_time = 0
        self.timer = None

        # Scene components
        self.ground = None
        self.sky = None
        self.shadow = None
        self.lighting = {}

        # Camera orbit state
        self.camera_angle = 0
        self.camera_height = 2
        self.camera_distance = 6

        # Ursina module references (set in _init_ursina)
        self.Entity = None
        self.camera = None
        self.color = None
        self.held_keys = None
        self.mouse = None
        self.window = None
        self.math = None

        self._init_ursina()

    def _init_ursina(self):
        """Initialize Ursina application and scene."""
        try:
            # Suppress Panda3D verbose logging
            import os
            import sys
            from io import StringIO
            import warnings

            # Suppress all warnings (including PNG iCCP warnings)
            warnings.filterwarnings('ignore')

            # Set Panda3D config via environment variables (more reliable)
            os.environ['PANDA_PRC_DIR'] = ''
            os.environ['PANDA_PRC_PATH'] = ''

            # Load custom config that suppresses logging
            from panda3d.core import loadPrcFileData
            loadPrcFileData('', '''
                notify-level error
                notify-level-pnmimage error
                default-directnotify-level error
                paste-emit-keystrokes 0
            ''')

            # Redirect stdout/stderr to suppress remaining output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            # Import Ursina (will use our config)
            from ursina import Ursina, Entity, camera, Sky, color, held_keys, mouse
            from ursina import AmbientLight, DirectionalLight, PointLight
            from ursina import window, Texture
            import math

            # Restore stdout/stderr after imports
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Store module references as instance attributes
            self.Entity = Entity
            self.camera = camera
            self.Sky = Sky
            self.color = color
            self.held_keys = held_keys
            self.mouse = mouse
            self.AmbientLight = AmbientLight
            self.DirectionalLight = DirectionalLight
            self.PointLight = PointLight
            self.window = window
            self.Texture = Texture
            self.math = math

            # Suppress Ursina initialization output temporarily
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            # Create Ursina app
            self.ursina_app = Ursina(
                title="DNA Editor - 3D Preview",
                borderless=False,
                fullscreen=False,
                size=(900, 700),
                position=(400, 50)
            )

            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Set window background (matches sky gradient bottom)
            self.window.color = self.color.rgb(0.9, 0.5, 0.65)

            # Create scene
            self._create_scene()

            # Set up camera with orbit position
            self.camera.position = (0, self.camera_height, -self.camera_distance)
            self.camera.look_at((0, 0, 0))
            self.camera.fov = 60

            # Start animation timer
            self.timer = QTimer()
            self.timer.timeout.connect(self._update_animation)
            self.timer.start(16)  # ~60 FPS

        except Exception as e:
            print(f"ERROR: Failed to initialize Ursina: {e}")
            import traceback
            traceback.print_exc()

    def _create_scene(self):
        """Create scene elements (ground, sky, lighting)."""
        # Import constants
        from ..core.constants import (
            GROUND_Y, GROUND_COLOR, SHADOW_Y,
            SKY_GRADIENT_BOTTOM, SKY_GRADIENT_TOP, FLOOR_Y
        )

        # Ground (positioned below tentacles)
        self.ground = self.Entity(
            model='plane',
            scale=20,
            color=self.color.rgb(*GROUND_COLOR),
            position=(0, GROUND_Y, 0)
        )

        # Physics floor (for blob drop physics, positioned higher than visual ground)
        self.floor = self.Entity(
            model='plane',
            scale=20,
            color=self.color.rgb(0.25, 0.30, 0.35),  # Slightly lighter blue-gray
            position=(0, FLOOR_Y, 0),
            visible=False  # Hidden by default, shown when physics active
        )

        # Shadow (radial gradient circle just above ground)
        shadow_pil_image = create_radial_gradient_texture(
            size=256,
            max_opacity=180,  # Semi-transparent
            falloff_power=2   # Quadratic falloff for soft edges
        )
        # Convert PIL Image to Ursina Texture
        shadow_texture = self.Texture(shadow_pil_image)

        self.shadow = self.Entity(
            model='plane',
            scale=3.5,
            texture=shadow_texture,
            position=(0, SHADOW_Y, 0),
            unlit=True  # Ignore lighting, keep pure black
            # Note: Ursina will handle alpha blending automatically
        )

        # Simple single-layer sky using Ursina's built-in Sky
        # Use an average of top and bottom gradient colors for a bright, colorful sky
        sky_color = tuple(
            (SKY_GRADIENT_BOTTOM[i] + SKY_GRADIENT_TOP[i]) / 2
            for i in range(3)
        )
        self.sky = self.Sky(color=self.color.rgb(*sky_color))

        # Enhanced lighting system for toon/cel-shading
        # Key: Lower ambient + stronger directional = clearer lighting bands
        self.lighting = {}

        # Reduced ambient for darker shadows and more pronounced bands
        self.lighting['ambient'] = self.AmbientLight(
            color=self.color.rgb(0.15, 0.15, 0.18),
            intensity=0.15  # Reduced from 0.2 to 0.15
        )

        # Stronger key light from top-right for clear main lighting band
        self.lighting['key'] = self.DirectionalLight(
            position=(6, 10, 4),
            rotation=(55, -30, 0),
            color=self.color.rgb(1.0, 0.98, 0.95),
            intensity=2.2  # Increased from 1.5 to 2.2 for stronger bands
        )

        # Subtle fill light to soften shadows slightly
        self.lighting['fill'] = self.DirectionalLight(
            position=(-4, 5, -3),
            rotation=(125, 40, 0),
            color=self.color.rgb(0.6, 0.65, 0.75),
            intensity=0.4  # Reduced from 0.6 to 0.4
        )

        # Rim light for edge definition (helps separate overlapping spheres)
        self.lighting['rim'] = self.DirectionalLight(
            position=(-3, 4, -6),
            rotation=(145, 25, 0),
            color=self.color.rgb(0.5, 0.6, 0.9),
            intensity=0.6  # Reduced from 0.8 to 0.6
        )

        # Point light near creature center for interior depth
        self.lighting['point'] = self.PointLight(
            position=(0, 1, 0),
            color=self.color.rgb(1.0, 0.96, 0.92),
            intensity=0.3  # Reduced from 0.4 to 0.3
        )

    def rebuild_creature(self, creature_type='tentacle',
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
                        starfish_color=(0.9, 0.5, 0.3), curl_factor=0.3,
                        starfish_anim_speed=1.5, starfish_pulse_amount=0.06,
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
        Rebuild creature with new parameters.

        Args:
            creature_type: 'tentacle', 'blob', 'polyp', 'starfish', or 'medusa'
            [Tentacle parameters]
            num_tentacles: Number of tentacles
            segments: Segments per tentacle
            algorithm: 'bezier' or 'fourier'
            params: Algorithm parameters dict
            thickness_base: Base thickness
            taper_factor: Taper factor
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
            [Blob parameters]
            blob_branch_depth: Branching depth (0-3)
            blob_branch_count: Branches per level (1-3)
            cube_size_min: Minimum cube size
            cube_size_max: Maximum cube size
            cube_spacing: Cube spacing
            blob_color: Blob color (RGB tuple 0-1)
            blob_transparency: Transparency (0-1)
            jiggle_speed: Jiggle animation speed
            blob_pulse_amount: Pulse intensity
            [Polyp parameters]
            num_spheres: Number of spheres in spine (3-5)
            base_sphere_size: Size of root sphere (0.4-1.5)
            polyp_color: Spine/tentacle color (RGB tuple 0-1)
            curve_intensity: Spine curve amount (0-1)
            polyp_tentacles_per_sphere: Number of tentacles per sphere (3-12)
            polyp_segments: Segments per tentacle, controls length (5-20)
            [Starfish parameters]
            num_arms: Number of arms (5-8)
            arm_segments: Segments per arm (4-10)
            central_body_size: Central body size (0.4-1.5)
            arm_base_thickness: Arm thickness (0.2-0.6)
            starfish_color: Starfish color (RGB tuple 0-1)
            curl_factor: Arm curvature amount (0-0.8)
            starfish_anim_speed: Animation speed
            starfish_pulse_amount: Pulse intensity
        """
        try:
            # Destroy old creature
            if self.creature:
                self.creature.destroy()

            if creature_type == 'tentacle':
                # Import and create tentacle creature
                from ..models.creature import TentacleCreature

                self.creature = TentacleCreature(
                    num_tentacles=num_tentacles,
                    segments_per_tentacle=segments,
                    algorithm=algorithm,
                    algorithm_params=params,
                    thickness_base=thickness_base,
                    taper_factor=taper_factor,
                    branch_depth=branch_depth,
                    branch_count=branch_count,
                    body_scale=body_scale,
                    tentacle_color=tentacle_color,
                    hue_shift=hue_shift,
                    anim_speed=anim_speed,
                    wave_amplitude=wave_amplitude,
                    pulse_speed=pulse_speed,
                    pulse_amount=pulse_amount,
                    num_eyes=num_eyes,
                    eye_size_min=eye_size_min,
                    eye_size_max=eye_size_max,
                    eyeball_color=eyeball_color,
                    pupil_color=pupil_color
                )

            elif creature_type == 'blob':
                # Import and create blob creature
                from ..models.blob_creature import BlobCreature

                self.creature = BlobCreature(
                    branch_depth=blob_branch_depth,
                    branch_count=blob_branch_count,
                    cube_size_min=cube_size_min,
                    cube_size_max=cube_size_max,
                    cube_spacing=cube_spacing,
                    blob_color=blob_color,
                    transparency=blob_transparency,
                    jiggle_speed=jiggle_speed,
                    pulse_amount=blob_pulse_amount
                )

                # Auto-enable physics to drop creature to floor
                print("[BLOB SPAWN] Auto-enabling physics for drop animation")
                self.creature.enable_physics()
                self.floor.visible = True  # Show physics floor
                print("[BLOB SPAWN] Physics enabled, creature will drop and settle")

            elif creature_type == 'polyp':
                # Import and create polyp creature
                from ..models.polyp_creature import PolypCreature

                # Create uniform tentacles per sphere list (all spheres get same count)
                tentacles_per_sphere = [polyp_tentacles_per_sphere] * num_spheres

                self.creature = PolypCreature(
                    num_spheres=num_spheres,
                    algorithm=algorithm,
                    algorithm_params=params,
                    base_sphere_size=base_sphere_size,
                    tentacles_per_sphere=tentacles_per_sphere,
                    segments_per_tentacle=polyp_segments,
                    thickness_base=thickness_base,
                    taper_factor=taper_factor,
                    spine_color=polyp_color,
                    curve_intensity=curve_intensity,
                    anim_speed=anim_speed,
                    pulse_amount=pulse_amount
                )

            elif creature_type == 'starfish':
                # Import and create starfish creature
                from ..models.starfish_creature import StarfishCreature

                self.creature = StarfishCreature(
                    num_arms=num_arms,
                    arm_segments=arm_segments,
                    central_body_size=central_body_size,
                    arm_base_thickness=arm_base_thickness,
                    starfish_color=starfish_color,
                    curl_factor=curl_factor,
                    anim_speed=starfish_anim_speed,
                    pulse_amount=starfish_pulse_amount
                )

            elif creature_type == 'medusa':
                # Import and create medusa creature (eyes on tentacle tips)
                from ..models.medusa_creature import MedusaCreature

                self.creature = MedusaCreature(
                    num_tentacles=num_tentacles,
                    segments_per_tentacle=segments,
                    algorithm=algorithm,
                    algorithm_params=params,
                    thickness_base=thickness_base,
                    taper_factor=taper_factor,
                    body_scale=body_scale,
                    tentacle_color=tentacle_color,
                    hue_shift=hue_shift,
                    anim_speed=anim_speed,
                    wave_amplitude=wave_amplitude,
                    pulse_speed=pulse_speed,
                    pulse_amount=pulse_amount,
                    eye_size=eye_size_max,  # Use max eye size for tip eyes
                    eyeball_color=eyeball_color,
                    pupil_color=pupil_color
                )

            elif creature_type == 'dragon':
                # Import and create dragon creature (Space Harrier inspired)
                from ..models.dragon_creature import DragonCreature

                self.creature = DragonCreature(
                    num_segments=dragon_segments,
                    segment_thickness=dragon_thickness,
                    taper_factor=dragon_taper,
                    head_scale=dragon_head_scale,
                    body_color=dragon_body_color,  # RGB 0-255
                    head_color=dragon_head_color,  # RGB 0-255
                    weave_amplitude=dragon_weave_amplitude,
                    bob_amplitude=dragon_bob_amplitude,
                    anim_speed=dragon_anim_speed,
                    num_eyes=dragon_num_eyes,
                    eye_size=dragon_eye_size,
                    eyeball_color=dragon_eyeball_color,  # RGB 0-255
                    pupil_color=dragon_pupil_color,  # RGB 0-255
                    mouth_size=dragon_mouth_size,
                    mouth_color=dragon_mouth_color,  # RGB 0-255
                    num_whiskers_per_side=dragon_num_whiskers_per_side,
                    whisker_segments=dragon_whisker_segments,
                    whisker_thickness=dragon_whisker_thickness
                )

            else:
                print(f"ERROR: Unknown creature type '{creature_type}'")

        except Exception as e:
            print(f"ERROR: Failed to rebuild creature: {e}")
            import traceback
            traceback.print_exc()

    def trigger_attack(self):
        """Trigger Attack 1 animation on creature (all tentacles whip attack)."""
        if self.creature:
            # Get camera position and pass it to creature
            camera_pos = self.camera.position
            self.creature.start_attack(camera_pos)

    def trigger_attack_2(self):
        """Trigger Attack 2 animation on creature (single tentacle slash)."""
        if self.creature:
            # Get camera position and pass it to creature
            camera_pos = self.camera.position
            self.creature.start_attack_2(camera_pos)

    def drop_creature(self):
        """Enable physics and drop blob creature."""
        print("=== DROP CREATURE CALLED ===")
        if not self.creature:
            print("ERROR: No creature exists")
            return

        if not hasattr(self.creature, 'enable_physics'):
            print(f"ERROR: Creature type {type(self.creature).__name__} doesn't support physics")
            return

        print(f"Creature has {len(self.creature.cubes)} cubes")
        print(f"Enabling physics (drop from current position)")

        self.creature.enable_physics()  # No drop_from_height parameter needed

        # Show physics floor when physics active
        self.floor.visible = True
        print(f"Physics enabled: {self.creature.physics_enabled}")
        print(f"Physics floor visible: {self.floor.visible}")
        print("=== DROP CREATURE COMPLETE ===")

    def _update_animation(self):
        """Update creature animation and handle rendering."""
        if self.ursina_app:
            try:
                # Step Ursina forward one frame (non-blocking)
                self.ursina_app.step()

                # Update animation time
                from ursina import time as ursina_time
                self.animation_time += ursina_time.dt
                dt = ursina_time.dt

                # Update creature (physics or animation)
                if self.creature:
                    # Check if physics is enabled
                    if hasattr(self.creature, 'physics_enabled') and self.creature.physics_enabled:
                        # Run physics simulation
                        from ..core.constants import DROP_DURATION

                        # Log first frame and occasional updates
                        if not hasattr(self, '_physics_frame_count'):
                            self._physics_frame_count = 0
                            print(f"[UPDATE] Starting physics simulation (actual dt={dt})")

                        self._physics_frame_count += 1
                        if self._physics_frame_count % 60 == 0:  # Log every 60 frames (~1 second)
                            print(f"[UPDATE] Physics frame {self._physics_frame_count}, time={self.creature.physics_time:.2f}s")
                            # Log first cube position
                            if self.creature.cubes:
                                pos = self.creature.cubes[0].entity.position
                                print(f"  Cube 0 position: {pos}")

                        # Clamp dt to prevent physics explosions on lag spikes
                        # (Cap at 30 FPS minimum, ~0.033s max timestep)
                        clamped_dt = min(dt, 1.0 / 30.0)

                        # Use actual dt instead of fixed timestep for better accuracy
                        self.creature.update_physics(clamped_dt)
                        self.creature.physics_time += clamped_dt

                        # Check if creature has settled (velocity-based detection)
                        if self._check_creature_settled():
                            print(f"[UPDATE] Physics settled at {self.creature.physics_time:.2f}s, disabling physics")
                            self.creature.disable_physics()
                            self.floor.visible = False  # Hide physics floor
                            delattr(self, '_physics_frame_count')
                            delattr(self, '_settle_check_timer')
                    else:
                        # Normal animation
                        self.creature.update_animation(self.animation_time, self.camera.position)

                # Handle camera controls
                self._handle_camera_controls()

            except Exception as e:
                # Silently ignore errors (app might be closing)
                pass

    def _check_creature_settled(self):
        """
        Check if creature has settled (all particles below velocity threshold).

        Returns:
            True if creature is settled and physics can be disabled
        """
        if not self.creature or not hasattr(self.creature, 'physics_engine'):
            return False

        # Import settling constants
        from ..core.constants import (
            MIN_PHYSICS_TIME, SETTLE_VELOCITY_THRESHOLD, SETTLE_DURATION
        )

        # Require minimum time before checking (let creature fall first)
        if self.creature.physics_time < MIN_PHYSICS_TIME:
            return False

        # Check if all particles have low velocity (settled)
        max_velocity = 0.0
        for particle in self.creature.physics_engine.particles:
            velocity = (particle.position - particle.old_position).length()
            max_velocity = max(max_velocity, velocity)

        # Initialize settle timer if not exists
        if not hasattr(self, '_settle_check_timer'):
            self._settle_check_timer = 0.0

        # If velocity low, increment timer; if high, reset timer
        if max_velocity < SETTLE_VELOCITY_THRESHOLD:
            self._settle_check_timer += self.creature.physics_time - getattr(self, '_last_physics_time', 0)
            print(f"[SETTLE CHECK] Max velocity: {max_velocity:.4f}, settle timer: {self._settle_check_timer:.2f}s")

            if self._settle_check_timer >= SETTLE_DURATION:
                return True  # Settled!
        else:
            self._settle_check_timer = 0.0  # Reset timer

        self._last_physics_time = self.creature.physics_time
        return False

    def _handle_camera_controls(self):
        """Handle mouse camera controls with orbit system."""
        try:
            # Import constants for limits
            from ..core.constants import (
                MIN_CAMERA_DISTANCE, MAX_CAMERA_DISTANCE,
                MIN_CAMERA_HEIGHT, MAX_CAMERA_HEIGHT
            )

            # Mouse drag to orbit (Ursina uses held_keys for mouse buttons)
            if self.held_keys['left mouse']:
                self.camera_angle += self.mouse.velocity[0] * 200
                self.camera_height += self.mouse.velocity[1] * 5

            # Clamp camera height
            self.camera_height = max(MIN_CAMERA_HEIGHT, min(MAX_CAMERA_HEIGHT, self.camera_height))

            # Scroll to zoom (Ursina uses held_keys for scroll events)
            if self.held_keys['scroll up']:
                self.camera_distance -= 0.5
            if self.held_keys['scroll down']:
                self.camera_distance += 0.5
            self.camera_distance = max(MIN_CAMERA_DISTANCE, min(MAX_CAMERA_DISTANCE, self.camera_distance))

            # Calculate camera position using orbit math
            angle_rad = self.math.radians(self.camera_angle)
            cam_x = self.camera_distance * self.math.sin(angle_rad)
            cam_z = -self.camera_distance * self.math.cos(angle_rad)

            # Update camera position and look at creature center
            self.camera.position = (cam_x, self.camera_height, cam_z)
            self.camera.look_at((0, 0, 0))

            # Reset camera (R key)
            if self.held_keys['r']:
                self.camera_angle = 0
                self.camera_height = 2
                self.camera_distance = 6
                self.held_keys['r'] = False

        except Exception as e:
            pass

    def cleanup(self):
        """Cleanup Ursina resources."""
        try:
            if self.timer:
                self.timer.stop()

            if self.creature:
                self.creature.destroy()

            if self.ursina_app:
                self.ursina_app.exit()

        except Exception as e:
            pass  # Silently ignore cleanup errors
