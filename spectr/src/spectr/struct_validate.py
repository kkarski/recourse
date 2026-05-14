"""Structural rules XSD 1.0 cannot express (body block uniqueness, nested use-case / AC shape)."""

from __future__ import annotations

from lxml import etree

from spectr.xmlio import get_text_content


def _doc_kind(root: etree._Element) -> str:
    kind = (root.get("doc-kind") or "spec").strip()
    if kind not in ("spec", "questions"):
        raise ValueError('html root: doc-kind must be "spec" or "questions"')
    return kind


def _validate_br_div(br_div: etree._Element) -> None:
    seen_questions = False
    for ch in br_div:
        if ch.tag == "p":
            if seen_questions:
                raise ValueError(
                    'business-rules div: <p> cannot follow <div type="questions">'
                )
        elif ch.tag == "div" and ch.get("type") == "questions":
            if seen_questions:
                raise ValueError('business-rules div: at most one <div type="questions">')
            seen_questions = True
        else:
            raise ValueError(
                f'business-rules div may only contain <p> or <div type="questions">, got <{ch.tag}>'
            )


def _validate_actors_div(div: etree._Element) -> None:
    n = 0
    for ch in div:
        if ch.tag != "p":
            raise ValueError(
                f'actors div may only contain <p type="actor">, got <{ch.tag}>'
            )
        if ch.get("type") != "actor":
            raise ValueError('actors div <p> must have type="actor"')
        if not get_text_content(ch).strip():
            raise ValueError('actors div: each <p type="actor"> must have non-empty text')
        n += 1
    if n < 1:
        raise ValueError('actors div requires at least one <p type="actor">')


def _validate_pre_post_div(div: etree._Element, inner_type: str, label: str) -> None:
    n = 0
    for ch in div:
        if ch.tag != "p":
            raise ValueError(f'{label} div may only contain <p type="{inner_type}">, got <{ch.tag}>')
        if ch.get("type") != inner_type:
            raise ValueError(f'{label} div <p> must have type="{inner_type}"')
        if not get_text_content(ch).strip():
            raise ValueError(
                f'{label} div: each <p type="{inner_type}"> must have non-empty text'
            )
        n += 1
    if n < 1:
        raise ValueError(f'{label} div requires at least one <p type="{inner_type}">')


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


def _validate_definition_p(p: etree._Element) -> None:
    """``p`` may be text-only, or a single leading ``<span type="term">`` plus body text."""
    kids = [c for c in p if isinstance(c, etree._Element)]
    if kids:
        if len(kids) > 1:
            raise ValueError(
                'definition <p> may contain at most one <span type="term"> as the only element child'
            )
        sp = kids[0]
        if sp.tag != "span" or (sp.get("type") or "").strip() != "term":
            raise ValueError(
                'definition <p> element children must be <span type="term"> only (optional)'
            )


def _validate_definitions_div(div: etree._Element) -> None:
    for ch in div:
        if ch.tag != "p":
            raise ValueError(
                'definitions div may only contain <p type="definition"> elements'
            )
        if ch.get("type") != "definition":
            raise ValueError(
                'definitions div <p> must have type="definition"'
            )
        _validate_definition_p(ch)


def _validate_references_ul(ul: etree._Element) -> None:
    """``body/ul[@type=references]``: ``li`` children only; each ``li`` holds one ``a[@href]``."""
    if ul.tag != "ul" or ul.get("type") != "references":
        raise ValueError("expected <ul type=\"references\">")
    for li in ul:
        if li.tag != "li":
            raise ValueError("references <ul> may only contain <li> children")
        li_kids = [x for x in li if isinstance(x, etree._Element)]
        if len(li_kids) != 1 or li_kids[0].tag != "a":
            raise ValueError(
                "references: each <li> must contain exactly one <a href=\"…\">"
            )
        a = li_kids[0]
        href = (a.get("href") or "").strip()
        if not href:
            raise ValueError("references: each <a> must have a non-empty href")




