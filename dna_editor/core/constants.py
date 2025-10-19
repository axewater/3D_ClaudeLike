"""
Constants and configuration for DNA Editor.
"""

import math

# Default algorithm parameters
DEFAULT_PARAMS = {
    'bezier': {'control_strength': 0.4},
    'fourier': {'num_waves': 3, 'amplitude': 0.15}
}

# Preset configurations for Tentacle creature (name, algorithm, params)
PRESETS = [
    ('Default', 'bezier', {'control_strength': 0.4}),
    ('Tight', 'bezier', {'control_strength': 0.2}),
]

# Blob creature presets (name, params_dict)
BLOB_PRESETS = [
    ('Default', {
        'blob_branch_depth': 2,
        'blob_branch_count': 2,
        'cube_size_min': 0.3,
        'cube_size_max': 0.8,
        'cube_spacing': 1.2,
        'blob_color': (0.2, 0.8, 0.4),
        'blob_transparency': 0.7,
        'jiggle_speed': 2.0,
        'blob_pulse_amount': 0.1
    }),
    ('Compact', {
        'blob_branch_depth': 1,
        'blob_branch_count': 3,
        'cube_size_min': 0.25,
        'cube_size_max': 0.6,
        'cube_spacing': 0.8,
        'blob_color': (0.3, 0.6, 0.9),
        'blob_transparency': 0.6,
        'jiggle_speed': 3.0,
        'blob_pulse_amount': 0.15
    }),
    ('Branching', {
        'blob_branch_depth': 3,
        'blob_branch_count': 2,
        'cube_size_min': 0.2,
        'cube_size_max': 0.5,
        'cube_spacing': 1.5,
        'blob_color': (0.8, 0.3, 0.7),
        'blob_transparency': 0.75,
        'jiggle_speed': 1.5,
        'blob_pulse_amount': 0.08
    }),
]

# Polyp creature presets (name, params_dict)
POLYP_PRESETS = [
    ('Default', {
        'num_spheres': 4,
        'base_sphere_size': 0.8,
        'polyp_color': (0.6, 0.3, 0.7),
        'curve_intensity': 0.4,
        'polyp_tentacles_per_sphere': 6,
        'polyp_segments': 12,
        'polyp_thickness': 0.2,
        'polyp_taper': 0.6,
        'polyp_anim_speed': 2.0,
        'polyp_pulse_amount': 0.08
    }),
    ('Tall', {
        'num_spheres': 5,
        'base_sphere_size': 0.6,
        'polyp_color': (0.3, 0.7, 0.5),
        'curve_intensity': 0.6,
        'polyp_tentacles_per_sphere': 5,
        'polyp_segments': 10,
        'polyp_thickness': 0.15,
        'polyp_taper': 0.7,
        'polyp_anim_speed': 1.5,
        'polyp_pulse_amount': 0.1
    }),
    ('Bushy', {
        'num_spheres': 3,
        'base_sphere_size': 1.0,
        'polyp_color': (0.8, 0.5, 0.3),
        'curve_intensity': 0.3,
        'polyp_tentacles_per_sphere': 8,
        'polyp_segments': 14,
        'polyp_thickness': 0.25,
        'polyp_taper': 0.5,
        'polyp_anim_speed': 2.5,
        'polyp_pulse_amount': 0.06
    }),
]

# Starfish creature presets (name, params_dict)
STARFISH_PRESETS = [
    ('Default', {
        'num_arms': 5,
        'arm_segments': 6,
        'central_body_size': 0.8,
        'arm_base_thickness': 0.4,
        'starfish_color': (0.9, 0.5, 0.3),
        'curl_factor': 0.3,
        'starfish_anim_speed': 1.5,
        'starfish_pulse_amount': 0.06
    }),
    ('Hexapus', {
        'num_arms': 6,
        'arm_segments': 8,
        'central_body_size': 0.6,
        'arm_base_thickness': 0.35,
        'starfish_color': (0.4, 0.6, 0.9),
        'curl_factor': 0.5,
        'starfish_anim_speed': 2.0,
        'starfish_pulse_amount': 0.08
    }),
    ('Octopus', {
        'num_arms': 8,
        'arm_segments': 7,
        'central_body_size': 1.0,
        'arm_base_thickness': 0.3,
        'starfish_color': (0.6, 0.3, 0.4),
        'curl_factor': 0.15,
        'starfish_anim_speed': 1.2,
        'starfish_pulse_amount': 0.05
    }),
]

