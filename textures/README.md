# Procedural Texture Generation System

Port of the stunning procedural textures from the OpenGL title screen (`ui/screens/title_screen_3d.py`) to PIL/Pillow for use throughout the Ursina-based 3D game.

## Status

**Phase 1: Infrastructure ✅ COMPLETE**
- Base classes and utilities implemented
- Public API defined (stub functions)
- Testing framework in place

**Phase 2: Brick Patterns ✅ COMPLETE**
- Ported brick generation from `title_screen_3d.py:238-284`
- Running bond pattern with staggered rows
- Color variation and cracks
- Darkness parameter for lighting
- 5 new unit tests, all passing
- Visual samples generated

**Phase 3: Organic Effects** (Next)
- Port moss generation from `title_screen_3d.py:303-567`
- Port weathering from `title_screen_3d.py:285-301`

**Phase 4: Carved Text**
- Port carved letters from `title_screen_3d.py:592-651`

**Phase 5: Ursina Integration**
- Optimize for game performance
- Add caching if needed

## Quick Start

```python
from textures import get_brick_texture
from ursina import Entity, Ursina

# Create Ursina app
app = Ursina()

# Create a brick wall (Phase 2 - WORKING!)
wall = Entity(
    model='cube',
    texture=get_brick_texture(size=256, darkness=1.0),
    position=(0, 0, 5),
    scale=(2, 2, 0.1)
)

app.run()
```

**Generate PNG samples:**
```python
from textures.bricks import generate_brick_pattern

# Generate and save brick texture
brick = generate_brick_pattern(size=256, darkness=0.8)
brick.save('my_brick_texture.png')
```

## Architecture

### Module Structure

```
textures/
├── __init__.py          # Public API
├── generator.py         # Base classes and utilities ✅
├── bricks.py            # Brick patterns (Phase 2)
├── organic.py           # Moss generation (Phase 3)
├── weathering.py        # Age effects (Phase 3)
├── carved.py            # Carved text (Phase 4)
└── README.md            # This file
```

### Design Principles

1. **Separation of Concerns** - Texture generation is pure image processing
2. **Framework Independence** - Core uses PIL, thin Ursina adapter
3. **Modularity** - Each texture type in its own module
4. **Composability** - Effects can be layered (brick + moss + weathering)

## API Reference (Phase 1)

### Base Classes

#### `TextureGenerator`
Base class for all texture generators.

```python
class TextureGenerator:
    def __init__(self, size=256)
    def generate(self) -> Image.Image  # Override this
    def to_ursina_texture(self)
```

**Example:**
```python
class RedGenerator(TextureGenerator):
    def generate(self):
        self.draw.rectangle([0, 0, self.size, self.size], fill=(255, 0, 0, 255))
        return self.image

gen = RedGenerator(256)
texture = gen.to_ursina_texture()
```

#### `RandomSeed`
Context manager for reproducible generation.

```python
with RandomSeed(12345):
    texture = generate_brick_pattern()  # Always identical with same seed
```

### Utility Functions

#### `blend_images(base, overlay, mode='multiply', alpha=1.0)`
Blend two images using various modes.

**Modes:** `'multiply'`, `'add'`, `'screen'`, `'overlay'`, `'alpha'`

```python
brick = generate_brick_pattern()
moss = generate_moss_overlay(brick)
result = blend_images(brick, moss, mode='multiply', alpha=0.8)
```

#### `add_noise(image, intensity=0.1, noise_type='uniform')`
Add random noise for organic texture.

```python
texture = generate_brick_pattern()
noisy = add_noise(texture, intensity=0.15, noise_type='gaussian')
```

#### `darken_image(image, factor=0.7)`
Multiply brightness.

```python
dark_brick = darken_image(brick, factor=0.6)
```

#### `adjust_saturation(image, factor=1.5)`
Adjust color vibrance.

```python
vibrant_moss = adjust_saturation(moss, factor=1.3)
```

## API Status

### ✅ Implemented (Phase 2)

```python
from textures import get_brick_texture

# Brick patterns - WORKING!
texture = get_brick_texture(size=256, darkness=1.0)
```

### ⏳ Coming Soon (Phases 3-4)

These functions are **defined but not yet implemented** (raise `NotImplementedError`):

```python
# Phase 3: Organic Effects
texture = get_moss_stone_texture(size=256, moss_density='heavy')
texture = get_weathered_texture(size=256, intensity=1.0)

# Phase 4: Carved Text
texture = get_carved_texture('A', size=256, bg='moss_stone')
```

## Testing

Run tests with:
```bash
cd /var/www/claudelike/roguelike
python -m pytest tests/test_textures.py -v
# or
python tests/test_textures.py
```

**Test Results:** 33 tests, all passing ✓
- Phase 1 (Infrastructure): 24 tests
- Phase 2 (Brick Patterns): 5 tests
- General imports: 4 tests

**Generate visual samples:**
```bash
python examples/brick_demo.py
# Outputs to: output/brick_samples/
```

## QPainter to PIL Conversion Guide

| QPainter | PIL Equivalent |
|----------|----------------|
| `QImage(w, h, Format_RGBA8888)` | `Image.new('RGBA', (w, h))` |
| `QPainter(image)` | `ImageDraw.Draw(image)` |
| `painter.fillRect(x, y, w, h, color)` | `draw.rectangle([x, y, x+w, y+h], fill=color)` |
| `painter.drawLine(x1, y1, x2, y2)` | `draw.line([x1, y1, x2, y2])` |
| `painter.drawEllipse(x, y, w, h)` | `draw.ellipse([x, y, x+w, y+h])` |
| `painter.drawPolygon(QPolygonF(...))` | `draw.polygon([(x1,y1), (x2,y2), ...])` |
| `QColor(r, g, b, a)` | `(r, g, b, a)` tuple |
| `painter.setCompositionMode(Multiply)` | `blend_images(img1, img2, mode='multiply')` |

## Development Workflow

1. **Study reference code** in `ui/screens/title_screen_3d.py`
2. **Port algorithms** to PIL using conversion guide above
3. **Write tests** to verify correctness
4. **Visual comparison** - compare output to OpenGL version
5. **Optimize** if needed

## Dependencies

```
Pillow>=10.0.0  # PIL fork, image processing
numpy>=1.24.0   # Already in requirements, used for noise
ursina>=6.0.0   # Already in requirements, 3D engine
```

## Performance Notes

- **Generation time:** Target < 50ms for 256x256 texture
- **Caching:** Will be added in Phase 5 if needed
- **Memory:** PIL images are efficient, ~256KB per 256x256 RGBA

## Contributing

When implementing new phases:

1. Follow the HANDOVER.md specifications
2. Port from reference implementation in `title_screen_3d.py`
3. Add comprehensive tests
4. Update this README with new API
5. Keep phase separation clean

## Questions?

See `HANDOVER.md` for complete implementation guide, or check the reference implementation in `ui/screens/title_screen_3d.py`.

---

**Version:** 0.2.0-phase2
**Last Updated:** 2025-10-12
**Next Phase:** Organic effects (moss and weathering) - Phase 3
