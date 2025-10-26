#!/usr/bin/env python3
"""
Item Model Viewer - Quick viewer for debugging 3D item models

Usage:
  python3 viewer_item_models.py                              # View all items (7 types × 5 rarities)
  python3 viewer_item_models.py --type sword                 # View all sword rarities
  python3 viewer_item_models.py --rarity legendary           # View all legendary items
  python3 viewer_item_models.py --type ring --rarity epic    # View only epic ring

Controls:
- Left mouse drag: Rotate camera
- Scroll wheel: Zoom in/out
- R: Reset camera
- 1-7: Focus on item types (Sword, Shield, Potion, Boots, Ring, Chest, Coin)
- Q/W/E/R/T: Focus on rarity tiers (Common, Uncommon, Rare, Epic, Legendary)
- 0: Return to overview
- ESC: Quit
"""

from ursina import Ursina, Entity, Vec3, Text, color as ursina_color, camera, mouse, held_keys, time
import sys
import math
import argparse

# Import item model creators
from graphics3d.items import create_item_model_3d, update_item_animation
import constants as c


def parse_arguments():
    """Parse command-line arguments for filtering items"""
    parser = argparse.ArgumentParser(
        description='3D Item Model Viewer - View procedurally generated item models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # View all items (7 types × 5 rarities)
  %(prog)s --type sword                 # View all sword rarities (5 items)
  %(prog)s --rarity legendary           # View all legendary items (7 items)
  %(prog)s --type ring --rarity epic    # View only epic ring (1 item)
        """
    )

    parser.add_argument(
        '--type',
        choices=['sword', 'shield', 'potion', 'boots', 'ring', 'chest', 'coin'],
        help='Filter by item type'
    )

    parser.add_argument(
        '--rarity',
        choices=['common', 'uncommon', 'rare', 'epic', 'legendary'],
        help='Filter by rarity tier'
    )

    return parser.parse_args()


class OrbitCamera:
    """
    Simple orbit camera controller - adapted from DNA Editor's working implementation.
    Uses Ursina's built-in mouse velocity tracking for smooth rotation.
    """

    def __init__(self, target_position=Vec3(0, 0, 0), distance=12.0, height=2.0, items_list=None):
        self.target = target_position
        self.camera_angle = 0  # Horizontal rotation angle
        self.camera_height = height  # Vertical height
        self.camera_distance = distance  # Distance from target

        # Focus state
        self.selected_item_index = None  # None = overview, 0-24 = specific item
        self.items_list = items_list or []

        # Default camera settings
        self.overview_defaults = {
            'target': target_position,
            'distance': distance,
            'height': height,
            'angle': 0
        }
        self.item_focus_defaults = {
            'distance': 4.0,  # Closer view for individual items
            'height': 1.0,    # Lower height for better angle
            'angle': 0
        }

        # Limits
        self.min_distance = 2.0
        self.max_distance = 25.0
        self.min_height = 0.5
        self.max_height = 8.0

        self.update_camera_position()

    def update_camera_position(self):
        """Update camera position using orbit math - same as DNA Editor"""
        # If an item is selected, update target to follow its position
        if self.selected_item_index is not None and self.selected_item_index < len(self.items_list):
            item = self.items_list[self.selected_item_index]
            item_pos = item['entity'].position
            self.target = Vec3(item_pos.x, item_pos.y + 0.5, item_pos.z)

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

        # Mouse drag to orbit horizontally (use held_keys like DNA Editor does)
        if held_keys['left mouse']:
            # Use mouse.velocity for smooth rotation (automatic delta calculation!)
            self.camera_angle += mouse.velocity[0] * 200  # Horizontal rotation only
            # Vertical mouse movement disabled - camera stays on horizontal plane
            camera_changed = True

        # Update camera position if anything changed
        if camera_changed:
            self.update_camera_position()

        # Reset camera (R key) - aware of current focus mode
        if held_keys['r']:
            if self.selected_item_index is None:
                # Reset to overview defaults
                self.camera_angle = self.overview_defaults['angle']
                self.camera_height = self.overview_defaults['height']
                self.camera_distance = self.overview_defaults['distance']
                print("Camera reset: Overview mode")
            else:
                # Reset to item focus defaults (stay focused on item)
                self.camera_angle = self.item_focus_defaults['angle']
                self.camera_height = self.item_focus_defaults['height']
                self.camera_distance = self.item_focus_defaults['distance']
                item_name = self.items_list[self.selected_item_index]['name']
                print(f"Camera reset: Focused on {item_name}")

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

    def focus_on_item(self, item_index):
        """
        Focus camera on a specific item (0-24)

        Args:
            item_index: Index of item in items_list
        """
        if 0 <= item_index < len(self.items_list):
            self.selected_item_index = item_index
            item = self.items_list[item_index]

            # Get item position (add small Y offset to center on model)
            item_pos = item['entity'].position
            self.target = Vec3(item_pos.x, item_pos.y + 0.5, item_pos.z)

            # Apply item focus defaults
            self.camera_distance = self.item_focus_defaults['distance']
            self.camera_height = self.item_focus_defaults['height']
            self.camera_angle = self.item_focus_defaults['angle']

            self.update_camera_position()
            print(f"Focused on: {item['name']}")

    def focus_overview(self):
        """Return to overview mode (viewing all items)"""
        self.selected_item_index = None

        # Restore overview defaults
        self.target = self.overview_defaults['target']
        self.camera_distance = self.overview_defaults['distance']
        self.camera_height = self.overview_defaults['height']
        self.camera_angle = self.overview_defaults['angle']

        self.update_camera_position()
        print("Returned to overview")


def create_item_grid(type_filter=None, rarity_filter=None):
    """
    Create item models in a grid layout, optionally filtered by type/rarity

    Args:
        type_filter: Optional string filter ('sword', 'shield', etc.)
        rarity_filter: Optional string filter ('common', 'rare', etc.)

    Grid layout:
    - Rows: Item types (Sword, Shield, Potion, Boots, Ring, Chest, Coin)
    - Columns: Rarities (Common, Uncommon, Rare, Epic, Legendary)

    Returns:
        list: List of dicts with item data (entity, type, rarity, label, name)
    """
    items_data = []

    # Mapping from string names to constants
    type_name_map = {
        'sword': c.ITEM_SWORD,
        'shield': c.ITEM_SHIELD,
        'potion': c.ITEM_HEALTH_POTION,
        'boots': c.ITEM_BOOTS,
        'ring': c.ITEM_RING,
        'chest': c.ITEM_TREASURE_CHEST,
        'coin': c.ITEM_GOLD_COIN,
    }

    rarity_name_map = {
        'common': c.RARITY_COMMON,
        'uncommon': c.RARITY_UNCOMMON,
        'rare': c.RARITY_RARE,
        'epic': c.RARITY_EPIC,
        'legendary': c.RARITY_LEGENDARY,
    }

    # Item types (rows)
    all_item_types = [
        (c.ITEM_SWORD, "Sword"),
        (c.ITEM_SHIELD, "Shield"),
        (c.ITEM_HEALTH_POTION, "Potion"),
        (c.ITEM_BOOTS, "Boots"),
        (c.ITEM_RING, "Ring"),
        (c.ITEM_TREASURE_CHEST, "Chest"),
        (c.ITEM_GOLD_COIN, "Coin"),
    ]

    # Rarities (columns)
    all_rarities = [
        (c.RARITY_COMMON, "Common"),
        (c.RARITY_UNCOMMON, "Uncommon"),
        (c.RARITY_RARE, "Rare"),
        (c.RARITY_EPIC, "Epic"),
        (c.RARITY_LEGENDARY, "Legendary"),
    ]

    # Apply filters
    if type_filter:
        filter_const = type_name_map[type_filter]
        item_types = [(t, n) for t, n in all_item_types if t == filter_const]
    else:
        item_types = all_item_types

    if rarity_filter:
        filter_const = rarity_name_map[rarity_filter]
        rarities = [(r, n) for r, n in all_rarities if r == filter_const]
    else:
        rarities = all_rarities

    # Grid layout - dynamic based on filtered items
    num_cols = len(rarities)
    num_rows = len(item_types)
    grid_spacing = 2.5

    # Calculate centering offsets
    col_offset = (num_cols - 1) / 2.0  # Center columns around origin
    row_offset = (num_rows - 1) / 2.0  # Center rows around origin

    # Column headers (rarity names) - only if showing multiple rarities
    if num_cols > 1:
        for col, (rarity, rarity_name) in enumerate(rarities):
            x = (col - col_offset) * grid_spacing
            z = -(row_offset + 0.8) * grid_spacing  # Above grid

            Text(
                text=rarity_name,
                position=(x, 0, z),
                scale=1.5,
                color=ursina_color.white,
                origin=(0, 0),
                billboard=True
            )

    # Row headers (item type names) - only if showing multiple types
    if num_rows > 1:
        for row, (item_type, item_name) in enumerate(item_types):
            x = -(col_offset + 1.4) * grid_spacing  # Left of grid
            z = (row - row_offset) * grid_spacing

            Text(
                text=item_name,
                position=(x, 0, z),
                scale=1.5,
                color=ursina_color.white,
                origin=(0, 0),
                billboard=True
            )

    # Create all items in grid
    for row, (item_type, item_name) in enumerate(item_types):
        for col, (rarity, rarity_name) in enumerate(rarities):
            # Calculate grid position (centered around origin)
            x = (col - col_offset) * grid_spacing
            z = (row - row_offset) * grid_spacing
            y = 0.5  # Slightly above ground (items float)

            position = Vec3(x, y, z)

            # Create item model
            item_entity = create_item_model_3d(item_type, rarity, position)

            # Full name for this specific item
            full_name = f"{rarity_name} {item_name}"

            items_data.append({
                'entity': item_entity,
                'type': item_type,
                'rarity': rarity,
                'name': full_name,
                'type_name': item_name,
                'rarity_name': rarity_name,
            })

    return items_data


def create_ground_plane():
    """Create a simple ground plane for spatial reference"""
    # Main ground plane
    ground = Entity(
        model='plane',
        scale=25,
        color=ursina_color.rgb(40, 40, 45),
        position=(0, -0.5, 0)
    )

    # Add grid lines for better depth perception
    grid_color = ursina_color.rgb(60, 60, 65)
    line_thickness = 0.02
    grid_range = 12
    grid_spacing = 2

    for i in range(-grid_range, grid_range + 1, grid_spacing):
        # X-axis lines (parallel to X)
        Entity(
            model='cube',
            scale=(25, 0.01, line_thickness),
            color=grid_color,
            position=(0, -0.49, i)
        )
        # Z-axis lines (parallel to Z)
        Entity(
            model='cube',
            scale=(line_thickness, 0.01, 25),
            color=grid_color,
            position=(i, -0.49, 0)
        )

    return ground


# Global variables for update function
orbit_cam = None
items = []
info_text = None  # Dynamic text showing current focus state


def update():
    """
    Global update function - called automatically by Ursina every frame.
    Must be defined at module level for Ursina to find it.
    """
    global orbit_cam, items

    if orbit_cam is None:
        return

    # Update camera controls
    orbit_cam.update()

    # Update all item animations (floating and rotation)
    for item_data in items:
        update_item_animation(item_data['entity'], time.dt)

    # ESC to quit
    if held_keys['escape']:
        print("Exiting viewer...")
        sys.exit(0)


def input(key):
    """
    Global input function - called automatically by Ursina on input events.
    Must be defined at module level for Ursina to find it.
    This is where scroll events and key presses are handled.
    """
    global orbit_cam, info_text, items

    if orbit_cam is None:
        return

    # Handle scroll for zoom (scroll is momentary, not "held")
    orbit_cam.handle_scroll(key)

    # Handle number keys for item type focus (1-7)
    if key == '0':
        orbit_cam.focus_overview()
        if info_text:
            info_text.text = "Overview Mode"
    elif key in ['1', '2', '3', '4', '5', '6', '7']:
        # Focus on first item of this type (common rarity)
        item_type_index = int(key) - 1  # Convert 1-7 to 0-6
        first_item_of_type = item_type_index * 5  # Each type has 5 rarities
        if first_item_of_type < len(items):
            orbit_cam.focus_on_item(first_item_of_type)
            if info_text:
                type_name = items[first_item_of_type]['type_name']
                info_text.text = f"Focused: {type_name} (All Rarities)"

    # Handle letter keys for rarity focus (Q/W/E/R/T)
    rarity_keys = {
        'q': (0, "Common"),
        'w': (1, "Uncommon"),
        'e': (2, "Rare"),
        'r': (3, "Epic"),
        't': (4, "Legendary"),
    }

    if key in rarity_keys:
        rarity_index, rarity_name = rarity_keys[key]
        # Focus on first item of this rarity (sword)
        if rarity_index < len(items):
            orbit_cam.focus_on_item(rarity_index)
            if info_text:
                info_text.text = f"Focused: {rarity_name} Rarity (All Types)"


def main():
    """Main entry point for the item model viewer"""
    global orbit_cam, items, info_text

    # Parse command-line arguments
    args = parse_arguments()

    # Initialize Ursina with simple window settings
    app = Ursina(
        title="Item Model Viewer",
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

    # Create filtered items
    print("Loading item models...")
    if args.type and args.rarity:
        print(f"  Filter: {args.rarity.capitalize()} {args.type.capitalize()}")
    elif args.type:
        print(f"  Filter: All {args.type.capitalize()} rarities")
    elif args.rarity:
        print(f"  Filter: All {args.rarity.capitalize()} items")
    else:
        print("  Filter: All items (7 types × 5 rarities)")

    items = create_item_grid(type_filter=args.type, rarity_filter=args.rarity)
    print(f"Loaded {len(items)} item model(s)")

    # Adjust camera defaults based on number of items
    # Single item: Close-up view
    # Row/column: Medium view
    # Full grid: Wide view
    if len(items) == 1:
        camera_distance = 4.0
        camera_height = 1.5
    elif len(items) <= 7:  # Single row or column
        camera_distance = 8.0
        camera_height = 2.0
    else:  # Full grid
        camera_distance = 15.0
        camera_height = 3.0

    # Setup orbit camera (look at center of grid)
    # Pass items list so camera can track them
    orbit_cam = OrbitCamera(target_position=Vec3(0, 0.5, 0), distance=camera_distance, height=camera_height, items_list=items)

    # Create controls text (top-left corner)
    controls_text = Text(
        text=(
            "Item Model Viewer\n"
            "---------------------\n"
            "Left Mouse Drag: Rotate\n"
            "Scroll Wheel: Zoom\n"
            "R: Reset Camera\n"
            "1-7: Focus Item Type\n"
            "  (1=Sword, 2=Shield,\n"
            "   3=Potion, 4=Boots,\n"
            "   5=Ring, 6=Chest,\n"
            "   7=Coin)\n"
            "Q/W/E/R/T: Focus Rarity\n"
            "  (Q=Common, W=Uncommon,\n"
            "   E=Rare, R=Epic, T=Legendary)\n"
            "0: Overview\n"
            "ESC: Quit"
        ),
        position=(-0.85, 0.48),
        scale=1.0,
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
    if len(items) > 1:
        print("  - 1-7 to focus on item types (Sword, Shield, Potion, Boots, Ring, Chest, Coin)")
        print("  - Q/W/E/R/T to focus on rarities (Common, Uncommon, Rare, Epic, Legendary)")
        print("  - 0 to return to overview")
    print("  - ESC to quit")
    print(f"\nCamera position: {camera.position}")
    print(f"Camera looking at: {orbit_cam.target}")

    # Show filtering info
    if args.type or args.rarity:
        print("\nFiltering enabled - use without filters to see all items:")
        print("  python3 viewer_item_models.py")

    # Run the app (update function will be called automatically)
    app.run()


if __name__ == "__main__":
    main()
