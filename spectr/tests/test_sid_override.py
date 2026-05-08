"""Optional entity ``sid`` at add time for uc/ac/br/q threads (CLI passes user_sid)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops
from spectr.uow import SpecUnitOfWork, load_for_read


class TestSidOverrides(unittest.TestCase):
    def test_uc_add_user_sid_freeform_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.uc_add(
                    root,
                    "UC",
                    "body",
                    user_sid="uc-exports-feature",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            self.assertEqual(sid, "uc-exports-feature")
            r = load_for_read(path)
            u = spec_ops.uc_read(r, "uc-exports-feature")
            assert u is not None
            self.assertEqual(u.title, "UC")
            self.assertEqual(u.desc.strip(), "body")

    def test_uc_add_user_sid_empty_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.uc_add(
                        root,
                        "UC",
                        "body",
                        user_sid="",
                        trigger="t",
                        actors=("a",),
                        preconditions=("p",),
                        postconditions=("o",),
                    )

    def test_uc_add_user_sid_and_duplicate_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.uc_add(
                    root,
                    "UC",
                    "body",
                    user_sid="uc-aaaaaaaa",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            self.assertEqual(sid, "uc-aaaaaaaa")
            r = load_for_read(path)
            u = spec_ops.uc_read(r, "uc-aaaaaaaa")
            assert u is not None
            self.assertEqual(u.title, "UC")
            self.assertEqual(u.desc.strip(), "body")
            with SpecUnitOfWork.mutate(path) as root:
                with self.assertRaises(ValueError):
                    spec_ops.uc_add(
                        root,
                        "U2",
                        "b2",
                        user_sid="uc-aaaaaaaa",
                        trigger="t2",
                        actors=("b",),
                        preconditions=("q",),
                        postconditions=("r",),
                    )

    def test_br_add_user_sid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.br_add(
                    root, "Users must accept terms.", under_uc_id=None, user_sid="br-11111111"
                )
            self.assertEqual(sid, "br-11111111")
            r = load_for_read(path)
            self.assertEqual(spec_ops.br_read(r, "br-11111111"), "Users must accept terms.")

    def test_br_add_duplicate_user_sid_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.br_add(root, "Users must enroll.", under_uc_id=None, user_sid="br-aaaaaaaa")
                with self.assertRaises(ValueError):
                    spec_ops.br_add(root, "Users may unenroll.", under_uc_id=None, user_sid="br-aaaaaaaa")

    def test_ac_add_user_sid_and_duplicate_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.ac_add(
                    root,
                    "Given a request, When accepted, Then status is active.",
                    under_uc_id=None,
                    user_sid="ac-aaaaaaaa",
                )
                with self.assertRaises(ValueError):
                    spec_ops.ac_add(
                        root,
                        "Given a request, When rejected, Then status is declined.",
                        under_uc_id=None,
                        user_sid="ac-aaaaaaaa",
                    )

    def test_ac_add_user_sid_unprefixed_external_label(self) -> None:
        """Acceptance criteria may use the same token as external docs (e.g. AC5) as sid."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                sid = spec_ops.ac_add(
                    root,
                    "Given criterion input, When evaluated, Then criterion passes.",
                    under_uc_id=None,
                    user_sid="AC5",
                )
            self.assertEqual(sid, "AC5")
            r = load_for_read(path)
            self.assertEqual(
                spec_ops.ac_read(r, "AC5"),
                "Given criterion input, When evaluated, Then criterion passes.",
            )

    def test_ac_user_sid_may_equal_existing_dom_id(self) -> None:
        """Override sid is checked only against other sids, not fragment ids."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                desc = root.find('.//p[@type="desc"]')
                assert desc is not None
                desc.set("id", "shared-token")
                sid = spec_ops.ac_add(
                    root,
                    "Given a shared sid, When created, Then it is accepted.",
                    under_uc_id=None,
                    user_sid="shared-token",
                )
            self.assertEqual(sid, "shared-token")

    def test_ac_update_preserves_sid_and_test_ref_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                ac = spec_ops.ac_add(
                    root,
                    "Given existing records, When queried, Then results are returned.",
                    under_uc_id=None,
                    user_sid="ac-11111111",
                )
                spec_ops.test_add(root, ac, "check", user_sid="tst-smoke-1")
                out = spec_ops.ac_update(
                    root,
                    ac,
                    "Given updated criteria, When evaluated, Then updated results are returned.",
                )
                self.assertEqual(out, "ac-11111111")
            r = load_for_read(path)
            tp = r.find('.//p[@type="test"]')
            assert tp is not None
            self.assertEqual(tp.get("ref_id"), "ac-11111111")
            self.assertEqual(tp.get("sid"), "tst-smoke-1")

    def test_write_minimal_spec_user_body_sid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(
                path, "T", "d", user_body_sid="spec-feature-auth"
            )
            r = load_for_read(path)
            self.assertEqual(r.find("body").get("sid"), "spec-feature-auth")

    def test_qs_ask_user_sid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                body_sid = root.find("body").get("sid")
                qid = spec_ops.qs_ask(
                    root,
                    body_sid,
                    "why?",
                    author=None,
                    target_role=None,
                    user_sid="q-33333333",
                )
            self.assertEqual(qid, "q-33333333")

    def test_qs_ask_duplicate_user_sid_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                body_sid = root.find("body").get("sid")
                spec_ops.qs_ask(
                    root,
                    body_sid,
                    "first?",
                    author=None,
                    target_role=None,
                    user_sid="q-aaaaaaaa",
                )
                with self.assertRaises(ValueError):
                    spec_ops.qs_ask(
                        root,
                        body_sid,
                        "second?",
                        author=None,
                        target_role=None,
                        user_sid="q-aaaaaaaa",
                    )

    def test_qs_thread_sid_stable_after_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                root.set("doc-kind", "questions")
                body_sid = root.find("body").get("sid")
                tid = spec_ops.qs_ask(
                    root,
                    body_sid,
                    "q?",
                    author=None,
                    target_role=None,
                    user_sid="q-44444444",
                )
                spec_ops.qs_answer(root, tid, "a.", author=None)
            r = load_for_read(path)
            qsids = {
                (p.get("type"), (p.get("sid") or "").strip())
                for p in r.findall(".//p")
                if p.get("type") in ("question", "answer")
            }
            self.assertIn(("question", "q-44444444"), qsids)
            self.assertIn(("answer", "q-44444444"), qsids)


if __name__ == "__main__":
    unittest.main()
