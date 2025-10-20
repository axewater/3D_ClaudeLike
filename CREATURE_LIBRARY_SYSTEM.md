# DNA Creatures Library System - Complete Guide

## Overview

This system allows you to create custom creature appearances in the DNA Editor, organize them into enemy packs, and (future) load them in the game for level-specific enemy customization.

## Complete Workflow

### 1. Create Creatures (DNA Editor)

```bash
python dna_editor/main_qt.py
```

**Steps:**
1. Select creature type (Tentacle, Blob, Polyp, Starfish, Medusa, Dragon)
2. Adjust parameters until it looks perfect
3. **File → Save to Library** (Ctrl+S)
4. Enter a descriptive name (e.g., "Tentacle Nightmare Level 20")
5. Creation saved to `dna_editor/library/creations/`

**Note:** You can also use **File → Export JSON** (Ctrl+E) for standalone exports, but **Save to Library** is the preferred method for the creature library system.

### 2. Organize Enemy Packs (Library Manager)

```bash
python dna_editor/library_manager.py
```

**Features:**
- 6 tabs for each enemy type (Startle, Slime, Skeleton, Orc, Demon, Dragon)
- Each tab shows the **game spawn range** for that enemy
- Add level range mappings with creature assignments
- Choose any creature type for any enemy (flexible remapping)
- Parameter interpolation between level ranges

**Enemy Spawn Ranges in Game:**

| Enemy Type | Display Name | Creature Type | Spawn Levels | Notes |
|------------|--------------|---------------|--------------|-------|
| ENEMY_STARTLE | Startle | Starfish | **1-5** | Early game only |
| ENEMY_SLIME | Slimey | Blob | **1-5** | Early game only |
| ENEMY_SKELETON | Polypian | Polyp | **2-14** | Mid game |
| ENEMY_ORC | Tentacle | Tentacle | **4-19** | Mid to late |
| ENEMY_DEMON | Medusa | Medusa | **6-25** | Late game dominant |
| ENEMY_DRAGON | Dragon | Dragon | **10-25** | End game boss |

**Key Points:**
- You **only need to configure the levels where enemies actually appear**
- Dragons only spawn levels 10-25, so you don't need mappings for levels 1-9
- Empty mappings = game uses default procedural generation
- Partial coverage = configured levels use your creations, rest use defaults

**Example Dragon Configuration:**
```
Dragon Tab:
  Game Spawn Range: Levels 10-25

  Mappings:
    Level 10-15: Dragon, "Dragon Basic"
    Level 16-25: Dragon, "Dragon Nightmare"
```

### 3. Save Enemy Pack

**File → Save Pack** (Ctrl+S)
- Validates all mappings (warnings only, won't block save)
- Saves to `dna_editor/library/enemy_packs/`
- JSON format for version control

**Validation Messages:**
- ✅ **"No mappings defined (will use default generation)"** - OK, enemy uses procedural gen
- ⚠️ **"Partial coverage"** - Some levels configured, rest use defaults
- ⚠️ **"Extends outside spawn range"** - You configured levels where enemy doesn't spawn
- ❌ **"Invalid creature type"** - Typo in creature type name

## File Structure

```
dna_editor/
├── library/
│   ├── creations/              # Individual creature presets
│   │   ├── tentacle_basic.json
│   │   ├── tentacle_advanced.json
│   │   ├── blob_simple.json
│   │   ├── dragon_basic.json
│   │   └── ...
│   │
│   ├── enemy_packs/            # Complete enemy configurations
│   │   ├── default_pack.json
│   │   └── nightmare_mode.json
│   │
│   └── README.md
│
├── models/
│   └── library_data.py         # Data classes (Creation, EnemyMapping, EnemyPack)
│
├── library_manager.py          # GUI application
└── qt_ui/
    └── editor_window.py        # DNA Editor with "Save to Library"
```

## JSON File Formats

### Creation File
```json
{
  "name": "Tentacle Basic",
  "creature_type": "tentacle",
  "parameters": {
    "num_tentacles": 4,
    "segments_per_tentacle": 10,
    "algorithm": "bezier",
    "thickness_base": 0.2,
    "tentacle_color": [0.6, 0.3, 0.7],
    ...
  }
}
```

### Enemy Pack File
```json
{
  "pack_name": "Default Enemy Pack",
  "version": "1.0",
  "enemies": {
    "ENEMY_DRAGON": {
      "mappings": [
        {
          "level_range": [10, 15],
          "creature_type": "dragon",
          "creation_name": "Dragon Basic",
          "parameters": { ... }
        },
        {
          "level_range": [16, 25],
          "creature_type": "dragon",
          "creation_name": "Dragon Nightmare",
          "parameters": { ... }
        }
      ]
    }
  }
}
```

## Level Range & Interpolation

### How It Works

When you define level ranges with gaps, the system interpolates parameters:

**Example:**
```
Level 1-5:   num_tentacles = 2
Level 11-15: num_tentacles = 12

Level 8 (in gap): interpolated to ~7 tentacles
```

**Interpolation Rules:**
- **Integers** (num_tentacles, segments): Linear interpolation, rounded
- **Floats** (thickness, scale): Linear interpolation
- **Colors** (RGB tuples): Per-channel interpolation
- **Strings** (algorithm): Nearest neighbor (no interpolation)
- **Dicts** (algorithm_params): Recursive interpolation

## Tips & Best Practices

### For Dragons (Late Game Only)

Since dragons only spawn levels 10-25:
- **Don't configure levels 1-9** (they won't spawn anyway)
- **Start at level 10** for first appearance
- **Use 2-3 ranges** for progression:
  - 10-15: Dragon Basic
  - 16-20: Dragon Intermediate
  - 21-25: Dragon Nightmare

### For Early Game (Startle/Slime)

Since they only spawn levels 1-5:
- **One range is often enough** (1-5 with same appearance)
- **Or use 2 ranges** for variety:
  - 1-3: Simple version
  - 4-5: Slightly tougher

## Future: Game Integration

**Coming Next:** Modify `graphics3d/enemies/creature_factory.py` to:
1. Load enemy pack on game start
2. Look up creature parameters by enemy type + level
3. Use interpolation for levels between ranges
4. Fall back to procedural generation for unconfigured enemies/levels

## Version History

**v1.0** (2025-10-20)
- Initial implementation
- DNA Editor "Save to Library" feature
- Library Manager with 6 enemy tabs
- Spawn range awareness
- Flexible validation (warnings only)
- Interpolation system
- Sample creations and default pack
