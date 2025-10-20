"""
DNA Creature Factory - Level-based procedural enemy generation

Integrates DNA editor creatures into the roguelike game with level scaling.
"""

from ursina import Vec3, color as ursina_color
import constants as c


# ========================================
# ENEMY TYPE → CREATURE TYPE MAPPING
# ========================================

ENEMY_CREATURE_MAP = {
    c.ENEMY_STARTLE: 'starfish',    # Starfish creature
    c.ENEMY_SLIME: 'blob',          # Translucent blob
    c.ENEMY_SKELETON: 'polyp',      # Bone-white polyp stack
    c.ENEMY_ORC: 'tentacle',        # Muscular tentacle mass
    c.ENEMY_DEMON: 'medusa',        # Demonic medusa
    c.ENEMY_DRAGON: 'dragon',       # Space Harrier serpent
}


# ========================================
# LEVEL TIER CALCULATION
# ========================================

def get_level_tier(dungeon_level: int) -> str:
    """
    Calculate creature complexity tier based on dungeon level.

    Args:
        dungeon_level: Dungeon depth (1-25)

    Returns:
        Tier name: 'basic', 'moderate', 'advanced', 'horrific', or 'nightmare'
    """
    if dungeon_level <= 5:
        return 'basic'
    elif dungeon_level <= 10:
        return 'moderate'
    elif dungeon_level <= 15:
        return 'advanced'
    elif dungeon_level <= 20:
        return 'horrific'
    else:  # 21-25
        return 'nightmare'


def get_level_factor(dungeon_level: int) -> float:
    """
    Calculate normalized level factor (0.0 to 1.0).

    Args:
        dungeon_level: Dungeon depth (1-25)

    Returns:
        Float 0.0-1.0 representing progression
    """
    return min(1.0, (dungeon_level - 1) / 24.0)


# ========================================
# TENTACLE CREATURE DNA (Orc, Demon)
# ========================================

def generate_tentacle_dna(level: int, color_rgb: tuple) -> dict:
    """
    Generate DNA for TentacleCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)
        color_rgb: Base color RGB tuple (0-1 range)

    Returns:
        Dict of DNA parameters for TentacleCreature
    """
    level_factor = get_level_factor(level)

    # Tentacles: 2→12 (more tentacles = more dangerous)
    num_tentacles = 2 + int((level / 5.0) * 2)
    num_tentacles = min(12, num_tentacles)

    # Segments: 8→18 (longer, more complex tentacles)
    segments = 8 + int((level / 3.0))
    segments = min(18, segments)

    # Eyes: 1→8 (creepy factor)
    num_eyes = 1 + int(level / 5.0)
    num_eyes = min(8, num_eyes)

    # Body scale: 1.0→1.5 (size intimidation)
    body_scale = 1.0 + (level_factor * 0.5)

    # Thickness: 0.2→0.35 (girth)
    thickness = 0.2 + (level_factor * 0.15)

    # Branching: 0→2 (late-game complexity)
    branch_depth = min(2, int(level / 12.0))

    return {
        'num_tentacles': num_tentacles,
        'segments_per_tentacle': segments,
        'algorithm': 'bezier',
        'algorithm_params': {'control_strength': 0.4},
        'thickness_base': thickness,
        'taper_factor': 0.6,
        'branch_depth': branch_depth,
        'branch_count': 1,
        'body_scale': body_scale,
        'tentacle_color': color_rgb,
        'hue_shift': 0.1,
        'anim_speed': 2.0,
        'wave_amplitude': 0.05,
        'pulse_speed': 1.5,
        'pulse_amount': 0.05,
        'num_eyes': num_eyes,
        'eye_size_min': 0.1,
        'eye_size_max': 0.25,
        'eyeball_color': (1.0, 1.0, 1.0),
        'pupil_color': (0.0, 0.0, 0.0),
    }


# ========================================
# BLOB CREATURE DNA (Goblin, Slime)
# ========================================

def generate_blob_dna(level: int, color_rgb: tuple, transparency: float = 0.7) -> dict:
    """
    Generate DNA for BlobCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)
        color_rgb: Base color RGB tuple (0-1 range)
        transparency: Alpha transparency (0=opaque, 1=transparent)

    Returns:
        Dict of DNA parameters for BlobCreature
    """
    level_factor = get_level_factor(level)

    # Branch depth: 1→3 (tree complexity - guarantees structure at all levels)
    branch_depth = 1 + min(2, int(level / 8.0))

    # Branch count: 2→4 (children per node - more visual interest)
    branch_count = 2 + int(level / 12.0)
    branch_count = min(4, branch_count)

    # Cube size: 0.5→0.9 (larger cubes for late-game)
    cube_size_max = 0.5 + (level_factor * 0.4)
    cube_size_min = cube_size_max * 0.4  # Min is 40% of max

    # Spacing: 1.0→1.5 (more spread out)
    spacing = 1.0 + (level_factor * 0.5)

    return {
        'branch_depth': branch_depth,
        'branch_count': branch_count,
        'cube_size_min': cube_size_min,
        'cube_size_max': cube_size_max,
        'cube_spacing': spacing,
        'blob_color': color_rgb,
        'transparency': transparency,
        'jiggle_speed': 2.0,
        'pulse_amount': 0.1,
    }


