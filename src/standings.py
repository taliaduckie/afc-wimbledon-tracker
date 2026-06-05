"""
standings.py
Render the full league table from data/standings.json.

Usage:
    python -m src standings
    python -m src standings --top 6
"""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.text import Text

from src.season import AUTO_PROMOTION, PLAYOFFS, RELEGATION_START

STANDINGS_PATH = Path(__file__).parent.parent / "data" / "standings.json"
TEAM = "AFC Wimbledon"

FORM_COLORS = {"W": "green", "D": "yellow", "L": "red"}


def load_standings() -> list[dict]:
    if not STANDINGS_PATH.exists():
        return []
    with open(STANDINGS_PATH) as f:
        return json.load(f)


def _form_text(form: str) -> Text:
    t = Text()
    for ch in form:
        t.append(ch, style=f"bold {FORM_COLORS.get(ch, 'white')}")
    return t


def _pos_text(pos: int) -> Text:
    if AUTO_PROMOTION[0] <= pos <= AUTO_PROMOTION[1]:
        return Text(str(pos), style="bold green")
    if PLAYOFFS[0] <= pos <= PLAYOFFS[1]:
        return Text(str(pos), style="green")
    if pos >= RELEGATION_START:
        return Text(str(pos), style="bold red")
    return Text(str(pos))


def display(standings: list[dict], top: int | None = None):
    console = Console()
    if not standings:
        console.print("[dim]No standings found. Run 'python -m src fetch' first.[/dim]")
        return

    rows = standings[:top] if top else standings

    table = Table(title="League One — Standings", title_style="bold cyan", expand=False)
    table.add_column("#", justify="right")
    table.add_column("Team")
    for col in ["P", "W", "D", "L", "GF", "GA", "GD", "Pts"]:
        table.add_column(col, justify="right")
    table.add_column("Form", justify="left")

    for row in rows:
        is_wimbledon = TEAM in row["team"]
        team_style = "bold blue on yellow" if is_wimbledon else ""

        gd = row["GD"]
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        gd_color = "green" if gd > 0 else ("red" if gd < 0 else "white")

        table.add_row(
            _pos_text(row["Pos"]),
            Text(row["team"], style=team_style),
            str(row["P"]),
            str(row["W"]),
            str(row["D"]),
            str(row["L"]),
            str(row["GF"]),
            str(row["GA"]),
            Text(gd_str, style=gd_color),
            Text(str(row["Pts"]), style="bold"),
            _form_text(row.get("Form", "")),
        )

    console.print(table)

    legend = Text()
    legend.append("  ")
    legend.append("auto promotion", style="bold green")
    legend.append("  •  ")
    legend.append("playoffs", style="green")
    legend.append("  •  ")
    legend.append("relegation", style="bold red")
    console.print(legend)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, help="Show only the top N teams")
    args = parser.parse_args()

    display(load_standings(), top=args.top)
