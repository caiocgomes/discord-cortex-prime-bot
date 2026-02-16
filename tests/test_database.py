"""Tests for models/database.py — query functions tested directly."""

import pytest

from cortex_bot.models.database import Database


@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    database = Database(path=db_path)
    await database.initialize()
    return database


@pytest.fixture
async def seeded_db(db):
    """DB with a campaign, players, scene, stress_types, and some data."""
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
            ("srv1", "ch1", "Test Campaign", '{"doom_pool": true}'),
        )
        campaign_id = cursor.lastrowid

        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "user1", "Alice", 0, 3, 5),
        )
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "gm1", "GameMaster", 1, 5, 0),
        )
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (campaign_id, "Physical"),
        )
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (campaign_id, "Mental"),
        )
        await conn.commit()
    return db, campaign_id


class TestGetCampaignByChannel:
    async def test_existing_campaign(self, seeded_db):
        db, _ = seeded_db
        result = await db.get_campaign_by_channel("srv1", "ch1")
        assert result is not None
        assert result["name"] == "Test Campaign"
        assert isinstance(result["config"], dict)
        assert result["config"]["doom_pool"] is True

    async def test_nonexistent_campaign(self, seeded_db):
        db, _ = seeded_db
        result = await db.get_campaign_by_channel("srv1", "ch_nonexistent")
        assert result is None


class TestGetActiveScene:
    async def test_no_active_scene(self, seeded_db):
        db, campaign_id = seeded_db
        result = await db.get_active_scene(campaign_id)
        assert result is None

    async def test_with_active_scene(self, seeded_db):
        db, campaign_id = seeded_db
        async with db.connect() as conn:
            await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, ?)",
                (campaign_id, "Tavern Fight", 1),
            )
            await conn.commit()
        result = await db.get_active_scene(campaign_id)
        assert result is not None
        assert result["name"] == "Tavern Fight"

    async def test_inactive_scene_not_returned(self, seeded_db):
        db, campaign_id = seeded_db
        async with db.connect() as conn:
            await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, ?)",
                (campaign_id, "Old Scene", 0),
            )
            await conn.commit()
        result = await db.get_active_scene(campaign_id)
        assert result is None


class TestGetCrisisPools:
    async def test_empty(self, seeded_db):
        db, campaign_id = seeded_db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, ?)",
                (campaign_id, "Scene1", 1),
            )
            scene_id = cursor.lastrowid
            await conn.commit()
        result = await db.get_crisis_pools(scene_id)
        assert result == []

    async def test_with_dice(self, seeded_db):
        db, campaign_id = seeded_db
        async with db.connect() as conn:
            cursor = await conn.execute(
                "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, ?)",
                (campaign_id, "Scene1", 1),
            )
            scene_id = cursor.lastrowid
            cursor = await conn.execute(
                "INSERT INTO crisis_pools (campaign_id, scene_id, name) VALUES (?, ?, ?)",
                (campaign_id, scene_id, "Flood"),
            )
            pool_id = cursor.lastrowid
            await conn.execute(
                "INSERT INTO crisis_pool_dice (crisis_pool_id, die_size) VALUES (?, ?)",
                (pool_id, 6),
            )
            await conn.execute(
                "INSERT INTO crisis_pool_dice (crisis_pool_id, die_size) VALUES (?, ?)",
                (pool_id, 8),
            )
            await conn.commit()

        result = await db.get_crisis_pools(scene_id)
        assert len(result) == 1
        assert result[0]["name"] == "Flood"
        assert len(result[0]["dice"]) == 2
        sizes = [d["die_size"] for d in result[0]["dice"]]
        assert sizes == [6, 8]


class TestGetLastUndoableAction:
    async def test_no_actions(self, seeded_db):
        db, campaign_id = seeded_db
        result = await db.get_last_undoable_action(campaign_id)
        assert result is None

    async def test_returns_last(self, seeded_db):
        db, campaign_id = seeded_db
        await db.log_action(campaign_id, "user1", "add_asset", {"name": "first"}, {"action": "delete"})
        await db.log_action(campaign_id, "user1", "add_asset", {"name": "second"}, {"action": "delete"})
        result = await db.get_last_undoable_action(campaign_id)
        assert result["action_data"]["name"] == "second"

    async def test_filter_by_actor(self, seeded_db):
        db, campaign_id = seeded_db
        await db.log_action(campaign_id, "user1", "add_asset", {"name": "alice_action"}, {"action": "delete"})
        await db.log_action(campaign_id, "gm1", "add_asset", {"name": "gm_action"}, {"action": "delete"})
        result = await db.get_last_undoable_action(campaign_id, actor_discord_id="user1")
        assert result["action_data"]["name"] == "alice_action"

    async def test_no_filter_returns_any_actor(self, seeded_db):
        db, campaign_id = seeded_db
        await db.log_action(campaign_id, "user1", "add_asset", {"name": "alice"}, {"action": "delete"})
        await db.log_action(campaign_id, "gm1", "add_asset", {"name": "gm"}, {"action": "delete"})
        result = await db.get_last_undoable_action(campaign_id)
        assert result["action_data"]["name"] == "gm"


class TestLogActionAndMarkUndone:
    async def test_log_returns_id(self, seeded_db):
        db, campaign_id = seeded_db
        action_id = await db.log_action(
            campaign_id, "user1", "test_action",
            {"key": "value"}, {"action": "delete"},
        )
        assert isinstance(action_id, int)
        assert action_id > 0

    async def test_mark_undone_excludes_from_last(self, seeded_db):
        db, campaign_id = seeded_db
        id1 = await db.log_action(campaign_id, "user1", "first", {"n": 1}, {"action": "delete"})
        id2 = await db.log_action(campaign_id, "user1", "second", {"n": 2}, {"action": "delete"})
        await db.mark_action_undone(id2)
        result = await db.get_last_undoable_action(campaign_id)
        assert result["id"] == id1

    async def test_all_undone_returns_none(self, seeded_db):
        db, campaign_id = seeded_db
        id1 = await db.log_action(campaign_id, "user1", "only", {"n": 1}, {"action": "delete"})
        await db.mark_action_undone(id1)
        result = await db.get_last_undoable_action(campaign_id)
        assert result is None


class TestGetPlayer:
    async def test_existing_player(self, seeded_db):
        db, campaign_id = seeded_db
        result = await db.get_player(campaign_id, "user1")
        assert result is not None
        assert result["name"] == "Alice"
        assert result["pp"] == 3
        assert result["xp"] == 5

    async def test_nonexistent_player(self, seeded_db):
        db, campaign_id = seeded_db
        result = await db.get_player(campaign_id, "nobody")
        assert result is None


class TestGetPlayers:
    async def test_returns_all_ordered(self, seeded_db):
        db, campaign_id = seeded_db
        result = await db.get_players(campaign_id)
        assert len(result) == 2
        names = [p["name"] for p in result]
        assert names == ["Alice", "GameMaster"]
