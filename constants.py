"""
Game constants and configuration for Claude-Like
"""
from PyQt6.QtGui import QColor

# ========================================
# RENDERING MODE CONFIGURATION
# ========================================
USE_3D_RENDERER = False  # Toggle between 2D (False) and 3D (True) rendering

# 3D rendering settings (for Ursina engine)
# Third-person camera (legacy, not used in first-person mode)
CAMERA_DISTANCE = 15.0  # Camera distance from player (third-person only)
CAMERA_HEIGHT = 8.0     # Camera height above ground (third-person only)
CAMERA_ANGLE = 45.0     # Camera pitch angle (degrees) (third-person only)

# First-person camera settings
USE_FIRST_PERSON = True  # True = first-person, False = third-person
EYE_HEIGHT = 1.2        # Camera height at eye level (first-person) - lowered for better ground visibility
CAMERA_ROTATION_SPEED = 8.0  # Rotation interpolation speed (higher = snappier)
CAMERA_FOV_FPS = 90     # Field of view for first-person (PC FPS standard 90-100°)

# Camera pitch (vertical tilt) settings
DEFAULT_CAMERA_PITCH = 10.0   # Default pitch: look down 10° (AAA FPS standard for ground visibility)
CAMERA_PITCH_SPEED = 1.5      # Pitch interpolation speed (smooth ~1 second transition)
ENEMY_FOCUS_PITCH = 20.0      # Degrees to tilt down when focusing on adjacent enemy (additive with default)

# Camera lens distortion (barrel/fisheye effect)
BARREL_DISTORTION_STRENGTH = 0.10  # Subtle fisheye warp at edges (0.0=none, 0.1=subtle, 0.3=strong)

# Corner shadow / ambient occlusion effect
CORNER_SHADOW_INTENSITY = 0.85  # Darkness at tile corners (0.0=none, 0.85=ultra dark, 1.0=maximum)

# World settings
WALL_HEIGHT = 2.0       # 3D wall height in world units
PLAYER_HEIGHT = 1.5     # Player model height
ENTITY_SCALE = 0.8      # Base entity scale
FOV = 60                # Field of view for 3D camera (third-person)

# Grid settings
GRID_WIDTH = 50
GRID_HEIGHT = 30
TILE_SIZE = 48  # pixels (2x scale for detailed sprites - used in 2D mode)

# Viewport/Camera settings
VIEWPORT_WIDTH = 25   # Tiles visible on screen
VIEWPORT_HEIGHT = 15  # Tiles visible on screen

# Window settings
SIDEBAR_WIDTH = 600
WINDOW_WIDTH = VIEWPORT_WIDTH * TILE_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = VIEWPORT_HEIGHT * TILE_SIZE

# Biomes (tilesets that change every 5 levels)
BIOME_DUNGEON = "dungeon"      # Levels 1-5
BIOME_CATACOMBS = "catacombs"  # Levels 6-10
BIOME_CAVES = "caves"          # Levels 11-15
BIOME_HELL = "hell"            # Levels 16-20
BIOME_ABYSS = "abyss"          # Levels 21-25

# Colors - Improved palette (default/dungeon biome)
COLOR_FLOOR = QColor(45, 45, 48)  # Dark floor
COLOR_WALL = QColor(30, 30, 35)  # Darker walls
COLOR_PLAYER = QColor(100, 200, 255)  # Bright blue
COLOR_PLAYER_BORDER = QColor(50, 100, 200)
COLOR_ENEMY_GOBLIN = QColor(100, 220, 80)  # Green
COLOR_ENEMY_SLIME = QColor(80, 200, 180)  # Cyan-teal
COLOR_ENEMY_SKELETON = QColor(220, 220, 220)  # White
COLOR_ENEMY_ORC = QColor(100, 140, 70)  # Dark green
COLOR_ENEMY_DEMON = QColor(140, 50, 120)  # Dark purple
COLOR_ENEMY_DRAGON = QColor(255, 80, 60)  # Red
COLOR_ITEM_POTION = QColor(255, 50, 200)  # Magenta
COLOR_ITEM_WEAPON = QColor(255, 215, 0)  # Gold
COLOR_ITEM_ARMOR = QColor(150, 180, 255)  # Light blue
COLOR_STAIRS = QColor(150, 100, 255)  # Purple

