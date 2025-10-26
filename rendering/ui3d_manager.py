"""
3D UI Overlay Manager

Manages all UI components for 3D mode using Ursina's UI system.
Now uses a unified Helmet HUD design for immersive gameplay.
"""

from typing import Optional
from ursina import Entity, color, window, camera
from game_logic.game import Game
from ui3d.helmet_hud import HelmetHUD3D
from ui3d.targeting import TargetingSystem


class UI3DManager:
    """
    Main manager for 3D UI overlay

    Now uses a unified Helmet HUD design for immersive gameplay.
    All UI elements are consolidated into a single widget.
    """

    def __init__(self, game: Game):
        """
        Initialize UI manager

        Args:
            game: Game instance to display UI for
        """
        self.game = game
        self.visible = True

        # UI widgets
        self.helmet_hud = None
        self.targeting_system = None

        # Root UI entity (parent for all UI elements)
        # IMPORTANT: Must be parented to camera.ui for screen-space rendering
        self.ui_root = Entity(
            name='ui_root_3d',
            parent=camera.ui,  # Attach to Ursina's screen-space UI system
            eternal=True,  # Don't destroy on scene change
            enabled=True
        )

        # Initialize all widgets
        self.initialize_widgets()

        print("✓ UI3DManager initialized (Helmet HUD design)")
        print(f"  - Screen size: {window.size}")
        print(f"  - Using unified Helmet HUD layout")

    def initialize_widgets(self):
        """Initialize all UI widgets"""
        # Helmet HUD (unified UI design)
        self.helmet_hud = HelmetHUD3D(
            game=self.game,
            parent=self.ui_root
        )

        # Targeting system
        self.targeting_system = TargetingSystem(
            game=self.game,
            parent=self.ui_root
        )

        print("✓ All UI widgets initialized")
        print(f"  - Widget count: 2 (Helmet HUD, Targeting)")
        print(f"  - UI root enabled: {self.ui_root.enabled}")
        print(f"  - UI visible: {self.visible}")


    def set_visibility(self, visible: bool):
        """
        Toggle UI visibility

        Args:
            visible: True to show UI, False to hide
        """
        self.visible = visible
        self.ui_root.enabled = visible

        print(f"[UI3D] Visibility set to: {visible}")

    def update(self, dt: float, camera_yaw: float = 0.0):
        """
        Update UI state (called every frame)

        Args:
            dt: Delta time since last frame
            camera_yaw: Camera yaw in degrees (for minimap orientation)
        """
        if not self.visible:
            return

        # Update Helmet HUD (with camera yaw for minimap)
        if self.helmet_hud:
            self.helmet_hud.update(dt, camera_yaw)

        # Update targeting system
        if self.targeting_system:
            self.targeting_system.update(dt)

    def add_message(self, message: str, msg_type: str = "event"):
        """
        Add a message to the combat log

        Args:
            message: Message text
            msg_type: Message type for color coding (damage, heal, loot, event, etc.)
        """
        if self.helmet_hud:
            self.helmet_hud.add_message(message, msg_type)
        else:
            print(f"[COMBAT LOG] {message}")  # Fallback to console

    def cleanup(self):
        """
        Clean up all UI entities and resources
        """
        # Clean up widgets
        if self.helmet_hud:
            self.helmet_hud.cleanup()
            self.helmet_hud = None

        if self.targeting_system:
            self.targeting_system.cleanup()
            self.targeting_system = None

        # Destroy root entity
        if self.ui_root:
            self.ui_root.disable()
            self.ui_root = None

        print("✓ UI3DManager cleaned up")

    def get_resolution_scale(self) -> float:
        """
        Calculate UI scale factor based on window resolution

        Uses 1920x1080 as baseline (scale=1.0)

        Returns:
            float: Scale factor for UI elements
        """
        baseline_width = 1920
        current_width = window.size[0]

        scale = current_width / baseline_width
        return max(0.5, min(2.0, scale))  # Clamp between 0.5x and 2.0x

    def __repr__(self) -> str:
        return f"<UI3DManager visible={self.visible} widgets={sum([1 for w in [self.helmet_hud, self.targeting_system] if w is not None])}>"
