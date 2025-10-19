"""
Warrior 3D Model - Enhanced armored tank with sword and shield

Creates a detailed 3D warrior model using Ursina primitives.
Features: Layered armor, detailed sword and shield, improved proportions.
Optimized for fast loading without procedural textures.
"""

from ursina import Entity, Vec3, color


def create_rivets(parent, positions, rivet_color, scale=0.02):
    """Create decorative rivets on armor"""
    rivets = []
    for pos in positions:
        rivet = Entity(
            parent=parent,
            model='sphere',
            color=rivet_color,
            scale=(scale, scale, scale * 0.5),
            position=pos
        )
        rivets.append(rivet)
    return rivets


def create_warrior_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    """
    Create an enhanced 3D warrior character model with improved proportions and detail.

    Args:
        position: Vec3 position for the model
        scale: Vec3 scale for the model

    Returns:
        Entity: Parent entity containing all model parts
    """
    warrior = Entity(position=position, scale=scale)

    # Enhanced color palette with more depth
    red_tunic = color.rgb(190/255, 50/255, 35/255)
    dark_red = color.rgb(150/255, 30/255, 20/255)
    steel_gray = color.rgb(130/255, 135/255, 145/255)
    polished_steel = color.rgb(180/255, 185/255, 195/255)
    dark_steel = color.rgb(90/255, 95/255, 100/255)
    bronze = color.rgb(140/255, 110/255, 55/255)
    dark_bronze = color.rgb(100/255, 75/255, 40/255)
    gold = color.rgb(200/255, 170/255, 40/255)
    bright_gold = color.rgb(220/255, 190/255, 60/255)
    skin_tone = color.rgb(210/255, 170/255, 140/255)
    royal_blue = color.rgb(40/255, 90/255, 160/255)
    deep_blue = color.rgb(25/255, 60/255, 120/255)
    dark_pants = color.rgb(70/255, 60/255, 50/255)
    leather_brown = color.rgb(110/255, 85/255, 50/255)
    dark_leather = color.rgb(80/255, 60/255, 35/255)
    iron_gray = color.rgb(95/255, 100/255, 110/255)

    # ========== TORSO & BODY ==========
    # Body (main torso) - slightly smaller
    body = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.45, 0.55, 0.28),
        position=(0, 0, 0)
    )

    # Body shading (darker layer for depth)
    body_shadow = Entity(
        parent=warrior,
        model='cube',
        color=dark_red,
        scale=(0.45, 0.55, 0.02),
        position=(0, -0.05, -0.15)
    )

    # Chest plate base layer (darker)
    chest_plate_base = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.50, 0.50, 0.05),
        position=(0, 0.06, 0.15)
    )

    # Chest plate (main armor) - brighter top layer
    chest_plate = Entity(
        parent=warrior,
        model='cube',
        color=polished_steel,
        scale=(0.48, 0.48, 0.04),
        position=(0, 0.08, 0.165)
    )

    # Chest plate segments (4 horizontal plates for detail)
    for i, y_pos in enumerate([0.22, 0.10, -0.02, -0.14]):
        segment = Entity(
            parent=warrior,
            model='cube',
            color=polished_steel if i % 2 == 0 else steel_gray,
            scale=(0.46, 0.08, 0.015),
            position=(0, y_pos, 0.18)
        )

    # Add decorative rivets to chest plate (improved pattern)
    rivet_positions = [
        # Top row
        (-0.18, 0.26, 0.19), (-0.06, 0.26, 0.19), (0.06, 0.26, 0.19), (0.18, 0.26, 0.19),
        # Middle rows
        (-0.18, 0.06, 0.19), (0.18, 0.06, 0.19),
        (-0.18, -0.10, 0.19), (0.18, -0.10, 0.19),
        # Center ornament
        (0, 0.24, 0.19), (0, -0.16, 0.19)
    ]
    chest_rivets = create_rivets(warrior, rivet_positions, dark_bronze, scale=0.020)

    # Back plate
    back_plate = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.46, 0.48, 0.04),
        position=(0, 0.04, -0.15)
    )

    # ========== HEAD & HELMET ==========
    # Neck (more visible, taller)
    neck = Entity(
        parent=warrior,
        model='sphere',
        color=skin_tone,
        scale=(0.14, 0.18, 0.14),
        position=(0, 0.38, 0)
    )

    # Head (properly connected to neck)
    head = Entity(
        parent=warrior,
        model='sphere',
        color=skin_tone,
        scale=(0.26, 0.28, 0.26),
        position=(0, 0.48, 0)
    )

    # Gorget base (neck armor) - connects helmet to chest, lower position
    gorget_base = Entity(
        parent=warrior,
        model='sphere',
        color=dark_steel,
        scale=(0.22, 0.10, 0.22),
        position=(0, 0.30, 0)
    )

    # Gorget top layer
    gorget = Entity(
        parent=warrior,
        model='sphere',
        color=polished_steel,
        scale=(0.20, 0.11, 0.20),
        position=(0, 0.31, 0)
    )

    # Helmet base (rounded top instead of flat box)
    helmet_base = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.30, 0.24, 0.30),
        position=(0, 0.56, 0)
    )

    # Helmet top cap (polished)
    helmet_top = Entity(
        parent=warrior,
        model='sphere',
        color=polished_steel,
        scale=(0.29, 0.18, 0.29),
        position=(0, 0.59, 0)
    )

    # Helmet brow guard (horizontal band)
    brow_guard = Entity(
        parent=warrior,
        model='cube',
        color=dark_steel,
        scale=(0.30, 0.05, 0.30),
        position=(0, 0.48, 0)
    )

    # Face plate (main visor)
    face_plate = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.26, 0.16, 0.08),
        position=(0, 0.48, 0.17)
    )

    # Visor slit (darker for eyes)
    visor_slit = Entity(
        parent=warrior,
        model='cube',
        color=color.rgb(0.1, 0.1, 0.1),
        scale=(0.20, 0.04, 0.01),
        position=(0, 0.50, 0.22)
    )

    # Nose guard (vertical center piece)
    nose_guard = Entity(
        parent=warrior,
        model='cube',
        color=polished_steel,
        scale=(0.04, 0.14, 0.10),
        position=(0, 0.47, 0.18)
    )

    # Cheek guards (left and right)
    left_cheek = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.08, 0.18, 0.10),
        position=(-0.16, 0.44, 0.14)
    )

    right_cheek = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.08, 0.18, 0.10),
        position=(0.16, 0.44, 0.14)
    )

    # Helmet crest (subtle ridge on top - much smaller)
    crest = Entity(
        parent=warrior,
        model='cube',
        color=dark_bronze,
        scale=(0.20, 0.04, 0.04),
        position=(0, 0.64, 0)
    )

    # Crest front ornament (small gold accent)
    crest_front = Entity(
        parent=warrior,
        model='sphere',
        color=gold,
        scale=(0.03, 0.03, 0.03),
        position=(0, 0.64, 0.12)
    )

    # ========== SHOULDERS ==========
    # Left pauldron (main)
    left_pauldron_main = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.24, 0.18, 0.24),
        position=(-0.38, 0.28, 0)
    )

    # Left pauldron plates (2 layers for detail)
    for i, y_offset in enumerate([0.02, -0.04]):
        plate = Entity(
            parent=warrior,
            model='sphere',
            color=polished_steel,
            scale=(0.22, 0.04, 0.22),
            position=(-0.38, 0.28 + y_offset, -0.01 - i * 0.02)
        )

    # Right pauldron (main)
    right_pauldron_main = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.24, 0.18, 0.24),
        position=(0.38, 0.28, 0)
    )

    # Right pauldron plates (2 layers)
    for i, y_offset in enumerate([0.02, -0.04]):
        plate = Entity(
            parent=warrior,
            model='sphere',
            color=polished_steel,
            scale=(0.22, 0.04, 0.22),
            position=(0.38, 0.28 + y_offset, -0.01 - i * 0.02)
        )

    # ========== ARMS ==========
    # Left upper arm
    left_upper_arm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.16, 0.48, 0.16),
        position=(-0.38, 0.06, 0)
    )

    # Left elbow guard
    left_elbow = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.12, 0.10, 0.12),
        position=(-0.38, -0.16, 0)
    )

    # Left forearm
    left_forearm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.15, 0.36, 0.15),
        position=(-0.38, -0.36, 0)
    )

    # Left gauntlet
    left_gauntlet = Entity(
        parent=warrior,
        model='cube',
        color=iron_gray,
        scale=(0.16, 0.14, 0.16),
        position=(-0.38, -0.54, 0)
    )

    # Left gauntlet plates (2 finger plates)
    for i, z_off in enumerate([0.04, -0.02]):
        plate = Entity(
            parent=warrior,
            model='cube',
            color=steel_gray,
            scale=(0.17, 0.030, 0.025),
            position=(-0.38, -0.54 + z_off, 0.09)
        )

    # Right upper arm
    right_upper_arm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.16, 0.48, 0.16),
        position=(0.38, 0.06, 0)
    )

    # Right elbow guard
    right_elbow = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.12, 0.10, 0.12),
        position=(0.38, -0.16, 0)
    )

    # Right forearm
    right_forearm = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.15, 0.36, 0.15),
        position=(0.38, -0.36, 0)
    )

    # Right gauntlet
    right_gauntlet = Entity(
        parent=warrior,
        model='cube',
        color=iron_gray,
        scale=(0.16, 0.14, 0.16),
        position=(0.38, -0.54, 0)
    )

    # Right gauntlet plates (2 finger plates)
    for i, z_off in enumerate([0.04, -0.02]):
        plate = Entity(
            parent=warrior,
            model='cube',
            color=steel_gray,
            scale=(0.17, 0.030, 0.025),
            position=(0.38, -0.54 + z_off, 0.09)
        )

    # ========== SWORD (DETAILED) ==========
    # Blade (main sword body) - positioned to extend diagonally forward-up from hand
    sword_blade = Entity(
        parent=warrior,
        model='cube',
        color=polished_steel,
        scale=(0.06, 0.78, 0.06),
        position=(0.42, -0.24, 0.535),
        rotation=(55, 0, 0)  # Tilt forward 55 degrees
    )

    # Fuller groove (blade center detail)
    fuller = Entity(
        parent=warrior,
        model='cube',
        color=color.rgb(0.55, 0.55, 0.60),
        scale=(0.02, 0.68, 0.01),
        position=(0.42, -0.22, 0.570),
        rotation=(55, 0, 0)  # Match blade rotation
    )

    # Crossguard (center)
    crossguard_center = Entity(
        parent=warrior,
        model='cube',
        color=bronze,
        scale=(0.28, 0.06, 0.10),
        position=(0.38, -0.464, 0.216),
        rotation=(55, 0, 0)  # Match blade rotation
    )

    # Crossguard ends (decorative spheres)
    for x_sign in [-1, 1]:
        end = Entity(
            parent=warrior,
            model='sphere',
            color=bronze,
            scale=(0.05, 0.05, 0.08),
            position=(0.38 + x_sign * 0.14, -0.464, 0.216),
            rotation=(55, 0, 0)  # Match blade rotation
        )

    # Hilt (leather grip)
    hilt = Entity(
        parent=warrior,
        model='cube',
        color=leather_brown,
        scale=(0.08, 0.22, 0.08),
        position=(0.38, -0.54, 0.10),
        rotation=(55, 0, 0)  # Match blade rotation
    )

    # Hilt wrapping detail (3 wire wraps)
    for y, z in [(-0.494, 0.161), (-0.540, 0.100), (-0.586, 0.029)]:
        wrap = Entity(
            parent=warrior,
            model='cube',
            color=dark_bronze,
            scale=(0.09, 0.015, 0.09),
            position=(0.38, y, z),
            rotation=(55, 0, 0)  # Match blade rotation
        )

    # Pommel (sphere)
    pommel = Entity(
        parent=warrior,
        model='sphere',
        color=bronze,
        scale=(0.10, 0.10, 0.10),
        position=(0.38, -0.66, -0.077),
        rotation=(55, 0, 0)  # Match blade rotation
    )

    # Pommel gem (decorative)
    gem = Entity(
        parent=warrior,
        model='sphere',
        color=color.rgb(0.8, 0.1, 0.1),  # Ruby red
        scale=(0.04, 0.04, 0.04),
        position=(0.38, -0.709, -0.041),
        rotation=(55, 0, 0)  # Match blade rotation
    )

    # ========== SHIELD (ENHANCED HERALDRY) ==========
    # Shield base (main body)
    shield_base = Entity(
        parent=warrior,
        model='cube',
        color=royal_blue,
        scale=(0.40, 0.54, 0.10),
        position=(-0.48, -0.02, 0.10),
        rotation=(0, 18, -8)
    )

    # Shield depth layer (darker for 3D effect)
    shield_depth = Entity(
        parent=warrior,
        model='cube',
        color=deep_blue,
        scale=(0.38, 0.52, 0.06),
        position=(-0.48, -0.04, 0.08),
        rotation=(0, 18, -8)
    )

    # Shield rim (metal reinforcement) - outer frame
    shield_rim_outer = Entity(
        parent=warrior,
        model='cube',
        color=dark_steel,
        scale=(0.42, 0.56, 0.03),
        position=(-0.48, -0.02, 0.16),
        rotation=(0, 18, -8)
    )

    # Shield rim inner (brighter metal)
    shield_rim_inner = Entity(
        parent=warrior,
        model='cube',
        color=iron_gray,
        scale=(0.40, 0.54, 0.025),
        position=(-0.48, -0.02, 0.165),
        rotation=(0, 18, -8)
    )

    # Shield boss outer ring (large gold centerpiece)
    shield_boss_ring = Entity(
        parent=warrior,
        model='sphere',
        color=gold,
        scale=(0.15, 0.15, 0.06),
        position=(-0.48, -0.02, 0.19),
        rotation=(0, 18, -8)
    )

    # Shield boss center (brighter)
    shield_boss = Entity(
        parent=warrior,
        model='sphere',
        color=bright_gold,
        scale=(0.10, 0.10, 0.05),
        position=(-0.48, -0.02, 0.20),
        rotation=(0, 18, -8)
    )

    # Heraldic cross design (4 arms)
    # Vertical bar
    cross_vertical = Entity(
        parent=warrior,
        model='cube',
        color=gold,
        scale=(0.06, 0.36, 0.015),
        position=(-0.48, -0.02, 0.175),
        rotation=(0, 18, -8)
    )

    # Horizontal bar
    cross_horizontal = Entity(
        parent=warrior,
        model='cube',
        color=gold,
        scale=(0.28, 0.06, 0.015),
        position=(-0.48, -0.02, 0.175),
        rotation=(0, 18, -8)
    )

    # Decorative corner emblems (4 quadrants)
    for x_sign, y_sign in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
        emblem = Entity(
            parent=warrior,
            model='sphere',
            color=bright_gold,
            scale=(0.04, 0.04, 0.02),
            position=(-0.48 + x_sign * 0.10, -0.02 + y_sign * 0.16, 0.178),
            rotation=(0, 18, -8)
        )

    # Shield edge reinforcements (top and bottom)
    for y_off in [-0.24, 0.24]:
        reinforce = Entity(
            parent=warrior,
            model='cube',
            color=dark_bronze,
            scale=(0.36, 0.03, 0.02),
            position=(-0.48, y_off, 0.17),
            rotation=(0, 18, -8)
        )

    # ========== LEGS & LOWER BODY ==========
    # Pelvis/Hip area (connects torso to legs)
    pelvis = Entity(
        parent=warrior,
        model='cube',
        color=dark_pants,
        scale=(0.46, 0.22, 0.30),
        position=(0, -0.38, 0)
    )

    # Hip padding (adds volume)
    hip_padding = Entity(
        parent=warrior,
        model='cube',
        color=red_tunic,
        scale=(0.48, 0.18, 0.28),
        position=(0, -0.36, 0)
    )

    # Belt (on top of hips)
    belt_base = Entity(
        parent=warrior,
        model='cube',
        color=leather_brown,
        scale=(0.52, 0.10, 0.32),
        position=(0, -0.28, 0)
    )

    # Belt buckle
    buckle = Entity(
        parent=warrior,
        model='cube',
        color=bronze,
        scale=(0.10, 0.10, 0.04),
        position=(0, -0.28, 0.18)
    )

    # Tassets (hip armor plates) - positioned lower
    left_tasset = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.18, 0.22, 0.04),
        position=(-0.18, -0.44, 0.16)
    )

    right_tasset = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.18, 0.22, 0.04),
        position=(0.18, -0.44, 0.16)
    )

    # Groin/codpiece armor (center protection)
    codpiece = Entity(
        parent=warrior,
        model='cube',
        color=polished_steel,
        scale=(0.14, 0.16, 0.04),
        position=(0, -0.46, 0.16)
    )

    # Legs (thighs) - positioned higher to connect with pelvis
    left_thigh = Entity(
        parent=warrior,
        model='cube',
        color=dark_pants,
        scale=(0.22, 0.46, 0.22),
        position=(-0.16, -0.68, 0)
    )

    right_thigh = Entity(
        parent=warrior,
        model='cube',
        color=dark_pants,
        scale=(0.22, 0.46, 0.22),
        position=(0.16, -0.68, 0)
    )

    # Knee guards (main)
    left_knee_main = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.14, 0.12, 0.14),
        position=(-0.16, -0.92, 0.04)
    )

    # Left knee plates (2 layers)
    for i in range(2):
        plate = Entity(
            parent=warrior,
            model='cube',
            color=polished_steel,
            scale=(0.16, 0.030, 0.02),
            position=(-0.16, -0.92 - i * 0.05, 0.13)
        )

    right_knee_main = Entity(
        parent=warrior,
        model='sphere',
        color=steel_gray,
        scale=(0.14, 0.12, 0.14),
        position=(0.16, -0.92, 0.04)
    )

    # Right knee plates (2 layers)
    for i in range(2):
        plate = Entity(
            parent=warrior,
            model='cube',
            color=polished_steel,
            scale=(0.16, 0.030, 0.02),
            position=(0.16, -0.92 - i * 0.05, 0.13)
        )

    # Lower legs (shins)
    left_shin = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.20, 0.42, 0.20),
        position=(-0.16, -1.16, 0)
    )

    right_shin = Entity(
        parent=warrior,
        model='cube',
        color=steel_gray,
        scale=(0.20, 0.42, 0.20),
        position=(0.16, -1.16, 0)
    )

    # Boots (enhanced with details)
    # Left boot base
    left_boot = Entity(
        parent=warrior,
        model='cube',
        color=dark_leather,
        scale=(0.16, 0.12, 0.22),
        position=(-0.16, -1.42, 0.05)
    )

    # Left boot top (lighter leather)
    left_boot_top = Entity(
        parent=warrior,
        model='cube',
        color=leather_brown,
        scale=(0.17, 0.04, 0.20),
        position=(-0.16, -1.36, 0.04)
    )

    # Left boot toe cap (steel)
    left_toe_cap = Entity(
        parent=warrior,
        model='cube',
        color=iron_gray,
        scale=(0.16, 0.10, 0.04),
        position=(-0.16, -1.42, 0.17)
    )

    # Right boot base
    right_boot = Entity(
        parent=warrior,
        model='cube',
        color=dark_leather,
        scale=(0.16, 0.12, 0.22),
        position=(0.16, -1.42, 0.05)
    )

    # Right boot top (lighter leather)
    right_boot_top = Entity(
        parent=warrior,
        model='cube',
        color=leather_brown,
        scale=(0.17, 0.04, 0.20),
        position=(0.16, -1.36, 0.04)
    )

    # Right boot toe cap (steel)
    right_toe_cap = Entity(
        parent=warrior,
        model='cube',
        color=iron_gray,
        scale=(0.16, 0.10, 0.04),
        position=(0.16, -1.42, 0.17)
    )

    # ========== HEROIC POSE ADJUSTMENTS ==========
    # Apply slight rotations and position adjustments for dynamic stance
    # (Optional: uncomment to add dynamic pose)
    # warrior.rotation_y = -5  # Slight turn
    # warrior.rotation_z = 2   # Slight tilt

    return warrior


__all__ = ['create_warrior_model']