# Medusa creature presets (name, params_dict)
MEDUSA_PRESETS = [
    ('Default', {
        'medusa_num_tentacles': 8,
        'medusa_segments': 16,
        'medusa_thickness': 0.25,
        'medusa_taper': 0.6,
        'medusa_body_scale': 1.0,
        'medusa_color': (0.4, 0.2, 0.6),
        'medusa_hue_shift': 0.08,
        'medusa_anim_speed': 1.5,
        'medusa_wave_amplitude': 0.08,
        'medusa_pulse_speed': 1.2,
        'medusa_pulse_amount': 0.06,
        'medusa_eye_size': 0.18
    }),
    ('Jellyfish', {
        'medusa_num_tentacles': 12,
        'medusa_segments': 20,
        'medusa_thickness': 0.15,
        'medusa_taper': 0.7,
        'medusa_body_scale': 1.2,
        'medusa_color': (0.5, 0.7, 0.9),
        'medusa_hue_shift': 0.05,
        'medusa_anim_speed': 1.0,
        'medusa_wave_amplitude': 0.12,
        'medusa_pulse_speed': 1.5,
        'medusa_pulse_amount': 0.1,
        'medusa_eye_size': 0.12
    }),
    ('Squid', {
        'medusa_num_tentacles': 6,
        'medusa_segments': 12,
        'medusa_thickness': 0.35,
        'medusa_taper': 0.5,
        'medusa_body_scale': 1.5,
        'medusa_color': (0.7, 0.3, 0.2),
        'medusa_hue_shift': 0.12,
        'medusa_anim_speed': 2.0,
        'medusa_wave_amplitude': 0.06,
        'medusa_pulse_speed': 0.8,
        'medusa_pulse_amount': 0.04,
        'medusa_eye_size': 0.25
    }),
]

# Dragon creature presets (name, params_dict)
DRAGON_PRESETS = [
    ('Default', {
        'dragon_segments': 15,
        'dragon_thickness': 0.3,
        'dragon_taper': 0.6,
        'dragon_head_scale': 3.0,
        'dragon_body_color': (200, 40, 40),
        'dragon_head_color': (255, 200, 50),
        'dragon_weave_amplitude': 0.5,
        'dragon_bob_amplitude': 0.3,
        'dragon_anim_speed': 1.5,
        'dragon_mouth_size': 0.25,
        'dragon_num_whiskers': 2,
        'dragon_whisker_segments': 4,
        'dragon_whisker_thickness': 0.05
    }),
    ('Serpent', {
        'dragon_segments': 25,
        'dragon_thickness': 0.2,
        'dragon_taper': 0.7,
        'dragon_head_scale': 2.5,
        'dragon_body_color': (50, 180, 50),
        'dragon_head_color': (150, 255, 150),
        'dragon_weave_amplitude': 0.7,
        'dragon_bob_amplitude': 0.2,
        'dragon_anim_speed': 2.0,
        'dragon_mouth_size': 0.3,
        'dragon_num_whiskers': 3,
        'dragon_whisker_segments': 5,
        'dragon_whisker_thickness': 0.04
    }),
    ('Wyrm', {
        'dragon_segments': 10,
        'dragon_thickness': 0.5,
        'dragon_taper': 0.4,
        'dragon_head_scale': 3.5,
        'dragon_body_color': (120, 80, 200),
        'dragon_head_color': (200, 150, 255),
        'dragon_weave_amplitude': 0.3,
        'dragon_bob_amplitude': 0.4,
        'dragon_anim_speed': 1.0,
        'dragon_mouth_size': 0.4,
        'dragon_num_whiskers': 1,
        'dragon_whisker_segments': 3,
        'dragon_whisker_thickness': 0.06
    }),
]

