# Claude-Like Roguelike - Complete Feature Guide 🎮

A feature-rich, turn-based 3D roguelike with procedural dungeons, class-based combat, and no external assets - everything is procedurally generated!

**First-person 3D dungeon crawler** with full UI overlay and procedural audio!

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game (3D first-person mode)
python main.py

# Skip intro animation for faster startup
python main.py --skip-intro
```

**Requirements**: Python 3.8+, ursina, panda3d, pygame, numpy

**Controls**:
- WASD - Move (camera-relative direction)
- Arrow Keys - Rotate camera (90° turns) / Move forward-backward
- 1/2/3 - Use abilities (click to target)
- Mouse - Aim targeting reticle for abilities
- ESC - Cancel targeting / Pause menu
- F1 - Debug: Reveal full map
- F2 - Debug: Skip to next level

## 🎮 Game Features

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

Item definitions in `entities.py`, visual rendering in `graphics3d/items/`.

#### Enemies
- **6 Enemy Types**: Goblin, Slime, Skeleton, Orc, Demon, Dragon
- **Smart AI** with pathfinding and alert system
- **Level scaling** - Stats increase with dungeon level
- **Unique visuals** - Each enemy has distinct procedurally-generated 3D models

Enemy logic in `entities.py`, 3D rendering in `graphics3d/enemies/`.

### Audio System 🔊

**100% Procedurally Generated** - No audio files required!

#### Sound Synthesis
- **Wave types**: Sine, Square, Sweep, Noise
- **25+ unique sounds**: Combat, abilities, movement, UI
- **Positional audio**: Volume based on distance from player
- **Pitch variation**: Prevents repetition
- **Adaptive music**: Changes with combat intensity

Implementation in `audio.py`:
- `SoundSynthesizer` - Wave generation (numpy-based)
- `AudioManager` - Playback and mixing (singleton pattern)

Example usage:
```python
from audio import get_audio_manager
audio = get_audio_manager()
audio.play_attack_sound('heavy')
audio.play_hit_sound(is_crit=True, position=(x, y), player_position=(px, py))
```

### 3D Visual Effects
- **3D Physics**: Gravity, velocity, friction
- **Billboard sprites**: Always face camera
- **Particle Effects**:
  - Explosions with directional spray
  - Floating 3D text with depth
  - Trail ribbons for movement/abilities
  - Screen shake (camera wobble)
  - Alert particles ("!" above enemies)
  - Blood splatters and impact particles
  - Heal sparkles and status effects

### Field of View & Fog of War

- **Ray-casting FOV** algorithm in `fov.py`
- **Fog of War** system in `visibility.py`
- **Explored tiles** remain dimly visible (darker)
- **Dynamic lighting** reveals tiles as you move
- **3D visualization**: Unexplored areas completely hidden, explored areas darkened

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
| `audio.py` | Procedural audio system | `AudioManager`, `SoundSynthesizer` |

### 3D Rendering & UI

| File/Directory | Purpose |
|----------------|---------|
| `main.py` | Entry point (shows title screen, launches Ursina) |
| `main_3d.py` | Ursina game loop and input handling |
| `renderer3d.py` | 3D scene management and entity rendering |
| `ui3d_manager.py` | HUD overlay (stats, abilities, combat log, minimap) |
| `graphics3d/tiles.py` | 3D dungeon meshes (walls, floors, stairs) |
| `graphics3d/players/*.py` | 3D player models (4 classes) |
| `graphics3d/enemies/*.py` | 3D enemy models (6 types) |
| `graphics3d/items/*.py` | 3D item models (5 types + treasure chests) |
| `graphics3d/utils.py` | 3D utilities (coordinate conversion, colors) |
| `animations3d.py` | 3D particle effects with physics |
| `ui/screens/title_screen_3d.py` | PyQt6 OpenGL title screen (flying letters) |
| `ui/screens/class_selection_3d.py` | 3D class selection with rotating models |
| `ui/screens/main_menu_3d.py` | Main menu in Ursina |
| `ui/screens/pause_menu_3d.py` | Pause menu overlay |
| `ui/screens/victory_screen_3d.py` | Victory screen |
| `ui/screens/game_over_3d.py` | Game over screen |

### Support Systems

| File | Purpose |
|------|---------|
| `fov.py` | Field of view ray-casting |
| `visibility.py` | Fog of war and exploration tracking |
| `shaders/` | Custom GLSL shaders (barrel distortion, corner shadows) |

## 🛠️ Adding New Content

### Add a New Enemy

**1. Define in `constants.py`:**
```python
ENEMY_VAMPIRE = "vampire"
ENEMY_STATS[ENEMY_VAMPIRE] = {
    "hp": 80, "attack": 12, "defense": 6, "xp": 50
}
# RGB tuple for 3D color (0-1 range)
COLOR_ENEMY_VAMPIRE_RGB = (0.6, 0.0, 0.0)
```

**2. Create 3D model in `graphics3d/enemies/vampire.py`:**
```python
def create_vampire_model(x, y):
    """Create 3D vampire model"""
    from ursina import Entity, color
    model = Entity(model='cube', scale=(0.4, 0.6, 0.3),
                   color=color.rgb(153, 0, 0))  # Use 0-255 RGB!
    # Add details (fangs, cloak as child entities)
    return model
```

**3. Register in `graphics3d/enemies/__init__.py`:**
Add to `create_enemy_model_3d()` dispatcher function

**4. Update spawn logic in `game.py`:**
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

**2. Create 3D model in `graphics3d/items/helmet.py`**

**3. Register in `graphics3d/items/__init__.py`**

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

### Game Architecture
```
        ┌─────────────┐
        │   main.py   │  (Entry point: title screen → Ursina)
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  main_3d.py │  (Ursina game loop, input handling)
        └──────┬──────┘
               │
       ┌───────┴────────┬──────────────┐
       │                │              │
   ┌───▼───────┐  ┌────▼────────┐  ┌──▼──────────┐
   │  game.py  │  │renderer3d.py│  │ui3d_manager│
   │  (logic)  │  │  (3D scene) │  │  (HUD)     │
   └───────────┘  └─────────────┘  └────────────┘
```

### Key Design Patterns

1. **Singleton Pattern** - `AudioManager` via `get_audio_manager()`
2. **Proxy Pattern** - `AnimationManager3DProxy` bridges neutral interface to 3D
3. **Dispatcher Pattern** - `graphics3d/enemies/__init__.py` routes to specific model builders
4. **Entity-Component** - Base `Entity` class, specialized subclasses (Player, Enemy, Item)
5. **MVC Pattern** - Game logic (Model), Renderer (View), GameController (Controller)

### Animation & Movement System

All entities inherit smooth movement from `Entity` base class:
- **Grid position** - Logical position (int)
- **Display position** - Visual position (float, interpolated)
- **Idle animation** - Bob cycle for breathing effect
- **Facing direction** - Tracked for model orientation

Managed by `AnimationManager3D` in `animations3d.py`
- 3D particles with physics (gravity, velocity, friction)
- Billboard sprites (always face camera)
- Screen shake, trails, explosions, text

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

**Enable debug output:**
```python
# main_3d.py line 656
app = Ursina(development_mode=True)  # Shows FPS, entity count, wireframes
```

**Console logging is built-in:**
- Movement: `[MOVE] Player moved: (x, y)`
- Combat: `[COMBAT] Attacking enemy`
- Events: `[EVENT] Player on stairs`
- Camera: `[CAMERA] Rotating right to 90°`
- Heartbeat: `[HEARTBEAT] Frame 60 | FPS=45.2`

**Debug keys:**
- F1 - Reveal entire map (disable fog of war)
- F2 - Skip to next level (for testing)

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

- **Target**: 45+ FPS on modern hardware
- **Bottlenecks**: Particle count, entity count, FOV calculation
- **Optimizations**: Particle limits (max 500), conditional UI updates, model pooling

Typical performance:
- Desktop: 60 FPS with 50+ entities
- Laptop: 45 FPS with 50+ entities

## 🚧 Known Limitations

- Saving/loading not implemented (permadeath roguelike)
- No multiplayer (single-player only)
- No mod support (Python-based, hackable source code)
- Audio requires pygame (included in requirements)
- First-person only (no third-person camera mode)

## 📚 Additional Documentation

- **`CLAUDE.md`** - Quick developer onboarding and project structure

## 🎯 Design Philosophy

1. **No External Assets** - Everything procedurally generated (graphics, audio)
2. **Clean Separation** - Game logic independent of rendering layer
3. **First-Person Immersion** - True 3D dungeon crawler experience
4. **Modular Design** - Easy to add content (enemies, abilities, items)
5. **Type Safety** - Type hints on all functions
6. **Self-Documenting** - Clear naming, comprehensive docstrings

## 📝 Code Style

- **Type hints** on all function signatures
- **Docstrings** for all classes and public methods
- **Constants** in `UPPER_CASE` (see `constants.py`)
- **Private methods** prefixed with `_`
- **Colors**: RGB tuples (0-1 range for Ursina, 0-255 for ursina.color.rgb())

**IMPORTANT for Ursina colors:**
```python
# Correct - 0-255 range for ursina.color.rgb()
entity.color = color.rgb(128, 64, 200)

# Wrong - 0-1 range makes colors too bright
entity.color = color.rgb(0.5, 0.25, 0.8)  # Don't do this!
```

---

**For quick start and development guide:** See `CLAUDE.md`

Happy coding! 🎮
