"""Tests for fetch_results.summarize()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_results import summarize


def _make_match(home, away, home_score, away_score):
    return {
        "utcDate": "2025-01-15T15:00:00Z",
        "homeTeam": {"name": home},
        "awayTeam": {"name": away},
        "score": {"fullTime": {"home": home_score, "away": away_score}},
    }


def test_home_win():
    m = _make_match("AFC Wimbledon", "Crawley Town", 2, 0)
    s = summarize(m)
    assert s["result"] == "W"
    assert s["home_score"] == 2
    assert s["away_score"] == 0
    assert s["date"] == "2025-01-15"


def test_away_win():
    m = _make_match("Doncaster Rovers", "AFC Wimbledon", 1, 3)
    s = summarize(m)
    assert s["result"] == "W"


def test_home_loss():
    m = _make_match("AFC Wimbledon", "Barrow", 0, 2)
    s = summarize(m)
    assert s["result"] == "L"


def test_away_loss():
    m = _make_match("Gillingham", "AFC Wimbledon", 3, 1)
    s = summarize(m)
    assert s["result"] == "L"


def test_draw():
    m = _make_match("AFC Wimbledon", "Swindon Town", 1, 1)
    s = summarize(m)
    assert s["result"] == "D"


def test_away_draw():
    m = _make_match("Notts County", "AFC Wimbledon", 0, 0)
    s = summarize(m)
    assert s["result"] == "D"
