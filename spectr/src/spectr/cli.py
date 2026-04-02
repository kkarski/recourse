#!/usr/bin/env python3
"""Spectr CLI for spec-driven software specifications.

Prefer ``spectr`` (after ``pip install -e .``) or ``python -m spectr``."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

# Allow `./cli.py` from a dev tree without installing: package lives in ../.. from this file.
_src = Path(__file__).resolve().parent.parent
if _src.name == "src" and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import click

from spectr import __version__
from spectr import dom_resolve
from spectr import ids
from spectr import phase_ops
from spectr import spec_ops
from spectr.discover import find_spec_html_upward
from spectr.naming import DEFAULT_INIT_TITLE, spec_folder_name_from_title
from spectr.user_config import resolve_role
from spectr import uow_session
from spectr.uow import SpecUnitOfWork, load_for_read
from spectr.refs import (
    format_porcelain,
    read_stdin_id_and_body,
    resolve_entity_id,
)


def _default_spec_parent_dir() -> Path:
    """./<title_with_spaces_as_underscores>/ (matches default init title)."""
    return Path(spec_folder_name_from_title(DEFAULT_INIT_TITLE))


def _default_spec() -> Path:
    env = os.environ.get("SPECTR_SPEC")
    if env:
        return Path(env)
    found = find_spec_html_upward()
    if found is not None:
        return found
    return _default_spec_parent_dir() / "spec.html"


def _emit(porcelain: bool, kind: str, entity_id: str) -> None:
    if porcelain:
        click.echo(format_porcelain(kind, entity_id))


def _merge_cmd_role(obj: dict, cmd_role: str | None) -> None:
    """Apply per-command --role / -r (overrides global --role for this invocation)."""
    if cmd_role is not None and str(cmd_role).strip():
        obj["role"] = str(cmd_role).strip()


def _resolved_author(obj: dict, explicit: str | None) -> str | None:
    """Author recorded on Q&A or feedback: non-empty ``--author`` / ``-a``, else configured role (if any)."""
    if explicit is not None:
        s = str(explicit).strip()
        if s:
            return s
    r = obj.get("role")
    if r is None:
        return None
    s = str(r).strip()
    return s if s else None


_CMD_ROLE_HELP = (
    "Default author role (e.g. pm, architect, engineer, qa) when --author is omitted "
    "(overrides global spectr --role for this command)."
)

_MARKDOWN_TEXT_HELP = (
    "Markdown body: headings, lists, fenced code blocks, and literal XML examples are "
    "supported. The CLI stores them as plain text in the specification file; characters "
    "like <, >, and & are escaped on write and restored when you read or export."
)

_SID_HELP = "Stable entity sid (e.g. uc-…, ac-…)."
_DOM_ID_HELP = "DOM fragment id attribute (normalized digits: 1, 2, …), not the entity sid."


def _sid_or_dom_id(
    root,
    sid: str | None,
    dom_id: str | None,
    *,
    label: str,
    from_dom,
) -> str:
    """Resolve exactly one of --sid or --id (node) to an entity sid."""
    has_sid = sid is not None and str(sid).strip() != ""
    has_dom = dom_id is not None and str(dom_id).strip() != ""
    if has_sid and has_dom:
        raise click.ClickException(f"Use only one of --sid or --id ({label}).")
    if has_sid:
        return str(sid).strip()
    if has_dom:
        resolved = from_dom(root, str(dom_id).strip())
        if resolved is None:
            raise click.ClickException(f"No {label} matches node id {dom_id!r}.")
        return resolved
    raise click.ClickException(f"Required: --sid or --id ({label}).")


def _read_spec(path: Path):
    """Load spec and normalize ``id`` attributes (persists if numbering changed)."""
    try:
        return load_for_read(path)
    except ValueError as e:
        raise click.ClickException(str(e)) from e


@contextmanager
def _mutating(path: Path):
    """Lock a draft DOM, yield it, commit (renumber ids + write) or rollback."""
    try:
        with SpecUnitOfWork.mutate(path) as root:
            yield root
    except ValueError as e:
        raise click.ClickException(str(e)) from e


def _work(obj: dict) -> Path:
    """Spec file to read/mutate: session draft when ``spectr uow begin`` is active."""
    return uow_session.resolve_working_spec_path(Path(obj["spec_path"]))


@click.group(invoke_without_command=True)
@click.version_option(__version__, "--version", prog_name="spectr")
@click.option(
    "--spec",
    "spec_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=_default_spec,
    help=(
        "Path to the Spectr HTML specification (default name spec.html; env: SPECTR_SPEC). "
        "If omitted, search upward from cwd for spec.html."
    ),
)
@click.option(
    "--role",
    "-r",
    "cli_role",
    default=None,
    help=(
        "Default author role (e.g. pm, architect, engineer, qa) for qs ask, qs answer, "
        "feedback add when --author is omitted (overrides SPECTR_ROLE and ~/.spectr/config). "
        "Ignored by other subcommands."
    ),
)
@click.pass_context
def cli(ctx: click.Context, spec_path: Path, cli_role: str | None) -> None:
    """Manage Spectr HTML specifications for software change sets.

    The specification is a single HTML document (see ``specs/spectr.xsd``): ``body``
    carries the spec ``sid``; use cases, acceptance criteria, tests, Q&A, feedback,
    and delivery plan live in typed ``div`` / ``p`` / ``ol`` / ``li`` elements. Entity
    ids are stored on ``sid`` (and unique ``id`` on each element). New ``sid`` values use
    ``prefix`` + hyphen + UUID segment (see ``spectr.ids``); assigned sids stay stable—only
    missing sids are filled on load (``spectr.uow.ensure_missing_entity_sids``).

    Markdown in text fields

      ``--desc``, questions, answers, feedback, task bodies, and similar fields accept
      Markdown. The tool stores them as text and escapes ``<``, ``>``, and ``&`` on write.

    Author role

      Only ``qs ask``, ``qs answer``, and ``feedback add`` use author role: optional
      ``--author`` / ``-a``, else per-command ``--role``, else global ``spectr --role``,
      else ``SPECTR_ROLE`` or ``spectr conf set --role``.

    Invocation

      ``spectr --help`` · ``spectr --spec ./My_Feature/spec.html uc list``

      Change-set blurb: ``spectr spec read`` · ``spectr spec update -d '…'``.

      Discovery walks upward for ``spec.html`` unless ``--spec`` or ``SPECTR_SPEC`` is set.
      Delivery plan: ``spectr task add -d '…'`` · ``spectr task list`` (optional ``--ph PHASE_SID``). Plan/phase markup is created when missing.

    Unit of work

      Each mutating subcommand runs one short transaction: clone → edit → renumber ``id`` → write.

      **Session (several commands, one write to ``spec.html``):** run ``spectr uow begin`` (for the
      same ``--spec``), then any mix of uc/ac/test/task/qs/feedback commands; they edit a draft
      under ``<spec-dir>/.spectr/``. Run ``spectr uow commit`` to merge the draft into the real
      spec (with id renumbering) and clear the session, or ``spectr uow abort`` to discard the
      draft. ``spectr uow status`` shows whether a session is active.

      Reads and exports use the draft while a session is open so you see uncommitted work.
      Stable references use ``sid``, not fragment ``id``.

    Piping

      Porcelain (``-p``): one line ``kind`` + tab + entity ``sid``. Use the same ``--spec``
      on both sides of a pipe when needed.

      ``spectr uc add -t T -d D -p | spectr ac add -d TEXT --uc -``

      ``(echo uc-xxxx; echo 'Q text') | spectr qs ask --pipe-id``

      ``spectr qs ask -s uc-xxxx -q 'Q text' -a pm -t architect``

    Targeting

      Most read/update/delete commands accept ``--sid`` / ``-s`` (entity sid) **or** ``--id``
      (DOM node id). Use only one per invocation.
    """
    ctx.ensure_object(dict)
    ctx.obj["spec_path"] = spec_path
    ctx.obj["role"] = resolve_role(cli_role=cli_role)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# --- conf ---


@cli.group(invoke_without_command=True)
@click.pass_context
def conf(ctx: click.Context) -> None:
    """Configure default author role for Q&A and feedback (pm, architect, engineer, qa; ~/.spectr/config)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@conf.command("set")
