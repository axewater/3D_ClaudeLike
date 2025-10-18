"""Tentacle creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QSlider, QSpinBox, QComboBox, QWidget
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton, SPINBOX_STYLE, COMBOBOX_STYLE


class TentaclePanel(BaseCreaturePanel):
    """Control panel for tentacle creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize tentacle-specific state variables
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
        self._body_scale = 1.2
        self._tentacle_color = (0.6, 0.3, 0.7)
        self._hue_shift = 0.1
        self._anim_speed = 2.0
        self._wave_amplitude = 0.05
        self._pulse_speed = 1.5
        self._pulse_amount = 0.05
        self._num_eyes = 3
        self._eye_size_min = 0.1
        self._eye_size_max = 0.25
        self._eyeball_color = (1.0, 1.0, 1.0)
        self._pupil_color = (0.0, 0.0, 0.0)

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Shape & Algorithm
        layout.addWidget(self._create_shape_section(), 0, 0)

        # Column 2: Appearance
        layout.addWidget(self._create_appearance_section(), 0, 1)

        # Column 3: Branching
        layout.addWidget(self._create_branching_section(), 0, 2)

        # Row 2: Eyes section (full width, spanning 3 columns)
        layout.addWidget(self._create_eyes_section(), 1, 0, 1, 3)

        self.setLayout(layout)

    def _create_shape_section(self):
        """Create Shape & Algorithm card."""
        group = self._create_card("SHAPE & ALGORITHM")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Tentacles
        layout.addWidget(self._create_label("Tentacles"))
        self.tentacles_spin = self._create_spinbox(1, 12, self._num_tentacles, self._on_tentacles_changed)
        layout.addWidget(self.tentacles_spin)
        layout.addSpacing(8)

        # Segments
        layout.addWidget(self._create_label("Segments"))
        self.segments_spin = self._create_spinbox(5, 20, self._segments, self._on_segments_changed)
        layout.addWidget(self.segments_spin)
        layout.addSpacing(8)

        # Algorithm
        layout.addWidget(self._create_label("Algorithm"))
        self.algorithm_combo = self._create_combobox(["Bezier", "Fourier"], self._on_algorithm_changed)
        layout.addWidget(self.algorithm_combo)
        layout.addSpacing(8)

        # Bezier controls
        self.bezier_widget = QWidget()
        bezier_layout = QVBoxLayout()
        bezier_layout.setContentsMargins(0, 10, 0, 0)
        bezier_layout.addWidget(self._create_label("Control Strength"))
        self.bezier_slider = self._create_slider(10, 80, 40, self._on_bezier_changed)
        bezier_layout.addWidget(self.bezier_slider)
        self.bezier_value_label = QLabel("0.40")
        self.bezier_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bezier_value_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        bezier_layout.addWidget(self.bezier_value_label)
        self.bezier_widget.setLayout(bezier_layout)
        layout.addWidget(self.bezier_widget)

        # Fourier controls
        self.fourier_widget = QWidget()
        fourier_layout = QVBoxLayout()
        fourier_layout.setContentsMargins(0, 10, 0, 0)
        fourier_layout.addWidget(self._create_label("Wave Count"))
        self.fourier_waves_spin = self._create_spinbox(1, 7, 3, self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_waves_spin)
        fourier_layout.addSpacing(8)
        fourier_layout.addWidget(self._create_label("Amplitude"))
        self.fourier_amp_slider = self._create_slider(5, 40, 15, self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_amp_slider)
        self.fourier_amp_label = QLabel("0.15")
        self.fourier_amp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fourier_amp_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        fourier_layout.addWidget(self.fourier_amp_label)
        self.fourier_widget.setLayout(fourier_layout)
        self.fourier_widget.setVisible(False)
        layout.addWidget(self.fourier_widget)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_appearance_section(self):
        """Create Appearance card."""
        group = self._create_card("APPEARANCE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Tentacle Color
        layout.addWidget(self._create_label("Base Color"))
        self.color_button = ColorButton(self._tentacle_color)
        self.color_button.colorChanged.connect(self._on_color_changed)
        layout.addWidget(self.color_button)

        # Hue Shift
        layout.addWidget(self._create_label("Color Variation"))
        self.hue_slider = self._create_slider(0, 30, int(self._hue_shift * 100), self._on_hue_changed)
        layout.addWidget(self.hue_slider)
        self.hue_label = QLabel("0.10")
        self.hue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hue_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.hue_label)

        # Thickness
        layout.addWidget(self._create_label("Base Thickness"))
        self.thickness_slider = self._create_slider(10, 50, 25, self._on_thickness_changed)
        layout.addWidget(self.thickness_slider)
        self.thickness_label = QLabel("0.25")
        self.thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thickness_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.thickness_label)

        # Taper
        layout.addWidget(self._create_label("Taper"))
        self.taper_slider = self._create_slider(0, 100, 60, self._on_taper_changed)
        layout.addWidget(self.taper_slider)
        self.taper_label = QLabel("0.60")
        self.taper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taper_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.taper_label)

        # Body Scale
        layout.addWidget(self._create_label("Body Size"))
        self.body_scale_slider = self._create_slider(50, 200, 120, self._on_body_scale_changed)
        layout.addWidget(self.body_scale_slider)
        self.body_scale_label = QLabel("1.20")
        self.body_scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_scale_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.body_scale_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_branching_section(self):
        """Create Branching card."""
        group = self._create_card("BRANCHING")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Depth
        layout.addWidget(self._create_label("Depth"))
        self.branch_depth_spin = self._create_spinbox(0, 3, self._branch_depth, self._on_branching_changed)
        layout.addWidget(self.branch_depth_spin)
        layout.addSpacing(8)

        # Count
        layout.addWidget(self._create_label("Count Per Level"))
        self.branch_count_spin = self._create_spinbox(1, 3, self._branch_count, self._on_branching_changed)
        layout.addWidget(self.branch_count_spin)
        layout.addSpacing(8)

        # Info
        self.branch_info_label = QLabel("Total: ~24 segments")
        self.branch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.branch_info_label.setStyleSheet("color: #06b6d4; font-size: 11pt; font-weight: bold; padding: 12px; background-color: #164e63; border-radius: 8px; margin-top: 10px; border: 1px solid #0891b2;")
        layout.addWidget(self.branch_info_label)
        self._update_branch_info()

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_eyes_section(self):
        """Create Eyes card (full width)."""
        group = self._create_card("EYES")
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)

        # Num Eyes
        eyes_layout = QVBoxLayout()
        eyes_layout.addWidget(self._create_label("Number of Eyes"))
        self.num_eyes_spin = self._create_spinbox(0, 12, self._num_eyes, self._on_num_eyes_changed)
        eyes_layout.addWidget(self.num_eyes_spin)
        layout.addLayout(eyes_layout)

        # Min Eye Size
        min_size_layout = QVBoxLayout()
        min_size_layout.addWidget(self._create_label("Min Size"))
        self.eye_size_min_slider = self._create_slider(5, 50, 10, self._on_eye_size_changed)
        min_size_layout.addWidget(self.eye_size_min_slider)
        self.eye_size_min_label = QLabel("0.10")
        self.eye_size_min_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eye_size_min_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        min_size_layout.addWidget(self.eye_size_min_label)
        layout.addLayout(min_size_layout)

        # Max Eye Size
        max_size_layout = QVBoxLayout()
        max_size_layout.addWidget(self._create_label("Max Size"))
        self.eye_size_max_slider = self._create_slider(5, 50, 25, self._on_eye_size_changed)
        max_size_layout.addWidget(self.eye_size_max_slider)
        self.eye_size_max_label = QLabel("0.25")
        self.eye_size_max_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eye_size_max_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        max_size_layout.addWidget(self.eye_size_max_label)
        layout.addLayout(max_size_layout)

        # Eyeball Color
        eyeball_color_layout = QVBoxLayout()
        eyeball_color_layout.addWidget(self._create_label("Eyeball Color"))
        self.eyeball_color_button = ColorButton(self._eyeball_color)
        self.eyeball_color_button.colorChanged.connect(self._on_eyeball_color_changed)
        eyeball_color_layout.addWidget(self.eyeball_color_button)
        layout.addLayout(eyeball_color_layout)

        # Pupil Color
        pupil_color_layout = QVBoxLayout()
        pupil_color_layout.addWidget(self._create_label("Pupil Color"))
        self.pupil_color_button = ColorButton(self._pupil_color)
        self.pupil_color_button.colorChanged.connect(self._on_pupil_color_changed)
        pupil_color_layout.addWidget(self.pupil_color_button)
        layout.addLayout(pupil_color_layout)

        group.setLayout(layout)
        return group

    # Event Handlers
    def _on_tentacles_changed(self, value):
        self._num_tentacles = value
        self._update_branch_info()
        self._emit_change()

    def _on_segments_changed(self, value):
        self._segments = value
        self._update_branch_info()
        self._emit_change()

    def _on_algorithm_changed(self, text):
        self._algorithm = text.lower()
        self.bezier_widget.setVisible(self._algorithm == 'bezier')
        self.fourier_widget.setVisible(self._algorithm == 'fourier')
        self._emit_change()

    def _on_bezier_changed(self, value):
        self._bezier_control_strength = value / 100.0
        self.bezier_value_label.setText(f"{self._bezier_control_strength:.2f}")
        self._emit_change()

    def _on_fourier_changed(self):
        self._fourier_waves = self.fourier_waves_spin.value()
        self._fourier_amplitude = self.fourier_amp_slider.value() / 100.0
        self.fourier_amp_label.setText(f"{self._fourier_amplitude:.2f}")
        self._emit_change()

    def _on_thickness_changed(self, value):
        self._thickness_base = value / 100.0
        self.thickness_label.setText(f"{self._thickness_base:.2f}")
        self._emit_change()

    def _on_taper_changed(self, value):
        self._taper_factor = value / 100.0
        self.taper_label.setText(f"{self._taper_factor:.2f}")
        self._emit_change()

    def _on_color_changed(self, rgb_tuple):
        self._tentacle_color = rgb_tuple
        self._emit_change()

    def _on_hue_changed(self, value):
        self._hue_shift = value / 100.0
        self.hue_label.setText(f"{self._hue_shift:.2f}")
        self._emit_change()

    def _on_body_scale_changed(self, value):
        self._body_scale = value / 100.0
        self.body_scale_label.setText(f"{self._body_scale:.2f}")
        self._emit_change()

    def _on_branching_changed(self):
        self._branch_depth = self.branch_depth_spin.value()
        self._branch_count = self.branch_count_spin.value()
        self._update_branch_info()
        self._emit_change()

    def _on_num_eyes_changed(self, value):
        self._num_eyes = value
        self._emit_change()

    def _on_eye_size_changed(self):
        self._eye_size_min = self.eye_size_min_slider.value() / 100.0
        self._eye_size_max = self.eye_size_max_slider.value() / 100.0
        self.eye_size_min_label.setText(f"{self._eye_size_min:.2f}")
        self.eye_size_max_label.setText(f"{self._eye_size_max:.2f}")
        self._emit_change()

    def _on_eyeball_color_changed(self, rgb_tuple):
        self._eyeball_color = rgb_tuple
        self._emit_change()

    def _on_pupil_color_changed(self, rgb_tuple):
        self._pupil_color = rgb_tuple
        self._emit_change()

    def _update_branch_info(self):
        """Update branch info label."""
        if self._branch_count == 1:
            branches_per_main = self._branch_depth + 1
        else:
            branches_per_main = (self._branch_count ** (self._branch_depth + 1) - 1) // (self._branch_count - 1)

        total_tentacles = self._num_tentacles * branches_per_main
        total_segments = total_tentacles * self._segments
        self.branch_info_label.setText(f"Total: ~{total_segments} segments")

    def get_state(self):
        """Get current state."""
        return {
            'num_tentacles': self._num_tentacles,
            'segments': self._segments,
            'algorithm': self._algorithm,
            'params': self._get_algorithm_params(),
            'thickness_base': self._thickness_base,
            'taper_factor': self._taper_factor,
            'branch_depth': self._branch_depth,
            'branch_count': self._branch_count,
            'body_scale': self._body_scale,
            'tentacle_color': self._tentacle_color,
            'hue_shift': self._hue_shift,
            'anim_speed': self._anim_speed,
            'wave_amplitude': self._wave_amplitude,
            'pulse_speed': self._pulse_speed,
            'pulse_amount': self._pulse_amount,
            'num_eyes': self._num_eyes,
            'eye_size_min': self._eye_size_min,
            'eye_size_max': self._eye_size_max,
            'eyeball_color': self._eyeball_color,
            'pupil_color': self._pupil_color,
        }

    def _get_algorithm_params(self):
        """Get algorithm parameters."""
        if self._algorithm == 'bezier':
            return {'control_strength': self._bezier_control_strength}
        else:
            return {
                'num_waves': self._fourier_waves,
                'amplitude': self._fourier_amplitude
            }

    def set_state(self, state):
        """Restore state."""
        self._updating = True

        # Tentacle parameters
        self._num_tentacles = state.get('num_tentacles', 2)
        self._segments = state.get('segments', 12)
        self._algorithm = state.get('algorithm', 'bezier')
        self._thickness_base = state.get('thickness_base', 0.25)
        self._taper_factor = state.get('taper_factor', 0.6)
        self._branch_depth = state.get('branch_depth', 0)
        self._branch_count = state.get('branch_count', 1)
        self._body_scale = state.get('body_scale', 1.2)
        self._tentacle_color = state.get('tentacle_color', (0.6, 0.3, 0.7))
        self._hue_shift = state.get('hue_shift', 0.1)
        self._anim_speed = state.get('anim_speed', 2.0)
        self._wave_amplitude = state.get('wave_amplitude', 0.05)
        self._pulse_speed = state.get('pulse_speed', 1.5)
        self._pulse_amount = state.get('pulse_amount', 0.05)
        self._num_eyes = state.get('num_eyes', 3)
        self._eye_size_min = state.get('eye_size_min', 0.1)
        self._eye_size_max = state.get('eye_size_max', 0.25)
        self._eyeball_color = state.get('eyeball_color', (1.0, 1.0, 1.0))
        self._pupil_color = state.get('pupil_color', (0.0, 0.0, 0.0))

        # Algorithm params
        params = state.get('params', {})
        if self._algorithm == 'bezier':
            self._bezier_control_strength = params.get('control_strength', 0.4)
        else:
            self._fourier_waves = params.get('num_waves', 3)
            self._fourier_amplitude = params.get('amplitude', 0.15)

        # Update UI
        self.tentacles_spin.setValue(self._num_tentacles)
        self.segments_spin.setValue(self._segments)
        self.algorithm_combo.setCurrentText(self._algorithm.capitalize())
        self.thickness_slider.setValue(int(self._thickness_base * 100))
        self.taper_slider.setValue(int(self._taper_factor * 100))
        self.branch_depth_spin.setValue(self._branch_depth)
        self.branch_count_spin.setValue(self._branch_count)
        self.body_scale_slider.setValue(int(self._body_scale * 100))
        self.color_button.set_color(self._tentacle_color)
        self.hue_slider.setValue(int(self._hue_shift * 100))
        self.num_eyes_spin.setValue(self._num_eyes)
        self.eye_size_min_slider.setValue(int(self._eye_size_min * 100))
        self.eye_size_max_slider.setValue(int(self._eye_size_max * 100))
        self.eyeball_color_button.set_color(self._eyeball_color)
        self.pupil_color_button.set_color(self._pupil_color)

        if self._algorithm == 'bezier':
            self.bezier_slider.setValue(int(self._bezier_control_strength * 100))
        else:
            self.fourier_waves_spin.setValue(self._fourier_waves)
            self.fourier_amp_slider.setValue(int(self._fourier_amplitude * 100))

        self._update_branch_info()
        self._updating = False
