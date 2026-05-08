# Rules vs acceptance criteria

**How to phrase business rules** (RuleSpeak, glossary alignment, `br` vs **Definitions**) lives in **[rule-speak-best-practices.md](rule-speak-best-practices.md)**. This page contrasts **rules** and **acceptance criteria**, how to **identify and cite** them, and how to **use** them together—without repeating the RuleSpeak guide.

---

## How they differ

| | **Business rules** | **Acceptance criteria** |
|---|--------------------|-------------------------|
| **What they are** | Durable **policies and invariants** for the domain or product | **Testable conditions** for a **specific** change (feature, story, task, slice of work) |
| **Scope** | Broad, **cross-cutting**; reused wherever the policy applies | **Narrow**, tied to one delivery item |
| **Purpose** | Define **logic, constraints, permissions, calculations** at the vocabulary level | **Verify** that the change behaves as intended and **honors** cited rules |
| **Lifecycle** | **Stable** and long-lived unless policy changes | Change as the **feature or verification needs** change |
| **Perspective** | Abstract policy—not implementation detail | **Concrete** behavior and **observable** outcomes |
| **Shape** | Natural-language rules per **rule-speak-best-practices.md** | Scenarios (e.g. **Given / When / Then**) or equivalent checks |

---

## When to use each

**Write or change a business rule when** you are stating **policy**, **business logic**, or **invariants** that should stay **one wording** for many features; when you need **consistency** across the system; or when you are clarifying **constraints, permissions, or calculations** at the domain level.

**Write or change acceptance criteria when** you are delivering a **specific feature or story**; when you need to **align developers and testers** on “done”; when you want **testable** scenarios (including **QA** planning); or when you must **validate completeness** of that slice—not restate every policy from scratch.

---

## Using acceptance criteria well

* Tie each criterion to a **concrete** feature, story, or task.
* Cover **happy paths, edge cases, and failure cases** as appropriate.
* Make outcomes **observable and specific** (what the user or system shows or does—use the perspective the spec agrees on).
* **Cite** the **`BR`** (or Spectr **`br`** **`sid`**) that the scenario exercises instead of copying full rule text.
* Treat them as **definition of done** for that work, while the **rules** remain the **authoritative** policy text.

---

## Using rules together with ACs

1. **Rules carry policy; ACs carry scenarios.** If **policy** changes, update the **rule** (and glossary if needed). If only **how you prove** the feature changes, update **ACs** and tests.

2. **One main idea per rule.** ACs may bundle **many** checks for one story (edges, failures); each check can still **reference** the same **`BR`**s.

3. **Traceability:** acceptance criteria (and tests, tasks, comments) should **point at rule IDs** so rule → verification stays explicit.

---

## Rule and AC identification

Stable identifiers matter because ACs, tests, plans, Q&A, and audits **reference** rules and criteria by id—renumbering or silent deletion breaks those links.

### Format

* **Business rules:** **`BR`** + space + positive integer (`BR 1`, `BR 17`). **Per spec**, numbering starts at **`BR 1`**. Referencing a rule in **another** spec: qualify it (e.g. `Document Parsing / BR 4`).
* **Acceptance criteria:** same discipline with **`AC`** + integer, **per spec**.
* **Spectr:** `br` and `ac` rows use stable **`sid`** values—treat them like immutable handles when citing from prose.

### One rule, one statement

Each **`BR`** is a **single atomic** statement. Split compound logic into **multiple** **`BR`** rows, each with its own id.

### Authoring pattern (markdown specs)

```markdown
- **BR 1**: [atomic rule—wording per rule-speak-best-practices.md]
- **BR 2 — Short name**: [atomic rule]
```

### Stability

* **Never re-number** an existing **`BR`** or **`AC`**. New rules use the **next unused** integer (e.g. after **`BR 12`**, add **`BR 13`**, even if **`BR 5`** is deprecated).
* **Do not delete** published rules or criteria if anything might reference them; **deprecate** instead. Examples:

  `- **~~BR 5~~** *(DEPRECATED YYYY-MM-DD — reason)*: [original text]`

  or keep the line and add `**Status**: Deprecated (reason, date)` below.

  In Spectr, prefer **`br update --deprecated`** / AC deprecation patterns over deleting rows when traceability matters.

---

## Quick mental model

* **Rules** = the **law** (one durable statement of policy).
* **Acceptance criteria** = the **checklist** that shows the law is **followed** for **this** delivery—by **scenario**, not by duplicating the law each time.

---

## Placement: use case vs global

A spec stores **definitions** once, then **use cases** (journeys), then optional **global** **business-rules** and **acceptance-criteria** sections for the whole change set. **Every BR and AC has exactly one home**—either a single owning use case or the global section. Cross-references use prose (**`Verifies BR N`**, **`see change-set AC N`**); the row text itself appears **once**.

> The persistence mechanics (CLI, **`sid`**, batching, deprecation) for moving or relocating rows live only in **`using-spectr`**. This page covers **where** rows belong, not **how** to edit the file.

### Where each row goes

| Placement | Put here | Examples (non-exhaustive) |
|-----------|----------|---------------------------|
| **Under one use case** | BRs/ACs whose **primary** story is that journey: one actor, trigger, and success path | "When the ops user assigns providers…", "When the candidate lands…", card/analytics scenarios scoped to that UC |
| **Global (after all use cases)** | BRs/ACs that are **cross-cutting** or **not owned by a single journey** | Identifier/uniqueness policies reused everywhere; scope pointers ("defined in another spec"); **accepted risk** or platform-wide invariants; one-time **migration / backfill**; ACs that **verify** BRs referenced from **multiple** flows |

### Heuristics

1. **One canonical home.** If the team can name **one** UC that "this is the main home for" the rule or AC, **nest** it there. If two UCs both feel primary, **decide a single canonical home** (or move to **global**) and use **`Verifies BR N`** / **`Related ACs`** in prose for cross-references—**do not** duplicate the same rule or AC text in two places.

2. **Cross-reference, don't duplicate.** When a globally placed BR is exercised by ACs in multiple use cases, each AC cites **`BR N`** (or **`sid`**); the BR text itself appears exactly once, in the global section.

3. **Related ACs hygiene.** **`Related ACs`** (and **`Related BRs`** if you use that pattern) inside a use case narrative must match reality: list only ACs/BRs that **live** under that UC, **or** explicitly point readers to a global row (e.g. "see change-set AC 12") so the spec is not misleading.

4. **Reorganization is a content decision.** Choosing where a BR or AC lives—and moving it after scope changes—is a **product** decision driven by ownership and audience. **How** to edit the file (stable IDs, add/delete, deprecation, batching) is **`using-spectr`** only.

### Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Duplicated rule text | Identical BR text appears under two use cases (or under a UC and globally) | Pick one canonical home; cite by **`BR N`** from the other location |
| `Related ACs` lies | UC narrative says "Related ACs: AC5–AC10" but those ACs only exist in the global section | Update the narrative to cite global ACs explicitly, or move the ACs to match the stated ownership |
| Cross-cutting BR nested under one UC | An identifier/uniqueness invariant filed under "landing" UC but cited from analytics, campaign config, etc. | Move the BR to the **global** section; update **`Verifies BR N`** in dependent ACs |
| Global section as dumping ground | BRs that have one obvious owning UC parked globally to "stay flexible" | Nest under that UC; reserve **global** for genuinely cross-cutting rules |
| Ambiguous home, no decision | Same rule cited from multiple places, no canonical placement chosen | Decide explicitly (UC or global), document the choice in the row, then update all citations |
