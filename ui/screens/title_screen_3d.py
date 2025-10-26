"""
3D OpenGL Animated Title Screen
Features flying letters with particle effects
"""
import math
import random
import time
from typing import List, Tuple

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics, QImage, QPainter, QColor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from audio import get_audio_manager


class Letter3D:
    """Represents a single 3D animated letter"""
    def __init__(self, char: str, final_x: float, final_y: float, delay: float, duration: float, texture_id: int = 0):
        self.char = char
        self.final_x = final_x
        self.final_y = final_y
        self.final_z = 0.0
        self.texture_id = texture_id  # OpenGL texture ID for this letter

        # Animation timing
        self.delay = delay  # Delay before starting animation
        self.duration = duration  # How long the flight takes
        self.time = 0.0
        self.state = "waiting"  # waiting, flying, landed

        # Starting position (off-screen, far back, high up)
        angle = random.uniform(-30, 30)
        self.start_x = final_x + random.uniform(-15, 15)
        self.start_y = final_y + 20 + random.uniform(5, 10)
        self.start_z = -50 + random.uniform(-10, 10)

        # Current position
        self.x = self.start_x
        self.y = self.start_y
        self.z = self.start_z

        # Rotation for spinning effect
        self.rotation_x = random.uniform(720, 1080)  # Multiple spins
        self.rotation_y = random.uniform(360, 540)
        self.rotation_z = random.uniform(180, 360)
        self.current_rotation_x = 0.0
        self.current_rotation_y = 0.0
        self.current_rotation_z = 0.0

        # Particle burst flag
        self.has_burst = False

        # Color (purple-blue gradient)
        self.color = [0.6 + random.uniform(0, 0.2), 0.4 + random.uniform(0, 0.3), 1.0]

        # Glow intensity
        self.glow = 0.0

        # Whoosh sound channel (for stopping when landing)
        self.whoosh_channel = None

    def update(self, dt: float) -> Tuple[bool, bool]:
        """Update animation state. Returns (trigger_burst, started_flying)"""
        self.time += dt
        trigger_burst = False
        started_flying = False

        if self.state == "waiting":
            if self.time >= self.delay:
                self.state = "flying"
                started_flying = True
                return False, started_flying

        elif self.state == "flying":
            # Calculate progress through flight (0 to 1)
            flight_time = self.time - self.delay
            progress = min(flight_time / self.duration, 1.0)

            # Ease-in-out cubic for dramatic effect (slow start, fast middle, gentle landing)
            if progress < 0.5:
                eased = 4 * progress ** 3  # Slow acceleration at start
            else:
                eased = 1 - pow(-2 * progress + 2, 3) / 2  # Fast then gentle deceleration

            # Interpolate position
            self.x = self.start_x + (self.final_x - self.start_x) * eased
            self.y = self.start_y + (self.final_y - self.start_y) * eased
            self.z = self.start_z + (self.final_z - self.start_z) * eased

            # Rotation (dramatic: slow spin at start, then fast)
            spin_progress = progress ** 2  # Quadratic ease-in for rotation
            self.current_rotation_x = self.rotation_x * spin_progress
            self.current_rotation_y = self.rotation_y * spin_progress
            self.current_rotation_z = self.rotation_z * spin_progress

            # Check if landed
            if progress >= 1.0:
                self.state = "landed"
                self.x = self.final_x
                self.y = self.final_y
                self.z = self.final_z
                self.current_rotation_x = 0
                self.current_rotation_y = 0
                self.current_rotation_z = 0
                trigger_burst = True

        elif self.state == "landed":
            # Pulsing glow effect
            self.glow = 0.3 + 0.2 * math.sin(self.time * 3.0)

        return trigger_burst, started_flying


class Particle3D:
    """3D particle for burst effects with enhanced visuals"""
    def __init__(self, x: float, y: float, z: float, vx: float, vy: float, vz: float,
                 color: List[float], particle_type: str = 'debris'):
        self.x = x
        self.y = y
        self.z = z
        self.prev_x = x  # For motion blur trails
        self.prev_y = y
        self.prev_z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.color = color[:]
        self.lifetime = 0.0
        self.particle_type = particle_type  # 'debris', 'spark', 'dust', 'glow'

        # Type-specific properties
        if particle_type == 'spark':
            self.max_lifetime = random.uniform(0.2, 0.4)
            self.size = random.uniform(0.08, 0.15)
            self.rotation_speed = random.uniform(10, 20)
        elif particle_type == 'dust':
            self.max_lifetime = random.uniform(0.5, 1.0)
            self.size = random.uniform(0.02, 0.06)
            self.rotation_speed = random.uniform(2, 5)
        elif particle_type == 'glow':
            self.max_lifetime = random.uniform(0.3, 0.6)
            self.size = random.uniform(0.12, 0.25)
            self.rotation_speed = random.uniform(1, 3)
        else:  # debris
            self.max_lifetime = random.uniform(0.4, 0.8)
            self.size = random.uniform(0.05, 0.15)
            self.rotation_speed = random.uniform(5, 15)

        self.rotation = random.uniform(0, 360)
        self.alpha = 1.0

    def update(self, dt: float) -> bool:
        """Update particle. Returns True if still alive"""
        self.lifetime += dt

        if self.lifetime >= self.max_lifetime:
            return False

        # Store previous position for trail
        self.prev_x = self.x
        self.prev_y = self.y
        self.prev_z = self.z

        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        # Apply gravity (less for dust/glow)
        if self.particle_type == 'dust':
            self.vy -= 2.0 * dt
        elif self.particle_type == 'glow':
            self.vy -= 1.0 * dt
        else:
            self.vy -= 5.0 * dt

        # Friction (more for dust)
        friction = 0.96 if self.particle_type == 'dust' else 0.98
        self.vx *= friction
        self.vz *= friction

        # Rotation
        self.rotation += self.rotation_speed * dt

        # Fade out
        self.alpha = 1.0 - (self.lifetime / self.max_lifetime)

        return True


