"""
Base class for all 3D menu screens.

Provides common initialization, show/hide logic, and cleanup to eliminate
code duplication across menu screen classes.
"""

from ursina import Entity, destroy
from audio import get_audio_manager


class BaseScreen3D(Entity):
    """
    Abstract base class for all 3D menu screens.

    Provides common initialization, show/hide logic, and cleanup.
    Subclasses only need to implement _create_ui() to define their specific UI elements.

    Attributes:
        screen_manager: Reference to the screen manager that controls this screen
        audio: AudioManager instance for playing sounds
        ui_elements: List of UI entities that should be shown/hidden with the screen
        particles: List of particle effects that should be cleaned up
        enabled: Whether the screen is currently visible
    """

    def __init__(self, screen_manager):
        """
        Initialize the base screen.

        Args:
            screen_manager: Screen manager instance that controls navigation
        """
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()
        self.ui_elements = []
        self.particles = []
        self.enabled = False

        # Let subclass create UI
        self._create_ui()

    def _create_ui(self):
        """
        Create UI elements for this screen.

        Subclasses should override this method to create their UI.
        Add created elements to self.ui_elements list so they can be
        automatically shown/hidden/cleaned up.

        Note: This is not truly abstract (no @abstractmethod) to avoid
        metaclass conflicts with Ursina's Entity class.
        """
        pass

    def show(self):
        """
        Show this screen and all UI elements.

        Override this method if you need custom show behavior
        (e.g., spawn particles, play sounds), but make sure to call
        super().show() to get the standard behavior.
        """
        self.enabled = True
        for elem in self.ui_elements:
            if elem:  # Check for None to avoid errors
                elem.enabled = True

    def hide(self):
        """
        Hide this screen and all UI elements.

        Override this method if you need custom hide behavior
        (e.g., stop animations, clear particles), but make sure to call
        super().hide() to get the standard behavior.
        """
        self.enabled = False
        for elem in self.ui_elements:
            if elem:  # Check for None to avoid errors
                elem.enabled = False

        # Clear particles when hiding
        for particle in self.particles:
            if hasattr(particle, 'entity') and particle.entity:
                particle.entity.enabled = False
        self.particles.clear()

    def cleanup(self):
        """
        Clean up all resources (UI elements, particles, etc.).

        Call this when the screen is being destroyed or reset.
        Override this method if you have additional cleanup to do,
        but make sure to call super().cleanup().
        """
        for elem in self.ui_elements:
            if elem:
                destroy(elem)

        for particle in self.particles:
            if hasattr(particle, 'entity') and particle.entity:
                destroy(particle.entity)

        self.ui_elements.clear()
        self.particles.clear()

    def update(self):
        """
        Optional update method for animations.

        Override this method if your screen has animations or
        time-based updates (e.g., particle spawning, text pulsing).
        """
        pass

    def set_stats(self, stats):
        """
        Update screen stats (used by GameOver and Victory screens).

        Override this method if your screen displays stats.

        Args:
            stats: Dictionary of stat name -> value pairs
        """
        pass
