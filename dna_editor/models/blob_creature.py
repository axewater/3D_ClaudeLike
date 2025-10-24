"""
BlobCreature model - creature made of translucent slime cubes.
"""

from ursina import Entity, Vec3, color, destroy
import math
import random
from ..core.constants import (
    DEFAULT_CUBE_SIZE_MIN, DEFAULT_CUBE_SIZE_MAX,
    DEFAULT_CUBE_SPACING, DEFAULT_BLOB_COLOR, DEFAULT_BLOB_TRANSPARENCY,
    DEFAULT_JIGGLE_SPEED, DEFAULT_BLOB_PULSE_AMOUNT,
    BLOB_JIGGLE_AMPLITUDE
)
from ..shaders import create_toon_shader


class BlobCube:
    """Single cube in the blob with individual animation state and tree structure."""

    def __init__(self, position, size, base_color, transparency, parent, toon_shader=None,
                 tree_depth=0, parent_cube=None):
        """
        Create a blob cube.

        Args:
            position: Vec3 position in world space
            size: Cube scale
            base_color: RGB tuple (0-1)
            transparency: Alpha value (0-1, where 1 is fully transparent)
            parent: Parent entity (scene root)
            toon_shader: Optional toon shader to apply
            tree_depth: Distance from root (0 = root, 1 = children, etc.)
            parent_cube: Reference to parent BlobCube (None for root)
        """
        self.original_position = position
        self.original_size = size
        self.base_color = base_color
        self.transparency = transparency
        self.tree_depth = tree_depth
        self.parent_cube = parent_cube
        self.children = []  # Child BlobCubes
        self.connector_tube = None  # Tube (stretched cube) connecting to parent
        self.physics_particle = None  # Physics particle for Verlet simulation (None = not enabled)

        # Random jiggle phase offset for organic motion
        self.jiggle_phase_x = random.random() * math.pi * 2
        self.jiggle_phase_y = random.random() * math.pi * 2
        self.jiggle_phase_z = random.random() * math.pi * 2

        # Create cube entity with transparency
        # Ursina color.rgba() for transparency
        cube_color = color.rgba(base_color[0], base_color[1], base_color[2], 1.0 - transparency)

        entity_params = {
            'model': 'cube',
            'color': cube_color,
            'scale': size,
            'position': position,
            'parent': parent
        }

        # Apply toon shader if provided
        if toon_shader is not None:
            entity_params['shader'] = toon_shader

        self.entity = Entity(**entity_params)

        # Create connector tube if this cube has a parent
        if parent_cube is not None:
            self._create_connector_tube(parent, base_color, transparency, toon_shader)

    def _create_connector_tube(self, scene_parent, base_color, transparency, toon_shader):
        """Create tube (stretched cube) connecting this cube to its parent cube."""
        from ..core.constants import CONNECTOR_TUBE_RADIUS_RATIO, CONNECTOR_TUBE_OPACITY_MULTIPLIER

        # Calculate tube radius (fraction of average cube size)
        avg_size = (self.original_size + self.parent_cube.original_size) / 2
        tube_radius = avg_size * CONNECTOR_TUBE_RADIUS_RATIO

        # Tube transparency (slightly more opaque than cubes)
        tube_transparency = transparency * CONNECTOR_TUBE_OPACITY_MULTIPLIER

        # Calculate initial position, rotation, and length
        midpoint = (self.original_position + self.parent_cube.original_position) / 2
        direction = (self.original_position - self.parent_cube.original_position).normalized()
        length = (self.original_position - self.parent_cube.original_position).length()

        # Calculate rotation to align tube with direction
        # Ursina cubes need to be oriented along Y axis for the connector tube
        # We need to rotate to align with direction vector
        from ursina import Vec3
        up = Vec3(0, 1, 0)
        if direction.length() > 0.001:
            # Calculate rotation axis and angle
            axis = up.cross(direction).normalized()
            angle = math.acos(max(-1, min(1, up.dot(direction))))
            # Convert to Euler angles (Ursina uses pitch, yaw, roll)
            # For simplicity, we'll use look_at approach
            rotation = Vec3(0, 0, 0)  # Will be set via look_at below
        else:
            rotation = Vec3(0, 0, 0)

        # Create tube color (same as cube but with tube transparency)
        tube_color = color.rgba(base_color[0], base_color[1], base_color[2], 1.0 - tube_transparency)

        # Create tube entity (using cube instead of cylinder, as Ursina doesn't have cylinder primitive)
        tube_params = {
            'model': 'cube',
            'color': tube_color,
            'position': midpoint,
            'scale': (tube_radius, length / 2, tube_radius),  # Y scale = half length
            'parent': scene_parent
        }

        # Apply toon shader if provided
        if toon_shader is not None:
            tube_params['shader'] = toon_shader

        self.connector_tube = Entity(**tube_params)

        # Point the cylinder from parent to child
        self.connector_tube.look_at(self.parent_cube.entity, axis=Vec3.up)

    def _update_connector_tube_transform(self):
        """Update connector tube position and orientation to follow animated cubes."""
        if self.connector_tube is None or self.parent_cube is None:
            return

        # Recalculate midpoint between current positions
        midpoint = (self.entity.position + self.parent_cube.entity.position) / 2
        self.connector_tube.position = midpoint

        # Recalculate length
        length = (self.entity.position - self.parent_cube.entity.position).length()
        self.connector_tube.scale_y = length / 2  # Y scale = half length for proper tube sizing

        # Update rotation to point from parent to child
        self.connector_tube.look_at(self.parent_cube.entity, axis=Vec3.up)

    def update_animation(self, time, jiggle_speed, jiggle_amplitude,
                        is_attacking=False, attack_progress=0.0, attack_phase='idle'):
        """
        Update cube animation.

        Args:
            time: Current animation time
            jiggle_speed: Speed of jiggle animation
            jiggle_amplitude: Intensity of jiggle
            is_attacking: Whether attack is in progress
            attack_progress: Attack phase progress (0-1)
            attack_phase: 'expand', 'contract', 'return', or 'idle'
        """
        # If physics is enabled, sync entity position from physics particle
        # Don't return early - let Ursina update cycle complete
        if self.physics_particle is not None:
            self.entity.position = self.physics_particle.position
            self._update_connector_tube_transform()
            # Skip animation logic when physics is active, but don't return
            # This allows Ursina to complete its rendering update cycle
        elif is_attacking and attack_phase == 'cascade':
            # Cascade attack: smooth wave expanding from root → leaves
            from ..core.constants import CASCADE_EXPAND_AMOUNT, CASCADE_PULSE_SCALE

            # Calculate direction from origin (for radial expansion)
            direction = self.original_position.normalized()
            if direction.length() < 0.001:
                direction = Vec3(0, 1, 0)  # Fallback for root at origin

            # Smooth wave: expand → contract → return
            if attack_progress < 0.5:
                # Expansion phase (0 → 0.5)
                t = attack_progress * 2.0  # Map to 0→1
                ease_t = self._ease_out_cubic(t)  # Ease-out for smooth expansion
                expansion_factor = 1.0 + (CASCADE_EXPAND_AMOUNT - 1.0) * ease_t
                position_offset = direction * (CASCADE_EXPAND_AMOUNT - 1.0) * ease_t * 0.5
                self.entity.position = self.original_position + position_offset
                self.entity.scale = self.original_size * (1.0 + (CASCADE_PULSE_SCALE - 1.0) * ease_t)
            else:
                # Contraction + return phase (0.5 → 1.0)
                t = (attack_progress - 0.5) * 2.0  # Map to 0→1
                ease_t = self._ease_in_cubic(t)  # Fast return
                remaining_expansion = 1.0 - ease_t
                expansion_factor = 1.0 + (CASCADE_EXPAND_AMOUNT - 1.0) * remaining_expansion
                position_offset = direction * (CASCADE_EXPAND_AMOUNT - 1.0) * remaining_expansion * 0.5
                self.entity.position = self.original_position + position_offset
                self.entity.scale = self.original_size * (1.0 + (CASCADE_PULSE_SCALE - 1.0) * remaining_expansion)

            # Update connector tube to follow cube
            self._update_connector_tube_transform()
        elif not self.physics_particle:  # Only do idle animation if no physics
            # Idle jiggle animation (each cube jiggles independently)
            jiggle_x = math.sin(time * jiggle_speed + self.jiggle_phase_x) * jiggle_amplitude
            jiggle_y = math.sin(time * jiggle_speed * 1.3 + self.jiggle_phase_y) * jiggle_amplitude * 0.8
            jiggle_z = math.cos(time * jiggle_speed * 0.9 + self.jiggle_phase_z) * jiggle_amplitude

            self.entity.position = self.original_position + Vec3(jiggle_x, jiggle_y, jiggle_z)

            # Subtle pulse in size
            pulse = 1.0 + math.sin(time * jiggle_speed * 0.7 + self.jiggle_phase_x) * 0.05
            self.entity.scale = self.original_size * pulse

            # Update connector tube to follow cube (if it has one)
            self._update_connector_tube_transform()

    def _ease_out_cubic(self, t):
        """Ease-out cubic (fast start, slow end)."""
        return 1 - pow(1 - t, 3)

    def _ease_in_cubic(self, t):
        """Ease-in cubic (slow start, fast end)."""
        return t * t * t

    def _ease_out_quad(self, t):
        """Ease-out quadratic."""
        return 1 - (1 - t) * (1 - t)

    def create_physics_particle(self, mass):
        """
        Create physics particle for Verlet simulation.

        Args:
            mass: Particle mass (usually proportional to cube volume)
        """
        from ..models.blob_physics import PhysicsParticle

        # Create new Vec3 from entity position (Ursina Vec3 doesn't have .copy())
        pos = self.entity.position
        self.physics_particle = PhysicsParticle(
            position=Vec3(pos.x, pos.y, pos.z),
            mass=mass,
            radius=self.original_size * 0.5  # Use half cube size for collision radius
        )

    def destroy(self):
        """Cleanup cube entity and connector tube."""
        if self.connector_tube is not None:
            destroy(self.connector_tube)
        destroy(self.entity)


