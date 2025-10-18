"""
Audio system for Claude-Like
Handles all sound effects and background music with procedural sound generation
"""
import pygame
import numpy as np
import random
import io
import os
import tempfile
import threading
from typing import Dict, Optional


class SoundSynthesizer:
    """Generate procedural retro-style game sounds"""

    SAMPLE_RATE = 22050  # Hz

    @staticmethod
    def generate_sine_wave(frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """Generate a sine wave"""
        samples = int(SoundSynthesizer.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        wave = np.sin(2 * np.pi * frequency * t)

        # Apply envelope (fade in/out)
        envelope = np.ones(samples)
        fade_samples = min(int(samples * 0.1), 1000)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        wave = wave * envelope * volume
        return wave

    @staticmethod
    def generate_noise(duration: float, volume: float = 0.3) -> np.ndarray:
        """Generate white noise"""
        samples = int(SoundSynthesizer.SAMPLE_RATE * duration)
        noise = np.random.uniform(-1, 1, samples) * volume

        # Apply envelope
        envelope = np.ones(samples)
        fade_samples = int(samples * 0.5)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        return noise * envelope

    @staticmethod
    def generate_sweep(start_freq: float, end_freq: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """Generate frequency sweep"""
        samples = int(SoundSynthesizer.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)

        # Exponential sweep
        freq = start_freq * (end_freq / start_freq) ** (t / duration)
        phase = 2 * np.pi * freq * t
        wave = np.sin(phase) * volume

        # Apply envelope
        envelope = np.ones(samples)
        fade_samples = int(samples * 0.3)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        return wave * envelope

    @staticmethod
    def generate_square_wave(frequency: float, duration: float, volume: float = 0.3) -> np.ndarray:
        """Generate square wave (retro game sound)"""
        samples = int(SoundSynthesizer.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        wave = np.sign(np.sin(2 * np.pi * frequency * t)) * volume

        # Apply envelope
        envelope = np.ones(samples)
        fade_samples = int(samples * 0.2)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        return wave * envelope

    @staticmethod
    def combine_waves(*waves: np.ndarray) -> np.ndarray:
        """Combine multiple waveforms, padding to the longest duration"""
        if not waves:
            return np.array([])

        # Find the longest wave
        max_length = max(len(wave) for wave in waves)

        # Pad all waves to the same length and combine
        padded_waves = []
        for wave in waves:
            if len(wave) < max_length:
                padding = np.zeros(max_length - len(wave))
                wave = np.concatenate([wave, padding])
            padded_waves.append(wave)

        # Sum all waves
        return np.sum(padded_waves, axis=0)

    @staticmethod
    def array_to_sound(wave: np.ndarray) -> pygame.mixer.Sound:
        """Convert numpy array to pygame Sound object"""
        # Normalize to 16-bit range
        wave = np.int16(wave * 32767)

        # Create stereo sound
        stereo = np.repeat(wave.reshape(-1, 1), 2, axis=1)

        # Convert to bytes
        sound_data = stereo.tobytes()

        # Create Sound from bytes
        sound = pygame.mixer.Sound(buffer=sound_data)
        return sound


class VoiceSynthesizer:
    """Generate robotic text-to-speech voices using pyttsx3"""

    def __init__(self):
        """Initialize voice synthesizer with robotic settings"""
        self.voice_cache: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self.engine = None
        self.cache_lock = threading.Lock()  # Thread safety for cache
        self.shutdown_flag = False

        try:
            import pyttsx3
            self.engine = pyttsx3.init()

            # Configure robotic voice settings
            self.engine.setProperty('rate', 120)  # Slow robotic pace (default ~200)
            self.engine.setProperty('volume', 0.9)  # Slightly quieter

            # Try to set pitch lower (not all engines support this)
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
            except:
                pass  # Pitch/voice selection not available on this system

            print("✓ Voice synthesizer initialized (pyttsx3 working)")
        except Exception as e:
            print(f"⚠ Voice synthesis unavailable: {e}")
            print("  To enable voice taunts, install: pip install pyttsx3")
            print("  Linux users also need: sudo apt-get install espeak")
            self.engine = None
            self.enabled = False

    def generate_voice(self, text: str) -> Optional[pygame.mixer.Sound]:
        """
        Generate robot voice for given text and return as pygame Sound
        Thread-safe method that checks cache first.

        Args:
            text: The text to synthesize

        Returns:
            pygame.mixer.Sound object or None if generation failed
        """
        if not self.enabled or not self.engine or self.shutdown_flag:
            return None

        # Check cache first (thread-safe)
        with self.cache_lock:
            if text in self.voice_cache:
                return self.voice_cache[text]

        # Retry up to 5 times if file generation fails
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Create temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_path = tmp_file.name

                # Generate speech to file
                self.engine.save_to_file(text, tmp_path)
                self.engine.runAndWait()

                # Wait a bit for file to be fully written (especially on slower systems)
                import time
                time.sleep(0.05)  # 50ms delay

                # Validate the WAV file before loading
                if not self._validate_wav_file(tmp_path):
                    # File is corrupted or empty
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

                    if attempt < max_retries - 1:
                        # Retry with exponential backoff
                        wait_time = 0.1 * (2 ** attempt)  # 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
                        print(f"⚠ Voice file corrupted for '{text}', retrying ({attempt + 1}/{max_retries}) after {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"⚠ Failed to generate valid voice file for '{text}' after {max_retries} attempts")
                        return None

                # File is valid, load as pygame Sound
                sound = pygame.mixer.Sound(tmp_path)

                # Cache the sound (thread-safe)
                with self.cache_lock:
                    self.voice_cache[text] = sound

                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass  # File cleanup failed, but sound is loaded

                return sound

            except Exception as e:
                if not self.shutdown_flag:
                    if attempt < max_retries - 1:
                        print(f"⚠ Error generating voice for '{text}': {e}, retrying ({attempt + 1}/{max_retries})...")
                        import time
                        time.sleep(0.1 * (2 ** attempt))
                        continue
                    else:
                        print(f"⚠ Failed to generate voice for '{text}': {e}")
                return None

        return None

    def _validate_wav_file(self, file_path: str) -> bool:
        """
        Validate that a WAV file exists and has proper structure

        Args:
            file_path: Path to WAV file to validate

        Returns:
            True if file is valid, False otherwise
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False

            # Check file has content (minimum WAV header is 44 bytes)
            file_size = os.path.getsize(file_path)
            if file_size < 44:
                return False

            # Try to read and validate WAV header
            with open(file_path, 'rb') as f:
                # Read first 12 bytes (RIFF header)
                header = f.read(12)

                if len(header) < 12:
                    return False

                # Check RIFF signature
                if header[0:4] != b'RIFF':
                    return False

                # Check WAVE signature
                if header[8:12] != b'WAVE':
                    return False

            return True

        except Exception as e:
            return False

    def shutdown(self):
        """Shutdown the voice synthesizer and cleanup resources"""
        self.shutdown_flag = True
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        self.enabled = False
        print("✓ Voice synthesizer shutdown")


class AudioManager:
    """Manages all game audio - sound effects and music"""

    def __init__(self):
        """Initialize audio system"""
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.mixer.init()

        # Audio state
        self.enabled = True
        self.sfx_volume = 0.7
        self.music_volume = 0.4
        self.voice_volume = 0.6  # Slightly quieter than SFX

        # Sound cache
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        # Music state
        self.current_music_intensity = 0.0  # 0.0 = calm, 1.0 = combat
        self.music_ducking = 1.0  # Multiplier for music volume
        self.music_track = None

        # Combat state for adaptive audio
        self.enemies_nearby = 0
        self.in_combat = False

        # Voice synthesizer
        self.voice_synth = VoiceSynthesizer()

        # Generate all sounds
        self._generate_sounds()

    def _generate_sounds(self):
        """Generate all procedural game sounds"""
        synth = SoundSynthesizer()

        # === COMBAT SOUNDS ===

        # Light attack - quick swish
        light_attack = synth.generate_sweep(400, 200, 0.1, 0.4)
        self.sounds['attack_light'] = synth.array_to_sound(light_attack)

        # Medium attack - deeper swish
        medium_attack = synth.generate_sweep(300, 150, 0.15, 0.5)
        self.sounds['attack_medium'] = synth.array_to_sound(medium_attack)

        # Heavy attack - powerful swish
        heavy_attack = synth.generate_sweep(250, 100, 0.2, 0.6)
        self.sounds['attack_heavy'] = synth.array_to_sound(heavy_attack)

        # Hit impact - thud
        hit = synth.combine_waves(
            synth.generate_noise(0.1, 0.4),
            synth.generate_sine_wave(80, 0.1, 0.3)
        )
        self.sounds['hit'] = synth.array_to_sound(hit)

        # Critical hit - special impact
        crit = synth.combine_waves(
            synth.generate_noise(0.15, 0.5),
            synth.generate_sine_wave(120, 0.15, 0.4),
            synth.generate_sine_wave(240, 0.15, 0.2)
        )
        self.sounds['crit'] = synth.array_to_sound(crit)

        # === ENEMY SOUNDS ===

        # Goblin death - high pitched squeal
        goblin_death = synth.generate_sweep(800, 400, 0.3, 0.5)
        self.sounds['enemy_death_goblin'] = synth.array_to_sound(goblin_death)

        # Slime death - wet splat
        slime_death = synth.combine_waves(
            synth.generate_sweep(300, 100, 0.25, 0.5),
            synth.generate_noise(0.15, 0.35)
        )
        self.sounds['enemy_death_slime'] = synth.array_to_sound(slime_death)

        # Skeleton death - bone rattle
        skeleton_death = synth.generate_noise(0.25, 0.4)
        self.sounds['enemy_death_skeleton'] = synth.array_to_sound(skeleton_death)

        # Orc death - deep guttural roar
        orc_death = synth.combine_waves(
            synth.generate_sweep(150, 50, 0.4, 0.6),
            synth.generate_noise(0.3, 0.3)
        )
        self.sounds['enemy_death_orc'] = synth.array_to_sound(orc_death)

        # Demon death - demonic screech
        demon_death = synth.combine_waves(
            synth.generate_sweep(800, 200, 0.35, 0.5),
            synth.generate_sweep(200, 100, 0.35, 0.4),
            synth.generate_noise(0.2, 0.3)
        )
        self.sounds['enemy_death_demon'] = synth.array_to_sound(demon_death)

        # Dragon death - epic roar
        dragon_death = synth.combine_waves(
            synth.generate_sweep(200, 50, 0.5, 0.6),
            synth.generate_noise(0.5, 0.3)
        )
        self.sounds['enemy_death_dragon'] = synth.array_to_sound(dragon_death)

        # === ABILITY SOUNDS ===

        # Fireball - whoosh + explosion
        fireball = synth.combine_waves(
            synth.generate_sweep(600, 200, 0.3, 0.5),
            synth.generate_noise(0.15, 0.3)
        )
        self.sounds['ability_fireball'] = synth.array_to_sound(fireball)

        # Dash/Teleport - blink sound
        dash = synth.generate_sweep(1000, 2000, 0.15, 0.4)
        self.sounds['ability_dash'] = synth.array_to_sound(dash)

        # Healing - gentle chime
        heal = synth.combine_waves(
            synth.generate_sine_wave(523, 0.3, 0.3),  # C
            synth.generate_sine_wave(659, 0.3, 0.2),  # E
            synth.generate_sine_wave(784, 0.3, 0.2)   # G
        )
        self.sounds['ability_heal'] = synth.array_to_sound(heal)

        # Frost Nova - ice crystallization
        frost = synth.combine_waves(
            synth.generate_sine_wave(1200, 0.3, 0.3),
            synth.generate_sine_wave(1600, 0.3, 0.2)
        )
        self.sounds['ability_frost'] = synth.array_to_sound(frost)

        # Whirlwind - spinning blade
        whirlwind = synth.generate_sweep(300, 600, 0.4, 0.5)
        self.sounds['ability_whirlwind'] = synth.array_to_sound(whirlwind)

        # Shadow Step - dark energy
        shadow = synth.generate_sweep(400, 100, 0.25, 0.5)
        self.sounds['ability_shadow'] = synth.array_to_sound(shadow)

        # === MOVEMENT & INTERACTION ===

        # Footstep - soft thud
        footstep = synth.combine_waves(
            synth.generate_noise(0.05, 0.15),
            synth.generate_sine_wave(60, 0.05, 0.1)
        )
        self.sounds['footstep'] = synth.array_to_sound(footstep)

        # Item pickup - ascending notes
        pickup = synth.combine_waves(
            synth.generate_sine_wave(440, 0.1, 0.2),
            synth.generate_sine_wave(554, 0.1, 0.15)
        )
        self.sounds['item_pickup'] = synth.array_to_sound(pickup)

        # Rare item pickup - special sparkle
        pickup_rare = synth.combine_waves(
            synth.generate_sine_wave(659, 0.15, 0.25),
            synth.generate_sine_wave(784, 0.15, 0.2),
            synth.generate_sine_wave(988, 0.15, 0.15)
        )
        self.sounds['item_pickup_rare'] = synth.array_to_sound(pickup_rare)

        # Potion drink - gulp
        potion = synth.generate_sweep(300, 200, 0.2, 0.3)
        self.sounds['potion_drink'] = synth.array_to_sound(potion)

        # Equip item - clank
        equip = synth.combine_waves(
            synth.generate_noise(0.1, 0.3),
            synth.generate_sine_wave(150, 0.1, 0.3)
        )
        self.sounds['equip'] = synth.array_to_sound(equip)

        # Stairs descend - descending tones
        stairs = synth.generate_sweep(500, 250, 0.4, 0.4)
        self.sounds['stairs'] = synth.array_to_sound(stairs)

        # Coin pickup - high-pitched metallic clink
        coin = synth.combine_waves(
            synth.generate_sine_wave(1200, 0.08, 0.3),  # High bright tone
            synth.generate_sine_wave(1800, 0.06, 0.15)  # Even higher overtone
        )
        self.sounds['coin'] = synth.array_to_sound(coin)

        # === UI SOUNDS ===

        # Level up - fanfare
        levelup = synth.combine_waves(
            synth.generate_sine_wave(523, 0.5, 0.3),   # C
            synth.generate_sine_wave(659, 0.5, 0.25),  # E
            synth.generate_sine_wave(784, 0.5, 0.3),   # G
            synth.generate_sine_wave(1047, 0.5, 0.25)  # C (octave)
        )
        self.sounds['levelup'] = synth.array_to_sound(levelup)

        # Game over - dramatic descending tones
        gameover = synth.generate_sweep(400, 100, 0.8, 0.6)
        self.sounds['gameover'] = synth.array_to_sound(gameover)

        # Menu select - click
        select = synth.generate_sine_wave(800, 0.05, 0.3)
        self.sounds['ui_select'] = synth.array_to_sound(select)

        # Menu hover - soft tick
        hover = synth.generate_sine_wave(600, 0.03, 0.15)
        self.sounds['ui_hover'] = synth.array_to_sound(hover)

        # === TITLE SCREEN EFFECTS ===

        # Letter whoosh - deep stone brick rumble
        whoosh = synth.combine_waves(
            synth.generate_sweep(200, 60, 0.35, 0.5),      # Deep air displacement
            synth.generate_sine_wave(45, 0.35, 0.35),      # Sub-bass weight
            synth.generate_noise(0.3, 0.25)                # Low rumble texture
        )
        self.sounds['letter_whoosh'] = synth.array_to_sound(whoosh)

        # Letter impact - deep stone brick thump
        impact = synth.combine_waves(
            synth.generate_sine_wave(45, 0.12, 0.45),      # Sub-bass rumble
            synth.generate_sine_wave(65, 0.12, 0.4),       # Low thump
            synth.generate_sweep(80, 35, 0.10, 0.35),      # Settling sweep
            synth.generate_noise(0.08, 0.3)                # Impact texture
        )
        self.sounds['letter_impact'] = synth.array_to_sound(impact)

        print(f"✓ Generated {len(self.sounds)} procedural sound effects")

    def _generate_ambient_music(self):
        """Generate ambient background music loop with melody and rhythm"""
        synth = SoundSynthesizer()

        # Musical parameters
        note_duration = 0.8  # Each note lasts 0.8 seconds
        gap_duration = 0.15  # Small gap between notes
        phrase_gap = 1.0  # Longer gap between phrases

        # Minor scale notes (A minor for dark atmosphere)
        # A, B, C, D, E, F, G
        scale_freqs = [220, 247, 262, 294, 330, 349, 392]  # A3 minor scale

        # Create multiple melodic phrases
        phrases = []

        # Phrase 1: Descending arpeggio (A - E - C - A)
        phrase1_notes = [scale_freqs[0], scale_freqs[4], scale_freqs[2], scale_freqs[0]]
        phrase1 = self._create_phrase(synth, phrase1_notes, note_duration, gap_duration, 0.12)
        phrases.append(phrase1)

        # Phrase 2: Rising pattern (C - D - E - F)
        phrase2_notes = [scale_freqs[2], scale_freqs[3], scale_freqs[4], scale_freqs[5]]
        phrase2 = self._create_phrase(synth, phrase2_notes, note_duration, gap_duration, 0.10)
        phrases.append(phrase2)

        # Phrase 3: Ambient chord (A + C + E sustained with pulse)
        chord = self._create_pulsing_chord(synth, [scale_freqs[0], scale_freqs[2], scale_freqs[4]],
                                          duration=3.0, pulse_speed=0.5)
        phrases.append(chord)

        # Add silences between phrases
        silence_short = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * gap_duration))
        silence_long = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * phrase_gap))

        # Combine phrases with gaps for breathing
        music = np.concatenate([
            phrases[0], silence_short,
            phrases[1], silence_long,
            phrases[2], silence_long,
            phrases[0], silence_short,  # Repeat first phrase
        ])

        # Add subtle bass drone underneath (much quieter)
        bass_duration = len(music) / SoundSynthesizer.SAMPLE_RATE
        bass_drone = synth.generate_sine_wave(110, bass_duration, 0.05)  # Very quiet

        # Apply slow amplitude modulation to bass for "breathing"
        breath_rate = 0.3  # Hz
        breath_envelope = np.sin(2 * np.pi * breath_rate * np.linspace(0, bass_duration, len(bass_drone))) * 0.5 + 0.5
        bass_drone = bass_drone * breath_envelope

        # Combine melody with bass
        final_music = synth.combine_waves(music, bass_drone)

        return synth.array_to_sound(final_music)

    def _create_phrase(self, synth, frequencies, note_duration, gap_duration, volume):
        """Create a melodic phrase from a sequence of notes"""
        notes = []
        for freq in frequencies:
            # Generate note with fade in/out envelope
            note = synth.generate_sine_wave(freq, note_duration, volume)

            # Apply envelope (fade in and out) for smooth notes
            envelope = self._create_envelope(len(note), attack=0.05, release=0.3)
            note = note * envelope

            notes.append(note)

            # Add gap between notes
            if gap_duration > 0:
                gap = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * gap_duration))
                notes.append(gap)

        return np.concatenate(notes)

    def _create_pulsing_chord(self, synth, frequencies, duration, pulse_speed):
        """Create a chord that pulses in volume"""
        # Generate each note in the chord
        chord_notes = [synth.generate_sine_wave(freq, duration, 0.08) for freq in frequencies]

        # Combine into chord
        chord = synth.combine_waves(*chord_notes)

        # Apply pulsing envelope
        pulse_envelope = np.sin(2 * np.pi * pulse_speed * np.linspace(0, duration, len(chord))) * 0.4 + 0.6
        chord = chord * pulse_envelope

        return chord

    def _create_envelope(self, length, attack=0.1, release=0.2):
        """Create an amplitude envelope (ADSR-style)"""
        envelope = np.ones(length)

        # Attack (fade in)
        attack_samples = int(length * attack)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Release (fade out)
        release_samples = int(length * release)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)

        return envelope

    def play_sound(self, sound_name: str, volume: float = 1.0, pitch_variation: float = 0.1,
                   position: tuple = None, player_position: tuple = None):
        """
        Play a sound effect with optional pitch variation and positional audio

        Args:
            sound_name: Name of the sound to play
            volume: Volume multiplier (0.0 to 1.0)
            pitch_variation: Random pitch variation amount (0.0 to 1.0)
            position: World position of sound source (x, y)
            player_position: Player position for positional audio (x, y)
        """
        if not self.enabled or sound_name not in self.sounds:
            return

        sound = self.sounds[sound_name]

        # Calculate volume based on distance (positional audio)
        final_volume = volume * self.sfx_volume
        if position and player_position:
            distance = abs(position[0] - player_position[0]) + abs(position[1] - player_position[1])
            # Volume falls off with distance (max range 10 tiles)
            distance_factor = max(0, 1.0 - (distance / 10.0))
            final_volume *= distance_factor

        # Set volume
        sound.set_volume(final_volume)

        # Play with pitch variation if supported
        channel = sound.play()

        if channel and pitch_variation > 0:
            # Simulate pitch variation by playing at different volumes
            # (pygame doesn't support pitch shifting directly, but this adds variety)
            variation = random.uniform(1.0 - pitch_variation, 1.0 + pitch_variation)
            sound.set_volume(final_volume * variation)

    def play_attack_sound(self, attack_strength: str = 'medium'):
        """Play attack sound based on strength"""
        sound_map = {
            'light': 'attack_light',
            'medium': 'attack_medium',
            'heavy': 'attack_heavy'
        }
        sound_name = sound_map.get(attack_strength, 'attack_medium')
        self.play_sound(sound_name, pitch_variation=0.15)

    def play_hit_sound(self, is_crit: bool = False, position: tuple = None, player_position: tuple = None):
        """Play hit impact sound"""
        sound_name = 'crit' if is_crit else 'hit'
        volume = 1.2 if is_crit else 1.0
        self.play_sound(sound_name, volume=volume, pitch_variation=0.2,
                       position=position, player_position=player_position)

    def play_enemy_death(self, enemy_type: str, position: tuple = None, player_position: tuple = None):
        """Play enemy death sound"""
        sound_name = f'enemy_death_{enemy_type}'
        if sound_name in self.sounds:
            self.play_sound(sound_name, volume=0.9, pitch_variation=0.1,
                           position=position, player_position=player_position)

    def play_ability_sound(self, ability_name: str):
        """Play ability sound effect"""
        # Map ability names to sound keys
        sound_map = {
            'Fireball': 'ability_fireball',
            'Dash': 'ability_dash',
            'Healing Touch': 'ability_heal',
            'Frost Nova': 'ability_frost',
            'Whirlwind': 'ability_whirlwind',
            'Shadow Step': 'ability_shadow',
        }

        sound_name = sound_map.get(ability_name)
        if sound_name:
            self.play_sound(sound_name, volume=1.0, pitch_variation=0.05)

    def play_footstep(self, position: tuple = None, player_position: tuple = None):
        """Play footstep sound"""
        # Quiet footsteps with variation
        self.play_sound('footstep', volume=0.3, pitch_variation=0.25,
                       position=position, player_position=player_position)

    def play_item_pickup(self, rarity: str = 'common'):
        """Play item pickup sound based on rarity"""
        if rarity in ['rare', 'epic', 'legendary']:
            self.play_sound('item_pickup_rare', volume=0.9)
        else:
            self.play_sound('item_pickup', volume=0.7, pitch_variation=0.2)

    def play_potion(self):
        """Play potion drinking sound"""
        self.play_sound('potion_drink', volume=0.8)

    def play_coin(self):
        """Play coin pickup sound"""
        self.play_sound('coin', volume=0.7, pitch_variation=0.1)

    def play_equip(self):
        """Play equipment sound"""
        self.play_sound('equip', volume=0.6, pitch_variation=0.15)

    def play_stairs(self):
        """Play stairs descending sound"""
        self.play_sound('stairs', volume=0.8)

    def play_levelup(self):
        """Play level up fanfare"""
        self.play_sound('levelup', volume=1.0)

    def play_gameover(self):
        """Play game over sound"""
        self.play_sound('gameover', volume=0.9)

    def play_ui_select(self):
        """Play UI selection sound"""
        self.play_sound('ui_select', volume=0.5)

    def play_ui_hover(self):
        """Play UI hover sound (softer than select)"""
        self.play_sound('ui_hover', volume=0.3)

    def play_letter_whoosh(self):
        """Play letter flying whoosh sound"""
        self.play_sound('letter_whoosh', volume=0.4, pitch_variation=0.2)

    def play_letter_impact(self):
        """Play letter landing impact sound"""
        self.play_sound('letter_impact', volume=0.6, pitch_variation=0.15)

    # === VOICE SYNTHESIS ===

    def play_voice(self, text: str, volume: float = 1.0):
        """
        Play robot voice line (non-blocking, uses threading)

        Args:
            text: Text to speak
            volume: Volume multiplier (0.0 to 1.0)
        """
        if not self.enabled or not self.voice_synth.enabled:
            return

        def _generate_and_play():
            """Generate voice in background thread and play when ready"""
            sound = self.voice_synth.generate_voice(text)
            if sound:
                sound.set_volume(volume * self.voice_volume)
                sound.play()

        # Run voice generation in background thread to avoid blocking UI
        thread = threading.Thread(target=_generate_and_play, daemon=True)
        thread.start()

    def play_voice_welcome(self):
        """Play welcome voice line"""
        self.play_voice("Welcome")

    def play_voice_levelup(self):
        """Play level up voice line"""
        self.play_voice("Level up")

    def play_voice_gameover(self):
        """Play game over voice line"""
        self.play_voice("Game over")

    def play_voice_critical(self):
        """Play critical hit voice line"""
        self.play_voice("Critical", volume=1.2)

    def play_voice_legendary(self):
        """Play legendary item voice line"""
        self.play_voice("Legendary", volume=1.3)

    def play_voice_epic(self):
        """Play epic item voice line"""
        self.play_voice("Epic", volume=1.1)

    def play_voice_rare(self):
        """Play rare item voice line"""
        self.play_voice("Rare item")

    def play_voice_dragon_defeated(self):
        """Play dragon defeated voice line"""
        self.play_voice("Dragon defeated", volume=1.2)

    def play_voice_descending(self):
        """Play descending stairs voice line"""
        self.play_voice("Descending")

    def play_voice_class(self, class_name: str):
        """Play class name voice line"""
        self.play_voice(class_name, volume=1.1)

    def play_voice_taunt(self):
        """Play random menacing taunt"""
        import constants as c
        taunt = random.choice(c.VOICE_TAUNTS)
        print(f"🔊 Playing taunt: '{taunt}'")
        if not self.enabled:
            print("⚠ Audio disabled - taunt not played")
        elif not self.voice_synth.enabled:
            print("⚠ Voice synthesis disabled - taunt not played")
        self.play_voice(taunt, volume=0.9)

    def start_background_music(self):
        """Start playing background music"""
        if not self.enabled:
            return

        # Generate and play ambient music
        self.music_track = self._generate_ambient_music()
        self.music_track.set_volume(self.music_volume * self.music_ducking)
        self.music_track.play(loops=-1)  # Loop forever

    def update_music_intensity(self, enemies_nearby: int, in_combat: bool):
        """Update music based on game state"""
        self.enemies_nearby = enemies_nearby
        self.in_combat = in_combat

        # Calculate target intensity
        if in_combat:
            target_intensity = 1.0
        elif enemies_nearby > 0:
            target_intensity = 0.5 + (min(enemies_nearby, 5) / 10)
        else:
            target_intensity = 0.0

        # Smooth transition
        self.current_music_intensity += (target_intensity - self.current_music_intensity) * 0.1

        # Update ducking (lower music during combat)
        target_ducking = 0.4 if in_combat else 1.0
        self.music_ducking += (target_ducking - self.music_ducking) * 0.05

        # Apply to music
        if self.music_track:
            self.music_track.set_volume(self.music_volume * self.music_ducking)

    def stop_music(self):
        """Stop background music"""
        if self.music_track:
            self.music_track.stop()

    def set_enabled(self, enabled: bool):
        """Enable/disable all audio"""
        self.enabled = enabled
        if not enabled:
            self.stop_music()
            pygame.mixer.stop()

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_track:
            self.music_track.set_volume(self.music_volume * self.music_ducking)

    def shutdown(self):
        """Shutdown audio manager and cleanup all resources"""
        print("🔊 Shutting down audio manager...")

        # Stop all sounds
        pygame.mixer.stop()

        # Stop music
        self.stop_music()

        # Shutdown voice synthesizer
        self.voice_synth.shutdown()

        # Quit pygame mixer
        try:
            pygame.mixer.quit()
        except:
            pass

        print("✓ Audio manager shutdown complete")


# Global audio manager instance
_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Get or create global audio manager instance"""
    global _audio_manager
    if _audio_manager is None:
        try:
            _audio_manager = AudioManager()
        except Exception as e:
            print(f"Warning: Failed to initialize audio: {e}")
            # Create a dummy audio manager that does nothing
            class DummyAudioManager:
                def __getattr__(self, name):
                    return lambda *args, **kwargs: None
            _audio_manager = DummyAudioManager()
    return _audio_manager
