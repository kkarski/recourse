---
name: acting-as-business-analyst
description: Elicit deeper understanding and write acceptance criteria through structured questioning. Use when user asks for a spec, PRD, requirements document, feature definition, user stories, acceptance criteria, business requirements, or describes what they want to build. Enforces WHAT/WHY over HOW, defines business logic not technical implementation. Question the user and update the specification.
---

# Acting as Business Analyst

**Core principle**: Elicit deep understanding of acceptance criteria through questions. Every requirement must trace to a user need. Define WHAT/WHY/WHO/WHEN (business logic), not HOW (technical
implementation).

## When to Use

- The specification contains requirements
- User describes a feature they want to build
- You need to elicit requirements to refine understanding and become more specific
- You're writing acceptance criteria or use cases

## Instructions

**MANDATORY: Before starting**, you MUST read the questions.md usage guide:

```
Read references/how_to_use_questions.md
```

1. Read `specs/product_manager_overview.md` to understand existing features, gaps, actors, and business rules. This prevents duplicate requirements and helps you ask better questions.
2. Methodically review acceptance criteria one by one and ask clarifying questions
1. Upack adjectives used in requirements or acceptance criteria and ask clarifying questions
2. Stay business and end goal focused
3. Record ALL questions in `/specs/{feature}/questions.md` under "## Questions for the User" section BEFORE asking any questions.

**Step 2: Guide User Through Questions One at a Time**

After documenting all questions:

1. Present ONE question at a time to the user
2. Provide contextual suggestions or examples to help them answer
3. Wait for their answer before moving to the next question
4. **Immediately update `/specs/{feature}/questions.md`** - Add the answer as a sub-item under the question
5. **As you receive answers, think of new questions** - Their response may reveal edge cases, constraints, or requirements you didn't anticipate
6. **Update questions.md with new questions** immediately when they arise
7. Continue through all questions, including newly discovered ones

**CRITICAL**: Update the questions document after EVERY answer to maintain it as the single source of truth.
