"""
Animation generation for ability icons.

This module combines effects and symbols to create complete animated
icon sequences for each ability type.
"""
from typing import List
from PIL import Image, ImageChops
from ability_icons.generator import RandomSeed, IconGenerator, blend_images
from ability_icons.effects import (
    create_energy_vortex, create_swirling_particles, create_energy_burst,
    create_smoke_tendrils, create_ice_crystals, create_speed_streaks,
    create_fire_embers
)
from ability_icons.symbols import create_symbol_image


# Icon size for all abilities
ICON_SIZE = 256
TOTAL_FRAMES = 8


def generate_fireball_frames(seed: int = 10001) -> List[Image.Image]:
    """Generate 8 animation frames for Fireball ability.

    Creates orange/red energy vortex with flame symbol and rising embers.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (255, 140, 0)  # Orange
        secondary_color = (220, 50, 20)  # Red
        symbol_color = (255, 200, 100)  # Bright yellow-orange

        for frame in range(TOTAL_FRAMES):
            # Base: Energy vortex (rotating)
            vortex = create_energy_vortex(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color, secondary_color,
                num_spirals=3, clockwise=True
            )

            # Layer 1: Rising embers
            embers = create_fire_embers(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color, secondary_color,
                num_embers=40
            )

            # Layer 2: Flame symbol (pulsing)
            pulse = 0.9 + 0.1 * (frame / TOTAL_FRAMES)
            symbol_size = int(ICON_SIZE * 0.5 * pulse)
            flame_symbol = create_symbol_image('flame', symbol_size, symbol_color + (200,))

            # Composite layers
            result = vortex.copy()
            result = Image.alpha_composite(result, embers)
            # Center the symbol
            symbol_x = (ICON_SIZE - symbol_size) // 2
            symbol_y = (ICON_SIZE - symbol_size) // 2
            result.paste(flame_symbol, (symbol_x, symbol_y), flame_symbol)

            frames.append(result)

    return frames


def generate_frost_nova_frames(seed: int = 10002) -> List[Image.Image]:
    """Generate 8 animation frames for Frost Nova ability.

    Creates cyan/white ice crystals with snowflake symbol.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (100, 200, 255)  # Cyan
        secondary_color = (200, 230, 255)  # Light blue/white
        symbol_color = (255, 255, 255)  # White

        for frame in range(TOTAL_FRAMES):
            # Base: Ice crystals radiating outward
            crystals = create_ice_crystals(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color,
                num_crystals=24
            )

            # Layer 1: Particle ring
            particles = create_swirling_particles(
                ICON_SIZE, frame, TOTAL_FRAMES,
                secondary_color,
                num_particles=20,
                orbit_radius=0.35
            )

            # Layer 2: Rotating snowflake symbol
            rotation = (frame / TOTAL_FRAMES) * 60  # Slow rotation
            symbol_size = int(ICON_SIZE * 0.6)
            snowflake_symbol = create_symbol_image(
                'snowflake', symbol_size,
                symbol_color + (220,),
                rotation=rotation
            )

            # Composite layers
            result = crystals.copy()
            result = Image.alpha_composite(result, particles)
            # Center the snowflake
            symbol_x = (ICON_SIZE - symbol_size) // 2
            symbol_y = (ICON_SIZE - symbol_size) // 2
            result.paste(snowflake_symbol, (symbol_x, symbol_y), snowflake_symbol)

            frames.append(result)

    return frames


def generate_heal_frames(seed: int = 10003) -> List[Image.Image]:
    """Generate 8 animation frames for Heal/HealingTouch ability.

    Creates green/gold swirl with heart or cross symbol and sparkles.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (50, 255, 100)  # Green
        secondary_color = (255, 220, 80)  # Gold
        symbol_color = (255, 50, 100)  # Bright pink/red for visibility
        outline_color = (255, 255, 255)  # White outline

        for frame in range(TOTAL_FRAMES):
            # Base: Gentle energy vortex
            vortex = create_energy_vortex(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color, secondary_color,
                num_spirals=2, clockwise=False  # Counter-clockwise for peaceful feel
            )

            # Layer 1: Rising sparkle particles
            sparkles = create_swirling_particles(
                ICON_SIZE, frame, TOTAL_FRAMES,
                secondary_color,
                num_particles=25,
                orbit_radius=0.25
            )

            # Layer 2: Heart symbol (pulsing)
            pulse = 0.85 + 0.15 * abs(frame - TOTAL_FRAMES / 2) / (TOTAL_FRAMES / 2)
            symbol_size = int(ICON_SIZE * 0.5 * pulse)
            heart_symbol = create_symbol_image('heart', symbol_size, symbol_color + (240,), outline_color=outline_color + (255,))

            # Composite layers
            result = vortex.copy()
            result = Image.alpha_composite(result, sparkles)
            # Center the symbol
            symbol_x = (ICON_SIZE - symbol_size) // 2
            symbol_y = (ICON_SIZE - symbol_size) // 2
            result.paste(heart_symbol, (symbol_x, symbol_y), heart_symbol)

            frames.append(result)

    return frames


def generate_dash_frames(seed: int = 10004) -> List[Image.Image]:
    """Generate 8 animation frames for Dash ability.

    Creates purple/blue speed streaks with arrow symbol.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (180, 100, 255)  # Purple
        secondary_color = (100, 150, 255)  # Blue
        symbol_color = (220, 200, 255)  # Light purple

        for frame in range(TOTAL_FRAMES):
            # Base: Speed streaks (diagonal)
            streaks = create_speed_streaks(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color,
                direction=45  # Diagonal up-right
            )

            # Layer 1: Energy burst for motion
            burst = create_energy_burst(
                ICON_SIZE, frame, TOTAL_FRAMES,
                secondary_color,
                num_rays=8
            )

            # Layer 2: Arrow symbol pointing direction
            symbol_size = int(ICON_SIZE * 0.6)
            arrow_symbol = create_symbol_image(
                'arrow', symbol_size,
                symbol_color + (230,),
                rotation=45  # Match streak direction
            )

            # Composite layers
            result = streaks.copy()
            result = blend_images(result, burst, mode='add', alpha=0.6)
            # Center the arrow symbol
            symbol_x = (ICON_SIZE - symbol_size) // 2
            symbol_y = (ICON_SIZE - symbol_size) // 2
            result.paste(arrow_symbol, (symbol_x, symbol_y), arrow_symbol)

            frames.append(result)

    return frames


