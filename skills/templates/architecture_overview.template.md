# [Product Name]

## Architecture Overview

### Purpose

This document provides a comprehensive overview of the system architecture to inform the Architect about existing technical design, patterns, constraints, and integration patterns. This serves as a
technical reference for understanding the current architecture when designing new features, evaluating technologies, and ensuring consistency with existing design patterns.

**Important**: This document must document not just **what** the architecture is, but **why** architectural decisions were made. Understanding the rationale behind existing architecture enables
informed decisions about when to follow existing patterns and when it's appropriate to deviate. Every architectural choice should include its reasoning, trade-offs, and constraints that influenced the
decision.

---

## 1. System Architecture & Service Decomposition

### High-Level Architecture

- **Architecture Style**: [Monolithic, Microservices, Modular Monolith, etc.]
- **Why This Style**: [Rationale for choosing this architecture style - what problems it solves, what constraints it addresses]
- **Deployment Model**: [Single application, distributed services, containerized, etc.]
- **Why This Deployment Model**: [Rationale for this deployment approach - scalability, operational, or cost considerations]
- **Communication Patterns**: [Synchronous (REST), Asynchronous (Events/Message Bus), Hybrid]
- **Why These Patterns**: [Rationale for communication patterns - performance, decoupling, consistency requirements]

### Service/Module Decomposition

- **Service/Module 1**: [Name]
    - **Responsibility**: [What this service/module is responsible for]
    - **Why Separated**: [Rationale for why this is a separate service/module - single responsibility, scalability, team boundaries, etc.]
    - **Key Components**: [Main components within this service]
    - **Dependencies**: [What other services/modules it depends on]
    - **APIs/Interfaces**: [How other services interact with it]

- **Service/Module 2**: [Name]
    - **Responsibility**: [What this service/module is responsible for]
    - **Why Separated**: [Rationale for why this is a separate service/module - single responsibility, scalability, team boundaries, etc.]
    - **Key Components**: [Main components within this service]
    - **Dependencies**: [What other services/modules it depends on]
    - **APIs/Interfaces**: [How other services interact with it]

- **Service/Module 3**: [Name]
    - **Responsibility**: [What this service/module is responsible for]
    - **Why Separated**: [Rationale for why this is a separate service/module - single responsibility, scalability, team boundaries, etc.]
    - **Key Components**: [Main components within this service]
    - **Dependencies**: [What other services/modules it depends on]
    - **APIs/Interfaces**: [How other services interact with it]

### Service Communication Patterns

- **Synchronous Communication**: [REST APIs, direct function calls, etc.]
    - **Why Synchronous**: [When and why synchronous communication is used - real-time requirements, transaction consistency, etc.]
- **Asynchronous Communication**: [Event bus, message queues, Cloud Tasks, etc.]
    - **Why Asynchronous**: [When and why asynchronous communication is used - decoupling, scalability, long-running operations, etc.]
- **Internal Message Bus**: [If applicable - how modules communicate internally]
    - **Why Message Bus**: [Rationale for using message bus - decoupling, event sourcing, etc.]
- **Event-Driven Patterns**: [How events flow through the system]
    - **Why Event-Driven**: [Rationale for event-driven architecture - scalability, loose coupling, auditability, etc.]

---

## 2. Technology Stack & Frameworks

### Technology Selection Rationale

- **Why These Technologies**: [Overall rationale for technology choices - team expertise, ecosystem, performance, maintainability, etc.]
- **Technology Constraints**: [Constraints that influenced technology selection - existing infrastructure, compliance, vendor relationships, etc.]

### Backend Technology Stack

- **Language**: [Programming language and version]
    - **Why This Language**: [Rationale for language choice - performance, ecosystem, team expertise, etc.]
- **Framework**: [Web framework name and version]
    - **Why This Framework**: [Rationale for framework choice - features, performance, community, etc.]
- **ORM/Database Layer**: [ORM library, database abstraction layer]
    - **Why This ORM**: [Rationale for ORM choice - features, performance, migration support, etc.]
- **API Framework**: [REST framework, GraphQL, etc.]
    - **Why This API Framework**: [Rationale for API framework choice - standards compliance, tooling, etc.]
