"""
league_table.py
Build and display a simple league table from saved match results.

Usage:
    python src/league_table.py
    python src/league_table.py --last 10   # form table over last N matches
"""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_PATH = Path(__file__).parent.parent / "data" / "results.json"


def load_results() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH) as f:
        return json.load(f)


def build_table(results: list[dict]) -> dict:
    """Aggregate AFC Wimbledon's record from saved match results."""
    stats = {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0}
    for m in results:
        stats["P"] += 1
        if m["result"] == "W":
            stats["W"] += 1
        elif m["result"] == "D":
            stats["D"] += 1
        else:
            stats["L"] += 1

        if m["home"] == "AFC Wimbledon":
            stats["GF"] += m["home_score"]
            stats["GA"] += m["away_score"]
        else:
            stats["GF"] += m["away_score"]
            stats["GA"] += m["home_score"]

    stats["GD"] = stats["GF"] - stats["GA"]
    stats["Pts"] = stats["W"] * 3 + stats["D"]
    return stats


def display(stats: dict, title: str = "AFC Wimbledon — Season Summary"):
    console = Console()
    table = Table(title=title)

    for col in ["P", "W", "D", "L", "GF", "GA", "GD", "Pts"]:
        table.add_column(col, justify="right")

    table.add_row(*[str(stats[c]) for c in ["P", "W", "D", "L", "GF", "GA", "GD", "Pts"]])
    console.print(table)


def form_string(results: list[dict], last_n: int = 5) -> str:
    """Return a compact form string like WWDLW for the last N matches."""
    return "".join(m["result"] for m in results[-last_n:])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--last", type=int, default=0, help="Show stats for last N matches only")
    args = parser.parse_args()

    results = load_results()
    if not results:
        print("No results found. Run fetch_results.py first.")
        raise SystemExit(1)

    subset = results[-args.last:] if args.last else results
    title = f"AFC Wimbledon — Last {args.last} Matches" if args.last else "AFC Wimbledon — Season Summary"

    stats = build_table(subset)
    display(stats, title=title)

    form = form_string(results)
    print(f"\nForm (last 5): {form}")
