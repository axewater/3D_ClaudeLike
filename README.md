# Claude-Like Roguelike - Complete Feature Guide 🎮

A feature-rich, turn-based roguelike with procedural dungeons, class-based combat, and no external assets - everything is procedurally generated!

**NEW**: 3D first-person mode with full UI overlay!

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Play in 3D (first-person, recommended)
python main.py --mode 3d

# Play in 2D (classic version)
python main.py --mode 2d
```

**Requirements**: Python 3.8+, PyQt6, pygame, numpy, ursina

**Controls (3D Mode)**:
- WASD - Move (camera-relative direction)
- Arrow Keys - Rotate camera / Move forward-backward
- 1/2/3 - Use abilities (click to target)
- ESC - Cancel targeting

## 🎮 Game Features

### Core Gameplay (Working in Both Modes)

#### Character Classes
- **Warrior** - High HP and defense, balanced attacker
- **Mage** - Glass cannon with powerful magic
- **Rogue** - Critical hit specialist with evasion
- **Ranger** - Ranged attacks and mobility

Each class has 3 unique abilities with cooldown management.

#### Abilities System
- **Fireball** (Mage) - Ranged damage with fire trail effect
- **Frost Nova** (Mage) - Area freeze with ice crystals
- **Heal** (Mage) - Self-healing with sparkle effect
- **Dash** (Rogue) - Teleport with speed lines
- **Shadow Step** (Rogue) - Invisible movement
- **Whirlwind** (Warrior) - Area attack with spin effect

See `abilities.py` for implementation details.

#### Combat System
- Turn-based bump-to-attack mechanics
- Damage calculation with variance (±20%)
- Critical hits with visual feedback
- Elemental effects and status conditions
- XP and leveling system

Combat formulas in `combat.py`.

#### Dungeon Generation
- Procedural BSP (Binary Space Partitioning) algorithm
- Random room placement with corridor connections
- 5 biomes changing every 5 levels:
  - Dungeon (1-5)
  - Catacombs (6-10)
  - Caves (11-15)
  - Hell (16-20)
  - Abyss (21-25)

See `dungeon.py` for generation logic.

#### Equipment & Items
- **5 Rarity Tiers**: Common → Uncommon → Rare → Epic → Legendary
- **Item Types**: Swords, Shields, Rings, Boots, Health Potions
- **Auto-equipping** on pickup with stat comparison
- **Dynamic stats** via `@property` decorators

Item definitions in `entities.py`, visual rendering in `graphics/items/` and `graphics3d/items/`.

#### Enemies
- **6 Enemy Types**: Goblin, Slime, Skeleton, Orc, Demon, Dragon
- **Smart AI** with pathfinding and alert system
- **Level scaling** - Stats increase with dungeon level
- **Unique visuals** - Each enemy has distinct 2D and 3D models

Enemy logic in `entities.py`, rendering in `graphics/enemies/` and `graphics3d/enemies/`.

### Audio System (2D Mode) 🔊

**100% Procedurally Generated** - No audio files required!

#### Sound Synthesis
- **Wave types**: Sine, Square, Sweep, Noise
- **22 unique sounds**: Combat, abilities, movement, UI
- **Positional audio**: Volume based on distance
- **Pitch variation**: Prevents repetition
- **Adaptive music**: Changes with combat intensity

Implementation in `audio.py`:
- `SoundSynthesizer` - Wave generation
- `AudioManager` - Playback and mixing (singleton pattern)

Example usage:
```python
from audio import get_audio_manager
audio = get_audio_manager()
audio.play_attack_sound('heavy')
audio.play_hit_sound(is_crit=True, position=(x, y), player_position=(px, py))
```

### Visual Effects

#### 2D Particle System (`animations.py`)
- **Particle Types**: Standard, Directional, Trail, Ambient
- **Effects**:
  - Floating damage text
  - Death bursts (enemy-specific)
  - Ability trails (fire, ice, dash)
  - Screen shake
  - Flash effects
  - Ambient atmosphere

#### 3D Particle System (`animations3d.py`)
- **3D Physics**: Gravity, velocity, friction
- **Billboard sprites**: Always face camera
- **Particle Effects**:
  - Explosions with directional spray
  - Floating 3D text
  - Trail ribbons
  - Screen shake (camera wobble)
  - Alert particles ("!" above enemies)

### Field of View & Visibility

- **Ray-casting FOV** algorithm in `fov.py`
- **Fog of War** system in `visibility.py`
- **Explored tiles** remain dimly visible
- **Dynamic lighting** reveals tiles as you move

*(Note: 3D FOV implementation pending)*

## 📁 File Reference

### Core Game Logic (Renderer-Agnostic)

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `game.py` | Main game state and turn manager | `Game`, `start_new_game()`, `_player_attack()`, `_enemy_turn()` |
| `entities.py` | Player, Enemy, Item classes | `Player`, `Enemy`, `Item`, inventory management |
| `dungeon.py` | Procedural dungeon generation | `Dungeon`, `generate()`, BSP algorithm |
| `combat.py` | Damage calculations | `calculate_damage()`, `apply_damage()` |
| `abilities.py` | Ability system | `Ability` base class, 6 ability implementations |
| `constants.py` | All game configuration | All constants, stats, colors |

### 2D Rendering (PyQt6)

| File/Directory | Purpose |
|----------------|---------|
| `ui/main_window.py` | Main PyQt6 window and screen manager |
| `ui/screens/title_screen.py` | Animated title screen |
| `ui/screens/class_selection.py` | Character class picker with preview |
| `ui/screens/main_menu.py` | Main menu navigation |
| `ui/screens/victory_screen.py` | Game over / victory display |
| `ui/widgets/game_widget.py` | Main game rendering widget |
| `ui/widgets/stats_panel.py` | Player stats HUD |
| `ui/widgets/combat_log.py` | Scrolling message log |
| `ui/widgets/ability_button.py` | Ability UI buttons |
| `graphics/tiles.py` | Tile rendering (floor, wall, stairs) |
| `graphics/players/*.py` | Player class visuals (4 classes) |
| `graphics/enemies/*.py` | Enemy visuals (6 types) |
| `graphics/items/*.py` | Item visuals (5 types) |
| `graphics/utils.py` | Rendering utilities (gems, runes, gradients) |
| `animations.py` | 2D particle effects manager |

### 3D Rendering (Ursina)

| File/Directory | Purpose |
|----------------|---------|
| `main_3d.py` | 3D mode entry point, game loop |
| `renderer3d.py` | Ursina 3D rendering manager |
| `graphics3d/tiles.py` | 3D dungeon meshes (walls, floors, stairs) |
| `graphics3d/players/*.py` | 3D player models (4 classes) |
| `graphics3d/enemies/*.py` | 3D enemy models (6 types) |
| `graphics3d/items/*.py` | 3D item models (5 types) |
| `graphics3d/utils.py` | 3D utilities (coordinate conversion, colors) |
| `animations3d.py` | 3D particle effects with physics |
| `ui/screens/title_screen_3d.py` | 3D title screen (development) |

### Support Systems

| File | Purpose |
|------|---------|
| `audio.py` | Procedural sound synthesis and playback |
| `fov.py` | Field of view ray-casting |
| `visibility.py` | Fog of war and exploration tracking |

## 🛠️ Adding New Content

### Add a New Enemy

**1. Define in `constants.py`:**
```python
ENEMY_VAMPIRE = "vampire"
ENEMY_STATS[ENEMY_VAMPIRE] = {
    "hp": 80, "attack": 12, "defense": 6, "xp": 50
}
COLOR_ENEMY_VAMPIRE = QColor(150, 0, 0)
```

**2. Create 2D renderer in `graphics/enemies/vampire.py`:**
```python
def draw_vampire(painter: QPainter, center_x: int, center_y: int,
                 tile_size: int, color: QColor, idle_time: float):
    """Draw vampire with cloak and fangs"""
    # Your 2D rendering code here
```

**3. Create 3D model in `graphics3d/enemies/vampire.py`:**
```python
def create_vampire_model(x, y):
    """Create 3D vampire model"""
    from ursina import Entity
    model = Entity(model='cube', scale=(0.4, 0.6, 0.3))
    # Add details (fangs, cloak)
    return model
```

**4. Register in dispatchers:**
- `graphics/enemies/__init__.py` - Add to `draw_enemy()`
- `graphics3d/enemies/__init__.py` - Add to `create_enemy_model_3d()`

**5. Update spawn logic in `game.py`:**
```python
# In _spawn_enemies() method
enemy_types = [c.ENEMY_GOBLIN, c.ENEMY_VAMPIRE, ...]
```

### Add a New Ability

Create in `abilities.py`:
```python
class NewAbility(Ability):
    def __init__(self):
        super().__init__(
            name="Teleport",
            description="Instantly move to target",
            cooldown=8,
            ability_type="utility"
        )

    def use(self, user, target_pos, game):
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        tx, ty = target_pos
        if not game.dungeon.is_walkable(tx, ty):
            self.current_cooldown = 0  # Refund
            return (False, "Can't teleport there!")

        user.start_move(tx, ty)
        game.anim_manager.add_ability_trail(tx, ty, color.purple, "dash")

        return (True, f"Teleported!")
```

Add to class in `CLASS_ABILITIES` dictionary.

### Add a New Item Type

**1. Constants in `constants.py`:**
```python
ITEM_HELMET = "helmet"
SYMBOL_HELMET = "^"
EQUIPMENT_TYPES[ITEM_HELMET] = SLOT_HEAD
ITEM_EFFECTS[ITEM_HELMET] = {"defense": 4}
```

**2. Create renderers:**
- `graphics/items/helmet.py` - 2D shape
- `graphics3d/items/helmet.py` - 3D model

**3. Register in both `graphics/items/__init__.py` and `graphics3d/items/__init__.py`**

**4. Add to spawn pool in `game.py` - `_spawn_items()` method**

### Add a Procedural Sound

In `audio.py`, add to `AudioManager._generate_sounds()`:
```python
synth = SoundSynthesizer()

# Create sound using wave synthesis
teleport_sound = synth.combine_waves(
    synth.generate_sweep(800, 1200, 0.15, 0.4),  # Ascending whoosh
    synth.generate_sine_wave(1200, 0.1, 0.3)     # High ping
)
self.sounds['teleport'] = synth.array_to_sound(teleport_sound)

# Add helper method
def play_teleport_sound(self):
    self.play_sound('teleport', volume=0.7, pitch_variation=0.1)
```

## 🎨 Visual Design

### 2D Graphics - Geometric Shapes
All visuals drawn with PyQt6 `QPainter`:
- **Techniques**: Gradients, polygons, layering
- **No sprites** - Everything procedural
- **Rarity effects**: Gems, glows, sparkles for rare items

See `graphics/utils.py` for shared rendering functions:
- `draw_gem()` - Faceted gems
- `draw_rune()` - Glowing symbols
- `draw_metallic_gradient()` - Metal shading

### 3D Graphics - Procedural Models
All 3D models built with Ursina primitives:
- **Cube, Sphere, Cylinder** base shapes
- **Scaling and parenting** for complex models
- **No external files** - Pure Python generation

Example - Warrior model (`graphics3d/players/warrior.py`):
```python
body = Entity(model='cube', scale=(0.4, 0.6, 0.3))
head = Entity(model='sphere', scale=0.25, parent=body, y=0.4)
sword = Entity(model='cube', scale=(0.1, 0.6, 0.05), parent=body, x=0.3)
```

## 🏗️ Architecture Patterns

### Dual Rendering Architecture
```
        ┌─────────────┐
        │   game.py   │  (Renderer-agnostic game logic)
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │   main.py   │  (Mode selector: --mode 2d/3d)
        └──────┬──────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼───┐      ┌────▼────┐
   │  2D   │      │   3D    │
   │ PyQt6 │      │ Ursina  │
   └───────┘      └─────────┘
```

### Key Design Patterns

1. **Singleton Pattern** - `AudioManager` via `get_audio_manager()`
2. **Proxy Pattern** - `AnimationManager3DProxy` bridges 2D/3D particles
3. **Dispatcher Pattern** - `graphics/enemies/__init__.py` routes to specific renderers
4. **Entity-Component** - Base `Entity` class, specialized subclasses
5. **Observer Pattern** - PyQt signals for UI events

### Animation & Movement System

All entities inherit smooth movement from `Entity` base class:
- **Grid position** - Logical position (int)
- **Display position** - Visual position (float, interpolated)
- **Idle animation** - Driven by `idle_time` parameter
- **Facing direction** - Tracked for sprite orientation

Managed by:
- **2D**: `AnimationManager` in `animations.py`
- **3D**: `AnimationManager3D` in `animations3d.py`

## ⚙️ Configuration & Balancing

### Key Constants (`constants.py`)

```python
# Dungeon
GRID_WIDTH = 80
GRID_HEIGHT = 50
MAX_ROOMS = 15

# Combat
DAMAGE_VARIANCE = 0.2  # ±20%
CRIT_DAMAGE_MULTIPLIER = 2.0

# Spawning
ENEMIES_PER_LEVEL_BASE = 5
ITEMS_PER_LEVEL = 3

# Rarity (drop rates scale with level)
RARITY_COMMON = 60% → 20%
RARITY_LEGENDARY = 0% → 2%
```

### Class Stats
```python
CLASS_STATS = {
    CLASS_WARRIOR: {"hp": 120, "attack": 12, "defense": 8},
    CLASS_MAGE: {"hp": 70, "attack": 15, "defense": 3},
    CLASS_ROGUE: {"hp": 85, "attack": 13, "defense": 4, "crit_chance": 0.25},
    CLASS_RANGER: {"hp": 90, "attack": 11, "defense": 5}
}
```

### Enemy Stats (Base, before level scaling)
```python
ENEMY_STATS = {
    ENEMY_GOBLIN: {"hp": 20, "attack": 5, "defense": 2, "xp": 10},
    ENEMY_DRAGON: {"hp": 100, "attack": 20, "defense": 12, "xp": 100}
}
# Scaling formula: stat * (1.0 + (level - 1) * 0.3)
```

## 🐛 Debugging & Development

### Debug Mode

**Enable debug output in 3D:**
```python
# main_3d.py
app = Ursina(development_mode=True)  # Shows FPS, entity count
```

**Console logging is built-in:**
- Movement: `[MOVE] Player moved: (x, y)`
- Combat: `[COMBAT] Attacking enemy`
- Events: `[EVENT] Player on stairs`
- Heartbeat: `[HEARTBEAT] Frame 60 | FPS=45.2`

### Testing Helpers

**God mode:**
```python
game.player.hp = 999999
game.player.max_hp = 999999
```

**Reveal entire map:**
```python
game.visibility_map.reveal_all()
```

**Spawn specific enemy:**
```python
from entities import Enemy
import constants as c
enemy = Enemy(10, 10, c.ENEMY_DRAGON, c.ENEMY_STATS[c.ENEMY_DRAGON])
game.enemies.append(enemy)
```

**Skip ability cooldowns:**
```python
for ability in game.player.abilities:
    ability.current_cooldown = 0
```

### Performance Profiling

- **Target**: 60 FPS in 2D, 45+ FPS in 3D
- **Bottlenecks**: Particle count, entity count, FOV calculation
- **Optimization**: Particle pooling, occlusion culling (planned for 3D)

Typical performance:
- 2D: 60 FPS with 100+ entities
- 3D: 40-45 FPS with 50+ entities

## 🚧 Known Limitations

### 3D Mode (80% Complete)
- ✅ Full UI overlay (stats, abilities, combat log)
- ✅ First-person camera with smooth rotation
- ✅ Ability targeting system (1/2/3 keys + mouse)
- ✅ Performance optimizations (particle limits, conditional UI updates)
- ❌ No FOV/Fog of War (planned for Phase 8)
- ❌ No class selection screen (hardcoded to Warrior - Phase 7)
- ❌ No title/menu screens (Phase 7)
- ❌ No 3D positional audio (optional - Phase 8)
- ❌ No victory/game over UI (console only - Phase 7)

### Both Modes
- Audio only works in 2D mode (3D audio planned)
- Saving/loading not implemented
- No multiplayer

See `MIGRATION.md` for detailed roadmap.

## 📚 Additional Documentation

- **`CLAUDE.md`** - Quick developer onboarding
- **`MIGRATION.md`** - 3D migration project plan
- **`docs_archive_2025-10-12/`** - Archived phase summaries

## 🎯 Design Philosophy

1. **No External Assets** - Everything procedurally generated
2. **Clean Separation** - Game logic independent of rendering
3. **Dual Rendering** - Support both 2D and 3D
4. **Modular Design** - Easy to add content (enemies, abilities, items)
5. **Type Safety** - Type hints on all functions
6. **Self-Documenting** - Clear naming, comprehensive docstrings

## 📝 Code Style

- **Type hints** on all function signatures
- **Docstrings** for all classes and public methods
- **Constants** in `UPPER_CASE`
- **Private methods** prefixed with `_`
- **Color objects** use PyQt6 `QColor` (2D) or RGB tuples (3D)

---

**For quick start:** See `CLAUDE.md`
**For development roadmap:** See `MIGRATION.md`

Happy coding! 🎮
