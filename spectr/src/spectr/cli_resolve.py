"""Resolve CLI inputs (stdin, DOM id, flags) for commands with non-trivial targeting rules."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from lxml import etree

from spectr import dom_resolve
from spectr.refs import read_stdin_id_and_body, resolve_entity_id


def resolve_ac_add_parent_uc(
    path: Path,
    *,
    under_uc: str | None,
    uc_node_id: str | None,
    pipe_uc: bool,
    read_spec: Callable[[Path], etree._Element],
) -> tuple[str | None, etree._Element | None]:
    """Return ``(parent_use_case_sid_or_none, prefetched_root_or_none)``.

    *prefetched_root* is set when the spec was loaded to resolve ``--uc-id``; pass it to the
    mutating context so the tree is not parsed twice.

    Raises ``ValueError`` for invalid flag combinations or resolution failures.
    """
    if uc_node_id and (under_uc is not None or pipe_uc):
        raise ValueError("Do not combine --uc-id with --uc or --pipe-uc.")

    prefetched: etree._Element | None = None
    if uc_node_id and str(uc_node_id).strip():
        prefetched = read_spec(path)
        parent_uc = dom_resolve.uc_sid_from_dom_id(prefetched, str(uc_node_id).strip())
        if not parent_uc:
            raise ValueError(f"No use case matches node id {uc_node_id!r}.")
        return parent_uc, prefetched

    if under_uc is None and not pipe_uc:
        return None, None
    if under_uc is not None and under_uc != "-":
        return under_uc, None

    uc_resolved = resolve_entity_id(
        under_uc,
        use_stdin_if_dash=(under_uc == "-"),
        use_stdin_if_piped=(under_uc is None and pipe_uc),
    )
    if not uc_resolved:
        raise ValueError("could not resolve use case sid (--uc or stdin)")
    return uc_resolved, None


def resolve_qs_ask_target(
    path: Path,
    *,
    target_sid: str | None,
    target_dom_id: str | None,
    pipe_id: bool,
    question: str | None,
    question_arg: str | None,
    stdin_isatty: bool,
    read_spec: Callable[[Path], etree._Element],
) -> tuple[str | None, str | None, etree._Element | None]:
    """Return ``(target_entity_sid, question_text, prefetched_root_or_none)``.

    *question_text* may be ``None`` if the caller should prompt. *target_entity_sid* is ``None``
    if resolution failed (caller should raise with a CLI-specific message).

    Raises ``ValueError`` for mutually exclusive flags.
    """
    qtext: str | None = question or question_arg
    has_sid = target_sid is not None and str(target_sid).strip() != ""
    has_dom = target_dom_id is not None and str(target_dom_id).strip() != ""
    if has_sid and has_dom:
        raise ValueError("Use only one of --sid or --id for the question target.")

    prefetched: etree._Element | None = None
    tid: str | None = None
    if has_dom:
        prefetched = read_spec(path)
        tid = dom_resolve.qs_target_sid_from_dom_id(
            prefetched, str(target_dom_id).strip()
        )
        if not tid:
            raise ValueError(f"No question target matches node id {target_dom_id!r}.")
    elif has_sid:
        tid = resolve_entity_id(
            target_sid, use_stdin_if_dash=True, use_stdin_if_piped=False
        )

    if tid is None and pipe_id and not stdin_isatty:
        sid, body = read_stdin_id_and_body()
        if sid:
            tid = sid
        if body and not qtext:
            qtext = body

    return tid, qtext, prefetched
