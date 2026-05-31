# Design Patterns — MUST / MUST NOT / MAY

Distilled rules for code review. Each pattern is expressed as MUST (required), MUST NOT (forbidden), and MAY (optional / situational) statements.

## Strategy Pattern

### MUST
- Encapsulate each algorithmic variant in a separate class that implements a **shared interface or abstract base**. The context class MUST hold a reference to that interface, never to a concrete implementation.
- Keep the strategy interface **narrow and stable** — ideally a single method (e.g. `calculate()`, `sort()`, `validate()`). An interface that grows with every new variant is a leaky abstraction.
- **Delegate unconditionally** — the context calls `this.strategy.execute(data)` without branching on the strategy's type. `instanceof` checks on strategies defeat the pattern.
- Make strategies **interchangeable at runtime or configuration time** without modifying the context class. Inject via constructor, setter, factory, or DI container.
- Ensure each strategy owns **exactly one behavioral variant**. A strategy must not manage state, perform I/O, or reference other strategies.

### MUST NOT
- Use `switch`/`if-else` chains that dispatch on a type discriminator (`if type == "pdf"`) — extract those branches behind a strategy interface instead.
- Write a class whose single method branches across algorithms. That is an **inline strategy** that should be split into separate strategy classes.
- Give a strategy more than one or two constructor arguments of its own. Heavy dependencies belong in the context, not in the strategy.
- Share significant boilerplate or prep/teardown logic across strategies. That signals Template Method, not Strategy.

### MAY
- Use a **factory or registry** to select the strategy when the choice depends on runtime state the context should not know about.
- Apply Template Method instead of Strategy when strategies share a common skeleton and only vary in specific steps.
- Extract strategies when you spot a multi-branch conditional inside any method — even if it was not planned upfront. The pattern can be introduced retroactively.
- Let the strategy receive per-call parameters through its method signature rather than storing them as instance state.

---

## Fluent API

### MUST
- Return `this` (or a new instance of the same builder type) from every intermediate chained method so calls can be daisy-chained without intermediate variables.
- Design the chain around a **single coherent operation** — building a query, constructing an object, composing a pipeline — with a clear **terminal operation** (`.build()`, `.execute()`, `.run()`) that returns the final result.
- Make intermediate methods **additive or idempotent** — calling `.filter(x).filter(y)` must stack or merge, not silently clobber `x` with `y`.
- Ensure the chain reads **left-to-right as a natural domain sentence**: `.select("name").from("users").where("age > 18")`.

### MUST NOT
- Hide expensive operations (database calls, network I/O) inside intermediate methods. Only the terminal operation should perform real work — intermediate methods must be free of visible side effects.
- Require the caller to know ordering constraints by convention (e.g. "call `.from()` before `.where()` or it crashes"). Enforce ordering through **return types that change per stage** or validate at terminal time.
- Mix side-effect verbs (`save()`, `send()`) in the middle of a chain. Fluent methods must be clearly either **intermediate** (return `this`, no effects) or **terminal** (return result, perform action).
- Produce chains longer than 5-7 method calls that cannot be broken into named intermediate variables. If every call needs a comment, the API is not expressive enough.

### MAY
- Use **type-safe builders** where each method returns a different interface for the next stage (e.g. `.select()` returns `FromSelector`, `.from()` returns `WhereSelector`). This enforces compile-time ordering.
- Break an overly long chain into **sub-builders** or named intermediate objects for readability.
- Accept that some fluent APIs cannot enforce all invariants at compile time — validate invariants in the terminal method and throw clear error messages.
- Use method names that are single verbs or prepositions (`with`, `and`, `from`, `where`) when the domain language supports it.

---

## Business Facade

### MUST
- Expose **coarse-grained business operations** that map to complete use-case steps. `submitOrder(orderId)` MUST orchestrate validation, inventory, payment, and notification — not just call `orderRepository.save()`.
- **Hide all internal orchestration** from callers. Callers pass domain-level inputs and receive domain-level results. They MUST NOT know about databases, services, transactions, or third-party APIs.
- Be the **single entry point** for its domain boundary. All external callers (controllers, CLI, scheduled tasks, test harnesses) MUST go through the facade. No external code reaches into domain services or repositories directly.
- Map **each facade method to exactly one business use case or user story step**. If one feature requires multiple facade calls in a specific order, the facade is too fine-grained.

