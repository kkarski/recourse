---
name: review-design
description: Reviews code and design for the architecture and code-quality failures that recur most in practice — misplaced behavior, duplicated or redundant concepts, needless code and abstractions, fat entry points, leaky boundaries, and weak naming. Use when the user requests a code review, design review, architecture review, or refactor assessment, or asks whether something is needed, duplicated, or correctly placed before merge.
disable-model-invocation: true
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/track-edits.sh"
  Stop:
    - hooks:
        - type: command
          command: "./scripts/trigger-design-review.sh"
---

# Review Design

## Overview

Review changed code (and its immediate callers) for recurring architecture and code-quality failures. Findings first, ordered by severity. Do not implement fixes unless asked.

**Good review output**: numbered findings with file/line references, each tagged Critical / Major / Minor, each stating the rule violated and what good looks like.

**You MUST** read the project's architecture docs and coding standards, and search for existing implementations, before judging new code.

The priorities below are ordered by how often they are the real problem. Work top-down.

## Lifecycle hooks

Hooks are defined in this skill's frontmatter and run only while this skill is active.

1. **`PostToolUse` (`Edit|Write`)** — records that the session edited files.
2. **`Stop`** — if edits were recorded and `stop_hook_active` is false, blocks stopping with a reason to run this review first; on the next stop (after review), allows completion and clears state.

Invoke `/review-design` before implementation work when you want the post-edit review gate.

---

## Priority 1 — Put behavior on the data that owns it

**You MUST** place logic on the type that holds the data it operates on, so data and behavior live together.

**You MUST NOT** leave free-standing functions that take an object only to read its fields and compute a result (feature envy) — move them onto that object.

**You MUST NOT** accept a class as "object-oriented" just because functions were moved inside it; it must model a real concept with identity, invariants, and cohesive behavior.

**You MAY** keep a standalone function only when it is pure, has no natural owner, and you state why.

**Example — bad**: `TaxCalculator.compute(order)` reaches into `order` to sum line items.
**Example — good**: `order.totalWithTax()` — the order computes its own total.

---

## Priority 2 — Reuse and extend existing concepts before adding new ones

**You MUST** map a new requirement onto existing domain types and extend them when the concept already exists.

**You MUST NOT** introduce a parallel concept for a fact the model already represents.

**You MUST** call out, in any new design, which concepts are reused/extended and which are genuinely new.

**Example — bad**: add `CompletionRecord` when `Verification` already captures the same outcome.
**Example — good**: extend `Verification` with the new state and reference it.

---

## Priority 3 — Challenge necessity; remove dead and speculative code

**You MUST** ask "what calls this, and what breaks if it is deleted?" for every new endpoint, class, abstraction, and parameter.

**You MUST** flag code that exists only in case it is needed later, or that wraps something already callable, as removable.

**You MUST NOT** approve an abstraction (facade, builder, manager, indirection layer) that has one caller and adds no behavior.

**You MAY** keep speculative seams when an imminent, documented requirement needs them.

**Example — bad**: `OrderFacade` whose every method forwards to `OrderService`; a delete endpoint nothing calls.
**Example — good**: callers use `OrderService` directly; the unused endpoint is removed.

---

## Priority 4 — Keep entry points thin

**You MUST** keep controllers, handlers, and CLI commands to: parse input → delegate to a domain type or service → map output.

**You MUST NOT** add private helper functions to a controller file when an existing domain type or service should own that logic.

**You MUST NOT** put multi-repository branching in a controller; collapse it into a typed command with one `execute()`.

**You MAY** keep a handler with up to ~15 lines of non-boilerplate logic.

**Example — bad**: `OrderController` has 40 lines choosing a repository from request shape.
**Example — good**: `CreateOrderCommand.from(request).execute()` — the handler is three lines.

---

## Priority 5 — One implementation per concept (DRY)

**You MUST NOT** duplicate the same logic across handlers, or expose two code paths for one operation that must stay identical.

**You MUST NOT** register the same API surface from two modules with different behavior.

**You MUST NOT** add a method that differs from an existing one only by name (a rename-only wrapper).

**You MAY** extract shared behavior onto the owning type or a single service when call sites need identical semantics.

**Example — bad**: export logic copied into the verifications path instead of reusing the invites path.
**Example — good**: both call one `Exporter` with the same output contract.

---

## Priority 6 — Cut indirection and file sprawl

**You MUST NOT** split a workflow into many single-method passthrough types that add layers without behavior.

**You MUST** consolidate thin wrappers and one-line methods onto the type that owns the workflow, reducing file count.

**You MAY** keep a small type only when it carries state, enforces an invariant, or groups three or more related operations.

**Example — bad**: `Storage`, `Registry`, `Scheduler`, `PhaseService` each with one method.
**Example — good**: one `Pipeline` owns orchestration; step state lives on the job object.

---

## Priority 7 — One responsibility per type (cohesion)

**You MUST** keep each type focused on a single concept and reason to change.

**You MUST NOT** pollute a core data type with unrelated concerns (e.g. presentation/rendering logic on a domain state object).

**You MUST** move borrowed concerns to the type that owns them.

**Example — bad**: `SessionData` gains page-layout and copy-rendering helpers.
**Example — good**: a `PageView` type owns rendering; `SessionData` holds session state only.

---

## Priority 8 — Name for what things are

**You MUST** choose names that reveal purpose and content, and match the conventions of sibling modules.

**You MUST** make shared/generic components generically named, and specific components specifically named — not the reverse.

