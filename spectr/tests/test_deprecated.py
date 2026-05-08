"""Deprecated flag on UC divs, AC/BR paragraphs, and question threads."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lxml import etree

from spectr import spec_ops
from spectr.uow import SpecUnitOfWork, load_for_read


class TestDeprecatedHelpers(unittest.TestCase):
    def test_element_is_deprecated(self) -> None:
        el = etree.Element("p")
        self.assertFalse(spec_ops.element_is_deprecated(el))
        el.set("deprecated", "true")
        self.assertTrue(spec_ops.element_is_deprecated(el))
        el.set("deprecated", "false")
        self.assertFalse(spec_ops.element_is_deprecated(el))


class TestDeprecatedListFiltering(unittest.TestCase):
    def test_uc_list_excludes_deprecated_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                a = spec_ops.uc_add(
                    root,
                    "keep",
                    "k",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
                b = spec_ops.uc_add(
                    root,
                    "gone",
                    "g",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
                self.assertTrue(spec_ops.uc_deprecate(root, b))
            r = load_for_read(path)
            self.assertEqual(len(spec_ops.uc_list(r)), 1)
            self.assertEqual(spec_ops.uc_list(r)[0][0], a)
            self.assertEqual(len(spec_ops.uc_list(r, include_deprecated=True)), 2)

    def test_br_list_excludes_deprecated_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid_keep = spec_ops.br_add(root, "Users must keep records.", under_uc_id=None)
                sid_dep = spec_ops.br_add(root, "Users may archive records.", under_uc_id=None)
                spec_ops.br_update(root, sid_dep, None, deprecated=True)
            r = load_for_read(path)
            flat = spec_ops.br_list_flat(r, include_deprecated=False)
            sids = [row[0] for row in flat]
            self.assertEqual(sids, [sid_keep])
            flat_all = spec_ops.br_list_flat(r, include_deprecated=True)
            self.assertEqual(len(flat_all), 2)

    def test_ac_list_excludes_deprecated_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                a = spec_ops.ac_add(
                    root,
                    "Given valid data, When submitted, Then it is stored.",
                    under_uc_id=None,
                )
                b = spec_ops.ac_add(
                    root,
                    "Given invalid data, When submitted, Then validation errors are shown.",
                    under_uc_id=None,
                )
                spec_ops.ac_update(root, b, None, deprecated=True)
            r = load_for_read(path)
            self.assertEqual(len(spec_ops.ac_list_flat(r)), 1)
            self.assertEqual(spec_ops.ac_list_flat(r)[0][0], a)
            self.assertEqual(len(spec_ops.ac_list_flat(r, include_deprecated=True)), 2)

    def test_qs_list_excludes_deprecated_question_threads(self) -> None:
        root = etree.fromstring(
            b"<html><head><title>x</title></head><body sid=\"spec-11111111\">"
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="questions"><p type="question" id="3" sid="q-aaaaaaaa">Q1</p>'
            b'<p type="question" id="4" sid="q-bbbbbbbb" deprecated="true">Old</p>'
            b"</div></body></html>"
        )
        rows = spec_ops.qs_list(root, include_deprecated=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "q-aaaaaaaa")
        rows_all = spec_ops.qs_list(root, include_deprecated=True)
        self.assertEqual(len(rows_all), 2)


class TestQsSetDeprecated(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                root.set("doc-kind", "questions")
                qid = spec_ops.qs_ask(root, root.find("body").get("sid"), "why?", author=None, target_role=None)
                self.assertTrue(spec_ops.qs_set_deprecated(root, qid, deprecated=True))
            r = load_for_read(path)
            q = r.find('.//p[@type="question"]')
            assert q is not None
            self.assertEqual(q.get("deprecated"), "true")


if __name__ == "__main__":
    unittest.main()
