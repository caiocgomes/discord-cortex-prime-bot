import pytest

from cortex_bot.models.dice import (
    is_valid_die,
    step_up,
    step_down,
    die_label,
    parse_dice_notation,
    parse_single_die,
)


class TestIsValidDie:
    def test_valid_sizes(self):
        for size in (4, 6, 8, 10, 12):
            assert is_valid_die(size) is True

    def test_invalid_sizes(self):
        for size in (0, 1, 2, 3, 5, 7, 14, 20):
            assert is_valid_die(size) is False


class TestStepUp:
    def test_d4_to_d6(self):
        assert step_up(4) == 6

    def test_d6_to_d8(self):
        assert step_up(6) == 8

    def test_d8_to_d10(self):
        assert step_up(8) == 10

    def test_d10_to_d12(self):
        assert step_up(10) == 12

    def test_d12_returns_none(self):
        assert step_up(12) is None


class TestStepDown:
    def test_d12_to_d10(self):
        assert step_down(12) == 10

    def test_d10_to_d8(self):
        assert step_down(10) == 8

    def test_d8_to_d6(self):
        assert step_down(8) == 6

    def test_d6_to_d4(self):
        assert step_down(6) == 4

    def test_d4_returns_none(self):
        assert step_down(4) is None


class TestDieLabel:
    def test_labels(self):
        assert die_label(4) == "d4"
        assert die_label(12) == "d12"


class TestParseDiceNotation:
    def test_single_die(self):
        assert parse_dice_notation("1d8") == [8]

    def test_multiple_same(self):
        assert parse_dice_notation("3d6") == [6, 6, 6]

    def test_mixed(self):
        result = parse_dice_notation("1d8 2d6 1d10")
        assert sorted(result) == [6, 6, 8, 10]

    def test_no_count_prefix(self):
        assert parse_dice_notation("d8") == [8]

    def test_case_insensitive(self):
        assert parse_dice_notation("1D8 2D6") == [8, 6, 6]

    def test_invalid_die_size(self):
        with pytest.raises(ValueError, match="d20"):
            parse_dice_notation("1d20")

    def test_no_dice(self):
        with pytest.raises(ValueError, match="No valid dice"):
            parse_dice_notation("hello")


class TestParseSingleDie:
    def test_with_d_prefix(self):
        assert parse_single_die("d8") == 8

    def test_without_d_prefix(self):
        assert parse_single_die("10") == 10

    def test_uppercase(self):
        assert parse_single_die("D12") == 12

    def test_with_spaces(self):
        assert parse_single_die("  d6  ") == 6

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_single_die("d20")
