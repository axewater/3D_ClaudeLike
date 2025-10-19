"""
Procedural Materials Library for 3D Models

Provides pre-configured procedural textures and material properties
for character models, weapons, and armor.

Uses the existing textures module to generate:
- Metal textures (polished steel, battle-worn, bronze, iron)
- Leather textures (brown, black, worn)
- Cloth textures (various colors with fabric weave)
- Skin tones
- Wood textures

Each material includes:
- Texture (PIL Image -> Ursina Texture)
- Shader hints
- Material properties (metallic, roughness, specular)
"""

from typing import Dict, Any, Optional, Tuple
from ursina import Texture, color as ursina_color
from PIL import Image, ImageDraw, ImageFilter
import random


class Material:
    """Container for material properties"""

    def __init__(self, texture: Optional[Texture] = None,
                 color: Optional[Tuple[int, int, int]] = None,
                 shader: str = 'matcap',
                 metallic: float = 0.0,
                 roughness: float = 0.5,
                 specular: float = 0.0,
                 emissive: bool = False):
        """
        Create a material with texture and properties.

        Args:
            texture: Ursina Texture object (procedurally generated)
            color: Fallback RGB color if no texture
            shader: Shader to use ('matcap', 'lit_with_shadows', 'unlit')
            metallic: How metallic (0=dielectric, 1=metal)
            roughness: Surface roughness (0=mirror, 1=matte)
            specular: Specular highlight intensity (0-1)
            emissive: Whether to emit light (for glowing effects)
        """
        self.texture = texture
        self.color = color
        self.shader = shader
        self.metallic = metallic
        self.roughness = roughness
        self.specular = specular
        self.emissive = emissive

    def get_ursina_color(self):
        """Convert RGB color to Ursina color"""
        if self.color:
            return ursina_color.rgb(self.color[0]/255, self.color[1]/255, self.color[2]/255)
        return ursina_color.white

    def apply_to_entity(self, entity):
        """Apply this material's properties to an Ursina entity"""
        if self.texture:
            entity.texture = self.texture
        elif self.color:
            entity.color = self.get_ursina_color()

        # Apply shader if not default
        if self.shader != 'default':
            entity.shader = self.shader

        # Apply material properties (Ursina may not support all, but we set them)
        if hasattr(entity, 'metallic'):
            entity.metallic = self.metallic
        if hasattr(entity, 'roughness'):
            entity.roughness = self.roughness
        if hasattr(entity, 'specular'):
            entity.specular = self.specular
        if self.emissive:
            entity.unlit = True


# ============================================================================
# METAL MATERIALS
# ============================================================================

def generate_metal_texture(base_color: Tuple[int, int, int],
                           size: int = 256,
                           scratches: int = 20,
                           worn: bool = False) -> Image.Image:
    """
    Generate procedural metal texture.

    Args:
        base_color: Base RGB color
        size: Texture size
        scratches: Number of scratch marks
        worn: Add wear and tear

    Returns:
        PIL Image with metal texture
    """
    # Start with base color
    img = Image.new('RGBA', (size, size), base_color + (255,))
    draw = ImageDraw.Draw(img)

    # Add subtle color variation (metallic sheen)
    for _ in range(50):
        x = random.randint(0, size)
        y = random.randint(0, size)
        radius = random.randint(5, 20)

        # Lighter or darker spot
        variation = random.randint(-10, 10)
        spot_color = tuple(max(0, min(255, c + variation)) for c in base_color) + (30,)

        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=spot_color)

    # Blur to blend
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    # Add scratches
    scratch_color = tuple(max(0, c - 40) for c in base_color) + (255,)
    for _ in range(scratches):
        x1 = random.randint(0, size)
        y1 = random.randint(0, size)
        length = random.randint(10, 40)
        angle = random.uniform(0, 360)

        import math
        x2 = x1 + int(length * math.cos(math.radians(angle)))
        y2 = y1 + int(length * math.sin(math.radians(angle)))

        draw.line([x1, y1, x2, y2], fill=scratch_color, width=1)

    # Add wear if requested
    if worn:
        from textures import add_noise, darken_image
        img = add_noise(img, intensity=0.1)
        img = darken_image(img, factor=0.9)

    return img


