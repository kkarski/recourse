## Phase 1: Core Identity & Business Context
**Start here - these define the fundamental nature of your user entity**

### Identity & Authentication
1. What uniquely identifies a user in our system? (email, username, ID, or combination?)
2. How do users prove their identity? (password, SSO, social login, MFA?)
3. What are our password requirements and security policies?
4. Do we require email/phone verification before account activation?
5. How do users recover forgotten passwords or locked accounts?

### Business Logic & User Lifecycle
6. What triggers user account creation? (self-registration, admin creation, invitation?)
7. What are the key states a user can be in? (pending, active, suspended, deleted?)
8. What business rules govern user behavior? (trial periods, subscription limits, usage quotas?)
9. How do users relate to other entities? (teams, organizations, projects, content?)
10. What events should trigger automated actions? (welcome emails, notifications, cleanup?)

## Phase 2: Access Control & Permissions
**Build on identity to define what users can do**

### Authorization & Permissions
11. What roles exist in our system? (admin, manager, user, guest?)
12. Are permissions role-based, attribute-based, or resource-based?
13. Can users belong to multiple roles or groups simultaneously?
14. How granular should permissions be? (feature-level, resource-level, field-level?)
15. Who can modify user permissions and roles?

## Phase 3: Data & Profile Management
**Define what information we store and how**

### Profile & Personal Data
16. What user information is required vs. optional?
17. What validation rules apply to user data? (email format, age limits, phone numbers?)
18. What privacy controls do users have over their data?
19. What personalization options do we support? (language, timezone, themes?)
20. How do users update their profile information?

### State Management
21. How long do user sessions last and can users have multiple concurrent sessions?
22. What user activities should we log for audit purposes?
23. How long do we retain user data after account deletion?
24. What happens to user-created content when they leave?
25. How do we handle data export requests?

## Phase 4: Technical Implementation
**Address system-level concerns**

### Technical Considerations
26. What are our performance requirements? (concurrent users, response times?)
27. Where will user data be cached and how do we ensure consistency?
28. What user data needs encryption at rest and in transit?
29. How do we handle user data across microservices or distributed systems?
30. What external systems need user information? (analytics, CRM, billing?)
31. How do we handle user data synchronization with external systems?
32. What are our backup and disaster recovery requirements for user data?

## Recommended Question Flow:
1. **Start with questions 1-10** to establish the foundation
2. **Move to questions 11-15** to define access patterns
3. **Address questions 16-25** to understand data requirements
4. **Finish with questions 26-32** for technical implementation