"""Base classes and utilities for Discord UI views."""

from typing import Callable, Awaitable

import discord

from cortex_bot.models.dice import VALID_SIZES, die_label
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


DieCallback = Callable[[discord.Interaction, int], Awaitable[None]]
PlayerCallback = Callable[[discord.Interaction, int], Awaitable[None]]


def add_die_buttons(
    view: "CortexView",
    callback: DieCallback,
    style: discord.ButtonStyle = discord.ButtonStyle.primary,
) -> None:
    """Add 5 die-size buttons (d4-d12) to a view, each calling callback(interaction, size)."""
    for size in VALID_SIZES:
        btn = discord.ui.Button(label=die_label(size), style=style)

        async def _cb(interaction: discord.Interaction, s: int = size) -> None:
            await callback(interaction, s)

        btn.callback = _cb
        view.add_item(btn)


def add_player_options(
    view: "CortexView",
    players: list[dict],
    callback: PlayerCallback,
    extra_buttons: list[tuple[str, str | None]] | None = None,
) -> None:
    """Add player selection to a view: buttons when <= 5, select when > 5.

    extra_buttons is a list of (label, value) tuples for additional options
    like "Asset de Cena". These are always added as buttons.
    """
    if len(players) <= 5:
        for p in players:
            btn = discord.ui.Button(
                label=p["name"], style=discord.ButtonStyle.secondary
            )

            async def _cb(
                interaction: discord.Interaction, pid: int = p["id"]
            ) -> None:
                await callback(interaction, pid)

            btn.callback = _cb
            view.add_item(btn)
    else:
        options = [
            discord.SelectOption(label=p["name"], value=str(p["id"]))
            for p in players[:25]
        ]
        select = discord.ui.Select(
            placeholder="Selecione jogador", options=options
        )

        async def _sel_cb(interaction: discord.Interaction) -> None:
            await callback(interaction, int(interaction.data["values"][0]))

        select.callback = _sel_cb
        view.add_item(select)

    if extra_buttons:
        for label, value in extra_buttons:
            btn = discord.ui.Button(
                label=label, style=discord.ButtonStyle.secondary
            )

            async def _extra_cb(
                interaction: discord.Interaction, v: str | None = value
            ) -> None:
                await callback(interaction, v)

            btn.callback = _extra_cb
            view.add_item(btn)


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
