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

**You MUST** read the project's architecture docs and coding standards before reviewing.

---

## Priority 1 — Real domain modeling (not cosmetic OO)

**You MUST** model real business concepts with identity, invariants, and cohesive behavior — not rename loose functions into a class.

**You MUST** place behavior on the type that owns the data: domain entities and value objects for business rules; repositories for persistence; application services only for cross-aggregate coordination.

**You MUST NOT** create “noise classes” or “engines” that mix unrelated concerns (parsing, I/O, pagination, response mapping, storage) with no domain identity.

**You MUST NOT** pass many unpacked primitives when a domain object already exists.

**You MAY** use a standalone function only when it is pure, stateless, and has no natural owner — and you MUST document why.

**Example — bad**: `PricingEngine.calculate()`, `PricingEngine.loadFromDb()`, `PricingEngine.toJson()` — unrelated responsibilities, no pricing concept with identity.

**Example — good**: `Order.applyDiscount(code)` enforces rules on the order; `OrderRepository.save(order)` handles persistence.

---

## Priority 2 — Thin entry points, fat domain layer

**You MUST** keep HTTP handlers, controllers, and CLI commands as orchestration only: parse input → delegate to domain/service → map output.

**You MUST** push URL building, error mapping, pagination, and validation into domain types or application services — not new private helpers in the controller file.

**You MUST NOT** add free-floating helper functions to controllers when an existing domain type or service already owns that concern.

**You MUST NOT** put multi-repository branching logic in a controller; collapse it into a typed command object with a single `execute()` or an application service.

**You MAY** keep a handler under ~15 lines of non-boilerplate logic.

**Example — bad**: `OrderController` contains 40 lines deciding which repository to call based on request shape.

**Example — good**: `CreateOrderCommand.from(request).execute()` — controller is three lines.

---

## Priority 3 — DRY: one concept, one implementation

**You MUST** search the codebase for existing implementations before adding parallel logic.

**You MUST NOT** duplicate the same composition block across handlers (two redirect builders, two “build response” paths, two write paths for the same operation).

**You MUST NOT** expose the same API endpoint from two modules with different behavior.

**You MUST NOT** introduce parallel repository methods that differ only by name (wrapper around an existing internal method).

**You MAY** extract shared behavior onto the domain object or a single service when two call sites need identical semantics.

**Example — bad**: `buildCheckoutUrl()` copied in `PaymentController` and `WebhookController` with drift over time.

**Example — good**: `CheckoutSession.redirectUrl()` — one implementation, all callers use it.

---

## Priority 4 — No anemic models, no thin wrappers

**You MUST NOT** add one-line methods or classes whose only job is to forward to another call.

**You MUST NOT** split a workflow into many single-method types (`Storage`, `Registry`, `Scheduler`, `PhaseService`) that add indirection without behavior.

**You MUST** consolidate thin wrappers by inlining onto the aggregate, pipeline, or domain type that owns the workflow.

**You MAY** keep a small type when it carries state, enforces invariants, or groups three or more related operations with shared context.

**Example — bad**: `OrderSaver.save(order)` → `orderRepository.insert(order)` — adds nothing.

**Example — good**: `ImportPipeline` owns orchestration; step state lives on `ImportJob`, not five passthrough classes.

---

## Priority 5 — Layer boundaries and leaky abstractions

**You MUST** keep shared infrastructure (HTTP clients, message publishers, generic batch runners) free of domain-specific knowledge.

**You MUST NOT** put domain field names, domain-specific stubs, or domain error text into shared library modules.

**You MUST** use typed query/command objects for filters and parameters — not untyped maps passed through layers.

**You MUST NOT** expose implementation details to API consumers (internal batch sizes, pipeline phase names, storage key formats).

**You MAY** place domain-specific serialization on domain request/response types at the boundary.

**Example — bad**: `HttpClient` contains `if (resourceType === "invoice")` branches and invoice-specific retry messages.

**Example — good**: `HttpClient.post(url, body)` is generic; `InvoiceExporter.toPayload()` lives in the billing module.

---

## Priority 6 — Command/query separation and side effects

**You MUST** treat read operations (GET, queries, list endpoints) as side-effect-free unless the specification explicitly documents otherwise.

**You MUST NOT** persist, reconcile, or lazily initialize state inside read handlers.

**You MUST** route read-only queries through the read path (read replica, read model, or query service) when the architecture provides one.

**You MUST** keep writes, row locks, and read-after-write in the same transaction on the primary data source.

**You MUST NOT** pass entities loaded in a read scope into a write scope without reloading within the write boundary.

**You MAY** force primary reads only for freshness-sensitive cases, with a documented reason.

**Example — bad**: `GET /users/123/profile` creates a profile row if missing.

**Example — good**: `GET` returns current state; `POST /users/123/profile/init` creates; background jobs handle deferred materialization.

---

## Priority 7 — Async workflow consistency

