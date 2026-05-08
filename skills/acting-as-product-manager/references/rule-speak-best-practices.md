# RuleSpeak sentence forms — examples and best practices

This guide summarizes **RuleSpeak** sentence patterns for writing **natural-language business rules** in English. It is derived from *RuleSpeak Sentence Forms* (Version 2.2, Business Rule Solutions, LLC; Ronald G. Ross), which aligns with SBVR (*Semantics of Business Vocabulary and Business Rules*). Use it for **operational, practicable guidance**—not as implementation syntax for a rule engine.

---

## Purpose and scope

| Use RuleSpeak for | Do **not** use it as |
|-------------------|----------------------|
| Clear business communication | System design or automation blueprints |
| Consistent wording across a large rule set | Laws, regulations, contracts, or top-level policy prose (different register) |
| Day-to-day operational decisions by authorized staff who know the vocabulary | Technical “if–then” rule-engine notation |

**Success criterion:** another practitioner can read the rule and know **what is mandatory, forbidden, or explicitly allowed**—without guessing implementation.

---

## Definitions, terms, and the business rules section (Spectr)

In a Spectr feature spec, **term definitions** and **business rules** live in different parts of the model, but they connect through **one shared vocabulary**.

### How they relate

- **Definitions** (glossary / `def`): Each row is **one term** and its **meaning**—the canonical names for actors, domain nouns, states, enumerations, metrics, and qualified phrases (e.g. how the business uses “high-risk customer” or “gold customer”). Definitions fix **what** each term denotes.
- **Business rules** (`br`): Each row is **normative** guidance in natural language (using RuleSpeak patterns below). Rules talk **about** the things named in definitions: subjects, objects, conditions, and classifications should use those **same terms** consistently.

Spectr does **not** attach a formal pointer from a specific `br` to a specific `def`. The link is **semantic**: important nouns and qualifiers in a business rule should match **Definitions**—same wording, no stray synonyms. If a rule needs a concept that is not yet named there, **add or refine a definition first**, then write the rule using that term.

### Division of labor

| Definitions | Business rules |
|-------------|----------------|
| Say **what** a term means (scope, categories, thresholds needed to use the term clearly). | Say **what must, must not, may, or need not** hold, using those terms. |
| Avoid embedding **must**, **may**, **need not**, or obligation-style **if/then** in the definition body—move that to a `br`. | Do not **redefine** concepts; rely on the glossary and use agreed term names. |

### Practices for cross-referencing by language

1. **Vocabulary before rules** — Define or stabilize terms in **Definitions** before stating rules that depend on them.
2. **One term per definition row** — Matches Spectr’s “one `def` = one term + meaning” discipline; keeps rules traceable to a single gloss.
3. **Reuse labels exactly** — Use the same spelling, qualifiers, and phrasing as in the glossary (e.g. “retired employee” not “former worker” unless both are defined and distinguished).
4. **Thresholds and states** — Put numeric cutoffs and allowed values in **Definitions** when they define a term; put obligations and prohibitions about those values in **business rules**.
5. **Stable rule ids** — Each `br` has its own `sid` for citations in ACs, tests, and Q&A; definitions have their own `sid`s. References between sections stay **by term name + rule id**, not by a built-in graph.

Together, **Definitions** supply the dictionary; the **business rules** section states the policies **in that dictionary’s language**.

---

## Keywords (use them deliberately)

### Rule keywords (business **rules** — they remove freedom)

Every **business rule statement** includes **exactly one** of:

- **must** — obligation or conditional obligation  
- **only** — appears with **may** for *conditionally allowed* patterns (`… may … only …`)

### Advice keywords (statements of **advice** — they do not remove freedom)

A **statement of advice** uses **exactly one** of:

- **may** — something is **allowed** (permission), never “might happen”
- **need not** — something is **not required**

**Important:** **may** + **only** in the same sentence is always a **business rule**, not advice.

### Word choice (usage notes)

| Term | Preference |
|------|------------|
| **must** vs **shall** | Prefer **must** for practicable rules (shall is typical of laws/contracts). |
| **must** vs **should** | Prefer **must** in the rule text; record enforcement strictness **elsewhere**, not by swapping should/must. |
| **may** | Always **permission** (“is allowed”). Never use **may** to mean **might** (possibility). |

---

## Sentence forms (quick reference)

### 1 — Something is **required**

| Pattern | Meaning |
|---------|---------|
| `… must …` | Unconditional requirement |
| `… must … if …` | Requirement when a condition holds (**if** = condition ongoing / whenever true) |
| `… must …` (with qualifying nouns) | Requirement qualified by adjectives/phrases on terms (no **if** needed) |
| `… must be computed as …` | Aggregations, formulas (sum, average, etc.) |
| `… must be considered … if …` | Classification / derivation when conditions hold |
| `… must be performed … when …` | Action at **specific point(s) in time** — use **when**, not **if** |

