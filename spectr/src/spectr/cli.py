#!/usr/bin/env python3
"""Spectr CLI for spec-driven software specifications.

Prefer ``spectr`` (after ``pip install -e .``) or ``python -m spectr``."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from itertools import zip_longest
from pathlib import Path

# Allow `./cli.py` from a dev tree without installing: package lives in ../.. from this file.
_src = Path(__file__).resolve().parent.parent
if _src.name == "src" and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import click
from click.core import ParameterSource

from spectr import __version__
from spectr import dom_resolve
from spectr import ids
from spectr import phase_ops
from spectr import spec_ops
from spectr import xmlio
from spectr.discover import find_spec_html_upward
from spectr.naming import DEFAULT_INIT_TITLE, questions_companion_stem, spec_folder_name_from_title
from spectr.user_config import resolve_role
from spectr import uow_session
from spectr.uow import SpecUnitOfWork, load_for_read
from spectr.refs import (
    format_porcelain,
    read_stdin_id_and_body,
    resolve_entity_id,
)


def _default_spec_parent_dir() -> Path:
    """Feature directory inferred from cwd name (spaces normalized to underscores)."""
    feature_dir = spec_folder_name_from_title(Path.cwd().name or DEFAULT_INIT_TITLE)
    return Path(feature_dir)


def _default_spec() -> Path:
    env = os.environ.get("SPECTR_SPEC")
    if env:
        return Path(env)
    found = find_spec_html_upward()
    if found is not None:
        return found
    feature = _default_spec_parent_dir().name
    return Path.cwd() / f"{feature}_spec.html"


def _cli_explicit(ctx: click.Context, param_name: str) -> bool:
    """True if the user set this option on the CLI (omit-on-update means clear)."""
    try:
        src = ctx.get_parameter_source(param_name)  # type: ignore[union-attr]
    except (ValueError, AttributeError):
        return False
    return src not in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP)


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

_SID_HELP = "Stable entity sid (any unique string; auto-allocated sids look like uc-xxxxxxxx)."
_DOM_ID_HELP = "DOM fragment id attribute (normalized digits: 1, 2, …), not the entity sid."
_WITH_SID_ADD_HELP = (
    "Optional entity sid: any non-empty string that does not duplicate another entity sid in the spec. "
    "Omit to auto-allocate (type prefix + 8 lowercase hex digits). "
    "Repeat once per --desc when adding several rows."
)
_QS_THREAD_WITH_SID_HELP = (
    "Optional Q&A thread sid: any unique string. "
    "Omit to auto-allocate (q- + 8 hex digits). Follow-up answers share this thread sid."
)
_INIT_SPEC_WITH_SID_HELP = (
    "Optional body (change-set) sid: any unique string. "
    "Omit to auto-allocate (spec- + 8 lowercase hex digits)."
)
_REF_WITH_SID_HELP = (
    "Optional reference-link sid: any unique string. "
    "Omit to auto-allocate (ref- + 8 lowercase hex digits)."
)
_TASK_WITH_SID_HELP = (
    "Optional task sid: any unique string. "
    "Omit to auto-allocate (tsk- + 8 hex digits)."
)
_TASK_PHASE_WITH_SID_HELP = (
    "When the plan has no phases yet, use this ph-… sid for the first phase. "
    "Ignored if phases already exist or when --ph is set."
)
_PH_ENTITY_HELP = (
    "Delivery phase sid(s) (repeat for multiple). Stored as space-separated ``ph`` on the entity."
)
_CLEAR_PH_HELP = "Drop all phase assignments (``ph`` attribute) on this entity."


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


def _questions_file_path(spec_path: Path) -> Path:
    """Companion questions document path next to the spec.

    ``stem`` comes from ``<stem>_spec.*`` when the filename matches that pattern; otherwise
    from the parent directory (same normalization as feature folder names).
    """
    resolved = spec_path.resolve()
    stem = questions_companion_stem(resolved)
    return resolved.parent / f"{stem}_questions.html"


def _questions_work(obj: dict) -> Path:
    """Q&A companion path for ``spectr qs``; created when missing or zero-byte.

    Creates an empty questions document (``doc-kind="questions"``) with ``body @sid`` matching
    the spec so change-set Q&A targets resolve. Threads are added by ``qs`` subcommands.
    """
    spec_work = _work(obj)
    canonical_spec = Path(obj["spec_path"]).resolve()
    qpath = _questions_file_path(canonical_spec)

    def _bootstrap_questions_file() -> None:
        qpath.parent.mkdir(parents=True, exist_ok=True)
        snap = load_for_read(spec_work)
        body_el = snap.find("body")
        if body_el is None:
            raise click.ClickException("spec has no <body> element")
        body_sid = (body_el.get("sid") or "").strip()
        if not body_sid:
            raise click.ClickException("spec body has no sid")
        try:
            spec_ops.write_minimal_questions_doc(qpath, body_sid=body_sid)
        except ValueError as e:
            raise click.ClickException(str(e)) from e

    if not qpath.is_file():
        _bootstrap_questions_file()
        return qpath
    try:
        is_empty = qpath.stat().st_size == 0
    except OSError:
        is_empty = True
    if is_empty:
        _bootstrap_questions_file()
    return qpath


@click.group(invoke_without_command=True)
@click.version_option(__version__, "--version", prog_name="spectr")
@click.option(
    "--spec",
    "spec_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=_default_spec,
    help=(
        "Path to the Spectr software specification file (env: SPECTR_SPEC). "
        "If omitted, discover the spec file by walking upward from cwd."
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
    """Spectr manages a structured software specification for a change set; this command loads the spec (via ``--spec``) and runs subcommands that edit or export requirements entities.

    The specification is a single document (see ``specs/spectr.xsd``): ``body``
    carries the spec ``sid``; use cases, business rules, acceptance criteria, Q&A, feedback,
    and delivery plan live in typed ``div`` / ``p`` / ``ol`` / ``li`` elements. Entity
    ids are stored on ``sid`` (and unique ``id`` on each element). Auto-allocated ``sid`` values use
    ``prefix`` + hyphen + UUID segment (see ``spectr.ids``); user ``--with-sid`` values need only
    be unique among other entity sids. Assigned sids stay stable—only
    missing sids are filled on load (``spectr.uow.ensure_missing_entity_sids``). Updates do not
    change entity ``sid`` (set at ``add`` or via optional ``--with-sid`` on feature add, uc/ac/br,
    task, and ``qs ask``; ``task add`` also supports ``--phase-with-sid`` for the first phase).

    Markdown in text fields

      ``--desc``, questions, answers, feedback, task bodies, and similar fields accept
      Markdown. The tool stores them as text and escapes ``<``, ``>``, and ``&`` on write.

    Author role

      Only ``qs ask``, ``qs answer``, and ``feedback add`` use author role: optional
      ``--author`` / ``-a``, else per-command ``--role``, else global ``spectr --role``,
      else ``SPECTR_ROLE`` or ``spectr conf set --role``.

    Invocation

      ``spectr --help`` · ``spectr --version`` / ``spectr version`` · ``spectr --spec ./My_Feature/<spec-file> uc list``

      Change-set blurb and links: ``spectr spec read`` · ``spectr spec update -d '…'`` ·
      ``spectr spec ref add -u URL -l '…'``.

      Discovery walks upward for the default spec filename unless ``--spec`` or ``SPECTR_SPEC`` is set.
      Delivery plan: ``spectr task add -d '…'`` · ``spectr task list`` (optional ``--ph PHASE_SID``). Plan/phase markup is created when missing.

    Unit of work

      Each mutating subcommand runs one short transaction: clone → edit → renumber ``id`` → write.

      **Session (several commands, one write to the spec file):** run ``spectr uow begin`` (for the
      same ``--spec``), then any mix of uc/ac/def/task/qs/feedback commands; they edit a draft
      under ``<spec-dir>/.spectr/``. Run ``spectr uow commit`` to merge the draft into the real
      spec (with id renumbering) and clear the session, or ``spectr uow abort`` to discard the
      draft. ``spectr uow status`` shows whether a session is active.

      Reads and exports use the draft while a session is open so you see uncommitted work.
      Stable references use ``sid``, not fragment ``id``.

    Piping

      Porcelain (``-p``): one line ``kind`` + tab + entity ``sid``. Use the same ``--spec``
      on both sides of a pipe when needed.

      ``spectr uc add -t T -d D --trigger TR --actor A --precond P --postcond O -p | spectr ac add -d TEXT --uc -``

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


