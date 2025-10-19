"""
Mathematical curve generators for organic tentacle shapes.

Two algorithms for generating smooth, organic curves:
1. Bezier Curves - Cubic polynomial curves with control points
2. Fourier Series - Wave composition for complex organic shapes
"""

from ursina import Vec3
import math


def bezier_curve(anchor, target, num_points, control_strength=0.4):
    """
    Generate points along a cubic Bezier curve.

    Bezier curve: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃

    Args:
        anchor: Vec3 start point
        target: Vec3 end point
        num_points: Number of points to generate
        control_strength: How far control points are from endpoints (0-1)

    Returns:
        list of Vec3 points along the curve
    """
    points = []

    # Calculate control points
    # P0 = anchor, P3 = target
    # P1 and P2 are offset along normals for natural curve

    direction = (target - anchor).normalized()
    length = (target - anchor).length()

    # Create perpendicular vectors for control point offsets
    up = Vec3(0, 1, 0)
    if abs(direction.y) > 0.99:
        up = Vec3(1, 0, 0)

    side = direction.cross(up).normalized()

    # Control points offset to the side for natural S-curve
    p0 = anchor
    p1 = anchor + direction * (length * control_strength) + side * (length * 0.2)
    p2 = target - direction * (length * control_strength) - side * (length * 0.2)
    p3 = target

    # Generate points along cubic Bezier
    for i in range(num_points):
        t = i / max(1, num_points - 1)

        # Cubic Bezier formula
        b0 = (1 - t) ** 3
        b1 = 3 * (1 - t) ** 2 * t
        b2 = 3 * (1 - t) * t ** 2
        b3 = t ** 3

        point = p0 * b0 + p1 * b1 + p2 * b2 + p3 * b3
        points.append(point)

    return points


def fourier_curve(anchor, target, num_points, num_waves=3, amplitude=0.1):
    """
    Generate points along a curve defined by Fourier series (wave composition).

    Combines multiple sine waves at different frequencies for organic shapes.
    Formula: P(t) = base_curve(t) + Σ(Aₙ sin(nωt + φₙ))

    Args:
        anchor: Vec3 start point
        target: Vec3 end point
        num_points: Number of points to generate
        num_waves: Number of Fourier components (3-5 recommended)
        amplitude: Wave amplitude as fraction of length

    Returns:
        list of Vec3 points along the curve
    """
    points = []

    direction = (target - anchor).normalized()
    length = (target - anchor).length()

    # Create perpendicular basis vectors
    up = Vec3(0, 1, 0)
    if abs(direction.y) > 0.99:
        up = Vec3(1, 0, 0)

    right = direction.cross(up).normalized()
    up = right.cross(direction).normalized()

    # Generate points with Fourier wave composition
    for i in range(num_points):
        t = i / max(1, num_points - 1)

        # Base position (straight line)
        base = anchor + direction * (t * length)

        # Add Fourier components
        offset_x = 0
        offset_y = 0

        for n in range(1, num_waves + 1):
            # Each wave has different frequency and phase
            freq = n * 2.0
            phase = n * 0.7  # Offset phases for variety

            # Amplitude decreases with frequency (lower frequencies dominate)
            wave_amp = amplitude * length / n

            # Add wave components
            offset_x += wave_amp * math.sin(freq * t * math.pi + phase)
            offset_y += wave_amp * math.cos(freq * t * math.pi + phase * 1.3)

        # Apply offsets in local coordinate system
        point = base + right * offset_x + up * offset_y
        points.append(point)

    return points
