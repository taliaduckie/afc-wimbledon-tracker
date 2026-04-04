"""Tests for restaurant_score.score() and difficulty_color()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from restaurant_score import score, difficulty_color


# --- score() ---

def test_easy_restaurant():
    """Walk-in friendly, no lead time, no waitlist."""
    s = score(weeks_out=0, walkin="yes", platform="opentable", waitlist="no")
    assert s == 0


def test_hard_restaurant():
    """Long lead time, no walk-ins, resy, waitlist."""
    s = score(weeks_out=8, walkin="no", platform="resy", waitlist="yes")
    # 5 (capped lead time) + 2 (no walkin) + 1 (resy) + 1.5 (waitlist) = 9.5
    assert s == 9.5


def test_max_score_capped_at_9_5():
    """Max possible is 5 (weeks cap) + 2 (no walkin) + 1 (resy) + 1.5 (waitlist) = 9.5."""
    s = score(weeks_out=100, walkin="no", platform="resy", waitlist="yes")
    assert s == 9.5
    assert s <= 10


def test_moderate_restaurant():
    """A few weeks out, no walk-in, opentable."""
    s = score(weeks_out=2, walkin="no", platform="opentable", waitlist="no")
    # 2.4 (weeks) + 2 (no walkin) + 0 + 0 = 4.4
    assert s == 4.4


def test_walkin_reduces_score():
    s_walkin = score(weeks_out=2, walkin="yes", platform="opentable", waitlist="no")
    s_no_walkin = score(weeks_out=2, walkin="no", platform="opentable", waitlist="no")
    assert s_walkin < s_no_walkin


def test_resy_adds_point():
    s_resy = score(weeks_out=2, walkin="no", platform="resy", waitlist="no")
    s_other = score(weeks_out=2, walkin="no", platform="opentable", waitlist="no")
    assert s_resy == s_other + 1


def test_waitlist_adds_points():
    s_wl = score(weeks_out=0, walkin="yes", platform="opentable", waitlist="yes")
    s_no_wl = score(weeks_out=0, walkin="yes", platform="opentable", waitlist="no")
    assert s_wl - s_no_wl == 1.5


# --- difficulty_color() ---

def test_color_red():
    assert difficulty_color(7.0) == "red"
    assert difficulty_color(10.0) == "red"


def test_color_yellow():
    assert difficulty_color(4.0) == "yellow"
    assert difficulty_color(6.9) == "yellow"


def test_color_green():
    assert difficulty_color(0.0) == "green"
    assert difficulty_color(3.9) == "green"
