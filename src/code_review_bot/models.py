"""Data structures for diffs and review findings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class DiffLine:
    kind: Literal["add", "remove", "context"]
    content: str
    new_lineno: int | None


@dataclass
class Hunk:
    header: str
    old_start: int
    new_start: int
    lines: list[DiffLine]


@dataclass
class FileDiff:
    path: str
    hunks: list[Hunk]


@dataclass
class Finding:
    file: str
    line: int
    category: Literal["style", "bug_risk", "security", "naming"]
    severity: Literal["low", "medium", "high"]
    message: str
