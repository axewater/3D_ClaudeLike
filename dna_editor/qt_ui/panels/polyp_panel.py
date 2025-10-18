"""Polyp creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QGroupBox, QLabel
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton


class PolypPanel(BaseCreaturePanel):
    """Control panel for polyp creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize polyp-specific state variables
        self._num_spheres = 4
        self._base_sphere_size = 0.8
        self._polyp_color = (0.6, 0.3, 0.7)
        self._curve_intensity = 0.4
        self._polyp_tentacles_per_sphere = 6
        self._polyp_segments = 12

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Spine Shape
        layout.addWidget(self._create_polyp_spine_section(), 0, 0)

        # Column 2: Tentacles
        layout.addWidget(self._create_polyp_tentacles_section(), 0, 1)

        # Column 3: Appearance
        layout.addWidget(self._create_polyp_appearance_section(), 0, 2)

        self.setLayout(layout)

    def _create_polyp_spine_section(self):
        """Create Polyp Spine Shape card."""
        group = self._create_card("SPINE SHAPE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Number of Spheres (3-5)
        layout.addWidget(self._create_label("Spheres in Spine"))
        self.num_spheres_spin = self._create_spinbox(3, 5, self._num_spheres, self._on_num_spheres_changed)
        layout.addWidget(self.num_spheres_spin)
        layout.addSpacing(8)

        # Base Sphere Size (0.4-1.5)
        layout.addWidget(self._create_label("Root Sphere Size"))
        self.base_sphere_slider = self._create_slider(40, 150, 80, self._on_base_sphere_changed)
        layout.addWidget(self.base_sphere_slider)
        self.base_sphere_label = QLabel("0.80")
        self.base_sphere_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.base_sphere_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.base_sphere_label)

        # Curve Intensity (0-1)
        layout.addWidget(self._create_label("Spine Curve Amount"))
        self.curve_intensity_slider = self._create_slider(0, 100, 40, self._on_curve_intensity_changed)
        layout.addWidget(self.curve_intensity_slider)
        self.curve_intensity_label = QLabel("0.40")
        self.curve_intensity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.curve_intensity_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.curve_intensity_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_polyp_tentacles_section(self):
        """Create Polyp Tentacles card."""
        group = self._create_card("TENTACLES")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Tentacles per Sphere (3-12)
        layout.addWidget(self._create_label("Tentacles per Sphere"))
        self.polyp_tentacles_spin = self._create_spinbox(3, 12, self._polyp_tentacles_per_sphere, self._on_polyp_tentacles_changed)
        layout.addWidget(self.polyp_tentacles_spin)
        layout.addSpacing(8)

        # Tentacle Segments (5-20)
        layout.addWidget(self._create_label("Tentacle Length (Segments)"))
        self.polyp_segments_spin = self._create_spinbox(5, 20, self._polyp_segments, self._on_polyp_segments_changed)
        layout.addWidget(self.polyp_segments_spin)
        layout.addSpacing(8)

        # Info label
        self.polyp_info_label = QLabel("More segments = longer tentacles")
        self.polyp_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.polyp_info_label.setStyleSheet("color: #06b6d4; font-size: 10pt; font-style: italic; padding: 8px; background-color: #164e63; border-radius: 8px; margin-top: 10px; border: 1px solid #0891b2;")
        layout.addWidget(self.polyp_info_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_polyp_appearance_section(self):
        """Create Polyp Appearance card."""
        group = self._create_card("APPEARANCE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Spine Color
        layout.addWidget(self._create_label("Spine & Tentacle Color"))
        self.polyp_color_button = ColorButton(self._polyp_color)
        self.polyp_color_button.colorChanged.connect(self._on_polyp_color_changed)
        layout.addWidget(self.polyp_color_button)

        layout.addStretch()
        group.setLayout(layout)
        return group

    # Event Handlers
    def _on_num_spheres_changed(self, value):
        self._num_spheres = value
        self._emit_change()

    def _on_base_sphere_changed(self, value):
        self._base_sphere_size = value / 100.0
        self.base_sphere_label.setText(f"{self._base_sphere_size:.2f}")
        self._emit_change()

    def _on_curve_intensity_changed(self, value):
        self._curve_intensity = value / 100.0
        self.curve_intensity_label.setText(f"{self._curve_intensity:.2f}")
        self._emit_change()

    def _on_polyp_tentacles_changed(self, value):
        self._polyp_tentacles_per_sphere = value
        self._emit_change()

    def _on_polyp_segments_changed(self, value):
        self._polyp_segments = value
        self._emit_change()

    def _on_polyp_color_changed(self, rgb_tuple):
        self._polyp_color = rgb_tuple
        self._emit_change()

    def get_state(self):
        """Get current state."""
        return {
            'num_spheres': self._num_spheres,
            'base_sphere_size': self._base_sphere_size,
            'polyp_color': self._polyp_color,
            'curve_intensity': self._curve_intensity,
            'polyp_tentacles_per_sphere': self._polyp_tentacles_per_sphere,
            'polyp_segments': self._polyp_segments,
        }

    def set_state(self, state):
        """Restore state."""
        self._updating = True

        # Polyp parameters
        self._num_spheres = state.get('num_spheres', 4)
        self._base_sphere_size = state.get('base_sphere_size', 0.8)
        self._polyp_color = state.get('polyp_color', (0.6, 0.3, 0.7))
        self._curve_intensity = state.get('curve_intensity', 0.4)
        self._polyp_tentacles_per_sphere = state.get('polyp_tentacles_per_sphere', 6)
        self._polyp_segments = state.get('polyp_segments', 12)

        # Update UI
        self.num_spheres_spin.setValue(self._num_spheres)
        self.base_sphere_slider.setValue(int(self._base_sphere_size * 100))
        self.curve_intensity_slider.setValue(int(self._curve_intensity * 100))
        self.polyp_tentacles_spin.setValue(self._polyp_tentacles_per_sphere)
        self.polyp_segments_spin.setValue(self._polyp_segments)
        self.polyp_color_button.set_color(self._polyp_color)

        self._updating = False
