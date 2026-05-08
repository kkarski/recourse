"""Delete paths for Q&A threads, feedback, and plan tasks (with empty-wrapper pruning)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import phase_ops, spec_ops
from spectr.uow import SpecUnitOfWork, load_for_read


class TestQsFeedbackTaskDelete(unittest.TestCase):
    def test_qs_delete_removes_question_and_answer_and_prunes_questions_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                body = root.find("body")
                assert body is not None
                body_sid = body.get("sid")
                assert body_sid
                tid = spec_ops.qs_ask(
                    root, body_sid, "Why?", author=None, target_role=None
                )
                self.assertTrue(spec_ops.qs_answer(root, tid, "Because.", author=None))
                self.assertTrue(spec_ops.qs_delete(root, tid))
            r = load_for_read(path)
            body_el = r.find("body")
            assert body_el is not None
            qdivs = [
                ch
                for ch in body_el
                if ch.tag == "div" and ch.get("type") == "questions"
            ]
            self.assertEqual(qdivs, [])

    def test_qs_delete_unknown_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                self.assertFalse(spec_ops.qs_delete(root, "q-nosuchthread"))

    def test_feedback_delete_prunes_empty_feedback_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                fid = spec_ops.feedback_add(root, "Nice spec", author=None)
                self.assertTrue(spec_ops.feedback_delete(root, fid))
            r = load_for_read(path)
            body_el = r.find("body")
            assert body_el is not None
            fdivs = [
                ch for ch in body_el if ch.tag == "div" and ch.get("type") == "feedback"
            ]
            self.assertEqual(fdivs, [])

    def test_task_delete_last_task_prunes_plan_div(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                tsk = phase_ops.task_add_auto(root, "Ship it")
                self.assertTrue(phase_ops.task_delete(root, tsk))
            r = load_for_read(path)
            body_el = r.find("body")
            assert body_el is not None
            pdivs = [ch for ch in body_el if ch.tag == "div" and ch.get("type") == "plan"]
            self.assertEqual(pdivs, [])

    def test_task_delete_one_of_two_keeps_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                ph = phase_ops.phase_add(root)
                a = phase_ops.task_add(root, "First", phase_sid=ph)
                phase_ops.task_add(root, "Second", phase_sid=ph)
                self.assertTrue(phase_ops.task_delete(root, a))
            r = load_for_read(path)
            rows = phase_ops.task_list(r)
            self.assertEqual(len(rows), 1)
            self.assertIn("Second", rows[0][2])


if __name__ == "__main__":
    unittest.main()
