from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple

from lxml import etree

from spectr import ids
from spectr.uc_cli_layout import (
    UC_LOOSE_NARRATIVE_FORBIDDEN,
    apply_uc_front_matter,
    set_uc_front_matter,
)
from spectr.xmlio import (
    definition_get_body,
    definition_get_term,
    definition_has_term_span,
    definition_set_term_and_body,
    get_text_content,
    set_text_content,
    write_tree,
)

# Block order for top-level body divs (after h1 and desc).
_BODY_BLOCK_ORDER = (
    "references",
    "definitions",
    "use-case",
    "business-rules",
    "acceptance-criteria",
    "tests",
    "questions",
    "feedback",
    "plan",
)

_TERM_MAX_CHARS = 100
_DEFINITION_BODY_MAX_CHARS = 500
_BR_NORMATIVE_WORD_RE = re.compile(r"\b(must|may|cannot|can)\b", re.IGNORECASE)
_AC_GIVEN_RE = re.compile(r"\bgiven\b", re.IGNORECASE)
_AC_WHEN_RE = re.compile(r"\bwhen\b", re.IGNORECASE)
_AC_THEN_RE = re.compile(r"\bthen\b", re.IGNORECASE)


def _validate_acceptance_criteria_text(text: str) -> None:
    given_matches = list(_AC_GIVEN_RE.finditer(text))
    when_matches = list(_AC_WHEN_RE.finditer(text))
    then_matches = list(_AC_THEN_RE.finditer(text))
    given_count = len(given_matches)
    if given_count > 1:
        raise ValueError(
            "Stop! Re-plan. Multiple acceptance criteria should be added (spectr uc add) as separate ACs; "
            f"split this text into {given_count} ACs. Do not simply rephrase."
        )
    if len(given_matches) != 1 or len(when_matches) != 1 or len(then_matches) != 1:
        raise ValueError(
            "Stop! Re-plan. Multiple acceptance criteria should be added (spectr uc add) as separate ACs. Do not simply rephrase."
        )
    given_pos = given_matches[0].start()
    when_pos = when_matches[0].start()
    then_pos = then_matches[0].start()
    if not (given_pos < when_pos < then_pos):
        raise ValueError(
            "Stop! Re-plan. Multiple acceptance criteria should be added (spectr uc add) as separate ACs. Do not simply rephrase."
        )


def _validate_business_rule_text(text: str) -> None:
    if _BR_NORMATIVE_WORD_RE.search(text):
        return
    raise ValueError(
        'business-rule text must contain at least one of: "must", "may", "can", "cannot"'
    )


def _validate_definition_term_and_body(term: str | None, body: str) -> None:
    term_value = (term or "").strip()
    if len(term_value) > _TERM_MAX_CHARS:
        raise ValueError(
            f"definition term must be at most {_TERM_MAX_CHARS} characters "
            "(split different terms into separate definitions)"
        )
    if len(body) > _DEFINITION_BODY_MAX_CHARS:
        raise ValueError(
            f"definition body must be at most {_DEFINITION_BODY_MAX_CHARS} characters "
            "(split different terms into separate definitions)"
        )


def element_is_deprecated(el: etree._Element) -> bool:
    """True if ``deprecated`` is set to a truthy XML boolean (``true``, ``1``, ``yes``)."""
    v = (el.get("deprecated") or "").strip().lower()
    return v in ("true", "1", "yes")


def _apply_deprecated(el: etree._Element, deprecated: bool) -> None:
    if deprecated:
        el.set("deprecated", "true")
    else:
        el.attrib.pop("deprecated", None)


class UcRead(NamedTuple):
    """Snapshot of use-case body fields (no ``sid`` on trigger / actors / pre / post nodes).

    A well-formed use case has a non-empty trigger, at least one actor, precondition, and postcondition.
    """

    title: str | None
    desc: str
    trigger: str | None
    actors: tuple[str, ...]
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]


def _ancestor_use_case_div(el: etree._Element | None) -> etree._Element | None:
    cur: etree._Element | None = el
    while cur is not None:
        if cur.tag == "div" and (cur.get("type") or "").strip() == "use-case":
            return cur
        cur = cur.getparent()
    return None


def _assert_br_ac_under_uc_not_deprecated(uc: etree._Element | None) -> None:
    if uc is not None and element_is_deprecated(uc):
        raise ValueError(f"cannot update content under deprecated use case {uc.get('sid')}")


def _guard_br_ac_update(
    p: etree._Element,
    sid: str,
    desc: str | None,
    deprecated: bool | None,
) -> None:
    uc = _ancestor_use_case_div(p)
    _assert_br_ac_under_uc_not_deprecated(uc)
    if element_is_deprecated(p):
        if desc is not None:
            raise ValueError(f"cannot update text of deprecated entity {sid}")
        if deprecated is None:
            raise ValueError(
                f"entity {sid} is deprecated; pass --not-deprecated or --deprecated explicitly"
            )


def _assert_qs_target_mutable(root: etree._Element, target_id: str) -> None:
    tid = (target_id or "").strip()
    body = _body(root)
    if (body.get("sid") or "").strip() == tid:
        return
    uc = _find_uc_div(body, tid)
    if uc is not None:
        if element_is_deprecated(uc):
            raise ValueError(f"cannot add Q&A to deprecated use case {tid}")
        return
    p = _find_ac_p(root, tid)
    if p is not None:
        if element_is_deprecated(p):
            raise ValueError(f"cannot add Q&A to deprecated acceptance criterion {tid}")
        _assert_br_ac_under_uc_not_deprecated(_ancestor_use_case_div(p))
        return
    p = _find_br_p(root, tid)
    if p is not None:
        if element_is_deprecated(p):
            raise ValueError(f"cannot add Q&A to deprecated business rule {tid}")
        _assert_br_ac_under_uc_not_deprecated(_ancestor_use_case_div(p))
        return


def _assert_no_deprecated_ancestor(el: etree._Element) -> None:
    cur: etree._Element | None = el
    while cur is not None:
        if element_is_deprecated(cur):
            raise ValueError("cannot modify Q&A under a deprecated entity")
        cur = cur.getparent()


def _body(root: etree._Element) -> etree._Element:
    if root.tag != "html":
        raise ValueError("expected <html> root")
    b = root.find("body")
    if b is None:
        raise ValueError("expected <body>")
    return b


def _alloc_id(existing: set[str]) -> str:
    for _ in range(128):
        c = f"i-{ids.uuid_first_segment()}"
        if c not in existing:
            existing.add(c)
            return c
    raise RuntimeError("could not allocate unique id")


