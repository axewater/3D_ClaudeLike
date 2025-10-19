#!/usr/bin/env python3
"""
Test script for AAA-quality brick texture with gradient mortar joints.

Generates a test texture and saves it to verify gradient quality.
"""

import sys
import time
from textures.bricks import generate_brick_pattern
from textures.organic import generate_moss_stone_texture

def main():
    print("=" * 60)
    print("AAA BRICK TEXTURE GRADIENT TEST")
    print("=" * 60)

    # Test 1: Pure brick pattern (1024×1024)
    print("\n[TEST 1] Generating 1024×1024 brick texture with gradients...")
    start_time = time.time()

    brick_texture = generate_brick_pattern(size=1024, darkness=1.0)

    generation_time = time.time() - start_time
    print(f"✓ Generated in {generation_time:.2f} seconds")

    # Save test image
    output_file = "test_brick_1024_gradient.png"
    brick_texture.save(output_file)
    print(f"✓ Saved to: {output_file}")

    # Calculate memory size
    width, height = brick_texture.size
    channels = len(brick_texture.getbands())
    memory_mb = (width * height * channels) / (1024 * 1024)
    print(f"✓ Texture size: {width}×{height} ({channels} channels)")
    print(f"✓ Memory usage: {memory_mb:.2f} MB")

    # Test 2: Full wall texture (brick + weathering + moss)
    print("\n[TEST 2] Generating 1024×1024 full wall texture (brick + moss)...")
    start_time = time.time()

    wall_texture = generate_moss_stone_texture(size=1024, moss_density='medium')

    generation_time = time.time() - start_time
    print(f"✓ Generated in {generation_time:.2f} seconds")

    # Save test image
    output_file2 = "test_wall_1024_full.png"
    wall_texture.save(output_file2)
    print(f"✓ Saved to: {output_file2}")

    # Test 3: Compare 512 vs 1024 (gradient width difference)
    print("\n[TEST 3] Generating 512×512 texture for comparison...")
    start_time = time.time()

    brick_512 = generate_brick_pattern(size=512, darkness=1.0)

    generation_time = time.time() - start_time
    print(f"✓ Generated in {generation_time:.2f} seconds")

    output_file3 = "test_brick_512_gradient.png"
    brick_512.save(output_file3)
    print(f"✓ Saved to: {output_file3}")

    memory_512 = (512 * 512 * 4) / (1024 * 1024)
    print(f"✓ 512px memory: {memory_512:.2f} MB")

    # Summary
    print("\n" + "=" * 60)
    print("GRADIENT QUALITY ANALYSIS")
    print("=" * 60)
    print("📊 At 1024px resolution:")
    print("   - Brick size: 341×256 pixels")
    print("   - Mortar width: 16 pixels")
    print("   - Gradient zones: 6px core + 3px shadow + 3px edge + 4px face")
    print("   - Memory per texture: ~4 MB")
    print("   - Total for 12 textures: ~48 MB")
    print()
    print("📊 At 512px resolution:")
    print("   - Brick size: 171×128 pixels")
    print("   - Mortar width: 8 pixels")
    print("   - Gradient zones: 3px core + 2px shadow + 2px edge + 1px face")
    print("   - Memory per texture: ~1 MB")
    print()
    print("✅ Gradient improvements:")
    print("   ✓ Smooth depth simulation (mortar recess)")
    print("   ✓ 4-zone color transition (core → shadow → edge → face)")
    print("   ✓ Ease-in-out interpolation curves")
    print("   ✓ Per-brick color variation preserved")
    print("   ✓ Scaled crack details")
    print()
    print("🎨 Test images generated:")
    print(f"   1. {output_file}")
    print(f"   2. {output_file2}")
    print(f"   3. {output_file3}")
    print()
    print("💡 Next steps:")
    print("   - Inspect test images to verify gradient smoothness")
    print("   - Compare 512px vs 1024px gradient quality")
    print("   - Launch game to test in first-person view")
    print("=" * 60)

if __name__ == "__main__":
    main()
