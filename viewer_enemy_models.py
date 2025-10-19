#!/usr/bin/env python3
"""
Enemy Model Viewer - Quick viewer for debugging 3D enemy models

Usage: python3 viewer_enemy_models.py

Controls:
- Left mouse drag: Rotate camera
- Scroll wheel: Zoom in/out
- R: Reset camera
- 1-6: Focus on individual enemies
- 0: Return to overview
- ESC: Quit
"""

from ursina import Ursina, Entity, Vec3, Text, color as ursina_color, camera, mouse, held_keys, time
import sys
import math

# Import enemy model creators
from graphics3d.enemies.goblin import create_goblin_3d, update_goblin_animation
from graphics3d.enemies.slime import create_slime_3d, update_slime_animation
from graphics3d.enemies.skeleton import create_skeleton_3d, update_skeleton_animation
from graphics3d.enemies.orc import create_orc_3d, update_orc_animation
from graphics3d.enemies.demon import create_demon_3d, update_demon_animation
from graphics3d.enemies.dragon import create_dragon_3d, update_dragon_animation
import constants as c


class OrbitCamera:
    """
    Simple orbit camera controller - adapted from DNA Editor's working implementation.
    Uses Ursina's built-in mouse velocity tracking for smooth rotation.
    """

    def __init__(self, target_position=Vec3(0, 0, 0), distance=12.0, height=2.0, enemies_list=None):
        self.target = target_position
        self.camera_angle = 0  # Horizontal rotation angle
        self.camera_height = height  # Vertical height
        self.camera_distance = distance  # Distance from target

        # Focus state
        self.selected_enemy_index = None  # None = overview, 0-5 = specific enemy
        self.enemies_list = enemies_list or []

        # Default camera settings
        self.overview_defaults = {
            'target': target_position,
            'distance': distance,
            'height': height,
            'angle': 0
        }
        self.enemy_focus_defaults = {
            'distance': 6.0,  # Closer view for individual enemies
            'height': 1.5,    # Lower height for better angle
            'angle': 0
        }

        # Limits
        self.min_distance = 3.0
        self.max_distance = 25.0
        self.min_height = 0.5
        self.max_height = 8.0

        self.update_camera_position()

    def update_camera_position(self):
        """Update camera position using orbit math - same as DNA Editor"""
        # If an enemy is selected, update target to follow its position
        if self.selected_enemy_index is not None and self.selected_enemy_index < len(self.enemies_list):
            enemy = self.enemies_list[self.selected_enemy_index]
            enemy_pos = enemy['entity'].position
            self.target = Vec3(enemy_pos.x, enemy_pos.y + 0.5, enemy_pos.z)

        # Calculate camera position using orbit angle
        angle_rad = math.radians(self.camera_angle)
        cam_x = self.camera_distance * math.sin(angle_rad)
        cam_z = -self.camera_distance * math.cos(angle_rad)

        # Update camera position and look at target
        camera.position = self.target + Vec3(cam_x, self.camera_height, cam_z)
        camera.look_at(self.target)

    def update(self):
        """
        Handle camera controls - adapted from DNA Editor's _handle_camera_controls().
        Uses held_keys and mouse.velocity for smooth, working controls.
        """
        camera_changed = False

        # Mouse drag to orbit (use held_keys like DNA Editor does)
        if held_keys['left mouse']:
            # Use mouse.velocity for smooth rotation (automatic delta calculation!)
            self.camera_angle += mouse.velocity[0] * 200  # Horizontal rotation
            self.camera_height += mouse.velocity[1] * 5   # Vertical movement
            camera_changed = True

        # Clamp camera height
        self.camera_height = max(self.min_height, min(self.max_height, self.camera_height))

        # Update camera position if anything changed
        if camera_changed:
            self.update_camera_position()

        # Reset camera (R key) - aware of current focus mode
        if held_keys['r']:
            if self.selected_enemy_index is None:
                # Reset to overview defaults
                self.camera_angle = self.overview_defaults['angle']
                self.camera_height = self.overview_defaults['height']
                self.camera_distance = self.overview_defaults['distance']
                print("Camera reset: Overview mode")
            else:
                # Reset to enemy focus defaults (stay focused on enemy)
                self.camera_angle = self.enemy_focus_defaults['angle']
                self.camera_height = self.enemy_focus_defaults['height']
                self.camera_distance = self.enemy_focus_defaults['distance']
                enemy_name = self.enemies_list[self.selected_enemy_index]['name']
                print(f"Camera reset: Focused on {enemy_name}")

            self.update_camera_position()
            held_keys['r'] = False  # Reset key state

    def handle_scroll(self, key):
        """Handle scroll input for zoom (must be called from input() function)"""
        if key == 'scroll up':
            self.camera_distance -= 0.5
            self.camera_distance = max(self.min_distance, min(self.max_distance, self.camera_distance))
            self.update_camera_position()
        elif key == 'scroll down':
            self.camera_distance += 0.5
            self.camera_distance = max(self.min_distance, min(self.max_distance, self.camera_distance))
            self.update_camera_position()

    def focus_on_enemy(self, enemy_index):
        """
        Focus camera on a specific enemy (0-5)

        Args:
            enemy_index: Index of enemy in enemies_list (0-5)
        """
        if 0 <= enemy_index < len(self.enemies_list):
            self.selected_enemy_index = enemy_index
            enemy = self.enemies_list[enemy_index]

            # Get enemy position (add small Y offset to center on model)
            enemy_pos = enemy['entity'].position
            self.target = Vec3(enemy_pos.x, enemy_pos.y + 0.5, enemy_pos.z)

            # Apply enemy focus defaults
            self.camera_distance = self.enemy_focus_defaults['distance']
            self.camera_height = self.enemy_focus_defaults['height']
            self.camera_angle = self.enemy_focus_defaults['angle']

            self.update_camera_position()
            print(f"Focused on: {enemy['name']}")

    def focus_overview(self):
        """Return to overview mode (viewing all enemies)"""
        self.selected_enemy_index = None

        # Restore overview defaults
        self.target = self.overview_defaults['target']
        self.camera_distance = self.overview_defaults['distance']
        self.camera_height = self.overview_defaults['height']
        self.camera_angle = self.overview_defaults['angle']

        self.update_camera_position()
        print("Returned to overview")


