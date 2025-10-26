#!/usr/bin/env python3
"""
Claude-Like - A 3D roguelike game
Entry point for 3D mode using Ursina Engine
"""
import sys
import argparse


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Claude-Like Roguelike - A 3D dungeon crawler'
    )
    parser.add_argument(
        '--skip-intro',
        action='store_true',
        help='Skip the animated intro screen for faster startup'
    )
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error'],
        default=None,
        help='Set logging verbosity (default: info). debug=all logs, info=important events, warning=issues only, error=errors only'
    )
    parser.add_argument(
        '--log-filter',
        default=None,
        help='Filter logs by module name (comma-separated list, e.g., "game,renderer3d")'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Quiet mode - only show errors (equivalent to --log-level error)'
    )
    parser.add_argument(
        '--regenerate-textures',
        action='store_true',
        help='Force regeneration of cached biome textures (slower startup)'
    )
    parser.add_argument(
        '--regenerate-ability-icons',
        action='store_true',
        help='Force regeneration of cached ability icon animations (slower startup)'
    )
    parser.add_argument(
        '--regenerate-voices',
        action='store_true',
        help='Force regeneration of cached TTS voice files (requires pyttsx3)'
    )
    parser.add_argument(
        '--reset-settings',
        action='store_true',
        help='Reset all settings to defaults (deletes game_settings.json) - use if display/audio settings cause problems'
    )
    parser.add_argument(
        '--windowed',
        action='store_true',
        help='Force windowed mode for this session (temporary override, does not modify saved settings)'
    )
    parser.add_argument(
        '--safe-mode',
        action='store_true',
        help='Safe mode: reset settings AND force windowed mode (use if game won\'t start)'
    )
    return parser.parse_args()


def show_3d_title_screen():
    """Show PyQt6 OpenGL title screen before launching Ursina"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from ui.screens.title_screen_3d import TitleScreen3D
    from logger import get_logger

    log = get_logger()
    log.info("Opening Title Screen")

    # Create PyQt6 app
    app = QApplication(sys.argv)

    # Create and show title screen
    title_screen = TitleScreen3D()
    title_screen.setWindowTitle("Claude-Like")

    # Set FIXED size to 1920x1080 (non-resizable)
    title_screen.setFixedSize(1920, 1080)

    # Remove window decorations for exact pixel dimensions and immersive feel
    title_screen.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    # Center window on primary screen
    screen_geometry = app.primaryScreen().geometry()
    screen_center = screen_geometry.center()
    window_rect = title_screen.frameGeometry()
    window_rect.moveCenter(screen_center)
    title_screen.move(window_rect.topLeft())

    log.debug("Title screen set to 1920x1080, centered on display", "title_screen")

    # Connect the continue signal to close the window
    title_screen.continue_pressed.connect(title_screen.close)

    title_screen.show()

    # Wait for user to press key (blocks until title screen closes)
    app.exec()

    # Cleanup
    title_screen.close()
    del title_screen
    del app

    log.info("Title screen closed, preparing to launch game")


def main():
    """Main entry point for 3D mode"""
    import os
    args = parse_args()

    # Handle --safe-mode (combines reset-settings + windowed)
    if args.safe_mode:
        args.reset_settings = True
        args.windowed = True
        print("[Safe Mode] Resetting settings and forcing windowed mode...")

    # Handle --reset-settings FIRST (before any settings are loaded)
    if args.reset_settings:
        from settings import reset_settings
        reset_settings()
        print("[Settings] Settings have been reset to defaults")

    # Set texture regeneration flag via environment variable
    # (checked by graphics3d/tiles.py during import)
    if args.regenerate_textures:
        os.environ['REGENERATE_TEXTURES'] = '1'

    # Set ability icon regeneration flag via environment variable
    # (checked by ui3d/helmet_hud.py during import)
    if args.regenerate_ability_icons:
        os.environ['REGENERATE_ABILITY_ICONS'] = '1'

    # Handle voice cache regeneration
    if args.regenerate_voices:
        import shutil
        from pathlib import Path
        voice_cache_path = Path("ursina_cache/voices")
        if voice_cache_path.exists():
            print(f"Deleting voice cache: {voice_cache_path}")
            shutil.rmtree(voice_cache_path)
            print("Voice cache deleted. Will regenerate on startup...")

    # Initialize logger FIRST (before any other imports that might log)
    from logger import init_logger, parse_log_level, LogLevel
    import constants as c

    # Determine log level
    if args.quiet:
        log_level = LogLevel.ERROR
    elif args.log_level:
        log_level = parse_log_level(args.log_level)
    else:
        # Use default from constants
        log_level = parse_log_level(c.DEFAULT_LOG_LEVEL)

    # Parse module filter (if provided)
    module_filter = None
    if args.log_filter:
        module_filter = set(m.strip() for m in args.log_filter.split(','))

    # Initialize global logger
    init_logger(log_level, module_filter)

    from logger import get_logger
    log = get_logger()

    log.info("=== Claude-Like (3D Mode) ===")

    # Show OpenGL title screen first (unless skipped)
    if not args.skip_intro:
        show_3d_title_screen()
    else:
        log.info("Skipping intro screen (--skip-intro flag set)")

    # Now launch Ursina game
    log.info("Launching Ursina 3D renderer...")
    from main_3d import main_3d as run_3d_game
    run_3d_game(force_windowed=args.windowed)


if __name__ == "__main__":
    main()
