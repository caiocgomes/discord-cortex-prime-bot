import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from cortex_bot.config import settings

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    name TEXT NOT NULL,
    config TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(server_id, channel_id)
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    discord_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    is_gm INTEGER NOT NULL DEFAULT 0,
    is_delegate INTEGER NOT NULL DEFAULT 0,
    pp INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    UNIQUE(campaign_id, discord_user_id)
);

CREATE TABLE IF NOT EXISTS stress_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    UNIQUE(campaign_id, name)
);

CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    die_size INTEGER NOT NULL,
    duration TEXT NOT NULL DEFAULT 'scene'
);

CREATE TABLE IF NOT EXISTS stress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    stress_type_id INTEGER NOT NULL REFERENCES stress_types(id) ON DELETE CASCADE,
    die_size INTEGER NOT NULL,
    UNIQUE(campaign_id, player_id, stress_type_id)
);

CREATE TABLE IF NOT EXISTS trauma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    stress_type_id INTEGER NOT NULL REFERENCES stress_types(id) ON DELETE CASCADE,
    die_size INTEGER NOT NULL,
    UNIQUE(campaign_id, player_id, stress_type_id)
);

CREATE TABLE IF NOT EXISTS complications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    die_size INTEGER NOT NULL,
    scope TEXT NOT NULL DEFAULT 'scene'
);

