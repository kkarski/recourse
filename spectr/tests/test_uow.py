"""Unit of work and DOM id normalization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lxml import etree

from spectr import spec_ops, xmlio
from spectr import ids
from spectr.uow import SpecUnitOfWork, clone_tree, ensure_missing_entity_sids, load_for_read, recompute_dom_ids


class TestEnsureMissingEntitySidsStable(unittest.TestCase):
    def test_preserves_existing_non_canonical_sid(self) -> None:
        root = etree.fromstring(
            b"<html><head><title>x</title></head><body sid=\"spec-legacy\">"
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p></body></html>'
        )
        self.assertFalse(ensure_missing_entity_sids(root))
        self.assertEqual(root.find("body").get("sid"), "spec-legacy")


class TestCanonicalSid(unittest.TestCase):
    def test_is_canonical_sid(self) -> None:
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_UC, "uc-a1b2c3d4"))
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_Q, "q-00000000"))
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_TEST, "tst-deadbeef"))
        self.assertFalse(ids.is_canonical_sid(ids.PREFIX_UC, "uc-short"))
        self.assertFalse(ids.is_canonical_sid(ids.PREFIX_UC, "wrong-a1b2c3d4"))
        self.assertFalse(ids.is_canonical_sid(ids.PREFIX_UC, ""))


class TestRecomputeDomIds(unittest.TestCase):
    def test_sequential_ids_in_document_order(self) -> None:
        root = etree.fromstring(
            b"<html><head><title>t</title></head><body sid=\"spec-x\">"
            b'<h1 id="old">T</h1><p type="desc" id="x">d</p></body></html>'
        )
        recompute_dom_ids(root)
        h1 = root.find("body/h1")
        p = root.find("body/p")
        assert h1 is not None and p is not None
        self.assertEqual(h1.get("id"), "1")
        self.assertEqual(p.get("id"), "2")
        self.assertEqual(root.find("body").get("sid"), "spec-x")

    def test_task_li_gets_sequential_id_preserves_sid(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="s">'
            b'<h1 id="a">H</h1><p type="desc" id="b">D</p>'
            b'<div type="plan"><ol type="phase" sid="ph-11111111">'
            b'<li type="task" id="w-old" sid="tsk-22222222">t</li></ol></div>'
            b"</body></html>"
        )
        recompute_dom_ids(root)
        li = root.find(".//li[@type='task']")
        assert li is not None
        self.assertEqual(li.get("sid"), "tsk-22222222")
        self.assertEqual(li.get("id"), "3")


class TestSpecUnitOfWork(unittest.TestCase):
    def test_commit_writes_normalized_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.uc_add(root, "U", "u")
            root2 = xmlio.load_tree(path)
            h1 = root2.find("body/h1")
            assert h1 is not None
            self.assertEqual(h1.get("id"), "1")

    def test_rollback_leaves_file_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            before = path.read_bytes()
            try:
                with SpecUnitOfWork.mutate(path) as root:
                    spec_ops.uc_add(root, "U", "u")
                    raise RuntimeError("abort")
            except RuntimeError:
                pass
            self.assertEqual(path.read_bytes(), before)

    def test_ensure_missing_entity_sids_fills_body_phase_task(self) -> None:
        root = etree.fromstring(
            b"<html><head><title>x</title></head><body>"
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="plan"><ol type="phase">'
            b'<li type="task" id="w1">one</li></ol></div></body></html>'
        )
        self.assertIsNone(root.find("body").get("sid"))
        ol = root.find(".//ol[@type='phase']")
        assert ol is not None
        self.assertIsNone(ol.get("sid"))
        li = root.find(".//li[@type='task']")
        assert li is not None
        self.assertIsNone(li.get("sid"))
        self.assertTrue(ensure_missing_entity_sids(root))
        bsid = root.find("body").get("sid")
        assert bsid is not None
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_SPEC, bsid))
        psid = ol.get("sid")
        assert psid is not None
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_PHASE, psid))
        tsid = li.get("sid")
        assert tsid is not None
        self.assertTrue(ids.is_canonical_sid(ids.PREFIX_TASK, tsid))

    def test_load_for_read_normalizes_before_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            root = etree.fromstring(
                b"<html><head><title>x</title></head><body sid=\"spec-z\">"
                b'<h1 id="z9">T</h1><p type="desc" id="z8">d</p></body></html>'
            )
            xmlio.write_tree(path, root)
            load_for_read(path)
            raw = path.read_text(encoding="utf-8")
            self.assertIn('id="1"', raw)
            self.assertIn('id="2"', raw)


class TestCloneTree(unittest.TestCase):
    def test_clone_is_independent(self) -> None:
        root = etree.fromstring(b"<html><body sid=\"s\"><h1 id=\"1\">x</h1></body></html>")
        c = clone_tree(root)
        h = root.find(".//h1")
        assert h is not None
        h.set("id", "99")
        assert c.find(".//h1") is not None
        self.assertEqual(c.find(".//h1").get("id"), "1")


if __name__ == "__main__":
    unittest.main()
