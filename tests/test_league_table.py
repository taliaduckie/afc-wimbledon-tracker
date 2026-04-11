"""Tests for league_table.build_table() and form_string()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from league_table import build_table, form_string

SAMPLE_RESULTS = [
    {"date": "2025-01-01", "home": "AFC Wimbledon", "away": "Crawley", "home_score": 2, "away_score": 0, "result": "W"},
    {"date": "2025-01-08", "home": "Barrow", "away": "AFC Wimbledon", "home_score": 1, "away_score": 1, "result": "D"},
    {"date": "2025-01-15", "home": "AFC Wimbledon", "away": "Gillingham", "home_score": 0, "away_score": 3, "result": "L"},
    {"date": "2025-01-22", "home": "Swindon", "away": "AFC Wimbledon", "home_score": 0, "away_score": 2, "result": "W"},
    {"date": "2025-01-29", "home": "AFC Wimbledon", "away": "Doncaster", "home_score": 1, "away_score": 1, "result": "D"},
]


# --- build_table ---

def test_build_table_played():
    stats = build_table(SAMPLE_RESULTS)
    assert stats["P"] == 5


def test_build_table_record():
    stats = build_table(SAMPLE_RESULTS)
    assert stats["W"] == 2
    assert stats["D"] == 2
    assert stats["L"] == 1


def test_build_table_goals():
    stats = build_table(SAMPLE_RESULTS)
    # Home: 2+0+1=3 GF, 0+3+1=4 GA  Away: 1+2=3 GF, 1+0=1 GA
    assert stats["GF"] == 6
    assert stats["GA"] == 5


def test_build_table_derived():
    stats = build_table(SAMPLE_RESULTS)
    assert stats["GD"] == stats["GF"] - stats["GA"]
    assert stats["Pts"] == stats["W"] * 3 + stats["D"]


def test_build_table_points():
    stats = build_table(SAMPLE_RESULTS)
    assert stats["Pts"] == 8  # 2*3 + 2*1


def test_build_table_empty():
    stats = build_table([])
    assert stats["P"] == 0
    assert stats["Pts"] == 0
    assert stats["GD"] == 0


# --- form_string ---

def test_form_string_default():
    form = form_string(SAMPLE_RESULTS)
    assert form == "WDLWD"


def test_form_string_last_3():
    form = form_string(SAMPLE_RESULTS, last_n=3)
    assert form == "LWD"


def test_form_string_last_1():
    form = form_string(SAMPLE_RESULTS, last_n=1)
    assert form == "D"


def test_form_string_more_than_available():
    form = form_string(SAMPLE_RESULTS, last_n=100)
    assert form == "WDLWD"


def test_form_string_empty():
    form = form_string([])
    assert form == ""
