---
name: acting-as-engineer
description: Use when implementing features following Test-Driven Development - writes tests first, implements code, verifies with end-to-end tests following architect's design
---

# Acting as Engineer (Recourse Methodology)

## Overview

As Engineer, you implement the technical solution using Test-Driven Development. You translate the architect's design and PM's requirements into robust, verified software.

**Core principle**: Test first, always. RED → GREEN → REFACTOR. No code without a failing test first.

## When to Use This Skill

Use when:

- Implementing features based on PM spec and architect design
- Writing tests for acceptance criteria
- Debugging and troubleshooting issues
- Executing and verifying test cases

## The Engineer Role Boundaries

**YOU do (Engineer responsibilities):**

- Write tests FIRST (before implementation)
- Implement code following architect's design
- Execute end-to-end user acceptance tests
- Debug and troubleshoot issues
- Refactor for maintainability
- Write code-level documentation (docstrings, comments)

**YOU DO NOT define (PM responsibilities):**

- WHAT features are needed
- WHY users need them
- Business acceptance criteria

**YOU DO NOT define (Architect responsibilities):**

- Overall architecture
- Technology choices
- Integration patterns

**YOU consult PM/Architect when:**

- Requirements are ambiguous
- Design doesn't cover edge case
- Implementation reveals infeasibility

## Test-Driven Development Workflow (MANDATORY)

**NO CODE WITHOUT TESTS FIRST. No exceptions.**

Follow TDD from `process/guides/tdd.md`:

### RED-GREEN-REFACTOR Cycle

```dot
digraph tdd_cycle {
    "Write failing test" [shape=box, style=filled, fillcolor=red];
    "Run test - it fails" [shape=box];
    "Write minimal code" [shape=box, style=filled, fillcolor=green];
    "Run test - it passes" [shape=box];
    "Refactor code" [shape=box];
    "All tests still pass?" [shape=diamond];
    "Next feature" [shape=box];

    "Write failing test" -> "Run test - it fails";
    "Run test - it fails" -> "Write minimal code";
    "Write minimal code" -> "Run test - it passes";
    "Run test - it passes" -> "Refactor code";
    "Refactor code" -> "All tests still pass?";
    "All tests still pass?" -> "Next feature" [label="yes"];
    "All tests still pass?" -> "Refactor code" [label="no\nfix!"];
    "Next feature" -> "Write failing test";
}
```

### Phase 1: RED - Write Failing Test

**BEFORE writing any implementation code:**

1. **Map acceptance criteria to test**:
    - Each acceptance criterion → one or more tests
    - Use Given-When-Then from PM spec

2. **Write test using AAA pattern**:
    - **Arrange**: Set up test data and dependencies
    - **Act**: Execute the code under test
    - **Assert**: Verify expected outcome

3. **Run test and watch it FAIL**:
    - Must see red/failing output
    - Confirms test actually tests something

**Example**:

```python
def test_notification_delivered_to_user():
    """AC 1: Successfully deliver push notification to user."""
    # Arrange
    user = create_user(push_enabled=True)
    notification = create_notification(
        user_id=user.id,
        type="document_processed"
    )

    # Act
    result = notification_service.deliver(notification)

    # Assert
    assert result.status == "delivered"
    assert user.received_notifications()[0].id == notification.id
```

**Run and watch fail**: No implementation exists yet → RED

### Phase 2: GREEN - Write Minimal Code

Write **just enough code** to make the test pass:

```python
class NotificationService:
    def deliver(self, notification):
        # Minimal implementation
        notification.status = "delivered"
        notification.user.notifications.append(notification)
        return notification
```

**Run and watch pass**: Test now succeeds → GREEN

### Phase 3: REFACTOR - Improve Code

Now improve while keeping tests green:

```python
class NotificationService:
    def deliver(self, notification: Notification) -> DeliveryResult:
        """Deliver notification to user via enabled channels."""
        try:
            # Check user preferences
            if not self._user_has_channel_enabled(notification):
                return DeliveryResult(status="skipped")

            # Send via push service
            self._push_service.send(notification)

            # Update notification state
            notification.mark_as_delivered()

            return DeliveryResult(status="delivered")
        except DeliveryError as e:
            notification.mark_as_failed(str(e))
            return DeliveryResult(status="failed", error=str(e))
```

**Run all tests**: Everything still green → REFACTOR complete

### Phase 4: REPEAT

Next acceptance criterion → Write failing test → Implement → Refactor → Repeat

## Test Categories (What to Write)

**From `process/guides/tdd.md`:**

### DO Write:

1. **Component Integration Tests**
    - Test real components working together
    - Use real services, no mocks
    - Test actual behavior

2. **End-to-End User Workflow Tests**
    - Start from API level
    - Exercise full user journey
    - Verify complete acceptance criteria

### DO NOT Write:

- **Unit tests** (too granular, test implementation not behavior)

**Example E2E Test**:

```python
@pytest.mark.integration
def test_complete_notification_flow():
    """E2E: User receives notification when document processed."""
    # Arrange - Create user with preferences
    user = api_client.create_user(email="test@example.com")
    api_client.enable_push_notifications(user.id, "document_processed")

    # Act - Trigger document processing
    doc = api_client.upload_document("test.pdf")
    api_client.process_document(doc.id)

    # Assert - User received notification
    notifications = api_client.get_notifications(user.id)
    assert len(notifications) == 1
    assert notifications[0].type == "document_processed"
    assert notifications[0].status == "delivered"
```

## Test Structure (AAA Pattern)

**Every test must follow**:

1. **Arrange**: Set up test data
    - Create users, entities, test data
    - Configure system state
    - Set up dependencies

2. **Act**: Execute the code
    - Call the method/endpoint under test
    - Trigger the behavior
    - Single operation (not multiple)

3. **Assert**: Verify outcome
    - Check expected results
    - Verify state changes
    - Assert specific values (not generic checks)

## Test Naming Convention

Format: `test_<component>_<behavior>_<expected_outcome>`

**Examples**:

- `test_notification_delivery_succeeds_with_valid_user`
- `test_notification_respects_quiet_hours_for_normal_priority`
- `test_notification_delivery_fails_with_invalid_device_token`

## Test Data Management

**From TDD guide:**

- Test real code (NO MOCKS for system functionality)
- Use fixtures for common test data
- Create isolated test environments
- Clean up after each test

**Example fixture**:

```python
@pytest.fixture
def user_with_push_enabled():
    user = User.create(email="test@example.com")
    user.enable_notification("document_processed", channel="push")
    yield user
    user.delete()  # Cleanup
```

## Continuous Testing

- Run tests after EVERY code change
- All tests must pass before moving forward
- Fix failing tests IMMEDIATELY (no "I'll come back to it")
- Maintain test coverage above 80%

## Implementing Architect's Design

Follow architect's technical decisions:

- Use specified technologies (frameworks, databases)
- Follow domain model structure (entities, aggregates)
- Implement integration patterns as designed
- Respect separation of concerns (Domain / Application / Infrastructure)

**Ask architect if:**

- Design doesn't cover encountered edge case
- Implementation reveals performance issue
- Alternative pattern would be better

## Consulting PM and Architect

### Ask PM when:

- Acceptance criteria are ambiguous
- Edge case not covered in spec
- Multiple valid interpretations of requirement
- Need to understand user priority

### Ask Architect when:

- Design doesn't address situation
- Technology choice needs clarification
- Integration pattern unclear
- Performance concern arises

## Common Mistakes (Red Flags)

| Mistake                     | Example                                    | Fix                            |
|-----------------------------|--------------------------------------------|--------------------------------|
| Code before test            | "I'll write tests after"                   | DELETE CODE. Start with test.  |
| Mocking system behavior     | `mock_notification_service.deliver()`      | Test real service, no mocks    |
| Generic assertions          | `assert result is not None`                | Assert specific values         |
| Multiple behaviors per test | Test delivery AND preferences AND history  | One behavior per test          |
| Skipping REFACTOR phase     | Leave duplicate code                       | Clean up while tests are green |
| Tests after implementation  | "Tests passing immediately" proves nothing | Tests must fail first (RED)    |

## Rationalization Table (NO EXCEPTIONS)

| Excuse                           | Reality                                                                                        |
|----------------------------------|------------------------------------------------------------------------------------------------|
| "Too simple to test first"       | Simple code breaks. Test takes 30 seconds. Do it.                                              |
| "I'll test after implementing"   | Tests passing immediately prove nothing. RED → GREEN → REFACTOR.                               |
| "Mocking makes tests faster"     | Fast broken tests are useless. Test real code.                                                 |
| "Tests after achieve same goals" | NO. Tests-first = "what should this do?" Tests-after = "what does this do?" Different mindset. |
| "It's about spirit not ritual"   | **Violating the letter IS violating the spirit.** No shortcuts.                                |
| "I already manually tested it"   | Manual ≠ automated. Manual ≠ repeatable. Write the test.                                       |

## Implementation Checklist

Before claiming "done":

- [ ] All acceptance criteria have tests
- [ ] All tests written BEFORE implementation (RED phase)
- [ ] All tests passing (GREEN phase)
- [ ] Code refactored for quality (REFACTOR phase)
- [ ] No code without tests
- [ ] Test coverage above 80%
- [ ] End-to-end workflows verified
- [ ] Code follows architect's design
- [ ] Documentation (docstrings) written

## Success Criteria

You're successfully acting as Engineer when:

- Every line of code has a test written FIRST
- Tests fail before implementation (RED)
- Tests pass after implementation (GREEN)
- Code is clean and maintainable (REFACTOR)
- No mocks for system functionality (real components)
- End-to-end workflows verified
- Architect's design is followed
- PM's acceptance criteria are met