@click.option(
    "--role",
    "-r",
    required=True,
    help="Default author role name (e.g. pm, architect, engineer, qa; used when --author omitted; see SPECTR_ROLE).",
)
@click.option(
    "--config",
    type=click.Path(dir_okay=False, path_type=Path),
    default=lambda: Path.home() / ".spectr" / "config",
)
def conf_set(role: str, config: Path) -> None:
    """Persist the default author role (e.g. pm, architect, engineer, qa) for Q&A and feedback when unset elsewhere."""
    config.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if config.is_file():
        for line in config.read_text(encoding="utf-8").splitlines():
            if line.startswith("role="):
                continue
            lines.append(line)
    lines.append(f"role={role}")
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    click.echo(f"Wrote {config}")


@conf.command("show")
@click.option(
    "--config",
    type=click.Path(dir_okay=False, path_type=Path),
    default=lambda: Path.home() / ".spectr" / "config",
)
def conf_show(config: Path) -> None:
    """Display the contents of the spectr config file (role and any other keys)."""
    if not config.is_file():
        click.echo("(no config file)")
        return
    click.echo(config.read_text(encoding="utf-8"), nl=False)


# --- init ---


@cli.command("init")
@click.argument("title")
@click.argument(
    "target",
    type=click.Path(path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "--desc",
    "-d",
    default="Describe the change set.",
    show_default=True,
    help=_MARKDOWN_TEXT_HELP,
)
@click.pass_context
def init_cmd(
    ctx: click.Context,
    title: str,
    target: Path | None,
    desc: str,
) -> None:
    """Create ``spec.html``; TITLE is written to ``<title>`` and ``<h1>`` (quote if it contains spaces).

    If TARGET is omitted, the directory name is derived from TITLE (spaces → underscores).
    """
    title = (title or "").strip() or DEFAULT_INIT_TITLE
    desc = (desc or "").strip() or "Describe the change set."
    if target is None:
        target = Path(spec_folder_name_from_title(title))
    target.mkdir(parents=True, exist_ok=True)
    spec_path = target / "spec.html"
    if spec_path.exists():
        raise click.ClickException(f"already exists: {spec_path}")
    spec_ops.write_minimal_spec(spec_path, title, desc)
    click.echo(f"Created {spec_path}")


# --- spec (change-set level) ---


@cli.group("spec", invoke_without_command=True)
@click.pass_context
def spec_cmd(ctx: click.Context) -> None:
    """Change-set document: ``read`` (description) and ``update -d`` (replace description)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@spec_cmd.command("read")
@click.pass_context
def spec_read_cmd(ctx: click.Context) -> None:
    """Print the change-set description (``p`` ``type=desc`` under ``body``)."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_desc_read(root))


@spec_cmd.command("update")
@click.option("-d", "--desc", required=True, help=_MARKDOWN_TEXT_HELP)
@click.pass_context
def spec_update_cmd(ctx: click.Context, desc: str) -> None:
    """Replace the change-set description (Markdown)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        spec_ops.spec_desc_set(root, desc)
    click.echo("updated spec description")


# --- export ---


@cli.group(invoke_without_command=True)
@click.pass_context
def export(ctx: click.Context) -> None:
    """Export the spec to Markdown or JSON for reading, review, or integration (see markdown | json)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@export.command("markdown")
@click.pass_context
def export_markdown(ctx: click.Context) -> None:
    """Print a Markdown outline (title, description, use cases, acceptance criteria, tests)."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_to_markdown(root), nl=False)


@export.command("json")
@click.pass_context
def export_json(ctx: click.Context) -> None:
    """Print the HTML specification tree as pretty-printed JSON."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_to_json(root), nl=False)


# --- uc ---


@cli.group(invoke_without_command=True)
@click.pass_context
def uc(ctx: click.Context) -> None:
    """Manage use cases—behavioral slices of the feature under specification."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@uc.command("add")
@click.option("--title", "-t", required=True)
@click.option("--desc", "-d", default="", show_default=False, help=_MARKDOWN_TEXT_HELP)
@click.option(
    "--porcelain",
    "-p",
    is_flag=True,
    help="Print only kind\\tid for piping.",
)
@click.pass_context
def uc_add(
    ctx: click.Context,
    title: str,
    desc: str,
    porcelain: bool,
) -> None:
    """Insert a new use case with title and description; optional porcelain id line for pipes."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        eid = spec_ops.uc_add(root, title, desc)
    _emit(porcelain, ids.PREFIX_UC, eid)
    if not porcelain:
        click.echo(f"added uc {eid}")


@uc.command("list")
@click.pass_context
def uc_list_cmd(ctx: click.Context) -> None:
    """Print all use cases: sid, title, and a short description preview per line."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    for uid, tit, de in spec_ops.uc_list(root):
        click.echo(f"{uid}\t{tit or ''}\t{de[:80]}")


@uc.command("read")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def uc_read_cmd(ctx: click.Context, uc_sid: str | None, uc_dom_id: str | None) -> None:
    """Show the title and full description for one use case."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    uc_id = _sid_or_dom_id(
        root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
    )
    row = spec_ops.uc_read(root, uc_id)
    if row is None:
        raise click.ClickException(f"unknown uc: {uc_id}")
    tit, de = row
    click.echo(f"title:\t{tit or ''}")
    click.echo(f"desc:\t{de}")


