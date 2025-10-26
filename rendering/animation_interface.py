"""
Abstract animation manager interface
This defines the contract that both 2D and 3D animation managers must implement.
"""
from abc import ABC, abstractmethod
from typing import Tuple, List

# Type alias for RGB color tuples (0-1 range)
ColorRGB = Tuple[float, float, float]


class AnimationManagerInterface(ABC):
    """Abstract base class for animation managers.

    Both 2D and 3D animation managers must implement this interface.
    Colors are passed as RGB tuples (0-1 range) to avoid PyQt6 dependencies.
    """

    @property
    @abstractmethod
    def particles(self):
        """Get the particles list (must support append())"""
        pass

    @abstractmethod
    def add_flash_effect(self, x: int, y: int, color: ColorRGB = None):
        """Add hit flash effect at grid position"""
        pass

    @abstractmethod
    def add_particle_burst(self, x: int, y: int, color: ColorRGB, count: int = 8,
                          particle_type: str = "square"):
        """Create burst of particles at grid position"""
        pass

    @abstractmethod
    def add_blood_splatter(self, x: int, y: int):
        """Create blood splatter effect at grid position"""
        pass

    @abstractmethod
    def add_heal_sparkles(self, x: int, y: int):
        """Create healing sparkle effect at grid position"""
        pass

    @abstractmethod
    def add_screen_shake(self, intensity: float = 5.0, duration: float = 0.2):
        """Add screen shake effect"""
        pass

    @abstractmethod
    def add_directional_impact(self, x: int, y: int, from_x: int, from_y: int,
                               color: ColorRGB, count: int = 10, is_crit: bool = False):
        """Create directional particle burst (sprays away from attacker)"""
        pass

    @abstractmethod
    def add_trail(self, x: int, y: int, color: ColorRGB, trail_type: str = "fade"):
        """Add trail effect at grid position"""
        pass

    @abstractmethod
    def add_ability_trail(self, x: int, y: int, color: ColorRGB, ability_type: str):
        """Add ability-specific trail effect at grid position"""
        pass

    @abstractmethod
    def add_ambient_particles(self, count: int = 1):
        """Add ambient particles (snow, ash, etc.)"""
        pass

    @abstractmethod
    def add_fog_particles(self, count: int = 1):
        """Add fog particles"""
        pass

    @abstractmethod
    def add_alert_particle(self, enemy):
        """Add alert particle above enemy"""
        pass

    @abstractmethod
    def add_damage_number(self, enemy, damage: int, damage_type: str = "normal"):
        """Add floating damage number above enemy"""
        pass

    @abstractmethod
    def add_player_damage_number(self, damage: int):
        """Add damage number in HUD for player"""
        pass

    @abstractmethod
    def add_death_burst(self, x: int, y: int, enemy_type: str):
        """Create death burst effect for enemy type"""
        pass

    @abstractmethod
    def add_level_title(self, level_number: int):
        """Add level entry title card"""
        pass

    @abstractmethod
    def update(self, dt: float):
        """Update all animations"""
        pass

    @abstractmethod
    def clear_all(self):
        """Clear all active animations"""
        pass
