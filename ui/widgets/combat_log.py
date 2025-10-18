"""
Modern scrollable combat log widget with Discord/Slack-style UX
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                               QGraphicsOpacityEffect, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient
import time

import constants as c


class CombatLogEntry(QLabel):
    """Single combat log entry with icon and rich formatting"""

    def __init__(self, text: str, icon: str, color: QColor, is_critical: bool = False):
        super().__init__()
        self.entry_text = text
        self.icon = icon
        self.base_color = color
        self.is_critical = is_critical
        self.creation_time = time.time()

        # Setup label
        self.setFont(QFont("Segoe UI", 10))
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setContentsMargins(0, 0, 0, 0)

        # Styling with proper spacing
        border_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 100)"
        bg_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 15)"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 4px;
                padding: 8px 10px;
                margin: 2px 4px;
            }}
        """)

        # Create the rich text content
        self._update_display()

        # Fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(200)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in_animation.start()

    def _update_display(self):
        """Update the display text with rich formatting"""
        # Style for critical entries
        icon_style = "font-size: 13pt; font-weight: bold;"
        if self.is_critical:
            icon_style += " filter: drop-shadow(0 0 3px rgba(255, 215, 0, 0.8));"

        html = f"""
        <div style="color: rgb({self.base_color.red()}, {self.base_color.green()}, {self.base_color.blue()});">
            <span style="{icon_style}">{self.icon}</span>
            <span style="margin-left: 8px; line-height: 1.4;">{self.entry_text}</span>
        </div>
        """
        self.setText(html)


