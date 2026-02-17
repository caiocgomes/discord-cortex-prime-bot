"""Tests for undo feedback formatting."""

from cortex_bot.cogs.undo import _format_undo_message


class TestFormatUndoMessage:
    def test_add_asset(self):
        msg = _format_undo_message("add_asset", {
            "id": 1, "name": "Big Wrench", "die_size": 8, "player": "Alice",
        })
        assert "Asset 'Big Wrench' d8 added to Alice" == msg

    def test_remove_asset(self):
        msg = _format_undo_message("remove_asset", {
            "id": 1, "name": "Shield", "player": "Bob",
        })
        assert "Asset 'Shield' removed from Bob" == msg

    def test_step_up_stress(self):
        msg = _format_undo_message("step_up_stress", {
            "id": 1, "player": "Alice", "type": "Physical", "from": 6, "to": 8,
        })
        assert "Stress Physical stepped up (d6 to d8) on Alice" == msg

    def test_add_stress(self):
        msg = _format_undo_message("add_stress", {
            "id": 1, "player": "Alice", "type": "Mental", "die_size": 6,
        })
        assert "Stress Mental d6 added to Alice" == msg

    def test_doom_add(self):
        msg = _format_undo_message("doom_add", {"die_size": 8})
        assert "Doom Pool: d8 added" == msg

    def test_doom_stepdown_eliminated(self):
        msg = _format_undo_message("doom_stepdown_eliminated", {"was": 4})
        assert "Doom Pool: d4 eliminated" == msg

    def test_update_pp(self):
        msg = _format_undo_message("update_pp", {
            "player": "Alice", "from": 3, "to": 5,
        })
        assert "Alice PP: 3 to 5" == msg

    def test_step_down_stress_eliminated(self):
        msg = _format_undo_message("step_down_stress_eliminated", {
            "id": 1, "player": "Alice", "type": "Physical", "was": 4,
        })
        assert "Stress Physical eliminated from Alice (was d4)" == msg

    def test_unknown_action_fallback(self):
        msg = _format_undo_message("some_future_action", {
            "id": 99, "foo": "bar", "baz": 42,
        })
        assert "some_future_action" in msg
        assert "foo=bar" in msg
        assert "baz=42" in msg
        assert "id=" not in msg

    def test_unknown_action_empty_data(self):
        msg = _format_undo_message("mystery", {"id": 1})
        assert msg == "mystery"

    def test_template_key_error_fallback(self):
        # Missing required keys should fall back to technical format
        msg = _format_undo_message("add_asset", {"id": 1})
        assert "add_asset" in msg
