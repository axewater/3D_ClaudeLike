#!/usr/bin/env python3
"""
Library Manager - Organize creature creations into enemy packs.

This standalone application allows users to:
1. Browse saved creature creations
2. Assign creations to enemy types with level ranges
3. Configure creature-to-enemy mappings
4. Save/load complete enemy packs as JSON files
"""

import sys
from pathlib import Path

# Import library_data using importlib to bypass package __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "library_data",
    Path(__file__).parent / "models" / "library_data.py"
)
library_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library_data)

# Extract classes from the module
Creation = library_data.Creation
EnemyMapping = library_data.EnemyMapping
EnemyPack = library_data.EnemyPack
list_creations = library_data.list_creations

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QMessageBox, QFileDialog, QInputDialog, QScrollArea
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt


class MappingWidget(QWidget):
    """Widget representing a single level range mapping."""

    def __init__(self, enemy_type, available_creations, mapping=None):
        """
        Args:
            enemy_type: Enemy type this mapping belongs to
            available_creations: List of Creation objects
            mapping: Optional existing EnemyMapping to load
        """
        super().__init__()
        self.enemy_type = enemy_type
        self.available_creations = available_creations

        # Create UI
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Level range inputs
        level_label = QLabel("Levels:")
        layout.addWidget(level_label)

        self.start_level_spin = QSpinBox()
        self.start_level_spin.setRange(1, 25)
        self.start_level_spin.setValue(mapping.start_level if mapping else 1)
        self.start_level_spin.setMinimumWidth(60)
        layout.addWidget(self.start_level_spin)

        dash_label = QLabel("-")
        layout.addWidget(dash_label)

        self.end_level_spin = QSpinBox()
        self.end_level_spin.setRange(1, 25)
        self.end_level_spin.setValue(mapping.end_level if mapping else 5)
        self.end_level_spin.setMinimumWidth(60)
        layout.addWidget(self.end_level_spin)

        # Creature type dropdown
        creature_label = QLabel("Creature:")
        layout.addWidget(creature_label)

        self.creature_combo = QComboBox()
        self.creature_combo.addItems([
            "starfish", "blob", "polyp", "tentacle", "medusa", "dragon"
        ])
        if mapping:
            index = self.creature_combo.findText(mapping.creature_type)
            if index >= 0:
                self.creature_combo.setCurrentIndex(index)
        self.creature_combo.setMinimumWidth(100)
        self.creature_combo.currentTextChanged.connect(self._on_creature_changed)
        layout.addWidget(self.creature_combo)

        # Creation selector dropdown
        creation_label = QLabel("Creation:")
        layout.addWidget(creation_label)

        self.creation_combo = QComboBox()
        self.creation_combo.setMinimumWidth(180)
        self._populate_creation_combo(mapping)
        layout.addWidget(self.creation_combo)

        # Remove button
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setMaximumWidth(30)
        self.remove_btn.setToolTip("Remove this mapping")
        layout.addWidget(self.remove_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Style
        self.setStyleSheet("""
            MappingWidget {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QLabel {
                color: #e5e5e5;
                font-size: 10pt;
            }
            QSpinBox, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
                color: #e5e5e5;
                font-size: 10pt;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e5e5e5;
                selection-background-color: #6366f1;
                selection-color: white;
                border: 1px solid #4a4a4a;
            }
            QComboBox::drop-down {
                background-color: #4a4a4a;
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #e5e5e5;
                width: 0;
                height: 0;
            }
            QPushButton {
                background-color: #d32f2f;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """)

    def _on_creature_changed(self, creature_type):
        """Update creation combo when creature type changes."""
        self._populate_creation_combo()

    def _populate_creation_combo(self, existing_mapping=None):
        """Populate the creation combo with creations of selected type."""
        current_creature = self.creature_combo.currentText()

        # Filter creations by type
        matching_creations = [
            c for c in self.available_creations
            if c.creature_type == current_creature
        ]

        # Clear and repopulate
        self.creation_combo.clear()

        if not matching_creations:
            self.creation_combo.addItem("(No creations available)")
            self.creation_combo.setEnabled(False)
            return

        self.creation_combo.setEnabled(True)
        for creation in matching_creations:
            self.creation_combo.addItem(creation.name, creation)

        # Try to restore previous selection
        if existing_mapping and existing_mapping.creation_name:
            index = self.creation_combo.findText(existing_mapping.creation_name)
            if index >= 0:
                self.creation_combo.setCurrentIndex(index)

    def get_mapping(self):
        """Create an EnemyMapping from current widget state."""
        start = self.start_level_spin.value()
        end = self.end_level_spin.value()
        creature_type = self.creature_combo.currentText()

        # Get selected creation
        creation = self.creation_combo.currentData()
        if not creation:
            # No creation selected or available
            return None

        return EnemyMapping(
            level_range=(start, end),
            creature_type=creature_type,
            parameters=creation.parameters,
            creation_name=creation.name
        )


class EnemyTabWidget(QWidget):
    """Tab widget for a single enemy type showing all its mappings."""

    # Game spawn level ranges for each enemy type
    ENEMY_SPAWN_RANGES = {
        "ENEMY_STARTLE": (1, 5),
        "ENEMY_SLIME": (1, 5),
        "ENEMY_SKELETON": (2, 14),
        "ENEMY_ORC": (4, 19),
        "ENEMY_DEMON": (6, 25),
        "ENEMY_DRAGON": (10, 25)
    }

    def __init__(self, enemy_type, available_creations):
        """
        Args:
            enemy_type: Enemy type constant (e.g., "ENEMY_ORC")
            available_creations: List of Creation objects
        """
        super().__init__()
        self.enemy_type = enemy_type
        self.available_creations = available_creations
        self.mapping_widgets = []

        # Main layout
        layout = QVBoxLayout()

        # Header with spawn range info
        spawn_range = self.ENEMY_SPAWN_RANGES.get(enemy_type, (1, 25))
        header = QLabel(f"{enemy_type} Level Mappings")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e5e5e5; padding: 10px;")
        layout.addWidget(header)

        # Spawn info label
        spawn_info = QLabel(f"Game Spawn Range: Levels {spawn_range[0]}-{spawn_range[1]}")
        spawn_info.setStyleSheet(
            "font-size: 10pt; color: #fbbf24; padding: 5px 10px; "
            "background-color: #3a2a1a; border-radius: 4px; margin: 0px 10px 10px 10px;"
        )
        spawn_info.setToolTip(
            f"This enemy appears in the game from level {spawn_range[0]} to {spawn_range[1]}.\n"
            "You only need to configure mappings for these levels.\n"
            "Unconfigured levels will use default procedural generation."
        )
        layout.addWidget(spawn_info)

        # Scroll area for mappings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6366f1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8b5cf6;
            }
        """)

        self.mappings_container = QWidget()
        self.mappings_container.setStyleSheet("background-color: #1e1e1e;")
        self.mappings_layout = QVBoxLayout()
        self.mappings_layout.setSpacing(10)
        self.mappings_layout.setContentsMargins(10, 10, 10, 10)
        self.mappings_container.setLayout(self.mappings_layout)
        scroll_area.setWidget(self.mappings_container)

        layout.addWidget(scroll_area)

        # Add button
        add_btn = QPushButton("+ Add Level Range")
        add_btn.clicked.connect(self.add_mapping)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8b5cf6;
            }
        """)
        layout.addWidget(add_btn)

        self.setLayout(layout)

        # Style
        self.setStyleSheet("""
            EnemyTabWidget {
                background-color: #1e1e1e;
            }
        """)

    def add_mapping(self, mapping=None):
        """Add a new mapping widget."""
        # Determine default level range (next available range)
        if self.mapping_widgets:
            last_widget = self.mapping_widgets[-1]
            last_end = last_widget.end_level_spin.value()
            new_start = min(last_end + 1, 25)
            new_end = min(new_start + 4, 25)

            if mapping is None:
                # Create a default mapping with next range
                mapping = EnemyMapping(
                    level_range=(new_start, new_end),
                    creature_type="tentacle",
                    parameters={},
                    creation_name=None
                )

        widget = MappingWidget(self.enemy_type, self.available_creations, mapping)
        widget.remove_btn.clicked.connect(lambda: self.remove_mapping(widget))

        self.mapping_widgets.append(widget)
        self.mappings_layout.addWidget(widget)

    def remove_mapping(self, widget):
        """Remove a mapping widget."""
        if widget in self.mapping_widgets:
            self.mapping_widgets.remove(widget)
            self.mappings_layout.removeWidget(widget)
            widget.deleteLater()

    def get_mappings(self):
        """Get all mappings from this tab."""
        mappings = []
        for widget in self.mapping_widgets:
            mapping = widget.get_mapping()
            if mapping:
                mappings.append(mapping)
        return mappings

    def load_mappings(self, mappings):
        """Load mappings into this tab."""
        # Clear existing
        for widget in list(self.mapping_widgets):
            self.remove_mapping(widget)

        # Add new mappings
        for mapping in mappings:
            self.add_mapping(mapping)

        # If no mappings, add one default
        if not mappings:
            self.add_mapping()


