"""
Unit tests for procedural texture generation system.

Tests:
- Phase 1: Infrastructure (base classes, utilities)
- Phase 2: Brick patterns
- Phase 3: Organic effects (moss and weathering)
"""
import unittest
import random
from PIL import Image
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from textures import (
    TextureGenerator,
    RandomSeed,
    blend_images,
    add_noise,
    darken_image,
    adjust_saturation,
    get_brick_texture,
    get_moss_stone_texture,
    get_carved_texture,
    get_weathered_texture
)


class TestTextureGenerator(unittest.TestCase):
    """Test TextureGenerator base class."""

    def test_instantiation(self):
        """Test that TextureGenerator can be instantiated."""
        gen = TextureGenerator(size=256)
        self.assertEqual(gen.size, 256)
        self.assertIsNotNone(gen.image)
        self.assertIsNotNone(gen.draw)

    def test_default_size(self):
        """Test default size is 256."""
        gen = TextureGenerator()
        self.assertEqual(gen.size, 256)

    def test_custom_size(self):
        """Test custom size is respected."""
        gen = TextureGenerator(size=512)
        self.assertEqual(gen.size, 512)
        self.assertEqual(gen.image.size, (512, 512))

    def test_image_format(self):
        """Test image is RGBA format."""
        gen = TextureGenerator()
        self.assertEqual(gen.image.mode, 'RGBA')

    def test_generate_not_implemented(self):
        """Test that generate() raises NotImplementedError."""
        gen = TextureGenerator()
        with self.assertRaises(NotImplementedError):
            gen.generate()

    def test_subclass_can_override(self):
        """Test that subclasses can override generate()."""
        class RedGenerator(TextureGenerator):
            def generate(self):
                self.draw.rectangle([0, 0, self.size, self.size], fill=(255, 0, 0, 255))
                return self.image

        gen = RedGenerator(64)
        img = gen.generate()
        self.assertIsInstance(img, Image.Image)
        # Check that image has red pixels
        pixels = list(img.getdata())
        self.assertTrue(any(p[0] > 200 for p in pixels))  # Has red channel


class TestRandomSeed(unittest.TestCase):
    """Test RandomSeed context manager."""

    def test_deterministic_generation(self):
        """Test that same seed produces identical random numbers."""
        nums1 = []
        with RandomSeed(12345):
            nums1 = [random.randint(0, 1000) for _ in range(10)]

        nums2 = []
        with RandomSeed(12345):
            nums2 = [random.randint(0, 1000) for _ in range(10)]

        self.assertEqual(nums1, nums2)

    def test_different_seeds_differ(self):
        """Test that different seeds produce different results."""
        nums1 = []
        with RandomSeed(111):
            nums1 = [random.randint(0, 1000) for _ in range(10)]

        nums2 = []
        with RandomSeed(222):
            nums2 = [random.randint(0, 1000) for _ in range(10)]

        self.assertNotEqual(nums1, nums2)

    def test_state_restoration(self):
        """Test that random state is restored after context."""
        # Get some random numbers before
        before = [random.random() for _ in range(3)]

        # Use RandomSeed context
        with RandomSeed(99999):
            _ = [random.random() for _ in range(10)]

        # Check that we're not in the seeded state anymore
        after = [random.random() for _ in range(3)]
        # If state wasn't restored, these would be deterministic
        # We can't predict exact values, but they shouldn't match the seeded sequence
        with RandomSeed(99999):
            seeded = [random.random() for _ in range(3)]
        self.assertNotEqual(after, seeded)


class TestBlendImages(unittest.TestCase):
    """Test blend_images utility."""

    def setUp(self):
        """Create test images."""
        # Create a red image
        self.red = Image.new('RGBA', (64, 64), (255, 0, 0, 255))
        # Create a blue image
        self.blue = Image.new('RGBA', (64, 64), (0, 0, 255, 255))

    def test_blend_multiply(self):
        """Test multiply blend mode."""
        result = blend_images(self.red, self.blue, mode='multiply')
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (64, 64))

    def test_blend_add(self):
        """Test additive blend mode."""
        result = blend_images(self.red, self.blue, mode='add')
        self.assertIsInstance(result, Image.Image)

    def test_blend_alpha(self):
        """Test alpha blend mode."""
        result = blend_images(self.red, self.blue, mode='alpha', alpha=0.5)
        self.assertIsInstance(result, Image.Image)

    def test_blend_size_mismatch(self):
        """Test that blending handles size mismatches."""
        small = Image.new('RGBA', (32, 32), (0, 255, 0, 255))
        result = blend_images(self.red, small, mode='multiply')
        self.assertEqual(result.size, self.red.size)

    def test_invalid_mode(self):
        """Test that invalid blend mode raises ValueError."""
        with self.assertRaises(ValueError):
            blend_images(self.red, self.blue, mode='invalid_mode')


