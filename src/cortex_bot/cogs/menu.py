"""Menu command: recoverable action panel."""

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.views.base import CortexView


class MenuView(CortexView):
    """Contextual action panel based on campaign state."""

    def __init__(self, campaign_id: int, has_scene: bool, doom_enabled: bool) -> None:
        super().__init__()
        if has_scene:
            from cortex_bot.views.rolling_views import RollStartButton
            from cortex_bot.views.state_views import (
                StressAddStartButton,
                AssetAddStartButton,
                ComplicationAddStartButton,
            )
            from cortex_bot.views.common import UndoButton, CampaignInfoButton

            self.add_item(RollStartButton(campaign_id))
            self.add_item(StressAddStartButton(campaign_id))
            self.add_item(AssetAddStartButton(campaign_id))
            self.add_item(ComplicationAddStartButton(campaign_id))
            self.add_item(UndoButton(campaign_id))
            self.add_item(CampaignInfoButton(campaign_id))
            if doom_enabled:
                from cortex_bot.views.doom_views import DoomAddStartButton, DoomRemoveButton, DoomRollButton
                self.add_item(DoomAddStartButton(campaign_id))
                self.add_item(DoomRemoveButton(campaign_id))
                self.add_item(DoomRollButton(campaign_id))
        else:
            from cortex_bot.views.scene_views import SceneStartButton
            from cortex_bot.views.common import CampaignInfoButton

            self.add_item(SceneStartButton(campaign_id))
            self.add_item(CampaignInfoButton(campaign_id))


class MenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def db(self):
        return self.bot.db

    @app_commands.command(
        name="menu",
        description="Exibir painel de acoes contextuais.",
    )
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def menu(self, interaction: Interaction) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)

        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
            )
            return

        config = campaign["config"]
        scene = await self.db.get_active_scene(campaign["id"])
        has_scene = scene is not None
        doom_enabled = config.get("doom_pool", False)

        scene_label = scene["name"] or "sem nome" if scene else None
        if has_scene:
            text = f"Painel de acoes. Cena ativa: {scene_label}. Use os botoes abaixo ou digite / para slash commands."
        else:
            text = "Painel de acoes. Nenhuma cena ativa. Use os botoes abaixo ou digite / para slash commands."

        view = MenuView(campaign["id"], has_scene, doom_enabled)
        await interaction.response.send_message(text, view=view)

    @menu.error
    async def menu_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Aguarde {error.retry_after:.0f} segundos para usar /menu novamente.",
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MenuCog(bot))
