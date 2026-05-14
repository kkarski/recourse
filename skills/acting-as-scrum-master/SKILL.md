---
name: acting-as-scrum-master
description: Turns a finished product specification into phased architecture, design, testing, and implementation plans with traceability. Use when dividing a spec into delivery phases, prioritizing use cases and acceptance criteria, aligning architecture to a spec, or producing a phasing plan with UC/AC coverage. Assumes requirements are maintained with the Spectr CLI per `using-spectr` and read via CLI output or a companion `.md` file when the team maintains one (see `acting-as-product-manager` and `references/spectr-cli-for-pm.md`).
disable-model-invocation: true
---

# Phasing from specification

## Assumptions

- The source of truth is the Spectr specification edited with the **Spectr CLI** per **`using-spectr`**. Read it with **`spectr`** `list` / `read` (and related inspect commands from **`using-spectr`**), or use a companion **`specs/{feature}/{feature}_spec.md`** when the team maintains one—not by opening the on-disk spec source directly. It holds **use cases**, **acceptance criteria**, **business rules**, **definitions**, tests, Q&A, etc., as structured by **`acting-as-product-manager`** / **`using-spectr`** and **`references/spectr-cli-for-pm.md`** — do not assume a Markdown template checklist.
- Phasing is **dependency-first**: a phase is valid only if every UC/AC it claims can be satisfied given prior phases, data model, and runtime behavior.

## Procedure

### 1. Inventory the spec

- List every **use case** (UC) with actor, objective, and any pre/postconditions that imply ordering.
- List every **acceptance criterion** (AC) with ID; note **deprecated** or superseded ACs and treat them as **out of scope** for new work unless explicitly revived.
- From **Business Process Documentation** and **entities**, note **events**, **state transitions**, and **aggregates** that imply build order (e.g. assignment before handoff, receipt before honor).
- From **E2E Test Cases**, note which scenarios are **minimum viable** checks per slice.

### 2. Stabilize the spec before phasing

Do **not** treat a phasing plan as authoritative if the spec still contradicts itself or leaves critical holes.

- Run a **contradiction and gap pass**: ownership of data (where fields live), default or edge behaviors, lifecycle gates, delete/soft-delete semantics, concurrency, and anything that would change aggregates or APIs.
- If the team uses a **questions / decisions log**, reconcile it with the Spectr spec; stale architect answers that predate model moves (e.g. field moved from one aggregate to another) must be **updated or marked superseded** before architecture work proceeds.
- Close gaps with **short, explicit stakeholder Q&A** (batch related questions); record decisions in the spec or decision log. Avoid baking **unconfirmed defaults** into the plan without labeling them as assumptions.

### 3. Cluster capabilities

Group UC/AC into **capability clusters** (e.g. catalog, assignment, inbound capture, verification + cookie, honor/reuse, analytics, admin). Clusters become the raw material for phases — not every cluster is one phase.

### 4. Choose phasing shape (ask if unclear)

Ask the stakeholder when it changes the plan materially:

- **Business priority** between competing pillars (e.g. reuse/honor vs operational analytics) when both depend on the same foundation.
- **Slice style**: **vertical** (each phase ships end-to-end user-visible value), **foundation-ordered** (early phases may be backend-heavy), or **hybrid** (minimal E2E in phase 1, deeper features later).

Document the chosen shape in the plan **overview**.

### 5. Order phases by dependencies

- **Data model first**: migrations, default provisioning, and invariants that later routes assume must land in an early phase unless you explicitly stub and revisit (avoid silent tech debt).
- **Runtime chains**: landing → session/invite → verification → receipt/cookie → honor/evaluator → read models/analytics. Place each UC/AC in the **first phase where all prerequisites exist**.
- **Split UC/AC across phases only when** the spec clearly separates concerns; when splitting, add a **one-line note** per ID (e.g. “Phase 1: assignment storage only; Phase 4: honor fields in UC1 editor”).
- **Wrong-phase anti-pattern**: do not place **landing-only** or **candidate-facing** UCs in a phase that only delivers admin configuration unless the spec explicitly allows a stub; validate against the **main flow** of each UC.

### 6. Architecture alignment pass

After phasing (or in lockstep with it):

