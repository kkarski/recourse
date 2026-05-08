"""Round-trip and escaping for Markdown-like text in Spectr HTML specs."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lxml import etree

from spectr import spec_ops, xmlio

MARKDOWN_WITH_XML = """## Notes

Use `<request>` and compare:

```xml
<root attr="1"/>
```

Also: 2 < 3 and AT&T.
"""


class TestXmlTextContent(unittest.TestCase):
    def test_set_get_roundtrip_preserves_markdown(self) -> None:
        el = etree.Element("p")
        xmlio.set_text_content(el, MARKDOWN_WITH_XML)
        self.assertEqual(xmlio.get_text_content(el), MARKDOWN_WITH_XML)

    def test_write_file_escapes_markup_then_reads_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            root = etree.Element("html")
            head = etree.SubElement(root, "head")
            t = etree.SubElement(head, "title")
            xmlio.set_text_content(t, "T")
            body = etree.SubElement(root, "body", sid="spec-88888888")
            h1 = etree.SubElement(body, "h1", id="h1")
            h1.text = "T"
            d = etree.SubElement(body, "p", type="desc", id="d1")
            xmlio.set_text_content(d, MARKDOWN_WITH_XML)
            xmlio.write_tree(path, root)
            raw = path.read_text(encoding="utf-8")
            self.assertIn("&lt;request&gt;", raw)
            self.assertIn("&lt;root", raw)
            self.assertIn("2 &lt; 3", raw)
            self.assertIn("AT&amp;T", raw)

            root2 = xmlio.load_tree(path)
            de = root2.find("body/p[@type='desc']")
            got = xmlio.get_text_content(de)
            self.assertEqual(got, MARKDOWN_WITH_XML)

    def test_uc_update_clears_stale_child_nodes(self) -> None:
        root = etree.fromstring(
            '<html><head><title>x</title></head><body sid="spec-99999999">'
            '<h1 id="h">x</h1><p type="desc" id="d">d</p>'
            '<div type="use-case" sid="uc-aaaaaaaa" ts="">'
            "<h3 id=\"t\">t</h3>"
            '<p id="n">old<b>bad</b></p></div></body></html>'
        )
        spec_ops.uc_update(
            root,
            "uc-aaaaaaaa",
            title="t",
            desc="only plain text now",
            trigger="tr",
            actors=("Actor",),
            preconditions=("pre",),
            postconditions=("post",),
        )
        row = spec_ops.uc_read(root, "uc-aaaaaaaa")
        assert row is not None
        self.assertEqual(row.desc, "only plain text now")


if __name__ == "__main__":
    unittest.main()
