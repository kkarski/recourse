"""Content constraints are enforced on add/update mutations."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops
from spectr.uow import SpecUnitOfWork


class TestContentConstraints(unittest.TestCase):
    def test_definition_add_rejects_term_longer_than_100(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.def_add(
                        root,
                        "Meaning.",
                        section="S",
                        term="T" * 101,
                    )

    def test_definition_add_rejects_body_longer_than_500(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.def_add(
                        root,
                        "D" * 501,
                        section="S",
                        term="Term",
                    )

    def test_definition_update_rejects_body_longer_than_500(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                did = spec_ops.def_add(root, "Meaning.", section="S", term="Term")
                with self.assertRaises(ValueError):
                    spec_ops.def_update(root, did, desc="D" * 501)

    def test_ac_add_rejects_missing_given_when_then_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.ac_add(
                        root,
                        "Then outcome. Given context. When action.",
                        under_uc_id=None,
                    )

    def test_ac_update_rejects_missing_given_when_then_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                ac = spec_ops.ac_add(
                    root,
                    "Given context, When action, Then outcome.",
                    under_uc_id=None,
                )
                with self.assertRaises(ValueError):
                    spec_ops.ac_update(root, ac, "Given one. Given two. When action. Then outcome.")

    def test_ac_update_multiple_given_reports_split_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                ac = spec_ops.ac_add(
                    root,
                    "Given context, When action, Then outcome.",
                    under_uc_id=None,
                )
                with self.assertRaises(ValueError) as ctx:
                    spec_ops.ac_update(
                        root,
                        ac,
                        "Given one, When first action, Then first outcome. "
                        "Given two, When second action, Then second outcome.",
                    )
                self.assertIn("split this text into 2 ACs", str(ctx.exception))

    def test_br_add_rejects_missing_normative_keyword(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.br_add(root, "Users sign in with email.", under_uc_id=None)

    def test_br_update_rejects_missing_normative_keyword(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                br = spec_ops.br_add(root, "Users must sign in.", under_uc_id=None)
                with self.assertRaises(ValueError):
                    spec_ops.br_update(root, br, "Users sign in with email.")


if __name__ == "__main__":
    unittest.main()
