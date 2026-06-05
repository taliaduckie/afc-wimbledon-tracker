"""Tests for squad parsing, diffing, and transfer recording."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import squad


def _p(pid, name, pos="Forward", num="9"):
    return {"id": pid, "name": name, "position": pos, "nationality": "England", "number": num}


# --- parse_player ---

def test_parse_player_maps_fields():
    raw = {"idPlayer": "1", "strPlayer": "Joe", "strPosition": "Forward",
           "strNationality": "Wales", "strNumber": "7"}
    p = squad.parse_player(raw)
    assert p == {"id": "1", "name": "Joe", "position": "Forward", "nationality": "Wales", "number": "7"}


def test_parse_player_handles_missing():
    p = squad.parse_player({"idPlayer": "2", "strPlayer": "Sam"})
    assert p["position"] == "" and p["nationality"] == "" and p["number"] == ""


# --- diff_squads ---

def test_diff_detects_arrival_and_departure():
    old = [_p("1", "Stayer"), _p("2", "Leaver")]
    new = [_p("1", "Stayer"), _p("3", "Joiner")]
    arrivals, departures = squad.diff_squads(old, new)
    assert [p["id"] for p in arrivals] == ["3"]
    assert [p["id"] for p in departures] == ["2"]


def test_diff_no_change():
    roster = [_p("1", "A"), _p("2", "B")]
    arrivals, departures = squad.diff_squads(roster, list(roster))
    assert arrivals == [] and departures == []


# --- build_moves ---

def test_build_moves_tags_in_and_out():
    arrivals = [_p("3", "Joiner", "Defender")]
    departures = [_p("2", "Leaver", "Midfielder")]
    moves = squad.build_moves(arrivals, departures, "2026-01-10")
    assert {"date": "2026-01-10", "type": "in", "name": "Joiner", "position": "Defender"} in moves
    assert {"date": "2026-01-10", "type": "out", "name": "Leaver", "position": "Midfielder"} in moves


# --- fetch_and_record (baseline + subsequent diffs) ---

def test_first_fetch_is_baseline_no_moves(tmp_path, monkeypatch):
    monkeypatch.setattr(squad, "DATA_DIR", tmp_path)
    monkeypatch.setattr(squad, "SQUAD_PATH", tmp_path / "squad.json")
    monkeypatch.setattr(squad, "TRANSFERS_PATH", tmp_path / "transfers.json")
    monkeypatch.setattr(squad, "fetch_squad", lambda: [_p("1", "A"), _p("2", "B")])

    roster, moves = squad.fetch_and_record(date="2026-01-01")
    assert len(roster) == 2
    assert moves == []  # first snapshot records nothing
    assert not (tmp_path / "transfers.json").exists()


def test_subsequent_fetch_records_moves(tmp_path, monkeypatch):
    monkeypatch.setattr(squad, "DATA_DIR", tmp_path)
    monkeypatch.setattr(squad, "SQUAD_PATH", tmp_path / "squad.json")
    monkeypatch.setattr(squad, "TRANSFERS_PATH", tmp_path / "transfers.json")

    monkeypatch.setattr(squad, "fetch_squad", lambda: [_p("1", "A"), _p("2", "B")])
    squad.fetch_and_record(date="2026-01-01")  # baseline

    # B leaves, C arrives
    monkeypatch.setattr(squad, "fetch_squad", lambda: [_p("1", "A"), _p("3", "C")])
    _, moves = squad.fetch_and_record(date="2026-01-15")

    kinds = {(m["type"], m["name"]) for m in moves}
    assert ("in", "C") in kinds
    assert ("out", "B") in kinds
    assert squad.load_transfers()  # persisted to the log