- **Validation/Serialization**: [Pydantic, Marshmallow, etc.]
    - **Why This Validation Library**: [Rationale for validation approach - type safety, performance, developer experience, etc.]

### Frontend Technology Stack (if applicable)

- **Framework**: [React, Vue, Angular, etc. and version]
    - **Why This Framework**: [Rationale for frontend framework choice - ecosystem, performance, developer experience, etc.]
- **Language**: [TypeScript, JavaScript, etc.]
    - **Why This Language**: [Rationale for language choice - type safety, tooling, etc.]
- **UI Library**: [Material-UI, Tailwind, etc.]
    - **Why This UI Library**: [Rationale for UI library choice - design system, customization, bundle size, etc.]
- **State Management**: [Redux, Context API, SWR, etc.]
    - **Why This State Management**: [Rationale for state management approach - complexity, performance, developer experience, etc.]
- **Build Tool**: [Webpack, Vite, Next.js, etc.]
    - **Why This Build Tool**: [Rationale for build tool choice - performance, features, ecosystem, etc.]

### Database & Storage

- **Database**: [PostgreSQL, MySQL, MongoDB, etc. and version]
    - **Why This Database**: [Rationale for database choice - ACID requirements, JSON support, scalability, etc.]
- **Migration Tool**: [Alembic, Flyway, etc.]
    - **Why This Migration Tool**: [Rationale for migration tool choice - framework integration, features, etc.]
- **Storage Solution**: [File storage, object storage, etc.]
    - **Why This Storage**: [Rationale for storage solution - scalability, cost, access patterns, etc.]
- **Caching**: [Redis, Memcached, in-memory, etc.]
    - **Why This Caching**: [Rationale for caching approach - performance requirements, data characteristics, etc.]

### Infrastructure & Deployment

- **Containerization**: [Docker, Kubernetes, etc.]
- **Cloud Platform**: [AWS, GCP, Azure, etc.]
- **Deployment Target**: [Cloud Run, ECS, Kubernetes, etc.]
- **CI/CD**: [GitHub Actions, GitLab CI, Jenkins, etc.]

### Development Tools

- **Testing Framework**: [pytest, Jest, etc.]
- **Code Quality**: [Linters, type checkers, formatters]
- **Documentation**: [API documentation tools, ADR tools]

---

## 3. Design Patterns & Architectural Patterns

### Design Patterns Used

