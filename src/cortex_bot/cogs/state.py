"""State tracking commands: assets, stress, trauma, complications, PP, XP, hero dice."""

import logging
from typing import Optional

import discord
from discord import app_commands, Interaction, Member
from discord.ext import commands

from cortex_bot.models.dice import parse_single_die, die_label, is_valid_die, step_up, step_down
from cortex_bot.services.state_manager import StateManager
from cortex_bot.services.formatter import format_action_confirm
from cortex_bot.utils import has_gm_permission, NO_CAMPAIGN_MSG
from cortex_bot.views.common import MenuOnlyView

log = logging.getLogger(__name__)

DIE_CHOICES = [
    app_commands.Choice(name="d4", value="d4"),
    app_commands.Choice(name="d6", value="d6"),
    app_commands.Choice(name="d8", value="d8"),
    app_commands.Choice(name="d10", value="d10"),
    app_commands.Choice(name="d12", value="d12"),
]

DURATION_CHOICES = [
    app_commands.Choice(name="scene", value="scene"),
    app_commands.Choice(name="session", value="session"),
]


async def _get_campaign(interaction: Interaction) -> dict | None:
    db = interaction.client.db
    campaign = await db.get_campaign_by_channel(
        str(interaction.guild_id), str(interaction.channel_id)
    )
    if campaign is None:
        await interaction.response.send_message(NO_CAMPAIGN_MSG)
    return campaign


async def _get_player(interaction: Interaction, campaign_id: int) -> dict | None:
    db = interaction.client.db
    player = await db.get_player(campaign_id, str(interaction.user.id))
    if player is None:
        await interaction.response.send_message(
            "You are not registered in this campaign. Ask the GM to add you via /campaign setup."
        )
    return player


async def _resolve_target_player(
    interaction: Interaction,
    campaign_id: int,
    actor: dict,
    member: Optional[Member],
    require_gm_for_others: bool = True,
) -> dict | None:
    """Resolve the target player. If member is None, targets self.

    When require_gm_for_others is True, only the GM can target other players.
    Returns the target player dict, or None (with error already sent).
    """
    db = interaction.client.db
    if member is None or member.id == interaction.user.id:
        return actor

    if require_gm_for_others and not has_gm_permission(actor):
        await interaction.response.send_message(
            "Only the GM can execute this command on other players."
        )
        return None

    target = await db.get_player(campaign_id, str(member.id))
    if target is None:
        await interaction.response.send_message(
            f"{member.display_name} is not registered in this campaign. Ask the GM to add them via /campaign setup."
        )
        return None
    return target


