"""Tests for fetch_results.summarize()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_results import summarize, season_code


def _make_row(home, away, home_score, away_score, ftr, date="15/01/2025"):
    return {
        "Date": date,
        "HomeTeam": home,
        "AwayTeam": away,
        "FTHG": str(home_score),
        "FTAG": str(away_score),
        "FTR": ftr,
    }


def test_home_win():
    s = summarize(_make_row("AFC Wimbledon", "Crawley Town", 2, 0, "H"))
    assert s["result"] == "W"
    assert s["home_score"] == 2
    assert s["away_score"] == 0
    assert s["date"] == "2025-01-15"


def test_away_win():
    s = summarize(_make_row("Doncaster Rovers", "AFC Wimbledon", 1, 3, "A"))
    assert s["result"] == "W"


def test_home_loss():
    s = summarize(_make_row("AFC Wimbledon", "Barrow", 0, 2, "A"))
    assert s["result"] == "L"


def test_away_loss():
    s = summarize(_make_row("Gillingham", "AFC Wimbledon", 3, 1, "H"))
    assert s["result"] == "L"


def test_draw():
    s = summarize(_make_row("AFC Wimbledon", "Swindon Town", 1, 1, "D"))
    assert s["result"] == "D"


def test_away_draw():
    s = summarize(_make_row("Notts County", "AFC Wimbledon", 0, 0, "D"))
    assert s["result"] == "D"


def test_non_wimbledon_match_returns_none():
    s = summarize(_make_row("Barrow", "Crawley Town", 1, 0, "H"))
    assert s is None


def test_malformed_date_falls_back():
    s = summarize(_make_row("AFC Wimbledon", "Crawley Town", 1, 0, "H", date="not-a-date"))
    assert s["date"] == "not-a-date"


def test_season_code():
    assert season_code(2024) == "2425"
    assert season_code(1999) == "9900"


def test_season_code_century():
    assert season_code(2000) == "0001"