@uc.command("update")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.option("--title", "-t", default=None)
@click.option("--desc", "-d", default=None, help=_MARKDOWN_TEXT_HELP)
@click.pass_context
def uc_update_cmd(
    ctx: click.Context,
    uc_sid: str | None,
    uc_dom_id: str | None,
    title: str | None,
    desc: str | None,
) -> None:
    """Change the title and/or description of an existing use case."""
    obj = ctx.obj
    if title is None and desc is None:
        raise click.ClickException("provide --title and/or --desc")
    path = _work(obj)
    with _mutating(path) as root:
        uc_id = _sid_or_dom_id(
            root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
        )
        if not spec_ops.uc_update(root, uc_id, title, desc):
            raise click.ClickException(f"unknown uc: {uc_id}")
    click.echo(f"updated {uc_id}")


@uc.command("delete")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def uc_delete_cmd(ctx: click.Context, uc_sid: str | None, uc_dom_id: str | None) -> None:
    """Remove a use case and its nested content from the spec."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        uc_id = _sid_or_dom_id(
            root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
        )
        if not spec_ops.uc_delete(root, uc_id):
            raise click.ClickException(f"unknown uc: {uc_id}")
    click.echo(f"deleted {uc_id}")


# --- ac ---


@cli.group(invoke_without_command=True)
@click.pass_context
def ac(ctx: click.Context) -> None:
    """Manage acceptance criteria—verifiable requirements that drive test cases (top-level or under a use case)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@ac.command("add")
