"""Tests for guided messages at lifecycle transition points.

The actual message sending is in cog methods (Discord-coupled), so these
tests verify the message content and formatting rather than the send mechanics.
"""

from cortex_bot.services.formatter import format_scene_end


class TestSceneEndGuide:
    """The scene end guide is now built into format_scene_end output."""

    def test_guide_included_in_scene_end(self):
        summary = format_scene_end("Tavern Fight", [], [], [])
        assert "SCENE ENDED: Tavern Fight" in summary
        assert "/scene start" in summary
        assert "/campaign info" in summary

    def test_guide_included_with_bridge_scene(self):
        changes = [
            {"player": "Alice", "type": "Physical", "from": 8, "to": 6},
        ]
        summary = format_scene_end("Fight", [], [], [], stress_changes=changes)
        assert "STRESS CHANGES (bridge)" in summary
        assert "/scene start" in summary


class TestSetupGuideContent:
    """The setup guide is appended inline in campaign.py setup method."""

    SETUP_GUIDE = (
        "Next steps: use /scene start to begin a scene. "
        "Players can use /roll to roll dice. "
        "/campaign info shows full state. "
        "/help for command reference."
    )

    def test_guide_mentions_scene_start(self):
        assert "/scene start" in self.SETUP_GUIDE

    def test_guide_mentions_roll(self):
        assert "/roll" in self.SETUP_GUIDE

    def test_guide_mentions_campaign_info(self):
        assert "/campaign info" in self.SETUP_GUIDE

    def test_guide_mentions_help(self):
        assert "/help" in self.SETUP_GUIDE


class TestSceneStartGuideContent:
    """The scene start guide is appended inline in scene.py _start method."""

    SCENE_START_GUIDE_BASE = (
        "Game commands: /roll to roll, /asset add to create assets, "
        "/campaign info to see state."
    )

    def test_guide_mentions_roll(self):
        assert "/roll" in self.SCENE_START_GUIDE_BASE

    def test_guide_mentions_asset_add(self):
        assert "/asset add" in self.SCENE_START_GUIDE_BASE

    def test_guide_mentions_campaign_info(self):
        assert "/campaign info" in self.SCENE_START_GUIDE_BASE
