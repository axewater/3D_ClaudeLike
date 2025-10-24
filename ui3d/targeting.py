"""
Targeting System for 3D Abilities

Provides mouse-based targeting with visual feedback for abilities that require targeting.
"""

from typing import Optional, Tuple
from ursina import Entity, Text, color, Vec2, Vec3, mouse, camera, raycast
from game import Game
import constants as c


class TargetingSystem:
    """
    Mouse targeting system for abilities

    Features:
    - Raycast from camera to world grid
    - Range validation
    - Line-of-sight checking
    - Visual feedback (range circle, target cursor)
    """

    # Targeting modes
    MODE_IDLE = 0
    MODE_TARGETING = 1

    def __init__(self, game: Game, parent: Optional[Entity] = None):
        """
        Initialize targeting system

        Args:
            game: Game instance
            parent: Parent entity
        """
        self.game = game
        self.parent = parent

        # State
        self.mode = self.MODE_IDLE
        self.selected_ability_index: Optional[int] = None
        self.selected_ability = None
        self.target_pos: Optional[Tuple[int, int]] = None
        self.is_valid_target = False

        # Visual elements
        self.range_circle: Optional[Entity] = None
        self.target_cursor: Optional[Entity] = None
        self.cursor_outline: Optional[Entity] = None  # Border around cursor
        self.info_text: Optional[Text] = None
        self.error_text: Optional[Text] = None

        # Constants
        self.CURSOR_SIZE = 2.0  # Large for visibility
        self.CURSOR_HEIGHT = 0.8  # Raised significantly above ground
        self.RANGE_CIRCLE_HEIGHT = 0.02

        print("✓ TargetingSystem initialized")

    def start_targeting(self, ability_index: int):
        """
        Enter targeting mode for an ability

        Args:
            ability_index: Index of ability to target (0, 1, or 2)
        """
        if not self.game.player or ability_index >= len(self.game.player.abilities):
            print(f"[TARGETING] Invalid ability index: {ability_index}")
            return

        ability = self.game.player.abilities[ability_index]

        if not ability.is_ready():
            print(f"[TARGETING] Ability '{ability.name}' on cooldown")
            return

        # Enter targeting mode
        self.mode = self.MODE_TARGETING
        self.selected_ability_index = ability_index
        self.selected_ability = ability

        # Create visual feedback
        self._create_targeting_visuals()

        print(f"[TARGETING] Started targeting for '{ability.name}'")

    def cancel_targeting(self):
        """Exit targeting mode without using ability"""
        if self.mode == self.MODE_TARGETING:
            self._destroy_targeting_visuals()
            self.mode = self.MODE_IDLE
            self.selected_ability_index = None
            self.selected_ability = None
            print("[TARGETING] Cancelled")

    def confirm_target(self) -> bool:
        """
        Confirm target and execute ability

        Returns:
            bool: True if ability executed successfully
        """
        print(f"[TARGETING] confirm_target() called - mode={self.mode}, target_pos={self.target_pos}, is_valid={self.is_valid_target}")

        if self.mode != self.MODE_TARGETING or not self.target_pos:
            print(f"[TARGETING] Rejected: Not in targeting mode or no target position")
            return False

        if not self.is_valid_target:
            print("[TARGETING] Rejected: Invalid target")
            return False

        # Execute ability through game (unpack target position tuple)
        # Note: use_ability() returns bool only, message is handled internally via game.add_message()
        success = self.game.use_ability(
            self.selected_ability_index,
            self.target_pos[0],  # target_x
            self.target_pos[1]   # target_y
        )

        if success:
            print(f"[TARGETING] Ability executed at {self.target_pos}")
            self.cancel_targeting()
            return True
        else:
            print(f"[TARGETING] Failed to execute ability")
            return False

    def _create_targeting_visuals(self):
        """Create visual elements for targeting mode"""
        if not self.selected_ability:
            return

        player_x, player_y = self.game.player.x, self.game.player.y

        # Range circle (around player)
        from graphics3d.utils import world_to_3d_position
        player_3d_pos = world_to_3d_position(player_x, player_y, self.RANGE_CIRCLE_HEIGHT)

        # Get ability range
        ability_range = self._get_ability_range(self.selected_ability.name)

        # IMPORTANT: NO PARENT - must be in world space, not UI space!
        self.range_circle = Entity(
            model='circle',
            color=color.rgba(0.3, 0.6, 1.0, 0.3),  # Blue, semi-transparent
            position=player_3d_pos,
            scale=(ability_range * 2, ability_range * 2, 1),  # Diameter = 2 * radius
            rotation_x=90,  # Lay flat on ground
            eternal=True
        )

        # Target cursor - using sphere for maximum visibility (always visible from any angle)
        # NO PARENT - must be in world space!
        self.target_cursor = Entity(
            model='sphere',
            color=color.rgb(1.0, 1.0, 1.0),  # Bright white (solid, no transparency)
            position=(0, 0, 0),
            scale=(self.CURSOR_SIZE * 0.5, self.CURSOR_SIZE * 0.5, self.CURSOR_SIZE * 0.5),  # Sphere scale
            visible=False,  # Hidden until we have a valid target
            eternal=True
        )

        # Cursor outline (ring around sphere for extra visibility)
        # NO PARENT - must be in world space!
        self.cursor_outline = Entity(
            model='circle',
            color=color.rgb(1.0, 1.0, 1.0),  # Solid white outline
            position=(0, 0, 0),
            scale=(self.CURSOR_SIZE * 1.2, self.CURSOR_SIZE * 1.2, 1),  # Larger ring
            rotation_x=90,  # Flat on ground
            visible=False,
            eternal=True
        )

        print(f"[TARGETING] Created cursor sphere (size={self.CURSOR_SIZE}, height={self.CURSOR_HEIGHT})")
        print(f"[TARGETING] Created cursor outline ring (scale={self.CURSOR_SIZE * 1.2})")

        # Info text (ability name and instructions)
        self.info_text = Text(
            text=f"Targeting: {self.selected_ability.name} (Range: {ability_range}) - Click to confirm, ESC to cancel",
            parent=self.parent,
            position=(0, 0.45, 0),  # Top center
            scale=0.8,
            color=color.rgba(1, 1, 1, 1),
            origin=(0, 0),
            eternal=True
        )

        # Error text (shown when hovering invalid target)
        self.error_text = Text(
            text="",
            parent=self.parent,
            position=(0, -0.45, 0),  # Bottom center
            scale=0.7,
            color=color.rgba(1, 0.3, 0.3, 1),  # Red
            origin=(0, 0),
            visible=False,
            eternal=True
        )

    def _destroy_targeting_visuals(self):
        """Destroy targeting visual elements"""
        elements = [
            self.range_circle,
            self.target_cursor,
            self.cursor_outline,
            self.info_text,
            self.error_text
        ]

        for element in elements:
            if element:
                element.disable()

        self.range_circle = None
        self.target_cursor = None
        self.cursor_outline = None
        self.info_text = None
        self.error_text = None

    def _get_ability_range(self, ability_name: str) -> int:
        """
        Get range for ability

        Args:
            ability_name: Name of ability

        Returns:
            int: Range in tiles
        """
        ability_ranges = {
            "Fireball": 8,
            "Frost Nova": 0,  # Self-centered
            "Heal": 0,        # Self-cast
            "Dash": 4,        # Fixed: was 5, but ability has max_distance = 4
            "Shadow Step": 6,
            "Whirlwind": 0,   # Self-centered
            "Healing Touch": 0,  # Self-cast (added for completeness)
        }

        return ability_ranges.get(ability_name, 5)

    def _screen_to_grid_coords(self) -> Optional[Tuple[int, int]]:
        """
        Convert mouse screen position to grid coordinates via raycast
        (Updated for first-person camera support)

        Returns:
            Tuple[int, int] or None: Grid coordinates (x, y) or None if no intersection
        """
        # Raycast from camera through mouse cursor position to ground plane (y=0)

        # Get ray from camera through mouse screen position
        ray_origin = camera.world_position

        # Calculate ray direction using mouse screen coordinates and camera properties
        # mouse.x and mouse.y are in normalized screen coords (-0.5 to 0.5)
        # We need to convert this to a world-space direction

        # Get camera's right and up vectors
        import math
        from ursina import Vec3

        # Camera rotation (yaw and pitch)
        yaw_rad = math.radians(camera.rotation_y)
        pitch_rad = math.radians(camera.rotation_x)

        # Camera forward vector (based on yaw and pitch)
        forward = Vec3(
            math.sin(yaw_rad) * math.cos(pitch_rad),
            -math.sin(pitch_rad),
            math.cos(yaw_rad) * math.cos(pitch_rad)
        ).normalized()

        # Camera right vector (perpendicular to forward in XZ plane)
        right = Vec3(
            math.cos(yaw_rad),
            0,
            -math.sin(yaw_rad)
        ).normalized()

        # Camera up vector (perpendicular to forward and right)
        up = right.cross(forward).normalized()

        # Calculate ray direction using mouse position and FOV
        fov_rad = math.radians(camera.fov)
        aspect_ratio = camera.aspect_ratio

        # Offset ray direction based on mouse position
        h_offset = mouse.x * math.tan(fov_rad / 2) * aspect_ratio
        v_offset = -mouse.y * math.tan(fov_rad / 2)  # NEGATED: screen Y is inverted from world coordinates

        ray_direction = (forward + right * h_offset + up * v_offset).normalized()

        # Calculate intersection with ground plane (y=0)
        # Ray equation: P = ray_origin + t * ray_direction
        # Plane equation: y = 0
        # Solving: ray_origin.y + t * ray_direction.y = 0
        # t = -ray_origin.y / ray_direction.y

        if abs(ray_direction.y) < 0.001:  # Near-horizontal ray, no intersection
            return None

        t = -ray_origin.y / ray_direction.y

        if t < 0:  # Intersection behind camera
            return None

        # Calculate intersection point
        intersection_point = ray_origin + (ray_direction * t)

        # Convert 3D world position to grid coordinates
        # 3D: x maps to grid x, z maps to grid y
        grid_x = int(round(intersection_point.x))
        grid_y = int(round(intersection_point.z))

        # Validate grid coordinates
        if (0 <= grid_x < self.game.dungeon.width and
            0 <= grid_y < self.game.dungeon.height):
            return (grid_x, grid_y)

        return None

    def _validate_target(self, grid_x: int, grid_y: int) -> Tuple[bool, str]:
        """
        Validate if target position is valid for selected ability

        Args:
            grid_x: Target grid X
            grid_y: Target grid Y

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not self.selected_ability or not self.game.player:
            return (False, "No ability selected")

        player_x, player_y = self.game.player.x, self.game.player.y

        # Calculate distance
        distance = abs(grid_x - player_x) + abs(grid_y - player_y)

        # Get ability range
        ability_range = self._get_ability_range(self.selected_ability.name)

        # Check range (0 = self-targeted, no need to check)
        if ability_range > 0 and distance > ability_range:
            return (False, f"OUT OF RANGE (max: {ability_range})")

        # Check if tile is walkable (for movement abilities like Dash)
        if self.selected_ability.name in ["Dash", "Shadow Step"]:
            if not self.game.dungeon.is_walkable(grid_x, grid_y):
                return (False, "Cannot target walls or obstacles")

        # Check line-of-sight (for ranged abilities like Fireball)
        if self.selected_ability.name in ["Fireball"]:
            if not self.game.dungeon.is_walkable(grid_x, grid_y) and \
               self.game.dungeon.get_tile(grid_x, grid_y) != c.TILE_FLOOR:
                return (False, "Line of sight blocked")

        return (True, "")

    def update(self, dt: float):
        """
        Update targeting system

        Args:
            dt: Delta time since last frame
        """
        if self.mode != self.MODE_TARGETING:
            return

        # Get target grid coordinates from mouse
        target_coords = self._screen_to_grid_coords()

        if target_coords:
            grid_x, grid_y = target_coords
            self.target_pos = target_coords

            # Validate target
            is_valid, error_msg = self._validate_target(grid_x, grid_y)
            self.is_valid_target = is_valid

            # Update cursor position
            from graphics3d.utils import world_to_3d_position
            cursor_3d_pos = world_to_3d_position(grid_x, grid_y, self.CURSOR_HEIGHT)

            if self.target_cursor:
                self.target_cursor.position = cursor_3d_pos

                # Debug: Log when cursor is made visible for the first time
                if not self.target_cursor.visible:
                    print(f"[TARGETING] Making cursor VISIBLE at 3D position {cursor_3d_pos}")

                self.target_cursor.visible = True

                # Update outline position (lower than cursor, on ground)
                if self.cursor_outline:
                    from graphics3d.utils import world_to_3d_position
                    outline_pos = world_to_3d_position(grid_x, grid_y, 0.05)  # Just above ground
                    self.cursor_outline.position = outline_pos
                    self.cursor_outline.visible = True

                # Color code cursor (green = valid, red = invalid) - USE SOLID COLORS
                if is_valid:
                    self.target_cursor.color = color.rgb(0.2, 1.0, 0.2)  # Bright solid green
                    if self.cursor_outline:
                        self.cursor_outline.color = color.rgb(0.2, 1.0, 0.2)  # Matching green ring
                else:
                    self.target_cursor.color = color.rgb(1.0, 0.2, 0.2)  # Bright solid red
                    if self.cursor_outline:
                        self.cursor_outline.color = color.rgb(1.0, 0.2, 0.2)  # Matching red ring

                # Debug: Log targeting info
                player_x, player_y = self.game.player.x, self.game.player.y
                distance = abs(grid_x - player_x) + abs(grid_y - player_y)
                print(f"[TARGETING] Cursor at grid ({grid_x}, {grid_y}) | "
                      f"Player at ({player_x}, {player_y}) | "
                      f"Distance: {distance} | "
                      f"Valid: {is_valid} | "
                      f"Error: {error_msg if not is_valid else 'None'}")

            # Update error text
            if self.error_text:
                if not is_valid and error_msg:
                    self.error_text.text = error_msg
                    self.error_text.visible = True
                else:
                    self.error_text.visible = False
        else:
            # No target under mouse
            if self.target_cursor:
                self.target_cursor.visible = False

            if self.cursor_outline:
                self.cursor_outline.visible = False

            if self.error_text:
                self.error_text.visible = False

            self.target_pos = None
            self.is_valid_target = False

    def cleanup(self):
        """Clean up targeting system"""
        self._destroy_targeting_visuals()
        print("✓ TargetingSystem cleaned up")

    def __repr__(self) -> str:
        return f"<TargetingSystem mode={'TARGETING' if self.mode == self.MODE_TARGETING else 'IDLE'}>"
