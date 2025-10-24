"""Blob creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QGroupBox, QLabel, QSlider
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton


class BlobPanel(BaseCreaturePanel):
    """Control panel for blob creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize blob-specific state variables
        self._blob_branch_depth = 2
        self._blob_branch_count = 2
        self._cube_size_min = 0.3
        self._cube_size_max = 0.8
        self._cube_spacing = 1.2
        self._blob_color = (0.2, 0.8, 0.4)  # Green slime
        self._blob_transparency = 0.7
        self._jiggle_speed = 2.0
        self._blob_pulse_amount = 0.1

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Blob Shape
        layout.addWidget(self._create_blob_shape_section(), 0, 0)

        # Column 2: Blob Appearance
        layout.addWidget(self._create_blob_appearance_section(), 0, 1)

        # Column 3: Blob Animation
        layout.addWidget(self._create_blob_animation_section(), 0, 2)

        self.setLayout(layout)

    def _create_blob_shape_section(self):
        """Create Blob Shape card with branching controls."""
        group = self._create_card("BLOB SHAPE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Branch Depth
        layout.addWidget(self._create_label("Branch Depth"))
        self.blob_branch_depth_spin = self._create_spinbox(0, 3, self._blob_branch_depth, self._on_blob_branching_changed)
        layout.addWidget(self.blob_branch_depth_spin)
        layout.addSpacing(8)

        # Branch Count
        layout.addWidget(self._create_label("Branches Per Level"))
        self.blob_branch_count_spin = self._create_spinbox(1, 3, self._blob_branch_count, self._on_blob_branching_changed)
        layout.addWidget(self.blob_branch_count_spin)
        layout.addSpacing(8)

        # Branch Info Label
        self.blob_branch_info_label = QLabel("Total: ~7 cubes")
        self.blob_branch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blob_branch_info_label.setStyleSheet("color: #06b6d4; font-size: 11pt; font-weight: bold; padding: 12px; background-color: #164e63; border-radius: 8px; margin-top: 10px; border: 1px solid #0891b2;")
        layout.addWidget(self.blob_branch_info_label)
        self._update_blob_branch_info()
        layout.addSpacing(8)

        # Cube Spacing
        layout.addWidget(self._create_label("Cube Spacing"))
        self.cube_spacing_slider = self._create_slider(50, 250, 120, self._on_cube_spacing_changed)
        layout.addWidget(self.cube_spacing_slider)
        self.cube_spacing_label = QLabel("1.20")
        self.cube_spacing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cube_spacing_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.cube_spacing_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_blob_appearance_section(self):
        """Create Blob Appearance card."""
        group = self._create_card("BLOB APPEARANCE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Blob Color
        layout.addWidget(self._create_label("Blob Color"))
        self.blob_color_button = ColorButton(self._blob_color)
        self.blob_color_button.colorChanged.connect(self._on_blob_color_changed)
        layout.addWidget(self.blob_color_button)

        # Transparency
        layout.addWidget(self._create_label("Transparency"))
        self.blob_transparency_slider = self._create_slider(10, 95, 70, self._on_blob_transparency_changed)
        layout.addWidget(self.blob_transparency_slider)
        self.blob_transparency_label = QLabel("70%")
        self.blob_transparency_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blob_transparency_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.blob_transparency_label)

        # Cube Size Min
        layout.addWidget(self._create_label("Min Cube Size"))
        self.cube_size_min_slider = self._create_slider(10, 150, 30, self._on_cube_size_changed)
        layout.addWidget(self.cube_size_min_slider)
        self.cube_size_min_label = QLabel("0.30")
        self.cube_size_min_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cube_size_min_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.cube_size_min_label)

        # Cube Size Max
        layout.addWidget(self._create_label("Max Cube Size"))
        self.cube_size_max_slider = self._create_slider(10, 150, 80, self._on_cube_size_changed)
        layout.addWidget(self.cube_size_max_slider)
        self.cube_size_max_label = QLabel("0.80")
        self.cube_size_max_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cube_size_max_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.cube_size_max_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_blob_animation_section(self):
        """Create Blob Animation card."""
        group = self._create_card("BLOB ANIMATION")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Jiggle Speed
        layout.addWidget(self._create_label("Jiggle Speed"))
        self.jiggle_speed_slider = self._create_slider(50, 500, 200, self._on_jiggle_speed_changed)
        layout.addWidget(self.jiggle_speed_slider)
        self.jiggle_speed_label = QLabel("2.0x")
        self.jiggle_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.jiggle_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.jiggle_speed_label)

        # Pulse Amount
        layout.addWidget(self._create_label("Pulse Amount"))
        self.blob_pulse_slider = self._create_slider(0, 30, 10, self._on_blob_pulse_changed)
        layout.addWidget(self.blob_pulse_slider)
        self.blob_pulse_label = QLabel("0.10")
        self.blob_pulse_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blob_pulse_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.blob_pulse_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    # Event Handlers
    def _on_blob_branching_changed(self):
        self._blob_branch_depth = self.blob_branch_depth_spin.value()
        self._blob_branch_count = self.blob_branch_count_spin.value()
        self._update_blob_branch_info()
        self._emit_change()

    def _on_cube_spacing_changed(self, value):
        self._cube_spacing = value / 100.0
        self.cube_spacing_label.setText(f"{self._cube_spacing:.2f}")
        self._emit_change()

    def _on_blob_color_changed(self, rgb_tuple):
        self._blob_color = rgb_tuple
        self._emit_change()

    def _on_blob_transparency_changed(self, value):
        self._blob_transparency = value / 100.0
        self.blob_transparency_label.setText(f"{int(value)}%")
        self._emit_change()

    def _on_cube_size_changed(self):
        self._cube_size_min = self.cube_size_min_slider.value() / 100.0
        self._cube_size_max = self.cube_size_max_slider.value() / 100.0
        self.cube_size_min_label.setText(f"{self._cube_size_min:.2f}")
        self.cube_size_max_label.setText(f"{self._cube_size_max:.2f}")
        self._emit_change()

    def _on_jiggle_speed_changed(self, value):
        self._jiggle_speed = value / 100.0
        self.jiggle_speed_label.setText(f"{self._jiggle_speed:.1f}x")
        self._emit_change()

    def _on_blob_pulse_changed(self, value):
        self._blob_pulse_amount = value / 100.0
        self.blob_pulse_label.setText(f"{self._blob_pulse_amount:.2f}")
        self._emit_change()

    def _update_blob_branch_info(self):
        """Calculate and display total cube count from branch parameters."""
        if self._blob_branch_count == 1:
            total_cubes = self._blob_branch_depth + 1
        else:
            total_cubes = (self._blob_branch_count ** (self._blob_branch_depth + 1) - 1) // (self._blob_branch_count - 1)
        self.blob_branch_info_label.setText(f"Total: ~{total_cubes} cubes")

    def get_state(self):
        """Get current state."""
        return {
            'branch_depth': self._blob_branch_depth,
            'branch_count': self._blob_branch_count,
            'cube_size_min': self._cube_size_min,
            'cube_size_max': self._cube_size_max,
            'cube_spacing': self._cube_spacing,
            'blob_color': self._blob_color,
            'transparency': self._blob_transparency,
            'jiggle_speed': self._jiggle_speed,
            'pulse_amount': self._blob_pulse_amount,
        }

    def set_state(self, state):
        """Restore state."""
        self._updating = True

        # Blob parameters
        self._blob_branch_depth = state.get('branch_depth', 2)
        self._blob_branch_count = state.get('branch_count', 2)
        self._cube_size_min = state.get('cube_size_min', 0.3)
        self._cube_size_max = state.get('cube_size_max', 0.8)
        self._cube_spacing = state.get('cube_spacing', 1.2)
        self._blob_color = state.get('blob_color', (0.2, 0.8, 0.4))
        self._blob_transparency = state.get('transparency', 0.7)
        self._jiggle_speed = state.get('jiggle_speed', 2.0)
        self._blob_pulse_amount = state.get('pulse_amount', 0.1)

        # Update UI
        self.blob_branch_depth_spin.setValue(self._blob_branch_depth)
        self.blob_branch_count_spin.setValue(self._blob_branch_count)
        self.cube_spacing_slider.setValue(int(self._cube_spacing * 100))
        self.blob_color_button.set_color(self._blob_color)
        self.blob_transparency_slider.setValue(int(self._blob_transparency * 100))
        self.cube_size_min_slider.setValue(int(self._cube_size_min * 100))
        self.cube_size_max_slider.setValue(int(self._cube_size_max * 100))
        self.jiggle_speed_slider.setValue(int(self._jiggle_speed * 100))
        self.blob_pulse_slider.setValue(int(self._blob_pulse_amount * 100))

        self._update_blob_branch_info()
        self._updating = False

    def load_preset(self, params):
        """Load a preset configuration."""
        # Merge preset params with current state and apply
        current_state = self.get_state()
        current_state.update(params)
        self.set_state(current_state)