def _validate_use_case_div(uc: etree._Element) -> None:
    kids = list(uc)
    if not kids or kids[0].tag != "h3":
        raise ValueError('use-case div must begin with <h3>')
    i = 1
    if i >= len(kids) or kids[i].tag != "p" or kids[i].get("type") == "trigger":
        raise ValueError("use-case div needs at least one narrative <p> after <h3>")
    while i < len(kids) and kids[i].tag == "p" and kids[i].get("type") != "trigger":
        i += 1
    if i >= len(kids) or kids[i].tag != "p" or kids[i].get("type") != "trigger":
        raise ValueError(
            'use-case div requires <p type="trigger"> after narrative paragraph(s)'
        )
    if not get_text_content(kids[i]).strip():
        raise ValueError('use-case <p type="trigger"> must have non-empty text')
    i += 1
    if i < len(kids) and kids[i].tag == "p":
        raise ValueError(
            'use-case div: at most one <p type="trigger"> before nested divs'
        )
    divs: list[tuple[int, str, etree._Element]] = []
    for j in range(i, len(kids)):
        ch = kids[j]
        if ch.tag != "div":
            raise ValueError(
                f"use-case div may only contain h3, p, and div children, got <{ch.tag}>"
            )
        bt = ch.get("type")
        if bt not in (
            "actors",
            "preconditions",
            "postconditions",
            "business-rules",
            "acceptance-criteria",
            "questions",
        ):
            raise ValueError(f"use-case div cannot contain nested div type={bt!r}")
        divs.append((j, bt, ch))
    seen: set[str] = set()
    for _j, bt, _el in divs:
        if bt in seen:
            raise ValueError(f"use-case div allows at most one nested div type={bt!r}")
        seen.add(bt)
    positions = {t: j for j, t, _e in divs}
    for req in ("actors", "preconditions", "postconditions"):
        if req not in positions:
            raise ValueError(
                f'use-case div requires <div type="{req}"> with at least one entry'
            )
    ordered = (
        "actors",
        "preconditions",
        "postconditions",
        "business-rules",
        "acceptance-criteria",
        "questions",
    )
    for ix, a in enumerate(ordered):
        for b in ordered[ix + 1 :]:
            if a in positions and b in positions and positions[a] > positions[b]:
                raise ValueError(
                    f'use-case div: nested <div type="{a}"> must come before '
                    f'<div type="{b}">'
                )
    for _j, bt, el in divs:
        if bt == "actors":
            _validate_actors_div(el)
        elif bt == "preconditions":
            _validate_pre_post_div(el, "precondition", "preconditions")
        elif bt == "postconditions":
            _validate_pre_post_div(el, "postcondition", "postconditions")
        elif bt == "business-rules":
            _validate_br_div(el)
        elif bt == "acceptance-criteria":
            _validate_ac_div(el)


def assert_valid_spec(root: etree._Element) -> None:
    """Raise ``ValueError`` if the tree violates Spectr layout rules."""
    if root.tag != "html":
        return
    kind = _doc_kind(root)
    body = root.find("body")
    if body is None:
        return

    from spectr.spec_ops import _BODY_BLOCK_ORDER

    seen_ref_ul = False
    seen_unique_body_div_types: set[str] = set()
    for ch in body:
        if ch.tag == "h1":
            continue
        if ch.tag == "p" and ch.get("type") == "desc":
            continue
        if ch.tag == "ul":
            if ch.get("type") != "references":
                raise ValueError(
                    f'body may only use <ul type="references"/> at top level; got type={ch.get("type")!r}'
                )
            if seen_ref_ul:
                raise ValueError('at most one <ul type="references"/> is allowed under body')
            seen_ref_ul = True
            _validate_references_ul(ch)
            continue
        if ch.tag != "div":
            raise ValueError(
                f"invalid body child <{ch.tag}>: expected h1, desc p, ul references, or section div"
            )
        bt = ch.get("type")
        if bt is None or bt not in _BODY_BLOCK_ORDER:
            if bt == "tests":
                raise ValueError(
                    'Spectr no longer supports <div type="tests">; remove that section from the specification.'
                )
            raise ValueError(f"unknown or missing body div type={bt!r}")
        if kind == "spec" and bt == "questions":
            raise ValueError('spec document (doc-kind="spec") cannot contain <div type="questions">')
        if bt == "references":
            raise ValueError(
                "obsolete <div type=\"references\"/> removed; use <ul type=\"references\"/> "
                "directly under <body> (open and save with Spectr to migrate legacy specs)"
            )
        if bt != "use-case" and bt in seen_unique_body_div_types:
            raise ValueError(
                f"body div blocks must be unique: duplicate <div type={bt!r}> under <body>"
            )
        if bt != "use-case":
            seen_unique_body_div_types.add(bt)
        if bt == "definitions":
            _validate_definitions_div(ch)
        elif bt == "use-case":
            _validate_use_case_div(ch)
        elif bt == "business-rules":
            _validate_br_div(ch)
        elif bt == "acceptance-criteria":
            _validate_ac_div(ch)

    if kind == "spec":
        for p in root.iter("p"):
            t = (p.get("type") or "").strip()
            if t == "test":
                raise ValueError(
                    'Spectr no longer supports <p type="test">; remove test markup from the specification.'
                )
            if t in ("question", "answer"):
                raise ValueError(
                    f'spec document (doc-kind="spec") cannot contain <p type="{t}">'
                )