- Compare the plan to the **architecture doc**: aggregates, tables, API surfaces, ADRs, and diagrams must reflect the **current** spec (removed features excised; fields on the correct aggregate).
- If the spec **moved** behavior between components, update architecture **before** implementation tickets cite stale designs.
- Resolve **API path / resource** ambiguity (e.g. catalog PUT vs assignment PUT) during this pass.

### 7. Testing and implementation per phase

For each phase, define:

- **Design**: which aggregates/APIs/UI surfaces change; concurrency and lifecycle rules that are newly enforced.
- **Testing**: unit/integration boundaries; **E2E** scenarios that prove the slice; regression risks from prior phases.
- **Implementation**: ordered tasks (migrations before routes before UI when applicable); feature flags only if the spec allows partial exposure.

Explicitly call out **deferred** AC families (e.g. lock behavior) if they are intentionally placed later to avoid building the wrong validator early.

### 8. Traceability and drift control

- Add a **traceability appendix**: **UC → phase(s)** and **AC → phase** tables. Every UC and AC in scope should appear **exactly once** as primary owner, or **split** with notes.
- After spec amendments, **re-run coverage**: update phases when UC/AC numbering or meaning changes.
- Keep **cross-cutting** items (observability, backfill migrations, performance) in a dedicated subsection so they are not dropped.

### 9. Post–core scope (optional section in the plan)

After the core runtime chain (e.g. setup → inbound → verify/cookie → honor), add what comes **next** per the spec: analytics, read models, hardening, and **explicitly out-of-scope** roadmap items so future work is not confused with current phases.

## Plan document outline

Use this structure for the phasing deliverable (file name and tooling are project-specific):

```markdown
# [Initiative] — delivery phasing

## Overview
- Goal and phasing shape (vertical | foundation | hybrid)
- Stakeholder priority decisions (if any)

## Phase summary
| Phase | Name | Outcome | Depends on |
|-----|------|---------|------------|
| 1 | … | … | — |
| … | … | … | … |

## Phase details
### Phase N — [name]
- **Scope**: …
- **Use cases**: UC…
- **Acceptance criteria**: AC… (note splits)
- **Architecture / design**: aggregates, APIs, migrations
- **Testing**: E2E and integration focus
- **Implementation notes**: ordering, flags, data backfill

## Cross-cutting
- Observability, migrations, performance, compliance

## Traceability appendix
### UC → phase
| UC | Phase | Notes |
|----|-------|-------|

### AC → phase
| AC | Phase | Notes |
|----|-------|-------|

## Out of scope / future
- Items deferred by spec or product choice
```

Optional: a **mermaid** phase chain diagram `P1 → P2 → …` when it clarifies dependencies.

## Best practices (summary)

- **Spec stability before plans**: contradictions become expensive if architecture and phasing diverge.
- **Explicit decisions**: record Q&A outcomes; flag assumed defaults the user did not answer.
- **Dependency-first ordering**: prevents “phase 1” plans that omit prerequisites for invite or handoff behavior.
- **Full UC/AC coverage**: use the appendix; fix mistakes like wrong-phase UCs immediately.
- **Architecture sync**: model moves (e.g. field from catalog to assignment) require doc updates in the same pass as phase definitions.
- **Respect AC hygiene**: never renumber or delete ACs per **`acting-as-product-manager`** / **`using-spectr`**; deprecate obsolete ones and exclude from traceability or mark DEPRECATED.

## Pitfalls illustrated by past phasing work

- **Stale architecture**: diagrams and ADRs still describing removed features or old aggregate boundaries while the Spectr spec has moved on.
- **Phase drift**: phase documents predating late spec rounds missing new ACs or still referencing removed ACs.
- **Misplaced UCs**: configuration-heavy phase lists candidate landing UCs without the runtime to support them (or the reverse).
- **Split AC confusion**: one AC ID meaning different things in different phases without a note (e.g. catalog vs UI behavior).
- **Unvalidated defaults**: closing a workshop with “defaults applied” where the user did not confirm — always list those separately.

## Related artifacts

- Product requirements: Spectr CLI per **`using-spectr`** and **`acting-as-product-manager`**; PM mechanics in **`references/spectr-cli-for-pm.md`**; optional readable companion **`specs/{feature}/{feature}_spec.md`** when the team maintains that artifact
- Architecture document, migration notes, and questions/decision logs should be cited from the repo when present.
