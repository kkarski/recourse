"""Glossary definitions (body-level ``div type=definitions``)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops, struct_validate
from spectr.uow import SpecUnitOfWork, load_for_read


class TestDefinitions(unittest.TestCase):
    def test_def_add_list_read_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                d1 = spec_ops.def_add(
                    root,
                    "Has an invite.",
                    section="Candidate states",
                    term="Invited",
                )
                d2 = spec_ops.def_add(
                    root,
                    "Started verification.",
                    section="Candidate states",
                    term="Attempted",
                    user_sid="def-custom-one",
                )
            self.assertTrue(d1.startswith("def-"))
            self.assertEqual(d2, "def-custom-one")
            r = load_for_read(path)
            rows = spec_ops.def_list_flat(r)
            self.assertEqual(len(rows), 2)
            struct_validate.assert_valid_spec(r)
            sec, tm, body = spec_ops.def_read(r, d1)
            self.assertEqual(sec, "Candidate states")
            self.assertEqual(tm, "Invited")
            self.assertIn("invite", body)
            raw = path.read_text(encoding="utf-8")
            self.assertIn('<span type="term">Invited</span>', raw)
            self.assertNotIn('term="Invited"', raw)

    def test_spec_to_markdown_includes_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.def_add(root, "Body text.", section="Metrics", term="Ver%")
            r = load_for_read(path)
            md = spec_ops.spec_to_markdown(r)
            self.assertIn("## Definitions", md)
            self.assertIn("### Metrics", md)
            self.assertIn("(Ver%)", md)

    def test_def_delete_removes_empty_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                did = spec_ops.def_add(root, "Only one.", section="S")
                spec_ops.def_delete(root, did)
            r = load_for_read(path)
            div = r.find('.//div[@type="definitions"]')
            self.assertIsNone(div)


if __name__ == "__main__":
    unittest.main()
