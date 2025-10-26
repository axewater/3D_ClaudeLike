"""
Settings Management System

Handles saving and loading game settings to/from a JSON file.
Settings persist between game sessions.
"""

import json
import os
from typing import Dict, Any
import constants as c


# Settings file path (in the game directory)
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "game_settings.json")


def get_default_settings() -> Dict[str, Any]:
    """
    Get default settings from constants.

    Returns:
        Dictionary of default settings
    """
    return {
        "music_volume": 0.7,
        "sfx_volume": 0.8,
        "particle_density": c.PARTICLE_DENSITY,
        "fullscreen": c.FULLSCREEN
    }


def load_settings() -> Dict[str, Any]:
    """
    Load settings from JSON file.

    Returns:
        Dictionary of settings (defaults if file doesn't exist)
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                print(f"[Settings] Loaded settings from {SETTINGS_FILE}")
                return settings
        else:
            print(f"[Settings] No settings file found, using defaults")
            return get_default_settings()
    except Exception as e:
        print(f"[Settings] Error loading settings: {e}")
        return get_default_settings()


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save settings to JSON file.

    Args:
        settings: Dictionary of settings to save

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"[Settings] Saved settings to {SETTINGS_FILE}")
        return True
    except Exception as e:
        print(f"[Settings] Error saving settings: {e}")
        return False


def apply_settings_to_constants(settings: Dict[str, Any]):
    """
    Apply loaded settings to constants module.

    Args:
        settings: Dictionary of settings to apply
    """
    c.PARTICLE_DENSITY = settings.get("particle_density", 0.5)
    c.FULLSCREEN = settings.get("fullscreen", False)
    print(f"[Settings] Applied settings to constants:")
    print(f"  - Particle Density: {c.PARTICLE_DENSITY}")
    print(f"  - Fullscreen: {c.FULLSCREEN}")


def get_current_settings() -> Dict[str, Any]:
    """
    Get current settings from constants and audio manager.

    Returns:
        Dictionary of current settings
    """
    settings = {
        "particle_density": c.PARTICLE_DENSITY,
        "fullscreen": c.FULLSCREEN
    }

    # Try to get audio settings if audio manager is initialized
    try:
        from audio import get_audio_manager
        audio = get_audio_manager()
        settings["music_volume"] = audio.music_volume
        settings["sfx_volume"] = audio.sfx_volume
    except:
        # Audio not initialized yet, use defaults
        settings["music_volume"] = 0.7
        settings["sfx_volume"] = 0.8

    return settings


# Convenience functions for common operations
def save_current_settings() -> bool:
    """Save current settings to file"""
    return save_settings(get_current_settings())


def load_and_apply_settings():
    """Load settings from file and apply to constants"""
    settings = load_settings()
    apply_settings_to_constants(settings)
    return settings
