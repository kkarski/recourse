### **Step-by-Step Story Creation Process**

#### **Phase 1: Foundation & Context (Complete First)**

1. **Ask JTBD Context Questions**:
   - *Customer Context*: "What specific, observable situation triggers this need? (e.g., 'When my flight gets canceled at midnight' vs. 'When travel plans change')"
   - *Current Struggle*: "What frustrations occur with current solutions? (e.g., 'I waste 2 hours calling airlines')"
   - *Desired Progress*: "What does meaningful success look like? (e.g., 'Arrive at my meeting without losing composure')"
   - *Constraints*: "What might block adoption? (e.g., 'Anxiety about app reliability when stressed')"

2. **Draft Job Statement**:
   - *When*: Combine **specific circumstance + emotional context** (e.g., "When my flight cancels last-minute *while I'm rushing to a keynote speech*, feeling panicked about missing it...")
   - *I want to*: Merge **functional + emotional jobs** (e.g., "...find a reliable alternative *while maintaining professionalism*")
   - *So I can*: State **progress + why it matters** (e.g., "...deliver my speech confidently *to strengthen my industry reputation*")

3. **Analyze Behavioral Forces**:
   - *Push*: Extract pain points from current struggles (e.g., "Call centers take 45+ mins on hold")
   - *Pull*: Identify hoped-for improvements (e.g., "Instant rebooking notifications")
   - *Anxiety*: Surface fears about change (e.g., "New app might overcharge during urgency")
   - *Habit*: Acknowledge inertia (e.g., "Default to calling because 'it's always worked'")

4. **Define Success Criteria**:
   - *Functional*: Quantifiable outcomes (e.g., "Book new flight in <5 mins")
   - *Emotional*: Feeling shifts (e.g., "Reduce panic to calm focus")
   - *Social*: Perception goals (e.g., "Be seen as prepared by colleagues")

5. **Identify Dependencies & Constraints**:
   - *System Dependencies*: "Real-time inventory from airline APIs; Payment processing gateway"
   - *Data Dependencies*: "Customer loyalty status; Flight schedules; Airport operational data"
   - *Regulatory Constraints*: "GDPR compliance for EU customers; PCI DSS for payment data"
   - *Technical Constraints*: "Mobile app must work offline for 30 minutes"

#### **Phase 2: Business Logic Design (Complete Second)**

6. **Define Business Rules**:
   - *Eligibility Rules*: "IF premium member AND cancellation within 24hrs THEN priority queue access"
   - *Process Rules*: "MUST verify passport validity before international rebooking; CANNOT book connections under minimum transfer time"
   - *Data Rules*: "REQUIRED: destination, departure date, passenger count; OPTIONAL: seat preference, meal preference"
   - *Temporal Rules*: "WITHIN 15 minutes MUST hold seat inventory; AFTER 24hrs THEN apply change fees"
   - *Calculation Rules*: "IF EU flight delayed >3hrs THEN compensation = €250-€600 based on distance"

7. **Design Validation Logic**:
   - *Input Validation*: "Departure date must be future date; Passenger count 1-9; Valid airport codes only"
   - *Business Logic Validation*: "Cross-check visa requirements for destination; Validate loyalty status before applying discounts"
   - *Error Handling*: "IF no availability THEN show waitlist option + alternative dates; IF payment fails THEN hold booking for 10 minutes"

8. **Document Assumptions & Risks**:
   - *Business Rule Assumptions*: "Airline partnerships remain stable; Regulatory requirements won't change mid-sprint"
   - *Validation Assumptions*: "Users will provide accurate passport information; Payment methods are valid"
   - *Change Management Risks*: "Frequent rule changes may confuse existing users"
   - *Performance Risks*: "Complex validation logic may slow booking process during peak times"

#### **Phase 3: Detailed Requirements (Complete Third)**

9. **Create Acceptance Criteria**:
   - *Functional*: "Given flight cancellation at 3AM, When I tap 'rebook', Then options appear in <10 secs"
   - *Emotional*: "Given high anxiety, When I see cost transparency, Then I feel in control"
   - *Social*: "Given colleagues waiting, When I share new itinerary, Then it looks polished"
   - *Business Rule Compliance*: "Given premium member status, When flight cancels, Then priority rebooking options shown first"
   - *Validation Scenarios*: "Given invalid passport expiry, When booking international flight, Then clear error message with renewal guidance shown"

10. **Define Non-Functional Requirements**:
    - *Performance*: "Load alternatives in <3s during peak travel"
    - *Security*: "Payment auto-hides in public spaces"
    - *Reliability*: "99.9% uptime during travel disruption events"
    - *Maintainability*: "Business rules updatable without code deployment"
    - *Auditability*: "Log all rule executions for compliance reporting"

#### **Phase 4: Measurement & Validation (Complete Last)**

11. **Define Validation Metrics**:
    - *Hire Rate*: "% target users adopting solution during cancellations"
    - *Progress Indicators*: "Time saved vs. old method", "Pre-event stress scores"
    - *Rule Compliance*: "% of bookings following business rules correctly"
    - *Validation Effectiveness*: "% of invalid inputs caught before processing"

12. **Create Title & Finalize**:
    - *Format*: Start with "[Desired Progress]"
    - *Example*: "Arrive at critical events calmly despite travel disruptions" *(not* "Flight rebooking feature")