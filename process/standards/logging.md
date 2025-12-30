# Logging and Observability Standards

## Core Principles

### 1. Use Structured Events, Not Traditional Logs

- **Emit one wide, structured event per service hop** - Each request that touches a service should generate a single, comprehensive event containing all relevant context
- **Avoid multiple log lines per request** - Consolidate all information into one rich event to reduce redundancy and improve clarity
- **Use structured formats** (JSON, structured logging) - Enable efficient querying and analysis

### 2. Events Must Be Unique, Ordered, and Traceable

- **Always include unique identifiers**:
  - Request ID (propagate through entire stack)
  - Trace ID (for distributed tracing)
  - User ID, Session ID, Transaction ID
  - Any other high-cardinality identifiers relevant to your domain
- **Preserve sequence/ordering** - Events should be timestamped and ordered to reconstruct request flows
- **Propagate request context** - Ensure request IDs flow through all service boundaries (HTTP headers, message queues, etc.)

### 3. Store Raw Events (No Pre-Aggregation)

- **Never aggregate at write time** - Aggregation is a one-way trip that destroys your ability to ask new questions
- **Store raw, unprocessed events** - You can always derive metrics, dashboards, and aggregates from raw events, but never reverse the process
- **Use columnar storage** - Enables efficient querying of high-cardinality data

### 4. Include Rich Contextual Information

Each event should be "arbitrarily wide" and include:

#### Technical Context
- **Request metadata**: HTTP method, path, headers, status codes
- **Timing information**: Duration, latency breakdowns, timestamps
- **Network calls**: All outgoing HTTP calls, their timing and contents
- **Database queries**: Raw queries, normalized query families, execution times
- **Infrastructure details**: Availability zone, instance type, cloud provider
- **Environment context**: Language version, build flags, environment variables
- **System state**: Resource metrics, network stats (when relevant)

#### Business Context
- **User information**: User ID, subscription tier, account type
- **Business identifiers**: Order ID, cart ID, transaction ID, feature flags
- **Application state**: Service name, build ID, deployment version
- **Domain-specific data**: Any context that helps understand the business impact of technical issues

### 5. Intelligent Sampling

- **Sample on the client side** - Control sampling at the source, not at the server
- **Keep interesting events**:
  - All errors (4xx, 5xx status codes)
  - All mutations (POST, PUT, DELETE, database writes)
  - Critical business operations (login, payment, checkout)
- **Sample heavily for boring events**:
  - Health checks returning 200 OK
  - Routine SELECT queries
  - Common, low-value operations
- **Don't treat observability data like billing data** - It's okay to be selective

### 6. First-Person Narrative (Self-Reported)

- **Log from the code's perspective** - Your application should explain itself from the inside out
- **Self-reported status** - Code reports what it's doing as it executes, not external monitoring checking up on it
- **Observability vs. Monitoring**:
  - **Monitoring**: Third-person perspective, watching for known-unknowns, predefined thresholds
  - **Observability**: First-person perspective, understanding unknown-unknowns, asking new questions without shipping code

### 7. Observability for Unknown-Unknowns

- **Design for exploratory analysis** - You must be able to ask brand new questions without shipping new code
- **Support ad-hoc queries** - Your event structure should enable answering questions you never anticipated
- **Think like business intelligence** - Exploratory data sifting to detect novel patterns and behaviors

## Anti-Patterns to Avoid

### ❌ Don't Do This

- Multiple log lines per request (creates redundancy and cost)
- Unstructured log messages (hard to query and analyze)
- Pre-aggregating data at write time (destroys ability to ask new questions)
- Relying only on metrics (lacks context and connective tissue)
- Dumb sampling (sampling everything equally, or sampling at server side)
- Logging without unique identifiers (can't trace requests)
- Treating observability data like production data (over-investing in reliability)

### ✅ Do This Instead

- One wide, structured event per service hop
- Structured formats (JSON) with rich context
- Store raw events, aggregate on read
- Use events as primary source, derive metrics from events
- Intelligent client-side sampling (keep interesting, drop boring)
- Always include request/trace IDs and propagate them
- Sample appropriately - observability data doesn't need 100% reliability

## Implementation Guidelines

1. **Event Structure**: Use JSON or structured logging format
2. **One Event Per Hop**: Each service interaction generates exactly one event
3. **Propagate Context**: Use headers, context objects, or middleware to pass request IDs
4. **Include Everything**: When in doubt, include more context rather than less
5. **Sample Intelligently**: Implement client-side sampling that keeps high-value events
6. **Query-Friendly Storage**: Use systems that support efficient querying of structured, high-cardinality data

## References

- [Live Your Best Life With Structured Events](https://charity.wtf/2022/08/15/live-your-best-life-with-structured-events/)
- [Logging Sucks](https://loggingsucks.com/)

