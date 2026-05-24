"""Shared HTML tree navigation for Spectr specs (body blocks, description paragraph).

Used by ``spec_ops``, ``phase_ops``, and ``dom_resolve`` so they do not import each other's
internals.
"""

from __future__ import annotations

from lxml import etree

from spectr.spec_xml_model import BODY_BLOCK_ORDER


def body(root: etree._Element) -> etree._Element:
    if root.tag != "html":
        raise ValueError("expected <html> root")
    b = root.find("body")
    if b is None:
        raise ValueError("expected <body>")
    return b


def desc_paragraph(body_el: etree._Element) -> etree._Element | None:
    """First ``p[@type='desc']`` directly under *body_el*."""
    for child in body_el:
        if child.tag == "p" and child.get("type") == "desc":
            return child
    return None


def _insert_body_div(body_el: etree._Element, div: etree._Element, block_type: str) -> None:
    want = BODY_BLOCK_ORDER.index(block_type)
    insert_at = None
    for i, child in enumerate(body_el):
        if child.tag != "div":
            continue
        bt = child.get("type")
        if bt in BODY_BLOCK_ORDER and BODY_BLOCK_ORDER.index(bt) >= want:
            insert_at = i
            break
    if insert_at is not None:
        body_el.insert(insert_at, div)
    else:
        body_el.append(div)


def ensure_body_block_div(body_el: etree._Element, block_type: str) -> etree._Element:
    for child in body_el:
        if child.tag == "div" and child.get("type") == block_type:
            return child
    div = etree.Element("div", type=block_type)
    _insert_body_div(body_el, div, block_type)
    return div
