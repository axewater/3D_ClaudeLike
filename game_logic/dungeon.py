"""
Dungeon generation for Claude-Like
"""
import random
from typing import List, Tuple, Optional
from core import constants as c


class Room:
    """Rectangular room"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self) -> Tuple[int, int]:
        """Get room center coordinates"""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: 'Room') -> bool:
        """Check if this room intersects with another"""
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)

    def get_random_point(self) -> Tuple[int, int]:
        """Get random point inside room"""
        return (
            random.randint(self.x + 1, self.x + self.width - 2),
            random.randint(self.y + 1, self.y + self.height - 2)
        )


class Dungeon:
    """Dungeon map"""
    def __init__(self, width: int, height: int, biome: str = c.BIOME_DUNGEON):
        self.width = width
        self.height = height
        self.biome = biome
        self.tiles = [[c.TILE_WALL for _ in range(width)] for _ in range(height)]
        self.rooms: List[Room] = []
        self.secret_wall_pos: Optional[Tuple[int, int]] = None
        self.secret_room: Optional[Room] = None

    def generate(self) -> Tuple[int, int]:
        """Generate dungeon and return starting position"""
        self.rooms = []

        # Try to place rooms
        for _ in range(c.MAX_ROOMS):
            w = random.randint(c.MIN_ROOM_SIZE, c.MAX_ROOM_SIZE)
            h = random.randint(c.MIN_ROOM_SIZE, c.MAX_ROOM_SIZE)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Room(x, y, w, h)

            # Check for intersection
            if not any(new_room.intersects(room) for room in self.rooms):
                self._carve_room(new_room)

                # Connect to previous room with corridor
                if self.rooms:
                    prev_center = self.rooms[-1].center()
                    new_center = new_room.center()

                    if random.random() < 0.5:
                        # Horizontal then vertical
                        self._carve_h_corridor(prev_center[0], new_center[0], prev_center[1])
                        self._carve_v_corridor(prev_center[1], new_center[1], new_center[0])
                    else:
                        # Vertical then horizontal
                        self._carve_v_corridor(prev_center[1], new_center[1], prev_center[0])
                        self._carve_h_corridor(prev_center[0], new_center[0], new_center[1])

                self.rooms.append(new_room)

        # Place stairs in last room
        if self.rooms:
            stairs_x, stairs_y = self.rooms[-1].center()
            self.tiles[stairs_y][stairs_x] = c.TILE_STAIRS

        # Place secret room (exactly 1 per level)
        self.place_secret_room()

        # Return starting position (center of first room)
        if self.rooms:
            return self.rooms[0].center()
        return (self.width // 2, self.height // 2)

    def _carve_room(self, room: Room):
        """Carve out a room"""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[y][x] = c.TILE_FLOOR

    def _carve_h_corridor(self, x1: int, x2: int, y: int):
        """Carve horizontal corridor"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = c.TILE_FLOOR

    def _carve_v_corridor(self, y1: int, y2: int, x: int):
        """Carve vertical corridor"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = c.TILE_FLOOR

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if tile is walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        tile = self.tiles[y][x]
        # Walls and secret walls block movement (until secret wall is broken)
        return tile not in [c.TILE_WALL, c.TILE_SECRET_WALL]

    def get_tile(self, x: int, y: int) -> int:
        """Get tile type at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return c.TILE_WALL

    def get_random_floor_position(self, avoid_stairs: bool = True) -> Tuple[int, int]:
        """Get random floor position"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if self.tiles[y][x] == c.TILE_FLOOR:
                return (x, y)
            elif not avoid_stairs and self.tiles[y][x] == c.TILE_STAIRS:
                return (x, y)

            attempts += 1

        # Fallback to center of first room
        if self.rooms:
            return self.rooms[0].center()
        return (self.width // 2, self.height // 2)

    def get_room_at(self, x: int, y: int) -> 'Room':
        """
        Get the room that contains the given position.
        Returns the Room object or None if not in any room.
        """
        for room in self.rooms:
            if (room.x <= x < room.x + room.width and
                room.y <= y < room.y + room.height):
                return room
        return None

    def is_secret_room(self, x: int, y: int) -> bool:
        """Check if position is inside the secret room"""
        if not self.secret_room:
            return False
        return (self.secret_room.x <= x < self.secret_room.x + self.secret_room.width and
                self.secret_room.y <= y < self.secret_room.y + self.secret_room.height)

    def place_secret_room(self):
        """
        Place exactly one secret room with a secret wall entrance.

        Algorithm:
        1. Find valid exterior walls (adjacent to floor, not near stairs/start)
        2. Check if 5x5 or 6x6 space available on opposite side
        3. Carve room
        4. 50% chance: carve 1-2 tile tunnel
        5. Mark entrance wall as TILE_SECRET_WALL
        """
        if len(self.rooms) < 2:
            return  # Need at least 2 rooms for valid placement

        # Get stairs position (avoid placing secret near it)
        stairs_pos = None
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == c.TILE_STAIRS:
                    stairs_pos = (x, y)
                    break
            if stairs_pos:
                break

        # Get starting room (avoid placing secret in first room)
        start_room = self.rooms[0] if self.rooms else None

        # Find candidate walls
        candidates = []

        # Check rooms 2 onwards (skip first room)
        for room_idx in range(1, len(self.rooms)):
            room = self.rooms[room_idx]

            # Check all four walls of the room
            directions = [
                ('north', 0, -1),  # Wall to north, room extends south
                ('south', 0, 1),   # Wall to south, room extends north
                ('west', -1, 0),   # Wall to west, room extends east
                ('east', 1, 0),    # Wall to east, room extends west
            ]

            for wall_name, dx, dy in directions:
                # Get wall tiles
                wall_tiles = []

                if wall_name == 'north':
                    # North wall (top edge)
                    for x in range(room.x, room.x + room.width):
                        wall_tiles.append((x, room.y - 1))
                elif wall_name == 'south':
                    # South wall (bottom edge)
                    for x in range(room.x, room.x + room.width):
                        wall_tiles.append((x, room.y + room.height))
                elif wall_name == 'west':
                    # West wall (left edge)
                    for y in range(room.y, room.y + room.height):
                        wall_tiles.append((room.x - 1, y))
                elif wall_name == 'east':
                    # East wall (right edge)
                    for y in range(room.y, room.y + room.height):
                        wall_tiles.append((room.x + room.width, y))

                # Check each wall tile
                for wx, wy in wall_tiles:
                    # Must be in bounds
                    if not (0 <= wx < self.width and 0 <= wy < self.height):
                        continue

                    # Must be a wall
                    if self.tiles[wy][wx] != c.TILE_WALL:
                        continue

                    # Must be adjacent to floor (room side)
                    room_side_x = wx - dx
                    room_side_y = wy - dy
                    if not (0 <= room_side_x < self.width and 0 <= room_side_y < self.height):
                        continue
                    if self.tiles[room_side_y][room_side_x] != c.TILE_FLOOR:
                        continue

                    # Avoid near stairs
                    if stairs_pos:
                        dist_to_stairs = abs(wx - stairs_pos[0]) + abs(wy - stairs_pos[1])
                        if dist_to_stairs < 5:
                            continue

                    # Check if there's space on opposite side for 5x5 or 6x6 room
                    secret_room_size = random.randint(5, 6)

                    # Calculate room position based on direction
                    if wall_name == 'north':
                        # Room extends upward
                        room_x = wx - secret_room_size // 2
                        room_y = wy - secret_room_size
                    elif wall_name == 'south':
                        # Room extends downward
                        room_x = wx - secret_room_size // 2
                        room_y = wy + 1
                    elif wall_name == 'west':
                        # Room extends left
                        room_x = wx - secret_room_size
                        room_y = wy - secret_room_size // 2
                    elif wall_name == 'east':
                        # Room extends right
                        room_x = wx + 1
                        room_y = wy - secret_room_size // 2

                    # Check if room area is valid (all walls, no overlap)
                    proposed_room = Room(room_x, room_y, secret_room_size, secret_room_size)

                    # Must be in bounds
                    if not (0 < room_x < self.width - secret_room_size and
                            0 < room_y < self.height - secret_room_size):
                        continue

                    # Check all tiles in proposed room area are walls
                    valid = True
                    for check_y in range(room_y - 1, room_y + secret_room_size + 1):
                        for check_x in range(room_x - 1, room_x + secret_room_size + 1):
                            if not (0 <= check_x < self.width and 0 <= check_y < self.height):
                                valid = False
                                break
                            # Allow the entrance wall to be the secret wall
                            if check_x == wx and check_y == wy:
                                continue
                            # Interior should be wall, exterior can be anything
                            if (room_x <= check_x < room_x + secret_room_size and
                                room_y <= check_y < room_y + secret_room_size):
                                if self.tiles[check_y][check_x] != c.TILE_WALL:
                                    valid = False
                                    break
                        if not valid:
                            break

                    if not valid:
                        continue

                    # Valid candidate!
                    candidates.append({
                        'wall_pos': (wx, wy),
                        'room': proposed_room,
                        'direction': wall_name,
                        'dx': dx,
                        'dy': dy
                    })

        # No valid candidates
        if not candidates:
            return

        # Pick random candidate
        chosen = random.choice(candidates)

        # Carve secret room
        self._carve_room(chosen['room'])
        self.secret_room = chosen['room']

        # Maybe add tunnel (50% chance, 1-2 tiles)
        if random.random() < 0.5:
            tunnel_length = random.randint(1, 2)
            tunnel_x, tunnel_y = chosen['wall_pos']

            for i in range(1, tunnel_length + 1):
                tx = tunnel_x + chosen['dx'] * i
                ty = tunnel_y + chosen['dy'] * i

                if 0 <= tx < self.width and 0 <= ty < self.height:
                    # Only carve if it's a wall (don't carve into secret room)
                    if self.tiles[ty][tx] == c.TILE_WALL:
                        self.tiles[ty][tx] = c.TILE_FLOOR

        # Mark entrance as secret wall
        wx, wy = chosen['wall_pos']
        self.tiles[wy][wx] = c.TILE_SECRET_WALL
        self.secret_wall_pos = (wx, wy)