def create_polished_steel_material(size: int = 256) -> Material:
    """Polished steel - bright, reflective, minimal wear"""
    texture_img = generate_metal_texture((180, 180, 190), size=size, scratches=10, worn=False)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.9,
        roughness=0.2,
        specular=0.95
    )


def create_battle_worn_steel_material(size: int = 256) -> Material:
    """Battle-worn steel - scratched, dented, heavily used"""
    texture_img = generate_metal_texture((140, 140, 150), size=size, scratches=30, worn=True)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.85,
        roughness=0.4,
        specular=0.7
    )


def create_bronze_material(size: int = 256) -> Material:
    """Bronze - warm metallic, slightly oxidized"""
    texture_img = generate_metal_texture((120, 100, 60), size=size, scratches=15, worn=False)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.8,
        roughness=0.3,
        specular=0.8
    )


def create_iron_material(size: int = 256) -> Material:
    """Dark iron - rough, matte finish"""
    texture_img = generate_metal_texture((70, 70, 75), size=size, scratches=25, worn=True)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.7,
        roughness=0.6,
        specular=0.5
    )


# ============================================================================
# LEATHER MATERIALS
# ============================================================================

def generate_leather_texture(base_color: Tuple[int, int, int],
                             size: int = 256,
                             grain: int = 50) -> Image.Image:
    """
    Generate procedural leather texture.

    Args:
        base_color: Base RGB color
        size: Texture size
        grain: Amount of leather grain detail

    Returns:
        PIL Image with leather texture
    """
    img = Image.new('RGBA', (size, size), base_color + (255,))
    draw = ImageDraw.Draw(img)

    # Add leather grain (small random lines)
    grain_color = tuple(max(0, c - 15) for c in base_color) + (255,)
    for _ in range(grain):
        x = random.randint(0, size)
        y = random.randint(0, size)
        length = random.randint(3, 8)
        angle = random.uniform(0, 360)

        import math
        x2 = x + int(length * math.cos(math.radians(angle)))
        y2 = y + int(length * math.sin(math.radians(angle)))

        draw.line([x, y, x2, y2], fill=grain_color, width=1)

    # Add wear marks
    for _ in range(20):
        x = random.randint(0, size)
        y = random.randint(0, size)
        radius = random.randint(2, 8)

        wear_color = tuple(max(0, c - 25) for c in base_color) + (50,)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=wear_color)

    # Blur slightly for smooth leather look
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    return img


def create_brown_leather_material(size: int = 256) -> Material:
    """Brown leather - typical for belts, straps, pouches"""
    texture_img = generate_leather_texture((100, 70, 40), size=size, grain=50)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.7,
        specular=0.2
    )


def create_black_leather_material(size: int = 256) -> Material:
    """Black leather - for rogue armor, dark clothing"""
    texture_img = generate_leather_texture((50, 45, 45), size=size, grain=60)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.75,
        specular=0.15
    )


def create_worn_leather_material(size: int = 256) -> Material:
    """Worn/aged leather - cracked and faded"""
    texture_img = generate_leather_texture((80, 65, 50), size=size, grain=80)
    # Add extra wear
    from textures import add_noise
    texture_img = add_noise(texture_img, intensity=0.15)

    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.85,
        specular=0.1
    )


# ============================================================================
# CLOTH MATERIALS
# ============================================================================

