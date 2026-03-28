from __future__ import annotations

from pathlib import Path


def find_file_upward(
    filenames: tuple[str, ...],
    *,
    start: Path | None = None,
) -> Path | None:
    """
    Walk from ``start`` (default: cwd) toward filesystem root.

    At each directory, look for an existing file whose name is in ``filenames``,
    in order. Return the first match (closest ancestor directory wins).
    """
    cur = (start or Path.cwd()).resolve()
    while True:
        for name in filenames:
            candidate = cur / name
            if candidate.is_file():
                return candidate
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None


def find_spec_html_upward(start: Path | None = None) -> Path | None:
    return find_file_upward(("spec.html",), start=start)
