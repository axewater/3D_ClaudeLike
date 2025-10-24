"""Starfish creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QGroupBox, QLabel
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton


class StarfishPanel(BaseCreaturePanel):
    """Control panel for starfish creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize starfish-specific state variables
        self._num_arms = 5
        self._arm_segments = 6
        self._central_body_size = 0.8
        self._arm_base_thickness = 0.4
        self._starfish_color = (0.9, 0.5, 0.3)  # Orange
        self._curl_factor = 0.3
        self._starfish_anim_speed = 1.5
        self._starfish_pulse = 0.06

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Arms & Body
        layout.addWidget(self._create_starfish_arms_section(), 0, 0)

        # Column 2: Appearance
        layout.addWidget(self._create_starfish_appearance_section(), 0, 1)

        # Column 3: Animation
        layout.addWidget(self._create_starfish_animation_section(), 0, 2)

        self.setLayout(layout)

    def _create_starfish_arms_section(self):
        """Create Starfish Arms & Body card."""
        group = self._create_card("ARMS & BODY")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Number of Arms (5-8)
        layout.addWidget(self._create_label("Number of Arms"))
        self.num_arms_spin = self._create_spinbox(5, 8, self._num_arms, self._on_num_arms_changed)
        layout.addWidget(self.num_arms_spin)
        layout.addSpacing(8)

        # Arm Segments (4-10)
        layout.addWidget(self._create_label("Segments Per Arm"))
        self.arm_segments_spin = self._create_spinbox(4, 10, self._arm_segments, self._on_arm_segments_changed)
        layout.addWidget(self.arm_segments_spin)
        layout.addSpacing(8)

        # Central Body Size (0.4-1.5)
        layout.addWidget(self._create_label("Central Body Size"))
        self.central_body_slider = self._create_slider(40, 150, 80, self._on_central_body_changed)
        layout.addWidget(self.central_body_slider)
        self.central_body_label = QLabel("0.80")
        self.central_body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_body_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.central_body_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_starfish_appearance_section(self):
        """Create Starfish Appearance card."""
        group = self._create_card("APPEARANCE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Starfish Color
        layout.addWidget(self._create_label("Starfish Color"))
        self.starfish_color_button = ColorButton(self._starfish_color)
        self.starfish_color_button.colorChanged.connect(self._on_starfish_color_changed)
        layout.addWidget(self.starfish_color_button)

        # Arm Base Thickness (0.2-0.6)
        layout.addWidget(self._create_label("Arm Thickness"))
        self.arm_thickness_slider = self._create_slider(20, 60, 40, self._on_arm_thickness_changed)
        layout.addWidget(self.arm_thickness_slider)
        self.arm_thickness_label = QLabel("0.40")
        self.arm_thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arm_thickness_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.arm_thickness_label)

        # Curl Factor (0-0.8)
        layout.addWidget(self._create_label("Arm Curl Amount"))
        self.curl_factor_slider = self._create_slider(0, 80, 30, self._on_curl_factor_changed)
        layout.addWidget(self.curl_factor_slider)
        self.curl_factor_label = QLabel("0.30")
        self.curl_factor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.curl_factor_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.curl_factor_label)

        # Info label
        self.starfish_info_label = QLabel("Higher curl = arms bend downward more")
        self.starfish_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.starfish_info_label.setStyleSheet("color: #06b6d4; font-size: 10pt; font-style: italic; padding: 8px; background-color: #164e63; border-radius: 8px; margin-top: 10px; border: 1px solid #0891b2;")
        layout.addWidget(self.starfish_info_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_starfish_animation_section(self):
        """Create Starfish Animation card."""
        group = self._create_card("ANIMATION")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Animation Speed
        layout.addWidget(self._create_label("Animation Speed"))
        self.starfish_anim_speed_slider = self._create_slider(50, 500, 150, self._on_starfish_anim_speed_changed)
        layout.addWidget(self.starfish_anim_speed_slider)
        self.starfish_anim_speed_label = QLabel("1.5x")
        self.starfish_anim_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.starfish_anim_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.starfish_anim_speed_label)

        # Pulse Amount
        layout.addWidget(self._create_label("Pulse Amount"))
        self.starfish_pulse_slider = self._create_slider(0, 20, 6, self._on_starfish_pulse_changed)
        layout.addWidget(self.starfish_pulse_slider)
        self.starfish_pulse_label = QLabel("0.06")
        self.starfish_pulse_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.starfish_pulse_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.starfish_pulse_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    # Event Handlers
    def _on_num_arms_changed(self, value):
        self._num_arms = value
        self._emit_change()

    def _on_arm_segments_changed(self, value):
        self._arm_segments = value
        self._emit_change()

    def _on_central_body_changed(self, value):
        self._central_body_size = value / 100.0
        self.central_body_label.setText(f"{self._central_body_size:.2f}")
        self._emit_change()

    def _on_starfish_color_changed(self, rgb_tuple):
        self._starfish_color = rgb_tuple
        self._emit_change()

    def _on_arm_thickness_changed(self, value):
        self._arm_base_thickness = value / 100.0
        self.arm_thickness_label.setText(f"{self._arm_base_thickness:.2f}")
        self._emit_change()

    def _on_curl_factor_changed(self, value):
        self._curl_factor = value / 100.0
        self.curl_factor_label.setText(f"{self._curl_factor:.2f}")
        self._emit_change()

    def _on_starfish_anim_speed_changed(self, value):
        self._starfish_anim_speed = value / 100.0
        self.starfish_anim_speed_label.setText(f"{self._starfish_anim_speed:.1f}x")
        self._emit_change()

    def _on_starfish_pulse_changed(self, value):
        self._starfish_pulse = value / 100.0
        self.starfish_pulse_label.setText(f"{self._starfish_pulse:.2f}")
        self._emit_change()

    def get_state(self):
        """Get current state."""
        return {
            'num_arms': self._num_arms,
            'arm_segments': self._arm_segments,
            'central_body_size': self._central_body_size,
            'arm_base_thickness': self._arm_base_thickness,
            'starfish_color': self._starfish_color,
            'curl_factor': self._curl_factor,
            'anim_speed': self._starfish_anim_speed,
            'pulse_amount': self._starfish_pulse,
        }

    def set_state(self, state):
        """Restore state."""
        self._updating = True

        # Starfish parameters
        self._num_arms = state.get('num_arms', 5)
        self._arm_segments = state.get('arm_segments', 6)
        self._central_body_size = state.get('central_body_size', 0.8)
        self._arm_base_thickness = state.get('arm_base_thickness', 0.4)
        self._starfish_color = state.get('starfish_color', (0.9, 0.5, 0.3))
        self._curl_factor = state.get('curl_factor', 0.3)
        self._starfish_anim_speed = state.get('anim_speed', 1.5)
        self._starfish_pulse = state.get('pulse_amount', 0.06)

        # Update UI
        self.num_arms_spin.setValue(self._num_arms)
        self.arm_segments_spin.setValue(self._arm_segments)
        self.central_body_slider.setValue(int(self._central_body_size * 100))
        self.arm_thickness_slider.setValue(int(self._arm_base_thickness * 100))
        self.starfish_color_button.set_color(self._starfish_color)
        self.curl_factor_slider.setValue(int(self._curl_factor * 100))
        self.starfish_anim_speed_slider.setValue(int(self._starfish_anim_speed * 100))
        self.starfish_pulse_slider.setValue(int(self._starfish_pulse * 100))

        self._updating = False

    def load_preset(self, params):
        """Load a preset configuration."""
        # Merge preset params with current state and apply
        current_state = self.get_state()
        current_state.update(params)
        self.set_state(current_state)
