"""Custom color picker button widget."""

from PyQt6.QtWidgets import QPushButton, QColorDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor


class ColorButton(QPushButton):
    """Custom button that opens a color picker."""
    colorChanged = pyqtSignal(tuple)  # Emits RGB tuple (0-1 range)

    def __init__(self, initial_color=(0.6, 0.3, 0.7), parent=None):
        super().__init__(parent)
        self.color = initial_color
        self.setMinimumHeight(45)
        self.setMinimumWidth(100)
        self.clicked.connect(self._pick_color)
        self._update_display()

    def _update_display(self):
        """Update button appearance to show current color."""
        r, g, b = [int(c * 255) for c in self.color]
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgb({r}, {g}, {b}),
                                           stop:1 rgb({max(0, r-30)}, {max(0, g-30)}, {max(0, b-30)}));
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                min-height: 45px;
                color: white;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                border: 2px solid #8b5cf6;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgb({min(255, r+20)}, {min(255, g+20)}, {min(255, b+20)}),
                                           stop:1 rgb({r}, {g}, {b}));
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgb({max(0, r-40)}, {max(0, g-40)}, {max(0, b-40)}),
                                           stop:1 rgb({max(0, r-20)}, {max(0, g-20)}, {max(0, b-20)}));
            }}
        """)
        self.setText(f"RGB({r}, {g}, {b})")

    def _pick_color(self):
        """Open color picker dialog."""
        r, g, b = [int(c * 255) for c in self.color]
        initial = QColor(r, g, b)
        color = QColorDialog.getColor(initial, self, "Choose Color")

        if color.isValid():
            self.color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self._update_display()
            self.colorChanged.emit(self.color)

    def set_color(self, rgb_tuple):
        """Set color programmatically."""
        self.color = rgb_tuple
        self._update_display()