**You MUST** make async/job/task identifiers reveal what is being processed.

**Example — bad**: a reusable store named `ExportFileService`; a queued task named `task-001`.
**Example — good**: `JobFileStorage` (reusable); `export-invoices-{jobId}` (says what runs).

---

## Priority 9 — Keep boundaries clean

**You MUST** keep shared infrastructure (HTTP clients, publishers, generic runners) free of domain-specific names, branches, and error text.

**You MUST** pass typed query/command objects across layers, not untyped maps of arbitrary keys.

**You MUST NOT** expose internal mechanics to consumers (batch sizes, phase names, storage key formats, embedding dimensions).

**Example — bad**: `HttpClient` contains `if (type === "invoice")` branches; a filter passed as an untyped map.
**Example — good**: `HttpClient.post(url, body)` is generic; filters are a typed `Query` object.

---

## Priority 10 — Separate commands from queries

**You MUST** keep reads (GET, queries, list endpoints) free of side effects unless the spec documents otherwise.

**You MUST NOT** persist, reconcile, or lazily create state inside a read.

**You MUST** route reads through the read path (read replica / read model / query service) when one exists, and keep writes, locks, and read-after-write on the primary in one transaction.

**Example — bad**: `GET /users/{id}/profile` creates the profile when missing.
**Example — good**: `GET` returns current state; a `POST` or background job does the creation.

---

## Priority 11 — Make async work consistent and idempotent

**You MUST** follow the project's established async pattern (stages, status tracking, idempotent handlers) and use the platform's retry semantics instead of long blocking polls in request handlers.

**You MUST** make handlers idempotent: emit an event once, dedupe by id, and never re-enqueue or re-create work that already exists.

**You MUST NOT** return success from a job handler that did no work, or leave a lock or job in a non-terminal state.

**Example — bad**: a step re-enqueues an existing task and emits a duplicate "success" event.
**Example — good**: `202 Accepted` + job id; client polls; the handler dedupes and releases locks on terminal states.

---

## Priority 12 — Place and order pipeline stages correctly

**You MUST** do each piece of work in the stage that consumes it, not an earlier stage "for convenience".

**You MUST** use one processing strategy per stage (batch throughout, or synchronous throughout) unless a documented exception exists.

**Example — bad**: enrichment runs in `prepare` though only `process` uses it; a per-row sync call sits inside an otherwise batched pipeline.
**Example — good**: enrichment runs in `process`; `prepare` only assembles batch input.

---

## Priority 13 — Align with the specification

**You MUST** keep first-class domain fields as explicit fields, not generic key-value context, when the spec defines them.

**You MUST** flag redundant or contradictory concepts across spec, API contract, and model, and ask which is canonical before adding a third.

**Example — bad**: spec defines `customerId` as reserved; code stores it in `metadata.customer_id`.
**Example — good**: spec, API, and model use the same term for the same fact.

---

## Priority 14 — Prove it: types, tests, hygiene, scope

**You MUST** require typed signatures on public methods and tests for each new sort order, pagination boundary, and retry/idempotency path — not only the happy path.

**You MUST NOT** approve silent early returns that mark work done while leaving resources held.

**You MUST** flag a diff whose footprint far exceeds its stated change (e.g. a filter tweak touching dozens of files) and ask why.

**You MAY** note pre-existing type/static-analysis debt separately from issues introduced by the change.

**Example — bad**: "only filters changed" but 60+ files differ; a worker returns OK on null input.
**Example — good**: the diff matches the change; terminal states fail loudly or transition to a defined error.

---

## Review procedure

1. **Scope** — changed files and immediate callers; include sibling modules exposing the same surface.
2. **Search first** — look for existing implementations, duplicate routes, and the type that should own new logic before judging it.
3. **Classify** — Critical (correctness/security/data loss), Major (architecture/DRY/maintainability), Minor (naming/style).
4. **Report** — findings first, ordered by severity; cite path and line; state the rule violated and what good looks like.
5. **Do not fix** — unless the user explicitly asks.

---

## Red flags — stop and report immediately

| Signal | Likely violation |
|--------|------------------|
| Function takes an object only to read its fields | Priority 1 — misplaced behavior |
| New type for a fact the model already has | Priority 2 — redundant concept |
| Class/endpoint with one caller and no behavior | Priority 3 — needless code |
| Controller file grew with private helpers | Priority 4 — fat entry point |
| Same logic or route in two places | Priority 5 — duplication |
| Many one-method passthrough classes | Priority 6 — indirection sprawl |
| Domain/presentation logic on a state object | Priority 7 — mixed responsibility |
| Generic component with a specific name (or vice versa) | Priority 8 — naming |
| Domain string or untyped map in shared lib | Priority 9 — leaky boundary |
| Write/transaction on a pure read | Priority 10 — side effect in query |
| Duplicate event/task, lock left held | Priority 11 — non-idempotent async |
| Work done in the wrong stage; mixed strategies | Priority 12 — stage placement |
| Reserved field stored as generic context | Priority 13 — spec drift |
| Diff far larger than its stated change | Priority 14 — scope creep |

---

## Additional resources

- DDD principles: [acting-as-architect/references/ddd.md](../acting-as-architect/references/ddd.md)
- Architect role and deliverables: [acting-as-architect/SKILL.md](../acting-as-architect/SKILL.md)
- Test rigor: [acting-as-quality-engineer/SKILL.md](../acting-as-quality-engineer/SKILL.md)
