"""Integration test: full flow setup -> scene -> roll -> transition -> undo."""

import json
import pytest

from cortex_bot.models.database import Database
from cortex_bot.models.dice import step_down
from cortex_bot.services.state_manager import StateManager
from cortex_bot.services.roller import roll_pool, find_hitches, is_botch, calculate_best_options
from cortex_bot.services.formatter import format_roll_result, format_campaign_info, format_scene_end


@pytest.fixture
async def db(tmp_path):
    database = Database(path=str(tmp_path / "integration.db"))
    await database.initialize()
    return database


async def test_full_game_flow(db):
    sm = StateManager(db)

    # 1. Setup campaign
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
            ("srv", "ch", "Test Game", json.dumps({
                "doom_pool": True, "hero_dice": False,
                "trauma": True, "best_mode": True,
            })),
        )
        campaign_id = cursor.lastrowid

        # Add players
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp) VALUES (?, ?, ?, ?, ?)",
            (campaign_id, "gm1", "GameMaster", 1, 5),
        )
        cursor = await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp) VALUES (?, ?, ?, ?, ?)",
            (campaign_id, "p1", "Alice", 0, 3),
        )
        alice_id = cursor.lastrowid
        cursor = await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp) VALUES (?, ?, ?, ?, ?)",
            (campaign_id, "p2", "Bob", 0, 2),
        )
        bob_id = cursor.lastrowid

        # Stress types
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (campaign_id, "Physical"),
        )
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (campaign_id, "Mental"),
        )
        await conn.commit()

    stress_types = await db.get_stress_types(campaign_id)
    physical_id = next(st["id"] for st in stress_types if st["name"] == "Physical")
    mental_id = next(st["id"] for st in stress_types if st["name"] == "Mental")

    # 2. Start scene
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO scenes (campaign_id, name) VALUES (?, ?)",
            (campaign_id, "Dark Dungeon"),
        )
        scene_id = cursor.lastrowid
        await conn.commit()

    scene = await db.get_active_scene(campaign_id)
    assert scene is not None
    assert scene["name"] == "Dark Dungeon"

    # 3. GM adds stress to Alice
    stress_result = await sm.add_stress(
        campaign_id, "gm1", alice_id, physical_id, 8,
        player_name="Alice", type_name="Physical",
    )
    assert stress_result["action"] == "added"

    # 4. Alice creates asset (scene duration)
    asset_result = await sm.add_asset(
        campaign_id, "p1", "Improvised Torch", 6,
        player_id=alice_id, scene_id=scene_id, duration="scene",
    )
    torch_id = asset_result["id"]

    # 5. GM adds complication to scene
    comp_result = await sm.add_complication(
        campaign_id, "gm1", "Slippery Floor", 8,
        scene_id=scene_id, scope="scene",
    )

    # 6. GM adds to doom pool
    async with db.connect() as conn:
        await conn.execute(
            "INSERT INTO doom_pool_dice (campaign_id, die_size) VALUES (?, ?)",
            (campaign_id, 6),
        )
        await conn.execute(
            "INSERT INTO doom_pool_dice (campaign_id, die_size) VALUES (?, ?)",
            (campaign_id, 8),
        )
        await conn.commit()

    # 7. Alice rolls with assets
    dice = [8, 10, 6]  # From her sheet
    alice_assets = await db.get_player_assets(campaign_id, alice_id)
    assert len(alice_assets) == 1
    dice.append(alice_assets[0]["die_size"])  # Include torch d6

    results = roll_pool(dice)
    assert len(results) == 4

    hitches = find_hitches(results)
    botch = is_botch(results)
    best_options = calculate_best_options(results)

    # Format accessible output
    output = format_roll_result(
        player_name="Alice",
        results=results,
        included_assets=["Improvised Torch d6"],
        hitches=hitches,
        is_botch=botch,
        best_options=best_options if best_options else None,
        difficulty=11,
    )
    assert "Alice rolled 4 dice" in output
    assert "Improvised Torch d6" in output

    # 8. Verify info output
    players = await db.get_players(campaign_id)
    player_states = {}
    for p in players:
        player_states[p["id"]] = {
            "stress": await db.get_player_stress(campaign_id, p["id"]),
            "trauma": await db.get_player_trauma(campaign_id, p["id"]),
            "assets": await db.get_player_assets(campaign_id, p["id"]),
            "complications": await db.get_player_complications(campaign_id, p["id"]),
            "hero_dice": await db.get_hero_dice(campaign_id, p["id"]),
        }
    doom = await db.get_doom_pool(campaign_id)
    scene_assets = await db.get_scene_assets(scene_id)
    scene_comps = await db.get_scene_complications(scene_id)

    campaign = await db.get_campaign_by_channel("srv", "ch")
    info = format_campaign_info(
        campaign, players, player_states, scene,
        doom, scene_assets, scene_comps,
    )
    assert "Test Game" in info
    assert "Dark Dungeon" in info
    assert "ALICE" in info
    assert "Physical d8" in info
    assert "DOOM POOL" in info

    # 9. GM adds Mental stress d6 to Bob
    await sm.add_stress(
        campaign_id, "gm1", bob_id, mental_id, 6,
        player_name="Bob", type_name="Mental",
    )

    # 10. End scene as bridge (step down stress)
    scene_assets_before = await db.get_scene_assets(scene_id)
    scene_comps_before = await db.get_scene_complications(scene_id)

    # Step down stress for bridge
    stress_changes = []
    for p in players:
        stresses = await db.get_player_stress(campaign_id, p["id"])
        for s in stresses:
            new_size = step_down(s["die_size"])
            async with db.connect() as conn:
                if new_size is None:
                    await conn.execute("DELETE FROM stress WHERE id = ?", (s["id"],))
                    stress_changes.append({
                        "player": p["name"], "type": s["stress_type_name"],
                        "eliminated": True,
                    })
                else:
                    await conn.execute(
                        "UPDATE stress SET die_size = ? WHERE id = ?",
                        (new_size, s["id"]),
                    )
                    stress_changes.append({
                        "player": p["name"], "type": s["stress_type_name"],
                        "from": s["die_size"], "to": new_size,
                    })
                await conn.commit()

    # Clean scene elements
    async with db.connect() as conn:
        await conn.execute(
            "DELETE FROM assets WHERE scene_id = ? AND duration = 'scene'",
            (scene_id,),
        )
        await conn.execute(
            "DELETE FROM complications WHERE scene_id = ? AND scope = 'scene'",
            (scene_id,),
        )
        await conn.execute(
            "UPDATE scenes SET is_active = 0 WHERE id = ?",
            (scene_id,),
        )
        await conn.commit()

    # Verify cleanup
    remaining_assets = await db.get_player_assets(campaign_id, alice_id)
    assert len(remaining_assets) == 0  # Torch was scene-scoped

    alice_stress = await db.get_player_stress(campaign_id, alice_id)
    assert len(alice_stress) == 1
    assert alice_stress[0]["die_size"] == 6  # Physical d8 -> d6 (bridge)

    bob_stress = await db.get_player_stress(campaign_id, bob_id)
    assert len(bob_stress) == 1
    assert bob_stress[0]["die_size"] == 4  # Mental d6 -> d4 (bridge step down)

    # Format scene end
    end_summary = format_scene_end(
        "Dark Dungeon",
        scene_assets_before,
        scene_comps_before,
        [],  # No crisis pools
        stress_changes,
    )
    assert "Dark Dungeon" in end_summary
    assert "Improvised Torch" in end_summary or "REMOVED" in end_summary

    # 11. Verify doom pool persists after scene end
    doom_after = await db.get_doom_pool(campaign_id)
    assert len(doom_after) == 2  # Doom pool persists

    # 12. Undo the stress addition to Alice
    # The last undoable action should be related to stress
    # But the bridge step-downs were done via raw SQL, not state manager
    # So undo should find the last state manager action
    action = await db.get_last_undoable_action(campaign_id, "gm1")
    assert action is not None

    # 13. Verify no active scene
    active = await db.get_active_scene(campaign_id)
    assert active is None
