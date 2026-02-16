"""Base classes and utilities for Discord UI views."""

import uuid
from collections.abc import Callable, Coroutine
from typing import Any

import discord

from cortex_bot.utils import has_gm_permission

DIE_SIZES = [4, 6, 8, 10, 12]


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


# Type alias for button callbacks: async fn(interaction, value) -> None
ButtonCallback = Callable[
    [discord.Interaction, int], Coroutine[Any, Any, None]
]
PlayerCallback = Callable[
    [discord.Interaction, str], Coroutine[Any, Any, None]
]


def add_die_buttons(
    view: discord.ui.View,
    callback: ButtonCallback,
) -> None:
    """Add 5 die buttons (d4-d12) to the view in a single ActionRow."""
    for size in DIE_SIZES:
        btn = discord.ui.Button(
            label=f"d{size}",
            style=discord.ButtonStyle.primary,
            custom_id=f"ephemeral:die:{size}:{uuid.uuid4().hex[:8]}",
            row=0,
        )

        async def make_callback(
            interaction: discord.Interaction,
            _btn: discord.ui.Button = btn,
            _size: int = size,
        ) -> None:
            await callback(interaction, _size)

        btn.callback = make_callback
        view.add_item(btn)


def add_player_options(
    view: discord.ui.View,
    players: list[dict],
    callback: PlayerCallback,
    extra_buttons: list[tuple[str, str]] | None = None,
) -> None:
    """Add player selection to a view.

    Uses buttons when total options (players + extra) <= 5, select when > 5.
    extra_buttons: list of (label, value) tuples for extra options like "Asset de Cena".
    """
    extras = extra_buttons or []
    total = len(players) + len(extras)

    if total <= 5:
        for p in players:
            btn = discord.ui.Button(
                label=p["name"],
                style=discord.ButtonStyle.primary,
                custom_id=f"ephemeral:player:{p['id']}:{uuid.uuid4().hex[:8]}",
            )

            async def make_player_cb(
                interaction: discord.Interaction,
                _btn: discord.ui.Button = btn,
                _val: str = str(p["id"]),
            ) -> None:
                await callback(interaction, _val)

            btn.callback = make_player_cb
            view.add_item(btn)

        for label, value in extras:
            btn = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.secondary,
                custom_id=f"ephemeral:extra:{value}:{uuid.uuid4().hex[:8]}",
            )

            async def make_extra_cb(
                interaction: discord.Interaction,
                _btn: discord.ui.Button = btn,
                _val: str = value,
            ) -> None:
                await callback(interaction, _val)

            btn.callback = make_extra_cb
            view.add_item(btn)
    else:
        options = [
            discord.SelectOption(label=p["name"], value=str(p["id"]))
            for p in players[:25]
        ]
        for label, value in extras:
            options.append(discord.SelectOption(label=label, value=value))

        select = discord.ui.Select(
            placeholder="Selecione jogador",
            options=options[:25],
            custom_id=f"ephemeral:player_sel:{uuid.uuid4().hex[:8]}",
        )

        async def on_select(
            interaction: discord.Interaction,
            _select: discord.ui.Select = select,
        ) -> None:
            await callback(interaction, _select.values[0])

        select.callback = on_select
        view.add_item(select)
