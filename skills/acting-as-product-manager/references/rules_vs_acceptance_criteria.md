## **How to use Rules**

* Write as **clear, general logic** that applies across the system
* Use structured patterns like **“If X, then Y (unless Z)”**
* Keep each rule **atomic** (one idea per rule)
* **Define key terms and thresholds** explicitly
* Focus on **what must be true**, not implementation details
* Make rules **reusable** across multiple features
* Ensure they are **unambiguous and testable in principle**

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
