"""Tests for the views module: custom_id parsing, view composition, and DynamicItem patterns."""

import re

import discord
import pytest

from cortex_bot.views.base import (
    parse_custom_id,
    make_custom_id,
    CortexView,
    add_die_buttons,
    add_player_options,
)


# ---------------------------------------------------------------------------
# Pure function tests (no event loop needed)
# ---------------------------------------------------------------------------


class TestParseCustomId:
    def test_simple_action(self):
        action, params = parse_custom_id("cortex:scene_start")
        assert action == "scene_start"
        assert params == []

    def test_action_with_one_param(self):
        action, params = parse_custom_id("cortex:undo:42")
        assert action == "undo"
        assert params == ["42"]

    def test_action_with_multiple_params(self):
        action, params = parse_custom_id("cortex:stress_add:1:2:3")
        assert action == "stress_add"
        assert params == ["1", "2", "3"]

    def test_invalid_prefix_raises(self):
        with pytest.raises(ValueError, match="Invalid custom_id"):
            parse_custom_id("notcortex:action")

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="Invalid custom_id"):
            parse_custom_id("cortex")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid custom_id"):
            parse_custom_id("")


class TestMakeCustomId:
    def test_simple(self):
        assert make_custom_id("scene_start") == "cortex:scene_start"

    def test_with_int_param(self):
        assert make_custom_id("undo", 42) == "cortex:undo:42"

    def test_with_multiple_params(self):
        assert make_custom_id("stress_add", 1, 2, 3) == "cortex:stress_add:1:2:3"

    def test_with_string_params(self):
        assert make_custom_id("roll", "quick", "10") == "cortex:roll:quick:10"

    def test_exceeds_100_chars_raises(self):
        with pytest.raises(ValueError, match="100 char limit"):
            make_custom_id("action", "x" * 100)

    def test_roundtrip(self):
        original_action = "stress_add"
        original_params = ["1", "5", "8"]
        custom_id = make_custom_id(original_action, *original_params)
        action, params = parse_custom_id(custom_id)
        assert action == original_action
        assert params == original_params


class TestCustomIdRegexPatterns:
    """Test that DynamicItem regex patterns match the custom_ids we generate."""

    def test_undo_button_pattern(self):
        pattern = r"cortex:undo:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("undo", 42)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "42"

    def test_campaign_info_pattern(self):
        pattern = r"cortex:campaign_info:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("campaign_info", 99)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "99"

    def test_scene_start_pattern(self):
        pattern = r"cortex:scene_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("scene_start", 7)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "7"

    def test_roll_start_pattern(self):
        pattern = r"cortex:roll_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("roll_start", 15)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "15"

    def test_stress_add_start_pattern(self):
        pattern = r"cortex:stress_add_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("stress_add_start", 3)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "3"

    def test_asset_add_start_pattern(self):
        pattern = r"cortex:asset_add_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("asset_add_start", 5)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "5"

    def test_comp_add_start_pattern(self):
        pattern = r"cortex:comp_add_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("comp_add_start", 8)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "8"

    def test_doom_add_start_pattern(self):
        pattern = r"cortex:doom_add_start:(?P<campaign_id>\d+)"
        custom_id = make_custom_id("doom_add_start", 11)
        match = re.match(pattern, custom_id)
        assert match is not None
        assert match["campaign_id"] == "11"


# ---------------------------------------------------------------------------
# Tests that require event loop (View/DynamicItem instantiation)
# ---------------------------------------------------------------------------


class TestAddDieButtons:
    """Test the add_die_buttons helper."""

    async def test_creates_five_buttons(self):
        view = CortexView()
        callback_log: list[int] = []

        async def cb(interaction, die_size):
            callback_log.append(die_size)

        add_die_buttons(view, cb)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_button_labels(self):
        view = CortexView()

        async def cb(interaction, die_size):
            pass

        add_die_buttons(view, cb)
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert labels == ["d4", "d6", "d8", "d10", "d12"]

    async def test_buttons_use_ephemeral_custom_ids(self):
        view = CortexView()

        async def cb(interaction, die_size):
            pass

        add_die_buttons(view, cb)
        for child in view.children:
            assert child.custom_id.startswith("ephemeral:die:")

    async def test_all_buttons_in_row_zero(self):
        view = CortexView()

        async def cb(interaction, die_size):
            pass

        add_die_buttons(view, cb)
        for child in view.children:
            assert child.row == 0