# Default values
DEFAULT_NUM_TENTACLES = 2
DEFAULT_SEGMENTS = 12
DEFAULT_THICKNESS_BASE = 0.25
DEFAULT_TAPER_FACTOR = 0.6
DEFAULT_ALGORITHM = 'bezier'

# Appearance defaults
DEFAULT_BODY_SCALE = 1.2
DEFAULT_TENTACLE_COLOR = (0.6, 0.3, 0.7)  # Purple
DEFAULT_HUE_SHIFT = 0.1  # Color variation between tentacles

# Animation defaults
DEFAULT_ANIM_SPEED = 2.0  # Wave motion speed
DEFAULT_WAVE_AMPLITUDE = 0.05  # Animation intensity
DEFAULT_BODY_PULSE_SPEED = 1.5  # Breathing rate
DEFAULT_BODY_PULSE_AMOUNT = 0.05  # Breathing expansion

# Limits
MIN_TENTACLES = 1
MAX_TENTACLES = 12
MIN_SEGMENTS = 5
MAX_SEGMENTS = 20

# Appearance limits
MIN_BODY_SCALE = 0.5
MAX_BODY_SCALE = 2.0
MIN_HUE_SHIFT = 0.0
MAX_HUE_SHIFT = 0.3

# Animation limits
MIN_ANIM_SPEED = 0.5
MAX_ANIM_SPEED = 5.0
MIN_WAVE_AMPLITUDE = 0.0
MAX_WAVE_AMPLITUDE = 0.2
MIN_PULSE_SPEED = 0.5
MAX_PULSE_SPEED = 3.0
MIN_PULSE_AMOUNT = 0.0
MAX_PULSE_AMOUNT = 0.15

# Branching (Fibonacci-based)
GOLDEN_RATIO = 1.618033988749895  # φ
GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~137.508 degrees in radians
DEFAULT_BRANCH_DEPTH = 0
DEFAULT_BRANCH_COUNT = 1
MIN_BRANCH_DEPTH = 0
MAX_BRANCH_DEPTH = 3
MIN_BRANCH_COUNT = 1
MAX_BRANCH_COUNT = 3

# History
MAX_HISTORY_SIZE = 50

# Camera defaults
DEFAULT_CAMERA_DISTANCE = 6
DEFAULT_CAMERA_HEIGHT = 2
DEFAULT_CAMERA_ANGLE = 0
MIN_CAMERA_DISTANCE = 2
MAX_CAMERA_DISTANCE = 15
MIN_CAMERA_HEIGHT = 0.5
MAX_CAMERA_HEIGHT = 5

# Scene positioning
GROUND_Y = -3.5  # Floor position (below tentacles at y=-2.5)
SHADOW_Y = -3.45  # Shadow plane just above floor

# Colors
BODY_COLOR = (0.6, 0.3, 0.7)  # Purple
GROUND_COLOR = (0.15, 0.2, 0.25)  # Lighter blue-gray ground
SKY_COLOR = (0.05, 0.05, 0.1)  # Legacy single color (not used with gradient)
SKY_GRADIENT_BOTTOM = (0.9, 0.5, 0.65)  # Bright warm pink/coral at horizon
SKY_GRADIENT_TOP = (0.35, 0.65, 0.95)  # Bright cyan/sky blue at top
DEBUG_MARKER_COLOR = (1, 1, 0)  # Yellow

# Shadow (layered circles for soft shadow effect)
SHADOW_LAYERS = 5  # Number of shadow layers
SHADOW_BASE_SIZE = 3.5  # Size of largest (outermost) shadow layer
SHADOW_SIZE_STEP = 0.6  # Size reduction per layer (creates gradient effect)
SHADOW_BASE_OPACITY = 25  # Opacity of darkest (innermost) layer (0-255) - SUBTLE!
SHADOW_OPACITY_STEP = 4  # Opacity reduction per layer - small steps to prevent accumulation

