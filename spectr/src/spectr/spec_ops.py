from __future__ import annotations

import json
from pathlib import Path

from lxml import etree

from spectr import ids
from spectr.xmlio import get_text_content, set_text_content, write_tree

# Block order for top-level body divs (after h1 and desc).
_BODY_BLOCK_ORDER = ("use-case", "acceptance-criteria", "tests", "questions", "feedback", "plan")


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


def _insert_body_div(body: etree._Element, div: etree._Element, block_type: str) -> None:
    want = _BODY_BLOCK_ORDER.index(block_type)
    insert_at = None
    for i, child in enumerate(body):
        if child.tag != "div":
            continue
        bt = child.get("type")
        if bt in _BODY_BLOCK_ORDER and _BODY_BLOCK_ORDER.index(bt) >= want:
            insert_at = i
            break
    if insert_at is not None:
        body.insert(insert_at, div)
    else:
        body.append(div)


def _ensure_body_block_div(body: etree._Element, block_type: str) -> etree._Element:
    for child in body:
        if child.tag == "div" and child.get("type") == block_type:
            return child
    div = etree.Element("div", type=block_type)
    _insert_body_div(body, div, block_type)
    return div


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
    de = _desc_p(body)
    if de is not None:
        _insert_after(body, de, div)
    else:
        h1 = body.find("h1")
        if h1 is not None:
            _insert_after(body, h1, div)
        else:
            body.append(div)


def _find_uc_div(body: etree._Element, uc_sid: str) -> etree._Element | None:
    for child in body:
        if child.tag == "div" and child.get("type") == "use-case" and child.get("sid") == uc_sid:
            return child
    return None


def _uc_narrative_p(uc_div: etree._Element) -> etree._Element | None:
    for ch in uc_div:
        if ch.tag == "p" and ch.get("type") not in (
            "acceptance-criteria",
            "question",
            "answer",
            "feedback",
            "test",
            "desc",
        ):
            return ch
    return None


def _ensure_uc_ac_div(uc_div: etree._Element) -> etree._Element:
    for ch in uc_div:
        if ch.tag == "div" and ch.get("type") == "acceptance-criteria":
            return ch
    div = etree.Element("div", type="acceptance-criteria")
    h3 = uc_div.find("h3")
    nar = _uc_narrative_p(uc_div)
    if nar is not None:
        idx = list(uc_div).index(nar)
        uc_div.insert(idx + 1, div)
    elif h3 is not None:
        idx = list(uc_div).index(h3)
        uc_div.insert(idx + 1, div)
    else:
        uc_div.insert(0, div)
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


def _ensure_body_questions_div(body: etree._Element) -> etree._Element:
    return _ensure_body_block_div(body, "questions")


def _find_ac_p(root: etree._Element, ac_sid: str) -> etree._Element | None:
    for el in root.iter("p"):
        if el.get("type") == "acceptance-criteria" and el.get("sid") == ac_sid:
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
        cur = parent
    return None


# --- use cases ---


def uc_add(root: etree._Element, title: str, desc: str) -> str:
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    uc_sid = ids.new_prefixed_id(ids.PREFIX_UC, existing)
    ts = ids.iso_now()
    div = etree.Element("div", type="use-case", sid=uc_sid, ts=ts)
    h3_id = _alloc_id(existing)
    p_id = _alloc_id(existing)
    h3 = etree.SubElement(div, "h3", id=h3_id)
    h3.text = title
    p = etree.SubElement(div, "p", id=p_id)
    set_text_content(p, desc)
    _insert_new_use_case(body, div)
    return uc_sid


def uc_list(root: etree._Element) -> list[tuple[str, str | None, str]]:
    body = _body(root)
    out: list[tuple[str, str | None, str]] = []
    for child in body:
        if child.tag != "div" or child.get("type") != "use-case":
            continue
        sid = child.get("sid") or ""
        h3 = child.find("h3")
        tit = (h3.text or "").strip() if h3 is not None and h3.text else ""
        if h3 is not None:
            tit = get_text_content(h3).strip() or tit
        np = _uc_narrative_p(child)
        de = get_text_content(np).strip() if np is not None else ""
        out.append((sid, tit or None, de))
    return out


def uc_read(root: etree._Element, uc_id: str) -> tuple[str | None, str] | None:
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return None
    h3 = uc.find("h3")
    tit = get_text_content(h3).strip() if h3 is not None else None
    np = _uc_narrative_p(uc)
    de = get_text_content(np) if np is not None else ""
    return tit or None, de


