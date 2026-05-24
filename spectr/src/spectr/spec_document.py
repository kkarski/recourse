"""Spec export (Markdown, JSON) and minimal spec file creation.

Kept separate from ``spec_ops`` to avoid a circular import with ``phase_ops``.
"""

from __future__ import annotations

import json
from pathlib import Path

from lxml import etree

from spectr import ids, phase_ops
from spectr import spec_ops
from spectr.spec_tree import body, desc_paragraph
from spectr.uow import recompute_dom_ids
from spectr.xmlio import get_text_content, set_text_content, write_tree


def spec_to_markdown(root: etree._Element) -> str:
    """Build a Markdown outline from the HTML spec (for export/review; canonical spec is HTML)."""
    body_el = body(root)
    lines: list[str] = []
    title_el = root.find("head/title")
    title = get_text_content(title_el).strip() if title_el is not None else ""
    lines.append(f"# {title}".strip() or "# Spec")
    lines.append("")
    lines.append(f"**sid** `{body_el.get('sid') or ''}`")
    de = desc_paragraph(body_el)
    if de is not None and get_text_content(de).strip():
        lines.append("")
        lines.append(get_text_content(de).strip())
    lines.append("")
    lines.append("## Use cases")
    for sid, tit, preview in spec_ops.uc_list(root):
        lines.append(f"- **{sid}** {tit or ''} — {preview[:80]}")
    lines.append("")
    lines.append("## Acceptance criteria")
    for aid, scope, prev in spec_ops.ac_list_flat(root):
        lines.append(f"- **{aid}** ({scope}) {prev[:100]}")
    lines.append("")
    lines.append("## Tests")
    tdiv = None
    for ch in body_el:
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


def write_minimal_spec(path: Path, title: str, desc: str) -> None:
    """Write a new spec: change set title is stored in both ``<head><title>`` and ``<body><h1>``."""
    existing: set[str] = set()
    body_sid = ids.new_prefixed_id(ids.PREFIX_SPEC, existing)
    existing.add(body_sid)
    h1_id = ids.new_dom_fragment_id(existing)
    p_id = ids.new_dom_fragment_id(existing)

    root = etree.Element("html")
    head = etree.SubElement(root, "head")
    t_el = etree.SubElement(head, "title")
    set_text_content(t_el, title)
    body_el = etree.SubElement(root, "body", sid=body_sid)
    h1 = etree.SubElement(body_el, "h1", id=h1_id)
    set_text_content(h1, title)
    d = etree.SubElement(body_el, "p", type="desc", id=p_id)
    set_text_content(d, desc)

    recompute_dom_ids(root)
    write_tree(path, root)
