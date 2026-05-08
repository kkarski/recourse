"""Plan phases and tasks (phase_ops, markdown export)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import phase_ops, spec_ops, xmlio
from spectr.uow import load_for_read, recompute_dom_ids


class TestPlanPhaseTask(unittest.TestCase):
    def test_task_add_requires_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            with self.assertRaises(ValueError) as ctx:
                phase_ops.task_add(root, "nope")
            self.assertIn("task add", str(ctx.exception).lower())

    def test_task_add_auto_creates_plan_and_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            tsk = phase_ops.task_add_auto(root, "First task")
            self.assertTrue(tsk.startswith("tsk-"))
            recompute_dom_ids(root)
            xmlio.write_tree(path, root)
            root2 = load_for_read(path)
            rows = phase_ops.plan_iter(root2)
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0][0].startswith("ph-"))
            self.assertEqual(len(rows[0][1]), 1)
            self.assertEqual(rows[0][1][0][0], tsk)
            self.assertIn("First", rows[0][1][0][1])

    def test_task_list_all_and_ph_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            pa = phase_ops.phase_add(root)
            pb = phase_ops.phase_add(root)
            phase_ops.task_add(root, "A", phase_sid=pa)
            phase_ops.task_add(root, "B", phase_sid=pb)
            phase_ops.task_add(root, "A2", phase_sid=pa)
            recompute_dom_ids(root)
            xmlio.write_tree(path, root)
            root2 = load_for_read(path)
            all_rows = phase_ops.task_list(root2)
            self.assertEqual(len(all_rows), 3)
            only_a = phase_ops.task_list(root2, phase_sid=pa)
            self.assertEqual(len(only_a), 2)
            self.assertTrue(all(r[0] == pa for r in only_a))
            self.assertIn("A", only_a[0][2])
            missing = phase_ops.task_list(root2, phase_sid="ph-nope")
            self.assertEqual(missing, [])

    def test_task_add_auto_unknown_ph_creates_new_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            ph0 = phase_ops.phase_add(root)
            phase_ops.task_add_auto(root, "On known", phase_sid=ph0)
            phase_ops.task_add_auto(root, "On new phase", phase_sid="ph-no-such-phase")
            rows = phase_ops.plan_iter(root)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], ph0)
            self.assertEqual(len(rows[0][1]), 1)
            self.assertEqual(rows[1][0], "ph-no-such-phase")
            self.assertEqual(len(rows[1][1]), 1)
            self.assertIn("new phase", rows[1][1][0][1])

    def test_task_add_auto_first_phase_custom_sids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            tid = phase_ops.task_add_auto(
                root,
                "First",
                user_task_sid="tsk-alpha",
                user_phase_sid="ph-milestone-1",
            )
            self.assertEqual(tid, "tsk-alpha")
            rows = phase_ops.plan_iter(root)
            self.assertEqual(rows[0][0], "ph-milestone-1")
            self.assertEqual(rows[0][1][0][0], "tsk-alpha")

    def test_task_add_auto_with_existing_phase_sid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            ph = phase_ops.phase_add(root)
            t1 = phase_ops.task_add_auto(root, "A", phase_sid=ph)
            t2 = phase_ops.task_add_auto(root, "B", phase_sid=ph)
            self.assertNotEqual(t1, t2)
            rows = phase_ops.plan_iter(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], ph)
            self.assertEqual(len(rows[0][1]), 2)

    def test_phase_add_task_add_and_plan_iter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            root = load_for_read(path)
            ph = phase_ops.phase_add(root)
            self.assertTrue(ph.startswith("ph-"))
            tsk = phase_ops.task_add(root, "Implement feature", phase_sid=ph)
            self.assertTrue(tsk.startswith("tsk-"))
            recompute_dom_ids(root)
            xmlio.write_tree(path, root)
            root2 = load_for_read(path)
            rows = phase_ops.plan_iter(root2)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], ph)
            self.assertEqual(len(rows[0][1]), 1)
            self.assertEqual(rows[0][1][0][0], tsk)
            self.assertIn("Implement", rows[0][1][0][1])

    def test_spec_to_markdown_includes_delivery_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "My Spec", "d")
            root = load_for_read(path)
            phase_ops.task_add_auto(root, "Ship it")
            recompute_dom_ids(root)
            xmlio.write_tree(path, root)
            root2 = load_for_read(path)
            md = spec_ops.spec_to_markdown(root2)
            self.assertIn("## Delivery plan", md)
            self.assertIn("Ship it", md)


if __name__ == "__main__":
    unittest.main()
