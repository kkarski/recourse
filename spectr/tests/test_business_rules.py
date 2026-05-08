"""Business rule CRUD."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops
from spectr.uow import SpecUnitOfWork, load_for_read


class TestBusinessRules(unittest.TestCase):
    def test_add_read_body_level_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.br_add(root, "Users must complete step Y after X.", under_uc_id=None)
            r = load_for_read(path)
            self.assertEqual(spec_ops.br_read(r, sid), "Users must complete step Y after X.")

    def test_list_flat_after_add(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.br_add(root, "Users may edit profile settings.", under_uc_id=None)
            r = load_for_read(path)
            rows = spec_ops.br_list_flat(r)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], sid)
            self.assertEqual(rows[0][1], "spec")

    def test_delete_last_br_prunes_empty_body_business_rules_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.br_add(root, "Users must keep one rule.", under_uc_id=None)
                spec_ops.br_delete(root, sid)
            r = load_for_read(path)
            body = r.find("body")
            assert body is not None
            br_divs = [
                ch
                for ch in body
                if ch.tag == "div" and ch.get("type") == "business-rules"
            ]
            self.assertEqual(br_divs, [])

    def test_delete_last_ac_prunes_empty_body_acceptance_criteria_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.ac_add(
                    root,
                    "Given one AC, When evaluated, Then it passes.",
                    under_uc_id=None,
                )
                spec_ops.ac_delete(root, sid)
            r = load_for_read(path)
            body = r.find("body")
            assert body is not None
            ac_divs = [
                ch
                for ch in body
                if ch.tag == "div" and ch.get("type") == "acceptance-criteria"
            ]
            self.assertEqual(ac_divs, [])

    def test_delete_last_test_prunes_empty_tests_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                ac = spec_ops.ac_add(
                    root,
                    "Given an account, When the user logs in, Then the dashboard is shown.",
                    under_uc_id=None,
                )
                tid = spec_ops.test_add(root, ac, "check")
                spec_ops.test_delete(root, tid)
            r = load_for_read(path)
            body = r.find("body")
            assert body is not None
            tdivs = [
                ch
                for ch in body
                if ch.tag == "div" and ch.get("type") == "tests"
            ]
            self.assertEqual(tdivs, [])

    def test_delete_last_br_under_use_case_prunes_nested_business_rules_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                uc = spec_ops.uc_add(
                    root,
                    "UC",
                    "narrative",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
                sid = spec_ops.br_add(root, "Users may add rules under UC.", under_uc_id=uc)
                spec_ops.br_delete(root, sid)
            r = load_for_read(path)
            body = r.find("body")
            assert body is not None
            uc_div = next(
                ch
                for ch in body
                if ch.tag == "div"
                and ch.get("type") == "use-case"
                and ch.get("sid") == uc
            )
            br_divs = [
                ch
                for ch in uc_div
                if ch.tag == "div" and ch.get("type") == "business-rules"
            ]
            self.assertEqual(br_divs, [])


if __name__ == "__main__":
    unittest.main()