async def _find_asset_by_name(
    db, campaign_id: int, player_id: int | None, name: str
) -> dict | None:
    """Find an asset by name (case-insensitive) for a player or scene."""
    async with db.connect() as conn:
        if player_id is not None:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE campaign_id = ? AND player_id = ? AND LOWER(name) = LOWER(?)",
                (campaign_id, player_id, name),
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE campaign_id = ? AND player_id IS NULL AND LOWER(name) = LOWER(?)",
                (campaign_id, name),
            )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def _find_complication_by_name(
    db, campaign_id: int, player_id: int | None, name: str
) -> dict | None:
    async with db.connect() as conn:
        if player_id is not None:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE campaign_id = ? AND player_id = ? AND LOWER(name) = LOWER(?)",
                (campaign_id, player_id, name),
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE campaign_id = ? AND player_id IS NULL AND LOWER(name) = LOWER(?)",
                (campaign_id, name),
            )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def _find_stress_type_by_name(db, campaign_id: int, name: str) -> dict | None:
    async with db.connect() as conn:
        cursor = await conn.execute(
            "SELECT * FROM stress_types WHERE campaign_id = ? AND LOWER(name) = LOWER(?)",
            (campaign_id, name),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


def _player_label(player: dict, is_self: bool) -> str:
    if is_self:
        return "You"
    return player["name"]


# ---------------------------------------------------------------------------
# Autocomplete helpers
# ---------------------------------------------------------------------------

async def _autocomplete_player(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    db = interaction.client.db
    campaign = await db.get_campaign_by_channel(
        str(interaction.guild_id), str(interaction.channel_id)
    )
    if campaign is None:
        return []
    players = await db.get_players(campaign["id"])
    choices = []
    for p in players:
        if current.lower() in p["name"].lower():
            choices.append(app_commands.Choice(name=p["name"], value=p["discord_user_id"]))
        if len(choices) >= 25:
            break
    return choices


async def _autocomplete_asset(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    db = interaction.client.db
    campaign = await db.get_campaign_by_channel(
        str(interaction.guild_id), str(interaction.channel_id)
    )
    if campaign is None:
        return []
    player = await db.get_player(campaign["id"], str(interaction.user.id))
    if player is None:
        return []
    assets = await db.get_player_assets(campaign["id"], player["id"])
    choices = []
    for a in assets:
        label = f"{a['name']} ({die_label(a['die_size'])})"
        if current.lower() in a["name"].lower():
            choices.append(app_commands.Choice(name=label, value=a["name"]))
        if len(choices) >= 25:
            break
    return choices


async def _autocomplete_stress_type(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    db = interaction.client.db
    campaign = await db.get_campaign_by_channel(
        str(interaction.guild_id), str(interaction.channel_id)
    )
    if campaign is None:
        return []
    types = await db.get_stress_types(campaign["id"])
    choices = []
    for t in types:
        if current.lower() in t["name"].lower():
            choices.append(app_commands.Choice(name=t["name"], value=t["name"]))
        if len(choices) >= 25:
            break
    return choices


async def _autocomplete_complication(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    db = interaction.client.db
    campaign = await db.get_campaign_by_channel(
        str(interaction.guild_id), str(interaction.channel_id)
    )
    if campaign is None:
        return []
    player = await db.get_player(campaign["id"], str(interaction.user.id))
    if player is None:
        return []
    comps = await db.get_player_complications(campaign["id"], player["id"])
    choices = []
    for c in comps:
        label = f"{c['name']} ({die_label(c['die_size'])})"
        if current.lower() in c["name"].lower():
            choices.append(app_commands.Choice(name=label, value=c["name"]))
        if len(choices) >= 25:
            break
    return choices


# ---------------------------------------------------------------------------
# Asset group
# ---------------------------------------------------------------------------

class AssetGroup(app_commands.Group):
    """Commands for managing assets."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="asset", description="Manage assets.")
        self.cog = cog

    @app_commands.command(name="add", description="Add an asset.")
    @app_commands.describe(
        name="Asset name",
        die="Die size (e.g. d6, d8)",
        duration="Duration: scene or session",
        player="Asset owner (default: you)",
        scene_asset="Create as a scene asset with no specific owner",
    )
    @app_commands.choices(die=DIE_CHOICES, duration=DURATION_CHOICES)
    async def add(
        self,
        interaction: Interaction,
        name: str,
        die: str,
        duration: str = "scene",
        player: Optional[Member] = None,
        scene_asset: bool = False,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        sm = StateManager(interaction.client.db)
        actor_id = str(interaction.user.id)
        scene = await interaction.client.db.get_active_scene(campaign["id"])
        scene_id = scene["id"] if scene else None

        if scene_asset:
            if not has_gm_permission(actor):
                await interaction.response.send_message(
                    "Only the GM can create scene assets."
                )
                return
            result = await sm.add_asset(
                campaign["id"], actor_id, name, die_size,
                player_id=None, scene_id=scene_id, duration=duration,
            )
            msg = format_action_confirm(
                "Scene asset created",
                f"{name} {die_label(die_size)}, duration {duration}.",
            )
        else:
            target = await _resolve_target_player(
                interaction, campaign["id"], actor, player
            )
            if target is None:
                return
            result = await sm.add_asset(
                campaign["id"], actor_id, name, die_size,
                player_id=target["id"], scene_id=scene_id, duration=duration,
            )
            label = _player_label(target, target["id"] == actor["id"])
            msg = format_action_confirm(
                "Asset added",
                f"{name} {die_label(die_size)} for {label}, duration {duration}.",
            )

        from cortex_bot.views.state_views import PostAssetView

        view = PostAssetView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepup", description="Step up an asset.")
    @app_commands.describe(
        name="Asset name",
        player="Asset owner (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_asset)
    async def stepup(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        asset = await _find_asset_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if asset is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Asset '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_up_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Error processing asset step up.")
            return

        if result.get("error") == "already_max":
            await interaction.response.send_message(
                f"Asset '{result['name']}' is already at d12. Cannot step up."
            )
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Asset stepped up",
            f"{result['name']} from {die_label(result['from'])} to {die_label(result['to'])} ({label}).",
        )
        from cortex_bot.views.state_views import PostAssetView

        view = PostAssetView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepdown", description="Step down an asset.")
    @app_commands.describe(
        name="Asset name",
        player="Asset owner (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_asset)
    async def stepdown(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        asset = await _find_asset_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if asset is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Asset '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_down_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Error processing asset step down.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("eliminated"):
            msg = format_action_confirm(
                "Asset eliminated",
                f"{result['name']} was {die_label(result['was'])}, step down from d4 removes the asset ({label}).",
            )
        else:
            msg = format_action_confirm(
                "Asset stepped down",
                f"{result['name']} from {die_label(result['from'])} to {die_label(result['to'])} ({label}).",
            )
        from cortex_bot.views.state_views import PostAssetView

        view = PostAssetView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="remove", description="Remove an asset.")
    @app_commands.describe(
        name="Asset name",
        player="Asset owner (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_asset)
    async def remove(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        asset = await _find_asset_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if asset is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Asset '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.remove_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Error removing asset.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Asset removed",
            f"{result['name']} {die_label(result['die_size'])} from {label}.",
        )
        from cortex_bot.views.state_views import PostAssetView

        view = PostAssetView(campaign["id"])
        await interaction.response.send_message(msg, view=view)


# ---------------------------------------------------------------------------
# Stress group
# ---------------------------------------------------------------------------

class StressGroup(app_commands.Group):
    """Commands for managing stress."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="stress", description="Manage stress.")
        self.cog = cog

    @app_commands.command(name="add", description="Add stress to a player (GM only).")
    @app_commands.describe(
        player="Player receiving the stress",
        type="Stress type (e.g. Physical, Mental)",
        die="Stress die size (e.g. d6, d8)",
    )
    @app_commands.choices(die=DIE_CHOICES)
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def add(
        self,
        interaction: Interaction,
        player: Member,
        type: str,
        die: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return
        if not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM can add stress to players."
            )
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Stress type '{type}' not found in this campaign. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.add_stress(
            campaign["id"], str(interaction.user.id),
            target["id"], stress_type["id"], die_size,
            player_name=target["name"], type_name=stress_type["name"],
        )

        action = result.get("action")
        if action == "added":
            msg = format_action_confirm(
                "Stress added",
                f"{target['name']} receives {stress_type['name']} {die_label(die_size)}.",
            )
        elif action == "replaced":
            msg = format_action_confirm(
                "Stress replaced",
                f"{target['name']} {stress_type['name']} from {die_label(result['from'])} to {die_label(result['to'])}. "
                f"Incoming die ({die_label(die_size)}) was larger than existing, replaced.",
            )
        elif action == "stepped_up":
            msg = format_action_confirm(
                "Stress stepped up",
                f"{target['name']} {stress_type['name']} from {die_label(result['from'])} to {die_label(result['to'])}. "
                f"Incoming die ({die_label(die_size)}) was equal or smaller, step up applied.",
            )
        elif action == "stressed_out":
            stressed_msg = (
                f"{target['name']} stressed out on {stress_type['name']}. "
                f"Stress was already d12 and received step up."
            )
            if campaign["config"].get("trauma"):
                trauma_result = await _create_trauma_from_stress_out(
                    interaction.client.db, campaign["id"],
                    str(interaction.user.id), target["id"], stress_type["id"],
                    target["name"], stress_type["name"],
                )
                if trauma_result:
                    stressed_msg += (
                        f" Trauma {stress_type['name']} {die_label(trauma_result['die_size'])} created for {target['name']}."
                    )
            msg = format_action_confirm("Stressed out", stressed_msg)
        else:
            msg = f"Stress processed for {target['name']}."

        from cortex_bot.views.state_views import PostStressView

        view = PostStressView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepup", description="Step up a player's stress (GM only).")
    @app_commands.describe(
        player="Player",
        type="Stress type",
    )
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def stepup(
        self,
        interaction: Interaction,
        player: Member,
        type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return
        if not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM can step up stress."
            )
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Stress type '{type}' not found in this campaign. Check the name and try again."
            )
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM stress WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if not existing:
                await interaction.response.send_message(
                    f"{target['name']} has no {stress_type['name']} stress to step up."
                )
                return
            existing = dict(existing)
            new_size = step_up(existing["die_size"])
            if new_size is None:
                stressed_msg = (
                    f"{target['name']} stressed out on {stress_type['name']}. "
                    f"Stress was already d12, cannot step up."
                )
                if campaign["config"].get("trauma"):
                    trauma_result = await _create_trauma_from_stress_out(
                        db, campaign["id"],
                        str(interaction.user.id), target["id"], stress_type["id"],
                        target["name"], stress_type["name"],
                    )
                    if trauma_result:
                        stressed_msg += (
                            f" Trauma {stress_type['name']} {die_label(trauma_result['die_size'])} created."
                        )
                await interaction.response.send_message(
                    format_action_confirm("Stressed out", stressed_msg)
                )
                return

            await conn.execute(
                "UPDATE stress SET die_size = ? WHERE id = ?",
                (new_size, existing["id"]),
            )
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "step_up_stress",
            {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
             "from": existing["die_size"], "to": new_size},
            {"action": "update", "table": "stress", "id": existing["id"],
             "field": "die_size", "value": existing["die_size"]},
        )
        msg = format_action_confirm(
            "Stress stepped up",
            f"{target['name']} {stress_type['name']} from {die_label(existing['die_size'])} to {die_label(new_size)}.",
        )
        from cortex_bot.views.state_views import PostStressView

        view = PostStressView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepdown", description="Step down a player's stress.")
    @app_commands.describe(
        player="Player",
        type="Stress type",
    )
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def stepdown(
        self,
        interaction: Interaction,
        player: Member,
        type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        is_self = target["id"] == actor["id"]
        if not is_self and not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM or the player themselves can step down stress."
            )
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Stress type '{type}' not found in this campaign. Check the name and try again."
            )
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM stress WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if not existing:
                label = _player_label(target, is_self)
                await interaction.response.send_message(
                    f"{label} has no {stress_type['name']} stress to step down."
                )
                return
            existing = dict(existing)
            new_size = step_down(existing["die_size"])

            if new_size is None:
                await conn.execute("DELETE FROM stress WHERE id = ?", (existing["id"],))
                await conn.commit()
                await db.log_action(
                    campaign["id"], str(interaction.user.id), "step_down_stress_eliminated",
                    {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
                     "was": existing["die_size"]},
                    {"action": "insert", "table": "stress",
                     "data": {"campaign_id": campaign["id"], "player_id": target["id"],
                              "stress_type_id": stress_type["id"], "die_size": existing["die_size"]}},
                )
                label = _player_label(target, is_self)
                msg = format_action_confirm(
                    "Stress eliminated",
                    f"{stress_type['name']} for {label} was d4, step down removes the stress.",
                )
                from cortex_bot.views.state_views import PostStressView

                view = PostStressView(campaign["id"])
                await interaction.response.send_message(msg, view=view)
                return

            await conn.execute(
                "UPDATE stress SET die_size = ? WHERE id = ?",
                (new_size, existing["id"]),
            )
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "step_down_stress",
            {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
             "from": existing["die_size"], "to": new_size},
            {"action": "update", "table": "stress", "id": existing["id"],
             "field": "die_size", "value": existing["die_size"]},
        )
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "Stress stepped down",
            f"{label} {stress_type['name']} from {die_label(existing['die_size'])} to {die_label(new_size)}.",
        )
        from cortex_bot.views.state_views import PostStressView

        view = PostStressView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="remove", description="Remove stress from a player.")
    @app_commands.describe(
        player="Player",
        type="Stress type",
    )
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def remove(
        self,
        interaction: Interaction,
        player: Member,
        type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        is_self = target["id"] == actor["id"]
        if not is_self and not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM or the player themselves can remove stress."
            )
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Stress type '{type}' not found in this campaign. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.remove_stress(
            campaign["id"], str(interaction.user.id),
            target["id"], stress_type["id"],
            player_name=target["name"], type_name=stress_type["name"],
        )
        if result is None:
            label = _player_label(target, is_self)
            await interaction.response.send_message(
                f"{label} has no {stress_type['name']} stress to remove."
            )
            return

        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "Stress removed",
            f"{stress_type['name']} {die_label(result['die_size'])} from {label}.",
        )
        from cortex_bot.views.state_views import PostStressView

        view = PostStressView(campaign["id"])
        await interaction.response.send_message(msg, view=view)


