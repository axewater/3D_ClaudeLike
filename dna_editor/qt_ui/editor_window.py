"""
Main editor window - orchestrates control panel and 3D renderer.

Handles undo/redo, file export, and coordinate updates between UI and 3D.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
import json
import sys
import os

from .control_panel_modern import ModernControlPanel
from .ursina_renderer import UrsinaRenderer
from ..controllers.state_manager import StateManager


class EditorWindow(QMainWindow):
    """Main DNA Editor window."""

    def __init__(self):
        """Initialize editor window."""
        super().__init__()

        self.state_manager = StateManager()

        self.setWindowTitle("DNA Editor - Creature Designer")
        self.setFixedSize(1300, 850)  # Modern wide layout with breathing room
        self.move(100, 100)

        # Apply modern dark theme stylesheet with enhanced visuals
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #1a1a1a, stop:1 #1e1e1e);
            }
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2d2d2d, stop:1 #252525);
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                margin-top: 16px;
                padding: 20px;
                font-weight: bold;
                color: #e5e5e5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 6px;
                color: white;
                font-size: 11pt;
                font-weight: bold;
            }
            QLabel {
                color: #e5e5e5;
                font-size: 11pt;
            }
            QSpinBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a3a3a, stop:1 #323232);
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px;
                color: #e5e5e5;
                font-size: 12pt;
                min-height: 45px;
                selection-background-color: #6366f1;
            }
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a3a3a, stop:1 #323232);
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px;
                padding-right: 35px;
                color: #e5e5e5;
                font-size: 12pt;
                min-height: 45px;
                selection-background-color: #6366f1;
            }
            QSpinBox:focus, QComboBox:focus {
                border: 2px solid #6366f1;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #424242, stop:1 #3a3a3a);
            }
            QSpinBox:hover, QComboBox:hover {
                border: 2px solid #8b5cf6;
            }
            QSpinBox::up-button {
                background: #4a4a4a;
                border-radius: 4px;
                border: none;
                width: 24px;
                subcontrol-origin: border;
                subcontrol-position: top right;
            }
            QSpinBox::down-button {
                background: #4a4a4a;
                border-radius: 4px;
                border: none;
                width: 24px;
                subcontrol-origin: border;
                subcontrol-position: bottom right;
            }
            QSpinBox::up-button:hover {
                background: #6366f1;
            }
            QSpinBox::down-button:hover {
                background: #6366f1;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #e0e0e0;
            }
            QSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #e0e0e0;
            }
            QSpinBox::up-arrow:hover {
                border-bottom-color: #ffffff;
            }
            QSpinBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                background-color: #3a3a3a;
                border-radius: 3px;
                border: none;
            }
            QComboBox::drop-down:hover {
                background-color: #8b5cf6;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #e0e0e0;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #7c3aed, stop:1 #6366f1);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 12px 20px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #8b5cf6, stop:1 #7c3aed);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #6d28d9, stop:1 #5b21b6);
                padding-top: 14px;
                padding-bottom: 10px;
            }
            QPushButton:disabled {
                background: #333333;
                color: #666666;
            }
            QSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a3a3a, stop:1 #2d2d2d);
                height: 10px;
                border-radius: 5px;
                border: 1px solid #4a4a4a;
            }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                                           fx:0.3, fy:0.3,
                                           stop:0 #a78bfa, stop:1 #6366f1);
                width: 24px;
                height: 24px;
                margin: -8px 0;
                border-radius: 12px;
                border: 2px solid #8b5cf6;
            }
            QSlider::handle:horizontal:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                                           fx:0.3, fy:0.3,
                                           stop:0 #c4b5fd, stop:1 #8b5cf6);
                border: 2px solid #a78bfa;
            }
            QSlider::handle:horizontal:pressed {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                                           fx:0.3, fy:0.3,
                                           stop:0 #ddd6fe, stop:1 #a78bfa);
            }
        """)

        self._init_ui()
        self._init_menu()

        # Initial creature build
        self._on_creature_changed()

    def _init_ui(self):
        """Initialize UI layout."""
        # Central widget with vertical layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Control panel
        self.control_panel = ModernControlPanel()
        self.control_panel.creature_changed.connect(self._on_creature_changed)
        self.control_panel.undo_requested.connect(self._on_undo)
        self.control_panel.redo_requested.connect(self._on_redo)
        self.control_panel.export_requested.connect(self._on_export)
        self.control_panel.attack_requested.connect(self._on_attack)
        self.control_panel.attack_2_requested.connect(self._on_attack_2)

        # Wrap control panel in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.control_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
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
        layout.addWidget(scroll_area)

        # Status label at bottom
        status_label = QLabel("3D Preview: Separate Window")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(
            "color: #888; "
            "font-size: 10px; "
            "padding: 8px; "
            "background-color: #2a2a2a;"
        )
        layout.addWidget(status_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize Ursina renderer (separate window)
        self.renderer = UrsinaRenderer()

    def _init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_action = QAction("&Export JSON", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(self.redo_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _on_creature_changed(self):
        """Handle creature parameter changes."""
        # Save current state for undo
        state = self.control_panel.get_state()
        self._save_state(state)

        # Rebuild creature in renderer
        self._rebuild_creature_from_state(state)

        # Update undo/redo button states
        self._update_undo_redo_state()

    def _save_state(self, state):
        """Save state for undo/redo."""
        self.state_manager.save_state(
            creature_type=state.get('creature_type', 'tentacle'),
            # Tentacle parameters
            num_tentacles=state.get('num_tentacles', 2),
            segments=state.get('segments', 12),
            algorithm=state.get('algorithm', 'bezier'),
            params=state.get('params', {}),
            thickness_base=state.get('thickness_base', 0.25),
            taper_factor=state.get('taper_factor', 0.6),
            branch_depth=state.get('branch_depth', 0),
            branch_count=state.get('branch_count', 1),
            body_scale=state.get('body_scale', 1.2),
            tentacle_color=state.get('tentacle_color', (0.6, 0.3, 0.7)),
            hue_shift=state.get('hue_shift', 0.1),
            anim_speed=state.get('anim_speed', 2.0),
            wave_amplitude=state.get('wave_amplitude', 0.05),
            pulse_speed=state.get('pulse_speed', 1.5),
            pulse_amount=state.get('pulse_amount', 0.05),
            num_eyes=state.get('num_eyes', 3),
            eye_size_min=state.get('eye_size_min', 0.1),
            eye_size_max=state.get('eye_size_max', 0.25),
            eyeball_color=state.get('eyeball_color', (1.0, 1.0, 1.0)),
            pupil_color=state.get('pupil_color', (0.0, 0.0, 0.0)),
            # Blob parameters
            blob_branch_depth=state.get('blob_branch_depth', 2),
            blob_branch_count=state.get('blob_branch_count', 2),
            cube_size_min=state.get('cube_size_min', 0.3),
            cube_size_max=state.get('cube_size_max', 0.8),
            cube_spacing=state.get('cube_spacing', 1.2),
            blob_color=state.get('blob_color', (0.2, 0.8, 0.4)),
            blob_transparency=state.get('blob_transparency', 0.7),
            jiggle_speed=state.get('jiggle_speed', 2.0),
            blob_pulse_amount=state.get('blob_pulse_amount', 0.1),
            # Polyp parameters
            num_spheres=state.get('num_spheres', 4),
            base_sphere_size=state.get('base_sphere_size', 0.8),
            polyp_color=state.get('polyp_color', (0.6, 0.3, 0.7)),
            curve_intensity=state.get('curve_intensity', 0.4),
            polyp_tentacles_per_sphere=state.get('polyp_tentacles_per_sphere', 6),
            polyp_segments=state.get('polyp_segments', 12),
            # Starfish parameters
            num_arms=state.get('num_arms', 5),
            arm_segments=state.get('arm_segments', 6),
            central_body_size=state.get('central_body_size', 0.8),
            arm_base_thickness=state.get('arm_base_thickness', 0.4),
            starfish_color=state.get('starfish_color', (0.9, 0.5, 0.3)),
            curl_factor=state.get('curl_factor', 0.3),
            starfish_anim_speed=state.get('starfish_anim_speed', 1.5),
            starfish_pulse_amount=state.get('starfish_pulse_amount', 0.06),
            # Dragon parameters
            dragon_segments=state.get('dragon_segments', 15),
            dragon_thickness=state.get('dragon_thickness', 0.3),
            dragon_taper=state.get('dragon_taper', 0.6),
            dragon_head_scale=state.get('dragon_head_scale', 3.0),
            dragon_body_color=state.get('dragon_body_color', (200, 40, 40)),
            dragon_head_color=state.get('dragon_head_color', (255, 200, 50)),
            dragon_weave_amplitude=state.get('dragon_weave_amplitude', 0.5),
            dragon_bob_amplitude=state.get('dragon_bob_amplitude', 0.3),
            dragon_anim_speed=state.get('dragon_anim_speed', 1.5),
            dragon_num_eyes=state.get('dragon_num_eyes', 2),
            dragon_eye_size=state.get('dragon_eye_size', 0.15),
            dragon_eyeball_color=state.get('dragon_eyeball_color', (255, 200, 50)),
            dragon_pupil_color=state.get('dragon_pupil_color', (20, 0, 0)),
            dragon_mouth_size=state.get('dragon_mouth_size', 0.25),
            dragon_mouth_color=state.get('dragon_mouth_color', (20, 0, 0)),
            dragon_num_whiskers_per_side=state.get('dragon_num_whiskers_per_side', 2),
            dragon_whisker_segments=state.get('dragon_whisker_segments', 4),
            dragon_whisker_thickness=state.get('dragon_whisker_thickness', 0.05)
        )

    def _on_undo(self):
        """Handle undo request."""
        state = self.state_manager.undo()
        if state:
            self.control_panel.set_state(state)
            self._update_undo_redo_state()
            self._rebuild_creature_from_state(state)

    def _on_redo(self):
        """Handle redo request."""
        state = self.state_manager.redo()
        if state:
            self.control_panel.set_state(state)
            self._update_undo_redo_state()
            self._rebuild_creature_from_state(state)

    def _rebuild_creature_from_state(self, state):
        """Rebuild creature from state dict."""
        self.renderer.rebuild_creature(
            creature_type=state.get('creature_type', 'tentacle'),
            # Tentacle parameters
            num_tentacles=state.get('num_tentacles', 2),
            segments=state.get('segments', 12),
            algorithm=state.get('algorithm', 'bezier'),
            params=state.get('params', {}),
            thickness_base=state.get('thickness_base', 0.25),
            taper_factor=state.get('taper_factor', 0.6),
            branch_depth=state.get('branch_depth', 0),
            branch_count=state.get('branch_count', 1),
            body_scale=state.get('body_scale', 1.2),
            tentacle_color=state.get('tentacle_color', (0.6, 0.3, 0.7)),
            hue_shift=state.get('hue_shift', 0.1),
            anim_speed=state.get('anim_speed', 2.0),
            wave_amplitude=state.get('wave_amplitude', 0.05),
            pulse_speed=state.get('pulse_speed', 1.5),
            pulse_amount=state.get('pulse_amount', 0.05),
            num_eyes=state.get('num_eyes', 3),
            eye_size_min=state.get('eye_size_min', 0.1),
            eye_size_max=state.get('eye_size_max', 0.25),
            eyeball_color=state.get('eyeball_color', (1.0, 1.0, 1.0)),
            pupil_color=state.get('pupil_color', (0.0, 0.0, 0.0)),
            # Blob parameters
            blob_branch_depth=state.get('blob_branch_depth', 2),
            blob_branch_count=state.get('blob_branch_count', 2),
            cube_size_min=state.get('cube_size_min', 0.3),
            cube_size_max=state.get('cube_size_max', 0.8),
            cube_spacing=state.get('cube_spacing', 1.2),
            blob_color=state.get('blob_color', (0.2, 0.8, 0.4)),
            blob_transparency=state.get('blob_transparency', 0.7),
            jiggle_speed=state.get('jiggle_speed', 2.0),
            blob_pulse_amount=state.get('blob_pulse_amount', 0.1),
            # Polyp parameters
            num_spheres=state.get('num_spheres', 4),
            base_sphere_size=state.get('base_sphere_size', 0.8),
            polyp_color=state.get('polyp_color', (0.6, 0.3, 0.7)),
            curve_intensity=state.get('curve_intensity', 0.4),
            polyp_tentacles_per_sphere=state.get('polyp_tentacles_per_sphere', 6),
            polyp_segments=state.get('polyp_segments', 12),
            # Starfish parameters
            num_arms=state.get('num_arms', 5),
            arm_segments=state.get('arm_segments', 6),
            central_body_size=state.get('central_body_size', 0.8),
            arm_base_thickness=state.get('arm_base_thickness', 0.4),
            starfish_color=state.get('starfish_color', (0.9, 0.5, 0.3)),
            curl_factor=state.get('curl_factor', 0.3),
            starfish_anim_speed=state.get('starfish_anim_speed', 1.5),
            starfish_pulse_amount=state.get('starfish_pulse_amount', 0.06),
            # Dragon parameters
            dragon_segments=state.get('dragon_segments', 15),
            dragon_thickness=state.get('dragon_thickness', 0.3),
            dragon_taper=state.get('dragon_taper', 0.6),
            dragon_head_scale=state.get('dragon_head_scale', 3.0),
            dragon_body_color=state.get('dragon_body_color', (200, 40, 40)),
            dragon_head_color=state.get('dragon_head_color', (255, 200, 50)),
            dragon_weave_amplitude=state.get('dragon_weave_amplitude', 0.5),
            dragon_bob_amplitude=state.get('dragon_bob_amplitude', 0.3),
            dragon_anim_speed=state.get('dragon_anim_speed', 1.5),
            dragon_num_eyes=state.get('dragon_num_eyes', 2),
            dragon_eye_size=state.get('dragon_eye_size', 0.15),
            dragon_eyeball_color=state.get('dragon_eyeball_color', (255, 200, 50)),
            dragon_pupil_color=state.get('dragon_pupil_color', (20, 0, 0)),
            dragon_mouth_size=state.get('dragon_mouth_size', 0.25),
            dragon_mouth_color=state.get('dragon_mouth_color', (20, 0, 0)),
            dragon_num_whiskers_per_side=state.get('dragon_num_whiskers_per_side', 2),
            dragon_whisker_segments=state.get('dragon_whisker_segments', 4),
            dragon_whisker_thickness=state.get('dragon_whisker_thickness', 0.05)
        )

    def _update_undo_redo_state(self):
        """Update undo/redo button and menu enabled states."""
        can_undo = self.state_manager.can_undo()
        can_redo = self.state_manager.can_redo()

        # Update control panel buttons
        self.control_panel.set_undo_redo_enabled(can_undo, can_redo)

        # Update menu actions
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)

    def _on_attack(self):
        """Handle Attack 1 button press (all tentacles whip attack)."""
        self.renderer.trigger_attack()

    def _on_attack_2(self):
        """Handle Attack 2 button press (single tentacle slash)."""
        self.renderer.trigger_attack_2()

    def _on_export(self):
        """Handle export to JSON."""
        # Get current state
        state = self.control_panel.get_state()
        creature_type = state.get('creature_type', 'tentacle')

        # Create DNA config dict with creature type
        dna_config = {
            'creature_type': creature_type
        }

        # Add type-specific parameters
        if creature_type == 'tentacle':
            dna_config.update({
                'num_tentacles': state['num_tentacles'],
                'segments_per_tentacle': state['segments'],
                'algorithm': state['algorithm'],
                'algorithm_params': state['params'],
                'thickness_base': state['thickness_base'],
                'taper_factor': state['taper_factor'],
                'branch_depth': state.get('branch_depth', 0),
                'branch_count': state.get('branch_count', 1),
                'body_scale': state.get('body_scale', 1.2),
                'tentacle_color': state.get('tentacle_color', (0.6, 0.3, 0.7)),
                'hue_shift': state.get('hue_shift', 0.1),
                'anim_speed': state.get('anim_speed', 2.0),
                'wave_amplitude': state.get('wave_amplitude', 0.05),
                'pulse_speed': state.get('pulse_speed', 1.5),
                'pulse_amount': state.get('pulse_amount', 0.05),
                'num_eyes': state.get('num_eyes', 3),
                'eye_size_min': state.get('eye_size_min', 0.1),
                'eye_size_max': state.get('eye_size_max', 0.25),
                'eyeball_color': state.get('eyeball_color', (1.0, 1.0, 1.0)),
                'pupil_color': state.get('pupil_color', (0.0, 0.0, 0.0))
            })
        elif creature_type == 'blob':
            dna_config.update({
                'branch_depth': state.get('blob_branch_depth', 2),
                'branch_count': state.get('blob_branch_count', 2),
                'cube_size_min': state.get('cube_size_min', 0.3),
                'cube_size_max': state.get('cube_size_max', 0.8),
                'cube_spacing': state.get('cube_spacing', 1.2),
                'blob_color': state.get('blob_color', (0.2, 0.8, 0.4)),
                'blob_transparency': state.get('blob_transparency', 0.7),
                'jiggle_speed': state.get('jiggle_speed', 2.0),
                'blob_pulse_amount': state.get('blob_pulse_amount', 0.1)
            })
        elif creature_type == 'polyp':
            dna_config.update({
                'num_spheres': state.get('num_spheres', 4),
                'base_sphere_size': state.get('base_sphere_size', 0.8),
                'polyp_color': state.get('polyp_color', (0.6, 0.3, 0.7)),
                'curve_intensity': state.get('curve_intensity', 0.4),
                'tentacles_per_sphere': state.get('polyp_tentacles_per_sphere', 6),
                'segments_per_tentacle': state.get('polyp_segments', 12),
                'algorithm': state.get('algorithm', 'bezier'),
                'thickness_base': state.get('thickness_base', 0.2),
                'taper_factor': state.get('taper_factor', 0.6)
            })
        elif creature_type == 'starfish':
            dna_config.update({
                'num_arms': state.get('num_arms', 5),
                'arm_segments': state.get('arm_segments', 6),
                'central_body_size': state.get('central_body_size', 0.8),
                'arm_base_thickness': state.get('arm_base_thickness', 0.4),
                'starfish_color': state.get('starfish_color', (0.9, 0.5, 0.3)),
                'curl_factor': state.get('curl_factor', 0.3),
                'anim_speed': state.get('starfish_anim_speed', 1.5),
                'pulse_amount': state.get('starfish_pulse_amount', 0.06)
            })
        elif creature_type == 'medusa':
            dna_config.update({
                'num_tentacles': state.get('num_tentacles', 8),
                'segments_per_tentacle': state.get('segments_per_tentacle', 16),
                'algorithm': state.get('algorithm', 'fourier'),
                'algorithm_params': state.get('algorithm_params', {}),
                'thickness_base': state.get('thickness_base', 0.25),
                'taper_factor': state.get('taper_factor', 0.6),
                'body_scale': state.get('body_scale', 1.0),
                'tentacle_color': state.get('tentacle_color', (0.4, 0.2, 0.6)),
                'hue_shift': state.get('hue_shift', 0.08),
                'anim_speed': state.get('anim_speed', 1.5),
                'wave_amplitude': state.get('wave_amplitude', 0.08),
                'pulse_speed': state.get('pulse_speed', 1.2),
                'pulse_amount': state.get('pulse_amount', 0.06),
                'eye_size': state.get('eye_size', 0.18),
                'eyeball_color': state.get('eyeball_color', (1.0, 0.95, 0.85)),
                'pupil_color': state.get('pupil_color', (0.1, 0.0, 0.2))
            })
        elif creature_type == 'dragon':
            dna_config.update({
                'num_segments': state.get('dragon_segments', 15),
                'segment_thickness': state.get('dragon_thickness', 0.3),
                'taper_factor': state.get('dragon_taper', 0.6),
                'head_scale': state.get('dragon_head_scale', 3.0),
                'body_color': state.get('dragon_body_color', (200, 40, 40)),
                'head_color': state.get('dragon_head_color', (255, 200, 50)),
                'weave_amplitude': state.get('dragon_weave_amplitude', 0.5),
                'bob_amplitude': state.get('dragon_bob_amplitude', 0.3),
                'anim_speed': state.get('dragon_anim_speed', 1.5)
            })

        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export DNA Configuration",
            "creature_dna.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(dna_config, f, indent=2)

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"DNA configuration exported to:\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export DNA:\n{str(e)}"
                )

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About DNA Editor",
            "<h2>DNA Editor - Procedural Creature Designer</h2>"
            "<p>Interactive 3D tool for designing procedural creatures "
            "with real-time parameter adjustment.</p>"
            "<p><b>Creature Types:</b></p>"
            "<ul>"
            "<li><b>Tentacle Creature</b> - Mathematical curve-based tentacles (Bezier/Fourier)</li>"
            "<li><b>Blob Creature</b> - Translucent slime cube clusters</li>"
            "<li><b>Polyp Creature</b> - Organic spine with spheres and tentacles</li>"
            "<li><b>Starfish Creature</b> - Radial symmetry with articulated arms</li>"
            "<li><b>Medusa Creature</b> - Tentacles with eyes at the tips</li>"
            "<li><b>Dragon Creature</b> - Space Harrier inspired segmented serpent</li>"
            "</ul>"
            "<p><b>Controls:</b></p>"
            "<ul>"
            "<li>Switch between creature types</li>"
            "<li>Adjust parameters with sliders</li>"
            "<li>Use presets for quick configurations (Tentacle)</li>"
            "<li>Undo/Redo (Ctrl+Z / Ctrl+Y)</li>"
            "<li>Export to JSON (Ctrl+E)</li>"
            "<li>Test attack animations</li>"
            "</ul>"
            "<p><b>Camera:</b></p>"
            "<ul>"
            "<li>Mouse Drag - Rotate view</li>"
            "<li>Scroll - Zoom in/out</li>"
            "<li>R - Reset camera</li>"
            "</ul>"
            "<p>Built with PyQt6 and Ursina Engine</p>"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # Cleanup renderer
        self.renderer.cleanup()

        # Accept close
        event.accept()
