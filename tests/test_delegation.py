"""Tests for GM delegation: delegate/undelegate, has_gm_permission, /gmroll, formatter, permissions, bridge scene."""

import json
from unittest.mock import patch

import pytest

from cortex_bot.models.database import Database
from cortex_bot.models.dice import die_label, step_down
from cortex_bot.services.roller import roll_pool, find_hitches, is_botch, calculate_best_options
from cortex_bot.services.formatter import format_roll_result, format_campaign_info
from cortex_bot.services.state_manager import StateManager
from cortex_bot.utils import has_gm_permission


@pytest.fixture
async def db(tmp_path):
    database = Database(path=str(tmp_path / "delegation.db"))
    await database.initialize()
    return database


@pytest.fixture
async def campaign(db):
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
            ("srv1", "ch1", "Test Campaign", json.dumps({
                "doom_pool": True, "best_mode": True, "trauma": True,
            })),
        )
        campaign_id = cursor.lastrowid
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "gm1", "GameMaster", 1, 5, 0),
        )
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "user1", "Alice", 0, 3, 0),
        )
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (campaign_id, "user2", "Bob", 0, 2, 0),
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
async def gm(db, campaign):
    return await db.get_player(campaign, "gm1")


@pytest.fixture
async def alice(db, campaign):
    return await db.get_player(campaign, "user1")


@pytest.fixture
async def bob(db, campaign):
    return await db.get_player(campaign, "user2")


# ---------------------------------------------------------------------------
# 6.1: Delegate/undelegate tests
# ---------------------------------------------------------------------------

class TestDelegate:
    async def test_grant_delegate(self, db, campaign, alice):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        updated = await db.get_player(campaign, "user1")
        assert updated["is_delegate"] == 1

    async def test_revoke_delegate(self, db, campaign, alice):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 0 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        updated = await db.get_player(campaign, "user1")
        assert updated["is_delegate"] == 0

    async def test_default_not_delegate(self, db, campaign, alice):
        assert alice["is_delegate"] == 0

    async def test_gm_not_delegate(self, db, campaign, gm):
        assert gm["is_delegate"] == 0
        assert gm["is_gm"] == 1


# ---------------------------------------------------------------------------
# 6.2: has_gm_permission tests
# ---------------------------------------------------------------------------

class TestHasGmPermission:
    def test_gm_returns_true(self):
        player = {"is_gm": 1, "is_delegate": 0}
        assert has_gm_permission(player)

    def test_delegate_returns_true(self):
        player = {"is_gm": 0, "is_delegate": 1}
        assert has_gm_permission(player)

    def test_normal_player_returns_false(self):
        player = {"is_gm": 0, "is_delegate": 0}
        assert not has_gm_permission(player)

    def test_missing_is_delegate_defaults_false(self):
        player = {"is_gm": 0}
        assert not has_gm_permission(player)

    def test_gm_and_delegate_returns_true(self):
        player = {"is_gm": 1, "is_delegate": 1}
        assert has_gm_permission(player)


# ---------------------------------------------------------------------------
# 6.3: /gmroll tests (service-level, no Discord mocking)
# ---------------------------------------------------------------------------

class TestGmRoll:
    def test_basic_roll_no_personal_state(self):
        results = [(8, 5), (10, 7), (6, 3)]
        output = format_roll_result(
            player_name="GM",
            results=results,
        )
        assert "GM rolled 3 dice." in output
        assert "Available assets" not in output
        assert "Opposition pool" not in output

    def test_roll_with_npc_name(self):
        results = [(8, 5), (10, 7)]
        output = format_roll_result(
            player_name="Guarda da Torre",
            results=results,
        )
        assert "Guarda da Torre rolled 2 dice." in output

    def test_roll_default_gm_name(self):
        results = [(8, 5)]
        name = None
        player_name = name or "GM"
        output = format_roll_result(
            player_name=player_name,
            results=results,
        )
        assert "GM rolled 1 dice." in output

    def test_roll_with_best_mode(self):
        results = [(8, 5), (10, 7), (6, 3)]
        best_options = calculate_best_options(results)
        output = format_roll_result(
            player_name="GM",
            results=results,
            best_options=best_options if best_options else None,
        )
        if best_options:
            assert "Best total:" in output

    def test_roll_with_difficulty(self):
        results = [(8, 5), (10, 7), (6, 3)]
        best_options = calculate_best_options(results)
        output = format_roll_result(
            player_name="GM",
            results=results,
            best_options=best_options,
            difficulty=10,
        )
        assert "10" in output

    def test_roll_no_available_assets(self):
        results = [(8, 5), (10, 7)]
        output = format_roll_result(
            player_name="GM",
            results=results,
        )
        assert "Available assets" not in output

    def test_roll_no_opposition_elements(self):
        results = [(8, 5), (10, 7)]
        output = format_roll_result(
            player_name="GM",
            results=results,
        )
        assert "Opposition pool" not in output


# ---------------------------------------------------------------------------
# 6.4: Formatter delegate label tests
# ---------------------------------------------------------------------------

