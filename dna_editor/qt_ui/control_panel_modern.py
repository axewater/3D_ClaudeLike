"""
Modern control panel - orchestrates creature-specific panels.
Reduced from 2094 lines to ~400 lines by extracting creature-specific panels.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QSlider,
    QComboBox, QPushButton, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..core.constants import PRESETS
from .panels import TentaclePanel, BlobPanel, PolypPanel, StarfishPanel, DragonPanel, MedusaPanel


class ModernControlPanel(QWidget):
    """Modern control panel that orchestrates creature-specific panels."""

    # Signals
    creature_changed = pyqtSignal()
    creature_type_changed = pyqtSignal(str)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    export_requested = pyqtSignal()
    attack_requested = pyqtSignal()
    attack_2_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Current creature type
        self._creature_type = 'tentacle'

        # Create creature-specific panels
        self.tentacle_panel = TentaclePanel()
        self.blob_panel = BlobPanel()
        self.polyp_panel = PolypPanel()
        self.starfish_panel = StarfishPanel()
        self.medusa_panel = MedusaPanel()
        self.dragon_panel = DragonPanel()

        # Connect panel signals to forward them
        self.tentacle_panel.creature_changed.connect(self.creature_changed.emit)
        self.blob_panel.creature_changed.connect(self.creature_changed.emit)
        self.polyp_panel.creature_changed.connect(self.creature_changed.emit)
        self.starfish_panel.creature_changed.connect(self.creature_changed.emit)
        self.medusa_panel.creature_changed.connect(self.creature_changed.emit)
        self.dragon_panel.creature_changed.connect(self.creature_changed.emit)

        # Shared animation parameters (for tentacle creature)
        self._anim_speed = 2.0
        self._wave_amplitude = 0.05
        self._pulse_speed = 1.5
        self._pulse_amount = 0.05

        self._updating = False
        self._init_ui()

    def _init_ui(self):
        """Initialize UI with tabbed interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #1a1a1a, stop:1 #1e1e1e);
                border-radius: 8px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2d2d2d, stop:1 #252525);
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 24px;
                margin-right: 4px;
                color: #a0a0a0;
                font-size: 11pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a3a3a, stop:1 #323232);
                color: #d0d0d0;
            }
        """)

        # Tab 1: Design
        design_tab = QWidget()
        design_layout = QVBoxLayout()
        design_layout.setSpacing(20)
        design_layout.setContentsMargins(20, 20, 20, 20)

        # Creature Type Selector
        type_selector_layout = QHBoxLayout()
        type_label = QLabel("Creature Type:")
        type_label.setStyleSheet("color: #e5e5e5; font-size: 12pt; font-weight: bold;")
        type_selector_layout.addWidget(type_label)

        self.creature_type_combo = QComboBox()
        self.creature_type_combo.addItems([
            "Tentacle Creature", "Blob Creature", "Polyp Creature",
            "Starfish Creature", "Medusa Creature", "Dragon Creature"
        ])
        self.creature_type_combo.setMinimumHeight(40)
        self.creature_type_combo.setStyleSheet(self._get_combobox_style())
        self.creature_type_combo.currentTextChanged.connect(self._on_creature_type_changed)
        type_selector_layout.addWidget(self.creature_type_combo)
        type_selector_layout.addStretch()
        design_layout.addLayout(type_selector_layout)

        # Title
        title = QLabel("CREATURE DESIGNER")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #8b5cf6, stop:0.5 #a78bfa, stop:1 #06b6d4);
            padding: 15px;
            letter-spacing: 2px;
        """)
        design_layout.addWidget(title)

        # Add all creature panels (only one visible at a time)
        design_layout.addWidget(self.tentacle_panel)
        design_layout.addWidget(self.blob_panel)
        design_layout.addWidget(self.polyp_panel)
        design_layout.addWidget(self.starfish_panel)
        design_layout.addWidget(self.medusa_panel)
        design_layout.addWidget(self.dragon_panel)

        # Hide all except tentacle initially
        self.blob_panel.setVisible(False)
        self.polyp_panel.setVisible(False)
        self.starfish_panel.setVisible(False)
        self.medusa_panel.setVisible(False)
        self.dragon_panel.setVisible(False)

        design_layout.addStretch()
        design_tab.setLayout(design_layout)

        # Tab 2: Animation
        animation_tab = QWidget()
        animation_layout = QVBoxLayout()
        animation_layout.setSpacing(20)
        animation_layout.setContentsMargins(20, 20, 20, 20)

        anim_title = QLabel("ANIMATION CONTROLS")
        anim_title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        anim_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anim_title.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #8b5cf6, stop:0.5 #a78bfa, stop:1 #06b6d4);
            padding: 15px;
            letter-spacing: 2px;
        """)
        animation_layout.addWidget(anim_title)

        # Animation section (tentacle-specific for now)
        animation_layout.addWidget(self._create_animation_section())

        # Actions section
        animation_layout.addWidget(self._create_actions_section())

        animation_layout.addStretch()
        animation_tab.setLayout(animation_layout)

        # Add tabs
        tab_widget.addTab(design_tab, "Design")
        tab_widget.addTab(animation_tab, "Animation")

        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

    def _get_combobox_style(self):
        """Get combobox stylesheet."""
        return """
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                padding: 5px 10px;
                padding-right: 30px;
                font-size: 11pt;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #8b5cf6;
                background-color: #323232;
            }
            QComboBox:focus {
                border: 2px solid #a78bfa;
                background-color: #353535;
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
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #e0e0e0;
                selection-background-color: #8b5cf6;
                selection-color: #ffffff;
                border: 2px solid #8b5cf6;
            }
        """

    def _create_animation_section(self):
        """Create Animation card (tentacle creature specific)."""
        group = QGroupBox("ANIMATION")
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)

        # Speed
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self._create_label("Wave Speed"))
        self.anim_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.anim_speed_slider.setRange(50, 500)
        self.anim_speed_slider.setValue(200)
        self.anim_speed_slider.setMinimumHeight(30)
        self.anim_speed_slider.valueChanged.connect(self._on_anim_speed_changed)
        speed_layout.addWidget(self.anim_speed_slider)
        self.anim_speed_label = QLabel("2.0x")
        self.anim_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.anim_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        speed_layout.addWidget(self.anim_speed_label)
        layout.addLayout(speed_layout)

        # Wave Amplitude
        wave_layout = QVBoxLayout()
        wave_layout.addWidget(self._create_label("Wave Intensity"))
        self.wave_amp_slider = QSlider(Qt.Orientation.Horizontal)
        self.wave_amp_slider.setRange(0, 20)
        self.wave_amp_slider.setValue(5)
        self.wave_amp_slider.setMinimumHeight(30)
        self.wave_amp_slider.valueChanged.connect(self._on_wave_amp_changed)
        wave_layout.addWidget(self.wave_amp_slider)
        self.wave_amp_label = QLabel("0.05")
        self.wave_amp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wave_amp_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        wave_layout.addWidget(self.wave_amp_label)
        layout.addLayout(wave_layout)

        # Pulse Speed
        pulse_speed_layout = QVBoxLayout()
        pulse_speed_layout.addWidget(self._create_label("Pulse Speed"))
        self.pulse_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.pulse_speed_slider.setRange(50, 300)
        self.pulse_speed_slider.setValue(150)
        self.pulse_speed_slider.setMinimumHeight(30)
        self.pulse_speed_slider.valueChanged.connect(self._on_pulse_speed_changed)
        pulse_speed_layout.addWidget(self.pulse_speed_slider)
        self.pulse_speed_label = QLabel("1.5x")
        self.pulse_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pulse_speed_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        pulse_speed_layout.addWidget(self.pulse_speed_label)
        layout.addLayout(pulse_speed_layout)

        # Pulse Amount
        pulse_amt_layout = QVBoxLayout()
        pulse_amt_layout.addWidget(self._create_label("Pulse Amount"))
        self.pulse_amt_slider = QSlider(Qt.Orientation.Horizontal)
        self.pulse_amt_slider.setRange(0, 15)
        self.pulse_amt_slider.setValue(5)
        self.pulse_amt_slider.setMinimumHeight(30)
        self.pulse_amt_slider.valueChanged.connect(self._on_pulse_amt_changed)
        pulse_amt_layout.addWidget(self.pulse_amt_slider)
        self.pulse_amt_label = QLabel("0.05")
        self.pulse_amt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pulse_amt_label.setStyleSheet("color: #a78bfa; font-size: 13pt; font-weight: bold; background-color: #2d1b4e; padding: 6px 14px; border-radius: 12px; border: 1px solid #6366f1;")
        pulse_amt_layout.addWidget(self.pulse_amt_label)
        layout.addLayout(pulse_amt_layout)

        group.setLayout(layout)
        return group

    def _create_actions_section(self):
        """Create Presets & Actions section."""
        group = QGroupBox("PRESETS & ACTIONS")
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Presets
        for name, algo, params in PRESETS:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, a=algo, p=params: self._load_preset(a, p))
            layout.addWidget(btn)

        layout.addStretch()

        # Attack buttons
        self.attack_btn = QPushButton("⚡ ATTACK 1 ⚡")
        self.attack_btn.setMinimumHeight(55)
        self.attack_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #dc2626, stop:1 #ea580c);
                border: 2px solid #f97316;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ef4444, stop:1 #f97316);
            }
        """)
        self.attack_btn.clicked.connect(self.attack_requested.emit)
        layout.addWidget(self.attack_btn)

        self.attack_2_btn = QPushButton("⚔ ATTACK 2 ⚔")
        self.attack_2_btn.setMinimumHeight(55)
        self.attack_2_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ea580c, stop:1 #f59e0b);
                border: 2px solid #fb923c;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #f97316, stop:1 #fbbf24);
            }
        """)
        self.attack_2_btn.clicked.connect(self.attack_2_requested.emit)
        layout.addWidget(self.attack_2_btn)

        # Undo/Redo/Export
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        self.undo_btn.setEnabled(False)
        layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        self.redo_btn.setEnabled(False)
        layout.addWidget(self.redo_btn)

        self.export_btn = QPushButton("Export JSON")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #10b981, stop:1 #059669);
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #34d399, stop:1 #10b981);
            }
        """)
        self.export_btn.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.export_btn)

        group.setLayout(layout)
        return group

    def _create_label(self, text):
        """Create a styled label."""
        label = QLabel(text)
        label.setStyleSheet("color: #d0d0d0; font-size: 9pt; font-weight: 500; padding: 2px 0px;")
        label.setMinimumWidth(100)
        label.setWordWrap(True)
        return label

    # Event Handlers
    def _on_creature_type_changed(self, text):
        """Handle creature type selection change."""
        if not self._updating:
            # Map display name to internal type
            type_map = {
                "Tentacle Creature": "tentacle",
                "Blob Creature": "blob",
                "Polyp Creature": "polyp",
                "Starfish Creature": "starfish",
                "Medusa Creature": "medusa",
                "Dragon Creature": "dragon"
            }
            self._creature_type = type_map.get(text, "tentacle")

            # Show/hide appropriate panel
            self.tentacle_panel.setVisible(self._creature_type == "tentacle")
            self.blob_panel.setVisible(self._creature_type == "blob")
            self.polyp_panel.setVisible(self._creature_type == "polyp")
            self.starfish_panel.setVisible(self._creature_type == "starfish")
            self.medusa_panel.setVisible(self._creature_type == "medusa")
            self.dragon_panel.setVisible(self._creature_type == "dragon")

            self.creature_type_changed.emit(self._creature_type)
            self.creature_changed.emit()

    def _on_anim_speed_changed(self, value):
        if not self._updating:
            self._anim_speed = value / 100.0
            self.anim_speed_label.setText(f"{self._anim_speed:.1f}x")
            self.creature_changed.emit()

    def _on_wave_amp_changed(self, value):
        if not self._updating:
            self._wave_amplitude = value / 100.0
            self.wave_amp_label.setText(f"{self._wave_amplitude:.2f}")
            self.creature_changed.emit()

    def _on_pulse_speed_changed(self, value):
        if not self._updating:
            self._pulse_speed = value / 100.0
            self.pulse_speed_label.setText(f"{self._pulse_speed:.1f}x")
            self.creature_changed.emit()

    def _on_pulse_amt_changed(self, value):
        if not self._updating:
            self._pulse_amount = value / 100.0
            self.pulse_amt_label.setText(f"{self._pulse_amount:.2f}")
            self.creature_changed.emit()

    def _load_preset(self, algorithm, params):
        """Load preset (only applies to tentacle creature)."""
        if self._creature_type == 'tentacle':
            self.tentacle_panel.set_state({
                'algorithm': algorithm,
                'params': params,
                **self.tentacle_panel.get_state()
            })

    def get_state(self):
        """Get current state from active panel."""
        state = {
            'creature_type': self._creature_type,
            'anim_speed': self._anim_speed,
            'wave_amplitude': self._wave_amplitude,
            'pulse_speed': self._pulse_speed,
            'pulse_amount': self._pulse_amount,
        }

        # Add creature-specific state
        if self._creature_type == 'tentacle':
            state.update(self.tentacle_panel.get_state())
        elif self._creature_type == 'blob':
            state.update(self.blob_panel.get_state())
        elif self._creature_type == 'polyp':
            state.update(self.polyp_panel.get_state())
        elif self._creature_type == 'starfish':
            state.update(self.starfish_panel.get_state())
        elif self._creature_type == 'medusa':
            state.update(self.medusa_panel.get_state())
        elif self._creature_type == 'dragon':
            state.update(self.dragon_panel.get_state())

        return state

    def set_state(self, state):
        """Restore state to appropriate panel."""
        self._updating = True

        # Creature type
        self._creature_type = state.get('creature_type', 'tentacle')

        # Shared animation
        self._anim_speed = state.get('anim_speed', 2.0)
        self._wave_amplitude = state.get('wave_amplitude', 0.05)
        self._pulse_speed = state.get('pulse_speed', 1.5)
        self._pulse_amount = state.get('pulse_amount', 0.05)

        # Update UI
        type_map_reverse = {
            "tentacle": "Tentacle Creature",
            "blob": "Blob Creature",
            "polyp": "Polyp Creature",
            "starfish": "Starfish Creature",
            "medusa": "Medusa Creature",
            "dragon": "Dragon Creature"
        }
        self.creature_type_combo.setCurrentText(type_map_reverse.get(self._creature_type, "Tentacle Creature"))

        self.anim_speed_slider.setValue(int(self._anim_speed * 100))
        self.wave_amp_slider.setValue(int(self._wave_amplitude * 100))
        self.pulse_speed_slider.setValue(int(self._pulse_speed * 100))
        self.pulse_amt_slider.setValue(int(self._pulse_amount * 100))

        # Restore creature-specific state
        if self._creature_type == 'tentacle':
            self.tentacle_panel.set_state(state)
        elif self._creature_type == 'blob':
            self.blob_panel.set_state(state)
        elif self._creature_type == 'polyp':
            self.polyp_panel.set_state(state)
        elif self._creature_type == 'starfish':
            self.starfish_panel.set_state(state)
        elif self._creature_type == 'medusa':
            self.medusa_panel.set_state(state)
        elif self._creature_type == 'dragon':
            self.dragon_panel.set_state(state)

        self._updating = False

    def set_undo_redo_enabled(self, can_undo, can_redo):
        """Enable/disable undo/redo buttons."""
        self.undo_btn.setEnabled(can_undo)
        self.redo_btn.setEnabled(can_redo)

    def get_algorithm_params(self):
        """Get algorithm parameters (tentacle creature only)."""
        if self._creature_type == 'tentacle':
            return self.tentacle_panel._get_algorithm_params()
        return {}
