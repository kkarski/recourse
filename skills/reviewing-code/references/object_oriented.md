# Object-Oriented Best Practices — MUST / MUST NOT / MAY

Rules for reviewing object-oriented code: modeling, encapsulation, cohesion, relationships, polymorphism, and leaky abstractions.

## Modeling Real-World Things

### MUST
- Model each **real-world concept** as one class. Use a domain noun for the name — not a verb, a database table, or an implementation detail.
- Keep **data and behavior together**. A class with only getters/setters and a separate service with all the logic is an anemic domain model — it violates the core idea of OOP.
- Make the class **honest about what it represents**. An `Invoice` must behave like a real invoice, not a mix of invoice logic, database columns, serialization, and rendering.
- Name methods so a **domain expert recognizes them**: `applyLateFee()`, not `updateStatus()`. Names should communicate intent, not mechanism.

### MUST NOT
- End class names with `-er` or `-or` unless they model a real actor in the domain (`Manager` as a role, not `OrderManager`). `Processor`, `Handler`, `Controller` are often procedural code in OOP clothing.
- Mirror **database schemas** as domain classes. A 1:1 mapping to tables with no business behavior is a record, not an object.
- Use **primitive obsession** — wrap domain values in their own types. `ship(TrackingId, EmailAddress, Money)` is self-documenting; `ship(String, String, String)` is not.
- Put **infrastructure annotations** (JSON tags, column mappings) directly on domain classes. Those couples the domain to the infrastructure layer.

### MAY
- Use **value objects** (immutable, equality-by-value) for `EmailAddress`, `Money`, `DateRange`. They let the type system enforce rules that plain strings and numbers cannot.
- Split a domain class into **smaller collaborating classes** when a subset of fields forms a coherent sub-concept. E.g. extract `ShippingDetail` from `Order`.
- Accept a **thin domain layer** when the primary complexity is data transformation (ETL, reporting) rather than business rules.

---

## Encapsulation

### MUST
- Keep all fields **private**. External access goes through methods that enforce invariants. `customer.balance` is wrong; `customer.getBalance()` that returns a read-only view is fine.
- Expose **behavior, not data**. Prefer `invoice.isOverdue()` over `invoice.getDueDate()` combined with caller-side arithmetic.
- Protect invariants at **construction** and every **mutation**. The constructor must establish a valid state; every setter or command must validate preconditions before changing state.
- Return **defensive copies or immutable views** of internal mutable state. `getItems()` must not return the internal list reference — callers could break invariants like "order must have at least one item."
- Put **validation inside the method**, not in every caller. If every caller checks `if (amount <= 0)` before calling `withdraw()`, the validation is in the wrong place.

### MUST NOT
- Expose setters for every field. Setters are only justified when they represent a valid domain operation: `invoice.markAsPaid()` is fine; `invoice.setStatus("PAID")` is not.
- Let method names reveal internal structure. `getRawData()`, `getUnderlyingCollection()` are signs encapsulation has failed. Name methods by what they mean, not by what field they expose.
- Allow invariant violations at any point — not during construction, not after mutations, not after deserialization. If `startDate` must come before `endDate`, no code path should be able to make that false.

### MAY
- Use **immutable objects** (all fields final, no mutators) for snapshots, values, or events. They cannot enter an invalid state after construction.
- Apply **tell-don't-ask**: instead of checking state and then deciding (`if (invoice.isOverdue()) invoice.applyLateFee()`), tell the object what happened and let it decide (`invoice.handleNewDay()`).
- Validate invariants in one **guard method** (`ensureValidState()`) called after every mutation rather than repeating checks in each method.

---

## Cohesion

### MUST
- Give every class a **single, well-defined purpose**. If you cannot describe it in one sentence without "and" or "but", it needs splitting.
- Keep methods that operate on the same data in the same class. If `applyDiscount` reads `order.total` and `order.customerTier`, those belong together.
- Ensure changing one business rule changes code in **exactly one class**. Updating a late-fee formula should not touch three different services.
- Extract a **new class** when a method works on a subset of fields that form a coherent sub-concept. Shipping address + method + cost + tracking number belongs in `ShippingDetail`, not scattered across `Order`.

### MUST NOT
- Create **utility or helper classes** that are grab-bags of unrelated methods. `StringUtils`, `DateUtils` are borderline; `MiscUtils` is never acceptable.
- Mix **domain logic with infrastructure** in the same class. `calculateTax()`, `toJson()`, `validate()`, and `save()` belong in separate layers.
- Have a class where half the fields are unused in half the methods — split along the usage boundaries.
- Accept **god classes** (500+ lines) that "do everything" for a subsystem. They bundle related operations but mix abstraction levels and make change risky.

### MAY
- Accept **temporary low cohesion** during step-by-step refactoring if tracked as technical debt.
- Split a class when it passes 200-300 lines, even if the split feels artificial. Smaller classes are easier to test and evolve.
- Use **mixins or traits** for truly horizontal concerns (logging, serialization) that many unrelated classes share.

---

## Aggregation vs Composition

### MUST
- Use **composition** (part-of, lifetime-coupled) when the child cannot exist without the parent. `Order` creates and owns its `OrderLine` objects; deleting the order deletes its lines.
- Use **aggregation** (has-a, independent lifetimes) when the child can exist on its own. A `Customer` can exist without a given `Address`; the same address can be reused across customers.
- Enforce the lifetime constraint in code. In composition, the parent constructor creates its children and the parent's destruction cascades to them. In aggregation, the parent holds a reference — the child lives independently.

