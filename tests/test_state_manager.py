import os
import pytest

from cortex_bot.models.database import Database
from cortex_bot.services.state_manager import StateManager


@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    database = Database(path=db_path)
    await database.initialize()
    return database


@pytest.fixture
async def campaign(db):
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
            ("srv1", "ch1", "Test Campaign", '{"doom_pool": true, "best_mode": true}'),
        )
        campaign_id = cursor.lastrowid
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "user1", "Alice", 0, 3, 0),
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
    return campaign_id


@pytest.fixture
async def alice(db, campaign):
    player = await db.get_player(campaign, "user1")
    return player


@pytest.fixture
async def sm(db):
    return StateManager(db)


class TestAssets:
    async def test_add_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Big Wrench", 6, player_id=alice["id"])
        assert result["name"] == "Big Wrench"
        assert result["die_size"] == 6
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 1
        assert assets[0]["name"] == "Big Wrench"

    async def test_step_up_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Shield", 6, player_id=alice["id"])
        step = await sm.step_up_asset(campaign, "user1", result["id"])
        assert step["from"] == 6
        assert step["to"] == 8

    async def test_step_up_d12_returns_error(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "MaxShield", 12, player_id=alice["id"])
        step = await sm.step_up_asset(campaign, "user1", result["id"])
        assert step["error"] == "already_max"

    async def test_step_down_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Torch", 8, player_id=alice["id"])
        step = await sm.step_down_asset(campaign, "user1", result["id"])
        assert step["from"] == 8
        assert step["to"] == 6

    async def test_step_down_d4_eliminates(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Weak", 4, player_id=alice["id"])
        step = await sm.step_down_asset(campaign, "user1", result["id"])
        assert step["eliminated"] is True
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 0

    async def test_remove_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Temp", 6, player_id=alice["id"])
        removed = await sm.remove_asset(campaign, "user1", result["id"])
        assert removed["name"] == "Temp"
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 0


class TestStress:
    async def _get_stress_type_id(self, db, campaign, name):
        types = await db.get_stress_types(campaign)
        return next(t["id"] for t in types if t["name"] == name)

    async def test_add_new_stress(self, sm, db, campaign, alice):
        st_id = await self._get_stress_type_id(db, campaign, "Physical")
        result = await sm.add_stress(
            campaign, "gm1", alice["id"], st_id, 8,
            player_name="Alice", type_name="Physical",
        )
        assert result["action"] == "added"
        assert result["die_size"] == 8

    async def test_stress_replaces_smaller(self, sm, db, campaign, alice):
        st_id = await self._get_stress_type_id(db, campaign, "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 6, "Alice", "Physical")
        result = await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        assert result["action"] == "replaced"
        assert result["from"] == 6
        assert result["to"] == 8

    async def test_stress_steps_up_equal_or_larger(self, sm, db, campaign, alice):
        st_id = await self._get_stress_type_id(db, campaign, "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        result = await sm.add_stress(campaign, "gm1", alice["id"], st_id, 6, "Alice", "Physical")
        assert result["action"] == "stepped_up"
        assert result["from"] == 8
        assert result["to"] == 10

    async def test_stress_beyond_d12(self, sm, db, campaign, alice):
        st_id = await self._get_stress_type_id(db, campaign, "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 12, "Alice", "Physical")
        result = await sm.add_stress(campaign, "gm1", alice["id"], st_id, 6, "Alice", "Physical")
        assert result["action"] == "stressed_out"

    async def test_remove_stress(self, sm, db, campaign, alice):
        st_id = await self._get_stress_type_id(db, campaign, "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        result = await sm.remove_stress(campaign, "gm1", alice["id"], st_id, "Alice", "Physical")
        assert result["die_size"] == 8
        stress = await db.get_player_stress(campaign, alice["id"])
        assert len(stress) == 0


class TestComplications:
    async def test_add_complication(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Broken Arm", 6,
            player_id=alice["id"], player_name="Alice",
        )
        assert result["name"] == "Broken Arm"

    async def test_step_up_complication(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Broken Arm", 6,
            player_id=alice["id"], player_name="Alice",
        )
        step = await sm.step_up_complication(campaign, "gm1", result["id"])
        assert step["from"] == 6
        assert step["to"] == 8

    async def test_step_up_beyond_d12_taken_out(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Fatal", 12,
            player_id=alice["id"], player_name="Alice",
        )
        step = await sm.step_up_complication(campaign, "gm1", result["id"])
        assert step["taken_out"] is True

    async def test_step_down_d4_eliminates(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Minor", 4,
            player_id=alice["id"], player_name="Alice",
        )
        step = await sm.step_down_complication(campaign, "gm1", result["id"])
        assert step["eliminated"] is True

    async def test_step_down_normal(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Hurt", 8,
            player_id=alice["id"], player_name="Alice",
        )
        step = await sm.step_down_complication(campaign, "gm1", result["id"])
        assert step["from"] == 8
        assert step["to"] == 6
        comps = await db.get_player_complications(campaign, alice["id"])
        assert len(comps) == 1
        assert comps[0]["die_size"] == 6

    async def test_remove_complication(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Burn", 6,
            player_id=alice["id"], player_name="Alice",
        )
        removed = await sm.remove_complication(campaign, "gm1", result["id"])
        assert removed["name"] == "Burn"
        comps = await db.get_player_complications(campaign, alice["id"])
        assert len(comps) == 0

    async def test_remove_nonexistent_complication(self, sm, db, campaign):
        result = await sm.remove_complication(campaign, "gm1", 9999)
        assert result is None


class TestPlotPoints:
    async def test_add_pp(self, sm, db, campaign, alice):
        result = await sm.update_pp(campaign, "user1", alice["id"], 2, "Alice")
        assert result["from"] == 3
        assert result["to"] == 5

    async def test_remove_pp(self, sm, db, campaign, alice):
        result = await sm.update_pp(campaign, "user1", alice["id"], -2, "Alice")
        assert result["from"] == 3
        assert result["to"] == 1

    async def test_pp_insufficient(self, sm, db, campaign, alice):
        result = await sm.update_pp(campaign, "user1", alice["id"], -10, "Alice")
        assert result["error"] == "insufficient"


class TestXP:
    async def test_add_xp(self, sm, db, campaign, alice):
        result = await sm.update_xp(campaign, "user1", alice["id"], 3, "Alice")
        assert result["from"] == 0
        assert result["to"] == 3

    async def test_remove_xp(self, sm, db, campaign, alice):
        await sm.update_xp(campaign, "user1", alice["id"], 5, "Alice")
        result = await sm.update_xp(campaign, "user1", alice["id"], -2, "Alice")
        assert result["from"] == 5
        assert result["to"] == 3

    async def test_xp_insufficient(self, sm, db, campaign, alice):
        result = await sm.update_xp(campaign, "user1", alice["id"], -1, "Alice")
        assert result["error"] == "insufficient"
        assert result["current"] == 0


class TestUndo:
    async def test_undo_add_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Undo Test", 8, player_id=alice["id"])
        action = await db.get_last_undoable_action(campaign, "user1")
        assert action is not None
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 0

    async def test_undo_remove_asset(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "Restore Me", 6, player_id=alice["id"])
        await sm.remove_asset(campaign, "user1", result["id"])
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 0
        action = await db.get_last_undoable_action(campaign, "user1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        assets = await db.get_player_assets(campaign, alice["id"])
        assert len(assets) == 1
        assert assets[0]["name"] == "Restore Me"

    async def test_undo_step_up(self, sm, db, campaign, alice):
        result = await sm.add_asset(campaign, "user1", "StepTest", 6, player_id=alice["id"])
        await sm.step_up_asset(campaign, "user1", result["id"])
        action = await db.get_last_undoable_action(campaign, "user1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        assets = await db.get_player_assets(campaign, alice["id"])
        assert assets[0]["die_size"] == 6

    async def test_undo_pp_change(self, sm, db, campaign, alice):
        await sm.update_pp(campaign, "user1", alice["id"], 5, "Alice")
        action = await db.get_last_undoable_action(campaign, "user1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        player = await db.get_player(campaign, "user1")
        assert player["pp"] == 3

    async def test_undo_add_stress(self, sm, db, campaign, alice):
        types = await db.get_stress_types(campaign)
        st_id = next(t["id"] for t in types if t["name"] == "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        stress = await db.get_player_stress(campaign, alice["id"])
        assert len(stress) == 0

    async def test_undo_remove_stress(self, sm, db, campaign, alice):
        types = await db.get_stress_types(campaign)
        st_id = next(t["id"] for t in types if t["name"] == "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        await sm.remove_stress(campaign, "gm1", alice["id"], st_id, "Alice", "Physical")
        stress = await db.get_player_stress(campaign, alice["id"])
        assert len(stress) == 0
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        stress = await db.get_player_stress(campaign, alice["id"])
        assert len(stress) == 1
        assert stress[0]["die_size"] == 8

    async def test_undo_step_up_stress(self, sm, db, campaign, alice):
        types = await db.get_stress_types(campaign)
        st_id = next(t["id"] for t in types if t["name"] == "Physical")
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 8, "Alice", "Physical")
        # Apply equal die to trigger step up (8 -> 10)
        await sm.add_stress(campaign, "gm1", alice["id"], st_id, 6, "Alice", "Physical")
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        stress = await db.get_player_stress(campaign, alice["id"])
        assert stress[0]["die_size"] == 8

    async def test_undo_add_complication(self, sm, db, campaign, alice):
        await sm.add_complication(
            campaign, "gm1", "Broken Arm", 6,
            player_id=alice["id"], player_name="Alice",
        )
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        comps = await db.get_player_complications(campaign, alice["id"])
        assert len(comps) == 0

    async def test_undo_remove_complication(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Burn", 6,
            player_id=alice["id"], player_name="Alice",
        )
        await sm.remove_complication(campaign, "gm1", result["id"])
        comps = await db.get_player_complications(campaign, alice["id"])
        assert len(comps) == 0
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        comps = await db.get_player_complications(campaign, alice["id"])
        assert len(comps) == 1
        assert comps[0]["name"] == "Burn"

    async def test_undo_step_up_complication(self, sm, db, campaign, alice):
        result = await sm.add_complication(
            campaign, "gm1", "Wound", 6,
            player_id=alice["id"], player_name="Alice",
        )
        await sm.step_up_complication(campaign, "gm1", result["id"])
        action = await db.get_last_undoable_action(campaign, "gm1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        comps = await db.get_player_complications(campaign, alice["id"])
        assert comps[0]["die_size"] == 6

    async def test_undo_xp_change(self, sm, db, campaign, alice):
        await sm.update_xp(campaign, "user1", alice["id"], 5, "Alice")
        action = await db.get_last_undoable_action(campaign, "user1")
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])
        player = await db.get_player(campaign, "user1")
        assert player["xp"] == 0
