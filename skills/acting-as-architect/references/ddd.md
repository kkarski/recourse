### Section 1: Strategic Design (The Big Picture)
**The Goal:** Define boundaries and protect the business logic.

* **DO** identify the **Core Domain** first; it’s where you should spend 80% of your architectural effort.
* **DO** create strict **Bounded Contexts** to prevent a single "User" or "Product" model from becoming a bloated, confusing mess.
* **DO** use **Context Mapping** to visualize how different teams and systems talk to each other.
* **DO** treat **Subdomains** as business capabilities, not technical layers (like "Database" or "UI").
* **DO** buy or outsource **Generic Subdomains** (e.g., Auth, Email) so you can focus on custom logic.
* **DO** ensure that a change in one Bounded Context has zero side effects on the internal logic of another.
* **DO** align your team structures (SQUADS) with your Bounded Contexts to reduce communication overhead.

* **DON’T** try to create a "Unified Model" for the entire company; it’s a trap that leads to "The Big Ball of Mud."
* **DON’T** confuse a Bounded Context with a Microservice; a context is a logical boundary, a service is a deployment choice.
* **DON’T** ignore the "Upstream/Downstream" relationship; know who breaks when an API changes.
* **DON’T** let technical constraints (like a shared database) dictate your domain boundaries.
* **DON’T** over-engineer Supporting Subdomains; keep them simple and "good enough."
* **DON’T** allow "Leaky Abstractions" where one context's internal logic spills into another.
* **DON’T** start coding before you’ve mapped out the high-level domains and their interactions.

---

### Section 2: Tactical Design (The Building Blocks)
**The Goal:** Write code that mirrors the domain's mental model.

* **DO** prioritize **Value Objects** over Entities; if it doesn't need a unique ID over time, make it a Value Object.
* **DO** make Value Objects **immutable**; to change a "Price," you replace the object, you don't edit its properties.
* **DO** enforce business invariants (rules) strictly inside the **Aggregate Root**.
* **DO** keep **Aggregates** as small as possible to avoid performance bottlenecks and locking issues.
* **DO** use **Domain Events** to communicate state changes to other parts of the system asynchronously.
* **DO** use **Repositories** to hide the "how" of data persistence from the domain logic.
* **DO** name your methods after business actions (e.g., `ConfirmOrder()`) rather than generic setters (e.g., `SetStatus(3)`).

* **DON’T** create "Anemic Domain Models" (objects with only getters/setters and no logic).
* **DON’T** allow an Aggregate to hold a direct reference to another Aggregate; use IDs instead.
* **DON’T** put business logic in Services if it naturally belongs inside an Entity or Value Object.
* **DON’T** leak persistence details (like SQL types or ORM annotations) into your Domain Layer.
* **DON’T** use a Repository to "save" every tiny change; save the entire Aggregate once the operation is done.
* **DON’T** trigger side effects across Aggregates within the same transaction if you can avoid it.
* **DON’T** use Entities when a simple Value Object would suffice; it makes the system harder to test.

---

### Section 4: Context Mapping
**The Goal:** Manage the relationships between different Bounded Contexts.

* **DO** use an **Anti-Corruption Layer (ACL)** when integrating with messy legacy systems to protect your clean model.
* **DO** define a **Published Language** (like a well-documented JSON schema) for contexts that many others depend on.
* **DO** recognize "Partnership" relationships where two teams must succeed or fail together.
* **DO** use "Customer-Supplier" mappings when one team’s output is the essential input for another.
* **DO** explicitly document where a **Shared Kernel** exists (code shared between contexts) and keep it tiny.
* **DO** communicate the "Downstream" impact before making any breaking changes to a shared contract.
* **DO** use "Separate Ways" if the cost of integration outweighs the benefit of collaboration.

* **DON’T** let a downstream team dictate the model of an upstream team without a "Customer-Supplier" agreement.
* **DON’T** let the "Conformist" pattern happen by accident; only adopt another team's model if it truly fits yours.
* **DON’T** share a database schema between two Bounded Contexts; it’s the ultimate "hidden" coupling.
* **DON’T** build an ACL for every single integration; sometimes a simple "Conformist" approach is faster for non-core tasks.
* **DON’T** assume everyone is using the same definition of a term just because they are in the same company.
* **DON’T** ignore the political/organizational reality of how teams interact; it mirrors your software (Conway’s Law).
* **DON’T** allow a Shared Kernel to grow into a "General Purpose" library that contains business logic.

---

