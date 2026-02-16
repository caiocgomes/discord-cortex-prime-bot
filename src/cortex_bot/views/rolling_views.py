"""Rolling-related views and buttons."""

import re

import discord
from discord.ui import TextInput

from cortex_bot.views.base import CortexView, make_custom_id
from cortex_bot.models.dice import parse_dice_notation, die_label
from cortex_bot.services.roller import (
    roll_pool,
    find_hitches,
    is_botch,
    calculate_best_options,
)
from cortex_bot.services.formatter import format_roll_result


async def execute_player_roll(
    interaction: discord.Interaction,
    campaign_id: int,
    player_id: int,
    player_name: str,
    pool: list[int],
    included_assets: list[str] | None = None,
    responded: bool = False,
) -> None:
    """Execute a dice roll and send the formatted result.

    If responded=True, uses interaction.followup.send (response already consumed).
    If responded=False, uses interaction.response.send_message.
    """
    db = interaction.client.db
    campaign = await db.get_campaign_by_id(campaign_id)
    config = campaign["config"] if campaign else {}

    results = roll_pool(pool)
    hitches = find_hitches(results)
    botch = is_botch(results)

    best_options: list[dict] | None = None
    if config.get("best_mode") and not botch:
        best_options = calculate_best_options(results)

    stress_list = await db.get_player_stress(campaign_id, player_id)
    complication_list = await db.get_player_complications(campaign_id, player_id)
    opposition_elements: list[str] = []
    for s in stress_list:
        opposition_elements.append(
            f"{s['stress_type_name']} {die_label(s['die_size'])}"
        )
    for c in complication_list:
        opposition_elements.append(
            f"{c['name']} {die_label(c['die_size'])}"
        )

    text = format_roll_result(
        player_name=player_name,
        results=results,
        included_assets=included_assets or None,
        hitches=hitches or None,
        is_botch=botch,
        best_options=best_options,
        opposition_elements=opposition_elements or None,
    )
    view = PostRollView(campaign_id)

    if responded:
        await interaction.followup.send(text, view=view)
    else:
        await interaction.response.send_message(text, view=view)


class DicePoolModal(discord.ui.Modal, title="Montar Pool"):
    """Modal for composing a dice pool via text input."""

    dice_field = TextInput(
        label="Dados",
        placeholder="Ex: 2d8 1d6 1d10",
        style=discord.TextStyle.short,
        required=True,
    )
    assets_field = TextInput(
        label="Assets para incluir",
        placeholder="Nenhum asset ativo",
        style=discord.TextStyle.short,
        required=False,
    )

    def __init__(
        self,
        campaign_id: int,
        player_id: int,
        player_name: str,
        asset_hint: str,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.player_id = player_id
        self.player_name = player_name
        self.assets_field.placeholder = asset_hint

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # Parse dice notation
        try:
            pool = parse_dice_notation(self.dice_field.value)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        included_assets: list[str] = []
        assets_text = self.assets_field.value.strip() if self.assets_field.value else ""

        if assets_text:
            db = interaction.client.db
            player_assets = await db.get_player_assets(self.campaign_id, self.player_id)
            asset_lookup = {a["name"].lower(): a for a in player_assets}

            requested_names = [n.strip() for n in assets_text.split(",") if n.strip()]
            not_found: list[str] = []

            for name in requested_names:
                asset = asset_lookup.get(name.lower())
                if asset is None:
                    not_found.append(name)

            if not_found:
                available = ", ".join(
                    f"{a['name']} ({die_label(a['die_size'])})" for a in player_assets
                ) if player_assets else "nenhum"
                await interaction.response.send_message(
                    f"Assets nao encontrados: {', '.join(not_found)}. "
                    f"Disponiveis: {available}",
                    ephemeral=True,
                )
                return

            for name in requested_names:
                asset = asset_lookup[name.lower()]
                pool.append(asset["die_size"])
                included_assets.append(
                    f"{asset['name']} {die_label(asset['die_size'])}"
                )

        await execute_player_roll(
            interaction,
            self.campaign_id,
            self.player_id,
            self.player_name,
            pool,
            included_assets or None,
            responded=False,
        )


class RollStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:roll_start:(?P<campaign_id>\d+)",
):
    """Persistent button to initiate a dice roll via modal."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Roll",
                style=discord.ButtonStyle.primary,
                custom_id=make_custom_id("roll_start", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match,
    ) -> "RollStartButton":
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        player = await db.get_player(self.campaign_id, str(interaction.user.id))
        if player is None:
            await interaction.response.send_message(
                "Voce nao esta registrado nesta campanha.", ephemeral=True
            )
            return

        assets = await db.get_player_assets(self.campaign_id, player["id"])
        if assets:
            asset_hint = "Disponiveis: " + ", ".join(
                f"{a['name']} {die_label(a['die_size'])}" for a in assets
            )
        else:
            asset_hint = "Nenhum asset ativo"

        modal = DicePoolModal(
            campaign_id=self.campaign_id,
            player_id=player["id"],
            player_name=player["name"],
            asset_hint=asset_hint,
        )
        await interaction.response.send_modal(modal)


class PostRollView(CortexView):
    """View shown after a roll: Roll, Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton

        self.add_item(RollStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))
