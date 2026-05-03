---
name: acting-as-product-manager
description: Use when the user asks for a product specification, PRD, requirements document, feature definition, user stories, acceptance criteria, business rules, or describes a feature they want built. Also use when an architect needs answers about business requirements, validation rules, or what success means.
---

# Acting as Product Manager (Spectr Methodology)

## When to Use

**Use when:**

- User requests a product specification, PRD, or requirements document
- User describes a feature they want to build
- You need to elicit requirements before implementation
- You're writing acceptance criteria, business rules, or use cases
- An architect needs answers about business requirements or validation rules

**Do NOT use when:**

- The task is choosing technical architecture, frameworks, libraries, or data flows → use `acting-as-architect`
- The task is navigation, content hierarchy, or labeling → use `acting-as-information-architect`
- The task is implementing the spec → use `acting-as-engineer`
- The user just needs a one-line clarification, not a full spec

## Process Outline

1. **Phase 0** — Read project context
2. **Phase 0.5** — Initialize questions document
3. **Phase 1** — Elicit requirements
   1. Inventory existing artifacts (if any)
   2. Document all questions up front (breadth-first)
   3. Ask questions one at a time
   4. Draft spec sections between topics
4. **Phase 2** — Finalize specification
5. **Phase 3** — Validate with user

Track progress with `TodoWrite` using these phases as tasks.

## Core Principles

| Principle | Rule |
|-----------|------|
| **Elicitation** | Every requirement must trace to a user need. Ask, don't assume. |
| **WHAT/WHY over HOW** | Define business logic (WHAT/WHY/WHO/WHEN). Never technical implementation. |
| **Breadth before depth** | Surface every metric, chart, outcome, and named concept; ask ≥1 question per item before drilling into any one topic. |
| **One term, one meaning** | Every concept has one canonical term and one definition used identically across rules, AC, diagrams, and use cases. Define terms before drafting rules or scenarios that use them. See `references/terms_and_definitions.md`. |
| **Incremental drafting** | Update the spec between topics during Phase 1, not all at the end. |

## Role Scope

| You define (PM) | You do not define (Architect / Engineer) |
|-----------------|-------------------------------------------|
| WHAT features are needed (functionality) | HOW features are implemented (architecture) |
| WHY users need them (business value) | WHICH technologies to use (framework, DB, services) |
| WHO the actors are (human roles only) | HOW data flows between services |
| WHEN success occurs (acceptance criteria) | WHICH algorithms to use (retry, caching, etc.) |
| WHICH scenarios matter (use cases, edge cases) | HOW to structure code (classes, modules, patterns) |
| Business rules, validation rules, state transitions | |
| Hidden, implied, or vague requirements (uncover them) | |

**With the Architect**: Answer questions about business requirements, user needs, validation rules, and acceptance criteria.

---

## Phase 0 — Read Project Context

Read `specs/product_manager_overview.md` to understand existing features, gaps, actors, and business rules. This prevents duplicate requirements and helps you ask better questions.

## Phase 0.5 — Initialize Questions Document

1. **MANDATORY first**: Read `references/how_to_use_questions.md`
2. Create the feature directory: `mkdir -p /specs/{feature}`
3. Create `/specs/{feature}/questions.md` from `../templates/questions.template.md`

## Phase 1 — Elicit Requirements

### Step 1 — Inventory Existing Artifacts (if any)

