---
name: using-spectr
description: Spectr CLI workflows for software feature specs (use cases, ACs, planning, Q&A). Use when creating or updating Spectr specs; summarizing or inspecting spec content. Apply this skill with the Spectr CLI (`spectr` or `python -m spectr`); prefer deprecation over delete for obsolete requirements; refuse wrapper scripts; read via CLI (`list`, `read`, and related inspect commands in this skill) or a team-maintained Markdown `.md` file as the primary read surface—not the on-disk spec source; batch structural edits with uow; porcelain piping between commands; Markdown bodies with code fences; author roles on qs or feedback. When authoring def/br/ac bodies, follow repository reference docs (RuleSpeak, rules vs ACs, terms)—see skill body; do not improvise vocabulary or policy layout.
---

# using-spectr

## Overview

**Spectr** is a CLI for structured software specifications: use cases, acceptance criteria, business rules, optional delivery planning, Q&A, and feedback.

- You MUST use the CLI (`spectr` or `python -m spectr`) for spec edits.
- You MUST run `spectr --help` and `spectr <group> --help` for flags and edge cases.
- You MUST use `list` and `read` (and group-specific reads such as `spec read`) as your primary read surfaces.
- You MUST NOT treat the on-disk spec source file as the primary source for analysis; use CLI output or a team-maintained `.md` companion (e.g. under `specs/{feature}/`) when one exists (see **Reading via CLI** / **Quick Reference** below).
- You MUST use one logical AC/BR/Q&A item per entity `sid`.
- You MUST use one glossary term definition per `def` row.
- You MUST expect auto-assigned `sid` values to use `{prefix}-` plus 8 lowercase hex digits.
- You MAY use any non-empty custom `sid` with `--with-sid`; you MUST NOT impose a required `uc-`/`ac-`/`br-` pattern.
- You MUST treat `--with-sid` as optional.
- You SHOULD use `--with-sid` only when the `sid` is already defined or explicitly mentioned in the content being added or updated.

## Follow repository guidance (mandatory)

Spectr defines structure, not policy quality. You MUST follow repository writing conventions while using Spectr commands.

### Required read sequence before bulk edits

1. You MUST identify which entities you are changing (`def`, `br`, `ac`).

### Non‑negotiables

- You MUST define vocabulary before policy: add/update `def` first, then reuse exact term labels in `br`.
- You MUST NOT introduce conflicting synonyms or shorthand for glossary terms.
- You MUST NOT replace normative prose with telegraphic bullets, arrows, or bare "cannot" phrasing where RuleSpeak is required.
- You MUST keep one logical rule per `br` row in normal practice.
- You MUST NOT use `br` for definitions or AC scenario text.
- You MUST state obligations/prohibitions explicitly; you MUST NOT rely on `(ACxx)` references as a substitute.
- You MAY include implementation details in ACs/constraints, but you MUST keep business-rule language policy-first.
- You MUST treat unstructured `br` dumps, multi-term `def` rows, and reference-free translation work as incorrect and fix them before completion.

## When to Use

- You MUST use this workflow when bootstrapping or extending a feature spec.
- You MAY use role-aware Q&A
- You MAY chain porcelain output (`-p`) and stdin handoff (`--uc -`, `qs ask --pipe-id`).
- You MUST use `uow` for batched edits that should commit atomically.
- You MAY use Markdown in `--desc`, Q&A, feedback, and task bodies.
- You MUST NOT use this workflow for unstructured prose with no spec model.
- You MUST NOT build custom wrappers for migrations that belong in repo tooling/CI.

## Reading via CLI

1. You MUST use `spectr <group> list` to enumerate entities; you MAY include `--include-deprecated` where supported.
2. You MUST use `spectr <group> read --sid ...` or `--id ...` for single-entity inspection.
3. You MUST remember that CLI reads resolve to the draft during `uow`.

## Quick Reference

- You MUST treat `spectr` as the root command for all spec operations.
- You MUST use `feature` to add a new feature specification
- You MUST use `spec` to manage the change-set overview description.
- You MUST use `uc` for use cases.
- You MUST use `ac` for acceptance criteria.
- You MUST use `br` for business rules.
- You MUST use `def` for glossary terms.
- You MUST use `qs` for auditable question/answer threads.
- You MAY use `task` for delivery planning (phases/tasks).
- You MAY use `--ph` to attach tasks to an existing phase `sid`.
- You MAY use `--phase-with-sid` and `--with-sid` where supported.
- You MAY use `conf` to manage default author settings.
- You MUST use `uow` for batched draft-then-commit changes.

## Roles

- You MUST apply role/author options only to `qs ask`, `qs answer`, and `feedback add`.
- You MUST resolve role precedence in this order: subcommand `--role` -> global `--role` -> `SPECTR_ROLE` -> `spectr conf set`.
- You MAY set per-message author metadata with `--author` / `-a`.

## Piping

