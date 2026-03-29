"""Structural rules XSD 1.0 cannot express (body div block order, nested use-case / AC shape)."""

from __future__ import annotations

from lxml import etree


def _validate_ac_div(ac_div: etree._Element) -> None:
    seen_questions = False
    for ch in ac_div:
        if ch.tag == "p":
            if seen_questions:
                raise ValueError(
                    'acceptance-criteria div: <p> cannot follow <div type="questions">'
                )
        elif ch.tag == "div" and ch.get("type") == "questions":
            if seen_questions:
                raise ValueError('acceptance-criteria div: at most one <div type="questions">')
            seen_questions = True
        else:
            raise ValueError(
                f'acceptance-criteria div may only contain <p> or <div type="questions">, got <{ch.tag}>'
            )


def _validate_use_case_div(uc: etree._Element) -> None:
    kids = list(uc)
    if not kids or kids[0].tag != "h3":
        raise ValueError('use-case div must begin with <h3>')
    i = 1
    while i < len(kids) and kids[i].tag == "p":
        i += 1
    if i < 2:
        raise ValueError("use-case div needs at least one narrative <p> after <h3>")
    divs: list[tuple[int, str, etree._Element]] = []
    for j in range(i, len(kids)):
        ch = kids[j]
        if ch.tag != "div":
            raise ValueError(
                f"use-case div may only contain h3, p, and div children, got <{ch.tag}>"
            )
        bt = ch.get("type")
        if bt not in ("acceptance-criteria", "questions"):
            raise ValueError(f"use-case div cannot contain nested div type={bt!r}")
        divs.append((j, bt, ch))
    seen: set[str] = set()
    for _j, bt, _el in divs:
        if bt in seen:
            raise ValueError(f"use-case div allows at most one nested div type={bt!r}")
        seen.add(bt)
    if "acceptance-criteria" in seen and "questions" in seen:
        ac_pos = next(j for j, t, _e in divs if t == "acceptance-criteria")
        q_pos = next(j for j, t, _e in divs if t == "questions")
        if ac_pos > q_pos:
            raise ValueError(
                'use-case div: nested <div type="acceptance-criteria"> must come before '
                '<div type="questions">'
            )
    for _j, bt, el in divs:
        if bt == "acceptance-criteria":
            _validate_ac_div(el)


def assert_valid_spec(root: etree._Element) -> None:
    """Raise ``ValueError`` if the tree violates Spectr layout rules."""
    if root.tag != "html":
        return
    body = root.find("body")
    if body is None:
        return

    from spectr.spec_ops import _BODY_BLOCK_ORDER

    prev_idx = -1
    for ch in body:
        if ch.tag != "div":
            continue
        bt = ch.get("type")
        if bt is None or bt not in _BODY_BLOCK_ORDER:
            raise ValueError(f"unknown or missing body div type={bt!r}")
        idx = _BODY_BLOCK_ORDER.index(bt)
        if idx < prev_idx:
            raise ValueError(
                f"body div blocks out of order: <div type={bt!r}> cannot appear after a "
                f"later section (expected order: {' → '.join(_BODY_BLOCK_ORDER)})"
            )
        prev_idx = idx
        if bt == "use-case":
            _validate_use_case_div(ch)
        elif bt == "acceptance-criteria":
            _validate_ac_div(ch)