# Body
BODY_SCALE = 1.2
BODY_PULSE_AMOUNT = 0.05
BODY_PULSE_SPEED = 1.5

# Toon Shader / Cel-Shading
TOON_CONTACT_SHADOW_SIZE = 0.6  # Shadow sphere size as fraction of segment (0.6 = 60%)
TOON_CONTACT_SHADOW_OPACITY = 60  # Shadow opacity 0-255 (60 = semi-transparent)
TOON_LIGHTING_BANDS = 4  # Number of discrete lighting bands (4 = full, medium, dark, shadow)

# Attack Animation (Whip Physics)
ATTACK_DURATION = 1.2  # Total attack cycle duration in seconds
ATTACK_WIND_UP_END = 0.2  # Wind-up phase ends at this time (pull back)
ATTACK_STRIKE_END = 0.5  # Strike phase ends at this time (forward lash)
ATTACK_FOLLOW_END = 0.8  # Follow-through phase ends at this time (continue motion)
ATTACK_RETURN_END = 1.2  # Return phase ends (ease back to idle)

# Whip wave propagation (exponential traveling wave)
WHIP_SPEED = 8.0  # Angular frequency (higher = faster wave travel)
WHIP_ACCELERATION = 3.5  # Exponential growth factor (higher = more tip acceleration)
WHIP_AMPLITUDE = 0.8  # Base amplitude of whip wave motion

# Dynamic stretching (distance-based extension)
STRETCH_THRESHOLD = 3.0  # Distance to camera before stretching kicks in
STRETCH_MULTIPLIER = 0.5  # How much to extend (0.5 = 50% of excess distance)
STRETCH_MAX = 2.0  # Maximum stretch factor (2.0 = can extend to 200% original length)

# Helical curl (spiral slash motion at tips)
CURL_INTENSITY = 0.3  # Spiral radius multiplier
CURL_SPEED = 10.0  # Spiral rotation speed (radians per second)
CURL_TWIST_FACTOR = 0.5  # How much twist increases per segment

# Wind-up motion (pull back before strike)
WIND_UP_DISTANCE = 0.3  # How far to pull back during wind-up phase

# Segment distance constraints (keep tentacles connected)
SEGMENT_STRETCH_MAX = 1.8  # Maximum distance multiplier (180% of original spacing)
SEGMENT_COMPRESS_MIN = 0.4  # Minimum distance multiplier (40% of original spacing)
CONSTRAINT_ITERATIONS = 2  # Number of constraint solver passes (more = stiffer)

# Attack 2 Animation (Single Tentacle Slash - More Subtle)
ATTACK_2_DURATION = 0.6  # Total duration (half of Attack 1 - faster)
ATTACK_2_WIND_UP_END = 0.1  # Brief wind-up phase
ATTACK_2_SLASH_END = 0.35  # Slash phase ends
ATTACK_2_RETURN_END = 0.6  # Return phase ends
ATTACK_2_AMPLITUDE = 0.4  # Wave amplitude (less than WHIP_AMPLITUDE)
ATTACK_2_SPEED = 12.0  # Wave speed (faster but simpler)
ATTACK_2_CURL_INTENSITY = 0.15  # Minimal curl (less than CURL_INTENSITY)

# Exploration Animation (Coordinated Tentacle Reaching)
EXPLORATION_REACH_DURATION = 4.0  # Seconds to reach target (smooth ease-out)
EXPLORATION_RETURN_DURATION = 0.5  # Seconds to spring back (fast return)
EXPLORATION_IDLE_GAP = 0.5  # Pause between cycles
EXPLORATION_TENTACLE_RATIO = (0.25, 0.40)  # 25-40% of tentacles reach together
EXPLORATION_TARGET_MIN_RADIUS = 1.5  # Minimum target distance from body center
EXPLORATION_TARGET_MAX_RADIUS = 2.5  # Maximum target distance from body center
EXPLORATION_REACH_STRENGTH = 1.5  # How far tentacles stretch toward target

