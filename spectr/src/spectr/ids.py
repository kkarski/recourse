from __future__ import annotations

import uuid
from datetime import datetime, timezone

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
