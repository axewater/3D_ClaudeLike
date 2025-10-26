"""
Audio system for Claude-Like
Handles all sound effects and background music with procedural sound generation
"""
import pygame
import numpy as np
import random
from typing import Dict, Optional
from logger import get_logger
import voice_cache

log = get_logger()


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

        # Sound cache
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        # Voice cache (TTS voice lines)
        self.voices: Dict[str, pygame.mixer.Sound] = {}

        # Music state
        self.current_music_intensity = 0.0  # 0.0 = calm, 1.0 = combat
        self.music_ducking = 1.0  # Multiplier for music volume
        self.music_track = None

        # Combat state for adaptive audio
        self.enemies_nearby = 0
        self.in_combat = False

        # Generate all sounds
        self._generate_sounds()

        # Load voice cache
        self._load_voices()

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

        # Startle death - high pitched squeal with harmonics (FIX: was 'goblin')
        startle_death = synth.combine_waves(
            synth.generate_sweep(900, 350, 0.28, 0.55),      # Main squeal
            synth.generate_sweep(1800, 700, 0.28, 0.25),     # Harmonic overtone
            synth.generate_square_wave(450, 0.15, 0.15),     # Distortion edge
            synth.generate_noise(0.12, 0.2)                  # Death rattle
        )
        self.sounds['enemy_death_startle'] = synth.array_to_sound(startle_death)

        # Slime death - wet bubbling splat with gooey texture
        slime_death = synth.combine_waves(
            synth.generate_sweep(320, 80, 0.35, 0.52),       # Main wet splat
            synth.generate_sweep(180, 60, 0.25, 0.38),       # Low gooey spread
            synth.generate_sine_wave(95, 0.18, 0.28),        # Bubble pop bass
            synth.generate_sine_wave(140, 0.15, 0.22),       # Secondary bubble
            synth.generate_noise(0.2, 0.36)                  # Liquid splatter texture
        )
        self.sounds['enemy_death_slime'] = synth.array_to_sound(slime_death)

        # Skeleton death - bone clatter and collapse with rattling
        skeleton_death = synth.combine_waves(
            synth.generate_noise(0.08, 0.42),                # Initial impact
            synth.generate_noise(0.15, 0.35),                # Bone scatter
            synth.generate_sweep(280, 120, 0.22, 0.32),      # Descending fall
            synth.generate_square_wave(180, 0.12, 0.18),     # Hollow bone tone
            synth.generate_sine_wave(90, 0.25, 0.25)         # Final settle thud
        )
        self.sounds['enemy_death_skeleton'] = synth.array_to_sound(skeleton_death)

        # Orc death - deep guttural roar with bass rumble (displays as "Tentacle")
        orc_death = synth.combine_waves(
            synth.generate_sweep(180, 45, 0.45, 0.62),       # Deep roar
            synth.generate_sweep(90, 35, 0.42, 0.48),        # Sub-bass rumble
            synth.generate_sine_wave(60, 0.35, 0.38),        # Guttural bass
            synth.generate_square_wave(120, 0.25, 0.22),     # Growl texture
            synth.generate_noise(0.35, 0.32)                 # Death rattle
        )
        self.sounds['enemy_death_orc'] = synth.array_to_sound(orc_death)

        # Demon death - demonic multi-layered screech (displays as "Medusa")
        demon_death = synth.combine_waves(
            synth.generate_sweep(850, 180, 0.38, 0.52),      # High screech
            synth.generate_sweep(420, 90, 0.38, 0.46),       # Mid demon wail
            synth.generate_sweep(210, 75, 0.40, 0.42),       # Low demonic rumble
            synth.generate_square_wave(350, 0.28, 0.28),     # Harsh distortion
            synth.generate_square_wave(175, 0.28, 0.22),     # Lower distortion layer
            synth.generate_noise(0.25, 0.32)                 # Chaotic texture
        )
        self.sounds['enemy_death_demon'] = synth.array_to_sound(demon_death)

        # Dragon death - epic multi-harmonic roar with sub-bass
        dragon_death = synth.combine_waves(
            synth.generate_sweep(220, 40, 0.65, 0.64),       # Main roar
            synth.generate_sweep(110, 30, 0.60, 0.52),       # Harmonic roar
            synth.generate_sine_wave(48, 0.55, 0.48),        # Deep sub-bass rumble
            synth.generate_sine_wave(72, 0.50, 0.40),        # Mid bass power
            synth.generate_square_wave(95, 0.35, 0.28),      # Draconic growl texture
            synth.generate_noise(0.55, 0.34)                 # Epic death rattle
        )
        self.sounds['enemy_death_dragon'] = synth.array_to_sound(dragon_death)

        # === ABILITY SOUNDS ===

        # Fireball - powerful fire blast with charge and explosion
        fireball = synth.combine_waves(
            synth.generate_sweep(450, 180, 0.32, 0.22),      # Fire whoosh
            synth.generate_sweep(850, 350, 0.22, 0.15),      # High sizzle
            synth.generate_sine_wave(95, 0.28, 0.17),        # Explosive bass
            synth.generate_square_wave(240, 0.18, 0.11),     # Crackling fire texture
            synth.generate_noise(0.18, 0.14)                 # Explosion burst
        )
        self.sounds['ability_fireball'] = synth.array_to_sound(fireball)

        # Dash - magical teleport blink with reality warp
        dash = synth.combine_waves(
            synth.generate_sweep(1100, 2200, 0.16, 0.18),    # Upward blink
            synth.generate_sweep(2200, 1100, 0.16, 0.15),    # Shimmer return
            synth.generate_sine_wave(1650, 0.14, 0.13),      # Magic shimmer hold
            synth.generate_sine_wave(880, 0.12, 0.11),       # Lower harmonic
            synth.generate_sine_wave(110, 0.10, 0.14)        # Reality pop bass
        )
        self.sounds['ability_dash'] = synth.array_to_sound(dash)

        # Healing Touch - warm magical chimes with sparkle
        heal = synth.combine_waves(
            synth.generate_sine_wave(523, 0.35, 0.15),       # C - main note
            synth.generate_sine_wave(659, 0.35, 0.13),       # E - harmony
            synth.generate_sine_wave(784, 0.35, 0.12),       # G - chord
            synth.generate_sine_wave(1046, 0.25, 0.09),      # High C - sparkle
            synth.generate_sine_wave(1318, 0.20, 0.07),      # E - shimmer
            synth.generate_sine_wave(220, 0.30, 0.10)        # Bass warmth
        )
        self.sounds['ability_heal'] = synth.array_to_sound(heal)

        # Frost Nova - crystalline ice burst with shattering
        frost = synth.combine_waves(
            synth.generate_sine_wave(1320, 0.32, 0.14),      # Crystal formation high
            synth.generate_sine_wave(1680, 0.32, 0.11),      # Ice harmonic
            synth.generate_sine_wave(2100, 0.25, 0.09),      # Crystalline sparkle
            synth.generate_sweep(1800, 900, 0.20, 0.13),     # Shattering sweep
            synth.generate_square_wave(1400, 0.15, 0.07),    # Sharp ice edges
            synth.generate_noise(0.12, 0.08)                 # Ice cracking texture
        )
        self.sounds['ability_frost'] = synth.array_to_sound(frost)

        # Whirlwind - spinning cyclone with metallic blade sounds
        whirlwind = synth.combine_waves(
            synth.generate_sweep(320, 680, 0.42, 0.20),      # Rising cyclone
            synth.generate_sweep(680, 320, 0.42, 0.18),      # Falling cyclone
            synth.generate_square_wave(420, 0.35, 0.12),     # Metallic blade whoosh
            synth.generate_square_wave(210, 0.35, 0.11),     # Lower blade harmonic
            synth.generate_sine_wave(85, 0.38, 0.14),        # Wind bass
            synth.generate_noise(0.28, 0.12)                 # Air turbulence
        )
        self.sounds['ability_whirlwind'] = synth.array_to_sound(whirlwind)

        # Shadow Step - dark sinister teleport with void energy
        shadow = synth.combine_waves(
            synth.generate_sweep(420, 85, 0.28, 0.20),       # Descending darkness
            synth.generate_sweep(210, 55, 0.30, 0.18),       # Deep void pull
            synth.generate_sine_wave(65, 0.26, 0.16),        # Sinister bass rumble
            synth.generate_square_wave(180, 0.20, 0.11),     # Dark energy distortion
            synth.generate_sine_wave(1400, 0.12, 0.09),      # Ethereal whisper
            synth.generate_noise(0.15, 0.10)                 # Shadow texture
        )
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

        # Rare item pickup - triumphant ascending trumpet (ta-ta-ta-daaa!)
        # Create ascending magical notes
        rare_note1 = synth.combine_waves(
            synth.generate_sine_wave(659, 0.12, 0.28),       # E
            synth.generate_sine_wave(1318, 0.12, 0.16)       # High E shimmer
        )
        rare_note2 = synth.combine_waves(
            synth.generate_sine_wave(784, 0.12, 0.30),       # G
            synth.generate_sine_wave(1568, 0.12, 0.18)       # High G shimmer
        )
        rare_note3 = synth.combine_waves(
            synth.generate_sine_wave(988, 0.12, 0.32),       # B
            synth.generate_sine_wave(1976, 0.12, 0.20)       # High B shimmer
        )
        # Final "daaa!" - fuller, warmer chord without piercing chirp
        rare_note4 = synth.combine_waves(
            synth.generate_sine_wave(1319, 0.25, 0.38),      # High E finale (main)
            synth.generate_sine_wave(988, 0.25, 0.30),       # B - chord fullness
            synth.generate_sine_wave(659, 0.25, 0.28),       # E - bass warmth
            synth.generate_sine_wave(1976, 0.20, 0.20),      # Gentle shimmer (no chirp!)
            synth.generate_sine_wave(330, 0.22, 0.25)        # Low E - triumphant bass
        )
        # Create ascending arpeggio sequence
        tiny_gap = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * 0.03))
        pickup_rare = np.concatenate([rare_note1, tiny_gap, rare_note2, tiny_gap,
                                      rare_note3, tiny_gap, rare_note4])
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

        # Stairs descend - sequential heavy footsteps with rhythm and structure
        # Create individual footstep sounds (descending in pitch as you go down)

        # Step 1 - First heavy footfall
        step1 = synth.combine_waves(
            synth.generate_sine_wave(95, 0.18, 0.32),        # Bass thud
            synth.generate_sweep(280, 140, 0.14, 0.20),      # Stone impact sweep
            synth.generate_noise(0.08, 0.12)                 # Brief stone texture
        )

        # Step 2 - Second footfall (slightly lower/deeper)
        step2 = synth.combine_waves(
            synth.generate_sine_wave(85, 0.18, 0.34),        # Deeper bass thud
            synth.generate_sweep(250, 125, 0.14, 0.20),      # Lower stone impact
            synth.generate_noise(0.08, 0.12)                 # Stone texture
        )

        # Step 3 - Third footfall (even lower)
        step3 = synth.combine_waves(
            synth.generate_sine_wave(75, 0.18, 0.36),        # Even deeper bass
            synth.generate_sweep(220, 110, 0.14, 0.20),      # Lower impact
            synth.generate_noise(0.08, 0.12)                 # Stone texture
        )

        # Final echo/reverb tail - settling into the depths
        echo_tail = synth.combine_waves(
            synth.generate_sweep(320, 140, 0.35, 0.18),      # Descending echo
            synth.generate_sine_wave(60, 0.30, 0.22)         # Deep dungeon rumble
        )

        # Combine with rhythm: step - gap - step - gap - step - gap - echo
        step_gap = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * 0.10))  # 0.1s gap between steps
        stairs = np.concatenate([step1, step_gap, step2, step_gap, step3, step_gap, echo_tail])
        self.sounds['stairs'] = synth.array_to_sound(stairs)

        # Coin pickup - classic "bling-bling" two-note ascending pickup sound
        coin_note1 = synth.generate_sine_wave(988, 0.08, 0.35)   # B - first bright note
        coin_note2 = synth.generate_sine_wave(1319, 0.12, 0.30)  # E - second higher note with sustain
        coin = np.concatenate([coin_note1, coin_note2])
        self.sounds['coin'] = synth.array_to_sound(coin)

        # === UI SOUNDS ===

        # Level up - triumphant ascending fanfare with sparkle
        # Create ascending arpeggio notes
        note1 = synth.combine_waves(
            synth.generate_sine_wave(523, 0.15, 0.35),   # C
            synth.generate_sine_wave(1046, 0.15, 0.18)   # High C harmonic
        )
        note2 = synth.combine_waves(
            synth.generate_sine_wave(659, 0.15, 0.35),   # E
            synth.generate_sine_wave(1318, 0.15, 0.18)   # High E harmonic
        )
        note3 = synth.combine_waves(
            synth.generate_sine_wave(784, 0.15, 0.38),   # G
            synth.generate_sine_wave(1568, 0.15, 0.20)   # High G harmonic
        )
        # Final triumphant chord with sparkle (volumes reduced to prevent clipping)
        final_chord = synth.combine_waves(
            synth.generate_sine_wave(1047, 0.45, 0.18),  # High C - victory!
            synth.generate_sine_wave(1319, 0.45, 0.14),  # High E
            synth.generate_sine_wave(1568, 0.45, 0.12),  # High G
            synth.generate_sine_wave(2093, 0.35, 0.10),  # Super high C - sparkle
            synth.generate_sine_wave(262, 0.40, 0.12)    # Bass C - power
        )
        # Apply gentle fade-out to the final chord to prevent harsh ending
        fade_out_length = int(len(final_chord) * 0.5)  # Fade out last 50% of chord
        fade_envelope = np.ones(len(final_chord))
        fade_envelope[-fade_out_length:] = np.linspace(1, 0, fade_out_length)
        final_chord = final_chord * fade_envelope

        # Combine into ascending sequence
        silence_gap = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * 0.05))
        levelup = np.concatenate([note1, silence_gap, note2, silence_gap, note3, silence_gap, final_chord])
        self.sounds['levelup'] = synth.array_to_sound(levelup)

        # Game over - Beethoven's 5th Symphony opening motif: "da-da-da-DUMMM" (Fate knocking!)
        # The iconic G-G-G-E♭ pattern (short-short-short-LONG)

        # Three short G notes (392 Hz) - "da-da-da"
        beethoven_g1 = synth.combine_waves(
            synth.generate_sine_wave(392, 0.15, 0.20),     # G4 - main note
            synth.generate_sine_wave(784, 0.15, 0.08),     # G5 - octave harmonic
            synth.generate_sine_wave(196, 0.15, 0.10)      # G3 - bass power
        )
        beethoven_g2 = synth.combine_waves(
            synth.generate_sine_wave(392, 0.15, 0.20),
            synth.generate_sine_wave(784, 0.15, 0.08),
            synth.generate_sine_wave(196, 0.15, 0.10)
        )
        beethoven_g3 = synth.combine_waves(
            synth.generate_sine_wave(392, 0.15, 0.20),
            synth.generate_sine_wave(784, 0.15, 0.08),
            synth.generate_sine_wave(196, 0.15, 0.10)
        )

        # One long E♭ note (311 Hz) - "DUMMM" (fate's answer)
        beethoven_eb = synth.combine_waves(
            synth.generate_sine_wave(311, 0.60, 0.22),     # E♭4 - main dramatic note
            synth.generate_sine_wave(622, 0.60, 0.10),     # E♭5 - octave harmonic
            synth.generate_sine_wave(155, 0.60, 0.12)      # E♭3 - deep ominous bass
        )

        # Combine with proper rhythm: short gap between quick notes, longer gap before the finale
        short_gap = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * 0.05))   # 50ms between "da"s
        dramatic_pause = np.zeros(int(SoundSynthesizer.SAMPLE_RATE * 0.08))  # Slight pause before "DUMMM"

        gameover = np.concatenate([
            beethoven_g1, short_gap,
            beethoven_g2, short_gap,
            beethoven_g3, dramatic_pause,
            beethoven_eb
        ])

        self.sounds['gameover'] = synth.array_to_sound(gameover)

        # Menu select - friendly "boop-BEEP!" confirmation
        select_note1 = synth.generate_sine_wave(659, 0.06, 0.20)   # E - friendly boop
        select_note2 = synth.generate_sine_wave(880, 0.10, 0.25)   # A - happy beep!
        select = np.concatenate([select_note1, select_note2])
        self.sounds['ui_select'] = synth.array_to_sound(select)

        # Menu hover - dark thump similar to stairs
        hover = synth.combine_waves(
            synth.generate_sine_wave(80, 0.12, 0.15),    # Deep bass thud
            synth.generate_sweep(240, 120, 0.10, 0.08),  # Stone impact
            synth.generate_noise(0.05, 0.05)             # Stone texture
        )
        self.sounds['ui_hover'] = synth.array_to_sound(hover)

        # === TITLE SCREEN EFFECTS ===

        # Letter whoosh - air displacement getting closer (soft to loud)
        # Create base whoosh components with safe volumes (stretched out, quieter)
        air_sweep = synth.generate_sweep(400, 150, 0.8, 0.11)     # Air cutting through
        wind_noise = synth.generate_noise(0.8, 0.07)              # Wind texture
        bass_rumble = synth.generate_sine_wave(55, 0.8, 0.09)     # Approaching mass

        # Combine waves
        whoosh = synth.combine_waves(air_sweep, wind_noise, bass_rumble)

        # Apply crescendo envelope (soft to loud, simulating approach)
        crescendo = np.linspace(0.15, 1.0, len(whoosh))  # Start at 15%, build to 100%
        whoosh = whoosh * crescendo

        self.sounds['letter_whoosh'] = synth.array_to_sound(whoosh)

        # Letter impact - deep stone brick thump
        impact = synth.combine_waves(
            synth.generate_sine_wave(45, 0.12, 0.45),      # Sub-bass rumble
            synth.generate_sine_wave(65, 0.12, 0.4),       # Low thump
            synth.generate_sweep(80, 35, 0.10, 0.35),      # Settling sweep
            synth.generate_noise(0.08, 0.3)                # Impact texture
        )
        self.sounds['letter_impact'] = synth.array_to_sound(impact)

    def _load_voices(self):
        """Load voice lines from cache (generates if needed)"""
        try:
            self.voices = voice_cache.ensure_voice_cache()
        except Exception as e:
            print(f"⚠ Failed to load voice cache: {e}")
            self.voices = {}

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
        """
        Play enemy death sound - tries voice-based scream first, falls back to procedural.

        Args:
            enemy_type: Type of enemy (startle, slime, skeleton, orc, demon, dragon)
            position: World position of enemy (x, y)
            player_position: Player position for positional audio (x, y)
        """
        # Try voice-based death scream first
        scream_key = f'death_scream_{enemy_type}'
        if scream_key in self.voices:
            # Calculate volume based on distance (positional audio)
            final_volume = 0.9 * self.sfx_volume
            if position and player_position:
                distance = abs(position[0] - player_position[0]) + abs(position[1] - player_position[1])
                # Volume falls off with distance (max range 10 tiles)
                distance_factor = max(0, 1.0 - (distance / 10.0))
                final_volume *= distance_factor

            # Play voice-based scream
            voice = self.voices[scream_key]
            voice.set_volume(final_volume)
            voice.play()
        else:
            # Fallback to procedural death sound
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
        """Play letter flying whoosh sound. Returns channel for stopping."""
        if not self.enabled or 'letter_whoosh' not in self.sounds:
            return None

        sound = self.sounds['letter_whoosh']
        sound.set_volume(0.4 * self.sfx_volume)
        channel = sound.play()
        return channel

    def play_letter_impact(self):
        """Play letter landing impact sound"""
        self.play_sound('letter_impact', volume=0.6, pitch_variation=0.15)

    def play_voice(self, voice_key: str, volume: float = 1.0):
        """
        Play a voice line (TTS speech)

        Args:
            voice_key: Key for the voice line (e.g., 'warrior', 'mage', 'rogue', 'ranger')
            volume: Volume multiplier (0.0 to 1.0)
        """
        if not self.enabled or voice_key not in self.voices:
            return

        voice = self.voices[voice_key]
        final_volume = volume * self.sfx_volume

        # Set volume and play
        voice.set_volume(final_volume)
        voice.play()

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
