"""
Visual effects for ability icons (swirls, vortexes, energy fields).

This module provides functions to generate dynamic magical effects
that can be animated across multiple frames.
"""
import math
import random
from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFilter
from ability_icons.generator import (
    create_radial_gradient, draw_spiral, draw_glow,
    create_particle_field, blend_colors, ease_in_out
)


def create_energy_vortex(size: int, frame: int, total_frames: int,
                        primary_color: tuple, secondary_color: tuple,
                        num_spirals: int = 3, clockwise: bool = True) -> Image.Image:
    """Generate animated energy vortex with multiple spirals.

    Args:
        size: Image size (square)
        frame: Current animation frame (0 to total_frames-1)
        total_frames: Total number of animation frames
        primary_color: Main spiral color (R, G, B)
        secondary_color: Secondary glow color (R, G, B)
        num_spirals: Number of spiral arms
        clockwise: Rotation direction

    Returns:
        PIL Image with energy vortex
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Calculate rotation based on frame
    rotation_per_frame = 360.0 / total_frames
    base_rotation = frame * rotation_per_frame
    if not clockwise:
        base_rotation = -base_rotation

    # Draw background glow
    glow_radius = size * 0.4
    draw_glow(draw, center, glow_radius, secondary_color, intensity=0.4)

    # Draw multiple spiral arms
    for i in range(num_spirals):
        spiral_offset = (360.0 / num_spirals) * i + base_rotation

        # Gradient color along spiral
        for j in range(3):  # Multiple layers for depth
            layer_offset = j * 10
            t = j / 3
            spiral_color = blend_colors(primary_color, secondary_color, t)

            # Make spirals glow (add alpha)
            alpha = int(200 - j * 40)
            spiral_color_alpha = spiral_color + (alpha,)

            draw_spiral(
                draw, center,
                start_radius=size * 0.05 + layer_offset,
                end_radius=size * 0.45 + layer_offset,
                turns=2.5,
                segments=50,
                color=spiral_color_alpha,
                width=6 - j,
                rotation_offset=spiral_offset
            )

    # Add center glow
    center_radius = size * 0.08
    draw_glow(draw, center, center_radius, primary_color, intensity=0.8)

    # Slight blur for soft glow
    image = image.filter(ImageFilter.GaussianBlur(2))

    return image


def create_swirling_particles(size: int, frame: int, total_frames: int,
                              color: tuple, num_particles: int = 30,
                              orbit_radius: float = 0.3) -> Image.Image:
    """Generate particles orbiting in circular paths.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        color: Particle color (R, G, B)
        num_particles: Number of orbiting particles
        orbit_radius: Orbit radius as fraction of image size (0-1)

    Returns:
        PIL Image with orbiting particles
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Animation progress
    t = frame / total_frames

    for i in range(num_particles):
        # Each particle has different orbit parameters
        particle_angle_offset = (360.0 / num_particles) * i
        particle_angle = particle_angle_offset + t * 360

        # Vary orbit radius slightly
        radius_variation = math.sin(math.radians(particle_angle * 2)) * 0.1
        radius = size * orbit_radius * (1.0 + radius_variation)

        # Calculate position
        angle_rad = math.radians(particle_angle)
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        # Particle size varies with position (depth effect)
        depth_factor = 0.5 + 0.5 * math.sin(angle_rad)
        particle_size = 3 + 4 * depth_factor

        # Color brightness varies with depth
        brightness = 0.6 + 0.4 * depth_factor
        particle_color = tuple(int(c * brightness) for c in color)
        alpha = int(200 * brightness)

        # Draw particle
        draw.ellipse([x - particle_size, y - particle_size,
                      x + particle_size, y + particle_size],
                     fill=particle_color + (alpha,))

    # Blur for glow
    image = image.filter(ImageFilter.GaussianBlur(2))

    return image


