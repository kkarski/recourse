"""DOM id → entity sid resolution."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import dom_resolve


class TestDomResolve(unittest.TestCase):
    def test_uc_sid_from_h3(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-11111111">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            b'<p type="trigger" id="4t">t</p>'
            b'<div type="actors"><p type="actor" id="4a">A</p></div>'
            b'<div type="preconditions"><p type="precondition" id="4p">P</p></div>'
            b'<div type="postconditions"><p type="postcondition" id="4o">O</p></div>'
            b"</div>"
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.uc_sid_from_dom_id(root, "3"), "uc-22222222")
        self.assertEqual(dom_resolve.uc_sid_from_dom_id(root, "4"), "uc-22222222")

    def test_ac_sid_from_dom_id(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-33333333">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="acceptance-criteria"><p type="acceptance-criteria" id="5" sid="ac-44444444">x</p></div>'
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.ac_sid_from_dom_id(root, "5"), "ac-44444444")

    def test_br_sid_from_dom_id(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-33333333">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="business-rules"><p type="business-rule" id="5" sid="br-44444444">r</p></div>'
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.br_sid_from_dom_id(root, "5"), "br-44444444")

    def test_qs_target_from_h1_and_desc(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-55555555">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p></body></html>'
        )
        self.assertEqual(dom_resolve.qs_target_sid_from_dom_id(root, "1"), "spec-55555555")
        self.assertEqual(dom_resolve.qs_target_sid_from_dom_id(root, "2"), "spec-55555555")

    def test_qs_target_from_business_rule(self) -> None:
        root = etree.fromstring(
            b'<html><head><title>x</title></head><body sid="spec-55555555">'
            b'<h1 id="1">T</h1><p type="desc" id="2">d</p>'
            b'<div type="business-rules"><p type="business-rule" id="3" sid="br-66666666">r</p></div>'
            b"</body></html>"
        )
        self.assertEqual(dom_resolve.qs_target_sid_from_dom_id(root, "3"), "br-66666666")

    def test_qs_thread_from_answer_p(self) -> None:
        root = etree.fromstring(
            b"<html><body sid=\"spec-66666666\"><h1 id=\"1\">x</h1><p type=\"desc\" id=\"2\"/>"
            b'<div type="questions"><p type="question" id="6" sid="q-77777777">Q</p>'
            b'<p type="answer" id="7" sid="q-77777777">A</p></div></body></html>'
        )
        self.assertEqual(dom_resolve.qs_thread_sid_from_dom_id(root, "7"), "q-77777777")

    def test_feedback_sid_from_dom_id(self) -> None:
        root = etree.fromstring(
            b'<html><body sid="spec-88888888"><div type="feedback">'
            b'<p type="feedback" id="9" sid="fb-aaaaaaaa">x</p></div></body></html>'
        )
        self.assertEqual(dom_resolve.feedback_sid_from_dom_id(root, "9"), "fb-aaaaaaaa")

    def test_task_sid_from_dom_id(self) -> None:
        root = etree.fromstring(
            b'<html><body sid="spec-99999999"><div type="plan">'
            b'<ol type="phase" sid="ph-bbbbbbbb">'
            b'<li type="task" id="10" sid="tsk-cccccccc">Work</li>'
            b"</ol></div></body></html>"
        )
        self.assertEqual(dom_resolve.task_sid_from_dom_id(root, "10"), "tsk-cccccccc")


if __name__ == "__main__":
    unittest.main()
