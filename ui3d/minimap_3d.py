"""
Minimap 3D Widget

Displays a top-down minimap of the dungeon showing:
- Explored/visible areas
- Player position and orientation
- Enemies (in visible areas)
- Items (in visible areas)
- Stairs
"""

from typing import Optional
from ursina import Entity, Vec2, Vec3, Texture, color
from PIL import Image, ImageDraw
from core import constants as c
from game_logic.game import Game
import math


class MiniMap3D:
    """
    3D Minimap widget that renders dungeon layout as a top-down texture

    Features:
    - Shows explored vs visible areas
    - Indicates player position with directional arrow
    - Shows enemies/items in visible areas
    - Supports full map and radar modes
    """

    # Color definitions (RGB 0-255)
    COLOR_UNEXPLORED = (0, 0, 0, 0)  # Transparent
    COLOR_EXPLORED_WALL = (48, 48, 53)  # Dark gray
    COLOR_EXPLORED_FLOOR = (45, 45, 48)  # Slightly lighter gray
    COLOR_VISIBLE_WALL = (96, 96, 101)  # Medium gray
    COLOR_VISIBLE_FLOOR = (80, 80, 83)  # Light gray
    COLOR_PLAYER = (100, 255, 255)  # Bright cyan
    COLOR_ENEMY = (255, 80, 80)  # Red
    COLOR_ITEM = (255, 220, 80)  # Yellow/gold
    COLOR_STAIRS = (180, 120, 255)  # Purple

    def __init__(self, game: Game, parent: Optional[Entity] = None, mode: str = "full"):
        """
        Initialize minimap

        Args:
            game: Game instance
            parent: Parent entity (camera.ui)
            mode: "full" for entire dungeon, "radar" for nearby area
        """
        self.game = game
        self.parent = parent
        self.mode = mode  # "full" or "radar"

        # Minimap size and position
        if mode == "full":
            self.map_width, self.map_height = c.MINIMAP_SIZE_FULL
        else:
            self.map_width, self.map_height = c.MINIMAP_SIZE_RADAR

        # Pixel scale (how many pixels per dungeon tile)
        self.pixel_scale = c.MINIMAP_PIXEL_SCALE

        # Calculate texture size (in pixels)
        self.texture_width = c.GRID_WIDTH * self.pixel_scale
        self.texture_height = c.GRID_HEIGHT * self.pixel_scale

        # UI elements
        self.background_panel: Optional[Entity] = None
        self.border_panel: Optional[Entity] = None
        self.map_entity: Optional[Entity] = None

        # Texture for minimap rendering
        self.texture: Optional[Texture] = None
        self.texture_needs_update = True

        # Cached state to detect changes
        self._last_player_x = -1
        self._last_player_y = -1
        self._last_camera_yaw = -1.0
        self._last_visibility_hash = None

        # Create UI
        self._create_ui()

        print(f"✓ MiniMap3D initialized ({mode} mode, {self.map_width}x{self.map_height})")

    def _create_ui(self):
        """Create minimap UI elements"""
        # Calculate position based on settings
        if c.MINIMAP_POSITION == "top_right":
            pos_x = 0.70 - (self.map_width * 0.001)  # Adjust for minimap size
            pos_y = 0.30
        else:  # bottom_right
            pos_x = 0.50  # Positioned right of center, adjusted for larger size
            pos_y = -0.25  # Higher position, above quick stats, adjusted for larger size

        # Calculate panel size in normalized screen coords
        panel_width = self.map_width * 0.001 + 0.04  # Add padding
        panel_height = self.map_height * 0.001 + 0.04  # Add padding

        # Background panel
        self.background_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(0.02, 0.02, 0.15, c.MINIMAP_OPACITY),
            position=(pos_x, pos_y, 10),  # Far back
            scale=(panel_width, panel_height),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Border panel
        border_color = c.MINIMAP_BORDER_COLOR
        self.border_panel = Entity(
            parent=self.parent,
            model='quad',
            color=color.rgba(*border_color),
            position=(pos_x + 0.002, pos_y - 0.002, 9),  # In front of background
            scale=(panel_width - 0.01, panel_height - 0.01),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Map entity (holds the texture) - centered in panel without title
        map_scale_x = panel_width - 0.04  # Slightly smaller than panel
        map_scale_y = (panel_height - 0.04) * 0.90  # Centered vertically with padding

        self.map_entity = Entity(
            parent=self.parent,
            model='quad',
            position=(pos_x + 0.01, pos_y - 0.02, -5),  # Centered in panel
            scale=(map_scale_x, map_scale_y),
            origin=(-0.5, 0.5),
            eternal=True
        )

        # Initialize texture
        self._create_initial_texture()

    def _create_initial_texture(self):
        """Create initial blank texture"""
        # Create PIL image
        img = Image.new('RGBA', (self.texture_width, self.texture_height), self.COLOR_UNEXPLORED)

        # Convert to Ursina texture
        self.texture = Texture(img)
        self.map_entity.texture = self.texture

    def _generate_minimap_texture(self):
        """Generate minimap texture from current game state"""
        if not self.game.dungeon or not self.game.visibility_map:
            return

        # Create PIL image
        img = Image.new('RGBA', (self.texture_width, self.texture_height), self.COLOR_UNEXPLORED)
        draw = ImageDraw.Draw(img)

        # Get dungeon and visibility data
        dungeon = self.game.dungeon
        vis_map = self.game.visibility_map

        # Determine render area based on mode
        if self.mode == "radar" and self.game.player:
            # Radar mode: only render nearby area
            center_x = self.game.player.x
            center_y = self.game.player.y
            radius = c.MINIMAP_RADAR_RANGE

            min_x = max(0, center_x - radius)
            max_x = min(c.GRID_WIDTH, center_x + radius)
            min_y = max(0, center_y - radius)
            max_y = min(c.GRID_HEIGHT, center_y + radius)
        else:
            # Full mode: render entire dungeon
            min_x, min_y = 0, 0
            max_x, max_y = c.GRID_WIDTH, c.GRID_HEIGHT

        # Render tiles
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                vis_state = vis_map.get_state(x, y)

                # Skip unexplored tiles
                if vis_state == c.VISIBILITY_UNEXPLORED:
                    continue

                # Get tile type
                tile = dungeon.get_tile(x, y)

                # Determine color based on visibility and tile type
                if vis_state == c.VISIBILITY_VISIBLE:
                    if tile == c.TILE_WALL:
                        tile_color = self.COLOR_VISIBLE_WALL
                    elif tile == c.TILE_STAIRS:
                        tile_color = self.COLOR_STAIRS
                    else:  # FLOOR
                        tile_color = self.COLOR_VISIBLE_FLOOR
                else:  # EXPLORED
                    if tile == c.TILE_WALL:
                        tile_color = self.COLOR_EXPLORED_WALL
                    else:  # FLOOR or STAIRS (both look like floor when explored)
                        tile_color = self.COLOR_EXPLORED_FLOOR

                # Draw tile as rectangle (scaled by pixel_scale)
                # Flip Y coordinate to match game coordinate system
                px = x * self.pixel_scale
                py = (c.GRID_HEIGHT - 1 - y) * self.pixel_scale
                draw.rectangle(
                    [px, py, px + self.pixel_scale - 1, py + self.pixel_scale - 1],
                    fill=tile_color
                )

        # Draw items (only in visible areas)
        for item in self.game.items:
            if vis_map.is_visible(item.x, item.y):
                px = item.x * self.pixel_scale
                py = (c.GRID_HEIGHT - 1 - item.y) * self.pixel_scale
                # Draw as small dot
                draw.ellipse(
                    [px, py, px + self.pixel_scale - 1, py + self.pixel_scale - 1],
                    fill=self.COLOR_ITEM
                )

        # Draw enemies (only in visible areas)
        for enemy in self.game.enemies:
            if vis_map.is_visible(enemy.x, enemy.y):
                px = enemy.x * self.pixel_scale
                py = (c.GRID_HEIGHT - 1 - enemy.y) * self.pixel_scale
                # Draw as small dot
                draw.ellipse(
                    [px, py, px + self.pixel_scale - 1, py + self.pixel_scale - 1],
                    fill=self.COLOR_ENEMY
                )

        # Draw player with directional arrow
        if self.game.player:
            self._draw_player_arrow(draw, self.game.player.x, self.game.player.y)

        # Update texture
        self.texture = Texture(img)
        self.map_entity.texture = self.texture

    def _draw_player_arrow(self, draw: ImageDraw.ImageDraw, px: int, py: int):
        """
        Draw player as directional arrow showing camera orientation

        Args:
            draw: PIL ImageDraw object
            px: Player grid X
            py: Player grid Y (in game coordinates, will be flipped for image)
        """
        # Get camera yaw from game controller (via renderer)
        # We'll estimate it from cached value or default to 0
        yaw = self._last_camera_yaw if self._last_camera_yaw >= 0 else 0

        # Convert yaw to radians (0° = North = -Y)
        angle_rad = math.radians(yaw)

        # Calculate arrow points (flip Y coordinate for image space)
        center_x = px * self.pixel_scale + self.pixel_scale / 2
        center_y = (c.GRID_HEIGHT - 1 - py) * self.pixel_scale + self.pixel_scale / 2

        # Arrow size
        arrow_length = self.pixel_scale * 1.5
        arrow_width = self.pixel_scale * 0.8

        # Arrow tip (pointing in camera direction)
        # Note: Y is flipped, so we need to invert the Y component
        tip_x = center_x + arrow_length * math.sin(angle_rad)
        tip_y = center_y + arrow_length * math.cos(angle_rad)  # Positive because Y is flipped

        # Arrow base corners (perpendicular to direction)
        perp_angle = angle_rad + math.pi / 2
        base1_x = center_x + arrow_width * math.sin(perp_angle)
        base1_y = center_y + arrow_width * math.cos(perp_angle)
        base2_x = center_x - arrow_width * math.sin(perp_angle)
        base2_y = center_y - arrow_width * math.cos(perp_angle)

        # Draw triangle
        draw.polygon(
            [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)],
            fill=self.COLOR_PLAYER,
            outline=self.COLOR_PLAYER
        )

    def update(self, dt: float, camera_yaw: float = 0.0):
        """
        Update minimap

        Args:
            dt: Delta time
            camera_yaw: Current camera yaw in degrees
        """
        if not c.MINIMAP_ENABLED:
            return

        if not self.game.player or not self.game.dungeon or not self.game.visibility_map:
            return

        # Update cached camera yaw
        self._last_camera_yaw = camera_yaw

        # Check if state changed (to avoid regenerating texture every frame)
        player_moved = (self.game.player.x != self._last_player_x or
                       self.game.player.y != self._last_player_y)
        camera_rotated = abs(camera_yaw - self._last_camera_yaw) > 5  # Threshold for rotation

        # Calculate visibility hash (simple hash of visible tile count)
        vis_hash = self.game.visibility_map.count_visible()
        visibility_changed = vis_hash != self._last_visibility_hash

        # Regenerate texture if state changed
        if player_moved or camera_rotated or visibility_changed or self.texture_needs_update:
            self._generate_minimap_texture()

            # Update cached state
            self._last_player_x = self.game.player.x
            self._last_player_y = self.game.player.y
            self._last_camera_yaw = camera_yaw
            self._last_visibility_hash = vis_hash
            self.texture_needs_update = False

    def cleanup(self):
        """Clean up minimap resources"""
        if self.background_panel:
            self.background_panel.disable()
        if self.border_panel:
            self.border_panel.disable()
        if self.map_entity:
            self.map_entity.disable()

        print("✓ MiniMap3D cleaned up")