def create_energy_burst(size: int, frame: int, total_frames: int,
                       color: tuple, num_rays: int = 12) -> Image.Image:
    """Generate pulsing energy burst with radiating rays.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        color: Ray color (R, G, B)
        num_rays: Number of radiating rays

    Returns:
        PIL Image with energy burst
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Pulse effect (sine wave)
    t = frame / total_frames
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi)

    # Draw rays
    for i in range(num_rays):
        angle = (360.0 / num_rays) * i
        angle_rad = math.radians(angle)

        # Ray length pulses
        ray_length = size * 0.4 * (0.6 + 0.4 * pulse)

        # Ray end position
        end_x = center[0] + ray_length * math.cos(angle_rad)
        end_y = center[1] + ray_length * math.sin(angle_rad)

        # Draw ray as triangle
        ray_width = 8
        perp_angle = angle_rad + math.pi / 2

        # Triangle points
        p1 = center
        p2 = (end_x + ray_width * math.cos(perp_angle),
              end_y + ray_width * math.sin(perp_angle))
        p3 = (end_x - ray_width * math.cos(perp_angle),
              end_y - ray_width * math.sin(perp_angle))

        # Gradient color (brighter at center)
        alpha = int(150 + 100 * pulse)
        ray_color = color + (alpha,)

        draw.polygon([p1, p2, p3], fill=ray_color)

    # Center glow
    glow_radius = size * 0.15 * (0.8 + 0.2 * pulse)
    draw_glow(draw, center, glow_radius, color, intensity=0.8 + 0.2 * pulse)

    # Blur for smooth glow
    image = image.filter(ImageFilter.GaussianBlur(3))

    return image


def create_smoke_tendrils(size: int, frame: int, total_frames: int,
                          color: tuple, num_tendrils: int = 5) -> Image.Image:
    """Generate wispy smoke/shadow tendrils.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        color: Smoke color (R, G, B)
        num_tendrils: Number of smoke trails

    Returns:
        PIL Image with smoke tendrils
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Animation progress
    t = frame / total_frames

    for i in range(num_tendrils):
        # Each tendril has different parameters
        tendril_offset = (360.0 / num_tendrils) * i + t * 30  # Slow drift

        # Wavy path
        coords = []
        for step in range(20):
            progress = step / 20.0
            angle = math.radians(tendril_offset + progress * 60)  # Slight curve
            radius = size * 0.1 + progress * size * 0.3

            # Sine wave wobble
            wobble = math.sin(progress * math.pi * 3 + t * math.pi * 2) * size * 0.05

            x = center[0] + radius * math.cos(angle) + wobble * math.sin(angle)
            y = center[1] + radius * math.sin(angle) - wobble * math.cos(angle)

            coords.append((x, y))

        # Draw tendril as thick line
        for j in range(len(coords) - 1):
            # Fade out toward end
            alpha = int(150 * (1.0 - j / len(coords)))
            tendril_color = color + (alpha,)

            # Width decreases toward end
            width = int(8 * (1.0 - j / len(coords) * 0.5))

            draw.line([coords[j], coords[j + 1]], fill=tendril_color, width=width)

    # Heavy blur for smoke effect
    image = image.filter(ImageFilter.GaussianBlur(5))

    return image


