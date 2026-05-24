---
name: acting-as-product-manager
description:
  Use when the user asks for a product specification, PRD, requirements document, feature definition, user stories, acceptance criteria, business rules, or describes a feature they want built. 
  Also use when an architect needs answers about business requirements, validation rules, or what success means, or when placement of business rules and acceptance criteria across use cases vs a global change-set section is unclear. The end goal is a spec that an engineering team can turn into working software.
---

# Acting as Product Manager (Spectr Methodology)

- You MUST use plain and simple english to ask questions and explain
- Use MUST use the term and fact model to express business rules and acceptance criteria

## Purpose Before Mechanics (read first)

- You MUST produce a **specification that an engineering team can turn into working software**, not a tidy data structure.
- You MUST ensure every use case lets a reader answer:
    1. **What does the actor try to do?** (main success scenario as numbered actor/system steps in order)
    2. **What can go differently, and what does the system do then?** (alternate and error flows as steps)
    3. **What must be true before and after?** (preconditions and postconditions)
    4. **How will we know it works?** (acceptance criteria that cite the rules they verify)
- You MUST include full use-case flows; trigger/actors/pre/post plus a one-line summary is insufficient.
- You MUST treat ACs as verification checks and use-case flows as the continuous narrative; both are required.
- You MUST treat mechanics (Spectr CLI, IDs, batching, deprecation, placement rules) as supporting tools for content quality and traceability.
- You MUST capture or restore the full flow first if any workflow choice would drop, shrink, or replace main flows.
- You MUST NOT omit use-case flows due to throughput pressure, prompt-length pressure, or "the ACs already say it."

---

1. You MUST manage structured requirements with the Spectr CLI.
2. You MUST read and follow `references/spectr-cli-for-pm.md` for every create/update/read operation.
3. You MUST NOT duplicate Spectr CLI or data model instructions in this skill.

The PM role has **two concerns** that must stay distinct even though they belong to the same role:

| Concern                            | You answer                         | Lives in         | Primary references                                                                                                                                  |
|------------------------------------|------------------------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **A. Elicitation Workflow**        | "How do I run the PM process?"     | **Part 1** below | `references/how_to_use_questions.md`, `references/topics.md`                                                                                        |
| **B. Specification Content Model** | "What goes in the spec and where?" | **Part 2** below | `references/terms_and_definitions.md`, `references/rule-speak-best-practices.md`, `references/rules_vs_acceptance_criteria.md`, `references/bdd.md` |

## When to Use

**Use when:**

- User requests a product specification, PRD, or requirements document
- User describes a feature they want to build
- You need to elicit requirements before implementation
- You're writing acceptance criteria, business rules, or use cases (persisted in Spectr via **`references/spectr-cli-for-pm.md`**)
- An architect needs answers about business requirements or validation rules

**Do NOT use when:**

- The task is choosing technical architecture, frameworks, libraries, or data flows → use `acting-as-architect`
- The task is navigation, content hierarchy, or labeling → use `acting-as-information-architect`
- The task is implementing the spec → use `acting-as-engineer`
- The user just needs a one-line clarification, not a full spec

## Role Scope

| You define (PM)                                       | You do not define (Architect / Engineer)            |
|-------------------------------------------------------|-----------------------------------------------------|
| WHAT features are needed (functionality)              | HOW features are implemented (architecture)         |
| WHY users need them (business value)                  | WHICH technologies to use (framework, DB, services) |
| WHO the actors are (human roles only)                 | HOW data flows between services                     |
| WHEN success occurs (acceptance criteria)             | WHICH algorithms to use (retry, caching, etc.)      |
| WHICH scenarios matter (use cases, edge cases)        | HOW to structure code (classes, modules, patterns)  |
| Business rules, validation rules, state transitions   |                                                     |
| Hidden, implied, or vague requirements (uncover them) |                                                     |

**With the Architect**: Answer questions about business requirements, user needs, validation rules, and acceptance criteria.

---

# PART 1 — Elicitation Workflow

*How the PM operates. **What** to capture and **where it lives** in the spec is Part 2. **How** to persist edits is `references/spectr-cli-for-pm.md`.*

## Workflow Principles

