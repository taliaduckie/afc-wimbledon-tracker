"""
Streamlit dashboard for AFC Wimbledon Tracker.

Run with: streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.season import (
    AUTO_PROMOTION,
    PLAYOFFS,
    RELEGATION_START,
    load_meta,
    status_label,
    takeaway,
)

DATA_DIR = Path(__file__).parent / "data"
RESULTS_PATH = DATA_DIR / "results.json"
STANDINGS_PATH = DATA_DIR / "standings.json"
BADGES_PATH = DATA_DIR / "badges.json"
SQUAD_PATH = DATA_DIR / "squad.json"
TRANSFERS_PATH = DATA_DIR / "transfers.json"
TEAM = "AFC Wimbledon"

st.set_page_config(page_title="Wombles Tracker", page_icon="\u26bd", layout="wide")

# AFC Wimbledon colors
BLUE = "#003DA5"
YELLOW = "#FFD700"

# Load badges
badges = {}
if BADGES_PATH.exists():
    with open(BADGES_PATH) as f:
        badges = json.load(f)


def badge_img(team: str, size: int = 30) -> str:
    url = badges.get(team, "")
    if url:
        return f'<img src="{url}" width="{size}" height="{size}" style="vertical-align: middle; margin-right: 8px;">'
    return ""


def result_color(result: str) -> str:
    return {"W": "#28a745", "D": "#ffc107", "L": "#dc3545"}.get(result, "#666")


def result_label(result: str) -> str:
    return {"W": "WIN", "D": "DRAW", "L": "LOSS"}.get(result, result)


st.markdown(f"""
<style>
    .stApp {{
        background-color: #f5f7fa;
    }}
    header[data-testid="stHeader"] {{
        background-color: {BLUE};
    }}
    h1 {{
        color: {BLUE} !important;
    }}
    h2 {{
        color: {BLUE} !important;
        border-bottom: 3px solid {YELLOW};
        padding-bottom: 0.3em;
    }}
    h3 {{
        color: {BLUE} !important;
    }}
    .stMetric label {{
        color: {BLUE} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {BLUE} !important;
    }}
    .match-card {{
        background: white;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 5px solid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    .match-card .date {{
        color: #888;
        font-size: 0.8em;
    }}
    .match-card .score {{
        font-size: 1.3em;
        font-weight: bold;
        color: {BLUE};
    }}
    .match-card .teams {{
        font-size: 1em;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .match-card .result-badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        font-size: 0.75em;
    }}
    .opp-card {{
        background: white;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 5px solid {BLUE};
    }}
    .opp-card .opp-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }}
    .opp-card .opp-name {{
        font-size: 1.1em;
        font-weight: bold;
        color: {BLUE};
    }}
    .opp-card .opp-stats {{
        color: #555;
        font-size: 0.9em;
    }}
    .opp-card .opp-matches {{
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #eee;
    }}
