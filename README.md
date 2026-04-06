# AFC Wimbledon & Restaurant Tracker

Two personal data projects in one repo, united by the theme of tracking
things you care about obsessively. GO WOMBLES.

## Projects

### 1. AFC Wimbledon Match Tracker
Fetches League One results from football-data.co.uk and upcoming fixtures
from TheSportsDB. Tracks form, goal difference over time, home vs away
performance, and opponent records. No API key needed.

### 2. Restaurant Difficulty Index
A personal CSV-backed tracker for restaurant booking difficulty, with a
scoring heuristic: how hard is it to actually get a table?

Inspired by the fact that booking difficulty is an underrated restaurant
signal — often more informative than review scores.

## Setup

```bash
pip install -r requirements.txt
python -m src afc fetch
```

## Usage

### Unified CLI

```bash
# Football
python -m src afc fetch                        # fetch current season results
python -m src afc fetch --season 2024 --league E3  # historical (League Two 2024/25)
python -m src afc table                        # season summary
python -m src afc table --last 10              # last N matches
python -m src afc opponents                    # record by opponent
python -m src afc opponents --top 5            # hardest opponents
python -m src afc opponents --big-results      # biggest wins and losses
python -m src afc fixtures                     # upcoming fixtures
python -m src afc fixtures --next 3            # next N fixtures

# Restaurants
python -m src restaurant list
python -m src restaurant add "Chez Panisse" --weeks 6 --walkin no --platform resy --waitlist yes
python -m src restaurant update "Chez Panisse" --weeks 4
python -m src restaurant remove "Chez Panisse"
```

### Streamlit Dashboard

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
│   ├── fixtures.py           # upcoming fixtures from TheSportsDB
│   └── restaurant_score.py   # restaurant difficulty tracker
├── data/
│   ├── results.json          # fetched match results
│   └── restaurants.csv       # restaurant tracker data
├── notebooks/
│   └── form_analysis.ipynb   # form, GD, and home/away charts
└── tests/
    ├── test_summarize.py
    ├── test_opponent_stats.py
    └── test_restaurant_score.py
```
