"""Rolling-related views and buttons."""

import re
import uuid
from collections import Counter

import discord

from cortex_bot.views.base import CortexView, make_custom_id, add_die_buttons, DIE_SIZES
from cortex_bot.models.dice import die_label
from cortex_bot.services.roller import (
    roll_pool,
    find_hitches,
    is_botch,
    calculate_best_options,
)
from cortex_bot.services.formatter import format_roll_result


async def execute_player_roll(
    db,
    campaign_id: int,
    player_id: int,
    player_name: str,
    pool: list[int],
    included_assets: list[str] | None = None,
) -> tuple[str, "PostRollView"]:
    """Execute a player roll and return (formatted_text, post_roll_view).

    Shared by PoolBuilderView and potentially other roll flows.
    """
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
    return text, view


class RollStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:roll_start:(?P<campaign_id>\d+)",
):
    """Persistent button to initiate a dice roll via pool builder."""

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
        assets_data = [
            {"id": a["id"], "name": a["name"], "die_size": a["die_size"]}
            for a in assets
        ]

        view = PoolBuilderView(
            self.campaign_id, player["id"], player["name"], assets_data
        )
        content = view.build_status_text()
        await interaction.response.send_message(
            content, view=view, ephemeral=True
        )


class PoolBuilderView(CortexView):
    """Interactive pool builder with buttons for dice and assets."""

    def __init__(
        self,
        campaign_id: int,
        player_id: int,
        player_name: str,
        assets_data: list[dict],
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.player_id = player_id
        self.player_name = player_name
        self.assets_data = assets_data
        self.pool: list[int] = []
        self.included_assets: set[int] = set()
        self.history: list[tuple[str, int]] = []  # ("die", size) or ("asset", asset_id)
        self._uid = uuid.uuid4().hex[:8]
        self._build_components()

    def build_status_text(self) -> str:
        if not self.pool:
            return "Pool vazio. Clique nos dados para montar o pool."
        counts = Counter(self.pool)
        parts = [f"{count}x {die_label(size)}" for size, count in sorted(counts.items())]
        return f"Pool: {', '.join(parts)}."

    def _build_components(self) -> None:
        self.clear_items()

        # Row 0: die buttons (d4-d12)
        counts = Counter(self.pool)
        for size in DIE_SIZES:
            count = counts.get(size, 0)
            label = f"+d{size}" if count == 0 else f"+d{size} ({count})"
            btn = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary,
                custom_id=f"ephemeral:pb_die:{size}:{self._uid}",
                row=0,
            )
            btn.callback = self._make_die_callback(size)
            self.add_item(btn)

        # Rows 1-2: asset buttons (up to 10 assets in 2 rows)
        if self.assets_data:
            for i, asset in enumerate(self.assets_data[:10]):
                included = asset["id"] in self.included_assets
                if included:
                    label = f"{asset['name']} {die_label(asset['die_size'])} (no pool)"
                    style = discord.ButtonStyle.success
                else:
                    label = f"{asset['name']} {die_label(asset['die_size'])}"
                    style = discord.ButtonStyle.secondary
                row = 1 + (i // 5)
                btn = discord.ui.Button(
                    label=label,
                    style=style,
                    custom_id=f"ephemeral:pb_asset:{asset['id']}:{self._uid}",
                    row=row,
                )
                btn.callback = self._make_asset_callback(asset)
                self.add_item(btn)

        # Control row (last row)
        control_row = 1
        if self.assets_data:
            control_row = 1 + min((len(self.assets_data[:10]) - 1) // 5 + 1, 2)

        total = len(self.pool)
        roll_label = f"Rolar {total} dado{'s' if total != 1 else ''}" if total > 0 else "Rolar"
        roll_btn = discord.ui.Button(
            label=roll_label,
            style=discord.ButtonStyle.success,
            custom_id=f"ephemeral:pb_roll:{self._uid}",
            row=control_row,
        )
        roll_btn.callback = self._on_roll
        self.add_item(roll_btn)

        clear_btn = discord.ui.Button(
            label="Limpar",
            style=discord.ButtonStyle.secondary,
            custom_id=f"ephemeral:pb_clear:{self._uid}",
            row=control_row,
        )
        clear_btn.callback = self._on_clear
        self.add_item(clear_btn)

        if self.history:
            undo_btn = discord.ui.Button(
                label="Remover ultimo",
                style=discord.ButtonStyle.secondary,
                custom_id=f"ephemeral:pb_undo:{self._uid}",
                row=control_row,
            )
            undo_btn.callback = self._on_remove_last
            self.add_item(undo_btn)

    def _make_die_callback(self, die_size: int):
        async def callback(interaction: discord.Interaction) -> None:
            self.pool.append(die_size)
            self.history.append(("die", die_size))
            await self._rebuild(interaction)

        return callback

    def _make_asset_callback(self, asset: dict):
        async def callback(interaction: discord.Interaction) -> None:
            aid = asset["id"]
            if aid in self.included_assets:
                self.included_assets.discard(aid)
                self.pool.remove(asset["die_size"])
                self.history.append(("asset_off", aid))
            else:
                self.included_assets.add(aid)
                self.pool.append(asset["die_size"])
                self.history.append(("asset_on", aid))
            await self._rebuild(interaction)

        return callback

    async def _on_roll(self, interaction: discord.Interaction) -> None:
        if not self.pool:
            await interaction.response.send_message(
                "Pool vazio. Adicione dados antes de rolar.", ephemeral=True
            )
            return

        asset_map = {a["id"]: a for a in self.assets_data}
        included_labels = []
        for aid in self.included_assets:
            a = asset_map.get(aid)
            if a:
                included_labels.append(f"{a['name']} {die_label(a['die_size'])}")

        db = interaction.client.db
        text, view = await execute_player_roll(
            db,
            self.campaign_id,
            self.player_id,
            self.player_name,
            list(self.pool),
            included_labels or None,
        )
        await interaction.response.edit_message(content=text, view=None)
        await interaction.followup.send(text, view=view)

    async def _on_clear(self, interaction: discord.Interaction) -> None:
        self.pool.clear()
        self.included_assets.clear()
        self.history.clear()
        await self._rebuild(interaction)

    async def _on_remove_last(self, interaction: discord.Interaction) -> None:
        if not self.history:
            await self._rebuild(interaction)
            return

        action_type, value = self.history.pop()
        if action_type == "die":
            self.pool.remove(value)
        elif action_type == "asset_on":
            asset = next((a for a in self.assets_data if a["id"] == value), None)
            if asset:
                self.included_assets.discard(value)
                self.pool.remove(asset["die_size"])
        elif action_type == "asset_off":
            asset = next((a for a in self.assets_data if a["id"] == value), None)
            if asset:
                self.included_assets.add(value)
                self.pool.append(asset["die_size"])
        await self._rebuild(interaction)

    async def _rebuild(self, interaction: discord.Interaction) -> None:
        self._build_components()
        content = self.build_status_text()
        await interaction.response.edit_message(content=content, view=self)


class PostRollView(CortexView):
    """View shown after a roll: Roll, Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton

        self.add_item(RollStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))
