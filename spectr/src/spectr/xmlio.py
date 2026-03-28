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