def _desc_p(body: etree._Element) -> etree._Element | None:
    for child in body:
        if child.tag == "p" and child.get("type") == "desc":
            return child
    return None


def _insert_after(body: etree._Element, after: etree._Element, el: etree._Element) -> None:
    idx = list(body).index(after)
    body.insert(idx + 1, el)


def _body_child_block_order(child: etree._Element) -> str | None:
    """Map a direct ``body`` child to ``_BODY_BLOCK_ORDER``, or ``None`` for ``h1`` / ``desc`` ``p``."""
    if child.tag == "h1":
        return None
    if child.tag == "p" and child.get("type") == "desc":
        return None
    if child.tag == "ul" and child.get("type") == "references":
        return "references"
    if child.tag == "div":
        bt = child.get("type")
        if bt in _BODY_BLOCK_ORDER:
            return bt
    return None


def _insert_body_block(body: etree._Element, el: etree._Element, block_type: str) -> None:
    """Insert *el* before the first body block whose order is >= *block_type* (after ``h1`` + ``desc``)."""
    want = _BODY_BLOCK_ORDER.index(block_type)
    insert_at = None
    for i, child in enumerate(body):
        key = _body_child_block_order(child)
        if key is None:
            continue
        if _BODY_BLOCK_ORDER.index(key) >= want:
            insert_at = i
            break
    if insert_at is not None:
        body.insert(insert_at, el)
    else:
        body.append(el)


def _insert_body_div(body: etree._Element, div: etree._Element, block_type: str) -> None:
    _insert_body_block(body, div, block_type)


def _ensure_body_block_div(body: etree._Element, block_type: str) -> etree._Element:
    for child in body:
        if child.tag == "div" and child.get("type") == block_type:
            return child
    div = etree.Element("div", type=block_type)
    _insert_body_div(body, div, block_type)
    return div


# --- empty section-container pruning (after deletes) ---

_PRUNABLE_SECTION_DIV_TYPES = frozenset(
    {
        "definitions",
        "business-rules",
        "acceptance-criteria",
        "tests",
        "questions",
        "feedback",
        "plan",
    }
)


def _questions_div_has_question(div: etree._Element) -> bool:
    return any(
        ch.tag == "p" and (ch.get("type") or "").strip() == "question" for ch in div
    )


def _phase_ol_has_tasks(ol: etree._Element) -> bool:
    return any(
        ch.tag == "li" and (ch.get("type") or "").strip() == "task" for ch in ol
    )


def _cleanup_nested_empty_containers(div: etree._Element) -> None:
    """Remove nested empty ``questions`` / empty phase ``ol`` nodes before checking whether *div* is empty."""
    bt = (div.get("type") or "").strip()
    if bt in ("business-rules", "acceptance-criteria"):
        for ch in list(div):
            if ch.tag == "div" and ch.get("type") == "questions":
                if not _questions_div_has_question(ch):
                    div.remove(ch)
    elif bt == "plan":
        for ch in list(div):
            if ch.tag == "ol" and ch.get("type") == "phase":
                if not _phase_ol_has_tasks(ch):
                    div.remove(ch)


def _section_container_is_empty(div: etree._Element) -> bool:
    """True if this section ``div`` has no remaining substantive children after nested cleanup."""
    if div.tag != "div":
        return False
    _cleanup_nested_empty_containers(div)
    bt = (div.get("type") or "").strip()
    if bt not in _PRUNABLE_SECTION_DIV_TYPES:
        return False
    if bt == "definitions":
        return not any(
            ch.tag == "p" and (ch.get("type") or "").strip() == "definition" for ch in div
        )
    if bt == "business-rules":
        return not any(
            ch.tag == "p" and (ch.get("type") or "").strip() == "business-rule" for ch in div
        )
    if bt == "acceptance-criteria":
        return not any(
            ch.tag == "p" and (ch.get("type") or "").strip() == "acceptance-criteria"
            for ch in div
        )
    if bt == "tests":
        return not any(ch.tag == "p" and (ch.get("type") or "").strip() == "test" for ch in div)
    if bt == "feedback":
        return not any(
            ch.tag == "p" and (ch.get("type") or "").strip() == "feedback" for ch in div
        )
    if bt == "questions":
        return not _questions_div_has_question(div)
    if bt == "plan":
        for ch in div:
            if ch.tag == "ol" and ch.get("type") == "phase" and _phase_ol_has_tasks(ch):
                return False
        return True
    return False


def prune_empty_section_containers_upward(
    root: etree._Element, start: etree._Element | None
) -> None:
    """Remove empty section wrappers (definitions, business-rules, AC, tests, questions, feedback, plan).

    After removing an entity paragraph, pass the removed node's parent so parents chain can collapse
    (e.g. last BR deleted → empty ``business-rules`` div removed → …).
    """
    if start is None:
        return
    cur: etree._Element | None = start
    while cur is not None:
        gp = cur.getparent()
        if gp is None:
            break
        _cleanup_nested_empty_containers(cur)
        if (
            cur.tag == "ol"
            and (cur.get("type") or "").strip() == "phase"
            and not _phase_ol_has_tasks(cur)
        ):
            gp.remove(cur)
            cur = gp
            continue
        if (
            cur.tag == "div"
            and (cur.get("type") or "").strip() in _PRUNABLE_SECTION_DIV_TYPES
            and _section_container_is_empty(cur)
        ):
            gp.remove(cur)
            cur = gp
            continue
        break


def _last_use_case_div(body: etree._Element) -> etree._Element | None:
    last = None
    for child in body:
        if child.tag == "div" and child.get("type") == "use-case":
            last = child
    return last


def _insert_new_use_case(body: etree._Element, div: etree._Element) -> None:
    last_uc = _last_use_case_div(body)
    if last_uc is not None:
        _insert_after(body, last_uc, div)
        return
    # First use case: honor ``references`` → ``definitions`` → … → ``use-case`` body block order.
    # Inserting only after ``desc`` breaks validation when definitions or references exist first.
    _insert_body_block(body, div, "use-case")


def _find_uc_div(body: etree._Element, uc_sid: str) -> etree._Element | None:
    for child in body:
        if child.tag == "div" and child.get("type") == "use-case" and child.get("sid") == uc_sid:
            return child
    return None