# Biome color schemes
BIOME_COLORS = {
    BIOME_DUNGEON: {
        "floor": QColor(45, 45, 48),
        "wall": QColor(30, 30, 35),
        "stairs": QColor(150, 100, 255),
    },
    BIOME_CATACOMBS: {
        "floor": QColor(60, 55, 50),  # Dusty brown
        "wall": QColor(90, 85, 80),   # Bone white-ish
        "stairs": QColor(200, 180, 120),  # Golden
    },
    BIOME_CAVES: {
        "floor": QColor(40, 50, 35),  # Earthy brown-green
        "wall": QColor(55, 45, 35),   # Dark rock brown
        "stairs": QColor(100, 180, 100),  # Mossy green
    },
    BIOME_HELL: {
        "floor": QColor(50, 25, 20),  # Dark charred
        "wall": QColor(80, 30, 25),   # Dark red stone
        "stairs": QColor(255, 100, 50),  # Lava orange
    },
    BIOME_ABYSS: {
        "floor": QColor(25, 20, 35),  # Dark purple-black
        "wall": QColor(35, 25, 50),   # Deep void purple
        "stairs": QColor(180, 120, 255),  # Ethereal purple
    },
}

# Text colors
COLOR_TEXT_LIGHT = QColor(220, 220, 220)
COLOR_TEXT_DARK = QColor(20, 20, 25)

# Message colors
COLOR_MSG_DAMAGE = "#ff6b6b"
COLOR_MSG_HEAL = "#51cf66"
COLOR_MSG_ITEM = "#ffd43b"
COLOR_MSG_EVENT = "#74c0fc"
COLOR_MSG_DEATH = "#ff4444"
COLOR_MSG_LEVELUP = "#a9e34b"

# UI colors
COLOR_PANEL_BG = QColor(35, 35, 40)
COLOR_HP_BAR_FULL = QColor(80, 200, 120)
COLOR_HP_BAR_MID = QColor(255, 193, 7)
COLOR_HP_BAR_LOW = QColor(244, 67, 54)
COLOR_HP_BAR_BG = QColor(50, 50, 55)
COLOR_XP_BAR = QColor(138, 43, 226)
COLOR_XP_BAR_BG = QColor(50, 50, 55)

# Enemy health bar colors
COLOR_ENEMY_HP_BAR = QColor(220, 80, 80)
COLOR_ENEMY_HP_BAR_BG = QColor(40, 40, 40, 180)
COLOR_ENEMY_HP_BAR_BORDER = QColor(20, 20, 20)

# 3D health bar settings
HEALTH_BAR_SCALE = 2.0  # Scale for 3D enemy health bars (increased from 0.8 for readability)
HEALTH_BAR_OFFSET_Y = 1.8  # Height above enemy

# Sidebar section colors
COLOR_SECTION_BG = QColor(42, 42, 47)
COLOR_SECTION_BORDER = QColor(60, 60, 65)
COLOR_DIVIDER = QColor(70, 70, 75)

# Symbols for entities
SYMBOL_PLAYER = "@"
SYMBOL_GOBLIN = "g"
SYMBOL_SLIME = "~"
SYMBOL_SKELETON = "s"
SYMBOL_ORC = "O"
SYMBOL_DEMON = "&"
SYMBOL_DRAGON = "D"
SYMBOL_POTION = "!"
SYMBOL_SWORD = "/"
SYMBOL_SHIELD = "]"
SYMBOL_BOOTS = "["
SYMBOL_RING = "o"
SYMBOL_STAIRS = ">"
SYMBOL_WALL = "#"
SYMBOL_FLOOR = "."

# Tile types
TILE_FLOOR = 0
TILE_WALL = 1
TILE_STAIRS = 2

# Entity types
ENTITY_PLAYER = "player"
ENTITY_ENEMY = "enemy"
ENTITY_ITEM = "item"

# Player class types
CLASS_WARRIOR = "warrior"
CLASS_MAGE = "mage"
CLASS_ROGUE = "rogue"
CLASS_RANGER = "ranger"

# Class stats [HP, Attack, Defense]
CLASS_STATS = {
    CLASS_WARRIOR: {"hp": 120, "attack": 12, "defense": 8, "description": "High HP tank with strong defense"},
    CLASS_MAGE: {"hp": 70, "attack": 15, "defense": 3, "description": "Glass cannon with powerful attacks"},
    CLASS_ROGUE: {"hp": 85, "attack": 13, "defense": 4, "crit_chance": 0.25, "description": "High critical hit chance and dodge"},
    CLASS_RANGER: {"hp": 90, "attack": 11, "defense": 5, "description": "Balanced fighter with ranged capabilities"},
}