# ========================================
# POLYP CREATURE DNA (Skeleton)
# ========================================

def generate_polyp_dna(level: int, color_rgb: tuple) -> dict:
    """
    Generate DNA for PolypCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)
        color_rgb: Base color RGB tuple (0-1 range)

    Returns:
        Dict of DNA parameters for PolypCreature
    """
    level_factor = get_level_factor(level)

    # Sphere count: 3→6 (height of creature)
    num_spheres = 3 + int(level / 5.0)
    num_spheres = min(6, num_spheres)

    # Tentacles per sphere: 4→8
    tentacles_per_sphere = 4 + int(level / 6.0)
    tentacles_per_sphere = min(8, tentacles_per_sphere)

    # Segments: 8→14
    segments = 8 + int(level / 4.0)
    segments = min(14, segments)

    return {
        'num_spheres': num_spheres,
        'base_sphere_size': 0.7,
        'spine_color': color_rgb,
        'curve_intensity': 0.4,
        'tentacles_per_sphere': tentacles_per_sphere,
        'segments_per_tentacle': segments,
        'thickness_base': 0.2,
        'taper_factor': 0.6,
        'anim_speed': 2.0,
        'pulse_amount': 0.08,
    }


# ========================================
# MEDUSA CREATURE DNA (Demon)
# ========================================

def generate_medusa_dna(level: int, color_rgb: tuple) -> dict:
    """
    Generate DNA for MedusaCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)
        color_rgb: Base color RGB tuple (0-1 range)

    Returns:
        Dict of DNA parameters for MedusaCreature
    """
    level_factor = get_level_factor(level)

    # Tentacles: 4→12
    num_tentacles = 4 + int(level / 3.0)
    num_tentacles = min(12, num_tentacles)

    # Segments: 8→16
    segments = 8 + int(level / 3.0)
    segments = min(16, segments)

    # Body scale: 0.8→1.3
    body_scale = 0.8 + (level_factor * 0.5)

    return {
        'num_tentacles': num_tentacles,
        'segments_per_tentacle': segments,
        'body_scale': body_scale,
        'tentacle_color': color_rgb,
        'thickness_base': 0.15,
        'taper_factor': 0.7,
        'anim_speed': 2.0,
        'wave_amplitude': 0.08,
        'pulse_speed': 1.5,
        'pulse_amount': 0.06,
    }


# ========================================
# DRAGON CREATURE DNA (Dragon)
# ========================================

def generate_dragon_dna(level: int) -> dict:
    """
    Generate DNA for DragonCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)

    Returns:
        Dict of DNA parameters for DragonCreature
    """
    level_factor = get_level_factor(level)

    # Segments: 10→24 (longer serpent)
    num_segments = 10 + int(level / 1.2)
    num_segments = min(24, num_segments)

    # Thickness: 0.25→0.4
    thickness = 0.25 + (level_factor * 0.15)

    # Head scale: 2.0→3.2
    head_scale = 2.0 + (level_factor * 1.2)

    # Eyes: 2→6
    num_eyes = 2 + int(level / 6.0)
    num_eyes = min(6, num_eyes)

    # Whiskers: 0→3 per side
    whiskers = min(3, int(level / 8.0))

    return {
        'num_segments': num_segments,
        'segment_thickness': thickness,
        'taper_factor': 0.6,
        'head_scale': head_scale,
        'body_color': (200, 40, 40),  # RGB 0-255 (Dragon expects this format)
        'head_color': (255, 200, 50),
        'weave_amplitude': 0.5,
        'bob_amplitude': 0.3,
        'anim_speed': 1.5,
        'num_eyes': num_eyes,
        'eye_size': 0.15,
        'eyeball_color': (255, 200, 50),  # RGB 0-255
        'pupil_color': (20, 0, 0),
        'mouth_size': 0.25,
        'mouth_color': (20, 0, 0),
        'num_whiskers_per_side': whiskers,
        'whisker_segments': 4,
        'whisker_thickness': 0.05,
        'spine_spike_color': (100, 20, 20),
    }


# ========================================
# STARFISH CREATURE DNA (Startle enemy)
# ========================================

def generate_starfish_dna(level: int, color_rgb: tuple) -> dict:
    """
    Generate DNA for StarfishCreature with level-based scaling.

    Args:
        level: Dungeon level (1-25)
        color_rgb: Base color RGB tuple (0-1 range)

    Returns:
        Dict of DNA parameters for StarfishCreature
    """
    level_factor = get_level_factor(level)

    # Arms: 4→8
    num_arms = 4 + int(level / 6.0)
    num_arms = min(8, num_arms)

    # Segments: 4→10
    arm_segments = 4 + int(level / 4.0)
    arm_segments = min(10, arm_segments)

    # Thickness: 0.25→0.5 (thicker arms for higher levels)
    arm_base_thickness = 0.25 + (level_factor * 0.25)

    # Body size: 0.6→1.0 (larger central body for higher levels)
    central_body_size = 0.6 + (level_factor * 0.4)

    # Curl factor: 0.2→0.5 (more curled arms for higher levels)
    curl_factor = 0.2 + (level_factor * 0.3)

    return {
        'num_arms': num_arms,
        'arm_segments': arm_segments,
        'central_body_size': central_body_size,
        'arm_base_thickness': arm_base_thickness,
        'starfish_color': color_rgb,
        'curl_factor': curl_factor,
        'anim_speed': 1.5,
        'pulse_amount': 0.06,
    }