class BlobCreature:
    """Creature made of translucent slime cubes in Fibonacci tree structure."""

    def __init__(self, branch_depth=None, branch_count=None,
                 cube_size_min=DEFAULT_CUBE_SIZE_MIN,
                 cube_size_max=DEFAULT_CUBE_SIZE_MAX,
                 cube_spacing=DEFAULT_CUBE_SPACING,
                 blob_color=DEFAULT_BLOB_COLOR,
                 transparency=DEFAULT_BLOB_TRANSPARENCY,
                 jiggle_speed=DEFAULT_JIGGLE_SPEED,
                 pulse_amount=DEFAULT_BLOB_PULSE_AMOUNT):
        """
        Create a blob creature with Fibonacci tree structure.

        Args:
            branch_depth: Maximum branching depth (0-3 levels)
            branch_count: Number of children per cube (1-3)
            cube_size_min: Minimum cube size
            cube_size_max: Maximum cube size
            cube_spacing: Distance between cube centers
            blob_color: Base color (RGB tuple 0-1)
            transparency: Alpha transparency (0=opaque, 1=fully transparent)
            jiggle_speed: Animation speed
            pulse_amount: Pulse animation intensity
        """
        from ..core.constants import DEFAULT_BLOB_BRANCH_DEPTH, DEFAULT_BLOB_BRANCH_COUNT

        # Use defaults if not provided
        if branch_depth is None:
            branch_depth = DEFAULT_BLOB_BRANCH_DEPTH
        if branch_count is None:
            branch_count = DEFAULT_BLOB_BRANCH_COUNT

        # Create root entity
        self.root = Entity(position=(0, 0, 0))
        self.cubes = []

        # Store parameters
        self.branch_depth = branch_depth
        self.branch_count = branch_count
        self.cube_size_min = cube_size_min
        self.cube_size_max = cube_size_max
        self.cube_spacing = cube_spacing
        self.blob_color = blob_color
        self.transparency = transparency
        self.jiggle_speed = jiggle_speed
        self.pulse_amount = pulse_amount

        # Attack animation state
        self.is_attacking = False
        self.attack_start_time = 0

        # Physics state (Verlet integration)
        self.physics_engine = None
        self.physics_enabled = False
        self.physics_time = 0.0

        # Create toon shader (shared across all cubes and tubes)
        self.toon_shader = create_toon_shader()
        if self.toon_shader is None:
            print("WARNING: Toon shader creation failed in BlobCreature, using default rendering")

        # Generate blob cubes with tree structure
        self._generate_cubes()

    def _generate_cubes(self):
        """Generate Fibonacci tree structure of cubes."""
        from ..core.constants import GOLDEN_RATIO, GOLDEN_ANGLE

        # Clear existing cubes and tubes
        for cube in self.cubes:
            cube.destroy()
        self.cubes.clear()

        # Create root cube at origin (top of creature, grows downward)
        root_position = Vec3(0, 0.5, 0)  # Start slightly above center
        root_cube = BlobCube(
            position=root_position,
            size=self.cube_size_max,  # Root is largest
            base_color=self.blob_color,
            transparency=self.transparency,
            parent=self.root,
            toon_shader=self.toon_shader,
            tree_depth=0,
            parent_cube=None  # Root has no parent
        )
        self.cubes.append(root_cube)

        # Recursively generate children
        if self.branch_depth > 0:
            self._generate_children(root_cube, current_depth=0)

    def _generate_children(self, parent_cube, current_depth):
        """Recursively generate child cubes using golden angle distribution."""
        from ..core.constants import GOLDEN_RATIO, GOLDEN_ANGLE

        if current_depth >= self.branch_depth:
            return  # Max depth reached

        # Generate branch_count children for this parent
        for i in range(self.branch_count):
            # Calculate child position using golden angle + lower hemisphere bias
            angle = i * GOLDEN_ANGLE  # Fibonacci spiral spacing (~137.5 degrees)

            # Bias toward lower hemisphere (y grows more negative with depth)
            # Depth 0 children: y_offset around -0.4 to -0.6
            # Depth 1+ children: y_offset gets more negative
            depth_factor = (current_depth + 1) / max(self.branch_depth, 1)
            y_offset = -0.4 - depth_factor * 0.5  # Range: -0.4 to -0.9

            # Calculate spherical offset from parent (biased downward)
            # Use smaller radius for y calculation to create elongated downward shape
            radius_horizontal = math.sqrt(max(0, 1 - (y_offset * 0.7) ** 2))  # Elliptical
            x_offset = radius_horizontal * math.cos(angle) * self.cube_spacing
            z_offset = radius_horizontal * math.sin(angle) * self.cube_spacing

            child_position = parent_cube.original_position + Vec3(
                x_offset,
                y_offset * self.cube_spacing,
                z_offset
            )

            # Scale cube size by golden ratio (children are smaller)
            child_size = parent_cube.original_size / GOLDEN_RATIO
            child_size = max(self.cube_size_min, child_size)  # Clamp to minimum

            # Slight color variation with depth (darker/greener as depth increases)
            hue_shift = current_depth * 0.08
            child_color = (
                max(0.0, self.blob_color[0] - hue_shift * 0.2),  # Slightly less red
                min(1.0, self.blob_color[1] + hue_shift * 0.1),  # Slightly more green
                max(0.0, self.blob_color[2] - hue_shift * 0.1)   # Slightly less blue
            )

            # Create child cube (with parent link for tree structure)
            child_cube = BlobCube(
                position=child_position,
                size=child_size,
                base_color=child_color,
                transparency=self.transparency,
                parent=self.root,
                toon_shader=self.toon_shader,
                tree_depth=current_depth + 1,
                parent_cube=parent_cube  # Link to parent (creates connector tube)
            )

            parent_cube.children.append(child_cube)
            self.cubes.append(child_cube)

            # Recurse to create grandchildren
            self._generate_children(child_cube, current_depth + 1)

    def rebuild(self, branch_depth, branch_count, cube_size_min, cube_size_max, cube_spacing,
                blob_color, transparency, jiggle_speed, pulse_amount):
        """
        Rebuild blob with new parameters.

        Args:
            branch_depth: Maximum branching depth
            branch_count: Children per cube
            cube_size_min: Minimum cube size
            cube_size_max: Maximum cube size
            cube_spacing: Cube spacing
            blob_color: Base color RGB tuple
            transparency: Alpha transparency
            jiggle_speed: Animation speed
            pulse_amount: Pulse intensity
        """
        self.branch_depth = branch_depth
        self.branch_count = branch_count
        self.cube_size_min = cube_size_min
        self.cube_size_max = cube_size_max
        self.cube_spacing = cube_spacing
        self.blob_color = blob_color
        self.transparency = transparency
        self.jiggle_speed = jiggle_speed
        self.pulse_amount = pulse_amount

        # Regenerate cubes with new tree structure
        self._generate_cubes()

    def start_attack(self, camera_position):
        """
        Start attack animation.

        Args:
            camera_position: Vec3 position of camera (not used for blob, but kept for interface consistency)
        """
        self.is_attacking = True
        self.attack_start_time = 0  # Will be set on first update

    def update_animation(self, time, camera_position=None):
        """
        Update blob animation with cascade attack.

        Args:
            time: Current animation time
            camera_position: Optional camera position (for interface consistency)
        """
        from ..core.constants import CASCADE_ATTACK_DURATION, CASCADE_WAVE_SPEED, BLOB_JIGGLE_AMPLITUDE

        # Handle attack state
        attack_phase = 'idle'
        global_attack_progress = 0.0

        if self.is_attacking:
            # Initialize attack start time on first frame
            if self.attack_start_time == 0:
                self.attack_start_time = time

            # Calculate global attack progress (0-1)
            attack_elapsed = time - self.attack_start_time
            global_attack_progress = min(attack_elapsed / CASCADE_ATTACK_DURATION, 1.0)

            if global_attack_progress >= 1.0:
                # Attack complete
                self.is_attacking = False
                self.attack_start_time = 0
                attack_phase = 'idle'
            else:
                attack_phase = 'cascade'

        # Update all cubes with depth-aware cascade timing
        jiggle_amplitude = BLOB_JIGGLE_AMPLITUDE * (1.0 + self.pulse_amount)

        for cube in self.cubes:
            # Calculate per-cube attack timing based on tree_depth
            # Each level triggers (1 / CASCADE_WAVE_SPEED) seconds after its parent
            if self.is_attacking and attack_phase == 'cascade':
                # Delay increases with tree depth
                cube_attack_delay = cube.tree_depth / CASCADE_WAVE_SPEED
                # Calculate cube's attack progress (starts at 0 when delay passes)
                cube_attack_time = global_attack_progress * CASCADE_ATTACK_DURATION - cube_attack_delay
                # Normalize to 0-1 and clamp (2x multiplier for faster individual pulse)
                cube_attack_progress = max(0.0, min(1.0, cube_attack_time / (CASCADE_ATTACK_DURATION * 0.5)))
            else:
                cube_attack_progress = 0.0

            cube.update_animation(
                time=time,
                jiggle_speed=self.jiggle_speed,
                jiggle_amplitude=jiggle_amplitude,
                is_attacking=self.is_attacking,
                attack_progress=cube_attack_progress,  # Per-cube progress (not global)
                attack_phase=attack_phase
            )

    def enable_physics(self, drop_from_height=0.0):
        """
        Activate Verlet physics and drop creature from current position.

        Args:
            drop_from_height: DEPRECATED - kept for API compatibility, always drops from current position
        """
        print(f"  [enable_physics] Starting with {len(self.cubes)} cubes, drop_from_current_position=True")

        from ..models.blob_physics import DistanceConstraint, VerletPhysics
        from ..core.constants import (
            PHYSICS_GRAVITY_Y, PHYSICS_DAMPING, CONSTRAINT_STIFFNESS,
            CONSTRAINT_ITERATIONS, FLOOR_Y, FLOOR_RESTITUTION, FLOOR_FRICTION
        )

        # Create physics particles for each cube at their CURRENT positions
        print(f"  [enable_physics] Creating physics particles at current positions...")
        for i, cube in enumerate(self.cubes):
            # Mass proportional to cube volume (size^3)
            mass = cube.original_size ** 3
            current_pos = cube.entity.position
            print(f"    Cube {i}: starting at pos={current_pos}, size={cube.original_size}, mass={mass:.3f}")

            # Create particle at current entity position (no lifting!)
            cube.create_physics_particle(mass)
            # Physics particle is already at correct position from entity.position in create_physics_particle()

            print(f"    Cube {i}: physics particle at y={cube.physics_particle.position.y:.2f}")

        # Optional: Pin root cube to prevent spinning (uncomment if needed)
        # self.cubes[0].physics_particle.pinned = True

        # Create distance constraints for tree structure
        print(f"  [enable_physics] Creating distance constraints...")
        constraints = []
        for cube in self.cubes:
            if cube.parent_cube:
                parent_particle = cube.parent_cube.physics_particle
                child_particle = cube.physics_particle
                rest_length = (cube.original_position - cube.parent_cube.original_position).length()
                constraints.append(
                    DistanceConstraint(parent_particle, child_particle, rest_length)
                )
        print(f"  [enable_physics] Created {len(constraints)} constraints")

        # Initialize physics engine
        gravity = Vec3(0, PHYSICS_GRAVITY_Y, 0)
        print(f"  [enable_physics] Initializing physics engine (gravity={PHYSICS_GRAVITY_Y}, floor={FLOOR_Y})")

        self.physics_engine = VerletPhysics(
            particles=[cube.physics_particle for cube in self.cubes],
            constraints=constraints,
            gravity=gravity,
            damping=PHYSICS_DAMPING,
            floor_y=FLOOR_Y,
            constraint_stiffness=CONSTRAINT_STIFFNESS,
            constraint_iterations=CONSTRAINT_ITERATIONS,
            floor_restitution=FLOOR_RESTITUTION,
            floor_friction=FLOOR_FRICTION
        )

        self.physics_enabled = True
        self.physics_time = 0.0
        print(f"  [enable_physics] Physics enabled successfully")

    def disable_physics(self):
        """Disable physics and return to keyframed animation at settled positions."""
        print(f"  [disable_physics] Disabling physics, baking settled positions as new original_position")

        # Update original positions to current settled positions before disabling
        # This makes idle/attack animations play from the floor position instead of reverting
        for cube in self.cubes:
            if cube.physics_particle:
                # Store the settled position as the new original position
                cube.original_position = Vec3(
                    cube.physics_particle.position.x,
                    cube.physics_particle.position.y,
                    cube.physics_particle.position.z
                )
                print(f"    Cube original_position updated to: {cube.original_position}")

        self.physics_enabled = False
        self.physics_engine = None

        # Clear physics particles from all cubes
        for cube in self.cubes:
            cube.physics_particle = None
        print(f"  [disable_physics] Physics disabled, animations will use settled floor positions")

    def update_physics(self, dt):
        """
        Step physics simulation.

        Args:
            dt: Delta time (seconds)
        """
        if self.physics_engine:
            # Log first physics step
            if not hasattr(self, '_first_physics_logged'):
                self._first_physics_logged = True
                print(f"  [update_physics] First physics step, dt={dt}")
                print(f"    Particles: {len(self.physics_engine.particles)}")
                print(f"    Constraints: {len(self.physics_engine.constraints)}")
                if self.cubes:
                    pos = self.cubes[0].physics_particle.position
                    print(f"    First cube particle at: {pos}")

            self.physics_engine.step(dt)

            # Sync visual entities with physics particles
            for i, cube in enumerate(self.cubes):
                if cube.physics_particle:
                    cube.entity.position = cube.physics_particle.position
                    cube.entity.enabled = True  # Force visible
                    cube.entity.visible = True  # Ensure not hidden
                    cube._update_connector_tube_transform()
                    # Also ensure connector tube is visible
                    if cube.connector_tube:
                        cube.connector_tube.enabled = True
                        cube.connector_tube.visible = True

                    # Debug logging for first cube on first physics frame
                    if not hasattr(self, '_physics_debug_logged') and i == 0:
                        self._physics_debug_logged = True
                        print(f"  [ENTITY DEBUG] First cube state after physics sync:")
                        print(f"    position: {cube.entity.position}")
                        print(f"    world_position: {cube.entity.world_position}")
                        print(f"    enabled: {cube.entity.enabled}")
                        print(f"    visible: {cube.entity.visible}")
                        print(f"    alpha: {cube.entity.alpha}")
                        print(f"    parent: {cube.entity.parent}")
                        print(f"    shader: {cube.entity.shader}")
                        if hasattr(cube.entity, 'color'):
                            print(f"    color: {cube.entity.color}")

    def destroy(self):
        """Cleanup all cube entities."""
        for cube in self.cubes:
            cube.destroy()
        destroy(self.root)
