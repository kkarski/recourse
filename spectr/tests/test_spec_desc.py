"""Change-set description helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops, xmlio
from spectr.uow import load_for_read


class TestSpecDesc(unittest.TestCase):
    def test_read_set_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "original")
            r = load_for_read(path)
            self.assertEqual(spec_ops.spec_desc_read(r), "original")
            spec_ops.spec_desc_set(r, "updated body")
            self.assertEqual(spec_ops.spec_desc_read(r), "updated body")
            xmlio.write_tree(path, r)
            r2 = load_for_read(path)
            self.assertEqual(spec_ops.spec_desc_read(r2), "updated body")


if __name__ == "__main__":
    unittest.main()
