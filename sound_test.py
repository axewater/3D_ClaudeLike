#!/usr/bin/env python3
"""
Sound Test Tool for Claude-Like Roguelike
Lists all game sounds and allows you to play them for testing
"""
import sys
import time
import argparse
import shutil
from pathlib import Path
from audio import AudioManager, get_audio_manager

def print_header():
    """Print tool header"""
    print("=" * 60)
    print("  SOUND TEST TOOL - Claude-Like Roguelike")
    print("=" * 60)
    print()

def list_sounds(audio_manager):
    """Display all available sounds organized by category"""
    sounds = sorted(audio_manager.sounds.keys())

    # Also get TTS voices (death screams)
    voices = sorted(audio_manager.voices.keys())

    # Organize sounds by category
    categories = {
        'Combat': [],
        'Enemy Deaths (TTS)': [],
        'Abilities': [],
        'Movement': [],
        'Items': [],
        'UI': [],
        'Voice Lines': [],
        'Other': []
    }

    # Categorize procedural sounds
    for sound in sounds:
        if 'attack' in sound or 'hit' in sound or 'crit' in sound:
            categories['Combat'].append(sound)
        elif 'enemy_death' in sound:
            categories['Enemy Deaths (TTS)'].append(sound)
        elif 'ability' in sound:
            categories['Abilities'].append(sound)
        elif 'footstep' in sound or 'stairs' in sound:
            categories['Movement'].append(sound)
        elif 'item' in sound or 'potion' in sound or 'equip' in sound or 'coin' in sound:
            categories['Items'].append(sound)
        elif 'ui_' in sound or 'levelup' in sound or 'gameover' in sound or 'letter' in sound:
            categories['UI'].append(sound)
        else:
            categories['Other'].append(sound)

    # Categorize TTS voices
    for voice in voices:
        if 'death_scream' in voice:
            categories['Enemy Deaths (TTS)'].append(voice)
        else:
            categories['Voice Lines'].append(voice)

    # Print categorized sounds
    index = 1
    sound_index_map = {}

    for category, sound_list in categories.items():
        if sound_list:
            print(f"\n{category}:")
            print("-" * 40)
            for sound in sound_list:
                print(f"  [{index:2d}] {sound}")
                sound_index_map[index] = sound
                index += 1

    print("\n" + "=" * 60)
    return sound_index_map

def play_sound(audio_manager, sound_name):
    """Play a sound by name"""
    # Check if this is a TTS death scream
    if 'death_scream_' in sound_name:
        enemy_type = sound_name.replace('death_scream_', '')
        print(f"\n▶ Playing TTS death scream for: {enemy_type}")
        audio_manager.play_enemy_death(enemy_type)
        return True
    # Check if it's a TTS voice
    elif sound_name in audio_manager.voices:
        print(f"\n▶ Playing TTS voice: {sound_name}")
        voice = audio_manager.voices[sound_name]
        voice.set_volume(audio_manager.sfx_volume)
        voice.play()
        return True
    # Check if it's a procedural sound
    elif sound_name in audio_manager.sounds:
        print(f"\n▶ Playing procedural sound: {sound_name}")
        audio_manager.play_sound(sound_name)
        return True
    else:
        print(f"\n✗ Sound '{sound_name}' not found!")
        return False

def main():
    """Main sound test loop"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sound Test Tool - Test game audio effects')
    parser.add_argument(
        '--regenerate-voices',
        action='store_true',
        help='Force regeneration of cached TTS voice files (requires pyttsx3)'
    )
    args = parser.parse_args()

    # Handle voice cache regeneration
    if args.regenerate_voices:
        voice_cache_path = Path("ursina_cache/voices")
        if voice_cache_path.exists():
            print(f"Deleting voice cache: {voice_cache_path}")
            shutil.rmtree(voice_cache_path)
            print("Voice cache deleted. Will regenerate on startup...\n")
        else:
            print("Voice cache not found (already deleted or never created)\n")

    print_header()
    print("Initializing audio system...")

    # Initialize audio manager
    audio_manager = get_audio_manager()

    print(f"✓ Loaded {len(audio_manager.sounds)} procedural sounds")
    print(f"✓ Loaded {len(audio_manager.voices)} TTS voices\n")

    # Display all sounds
    sound_index_map = list_sounds(audio_manager)

    print("\nCommands:")
    print("  - Enter a number (1-{}) to play a sound".format(len(sound_index_map)))
    print("  - Enter a sound name to play it")
    print("  - Type 'list' or 'l' to show sounds again")
    print("  - Type 'quit' or 'q' to exit")
    print("=" * 60)

    # Main loop
    while True:
        try:
            user_input = input("\n> ").strip().lower()

            if not user_input:
                continue

            # Check for quit commands
            if user_input in ['quit', 'q', 'exit']:
                print("\nGoodbye!")
                break

            # Check for list command
            if user_input in ['list', 'l']:
                sound_index_map = list_sounds(audio_manager)
                continue

            # Try to parse as number
            try:
                sound_num = int(user_input)
                if sound_num in sound_index_map:
                    play_sound(audio_manager, sound_index_map[sound_num])
                else:
                    print(f"✗ Invalid number. Choose 1-{len(sound_index_map)}")
            except ValueError:
                # Not a number, try as sound name
                play_sound(audio_manager, user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == '__main__':
    main()
