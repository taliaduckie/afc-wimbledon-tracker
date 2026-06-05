"""Tests for season metadata and the takeaway summary."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import season


def _table(wimbledon_pos, wimbledon_pts, releg_pts=40, n=24, games=46):
    """Build a minimal standings list placing Wimbledon at a given spot."""
    rows = []
    for pos in range(1, n + 1):
        if pos == wimbledon_pos:
            team, pts = season.TEAM, wimbledon_pts
        elif pos == season.RELEGATION_START:
            team, pts = f"Team{pos}", releg_pts
        else:
            team, pts = f"Team{pos}", 50
        rows.append({"team": team, "Pos": pos, "Pts": pts, "P": games})
    return rows


# --- labels ---

def test_season_label():
    assert season.season_label(2025) == "2025/26"
    assert season.season_label(1999) == "1999/00"


def test_league_name():
    assert season.league_name("E2") == "League One"
    assert season.league_name("ZZ") == "ZZ"


def test_ordinal():
    assert season._ordinal(1) == "1st"
    assert season._ordinal(2) == "2nd"
    assert season._ordinal(11) == "11th"
    assert season._ordinal(19) == "19th"
    assert season._ordinal(22) == "22nd"


# --- meta ---

def test_build_meta_complete():
    standings = _table(19, 53, games=46)
    meta = season.build_meta(standings, 2025, "E2")
    assert meta["complete"] is True
    assert meta["league_name"] == "League One"
    assert meta["season_label"] == "2025/26"
    assert meta["teams"] == 24


def test_build_meta_in_progress():
    standings = _table(19, 30, games=20)
    meta = season.build_meta(standings, 2025, "E2")
    assert meta["complete"] is False


def test_status_label():
    assert season.status_label({"league_name": "League One", "season_label": "2025/26", "complete": True}) \
        == "League One 2025/26 — Final"
    assert "In Progress" in season.status_label(
        {"league_name": "League One", "season_label": "2025/26", "complete": False})
    assert season.status_label(None) == ""


# --- takeaway ---

def test_takeaway_safe_midtable():
    standings = _table(19, 53, releg_pts=49)
    meta = season.build_meta(standings, 2025, "E2")
    line = season.takeaway(standings, meta)
    assert "Finished 19th" in line
    assert "safe" in line
    assert "4 pts clear" in line  # 53 - 49


def test_takeaway_promotion():
    standings = _table(2, 95)
    line = season.takeaway(standings, season.build_meta(standings, 2025, "E2"))
    assert "automatic promotion" in line


def test_takeaway_playoffs():
    standings = _table(5, 80)
    line = season.takeaway(standings, season.build_meta(standings, 2025, "E2"))
    assert "playoff" in line


def test_takeaway_relegation():
    standings = _table(23, 30)
    line = season.takeaway(standings, season.build_meta(standings, 2025, "E2"))
    assert "relegated" in line


def test_takeaway_no_wimbledon():
    standings = [{"team": "Other", "Pos": 1, "Pts": 90, "P": 46}]
    assert season.takeaway(standings, None) == ""
