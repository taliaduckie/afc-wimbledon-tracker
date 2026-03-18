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

def list_restaurants():
    rows = load()
    if not rows:
        print("No restaurants tracked yet.")
        return
    rows_sorted = sorted(rows, key=lambda r: float(r["difficulty_score"]), reverse=True)
    print(f"{'Name':<30} {'Difficulty':>10} {'Weeks':>6} {'Walk-in':>8}")
    print("-" * 60)
    for r in rows_sorted:
        print(f"{r['name']:<30} {r['difficulty_score']:>10} {r['weeks_out']:>6} {r['walkin']:>8}")

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