@cli.command("version")
def version_cmd() -> None:
    """Print the Spectr CLI version (same output as ``spectr --version``)."""
    click.echo(f"spectr, version {__version__}")


# --- conf ---


@cli.group(invoke_without_command=True)
@click.pass_context
def conf(ctx: click.Context) -> None:
    """Author-role defaults are persisted preferences (who speaks when ``--author`` is omitted on ``qs`` / ``feedback``).

    Configure default author role for Q&A and feedback (pm, architect, engineer, qa; ~/.spectr/config)."""
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


# --- feature ---


@cli.group("feature", invoke_without_command=True)
@click.pass_context
def feature_cmd(ctx: click.Context) -> None:
    """Feature workspace commands (directory + spec/questions companion docs)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@feature_cmd.command("add")
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
@click.option(
    "--with-sid",
    "user_spec_sid",
    default=None,
    help=_INIT_SPEC_WITH_SID_HELP,
)
def feature_add_cmd(
    title: str, target: Path | None, desc: str, user_spec_sid: str | None
) -> None:
    """Create feature directory, initialize the feature spec and companion questions files, then chdir into it."""
    feature_title = (title or "").strip() or DEFAULT_INIT_TITLE
    feature_desc = (desc or "").strip() or "Describe the change set."
    if target is None:
        target = Path(spec_folder_name_from_title(feature_title))
    if target.exists():
        raise click.ClickException(f"already exists: {target}")
    target.mkdir(parents=True, exist_ok=False)
    feature_name = target.name
    spec_path = target / f"{feature_name}_spec.html"
    try:
        spec_ops.write_minimal_spec(
            spec_path,
            feature_title,
            feature_desc,
            user_body_sid=(user_spec_sid or "").strip() or None,
        )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    questions_path = _questions_file_path(spec_path)
    spec_root = load_for_read(spec_path)
    body_el = spec_root.find("body")
    if body_el is None:
        raise click.ClickException("spec has no <body> element")
    body_sid = (body_el.get("sid") or "").strip()
    if not body_sid:
        raise click.ClickException("spec body has no sid")
    try:
        spec_ops.write_minimal_questions_doc(questions_path, body_sid=body_sid)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    os.chdir(target)
    click.echo(f"Created {spec_path}")
    click.echo(f"Created {questions_path}")
    click.echo(f"Changed directory to {target.resolve()}")


# --- spec (change-set level) ---


@cli.group("spec", invoke_without_command=True)
@click.pass_context
def spec_cmd(ctx: click.Context) -> None:
    """The change-set description is the Markdown overview (``p type=desc``); use ``ref`` for external links (``ul type=references`` under ``body``).

    Subcommands: ``read``, ``update``, ``ref`` (``add`` / ``list`` / ``read`` / ``delete``)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@spec_cmd.command("read")
@click.pass_context
def spec_read_cmd(ctx: click.Context) -> None:
    """Print the change-set description (``p`` ``type=desc``): the Markdown scope/overview under the title."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_desc_read(root))


@spec_cmd.command("update")
@click.option("-d", "--desc", required=True, help=_MARKDOWN_TEXT_HELP)
@click.pass_context
def spec_update_cmd(ctx: click.Context, desc: str) -> None:
    """Replace the scope/overview Markdown that frames the change set for readers and reviewers."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        spec_ops.spec_desc_set(root, desc)
    click.echo("updated spec description")


@spec_cmd.group("ref")
@click.pass_context
def spec_ref_cmd(ctx: click.Context) -> None:
    """External links for the change set (``ul type=references`` → ``li`` → ``a href`` under ``body``).

    Subcommands: ``add``, ``list``, ``read``, ``delete``."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@spec_ref_cmd.command("add")
@click.option("--url", "-u", "url", required=True, help="Target URL (stored as the link href).")
@click.option("--label", "-l", "label", required=True, help="Link text (anchor body).")
@click.option("--with-sid", "user_ref_sid", default=None, help=_REF_WITH_SID_HELP)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def spec_ref_add_cmd(
    ctx: click.Context,
    url: str,
    label: str,
    user_ref_sid: str | None,
    porcelain: bool,
) -> None:
    """Append a reference link (creates ``ul type=references`` when missing)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        try:
            rid = spec_ops.spec_ref_add(
                root,
                url,
                label,
                user_sid=(user_ref_sid or "").strip() or None,
            )
        except ValueError as e:
            raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_REF, rid)
    if not porcelain:
        click.echo(f"added reference {rid}")


@spec_ref_cmd.command("list")
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def spec_ref_list_cmd(ctx: click.Context, porcelain: bool) -> None:
    """List reference links: ``sid``, ``href``, and label text per line."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    rows = spec_ops.spec_ref_list(root)
    if porcelain:
        for sid, _href, _lab in rows:
            click.echo(format_porcelain(ids.PREFIX_REF, sid))
        return
    for sid, href, lab in rows:
        click.echo(f"{sid}\t{href}\t{lab}")


@spec_ref_cmd.command("read")
@click.option("--sid", "-s", "ref_sid", default=None, help=_SID_HELP)
@click.option("--id", "ref_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def spec_ref_read_cmd(
    ctx: click.Context, ref_sid: str | None, ref_dom_id: str | None
) -> None:
    """Print ``url:`` and ``label:`` lines for one reference link."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    ref_id = _sid_or_dom_id(
        root,
        ref_sid,
        ref_dom_id,
        label="reference",
        from_dom=dom_resolve.ref_sid_from_dom_id,
    )
    row = spec_ops.spec_ref_read(root, ref_id)
    if row is None:
        raise click.ClickException(f"unknown reference: {ref_id}")
    href, lab = row
    click.echo(f"url:\t{href}")
    click.echo(f"label:\t{lab}")


