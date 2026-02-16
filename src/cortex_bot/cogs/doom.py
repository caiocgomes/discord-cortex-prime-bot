"""Doom pool and crisis pool management commands."""

import logging
from typing import Optional

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from cortex_bot.models.dice import (
    parse_single_die,
    parse_dice_notation,
    die_label,
    step_up,
    step_down,
)
from cortex_bot.services.roller import roll_pool, calculate_best_options
from cortex_bot.utils import has_gm_permission

log = logging.getLogger(__name__)


class DoomGroup(app_commands.Group):
    """Doom pool commands (GM only)."""

    def __init__(self) -> None:
        super().__init__(name="doom", description="Gerenciamento do Doom Pool.")


class CrisisGroup(app_commands.Group):
    """Crisis pool commands (GM only)."""

    def __init__(self) -> None:
        super().__init__(name="crisis", description="Gerenciamento de Crisis Pools.")


class DoomCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.doom_group = DoomGroup()
        self.crisis_group = CrisisGroup()
        self.bot.tree.add_command(self.doom_group)
        self.bot.tree.add_command(self.crisis_group)
        self._register_doom_commands()
        self._register_crisis_commands()

    @property
    def db(self):
        return self.bot.db

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.doom_group.name, type=self.doom_group.type)
        self.bot.tree.remove_command(self.crisis_group.name, type=self.crisis_group.type)

    # ── helpers ──────────────────────────────────────────────────────

    async def _resolve_campaign(self, interaction: Interaction) -> dict | None:
        server_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        campaign = await self.db.get_campaign_by_channel(server_id, channel_id)
        if campaign is None:
            await interaction.response.send_message(
                "Nenhuma campanha ativa neste canal. Use /campaign setup para criar uma."
            )
        return campaign

    async def _require_gm(
        self, interaction: Interaction, campaign_id: int
    ) -> dict | None:
        player = await self.db.get_player(campaign_id, str(interaction.user.id))
        if player is None or not has_gm_permission(player):
            await interaction.response.send_message(
                "Apenas o GM pode usar este comando."
            )
            return None
        return player

    async def _require_doom_enabled(
        self, interaction: Interaction, campaign: dict
    ) -> bool:
        if not campaign["config"].get("doom_pool", False):
            await interaction.response.send_message(
                "Doom Pool nao esta habilitado nesta campanha."
            )
            return False
        return True

    def _format_doom_pool(self, doom_dice: list[dict]) -> str:
        if not doom_dice:
            return "Doom Pool: vazio."
        labels = [die_label(d["die_size"]) for d in doom_dice]
        return f"Doom Pool: {', '.join(labels)}."

    # ── doom commands ────────────────────────────────────────────────

    def _register_doom_commands(self) -> None:
        group = self.doom_group

        @group.command(name="add", description="Adicionar dado ao Doom Pool.")
        @app_commands.describe(die="Dado para adicionar (ex: d6, d8).")
        async def doom_add(interaction: Interaction, die: str) -> None:
            await self._doom_add(interaction, die)

        @group.command(name="remove", description="Remover um dado do Doom Pool.")
        @app_commands.describe(die="Dado para remover (ex: d6).")
        async def doom_remove(interaction: Interaction, die: str) -> None:
            await self._doom_remove(interaction, die)

        @group.command(name="stepup", description="Step up de um dado no Doom Pool.")
        @app_commands.describe(die="Dado para fazer step up (ex: d6 vira d8).")
        async def doom_stepup(interaction: Interaction, die: str) -> None:
            await self._doom_stepup(interaction, die)

        @group.command(name="stepdown", description="Step down de um dado no Doom Pool.")
        @app_commands.describe(die="Dado para fazer step down (ex: d8 vira d6).")
        async def doom_stepdown(interaction: Interaction, die: str) -> None:
            await self._doom_stepdown(interaction, die)

        @group.command(name="roll", description="Rolar o Doom Pool.")
        @app_commands.describe(dice="Dados especificos para rolar (opcional, ex: d8 d6). Sem argumento rola todos.")
        async def doom_roll(interaction: Interaction, dice: Optional[str] = None) -> None:
            await self._doom_roll(interaction, dice)

        @group.command(name="spend", description="Gastar um dado do Doom Pool.")
        @app_commands.describe(die="Dado para gastar (ex: d8).")
        async def doom_spend(interaction: Interaction, die: str) -> None:
            await self._doom_spend(interaction, die)

    async def _doom_add(self, interaction: Interaction, die: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        campaign_id = campaign["id"]
        actor_id = str(interaction.user.id)

        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO doom_pool_dice (campaign_id, die_size) VALUES (?, ?)",
                (campaign_id, size),
            )
            doom_die_id = cursor.lastrowid
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "doom_add",
            {"die_size": size},
            {"action": "delete", "table": "doom_pool_dice", "id": doom_die_id},
        )

        pool = await self.db.get_doom_pool(campaign_id)
        await interaction.response.send_message(
            f"Adicionado {die_label(size)} ao Doom Pool. {self._format_doom_pool(pool)}"
        )

    async def _doom_remove(self, interaction: Interaction, die: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        campaign_id = campaign["id"]
        actor_id = str(interaction.user.id)
        pool = await self.db.get_doom_pool(campaign_id)

        target = None
        for d in pool:
            if d["die_size"] == size:
                target = d
                break

        if target is None:
            await interaction.response.send_message(
                f"Nenhum {die_label(size)} no Doom Pool."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "DELETE FROM doom_pool_dice WHERE id = ?", (target["id"],)
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "doom_remove",
            {"die_size": size},
            {
                "action": "insert", "table": "doom_pool_dice",
                "data": {"campaign_id": campaign_id, "die_size": size},
            },
        )

        pool = await self.db.get_doom_pool(campaign_id)
        await interaction.response.send_message(
            f"Removido {die_label(size)} do Doom Pool. {self._format_doom_pool(pool)}"
        )

    async def _doom_stepup(self, interaction: Interaction, die: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        campaign_id = campaign["id"]
        actor_id = str(interaction.user.id)
        pool = await self.db.get_doom_pool(campaign_id)

        target = None
        for d in pool:
            if d["die_size"] == size:
                target = d
                break

        if target is None:
            await interaction.response.send_message(
                f"Nenhum {die_label(size)} no Doom Pool."
            )
            return

        new_size = step_up(size)
        if new_size is None:
            await interaction.response.send_message(
                f"{die_label(size)} ja esta no maximo. Nao e possivel fazer step up."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "UPDATE doom_pool_dice SET die_size = ? WHERE id = ?",
                (new_size, target["id"]),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "doom_stepup",
            {"from": size, "to": new_size},
            {"action": "update", "table": "doom_pool_dice", "id": target["id"], "field": "die_size", "value": size},
        )

        pool = await self.db.get_doom_pool(campaign_id)
        await interaction.response.send_message(
            f"Step up no Doom Pool: {die_label(size)} para {die_label(new_size)}. {self._format_doom_pool(pool)}"
        )

    async def _doom_stepdown(self, interaction: Interaction, die: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        campaign_id = campaign["id"]
        actor_id = str(interaction.user.id)
        pool = await self.db.get_doom_pool(campaign_id)

        target = None
        for d in pool:
            if d["die_size"] == size:
                target = d
                break

        if target is None:
            await interaction.response.send_message(
                f"Nenhum {die_label(size)} no Doom Pool."
            )
            return

        new_size = step_down(size)
        if new_size is None:
            # d4 stepped down is eliminated
            async with self.db.connect() as conn:
                await conn.execute(
                    "DELETE FROM doom_pool_dice WHERE id = ?", (target["id"],)
                )
                await conn.commit()

            await self.db.log_action(
                campaign_id, actor_id, "doom_stepdown_eliminated",
                {"was": size},
                {
                    "action": "insert", "table": "doom_pool_dice",
                    "data": {"campaign_id": campaign_id, "die_size": size},
                },
            )

            pool = await self.db.get_doom_pool(campaign_id)
            await interaction.response.send_message(
                f"Step down no Doom Pool: {die_label(size)} eliminado. {self._format_doom_pool(pool)}"
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "UPDATE doom_pool_dice SET die_size = ? WHERE id = ?",
                (new_size, target["id"]),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "doom_stepdown",
            {"from": size, "to": new_size},
            {"action": "update", "table": "doom_pool_dice", "id": target["id"], "field": "die_size", "value": size},
        )

        pool = await self.db.get_doom_pool(campaign_id)
        await interaction.response.send_message(
            f"Step down no Doom Pool: {die_label(size)} para {die_label(new_size)}. {self._format_doom_pool(pool)}"
        )

    async def _doom_roll(self, interaction: Interaction, dice: Optional[str]) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        campaign_id = campaign["id"]
        pool = await self.db.get_doom_pool(campaign_id)

        if not pool:
            await interaction.response.send_message("Doom Pool esta vazio.")
            return

        if dice is not None:
            try:
                requested_sizes = parse_dice_notation(dice)
            except ValueError as exc:
                await interaction.response.send_message(str(exc))
                return
            roll_sizes = requested_sizes
        else:
            roll_sizes = [d["die_size"] for d in pool]

        results = roll_pool(roll_sizes)

        lines: list[str] = []
        lines.append(f"Doom Pool rolado: {len(results)} dados.")

        dice_parts = []
        for size, value in results:
            dice_parts.append(f"{die_label(size)}: {value}")
        lines.append(", ".join(dice_parts) + ".")

        best_options = calculate_best_options(results)
        if best_options:
            for opt in best_options:
                lines.append(
                    f"{opt['label']}: "
                    f"{die_label(opt['dice'][0][0])} com {opt['dice'][0][1]} "
                    f"mais {die_label(opt['dice'][1][0])} com {opt['dice'][1][1]}, "
                    f"igual a {opt['total']}. "
                    f"Effect die: {die_label(opt['effect_size'])}."
                )
            top = best_options[0]
            lines.append(f"Sugestao de dificuldade: {top['total']}.")
        else:
            non_hitch = [v for _, v in results if v != 1]
            if non_hitch:
                non_hitch.sort(reverse=True)
                if len(non_hitch) >= 2:
                    total = non_hitch[0] + non_hitch[1]
                    lines.append(f"Sugestao de dificuldade (soma dos 2 maiores): {total}.")
                else:
                    lines.append(f"Sugestao de dificuldade: {non_hitch[0]}.")

        await interaction.response.send_message("\n".join(lines))

    async def _doom_spend(self, interaction: Interaction, die: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        if not await self._require_doom_enabled(interaction, campaign):
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        campaign_id = campaign["id"]
        pool = await self.db.get_doom_pool(campaign_id)

        target = None
        for d in pool:
            if d["die_size"] == size:
                target = d
                break

        if target is None:
            await interaction.response.send_message(
                f"Nenhum {die_label(size)} no Doom Pool para gastar."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "DELETE FROM doom_pool_dice WHERE id = ?", (target["id"],)
            )
            await conn.commit()

        pool = await self.db.get_doom_pool(campaign_id)
        await interaction.response.send_message(
            f"Gasto {die_label(size)} do Doom Pool. {self._format_doom_pool(pool)}"
        )

    # ── crisis commands ──────────────────────────────────────────────

    def _register_crisis_commands(self) -> None:
        group = self.crisis_group

        @group.command(name="add", description="Criar uma Crisis Pool na cena ativa.")
        @app_commands.describe(
            name="Nome da crisis pool.",
            dice="Dados iniciais (ex: d8 d6 d10).",
        )
        async def crisis_add(interaction: Interaction, name: str, dice: str) -> None:
            await self._crisis_add(interaction, name, dice)

        @group.command(name="remove", description="Remover um dado de uma Crisis Pool.")
        @app_commands.describe(
            name="Nome da crisis pool.",
            die="Dado para remover (ex: d8).",
        )
        async def crisis_remove(interaction: Interaction, name: str, die: str) -> None:
            await self._crisis_remove(interaction, name, die)

        @group.command(name="roll", description="Rolar uma Crisis Pool.")
        @app_commands.describe(name="Nome da crisis pool.")
        async def crisis_roll(interaction: Interaction, name: str) -> None:
            await self._crisis_roll(interaction, name)

    async def _crisis_add(
        self, interaction: Interaction, name: str, dice: str
    ) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        campaign_id = campaign["id"]
        scene = await self.db.get_active_scene(campaign_id)
        if scene is None:
            await interaction.response.send_message(
                "Nenhuma cena ativa. Inicie uma cena antes de criar crisis pools."
            )
            return

        try:
            die_sizes = parse_dice_notation(dice)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO crisis_pools (campaign_id, scene_id, name) VALUES (?, ?, ?)",
                (campaign_id, scene["id"], name),
            )
            pool_id = cursor.lastrowid
            for size in die_sizes:
                await conn.execute(
                    "INSERT INTO crisis_pool_dice (crisis_pool_id, die_size) VALUES (?, ?)",
                    (pool_id, size),
                )
            await conn.commit()

        dice_labels = [die_label(s) for s in die_sizes]
        await interaction.response.send_message(
            f"Crisis Pool '{name}' criada com {', '.join(dice_labels)}."
        )

    async def _crisis_remove(
        self, interaction: Interaction, name: str, die: str
    ) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        campaign_id = campaign["id"]
        scene = await self.db.get_active_scene(campaign_id)
        if scene is None:
            await interaction.response.send_message("Nenhuma cena ativa.")
            return

        try:
            size = parse_single_die(die)
        except ValueError as exc:
            await interaction.response.send_message(str(exc))
            return

        pools = await self.db.get_crisis_pools(scene["id"])
        target_pool = None
        for p in pools:
            if p["name"].lower() == name.lower():
                target_pool = p
                break

        if target_pool is None:
            await interaction.response.send_message(
                f"Crisis Pool '{name}' nao encontrada na cena atual."
            )
            return

        target_die = None
        for d in target_pool["dice"]:
            if d["die_size"] == size:
                target_die = d
                break

        if target_die is None:
            await interaction.response.send_message(
                f"Nenhum {die_label(size)} na Crisis Pool '{name}'."
            )
            return

        async with self.db.connect() as conn:
            await conn.execute(
                "DELETE FROM crisis_pool_dice WHERE id = ?", (target_die["id"],)
            )
            await conn.commit()

        remaining = [d for d in target_pool["dice"] if d["id"] != target_die["id"]]

        if not remaining:
            async with self.db.connect() as conn:
                await conn.execute(
                    "DELETE FROM crisis_pools WHERE id = ?", (target_pool["id"],)
                )
                await conn.commit()
            await interaction.response.send_message(
                f"Removido {die_label(size)} da Crisis Pool '{name}'. Pool vazia, crisis resolvida."
            )
        else:
            remaining_labels = [die_label(d["die_size"]) for d in remaining]
            await interaction.response.send_message(
                f"Removido {die_label(size)} da Crisis Pool '{name}'. "
                f"Restante: {', '.join(remaining_labels)}."
            )

    async def _crisis_roll(self, interaction: Interaction, name: str) -> None:
        campaign = await self._resolve_campaign(interaction)
        if campaign is None:
            return
        gm = await self._require_gm(interaction, campaign["id"])
        if gm is None:
            return

        campaign_id = campaign["id"]
        scene = await self.db.get_active_scene(campaign_id)
        if scene is None:
            await interaction.response.send_message("Nenhuma cena ativa.")
            return

        pools = await self.db.get_crisis_pools(scene["id"])
        target_pool = None
        for p in pools:
            if p["name"].lower() == name.lower():
                target_pool = p
                break

        if target_pool is None:
            await interaction.response.send_message(
                f"Crisis Pool '{name}' nao encontrada na cena atual."
            )
            return

        if not target_pool["dice"]:
            await interaction.response.send_message(
                f"Crisis Pool '{name}' esta vazia."
            )
            return

        roll_sizes = [d["die_size"] for d in target_pool["dice"]]
        results = roll_pool(roll_sizes)

        lines: list[str] = []
        lines.append(f"Crisis Pool '{name}' rolada: {len(results)} dados.")

        dice_parts = []
        for size, value in results:
            dice_parts.append(f"{die_label(size)}: {value}")
        lines.append(", ".join(dice_parts) + ".")

        best_options = calculate_best_options(results)
        if best_options:
            for opt in best_options:
                lines.append(
                    f"{opt['label']}: "
                    f"{die_label(opt['dice'][0][0])} com {opt['dice'][0][1]} "
                    f"mais {die_label(opt['dice'][1][0])} com {opt['dice'][1][1]}, "
                    f"igual a {opt['total']}. "
                    f"Effect die: {die_label(opt['effect_size'])}."
                )

        await interaction.response.send_message("\n".join(lines))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DoomCog(bot))