class TestAddNoise(unittest.TestCase):
    """Test add_noise utility."""

    def setUp(self):
        """Create test image."""
        self.image = Image.new('RGBA', (64, 64), (128, 128, 128, 255))

    def test_add_noise_uniform(self):
        """Test uniform noise addition."""
        noisy = add_noise(self.image, intensity=0.1, noise_type='uniform')
        self.assertIsInstance(noisy, Image.Image)
        self.assertEqual(noisy.size, self.image.size)

    def test_add_noise_gaussian(self):
        """Test gaussian noise addition."""
        noisy = add_noise(self.image, intensity=0.1, noise_type='gaussian')
        self.assertIsInstance(noisy, Image.Image)

    def test_noise_changes_pixels(self):
        """Test that noise actually modifies the image."""
        import numpy as np
        original = np.array(self.image)
        noisy = add_noise(self.image, intensity=0.2)
        noisy_array = np.array(noisy)

        # Images should differ
        self.assertFalse(np.array_equal(original, noisy_array))

    def test_invalid_noise_type(self):
        """Test that invalid noise type raises ValueError."""
        with self.assertRaises(ValueError):
            add_noise(self.image, noise_type='invalid_type')


class TestImageAdjustments(unittest.TestCase):
    """Test darken_image and adjust_saturation utilities."""

    def setUp(self):
        """Create test image."""
        self.image = Image.new('RGBA', (64, 64), (200, 150, 100, 255))

    def test_darken_image(self):
        """Test image darkening."""
        dark = darken_image(self.image, factor=0.5)
        self.assertIsInstance(dark, Image.Image)

        # Check that image is actually darker
        import numpy as np
        original_brightness = np.mean(np.array(self.image)[:, :, :3])
        dark_brightness = np.mean(np.array(dark)[:, :, :3])
        self.assertLess(dark_brightness, original_brightness)

    def test_darken_factor_zero(self):
        """Test that factor=0 creates black image."""
        black = darken_image(self.image, factor=0.0)
        import numpy as np
        # RGB channels should be very dark
        rgb_mean = np.mean(np.array(black)[:, :, :3])
        self.assertLess(rgb_mean, 10)  # Nearly black

    def test_adjust_saturation(self):
        """Test saturation adjustment."""
        vibrant = adjust_saturation(self.image, factor=1.5)
        self.assertIsInstance(vibrant, Image.Image)

    def test_desaturate(self):
        """Test that factor=0 creates grayscale."""
        gray = adjust_saturation(self.image, factor=0.0)
        # Check that R, G, B values are similar (grayscale)
        pixels = list(gray.getdata())
        # For grayscale, R ≈ G ≈ B
        sample = pixels[0]
        self.assertTrue(abs(sample[0] - sample[1]) < 5)
        self.assertTrue(abs(sample[1] - sample[2]) < 5)


class TestBrickGeneration(unittest.TestCase):
    """Test brick pattern generation (Phase 2)."""

    def test_generate_brick_pattern(self):
        """Test that brick pattern can be generated."""
        from textures.bricks import generate_brick_pattern

        brick = generate_brick_pattern(size=256)
        self.assertIsInstance(brick, Image.Image)
        self.assertEqual(brick.size, (256, 256))
        self.assertEqual(brick.mode, 'RGBA')

    def test_brick_custom_size(self):
        """Test brick generation with custom size."""
        from textures.bricks import generate_brick_pattern

        brick = generate_brick_pattern(size=128)
        self.assertEqual(brick.size, (128, 128))

    def test_brick_darkness(self):
        """Test darkness parameter."""
        from textures.bricks import generate_brick_pattern
        import numpy as np

        brick_normal = generate_brick_pattern(size=64, darkness=1.0)
        brick_dark = generate_brick_pattern(size=64, darkness=0.5)

        # Measure average brightness
        avg_normal = np.mean(np.array(brick_normal)[:, :, :3])
        avg_dark = np.mean(np.array(brick_dark)[:, :, :3])

        # Dark version should be darker
        self.assertLess(avg_dark, avg_normal)

    def test_brick_deterministic(self):
        """Test that same seed produces identical bricks."""
        from textures.bricks import generate_brick_pattern
        from textures import RandomSeed

        with RandomSeed(54321):
            brick1 = generate_brick_pattern(size=64)

        with RandomSeed(54321):
            brick2 = generate_brick_pattern(size=64)

        # Should be identical
        self.assertEqual(list(brick1.getdata()), list(brick2.getdata()))

    def test_brick_has_variation(self):
        """Test that bricks have color variation (not uniform)."""
        from textures.bricks import generate_brick_pattern
        import numpy as np

        brick = generate_brick_pattern(size=128)
        pixels = np.array(brick)[:, :, :3]  # RGB only

        # Check that there's variation (std dev > 0)
        std_dev = np.std(pixels)
        self.assertGreater(std_dev, 5)  # Should have noticeable variation


