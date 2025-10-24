"""
3D Class Selection Screen

Displays 4 class models in a circular formation with stats and ability descriptions.
Player can rotate between classes and select one to start the game.
"""

from ursina import Entity, camera, color, Text, Button, Vec3, held_keys, mouse, time as ursina_time, AmbientLight, DirectionalLight, PointLight
import math
import constants as c
from audio import get_audio_manager
from ui.widgets.dungeon_button_3d import DungeonButton


class ClassSelection3D(Entity):
    """
    3D class selection screen with rotating character models.

    Layout:
    - Center: Rotating 3D class model (large)
    - Left/Right arrows: Navigate between classes
    - Top: Class name and description
    - Bottom: Stats bars (HP, Attack, Defense)
    - Bottom-right: "Start Game" button
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # Class data
        self.classes = [c.CLASS_WARRIOR, c.CLASS_MAGE, c.CLASS_ROGUE, c.CLASS_RANGER]
        self.current_class_index = 0
        self.current_class = self.classes[self.current_class_index]

        # Class models (lazy loaded)
        self.class_models = {}

        # Lighting
        self.ambient_light = None
        self.key_light = None
        self.rim_light = None

        # UI elements
        self.ui_elements = []
        self.class_name_text = None
        self.class_desc_text = None
        self.stat_texts = {}
        self.ability_texts = []
        self.start_button = None
        self.left_arrow = None
        self.right_arrow = None

        # Animation
        self.model_rotation = 0.0
        self.model_rotation_speed = 30.0  # Degrees per second
        self.transition_progress = 0.0
        self.transitioning = False

        # Mouse drag rotation
        self.is_dragging = False
        self.last_mouse_x = 0
        self.drag_sensitivity = 200.0  # Degrees per screen width
        self.auto_rotate = True  # Auto-rotate when not dragging
        self.idle_timer = 0.0  # Time since last drag
        self.idle_timeout = 2.0  # Resume auto-rotation after 2 seconds of no dragging

        # Camera position
        self.camera_distance = 4.5  # Slightly closer
        self.camera_height = 1.2    # Lower to center on model better
        self.model_display_height = 0.5  # Model center height

        # Initialize
        self._setup_lighting()
        self._create_ui()
        self._load_current_model()
        self._update_ui_for_class()

        # Initially hidden
        self.enabled = False

        print(f"✓ ClassSelection3D initialized")

    def _setup_lighting(self):
        """Set up lighting for character display"""
        # Ambient light (general illumination)
        self.ambient_light = AmbientLight(
            color=color.rgb(0.784, 0.784, 0.824),
            intensity=0.4
        )

        # Key light (main light from front-upper-right)
        self.key_light = DirectionalLight(
            position=(3, 5, 2),
            rotation=(45, -30, 0),
            color=color.rgb(1.0, 0.98, 0.941),  # Warm white
            intensity=1.0
        )

        # Rim light (back light for depth)
        self.rim_light = DirectionalLight(
            position=(-2, 3, -4),
            rotation=(135, 30, 0),
            color=color.rgb(0.706, 0.784, 1.0),  # Cool blue
            intensity=0.6
        )

        print("✓ Class selection lighting configured")

    def _create_ui(self):
        """Create UI overlay elements"""
        # Title
        title = Text(
            text="SELECT YOUR CLASS",
            position=(0, 0.45),
            origin=(0, 0),
            scale=2.5,
            color=color.rgb(0.863, 0.863, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(title)

        # Class name (large, centered)
        self.class_name_text = Text(
            text="WARRIOR",
            position=(0, 0.35),
            origin=(0, 0),
            scale=3.0,
            color=color.rgb(0.706, 0.235, 0.157),
            parent=camera.ui
        )
        self.ui_elements.append(self.class_name_text)

        # Class description
        self.class_desc_text = Text(
            text="High HP tank with strong defense",
            position=(0, 0.28),
            origin=(0, 0),
            scale=1.2,
            color=color.rgb(0.706, 0.706, 0.784),
            parent=camera.ui
        )
        self.ui_elements.append(self.class_desc_text)

        # Stat display (bottom-left)
        stat_y_start = -0.25
        stat_spacing = 0.08

        # HP
        hp_label = Text(
            text="HP:",
            position=(-0.45, stat_y_start),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.863, 0.863, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(hp_label)
        self.stat_texts['hp'] = Text(
            text="120",
            position=(-0.35, stat_y_start),
            origin=(0, 0),
            scale=1.8,
            color=color.rgb(0.392, 0.784, 0.471),
            parent=camera.ui
        )
        self.ui_elements.append(self.stat_texts['hp'])

        # Attack
        attack_label = Text(
            text="ATK:",
            position=(-0.45, stat_y_start - stat_spacing),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.863, 0.863, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(attack_label)
        self.stat_texts['attack'] = Text(
            text="12",
            position=(-0.35, stat_y_start - stat_spacing),
            origin=(0, 0),
            scale=1.8,
            color=color.rgb(1.0, 0.392, 0.392),
            parent=camera.ui
        )
        self.ui_elements.append(self.stat_texts['attack'])

        # Defense
        defense_label = Text(
            text="DEF:",
            position=(-0.45, stat_y_start - stat_spacing * 2),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.863, 0.863, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(defense_label)
        self.stat_texts['defense'] = Text(
            text="8",
            position=(-0.35, stat_y_start - stat_spacing * 2),
            origin=(0, 0),
            scale=1.8,
            color=color.rgb(0.392, 0.588, 1.0),
            parent=camera.ui
        )
        self.ui_elements.append(self.stat_texts['defense'])

        # Abilities (bottom-right)
        abilities_label = Text(
            text="ABILITIES:",
            position=(0.25, stat_y_start),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.863, 0.863, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(abilities_label)

        # Create 3 ability text slots
        for i in range(3):
            ability_text = Text(
                text=f"Ability {i+1}",
                position=(0.25, stat_y_start - stat_spacing * (i + 1)),
                origin=(0, 0),
                scale=1.3,
                color=color.rgb(0.588, 0.706, 1.0),
                parent=camera.ui
            )
            self.ability_texts.append(ability_text)
            self.ui_elements.append(ability_text)

        # Navigation arrows (dungeon-styled)
        self.left_arrow = DungeonButton(
            text="< PREV",
            scale=(0.15, 0.07),
            position=(-0.6, 0),
            parent=camera.ui,
            on_click=self._previous_class
        )
        self.ui_elements.append(self.left_arrow)

        self.right_arrow = DungeonButton(
            text="NEXT >",
            scale=(0.15, 0.07),
            position=(0.6, 0),
            parent=camera.ui,
            on_click=self._next_class
        )
        self.ui_elements.append(self.right_arrow)

        # Start button (dungeon-styled, larger)
        self.start_button = DungeonButton(
            text="START GAME",
            scale=(0.35, 0.09),
            position=(0, -0.42),
            parent=camera.ui,
            on_click=self._start_game
        )
        self.ui_elements.append(self.start_button)

        # Instructions
        instructions = Text(
            text="Arrow Keys: Navigate  |  Enter/Click: Start Game",
            position=(0, -0.48),
            origin=(0, 0),
            scale=1.0,
            color=color.rgb(0.471, 0.471, 0.51),
            parent=camera.ui
        )
        self.ui_elements.append(instructions)

    def _load_current_model(self):
        """Load and display the current class model"""
        # Clear previous model
        for class_type, model in self.class_models.items():
            if model:
                model.enabled = False

        # Load model if not cached
        if self.current_class not in self.class_models:
            self._create_class_model(self.current_class)

        # Show current model
        if self.current_class in self.class_models:
            self.class_models[self.current_class].enabled = True

    def _create_class_model(self, class_type: str):
        """Create a 3D model for the class"""
        # Import the appropriate player model
        if class_type == c.CLASS_WARRIOR:
            from graphics3d.players.warrior import create_warrior_model
            model_func = create_warrior_model
        elif class_type == c.CLASS_MAGE:
            from graphics3d.players.mage import create_mage_model
            model_func = create_mage_model
        elif class_type == c.CLASS_ROGUE:
            from graphics3d.players.rogue import create_rogue_model
            model_func = create_rogue_model
        elif class_type == c.CLASS_RANGER:
            from graphics3d.players.ranger import create_ranger_model
            model_func = create_ranger_model
        else:
            print(f"[ClassSelection] Unknown class type: {class_type}")
            return

        # Create model entity - scaled to comfortable viewing size (0.3125 = 50% of original 0.625)
        model = model_func(position=Vec3(0, 0, 0), scale=Vec3(0.3125, 0.3125, 0.3125))
        # NOTE: Do NOT override model.color - let child entities keep their individual colors
        model.rotation_y = 0
        model.rotation_z = 180  # Flip model right-side up

        # Position in front of camera at display height
        model.position = Vec3(0, self.model_display_height, -self.camera_distance)

        self.class_models[class_type] = model

        print(f"✓ Created model for {class_type} at position {model.position} with scale 0.3125")

    def _update_ui_for_class(self):
        """Update UI text and colors for current class"""
        # Get class data
        stats = c.CLASS_STATS.get(self.current_class, {})
        class_colors = {
            c.CLASS_WARRIOR: color.rgb(0.706, 0.235, 0.157),
            c.CLASS_MAGE: color.rgb(0.392, 0.588, 1.0),
            c.CLASS_ROGUE: color.rgb(0.706, 0.392, 1.0),
            c.CLASS_RANGER: color.rgb(0.392, 0.784, 0.392),
        }
        class_names = {
            c.CLASS_WARRIOR: "WARRIOR",
            c.CLASS_MAGE: "MAGE",
            c.CLASS_ROGUE: "ROGUE",
            c.CLASS_RANGER: "RANGER",
        }
        class_abilities = {
            c.CLASS_WARRIOR: ["Healing Touch", "Whirlwind", "Dash"],
            c.CLASS_MAGE: ["Fireball", "Frost Nova", "Healing Touch"],
            c.CLASS_ROGUE: ["Shadow Step", "Dash", "Healing Touch"],
            c.CLASS_RANGER: ["Fireball", "Dash", "Healing Touch"],
        }

        # Update class name
        self.class_name_text.text = class_names.get(self.current_class, "UNKNOWN")
        self.class_name_text.color = class_colors.get(self.current_class, color.white)

        # Update description
        self.class_desc_text.text = stats.get("description", "")

        # Update stats
        self.stat_texts['hp'].text = str(stats.get('hp', 0))
        self.stat_texts['attack'].text = str(stats.get('attack', 0))
        self.stat_texts['defense'].text = str(stats.get('defense', 0))

        # Update abilities
        abilities = class_abilities.get(self.current_class, [])
        for i, ability_text in enumerate(self.ability_texts):
            if i < len(abilities):
                ability_text.text = f"{i+1}. {abilities[i]}"
            else:
                ability_text.text = ""

    def _next_class(self):
        """Navigate to next class"""
        self.audio.play_ui_hover()
        self.current_class_index = (self.current_class_index + 1) % len(self.classes)
        self.current_class = self.classes[self.current_class_index]
        self._load_current_model()
        self._update_ui_for_class()
        # Reset drag state when switching classes
        self.is_dragging = False
        self.auto_rotate = True
        self.idle_timer = 0.0
        print(f"[ClassSelection] Selected: {self.current_class}")

    def _previous_class(self):
        """Navigate to previous class"""
        self.audio.play_ui_hover()
        self.current_class_index = (self.current_class_index - 1) % len(self.classes)
        self.current_class = self.classes[self.current_class_index]
        self._load_current_model()
        self._update_ui_for_class()
        # Reset drag state when switching classes
        self.is_dragging = False
        self.auto_rotate = True
        self.idle_timer = 0.0
        print(f"[ClassSelection] Selected: {self.current_class}")

    def _start_game(self):
        """Start game with selected class"""
        self.audio.play_ui_select()

        # Play voice line for selected class
        self.audio.play_voice(self.current_class, volume=1.0)

        print(f"[ClassSelection] Starting game with {self.current_class}")

        # Notify screen manager
        self.screen_manager.start_game_with_class(self.current_class)

    def update(self):
        """Update animations and input"""
        if not self.enabled:
            return

        dt = ursina_time.dt

        # Handle mouse drag rotation
        if mouse.left:
            if not self.is_dragging:
                # Start dragging
                self.is_dragging = True
                self.last_mouse_x = mouse.x
                self.auto_rotate = False
                self.idle_timer = 0.0
            else:
                # Continue dragging - calculate delta and rotate
                mouse_delta_x = mouse.x - self.last_mouse_x
                self.last_mouse_x = mouse.x

                # Apply rotation to current model
                if self.current_class in self.class_models:
                    model = self.class_models[self.current_class]
                    if model and model.enabled:
                        # Rotate based on horizontal drag
                        rotation_amount = mouse_delta_x * self.drag_sensitivity
                        model.rotation_y += rotation_amount
        else:
            if self.is_dragging:
                # Stop dragging
                self.is_dragging = False

            # Increment idle timer
            self.idle_timer += dt
            if self.idle_timer >= self.idle_timeout:
                # Resume auto-rotation after idle timeout
                self.auto_rotate = True

        # Auto-rotate model when not dragging
        if self.auto_rotate and not self.is_dragging:
            if self.current_class in self.class_models:
                model = self.class_models[self.current_class]
                if model and model.enabled:
                    model.rotation_y += self.model_rotation_speed * dt

        # Handle keyboard input
        if held_keys['left arrow'] or held_keys['a']:
            # Debounce by checking if we just changed
            if not hasattr(self, '_last_nav_time') or (ursina_time.time() - self._last_nav_time) > 0.3:
                self._previous_class()
                self._last_nav_time = ursina_time.time()

        if held_keys['right arrow'] or held_keys['d']:
            if not hasattr(self, '_last_nav_time') or (ursina_time.time() - self._last_nav_time) > 0.3:
                self._next_class()
                self._last_nav_time = ursina_time.time()

        if held_keys['enter'] or held_keys['space']:
            if not hasattr(self, '_last_start_time') or (ursina_time.time() - self._last_start_time) > 0.5:
                self._start_game()
                self._last_start_time = ursina_time.time()

    def show(self):
        """Show the class selection screen"""
        self.enabled = True

        # Reset drag state
        self.is_dragging = False
        self.auto_rotate = True
        self.idle_timer = 0.0

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Enable lighting
        if self.ambient_light:
            self.ambient_light.enabled = True
        if self.key_light:
            self.key_light.enabled = True
        if self.rim_light:
            self.rim_light.enabled = True

        # Show current model
        self._load_current_model()

        # Position camera to frame the character nicely
        camera.position = Vec3(0, self.camera_height, 0)

        # Make camera look at the model (at display height)
        model_look_at_pos = Vec3(0, self.model_display_height, -self.camera_distance)
        camera.look_at(model_look_at_pos)

        print(f"[ClassSelection] Screen shown")
        print(f"  Camera at: {camera.position}")
        print(f"  Looking at: {model_look_at_pos}")
        print(f"  Camera rotation: {camera.rotation}")

    def hide(self):
        """Hide the class selection screen"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        # Disable lighting (but don't destroy - we'll reuse)
        if self.ambient_light:
            self.ambient_light.enabled = False
        if self.key_light:
            self.key_light.enabled = False
        if self.rim_light:
            self.rim_light.enabled = False

        # Hide all models
        for model in self.class_models.values():
            if model:
                model.enabled = False

        print("[ClassSelection] Screen hidden")
