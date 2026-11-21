"""Smoke tests for the unified CLI argument parser (src/__main__.py)."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.__main__ import build_parser


def test_all_subcommands_registered():
    parser = build_parser()
    sub = next(a for a in parser._actions if a.dest == "action")
    assert set(sub.choices) == {"fetch", "table", "opponents", "fixtures", "standings", "players"}


def test_standings_parses_with_top():
    parser = build_parser()
    args = parser.parse_args(["standings", "--top", "6"])
    assert args.action == "standings"
    assert args.top == 6


def test_standings_parses_without_top():
    parser = build_parser()
    args = parser.parse_args(["standings"])
    assert args.action == "standings"
    assert args.top is None


def test_no_action_is_allowed():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.action is None


@pytest.mark.parametrize("name", ["fetch_results", "fixtures", "squad"])
def test_direct_script_help(name):
    result = subprocess.run(
        [sys.executable, "-E", f"src/{name}.py", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage:" in result.stdout
