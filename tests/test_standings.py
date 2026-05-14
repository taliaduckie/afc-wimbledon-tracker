"""Tests for fetch_results.build_standings()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_results import build_standings


def _row(home, away, hg, ag, ftr, date=""):
    return {"HomeTeam": home, "AwayTeam": away, "FTHG": str(hg), "FTAG": str(ag), "FTR": ftr, "Date": date}


SAMPLE_ROWS = [
    _row("Team A", "Team B", 2, 0, "H"),
    _row("Team C", "Team A", 1, 1, "D"),
    _row("Team B", "Team C", 3, 1, "H"),
]


# --- basic aggregation ---

def test_standings_team_count():
    table = build_standings(SAMPLE_ROWS)
    assert len(table) == 3


def test_standings_positions_assigned():
    table = build_standings(SAMPLE_ROWS)
    positions = [t["Pos"] for t in table]
    assert positions == [1, 2, 3]


def test_standings_sorted_by_points():
    table = build_standings(SAMPLE_ROWS)
    points = [t["Pts"] for t in table]
    assert points == sorted(points, reverse=True)


def test_standings_team_a():
    table = build_standings(SAMPLE_ROWS)
    a = next(t for t in table if t["team"] == "Team A")
    # Beat B 2-0 (H), drew C 1-1 (A) => W1 D1 L0, GF 3 GA 1
    assert a["P"] == 2
    assert a["W"] == 1
    assert a["D"] == 1
    assert a["L"] == 0
    assert a["GF"] == 3
    assert a["GA"] == 1
    assert a["GD"] == 2
    assert a["Pts"] == 4


def test_standings_team_b():
    table = build_standings(SAMPLE_ROWS)
    b = next(t for t in table if t["team"] == "Team B")
    # Lost to A 0-2 (A), beat C 3-1 (H) => W1 D0 L1, GF 3 GA 3
    assert b["P"] == 2
    assert b["W"] == 1
    assert b["L"] == 1
    assert b["GF"] == 3
    assert b["GA"] == 3
    assert b["GD"] == 0
    assert b["Pts"] == 3


def test_standings_team_c():
    table = build_standings(SAMPLE_ROWS)
    c = next(t for t in table if t["team"] == "Team C")
    # Drew A 1-1 (H), lost to B 1-3 (A) => W0 D1 L1, GF 2 GA 4
    assert c["P"] == 2
    assert c["W"] == 0
    assert c["D"] == 1
    assert c["L"] == 1
    assert c["GF"] == 2
    assert c["GA"] == 4
    assert c["GD"] == -2
    assert c["Pts"] == 1


# --- sorting tiebreakers ---

def test_standings_tiebreak_gd():
    """Teams with equal points should be sorted by GD."""
    rows = [
        _row("Team A", "Team B", 3, 0, "H"),  # A: W, GD +3
        _row("Team C", "Team D", 1, 0, "H"),  # C: W, GD +1
        _row("Team B", "Team D", 0, 0, "D"),  # filler
        _row("Team A", "Team C", 0, 0, "D"),  # both draw
    ]
    table = build_standings(rows)
    # A: 4pts GD+3, C: 4pts GD+1
    a = next(t for t in table if t["team"] == "Team A")
    c = next(t for t in table if t["team"] == "Team C")
    assert a["Pos"] < c["Pos"]


# --- edge cases ---

def test_standings_empty():
    table = build_standings([])
    assert table == []


def test_standings_single_match():
    rows = [_row("X", "Y", 1, 0, "H")]
    table = build_standings(rows)
    assert len(table) == 2
    x = next(t for t in table if t["team"] == "X")
    y = next(t for t in table if t["team"] == "Y")
    assert x["Pts"] == 3
    assert y["Pts"] == 0
    assert x["Pos"] == 1
    assert y["Pos"] == 2


def test_standings_all_draws():
    rows = [
        _row("A", "B", 0, 0, "D"),
        _row("B", "A", 1, 1, "D"),
    ]
    table = build_standings(rows)
    a = next(t for t in table if t["team"] == "A")
    b = next(t for t in table if t["team"] == "B")
    assert a["Pts"] == b["Pts"] == 2
    assert a["W"] == b["W"] == 0


# --- form ---

def test_standings_form_last_five():
    """Form should be the last 5 results in chronological order."""
    rows = [
        _row("A", "B", 1, 0, "H", "01/08/2024"),  # A W, B L
        _row("A", "C", 2, 1, "H", "08/08/2024"),  # A W
        _row("A", "D", 0, 0, "D", "15/08/2024"),  # A D
        _row("E", "A", 1, 0, "H", "22/08/2024"),  # A L
        _row("A", "F", 3, 1, "H", "29/08/2024"),  # A W
        _row("G", "A", 2, 2, "D", "05/09/2024"),  # A D — 6th match, oldest 'W' drops off
    ]
    table = build_standings(rows)
    a = next(t for t in table if t["team"] == "A")
    assert a["Form"] == "WDLWD"


def test_standings_form_shorter_than_five():
    """Teams with fewer than 5 matches should have a shorter form string."""
    rows = [_row("X", "Y", 1, 0, "H", "01/08/2024")]
    table = build_standings(rows)
    x = next(t for t in table if t["team"] == "X")
    y = next(t for t in table if t["team"] == "Y")
    assert x["Form"] == "W"
    assert y["Form"] == "L"


def test_standings_form_uses_date_order_not_row_order():
    """Even if rows are passed out of order, form follows match date."""
    rows = [
        _row("A", "B", 3, 0, "H", "15/09/2024"),  # later
        _row("A", "B", 0, 1, "A", "01/08/2024"),  # earlier
    ]
    table = build_standings(rows)
    a = next(t for t in table if t["team"] == "A")
    assert a["Form"] == "LW"


def test_standings_skips_empty_team_names():
    rows = [
        _row("", "Team A", 1, 0, "H"),
        _row("Team A", "Team B", 2, 1, "H"),
    ]
    table = build_standings(rows)
    teams = [t["team"] for t in table]
    assert "" not in teams
