"""Tests for services/formatter.py — all 4 public functions."""

from cortex_bot.services.formatter import (
    format_roll_result,
    format_campaign_info,
    format_scene_end,
    format_action_confirm,
)


class TestFormatRollResult:
    def test_basic_roll_no_special(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result("Alice", results)
        assert "Alice rolou 3 dados." in output
        assert "d8: 5" in output
        assert "d6: 3" in output
        assert "d10: 7" in output

    def test_default_total_two_best(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result("Alice", results)
        # Best two values: 7 and 5, total=12, effect d6
        assert "igual a 12." in output
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
        # Botch should return early, no total line
        assert "igual a" not in output

    def test_hitches(self):
        results = [(8, 5), (6, 1), (10, 7)]
        hitches = [(6, 1)]
        output = format_roll_result("Alice", results, hitches=hitches)
        assert "d6: 1 (hitch)" in output
        assert "Hitches: d6." in output
        assert "GM pode dar PP" in output

    def test_best_options_no_difficulty(self):
        results = [(8, 5), (6, 3), (10, 7)]
        best_options = [
            {
                "label": "Melhor total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 6,
            }
        ]
        output = format_roll_result("Alice", results, best_options=best_options)
        assert "Melhor total:" in output
        assert "igual a 12." in output
        assert "Effect die: d6." in output
        # No difficulty, no success/failure status
        assert "Sucesso" not in output
        assert "Falha" not in output

    def test_best_options_with_difficulty_success(self):
        results = [(8, 5), (6, 3), (10, 7)]
        best_options = [
            {
                "label": "Melhor total",
                "dice": [(10, 7), (8, 5)],
                "total": 12,
                "effect_size": 6,
            }
        ]
        output = format_roll_result(
            "Alice", results, best_options=best_options, difficulty=9
        )
        assert "Sucesso, margem 3." in output

    def test_best_options_with_difficulty_failure(self):
        best_options = [
            {
                "label": "Melhor total",
                "dice": [(6, 3), (4, 2)],
                "total": 5,
                "effect_size": 4,
            }
        ]
        output = format_roll_result(
            "Alice", [(6, 3), (4, 2)],
            best_options=best_options, difficulty=8,
        )
        assert "Falha por 3." in output

    def test_best_options_heroic_success(self):
        best_options = [
            {
                "label": "Melhor total",
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
        assert "margem 10" in output
        assert "step up 2 vez(es)" in output

    def test_included_assets(self):
        results = [(8, 5), (6, 3)]
        output = format_roll_result(
            "Alice", results, included_assets=["Big Wrench", "Shield"]
        )
        assert "Incluidos: Big Wrench, Shield." in output

    def test_available_assets(self):
        results = [(8, 5), (6, 3), (10, 7)]
        available = [
            {"name": "Big Wrench", "die_size": 6},
            {"name": "Shield", "die_size": 8},
        ]
        output = format_roll_result("Alice", results, available_assets=available)
        assert "Assets disponiveis: Big Wrench d6, Shield d8." in output

    def test_opposition_elements(self):
        results = [(8, 5), (6, 3), (10, 7)]
        output = format_roll_result(
            "Alice", results,
            opposition_elements=["Doom d10", "Guard d8"],
        )
        assert "Pool da oposicao: Doom d10, Guard d8." in output


class TestFormatCampaignInfo:
    def _make_player(self, pid=1, name="Alice", is_gm=0, pp=3, xp=0):
        return {"id": pid, "name": name, "is_gm": is_gm, "pp": pp, "xp": xp}

    def test_no_scene(self):
        campaign = {"name": "Dark Fantasy"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "Campanha: Dark Fantasy." in output
        assert "Cena atual: nenhuma." in output

    def test_with_active_scene(self):
        campaign = {"name": "Dark Fantasy"}
        players = [self._make_player()]
        scene = {"name": "Tavern Fight"}
        output = format_campaign_info(
            campaign, players, player_states={}, scene=scene, doom_pool=None
        )
        assert "Cena atual: Tavern Fight." in output

    def test_gm_label(self):
        campaign = {"name": "Test"}
        players = [self._make_player(pid=1, name="Carlos", is_gm=1)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "Carlos (GM):" in output

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
        assert "Stress Physical d8." in output

    def test_player_no_stress(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={1: {}}, scene=None, doom_pool=None
        )
        assert "Sem stress." in output

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
        assert "Trauma Mental d6." in output

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
        assert "Assets: Sword d8 (scene)." in output

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
        assert "Complications: Broken Arm d6." in output

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
        assert "Hero dice: d8, d10." in output

    def test_pp_xp_shown(self):
        campaign = {"name": "Test"}
        players = [self._make_player(pp=5, xp=2)]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "PP 5, XP 2." in output

    def test_doom_pool_empty(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=[]
        )
        assert "Doom Pool: vazio." in output

    def test_doom_pool_with_dice(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        doom = [{"die_size": 6}, {"die_size": 8}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=doom
        )
        assert "Doom Pool: d6, d8." in output

    def test_doom_pool_none_hidden(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None, doom_pool=None
        )
        assert "Doom Pool" not in output

    def test_scene_assets(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        scene_assets = [{"name": "Cover", "die_size": 8}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, scene_assets=scene_assets,
        )
        assert "Assets de cena: Cover d8." in output

    def test_scene_complications(self):
        campaign = {"name": "Test"}
        players = [self._make_player()]
        scene_comps = [{"name": "Fire", "die_size": 6}]
        output = format_campaign_info(
            campaign, players, player_states={}, scene=None,
            doom_pool=None, scene_complications=scene_comps,
        )
        assert "Complications de cena: Fire d6." in output

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
        assert "Crisis Pool 'Flood': d6, d8." in output


class TestFormatSceneEnd:
    def test_no_elements(self):
        output = format_scene_end("Tavern Fight", [], [], [])
        assert "Cena encerrada: Tavern Fight." in output
        assert "Nenhum elemento de cena para remover." in output

    def test_no_name(self):
        output = format_scene_end(None, [], [], [])
        assert "Cena encerrada: sem nome." in output

    def test_removed_assets(self):
        assets = [{"name": "Cover", "die_size": 8, "player_name": "Alice"}]
        output = format_scene_end("Fight", assets, [], [])
        assert "Assets removidos:" in output
        assert "Cover d8 (Alice)." in output

    def test_removed_asset_scene_scope(self):
        assets = [{"name": "Torch", "die_size": 6}]
        output = format_scene_end("Fight", assets, [], [])
        assert "Torch d6 (cena)." in output

    def test_removed_complications(self):
        comps = [{"name": "Fire", "die_size": 6, "player_name": "Bob"}]
        output = format_scene_end("Fight", [], comps, [])
        assert "Complications removidas:" in output
        assert "Fire d6 (Bob)." in output

    def test_removed_crisis_pools(self):
        pools = [{"name": "Flood"}]
        output = format_scene_end("Fight", [], [], pools)
        assert "Crisis pools removidos:" in output
        assert "Flood." in output

    def test_stress_changes_bridge(self):
        changes = [
            {"player": "Alice", "type": "Physical", "from": 8, "to": 6},
        ]
        output = format_scene_end("Fight", [], [], [], stress_changes=changes)
        assert "Mudancas de stress (bridge):" in output
        assert "Alice: Physical d8 para d6." in output

    def test_stress_changes_eliminated(self):
        changes = [
            {"player": "Alice", "type": "Physical", "eliminated": True},
        ]
        output = format_scene_end("Fight", [], [], [], stress_changes=changes)
        assert "eliminado (era d4)." in output

    def test_persistent_state(self):
        output = format_scene_end(
            "Fight", [], [], [], persistent_state="Some state info"
        )
        assert "Some state info" in output


class TestFormatActionConfirm:
    def test_basic(self):
        output = format_action_confirm("Asset criado", "Big Wrench d6")
        assert output == "Asset criado. Big Wrench d6"

    def test_with_player_state(self):
        output = format_action_confirm(
            "Asset criado", "Big Wrench d6", player_state="PP 3, XP 0."
        )
        assert output == "Asset criado. Big Wrench d6 PP 3, XP 0."