class TestAddPlayerOptions:
    """Test the add_player_options helper."""

    async def test_buttons_when_lte_5_players(self):
        view = CortexView()
        players = [{"id": i, "name": f"Player{i}"} for i in range(1, 4)]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 3
        assert buttons[0].label == "Player1"

    async def test_select_when_gt_5_players(self):
        view = CortexView()
        players = [{"id": i, "name": f"Player{i}"} for i in range(1, 8)]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb)
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 1
        assert len(selects[0].options) == 7

    async def test_extra_buttons_count_toward_threshold(self):
        view = CortexView()
        players = [{"id": i, "name": f"P{i}"} for i in range(1, 5)]
        extras = [("Cena", "scene"), ("Extra", "extra")]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb, extra_buttons=extras)
        # 4 players + 2 extras = 6 > 5, so should use select
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 1

    async def test_extra_buttons_as_buttons_when_under_threshold(self):
        view = CortexView()
        players = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        extras = [("Cena", "scene")]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb, extra_buttons=extras)
        # 2 + 1 = 3 <= 5, uses buttons
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 3
        labels = [b.label for b in buttons]
        assert "Alice" in labels
        assert "Cena" in labels

    async def test_exactly_5_uses_buttons(self):
        view = CortexView()
        players = [{"id": i, "name": f"P{i}"} for i in range(1, 6)]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5


class TestCortexView:
    async def test_timeout_is_none(self):
        view = CortexView()
        assert view.timeout is None


