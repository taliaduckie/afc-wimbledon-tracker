"""Tests for opponent_stats helper functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from opponent_stats import opponent_name, goal_diff, build_opponent_records

SAMPLE_RESULTS = [
    {"date": "2025-01-01", "home": "AFC Wimbledon", "away": "Crawley Town", "home_score": 2, "away_score": 0, "result": "W"},
    {"date": "2025-01-08", "home": "Crawley Town", "away": "AFC Wimbledon", "home_score": 1, "away_score": 1, "result": "D"},
    {"date": "2025-01-15", "home": "AFC Wimbledon", "away": "Barrow", "home_score": 0, "away_score": 3, "result": "L"},
    {"date": "2025-01-22", "home": "Gillingham", "away": "AFC Wimbledon", "home_score": 0, "away_score": 2, "result": "W"},
]


# --- opponent_name ---

def test_opponent_when_home():
    assert opponent_name(SAMPLE_RESULTS[0]) == "Crawley Town"


def test_opponent_when_away():
    assert opponent_name(SAMPLE_RESULTS[1]) == "Crawley Town"


# --- goal_diff ---

def test_gd_home_win():
    assert goal_diff(SAMPLE_RESULTS[0]) == 2


def test_gd_away_draw():
    assert goal_diff(SAMPLE_RESULTS[1]) == 0


def test_gd_home_loss():
    assert goal_diff(SAMPLE_RESULTS[2]) == -3


def test_gd_away_win():
    assert goal_diff(SAMPLE_RESULTS[3]) == 2


# --- build_opponent_records ---

def test_records_groups_by_opponent():
    records = build_opponent_records(SAMPLE_RESULTS)
    assert set(records.keys()) == {"Crawley Town", "Barrow", "Gillingham"}


def test_records_crawley():
    records = build_opponent_records(SAMPLE_RESULTS)
    r = records["Crawley Town"]
    assert r["P"] == 2
    assert r["W"] == 1
    assert r["D"] == 1
    assert r["L"] == 0
    assert r["GF"] == 3  # 2 + 1
    assert r["GA"] == 1  # 0 + 1


def test_records_barrow():
    records = build_opponent_records(SAMPLE_RESULTS)
    r = records["Barrow"]
    assert r["P"] == 1
    assert r["L"] == 1
    assert r["GF"] == 0
    assert r["GA"] == 3


def test_records_gillingham():
    records = build_opponent_records(SAMPLE_RESULTS)
    r = records["Gillingham"]
    assert r["P"] == 1
    assert r["W"] == 1
    assert r["GF"] == 2
    assert r["GA"] == 0


def test_records_empty():
    records = build_opponent_records([])
    assert records == {}


def test_records_single_match():
    single = [SAMPLE_RESULTS[0]]
    records = build_opponent_records(single)
    assert len(records) == 1
    assert "Crawley Town" in records
