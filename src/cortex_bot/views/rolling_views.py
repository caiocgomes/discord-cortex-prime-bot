"""Rolling-related views and buttons."""

import re

import discord

from cortex_bot.views.base import CortexView, make_custom_id, get_campaign_from_channel
from cortex_bot.models.dice import parse_dice_notation, die_label
from cortex_bot.services.roller import (
    roll_pool,
    find_hitches,
    is_botch,
    calculate_best_options,
)
from cortex_bot.services.formatter import format_roll_result


class RollStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:roll_start:(?P<campaign_id>\d+)",
):
    """Persistent button to initiate a dice roll via select chain."""

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

        view = DicePoolSelectView(self.campaign_id, player["id"], player["name"])
        await interaction.response.send_message(
            "Selecione os dados para o pool de rolagem.",
            view=view,
            ephemeral=True,
        )


DIE_OPTIONS = [
    discord.SelectOption(label="d4", value="4"),
    discord.SelectOption(label="d6", value="6"),
    discord.SelectOption(label="d8", value="8"),
    discord.SelectOption(label="d10", value="10"),
    discord.SelectOption(label="d12", value="12"),
]


class DicePoolSelectView(CortexView):
    """Ephemeral view for selecting dice to roll."""

    def __init__(
        self, campaign_id: int, player_id: int, player_name: str
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.player_id = player_id
        self.player_name = player_name

    @discord.ui.select(
        placeholder="Selecione dados para o pool (multiplos permitidos)",
        options=DIE_OPTIONS,
        min_values=1,
        max_values=5,
        custom_id="cortex:dice_pool_select",
    )
    async def dice_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        pool = [int(v) for v in select.values]

        db = interaction.client.db
        assets = await db.get_player_assets(self.campaign_id, self.player_id)

        if assets:
            view = AssetIncludeSelectView(
                self.campaign_id, self.player_id, self.player_name, pool, assets
            )
            asset_labels = [
                f"{a['name']} ({die_label(a['die_size'])})" for a in assets
            ]
            await interaction.response.edit_message(
                content=f"Pool: {', '.join(die_label(d) for d in pool)}. Incluir assets?",
                view=view,
            )
        else:
            await self._execute_roll(interaction, pool, [])

    async def _execute_roll(
        self,
        interaction: discord.Interaction,
        pool: list[int],
        included_assets: list[str],
    ) -> None:
        db = interaction.client.db
        campaign = await db.get_campaign_by_id(self.campaign_id)
        config = campaign["config"] if campaign else {}

        results = roll_pool(pool)
        hitches = find_hitches(results)
        botch = is_botch(results)

        best_options: list[dict] | None = None
        if config.get("best_mode") and not botch:
            best_options = calculate_best_options(results)

        stress_list = await db.get_player_stress(self.campaign_id, self.player_id)
        complication_list = await db.get_player_complications(
            self.campaign_id, self.player_id
        )
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
            player_name=self.player_name,
            results=results,
            included_assets=included_assets or None,
            hitches=hitches or None,
            is_botch=botch,
            best_options=best_options,
            opposition_elements=opposition_elements or None,
        )
        view = PostRollView(self.campaign_id)
        await interaction.response.edit_message(content=text, view=None)
        await interaction.followup.send(text, view=view)


class AssetIncludeSelectView(CortexView):
    """Ephemeral view for optionally including assets in the roll."""

    def __init__(
        self,
        campaign_id: int,
        player_id: int,
        player_name: str,
        pool: list[int],
        assets: list[dict],
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.player_id = player_id
        self.player_name = player_name
        self.pool = pool
        self.assets = assets

        options = [
            discord.SelectOption(
                label=f"{a['name']} ({die_label(a['die_size'])})",
                value=str(a["id"]),
            )
            for a in assets[:25]
        ]
        self.asset_select = discord.ui.Select(
            placeholder="Incluir assets (opcional, pode pular)",
            options=options,
            min_values=0,
            max_values=len(options),
            custom_id="cortex:asset_include_select",
        )
        self.asset_select.callback = self._on_select
        self.add_item(self.asset_select)

        skip_btn = discord.ui.Button(
            label="Rolar sem assets",
            style=discord.ButtonStyle.secondary,
            custom_id="cortex:roll_skip_assets",
        )
        skip_btn.callback = self._on_skip
        self.add_item(skip_btn)

    async def _on_select(self, interaction: discord.Interaction) -> None:
        selected_ids = {int(v) for v in self.asset_select.values}
        asset_map = {a["id"]: a for a in self.assets}
        included_assets: list[str] = []
        full_pool = list(self.pool)

        for aid in selected_ids:
            asset = asset_map.get(aid)
            if asset:
                full_pool.append(asset["die_size"])
                included_assets.append(
                    f"{asset['name']} {die_label(asset['die_size'])}"
                )

        await self._execute_roll(interaction, full_pool, included_assets)

    async def _on_skip(self, interaction: discord.Interaction) -> None:
        await self._execute_roll(interaction, self.pool, [])

    async def _execute_roll(
        self,
        interaction: discord.Interaction,
        pool: list[int],
        included_assets: list[str],
    ) -> None:
        db = interaction.client.db
        campaign = await db.get_campaign_by_id(self.campaign_id)
        config = campaign["config"] if campaign else {}

        results = roll_pool(pool)
        hitches = find_hitches(results)
        botch = is_botch(results)

        best_options: list[dict] | None = None
        if config.get("best_mode") and not botch:
            best_options = calculate_best_options(results)

        stress_list = await db.get_player_stress(self.campaign_id, self.player_id)
        complication_list = await db.get_player_complications(
            self.campaign_id, self.player_id
        )
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
            player_name=self.player_name,
            results=results,
            included_assets=included_assets or None,
            hitches=hitches or None,
            is_botch=botch,
            best_options=best_options,
            opposition_elements=opposition_elements or None,
        )
        view = PostRollView(self.campaign_id)
        await interaction.response.edit_message(content=text, view=None)
        await interaction.followup.send(text, view=view)


class PostRollView(CortexView):
    """View shown after a roll: Roll, Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton

        self.add_item(RollStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))
