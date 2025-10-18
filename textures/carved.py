"""
Carved Text/Symbols (Phase 4)

This module will generate carved letter/symbol textures with:
- 3-layer depth effect (shadow, highlight, main)
- Font loading and rendering
- Multiple background options (brick, moss stone, plain)
- Illusion of carved depth

Reference: ui/screens/title_screen_3d.py:592-651 (_generate_letter_textures)

Status: NOT YET IMPLEMENTED
"""

from PIL import Image


def generate_carved_texture(char: str, size: int = 256, bg: str = 'moss_stone') -> Image.Image:
    """Generate texture with carved character.

    Creates a 3D carved effect by layering:
    1. Shadow layer (offset down+right for depth)
    2. Highlight layer (offset up+left for edge lighting)
    3. Main layer (carved surface)

    Args:
        char: Single character to carve
        size: Texture size (power of 2 recommended)
        bg: Background type - 'moss_stone', 'brick', or 'plain'

    Returns:
        PIL Image with carved character
    """
    raise NotImplementedError("Phase 4: To be ported from title_screen_3d.py:592-651")


def find_system_font() -> str:
    """Find a suitable bold font across platforms.

    Checks common font paths on Linux, Windows, and macOS.

    Returns:
        Path to font file

    Raises:
        FileNotFoundError: If no suitable font found
    """
    raise NotImplementedError("Phase 4: Font path detection")
