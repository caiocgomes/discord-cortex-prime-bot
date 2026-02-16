import re

VALID_SIZES = (4, 6, 8, 10, 12)
DICE_PATTERN = re.compile(r"(\d+)?d(\d+)", re.IGNORECASE)


def is_valid_die(size: int) -> bool:
    return size in VALID_SIZES


def step_up(size: int) -> int | None:
    """Step up a die. Returns None if already d12 (beyond max)."""
    idx = VALID_SIZES.index(size)
    if idx >= len(VALID_SIZES) - 1:
        return None
    return VALID_SIZES[idx + 1]


def step_down(size: int) -> int | None:
    """Step down a die. Returns None if d4 (die is eliminated)."""
    idx = VALID_SIZES.index(size)
    if idx <= 0:
        return None
    return VALID_SIZES[idx - 1]


def die_label(size: int) -> str:
    return f"d{size}"


def parse_dice_notation(text: str) -> list[int]:
    """Parse notation like '1d8 2d6 1d10' into a flat list of die sizes.

    Returns list of individual die sizes, e.g. [8, 6, 6, 10].
    """
    dice: list[int] = []
    for match in DICE_PATTERN.finditer(text):
        count = int(match.group(1)) if match.group(1) else 1
        size = int(match.group(2))
        if not is_valid_die(size):
            raise ValueError(f"d{size} is not a valid Cortex die. Use d4, d6, d8, d10, or d12.")
        dice.extend([size] * count)
    if not dice:
        raise ValueError(
            "No valid dice found. Use notation like '1d8 2d6' (valid sizes: d4, d6, d8, d10, d12)."
        )
    return dice


def parse_single_die(text: str) -> int:
    """Parse a single die notation like 'd8' or 'D10' into size int."""
    text = text.strip().lower()
    if text.startswith("d"):
        text = text[1:]
    size = int(text)
    if not is_valid_die(size):
        raise ValueError(f"d{size} is not a valid Cortex die. Use d4, d6, d8, d10, or d12.")
    return size
