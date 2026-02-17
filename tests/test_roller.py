import pytest

from cortex_bot.services.roller import (
    roll_pool,
    find_hitches,
    is_botch,
    calculate_best_options,
    evaluate_difficulty,
)


class TestRollPool:
    def test_returns_correct_count(self):
        results = roll_pool([8, 6, 10])
        assert len(results) == 3

    def test_die_sizes_preserved(self):
        results = roll_pool([4, 6, 8, 10, 12])
        sizes = [s for s, _ in results]
        assert sizes == [4, 6, 8, 10, 12]

    def test_values_in_range(self):
        for _ in range(100):
            results = roll_pool([6])
            size, val = results[0]
            assert 1 <= val <= size


class TestFindHitches:
    def test_no_hitches(self):
        results = [(8, 5), (6, 3), (10, 7)]
        assert find_hitches(results) == []

    def test_one_hitch(self):
        results = [(8, 1), (6, 3), (10, 7)]
        assert find_hitches(results) == [(8, 1)]

    def test_multiple_hitches(self):
        results = [(8, 1), (6, 1), (10, 7)]
        hitches = find_hitches(results)
        assert len(hitches) == 2


class TestIsBotch:
    def test_all_ones(self):
        results = [(8, 1), (6, 1), (10, 1)]
        assert is_botch(results) is True

    def test_not_botch(self):
        results = [(8, 1), (6, 3), (10, 1)]
        assert is_botch(results) is False

    def test_no_ones(self):
        results = [(8, 5), (6, 3)]
        assert is_botch(results) is False


class TestCalculateBestOptions:
    def test_basic_four_dice(self):
        results = [(10, 7), (8, 5), (6, 4), (6, 3)]
        options = calculate_best_options(results)
        assert len(options) >= 1
        best = options[0]
        assert best["label"] == "Best total"
        assert best["total"] == 12  # 7 + 5

    def test_excludes_hitches(self):
        results = [(10, 7), (8, 1), (6, 4), (6, 3)]
        options = calculate_best_options(results)
        for opt in options:
            for die in opt["dice"]:
                assert die[1] != 1

    def test_single_non_hitch_returns_empty(self):
        results = [(8, 1), (6, 1), (10, 5)]
        options = calculate_best_options(results)
        assert options == []

    def test_two_dice(self):
        results = [(8, 5), (6, 3)]
        options = calculate_best_options(results)
        assert len(options) == 1
        assert options[0]["total"] == 8

    def test_best_total_vs_best_effect(self):
        # d12:7, d10:6, d8:5, d4:4
        results = [(12, 7), (10, 6), (8, 5), (4, 4)]
        options = calculate_best_options(results)
        totals = {o["label"]: o for o in options}
        if "Best total" in totals and "Best effect" in totals:
            assert totals["Best total"]["total"] >= totals["Best effect"]["total"]
            assert totals["Best effect"]["effect_size"] >= totals["Best total"]["effect_size"]


class TestEvaluateDifficulty:
    def test_success(self):
        result = evaluate_difficulty(12, 11)
        assert result["success"] is True
        assert result["margin"] == 1
        assert result["heroic"] is False

    def test_failure(self):
        result = evaluate_difficulty(10, 11)
        assert result["success"] is False
        assert result["margin"] == -1

    def test_tie_is_failure(self):
        result = evaluate_difficulty(11, 11)
        assert result["success"] is False

    def test_heroic_success(self):
        result = evaluate_difficulty(17, 11)
        assert result["success"] is True
        assert result["heroic"] is True
        assert result["heroic_steps"] == 1

    def test_heroic_success_two_steps(self):
        result = evaluate_difficulty(21, 11)
        assert result["heroic"] is True
        assert result["heroic_steps"] == 2

    def test_margin_4_not_heroic(self):
        result = evaluate_difficulty(15, 11)
        assert result["heroic"] is False
