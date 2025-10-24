"""
3D Rendering Manager using Ursina Engine

This module handles all 3D rendering for the game, converting the 2D game state
into a 3D visualization while keeping all game logic unchanged.
"""

from typing import Dict, List, Optional, Tuple
from ursina import Entity, camera, Vec3, color as ursina_color, DirectionalLight, AmbientLight, PointLight, scene
import random
import math
import constants as c
from game import Game
from graphics3d.tiles import create_floor_mesh, create_wall_mesh, create_stairs_mesh, create_ceiling_mesh
from graphics3d.utils import world_to_3d_position
from graphics3d.enemies import create_enemy_model_3d, update_enemy_animation, create_health_bar_billboard, update_health_bar
from graphics3d.items import create_item_model_3d, update_item_animation
from animations3d import AnimationManager3D
from textures import get_fog_of_war_texture
import time
from logger import get_logger

log = get_logger()


class Renderer3D:
    """
    3D rendering manager using Ursina Engine
    Interfaces with the Game class to render dungeon, entities, and effects
    """

    def __init__(self, game: Game):
        """
        Initialize the 3D renderer

        Args:
            game: Game instance to render
        """
        self.game = game

        # Entity tracking dictionaries
        self.dungeon_entities: Dict[Tuple[int, int], List[Entity]] = {}  # (x, y) -> [entities at that position]
        self.tile_visibility_cache: Dict[Tuple[int, int], str] = {}  # (x, y) -> last visibility state
        self.fog_entities: Dict[Tuple[int, int], Entity] = {}  # (x, y) -> fog plane entity
        self.player_entity: Optional[Entity] = None
        self.enemy_entities: Dict[int, Entity] = {}  # enemy id -> Entity
        self.item_entities: Dict[int, Entity] = {}   # item id -> Entity

        # Enemy model pool (for performance - eliminates lag spikes)
        self.enemy_model_pool: Dict[str, List[Dict]] = {}  # enemy_type -> [pool entries]
        self.pool_initialized = False  # Track if pool has been created for current level

        # Lighting
        self.ambient_light: Optional[AmbientLight] = None
        self.sun_light: Optional[DirectionalLight] = None
        self.player_light: Optional[PointLight] = None

        # Camera state
        self.camera_yaw = 0.0  # Camera yaw (set by GameController)
        self.camera_pitch = c.DEFAULT_CAMERA_PITCH  # Camera pitch (vertical tilt)
        self.camera_initialized = False  # Track if camera has been positioned initially
        self.base_camera_pos = Vec3(0, 0, 0)  # Store base camera position for shake

        # 3D Animation Manager
        self.animation_manager = AnimationManager3D()

        # Fog of War
        self.fog_texture = None  # Lazy-loaded fog texture
        self.fog_animation_time = 0.0  # Track time for UV animation

        # Setup
        self.setup_camera()
        self.setup_lighting()

    def setup_camera(self):
        """Configure first-person camera"""
        if c.USE_FIRST_PERSON:
            camera.position = (0, c.EYE_HEIGHT, 0)
            camera.rotation_x = 0  # Look horizontally
            camera.fov = c.CAMERA_FOV_FPS
            camera.clip_plane_near = 0.05  # Reduce near clipping to prevent wall/floor disappearing
            log.debug(f"First-person camera configured: eye_height={c.EYE_HEIGHT}, fov={c.CAMERA_FOV_FPS}°", "renderer")

            # Apply barrel distortion shader if enabled
            if c.BARREL_DISTORTION_STRENGTH > 0.0:
                from shaders import create_barrel_distortion_shader
                barrel_shader = create_barrel_distortion_shader(strength=c.BARREL_DISTORTION_STRENGTH)
                camera.shader = barrel_shader
                log.debug(f"Barrel distortion shader applied (strength={c.BARREL_DISTORTION_STRENGTH})", "renderer")
        else:
            # Third-person (legacy)
            camera.position = (0, c.CAMERA_HEIGHT, -c.CAMERA_DISTANCE)
            camera.rotation_x = c.CAMERA_ANGLE
            camera.fov = c.FOV
            log.debug(f"Third-person camera configured", "renderer")

    def setup_lighting(self):
        """Set up basic 3D lighting with fog of war ambiance"""
        # Ambient light (general illumination) - IMPROVED for better visibility
        self.ambient_light = AmbientLight(color=(0.4, 0.4, 0.45, 1))

        # Directional light (sun/moon) - IMPROVED for better depth perception
        self.sun_light = DirectionalLight(
            position=(10, 20, 10),
            rotation=(45, 45, 0),
            color=(0.6, 0.6, 0.65, 1)  # Brighter blue-gray light
        )

        # Point light following player (torch effect) - BRIGHTER for better illumination
        self.player_light = PointLight(
            color=(1.5, 1.2, 0.8, 1),  # Brighter, warmer torch light
            position=(0, 2, 0)
        )

        # Atmospheric fog for depth and mystery - REDUCED for better visibility
        scene.fog_color = ursina_color.rgb(0.1, 0.1, 0.15)  # Dark blue-gray
        scene.fog_density = (8, 20)  # Start at 8 units, full fog at 20 units

        log.debug("Lighting configured with improved visibility (ambient: 0.4, directional: 0.6)", "renderer")
        log.debug("Atmospheric fog enabled (density: 8-20 units)", "renderer")

        # NOTE: Auto shader generation DISABLED - using custom toon shader for walls
        # Walls use custom toon shader with exaggerated normal mapping for cartoon effect
        log.debug("Custom toon shader will be applied to walls", "renderer")

    def render_dungeon(self):
        """
        Render the entire dungeon from game.dungeon

        Clears old dungeon meshes and creates new ones based on current level.
        """
        # Clear old dungeon entities
        for pos, entities in self.dungeon_entities.items():
            for entity in entities:
                entity.disable()  # Disable instead of destroy for better performance
        self.dungeon_entities.clear()
        self.tile_visibility_cache.clear()

        # Clear old fog entities from previous level
        for fog_entity in self.fog_entities.values():
            fog_entity.disable()
        self.fog_entities.clear()

        # Clear old stairs glow effects from previous level
        self.animation_manager.clear_stairs_glow_effects()

        if not self.game.dungeon:
            return

        # Get biome colors (RGB tuples for 3D rendering)
        biome = self.game.dungeon.biome
        biome_colors = c.BIOME_COLORS_RGB.get(biome, c.BIOME_COLORS_RGB[c.BIOME_DUNGEON])
        floor_color = biome_colors["floor"]
        wall_color = biome_colors["wall"]
        stairs_color = biome_colors["stairs"]

        # Render tiles
        for y in range(self.game.dungeon.height):
            for x in range(self.game.dungeon.width):
                tile = self.game.dungeon.get_tile(x, y)
                tile_entities = []

                if tile == c.TILE_FLOOR:
                    # Check adjacent tiles for wall detection (for edge-based shadows)
                    has_wall_north = self.game.dungeon.get_tile(x, y - 1) == c.TILE_WALL
                    has_wall_south = self.game.dungeon.get_tile(x, y + 1) == c.TILE_WALL
                    has_wall_east = self.game.dungeon.get_tile(x + 1, y) == c.TILE_WALL
                    has_wall_west = self.game.dungeon.get_tile(x - 1, y) == c.TILE_WALL

                    # Render floor with wall adjacency info
                    entity = create_floor_mesh(x, y, biome, floor_color,
                                              has_wall_north, has_wall_south,
                                              has_wall_east, has_wall_west)
                    tile_entities.append(entity)

                    # Render ceiling above floor with wall adjacency info
                    ceiling_entity = create_ceiling_mesh(x, y, biome, wall_color,
                                                        has_wall_north, has_wall_south,
                                                        has_wall_east, has_wall_west)
                    tile_entities.append(ceiling_entity)

                elif tile == c.TILE_WALL:
                    entity = create_wall_mesh(x, y, biome, wall_color)
                    tile_entities.append(entity)

                elif tile == c.TILE_STAIRS:
                    # Check adjacent tiles for wall detection (for edge-based shadows)
                    has_wall_north = self.game.dungeon.get_tile(x, y - 1) == c.TILE_WALL
                    has_wall_south = self.game.dungeon.get_tile(x, y + 1) == c.TILE_WALL
                    has_wall_east = self.game.dungeon.get_tile(x + 1, y) == c.TILE_WALL
                    has_wall_west = self.game.dungeon.get_tile(x - 1, y) == c.TILE_WALL

                    # Create partial floor on back half (stairs take front half)
                    # This fills the black void where stairs don't reach
                    from graphics3d.tiles import FLOOR_TEXTURES, CORNER_SHADOW_SHADER
                    pos = world_to_3d_position(x, y, 0)

                    # Get floor texture and color (same as regular floors)
                    biome_textures = FLOOR_TEXTURES.get(biome, FLOOR_TEXTURES[c.BIOME_DUNGEON])
                    variant_idx = (x * 7 + y * 13) % len(biome_textures)
                    floor_texture = biome_textures[variant_idx]

                    floor_color_converted = ursina_color.rgb(floor_color[0] * 255, floor_color[1] * 255, floor_color[2] * 255)
                    floor_tint = ursina_color.rgb(
                        min(255, 0.3 * 255 + floor_color_converted.r * 255 * 0.7),
                        min(255, 0.3 * 255 + floor_color_converted.g * 255 * 0.7),
                        min(255, 0.3 * 255 + floor_color_converted.b * 255 * 0.7)
                    )

                    # Partial floor plane (back half only - positive Z)
                    partial_floor = Entity(
                        model='plane',
                        position=(pos[0], pos[1], pos[2] + 0.25),  # Shift back by quarter tile
                        scale=(1, 1, 0.5),  # Half depth
                        color=floor_tint,
                        texture=floor_texture,
                        collider=None
                    )
                    partial_floor.shader = CORNER_SHADOW_SHADER
                    # Pass wall adjacency info to shader
                    partial_floor.set_shader_input('has_wall_north', 1.0 if has_wall_north else 0.0)
                    partial_floor.set_shader_input('has_wall_south', 1.0 if has_wall_south else 0.0)
                    partial_floor.set_shader_input('has_wall_east', 1.0 if has_wall_east else 0.0)
                    partial_floor.set_shader_input('has_wall_west', 1.0 if has_wall_west else 0.0)
                    tile_entities.append(partial_floor)

                    # Create descending staircase with biome floor texture
                    stairs_entity = create_stairs_mesh(x, y, biome, floor_color)
                    tile_entities.append(stairs_entity)

                    # Add glowing particle beam effect for stairs (dungeon exit)
                    self.animation_manager.add_stairs_glow_effect(x, y)

                    # Render ceiling above stairs with wall adjacency info
                    ceiling_entity = create_ceiling_mesh(x, y, biome, wall_color,
                                                        has_wall_north, has_wall_south,
                                                        has_wall_east, has_wall_west)
                    tile_entities.append(ceiling_entity)

                # Store entities by position for fog of war updates
                if tile_entities:
                    self.dungeon_entities[(x, y)] = tile_entities

        # Preload enemy models for this level (eliminates lag spikes)
        self.preload_enemy_models()

        # Summarize dungeon generation in one line (INFO level for important events)
        if self.game.player:
            log.info(f"Level {self.game.current_level} generated - {self.game.dungeon.width}x{self.game.dungeon.height} {self.game.dungeon.biome} dungeon ({len(self.dungeon_entities)} tiles)", "game")
        else:
            log.debug(f"Rendered {len(self.dungeon_entities)} tiles", "renderer")

    def render_player(self):
        """
        Render or update the player entity
        """
        if not self.game.player:
            return

        # Player position
        pos = world_to_3d_position(
            self.game.player.x,
            self.game.player.y,
            c.PLAYER_HEIGHT / 2
        )

        # Get class color
        class_colors = {
            c.CLASS_WARRIOR: (100, 200, 255),   # Blue
            c.CLASS_MAGE: (150, 100, 255),      # Purple
            c.CLASS_ROGUE: (80, 80, 80),        # Gray
            c.CLASS_RANGER: (100, 220, 80),     # Green
        }

        color_rgb = class_colors.get(self.game.player.class_type, (100, 200, 255))
        player_color = ursina_color.rgb(color_rgb[0] / 255, color_rgb[1] / 255, color_rgb[2] / 255)

        # Create or update player entity
        if self.player_entity is None:
            if c.USE_FIRST_PERSON:
                # First-person: Create invisible player cube (or skip entirely)
                self.player_entity = Entity(
                    model='cube',
                    color=player_color,
                    scale=(c.ENTITY_SCALE, c.PLAYER_HEIGHT, c.ENTITY_SCALE),
                    position=pos,
                    visible=False  # Hide player in first-person
                )
                log.debug("Created player entity (INVISIBLE - first-person mode)", "renderer")
            else:
                # Third-person: Visible player cube
                self.player_entity = Entity(
                    model='cube',
                    color=player_color,
                    scale=(c.ENTITY_SCALE, c.PLAYER_HEIGHT, c.ENTITY_SCALE),
                    position=pos,
                    texture='white_cube'
                )
                log.debug(f"Created player cube at {pos}, class: {self.game.player.class_type}", "renderer")

            # Position camera immediately after creating player
            self.update_camera()
            log.debug(f"Camera positioned at {camera.position}", "renderer")
        else:
            # Update position
            self.player_entity.position = pos

        # Update player light position
        if self.player_light:
            self.player_light.position = (pos[0], pos[1] + 2, pos[2])

    def render_enemies(self):
        """
        Render or update all enemy entities with health bars
        Only renders enemies in visible tiles (FOV system)
        """
        if not self.game.enemies:
            return

        # Track which enemies currently exist AND are visible
        current_enemy_ids = set()

        for enemy in self.game.enemies:
            enemy_id = id(enemy)

            # FOG OF WAR: Only render enemies in visible tiles
            if self.game.visibility_map and not self.game.visibility_map.is_visible(enemy.x, enemy.y):
                # Enemy not visible - hide if it exists, skip creation if it doesn't
                if enemy_id in self.enemy_entities:
                    self.enemy_entities[enemy_id]['model'].visible = False
                    self.enemy_entities[enemy_id]['health_bar'].visible = False
                continue

            # Enemy is visible
            current_enemy_ids.add(enemy_id)

            # Calculate 3D position
            pos = world_to_3d_position(enemy.x, enemy.y, 0.5)

            # Create enemy model if it doesn't exist
            if enemy_id not in self.enemy_entities:
                # Get dungeon level for creature scaling
                dungeon_level = getattr(self.game, 'current_level', 1)

                # Get enemy from pool (or create new if pool exhausted/disabled)
                enemy_data = self.get_from_pool(
                    enemy.enemy_type,
                    Vec3(*pos),
                    dungeon_level
                )

                # Update health bar to current HP
                hp_pct = enemy.hp / enemy.max_hp
                update_health_bar(enemy_data['health_bar'], hp_pct)

                # Store references
                self.enemy_entities[enemy_id] = enemy_data

                log.debug(f"Created {enemy.enemy_type} at ({enemy.x}, {enemy.y})", "renderer")
            else:
                # Update existing enemy position
                enemy_data = self.enemy_entities[enemy_id]
                enemy_data['model'].position = pos
                enemy_data['model'].visible = True  # Make visible if was hidden
                enemy_data['health_bar'].visible = True

                # Update health bar
                hp_pct = enemy.hp / enemy.max_hp
                update_health_bar(enemy_data['health_bar'], hp_pct)

        # Remove entities for enemies that no longer exist (died)
        dead_enemy_ids = set(self.enemy_entities.keys()) - current_enemy_ids
        for enemy_id in dead_enemy_ids:
            enemy_data = self.enemy_entities[enemy_id]
            enemy_type = enemy_data.get('enemy_type', 'enemy')

            # Return to pool (or destroy if pool disabled)
            self.return_to_pool(enemy_data)

            del self.enemy_entities[enemy_id]
            log.debug(f"Removed dead {enemy_type}", "renderer")

    def render_items(self):
        """
        Render or update all item entities with floating/rotation animations
        Only renders items in visible tiles (FOV system)
        """
        if not self.game.items:
            return

        # Track which items currently exist AND are visible
        current_item_ids = set()

        for item in self.game.items:
            item_id = id(item)

            # FOG OF WAR: Only render items in visible tiles
            if self.game.visibility_map and not self.game.visibility_map.is_visible(item.x, item.y):
                # Item not visible - hide if it exists, skip creation if it doesn't
                if item_id in self.item_entities:
                    self.item_entities[item_id].visible = False
                continue

            # Item is visible
            current_item_ids.add(item_id)

            # Calculate 3D position (items float above ground)
            pos = world_to_3d_position(item.x, item.y, 0.5)

            # Create item model if it doesn't exist
            if item_id not in self.item_entities:
                item_model = create_item_model_3d(item.item_type, item.rarity, Vec3(*pos))

                # Store reference
                self.item_entities[item_id] = item_model

                log.debug(f"Created {item.rarity} {item.item_type} at ({item.x}, {item.y})", "renderer")
            else:
                # Update existing item position (base position, animation handles float)
                item_entity = self.item_entities[item_id]
                # Only update X and Z, Y is controlled by float animation
                # pos is a tuple (x, y, z), not a Vec3
                item_entity.x = pos[0]
                item_entity.z = pos[2]
                item_entity.visible = True  # Make visible if was hidden

        # Remove entities for items that no longer exist (picked up)
        picked_up_item_ids = set(self.item_entities.keys()) - current_item_ids
        for item_id in picked_up_item_ids:
            item_entity = self.item_entities[item_id]
            item_entity.disable()  # Disable the model
            del self.item_entities[item_id]
            log.debug("Picked up item", "renderer")

    def preload_enemy_models(self, enemy_types: Optional[List[str]] = None):
        """
        Pre-create enemy models for the current level to eliminate lag spikes.
        Creates a pool of reusable models hidden offscreen.

        Args:
            enemy_types: List of enemy types to preload. If None, preloads all types that spawn on current level.
        """
        if not c.ENABLE_ENEMY_POOL:
            return

        # Determine which enemy types to preload
        if enemy_types is None:
            # Auto-detect based on current level
            dungeon_level = getattr(self.game, 'current_level', 1)

            # Determine which enemies spawn at this level (based on game logic)
            # ENEMY_STARTLE and ENEMY_SLIME: levels 1-5
            # ENEMY_SKELETON: levels 2-14
            # ENEMY_ORC: levels 4-19
            # ENEMY_DEMON: levels 6-25
            # ENEMY_DRAGON: levels 10-25
            enemy_types = []
            if dungeon_level <= 5:
                enemy_types.extend([c.ENEMY_STARTLE, c.ENEMY_SLIME])
            if 2 <= dungeon_level <= 14:
                enemy_types.append(c.ENEMY_SKELETON)
            if 4 <= dungeon_level <= 19:
                enemy_types.append(c.ENEMY_ORC)
            if 6 <= dungeon_level:
                enemy_types.append(c.ENEMY_DEMON)
            if 10 <= dungeon_level:
                enemy_types.append(c.ENEMY_DRAGON)

        if not enemy_types:
            return

        dungeon_level = getattr(self.game, 'current_level', 1)

        # Clear existing pool
        self.clear_enemy_pool()

        # Create pool for each enemy type
        for enemy_type in enemy_types:
            pool = []

            for i in range(c.ENEMY_POOL_SIZE_PER_TYPE):
                # Create model offscreen and hidden
                offscreen_pos = Vec3(0, -100, 0)  # Far below the map

                try:
                    enemy_model = create_enemy_model_3d(
                        enemy_type,
                        offscreen_pos,
                        dungeon_level=dungeon_level
                    )

                    # Extract root entity
                    if hasattr(enemy_model, 'root'):
                        root_entity = enemy_model.root
                        creature_obj = enemy_model
                    else:
                        root_entity = enemy_model
                        creature_obj = None

                    # Hide model
                    root_entity.visible = False

                    # Create health bar (also hidden)
                    health_bar = create_health_bar_billboard(1.0)
                    health_bar.parent = root_entity
                    health_bar.visible = False

                    # Add to pool
                    pool.append({
                        'creature': creature_obj,
                        'model': root_entity,
                        'health_bar': health_bar,
                        'enemy_type': enemy_type,
                        'in_use': False  # Track if this instance is currently being used
                    })

                except Exception as e:
                    log.error(f"Failed to preload {enemy_type} #{i}: {e}", "renderer")

            self.enemy_model_pool[enemy_type] = pool

        self.pool_initialized = True

    def get_from_pool(self, enemy_type: str, position: Vec3, dungeon_level: int):
        """
        Get an enemy model from the pool (or create new if pool exhausted).

        Args:
            enemy_type: Type of enemy to get
            position: 3D world position for the enemy
            dungeon_level: Current dungeon level (for fallback creation)

        Returns:
            Dict with 'creature', 'model', 'health_bar', 'enemy_type' keys
        """
        if not c.ENABLE_ENEMY_POOL or enemy_type not in self.enemy_model_pool:
            # Pool disabled or this type not preloaded - create new
            return self._create_enemy_fresh(enemy_type, position, dungeon_level)

        # Find an available instance in the pool
        pool = self.enemy_model_pool[enemy_type]
        for entry in pool:
            if not entry['in_use']:
                # Found available instance - activate it
                entry['in_use'] = True
                entry['model'].position = position
                entry['model'].visible = True
                entry['health_bar'].visible = True

                # Reset health bar to full
                update_health_bar(entry['health_bar'], 1.0)

                log.debug(f"Reused {enemy_type} from pool", "renderer")
                return entry

        # Pool exhausted - create new instance (rare case)
        log.warning(f"Pool exhausted for {enemy_type}, creating new instance", "renderer")
        return self._create_enemy_fresh(enemy_type, position, dungeon_level)

    def return_to_pool(self, enemy_data: Dict):
        """
        Return an enemy model to the pool for reuse.

        Args:
            enemy_data: Enemy entity data dict (with 'creature', 'model', 'health_bar', 'enemy_type')
        """
        if not c.ENABLE_ENEMY_POOL:
            # Pool disabled - just destroy the model
            enemy_data['model'].disable()
            enemy_data['health_bar'].disable()
            return

        enemy_type = enemy_data.get('enemy_type')

        # Check if this enemy type has a pool
        if enemy_type not in self.enemy_model_pool:
            # No pool for this type - destroy it
            enemy_data['model'].disable()
            enemy_data['health_bar'].disable()
            return

        # Find this instance in the pool
        pool = self.enemy_model_pool[enemy_type]
        for entry in pool:
            if entry['model'] is enemy_data['model']:
                # Found it - mark as available and hide
                entry['in_use'] = False
                entry['model'].visible = False
                entry['health_bar'].visible = False
                entry['model'].position = Vec3(0, -100, 0)  # Move offscreen
                log.debug(f"Returned {enemy_type} to pool", "renderer")
                return

        # Not in pool (was created fresh due to exhaustion) - destroy it
        log.debug(f"Destroying non-pooled {enemy_type}", "renderer")
        enemy_data['model'].disable()
        enemy_data['health_bar'].disable()

    def _create_enemy_fresh(self, enemy_type: str, position: Vec3, dungeon_level: int) -> Dict:
        """
        Create a new enemy model (fallback when pool disabled or exhausted).

        Args:
            enemy_type: Type of enemy to create
            position: 3D world position
            dungeon_level: Current dungeon level

        Returns:
            Dict with 'creature', 'model', 'health_bar', 'enemy_type' keys
        """
        enemy_model = create_enemy_model_3d(
            enemy_type,
            position,
            dungeon_level=dungeon_level
        )

        # Extract root entity
        if hasattr(enemy_model, 'root'):
            root_entity = enemy_model.root
            creature_obj = enemy_model
        else:
            root_entity = enemy_model
            creature_obj = None

        # Create health bar
        health_bar = create_health_bar_billboard(1.0)
        health_bar.parent = root_entity

        return {
            'creature': creature_obj,
            'model': root_entity,
            'health_bar': health_bar,
            'enemy_type': enemy_type,
            'in_use': True  # Mark as in use (not pooled)
        }

    def clear_enemy_pool(self):
        """Clear and destroy all models in the enemy pool."""
        for enemy_type, pool in self.enemy_model_pool.items():
            for entry in pool:
                if entry['model']:
                    entry['model'].disable()
                if entry['health_bar']:
                    entry['health_bar'].disable()

        self.enemy_model_pool.clear()
        self.pool_initialized = False

    def render_entities(self):
        """
        Render or update all game entities (player, enemies, items)
        """
        self.render_player()
        self.render_enemies()
        self.render_items()

    def create_fog_plane(self, x: int, y: int) -> Entity:
        """
        Create a fog-of-war wall entity for an unexplored tile.

        Fog cubes are oversized (1.15-1.25x) to create natural bleeding
        into adjacent tiles, combined with the radial alpha gradient texture.

        Args:
            x, y: Grid coordinates

        Returns:
            Entity representing fog wall
        """
        # Lazy-load fog texture on first use
        if self.fog_texture is None:
            print("Generating fog-of-war texture (512x512 with radial alpha gradient)...")
            self.fog_texture = get_fog_of_war_texture(size=512)
            print("✓ Fog texture generated")

        # Position fog wall at center height (like walls)
        pos = world_to_3d_position(x, y, c.WALL_HEIGHT / 2)

        # Random scale variation for natural fog variation (1.15-1.25x)
        # This makes fog extend 15-25% beyond its grid square (7.5-12.5% per side)
        random_scale = random.uniform(1.15, 1.25)

        # Create semi-transparent vertical fog wall (oversized cube)
        fog_wall = Entity(
            model='cube',
            texture=self.fog_texture,
            position=pos,
            scale=(random_scale, c.WALL_HEIGHT, random_scale),  # Oversized for fog bleeding
            color=ursina_color.white,
            alpha=0.85,  # Semi-transparent for mystery effect
            collider=None  # No collision
        )

        return fog_wall

    def update_tile_visibility(self):
        """
        Update tile appearance based on fog of war visibility state

        - VISIBLE tiles: Full brightness, no fog
        - EXPLORED tiles: Darkened (0.3x brightness), no fog
        - UNEXPLORED tiles: Hidden tiles, visible fog plane

        PERFORMANCE: Distance culling - only render tiles within render distance
        """
        if not self.game.visibility_map or not self.game.dungeon:
            return

        if not self.game.player:
            return

        # Calculate render distance (vision radius + margin)
        render_distance = c.PLAYER_VISION_RADIUS + c.RENDER_DISTANCE_MARGIN

        # Only update tiles that changed visibility state (optimization)
        for (x, y), entities in self.dungeon_entities.items():
            # PERFORMANCE: Distance culling - disable tiles beyond render distance
            dx = abs(x - self.game.player.x)
            dy = abs(y - self.game.player.y)

            if dx > render_distance or dy > render_distance:
                # Beyond render distance - disable all entities and fog
                for entity in entities:
                    entity.visible = False

                # Hide fog for distant tiles
                if (x, y) in self.fog_entities:
                    self.fog_entities[(x, y)].visible = False

                continue  # Skip visibility processing for distant tiles

            # Get current visibility state
            vis_state = self.game.visibility_map.get_state(x, y)

            # Check if state changed (optimization - skip if no change)
            cached_state = self.tile_visibility_cache.get((x, y))
            if cached_state == vis_state:
                continue  # No change, skip update

            # Update cache
            self.tile_visibility_cache[(x, y)] = vis_state

            # Apply visibility changes to all entities at this position
            for entity in entities:
                if vis_state == c.VISIBILITY_VISIBLE:
                    # Visible: Full brightness
                    entity.visible = True
                    entity.color = ursina_color.white  # Reset to full brightness

                elif vis_state == c.VISIBILITY_EXPLORED:
                    # Explored: Darkened
                    entity.visible = True
                    entity.color = ursina_color.rgb(0.3, 0.3, 0.35)  # Dark blue-gray tint

                elif vis_state == c.VISIBILITY_UNEXPLORED:
                    # Unexplored: Hidden
                    entity.visible = False

            # Fog plane handling
            if vis_state == c.VISIBILITY_UNEXPLORED:
                # PERFORMANCE: FOG_EDGE_ONLY - only show fog at boundary of explored area
                should_show_fog = True

                if c.FOG_EDGE_ONLY:
                    # Check if this unexplored tile is adjacent to any explored/visible tile
                    # (Only create fog at the "edge" of explored area, not deep in unexplored territory)
                    adjacent_tiles = [
                        (x - 1, y),  # West
                        (x + 1, y),  # East
                        (x, y - 1),  # North
                        (x, y + 1),  # South
                    ]

                    # Check if any adjacent tile is explored or visible
                    has_explored_neighbor = False
                    for ax, ay in adjacent_tiles:
                        neighbor_state = self.game.visibility_map.get_state(ax, ay)
                        if neighbor_state in [c.VISIBILITY_EXPLORED, c.VISIBILITY_VISIBLE]:
                            has_explored_neighbor = True
                            break

                    should_show_fog = has_explored_neighbor

                # Create or show fog plane only if at edge
                if should_show_fog:
                    if (x, y) not in self.fog_entities:
                        # Create new fog plane
                        self.fog_entities[(x, y)] = self.create_fog_plane(x, y)
                    else:
                        # Show existing fog plane
                        self.fog_entities[(x, y)].visible = True
                else:
                    # Not at edge - hide fog
                    if (x, y) in self.fog_entities:
                        self.fog_entities[(x, y)].visible = False

            else:
                # Hide fog plane for explored/visible tiles
                if (x, y) in self.fog_entities:
                    self.fog_entities[(x, y)].visible = False

    def find_enemy_in_front(self, camera_yaw: float) -> Optional[Tuple[float, float, float]]:
        """
        Check if there's an enemy in the tile directly in front of the player

        Args:
            camera_yaw: Current camera yaw angle in degrees

        Returns:
            Tuple of (x, y, z) 3D position of enemy in front, or None
        """
        if not self.game.player or not self.game.enemies:
            return None

        # Get player position
        player_x = self.game.player.x
        player_y = self.game.player.y

        # Calculate the tile directly in front based on camera yaw
        # Round yaw to nearest 90° for grid-aligned directions
        yaw = round(camera_yaw / 90) * 90 % 360

        # Map yaw to grid offsets (same as movement system)
        direction_map = {
            0: (0, 1),     # South (+Y grid)
            90: (1, 0),    # East (+X grid)
            180: (0, -1),  # North (-Y grid)
            270: (-1, 0),  # West (-X grid)
        }

        offset_x, offset_y = direction_map.get(yaw, (0, 1))
        target_x = player_x + offset_x
        target_y = player_y + offset_y

        # Check if any enemy is at that position
        for enemy in self.game.enemies:
            if enemy.x == target_x and enemy.y == target_y:
                # Check if enemy is visible (fog of war)
                if self.game.visibility_map and not self.game.visibility_map.is_visible(enemy.x, enemy.y):
                    continue

                # Enemy found! Return its 3D position
                from graphics3d.utils import world_to_3d_position
                return world_to_3d_position(enemy.x, enemy.y, 0.5)

        return None

    def trigger_enemy_attack(self, enemy_id: int):
        """
        Trigger attack animation for an enemy (DNA creatures only).

        Args:
            enemy_id: Python id() of the enemy object
        """
        if enemy_id not in self.enemy_entities:
            return

        enemy_data = self.enemy_entities[enemy_id]
        creature = enemy_data.get('creature')

        if creature and hasattr(creature, 'start_attack'):
            # Get player position as attack target
            if self.game.player:
                player_pos = Vec3(
                    float(self.game.player.x),
                    0.5,  # Mid-height
                    float(self.game.player.y)
                )
                creature.start_attack(player_pos)
                log.debug(f"Attack animation for {enemy_data['enemy_type']}", "renderer")

    def update_camera(self):
        """
        Update camera position and rotation
        - First-person: Camera at player position, rotate based on yaw
        - Third-person: Camera follows behind player
        """
        if not self.game.player:
            return

        player_x = float(self.game.player.x)
        player_y = float(self.game.player.y)

        if c.USE_FIRST_PERSON:
            # First-person with over-the-shoulder offset
            # Calculate backward offset based on camera yaw
            import math
            yaw_rad = math.radians(self.camera_yaw)

            # Camera faces forward, so backward offset is opposite of forward direction
            # In Ursina: yaw 0° = +Z (South), 90° = +X (East), 180° = -Z (North), 270° = -X (West)
            # Backward offset is negative of forward direction
            back_offset_x = -math.sin(yaw_rad) * c.CAMERA_BACK_OFFSET
            back_offset_z = -math.cos(yaw_rad) * c.CAMERA_BACK_OFFSET

            cam_x = player_x + back_offset_x
            cam_y = c.EYE_HEIGHT
            cam_z = player_y + back_offset_z

            # On first call, jump directly to position
            if not self.camera_initialized:
                self.base_camera_pos = Vec3(cam_x, cam_y, cam_z)
                camera.position = self.base_camera_pos
                camera.rotation_y = self.camera_yaw
                self.camera_initialized = True
                print(f"✓ First-person camera initialized at {camera.position}")
            else:
                # Update position (instant snap in first-person for precise control)
                self.base_camera_pos = Vec3(cam_x, cam_y, cam_z)

            # Apply screen shake offset
            shake_offset = self.animation_manager.get_screen_shake_offset()
            camera.position = self.base_camera_pos + shake_offset

            # Set rotation based on yaw and pitch
            camera.rotation = (self.camera_pitch, self.camera_yaw, 0)

        else:
            # Third-person: Camera follows behind player
            cam_x = player_x
            cam_y = c.CAMERA_HEIGHT
            cam_z = player_y - c.CAMERA_DISTANCE

            # On first call, jump directly to position
            if not self.camera_initialized:
                self.base_camera_pos = Vec3(cam_x, cam_y, cam_z)
                camera.position = self.base_camera_pos
                self.camera_initialized = True
                print(f"✓ Third-person camera initialized at {camera.position}")
            else:
                # Smooth interpolation for third-person
                smooth_factor = 0.3
                self.base_camera_pos = Vec3(
                    self.base_camera_pos.x + (cam_x - self.base_camera_pos.x) * smooth_factor,
                    self.base_camera_pos.y + (cam_y - self.base_camera_pos.y) * smooth_factor,
                    self.base_camera_pos.z + (cam_z - self.base_camera_pos.z) * smooth_factor
                )

            # Apply screen shake offset
            shake_offset = self.animation_manager.get_screen_shake_offset()
            camera.position = self.base_camera_pos + shake_offset

            # Look at player
            look_at_pos = Vec3(player_x, c.PLAYER_HEIGHT / 2, player_y) + shake_offset
            camera.look_at(look_at_pos)

    def update(self, dt: float):
        """
        Update renderer state (called every frame)

        Args:
            dt: Delta time since last frame
        """
        # Update entity positions
        self.render_entities()

        # Update tile visibility (fog of war)
        self.update_tile_visibility()

        # Update fog-of-war animation (UV scrolling) - PERFORMANCE: Disable if not needed
        if c.ENABLE_FOG_ANIMATION:
            self.fog_animation_time += dt * 0.08  # Slow scroll speed
            for fog_entity in self.fog_entities.values():
                if fog_entity.visible:
                    # Scroll UV coordinates to create swirling motion
                    # Use sine/cosine for circular motion effect
                    offset_x = self.fog_animation_time * 0.3
                    offset_y = self.fog_animation_time * 0.2

                    # Set texture offset (Ursina uses texture_offset for UV scrolling)
                    fog_entity.texture_offset = (offset_x, offset_y)

        # Update enemy animations
        for enemy_id, enemy_data in self.enemy_entities.items():
            # Get camera position for DNA creatures
            camera_pos = Vec3(camera.position) if camera else None

            # Make enemy face the player
            if self.game and self.game.player and enemy_data.get('model'):
                # Get player position in 3D space
                player_pos = Vec3(self.game.player.x, 0, self.game.player.y)
                # Get enemy position
                enemy_pos = enemy_data['model'].position
                # Calculate direction vector (XZ plane only)
                direction = player_pos - enemy_pos
                # Calculate angle in degrees (atan2 gives angle from Z-axis)
                # Add 180 degrees because creatures' default "forward" is -Z direction
                angle = math.degrees(math.atan2(direction.x, direction.z)) + 180
                # Apply rotation to make enemy face player
                enemy_data['model'].rotation_y = angle

            # For DNA creatures, pass the creature object; for legacy, pass the model entity
            animation_target = enemy_data.get('creature') or enemy_data['model']

            update_enemy_animation(
                animation_target,
                enemy_data['enemy_type'],
                dt,
                camera_position=camera_pos
            )

        # Update item animations (floating and rotation)
        for item_id, item_entity in self.item_entities.items():
            update_item_animation(item_entity, dt)

        # Update 3D particle animations
        self.animation_manager.update(dt)

        # Update camera (includes screen shake)
        self.update_camera()

    def cleanup(self):
        """
        Clean up all 3D entities and resources
        """
        # Destroy dungeon
        for pos, entities in self.dungeon_entities.items():
            for entity in entities:
                entity.disable()
        self.dungeon_entities.clear()
        self.tile_visibility_cache.clear()

        # Destroy fog entities
        for fog_entity in self.fog_entities.values():
            fog_entity.disable()
        self.fog_entities.clear()

        # Destroy player
        if self.player_entity:
            self.player_entity.disable()
            self.player_entity = None

        # Destroy enemies
        for enemy_id, enemy_data in self.enemy_entities.items():
            enemy_data['model'].disable()
            enemy_data['health_bar'].disable()
        self.enemy_entities.clear()

        # Clear enemy pool
        self.clear_enemy_pool()

        # Destroy items
        for item_id, item_entity in self.item_entities.items():
            item_entity.disable()
        self.item_entities.clear()

        # Destroy lights
        if self.ambient_light:
            self.ambient_light.disable()
        if self.sun_light:
            self.sun_light.disable()
        if self.player_light:
            self.player_light.disable()

        # Clean up animations
        if self.animation_manager:
            self.animation_manager.clear_all()

        print("3D renderer cleaned up")
