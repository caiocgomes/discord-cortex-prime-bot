"""Tests for the views module: custom_id parsing, view composition, and DynamicItem patterns."""

import re

import discord
import pytest

from cortex_bot.views.base import parse_custom_id, make_custom_id, CortexView


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
# Tests for add_die_buttons helper (Task 1.3)
# ---------------------------------------------------------------------------


class TestAddDieButtons:
    async def test_adds_five_buttons(self):
        from cortex_bot.views.base import CortexView, add_die_buttons

        view = CortexView()

        async def noop(inter, size):
            pass

        add_die_buttons(view, noop)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_button_labels(self):
        from cortex_bot.views.base import CortexView, add_die_buttons

        view = CortexView()

        async def noop(inter, size):
            pass

        add_die_buttons(view, noop)
        labels = [c.label for c in view.children if isinstance(c, discord.ui.Button)]
        assert labels == ["d4", "d6", "d8", "d10", "d12"]


# ---------------------------------------------------------------------------
# Tests for add_player_options helper (Task 1.3)
# ---------------------------------------------------------------------------


class TestAddPlayerOptions:
    async def test_uses_buttons_for_5_or_fewer(self):
        from cortex_bot.views.base import CortexView, add_player_options

        view = CortexView()
        players = [{"id": i, "name": f"P{i}"} for i in range(5)]

        async def noop(inter, pid):
            pass

        add_player_options(view, players, noop)
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 5

    async def test_uses_select_for_more_than_5(self):
        from cortex_bot.views.base import CortexView, add_player_options

        view = CortexView()
        players = [{"id": i, "name": f"P{i}"} for i in range(6)]

        async def noop(inter, pid):
            pass

        add_player_options(view, players, noop)
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        assert len(selects) == 1
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 0

    async def test_extra_buttons_added(self):
        from cortex_bot.views.base import CortexView, add_player_options

        view = CortexView()
        players = [{"id": 1, "name": "Alice"}]

        async def noop(inter, val):
            pass

        add_player_options(view, players, noop, extra_buttons=[("Scene Asset", "scene")])
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(buttons) == 2  # Alice + Scene Asset
        labels = [b.label for b in buttons]
        assert "Scene Asset" in labels

    async def test_extra_buttons_with_select(self):
        from cortex_bot.views.base import CortexView, add_player_options

        view = CortexView()
        players = [{"id": i, "name": f"P{i}"} for i in range(6)]

        async def noop(inter, val):
            pass

        add_player_options(view, players, noop, extra_buttons=[("Scene", "scene")])
        selects = [c for c in view.children if isinstance(c, discord.ui.Select)]
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        assert len(selects) == 1
        assert len(buttons) == 1  # only the extra button


# ---------------------------------------------------------------------------
# Tests for DicePoolModal (Task 2.6)
# ---------------------------------------------------------------------------


class TestDicePoolModal:
    async def test_modal_has_two_fields(self):
        from cortex_bot.views.rolling_views import DicePoolModal

        modal = DicePoolModal(
            campaign_id=1, player_id=1, player_name="Alice", asset_hint="Nenhum"
        )
        text_inputs = [
            c for c in modal.children if isinstance(c, discord.ui.TextInput)
        ]
        assert len(text_inputs) == 2

    async def test_modal_first_field_required(self):
        from cortex_bot.views.rolling_views import DicePoolModal

        modal = DicePoolModal(
            campaign_id=1, player_id=1, player_name="Alice", asset_hint="Nenhum"
        )
        text_inputs = [
            c for c in modal.children if isinstance(c, discord.ui.TextInput)
        ]
        assert text_inputs[0].required is True

    async def test_modal_second_field_optional(self):
        from cortex_bot.views.rolling_views import DicePoolModal

        modal = DicePoolModal(
            campaign_id=1, player_id=1, player_name="Alice", asset_hint="Nenhum"
        )
        text_inputs = [
            c for c in modal.children if isinstance(c, discord.ui.TextInput)
        ]
        assert text_inputs[1].required is False

    async def test_modal_asset_hint_in_placeholder(self):
        from cortex_bot.views.rolling_views import DicePoolModal

        hint = "Disponiveis: Sword d8, Shield d6"
        modal = DicePoolModal(
            campaign_id=1, player_id=1, player_name="Alice", asset_hint=hint
        )
        text_inputs = [
            c for c in modal.children if isinstance(c, discord.ui.TextInput)
        ]
        assert text_inputs[1].placeholder == hint


# ---------------------------------------------------------------------------
# Tests for MenuView (Task 5.5)
# ---------------------------------------------------------------------------


class TestMenuView:
    async def test_menu_with_scene_has_roll_and_stress(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_scene=True, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:roll_start:1" in custom_ids
        assert "cortex:stress_add_start:1" in custom_ids
        assert "cortex:asset_add_start:1" in custom_ids
        assert "cortex:comp_add_start:1" in custom_ids
        assert "cortex:undo:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids

    async def test_menu_with_scene_and_doom(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_scene=True, doom_enabled=True)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:doom_add_start:1" in custom_ids
        assert any("doom_remove" in cid for cid in custom_ids)
        assert any("doom_roll" in cid for cid in custom_ids)

    async def test_menu_without_scene(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_scene=False, doom_enabled=False)
        custom_ids = [item.custom_id for item in view.children]
        assert "cortex:scene_start:1" in custom_ids
        assert "cortex:campaign_info:1" in custom_ids
        assert "cortex:roll_start:1" not in custom_ids

    async def test_menu_without_scene_no_doom(self):
        from cortex_bot.cogs.menu import MenuView

        view = MenuView(campaign_id=1, has_scene=False, doom_enabled=True)
        custom_ids = [item.custom_id for item in view.children]
        # doom buttons should NOT appear without scene
        assert not any("doom" in cid for cid in custom_ids)