def generate_cloth_texture(base_color: Tuple[int, int, int],
                           size: int = 256,
                           weave: int = 100) -> Image.Image:
    """
    Generate procedural cloth/fabric texture.

    Args:
        base_color: Base RGB color
        size: Texture size
        weave: Density of fabric weave pattern

    Returns:
        PIL Image with cloth texture
    """
    img = Image.new('RGBA', (size, size), base_color + (255,))
    draw = ImageDraw.Draw(img)

    # Create fabric weave pattern (cross-hatch)
    weave_color = tuple(max(0, c - 8) for c in base_color) + (255,)

    # Horizontal threads
    for i in range(0, size, size // weave):
        y = i + random.randint(-1, 1)
        draw.line([0, y, size, y], fill=weave_color, width=1)

    # Vertical threads
    for i in range(0, size, size // weave):
        x = i + random.randint(-1, 1)
        draw.line([x, 0, x, size], fill=weave_color, width=1)

    # Add fabric folds/wrinkles
    for _ in range(10):
        x = random.randint(0, size)
        y = random.randint(0, size)
        width = random.randint(10, 30)
        height = random.randint(3, 8)

        shadow_color = tuple(max(0, c - 20) for c in base_color) + (40,)
        draw.ellipse([x, y, x+width, y+height], fill=shadow_color)

    # Subtle blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    return img


def create_red_cloth_material(size: int = 256) -> Material:
    """Red cloth - warrior tunic"""
    texture_img = generate_cloth_texture((180, 60, 40), size=size, weave=30)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.9,
        specular=0.05
    )


def create_blue_cloth_material(size: int = 256) -> Material:
    """Blue cloth - mage robes"""
    texture_img = generate_cloth_texture((100, 150, 255), size=size, weave=35)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.9,
        specular=0.05
    )


def create_green_cloth_material(size: int = 256) -> Material:
    """Green cloth - ranger cloak"""
    texture_img = generate_cloth_texture((100, 200, 100), size=size, weave=32)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.9,
        specular=0.05
    )


def create_dark_cloth_material(size: int = 256) -> Material:
    """Dark cloth - rogue clothing"""
    texture_img = generate_cloth_texture((60, 60, 65), size=size, weave=40)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.95,
        specular=0.02
    )


# ============================================================================
# WOOD MATERIALS
# ============================================================================

def generate_wood_texture(base_color: Tuple[int, int, int],
                         size: int = 256,
                         grain_lines: int = 30) -> Image.Image:
    """
    Generate procedural wood texture.

    Args:
        base_color: Base wood RGB color
        size: Texture size
        grain_lines: Number of wood grain lines

    Returns:
        PIL Image with wood grain texture
    """
    img = Image.new('RGBA', (size, size), base_color + (255,))
    draw = ImageDraw.Draw(img)

    # Wood grain (wavy horizontal lines)
    grain_color = tuple(max(0, c - 20) for c in base_color) + (255,)

    for i in range(grain_lines):
        y = (size // grain_lines) * i + random.randint(-3, 3)
        points = []

        for x in range(0, size, 5):
            import math
            wave_offset = int(math.sin(x * 0.1 + i) * 2)
            points.append((x, y + wave_offset))

        if len(points) > 1:
            draw.line(points, fill=grain_color, width=1)

    # Add knots
    for _ in range(3):
        x = random.randint(size//4, 3*size//4)
        y = random.randint(size//4, 3*size//4)
        radius = random.randint(5, 12)

        knot_color = tuple(max(0, c - 40) for c in base_color) + (255,)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline=knot_color, width=2)

    return img


def create_wood_material(size: int = 256) -> Material:
    """Brown wood - for staffs, bows, sword hilts"""
    texture_img = generate_wood_texture((120, 80, 40), size=size, grain_lines=40)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.8,
        specular=0.1
    )


def create_dark_wood_material(size: int = 256) -> Material:
    """Dark wood - aged or stained"""
    texture_img = generate_wood_texture((60, 45, 25), size=size, grain_lines=35)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.85,
        specular=0.08
    )


# ============================================================================
# SKIN MATERIALS
# ============================================================================

def create_skin_material(size: int = 256) -> Material:
    """Skin tone - for hands, face"""
    # Simple solid color for now (could add pores, freckles later)
    base_color = (200, 160, 130)
    img = Image.new('RGBA', (size, size), base_color + (255,))

    return Material(
        texture=Texture(img),
        shader='lit_with_shadows',
        metallic=0.0,
        roughness=0.6,
        specular=0.3  # Slight sheen for skin
    )


# ============================================================================
# SPECIAL MATERIALS
# ============================================================================

def create_glowing_material(glow_color: Tuple[int, int, int],
                           size: int = 256) -> Material:
    """Glowing/emissive material - for magic effects, eyes"""
    img = Image.new('RGBA', (size, size), glow_color + (255,))

    return Material(
        texture=Texture(img),
        shader='unlit',  # Don't apply lighting
        metallic=0.0,
        roughness=0.0,
        specular=0.0,
        emissive=True
    )


