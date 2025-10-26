"""
Centralized shader management for 3D models.

Provides singleton ShaderManager to eliminate duplicate shader initialization
across item and enemy model files.
"""

import sys
from pathlib import Path


class ShaderManager:
    """
    Singleton for shader creation and caching.

    Manages toon shader instances and provides LOD (Level of Detail) selection
    based on model scale to optimize performance.
    """
    _instance = None

    def __init__(self):
        """Initialize shader instances."""
        # Setup imports (needed for dna_editor shaders)
        self._setup_imports()

        # Import shader functions
        from dna_editor.shaders import create_toon_shader, create_toon_shader_lite, get_shader_for_scale

        # Create shader instances
        self.toon_shader = create_toon_shader()
        self.toon_shader_lite = create_toon_shader_lite()
        self._get_shader_for_scale = get_shader_for_scale

    def _setup_imports(self):
        """Setup project root and dna_editor paths for imports."""
        # Add project root to path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # Add dna_editor to path
        dna_editor_path = str(Path(__file__).parent.parent / 'dna_editor')
        if dna_editor_path not in sys.path:
            sys.path.append(dna_editor_path)

    def get_shader_for_scale(self, scale):
        """
        Get appropriate shader based on model scale.

        Uses LOD (Level of Detail) to select between full toon shader
        and lite toon shader based on the scale threshold.

        Args:
            scale: Model scale value (float, tuple, or Vec3)

        Returns:
            Shader instance appropriate for the given scale, or None if shaders unavailable
        """
        if self.toon_shader and self.toon_shader_lite:
            return self._get_shader_for_scale(scale, self.toon_shader, self.toon_shader_lite)
        return None

    @classmethod
    def get_instance(cls):
        """
        Get or create the singleton ShaderManager instance.

        Returns:
            ShaderManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None


# Convenience function for quick access
def get_shader_manager():
    """
    Get the global ShaderManager instance.

    Returns:
        ShaderManager: The singleton shader manager
    """
    return ShaderManager.get_instance()