class TestWeatheringEffects(unittest.TestCase):
    """Test weathering effects (Phase 3)."""

    def setUp(self):
        """Create base test image."""
        self.image = Image.new('RGBA', (128, 128), (100, 95, 90, 255))

    def test_add_weathering(self):
        """Test basic weathering application."""
        from textures.weathering import add_weathering

        weathered = add_weathering(self.image, intensity=1.0)
        self.assertIsInstance(weathered, Image.Image)
        self.assertEqual(weathered.size, self.image.size)
        self.assertEqual(weathered.mode, 'RGBA')

    def test_weathering_darkens_image(self):
        """Test that weathering darkens the image."""
        from textures.weathering import add_weathering
        import numpy as np

        weathered = add_weathering(self.image, intensity=1.0)

        # Measure brightness
        original_brightness = np.mean(np.array(self.image)[:, :, :3])
        weathered_brightness = np.mean(np.array(weathered)[:, :, :3])

        # Weathering should darken
        self.assertLess(weathered_brightness, original_brightness)

    def test_weathering_intensity_zero(self):
        """Test that intensity=0 returns unchanged image."""
        from textures.weathering import add_weathering

        weathered = add_weathering(self.image, intensity=0.0)

        # Should be identical
        self.assertEqual(list(self.image.getdata()), list(weathered.getdata()))

    def test_weathering_intensity_scaling(self):
        """Test that higher intensity creates more weathering."""
        from textures.weathering import add_weathering
        import numpy as np

        light = add_weathering(self.image.copy(), intensity=0.3)
        heavy = add_weathering(self.image.copy(), intensity=2.0)

        light_brightness = np.mean(np.array(light)[:, :, :3])
        heavy_brightness = np.mean(np.array(heavy)[:, :, :3])

        # Heavy weathering should be darker than light
        self.assertLess(heavy_brightness, light_brightness)

    def test_add_stains(self):
        """Test stain addition."""
        from textures.weathering import add_stains

        stained = add_stains(self.image, num_stains=10)
        self.assertIsInstance(stained, Image.Image)
        self.assertEqual(stained.size, self.image.size)

    def test_add_age_marks(self):
        """Test age mark addition."""
        from textures.weathering import add_age_marks

        aged = add_age_marks(self.image, num_marks=5)
        self.assertIsInstance(aged, Image.Image)