# Eye defaults
DEFAULT_NUM_EYES = 3
DEFAULT_EYE_SIZE_MIN = 0.1
DEFAULT_EYE_SIZE_MAX = 0.25
DEFAULT_EYEBALL_COLOR = (1.0, 1.0, 1.0)  # White
DEFAULT_PUPIL_COLOR = (0.0, 0.0, 0.0)  # Black

# Eye limits
MIN_NUM_EYES = 0
MAX_NUM_EYES = 12
MIN_EYE_SIZE = 0.05
MAX_EYE_SIZE = 0.5

# Eye animation
EYE_BLINK_DURATION = 0.2  # Total blink time in seconds
EYE_BLINK_INTERVAL_MIN = 3.0  # Minimum seconds between blinks
EYE_BLINK_INTERVAL_MAX = 8.0  # Maximum seconds between blinks

# ==========================================
# BLOB CREATURE CONSTANTS
# ==========================================

# Blob defaults
DEFAULT_NUM_CUBES = 8  # DEPRECATED: Use branch_depth + branch_count instead
DEFAULT_CUBE_SIZE_MIN = 0.18  # 40% smaller (0.3 * 0.6)
DEFAULT_CUBE_SIZE_MAX = 0.48  # 40% smaller (0.8 * 0.6)
DEFAULT_CUBE_SPACING = 0.72  # 40% smaller (1.2 * 0.6)
DEFAULT_BLOB_COLOR = (0.2, 0.8, 0.4)  # Green slime
DEFAULT_BLOB_TRANSPARENCY = 0.7  # 70% transparent
DEFAULT_JIGGLE_SPEED = 2.0
DEFAULT_BLOB_PULSE_AMOUNT = 0.1

# Blob Branching (Fibonacci Tree Structure)
DEFAULT_BLOB_BRANCH_DEPTH = 2  # 0-3 levels (depth=2 with count=2 → ~7 cubes)
DEFAULT_BLOB_BRANCH_COUNT = 2  # 1-3 children per cube
MIN_BLOB_BRANCH_DEPTH = 0
MAX_BLOB_BRANCH_DEPTH = 3
MIN_BLOB_BRANCH_COUNT = 1
MAX_BLOB_BRANCH_COUNT = 3

# Blob limits
MIN_NUM_CUBES = 1  # DEPRECATED
MAX_NUM_CUBES = 20  # DEPRECATED
MIN_CUBE_SIZE = 0.1
MAX_CUBE_SIZE = 1.5
MIN_CUBE_SPACING = 0.5
MAX_CUBE_SPACING = 2.5
MIN_BLOB_TRANSPARENCY = 0.1  # Min 10% transparent (90% opaque)
MAX_BLOB_TRANSPARENCY = 0.95  # Max 95% transparent (5% opaque)
MIN_JIGGLE_SPEED = 0.5
MAX_JIGGLE_SPEED = 5.0
MIN_BLOB_PULSE = 0.0
MAX_BLOB_PULSE = 0.3

# Connector Tubes (visual connections between parent-child cubes)
CONNECTOR_TUBE_RADIUS_RATIO = 0.15  # Tube radius = 15% of cube size
CONNECTOR_TUBE_OPACITY_MULTIPLIER = 0.6  # Tubes are 60% of cube transparency

# Blob animation
BLOB_JIGGLE_AMPLITUDE = 0.1  # How much each cube jiggles (world units)

# Cascade Attack Animation (wave propagates through tree structure)
CASCADE_ATTACK_DURATION = 1.4  # Total attack duration
CASCADE_WAVE_SPEED = 3.0  # Levels per second (higher = faster wave propagation)
CASCADE_EXPAND_AMOUNT = 1.6  # Max expansion multiplier (outward push)
CASCADE_PULSE_SCALE = 1.35  # Individual cube scale during attack

# Old attack constants (DEPRECATED - using cascade now)
BLOB_ATTACK_DURATION = 1.2  # DEPRECATED
BLOB_ATTACK_EXPAND_END = 0.4  # DEPRECATED
BLOB_ATTACK_CONTRACT_END = 0.8  # DEPRECATED
BLOB_ATTACK_RETURN_END = 1.2  # DEPRECATED
BLOB_ATTACK_EXPANSION = 1.5  # DEPRECATED
BLOB_ATTACK_SCALE = 1.3  # DEPRECATED