def create_gold_material(size: int = 256) -> Material:
    """Gold - for decorations, shield boss"""
    texture_img = generate_metal_texture((180, 160, 50), size=size, scratches=5, worn=False)
    return Material(
        texture=Texture(texture_img),
        shader='lit_with_shadows',
        metallic=0.95,
        roughness=0.15,
        specular=0.98
    )


# ============================================================================
# MATERIAL CACHE (for performance)
# ============================================================================

_material_cache: Dict[str, Material] = {}

def get_material(material_name: str, size: int = 256) -> Material:
    """
    Get a cached material by name.

    Args:
        material_name: Name of material (e.g., 'polished_steel', 'brown_leather')
        size: Texture size (default 256)

    Returns:
        Material object

    Available materials:
        Metals: 'polished_steel', 'battle_worn_steel', 'bronze', 'iron', 'gold'
        Leather: 'brown_leather', 'black_leather', 'worn_leather'
        Cloth: 'red_cloth', 'blue_cloth', 'green_cloth', 'dark_cloth'
        Wood: 'wood', 'dark_wood'
        Other: 'skin', 'glowing_red', 'glowing_blue', 'glowing_purple'
    """
    cache_key = f"{material_name}_{size}"

    if cache_key not in _material_cache:
        # Generate material based on name
        if material_name == 'polished_steel':
            _material_cache[cache_key] = create_polished_steel_material(size)
        elif material_name == 'battle_worn_steel':
            _material_cache[cache_key] = create_battle_worn_steel_material(size)
        elif material_name == 'bronze':
            _material_cache[cache_key] = create_bronze_material(size)
        elif material_name == 'iron':
            _material_cache[cache_key] = create_iron_material(size)
        elif material_name == 'gold':
            _material_cache[cache_key] = create_gold_material(size)

        elif material_name == 'brown_leather':
            _material_cache[cache_key] = create_brown_leather_material(size)
        elif material_name == 'black_leather':
            _material_cache[cache_key] = create_black_leather_material(size)
        elif material_name == 'worn_leather':
            _material_cache[cache_key] = create_worn_leather_material(size)

        elif material_name == 'red_cloth':
            _material_cache[cache_key] = create_red_cloth_material(size)
        elif material_name == 'blue_cloth':
            _material_cache[cache_key] = create_blue_cloth_material(size)
        elif material_name == 'green_cloth':
            _material_cache[cache_key] = create_green_cloth_material(size)
        elif material_name == 'dark_cloth':
            _material_cache[cache_key] = create_dark_cloth_material(size)

        elif material_name == 'wood':
            _material_cache[cache_key] = create_wood_material(size)
        elif material_name == 'dark_wood':
            _material_cache[cache_key] = create_dark_wood_material(size)

        elif material_name == 'skin':
            _material_cache[cache_key] = create_skin_material(size)

        elif material_name == 'glowing_red':
            _material_cache[cache_key] = create_glowing_material((255, 0, 0), size)
        elif material_name == 'glowing_blue':
            _material_cache[cache_key] = create_glowing_material((100, 150, 255), size)
        elif material_name == 'glowing_purple':
            _material_cache[cache_key] = create_glowing_material((150, 100, 255), size)

        else:
            raise ValueError(f"Unknown material: {material_name}")

    return _material_cache[cache_key]


__all__ = [
    'Material',
    'get_material',
    # Metal
    'create_polished_steel_material',
    'create_battle_worn_steel_material',
    'create_bronze_material',
    'create_iron_material',
    'create_gold_material',
    # Leather
    'create_brown_leather_material',
    'create_black_leather_material',
    'create_worn_leather_material',
    # Cloth
    'create_red_cloth_material',
    'create_blue_cloth_material',
    'create_green_cloth_material',
    'create_dark_cloth_material',
    # Wood
    'create_wood_material',
    'create_dark_wood_material',
    # Other
    'create_skin_material',
    'create_glowing_material',
]
