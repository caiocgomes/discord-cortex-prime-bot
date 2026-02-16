"""Tests for the help cog content."""

from cortex_bot.cogs.help import HELP_TOPICS, HELP_GERAL, HELP_GM, HELP_JOGADOR, HELP_ROLAGEM


class TestHelpContent:
    def test_all_topics_present(self):
        assert set(HELP_TOPICS.keys()) == {"geral", "gm", "jogador", "rolagem"}

    def test_geral_mentions_lifecycle(self):
        assert "/campaign setup" in HELP_GERAL
        assert "/scene start" in HELP_GERAL
        assert "/roll" in HELP_GERAL

    def test_geral_mentions_subtopics(self):
        assert "/help topic:gm" in HELP_GERAL
        assert "/help topic:jogador" in HELP_GERAL
        assert "/help topic:rolagem" in HELP_GERAL

    def test_gm_organized_by_moment(self):
        assert "Setup da campanha:" in HELP_GM
        assert "Durante a cena:" in HELP_GM
        assert "Entre cenas:" in HELP_GM
        assert "Administracao:" in HELP_GM

    def test_gm_has_examples(self):
        assert "/campaign setup name:" in HELP_GM
        assert "/stress add player:" in HELP_GM
        assert "/scene start name:" in HELP_GM

    def test_jogador_omits_gm_only(self):
        assert "/campaign setup" not in HELP_JOGADOR
        assert "/stress add" not in HELP_JOGADOR
        assert "/doom" not in HELP_JOGADOR
        assert "/campaign campaign_end" not in HELP_JOGADOR

    def test_jogador_includes_player_commands(self):
        assert "/roll" in HELP_JOGADOR
        assert "/asset" in HELP_JOGADOR
        assert "/pp" in HELP_JOGADOR
        assert "/campaign info" in HELP_JOGADOR

    def test_rolagem_covers_mechanics(self):
        assert "include" in HELP_ROLAGEM.lower()
        assert "extra" in HELP_ROLAGEM.lower()
        assert "dificuldade" in HELP_ROLAGEM.lower() or "difficulty" in HELP_ROLAGEM.lower()
        assert "hitch" in HELP_ROLAGEM.lower()
        assert "botch" in HELP_ROLAGEM.lower()
        assert "best mode" in HELP_ROLAGEM.lower()
        assert "effect die" in HELP_ROLAGEM.lower()
        assert "heroic success" in HELP_ROLAGEM.lower()

    def test_all_topics_are_linear_text(self):
        for topic, content in HELP_TOPICS.items():
            assert "|" not in content, f"Topic '{topic}' contains table-like formatting"
            assert "```" not in content, f"Topic '{topic}' contains code blocks"
