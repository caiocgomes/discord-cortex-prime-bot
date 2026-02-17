"""Tests for the help cog content."""

from cortex_bot.cogs.help import HELP_TOPICS, HELP_GENERAL, HELP_GM, HELP_PLAYER, HELP_ROLLING


class TestHelpContent:
    def test_all_topics_present(self):
        assert set(HELP_TOPICS.keys()) == {"general", "gm", "player", "rolling"}

    def test_general_mentions_lifecycle(self):
        assert "/campaign setup" in HELP_GENERAL
        assert "/scene start" in HELP_GENERAL
        assert "/roll" in HELP_GENERAL

    def test_general_mentions_subtopics(self):
        assert "/help topic:gm" in HELP_GENERAL
        assert "/help topic:player" in HELP_GENERAL
        assert "/help topic:rolling" in HELP_GENERAL

    def test_gm_organized_by_phase(self):
        assert "Campaign setup:" in HELP_GM
        assert "During a scene:" in HELP_GM
        assert "Between scenes:" in HELP_GM
        assert "Administration:" in HELP_GM

    def test_gm_has_examples(self):
        assert "/campaign setup name:" in HELP_GM
        assert "/stress add player:" in HELP_GM
        assert "/scene start name:" in HELP_GM

    def test_player_omits_gm_only(self):
        assert "/campaign setup" not in HELP_PLAYER
        assert "/stress add" not in HELP_PLAYER
        assert "/doom" not in HELP_PLAYER
        assert "/campaign end" not in HELP_PLAYER

    def test_player_includes_player_commands(self):
        assert "/roll" in HELP_PLAYER
        assert "/asset" in HELP_PLAYER
        assert "/pp" in HELP_PLAYER
        assert "/campaign info" in HELP_PLAYER

    def test_rolling_covers_mechanics(self):
        assert "include" in HELP_ROLLING.lower()
        assert "extra" in HELP_ROLLING.lower()
        assert "difficulty" in HELP_ROLLING.lower()
        assert "hitch" in HELP_ROLLING.lower()
        assert "botch" in HELP_ROLLING.lower()
        assert "best mode" in HELP_ROLLING.lower()
        assert "effect die" in HELP_ROLLING.lower()
        assert "heroic success" in HELP_ROLLING.lower()

    def test_all_topics_are_linear_text(self):
        for topic, content in HELP_TOPICS.items():
            assert "|" not in content, f"Topic '{topic}' contains table-like formatting"
            assert "```" not in content, f"Topic '{topic}' contains code blocks"
