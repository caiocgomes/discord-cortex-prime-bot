"""Base classes and utilities for Discord UI views."""

import discord

from cortex_bot.utils import has_gm_permission


class CortexView(discord.ui.View):
    """Base view with timeout=None for persistent buttons."""

    def __init__(self) -> None:
        super().__init__(timeout=None)


def parse_custom_id(custom_id: str) -> tuple[str, list[str]]:
    """Parse a cortex custom_id into action and params.

    Format: cortex:{action}:{param1}:{param2}:...
    Returns: (action, [param1, param2, ...])
    """
    parts = custom_id.split(":")
    if len(parts) < 2 or parts[0] != "cortex":
        raise ValueError(f"Invalid custom_id format: {custom_id}")
    action = parts[1]
    params = parts[2:] if len(parts) > 2 else []
    return action, params


def make_custom_id(action: str, *params: str | int) -> str:
    """Build a cortex custom_id from action and params.

    Example: make_custom_id("scene_start", 42) -> "cortex:scene_start:42"
    """
    parts = ["cortex", action] + [str(p) for p in params]
    custom_id = ":".join(parts)
    if len(custom_id) > 100:
        raise ValueError(f"custom_id exceeds 100 char limit: {len(custom_id)}")
    return custom_id


async def check_gm_permission(
    interaction: discord.Interaction, campaign_id: int
) -> dict | None:
    """Check if the interacting user has GM permission.

    Returns the player dict if authorized, None otherwise.
    Sends an ephemeral error response if permission denied.
    """
    db = interaction.client.db
    player = await db.get_player(campaign_id, str(interaction.user.id))
    if player is None or not has_gm_permission(player):
        await interaction.response.send_message(
            "Apenas o GM pode usar este comando.",
            ephemeral=True,
        )
        return None
    return player


async def get_campaign_from_channel(
    interaction: discord.Interaction,
) -> dict | None:
    """Get the campaign for the current channel.

    Returns the campaign dict, or None with ephemeral error.
    """
    db = interaction.client.db
    server_id = str(interaction.guild_id)
    channel_id = str(interaction.channel_id)
    campaign = await db.get_campaign_by_channel(server_id, channel_id)
    if campaign is None:
        await interaction.response.send_message(
            "Nenhuma campanha ativa neste canal.",
            ephemeral=True,
        )
    return campaign