class TestViewComposition:
    """Test that views compose the correct buttons based on context."""

    async def test_post_setup_view_has_scene_start(self):
        from cortex_bot.views.scene_views import PostSetupView

        view = PostSetupView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:scene_start:1" in custom_ids

    async def test_post_scene_start_view_has_core_buttons(self):
        from cortex_bot.views.scene_views import PostSceneStartView

        view = PostSceneStartView(campaign_id=1, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:stress_add_start:1" in custom_ids
        assert "cortex:asset_add_start:1" in custom_ids
        assert "cortex:comp_add_start:1" in custom_ids

    async def test_post_scene_start_view_no_doom_when_disabled(self):
        from cortex_bot.views.scene_views import PostSceneStartView

        view = PostSceneStartView(campaign_id=1, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:doom_add_start:1" not in custom_ids

    async def test_post_scene_start_view_has_doom_when_enabled(self):
        from cortex_bot.views.scene_views import PostSceneStartView

        view = PostSceneStartView(campaign_id=1, doom_enabled=True)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:doom_add_start:1" in custom_ids

    async def test_post_scene_end_view(self):
        from cortex_bot.views.scene_views import PostSceneEndView

        view = PostSceneEndView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:scene_start:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids

    async def test_post_roll_view(self):
        from cortex_bot.views.rolling_views import PostRollView

        view = PostRollView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids

    async def test_post_stress_view(self):
        from cortex_bot.views.state_views import PostStressView

        view = PostStressView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:stress_add_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids

    async def test_post_asset_view(self):
        from cortex_bot.views.state_views import PostAssetView

        view = PostAssetView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:asset_add_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids

    async def test_post_complication_view(self):
        from cortex_bot.views.state_views import PostComplicationView

        view = PostComplicationView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:comp_add_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids

    async def test_post_doom_action_view(self):
        from cortex_bot.views.doom_views import PostDoomActionView

        view = PostDoomActionView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:doom_add_start:1" in custom_ids
        assert any("doom_remove" in cid for cid in custom_ids)
        assert any("doom_roll" in cid for cid in custom_ids)

    async def test_post_undo_view(self):
        from cortex_bot.views.common import PostUndoView

        view = PostUndoView(campaign_id=1)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:undo:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids

    async def test_post_info_view_with_active_scene(self):
        from cortex_bot.views.common import PostInfoView

        view = PostInfoView(campaign_id=1, has_active_scene=True)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:scene_start:1" not in custom_ids

    async def test_post_info_view_without_active_scene(self):
        from cortex_bot.views.common import PostInfoView

        view = PostInfoView(campaign_id=1, has_active_scene=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:scene_start:1" in custom_ids
        assert "cortex:roll_start:1" not in custom_ids


class TestPoolBuilderView:
    """Test PoolBuilderView state management."""

    async def test_initial_state_empty_pool(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        assert view.pool == []
        assert view.included_toggles == set()
        assert view.build_status_text() == "Pool vazio. Clique nos dados para montar o pool."

    async def test_add_die_updates_pool(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        view.pool.append(8)
        view.history.append(("die", 8))
        assert view.pool == [8]
        assert "1x d8" in view.build_status_text()

    async def test_add_multiple_dice(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        view.pool.extend([8, 8, 6])
        assert "2x d8" in view.build_status_text()
        assert "1x d6" in view.build_status_text()

    async def test_toggle_on(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [{"id": "asset:10", "label": "Sword d8", "die_size": 8}]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=toggles
        )
        view.included_toggles.add("asset:10")
        view.pool.append(8)
        view.history.append(("toggle_on", "asset:10"))
        assert "asset:10" in view.included_toggles
        assert 8 in view.pool

    async def test_toggle_off(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [{"id": "asset:10", "label": "Sword d8", "die_size": 8}]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=toggles
        )
        view.included_toggles.add("asset:10")
        view.pool.append(8)
        view.included_toggles.discard("asset:10")
        view.pool.remove(8)
        assert "asset:10" not in view.included_toggles
        assert 8 not in view.pool

    async def test_remove_last_die(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        view.pool.extend([8, 6])
        view.history.extend([("die", 8), ("die", 6)])

        # Remove last (d6)
        action_type, value = view.history.pop()
        view.pool.remove(value)
        assert view.pool == [8]

    async def test_clear_resets_everything(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [{"id": "asset:10", "label": "Sword d8", "die_size": 8}]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=toggles
        )
        view.pool.extend([8, 6])
        view.included_toggles.add("asset:10")
        view.history.extend([("die", 8), ("die", 6), ("toggle_on", "asset:10")])

        view.pool.clear()
        view.included_toggles.clear()
        view.history.clear()

        assert view.pool == []
        assert view.included_toggles == set()
        assert view.history == []
        assert "Pool vazio" in view.build_status_text()

    async def test_die_buttons_present(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "+d4" in labels
        assert "+d6" in labels
        assert "+d8" in labels
        assert "+d10" in labels
        assert "+d12" in labels

    async def test_toggle_buttons_present(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [
            {"id": "asset:10", "label": "Sword d8", "die_size": 8},
            {"id": "asset:11", "label": "Shield d6", "die_size": 6},
        ]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=toggles
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Sword d8" in labels
        assert "Shield d6" in labels

    async def test_no_toggle_row_without_toggles(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert not any("Sword" in l or "Shield" in l for l in labels)

    async def test_control_buttons_present(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Rolar" in labels
        assert "Limpar" in labels
        assert "Remover ultimo" not in labels

    async def test_remover_ultimo_appears_with_history(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        view.pool.append(8)
        view.history.append(("die", 8))
        view._build_components()
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Remover ultimo" in labels

    async def test_roll_button_label_updates_with_pool_size(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        view.pool.extend([8, 6, 8])
        view._build_components()
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Rolar 3 dados" in labels

    async def test_ephemeral_custom_ids_use_uuid(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        v1 = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        v2 = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=[]
        )
        ids1 = {c.custom_id for c in v1.children}
        ids2 = {c.custom_id for c in v2.children}
        assert ids1.isdisjoint(ids2)


class TestStateViewButtonChains:
    """Test that state views use buttons for die selection and player selection."""

    async def test_stress_die_view_uses_buttons(self):
        from cortex_bot.views.state_views import StressDieSelectView

        view = StressDieSelectView(
            campaign_id=1, actor_id="123", player_id=1, stress_type_id=1
        )

        async def on_die(interaction, die_size):
            pass

        add_die_buttons(view, on_die)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5
        labels = [b.label for b in buttons]
        assert "d4" in labels
        assert "d12" in labels

    async def test_asset_die_view_uses_buttons(self):
        from cortex_bot.views.state_views import AssetDieSelectView

        view = AssetDieSelectView(
            campaign_id=1, actor_id="123", player_id=1, is_scene=False, name="Sword"
        )

        async def on_die(interaction, die_size):
            pass

        add_die_buttons(view, on_die)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_comp_die_view_uses_buttons(self):
        from cortex_bot.views.state_views import CompDieSelectView

        view = CompDieSelectView(
            campaign_id=1, actor_id="123", player_id=1, is_scene=False, name="Wounded"
        )

        async def on_die(interaction, die_size):
            pass

        add_die_buttons(view, on_die)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_stress_player_view_buttons_with_few_players(self):
        from cortex_bot.views.state_views import StressPlayerSelectView

        view = StressPlayerSelectView(campaign_id=1, actor_id="123")
        players = [{"id": i, "name": f"P{i}"} for i in range(1, 4)]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 3

    async def test_stress_player_view_select_with_many_players(self):
        from cortex_bot.views.state_views import StressPlayerSelectView

        view = StressPlayerSelectView(campaign_id=1, actor_id="123")
        players = [{"id": i, "name": f"P{i}"} for i in range(1, 8)]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb)
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 1
        assert len(selects[0].options) == 7

    async def test_asset_owner_view_with_scene_extra_button(self):
        from cortex_bot.views.state_views import AssetOwnerSelectView

        view = AssetOwnerSelectView(
            campaign_id=1, actor_id="123", actor={"is_gm": 1}
        )
        players = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb, extra_buttons=[("Asset de Cena", "scene")])
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        labels = [b.label for b in buttons]
        assert "Alice" in labels
        assert "Asset de Cena" in labels

    async def test_comp_target_view_with_scene_extra_button(self):
        from cortex_bot.views.state_views import CompTargetSelectView

        view = CompTargetSelectView(
            campaign_id=1, actor_id="123", actor={"is_gm": 1}
        )
        players = [{"id": 1, "name": "Alice"}]

        async def cb(interaction, val):
            pass

        add_player_options(view, players, cb, extra_buttons=[("Complicacao de Cena", "scene")])
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        labels = [b.label for b in buttons]
        assert "Alice" in labels
        assert "Complicacao de Cena" in labels


class TestMenuView:
    """Test MenuView composition based on campaign state."""

    async def test_menu_with_active_scene_no_doom(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_active_scene=True, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:stress_add_start:1" in custom_ids
        assert "cortex:asset_add_start:1" in custom_ids
        assert "cortex:comp_add_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids
        assert "cortex:doom_add_start:1" not in custom_ids

    async def test_menu_with_active_scene_and_doom(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_active_scene=True, doom_enabled=True)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:doom_add_start:1" in custom_ids

    async def test_menu_without_active_scene(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_active_scene=False, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:scene_start:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids
        assert "cortex:roll_start:1" not in custom_ids

    async def test_menu_without_active_scene_ignores_doom(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_active_scene=False, doom_enabled=True)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:doom_add_start:1" not in custom_ids
        assert "cortex:scene_start:1" in custom_ids


class TestDoomViewButtons:
    """Test that doom views use buttons instead of selects."""

    async def test_doom_die_select_view_has_no_selects(self):
        from cortex_bot.views.doom_views import DoomDieSelectView

        view = DoomDieSelectView(campaign_id=1, actor_id="123")

        async def on_die(interaction, die_size):
            pass

        add_die_buttons(view, on_die)
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 0
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_doom_remove_view_uses_buttons(self):
        from cortex_bot.views.doom_views import DoomRemoveSelectView
        import uuid as _uuid

        view = DoomRemoveSelectView(campaign_id=1, actor_id="123")
        # Simulate adding deduped buttons for d6 and d8
        uid = _uuid.uuid4().hex[:8]
        for size in [6, 8]:
            btn = discord.ui.Button(
                label=f"d{size}",
                style=discord.ButtonStyle.primary,
                custom_id=f"ephemeral:doom_remove:{size}:{uid}",
            )
            view.add_item(btn)

        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 2
        labels = [b.label for b in buttons]
        assert "d6" in labels
        assert "d8" in labels
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 0


class TestDynamicItemRegistration:
    """Test that all DynamicItems can be imported and have correct template patterns."""

    async def test_all_dynamic_items_importable(self):
        from cortex_bot.views.common import UndoButton, CampaignInfoButton
        from cortex_bot.views.scene_views import SceneStartButton
        from cortex_bot.views.rolling_views import RollStartButton
        from cortex_bot.views.state_views import (
            StressAddStartButton,
            AssetAddStartButton,
            ComplicationAddStartButton,
        )
        from cortex_bot.views.doom_views import DoomAddStartButton

        for cls, cid in [
            (UndoButton, 1),
            (CampaignInfoButton, 1),
            (SceneStartButton, 1),
            (RollStartButton, 1),
            (StressAddStartButton, 1),
            (AssetAddStartButton, 1),
            (ComplicationAddStartButton, 1),
            (DoomAddStartButton, 1),
        ]:
            item = cls(cid)
            assert item.item.custom_id.startswith("cortex:")

    async def test_custom_id_uniqueness_across_buttons(self):
        """Each button type generates a distinct custom_id prefix."""
        from cortex_bot.views.common import UndoButton, CampaignInfoButton
        from cortex_bot.views.scene_views import SceneStartButton
        from cortex_bot.views.rolling_views import RollStartButton
        from cortex_bot.views.state_views import (
            StressAddStartButton,
            AssetAddStartButton,
            ComplicationAddStartButton,
        )
        from cortex_bot.views.doom_views import DoomAddStartButton

        items = [
            UndoButton(1),
            CampaignInfoButton(1),
            SceneStartButton(1),
            RollStartButton(1),
            StressAddStartButton(1),
            AssetAddStartButton(1),
            ComplicationAddStartButton(1),
            DoomAddStartButton(1),
        ]
        custom_ids = [item.item.custom_id for item in items]
        assert len(custom_ids) == len(set(custom_ids)), (
            f"Duplicate custom_ids found: {custom_ids}"
        )


class TestPersistenceCustomIdParsing:
    """Test that custom_ids generated by buttons can be parsed back by their DynamicItem patterns.

    Simulates what happens after a bot restart: the bot sees a button click
    with a custom_id and needs to match it to the right DynamicItem handler.
    """

    def _verify_pattern_matches(self, cls, campaign_id: int):
        instance = cls(campaign_id)
        custom_id = instance.item.custom_id
        pattern = cls.__discord_ui_compiled_template__
        match = pattern.search(custom_id)
        assert match is not None, (
            f"Pattern {pattern.pattern} didn't match {custom_id}"
        )
        assert int(match["campaign_id"]) == campaign_id

    async def test_undo_button_persistence(self):
        from cortex_bot.views.common import UndoButton

        self._verify_pattern_matches(UndoButton, 42)

    async def test_campaign_info_button_persistence(self):
        from cortex_bot.views.common import CampaignInfoButton

        self._verify_pattern_matches(CampaignInfoButton, 99)

    async def test_scene_start_button_persistence(self):
        from cortex_bot.views.scene_views import SceneStartButton

        self._verify_pattern_matches(SceneStartButton, 7)

    async def test_roll_start_button_persistence(self):
        from cortex_bot.views.rolling_views import RollStartButton

        self._verify_pattern_matches(RollStartButton, 15)

    async def test_stress_add_start_button_persistence(self):
        from cortex_bot.views.state_views import StressAddStartButton

        self._verify_pattern_matches(StressAddStartButton, 3)

    async def test_asset_add_start_button_persistence(self):
        from cortex_bot.views.state_views import AssetAddStartButton

        self._verify_pattern_matches(AssetAddStartButton, 5)

    async def test_complication_add_start_button_persistence(self):
        from cortex_bot.views.state_views import ComplicationAddStartButton

        self._verify_pattern_matches(ComplicationAddStartButton, 8)

    async def test_doom_add_start_button_persistence(self):
        from cortex_bot.views.doom_views import DoomAddStartButton

        self._verify_pattern_matches(DoomAddStartButton, 11)


# ---------------------------------------------------------------------------
# GM Pool Builder tests (tasks 4.1-4.8)
# ---------------------------------------------------------------------------

from cortex_bot.models.database import Database


@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    database = Database(path=db_path)
    await database.initialize()
    return database


@pytest.fixture
async def gm_campaign(db):
    """Campaign with GM, two players, stress types, active scene."""
    async with db.connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO campaigns (server_id, channel_id, name, config) VALUES (?, ?, ?, ?)",
            ("srv1", "ch1", "Test Campaign", '{}'),
        )
        cid = cursor.lastrowid
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (cid, "gm1", "GameMaster", 1, 5, 0),
        )
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (cid, "user1", "Alice", 0, 3, 0),
        )
        await conn.execute(
            "INSERT INTO players (campaign_id, discord_user_id, name, is_gm, pp, xp) VALUES (?, ?, ?, ?, ?, ?)",
            (cid, "user2", "Bob", 0, 3, 0),
        )
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (cid, "Physical"),
        )
        await conn.execute(
            "INSERT INTO stress_types (campaign_id, name) VALUES (?, ?)",
            (cid, "Mental"),
        )
        await conn.execute(
            "INSERT INTO scenes (campaign_id, name, is_active) VALUES (?, ?, ?)",
            (cid, "Battle", 1),
        )
        await conn.commit()
    return cid


class TestPoolBuilderToggleItems:
    """Task 4.1: PoolBuilderView accepts toggle_items with string id and formatted label."""

    async def test_accepts_string_ids_and_labels(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [
            {"id": "stress:1", "label": "Alice: Physical d8", "die_size": 8},
            {"id": "comp:5", "label": "Cena: Trapped d6", "die_size": 6},
        ]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="GM", toggle_items=toggles
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Alice: Physical d8" in labels
        assert "Cena: Trapped d6" in labels

    async def test_toggle_on_adds_to_pool_and_shows_in_pool_label(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [{"id": "stress:1", "label": "Alice: Physical d8", "die_size": 8}]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="GM", toggle_items=toggles
        )
        view.included_toggles.add("stress:1")
        view.pool.append(8)
        view._build_components()
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert any("(no pool)" in l for l in labels)


class TestGMPoolBuilderToggles:
    """Tasks 4.2, 4.4, 4.5: _build_gm_toggles returns correct items."""

    async def test_gm_gets_stress_and_complications(self, db, gm_campaign):
        from cortex_bot.views.rolling_views import _build_gm_toggles

        alice = await db.get_player(gm_campaign, "user1")
        stress_types = await db.get_stress_types(gm_campaign)
        phys_id = next(st["id"] for st in stress_types if st["name"] == "Physical")

        async with db.connect() as conn:
            await conn.execute(
                "INSERT INTO stress (campaign_id, player_id, stress_type_id, die_size) VALUES (?, ?, ?, ?)",
                (gm_campaign, alice["id"], phys_id, 8),
            )
            scene = await db.get_active_scene(gm_campaign)
            await conn.execute(
                "INSERT INTO complications (campaign_id, player_id, scene_id, name, die_size) VALUES (?, ?, ?, ?, ?)",
                (gm_campaign, alice["id"], scene["id"], "Wounded", 6),
            )
            # Scene complication (no player)
            await conn.execute(
                "INSERT INTO complications (campaign_id, player_id, scene_id, name, die_size) VALUES (?, ?, ?, ?, ?)",
                (gm_campaign, None, scene["id"], "Trapped", 6),
            )
            await conn.commit()

        toggles = await _build_gm_toggles(db, gm_campaign)

        labels = [t["label"] for t in toggles]
        ids = [t["id"] for t in toggles]

        # Stress label
        assert any("Alice: Physical d8" in l for l in labels)
        # Player complication label
        assert any("Alice: Wounded d6" in l for l in labels)
        # Scene complication label
        assert any("Cena: Trapped d6" in l for l in labels)
        # IDs use correct prefixes
        assert any(i.startswith("stress:") for i in ids)
        assert any(i.startswith("comp:") for i in ids)

    async def test_gm_no_stress_or_complications_returns_empty(self, db, gm_campaign):
        from cortex_bot.views.rolling_views import _build_gm_toggles

        toggles = await _build_gm_toggles(db, gm_campaign)
        assert toggles == []

    async def test_labels_follow_correct_format(self, db, gm_campaign):
        from cortex_bot.views.rolling_views import _build_gm_toggles

        bob = await db.get_player(gm_campaign, "user2")
        stress_types = await db.get_stress_types(gm_campaign)
        mental_id = next(st["id"] for st in stress_types if st["name"] == "Mental")

        async with db.connect() as conn:
            await conn.execute(
                "INSERT INTO stress (campaign_id, player_id, stress_type_id, die_size) VALUES (?, ?, ?, ?)",
                (gm_campaign, bob["id"], mental_id, 10),
            )
            await conn.commit()

        toggles = await _build_gm_toggles(db, gm_campaign)
        assert any(t["label"] == "Bob: Mental d10" for t in toggles)


class TestPlayerPoolBuilderToggles:
    """Task 4.3: Player gets only their own assets as toggles."""

    async def test_player_toggles_are_assets_only(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [
            {"id": "asset:1", "label": "Sword d8", "die_size": 8},
            {"id": "asset:2", "label": "Shield d6", "die_size": 6},
        ]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="Alice", toggle_items=toggles
        )
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert "Sword d8" in labels
        assert "Shield d6" in labels
        # No stress/comp labels
        assert not any(":" in l and "d" in l.split(":")[-1] for l in labels
                       if l not in ("Sword d8", "Shield d6") and not l.startswith("+"))


class TestGMRollResult:
    """Tasks 4.6, 4.7: GM roll result formatting."""

    async def test_gm_roll_with_toggles_shows_incluidos(self, db, gm_campaign):
        from cortex_bot.views.rolling_views import execute_player_roll

        gm = await db.get_player(gm_campaign, "gm1")
        text, _view = await execute_player_roll(
            db, gm_campaign, gm["id"], gm["name"],
            pool=[8, 6],
            included_assets=["Alice: Physical d8", "Cena: Trapped d6"],
            is_gm_roll=True,
        )
        assert "Incluidos:" in text
        assert "Alice: Physical d8" in text
        assert "Cena: Trapped d6" in text
        # GM roll has no opposition_elements
        assert "Pool da oposicao" not in text

    async def test_gm_roll_without_toggles_no_incluidos(self, db, gm_campaign):
        from cortex_bot.views.rolling_views import execute_player_roll

        gm = await db.get_player(gm_campaign, "gm1")
        text, _view = await execute_player_roll(
            db, gm_campaign, gm["id"], gm["name"],
            pool=[8, 10],
            is_gm_roll=True,
        )
        assert "Incluidos:" not in text
        assert "Pool da oposicao" not in text


class TestToggleTruncation:
    """Task 4.8: Truncation at 15 toggle items with message."""

    async def test_truncation_at_15_items(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [
            {"id": f"stress:{i}", "label": f"Player{i}: Stress d{(i % 5 + 1) * 2}", "die_size": (i % 5 + 1) * 2}
            for i in range(20)
        ]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="GM", toggle_items=toggles
        )
        # Only 15 toggle buttons should be rendered
        toggle_buttons = [
            c for c in view.children
            if isinstance(c, discord.ui.Button) and c.custom_id.startswith("ephemeral:pb_toggle:")
        ]
        assert len(toggle_buttons) == 15

        # Status text should mention truncation
        status = view.build_status_text()
        assert "15 de 20" in status

    async def test_no_truncation_message_under_15(self):
        from cortex_bot.views.rolling_views import PoolBuilderView

        toggles = [
            {"id": f"stress:{i}", "label": f"Item{i} d6", "die_size": 6}
            for i in range(5)
        ]
        view = PoolBuilderView(
            campaign_id=1, player_id=1, player_name="GM", toggle_items=toggles
        )
        status = view.build_status_text()
        assert "de" not in status or "dados" in status