# ---------------------------------------------------------------------------
# Trauma helpers and group
# ---------------------------------------------------------------------------

async def _create_trauma_from_stress_out(
    db, campaign_id: int, actor_id: str,
    player_id: int, stress_type_id: int,
    player_name: str, type_name: str,
) -> dict | None:
    """Create a d6 trauma when a player is stressed out. Returns result dict or None."""
    async with db.connect() as conn:
        cursor = await conn.execute(
            "SELECT * FROM trauma WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
            (campaign_id, player_id, stress_type_id),
        )
        existing = await cursor.fetchone()
        if existing:
            existing = dict(existing)
            new_size = step_up(existing["die_size"])
            if new_size is None:
                return {"die_size": 12, "permanent_removal": True, "player": player_name, "type": type_name}
            await conn.execute(
                "UPDATE trauma SET die_size = ? WHERE id = ?",
                (new_size, existing["id"]),
            )
            await conn.commit()
            await db.log_action(
                campaign_id, actor_id, "step_up_trauma_from_stress_out",
                {"id": existing["id"], "player": player_name, "type": type_name,
                 "from": existing["die_size"], "to": new_size},
                {"action": "update", "table": "trauma", "id": existing["id"],
                 "field": "die_size", "value": existing["die_size"]},
            )
            return {"die_size": new_size, "player": player_name, "type": type_name}
        else:
            die_size = 6
            cursor = await conn.execute(
                "INSERT INTO trauma (campaign_id, player_id, stress_type_id, die_size) VALUES (?, ?, ?, ?)",
                (campaign_id, player_id, stress_type_id, die_size),
            )
            trauma_id = cursor.lastrowid
            await conn.commit()
            await db.log_action(
                campaign_id, actor_id, "add_trauma_from_stress_out",
                {"id": trauma_id, "player": player_name, "type": type_name, "die_size": die_size},
                {"action": "delete", "table": "trauma", "id": trauma_id},
            )
            return {"die_size": die_size, "player": player_name, "type": type_name}


