"""Shared utility functions for cogs."""


def has_gm_permission(player: dict) -> bool:
    """Check if player has GM-level permissions (is GM or delegate)."""
    return player["is_gm"] or player.get("is_delegate", 0)
