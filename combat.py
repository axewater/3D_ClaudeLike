"""
Combat system for Claude-Like
"""
import random
from typing import Tuple
import constants as c
from constants import get_enemy_display_name
from entities import Player, Enemy


def calculate_damage(attacker_attack: int, defender_defense: int) -> int:
    """Calculate damage dealt in combat"""
    # Base damage = attack - defense (minimum 1)
    base_damage = max(1, attacker_attack - defender_defense)

    # Add variance
    variance = int(base_damage * c.DAMAGE_VARIANCE)
    damage = random.randint(base_damage - variance, base_damage + variance)

    return max(1, damage)


def resolve_combat(attacker, defender) -> Tuple[int, bool]:
    """
    Resolve combat between attacker and defender.
    Returns: (damage_dealt, target_died)
    """
    damage = calculate_damage(attacker.attack, defender.defense)
    target_alive = defender.take_damage(damage)

    return (damage, not target_alive)


def player_attack_enemy(player: Player, enemy: Enemy, is_backstab: bool = False) -> Tuple[str, bool, int, bool]:
    """
    Player attacks enemy.
    Returns: (message, enemy_died, xp_gained, was_backstab)
    """
    damage = calculate_damage(player.attack, enemy.defense)

    # Apply backstab bonus if applicable
    if is_backstab:
        damage = int(damage * c.BACKSTAB_DAMAGE_MULTIPLIER)

    # Apply damage
    target_alive = enemy.take_damage(damage)
    enemy_died = not target_alive

    if enemy_died:
        xp = enemy.xp_reward
        enemy_name = get_enemy_display_name(enemy.enemy_type)
        if is_backstab:
            message = f"BACKSTAB! You dealt {damage} damage and killed the {enemy_name}! (+{xp} XP)"
        else:
            message = f"You dealt {damage} damage and killed the {enemy_name}! (+{xp} XP)"
        return (message, True, xp, is_backstab)
    else:
        enemy_name = get_enemy_display_name(enemy.enemy_type)
        if is_backstab:
            message = f"BACKSTAB! You dealt {damage} damage to the {enemy_name}. ({enemy.hp}/{enemy.max_hp} HP)"
        else:
            message = f"You dealt {damage} damage to the {enemy_name}. ({enemy.hp}/{enemy.max_hp} HP)"
        return (message, False, 0, is_backstab)


def enemy_attack_player(enemy: Enemy, player: Player) -> Tuple[str, bool]:
    """
    Enemy attacks player.
    Returns: (message, player_died)
    """
    damage, player_died = resolve_combat(enemy, player)
    enemy_name = get_enemy_display_name(enemy.enemy_type)

    if player_died:
        message = f"The {enemy_name} dealt {damage} damage and killed you!"
        return (message, True)
    else:
        message = f"The {enemy_name} dealt {damage} damage to you. ({player.hp}/{player.max_hp} HP)"
        return (message, False)
