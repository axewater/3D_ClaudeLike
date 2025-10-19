# Bump Mapping Implementation Plan

**Project:** 3D Roguelike Dungeon Crawler
**Feature:** Advanced Wall Texture Detail via Bump/Height Mapping
**Prerequisites:** GLSL shader knowledge, Panda3D rendering pipeline understanding


---

## Overview

### Goal
Add true 3D depth perception to dungeon walls using height maps and normal maps, making brick surfaces appear physically raised/recessed without adding geometry.

### What You'll Build
- **Height map generator** - Grayscale images where brightness = surface height
- **Normal map generator** - RGB images encoding surface orientation vectors
- **GLSL shader** - Implements parallax occlusion mapping for depth illusion
- **Texture pipeline integration** - Extends existing procedural system

### Ursina/Panda3D Integration
**Rendering engine:** Panda3D (Ursina is a wrapper)
**Shader system:** GLSL 1.30+ (OpenGL 3.0+)
**Texture binding:** Ursina handles automatically, access via `p3d_TextureN` in shaders

---

## Implementation Strategy

### Phased Approach (Incremental Development)

#### Phase 1: Height Map Generation (2-3 hours)
- Generate grayscale height maps from existing texture generation
- Save/cache height maps alongside color textures
- Visual verification (display height maps as images)

#### Phase 2: Normal Map Generation (2-3 hours)
- Convert height maps to normal maps (Sobel edge detection)
- Implement RGB encoding of normal vectors
- Visual verification (normal maps should look purple/blue-ish)

#### Phase 3: Basic Normal Mapping Shader (2-3 hours)
- Write GLSL vertex/fragment shaders
- Pass normal map as second texture
- Implement per-pixel lighting using normals
- Test with existing dungeon lighting

#### Phase 4: Parallax Occlusion Mapping (3-4 hours)
- Extend shader with height-based UV offset
- Implement ray-marching for accurate depth
- Add self-shadowing for realism
- Performance optimization (adjustable quality settings)

#### Phase 5: Integration & Polish (1-2 hours)
- Hook into texture generation pipeline
- Update wall mesh creation
- Add quality settings (high/medium/low)
- Performance testing

---

## Step-by-Step Guide

### Step 1: Generate Height Maps from Existing Textures

**Location:** Create new file `textures/height_maps.py`

**What to implement:**
```python
def generate_height_map_from_texture(color_image: Image.Image) -> Image.Image:
    """
    Convert color texture to grayscale height map.

    Height interpretation:
    - Bricks = High (white/light gray)
    - Mortar = Low (dark gray)
    - Moss = Medium-High (medium gray)
    - Cracks = Very Low (black)

    Returns:
        PIL Image in 'L' mode (8-bit grayscale)
    """
    pass
```

**Algorithm approach:**
1. Convert color image to grayscale (use luminance formula)
2. Apply edge detection to find brick/mortar boundaries
3. Boost contrast (bricks should be 200-255, mortar 0-50)
4. Apply Gaussian blur for smooth transitions
5. Optional: Use alpha channel for moss height


---

### Step 6: Handle Tangent Vectors

**CRITICAL:** Normal mapping requires tangent vectors for the TBN matrix.

**Problem:** Ursina's built-in `'cube'` model may not have tangents.

---

## Integration Points

### Files to Modify

1. **`textures/height_maps.py`** - CREATE NEW (height/normal generation)
2. **`shaders/normal_mapping.py`** - CREATE NEW (GLSL shaders)
3. **`graphics3d/tiles.py`** - MODIFY (lines 26-62, 120-151)
4. **`requirements.txt`** - ADD `scipy` dependency

---

## Resources

### GLSL Shader Tutorials
- **Learn OpenGL - Normal Mapping:** https://learnopengl.com/Advanced-Lighting/Normal-Mapping
- **Learn OpenGL - Parallax Mapping:** https://learnopengl.com/Advanced-Lighting/Parallax-Mapping
- **Panda3D Shader Reference:** https://docs.panda3d.org/1.10/python/programming/shaders/index

### Height/Normal Map Tools
- **Online normal map generator:** https://cpetry.github.io/NormalMap-Online/
- **Visual normal map reference:** http://wiki.polycount.com/wiki/Normal_Map_Technical_Details

### Procedural Texture References
- **PIL ImageFilter docs:** https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html
- **NumPy convolution:** https://numpy.org/doc/stable/reference/generated/numpy.convolve.html
- **Sobel operator:** https://en.wikipedia.org/wiki/Sobel_operator

### Debugging Tools
- **RenderDoc** - Graphics debugger (can inspect shaders/textures): https://renderdoc.org/
- **Panda3D PStats** - Performance profiler: https://docs.panda3d.org/1.10/python/tools/pstats

---
