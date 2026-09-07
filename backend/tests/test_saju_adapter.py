from datetime import date, time

from app.adapters.saju import MockSajuAdapter


def test_same_input_produces_same_result():
    adapter = MockSajuAdapter()
    result1 = adapter.analyze(date(1990, 5, 20), time(10, 30))
    result2 = adapter.analyze(date(1990, 5, 20), time(10, 30))
    assert result1.five_elements == result2.five_elements


def test_five_elements_cover_all_five_and_sum_to_eight():
    adapter = MockSajuAdapter()
    result = adapter.analyze(date(1990, 5, 20), time(10, 30))
    assert set(result.five_elements.keys()) == {"목", "화", "토", "금", "수"}
    assert sum(result.five_elements.values()) == 8


def test_missing_and_excess_elements_match_distribution_extremes():
    adapter = MockSajuAdapter()
    result = adapter.analyze(date(1990, 5, 20), time(10, 30))
    min_count = min(result.five_elements.values())
    max_count = max(result.five_elements.values())
    assert result.missing_elements
    assert result.excess_elements
    assert all(result.five_elements[e] == min_count for e in result.missing_elements)
    assert all(result.five_elements[e] == max_count for e in result.excess_elements)


def test_different_birth_time_changes_result():
    adapter = MockSajuAdapter()
    result1 = adapter.analyze(date(1990, 5, 20), time(10, 30))
    result2 = adapter.analyze(date(1990, 5, 20), time(22, 45))
    assert result1.five_elements != result2.five_elements


def test_different_birth_date_changes_result():
    adapter = MockSajuAdapter()
    result1 = adapter.analyze(date(1990, 5, 20), time(10, 30))
    result2 = adapter.analyze(date(1985, 11, 3), time(10, 30))
    assert result1.five_elements != result2.five_elements


def test_missing_birth_time_still_produces_valid_result():
    adapter = MockSajuAdapter()
    result = adapter.analyze(date(1990, 5, 20), None)
    assert sum(result.five_elements.values()) == 8


def test_sinsal_is_empty_for_phase1():
    adapter = MockSajuAdapter()
    result = adapter.analyze(date(1990, 5, 20), time(10, 30))
    assert result.sinsal == []
