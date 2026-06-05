"""
Unified CLI for AFC Wimbledon Tracker.

Usage:
    python -m src fetch
    python -m src fetch --season 2024 --league E3
    python -m src table
    python -m src table --last 10
    python -m src opponents
    python -m src opponents --top 5
    python -m src opponents --big-results
    python -m src fixtures
    python -m src fixtures --next 3
    python -m src standings
    python -m src standings --top 6
"""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wombles",
        description="AFC Wimbledon Match Tracker. GO WOMBLES.",
    )
    sub = parser.add_subparsers(dest="action")

    fetch = sub.add_parser("fetch", help="Fetch match results")
    fetch.add_argument("--season", type=int, default=2025, help="Season start year (default: 2025)")
    fetch.add_argument("--league", default="E2", help="League code: E0/E1/E2/E3 (default: E2)")

    table = sub.add_parser("table", help="Season summary table")
    table.add_argument("--last", type=int, default=0, help="Show stats for last N matches only")

    opponents = sub.add_parser("opponents", help="Record by opponent")
    opponents.add_argument("--top", type=int, help="Show only the N hardest opponents")
    opponents.add_argument("--big-results", action="store_true", help="Biggest wins and losses")

    fixtures = sub.add_parser("fixtures", help="Upcoming fixtures")
    fixtures.add_argument("--next", type=int, dest="limit", help="Show only the next N fixtures")

    standings = sub.add_parser("standings", help="Full league table")
    standings.add_argument("--top", type=int, help="Show only the top N teams")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    if args.action == "fetch":
        from src.fetch_results import fetch_season_csv, summarize, build_standings, DATA_DIR, DATA_PATH, STANDINGS_PATH
        import json
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

    elif args.action == "table":
        from src.league_table import load_results, build_table, display, form_string
        results = load_results()
        if not results:
            print("No results found. Run 'python -m src fetch' first.")
            sys.exit(1)
        subset = results[-args.last:] if args.last else results
        title = f"AFC Wimbledon — Last {args.last} Matches" if args.last else "AFC Wimbledon — Season Summary"
        stats = build_table(subset)
        display(stats, title=title)
        print(f"\nForm (last 5): {form_string(results)}")

    elif args.action == "opponents":
        from src.opponent_stats import load_results, build_opponent_records, display_records, display_big_results
        results = load_results()
        if not results:
            print("No results found. Run 'python -m src fetch' first.")
            sys.exit(1)
        if args.big_results:
            display_big_results(results)
        else:
            records = build_opponent_records(results)
            display_records(records, top_n=args.top)

    elif args.action == "fixtures":
        from src.fixtures import fetch_upcoming, display
        matches = fetch_upcoming(limit=args.limit)
        display(matches)

    elif args.action == "standings":
        from src.standings import load_standings, display
        display(load_standings(), top=args.top)


if __name__ == "__main__":
    main()
