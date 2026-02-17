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
    "add_asset": "Asset '{name}' {die_label} added to {player}",
    "remove_asset": "Asset '{name}' removed from {player}",
    "step_up_asset": "Asset '{name}' stepped up ({from_label} to {to_label})",
    "step_down_asset": "Asset '{name}' stepped down ({from_label} to {to_label})",
    "step_down_asset_eliminated": "Asset '{name}' eliminated (was {was_label})",
    "add_stress": "Stress {type} {die_label} added to {player}",
    "replace_stress": "Stress {type} replaced ({from_label} to {to_label}) on {player}",
    "step_up_stress": "Stress {type} stepped up ({from_label} to {to_label}) on {player}",
    "stressed_out": "Stressed out: {player} on {type}",
    "step_down_stress": "Stress {type} stepped down ({from_label} to {to_label}) on {player}",
    "step_down_stress_eliminated": "Stress {type} eliminated from {player} (was {was_label})",
    "remove_stress": "Stress {type} removed from {player}",
    "add_complication": "Complication '{name}' {die_label} added",
    "remove_complication": "Complication '{name}' removed",
    "step_up_complication": "Complication '{name}' stepped up ({from_label} to {to_label})",
    "step_down_complication": "Complication '{name}' stepped down ({from_label} to {to_label})",
    "step_down_complication_eliminated": "Complication '{name}' eliminated (was {was_label})",
    "update_pp": "{player} PP: {from} to {to}",
    "update_xp": "{player} XP: {from} to {to}",
    "doom_add": "Doom Pool: {die_label} added",
    "doom_remove": "Doom Pool: {die_label} removed",
    "doom_stepup": "Doom Pool: stepped up ({from_label} to {to_label})",
    "doom_stepdown": "Doom Pool: stepped down ({from_label} to {to_label})",
    "doom_stepdown_eliminated": "Doom Pool: {was_label} eliminated",
    "doom_spend": "Doom Pool: {die_label} spent",
    "bank_hero_die": "Hero die {die_label} banked by {player}",
    "use_hero_die": "Hero die {die_label} used by {player}",
    "add_trauma": "Trauma {type} {die_label} added to {player}",
    "add_trauma_from_stress_out": "Trauma {type} {die_label} created (stress out) for {player}",
    "step_up_trauma": "Trauma {type} stepped up ({from_label} to {to_label}) on {player}",
    "step_up_trauma_from_stress_out": "Trauma {type} stepped up ({from_label} to {to_label}) on {player}",
    "replace_trauma": "Trauma {type} replaced ({from_label} to {to_label}) on {player}",
    "step_down_trauma": "Trauma {type} stepped down ({from_label} to {to_label}) on {player}",
    "step_down_trauma_eliminated": "Trauma {type} eliminated from {player} (was {was_label})",
    "remove_trauma": "Trauma {type} removed from {player}",
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

    @app_commands.command(name="undo", description="Undo the last action.")
    async def undo(self, interaction: Interaction) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "No active campaign in this channel. Use /campaign setup to create one."
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
            await interaction.response.send_message("Nothing to undo.")
            return

        state_manager = StateManager(self.db)
        await state_manager.execute_undo(action["inverse_data"])
        await self.db.mark_action_undone(action["id"])

        msg = _format_undo_message(action["action_type"], action["action_data"])
        from cortex_bot.views.common import PostUndoView

        view = PostUndoView(campaign_id)
        await interaction.response.send_message(f"Undone: {msg}", view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UndoCog(bot))
