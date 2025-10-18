# Claude-Like Roguelike 🎮

A Python roguelike game with both 2D (PyQt6) and 3D (Ursina Engine) rendering modes.

**NEW**: 3D first-person mode is now fully playable!

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in 3D mode (first-person, recommended)
python3 main.py --mode 3d

# Run in 2D mode (classic version)
python3 main.py --mode 2d
```

## Project Structure

### Core Game Files
- **`game.py`** - Main game logic (turn-based, combat, dungeon management)
- **`entities.py`** - Player, Enemy, Item classes
- **`dungeon.py`** - Procedural dungeon generation
- **`abilities.py`** - Class abilities and cooldown system
- **`combat.py`** - Damage calculations
- **`constants.py`** - All configuration and game constants

### 2D Rendering (Complete)
- **`ui/`** - PyQt6 UI (screens, widgets, menus)
- **`graphics/`** - 2D geometric shape rendering
- **`animations.py`** - 2D particle effects

### 3D Rendering (In Development)
- **`main_3d.py`** - 3D mode entry point
- **`renderer3d.py`** - Ursina 3D rendering manager
- **`graphics3d/`** - 3D models (procedurally generated)
- **`animations3d.py`** - 3D particle effects

### Support Systems
- **`audio.py`** - Procedural sound synthesis (no audio files needed!)
- **`fov.py`** / **`visibility.py`** - Field of view and fog of war

## Documentation

- **`README.md`** - Complete feature documentation and file reference
- **`MIGRATION.md`** - 3D migration project plan and roadmap
- **`docs_archive_2025-10-12/`** - Archived phase summaries and old docs

## Current Status

**2D Mode**: ✅ Complete - Fully playable with all features
**3D Mode**: ✅ 80% Complete - Fully playable first-person mode!

### What Works in 3D (Phase 1-6.5 Complete)
- ✅ Dungeon rendering (walls, floors, stairs)
- ✅ **First-person camera** with smooth rotation (arrow keys)
- ✅ **Directional WASD movement** (camera-relative)
- ✅ Combat system (bump-to-attack)
- ✅ Enemy AI and 3D models with health bars
- ✅ Item models with animations
- ✅ Particle effects (explosions, trails, text)
- ✅ Level progression
- ✅ **Full UI overlay** (stats, abilities, combat log)
- ✅ **Ability targeting system** (1/2/3 keys + mouse)
- ✅ **Performance optimizations** (particle limits, conditional UI updates)
- ✅ FOV/Fog of War in 3D 
- ✅ Class selection screen 

### What's Missing in 3D (Optional Polish)

- ❌ Title/Victory/Menu screens (Phase 7)
- ❌ 3D positional audio (Phase 8 - optional)

See `MIGRATION.md` for the complete development roadmap.

## Architecture Notes

### Dual Rendering
The game supports both 2D and 3D rendering:
- **Game logic** (`game.py`) is renderer-agnostic
- **2D mode** uses PyQt6 widgets
- **3D mode** uses Ursina Entity system
- Mode selection via `--mode` flag in `main.py`

### Particle System Bridging
The `AnimationManager3DProxy` in `main_3d.py` converts 2D particle calls to 3D:
- Converts PyQt6 `QColor` to RGB tuples
- Translates pixel coords to 3D world space
- Allows `game.py` to remain unchanged

### No External Assets
- **Graphics**: All 3D models procedurally generated (no .obj files)
- **Audio**: All sounds procedurally synthesized (no .wav files)
- **Textures**: Ursina primitive shapes with color/materials

## Development Workflow

1. **2D is the reference** - All features work in 2D
2. **3D mirrors 2D** - Porting features from 2D to 3D
3. **Game logic unchanged** - Only rendering layer modified
4. **Test both modes** - Ensure 2D doesn't break

## Key Technologies

- **Python 3.8+**
- **PyQt6** - 2D UI and rendering
- **Ursina Engine** - 3D rendering (built on Panda3D)
- **pygame** - Audio playback
- **numpy** - Sound wave synthesis

---

**For detailed feature documentation:** See `README.md`
**For migration progress:** See `MIGRATION.md`

Notes:
- You are working in a Linux shell on a headless server. You must ask the user to perform any testing (its done on windows)
- If you need to load libraries or test other stuff from the command line, activate the "venv_linux"