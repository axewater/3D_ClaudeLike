"""
Centralized logging system for Claude-Like
Provides configurable log levels and filtering to reduce console spam
"""
import sys
from enum import IntEnum
from typing import Optional, Set


class LogLevel(IntEnum):
    """Log level enumeration"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class GameLogger:
    """
    Central game logger with level filtering and module filtering
    """

    def __init__(self, level: LogLevel = LogLevel.INFO, module_filter: Optional[Set[str]] = None):
        """
        Initialize the logger

        Args:
            level: Minimum log level to display
            module_filter: Optional set of module names to display (None = all modules)
        """
        self.level = level
        self.module_filter = module_filter
        self.use_colors = sys.stdout.isatty()  # Use colors if outputting to terminal

        # ANSI color codes
        self.colors = {
            LogLevel.DEBUG: '\033[90m',     # Gray
            LogLevel.INFO: '\033[0m',       # Default
            LogLevel.WARNING: '\033[93m',   # Yellow
            LogLevel.ERROR: '\033[91m',     # Red
        }
        self.color_reset = '\033[0m'

    def set_level(self, level: LogLevel):
        """Set the minimum log level"""
        self.level = level

    def set_module_filter(self, modules: Optional[Set[str]]):
        """Set module filter (None = show all)"""
        self.module_filter = modules

    def _should_log(self, level: LogLevel, module: str) -> bool:
        """Check if message should be logged based on level and module filter"""
        # Check log level
        if level < self.level:
            return False

        # Check module filter (if set)
        if self.module_filter is not None and module not in self.module_filter:
            return False

        return True

    def _format_message(self, level: LogLevel, module: str, message: str) -> str:
        """Format log message with optional color"""
        # Create prefix
        level_names = {
            LogLevel.DEBUG: 'DEBUG',
            LogLevel.INFO: 'INFO',
            LogLevel.WARNING: 'WARN',
            LogLevel.ERROR: 'ERROR',
        }

        prefix = f"[{level_names[level]}]"
        if module:
            prefix = f"[{module}] {prefix}"

        # Apply color if enabled
        if self.use_colors:
            color = self.colors.get(level, '')
            return f"{color}{prefix} {message}{self.color_reset}"
        else:
            return f"{prefix} {message}"

    def debug(self, message: str, module: str = ""):
        """Log debug message"""
        if self._should_log(LogLevel.DEBUG, module):
            print(self._format_message(LogLevel.DEBUG, module, message))

    def info(self, message: str, module: str = ""):
        """Log info message"""
        if self._should_log(LogLevel.INFO, module):
            print(self._format_message(LogLevel.INFO, module, message))

    def warning(self, message: str, module: str = ""):
        """Log warning message"""
        if self._should_log(LogLevel.WARNING, module):
            print(self._format_message(LogLevel.WARNING, module, message))

    def error(self, message: str, module: str = ""):
        """Log error message"""
        if self._should_log(LogLevel.ERROR, module):
            print(self._format_message(LogLevel.ERROR, module, message))


# Global logger instance (initialized by main.py)
_global_logger: Optional[GameLogger] = None


def init_logger(level: LogLevel = LogLevel.INFO, module_filter: Optional[Set[str]] = None):
    """Initialize the global logger"""
    global _global_logger
    _global_logger = GameLogger(level, module_filter)


def get_logger() -> GameLogger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        # Auto-initialize with INFO level if not initialized
        init_logger(LogLevel.INFO)
    return _global_logger


def parse_log_level(level_str: str) -> LogLevel:
    """Parse log level from string (case-insensitive)"""
    level_map = {
        'debug': LogLevel.DEBUG,
        'info': LogLevel.INFO,
        'warning': LogLevel.WARNING,
        'warn': LogLevel.WARNING,
        'error': LogLevel.ERROR,
    }

    level_str = level_str.lower()
    if level_str not in level_map:
        raise ValueError(f"Invalid log level: {level_str}. Valid options: debug, info, warning, error")

    return level_map[level_str]