@click.option(
    "--desc",
    "-d",
    multiple=True,
    required=True,
    help=(
        "Criterion description (Markdown; code and XML examples OK). "
        "Repeat to add several under the same parent."
    ),
)
@click.option(
    "--uc",
    "under_uc",
    default=None,
    help="Parent use case sid, or '-' to read sid from first stdin line (pipe from uc add).",
)
@click.option(
    "--uc-id",
    "uc_node_id",
    default=None,
    help="Parent use case via DOM node id (under that use case: h3, narrative p, …).",
)
@click.option(
    "--pipe-uc",
    is_flag=True,
    help="If --uc omitted and stdin is piped, read uc sid from first stdin line.",
)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def ac_add_cmd(
    ctx: click.Context,
    desc: tuple[str, ...],
    under_uc: str | None,
    uc_node_id: str | None,
    pipe_uc: bool,
    porcelain: bool,
) -> None:
    """Add acceptance-criteria paragraphs; ``--uc`` or stdin supplies the parent use-case ``sid`` (omit for body-level AC)."""
    obj = ctx.obj
    path = _work(obj)
    if uc_node_id and (under_uc is not None or pipe_uc):
        raise click.ClickException("Do not combine --uc-id with --uc or --pipe-uc.")
    parent_uc: str | None
    if uc_node_id and str(uc_node_id).strip():
        snap = _read_spec(path)
        parent_uc = dom_resolve.uc_sid_from_dom_id(snap, str(uc_node_id).strip())
        if not parent_uc:
            raise click.ClickException(f"No use case matches node id {uc_node_id!r}.")
    elif under_uc is None and not pipe_uc:
        parent_uc = None
    elif under_uc is not None and under_uc != "-":
        parent_uc = under_uc
    else:
        uc_resolved = resolve_entity_id(
            under_uc,
            use_stdin_if_dash=(under_uc == "-"),
            use_stdin_if_piped=(under_uc is None and pipe_uc),
        )
        if not uc_resolved:
            raise click.ClickException("could not resolve use case sid (--uc or stdin)")
        parent_uc = uc_resolved
    # Load spec after resolving stdin so a producer in a pipe can finish writing.
    new_ids: list[str] = []
    with _mutating(path) as root:
        for text in desc:
            eid = spec_ops.ac_add(root, text, under_uc_id=parent_uc)
            new_ids.append(eid)
    for eid in new_ids:
        _emit(porcelain, ids.PREFIX_AC, eid)
        if not porcelain:
            click.echo(f"added ac {eid}")


