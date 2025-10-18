"""
Field of View calculation using recursive shadowcasting algorithm
"""
from typing import Set, Tuple
from dungeon import Dungeon


def calculate_fov(dungeon: Dungeon, origin_x: int, origin_y: int, radius: int) -> Set[Tuple[int, int]]:
    """
    Calculate field of view from origin point using shadowcasting algorithm.
    Returns set of (x, y) tuples for all visible tiles.

    Args:
        dungeon: Dungeon map to check for walls
        origin_x: X coordinate of viewpoint
        origin_y: Y coordinate of viewpoint
        radius: Maximum vision distance (Manhattan distance)

    Returns:
        Set of (x, y) coordinates that are visible
    """
    visible = {(origin_x, origin_y)}  # Origin is always visible

    # Cast shadows in all 8 octants
    for octant in range(8):
        cast_light(dungeon, origin_x, origin_y, 1, 1.0, 0.0, radius, octant, visible)

    return visible


def cast_light(dungeon: Dungeon, cx: int, cy: int, row: int,
               start_slope: float, end_slope: float, radius: int,
               octant: int, visible: Set[Tuple[int, int]]):
    """
    Recursive shadowcasting for a single octant.

    Args:
        dungeon: Dungeon map
        cx, cy: Center point (origin of vision)
        row: Current row being scanned (distance from origin)
        start_slope: Starting slope of visible area
        end_slope: Ending slope of visible area
        radius: Maximum vision radius
        octant: Which octant (0-7) we're scanning
        visible: Set to add visible tiles to
    """
    if start_slope < end_slope:
        return

    next_start_slope = start_slope

    for i in range(row, radius + 1):
        blocked = False

        for dx in range(-i, i + 1):
            dy = -i

            # Apply octant transform
            x, y = transform_octant(cx, cy, dx, dy, octant)

            # Check if tile is in bounds
            if not (0 <= x < dungeon.width and 0 <= y < dungeon.height):
                continue

            # Calculate slopes
            left_slope = (dx - 0.5) / (dy + 0.5) if dy + 0.5 != 0 else 0
            right_slope = (dx + 0.5) / (dy - 0.5) if dy - 0.5 != 0 else 0

            # Skip if outside current cone
            if start_slope < right_slope:
                continue
            elif end_slope > left_slope:
                break

            # Check Manhattan distance (diamond shape)
            if abs(dx) + abs(dy) <= radius:
                visible.add((x, y))

            # Check if tile blocks vision
            is_wall = not dungeon.is_walkable(x, y)

            if blocked:
                # We're scanning through a shadow
                if is_wall:
                    next_start_slope = right_slope
                    continue
                else:
                    blocked = False
                    start_slope = next_start_slope
            else:
                # Not in shadow
                if is_wall and i < radius:
                    # This tile starts a shadow
                    blocked = True
                    next_start_slope = right_slope

                    # Recursively scan the narrow cone before this obstacle
                    cast_light(dungeon, cx, cy, i + 1, start_slope, left_slope,
                             radius, octant, visible)

        if blocked:
            break


def transform_octant(cx: int, cy: int, dx: int, dy: int, octant: int) -> Tuple[int, int]:
    """
    Transform coordinates from octant 0 coordinate system to actual coordinates.

    Octants:
      \\2|1/
      3\\|/0
      --+--
      4/|\\7
      /5|6\\

    Args:
        cx, cy: Center coordinates
        dx, dy: Offset in octant coordinate system
        octant: Which octant (0-7)

    Returns:
        Actual (x, y) coordinates
    """
    if octant == 0:
        return (cx + dx, cy - dy)
    elif octant == 1:
        return (cx + dy, cy - dx)
    elif octant == 2:
        return (cx - dy, cy - dx)
    elif octant == 3:
        return (cx - dx, cy - dy)
    elif octant == 4:
        return (cx - dx, cy + dy)
    elif octant == 5:
        return (cx - dy, cy + dx)
    elif octant == 6:
        return (cx + dy, cy + dx)
    elif octant == 7:
        return (cx + dx, cy + dy)

    return (cx, cy)
