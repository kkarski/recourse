from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr.discover import find_spec_html_upward
from spectr.cli import _questions_file_path


class TestDiscoverSpec(unittest.TestCase):
    def test_prefers_feature_spec_html_when_spec_html_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = root / "My_Feature"
            feature.mkdir()
            spec = feature / "My_Feature_spec.html"
            spec.write_text("<html/>", encoding="utf-8")
            nested = feature / "sub" / "deep"
            nested.mkdir(parents=True)
            found = find_spec_html_upward(start=nested)
            self.assertEqual(found, spec)

    def test_questions_file_path_uses_spec_stem_when_named_star_spec_html(self) -> None:
        spec = Path("/tmp/My Feature/custom_name_spec.html")
        self.assertEqual(
            _questions_file_path(spec),
            Path("/tmp/My Feature/custom_name_questions.html"),
        )

    def test_questions_file_path_uses_parent_directory_for_spec_html(self) -> None:
        spec = Path("/tmp/My Feature/spec.html")
        self.assertEqual(
            _questions_file_path(spec),
            Path("/tmp/My Feature/My_Feature_questions.html"),
        )

    def test_questions_file_path_flat_specs_directory(self) -> None:
        spec = Path("/tmp/specs/candidate_providers_spec.html")
        self.assertEqual(
            _questions_file_path(spec),
            Path("/tmp/specs/candidate_providers_questions.html"),
        )


if __name__ == "__main__":
    unittest.main()