@ac.command("list")
@click.option("--recursive", "-r", is_flag=True)
@click.pass_context
def ac_list_cmd(ctx: click.Context, recursive: bool) -> None:
    """List criteria (flat: scope column) or --recursive paths under ucs."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    if recursive:
        for path, aid in spec_ops.ac_list_recursive(root):
            click.echo(f"{path}\t{aid}")
    else:
        for aid, scope, prev in spec_ops.ac_list_flat(root):
            click.echo(f"{aid}\t{scope}\t{prev}")


@ac.command("read")
@click.option("--sid", "-s", "ac_sid", default=None, help=_SID_HELP)
@click.option("--id", "ac_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def ac_read_cmd(ctx: click.Context, ac_sid: str | None, ac_dom_id: str | None) -> None:
    """Print the description body for one acceptance criterion."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    ac_id = _sid_or_dom_id(
        root,
        ac_sid,
        ac_dom_id,
        label="acceptance criterion",
        from_dom=dom_resolve.ac_sid_from_dom_id,
    )
    text = spec_ops.ac_read(root, ac_id)
    if text is None:
        raise click.ClickException(f"unknown ac: {ac_id}")
    click.echo(text)


@ac.command("update")
@click.option("--sid", "-s", "ac_sid", default=None, help=_SID_HELP)
@click.option("--id", "ac_dom_id", default=None, help=_DOM_ID_HELP)
@click.option("--desc", "-d", required=True, help=_MARKDOWN_TEXT_HELP)
@click.pass_context
def ac_update_cmd(
    ctx: click.Context,
    ac_sid: str | None,
    ac_dom_id: str | None,
    desc: str,
) -> None:
    """Replace the description text of an acceptance criterion."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        ac_id = _sid_or_dom_id(
            root,
            ac_sid,
            ac_dom_id,
            label="acceptance criterion",
            from_dom=dom_resolve.ac_sid_from_dom_id,
        )
        if not spec_ops.ac_update(root, ac_id, desc):
            raise click.ClickException(f"unknown ac: {ac_id}")
    click.echo(f"updated {ac_id}")


@ac.command("delete")
@click.option("--sid", "-s", "ac_sid", default=None, help=_SID_HELP)
@click.option("--id", "ac_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def ac_delete_cmd(ctx: click.Context, ac_sid: str | None, ac_dom_id: str | None) -> None:
    """Delete an acceptance criterion (wherever it appears in the tree)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        ac_id = _sid_or_dom_id(
            root,
            ac_sid,
            ac_dom_id,
            label="acceptance criterion",
            from_dom=dom_resolve.ac_sid_from_dom_id,
        )
        if not spec_ops.ac_delete(root, ac_id):
            raise click.ClickException(f"unknown ac: {ac_id}")
    click.echo(f"deleted {ac_id}")


# --- test ---


@cli.group(invoke_without_command=True)
@click.pass_context
def test(ctx: click.Context) -> None:
    """Manage test cases tied to acceptance criteria—how criteria become concrete checks."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@test.command("add")
@click.option("--ac", "ac_sid", default=None, help="Acceptance criterion sid.")
@click.option("--ac-id", "ac_node_id", default=None, help="Acceptance criterion DOM node id.")
@click.option("--desc", "-d", required=True, help=_MARKDOWN_TEXT_HELP)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def test_add_cmd(
    ctx: click.Context,
    ac_sid: str | None,
    ac_node_id: str | None,
    desc: str,
    porcelain: bool,
) -> None:
    """Add a ``p type=test`` under the body tests block; reference the AC by ``--ac`` or ``--ac-id``."""
    obj = ctx.obj
    path = _work(obj)
    has_ac = ac_sid is not None and str(ac_sid).strip() != ""
    has_nid = ac_node_id is not None and str(ac_node_id).strip() != ""
    if has_ac and has_nid:
        raise click.ClickException("Use only one of --ac or --ac-id.")
    if not has_ac and not has_nid:
        raise click.ClickException("Required: --ac or --ac-id.")
    try:
        with _mutating(path) as root:
            if has_nid:
                ac_id = dom_resolve.ac_sid_from_dom_id(root, str(ac_node_id).strip())
                if not ac_id:
                    raise click.ClickException(f"No acceptance criterion matches node id {ac_node_id!r}.")
            else:
                ac_id = str(ac_sid).strip()
            eid = spec_ops.test_add(root, ac_id, desc)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_TEST, eid)
    if not porcelain:
        click.echo(f"added test {eid}")


@test.command("read")
@click.option("--sid", "-s", "test_sid", default=None, help=_SID_HELP)
@click.option("--id", "test_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def test_read_cmd(ctx: click.Context, test_sid: str | None, test_dom_id: str | None) -> None:
    """Show ``ref_id`` (AC sid) and description for one test."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    test_id = _sid_or_dom_id(
        root,
        test_sid,
        test_dom_id,
        label="test",
        from_dom=dom_resolve.test_sid_from_dom_id,
    )
    row = spec_ops.test_read(root, test_id)
    if row is None:
        raise click.ClickException(f"unknown test: {test_id}")
    ref, de = row
    click.echo(f"ref_id:\t{ref}")
    click.echo(f"desc:\t{de}")


