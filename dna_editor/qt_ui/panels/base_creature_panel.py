"""Base class for creature-specific control panels."""

from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QSlider, QSpinBox, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from ..widgets import SPINBOX_STYLE, COMBOBOX_STYLE, create_label


class BaseCreaturePanel(QWidget):
    """Abstract base class for creature-specific panels."""

    # Signals that all creature panels should emit
    creature_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False  # Flag to prevent signal loops during programmatic updates

    def _create_card(self, title, min_width=280):
        """Create a styled group box card."""
        group = QGroupBox(title)
        group.setMinimumWidth(min_width)
        group.setStyleSheet("""
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2a2a2a, stop:1 #252525);
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                font-size: 11pt;
                font-weight: bold;
                color: #a78bfa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 6px;
                color: white;
            }
        """)
        return group

    def _create_label(self, text):
        """Create a styled label."""
        return create_label(text)

    def _create_spinbox(self, min_val, max_val, initial_val, callback):
        """Create a styled spinbox with standard settings."""
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(initial_val)
        spinbox.setMinimumHeight(35)
        spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        spinbox.setStyleSheet(SPINBOX_STYLE)
        spinbox.valueChanged.connect(callback)
        return spinbox

    def _create_combobox(self, items, callback):
        """Create a styled combobox."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setMinimumHeight(40)
        combo.setStyleSheet(COMBOBOX_STYLE)
        combo.currentTextChanged.connect(callback)
        return combo

    def _create_slider(self, min_val, max_val, initial_val, callback, tick_interval=10):
        """Create a styled slider."""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial_val)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(tick_interval)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #1a1a1a, stop:1 #2a2a2a);
                height: 8px;
                border-radius: 4px;
                border: 1px solid #3a3a3a;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #6366f1, stop:1 #8b5cf6);
                border: 2px solid #4a4a4a;
                width: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #7c3aed, stop:1 #a78bfa);
                border: 2px solid #8b5cf6;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 4px;
            }
        """)
        slider.valueChanged.connect(callback)
        return slider

    def _emit_change(self):
        """Emit creature_changed signal if not in updating mode."""
        if not self._updating:
            self.creature_changed.emit()

    def get_state(self):
        """Get current state - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_state()")

    def set_state(self, state):
        """Set state - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement set_state()")
