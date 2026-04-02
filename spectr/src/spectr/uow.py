"""Unit of work for Spectr HTML specs: lock a draft DOM, mutate, commit with id normalization.

Stable entity references use ``sid``. ``id`` attributes are document-order fragment ids,
recomputed on every commit and before any read/export path via ``load_for_read``.

Entity ``sid`` values are **stable**: once present they are never rewritten on load. Missing or
blank ``sid`` on known entities is filled with a new globally unique value (``prefix`` + UUID
segment). Q&A answers without a sid inherit the question’s sid when the question has one.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from lxml import etree

from spectr import ids, struct_validate, xmlio

HTML_ROOT = "html"


def clone_tree(root: etree._Element) -> etree._Element:
    """Deep copy of an element tree (lxml elements are not copy.deepcopy-safe)."""
    return etree.fromstring(etree.tostring(root, encoding="utf-8"))


def _element_needs_dom_id(el: etree._Element) -> bool:
    tag = el.tag
    if tag in ("h1", "h3"):
        return True
    if tag == "p":
        return True
    if tag == "li" and el.get("type") == "task":
        return True
    return False


def _strip_spurious_id(el: etree._Element) -> bool:
    if el.get("id") is None:
        return False
    tag = el.tag
    if tag in ("div", "ol", "ul", "body", "html", "head", "title"):
        el.attrib.pop("id", None)
        return True
    if tag == "li" and el.get("type") != "task":
        el.attrib.pop("id", None)
        return True
    if tag == "img":
        el.attrib.pop("id", None)
        return True
    return False


def recompute_dom_ids(root: etree._Element) -> bool:
    """Assign sequential ``id`` values (``1``, ``2``, …) in document order for h1, h3, p, and task li.

    Preserves all ``sid`` and other attributes. Removes stray ``id`` on structural elements.
    Returns whether any attribute was changed.
    """
    if root.tag != HTML_ROOT:
        raise ValueError(f"expected <{HTML_ROOT}> root, got <{root.tag}>")
    changed = False
    seq = 1
    for el in root.iter():
        if _element_needs_dom_id(el):
            new_id = str(seq)
            seq += 1
            if el.get("id") != new_id:
                el.set("id", new_id)
                changed = True
        elif _strip_spurious_id(el):
            changed = True
    return changed


def ensure_missing_entity_sids(root: etree._Element) -> bool:
    """Assign ``sid`` only where missing or blank. Existing sids are never changed. Returns whether anything changed."""
    if root.tag != HTML_ROOT:
        raise ValueError(f"expected <{HTML_ROOT}> root, got <{root.tag}>")
    body = root.find("body")
    if body is None:
        return False
    existing: set[str] = set(ids.collect_xml_ids(root))
    changed = False

    def fill_if_missing(el: etree._Element, prefix: str) -> None:
        nonlocal changed
        old = (el.get("sid") or "").strip()
        if old:
            return
        new = ids.new_prefixed_id(prefix, existing)
        el.set("sid", new)
        existing.add(new)
        changed = True

    for el in root.iter("p"):
        if el.get("type") == "acceptance-criteria":
            fill_if_missing(el, ids.PREFIX_AC)

    for el in root.iter("p"):
        if el.get("type") == "test":
            fill_if_missing(el, ids.PREFIX_TEST)

    for el in root.iter("div"):
        if el.get("type") == "use-case":
            fill_if_missing(el, ids.PREFIX_UC)

    fill_if_missing(body, ids.PREFIX_SPEC)

    for el in root.iter("p"):
        if el.get("type") == "feedback":
            fill_if_missing(el, ids.PREFIX_FB)

    for plan_div in body:
        if plan_div.tag != "div" or plan_div.get("type") != "plan":
            continue
        for el in plan_div.iter():
            if el is plan_div:
                continue
            if el.tag == "ol" and el.get("type") == "phase":
                fill_if_missing(el, ids.PREFIX_PHASE)
            elif el.tag == "li" and el.get("type") == "task":
                fill_if_missing(el, ids.PREFIX_TASK)

    def ensure_qdiv(qdiv: etree._Element) -> None:
        nonlocal changed
        thread: list[etree._Element] = []

        def flush() -> None:
            nonlocal changed, thread
            if not thread:
                return
            basis: str | None = None
            for p in thread:
                s = (p.get("sid") or "").strip()
                if s:
                    basis = s
                    break
            if basis:
                for p in thread:
                    if not (p.get("sid") or "").strip():
                        p.set("sid", basis)
                        changed = True
            else:
                new_sid = ids.new_prefixed_id(ids.PREFIX_Q, existing)
                existing.add(new_sid)
                for p in thread:
                    p.set("sid", new_sid)
                changed = True
            thread = []

        for child in qdiv:
            if child.tag != "p":
                continue
            typ = child.get("type")
            if typ == "question":
                flush()
                thread = [child]
            elif typ == "answer":
                if thread:
                    thread.append(child)
                elif not (child.get("sid") or "").strip():
                    new_sid = ids.new_prefixed_id(ids.PREFIX_Q, existing)
                    child.set("sid", new_sid)
                    existing.add(new_sid)
                    changed = True
        flush()

    for el in root.iter("div"):
        if el.get("type") == "questions":
            ensure_qdiv(el)

    return changed


def load_for_read(path: Path | str) -> etree._Element:
    """Load the spec from disk, normalize ``id`` attributes, persist if they changed, return the root.

    Call this before any list/read/export logic so the DOM matches the canonical numbering rule.
    """
    p = Path(path)
    root = xmlio.load_tree(p)
    struct_validate.assert_valid_spec(root)
    if root.tag != HTML_ROOT:
        raise ValueError(f"expected <{HTML_ROOT}> root, got <{root.tag}> in {p}")
    changed = ensure_missing_entity_sids(root)
    if recompute_dom_ids(root):
        changed = True
    if changed:
        xmlio.write_tree(p, root)
    return root


class SpecUnitOfWork:
    """Edit session: :meth:`lock` loads a clone; mutations apply to the clone; :meth:`commit` renumbers ids and writes."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._draft: etree._Element | None = None
        self._locked = False

    @property
    def locked(self) -> bool:
        return self._locked

    def lock(self) -> etree._Element:
        if self._locked:
            raise RuntimeError("spec unit of work is already locked")
        root = xmlio.load_tree(self.path)
        struct_validate.assert_valid_spec(root)
        if root.tag != HTML_ROOT:
            raise ValueError(f"expected <{HTML_ROOT}> root, got <{root.tag}> in {self.path}")
        changed = ensure_missing_entity_sids(root)
        if changed:
            xmlio.write_tree(self.path, root)
        self._draft = clone_tree(root)
        self._locked = True
        return self._draft

    def commit(self) -> None:
        if not self._locked or self._draft is None:
            raise RuntimeError("spec unit of work is not locked")
        recompute_dom_ids(self._draft)
        xmlio.write_tree(self.path, self._draft)
        self._draft = None
        self._locked = False

    def rollback(self) -> None:
        self._draft = None
        self._locked = False

    @classmethod
    @contextmanager
    def mutate(cls, path: Path | str) -> Iterator[etree._Element]:
        """Lock → yield draft root → commit (renumber + write) on success, rollback on failure."""
        u = cls(path)
        u.lock()
        try:
            assert u._draft is not None
            yield u._draft
        except BaseException:
            u.rollback()
            raise
        else:
            u.commit()