def _collect_narrative_text(uc_div: etree._Element) -> str:
    parts: list[str] = []
    for ch in uc_div:
        if ch.tag == "h3":
            continue
        if ch.tag != "p":
            break
        pt = (ch.get("type") or "").strip()
        if pt == "trigger":
            break
        if pt in UC_LOOSE_NARRATIVE_FORBIDDEN:
            break
        parts.append(get_text_content(ch))
    return "\n\n".join(parts).strip()


def _uc_narrative_p(uc_div: etree._Element) -> etree._Element | None:
    for ch in uc_div:
        if ch.tag == "h3":
            continue
        if ch.tag != "p":
            return None
        pt = (ch.get("type") or "").strip()
        if pt == "trigger":
            return None
        if pt in UC_LOOSE_NARRATIVE_FORBIDDEN:
            return None
        return ch
    return None


def _parse_uc_trigger(uc_div: etree._Element) -> str | None:
    kids = list(uc_div)
    i = 1 if kids and kids[0].tag == "h3" else 0
    while i < len(kids) and kids[i].tag == "p" and (kids[i].get("type") or "").strip() != "trigger":
        i += 1
    if i < len(kids) and kids[i].tag == "p" and (kids[i].get("type") or "").strip() == "trigger":
        t = get_text_content(kids[i]).strip()
        return t if t else None
    return None


def _parse_uc_actors(uc_div: etree._Element) -> tuple[str, ...]:
    for ch in uc_div:
        if ch.tag == "div" and (ch.get("type") or "").strip() == "actors":
            out: list[str] = []
            for p in ch.findall("p"):
                if (p.get("type") or "").strip() != "actor":
                    continue
                t = get_text_content(p).strip()
                if t:
                    out.append(t)
            return tuple(out)
    return ()


def _parse_uc_cond_list(uc_div: etree._Element, div_type: str) -> tuple[str, ...]:
    out: list[str] = []
    for ch in uc_div:
        if ch.tag == "div" and (ch.get("type") or "").strip() == div_type:
            inner = "precondition" if div_type == "preconditions" else "postcondition"
            for p in ch.findall("p"):
                if (p.get("type") or "").strip() != inner:
                    continue
                t = get_text_content(p).strip()
                if t:
                    out.append(t)
            break
    return tuple(out)


def _deprecate_br_ac_under_uc(uc_div: etree._Element) -> None:
    ts = ids.iso_now()
    for ch in uc_div:
        if ch.tag != "div":
            continue
        bt = (ch.get("type") or "").strip()
        if bt == "business-rules":
            for p in ch.findall("p"):
                if (p.get("type") or "").strip() != "business-rule":
                    continue
                _apply_deprecated(p, True)
                p.set("ts", ts)
        elif bt == "acceptance-criteria":
            for p in ch.findall("p"):
                if (p.get("type") or "").strip() != "acceptance-criteria":
                    continue
                _apply_deprecated(p, True)
                p.set("ts", ts)


def _ensure_uc_br_div(uc_div: etree._Element) -> etree._Element:
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "business-rules":
            return ch
    div = etree.Element("div", type="business-rules")
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "acceptance-criteria":
            idx = list(uc_div).index(ch)
            uc_div.insert(idx, div)
            return div
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "questions":
            idx = list(uc_div).index(ch)
            uc_div.insert(idx, div)
            return div
    uc_div.append(div)
    return div


def _ensure_uc_ac_div(uc_div: etree._Element) -> etree._Element:
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "acceptance-criteria":
            return ch
    div = etree.Element("div", type="acceptance-criteria")
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "business-rules":
            idx = list(uc_div).index(ch)
            uc_div.insert(idx + 1, div)
            return div
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "questions":
            idx = list(uc_div).index(ch)
            uc_div.insert(idx, div)
            return div
    uc_div.append(div)
    return div


def _ensure_uc_questions_div(uc_div: etree._Element) -> etree._Element:
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "questions":
            return ch
    div = etree.Element("div", type="questions")
    uc_div.append(div)
    return div


def _ensure_ac_questions_div(ac_container: etree._Element) -> etree._Element:
    for ch in ac_container:
        if ch.tag == "div" and ch.get("type") == "questions":
            return ch
    div = etree.SubElement(ac_container, "div", type="questions")
    return div


def _ensure_br_questions_div(br_container: etree._Element) -> etree._Element:
    return _ensure_ac_questions_div(br_container)


def _ensure_body_questions_div(body: etree._Element) -> etree._Element:
    return _ensure_body_block_div(body, "questions")


def _find_ac_p(root: etree._Element, ac_sid: str) -> etree._Element | None:
    for el in root.iter("p"):
        if el.get("type") == "acceptance-criteria" and el.get("sid") == ac_sid:
            return el
    return None


def _find_br_p(root: etree._Element, br_sid: str) -> etree._Element | None:
    for el in root.iter("p"):
        if el.get("type") == "business-rule" and el.get("sid") == br_sid:
            return el
    return None


def _find_test_p(root: etree._Element, test_sid: str) -> etree._Element | None:
    for el in root.iter("p"):
        if el.get("type") == "test" and el.get("sid") == test_sid:
            return el
    return None


def _question_thread_ref(question_p: etree._Element) -> str | None:
    cur: etree._Element | None = question_p
    while cur is not None:
        parent = cur.getparent()
        if parent is None:
            break
        if parent.tag == "div" and parent.get("type") == "use-case":
            return parent.get("sid")
        if parent.tag == "div" and parent.get("type") == "acceptance-criteria":
            for ch in parent:
                if ch.tag == "p" and ch.get("type") == "acceptance-criteria":
                    return ch.get("sid")
            return None
        if parent.tag == "div" and parent.get("type") == "business-rules":
            for ch in parent:
                if ch.tag == "p" and ch.get("type") == "business-rule":
                    return ch.get("sid")
            return None
        cur = parent
    return None


# --- use cases ---


def _assert_uc_structured_fields(
    *,
    trigger: str,
    actors: tuple[str, ...],
    preconditions: tuple[str, ...],
    postconditions: tuple[str, ...],
) -> None:
    if not (trigger or "").strip():
        raise ValueError("use case requires a non-empty trigger")
    act = tuple((s or "").strip() for s in actors if (s or "").strip())
    if len(act) < 1:
        raise ValueError("use case requires at least one actor")
    pres = tuple((s or "").strip() for s in preconditions if (s or "").strip())
    if len(pres) < 1:
        raise ValueError("use case requires at least one precondition")
    posts = tuple((s or "").strip() for s in postconditions if (s or "").strip())
    if len(posts) < 1:
        raise ValueError("use case requires at least one postcondition")


