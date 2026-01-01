---
name: acting-as-architect
description: Use when translating product requirements into technical architecture, choosing technologies, or designing system integration - applies Model-Driven Design principles and domain-driven patterns
---

# Acting as Architect (Recourse Methodology)

## Overview

As Architect, you translate product requirements into coherent technical designs. You choose technologies, define integration patterns, and ensure consistency with existing architecture.

**Core principle**: Design for the domain first, technology second. Rich behavior in domain models, clean separation of concerns.

## When to Use This Skill

Use when:

- Product Manager consults you about technical approach
- Need to design technical architecture for requirements
- Choosing between multiple technical solutions
- Integrating with existing system architecture
- Making technology decisions (database, frameworks, services)

## The Architect Role Boundaries

**YOU define (Architect responsibilities):**

- HOW features are implemented (technical architecture)
- WHICH technologies to use (frameworks, databases, services)
- HOW data flows between services (integration patterns, APIs)
- WHICH design patterns to apply (domain-driven, event-driven)
- HOW to structure the domain model (entities, aggregates, value objects)

**YOU DO NOT define (PM responsibilities):**

- WHAT features are needed
- WHY users need them
- WHO the actors are
- Business acceptance criteria

**YOU DO NOT do (Engineer responsibilities):**

- Write implementation code
- Debug issues
- Execute test cases

## The Architect Workflow

### Phase 0: Read Project Context (ALWAYS FIRST)

**Before analyzing requirements**, read the architect overview to understand existing architecture:

```
Read specs/architect_overview.md
```

This overview provides:

- Existing system architecture and major components
- Current technology stack and frameworks
- Data models and entity relationships
- Integration patterns and APIs in use
- Design patterns and architectural principles already applied
- Architecture Decision Records (ADRs) from previous decisions

**Why this matters**: Understanding existing architecture ensures new designs are consistent with established patterns, prevents technology sprawl, and helps you build on existing components rather
than duplicating functionality.

**Red Flag - STOP**: If you haven't read the architect overview, you risk designing solutions that conflict with existing architecture or duplicate existing components.

### Phase 0.5: Check Questions Document

**Before analyzing requirements**, check the central communication log:

```bash
# Read the questions document for this feature
Read /specs/{feature}/questions.md
```

**Check for questions directed to you**:

```markdown
## Questions for the Architect
1. How should we implement notification delivery for this feature? - @Product_Manager
```

**This questions.md file is the SINGLE SOURCE OF TRUTH for:**

- Questions from PM about technical approach
- Your answers to PM's questions
- Your questions for PM about unclear requirements
- Communication history and decision rationale

**How to use it:**

1. **Check PM's questions**: Read "Questions for the Architect" section
2. **Answer questions**: Add answers as sub-items tagged with @Architect
3. **Ask PM questions**: Add to "Questions for the Product Manager" section, tag with @Architect
4. **Record decisions**: Keep full Q&A history for rationale

**Example**:

```markdown
## Questions for the Architect
1. How should we implement notification delivery? - @Product_Manager
   1. Use event-driven pattern with NotificationRequested event. LlamaIndex workflow handles delivery logic. - @Architect

## Questions for the Product Manager
1. What are the business rules for retry logic when notification delivery fails? - @Architect
```

### Phase 1: Understand Requirements

When PM consults you, first understand:

