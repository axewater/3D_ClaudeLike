"""
3D Game Over Screen

Displays death reason and final stats when player dies.
"""

from ursina import Entity, camera, color, Text, Button, Vec3, time as ursina_time
import math
import random
from audio import get_audio_manager
from animations3d import Particle3D


class GameOverScreen3D(Entity):
    """
    Game Over screen with dark/red particles and death stats.

    Shows:
    - "GAME OVER" title
    - Death reason (e.g., "Slain by Goblin")
    - Final stats (level reached, XP, enemies defeated)
    - Options: Try Again, Main Menu, Quit
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # Stats
        self.stats = {
            'level': 1,
            'xp': 0,
            'enemies_defeated': 0
        }
        self.death_reason = "You were defeated"

        # UI elements
        self.ui_elements = []

        # Particles
        self.particles = []
        self.particle_spawn_timer = 0.0

        # Animation
        self.time_elapsed = 0.0
        self.fade_progress = 0.0

        # Initialize
        self._create_ui()

        # Initially hidden
        self.enabled = False

        print("✓ GameOverScreen3D initialized")

    def _create_ui(self):
        """Create UI overlay elements"""
        # Background tint (dark with red glow) - RGBA tuple
        bg = Entity(
            model='quad',
            color=(20/255, 10/255, 10/255, 220/255),  # Normalized RGBA (0-1 range)
            scale=(100, 100),
            position=(0, 0, -1),
            parent=camera.ui
        )
        self.ui_elements.append(bg)

        # Title "GAME OVER"
        self.title_text = Text(
            text="GAME OVER",
            position=(0, 0.3),
            origin=(0, 0),
            scale=4.5,
            color=color.rgb(0.784, 0.196, 0.196),
            parent=camera.ui
        )
        self.ui_elements.append(self.title_text)

        # Death reason
        self.death_reason_text = Text(
            text="You were defeated",
            position=(0, 0.18),
            origin=(0, 0),
            scale=1.8,
            color=color.rgb(0.706, 0.392, 0.392),
            parent=camera.ui
        )
        self.ui_elements.append(self.death_reason_text)

        # Stats display
        stats_y = 0.03
        stats_spacing = 0.07

        self.level_text = Text(
            text="Level Reached: 1",
            position=(0, stats_y),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.627, 0.627, 0.706),
            parent=camera.ui
        )
        self.ui_elements.append(self.level_text)

        self.xp_text = Text(
            text="Total XP: 0",
            position=(0, stats_y - stats_spacing),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.627, 0.627, 0.706),
            parent=camera.ui
        )
        self.ui_elements.append(self.xp_text)

        self.enemies_text = Text(
            text="Enemies Defeated: 0",
            position=(0, stats_y - stats_spacing * 2),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.627, 0.627, 0.706),
            parent=camera.ui
        )
        self.ui_elements.append(self.enemies_text)

        # Buttons
        button_y = -0.25
        button_spacing = 0.12

        self.try_again_button = Button(
            text="TRY AGAIN",
            scale=(0.25, 0.08),
            position=(0, button_y),
            color=color.rgb(0.314, 0.392, 0.471),
            parent=camera.ui,
            on_click=self._try_again
        )
        self.ui_elements.append(self.try_again_button)

        self.main_menu_button = Button(
            text="MAIN MENU",
            scale=(0.25, 0.08),
            position=(0, button_y - button_spacing),
            color=color.rgb(0.314, 0.314, 0.392),
            parent=camera.ui,
            on_click=self._main_menu
        )
        self.ui_elements.append(self.main_menu_button)

        self.quit_button = Button(
            text="QUIT",
            scale=(0.25, 0.08),
            position=(0, button_y - button_spacing * 2),
            color=color.rgb(0.471, 0.235, 0.235),
            parent=camera.ui,
            on_click=self._quit
        )
        self.ui_elements.append(self.quit_button)

        # Hint text
        hint = Text(
            text="Learn from your mistakes and try again",
            position=(0, -0.48),
            origin=(0, 0),
            scale=1.0,
            color=color.rgb(0.392, 0.314, 0.314),
            parent=camera.ui
        )
        self.ui_elements.append(hint)

    def set_stats(self, stats: dict, death_reason: str):
        """Set final stats and death reason to display"""
        self.stats = stats
        self.death_reason = death_reason
        self._update_display()

    def _update_display(self):
        """Update text with current values"""
        self.death_reason_text.text = self.death_reason
        self.level_text.text = f"Level Reached: {self.stats.get('level', 1)}"
        self.xp_text.text = f"Total XP: {self.stats.get('xp', 0)}"
        self.enemies_text.text = f"Enemies Defeated: {self.stats.get('enemies_defeated', 0)}"

    def _try_again(self):
        """Return to class selection to start a new game"""
        self.audio.play_ui_select()
        print("[GameOverScreen] Try Again clicked")
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.CLASS_SELECTION)

    def _main_menu(self):
        """Return to main menu"""
        self.audio.play_ui_select()
        print("[GameOverScreen] Main Menu clicked")
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.MAIN_MENU)

    def _quit(self):
        """Quit the game"""
        self.audio.play_ui_select()
        print("[GameOverScreen] Quit clicked")
        self.screen_manager.quit_game()

    def _spawn_death_particles(self):
        """Spawn dark/red death particles"""
        # Spawn 2-4 particles
        for _ in range(random.randint(2, 4)):
            # Random position across screen
            x = random.uniform(-10, 10)
            y = random.uniform(-5, 10)
            z = random.uniform(-5, -2)

            # Slow downward velocity
            vx = random.uniform(-0.3, 0.3)
            vy = random.uniform(-1.5, -0.5)
            vz = random.uniform(-0.3, 0.3)

            # Dark red, dark purple, or gray color
            color_choice = random.randint(0, 2)
            if color_choice == 0:
                particle_color = (0.6, 0.1, 0.1)  # Dark red
            elif color_choice == 1:
                particle_color = (0.3, 0.1, 0.3)  # Dark purple
            else:
                particle_color = (0.2, 0.2, 0.2)  # Dark gray

            # Create particle
            particle = Particle3D(
                position=Vec3(x, y, z),
                velocity=Vec3(vx, vy, vz),
                color=particle_color,
                size=random.uniform(0.15, 0.35),
                lifetime=random.uniform(3.0, 5.0),
                particle_type='circle',
                apply_gravity=True
            )
            self.particles.append(particle)

    def update(self):
        """Update animations"""
        if not self.enabled:
            return

        dt = ursina_time.dt
        self.time_elapsed += dt

        # Fade in effect
        if self.fade_progress < 1.0:
            self.fade_progress += dt * 0.8
            alpha = min(1.0, self.fade_progress)
            # Update title alpha
            current_color = self.title_text.color
            self.title_text.color = color.rgba(
                current_color[0] * 255,
                current_color[1] * 255,
                current_color[2] * 255,
                int(alpha * 255)
            )

        # Spawn death particles periodically
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer > 0.3 and len(self.particles) < 30:
            self.particle_spawn_timer = 0.0
            self._spawn_death_particles()

        # Update particles
        for particle in self.particles[:]:
            if not particle.update(dt):
                # Particle died
                self.particles.remove(particle)
                if hasattr(particle, 'entity') and particle.entity:
                    particle.entity.enabled = False

    def show(self):
        """Show the game over screen"""
        self.enabled = True
        self.fade_progress = 0.0

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Play defeat sound (optional)
        # self.audio.play_defeat_sound()

        # Spawn initial particles
        for _ in range(15):
            self._spawn_death_particles()

        print("[GameOverScreen] Screen shown")

    def hide(self):
        """Hide the game over screen"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        # Clear particles
        for particle in self.particles:
            if hasattr(particle, 'entity') and particle.entity:
                particle.entity.enabled = False
        self.particles.clear()

        print("[GameOverScreen] Screen hidden")