class ScrollIndicator(QPushButton):
    """Floating indicator showing new messages when scrolled up"""

    def __init__(self):
        super().__init__("↓ New Messages")
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 150, 255, 200);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 6px 16px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: rgba(120, 170, 255, 230);
            }
        """)

        self.hide()


class CombatLogWidget(QWidget):
    """Modern scrollable combat log with auto-scroll and hover detection"""

    # Icon mappings for different event types
    ICON_MAP = {
        "player_attack": "⚔️",
        "player_attack_crit": "⚡",
        "enemy_attack": "🗡️",
        "damage": "💥",
        "crit": "⚡",
        "kill": "💀",
        "death": "☠️",
        "heal": "💚",
        "ability_fire": "🔥",
        "ability_ice": "❄️",
        "ability_dash": "💨",
        "ability_heal": "✨",
        "ability_shadow": "🌑",
        "ability_whirlwind": "🌀",
        "ability": "✨",
        "loot": "🎁",
        "loot_rare": "💎",
        "loot_legendary": "⭐",
        "pickup": "📦",
        "equip": "🎯",
        "levelup": "🆙",
        "stairs": "🚪",
        "potion": "🧪",
        "event": "📢",
        "warning": "⚠️",
    }

    # Color mappings for event types
    COLOR_MAP = {
        "player_attack": QColor(100, 200, 255),
        "player_attack_crit": QColor(255, 215, 0),
        "enemy_attack": QColor(255, 100, 100),
        "damage": QColor(255, 107, 107),
        "crit": QColor(255, 215, 0),
        "kill": QColor(200, 200, 200),
        "death": QColor(255, 68, 68),
        "heal": QColor(81, 207, 102),
        "ability_fire": QColor(255, 140, 0),
        "ability_ice": QColor(135, 206, 250),
        "ability_dash": QColor(255, 255, 150),
        "ability_heal": QColor(144, 238, 144),
        "ability_shadow": QColor(138, 43, 226),
        "ability_whirlwind": QColor(173, 216, 230),
        "ability": QColor(186, 85, 211),
        "loot": QColor(255, 215, 0),
        "loot_rare": QColor(147, 112, 219),
        "loot_legendary": QColor(255, 165, 0),
        "pickup": QColor(255, 212, 59),
        "equip": QColor(116, 196, 255),
        "levelup": QColor(169, 227, 75),
        "stairs": QColor(150, 100, 255),
        "potion": QColor(255, 80, 200),
        "event": QColor(116, 192, 252),
        "warning": QColor(255, 193, 7),
    }

    def __init__(self):
        super().__init__()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Create scroll area (like Discord/Slack)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Modern scrollbar styling
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: rgba({c.COLOR_SECTION_BG.red()}, {c.COLOR_SECTION_BG.green()}, {c.COLOR_SECTION_BG.blue()}, 200);
                border: 1px solid rgb({c.COLOR_SECTION_BORDER.red()}, {c.COLOR_SECTION_BORDER.green()}, {c.COLOR_SECTION_BORDER.blue()});
                border-radius: 6px;
            }}
            QScrollBar:vertical {{
                background-color: rgba(40, 40, 45, 150);
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(100, 100, 110, 180);
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(130, 130, 140, 200);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # Content widget inside scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(6, 6, 6, 6)
        self.content_layout.setSpacing(3)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        # Scroll indicator (shows when scrolled up and new messages arrive)
        self.scroll_indicator = ScrollIndicator()
        self.scroll_indicator.clicked.connect(self._scroll_to_bottom)
        self.scroll_indicator.setParent(self)
        self.scroll_indicator.hide()

        # Track entries
        self.entries = []
        self.max_entries = 50  # Keep last 50 messages

        # Track scroll state
        self.is_hovered = False
        self.user_scrolled_up = False

        # Install event filter for hover detection
        self.scroll_area.viewport().installEventFilter(self)

        # Get scrollbar
        self.scrollbar = self.scroll_area.verticalScrollBar()
        self.scrollbar.valueChanged.connect(self._on_scroll)

        # Auto-scroll timer
        self.auto_scroll_timer = QTimer()
        self.auto_scroll_timer.timeout.connect(self._check_auto_scroll)
        self.auto_scroll_timer.start(100)  # Check every 100ms

    def eventFilter(self, obj, event):
        """Detect hover to pause auto-scroll (modern UX pattern)"""
        if obj == self.scroll_area.viewport():
            if event.type() == QEvent.Type.Enter:
                self.is_hovered = True
            elif event.type() == QEvent.Type.Leave:
                self.is_hovered = False
                # When leaving, auto-scroll if at bottom
                if self._is_at_bottom():
                    self.user_scrolled_up = False

        return super().eventFilter(obj, event)

    def _on_scroll(self, value):
        """Track if user manually scrolled up"""
        if self.is_hovered and not self._is_at_bottom():
            self.user_scrolled_up = True
        elif self._is_at_bottom():
            self.user_scrolled_up = False
            self.scroll_indicator.hide()

    def _is_at_bottom(self):
        """Check if scrollbar is at bottom"""
        return self.scrollbar.value() >= self.scrollbar.maximum() - 10

    def _scroll_to_bottom(self):
        """Smoothly scroll to bottom"""
        self.scrollbar.setValue(self.scrollbar.maximum())
        self.user_scrolled_up = False
        self.scroll_indicator.hide()

    def _check_auto_scroll(self):
        """Auto-scroll to bottom if conditions are met"""
        # Auto-scroll only if:
        # 1. Not hovered (user not reading)
        # 2. User hasn't manually scrolled up
        # 3. OR already at bottom
        if (not self.is_hovered and not self.user_scrolled_up) or self._is_at_bottom():
            self._scroll_to_bottom()

    def add_entry(self, text: str, event_type: str = "event", is_critical: bool = False):
        """Add a new entry to the combat log"""
        # Get icon and color for event type
        icon = self.ICON_MAP.get(event_type, "📢")
        color = self.COLOR_MAP.get(event_type, QColor(200, 200, 200))

        # Create new entry
        entry = CombatLogEntry(text, icon, color, is_critical)

        # Add to layout and tracking
        self.content_layout.addWidget(entry)
        self.entries.append(entry)

        # Remove old entries if too many
        while len(self.entries) > self.max_entries:
            old_entry = self.entries.pop(0)
            self.content_layout.removeWidget(old_entry)
            old_entry.deleteLater()

        # Show scroll indicator if user is scrolled up
        if self.user_scrolled_up and not self._is_at_bottom():
            self.scroll_indicator.show()

    def resizeEvent(self, event):
        """Position scroll indicator at bottom-center"""
        super().resizeEvent(event)
        indicator_width = self.scroll_indicator.sizeHint().width()
        indicator_height = self.scroll_indicator.sizeHint().height()
        x = (self.width() - indicator_width) // 2
        y = self.height() - indicator_height - 16
        self.scroll_indicator.setGeometry(x, y, indicator_width, indicator_height)

    def clear(self):
        """Clear all entries"""
        for entry in self.entries:
            self.content_layout.removeWidget(entry)
            entry.deleteLater()
        self.entries.clear()
