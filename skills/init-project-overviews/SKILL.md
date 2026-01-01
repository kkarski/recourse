---
name: init-project-overviews
description: Use when starting work on a project to generate role-specific overview documentation for Product Manager, Architect, and Engineer roles
---

# Initialize Project Overviews

## Overview

When starting work on a project, each role needs different context about the existing system. This skill generates role-specific overview documents that provide the essential context each role needs.

**Core principle**: Each role has different information needs. PM needs features/capabilities, Architect needs architecture/patterns, Engineer needs code structure/utilities.

## When to Use

Use this skill when:

- Starting work on an existing project for the first time
- Onboarding to a new codebase
- Creating documentation for role-based AI agents
- Project context has significantly changed

**Invoke as**: `/init` or use this skill manually

## What Gets Created

Three overview documents in `/specs` folder:

```
/specs/
├── product_manager_overview.md    # Existing features, capabilities, gaps
├── architect_overview.md          # Architecture, components, patterns, tech stack
└── engineer_overview.md           # Code structure, utilities, patterns
```

## Role-Specific Content

### Product Manager Overview

**Purpose**: Understand existing features and capabilities as baseline for new features

**Content to generate**:

1. **Product Vision & Scope**
    - What problem does this product solve?
    - Who are the users?
    - What is the overall product scope?

2. **Existing Features & Capabilities**
    - What can users currently do?
    - What workflows are supported?
    - What are the key features?

3. **Current Limitations & Gaps**
    - What can't users do yet?
    - Known pain points or missing features
    - Technical debt affecting user experience

4. **User Roles & Actors**
    - What user roles exist?
    - What can each role do?

5. **Key Business Rules**
    - Important validation rules
    - Business constraints
    - Domain-specific logic

### Architect Overview

**Purpose**: Understand system architecture to maintain consistency with existing patterns

**Content to generate**:

1. **System Architecture**
    - High-level architecture diagram (describe in text/Mermaid)
    - Major system components
    - How components interact

2. **Technology Stack**
    - Languages and frameworks
    - Databases and storage
    - External services and integrations
    - Infrastructure (cloud, deployment)

3. **Data Models**
    - Key entities and their relationships
    - Database schema overview
    - Aggregates and bounded contexts (if DDD)

4. **APIs & Integrations**
    - Internal APIs (REST, GraphQL, events)
    - External service integrations
    - Authentication/authorization patterns

5. **Design Patterns & Principles**
    - Architectural patterns in use (MVC, event-driven, microservices, etc.)
    - Domain-Driven Design patterns (if applicable)
    - Code organization principles

6. **Architecture Decisions**
    - Key technical decisions and rationale
    - Trade-offs made
    - Constraints to be aware of

### Engineer Overview

**Purpose**: Understand code structure and existing utilities to reuse when implementing features

**Content to generate**:

1. **Code Structure**
    - Directory/package organization
    - Module breakdown
    - Where different types of code live

2. **Key Components & Utilities**
    - Existing services that can be reused
    - Utility functions and helpers
    - Shared libraries and modules

3. **Development Patterns**
    - Coding conventions in use
    - Common patterns (repository, service, factory, etc.)
    - How features are typically structured

4. **Testing Approach**
    - Testing framework and tools
    - Where tests live
    - How to run tests
    - Test coverage expectations

5. **Development Workflow**
    - How to build/run locally
    - Development dependencies
    - Common development tasks

6. **Extension Points**
    - How to add new features
    - How to add new entities/models
    - How to add new API endpoints
    - Code generation or scaffolding tools

## Implementation Workflow

### Step 1: Explore Codebase

Use the Task tool with Explore subagent to gather information:

```
Task tool → Explore subagent (thoroughness: "very thorough")

For Product Manager:
- "What features does this application provide to users?"
- "What can users do with this system?"
- "What are the main user workflows?"

For Architect:
- "What is the high-level architecture?"
- "What technology stack is used?"
- "What are the main system components?"
- "What design patterns are used?"

For Engineer:
- "What is the code structure and organization?"
- "What reusable utilities and services exist?"
- "How are tests organized?"
- "How to build and run the application?"
```

### Step 2: Read Key Files

Based on codebase type:

**For Python projects**:

- `README.md`, `requirements.txt`, `pyproject.toml`
- Main application files
- `models.py`, `schemas.py`, `entities.py`
- `settings.py`, `config.py`
- Test files to understand test approach

**For TypeScript/JavaScript projects**:

- `package.json`, `tsconfig.json`
- `src/` directory structure
- Models, types, interfaces
- API routes/controllers
- Test files

**For any project**:

- Documentation in `docs/`, `process/`, `.claude/`
- Architecture diagrams
- API specifications (OpenAPI/Swagger)
- Database schemas or migrations

### Step 3: Generate Overview Documents

For each role, create structured Markdown document:

#### Product Manager Overview Template