def uc_update(root: etree._Element, uc_id: str, title: str | None, desc: str | None) -> bool:
    body = _body(root)
    uc = _find_uc_div(body, uc_id)
    if uc is None:
        return False
    if title is not None:
        h3 = uc.find("h3")
        if h3 is None:
            h3 = etree.SubElement(uc, "h3", id=_alloc_id(ids.collect_xml_ids(root)))
        set_text_content(h3, title)
    if desc is not None:
        np = _uc_narrative_p(uc)
        if np is None:
            existing = ids.collect_xml_ids(root)
            np = etree.SubElement(uc, "p", id=_alloc_id(existing))
        set_text_content(np, desc)
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
) -> str:
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    ac_sid = ids.new_prefixed_id(ids.PREFIX_AC, existing)
    ts = ids.iso_now()
    pid = _alloc_id(existing)
    p = etree.Element("p", type="acceptance-criteria", id=pid, sid=ac_sid, ts=ts)
    set_text_content(p, desc)
    if under_uc_id:
        uc = _find_uc_div(body, under_uc_id)
        if uc is None:
            raise ValueError(f"use case not found: {under_uc_id}")
        ac_div = _ensure_uc_ac_div(uc)
        ac_div.append(p)
    else:
        ac_div = _ensure_body_block_div(body, "acceptance-criteria")
        ac_div.append(p)
    return ac_sid


def ac_list_flat(root: etree._Element) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    body = _body(root)
    for child in body:
        if child.tag == "div" and child.get("type") == "acceptance-criteria":
            for ac in child.findall("p"):
                if ac.get("type") != "acceptance-criteria":
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
                sid = ac.get("sid") or ""
                d = get_text_content(ac).strip()
                out.append((sid, f"uc:{uid}", d[:120]))
    return out


def ac_list_recursive(root: etree._Element) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for scope, sid, _ in ac_list_flat(root):
        rows.append((scope, sid))
    return rows


def ac_read(root: etree._Element, ac_id: str) -> str | None:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return None
    return get_text_content(p)


def ac_update(root: etree._Element, ac_id: str, desc: str) -> bool:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return False
    set_text_content(p, desc)
    p.set("ts", ids.iso_now())
    return True


def ac_delete(root: etree._Element, ac_id: str) -> bool:
    p = _find_ac_p(root, ac_id)
    if p is None:
        return False
    parent = p.getparent()
    if parent is None:
        return False
    parent.remove(p)
    return True


# --- tests (body div type=tests; p type=test) ---


def _ensure_body_tests_div(body: etree._Element) -> etree._Element:
    return _ensure_body_block_div(body, "tests")


def test_add(root: etree._Element, ac_id: str, desc: str) -> str:
    if _find_ac_p(root, ac_id) is None:
        raise ValueError(f"acceptance criterion not found: {ac_id}")
    body = _body(root)
    existing = ids.collect_xml_ids(root)
    tst_sid = ids.new_prefixed_id(ids.PREFIX_TEST, existing)
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
    raise ValueError(f"entity not found for ref_id: {target_id}")


def qs_ask(
    root: etree._Element,
    target_id: str,
    question: str,
    *,
    author: str | None,
    target_role: str | None,
) -> str:
    container = _resolve_qs_container(root, target_id)
    existing = ids.collect_xml_ids(root)
    thread_sid = ids.new_prefixed_id(ids.PREFIX_Q, existing)
    pid = _alloc_id(existing)
    qel = etree.Element("p", type="question", id=pid, sid=thread_sid, ts=ids.iso_now())
    if author:
        qel.set("author", author)
    if target_role:
        qel.set("target", target_role)
    set_text_content(qel, question)
    container.append(qel)
    return thread_sid


def qs_answer(root: etree._Element, thread_id: str, body: str, *, author: str | None) -> bool:
    for q in root.iter("p"):
        if q.get("type") != "question" or q.get("sid") != thread_id:
            continue
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


def qs_list(root: etree._Element) -> list[tuple[str, str | None, str | None, str]]:
    rows: list[tuple[str, str | None, str | None, str]] = []
    for q in root.iter("p"):
        if q.get("type") != "question":
            continue
        sid = q.get("sid")
        if not sid:
            continue
        auth = q.get("author")
        ref = _question_thread_ref(q)
        prev = get_text_content(q)[:80]
        rows.append((sid, ref, auth, prev))
    return rows


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
    lines.append("")
    lines.append("## Use cases")
    for sid, tit, preview in uc_list(root):
        lines.append(f"- **{sid}** {tit or ''} — {preview[:80]}")
    lines.append("")
    lines.append("## Acceptance criteria")
    for aid, scope, prev in ac_list_flat(root):
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


def write_minimal_spec(path: Path, title: str, desc: str) -> None:
    """Write a new spec: change set title is stored in both ``<head><title>`` and ``<body><h1>``."""
    existing: set[str] = set()
    body_sid = ids.new_prefixed_id(ids.PREFIX_SPEC, existing)
    existing.add(body_sid)
    h1_id = _alloc_id(existing)
    p_id = _alloc_id(existing)

    root = etree.Element("html")
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
