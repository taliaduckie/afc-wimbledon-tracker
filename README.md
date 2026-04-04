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
python src/fetch_results.py
```

## Usage

### Football

```bash
python src/fetch_results.py              # fetch match results
python src/league_table.py               # season summary (P/W/D/L/GF/GA/GD/Pts)
python src/league_table.py --last 10     # form over last N matches
python src/opponent_stats.py             # record by opponent
python src/opponent_stats.py --top 5     # 5 hardest opponents
python src/opponent_stats.py --big-results  # biggest wins and losses
python src/fixtures.py                   # upcoming fixtures
python src/fixtures.py --next 3          # next N fixtures
```

### Restaurants

```bash
python src/restaurant_score.py --list
python src/restaurant_score.py --add "Chez Panisse" --weeks 6 --walkin no --platform resy --waitlist yes
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
├── src/
│   ├��─ fetch_results.py      # pull match results from CSV
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
