"""
Control panel with all DNA editor controls.

Provides sliders, spinboxes, buttons for creature parameters.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QSlider,
    QSpinBox, QComboBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..core.constants import PRESETS


class ControlPanel(QWidget):
    """Left panel with all creature parameter controls."""

    # Signals emitted when parameters change
    creature_changed = pyqtSignal()  # Any parameter changed
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    export_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize control panel."""
        super().__init__(parent)

        # Initialize state
        self._num_tentacles = 2
        self._segments = 12
        self._algorithm = 'bezier'
        self._bezier_control_strength = 0.4
        self._fourier_waves = 3
        self._fourier_amplitude = 0.15
        self._thickness_base = 0.25
        self._taper_factor = 0.6
        self._branch_depth = 0
        self._branch_count = 1

        # Block signals during programmatic updates
        self._updating = False

        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Increased from 15
        layout.setContentsMargins(15, 15, 15, 15)  # Increased from 10

        # Title
        title = QLabel("DNA Editor Controls")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # Increased from 16
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Creature Settings
        layout.addWidget(self._create_creature_settings())

        # Algorithm Parameters
        layout.addWidget(self._create_algorithm_params())

        # Thickness Settings
        layout.addWidget(self._create_thickness_settings())

        # Branching Settings
        layout.addWidget(self._create_branching_settings())

        # Presets
        layout.addWidget(self._create_presets())

        # Actions (Undo/Redo/Export)
        layout.addWidget(self._create_actions())

        layout.addStretch()
        self.setLayout(layout)
        self.setMinimumWidth(480)  # Minimum width to fit all controls
        self.setMaximumWidth(480)

    def _create_creature_settings(self):
        """Create creature settings group."""
        group = QGroupBox("Creature Settings")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Add spacing between items
        layout.setContentsMargins(12, 15, 12, 12)  # Add internal padding

        # Tentacle count
        tent_layout = QHBoxLayout()
        tent_label = QLabel("Tentacles:")
        tent_label.setFont(QFont("Arial", 11))
        tent_label.setMinimumWidth(110)
        tent_layout.addWidget(tent_label)
        self.tentacles_spin = QSpinBox()
        self.tentacles_spin.setFont(QFont("Arial", 11))
        self.tentacles_spin.setMinimumWidth(120)
        self.tentacles_spin.setMinimumHeight(40)
        self.tentacles_spin.setRange(1, 12)
        self.tentacles_spin.setValue(self._num_tentacles)
        self.tentacles_spin.valueChanged.connect(self._on_tentacles_changed)
        tent_layout.addWidget(self.tentacles_spin)
        tent_layout.addStretch()
        layout.addLayout(tent_layout)

        # Segments
        seg_layout = QHBoxLayout()
        seg_label = QLabel("Segments:")
        seg_label.setFont(QFont("Arial", 11))
        seg_label.setMinimumWidth(110)
        seg_layout.addWidget(seg_label)
        self.segments_spin = QSpinBox()
        self.segments_spin.setFont(QFont("Arial", 11))
        self.segments_spin.setMinimumWidth(120)
        self.segments_spin.setMinimumHeight(40)
        self.segments_spin.setRange(5, 20)
        self.segments_spin.setValue(self._segments)
        self.segments_spin.valueChanged.connect(self._on_segments_changed)
        seg_layout.addWidget(self.segments_spin)
        seg_layout.addStretch()
        layout.addLayout(seg_layout)

        # Algorithm
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Algorithm:")
        algo_label.setFont(QFont("Arial", 11))
        algo_label.setMinimumWidth(110)
        algo_layout.addWidget(algo_label)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setFont(QFont("Arial", 11))
        self.algorithm_combo.setMinimumWidth(180)
        self.algorithm_combo.setMinimumHeight(40)
        self.algorithm_combo.addItems(["Bezier", "Fourier"])
        self.algorithm_combo.setCurrentText("Bezier")
        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)
        algo_layout.addWidget(self.algorithm_combo)
        algo_layout.addStretch()
        layout.addLayout(algo_layout)

        group.setLayout(layout)
        return group

    def _create_algorithm_params(self):
        """Create algorithm-specific parameters group."""
        group = QGroupBox("Algorithm Parameters")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 15, 12, 12)

        # Bezier controls
        self.bezier_widget = QWidget()
        bezier_layout = QVBoxLayout()
        bezier_layout.setSpacing(8)
        bezier_layout.setContentsMargins(0, 0, 0, 0)

        strength_label = QLabel("Control Strength:")
        strength_label.setFont(QFont("Arial", 10))
        bezier_layout.addWidget(strength_label)
        self.bezier_slider = QSlider(Qt.Orientation.Horizontal)
        self.bezier_slider.setRange(10, 80)
        self.bezier_slider.setValue(40)
        self.bezier_slider.setMinimumHeight(25)
        self.bezier_slider.valueChanged.connect(self._on_bezier_changed)
        bezier_layout.addWidget(self.bezier_slider)

        self.bezier_value_label = QLabel("0.40")
        self.bezier_value_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.bezier_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bezier_layout.addWidget(self.bezier_value_label)

        self.bezier_widget.setLayout(bezier_layout)
        layout.addWidget(self.bezier_widget)

        # Fourier controls
        self.fourier_widget = QWidget()
        fourier_layout = QVBoxLayout()
        fourier_layout.setSpacing(8)
        fourier_layout.setContentsMargins(0, 0, 0, 0)

        wave_label = QLabel("Wave Count:")
        wave_label.setFont(QFont("Arial", 10))
        fourier_layout.addWidget(wave_label)
        self.fourier_waves_spin = QSpinBox()
        self.fourier_waves_spin.setFont(QFont("Arial", 11))
        self.fourier_waves_spin.setMinimumWidth(100)
        self.fourier_waves_spin.setMinimumHeight(35)
        self.fourier_waves_spin.setRange(1, 7)
        self.fourier_waves_spin.setValue(3)
        self.fourier_waves_spin.valueChanged.connect(self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_waves_spin)

        amp_label = QLabel("Amplitude:")
        amp_label.setFont(QFont("Arial", 10))
        fourier_layout.addWidget(amp_label)
        fourier_layout.addSpacing(5)
        self.fourier_amp_slider = QSlider(Qt.Orientation.Horizontal)
        self.fourier_amp_slider.setRange(5, 40)
        self.fourier_amp_slider.setValue(15)
        self.fourier_amp_slider.setMinimumHeight(25)
        self.fourier_amp_slider.valueChanged.connect(self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_amp_slider)

        self.fourier_amp_label = QLabel("0.15")
        self.fourier_amp_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.fourier_amp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fourier_layout.addWidget(self.fourier_amp_label)

        self.fourier_widget.setLayout(fourier_layout)
        self.fourier_widget.setVisible(False)
        layout.addWidget(self.fourier_widget)

        group.setLayout(layout)
        return group

    def _create_thickness_settings(self):
        """Create thickness settings group."""
        group = QGroupBox("Thickness")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 15, 12, 12)

        # Base thickness
        base_label = QLabel("Base:")
        base_label.setFont(QFont("Arial", 10))
        layout.addWidget(base_label)
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(10, 50)
        self.thickness_slider.setValue(25)
        self.thickness_slider.setMinimumHeight(25)
        self.thickness_slider.valueChanged.connect(self._on_thickness_changed)
        layout.addWidget(self.thickness_slider)

        self.thickness_value_label = QLabel("0.25")
        self.thickness_value_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.thickness_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.thickness_value_label)

        layout.addSpacing(10)

        # Taper
        taper_label = QLabel("Taper:")
        taper_label.setFont(QFont("Arial", 10))
        layout.addWidget(taper_label)
        self.taper_slider = QSlider(Qt.Orientation.Horizontal)
        self.taper_slider.setRange(0, 100)
        self.taper_slider.setValue(60)
        self.taper_slider.setMinimumHeight(25)
        self.taper_slider.valueChanged.connect(self._on_taper_changed)
        layout.addWidget(self.taper_slider)

        self.taper_value_label = QLabel("0.60")
        self.taper_value_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.taper_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.taper_value_label)

        group.setLayout(layout)
        return group

    def _create_branching_settings(self):
        """Create branching settings group."""
        group = QGroupBox("Branching")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 15, 12, 12)

        # Branch depth
        depth_layout = QHBoxLayout()
        depth_label = QLabel("Depth:")
        depth_label.setFont(QFont("Arial", 11))
        depth_label.setMinimumWidth(110)
        depth_layout.addWidget(depth_label)
        self.branch_depth_spin = QSpinBox()
        self.branch_depth_spin.setFont(QFont("Arial", 11))
        self.branch_depth_spin.setMinimumWidth(120)
        self.branch_depth_spin.setMinimumHeight(40)
        self.branch_depth_spin.setRange(0, 3)
        self.branch_depth_spin.setValue(self._branch_depth)
        self.branch_depth_spin.valueChanged.connect(self._on_branching_changed)
        depth_layout.addWidget(self.branch_depth_spin)
        depth_layout.addStretch()
        layout.addLayout(depth_layout)

        # Branch count
        count_layout = QHBoxLayout()
        count_label = QLabel("Count:")
        count_label.setFont(QFont("Arial", 11))
        count_label.setMinimumWidth(110)
        count_layout.addWidget(count_label)
        self.branch_count_spin = QSpinBox()
        self.branch_count_spin.setFont(QFont("Arial", 11))
        self.branch_count_spin.setMinimumWidth(120)
        self.branch_count_spin.setMinimumHeight(40)
        self.branch_count_spin.setRange(1, 3)
        self.branch_count_spin.setValue(self._branch_count)
        self.branch_count_spin.valueChanged.connect(self._on_branching_changed)
        count_layout.addWidget(self.branch_count_spin)
        count_layout.addStretch()
        layout.addLayout(count_layout)

        layout.addSpacing(5)

        # Info label showing estimated total
        self.branch_info_label = QLabel("Total: ~24 segments")
        self.branch_info_label.setFont(QFont("Arial", 10))
        self.branch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.branch_info_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.branch_info_label)

        group.setLayout(layout)
        return group

    def _create_presets(self):
        """Create presets group."""
        group = QGroupBox("Presets")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 15, 12, 12)

        # Preset buttons (use imported PRESETS from constants)
        for name, algo, params in PRESETS:
            btn = QPushButton(name)
            btn.setFont(QFont("Arial", 10))
            btn.setMinimumHeight(32)
            btn.clicked.connect(lambda checked, a=algo, p=params: self._load_preset(a, p))
            layout.addWidget(btn)

        group.setLayout(layout)
        return group

    def _create_actions(self):
        """Create action buttons."""
        group = QGroupBox("Actions")
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 15, 12, 12)

        # Undo/Redo
        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.setSpacing(10)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setFont(QFont("Arial", 10))
        self.undo_btn.setMinimumHeight(32)
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        self.undo_btn.setEnabled(False)
        undo_redo_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("Redo")
        self.redo_btn.setFont(QFont("Arial", 10))
        self.redo_btn.setMinimumHeight(32)
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        self.redo_btn.setEnabled(False)
        undo_redo_layout.addWidget(self.redo_btn)

        layout.addLayout(undo_redo_layout)

        # Export
        self.export_btn = QPushButton("Export JSON")
        self.export_btn.setFont(QFont("Arial", 10))
        self.export_btn.setMinimumHeight(32)
        self.export_btn.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.export_btn)

        group.setLayout(layout)
        return group

    # Getters for current state
    def get_state(self):
        """Get current creature parameters as dict."""
        return {
            'num_tentacles': self._num_tentacles,
            'segments': self._segments,
            'algorithm': self._algorithm,
            'params': self.get_algorithm_params(),
            'thickness_base': self._thickness_base,
            'taper_factor': self._taper_factor,
            'branch_depth': self._branch_depth,
            'branch_count': self._branch_count
        }

    def get_algorithm_params(self):
        """Get parameters for current algorithm."""
        if self._algorithm == 'bezier':
            return {'control_strength': self._bezier_control_strength}
        else:
            return {
                'num_waves': self._fourier_waves,
                'amplitude': self._fourier_amplitude
            }

    # Setters for restoring state (e.g., undo/redo)
    def set_state(self, state):
        """Restore state from dict (for undo/redo)."""
        self._updating = True

        self._num_tentacles = state['num_tentacles']
        self._segments = state['segments']
        self._algorithm = state['algorithm']
        self._thickness_base = state['thickness_base']
        self._taper_factor = state['taper_factor']
        self._branch_depth = state.get('branch_depth', 0)
        self._branch_count = state.get('branch_count', 1)

        # Update UI widgets
        self.tentacles_spin.setValue(self._num_tentacles)
        self.segments_spin.setValue(self._segments)
        self.algorithm_combo.setCurrentText(self._algorithm.capitalize())
        self.thickness_slider.setValue(int(self._thickness_base * 100))
        self.taper_slider.setValue(int(self._taper_factor * 100))
        self.branch_depth_spin.setValue(self._branch_depth)
        self.branch_count_spin.setValue(self._branch_count)

        # Update algorithm params
        params = state['params']
        if self._algorithm == 'bezier':
            self._bezier_control_strength = params.get('control_strength', 0.4)
            self.bezier_slider.setValue(int(self._bezier_control_strength * 100))
        else:
            self._fourier_waves = params.get('num_waves', 3)
            self._fourier_amplitude = params.get('amplitude', 0.15)
            self.fourier_waves_spin.setValue(self._fourier_waves)
            self.fourier_amp_slider.setValue(int(self._fourier_amplitude * 100))

        # Update branch info
        self._update_branch_info()

        self._updating = False
        self.creature_changed.emit()

    def set_undo_redo_enabled(self, can_undo, can_redo):
        """Update undo/redo button states."""
        self.undo_btn.setEnabled(can_undo)
        self.redo_btn.setEnabled(can_redo)

    # Event handlers
    def _on_tentacles_changed(self, value):
        """Handle tentacle count change."""
        if not self._updating:
            self._num_tentacles = value
            self._update_branch_info()
            self.creature_changed.emit()

    def _on_segments_changed(self, value):
        """Handle segment count change."""
        if not self._updating:
            self._segments = value
            self._update_branch_info()
            self.creature_changed.emit()

    def _on_algorithm_changed(self, text):
        """Handle algorithm change."""
        if not self._updating:
            self._algorithm = text.lower()

            # Show/hide appropriate parameter widgets
            self.bezier_widget.setVisible(self._algorithm == 'bezier')
            self.fourier_widget.setVisible(self._algorithm == 'fourier')

            self.creature_changed.emit()

    def _on_bezier_changed(self, value):
        """Handle Bezier parameter change."""
        if not self._updating:
            self._bezier_control_strength = value / 100.0
            self.bezier_value_label.setText(f"{self._bezier_control_strength:.2f}")
            self.creature_changed.emit()

    def _on_fourier_changed(self):
        """Handle Fourier parameter change."""
        if not self._updating:
            self._fourier_waves = self.fourier_waves_spin.value()
            self._fourier_amplitude = self.fourier_amp_slider.value() / 100.0
            self.fourier_amp_label.setText(f"{self._fourier_amplitude:.2f}")
            self.creature_changed.emit()

    def _on_thickness_changed(self, value):
        """Handle thickness change."""
        if not self._updating:
            self._thickness_base = value / 100.0
            self.thickness_value_label.setText(f"{self._thickness_base:.2f}")
            self.creature_changed.emit()

    def _on_taper_changed(self, value):
        """Handle taper change."""
        if not self._updating:
            self._taper_factor = value / 100.0
            self.taper_value_label.setText(f"{self._taper_factor:.2f}")
            self.creature_changed.emit()

    def _on_branching_changed(self):
        """Handle branching parameter change."""
        if not self._updating:
            self._branch_depth = self.branch_depth_spin.value()
            self._branch_count = self.branch_count_spin.value()
            self._update_branch_info()
            self.creature_changed.emit()

    def _update_branch_info(self):
        """Update the branch info label with total segment estimate."""
        # Calculate total tentacles using geometric series
        # For depth d and count c: total = 1 + c + c² + ... + c^d = (c^(d+1) - 1) / (c - 1)
        if self._branch_count == 1:
            branches_per_main = self._branch_depth + 1
        else:
            branches_per_main = (self._branch_count ** (self._branch_depth + 1) - 1) // (self._branch_count - 1)

        total_tentacles = self._num_tentacles * branches_per_main
        total_segments = total_tentacles * self._segments

        self.branch_info_label.setText(f"Total: ~{total_segments} segments")

    def _load_preset(self, algorithm, params):
        """Load a preset configuration."""
        self._updating = True

        self._algorithm = algorithm
        self.algorithm_combo.setCurrentText(algorithm.capitalize())

        if algorithm == 'bezier':
            self._bezier_control_strength = params['control_strength']
            self.bezier_slider.setValue(int(self._bezier_control_strength * 100))
            self.bezier_widget.setVisible(True)
            self.fourier_widget.setVisible(False)
        else:
            self._fourier_waves = params['num_waves']
            self._fourier_amplitude = params['amplitude']
            self.fourier_waves_spin.setValue(self._fourier_waves)
            self.fourier_amp_slider.setValue(int(self._fourier_amplitude * 100))
            self.bezier_widget.setVisible(False)
            self.fourier_widget.setVisible(True)

        self._updating = False
        self.creature_changed.emit()