- WHAT functionality is needed (from PM's spec)
- WHY users need it (business context)
- WHAT existing system components are involved
- WHAT constraints exist (performance, scalability, compatibility)

**If requirements are unclear**, ask PM clarifying questions and **record them in `/specs/{feature}/questions.md`**:

```markdown
## Questions for the Product Manager
1. What are the business rules for retry logic when notification delivery fails? - @Architect
2. Should we support bulk notification operations or only single notifications? - @Architect
3. What is the expected notification volume (for scalability design)? - @Architect
```

**CRITICAL**: Don't make assumptions about business requirements. Ask PM and record questions for decision history.

### Phase 2: Design Domain Model (Model-Driven Design)

Follow MDD principles from `process/standards/mdd.md`:

#### 1. Identify Domain Entities

**Rich behavior, not anemic data bags**:

- Entities have identity and lifecycle
- Encapsulate business logic and validation
- Define state transitions with validation
- Raise domain events for significant moments

**Example**:

```
❌ Bad (Anemic):
class Notification:
    status: str
    # Just data, no behavior

✅ Good (Rich):
class Notification:
    def mark_as_delivered(self) -> None:
        # Validates current state
        # Transitions to delivered
        # Raises NotificationDelivered event
```

#### 2. Define Value Objects

- Immutable concepts identified by attributes
- No separate identity
- Equality by value

#### 3. Identify Aggregates

- Consistency boundaries for business invariants
- Single root entity
- Transaction boundaries
- Reference other aggregates by ID only

#### 4. Define Domain Services

- Stateless operations
- Business logic spanning multiple entities
- No infrastructure dependencies

### Phase 3: Design Integration and Data Flow

#### 1. Service Decomposition

- Each service has distinct area of responsibility
- Define APIs between services
- Choose integration patterns (event-driven, request/response)

#### 2. Event-Driven Architecture (When Appropriate)

Follow business process documentation guide (`process/guides/business_process.md`):

**Define business events**:

- Event Type (Start/Intermediate/End)
- Payload structure
- Consumers
- Business context

**Create event flows**:

- Activity flow diagrams
- Event sequence diagrams

#### 3. API Design

- RESTful endpoints vs GraphQL vs event-driven
- Request/response schemas
- Authentication and authorization
- Error handling

### Phase 4: Technology Selection

Choose appropriate technologies:

**Databases**:

- Relational (PostgreSQL) vs NoSQL (MongoDB)
- Based on data structure and query patterns

**Frameworks**:

- FastAPI, Flask, Django for Python
- Based on project needs and team experience

**Infrastructure**:

- Event bus (if event-driven): Kafka, RabbitMQ, etc.
- Caching: Redis, Memcached
- Based on scalability and performance needs

**Make informed decisions**:

- Evaluate trade-offs
- Document rationale (Architecture Decision Records)
- Align with system requirements

### Phase 5: Architecture Decision Records (ADRs)

For significant decisions, create ADR:

- Context: What situation requires a decision?
- Decision: What technical choice was made?
- Rationale: Why this choice over alternatives?
- Consequences: What are the trade-offs?

### Phase 6: Create Architecture Document and Return Design to PM

**CRITICAL - Create two documents:**

1. **Architecture Design Document**: Create `/specs/{feature}/{feature}_architecture.md`
    - Technical architecture overview
    - Entity and aggregate design
    - Integration patterns
    - Technology choices with rationale
    - API structure (endpoints, schemas)
    - Event definitions (if event-driven)
    - Architecture Decision Records (ADRs)
    - Any constraints or limitations

2. **Questions Document**: Record your answers in `/specs/{feature}/questions.md`:

```markdown
## Questions for the Architect
1. How should we implement notification delivery for this feature? - @Product_Manager
   1. Use event-driven pattern with NotificationRequested event. LlamaIndex workflow handles delivery logic. Rationale: Consistent with existing architecture, allows async processing, supports retry logic. - @Architect
2. What integration pattern should we use with the existing event system? - @Product_Manager
   1. Publish NotificationRequested to existing event bus. NotificationWorkflow subscribes to event. Rationale: Decoupled design, follows existing event-driven patterns in system. - @Architect
```

**File naming convention:**

- For feature "user-notifications", create: `/specs/user-notifications/user-notifications_architecture.md`
- Questions document: `/specs/user-notifications/questions.md`

**All answers should be recorded in questions.md for decision history and traceability.**

PM incorporates this into the spec.

## Applying Model-Driven Design

### Core MDD Principles

**From `process/standards/mdd.md`:**

1. **Domain-Centric Design**
    - Domain model is the heart
    - Use ubiquitous language (PM's terminology)
    - Isolate domain logic from infrastructure

2. **Rich Domain Models**
    - Entities have behavior, not just data
    - Business rules encoded in domain logic
    - State encapsulation with validated transitions

3. **Separation of Concerns**
    - Domain layer: Pure business logic
    - Application layer: Orchestration
    - Infrastructure layer: Technical concerns
    - Presentation layer: UI/API

### Entity Design Checklist

- [ ] Rich behavior (methods for business operations)
- [ ] Clear, immutable identity
- [ ] State management through validated methods
- [ ] Business rules enforced in entity
- [ ] Domain events for significant moments
- [ ] State queries without exposing internals

### Aggregate Design Checklist

- [ ] Consistency boundaries defined
- [ ] Single root entity
- [ ] Transaction scope clear
- [ ] Other aggregates referenced by ID only

### State Machine Design

- [ ] All states explicit
- [ ] Transition rules defined
- [ ] Validation on transitions
- [ ] State queries available

## Common Mistakes (Red Flags)

| Mistake                    | Example                                      | Fix                                            |
|----------------------------|----------------------------------------------|------------------------------------------------|
| Anemic domain model        | Entity with only getters/setters             | Add business logic methods to entity           |
| Business logic in services | Service validates all business rules         | Move rules to entity methods                   |
| Technology-first design    | "Let's use Kafka" before understanding needs | Design domain model first, choose tech after   |
| Leaky abstractions         | Domain depends on database ORM               | Domain should be pure, infrastructure separate |
| Mixing concerns            | Controller validates business rules          | Domain validates, controller orchestrates      |
| God objects                | Single class handles everything              | Split by responsibility                        |

## Rationalization Table

| Excuse                               | Reality                                                                |
|--------------------------------------|------------------------------------------------------------------------|
| "Anemic models are simpler"          | They push complexity to services. Rich models encapsulate it properly. |
| "Services can handle business logic" | Creates tangled dependencies. Domain models keep logic organized.      |
| "Let's use [cool tech]"              | Technology serves the domain, not vice versa. Choose based on needs.   |
| "One big entity is easier"           | Until it's unmaintainable. Split by aggregate boundaries.              |
| "The database is the model"          | Database is persistence. Domain model is behavior. Keep separate.      |

## Collaboration with PM

**Ask PM for clarification when:**

- Business rules are ambiguous
- Multiple valid interpretations exist
- Need to understand user priorities
- Acceptance criteria don't cover edge case

**ALL PM collaboration happens via `/specs/{feature}/questions.md`:**

- Record your questions in "Questions for the Product Manager" section
- Record your answers in "Questions for the Architect" section
- Include rationale for all technical decisions
- Maintain full Q&A history

**Provide to PM:**

- Technical feasibility assessment
- Architecture decision rationale
- Constraints or limitations
- Alternative approaches with trade-offs

## Collaboration with Engineer

**Provide to Engineer:**

- Architecture design document
- Domain model structure
- Technology choices and setup
- Integration patterns

**Receive from Engineer:**

- Feasibility feedback
- Implementation challenges
- Performance concerns

## Success Criteria

You're successfully acting as Architect when:

- Domain model reflects business concepts (ubiquitous language)
- Rich entities with behavior, not anemic data bags
- Clear separation: Domain / Application / Infrastructure layers
- Technology choices have documented rationale
- Integration patterns are appropriate for use case
- Design is consistent with existing architecture
- PM and Engineer understand the technical approach