def uc_add(
    root: etree._Element,
    title: str,
    desc: str,
    *,
    user_sid: str | None = None,
    trigger: str = "",
    actors: tuple[str, ...] = (),
    preconditions: tuple[str, ...] = (),
    postconditions: tuple[str, ...] = (),
) -> str:
    _assert_uc_structured_fields(
        trigger=trigger,
        actors=actors,
        preconditions=preconditions,
        postconditions=postconditions,
    )
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        uc_sid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        uc_sid = ids.new_prefixed_id(ids.PREFIX_UC, existing)
    existing.add(uc_sid)
    ts = ids.iso_now()
    div = etree.Element("div", type="use-case", sid=uc_sid, ts=ts)
    h3_id = _alloc_id(existing)
    h3 = etree.SubElement(div, "h3", id=h3_id)
    set_text_content(h3, title)
    apply_uc_front_matter(
        div,
        existing,
        desc=desc,
        trigger=trigger,
        actors=actors,
        preconditions=preconditions,
        postconditions=postconditions,
    )
    _insert_new_use_case(body, div)
    ids.assert_entity_sid_singleton(root, uc_sid)
    return uc_sid


def uc_list(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str | None, str]]:
    body = _body(root)
    out: list[tuple[str, str | None, str]] = []
    for child in body:
        if child.tag != "div" or child.get("type") != "use-case":
            continue
        if element_is_deprecated(child) and not include_deprecated:
            continue
        sid = child.get("sid") or ""
        h3 = child.find("h3")
        tit = (h3.text or "").strip() if h3 is not None and h3.text else ""
        if h3 is not None:
            tit = get_text_content(h3).strip() or tit
        de = _collect_narrative_text(child)
        out.append((sid, tit or None, de))
    return out


def uc_read(root: etree._Element, uc_id: str) -> UcRead | None:
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return None
    h3 = uc.find("h3")
    tit = get_text_content(h3).strip() if h3 is not None else None
    desc = _collect_narrative_text(uc)
    return UcRead(
        title=tit or None,
        desc=desc,
        trigger=_parse_uc_trigger(uc),
        actors=_parse_uc_actors(uc),
        preconditions=_parse_uc_cond_list(uc, "preconditions"),
        postconditions=_parse_uc_cond_list(uc, "postconditions"),
    )


def uc_update(
    root: etree._Element,
    uc_id: str,
    *,
    title: str,
    desc: str,
    trigger: str = "",
    actors: tuple[str, ...] = (),
    preconditions: tuple[str, ...] = (),
    postconditions: tuple[str, ...] = (),
) -> None:
    _assert_uc_structured_fields(
        trigger=trigger,
        actors=actors,
        preconditions=preconditions,
        postconditions=postconditions,
    )
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        raise ValueError(f"use case not found: {uc_id}")
    if element_is_deprecated(uc):
        raise ValueError(
            f"cannot update deprecated use case {uc_id}; run uc restore first"
        )
    existing = ids.collect_xml_ids(root)
    h3 = uc.find("h3")
    if h3 is None:
        hid = _alloc_id(existing)
        h3 = etree.SubElement(uc, "h3", id=hid)
        uc.insert(0, h3)
    set_text_content(h3, title)
    set_uc_front_matter(
        uc,
        existing,
        desc=desc,
        trigger=trigger,
        actors=actors,
        preconditions=preconditions,
        postconditions=postconditions,
    )
    uc.set("ts", ids.iso_now())


def uc_deprecate(root: etree._Element, uc_id: str) -> bool:
    """Mark a use case deprecated and recursively deprecate BR/AC nodes scoped under it."""
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return False
    if element_is_deprecated(uc):
        return True
    _apply_deprecated(uc, True)
    uc.set("ts", ids.iso_now())
    _deprecate_br_ac_under_uc(uc)
    return True


def uc_restore(root: etree._Element, uc_id: str) -> bool:
    """Clear deprecation on the use-case div only (BR/AC remain as-is)."""
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return False
    if not element_is_deprecated(uc):
        return True
    _apply_deprecated(uc, False)
    uc.set("ts", ids.iso_now())
    return True


def uc_delete(root: etree._Element, uc_id: str) -> bool:
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return False
    body.remove(uc)
    return True


# --- acceptance criteria ---


def ac_add(
    root: etree._Element,
    desc: str,
    *,
    under_uc_id: str | None,
    user_sid: str | None = None,
) -> str:
    _validate_acceptance_criteria_text((desc or "").strip())
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        ac_sid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        ac_sid = ids.new_prefixed_id(ids.PREFIX_AC, existing)
    existing.add(ac_sid)
    ts = ids.iso_now()
    pid = _alloc_id(existing)
    p = etree.Element("p", type="acceptance-criteria", id=pid, sid=ac_sid, ts=ts)
    set_text_content(p, desc)
    if under_uc_id:
        uc = _find_uc_div(body, under_uc_id)
        if uc is None:
            raise ValueError(f"use case not found: {under_uc_id}")
        if element_is_deprecated(uc):
            raise ValueError(f"use case is deprecated: {under_uc_id}")
        ac_div = _ensure_uc_ac_div(uc)
        ac_div.append(p)
    else:
        ac_div = _ensure_body_block_div(body, "acceptance-criteria")
        ac_div.append(p)
    ids.assert_entity_sid_singleton(root, ac_sid)
    return ac_sid


