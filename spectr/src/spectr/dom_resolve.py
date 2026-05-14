"""Map DOM fragment ``id`` attributes (normalized ``1``, ``2``, …) to entity ``sid`` values."""

from __future__ import annotations

from lxml import etree

from spectr.spec_ops import _body


def find_by_dom_id(root: etree._Element, node_id: str) -> etree._Element | None:
    if not node_id:
        return None
    for el in root.iter():
        if el.get("id") == node_id:
            return el
    return None


def _ancestor_use_case_sid(el: etree._Element | None) -> str | None:
    cur: etree._Element | None = el
    while cur is not None:
        if cur.tag == "div" and cur.get("type") == "use-case":
            return cur.get("sid")
        cur = cur.getparent()
    return None


def uc_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "div" and el.get("type") == "use-case":
        return el.get("sid")
    return _ancestor_use_case_sid(el)


def ac_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "p" and el.get("type") == "acceptance-criteria":
        return el.get("sid")
    return None


def br_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "p" and el.get("type") == "business-rule":
        return el.get("sid")
    return None


def def_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "p" and el.get("type") == "definition":
        return el.get("sid")
    return None


def ref_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    """Reference link ``sid`` from an ``<a>`` node's DOM fragment ``id`` (under ``ul type=references``)."""
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "a" and (el.get("href") or "").strip():
        return (el.get("sid") or "").strip() or None
    return None


def feedback_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "p" and el.get("type") == "feedback":
        return el.get("sid")
    return None


def task_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "li" and el.get("type") == "task":
        return el.get("sid")
    return None


def qs_target_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    """Resolve entity sid for ``qs ask`` targets: spec (body), use case, acceptance criterion, or business rule."""
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "h1":
        return _body(root).get("sid")
    if el.tag == "p" and el.get("type") == "desc":
        return _body(root).get("sid")
    if el.tag == "p" and el.get("type") == "acceptance-criteria":
        return el.get("sid")
    if el.tag == "p" and el.get("type") == "business-rule":
        return el.get("sid")
    if el.tag == "p" and el.get("type") == "definition":
        return el.get("sid")
    sid = _ancestor_use_case_sid(el)
    if sid:
        return sid
    return None


def qs_thread_sid_from_dom_id(root: etree._Element, node_id: str) -> str | None:
    """Thread sid from a ``question`` or ``answer`` paragraph's DOM id."""
    el = find_by_dom_id(root, node_id)
    if el is None:
        return None
    if el.tag == "p" and el.get("type") in ("question", "answer"):
        return el.get("sid")
    return None
