# Spectr spec XML entity model

Pydantic-XML models for a Spectr specification document (`SpectrDocument` root). Source: `spectr/src/spectr/spec_xml_model.py`.

Layout constraints (body `<div>` block order, use-case child sequence, acceptance-criteria vs questions ordering) are enforced by Pydantic **`model_validator`** hooks on `SpecificationBody`, `UseCaseSection`, `UseCaseAcceptanceCriteria`, and `SpecificationAcceptanceCriteria` during `SpectrDocument.from_xml_tree`.

`BodySection` is a type alias (union) in code, not a class; it is shown below as a logical grouping for `SpecificationBody.blocks`.

```mermaid
classDiagram
  direction TB

  class SpectrDocument
  class DocumentHead
  class DocumentTitle
  class SpecificationBody
  class BodySection {
    <<union>>
  }

  class ChangeSetTitle
  class UseCaseTitle
  class ChangeSetOverview
  class ScopePreconditions
  class UseCaseTrigger
  class UseCaseMainFlow
  class UseCasePostConditions
  class MermaidDiagram
  class UseCaseDescription
  class AcceptanceCriterion
  class LinkedTestCase
  class StakeholderQuestion
  class StakeholderAnswer
  class FeedbackNote
  class PlanTask
  class PlanPhase

  class UseCaseSection
  class UseCaseAcceptanceCriteria
  class SpecificationAcceptanceCriteria
  class ThreadedQuestions
  class SpecificationQuestions
  class TestSuiteSection
  class FeedbackSection
  class DeliveryPlanSection

  SpectrDocument --> DocumentHead : head
  SpectrDocument --> SpecificationBody : body
  DocumentHead --> DocumentTitle : title

  SpecificationBody --> ChangeSetTitle : h1
  SpecificationBody --> ChangeSetOverview : desc
  SpecificationBody o-- BodySection : blocks 0..*

  BodySection <|.. UseCaseSection
  BodySection <|.. SpecificationAcceptanceCriteria
  BodySection <|.. TestSuiteSection
  BodySection <|.. SpecificationQuestions
  BodySection <|.. FeedbackSection
  BodySection <|.. DeliveryPlanSection

  UseCaseSection o-- UseCaseTitle : children
  UseCaseSection o-- ScopePreconditions : children
  UseCaseSection o-- UseCaseTrigger : children
  UseCaseSection o-- UseCaseMainFlow : children
  UseCaseSection o-- UseCasePostConditions : children
  UseCaseSection o-- MermaidDiagram : children
  UseCaseSection o-- UseCaseDescription : children
  UseCaseSection o-- UseCaseAcceptanceCriteria : children
  UseCaseSection o-- ThreadedQuestions : children

  UseCaseAcceptanceCriteria o-- AcceptanceCriterion : children
  UseCaseAcceptanceCriteria o-- MermaidDiagram : children
  UseCaseAcceptanceCriteria o-- ThreadedQuestions : children

  SpecificationAcceptanceCriteria o-- AcceptanceCriterion : children
  SpecificationAcceptanceCriteria o-- MermaidDiagram : children
  SpecificationAcceptanceCriteria o-- ThreadedQuestions : children

  ThreadedQuestions o-- StakeholderQuestion : children
  ThreadedQuestions o-- StakeholderAnswer : children

  SpecificationQuestions o-- StakeholderQuestion : children
  SpecificationQuestions o-- StakeholderAnswer : children

  TestSuiteSection o-- LinkedTestCase : children
  TestSuiteSection o-- MermaidDiagram : children
  FeedbackSection o-- FeedbackNote : children
  DeliveryPlanSection o-- PlanPhase : children
  PlanPhase o-- PlanTask : tasks
```

All listed element classes extend `BaseXmlModel` from pydantic-xml; attributes (`id`, `sid`, `type`, and other XML attributes) are omitted from the diagram for readability.

## Conceptual model (aggregates & composites)

This view uses domain-driven design language: **aggregate** marks a consistency boundary (typically one persisted Spectr document), **composite** marks a tree of parts that share a structural invariant, and **entity** marks something with a stable identity (`id` / `sid` in XML). It is a conceptual map to the shapes above, not a second parallel type hierarchy in code.