# ==========================================
# BLOB PHYSICS (VERLET INTEGRATION)
# ==========================================

# Physics simulation
PHYSICS_TIMESTEP = 1.0 / 60.0  # 60Hz fixed update (DEPRECATED - now using actual dt)
PHYSICS_GRAVITY_Y = -98.0  # Gravity acceleration (m/s^2) - 10x stronger for visible drop
PHYSICS_DAMPING = 0.98  # Velocity damping (0.98 = 2% loss per frame)

# Floor collision
FLOOR_Y = -2.0  # Floor plane Y position
FLOOR_RESTITUTION = 0.4  # Bounce factor (0.4 = 40% energy retained)
FLOOR_FRICTION = 0.9  # Horizontal friction multiplier (0.9 = 10% loss)

# Distance constraints
CONSTRAINT_STIFFNESS = 0.5  # How rigid constraints are (0-1, where 0.5 = moderate)
CONSTRAINT_ITERATIONS = 10  # Solver passes per frame (more = stiffer, max 10)

# Drop animation
DROP_START_HEIGHT = 5.0  # DEPRECATED - creature now drops from current position
DROP_DURATION = 3.0  # DEPRECATED - physics now runs until velocity settling

# Physics settling detection (replaces fixed DROP_DURATION)
SETTLE_VELOCITY_THRESHOLD = 0.02  # Maximum velocity to consider "settled" (units/second) - lower = stricter
SETTLE_DURATION = 2.0  # Must be below threshold for this long (seconds) - increased from 0.5s
MIN_PHYSICS_TIME = 2.0  # Minimum physics time before checking for settling (seconds) - increased from 1.0s

# ==========================================
# POLYP CREATURE CONSTANTS
# ==========================================

# Polyp defaults (segmented spine with spheres and tentacles)
DEFAULT_NUM_SPHERES = 4  # Number of spheres in chain (3-5)
DEFAULT_BASE_SPHERE_SIZE = 0.8  # Size of root sphere
DEFAULT_TENTACLES_PER_SPHERE = [8, 6, 5, 4]  # Tentacles per sphere (decreases along chain)
DEFAULT_POLYP_SEGMENTS = 12  # Segments per tentacle
DEFAULT_POLYP_THICKNESS = 0.2  # Base tentacle thickness
DEFAULT_POLYP_TAPER = 0.6  # Tentacle taper factor
DEFAULT_POLYP_COLOR = (0.6, 0.3, 0.7)  # Purple spine
DEFAULT_CURVE_INTENSITY = 0.4  # Spine curve amount (0-1)
DEFAULT_POLYP_ANIM_SPEED = 2.0  # Animation speed
DEFAULT_POLYP_PULSE = 0.08  # Pulse intensity

# Polyp limits
MIN_NUM_SPHERES = 3
MAX_NUM_SPHERES = 5
MIN_BASE_SPHERE_SIZE = 0.4
MAX_BASE_SPHERE_SIZE = 1.5
MIN_TENTACLES_PER_SPHERE = 3
MAX_TENTACLES_PER_SPHERE = 10
MIN_CURVE_INTENSITY = 0.0
MAX_CURVE_INTENSITY = 1.0
MIN_POLYP_PULSE = 0.0
MAX_POLYP_PULSE = 0.2

# ==========================================
# STARFISH CREATURE CONSTANTS
# ==========================================

# Starfish defaults (radial symmetry with articulated arms)
DEFAULT_NUM_ARMS = 5  # Number of arms (5-8)
DEFAULT_ARM_SEGMENTS = 6  # Segments per arm (4-10)
DEFAULT_CENTRAL_BODY_SIZE = 0.8  # Central body sphere size
DEFAULT_ARM_BASE_THICKNESS = 0.4  # Base thickness of arms
DEFAULT_STARFISH_COLOR = (0.9, 0.5, 0.3)  # Orange
DEFAULT_CURL_FACTOR = 0.3  # Arm curvature amount (0-0.8)
DEFAULT_STARFISH_ANIM_SPEED = 1.5  # Animation speed
DEFAULT_STARFISH_PULSE = 0.06  # Pulse intensity

