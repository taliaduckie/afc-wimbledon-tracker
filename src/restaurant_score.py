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

def remove_restaurant(name: str):
    rows = load()
    matching = [r for r in rows if r["name"].lower() == name.lower()]
    if not matching:
        print(f"No restaurant found matching '{name}'.")
        return
    rows = [r for r in rows if r["name"].lower() != name.lower()]
    save(rows)
    print(f"Removed '{matching[0]['name']}'.")


def update_restaurant(name: str, **kwargs):
    rows = load()
    found = False
    for r in rows:
        if r["name"].lower() == name.lower():
            found = True
            if "weeks_out" in kwargs:
                r["weeks_out"] = kwargs["weeks_out"]
            if "walkin" in kwargs:
                r["walkin"] = kwargs["walkin"]
            if "platform" in kwargs:
                r["platform"] = kwargs["platform"]
            if "waitlist" in kwargs:
                r["waitlist"] = kwargs["waitlist"]
            if "notes" in kwargs:
                r["notes"] = kwargs["notes"]
            r["difficulty_score"] = score(
                int(r["weeks_out"]), r["walkin"], r["platform"], r["waitlist"]
            )
            print(f"Updated '{r['name']}' — new difficulty score {r['difficulty_score']}/10")
            break
    if not found:
        print(f"No restaurant found matching '{name}'.")
        return
    save(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--add", metavar="NAME")
    parser.add_argument("--remove", metavar="NAME")
    parser.add_argument("--update", metavar="NAME")
    parser.add_argument("--weeks", type=int, default=None)
    parser.add_argument("--walkin", choices=["yes", "no"], default=None)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--waitlist", choices=["yes", "no"], default=None)
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    if args.list:
        list_restaurants()
    elif args.remove:
        remove_restaurant(args.remove)
    elif args.update:
        kwargs = {k: v for k, v in {
            "weeks_out": args.weeks,
            "walkin": args.walkin,
            "platform": args.platform,
            "waitlist": args.waitlist,
            "notes": args.notes,
        }.items() if v is not None}
        if not kwargs:
            print("Provide at least one field to update (--weeks, --walkin, --platform, --waitlist, --notes).")
        else:
            update_restaurant(args.update, **kwargs)
    elif args.add:
        rows = load()
        d = score(args.weeks or 2, args.walkin or "no", args.platform or "opentable", args.waitlist or "no")
        rows.append({
            "name": args.add,
            "weeks_out": args.weeks or 2,
            "walkin": args.walkin or "no",
            "platform": args.platform or "opentable",
            "waitlist": args.waitlist or "no",
            "difficulty_score": d,
            "notes": args.notes or "",
        })
        save(rows)
        print(f"Added '{args.add}' with difficulty score {d}/10")
