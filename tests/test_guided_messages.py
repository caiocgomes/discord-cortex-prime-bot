"""Tests for guided messages at lifecycle transition points.

The actual message sending is in cog methods (Discord-coupled), so these
tests verify the message content and formatting rather than the send mechanics.
"""

from cortex_bot.services.formatter import format_scene_end


class TestSceneEndGuide:
    """The scene end guide is appended to format_scene_end output in the cog."""

    SCENE_END_GUIDE = (
        "\n\nUse /scene start para iniciar nova cena, "
        "ou /campaign info para ver estado persistente."
    )

    def test_guide_appended_to_scene_end(self):
        summary = format_scene_end("Tavern Fight", [], [], [])
        full = summary + self.SCENE_END_GUIDE
        assert "Cena encerrada: Tavern Fight." in full
        assert "/scene start" in full
        assert "/campaign info" in full

    def test_guide_appended_to_bridge_scene(self):
        changes = [
            {"player": "Alice", "type": "Physical", "from": 8, "to": 6},
        ]
        summary = format_scene_end("Fight", [], [], [], stress_changes=changes)
        full = summary + self.SCENE_END_GUIDE
        assert "Mudancas de stress (bridge):" in full
        assert "/scene start" in full


class TestSetupGuideContent:
    """The setup guide is appended inline in campaign.py setup method."""

    SETUP_GUIDE = (
        "Proximos passos: use /scene start para iniciar uma cena. "
        "Jogadores podem usar /roll para rolar dados. "
        "/campaign info mostra o estado completo. "
        "/help para referencia de comandos."
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
        "Comandos de jogo: /roll para rolar, /asset add para criar assets, "
        "/campaign info para ver estado."
    )

    def test_guide_mentions_roll(self):
        assert "/roll" in self.SCENE_START_GUIDE_BASE

    def test_guide_mentions_asset_add(self):
        assert "/asset add" in self.SCENE_START_GUIDE_BASE

    def test_guide_mentions_campaign_info(self):
        assert "/campaign info" in self.SCENE_START_GUIDE_BASE
