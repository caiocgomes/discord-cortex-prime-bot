"""Rolling-related views and buttons."""

import re
import uuid
from collections import Counter

import discord

from cortex_bot.views.base import (
    CortexView,
    make_custom_id,
    check_gm_permission,
    add_die_buttons,
    add_player_options,
    DIE_SIZES,
)
from cortex_bot.models.dice import die_label
from cortex_bot.utils import has_gm_permission
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
    is_gm_roll: bool = False,
) -> tuple[str, "PostRollView"]:
    """Execute a player roll and return (formatted_text, post_roll_view).

    Shared by PoolBuilderView and potentially other roll flows.
    When is_gm_roll=True, skips opposition_elements lookup (GM IS the opposition)
    and does not inject any state side effects.
    """
    campaign = await db.get_campaign_by_id(campaign_id)
    config = campaign["config"] if campaign else {}

    results = roll_pool(pool)
    hitches = find_hitches(results)
    botch = is_botch(results)

    best_options: list[dict] | None = None
    if config.get("best_mode") and not botch:
        best_options = calculate_best_options(results)

    opposition_elements: list[str] | None = None
    if not is_gm_roll:
        stress_list = await db.get_player_stress(campaign_id, player_id)
        complication_list = await db.get_player_complications(campaign_id, player_id)
        opp: list[str] = []
        for s in stress_list:
            opp.append(
                f"{s['stress_type_name']} {die_label(s['die_size'])}"
            )
        for c in complication_list:
            opp.append(
                f"{c['name']} {die_label(c['die_size'])}"
            )
        opposition_elements = opp or None

    text = format_roll_result(
        player_name=player_name,
        results=results,
        included_assets=included_assets or None,
        hitches=hitches or None,
        is_botch=botch,
        best_options=best_options,
        opposition_elements=opposition_elements,
    )
    has_hitches = bool(hitches) and not botch
    doom_enabled = config.get("doom_pool", False)
    view = PostRollView(
        campaign_id,
        has_hitches=has_hitches,
        doom_enabled=doom_enabled,
    )
    return text, view


async def _build_gm_toggles(db, campaign_id: int) -> list[dict]:
    """Build toggle_items for GM: stress and complications from all players + scene."""
    toggle_items: list[dict] = []

    players = await db.get_players(campaign_id)
    for p in players:
        stress_list = await db.get_player_stress(campaign_id, p["id"])
        for s in stress_list:
            toggle_items.append({
                "id": f"stress:{s['id']}",
                "label": f"{p['name']}: {s['stress_type_name']} {die_label(s['die_size'])}",
                "die_size": s["die_size"],
            })
        comp_list = await db.get_player_complications(campaign_id, p["id"])
        for c in comp_list:
            toggle_items.append({
                "id": f"comp:{c['id']}",
                "label": f"{p['name']}: {c['name']} {die_label(c['die_size'])}",
                "die_size": c["die_size"],
            })

    scene = await db.get_active_scene(campaign_id)
    if scene:
        scene_comps = await db.get_scene_complications(scene["id"])
        for c in scene_comps:
            if c.get("player_name") is None:
                toggle_items.append({
                    "id": f"comp:{c['id']}",
                    "label": f"Cena: {c['name']} {die_label(c['die_size'])}",
                    "die_size": c["die_size"],
                })

    return toggle_items


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

        if has_gm_permission(player):
            toggle_items = await _build_gm_toggles(db, self.campaign_id)
            is_gm_roll = True
        else:
            assets = await db.get_player_assets(self.campaign_id, player["id"])
            toggle_items = [
                {
                    "id": f"asset:{a['id']}",
                    "label": f"{a['name']} {die_label(a['die_size'])}",
                    "die_size": a["die_size"],
                }
                for a in assets
            ]
            is_gm_roll = False

        view = PoolBuilderView(
            self.campaign_id, player["id"], player["name"], toggle_items,
            is_gm_roll=is_gm_roll,
        )
        content = view.build_status_text()
        await interaction.response.send_message(
            content, view=view, ephemeral=True
        )


