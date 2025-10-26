"""
Shield 3D model - Defense armor with rarity variants

Procedurally generated 3D model using Ursina primitives.
"""

from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color

# Import toon shader system
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add dna_editor to path (after project root)
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.append(dna_editor_path)

from dna_editor.shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale

# Import radial gradient shader for glow effects
from shaders.radial_gradient_shader import create_force_field_shader


def create_shield_3d(position: Vec3, rarity: str) -> Entity:
    """
    Create a 3D shield model with rarity-based appearance
    Medieval kite shield with tapered pointed bottom

    Args:
        position: 3D world position
        rarity: Item rarity (common, uncommon, rare, epic, legendary)

    Returns:
        Entity: Shield 3D model
    """
    # Container entity (invisible parent)
    shield = Entity(position=position)

    # Create toon shader instances (shared across all shield components)
    toon_shader = create_toon_shader()
    toon_shader_lite = create_toon_shader_lite()

    # Create radial gradient shader for glow effects (force field preset for shields)
    radial_glow_shader = create_force_field_shader()

    # Height configuration - shields get progressively taller with rarity
    height_config = {
        c.RARITY_COMMON:     {"face_h": 0.35, "taper_h": 0.15},  # Compact
        c.RARITY_UNCOMMON:   {"face_h": 0.40, "taper_h": 0.16},  # Slightly taller
        c.RARITY_RARE:       {"face_h": 0.45, "taper_h": 0.18},  # Medium
        c.RARITY_EPIC:       {"face_h": 0.52, "taper_h": 0.20},  # Tall
        c.RARITY_LEGENDARY:  {"face_h": 0.60, "taper_h": 0.22},  # Tower shield
    }

    config = height_config.get(rarity, height_config[c.RARITY_COMMON])
    face_height = config["face_h"]
    taper_height = config["taper_h"]
    total_height = face_height + taper_height
    shield_width = 0.28

    # Rarity-based colors
    if rarity == c.RARITY_COMMON:
        face_color = rgb_to_ursina_color(120, 90, 60)  # Wooden brown
        rim_color = rgb_to_ursina_color(80, 60, 40)  # Dark brown
        boss_color = rgb_to_ursina_color(140, 140, 140)  # Iron
        has_glow = False
    elif rarity == c.RARITY_UNCOMMON:
        face_color = rgb_to_ursina_color(140, 140, 150)  # Steel gray
        rim_color = rgb_to_ursina_color(100, 100, 110)  # Dark steel
        boss_color = rgb_to_ursina_color(180, 140, 80)  # Brass
        has_glow = False
    elif rarity == c.RARITY_RARE:
        face_color = rgb_to_ursina_color(150, 180, 255)  # Blue steel
        rim_color = rgb_to_ursina_color(100, 130, 200)  # Dark blue
        boss_color = rgb_to_ursina_color(192, 192, 192)  # Silver
        has_glow = False
    elif rarity == c.RARITY_EPIC:
        face_color = rgb_to_ursina_color(200, 100, 255)  # Purple
        rim_color = rgb_to_ursina_color(150, 50, 200)  # Dark purple
        boss_color = rgb_to_ursina_color(220, 180, 100)  # Gold
        has_glow = True
        glow_color = rgb_to_ursina_color(200, 100, 255)
    else:  # LEGENDARY
        face_color = rgb_to_ursina_color(255, 215, 0)  # Gold
        rim_color = rgb_to_ursina_color(200, 160, 0)  # Dark gold
        boss_color = rgb_to_ursina_color(100, 200, 255)  # Bright cyan
        has_glow = True
        glow_color = rgb_to_ursina_color(100, 200, 255)

    # Glow effect for epic/legendary (scaled based on total height)
    if has_glow:
        glow_scale = 0.30 + (total_height * 0.15)
        glow = Entity(
            model='sphere',
            color=glow_color,
            scale=glow_scale,
            parent=shield,
            position=(0, 0, 0),
            alpha=0.4,  # Increased from 0.3 - shader will create gradient
            unlit=True,
            shader=radial_glow_shader
        )

    # === CORE STRUCTURE ===

    # 1. Main Shield Face (upper section)
    face_y_offset = taper_height / 2  # Position upper section above center
    face_shader = get_shader_for_scale(face_height, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    face = Entity(
        model='cube',
        color=face_color,
        scale=(shield_width, face_height, 0.08),
        parent=shield,
        position=(0, face_y_offset, 0),
        shader=face_shader
    )

    # 2. Lower Taper (creates kite shield pointed bottom)
    taper_shader = get_shader_for_scale(taper_height, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    taper = Entity(
        model='cube',
        color=face_color,
        scale=(0.20, taper_height, 0.08),  # Narrower than main face
        parent=shield,
        position=(0, -face_height / 2, 0),  # Below main face
        shader=taper_shader
    )

    # 3. Shield Rim/Border (wraps both face and taper)
    rim_shader = get_shader_for_scale(total_height, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    rim = Entity(
        model='cube',
        color=rim_color,
        scale=(shield_width + 0.02, total_height + 0.02, 0.06),
        parent=shield,
        position=(0, 0, -0.05),  # Pushed back to avoid z-fighting
        shader=rim_shader
    )

    # 4. Central Vertical Spine (raised ridge)
    spine_height = total_height * 0.8
    spine_shader = get_shader_for_scale(spine_height, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    spine = Entity(
        model='cube',
        color=rim_color.tint(-0.1),  # Slightly darker than rim
        scale=(0.06, spine_height, 0.10),  # Taller than face depth
        parent=shield,
        position=(0, 0, 0.04),
        shader=spine_shader
    )

    # 5. Center Boss (on upper face section)
    boss_shader = get_shader_for_scale(0.12, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
    boss = Entity(
        model='sphere',
        color=boss_color,
        scale=0.12,  # Slightly larger than before
        parent=shield,
        position=(0, face_y_offset * 0.5, 0.06),  # Positioned on upper face
        shader=boss_shader
    )

    # === REINFORCEMENTS AND DETAILS ===

    # 6. Top Corner Reinforcements (rare+ only)
    if rarity in [c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        corner_y = face_y_offset + (face_height / 2) - 0.04
        corner_positions = [
            (-shield_width / 2 + 0.04, corner_y, 0.05),
            (shield_width / 2 - 0.04, corner_y, 0.05),
        ]
        corner_shader = get_shader_for_scale(0.08, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
        for pos in corner_positions:
            corner = Entity(
                model='cube',
                color=boss_color,
                scale=(0.08, 0.08, 0.10),
                parent=shield,
                position=pos,
                shader=corner_shader
            )

    # 7. Horizontal Bands (epic/legendary only)
    if rarity in [c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        band_shader = get_shader_for_scale(0.25, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
        # First band in upper third
        band1_y = face_y_offset + (face_height / 4)
        band1 = Entity(
            model='cube',
            color=boss_color,
            scale=(0.25, 0.03, 0.09),
            parent=shield,
            position=(0, band1_y, 0.04),
            shader=band_shader
        )

        # Second band only for legendary (middle section)
        if rarity == c.RARITY_LEGENDARY:
            band2_y = face_y_offset - (face_height / 4)
            band2 = Entity(
                model='cube',
                color=boss_color,
                scale=(0.25, 0.03, 0.09),
                parent=shield,
                position=(0, band2_y, 0.04),
                shader=band_shader
            )

    # 8. Rivets/Studs along spine (uncommon+ only)
    if rarity in [c.RARITY_UNCOMMON, c.RARITY_RARE, c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        num_rivets = 4 if rarity == c.RARITY_UNCOMMON else 6
        rivet_color = boss_color.tint(-0.2)
        rivet_shader = get_shader_for_scale(0.03, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

        # Distribute rivets along spine
        for i in range(num_rivets):
            rivet_y = (spine_height / 2) - (i * spine_height / (num_rivets - 1))
            rivet = Entity(
                model='sphere',
                color=rivet_color,
                scale=0.03,
                parent=shield,
                position=(0, rivet_y, 0.08),
                shader=rivet_shader
            )

    # 9. Pointed Tip Reinforcement (epic/legendary only)
    if rarity in [c.RARITY_EPIC, c.RARITY_LEGENDARY]:
        tip_y = -face_height / 2 - taper_height / 2 + 0.03
        tip_color = boss_color if rarity == c.RARITY_LEGENDARY else boss_color.tint(-0.1)
        tip_shader = get_shader_for_scale(0.06, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
        tip = Entity(
            model='sphere',
            color=tip_color,
            scale=0.06,
            parent=shield,
            position=(0, tip_y, 0.05),
            shader=tip_shader
        )

    # Store animation state
    shield.float_time = 0.0
    shield.rotation_speed = 50.0

    return shield
