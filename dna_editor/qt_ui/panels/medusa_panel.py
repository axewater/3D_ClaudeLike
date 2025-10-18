"""Medusa creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QWidget
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton


class MedusaPanel(BaseCreaturePanel):
    """Control panel for medusa creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize medusa-specific state variables (based on MedusaCreature.__init__)
        self._num_tentacles = 8
        self._segments_per_tentacle = 16
        self._algorithm = 'fourier'
        self._bezier_control_strength = 0.4
        self._fourier_waves = 3
        self._fourier_amplitude = 0.15
        self._thickness_base = 0.25
        self._taper_factor = 0.6
        self._body_scale = 1.0
        self._tentacle_color = (0.4, 0.2, 0.6)  # RGB 0-1
        self._hue_shift = 0.08
        self._anim_speed = 1.5
        self._wave_amplitude = 0.08
        self._pulse_speed = 1.2
        self._pulse_amount = 0.06
        self._eye_size = 0.18
        self._eyeball_color = (1.0, 0.95, 0.85)  # RGB 0-1
        self._pupil_color = (0.1, 0.0, 0.2)  # RGB 0-1

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

        # Column 3: Animation
        layout.addWidget(self._create_animation_section(), 0, 2)

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
        self.tentacles_spin = self._create_spinbox(4, 12, self._num_tentacles, self._on_tentacles_changed)
        layout.addWidget(self.tentacles_spin)
        layout.addSpacing(8)

        # Segments
        layout.addWidget(self._create_label("Segments"))
        self.segments_spin = self._create_spinbox(12, 20, self._segments_per_tentacle, self._on_segments_changed)
        layout.addWidget(self.segments_spin)
        layout.addSpacing(8)

        # Algorithm
        layout.addWidget(self._create_label("Algorithm"))
        self.algorithm_combo = self._create_combobox(["Bezier", "Fourier"], self._on_algorithm_changed)
        self.algorithm_combo.setCurrentText("Fourier")  # Default to Fourier
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
        self.bezier_widget.setVisible(False)  # Hidden initially (Fourier is default)
        layout.addWidget(self.bezier_widget)

        # Fourier controls
        self.fourier_widget = QWidget()
        fourier_layout = QVBoxLayout()
        fourier_layout.setContentsMargins(0, 10, 0, 0)
        fourier_layout.addWidget(self._create_label("Wave Count"))
        self.fourier_waves_spin = self._create_spinbox(1, 7, self._fourier_waves, self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_waves_spin)
        fourier_layout.addSpacing(5)
        fourier_layout.addWidget(self._create_label("Amplitude"))
        self.fourier_amp_slider = self._create_slider(5, 40, 15, self._on_fourier_changed)
        fourier_layout.addWidget(self.fourier_amp_slider)
        self.fourier_amp_label = QLabel("0.15")
        self.fourier_amp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fourier_amp_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        fourier_layout.addWidget(self.fourier_amp_label)
        self.fourier_widget.setLayout(fourier_layout)
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

        # Body Scale (0.5-2.0)
        layout.addWidget(self._create_label("Body Size"))
        self.body_scale_slider = self._create_slider(50, 200, 100, self._on_body_scale_changed)
        layout.addWidget(self.body_scale_slider)
        self.body_scale_label = QLabel("1.0x")
        self.body_scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_scale_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.body_scale_label)
        layout.addSpacing(8)

        # Tentacle Color
        layout.addWidget(self._create_label("Tentacle Color"))
        self.tentacle_color_button = ColorButton(self._tentacle_color)
        self.tentacle_color_button.colorChanged.connect(self._on_tentacle_color_changed)
        layout.addWidget(self.tentacle_color_button)
        layout.addSpacing(8)

        # Hue Shift (0.0-0.2)
        layout.addWidget(self._create_label("Color Variation"))
        self.hue_shift_slider = self._create_slider(0, 20, 8, self._on_hue_shift_changed)
        layout.addWidget(self.hue_shift_slider)
        self.hue_shift_label = QLabel("0.08")
        self.hue_shift_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hue_shift_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.hue_shift_label)
        layout.addSpacing(8)

        # Thickness Base (0.1-0.5)
        layout.addWidget(self._create_label("Thickness"))
        self.thickness_slider = self._create_slider(10, 50, 25, self._on_thickness_changed)
        layout.addWidget(self.thickness_slider)
        self.thickness_label = QLabel("0.25")
        self.thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thickness_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.thickness_label)
        layout.addSpacing(8)

        # Taper Factor (0.0-1.0)
        layout.addWidget(self._create_label("Taper"))
        self.taper_slider = self._create_slider(0, 100, 60, self._on_taper_changed)
        layout.addWidget(self.taper_slider)
        self.taper_label = QLabel("0.60")
        self.taper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taper_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.taper_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_animation_section(self):
        """Create Animation card."""
        group = self._create_card("ANIMATION")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Animation Speed (0.5-5.0)
        layout.addWidget(self._create_label("Wave Speed"))
        self.anim_speed_slider = self._create_slider(50, 500, 150, self._on_anim_speed_changed)
        layout.addWidget(self.anim_speed_slider)
        self.anim_speed_label = QLabel("1.5x")
        self.anim_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.anim_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.anim_speed_label)
        layout.addSpacing(8)

        # Wave Amplitude (0.0-0.2)
        layout.addWidget(self._create_label("Wave Intensity"))
        self.wave_amp_slider = self._create_slider(0, 20, 8, self._on_wave_amp_changed)
        layout.addWidget(self.wave_amp_slider)
        self.wave_amp_label = QLabel("0.08")
        self.wave_amp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wave_amp_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.wave_amp_label)
        layout.addSpacing(8)

        # Pulse Speed (0.5-3.0)
        layout.addWidget(self._create_label("Pulse Speed"))
        self.pulse_speed_slider = self._create_slider(50, 300, 120, self._on_pulse_speed_changed)
        layout.addWidget(self.pulse_speed_slider)
        self.pulse_speed_label = QLabel("1.2x")
        self.pulse_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pulse_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.pulse_speed_label)
        layout.addSpacing(8)

        # Pulse Amount (0.0-0.15)
        layout.addWidget(self._create_label("Pulse Amount"))
        self.pulse_amt_slider = self._create_slider(0, 15, 6, self._on_pulse_amt_changed)
        layout.addWidget(self.pulse_amt_slider)
        self.pulse_amt_label = QLabel("0.06")
        self.pulse_amt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pulse_amt_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.pulse_amt_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_eyes_section(self):
        """Create Eyes card (full width)."""
        group = self._create_card("TENTACLE TIP EYES")
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)

        # Eye Size (0.1-0.3)
        eye_size_layout = QVBoxLayout()
        eye_size_layout.addWidget(self._create_label("Eye Size"))
        self.eye_size_slider = self._create_slider(10, 30, 18, self._on_eye_size_changed)
        eye_size_layout.addWidget(self.eye_size_slider)
        self.eye_size_label = QLabel("0.18")
        self.eye_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eye_size_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        eye_size_layout.addWidget(self.eye_size_label)
        layout.addLayout(eye_size_layout)

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
        self._emit_change()

    def _on_segments_changed(self, value):
        self._segments_per_tentacle = value
        self._emit_change()

    def _on_algorithm_changed(self, text):
        self._algorithm = text.lower()
        # Show/hide appropriate parameter widgets (only if they exist)
        if hasattr(self, 'bezier_widget'):
            self.bezier_widget.setVisible(self._algorithm == 'bezier')
        if hasattr(self, 'fourier_widget'):
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

    def _on_body_scale_changed(self, value):
        self._body_scale = value / 100.0
        self.body_scale_label.setText(f"{self._body_scale:.1f}x")
        self._emit_change()

    def _on_tentacle_color_changed(self, color):
        self._tentacle_color = color  # Already in 0-1 range
        self._emit_change()

    def _on_hue_shift_changed(self, value):
        self._hue_shift = value / 100.0
        self.hue_shift_label.setText(f"{self._hue_shift:.2f}")
        self._emit_change()

    def _on_thickness_changed(self, value):
        self._thickness_base = value / 100.0
        self.thickness_label.setText(f"{self._thickness_base:.2f}")
        self._emit_change()

    def _on_taper_changed(self, value):
        self._taper_factor = value / 100.0
        self.taper_label.setText(f"{self._taper_factor:.2f}")
        self._emit_change()

    def _on_anim_speed_changed(self, value):
        self._anim_speed = value / 100.0
        self.anim_speed_label.setText(f"{self._anim_speed:.1f}x")
        self._emit_change()

    def _on_wave_amp_changed(self, value):
        self._wave_amplitude = value / 100.0
        self.wave_amp_label.setText(f"{self._wave_amplitude:.2f}")
        self._emit_change()

    def _on_pulse_speed_changed(self, value):
        self._pulse_speed = value / 100.0
        self.pulse_speed_label.setText(f"{self._pulse_speed:.1f}x")
        self._emit_change()

    def _on_pulse_amt_changed(self, value):
        self._pulse_amount = value / 100.0
        self.pulse_amt_label.setText(f"{self._pulse_amount:.2f}")
        self._emit_change()

    def _on_eye_size_changed(self, value):
        self._eye_size = value / 100.0
        self.eye_size_label.setText(f"{self._eye_size:.2f}")
        self._emit_change()

    def _on_eyeball_color_changed(self, color):
        self._eyeball_color = color  # Already in 0-1 range
        self._emit_change()

    def _on_pupil_color_changed(self, color):
        self._pupil_color = color  # Already in 0-1 range
        self._emit_change()

    def get_state(self):
        """Get current state."""
        return {
            'num_tentacles': self._num_tentacles,
            'segments_per_tentacle': self._segments_per_tentacle,
            'algorithm': self._algorithm,
            'algorithm_params': self._get_algorithm_params(),
            'params': self._get_algorithm_params(),  # Also export as 'params' for compatibility
            'segments': self._segments_per_tentacle,  # Also export as 'segments' for compatibility
            'thickness_base': self._thickness_base,
            'taper_factor': self._taper_factor,
            'body_scale': self._body_scale,
            'tentacle_color': self._tentacle_color,
            'hue_shift': self._hue_shift,
            'anim_speed': self._anim_speed,
            'wave_amplitude': self._wave_amplitude,
            'pulse_speed': self._pulse_speed,
            'pulse_amount': self._pulse_amount,
            'eye_size': self._eye_size,
            'eye_size_max': self._eye_size,  # Export as eye_size_max for renderer compatibility
            'eyeball_color': self._eyeball_color,
            'pupil_color': self._pupil_color,
        }

    def _get_algorithm_params(self):
        """Get parameters for current algorithm."""
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

        # Medusa parameters
        self._num_tentacles = state.get('num_tentacles', 8)
        self._segments_per_tentacle = state.get('segments_per_tentacle', 16)
        self._algorithm = state.get('algorithm', 'fourier')
        algorithm_params = state.get('algorithm_params', {})
        self._bezier_control_strength = algorithm_params.get('control_strength', 0.4)
        self._fourier_waves = algorithm_params.get('num_waves', 3)
        self._fourier_amplitude = algorithm_params.get('amplitude', 0.15)
        self._thickness_base = state.get('thickness_base', 0.25)
        self._taper_factor = state.get('taper_factor', 0.6)
        self._body_scale = state.get('body_scale', 1.0)
        self._tentacle_color = state.get('tentacle_color', (0.4, 0.2, 0.6))
        self._hue_shift = state.get('hue_shift', 0.08)
        self._anim_speed = state.get('anim_speed', 1.5)
        self._wave_amplitude = state.get('wave_amplitude', 0.08)
        self._pulse_speed = state.get('pulse_speed', 1.2)
        self._pulse_amount = state.get('pulse_amount', 0.06)
        self._eye_size = state.get('eye_size', 0.18)
        self._eyeball_color = state.get('eyeball_color', (1.0, 0.95, 0.85))
        self._pupil_color = state.get('pupil_color', (0.1, 0.0, 0.2))

        # Update UI
        self.tentacles_spin.setValue(self._num_tentacles)
        self.segments_spin.setValue(self._segments_per_tentacle)
        self.algorithm_combo.setCurrentText(self._algorithm.capitalize())
        self.bezier_slider.setValue(int(self._bezier_control_strength * 100))
        self.fourier_waves_spin.setValue(self._fourier_waves)
        self.fourier_amp_slider.setValue(int(self._fourier_amplitude * 100))
        self.thickness_slider.setValue(int(self._thickness_base * 100))
        self.taper_slider.setValue(int(self._taper_factor * 100))
        self.body_scale_slider.setValue(int(self._body_scale * 100))
        self.tentacle_color_button.set_color(self._tentacle_color)
        self.hue_shift_slider.setValue(int(self._hue_shift * 100))
        self.anim_speed_slider.setValue(int(self._anim_speed * 100))
        self.wave_amp_slider.setValue(int(self._wave_amplitude * 100))
        self.pulse_speed_slider.setValue(int(self._pulse_speed * 100))
        self.pulse_amt_slider.setValue(int(self._pulse_amount * 100))
        self.eye_size_slider.setValue(int(self._eye_size * 100))
        self.eyeball_color_button.set_color(self._eyeball_color)
        self.pupil_color_button.set_color(self._pupil_color)

        # Show/hide algorithm widgets
        self.bezier_widget.setVisible(self._algorithm == 'bezier')
        self.fourier_widget.setVisible(self._algorithm == 'fourier')

        self._updating = False
