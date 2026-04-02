"""
restaurant_score.py
Personal restaurant difficulty index.

Difficulty is scored 1-10 based on:
- Weeks in advance needed to book
- Whether walk-ins are possible
- Whether OpenTable/Resy is required vs. phone
- Whether they have a waitlist

Usage:
    python restaurant_score.py --list
    python restaurant_score.py --add "Chez Panisse" --weeks 6 --walkin no --platform resy
"""

import argparse
import csv
import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

CSV_PATH = Path(__file__).parent.parent / "data" / "restaurants.csv"
FIELDS = ["name", "weeks_out", "walkin", "platform", "waitlist", "difficulty_score", "notes"]

def load() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))

def save(rows: list[dict]):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def score(weeks_out: int, walkin: str, platform: str, waitlist: str) -> int:
    s = 0
    s += min(weeks_out * 1.2, 5)       # up to 5 points for lead time
    s += 0 if walkin == "yes" else 2   # walk-ins reduce difficulty
    s += 1 if platform == "resy" else 0
    s += 1.5 if waitlist == "yes" else 0
    return round(min(s, 10), 1)

def difficulty_color(score: float) -> str:
    if score >= 7:
        return "red"
    if score >= 4:
        return "yellow"
    return "green"


def list_restaurants():
    rows = load()
    if not rows:
        print("No restaurants tracked yet.")
        return
    rows_sorted = sorted(rows, key=lambda r: float(r["difficulty_score"]), reverse=True)

    console = Console()
    table = Table(title="Restaurant Difficulty Index")
    table.add_column("Name", style="bold")
    table.add_column("Difficulty", justify="right")
    table.add_column("Weeks Out", justify="right")
    table.add_column("Walk-in", justify="center")
    table.add_column("Platform", justify="center")
    table.add_column("Notes", max_width=40)

    for r in rows_sorted:
        score = float(r["difficulty_score"])
        color = difficulty_color(score)
        table.add_row(
            r["name"],
            f"[{color}]{score}/10[/{color}]",
            r["weeks_out"],
            r["walkin"],
            r.get("platform", ""),
            r.get("notes", ""),
        )

    console.print(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--add", metavar="NAME")
    parser.add_argument("--weeks", type=int, default=2)
    parser.add_argument("--walkin", choices=["yes", "no"], default="no")
    parser.add_argument("--platform", default="opentable")
    parser.add_argument("--waitlist", choices=["yes", "no"], default="no")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.list:
        list_restaurants()
    elif args.add:
        rows = load()
        d = score(args.weeks, args.walkin, args.platform, args.waitlist)
        rows.append({
            "name": args.add,
            "weeks_out": args.weeks,
            "walkin": args.walkin,
            "platform": args.platform,
            "waitlist": args.waitlist,
            "difficulty_score": d,
            "notes": args.notes,
        })
        save(rows)
        print(f"Added '{args.add}' with difficulty score {d}/10")
