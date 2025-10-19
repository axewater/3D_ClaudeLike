# Claude-Like Roguelike 🎮

A Python 3D first-person roguelike dungeon crawler built with Ursina Engine.

**100% procedurally generated** - graphics, audio, and voice taunts!

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python3 main.py

# Skip intro animation for faster startup
python3 main.py --skip-intro
```

## Project Structure

### Core Game Files
- **`game.py`** - Main game logic (turn-based, combat, dungeon management)
- **`entities.py`** - Player, Enemy, Item classes
- **`dungeon.py`** - Procedural dungeon generation (BSP algorithm)
- **`abilities.py`** - Class abilities and cooldown system
- **`combat.py`** - Damage calculations
- **`constants.py`** - All configuration and game constants

### 3D Rendering & UI
- **`main.py`** - Entry point (shows title screen, launches Ursina)
- **`main_3d.py`** - Ursina game loop and input handling
- **`renderer3d.py`** - 3D scene management and entity rendering
- **`ui3d_manager.py`** - HUD overlay (stats, abilities, combat log, minimap)
- **`graphics3d/`** - 3D models (procedurally generated, no .obj files)
- **`animations3d.py`** - 3D particle effects with physics
- **`ui/screens/`** - Menu screens (title, class selection, pause, victory, game over)

### Support Systems
- **`audio.py`** - Procedural sound synthesis (no audio files needed!) + voice taunts
- **`fov.py`** / **`visibility.py`** - Field of view and fog of war
- **`shaders/`** - Custom GLSL shaders (barrel distortion, corner shadows)

## Documentation

- **`README.md`** - Complete feature documentation and file reference
- **`CLAUDE.md`** - This file (quick developer onboarding)

## Current Status

**✅ COMPLETE** - Fully playable 3D first-person roguelike!

### Features Implemented
- ✅ Dungeon rendering (walls, floors, stairs) with biome variations
- ✅ **First-person camera** with smooth rotation (arrow keys, 90° snaps)
- ✅ **Directional WASD movement** (camera-relative)
- ✅ **Camera pitch tilt** (auto-focus on enemies ahead)
- ✅ Combat system (bump-to-attack)
- ✅ Enemy AI and 3D models with health bars and alert particles
- ✅ Item models with rarity-based visuals
- ✅ Particle effects (explosions, trails, text, blood splatters)
- ✅ Level progression (25 levels, 5 biomes)
- ✅ **Full UI overlay** (stats, abilities, combat log, minimap)
- ✅ **Ability targeting system** (1/2/3 keys + mouse)
- ✅ **Performance optimizations** (particle limits, conditional UI updates)
- ✅ **FOV/Fog of War** in 3D with visibility tracking
- ✅ **Class selection screen** with rotating 3D models
- ✅ **Title screen** (PyQt6 OpenGL flying letters)
- ✅ **Menu screens** (main menu, pause, victory, game over)
- ✅ **Audio system** (procedural SFX, music, voice taunts)

## Architecture Notes

### 3D First-Person Design
The game uses a clean MVC-style architecture:
- **Game logic** (`game.py`) - Renderer-agnostic, handles turns and state
- **3D Renderer** (`renderer3d.py`) - Ursina Entity system, scene management
- **UI Overlay** (`ui3d_manager.py`) - HUD elements (stats, abilities, combat log)
- **Controller** (`main_3d.py`) - Input handling, camera control

### Animation System
The `AnimationManager3DProxy` in `main_3d.py` bridges neutral interface to 3D:
- Converts RGB tuples to Ursina colors
- Translates grid coords to 3D world space
- Allows `game.py` to remain rendering-agnostic

### No External Assets
- **Graphics**: All 3D models procedurally generated (no .obj/.fbx files)
- **Audio**: All sounds procedurally synthesized (no .wav/.mp3 files)
- **Voices**: Text-to-speech using pyttsx3 (no voice recordings)
- **Textures**: Ursina primitive shapes with color/materials

## Development Workflow

1. **Game logic first** - All features implemented in `game.py`
2. **3D rendering** - Visualized in `renderer3d.py` and `graphics3d/`
3. **Audio integration** - Triggered from `game.py` and `abilities.py`
4. **Test on Windows** - User tests on their machine (headless server for dev)

## Key Technologies

- **Python 3.8+**
- **Ursina Engine** - 3D rendering (built on Panda3D)
- **PyQt6** - Title screen with OpenGL (flying letters effect)
- **pygame** - Audio playback
- **numpy** - Sound wave synthesis
- **pyttsx3** - Text-to-speech for voice taunts

## Controls

- **WASD** - Move (camera-relative direction)
- **Arrow Keys** - Rotate camera 90° / Move forward-backward
- **1/2/3** - Use abilities (click to target)
- **Mouse** - Aim targeting reticle
- **ESC** - Cancel targeting / Pause menu
- **F1** - Debug: Reveal full map
- **F2** - Debug: Skip to next level

---

**For detailed feature documentation:** See `README.md`

## Development Notes
- You are working in a Linux shell on a headless server
- User performs all testing on Windows
- Activate `venv_linux` if you need to test library imports