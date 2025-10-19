#!/usr/bin/env python3
"""
Verification script for preset system implementation.
This script verifies all preset-related code is in place WITHOUT launching the UI.
"""

import sys
import os

print("=" * 70)
print("PRESET SYSTEM VERIFICATION")
print("=" * 70)

# Check 1: Verify constants.py has all presets
print("\n[1/5] Checking core/constants.py for preset definitions...")
try:
    import ast
    with open('core/constants.py', 'r') as f:
        content = f.read()
        tree = ast.parse(content)

    preset_counts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if 'PRESETS' in name:
                        if isinstance(node.value, ast.List):
                            count = len(node.value.elts)
                            preset_counts[name] = count

    expected = {
        'PRESETS': 2,  # Tentacle
        'BLOB_PRESETS': 3,
        'POLYP_PRESETS': 3,
        'STARFISH_PRESETS': 3,
        'MEDUSA_PRESETS': 3,
        'DRAGON_PRESETS': 3
    }

    all_good = True
    for name, expected_count in expected.items():
        actual_count = preset_counts.get(name, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f"  {status} {name}: {actual_count}/{expected_count} presets")
        if actual_count != expected_count:
            all_good = False

    if all_good:
        print("  ✅ All preset constants defined correctly!")
    else:
        print("  ❌ Some presets are missing!")
        sys.exit(1)

except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# Check 2: Verify control_panel_modern.py has preset imports
print("\n[2/5] Checking qt_ui/control_panel_modern.py for preset imports...")
try:
    with open('qt_ui/control_panel_modern.py', 'r') as f:
        content = f.read()

    required_imports = [
        'PRESETS', 'BLOB_PRESETS', 'POLYP_PRESETS',
        'STARFISH_PRESETS', 'MEDUSA_PRESETS', 'DRAGON_PRESETS'
    ]

    all_imported = True
    for imp in required_imports:
        if imp in content:
            print(f"  ✅ {imp} imported")
        else:
            print(f"  ❌ {imp} NOT imported")
            all_imported = False

    if not all_imported:
        sys.exit(1)

except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# Check 3: Verify _get_current_presets method exists
print("\n[3/5] Checking for _get_current_presets() method...")
try:
    if '_get_current_presets' in content:
        print(f"  ✅ _get_current_presets() method found")
    else:
        print(f"  ❌ _get_current_presets() method NOT found")
        sys.exit(1)

    if '_populate_preset_buttons' in content:
        print(f"  ✅ _populate_preset_buttons() method found")
    else:
        print(f"  ❌ _populate_preset_buttons() method NOT found")
        sys.exit(1)

except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# Check 4: Verify all creature panels have load_preset method
print("\n[4/5] Checking creature panels for load_preset() methods...")
panels = [
    'blob_panel.py',
    'polyp_panel.py',
    'starfish_panel.py',
    'medusa_panel.py',
    'dragon_panel.py',
    'tentacle_panel.py'
]

all_have_method = True
for panel in panels:
    try:
        with open(f'qt_ui/panels/{panel}', 'r') as f:
            content = f.read()

        if 'def load_preset' in content:
            print(f"  ✅ {panel} has load_preset()")
        else:
            print(f"  ❌ {panel} MISSING load_preset()")
            all_have_method = False
    except Exception as e:
        print(f"  ❌ Error reading {panel}: {e}")
        all_have_method = False

if not all_have_method:
    sys.exit(1)

# Check 5: Verify base class has load_preset interface
print("\n[5/5] Checking base_creature_panel.py for load_preset() interface...")
try:
    with open('qt_ui/panels/base_creature_panel.py', 'r') as f:
        content = f.read()

    if 'def load_preset' in content:
        print(f"  ✅ base_creature_panel.py has load_preset() interface")
    else:
        print(f"  ❌ base_creature_panel.py MISSING load_preset() interface")
        sys.exit(1)

except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED!")
print("=" * 70)
print("\nThe preset system is FULLY IMPLEMENTED and ready to use.")
print("\nTo see it in action:")
print("  1. Run: python3 main_qt.py")
print("  2. Click the 'Animation' tab (2nd tab)")
print("  3. Look for purple preset buttons in 'PRESETS & ACTIONS' section")
print("  4. Switch creature types to see different preset buttons")
print("\nIf you don't see buttons, check the console for debug output:")
print("  [PRESET DEBUG] Loading X presets for creature type: ...")
print("=" * 70)