class TitleScreen3D(QOpenGLWidget):
    """3D animated title screen with flying letters"""
    continue_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Animation state
        self.letters: List[Letter3D] = []
        self.particles: List[Particle3D] = []
        self.time_elapsed = 0.0
        self.last_time = time.time()
        self.animation_complete = False

        # Star tunnel state - list of (x, y, z, angle, speed, size)
        self.stars = []
        self._init_stars()

        # Camera
        self.camera_shake = 0.0
        self.camera_zoom = 0.0

        # Prompt fade
        self.prompt_fade = 0.0

        # Letter textures (created in initializeGL)
        self.letter_textures = {}

        # Face textures for cube sides (created in initializeGL)
        self.brick_side_texture = None
        self.brick_back_texture = None
        self.stone_top_texture = None
        self.stone_bottom_texture = None

        # Letters will be initialized in initializeGL (after OpenGL context is ready)

        # Timer for animation updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Audio
        self.audio = get_audio_manager()

    def _draw_brick_pattern(self, painter: QPainter, width: int, height: int):
        """Draw brick pattern with mortar lines"""
        # Brick colors (varied gray-brown tones)
        brick_base = QColor(65, 60, 55)
        mortar = QColor(95, 90, 85)

        # Fill with mortar color first
        painter.fillRect(0, 0, width, height, mortar)

        # Draw bricks in rows
        brick_height = height // 4
        brick_width = width // 3
        mortar_size = 3

        for row in range(4):
            y = row * brick_height
            # Stagger every other row
            offset = (brick_width // 2) if row % 2 == 1 else 0

            for col in range(-1, 4):  # Extra columns for offset
                x = col * brick_width + offset

                # Vary brick color slightly
                variation = random.randint(-8, 8)
                brick_color = QColor(
                    brick_base.red() + variation,
                    brick_base.green() + variation,
                    brick_base.blue() + variation
                )

                # Draw brick (leaving mortar gaps)
                brick_rect = (
                    x + mortar_size,
                    y + mortar_size,
                    brick_width - mortar_size * 2,
                    brick_height - mortar_size * 2
                )
                painter.fillRect(*brick_rect, brick_color)

                # Add some texture/cracks to brick
                painter.setPen(QColor(brick_base.red() - 15, brick_base.green() - 15, brick_base.blue() - 15))
                for _ in range(2):
                    crack_x = x + random.randint(mortar_size, brick_width - mortar_size)
                    crack_y = y + random.randint(mortar_size, brick_height - mortar_size)
                    crack_len = random.randint(5, 15)
                    painter.drawLine(crack_x, crack_y, crack_x + crack_len, crack_y + random.randint(-3, 3))

    def _add_weathering(self, painter: QPainter, width: int, height: int):
        """Add weathering effects (age marks, stains)"""
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)

        # Random dark spots and stains
        for _ in range(15):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(8, 25)
            opacity = random.randint(30, 80)

            stain_color = QColor(50, 45, 40, opacity)
            painter.setBrush(stain_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x - size // 2, y - size // 2, size, size)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

    def _draw_organic_moss_patch(self, painter: QPainter, x: float, y: float, size: float, moss_color: QColor, draping: bool = False):
        """Draw an organic-looking moss patch with irregular edges and spreading patterns

        Args:
            draping: If True, tendrils grow primarily downward for draping effect
        """
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF

        # Main irregular blob shape (using polygon)
        num_points = random.randint(8, 16)
        points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            # Vary the radius randomly for irregular edges
            radius_var = random.uniform(0.5, 1.0)
            radius = size * radius_var

            # Add some wobble to the angle
            angle_wobble = random.uniform(-0.3, 0.3)
            px = x + radius * math.cos(angle + angle_wobble)
            py = y + radius * math.sin(angle + angle_wobble)
            points.append(QPointF(px, py))

        # Draw main patch with multiple opacity layers for depth
        polygon = QPolygonF(points)

        # Outer layer (lighter, more transparent)
        outer_color = QColor(moss_color)
        outer_color.setAlpha(int(moss_color.alpha() * 0.4))
        painter.setBrush(outer_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(polygon)

        # Inner layer (darker, more opaque) - slightly smaller
        inner_points = []
        for point in points:
            # Move point toward center
            dx = point.x() - x
            dy = point.y() - y
            inner_points.append(QPointF(x + dx * 0.6, y + dy * 0.6))
        inner_polygon = QPolygonF(inner_points)
        inner_color = QColor(moss_color)
        painter.setBrush(inner_color)
        painter.drawPolygon(inner_polygon)

        # Add small satellite clusters around main patch (moss spreading)
        num_satellites = random.randint(2, 5)
        for _ in range(num_satellites):
            # Position near main patch
            sat_angle = random.uniform(0, 2 * math.pi)
            sat_dist = size * random.uniform(0.8, 1.5)
            sat_x = x + sat_dist * math.cos(sat_angle)
            sat_y = y + sat_dist * math.sin(sat_angle)
            sat_size = size * random.uniform(0.2, 0.4)

            # Draw small irregular cluster
            sat_points = []
            for i in range(random.randint(5, 8)):
                angle = (2 * math.pi * i) / 8
                radius = sat_size * random.uniform(0.6, 1.0)
                px = sat_x + radius * math.cos(angle)
                py = sat_y + radius * math.sin(angle)
                sat_points.append(QPointF(px, py))

            sat_color = QColor(moss_color)
            sat_color.setAlpha(int(moss_color.alpha() * 0.6))
            painter.setBrush(sat_color)
            painter.drawPolygon(QPolygonF(sat_points))

        # Add thin tendrils/veins (spreading growth)
        if draping:
            # More tendrils, longer, and biased downward for draping effect
            num_tendrils = random.randint(3, 6)
        else:
            num_tendrils = random.randint(1, 3)

        for _ in range(num_tendrils):
            if draping:
                # Bias tendril angle downward (between 45° and 135° from horizontal, pointing down)
                tendril_angle = random.uniform(math.pi * 0.25, math.pi * 0.75)
                tendril_length = size * random.uniform(2.0, 4.0)  # Much longer for draping
            else:
                tendril_angle = random.uniform(0, 2 * math.pi)
                tendril_length = size * random.uniform(1.2, 2.0)

            # Draw tendril as a series of small circles getting smaller
            tendril_color = QColor(moss_color)
            tendril_color.setAlpha(int(moss_color.alpha() * 0.5))
            painter.setBrush(tendril_color)

            num_segments = random.randint(4, 8) if draping else random.randint(3, 6)
            for seg in range(num_segments):
                t = seg / num_segments
                # Add some curve/wobble to tendril
                curve = math.sin(t * math.pi) * size * 0.3
                seg_x = x + (tendril_length * t) * math.cos(tendril_angle) + curve * math.sin(tendril_angle)
                seg_y = y + (tendril_length * t) * math.sin(tendril_angle) - curve * math.cos(tendril_angle)
                seg_size = size * 0.15 * (1.0 - t * 0.7)  # Get smaller toward end

                painter.drawEllipse(QPointF(seg_x, seg_y), seg_size, seg_size)

        # Add tiny speckles for organic texture
        num_speckles = random.randint(5, 15)
        speckle_color = QColor(moss_color)
        speckle_color.setAlpha(int(moss_color.alpha() * 0.7))
        painter.setBrush(speckle_color)

        for _ in range(num_speckles):
            speckle_x = x + random.uniform(-size * 1.5, size * 1.5)
            speckle_y = y + random.uniform(-size * 1.5, size * 1.5)
            speckle_size = random.uniform(1, 3)
            painter.drawEllipse(QPointF(speckle_x, speckle_y), speckle_size, speckle_size)

    def _draw_dense_moss_base(self, painter: QPainter, width: int, height: int, moss_colors: list):
        """Draw a dense moss layer covering the entire top of the texture with irregular bottom edge"""
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QPolygonF

        # Define the top coverage area (15-25% of height)
        base_coverage = random.uniform(0.15, 0.25)
        base_height = int(height * base_coverage)

        # Create irregular wavy bottom edge using multiple points
        num_edge_points = 20
        edge_points = []

        # Start from top-left, go across top, then down right side with wavy edge, back to left
        edge_points.append(QPointF(0, 0))
        edge_points.append(QPointF(width, 0))

        # Create wavy bottom edge from right to left
        for i in range(num_edge_points, -1, -1):
            x = (i / num_edge_points) * width
            # Wavy variation in the bottom edge (±20-40% of base height)
            wave_offset = random.uniform(0.7, 1.3)
            y = base_height * wave_offset + math.sin(i * 0.5) * base_height * 0.2
            edge_points.append(QPointF(x, y))

        # Close the polygon
        edge_points.append(QPointF(0, 0))

        base_polygon = QPolygonF(edge_points)

        # Draw multiple layers for depth and texture variation
        # Layer 1: Darkest base layer (full coverage)
        dark_moss = random.choice(moss_colors[:3])  # Use darker greens
        dark_moss.setAlpha(180)
        painter.setBrush(dark_moss)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(base_polygon)

        # Layer 2: Medium layer with slightly smaller coverage for depth
        medium_points = []
        medium_points.append(QPointF(0, 0))
        medium_points.append(QPointF(width, 0))
        for i in range(num_edge_points, -1, -1):
            x = (i / num_edge_points) * width
            wave_offset = random.uniform(0.6, 1.1)
            y = base_height * wave_offset * 0.85 + math.sin(i * 0.7) * base_height * 0.15
            medium_points.append(QPointF(x, y))
        medium_points.append(QPointF(0, 0))

        medium_moss = random.choice(moss_colors[2:5])
        medium_moss.setAlpha(160)
        painter.setBrush(medium_moss)
        painter.drawPolygon(QPolygonF(medium_points))

        # Layer 3: Add texture variation on top with small patches
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, int(base_height * 1.2))
            size = random.randint(5, 20)

            texture_moss = random.choice(moss_colors)
            texture_moss.setAlpha(random.randint(100, 180))
            painter.setBrush(texture_moss)

            # Small irregular blob
            num_points = random.randint(6, 10)
            points = []
            for i in range(num_points):
                angle = (2 * math.pi * i) / num_points
                radius = size * random.uniform(0.6, 1.0)
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append(QPointF(px, py))

            painter.drawPolygon(QPolygonF(points))

    def _generate_moss_overlay(self, image: QImage):
        """Add organic moss growth to existing texture with dense top coverage and draping growth"""
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Moss colors (varied dark greens with some yellow-green)
        moss_colors = [
            QColor(40, 80, 35),   # Dark green
            QColor(35, 75, 30),   # Darker green
            QColor(45, 85, 40),   # Medium green
            QColor(30, 70, 25),   # Deep green
            QColor(50, 90, 35),   # Lighter green
            QColor(45, 75, 25),   # Olive green
        ]

        # 1. Draw dense moss base layer covering entire top
        self._draw_dense_moss_base(painter, image.width(), image.height(), moss_colors)

        # 2. Draw draping organic moss patches extending from top
        num_draping = random.randint(10, 18)
        for _ in range(num_draping):
            # Start near the top
            x = random.randint(-10, image.width() + 10)
            y = random.randint(0, int(image.height() * 0.25))  # Start in top quarter
            size = random.randint(20, 60)
            opacity = random.randint(140, 220)

            moss = random.choice(moss_colors)
            moss.setAlpha(opacity)

            # Draw patch with emphasis on vertical draping (modify tendril direction)
            self._draw_organic_moss_patch(painter, x, y, size, moss, draping=True)

        # 3. Add main organic moss patches (can be anywhere in top half)
        num_patches = random.randint(8, 15)
        for _ in range(num_patches):
            x = random.randint(-10, image.width() + 10)
            y = random.randint(0, int(image.height() * 0.5))  # Top half
            size = random.randint(15, 50)
            opacity = random.randint(120, 200)

            moss = random.choice(moss_colors)
            moss.setAlpha(opacity)

            self._draw_organic_moss_patch(painter, x, y, size, moss)

        # 4. Add smaller moss clusters along draping paths
        num_small = random.randint(20, 35)
        for _ in range(num_small):
            x = random.randint(0, image.width())
            y = random.randint(0, int(image.height() * 0.7))  # Can spread further down
            size = random.randint(5, 15)
            opacity = random.randint(80, 160)

            moss = random.choice(moss_colors)
            moss.setAlpha(opacity)

            # Draw simple irregular blob for small clusters
            num_points = random.randint(6, 10)
            points = []
            for i in range(num_points):
                angle = (2 * math.pi * i) / num_points
                radius = size * random.uniform(0.6, 1.0)
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append(QPointF(px, py))

            painter.setBrush(moss)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF(points))

        painter.end()

    def _generate_stone_texture(self, size: int, darkness: float = 1.0) -> QImage:
        """Generate procedural stone/brick texture"""
        image = QImage(size, size, QImage.Format.Format_RGBA8888)
        image.fill(QColor(95, 90, 85))  # Base mortar color

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw brick pattern
        self._draw_brick_pattern(painter, size, size)

        # Add weathering
        self._add_weathering(painter, size, size)

        # Apply darkness multiplier
        if darkness != 1.0:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
            dark_overlay = QColor(int(255 * darkness), int(255 * darkness), int(255 * darkness))
            painter.fillRect(0, 0, size, size, dark_overlay)

        painter.end()
        return image

    def _generate_letter_textures(self):
        """Generate OpenGL textures for each unique letter with carved stone effect"""
        text = "CLAUDE-LIKE"
        unique_chars = set(text.replace(' ', '').replace('-', ''))

        for char in unique_chars:
            size = 256  # Texture size (power of 2)

            # Generate stone background
            image = self._generate_stone_texture(size, darkness=1.0)

            # Add moss overlay FIRST (before carving letters)
            self._generate_moss_overlay(image)

            # Now carve the letter through the moss-covered stone
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            # Set font
            font = QFont("Arial", 180, QFont.Weight.Bold)
            painter.setFont(font)

            # Create carved effect with 3 layers:
            # 1. Shadow (carved depth) - dark, offset down+right
            painter.setPen(QColor(15, 15, 20, 255))
            painter.drawText(image.rect().adjusted(3, 3, 3, 3), Qt.AlignmentFlag.AlignCenter, char)

            # 2. Highlight (carved edge) - light, offset up+left
            painter.setPen(QColor(100, 95, 90, 180))
            painter.drawText(image.rect().adjusted(-2, -2, -2, -2), Qt.AlignmentFlag.AlignCenter, char)

            # 3. Main letter (carved surface) - medium stone color
            painter.setPen(QColor(50, 48, 45, 255))
            painter.drawText(image.rect(), Qt.AlignmentFlag.AlignCenter, char)

            painter.end()

            # Convert to OpenGL texture
            # Flip image vertically for OpenGL coordinate system
            image = image.mirrored(False, True)

            # Generate texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)

            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            # Upload texture data
            img_data = image.constBits().asstring(size * size * 4)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            # Store texture ID
            self.letter_textures[char] = texture_id

        print(f"✓ Generated {len(self.letter_textures)} carved stone letter textures")

    def _generate_face_textures(self):
        """Generate textures for different cube faces"""
        size = 256

        # 1. Brick texture for side faces (normal brightness)
        side_image = self._generate_stone_texture(size, darkness=1.0)
        side_image = side_image.mirrored(False, True)
        self.brick_side_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.brick_side_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        img_data = side_image.constBits().asstring(size * size * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        # 2. Darker brick texture for back face
        back_image = self._generate_stone_texture(size, darkness=0.7)
        back_image = back_image.mirrored(False, True)
        self.brick_back_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.brick_back_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        img_data = back_image.constBits().asstring(size * size * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        # 3. Stone texture with heavy moss for top face
        top_image = self._generate_stone_texture(size, darkness=1.0)
        self._generate_moss_overlay(top_image)  # Add heavy moss growth
        top_image = top_image.mirrored(False, True)
        self.stone_top_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.stone_top_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        img_data = top_image.constBits().asstring(size * size * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        # 4. Darker stone for bottom face (less light)
        bottom_image = self._generate_stone_texture(size, darkness=0.6)
        bottom_image = bottom_image.mirrored(False, True)
        self.stone_bottom_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.stone_bottom_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        img_data = bottom_image.constBits().asstring(size * size * 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        print("✓ Generated face textures (sides, top, bottom, back)")

    def _init_letters(self):
        """Initialize 3D letters with staggered timing"""
        text = "CLAUDE-LIKE"
        spacing = 1.2

        # Count actual letters (excluding spaces and hyphens)
        num_letters = len([c for c in text if c not in (' ', '-')])

        # Calculate total width to center text
        total_width = (num_letters - 1) * spacing
        start_x = -total_width / 2

        # Create letters with dramatic slow-to-fast animation
        base_duration = 4.0
        duration_decrease = 0.05
        delay_offset = 0.3

        letter_index = 0
        for i, char in enumerate(text):
            if char in (' ', '-'):
                continue  # Skip spaces and hyphens (creates gap)

            x = start_x + letter_index * spacing
            y = 0.0

            # Each letter starts slightly later and moves slightly faster
            delay = letter_index * delay_offset
            duration = max(base_duration - (letter_index * duration_decrease), 2.0)

            # Get texture ID for this character
            texture_id = self.letter_textures.get(char, 0)

            letter = Letter3D(char, x, y, delay, duration, texture_id)
            self.letters.append(letter)
            letter_index += 1

    def _init_stars(self):
        """Initialize star tunnel with 800-1000 stars in cylindrical distribution"""
        num_stars = random.randint(800, 1000)

        for _ in range(num_stars):
            # Cylindrical distribution for tunnel effect
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, 18)  # Max radius from center

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = random.uniform(-60, -5)  # Depth range

            # Rotation angle for spiral effect
            rotation_angle = random.uniform(0, 360)

            # Speed varies per star
            speed = random.uniform(0.8, 1.5)

            # Size varies with distance (closer = bigger)
            size = 1.0

            self.stars.append({
                'x': x, 'y': y, 'z': z,
                'angle': rotation_angle,
                'speed': speed,
                'size': size,
                'base_x': x,  # Remember original radius position
                'base_y': y
            })

    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set up light
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 10, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.4, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 1.0, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1])

        # Background color (dark blue-purple)
        glClearColor(0.05, 0.05, 0.15, 1.0)

        # Generate letter textures and face textures
        self._generate_letter_textures()
        self._generate_face_textures()
        self._init_letters()

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Set up perspective projection
        aspect = w / h if h > 0 else 1
        gluPerspective(45, aspect, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the 3D scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Position camera with slight shake effect
        shake_x = math.sin(self.camera_shake * 20) * 0.1 if self.camera_shake > 0 else 0
        shake_y = math.cos(self.camera_shake * 25) * 0.1 if self.camera_shake > 0 else 0
        gluLookAt(
            shake_x, shake_y, 8 + self.camera_zoom,  # Camera position
            0, 0, 0,  # Look at origin
            0, 1, 0   # Up vector
        )

        # Draw starfield background
        self._draw_starfield()

        # Draw letters
        for letter in self.letters:
            if letter.state != "waiting":
                self._draw_letter(letter)

        # Draw particles
        glDisable(GL_LIGHTING)
        for particle in self.particles:
            self._draw_particle(particle)
        glEnable(GL_LIGHTING)

        # Draw 2D overlay (prompt text)
        if self.animation_complete:
            self._draw_overlay()

    def _draw_starfield(self):
        """Draw animated rotating star tunnel"""
        glDisable(GL_LIGHTING)
        glEnable(GL_POINT_SMOOTH)  # Anti-aliased points

        for star in self.stars:
            # Apply rotation around Z-axis for spiral effect
            angle_rad = math.radians(star['angle'])
            radius = math.sqrt(star['base_x']**2 + star['base_y']**2)
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            z = star['z']

            # Calculate depth factor (0 = far, 1 = near)
            depth_factor = (z + 60) / 55
            depth_factor = max(0, min(1, depth_factor))

            # Size based on depth (closer = bigger)
            size = 1.0 + depth_factor * 3.5
            glPointSize(size)

            # Color: Blue-white gradient based on depth and twinkle
            # Far stars = more blue, near stars = more white
            twinkle = 0.5 + 0.5 * math.sin(self.time_elapsed * 3 + star['angle'])
            base_brightness = 0.3 + depth_factor * 0.5 + twinkle * 0.2

            # Color variation: far = blue, near = white
            r = base_brightness * (0.7 + depth_factor * 0.3)
            g = base_brightness * (0.7 + depth_factor * 0.3)
            b = base_brightness * (0.9 + depth_factor * 0.1)

            glBegin(GL_POINTS)
            glColor4f(r, g, b, 0.8 + depth_factor * 0.2)
            glVertex3f(x, y, z)
            glEnd()

            # Draw motion blur trail for close, fast stars
            if depth_factor > 0.6 and star['speed'] > 1.2:
                trail_length = depth_factor * 2.0
                trail_alpha = depth_factor * 0.3

                glBegin(GL_LINES)
                glColor4f(r, g, b, trail_alpha)
                glVertex3f(x, y, z)
                glVertex3f(x, y, z - trail_length)
                glEnd()

        glDisable(GL_POINT_SMOOTH)
        glEnable(GL_LIGHTING)

    def _draw_letter(self, letter: Letter3D):
        """Draw a 3D letter"""
        glPushMatrix()

        # Position
        glTranslatef(letter.x, letter.y, letter.z)

        # Rotation
        glRotatef(letter.current_rotation_x, 1, 0, 0)
        glRotatef(letter.current_rotation_y, 0, 1, 0)
        glRotatef(letter.current_rotation_z, 0, 0, 1)

        # Color with glow
        r = letter.color[0] + letter.glow
        g = letter.color[1] + letter.glow
        b = letter.color[2]
        glColor3f(r, g, b)

        # Draw extruded letter (3D box with textured character)
        self._draw_3d_char(letter.texture_id)

        glPopMatrix()

    def _draw_3d_char(self, texture_id: int):
        """Draw a 3D character as textured dungeon stone block"""
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)  # White to show textures as-is

        # Front face - Carved letter texture
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0); glVertex3f(-0.4, -0.5, 0.2)
        glTexCoord2f(1, 0); glVertex3f(0.4, -0.5, 0.2)
        glTexCoord2f(1, 1); glVertex3f(0.4, 0.5, 0.2)
        glTexCoord2f(0, 1); glVertex3f(-0.4, 0.5, 0.2)
        glEnd()

        # Back face - Dark brick texture
        glBindTexture(GL_TEXTURE_2D, self.brick_back_texture)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glTexCoord2f(0, 0); glVertex3f(-0.4, -0.5, -0.2)
        glTexCoord2f(1, 0); glVertex3f(0.4, -0.5, -0.2)
        glTexCoord2f(1, 1); glVertex3f(0.4, 0.5, -0.2)
        glTexCoord2f(0, 1); glVertex3f(-0.4, 0.5, -0.2)
        glEnd()

        # Top face - Mossy stone texture
        glBindTexture(GL_TEXTURE_2D, self.stone_top_texture)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-0.4, 0.5, -0.2)
        glTexCoord2f(1, 0); glVertex3f(0.4, 0.5, -0.2)
        glTexCoord2f(1, 1); glVertex3f(0.4, 0.5, 0.2)
        glTexCoord2f(0, 1); glVertex3f(-0.4, 0.5, 0.2)
        glEnd()

        # Bottom face - Dark stone texture
        glBindTexture(GL_TEXTURE_2D, self.stone_bottom_texture)
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glTexCoord2f(0, 0); glVertex3f(-0.4, -0.5, -0.2)
        glTexCoord2f(1, 0); glVertex3f(0.4, -0.5, -0.2)
        glTexCoord2f(1, 1); glVertex3f(0.4, -0.5, 0.2)
        glTexCoord2f(0, 1); glVertex3f(-0.4, -0.5, 0.2)
        glEnd()

        # Left face - Brick texture
        glBindTexture(GL_TEXTURE_2D, self.brick_side_texture)
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(-0.4, -0.5, -0.2)
        glTexCoord2f(1, 0); glVertex3f(-0.4, -0.5, 0.2)
        glTexCoord2f(1, 1); glVertex3f(-0.4, 0.5, 0.2)
        glTexCoord2f(0, 1); glVertex3f(-0.4, 0.5, -0.2)
        glEnd()

        # Right face - Brick texture
        glBindTexture(GL_TEXTURE_2D, self.brick_side_texture)
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(0.4, -0.5, -0.2)
        glTexCoord2f(1, 0); glVertex3f(0.4, 0.5, -0.2)
        glTexCoord2f(1, 1); glVertex3f(0.4, 0.5, 0.2)
        glTexCoord2f(0, 1); glVertex3f(0.4, -0.5, 0.2)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    def _draw_particle(self, particle: Particle3D):
        """Draw a particle with multi-layer glow and effects"""
        # Enable additive blending for glow
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # Draw motion blur trail
        if particle.particle_type in ('spark', 'debris'):
            trail_alpha = particle.alpha * 0.3
            glColor4f(particle.color[0], particle.color[1], particle.color[2], trail_alpha)
            glBegin(GL_LINES)
            glVertex3f(particle.prev_x, particle.prev_y, particle.prev_z)
            glVertex3f(particle.x, particle.y, particle.z)
            glEnd()

        glPushMatrix()
        glTranslatef(particle.x, particle.y, particle.z)
        glRotatef(particle.rotation, 0, 0, 1)

        # Type-specific rendering
        if particle.particle_type == 'spark':
            # Sparks: Elongated diamond shape with bright core
            self._draw_spark(particle)
        elif particle.particle_type == 'glow':
            # Glow: Large soft circle with fade
            self._draw_glow(particle)
        elif particle.particle_type == 'dust':
            # Dust: Tiny fading dots
            self._draw_dust(particle)
        else:  # debris
            # Debris: Multi-layer circles with glow
            self._draw_debris(particle)

        glPopMatrix()

        # Restore normal blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _draw_spark(self, particle: Particle3D):
        """Draw an elongated spark particle"""
        size = particle.size
        # Bright core
        glColor4f(1.0, 1.0, 1.0, particle.alpha)
        glBegin(GL_QUADS)
        glVertex3f(-size * 0.5, -size * 1.5, 0)
        glVertex3f(size * 0.5, -size * 1.5, 0)
        glVertex3f(size * 0.5, size * 1.5, 0)
        glVertex3f(-size * 0.5, size * 1.5, 0)
        glEnd()
        # Colored glow
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.6)
        glBegin(GL_QUADS)
        glVertex3f(-size * 0.8, -size * 2.0, 0)
        glVertex3f(size * 0.8, -size * 2.0, 0)
        glVertex3f(size * 0.8, size * 2.0, 0)
        glVertex3f(-size * 0.8, size * 2.0, 0)
        glEnd()

    def _draw_glow(self, particle: Particle3D):
        """Draw a soft glowing particle"""
        size = particle.size
        # Outer glow (large, faint)
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.2)
        self._draw_circle(size * 1.5, 12)
        # Middle glow
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.5)
        self._draw_circle(size * 1.0, 10)
        # Bright core
        glColor4f(1.0, 1.0, 1.0, particle.alpha * 0.8)
        self._draw_circle(size * 0.3, 8)

    def _draw_dust(self, particle: Particle3D):
        """Draw a tiny dust particle"""
        size = particle.size
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.7)
        self._draw_circle(size, 6)

    def _draw_debris(self, particle: Particle3D):
        """Draw a debris particle with glow layers"""
        size = particle.size
        # Outer glow
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.3)
        self._draw_circle(size * 1.8, 12)
        # Middle layer
        glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha * 0.7)
        self._draw_circle(size * 1.2, 10)
        # Core
        glColor4f(particle.color[0] * 1.2, particle.color[1] * 1.2, particle.color[2] * 1.2, particle.alpha)
        self._draw_circle(size, 8)

    def _draw_circle(self, radius: float, segments: int):
        """Draw a filled circle using triangle fan"""
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)  # Center
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()

    def _draw_overlay(self):
        """Draw 2D overlay text"""
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

        # Draw "Press Any Key" with fade
        alpha = self.prompt_fade
        glColor4f(0.8, 0.8, 0.9, alpha)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        # Restore 3D projection
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def update_animation(self):
        """Update animation state"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time_elapsed += dt

        # Update letters
        all_landed = True
        for letter in self.letters:
            trigger_burst, started_flying = letter.update(dt)

            # Play whoosh sound when letter starts flying
            if started_flying:
                letter.whoosh_channel = self.audio.play_letter_whoosh()

            # Play impact sound and create particles when letter lands
            if trigger_burst and not letter.has_burst:
                letter.has_burst = True
                self._create_particle_burst(letter.x, letter.y, letter.z, letter.color)

                # Camera shake
                self.camera_shake = 0.2

                # Stop whoosh sound immediately before impact
                if letter.whoosh_channel:
                    letter.whoosh_channel.stop()
                    letter.whoosh_channel = None

                # Play impact sound
                self.audio.play_letter_impact()

            if letter.state != "landed":
                all_landed = False

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update star tunnel - move toward camera and rotate
        for star in self.stars:
            # Move toward camera
            star['z'] += dt * star['speed'] * 25

            # Rotate around Z-axis for spiral effect
            star['angle'] += dt * 30  # Degrees per second

            # Respawn star at back when it reaches camera
            if star['z'] > -1:
                star['z'] = -60
                # Randomize position slightly on respawn
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 18)
                star['base_x'] = radius * math.cos(angle)
                star['base_y'] = radius * math.sin(angle)
                star['angle'] = random.uniform(0, 360)
                star['speed'] = random.uniform(0.8, 1.5)

        # Camera effects
        if self.camera_shake > 0:
            self.camera_shake -= dt * 2
            self.camera_shake = max(0, self.camera_shake)

        # Check if animation complete
        if all_landed and not self.animation_complete:
            self.animation_complete = True

        # Update prompt fade
        if self.animation_complete:
            self.prompt_fade = min(1.0, self.prompt_fade + dt)

        self.update()

    def _create_particle_burst(self, x: float, y: float, z: float, color: List[float]):
        """Create a burst of particles with variety (30-40 particles)"""
        num_particles = random.randint(30, 40)

        # Particle type distribution
        for i in range(num_particles):
            # Determine particle type with weighted distribution
            rand = random.random()
            if rand < 0.5:  # 50% debris
                particle_type = 'debris'
                speed_mult = 1.0
            elif rand < 0.7:  # 20% sparks (fast and bright)
                particle_type = 'spark'
                speed_mult = 1.8
            elif rand < 0.85:  # 15% glow (slow, large)
                particle_type = 'glow'
                speed_mult = 0.6
            else:  # 15% dust (many tiny particles)
                particle_type = 'dust'
                speed_mult = 0.8

            # Random direction with more vertical spread
            angle_h = random.uniform(0, 2 * math.pi)
            angle_v = random.uniform(-math.pi/3, math.pi/3)
            speed = random.uniform(3, 10) * speed_mult

            vx = math.cos(angle_h) * math.cos(angle_v) * speed
            vy = math.sin(angle_v) * speed + random.uniform(2, 6)
            vz = math.sin(angle_h) * math.cos(angle_v) * speed

            # Color variation based on type
            if particle_type == 'spark':
                # Sparks are brighter/whiter
                particle_color = [
                    min(1.0, color[0] + random.uniform(0.1, 0.3)),
                    min(1.0, color[1] + random.uniform(0.1, 0.3)),
                    min(1.0, color[2] + random.uniform(0.0, 0.2))
                ]
            elif particle_type == 'dust':
                # Dust is darker/muted
                particle_color = [
                    color[0] * random.uniform(0.5, 0.8),
                    color[1] * random.uniform(0.5, 0.8),
                    color[2] * random.uniform(0.7, 0.9)
                ]
            else:
                # Debris and glow: normal color variation
                particle_color = [
                    color[0] + random.uniform(-0.1, 0.1),
                    color[1] + random.uniform(-0.1, 0.1),
                    color[2]
                ]

            particle = Particle3D(x, y, z, vx, vy, vz, particle_color, particle_type)
            self.particles.append(particle)

    def keyPressEvent(self, event):
        """Handle key press to continue"""
        if self.animation_complete:
            self.audio.play_ui_select()
            self.continue_pressed.emit()
        else:
            # Skip animation
            for letter in self.letters:
                letter.state = "landed"
                letter.x = letter.final_x
                letter.y = letter.final_y
                letter.z = letter.final_z
                letter.current_rotation_x = 0
                letter.current_rotation_y = 0
                letter.current_rotation_z = 0
            self.animation_complete = True
            self.audio.play_ui_select()

    def mousePressEvent(self, event):
        """Handle mouse press to continue"""
        if self.animation_complete:
            self.audio.play_ui_select()
            self.continue_pressed.emit()
        else:
            # Skip animation
            for letter in self.letters:
                letter.state = "landed"
                letter.x = letter.final_x
                letter.y = letter.final_y
                letter.z = letter.final_z
                letter.current_rotation_x = 0
                letter.current_rotation_y = 0
                letter.current_rotation_z = 0
            self.animation_complete = True
            self.audio.play_ui_select()
