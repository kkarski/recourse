from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

# New entity ``sid`` values use ``{prefix}-{segment}`` where *segment* is the first 8-character
# hex group of a UUID (see :func:`uuid_first_segment`). Assigned sids are stable; the tool only
# fills missing ``sid`` attributes on load (see :func:`spectr.uow.ensure_missing_entity_sids`).
_SID_HEX8 = re.compile(r"^[0-9a-f]{8}$")

PREFIX_SPEC = "spec"
PREFIX_UC = "uc"
PREFIX_AC = "ac"
PREFIX_TEST = "tst"
PREFIX_Q = "q"
PREFIX_PHASE = "ph"
PREFIX_TASK = "tsk"
PREFIX_FB = "fb"


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def uuid_first_segment() -> str:
    return str(uuid.uuid4()).split("-")[0].lower()


def is_canonical_sid(prefix: str, sid: str | None) -> bool:
    """True if *sid* matches the format produced by :func:`new_prefixed_id` (not a stability check)."""
    if not sid or not isinstance(sid, str):
        return False
    s = sid.strip()
    head = f"{prefix}-"
    if not s.startswith(head):
        return False
    return bool(_SID_HEX8.match(s[len(head) :]))


def new_prefixed_id(prefix: str, existing: set[str] | None = None) -> str:
    for _ in range(64):
        candidate = f"{prefix}-{uuid_first_segment()}"
        if existing is None or candidate not in existing:
            return candidate
    raise RuntimeError("could not allocate unique id")


def collect_xml_ids(root) -> set[str]:
    out: set[str] = set()
    for el in root.iter():
        i = el.get("id")
        if i:
            out.add(i)
        s = el.get("sid")
        if s:
            out.add(s)
    return out