@test.command("update")
@click.option("--sid", "-s", "test_sid", default=None, help=_SID_HELP)
@click.option("--id", "test_dom_id", default=None, help=_DOM_ID_HELP)
@click.option("--desc", "-d", required=True, help=_MARKDOWN_TEXT_HELP)
@click.pass_context
def test_update_cmd(
    ctx: click.Context,
    test_sid: str | None,
    test_dom_id: str | None,
    desc: str,
) -> None:
    """Update the description of an existing test."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        test_id = _sid_or_dom_id(
            root,
            test_sid,
            test_dom_id,
            label="test",
            from_dom=dom_resolve.test_sid_from_dom_id,
        )
        if not spec_ops.test_update(root, test_id, desc):
            raise click.ClickException(f"unknown test: {test_id}")
    click.echo(f"updated {test_id}")


@test.command("delete")
@click.option("--sid", "-s", "test_sid", default=None, help=_SID_HELP)
@click.option("--id", "test_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def test_delete_cmd(ctx: click.Context, test_sid: str | None, test_dom_id: str | None) -> None:
    """Remove a test from the specification."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        test_id = _sid_or_dom_id(
            root,
            test_sid,
            test_dom_id,
            label="test",
            from_dom=dom_resolve.test_sid_from_dom_id,
        )
        if not spec_ops.test_delete(root, test_id):
            raise click.ClickException(f"unknown test: {test_id}")
    click.echo(f"deleted {test_id}")


# --- qs ---


