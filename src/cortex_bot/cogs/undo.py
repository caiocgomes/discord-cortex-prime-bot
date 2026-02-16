"""Undo command for reversing the last logged action."""

import logging

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.models.dice import die_label
from cortex_bot.services.state_manager import StateManager
from cortex_bot.utils import has_gm_permission

log = logging.getLogger(__name__)

ACTION_LABELS = {
    "add_asset": "Asset '{name}' {die_label} adicionado para {player}",
    "remove_asset": "Asset '{name}' removido de {player}",
    "step_up_asset": "Step up de asset '{name}' ({from_label} para {to_label})",
    "step_down_asset": "Step down de asset '{name}' ({from_label} para {to_label})",
    "step_down_asset_eliminated": "Asset '{name}' eliminado (era {was_label})",
    "add_stress": "Stress {type} {die_label} adicionado a {player}",
    "replace_stress": "Stress {type} substituido ({from_label} para {to_label}) em {player}",
    "step_up_stress": "Step up de stress {type} ({from_label} para {to_label}) em {player}",
    "stressed_out": "Stressed out: {player} em {type}",
    "step_down_stress": "Step down de stress {type} ({from_label} para {to_label}) em {player}",
    "step_down_stress_eliminated": "Stress {type} eliminado de {player} (era {was_label})",
    "remove_stress": "Stress {type} removido de {player}",
    "add_complication": "Complication '{name}' {die_label} adicionada",
    "remove_complication": "Complication '{name}' removida",
    "step_up_complication": "Step up de complication '{name}' ({from_label} para {to_label})",
    "step_down_complication": "Step down de complication '{name}' ({from_label} para {to_label})",
    "step_down_complication_eliminated": "Complication '{name}' eliminada (era {was_label})",
    "update_pp": "PP de {player}: {from} para {to}",
    "update_xp": "XP de {player}: {from} para {to}",
    "doom_add": "Doom Pool: {die_label} adicionado",
    "doom_remove": "Doom Pool: {die_label} removido",
    "doom_stepup": "Doom Pool: step up ({from_label} para {to_label})",
    "doom_stepdown": "Doom Pool: step down ({from_label} para {to_label})",
    "doom_stepdown_eliminated": "Doom Pool: {was_label} eliminado",
    "doom_spend": "Doom Pool: {die_label} gasto",
    "bank_hero_die": "Hero die {die_label} bancado por {player}",
    "use_hero_die": "Hero die {die_label} usado por {player}",
    "add_trauma": "Trauma {type} {die_label} adicionado a {player}",
    "add_trauma_from_stress_out": "Trauma {type} {die_label} criado (stress out) para {player}",
    "step_up_trauma": "Step up de trauma {type} ({from_label} para {to_label}) em {player}",
    "step_up_trauma_from_stress_out": "Step up de trauma {type} ({from_label} para {to_label}) em {player}",
    "replace_trauma": "Trauma {type} substituido ({from_label} para {to_label}) em {player}",
    "step_down_trauma": "Step down de trauma {type} ({from_label} para {to_label}) em {player}",
    "step_down_trauma_eliminated": "Trauma {type} eliminado de {player} (era {was_label})",
    "remove_trauma": "Trauma {type} removido de {player}",
}


def _format_undo_message(action_type: str, action_data: dict) -> str:
    """Build a human-readable undo message from action type and data."""
    template = ACTION_LABELS.get(action_type)
    if template is None:
        parts = [f"{k}={v}" for k, v in action_data.items() if k != "id"]
        return f"{action_type} - {', '.join(parts)}" if parts else action_type

    fmt = {}
    for key, value in action_data.items():
        fmt[key] = value
    if "die_size" in action_data:
        fmt["die_label"] = die_label(action_data["die_size"])
    if "from" in action_data:
        fmt["from_label"] = die_label(action_data["from"])
    if "to" in action_data:
        fmt["to_label"] = die_label(action_data["to"])
    if "was" in action_data:
        fmt["was_label"] = die_label(action_data["was"])

    try:
        return template.format(**fmt)
    except (KeyError, IndexError):
        parts = [f"{k}={v}" for k, v in action_data.items() if k != "id"]
        return f"{action_type} - {', '.join(parts)}" if parts else action_type


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
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
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

        msg = _format_undo_message(action["action_type"], action["action_data"])
        from cortex_bot.views.common import PostUndoView

        view = PostUndoView(campaign_id)
        await interaction.response.send_message(f"Desfeito: {msg}", view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UndoCog(bot))
