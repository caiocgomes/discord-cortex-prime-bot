"""State-related views: stress, asset, complication select chains."""

import re
import uuid

import discord

from cortex_bot.views.base import (
    CortexView,
    make_custom_id,
    check_gm_permission,
    add_die_buttons,
    add_player_options,
)
from cortex_bot.models.dice import die_label, parse_single_die
from cortex_bot.services.state_manager import StateManager
from cortex_bot.services.formatter import format_action_confirm


# ---------------------------------------------------------------------------
# Stress Add chain
# ---------------------------------------------------------------------------


class StressAddStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:stress_add_start:(?P<campaign_id>\d+)",
):
    """Button to start stress add chain: player -> type -> die."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Stress Add",
                style=discord.ButtonStyle.danger,
                custom_id=make_custom_id("stress_add_start", campaign_id),
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
                "Nenhum jogador registrado na campanha.", ephemeral=True
            )
            return

        view = StressPlayerSelectView(self.campaign_id, str(interaction.user.id))

        async def on_player(interaction: discord.Interaction, value: str) -> None:
            await view._on_player_selected(interaction, int(value))

        add_player_options(view, non_gm, on_player)
        await interaction.response.send_message(
            "Selecione o jogador para receber stress.",
            view=view,
            ephemeral=True,
        )


class StressPlayerSelectView(CortexView):
    """Select player for stress add."""

    def __init__(self, campaign_id: int, actor_id: str) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id

    async def _on_player_selected(
        self, interaction: discord.Interaction, player_id: int
    ) -> None:
        db = interaction.client.db
        stress_types = await db.get_stress_types(self.campaign_id)

        if not stress_types:
            await interaction.response.edit_message(
                content="Nenhum tipo de stress configurado.", view=None
            )
            return

        view = StressTypeSelectView(
            self.campaign_id, self.actor_id, player_id
        )

        uid = uuid.uuid4().hex[:8]
        for st in stress_types[:4]:
            btn = discord.ui.Button(
                label=st["name"],
                style=discord.ButtonStyle.primary,
                custom_id=f"ephemeral:stress_type:{st['id']}:{uid}",
            )

            async def make_cb(
                interaction: discord.Interaction,
                _btn: discord.ui.Button = btn,
                _type_id: int = st["id"],
            ) -> None:
                await view._on_type_selected(interaction, _type_id)

            btn.callback = make_cb
            view.add_item(btn)

        await interaction.response.edit_message(
            content="Selecione o tipo de stress.", view=view
        )


class StressTypeSelectView(CortexView):
    """Select stress type via dynamic buttons."""

    def __init__(self, campaign_id: int, actor_id: str, player_id: int) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id

    async def _on_type_selected(
        self, interaction: discord.Interaction, stress_type_id: int
    ) -> None:
        view = StressDieSelectView(
            self.campaign_id, self.actor_id, self.player_id, stress_type_id
        )

        async def on_die(interaction: discord.Interaction, die_size: int) -> None:
            await view._on_die_selected(interaction, die_size)

        add_die_buttons(view, on_die)
        await interaction.response.edit_message(
            content="Selecione o dado de stress.", view=view
        )


class StressDieSelectView(CortexView):
    """Select die for stress add, then execute."""

    def __init__(
        self, campaign_id: int, actor_id: str, player_id: int, stress_type_id: int
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id
        self.stress_type_id = stress_type_id

    async def _on_die_selected(
        self, interaction: discord.Interaction, die_size: int
    ) -> None:
        db = interaction.client.db

        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT name FROM players WHERE id = ?", (self.player_id,)
            )
            row = await cursor.fetchone()
            player_name = row["name"] if row else "Jogador"

            cursor = await conn.execute(
                "SELECT name FROM stress_types WHERE id = ?", (self.stress_type_id,)
            )
            row = await cursor.fetchone()
            type_name = row["name"] if row else "Stress"

        sm = StateManager(db)
        result = await sm.add_stress(
            self.campaign_id,
            self.actor_id,
            self.player_id,
            self.stress_type_id,
            die_size,
            player_name=player_name,
            type_name=type_name,
        )

        action = result.get("action")
        if action == "added":
            msg = format_action_confirm(
                "Stress adicionado",
                f"{player_name} recebe {type_name} {die_label(die_size)}.",
            )
        elif action == "replaced":
            msg = format_action_confirm(
                "Stress substituido",
                f"{player_name} {type_name} de {die_label(result['from'])} para {die_label(result['to'])}.",
            )
        elif action == "stepped_up":
            msg = format_action_confirm(
                "Stress step up",
                f"{player_name} {type_name} de {die_label(result['from'])} para {die_label(result['to'])}.",
            )
        elif action == "stressed_out":
            msg = format_action_confirm(
                "Stressed out",
                f"{player_name} stressed out em {type_name}.",
            )
        else:
            msg = f"Stress processado para {player_name}."

        view = PostStressView(self.campaign_id)
        await interaction.response.edit_message(content=msg, view=None)
        await interaction.followup.send(msg, view=view)


# ---------------------------------------------------------------------------
# Asset Add chain
# ---------------------------------------------------------------------------


class AssetAddStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:asset_add_start:(?P<campaign_id>\d+)",
):
    """Button to start asset add chain."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Asset Add",
                style=discord.ButtonStyle.success,
                custom_id=make_custom_id("asset_add_start", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        player = await db.get_player(self.campaign_id, str(interaction.user.id))
        if player is None:
            await interaction.response.send_message(
                "Voce nao esta registrado nesta campanha.", ephemeral=True
            )
            return

        players = await db.get_players(self.campaign_id)

        view = AssetOwnerSelectView(
            self.campaign_id, str(interaction.user.id), player
        )

        async def on_owner(interaction: discord.Interaction, value: str) -> None:
            await view._on_owner_selected(interaction, value)

        add_player_options(
            view,
            players,
            on_owner,
            extra_buttons=[("Asset de Cena", "scene")],
        )
        await interaction.response.send_message(
            "Para quem e o asset?", view=view, ephemeral=True
        )


class AssetOwnerSelectView(CortexView):
    """Select owner for asset add."""

    def __init__(self, campaign_id: int, actor_id: str, actor: dict) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.actor = actor

    async def _on_owner_selected(
        self, interaction: discord.Interaction, val: str
    ) -> None:
        is_scene = val == "scene"
        player_id = None if is_scene else int(val)

        if is_scene:
            from cortex_bot.utils import has_gm_permission

            if not has_gm_permission(self.actor):
                await interaction.response.edit_message(
                    content="Apenas o GM pode criar assets de cena.", view=None
                )
                return

        common_names = [
            "Advantage", "Cover", "Weapon", "Shield", "Tool",
            "Ally", "Position", "Knowledge", "Preparation",
        ]
        options = [
            discord.SelectOption(label=n, value=n) for n in common_names
        ]

        view = AssetNameSelectView(
            self.campaign_id, self.actor_id, player_id, is_scene
        )
        view.add_name_select(options)
        await interaction.response.edit_message(
            content="Selecione um nome para o asset ou use /asset add para nome customizado.",
            view=view,
        )


class AssetNameSelectView(CortexView):
    """Select asset name."""

    def __init__(
        self,
        campaign_id: int,
        actor_id: str,
        player_id: int | None,
        is_scene: bool,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id
        self.is_scene = is_scene

    def add_name_select(self, options: list[discord.SelectOption]) -> None:
        select = discord.ui.Select(
            placeholder="Nome do asset",
            options=options,
            custom_id=f"ephemeral:asset_name_sel:{uuid.uuid4().hex[:8]}",
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction) -> None:
        name = interaction.data["values"][0]
        view = AssetDieSelectView(
            self.campaign_id, self.actor_id, self.player_id, self.is_scene, name
        )

        async def on_die(interaction: discord.Interaction, die_size: int) -> None:
            await view._on_die_selected(interaction, die_size)

        add_die_buttons(view, on_die)
        await interaction.response.edit_message(
            content=f"Asset: {name}. Selecione o dado.", view=view
        )


class AssetDieSelectView(CortexView):
    """Select die for asset, then execute."""

    def __init__(
        self,
        campaign_id: int,
        actor_id: str,
        player_id: int | None,
        is_scene: bool,
        name: str,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id
        self.is_scene = is_scene
        self.name = name

    async def _on_die_selected(
        self, interaction: discord.Interaction, die_size: int
    ) -> None:
        db = interaction.client.db

        scene = await db.get_active_scene(self.campaign_id)
        scene_id = scene["id"] if scene else None

        sm = StateManager(db)
        if self.is_scene:
            result = await sm.add_asset(
                self.campaign_id,
                self.actor_id,
                self.name,
                die_size,
                player_id=None,
                scene_id=scene_id,
                duration="scene",
            )
            msg = format_action_confirm(
                "Asset de cena criado",
                f"{self.name} {die_label(die_size)}, duracao scene.",
            )
        else:
            result = await sm.add_asset(
                self.campaign_id,
                self.actor_id,
                self.name,
                die_size,
                player_id=self.player_id,
                scene_id=scene_id,
                duration="scene",
            )
            msg = format_action_confirm(
                "Asset adicionado",
                f"{self.name} {die_label(die_size)}.",
            )

        view = PostAssetView(self.campaign_id)
        await interaction.response.edit_message(content=msg, view=None)
        await interaction.followup.send(msg, view=view)


# ---------------------------------------------------------------------------
# Complication Add chain
# ---------------------------------------------------------------------------


class ComplicationAddStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:comp_add_start:(?P<campaign_id>\d+)",
):
    """Button to start complication add chain."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Complication Add",
                style=discord.ButtonStyle.danger,
                custom_id=make_custom_id("comp_add_start", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        player = await db.get_player(self.campaign_id, str(interaction.user.id))
        if player is None:
            await interaction.response.send_message(
                "Voce nao esta registrado nesta campanha.", ephemeral=True
            )
            return

        players = await db.get_players(self.campaign_id)

        view = CompTargetSelectView(
            self.campaign_id, str(interaction.user.id), player
        )

        async def on_target(interaction: discord.Interaction, value: str) -> None:
            await view._on_target_selected(interaction, value)

        add_player_options(
            view,
            players,
            on_target,
            extra_buttons=[("Complicacao de Cena", "scene")],
        )
        await interaction.response.send_message(
            "Quem recebe a complication?", view=view, ephemeral=True
        )


class CompTargetSelectView(CortexView):
    """Select target for complication add."""

    def __init__(self, campaign_id: int, actor_id: str, actor: dict) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.actor = actor

    async def _on_target_selected(
        self, interaction: discord.Interaction, val: str
    ) -> None:
        is_scene = val == "scene"
        player_id = None if is_scene else int(val)

        if is_scene:
            from cortex_bot.utils import has_gm_permission

            if not has_gm_permission(self.actor):
                await interaction.response.edit_message(
                    content="Apenas o GM pode criar complications de cena.",
                    view=None,
                )
                return

        common_names = [
            "Wounded", "Confused", "Afraid", "Trapped",
            "Exposed", "Exhausted", "Distracted", "Outnumbered",
        ]
        options = [
            discord.SelectOption(label=n, value=n) for n in common_names
        ]
        view = CompNameSelectView(
            self.campaign_id, self.actor_id, player_id, is_scene
        )
        view.add_name_select(options)
        await interaction.response.edit_message(
            content="Selecione um nome para a complication ou use /complication add para nome customizado.",
            view=view,
        )


class CompNameSelectView(CortexView):
    """Select complication name."""

    def __init__(
        self,
        campaign_id: int,
        actor_id: str,
        player_id: int | None,
        is_scene: bool,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id
        self.is_scene = is_scene

    def add_name_select(self, options: list[discord.SelectOption]) -> None:
        select = discord.ui.Select(
            placeholder="Nome da complication",
            options=options,
            custom_id=f"ephemeral:comp_name_sel:{uuid.uuid4().hex[:8]}",
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction) -> None:
        name = interaction.data["values"][0]
        view = CompDieSelectView(
            self.campaign_id, self.actor_id, self.player_id, self.is_scene, name
        )

        async def on_die(interaction: discord.Interaction, die_size: int) -> None:
            await view._on_die_selected(interaction, die_size)

        add_die_buttons(view, on_die)
        await interaction.response.edit_message(
            content=f"Complication: {name}. Selecione o dado.", view=view
        )


class CompDieSelectView(CortexView):
    """Select die for complication, then execute."""

    def __init__(
        self,
        campaign_id: int,
        actor_id: str,
        player_id: int | None,
        is_scene: bool,
        name: str,
    ) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id
        self.player_id = player_id
        self.is_scene = is_scene
        self.name = name

    async def _on_die_selected(
        self, interaction: discord.Interaction, die_size: int
    ) -> None:
        db = interaction.client.db

        scene = await db.get_active_scene(self.campaign_id)
        scene_id = scene["id"] if scene else None

        sm = StateManager(db)
        scope = "scene" if self.is_scene else "session"
        player_name = None
        if self.player_id:
            async with db.connect() as conn:
                cursor = await conn.execute(
                    "SELECT name FROM players WHERE id = ?", (self.player_id,)
                )
                row = await cursor.fetchone()
                player_name = row["name"] if row else None

        result = await sm.add_complication(
            self.campaign_id,
            self.actor_id,
            self.name,
            die_size,
            player_id=self.player_id,
            scene_id=scene_id,
            scope=scope,
            player_name=player_name,
        )

        if self.is_scene:
            msg = format_action_confirm(
                "Complication de cena criada",
                f"{self.name} {die_label(die_size)}.",
            )
        else:
            msg = format_action_confirm(
                "Complication adicionada",
                f"{self.name} {die_label(die_size)}.",
            )

        view = PostComplicationView(self.campaign_id)
        await interaction.response.edit_message(content=msg, view=None)
        await interaction.followup.send(msg, view=view)


# ---------------------------------------------------------------------------
# Post-action views
# ---------------------------------------------------------------------------


class PostStressView(CortexView):
    """View after stress action: Stress Add + Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton, CampaignInfoButton

        self.add_item(StressAddStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))
        self.add_item(CampaignInfoButton(campaign_id))


class PostAssetView(CortexView):
    """View after asset action: Asset Add + Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton

        self.add_item(AssetAddStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))


class PostComplicationView(CortexView):
    """View after complication action: Complication Add + Undo."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import UndoButton

        self.add_item(ComplicationAddStartButton(campaign_id))
        self.add_item(UndoButton(campaign_id))