@cli.group(invoke_without_command=True)
@click.pass_context
def qs(ctx: click.Context) -> None:
    """Ask, answer, or list Q&A threads so roles can refine requirements on entities in the specification."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@qs.command("ask")
@click.option("--sid", "-s", "target_sid", default=None, help="Target entity sid (body, uc, or ac).")
@click.option(
    "--id",
    "target_dom_id",
    default=None,
    help="Target entity via DOM id (h1, desc p, element under a use case, or AC p).",
)
@click.option(
    "--pipe-id",
    is_flag=True,
    help="Read target sid from stdin line 1 (optional body on following lines).",
)
@click.option("--author", "-a", default=None)
@click.option("--target", "-t", "target_role", default=None)
@click.option(
    "--question",
    "-q",
    default=None,
    help="Question text if not positional. " + _MARKDOWN_TEXT_HELP,
)
@click.argument("question_arg", required=False)
@click.option("--porcelain", "-p", is_flag=True)
@click.option("--role", "-r", "cmd_role", default=None, help=_CMD_ROLE_HELP)
@click.pass_context
def qs_ask_cmd(
    ctx: click.Context,
    target_sid: str | None,
    target_dom_id: str | None,
    pipe_id: bool,
    author: str | None,
    target_role: str | None,
    question: str | None,
    question_arg: str | None,
    porcelain: bool,
    cmd_role: str | None,
) -> None:
    """Post a question against the spec (body ``sid``), a use-case ``sid``, or an AC ``sid``; answer with ``qs answer``.

    Returns the question thread ``sid`` (porcelain: ``q`` + tab + sid).
    """
    obj = ctx.obj
    _merge_cmd_role(obj, cmd_role)
    author_resolved = _resolved_author(obj, author)
    tid: str | None = None
    qtext: str | None = question or question_arg

    has_sid = target_sid is not None and str(target_sid).strip() != ""
    has_dom = target_dom_id is not None and str(target_dom_id).strip() != ""
    if has_sid and has_dom:
        raise click.ClickException("Use only one of --sid or --id for the question target.")
    path = _work(obj)
    if has_dom:
        root_snap = _read_spec(path)
        tid = dom_resolve.qs_target_sid_from_dom_id(root_snap, str(target_dom_id).strip())
        if not tid:
            raise click.ClickException(f"No question target matches node id {target_dom_id!r}.")
    elif has_sid:
        tid = resolve_entity_id(
            target_sid, use_stdin_if_dash=True, use_stdin_if_piped=False
        )
    if tid is None and pipe_id and not sys.stdin.isatty():
        sid, body = read_stdin_id_and_body()
        if sid:
            tid = sid
        if body and not qtext:
            qtext = body
    if tid is None:
        raise click.ClickException(
            "need --sid ENTITY, --sid - (stdin sid), --id NODE, or --pipe-id with piped stdin"
        )
    if not qtext:
        qtext = click.prompt("Question text")

    try:
        with _mutating(path) as root:
            qid = spec_ops.qs_ask(
                root, tid, qtext, author=author_resolved, target_role=target_role
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_Q, qid)
    if not porcelain:
        click.echo(f"asked q {qid} on {tid}")


@qs.command("answer")
@click.option("--sid", "-s", "thread_sid", default=None, help="Question thread sid.")
@click.option(
    "--id",
    "question_dom_id",
    default=None,
    help="DOM id of a question or answer paragraph in that thread.",
)
@click.option("--author", "-a", default=None)
@click.argument("text", required=False)
@click.option("--role", "-r", "cmd_role", default=None, help=_CMD_ROLE_HELP)
@click.pass_context
def qs_answer_cmd(
    ctx: click.Context,
    thread_sid: str | None,
    question_dom_id: str | None,
    author: str | None,
    text: str | None,
    cmd_role: str | None,
) -> None:
    """Answer by thread ``sid`` or by DOM id of a question/answer ``p`` in that thread."""
    obj = ctx.obj
    _merge_cmd_role(obj, cmd_role)
    author_resolved = _resolved_author(obj, author)
    body = text
    if not body:
        body = click.prompt("Answer text")
    path = _work(obj)
    with _mutating(path) as root:
        question_id = _sid_or_dom_id(
            root,
            thread_sid,
            question_dom_id,
            label="question thread",
            from_dom=dom_resolve.qs_thread_sid_from_dom_id,
        )
        if not spec_ops.qs_answer(root, question_id, body, author=author_resolved):
            raise click.ClickException(f"unknown question thread: {question_id}")
    click.echo(f"answered {question_id}")


@qs.command("list")
@click.pass_context
def qs_list_cmd(ctx: click.Context) -> None:
    """List questions: thread sid, context ref (e.g. parent uc sid), author, preview."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    for qid, ref, auth, prev in spec_ops.qs_list(root):
        click.echo(f"{qid}\t{ref or ''}\t{auth or ''}\t{prev}")


# --- feedback ---


@cli.group(invoke_without_command=True)
@click.pass_context
def feedback(ctx: click.Context) -> None:
    """Add or manage feedback on the specification during review."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@feedback.command("add")
@click.option("--author", "-a", default=None)
@click.argument("text", required=False)
@click.option("--porcelain", "-p", is_flag=True)
@click.option("--role", "-r", "cmd_role", default=None, help=_CMD_ROLE_HELP)
@click.pass_context
def feedback_add_cmd(
    ctx: click.Context,
    author: str | None,
    text: str | None,
    porcelain: bool,
    cmd_role: str | None,
) -> None:
    """Append feedback (Markdown; code/XML OK); prompts for text if omitted."""
    obj = ctx.obj
    _merge_cmd_role(obj, cmd_role)
    author_resolved = _resolved_author(obj, author)
    body = text
    if not body:
        body = click.prompt("Comment")
    path = _work(obj)
    with _mutating(path) as root:
        eid = spec_ops.feedback_add(root, body, author=author_resolved)
    _emit(porcelain, ids.PREFIX_FB, eid)
    if not porcelain:
        click.echo(f"added feedback {eid}")


# --- task (delivery plan: li type=task) ---


_PH_HELP = (
    "Phase sid from `task list`: append under that phase. If it does not exist, a new phase "
    "is created (auto ph-… sid) and the task is added there. If omitted: use the last phase, "
    "or create one when none exist."
)


def _exec_task_add_auto(obj: dict, body: str, phase_sid: str | None, porcelain: bool) -> None:
    path = _work(obj)
    try:
        with _mutating(path) as root:
            eid = phase_ops.task_add_auto(root, body, phase_sid=phase_sid)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_TASK, eid)
    if not porcelain:
        click.echo(f"added task {eid}")


@cli.group("task", invoke_without_command=True)
@click.pass_context
def task_cli(ctx: click.Context) -> None:
    """List or add delivery-plan tasks (``li type=task`` under ``div type=plan``)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@task_cli.command("list")
