from __future__ import annotations

import sys

PORCELAIN_SEP = "\t"


def format_porcelain(kind: str, entity_id: str) -> str:
    return f"{kind}{PORCELAIN_SEP}{entity_id}"


def parse_porcelain_line(line: str) -> tuple[str, str] | None:
    s = line.strip()
    if not s:
        return None
    if PORCELAIN_SEP in s:
        kind, _, rest = s.partition(PORCELAIN_SEP)
        return kind.strip(), rest.strip()
    if "-" in s:
        pfx, _, _ = s.partition("-")
        return pfx, s
    return "id", s


def read_stdin_text() -> str | None:
    if sys.stdin.isatty():
        return None
    data = sys.stdin.read()
    if not data or not data.strip():
        return None
    return data


def read_stdin_first_line() -> str | None:
    text = read_stdin_text()
    if text is None:
        return None
    return text.strip().splitlines()[0]


def read_stdin_id_and_body() -> tuple[str | None, str | None]:
    """First line: entity id (or kind\\tid porcelain). Remaining lines: body text."""
    text = read_stdin_text()
    if text is None:
        return None, None
    stripped = text.strip().splitlines()
    if not stripped:
        return None, None
    first = stripped[0].strip()
    parsed = parse_porcelain_line(first)
    eid = parsed[1] if parsed else first
    if len(stripped) > 1:
        body = "\n".join(stripped[1:]).strip()
    else:
        body = None
    return eid, body


def resolve_entity_id(
    explicit: str | None,
    *,
    use_stdin_if_dash: bool = True,
    use_stdin_if_piped: bool = False,
) -> str | None:
    if explicit and explicit != "-":
        return explicit
    if explicit == "-" and use_stdin_if_dash:
        line = read_stdin_first_line()
        if line:
            parsed = parse_porcelain_line(line)
            return parsed[1] if parsed else line
        return None
    if explicit is None and use_stdin_if_piped and not sys.stdin.isatty():
        line = read_stdin_first_line()
        if line:
            parsed = parse_porcelain_line(line)
            return parsed[1] if parsed else line
    return None