@spec_ref_cmd.command("delete")
@click.option("--sid", "-s", "ref_sid", default=None, help=_SID_HELP)
@click.option("--id", "ref_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def spec_ref_delete_cmd(
    ctx: click.Context, ref_sid: str | None, ref_dom_id: str | None
) -> None:
    """Remove a reference link by ``sid`` or DOM fragment ``id``."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        ref_id = _sid_or_dom_id(
            root,
            ref_sid,
            ref_dom_id,
            label="reference",
            from_dom=dom_resolve.ref_sid_from_dom_id,
        )
        if not spec_ops.spec_ref_delete(root, ref_id):
            raise click.ClickException(f"unknown reference: {ref_id}")
    click.echo(f"deleted {ref_id}")


# --- export ---


@cli.group(invoke_without_command=True)
@click.pass_context
def export(ctx: click.Context) -> None:
    """Exports materialize the whole spec for humans (Markdown) or machines (JSON) — the primary read path outside the CLI lists.

    Subcommands: ``markdown`` and ``json``."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@export.command("markdown")
@click.pass_context
def export_markdown(ctx: click.Context) -> None:
    """Write a readable Markdown outline of the change set (title, description, entities, plan) for review and diffs."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_to_markdown(root), nl=False)


@export.command("json")
@click.pass_context
def export_json(ctx: click.Context) -> None:
    """Emit the spec tree as pretty-printed JSON for scripts and integrations."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    click.echo(spec_ops.spec_to_json(root), nl=False)


# --- uc ---


@cli.group(invoke_without_command=True)
@click.pass_context
def uc(ctx: click.Context) -> None:
    """Use cases bundle narrative, trigger, actors, pre/post conditions (atomic add/update), nested BRs/ACs, and Q&A.

    Structured markup (nested ``div`` elements for ``actors``, ``preconditions``, and ``postconditions`` — not loose
    typed ``<p>`` siblings) is defined in :mod:`spectr.uc_cli_layout`; these commands apply it through
    :mod:`spectr.spec_ops`.

    List, add, read, update, delete, deprecate (cascade BR/AC), and restore (UC only) use case nodes."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@uc.command("add")
@click.option("--title", "-t", required=True)
@click.option("--desc", "-d", default="", show_default=False, help=_MARKDOWN_TEXT_HELP)
@click.option(
    "--trigger",
    required=True,
    help="Trigger condition (required, non-empty).",
)
@click.option(
    "--actor",
    "actors",
    multiple=True,
    default=(),
    help="Actor (required: pass at least once; repeat in order for multiple).",
)
@click.option(
    "--precond",
    "precond",
    multiple=True,
    default=(),
    help="Precondition (required: pass at least once; repeat for more).",
)
@click.option(
    "--postcond",
    "postcond",
    multiple=True,
    default=(),
    help="Postcondition (required: pass at least once; repeat for more).",
)
@click.option(
    "--with-sid",
    "user_uc_sid",
    default=None,
    help="For uc-…: " + _WITH_SID_ADD_HELP,
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP,
)
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
    trigger: str,
    actors: tuple[str, ...],
    precond: tuple[str, ...],
    postcond: tuple[str, ...],
    user_uc_sid: str | None,
    phase_sids: tuple[str, ...],
    porcelain: bool,
) -> None:
    """Insert a new use case (narrative plus required trigger, actors, preconditions, postconditions)."""
    obj = ctx.obj
    path = _work(obj)
    try:
        with _mutating(path) as root:
            eid = spec_ops.uc_add(
                root,
                title,
                desc,
                user_sid=(user_uc_sid.strip() if user_uc_sid else None),
                trigger=trigger.strip(),
                actors=tuple(x.strip() for x in actors if str(x).strip()),
                preconditions=tuple(x.strip() for x in precond if str(x).strip()),
                postconditions=tuple(x.strip() for x in postcond if str(x).strip()),
                phases=tuple(x.strip() for x in phase_sids if str(x).strip()),
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_UC, eid)
    if not porcelain:
        click.echo(f"added uc {eid}")


@uc.command("list")
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include use cases with deprecated=\"true\" (hidden by default).",
)
@click.pass_context
def uc_list_cmd(ctx: click.Context, include_deprecated: bool) -> None:
    """Print all use cases: sid, title, and a short description preview per line."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    for uid, tit, de in spec_ops.uc_list(root, include_deprecated=include_deprecated):
        click.echo(f"{uid}\t{tit or ''}\t{de[:80]}")