# Class colors
COLOR_CLASS_WARRIOR = QColor(180, 60, 40)  # Deep blood red (Berserker)
COLOR_CLASS_MAGE = QColor(100, 150, 255)  # Blue
COLOR_CLASS_ROGUE = QColor(180, 100, 255)  # Purple
COLOR_CLASS_RANGER = QColor(100, 200, 100)  # Green

# Ability colors and visual settings
ABILITY_ICON_SIZE = 70  # Diameter of circular ability icons
ABILITY_ICON_SPACING = 12  # Space between icons

# Ability-specific colors
COLOR_ABILITY_FIREBALL = QColor(255, 120, 40)  # Orange-red fire
COLOR_ABILITY_FIREBALL_SECONDARY = QColor(255, 60, 0)  # Deep red
COLOR_ABILITY_DASH = QColor(120, 180, 255)  # Electric blue
COLOR_ABILITY_DASH_SECONDARY = QColor(200, 220, 255)  # Light blue
COLOR_ABILITY_HEALING = QColor(80, 220, 120)  # Vibrant green
COLOR_ABILITY_HEALING_SECONDARY = QColor(180, 255, 200)  # Light green
COLOR_ABILITY_FROST = QColor(150, 220, 255)  # Ice blue
COLOR_ABILITY_FROST_SECONDARY = QColor(200, 240, 255)  # Pale ice
COLOR_ABILITY_WHIRLWIND = QColor(255, 100, 100)  # Red
COLOR_ABILITY_WHIRLWIND_SECONDARY = QColor(255, 180, 180)  # Light red
COLOR_ABILITY_SHADOW = QColor(120, 60, 180)  # Dark purple
COLOR_ABILITY_SHADOW_SECONDARY = QColor(60, 20, 100)  # Deep shadow

# Ability icon states
COLOR_ABILITY_READY_GLOW = QColor(255, 255, 150)  # Golden glow when ready
COLOR_ABILITY_COOLDOWN_OVERLAY = QColor(20, 20, 30, 200)  # Dark overlay
COLOR_ABILITY_BORDER = QColor(80, 80, 90)  # Default border
COLOR_ABILITY_HOVER_BORDER = QColor(200, 200, 220)  # Hover border

# Enemy types
ENEMY_GOBLIN = "goblin"
ENEMY_SLIME = "slime"
ENEMY_SKELETON = "skeleton"
ENEMY_ORC = "orc"
ENEMY_DEMON = "demon"
ENEMY_DRAGON = "dragon"

# Item types
ITEM_HEALTH_POTION = "health_potion"
ITEM_SWORD = "sword"
ITEM_SHIELD = "shield"
ITEM_BOOTS = "boots"
ITEM_RING = "ring"
ITEM_GOLD_COIN = "gold_coin"
ITEM_TREASURE_CHEST = "treasure_chest"

# Equipment slots
SLOT_WEAPON = "weapon"
SLOT_ARMOR = "armor"
SLOT_ACCESSORY = "accessory"
SLOT_BOOTS = "boots"

# Equipment item types (can be equipped)
EQUIPMENT_TYPES = {
    ITEM_SWORD: SLOT_WEAPON,
    ITEM_SHIELD: SLOT_ARMOR,
    ITEM_BOOTS: SLOT_BOOTS,
    ITEM_RING: SLOT_ACCESSORY,
}

# Item rarities
RARITY_COMMON = "common"
RARITY_UNCOMMON = "uncommon"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

# Rarity colors
COLOR_RARITY_COMMON = QColor(180, 180, 180)  # Gray
COLOR_RARITY_UNCOMMON = QColor(100, 200, 100)  # Green
COLOR_RARITY_RARE = QColor(100, 150, 255)  # Blue
COLOR_RARITY_EPIC = QColor(200, 100, 255)  # Purple
COLOR_RARITY_LEGENDARY = QColor(255, 180, 0)  # Gold

# Player starting stats
PLAYER_START_HP = 100
PLAYER_START_MAX_HP = 100
PLAYER_START_ATTACK = 10
PLAYER_START_DEFENSE = 5

# Enemy stats [HP, Attack, Defense]
ENEMY_STATS = {
    ENEMY_GOBLIN: {"hp": 30, "attack": 5, "defense": 2, "xp": 10},
    ENEMY_SLIME: {"hp": 40, "attack": 6, "defense": 3, "xp": 15},
    ENEMY_SKELETON: {"hp": 50, "attack": 8, "defense": 4, "xp": 20},
    ENEMY_ORC: {"hp": 80, "attack": 12, "defense": 7, "xp": 40},
    ENEMY_DEMON: {"hp": 110, "attack": 16, "defense": 9, "xp": 70},
    ENEMY_DRAGON: {"hp": 150, "attack": 20, "defense": 10, "xp": 100},
}

