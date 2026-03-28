"""DOM id → entity sid resolution."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import dom_resolve


class TestDomResolve(unittest.TestCase):
    def test_uc_sid_from_h3(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-1">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="use-case" sid="uc-a"><h3 id="3">U</h3><p id="4">n</p></div>'
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.uc_sid_from_dom_id(root, "3"), "uc-a")
        self.assertEqual(dom_resolve.uc_sid_from_dom_id(root, "4"), "uc-a")

    def test_ac_sid_from_dom_id(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="s">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="acceptance-criteria"><p type="acceptance-criteria" id="5" sid="ac-z">x</p></div>'
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.ac_sid_from_dom_id(root, "5"), "ac-z")

    def test_qs_target_from_h1_and_desc(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-9">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p></body></html>'
        )
        self.assertEqual(dom_resolve.qs_target_sid_from_dom_id(root, "1"), "spec-9")
        self.assertEqual(dom_resolve.qs_target_sid_from_dom_id(root, "2"), "spec-9")

    def test_qs_thread_from_answer_p(self) -> None:
        root = etree.fromstring(
            b"<html><body sid=\"s\"><h1 id=\"1\">x</h1><p type=\"desc\" id=\"2\"/>"
            b'<div type="questions"><p type="question" id="6" sid="q-1">Q</p>'
            b'<p type="answer" id="7" sid="q-1">A</p></div></body></html>'
        )
        self.assertEqual(dom_resolve.qs_thread_sid_from_dom_id(root, "7"), "q-1")


if __name__ == "__main__":
    unittest.main()
