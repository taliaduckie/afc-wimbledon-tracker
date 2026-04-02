"""
fixtures.py
Fetch and display upcoming AFC Wimbledon fixtures from football-data.org.

Usage:
    python src/fixtures.py
    python src/fixtures.py --next 3   # show only the next 3 matches
"""

import argparse
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
TEAM_ID = 57  # AFC Wimbledon — verify this is current
BASE_URL = "https://api.football-data.org/v4"
TEAM = "AFC Wimbledon"


def fetch_upcoming(limit: int | None = None) -> list[dict]:
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/teams/{TEAM_ID}/matches?status=SCHEDULED"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    matches = resp.json().get("matches", [])
    matches.sort(key=lambda m: m["utcDate"])
    if limit:
        matches = matches[:limit]
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
    table.add_column("Competition")

    for m in matches:
        dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        comp = m.get("competition", {}).get("name", "")

        home_style = "bold cyan" if home == TEAM else ""
        away_style = "bold cyan" if away == TEAM else ""

        table.add_row(
            dt.strftime("%a %d %b"),
            dt.strftime("%H:%M"),
            f"[{home_style}]{home}[/{home_style}]" if home_style else home,
            "vs",
            f"[{away_style}]{away}[/{away_style}]" if away_style else away,
            comp,
        )

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--next", type=int, dest="limit", help="Show only the next N fixtures")
    args = parser.parse_args()

    matches = fetch_upcoming(limit=args.limit)
    display(matches)
