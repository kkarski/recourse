"""Layout rules: body block order and nested use-case / AC shape."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import struct_validate


def _minimal_body(inner: str) -> etree._Element:
    return etree.fromstring(
        f'<html><head><title>x</title></head><body sid="spec-11111111">'
        f'<h1 id="1">T</h1><p type="desc" id="2">d</p>{inner}</body></html>'
    )


class TestStructValidate(unittest.TestCase):
    def test_body_blocks_must_not_regress(self) -> None:
        root = _minimal_body(
            '<div type="questions"><p type="question" id="3" sid="q-11111111">Q</p></div>'
            '<div type="use-case" sid="uc-22222222"><h3 id="4">U</h3><p id="5">n</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("out of order", str(ctx.exception).lower())

    def test_use_case_nested_questions_before_ac_rejected(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<div type="questions"><p type="question" id="5" sid="q-11111111">Q</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="6" sid="ac-33333333">x</p></div>'
            "</div>"
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("acceptance-criteria", str(ctx.exception))
        self.assertIn("before", str(ctx.exception).lower())

    def test_ac_div_p_after_questions_rejected(self) -> None:
        root = _minimal_body(
            '<div type="acceptance-criteria">'
            '<div type="questions"><p type="question" id="3" sid="q-11111111">Q</p></div>'
            '<p type="acceptance-criteria" id="4" sid="ac-22222222">late</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("follow", str(ctx.exception).lower())

    def test_valid_sample_like_tree_ok(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="5" sid="ac-33333333">x</p></div>'
            '<div type="questions"><p type="question" id="6" sid="q-44444444">Q</p></div>'
            "</div>"
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="7" sid="ac-55555555">y</p></div>'
        )
        struct_validate.assert_valid_spec(root)


if __name__ == "__main__":
    unittest.main()
