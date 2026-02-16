"""Menu cog: /menu command for contextual action panel."""

import discord
from discord import app_commands
from discord.ext import commands

from cortex_bot.views.base import CortexView


class MenuView(CortexView):
    """Contextual menu view with action buttons based on campaign state."""

    def __init__(
        self,
        campaign_id: int,
        has_active_scene: bool,
        doom_enabled: bool,
    ) -> None:
        super().__init__()

        if has_active_scene:
            from cortex_bot.views.rolling_views import RollStartButton
            from cortex_bot.views.state_views import (
                StressAddStartButton,
                AssetAddStartButton,
                ComplicationAddStartButton,
                PPStartButton,
                XPStartButton,
            )
            from cortex_bot.views.common import UndoButton, CampaignInfoButton

            self.add_item(RollStartButton(campaign_id))
            self.add_item(StressAddStartButton(campaign_id))
            self.add_item(AssetAddStartButton(campaign_id))
            self.add_item(ComplicationAddStartButton(campaign_id))
            self.add_item(PPStartButton(campaign_id))
            self.add_item(XPStartButton(campaign_id))
            self.add_item(UndoButton(campaign_id))
            self.add_item(CampaignInfoButton(campaign_id))

            if doom_enabled:
                from cortex_bot.views.doom_views import DoomAddStartButton

                self.add_item(DoomAddStartButton(campaign_id))
        else:
            from cortex_bot.views.scene_views import SceneStartButton
            from cortex_bot.views.common import CampaignInfoButton

            self.add_item(SceneStartButton(campaign_id))
            self.add_item(CampaignInfoButton(campaign_id))


class MenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="menu", description="Painel de acoes da campanha")
    @app_commands.checks.cooldown(1, 10.0)
    async def menu(self, interaction: discord.Interaction) -> None:
        db = self.bot.db
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await db.get_campaign_by_channel(server_id, channel_id)

        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal.", ephemeral=True
            )
            return

        scene = await db.get_active_scene(campaign["id"])
        has_active_scene = scene is not None
        config = campaign.get("config", {})
        doom_enabled = config.get("doom_pool", False)

        view = MenuView(
            campaign["id"],
            has_active_scene=has_active_scene,
            doom_enabled=doom_enabled,
        )

        if has_active_scene:
            text = "Painel de acoes. Use os botoes abaixo."
        else:
            text = "Nenhuma cena ativa. Inicie uma cena para acessar mais acoes."

        await interaction.response.send_message(text, view=view)

    @menu.error
    async def menu_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Cooldown ativo. Tente novamente em {error.retry_after:.0f} segundos.",
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MenuCog(bot))
