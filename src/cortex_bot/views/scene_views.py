"""Scene-related views and buttons."""

import re

import discord

from cortex_bot.views.base import CortexView, make_custom_id, check_gm_permission


class SceneStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:scene_start:(?P<campaign_id>\d+)",
):
    """Persistent button to start a new scene."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Scene Start",
                style=discord.ButtonStyle.primary,
                custom_id=make_custom_id("scene_start", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match,
    ) -> "SceneStartButton":
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        active = await db.get_active_scene(self.campaign_id)
        if active is not None:
            label = active["name"] or "sem nome"
            await interaction.response.send_message(
                f"Ja existe uma cena ativa: {label}. Encerre-a antes de iniciar outra.",
                ephemeral=True,
            )
            return

        async with db.connect() as conn:
            await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, 1)",
                (self.campaign_id, None),
            )
            await conn.commit()

        campaign = await db.get_campaign_by_id(self.campaign_id)
        doom_enabled = campaign["config"].get("doom_pool", False) if campaign else False

        guide = (
            "\n"
            "Comandos de jogo: /roll para rolar, /asset add para criar assets, "
            "/campaign info para ver estado."
        )
        if doom_enabled:
            guide += " GM: /stress add, /complication add, /doom."
        else:
            guide += " GM: /stress add, /complication add."

        view = PostSceneStartView(self.campaign_id, doom_enabled=doom_enabled)
        await interaction.response.send_message(
            f"Cena iniciada: sem nome.{guide}", view=view
        )


class PostSetupView(CortexView):
    """View shown after campaign setup: Scene Start + Menu."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import MenuButton

        self.add_item(SceneStartButton(campaign_id))
        self.add_item(MenuButton(campaign_id))


class PostSceneStartView(CortexView):
    """View after scene start: Roll, Stress Add, Asset Add, Complication Add, Doom Add (conditional), Menu."""

    def __init__(self, campaign_id: int, doom_enabled: bool = False) -> None:
        super().__init__()
        from cortex_bot.views.rolling_views import RollStartButton
        from cortex_bot.views.state_views import (
            StressAddStartButton,
            AssetAddStartButton,
            ComplicationAddStartButton,
        )
        from cortex_bot.views.doom_views import DoomAddStartButton
        from cortex_bot.views.common import MenuButton

        self.add_item(RollStartButton(campaign_id))
        self.add_item(StressAddStartButton(campaign_id))
        self.add_item(AssetAddStartButton(campaign_id))
        self.add_item(ComplicationAddStartButton(campaign_id))
        if doom_enabled:
            self.add_item(DoomAddStartButton(campaign_id))
        self.add_item(MenuButton(campaign_id))


class PostSceneEndView(CortexView):
    """View after scene end: Scene Start, Campaign Info, Menu."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import CampaignInfoButton, MenuButton

        self.add_item(SceneStartButton(campaign_id))
        self.add_item(CampaignInfoButton(campaign_id))
        self.add_item(MenuButton(campaign_id))
