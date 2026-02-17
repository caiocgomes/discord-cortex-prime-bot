"""Roll command cog for Cortex Prime dice rolling."""

import logging
from typing import Optional

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.models.dice import parse_dice_notation, die_label
from cortex_bot.services.roller import (
    roll_pool,
    find_hitches,
    is_botch,
    calculate_best_options,
)
from cortex_bot.services.formatter import format_roll_result
from cortex_bot.services.state_manager import StateManager
from cortex_bot.utils import has_gm_permission

log = logging.getLogger(__name__)


class RollingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def db(self):
        return self.bot.db

    async def _include_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for the include parameter: suggests the player's assets."""
        try:
            server_id = str(interaction.guild_id)
            channel_id = str(interaction.channel_id)
            campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
            if campaign is None:
                return []
            player = await self.db.get_player(
                campaign["id"], str(interaction.user.id)
            )
            if player is None:
                return []
            assets = await self.db.get_player_assets(campaign["id"], player["id"])
            if not assets:
                return []

            # Parse what the user already typed to know which assets are already selected.
            already_selected = set()
            if current:
                parts = [p.strip().lower() for p in current.rsplit(",", 1)]
                if len(parts) > 1:
                    already_selected = {
                        s.strip().lower() for s in parts[0].split(",") if s.strip()
                    }

            # Build the prefix so we append to what was already typed.
            prefix = ""
            if "," in current:
                prefix = current.rsplit(",", 1)[0] + ", "

            search = current.rsplit(",", 1)[-1].strip().lower()

            choices: list[app_commands.Choice[str]] = []
            for asset in assets:
                name_lower = asset["name"].lower()
                if name_lower in already_selected:
                    continue
                if search and search not in name_lower:
                    continue
                label = f"{asset['name']} {die_label(asset['die_size'])}"
                value = prefix + asset["name"]
                choices.append(app_commands.Choice(name=label, value=value))
                if len(choices) >= 25:
                    break
            return choices
        except Exception:
            log.exception("Autocomplete error in include")
            return []

    @app_commands.command(
        name="roll",
        description="Rolar dados no Cortex Prime. Ex: /roll dice:1d8 1d10 1d6",
    )
    @app_commands.describe(
        dice="Notacao de dados separados por espaco, ex: 1d8 1d10 2d6",
        include="Nomes de assets para incluir na pool (separados por virgula)",
        difficulty="Numero alvo para comparar o total",
        extra="Dados extras comprados com PP, ex: 1d6",
    )
    @app_commands.autocomplete(include=_include_autocomplete)
    async def roll(
        self,
        interaction: Interaction,
        dice: str,
        include: Optional[str] = None,
        difficulty: Optional[int] = None,
        extra: Optional[str] = None,
    ) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        actor_id = str(interaction.user.id)

        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
            )
            return

        campaign_id = campaign["id"]
        config = campaign["config"]

        player = await self.db.get_player(campaign_id, actor_id)
        if player is None:
            await interaction.response.send_message(
                "Voce nao esta registrado nesta campanha."
            )
            return

        player_id = player["id"]
        player_name = player["name"]

        # 1. Parse base dice notation.
        try:
            pool = parse_dice_notation(dice)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        # 2. Resolve included assets.
        all_assets = await self.db.get_player_assets(campaign_id, player_id)
        included_assets: list[str] = []
        available_assets: list[dict] = []

        if include:
            requested_names = [n.strip().lower() for n in include.split(",") if n.strip()]
            asset_by_name: dict[str, dict] = {
                a["name"].lower(): a for a in all_assets
            }
            not_found: list[str] = []
            for req in requested_names:
                asset = asset_by_name.get(req)
                if asset is None:
                    not_found.append(req)
                else:
                    pool.append(asset["die_size"])
                    included_assets.append(
                        f"{asset['name']} {die_label(asset['die_size'])}"
                    )
            if not_found:
                await interaction.response.send_message(
                    f"Assets nao encontrados: {', '.join(not_found)}. "
                    "Verifique os nomes e tente novamente."
                )
                return
            included_names_lower = set(requested_names)
            available_assets = [
                a for a in all_assets if a["name"].lower() not in included_names_lower
            ]
        else:
            available_assets = list(all_assets)

        # 3. Handle extra dice bought with PP.
        if extra:
            try:
                extra_dice = parse_dice_notation(extra)
            except ValueError as exc:
                await interaction.response.send_message(f"Dados extras invalidos: {exc}")
                return

            pp_cost = len(extra_dice)
            state_mgr = StateManager(self.db)
            pp_result = await state_mgr.update_pp(
                campaign_id, actor_id, player_id, -pp_cost, player_name
            )
            if "error" in pp_result:
                await interaction.response.send_message(
                    f"PP insuficiente. Voce tem {pp_result['current']}, "
                    f"precisa de {pp_result['requested']}."
                )
                return

            pool.extend(extra_dice)

        # 4. Roll.
        results = roll_pool(pool)

        # 5. Hitches and botch.
        hitches = find_hitches(results)
        botch = is_botch(results)

        # 6. Best options (if campaign has best_mode enabled).
        best_options: list[dict] | None = None
        if config.get("best_mode") and not botch:
            best_options = calculate_best_options(results)

        # 7. Opposition elements: stress and complications on this player.
        stress_list = await self.db.get_player_stress(campaign_id, player_id)
        complication_list = await self.db.get_player_complications(campaign_id, player_id)
        opposition_elements: list[str] = []
        for s in stress_list:
            opposition_elements.append(
                f"{s['stress_type_name']} {die_label(s['die_size'])}"
            )
        for c in complication_list:
            opposition_elements.append(
                f"{c['name']} {die_label(c['die_size'])}"
            )

        # 8. Format and send.
        text = format_roll_result(
            player_name=player_name,
            results=results,
            included_assets=included_assets or None,
            hitches=hitches or None,
            is_botch=botch,
            best_options=best_options,
            difficulty=difficulty,
            available_assets=available_assets or None,
            opposition_elements=opposition_elements or None,
        )
        from cortex_bot.views.rolling_views import PostRollView

        hitch_count = len(hitches) if hitches and not botch else 0
        doom_enabled = config.get("doom_pool", False)
        view = PostRollView(
            campaign_id,
            hitch_count=hitch_count,
            doom_enabled=doom_enabled,
        )
        await interaction.response.send_message(text, view=view)


    @app_commands.command(
        name="gmroll",
        description="Rolar dados como GM/NPC, sem estado pessoal.",
    )
    @app_commands.describe(
        dice="Notacao de dados separados por espaco, ex: 2d8 1d10",
        name="Nome do NPC (default: GM)",
        difficulty="Numero alvo para comparar o total",
    )
    async def gmroll(
        self,
        interaction: Interaction,
        dice: str,
        name: Optional[str] = None,
        difficulty: Optional[int] = None,
    ) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)

        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
            )
            return

        player = await self.db.get_player(campaign["id"], str(interaction.user.id))
        if player is None or not has_gm_permission(player):
            await interaction.response.send_message(
                "Apenas o GM ou delegados podem usar este comando."
            )
            return

        try:
            pool = parse_dice_notation(dice)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        results = roll_pool(pool)
        hitches = find_hitches(results)
        botch = is_botch(results)

        best_options: list[dict] | None = None
        if campaign["config"].get("best_mode") and not botch:
            best_options = calculate_best_options(results)

        player_name = name or "GM"
        text = format_roll_result(
            player_name=player_name,
            results=results,
            hitches=hitches or None,
            is_botch=botch,
            best_options=best_options,
            difficulty=difficulty,
        )
        from cortex_bot.views.rolling_views import PostRollView

        hitch_count = len(hitches) if hitches and not botch else 0
        doom_enabled = campaign["config"].get("doom_pool", False)
        view = PostRollView(
            campaign["id"],
            hitch_count=hitch_count,
            doom_enabled=doom_enabled,
        )
        await interaction.response.send_message(text, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RollingCog(bot))
