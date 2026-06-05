"""Tests for fixtures fetching, with TheSportsDB calls mocked."""

import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fixtures


class FakeResp:
    def __init__(self, payload, status=200, text="x"):
        self._payload = payload
        self.status_code = status
        self.text = text

    def json(self):
        return self._payload


FUTURE = "2099-12-31"
PAST = "2000-01-01"


def _event(home, away, date, scored=None, rnd="20"):
    return {
        "strHomeTeam": home, "strAwayTeam": away, "dateEvent": date,
        "intHomeScore": scored, "strTime": "15:00:00", "strVenue": "Plough Lane",
        "intRound": rnd,
    }


def _fake_get(url):
    """Route TheSportsDB URLs to canned responses."""
    if "eventslast" in url:
        return FakeResp({"results": [{"intRound": "20"}]})
    if "eventsround" in url:
        r = int(parse_qs(urlparse(url).query)["r"][0])
        if r == 20:
            return FakeResp({"events": [
                _event(fixtures.TEAM, "Wigan", FUTURE),       # upcoming — keep
                _event("Reading", fixtures.TEAM, PAST, scored="1"),  # finished — drop
                _event("Other", "Teams", FUTURE),             # not us — drop
            ]})
        return FakeResp({"events": []})
    return FakeResp({}, status=404, text="")


def test_last_round_reads_intround(monkeypatch):
    monkeypatch.setattr(fixtures.requests, "get", lambda u: FakeResp({"results": [{"intRound": "33"}]}))
    assert fixtures._last_round() == 33


def test_last_round_defaults_to_one_on_empty(monkeypatch):
    monkeypatch.setattr(fixtures.requests, "get", lambda u: FakeResp({"results": []}))
    assert fixtures._last_round() == 1


def test_fetch_round_returns_events(monkeypatch):
    monkeypatch.setattr(fixtures.requests, "get",
                        lambda u: FakeResp({"events": [_event(fixtures.TEAM, "Wigan", FUTURE)]}))
    events = fixtures._fetch_round(20)
    assert len(events) == 1 and events[0]["strHomeTeam"] == fixtures.TEAM


def test_fetch_round_empty_on_error(monkeypatch):
    monkeypatch.setattr(fixtures.requests, "get", lambda u: FakeResp({}, status=500, text=""))
    assert fixtures._fetch_round(20) == []


def test_fetch_upcoming_keeps_only_our_future_unplayed(monkeypatch):
    monkeypatch.setattr(fixtures.requests, "get", lambda u: _fake_get(u))
    monkeypatch.setattr(fixtures.time, "sleep", lambda *_: None)
    matches = fixtures.fetch_upcoming(limit=1)
    assert len(matches) == 1
    m = matches[0]
    assert fixtures.TEAM in (m["strHomeTeam"], m["strAwayTeam"])
    assert m["dateEvent"] == FUTURE
    assert m["intHomeScore"] is None


def test_display_handles_empty(capsys):
    fixtures.display([])
    out = capsys.readouterr().out
    assert "No upcoming fixtures" in out
