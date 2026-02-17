"""Shared DynamicItem buttons: Undo and Campaign Info."""

import re

import discord

from cortex_bot.views.base import (
    CortexView,
    make_custom_id,
    check_gm_permission,
    get_campaign_from_channel,
)
from cortex_bot.services.state_manager import StateManager
from cortex_bot.utils import has_gm_permission


class UndoButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:undo:(?P<campaign_id>\d+)",
):
    """Persistent Undo button that executes undo directly."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Undo",
                style=discord.ButtonStyle.secondary,
                custom_id=make_custom_id("undo", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match,
    ) -> "UndoButton":
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        user_id = str(interaction.user.id)
        player = await db.get_player(self.campaign_id, user_id)

        can_undo_all = player is not None and has_gm_permission(player)

        if can_undo_all:
            action = await db.get_last_undoable_action(self.campaign_id)
        else:
            action = await db.get_last_undoable_action(
                self.campaign_id, actor_discord_id=user_id
            )

        if action is None:
            await interaction.response.send_message(
                "Nada para desfazer.", ephemeral=True
            )
            return

        state_manager = StateManager(db)
        await state_manager.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])

        from cortex_bot.cogs.undo import _format_undo_message

        msg = _format_undo_message(action["action_type"], action["action_data"])
        view = PostUndoView(self.campaign_id)
        await interaction.response.send_message(f"Desfeito: {msg}", view=view)


class CampaignInfoButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:campaign_info:(?P<campaign_id>\d+)",
):
    """Persistent Campaign Info button."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Campaign Info",
                style=discord.ButtonStyle.secondary,
                custom_id=make_custom_id("campaign_info", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match,
    ) -> "CampaignInfoButton":
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        campaign = await db.get_campaign_by_id(self.campaign_id)
        if campaign is None:
            await interaction.response.send_message(
                "Campanha nao encontrada.", ephemeral=True
            )
            return

        from cortex_bot.services.formatter import format_campaign_info

        config = campaign["config"]
        players = await db.get_players(self.campaign_id)
        scene = await db.get_active_scene(self.campaign_id)

        player_states: dict[int, dict] = {}
        for p in players:
            pid = p["id"]
            state: dict = {}
            state["stress"] = await db.get_player_stress(self.campaign_id, pid)
            state["assets"] = await db.get_player_assets(self.campaign_id, pid)
            state["complications"] = await db.get_player_complications(
                self.campaign_id, pid
            )
            if config.get("trauma"):
                state["trauma"] = await db.get_player_trauma(self.campaign_id, pid)
            if config.get("hero_dice"):
                state["hero_dice"] = await db.get_hero_dice(self.campaign_id, pid)
            player_states[pid] = state

        doom_pool = None
        if config.get("doom_pool"):
            doom_pool = await db.get_doom_pool(self.campaign_id)

        scene_assets = None
        scene_complications = None
        crisis_pools = None
        if scene is not None:
            scene_assets = await db.get_scene_assets(scene["id"])
            scene_complications = await db.get_scene_complications(scene["id"])
            crisis_pools = await db.get_crisis_pools(scene["id"])

        text = format_campaign_info(
            campaign=campaign,
            players=players,
            player_states=player_states,
            scene=scene,
            doom_pool=doom_pool,
            scene_assets=scene_assets,
            scene_complications=scene_complications,
            crisis_pools=crisis_pools,
        )
        view = PostInfoView(self.campaign_id, has_active_scene=scene is not None)
        await interaction.response.send_message(text, view=view)


class MenuButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:menu:(?P<campaign_id>\d+)",
):
    """Persistent Menu button that sends contextual menu as ephemeral."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Menu",
                style=discord.ButtonStyle.secondary,
                custom_id=make_custom_id("menu", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match,
    ) -> "MenuButton":
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        db = interaction.client.db
        campaign = await db.get_campaign_by_id(self.campaign_id)
        if campaign is None:
            await interaction.response.send_message(
                "Campanha nao encontrada.", ephemeral=True
            )
            return

        scene = await db.get_active_scene(self.campaign_id)
        has_active_scene = scene is not None
        config = campaign.get("config", {})
        doom_enabled = config.get("doom_pool", False)

        from cortex_bot.cogs.menu import MenuView

        view = MenuView(
            self.campaign_id,
            has_active_scene=has_active_scene,
            doom_enabled=doom_enabled,
        )

        if has_active_scene:
            text = "Painel de acoes. Use os botoes abaixo."
        else:
            text = "Nenhuma cena ativa. Inicie uma cena para acessar mais acoes."

        await interaction.response.send_message(text, view=view, ephemeral=True)


class MenuOnlyView(CortexView):
    """Minimal view with just a Menu button, for messages without a specific post-action view."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        self.add_item(MenuButton(campaign_id))


class PostUndoView(CortexView):
    """View shown after an undo action: Undo (another) + Campaign Info + Menu."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        self.add_item(UndoButton(campaign_id))
        self.add_item(CampaignInfoButton(campaign_id))
        self.add_item(MenuButton(campaign_id))


class PostInfoView(CortexView):
    """View shown after campaign/scene info.

    Shows Roll if scene active, Scene Start if not. Always includes Menu.
    """

    def __init__(self, campaign_id: int, has_active_scene: bool = False) -> None:
        super().__init__()
        if has_active_scene:
            from cortex_bot.views.rolling_views import RollStartButton

            self.add_item(RollStartButton(campaign_id))
        else:
            from cortex_bot.views.scene_views import SceneStartButton

            self.add_item(SceneStartButton(campaign_id))
        self.add_item(MenuButton(campaign_id))