class TestMossGeneration(unittest.TestCase):
    """Test organic moss generation (Phase 3)."""

    def setUp(self):
        """Create base brick texture."""
        from textures.bricks import generate_brick_pattern
        self.brick = generate_brick_pattern(size=128)

    def test_generate_moss_overlay(self):
        """Test basic moss overlay generation."""
        from textures.organic import generate_moss_overlay

        mossy = generate_moss_overlay(self.brick, density='heavy')
        self.assertIsInstance(mossy, Image.Image)
        self.assertEqual(mossy.size, self.brick.size)
        self.assertEqual(mossy.mode, 'RGBA')

    def test_moss_density_light(self):
        """Test light moss density."""
        from textures.organic import generate_moss_overlay

        mossy = generate_moss_overlay(self.brick, density='light')
        self.assertIsInstance(mossy, Image.Image)

    def test_moss_density_medium(self):
        """Test medium moss density."""
        from textures.organic import generate_moss_overlay

        mossy = generate_moss_overlay(self.brick, density='medium')
        self.assertIsInstance(mossy, Image.Image)

    def test_moss_density_heavy(self):
        """Test heavy moss density."""
        from textures.organic import generate_moss_overlay

        mossy = generate_moss_overlay(self.brick, density='heavy')
        self.assertIsInstance(mossy, Image.Image)

    def test_moss_adds_green_tones(self):
        """Test that moss overlay adds green color."""
        from textures.organic import generate_moss_overlay
        import numpy as np

        mossy = generate_moss_overlay(self.brick, density='heavy')

        # Sample some pixels and check for green channel presence
        pixels = np.array(mossy)
        green_channel = pixels[:, :, 1]  # G channel

        # Should have significant green values
        self.assertGreater(np.max(green_channel), 50)

    def test_moss_deterministic(self):
        """Test that moss generation with same seed is deterministic."""
        from textures.organic import generate_moss_overlay
        from textures import RandomSeed

        with RandomSeed(77777):
            mossy1 = generate_moss_overlay(self.brick.copy(), density='medium')

        with RandomSeed(77777):
            mossy2 = generate_moss_overlay(self.brick.copy(), density='medium')

        # Should be very similar (allowing for minor floating point differences)
        import numpy as np
        diff = np.mean(np.abs(np.array(mossy1).astype(int) - np.array(mossy2).astype(int)))
        self.assertLess(diff, 1.0)  # Nearly identical


class TestMossStoneTexture(unittest.TestCase):
    """Test complete moss-covered stone texture (Phase 3)."""

    def test_generate_moss_stone_texture(self):
        """Test complete moss stone generation."""
        from textures.organic import generate_moss_stone_texture

        texture = generate_moss_stone_texture(size=128, moss_density='heavy')
        self.assertIsInstance(texture, Image.Image)
        self.assertEqual(texture.size, (128, 128))
        self.assertEqual(texture.mode, 'RGBA')

    def test_moss_stone_custom_size(self):
        """Test custom size generation."""
        from textures.organic import generate_moss_stone_texture

        texture = generate_moss_stone_texture(size=256, moss_density='medium')
        self.assertEqual(texture.size, (256, 256))

    def test_moss_stone_with_darkness(self):
        """Test base darkness parameter."""
        from textures.organic import generate_moss_stone_texture
        import numpy as np

        normal = generate_moss_stone_texture(size=64, moss_density='light', base_darkness=1.0)
        dark = generate_moss_stone_texture(size=64, moss_density='light', base_darkness=0.5)

        # Dark version should be darker overall
        avg_normal = np.mean(np.array(normal)[:, :, :3])
        avg_dark = np.mean(np.array(dark)[:, :, :3])

        self.assertLess(avg_dark, avg_normal)

    def test_moss_stone_has_layers(self):
        """Test that texture has both brick base and moss overlay."""
        from textures.organic import generate_moss_stone_texture
        import numpy as np

        texture = generate_moss_stone_texture(size=128, moss_density='heavy')
        pixels = np.array(texture)

        # Should have variation in color (multiple layers)
        std_dev = np.std(pixels[:, :, :3])
        self.assertGreater(std_dev, 10)


class TestPublicAPI(unittest.TestCase):
    """Test public API functions."""

    def test_get_carved_texture_not_implemented(self):
        """Test that get_carved_texture raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            get_carved_texture('A')


class TestImports(unittest.TestCase):
    """Test that all imports work correctly."""

    def test_can_import_from_textures(self):
        """Test that we can import from textures package."""
        from textures import TextureGenerator, RandomSeed
        self.assertTrue(callable(TextureGenerator))
        self.assertTrue(callable(RandomSeed))

    def test_can_import_utilities(self):
        """Test that utility functions can be imported."""
        from textures import blend_images, add_noise, darken_image
        self.assertTrue(callable(blend_images))
        self.assertTrue(callable(add_noise))
        self.assertTrue(callable(darken_image))

    def test_can_import_api_functions(self):
        """Test that API functions can be imported."""
        from textures import (
            get_brick_texture,
            get_moss_stone_texture,
            get_carved_texture,
            get_weathered_texture
        )
        self.assertTrue(callable(get_brick_texture))
        self.assertTrue(callable(get_moss_stone_texture))
        self.assertTrue(callable(get_carved_texture))
        self.assertTrue(callable(get_weathered_texture))


if __name__ == '__main__':
    unittest.main()
