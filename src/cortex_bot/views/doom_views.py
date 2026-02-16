"""Doom pool and crisis pool views."""

import re
import uuid

import discord

from cortex_bot.views.base import CortexView, make_custom_id, check_gm_permission, add_die_buttons
from cortex_bot.models.dice import die_label, parse_single_die
from cortex_bot.services.roller import roll_pool, calculate_best_options


class DoomAddStartButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"cortex:doom_add_start:(?P<campaign_id>\d+)",
):
    """Button to start doom add: select die -> execute."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            discord.ui.Button(
                label="Doom Add",
                style=discord.ButtonStyle.danger,
                custom_id=make_custom_id("doom_add_start", campaign_id),
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["campaign_id"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        campaign = await db.get_campaign_by_id(self.campaign_id)
        if campaign is None or not campaign["config"].get("doom_pool", False):
            await interaction.response.send_message(
                "Doom Pool nao esta habilitado nesta campanha.", ephemeral=True
            )
            return

        view = DoomDieSelectView(self.campaign_id, str(interaction.user.id))

        async def on_die(interaction: discord.Interaction, die_size: int) -> None:
            await view._on_die_selected(interaction, die_size)

        add_die_buttons(view, on_die)
        await interaction.response.send_message(
            "Selecione o dado para adicionar ao Doom Pool.",
            view=view,
            ephemeral=True,
        )


class DoomDieSelectView(CortexView):
    """Select die to add to doom pool."""

    def __init__(self, campaign_id: int, actor_id: str) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id

    async def _on_die_selected(
        self, interaction: discord.Interaction, die_size: int
    ) -> None:
        db = interaction.client.db

        async with db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO doom_pool_dice (campaign_id, die_size) VALUES (?, ?)",
                (self.campaign_id, die_size),
            )
            doom_die_id = cursor.lastrowid
            await conn.commit()

        await db.log_action(
            self.campaign_id,
            self.actor_id,
            "doom_add",
            {"die_size": die_size},
            {"action": "delete", "table": "doom_pool_dice", "id": doom_die_id},
        )

        pool = await db.get_doom_pool(self.campaign_id)
        labels = [die_label(d["die_size"]) for d in pool]
        pool_str = ", ".join(labels) if labels else "vazio"
        msg = f"Adicionado {die_label(die_size)} ao Doom Pool. Doom Pool: {pool_str}."

        view = PostDoomActionView(self.campaign_id)
        await interaction.response.edit_message(content=msg, view=None)
        await interaction.followup.send(msg, view=view)


class DoomRemoveButton(discord.ui.Button):
    """Non-persistent button for doom remove (in post-action view)."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            label="Doom Remove",
            style=discord.ButtonStyle.secondary,
            custom_id=make_custom_id("doom_remove_btn", campaign_id),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        pool = await db.get_doom_pool(self.campaign_id)
        if not pool:
            await interaction.response.send_message(
                "Doom Pool esta vazio.", ephemeral=True
            )
            return

        # Deduplicate die sizes for buttons
        seen: set[int] = set()
        unique_sizes: list[int] = []
        for d in pool:
            if d["die_size"] not in seen:
                seen.add(d["die_size"])
                unique_sizes.append(d["die_size"])

        view = DoomRemoveSelectView(self.campaign_id, str(interaction.user.id))

        uid = uuid.uuid4().hex[:8]
        for size in sorted(unique_sizes):
            btn = discord.ui.Button(
                label=die_label(size),
                style=discord.ButtonStyle.primary,
                custom_id=f"ephemeral:doom_remove:{size}:{uid}",
            )

            async def make_cb(
                interaction: discord.Interaction,
                _btn: discord.ui.Button = btn,
                _size: int = size,
            ) -> None:
                await view._on_die_selected(interaction, _size)

            btn.callback = make_cb
            view.add_item(btn)

        await interaction.response.send_message(
            "Selecione o dado para remover do Doom Pool.",
            view=view,
            ephemeral=True,
        )


class DoomRemoveSelectView(CortexView):
    """Handles die removal from doom pool."""

    def __init__(self, campaign_id: int, actor_id: str) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.actor_id = actor_id

    async def _on_die_selected(
        self, interaction: discord.Interaction, size: int
    ) -> None:
        db = interaction.client.db
        pool = await db.get_doom_pool(self.campaign_id)

        target = None
        for d in pool:
            if d["die_size"] == size:
                target = d
                break

        if target is None:
            await interaction.response.edit_message(
                content=f"Nenhum {die_label(size)} no Doom Pool.", view=None
            )
            return

        async with db.connect() as conn:
            await conn.execute(
                "DELETE FROM doom_pool_dice WHERE id = ?", (target["id"],)
            )
            await conn.commit()

        await db.log_action(
            self.campaign_id,
            self.actor_id,
            "doom_remove",
            {"die_size": size},
            {
                "action": "insert",
                "table": "doom_pool_dice",
                "data": {"campaign_id": self.campaign_id, "die_size": size},
            },
        )

        pool = await db.get_doom_pool(self.campaign_id)
        labels = [die_label(d["die_size"]) for d in pool]
        pool_str = ", ".join(labels) if labels else "vazio"
        msg = f"Removido {die_label(size)} do Doom Pool. Doom Pool: {pool_str}."

        view = PostDoomActionView(self.campaign_id)
        await interaction.response.edit_message(content=msg, view=None)
        await interaction.followup.send(msg, view=view)


class DoomRollButton(discord.ui.Button):
    """Non-persistent button for doom roll."""

    def __init__(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        super().__init__(
            label="Doom Roll",
            style=discord.ButtonStyle.primary,
            custom_id=make_custom_id("doom_roll_btn", campaign_id),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        gm = await check_gm_permission(interaction, self.campaign_id)
        if gm is None:
            return

        db = interaction.client.db
        pool = await db.get_doom_pool(self.campaign_id)
        if not pool:
            await interaction.response.send_message(
                "Doom Pool esta vazio.", ephemeral=True
            )
            return

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

        view = PostDoomActionView(self.campaign_id)
        await interaction.response.send_message("\n".join(lines), view=view)


class PostDoomActionView(CortexView):
    """View after doom action: Doom Add, Doom Remove, Doom Roll."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        self.add_item(DoomAddStartButton(campaign_id))
        self.add_item(DoomRemoveButton(campaign_id))
        self.add_item(DoomRollButton(campaign_id))


class PostCrisisActionView(CortexView):
    """View after crisis action. Placeholder for crisis-specific buttons."""

    def __init__(self, campaign_id: int) -> None:
        super().__init__()
        from cortex_bot.views.common import CampaignInfoButton

        self.add_item(CampaignInfoButton(campaign_id))
