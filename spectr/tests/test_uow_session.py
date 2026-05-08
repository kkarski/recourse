"""CLI-style multi-command unit of work (draft under .spectr/)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops, uow_session, xmlio
from spectr.uow import SpecUnitOfWork


class TestUowSession(unittest.TestCase):
    def test_begin_commit_leaves_original_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(spec, "T", "d")
            uow_session.begin(spec)
            draft = uow_session.resolve_working_spec_path(spec)
            self.assertTrue(draft.is_file())
            self.assertNotEqual(draft.resolve(), spec.resolve())
            with SpecUnitOfWork.mutate(draft) as root:
                spec_ops.uc_add(
                    root,
                    "U",
                    "u",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            root_check = xmlio.load_tree(spec)
            body = root_check.find("body")
            assert body is not None
            uc_divs = [c for c in body if c.tag == "div" and c.get("type") == "use-case"]
            self.assertEqual(len(uc_divs), 0)
            dr = xmlio.load_tree(draft)
            body_d = dr.find("body")
            assert body_d is not None
            uc_d = [c for c in body_d if c.tag == "div" and c.get("type") == "use-case"]
            self.assertEqual(len(uc_d), 1)
            uow_session.commit(spec)
            self.assertFalse(draft.is_file())
            root_final = xmlio.load_tree(spec)
            body_f = root_final.find("body")
            assert body_f is not None
            uc_f = [c for c in body_f if c.tag == "div" and c.get("type") == "use-case"]
            self.assertEqual(len(uc_f), 1)

    def test_abort_discards_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(spec, "T", "d")
            uow_session.begin(spec)
            draft = uow_session.resolve_working_spec_path(spec)
            with SpecUnitOfWork.mutate(draft) as root:
                spec_ops.uc_add(
                    root,
                    "U",
                    "u",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            uow_session.abort(spec)
            self.assertFalse(uow_session.is_active(spec))
            root = xmlio.load_tree(spec)
            body = root.find("body")
            assert body is not None
            uc_f = [c for c in body if c.tag == "div" and c.get("type") == "use-case"]
            self.assertEqual(len(uc_f), 0)


if __name__ == "__main__":
    unittest.main()