</style>
""", unsafe_allow_html=True)

st.title("\u26bd AFC Wimbledon Tracker")

# Position tag
standings = []
wimbledon_pos = None
if STANDINGS_PATH.exists():
    with open(STANDINGS_PATH) as f:
        standings = json.load(f)
    for row in standings:
        if TEAM in row.get("team", ""):
            wimbledon_pos = row
            break

meta = load_meta()
status = status_label(meta)

if status:
    final = meta and meta.get("complete")
    chip_bg = "#888" if final else "#28a745"
    st.markdown(
        f'<div style="display:inline-block; background:{chip_bg}; color:white; '
        f'padding:4px 12px; border-radius:14px; font-weight:bold; font-size:0.85em; margin-bottom:8px;">'
        f'{status}</div>',
        unsafe_allow_html=True,
    )

if wimbledon_pos:
    pos = wimbledon_pos["Pos"]
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(pos if pos < 20 else pos % 10, "th")
    league = (meta or {}).get("league_name", "League One")
    st.markdown(
        f'<div style="display:inline-block; background:{BLUE}; color:{YELLOW}; '
        f'padding:6px 16px; border-radius:20px; font-weight:bold; font-size:1.1em; margin-bottom:10px;">'
        f'{pos}{suffix} in {league} &bull; {wimbledon_pos["Pts"]} pts &bull; '
        f'GD {wimbledon_pos["GD"]:+d}'
        f'</div>',
        unsafe_allow_html=True,
    )

line = takeaway(standings, meta)
if line:
    st.markdown(f"**{line}**")

st.caption("GO WOMBLES")

if not RESULTS_PATH.exists():
    st.warning("No results found. Run `python -m src fetch` first.")
    st.stop()

with open(RESULTS_PATH) as f:
    results = json.load(f)

df = pd.DataFrame(results)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Compute columns used everywhere
df["gf"] = df.apply(lambda r: r["home_score"] if r["home"] == TEAM else r["away_score"], axis=1)
df["ga"] = df.apply(lambda r: r["away_score"] if r["home"] == TEAM else r["home_score"], axis=1)
df["gd"] = df["gf"] - df["ga"]
df["points"] = df["result"].map({"W": 3, "D": 1, "L": 0})
df["cum_pts"] = df["points"].cumsum()
df["cum_gd"] = df["gd"].cumsum()
df["rolling_ppg"] = df["points"].rolling(5, min_periods=1).mean() * 3
df["venue"] = df["home"].apply(lambda h: "Home" if h == TEAM else "Away")
df["opponent"] = df.apply(lambda r: r["away"] if r["home"] == TEAM else r["home"], axis=1)

wins = (df["result"] == "W").sum()
draws = (df["result"] == "D").sum()
losses = (df["result"] == "L").sum()
gf = df["gf"].sum()
ga = df["ga"].sum()

# --- Two-column layout: left (2/3) content, right (1/3) charts ---
left, right = st.columns([2, 1])

# =============================================================================
# LEFT COLUMN — summary, opponents, results
# =============================================================================
with left:
    st.header("Season Summary")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Played", len(df))
    c2.metric("W / D / L", f"{wins} / {draws} / {losses}")
    c3.metric("Points", wins * 3 + draws)
    c4.metric("GF", gf)
    c5.metric("GA", ga)
    c6.metric("GD", f"{'+' if gf - ga > 0 else ''}{gf - ga}")

    form = "".join(df["result"].tail(5).tolist())
    st.markdown(f"**Form (last 5):** `{form}`")

    # --- W/D/L bar chart ---
    fig, ax = plt.subplots(figsize=(6, 2.5))
    bars = ax.bar(
        ["Wins", "Draws", "Losses"],
        [wins, draws, losses],
        color=["#28a745", "#ffc107", "#dc3545"],
    )
    ax.bar_label(bars, fontweight="bold")
    ax.set_ylim(0, max(wins, draws, losses) * 1.2)
    ax.set_ylabel("Matches")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    plt.tight_layout()
    st.pyplot(fig)

    # --- Home vs Away ---
    st.header("Home vs Away")
    col1, col2 = st.columns(2)
    for venue, col in [("Home", col1), ("Away", col2)]:
        sub = df[df["venue"] == venue]
        w = (sub["result"] == "W").sum()
        d = (sub["result"] == "D").sum()
        l = (sub["result"] == "L").sum()
        col.subheader(venue)
        col.write(f"**{len(sub)}** played: {w}W {d}D {l}L ({w*3+d} pts)")

    # --- League Standings ---
    if standings:
        st.header("League Standings")
        st_df = pd.DataFrame(standings)
        st_df["Form"] = st_df.get("Form", "")
        st_df = st_df[["Pos", "team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts", "Form"]]
        st_df.columns = ["#", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts", "Form"]

        # League One zones (matches src/standings.py)
        AUTO_PROMOTION = (1, 2)
        PLAYOFFS = (3, 6)
        RELEGATION_START = 21

        def zone_style(pos):
            if AUTO_PROMOTION[0] <= pos <= AUTO_PROMOTION[1]:
                return "background-color: #d4f7d4"  # auto promotion
            if PLAYOFFS[0] <= pos <= PLAYOFFS[1]:
                return "background-color: #eafbea"  # playoffs
            if pos >= RELEGATION_START:
                return "background-color: #fdd"  # relegation
            return ""

        def highlight_rows(row):
            if TEAM in row["Team"]:
                return [f"background-color: {BLUE}; color: {YELLOW}; font-weight: bold"] * len(row)
            return [zone_style(row["#"])] * len(row)

        styled = st_df.style.apply(highlight_rows, axis=1).format({"GD": "{:+d}"})
        st.dataframe(styled, use_container_width=True, hide_index=True, height=min(len(standings) * 35 + 40, 900))
        st.caption(
            ":green[**auto promotion** (1–2)] &nbsp;•&nbsp; :green[playoffs (3–6)] "
            "&nbsp;•&nbsp; :red[relegation (21–24)]"
        )

    # --- Opponent records ---
    st.header("Record by Opponent")

    opp_list = sorted(df["opponent"].unique())
    selected_opp = st.selectbox(
        "Select opponent",
        ["All opponents"] + opp_list,
        key="opp_select",
    )

    # Build opponent records
    opponents = {}
    for _, m in df.iterrows():
        opp = m["opponent"]
        if opp not in opponents:
            opponents[opp] = {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "matches": []}
        r = opponents[opp]
        r["P"] += 1
        r[m["result"]] += 1
        r["GF"] += m["gf"]
        r["GA"] += m["ga"]
        r["matches"].append(m)

    display_opps = opp_list if selected_opp == "All opponents" else [selected_opp]

    # Sort by PPG ascending (hardest first)
    def ppg(opp):
        r = opponents[opp]
        return (r["W"] * 3 + r["D"]) / r["P"] if r["P"] else 0

    display_opps = sorted(display_opps, key=ppg)

    for opp in display_opps:
        r = opponents[opp]
        gd = r["GF"] - r["GA"]
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        pts = r["W"] * 3 + r["D"]

        with st.expander(f"{opp}  —  {r['P']}P  {r['W']}W {r['D']}D {r['L']}L  |  GD: {gd_str}  |  {pts} pts"):
            # Opponent header with badge
            st.markdown(
                f'<div class="opp-card">'
                f'<div class="opp-header">{badge_img(opp, 40)}'
                f'<span class="opp-name">{opp}</span></div>'
                f'<div class="opp-stats">'
                f'{r["P"]} played &bull; {r["W"]}W {r["D"]}D {r["L"]}L &bull; '
                f'GF {r["GF"]} GA {r["GA"]} GD {gd_str} &bull; {pts} pts'
                f'</div>'
                f'<div class="opp-matches">',
                unsafe_allow_html=True,
            )

            # Show each match against this opponent
            for m in reversed(r["matches"]):
                date_str = m["date"].strftime("%d %b %Y")
                venue = "H" if m["home"] == TEAM else "A"
                res = m["result"]
                color = result_color(res)
                home_badge = badge_img(m["home"], 20)
                away_badge = badge_img(m["away"], 20)

                st.markdown(
                    f'<div class="match-card" style="border-left-color: {color};">'
                    f'<div class="date">{date_str} &bull; {venue}</div>'
                    f'<div class="teams">'
                    f'{home_badge}<strong>{m["home"]}</strong>'
                    f'<span class="score">{m["home_score"]} - {m["away_score"]}</span>'
                    f'<strong>{m["away"]}</strong>{away_badge}'
                    f'<span class="result-badge" style="background:{color};">{result_label(res)}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            st.markdown('</div></div>', unsafe_allow_html=True)

    # --- All Results ---
    st.header("All Results")

    for _, m in df.iloc[::-1].iterrows():
        date_str = m["date"].strftime("%d %b %Y")
        venue = "H" if m["home"] == TEAM else "A"
        res = m["result"]
        color = result_color(res)
        home_badge = badge_img(m["home"], 22)
        away_badge = badge_img(m["away"], 22)

        st.markdown(
            f'<div class="match-card" style="border-left-color: {color};">'
            f'<div class="date">{date_str} &bull; {venue}</div>'
            f'<div class="teams">'
            f'{home_badge}<strong>{m["home"]}</strong>'
            f'&nbsp;&nbsp;<span class="score">{m["home_score"]} - {m["away_score"]}</span>&nbsp;&nbsp;'
            f'<strong>{m["away"]}</strong>{away_badge}'
            f'&nbsp;&nbsp;<span class="result-badge" style="background:{color};">{result_label(res)}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# =============================================================================
# RIGHT COLUMN — charts
# =============================================================================
with right:
    st.header("Cumulative Points")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(df["date"], df["cum_pts"], marker="o", markersize=2, color=BLUE)
    ax.set_ylabel("Points")
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", labelsize=7, rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.header("Goal Difference")
    fig, ax = plt.subplots(figsize=(6, 3))
    colors = df["gd"].apply(lambda x: BLUE if x > 0 else (YELLOW if x < 0 else "#cccccc"))
    ax.bar(df["date"], df["gd"], color=colors, width=2)
    ax.plot(df["date"], df["cum_gd"], color=BLUE, linewidth=1.5, label="Cumulative GD")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", labelsize=7, rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.header("Rolling Form")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.fill_between(df["date"], df["rolling_ppg"], alpha=0.2, color=BLUE)
    ax.plot(df["date"], df["rolling_ppg"], color=BLUE, linewidth=1.5)
    ax.axhline(2.0, color=YELLOW, linestyle="--", linewidth=2, alpha=0.8, label="Promotion (~2 PPG)")
    ax.axhline(1.0, color="#cc0000", linestyle="--", alpha=0.5, label="Relegation (~1 PPG)")
    ax.set_ylabel("PPG")
    ax.set_ylim(0, 3)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", labelsize=7, rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
