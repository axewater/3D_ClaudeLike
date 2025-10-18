"""
3D Victory Screen

Displays celebration effects and final stats when player completes all 25 levels.
"""

from ursina import Entity, camera, color, Text, Button, Vec3, time as ursina_time
import math
import random
from audio import get_audio_manager
from animations3d import Particle3D


class VictoryScreen3D(Entity):
    """
    Victory screen with golden celebration particles and stats display.

    Shows:
    - "VICTORY!" title with glow
    - Final stats (level, XP, enemies defeated)
    - Options: Play Again, Main Menu, Quit
    """

    def __init__(self, screen_manager):
        super().__init__()
        self.screen_manager = screen_manager
        self.audio = get_audio_manager()

        # Stats
        self.stats = {
            'level': 25,
            'xp': 0,
            'enemies_defeated': 0,
            'time_played': 0
        }

        # UI elements
        self.ui_elements = []

        # Particles
        self.particles = []
        self.particle_spawn_timer = 0.0

        # Animation
        self.time_elapsed = 0.0
        self.title_pulse = 0.0

        # Initialize
        self._create_ui()

        # Initially hidden
        self.enabled = False

        # Play victory sound
        self.audio.play_ui_select()

        print("✓ VictoryScreen3D initialized")

    def _create_ui(self):
        """Create UI overlay elements"""
        # Background tint (dark with golden glow) - RGBA tuple
        bg = Entity(
            model='quad',
            color=(25/255, 20/255, 15/255, 200/255),  # Normalized RGBA (0-1 range)
            scale=(100, 100),
            position=(0, 0, -1),
            parent=camera.ui
        )
        self.ui_elements.append(bg)

        # Title "VICTORY!"
        self.title_text = Text(
            text="VICTORY!",
            position=(0, 0.3),
            origin=(0, 0),
            scale=5.0,
            color=color.rgb(255, 215, 0),
            parent=camera.ui
        )
        self.ui_elements.append(self.title_text)

        # Subtitle
        subtitle = Text(
            text="You have conquered all 25 levels!",
            position=(0, 0.18),
            origin=(0, 0),
            scale=1.8,
            color=color.rgb(0.784, 0.706, 0.863),
            parent=camera.ui
        )
        self.ui_elements.append(subtitle)

        # Stats display
        self.level_text = Text(
            text="Level Reached: 25",
            position=(0, 0.05),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.706, 0.706, 0.784),
            parent=camera.ui
        )
        self.ui_elements.append(self.level_text)

        self.xp_text = Text(
            text="Total XP: 0",
            position=(0, -0.02),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.706, 0.706, 0.784),
            parent=camera.ui
        )
        self.ui_elements.append(self.xp_text)

        self.enemies_text = Text(
            text="Enemies Defeated: 0",
            position=(0, -0.09),
            origin=(0, 0),
            scale=1.5,
            color=color.rgb(0.706, 0.706, 0.784),
            parent=camera.ui
        )
        self.ui_elements.append(self.enemies_text)

        # Buttons
        button_y = -0.25
        button_spacing = 0.12

        self.play_again_button = Button(
            text="PLAY AGAIN",
            scale=(0.25, 0.08),
            position=(0, button_y),
            color=color.rgb(0.235, 0.471, 0.235),
            parent=camera.ui,
            on_click=self._play_again
        )
        self.ui_elements.append(self.play_again_button)

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

        # Credits
        credits = Text(
            text="Claude-Like - A Roguelike Adventure",
            position=(0, -0.48),
            origin=(0, 0),
            scale=0.8,
            color=color.rgb(0.392, 0.353, 0.431),
            parent=camera.ui
        )
        self.ui_elements.append(credits)

    def set_stats(self, stats: dict):
        """Set final stats to display"""
        self.stats = stats
        self._update_stats_display()

    def _update_stats_display(self):
        """Update stat text with current values"""
        self.level_text.text = f"Level Reached: {self.stats.get('level', 25)}"
        self.xp_text.text = f"Total XP: {self.stats.get('xp', 0)}"
        self.enemies_text.text = f"Enemies Defeated: {self.stats.get('enemies_defeated', 0)}"

    def _play_again(self):
        """Return to class selection to start a new game"""
        self.audio.play_ui_select()
        print("[VictoryScreen] Play Again clicked")
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.CLASS_SELECTION)

    def _main_menu(self):
        """Return to main menu"""
        self.audio.play_ui_select()
        print("[VictoryScreen] Main Menu clicked")
        from ui.screens.screen_manager_3d import ScreenState
        self.screen_manager.change_screen(ScreenState.MAIN_MENU)

    def _quit(self):
        """Quit the game"""
        self.audio.play_ui_select()
        print("[VictoryScreen] Quit clicked")
        self.screen_manager.quit_game()

    def _spawn_celebration_particles(self):
        """Spawn golden celebration particles"""
        # Spawn 3-5 particles
        for _ in range(random.randint(3, 5)):
            # Random position across screen
            x = random.uniform(-10, 10)
            y = random.uniform(-5, 10)
            z = random.uniform(-5, -2)

            # Upward velocity with some randomness
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(1.0, 3.0)
            vz = random.uniform(-0.5, 0.5)

            # Golden, purple, or pink color
            color_choice = random.randint(0, 2)
            if color_choice == 0:
                particle_color = (1.0, 0.84, 0.0)  # Gold
            elif color_choice == 1:
                particle_color = (0.7, 0.4, 1.0)  # Purple
            else:
                particle_color = (1.0, 0.6, 0.8)  # Pink

            # Create particle
            particle = Particle3D(
                position=Vec3(x, y, z),
                velocity=Vec3(vx, vy, vz),
                color=particle_color,
                size=random.uniform(0.1, 0.3),
                lifetime=random.uniform(2.0, 4.0),
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

        # Update title pulse
        self.title_pulse = math.sin(self.time_elapsed * 3.0) * 0.5 + 0.5

        # Update title color with pulse
        brightness = int(200 + self.title_pulse * 55)
        self.title_text.color = color.rgb(255, brightness, int(brightness * 0.6))

        # Spawn celebration particles periodically
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer > 0.2 and len(self.particles) < 50:
            self.particle_spawn_timer = 0.0
            self._spawn_celebration_particles()

        # Update particles
        for particle in self.particles[:]:
            if not particle.update(dt):
                # Particle died
                self.particles.remove(particle)
                if hasattr(particle, 'entity') and particle.entity:
                    particle.entity.enabled = False

    def show(self):
        """Show the victory screen"""
        self.enabled = True

        # Show all UI elements
        for element in self.ui_elements:
            element.enabled = True

        # Spawn initial burst of particles
        for _ in range(20):
            self._spawn_celebration_particles()

        print("[VictoryScreen] Screen shown")

    def hide(self):
        """Hide the victory screen"""
        self.enabled = False

        # Hide all UI elements
        for element in self.ui_elements:
            element.enabled = False

        # Clear particles
        for particle in self.particles:
            if hasattr(particle, 'entity') and particle.entity:
                particle.entity.enabled = False
        self.particles.clear()

        print("[VictoryScreen] Screen hidden")