class TraumaGroup(app_commands.Group):
    """Commands for managing trauma."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="trauma", description="Manage trauma.")
        self.cog = cog

    async def _check_trauma_enabled(self, interaction: Interaction, campaign: dict) -> bool:
        if not campaign["config"].get("trauma"):
            await interaction.response.send_message(
                "Trauma module is not enabled in this campaign."
            )
            return False
        return True

    @app_commands.command(name="add", description="Add trauma to a player (GM only).")
    @app_commands.describe(
        player="Player receiving the trauma",
        type="Trauma type (same as stress type)",
        die="Trauma die size",
    )
    @app_commands.choices(die=DIE_CHOICES)
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def add(
        self,
        interaction: Interaction,
        player: Member,
        type: str,
        die: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_trauma_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return
        if not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM can add trauma."
            )
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Type '{type}' not found in this campaign. Check the name and try again."
            )
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM trauma WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if existing:
                existing = dict(existing)
                if die_size > existing["die_size"]:
                    old_size = existing["die_size"]
                    await conn.execute(
                        "UPDATE trauma SET die_size = ? WHERE id = ?",
                        (die_size, existing["id"]),
                    )
                    await conn.commit()
                    await db.log_action(
                        campaign["id"], str(interaction.user.id), "replace_trauma",
                        {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
                         "from": old_size, "to": die_size},
                        {"action": "update", "table": "trauma", "id": existing["id"],
                         "field": "die_size", "value": old_size},
                    )
                    msg = format_action_confirm(
                        "Trauma replaced",
                        f"{target['name']} {stress_type['name']} from {die_label(old_size)} to {die_label(die_size)}.",
                    )
                else:
                    new_size = step_up(existing["die_size"])
                    if new_size is None:
                        msg = format_action_confirm(
                            "Permanent removal",
                            f"{target['name']} trauma {stress_type['name']} was already d12 and received step up. "
                            f"Character suffers permanent removal.",
                        )
                        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))
                        return
                    await conn.execute(
                        "UPDATE trauma SET die_size = ? WHERE id = ?",
                        (new_size, existing["id"]),
                    )
                    await conn.commit()
                    await db.log_action(
                        campaign["id"], str(interaction.user.id), "step_up_trauma",
                        {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
                         "from": existing["die_size"], "to": new_size},
                        {"action": "update", "table": "trauma", "id": existing["id"],
                         "field": "die_size", "value": existing["die_size"]},
                    )
                    msg = format_action_confirm(
                        "Trauma stepped up",
                        f"{target['name']} {stress_type['name']} from {die_label(existing['die_size'])} to {die_label(new_size)}. "
                        f"Incoming die ({die_label(die_size)}) was equal or smaller, step up applied.",
                    )
            else:
                cursor = await conn.execute(
                    "INSERT INTO trauma (campaign_id, player_id, stress_type_id, die_size) VALUES (?, ?, ?, ?)",
                    (campaign["id"], target["id"], stress_type["id"], die_size),
                )
                trauma_id = cursor.lastrowid
                await conn.commit()
                await db.log_action(
                    campaign["id"], str(interaction.user.id), "add_trauma",
                    {"id": trauma_id, "player": target["name"], "type": stress_type["name"],
                     "die_size": die_size},
                    {"action": "delete", "table": "trauma", "id": trauma_id},
                )
                msg = format_action_confirm(
                    "Trauma added",
                    f"{target['name']} receives trauma {stress_type['name']} {die_label(die_size)}.",
                )

        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="stepup", description="Step up a player's trauma (GM only).")
    @app_commands.describe(player="Player", type="Trauma type")
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def stepup(
        self, interaction: Interaction, player: Member, type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_trauma_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return
        if not has_gm_permission(actor):
            await interaction.response.send_message("Only the GM can step up trauma.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Type '{type}' not found in this campaign. Check the name and try again.")
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM trauma WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if not existing:
                await interaction.response.send_message(
                    f"{target['name']} has no {stress_type['name']} trauma."
                )
                return
            existing = dict(existing)
            new_size = step_up(existing["die_size"])
            if new_size is None:
                msg = format_action_confirm(
                    "Permanent removal",
                    f"{target['name']} trauma {stress_type['name']} was already d12, step up indicates permanent character removal.",
                )
                await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))
                return

            await conn.execute(
                "UPDATE trauma SET die_size = ? WHERE id = ?",
                (new_size, existing["id"]),
            )
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "step_up_trauma",
            {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
             "from": existing["die_size"], "to": new_size},
            {"action": "update", "table": "trauma", "id": existing["id"],
             "field": "die_size", "value": existing["die_size"]},
        )
        msg = format_action_confirm(
            "Trauma stepped up",
            f"{target['name']} {stress_type['name']} from {die_label(existing['die_size'])} to {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="stepdown", description="Step down a player's trauma.")
    @app_commands.describe(player="Player", type="Trauma type")
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def stepdown(
        self, interaction: Interaction, player: Member, type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_trauma_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        is_self = target["id"] == actor["id"]
        if not is_self and not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM or the player themselves can step down trauma."
            )
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Type '{type}' not found in this campaign. Check the name and try again.")
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM trauma WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if not existing:
                label = _player_label(target, is_self)
                await interaction.response.send_message(
                    f"{label} has no {stress_type['name']} trauma."
                )
                return
            existing = dict(existing)
            new_size = step_down(existing["die_size"])

            if new_size is None:
                await conn.execute("DELETE FROM trauma WHERE id = ?", (existing["id"],))
                await conn.commit()
                await db.log_action(
                    campaign["id"], str(interaction.user.id), "step_down_trauma_eliminated",
                    {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
                     "was": existing["die_size"]},
                    {"action": "insert", "table": "trauma",
                     "data": {"campaign_id": campaign["id"], "player_id": target["id"],
                              "stress_type_id": stress_type["id"], "die_size": existing["die_size"]}},
                )
                label = _player_label(target, is_self)
                msg = format_action_confirm(
                    "Trauma eliminated",
                    f"{stress_type['name']} for {label} was d4, step down removes the trauma.",
                )
                await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))
                return

            await conn.execute(
                "UPDATE trauma SET die_size = ? WHERE id = ?",
                (new_size, existing["id"]),
            )
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "step_down_trauma",
            {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
             "from": existing["die_size"], "to": new_size},
            {"action": "update", "table": "trauma", "id": existing["id"],
             "field": "die_size", "value": existing["die_size"]},
        )
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "Trauma stepped down",
            f"{label} {stress_type['name']} from {die_label(existing['die_size'])} to {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="remove", description="Remove trauma from a player.")
    @app_commands.describe(player="Player", type="Trauma type")
    @app_commands.autocomplete(type=_autocomplete_stress_type)
    async def remove(
        self, interaction: Interaction, player: Member, type: str,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_trauma_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        is_self = target["id"] == actor["id"]
        if not is_self and not has_gm_permission(actor):
            await interaction.response.send_message(
                "Only the GM or the player themselves can remove trauma."
            )
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Type '{type}' not found in this campaign. Check the name and try again.")
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM trauma WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign["id"], target["id"], stress_type["id"]),
            )
            existing = await cursor.fetchone()
            if not existing:
                label = _player_label(target, is_self)
                await interaction.response.send_message(
                    f"{label} has no {stress_type['name']} trauma to remove."
                )
                return
            existing = dict(existing)
            await conn.execute("DELETE FROM trauma WHERE id = ?", (existing["id"],))
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "remove_trauma",
            {"id": existing["id"], "player": target["name"], "type": stress_type["name"],
             "die_size": existing["die_size"]},
            {"action": "insert", "table": "trauma",
             "data": {"campaign_id": campaign["id"], "player_id": target["id"],
                      "stress_type_id": stress_type["id"], "die_size": existing["die_size"]}},
        )
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "Trauma removed",
            f"{stress_type['name']} {die_label(existing['die_size'])} from {label}.",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))


# ---------------------------------------------------------------------------
# Complication group
# ---------------------------------------------------------------------------

class ComplicationGroup(app_commands.Group):
    """Commands for managing complications."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="complication", description="Manage complications.")
        self.cog = cog

    @app_commands.command(name="add", description="Add a complication.")
    @app_commands.describe(
        name="Complication name",
        die="Die size",
        player="Affected player (default: you)",
        scene="Create as a scene complication (removed when scene ends)",
    )
    @app_commands.choices(die=DIE_CHOICES)
    async def add(
        self,
        interaction: Interaction,
        name: str,
        die: str,
        player: Optional[Member] = None,
        scene: bool = False,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        sm = StateManager(interaction.client.db)
        actor_id = str(interaction.user.id)
        active_scene = await interaction.client.db.get_active_scene(campaign["id"])
        scene_id = active_scene["id"] if active_scene else None

        if scene:
            if not has_gm_permission(actor):
                await interaction.response.send_message(
                    "Only the GM can create scene complications."
                )
                return
            result = await sm.add_complication(
                campaign["id"], actor_id, name, die_size,
                player_id=None, scene_id=scene_id, scope="scene",
            )
            msg = format_action_confirm(
                "Scene complication created",
                f"{name} {die_label(die_size)}.",
            )
        else:
            target = await _resolve_target_player(
                interaction, campaign["id"], actor, player
            )
            if target is None:
                return
            scope = "session"
            result = await sm.add_complication(
                campaign["id"], actor_id, name, die_size,
                player_id=target["id"], scene_id=scene_id, scope=scope,
                player_name=target["name"],
            )
            label = _player_label(target, target["id"] == actor["id"])
            msg = format_action_confirm(
                "Complication added",
                f"{name} {die_label(die_size)} for {label}.",
            )

        from cortex_bot.views.state_views import PostComplicationView

        view = PostComplicationView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepup", description="Step up a complication.")
    @app_commands.describe(
        name="Complication name",
        player="Affected player (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_complication)
    async def stepup(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        comp = await _find_complication_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if comp is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Complication '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_up_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Error processing complication step up.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("taken_out"):
            msg = format_action_confirm(
                "Taken out",
                f"Complication '{result['name']}' was already d12, step up means {label} is taken out.",
            )
        else:
            msg = format_action_confirm(
                "Complication stepped up",
                f"{result['name']} from {die_label(result['from'])} to {die_label(result['to'])} ({label}).",
            )
        from cortex_bot.views.state_views import PostComplicationView

        view = PostComplicationView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="stepdown", description="Step down a complication.")
    @app_commands.describe(
        name="Complication name",
        player="Affected player (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_complication)
    async def stepdown(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        comp = await _find_complication_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if comp is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Complication '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_down_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Error processing complication step down.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("eliminated"):
            msg = format_action_confirm(
                "Complication eliminated",
                f"{result['name']} was {die_label(result['was'])}, step down from d4 removes the complication ({label}).",
            )
        else:
            msg = format_action_confirm(
                "Complication stepped down",
                f"{result['name']} from {die_label(result['from'])} to {die_label(result['to'])} ({label}).",
            )
        from cortex_bot.views.state_views import PostComplicationView

        view = PostComplicationView(campaign["id"])
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(name="remove", description="Remove a complication.")
    @app_commands.describe(
        name="Complication name",
        player="Affected player (default: you)",
    )
    @app_commands.autocomplete(name=_autocomplete_complication)
    async def remove(
        self,
        interaction: Interaction,
        name: str,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        comp = await _find_complication_by_name(
            interaction.client.db, campaign["id"], target["id"], name
        )
        if comp is None:
            label = _player_label(target, target["id"] == actor["id"])
            await interaction.response.send_message(
                f"Complication '{name}' not found for {label}. Check the name and try again."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.remove_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Error removing complication.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Complication removed",
            f"{result['name']} {die_label(result['die_size'])} from {label}.",
        )
        from cortex_bot.views.state_views import PostComplicationView

        view = PostComplicationView(campaign["id"])
        await interaction.response.send_message(msg, view=view)


# ---------------------------------------------------------------------------
# PP group
# ---------------------------------------------------------------------------

class PPGroup(app_commands.Group):
    """Commands for managing plot points."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="pp", description="Manage plot points.")
        self.cog = cog

    @app_commands.command(name="add", description="Add plot points.")
    @app_commands.describe(
        amount="Amount of PP to add",
        player="Player (default: you, GM can give to others)",
    )
    async def add(
        self,
        interaction: Interaction,
        amount: int,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive. Use /pp remove to spend PP.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        sm = StateManager(interaction.client.db)
        result = await sm.update_pp(
            campaign["id"], str(interaction.user.id),
            target["id"], amount, player_name=target["name"],
        )

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "PP added",
            f"{label}: {result['from']} to {result['to']} PP (+{amount}).",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="remove", description="Spend plot points.")
    @app_commands.describe(
        amount="Amount of PP to spend",
        player="Player (default: you, GM can remove from others)",
    )
    async def remove(
        self,
        interaction: Interaction,
        amount: int,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive. Use /pp add to earn PP.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        sm = StateManager(interaction.client.db)
        result = await sm.update_pp(
            campaign["id"], str(interaction.user.id),
            target["id"], -amount, player_name=target["name"],
        )

        if result.get("error") == "insufficient":
            is_self = target["id"] == actor["id"]
            label = _player_label(target, is_self)
            await interaction.response.send_message(
                f"{label} only has {result['current']} PP, cannot spend {result['requested']}."
            )
            return

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "PP spent",
            f"{label}: {result['from']} to {result['to']} PP (-{amount}).",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))


# ---------------------------------------------------------------------------
# XP group
# ---------------------------------------------------------------------------

class XPGroup(app_commands.Group):
    """Commands for managing XP."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="xp", description="Manage experience points.")
        self.cog = cog

    @app_commands.command(name="add", description="Add XP.")
    @app_commands.describe(
        amount="Amount of XP to add",
        player="Player (default: you)",
    )
    async def add(
        self,
        interaction: Interaction,
        amount: int,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive. Use /xp remove to remove XP.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        sm = StateManager(interaction.client.db)
        result = await sm.update_xp(
            campaign["id"], str(interaction.user.id),
            target["id"], amount, player_name=target["name"],
        )

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "XP added",
            f"{label}: {result['from']} to {result['to']} XP (+{amount}).",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="remove", description="Remove XP.")
    @app_commands.describe(
        amount="Amount of XP to remove",
        player="Player (default: you)",
    )
    async def remove(
        self,
        interaction: Interaction,
        amount: int,
        player: Optional[Member] = None,
    ) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player
        )
        if target is None:
            return

        sm = StateManager(interaction.client.db)
        result = await sm.update_xp(
            campaign["id"], str(interaction.user.id),
            target["id"], -amount, player_name=target["name"],
        )

        if result.get("error") == "insufficient":
            is_self = target["id"] == actor["id"]
            label = _player_label(target, is_self)
            await interaction.response.send_message(
                f"{label} only has {result['current']} XP, cannot remove {result['requested']}."
            )
            return

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "XP removed",
            f"{label}: {result['from']} to {result['to']} XP (-{amount}).",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))


# ---------------------------------------------------------------------------
# Hero dice group
# ---------------------------------------------------------------------------

class HeroGroup(app_commands.Group):
    """Commands for managing hero dice."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="hero", description="Manage hero dice.")
        self.cog = cog

    async def _check_hero_enabled(self, interaction: Interaction, campaign: dict) -> bool:
        if not campaign["config"].get("hero_dice"):
            await interaction.response.send_message(
                "Hero dice module is not enabled in this campaign."
            )
            return False
        return True

    @app_commands.command(name="bank", description="Bank a hero die.")
    @app_commands.describe(die="Die size to bank")
    @app_commands.choices(die=DIE_CHOICES)
    async def bank(self, interaction: Interaction, die: str) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_hero_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO hero_dice (campaign_id, player_id, die_size) VALUES (?, ?, ?)",
                (campaign["id"], actor["id"], die_size),
            )
            hero_id = cursor.lastrowid
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "bank_hero_die",
            {"id": hero_id, "player": actor["name"], "die_size": die_size},
            {"action": "delete", "table": "hero_dice", "id": hero_id},
        )

        hero_dice = await db.get_hero_dice(campaign["id"], actor["id"])
        bank_strs = [die_label(h["die_size"]) for h in hero_dice]
        msg = format_action_confirm(
            "Hero die banked",
            f"{die_label(die_size)} added to bank.",
            f"Current bank: {', '.join(bank_strs)}.",
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))

    @app_commands.command(name="use", description="Use a hero die from the bank.")
    @app_commands.describe(die="Die size to use")
    @app_commands.choices(die=DIE_CHOICES)
    async def use(self, interaction: Interaction, die: str) -> None:
        campaign = await _get_campaign(interaction)
        if campaign is None:
            return
        if not await self._check_hero_enabled(interaction, campaign):
            return
        actor = await _get_player(interaction, campaign["id"])
        if actor is None:
            return

        try:
            die_size = parse_single_die(die)
        except ValueError as e:
            await interaction.response.send_message(str(e))
            return

        db = interaction.client.db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM hero_dice WHERE campaign_id = ? AND player_id = ? AND die_size = ? LIMIT 1",
                (campaign["id"], actor["id"], die_size),
            )
            hero = await cursor.fetchone()
            if not hero:
                await interaction.response.send_message(
                    f"You don't have a hero die {die_label(die_size)} in the bank."
                )
                return
            hero = dict(hero)
            await conn.execute("DELETE FROM hero_dice WHERE id = ?", (hero["id"],))
            await conn.commit()

        await db.log_action(
            campaign["id"], str(interaction.user.id), "use_hero_die",
            {"id": hero["id"], "player": actor["name"], "die_size": die_size},
            {"action": "insert", "table": "hero_dice",
             "data": {"campaign_id": campaign["id"], "player_id": actor["id"], "die_size": die_size}},
        )

        hero_dice = await db.get_hero_dice(campaign["id"], actor["id"])
        if hero_dice:
            bank_strs = [die_label(h["die_size"]) for h in hero_dice]
            bank_info = f"Remaining bank: {', '.join(bank_strs)}."
        else:
            bank_info = "Bank empty."

        msg = format_action_confirm(
            "Hero die used",
            f"{die_label(die_size)} removed from bank. Roll and add to total.",
            bank_info,
        )
        await interaction.response.send_message(msg, view=MenuOnlyView(campaign["id"]))


# ---------------------------------------------------------------------------
# Main cog
# ---------------------------------------------------------------------------

class StateCog(commands.Cog):
    """State tracking: assets, stress, trauma, complications, PP, XP, hero dice."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.asset_group = AssetGroup(self)
        self.stress_group = StressGroup(self)
        self.trauma_group = TraumaGroup(self)
        self.complication_group = ComplicationGroup(self)
        self.pp_group = PPGroup(self)
        self.xp_group = XPGroup(self)
        self.hero_group = HeroGroup(self)

        self.bot.tree.add_command(self.asset_group)
        self.bot.tree.add_command(self.stress_group)
        self.bot.tree.add_command(self.trauma_group)
        self.bot.tree.add_command(self.complication_group)
        self.bot.tree.add_command(self.pp_group)
        self.bot.tree.add_command(self.xp_group)
        self.bot.tree.add_command(self.hero_group)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command("asset")
        self.bot.tree.remove_command("stress")
        self.bot.tree.remove_command("trauma")
        self.bot.tree.remove_command("complication")
        self.bot.tree.remove_command("pp")
        self.bot.tree.remove_command("xp")
        self.bot.tree.remove_command("hero")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StateCog(bot))
