import logging

import discord
from discord import app_commands
from discord.ext import commands

from cortex_bot.models.dice import die_label, step_down
from cortex_bot.services.formatter import format_scene_end, format_campaign_info
from cortex_bot.utils import has_gm_permission

log = logging.getLogger(__name__)


class SceneGroup(app_commands.Group):
    """Scene management commands."""

    def __init__(self) -> None:
        super().__init__(name="scene", description="Gerenciamento de cenas.")


class SceneCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.scene_group = SceneGroup()
        self.bot.tree.add_command(self.scene_group)
        self._register_commands()

    def _register_commands(self) -> None:
        group = self.scene_group

        @group.command(name="start", description="Iniciar uma nova cena.")
        @app_commands.describe(name="Nome da cena (opcional).")
        async def scene_start(interaction: discord.Interaction, name: str | None = None) -> None:
            await self._start(interaction, name)

        @group.command(name="end", description="Encerrar a cena ativa.")
        @app_commands.describe(bridge="Bridge scene: step down all stress (d4 eliminado).")
        async def scene_end(interaction: discord.Interaction, bridge: bool = False) -> None:
            await self._end(interaction, bridge)

        @group.command(name="info", description="Mostrar estado da cena atual.")
        async def scene_info(interaction: discord.Interaction) -> None:
            await self._info(interaction)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.scene_group.name, type=self.scene_group.type)

    async def _resolve_campaign(
        self, interaction: discord.Interaction
    ) -> dict | None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await self.bot.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
            )
        return campaign

    async def _require_gm(
        self, interaction: discord.Interaction, campaign_id: int
    ) -> dict | None:
        player = await self.bot.db.get_player(
            campaign_id, str(interaction.user.id)
        )
        if player is None or not has_gm_permission(player):
            await interaction.response.send_message(
                "Apenas o GM pode usar este comando."
            )
            return None
        return player

    async def _start(
        self, interaction: discord.Interaction, name: str | None
    ) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return

        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        active = await self.bot.db.get_active_scene(campaign["id"])
        if active is not None:
            label = active["name"] or "sem nome"
            await interaction.response.send_message(
                f"Ja existe uma cena ativa: {label}. Encerre-a antes de iniciar outra."
            )
            return

        async with self.bot.db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, 1)",
                (campaign["id"], name),
            )
            await conn.commit()

        label = name or "sem nome"

        doom_enabled = campaign["config"].get("doom_pool", False)
        guide = (
            "\n"
            "Comandos de jogo: /roll para rolar, /asset add para criar assets, "
            "/campaign info para ver estado."
        )
        if doom_enabled:
            guide += " GM: /stress add, /complication add, /doom."
        else:
            guide += " GM: /stress add, /complication add."

        from cortex_bot.views.scene_views import PostSceneStartView

        view = PostSceneStartView(campaign["id"], doom_enabled=doom_enabled)
        await interaction.response.send_message(
            f"Cena iniciada: {label}.{guide}", view=view
        )

    async def _end(
        self, interaction: discord.Interaction, bridge: bool
    ) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return

        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        scene = await self.bot.db.get_active_scene(campaign["id"])
        if scene is None:
            await interaction.response.send_message("Nenhuma cena ativa.")
            return

        await interaction.response.defer()

        scene_id = scene["id"]
        campaign_id = campaign["id"]

        removed_assets = await self.bot.db.get_scene_assets(scene_id)
        removed_complications = await self.bot.db.get_scene_complications(scene_id)
        removed_crisis_pools = await self.bot.db.get_crisis_pools(scene_id)

        stress_changes: list[dict] = []
        if bridge:
            players = await self.bot.db.get_players(campaign_id)
            for p in players:
                if p["is_gm"]:
                    continue
                stress_list = await self.bot.db.get_player_stress(
                    campaign_id, p["id"]
                )
                for s in stress_list:
                    new_size = step_down(s["die_size"])
                    if new_size is None:
                        async with self.bot.db.connect() as conn:
                            await conn.execute(
                                "DELETE FROM stress WHERE id = ?", (s["id"],)
                            )
                            await conn.commit()
                        stress_changes.append({
                            "player": p["name"],
                            "type": s["stress_type_name"],
                            "eliminated": True,
                            "from": s["die_size"],
                        })
                    else:
                        async with self.bot.db.connect() as conn:
                            await conn.execute(
                                "UPDATE stress SET die_size = ? WHERE id = ?",
                                (new_size, s["id"]),
                            )
                            await conn.commit()
                        stress_changes.append({
                            "player": p["name"],
                            "type": s["stress_type_name"],
                            "from": s["die_size"],
                            "to": new_size,
                        })

        async with self.bot.db.connect() as conn:
            await conn.execute(
                "DELETE FROM assets WHERE scene_id = ? AND duration = 'scene'",
                (scene_id,),
            )
            await conn.execute(
                "DELETE FROM complications WHERE scene_id = ? AND scope = 'scene'",
                (scene_id,),
            )
            for cp in removed_crisis_pools:
                await conn.execute(
                    "DELETE FROM crisis_pool_dice WHERE crisis_pool_id = ?",
                    (cp["id"],),
                )
            await conn.execute(
                "DELETE FROM crisis_pools WHERE scene_id = ?",
                (scene_id,),
            )
            await conn.execute(
                "UPDATE scenes SET is_active = 0 WHERE id = ?",
                (scene_id,),
            )
            await conn.commit()

        doom_pool = await self.bot.db.get_doom_pool(campaign_id)
        players = await self.bot.db.get_players(campaign_id)
        persistent_parts: list[str] = []

        for p in players:
            remaining_stress = await self.bot.db.get_player_stress(
                campaign_id, p["id"]
            )
            if remaining_stress:
                stress_strs = [
                    f"{rs['stress_type_name']} {die_label(rs['die_size'])}"
                    for rs in remaining_stress
                ]
                persistent_parts.append(
                    f"{p['name']}: stress {', '.join(stress_strs)}."
                )

        if doom_pool:
            doom_strs = [die_label(d["die_size"]) for d in doom_pool]
            persistent_parts.append(f"Doom Pool: {', '.join(doom_strs)}.")

        persistent_state = "\n".join(persistent_parts) if persistent_parts else ""

        summary = format_scene_end(
            scene["name"],
            removed_assets,
            removed_complications,
            removed_crisis_pools,
            stress_changes=stress_changes or None,
            persistent_state=persistent_state,
        )
        summary += (
            "\n\nUse /scene start para iniciar nova cena, "
            "ou /campaign info para ver estado persistente."
        )
        from cortex_bot.views.scene_views import PostSceneEndView

        view = PostSceneEndView(campaign["id"])
        await interaction.followup.send(summary, view=view)

    async def _info(self, interaction: discord.Interaction) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return

        scene = await self.bot.db.get_active_scene(campaign["id"])
        if scene is None:
            await interaction.response.send_message("Nenhuma cena ativa.")
            return

        campaign_id = campaign["id"]
        scene_id = scene["id"]

        players = await self.bot.db.get_players(campaign_id)
        player_states: dict[int, dict] = {}
        for p in players:
            pid = p["id"]
            stress = await self.bot.db.get_player_stress(campaign_id, pid)
            trauma = await self.bot.db.get_player_trauma(campaign_id, pid)
            assets = await self.bot.db.get_player_assets(campaign_id, pid)
            complications = await self.bot.db.get_player_complications(
                campaign_id, pid
            )
            hero_dice = await self.bot.db.get_hero_dice(campaign_id, pid)
            player_states[pid] = {
                "stress": stress,
                "trauma": trauma,
                "assets": assets,
                "complications": complications,
                "hero_dice": hero_dice,
            }

        doom_pool = await self.bot.db.get_doom_pool(campaign_id)
        scene_assets = await self.bot.db.get_scene_assets(scene_id)
        scene_complications = await self.bot.db.get_scene_complications(scene_id)
        crisis_pools = await self.bot.db.get_crisis_pools(scene_id)

        msg = format_campaign_info(
            campaign,
            players,
            player_states,
            scene,
            doom_pool,
            scene_assets=scene_assets,
            scene_complications=scene_complications,
            crisis_pools=crisis_pools,
        )
        from cortex_bot.views.common import PostInfoView

        view = PostInfoView(campaign["id"], has_active_scene=True)
        await interaction.response.send_message(msg, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SceneCog(bot))
