#!/usr/bin/env python3
"""
TTS Test Tool - Test text-to-speech inputs interactively
Type text and hear it spoken immediately to find good phonetic inputs
"""
import sys
import pygame
import numpy as np
from pathlib import Path
import tempfile

# Try to import pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("ERROR: pyttsx3 not available!")
    print("Install with: pip install pyttsx3")
    sys.exit(1)

# Import voice cache functions for transformations
from voice_cache import load_wav_as_array, pitch_shift_scipy, time_stretch_scipy, apply_fade_out


def init_tts_engine():
    """Initialize TTS engine with good settings"""
    engine = pyttsx3.init()

    # Set volume
    engine.setProperty('volume', 1.0)

    # Try to find a good voice
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
            print(f"Using voice: {male_voice.name}")
        else:
            engine.setProperty('voice', voices[0].id)
            print(f"Using voice: {voices[0].name}")

    return engine


def speak_text(voice_id, text, tts_rate=150, pitch_shift=0, time_stretch=1.0):
    """
    Speak text with TTS and apply transformations

    Args:
        voice_id: Voice ID to use (from engine.getProperty('voices'))
        text: Text to speak
        tts_rate: TTS speech rate (50-300, default 150)
        pitch_shift: Semitones to shift pitch (+12 = octave up, -12 = octave down)
        time_stretch: Time stretch factor (1.0 = normal, 2.0 = twice as long)
    """
    # Generate TTS to temporary file
    temp_file = Path(tempfile.gettempdir()) / "_tts_test_temp.wav"

    try:
        # Create fresh engine for each generation (prevents hangs)
        engine = pyttsx3.init()
        engine.setProperty('rate', tts_rate)
        engine.setProperty('volume', 1.0)
        if voice_id:
            engine.setProperty('voice', voice_id)

        # Save to file
        engine.save_to_file(text, str(temp_file))
        engine.runAndWait()

        # Explicitly stop and delete the engine
        engine.stop()
        del engine

        # Load and transform if needed
        if pitch_shift != 0 or time_stretch != 1.0:
            audio, sample_rate = load_wav_as_array(temp_file)

            if time_stretch != 1.0:
                audio = time_stretch_scipy(audio, time_stretch)

            if pitch_shift != 0:
                audio = pitch_shift_scipy(audio, pitch_shift, sample_rate)

            # Apply fade out
            audio = apply_fade_out(audio, fade_duration=0.3)

            # Save transformed audio
            from voice_cache import save_array_as_wav
            save_array_as_wav(audio, temp_file, sample_rate)

        # Play the sound
        sound = pygame.mixer.Sound(str(temp_file))
        sound.set_volume(1.0)
        sound.play()

        # Wait for sound to finish
        while pygame.mixer.get_busy():
            pygame.time.wait(100)

        # Clean up
        if temp_file.exists():
            temp_file.unlink()

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def print_header():
    """Print tool header"""
    print("=" * 60)
    print("  TTS TEST TOOL - Interactive Text-to-Speech Tester")
    print("=" * 60)
    print()
    print("Type text to hear it spoken by the TTS engine.")
    print("Test different phonetic spellings to find what works best!")
    print()


def print_help():
    """Print help information"""
    print("\nCommands:")
    print("  - Type any text to hear it spoken")
    print("  - /rate <50-300>  - Set TTS speech rate (default: 150)")
    print("  - /pitch <-12 to +12> - Set pitch shift in semitones (default: 0)")
    print("  - /stretch <0.5-2.0> - Set time stretch (default: 1.0)")
    print("  - /reset - Reset all settings to defaults")
    print("  - /help or /h - Show this help")
    print("  - /quit or /q - Exit")
    print()
    print("Current Settings:")
    return {'rate': 150, 'pitch': 0, 'stretch': 1.0}


def main():
    """Main TTS test loop"""
    print_header()

    # Initialize pygame mixer for audio playback
    pygame.mixer.pre_init(22050, -16, 2, 512)
    pygame.mixer.init()

    # Get voice ID to use (initialize engine once just to get voice)
    print("Initializing TTS engine...\n")
    engine = init_tts_engine()
    voice_id = engine.getProperty('voice')
    engine.stop()
    del engine
    print()

    # Settings
    settings = print_help()

    # Main loop
    while True:
        try:
            # Show current settings in prompt
            print(f"[rate:{settings['rate']} pitch:{settings['pitch']:+d} stretch:{settings['stretch']:.1f}]")
            user_input = input("> ").strip()

            if not user_input:
                continue

            # Check for commands
            if user_input.startswith('/'):
                cmd_parts = user_input.lower().split()
                cmd = cmd_parts[0]

                if cmd in ['/quit', '/q', '/exit']:
                    print("\nGoodbye!")
                    break

                elif cmd in ['/help', '/h']:
                    print_help()
                    continue

                elif cmd == '/rate':
                    if len(cmd_parts) < 2:
                        print("Usage: /rate <50-300>")
                    else:
                        try:
                            rate = int(cmd_parts[1])
                            if 50 <= rate <= 300:
                                settings['rate'] = rate
                                print(f"✓ TTS rate set to {rate}")
                            else:
                                print("✗ Rate must be between 50 and 300")
                        except ValueError:
                            print("✗ Invalid rate value")
                    continue

                elif cmd == '/pitch':
                    if len(cmd_parts) < 2:
                        print("Usage: /pitch <-12 to +12>")
                    else:
                        try:
                            pitch = int(cmd_parts[1])
                            if -12 <= pitch <= 12:
                                settings['pitch'] = pitch
                                print(f"✓ Pitch shift set to {pitch:+d} semitones")
                            else:
                                print("✗ Pitch must be between -12 and +12")
                        except ValueError:
                            print("✗ Invalid pitch value")
                    continue

                elif cmd == '/stretch':
                    if len(cmd_parts) < 2:
                        print("Usage: /stretch <0.5-2.0>")
                    else:
                        try:
                            stretch = float(cmd_parts[1])
                            if 0.5 <= stretch <= 2.0:
                                settings['stretch'] = stretch
                                print(f"✓ Time stretch set to {stretch:.1f}x")
                            else:
                                print("✗ Stretch must be between 0.5 and 2.0")
                        except ValueError:
                            print("✗ Invalid stretch value")
                    continue

                elif cmd == '/reset':
                    settings = {'rate': 150, 'pitch': 0, 'stretch': 1.0}
                    print("✓ Settings reset to defaults")
                    continue

                else:
                    print(f"✗ Unknown command: {cmd}")
                    print("Type /help for list of commands")
                    continue

            # Not a command - speak the text
            print(f"▶ Speaking: \"{user_input}\"")
            speak_text(voice_id, user_input,
                      tts_rate=settings['rate'],
                      pitch_shift=settings['pitch'],
                      time_stretch=settings['stretch'])

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