### Section 5: Distilling the Core Domain
**The Goal:** Focus your best resources on what actually makes the business money.

* **DO** spend your most senior engineering hours on the **Core Domain**.
* **DO** ruthlessly simplify or outsource everything that isn't "Core."
* **DO** create a **Domain Vision Statement** to keep the team aligned on what the "Core" actually is.
* **DO** look for "Hidden Gems"—sometimes a Supporting Subdomain evolves into a Core competitive advantage.
* **DO** treat the Core Domain as an evolving asset that requires constant refactoring and deep modeling.
* **DO** use the **Ubiquitous Language** most strictly within the Core Domain.
* **DO** differentiate between "Essential Complexity" (the hard business problem) and "Accidental Complexity" (bad code).

* **DON’T** "Gold Plate" (over-engineer) a Generic Subdomain like a login screen or a PDF generator.
* **DON’T** assume the most technically difficult part of the system is the Core Domain; difficulty $\neq$ business value.
* **DON’T** ignore a "Core" domain just because the legacy code there is scary; that’s exactly where you need to refactor.
* **DON’T** let "Supporting" logic clutter the "Core" logic; use separate packages or modules.
* **DON’T** outsource the development of your Core Domain to a third-party agency if you can avoid it.
* **DON’T** treat all Subdomains as equal in your sprint planning or budget.
* **DON’T** lose sight of the business goal by getting distracted by "Cool Tech" that doesn't serve the Core.

### **DDD Technical Glossary**
This glossary serves as a single source of truth for aligning engineering and business stakeholders. Use these definitions to audit your current architecture and ensure your **Ubiquitous Language** is consistent.

---
## **I. Strategic & Organizational Terms**
*Focus: How the business is partitioned and how teams interact.*

| Term | Definition |
| :--- | :--- |
| **Bounded Context** | A clear boundary (logical or physical) within which a specific domain model is defined and applicable. Terms inside this boundary have zero ambiguity. |
| **Core Domain** | The specific part of the business that provides a competitive advantage. It is the highest priority for custom development and senior talent. |
| **Subdomain** | A granular slice of the overall business. Can be **Core** (unique value), **Supporting** (necessary but simple), or **Generic** (standard/off-the-shelf). |
| **Context Mapping** | The process of documenting the relationships (e.g., Upstream/Downstream) and data flow between different Bounded Contexts. |
| **Ubiquitous Language** | A shared, rigorous vocabulary used by both Domain Experts and Developers to ensure the code matches the business mental model. |
| **Anti-Corruption Layer (ACL)** | A translation layer that isolates a clean Bounded Context from a messy or legacy external system, preventing "model leakage." |
| **Shared Kernel** | A small, shared piece of the model (code or database) that two or more teams agree to maintain together. High risk, high coupling. |

---

## **II. Tactical & Implementation Terms**
*Focus: How the business logic is structured within the code.*

| Term | Definition |
| :--- | :--- |
| **Aggregate** | A cluster of domain objects (Entities and Value Objects) that are treated as a single unit for data changes and consistency. |
| **Aggregate Root** | The "gatekeeper" Entity of an Aggregate. External objects can only hold a reference to the Root, never its internal children. |
| **Entity** | An object defined by its **identity** (e.g., a unique ID) rather than its attributes. It has a lifecycle and can change state over time. |
| **Value Object** | An immutable object defined entirely by its **attributes**. It has no identity (e.g., $10 USD is $10 USD regardless of which "instance" it is). |
| **Domain Event** | A record of a significant business occurrence (e.g., `OrderPlaced`). Usually used to trigger side effects in other Aggregates or Contexts. |
| **Repository** | A service-like interface that provides an abstraction for retrieving and persisting Aggregates, hiding database complexity from the domain. |
| **Domain Service** | A stateless service used for business logic that doesn't naturally fit inside a single Entity or Value Object (e.g., a complex tax calculator). |

---

## **III. Architectural "Red Flags"**
*Focus: Common patterns that signal a failure in DDD application.*

* **Anemic Domain Model:** A model where objects are just "data bags" with getters and setters, and all logic lives in external service layers.
* **Big Ball of Mud:** A system with no discernible architecture where boundaries are blurred and changes cause unpredictable ripples.
* **Leaky Abstraction:** When technical details (like SQL fragments or UI constraints) bleed into the Domain Layer.
* **Conformist:** When a team is forced to use an upstream team's flawed or mismatched model because they lack the resources to build an ACL.

---

**Would you like me to generate a Markdown file version of this glossary that you can drop directly into your project's GitHub repository?**