# Terms and Definitions

**Why this matters**: Business rules, acceptance criteria, and BDD scenarios are only as clear as the words they use. A spec with undefined or inconsistent terms produces ambiguous rules, untestable acceptance criteria, and divergent implementations. RuleSpeak (the Business Rules Manifesto) and BDD (via Domain-Driven Design's *ubiquitous language*) both require that every concept have **one name** and **one definition** that the whole team — business, product, engineering, QA — uses identically.

This document defines how to establish, maintain, and validate definitions in Spectr business specs.

## Core Principle

> **Rules and acceptance criteria are built on top of terms and facts.** Define the vocabulary first; then write the rules and scenarios using only that vocabulary.

If a rule or scenario uses a word that is not in the Definitions section, either add it to Definitions or change the rule to use a defined term. No exceptions.

## What Must Be Defined

For every spec, the Definitions section must cover:

| Category | What to define | Example |
|----------|----------------|---------|
| **Actor / Role** | Each human role that interacts with the system | *User, Administrator, Reviewer* |
| **Concept / Entity** | Each domain noun the spec talks about | *Document, Campaign, Subscription* |
| **State** | Each value in a lifecycle | *pending, processing, completed, failed* |
| **Status / Enum** | Each value in a non-lifecycle enumeration | *priority: low / medium / high* |
| **Event** | Each business event that triggers behavior | *DocumentUploaded, PaymentReceived* |
| **Metric / Measurement** | Each quantitative measure with its unit and aggregation | *Active users (count, distinct, last 30 days)* |
| **Qualified term** | Every adjective/qualifier used in a rule or AC | *"significant ad" = ad with ≥1,000 impressions in the last 24h* |
| **Fact / Relationship** | Verb phrases connecting two terms (when relevant) | *"User OWNS Document"; "Document IS-IN State"* |

## RuleSpeak Principles for Definitions

1. **Atomic** — One term, one concept. Don't define "User and account" together.
2. **Business language** — Use vocabulary the user/stakeholder uses. Avoid technical jargon ("entity", "service", "API", "row"). If a stakeholder wouldn't say it, don't define it that way.
3. **Single source of truth** — Every term has exactly one definition. If two definitions disagree, one is wrong.
4. **No circularity** — A definition must not contain the term being defined (e.g., "A *valid document* is a document that is valid" is forbidden).
5. **No embedded rules** — A definition states *what something is*, not *what must be true about it*. Move "must"/"shall"/"may"/"if-then" statements to the Business Rules section.
   - Bad: "*Document* — a file that must be under 50MB and not corrupted."
   - Good: "*Document* — a file uploaded by a User for processing." Then a separate rule: "If a Document is over 50MB, the system rejects it."
6. **Unambiguous and testable** — A reader must be able to determine, for any candidate object, whether the definition applies. Vague adjectives ("significant", "large", "recent") must include a threshold.

## BDD Ubiquitous Language Principles

1. **Same concept, same name, everywhere** — In Use Cases, Business Rules, Acceptance Criteria, Entity Definitions, Activity Diagrams, and Event Sequences, the same concept must be referenced by the same term. No synonyms.
2. **Gherkin uses defined terms only** — Every noun in a Given/When/Then must appear in the Definitions section (or be a primitive like "the system", "a number").
3. **States and statuses match the Definitions** — If the Definitions section says states are `pending`, `processing`, `completed`, `failed`, then a scenario must NOT say "queued", "in-progress", or "done".
4. **Avoid pronouns across steps** — Repeat the term rather than relying on "it" or "they" across Given/When/Then.
5. **No technology in scenarios** — "the API", "the database", "the queue" are implementation. Use business terms ("the system", "the Document", "the cache" only if cache is a defined business concept).

## Definition Format

Each entry in the Definitions section should follow this format:

```markdown
**Term** — short business-language definition (one or two sentences).
- Aliases: (synonyms used elsewhere — list them so they can be eliminated)
- Examples: (concrete instances)
- Counter-examples: (what it is NOT — useful for ambiguous concepts)
```

**Worked example:**

```markdown
**Significant ad** — an ad that received at least 1,000 impressions in the previous 24-hour window.
- Aliases: "popular ad" (do not use), "trending ad" (do not use)
- Examples: an ad with 1,500 impressions yesterday qualifies; an ad with 50,000 lifetime impressions but only 300 in the last 24h does NOT qualify
- Counter-examples: ads that have not been served in the last 24h
```

## Process for Establishing Definitions

1. **Extract candidate terms early** — During artifact inventory (Phase 1 Step 1), every metric, chart, named concept, qualified adjective, state, and status becomes a candidate term.
2. **Define before drafting** — Before writing a Business Rule or Acceptance Criterion that uses a term, the term must already exist in the Definitions section. If it doesn't, add it first.
3. **Refine with each answer** — When the user clarifies a term ("by 'significant' I mean ≥1000 impressions"), update the Definitions section immediately.
4. **Reconcile aliases** — When the user uses two words for the same thing ("user" and "account holder"), pick one as canonical, list the other as an Alias, and replace it everywhere in the spec.
5. **Lock states/statuses** — As soon as a lifecycle is discovered, lock the exact state names. All rules, AC, state diagrams, and events must use those exact names.

## Anti-Patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **Synonym sprawl** | "user", "customer", "account holder" used interchangeably | Pick one canonical term, list others as Aliases, replace globally |
| **Undefined term** | Rule/AC uses a noun that has no definition | Add the term to Definitions, or rewrite using a defined term |
| **Ambiguous adjective** | "significant", "valid", "complete", "recent" with no threshold | Define the term with a numeric or rule-based threshold |
| **Definition-as-rule** | Definition contains "must", "shall", "if/then" | Split: keep "what it is" in Definitions, move "what must be true" to Business Rules |
| **Circular definition** | "A *valid User* is a User that is valid" | Rewrite using primitive concepts and observable conditions |
| **Implementation jargon** | Definition uses "entity", "table", "service", "endpoint" | Rewrite in business language |
| **State name drift** | Spec uses `pending`; AC uses "queued"; diagram uses "Awaiting" | Lock canonical state names; replace everywhere |
| **Missing alias map** | Stakeholder says "campaign" but plan says "promotion" | Record both, pick canonical, mark the other as alias |
| **Hidden polymorphism** | Same term means different things in different sections (e.g., "User" sometimes means logged-in person, sometimes any visitor) | Split into two distinct terms with distinct names |

## Quality Checklist

Use this to validate the Definitions section and the spec's term consistency.

### Coverage
- [ ] Every actor/role used in the spec is in Definitions
- [ ] Every domain entity/concept named in the spec is in Definitions
- [ ] Every state in any lifecycle is in Definitions, with exact spelling
- [ ] Every status/enumeration value is in Definitions
- [ ] Every business event is in Definitions
- [ ] Every metric is in Definitions, with unit and aggregation
- [ ] Every qualifying adjective ("significant", "large", "recent") has a defined threshold

### Quality
- [ ] No definition contains the term being defined (no circularity)
- [ ] No definition contains "must", "shall", "may", or "if/then" (no embedded rules)
- [ ] No definition uses implementation jargon (entity, service, API, row, endpoint, etc.)
- [ ] Each term has exactly one definition (no duplicates with conflicting wording)
- [ ] Aliases are listed where stakeholders use multiple words for one concept
- [ ] All ambiguous adjectives have explicit thresholds

### Consistency (cross-section)
- [ ] Business Rules use only terms from Definitions
- [ ] Acceptance Criteria (Given/When/Then) use only terms from Definitions
- [ ] Use Case actors match Definitions exactly (same casing, same wording)
- [ ] Entity state diagrams use the exact state names from Definitions
- [ ] Event Sequence Diagrams use the exact event names from Definitions
- [ ] Activity Flow Diagrams use the exact term names from Definitions
- [ ] No alias appears in any rule, AC, or diagram (only the canonical term)

## Mental Model

| Layer | Built on | Contains |
|-------|----------|----------|
| Acceptance Criteria | Business Rules + Terms | Concrete, testable scenarios |
| Business Rules | Terms + Facts | "If X, then Y (unless Z)" using defined terms |
| Facts | Terms | Verb-phrase relationships ("User OWNS Document") |
| Terms | — | Atomic business-language nouns and qualifiers |

You build upward: terms first, then facts, then rules, then scenarios. Skipping the foundation is the single largest source of spec ambiguity.
