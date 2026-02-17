"""Tests for services/formatter.py — all 4 public functions."""

from cortex_bot.services.formatter import (
    format_roll_result,
    format_campaign_info,
    format_scene_end,
    format_action_confirm,
)


class TestFormatRollResult:
    def test_basic_roll_total_first(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result("Alice", results)
        assert "Alice rolled 3 dice." in output
        assert "Total 12" in output
        assert "d8 rolled 5" in output
        assert "d6 rolled 3" in output
        assert "d10 rolled 7" in output
        assert "Effect die: d6." in output

    def test_single_non_hitch_die(self):
        results = [(8, 5), (6, 1)]
        hitches = [(6, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "default d4" in output

    def test_botch(self):
        results = [(8, 1), (6, 1)]
        hitches = [(8, 1), (6, 1)]
        output = format_roll_result(
            "Alice", results, hitches=hitches, is_botch=True
        )
        assert "Botch" in output
        assert "Total zero" in output

    def test_hitches_doom_disabled(self):
        results = [(8, 5), (6, 1), (10, 7)]
        hitches = [(6, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "d6 rolled 1 (hitch)" in output
        assert "Hitches: d6." in output
        assert "GM may award 1 PP" in output
        assert "create a d6 complication." in output
        assert "Doom Pool" not in output

    def test_hitches_doom_enabled(self):
        results = [(8, 5), (6, 1), (10, 7)]
        hitches = [(6, 1)]
        output = format_roll_result(
            "Alice", results, hitches=hitches, doom_enabled=True
        )
        assert "Hitches: d6." in output
        assert "or add a die to the Doom Pool." in output

    def test_multiple_hitches_scale_complication_die(self):
        results = [(8, 1), (6, 1), (10, 7), (12, 5)]
        hitches = [(8, 1), (6, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "create a d8 complication." in output

    def test_three_hitches_d10_complication(self):
        results = [(8, 1), (6, 1), (4, 1), (10, 7)]
        hitches = [(8, 1), (6, 1), (4, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "create a d10 complication." in output

    def test_four_hitches_d12_complication(self):
        results = [(8, 1), (6, 1), (4, 1), (10, 1), (12, 5)]
        hitches = [(8, 1), (6, 1), (4, 1), (10, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "create a d12 complication." in output

    def test_best_options_shows_all_dice_before_options(self):
        results = [(8, 5), (6, 3), (10, 7), (6, 2)]
        best_options = [
            {
                "label": "Best total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 6,
            }
        ]
        output = format_roll_result("Alice", results, best_options=best_options)
        lines = output.strip().split("\n")
        detail_line = next(l for l in lines if "d8 rolled 5" in l and "d6 rolled 3" in l)
        best_line = next(l for l in lines if "Best total" in l)
        assert lines.index(detail_line) < lines.index(best_line)
        assert "d8 rolled 5" in detail_line
        assert "d6 rolled 3" in detail_line
        assert "d10 rolled 7" in detail_line
        assert "d6 rolled 2" in detail_line

    def test_best_options_with_hitch_shows_all_dice(self):
        results = [(8, 5), (6, 1), (10, 7)]
        hitches = [(6, 1)]
        best_options = [
            {
                "label": "Best total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 4,
            }
        ]
        output = format_roll_result(
            "Alice", results, hitches=hitches, best_options=best_options
        )
        assert "d6 rolled 1 (hitch)" in output
        assert "d8 rolled 5" in output
        assert "d10 rolled 7" in output

    def test_best_options_label_first(self):
        results = [(8, 5), (6, 3), (10, 7)]
        best_options = [
            {
                "label": "Best total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 6,
            }
        ]
        output = format_roll_result("Alice", results, best_options=best_options)
        assert "Best total: 12" in output
        assert "d10 rolled 7" in output
        assert "d8 rolled 5" in output
        assert "Effect die: d6." in output
        assert "Success" not in output
        assert "Failure" not in output

    def test_best_options_with_difficulty_success(self):
        results = [(8, 5), (6, 3), (10, 7)]
        best_options = [
            {
                "label": "Best total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 6,
            }
        ]
        output = format_roll_result(
            "Alice", results, best_options=best_options, difficulty=9
        )
        assert "Success, margin 3." in output

    def test_best_options_with_difficulty_failure(self):
        best_options = [
            {
                "label": "Best total",
                "dice": [(6, 3), (4, 2)],
                "total": 5,
                "effect_size": 4,
            }
        ]
        output = format_roll_result(
            "Alice", [(6, 3), (4, 2)],
            best_options=best_options, difficulty=8,
        )
        assert "Failure, short by 3." in output

    def test_best_options_heroic_success(self):
        best_options = [
            {
                "label": "Best total",
                "dice": [(12, 11), (10, 9)],
                "total": 20,
                "effect_size": 8,
            }
        ]
        output = format_roll_result(
            "Alice", [(12, 11), (10, 9), (8, 5)],
            best_options=best_options, difficulty=10,
        )
        assert "Heroic success" in output
        assert "margin 10" in output
        assert "steps up 2 time(s)" in output

    def test_no_best_with_difficulty_success(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result("Alice", results, difficulty=9)
        assert "Total 12" in output
        assert "Success, margin 3." in output

    def test_no_best_with_difficulty_failure(self):
        results = [(8, 3), (6, 2), (10, 4)]
        output = format_roll_result("Alice", results, difficulty=9)
        assert "Total 7" in output
        assert "Failure, short by 2." in output

    def test_included_assets(self):
        results = [(8, 5), (6, 3)]
        output = format_roll_result(
            "Alice", results, included_assets=["Big Wrench", "Shield"]
        )
        assert "Included: Big Wrench, Shield." in output

    def test_available_assets(self):
        results = [(8, 5), (6, 3), (10, 7)]
        available = [
            {"name": "Big Wrench", "die_size": 6},
            {"name": "Shield", "die_size": 8},
        ]
        output = format_roll_result("Alice", results, available_assets=available)
        assert "Available assets: Big Wrench d6, Shield d8." in output

    def test_opposition_elements(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result(
            "Alice", results,
            opposition_elements=["Doom d10", "Guard d8"],
        )
        assert "Opposition pool: Doom d10, Guard d8." in output


class TestFormatCampaignInfo:
    def _make_player(self, pid=1, name="Alice", is_gm=0, pp=3, xp=0):
        return {"id": pid, "name": name, "is_gm": is_gm, "pp": pp, "xp": xp}

    def test_no_scene(self):
        campaign = {"name": "Dark Fantasy"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "CAMPAIGN: Dark Fantasy" in output
        assert "Active scene: none" in output

    def test_with_active_scene(self):
        campaign = {"name": "Dark Fantasy"}
        players = [self._make_player()]
        scene = {"name": "Tavern Fight"}
        output = format_campaign_info(
            campaign, players, player_states={}, scene=scene, doom_pool=None
        )
        assert "Active scene: Tavern Fight" in output

    def test_gm_label(self):
        campaign = {"name": "Test"}
        players = [self._make_player(pid=1, name="Carlos", is_gm=1)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "CARLOS (GM)" in output

    def test_delegate_label(self):
        campaign = {"name": "Test"}
        players = [{"id": 1, "name": "Bob", "is_gm": 0, "is_delegate": 1, "pp": 3, "xp": 0}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "BOB (delegate)" in output

    def test_player_with_stress(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        states = {
            1: {
                "stress": [{"stress_type_name": "Physical", "die_size": 8}],
            },
        }
        output = format_campaign_info(
            campaign, players, states, scene=None, doom_pool=None
        )
        assert "Stress: Physical d8" in output

    def test_player_no_stress(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={1: {}}, scene=None, doom_pool=None
        )
        assert "Stress: none" in output

    def test_player_with_trauma(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        states = {
            1: {
                "stress": [],
                "trauma": [{"stress_type_name": "Mental", "die_size": 6}],
            },
        }
        output = format_campaign_info(
            campaign, players, states, scene=None, doom_pool=None
        )
        assert "Trauma: Mental d6" in output

    def test_player_with_assets(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        states = {
            1: {
                "stress": [],
                "assets": [{"name": "Sword", "die_size": 8, "duration": "scene"}],
            },
        }
        output = format_campaign_info(
            campaign, players, states, scene=None, doom_pool=None
        )
        assert "Assets: Sword d8 (scene)" in output

    def test_player_no_assets(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={1: {}}, scene=None, doom_pool=None
        )
        assert "Assets: none" in output

    def test_player_with_complications(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        states = {
            1: {
                "stress": [],
                "complications": [{"name": "Broken Arm", "die_size": 6}],
            },
        }
        output = format_campaign_info(
            campaign, players, states, scene=None, doom_pool=None
        )
        assert "Complications: Broken Arm d6" in output

    def test_player_no_complications(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={1: {}}, scene=None, doom_pool=None
        )
        assert "Complications: none" in output

    def test_player_with_hero_dice(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        states = {
            1: {
                "stress": [],
                "hero_dice": [{"die_size": 8}, {"die_size": 10}],
            },
        }
        output = format_campaign_info(
            campaign, players, states, scene=None, doom_pool=None
        )
        assert "Hero dice: d8, d10" in output

    def test_pp_xp_shown(self):
        campaign = {"name": "Test"}
        players = [self._make_player(pp=5, xp=2)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "PP 5, XP 2" in output

    def test_gm_no_pp_xp(self):
        campaign = {"name": "Test"}
        players = [self._make_player(name="Carlos", is_gm=1, pp=5, xp=2)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "CARLOS (GM)" in output
        assert "PP" not in output
        assert "XP" not in output

    def test_blank_line_between_players(self):
        campaign = {"name": "Test"}
        players = [
            self._make_player(pid=1, name="Alice"),
            self._make_player(pid=2, name="Bob"),
        ]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "---" not in output
        assert "ALICE" in output
        assert "BOB" in output
        lines = output.split("\n")
        alice_idx = next(i for i, l in enumerate(lines) if "ALICE" in l)
        bob_idx = next(i for i, l in enumerate(lines) if "BOB" in l)
        # There should be a blank line between the two player blocks
        assert any(lines[j] == "" for j in range(alice_idx + 1, bob_idx))

    def test_no_separator_single_player(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "---" not in output

    def test_doom_pool_empty(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=[]
        )
        assert "DOOM POOL" in output
        assert "empty" in output

    def test_doom_pool_with_dice(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        doom = [{"die_size": 6}, {"die_size": 8}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=doom
        )
        assert "DOOM POOL" in output
        assert "d6, d8" in output

    def test_doom_pool_none_hidden(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "DOOM POOL" not in output

    def test_scene_assets(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        scene_assets = [{"name": "Cover", "die_size": 8}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, scene_assets=scene_assets,
        )
        assert "SCENE ELEMENTS" in output
        assert "Scene assets: Cover d8" in output

    def test_scene_complications(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        scene_comps = [{"name": "Fire", "die_size": 6}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, scene_complications=scene_comps,
        )
        assert "SCENE ELEMENTS" in output
        assert "Scene complications: Fire d6" in output

    def test_crisis_pools(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        crisis = [
            {
                "name": "Flood",
                "dice": [{"die_size": 6}, {"die_size": 8}],
            }
        ]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, crisis_pools=crisis,
        )
        assert "Crisis Pool 'Flood': d6, d8" in output

    def test_modules_all_active(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        config = {"doom_pool": True, "hero_dice": True, "trauma": True, "best_mode": True}
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, config=config,
        )
        assert "MODULES" in output
        assert "doom_pool: active" in output
        assert "hero_dice: active" in output
        assert "trauma: active" in output
        assert "best_mode: active" in output

    def test_modules_mixed(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        config = {"doom_pool": True, "hero_dice": False, "trauma": False, "best_mode": True}
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, config=config,
        )
        assert "doom_pool: active" in output
        assert "hero_dice: inactive" in output
        assert "trauma: inactive" in output
        assert "best_mode: active" in output

    def test_modules_none_omitted(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, config=None,
        )
        assert "MODULES" not in output

    def test_player_name_uppercase(self):
        campaign = {"name": "Test"}
        players = [self._make_player(name="alice")]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "ALICE" in output


class TestFormatSceneEnd:
    def test_no_elements(self):
        output = format_scene_end("Tavern Fight", [], [], [])
        assert "SCENE ENDED: Tavern Fight" in output
        assert "No scene elements to remove." in output
        assert "Next:" in output

    def test_no_name(self):
        output = format_scene_end(None, [], [], [])
        assert "SCENE ENDED: unnamed" in output

    def test_removed_assets(self):
        assets = [{"name": "Cover", "die_size": 8, "player_name": "Alice"}]
        output = format_scene_end("Fight", assets, [], [])
        assert "REMOVED (scene scope)" in output
        assert "Cover d8 (Alice)" in output

    def test_removed_asset_scene_scope(self):
        assets = [{"name": "Torch", "die_size": 6}]
        output = format_scene_end("Fight", assets, [], [])
        assert "Torch d6 (scene)" in output

    def test_removed_complications(self):
        comps = [{"name": "Fire", "die_size": 6, "player_name": "Bob"}]
        output = format_scene_end("Fight", [], comps, [])
        assert "REMOVED (scene scope)" in output
        assert "Fire d6 (Bob)" in output

    def test_removed_crisis_pools(self):
        pools = [{"name": "Flood"}]
        output = format_scene_end("Fight", [], [], pools)
        assert "REMOVED (scene scope)" in output
        assert "Flood" in output

    def test_stress_changes_bridge(self):
        changes = [
            {"player": "Alice", "type": "Physical", "from": 8, "to": 6},
        ]
        output = format_scene_end("Fight", [], [], [], stress_changes=changes)
        assert "STRESS CHANGES (bridge)" in output
        assert "Alice: Physical d8 to d6" in output

    def test_stress_changes_eliminated(self):
        changes = [
            {"player": "Alice", "type": "Physical", "eliminated": True},
        ]
        output = format_scene_end("Fight", [], [], [], stress_changes=changes)
        assert "eliminated (was d4)" in output

    def test_persistent_state(self):
        output = format_scene_end(
            "Fight", [], [], [], persistent_state="Some state info"
        )
        assert "Some state info" in output

    def test_next_guidance_always_present(self):
        output = format_scene_end("Fight", [], [], [])
        assert "Next: /scene start" in output
        assert "/campaign info" in output


class TestFormatActionConfirm:
    def test_basic(self):
        output = format_action_confirm("Asset created", "Big Wrench d6")
        assert output == "Asset created. Big Wrench d6"

    def test_with_player_state(self):
        output = format_action_confirm(
            "Asset created", "Big Wrench d6", player_state="PP 3, XP 0."
        )
        assert output == "Asset created. Big Wrench d6 PP 3, XP 0."
