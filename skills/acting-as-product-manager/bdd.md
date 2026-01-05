## Acceptance Criteria Format Options

Acceptance criteria can be expressed in three formats. Choose the format that best fits your story type:

1. **BDD/Gherkin** - User-centric scenarios, behavior-driven development (recommended for most cases)
2. **Checklist** - Complex business logic, multiple rules
3. **Flow/Narrative** - Multi-step user journeys, sequential processes

## BDD/Gherkin Format Guidelines

**Given** - Sets up initial context and preconditions (present tense)
- Examples: "Given a user is authenticated", "Given a campaign exists in Draft state"

**When** - Describes the action or event that triggers the behavior (present tense)
- Examples: "When the user creates a campaign", "When the system processes the document"

**Then** - Describes the expected outcome or result (future tense)
- Examples: "Then the system should validate the campaign ID", "Then the system should create a cached file"

**Guidelines**:
- Use present tense for Given/When, future tense for Then
- Be specific about data, states, and conditions
- Each scenario should be independent and testable
- Focus on business value, avoid implementation details
- Use "And" to add context/outcomes, "But" for exceptions
- Examples: "Given a user is authenticated **And** has CAMPAIGN scope", "When the user creates a campaign **But** uses an invalid ID"

## Quality Principles

**SMART Criteria**: Specific, Measurable, Achievable, Relevant, Testable

**Coverage**: Include positive cases (happy paths), negative cases (errors/edge cases), boundary conditions, validation rules, and state transitions

**Writing Tips**: Be specific with error messages, cover edge cases (empty inputs, null values, timeouts), state preconditions clearly, use visual aids when needed


## Acceptance Criteria Format Examples

### Format 1: BDD/Gherkin

```gherkin
Feature: Document Parsing
  As a document uploader
  I want to upload and process documents
  So that I can convert them to markdown format

  Scenario: First-time document processing (Positive case)
    Given a valid document has never been processed before
    When the document is processed for the first time
    Then the system should parse the document content
    And the system should create a cached markdown (.md) file
    And the processing status should be set to "completed"

  Scenario: Reject markdown files as input (Negative case)
    Given a user has a markdown (.md) file
    When the markdown file is uploaded as input
    Then the system should reject the file
    And the system should return an error message: "Markdown files are not accepted as input"
```

### Format 2: Checklist

Use for complex business logic with multiple independent rules. Each item should be independently testable, use clear actionable language, and include specific values where applicable.

```markdown
- [ ] **File Type Validation**: The system must detect file type upon upload and validate it against supported formats (PDF, DOCX, TXT)
- [ ] **First-Time Processing**: When a valid document is processed for the first time, the system must parse the document content and create a cached markdown (.md) file
- [ ] **Processing Status Update**: After successful processing, the system must set the processing status to "completed"
- [ ] **Markdown File Rejection**: The system must reject markdown (.md) files as input and return error message: "Markdown files are not accepted as input"
- [ ] **Cache Utilization**: The system must use the cached markdown file for previously processed documents instead of re-parsing
- [ ] **File Size Validation**: The system must check file size against maximum limit (50MB) before processing
```

### Format 3: Flow/Narrative

Use for multi-step user journeys and sequential processes. Number steps sequentially, clearly identify actor (User/System) for each step, include decision points, and cover both happy paths and error flows.

```markdown
**First-Time Document Processing Flow:**
1. User uploads a valid document that has never been processed before
2. System detects the file type and validates it against supported formats (PDF, DOCX, TXT)
3. System validates file size is within limits (max 50MB) and file is not corrupted
4. System begins processing the document
5. System parses the document content based on file type
6. System extracts metadata (title, author, creation date, etc.)
7. System creates a cached markdown (.md) file with parsed content
8. System stores metadata in the document entity
9. System sets processing status to "completed"
```

**Guidelines for Flow/Narrative Format**:
- Number steps sequentially to show order
- Clearly identify actor (User, System) for each step
- Include decision points and alternative paths when applicable
- Specify data and conditions at each step
- Cover both happy paths and error flows
- Use consistent terminology throughout the flow

## Acceptance Criteria Quality Checklist

Use this checklist to verify that acceptance criteria have been written correctly according to this guide:

### Specification Document Completeness
- [ ] All functional requirements are expressed as acceptance criteria
- [ ] Acceptance criteria use appropriate format (BDD/Gherkin, Checklist, or Flow/Narrative)
- [ ] All business rules are included as verifiable acceptance criteria
- [ ] All exception flows and error conditions are covered (see "Coverage Requirements" above)
- [ ] Clear success and failure outcomes are defined for each scenario

### Business Rule Translation
- [ ] Each business rule is expressed in an appropriate format (BDD/Gherkin recommended, or Checklist/Flow/Narrative when suitable)
- [ ] Each rule is specific and measurable (see "SMART Criteria" above)
- [ ] Each rule is independent and testable
- [ ] Each rule focuses on business value rather than implementation details

### Multiple Scenarios Handling
- [ ] Each scenario is expressed as a separate acceptance criterion
- [ ] Positive cases (happy paths) are clearly distinguished from negative cases (exception flows)
- [ ] Edge cases are explicitly documented
- [ ] All scenarios are mutually exclusive and collectively exhaustive

### Exception Flow Documentation
- [ ] Preconditions that trigger exceptions are clearly defined
- [ ] Exact error response or behavior is specified
- [ ] Recovery or fallback mechanisms are included (if applicable)
- [ ] Error scenarios are testable with specific error conditions

### BDD/Gherkin Format Quality (if using BDD/Gherkin format)
- [ ] Each **Given** statement establishes clear preconditions
- [ ] Each **When** statement describes a single, unambiguous action
- [ ] Each **Then** statement specifies verifiable outcomes
- [ ] All statements use appropriate tense (present tense for Given/When, future tense for Then - see "Additional Guidelines" above)
- [ ] "And" and "But" clauses are used appropriately to extend statements

### Checklist Format Quality (if using Checklist format)
- [ ] Each item is independently testable
- [ ] Clear, actionable language is used ("must", "should")
- [ ] Specific values and thresholds are included where applicable
- [ ] Related rules are grouped together

### Flow/Narrative Format Quality (if using Flow/Narrative format)
- [ ] Steps are numbered sequentially to show order
- [ ] Actor (User, System) is clearly identified for each step
- [ ] Decision points and alternative paths are included when applicable
- [ ] Data and conditions are specified at each step
- [ ] Both happy paths and error flows are covered
- [ ] Consistent terminology is used throughout the flow

### General Quality Standards
- [ ] All acceptance criteria meet SMART criteria (Specific, Measurable, Achievable, Relevant, Testable)
- [ ] Coverage includes positive cases, negative cases, boundary conditions, validation rules, and state transitions
- [ ] Error messages are specific (not generic like "handle errors gracefully")
- [ ] Edge cases are considered (empty inputs, null values, timeouts, network failures)
- [ ] Preconditions are clearly stated
- [ ] Visual aids are included when words aren't sufficient