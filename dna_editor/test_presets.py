#!/usr/bin/env python3
"""Test preset loading."""

import sys
sys.path.insert(0, '/var/www/claudelike/3droguelike/dna_editor')

from core.constants import (
    PRESETS, BLOB_PRESETS, POLYP_PRESETS, STARFISH_PRESETS,
    MEDUSA_PRESETS, DRAGON_PRESETS
)

print("=== PRESET TEST ===")
print(f"\nTentacle PRESETS: {len(PRESETS)} presets")
for preset in PRESETS:
    print(f"  - {preset[0]}")

print(f"\nBLOB_PRESETS: {len(BLOB_PRESETS)} presets")
for preset in BLOB_PRESETS:
    print(f"  - {preset[0]}")

print(f"\nPOLYP_PRESETS: {len(POLYP_PRESETS)} presets")
for preset in POLYP_PRESETS:
    print(f"  - {preset[0]}")

print(f"\nSTARFISH_PRESETS: {len(STARFISH_PRESETS)} presets")
for preset in STARFISH_PRESETS:
    print(f"  - {preset[0]}")

print(f"\nMEDUSA_PRESETS: {len(MEDUSA_PRESETS)} presets")
for preset in MEDUSA_PRESETS:
    print(f"  - {preset[0]}")

print(f"\nDRAGON_PRESETS: {len(DRAGON_PRESETS)} presets")
for preset in DRAGON_PRESETS:
    print(f"  - {preset[0]}")

print("\n✅ All presets loaded successfully!")
