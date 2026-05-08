"""Regression: first ``uc_add`` must not precede ``definitions`` / ``references``."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from spectr import spec_ops, struct_validate
from spectr.uow import SpecUnitOfWork, load_for_read


class TestUseCaseInsertion(unittest.TestCase):
    def test_first_uc_after_definitions_preserves_body_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.html"
            spec_ops.write_minimal_spec(path, "T", "d")
            with SpecUnitOfWork.mutate(path) as root:
                spec_ops.def_add(
                    root,
                    "Meaning.",
                    section="S",
                    term="Term",
                )
                spec_ops.uc_add(
                    root,
                    "UC",
                    "narrative",
                    trigger="t",
                    actors=("a",),
                    preconditions=("p",),
                    postconditions=("o",),
                )
            r = load_for_read(path)
            struct_validate.assert_valid_spec(r)
            body = r.find("body")
            assert body is not None
            kinds: list[str | None] = []
            for ch in body:
                if ch.tag == "h1" or (ch.tag == "p" and ch.get("type") == "desc"):
                    continue
                if ch.tag == "ul" and ch.get("type") == "references":
                    kinds.append("references")
                elif ch.tag == "div":
                    kinds.append((ch.get("type") or "").strip())
            self.assertEqual(
                kinds,
                ["definitions", "use-case"],
                "definitions must precede the first use-case section",
            )


if __name__ == "__main__":
    unittest.main()
