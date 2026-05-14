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


def build_standings(rows: list[dict]) -> list[dict]:
    """Build a full league table from all matches in the CSV."""
    # Sort by date so each team's form sequence is chronological. Rows without
    # a parseable date keep their original order at the end.
    def _date_key(row):
        try:
            return (0, datetime.strptime(row.get("Date", ""), "%d/%m/%Y"))
        except ValueError:
            return (1, datetime.min)

    ordered_rows = sorted(rows, key=_date_key)

    teams: dict[str, dict] = {}
    for row in ordered_rows:
        home = row.get("HomeTeam", "")
        away = row.get("AwayTeam", "")
        if not home or not away:
            continue
        hg = int(row["FTHG"])
        ag = int(row["FTAG"])
        ftr = row["FTR"]

        for name in (home, away):
            if name not in teams:
                teams[name] = {"team": name, "P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "_form": []}

        teams[home]["P"] += 1
        teams[away]["P"] += 1
        teams[home]["GF"] += hg
        teams[home]["GA"] += ag
        teams[away]["GF"] += ag
        teams[away]["GA"] += hg

        if ftr == "H":
            teams[home]["W"] += 1
            teams[away]["L"] += 1
            teams[home]["_form"].append("W")
            teams[away]["_form"].append("L")
        elif ftr == "A":
            teams[away]["W"] += 1
            teams[home]["L"] += 1
            teams[away]["_form"].append("W")
            teams[home]["_form"].append("L")
        else:
            teams[home]["D"] += 1
            teams[away]["D"] += 1
            teams[home]["_form"].append("D")
            teams[away]["_form"].append("D")

    table = []
    for t in teams.values():
        t["GD"] = t["GF"] - t["GA"]
        t["Pts"] = t["W"] * 3 + t["D"]
        t["Form"] = "".join(t.pop("_form")[-5:])
        table.append(t)

    table.sort(key=lambda t: (-t["Pts"], -t["GD"], -t["GF"]))
    for i, t in enumerate(table, 1):
        t["Pos"] = i

    return table


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

    rows = fetch_season_csv(args.season, args.league)

    matches = [summarize(r) for r in rows]
    matches = [m for m in matches if m is not None]
    matches.sort(key=lambda m: m["date"])
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(matches, f, indent=2)
    print(f"Saved {len(matches)} matches to {DATA_PATH}")

    standings = build_standings(rows)
    with open(STANDINGS_PATH, "w") as f:
        json.dump(standings, f, indent=2)
    print(f"Saved {len(standings)}-team standings to {STANDINGS_PATH}")