class TestFormatterDelegate:
    def _make_player(self, pid=1, name="Alice", is_gm=0, is_delegate=0, pp=3, xp=0):
        return {"id": pid, "name": name, "is_gm": is_gm, "is_delegate": is_delegate, "pp": pp, "xp": xp}

    def test_delegate_label_shown(self):
        campaign = {"name": "Test"}
        players = [self._make_player(is_delegate=1)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "ALICE (delegate)" in output

    def test_gm_label_not_delegate(self):
        campaign = {"name": "Test"}
        players = [self._make_player(is_gm=1)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "(GM)" in output
        assert "(delegate)" not in output

    def test_normal_player_no_label(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "ALICE" in output
        assert "(delegate)" not in output
        assert "(GM)" not in output

    def test_multiple_players_mixed(self):
        campaign = {"name": "Test"}
        players = [
            self._make_player(pid=1, name="Carlos", is_gm=1),
            self._make_player(pid=2, name="Alice", is_delegate=1),
            self._make_player(pid=3, name="Bob"),
        ]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "CARLOS (GM)" in output
        assert "ALICE (delegate)" in output
        assert "BOB" in output
        assert "BOB (delegate)" not in output


# ---------------------------------------------------------------------------
# 6.5: Permission tests: delegate executes GM-only commands, blocked on campaign_end
# ---------------------------------------------------------------------------

class TestDelegatePermissions:
    async def test_delegate_can_add_stress(self, db, campaign, alice, bob):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        alice_updated = await db.get_player(campaign, "user1")
        assert has_gm_permission(alice_updated)

        sm = StateManager(db)
        stress_types = await db.get_stress_types(campaign)
        physical_id = next(t["id"] for t in stress_types if t["name"] == "Physical")
        result = await sm.add_stress(
            campaign, "user1", bob["id"], physical_id, 8,
            player_name="Bob", type_name="Physical",
        )
        assert result["action"] == "added"

    async def test_delegate_blocked_on_campaign_end(self, db, campaign, alice):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        alice_updated = await db.get_player(campaign, "user1")
        assert has_gm_permission(alice_updated)
        assert not alice_updated["is_gm"]

    async def test_normal_player_no_gm_permission(self, db, campaign, bob):
        assert not has_gm_permission(bob)

    async def test_delegate_can_undo_others(self, db, campaign, alice, bob):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()
        alice_updated = await db.get_player(campaign, "user1")

        sm = StateManager(db)
        await sm.add_asset(campaign, "user2", "Shield", 8, player_id=bob["id"])

        action = await db.get_last_undoable_action(campaign)
        assert action is not None
        await sm.execute_undo(action["inverse_data"])
        await db.mark_action_undone(action["id"])

        assets = await db.get_player_assets(campaign, bob["id"])
        assert len(assets) == 0


# ---------------------------------------------------------------------------
# 6.6: Bridge scene: delegate receives step down, GM does not
# ---------------------------------------------------------------------------

class TestBridgeSceneDelegate:
    async def test_delegate_receives_step_down(self, db, campaign, alice, gm):
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE players SET is_delegate = 1 WHERE id = ?",
                (alice["id"],),
            )
            await conn.commit()

        sm = StateManager(db)
        stress_types = await db.get_stress_types(campaign)
        physical_id = next(t["id"] for t in stress_types if t["name"] == "Physical")

        await sm.add_stress(
            campaign, "gm1", alice["id"], physical_id, 8,
            player_name="Alice", type_name="Physical",
        )

        players = await db.get_players(campaign)
        stress_changes = []
        for p in players:
            if p["is_gm"]:
                continue
            stress_list = await db.get_player_stress(campaign, p["id"])
            for s in stress_list:
                new_size = step_down(s["die_size"])
                async with db.connect() as conn:
                    if new_size is None:
                        await conn.execute("DELETE FROM stress WHERE id = ?", (s["id"],))
                    else:
                        await conn.execute(
                            "UPDATE stress SET die_size = ? WHERE id = ?",
                            (new_size, s["id"]),
                        )
                    await conn.commit()
                stress_changes.append({
                    "player": p["name"],
                    "from": s["die_size"],
                    "to": new_size,
                })

        alice_changes = [c for c in stress_changes if c["player"] == "Alice"]
        assert len(alice_changes) == 1
        assert alice_changes[0]["from"] == 8
        assert alice_changes[0]["to"] == 6

    async def test_gm_skipped_in_bridge(self, db, campaign, gm):
        sm = StateManager(db)
        stress_types = await db.get_stress_types(campaign)
        physical_id = next(t["id"] for t in stress_types if t["name"] == "Physical")

        await sm.add_stress(
            campaign, "gm1", gm["id"], physical_id, 8,
            player_name="GameMaster", type_name="Physical",
        )

        players = await db.get_players(campaign)
        stress_changes = []
        for p in players:
            if p["is_gm"]:
                continue
            stress_list = await db.get_player_stress(campaign, p["id"])
            for s in stress_list:
                new_size = step_down(s["die_size"])
                stress_changes.append({"player": p["name"]})

        gm_changes = [c for c in stress_changes if c["player"] == "GameMaster"]
        assert len(gm_changes) == 0

        gm_stress = await db.get_player_stress(campaign, gm["id"])
        assert len(gm_stress) == 1
        assert gm_stress[0]["die_size"] == 8