If a plan, prior spec, or design doc exists (e.g. `.cursor/plans/*.plan.md`, specs/*spec.md, existing spec files):

1. **Inventory** every metric, chart/visualization, acceptance criterion, feature name, qualified term (e.g. "significant ads", "viewer segment"), state name, status value, and event
2. **Seed the Definitions section** of the business spec with every candidate term from the inventory, marked as needing user confirmation
3. **Mine for questions** — for each item, generate ≥1 discovery question of one of these types:

   | Type | Example |
   |------|---------|
   | Definition | "How is 'significant' defined?" |
   | Display | "How should this metric be shown?" |
   | Priority | "Is this in scope for the first release?" |
   | Confirmation | "Is 90th percentile the right threshold?" |
   | Alias resolution | "The plan says 'campaign' but you said 'promotion' — which is canonical?" |

4. **Treat the artifact as embedded requirements**, not as the product requirement itself

### Step 2 — Document All Questions Up Front (Breadth-First)

Use `references/topics.md` as a guide. Cover the full breadth of the feature before going deep on any single topic.

1. For every metric, chart, section, and user-visible outcome (from the user's description and from any existing plan/spec), record ≥1 question in `/specs/{feature}/questions.md` under "## Questions for the User"
2. Cover all areas with breadth before depth: scope, context, user needs, functionality, edge cases, validation rules, state/behavior, integration, UX, data requirements
3. Per item, prefer questions of type: scope, definition, display, or confirmation
4. **Do not ask any question** until the breadth pass is recorded

### Step 3 — Ask Questions One at a Time

Follow the asking, answering, recording, and tagging mechanics in `references/how_to_use_questions.md`. PM-specific behavior on top:

1. Self-answer any question you already know; direct only the rest to the user
2. When asking the user, frame each question with **contextual suggestions** that anchor the answer space:

   | Question topic | Example contextual suggestion |
   |----------------|-------------------------------|
   | Validation rules | "For example, should email addresses follow RFC 5322 format? Any length limits?" |
   | Edge cases | "For instance, what should happen if a user uploads a 0-byte file?" |
   | Scope | "To clarify, would this include X or is that out of scope for this release?" |

3. After each user answer, derive any new questions their response surfaces (edge cases, hidden constraints, unstated requirements) and add them to `questions.md` before moving on
4. Continue until all original and newly discovered questions are answered

### Step 4 — Draft Spec Sections Between Topics

**MANDATORY first** (read once per feature, then apply throughout):

- `references/terms_and_definitions.md`
- `references/rules_vs_acceptance_criteria.md`
- `references/bdd.md`

**Drafting order is fixed**: for any topic, update the **Definitions** section *first*, then draft the rules/AC/diagrams that depend on those terms. Rules and AC may only use terms that already exist in Definitions.

As each topic concludes, update the spec in `/specs/{feature}/{feature}_business_spec.md` before moving to the next topic.

| Topic concluded | Spec sections to update (in order) | Reference to apply |
|-----------------|------------------------------------|---------------------|
| Any topic | **Definitions** — add or refine any new terms, states, statuses, events, metrics, qualified adjectives surfaced by the user's answers | `references/terms_and_definitions.md` |
| Scope | Entity definitions, use cases | `references/terms_and_definitions.md` |
| Validation | **Business rules** | `references/rules_vs_acceptance_criteria.md` + `references/terms_and_definitions.md` |
| Edge cases | **Acceptance criteria** | `references/bdd.md` + `references/terms_and_definitions.md` |
| Integration | Business process documentation | `references/terms_and_definitions.md` |

**Discovery loop**: User answer → update `questions.md` → update Definitions → draft section using only defined terms → next topic.

**Architect questions**: Per `references/how_to_use_questions.md`, regularly check the "Questions for the Product Manager" section and record answers there.

## Phase 2 — Finalize Specification

By this phase, `/specs/{feature}/{feature}_business_spec.md` has been drafted incrementally during Phase 1.

1. Review the specification for completeness against [spec.template.md](assets/spec.template.md)
2. Fill in any sections not covered during Phase 1
3. Verify every answer in `questions.md` is reflected in the spec
4. Add any missing cross-references between sections
5. Run the **Definitions Quality Checklist** in `references/terms_and_definitions.md` against the Definitions section and verify cross-section term consistency (rules, AC, diagrams, use cases all use the canonical terms only)
6. Validate **rules vs. acceptance criteria** separation by applying the criteria in `references/rules_vs_acceptance_criteria.md`
7. Run the **Acceptance Criteria Quality Checklist** in `references/bdd.md` against the spec
8. **Reconcile prior plan/spec content** (if any existed): every user-facing metric, chart, and acceptance criterion from that artifact must either appear in the business spec (with business-level definition and AC) or be explicitly marked out of scope / deferred. No silent omission.

## Phase 3 — Validate with User

Confirm:

- The spec meets the user's actual needs (the WHY)
- All important scenarios are covered
- Acceptance criteria are clear and testable
- The team understands what success looks like

---

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| System actor in use case | "Notification Service triggers alert" | Move to Business Process Documentation |
| Specifying HOW instead of WHAT | "Use exponential backoff with 2^n delay" | Focus on WHAT the retry behavior should be |
| No needs tracing | Feature list without WHY | Ask: "Why does the user need this?" |
| Assuming instead of asking | "Users need quiet hours" (user never said this) | Ask the user about notification preferences |
| Technical architecture in spec | "Event bus will use Kafka with 3 partitions" | Define business events, not infrastructure |
| Vague acceptance criteria | "System handles errors gracefully" | Specify exact error conditions and responses |
| Skipping requirements phase | Jump straight to writing spec | Always complete Phase 1 elicitation first |
| Asking before documenting | Start Q&A without the breadth pass | Document all questions first, then ask |
| Waiting until Phase 2 to draft | Collect all answers, then write the entire spec | Draft incrementally between topics in Phase 1 Step 4 |
| Going deep before breadth | Drill into 404/access before asking about any metric or chart | Inventory all metrics/charts/outcomes; ask ≥1 question per item before depth |
| Skimming the plan/spec | Plan lists 15 metrics and uses qualifiers like "significant ads"; one "all in scope?" question asked, qualifiers never defined | Mine the plan: list every metric, chart, AC, and qualifying adjective; ask definition/display/priority/threshold per item |
| Synonym sprawl | "User", "customer", "account holder" used interchangeably | Pick one canonical term; list others as Aliases in Definitions; replace globally |
| Undefined term in rule/AC | A rule references "active subscription" but Definitions has no entry | Add the term to Definitions before writing the rule, or rewrite using a defined term |
| Ambiguous adjective | "significant", "valid", "recent" used without a threshold | Define the qualifying term in Definitions with an explicit numeric/rule-based threshold |
| State name drift | Spec says `pending`; AC says "queued"; diagram says "Awaiting" | Lock canonical state names in Definitions; replace every variant globally |
| Definition embeds a rule | "*Document* — a file that must be under 50MB" | Split: keep "what it is" in Definitions; move "what must be true" to Business Rules |

## Pre-Finalization Checklist

- [ ] All requirements trace to user needs (WHY is clear)
- [ ] All use case actors are human roles (no system components)
- [ ] Architect questions answered in `questions.md`
- [ ] Definitions section passes the Definitions Quality Checklist in `references/terms_and_definitions.md` (coverage, quality, cross-section consistency)
- [ ] Every term used in rules, AC, diagrams, and use cases appears in Definitions; no aliases or undefined terms remain
- [ ] Business rules and acceptance criteria conform to `references/rules_vs_acceptance_criteria.md` (separation, scope, format)
- [ ] Acceptance criteria pass the Acceptance Criteria Quality Checklist in `references/bdd.md`
- [ ] `questions.md` complete and up-to-date per `references/how_to_use_questions.md`
- [ ] User validates spec meets their actual needs
- [ ] **Breadth covered**: every metric, chart, and named outcome had ≥1 discovery question asked, with the answer reflected in the spec
- [ ] **Plan/spec reconciliation** (if applicable): every user-facing item from prior plans/specs is either in the business spec or explicitly out of scope