@uc.command("read")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def uc_read_cmd(ctx: click.Context, uc_sid: str | None, uc_dom_id: str | None) -> None:
    """Show title, narrative, trigger, actors, and pre/post conditions for one use case."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    uc_id = _sid_or_dom_id(
        root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
    )
    row = spec_ops.uc_read(root, uc_id)
    if row is None:
        raise click.ClickException(f"unknown uc: {uc_id}")
    click.echo(f"title:\t{row.title or ''}")
    click.echo(f"desc:\t{row.desc}")
    click.echo(f"trigger:\t{row.trigger or ''}")
    for a in row.actors:
        click.echo(f"actor:\t{a}")
    for pr in row.preconditions:
        click.echo(f"precond:\t{pr}")
    for po in row.postconditions:
        click.echo(f"postcond:\t{po}")
    if row.phases:
        click.echo(f"ph:\t{' '.join(row.phases)}")


@uc.command("update")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.option("--title", "-t", default=None)
@click.option("--desc", "-d", default=None, help=_MARKDOWN_TEXT_HELP)
@click.option("--trigger", default=None, help="Trigger (omit on CLI to clear; required non-empty when set).")
@click.option(
    "--actor",
    "actors",
    multiple=True,
    default=(),
    help="Actor (repeat). Omit --actor entirely to clear all (invalid unless other fields restore a full UC).",
)
@click.option(
    "--precond",
    "precond",
    multiple=True,
    default=(),
    help="Precondition (repeat). Omit --precond entirely to clear all.",
)
@click.option(
    "--postcond",
    "postcond",
    multiple=True,
    default=(),
    help="Postcondition (repeat). Omit --postcond entirely to clear all.",
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP + " Omit entirely to leave phases unchanged.",
)
@click.option("--clear-ph", "clear_ph", is_flag=True, help=_CLEAR_PH_HELP)
@click.pass_context
def uc_update_cmd(
    ctx: click.Context,
    uc_sid: str | None,
    uc_dom_id: str | None,
    title: str | None,
    desc: str | None,
    trigger: str | None,
    actors: tuple[str, ...],
    precond: tuple[str, ...],
    postcond: tuple[str, ...],
    phase_sids: tuple[str, ...],
    clear_ph: bool,
) -> None:
    """Replace the whole use-case body: every option not passed on the CLI is cleared (atomic update).

    A valid use case must have a non-empty trigger, at least one actor, one precondition, and one
    postcondition — pass ``--trigger``, ``--actor`` (repeat), ``--precond``, and ``--postcond`` each
    time so the result stays complete.

    Deprecated use cases cannot be updated; use ``uc restore`` first.
    """
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        uc_id = _sid_or_dom_id(
            root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
        )
        tit = (title if _cli_explicit(ctx, "title") else "") or ""
        de = desc if _cli_explicit(ctx, "desc") else ""
        tr = (trigger if _cli_explicit(ctx, "trigger") else "") or ""
        act = (
            tuple(x.strip() for x in actors if str(x).strip())
            if _cli_explicit(ctx, "actors")
            else ()
        )
        pres = (
            tuple(x.strip() for x in precond if str(x).strip())
            if _cli_explicit(ctx, "precond")
            else ()
        )
        posts = (
            tuple(x.strip() for x in postcond if str(x).strip())
            if _cli_explicit(ctx, "postcond")
            else ()
        )
        phase_payload: tuple[str, ...] | None = None
        if clear_ph:
            phase_payload = ()
        elif _cli_explicit(ctx, "phase_sids"):
            phase_payload = tuple(x.strip() for x in phase_sids if str(x).strip())
        try:
            spec_ops.uc_update(
                root,
                uc_id,
                title=tit,
                desc=de,
                trigger=tr,
                actors=act,
                preconditions=pres,
                postconditions=posts,
                phases=phase_payload,
            )
        except ValueError as e:
            raise click.ClickException(str(e)) from e
    click.echo(f"updated {uc_id}")


@uc.command("deprecate")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def uc_deprecate_cmd(
    ctx: click.Context, uc_sid: str | None, uc_dom_id: str | None
) -> None:
    """Mark a use case deprecated and recursively deprecate BRs and ACs nested under it."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        uc_id = _sid_or_dom_id(
            root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
        )
        if not spec_ops.uc_deprecate(root, uc_id):
            raise click.ClickException(f"unknown uc: {uc_id}")
    click.echo(f"deprecated {uc_id}")


@uc.command("restore")
@click.option("--sid", "-s", "uc_sid", default=None, help=_SID_HELP)
@click.option("--id", "uc_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def uc_restore_cmd(
    ctx: click.Context, uc_sid: str | None, uc_dom_id: str | None
) -> None:
    """Clear deprecation on the use-case div only (BR/AC deprecation is unchanged)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        uc_id = _sid_or_dom_id(
            root, uc_sid, uc_dom_id, label="use case", from_dom=dom_resolve.uc_sid_from_dom_id
        )
        if not spec_ops.uc_restore(root, uc_id):
            raise click.ClickException(f"unknown uc: {uc_id}")
    click.echo(f"restored {uc_id}")


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


# --- br (business rules) ---


@cli.group(invoke_without_command=True)
@click.pass_context
def br(ctx: click.Context) -> None:
    """Business rules are policy and invariants that cut across UI flows; they are citeable text, optionally scoped under a use case.

    List, add, read, update, and delete business rule nodes."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


@br.command("add")
@click.option(
    "--desc",
    "-d",
    multiple=True,
    required=True,
    help=(
        "Rule text (Markdown; code and XML examples OK). "
        'Must include at least one of "must", "may", "can", "cannot". '
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
@click.option(
    "--with-sid",
    multiple=True,
    default=(),
    help="For br-…: " + _WITH_SID_ADD_HELP,
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP,
)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def br_add_cmd(
    ctx: click.Context,
    desc: tuple[str, ...],
    under_uc: str | None,
    uc_node_id: str | None,
    pipe_uc: bool,
    with_sid: tuple[str, ...],
    phase_sids: tuple[str, ...],
    porcelain: bool,
) -> None:
    """Add business-rule paragraphs; ``--uc`` or stdin supplies the parent use-case ``sid`` (omit for body-level rules)."""
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
    if with_sid and len(with_sid) != len(desc):
        raise click.ClickException("--with-sid must be omitted or repeated once per --desc.")
    new_ids: list[str] = []
    try:
        with _mutating(path) as root:
            for text, ws in zip_longest(desc, with_sid, fillvalue=None):
                eid = spec_ops.br_add(
                    root,
                    text,
                    under_uc_id=parent_uc,
                    user_sid=(ws.strip() if ws else None),
                    phases=tuple(x.strip() for x in phase_sids if str(x).strip()),
                )
                new_ids.append(eid)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    for eid in new_ids:
        _emit(porcelain, ids.PREFIX_BR, eid)
        if not porcelain:
            click.echo(f"added br {eid}")


@br.command("list")
@click.option("--recursive", "-r", is_flag=True)
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include items with deprecated=\"true\" (hidden by default).",
)
@click.pass_context
def br_list_cmd(
    ctx: click.Context,
    recursive: bool,
    include_deprecated: bool,
) -> None:
    """List business rules (flat: scope column) or --recursive paths under ucs."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    if recursive:
        for path, bid in spec_ops.br_list_recursive(
            root, include_deprecated=include_deprecated
        ):
            click.echo(f"{path}\t{bid}")
    else:
        for bid, scope, prev in spec_ops.br_list_flat(
            root, include_deprecated=include_deprecated
        ):
            click.echo(f"{bid}\t{scope}\t{prev}")


@br.command("read")
@click.option("--sid", "-s", "br_sid", default=None, help=_SID_HELP)
@click.option("--id", "br_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def br_read_cmd(ctx: click.Context, br_sid: str | None, br_dom_id: str | None) -> None:
    """Print the text body for one business rule."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    br_id = _sid_or_dom_id(
        root,
        br_sid,
        br_dom_id,
        label="business rule",
        from_dom=dom_resolve.br_sid_from_dom_id,
    )
    text = spec_ops.br_read(root, br_id)
    if text is None:
        raise click.ClickException(f"unknown br: {br_id}")
    click.echo(text)