CREATE TABLE IF NOT EXISTS hero_dice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    die_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS doom_pool_dice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    die_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS crisis_pools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    scene_id INTEGER NOT NULL REFERENCES scenes(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS crisis_pool_dice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crisis_pool_id INTEGER NOT NULL REFERENCES crisis_pools(id) ON DELETE CASCADE,
    die_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS action_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    actor_discord_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_data TEXT NOT NULL DEFAULT '{}',
    inverse_data TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    undone INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_players_campaign ON players(campaign_id);
CREATE INDEX IF NOT EXISTS idx_assets_campaign ON assets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_assets_scene ON assets(scene_id);
CREATE INDEX IF NOT EXISTS idx_stress_player ON stress(campaign_id, player_id);
CREATE INDEX IF NOT EXISTS idx_complications_campaign ON complications(campaign_id);
CREATE INDEX IF NOT EXISTS idx_complications_scene ON complications(scene_id);
CREATE INDEX IF NOT EXISTS idx_doom_pool_campaign ON doom_pool_dice(campaign_id);
CREATE INDEX IF NOT EXISTS idx_action_log_campaign ON action_log(campaign_id, undone);
CREATE INDEX IF NOT EXISTS idx_scenes_active ON scenes(campaign_id, is_active);
"""


class Database:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or settings.db

    async def initialize(self) -> None:
        async with aiosqlite.connect(self.path) as conn:
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA foreign_keys=ON")
            await conn.executescript(SCHEMA)
            try:
                await conn.execute(
                    "ALTER TABLE players ADD COLUMN is_delegate INTEGER NOT NULL DEFAULT 0"
                )
            except Exception:
                pass  # Column already exists
            await conn.commit()
        log.info("Database initialized at %s", self.path)

    @asynccontextmanager
    async def connect(self):
        conn = await aiosqlite.connect(self.path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
        finally:
            await conn.close()

    async def get_campaign_by_channel(
        self, server_id: str, channel_id: str
    ) -> dict | None:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM campaigns WHERE server_id = ? AND channel_id = ?",
                (server_id, channel_id),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            result = dict(row)
            result["config"] = json.loads(result["config"])
            return result

    async def get_campaign_by_id(self, campaign_id: int) -> dict | None:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            result = dict(row)
            result["config"] = json.loads(result["config"])
            return result

    async def get_player(
        self, campaign_id: int, discord_user_id: str
    ) -> dict | None:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM players WHERE campaign_id = ? AND discord_user_id = ?",
                (campaign_id, discord_user_id),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_players(self, campaign_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM players WHERE campaign_id = ? ORDER BY name",
                (campaign_id,),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_active_scene(self, campaign_id: int) -> dict | None:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM scenes WHERE campaign_id = ? AND is_active = 1",
                (campaign_id,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_stress_types(self, campaign_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM stress_types WHERE campaign_id = ? ORDER BY name",
                (campaign_id,),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_player_assets(
        self, campaign_id: int, player_id: int
    ) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM assets WHERE campaign_id = ? AND player_id = ? ORDER BY name",
                (campaign_id, player_id),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_player_stress(
        self, campaign_id: int, player_id: int
    ) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                """SELECT s.*, st.name as stress_type_name
                   FROM stress s
                   JOIN stress_types st ON s.stress_type_id = st.id
                   WHERE s.campaign_id = ? AND s.player_id = ?
                   ORDER BY st.name""",
                (campaign_id, player_id),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_player_trauma(
        self, campaign_id: int, player_id: int
    ) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                """SELECT t.*, st.name as stress_type_name
                   FROM trauma t
                   JOIN stress_types st ON t.stress_type_id = st.id
                   WHERE t.campaign_id = ? AND t.player_id = ?
                   ORDER BY st.name""",
                (campaign_id, player_id),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_player_complications(
        self, campaign_id: int, player_id: int
    ) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM complications WHERE campaign_id = ? AND player_id = ? ORDER BY name",
                (campaign_id, player_id),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_scene_assets(self, scene_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                """SELECT a.*, p.name as player_name
                   FROM assets a
                   LEFT JOIN players p ON a.player_id = p.id
                   WHERE a.scene_id = ? AND a.duration = 'scene'
                   ORDER BY a.name""",
                (scene_id,),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_scene_complications(self, scene_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                """SELECT c.*, p.name as player_name
                   FROM complications c
                   LEFT JOIN players p ON c.player_id = p.id
                   WHERE c.scene_id = ? AND c.scope = 'scene'
                   ORDER BY c.name""",
                (scene_id,),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_doom_pool(self, campaign_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM doom_pool_dice WHERE campaign_id = ? ORDER BY die_size",
                (campaign_id,),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_crisis_pools(self, scene_id: int) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM crisis_pools WHERE scene_id = ?",
                (scene_id,),
            )
            pools = [dict(r) for r in await cursor.fetchall()]
            for pool in pools:
                dice_cursor = await conn.execute(
                    "SELECT * FROM crisis_pool_dice WHERE crisis_pool_id = ? ORDER BY die_size",
                    (pool["id"],),
                )
                pool["dice"] = [dict(r) for r in await dice_cursor.fetchall()]
            return pools

    async def get_hero_dice(
        self, campaign_id: int, player_id: int
    ) -> list[dict]:
        async with self.connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM hero_dice WHERE campaign_id = ? AND player_id = ? ORDER BY die_size",
                (campaign_id, player_id),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def log_action(
        self,
        campaign_id: int,
        actor_discord_id: str,
        action_type: str,
        action_data: dict,
        inverse_data: dict,
    ) -> int:
        async with self.connect() as conn:
            cursor = await conn.execute(
                """INSERT INTO action_log
                   (campaign_id, actor_discord_id, action_type, action_data, inverse_data)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    campaign_id,
                    actor_discord_id,
                    action_type,
                    json.dumps(action_data),
                    json.dumps(inverse_data),
                ),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_last_undoable_action(
        self, campaign_id: int, actor_discord_id: str | None = None
    ) -> dict | None:
        async with self.connect() as conn:
            if actor_discord_id:
                cursor = await conn.execute(
                    """SELECT * FROM action_log
                       WHERE campaign_id = ? AND actor_discord_id = ? AND undone = 0
                       ORDER BY id DESC LIMIT 1""",
                    (campaign_id, actor_discord_id),
                )
            else:
                cursor = await conn.execute(
                    """SELECT * FROM action_log
                       WHERE campaign_id = ? AND undone = 0
                       ORDER BY id DESC LIMIT 1""",
                    (campaign_id,),
                )
            row = await cursor.fetchone()
            if row is None:
                return None
            result = dict(row)
            result["action_data"] = json.loads(result["action_data"])
            result["inverse_data"] = json.loads(result["inverse_data"])
            return result

    async def mark_action_undone(self, action_id: int) -> None:
        async with self.connect() as conn:
            await conn.execute(
                "UPDATE action_log SET undone = 1 WHERE id = ?",
                (action_id,),
            )
            await conn.commit()