class PoolBuilderView(CortexView):
    """Interactive pool builder with buttons for dice and toggles (assets, stress, complications)."""

    def __init__(
        self,
        campaign_id: int,
        player_id: int,
        player_name: str,
        toggle_items: list[dict],
        is_gm_roll: bool = False,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.player_id = player_id
        self.player_name = player_name
        self.toggle_items = toggle_items
        self.is_gm_roll = is_gm_roll
        self.pool: list[int] = []
        self.included_toggles: set[str] = set()
        self.history: list[tuple[str, str | int]] = []  # ("die", size) or ("toggle_on/off", str_id)
        self._uid = uuid.uuid4().hex[:8]
        self._build_components()

    def build_status_text(self) -> str:
        lines = []
        if not self.pool:
            lines.append("Pool vazio. Clique nos dados para montar o pool.")
        else:
            counts = Counter(self.pool)
            parts = [f"{count}x {die_label(size)}" for size, count in sorted(counts.items())]
            lines.append(f"Pool: {', '.join(parts)}.")
        if len(self.toggle_items) > 15:
            lines.append(f"Mostrando 15 de {len(self.toggle_items)} itens disponiveis.")
        return "\n".join(lines)

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

        # Rows 1-3: toggle buttons (up to 15 items in 3 rows)
        visible_toggles = self.toggle_items[:15]
        if visible_toggles:
            for i, item in enumerate(visible_toggles):
                included = item["id"] in self.included_toggles
                if included:
                    label = f"{item['label']} (no pool)"
                    style = discord.ButtonStyle.success
                else:
                    label = item["label"]
                    style = discord.ButtonStyle.secondary
                row = 1 + (i // 5)
                btn = discord.ui.Button(
                    label=label,
                    style=style,
                    custom_id=f"ephemeral:pb_toggle:{item['id']}:{self._uid}",
                    row=row,
                )
                btn.callback = self._make_toggle_callback(item)
                self.add_item(btn)

        # Control row (last row)
        control_row = 1
        if visible_toggles:
            control_row = 1 + min((len(visible_toggles) - 1) // 5 + 1, 3)

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

    def _make_toggle_callback(self, item: dict):
        async def callback(interaction: discord.Interaction) -> None:
            tid = item["id"]
            if tid in self.included_toggles:
                self.included_toggles.discard(tid)
                self.pool.remove(item["die_size"])
                self.history.append(("toggle_off", tid))
            else:
                self.included_toggles.add(tid)
                self.pool.append(item["die_size"])
                self.history.append(("toggle_on", tid))
            await self._rebuild(interaction)

        return callback

    async def _on_roll(self, interaction: discord.Interaction) -> None:
        if not self.pool:
            await interaction.response.send_message(
                "Pool vazio. Adicione dados antes de rolar.", ephemeral=True
            )
            return

        toggle_map = {t["id"]: t for t in self.toggle_items}
        included_labels = []
        for tid in self.included_toggles:
            t = toggle_map.get(tid)
            if t:
                included_labels.append(t["label"])

        db = interaction.client.db
        text, view = await execute_player_roll(
            db,
            self.campaign_id,
            self.player_id,
            self.player_name,
            list(self.pool),
            included_labels or None,
            is_gm_roll=self.is_gm_roll,
        )
        await interaction.response.edit_message(content=text, view=None)
        await interaction.followup.send(text, view=view)

    async def _on_clear(self, interaction: discord.Interaction) -> None:
        self.pool.clear()
        self.included_toggles.clear()
        self.history.clear()
        await self._rebuild(interaction)

    async def _on_remove_last(self, interaction: discord.Interaction) -> None:
        if not self.history:
            await self._rebuild(interaction)
            return

        action_type, value = self.history.pop()
        if action_type == "die":
            self.pool.remove(value)
        elif action_type == "toggle_on":
            item = next((t for t in self.toggle_items if t["id"] == value), None)
            if item:
                self.included_toggles.discard(value)
                self.pool.remove(item["die_size"])
        elif action_type == "toggle_off":
            item = next((t for t in self.toggle_items if t["id"] == value), None)
            if item:
                self.included_toggles.add(value)
                self.pool.append(item["die_size"])
        await self._rebuild(interaction)

    async def _rebuild(self, interaction: discord.Interaction) -> None:
        self._build_components()
        content = self.build_status_text()
        await interaction.response.edit_message(content=content, view=self)


class HitchComplicationButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:hitch_comp:(?P<campaign_id>\d+)",
):
    """Persistent button to create a complication from a hitch."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Criar complicacao",
                style=discord.ButtonStyle.danger,
                custom_id=make_custom_id("hitch_comp", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        players = await db.get_players(self.campaign_id)
        non_gm = [p for p in players if not p["is_gm"]]

        if not non_gm:
            await interaction.response.send_message(
                "Nenhum jogador registrado.", ephemeral=True
            )
            return

        view = HitchPlayerSelectView(self.campaign_id, str(interaction.user.id))

        async def on_player(interaction: discord.Interaction, value: str) -> None:
            await view._on_player_selected(interaction, int(value))

        add_player_options(view, non_gm, on_player)
        await interaction.response.send_message(
            "Selecione o jogador que recebe a complicacao.",
            view=view,
            ephemeral=True,
        )


class HitchPlayerSelectView(CortexView):
    """Select player to receive hitch complication."""

    def __init__(self, campaign_id: int, actor_id: str) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id

    async def _on_player_selected(
        self, interaction: discord.Interaction, player_id: int
    ) -> None:
        modal = ComplicationNameModal(
            self.campaign_id, self.actor_id, player_id
        )
        await interaction.response.send_modal(modal)


class ComplicationNameModal(discord.ui.Modal, title="Nome da complicacao"):
    """Modal to input complication name for hitch resolution."""

    name_input = discord.ui.TextInput(
        label="Nome da complicacao",
        placeholder="Ex: Desarmado, Cego, Confuso",
        max_length=50,
    )

    def __init__(self, campaign_id: int, actor_id: str, player_id: int) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id

    async def on_submit(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        comp_name = self.name_input.value.strip()
        if not comp_name:
            await interaction.response.send_message(
                "Nome da complicacao nao pode ser vazio.", ephemeral=True
            )
            return

        player = await db.get_player_by_id(self.player_id)
        if player is None:
            await interaction.response.send_message(
                "Jogador nao encontrado.", ephemeral=True
            )
            return

        player_name = player["name"]
        scene = await db.get_active_scene(self.campaign_id)
        scene_id = scene["id"] if scene else None

        from cortex_bot.services.state_manager import StateManager

        state_mgr = StateManager(db)

        # Check for existing complication with same name on this player
        existing_comps = await db.get_player_complications(
            self.campaign_id, self.player_id
        )
        existing = next(
            (c for c in existing_comps if c["name"].lower() == comp_name.lower()),
            None,
        )

        if existing:
            result = await state_mgr.step_up_complication(
                self.campaign_id, self.actor_id, existing["id"]
            )
            if result and result.get("taken_out"):
                comp_msg = (
                    f"Complicacao {comp_name} ja estava em d12 em {player_name}. "
                    "Taken out."
                )
            elif result:
                comp_msg = (
                    f"Complicacao {comp_name} em {player_name} fez step up: "
                    f"{die_label(result['from'])} para {die_label(result['to'])}."
                )
            else:
                comp_msg = "Erro ao fazer step up da complicacao."
        else:
            await state_mgr.add_complication(
                self.campaign_id,
                self.actor_id,
                comp_name,
                6,
                player_id=self.player_id,
                scene_id=scene_id,
                player_name=player_name,
            )
            comp_msg = f"Complicacao {comp_name} d6 criada em {player_name}."

        # Give 1 PP to the target player
        pp_result = await state_mgr.update_pp(
            self.campaign_id, self.actor_id, self.player_id, 1, player_name
        )
        pp_msg = f"{player_name} recebeu 1 PP (agora {pp_result['to']})."

        await interaction.response.send_message(f"{comp_msg} {pp_msg}")


class HitchDoomButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:hitch_doom:(?P<campaign_id>\d+)",
):
    """Persistent button to add d6 to doom pool from a hitch."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="+Doom",
                style=discord.ButtonStyle.danger,
                custom_id=make_custom_id("hitch_doom", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        actor_id = str(interaction.user.id)

        async with db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO doom_pool_dice (campaign_id, die_size) VALUES (?, ?)",
                (self.campaign_id, 6),
            )
            doom_die_id = cursor.lastrowid
            await conn.commit()

        await db.log_action(
            self.campaign_id,
            actor_id,
            "doom_add",
            {"die_size": 6},
            {"action": "delete", "table": "doom_pool_dice", "id": doom_die_id},
        )

        pool = await db.get_doom_pool(self.campaign_id)
        labels = [die_label(d["die_size"]) for d in pool]
        pool_str = ", ".join(labels) if labels else "vazio"
        await interaction.response.send_message(
            f"Adicionado d6 ao Doom Pool. Doom Pool: {pool_str}."
        )


class PostRollView(CortexView):
    """View shown after a roll: Roll, Undo, plus conditional hitch/doom/menu buttons."""

    def __init__(
        self,
        campaign_id: int,
        has_hitches: bool = False,
        doom_enabled: bool = False,
    ) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton, MenuButton

        # Row 0: core actions
        self.add_item(RollStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))

        # Hitch actions (GM-only buttons, visible to all but permission-checked on click)
        if has_hitches:
            self.add_item(HitchComplicationButton(campaign_id))
            if doom_enabled:
                self.add_item(HitchDoomButton(campaign_id))

        # Doom Roll (when doom enabled, even without hitches)
        if doom_enabled:
            from cortex_bot.views.doom_views import DoomRollButton

            self.add_item(DoomRollButton(campaign_id))

        self.add_item(MenuButton(campaign_id))