@br.command("update")
@click.option("--sid", "-s", "br_sid", default=None, help=_SID_HELP)
@click.option("--id", "br_dom_id", default=None, help=_DOM_ID_HELP)
@click.option("--desc", "-d", default=None, help=_MARKDOWN_TEXT_HELP)
@click.option(
    "--deprecated/--not-deprecated",
    "deprecated_flag",
    default=None,
    help='Set or clear ``deprecated="true"``; omit to leave unchanged.',
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP + " Omit entirely to leave phases unchanged.",
)
@click.option("--clear-ph", "clear_ph", is_flag=True, help=_CLEAR_PH_HELP)
@click.pass_context
def br_update_cmd(
    ctx: click.Context,
    br_sid: str | None,
    br_dom_id: str | None,
    desc: str | None,
    deprecated_flag: bool | None,
    phase_sids: tuple[str, ...],
    clear_ph: bool,
) -> None:
    """Replace business rule text and/or deprecated flag (entity ``sid`` is fixed at add time)."""
    has_ph = clear_ph or _cli_explicit(ctx, "phase_sids")
    if desc is None and deprecated_flag is None and not has_ph:
        raise click.ClickException(
            "Provide --desc, --deprecated/--not-deprecated, --ph, and/or --clear-ph."
        )
    obj = ctx.obj
    path = _work(obj)
    try:
        with _mutating(path) as root:
            br_id = _sid_or_dom_id(
                root,
                br_sid,
                br_dom_id,
                label="business rule",
                from_dom=dom_resolve.br_sid_from_dom_id,
            )
            ph_payload: tuple[str, ...] | None = None
            if clear_ph:
                ph_payload = ()
            elif _cli_explicit(ctx, "phase_sids"):
                ph_payload = tuple(x.strip() for x in phase_sids if str(x).strip())
            out = spec_ops.br_update(
                root,
                br_id,
                desc,
                deprecated=deprecated_flag,
                phases=ph_payload,
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    if out is None:
        raise click.ClickException(f"unknown br: {br_id}")
    click.echo(f"updated {out}")


@br.command("delete")
@click.option("--sid", "-s", "br_sid", default=None, help=_SID_HELP)
@click.option("--id", "br_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def br_delete_cmd(ctx: click.Context, br_sid: str | None, br_dom_id: str | None) -> None:
    """Delete a business rule (wherever it appears in the tree)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        br_id = _sid_or_dom_id(
            root,
            br_sid,
            br_dom_id,
            label="business rule",
            from_dom=dom_resolve.br_sid_from_dom_id,
        )
        if not spec_ops.br_delete(root, br_id):
            raise click.ClickException(f"unknown br: {br_id}")
    click.echo(f"deleted {br_id}")


# --- def (glossary definitions; body-level only) ---


_DEF_WITH_SID_HELP = (
    "Optional definition sid: any unique string. "
    "Omit for auto def- + 8 lowercase hex digits."
)
_DEF_BODY_HELP = (
    "Definition body (Markdown). Synonyms: ``--desc``. Separate from ``--term`` (short label stored as "
    "``<span type=term>`` in the document). Max 500 chars; one term/definition per row."
)


@cli.group("def", invoke_without_command=True)
@click.pass_context
def def_cli(ctx: click.Context):
    """Definitions are a top-level glossary (terms and meanings grouped by section) so ACs and BRs share one vocabulary.

    List, add, read, update, and delete definition paragraphs under ``div type=definitions``."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@def_cli.command("add")
@click.option(
    "-d",
    "--desc",
    "--definition",
    "definition_body",
    required=True,
    help=_MARKDOWN_TEXT_HELP + " " + _DEF_BODY_HELP,
)
@click.option(
    "--section",
    "-S",
    required=True,
    help='Section heading for grouping (e.g. "Candidate states (used in metrics and ACs)").',
)
@click.option(
    "--term",
    "-t",
    default=None,
    help='Optional glossary term label (e.g. Invited); max 100 chars; rendered as <span type="term"> in the document.',
)
@click.option("--with-sid", "user_sid", default=None, help=_DEF_WITH_SID_HELP)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def def_add_cmd(
    ctx: click.Context,
    definition_body: str,
    section: str,
    term: str | None,
    user_sid: str | None,
    porcelain: bool,
) -> None:
    """Append a ``p type=definition`` under ``div type=definitions`` (created if missing)."""
    obj = ctx.obj
    path = _work(obj)
    ut = (user_sid or "").strip() or None
    try:
        with _mutating(path) as root:
            eid = spec_ops.def_add(
                root,
                definition_body,
                section=section,
                term=(term or "").strip() or None,
                user_sid=ut,
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_DEF, eid)
    if not porcelain:
        click.echo(f"added definition {eid}")


@def_cli.command("list")
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include definitions with deprecated=\"true\" (hidden by default).",
)
@click.pass_context
def def_list_cmd(ctx: click.Context, include_deprecated: bool) -> None:
    """List definitions: sid, section, term, preview."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    for sid, sec, tm, prev in spec_ops.def_list_flat(
        root, include_deprecated=include_deprecated
    ):
        term_col = tm if tm else ""
        click.echo(f"{sid}\t{sec}\t{term_col}\t{prev}")


@def_cli.command("read")
@click.option("--sid", "-s", "def_sid", default=None, help=_SID_HELP)
@click.option("--id", "def_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def def_read_cmd(
    ctx: click.Context, def_sid: str | None, def_dom_id: str | None
) -> None:
    """Print section, optional term, and body for one definition."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    did = _sid_or_dom_id(
        root,
        def_sid,
        def_dom_id,
        label="definition",
        from_dom=dom_resolve.def_sid_from_dom_id,
    )
    row = spec_ops.def_read(root, did)
    if row is None:
        raise click.ClickException(f"unknown definition: {did}")
    sec, tm, body = row
    click.echo(f"section:\t{sec}")
    click.echo(f"term:\t{tm}")
    click.echo(f"definition:\t{body}")


