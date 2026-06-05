"""
season.py
Shared season/league metadata for the CLI and dashboard

Single source of truth for league names and the League One zones
"""

import json
from pathlib import Path

TEAM = "AFC Wimbledon"
META_PATH = Path(__file__).parent.parent / "data" / "meta.json"

LEAGUE_NAMES = {
    "E0": "Premier League",
    "E1": "Championship",
    "E2": "League One",
    "E3": "League Two",
}

# League One zones (24-team league)
AUTO_PROMOTION = (1, 2)
PLAYOFFS = (3, 6)
RELEGATION_START = 21  # 21-24 relegated


def season_label(start_year: int) -> str:
    """2025 -> '2025/26'"""
    return f"{start_year}/{(start_year + 1) % 100:02d}"


def league_name(code: str) -> str:
    return LEAGUE_NAMES.get(code, code)


def _ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def build_meta(standings: list[dict], season: int, league: str) -> dict:
    """Summarise the dataset: season, league, whether it's complete"""
    n_teams = len(standings)
    expected_games = (n_teams - 1) * 2 if n_teams else 0
    wimbledon = next((r for r in standings if TEAM in r.get("team", "")), None)
    games = wimbledon["P"] if wimbledon else 0
    return {
        "season": season,
        "season_label": season_label(season),
        "league": league,
        "league_name": league_name(league),
        "teams": n_teams,
        "wimbledon_games": games,
        "expected_games": expected_games,
        "complete": bool(expected_games) and games >= expected_games,
    }


def load_meta() -> dict | None:
    if not META_PATH.exists():
        return None
    with open(META_PATH) as f:
        return json.load(f)


def save_meta(meta: dict) -> None:
    META_PATH.parent.mkdir(exist_ok=True)
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)


def status_label(meta: dict | None) -> str:
    """Header label e.g. 'League One 2025/26 — Final'"""
    if not meta:
        return ""
    state = "Final" if meta.get("complete") else "In Progress"
    return f"{meta.get('league_name', '')} {meta.get('season_label', '')} — {state}".strip()


def takeaway(standings: list[dict], meta: dict | None = None) -> str:
    """One-line summary of Wimbledon's position and what it means"""
    row = next((r for r in standings if TEAM in r.get("team", "")), None)
    if not row:
        return ""
    pos, pts = row["Pos"], row["Pts"]
    complete = bool(meta and meta.get("complete"))
    league = (meta or {}).get("league_name", "the league")
    verb = "Finished" if complete else "Currently"
    msg = f"{verb} {_ordinal(pos)} in {league} — {pts} pts"

    if pos <= AUTO_PROMOTION[1]:
        return msg + " — automatic promotion!"
    if pos <= PLAYOFFS[1]:
        return msg + " — in the playoff places"
    if pos >= RELEGATION_START:
        releg = "relegated" if complete else "in the relegation zone"
        return msg + f" — {releg}"

    # mid-table: cushion to the drop
    releg_row = next((r for r in standings if r["Pos"] == RELEGATION_START), None)
    if releg_row:
        cushion = pts - releg_row["Pts"]
        clear = "safe" if complete else "currently safe"
        return msg + f" — {clear}, {cushion} pts clear of the drop"
    return msg + " — mid-table"
