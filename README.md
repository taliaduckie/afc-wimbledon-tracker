# AFC Wimbledon Tracker

Track AFC Wimbledon's season — results, form, opponents, and upcoming
fixtures. No API key needed. GO WOMBLES.

## Setup

```bash
pip install -r requirements.txt
python -m src fetch
```

## Usage

### CLI

```bash
python -m src fetch                            # fetch current season results
python -m src fetch --season 2024 --league E3  # historical (League Two 2024/25)
python -m src table                            # season summary
python -m src table --last 10                  # last N matches
python -m src table --season 2024 --league E3  # view another season live
python -m src opponents                        # record by opponent
python -m src opponents --top 5                # hardest opponents
python -m src opponents --big-results          # biggest wins and losses
python -m src fixtures                         # upcoming fixtures
python -m src fixtures --next 3                # next N fixtures
python -m src standings                        # full league table
python -m src standings --top 6                # top N teams
python -m src players                          # current squad
python -m src players --fetch                  # refresh squad, record any moves
python -m src players --transfers              # transfer window movement log
```

The `table`, `standings`, and `opponents` commands read the cached season by
default; pass `--season`/`--league` to pull a different one live. `table` and
`standings` print a one-line takeaway (e.g. "Finished 19th in League One — 53
pts — safe"). Off-season, headers read "League One 2025/26 — Final".

### Dashboard

```bash
streamlit run app.py
```

### Tests

```bash
pytest tests/
```

## Data Sources

- **Match results**: [football-data.co.uk](https://www.football-data.co.uk/) — free CSV downloads, no key required
- **Upcoming fixtures**: [TheSportsDB](https://www.thesportsdb.com/) — free JSON API, no key required
- **Squad & transfers**: [TheSportsDB](https://www.thesportsdb.com/) roster — moves are detected by diffing each squad fetch against the last snapshot (free tier caps the roster at ~10 players)

## Project Structure
```
afc-wimbledon-tracker/
├── app.py                    # Streamlit dashboard
├── src/
│   ├── __main__.py           # unified CLI entrypoint
│   ├── fetch_results.py      # pull match results from CSV
│   ├── league_table.py       # season summary with rich tables
│   ├── opponent_stats.py     # per-opponent record and big results
│   ├── fixtures.py           # upcoming fixtures from TheSportsDB
│   ├── standings.py          # full league table with zones
│   ├── season.py             # season/league metadata + takeaway
│   └── squad.py              # squad snapshot and transfer-move tracking
├── data/
│   ├── results.json          # fetched match results
│   ├── standings.json        # full league table
│   ├── meta.json             # season/league + complete flag
│   ├── squad.json            # latest squad snapshot
│   └── transfers.json        # detected transfer-window moves
├── notebooks/
│   └── form_analysis.ipynb   # form, GD, and home/away charts
└── tests/
    ├── test_summarize.py
    └── test_opponent_stats.py
```
