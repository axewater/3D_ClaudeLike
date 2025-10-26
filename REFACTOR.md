# Codebase Refactoring Plan

**Analysis Date:** 2025-10-26
**Total Python Files:** 123 (excluding venv)
**Total Lines of Code:** 38,674
**Status:** Functionally complete, needs organizational refactoring

---

## Executive Summary

The 3D roguelike codebase is **functionally solid** but suffers from maintainability issues:

1. **Root directory clutter** - 22 files instead of organized subdirectories
2. **Large monolithic files** - 5 files over 1,000 lines
3. **Significant code duplication** - 6 major patterns, ~500-800 lines reducible
4. **Coupling concerns** - UI/rendering directly importing game logic

**Code quality:** Good for a working prototype, needs professional refactoring for scalability.

**Estimated refactoring effort:** 10-15 hours for complete cleanup

---

## Table of Contents

1. [Root Directory Clutter](#1-root-directory-clutter)
2. [Large Files Needing Modularization](#2-large-files-needing-modularization)
3. [Code Duplication Patterns](#3-code-duplication-patterns)
4. [Current Module Organization](#4-current-module-organization)
5. [Coupling & Dependency Analysis](#5-coupling--dependency-analysis)
6. [Refactoring Recommendations](#6-refactoring-recommendations)
7. [Action Plan](#7-action-plan)
8. [Impact Summary](#8-impact-summary)

---

## 1. Root Directory Clutter

### Current State: 22 Python Files in Root

#### Core Game Logic (5 files)
- `game.py` (874 lines) - Main game logic
- `entities.py` (533 lines) - Player, Enemy, Item classes
- `dungeon.py` (147 lines) - Procedural dungeon generation
- `combat.py` (79 lines) - Damage calculations
- `abilities.py` (358 lines) - Class abilities and cooldowns

#### 3D Rendering & Engine (4 files)
- `renderer3d.py` (1,259 lines) **[LARGE]**
- `main_3d.py` (802 lines) **[LARGE]**
- `animations3d.py` (1,201 lines) **[LARGE]**
- `animation_interface.py` (110 lines)

#### UI Management (1 file)
- `ui3d_manager.py` (153 lines)

#### Audio System (1 file)
- `audio.py` (957 lines) **[LARGE]**

#### Support Systems (5 files)
- `constants.py` (533 lines) - Configuration
- `fov.py` (141 lines) - Field of view
- `visibility.py` (138 lines) - Fog of war
- `logger.py` (139 lines) - Debug logging
- `settings.py` (145 lines) - Settings management

#### Entry Points (1 file)
- `main.py` (193 lines) - Application entry point

#### Utilities/Test/Viewer Files (5 files)
- `viewer_item_models.py` (592 lines) - Model viewer
- `voice_cache.py` (448 lines) - TTS cache
- `sound_test.py` (179 lines) - Audio testing
- `tts_test.py` (258 lines) - TTS testing
- `particle_types.py` (51 lines) - Particle definitions

### Problem
Too many files in root directory mixing different concerns. Should be organized into subdirectories.

---

## 2. Large Files Needing Modularization

### Top 10 Largest Python Files

| Rank | File | Lines | Status |
|------|------|-------|--------|
| 1 | `ui3d/helmet_hud.py` | 1,442 | **NEEDS REFACTORING** - HUD components could be split |
| 2 | `ui/screens/title_screen_3d.py` | 1,280 | **NEEDS REFACTORING** - OpenGL animation is monolithic |
| 3 | `renderer3d.py` | 1,259 | **NEEDS REFACTORING** - Scene management is massive |
| 4 | `animations3d.py` | 1,201 | **NEEDS REFACTORING** - Particle system is one file |
| 5 | `audio.py` | 957 | **NEEDS REFACTORING** - Sound generation is monolithic |
| 6 | `game.py` | 874 | **ACCEPTABLE** - Core game loop, reasonable size |
| 7 | `dna_editor/models/dragon_creature.py` | 871 | **SEPARATE PROJECT** - DNA editor is its own tool |
| 8 | `dna_editor/qt_ui/editor_window.py` | 858 | **SEPARATE PROJECT** |
| 9 | `main_3d.py` | 802 | **NEEDS REFACTORING** - Input handling + camera control |
| 10 | `dna_editor/library_manager.py` | 735 | **SEPARATE PROJECT** |

**Files exceeding 300 lines:** 24 files (excluding dna_editor)

### Recommendation
Files over 1,000 lines should be split into focused modules (scene management, particle types, HUD components, etc.).

---

## 3. Code Duplication Patterns

### A. Path Setup Boilerplate (7 instances)

**Pattern found in all item files + creature_factory:**

```python
# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add dna_editor to path
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.insert(0, dna_editor_path)
```

**Affected files:**
- `graphics3d/items/sword.py` (lines 12-23)
- `graphics3d/items/shield.py` (lines 12-23)
- `graphics3d/items/boots.py` (lines 12-23)
- `graphics3d/items/health_potion.py`
- `graphics3d/items/ring.py`
- `graphics3d/items/gold_coin.py`
- `graphics3d/items/treasure_chest.py`
- `graphics3d/enemies/creature_factory.py`

**Recommendation:** Create `graphics3d/import_helper.py` with path setup logic.

---

### B. Shader Initialization Pattern (15+ instances)

**Pattern:**

```python
toon_shader = create_toon_shader()
toon_shader_lite = create_toon_shader_lite()
# ... then repeated for each entity component:
blade_shader = get_shader_for_scale(0.45, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None
```

**Found in:**
- All 8 item creation files (sword, shield, boots, ring, health potion, gold coin, treasure chest)
- `graphics3d/enemies/creature_factory.py`
- `ui/screens/class_selection_3d.py`

**Recommendation:** Create `ShaderManager` class in `graphics3d/shader_manager.py` to handle shader lifecycle.

**Proposed solution:**
```python
class ShaderManager:
    """Singleton for shader creation and caching"""
    _instance = None

    def __init__(self):
        self.toon_shader = create_toon_shader()
        self.toon_shader_lite = create_toon_shader_lite()

    def get_shader_for_scale(self, scale):
        return get_shader_for_scale(scale, self.toon_shader, self.toon_shader_lite)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Saves:** 15+ shader setup blocks → 1 line: `ShaderManager.get_instance().get_shader_for_scale(0.45)`

---

### C. Rarity-Based Color Setup (8 instances)

**Pattern:**

```python
if rarity == c.RARITY_COMMON:
    blade_color = rgb_to_ursina_color(160, 160, 160)
    # ... more colors
elif rarity == c.RARITY_UNCOMMON:
    # ... repeated structure
elif rarity == c.RARITY_RARE:
    # ...
```

**Found in:**
- `graphics3d/items/sword.py` (lines 52-82)
- `graphics3d/items/shield.py` (lines 68-95)
- `graphics3d/items/boots.py`
- `graphics3d/items/ring.py`
- `graphics3d/items/health_potion.py`
- `graphics3d/items/gold_coin.py`
- `graphics3d/items/treasure_chest.py`

**Recommendation:** Create `RarityPalette` class in `graphics3d/rarity_palette.py`.

**Proposed solution:**
```python
class RarityPalette:
    """Color schemes for different item types and rarities"""

    SWORD_COLORS = {
        c.RARITY_COMMON: {
            'blade': (160, 160, 160),
            'grip': (80, 60, 40),
            'guard': (120, 120, 120)
        },
        c.RARITY_UNCOMMON: {
            'blade': (100, 200, 100),
            'grip': (50, 100, 50),
            'guard': (80, 160, 80)
        },
        # ... other rarities
    }

    SHIELD_COLORS = { ... }
    BOOTS_COLORS = { ... }
    # etc.

    @staticmethod
    def get_colors(item_type: str, rarity: str) -> dict:
        palette_name = f'{item_type.upper()}_COLORS'
        palette = getattr(RarityPalette, palette_name, {})
        return palette.get(rarity, {})
```

**Saves:** 8+ rarity if/elif chains → 1 line: `RarityPalette.get_colors('sword', rarity)`

---

### D. UI Screen Structure (9 screens)

**Repeated pattern in all menu screens:**

```python
class GameOverScreen3D(Entity):
    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()
        self.ui_elements = []
        self.particles = []
        self.enabled = False
        self._create_ui()
```

**Affected files:**
- `ui/screens/victory_screen_3d.py`
- `ui/screens/game_over_3d.py`
- `ui/screens/pause_menu_3d.py`
- `ui/screens/main_menu_3d.py`
- `ui/screens/settings_screen_3d.py`
- All 9 screen files follow this pattern

**Recommendation:** Create `BaseScreen3D` abstract class in `ui/screens/base_screen.py`.

**Proposed solution:**
```python
from abc import ABC, abstractmethod
from ursina import Entity

class BaseScreen3D(Entity, ABC):
    """Base class for all 3D menu screens"""

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()
        self.ui_elements = []
        self.particles = []
        self.enabled = False
        self._create_ui()

    @abstractmethod
    def _create_ui(self):
        """Subclasses implement their UI here"""
        pass

    def show(self):
        """Show this screen"""
        self.enabled = True
        for elem in self.ui_elements:
            elem.enabled = True

    def hide(self):
        """Hide this screen"""
        self.enabled = False
        for elem in self.ui_elements:
            elem.enabled = False

    def cleanup(self):
        """Clean up resources"""
        for elem in self.ui_elements:
            destroy(elem)
        for particle in self.particles:
            destroy(particle)
        self.ui_elements.clear()
        self.particles.clear()
```

**Saves:** 9 screen classes inherit instead of duplicating initialization code.

---

### E. Player Model Structure (4 classes)

**Pattern:**

```python
def create_warrior_model(position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
    warrior = Entity(position=position, scale=scale)
    # Color palette (using /255 division)
    # Body parts (head, torso, arms, legs, equipment)
    warrior.rotation_y = 270
    return warrior
```

**Found in:**
- `graphics3d/players/warrior.py`
- `graphics3d/players/mage.py`
- `graphics3d/players/ranger.py`
- `graphics3d/players/rogue.py`

All 4 files create models with near-identical structure (body parts, equipment) but different colors/proportions.

**Recommendation:** Create `PlayerModelBuilder` class in `graphics3d/players/model_builder.py`.

**Proposed solution:**
```python
class HumanoidModelBuilder:
    """Builder pattern for creating humanoid player models"""

    def __init__(self, position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
        self.entity = Entity(position=position, scale=scale)
        self.colors = {}

    def set_color_palette(self, palette: dict):
        self.colors = palette
        return self

    def add_head(self, head_scale=0.4):
        # Shared head creation logic
        return self

    def add_body(self, body_scale=0.6):
        # Shared body creation logic
        return self

    def add_arms(self, arm_length=0.5):
        # Shared arm creation logic
        return self

    def add_legs(self, leg_length=0.6):
        # Shared leg creation logic
        return self

    def add_equipment(self, equipment_config: dict):
        # Equipment attachment logic
        return self

    def build(self):
        self.entity.rotation_y = 270
        return self.entity
```

**Usage:**
```python
def create_warrior_model(position, scale):
    palette = {
        'skin': (210, 180, 140),
        'armor': (100, 100, 120),
        'accent': (180, 160, 140)
    }
    return (HumanoidModelBuilder(position, scale)
            .set_color_palette(palette)
            .add_head()
            .add_body()
            .add_arms()
            .add_legs()
            .add_equipment({'sword': True, 'shield': True})
            .build())
```

---

### F. Import Statement Patterns

**Most common imports (509 total import statements across 123 files):**

- `import constants as c` - Used in 33 files
- `from ursina import Entity, Vec3, color` - Used in 60+ files (various combinations)
- `from graphics3d.utils import rgb_to_ursina_color` - Used in item/enemy files

**Pattern:** Every graphics file does:
```python
from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color
```

**Recommendation:** Consider creating `graphics3d/common.py` with common imports:
```python
# graphics3d/common.py
from ursina import Entity, Vec3, color as ursina_color
import constants as c
from graphics3d.utils import rgb_to_ursina_color

__all__ = ['Entity', 'Vec3', 'ursina_color', 'c', 'rgb_to_ursina_color']
```

Then files can do: `from graphics3d.common import *`

---

## 4. Current Module Organization

### Existing Directory Structure

```
/var/www/claudelike/3droguelike/
├── graphics3d/              # 24 Python files - 3D models
│   ├── enemies/            # Enemy models (3 files)
│   ├── items/              # Item models (8 files)
│   ├── players/            # Player models (5 files)
│   ├── tiles.py            # Dungeon tiles
│   ├── utils.py            # Shared utilities
│   └── *_cache.py          # Caching systems
├── ui/                     # UI system
│   ├── screens/            # Menu screens (9 files)
│   └── widgets/            # UI components (2 files)
├── ui3d/                   # 3D HUD components (4 files)
├── shaders/                # GLSL shaders (9 files)
├── textures/               # Procedural textures (7 files)
├── ability_icons/          # Icon generation (5 files)
├── tests/                  # Test files (3 files)
├── dna_editor/             # Separate creature editor tool (50+ files)
└── [22 root Python files]  # CLUTTERED - Should be organized
```

### Well-Organized Subdirectories
- `graphics3d/` - Good structure, could use better utils
- `ui/screens/` - Good separation, needs base class
- `shaders/` - Clean, each shader is independent
- `textures/` - Clean organization

### Poorly Organized
- **Root directory** has 22 Python files mixing concerns
- **`ui3d/` vs `ui/`** split is confusing (HUD vs menus)

---

## 5. Coupling & Dependency Analysis

### High-Coupling Files (Central Dependencies)

#### Most Imported Files:

**1. `constants.py`** - Imported by 33 files
- Used everywhere for colors, config, game constants
- **Status:** ACCEPTABLE - Configuration files should be central

**2. `game.py`** - Imported by 6 files
- `main_3d.py`, `renderer3d.py`, `ui3d_manager.py`, `helmet_hud.py`, `minimap_3d.py`, `targeting.py`
- **Status:** CONCERNING - Game logic shouldn't be imported by rendering/UI

**3. `audio.py`** - Imported by 13 files
- All UI screens, abilities, game logic
- **Status:** ACCEPTABLE - Audio manager pattern is fine

**4. `animations3d.py`** - Imported by 4 files
- Used for particle effects
- **Status:** ACCEPTABLE

### Problematic Coupling

- **`renderer3d.py` and `game.py`** have circular dependency potential
- **UI screens** directly import `game` module instead of using events/callbacks
- **`main_3d.py`** imports both `game` and `renderer3d`, acting as mediator

### Recommendation
Implement event bus pattern to decouple game logic from rendering/UI layers.

---

## 6. Refactoring Recommendations

### Priority 1: Root Directory Organization

**Move files into subdirectories:**

```
3droguelike/
├── game_logic/           # NEW - Core game systems
│   ├── __init__.py
│   ├── game.py           # From root
│   ├── entities.py       # From root
│   ├── dungeon.py        # From root
│   ├── combat.py         # From root
│   ├── abilities.py      # From root
│   ├── fov.py            # From root
│   └── visibility.py     # From root
│
├── rendering/            # NEW - All 3D rendering
│   ├── __init__.py
│   ├── renderer3d.py     # From root
│   ├── animations3d.py   # From root
│   ├── animation_interface.py  # From root
│   └── ui3d_manager.py   # From root
│
├── audio/                # NEW - Sound systems
│   ├── __init__.py
│   ├── audio.py          # From root (audio.py → manager.py)
│   ├── voice_cache.py    # From root
│   └── sound_test.py     # From root
│
├── core/                 # NEW - Shared infrastructure
│   ├── __init__.py
│   ├── constants.py      # From root
│   ├── settings.py       # From root
│   └── logger.py         # From root
│
├── utils/                # NEW - Utilities and tools
│   ├── __init__.py
│   ├── viewer_item_models.py  # From root
│   ├── particle_types.py      # From root
│   └── tts_test.py            # From root
│
├── main.py               # KEEP IN ROOT (entry point)
│
├── graphics3d/           # Already well-organized
├── ui/                   # Already well-organized
├── ui3d/                 # Keep for now
├── shaders/              # Already well-organized
├── textures/             # Already well-organized
├── ability_icons/        # Already well-organized
├── tests/                # Already well-organized
└── dna_editor/           # Separate tool, already well-organized
```

**Benefits:**
- Reduces root directory from 22 files to ~1-2 files
- Clear separation of concerns (game logic vs rendering vs audio)
- Easier to navigate and find code
- Better for IDE auto-import suggestions

---

### Priority 2: Create Utility Modules to Reduce Duplication

#### A. `graphics3d/shader_manager.py` (NEW)

```python
"""Centralized shader management for 3D models"""

class ShaderManager:
    """Singleton for shader creation and caching"""
    _instance = None

    def __init__(self):
        self.toon_shader = create_toon_shader()
        self.toon_shader_lite = create_toon_shader_lite()

    def get_shader_for_scale(self, scale):
        """Get appropriate shader based on model scale"""
        return get_shader_for_scale(scale, self.toon_shader, self.toon_shader_lite)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Convenience function
def get_shader_manager():
    return ShaderManager.get_instance()
```

**Usage in item files:**
```python
# Before (15+ instances):
toon_shader = create_toon_shader()
toon_shader_lite = create_toon_shader_lite()
blade_shader = get_shader_for_scale(0.45, toon_shader, toon_shader_lite) if toon_shader and toon_shader_lite else None

# After (1 line):
blade_shader = get_shader_manager().get_shader_for_scale(0.45)
```

**Eliminates:** 15+ instances of shader initialization boilerplate

---

#### B. `graphics3d/rarity_palette.py` (NEW)

```python
"""Color schemes for different item types and rarities"""
import constants as c
from graphics3d.utils import rgb_to_ursina_color

class RarityPalette:
    """Centralized color palettes for items by type and rarity"""

    SWORD_COLORS = {
        c.RARITY_COMMON: {
            'blade': (160, 160, 160),
            'grip': (80, 60, 40),
            'guard': (120, 120, 120),
            'glow': (100, 100, 100)
        },
        c.RARITY_UNCOMMON: {
            'blade': (100, 200, 100),
            'grip': (50, 100, 50),
            'guard': (80, 160, 80),
            'glow': (100, 255, 100)
        },
        c.RARITY_RARE: {
            'blade': (100, 150, 255),
            'grip': (50, 75, 128),
            'guard': (80, 120, 200),
            'glow': (150, 200, 255)
        },
        c.RARITY_EPIC: {
            'blade': (200, 100, 255),
            'grip': (100, 50, 128),
            'guard': (160, 80, 200),
            'glow': (255, 150, 255)
        },
        c.RARITY_LEGENDARY: {
            'blade': (255, 200, 50),
            'grip': (128, 100, 25),
            'guard': (200, 160, 40),
            'glow': (255, 255, 100)
        }
    }

    SHIELD_COLORS = { ... }
    BOOTS_COLORS = { ... }
    RING_COLORS = { ... }
    POTION_COLORS = { ... }
    # etc.

    @staticmethod
    def get_colors(item_type: str, rarity: str) -> dict:
        """Get color palette for item type and rarity

        Args:
            item_type: 'sword', 'shield', 'boots', etc.
            rarity: c.RARITY_COMMON, c.RARITY_UNCOMMON, etc.

        Returns:
            Dictionary of color names to RGB tuples
        """
        palette_name = f'{item_type.upper()}_COLORS'
        palette = getattr(RarityPalette, palette_name, {})
        return palette.get(rarity, {})

    @staticmethod
    def get_ursina_colors(item_type: str, rarity: str) -> dict:
        """Get Ursina color objects for item type and rarity"""
        rgb_colors = RarityPalette.get_colors(item_type, rarity)
        return {
            name: rgb_to_ursina_color(*rgb)
            for name, rgb in rgb_colors.items()
        }
```

**Usage in item files:**
```python
# Before (8+ instances):
if rarity == c.RARITY_COMMON:
    blade_color = rgb_to_ursina_color(160, 160, 160)
    grip_color = rgb_to_ursina_color(80, 60, 40)
elif rarity == c.RARITY_UNCOMMON:
    blade_color = rgb_to_ursina_color(100, 200, 100)
    grip_color = rgb_to_ursina_color(50, 100, 50)
# ... 20+ more lines

# After (1 line):
colors = RarityPalette.get_ursina_colors('sword', rarity)
blade_color = colors['blade']
grip_color = colors['grip']
```

**Eliminates:** 8+ rarity if/elif chains

---

#### C. `graphics3d/import_helper.py` (NEW)

```python
"""Helper for setting up import paths in graphics modules"""
import sys
from pathlib import Path

def setup_graphics_imports():
    """Setup project root and dna_editor paths for imports"""
    # Add project root to path
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Add dna_editor to path
    dna_editor_path = str(Path(__file__).parent.parent / 'dna_editor')
    if dna_editor_path not in sys.path:
        sys.path.insert(0, dna_editor_path)

# Auto-setup when imported
setup_graphics_imports()
```

**Usage in item files:**
```python
# Before (7+ instances):
import sys
from pathlib import Path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
dna_editor_path = str(Path(__file__).parent.parent.parent / 'dna_editor')
if dna_editor_path not in sys.path:
    sys.path.insert(0, dna_editor_path)

# After (1 line):
from graphics3d.import_helper import setup_graphics_imports
```

**Eliminates:** 7 instances of path setup boilerplate

---

#### D. `graphics3d/players/model_builder.py` (NEW)

```python
"""Builder pattern for creating humanoid player models"""
from ursina import Entity, Vec3
from graphics3d.utils import rgb_to_ursina_color

class HumanoidModelBuilder:
    """Builder for creating customizable humanoid models"""

    def __init__(self, position=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):
        self.entity = Entity(position=position, scale=scale)
        self.colors = {}
        self.proportions = {
            'head_scale': 0.4,
            'body_scale': 0.6,
            'arm_length': 0.5,
            'leg_length': 0.6
        }

    def set_color_palette(self, palette: dict):
        """Set color palette (skin, armor, accent, etc.)"""
        self.colors = palette
        return self

    def set_proportions(self, proportions: dict):
        """Set body proportions"""
        self.proportions.update(proportions)
        return self

    def add_head(self):
        """Add head with current color palette"""
        # Shared head creation logic
        return self

    def add_body(self):
        """Add torso with current color palette"""
        # Shared body creation logic
        return self

    def add_arms(self):
        """Add arms with current proportions"""
        # Shared arm creation logic
        return self

    def add_legs(self):
        """Add legs with current proportions"""
        # Shared leg creation logic
        return self

    def add_equipment(self, equipment_config: dict):
        """Add equipment (weapon, shield, armor details)"""
        # Equipment attachment logic
        return self

    def build(self):
        """Finalize and return the model"""
        self.entity.rotation_y = 270
        return self.entity
```

**Usage in player model files:**
```python
# warrior.py
def create_warrior_model(position, scale):
    palette = {
        'skin': (210, 180, 140),
        'armor': (100, 100, 120),
        'accent': (180, 160, 140)
    }
    return (HumanoidModelBuilder(position, scale)
            .set_color_palette(palette)
            .add_head()
            .add_body()
            .add_arms()
            .add_legs()
            .add_equipment({'sword': True, 'shield': True})
            .build())
```

**Eliminates:** Duplication across 4 player model files

---

#### E. `ui/screens/base_screen.py` (NEW)

```python
"""Base class for all 3D menu screens"""
from abc import ABC, abstractmethod
from ursina import Entity, destroy

class BaseScreen3D(Entity, ABC):
    """Abstract base class for all 3D menu screens

    Provides common initialization, show/hide logic, and cleanup.
    Subclasses only need to implement _create_ui().
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()
        self.ui_elements = []
        self.particles = []
        self.enabled = False
        self._create_ui()

    @abstractmethod
    def _create_ui(self):
        """Create UI elements for this screen

        Subclasses must implement this method to create their UI.
        Add created elements to self.ui_elements list.
        """
        pass

    def show(self):
        """Show this screen and all UI elements"""
        self.enabled = True
        for elem in self.ui_elements:
            elem.enabled = True

    def hide(self):
        """Hide this screen and all UI elements"""
        self.enabled = False
        for elem in self.ui_elements:
            elem.enabled = False

    def cleanup(self):
        """Clean up all resources (UI elements, particles, etc.)"""
        for elem in self.ui_elements:
            destroy(elem)
        for particle in self.particles:
            destroy(particle)
        self.ui_elements.clear()
        self.particles.clear()

    def update(self):
        """Optional update method for animations"""
        pass
```

**Usage in screen files:**
```python
# Before (9 screens):
class VictoryScreen3D(Entity):
    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()
        self.ui_elements = []
        self.particles = []
        self.enabled = False
        self._create_ui()

    def _create_ui(self):
        # ... screen-specific UI

# After:
class VictoryScreen3D(BaseScreen3D):
    def _create_ui(self):
        # ... screen-specific UI (only this method needed!)
```

**Eliminates:** 9 screen classes inherit instead of duplicating initialization

---

### Priority 3: Split Large Files

#### `renderer3d.py` (1,259 lines) → Split into:

```
rendering/
├── __init__.py
├── scene_manager.py      # Camera, scene setup, initialization (300-400 lines)
├── entity_renderer.py    # Entity drawing logic (300-400 lines)
├── dungeon_renderer.py   # Tile rendering (200-300 lines)
└── lighting_manager.py   # Lighting system (200-300 lines)
```

**Benefits:**
- Each module has single responsibility
- Easier to find specific rendering logic
- More testable in isolation

---

#### `animations3d.py` (1,201 lines) → Split into:

```
rendering/particles/
├── __init__.py
├── particle_system.py    # Core particle system class (300-400 lines)
├── particle_types.py     # Specific effects (explosion, blood, trails) (400-500 lines)
└── particle_manager.py   # Lifecycle management, pooling (200-300 lines)
```

**Benefits:**
- Separate particle types from system logic
- Easier to add new particle effects
- Better performance optimization opportunities

---

#### `ui3d/helmet_hud.py` (1,442 lines) → Split into:

```
ui3d/hud/
├── __init__.py
├── hud_manager.py        # Main HUD coordinator (200-300 lines)
├── stats_display.py      # Health, stats, level display (300-400 lines)
├── ability_bar.py        # Ability UI and cooldowns (300-400 lines)
├── combat_log.py         # Combat message log (200-300 lines)
└── minimap_display.py    # Map display (200-300 lines)
```

**Benefits:**
- Each HUD component is independent
- Easier to modify individual HUD elements
- Better performance (update only what changed)

---

#### `main_3d.py` (802 lines) → Split into:

```
core/
├── input_handler.py      # Keyboard/mouse input processing (300-400 lines)
├── camera_controller.py  # Camera movement and rotation logic (200-300 lines)
└── game_controller.py    # Game loop orchestration (200-300 lines)

# main_3d.py becomes thin orchestration layer (100-150 lines)
```

**Benefits:**
- Separates input handling from camera logic
- Easier to test input mappings
- Cleaner game loop

---

#### `audio.py` (957 lines) → Split into:

```
audio/
├── __init__.py
├── manager.py            # AudioManager class (200-300 lines)
├── sound_generator.py    # Procedural sound synthesis (300-400 lines)
├── music_generator.py    # Background music generation (200-300 lines)
└── audio_cache.py        # Sound caching system (150-200 lines)
```

**Benefits:**
- Separate manager from generation logic
- Easier to extend with new sound types
- Better cache management

---

### Priority 4: Decouple Architecture

**Problem:** UI and rendering directly import `game.py`, creating tight coupling.

**Solution:** Create event system for communication.

#### `core/event_bus.py` (NEW)

```python
"""Event bus for decoupling game logic from rendering/UI"""
from typing import Callable, Dict, List

class EventBus:
    """Simple event bus for publish-subscribe pattern"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, callback: Callable):
        """Subscribe to an event

        Args:
            event_name: Name of the event to listen for
            callback: Function to call when event is emitted
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Callable):
        """Unsubscribe from an event

        Args:
            event_name: Name of the event
            callback: Function to remove from listeners
        """
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)

    def emit(self, event_name: str, **data):
        """Emit an event with data

        Args:
            event_name: Name of the event to emit
            **data: Keyword arguments passed to listeners
        """
        for callback in self._listeners.get(event_name, []):
            callback(data)

    def clear(self):
        """Clear all event listeners"""
        self._listeners.clear()

# Global event bus instance
event_bus = EventBus()
```

#### Usage Example:

**In `game_logic/game.py` (emitter):**
```python
from core.event_bus import event_bus

class Game:
    def damage_player(self, damage):
        self.player.hp -= damage
        # Emit event instead of directly calling renderer
        event_bus.emit('player_damaged',
                      damage=damage,
                      hp=self.player.hp,
                      max_hp=self.player.max_hp)

    def pick_up_item(self, item):
        self.player.add_item(item)
        event_bus.emit('item_picked_up',
                      item_name=item.name,
                      item_type=item.type)
```

**In `ui3d/hud/stats_display.py` (listener):**
```python
from core.event_bus import event_bus

class StatsDisplay:
    def __init__(self):
        # Subscribe to events (no import of game.py needed!)
        event_bus.on('player_damaged', self.on_player_damaged)
        event_bus.on('player_healed', self.on_player_healed)

    def on_player_damaged(self, event_data):
        hp = event_data['hp']
        max_hp = event_data['max_hp']
        self.update_health_bar(hp, max_hp)
```

**In `rendering/entity_renderer.py` (listener):**
```python
from core.event_bus import event_bus

class EntityRenderer:
    def __init__(self):
        event_bus.on('item_picked_up', self.on_item_picked_up)

    def on_item_picked_up(self, event_data):
        item_name = event_data['item_name']
        self.remove_item_from_scene(item_name)
```

**Benefits:**
- **No circular dependencies** - `game.py` doesn't import `renderer3d.py` or vice versa
- **Easier testing** - Can test game logic without rendering
- **More maintainable** - Changes to one module don't break others
- **More extensible** - New systems can listen to existing events without modifying game logic

---

## 7. Action Plan

### Phase 1: Quick Wins (1-2 hours)

**Goal:** Reduce code duplication with minimal risk

1. Create `graphics3d/shader_manager.py`
   - Implement `ShaderManager` singleton
   - Update all item/enemy files to use it
   - **Eliminates:** 15+ duplicate shader setups

2. Create `graphics3d/rarity_palette.py`
   - Define color palettes for all item types
   - Update all item files to use it
   - **Eliminates:** 8+ rarity color if/elif chains

3. Create `ui/screens/base_screen.py`
   - Implement `BaseScreen3D` abstract class
   - Update all 9 screen classes to inherit from it
   - **Eliminates:** Repeated initialization in 9 files

**Deliverables:**
- 3 new utility modules
- 32+ files updated (15 items + 8 items + 9 screens)
- ~500 lines of code eliminated

**Testing:**
- Run game and verify all screens work
- Test item rendering with all rarities
- Verify shader effects still work

---

### Phase 2: File Organization (2-3 hours)

**Goal:** Clean up root directory structure

1. Create new subdirectories:
   - `game_logic/`
   - `rendering/`
   - `audio/`
   - `core/`
   - `utils/`

2. Move files from root to subdirectories:
   - Move game files to `game_logic/`
   - Move rendering files to `rendering/`
   - Move audio files to `audio/`
   - Move core infrastructure to `core/`
   - Move utilities to `utils/`

3. Update all import statements:
   - Find/replace `import game` → `from game_logic import game`
   - Find/replace `import constants` → `from core import constants`
   - Find/replace `import audio` → `from audio import manager`
   - etc.

4. Add `__init__.py` files to all new packages

**Deliverables:**
- Root directory reduced from 22 files to 1-2 files
- 5 new organized subdirectories
- All imports updated and working

**Testing:**
- Run full game from main.py
- Verify all imports resolve correctly
- Test all game features

---

### Phase 3: Large File Splitting (4-6 hours)

**Goal:** Break up monolithic files into focused modules

**3.1: Split `renderer3d.py` (1,259 lines)**
1. Create `rendering/scene_manager.py` - Camera and scene setup
2. Create `rendering/entity_renderer.py` - Entity drawing logic
3. Create `rendering/dungeon_renderer.py` - Tile rendering
4. Create `rendering/lighting_manager.py` - Lighting system
5. Update `renderer3d.py` to import and orchestrate these modules

**3.2: Split `animations3d.py` (1,201 lines)**
1. Create `rendering/particles/particle_system.py` - Core system
2. Create `rendering/particles/particle_types.py` - Effect implementations
3. Create `rendering/particles/particle_manager.py` - Lifecycle management
4. Update imports in files that use particles

**3.3: Split `ui3d/helmet_hud.py` (1,442 lines)**
1. Create `ui3d/hud/hud_manager.py` - Main coordinator
2. Create `ui3d/hud/stats_display.py` - Health/stats display
3. Create `ui3d/hud/ability_bar.py` - Ability UI
4. Create `ui3d/hud/combat_log.py` - Combat messages
5. Update `helmet_hud.py` to import and orchestrate components

**3.4: Split `audio.py` (957 lines)**
1. Create `audio/manager.py` - AudioManager class
2. Create `audio/sound_generator.py` - Sound synthesis
3. Create `audio/music_generator.py` - Music generation
4. Create `audio/audio_cache.py` - Caching system
5. Update imports in all files that use audio

**3.5: Split `main_3d.py` (802 lines)**
1. Create `core/input_handler.py` - Input processing
2. Create `core/camera_controller.py` - Camera logic
3. Keep `main_3d.py` as thin orchestration layer

**Deliverables:**
- 5 large files split into 20+ focused modules
- Each module under 500 lines
- Clear separation of concerns

**Testing:**
- After each file split, run game and test affected features
- Verify rendering, particles, HUD, audio all work
- Test all input controls and camera movement

---

### Phase 4: Decoupling (3-4 hours)

**Goal:** Remove tight coupling between game logic and rendering/UI

1. Create `core/event_bus.py`:
   - Implement `EventBus` class
   - Add global `event_bus` instance

2. Define event schema in `core/events.py`:
   - Document all game events (player_damaged, item_picked_up, etc.)
   - List event data payloads

3. Update `game_logic/game.py` to emit events:
   - Replace direct renderer calls with `event_bus.emit()`
   - Emit events for: damage, healing, movement, item pickup, etc.

4. Update UI components to listen to events:
   - `ui3d/hud/stats_display.py` listens to player events
   - `ui3d/hud/combat_log.py` listens to combat events
   - Remove direct imports of `game.py`

5. Update renderer to listen to events:
   - Listen to entity movement, item pickup, etc.
   - Remove direct imports of `game.py` where possible

**Deliverables:**
- Event bus system implemented
- Game logic decoupled from rendering/UI
- No circular dependencies

**Testing:**
- Test all game features end-to-end
- Verify events propagate correctly
- Test game state updates and UI updates

---

### Estimated Total Effort

| Phase | Effort | Risk | Value |
|-------|--------|------|-------|
| Phase 1: Quick Wins | 1-2 hours | Low | High |
| Phase 2: File Organization | 2-3 hours | Medium | High |
| Phase 3: Large File Splitting | 4-6 hours | Medium-High | Medium |
| Phase 4: Decoupling | 3-4 hours | High | Medium |
| **TOTAL** | **10-15 hours** | **Medium** | **High** |

---

## 8. Impact Summary

### Code Quality Metrics - Before

- **Root directory files:** 22 files (cluttered)
- **Largest file:** 1,442 lines (helmet_hud.py)
- **Files > 1000 lines:** 5 files
- **Files > 500 lines:** 14 files
- **Code duplication:** ~500-800 lines
- **Tight coupling:** UI/rendering imports game.py directly
- **Total LOC:** 38,674 lines

### Code Quality Metrics - After (Projected)

- **Root directory files:** 1-2 files (clean)
- **Largest file:** ~400-500 lines (well-modularized)
- **Files > 1000 lines:** 0 files
- **Files > 500 lines:** 3-5 files
- **Code duplication:** Minimal (shared utilities)
- **Coupling:** Loose (event-based communication)
- **Total LOC:** ~37,500-38,000 lines (net reduction)

### Benefits

#### Maintainability
- **Easier navigation:** Clear directory structure, easy to find code
- **Easier debugging:** Smaller files, focused modules
- **Easier code review:** Smaller, focused changes
- **Better IDE support:** Faster indexing, better autocomplete

#### Extensibility
- **Add new features:** Clear where new code should go
- **Modify existing features:** Changes isolated to specific modules
- **Add new event listeners:** No need to modify game logic
- **Add new UI components:** Inherit from base classes

#### Testing
- **Unit testing:** Smaller, focused modules easier to test
- **Integration testing:** Event bus enables mocking
- **Regression testing:** Less risk of breaking unrelated code

#### Collaboration
- **Onboarding:** Easier for new developers to understand structure
- **Parallel development:** Less merge conflicts with organized structure
- **Code ownership:** Clear module boundaries

#### Performance
- **Faster imports:** Smaller modules load faster
- **Better caching:** Modular design enables better optimization
- **Easier profiling:** Can profile individual modules

---

## Conclusion

The 3D roguelike codebase is **functionally complete and working well**, but would significantly benefit from organizational refactoring. The recommended changes are **incremental and low-risk**, with each phase independently valuable.

**Recommended approach:**
1. Start with **Phase 1** (quick wins) - High value, low risk
2. Then tackle **Phase 2** (organization) - Biggest UX improvement
3. Phases 3-4 can be done gradually as time permits

**Priority order if time-limited:**
1. Phase 1 (deduplication) - 1-2 hours, immediate benefits
2. Phase 2 (organization) - 2-3 hours, solves root directory clutter
3. Phase 3 (splitting) - Can be done file-by-file over time
4. Phase 4 (decoupling) - Nice to have, but lower priority

---

## Appendix: Files by Size

### All Files Over 300 Lines (Excluding dna_editor)

| Rank | File | Lines | Category |
|------|------|-------|----------|
| 1 | ui3d/helmet_hud.py | 1,442 | UI |
| 2 | ui/screens/title_screen_3d.py | 1,280 | UI |
| 3 | renderer3d.py | 1,259 | Rendering |
| 4 | animations3d.py | 1,201 | Rendering |
| 5 | audio.py | 957 | Audio |
| 6 | game.py | 874 | Game Logic |
| 7 | main_3d.py | 802 | Core |
| 8 | viewer_item_models.py | 592 | Utils |
| 9 | entities.py | 533 | Game Logic |
| 10 | constants.py | 533 | Core |
| 11 | voice_cache.py | 448 | Audio |
| 12 | ui/screens/class_selection_3d.py | 393 | UI |
| 13 | abilities.py | 358 | Game Logic |
| 14 | ui/screens/main_menu_3d.py | 336 | UI |
| 15 | graphics3d/enemies/creature_factory.py | 313 | Graphics |
| 16 | tts_test.py | 258 | Utils |
| 17 | main.py | 193 | Core |
| 18 | sound_test.py | 179 | Utils |
| 19 | ui3d/minimap_3d.py | 157 | UI |
| 20 | ui3d/targeting.py | 156 | UI |
| 21 | ui3d_manager.py | 153 | UI |
| 22 | dungeon.py | 147 | Game Logic |
| 23 | settings.py | 145 | Core |
| 24 | fov.py | 141 | Game Logic |

**Total files over 300 lines:** 24 files
**Total lines in these files:** 14,390 lines (37% of codebase)

---

**End of Refactoring Plan**