# Item effects (base values, modified by rarity)
ITEM_EFFECTS = {
    ITEM_HEALTH_POTION: {"heal": 50},
    ITEM_SWORD: {"attack": 5},
    ITEM_SHIELD: {"defense": 2},
    ITEM_BOOTS: {"defense": 1},
    ITEM_RING: {"attack": 2, "defense": 1},
    ITEM_GOLD_COIN: {"gold_value": 1},  # Base gold value (multiplied by rarity)
    ITEM_TREASURE_CHEST: {"gold_value": 10},  # 10x gold coins (multiplied by rarity)
}

# Dungeon generation
MIN_ROOM_SIZE = 4
MAX_ROOM_SIZE = 10
MAX_ROOMS = 15
ENEMIES_PER_LEVEL_BASE = 5
ITEMS_PER_LEVEL = 5
MAX_LEVEL = 25  # Maximum level before victory

# Game mechanics
DAMAGE_VARIANCE = 0.2  # +/- 20% damage variance
BACKSTAB_DAMAGE_MULTIPLIER = 1.75  # Rogue backstab bonus (75% extra damage)

# Field of View / Visibility
PLAYER_VISION_RADIUS = 10  # Base vision range (Manhattan distance)
ROGUE_VISION_BONUS = 5     # Rogue sees +5 tiles further
ENEMY_VISION_RADIUS = 8    # Enemy detection range
ENEMY_VISION_VS_ROGUE = 6  # Reduced vision when chasing Rogue

# Visibility states
VISIBILITY_UNEXPLORED = "unexplored"
VISIBILITY_EXPLORED = "explored"
VISIBILITY_VISIBLE = "visible"

# Rendering
EXPLORED_TILE_ALPHA = 0.3  # Darkness factor for explored tiles (30% brightness)

# 3D performance settings
MAX_PARTICLES = 100  # Maximum active particles (performance limit)
UI_UPDATE_THROTTLE = 0.05  # Minimum seconds between UI updates (20 FPS update rate)
ENABLE_AMBIENT_PARTICLES_3D = False  # Disable fog/cloud particles in 3D mode (can't see outside dungeon in first-person)

# Minimap settings
MINIMAP_ENABLED = True  # Enable/disable minimap
MINIMAP_MODE = "full"  # "full" (entire dungeon) or "radar" (nearby area only)
MINIMAP_SIZE_FULL = (200, 120)  # Width x Height for full map view
MINIMAP_SIZE_RADAR = (150, 150)  # Size for radar mode
MINIMAP_RADAR_RANGE = 15  # Tiles visible in radar mode
MINIMAP_POSITION = "bottom_right"  # "top_right" or "bottom_right"
MINIMAP_OPACITY = 0.90  # Background panel opacity
MINIMAP_BORDER_COLOR = (0.2, 0.4, 0.6, 0.4)  # Cyan border (matches HUD style)
MINIMAP_PIXEL_SCALE = 2  # Pixels per tile (2 = 2x2 pixels per dungeon tile)

# Voice taunts
VOICE_TAUNTS = [
    "You will never get there",
    "You will fail miserably",
    "Your death is inevitable",
    "Give up now",
    "You cannot win",
    "Pathetic effort",
    "Is that all you have",
    "Weakness",
    "You are doomed",
    "Futile resistance",
]

# Taunt configuration
TAUNT_COOLDOWN = 5.0  # Minimum seconds between taunts (reduced for testing)
TAUNT_CHANCE_ON_DAMAGE = 0.80  # 80% chance when player takes damage (increased for testing)
TAUNT_CHANCE_ON_LEVEL = 0.80  # 80% chance when entering new level (increased for testing)
TAUNT_LOW_HP_THRESHOLD = 0.30  # Trigger when below 30% health


# Helper functions
def get_biome_for_level(level: int) -> str:
    """Determine biome based on current level"""
    if level <= 5:
        return BIOME_DUNGEON
    elif level <= 10:
        return BIOME_CATACOMBS
    elif level <= 15:
        return BIOME_CAVES
    elif level <= 20:
        return BIOME_HELL
    else:  # 21-25
        return BIOME_ABYSS