# ========================================
# MAIN FACTORY FUNCTION
# ========================================

def create_dna_creature(enemy_type: str, position: Vec3, dungeon_level: int = 1):
    """
    Factory function to create DNA editor creatures for game enemies.

    Args:
        enemy_type: Enemy type constant (e.g., c.ENEMY_GOBLIN)
        position: Vec3 3D world position
        dungeon_level: Dungeon depth (1-25) for scaling

    Returns:
        Creature instance (TentacleCreature, BlobCreature, etc.)

    Raises:
        ValueError: If enemy_type is unknown
    """
    # Get enemy color from constants
    enemy_colors_rgb = {
        c.ENEMY_STARTLE: c.COLOR_ENEMY_STARTLE_RGB,
        c.ENEMY_SLIME: c.COLOR_ENEMY_SLIME_RGB,
        c.ENEMY_SKELETON: c.COLOR_ENEMY_SKELETON_RGB,
        c.ENEMY_ORC: c.COLOR_ENEMY_ORC_RGB,
        c.ENEMY_DEMON: c.COLOR_ENEMY_DEMON_RGB,
        c.ENEMY_DRAGON: c.COLOR_ENEMY_DRAGON_RGB,
    }

    color_rgb = enemy_colors_rgb.get(enemy_type, c.COLOR_ENEMY_STARTLE_RGB)

    # Get creature type mapping
    creature_type = ENEMY_CREATURE_MAP.get(enemy_type)

    if creature_type is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    # Generate DNA based on creature type
    creature = None

    try:
        if creature_type == 'tentacle':
            from dna_editor.models.creature import TentacleCreature
            dna = generate_tentacle_dna(dungeon_level, color_rgb)
            creature = TentacleCreature(**dna)

        elif creature_type == 'blob':
            from dna_editor.models.blob_creature import BlobCreature
            # Slime is more transparent than goblin
            transparency = 0.8 if enemy_type == c.ENEMY_SLIME else 0.6
            dna = generate_blob_dna(dungeon_level, color_rgb, transparency)
            creature = BlobCreature(**dna)

        elif creature_type == 'polyp':
            from dna_editor.models.polyp_creature import PolypCreature
            dna = generate_polyp_dna(dungeon_level, color_rgb)
            creature = PolypCreature(**dna)

        elif creature_type == 'medusa':
            from dna_editor.models.medusa_creature import MedusaCreature
            dna = generate_medusa_dna(dungeon_level, color_rgb)
            creature = MedusaCreature(**dna)

        elif creature_type == 'dragon':
            from dna_editor.models.dragon_creature import DragonCreature
            dna = generate_dragon_dna(dungeon_level)
            creature = DragonCreature(**dna)

        elif creature_type == 'starfish':
            from dna_editor.models.starfish_creature import StarfishCreature
            dna = generate_starfish_dna(dungeon_level, color_rgb)
            creature = StarfishCreature(**dna)

        # Set creature position and scale
        if creature:
            # Scale by enemy difficulty (smaller = early-game, larger = late-game)
            enemy_scales = {
                c.ENEMY_STARTLE: 0.4,  # Smallest (early-game)
                c.ENEMY_SLIME: 0.4,    # Smallest (early-game)
                c.ENEMY_SKELETON: 0.5, # Medium (mid-game)
                c.ENEMY_ORC: 0.5,      # Medium (mid-game)
                c.ENEMY_DEMON: 0.6,    # Larger (late-game)
                c.ENEMY_DRAGON: 0.6,   # Larger (late-game)
            }
            creature.root.scale = enemy_scales.get(enemy_type, 0.5)

            # Raise Y position to prevent floating inside ground
            creature.root.position = Vec3(position.x, position.y + 0.5, position.z)

            complexity = dna.get('num_tentacles') or dna.get('num_segments') or dna.get('branch_depth') or '?'
            print(f"✓ DNA: Created {creature_type} for {enemy_type} (lvl {dungeon_level}, complexity: {complexity})")

        return creature

    except Exception as e:
        import traceback
        print(f"\n⚠ FAILED to create {creature_type} creature for {enemy_type}:")
        print(f"  Error: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        print(f"  Falling back to simple cube\n")
        # Fallback to simple cube
        from ursina import Entity
        # Use STARTLE color as fallback (was GOBLIN)
        fallback_color = ursina_color.rgb(color_rgb[0], color_rgb[1], color_rgb[2])
        return Entity(
            model='cube',
            color=fallback_color,
            scale=0.5,
            position=position
        )
