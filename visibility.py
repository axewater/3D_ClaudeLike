"""
Visibility state management for fog of war
"""
from typing import Set, Tuple
import constants as c


class VisibilityMap:
    """
    Tracks visibility state of all tiles in the dungeon.

    Three states:
    - UNEXPLORED: Player has never seen this tile
    - EXPLORED: Player has seen this tile but can't see it now
    - VISIBLE: Player can currently see this tile
    """

    def __init__(self, width: int, height: int):
        """
        Initialize visibility map.

        Args:
            width: Map width in tiles
            height: Map height in tiles
        """
        self.width = width
        self.height = height

        # Initialize all tiles as unexplored
        self.tiles = [[c.VISIBILITY_UNEXPLORED for _ in range(width)]
                      for _ in range(height)]

    def update_visibility(self, visible_tiles: Set[Tuple[int, int]]):
        """
        Update visibility map with new visible tiles.

        - Previous VISIBLE tiles become EXPLORED
        - New visible tiles become VISIBLE
        - UNEXPLORED tiles that become visible become VISIBLE

        Args:
            visible_tiles: Set of (x, y) coordinates currently visible
        """
        # First pass: downgrade all VISIBLE tiles to EXPLORED
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == c.VISIBILITY_VISIBLE:
                    self.tiles[y][x] = c.VISIBILITY_EXPLORED

        # Second pass: mark new visible tiles as VISIBLE
        for x, y in visible_tiles:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = c.VISIBILITY_VISIBLE

    def get_state(self, x: int, y: int) -> str:
        """
        Get visibility state of a tile.

        Args:
            x, y: Tile coordinates

        Returns:
            Visibility state constant (UNEXPLORED, EXPLORED, or VISIBLE)
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return c.VISIBILITY_UNEXPLORED

        return self.tiles[y][x]

    def is_visible(self, x: int, y: int) -> bool:
        """
        Quick check if tile is currently visible.

        Args:
            x, y: Tile coordinates

        Returns:
            True if tile is visible, False otherwise
        """
        return self.get_state(x, y) == c.VISIBILITY_VISIBLE

    def is_explored(self, x: int, y: int) -> bool:
        """
        Check if tile has ever been seen (explored or visible).

        Args:
            x, y: Tile coordinates

        Returns:
            True if tile is explored or visible, False if unexplored
        """
        state = self.get_state(x, y)
        return state in [c.VISIBILITY_EXPLORED, c.VISIBILITY_VISIBLE]

    def reveal_all(self):
        """
        Reveal entire map (for debugging/testing).
        Sets all tiles to VISIBLE.
        """
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = c.VISIBILITY_VISIBLE

    def reset(self):
        """
        Reset all tiles to unexplored state.
        Used when descending to a new dungeon level.
        """
        self.tiles = [[c.VISIBILITY_UNEXPLORED for _ in range(self.width)]
                      for _ in range(self.height)]

    def count_explored(self) -> int:
        """
        Count number of explored or visible tiles.

        Returns:
            Number of tiles that have been seen
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] in [c.VISIBILITY_EXPLORED, c.VISIBILITY_VISIBLE]:
                    count += 1
        return count

    def count_visible(self) -> int:
        """
        Count number of currently visible tiles.

        Returns:
            Number of tiles that are visible right now
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == c.VISIBILITY_VISIBLE:
                    count += 1
        return count