### MUST NOT
- Be a **thin wrapper** around a single repository or service call (e.g. `getUser(id) { return repo.findById(id); }`). A facade must add value: bundling steps, enforcing invariants, or coordinating multiple services. Without that, it is a "wrapper facade" antipattern.
- Allow callers to **bypass** the facade by importing domain services or repositories directly alongside the facade. If controllers or tests reach behind the facade, the facade boundary is broken.
- Grow into a **CRUD collection** (save, find, delete, update). A Business Facade uses business language: `processRefund`, `applyDiscount`, `escalateTicket`. If it reads like a database table mapping, rename it to a Repository and build a proper facade on top.
- Accept or return **primitive types** (strings, ints, booleans) instead of domain objects or DTOs. `OrderDTO` not `Map<String, Object>`. Primitive-heavy facades cannot be type-checked and resist evolution.
- Have **no tests of its own**. If mocking the facade requires hundreds of lines or a running database, it is too tightly coupled. Each facade method MUST be testable with a DTO in, DTO out.

### MAY
- Apply **cross-cutting concerns** (transactions, security checks, logging, audit trails) at the facade level rather than scattering them through domain services. The facade is the natural boundary for these concerns.
- Throw **domain-specific exceptions** from the facade rather than leaking infrastructure exceptions (SQLException, HTTP 500). Translate at the facade boundary.
- Accept that a facade may delegate to **other facades** when a use case crosses bounded contexts. Each facade remains the single entry point for its own context.
- Introduce a facade **retroactively** when external callers are found duplicating the same orchestration pattern across controllers or tests. The duplicate pattern signals the missing facade boundary.

---

## DAO (Data Access Object) with Local Caching

### MUST
- Abstract **all data access** behind the DAO interface. Callers MUST NOT know whether data comes from a database, a remote API, or a local cache — they call `dao.findById(id)` and get a result regardless of the backing source.
- Implement a **local cache layer** inside the DAO that sits in front of the remote data source. Every read MUST check the cache first before hitting the network or database.
- Define an explicit **cache lifetime (TTL)** per entity or query type. Stale data MUST be refreshed or evicted when the TTL expires. A single global TTL for all entities is almost always wrong — fast-changing data needs seconds, reference data may tolerate hours.
- Invalidate or update the local cache on **write operations** (create, update, delete). After `dao.save(entity)`, a subsequent `dao.findById(entity.id)` MUST return the new state, not stale cache. Use cache-aside (invalidate on write, lazy-reload on next read) or write-through (update cache and remote together) consistently.
- Make the cache **transparent to callers** — no caller should pass cache hints, flush the cache manually, or know that caching exists. If callers need cache-control knobs (e.g. `forceRefresh: true`), the cache abstraction has leaked.

### MUST NOT
- Return **stale data** from the cache after a write that should have invalidated it. Every write path MUST have a matching cache-invalidation or cache-update step. Missing invalidation is the most common cache bug.
- Let the cache grow **without bound**. Implement an eviction policy (LRU, LFU, TTL-based, or size-cap) so the DAO does not leak memory under sustained load.
- Expose the cache as a **separate, public abstraction** that callers can import directly. If `Cache` and `Dao` are both public classes, callers will inevitably bypass the DAO for reads, defeating the abstraction and making cache-invalidation logic unreachable from the write path.
- Perform **I/O inside a cache-miss handler while holding a lock** that blocks concurrent requests for the same key, unless the miss handler is short and idempotent. Use a "future-based" or "promise" cache (sometimes called a "loading cache") that lets concurrent callers for the same key await the single in-flight fetch instead of each triggering their own.
- Mix **different cache strategies** (cache-aside vs read-through vs write-through) for the same entity within the same DAO. Pick one strategy per entity and apply it consistently — mixing leads to subtle races and unreachable stale states.
- Cache **entire collection results** (`dao.findAll()`) without considering invalidation complexity. Collection caches are notoriously hard to keep consistent because any write to any member invalidates the whole set. Prefer caching individual lookups and composing them, or use a short-TTL collection cache with explicit acceptance of eventual consistency.
- Use the DAO with caching for **local, in-process data** (e.g. reading a local SQLite file). Caching adds overhead and stale-risk with zero benefit when the "remote" source is already local and fast.

