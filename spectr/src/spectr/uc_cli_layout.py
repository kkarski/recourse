"""Use-case structured markup for the Spectr CLI contract.

``spectr uc add`` and ``spectr uc update`` assemble narrative, trigger, and nested
``div`` containers (``actors``, ``preconditions``, ``postconditions``). Programmatic
callers use :func:`spectr.spec_ops.uc_add` / :func:`spectr.spec_ops.uc_update`,
which delegate here so layout stays in one place.
"""

from __future__ import annotations

from lxml import etree

from spectr import ids
from spectr.xmlio import set_text_content

# Must match narrative collection rules in spec_ops (stop when we hit these <p> types).
UC_LOOSE_NARRATIVE_FORBIDDEN = frozenset(
    {
        "acceptance-criteria",
        "question",
        "answer",
        "feedback",
        "desc",
    }
)


def _alloc_id(existing: set[str]) -> str:
    for _ in range(128):
        c = f"i-{ids.uuid_first_segment()}"
        if c not in existing:
            existing.add(c)
            return c
    raise RuntimeError("could not allocate unique id")


def clear_uc_front_matter(uc_div: etree._Element) -> None:
    """Remove narrative block, trigger, actors, preconditions, postconditions (keep br / ac / questions)."""
    h3 = uc_div.find("h3")
    if h3 is None:
        return
    while True:
        chs = list(uc_div)
        try:
            idx = chs.index(h3) + 1
        except ValueError:
            return
        if idx >= len(chs):
            return
        ch = chs[idx]
        if ch.tag == "p":
            pt = (ch.get("type") or "").strip()
            if pt == "trigger":
                uc_div.remove(ch)
                continue
            if pt in UC_LOOSE_NARRATIVE_FORBIDDEN:
                return
            uc_div.remove(ch)
            continue
        if ch.tag == "div" and (ch.get("type") or "").strip() in (
            "actors",
            "preconditions",
            "postconditions",
        ):
            uc_div.remove(ch)
            continue
        return


def apply_uc_front_matter(
    uc_div: etree._Element,
    existing: set[str],
    *,
    desc: str,
    trigger: str,
    actors: tuple[str, ...],
    preconditions: tuple[str, ...],
    postconditions: tuple[str, ...],
) -> None:
    """Insert narrative ``p`` and optional trigger, actors, pre/post **container** divs after ``h3``."""
    h3 = uc_div.find("h3")
    if h3 is None:
        return
    insert_at = list(uc_div).index(h3) + 1
    nar_id = _alloc_id(existing)
    existing.add(nar_id)
    nar = etree.Element("p", id=nar_id)
    set_text_content(nar, desc)
    uc_div.insert(insert_at, nar)
    insert_at += 1
    tr = (trigger or "").strip()
    if tr:
        tid = _alloc_id(existing)
        existing.add(tid)
        tp = etree.Element("p", type="trigger", id=tid)
        set_text_content(tp, tr)
        uc_div.insert(insert_at, tp)
        insert_at += 1
    act = tuple((s or "").strip() for s in actors if (s or "").strip())
    if act:
        adiv = etree.Element("div", type="actors")
        for a in act:
            aid = _alloc_id(existing)
            existing.add(aid)
            ap = etree.Element("p", type="actor", id=aid)
            set_text_content(ap, a)
            adiv.append(ap)
        uc_div.insert(insert_at, adiv)
        insert_at += 1
    pres = tuple((s or "").strip() for s in preconditions if (s or "").strip())
    if pres:
        prediv = etree.Element("div", type="preconditions")
        for pr in pres:
            pid = _alloc_id(existing)
            existing.add(pid)
            pp = etree.Element("p", type="precondition", id=pid)
            set_text_content(pp, pr)
            prediv.append(pp)
        uc_div.insert(insert_at, prediv)
        insert_at += 1
    posts = tuple((s or "").strip() for s in postconditions if (s or "").strip())
    if posts:
        podiv = etree.Element("div", type="postconditions")
        for po in posts:
            pid = _alloc_id(existing)
            existing.add(pid)
            pp = etree.Element("p", type="postcondition", id=pid)
            set_text_content(pp, po)
            podiv.append(pp)
        uc_div.insert(insert_at, podiv)


def set_uc_front_matter(
    uc_div: etree._Element,
    existing: set[str],
    *,
    desc: str,
    trigger: str,
    actors: tuple[str, ...],
    preconditions: tuple[str, ...],
    postconditions: tuple[str, ...],
) -> None:
    """Replace narrative + structured fields (used by ``uc update``)."""
    clear_uc_front_matter(uc_div)
    apply_uc_front_matter(
        uc_div,
        existing,
        desc=desc,
        trigger=trigger,
        actors=actors,
        preconditions=preconditions,
        postconditions=postconditions,
    )


__all__ = [
    "UC_LOOSE_NARRATIVE_FORBIDDEN",
    "apply_uc_front_matter",
    "clear_uc_front_matter",
    "set_uc_front_matter",
]
