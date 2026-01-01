# Product Manager Summary: User Notifications System

## What I Did

Following the recourse Product Manager methodology, I completed Phase 1: Requirements Elicitation by asking you 15 clarifying questions about:

- User needs (the WHY)
- Scope (the WHAT)
- Existing system
- Details and edge cases

Based on your answers, I created a **minimal product specification** that focuses strictly on WHAT users need and WHY, without making technical HOW decisions.

---

## Key Deliverables

### 1. Product Specification Document

**Location**: `/home/kkarski/dev/gits/recourse/req/elicitation/business_requirements/notifications_minimal_spec.md`

**Contents**:

- **Business Context**: Problem statement, business value, success metrics
- **Scope**: What's in/out based on your answers
- **Use Cases**: Only human actors (User), no system components
- **Acceptance Criteria**: BDD format (Given/When/Then) with 14 scenarios
- **Business Process Documentation**: Event flows, activity diagrams, sequence diagrams
- **Architect Consultation Section**: 25+ technical questions requiring architect input
- **API Contracts**: Preliminary (pending architect decisions)
- **E2E Test Cases**: 14 test scenarios
- **Open Questions**: 6 questions for stakeholders

---

## How This Spec Follows PM Methodology

### ✅ Correct PM Behaviors

1. **Asked Before Assuming**: 15 clarifying questions before writing any spec
2. **Traced to User Needs**: Every feature traces back to your problem statement (users missing updates)
3. **Only Human Actors**: Use cases only include "User" actor, no "Application Service" or system components
4. **WHAT, not HOW**: Spec defines what users need, not how to implement it
5. **Consulted Architect**: Identified 5 infrastructure gaps and created 25+ questions for architect
6. **No Feature Creep**: Only included what you explicitly requested:
    - 3 notification types (document_processed, document_failed, document_shared)
    - Push (must-have) and Email (nice-to-have)
    - Per-type opt-out preferences
    - **Excluded**: Quiet hours, archiving, in-app notifications, priority levels (not requested by you)

### ❌ Violations Avoided (vs Old Spec)

The old spec (`notifications_spec.md`) violated PM role by:

1. Including "Application Service" as a use case actor (UC8)
2. Assuming features you never requested (quiet hours, archiving, in-app, priority levels)
3. Specifying retry logic and technical implementation (exponential backoff, etc.)
4. Not consulting architect before making infrastructure decisions

The new minimal spec avoids all these violations.

---

## What Happens Next

### Immediate Next Step: Architect Consultation (BLOCKING)

**Status**: The specification is **BLOCKED** on architect input.

**Why**: The PM identified 3 critical infrastructure gaps:

1. No push notification infrastructure
2. No email delivery service
3. No notification preferences database

**Architect Must Decide**:

- Which push service to use (FCM, AWS SNS, OneSignal, etc.)
- Which email service to use (SendGrid, AWS SES, etc.)
- How to store preferences (new DB table, separate service, etc.)
- Event integration pattern (API calls, message queue, etc.)
- Retry strategies, monitoring, disaster recovery

**How to Proceed**:
You have two options:

**Option A: You act as architect** and answer the 25+ questions in the "Architect Consultation Required" section of the spec.

**Option B: Bring in an actual architect** to review the spec and provide technical decisions.

Once architect decisions are made, the PM can:

1. Finalize API contracts
2. Update the spec with technical constraints
3. Hand off to engineering for implementation planning

---

## Comparison: Old Spec vs New Minimal Spec

| Aspect                       | Old Spec (`notifications_spec.md`)               | New Spec (`notifications_minimal_spec.md`)  |
|------------------------------|--------------------------------------------------|---------------------------------------------|
| **Use Case Actors**          | 3 actors: User, Admin, **Application Service** ❌ | 1 actor: User ✅                             |
| **Quiet Hours**              | Included (15+ mentions) ❌                        | Excluded (not requested) ✅                  |
| **In-App Notifications**     | Included ❌                                       | Excluded (out of scope) ✅                   |
| **Archiving**                | Included (UC4, multiple ACs) ❌                   | Excluded (not requested) ✅                  |
| **Priority Levels**          | 4 levels (low, normal, high, urgent) ❌           | Excluded (not requested) ✅                  |
| **Retry Logic**              | Specified exponential backoff ❌                  | Deferred to architect ✅                     |
| **Infrastructure Decisions** | Made without architect ❌                         | Consultant section for architect ✅          |
| **Acceptance Criteria**      | 19 ACs (many for unrequested features)           | 14 ACs (only for requested features) ✅      |
| **Traceability**             | Features don't trace to user need ❌              | Every feature traces to problem statement ✅ |

---

## Key Insights from PM Process

### What You Actually Need (Based on Your Answers)

- **Problem**: Users don't check app regularly → miss updates → complain about slow response
- **Solution**: Real-time notifications (push) so users know immediately
- **Fallback**: Email for users who disable push
- **Control**: Per-type preferences so users don't get overwhelmed
- **Success**: 80%+ adoption, <5 min time-to-action

### What You Don't Need (Yet)

- Quiet hours (you never mentioned sleep/work disruption as a problem)
- Notification history/inbox (you never mentioned users need to review past notifications)
- Archiving (you never mentioned managing notification clutter)
- Priority levels (you never mentioned urgent vs non-urgent scenarios)
- In-app banners (you explicitly excluded this)

### Why This Matters

The old spec would have required engineering to build 5+ features you don't need, delaying time-to-market and increasing cost. The minimal spec gets you to your success metrics faster.

---

## Open Questions for You (Stakeholder)

Before architect review, please answer these 6 questions:

1. **Default Preferences**: Should notifications be enabled by default for new users, or opt-in?
    - Recommendation: Enabled by default (to achieve 80%+ adoption goal)

2. **Notification Content Limits**: Max length for messages? Should we truncate long document names?

3. **Multiple Devices**: If user has iPhone + iPad, send push to both or just one?

4. **Email Sender**: What "From" name/address? (e.g., "MyApp <notifications@myapp.com>")

5. **Unsubscribe Requirements**: Need "unsubscribe all" for legal compliance (CAN-SPAM)?

6. **Future Notification Types**: Any on roadmap we should design for now?

---

## Files Created

1. **Main Spec**: `/home/kkarski/dev/gits/recourse/req/elicitation/business_requirements/notifications_minimal_spec.md`
2. **PM Summary** (this file): `/home/kkarski/dev/gits/recourse/req/elicitation/business_requirements/notifications_pm_summary.md`
3. **Old Spec** (for reference): `/home/kkarski/dev/gits/recourse/req/elicitation/business_requirements/notifications_spec.md`

---

## Recommended Next Actions

1. **Review the minimal spec** (`notifications_minimal_spec.md`) - Does it capture your needs?
2. **Answer the 6 open questions** above
3. **Architect consultation** - Either:
    - You answer the technical questions in the spec, OR
    - Bring in an architect to answer them
4. **Finalize API contracts** after architect decisions
5. **Engineering kickoff** with finalized spec

---

**Status**: ✅ PM Phase Complete, ⏸️ Blocked on Architect Review
**Next Role**: Software Architect
**Blocking Questions**: 25+ in "Architect Consultation Required" section