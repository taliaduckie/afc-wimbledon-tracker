"""
fetch_results.py
Fetch AFC Wimbledon match results from football-data.org API.
Saves to data/results.json.

Football-Data.org team ID for AFC Wimbledon: 57 (League Two era)
Check https://www.football-data.org/v4/teams for current ID if changed.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
TEAM_ID = 347  # AFC Wimbledon
BASE_URL = "https://api.football-data.org/v4"
DATA_PATH = Path(__file__).parent.parent / "data" / "results.json"

def fetch_matches(season: int = 2024) -> list[dict]:
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/teams/{TEAM_ID}/matches?season={season}&status=FINISHED"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("matches", [])

def summarize(match: dict) -> dict:
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    score = match["score"]["fullTime"]
    return {
        "date": match["utcDate"][:10],
        "home": home,
        "away": away,
        "home_score": score["home"],
        "away_score": score["away"],
        "result": "W" if (
            (home == "AFC Wimbledon" and score["home"] > score["away"]) or
            (away == "AFC Wimbledon" and score["away"] > score["home"])
        ) else "D" if score["home"] == score["away"] else "L",
    }

if __name__ == "__main__":
    matches = fetch_matches()
    summaries = [summarize(m) for m in matches]
    DATA_PATH.parent.mkdir(exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"Saved {len(summaries)} matches to {DATA_PATH}")
