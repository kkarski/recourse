"""Layout rules: body block uniqueness and nested use-case / AC shape."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import struct_validate


def _minimal_body(inner: str, *, doc_kind: str = "spec") -> etree._Element:
    return etree.fromstring(
        f'<html doc-kind="{doc_kind}"><head><title>x</title></head><body sid="spec-11111111">'
        f'<h1 id="1">T</h1><p type="desc" id="2">d</p>{inner}</body></html>'
    )


class TestStructValidate(unittest.TestCase):
    def test_definition_text_constraints_are_not_enforced_on_read(self) -> None:
        long_term = "T" * 101
        long_definition = "D" * 501
        root = _minimal_body(
            '<div type="definitions"><p type="definition" id="3" sid="def-aaaaaaaa" section="S">'
            f'<span type="term">{long_term}</span>{long_definition}'
            "</p></div>"
        )
        struct_validate.assert_valid_spec(root)

    def test_acceptance_criteria_text_constraints_are_not_enforced_on_read(self) -> None:
        root = _minimal_body(
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="3" sid="ac-11111111">'
            "Then outcome. Given context. When action."
            "</p></div>"
        )
        struct_validate.assert_valid_spec(root)

    def test_business_rule_text_constraints_are_not_enforced_on_read(self) -> None:
        root = _minimal_body(
            '<div type="business-rules"><p type="business-rule" id="3" sid="br-11111111">'
            "Users sign in with email."
            "</p></div>"
        )
        struct_validate.assert_valid_spec(root)

    def test_body_blocks_must_not_regress(self) -> None:
        root = _minimal_body(
            '<div type="questions"><p type="question" id="3" sid="q-11111111">Q</p></div>'
            '<div type="use-case" sid="uc-22222222"><h3 id="4">U</h3><p id="5">n</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn('doc-kind="spec"', str(ctx.exception))

    def test_use_case_nested_questions_before_ac_rejected(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<p type="trigger" id="4t">t</p>'
            '<div type="actors"><p type="actor" id="4a">A</p></div>'
            '<div type="preconditions"><p type="precondition" id="4p">P</p></div>'
            '<div type="postconditions"><p type="postcondition" id="4o">O</p></div>'
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
            '<p type="acceptance-criteria" id="4" sid="ac-22222222">'
            "Given context, When action, Then result."
            "</p></div>"
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("follow", str(ctx.exception).lower())

    def test_valid_sample_like_tree_ok(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<p type="trigger" id="4tr">t</p>'
            '<div type="actors"><p type="actor" id="4a">A</p></div>'
            '<div type="preconditions"><p type="precondition" id="4p">P</p></div>'
            '<div type="postconditions"><p type="postcondition" id="4o">O</p></div>'
            '<div type="business-rules"><p type="business-rule" id="5" sid="br-aaaaaaaa">Users must authenticate.</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="6" sid="ac-33333333">Given valid credentials, When user signs in, Then dashboard is shown.</p></div>'
            '<div type="questions"><p type="question" id="7" sid="q-44444444">Q</p></div>'
            "</div>"
            '<div type="business-rules"><p type="business-rule" id="8" sid="br-bbbbbbbb">Operators may export reports.</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="9" sid="ac-55555555">Given exported data, When file opens, Then columns are preserved.</p></div>'
        , doc_kind="questions")
        struct_validate.assert_valid_spec(root)

    def test_spec_doc_kind_rejects_questions_div(self) -> None:
        root = _minimal_body(
            '<div type="questions"><p type="question" id="3" sid="q-11111111">Q</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn('doc-kind="spec"', str(ctx.exception))

    def test_questions_doc_kind_allows_questions_div(self) -> None:
        root = _minimal_body(
            '<div type="questions"><p type="question" id="3" sid="q-11111111">Q</p>'
            '<p type="answer" id="4" sid="q-11111111">A</p></div>',
            doc_kind="questions",
        )
        struct_validate.assert_valid_spec(root)

    def test_body_br_after_ac_allowed(self) -> None:
        root = _minimal_body(
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="3" sid="ac-11111111">Given input, When validated, Then it passes.</p></div>'
            '<div type="business-rules"><p type="business-rule" id="4" sid="br-22222222">Records must be auditable.</p></div>'
        )
        struct_validate.assert_valid_spec(root)

    def test_references_after_definitions_allowed(self) -> None:
        root = _minimal_body(
            '<div type="definitions"><p type="definition" id="3" sid="def-aaaaaaaa" section="S">d</p></div>'
            '<ul type="references"><li>'
            '<a href="https://example.com" id="4" sid="ref-bbbbbbbb">x</a></li></ul>'
        )
        struct_validate.assert_valid_spec(root)

    def test_valid_references_before_definitions(self) -> None:
        root = _minimal_body(
            '<ul type="references"><li>'
            '<a href="https://example.com" id="3" sid="ref-bbbbbbbb">x</a></li></ul>'
            '<div type="definitions"><p type="definition" id="4" sid="def-aaaaaaaa" section="S">d</p></div>'
        )
        struct_validate.assert_valid_spec(root)

    def test_duplicate_top_level_body_div_rejected(self) -> None:
        root = _minimal_body(
            '<div type="business-rules"><p type="business-rule" id="3" sid="br-11111111">Users must sign in.</p></div>'
            '<div type="business-rules"><p type="business-rule" id="4" sid="br-22222222">Users may sign out.</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("unique", str(ctx.exception).lower())

    def test_multiple_top_level_use_case_divs_allowed(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-11111111"><h3 id="3">U1</h3><p id="4">n1</p>'
            '<p type="trigger" id="5">t1</p>'
            '<div type="actors"><p type="actor" id="6">A1</p></div>'
            '<div type="preconditions"><p type="precondition" id="7">P1</p></div>'
            '<div type="postconditions"><p type="postcondition" id="8">Po1</p></div>'
            '<div type="business-rules"><p type="business-rule" id="9" sid="br-aaaaaaaa">Users must complete profile setup.</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="10" sid="ac-aaaaaaaa">Given a new account, When setup completes, Then profile is active.</p></div>'
            "</div>"
            '<div type="use-case" sid="uc-22222222"><h3 id="11">U2</h3><p id="12">n2</p>'
            '<p type="trigger" id="13">t2</p>'
            '<div type="actors"><p type="actor" id="14">A2</p></div>'
            '<div type="preconditions"><p type="precondition" id="15">P2</p></div>'
            '<div type="postconditions"><p type="postcondition" id="16">Po2</p></div>'
            '<div type="business-rules"><p type="business-rule" id="17" sid="br-bbbbbbbb">Users can update notification settings.</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="18" sid="ac-bbbbbbbb">Given settings page, When user saves preferences, Then changes persist.</p></div>'
            "</div>"
        )
        struct_validate.assert_valid_spec(root)

    def test_use_case_requires_trigger_and_container_divs(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p></div>'
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("trigger", str(ctx.exception).lower())

    def test_use_case_metadata_divs_ordered_ok(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<p type="trigger" id="5">t</p>'
            '<div type="actors"><p type="actor" id="6">A</p></div>'
            '<div type="preconditions"><p type="precondition" id="7">P</p></div>'
            '<div type="postconditions"><p type="postcondition" id="8">Po</p></div>'
            '<div type="business-rules"><p type="business-rule" id="9" sid="br-aaaaaaaa">Users must verify email before checkout.</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="10" sid="ac-33333333">Given verified email, When user checks out, Then order is accepted.</p></div>'
            "</div>"
        )
        struct_validate.assert_valid_spec(root)

    def test_use_case_nested_br_after_ac_rejected(self) -> None:
        root = _minimal_body(
            '<div type="use-case" sid="uc-22222222"><h3 id="3">U</h3><p id="4">n</p>'
            '<p type="trigger" id="4t">t</p>'
            '<div type="actors"><p type="actor" id="4a">A</p></div>'
            '<div type="preconditions"><p type="precondition" id="4p">P</p></div>'
            '<div type="postconditions"><p type="postcondition" id="4o">O</p></div>'
            '<div type="acceptance-criteria"><p type="acceptance-criteria" id="5" sid="ac-33333333">x</p></div>'
            '<div type="business-rules"><p type="business-rule" id="6" sid="br-44444444">late</p></div>'
            "</div>"
        )
        with self.assertRaises(ValueError) as ctx:
            struct_validate.assert_valid_spec(root)
        self.assertIn("business-rules", str(ctx.exception))
        self.assertIn("before", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
