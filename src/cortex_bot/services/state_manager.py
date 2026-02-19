"""State management with action logging for undo support."""

import json

from cortex_bot.models.database import Database
from cortex_bot.models.dice import die_label, step_up, step_down

# Allowlists for the undo system — only these identifiers may appear
# in inverse_data used by execute_undo.  Anything else is rejected.
UNDO_ALLOWED_TABLES = frozenset({
    "assets", "stress", "trauma", "complications", "players",
    "hero_dice", "doom_pool_dice", "crisis_pool_dice",
})
UNDO_ALLOWED_FIELDS = frozenset({"die_size", "pp", "xp"})
UNDO_ALLOWED_COLUMNS = frozenset({
    "campaign_id", "player_id", "scene_id", "name", "die_size",
    "duration", "stress_type_id", "scope",
})


class StateManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def add_asset(
        self,
        campaign_id: int,
        actor_id: str,
        name: str,
        die_size: int,
        player_id: int | None = None,
        scene_id: int | None = None,
        duration: str = "scene",
    ) -> dict:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                """INSERT INTO assets (campaign_id, player_id, scene_id, name, die_size, duration)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (campaign_id, player_id, scene_id, name, die_size, duration),
            )
            asset_id = cursor.lastrowid
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "add_asset",
            {"id": asset_id, "name": name, "die_size": die_size, "player_id": player_id, "duration": duration},
            {"action": "delete", "table": "assets", "id": asset_id},
        )
        return {"id": asset_id, "name": name, "die_size": die_size, "duration": duration}

    async def remove_asset(
        self, campaign_id: int, actor_id: str, asset_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE id = ? AND campaign_id = ?",
                (asset_id, campaign_id),
            )
            asset = await cursor.fetchone()
            if not asset:
                return None
            asset = dict(asset)
            await conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "remove_asset",
            {"id": asset_id, "name": asset["name"]},
            {
                "action": "insert", "table": "assets",
                "data": {
                    "campaign_id": campaign_id, "player_id": asset["player_id"],
                    "scene_id": asset["scene_id"], "name": asset["name"],
                    "die_size": asset["die_size"], "duration": asset["duration"],
                },
            },
        )
        return asset

    async def step_up_asset(
        self, campaign_id: int, actor_id: str, asset_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE id = ? AND campaign_id = ?",
                (asset_id, campaign_id),
            )
            asset = await cursor.fetchone()
            if not asset:
                return None
            asset = dict(asset)
            new_size = step_up(asset["die_size"])
            if new_size is None:
                return {"error": "already_max", "name": asset["name"], "die_size": asset["die_size"]}
            await conn.execute(
                "UPDATE assets SET die_size = ? WHERE id = ?",
                (new_size, asset_id),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "step_up_asset",
            {"id": asset_id, "name": asset["name"], "from": asset["die_size"], "to": new_size},
            {"action": "update", "table": "assets", "id": asset_id, "field": "die_size", "value": asset["die_size"]},
        )
        return {"name": asset["name"], "from": asset["die_size"], "to": new_size}

    async def step_down_asset(
        self, campaign_id: int, actor_id: str, asset_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE id = ? AND campaign_id = ?",
                (asset_id, campaign_id),
            )
            asset = await cursor.fetchone()
            if not asset:
                return None
            asset = dict(asset)
            new_size = step_down(asset["die_size"])
            if new_size is None:
                await conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
                await conn.commit()
                await self.db.log_action(
                    campaign_id, actor_id, "step_down_asset_eliminated",
                    {"id": asset_id, "name": asset["name"], "was": asset["die_size"]},
                    {
                        "action": "insert", "table": "assets",
                        "data": {
                            "campaign_id": campaign_id, "player_id": asset["player_id"],
                            "scene_id": asset["scene_id"], "name": asset["name"],
                            "die_size": asset["die_size"], "duration": asset["duration"],
                        },
                    },
                )
                return {"name": asset["name"], "eliminated": True, "was": asset["die_size"]}
            await conn.execute(
                "UPDATE assets SET die_size = ? WHERE id = ?",
                (new_size, asset_id),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "step_down_asset",
            {"id": asset_id, "name": asset["name"], "from": asset["die_size"], "to": new_size},
            {"action": "update", "table": "assets", "id": asset_id, "field": "die_size", "value": asset["die_size"]},
        )
        return {"name": asset["name"], "from": asset["die_size"], "to": new_size}

    async def add_stress(
        self, campaign_id: int, actor_id: str, player_id: int,
        stress_type_id: int, die_size: int, player_name: str = "", type_name: str = "",
    ) -> dict:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM stress WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign_id, player_id, stress_type_id),
            )
            existing = await cursor.fetchone()

            if existing:
                existing = dict(existing)
                if die_size > existing["die_size"]:
                    old_size = existing["die_size"]
                    await conn.execute(
                        "UPDATE stress SET die_size = ? WHERE id = ?",
                        (die_size, existing["id"]),
                    )
                    await conn.commit()
                    await self.db.log_action(
                        campaign_id, actor_id, "replace_stress",
                        {"id": existing["id"], "player": player_name, "type": type_name, "from": old_size, "to": die_size},
                        {"action": "update", "table": "stress", "id": existing["id"], "field": "die_size", "value": old_size},
                    )
                    return {"player": player_name, "type": type_name, "action": "replaced", "from": old_size, "to": die_size}
                else:
                    new_size = step_up(existing["die_size"])
                    if new_size is None:
                        await conn.commit()
                        return {
                            "player": player_name, "type": type_name,
                            "action": "stressed_out", "die_size": 12,
                        }
                    await conn.execute(
                        "UPDATE stress SET die_size = ? WHERE id = ?",
                        (new_size, existing["id"]),
                    )
                    await conn.commit()
                    await self.db.log_action(
                        campaign_id, actor_id, "step_up_stress",
                        {"id": existing["id"], "player": player_name, "type": type_name, "from": existing["die_size"], "to": new_size},
                        {"action": "update", "table": "stress", "id": existing["id"], "field": "die_size", "value": existing["die_size"]},
                    )
                    return {"player": player_name, "type": type_name, "action": "stepped_up", "from": existing["die_size"], "to": new_size}
            else:
                cursor = await conn.execute(
                    "INSERT INTO stress (campaign_id, player_id, stress_type_id, die_size) VALUES (?, ?, ?, ?)",
                    (campaign_id, player_id, stress_type_id, die_size),
                )
                stress_id = cursor.lastrowid
                await conn.commit()
                await self.db.log_action(
                    campaign_id, actor_id, "add_stress",
                    {"id": stress_id, "player": player_name, "type": type_name, "die_size": die_size},
                    {"action": "delete", "table": "stress", "id": stress_id},
                )
                return {"player": player_name, "type": type_name, "action": "added", "die_size": die_size}

    async def remove_stress(
        self, campaign_id: int, actor_id: str, player_id: int,
        stress_type_id: int, player_name: str = "", type_name: str = "",
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM stress WHERE campaign_id = ? AND player_id = ? AND stress_type_id = ?",
                (campaign_id, player_id, stress_type_id),
            )
            existing = await cursor.fetchone()
            if not existing:
                return None
            existing = dict(existing)
            await conn.execute("DELETE FROM stress WHERE id = ?", (existing["id"],))
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "remove_stress",
            {"id": existing["id"], "player": player_name, "type": type_name, "die_size": existing["die_size"]},
            {
                "action": "insert", "table": "stress",
                "data": {
                    "campaign_id": campaign_id, "player_id": player_id,
                    "stress_type_id": stress_type_id, "die_size": existing["die_size"],
                },
            },
        )
        return {"player": player_name, "type": type_name, "die_size": existing["die_size"]}

    async def add_complication(
        self, campaign_id: int, actor_id: str, name: str, die_size: int,
        player_id: int | None = None, scene_id: int | None = None,
        scope: str = "scene", player_name: str = "",
    ) -> dict:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                """INSERT INTO complications (campaign_id, player_id, scene_id, name, die_size, scope)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (campaign_id, player_id, scene_id, name, die_size, scope),
            )
            comp_id = cursor.lastrowid
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "add_complication",
            {"id": comp_id, "name": name, "die_size": die_size, "player": player_name},
            {"action": "delete", "table": "complications", "id": comp_id},
        )
        return {"id": comp_id, "name": name, "die_size": die_size, "player": player_name}

    async def remove_complication(
        self, campaign_id: int, actor_id: str, comp_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE id = ? AND campaign_id = ?",
                (comp_id, campaign_id),
            )
            comp = await cursor.fetchone()
            if not comp:
                return None
            comp = dict(comp)
            await conn.execute("DELETE FROM complications WHERE id = ?", (comp_id,))
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "remove_complication",
            {"id": comp_id, "name": comp["name"]},
            {
                "action": "insert", "table": "complications",
                "data": {
                    "campaign_id": campaign_id, "player_id": comp["player_id"],
                    "scene_id": comp["scene_id"], "name": comp["name"],
                    "die_size": comp["die_size"], "scope": comp["scope"],
                },
            },
        )
        return comp

    async def step_up_complication(
        self, campaign_id: int, actor_id: str, comp_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE id = ? AND campaign_id = ?",
                (comp_id, campaign_id),
            )
            comp = await cursor.fetchone()
            if not comp:
                return None
            comp = dict(comp)
            new_size = step_up(comp["die_size"])
            if new_size is None:
                return {"name": comp["name"], "taken_out": True, "die_size": 12}
            await conn.execute(
                "UPDATE complications SET die_size = ? WHERE id = ?",
                (new_size, comp_id),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "step_up_complication",
            {"id": comp_id, "name": comp["name"], "from": comp["die_size"], "to": new_size},
            {"action": "update", "table": "complications", "id": comp_id, "field": "die_size", "value": comp["die_size"]},
        )
        return {"name": comp["name"], "from": comp["die_size"], "to": new_size}

    async def step_down_complication(
        self, campaign_id: int, actor_id: str, comp_id: int
    ) -> dict | None:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE id = ? AND campaign_id = ?",
                (comp_id, campaign_id),
            )
            comp = await cursor.fetchone()
            if not comp:
                return None
            comp = dict(comp)
            new_size = step_down(comp["die_size"])
            if new_size is None:
                await conn.execute("DELETE FROM complications WHERE id = ?", (comp_id,))
                await conn.commit()
                await self.db.log_action(
                    campaign_id, actor_id, "step_down_complication_eliminated",
                    {"id": comp_id, "name": comp["name"], "was": comp["die_size"]},
                    {
                        "action": "insert", "table": "complications",
                        "data": {
                            "campaign_id": campaign_id, "player_id": comp["player_id"],
                            "scene_id": comp["scene_id"], "name": comp["name"],
                            "die_size": comp["die_size"], "scope": comp["scope"],
                        },
                    },
                )
                return {"name": comp["name"], "eliminated": True, "was": comp["die_size"]}
            await conn.execute(
                "UPDATE complications SET die_size = ? WHERE id = ?",
                (new_size, comp_id),
            )
            await conn.commit()

        await self.db.log_action(
            campaign_id, actor_id, "step_down_complication",
            {"id": comp_id, "name": comp["name"], "from": comp["die_size"], "to": new_size},
            {"action": "update", "table": "complications", "id": comp_id, "field": "die_size", "value": comp["die_size"]},
        )
        return {"name": comp["name"], "from": comp["die_size"], "to": new_size}

    async def update_pp(
        self, campaign_id: int, actor_id: str, player_id: int,
        amount: int, player_name: str = "",
    ) -> dict:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT pp FROM players WHERE id = ?", (player_id,)
            )
            row = await cursor.fetchone()
            old_pp = row["pp"]
            new_pp = old_pp + amount
            if new_pp < 0:
                return {"error": "insufficient", "player": player_name, "current": old_pp, "requested": abs(amount)}
            await conn.execute(
                "UPDATE players SET pp = ? WHERE id = ?", (new_pp, player_id)
            )
            await conn.commit()

        action_type = "add_pp" if amount > 0 else "remove_pp"
        await self.db.log_action(
            campaign_id, actor_id, action_type,
            {"player_id": player_id, "player": player_name, "amount": amount, "from": old_pp, "to": new_pp},
            {"action": "update", "table": "players", "id": player_id, "field": "pp", "value": old_pp},
        )
        return {"player": player_name, "from": old_pp, "to": new_pp}

    async def update_xp(
        self, campaign_id: int, actor_id: str, player_id: int,
        amount: int, player_name: str = "",
    ) -> dict:
        async with self.db.connect() as conn:
            cursor = await conn.execute(
                "SELECT xp FROM players WHERE id = ?", (player_id,)
            )
            row = await cursor.fetchone()
            old_xp = row["xp"]
            new_xp = old_xp + amount
            if new_xp < 0:
                return {"error": "insufficient", "player": player_name, "current": old_xp, "requested": abs(amount)}
            await conn.execute(
                "UPDATE players SET xp = ? WHERE id = ?", (new_xp, player_id)
            )
            await conn.commit()

        action_type = "add_xp" if amount > 0 else "remove_xp"
        await self.db.log_action(
            campaign_id, actor_id, action_type,
            {"player_id": player_id, "player": player_name, "amount": amount, "from": old_xp, "to": new_xp},
            {"action": "update", "table": "players", "id": player_id, "field": "xp", "value": old_xp},
        )
        return {"player": player_name, "from": old_xp, "to": new_xp}

    async def execute_undo(self, inverse_data: dict) -> None:
        """Execute an inverse action to undo a previous operation."""
        action = inverse_data["action"]
        table = inverse_data["table"]

        if table not in UNDO_ALLOWED_TABLES:
            raise ValueError(f"Undo blocked: invalid table '{table}'")

        async with self.db.connect() as conn:
            if action == "delete":
                await conn.execute(
                    f"DELETE FROM {table} WHERE id = ?",
                    (inverse_data["id"],),
                )
            elif action == "insert":
                data = inverse_data["data"]
                bad_cols = set(data.keys()) - UNDO_ALLOWED_COLUMNS
                if bad_cols:
                    raise ValueError(f"Undo blocked: invalid columns {bad_cols}")
                columns = ", ".join(data.keys())
                placeholders = ", ".join("?" for _ in data)
                await conn.execute(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                    tuple(data.values()),
                )
            elif action == "update":
                field = inverse_data["field"]
                if field not in UNDO_ALLOWED_FIELDS:
                    raise ValueError(f"Undo blocked: invalid field '{field}'")
                await conn.execute(
                    f"UPDATE {table} SET {field} = ? WHERE id = ?",
                    (inverse_data["value"], inverse_data["id"]),
                )
            else:
                raise ValueError(f"Undo blocked: invalid action '{action}'")
            await conn.commit()
