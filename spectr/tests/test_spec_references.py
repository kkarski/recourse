"""Top-level ``ul type=references`` external links."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import dom_resolve, spec_ops
from spectr.uow import SpecUnitOfWork, load_for_read


class TestSpecReferences(unittest.TestCase):
    def test_add_list_delete_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spec.html"
            spec_ops.write_minimal_spec(p, "T", "d")
            with SpecUnitOfWork.mutate(p) as root:
                rid = spec_ops.spec_ref_add(
                    root, "https://docs.example.com/a", "Doc A"
                )
                self.assertTrue(rid.startswith("ref-"))
            r = load_for_read(p)
            rows = spec_ops.spec_ref_list(r)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], "https://docs.example.com/a")
            self.assertEqual(rows[0][2], "Doc A")

            with SpecUnitOfWork.mutate(p) as root:
                self.assertTrue(spec_ops.spec_ref_delete(root, rid))
            r3 = load_for_read(p)
            self.assertEqual(spec_ops.spec_ref_list(r3), [])

    def test_export_markdown_includes_references(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spec.html"
            spec_ops.write_minimal_spec(p, "T", "scope text")
            with SpecUnitOfWork.mutate(p) as root:
                spec_ops.spec_ref_add(
                    root,
                    "specs/related.md",
                    "Related spec",
                    user_sid="ref-my-link",
                )
            r = load_for_read(p)
            md = spec_ops.spec_to_markdown(r)
            self.assertIn("## References", md)
            self.assertIn("[`Related spec`](specs/related.md)", md)
            self.assertIn("`ref-my-link`", md)

    def test_ref_sid_from_dom_id(self) -> None:
        from lxml import etree

        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-11111111">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<ul type="references"><li>'
            b'<a href="https://x.test" id="3" sid="ref-aaaaaaaa">L</a>'
            b"</li></ul></body></html>"
        )
        self.assertEqual(dom_resolve.ref_sid_from_dom_id(root, "3"), "ref-aaaaaaaa")

    def test_migrate_legacy_div_wraps_ul(self) -> None:
        from lxml import etree

        from spectr.spec_ops import migrate_legacy_references_div

        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-11111111">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="references"><ul type="references"><li>'
            b'<a href="https://old.wrap" id="3" sid="ref-aaaaaaaa">L</a>'
            b"</li></ul></div></body></html>"
        )
        self.assertTrue(migrate_legacy_references_div(root))
        body = root.find("body")
        self.assertIsNotNone(body)
        uls = [c for c in body if c.tag == "ul" and c.get("type") == "references"]
        self.assertEqual(len(uls), 1)
        self.assertEqual(uls[0].find("li/a").get("href"), "https://old.wrap")
        self.assertEqual(
            [c for c in body if c.tag == "div" and c.get("type") == "references"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
