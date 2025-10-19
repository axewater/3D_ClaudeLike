"""
Goblin 3D model - Small wicked trickster with hunched posture

Procedurally generated 3D model using custom mesh generation with:
- Manual feature sculpting (jutting chin, crooked nose, etc.)
- Noise-based organic detail (lumpy skin texture)
- Per-goblin parametric variation
"""

from ursina import Entity, Vec3, Mesh, color as ursina_color
import math


# ============================================================================
# MESH GENERATION INFRASTRUCTURE (Phase 1)
# ============================================================================
#
# PERFORMANCE METRICS (16x16 segments):
# - Vertices: 289 (17x17 grid)
# - Triangles: 512 (within target 400-800 range)
# - Memory: ~14KB per goblin head mesh
# - Generation time: <5ms per mesh (fast enough for runtime generation)
#
# ============================================================================

def create_custom_mesh(vertices, triangles, normals):
    """
    Create a custom Ursina mesh from vertex/triangle/normal data

    Args:
        vertices: List of Vec3 vertex positions
        triangles: List of (v1, v2, v3) triangle index tuples
        normals: List of Vec3 vertex normals

    Returns:
        Mesh: Ursina Mesh object ready for rendering

    Raises:
        ValueError: If vertex/triangle/normal data is invalid
    """
    if not vertices or not triangles:
        raise ValueError("Mesh must have vertices and triangles")

    if len(normals) != len(vertices):
        raise ValueError(f"Normal count ({len(normals)}) must match vertex count ({len(vertices)})")

    # Validate triangle indices
    max_index = len(vertices) - 1
    for tri in triangles:
        if any(idx < 0 or idx > max_index for idx in tri):
            raise ValueError(f"Triangle index out of range: {tri}, max={max_index}")

    # Create and return the mesh
    return Mesh(vertices=vertices, triangles=triangles, normals=normals)


def generate_sphere_vertices(segments_lat=16, segments_lon=16, apply_deformations=True,
                            apply_noise=True, params=None):
    """
    Generate vertices, triangles, and normals for a parametric sphere

    Uses latitude/longitude parameterization with even spacing.
    16x16 segments = 512 triangles (within target 400-800 range)

    Args:
        segments_lat: Number of latitude segments (vertical divisions)
        segments_lon: Number of longitude segments (horizontal divisions)
        apply_deformations: If True, apply goblin feature sculpting (Phase 2)
        apply_noise: If True, apply organic noise detail (Phase 4)
        params: Parameter dict from generate_goblin_head_params() (Phase 5)

    Returns:
        tuple: (vertices, triangles, normals) where:
            - vertices: List of Vec3 positions
            - triangles: List of (i1, i2, i3) index tuples
            - normals: List of Vec3 normal vectors
    """
    vertices = []
    triangles = []
    normals = []

    # Extract noise seed from params (default 0 if no params)
    noise_seed = params['noise_seed'] if params else 0

    # Generate vertices using spherical coordinates
    for i in range(segments_lat + 1):
        # Latitude: 0 (top) to π (bottom)
        lat = (i / segments_lat) * math.pi

        for j in range(segments_lon + 1):
            # Longitude: 0 to 2π (around equator)
            lon = (j / segments_lon) * 2 * math.pi

            # Convert spherical to Cartesian coordinates
            x = math.sin(lat) * math.cos(lon)
            y = math.cos(lat)
            z = math.sin(lat) * math.sin(lon)

            # Apply goblin feature deformations (Phase 2) with parametric variation (Phase 5)
            if apply_deformations:
                x, y, z = apply_goblin_features(x, y, z, lat, lon, params=params)

            # Apply organic noise detail (Phase 4)
            if apply_noise:
                x, y, z = apply_organic_detail(x, y, z, lat, lon, seed=noise_seed)

            # Store vertex
            vertices.append(Vec3(x, y, z))

            # Normal: for deformed mesh, approximate as normalized position
            # (More accurate would be gradient-based, but this works well enough)
            normals.append(Vec3(x, y, z).normalized())

    # Generate triangle indices (two triangles per quad)
    for i in range(segments_lat):
        for j in range(segments_lon):
            # Get the four corners of this quad
            current = i * (segments_lon + 1) + j
            next_row = (i + 1) * (segments_lon + 1) + j

            # Triangle 1: current, next_row, current+1
            triangles.append((current, next_row, current + 1))

            # Triangle 2: current+1, next_row, next_row+1
            triangles.append((current + 1, next_row, next_row + 1))

    return vertices, triangles, normals


