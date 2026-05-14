from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

# Auto-assigned ``sid`` values use ``{prefix}-{segment}`` where *segment* is the first 8-character
# hex group of a UUID (see :func:`uuid_first_segment`). User-supplied ``--with-sid`` values must be
# non-empty and unique among other entity ``sid`` values; see
# :func:`require_unique_override_sid`. Assigned sids are stable; the tool only fills missing
# ``sid`` attributes on load (see :func:`spectr.uow.ensure_missing_entity_sids`).
_SID_HEX8 = re.compile(r"^[0-9a-f]{8}$")

PREFIX_SPEC = "spec"
PREFIX_UC = "uc"
PREFIX_BR = "br"
PREFIX_AC = "ac"
PREFIX_Q = "q"
PREFIX_PHASE = "ph"
PREFIX_TASK = "tsk"
PREFIX_FB = "fb"
PREFIX_DEF = "def"
PREFIX_REF = "ref"


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


def require_unused_canonical_sid(prefix: str, sid: str, existing: set[str]) -> str:
    """Validate *sid* for *prefix* and ensure it is not already present in *existing*.

    Raises ``ValueError`` if the format is wrong or the sid is taken.
    """
    s = (sid or "").strip()
    if not is_canonical_sid(prefix, s):
        raise ValueError(
            f"invalid {prefix} sid {s!r}: expected {prefix}- plus 8 lowercase hex digits"
        )
    if s in existing:
        raise ValueError(f"sid already in use: {s}")
    return s


def require_unique_override_sid(sid: str, existing_sids: set[str]) -> str:
    """Validate a user-chosen ``--with-sid`` value: non-empty and unique among entity ``sid``s.

    Fragment ``id`` values are not considered; only :func:`collect_sids` needs to match.
    Auto-allocation still uses :func:`new_prefixed_id` (which avoids collision with both ids and
    sids when generating the default shape).
    """
    s = (sid or "").strip()
    if not s:
        raise ValueError("empty sid")
    if s in existing_sids:
        raise ValueError(f"sid already in use: {s!r}")
    return s


def new_prefixed_id(prefix: str, existing: set[str] | None = None) -> str:
    """Allocate a new ``{prefix}-xxxxxxxx`` sid not in *existing*.

    When *existing* is provided, the chosen value is **added** to the set so multiple
    allocations in the same batch cannot return the same candidate.
    """
    for _ in range(64):
        candidate = f"{prefix}-{uuid_first_segment()}"
        if existing is None or candidate not in existing:
            if existing is not None:
                existing.add(candidate)
            return candidate
    raise RuntimeError("could not allocate unique id")


def assert_entity_sid_singleton(root, sid: str) -> None:
    """After inserting a new node, raise ``ValueError`` unless *sid* appears on exactly one element.

    Catches duplicate entity sids (same ``sid`` attribute on multiple nodes) across the tree.
    """
    s = (sid or "").strip()
    if not s:
        raise ValueError("empty sid")
    n = sum(1 for el in root.iter() if (el.get("sid") or "").strip() == s)
    if n != 1:
        raise ValueError(
            f"expected exactly one element with entity sid {s!r}, found {n} "
            "(duplicate sid or missing attribute)"
        )


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


def collect_sids(root) -> set[str]:
    """All non-empty ``sid`` attribute values in the document (stripped)."""
    out: set[str] = set()
    for el in root.iter():
        s = el.get("sid")
        if s:
            t = s.strip()
            if t:
                out.add(t)
    return out
