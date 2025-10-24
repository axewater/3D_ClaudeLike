"""
Voice Cache System

Caches procedurally generated voice lines using pyttsx3 for faster startup.
Generates voice files once and reuses them on subsequent launches.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import pygame.mixer

# Try to import pyttsx3, but make it optional
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Warning: pyttsx3 not available, voice effects will be disabled")


# Cache directory
CACHE_ROOT = Path("ursina_cache/voices")

# Voice lines to generate (class names and game events)
VOICE_LINES = {
    'warrior': 'Warrior',
    'mage': 'Mage',
    'rogue': 'Rogue',
    'ranger': 'Ranger',
    'dungeon_entrance': 'You will never escape',
}


def cache_exists() -> bool:
    """
    Check if voice cache exists and is complete.

    Returns:
        True if all expected voice files are present, False otherwise
    """
    if not CACHE_ROOT.exists():
        return False

    # Check if all expected files exist
    for key in VOICE_LINES.keys():
        voice_file = CACHE_ROOT / f"{key}.wav"
        if not voice_file.exists():
            return False

    return True


def get_cache_filename(voice_key: str) -> Path:
    """
    Get cache filename for a specific voice line.

    Args:
        voice_key: Key for the voice line (e.g., 'warrior', 'mage')

    Returns:
        Path to cache file
    """
    return CACHE_ROOT / f"{voice_key}.wav"


def generate_voice_cache():
    """
    Generate all voice lines and save them to disk cache.
    Uses pyttsx3 to synthesize speech for each class name.
    """
    if not PYTTSX3_AVAILABLE:
        print("⚠ Skipping voice generation - pyttsx3 not available")
        return

    print("Generating voice cache...")

    # Create cache directory
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    # Initialize TTS engine
    try:
        engine = pyttsx3.init()

        # Configure voice properties
        # Set rate (speed) - default is 200, we'll slow it down a bit
        engine.setProperty('rate', 150)

        # Set volume (0.0 to 1.0)
        engine.setProperty('volume', 1.0)

        # Try to set a good voice (prefer male voices for game feel)
        voices = engine.getProperty('voices')
        if voices:
            # Try to find a male voice
            male_voice = None
            for voice in voices:
                if 'male' in voice.name.lower() and 'female' not in voice.name.lower():
                    male_voice = voice
                    break
            if male_voice:
                engine.setProperty('voice', male_voice.id)
            else:
                # Just use the first available voice
                engine.setProperty('voice', voices[0].id)

        # Generate each voice line
        for key, text in VOICE_LINES.items():
            output_file = get_cache_filename(key)

            # Save to file
            engine.save_to_file(text, str(output_file))

        # Process the queue (actually generate the files)
        engine.runAndWait()

        # Clean up
        engine.stop()

        print(f"✓ Voice cache saved to {CACHE_ROOT} ({len(VOICE_LINES)} voice lines)")

    except Exception as e:
        print(f"⚠ Error generating voice cache: {e}")
        print("  Voice effects will be disabled")


def load_voice_cache() -> Dict[str, pygame.mixer.Sound]:
    """
    Load all voice files from disk cache.

    Returns:
        Dict[voice_key -> pygame.mixer.Sound] ready for playback
    """
    print("Loading voice cache from disk...")

    voices = {}

    for key in VOICE_LINES.keys():
        cache_path = get_cache_filename(key)

        if cache_path.exists():
            try:
                # Load the WAV file as a pygame Sound
                sound = pygame.mixer.Sound(str(cache_path))
                voices[key] = sound
            except Exception as e:
                print(f"⚠ Failed to load voice '{key}': {e}")
        else:
            print(f"⚠ Voice file not found: {cache_path}")

    print(f"✓ Voice cache loaded from {CACHE_ROOT} ({len(voices)} voice lines)")

    return voices


def ensure_voice_cache() -> Dict[str, pygame.mixer.Sound]:
    """
    Ensure voice cache exists, generating it if necessary, then load and return voices.

    Returns:
        Dict[voice_key -> pygame.mixer.Sound] ready for playback
    """
    if not cache_exists():
        print("Voice cache not found, generating...")
        generate_voice_cache()

    # Load the cache
    return load_voice_cache()