def create_ice_crystals(size: int, frame: int, total_frames: int,
                       color: tuple, num_crystals: int = 20) -> Image.Image:
    """Generate crystalline ice shards radiating outward.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        color: Crystal color (R, G, B)
        num_crystals: Number of ice shards

    Returns:
        PIL Image with ice crystals
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Animation: crystals grow outward
    t = frame / total_frames
    growth = ease_in_out(t)

    for i in range(num_crystals):
        # Random angle for each crystal
        angle = (360.0 / num_crystals) * i + random.uniform(-10, 10)
        angle_rad = math.radians(angle)

        # Crystal extends from center
        start_radius = size * 0.1
        end_radius = size * 0.4 * growth

        start_x = center[0] + start_radius * math.cos(angle_rad)
        start_y = center[1] + start_radius * math.sin(angle_rad)
        end_x = center[0] + end_radius * math.cos(angle_rad)
        end_y = center[1] + end_radius * math.sin(angle_rad)

        # Draw crystal as diamond shape
        crystal_width = 4
        perp_angle = angle_rad + math.pi / 2

        # Four points of diamond
        p1 = (start_x, start_y)  # Base
        p2 = (end_x + crystal_width * math.cos(perp_angle),
              end_y + crystal_width * math.sin(perp_angle))
        p3 = (end_x + end_radius * 0.1 * math.cos(angle_rad),  # Tip
              end_y + end_radius * 0.1 * math.sin(angle_rad))
        p4 = (end_x - crystal_width * math.cos(perp_angle),
              end_y - crystal_width * math.sin(perp_angle))

        # Bright crystal color
        alpha = 220
        crystal_color = tuple(min(255, int(c * 1.2)) for c in color) + (alpha,)

        draw.polygon([p1, p2, p3, p4], fill=crystal_color)

    # Slight blur for icy glow
    image = image.filter(ImageFilter.GaussianBlur(1))

    return image


def create_speed_streaks(size: int, frame: int, total_frames: int,
                        color: tuple, direction: float = 45) -> Image.Image:
    """Generate motion blur speed lines.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        color: Streak color (R, G, B)
        direction: Streak angle in degrees (0 = right)

    Returns:
        PIL Image with speed streaks
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Animation: streaks slide across
    t = frame / total_frames
    offset = t * size * 0.3

    angle_rad = math.radians(direction)

    # Draw multiple streaks
    for i in range(15):
        # Stagger streaks
        streak_offset = (i / 15.0) * size - size * 0.5 + offset

        # Start and end positions
        start_x = center[0] - size * 0.4 * math.cos(angle_rad) + streak_offset * math.sin(angle_rad)
        start_y = center[1] - size * 0.4 * math.sin(angle_rad) - streak_offset * math.cos(angle_rad)
        end_x = center[0] + size * 0.4 * math.cos(angle_rad) + streak_offset * math.sin(angle_rad)
        end_y = center[1] + size * 0.4 * math.sin(angle_rad) - streak_offset * math.cos(angle_rad)

        # Fade out at edges
        edge_dist = abs(streak_offset) / (size * 0.3)
        alpha = int(150 * max(0, 1.0 - edge_dist))

        streak_color = color + (alpha,)
        width = random.randint(2, 5)

        draw.line([(start_x, start_y), (end_x, end_y)], fill=streak_color, width=width)

    # Motion blur
    image = image.filter(ImageFilter.GaussianBlur(2))

    return image


def create_fire_embers(size: int, frame: int, total_frames: int,
                      primary_color: tuple, secondary_color: tuple,
                      num_embers: int = 40) -> Image.Image:
    """Generate rising fire embers/sparks.

    Args:
        size: Image size (square)
        frame: Current animation frame
        total_frames: Total number of animation frames
        primary_color: Hot ember color (R, G, B) - e.g., orange
        secondary_color: Cooler ember color (R, G, B) - e.g., red
        num_embers: Number of floating embers

    Returns:
        PIL Image with fire embers
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size // 2, size // 2)

    # Animation progress
    t = frame / total_frames

    for i in range(num_embers):
        # Each ember has unique rise pattern
        ember_seed = i / num_embers
        rise_speed = 0.5 + ember_seed * 0.5

        # Vertical position (rises over time)
        y_progress = (ember_seed + t * rise_speed) % 1.0
        y = size * (1.0 - y_progress)

        # Horizontal position (slight drift)
        drift = math.sin((ember_seed + t) * math.pi * 2) * size * 0.1
        x = center[0] + drift

        # Ember size
        ember_size = 2 + random.uniform(1, 4)

        # Color transitions from hot to cool as it rises
        ember_color = blend_colors(primary_color, secondary_color, y_progress)

        # Fade out as it rises
        alpha = int(255 * (1.0 - y_progress))

        # Draw ember
        draw.ellipse([x - ember_size, y - ember_size,
                      x + ember_size, y + ember_size],
                     fill=ember_color + (alpha,))

    # Slight glow
    image = image.filter(ImageFilter.GaussianBlur(1))

    return image
