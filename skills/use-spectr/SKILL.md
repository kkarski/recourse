---
name: use-spectr
description: Use when creating or updating Spectr feature specifications from the terminal, piping entity ids between commands, configuring author roles for Q&A or feedback, or storing Markdown (including code fences and example snippets) in specification bodies.
---

# use-spectr

## Overview

**Spectr** is a CLI for **software specifications** for new features. A spec holds **use cases**, **acceptance criteria**, **tests** (under ACs), optional **planning** (phases / tasks / refs), and **Q&A** plus **feedback** so pm, architect, engineer, qa refine requirements in one place.

**Principle:** Prefer the CLI for structural edits; defer flags and edge cases to `spectr --help` and `spectr <group> --help`.

## When to Use

- Bootstrap or extend a feature spec (use cases → ACs → tests → plan).
- Post questions, answers, or feedback with an **author role** (`--author` or default role chain).
- Chain commands with **porcelain** (`-p`) and stdin (`--uc -`, `qs ask --pipe-id`).
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
| `plan` | `phase-add`, `task-add`, `ac-ref`, `test-ref` |
| `export` | `markdown`, `json` |
| `conf` | `set`, `show` (default author role) |

**Globals:** `--spec` (main spec file, often `spec.xml`), `--phase` (plan phase doc, often `step.xml` / `plan/step.xml`), `-r` / `--role` (default author on **qs** and **feedback add** only). Omitted paths: search **upward** from cwd; `SPECTR_SPEC` / `SPECTR_PHASE` override.

## Roles

Only **`qs ask`**, **`qs answer`**, **`feedback add`** use author. Default role order: subcommand `--role` → global `--role` → `SPECTR_ROLE` → `spectr conf set`. Per-message override: **`--author` / `-a`**.

## Piping

`-p` prints `kind` + tab + `id`. `ac add --uc -` reads uc id from stdin. Use the **same `--spec`** (and `--phase` if needed) on both sides of a pipe when discovery could differ.

## Markdown

`--desc`, questions, answers, feedback, and plan task bodies accept Markdown. Details: **`spectr --help`** (section “Markdown in descriptions”).

## Common Mistakes

| Issue | Fix |
|-------|-----|
| Wrong file after `cd` | `--spec` / `--phase` or env vars |
| Pipe id mismatch | Same `--spec`; follow `-p` / `--uc -` pattern |
| Role ignored on `uc`/`ac` | Role only for `qs` / `feedback`; use `--author` there |
| Treating work as “raw XML” | Edit the **specification** via Spectr; avoid hand-tag editing |

## Invoke

`pip install -e .` in the `spectr` project (venv on), then **`spectr`**. Alternatives: **`python -m spectr`**, **`./spectr/src/spectr/cli.py`**.
