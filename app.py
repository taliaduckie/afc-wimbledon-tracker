"""
Streamlit dashboard for AFC Wimbledon Tracker.

Run with: streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent / "data"
RESULTS_PATH = DATA_DIR / "results.json"
TEAM = "AFC Wimbledon"

st.set_page_config(page_title="Wombles Tracker", page_icon="\u26bd", layout="wide")

# AFC Wimbledon colors
BLUE = "#003DA5"
YELLOW = "#FFD700"

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
    .stMetric label {{
        color: {BLUE} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {BLUE} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("\u26bd AFC Wimbledon Tracker")
st.caption("GO WOMBLES")

if not RESULTS_PATH.exists():
    st.warning("No results found. Run `python -m src fetch` first.")
    st.stop()

with open(RESULTS_PATH) as f:
    results = json.load(f)

df = pd.DataFrame(results)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# --- Season summary ---
st.header("Season Summary")
wins = (df["result"] == "W").sum()
draws = (df["result"] == "D").sum()
losses = (df["result"] == "L").sum()
df["gf"] = df.apply(lambda r: r["home_score"] if r["home"] == TEAM else r["away_score"], axis=1)
df["ga"] = df.apply(lambda r: r["away_score"] if r["home"] == TEAM else r["home_score"], axis=1)
gf = df["gf"].sum()
ga = df["ga"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Played", len(df))
c2.metric("W / D / L", f"{wins} / {draws} / {losses}")
c3.metric("Points", wins * 3 + draws)
c4.metric("GF", gf)
c5.metric("GA", ga)
c6.metric("GD", f"{'+' if gf - ga > 0 else ''}{gf - ga}")

form = "".join(df["result"].tail(5).tolist())
st.markdown(f"**Form (last 5):** `{form}`")

# --- Cumulative points ---
st.header("Cumulative Points")
df["points"] = df["result"].map({"W": 3, "D": 1, "L": 0})
df["cum_pts"] = df["points"].cumsum()

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(df["date"], df["cum_pts"], marker="o", markersize=3, color=BLUE)
ax.set_ylabel("Points")
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# --- Goal difference ---
st.header("Goal Difference")
df["gd"] = df["gf"] - df["ga"]
df["cum_gd"] = df["gd"].cumsum()

fig, ax = plt.subplots(figsize=(10, 3.5))
colors = df["gd"].apply(lambda x: BLUE if x > 0 else (YELLOW if x < 0 else "#cccccc"))
ax.bar(df["date"], df["gd"], color=colors, width=2)
ax.plot(df["date"], df["cum_gd"], color=BLUE, linewidth=1.5, label="Cumulative GD")
ax.axhline(0, color="gray", linewidth=0.5)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# --- Rolling form ---
st.header("Rolling Form (5-match PPG)")
df["rolling_ppg"] = df["points"].rolling(5, min_periods=1).mean() * 3

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.fill_between(df["date"], df["rolling_ppg"], alpha=0.2, color=BLUE)
ax.plot(df["date"], df["rolling_ppg"], color=BLUE, linewidth=1.5)
ax.axhline(2.0, color=YELLOW, linestyle="--", linewidth=2, alpha=0.8, label="Promotion pace (~2 PPG)")
ax.axhline(1.0, color="#cc0000", linestyle="--", alpha=0.5, label="Relegation pace (~1 PPG)")
ax.set_ylabel("PPG (scaled to 3)")
ax.set_ylim(0, 3)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# --- Home vs Away ---
st.header("Home vs Away")
df["venue"] = df["home"].apply(lambda h: "Home" if h == TEAM else "Away")

col1, col2 = st.columns(2)
for venue, col in [("Home", col1), ("Away", col2)]:
    sub = df[df["venue"] == venue]
    w = (sub["result"] == "W").sum()
    d = (sub["result"] == "D").sum()
    l = (sub["result"] == "L").sum()
    col.subheader(venue)
    col.write(f"**{len(sub)}** played: {w}W {d}D {l}L ({w*3+d} pts)")

# --- Opponent records ---
st.header("Record by Opponent")
opponents = {}
for _, m in df.iterrows():
    opp = m["away"] if m["home"] == TEAM else m["home"]
    if opp not in opponents:
        opponents[opp] = {"Opponent": opp, "P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0}
    r = opponents[opp]
    r["P"] += 1
    r[m["result"]] += 1
    r["GF"] += m["gf"]
    r["GA"] += m["ga"]

opp_df = pd.DataFrame(opponents.values())
opp_df["GD"] = opp_df["GF"] - opp_df["GA"]
opp_df["Pts"] = opp_df["W"] * 3 + opp_df["D"]
opp_df["PPG"] = (opp_df["Pts"] / opp_df["P"]).round(1)
opp_df = opp_df.sort_values("PPG").reset_index(drop=True)
st.dataframe(opp_df, use_container_width=True, hide_index=True)

# --- Results log ---
st.header("All Results")
display_df = df[["date", "home", "home_score", "away_score", "away", "result"]].copy()
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df.columns = ["Date", "Home", "HG", "AG", "Away", "Result"]
st.dataframe(display_df.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
