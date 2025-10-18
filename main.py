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
    return parser.parse_args()


def show_3d_title_screen():
    """Show PyQt6 OpenGL title screen before launching Ursina"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from ui.screens.title_screen_3d import TitleScreen3D

    print("=== Opening Title Screen ===")

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

    print(f"✓ Title screen set to 1920x1080, centered on display")

    # Connect the continue signal to close the window
    title_screen.continue_pressed.connect(title_screen.close)

    title_screen.show()

    # Wait for user to press key (blocks until title screen closes)
    app.exec()

    # Cleanup
    title_screen.close()
    del title_screen
    del app

    print("✓ Title screen closed, preparing to launch game...")


def main():
    """Main entry point for 3D mode"""
    args = parse_args()

    print("=== Claude-Like (3D Mode) ===")

    # Show OpenGL title screen first (unless skipped)
    if not args.skip_intro:
        show_3d_title_screen()
    else:
        print("⏩ Skipping intro screen (--skip-intro flag set)")

    # Now launch Ursina game
    print("Launching Ursina 3D renderer...")
    from main_3d import main_3d as run_3d_game
    run_3d_game()


if __name__ == "__main__":
    main()
