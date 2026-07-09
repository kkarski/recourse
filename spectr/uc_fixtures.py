"""Minimal valid <div type="use-case"> XML for tests (mandatory sections + mermaid + narrative)."""

from __future__ import annotations

# Placeholders keep documents valid under the Spectr pydantic-xml model (layout validators).
_UC_PLACEHOLDER = "TBD"


def use_case_div(
    *,
    sid: str = "uc-22222222",
    h3_id: str = "3",
    title: str = "U",
    sp_id: str = "sp1",
    tr_id: str = "tr1",
    mf_id: str = "mf1",
    pc_id: str = "pc1",
    mer_id: str = "m1",
    narr_id: str = "4",
    narrative: str = "n",
    mermaid_body: str | None = None,
) -> str:
    mb = mermaid_body or (
        "useCaseDiagram\n"
        "  actor User\n"
        f'  usecase "{title}" as UC1\n'
        "  User --> UC1"
    )
    return (
        f'<div type="use-case" sid="{sid}">'
        f'<h3 id="{h3_id}">{title}</h3>'
        f'<p type="scope-preconditions" id="{sp_id}">{_UC_PLACEHOLDER}</p>'
        f'<p type="trigger" id="{tr_id}">{_UC_PLACEHOLDER}</p>'
        f'<p type="main-flow" id="{mf_id}">{_UC_PLACEHOLDER}</p>'
        f'<p type="post-conditions" id="{pc_id}">{_UC_PLACEHOLDER}</p>'
        f'<p type="mermaid" id="{mer_id}" diagram="use-case">{mb}</p>'
        f'<p id="{narr_id}">{narrative}</p>'
        "</div>"
    )