# Starfish limits
MIN_NUM_ARMS = 5
MAX_NUM_ARMS = 8
MIN_ARM_SEGMENTS = 4
MAX_ARM_SEGMENTS = 10
MIN_CENTRAL_BODY_SIZE = 0.4
MAX_CENTRAL_BODY_SIZE = 1.5
MIN_ARM_THICKNESS = 0.2
MAX_ARM_THICKNESS = 0.6
MIN_CURL_FACTOR = 0.0
MAX_CURL_FACTOR = 0.8

# Starfish animation
STARFISH_ATTACK_DURATION = 1.0  # Attack cycle duration (seconds)
STARFISH_CURL_SPEED = 2.5  # Speed of curl animation

# ==========================================
# DRAGON CREATURE CONSTANTS
# ==========================================

# Dragon defaults (Space Harrier inspired segmented flying serpent)
DEFAULT_DRAGON_SEGMENTS = 15  # Number of body segments (5-30)
DEFAULT_DRAGON_THICKNESS = 0.3  # Base segment size
DEFAULT_DRAGON_TAPER = 0.6  # Tail taper factor (0.0-0.9)
DEFAULT_DRAGON_HEAD_SCALE = 3.0  # Head size multiplier (1.0-3.5)
DEFAULT_DRAGON_BODY_COLOR = (200, 40, 40)  # Dark red body (RGB 0-255)
DEFAULT_DRAGON_HEAD_COLOR = (255, 200, 50)  # Golden head (RGB 0-255)
DEFAULT_DRAGON_WEAVE_AMPLITUDE = 0.5  # Side-to-side motion (0.0-1.0)
DEFAULT_DRAGON_BOB_AMPLITUDE = 0.3  # Up-down motion (0.0-1.0)
DEFAULT_DRAGON_ANIM_SPEED = 1.5  # Animation speed
DEFAULT_DRAGON_MOUTH_SIZE = 0.25  # Mouth cavity size (0.25-0.5)
DEFAULT_DRAGON_MOUTH_COLOR = (20, 0, 0)  # Dark red mouth cavity (RGB 0-255)

# Dragon limits
MIN_DRAGON_SEGMENTS = 5
MAX_DRAGON_SEGMENTS = 30
MIN_DRAGON_THICKNESS = 0.1
MAX_DRAGON_THICKNESS = 0.8
MIN_DRAGON_TAPER = 0.0
MAX_DRAGON_TAPER = 0.9
MIN_DRAGON_HEAD_SCALE = 1.0
MAX_DRAGON_HEAD_SCALE = 3.5
MIN_DRAGON_WEAVE = 0.0
MAX_DRAGON_WEAVE = 1.0
MIN_DRAGON_BOB = 0.0
MAX_DRAGON_BOB = 1.0
MIN_DRAGON_MOUTH_SIZE = 0.25
MAX_DRAGON_MOUTH_SIZE = 0.5

# Dragon animation
DRAGON_ATTACK_DURATION = 1.0  # Attack cycle duration (seconds)

# Dragon whiskers
DEFAULT_NUM_WHISKERS_PER_SIDE = 2  # Whiskers on each side (1-3)
DEFAULT_WHISKER_SEGMENTS = 4  # Segments per whisker (3-6)
DEFAULT_WHISKER_THICKNESS = 0.05  # Base thickness (0.03-0.08)
DRAGON_WHISKER_CURVE_INTENSITY = 0.4  # Bezier control strength (0.2-0.6)

# Whisker limits
MIN_WHISKERS_PER_SIDE = 0
MAX_WHISKERS_PER_SIDE = 3
MIN_WHISKER_SEGMENTS = 3
MAX_WHISKER_SEGMENTS = 6
MIN_WHISKER_THICKNESS = 0.03
MAX_WHISKER_THICKNESS = 0.08
