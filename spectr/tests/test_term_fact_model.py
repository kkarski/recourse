"""Body-level term-fact-model (Mermaid erDiagram)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops, struct_validate
from spectr.uow import SpecUnitOfWork, load_for_read

_SAMPLE_ER = """erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains"""


class TestTermFactModel(unittest.TestCase):
    def test_tfm_add_read_update_delete_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                tid = spec_ops.tfm_add(root, _SAMPLE_ER, user_sid="tfm-custom")
            self.assertEqual(tid, "tfm-custom")
            r = load_for_read(path)
            struct_validate.assert_valid_spec(r)
            row = spec_ops.tfm_read(r)
            assert row is not None
            self.assertEqual(row[0], "tfm-custom")
            self.assertIn("CUSTOMER", row[1])
            raw = path.read_text(encoding="utf-8")
            self.assertIn('type="term-fact-model"', raw)
            self.assertIn('diagram="term-fact-model"', raw)
            with SpecUnitOfWork.mutate(path) as root2:
                updated = """erDiagram
    ACCOUNT ||--|| CUSTOMER : belongs_to"""
                out = spec_ops.tfm_update(root2, updated)
            self.assertEqual(out, "tfm-custom")
            r2 = load_for_read(path)
            self.assertIn("ACCOUNT", spec_ops.tfm_read(r2)[1])
            with SpecUnitOfWork.mutate(path) as root3:
                self.assertTrue(spec_ops.tfm_delete(root3, "tfm-custom"))
            r3 = load_for_read(path)
            self.assertIsNone(r3.find('.//div[@type="term-fact-model"]'))

    def test_tfm_add_rejects_duplicate_and_invalid_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.tfm_add(root, _SAMPLE_ER)
                with self.assertRaises(ValueError):
                    spec_ops.tfm_add(root, _SAMPLE_ER)
                with self.assertRaises(ValueError):
                    spec_ops.tfm_add(root, "not an er diagram")

    def test_tfm_after_definitions_before_use_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.def_add(root, "Body.", section="S", term="T")
                spec_ops.tfm_add(root, _SAMPLE_ER)
                spec_ops.uc_add(
                    root,
                    "UC",
                    "narrative",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            r = load_for_read(path)
            struct_validate.assert_valid_spec(r)
            body = r.find("body")
            assert body is not None
            kinds: list[str | None] = []
            for ch in body:
                if ch.tag == "h1" or (ch.tag == "p" and ch.get("type") == "desc"):
                    continue
                if ch.tag == "div":
                    kinds.append((ch.get("type") or "").strip())
            self.assertEqual(
                kinds,
                ["definitions", "term-fact-model", "use-case"],
            )

    def test_spec_to_markdown_includes_term_fact_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.tfm_add(root, _SAMPLE_ER)
            md = spec_ops.spec_to_markdown(load_for_read(path))
            self.assertIn("## Term fact model", md)
            self.assertIn("erDiagram", md)


if __name__ == "__main__":
    unittest.main()
