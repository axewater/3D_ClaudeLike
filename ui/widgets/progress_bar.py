"""
Custom progress bar widget for health and experience display
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont

import constants as c


class ProgressBar(QWidget):
    """Custom progress bar widget"""
    def __init__(self, height=20):
        super().__init__()
        self.value = 0
        self.max_value = 100
        self.bar_color = c.COLOR_HP_BAR_FULL
        self.bg_color = c.COLOR_HP_BAR_BG
        self.text = ""
        self.setFixedHeight(height)
        self.setMinimumWidth(200)

    def set_value(self, value: int, max_value: int, text: str = "", color: QColor = None):
        """Set progress bar value"""
        self.value = value
        self.max_value = max_value
        self.text = text
        if color:
            self.bar_color = color
        self.update()

    def paintEvent(self, event):
        """Paint the progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(0, 0, self.width(), self.height(), self.bg_color)

        # Draw progress
        if self.max_value > 0:
            progress_width = int((self.value / self.max_value) * self.width())
            painter.fillRect(0, 0, progress_width, self.height(), self.bar_color)

        # Draw border
        painter.setPen(QColor(70, 70, 75))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Draw text
        if self.text:
            painter.setPen(c.COLOR_TEXT_LIGHT)
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(0, 0, self.width(), self.height(),
                           Qt.AlignmentFlag.AlignCenter, self.text)
