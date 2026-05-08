from __future__ import annotations

from pathlib import Path

from lxml import etree


def set_text_content(element: etree._Element, text: str) -> None:
    """Store plain text in *element* (Markdown, code, and XML snippets allowed).

    Removes existing child nodes so the body is a single text node. On write,
    lxml escapes ``<``, ``>``, and ``&`` in that text, so content such as fenced
    code blocks or example XML remains valid in the surrounding document.
    """
    for child in list(element):
        element.remove(child)
    element.text = text


def get_text_content(element: etree._Element | None) -> str:
    """Full text under *element* (decodes XML entities; empty string if *element* is None)."""
    if element is None:
        return ""
    return "".join(element.itertext())


DEF_TERM_SPAN_TYPE = "term"


def _definition_term_span(p: etree._Element) -> etree._Element | None:
    for c in p:
        if isinstance(c, etree._Element) and c.tag == "span" and c.get("type") == DEF_TERM_SPAN_TYPE:
            return c
    return None


def definition_has_term_span(p: etree._Element) -> bool:
    """True if *p* already contains a ``span[@type=term]`` child."""
    return _definition_term_span(p) is not None


def definition_clear_children(p: etree._Element) -> None:
    """Remove all child elements from *p* and clear ``text``/``tail``."""
    for child in list(p):
        p.remove(child)
    p.text = None


def definition_set_term_and_body(p: etree._Element, term: str | None, body: str) -> None:
    """Set glossary content: optional ``<span type="term">…</span>`` then definition body as following text."""
    definition_clear_children(p)
    t = (term or "").strip()
    b = body if body is not None else ""
    if t:
        sp = etree.SubElement(p, "span", type=DEF_TERM_SPAN_TYPE)
        sp.text = t
        sp.tail = b
    else:
        p.text = b
    p.attrib.pop("term", None)


def definition_get_term(p: etree._Element) -> str:
    """Term label from ``span[@type=term]``, else legacy ``term`` attribute."""
    span = _definition_term_span(p)
    if span is not None:
        return (span.text or "").strip()
    return (p.get("term") or "").strip()


def definition_get_body(p: etree._Element) -> str:
    """Definition body text (excluding the term span)."""
    span = _definition_term_span(p)
    if span is not None:
        parts: list[str] = [span.tail or ""]
        seen = False
        for child in p:
            if child is span:
                seen = True
                continue
            if seen:
                parts.append("".join(child.itertext()))
        return "".join(parts).strip()
    return get_text_content(p).strip()


def load_tree(path: Path) -> etree._Element:
    p = Path(path)
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(p), parser)
    return tree.getroot()


def write_tree(path: Path, root: etree._Element) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tree = etree.ElementTree(root)
    tree.write(
        str(p),
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True,
    )


def ensure_child(parent: etree._Element, tag: str) -> etree._Element:
    child = parent.find(tag)
    if child is None:
        child = etree.SubElement(parent, tag)
    return child


def find_by_id(root: etree._Element, tag: str, eid: str) -> etree._Element | None:
    for el in root.iter(tag):
        if el.get("id") == eid:
            return el
    return None


def find_any_by_id(root: etree._Element, eid: str) -> tuple[etree._Element, str] | None:
    for el in root.iter():
        if el.get("id") == eid:
            return el, etree.QName(el).localname
    return None
