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
    cur = (start or Path.cwd()).resolve()
    while True:
        canonical = cur / "spec.html"
        if canonical.is_file():
            return canonical
        matches = sorted(
            p for p in cur.glob("*_spec.html") if p.is_file()
        )
        if matches:
            return matches[0]
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None