# ============================================================================
# MANUAL FEATURE SCULPTING (Phase 2)
# ============================================================================

def apply_goblin_features(x, y, z, lat, lon, params=None):
    """
    Apply distinctive goblin facial features through parametric deformation

    Takes a point on a unit sphere and deforms it to create:
    - Elongated skull (top stretch)
    - Jutting chin (bottom-front protrusion)
    - Sunken eye sockets (side indents)
    - Crooked nose (front bump with asymmetry)
    - Wide jaw (lateral expansion)
    - Basic bumpy texture (high-frequency detail)

    Args:
        x, y, z: Original spherical coordinates (on unit sphere)
        lat: Latitude angle (0 to π)
        lon: Longitude angle (0 to 2π)
        params: Optional parameter dict for feature variation (Phase 5)

    Returns:
        tuple: (x, y, z) deformed coordinates
    """
    # Default parameters (all 1.0 = baseline goblin)
    if params is None:
        params = {
            'nose_length': 1.0,
            'chin_jut': 1.0,
            'jaw_width': 1.0,
            'skull_height': 1.0,
            'eye_depth': 1.0,
            'asymmetry': 1.0
        }

    # 1. ELONGATED SKULL - Stretch top of head vertically
    if y > 0.3:
        stretch_amount = 1.0 + (0.3 * params['skull_height'])
        y *= stretch_amount

    # 2. JUTTING CHIN - Extend forward and drop down at bottom-front
    if y < -0.2 and z > 0.2:
        z *= (1.0 + 0.4 * params['chin_jut'])  # Push forward
        y -= (0.15 * params['chin_jut'])  # Drop down

    # 3. SUNKEN EYE SOCKETS - Create indents on sides where eyes would be
    # Eyes typically at upper-middle of face, on the sides
    if 0.0 < y < 0.4 and abs(x) > 0.3 and 0.3 < z < 0.6:
        radius_reduction = 0.15 * params['eye_depth']
        x *= (1 - radius_reduction)
        z *= (1 - radius_reduction)

    # 4. CROOKED NOSE - Front protrusion with asymmetric offset
    # Nose is at middle height (y ≈ 0.1), front of face (lon ≈ π/2)
    nose_influence_y = max(0, 1 - abs(y - 0.1) / 0.3)  # Peak at y=0.1
    nose_influence_lon = max(0, 1 - abs(lon - math.pi/2) / 0.4)  # Peak at front
    nose_influence = nose_influence_y * nose_influence_lon

    if nose_influence > 0:
        z += nose_influence * 0.25 * params['nose_length']  # Extend forward
        x += nose_influence * 0.08 * params['asymmetry']    # Crooked to the side!

    # 5. WIDE JAW - Expand sides at lower-middle face
    if -0.2 < y < 0.1:
        jaw_expansion = (0.1 - y) * 1.5  # More expansion as we go down
        x *= (1 + jaw_expansion * 0.3 * params['jaw_width'])

    # 6. BASIC BUMPY TEXTURE - High-frequency sine waves for rough skin
    bump_freq = 8
    bump = math.sin(lat * bump_freq) * math.cos(lon * bump_freq * 1.3) * 0.02
    radius_mult = 1 + bump

    x *= radius_mult
    y *= radius_mult
    z *= radius_mult

    return x, y, z


# ============================================================================
# NOISE FUNCTIONS (Phase 3)
# ============================================================================