class LibraryManagerWindow(QMainWindow):
    """Main library manager window."""

    def __init__(self):
        super().__init__()

        self.current_pack = EnemyPack("Untitled Pack")
        self.current_file_path = None
        self.available_creations = []

        self.setWindowTitle("Creature Library Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #e5e5e5;
                padding: 10px 20px;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                font-size: 11pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #6366f1;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3a3a3a;
            }
        """)

        self._init_ui()
        self._init_menu()
        self._load_creations()
        self._setup_default_pack()

    def _init_ui(self):
        """Initialize UI layout."""
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Pack name label
        self.pack_label = QLabel(f"Enemy Pack: {self.current_pack.pack_name}")
        self.pack_label.setStyleSheet(
            "font-size: 16pt; font-weight: bold; color: #e5e5e5; padding: 10px;"
        )
        layout.addWidget(self.pack_label)

        # Tab widget for enemy types
        self.tabs = QTabWidget()

        self.enemy_tabs = {}
        enemy_names = {
            "ENEMY_STARTLE": "Startle",
            "ENEMY_SLIME": "Slime",
            "ENEMY_SKELETON": "Skeleton",
            "ENEMY_ORC": "Orc",
            "ENEMY_DEMON": "Demon",
            "ENEMY_DRAGON": "Dragon"
        }

        for enemy_type in EnemyPack.VALID_ENEMY_TYPES:
            tab = EnemyTabWidget(enemy_type, self.available_creations)
            self.enemy_tabs[enemy_type] = tab
            display_name = enemy_names.get(enemy_type, enemy_type)
            self.tabs.addTab(tab, display_name)

        layout.addWidget(self.tabs)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Pack", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._new_pack)
        file_menu.addAction(new_action)

        load_action = QAction("&Load Pack", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self._load_pack)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        save_action = QAction("&Save Pack", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._save_pack)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Pack &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_pack_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        refresh_action = QAction("&Refresh Creations", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._load_creations)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _load_creations(self):
        """Load all available creations from library."""
        library_dir = Path(__file__).parent / 'library' / 'creations'
        self.available_creations = list_creations(library_dir)

        # Update all tabs
        for tab in self.enemy_tabs.values():
            tab.available_creations = self.available_creations

        # Show count in status
        count = len(self.available_creations)
        QMessageBox.information(
            self,
            "Creations Loaded",
            f"Loaded {count} creation(s) from library."
        )

    def _setup_default_pack(self):
        """Set up a new pack with default empty mappings."""
        for enemy_type, tab in self.enemy_tabs.items():
            tab.load_mappings([])

    def _new_pack(self):
        """Create a new enemy pack."""
        # Prompt for pack name
        name, ok = QInputDialog.getText(
            self,
            "New Enemy Pack",
            "Enter pack name:",
            text="New Pack"
        )

        if not ok or not name.strip():
            return

        self.current_pack = EnemyPack(name.strip())
        self.current_file_path = None
        self._setup_default_pack()
        self._update_title()

    def _load_pack(self):
        """Load an enemy pack from file."""
        library_dir = Path(__file__).parent / 'library' / 'enemy_packs'
        library_dir.mkdir(parents=True, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Enemy Pack",
            str(library_dir),
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            pack = EnemyPack.load_from_file(Path(file_path))
            self.current_pack = pack
            self.current_file_path = Path(file_path)

            # Load mappings into tabs
            for enemy_type, tab in self.enemy_tabs.items():
                mappings = pack.get_all_mappings(enemy_type)
                tab.load_mappings(mappings)

            self._update_title()

            # Show validation warnings if any
            warnings = pack.validate()
            if warnings:
                QMessageBox.warning(
                    self,
                    "Pack Validation Warnings",
                    "Pack loaded with warnings:\n\n" + "\n".join(warnings)
                )
            else:
                QMessageBox.information(
                    self,
                    "Pack Loaded",
                    f"Successfully loaded '{pack.pack_name}'"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load enemy pack:\n{str(e)}"
            )

    def _save_pack(self):
        """Save current pack to file."""
        if self.current_file_path:
            self._save_to_file(self.current_file_path)
        else:
            self._save_pack_as()

    def _save_pack_as(self):
        """Save current pack to a new file."""
        library_dir = Path(__file__).parent / 'library' / 'enemy_packs'
        library_dir.mkdir(parents=True, exist_ok=True)

        # Suggest filename based on pack name
        safe_name = "".join(
            c if c.isalnum() or c in (' ', '_', '-') else '_'
            for c in self.current_pack.pack_name
        ).replace(' ', '_').lower()
        default_name = f"{safe_name}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Enemy Pack",
            str(library_dir / default_name),
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        self._save_to_file(Path(file_path))

    def _save_to_file(self, file_path):
        """Save pack to specified file path."""
        try:
            # Collect all mappings from tabs
            self.current_pack.enemies = {
                enemy_type: [] for enemy_type in EnemyPack.VALID_ENEMY_TYPES
            }

            for enemy_type, tab in self.enemy_tabs.items():
                mappings = tab.get_mappings()
                for mapping in mappings:
                    try:
                        self.current_pack.add_mapping(enemy_type, mapping)
                    except ValueError as e:
                        QMessageBox.critical(
                            self,
                            "Validation Error",
                            f"Error in {enemy_type}:\n{str(e)}"
                        )
                        return

            # Validate pack (informational only)
            warnings = self.current_pack.validate()

            # Save to file
            self.current_pack.save_to_file(file_path)
            self.current_file_path = file_path
            self._update_title()

            # Show success with optional warnings
            if warnings:
                # Show warnings but indicate successful save
                msg = f"Enemy pack saved to:\n{file_path.name}\n\nNotes:\n" + "\n".join(f"• {w}" for w in warnings[:5])
                if len(warnings) > 5:
                    msg += f"\n• ... and {len(warnings) - 5} more"
                QMessageBox.information(
                    self,
                    "Pack Saved",
                    msg
                )
            else:
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"Enemy pack saved to:\n{file_path.name}\n\nAll enemy types fully configured!"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save enemy pack:\n{str(e)}"
            )

    def _update_title(self):
        """Update window title and pack label."""
        title = f"Creature Library Manager - {self.current_pack.pack_name}"
        if self.current_file_path:
            title += f" ({self.current_file_path.name})"
        else:
            title += " (unsaved)"

        self.setWindowTitle(title)
        self.pack_label.setText(f"Enemy Pack: {self.current_pack.pack_name}")

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Library Manager",
            "<h2>Creature Library Manager</h2>"
            "<p>Organize creature creations into level-based enemy packs.</p>"
            "<p><b>Workflow:</b></p>"
            "<ol>"
            "<li>Create creatures in the DNA Editor</li>"
            "<li>Save them to the library (Ctrl+S)</li>"
            "<li>Organize them here by enemy type and level range</li>"
            "<li>Save complete enemy packs for use in the game</li>"
            "</ol>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Flexible creature-to-enemy mapping</li>"
            "<li>Level range assignments with interpolation support</li>"
            "<li>Validation and warnings for incomplete packs</li>"
            "<li>JSON export for game integration</li>"
            "</ul>"
            f"<p>Creations loaded: {len(self.available_creations)}</p>"
        )


def main():
    """Entry point for library manager application."""
    app = QApplication(sys.argv)

    # Set application-wide font
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = LibraryManagerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