### MAY
- Use **read-through caching** where the cache automatically fetches from the remote source on miss and stores the result before returning. This keeps the DAO implementation simpler than cache-aside because the fetch logic lives in the cache layer.
- Use **write-through caching** when read-after-write consistency is critical — every write updates both cache and remote in the same transaction or unit of work, so subsequent reads always see the latest state.
- Implement a **stale-while-revalidate pattern** for performance-sensitive reads: return the cached (possibly stale) value immediately, then refresh the cache in the background. This avoids blocking the caller on a slow remote fetch but requires the caller to tolerate bounded staleness.
- Cache **null / not-found** results with a short TTL to protect the remote source against repeated lookups of missing keys (negative caching). Without this, a hot key that does not exist can still hit the remote on every access.
- Add **observability hooks** (cache hit/miss counters, latency histograms, eviction events) to the DAO cache layer. These are internal instrumentation, not caller-facing — they help review whether the cache is working without leaking the abstraction.
- Pre-warm the cache at **startup or deployment** for reference data that is read frequently but changes rarely. This avoids a thundering-herd of cache misses when a new instance comes online.
- Test cache behavior explicitly: hit ratio under realistic load, invalidation correctness, concurrent read/write correctness, TTL expiry, and eviction order. A cache that has no tests is assumed broken until proven otherwise.

---

## Singleton Pattern

### MUST
- Ensure the singleton has **exactly one instance per process** and provides a single, well-known access point (e.g. `Instance()` or `getInstance()`). Every caller MUST obtain the instance through this access point — never by constructing a new one.
- Make the constructor **private or otherwise inaccessible** to external callers. The only way to get the instance is through the static access point. A class with a public constructor is not a singleton regardless of documentation saying otherwise.
- Protect the singleton against **concurrent initialization** — use a thread-safe construction mechanism (static initializer, `sync.Once`, double-checked locking with volatile, or language-native singleton guarantees). Two threads calling `getInstance()` simultaneously must never produce two instances.
- Keep the singleton **narrow in responsibility** — it should own exactly one concern (a registry, a connection pool, a configuration store). A singleton that manages logging, caching, and feature flags simultaneously is a god object hiding behind the pattern.
- Ensure the singleton is **testable** — either by allowing instance replacement in tests (setter, environment override, DI override) or by designing the singleton as a thin holder that delegates to an injectable interface. A singleton that cannot be mocked or substituted in tests is a liability.

### MUST NOT
- Use a singleton for **shared state that mutates concurrently** from multiple threads without synchronization. If two threads can call `singleton.setConfig(x)` and `singleton.getConfig()` simultaneously without coordination, the singleton becomes a race-condition carrier.
- Introduce a singleton for **stateless utility methods** — a class with `Utils.formatDate()`, `Utils.calculateTax()` that has no mutable state and no lifecycle. A module of static functions is not a singleton and should not be dressed as one.
- Let the singleton **hide or abstract away its dependencies**. A `DatabasePool.getInstance()` that reads configuration from a global env variable or a magic file path is a hidden coupling — the singleton makes the dependency implicit and untestable.
- Use a singleton as a **convenience proxy for a global variable**. `GlobalState.getCurrentUser()` is not a singleton — it is a global mutable bucket. The pattern requires controlled initialization and lifecycle, not carte-blanche global access.
- Let the singleton class **accumulate responsibilities over time** — the single-instance guarantee makes it tempting to tack on "one more thing." When a singleton grows past 200 lines or three responsibilities, extract the secondary concerns into separate classes.

### MAY
- Use a **singleton registry** (a map of singletons keyed by name or type) when you need multiple independently managed singletons but want a uniform access pattern. This is common for plugin systems or service registries.
- Replace a singleton with **dependency injection** when the framework manages lifecycle and scoping (e.g. DI container with singleton scope). The DI container's singleton scope provides the same guarantee without the class enforcing it itself.
- Implement **lazy initialization** when the singleton is expensive to construct and may not be needed on every code path. Ensure the lazy path is thread-safe.
- Accept that a singleton for **infrastructure concerns** (logging framework, configuration reader, metrics exporter) is pragmatic even when the pattern is considered an anti-pattern by purists — these are genuine "exactly one per process" concerns. Just keep them narrow.
- Add **lifecycle hooks** (start, stop, shutdown) to the singleton when it manages resources (connections, thread pools, file handles). A singleton that leaks connections or threads because it has no shutdown path is a production incident waiting to happen.