**You MUST** follow the project's established async pattern (stages, status tracking, idempotent handlers) for long-running work.

**You MUST** use the platform's built-in retry semantics (queue retries, retryable errors) instead of long blocking polls inside request handlers.

**You MUST NOT** acknowledge or delete a queued job while work is still in a retriable incomplete state.

**You MUST NOT** block HTTP responses on worker polling; return an appropriate deferred status and let the client or queue retry.

**You MUST** name workflow entry points consistently — one clear verb per step, not parallel `start` + `run` without reason.

**You MAY** split phases into separate handlers when each phase has distinct retry, timeout, or idempotency needs.

**Example — bad**: API handler loops 60s waiting for export file; returns 200 only when done.

**Example — good**: API returns `202 Accepted` + job id; client polls `GET /jobs/{id}` or receives a webhook; worker retries on transient failure.

---

## Priority 8 — Module placement and duplicate surfaces

**You MUST** place code in the bounded context that owns the concept — not a generic catch-all module.

**You MUST NOT** couple an analysis or utility module to a single consumer without an explicit boundary (interface, port, or documented integration point).

**You MUST** resolve duplicate API surfaces into one canonical endpoint with one behavior.

**You MUST NOT** open a separate transaction inside a guard or assertion that races with the caller's transaction (TOCTOU).

**Example — bad**: `BillingService` and `InvoiceApi` both expose `POST /invoices` with different validation.

**Example — good**: one `InvoiceController`; other modules call `InvoiceService` through a defined port.

---

## Priority 9 — Consistent processing strategy per stage

**You MUST** use one processing strategy per pipeline stage (batch throughout, or synchronous throughout) unless a documented exception exists.

**You MUST NOT** mix a slow synchronous call in an early stage with batch processing in later stages on the same hot path — that fails under load.

**You MUST** split and merge batches internally; callers MUST NOT know per-strategy batch sizes or shard rules.

**Example — bad**: `prepare` calls a synchronous enrichment API per row while `process` uses a batch job — prepare becomes the bottleneck.

**Example — good**: `prepare` writes a batch input file; `process` submits and consumes batch output; no per-row sync calls on the hot path.

---

## Priority 10 — Specification and domain concept alignment

**You MUST** verify first-class domain fields are not stored as generic key-value context when the spec defines them explicitly.

**You MUST** flag redundant domain concepts and ask which is canonical before adding a third parallel type.

**You MUST** check acceptance criteria, business rules, and architecture docs for contradictions before approving new endpoints or states.

**You MAY** record spec gaps as Major findings when implementation exposes missing rules.

**Example — bad**: spec defines `customerId` as a reserved field; implementation stuffs it into `metadata.customer_id`.

**Example — good**: API contract, domain model, and persistence use the same term for the same fact.

---

## Priority 11 — Types, tests, and operational hygiene

**You MUST** flag new untyped parameter bags where a typed query or command object exists or should exist.

**You MUST** require tests for each new sort order, pagination boundary, and idempotent retry path — not only the happy path.

**You MUST NOT** approve silent early returns in job handlers that mark work completed while leaving locks held or jobs orphaned.

**You MAY** note pre-existing static-analysis or type debt separately from findings introduced by the change under review.

**Example — bad**: worker returns success when batch reference is null; distributed lock never released.

**Example — good**: terminal states always release resources; missing input fails loudly or transitions to a defined error state.

---

## Review procedure

1. **Scope** — changed files and immediate callers only; include sibling modules that expose the same surface.
2. **Search** — look for parallel implementations, duplicate route registrations, and existing domain methods before judging new code.
3. **Classify** — tag each finding Critical (correctness/security/data loss), Major (architecture/DRY/maintainability), Minor (naming/style).
4. **Report** — findings first, ordered by severity; cite path and line; state which rule was violated and what good looks like.
5. **Do not fix** — unless the user explicitly asks to implement changes.

---

## Red flags — stop and report immediately

| Signal | Likely violation |
|--------|------------------|
| Controller file grew with new private helpers | Priority 2 — fat entry point |
| New class named `*Engine` or `*Helper` | Priority 1 — cosmetic OO |
| Same 20+ line block in two handlers | Priority 3 — DRY |
| Write/transaction scope on a pure read/list | Priority 6 — side effects |
| Domain-specific string in shared `client/` lib | Priority 5 — leaky abstraction |
| `start` + `run` on same workflow step | Priority 7 — async inconsistency |
| Second registration for same API path | Priority 8 — duplicate surface |
| Job returns OK with no work done, lock held | Priority 11 — silent failure |

---

## Additional resources

- DDD principles: [acting-as-architect/references/ddd.md](../acting-as-architect/references/ddd.md)
- Architect role and deliverables: [acting-as-architect/SKILL.md](../acting-as-architect/SKILL.md)
- Test rigor: [acting-as-quality-engineer/SKILL.md](../acting-as-quality-engineer/SKILL.md)
