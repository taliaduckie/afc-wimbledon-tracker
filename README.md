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
python -m src opponents                        # record by opponent
python -m src opponents --top 5                # hardest opponents
python -m src opponents --big-results          # biggest wins and losses
python -m src fixtures                         # upcoming fixtures
python -m src fixtures --next 3                # next N fixtures
python -m src standings                        # full league table
python -m src standings --top 6                # top N teams
```

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

## Project Structure
```
afc-wimbledon-tracker/
├── app.py                    # Streamlit dashboard
├── src/
│   ├── __main__.py           # unified CLI entrypoint
│   ├── fetch_results.py      # pull match results from CSV
│   ├── league_table.py       # season summary with rich tables
│   ├── opponent_stats.py     # per-opponent record and big results
│   └── fixtures.py           # upcoming fixtures from TheSportsDB
├── data/
│   └── results.json          # fetched match results
├── notebooks/
│   └── form_analysis.ipynb   # form, GD, and home/away charts
└── tests/
    ├── test_summarize.py
    └── test_opponent_stats.py
```
