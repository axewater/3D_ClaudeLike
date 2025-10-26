"""
Voice Cache System

Caches procedurally generated voice lines using pyttsx3 for faster startup.
Generates voice files once and reuses them on subsequent launches.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import pygame.mixer
import numpy as np
from scipy import signal
import wave

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

# Death scream configurations (enemy_type -> transformation parameters)
DEATH_SCREAM_CONFIGS = {
    'startle': {
        'text': 'ha ha haa',   # Panicked laughter-scream
        'pitch_shift': 8,      # +8 semitones (high-pitched squeal)
        'time_stretch': 1.6,   # 160% duration (extended panic)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 200,       # Fast panicked voice
    },
    'slime': {
        'text': 'plupe plupe plupedeedoop',  # Bubbly splat sounds
        'pitch_shift': -8,     # -8 semitones (low bubbly)
        'time_stretch': 0.5,   # 50% duration (quick splat)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 200,       # Fast bubbling
    },
    'skeleton': {
        'text': 'oh nooh',     # Hollow mournful wail
        'pitch_shift': 12,     # +12 semitones (high hollow)
        'time_stretch': 2.0,   # 200% duration (long rattle)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 150,       # Medium pace
    },
    'orc': {
        'text': 'graar',       # Guttural roar
        'pitch_shift': 8,      # +8 semitones (guttural roar)
        'time_stretch': 1.5,   # 150% duration (long roar)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 125,       # Steady growl
    },
    'demon': {
        'text': 'aahh',        # KEEP AS-IS - sounds amazing!
        'pitch_shift': 12,     # +12 semitones (piercing screech)
        'time_stretch': 1.4,   # 140% duration (extended wail)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 110,
    },
    'dragon': {
        'text': 'haa',         # Epic roar
        'pitch_shift': 12,     # +12 semitones (epic roar)
        'time_stretch': 2.0,   # 200% duration (dramatic death)
        'distortion': 0.0,     # No white noise distortion
        'tts_rate': 125,       # Steady epic voice
    },
}


def load_wav_as_array(filepath: Path) -> tuple[np.ndarray, int]:
    """
    Load a WAV file as numpy array (handles mono/stereo, various bit depths).

    Args:
        filepath: Path to WAV file

    Returns:
        Tuple of (audio_data as float array, sample_rate)
    """
    with wave.open(str(filepath), 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        audio_bytes = wav_file.readframes(n_frames)

        # Convert to numpy array based on bit depth
        if sampwidth == 1:  # 8-bit
            audio = np.frombuffer(audio_bytes, dtype=np.uint8)
            audio = (audio.astype(np.float32) - 128) / 128.0
        elif sampwidth == 2:  # 16-bit
            audio = np.frombuffer(audio_bytes, dtype=np.int16)
            audio = audio.astype(np.float32) / 32768.0
        elif sampwidth == 4:  # 32-bit
            audio = np.frombuffer(audio_bytes, dtype=np.int32)
            audio = audio.astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        # If stereo, convert to mono by averaging channels
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            audio = np.mean(audio, axis=1)
        elif n_channels > 2:
            audio = audio.reshape(-1, n_channels)
            audio = np.mean(audio, axis=1)

        return audio, sample_rate


def save_array_as_wav(audio: np.ndarray, filepath: Path, sample_rate: int = 22050):
    """
    Save numpy array as WAV file.

    Args:
        audio: Audio data as float array (-1.0 to 1.0)
        filepath: Path to save WAV file
        sample_rate: Sample rate in Hz
    """
    # Normalize to prevent clipping
    audio = np.clip(audio, -1.0, 1.0)

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(str(filepath), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())


def pitch_shift_scipy(audio: np.ndarray, semitones: float, sample_rate: int = 22050) -> np.ndarray:
    """
    Shift pitch of audio by semitones using scipy resampling.

    Args:
        audio: Input audio as float array
        semitones: Number of semitones to shift (+12 = octave up, -12 = octave down)
        sample_rate: Sample rate of audio

    Returns:
        Pitch-shifted audio array
    """
    if semitones == 0:
        return audio

    # Calculate pitch shift factor (2^(semitones/12))
    shift_factor = 2.0 ** (semitones / 12.0)

    # Resample to shift pitch
    # Higher shift_factor = higher pitch (more samples)
    new_length = int(len(audio) * shift_factor)
    shifted = signal.resample(audio, new_length)

    return shifted


def time_stretch_scipy(audio: np.ndarray, stretch_factor: float) -> np.ndarray:
    """
    Stretch time of audio without changing pitch.

    Args:
        audio: Input audio as float array
        stretch_factor: Time stretch factor (1.5 = 150% duration, 0.8 = 80% duration)

    Returns:
        Time-stretched audio array
    """
    if stretch_factor == 1.0:
        return audio

    # Calculate new length
    new_length = int(len(audio) * stretch_factor)

    # Use linear interpolation to stretch
    old_indices = np.arange(len(audio))
    new_indices = np.linspace(0, len(audio) - 1, new_length)
    stretched = np.interp(new_indices, old_indices, audio)

    return stretched


def add_distortion(audio: np.ndarray, amount: float = 0.1) -> np.ndarray:
    """
    Add distortion/graininess to audio for variety.

    Args:
        audio: Input audio as float array
        amount: Amount of distortion (0.0 = none, 1.0 = full noise)

    Returns:
        Audio with distortion added
    """
    if amount <= 0:
        return audio

    # Generate noise
    noise = np.random.uniform(-1, 1, len(audio)) * amount

    # Mix noise with audio (weighted)
    distorted = audio * (1 - amount * 0.3) + noise * amount

    # Normalize to prevent clipping
    distorted = np.clip(distorted, -1.0, 1.0)

    return distorted


def apply_fade_out(audio: np.ndarray, fade_duration: float = 0.3) -> np.ndarray:
    """
    Apply fade-out envelope to audio.

    Args:
        audio: Input audio as float array
        fade_duration: Fade-out duration as fraction of audio length (0.0 to 1.0)

    Returns:
        Audio with fade-out applied
    """
    fade_samples = int(len(audio) * fade_duration)

    if fade_samples <= 0:
        return audio

    # Create envelope (1.0 at start, fade to 0.0 at end)
    envelope = np.ones(len(audio))
    envelope[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    return audio * envelope


def cache_exists() -> bool:
    """
    Check if voice cache exists and is complete.

    Returns:
        True if all expected voice files are present, False otherwise
    """
    if not CACHE_ROOT.exists():
        return False

    # Check if all expected voice line files exist
    for key in VOICE_LINES.keys():
        voice_file = CACHE_ROOT / f"{key}.wav"
        if not voice_file.exists():
            return False

    # Check if all expected death scream files exist
    for enemy_type in DEATH_SCREAM_CONFIGS.keys():
        scream_file = CACHE_ROOT / f"death_scream_{enemy_type}.wav"
        if not scream_file.exists():
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


def transform_death_scream(enemy_type: str, config: dict) -> bool:
    """
    Transform a TTS file into a death scream (called after TTS generation).

    Args:
        enemy_type: Enemy type key (e.g., 'startle', 'orc')
        config: Configuration dict with transformation parameters

    Returns:
        True if transformation succeeded, False otherwise
    """
    try:
        # File paths
        temp_file = CACHE_ROOT / f"_temp_{enemy_type}.wav"
        final_file = CACHE_ROOT / f"death_scream_{enemy_type}.wav"

        # Check if temp file exists
        if not temp_file.exists():
            return False

        # Load and transform the audio
        audio, sample_rate = load_wav_as_array(temp_file)
        audio = time_stretch_scipy(audio, config['time_stretch'])
        audio = pitch_shift_scipy(audio, config['pitch_shift'], sample_rate)
        audio = add_distortion(audio, config['distortion'])
        audio = apply_fade_out(audio, fade_duration=0.3)

        # Save transformed audio
        save_array_as_wav(audio, final_file, sample_rate)

        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()

        return True

    except Exception as e:
        print(f"  ⚠ Failed to transform death scream for '{enemy_type}': {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_voice_cache():
    """
    Generate all voice lines and death screams, saving them to disk cache.
    Uses pyttsx3 to synthesize speech for each class name and enemy death scream.
    """
    if not PYTTSX3_AVAILABLE:
        return

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

        # Queue all TTS generations (voice lines + death screams)
        # We queue everything first, then call runAndWait() ONCE to avoid hangs

        # Queue voice lines
        for key, text in VOICE_LINES.items():
            output_file = get_cache_filename(key)
            engine.save_to_file(text, str(output_file))

        # Queue death scream base TTS files
        for enemy_type, config in DEATH_SCREAM_CONFIGS.items():
            temp_file = CACHE_ROOT / f"_temp_{enemy_type}.wav"
            engine.setProperty('rate', config['tts_rate'])
            engine.save_to_file(config['text'], str(temp_file))

        # Process the entire queue with ONE runAndWait() call
        engine.runAndWait()
        engine.stop()

        # Now transform death screams (TTS files already exist)
        scream_count = 0
        for enemy_type, config in DEATH_SCREAM_CONFIGS.items():
            if transform_death_scream(enemy_type, config):
                scream_count += 1

        print(f"✓ Voice cache generated: {len(VOICE_LINES)} lines + {scream_count} screams")

    except Exception as e:
        print(f"⚠ Error generating voice cache: {e}")
        print("  Voice effects will be disabled")


def load_voice_cache() -> Dict[str, pygame.mixer.Sound]:
    """
    Load all voice files and death screams from disk cache.

    Returns:
        Dict[voice_key -> pygame.mixer.Sound] ready for playback
        Includes both regular voice lines and death screams
    """
    voices = {}

    # Load regular voice lines
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

    # Load death screams
    for enemy_type in DEATH_SCREAM_CONFIGS.keys():
        scream_key = f"death_scream_{enemy_type}"
        scream_path = CACHE_ROOT / f"{scream_key}.wav"

        if scream_path.exists():
            try:
                sound = pygame.mixer.Sound(str(scream_path))
                voices[scream_key] = sound
            except Exception as e:
                print(f"⚠ Failed to load death scream '{enemy_type}': {e}")
        else:
            print(f"⚠ Death scream file not found: {scream_path}")

    return voices


def ensure_voice_cache() -> Dict[str, pygame.mixer.Sound]:
    """
    Ensure voice cache exists, generating it if necessary, then load and return voices.

    Returns:
        Dict[voice_key -> pygame.mixer.Sound] ready for playback
    """
    if not cache_exists():
        generate_voice_cache()

    # Load the cache
    return load_voice_cache()