def noise_3d(x, y, z, seed=0):
    """
    Simple 3D hash-based pseudo-random noise

    Not true Perlin noise, but fast and sufficient for organic detail.
    Uses integer hashing with bit operations for pseudo-randomness.

    Args:
        x, y, z: 3D coordinates (any float values)
        seed: Random seed for variation (default 0)

    Returns:
        float: Pseudo-random value between -1 and 1
    """
    # Hash the coordinates with the seed
    n = int(x * 57.0 + y * 113.0 + z * 179.0 + seed * 1000.0)

    # Apply bit operations for pseudo-randomness
    n = (n << 13) ^ n
    result = (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    return result


def fractal_noise_3d(x, y, z, octaves=4, persistence=0.5, seed=0):
    """
    Layered multi-octave fractal noise for organic detail

    Combines multiple octaves of noise at different frequencies/amplitudes.
    Each octave adds finer detail at a smaller scale.

    Args:
        x, y, z: 3D coordinates
        octaves: Number of noise layers (more = finer detail, default 4)
        persistence: Amplitude decay per octave (default 0.5)
        seed: Base random seed

    Returns:
        float: Fractal noise value between -1 and 1
    """
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0

    for i in range(octaves):
        # Sample noise at current frequency
        total += noise_3d(
            x * frequency,
            y * frequency,
            z * frequency,
            seed=seed + i
        ) * amplitude

        # Track normalization factor
        max_value += amplitude

        # Update for next octave
        amplitude *= persistence  # Decay amplitude
        frequency *= 2.0  # Double frequency

    # Normalize to -1 to 1 range
    return total / max_value


def spherical_harmonic(theta, phi, l, m):
    """
    Simplified spherical harmonic functions for smooth organic deformation

    Spherical harmonics are basis functions on a sphere, used for
    large-scale asymmetric warping. This is a simplified version
    with only the most common cases implemented.

    Args:
        theta: Latitude angle (0 to π)
        phi: Longitude angle (0 to 2π)
        l: Degree (0-3, higher = more complex pattern)
        m: Order (-l to l, controls directionality)

    Returns:
        float: Harmonic value (roughly -1 to 1)
    """
    # Simplified versions for common cases
    if l == 0:
        # Constant (sphere)
        return 1.0

    elif l == 1:
        if m == 0:
            # Vertical stretch/compression
            return math.cos(theta)
        elif m == 1:
            # Lateral bulge (x-direction)
            return math.sin(theta) * math.cos(phi)
        elif m == -1:
            # Lateral bulge (y-direction)
            return math.sin(theta) * math.sin(phi)

    elif l == 2:
        if m == 0:
            # Vertical peanut shape
            return 0.5 * (3 * math.cos(theta)**2 - 1)
        elif m == 1:
            # Diagonal warping
            return math.sin(theta) * math.cos(theta) * math.cos(phi)
        elif m == 2:
            # Quadrupole (4-lobed)
            return math.sin(theta)**2 * math.cos(2 * phi)

    # Fallback: simple periodic function
    return math.sin(l * theta) * math.cos(m * phi)


# ============================================================================
# ORGANIC DETAIL INTEGRATION (Phase 4)
# ============================================================================

def apply_organic_detail(x, y, z, lat, lon, seed=0):
    """
    Apply multi-scale noise-based organic detail to a deformed vertex

    Layers three scales of noise for natural-looking goblin skin:
    - Large lumps (major irregularities)
    - Medium bumps (skin texture)
    - Fine detail (pores, roughness)

    Also adds spherical harmonic warping for large-scale asymmetry.

    Args:
        x, y, z: Vertex position (after manual feature deformation)
        lat, lon: Spherical coordinates (for harmonic warping)
        seed: Random seed for unique texture per goblin

    Returns:
        tuple: (x, y, z) with organic detail applied
    """

    # Calculate base radius from center
    radius = math.sqrt(x*x + y*y + z*z)
    if radius < 0.001:  # Avoid division by zero
        return x, y, z

    # Direction vector (normalized)
    nx, ny, nz = x / radius, y / radius, z / radius

    # --- SPHERICAL HARMONIC WARPING (large-scale organic asymmetry) ---
    # Subtle warping to make head less perfectly symmetric
    sh_vertical = spherical_harmonic(lat, lon, 2, 0) * 0.05  # Vertical peanut shape
    sh_lateral = spherical_harmonic(lat, lon, 1, 1) * 0.06   # Lateral bulge

    radius += sh_vertical + sh_lateral

    # --- MULTI-SCALE NOISE (organic skin texture) ---

    # Large lumps (major skin irregularities, warts, bulges)
    # Low frequency (2x), high amplitude (0.08)
    lump_noise = fractal_noise_3d(x * 2, y * 2, z * 2, octaves=3, seed=seed)
    radius += lump_noise * 0.08

    # Medium bumps (goblin skin texture, coarse detail)
    # Medium frequency (4x), medium amplitude (0.05)
    bump_noise = fractal_noise_3d(x * 4, y * 4, z * 4, octaves=3, seed=seed + 100)
    radius += bump_noise * 0.05

    # Fine skin detail (pores, micro-roughness)
    # High frequency (8x), low amplitude (0.03)
    fine_noise = fractal_noise_3d(x * 8, y * 8, z * 8, octaves=4, persistence=0.4, seed=seed + 200)
    radius += fine_noise * 0.03

    # Apply modified radius back to position
    x = nx * radius
    y = ny * radius
    z = nz * radius

    return x, y, z


# ============================================================================
# PARAMETRIC VARIATION SYSTEM (Phase 5)
# ============================================================================

def generate_goblin_head_params(seed):
    """
    Generate randomized parameters for goblin head features

    Uses seed to deterministically randomize feature sizes while keeping
    variations within "goblin range" (not too extreme).

    Args:
        seed: Integer seed for deterministic randomization

    Returns:
        dict: Parameter dictionary with multipliers for each feature:
            - nose_length: 0.8 - 1.3 (nose protrusion)
            - chin_jut: 0.8 - 1.2 (chin forward extension)
            - jaw_width: 0.9 - 1.15 (lateral jaw expansion)
            - skull_height: 0.95 - 1.2 (vertical skull stretch)
            - eye_depth: 0.7 - 1.3 (eye socket indent amount)
            - asymmetry: 0.5 - 1.5 (nose crookedness, overall asymmetry)
            - noise_seed: seed value for noise functions
    """
    # Simple deterministic pseudo-random using seed
    def seeded_random(s, index):
        """Return pseudo-random float between 0 and 1"""
        n = (s * 1000 + index) * 16807 % 2147483647
        return (n % 10000) / 10000.0

    # Generate parameters with specific ranges
    params = {
        'nose_length': 0.8 + seeded_random(seed, 1) * 0.5,      # 0.8 - 1.3
        'chin_jut': 0.8 + seeded_random(seed, 2) * 0.4,         # 0.8 - 1.2
        'jaw_width': 0.9 + seeded_random(seed, 3) * 0.25,       # 0.9 - 1.15
        'skull_height': 0.95 + seeded_random(seed, 4) * 0.25,   # 0.95 - 1.2
        'eye_depth': 0.7 + seeded_random(seed, 5) * 0.6,        # 0.7 - 1.3
        'asymmetry': 0.5 + seeded_random(seed, 6) * 1.0,        # 0.5 - 1.5
        'noise_seed': seed
    }

    return params


# ============================================================================
# GOBLIN MODEL CREATION
# ============================================================================

def create_goblin_3d(position: Vec3, enemy_color: ursina_color, seed=None) -> Entity:
    """
    Create a 3D goblin model with detailed accessories and clothing

    Args:
        position: 3D world position
        enemy_color: Base color for the goblin (green)
        seed: Optional seed for head variation (Phase 5). If None, generated from position.

    Returns:
        Entity: Goblin model with all child entities
    """
    # Container entity (invisible parent)
    goblin = Entity(position=position)

    # Generate unique seed for this goblin if not provided (Phase 5)
    if seed is None:
        # Hash position to create deterministic but unique seed
        seed = (int(position.x * 73856093) ^ int(position.y * 19349663) ^ int(position.z * 83492791)) % 100000

    # Generate head variation parameters (Phase 5)
    head_params = generate_goblin_head_params(seed)

    # Define goblin colors (using 0-1 float scale, divide by 255)
    skin_color = ursina_color.rgb(85/255, 110/255, 70/255)  # Muddy green skin
    skin_dark = ursina_color.rgb(70/255, 90/255, 55/255)  # Darker green for shadows
    skin_light = ursina_color.rgb(100/255, 125/255, 85/255)  # Lighter green for highlights
    leather_color = ursina_color.rgb(80/255, 60/255, 40/255)  # Brown leather
    rag_color = ursina_color.rgb(85/255, 70/255, 55/255)  # Dirty brown rags (lighter)
    tooth_color = ursina_color.rgb(200/255, 190/255, 150/255)  # Dirty yellow teeth
    claw_color = ursina_color.rgb(180/255, 180/255, 160/255)  # Gray claws
    wood_color = ursina_color.rgb(100/255, 75/255, 45/255)  # Dark wood (lighter)
    bone_color = ursina_color.rgb(220/255, 210/255, 190/255)  # Bone/ivory

    # Hunched body (stretched sphere for organic look)
    body = Entity(
        model='sphere',
        color=skin_color,
        scale=(0.4, 0.5, 0.35),  # Wider, taller, hunched
        parent=goblin,
        position=(0, 0.35, 0)
    )

    # Oversized head (signature goblin feature)
    # Generate custom mesh for head with parametric variation (Phases 1-5 complete)
    head_vertices, head_triangles, head_normals = generate_sphere_vertices(
        segments_lat=16,
        segments_lon=16,
        apply_deformations=True,  # Phase 2: manual features
        apply_noise=True,          # Phase 4: organic detail
        params=head_params         # Phase 5: per-goblin variation
    )
    head_mesh = create_custom_mesh(head_vertices, head_triangles, head_normals)

    head = Entity(
        model=head_mesh,
        color=skin_light,  # Slightly lighter
        scale=0.14,  # 40% of original size (0.35 * 0.4)
        parent=goblin,
        position=(0, 0.75, 0)  # Adjusted for taller body
    )

    # Pointed left ear
    left_ear = Entity(
        model='cube',
        color=skin_color,
        scale=(0.08, 0.15, 0.05),
        parent=head,
        position=(-0.25, 0.1, 0),
        rotation=(0, 0, -20)  # Angled outward
    )

    # Pointed right ear
    right_ear = Entity(
        model='cube',
        color=skin_color,
        scale=(0.08, 0.15, 0.05),
        parent=head,
        position=(0.25, 0.1, 0),
        rotation=(0, 0, 20)  # Angled outward
    )

    # Left tusk/tooth
    left_tusk = Entity(
        model='cube',
        color=tooth_color,
        scale=(0.04, 0.08, 0.04),
        parent=head,
        position=(-0.08, -0.1, 0.15),
        rotation=(15, 0, 0)  # Angled up
    )

    # Right tusk/tooth
    right_tusk = Entity(
        model='cube',
        color=tooth_color,
        scale=(0.04, 0.08, 0.04),
        parent=head,
        position=(0.08, -0.1, 0.15),
        rotation=(15, 0, 0)  # Angled up
    )

    # Ragged vest/torso covering (larger and protruding)
    vest = Entity(
        model='cube',
        color=rag_color,
        scale=(0.45, 0.45, 0.3),
        parent=body,
        position=(0, 0.05, 0.05)  # Stick out more
    )

    # Left shoulder joint
    left_shoulder = Entity(
        model='sphere',
        color=skin_dark,
        scale=0.18,
        parent=body,
        position=(-0.45, 0.2, 0)  # At body edge
    )

    # Right shoulder joint
    right_shoulder = Entity(
        model='sphere',
        color=skin_dark,
        scale=0.18,
        parent=body,
        position=(0.45, 0.2, 0)  # At body edge
    )

    # Left arm (thinner and 15% shorter)
    left_arm = Entity(
        model='sphere',
        color=skin_color,
        scale=(0.24, 0.85, 0.24),  # 50% thinner, 15% shorter
        parent=body,
        position=(-0.7, 0.0, 0),  # Further out, hangs down
        rotation=(0, 0, 15)
    )

    # Left hand (clawed)
    left_hand = Entity(
        model='sphere',
        color=skin_dark,
        scale=(0.15, 0.15, 0.15),
        parent=body,
        position=(-0.8, -0.35, 0)
    )

    # Left claws (3 small cubes)
    for i in range(3):
        Entity(
            model='cube',
            color=claw_color,
            scale=(0.03, 0.08, 0.03),
            parent=left_hand,
            position=((-0.05 + i * 0.05), -0.1, 0.08),
            rotation=(20, 0, 0)
        )

    # Right arm (thinner and 15% shorter)
    right_arm = Entity(
        model='sphere',
        color=skin_color,
        scale=(0.24, 0.85, 0.24),  # 50% thinner, 15% shorter
        parent=body,
        position=(0.7, 0.0, 0),  # Further out, hangs down
        rotation=(0, 0, -15)
    )

    # Right hand (clawed)
    right_hand = Entity(
        model='sphere',
        color=skin_dark,
        scale=(0.15, 0.15, 0.15),
        parent=body,
        position=(0.8, -0.35, 0)
    )

    # Right claws (3 small cubes)
    for i in range(3):
        Entity(
            model='cube',
            color=claw_color,
            scale=(0.03, 0.08, 0.03),
            parent=right_hand,
            position=((-0.05 + i * 0.05), -0.1, 0.08),
            rotation=(20, 0, 0)
        )

    # Crude wooden club (parented to body like rogue's daggers, not to hand!)
    # Position it near the right hand at (0.8, -0.35, 0) but sticking forward
    club_handle = Entity(
        model='cube',
        color=wood_color,
        scale=(0.1, 0.55, 0.1),  # Thin handle for taper
        parent=body,  # Parent to body, not hand!
        position=(0.77, -0.45, 0.35),  # Moved closer by ~0.18 (foot width)
        rotation=(-45, 0, 15)  # Angled forward and out
    )

    # Club head (MUCH bigger for heavy taper)
    club_head = Entity(
        model='cube',
        color=ursina_color.rgb(130/255, 95/255, 60/255),  # Much lighter brown
        scale=(0.3, 0.35, 0.3),  # 3x wider than handle!
        parent=club_handle,
        position=(0, -0.38, 0)  # Below handle
    )

    # Leather belt
    belt = Entity(
        model='cube',
        color=leather_color,
        scale=(0.45, 0.1, 0.3),
        parent=body,
        position=(0, -0.35, 0)
    )

    # Small pouch on belt
    pouch = Entity(
        model='cube',
        color=rag_color,
        scale=(0.12, 0.12, 0.12),
        parent=belt,
        position=(-0.2, -0.08, 0.05)
    )

    # Ragged loincloth (more visible)
    loincloth = Entity(
        model='cube',
        color=ursina_color.rgb(75/255, 65/255, 55/255),  # Slightly lighter brown
        scale=(0.35, 0.3, 0.08),  # Bigger and thicker
        parent=body,
        position=(0, -0.5, 0.15)  # Further forward
    )

    # Left hip joint
    left_hip = Entity(
        model='sphere',
        color=skin_dark,
        scale=0.2,
        parent=body,
        position=(-0.2, -0.5, 0)  # At body bottom
    )

    # Right hip joint
    right_hip = Entity(
        model='sphere',
        color=skin_dark,
        scale=0.2,
        parent=body,
        position=(0.2, -0.5, 0)  # At body bottom
    )

    # Left leg (skinny)
    left_leg = Entity(
        model='sphere',
        color=skin_color,
        scale=(0.25, 0.7, 0.25),  # Thin legs
        parent=body,
        position=(-0.2, -1.0, 0)  # Below body, adjusted for larger size
    )

    # Left foot (big goblin foot)
    left_foot = Entity(
        model='cube',
        color=skin_dark,
        scale=(0.18, 0.12, 0.28),
        parent=body,
        position=(-0.2, -1.42, 0.05)
    )

    # Right leg (skinny)
    right_leg = Entity(
        model='sphere',
        color=skin_color,
        scale=(0.25, 0.7, 0.25),  # Thin legs
        parent=body,
        position=(0.2, -1.0, 0)  # Below body, adjusted for larger size
    )

    # Right foot (big goblin foot)
    right_foot = Entity(
        model='cube',
        color=skin_dark,
        scale=(0.18, 0.12, 0.28),
        parent=body,
        position=(0.2, -1.42, 0.05)
    )

    # Bone necklace (center)
    necklace_cord = Entity(
        model='cube',
        color=leather_color,
        scale=(0.3, 0.03, 0.03),
        parent=body,
        position=(0, 0.45, 0.15)
    )

    # Bone pendant on necklace
    bone_pendant = Entity(
        model='cube',
        color=bone_color,
        scale=(0.08, 0.12, 0.05),
        parent=necklace_cord,
        position=(0, -0.08, 0)
    )

    # Store animation state in goblin entity
    goblin.idle_time = 0.0
    goblin.head_ref = head  # Reference for animation

    return goblin


def update_goblin_animation(goblin: Entity, dt: float):
    """
    Update goblin idle animation (nervous head movement)

    Args:
        goblin: Goblin entity to animate
        dt: Delta time since last frame
    """
    goblin.idle_time += dt

    # Nervous head darting (3.5 Hz)
    head_dart = math.sin(goblin.idle_time * 3.5) * 2.5

    # Apply head dart (subtle rotation)
    if hasattr(goblin, 'head_ref'):
        goblin.head_ref.rotation_y = head_dart