@def_cli.command("update")
@click.option("--sid", "-s", "def_sid", default=None, help=_SID_HELP)
@click.option("--id", "def_dom_id", default=None, help=_DOM_ID_HELP)
@click.option(
    "-d",
    "--desc",
    "--definition",
    "desc",
    default=None,
    help=_MARKDOWN_TEXT_HELP + " " + _DEF_BODY_HELP,
)
@click.option("--section", "-S", default=None, help="Replace section grouping.")
@click.option(
    "--term",
    "-t",
    default=None,
    help='Replace term label (<span type="term">); omit to leave unchanged.',
)
@click.option(
    "--clear-term",
    is_flag=True,
    help='Remove the term label (<span type="term"> or legacy attribute).',
)
@click.option(
    "--deprecated/--not-deprecated",
    "deprecated_flag",
    default=None,
    help='Set or clear ``deprecated="true"``; omit to leave unchanged.',
)
@click.pass_context
def def_update_cmd(
    ctx: click.Context,
    def_sid: str | None,
    def_dom_id: str | None,
    desc: str | None,
    section: str | None,
    term: str | None,
    clear_term: bool,
    deprecated_flag: bool | None,
) -> None:
    """Update definition text, section, term, and/or deprecated flag."""
    if (
        desc is None
        and section is None
        and term is None
        and not clear_term
        and deprecated_flag is None
    ):
        raise click.ClickException(
            "Provide at least one of --definition/--desc, --section, --term, --clear-term, "
            "--deprecated/--not-deprecated."
        )
    if clear_term and term is not None:
        raise click.ClickException("Use only one of --term and --clear-term.")
    obj = ctx.obj
    path = _work(obj)
    try:
        with _mutating(path) as root:
            did = _sid_or_dom_id(
                root,
                def_sid,
                def_dom_id,
                label="definition",
                from_dom=dom_resolve.def_sid_from_dom_id,
            )
            out = spec_ops.def_update(
                root,
                did,
                desc,
                section=section,
                term=None if clear_term else term,
                remove_term=clear_term,
                deprecated=deprecated_flag,
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    if out is None:
        raise click.ClickException(f"unknown definition: {did}")
    click.echo(f"updated {out}")


@def_cli.command("delete")
@click.option("--sid", "-s", "def_sid", default=None, help=_SID_HELP)
@click.option("--id", "def_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def def_delete_cmd(
    ctx: click.Context, def_sid: str | None, def_dom_id: str | None
) -> None:
    """Remove a definition from the spec."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        did = _sid_or_dom_id(
            root,
            def_sid,
            def_dom_id,
            label="definition",
            from_dom=dom_resolve.def_sid_from_dom_id,
        )
        if not spec_ops.def_delete(root, did):
            raise click.ClickException(f"unknown definition: {did}")
    click.echo(f"deleted {did}")


# --- tfm (term-fact-model ER diagram; body-level singleton) ---

_TFM_SOURCE_HELP = (
    "Mermaid erDiagram source for the term/fact model (plain text, not a fenced code block). "
    'Must start with "erDiagram". Entities are terms; relationship labels are facts.'
)
_TFM_WITH_SID_HELP = (
    "Optional term-fact-model sid: any unique string. "
    "Omit for auto tfm- + 8 lowercase hex digits."
)


@cli.group("tfm", invoke_without_command=True)
@click.pass_context
def tfm_cli(ctx: click.Context):
    """Term-fact model is a single body-level Mermaid ER diagram of terms (entities) and facts (relationships).

    Add, read, update, and delete the diagram under ``div type=term-fact-model``."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@tfm_cli.command("add")
@click.option(
    "-d",
    "--desc",
    "--diagram",
    "source",
    required=True,
    help=_TFM_SOURCE_HELP,
)
@click.option("--with-sid", "user_sid", default=None, help=_TFM_WITH_SID_HELP)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def tfm_add_cmd(
    ctx: click.Context,
    source: str,
    user_sid: str | None,
    porcelain: bool,
) -> None:
    """Create ``div type=term-fact-model`` with one Mermaid erDiagram paragraph."""
    obj = ctx.obj
    path = _work(obj)
    ut = (user_sid or "").strip() or None
    try:
        with _mutating(path) as root:
            eid = spec_ops.tfm_add(root, source, user_sid=ut)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_TFM, eid)
    if not porcelain:
        click.echo(f"added term-fact-model {eid}")


