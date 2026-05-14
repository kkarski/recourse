# Spectr CLI for Product Manager Role

Use this guide for PM-facing Spectr operations only. It intentionally omits engineering-only or low-relevance commands.

## Core Rules

1. You MUST use Spectr CLI (or `python -m spectr`) for structured spec work.
2. You MUST read and inspect via CLI output (`list`, `read`, and related commands below) or a team-maintained Markdown file (e.g. `specs/{feature}/{feature}_spec.md`), not by opening the on-disk spec source file directly. Follow **`using-spectr`** for read surfaces and conventions.
3. You MUST prefer deprecation over deletion for obsolete requirements.
4. You MUST batch multi-step edits with `uow` when making topic-level updates.

## Commands You Should Use

### 1) Initialize or Open Spec Context

Use when you are starting a new feature spec or confirming the active spec context.

```bash
spectr init
spectr spec read
```

### 2) Read Current State Before/After Edits

Use when you need a reliable view for elicitation, review, reconciliation, or summary.

```bash
spectr spec read
spectr def list
spectr uc list
spectr br list
spectr ac list
spectr qs list
```

Use targeted `spectr <group> read -s …` (or `--id …`) for single-entity inspection per **`using-spectr`**. When the team keeps a companion **`specs/{feature}/{feature}_spec.md`**, you may use it alongside CLI reads.

### 3) Capture Scope Narrative

Use when updating the change-set description and feature framing.

```bash
spectr spec update -d "Updated scope and context"
```

### 4) Manage Definitions First

Use before writing or updating BRs/ACs that depend on terminology.

```bash
spectr def add --section "Domain Terms" --term "Eligible Record" --definition "..."
spectr def update -s def-xxxxxxx --definition "..."
spectr def read -s def-xxxxxxx
```

### 5) Maintain Use Cases

Use when creating or refining actor journeys and flow narratives.

```bash
spectr uc add -t "Use case title" -d "Main and alternate flows"
spectr uc update -s uc-xxxxxxx -t "Updated title" -d "Updated flow narrative"
spectr uc read -s uc-xxxxxxx
```

### 6) Maintain Business Rules

Use when adding or updating RuleSpeak policy statements.

```bash
spectr br add --uc uc-xxxxxxx -d "System must ..."
spectr br update -s br-xxxxxxx -d "Updated policy text"
spectr br read -s br-xxxxxxx
```

### 7) Maintain Acceptance Criteria

Use when adding or updating verifiable outcomes that trace to BRs.

```bash
spectr ac add --uc uc-xxxxxxx -d "Verifies BR N: ..."
spectr ac update -s ac-xxxxxxx -d "Updated criterion"
spectr ac read -s ac-xxxxxxx
```

### 8) Manage Requirement Q&A Threads

Use during elicitation and clarification cycles with the user/architect.

```bash
spectr qs ask --entity br-xxxxxxx -d "Clarifying question?"
spectr qs answer -s q-xxxxxxx -d "Answer text"
spectr qs list
```

### 9) Batch Topic-Level Edits (Unit of Work)

Use when applying several related edits and committing once.

```bash
spectr uow begin
# run def/uc/br/ac/spec edits
spectr uow status
spectr uow commit
```

Use `spectr uow abort` to discard draft changes.

### 10) Deprecate Obsolete Requirements

Use when requirements are superseded or out of scope but must remain traceable.

```bash
spectr uc update -s uc-xxxxxxx --deprecated
spectr br update -s br-xxxxxxx --deprecated
spectr ac update -s ac-xxxxxxx --deprecated
spectr qs deprecate -s q-xxxxxxx
```

## Out of Scope for This PM Reference

This document intentionally omits non-PM-centric commands and advanced CLI mechanics. For PM work, use only the command set above unless explicitly required by the user.
