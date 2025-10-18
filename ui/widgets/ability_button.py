"""
Custom button widget for displaying and triggering abilities
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


class AbilityButton(QPushButton):
    """Custom button for abilities with visual feedback"""
    ability_clicked = pyqtSignal(int)  # Emits ability index

    def __init__(self, ability_index: int):
        super().__init__()
        self.ability_index = ability_index
        self.is_ready = False
        self.ability_name = ""
        self.ability_status = ""

        self.setMinimumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.ability_clicked.emit(self.ability_index))

    def set_ability_state(self, name: str, is_ready: bool, status: str):
        """Update ability state and appearance"""
        self.ability_name = name
        self.is_ready = is_ready
        self.ability_status = status

        # Update text
        key_num = self.ability_index + 1
        self.setText(f"[{key_num}] {name}: {status}")

        # Update style based on readiness
        if is_ready:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(81, 207, 102, 0.2);
                    color: rgb(81, 207, 102);
                    border: 2px solid rgb(81, 207, 102);
                    border-radius: 4px;
                    padding: 6px;
                    font-family: 'Courier New';
                    font-size: 9pt;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(81, 207, 102, 0.4);
                    border: 2px solid rgb(100, 230, 120);
                }
                QPushButton:pressed {
                    background-color: rgba(81, 207, 102, 0.6);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 100, 100, 0.2);
                    color: rgb(150, 150, 150);
                    border: 2px solid rgb(100, 100, 100);
                    border-radius: 4px;
                    padding: 6px;
                    font-family: 'Courier New';
                    font-size: 9pt;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 100, 0.3);
                }
            """)