def create_enemy_grid():
    """
    Create all enemy models in a 3x2 grid layout on the ground

    Returns:
        list: List of dicts with enemy data (entity, type, update_func, label, name)
    """
    enemies_data = []

    # Enemy types and their configurations
    enemy_configs = [
        (c.ENEMY_GOBLIN, "Goblin", create_goblin_3d, update_goblin_animation, c.COLOR_ENEMY_GOBLIN),
        (c.ENEMY_SLIME, "Slime", create_slime_3d, update_slime_animation, c.COLOR_ENEMY_SLIME),
        (c.ENEMY_SKELETON, "Skeleton", create_skeleton_3d, update_skeleton_animation, c.COLOR_ENEMY_SKELETON),
        (c.ENEMY_ORC, "Orc", create_orc_3d, update_orc_animation, c.COLOR_ENEMY_ORC),
        (c.ENEMY_DEMON, "Demon", create_demon_3d, update_demon_animation, c.COLOR_ENEMY_DEMON),
        (c.ENEMY_DRAGON, "Dragon", create_dragon_3d, update_dragon_animation, c.COLOR_ENEMY_DRAGON),
    ]

    # Grid layout: 3 columns x 2 rows
    grid_cols = 3
    grid_spacing = 3.0

    for i, (enemy_type, name, create_func, update_func, qcolor) in enumerate(enemy_configs):
        # Calculate grid position (centered around origin)
        col = i % grid_cols
        row = i // grid_cols

        x = (col - 1) * grid_spacing  # -1 to center (cols: -1, 0, 1)
        z = (row - 0.5) * grid_spacing  # -0.5 to center (rows: -0.5, 0.5)
        y = 0  # Place on ground level

        position = Vec3(x, y, z)

        # Convert RGB tuple to Ursina color
        from ursina import color as ursina_color
        # Get RGB tuple for this enemy type
        enemy_colors_rgb = {
            c.ENEMY_GOBLIN: c.COLOR_ENEMY_GOBLIN_RGB,
            c.ENEMY_SLIME: c.COLOR_ENEMY_SLIME_RGB,
            c.ENEMY_SKELETON: c.COLOR_ENEMY_SKELETON_RGB,
            c.ENEMY_ORC: c.COLOR_ENEMY_ORC_RGB,
            c.ENEMY_DEMON: c.COLOR_ENEMY_DEMON_RGB,
            c.ENEMY_DRAGON: c.COLOR_ENEMY_DRAGON_RGB,
        }
        rgb_tuple = enemy_colors_rgb.get(enemy_type, c.COLOR_ENEMY_GOBLIN_RGB)
        enemy_color = ursina_color.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

        # Create enemy model
        enemy_entity = create_func(position, enemy_color)

        # Create label text below the enemy
        label = Text(
            text=name,
            position=(x, -0.8, z),
            scale=2.5,
            color=ursina_color.white,
            origin=(0, 0),
            billboard=True
        )

        enemies_data.append({
            'entity': enemy_entity,
            'type': enemy_type,
            'update_func': update_func,
            'label': label,
            'name': name
        })

    return enemies_data


