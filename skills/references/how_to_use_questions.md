# How to Use questions.md

## Overview

The `questions.md` file is the **SINGLE SOURCE OF TRUTH** for cross-role communication during feature development. It serves as a central communication log for questions, answers, and decision
rationale.

## Location

The questions document is located at:

```
/specs/{feature}/questions.md
```

Where `{feature}` is the name of the feature you're working on (e.g., `user-notifications`, `document-processing`).

## What questions.md Contains

This file contains:

- **Questions FROM other roles directed TO you** - Questions that need your input
- **Your answers TO those questions** - Your responses with rationale
- **Your questions FOR other roles** - Questions you need answered
- **Communication history and decision rationale** - Full Q&A history for traceability

## How to Check for Questions Directed to You

**Before starting work on any feature**, check the questions document:

```bash
# Read the questions document for this feature
Read /specs/{feature}/questions.md
```

Look for sections tagged with your role (see "Master Example" below for the complete structure).

## How to Answer Questions

When you find questions directed to you, add your answers as numbered sub-items tagged with your role. Include rationale for your decisions.

**Key points:**

- Add answers as numbered sub-items (1.1, 1.2, etc.)
- Tag your answer with your role (@Architect, @Engineer, @Information_Architect, @Product_Manager)
- Include rationale for your decisions
- Keep full Q&A history for traceability

## How to Ask Questions

When you need clarification from other roles, add questions to the appropriate section tagged with your role.

**Key points:**

- Add questions to the appropriate section (Questions for the Product Manager, Questions for the Architect, etc.)
- Tag your question with your role
- Be specific about what you need to know
- Record questions even if the other role is unavailable (see "Proceeding with Assumptions" below)

## Master Example

Here's a complete example showing all patterns for how questions.md should look:

```markdown
## Questions for the User

1. Why do users need this feature? What problem does it solve? - @Product_Manager
    1. Users complained about too many notifications - @User
2. What does "empty" really mean when evaluating a LinkedIn or Booking.com profile? - @Business_Analyst

## Questions for the Architect

1. How should we implement notification delivery for this feature? - @Product_Manager
    1. Use event-driven pattern with NotificationRequested event. LlamaIndex workflow handles delivery logic. Rationale: Consistent with existing architecture, allows async processing, supports retry
       logic. - @Architect
2. What integration pattern should we use with the existing event system? - @Product_Manager
    1. Publish NotificationRequested to existing event bus. NotificationWorkflow subscribes to event. Rationale: Decoupled design, follows existing event-driven patterns in system. - @Architect

## Questions for the Product Manager

1. What are the business rules for retry logic when notification delivery fails? - @Architect
2. Should we support bulk notification operations or only single notifications? - @Architect
3. What terminology do users use for "workspace" vs "project"? - @Information_Architect
4. What terminology do users use for "workspace"? - @Information_Architect
    - **Proceeding with assumption**: Using "Workspace" based on business spec language
    - **If wrong**: Will need to update all nav labels
    - **Validation needed**: User terminology research

## Questions for the Engineer

1. What's the expected performance requirement for this endpoint? - @Product_Manager

## Questions for the Information Architect

1. How should we organize the settings hierarchy? - @Product_Manager
    1. Use 2-level hierarchy: Settings > Category. Max 6 top-level categories. Rationale: Reduces cognitive load, follows existing IA conventions. - @Information_Architect
2. What URL structure does the navigation require? - @Architect
    1. /feature/section/subsection pattern. Max 3 levels. See site map in {feature}_ia.md. - @Information_Architect
```

**This example demonstrates:**

- Questions from one role to another (e.g., PM asking Architect)
- Answers formatted as numbered sub-items with rationale
- Questions from multiple roles to the same role
- Questions for the User with answers recorded
- Proceeding with assumptions when a role is unavailable (question 4 under "Questions for the Product Manager")

## Proceeding with Assumptions

When other roles are unavailable, you can proceed with documented assumptions. Record these in questions.md using the format shown in the master example (question 4 under "Questions for the Product
Manager"):

```markdown
## Questions for the Product Manager

1. What terminology do users use for "workspace"? - @Information_Architect
    - **Proceeding with assumption**: Using "Workspace" based on business spec language
    - **If wrong**: Will need to update all nav labels
    - **Validation needed**: User terminology research
```

This ensures:

- Your assumptions are visible and can be validated later
- The impact of wrong assumptions is documented
- Decision history is maintained

## When to Use questions.md

**ALWAYS use questions.md for:**

- Cross-role communication
- Recording technical decisions and rationale
- Asking clarifying questions about requirements
- Documenting assumptions when proceeding without full information
- Maintaining decision history and traceability

**DO NOT:**

- Make assumptions without documenting them
- Skip checking questions.md before starting work
- Answer questions without recording them in questions.md
- Have side conversations outside of questions.md

## Best Practices

1. **Check questions.md FIRST** - Before starting any work on a feature, check for questions directed to you
2. **Answer promptly** - When you find questions, answer them with rationale
3. **Record everything** - All Q&A should be in questions.md for traceability
4. **Include rationale** - Always explain why you made a decision, not just what you decided
5. **Tag appropriately** - Use role tags (@Architect, @Engineer, @Information_Architect, @Product_Manager) to identify who asked/answered
6. **Maintain history** - Don't delete old questions/answers; they provide valuable context

## Role-Specific Sections

The questions.md file typically contains these sections:

- `## Questions for the User` - Questions from Product Manager or Business Analyst to the user about requirements, needs, and business context
- `## Questions for the Product Manager` - Questions about business requirements, user needs, acceptance criteria
- `## Questions for the Architect` - Questions about technical architecture, technology choices, integration patterns
- `## Questions for the Engineer` - Questions about implementation details, performance, feasibility
- `## Questions for the Information Architect` - Questions about navigation, content organization, labeling

Each role should check their section and respond appropriately. For role-specific workflows and detailed instructions, see the individual skill files (e.g., `acting-as-product-manager/SKILL.md`).
