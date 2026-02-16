"""Dice rolling engine with Cortex Prime mechanics."""

import random
from itertools import combinations

from cortex_bot.models.dice import die_label


def roll_pool(dice: list[int]) -> list[tuple[int, int]]:
    """Roll a pool of dice. Returns list of (die_size, result)."""
    return [(size, random.randint(1, size)) for size in dice]


def find_hitches(results: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Find all dice that rolled 1 (hitches)."""
    return [(size, val) for size, val in results if val == 1]


def is_botch(results: list[tuple[int, int]]) -> bool:
    """Check if all dice rolled 1."""
    return all(val == 1 for _, val in results)


def calculate_best_options(
    results: list[tuple[int, int]],
) -> list[dict]:
    """Calculate best total and best effect die combinations.

    Excludes hitches from consideration. Returns list of options
    with label, total, dice used for total, and effect die.
    """
    non_hitch = [(size, val) for size, val in results if val != 1]
    if len(non_hitch) < 2:
        return []

    options = []
    best_total_option = None
    best_effect_option = None

    for combo in combinations(range(len(non_hitch)), 2):
        total = non_hitch[combo[0]][1] + non_hitch[combo[1]][1]
        remaining = [non_hitch[i] for i in range(len(non_hitch)) if i not in combo]
        if remaining:
            effect = max(remaining, key=lambda x: x[0])
        else:
            effect = (4, 0)

        option = {
            "dice": [non_hitch[combo[0]], non_hitch[combo[1]]],
            "total": total,
            "effect_size": effect[0],
            "effect_value": effect[1],
        }

        if best_total_option is None or total > best_total_option["total"]:
            best_total_option = option
        if best_effect_option is None or effect[0] > best_effect_option["effect_size"]:
            best_effect_option = option
        elif effect[0] == best_effect_option["effect_size"] and total > best_effect_option["total"]:
            best_effect_option = option

    if best_total_option:
        best_total_option["label"] = "Melhor total"
        options.append(best_total_option)

    if best_effect_option and best_effect_option != best_total_option:
        best_effect_option["label"] = "Maior effect"
        options.append(best_effect_option)

    return options


def evaluate_difficulty(total: int, difficulty: int) -> dict:
    """Evaluate a total against difficulty.

    Returns dict with success/fail, margin, and heroic success info.
    """
    margin = total - difficulty
    result = {
        "success": margin > 0,
        "margin": margin,
        "heroic": False,
        "heroic_steps": 0,
    }
    if margin >= 5:
        result["heroic"] = True
        result["heroic_steps"] = margin // 5
    return result
