"""
Unified CLI for AFC Wimbledon & Restaurant Tracker.

Usage:
    python -m src afc fetch
    python -m src afc fetch --season 2024 --league E3
    python -m src afc table
    python -m src afc table --last 10
    python -m src afc opponents
    python -m src afc opponents --top 5
    python -m src afc opponents --big-results
    python -m src afc fixtures
    python -m src afc fixtures --next 3

    python -m src restaurant list
    python -m src restaurant add "Chez Panisse" --weeks 6 --walkin no
    python -m src restaurant update "Chez Panisse" --weeks 4
    python -m src restaurant remove "Chez Panisse"
"""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wombles",
        description="AFC Wimbledon & Restaurant Tracker. GO WOMBLES.",
    )
    sub = parser.add_subparsers(dest="command")

    # --- afc ---
    afc = sub.add_parser("afc", help="AFC Wimbledon match tracker")
    afc_sub = afc.add_subparsers(dest="action")

    fetch = afc_sub.add_parser("fetch", help="Fetch match results")
    fetch.add_argument("--season", type=int, default=2025, help="Season start year (default: 2025)")
    fetch.add_argument("--league", default="E2", help="League code: E0/E1/E2/E3 (default: E2)")

    table = afc_sub.add_parser("table", help="Season summary table")
    table.add_argument("--last", type=int, default=0, help="Show stats for last N matches only")

    opponents = afc_sub.add_parser("opponents", help="Record by opponent")
    opponents.add_argument("--top", type=int, help="Show only the N hardest opponents")
    opponents.add_argument("--big-results", action="store_true", help="Biggest wins and losses")

    fixtures = afc_sub.add_parser("fixtures", help="Upcoming fixtures")
    fixtures.add_argument("--next", type=int, dest="limit", help="Show only the next N fixtures")

    # --- restaurant ---
    rest = sub.add_parser("restaurant", help="Restaurant difficulty tracker")
    rest_sub = rest.add_subparsers(dest="action")

    rest_sub.add_parser("list", help="List all restaurants")

    add = rest_sub.add_parser("add", help="Add a restaurant")
    add.add_argument("name")
    add.add_argument("--weeks", type=int, default=2)
    add.add_argument("--walkin", choices=["yes", "no"], default="no")
    add.add_argument("--platform", default="opentable")
    add.add_argument("--waitlist", choices=["yes", "no"], default="no")
    add.add_argument("--notes", default="")

    update = rest_sub.add_parser("update", help="Update a restaurant")
    update.add_argument("name")
    update.add_argument("--weeks", type=int)
    update.add_argument("--walkin", choices=["yes", "no"])
    update.add_argument("--platform")
    update.add_argument("--waitlist", choices=["yes", "no"])
    update.add_argument("--notes")

    remove = rest_sub.add_parser("remove", help="Remove a restaurant")
    remove.add_argument("name")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "afc":
        if not args.action:
            parser.parse_args(["afc", "-h"])
            return

        if args.action == "fetch":
            from src.fetch_results import fetch_matches, DATA_PATH
            import json
            matches = fetch_matches(args.season, args.league)
            matches.sort(key=lambda m: m["date"])
            DATA_PATH.parent.mkdir(exist_ok=True)
            with open(DATA_PATH, "w") as f:
                json.dump(matches, f, indent=2)
            print(f"Saved {len(matches)} matches to {DATA_PATH}")

        elif args.action == "table":
            from src.league_table import load_results, build_table, display, form_string
            results = load_results()
            if not results:
                print("No results found. Run 'python -m src afc fetch' first.")
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
                print("No results found. Run 'python -m src afc fetch' first.")
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

    elif args.command == "restaurant":
        if not args.action:
            parser.parse_args(["restaurant", "-h"])
            return

        if args.action == "list":
            from src.restaurant_score import list_restaurants
            list_restaurants()

        elif args.action == "add":
            from src.restaurant_score import load, save, score
            rows = load()
            d = score(args.weeks, args.walkin, args.platform, args.waitlist)
            rows.append({
                "name": args.name,
                "weeks_out": args.weeks,
                "walkin": args.walkin,
                "platform": args.platform,
                "waitlist": args.waitlist,
                "difficulty_score": d,
                "notes": args.notes,
            })
            save(rows)
            print(f"Added '{args.name}' with difficulty score {d}/10")

        elif args.action == "update":
            from src.restaurant_score import update_restaurant
            kwargs = {k: v for k, v in {
                "weeks_out": args.weeks,
                "walkin": args.walkin,
                "platform": args.platform,
                "waitlist": args.waitlist,
                "notes": args.notes,
            }.items() if v is not None}
            if not kwargs:
                print("Provide at least one field to update.")
            else:
                update_restaurant(args.name, **kwargs)

        elif args.action == "remove":
            from src.restaurant_score import remove_restaurant
            remove_restaurant(args.name)


if __name__ == "__main__":
    main()
