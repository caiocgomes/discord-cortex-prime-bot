"""Campaign lifecycle commands: setup, info, and campaign end."""

import json
import logging
import re

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.services.formatter import format_campaign_info
from cortex_bot.models.dice import die_label
from discord import Member

log = logging.getLogger(__name__)

MENTION_PATTERN = re.compile(r"<@!?(\d+)>")


async def get_campaign_or_error(interaction: Interaction) -> dict | None:
    """Fetch the campaign for this channel. Sends an error and returns None if absent."""
    db = interaction.client.db
    server_id = str(interaction.guild_id)
    channel_id = str(interaction.channel_id)
    campaign = await db.get_campaign_by_channel(server_id, channel_id)
    if campaign is None:
        await interaction.response.send_message(
            "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
        )
    return campaign


async def is_gm_check(interaction: Interaction, campaign: dict) -> bool:
    """Return True if the user is the GM. Sends an error message and returns False otherwise."""
    db = interaction.client.db
    player = await db.get_player(campaign["id"], str(interaction.user.id))
    if player is None or not player["is_gm"]:
        await interaction.response.send_message(
            "Apenas o GM pode executar este comando."
        )
        return False
    return True


class CampaignCog(commands.GroupCog, group_name="campaign"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def db(self):
        return self.bot.db

    @app_commands.command(name="setup", description="Criar uma nova campanha neste canal.")
    @app_commands.describe(
        name="Nome da campanha",
        players="Jogadores (mencoes separadas por espaco, ex: @Alice @Bob)",
        stress_types="Tipos de stress separados por virgula (ex: Physical,Mental,Social)",
        gm="Mestre da campanha (default: quem executa o comando)",
        doom_pool="Habilitar Doom Pool (default: nao)",
        hero_dice="Habilitar Hero Dice (default: nao)",
        trauma="Habilitar Trauma (default: nao)",
        best_mode="Habilitar Best Mode com opcoes pre-calculadas (default: sim)",
    )
    async def setup(
        self,
        interaction: Interaction,
        name: str,
        players: str,
        stress_types: str,
        gm: Member | None = None,
        doom_pool: bool = False,
        hero_dice: bool = False,
        trauma: bool = False,
        best_mode: bool = True,
    ) -> None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)

        existing = await self.db.get_campaign_by_channel(server_id, channel_id)
        if existing is not None:
            await interaction.response.send_message(
                "Ja existe uma campanha ativa neste canal. "
                "Use /campaign campaign_end para encerrar antes de criar outra."
            )
            return

        player_ids = MENTION_PATTERN.findall(players)
        if not player_ids:
            await interaction.response.send_message(
                "Nenhum jogador identificado. Mencione pelo menos um jogador "
                "(ex: @Alice @Bob)."
            )
            return

        stress_names = [s.strip() for s in stress_types.split(",") if s.strip()]
        if not stress_names:
            await interaction.response.send_message(
                "Informe pelo menos um tipo de stress separado por virgula."
            )
            return

        config = {
            "doom_pool": doom_pool,
            "hero_dice": hero_dice,
            "trauma": trauma,
            "best_mode": best_mode,
        }

        gm_member = gm or interaction.user
        gm_discord_id = str(gm_member.id)

        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
                (server_id, channel_id, name, json.dumps(config)),
            )
            campaign_id = cursor.lastrowid

            # Register the GM.
            await conn.execute(
                "INSERT INTO players (campaign_id, discord_user_id, name, is_gm) VALUES (?, ?, ?, 1)",
                (campaign_id, gm_discord_id, gm_member.display_name),
            )

            # Register mentioned players. Skip the GM if mentioned.
            for uid in player_ids:
                if uid == gm_discord_id:
                    continue
                try:
                    member = await interaction.guild.fetch_member(int(uid))
                    member_name = member.display_name
                except discord.NotFound:
                    member_name = f"User#{uid}"
                await conn.execute(
                    "INSERT OR IGNORE INTO players (campaign_id, discord_user_id, name, is_gm) VALUES (?, ?, ?, 0)",
                    (campaign_id, uid, member_name),
                )

            for sname in stress_names:
                await conn.execute(
                    "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
                    (campaign_id, sname),
                )

            await conn.commit()

        registered = await self.db.get_players(campaign_id)
        player_names = [p["name"] for p in registered]
        modules_on = [k for k, v in config.items() if v]
        modules_str = ", ".join(modules_on) if modules_on else "nenhum modulo extra"

        await interaction.response.send_message(
            f"Campanha '{name}' criada. "
            f"GM: {gm_member.display_name}. "
            f"Jogadores: {', '.join(player_names)}. "
            f"Stress: {', '.join(stress_names)}. "
            f"Modulos ativos: {modules_str}.\n"
            "\n"
            "Proximos passos: use /scene start para iniciar uma cena. "
            "Jogadores podem usar /roll para rolar dados. "
            "/campaign info mostra o estado completo. "
            "/help para referencia de comandos."
        )

    @app_commands.command(name="info", description="Exibir estado completo da campanha.")
    async def info(self, interaction: Interaction) -> None:
        campaign = await get_campaign_or_error(interaction)
        if campaign is None:
            return

        campaign_id = campaign["id"]
        config = campaign["config"]
        players = await self.db.get_players(campaign_id)
        scene = await self.db.get_active_scene(campaign_id)

        player_states: dict[int, dict] = {}
        for p in players:
            pid = p["id"]
            state: dict = {}
            state["stress"] = await self.db.get_player_stress(campaign_id, pid)
            state["assets"] = await self.db.get_player_assets(campaign_id, pid)
            state["complications"] = await self.db.get_player_complications(campaign_id, pid)
            if config.get("trauma"):
                state["trauma"] = await self.db.get_player_trauma(campaign_id, pid)
            if config.get("hero_dice"):
                state["hero_dice"] = await self.db.get_hero_dice(campaign_id, pid)
            player_states[pid] = state

        doom_pool = None
        if config.get("doom_pool"):
            doom_pool = await self.db.get_doom_pool(campaign_id)

        scene_assets = None
        scene_complications = None
        crisis_pools = None
        if scene is not None:
            scene_assets = await self.db.get_scene_assets(scene["id"])
            scene_complications = await self.db.get_scene_complications(scene["id"])
            crisis_pools = await self.db.get_crisis_pools(scene["id"])

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
        await interaction.response.send_message(text)

    @app_commands.command(name="delegate", description="Promover um jogador a delegado (apenas GM).")
    @app_commands.describe(player="Jogador para promover a delegado")
    async def delegate(self, interaction: Interaction, player: Member) -> None:
        campaign = await get_campaign_or_error(interaction)
        if campaign is None:
            return

        if not await is_gm_check(interaction, campaign):
            return

        target_id = str(player.id)
        gm_id = str(interaction.user.id)

        if target_id == gm_id:
            await interaction.response.send_message(
                "O GM ja possui todas as permissoes."
            )
            return

        target = await self.db.get_player(campaign["id"], target_id)
        if target is None:
            await interaction.response.send_message(
                f"{player.display_name} nao esta registrado nesta campanha."
            )
            return

        if target["is_delegate"]:
            await interaction.response.send_message(
                f"{target['name']} ja e delegado."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (target["id"],),
            )
            await conn.commit()

        await interaction.response.send_message(
            f"{target['name']} agora e delegado. Possui acesso a comandos de GM."
        )

    @app_commands.command(name="undelegate", description="Revogar delegacao de um jogador (apenas GM).")
    @app_commands.describe(player="Jogador para revogar delegacao")
    async def undelegate(self, interaction: Interaction, player: Member) -> None:
        campaign = await get_campaign_or_error(interaction)
        if campaign is None:
            return

        if not await is_gm_check(interaction, campaign):
            return

        target_id = str(player.id)
        target = await self.db.get_player(campaign["id"], target_id)
        if target is None:
            await interaction.response.send_message(
                f"{player.display_name} nao esta registrado nesta campanha."
            )
            return

        if not target["is_delegate"]:
            await interaction.response.send_message(
                f"{target['name']} nao e delegado."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 0 WHERE id = ?",
                (target["id"],),
            )
            await conn.commit()

        await interaction.response.send_message(
            f"Delegacao de {target['name']} revogada."
        )

    @app_commands.command(
        name="campaign_end",
        description="Encerrar a campanha deste canal (apenas GM).",
    )
    @app_commands.describe(
        confirm="Confirmar encerramento da campanha.",
    )
    @app_commands.choices(
        confirm=[app_commands.Choice(name="sim", value="sim")],
    )
    async def campaign_end(
        self, interaction: Interaction, confirm: app_commands.Choice[str] | None = None,
    ) -> None:
        campaign = await get_campaign_or_error(interaction)
        if campaign is None:
            return

        if not await is_gm_check(interaction, campaign):
            return

        if confirm is None or confirm.value != "sim":
            await interaction.response.send_message(
                f"Para encerrar a campanha '{campaign['name']}', execute novamente "
                "com confirm:sim. Todos os dados serao removidos permanentemente."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "DELETE FROM campaigns WHERE id = ?", (campaign["id"],)
            )
            await conn.commit()

        await interaction.response.send_message(
            f"Campanha '{campaign['name']}' encerrada. Todos os dados foram removidos."
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CampaignCog(bot))
