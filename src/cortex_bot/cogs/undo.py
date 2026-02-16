"""Undo command for reversing the last logged action."""

import logging

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.services.state_manager import StateManager
from cortex_bot.utils import has_gm_permission

log = logging.getLogger(__name__)


class UndoCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def db(self):
        return self.bot.db

    @app_commands.command(name="undo", description="Desfazer a ultima acao registrada.")
    async def undo(self, interaction: Interaction) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha registrada neste canal."
            )
            return

        campaign_id = campaign["id"]
        user_id = str(interaction.user.id)
        player = await self.db.get_player(campaign_id, user_id)

        can_undo_all = player is not None and has_gm_permission(player)

        if can_undo_all:
            action = await self.db.get_last_undoable_action(campaign_id)
        else:
            action = await self.db.get_last_undoable_action(
                campaign_id, actor_discord_id=user_id
            )

        if action is None:
            await interaction.response.send_message("Nada para desfazer.")
            return

        state_manager = StateManager(self.db)
        await state_manager.execute_undo(action["inverse_data"])
        await self.db.mark_action_undone(action["id"])

        action_type = action["action_type"]
        action_data = action["action_data"]

        details_parts: list[str] = []
        for key, value in action_data.items():
            if key == "id":
                continue
            details_parts.append(f"{key}={value}")
        details = ", ".join(details_parts) if details_parts else ""

        await interaction.response.send_message(
            f"Desfeito: {action_type} - {details}"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UndoCog(bot))
