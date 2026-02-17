"""Shared utility functions for cogs."""

NO_CAMPAIGN_MSG = "No active campaign in this channel. Use /campaign setup to create one."


def has_gm_permission(player: dict) -> bool:
    """Check if player has GM-level permissions (is GM or delegate)."""
    return player["is_gm"] or player.get("is_delegate", 0)
