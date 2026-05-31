from __future__ import annotations

from pathlib import Path

from code_review_bot.diff import parse_diff

SAMPLES = Path(__file__).parent.parent / "benchmarks" / "samples"


def _read(name: str) -> str:
    return (SAMPLES / name).read_text(encoding="utf-8")


def test_empty_diff() -> None:
    assert parse_diff("") == []


def test_single_file() -> None:
    files = parse_diff(_read("single_file.diff"))
    assert len(files) == 1
    assert files[0].path == "example.py"
    assert len(files[0].hunks) == 1


def test_single_file_hunk_starts() -> None:
    hunk = parse_diff(_read("single_file.diff"))[0].hunks[0]
    assert hunk.old_start == 1
    assert hunk.new_start == 1


def test_single_file_line_numbers() -> None:
    hunk = parse_diff(_read("single_file.diff"))[0].hunks[0]
    # @@ -1,4 +1,5 @@
    #  import os        context -> new line 1
    # -x = 1            remove  -> None
    # +x = 2            add     -> new line 2
    # +y = 3            add     -> new line 3
    #  print(x)         context -> new line 4
    kinds = [(line.kind, line.new_lineno) for line in hunk.lines]
    assert kinds == [
        ("context", 1),
        ("remove", None),
        ("add", 2),
        ("add", 3),
        ("context", 4),
    ]


def test_multiple_files() -> None:
    files = parse_diff(_read("multi_file.diff"))
    assert [f.path for f in files] == ["alpha.py", "beta.py"]


def test_multiple_hunks_per_file() -> None:
    files = parse_diff(_read("multi_file.diff"))
    alpha = files[0]
    assert len(alpha.hunks) == 2
    assert alpha.hunks[0].new_start == 1
    assert alpha.hunks[1].new_start == 11


def test_second_hunk_line_numbers() -> None:
    alpha = parse_diff(_read("multi_file.diff"))[0]
    second = alpha.hunks[1]
    # @@ -10,2 +11,3 @@
    #      pass         context -> 11
    # +    extra = True  add    -> 12
    #  # tail           context -> 13
    kinds = [(line.kind, line.new_lineno) for line in second.lines]
    assert kinds == [
        ("context", 11),
        ("add", 12),
        ("context", 13),
    ]


def test_add_line_content_stripped_of_marker() -> None:
    hunk = parse_diff(_read("single_file.diff"))[0].hunks[0]
    adds = [line.content for line in hunk.lines if line.kind == "add"]
    assert adds == ["x = 2", "y = 3"]
