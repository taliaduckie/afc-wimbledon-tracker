"""
squad.py
Track the AFC Wimbledon squad and detect transfer-window moves

No API key needed (TheSportsDB free tier — note it caps the roster at
~10 players). Moves are found by diffing the latest roster against the
last saved snapshot: a player who drops out is an OUT, a new one is an IN
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table

TEAM = "AFC Wimbledon"
TEAM_ID = 134241
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

DATA_DIR = Path(__file__).parent.parent / "data"
SQUAD_PATH = DATA_DIR / "squad.json"
TRANSFERS_PATH = DATA_DIR / "transfers.json"


def parse_player(raw: dict) -> dict:
    """Pull the fields we care about from a TheSportsDB player record"""
    return {
        "id": raw.get("idPlayer", ""),
        "name": raw.get("strPlayer", ""),
        "position": raw.get("strPosition") or "",
        "nationality": raw.get("strNationality") or "",
        "number": raw.get("strNumber") or "",
    }


def fetch_squad() -> list[dict]:
    """Fetch the current roster from TheSportsDB"""
    url = f"{BASE_URL}/lookup_all_players.php?id={TEAM_ID}"
    resp = requests.get(url)
    resp.raise_for_status()
    players = resp.json().get("player") or []
    return [parse_player(p) for p in players]


def diff_squads(old: list[dict], new: list[dict]) -> tuple[list[dict], list[dict]]:
    """Compare snapshots by player id -> (arrivals, departures)"""
    old_ids = {p["id"] for p in old}
    new_ids = {p["id"] for p in new}
    arrivals = [p for p in new if p["id"] not in old_ids]
    departures = [p for p in old if p["id"] not in new_ids]
    return arrivals, departures


def build_moves(arrivals: list[dict], departures: list[dict], date: str) -> list[dict]:
    """Turn arrivals/departures into dated transfer-log events"""
    moves = []
    for p in arrivals:
        moves.append({"date": date, "type": "in", "name": p["name"], "position": p["position"]})
    for p in departures:
        moves.append({"date": date, "type": "out", "name": p["name"], "position": p["position"]})
    return moves


def load_squad() -> list[dict]:
    if not SQUAD_PATH.exists():
        return []
    with open(SQUAD_PATH) as f:
        return json.load(f)


def load_transfers() -> list[dict]:
    if not TRANSFERS_PATH.exists():
        return []
    with open(TRANSFERS_PATH) as f:
        return json.load(f)


def _save(path: Path, data) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fetch_and_record(date: str | None = None) -> tuple[list[dict], list[dict]]:
    """Fetch latest squad, diff vs snapshot, append moves -> (squad, new_moves)"""
    date = date or datetime.now().strftime("%Y-%m-%d")
    new = fetch_squad()
    old = load_squad()
    arrivals, departures = diff_squads(old, new)
    moves = build_moves(arrivals, departures, date)
    if moves:
        log = load_transfers()
        log.extend(moves)
        _save(TRANSFERS_PATH, log)
    _save(SQUAD_PATH, new)
    return new, moves


def display_squad(players: list[dict]):
    console = Console()
    if not players:
        console.print("[dim]No squad data.[/dim]")
        return

    table = Table(title=f"{TEAM} Squad ({len(players)})", title_style="bold cyan")
    table.add_column("No", justify="right")
    table.add_column("Player")
    table.add_column("Position")
    table.add_column("Nationality")

    def _num(p):
        try:
            return int(p["number"])
        except (ValueError, TypeError):
            return 999

    for p in sorted(players, key=lambda p: (_num(p), p["name"])):
        table.add_row(p["number"] or "—", p["name"], p["position"], p["nationality"])
    console.print(table)


def display_transfers(moves: list[dict], title: str = "Transfer Window Moves"):
    console = Console()
    if not moves:
        console.print("[dim]No moves recorded.[/dim]")
        return

    table = Table(title=title, title_style="bold cyan")
    table.add_column("Date")
    table.add_column("Move", justify="center")
    table.add_column("Player")
    table.add_column("Position")

    for m in moves:
        if m["type"] == "in":
            badge = "[green]IN ▲[/green]"
        else:
            badge = "[red]OUT ▼[/red]"
        table.add_row(m["date"], badge, m["name"], m["position"])
    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Fetch latest squad and record any moves")
    parser.add_argument("--transfers", action="store_true", help="Show the transfer movement log")
    args = parser.parse_args()

    if args.transfers:
        display_transfers(load_transfers())
    elif args.fetch:
        squad, moves = fetch_and_record()
        display_squad(squad)
        display_transfers(moves, title="Moves detected this fetch")
    else:
        display_squad(load_squad())
