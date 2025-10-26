"""
Combat Log Component

Message display system with color-coded message types and fade effects.
"""

from typing import Optional
from ursina import Text


class CombatLogEntry:
    """Single combat log entry with fade effect"""
    def __init__(self, message: str, msg_type: str, lifetime: float = 5.0):
        self.message = message
        self.msg_type = msg_type
        self.lifetime = lifetime
        self.age = 0.0
        self.text_entity: Optional[Text] = None
