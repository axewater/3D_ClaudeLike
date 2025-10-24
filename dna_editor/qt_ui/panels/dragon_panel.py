"""Dragon creature control panel."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel
)
from PyQt6.QtCore import Qt
from .base_creature_panel import BaseCreaturePanel
from ..widgets import ColorButton


class DragonPanel(BaseCreaturePanel):
    """Control panel for dragon creature parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize dragon-specific state variables
        self._dragon_segments = 15
        self._dragon_thickness = 0.3
        self._dragon_taper = 0.6
        self._dragon_head_scale = 3.0
        self._dragon_body_color = (200, 40, 40)  # RGB 0-255
        self._dragon_head_color = (255, 200, 50)  # RGB 0-255
        self._dragon_weave_amplitude = 0.5
        self._dragon_bob_amplitude = 0.3
        self._dragon_anim_speed = 1.5
        self._dragon_num_eyes = 2
        self._dragon_eye_size = 0.15
        self._dragon_eyeball_color = (255, 200, 50)  # RGB 0-255
        self._dragon_pupil_color = (20, 0, 0)  # RGB 0-255
        self._dragon_mouth_size = 0.25
        self._dragon_mouth_color = (20, 0, 0)  # RGB 0-255
        self._dragon_num_whiskers_per_side = 2
        self._dragon_whisker_segments = 4
        self._dragon_whisker_thickness = 0.05

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Column 1: Body Shape
        layout.addWidget(self._create_dragon_body_section(), 0, 0)

        # Column 2: Appearance
        layout.addWidget(self._create_dragon_appearance_section(), 0, 1)

        # Column 3: Animation
        layout.addWidget(self._create_dragon_animation_section(), 0, 2)

        # Row 2: Eyes section (full width, spanning 3 columns)
        layout.addWidget(self._create_dragon_eyes_section(), 1, 0, 1, 3)

        # Row 3: Mouth section (full width, spanning 3 columns)
        layout.addWidget(self._create_dragon_mouth_section(), 2, 0, 1, 3)

        # Row 4: Whiskers section (full width, spanning 3 columns)
        layout.addWidget(self._create_dragon_whiskers_section(), 3, 0, 1, 3)

        self.setLayout(layout)

    def _create_dragon_body_section(self):
        """Create Dragon Body Shape card."""
        group = self._create_card("DRAGON BODY")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Number of Segments (5-30)
        layout.addWidget(self._create_label("Body Segments"))
        self.dragon_segments_spin = self._create_spinbox(5, 30, self._dragon_segments, self._on_dragon_segments_changed)
        layout.addWidget(self.dragon_segments_spin)
        layout.addSpacing(8)

        # Segment Thickness (0.1-0.8)
        layout.addWidget(self._create_label("Segment Thickness"))
        self.dragon_thickness_slider = self._create_slider(10, 80, 30, self._on_dragon_thickness_changed)
        layout.addWidget(self.dragon_thickness_slider)
        self.dragon_thickness_label = QLabel("0.30")
        self.dragon_thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_thickness_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_thickness_label)

        # Taper Factor (0.0-0.9)
        layout.addWidget(self._create_label("Tail Taper"))
        self.dragon_taper_slider = self._create_slider(0, 90, 60, self._on_dragon_taper_changed)
        layout.addWidget(self.dragon_taper_slider)
        self.dragon_taper_label = QLabel("0.60")
        self.dragon_taper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_taper_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_taper_label)

        # Head Scale (1.0-3.5)
        layout.addWidget(self._create_label("Head Size"))
        self.dragon_head_scale_slider = self._create_slider(10, 35, 30, self._on_dragon_head_scale_changed)
        layout.addWidget(self.dragon_head_scale_slider)
        self.dragon_head_scale_label = QLabel("3.0x")
        self.dragon_head_scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_head_scale_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_head_scale_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_dragon_appearance_section(self):
        """Create Dragon Appearance card."""
        group = self._create_card("DRAGON APPEARANCE")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Body Color (note: ColorButton expects 0-1 range, but we store 0-255)
        layout.addWidget(self._create_label("Body Color"))
        body_color_01 = tuple(c / 255.0 for c in self._dragon_body_color)
        self.dragon_body_color_button = ColorButton(body_color_01)
        self.dragon_body_color_button.colorChanged.connect(self._on_dragon_body_color_changed)
        layout.addWidget(self.dragon_body_color_button)

        # Head Color
        layout.addWidget(self._create_label("Head Color"))
        head_color_01 = tuple(c / 255.0 for c in self._dragon_head_color)
        self.dragon_head_color_button = ColorButton(head_color_01)
        self.dragon_head_color_button.colorChanged.connect(self._on_dragon_head_color_changed)
        layout.addWidget(self.dragon_head_color_button)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_dragon_animation_section(self):
        """Create Dragon Animation card."""
        group = self._create_card("DRAGON ANIMATION")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Weave Amplitude (0.0-1.0)
        layout.addWidget(self._create_label("Weave Amount"))
        self.dragon_weave_slider = self._create_slider(0, 100, 50, self._on_dragon_weave_changed)
        layout.addWidget(self.dragon_weave_slider)
        self.dragon_weave_label = QLabel("0.50")
        self.dragon_weave_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_weave_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_weave_label)

        # Bob Amplitude (0.0-1.0)
        layout.addWidget(self._create_label("Bob Amount"))
        self.dragon_bob_slider = self._create_slider(0, 100, 30, self._on_dragon_bob_changed)
        layout.addWidget(self.dragon_bob_slider)
        self.dragon_bob_label = QLabel("0.30")
        self.dragon_bob_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_bob_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_bob_label)

        # Animation Speed (0.5-5.0)
        layout.addWidget(self._create_label("Animation Speed"))
        self.dragon_anim_speed_slider = self._create_slider(50, 500, 150, self._on_dragon_anim_speed_changed)
        layout.addWidget(self.dragon_anim_speed_slider)
        self.dragon_anim_speed_label = QLabel("1.5x")
        self.dragon_anim_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_anim_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        layout.addWidget(self.dragon_anim_speed_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_dragon_eyes_section(self):
        """Create Dragon Eyes card (full width)."""
        group = self._create_card("DRAGON EYES")
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)

        # Number of Eyes
        eyes_layout = QVBoxLayout()
        eyes_layout.addWidget(self._create_label("Number of Eyes"))
        self.dragon_num_eyes_spin = self._create_spinbox(0, 8, self._dragon_num_eyes, self._on_dragon_num_eyes_changed)
        eyes_layout.addWidget(self.dragon_num_eyes_spin)
        layout.addLayout(eyes_layout)

        # Eye Size
        eye_size_layout = QVBoxLayout()
        eye_size_layout.addWidget(self._create_label("Eye Size"))
        self.dragon_eye_size_slider = self._create_slider(5, 30, 15, self._on_dragon_eye_size_changed)
        eye_size_layout.addWidget(self.dragon_eye_size_slider)
        self.dragon_eye_size_label = QLabel("0.15")
        self.dragon_eye_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_eye_size_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        eye_size_layout.addWidget(self.dragon_eye_size_label)
        layout.addLayout(eye_size_layout)

        # Eyeball Color
        eyeball_color_layout = QVBoxLayout()
        eyeball_color_layout.addWidget(self._create_label("Eyeball Color"))
        eyeball_color_01 = tuple(c / 255.0 for c in self._dragon_eyeball_color)
        self.dragon_eyeball_color_button = ColorButton(eyeball_color_01)
        self.dragon_eyeball_color_button.colorChanged.connect(self._on_dragon_eyeball_color_changed)
        eyeball_color_layout.addWidget(self.dragon_eyeball_color_button)
        layout.addLayout(eyeball_color_layout)

        # Pupil Color
        pupil_color_layout = QVBoxLayout()
        pupil_color_layout.addWidget(self._create_label("Pupil Color"))
        pupil_color_01 = tuple(c / 255.0 for c in self._dragon_pupil_color)
        self.dragon_pupil_color_button = ColorButton(pupil_color_01)
        self.dragon_pupil_color_button.colorChanged.connect(self._on_dragon_pupil_color_changed)
        pupil_color_layout.addWidget(self.dragon_pupil_color_button)
        layout.addLayout(pupil_color_layout)

        group.setLayout(layout)
        return group

    def _create_dragon_mouth_section(self):
        """Create Dragon Mouth card."""
        group = self._create_card("DRAGON MOUTH")
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)

        # Mouth Size
        mouth_size_layout = QVBoxLayout()
        mouth_size_layout.addWidget(self._create_label("Mouth Size"))
        self.dragon_mouth_size_slider = self._create_slider(25, 50, 25, self._on_dragon_mouth_size_changed)
        mouth_size_layout.addWidget(self.dragon_mouth_size_slider)
        self.dragon_mouth_size_label = QLabel("0.25")
        self.dragon_mouth_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_mouth_size_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        mouth_size_layout.addWidget(self.dragon_mouth_size_label)
        layout.addLayout(mouth_size_layout)

        # Mouth Color
        mouth_color_layout = QVBoxLayout()
        mouth_color_layout.addWidget(self._create_label("Mouth Cavity Color"))
        mouth_color_01 = tuple(c / 255.0 for c in self._dragon_mouth_color)
        self.dragon_mouth_color_button = ColorButton(mouth_color_01)
        self.dragon_mouth_color_button.colorChanged.connect(self._on_dragon_mouth_color_changed)
        mouth_color_layout.addWidget(self.dragon_mouth_color_button)
        layout.addLayout(mouth_color_layout)

        group.setLayout(layout)
        return group

    def _create_dragon_whiskers_section(self):
        """Create Dragon Whiskers card."""
        group = self._create_card("WHISKERS")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Number of Whiskers Per Side (0-3)
        whisker_count_layout = QVBoxLayout()
        whisker_count_layout.addWidget(self._create_label("Whiskers Per Side"))
        self.dragon_num_whiskers_spin = self._create_spinbox(0, 3, self._dragon_num_whiskers_per_side, self._on_dragon_num_whiskers_changed)
        whisker_count_layout.addWidget(self.dragon_num_whiskers_spin)
        layout.addLayout(whisker_count_layout)

        # Whisker Segments (3-6)
        whisker_segments_layout = QVBoxLayout()
        whisker_segments_layout.addWidget(self._create_label("Whisker Segments"))
        self.dragon_whisker_segments_spin = self._create_spinbox(3, 6, self._dragon_whisker_segments, self._on_dragon_whisker_segments_changed)
        whisker_segments_layout.addWidget(self.dragon_whisker_segments_spin)
        layout.addLayout(whisker_segments_layout)

        # Whisker Thickness (0.03-0.08)
        whisker_thickness_layout = QVBoxLayout()
        whisker_thickness_layout.addWidget(self._create_label("Whisker Thickness"))
        self.dragon_whisker_thickness_slider = self._create_slider(3, 8, 5, self._on_dragon_whisker_thickness_changed)
        whisker_thickness_layout.addWidget(self.dragon_whisker_thickness_slider)
        self.dragon_whisker_thickness_label = QLabel("0.05")
        self.dragon_whisker_thickness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dragon_whisker_thickness_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        whisker_thickness_layout.addWidget(self.dragon_whisker_thickness_label)
        layout.addLayout(whisker_thickness_layout)

        group.setLayout(layout)
        return group

    # Event Handlers
    def _on_dragon_segments_changed(self, value):
        self._dragon_segments = value
        self._emit_change()

    def _on_dragon_thickness_changed(self, value):
        self._dragon_thickness = value / 100.0
        self.dragon_thickness_label.setText(f"{self._dragon_thickness:.2f}")
        self._emit_change()

    def _on_dragon_taper_changed(self, value):
        self._dragon_taper = value / 100.0
        self.dragon_taper_label.setText(f"{self._dragon_taper:.2f}")
        self._emit_change()

    def _on_dragon_head_scale_changed(self, value):
        self._dragon_head_scale = value / 10.0
        self.dragon_head_scale_label.setText(f"{self._dragon_head_scale:.1f}x")
        self._emit_change()

    def _on_dragon_body_color_changed(self, color):
        # Convert 0-1 to 0-255
        self._dragon_body_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self._emit_change()

    def _on_dragon_head_color_changed(self, color):
        # Convert 0-1 to 0-255
        self._dragon_head_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self._emit_change()

    def _on_dragon_weave_changed(self, value):
        self._dragon_weave_amplitude = value / 100.0
        self.dragon_weave_label.setText(f"{self._dragon_weave_amplitude:.2f}")
        self._emit_change()

    def _on_dragon_bob_changed(self, value):
        self._dragon_bob_amplitude = value / 100.0
        self.dragon_bob_label.setText(f"{self._dragon_bob_amplitude:.2f}")
        self._emit_change()

    def _on_dragon_anim_speed_changed(self, value):
        self._dragon_anim_speed = value / 100.0
        self.dragon_anim_speed_label.setText(f"{self._dragon_anim_speed:.1f}x")
        self._emit_change()

    def _on_dragon_num_eyes_changed(self, value):
        self._dragon_num_eyes = value
        self._emit_change()

    def _on_dragon_eye_size_changed(self, value):
        self._dragon_eye_size = value / 100.0
        self.dragon_eye_size_label.setText(f"{self._dragon_eye_size:.2f}")
        self._emit_change()

    def _on_dragon_eyeball_color_changed(self, color):
        # Convert 0-1 to 0-255
        self._dragon_eyeball_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self._emit_change()

    def _on_dragon_pupil_color_changed(self, color):
        # Convert 0-1 to 0-255
        self._dragon_pupil_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self._emit_change()

    def _on_dragon_mouth_size_changed(self, value):
        self._dragon_mouth_size = value / 100.0
        self.dragon_mouth_size_label.setText(f"{self._dragon_mouth_size:.2f}")
        self._emit_change()

    def _on_dragon_mouth_color_changed(self, color):
        # Convert 0-1 to 0-255
        self._dragon_mouth_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self._emit_change()

    def _on_dragon_num_whiskers_changed(self, value):
        self._dragon_num_whiskers_per_side = value
        self._emit_change()

    def _on_dragon_whisker_segments_changed(self, value):
        self._dragon_whisker_segments = value
        self._emit_change()

    def _on_dragon_whisker_thickness_changed(self, value):
        self._dragon_whisker_thickness = value / 100.0
        self.dragon_whisker_thickness_label.setText(f"{self._dragon_whisker_thickness:.2f}")
        self._emit_change()

    def get_state(self):
        """Get current state."""
        return {
            'num_segments': self._dragon_segments,
            'segment_thickness': self._dragon_thickness,
            'taper_factor': self._dragon_taper,
            'head_scale': self._dragon_head_scale,
            'body_color': self._dragon_body_color,
            'head_color': self._dragon_head_color,
            'weave_amplitude': self._dragon_weave_amplitude,
            'bob_amplitude': self._dragon_bob_amplitude,
            'anim_speed': self._dragon_anim_speed,
            'num_eyes': self._dragon_num_eyes,
            'eye_size': self._dragon_eye_size,
            'eyeball_color': self._dragon_eyeball_color,
            'pupil_color': self._dragon_pupil_color,
            'mouth_size': self._dragon_mouth_size,
            'mouth_color': self._dragon_mouth_color,
            'num_whiskers_per_side': self._dragon_num_whiskers_per_side,
            'whisker_segments': self._dragon_whisker_segments,
            'whisker_thickness': self._dragon_whisker_thickness,
            # Add default for parameter not in UI
            'spine_spike_color': (100, 20, 20),
        }

    def set_state(self, state):
        """Restore state."""
        self._updating = True

        # Dragon parameters
        self._dragon_segments = state.get('num_segments', 15)
        self._dragon_thickness = state.get('segment_thickness', 0.3)
        self._dragon_taper = state.get('taper_factor', 0.6)
        self._dragon_head_scale = state.get('head_scale', 3.0)
        self._dragon_body_color = state.get('body_color', (200, 40, 40))
        self._dragon_head_color = state.get('head_color', (255, 200, 50))
        self._dragon_weave_amplitude = state.get('weave_amplitude', 0.5)
        self._dragon_bob_amplitude = state.get('bob_amplitude', 0.3)
        self._dragon_anim_speed = state.get('anim_speed', 1.5)
        self._dragon_num_eyes = state.get('num_eyes', 2)
        self._dragon_eye_size = state.get('eye_size', 0.15)
        self._dragon_eyeball_color = state.get('eyeball_color', (255, 200, 50))
        self._dragon_pupil_color = state.get('pupil_color', (20, 0, 0))
        self._dragon_mouth_size = state.get('mouth_size', 0.25)
        self._dragon_mouth_color = state.get('mouth_color', (20, 0, 0))
        self._dragon_num_whiskers_per_side = state.get('num_whiskers_per_side', 2)
        self._dragon_whisker_segments = state.get('whisker_segments', 4)
        self._dragon_whisker_thickness = state.get('whisker_thickness', 0.05)

        # Update UI
        self.dragon_segments_spin.setValue(self._dragon_segments)
        self.dragon_thickness_slider.setValue(int(self._dragon_thickness * 100))
        self.dragon_taper_slider.setValue(int(self._dragon_taper * 100))
        self.dragon_head_scale_slider.setValue(int(self._dragon_head_scale * 10))

        # Convert 0-255 to 0-1 for color buttons
        body_color_01 = tuple(c / 255.0 for c in self._dragon_body_color)
        self.dragon_body_color_button.set_color(body_color_01)
        head_color_01 = tuple(c / 255.0 for c in self._dragon_head_color)
        self.dragon_head_color_button.set_color(head_color_01)

        self.dragon_weave_slider.setValue(int(self._dragon_weave_amplitude * 100))
        self.dragon_bob_slider.setValue(int(self._dragon_bob_amplitude * 100))
        self.dragon_anim_speed_slider.setValue(int(self._dragon_anim_speed * 100))

        # Eye parameters
        self.dragon_num_eyes_spin.setValue(self._dragon_num_eyes)
        self.dragon_eye_size_slider.setValue(int(self._dragon_eye_size * 100))
        eyeball_color_01 = tuple(c / 255.0 for c in self._dragon_eyeball_color)
        self.dragon_eyeball_color_button.set_color(eyeball_color_01)
        pupil_color_01 = tuple(c / 255.0 for c in self._dragon_pupil_color)
        self.dragon_pupil_color_button.set_color(pupil_color_01)

        # Mouth parameters
        self.dragon_mouth_size_slider.setValue(int(self._dragon_mouth_size * 100))
        mouth_color_01 = tuple(c / 255.0 for c in self._dragon_mouth_color)
        self.dragon_mouth_color_button.set_color(mouth_color_01)

        # Whisker parameters
        self.dragon_num_whiskers_spin.setValue(self._dragon_num_whiskers_per_side)
        self.dragon_whisker_segments_spin.setValue(self._dragon_whisker_segments)
        self.dragon_whisker_thickness_slider.setValue(int(self._dragon_whisker_thickness * 100))

        self._updating = False

    def load_preset(self, params):
        """Load a preset configuration."""
        # Merge preset params with current state and apply
        current_state = self.get_state()
        current_state.update(params)
        self.set_state(current_state)
