from __future__ import annotations

import unittest
from pathlib import Path

from click.testing import CliRunner

from spectr.cli import cli
from spectr.uow import load_for_read


class TestCliQuestionsFile(unittest.TestCase):
    def test_qs_ask_and_answer_write_to_feature_questions_html(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            root = Path.cwd()
            feature_dir = root / "My_Feature"
            spec_path = feature_dir / "My_Feature_spec.html"
            questions_path = feature_dir / "My_Feature_questions.html"

            feature_add_result = runner.invoke(
                cli,
                ["feature", "add", "My Feature", str(feature_dir)],
            )
            self.assertEqual(feature_add_result.exit_code, 0, feature_add_result.output)
            body_sid = load_for_read(spec_path).find("body").get("sid")  # type: ignore[union-attr]
            assert body_sid

            ask_result = runner.invoke(
                cli,
                [
                    "--spec",
                    str(spec_path),
                    "qs",
                    "ask",
                    "--sid",
                    body_sid,
                    "--question",
                    "What does this mean?",
                ],
            )
            self.assertEqual(ask_result.exit_code, 0, ask_result.output)

            thread_sid = ask_result.output.strip().split()[2]
            answer_result = runner.invoke(
                cli,
                [
                    "--spec",
                    str(spec_path),
                    "qs",
                    "answer",
                    "--sid",
                    thread_sid,
                    "It means the flow is clarified.",
                ],
            )
            self.assertEqual(answer_result.exit_code, 0, answer_result.output)

            self.assertTrue(questions_path.exists())
            qroot = load_for_read(questions_path)
            self.assertEqual((qroot.get("doc-kind") or "").strip(), "questions")
            qitems = qroot.findall(".//p[@type='question']")
            aitems = qroot.findall(".//p[@type='answer']")
            self.assertEqual(len(qitems), 1)
            self.assertEqual(len(aitems), 1)

            sroot = load_for_read(spec_path)
            self.assertEqual((sroot.get("doc-kind") or "").strip(), "spec")
            self.assertEqual(sroot.findall(".//p[@type='question']"), [])
            self.assertEqual(sroot.findall(".//p[@type='answer']"), [])

    def test_qs_recreates_missing_questions_html(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            root = Path.cwd()
            feature_dir = root / "My_Feature"
            spec_path = feature_dir / "My_Feature_spec.html"
            questions_path = feature_dir / "My_Feature_questions.html"

            feature_add_result = runner.invoke(
                cli,
                ["feature", "add", "My Feature", str(feature_dir)],
            )
            self.assertEqual(feature_add_result.exit_code, 0, feature_add_result.output)
            self.assertTrue(questions_path.is_file())
            questions_path.unlink()
            self.assertFalse(questions_path.exists())

            list_result = runner.invoke(
                cli,
                ["--spec", str(spec_path), "qs", "list"],
            )
            self.assertEqual(list_result.exit_code, 0, list_result.output)
            self.assertTrue(questions_path.is_file())
            qroot = load_for_read(questions_path)
            self.assertEqual((qroot.get("doc-kind") or "").strip(), "questions")

    def test_qs_list_bootstraps_empty_questions_html(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            root = Path.cwd()
            feature_dir = root / "My_Feature"
            spec_path = feature_dir / "My_Feature_spec.html"
            questions_path = feature_dir / "My_Feature_questions.html"

            feature_add_result = runner.invoke(
                cli,
                ["feature", "add", "My Feature", str(feature_dir)],
            )
            self.assertEqual(feature_add_result.exit_code, 0, feature_add_result.output)
            questions_path.write_bytes(b"")
            self.assertEqual(questions_path.stat().st_size, 0)

            list_result = runner.invoke(
                cli,
                ["--spec", str(spec_path), "qs", "list"],
            )
            self.assertEqual(list_result.exit_code, 0, list_result.output)
            self.assertGreater(questions_path.stat().st_size, 0)
            qroot = load_for_read(questions_path)
            self.assertEqual((qroot.get("doc-kind") or "").strip(), "questions")


if __name__ == "__main__":
    unittest.main()
