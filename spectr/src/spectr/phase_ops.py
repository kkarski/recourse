from __future__ import annotations

from lxml import etree

from spectr import ids
from spectr.spec_ops import _body, _ensure_body_block_div
from spectr.xmlio import get_text_content, set_text_content


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
    raise ValueError("no plan phase; run spectr task add (optional --ph) to create one")


def phase_add(root: etree._Element) -> str:
    """Append a phase list with an auto ``ph-{uuid8}`` sid (never caller-assigned)."""
    body_el = _body(root)
    plan = _plan_div(body_el)
    existing = ids.collect_xml_ids(root)
    sid = ids.new_prefixed_id(ids.PREFIX_PHASE, existing)
    ol = etree.Element("ol", type="phase", sid=sid)
    plan.append(ol)
    return sid


def plan_iter(
    root: etree._Element,
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Phases under ``div[@type=plan]``: ``(phase_sid or '', [(task_sid, preview), ...])`` per phase in document order."""
    body_el = _body(root)
    plan_div: etree._Element | None = None
    for ch in body_el:
        if ch.tag == "div" and ch.get("type") == "plan":
            plan_div = ch
            break
    if plan_div is None:
        return []
    out: list[tuple[str, list[tuple[str, str]]]] = []
    for ch in plan_div:
        if ch.tag != "ol" or ch.get("type") != "phase":
            continue
        ph_sid = (ch.get("sid") or "").strip()
        tasks: list[tuple[str, str]] = []
        for li in ch:
            if li.tag != "li" or li.get("type") != "task":
                continue
            tsk_sid = (li.get("sid") or "").strip()
            text = get_text_content(li).strip()
            preview = text[:120] if text else ""
            tasks.append((tsk_sid, preview))
        out.append((ph_sid, tasks))
    return out


def task_list(
    root: etree._Element,
    *,
    phase_sid: str | None = None,
) -> list[tuple[str, str, str]]:
    """Tasks in document order: ``(phase_sid, task_sid, preview)``.

    If ``phase_sid`` is set, only tasks under the matching phase ``ol`` (exact ``sid`` match).
    """
    want = str(phase_sid).strip() if phase_sid is not None and str(phase_sid).strip() else None
    out: list[tuple[str, str, str]] = []
    for ph_sid, tasks in plan_iter(root):
        if want is not None and ph_sid != want:
            continue
        for tsk_sid, prev in tasks:
            out.append((ph_sid, tsk_sid, prev))
    return out


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


def task_add_auto(
    root: etree._Element,
    text: str,
    *,
    phase_sid: str | None = None,
) -> str:
    """Ensure ``div type=plan`` and a target ``ol type=phase`` exist, then append a task (CLI default).

    * With ``phase_sid``: if a phase with that ``sid`` exists, append there; otherwise create a new phase (auto ``ph-…`` sid) and append there.
    * Without ``phase_sid``: if there are no phases yet, create one with an auto ``ph-…`` sid; else append to the last phase.
    """
    body_el = _body(root)
    plan = _plan_div(body_el)
    phases = _iter_phases(plan)
    want = str(phase_sid).strip() if phase_sid is not None and str(phase_sid).strip() else None

    if want:
        for p in phases:
            if p.get("sid") == want:
                return task_add(root, text, phase_sid=want)
        ph = phase_add(root)
        return task_add(root, text, phase_sid=ph)

    if not phases:
        ph = phase_add(root)
        return task_add(root, text, phase_sid=ph)

    return task_add(root, text, phase_sid=None)
