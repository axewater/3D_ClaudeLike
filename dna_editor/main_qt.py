"""
DNA Editor - PyQt6 Version

Interactive 3D editor for creating tentacle creatures using mathematical curves.

Usage:
    cd dna_editor
    python3 main_qt.py

Features:
- PyQt6 controls with precise layout
- Real-time 3D preview (Ursina in separate window)
- Undo/Redo system (50 steps)
- Export DNA to JSON
- Preset configurations
"""

import sys
import os

# Add current directory to path so package imports work
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import using package name
from dna_editor.qt_ui import EditorWindow


def main():
    """Main entry point."""
    print("DNA Editor - Starting...")

    # Suppress Qt warnings about unknown CSS properties
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

    # Create Qt application
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create main window
    window = EditorWindow()
    window.show()

    print("✓ Ready - Use control panel to adjust creature parameters")

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