def ac_list_flat(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    body = _body(root)
    for child in body:
        if child.tag == "div" and child.get("type") == "acceptance-criteria":
            for ac in child.findall("p"):
                if ac.get("type") != "acceptance-criteria":
                    continue
                if element_is_deprecated(ac) and not include_deprecated:
                    continue
                sid = ac.get("sid") or ""
                d = get_text_content(ac).strip()
                out.append((sid, "spec", d[:120]))
    for uc in body.findall("div"):
        if uc.get("type") != "use-case":
            continue
        uid = uc.get("sid") or ""
        for acd in uc.findall("div"):
            if acd.get("type") != "acceptance-criteria":
                continue
            for ac in acd.findall("p"):
                if ac.get("type") != "acceptance-criteria":
                    continue
                if element_is_deprecated(ac) and not include_deprecated:
                    continue
                sid = ac.get("sid") or ""
                d = get_text_content(ac).strip()
                out.append((sid, f"uc:{uid}", d[:120]))
    return out


def ac_list_recursive(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for scope, sid, _ in ac_list_flat(root, include_deprecated=include_deprecated):
        rows.append((scope, sid))
    return rows


def ac_read(root: etree._Element, ac_id: str) -> str | None:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return None
    return get_text_content(p)


def ac_update(
    root: etree._Element,
    ac_id: str,
    desc: str | None = None,
    *,
    deprecated: bool | None = None,
) -> str | None:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return None
    if desc is None and deprecated is None:
        return (p.get("sid") or "").strip() or None
    _guard_br_ac_update(p, ac_id, desc, deprecated)
    if desc is not None:
        _validate_acceptance_criteria_text((desc or "").strip())
        set_text_content(p, desc)
    if deprecated is not None:
        _apply_deprecated(p, deprecated)
    if desc is not None or deprecated is not None:
        p.set("ts", ids.iso_now())
    return (p.get("sid") or "").strip() or None


def ac_delete(root: etree._Element, ac_id: str) -> bool:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return False
    parent = p.getparent()
    if parent is None:
        return False
    parent.remove(p)
    prune_empty_section_containers_upward(root, parent)
    return True


# --- business rules ---


def br_add(
    root: etree._Element,
    desc: str,
    *,
    under_uc_id: str | None,
    user_sid: str | None = None,
) -> str:
    _validate_business_rule_text((desc or "").strip())
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        br_sid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        br_sid = ids.new_prefixed_id(ids.PREFIX_BR, existing)
    existing.add(br_sid)
    ts = ids.iso_now()
    pid = _alloc_id(existing)
    p = etree.Element("p", type="business-rule", id=pid, sid=br_sid, ts=ts)
    set_text_content(p, desc)
    if under_uc_id:
        uc = _find_uc_div(body, under_uc_id)
        if uc is None:
            raise ValueError(f"use case not found: {under_uc_id}")
        if element_is_deprecated(uc):
            raise ValueError(f"use case is deprecated: {under_uc_id}")
        br_div = _ensure_uc_br_div(uc)
        br_div.append(p)
    else:
        br_div = _ensure_body_block_div(body, "business-rules")
        br_div.append(p)
    ids.assert_entity_sid_singleton(root, br_sid)
    return br_sid


def br_list_flat(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    body = _body(root)
    for child in body:
        if child.tag == "div" and child.get("type") == "business-rules":
            for br in child.findall("p"):
                if br.get("type") != "business-rule":
                    continue
                if element_is_deprecated(br) and not include_deprecated:
                    continue
                sid = br.get("sid") or ""
                d = get_text_content(br).strip()
                out.append((sid, "spec", d[:120]))
    for uc in body.findall("div"):
        if uc.get("type") != "use-case":
            continue
        uid = uc.get("sid") or ""
        for brd in uc.findall("div"):
            if brd.get("type") != "business-rules":
                continue
            for br in brd.findall("p"):
                if br.get("type") != "business-rule":
                    continue
                if element_is_deprecated(br) and not include_deprecated:
                    continue
                sid = br.get("sid") or ""
                d = get_text_content(br).strip()
                out.append((sid, f"uc:{uid}", d[:120]))
    return out


def br_list_recursive(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for scope, sid, _ in br_list_flat(root, include_deprecated=include_deprecated):
        rows.append((scope, sid))
    return rows


def br_read(root: etree._Element, br_id: str) -> str | None:
    p = _find_br_p(root, br_id)
    if p is None:
        return None
    return get_text_content(p)


def br_update(
    root: etree._Element,
    br_id: str,
    desc: str | None = None,
    *,
    deprecated: bool | None = None,
) -> str | None:
    p = _find_br_p(root, br_id)
    if p is None:
        return None
    if desc is None and deprecated is None:
        return (p.get("sid") or "").strip() or None
    _guard_br_ac_update(p, br_id, desc, deprecated)
    if desc is not None:
        _validate_business_rule_text((desc or "").strip())
        set_text_content(p, desc)
    if deprecated is not None:
        _apply_deprecated(p, deprecated)
    if desc is not None or deprecated is not None:
        p.set("ts", ids.iso_now())
    return (p.get("sid") or "").strip() or None


def br_delete(root: etree._Element, br_id: str) -> bool:
    p = _find_br_p(root, br_id)
    if p is None:
        return False
    parent = p.getparent()
    if parent is None:
        return False
    parent.remove(p)
    prune_empty_section_containers_upward(root, parent)
    return True


# --- definitions (body div type=definitions; top-level only) ---


def _definitions_div(body: etree._Element) -> etree._Element | None:
    for child in body:
        if child.tag == "div" and child.get("type") == "definitions":
            return child
    return None


def _find_def_p(root: etree._Element, def_id: str) -> etree._Element | None:
    body = _body(root)
    div = _definitions_div(body)
    if div is None:
        return None
    for p in div.findall("p"):
        if p.get("type") == "definition" and (p.get("sid") or "").strip() == def_id:
            return p
    return None


def def_add(
    root: etree._Element,
    desc: str,
    *,
    section: str,
    term: str | None = None,
    user_sid: str | None = None,
) -> str:
    sec = (section or "").strip()
    if not sec:
        raise ValueError("definition section must be non-empty")
    _validate_definition_term_and_body(term, desc)
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        did = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        did = ids.new_prefixed_id(ids.PREFIX_DEF, existing)
    existing.add(did)
    ts = ids.iso_now()
    pid = _alloc_id(existing)
    p = etree.Element(
        "p",
        type="definition",
        id=pid,
        sid=did,
        section=sec,
        ts=ts,
    )
    definition_set_term_and_body(p, (term or "").strip() or None, desc)
    div = _ensure_body_block_div(body, "definitions")
    div.append(p)
    ids.assert_entity_sid_singleton(root, did)
    return did


def def_list_flat(
    root: etree._Element, *, include_deprecated: bool = False
) -> list[tuple[str, str, str, str]]:
    """Top-level definitions only: ``(sid, section, term, preview)``."""
    out: list[tuple[str, str, str, str]] = []
    body = _body(root)
    div = _definitions_div(body)
    if div is None:
        return out
    for p in div.findall("p"):
        if p.get("type") != "definition":
            continue
        if element_is_deprecated(p) and not include_deprecated:
            continue
        sid = (p.get("sid") or "").strip()
        sec = (p.get("section") or "").strip()
        tm = definition_get_term(p)
        d = definition_get_body(p)
        out.append((sid, sec, tm, d[:120]))
    return out


def def_read(
    root: etree._Element, def_id: str
) -> tuple[str, str, str] | None:
    """``(section, term, body)`` text; term may be empty."""
    p = _find_def_p(root, def_id)
    if p is None:
        return None
    sec = (p.get("section") or "").strip()
    return sec, definition_get_term(p), definition_get_body(p)


def def_update(
    root: etree._Element,
    def_id: str,
    desc: str | None = None,
    *,
    section: str | None = None,
    term: str | None = None,
    remove_term: bool = False,
    deprecated: bool | None = None,
) -> str | None:
    p = _find_def_p(root, def_id)
    if p is None:
        return None
    tm_cur = definition_get_term(p)
    bd_cur = definition_get_body(p)
    if remove_term:
        tm_cur = ""
    elif term is not None:
        tm_cur = (term or "").strip()
    if desc is not None:
        bd_cur = desc
    if remove_term or term is not None or desc is not None:
        _validate_definition_term_and_body(tm_cur, bd_cur)
    if remove_term or term is not None or desc is not None:
        definition_set_term_and_body(p, tm_cur if tm_cur else None, bd_cur)
    if section is not None:
        s = section.strip()
        if not s:
            raise ValueError("definition section must be non-empty")
        p.set("section", s)
    if deprecated is not None:
        _apply_deprecated(p, deprecated)
    if (
        desc is not None
        or section is not None
        or term is not None
        or remove_term
        or deprecated is not None
    ):
        p.set("ts", ids.iso_now())
    return (p.get("sid") or "").strip() or None


def def_delete(root: etree._Element, def_id: str) -> bool:
    p = _find_def_p(root, def_id)
    if p is None:
        return False
    parent = p.getparent()
    if parent is None:
        return False
    parent.remove(p)
    prune_empty_section_containers_upward(root, parent)
    return True


# --- tests (body div type=tests; p type=test) ---


def _ensure_body_tests_div(body: etree._Element) -> etree._Element:
    return _ensure_body_block_div(body, "tests")


def test_add(
    root: etree._Element, ac_id: str, desc: str, *, user_sid: str | None = None
) -> str:
    if _find_ac_p(root, ac_id) is None:
        raise ValueError(f"acceptance criterion not found: {ac_id}")
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        tst_sid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        tst_sid = ids.new_prefixed_id(ids.PREFIX_TEST, existing)
    existing.add(tst_sid)
    ts = ids.iso_now()
    tid = _alloc_id(existing)
    p = etree.Element(
        "p",
        type="test",
        id=tid,
        sid=tst_sid,
        ref_id=ac_id,
        ts=ts,
    )
    set_text_content(p, desc)
    tdiv = _ensure_body_tests_div(body)
    tdiv.append(p)
    ids.assert_entity_sid_singleton(root, tst_sid)
    return tst_sid


def test_read(root: etree._Element, test_id: str) -> tuple[str | None, str | None] | None:
    p = _find_test_p(root, test_id)
    if p is None:
        return None
    ref = p.get("ref_id")
    return ref, get_text_content(p)


def test_update(root: etree._Element, test_id: str, desc: str | None) -> bool:
    p = _find_test_p(root, test_id)
    if p is None:
        return False
    if desc is not None:
        set_text_content(p, desc)
    p.set("ts", ids.iso_now())
    return True


def test_delete(root: etree._Element, test_id: str) -> bool:
    p = _find_test_p(root, test_id)
    if p is None:
        return False
    parent = p.getparent()
    if parent is None:
        return False
    parent.remove(p)
    prune_empty_section_containers_upward(root, parent)
    return True


# --- Q&A ---


def _resolve_qs_container(root: etree._Element, target_id: str) -> etree._Element:
    body = _body(root)
    if body.get("sid") == target_id:
        return _ensure_body_questions_div(body)
    uc = _find_uc_div(body, target_id)
    if uc is not None:
        return _ensure_uc_questions_div(uc)
    acp = _find_ac_p(root, target_id)
    if acp is not None:
        parent = acp.getparent()
        if parent is None:
            raise ValueError("invalid acceptance criterion parent")
        return _ensure_ac_questions_div(parent)
    brp = _find_br_p(root, target_id)
    if brp is not None:
        parent = brp.getparent()
        if parent is None:
            raise ValueError("invalid business rule parent")
        return _ensure_br_questions_div(parent)
    raise ValueError(f"entity not found for ref_id: {target_id}")


def qs_ask(
    root: etree._Element,
    target_id: str,
    question: str,
    *,
    author: str | None,
    target_role: str | None,
    user_sid: str | None = None,
) -> str:
    _assert_qs_target_mutable(root, target_id)
    container = _resolve_qs_container(root, target_id)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        thread_sid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
    else:
        thread_sid = ids.new_prefixed_id(ids.PREFIX_Q, existing)
    existing.add(thread_sid)
    pid = _alloc_id(existing)
    qel = etree.Element("p", type="question", id=pid, sid=thread_sid, ts=ids.iso_now())
    if author:
        qel.set("author", author)
    if target_role:
        qel.set("target", target_role)
    set_text_content(qel, question)
    container.append(qel)
    ids.assert_entity_sid_singleton(root, thread_sid)
    return thread_sid


def qs_answer(root: etree._Element, thread_id: str, body: str, *, author: str | None) -> bool:
    for q in root.iter("p"):
        if q.get("type") != "question" or q.get("sid") != thread_id:
            continue
        _assert_no_deprecated_ancestor(q)
        parent = q.getparent()
        if parent is None:
            return False
        for ch in parent:
            if ch.tag == "p" and ch.get("type") == "answer" and ch.get("sid") == thread_id:
                set_text_content(ch, body)
                if author:
                    ch.set("author", author)
                ch.set("ts", ids.iso_now())
                return True
        existing = ids.collect_xml_ids(root)
        pid = _alloc_id(existing)
        ans = etree.Element("p", type="answer", id=pid, sid=thread_id, ts=ids.iso_now())
        if author:
            ans.set("author", author)
        set_text_content(ans, body)
        parent.insert(list(parent).index(q) + 1, ans)
        return True
    return False


def qs_list(root: etree._Element, *, include_deprecated: bool = False) -> list[tuple[str, str | None, str | None, str]]:
    rows: list[tuple[str, str | None, str | None, str]] = []
    for q in root.iter("p"):
        if q.get("type") != "question":
            continue
        if element_is_deprecated(q) and not include_deprecated:
            continue
        sid = q.get("sid")
        if not sid:
            continue
        auth = q.get("author")
        ref = _question_thread_ref(q)
        prev = get_text_content(q)[:80]
        rows.append((sid, ref, auth, prev))
    return rows


def qs_set_deprecated(root: etree._Element, thread_id: str, *, deprecated: bool) -> bool:
    for q in root.iter("p"):
        if q.get("type") != "question" or q.get("sid") != thread_id:
            continue
        _apply_deprecated(q, deprecated)
        q.set("ts", ids.iso_now())
        return True
    return False


def qs_delete(root: etree._Element, thread_id: str) -> bool:
    """Remove a Q&A thread: all ``p`` elements with types ``question`` and ``answer`` for ``sid=thread_id``."""
    to_remove: list[etree._Element] = []
    for p in root.iter("p"):
        if p.get("sid") != thread_id:
            continue
        if (p.get("type") or "").strip() not in ("question", "answer"):
            continue
        to_remove.append(p)
    if not to_remove:
        return False
    parents: list[etree._Element] = []
    seen: set[int] = set()
    for p in to_remove:
        gp = p.getparent()
        if gp is not None and id(gp) not in seen:
            seen.add(id(gp))
            parents.append(gp)
    for p in to_remove:
        par = p.getparent()
        if par is not None:
            par.remove(p)
    for par in parents:
        prune_empty_section_containers_upward(root, par)
    return True


# --- feedback ---


def feedback_add(root: etree._Element, text: str, *, author: str | None) -> str:
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    fb_sid = ids.new_prefixed_id(ids.PREFIX_FB, existing)
    ts = ids.iso_now()
    pid = _alloc_id(existing)
    fdiv = _ensure_body_block_div(body, "feedback")
    p = etree.Element("p", type="feedback", id=pid, sid=fb_sid, ts=ts)
    if author:
        p.set("author", author)
    set_text_content(p, text)
    fdiv.append(p)
    return fb_sid


def feedback_delete(root: etree._Element, feedback_sid: str) -> bool:
    for p in root.iter("p"):
        if (p.get("type") or "").strip() != "feedback" or p.get("sid") != feedback_sid:
            continue
        parent = p.getparent()
        if parent is None:
            return False
        parent.remove(p)
        prune_empty_section_containers_upward(root, parent)
        return True
    return False


# --- change-set (body-level) ---


def spec_desc_read(root: etree._Element) -> str:
    """Text of the first ``p[@type='desc']`` under ``body`` (change-set description)."""
    de = _desc_p(_body(root))
    return get_text_content(de) if de is not None else ""


def spec_desc_set(root: etree._Element, text: str) -> None:
    """Set or create the change-set description paragraph (after ``h1`` if present)."""
    body = _body(root)
    de = _desc_p(body)
    if de is None:
        existing = ids.collect_xml_ids(root)
        pid = _alloc_id(existing)
        de = etree.Element("p", type="desc", id=pid)
        h1 = body.find("h1")
        if h1 is not None:
            _insert_after(body, h1, de)
        else:
            body.insert(0, de)
    set_text_content(de, text)


def _references_ul_body(body: etree._Element) -> etree._Element | None:
    """The optional ``ul[@type=references]`` direct child of ``body``."""
    for ch in body:
        if ch.tag == "ul" and ch.get("type") == "references":
            return ch
    return None


def migrate_definition_term_attr_to_span(root: etree._Element) -> bool:
    """Legacy definitions stored ``term`` on ``p``; rewrite as ``<span type="term">`` inside the paragraph."""
    changed = False
    for p in root.iter("p"):
        if p.get("type") != "definition":
            continue
        if definition_has_term_span(p):
            if "term" in p.attrib:
                p.attrib.pop("term", None)
                changed = True
            continue
        if "term" not in p.attrib:
            continue
        tm = (p.get("term") or "").strip()
        body = get_text_content(p)
        definition_set_term_and_body(p, tm if tm else None, body)
        changed = True
    return changed


def migrate_legacy_references_div(root: etree._Element) -> bool:
    """If ``body`` still has legacy ``div type=references`` wrapping ``ul type=references``, lift the ``ul``.

    Returns whether the tree was modified.
    """
    body = _body(root)
    changed = False
    for ch in list(body):
        if ch.tag != "div" or ch.get("type") != "references":
            continue
        ul = None
        for kid in ch:
            if kid.tag == "ul" and kid.get("type") == "references":
                ul = kid
                break
        if ul is None:
            continue
        pos = list(body).index(ch)
        ch.remove(ul)
        body.remove(ch)
        body.insert(pos, ul)
        changed = True
    return changed


def _ensure_references_ul(body: etree._Element) -> etree._Element:
    ul = _references_ul_body(body)
    if ul is not None:
        return ul
    ul = etree.Element("ul", type="references")
    _insert_body_block(body, ul, "references")
    return ul


def _iter_ref_links(body: etree._Element):
    """Yield ``a`` elements under ``body/ul[@type=references]``."""
    ul = _references_ul_body(body)
    if ul is None:
        return
    for li in ul:
        if li.tag != "li":
            continue
        for ch in li:
            if ch.tag == "a":
                yield ch


def _find_ref_a(root: etree._Element, ref_id: str) -> etree._Element | None:
    """Resolve ``ref_id`` as entity ``sid`` or DOM fragment ``id`` on a reference ``<a>``."""
    rid = (ref_id or "").strip()
    if not rid:
        return None
    body = _body(root)
    for a in _iter_ref_links(body):
        if (a.get("sid") or "").strip() == rid:
            return a
    from spectr.dom_resolve import find_by_dom_id

    el = find_by_dom_id(root, rid)
    if el is not None and el.tag == "a":
        return el
    return None


def spec_ref_list(root: etree._Element) -> list[tuple[str, str, str]]:
    """Each reference link as ``(sid, href, label_text)`` in document order."""
    out: list[tuple[str, str, str]] = []
    body = _body(root)
    for a in _iter_ref_links(body):
        sid = (a.get("sid") or "").strip()
        href = (a.get("href") or "").strip()
        out.append((sid, href, get_text_content(a).strip()))
    return out


def spec_ref_read(root: etree._Element, ref_id: str) -> tuple[str, str] | None:
    """Return ``(href, label)`` for a reference link, or ``None``."""
    a = _find_ref_a(root, ref_id)
    if a is None:
        return None
    return (a.get("href") or "").strip(), get_text_content(a).strip()


def spec_ref_add(
    root: etree._Element,
    href: str,
    label: str,
    *,
    user_sid: str | None = None,
) -> str:
    """Append a reference link under ``body/ul[@type=references]``. Returns entity ``sid``."""
    u = (href or "").strip()
    if not u:
        raise ValueError("reference href must be non-empty")
    lab = (label or "").strip()
    if not lab:
        raise ValueError("reference label must be non-empty")

    body = _body(root)
    existing = ids.collect_xml_ids(root)
    if user_sid is not None:
        rid = ids.require_unique_override_sid(user_sid, ids.collect_sids(root))
        existing.add(rid)
    else:
        rid = ids.new_prefixed_id(ids.PREFIX_REF, existing)

    ul = _ensure_references_ul(body)
    aid = _alloc_id(existing)
    li = etree.SubElement(ul, "li")
    a = etree.SubElement(li, "a", href=u, sid=rid, id=aid)
    set_text_content(a, lab)

    ids.assert_entity_sid_singleton(root, rid)
    return rid


def spec_ref_delete(root: etree._Element, ref_id: str) -> bool:
    """Remove a reference link by ``sid`` or DOM ``id``. Cleans up empty containers."""
    a = _find_ref_a(root, ref_id)
    if a is None:
        return False
    li = a.getparent()
    if li is None or li.tag != "li":
        return False
    ul = li.getparent()
    if ul is None:
        return False
    ul.remove(li)
    if not len(ul):
        parent = ul.getparent()
        if parent is not None:
            parent.remove(ul)
    return True


# --- export / init ---


def spec_to_markdown(root: etree._Element) -> str:
    body = _body(root)
    lines: list[str] = []
    title_el = root.find("head/title")
    title = get_text_content(title_el).strip() if title_el is not None else ""
    lines.append(f"# {title}".strip() or "# Spec")
    lines.append("")
    lines.append(f"**sid** `{body.get('sid') or ''}`")
    de = _desc_p(body)
    if de is not None and get_text_content(de).strip():
        lines.append("")
        lines.append(get_text_content(de).strip())
    ref_rows = spec_ref_list(root)
    if ref_rows:
        lines.append("")
        lines.append("## References")
        for sid, href, label in ref_rows:
            lines.append(f"- [`{label}`]({href}) · `{sid}`")
    def_rows = def_list_flat(root, include_deprecated=False)
    if def_rows:
        lines.append("")
        lines.append("## Definitions")
        prev_sec: str | None = None
        for sid, sec, tm, prev in def_rows:
            if sec != prev_sec:
                lines.append("")
                lines.append(f"### {sec}")
                prev_sec = sec
            term_part = f" ({tm})" if tm else ""
            lines.append(f"- **{sid}**{term_part} {prev}")
    lines.append("")
    lines.append("## Use cases")
    for sid, tit, preview in uc_list(root):
        lines.append(f"- **{sid}** {tit or ''} — {preview[:80]}")
    lines.append("")
    lines.append("## Business rules")
    for bid, scope, prev in br_list_flat(root, include_deprecated=False):
        lines.append(f"- **{bid}** ({scope}) {prev[:100]}")
    lines.append("")
    lines.append("## Acceptance criteria")
    for aid, scope, prev in ac_list_flat(root, include_deprecated=False):
        lines.append(f"- **{aid}** ({scope}) {prev[:100]}")
    lines.append("")
    lines.append("## Tests")
    tdiv = None
    for ch in body:
        if ch.tag == "div" and ch.get("type") == "tests":
            tdiv = ch
            break
    if tdiv is not None:
        for tp in tdiv.findall("p"):
            if tp.get("type") == "test":
                lines.append(
                    f"- **{tp.get('sid')}** → `{tp.get('ref_id')}` "
                    f"{get_text_content(tp).strip()[:80]}"
                )
    lines.append("")
    lines.append("## Delivery plan")
    from spectr import phase_ops

    plan_rows = phase_ops.plan_iter(root)
    if not plan_rows:
        lines.append("(no phases)")
    else:
        for ph_sid, tasks in plan_rows:
            label = f"`{ph_sid}`" if ph_sid else "(phase without sid)"
            lines.append(f"- Phase {label}")
            if not tasks:
                lines.append("  - _(no tasks yet)_")
            else:
                for tsk_sid, prev in tasks:
                    tid = f"**{tsk_sid}** " if tsk_sid else ""
                    lines.append(f"  - {tid}{prev}".rstrip())
    return "\n".join(lines).strip() + "\n"


def _el_to_json(el: etree._Element) -> dict | list | str:
    kids = list(el)
    if not kids:
        combined = get_text_content(el).strip()
        text = combined if combined else None
    else:
        text = el.text.strip() if el.text and el.text.strip() else None
    tail: dict = {}
    if el.attrib:
        tail["@"] = dict(el.attrib)
    if not kids and text is not None:
        if tail:
            tail["_text"] = text
            return tail
        return text
    if not kids and not text:
        return tail if tail else {}
    out: dict[str, object] = {}
    if text is not None:
        out["_text"] = text
    out.update(tail)
    by_tag: dict[str, list] = {}
    for ch in kids:
        t = etree.QName(ch).localname
        by_tag.setdefault(t, []).append(_el_to_json(ch))
    for t, lst in by_tag.items():
        out[t] = lst[0] if len(lst) == 1 else lst
    return out


def spec_to_json(root: etree._Element) -> str:
    data = {etree.QName(root).localname: _el_to_json(root)}
    return json.dumps(data, indent=2) + "\n"


def write_minimal_spec(
    path: Path, title: str, desc: str, *, user_body_sid: str | None = None
) -> None:
    """Write a new spec: change set title is stored in both ``<head><title>`` and ``<body><h1>``."""
    existing: set[str] = set()
    if user_body_sid is not None:
        body_sid = ids.require_unique_override_sid(user_body_sid, existing)
    else:
        body_sid = ids.new_prefixed_id(ids.PREFIX_SPEC, existing)
    existing.add(body_sid)
    h1_id = _alloc_id(existing)
    p_id = _alloc_id(existing)

    root = etree.Element("html", **{"doc-kind": "spec"})
    head = etree.SubElement(root, "head")
    t_el = etree.SubElement(head, "title")
    set_text_content(t_el, title)
    body = etree.SubElement(root, "body", sid=body_sid)
    h1 = etree.SubElement(body, "h1", id=h1_id)
    set_text_content(h1, title)
    d = etree.SubElement(body, "p", type="desc", id=p_id)
    set_text_content(d, desc)

    from spectr.uow import recompute_dom_ids

    recompute_dom_ids(root)
    write_tree(path, root)
