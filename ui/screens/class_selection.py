"""
Class selection screen with character preview and animated stat bars
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (QPainter, QColor, QFont, QLinearGradient,
                          QRadialGradient, QPen)
import time
import math
import random

import constants as c
from audio import get_audio_manager
from animations import AnimationManager, Particle
import graphics as gfx


class CharacterPreviewPanel(QWidget):
    """Left panel showing animated character preview"""
    def __init__(self):
        super().__init__()
        self.current_class = c.CLASS_WARRIOR
        self.float_offset = 0.0
        self.time_elapsed = 0.0
        self.anim_manager = AnimationManager()
        self.particle_spawn_timer = 0.0

        self.setStyleSheet("background-color: rgb(25, 25, 30);")
        self.setMinimumHeight(600)

    def set_class(self, class_type: str):
        """Set the class to display"""
        if self.current_class != class_type:
            self.current_class = class_type
            # Spawn transition particles
            self._spawn_class_particles(burst=True)

    def update_animation(self, dt: float):
        """Update animations"""
        self.time_elapsed += dt

        # Floating animation (slow sine wave)
        self.float_offset = math.sin(self.time_elapsed * 2.0) * 10

        # Update particle system
        self.anim_manager.update(dt)

        # Spawn class-themed particles periodically
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer > 0.5:
            self.particle_spawn_timer = 0.0
            self._spawn_class_particles(burst=False)

        self.update()

    def _spawn_class_particles(self, burst: bool = False):
        """Spawn class-themed particles"""
        count = 8 if burst else 2
        center_x = self.width() // 2
        center_y = self.height() // 2

        color = self._get_class_color()

        for _ in range(count):
            # Orbit around character
            angle = random.uniform(0, 6.28)
            radius = random.uniform(80, 120) if not burst else random.uniform(50, 150)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle) - 50

            # Velocity for orbit
            vx = -math.sin(angle) * 0.5
            vy = math.cos(angle) * 0.5 - 0.3  # Slight upward drift

            particle = Particle(
                x, y, vx, vy,
                color,
                size=random.uniform(2, 5),
                lifetime=random.uniform(1.5, 2.5),
                particle_type="circle" if self.current_class == c.CLASS_MAGE else "square",
                apply_gravity=False
            )
            self.anim_manager.particles.append(particle)

    def _get_class_color(self) -> QColor:
        """Get current class color"""
        colors = {
            c.CLASS_WARRIOR: c.COLOR_CLASS_WARRIOR,
            c.CLASS_MAGE: c.COLOR_CLASS_MAGE,
            c.CLASS_ROGUE: c.COLOR_CLASS_ROGUE,
            c.CLASS_RANGER: c.COLOR_CLASS_RANGER,
        }
        return colors.get(self.current_class, c.COLOR_TEXT_LIGHT)

    def paintEvent(self, event):
        """Render character preview"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(25, 25, 30))
        gradient.setColorAt(1, QColor(35, 35, 40))
        painter.fillRect(0, 0, self.width(), self.height(), gradient)

        # Draw particles in background
        for particle in self.anim_manager.particles:
            particle_color = QColor(
                particle.color.red(),
                particle.color.green(),
                particle.color.blue(),
                particle.alpha
            )
            painter.setBrush(particle_color)
            painter.setPen(Qt.PenStyle.NoPen)
            if particle.particle_type == "circle":
                painter.drawEllipse(
                    int(particle.x - particle.size / 2),
                    int(particle.y - particle.size / 2),
                    int(particle.size),
                    int(particle.size)
                )
            else:
                painter.fillRect(
                    int(particle.x - particle.size / 2),
                    int(particle.y - particle.size / 2),
                    int(particle.size),
                    int(particle.size),
                    particle_color
                )

        # Calculate character position (centered, with float offset)
        char_x = self.width() // 2 - c.TILE_SIZE * 2
        char_y = self.height() // 2 - c.TILE_SIZE * 2 + int(self.float_offset)

        # Scale up character (4x size for preview)
        scale = 4
        tile_size = c.TILE_SIZE * scale

        # Save painter state
        painter.save()

        # Create a larger virtual tile at the scaled position
        # Draw character using graphics functions
        screen_x = 0  # Will draw at specific pixel position
        screen_y = 0

        # Temporarily modify tile size for drawing
        painter.translate(char_x, char_y)

        # Draw a glowing aura behind character
        class_color = self._get_class_color()
        aura_gradient = QRadialGradient(tile_size // 2, tile_size // 2, tile_size)
        aura_gradient.setColorAt(0, QColor(class_color.red(), class_color.green(), class_color.blue(), 100))
        aura_gradient.setColorAt(0.5, QColor(class_color.red(), class_color.green(), class_color.blue(), 40))
        aura_gradient.setColorAt(1, QColor(class_color.red(), class_color.green(), class_color.blue(), 0))
        painter.fillRect(0, 0, tile_size, tile_size, aura_gradient)

        # Draw the character (scaled up) with idle animation
        gfx.draw_player(painter, screen_x, screen_y, tile_size, class_color, self.current_class, (0, 1), self.time_elapsed)

        painter.restore()

        # Draw class name below character
        painter.setPen(class_color.lighter(130))
        painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        class_names = {
            c.CLASS_WARRIOR: "WARRIOR",
            c.CLASS_MAGE: "MAGE",
            c.CLASS_ROGUE: "ROGUE",
            c.CLASS_RANGER: "RANGER",
        }
        class_name = class_names.get(self.current_class, "")
        painter.drawText(0, self.height() - 80, self.width(), 40,
                        Qt.AlignmentFlag.AlignCenter, class_name)

        # Draw class description
        painter.setPen(c.COLOR_TEXT_LIGHT)
        painter.setFont(QFont("Arial", 12))
        stats = c.CLASS_STATS.get(self.current_class, {})
        desc = stats.get("description", "")
        painter.drawText(20, self.height() - 45, self.width() - 40, 40,
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, desc)


class StatComparisonPanel(QWidget):
    """Panel showing stat bars for comparison"""
    def __init__(self):
        super().__init__()
        self.current_class = None
        self.target_values = {'hp': 0, 'attack': 0, 'defense': 0}
        self.current_values = {'hp': 0.0, 'attack': 0.0, 'defense': 0.0}

        self.setFixedHeight(120)
        self.setStyleSheet("background-color: rgb(40, 40, 45); border-radius: 10px; padding: 15px;")

    def set_class(self, class_type: str):
        """Set class and update stat targets"""
        self.current_class = class_type
        stats = c.CLASS_STATS.get(class_type, {})
        self.target_values = {
            'hp': stats.get('hp', 0),
            'attack': stats.get('attack', 0),
            'defense': stats.get('defense', 0)
        }

    def update_animation(self, dt: float):
        """Animate stat bars toward target values"""
        lerp_speed = 5.0
        for stat in ['hp', 'attack', 'defense']:
            target = self.target_values[stat]
            current = self.current_values[stat]
            # Lerp toward target
            self.current_values[stat] += (target - current) * lerp_speed * dt

    def paintEvent(self, event):
        """Draw stat bars"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(0, 0, self.width(), self.height(), QColor(40, 40, 45))

        if not self.current_class:
            return

        # Stat bar configuration
        stats_config = [
            ('HP', self.current_values['hp'], 120, QColor(100, 200, 120), 10),
            ('ATK', self.current_values['attack'], 20, QColor(255, 100, 100), 45),
            ('DEF', self.current_values['defense'], 12, QColor(100, 150, 255), 80),
        ]

        for stat_name, value, max_val, color, y_offset in stats_config:
            y_pos = y_offset

            # Stat label
            painter.setPen(c.COLOR_TEXT_LIGHT)
            painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            painter.drawText(15, y_pos, 50, 20, Qt.AlignmentFlag.AlignLeft, stat_name)

            # Value label
            painter.drawText(self.width() - 60, y_pos, 50, 20,
                           Qt.AlignmentFlag.AlignRight, f"{int(value)}")

            # Bar background
            bar_x = 70
            bar_width = self.width() - 140
            bar_height = 18
            painter.fillRect(bar_x, y_pos - 2, bar_width, bar_height, QColor(30, 30, 35))

            # Bar fill (animated)
            fill_width = int((value / max_val) * bar_width)
            if fill_width > 0:
                # Gradient fill
                gradient = QLinearGradient(bar_x, y_pos, bar_x + fill_width, y_pos)
                gradient.setColorAt(0, color.darker(110))
                gradient.setColorAt(1, color.lighter(120))
                painter.fillRect(bar_x, y_pos - 2, fill_width, bar_height, gradient)

            # Bar border
            painter.setPen(QColor(70, 70, 75))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(bar_x, y_pos - 2, bar_width, bar_height)


class ClassCard(QWidget):
    """Individual class selection card with hover effects"""
    clicked = pyqtSignal()
    hovered = pyqtSignal()
    unhovered = pyqtSignal()

    def __init__(self, class_type: str, color: QColor, label: str, abilities: list):
        super().__init__()
        self.class_type = class_type
        self.color = color
        self.label = label
        self.abilities = abilities
        self.is_hovered = False
        self.is_selected = False
        self.hover_glow = 0.0

        self.setMinimumSize(220, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()

    def setup_ui(self):
        """Setup card UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Class name
        name_label = QLabel(self.label)
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()}); background: transparent; border: none;")
        layout.addWidget(name_label)

        # Stats (mini version)
        stats = c.CLASS_STATS[self.class_type]
        stats_text = f"HP:{stats['hp']} ATK:{stats['attack']} DEF:{stats['defense']}"
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("color: rgb(180, 180, 180); background: transparent; border: none;")
        layout.addWidget(stats_label)

        # Abilities (compact)
        abilities_text = " • ".join(self.abilities)
        abilities_label = QLabel(abilities_text)
        abilities_label.setFont(QFont("Arial", 8))
        abilities_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        abilities_label.setWordWrap(True)
        abilities_label.setStyleSheet("color: rgb(150, 150, 180); background: transparent; border: none; padding: 4px;")
        layout.addWidget(abilities_label)

        layout.addStretch()

        # SELECT label
        select_label = QLabel("CLICK TO SELECT")
        select_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        select_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        select_label.setStyleSheet("color: rgb(120, 120, 130); background: transparent; border: none;")
        layout.addWidget(select_label)

        self.setLayout(layout)

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.update()

    def enterEvent(self, event):
        """Mouse enter"""
        self.is_hovered = True
        self.hovered.emit()
        self.update()

    def leaveEvent(self, event):
        """Mouse leave"""
        self.is_hovered = False
        self.unhovered.emit()
        self.update()

    def mousePressEvent(self, event):
        """Mouse click"""
        self.clicked.emit()

    def paintEvent(self, event):
        """Custom paint with glow effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine colors based on state
        if self.is_selected:
            border_color = self.color.lighter(140)
            border_width = 3
            bg_alpha = 30
        elif self.is_hovered:
            border_color = self.color.lighter(120)
            border_width = 3
            bg_alpha = 20
        else:
            border_color = QColor(70, 70, 80)
            border_width = 2
            bg_alpha = 10

        # Background with class tint
        bg_color = QColor(
            min(40 + self.color.red() // 10, 60),
            min(40 + self.color.green() // 10, 60),
            min(45 + self.color.blue() // 10, 65),
            bg_alpha if not self.is_selected else 40
        )
        painter.fillRect(0, 0, self.width(), self.height(), bg_color)

        # Glow effect when hovered or selected
        if self.is_hovered or self.is_selected:
            glow_gradient = QLinearGradient(0, 0, self.width(), self.height())
            glow_color = QColor(self.color.red(), self.color.green(), self.color.blue(), 40)
            glow_gradient.setColorAt(0, glow_color)
            glow_gradient.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 10))
            painter.fillRect(0, 0, self.width(), self.height(), glow_gradient)

        # Border
        painter.setPen(QPen(border_color, border_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            border_width // 2,
            border_width // 2,
            self.width() - border_width,
            self.height() - border_width,
            8, 8
        )


class ClassSelectionScreen(QWidget):
    """Enhanced class selection screen with live preview and animations"""
    class_selected = pyqtSignal(str)
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Class ability descriptions
        self.class_abilities = {
            c.CLASS_WARRIOR: ["Healing Touch", "Whirlwind", "Dash"],
            c.CLASS_MAGE: ["Fireball", "Frost Nova", "Healing Touch"],
            c.CLASS_ROGUE: ["Shadow Step", "Dash", "Healing Touch"],
            c.CLASS_RANGER: ["Fireball", "Dash", "Healing Touch"],
        }

        # Animation system
        self.anim_manager = AnimationManager()
        self.time_elapsed = 0.0
        self.last_time = time.time()

        # Selected/hovered class tracking
        self.selected_class = None
        self.hovered_class = None

        # Animation values for smooth transitions
        self.preview_float_offset = 0.0
        self.stat_bar_progress = {
            'hp': 0.0,
            'attack': 0.0,
            'defense': 0.0
        }

        # Class cards for hover detection
        self.class_cards = {}

        self.setup_ui()

        # Start animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

    def setup_ui(self):
        """Setup the enhanced split-view UI"""
        self.setStyleSheet(f"background-color: rgb({c.COLOR_PANEL_BG.red()}, {c.COLOR_PANEL_BG.green()}, {c.COLOR_PANEL_BG.blue()});")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        title = QLabel("CHOOSE YOUR CLASS")
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: rgb({c.COLOR_TEXT_LIGHT.red()}, {c.COLOR_TEXT_LIGHT.green()}, {c.COLOR_TEXT_LIGHT.blue()}); padding: 25px; background-color: rgb(25, 25, 30);")
        main_layout.addWidget(title)

        # Split view: Preview (left) | Class Grid (right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        # LEFT: Character Preview Panel
        self.preview_panel = CharacterPreviewPanel()
        self.preview_panel.setFixedWidth(int(c.WINDOW_WIDTH * 0.45))
        content_layout.addWidget(self.preview_panel)

        # RIGHT: Class Selection Grid
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(30, 30, 30, 20)
        right_layout.setSpacing(20)

        # Stat comparison panel
        self.stat_panel = StatComparisonPanel()
        right_layout.addWidget(self.stat_panel)

        # Class cards in 2x2 grid
        grid_container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        classes = [
            (c.CLASS_WARRIOR, c.COLOR_CLASS_WARRIOR, "WARRIOR", 0, 0),
            (c.CLASS_MAGE, c.COLOR_CLASS_MAGE, "MAGE", 0, 1),
            (c.CLASS_ROGUE, c.COLOR_CLASS_ROGUE, "ROGUE", 1, 0),
            (c.CLASS_RANGER, c.COLOR_CLASS_RANGER, "RANGER", 1, 1),
        ]

        for class_type, color, label_text, row, col in classes:
            card = ClassCard(class_type, color, label_text, self.class_abilities[class_type])
            card.clicked.connect(lambda ct=class_type: self._on_class_select(ct))
            card.hovered.connect(lambda ct=class_type: self._on_class_hover(ct))
            card.unhovered.connect(self._on_class_unhover)
            self.class_cards[class_type] = card
            grid_layout.addWidget(card, row, col)

        grid_container.setLayout(grid_layout)
        right_layout.addWidget(grid_container)

        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        back_button.setFixedHeight(45)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(60, 60, 70);
                color: rgb(180, 180, 185);
                border: 2px solid rgb(80, 80, 90);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(80, 80, 90);
                border: 2px solid rgb(150, 150, 180);
                color: rgb(220, 220, 220);
            }
        """)
        back_button.clicked.connect(self._on_back_clicked)
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        right_layout.addWidget(back_button)

        right_panel.setLayout(right_layout)
        content_layout.addWidget(right_panel)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Initialize with warrior selected
        self.selected_class = c.CLASS_WARRIOR
        self._update_preview()

    def _on_class_select(self, class_type: str):
        """Handle class selection"""
        audio = get_audio_manager()
        audio.play_ui_select()
        self.selected_class = class_type
        self._update_preview()

        # Highlight selected card
        for ct, card in self.class_cards.items():
            card.set_selected(ct == class_type)

        # Play class name voice
        class_names = {
            c.CLASS_WARRIOR: "Warrior",
            c.CLASS_MAGE: "Mage",
            c.CLASS_ROGUE: "Rogue",
            c.CLASS_RANGER: "Ranger",
        }
        class_name = class_names.get(class_type, "")
        if class_name:
            audio.play_voice_class(class_name)

        # Emit signal to start game
        self.class_selected.emit(class_type)

    def _on_class_hover(self, class_type: str):
        """Handle class hover"""
        if self.hovered_class != class_type:
            audio = get_audio_manager()
            audio.play_ui_hover()
            self.hovered_class = class_type
            self._update_preview()

    def _on_class_unhover(self):
        """Handle mouse leaving class card"""
        self.hovered_class = None
        self._update_preview()

    def _update_preview(self):
        """Update character preview and stats"""
        display_class = self.hovered_class if self.hovered_class else self.selected_class
        if display_class:
            self.preview_panel.set_class(display_class)
            self.stat_panel.set_class(display_class)

    def _on_back_clicked(self):
        """Handle back button click"""
        audio = get_audio_manager()
        audio.play_ui_select()
        self.back_clicked.emit()

    def update_animation(self):
        """Update animations"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time_elapsed += dt

        # Update animation manager
        self.anim_manager.update(dt)

        # Update preview panel animations
        if hasattr(self, 'preview_panel'):
            self.preview_panel.update_animation(dt)

        # Update stat panel animations
        if hasattr(self, 'stat_panel'):
            self.stat_panel.update_animation(dt)

        # Update display
        self.update()
