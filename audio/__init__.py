"""
Audio module - Sound and music systems.

Contains procedural audio synthesis, voice caching, and audio management.

Note: audio.py has been renamed to manager.py to avoid module/file name collision.
Import like: from audio.manager import AudioManager, get_audio_manager
"""

# Re-export common functions for backward compatibility
from audio.manager import AudioManager, get_audio_manager

__all__ = ['AudioManager', 'get_audio_manager']
