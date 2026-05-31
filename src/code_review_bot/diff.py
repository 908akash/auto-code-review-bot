"""Parser for standard `git diff` unified output."""

from __future__ import annotations

import re

from .models import DiffLine, FileDiff, Hunk

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_diff(text: str) -> list[FileDiff]:
    """Parse unified git diff text into a list of FileDiff objects.

    Tracks new-file line numbers so findings can point to real lines.
    Pure function: no I/O, no network.
    """
    files: list[FileDiff] = []
    current_file: FileDiff | None = None
    current_hunk: Hunk | None = None
    new_lineno = 0

    for line in text.splitlines():
        if line.startswith("diff --git"):
            current_file = None
            current_hunk = None
            continue

        if line.startswith("+++ "):
            path = line[4:]
            if path.startswith("b/"):
                path = path[2:]
            current_file = FileDiff(path=path, hunks=[])
            files.append(current_file)
            current_hunk = None
            continue

        if line.startswith("--- "):
            # old-file header; path comes from the +++ line instead
            continue

        match = _HUNK_RE.match(line)
        if match:
            if current_file is None:
                continue
            old_start = int(match.group(1))
            new_start = int(match.group(2))
            current_hunk = Hunk(
                header=line, old_start=old_start, new_start=new_start, lines=[]
            )
            current_file.hunks.append(current_hunk)
            new_lineno = new_start
            continue

        if current_hunk is None:
            continue

        if line.startswith("+"):
            current_hunk.lines.append(
                DiffLine(kind="add", content=line[1:], new_lineno=new_lineno)
            )
            new_lineno += 1
        elif line.startswith("-"):
            current_hunk.lines.append(
                DiffLine(kind="remove", content=line[1:], new_lineno=None)
            )
        elif line.startswith(" "):
            current_hunk.lines.append(
                DiffLine(kind="context", content=line[1:], new_lineno=new_lineno)
            )
            new_lineno += 1
        # Any other line (e.g. "\ No newline at end of file") is ignored.

    return files