```mermaid
classDiagram
  direction TB

  class SpectrSpecification {
    <<Aggregate Root>>
    +sid
  }

  class SpecHeader {
    <<Value Object / part>>
    +document title
  }

  class SpecOverview {
    <<Entity / part>>
    +spec id (h1)
    +description
  }

  class SpecSection {
    <<Composite>>
  }

  class UseCaseSection {
    <<Composite>>
    +optional sid
  }

  class StandaloneACSection {
    <<Composite>>
    +optional sid
  }

  class TestsSection {
    <<Composite>>
  }

  class QuestionsSection {
    <<Composite>>
  }

  class FeedbackSection {
    <<Composite>>
  }

  class PlanSection {
    <<Composite>>
  }

  class UseCaseTitle {
    <<Entity>>
    +id
  }

  class Narrative {
    <<Entity>>
    +id
  }

  class ScopePreconditions {
    <<Entity>>
    +id
  }

  class Trigger {
    <<Entity>>
    +id
  }

  class MainFlow {
    <<Entity>>
    +id
  }

  class PostConditions {
    <<Entity>>
    +id
  }

  class MermaidDiagram {
    <<Entity>>
    +id
    +diagram attr
  }

  class AcceptanceCluster {
    <<Composite>>
    +optional sid
  }

  class AcceptanceCriterion {
    <<Entity>>
    +id
  }

  class QuestionThread {
    <<Composite>>
  }

  class Question {
    <<Entity>>
    +id
  }

  class Answer {
    <<Entity>>
    +id
  }

  class TestCase {
    <<Entity>>
    +id
    +ref
  }

  class FeedbackItem {
    <<Entity>>
    +id
  }

  class Phase {
    <<Composite>>
    +optional sid
  }

  class PlanTask {
    <<Entity>>
    +id
  }

  SpectrSpecification *-- SpecHeader : head
  SpectrSpecification *-- SpecOverview : overview
  SpectrSpecification o-- SpecSection : sections ordered

  SpecSection <|.. UseCaseSection
  SpecSection <|.. StandaloneACSection
  SpecSection <|.. TestsSection
  SpecSection <|.. QuestionsSection
  SpecSection <|.. FeedbackSection
  SpecSection <|.. PlanSection

  UseCaseSection *-- UseCaseTitle : title
  UseCaseSection o-- ScopePreconditions : 1
  UseCaseSection o-- Trigger : 1
  UseCaseSection o-- MainFlow : 1
  UseCaseSection o-- PostConditions : 1
  UseCaseSection o-- MermaidDiagram : 1..*
  UseCaseSection o-- Narrative : narratives
  UseCaseSection o-- AcceptanceCluster : acceptance
  UseCaseSection o-- QuestionThread : questions

  StandaloneACSection o-- AcceptanceCriterion : criteria
  StandaloneACSection o-- MermaidDiagram : optional
  StandaloneACSection o-- QuestionThread : threads

  AcceptanceCluster o-- AcceptanceCriterion : criteria
  AcceptanceCluster o-- MermaidDiagram : optional
  AcceptanceCluster o-- QuestionThread : threads

  QuestionThread o-- Question : 1
  QuestionThread o-- Answer : 0..*

  TestsSection o-- TestCase : cases
  TestsSection o-- MermaidDiagram : optional
  QuestionsSection o-- Question
  QuestionsSection o-- Answer
  FeedbackSection o-- FeedbackItem : items
  PlanSection o-- Phase : phases
  Phase o-- PlanTask : tasks

  note for SpectrSpecification "One document = one aggregate; SpecificationBody.sid identifies the root."
  note for SpecSection "Composite: polymorphic body block; order matters."
  note for AcceptanceCluster "Composite: AC block under a use case or at body level (nested vs body div)."
  note for QuestionThread "Composite: Q followed by related A elements in document order."
```

**How this lines up with the implementation diagram:** `SpectrDocument` / `SpecificationBody` realize **SpectrSpecification**; `DocumentHead` / `DocumentTitle` → **SpecHeader**; `ChangeSetTitle` + `ChangeSetOverview` → **SpecOverview**; each major body block model (`UseCaseSection`, `SpecificationAcceptanceCriteria`, …) → a **SpecSection** specialization; under **UseCaseSection**, `ScopePreconditions` / `UseCaseTrigger` / `UseCaseMainFlow` / `UseCasePostConditions` are mandatory `<p type="…">` in that order, followed by one or more `MermaidDiagram` (`<p type="mermaid">`) with at least one `diagram="use-case"`; `MermaidDiagram` may also appear under `UseCaseAcceptanceCriteria`, `SpecificationAcceptanceCriteria`, and `TestSuiteSection`; nested vs body-level acceptance blocks → **AcceptanceCluster** vs **StandaloneACSection**; `ThreadedQuestions` / `SpecificationQuestions` → **QuestionThread** nesting or top-level **QuestionsSection**; `PlanPhase` / `PlanTask` → **Phase** / **PlanTask**.

### Use-case structure (XML) — mandatory order

Inside `<div type="use-case">`, after `<h3>`, this order is **required** (each `<p>` needs a unique `id`):

1. `<p type="scope-preconditions">`
2. `<p type="trigger">`
3. `<p type="main-flow">`
4. `<p type="post-conditions">`
5. One or more `<p type="mermaid" diagram="…">` — **at least one** must have `diagram="use-case"` (Mermaid **use case diagram** source in the element body; e.g. `useCaseDiagram` …).
6. Optional narrative `<p id="…">` (no `type`, or a narrative-only `type` not reserved elsewhere).
7. Optional nested `<div type="acceptance-criteria">` and/or `<div type="questions">` (acceptance-criteria before questions).

Additional `<p type="mermaid">` blocks may use other `diagram` values (e.g. sequence, class) when you attach diagrams under acceptance-criteria or tests sections.

| Kind | `type` / attributes |
|------|----------------------|
| Scope & preconditions | `type="scope-preconditions"` |
| Trigger | `type="trigger"` |
| Main flow | `type="main-flow"` |
| Post conditions | `type="post-conditions"` |
| Mermaid (reusable) | `type="mermaid"`, optional `diagram="use-case"` \| … |

**CLI:** `spectr uc update --id <h3-or-uc-dom-id> --sid <uc-sid> …` accepts `--pre`, `--trigger`, `--flow`, and `--post` (HTML-capable text, same as `--desc`), plus existing `--title` / `--desc`. Example:

```bash
spectr uc update --sid uc-22222222 \
  --pre "Actor is logged in; appointment service available." \
  --trigger "User chooses Book from the home screen." \
  --flow "<ol><li>System shows slots</li><li>User confirms</li></ol>" \
  --post "Appointment row exists with status pending."
```