**Examples**

- An order must have a promised shipment date.  
- A shipment must be insured if the value of the shipment is greater than $500.  
- A student must be enrolled in at least 2 courses by the close of registration.  
- A product’s cost must be computed as the sum of the cost of all the product’s components.  
- A customer must be considered high-risk if the outstanding balance exceeds $1,000 on each of their last three successive invoices.  
- The procedure ‘Send-Advance-Notice’ must be performed for an order **when** the order is shipped.

### 2 — Something is **disallowed**

| Pattern | Meaning |
|---------|---------|
| `… must not …` | Forbidden (unconditional or qualified on the noun phrase) |
| `… must not … if …` | Forbidden when a condition holds |

**Examples**

- The number of seats for a course section must not exceed 30.  
- An order must not be shipped if the outstanding balance of the customer’s account exceeds the customer’s credit authorization.  
- A high-risk customer must not place an order for a big-ticket item.

### 3 — Something is **conditionally allowed** (restriction)

| Pattern | Meaning |
|---------|---------|
| `… may … only if …` | Allowed **only** under stated conditions |
| `… may … only …` | Allowed **only** in situations stated without **if** (e.g. qualifying the object) |

**Examples**

- A customer may place an order only if the customer holds an account.  
- A shipment fee may be waived only for an order placed by an in-state customer.

### 4 — **Advice**: something is **allowed**

| Pattern | Meaning |
|---------|---------|
| `… may …` | Clarifies permission (does not by itself forbid other cases—add a separate rule if needed) |

**Examples**

- A person of any age may hold a bank account.  
- A retired employee may work part-time in Alberta.

### 5 — **Advice**: something is **not required**

| Pattern | Meaning |
|---------|---------|
| `… need not …` | Not mandatory |
| `… need not … if …` | Not mandatory under a condition |

**Examples**

- A customer need not place an order.  
- A credit check need not be requested for an order if the amount of the order is under $1,000.  
- A gold customer need not pay in cash for an order with an international destination.

---

## Best practices

1. **One rule keyword per business rule** — exactly one of **must** / **only** (the latter as part of the `may … only …` pattern). Advice statements use **may** or **need not**, not those rule keywords.

2. **Write complete, grammatical sentences** with normal English structure.

3. **Start with an explicit subject** — preferably a **singular** noun (possibly qualified). Avoid IT-style “If … then …” as the main structure for business-facing rules: it hides the subject and is awkward for simple obligations (e.g. “An employee must have a name.”).

4. **Qualify with `if`, embedded qualifiers, or `when`:**
   - Use **`if`** when the condition is **continuously** relevant (whenever it holds, the rule applies).  
   - Use **`when`** when the rule applies at **specific moments** (e.g. at registration, at shipment).  
   - Prefer natural qualification on nouns when it reads clearly (“A **retired** employee must not …”).

5. **Avoid `… may … if …` without `only`.** It is easy to misread.  
   - Weak: *An item may be returned if some proof of purchase is provided.* (Advice that only addresses the case where proof exists; it does not define the no-proof case.)  
   - Stronger if the intent is restriction: *An item may be returned **only if** some proof of purchase is provided.*

6. **Advice does not fill gaps.** *A retired employee may work part-time in Alberta* does not restrict non-retired employees or other locations; add explicit **must not** / **may … only** rules if those cases matter.

7. **`need not … if …` states an exemption** from obligation; it does **not** say what happens above the threshold. Example: *A credit check need not be requested for an order if the amount is under $1,000* does not require checks for larger orders—you need a separate rule if checks are required there.

8. **Default freedom.** Nothing is mandatory unless a **business rule** says so; **nothing is forbidden** unless stated (except where **must not** applies).

9. **Instances vs categories.** If a term might be read either way, put the **instance** in **single quotes** (e.g. a ‘flammable’ sticker as one label instance, not the class “flammable stickers”).

10. **Glossary alignment.** Write business rules using the **same term labels** as in the **Definitions** section; introduce new concepts there before relying on them in a `br` (see *Definitions, terms, and the business rules section* above).

---

## Source

RuleSpeak Sentence Forms, Version 2.2 — *Specifying Natural-Language Business Rules in English* (Business Rule Solutions, LLC; © 2001–2009). RuleSpeak was used as a reference notation in the development of SBVR.

Commercial reuse requires permission from BRS; in-house non-commercial use is permitted per the original notice.
