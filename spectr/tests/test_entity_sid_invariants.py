"""Guards for unique entity sids: ``new_prefixed_id`` batch safety and post-insert checks."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import ids


class TestEntitySidInvariants(unittest.TestCase):
    def test_new_prefixed_id_reserves_each_candidate_in_set(self) -> None:
        reserved: set[str] = set()
        a = ids.new_prefixed_id(ids.PREFIX_AC, reserved)
        b = ids.new_prefixed_id(ids.PREFIX_AC, reserved)
        self.assertNotEqual(a, b)
        self.assertIn(a, reserved)
        self.assertIn(b, reserved)

    def test_assert_entity_sid_singleton_passes_once(self) -> None:
        root = etree.Element("spec")
        body = etree.SubElement(root, "body")
        etree.SubElement(body, "p", sid="ac-aaaaaaaa")
        ids.assert_entity_sid_singleton(root, "ac-aaaaaaaa")

    def test_assert_entity_sid_singleton_raises_on_duplicate(self) -> None:
        root = etree.Element("spec")
        body = etree.SubElement(root, "body")
        etree.SubElement(body, "p", sid="br-bbbbbbbb")
        etree.SubElement(body, "p", sid="br-bbbbbbbb")
        with self.assertRaises(ValueError) as ctx:
            ids.assert_entity_sid_singleton(root, "br-bbbbbbbb")
        self.assertIn("exactly one element", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
