"""Multi-command CLI unit of work: draft beside the spec until ``commit`` or ``abort``."""

from __future__ import annotations

import json
from pathlib import Path

from spectr import xmlio
from spectr.uow import load_for_read, recompute_dom_ids

SPECTR_DIR = ".spectr"
META_NAME = "uow.json"
DRAFT_NAME = "uow-draft.html"


def _spectr_dir(canonical_spec: Path) -> Path:
    return canonical_spec.resolve().parent / SPECTR_DIR


def _meta_path(canonical_spec: Path) -> Path:
    return _spectr_dir(canonical_spec) / META_NAME


def _draft_path(canonical_spec: Path) -> Path:
    return _spectr_dir(canonical_spec) / DRAFT_NAME


def read_meta(canonical_spec: Path) -> dict | None:
    mp = _meta_path(canonical_spec)
    if not mp.is_file():
        return None
    return json.loads(mp.read_text(encoding="utf-8"))


def is_active(canonical_spec: Path) -> bool:
    c = canonical_spec.resolve()
    meta = read_meta(c)
    if not meta:
        return False
    orig = Path(meta["original"]).resolve()
    if orig != c:
        return False
    return Path(meta["draft"]).is_file()


def resolve_working_spec_path(spec: Path) -> Path:
    """Path to edit/read: session draft when a UoW is active, else the canonical spec file."""
    c = spec.resolve()
    if is_active(c):
        meta = read_meta(c)
        assert meta is not None
        return Path(meta["draft"]).resolve()
    return c


def _cleanup_empty_spectr_dir(canonical_spec: Path) -> None:
    d = _spectr_dir(canonical_spec)
    if d.is_dir():
        try:
            next(d.iterdir())
        except StopIteration:
            d.rmdir()


def begin(canonical_spec: Path) -> None:
    c = canonical_spec.resolve()
    if is_active(c):
        raise ValueError(f"Unit of work already active for {c}")
    ddir = _spectr_dir(c)
    ddir.mkdir(parents=True, exist_ok=True)
    draft = _draft_path(c)
    mp = _meta_path(c)
    if draft.exists() and not mp.is_file():
        draft.unlink()
    root = load_for_read(c)
    xmlio.write_tree(draft, root)
    mp.write_text(
        json.dumps({"original": str(c), "draft": str(draft.resolve())}, indent=2),
        encoding="utf-8",
    )


def commit(canonical_spec: Path) -> None:
    c = canonical_spec.resolve()
    if not is_active(c):
        raise ValueError(f"No active unit of work for {c}")
    meta = read_meta(c)
    assert meta is not None
    draft = Path(meta["draft"])
    orig = Path(meta["original"]).resolve()
    root = xmlio.load_tree(draft)
    if root.tag != "html":
        raise ValueError("draft root is not <html>")
    recompute_dom_ids(root)
    xmlio.write_tree(orig, root)
    draft.unlink(missing_ok=True)
    _meta_path(c).unlink(missing_ok=True)
    _cleanup_empty_spectr_dir(c)


def abort(canonical_spec: Path) -> None:
    c = canonical_spec.resolve()
    meta = read_meta(c)
    if meta:
        Path(meta["draft"]).unlink(missing_ok=True)
    mp = _meta_path(c)
    if mp.is_file():
        mp.unlink()
    dp = _draft_path(c)
    if dp.is_file():
        dp.unlink()
    _cleanup_empty_spectr_dir(c)


def status_lines(canonical_spec: Path) -> list[str]:
    c = canonical_spec.resolve()
    if not is_active(c):
        return ["No active unit of work for this spec."]
    meta = read_meta(c)
    assert meta is not None
    return [
        "Unit of work active.",
        f"  original: {meta['original']}",
        f"  draft:    {meta['draft']}",
        "  Run `spectr uow commit` to write the draft to the spec file, or `spectr uow abort` to discard it.",
    ]
