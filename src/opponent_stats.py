"""
opponent_stats.py
Analyse AFC Wimbledon's record broken down by opponent.

Usage:
    python src/opponent_stats.py
    python src/opponent_stats.py --top 5        # worst 5 opponents by points-per-game
    python src/opponent_stats.py --big-results   # biggest wins and losses
"""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_PATH = Path(__file__).parent.parent / "data" / "results.json"
TEAM = "AFC Wimbledon"


def load_results() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH) as f:
        return json.load(f)


def opponent_name(match: dict) -> str:
    return match["away"] if match["home"] == TEAM else match["home"]


def goal_diff(match: dict) -> int:
    if match["home"] == TEAM:
        return match["home_score"] - match["away_score"]
    return match["away_score"] - match["home_score"]


def build_opponent_records(results: list[dict]) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for m in results:
        opp = opponent_name(m)
        if opp not in records:
            records[opp] = {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0}
        r = records[opp]
        r["P"] += 1
        r[m["result"]] += 1
        if m["home"] == TEAM:
            r["GF"] += m["home_score"]
            r["GA"] += m["away_score"]
        else:
            r["GF"] += m["away_score"]
            r["GA"] += m["home_score"]
    return records


def display_records(records: dict[str, dict], top_n: int | None = None):
    console = Console()

    rows = []
    for opp, r in records.items():
        ppg = (r["W"] * 3 + r["D"]) / r["P"] if r["P"] else 0
        gd = r["GF"] - r["GA"]
        rows.append((opp, r["P"], r["W"], r["D"], r["L"], r["GF"], r["GA"], gd, ppg))

    rows.sort(key=lambda x: x[-1])  # sort by PPG ascending (hardest opponents first)

    if top_n:
        rows = rows[:top_n]

    table = Table(title="Record by Opponent (hardest first)")
    for col in ["Opponent", "P", "W", "D", "L", "GF", "GA", "GD", "PPG"]:
        justify = "left" if col == "Opponent" else "right"
        table.add_column(col, justify=justify)

    for opp, p, w, d, l, gf, ga, gd, ppg in rows:
        gd_str = f"[green]+{gd}[/green]" if gd > 0 else f"[red]{gd}[/red]" if gd < 0 else "0"
        table.add_row(opp, str(p), str(w), str(d), str(l), str(gf), str(ga), gd_str, f"{ppg:.1f}")

    console.print(table)


def display_big_results(results: list[dict], n: int = 5):
    console = Console()
    scored = [(m, goal_diff(m)) for m in results]

    # Biggest wins
    wins = sorted(scored, key=lambda x: x[1], reverse=True)[:n]
    table = Table(title=f"Top {n} Biggest Wins")
    table.add_column("Date")
    table.add_column("Match")
    table.add_column("Score", justify="center")
    table.add_column("GD", justify="right")
    for m, gd in wins:
        if gd <= 0:
            break
        table.add_row(m["date"], f"{m['home']} vs {m['away']}", f"{m['home_score']}-{m['away_score']}", f"[green]+{gd}[/green]")
    console.print(table)

    console.print()

    # Biggest losses
    losses = sorted(scored, key=lambda x: x[1])[:n]
    table = Table(title=f"Top {n} Biggest Losses")
    table.add_column("Date")
    table.add_column("Match")
    table.add_column("Score", justify="center")
    table.add_column("GD", justify="right")
    for m, gd in losses:
        if gd >= 0:
            break
        table.add_row(m["date"], f"{m['home']} vs {m['away']}", f"{m['home_score']}-{m['away_score']}", f"[red]{gd}[/red]")
    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, help="Show only the N hardest opponents")
    parser.add_argument("--big-results", action="store_true", help="Show biggest wins and losses")
    args = parser.parse_args()

    results = load_results()
    if not results:
        print("No results found. Run fetch_results.py first.")
        raise SystemExit(1)

    if args.big_results:
        display_big_results(results)
    else:
        records = build_opponent_records(results)
        display_records(records, top_n=args.top)
