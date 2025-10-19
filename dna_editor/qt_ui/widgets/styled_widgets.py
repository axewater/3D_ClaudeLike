"""Shared widget styles and helper functions."""

from PyQt6.QtWidgets import QLabel


# Spinbox style constant
SPINBOX_STYLE = """
    QSpinBox {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 2px solid #4a4a4a;
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 11pt;
        font-weight: bold;
    }
    QSpinBox:hover {
        border: 2px solid #8b5cf6;
        background-color: #323232;
    }
    QSpinBox:focus {
        border: 2px solid #a78bfa;
        background-color: #353535;
    }
    QSpinBox::up-button {
        background-color: #3a3a3a;
        border-radius: 3px;
        border: none;
        width: 24px;
        subcontrol-origin: border;
        subcontrol-position: top right;
    }
    QSpinBox::down-button {
        background-color: #3a3a3a;
        border-radius: 3px;
        border: none;
        width: 24px;
        subcontrol-origin: border;
        subcontrol-position: bottom right;
    }
    QSpinBox::up-button:hover {
        background-color: #8b5cf6;
    }
    QSpinBox::down-button:hover {
        background-color: #8b5cf6;
    }
    QSpinBox::up-arrow {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-bottom: 6px solid #e0e0e0;
    }
    QSpinBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #e0e0e0;
    }
    QSpinBox::up-arrow:hover {
        border-bottom-color: #ffffff;
    }
    QSpinBox::down-arrow:hover {
        border-top-color: #ffffff;
    }
"""

# ComboBox style constant
COMBOBOX_STYLE = """
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


def create_label(text):
    """Create a styled label."""
    label = QLabel(text)
    label.setStyleSheet("color: #d0d0d0; font-size: 9pt; font-weight: 500; padding: 2px 0px;")
    label.setMinimumWidth(100)
    label.setWordWrap(True)
    return label
