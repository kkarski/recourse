---
name: use-spectr
description: Use when creating or updating Spectr feature specifications from the terminal (spectr CLI / spectr/src/spectr/cli.py), piping entity sids between commands, using uow begin/commit/abort for batched edits, configuring author roles for Q&A or feedback, or storing Markdown (including code fences and example snippets) in specification bodies.
---

# use-spectr

## Overview

**Spectr** is a CLI for **software specifications** for new features. A spec holds **use cases**, **acceptance criteria**, **tests** (under ACs), optional **planning** (phases / tasks), and **Q&A** plus **feedback** so pm, architect, engineer, qa refine requirements in one place.

**Principle:** Prefer the CLI for structural edits; defer flags and edge cases to `spectr --help` and `spectr <group> --help`.

## When to Use

- Bootstrap or extend a feature spec (use cases → ACs → tests → plan).
- Post questions, answers, or feedback with an **author role** (`--author` or default role chain).
- Chain commands with **porcelain** (`-p`) and stdin (`--uc -`, `qs ask --pipe-id`).
- Batch many structural edits then **one** write to disk with **`uow begin` → … → `uow commit`** (or `uow abort`).
- Put **Markdown** in description-style fields; code fences and literal `<`/`>`/`&` in examples are stored safely (escaped on save).

**Skip:** Unstructured one-off prose with no spec model; bulk changes that belong in a script or migration.

## Quick Reference

| Group | Actions |
|-------|---------|
| `init` | New folder + default spec file |
| `uc` | `add`, `list`, `read`, `update`, `delete` |
| `ac` | `add` (repeat `--desc`), `list`, `read`, `update`, `delete` |
| `test` | `add` (needs `--ac`), `read`, `update`, `delete` |
| `qs` | `ask`, `answer`, `list` |
| `feedback` | `add` |
| `task` | `add -d '…'` (optional `--ph`: match phase sid from `task list`, or create a new auto `ph-…` phase if no match), `list` (`--ph` filters) |
| `export` | `markdown`, `json` |
| `conf` | `set`, `show` (default author role) |
| `uow` | `begin`, `commit`, `abort`, `status` (multi-command edit session; see below) |

**Globals:** `--spec` (path to `spec.html`; default: walk **upward** from cwd), `-r` / `--role` (default author on **qs** and **feedback add** only). Env: **`SPECTR_SPEC`** overrides default spec path.

**Entity `sid`:** Stable identifiers: once set, they are **not** rewritten on load. New elements get auto `prefix-{uuid8}` sids (see `spectr.ids`). Only **missing/blank** sids are filled when a spec is loaded. `--ph` targets an existing phase sid, or Spectr creates a new auto `ph-…` phase if there is no match.

## Roles

Only **`qs ask`**, **`qs answer`**, **`feedback add`** use author. Default role order: subcommand `--role` → global `--role` → `SPECTR_ROLE` → `spectr conf set`. Per-message override: **`--author` / `-a`**.

## Piping

`-p` prints `kind` + tab + entity **`sid`**. `ac add --uc -` reads uc sid from stdin. Use the **same `--spec`** on both sides of a pipe when discovery could differ. During an open **uow** session, reads/exports see the draft (see Unit of work).

## Markdown

`--desc`, questions, answers, feedback, and plan task bodies accept Markdown. Details: **`spectr --help`** (section “Markdown in descriptions”).

## Common Mistakes

| Issue | Fix |
|-------|-----|
| Wrong file after `cd` | `--spec` or `SPECTR_SPEC` |
| Pipe id mismatch | Same `--spec`; follow `-p` / `--uc -` pattern |
| Role ignored on `uc`/`ac` | Role only for `qs` / `feedback`; use `--author` there |
| Treating work as “raw XML” | Edit the **specification** via Spectr; avoid hand-tag editing |

## Invoke the CLI

Implementation lives in **`spectr/src/spectr/cli.py`** (Click app: `cli` group, `main()` entrypoint). Use it in one of these ways:

1. **Installed package** (recommended): from the `spectr` directory with your venv active, `pip install -e .`, then run **`spectr`** on your `PATH`.
2. **Module**: from a cwd where the package resolves (e.g. repo root with `spectr` on `PYTHONPATH`, or after install), **`python -m spectr`** … same subcommands as `spectr`.
3. **Dev tree, no install**: run **`python spectr/src/spectr/cli.py`** (or make `cli.py` executable and run it directly). The file prepends `spectr/src` to `sys.path` so the `spectr` package loads without an editable install.

Pass **`--help`** on the top-level command or any group (e.g. `spectr uc --help`) for flags and arguments.

## Unit of work (`uow`)

By default, each mutating subcommand is its own short transaction (clone → edit → renumber DOM `id` → write **`spec.html`**). For **several edits with a single final write**, use a session:

| Command | Effect |
|---------|--------|
| **`spectr uow begin`** | Copies the canonical spec to **`<spec-dir>/.spectr/uow-draft.html`** and records an active session for that resolved **`--spec`**. |
| *(any mutating commands)* | They update the **draft** only (same `--spec` as `begin`). |
| **`spectr uow commit`** | Merges the draft into the real spec (id renumbering), removes the session. |
| **`spectr uow abort`** | Discards the draft; canonical file unchanged. |
| **`spectr uow status`** | Prints whether a session is active and where the draft lives. |

**Rules:** Use the **same** `--spec` (or discovery / `SPECTR_SPEC`) for `begin`, every command in the session, and `commit` / `abort` / `status`. While a session is open, **reads and exports** use the draft so you see uncommitted work. Stable references in scripts and pipes use entity **`sid`**, not fragment **`id`**.

**Examples:**

```bash
spectr --spec ./My_Feature/spec.html uow begin
spectr --spec ./My_Feature/spec.html uc add -t "Title" -d "Body"
spectr --spec ./My_Feature/spec.html task add -d "Do the thing"
spectr --spec ./My_Feature/spec.html task list
spectr --spec ./My_Feature/spec.html task add -d "Phase-specific" --ph ph-xxxxxxxx
spectr --spec ./My_Feature/spec.html export markdown
spectr --spec ./My_Feature/spec.html uow commit
```