def create_ground_plane():
    """Create a simple ground plane for spatial reference - like DNA Editor"""
    # Main ground plane
    ground = Entity(
        model='plane',
        scale=20,
        color=ursina_color.rgb(40, 40, 45),
        position=(0, -0.5, 0)
    )

    # Add grid lines for better depth perception
    grid_color = ursina_color.rgb(60, 60, 65)
    line_thickness = 0.02
    grid_range = 10
    grid_spacing = 2

    for i in range(-grid_range, grid_range + 1, grid_spacing):
        # X-axis lines (parallel to X)
        Entity(
            model='cube',
            scale=(20, 0.01, line_thickness),
            color=grid_color,
            position=(0, -0.49, i)
        )
        # Z-axis lines (parallel to Z)
        Entity(
            model='cube',
            scale=(line_thickness, 0.01, 20),
            color=grid_color,
            position=(i, -0.49, 0)
        )

    return ground


# Global variables for update function
orbit_cam = None
enemies = []
info_text = None  # Dynamic text showing current focus state


def update():
    """
    Global update function - called automatically by Ursina every frame.
    Must be defined at module level for Ursina to find it.
    """
    global orbit_cam, enemies

    if orbit_cam is None:
        return

    # Update camera controls
    orbit_cam.update()

    # Update all enemy animations
    for enemy_data in enemies:
        enemy_data['update_func'](enemy_data['entity'], time.dt)

    # ESC to quit
    if held_keys['escape']:
        print("Exiting viewer...")
        sys.exit(0)


def input(key):
    """
    Global input function - called automatically by Ursina on input events.
    Must be defined at module level for Ursina to find it.
    This is where scroll events are handled (they don't work with held_keys).
    """
    global orbit_cam, info_text

    if orbit_cam is None:
        return

    # Handle scroll for zoom (scroll is momentary, not "held")
    orbit_cam.handle_scroll(key)

    # Handle number keys for camera focus (0-6)
    if key == '0':
        orbit_cam.focus_overview()
        if info_text:
            info_text.text = "Overview Mode"
    elif key in ['1', '2', '3', '4', '5', '6']:
        enemy_index = int(key) - 1  # Convert 1-6 to 0-5
        if enemy_index < len(enemies):
            orbit_cam.focus_on_enemy(enemy_index)
            if info_text:
                info_text.text = f"Focused: {enemies[enemy_index]['name']}"


def main():
    """Main entry point for the enemy model viewer"""
    global orbit_cam, enemies, info_text

    # Initialize Ursina with simple window settings
    app = Ursina(
        title="Enemy Model Viewer",
        borderless=False,
        fullscreen=False,
        size=(1280, 720),
        vsync=True
    )

    # Set window background color
    from ursina import window
    window.color = ursina_color.rgb(25, 25, 30)

    # Set up camera
    camera.fov = 60
    camera.clip_plane_near = 0.1

    # Create ground plane
    ground = create_ground_plane()

    # Create all enemies in a grid
    print("Loading enemy models...")
    enemies = create_enemy_grid()
    print(f"Loaded {len(enemies)} enemy models")

    # Setup orbit camera (look at center of grid, slightly above ground)
    # Pass enemies list so camera can track them
    orbit_cam = OrbitCamera(target_position=Vec3(0, 0.5, 0), distance=12.0, height=2.0, enemies_list=enemies)

    # Create controls text (top-left corner)
    controls_text = Text(
        text=(
            "Enemy Model Viewer\n"
            "---------------------\n"
            "Left Mouse Drag: Rotate\n"
            "Scroll Wheel: Zoom\n"
            "R: Reset Camera\n"
            "1-6: Focus Enemy\n"
            "0: Overview\n"
            "ESC: Quit"
        ),
        position=(-0.85, 0.45),
        scale=1.2,
        color=ursina_color.rgb(200, 200, 200),
        origin=(-0.5, 0.5),
        background=True
    )

    # Create info text (top-right corner) showing current focus state
    info_text = Text(
        text="Overview Mode",
        position=(0.75, 0.45),
        scale=1.5,
        color=ursina_color.rgb(100, 200, 255),
        origin=(0.5, 0.5)
    )

    print("\nViewer ready!")
    print("Controls:")
    print("  - Left mouse drag to rotate, scroll to zoom")
    print("  - R to reset camera")
    print("  - 1-6 to focus on individual enemies")
    print("  - 0 to return to overview")
    print("  - ESC to quit")
    print(f"\nCamera position: {camera.position}")
    print(f"Camera looking at: {orbit_cam.target}")

    # Run the app (update function will be called automatically)
    app.run()


if __name__ == "__main__":
    main()
