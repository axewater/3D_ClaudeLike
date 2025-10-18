"""
Dungeon generation for Claude-Like
"""
import random
from typing import List, Tuple
import constants as c


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
        return self.tiles[y][x] != c.TILE_WALL

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
