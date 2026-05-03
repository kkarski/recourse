## **How to use Rules**

* Write as **clear, general logic** that applies across the system
* Use structured patterns like **“If X, then Y (unless Z)”**
* Keep each rule **atomic** (one idea per rule)
* **Define key terms and thresholds** explicitly
* Focus on **what must be true**, not implementation details
* Make rules **reusable** across multiple features
* Ensure they are **unambiguous and testable in principle**
* **Assign each rule a stable, unique ID** (see "Rule Identification & Management" below)

---

## **Rule Identification & Management**

Every business rule must have a stable, unique identifier so that acceptance criteria, tests, code comments, change requests, and architect/engineer questions can reference it unambiguously. The same management discipline applied to acceptance criteria (`AC N`) applies to business rules (`BR N`).

### **ID format**

* Use the prefix **`BR`** (Business Rule) followed by a space and a positive integer, e.g. `BR 1`, `BR 2`, `BR 17`.
* IDs are **per-spec**: numbering restarts at `BR 1` in each `{feature}_business_spec.md`. Cross-spec references must qualify the ID with the spec name (e.g. `Document Parsing / BR 4`).
* Each rule is a single atomic statement. Compound rules ("If A and B, then C; unless D, then E") must be split into multiple `BR` entries, each with its own ID.

### **Authoring format**

```markdown
- **BR 1**: [Atomic rule, e.g. "If a Document file size exceeds 50 MB, the system must reject the upload."]
- **BR 2**: [Atomic rule]
- **BR 3**: [Atomic rule]
```

When a rule has a name in addition to an ID, place the name after the ID:

```markdown
- **BR 4 — File-size limit**: If a Document file size exceeds 50 MB, the system must reject the upload.
```

### **Stability requirements**

These mirror the acceptance-criteria management rules:

* **Never re-number a business rule once created.** Once `BR 7` exists, that ID is permanent. Adding, removing, or reordering other rules must not shift `BR 7`.
* **Never delete a business rule once created.** If a rule is no longer needed, mark it deprecated rather than removing it. Use one of:
  * `- **~~BR 5~~** *(DEPRECATED YYYY-MM-DD — reason)*: [original rule text]`
  * Or keep the entry and add a `**Status**: Deprecated (reason, date)` line beneath it.
* **New rules take the next unused number.** If the highest existing rule is `BR 12`, the next new rule is `BR 13`, even if `BR 5` is deprecated.
* **Acceptance criteria reference rules by ID.** Each `AC N` should cite the `BR N`s it verifies (e.g. "Verifies BR 3, BR 7"). This makes the rule→AC traceability explicit and machine-checkable.

### **Why this matters**

Stable IDs let downstream artifacts (acceptance criteria, test cases, plan tasks, architect Q&A, code comments, audit trails) point at a rule without re-quoting it. Renumbering or deleting rules silently breaks every one of those references.

---

## **How to use Acceptance Criteria**

* Tie them to a **specific feature, story, or task**
* Write as **testable scenarios** (e.g., “Given / When / Then”)
* Include **happy paths, edge cases, and failure cases**
* Make outcomes **observable and specific** (what the user/system sees or does)
* Reflect how the feature behaves from a **user or system perspective**
* Ensure they collectively **demonstrate the rules are enforced**
* Use them as a **definition of done** for the work

---

## **How they are different**

* **Scope**

  * Rules → broad, system-wide
  * Acceptance criteria → narrow, feature-specific

* **Purpose**

  * Rules → define logic and constraints
  * Acceptance criteria → verify a feature works

* **Lifespan**

  * Rules → stable and long-lived
  * Acceptance criteria → change per feature or task

* **Perspective**

  * Rules → abstract/system logic
  * Acceptance criteria → concrete behavior and outcomes

* **Format**

  * Rules → “If / then / unless”
  * Acceptance criteria → “Given / When / Then”

---

## **When to use each**

**Use Rules when:**

* You’re defining **business logic or policies**
* You need **consistency across multiple features**
* You’re clarifying **constraints, permissions, or calculations**
* You want a **single source of truth** for how something works

**Use Acceptance Criteria when:**

* You’re building or refining a **specific feature or user story**
* You need to **communicate expectations to developers/testers**
* You want to **validate that a feature is complete and correct**
* You’re writing **tests or planning QA checks**

---

## **Quick mental model**

* Rules = **the law**
* Acceptance criteria = **the checklist that proves the law is followed**

---

If you want to go a level deeper, I can show how poor requirements usually mix these up—and how separating them makes everything clearer fast.
