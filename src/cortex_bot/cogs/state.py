"""State tracking commands: assets, stress, trauma, complications, PP, XP, hero dice."""

import logging
from typing import Optional

import discord
from discord import app_commands, Interaction, Member
from discord.ext import commands

from cortex_bot.models.dice import parse_single_die, die_label, is_valid_die, step_up, step_down
from cortex_bot.services.state_manager import StateManager
from cortex_bot.services.formatter import format_action_confirm
from cortex_bot.utils import has_gm_permission

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
        await interaction.response.send_message(
            "Nenhuma campanha ativa neste canal. Use /setup para criar uma."
        )
    return campaign


async def _get_player(interaction: Interaction, campaign_id: int) -> dict | None:
    db = interaction.client.db
    player = await db.get_player(campaign_id, str(interaction.user.id))
    if player is None:
        await interaction.response.send_message(
            "Voce nao esta registrado nesta campanha."
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
            "Apenas o GM pode executar este comando em outros jogadores."
        )
        return None

    target = await db.get_player(campaign_id, str(member.id))
    if target is None:
        await interaction.response.send_message(
            f"{member.display_name} nao esta registrado nesta campanha."
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
        return "Voce"
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
    """Comandos para gerenciar assets."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="asset", description="Gerenciar assets.")
        self.cog = cog

    @app_commands.command(name="add", description="Adicionar um asset.")
    @app_commands.describe(
        name="Nome do asset",
        die="Tamanho do dado (ex: d6, d8)",
        duration="Duracao: scene ou session",
        player="Jogador dono do asset (default: voce). Omitir para asset de cena.",
        scene_asset="Criar como asset de cena, sem dono especifico",
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
                    "Apenas o GM pode criar assets de cena."
                )
                return
            result = await sm.add_asset(
                campaign["id"], actor_id, name, die_size,
                player_id=None, scene_id=scene_id, duration=duration,
            )
            msg = format_action_confirm(
                "Asset de cena criado",
                f"{name} {die_label(die_size)}, duracao {duration}.",
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
                "Asset adicionado",
                f"{name} {die_label(die_size)} para {label}, duracao {duration}.",
            )

        await interaction.response.send_message(msg)

    @app_commands.command(name="stepup", description="Step up de um asset.")
    @app_commands.describe(
        name="Nome do asset",
        player="Jogador dono do asset (default: voce)",
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
                f"Asset '{name}' nao encontrado para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_up_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Erro ao processar step up do asset.")
            return

        if result.get("error") == "already_max":
            await interaction.response.send_message(
                f"Asset '{result['name']}' ja esta em d12, nao pode fazer step up."
            )
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Asset step up",
            f"{result['name']} de {die_label(result['from'])} para {die_label(result['to'])} ({label}).",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="stepdown", description="Step down de um asset.")
    @app_commands.describe(
        name="Nome do asset",
        player="Jogador dono do asset (default: voce)",
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
                f"Asset '{name}' nao encontrado para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_down_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Erro ao processar step down do asset.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("eliminated"):
            msg = format_action_confirm(
                "Asset eliminado",
                f"{result['name']} era {die_label(result['was'])}, step down de d4 remove o asset ({label}).",
            )
        else:
            msg = format_action_confirm(
                "Asset step down",
                f"{result['name']} de {die_label(result['from'])} para {die_label(result['to'])} ({label}).",
            )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Remover um asset.")
    @app_commands.describe(
        name="Nome do asset",
        player="Jogador dono do asset (default: voce)",
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
                f"Asset '{name}' nao encontrado para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.remove_asset(campaign["id"], str(interaction.user.id), asset["id"])
        if result is None:
            await interaction.response.send_message("Erro ao remover asset.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Asset removido",
            f"{result['name']} {die_label(result['die_size'])} de {label}.",
        )
        await interaction.response.send_message(msg)


# ---------------------------------------------------------------------------
# Stress group
# ---------------------------------------------------------------------------

class StressGroup(app_commands.Group):
    """Comandos para gerenciar stress."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="stress", description="Gerenciar stress.")
        self.cog = cog

    @app_commands.command(name="add", description="Adicionar stress a um jogador (GM only).")
    @app_commands.describe(
        player="Jogador que recebe o stress",
        type="Tipo de stress (ex: Physical, Mental)",
        die="Tamanho do dado de stress (ex: d6, d8)",
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
                "Apenas o GM pode adicionar stress a outros jogadores."
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
                f"Tipo de stress '{type}' nao encontrado nesta campanha."
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
                "Stress adicionado",
                f"{target['name']} recebe {stress_type['name']} {die_label(die_size)}.",
            )
        elif action == "replaced":
            msg = format_action_confirm(
                "Stress substituido",
                f"{target['name']} {stress_type['name']} de {die_label(result['from'])} para {die_label(result['to'])}. "
                f"Dado recebido ({die_label(die_size)}) era maior que o existente, substituiu.",
            )
        elif action == "stepped_up":
            msg = format_action_confirm(
                "Stress step up",
                f"{target['name']} {stress_type['name']} de {die_label(result['from'])} para {die_label(result['to'])}. "
                f"Dado recebido ({die_label(die_size)}) era igual ou menor, step up aplicado.",
            )
        elif action == "stressed_out":
            stressed_msg = (
                f"{target['name']} stressed out em {stress_type['name']}. "
                f"Stress ja era d12 e recebeu step up."
            )
            if campaign["config"].get("trauma"):
                trauma_result = await _create_trauma_from_stress_out(
                    interaction.client.db, campaign["id"],
                    str(interaction.user.id), target["id"], stress_type["id"],
                    target["name"], stress_type["name"],
                )
                if trauma_result:
                    stressed_msg += (
                        f" Trauma {stress_type['name']} {die_label(trauma_result['die_size'])} criado para {target['name']}."
                    )
            msg = format_action_confirm("Stressed out", stressed_msg)
        else:
            msg = f"Stress processado para {target['name']}."

        await interaction.response.send_message(msg)

    @app_commands.command(name="stepup", description="Step up do stress de um jogador (GM only).")
    @app_commands.describe(
        player="Jogador",
        type="Tipo de stress",
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
                "Apenas o GM pode fazer step up de stress."
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
                f"Tipo de stress '{type}' nao encontrado nesta campanha."
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
                    f"{target['name']} nao tem stress {stress_type['name']} para fazer step up."
                )
                return
            existing = dict(existing)
            new_size = step_up(existing["die_size"])
            if new_size is None:
                stressed_msg = (
                    f"{target['name']} stressed out em {stress_type['name']}. "
                    f"Stress ja era d12 e nao pode fazer step up."
                )
                if campaign["config"].get("trauma"):
                    trauma_result = await _create_trauma_from_stress_out(
                        db, campaign["id"],
                        str(interaction.user.id), target["id"], stress_type["id"],
                        target["name"], stress_type["name"],
                    )
                    if trauma_result:
                        stressed_msg += (
                            f" Trauma {stress_type['name']} {die_label(trauma_result['die_size'])} criado."
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
            "Stress step up",
            f"{target['name']} {stress_type['name']} de {die_label(existing['die_size'])} para {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="stepdown", description="Step down do stress de um jogador.")
    @app_commands.describe(
        player="Jogador",
        type="Tipo de stress",
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
                "Apenas o GM ou o proprio jogador pode fazer step down de stress."
            )
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Tipo de stress '{type}' nao encontrado nesta campanha."
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
                    f"{label} nao tem stress {stress_type['name']} para fazer step down."
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
                    "Stress eliminado",
                    f"{stress_type['name']} de {label} era d4, step down remove o stress.",
                )
                await interaction.response.send_message(msg)
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
            "Stress step down",
            f"{label} {stress_type['name']} de {die_label(existing['die_size'])} para {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Remover stress de um jogador.")
    @app_commands.describe(
        player="Jogador",
        type="Tipo de stress",
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
                "Apenas o GM ou o proprio jogador pode remover stress."
            )
            return

        stress_type = await _find_stress_type_by_name(
            interaction.client.db, campaign["id"], type
        )
        if stress_type is None:
            await interaction.response.send_message(
                f"Tipo de stress '{type}' nao encontrado nesta campanha."
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
                f"{label} nao tem stress {stress_type['name']} para remover."
            )
            return

        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "Stress removido",
            f"{stress_type['name']} {die_label(result['die_size'])} de {label}.",
        )
        await interaction.response.send_message(msg)


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
    """Comandos para gerenciar trauma."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="trauma", description="Gerenciar trauma.")
        self.cog = cog

    async def _check_trauma_enabled(self, interaction: Interaction, campaign: dict) -> bool:
        if not campaign["config"].get("trauma"):
            await interaction.response.send_message(
                "Modulo de trauma nao esta habilitado nesta campanha."
            )
            return False
        return True

    @app_commands.command(name="add", description="Adicionar trauma a um jogador (GM only).")
    @app_commands.describe(
        player="Jogador que recebe o trauma",
        type="Tipo de trauma (mesmo que stress type)",
        die="Tamanho do dado de trauma",
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
                "Apenas o GM pode adicionar trauma."
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
                f"Tipo '{type}' nao encontrado nesta campanha."
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
                        "Trauma substituido",
                        f"{target['name']} {stress_type['name']} de {die_label(old_size)} para {die_label(die_size)}.",
                    )
                else:
                    new_size = step_up(existing["die_size"])
                    if new_size is None:
                        msg = format_action_confirm(
                            "Remocao permanente",
                            f"{target['name']} trauma {stress_type['name']} ja era d12 e recebeu step up. "
                            f"Personagem sofre remocao permanente.",
                        )
                        await interaction.response.send_message(msg)
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
                        "Trauma step up",
                        f"{target['name']} {stress_type['name']} de {die_label(existing['die_size'])} para {die_label(new_size)}. "
                        f"Dado recebido ({die_label(die_size)}) era igual ou menor, step up aplicado.",
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
                    "Trauma adicionado",
                    f"{target['name']} recebe trauma {stress_type['name']} {die_label(die_size)}.",
                )

        await interaction.response.send_message(msg)

    @app_commands.command(name="stepup", description="Step up de trauma de um jogador (GM only).")
    @app_commands.describe(player="Jogador", type="Tipo de trauma")
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
            await interaction.response.send_message("Apenas o GM pode fazer step up de trauma.")
            return

        target = await _resolve_target_player(
            interaction, campaign["id"], actor, player, require_gm_for_others=False
        )
        if target is None:
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Tipo '{type}' nao encontrado nesta campanha.")
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
                    f"{target['name']} nao tem trauma {stress_type['name']}."
                )
                return
            existing = dict(existing)
            new_size = step_up(existing["die_size"])
            if new_size is None:
                msg = format_action_confirm(
                    "Remocao permanente",
                    f"{target['name']} trauma {stress_type['name']} ja era d12, step up indica remocao permanente do personagem.",
                )
                await interaction.response.send_message(msg)
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
            "Trauma step up",
            f"{target['name']} {stress_type['name']} de {die_label(existing['die_size'])} para {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="stepdown", description="Step down de trauma de um jogador.")
    @app_commands.describe(player="Jogador", type="Tipo de trauma")
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
                "Apenas o GM ou o proprio jogador pode fazer step down de trauma."
            )
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Tipo '{type}' nao encontrado nesta campanha.")
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
                    f"{label} nao tem trauma {stress_type['name']}."
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
                    "Trauma eliminado",
                    f"{stress_type['name']} de {label} era d4, step down remove o trauma.",
                )
                await interaction.response.send_message(msg)
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
            "Trauma step down",
            f"{label} {stress_type['name']} de {die_label(existing['die_size'])} para {die_label(new_size)}.",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Remover trauma de um jogador.")
    @app_commands.describe(player="Jogador", type="Tipo de trauma")
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
                "Apenas o GM ou o proprio jogador pode remover trauma."
            )
            return

        stress_type = await _find_stress_type_by_name(interaction.client.db, campaign["id"], type)
        if stress_type is None:
            await interaction.response.send_message(f"Tipo '{type}' nao encontrado nesta campanha.")
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
                    f"{label} nao tem trauma {stress_type['name']} para remover."
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
            "Trauma removido",
            f"{stress_type['name']} {die_label(existing['die_size'])} de {label}.",
        )
        await interaction.response.send_message(msg)


# ---------------------------------------------------------------------------
# Complication group
# ---------------------------------------------------------------------------

class ComplicationGroup(app_commands.Group):
    """Comandos para gerenciar complications."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="complication", description="Gerenciar complications.")
        self.cog = cog

    @app_commands.command(name="add", description="Adicionar uma complication.")
    @app_commands.describe(
        name="Nome da complication",
        die="Tamanho do dado",
        player="Jogador afetado (default: voce)",
        scene="Criar como complication de cena (removida ao encerrar cena)",
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
                    "Apenas o GM pode criar complications de cena."
                )
                return
            result = await sm.add_complication(
                campaign["id"], actor_id, name, die_size,
                player_id=None, scene_id=scene_id, scope="scene",
            )
            msg = format_action_confirm(
                "Complication de cena criada",
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
                "Complication adicionada",
                f"{name} {die_label(die_size)} para {label}.",
            )

        await interaction.response.send_message(msg)

    @app_commands.command(name="stepup", description="Step up de uma complication.")
    @app_commands.describe(
        name="Nome da complication",
        player="Jogador afetado (default: voce)",
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
                f"Complication '{name}' nao encontrada para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_up_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Erro ao processar step up da complication.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("taken_out"):
            msg = format_action_confirm(
                "Taken out",
                f"Complication '{result['name']}' ja era d12, step up indica que {label} esta taken out.",
            )
        else:
            msg = format_action_confirm(
                "Complication step up",
                f"{result['name']} de {die_label(result['from'])} para {die_label(result['to'])} ({label}).",
            )
        await interaction.response.send_message(msg)

    @app_commands.command(name="stepdown", description="Step down de uma complication.")
    @app_commands.describe(
        name="Nome da complication",
        player="Jogador afetado (default: voce)",
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
                f"Complication '{name}' nao encontrada para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.step_down_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Erro ao processar step down da complication.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        if result.get("eliminated"):
            msg = format_action_confirm(
                "Complication eliminada",
                f"{result['name']} era {die_label(result['was'])}, step down de d4 remove a complication ({label}).",
            )
        else:
            msg = format_action_confirm(
                "Complication step down",
                f"{result['name']} de {die_label(result['from'])} para {die_label(result['to'])} ({label}).",
            )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Remover uma complication.")
    @app_commands.describe(
        name="Nome da complication",
        player="Jogador afetado (default: voce)",
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
                f"Complication '{name}' nao encontrada para {label}."
            )
            return

        sm = StateManager(interaction.client.db)
        result = await sm.remove_complication(campaign["id"], str(interaction.user.id), comp["id"])
        if result is None:
            await interaction.response.send_message("Erro ao remover complication.")
            return

        label = _player_label(target, target["id"] == actor["id"])
        msg = format_action_confirm(
            "Complication removida",
            f"{result['name']} {die_label(result['die_size'])} de {label}.",
        )
        await interaction.response.send_message(msg)


# ---------------------------------------------------------------------------
# PP group
# ---------------------------------------------------------------------------

class PPGroup(app_commands.Group):
    """Comandos para gerenciar plot points."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="pp", description="Gerenciar plot points.")
        self.cog = cog

    @app_commands.command(name="add", description="Adicionar plot points.")
    @app_commands.describe(
        amount="Quantidade de PP a adicionar",
        player="Jogador (default: voce, GM pode dar para outros)",
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
            await interaction.response.send_message("Quantidade deve ser positiva. Use /pp remove para gastar PP.")
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
            "PP adicionado",
            f"{label}: {result['from']} para {result['to']} PP (+{amount}).",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Gastar plot points.")
    @app_commands.describe(
        amount="Quantidade de PP a gastar",
        player="Jogador (default: voce, GM pode remover de outros)",
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
            await interaction.response.send_message("Quantidade deve ser positiva. Use /pp add para ganhar PP.")
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
                f"{label} tem apenas {result['current']} PP, nao pode gastar {result['requested']}."
            )
            return

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "PP gasto",
            f"{label}: {result['from']} para {result['to']} PP (-{amount}).",
        )
        await interaction.response.send_message(msg)


# ---------------------------------------------------------------------------
# XP group
# ---------------------------------------------------------------------------

class XPGroup(app_commands.Group):
    """Comandos para gerenciar XP."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="xp", description="Gerenciar experience points.")
        self.cog = cog

    @app_commands.command(name="add", description="Adicionar XP.")
    @app_commands.describe(
        amount="Quantidade de XP a adicionar",
        player="Jogador (default: voce)",
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
            await interaction.response.send_message("Quantidade deve ser positiva. Use /xp remove para remover XP.")
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
            "XP adicionado",
            f"{label}: {result['from']} para {result['to']} XP (+{amount}).",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="remove", description="Remover XP.")
    @app_commands.describe(
        amount="Quantidade de XP a remover",
        player="Jogador (default: voce)",
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
            await interaction.response.send_message("Quantidade deve ser positiva.")
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
                f"{label} tem apenas {result['current']} XP, nao pode remover {result['requested']}."
            )
            return

        is_self = target["id"] == actor["id"]
        label = _player_label(target, is_self)
        msg = format_action_confirm(
            "XP removido",
            f"{label}: {result['from']} para {result['to']} XP (-{amount}).",
        )
        await interaction.response.send_message(msg)


# ---------------------------------------------------------------------------
# Hero dice group
# ---------------------------------------------------------------------------

class HeroGroup(app_commands.Group):
    """Comandos para gerenciar hero dice."""

    def __init__(self, cog: "StateCog") -> None:
        super().__init__(name="hero", description="Gerenciar hero dice.")
        self.cog = cog

    async def _check_hero_enabled(self, interaction: Interaction, campaign: dict) -> bool:
        if not campaign["config"].get("hero_dice"):
            await interaction.response.send_message(
                "Modulo de hero dice nao esta habilitado nesta campanha."
            )
            return False
        return True

    @app_commands.command(name="bank", description="Bancar um hero die.")
    @app_commands.describe(die="Tamanho do dado a bancar")
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
            "Hero die bancado",
            f"{die_label(die_size)} adicionado ao banco.",
            f"Banco atual: {', '.join(bank_strs)}.",
        )
        await interaction.response.send_message(msg)

    @app_commands.command(name="use", description="Usar um hero die do banco.")
    @app_commands.describe(die="Tamanho do dado a usar")
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
                    f"Voce nao tem um hero die {die_label(die_size)} no banco."
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
            bank_info = f"Banco restante: {', '.join(bank_strs)}."
        else:
            bank_info = "Banco vazio."

        msg = format_action_confirm(
            "Hero die usado",
            f"{die_label(die_size)} removido do banco. Role e some ao total.",
            bank_info,
        )
        await interaction.response.send_message(msg)


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
