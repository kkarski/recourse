"""Optional ``ph`` on UC / BR / AC and ``requirements_list_for_phase``."""

from __future__ import annotations

import unittest

from lxml import etree

from spectr import phase_ops, spec_ops


class TestPhRequirements(unittest.TestCase):
    def test_uc_br_ac_ph_roundtrip_and_list(self) -> None:
        root = etree.fromstring(
            b'<html doc-kind="spec">'
            b"<head><title>t</title></head>"
            b'<body sid="spec-11111111">'
            b'<h1 id="h1">t</h1><p type="desc" id="d">d</p>'
            b"</body></html>"
        )
        ph = phase_ops.phase_add(root)
        uc = spec_ops.uc_add(
            root,
            "U",
            "narrative here",
            trigger="tr",
            actors=("A",),
            preconditions=("pre",),
            postconditions=("post",),
            phases=(ph, "ph-extra"),
        )
        br = spec_ops.br_add(
            root,
            "Staff must frobnicate.",
            under_uc_id=None,
            phases=(ph,),
        )
        ac = spec_ops.ac_add(
            root,
            "Given g. When w. Then t.",
            under_uc_id=None,
            phases=("ph-extra",),
        )
        urow = spec_ops.uc_read(root, uc)
        assert urow is not None
        self.assertEqual(urow.phases, (ph, "ph-extra"))

        rows_ph = spec_ops.requirements_list_for_phase(root, ph)
        kinds = {r[0] for r in rows_ph}
        self.assertEqual(kinds, {"uc", "br"})
        sids = {r[1] for r in rows_ph}
        self.assertEqual(sids, {uc, br})

        rows_extra = spec_ops.requirements_list_for_phase(root, "ph-extra")
        kinds_x = {r[0] for r in rows_extra}
        self.assertEqual(kinds_x, {"uc", "ac"})

    def test_uc_update_clear_ph(self) -> None:
        root = etree.fromstring(
            b'<html doc-kind="spec">'
            b"<head><title>t</title></head>"
            b'<body sid="spec-22222222">'
            b'<h1 id="h1">t</h1><p type="desc" id="d">d</p>'
            b'<div type="use-case" sid="uc-aaaaaaaa" ph="ph-one">'
            b'<h3 id="t">U</h3>'
            b"<p id=\"n\">x</p>"
            b'<p type="trigger" id="tr">tr</p>'
            b'<div type="actors"><p type="actor" id="a1">A</p></div>'
            b'<div type="preconditions"><p type="precondition" id="p1">pre</p></div>'
            b'<div type="postconditions"><p type="postcondition" id="o1">post</p></div>'
            b"</div>"
            b"</body></html>"
        )
        spec_ops.uc_update(
            root,
            "uc-aaaaaaaa",
            title="U",
            desc="x",
            trigger="tr",
            actors=("A",),
            preconditions=("pre",),
            postconditions=("post",),
            phases=(),
        )
        uc_el = root.find('.//div[@type="use-case"]')
        assert uc_el is not None
        self.assertIsNone(uc_el.get("ph"))


if __name__ == "__main__":
    unittest.main()