@click.option(
    "--ph",
    "phase_sid",
    default=None,
    help="Only list tasks under this phase sid (exact match on the phase ol).",
)
@click.pass_context
def task_list_cmd(ctx: click.Context, phase_sid: str | None) -> None:
    """Print tasks as tab-separated phase sid, task sid, body preview (use ``--ph`` to filter one phase)."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    want = str(phase_sid).strip() if phase_sid is not None and str(phase_sid).strip() else None
    rows = phase_ops.task_list(root, phase_sid=want)
    if not rows:
        if want:
            click.echo(f"(no tasks for phase {want!r})")
        else:
            click.echo("(no plan tasks)")
        return
    for ph_sid, tsk_sid, prev in rows:
        ps = ph_sid if ph_sid else ""
        ts = tsk_sid if tsk_sid else ""
        click.echo(f"{ps}\t{ts}\t{prev}")


@task_cli.command("add")
@click.option("--desc", "-d", "body", required=True, help=_MARKDOWN_TEXT_HELP)
@click.option("--ph", "phase_sid", default=None, help=_PH_HELP)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def task_add_delivery_cmd(
    ctx: click.Context,
    body: str,
    phase_sid: str | None,
    porcelain: bool,
) -> None:
    """Append a task; creates plan/phases with auto sids when needed. ``--ph`` targets a phase by sid or creates one."""
    _exec_task_add_auto(ctx.obj, body, phase_sid, porcelain)


# --- uow (multi-command session) ---


@cli.group("uow", invoke_without_command=True)
@click.pass_context
def uow_group(ctx: click.Context) -> None:
    """Multi-command edit session: begin → mutate (draft) → commit or abort."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@uow_group.command("begin")
@click.pass_context
def uow_begin_cmd(ctx: click.Context) -> None:
    """Start a session: copy the spec to ``.spectr/uow-draft.html``; later commands edit that draft."""
    obj = ctx.obj
    canon = Path(obj["spec_path"]).resolve()
    try:
        uow_session.begin(canon)
    except (ValueError, OSError) as e:
        raise click.ClickException(str(e)) from e
    click.echo(
        "Unit of work started. Mutating commands now update the draft until "
        "`spectr uow commit` or `spectr uow abort`."
    )


@uow_group.command("commit")
@click.pass_context
def uow_commit_cmd(ctx: click.Context) -> None:
    """Write the draft to the spec file (renumber ids), remove the session."""
    obj = ctx.obj
    canon = Path(obj["spec_path"]).resolve()
    try:
        uow_session.commit(canon)
    except (ValueError, OSError) as e:
        raise click.ClickException(str(e)) from e
    click.echo(f"Committed unit of work to {canon}")


@uow_group.command("abort")
@click.pass_context
def uow_abort_cmd(ctx: click.Context) -> None:
    """Discard the draft and clear the session (spec file unchanged)."""
    obj = ctx.obj
    canon = Path(obj["spec_path"]).resolve()
    was_active = uow_session.is_active(canon)
    uow_session.abort(canon)
    click.echo(
        "Aborted unit of work; draft discarded."
        if was_active
        else "No active unit of work (nothing to discard)."
    )


@uow_group.command("status")
@click.pass_context
def uow_status_cmd(ctx: click.Context) -> None:
    """Show whether a unit of work is active and where the draft lives."""
    obj = ctx.obj
    canon = Path(obj["spec_path"]).resolve()
    for line in uow_session.status_lines(canon):
        click.echo(line)


def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
