"""
UI package for Claude-Like

This package contains all UI components organized into screens and widgets.
Exports all components for backward compatibility with the original ui.py module.
"""

# Import screens
from ui.screens import (
    TitleScreen,
    MainMenuScreen,
    SettingsScreen,
    ClassSelectionScreen,
    ClassCard,
    CharacterPreviewPanel,
    StatComparisonPanel,
)

# Import widgets
from ui.widgets import (
    AbilityButton,
    ProgressBar,
    GameWidget,
    StatsPanel,
)

# Import main window
from ui.main_window import MainWindow

# Export all for backward compatibility
__all__ = [
    # Main window
    'MainWindow',
    # Screens
    'TitleScreen',
    'MainMenuScreen',
    'SettingsScreen',
    'ClassSelectionScreen',
    'ClassCard',
    'CharacterPreviewPanel',
    'StatComparisonPanel',
    # Widgets
    'AbilityButton',
    'ProgressBar',
    'GameWidget',
    'StatsPanel',
]
