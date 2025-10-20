# Creature Library

This directory contains the creature library system for organizing and managing enemy appearances.

## Directory Structure

- **`creations/`** - Individual creature preset files (JSON)
  - Created by exporting from the DNA editor
  - Contain creature type and all DNA parameters
  - Neutral presets (no enemy/level association)

- **`enemy_packs/`** - Complete enemy pack files (JSON)
  - Created by the Library Manager application
  - Define which creatures appear for which enemies at which levels
  - Can be loaded by the game (future feature)

## Workflow

1. **Create in DNA Editor**
   - Adjust creature parameters until it looks good
   - File → Save to Library (Ctrl+S)
   - Enter a descriptive name
   - Creation saved to `creations/` folder

2. **Organize in Library Manager**
   - Run `python dna_editor/library_manager.py`
   - Select enemy type (Orc, Slime, etc.)
   - Add level range mappings
   - Choose creature type and creation for each range
   - Save as enemy pack to `enemy_packs/` folder

3. **Use in Game** (Future)
   - Game will load enemy packs on startup
   - Enemies will use configured creatures at appropriate levels
   - Supports parameter interpolation between level ranges

## File Formats

### Creation JSON
```json
{
  "name": "Spiky Tentacle Basic",
  "creature_type": "tentacle",
  "parameters": {
    "num_tentacles": 4,
    "segments_per_tentacle": 10,
    ...
  }
}
```

### Enemy Pack JSON
```json
{
  "pack_name": "Default Pack",
  "version": "1.0",
  "enemies": {
    "ENEMY_ORC": {
      "mappings": [
        {
          "level_range": [1, 5],
          "creature_type": "tentacle",
          "parameters": {...},
          "creation_name": "Tentacle Basic"
        }
      ]
    }
  }
}
```