```markdown
# Product Manager Overview

## Product Vision

[What problem does this solve? Who are the users?]

## Existing Features

### [Feature Category 1]

- **Feature**: [Feature name]
    - **What it does**: [User-facing description]
    - **Who uses it**: [User role]
    - **Key workflows**: [How users accomplish tasks]

[Repeat for each feature]

## Current Limitations

- [Gap 1]: [What users can't do yet]
- [Gap 2]: [Known pain point]

## User Roles

- **[Role 1]**: [What they can do]
- **[Role 2]**: [What they can do]

## Key Business Rules

- [Rule 1]
- [Rule 2]
```

#### Architect Overview Template

```markdown
# Architect Overview

## System Architecture

[High-level description or Mermaid diagram]

```mermaid
graph TD
    [Component diagram showing major components and interactions]
```

## Technology Stack

- **Language**: [Python, TypeScript, etc.]
- **Framework**: [FastAPI, Django, Express, etc.]
- **Database**: [PostgreSQL, MongoDB, etc.]
- **External Services**: [List integrations]
- **Infrastructure**: [Cloud provider, deployment]

## Data Models

### [Entity 1]

- **Purpose**: [What it represents]
- **Key fields**: [Important attributes]
- **Relationships**: [How it relates to other entities]

## APIs

- **Internal APIs**: [REST endpoints, GraphQL, etc.]
- **External Integrations**: [Third-party services]
- **Authentication**: [How auth works]

## Design Patterns

- **[Pattern 1]**: [Where/how it's used]
- **[Pattern 2]**: [Where/how it's used]

## Architecture Decisions

- **Decision**: [Technology/pattern choice]
    - **Rationale**: [Why this was chosen]
    - **Trade-offs**: [What was sacrificed]

```

#### Engineer Overview Template

```markdown
# Engineer Overview

## Code Structure

```

project/
├── src/
│ ├── [module1]/ # [What lives here]
│ ├── [module2]/ # [What lives here]
│ └── [module3]/ # [What lives here]
├── tests/
└── [other dirs]

```

## Key Components

### [Component 1]
- **Location**: `src/path/to/component.py`
- **Purpose**: [What it does]
- **How to use**: [Example]

## Development Patterns

- **[Pattern 1]**: [How it's implemented]
- **[Pattern 2]**: [How it's implemented]

## Testing

- **Framework**: [pytest, jest, etc.]
- **Run tests**: `[command]`
- **Test location**: `[where tests live]`
- **Coverage**: [Expected coverage level]

## Development Workflow

### Setup
```bash
# Installation
[commands to install dependencies]

# Run locally
[commands to run application]
```

### Common Tasks

- **Build**: `[command]`
- **Test**: `[command]`
- **Lint**: `[command]`

## How to Extend

### Adding a New Feature

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Adding a New API Endpoint

1. [Step 1]
2. [Step 2]

### Adding a New Entity

1. [Step 1]
2. [Step 2]

```

### Step 4: Write to /specs Folder

```bash
# Create specs directory if it doesn't exist
mkdir -p /specs

# Write each overview
Write product_manager_overview.md to /specs/
Write architect_overview.md to /specs/
Write engineer_overview.md to /specs/
```

## Quality Checklist

Before completing, verify each overview:

**Product Manager Overview**:

- [ ] Lists all major user-facing features
- [ ] Describes what users can currently do
- [ ] Identifies gaps and limitations
- [ ] Defines user roles clearly
- [ ] Captures key business rules

**Architect Overview**:

- [ ] Describes high-level architecture
- [ ] Lists complete technology stack
- [ ] Documents major components
- [ ] Explains design patterns in use
- [ ] Includes API/integration information
- [ ] References architecture decisions

**Engineer Overview**:

- [ ] Shows code structure clearly
- [ ] Lists reusable utilities/services
- [ ] Explains development patterns
- [ ] Provides setup/run instructions
- [ ] Describes how to extend system
- [ ] Includes testing information

## Common Mistakes

| Mistake                                | Fix                                                            |
|----------------------------------------|----------------------------------------------------------------|
| Too high-level (not actionable)        | Include specific examples, file paths, commands                |
| Too detailed (overwhelming)            | Focus on what's essential for that role                        |
| Technology-focused for PM              | PM overview should be user/feature-focused, not technical      |
| Missing "how to extend" for Engineer   | Engineers need to know how to add features, not just read code |
| No architecture diagrams for Architect | Visual representations help understanding                      |

## Example Usage

```
User: "/init"

You (following this skill):
1. Use Task tool → Explore subagent to analyze codebase
2. Read key files (README, package.json, main code files)
3. Generate product_manager_overview.md with features and capabilities
4. Generate architect_overview.md with architecture and tech stack
5. Generate engineer_overview.md with code structure and patterns
6. Write all three to /specs/ folder
7. Respond: "Created role overviews in /specs/ folder"
```

## Success Criteria

You've successfully initialized project overviews when:

- All three overview files exist in `/specs/` folder
- Each overview contains role-specific, actionable information
- Product Manager can understand what users can currently do
- Architect can understand architecture and maintain consistency
- Engineer can understand how to add features using existing patterns
- Information is current and accurate based on codebase analysis

## Notes

- Overviews should be regenerated when major changes occur
- Keep overviews concise (< 500 lines each)
- Link to detailed docs when they exist, don't duplicate
- Use code examples and file paths to make information actionable