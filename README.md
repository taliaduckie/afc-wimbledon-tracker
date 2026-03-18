# AFC Wimbledon & Restaurant Tracker

Two personal data projects in one repo, united by the theme of tracking
things you care about obsessively.

## Projects

### 1. AFC Wimbledon Match Tracker
Fetches results and league table data from the Football-Data.org API
and stores them locally for analysis. Tracks form, goal difference over time,
and home vs away performance.

### 2. Restaurant Difficulty Index
A personal CSV-backed tracker for restaurant booking difficulty, with a
scoring heuristic: how hard is it to actually get a table?

Inspired by the fact that booking difficulty is an underrated restaurant
signal — often more informative than review scores.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add your Football-Data.org API key
python src/fetch_results.py
python src/restaurant_score.py --list
```

## Football-Data.org

Free tier is sufficient. Get a key at https://www.football-data.org/

## Project Structure
```
afc-wimbledon-tracker/
├── src/
│   ├── fetch_results.py      # pull match results from API
│   ├── league_table.py       # format and display table
│   └── restaurant_score.py  # restaurant difficulty tracker
├── data/
│   ├── results.json
│   └── restaurants.csv
└── notebooks/
    └── form_analysis.ipynb
```