- You MAY emit porcelain output with `-p` (`kind<TAB>sid`).
- You MAY pass `sid` through stdin (for example `ac add --uc -`).
- You MUST set the same `--spec` on both sides of a pipe.

## Markdown

- You MAY use Markdown in `--desc`, Q&A, feedback, and task bodies.
- You MUST expect literal text to be escaped on save.

## Deprecation (UC, AC, BR, Q&A)

- You MUST prefer deprecation over deletion for obsolete but historically relevant content.
- You MUST use `--not-deprecated` or `qs deprecate --clear` to restore when needed.
- You MUST remember that deprecated rows are hidden from default list output.
- You MAY use `--include-deprecated` to list hidden rows.

### Deprecation flow

1. You MUST identify the correct entity `sid`.
2. You MUST deprecate via entity update (`uc/ac/br`) or `qs deprecate`.
3. You MUST verify visibility behavior with `list` and optional `--include-deprecated`.
4. You MAY clear deprecation when restoring scope.

```bash
spectr uc update -s uc-onboarding-v2 --deprecated
spectr uc update -s uc-onboarding-v2 --not-deprecated
spectr ac update -s AC13 --deprecated
spectr ac update -s AC13 --not-deprecated
spectr br update -s br-owner_edits_only --deprecated
spectr br update -s br-owner_edits_only --not-deprecated
spectr qs deprecate -s q-herwfsdx
spectr qs deprecate -s q-herwfsdx --clear
spectr qs list --include-deprecated
```

## `sid` assignment, updates, and delete policy

- You MUST treat `--with-sid` as optional and pass full IDs when used.
- You MUST ensure custom `sid` values are non-empty and unique among entity `sid` values.
- You MUST enforce uniqueness only against other entity `sid` values; fragment `id` values do not block reuse.
- You MUST keep one `--with-sid` per `--desc` item for multi-row `ac add` / `br add`.
- You MUST treat entity `sid` as stable after creation.
- You SHOULD use `--with-sid` only when the `sid` is already defined or explicitly mentioned in the content being added or updated.
- You MUST treat delete as a last resort after evaluating deprecation.

```bash
spectr uc add -t "Import spreadsheet" -d "User uploads a file for parsing."
spectr ac add --uc import-13 \
  -d "Reject rows missing a primary key column."
spectr ac add --uc import-13 \
  -d "AC7a: Return visit honors prior verification when eligible." \
  --with-sid AC7a
spectr br add --uc import-13 \
  -d "Only owners may edit catalog rows."
  -d "Uploaded files are scanned for malware before parse."
spectr uc add -t "AC-27: Legacy flow" -d "Kept for comparison." --with-sid AC-27
```

- You MUST use `-s` / `--sid` (or `--id` where supported) for updates and deletes.
- You MUST remember entity `sid` values are fixed at add time.
- You MUST use `qs deprecate` for Q&A thread retirement.

```bash
spectr ac update -s ac-schema.pk_required -d "Reject rows missing any required column, not only PK."
spectr br update -s br-owner_edits_only -d "Editors must hold catalog-admin role." --deprecated
spectr uc update -s uc-import-v3 -t "Import spreadsheet" -d "Covers CSV and XLSX upload."
```

- You MUST delete only for mistaken additions, structural cleanup, or intentional purge.
- You MUST NOT delete merely to represent obsolete scope when deprecation is appropriate.

```bash
spectr ac delete -s ac-schema.pk_required
spectr br delete -s br-owner_edits_only
spectr uc delete -s import-13
```

## Unit of work (`uow`)

You MUST use this sequence for batch changes that should persist together:

1. You MUST run `spectr uow begin`.
2. You MUST perform all mutations against the same spec target.
3. You MAY inspect draft state with CLI reads or `spectr uow status`.
4. You MUST run `spectr uow commit` to persist changes, or `spectr uow abort` to discard.
5. You MUST remember that CLI reads target the draft while `uow` is open.

```bash
spectr uow begin
spectr uc add -t "Title" -d "Body"
spectr task add -d "Do the thing"
spectr task list
spectr task add -d "Phase-specific" --ph ph-mvp
spectr uow commit
```

## Invoke the CLI

- You MUST run `spectr` or `python -m spectr` directly.
- You MUST navigate to the feature's directory before issuing commands
- You MUST NOT create maintained wrapper scripts that drive Spectr commands.
- You MAY use command pipes between Spectr invocations.

## Common Mistakes

1. You MUST NOT hand-edit the specification source; use the **Spectr CLI** and follow **`using-spectr`**.
2. You MUST NOT apply role options to `uc`/`ac`; you MUST apply author/role metadata only to `qs` and `feedback`.
3. You MUST NOT combine many ACs/BRs into one `--desc` blob; you MUST repeat `-d` or split commands.
4. You MUST NOT combine multiple terms in one `def` row.
5. You MUST NOT write mega-`br` blobs without normative prose.
6. You MUST align `br` wording with glossary terms.
7. You MUST NOT use `ACxx` citations as a replacement for actual obligations.
