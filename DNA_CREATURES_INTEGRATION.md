# DNA Creatures Integration - Testing Guide

## Overview
DNA editor creatures have been integrated into the roguelike game with level-based scaling and attack animations.

## What Was Changed

### New Files
1. **`graphics3d/enemies/creature_factory.py`** - DNA generation factory
   - Maps enemy types to creature types
   - Generates level-scaled DNA parameters
   - Creates creature instances

### Modified Files
1. **`graphics3d/enemies/base.py`**
   - Added `dungeon_level` parameter to `create_enemy_model_3d()`
   - Added DNA creature support with fallback to legacy models
   - Updated `update_enemy_animation()` to handle both systems

2. **`renderer3d.py`**
   - Stores creature objects in `enemy_entities` dict
   - Added `trigger_enemy_attack()` method
   - Passes camera position to creature animations
   - Uses `current_level` for scaling

3. **`game.py`**
   - Triggers attack animations when enemies attack player (line 476-479)

4. **`main_3d.py`**
   - Stores renderer reference in game object (line 183)

---

## Enemy → Creature Mapping

| Enemy Type | Creature Type | Description |
|-----------|--------------|-------------|
| Goblin | BlobCreature | Green slime blob |
| Slime | BlobCreature | Translucent blob (80% transparent) |
| Skeleton | PolypCreature | Bone-white polyp stack |
| Orc | TentacleCreature | Muscular tentacle mass |
| Demon | MedusaCreature | Demonic medusa |
| Dragon | DragonCreature | Segmented serpent |

---

## Level Scaling Tiers

### Level 1-5 (Dungeon Biome) - **BASIC**
- Tentacles: 2
- Eyes: 1
- Segments: 8
- Body scale: 1.0
- Simple, manageable creatures

### Level 6-10 (Catacombs Biome) - **MODERATE**
- Tentacles: 4
- Eyes: 2
- Segments: 12
- Body scale: 1.2
- Noticeable increase

### Level 11-15 (Caves Biome) - **ADVANCED**
- Tentacles: 6
- Eyes: 4
- Segments: 14
- Body scale: 1.3
- Intimidating

### Level 16-20 (Hell Biome) - **HORRIFIC**
- Tentacles: 9
- Eyes: 6
- Segments: 16
- Body scale: 1.4
- Nightmare fuel

### Level 21-25 (Abyss Biome) - **NIGHTMARE**
- Tentacles: 12
- Eyes: 8
- Segments: 18
- Body scale: 1.5
- Maximum horror

---

## Testing Checklist

### Basic Functionality
- [ ] Game starts without errors
- [ ] Enemies spawn with DNA creatures
- [ ] Level 1 creatures look simple (2 tentacles, 1 eye)
- [ ] Creatures are positioned correctly in 3D space
- [ ] Health bars display above creatures
- [ ] Creatures animate (idle breathing/movement)

### Level Progression
- [ ] Descend to level 5 - creatures should be larger
- [ ] Descend to level 10 - noticeable complexity increase
- [ ] Descend to level 15 - creatures look intimidating
- [ ] Descend to level 20 - nightmare difficulty
- [ ] Descend to level 25 - maximum complexity

### Attack Animations
- [ ] Walk into enemy - enemy should NOT attack (player attacks first)
- [ ] Wait for enemy to bump into player
- [ ] Enemy attack animation triggers (tentacles lash out)
- [ ] Animation completes before returning to idle
- [ ] Combat particles still appear
- [ ] Damage numbers still display

### Performance
- [ ] No FPS drop with 10+ creatures visible
- [ ] Attack animations don't cause stuttering
- [ ] Game runs smoothly on level 25 (max complexity)

### Visual Quality
- [ ] Creatures match enemy colors (green goblins, white skeletons, etc.)
- [ ] Transparency works (slimes should be more transparent than goblins)
- [ ] Toon shader applied correctly
- [ ] Creatures face correct direction

---

## Troubleshooting

### Creatures Don't Appear
**Check console for errors:**
```
⚠ DNA creature creation failed, falling back to legacy: [error message]
```

