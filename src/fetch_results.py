"""
fetch_results.py
Fetch AFC Wimbledon match results from football-data.co.uk CSV files.
Saves to data/results.json.

Source: https://www.football-data.co.uk/englandm.php
League codes: E0=PL, E1=Championship, E2=League One, E3=League Two
"""

import csv
import io
import json
from datetime import datetime
from pathlib import Path

import requests

TEAM = "AFC Wimbledon"
LEAGUE = "E2"  # League One
BASE_URL = "https://www.football-data.co.uk/mmz4281"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_PATH = DATA_DIR / "results.json"
STANDINGS_PATH = DATA_DIR / "standings.json"


def season_code(start_year: int) -> str:
    """Convert e.g. 2024 -> '2425'."""
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def fetch_season_csv(start_year: int, league: str = LEAGUE) -> list[dict]:
    """Download and parse one season's CSV."""
    url = f"{BASE_URL}/{season_code(start_year)}/{league}.csv"
    resp = requests.get(url)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return list(reader)


def summarize(row: dict) -> dict | None:
    """Convert a CSV row into our standard match format. Returns None if not an AFC Wimbledon match."""
    home = row.get("HomeTeam", "")
    away = row.get("AwayTeam", "")
    if TEAM not in (home, away):
        return None

    home_score = int(row["FTHG"])
    away_score = int(row["FTAG"])

    # Parse date — format is DD/MM/YYYY
    date_str = row["Date"]
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        date = date_str

    ftr = row["FTR"]  # H=Home win, D=Draw, A=Away win
    if (home == TEAM and ftr == "H") or (away == TEAM and ftr == "A"):
        result = "W"
    elif ftr == "D":
        result = "D"
    else:
        result = "L"

    return {
        "date": date,
        "home": home,
        "away": away,
        "home_score": home_score,
        "away_score": away_score,
        "result": result,
    }


def fetch_matches(start_year: int = 2025, league: str = LEAGUE) -> list[dict]:
    rows = fetch_season_csv(start_year, league)
    matches = [summarize(r) for r in rows]
    return [m for m in matches if m is not None]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2025,
                        help="Season start year, e.g. 2024 for 2024/25 (default: 2025)")
    parser.add_argument("--league", default=LEAGUE,
                        help="League code: E0=PL, E1=Championship, E2=League One, E3=League Two (default: E2)")
    args = parser.parse_args()

    matches = fetch_matches(args.season, args.league)
    matches.sort(key=lambda m: m["date"])
    DATA_PATH.parent.mkdir(exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(matches, f, indent=2)
    print(f"Saved {len(matches)} matches to {DATA_PATH}")
