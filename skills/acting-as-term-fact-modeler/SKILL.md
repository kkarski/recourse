---
name: acting-as-term-fact-modeler
description:
  Use when new information is gathered from user and terms and facts need to be defined or clarified.
---

You review feature specifications, Q&A, and glossary definitions to keep a **term-fact model** (terms as entities, facts as relationships) aligned with RuleSpeak and the spec.

## Term and fact modeling (RuleSpeak)

Spectr term definitions should align with a clear **fact model**: stable noun phrases (terms) and expressive verb phrases (facts) that rules and acceptance criteria reuse verbatim.

Declare atomic facts first.

**Facts (examples):**

- customer places order
- customer holds account

**Rule (follows those facts exactly):**

- A customer may place an order only if the customer holds an account.

Imprecise or free-form wording that does not trace to named facts invites inconsistency as the spec scales.

### Prefer precise relationships over vague “have”

“Have” hides the real relationship between independent concepts. Replace with a specific fact and reuse it in rules.

**Weak:** A team must have a manager.

**Fact:** team is managed by manager

**Exception:** “Have” is acceptable for **direct properties** of a thing, e.g. account has outstanding balance.

### Name every thing a rule depends on (disambiguate)

Omitting facts forces readers to guess which object’s balance or limit applies.

**Ambiguous rule:** An order must not be shipped if the outstanding balance exceeds credit authorization.

**Facts (examples):**

- customer places order
- customer has credit authorization (property)
- customer holds account
- account has outstanding balance (property)

Develop and reuse terms for derived or threshold concepts where many rules share the same number or formula (e.g. name “maximum contribution per family per year” instead of embedding `$500` everywhere).

### Small wording habits that keep facts readable

- Use **singular** subjects with a leading “a(n)” (read as “each”), e.g. “A programmer must work on a system,” not “Programmers must…”.
- For numeric thresholds, make the **subject numeric**, e.g. “The number of seats for a course section must not exceed 30,” not “A course section must not include more than 30 seats.”
- Avoid **actor** subjects when the rule governs a thing or event, e.g. prefer “A withdrawal for an account may be made only if the account is active” over centering “customer” when third parties or the bank might act.

## Term-fact model (ER diagram in the spec)

The spec stores **one** body-level term-fact model as a Mermaid **erDiagram** under `div type=term-fact-model` (see `spectr/resources/spectr.xsd`). Entities are **terms**; relationship labels are **facts**. Property-style facts (e.g. outstanding balance on account) may appear as attributes on an entity in the diagram when they are not separate terms.

Run `spectr tfm --help` before TFM commands. Subcommands: `add`, `read`, `update`, `delete` (each has `--help`).

```bash
spectr tfm read
spectr tfm add -d 'erDiagram
    CUSTOMER ||--o{ ORDER : places'
spectr tfm update -d 'erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--|| ACCOUNT : holds'
```

Diagram source must start with `erDiagram` (no markdown fence). Use `spectr def list` / `spectr def add` for glossary rows; keep **definitions** and the **ER diagram** consistent.

## When invoked

1. Read the feature spec (`spec.html`), companion questions (`*_questions.html` via `spectr qs list`), and existing glossary (`spectr def list`).
2. Run `spectr tfm read` if a model exists; run `spectr def --help` / `spectr tfm --help` when unsure of flags.
3. Extract terms and facts from scope, use cases, business rules, acceptance criteria, definitions, and Q&A answers.
4. Build or revise a Mermaid erDiagram: one entity per canonical term; relationship verbs as fact labels; cardinalities that match the domain.
5. **Normalize terminology** — pick one canonical name per concept; align `spectr def` entries and the ER diagram; fix aliases in rules/AC only when you are also updating those sections (stay in scope for this agent: defs + TFM).
6. **Find ambiguity** — same label for different concepts, missing entities implied by rules, vague “have”/“manage” without a named fact, properties attached to the wrong entity.
7. **Verify consistency** — every fact label in the diagram should appear (or be implied) in definitions or spec text; every critical term in BR/AC should appear as an entity or documented property; no orphan entities with no rules/AC touchpoint unless defined for future use.
8. Update the diagram with `spectr tfm add` (first time) or `spectr tfm update`; update glossary with `spectr def add` / `update` / `delete` as needed.
9. If blocking ambiguity remains, ask in Spectr Q&A per `skills/references/how_to_use_questions.md` (do not use side channels).

### Clarifying questions (required style)

- Review `spectr qs list` before asking.
- One clear, bounded question per thread; include context and impact.
- Offer **three likely answers** plus an explicit option for the user to supply their own wording.
- Record rationale when answering; deprecate obsolete threads instead of deleting.

Example:

```bash
spectr qs ask -d "Should 'credit authorization' be modeled as a separate term (entity) or as a property of Customer? Impact: BR12 and the term-fact ER diagram.

Options:
A) Separate entity CREDIT_AUTHORIZATION linked to Customer
B) Property on Customer only (no extra entity)
C) Other (please specify)"
```

## Severity when reporting

- **Critical:** Contradictory facts or terms between diagram, definitions, and normative BR/AC.
- **Major:** Missing entities/facts needed to read rules without guessing; duplicate terms for one concept.
- **Minor:** Naming/style (singular “a customer”, numeric subject) or diagram layout only.

Report changes made (TFM + def sids) or stay silent if the model and glossary are already consistent.
