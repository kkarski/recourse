### Topics the Product Manager should consider exploring about any feature

#### Scope (breadth-first)
- **First**: Discover and uncover all explicit and implicit requirements. Do not go deep on one area until breadth is covered.
- **Inventory**: List every metric, chart, section, and user-visible outcome mentioned in the problem statement or in any existing plan/spec. Ensure at least one question per item (in/out of scope? how defined? how shown?) before moving to depth.
- Explore in-scope and out-of-scope use cases for the proposed feature.
- Perform an end-to-end step-by-step use case walkthrough to ensure all use cases and actors have been identified.
- Review existing product features and understand how this new feature will integrate with existing features.
- Don't get stuck on a single area or topic; be comprehensive across all items before drilling down.

#### Discovery (unpack implicit and embedded requirements)
- Discover requirements embedded in adjectives and declarative statements (e.g. "significant", "top", "repeat").
- Unpack requirements behind names and titles of features, metrics, and functions—each name may hide a definition, threshold, or rule.
- **For each metric**: What does it mean (definition)? How should it be displayed (unit, format, label)? Any threshold or band? Priority for first release?
- **For each chart or visualization**: What does it show? Chart type (line/bar/pie) and axes? Any threshold line or band (e.g. p90)? What is the empty state?
- **For each qualified term** (e.g. "significant ads", "viewer segment", "top advertisers"): How is it defined (e.g. percentile, count, ranking rule)? Who decides the definition? How is it shown to the user?

#### When a plan or prior spec exists
- **Inventory**: From the plan/spec, list every metric, chart, acceptance criterion (or scenario), feature name, and qualified term.
- **One question per item**: For each item, ask at least one discovery question—definition, display, priority, or confirmation. Do not assume the plan is the product requirement; treat it as a source of implicit requirements to unpack.
- **Reconcile later**: Ensure the business spec reflects or explicitly overrides every plan item that has user-facing impact. No silent omission—either include in spec or mark out of scope.

#### Context
- Explore the motivations behind the feature: the why.

#### Diverse discovery questions (avoid going deep in one direction)
- Vary question types across the inventory: definition, display/UX, priority/scope, edge case, and confirmation. Do not ask five follow-ups on access control before asking anything about metrics or charts.
- For each topic area (scope, validation, UX, integration, etc.), ask a few breadth questions that touch many items (e.g. "For each of these metrics: in scope for v1?") before asking depth questions on a single item (e.g. "When metric X is null, exactly what message?").
- Explicitly include questions that map plan/spec content to business meaning: e.g. "The plan mentions [metric/chart/term]—how should we define it for the user?" or "How should [X] be shown on the page?"

#### Reports, dashboards, and analytics (when the feature includes metrics or charts)
- **Metrics**: For each metric—definition (how computed or sourced), unit and format (e.g. seconds, %, count), label/copy, and behavior when missing or zero (show zero, hide, or distinct empty state).
- **Charts**: For each chart—what it represents, chart type and axes, any reference line or threshold (and what it means to the user), empty state (hide section, show "No data", or other).
- **Segments/classifications** (e.g. viewer segment, "significant" vs not): How are buckets or thresholds defined (percentile, count, rule)? How are they labeled and displayed?
- **Acceptance criteria**: Ensure business-level AC exist for: which metrics/charts are shown, when sections are hidden or shown, and what "success" looks like for the report (not only technical triggers and API behavior).