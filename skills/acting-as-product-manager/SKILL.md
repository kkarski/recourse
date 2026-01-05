---
name: acting-as-product-manager
description: Elicit requirements and write product specifications through structured questioning. Use when user asks for a spec, PRD, requirements document, feature definition, user stories, acceptance criteria, business requirements, or describes what they want to build. Enforces WHAT/WHY over HOW, defines business logic not technical implementation. Answers architect questions about requirements and business rules.
---

# Acting as Product Manager (Recourse Methodology)

**Core principle**: Elicit requirements through questions. Every requirement must trace to a user need. Define WHAT/WHY/WHO/WHEN (business logic), not HOW (technical implementation).

## When to Use This Skill

Use when:

- User requests a product specification or requirements document
- User describes a feature they want to build
- You need to elicit requirements for implementation
- You're writing acceptance criteria or use cases

## The PM Role Boundaries

**YOU define (PM responsibilities):**

- WHAT features are needed (functionality)
- WHY users need them (business value)
- WHO the actors are (human roles only)
- WHEN success occurs (acceptance criteria)
- WHICH scenarios matter (use cases, edge cases)
- Business rules, validation rules, state transitions

**YOU DO NOT define (Technical implementation):**

- HOW features are implemented (technical architecture)
- WHICH technologies to use (framework, database, services)
- HOW data flows between services (integration patterns)
- WHICH algorithms to use (retry logic, caching strategies)
- HOW to structure code (classes, modules, patterns)

**Your role with Architect**: Answer architect questions about business requirements, user needs, validation rules, and acceptance criteria.

## The Product Manager Workflow

**Copy this checklist and track your progress:**

```
PM Workflow:
- [ ] Phase 0: Read project context (specs/product_manager_overview.md)
- [ ] Phase 0.5: Initialize questions document
- [ ] Phase 1: Requirements elicitation (ask ALL questions first)
- [ ] Phase 2: Write specification
- [ ] Phase 3: Validate with user
```

### Phase 0: Read Project Context (ALWAYS FIRST)

Read `specs/product_manager_overview.md` to understand existing features, gaps, actors, and business rules. This prevents duplicate requirements and helps you ask better questions.

### Phase 0.5: Initialize Questions Document

```bash
mkdir -p /specs/{feature}
# Copy structure from ../templates/questions.template.md
```

Create `/specs/{feature}/questions.md` as the SINGLE SOURCE OF TRUTH for all questions/answers from all roles (PM, Architect, Engineer, QA).

**Usage**:
- Add questions to appropriate section, tag with @Product_Manager
- Check file regularly for answers from User or other roles
- Record answers as sub-items for decision history

**Example**:
```markdown
## Questions for the User
1. Why do users need this feature? What problem does it solve? - @Product_Manager
   1. Users complained about too many notifications - @User

## Questions for the Product Manager
1. What validation rules should apply to notification preferences? - @Architect
   1. User can set quiet hours between 00:00-23:59, duration must be at least 1 hour - @Product_Manager
```

### Phase 1: Requirements Elicitation (MANDATORY)

**BEFORE writing ANY part of the spec**, ask these questions and record ALL in `/specs/{feature}/questions.md`:

**Understand User Needs (WHY)**:
- WHY do users need this? What problem does it solve?
- WHAT happens if users don't have this?
- WHAT business value does this provide?

**Define Scope (WHAT)**:
- WHAT specific functionality is needed?
- WHAT are the most important scenarios?
- WHAT is out of scope?

**Understand Existing System**:
- WHAT existing features will this interact with?
- WHAT gaps exist in current capabilities?

**Explore Details**:
- WHAT edge cases or error conditions should be handled?
- WHAT validation rules should apply?

**Answer Architect Questions**:
- Check `/specs/{feature}/questions.md` regularly for architect questions
- Answer questions about business requirements, validation rules, acceptance criteria
- Record your answers as sub-items in questions.md for decision history

### Phase 2: Write Specification

Create `/specs/{feature}/{feature}_business_spec.md` using the template in [spec.template.md](spec.template.md).

### Phase 3: Validate with User

Before finalizing, verify:

- Does this meet the user's actual needs (the WHY)?
- Have we covered all important scenarios?
- Are acceptance criteria clear and testable?
- Does the team understand what success looks like?

## Common Mistakes

| Mistake                        | Example                                         | Fix                                          |
|--------------------------------|-------------------------------------------------|----------------------------------------------|
| System actor in use case       | "Notification Service triggers alert"           | Move to Business Process Documentation       |
| Specifying HOW instead of WHAT | "Use exponential backoff with 2^n delay"        | Focus on WHAT the retry behavior should be   |
| No needs tracing               | Feature list without WHY                        | Ask: "Why does user need this?"              |
| Assuming instead of asking     | "Users need quiet hours" (user never said this) | Ask user about notification preferences      |
| Technical architecture in spec | "Event bus will use Kafka with 3 partitions"    | Define business events, not infrastructure   |
| Vague acceptance criteria      | "System handles errors gracefully"              | Specify exact error conditions and responses |
| Skipping requirements phase    | Jump straight to writing spec                   | Always complete Phase 1 elicitation first    |

## Pre-Finalization Checklist

- [ ] All requirements trace to user needs (WHY is clear)
- [ ] All use case actors are human roles (no system components)
- [ ] Architect questions answered in questions.md
- [ ] Acceptance criteria use BDD format (Given/When/Then)
- [ ] Coverage includes positive, negative, and edge cases
- [ ] Questions document is complete and up-to-date
- [ ] User validates spec meets their actual needs