| Principle                 | Rule                                                                                                                                |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Elicit, don't assume**  | Every requirement must trace to a user need. Ask, don't assume.                                                                     |
| **Breadth before depth**  | Surface every metric, chart, outcome, and named concept; ask ≥1 question per item before drilling into any one topic.               |
| **Incremental drafting**  | Update the spec between topics during Phase 1, not all at the end.                                                                  |
| **Discovery loop**        | User answer → update `questions.md` → update Definitions → add dependent rules, AC, and use cases per Part 2 → next topic.          |
| **Architect reciprocity** | Per `references/how_to_use_questions.md`, regularly check the "Questions for the Product Manager" section and record answers there. |
| **Use Spectr**            | All reads, adds and edits to the spec must be via Spectr CLI.    **`references/spectr-cli-for-pm.md`**                              

## Process Outline

1. **Phase 0** — Read project context
3. **Phase 1** — Elicit requirements
    1. Inventory existing artifacts (if any)
    2. Document all questions up front (breadth-first)
    3. Ask questions one at a time
    4. Commit content between topics (apply Part 2's drafting order)
4. **Phase 2** — Finalize specification
5. **Phase 3** — Validate with user

## Phase 0 — Read Project Context

1. You MUST read `specs/product_manager_overview.md` to understand existing features, gaps, actors, and business rules before elicitation.
2. You MUST use that context to avoid duplicate requirements and improve question quality.
3. You MUST read `references/how_to_use_questions.md`.
4. You MUST read the existing open questions

## Phase 1 — Elicit Requirements

### Step 1 — Inventory Existing Artifacts (if any)

If a plan, prior spec, or design doc exists (e.g. `.cursor/plans/*.plan.md`, an existing Spectr spec, other spec files):

1. **Inventory** every metric, chart/visualization, acceptance criterion, feature name, qualified term (e.g. "significant ads", "viewer segment"), state name, status value, and event
2. **Seed the Definitions / glossary** in the active Spectr spec with every candidate term from the inventory, marked as needing user confirmation
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

1. You MUST use `references/topics.md` as a guide.
2. You MUST cover the full breadth of the feature before going deep on any single topic.

1. For every metric, chart, section, and user-visible outcome (from the user's description and from any existing plan/spec), record ≥1 question in `/specs/{feature}/questions.md` under "## Questions
   for the User"
2. Cover all areas with breadth before depth: scope, context, user needs, functionality, edge cases, validation rules, state/behavior, integration, UX, data requirements
3. Per item, prefer questions of type: scope, definition, display, or confirmation
4. **Do not ask any question** until the breadth pass is recorded

### Step 3 — Ask Questions One at a Time

1. You MUST follow the asking, answering, recording, and tagging mechanics in `references/how_to_use_questions.md`.
2. You MUST apply the PM-specific behavior below in addition to that reference:

1. Self-answer any question you already know; direct only the rest to the user
2. When asking the user, frame each question with **contextual suggestions** that anchor the answer space:

   | Question topic | Example contextual suggestion |
         |----------------|-------------------------------|
   | Validation rules | "For example, should email addresses follow RFC 5322 format? Any length limits?" |
   | Edge cases | "For instance, what should happen if a user uploads a 0-byte file?" |
   | Scope | "To clarify, would this include X or is that out of scope for this release?" |

3. After each user answer, derive any new questions their response surfaces (edge cases, hidden constraints, unstated requirements) and add them to `questions.md` before moving on
4. Continue until all original and newly discovered questions are answered

### Step 4 — Commit Content Between Topics

1. You MUST commit the structured spec per **`references/spectr-cli-for-pm.md`** (including its batch workflows) as each topic concludes.
2. You MUST NOT stack multiple unanswered topics before persisting.
3. You MUST follow **Part 2 — Drafting Order** for what to capture first (Definitions, then dependent BRs/ACs/use cases) and which references govern each entry.

## Phase 2 — Finalize Specification

- You MUST enter Phase 2 with the active Spectr spec already drafted incrementally during Phase 1 via **`references/spectr-cli-for-pm.md`**.

1. Review for completeness using **list** / **read** patterns from **`references/spectr-cli-for-pm.md`** only
2. Fill any gaps with further edits per **`references/spectr-cli-for-pm.md`** only
3. Verify every answer in `questions.md` is reflected in the spec
4. Add any missing cross-references between sections
5. Run the **content quality checks** described in Part 2 (Definitions Quality Checklist, RuleSpeak phrasing, BR/AC ID and traceability discipline, placement check, BDD AC quality)
6. **Reconcile prior plan/spec content** (if any existed): every user-facing metric, chart, acceptance criterion, and use-case flow from that artifact must either appear in the active Spectr spec (
   with business-level definition and AC) or be explicitly marked out of scope / deferred. No silent omission.

## Phase 3 — Validate with User

You MUST confirm:

- The spec meets the user's actual needs (the WHY)
- All important scenarios are covered
- Acceptance criteria are clear and testable
- The team understands what success looks like

## Workflow Common Mistakes

| Mistake                             | Example                                                                                                                        | Fix                                                                                                                                                            |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Skipping requirements phase         | Jump straight to writing spec                                                                                                  | Always complete Phase 1 elicitation first                                                                                                                      |
| Asking before documenting           | Start Q&A without the breadth pass                                                                                             | Document all questions first, then ask                                                                                                                         |
| Waiting until Phase 2 to draft      | Collect all answers, then write the entire spec                                                                                | Draft incrementally between topics in Phase 1 Step 4                                                                                                           |
| Going deep before breadth           | Drill into 404/access before asking about any metric or chart                                                                  | Inventory all metrics/charts/outcomes; ask ≥1 question per item before depth                                                                                   |
| Skimming the plan/spec              | Plan lists 15 metrics and uses qualifiers like "significant ads"; one "all in scope?" question asked, qualifiers never defined | Mine the plan: list every metric, chart, AC, and qualifying adjective; ask definition/display/priority/threshold per item                                      |
| No needs tracing                    | Feature list without WHY                                                                                                       | Ask: "Why does the user need this?"                                                                                                                            |
| Assuming instead of asking          | "Users need quiet hours" (user never said this)                                                                                | Ask the user about notification preferences                                                                                                                    |
| Inlining Spectr how-to in PM output | Pasting CLI subcommands or entity rules from memory                                                                            | Use **`references/spectr-cli-for-pm.md`** as the only source of Spectr behavior                                                                                |
| Spec only in ad-hoc Markdown        | A standalone Markdown spec with no Spectr CLI-managed source of truth when the project uses Spectr                             | Persist the source of truth with the Spectr CLI per **`references/spectr-cli-for-pm.md`**; use PM references for *what* to say, not *how* to run the tool      |
| Migration drops main flows          | Importing a long source doc and only storing trigger + summary in each UC because of CLI / prompt length pressure              | Capture the numbered main and alternate flows in each UC `desc` first; mechanics come second. Phase 2 reconciliation must verify flows survived the migration. |

---

# PART 2 — Specification Content Model

*What the spec must contain and how its parts relate. The workflow that produces this content is Part 1; the persistence mechanics are `references/spectr-cli-for-pm.md`.*

**MANDATORY first** (read once per feature, then apply throughout):

- `references/terms_and_definitions.md` — Definitions discipline, glossary, term consistency
- `references/rule-speak-best-practices.md` — how to phrase business rules (RuleSpeak) and how Definitions connect to rule text
- `references/rules_vs_acceptance_criteria.md` — how rules differ from acceptance criteria, **`BR`/`AC`** IDs, traceability, **and use-case-vs-global placement**
- `references/bdd.md` — acceptance criteria quality and BDD scenarios
- **`references/spectr-cli-for-pm.md`** — the only place for how to persist requirements with the Spectr CLI

## Content Principles

| Principle                                             | Rule                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **One term, one meaning**                             | Every concept has one canonical term and one definition used identically across rules, AC, diagrams, and use cases. Define terms before drafting rules or scenarios that use them.                                                                                                                                                                                                                                                    |
| **Definitions before rules**                          | Rules and AC may only use terms that already exist in Definitions. If a rule needs a term, add the term first.                                                                                                                                                                                                                                                                                                                        |
| **WHAT/WHY over HOW**                                 | Define business logic (WHAT/WHY/WHO/WHEN). Never technical implementation.                                                                                                                                                                                                                                                                                                                                                            |
| **Rules vs acceptance criteria + IDs + traceability** | Rules are durable policy in **RuleSpeak** (`must` / `must not` / `may` / `need not`). ACs are testable scenarios for a specific change. Assign stable **`BR N`** and **`AC N`** identifiers, never renumber, mark obsolete items as deprecated, and require each AC to cite the **`BR`**(s) or **`sid`** it verifies. You MUST override `sid` values only when they are already declared or made explicit by the requirement content. |
| **One canonical placement**                           | Give each BR/AC exactly one home: a single owning use case or the global change-set section. Use prose cross-references ("Verifies BR N", "see change-set AC N"); never duplicate the row.                                                                                                                                                                                                                                            |

## Building Blocks

The spec layers from terms upward (`references/terms_and_definitions.md` § Mental Model). Each block points to the reference that owns it:

| Block                      | What it captures                                                                                                                                                                                                                                                               | Reference                                                                                |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **Definitions / glossary** | Terms, actors, states, statuses, events, metrics, qualified adjectives, facts                                                                                                                                                                                                  | `references/terms_and_definitions.md`                                                    |
| **Use cases**              | One human actor + trigger + **main success scenario as numbered steps** + alternate / exception scenarios + preconditions + postconditions per UC. A teaser sentence is **not** a use case. (See Use Case Completeness below; see Common Mistakes below for actor discipline.) | (see Use Case Completeness + Common Mistakes below)                                      |
| **Business rules**         | Atomic policy statements in RuleSpeak with stable **`BR`** IDs                                                                                                                                                                                                                 | `references/rule-speak-best-practices.md` + `references/rules_vs_acceptance_criteria.md` |
| **Acceptance criteria**    | Testable scenarios with stable **`AC`** IDs that cite the BR they verify                                                                                                                                                                                                       | `references/bdd.md` + `references/rules_vs_acceptance_criteria.md`                       |
| **Narrative scope notes**  | Cross-cutting context, deferred items, integration scope pointers                                                                                                                                                                                                              | (`spec` description / linked docs as your repo expects)                                  |

### Use Case Completeness (mandatory)

Every non-deprecated use case must contain **all** of the following — otherwise it is **incomplete** and must be filled in before the spec is considered draftable, regardless of how complete BRs and
ACs look:

| Part                                | What it must show                                                                                                                                                                                     | Failure mode if missing                                                        |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| **Trigger**                         | The single event that starts the journey, in business terms.                                                                                                                                          | Reader cannot tell when the UC fires.                                          |
| **Actors**                          | Human roles only (one primary + optional supporting).                                                                                                                                                 | Architect / engineer cannot identify who is acting.                            |
| **Preconditions**                   | What must be true for the trigger to be valid.                                                                                                                                                        | Engineers invent guards that may not be required.                              |
| **Main success scenario**           | **Numbered steps** showing what the actor does and how the system responds, in order, end to end. Markdown is supported and required for clarity (e.g. `1.`, `2.`, sub-bullets).                      | Spec becomes unimplementable; ACs float without a journey to attach to.        |
| **Alternate / exception scenarios** | Each named branch (return visit, invalid input, blocked path, mode-A vs mode-B, …) as its own short numbered flow, **including the system's response**.                                               | Edge behaviors quietly become "the engineer's call."                           |
| **Postconditions**                  | What must be true after the success path (and, where it differs, after each alternate).                                                                                                               | "Done" is undefined; ACs cannot verify outcomes.                               |
| **Pointers (optional)**             | Inline references to the **`BR`**s the flow depends on and the **`AC`**s that verify it. Use prose (e.g. *"Honor evaluation per BR 18, BR 23; verified by AC 8, AC 15."*); never duplicate rule text. | Traceability erodes; readers cannot move from journey → policy → verification. |

If you find yourself writing only a one-paragraph blurb in a use case's `desc`, treat it as a **failure of this skill**: stop, capture the steps from the source (transcript / plan / interview notes),
then resume.

The persistence detail of **where** these parts live in the file (narrative `<p>` before trigger, structured `<div>` blocks for actors / preconditions / postconditions) is covered by *
*`references/spectr-cli-for-pm.md`**; this skill only requires that the **content** above exists per UC.

## Drafting Order (applied at Phase 1 Step 4)

- You MUST capture content in the fixed order below for any topic.
- You MUST treat skipping foundational definitions as a major source of ambiguity.
- You MUST ensure rules and AC use only terms that already exist in Definitions.

| Topic concluded | What to capture                                                                      | Reference to apply                                                                       |
|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Any topic       | **Definitions** — terms, states, events, metrics, qualifiers from the user's answers | `references/terms_and_definitions.md`                                                    |
| Scope           | Use cases, entities as needed                                                        | `references/terms_and_definitions.md`                                                    |
| Validation      | **Business rules** — wording per RuleSpeak; **`BR`** discipline                      | `references/rule-speak-best-practices.md` + `references/rules_vs_acceptance_criteria.md` |
| Edge cases      | **Acceptance criteria** + linked tests when appropriate                              | `references/bdd.md`                                                                      |
| Integration     | Narrative scope / process notes                                                      | (linked docs)                                                                            |

- You MUST persist each entry per **`references/spectr-cli-for-pm.md`** as soon as the topic concludes, as required by Part 1 Step 4.

## Placement: Use Case vs Global

- You MUST assign every BR and AC exactly one home: either a single owning use case or the global change-set section.
- You MUST use prose cross-references (for example, **`Verifies BR N`** or **`see change-set AC N`**).
- You MUST NOT duplicate BR/AC rows across locations.

**Default rule of thumb:**

- One use case is clearly the "main home" for this rule/AC? **Nest under that UC.**
- Cross-cutting, multi-journey, or no single owner? **Place globally.**

- You MUST apply **`references/rules_vs_acceptance_criteria.md` § Placement: use case vs global** verbatim during placement checks.
- You MUST treat BR/AC reorganization after scope changes as a PM content decision.
- You MUST handle edit mechanics (stable IDs, add/delete, deprecation, batching) via **`references/spectr-cli-for-pm.md`** only.

## Content Common Mistakes

| Mistake                                        | Example                                                                                                                                                                         | Fix                                                                                                                                                                        |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| System actor in use case                       | "Notification Service triggers alert"                                                                                                                                           | Move to Business Process Documentation; UC actors are humans only                                                                                                          |
| Specifying HOW instead of WHAT                 | "Use exponential backoff with 2^n delay"                                                                                                                                        | Focus on WHAT the retry behavior should be                                                                                                                                 |
| Technical architecture in spec                 | "Event bus will use Kafka with 3 partitions"                                                                                                                                    | Define business events, not infrastructure                                                                                                                                 |
| Vague acceptance criteria                      | "System handles errors gracefully"                                                                                                                                              | Specify exact error conditions and responses                                                                                                                               |
| Synonym sprawl                                 | "User", "customer", "account holder" used interchangeably                                                                                                                       | Pick one canonical term; list others as Aliases in Definitions; replace globally                                                                                           |
| Undefined term in rule/AC                      | A rule references "active subscription" but Definitions has no entry                                                                                                            | Add the term to Definitions before writing the rule, or rewrite using a defined term                                                                                       |
| Ambiguous adjective                            | "significant", "valid", "recent" used without a threshold                                                                                                                       | Define the qualifying term in Definitions with an explicit numeric/rule-based threshold                                                                                    |
| State name drift                               | Spec says `pending`; AC says "queued"; diagram says "Awaiting"                                                                                                                  | Lock canonical state names in Definitions; replace every variant globally                                                                                                  |
| Definition embeds a rule                       | "*Document* — a file that must be under 50MB"                                                                                                                                   | Split: keep "what it is" in Definitions; move "what must be true" to Business Rules                                                                                        |
| Missing or unstable BR/AC identifiers          | Rule or AC is added as plain text, or existing IDs are renumbered after edits                                                                                                   | Assign stable **`BR N`** / **`AC N`** IDs, never renumber, and deprecate obsolete items instead of deleting                                                                |
| AC lacks explicit verification target          | `AC 3` checks file-size rejection but doesn't reference `BR 2`                                                                                                                  | Add "Verifies BR N" (or `sid`) so rule→AC traceability is explicit                                                                                                         |
| BR/AC "home" is ambiguous                      | Same identifier-level rule filed under **landing** UC but also cited from **campaign config** and analytics                                                                     | Pick **one** canonical placement (**global** if no single journey owns it); align **`Related ACs`** text and **`Verifies`** lines accordingly—do not duplicate the row     |
| Use case lists Related ACs that live elsewhere | UC narrative says "Related ACs: AC5–AC10" but those ACs only exist in the global section                                                                                        | Update the narrative to cite global ACs explicitly or move ACs to match the stated ownership—avoid stakeholder confusion                                                   |
| **Use case has no main flow**                  | UC `desc` is a one-line summary like *"Cookie and DB honor evaluation; honor most recent eligible record."* with trigger / actors / pre / post but no steps                     | **Spec cannot become software.** Capture the numbered main success scenario and each alternate scenario in the UC's narrative `desc` (Markdown). ACs do not replace flows. |
| **Mechanics over content**                     | Skipping flow capture to keep `spectr uc add -d` short, fit a batch, or save context                                                                                            | The PM goal is implementable behavior. Write the flow first; **then** persist via `references/spectr-cli-for-pm.md`. Throughput is not a valid reason to drop content.     |
| **Migration loses prose**                      | Importing a transcript / plan into Spectr and storing only the trigger + summary, leaving the numbered "Main success scenario" / "Alternate scenarios" behind in the source doc | Treat flows as first-class content. Copy the numbered steps into each UC's narrative, then refine. Reconciliation (Phase 2 step 6) covers this.                            |
| **Teaser-only use case**                       | A single sentence in `desc` that gestures at the flow ("Persist result; issue cookie; routing per rules.")                                                                      | Replace with explicit numbered steps for the main path and each alternate, including system responses and the postcondition each branch reaches.                           |

---

# Pre-Finalization Checklist

Run in order: workflow gates first (Part 1), then content gates (Part 2), then persistence and user validation.

**Workflow (Part 1):**

- [ ] **Breadth covered**: every metric, chart, and named outcome had ≥1 discovery question asked, with the answer reflected in the spec
- [ ] All requirements trace to user needs (WHY is clear)
- [ ] Architect questions answered in `questions.md`
- [ ] `questions.md` complete and up-to-date per `references/how_to_use_questions.md`
- [ ] **Plan/spec reconciliation** (if applicable): every user-facing item from prior plans/specs is either in the active Spectr spec or explicitly out of scope

**Content (Part 2):**

- [ ] **Every use case carries its main success scenario as numbered steps** (actor actions + system responses) in the UC narrative — not a one-line summary
- [ ] **Every named alternate / exception path** (return visit, invalid input, mode toggles, blocked paths, …) is captured as its own short numbered flow, including the system's response and resulting
  postcondition
- [ ] Each use case has explicit **preconditions** and **postconditions** that match the flows above (postconditions cover both the success path and any alternate that ends differently)
- [ ] Each use case includes prose pointers to the **`BR`**s the flow depends on and the **`AC`**s that verify it (no duplicated rule text)
- [ ] All use case actors are human roles (no system components)
- [ ] Definitions section passes the Definitions Quality Checklist in `references/terms_and_definitions.md` (coverage, quality, cross-section consistency)
- [ ] Every term used in rules, AC, diagrams, and use cases appears in Definitions; no aliases or undefined terms remain
- [ ] Business rule **phrasing** conforms to `references/rule-speak-best-practices.md`; **rules vs. acceptance criteria** and **ID/traceability** discipline conform to
  `references/rules_vs_acceptance_criteria.md`
- [ ] Every business rule has stable **`BR N`** identifiers; nothing renumbered or deleted without deprecation
- [ ] Each acceptance criterion references the **`BR`**(s) or **`sid`** it verifies, so every business rule can be traced to verification
- [ ] Each **BR** / **AC** has one canonical placement: a **single** owning use case **or** the **global** change-set section; no duplicate text; **`Related ACs`** in use case prose matches that
  placement (apply `references/rules_vs_acceptance_criteria.md` § Placement)
- [ ] Acceptance criteria pass the Acceptance Criteria Quality Checklist in `references/bdd.md`

**Persistence and validation:**

- [ ] Structured spec edits follow **`references/spectr-cli-for-pm.md`** (identifiers, deprecation, granularity, units of work—exact rules are in that reference only)
- [ ] User validates spec meets their actual needs
