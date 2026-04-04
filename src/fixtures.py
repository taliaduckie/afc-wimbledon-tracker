"""
fixtures.py
Fetch and display upcoming AFC Wimbledon fixtures from TheSportsDB.

Uses the round-based endpoint since the team-based one has a known bug.
No API key needed.

Usage:
    python src/fixtures.py
    python src/fixtures.py --next 3
"""

import argparse
import time
from datetime import datetime

import requests
from rich.console import Console
from rich.table import Table

TEAM = "AFC Wimbledon"
TEAM_ID = 134241
LEAGUE_ID = 4396  # English League 1
SEASON = "2025-2026"
TOTAL_ROUNDS = 46
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"


def _last_round() -> int:
    """Get the most recent round played from the last results endpoint."""
    url = f"{BASE_URL}/eventslast.php?id={TEAM_ID}"
    resp = requests.get(url)
    if resp.status_code == 200 and resp.text.strip():
        results = resp.json().get("results") or []
        if results:
            return int(results[0].get("intRound", 1))
    return 1


def _fetch_round(round_num: int) -> list[dict]:
    """Fetch events for a single round, returning [] on error."""
    url = f"{BASE_URL}/eventsround.php?id={LEAGUE_ID}&r={round_num}&s={SEASON}"
    resp = requests.get(url)
    if resp.status_code != 200 or not resp.text.strip():
        return []
    try:
        return resp.json().get("events") or []
    except requests.exceptions.JSONDecodeError:
        return []


def fetch_upcoming(limit: int | None = None) -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    start = _last_round()
    matches = []

    for r in range(start, TOTAL_ROUNDS + 1):
        events = _fetch_round(r)
        for e in events:
            if TEAM in (e.get("strHomeTeam", ""), e.get("strAwayTeam", "")):
                if e.get("dateEvent", "") >= today and e.get("intHomeScore") is None:
                    matches.append(e)
        if limit and len(matches) >= limit:
            matches = matches[:limit]
            break
        time.sleep(0.5)

    matches.sort(key=lambda e: e.get("dateEvent", ""))
    return matches


def display(matches: list[dict]):
    console = Console()
    if not matches:
        console.print("[dim]No upcoming fixtures found.[/dim]")
        return

    table = Table(title="Upcoming Fixtures")
    table.add_column("Date", style="bold")
    table.add_column("Time")
    table.add_column("Home")
    table.add_column("", justify="center")
    table.add_column("Away")
    table.add_column("Venue")

    for m in matches:
        date_str = m.get("dateEvent", "")
        time_str = m.get("strTime", "")[:5] or "TBD"
        home = m.get("strHomeTeam", "")
        away = m.get("strAwayTeam", "")
        venue = m.get("strVenue", "")

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            date_display = dt.strftime("%a %d %b")
        except ValueError:
            date_display = date_str

        home_style = "bold cyan" if home == TEAM else ""
        away_style = "bold cyan" if away == TEAM else ""

        table.add_row(
            date_display,
            time_str,
            f"[{home_style}]{home}[/{home_style}]" if home_style else home,
            "vs",
            f"[{away_style}]{away}[/{away_style}]" if away_style else away,
            venue,
        )

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--next", type=int, dest="limit", help="Show only the next N fixtures")
    args = parser.parse_args()

    matches = fetch_upcoming(limit=args.limit)
    display(matches)
