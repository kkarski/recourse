from __future__ import annotations

import os
import unittest
from pathlib import Path

from click.testing import CliRunner

from spectr.cli import cli
from spectr.uow import load_for_read


class TestCliFeatureAdd(unittest.TestCase):
    def test_feature_add_creates_docs_and_changes_cwd(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            before = Path.cwd()
            res = runner.invoke(cli, ["feature", "add", "My Feature"])
            self.assertEqual(res.exit_code, 0, res.output)

            feature_dir = before / "My_Feature"
            spec_path = feature_dir / "My_Feature_spec.html"
            questions_path = feature_dir / "My_Feature_questions.html"

            self.assertTrue(feature_dir.is_dir())
            self.assertTrue(spec_path.is_file())
            self.assertTrue(questions_path.is_file())
            self.assertEqual(Path(os.getcwd()), feature_dir)

            sroot = load_for_read(spec_path)
            qroot = load_for_read(questions_path)
            self.assertEqual((sroot.get("doc-kind") or "").strip(), "spec")
            self.assertEqual((qroot.get("doc-kind") or "").strip(), "questions")
            self.assertEqual(sroot.findall(".//p[@type='question']"), [])
            self.assertEqual(qroot.findall(".//p[@type='question']"), [])

    def test_feature_add_supports_desc_and_with_sid(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            before = Path.cwd()
            res = runner.invoke(
                cli,
                [
                    "feature",
                    "add",
                    "Roadmap",
                    "--desc",
                    "Plan and scope.",
                    "--with-sid",
                    "spec-deadbeef",
                ],
            )
            self.assertEqual(res.exit_code, 0, res.output)
            spec_path = before / "Roadmap" / "Roadmap_spec.html"
            root = load_for_read(spec_path)
            body = root.find("body")
            desc = root.find("./body/p[@type='desc']")
            assert body is not None
            assert desc is not None
            self.assertEqual(body.get("sid"), "spec-deadbeef")
            self.assertEqual("".join(desc.itertext()), "Plan and scope.")


if __name__ == "__main__":
    unittest.main()