- **Pattern 1**: [Name - e.g., Repository/DAO Pattern]
    - **Where Used**: [Which modules/services use this pattern]
    - **Why This Pattern**: [Rationale for choosing this pattern - what problem it solves, what benefits it provides]
    - **Trade-offs**: [What trade-offs were made - complexity vs. flexibility, performance vs. maintainability, etc.]
    - **Implementation**: [How it's implemented - file locations, class names]

- **Pattern 2**: [Name - e.g., Unit of Work Pattern]
    - **Where Used**: [Which modules/services use this pattern]
    - **Why This Pattern**: [Rationale for choosing this pattern - transaction management, consistency, etc.]
    - **Trade-offs**: [What trade-offs were made]
    - **Implementation**: [How it's implemented]

- **Pattern 3**: [Name - e.g., Strategy Pattern]
    - **Where Used**: [Which modules/services use this pattern]
    - **Why This Pattern**: [Rationale for choosing this pattern - flexibility, extensibility, etc.]
    - **Trade-offs**: [What trade-offs were made]
    - **Implementation**: [How it's implemented]

- **Pattern 4**: [Name - e.g., Facade Pattern]
    - **Where Used**: [Which modules/services use this pattern]
    - **Why This Pattern**: [Rationale for choosing this pattern - simplification, API design, etc.]
    - **Trade-offs**: [What trade-offs were made]
    - **Implementation**: [How it's implemented]

### Architectural Patterns

- **Event-Driven Architecture**: [How events are used, event bus implementation]
    - **Why Event-Driven**: [Rationale for event-driven approach - decoupling, scalability, auditability, etc.]
- **Layered Architecture**: [Presentation, Business Logic, Data layers]
    - **Why Layered**: [Rationale for layered architecture - separation of concerns, testability, maintainability, etc.]
- **Domain-Driven Design**: [Domain models, bounded contexts]
    - **Why DDD**: [Rationale for DDD approach - complex domain, team structure, etc.]
- **Object-Oriented Design**: [How OOP principles are applied, class organization]
    - **Why OOP**: [Rationale for OOP approach - encapsulation, maintainability, code organization, etc.]

---

## 4. Code Organization & Conventions

### File Structure & Naming Conventions

- **Module Organization**: [How code is organized - by feature, by layer, etc.]
    - **Why This Organization**: [Rationale for organization approach - team structure, feature boundaries, maintainability, etc.]
- **File Naming**: [Conventions for files - router.py, models.py, schemas.py, etc.]
    - **Why These Conventions**: [Rationale for naming conventions - discoverability, consistency, framework patterns, etc.]
- **Directory Structure**: [How directories are organized]
    - **Why This Structure**: [Rationale for directory structure - scalability, navigation, team collaboration, etc.]
- **Package/Module Structure**: [How modules are packaged]
    - **Why This Packaging**: [Rationale for packaging approach - dependencies, reusability, etc.]

### Code Style & Conventions

- **Coding Standards**: [PEP 8, Google Style, etc.]
- **Documentation Standards**: [Docstring format, ADR format]
- **Exception Handling**: [Where exceptions are caught, custom exception types]
- **Logging Conventions**: [Logging patterns, correlation IDs]
- **Type Hints**: [Type checking approach, typing standards]

### Object-Oriented Design Principles

- **Data and Behavior Together**: [How related data and logic are grouped]
- **Class Organization**: [How classes are structured and organized]
- **Inheritance vs Composition**: [When each is used]
- **Encapsulation**: [How data is encapsulated]

---

## 5. Data Architecture & Storage

### Database Design Patterns

- **ORM Usage**: [How ORM is used, active record vs data mapper]
    - **Why This ORM Pattern**: [Rationale for ORM pattern choice - abstraction level, performance, maintainability, etc.]
- **Migration Strategy**: [How schema changes are managed]
    - **Why This Migration Strategy**: [Rationale for migration approach - safety, rollback capability, team coordination, etc.]
- **Transaction Management**: [How transactions are handled, unit of work pattern]
    - **Why This Transaction Approach**: [Rationale for transaction management - consistency, performance, complexity, etc.]
- **Optimistic Locking**: [Version fields, concurrency control]
    - **Why Optimistic Locking**: [Rationale for optimistic vs pessimistic locking - concurrency patterns, performance, etc.]
- **Soft Deletes**: [How soft deletes are implemented]
    - **Why Soft Deletes**: [Rationale for soft deletes - audit requirements, data recovery, compliance, etc.]

### Data Storage Patterns

- **Relational Data**: [How relational data is stored]
    - **Why Relational**: [Rationale for relational storage - ACID requirements, relationships, query patterns, etc.]
- **JSON/JSONB Storage**: [When and how JSON fields are used]
    - **Why JSON/JSONB**: [Rationale for JSON storage - flexibility, schema evolution, query patterns, etc.]
- **File Storage**: [How files are stored and organized]
    - **Why This File Storage**: [Rationale for file storage approach - scalability, cost, access patterns, etc.]
- **Caching Strategy**: [What is cached and how]
    - **Why This Caching**: [Rationale for caching strategy - performance requirements, data characteristics, consistency needs, etc.]

### Data Flow Patterns

- **Data Collection**: [How data flows into the system]
- **Data Processing**: [How data is processed and transformed]
- **Data Persistence**: [How data is persisted]
- **Data Retrieval**: [How data is queried and retrieved]

---

## 6. Integration Patterns & Communication

### Internal Integration Patterns

- **Module Communication**: [How modules communicate internally]
    - **Why This Communication Pattern**: [Rationale for internal communication approach - coupling, testability, performance, etc.]
- **Event Bus**: [Internal message bus, event routing]
    - **Why Event Bus**: [Rationale for event bus - decoupling, scalability, event sourcing, etc.]
- **Service Calls**: [Direct service calls, dependency injection]
    - **Why Direct Calls**: [Rationale for direct calls vs. events - simplicity, performance, transaction boundaries, etc.]
- **Shared Libraries**: [Common utilities, shared code]
    - **Why Shared Libraries**: [Rationale for shared code approach - DRY principle, consistency, maintenance, etc.]

### External Integration Patterns

- **API Integration**: [REST, GraphQL, gRPC, etc.]
    - **Why This API Style**: [Rationale for API style choice - standards, tooling, performance, ecosystem, etc.]
- **OAuth Flows**: [OAuth 2.0 implementation patterns]
    - **Why OAuth 2.0**: [Rationale for OAuth approach - security, standardization, provider support, etc.]
- **Webhook Handling**: [How webhooks are processed]
    - **Why Webhooks**: [Rationale for webhook pattern - real-time updates, decoupling, etc.]
- **Async Task Processing**: [How async tasks are handled]
    - **Why Async Processing**: [Rationale for async approach - performance, scalability, user experience, etc.]

### Error Handling & Resilience

- **Retry Logic**: [Retry patterns, exponential backoff]
- **Circuit Breakers**: [If used, how they're implemented]
- **Error Propagation**: [How errors flow through the system]
- **Fallback Mechanisms**: [How failures are handled]

---

## 7. System Events & Event Architecture

### Event-Driven Architecture Overview

- **Event System**: [Overview of the event system - event bus, event publisher, event routing mechanism]
- **Why Event-Driven**: [Rationale for using events - decoupling, scalability, async processing, etc.]
- **Event Processing Model**: [Synchronous vs asynchronous event processing, event queues, event handlers]
- **Event Storage**: [Whether events are stored, event history, event replay capabilities]

### System Events

- **Event 1: [Event Name/Type]**
    - **Event Type**: [Technical event type/class name]
    - **Purpose**: [What this event represents from a system perspective]
    - **Triggers**:
        - [What system action, user action, or condition triggers this event]
        - [What module or component publishes this event]
        - [Any prerequisites or conditions required]
    - **When It Occurs**: [Specific circumstances, timing, or system state when this event fires]
    - **Event Payload**:
        - [What data is included in the event payload]
        - [Key fields and their types]
        - [Correlation IDs or identifiers]
    - **Subscribers/Handlers**:
        - [Which modules or components subscribe to this event]
        - [What handlers process this event]
        - [What actions are taken when the event is received]
    - **Processing**:
        - [Synchronous or asynchronous processing]
        - [Processing time or latency expectations]
        - [Error handling if processing fails]
    - **Downstream Effects**:
        - [What system operations or state changes result from this event]
        - [What other events might be triggered as a result]
        - [What modules are affected]
    - **Technical Implementation**:
        - [How the event is published - event bus, message queue, etc.]
        - [Event routing mechanism]
        - [Event serialization format]

- **Event 2: [Event Name/Type]**
    - **Event Type**: [Technical event type/class name]
    - **Purpose**: [What this event represents from a system perspective]
    - **Triggers**:
        - [What system action, user action, or condition triggers this event]
        - [What module or component publishes this event]
        - [Any prerequisites or conditions required]
    - **When It Occurs**: [Specific circumstances, timing, or system state when this event fires]
    - **Event Payload**:
        - [What data is included in the event payload]
        - [Key fields and their types]
        - [Correlation IDs or identifiers]
    - **Subscribers/Handlers**:
        - [Which modules or components subscribe to this event]
        - [What handlers process this event]
        - [What actions are taken when the event is received]
    - **Processing**:
        - [Synchronous or asynchronous processing]
        - [Processing time or latency expectations]
        - [Error handling if processing fails]
    - **Downstream Effects**:
        - [What system operations or state changes result from this event]
        - [What other events might be triggered as a result]
        - [What modules are affected]
    - **Technical Implementation**:
        - [How the event is published - event bus, message queue, etc.]
        - [Event routing mechanism]
        - [Event serialization format]

- **Event 3: [Event Name/Type]**
    - **Event Type**: [Technical event type/class name]
    - **Purpose**: [What this event represents from a system perspective]
    - **Triggers**:
        - [What system action, user action, or condition triggers this event]
        - [What module or component publishes this event]
        - [Any prerequisites or conditions required]
    - **When It Occurs**: [Specific circumstances, timing, or system state when this event fires]
    - **Event Payload**:
        - [What data is included in the event payload]
        - [Key fields and their types]
        - [Correlation IDs or identifiers]
    - **Subscribers/Handlers**:
        - [Which modules or components subscribe to this event]
        - [What handlers process this event]
        - [What actions are taken when the event is received]
    - **Processing**:
        - [Synchronous or asynchronous processing]
        - [Processing time or latency expectations]
        - [Error handling if processing fails]
    - **Downstream Effects**:
        - [What system operations or state changes result from this event]
        - [What other events might be triggered as a result]
        - [What modules are affected]
    - **Technical Implementation**:
        - [How the event is published - event bus, message queue, etc.]
        - [Event routing mechanism]
        - [Event serialization format]

### Event Flows & Dependencies

- **Event Flow 1: [Flow Name]**
    - **Sequence**: [Order of events in this flow - Event A → Event B → Event C]
    - **Trigger**: [What initiates this event flow]
    - **Dependencies**: [Which events depend on others, what must happen first]
    - **Technical Context**: [What system process or workflow this flow supports]
    - **Error Handling**: [What happens if an event in the flow fails - retry, rollback, compensation]
    - **Performance Characteristics**: [Expected latency, throughput, scalability considerations]

- **Event Flow 2: [Flow Name]**
    - **Sequence**: [Order of events]
    - **Trigger**: [What initiates this event flow]
    - **Dependencies**: [Event dependencies]
    - **Technical Context**: [System process supported]
    - **Error Handling**: [Failure scenarios]
    - **Performance Characteristics**: [Latency, throughput, scalability]

### Event Processing Patterns

- **Synchronous Events**: [Events processed immediately and block operations]
    - **Why Synchronous**: [Technical rationale for immediate processing - consistency, transaction boundaries, etc.]
    - **Use Cases**: [When synchronous processing is used]
    - **Performance Impact**: [How synchronous processing affects system performance]

- **Asynchronous Events**: [Events processed in the background]
    - **Why Asynchronous**: [Technical rationale for background processing - performance, scalability, long-running operations, etc.]
    - **Processing Mechanism**: [How async events are processed - queues, Cloud Tasks, message brokers, etc.]
    - **Processing Time**: [Expected time for async processing]
    - **Reliability**: [How async event processing is made reliable - retry logic, dead letter queues, etc.]

### Event Infrastructure

- **Event Bus/Message Queue**: [What technology is used for event routing - internal event bus, Cloud Tasks, message broker, etc.]
    - **Why This Technology**: [Rationale for event infrastructure choice - scalability, reliability, features, etc.]
- **Event Serialization**: [How events are serialized - JSON, Protocol Buffers, Avro, etc.]
    - **Why This Format**: [Rationale for serialization format - performance, compatibility, schema evolution, etc.]
- **Event Routing**: [How events are routed to subscribers - topic-based, queue-based, direct routing, etc.]
    - **Why This Routing**: [Rationale for routing mechanism]
- **Event Ordering**: [Whether event ordering is guaranteed, ordering guarantees, partitioning strategy]
    - **Why Ordering Matters**: [When and why event ordering is important]
- **Event Deduplication**: [Whether duplicate events are handled, idempotency mechanisms]
    - **Why Deduplication**: [When and why duplicate events might occur and how they're handled]

### Event Observability & Monitoring

- **Event Logging**: [How events are logged - structured logging, event traces, correlation IDs]
- **Event Metrics**: [What metrics are tracked - event volume, processing time, error rates, etc.]
- **Event Tracing**: [How events are traced across the system - correlation IDs, distributed tracing]
- **Event Monitoring**: [How events are monitored - dashboards, alerts, anomaly detection]
- **Event Debugging**: [How events can be debugged - event replay, event inspection tools]

---

## 8. Security & Compliance Architecture

### Authentication & Authorization

- **Authentication Method**: [JWT, OAuth, session-based, etc.]
    - **Why This Authentication**: [Rationale for authentication method - statelessness, scalability, security, etc.]
- **Authorization Model**: [Role-based, scope-based, attribute-based]
    - **Why This Authorization Model**: [Rationale for authorization approach - flexibility, granularity, complexity, etc.]
- **Token Management**: [How tokens are stored, refreshed, validated]
    - **Why This Token Management**: [Rationale for token management approach - security, performance, refresh patterns, etc.]
- **Multi-tenant Isolation**: [How customer data is isolated]
    - **Why This Isolation Approach**: [Rationale for isolation strategy - security, compliance, performance, etc.]

### Data Security

- **Encryption**: [Data encryption at rest and in transit]
- **Sensitive Data Handling**: [How sensitive data is protected]
- **Session Security**: [How sessions are secured]
- **API Security**: [API authentication, rate limiting, etc.]

### Compliance Considerations

- **Data Privacy**: [GDPR, data retention, user rights]
- **Audit Trails**: [How actions are logged and audited]
- **Data Isolation**: [How data is isolated between tenants/customers]
- **Regulatory Requirements**: [Industry-specific compliance needs]

---

## 9. Technical Constraints & Risks

### Technical Constraints

- **Database Constraints**: [PostgreSQL-specific features, schema limitations]
- **Framework Constraints**: [Framework limitations, version constraints]
- **Third-Party Service Constraints**: [Rate limits, API limitations]
- **Deployment Constraints**: [Cloud platform limitations, scaling constraints]

### Architectural Risks

- **Single Points of Failure**: [Critical dependencies, bottlenecks]
- **Scalability Risks**: [Potential scaling issues, bottlenecks]
- **Technology Lock-in**: [Vendor lock-in, framework dependencies]
- **Technical Debt**: [Known technical debt areas]

### Performance Considerations

- **Bottlenecks**: [Known performance bottlenecks]
- **Optimization Strategies**: [Caching, query optimization, etc.]
- **Monitoring**: [How performance is monitored]

---

## 10. Third-Party Services & Integrations

### Service 1: [Service Name]

- **Provider**: [Company/Organization providing the service]
- **Purpose**: [What business need or capability does this service fulfill?]
- **Why This Service**: [Rationale for choosing this service over alternatives - features, cost, reliability, ecosystem, etc.]
- **What It Does**: [Detailed description of the service's functionality and how it works]
- **Integration Method**: [How the system connects to this service - API, SDK, webhook, etc.]
    - **Why This Integration Method**: [Rationale for integration approach - performance, reliability, features, etc.]
- **Data Flow**: [What data is sent to/received from this service]
- **Key Features Used**: [Specific features or capabilities of the service that are utilized]
- **Dependencies**: [What the system depends on from this service]
- **Limitations**: [Known limitations, rate limits, or constraints of this service]
- **Cost/Impact**: [Any cost implications or business impact of using this service]
- **Trade-offs**: [What trade-offs were made in choosing this service - vendor lock-in, cost vs. features, etc.]

### Service 2: [Service Name]

- **Provider**: [Company/Organization providing the service]
- **Purpose**: [What business need or capability does this service fulfill?]
- **Why This Service**: [Rationale for choosing this service over alternatives - features, cost, reliability, ecosystem, etc.]
- **What It Does**: [Detailed description of the service's functionality and how it works]
- **Integration Method**: [How the system connects to this service - API, SDK, webhook, etc.]
    - **Why This Integration Method**: [Rationale for integration approach - performance, reliability, features, etc.]
- **Data Flow**: [What data is sent to/received from this service]
- **Key Features Used**: [Specific features or capabilities of the service that are utilized]
- **Dependencies**: [What the system depends on from this service]
- **Limitations**: [Known limitations, rate limits, or constraints of this service]
- **Cost/Impact**: [Any cost implications or business impact of using this service]
- **Trade-offs**: [What trade-offs were made in choosing this service - vendor lock-in, cost vs. features, etc.]

### Service 3: [Service Name]

- **Provider**: [Company/Organization providing the service]
- **Purpose**: [What business need or capability does this service fulfill?]
- **Why This Service**: [Rationale for choosing this service over alternatives - features, cost, reliability, ecosystem, etc.]
- **What It Does**: [Detailed description of the service's functionality and how it works]
- **Integration Method**: [How the system connects to this service - API, SDK, webhook, etc.]
    - **Why This Integration Method**: [Rationale for integration approach - performance, reliability, features, etc.]
- **Data Flow**: [What data is sent to/received from this service]
- **Key Features Used**: [Specific features or capabilities of the service that are utilized]
- **Dependencies**: [What the system depends on from this service]
- **Limitations**: [Known limitations, rate limits, or constraints of this service]
- **Cost/Impact**: [Any cost implications or business impact of using this service]
- **Trade-offs**: [What trade-offs were made in choosing this service - vendor lock-in, cost vs. features, etc.]

### OAuth/Identity Providers

- **Provider 1**: [Name of OAuth provider]
    - **Purpose**: [Why this provider is integrated - what user data or capabilities it provides]
    - **Why This Provider**: [Rationale for integrating this OAuth provider - user base, data quality, API reliability, etc.]
    - **OAuth Flow**: [Description of the OAuth 2.0 flow used]
    - **Why This OAuth Flow**: [Rationale for OAuth flow choice - security, user experience, refresh token availability, etc.]
    - **Data Collected**: [What user data is collected from this provider]
    - **Scopes/Permissions**: [What OAuth scopes are requested]
    - **Why These Scopes**: [Rationale for scope selection - data needs, privacy considerations, user consent, etc.]
    - **Token Management**: [How access tokens are stored and refreshed]
    - **Why This Token Management**: [Rationale for token management approach - security, refresh patterns, storage constraints, etc.]
    - **Use Cases**: [When and why this provider is used in the system]

- **Provider 2**: [Name of OAuth provider]
    - **Purpose**: [Why this provider is integrated - what user data or capabilities it provides]
    - **Why This Provider**: [Rationale for integrating this OAuth provider - user base, data quality, API reliability, etc.]
    - **OAuth Flow**: [Description of the OAuth 2.0 flow used]
    - **Why This OAuth Flow**: [Rationale for OAuth flow choice - security, user experience, refresh token availability, etc.]
    - **Data Collected**: [What user data is collected from this provider]
    - **Scopes/Permissions**: [What OAuth scopes are requested]
    - **Why These Scopes**: [Rationale for scope selection - data needs, privacy considerations, user consent, etc.]
    - **Token Management**: [How access tokens are stored and refreshed]
    - **Why This Token Management**: [Rationale for token management approach - security, refresh patterns, storage constraints, etc.]
    - **Use Cases**: [When and why this provider is used in the system]

### Integration Dependencies

- **Critical Dependencies**: [Services that are critical for core functionality - what happens if they're unavailable]
- **Optional Dependencies**: [Services that enhance functionality but aren't critical]
- **Fallback Mechanisms**: [How the system handles service unavailability or failures]
- **Service Level Agreements**: [Any SLAs or guarantees from third-party providers]

---

## 11. Architecture Decision Records (ADRs)

### Key Architectural Decisions

- **Decision 1**: [Title of architectural decision]
    - **Context**: [What situation led to this decision]
    - **Decision**: [What was decided]
    - **Rationale**: [Why this decision was made]
    - **Consequences**: [Positive and negative consequences]
    - **Status**: [Active, Superseded, Deprecated]
    - **Location**: [Link to ADR document]

- **Decision 2**: [Title of architectural decision]
    - **Context**: [What situation led to this decision]
    - **Decision**: [What was decided]
    - **Rationale**: [Why this decision was made]
    - **Consequences**: [Positive and negative consequences]
    - **Status**: [Active, Superseded, Deprecated]
    - **Location**: [Link to ADR document]

### ADR Management

- **ADR Location**: [Where ADRs are stored]
- **ADR Format**: [Standard format used for ADRs]
- **Review Process**: [How ADRs are reviewed and maintained]

---

## Notes for Architect

### Key Considerations When Designing New Features

- [Important architectural constraint or pattern to follow]
- [Important architectural constraint or pattern to follow]
- [Important architectural constraint or pattern to follow]

### Areas Requiring Architectural Attention

- [Area that may need architectural refactoring or improvement]
- [Area that may need architectural refactoring or improvement]

### Related Documentation

- [Links to ADRs, design documents, API specifications, etc.]

---

## Document Maintenance

**Last Updated**: [Date]
**Maintained By**: [Role/Team]
**Review Frequency**: [How often this should be reviewed]