def generate_shadow_step_frames(seed: int = 10005) -> List[Image.Image]:
    """Generate 8 animation frames for Shadow Step ability.

    Creates gray/black smoke with skull or shadow symbol.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (80, 80, 100)  # Dark gray
        secondary_color = (40, 40, 50)  # Near black
        symbol_color = (150, 150, 170)  # Light gray

        for frame in range(TOTAL_FRAMES):
            # Base: Wispy smoke tendrils
            smoke = create_smoke_tendrils(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color,
                num_tendrils=6
            )

            # Layer 1: Dark particles
            particles = create_swirling_particles(
                ICON_SIZE, frame, TOTAL_FRAMES,
                secondary_color,
                num_particles=30,
                orbit_radius=0.3
            )

            # Layer 2: Skull symbol (fading in/out)
            fade = 0.5 + 0.5 * abs(frame - TOTAL_FRAMES / 2) / (TOTAL_FRAMES / 2)
            alpha = int(200 * fade)
            skull_symbol = create_symbol_image(
                'skull', int(ICON_SIZE * 0.5),
                symbol_color + (alpha,)
            )

            # Composite layers
            result = smoke.copy()
            result = Image.alpha_composite(result, particles)
            # Center the symbol
            symbol_x = (ICON_SIZE - int(ICON_SIZE * 0.5)) // 2
            symbol_y = (ICON_SIZE - int(ICON_SIZE * 0.5)) // 2
            result.paste(skull_symbol, (symbol_x, symbol_y), skull_symbol)

            frames.append(result)

    return frames


def generate_whirlwind_frames(seed: int = 10006) -> List[Image.Image]:
    """Generate 8 animation frames for Whirlwind ability.

    Creates red/white tornado vortex with spinning blade symbols.

    Args:
        seed: Random seed for deterministic generation

    Returns:
        List of 8 PIL Images (256x256 RGBA)
    """
    frames = []

    with RandomSeed(seed):
        primary_color = (255, 80, 80)  # Red
        secondary_color = (255, 200, 200)  # Light red/white
        symbol_color = (255, 255, 255)  # White

        for frame in range(TOTAL_FRAMES):
            # Base: Fast rotating vortex
            vortex = create_energy_vortex(
                ICON_SIZE, frame, TOTAL_FRAMES,
                primary_color, secondary_color,
                num_spirals=4, clockwise=True
            )

            # Layer 1: Speed particles in circular motion
            particles = create_swirling_particles(
                ICON_SIZE, frame, TOTAL_FRAMES,
                secondary_color,
                num_particles=35,
                orbit_radius=0.35
            )

            # Layer 2: Multiple spinning blade symbols
            rotation = (frame / TOTAL_FRAMES) * 360  # Fast spin
            blades_layer = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))

            # 3 blades at different angles
            blade_size = int(ICON_SIZE * 0.5)
            blade_x = (ICON_SIZE - blade_size) // 2
            blade_y = (ICON_SIZE - blade_size) // 2

            for i in range(3):
                blade_rotation = rotation + i * 120
                blade_symbol = create_symbol_image(
                    'blade', blade_size,
                    symbol_color + (180,),
                    rotation=blade_rotation
                )
                # Paste centered blade onto layer
                blades_layer.paste(blade_symbol, (blade_x, blade_y), blade_symbol)

            # Composite layers
            result = vortex.copy()
            result = Image.alpha_composite(result, particles)
            result = Image.alpha_composite(result, blades_layer)

            frames.append(result)

    return frames


def generate_all_ability_frames() -> dict:
    """Generate all ability icon animations.

    Returns:
        Dictionary mapping ability names to lists of 8 frames:
        {
            "Fireball": [frame0, frame1, ..., frame7],
            "Frost Nova": [frame0, frame1, ..., frame7],
            ...
        }
    """
    ability_frames = {
        "Fireball": generate_fireball_frames(),
        "Frost Nova": generate_frost_nova_frames(),
        "Heal": generate_heal_frames(),
        "Dash": generate_dash_frames(),
        "Shadow Step": generate_shadow_step_frames(),
        "Whirlwind": generate_whirlwind_frames(),
    }

    # Add aliases for different ability name variations
    ability_frames["Healing Touch"] = ability_frames["Heal"]  # With space (actual ability name)
    ability_frames["HealingTouch"] = ability_frames["Heal"]  # Without space (fallback)

    return ability_frames
