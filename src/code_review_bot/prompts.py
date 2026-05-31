"""Prompt construction for the review model."""

from __future__ import annotations

from .models import FileDiff


def build_review_prompt(file_diff: FileDiff) -> str:
    """Build a structured prompt asking the model to return findings as JSON."""
    lines: list[str] = []
    lines.append(
        "You are a code reviewer. Review the following diff for one file and "
        "report issues."
    )
    lines.append("")
    lines.append(f"File: {file_diff.path}")
    lines.append("")
    lines.append("Diff:")
    for hunk in file_diff.hunks:
        lines.append(hunk.header)
        for dline in hunk.lines:
            prefix = {"add": "+", "remove": "-", "context": " "}[dline.kind]
            loc = "" if dline.new_lineno is None else f"  (line {dline.new_lineno})"
            lines.append(f"{prefix}{dline.content}{loc}")
    lines.append("")
    lines.append(
        "Return your findings as a JSON array. Each element must be an object "
        "with these fields:"
    )
    lines.append('  - "file": the file path (string)')
    lines.append('  - "line": the line number in the new file (integer)')
    lines.append('  - "category": one of "style", "bug_risk", "security", "naming"')
    lines.append('  - "severity": one of "low", "medium", "high"')
    lines.append('  - "message": a short description of the issue (string)')
    lines.append("")
    lines.append("Return only the JSON array, with no other text.")
    return "\n".join(lines)
