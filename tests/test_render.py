from __future__ import annotations

import json

from code_review_bot.models import Finding
from code_review_bot.render import render

FINDINGS = [
    Finding("a.py", 2, "naming", "low", "Bad name."),
    Finding("a.py", 5, "security", "high", "Unsafe input."),
    Finding("b.py", 1, "style", "low", "Trailing space."),
]


def test_json_format_roundtrips() -> None:
    out = render(FINDINGS, "json")
    parsed = json.loads(out)
    assert len(parsed) == 3
    assert parsed[0] == {
        "file": "a.py",
        "line": 2,
        "category": "naming",
        "severity": "low",
        "message": "Bad name.",
    }


def test_inline_format() -> None:
    out = render(FINDINGS, "inline")
    lines = out.splitlines()
    assert lines[0] == "a.py:2 [low] naming — Bad name."
    assert lines[1] == "a.py:5 [high] security — Unsafe input."
    assert lines[2] == "b.py:1 [low] style — Trailing space."


def test_summary_groups_by_file() -> None:
    out = render(FINDINGS, "summary")
    assert "a.py (2 finding(s)):" in out
    assert "b.py (1 finding(s)):" in out
    assert "line 2 [low] naming — Bad name." in out


def test_summary_empty() -> None:
    assert render([], "summary") == "No findings."


def test_inline_empty() -> None:
    assert render([], "inline") == ""
