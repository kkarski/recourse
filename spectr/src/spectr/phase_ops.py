from __future__ import annotations

from lxml import etree

from spectr import ids
from spectr.spec_ops import _body, _ensure_body_block_div
from spectr.xmlio import set_text_content


def _plan_div(body_el: etree._Element) -> etree._Element:
    return _ensure_body_block_div(body_el, "plan")


def _iter_phases(plan: etree._Element) -> list[etree._Element]:
    return [ch for ch in plan if ch.tag == "ol" and ch.get("type") == "phase"]


def _resolve_phase_ol(plan: etree._Element, phase_sid: str | None) -> etree._Element:
    phases = _iter_phases(plan)
    if phase_sid is not None:
        for ol in phases:
            if ol.get("sid") == phase_sid:
                return ol
        raise ValueError(f"plan phase not found: {phase_sid}")
    if phases:
        return phases[-1]
    raise ValueError("no plan phase; run plan phase-add first")


def phase_add(root: etree._Element, *, phase_sid: str | None = None) -> str:
    body_el = _body(root)
    plan = _plan_div(body_el)
    existing = ids.collect_xml_ids(root)
    if phase_sid is not None:
        sid = phase_sid
        if sid in existing:
            raise ValueError(f"phase sid already exists: {sid}")
    else:
        sid = ids.new_prefixed_id(ids.PREFIX_PHASE, existing)
    ol = etree.Element("ol", type="phase", sid=sid)
    plan.append(ol)
    return sid


def task_add(
    root: etree._Element,
    text: str,
    *,
    phase_sid: str | None = None,
) -> str:
    body_el = _body(root)
    plan = _plan_div(body_el)
    ol = _resolve_phase_ol(plan, phase_sid)
    existing = ids.collect_xml_ids(root)
    task_sid = ids.new_prefixed_id(ids.PREFIX_TASK, existing)
    tmp_id = f"w-{ids.uuid_first_segment()}"
    li = etree.SubElement(ol, "li", type="task", id=tmp_id, sid=task_sid)
    set_text_content(li, text)
    return task_sid
