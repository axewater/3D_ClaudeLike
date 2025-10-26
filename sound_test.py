#!/usr/bin/env python3
"""
Sound Test Tool for Claude-Like Roguelike
Lists all game sounds and allows you to play them for testing
"""
import sys
import time
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

    # Organize sounds by category
    categories = {
        'Combat': [],
        'Enemy Deaths': [],
        'Abilities': [],
        'Movement': [],
        'Items': [],
        'UI': [],
        'Other': []
    }

    for sound in sounds:
        if 'attack' in sound or 'hit' in sound or 'crit' in sound:
            categories['Combat'].append(sound)
        elif 'enemy_death' in sound:
            categories['Enemy Deaths'].append(sound)
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
    if sound_name in audio_manager.sounds:
        print(f"\n▶ Playing: {sound_name}")
        audio_manager.play_sound(sound_name)
        return True
    else:
        print(f"\n✗ Sound '{sound_name}' not found!")
        return False

def main():
    """Main sound test loop"""
    print_header()
    print("Initializing audio system...")

    # Initialize audio manager
    audio_manager = get_audio_manager()

    print(f"✓ Loaded {len(audio_manager.sounds)} sounds\n")

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