**Solution:** Check that DNA editor models are importable

### Attack Animations Don't Trigger
**Check console for:**
```
✓ Triggered attack animation for [enemy_type]
```

**If missing:**
1. Verify `game.renderer` exists
2. Check `trigger_enemy_attack()` is called in `game.py:476`
3. Ensure enemy has `start_attack()` method

### Creatures Look Wrong
**Check level scaling:**
- Level 1 should have 2 tentacles, not 12
- Verify `current_level` is correct

### Performance Issues
**If FPS drops:**
1. Reduce max enemies per level in `constants.py`
2. Lower segment counts in `creature_factory.py`
3. Disable branching for lower levels

---

## Tuning Parameters

### Quick Adjustments

**Make creatures simpler (better performance):**
```python
# In creature_factory.py, reduce max values:
segments = 8 + int((level / 5.0))  # Was level/3.0 (slower growth)
num_tentacles = 2 + int((level / 8.0) * 2)  # Was level/5.0
```

**Make creatures scarier faster:**
```python
# Faster scaling:
segments = 8 + int((level / 2.0))  # Was level/3.0
num_tentacles = 2 + int((level / 3.0) * 2)  # Was level/5.0
```

**Change creature mapping:**
```python
# In creature_factory.py, line 15:
ENEMY_CREATURE_MAP = {
    c.ENEMY_GOBLIN: 'starfish',  # Change goblin to starfish
    # ... etc
}
```

### Toggle System

**Switch back to legacy models:**
```python
# In renderer3d.py, line 283:
use_dna_creatures=False  # Was True
```

**Disable attack animations:**
```python
# In game.py, line 476-479:
# Comment out these lines:
# if hasattr(self, 'renderer') and self.renderer:
#     enemy_id = id(enemy)
#     self.renderer.trigger_enemy_attack(enemy_id)
```

---

## Advanced: Per-Enemy Randomization

To add variety within each level, modify `creature_factory.py`:

```python
import random

def generate_tentacle_dna(level: int, color_rgb: tuple) -> dict:
    # ... existing code ...

    # Add ±1 tentacle variation
    num_tentacles += random.randint(-1, 1)
    num_tentacles = max(2, min(12, num_tentacles))

    # Add ±1 eye variation
    num_eyes += random.randint(-1, 1)
    num_eyes = max(1, min(8, num_eyes))

    # ... rest of code ...
```

---

## Performance Metrics

**Expected performance:**
- Creature generation: < 10ms per enemy
- 10 creatures visible: 60 FPS
- Attack animation: No stutter
- Memory: ~50KB per creature

**If slower:**
- Reduce `segments_per_tentacle` (biggest impact)
- Reduce `branch_depth` to 0 or 1
- Disable connector tubes in BlobCreature

---

## Debug Output

When creatures spawn, you should see:
```
✓ Created blob creature for goblin (level 5): 2 complexity
✓ Created tentacle creature for orc (level 10): 4 complexity
✓ Created dragon creature for dragon (level 15): 20 complexity
```

When enemies attack:
```
  ✓ Triggered attack animation for orc
```

---

## Known Issues / Future Improvements

1. **All creatures use Attack 1 only**
   - Attack 2 is available but not used (many are duplicates)
   - Could randomize between Attack 1 and 2

2. **No per-enemy DNA variation**
   - All level 10 orcs look identical
   - Could add randomization (see Advanced section)

3. **Static color mapping**
   - Colors from `constants.py` are fixed
   - Could vary hue based on level/biome

4. **No death animations**
   - Creatures just disappear when killed
   - Could add death animation to DNA creatures

---

## Contact

If you encounter issues:
1. Check console output for error messages
2. Verify syntax with `python3 -m py_compile [file]`
3. Test with `use_dna_creatures=False` to isolate DNA creature issues
4. Post issues with console output and reproduction steps

---

**Implementation Date:** 2025-10-19
**Version:** 1.0
**Status:** ✅ Complete - Ready for testing
