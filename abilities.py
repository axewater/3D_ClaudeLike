"""
Ability system for Claude-Like
"""
from typing import Tuple, List
import constants as c
from audio import get_audio_manager


class Ability:
    """Base ability class"""
    def __init__(self, name: str, description: str, cooldown: int, ability_type: str):
        self.name = name
        self.description = description
        self.max_cooldown = cooldown
        self.current_cooldown = 0
        self.ability_type = ability_type  # damage, heal, utility, buff

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        """
        Use the ability. Returns (success, message).
        Override in subclasses.
        """
        if not self.is_ready():
            return (False, f"{self.name} is on cooldown ({self.current_cooldown} turns)")

        self.current_cooldown = self.max_cooldown
        return (True, f"Used {self.name}!")

    def is_ready(self) -> bool:
        """Check if ability is off cooldown"""
        return self.current_cooldown == 0

    def reduce_cooldown(self):
        """Reduce cooldown by 1"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class Fireball(Ability):
    """AOE damage ability"""
    def __init__(self):
        super().__init__("Fireball", "Deal 20 damage in 3x3 area", 5, "damage")
        self.damage = 20
        self.radius = 1

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        # Play fireball sound
        audio = get_audio_manager()
        audio.play_ability_sound('Fireball')

        # Deal damage to all enemies in radius
        tx, ty = target_pos
        hit_count = 0

        # Create fireball trail from caster to target
        import math
        dx = tx - user.x
        dy = ty - user.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            steps = max(int(distance), 1)
            for i in range(steps + 1):
                t = i / max(steps, 1)
                trail_x = int(user.x + dx * t)
                trail_y = int(user.y + dy * t)
                game.anim_manager.add_ability_trail(trail_x, trail_y, (1.0, 150/255, 0.0), "fireball")

        for enemy in game.enemies[:]:
            dist_x = abs(enemy.x - tx)
            dist_y = abs(enemy.y - ty)
            if dist_x <= self.radius and dist_y <= self.radius:
                enemy.take_damage(self.damage)
                hit_count += 1

                # Create animations (using RGB tuples)
                game.anim_manager.add_floating_text(enemy.x, enemy.y, str(self.damage), (1.0, 150/255, 50/255))
                game.anim_manager.add_particle_burst(enemy.x, enemy.y, (1.0, 100/255, 0.0), count=15, particle_type="circle")

                # Directional impact
                game.anim_manager.add_directional_impact(enemy.x, enemy.y, user.x, user.y,
                                                        (1.0, 120/255, 0.0), count=12)

                if enemy.hp <= 0:
                    game.anim_manager.add_death_burst(enemy.x, enemy.y, enemy.enemy_type)
                    game.enemies.remove(enemy)
                    xp = enemy.xp_reward
                    user.gain_xp(xp)

        game.anim_manager.add_screen_shake(4.0, 0.2)

        return (True, f"Fireball hit {hit_count} enemies!")


class Dash(Ability):
    """Teleport ability"""
    def __init__(self):
        super().__init__("Dash", "Teleport up to 4 tiles", 4, "utility")
        self.max_distance = 4

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        tx, ty = target_pos

        # Check if target is valid
        if not game.dungeon.is_walkable(tx, ty):
            self.current_cooldown = 0  # Refund cooldown
            return (False, "Cannot dash to that location!")

        # Check distance
        dist = abs(tx - user.x) + abs(ty - user.y)
        if dist > self.max_distance:
            self.current_cooldown = 0  # Refund cooldown
            return (False, f"Too far! Max distance: {self.max_distance}")

        # Play dash sound
        audio = get_audio_manager()
        audio.play_ability_sound('Dash')

        # Teleport
        old_x, old_y = user.x, user.y
        user.set_pos(tx, ty)

        # Create animations (using RGB tuples)
        # Speed trail between old and new position
        import math
        dx = tx - old_x
        dy = ty - old_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            steps = max(int(distance * 2), 1)  # More steps for smoother trail
            for i in range(steps + 1):
                t = i / max(steps, 1)
                trail_x = int(old_x + dx * t)
                trail_y = int(old_y + dy * t)
                game.anim_manager.add_ability_trail(trail_x, trail_y, (150/255, 150/255, 1.0), "dash")

        game.anim_manager.add_particle_burst(old_x, old_y, (150/255, 150/255, 1.0), count=12, particle_type="star")
        game.anim_manager.add_particle_burst(tx, ty, (150/255, 150/255, 1.0), count=12, particle_type="star")

        return (True, "Dashed!")


class HealingTouch(Ability):
    """Self-heal ability"""
    def __init__(self):
        super().__init__("Healing Touch", "Restore 40 HP", 8, "heal")
        self.heal_amount = 40

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        # Play healing sound
        audio = get_audio_manager()
        audio.play_ability_sound('Healing Touch')

        # Heal player
        old_hp = user.hp
        user.heal(self.heal_amount)
        actual_heal = user.hp - old_hp

        # Create animations (using RGB tuples)
        game.anim_manager.add_floating_text(user.x, user.y, f"+{actual_heal}", (100/255, 1.0, 100/255))
        game.anim_manager.add_heal_sparkles(user.x, user.y)

        return (True, f"Healed {actual_heal} HP!")


class FrostNova(Ability):
    """AOE freeze ability"""
    def __init__(self):
        super().__init__("Frost Nova", "Freeze enemies around you", 6, "utility")
        self.radius = 2
        self.freeze_duration = 2

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        # Play frost sound
        audio = get_audio_manager()
        audio.play_ability_sound('Frost Nova')

        # Freeze all nearby enemies
        frozen_count = 0

        # Create expanding ice crystal ring (using RGB tuples)
        for radius in range(self.radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) == radius:  # Only on the ring
                        ice_x = user.x + dx
                        ice_y = user.y + dy
                        if 0 <= ice_x < c.GRID_WIDTH and 0 <= ice_y < c.GRID_HEIGHT:
                            game.anim_manager.add_ability_trail(ice_x, ice_y, (150/255, 200/255, 1.0), "ice")

        for enemy in game.enemies:
            dist = abs(enemy.x - user.x) + abs(enemy.y - user.y)
            if dist <= self.radius:
                # Apply frozen status effect
                enemy.frozen_turns = self.freeze_duration
                frozen_count += 1

                # Create animations (using RGB tuples)
                game.anim_manager.add_particle_burst(enemy.x, enemy.y, (150/255, 220/255, 1.0), count=12, particle_type="star")
                game.anim_manager.add_flash_effect(enemy.x, enemy.y, (200/255, 230/255, 1.0))

        return (True, f"Froze {frozen_count} enemies for {self.freeze_duration} turns!")


class Whirlwind(Ability):
    """Melee AOE attack"""
    def __init__(self):
        super().__init__("Whirlwind", "Attack all adjacent enemies", 5, "damage")

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        # Play whirlwind sound
        audio = get_audio_manager()
        audio.play_ability_sound('Whirlwind')

        # Create circular slash effect around player (using RGB tuples)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:  # Skip center
                    slash_x = user.x + dx
                    slash_y = user.y + dy
                    if 0 <= slash_x < c.GRID_WIDTH and 0 <= slash_y < c.GRID_HEIGHT:
                        game.anim_manager.add_trail(slash_x, slash_y, (1.0, 150/255, 150/255), "fade")
                        # Add directional particles for spinning effect
                        game.anim_manager.add_directional_impact(slash_x, slash_y, user.x, user.y,
                                                                (1.0, 120/255, 120/255), count=6)

        # Attack all adjacent enemies
        hit_count = 0
        total_damage = 0

        for enemy in game.enemies[:]:
            dist = abs(enemy.x - user.x) + abs(enemy.y - user.y)
            if dist == 1:  # Adjacent
                damage = user.attack
                enemy.take_damage(damage)
                hit_count += 1
                total_damage += damage

                # Create animations (using RGB tuples)
                game.anim_manager.add_floating_text(enemy.x, enemy.y, str(damage), (1.0, 100/255, 100/255))
                game.anim_manager.add_flash_effect(enemy.x, enemy.y)

                if enemy.hp <= 0:
                    game.anim_manager.add_death_burst(enemy.x, enemy.y, enemy.enemy_type)
                    game.enemies.remove(enemy)
                    xp = enemy.xp_reward
                    user.gain_xp(xp)

        if hit_count > 0:
            game.anim_manager.add_screen_shake(4.0, 0.2)

        return (True, f"Whirlwind hit {hit_count} enemies for {total_damage} total damage!")


class ShadowStep(Ability):
    """Rogue teleport with backstab"""
    def __init__(self):
        super().__init__("Shadow Step", "Teleport behind enemy for bonus damage", 6, "utility")

    def use(self, user, target_pos: Tuple[int, int], game) -> Tuple[bool, str]:
        success, msg = super().use(user, target_pos, game)
        if not success:
            return (success, msg)

        # Find enemy at target
        target_enemy = None
        for enemy in game.enemies:
            if enemy.x == target_pos[0] and enemy.y == target_pos[1]:
                target_enemy = enemy
                break

        if not target_enemy:
            self.current_cooldown = 0  # Refund
            return (False, "No enemy at target location!")

        # Find position behind enemy
        dx = target_enemy.x - user.x
        dy = target_enemy.y - user.y

        behind_x = target_enemy.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        behind_y = target_enemy.y + (1 if dy > 0 else -1 if dy < 0 else 0)

        if not game.dungeon.is_walkable(behind_x, behind_y):
            self.current_cooldown = 0  # Refund
            return (False, "Cannot teleport behind enemy!")

        # Play shadow step sound
        audio = get_audio_manager()
        audio.play_ability_sound('Shadow Step')

        # Teleport
        old_x, old_y = user.x, user.y
        user.set_pos(behind_x, behind_y)

        # Deal bonus damage
        damage = int(user.attack * 1.5)
        target_enemy.take_damage(damage)

        # Animations (using RGB tuples)
        # Dark shadow trail
        import math
        dx = behind_x - old_x
        dy = behind_y - old_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            steps = max(int(distance * 2), 1)
            for i in range(steps + 1):
                t = i / max(steps, 1)
                trail_x = int(old_x + dx * t)
                trail_y = int(old_y + dy * t)
                # Dark purple/black smoke
                smoke_color = (80/255, 20/255, 100/255)
                game.anim_manager.add_trail(trail_x, trail_y, smoke_color, "fade")

        game.anim_manager.add_floating_text(target_enemy.x, target_enemy.y, str(damage), (200/255, 100/255, 1.0), is_crit=True)
        game.anim_manager.add_particle_burst(behind_x, behind_y, (120/255, 40/255, 180/255), count=20, particle_type="star")
        game.anim_manager.add_directional_impact(target_enemy.x, target_enemy.y, behind_x, behind_y,
                                                (150/255, 50/255, 200/255), count=15, is_crit=True)

        if target_enemy.hp <= 0:
            game.anim_manager.add_death_burst(target_enemy.x, target_enemy.y, target_enemy.enemy_type)
            game.enemies.remove(target_enemy)
            xp = target_enemy.xp_reward
            user.gain_xp(xp)

        return (True, f"Shadow Step dealt {damage} damage!")


# Class-specific ability sets
CLASS_ABILITIES = {
    c.CLASS_WARRIOR: [HealingTouch(), Whirlwind(), Dash()],
    c.CLASS_MAGE: [Fireball(), FrostNova(), HealingTouch()],
    c.CLASS_ROGUE: [ShadowStep(), Dash(), HealingTouch()],
    c.CLASS_RANGER: [Fireball(), Dash(), HealingTouch()],
}