### MUST NOT
- Model a composition relationship as aggregation (orphaned children with no invariant enforcement) or vice versa (children that cannot survive a parent deletion when they should).
- Use inheritance to model composition — `Employee { Contract contract }` (has-a) is composition; `ContractEmployee extends Employee` (is-a) is not. Prefer has-a.
- Create circular references between composing objects. If a child needs to refer to its parent, use an interface or event.

### MAY
- Default to **composition** and relax to aggregation only when you have evidence the child needs an independent lifecycle. Composition is safer.
- Use **weak references** for child-to-parent back-references to avoid memory leaks.
- Use **domain events** for cascading deletes instead of imperative cleanup — fire `PolicyCancelled` and let each child handle it.

---

## Inheritance and Polymorphism

### MUST
- Apply **Liskov Substitution**: a subclass must be substitutable for its parent. If `Square extends Rectangle` and `setWidth()` also changes height, `Square` is not a valid `Rectangle`.
- Use **polymorphism instead of conditionals**. `document.print(printer)` replaces `if (doc instanceof PdfDocument)` chains. Every `instanceof` outside test code is a smell.
- Depend on **interfaces, not concrete types**. Accept `Printer`, not `HpLaserJetPrinter`.
- Favor **composition over inheritance**: `class Order { DiscountCalculator calculator }` is more flexible than `class DiscountOrder extends Order`.

### MUST NOT
- Create inheritance hierarchies **deeper than three levels**. Changes at the top affect every leaf, and understanding the full behavior requires reading every ancestor.
- Override a method and throw `UnsupportedOperationException` — this violates Liskov substitution. Either make the method optional in the interface or restructure.
- Subclass just to reuse utility methods — that is implementation inheritance for the wrong reason. Extract a shared utility or compose instead.
- Inherit across module boundaries unless the hierarchy is explicitly designed as extensible.

### MAY
- Use **abstract base classes** when several subclasses share significant implementation. Keep them internal to the module.
- Apply **template method pattern** (base class defines skeleton, subclasses override specific steps) to eliminate duplication in polymorphic algorithms.
- Accept shallow inheritance (1-2 levels) for UI components or framework extensions where the framework mandates it. Keep your subclass thin and delegate real logic to composed services.

---

## Leaky Abstractions

### MUST
- Hide **all** underlying complexity. Every error, exception, or behavior from the underlying layer must be caught or translated before it reaches the abstraction boundary. An SQL syntax error must not surface through a repository.
- Keep performance **consistent enough that callers don't need to guess the implementation**. If `findById(id)` returns in 2ms or 2s depending on cache state, callers must plan around that variance.
- Describe the **contract, not the implementation**. A comment that says "persists to PostgreSQL" is a leak; say "persists the entity" and leave the mechanism hidden.
- Match **failure modes to the abstraction level**. `UserRepository` throws `UserNotFound`, not `SQLException` or `TimeoutException`. Translate every infrastructure exception at the boundary.

### MUST NOT
- Expose **implementation types in the public API**. Return domain objects or DTOs, not `ResultSet`, `HttpResponse`, or `JsonNode`.
- Require callers to **set up or tear down the underlying layer**. If using `FileRepository` requires callers to create directories or call `fsync()`, the filesystem has leaked into their responsibility.
- Expose **configuration knobs for implementation details**. `cacheTtlMs`, `connectionPoolSize` on a repository constructor leak tuning into every caller. Put them in a configuration object the abstraction reads internally.
- Put **methods on the interface that only work with some implementations**. If `StorageService` has `seek()` but only `FileStorage` can seek while `S3Storage` throws, the interface is wrong. Split it.
- Change **semantics based on hidden state**. If `findById(id)` returns stale data after an uncommitted write, or throws after a transparent retry timeout, the abstraction behaves unpredictably.

### HOW TO DETECT
- Callers catch **infrastructure exceptions** (`IOException`, `SQLException`) from the abstraction.
- Callers add **timeouts, retries, or circuit-breakers** around a method that should be simple.
- Callers check **specific error messages** — `err.message.contains("connection refused")` in calling code.
- Duplicated **pre or post conditions** across callers — every caller calls `flush()` after `write()`.
- The interface has **methods that mirror the underlying layer**: `open()`, `close()`, `flush()`, `connect()`.
- Callers use `instanceof` to **check which implementation** is behind the abstraction.

### HOW TO FIX
1. **Translate exceptions at the boundary** — catch every infrastructure exception and convert to 1-3 abstraction-level types (`NotFound`, `Conflict`, `SystemError`).
2. **Remove infrastructure types from the API** — replace `ResultSet`, `HttpResponse`, `JsonNode` with domain types or DTOs.
3. **Own the lifecycle internally** — open/close, flush/sync, begin/commit must be handled inside the abstraction.
4. **Document performance expectations** as part of the contract so callers don't guess based on implementation.
5. **Move implementation-specific methods** off the public interface. `seek()` belongs on `FileStorage`, not `StorageService`.
6. **Write contract tests** that exercise the abstraction through its public API against every implementation. If a test passes with the in-memory version but fails with the database version, the abstraction leaks database assumptions.

### MAY
- Accept **bounded, documented leaks** when the contract explicitly describes them (e.g. "may return stale data for 30 seconds after a write").
- Provide an **escape hatch** (`getUnderlyingConnection()`) for advanced use cases, clearly documented as non-portable.
- Use **interceptors** (retry, circuit-breaking, caching) transparently so callers don't see them.
- Accept that **zero-leak abstractions are rare** for cross-cutting concerns like performance. Prioritize fixing type leaks and inconsistent failure behavior over eliminating every behavioral leak.