@tfm_cli.command("read")
@click.option("--sid", "-s", "tfm_sid", default=None, help=_SID_HELP)
@click.option("--id", "tfm_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def tfm_read_cmd(
    ctx: click.Context, tfm_sid: str | None, tfm_dom_id: str | None
) -> None:
    """Print the term-fact-model sid and erDiagram source."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    if tfm_sid or tfm_dom_id:
        tid = _sid_or_dom_id(
            root,
            tfm_sid,
            tfm_dom_id,
            label="term-fact-model",
            from_dom=dom_resolve.tfm_sid_from_dom_id,
        )
        row = spec_ops.tfm_read(root)
        if row is None or row[0] != tid:
            raise click.ClickException(f"unknown term-fact-model: {tid}")
        sid, src = row
    else:
        row = spec_ops.tfm_read(root)
        if row is None:
            raise click.ClickException("no term-fact-model in this spec")
        sid, src = row
    click.echo(f"sid:\t{sid}")
    click.echo(f"diagram:\t{src}")


@tfm_cli.command("update")
@click.option(
    "-d",
    "--desc",
    "--diagram",
    "source",
    required=True,
    help=_TFM_SOURCE_HELP,
)
@click.option("--sid", "-s", "tfm_sid", default=None, help=_SID_HELP)
@click.option("--id", "tfm_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def tfm_update_cmd(
    ctx: click.Context,
    source: str,
    tfm_sid: str | None,
    tfm_dom_id: str | None,
) -> None:
    """Replace the erDiagram source for the existing term-fact-model."""
    obj = ctx.obj
    path = _work(obj)
    tid: str | None = None
    if tfm_sid or tfm_dom_id:
        root_ro = _read_spec(path)
        tid = _sid_or_dom_id(
            root_ro,
            tfm_sid,
            tfm_dom_id,
            label="term-fact-model",
            from_dom=dom_resolve.tfm_sid_from_dom_id,
        )
    try:
        with _mutating(path) as root:
            out = spec_ops.tfm_update(root, source, tfm_id=tid)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    if out is None:
        raise click.ClickException(
            "no term-fact-model in this spec; use spectr tfm add first"
        )
    click.echo(f"updated {out}")


@tfm_cli.command("delete")
@click.option("--sid", "-s", "tfm_sid", default=None, help=_SID_HELP)
@click.option("--id", "tfm_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def tfm_delete_cmd(
    ctx: click.Context, tfm_sid: str | None, tfm_dom_id: str | None
) -> None:
    """Remove the term-fact-model section from the spec."""
    obj = ctx.obj
    path = _work(obj)
    tid: str | None = None
    with _mutating(path) as root:
        if tfm_sid or tfm_dom_id:
            tid = _sid_or_dom_id(
                root,
                tfm_sid,
                tfm_dom_id,
                label="term-fact-model",
                from_dom=dom_resolve.tfm_sid_from_dom_id,
            )
        if not spec_ops.tfm_delete(root, tid):
            if tid:
                raise click.ClickException(f"unknown term-fact-model: {tid}")
            raise click.ClickException("no term-fact-model in this spec")
    if tid:
        click.echo(f"deleted {tid}")
    else:
        click.echo("deleted term-fact-model")


# --- ac ---


@cli.group(invoke_without_command=True)
@click.pass_context
def ac(ctx: click.Context) -> None:
    """Acceptance criteria are verifiable “done” statements; they settle whether behavior meets intent.

    List, add, read, update, and delete AC nodes (top-level or under a use case)."""
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
        "Must contain Given, When, Then in that order exactly once each. "
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
@click.option(
    "--with-sid",
    multiple=True,
    default=(),
    help="For ac-…: " + _WITH_SID_ADD_HELP,
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP,
)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def ac_add_cmd(
    ctx: click.Context,
    desc: tuple[str, ...],
    under_uc: str | None,
    uc_node_id: str | None,
    pipe_uc: bool,
    with_sid: tuple[str, ...],
    phase_sids: tuple[str, ...],
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
    if with_sid and len(with_sid) != len(desc):
        raise click.ClickException("--with-sid must be omitted or repeated once per --desc.")
    # Load spec after resolving stdin so a producer in a pipe can finish writing.
    new_ids: list[str] = []
    try:
        with _mutating(path) as root:
            for text, ws in zip_longest(desc, with_sid, fillvalue=None):
                eid = spec_ops.ac_add(
                    root,
                    text,
                    under_uc_id=parent_uc,
                    user_sid=(ws.strip() if ws else None),
                    phases=tuple(x.strip() for x in phase_sids if str(x).strip()),
                )
                new_ids.append(eid)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    for eid in new_ids:
        _emit(porcelain, ids.PREFIX_AC, eid)
        if not porcelain:
            click.echo(f"added ac {eid}")


@ac.command("list")
@click.option("--recursive", "-r", is_flag=True)
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include items with deprecated=\"true\" (hidden by default).",
)
@click.pass_context
def ac_list_cmd(
    ctx: click.Context,
    recursive: bool,
    include_deprecated: bool,
) -> None:
    """List criteria (flat: scope column) or --recursive paths under ucs."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    if recursive:
        for path, aid in spec_ops.ac_list_recursive(
            root, include_deprecated=include_deprecated
        ):
            click.echo(f"{path}\t{aid}")
    else:
        for aid, scope, prev in spec_ops.ac_list_flat(
            root, include_deprecated=include_deprecated
        ):
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
@click.option("--desc", "-d", default=None, help=_MARKDOWN_TEXT_HELP)
@click.option(
    "--deprecated/--not-deprecated",
    "deprecated_flag",
    default=None,
    help='Set or clear ``deprecated="true"``; omit to leave unchanged.',
)
@click.option(
    "--ph",
    "phase_sids",
    multiple=True,
    default=(),
    help=_PH_ENTITY_HELP + " Omit entirely to leave phases unchanged.",
)
@click.option("--clear-ph", "clear_ph", is_flag=True, help=_CLEAR_PH_HELP)
@click.pass_context
def ac_update_cmd(
    ctx: click.Context,
    ac_sid: str | None,
    ac_dom_id: str | None,
    desc: str | None,
    deprecated_flag: bool | None,
    phase_sids: tuple[str, ...],
    clear_ph: bool,
) -> None:
    """Replace acceptance-criterion text and/or deprecated flag (entity ``sid`` is fixed at add time)."""
    has_ph = clear_ph or _cli_explicit(ctx, "phase_sids")
    if desc is None and deprecated_flag is None and not has_ph:
        raise click.ClickException(
            "Provide --desc, --deprecated/--not-deprecated, --ph, and/or --clear-ph."
        )
    obj = ctx.obj
    path = _work(obj)
    ac_id = ""
    try:
        with _mutating(path) as root:
            ac_id = _sid_or_dom_id(
                root,
                ac_sid,
                ac_dom_id,
                label="acceptance criterion",
                from_dom=dom_resolve.ac_sid_from_dom_id,
            )
            ph_payload: tuple[str, ...] | None = None
            if clear_ph:
                ph_payload = ()
            elif _cli_explicit(ctx, "phase_sids"):
                ph_payload = tuple(x.strip() for x in phase_sids if str(x).strip())
            out = spec_ops.ac_update(
                root,
                ac_id,
                desc,
                deprecated=deprecated_flag,
                phases=ph_payload,
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    if out is None:
        raise click.ClickException(f"unknown ac: {ac_id}")
    click.echo(f"updated {out}")


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


# --- qs ---


@cli.group(invoke_without_command=True)
@click.pass_context
def qs(ctx: click.Context) -> None:
    """Q&A threads record questions and answers on spec entities so ambiguity is resolved with auditable history.

    Ask, answer, list, deprecate, and delete Q&A items (author roles apply). The companion
    questions document next to the spec is created when it is missing or empty (zero bytes)."""
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
@click.option("--with-sid", "user_thread_sid", default=None, help=_QS_THREAD_WITH_SID_HELP)
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
    user_thread_sid: str | None,
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
    path = _questions_work(obj)
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

    ut = (user_thread_sid or "").strip() or None
    try:
        with _mutating(path) as root:
            qid = spec_ops.qs_ask(
                root,
                tid,
                qtext,
                author=author_resolved,
                target_role=target_role,
                user_sid=ut,
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
    path = _questions_work(obj)
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
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include threads whose question has deprecated=\"true\" (hidden by default).",
)
@click.pass_context
def qs_list_cmd(ctx: click.Context, include_deprecated: bool) -> None:
    """List questions: thread sid, context ref (e.g. parent uc sid), author, preview."""
    obj = ctx.obj
    qpath = _questions_work(obj)
    root = _read_spec(qpath)
    for qid, ref, auth, prev in spec_ops.qs_list(
        root, include_deprecated=include_deprecated
    ):
        click.echo(f"{qid}\t{ref or ''}\t{auth or ''}\t{prev}")


@qs.command("deprecate")
@click.option("--sid", "-s", "thread_sid", default=None, help="Question thread sid (q-…).")
@click.option(
    "--id",
    "question_dom_id",
    default=None,
    help="DOM id of a question or answer paragraph in that thread.",
)
@click.option(
    "--clear",
    is_flag=True,
    help="Clear deprecated=\"true\" instead of setting it.",
)
@click.pass_context
def qs_deprecate_cmd(
    ctx: click.Context,
    thread_sid: str | None,
    question_dom_id: str | None,
    clear: bool,
) -> None:
    """Set or clear the deprecated flag on a question thread (the ``p type=question`` element)."""
    obj = ctx.obj
    path = _questions_work(obj)
    with _mutating(path) as root:
        tid = _sid_or_dom_id(
            root,
            thread_sid,
            question_dom_id,
            label="question thread",
            from_dom=dom_resolve.qs_thread_sid_from_dom_id,
        )
        if not spec_ops.qs_set_deprecated(root, tid, deprecated=not clear):
            raise click.ClickException(f"unknown question thread: {tid}")
    click.echo(
        f"{'cleared deprecated on' if clear else 'marked deprecated'} {tid}"
    )


@qs.command("delete")
@click.option("--sid", "-s", "thread_sid", default=None, help="Question thread sid (q-…).")
@click.option(
    "--id",
    "question_dom_id",
    default=None,
    help="DOM id of a question or answer paragraph in that thread.",
)
@click.pass_context
def qs_delete_cmd(
    ctx: click.Context,
    thread_sid: str | None,
    question_dom_id: str | None,
) -> None:
    """Remove a question thread (question and answer paragraphs) from the spec."""
    obj = ctx.obj
    path = _questions_work(obj)
    with _mutating(path) as root:
        tid = _sid_or_dom_id(
            root,
            thread_sid,
            question_dom_id,
            label="question thread",
            from_dom=dom_resolve.qs_thread_sid_from_dom_id,
        )
        if not spec_ops.qs_delete(root, tid):
            raise click.ClickException(f"unknown question thread: {tid}")
    click.echo(f"deleted {tid}")


# --- feedback ---


@cli.group(invoke_without_command=True)
@click.pass_context
def feedback(ctx: click.Context) -> None:
    """Feedback stores unstructured review notes on the change set so stakeholders can comment outside formal Q&A.

    Use ``feedback add`` to append an entry or ``feedback delete`` to remove one (author roles apply)."""
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


@feedback.command("delete")
@click.option("--sid", "-s", "feedback_sid", default=None, help=_SID_HELP)
@click.option("--id", "feedback_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def feedback_delete_cmd(
    ctx: click.Context,
    feedback_sid: str | None,
    feedback_dom_id: str | None,
) -> None:
    """Remove one feedback paragraph by sid or DOM id."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        fid = _sid_or_dom_id(
            root,
            feedback_sid,
            feedback_dom_id,
            label="feedback",
            from_dom=dom_resolve.feedback_sid_from_dom_id,
        )
        if not spec_ops.feedback_delete(root, fid):
            raise click.ClickException(f"unknown feedback: {fid}")
    click.echo(f"deleted {fid}")


# --- task (delivery plan: li type=task) ---


_PH_HELP = (
    "Phase sid from `task list`: append under that phase. If it does not exist, a new phase "
    "is created using this ph-… sid and the task is added there. If omitted: use the last phase, "
    "or create one when none exist."
)


def _exec_task_add_auto(
    obj: dict,
    body: str,
    phase_sid: str | None,
    porcelain: bool,
    *,
    user_task_sid: str | None = None,
    user_phase_sid: str | None = None,
) -> None:
    path = _work(obj)
    try:
        with _mutating(path) as root:
            eid = phase_ops.task_add_auto(
                root,
                body,
                phase_sid=phase_sid,
                user_task_sid=user_task_sid,
                user_phase_sid=user_phase_sid,
            )
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    _emit(porcelain, ids.PREFIX_TASK, eid)
    if not porcelain:
        click.echo(f"added task {eid}")


@cli.group("task", invoke_without_command=True)
@click.pass_context
def task_cli(ctx: click.Context) -> None:
    """Tasks (and phases) are the delivery plan: ordered work to implement and ship the change set.

    List, add, and delete tasks; missing plan markup is created as needed."""
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


@task_cli.command("delete")
@click.option("--sid", "-s", "task_sid", default=None, help=_SID_HELP)
@click.option("--id", "task_dom_id", default=None, help=_DOM_ID_HELP)
@click.pass_context
def task_delete_cmd(
    ctx: click.Context,
    task_sid: str | None,
    task_dom_id: str | None,
) -> None:
    """Remove a task from the delivery plan (empty phases and plan wrappers are pruned)."""
    obj = ctx.obj
    path = _work(obj)
    with _mutating(path) as root:
        tid = _sid_or_dom_id(
            root,
            task_sid,
            task_dom_id,
            label="task",
            from_dom=dom_resolve.task_sid_from_dom_id,
        )
        if not phase_ops.task_delete(root, tid):
            raise click.ClickException(f"unknown task: {tid}")
    click.echo(f"deleted {tid}")


@task_cli.command("add")
@click.option("--desc", "-d", "body", required=True, help=_MARKDOWN_TEXT_HELP)
@click.option("--ph", "phase_sid", default=None, help=_PH_HELP)
@click.option("--with-sid", "user_task_sid", default=None, help=_TASK_WITH_SID_HELP)
@click.option(
    "--phase-with-sid",
    "user_phase_sid",
    default=None,
    help=_TASK_PHASE_WITH_SID_HELP,
)
@click.option("--porcelain", "-p", is_flag=True)
@click.pass_context
def task_add_delivery_cmd(
    ctx: click.Context,
    body: str,
    phase_sid: str | None,
    user_task_sid: str | None,
    user_phase_sid: str | None,
    porcelain: bool,
) -> None:
    """Append a task; creates plan/phases with auto sids when needed. ``--ph`` targets a phase by sid or creates one."""
    ut = (user_task_sid or "").strip() or None
    up = (user_phase_sid or "").strip() or None
    _exec_task_add_auto(
        ctx.obj,
        body,
        phase_sid,
        porcelain,
        user_task_sid=ut,
        user_phase_sid=up,
    )


# --- ph (requirements ↔ delivery phases) ---


@cli.group("ph", invoke_without_command=True)
@click.pass_context
def ph_cli(ctx: click.Context) -> None:
    """Requirements (UC, BR, AC) may list phase sids in optional ``ph``; list them per phase here."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@ph_cli.command("list")
@click.argument("phase_sid")
@click.pass_context
def ph_list_cmd(ctx: click.Context, phase_sid: str) -> None:
    """Print UC/BR/AC rows whose ``ph`` attribute includes *phase_sid* (tab: kind, sid, scope, preview)."""
    obj = ctx.obj
    root = _read_spec(_work(obj))
    want = (phase_sid or "").strip()
    if not want:
        raise click.ClickException("phase_sid must be non-empty")
    rows = spec_ops.requirements_list_for_phase(root, want)
    if not rows:
        click.echo(f"(no requirements for phase {want!r})")
        return
    for kind, sid, scope, prev in rows:
        click.echo(f"{kind}\t{sid}\t{scope}\t{prev}")


# --- uow (multi-command session) ---


@cli.group("uow", invoke_without_command=True)
@click.pass_context
def uow_group(ctx: click.Context) -> None:
    """A unit of work is a short-lived draft of the spec: batch many CLI edits, then commit once to the spec file.

    ``begin`` → mutating subcommands (draft) → ``commit`` or ``abort``; ``status`` shows session state."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@uow_group.command("begin")
@click.pass_context
def uow_begin_cmd(ctx: click.Context) -> None:
    """Start a session: copy the spec to a draft under ``.spectr/``; later commands edit that draft."""
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


@cli.command("serve")
@click.option(
    "--bind",
    "-b",
    "bind_host",
    default="127.0.0.1",
    metavar="ADDR",
    help="Interface to bind (default 127.0.0.1).",
)
@click.option(
    "--port",
    "-p",
    "port",
    default=8765,
    type=int,
    help="TCP port (default 8765).",
)
def serve_cmd(bind_host: str, port: int) -> None:
    """Serve files from the current working directory over HTTP.

    Spectr specification documents open in a wrapper page with an iframe;
    chrome CSS/JS lives on the wrapper; typography CSS is applied inside the iframe.
    Append ``?spectr-raw=1`` to load the spec document alone (no wrapper)."""
    if not (1 <= port <= 65535):
        raise click.ClickException("port must be between 1 and 65535")
    from spectr.serve import run_serve

    run_serve(Path.cwd(), bind_host, port)


def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
