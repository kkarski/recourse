# Candidate Providers Business Specification

**Scope:** This document defines behavior for **verification campaigns** only: candidate providers, ownership (`spgid`), honor/reuse, verification landing and invites, and verification analytics. It
does **not** define **survey** campaigns, survey invites, or survey completion UX (see **Out of scope** and **Related specs**).

**Terminology:** Unless explicitly cross-referencing survey product specs, the term **“campaign”** in this document means **verification campaign** (identified by `cmp` / `cgid` in this model).

## Problem statement

Within **verification campaigns**, customers need to source candidates from multiple providers while preserving ownership attribution and reducing verification friction through controlled verification
reuse.

## Business goals

- Preserve candidate ownership provenance for every invite/session.
- Allow controlled reuse of prior verifications to reduce candidate drop-off.
- Maintain auditable verification and ownership behavior.
- Give customer operations users a **verification-campaign-level** read-only view of verification performance.

## Product decisions (stakeholder alignment)

The following decisions refine scope and user-visible behavior; they align with `specs/sample_providers/questions.md` (Clarifications, 2026-04).

- **Post-verification handoff:** After fresh verification or honor, the candidate leaves Taxiway’s verification journey via the invite’s **`return_url`** (defaulting to the **campaign–provider
  assignment’s** completed or qc outcome link per mandatory-DS routing unless overridden per invite). **No additional Taxiway-hosted step is required** in this specification; destinations after
  `return_url` are outside this document (e.g. partner or client-hosted experiences—**not** specified here).
- **Issued invite links:** **Newly generated** invite links **must** include **`cgid`** as a core campaign identifier (not only an internal campaign code visible elsewhere).
- **Landing without `spgid`:** Resolve ownership to the customer’s **default** candidate provider **`spgid`** (the customer **as their own** default provider).
- **Provider catalog scope:** Each customer has exactly two kinds of candidate providers: (i) a non-removable **default** candidate provider (the customer as their own provider; **display name** is
  customer-editable at the provider record; **outcome links are not** stored on the provider record—see **Campaign–provider assignment**), and (ii) zero or more **custom** candidate providers the
  customer adds. There is no system-wide / globally managed candidate provider in this initiative (see questions.md, Round 8 / D48).
- **Default provider provisioning:** The default candidate provider is **provisioned when the customer’s first verification campaign is created** and is **reused** for all subsequent verification
  campaigns; it is not required to exist before that moment.
- **Default provider auto-assignment:** Every verification campaign **automatically carries a default-provider assignment**, created at campaign-create time. The customer ops user **must supply
  completed and qc outcome links** for that assignment as part of campaign-create input (security and over-quota are optional). The default-provider assignment **cannot be removed** from a
  verification campaign for the campaign’s lifetime; the default provider itself **cannot be hard-deleted or soft-deleted** at the catalog level (AC22, AC64).
- **Outcome links per campaign:** Completed, qc, security, and over-quota outcome links are configured on the **campaign–provider assignment** (the relationship between a candidate provider and a
  verification campaign), not on the shared provider catalog row. The same catalog provider may be assigned to multiple verification campaigns with **different** link sets per assignment. **Verified
  candidate pools** remain keyed by `(spgid, cmp)`—one pool per provider **per verification campaign** that uses that provider.
- **Verification honor cookie (reuse):** Intended for **first-party Taxiway** use only; partners do not rely on this cookie—only on **`return_url`** for continuation.
- **Return visit — “data source completion”:** Judged against **historical** verification reality (sources completed **at the time of that verification** for this invite/session), not by re-evaluating
  against the **verification campaign’s current** data-source list if that list changes later.
- **Read-only verification campaign card:** Metrics and charts are expected to be **near real-time** from the operations user’s perspective (seconds to a short delay is acceptable; no day-level
  batch-only requirement).
- **Existing data:** **Invite** and **session** records that predate mandatory **`spgid`** must be **backfilled** to the customer’s **default** candidate provider **`spgid`** (same semantics as
  “customer as own default provider”), so analytics and filters remain consistent.
- **Mandatory data sources:** A **verification campaign** may declare a `mandatory_data_sources` subset of its `data_sources` list. A candidate is considered fully `Verified` only when every
  mandatory entry has been authorized (or the list is empty and ≥ 1 source is authorized). Mandatory satisfaction governs which **assignment** outcome link is used as the default `return_url`
  (completed vs qc), the honor coverage check, and the analytics `Verified` count. A per-invite `return_url` override (AC52) still wins over this default routing.

## Actors

- Customer operations user (configures verification campaigns and providers, views read-only analytics)
- Candidate (lands, verifies, and continues via `return_url`)

## Actor definitions

- Customer operations user
    - Owns customer-scoped candidate provider setup and campaign assignment decisions.
    - Configures verification campaign honor mode/freshness in edit mode.
    - Uses read-only verification campaign card analytics and invitee quick-navigation actions.
- Candidate
    - Enters via invite landing URL.
    - Either completes fresh verification or is honored from eligible same-campaign prior verification.
    - After verification decision, continues to the destination implied by **`return_url`** (see Product decisions).

## In scope

- Provider ownership model (default + custom providers, all customer-managed)
- Customer-level candidate provider catalog (identity, display name, soft delete, list/get) and editing **subject to campaign editability and concurrency rules**
- **Campaign–provider assignment** from customer-managed providers, including **per-assignment** outcome links (completed, qc, security, over-quota) and `{{param}}` templating
- Campaign page quick-add modal for creating new candidate providers **and** their first assignment links
- Read-only verification campaign card visibility of configured verification options
- Read-only verification campaign card per-provider row metrics (`Ver%`, `Try%`, `Err/Req%`, `Invited`)
- Read-only verification campaign card aggregate pie charts by data source (`Total Verified Invites`, `Success Verification %`, `Attempted Verification %`, `Failed/Requested Verification %`)
- Read-only verification campaign card quick navigation to invitee list filtered by **verification campaign** (`cmp`)
- Per-provider row quick navigation to invitee list filtered by **verification campaign** + candidate provider
- **Assignment-level** configuration for outcome links (completed and qc required per assignment; security, over-quota optional)
- Link templating with `{{param}}` placeholders on assignment outcome URLs
- Landing attribution via `cgid` and `spgid`
- Landing context capture and forwarding of dynamic query parameters
- Verification honor modes and freshness window
- Campaign-level `mandatory_data_sources` configuration and outcome-link routing (completed vs qc) by mandatory satisfaction
- Partial verification receipts (audit-only, never honor-eligible)
- Mandatory-DS lock under honor mode (no new mandatory entries once a campaign has fully-verified records and honor is enabled)
- Cookie + DB cross-check honor flow
- Verified candidate pool ownership semantics
- Return visit handling when landing repeats the same `cgid`, `ref_id`, and `spgid` as an existing invite
- Migration of legacy invites/sessions to mandatory **`spgid`** (default-provider attribution)

## Out of scope (this version)

- Collision mitigation logic for identifier hashes
- App-level query-param size/length governance
- Finalized UI copy/content design polish
- Risk-score-based gating of honor decisions (risk score is captured for audit only, not used to gate honor)
- Provider lifecycle details beyond catalog soft delete, assignment presence, and verification campaign **draft / active / paused / archived** editability
- Role-based gating of analytics beyond existing campaign OAuth scope
- Time-window selection for analytics (all metrics are cumulative all-time for the **verification campaign**)
- Fine-grained outcome-link routing for **security** and **over-quota** destinations (default end-of-flow routing for `return_url` without per-invite override uses **completed** vs **qc** from the
  **assignment** per AC54; when security/over-quota links are selected is out of scope for this document except that they are stored on the assignment for future use).
- Honoring of already-honored verifications (honoring is single-level only; chained honoring is not supported)
- Cross-campaign honoring of prior verifications. Honor mode is restricted to the same verification campaign that originally issued the verification; verifications from other verification campaigns
  cannot be honored.
- **Survey campaigns, survey invites, and survey completion UX** as defined in survey product specs (this spec governs verification + candidate-provider behavior and **`return_url`** handoff only).
- A detailed deprecation calendar for **legacy invite links** that omit **`cgid`** (compatibility may be required for a transition period; exact policy is a delivery coordination matter).
- **Restoration / undelete** of a soft-deleted custom candidate provider by the customer (out of scope this version; if needed it is a support / ops action).

## Preconditions

- Customer exists. **First verification campaign creation** for that customer **provisions** the non-removable default candidate provider if it does not yet exist; subsequent campaigns reuse it (see
  Product decisions).
- Verification campaign exists and resolves via `cgid` to a valid `(customer_id, cmp)` context.
- Candidate provider entities referenced by `spgid` belong to the same customer as the **verification campaign**.
- Invite creation inputs include required core identifiers (`cgid`, `ref_id`) and optional `spgid`, plus any non-core context keys.
- Verification service key is configured for cookie encryption/decryption.
- Where **`spgid`** is introduced on stored invites/sessions, legacy rows have been **backfilled** to the customer’s default candidate provider **`spgid`** when required for consistent ownership and
  reporting.

## Postconditions

- Every created invite/session has exactly one ownership reference `spgid`.
- Verification decision is deterministic for each landing attempt:
    - honored (same-campaign, fresh, DB-valid), or
    - routed to fresh verification.
- When verification completes (fresh or honored), the candidate is handed off through the invite **`return_url`** (see Product decisions).
- Read-only verification campaign card reflects cumulative **verification campaign** analytics and provider-row metrics per current business rules (**near real-time** expectation; see Product
  decisions).
- Invitees quick-navigation actions pre-set invitees page filters with `cmp` and optional `spgid`.

## Overall flow

1. Candidate lands using **verification campaign** link (required `cgid`, `ref_id`; optional `spgid`; optional context params).
2. Platform resolves **verification campaign** / customer context from `cgid`.
3. Platform resolves ownership `spgid`:
    - use provided valid `spgid`, else use default provider when absent,
    - reject with `400` when provided `spgid` is invalid for the customer.
4. Platform captures non-core query params as invite context.
5. Platform resolves invite identity (`sgid`) from `(customer_id, cmp, ref_id)`:
    - **First visit:** create invite/session records as needed.
    - **Return visit:** same resolved `(cgid, ref_id, spgid)` as an existing invite — no duplicate invite row; apply return-visit routing:
        - eligible verification cookie present → continue to honor evaluation (step 6),
        - no cookie and no data-source completions on record for this invite/session → proceed with verification as normal (step 7),
        - no cookie but data-source completion exists → show error and log (no further verification attempt).
6. Honor evaluation executes when honor-eligible cookie may apply (`same campaign only` mode):
    - enumerate cookies, filter to same customer and same `cmp`,
    - drop expired records by campaign freshness,
    - DB cross-check survivors,
    - honor most-recent eligible record if any.
7. If not honored (or mode is `always verify new`), candidate completes fresh verification when routing permits.
8. Verification result persists and cookie is issued when verification completes successfully (first-party reuse per Product decisions).
9. Candidate continues via verification invite **`return_url`**.
10. Read-only verification campaign card surfaces provider-row metrics and aggregate analytics.
11. User may navigate to invitees page from **verification-campaign-level** or provider-level quick actions.

## Use cases

### UC1 - Configure candidate providers for a verification campaign

- Primary actor: Customer operations user
- Trigger: User enters **verification campaign** edit mode to add/manage providers **and** assignment outcome links.
- Preconditions:
    - **Verification campaign** exists and belongs to user's customer scope.
  - **Verification campaign** is **not archived** (draft, active, or paused — edits allowed; archived campaigns reject mutations).
  - Candidate provider catalog is available for that customer (including default provider after first campaign provisioning).
- Main success scenario:
  1. User selects existing candidate provider or creates a new one (display name unique per customer — AC60).
  2. User configures or edits **per-assignment** outcome links (completed, qc required; security and over-quota optional) for this verification campaign.
  3. System validates required fields, assignment uniqueness, URLs (AC32a), and optimistic concurrency (AC61) where applicable.
  4. System saves assignment to the **verification campaign**.
- Postconditions:
  - **Verification campaign** has updated provider assignment set **each with its own link set for `(spgid, cmp)`**.
    - Each assigned provider appears in read-only card provider rows.
- Related ACs: AC30, AC33, AC36, AC36a, AC37, AC60–AC63.

### UC2 - Candidate lands and ownership attribution is established

- Primary actor: Candidate
- Trigger: Candidate opens invite landing URL.
- Preconditions:
    - URL includes valid `cgid` and non-empty `ref_id`.
    - If `spgid` present, it must belong to same resolved customer.
- Main success scenario:
    1. System resolves `(customer_id, cmp)` from `cgid`.
    2. System assigns ownership using provided valid `spgid` or default provider.
    3. System persists or resolves invite/session with exactly one `spgid`.
- Alternate scenarios:
    - Invalid provided `spgid` -> reject request with `400` and no invite creation.
    - Return visit (same `cgid`, `ref_id`, `spgid` as existing invite): no duplicate invite identity; route per cookie, data-source completion state, and honor mode (see Landing and return visits).
    - Return visit with mismatched `spgid` vs stored invite ownership -> reject with `400`.
- Postconditions:
    - Ownership attribution is auditable for the candidate journey.
- Related ACs: AC1, AC2, AC3, AC4, AC4a, AC5, AC6, AC20.

### UC3 - Reuse same-campaign verification when eligible

- Primary actor: Candidate
- Trigger: Candidate with prior verification lands on a **verification campaign** entry point.
- Preconditions:
    - Honor mode is `same campaign only`.
    - Prior verification belongs to same customer and same `cmp`.
- Main success scenario:
    1. System evaluates cookies and DB records per honor order.
    2. If eligible record(s) exist, system honors most recent one.
    3. System records honored verification invite linked to root `sgid`.
- Alternate scenario:
    - No eligible same-campaign record -> route to fresh verification.
- Postconditions:
    - Candidate either bypasses fresh verification or completes fresh verification.
- Related ACs: AC8, AC9, AC12, AC14, AC15, AC16, AC17, AC17a, AC26.

### UC4 - View verification campaign read-only analytics and drill into invitees

- Primary actor: Customer operations user
- Trigger: User views verification campaign card outside edit mode.
- Preconditions:
    - User has campaign OAuth scope.
    - Campaign has provider assignments (and optionally verified records).
- Main success scenario:
    1. System renders read-only verification settings.
    2. System renders provider-row metrics for all assigned providers.
    3. If verified candidates exist, system renders aggregate pie charts.
    4. User clicks **verification-campaign-level** or provider-level `View Invitees`.
    5. System navigates to invites page with pre-set filters.
- Postconditions:
    - User can inspect **verification-campaign** / provider-scoped invite cohorts without manual filter setup.
- Related ACs: AC34, AC39–AC50.

### UC5 - Manage candidate-provider catalog (customer scope)

- Primary actor: Customer operations user
- Trigger: User opens the customer-scoped candidate-provider catalog and creates, edits display name, **lists or gets** providers, or **soft-deletes** a provider (outside any specific verification
  campaign where catalog-only actions apply).
- Preconditions:
  - Default candidate provider exists once the customer has at least one verification campaign (see Product decisions).
- Main success scenario:
  1. User creates a **custom** candidate provider with required field **display name** (unique per customer — AC60); outcome links are **not** stored on the catalog row.
  2. System validates **unique display name**, persists the provider with optimistic concurrency (AC61), and exposes list/get per UC11.
- Alternate scenarios:
  - Edit existing provider's **display name** only at catalog level; outcome links are edited per verification campaign on the **assignment** (UC1).
  - **Hard delete:** rejected when the provider has **linked candidates** (any invite/session/historical verification tied to that provider); only **soft delete** is allowed in that case (AC65).
  - **Soft delete:** allowed only when **every** campaign–provider assignment for that provider is on an **archived** verification campaign. If any assignment is on a draft/active/paused campaign,
    soft delete is rejected with a deterministic message (the user must archive the campaigns first). After soft delete, the provider and its linked candidates are filtered from operational
    default views (catalog list, invitees default list, campaign card row); historical pool queryability per AC25 is preserved for explicit archive-time queries. Restoration is out of scope.
  - Attempt to remove or hard-delete default provider: rejected per AC22; default provider remains.
- Postconditions:
  - Catalog reflects user changes; provider is selectable for campaign assignment in UC1 / UC7 **when not soft-deleted** and when campaigns allow edits.
- Related ACs: AC22, AC31, AC60, AC61, AC65, AC66, UC11.

### UC6 - Edit default provider catalog identity

- Primary actor: Customer operations user
- Trigger: User opens default provider configuration to update **display name** (catalog-level).
- Preconditions:
  - Default provider exists for the customer (provisioned on first verification campaign — Product decisions).
- Main success scenario:
  1. User edits display name.
  2. System validates uniqueness (AC60), applies optimistic concurrency (AC61), and persists; default provider remains non-removable.
- Alternate scenarios:
  - User attempts to remove, hard-delete, or soft-delete the default provider in a way that removes ownership: rejected (AC22).
- Postconditions:
  - Default provider **display name** reflects the user's edits; **`spgid` and ownership semantics for existing invites are unchanged**. Outcome links for each verification campaign remain on that
    campaign’s assignment to this provider.
- Related ACs: AC22, AC38, AC50, AC60, AC61.

### UC11 - List and get candidate providers

- Primary actor: Customer operations user
- Trigger: User or client loads the candidate-provider catalog list, or requests a single provider by identifier.
- Preconditions:
  - User is scoped to a customer with permission to read providers.
- Main success scenario:
  1. User requests **list** of candidate providers for the customer (optionally excluding soft-deleted rows per API contract).
  2. User requests **get** for one provider by id.
  3. System returns provider records including **display name**, identifiers, **version** for concurrency (AC61), soft-delete state, and **does not** embed campaign-specific outcome links (those
     live on assignments).
- Alternate scenarios:
  - Provider not found or wrong customer: request rejected with `404` or `403` per API standards.
- Postconditions:
  - Caller can drive UI and optimistic-update flows using returned **version**.
- Related ACs: AC61, AC66 (list/get contract).

### UC7 - Quick-add candidate provider from verification campaign page

- Primary actor: Customer operations user
- Trigger: From the verification campaign page (in edit mode), user opens the "new candidate provider" modal to create catalog identity **and** the **campaign–provider assignment** (including outcome
  links) in one flow.
- Preconditions:
    - User is in verification campaign edit mode for a campaign in their customer scope.
  - **Verification campaign** is **not archived** (AC62).
- Main success scenario:
  1. User fills required catalog field (**display name**, unique per AC60) and required **assignment** fields (completed link, qc link) and optional assignment fields (security, over-quota links).
  2. System validates required fields, URL rules (AC32a), uniqueness (AC60), and concurrency (AC61).
  3. System creates the candidate provider in the customer catalog and creates the assignment to the current campaign **with that assignment’s link set** in a single transactional action.
- Alternate scenarios:
    - Validation fails on save: provider is not created and no campaign assignment is made.
    - Provider assignment would duplicate an existing one for the campaign: blocked per AC33.
- Postconditions:
  - New provider exists in customer catalog and **one assignment** exists for the current campaign with its own outcome links.
- Related ACs: AC31, AC32a, AC33, AC60, AC61, AC62.

### UC8 - Remove candidate provider from a verification campaign

- Primary actor: Customer operations user
- Trigger: User attempts to remove a candidate provider **assignment** from a verification campaign in edit mode (remove provider from this campaign).
- Preconditions:
    - Provider is currently assigned to the campaign.
  - **Verification campaign** is **not archived** (AC62).
- Main success scenario:
  1. System checks whether any invites for `(spgid, cmp)` are still in **non-terminal** state (see Definitions — **Invite terminal state**).
  2. If none, system removes the **assignment** (and its assignment-level outcome links for this campaign).
- Alternate scenarios:
  - **Non-terminal** invites exist: removal is blocked with a deterministic message; assignment is preserved (AC51).
- Postconditions:
    - Campaign provider list reflects the removal (when allowed); historical metrics for prior `(spgid, cmp)` activity remain queryable per AC25.
- Related ACs: AC51, AC25, AC62.

### UC9 - Return visit routing

- Primary actor: Candidate
- Trigger: Candidate lands on a verification campaign URL with the same `(cgid, ref_id, spgid)` that already resolves to an existing invite (per UC2).
- Preconditions:
    - An invite/session already exists for resolved `(customer_id, cmp, ref_id)` with stored `spgid` matching the current resolution.
- Main success scenario:
    1. System recognizes the request as a return visit and resolves the same `sgid` (no duplicate invite identity created).
    2. System inspects available verification cookies and authoritative completion records for this invite/session.
    3. System routes per the three branches below.
- Branches:
    - **Eligible cookie present:** continue into honor evaluation per UC3 honor rules (AC7c).
    - **No eligible cookie, no historical data-source completion:** proceed with fresh verification as in a normal in-flow candidate (AC7b).
    - **No eligible cookie, historical data-source completion exists:** block another verification attempt; show user-facing error and emit observability log entry with reason code per Observability
      section (AC7d).
- Alternate scenarios:
    - Stored ownership `spgid` does not match resolved `spgid` for the current landing: reject with `400 Bad Request` (AC7a).
- Postconditions:
    - At most one outcome occurs (honor / fresh verify / blocked) and is observable per Observability rules.
- Related ACs: AC7, AC7a, AC7b, AC7c, AC7d.

### UC10 - Fresh verification completion and `return_url` handoff

- Primary actor: Candidate (with system-side persistence and cookie issuance)
- Trigger: Candidate completes the fresh verification flow successfully (entered from UC2 first visit, UC3 honor-not-eligible path, UC9 return-visit-no-completion path, or under `always verify new`
  mode).
- Preconditions:
    - Verification flow has produced an authoritative successful result for at least one configured data source.
- Main success scenario:
    1. System persists the verification result, including risk score for audit.
  2. System issues one encrypted verification cookie with required payload fields and TTL equal to issuing campaign freshness window (AC13). When `mandatory_data_sources` is non-empty and the
     candidate's authorizations do not cover every entry, the receipt is marked **partial** and is not honor-eligible (AC55) until upgraded.
  3. System hands the candidate off via the invite's `return_url`. With no per-invite override, the platform applies the mandatory-DS routing rule (AC54): this **`(spgid, cmp)` assignment’s** *
     *completed**
     link when the candidate is `Verified`, that assignment’s **qc** link when `PartiallyVerified`. With a per-invite override, the override always wins (AC52).
- Alternate scenarios:
  - Honor mode is `always verify new`: cookie is still issued (AC11); honor evaluation is suppressed for future landings on this campaign per AC10. Receipts may still be marked `partial` per AC55.
  - Per-invite `return_url` override is set: override value is used in step 3 regardless of mandatory satisfaction (AC52).
  - Same-campaign honor cookie does not cover the current mandatory list in full: cookie is disqualified entirely (AC56); candidate completes fresh verification of all mandatory entries.
- Postconditions:
    - Candidate is no longer inside Taxiway's verification UI; downstream destination behavior is out of scope (Product decisions).
  - Verified candidate pool `(spgid, cmp)` reflects this candidate only when the candidate is `Verified` per the Definitions; `PartiallyVerified` candidates do not contribute to `Verified` counts.
- Related ACs: AC10, AC11, AC13, AC18, AC52, AC54, AC55, AC56.

### UC12 - Backfill legacy invites/sessions to default `spgid`

- Primary actor: Platform operator (executing one-time data migration; not a customer-facing actor in this initiative)
- Trigger: Migration is run to enforce mandatory `spgid` on existing invite and session rows that predate this model.
- Preconditions:
  - Customer's default candidate provider is provisioned **when needed** (first verification campaign or legacy migration — so a stable default `spgid` exists for backfill).
- Main success scenario:
    1. System identifies invite/session rows for the customer where `spgid` is absent.
    2. System assigns `spgid` = customer's default candidate provider `spgid` ("customer as own default provider") to each such row.
    3. System verifies post-condition that **every** invite/session for the customer now carries exactly one `spgid` (AC20).
- Alternate scenarios:
    - Row already has a non-default `spgid`: row is skipped (no overwrite).
    - Row references a customer without a provisioned default provider: migration halts for that customer with a deterministic error (operational follow-up required).
- Postconditions:
    - Analytics, invitees filters, and ownership semantics behave consistently for legacy rows; no orphan rows remain without `spgid`.
- Related ACs: AC20, AC53; Product decisions (Existing data backfill).

## Actors and roles

- Visibility of read-only verification campaign card analytics (pie charts and per-provider row metrics) follows the existing **verification-relevant** campaign OAuth scope; no additional role gating
  is introduced by this spec.

## Business rules

### Provider model

- Each customer has a non-removable default provider (the customer **as their own** candidate provider for ownership purposes; **provisioned on first verification campaign creation** and reused;
  see Product decisions for backfill). The default provider **cannot be hard-deleted, soft-deleted, or unassigned** from any verification campaign that uses it (AC22).
- The default candidate provider is **always assigned** to every verification campaign for that customer. Its assignment is created at campaign-create time with required **completed** and **qc**
  links supplied by the user (validated per AC32a) and **cannot be removed** while the campaign exists (AC22, AC64).
- Each candidate provider has a unique identifier (`candidate_provider_id`) and stable ownership key **`spgid`** per customer.
- The customer's candidate provider catalog consists of (i) the non-removable **default** provider and (ii) zero or more **custom** providers added by the customer. There is no system-wide /
  globally managed candidate provider in this initiative (see questions.md, Round 8 / D48).
- **Catalog-level fields** for every candidate provider: **display name** (required; **unique among all candidate providers for that customer** after trim; case-insensitive comparison — AC60),
  soft-delete
  metadata when applicable, and **optimistic concurrency version** (AC61). **Outcome links are not stored on the catalog row.**
- Candidate providers are created and managed at customer scope, then **assigned** to **verification campaigns**. Each **assignment** (campaign–provider relationship) stores **completed**, **qc**
  (required), **security**, and **over-quota** (optional) outcome links for **that verification campaign only**. The same `spgid` reused across campaigns has **independent** link sets and *
  *independent**
  verified candidate pools `(spgid, cmp)`.
- **Verification campaign** assignment must only allow selecting providers that belong to the same customer and are not excluded by soft-delete rules for new assignment UIs.
- A candidate provider can be assigned at most once per **verification campaign** (unique `(verification campaign, spgid)` assignment).
- **Deletion (custom providers).** Custom (non-default) candidate providers **cannot be hard-deleted** while they have **linked candidates** (any persisted invite/session or verification history
  referencing that provider). **Soft delete** is permitted only when **all** of the provider’s campaign–provider assignments are on **archived** verification campaigns (AC65). After soft delete, the
  provider and its linked candidates are filtered from operational default views (catalog list, invitees default list, campaign card), while AC25 historical pool queryability is preserved for
  explicit archive-time queries. **Restoration / undelete** of a soft-deleted provider by the customer is **out of scope** in this version.
- **Deletion (default provider).** The default provider is **never deletable** at the catalog level and its assignment is **never removable** from any campaign (AC22). **Linked candidates** and
  **non-terminal invites** are defined in Definitions.
- An invite's `return_url` defaults per mandatory-DS routing to the **assignment’s** completed or qc link for `(spgid, cmp)`, with per-invite override permitted (AC52, AC54).

### Verification campaign editability

- Mutations to **verification campaign** configuration that affect providers, assignments, honor mode, freshness, or data sources are **allowed** when the campaign is **draft**, **active**, or *
  *paused**.
- The same mutation set is **not allowed** when the verification campaign is **archived** (read-only for operations users except where separately specified for analytics navigation — AC62).

### Concurrency (optimistic locking)

- Persisted candidate-provider catalog rows and campaign–provider assignment rows carry a **version** (or equivalent) for **optimistic locking** at the persistence (DAO) layer. Updates **reject** when
  the
  client-provided version does not match the stored row (**conflict** — AC61).

### Landing and return visits

- A landing that resolves to an existing invite with the same `(cgid, ref_id, spgid)` attribution is a **return visit** — not a duplicate-invite error.
- On return visit, invite identification remains `sgid` derived from `(customer_id, cmp, ref_id)`; no second invite identity is created for the same tuple.
- Return visit verification routing:
    - If the candidate has an eligible successful verification cookie for honor evaluation, follow verification campaign honor rules (`same campaign only` / `always verify new`) as elsewhere in this
      spec.
    - If the candidate has **no** eligible successful verification cookie **and** the platform has **no** recorded successful completion for this invite/session **under the historical data-source
      completion rule** (see Definitions), proceed with verification as for a normal in-flow candidate.
    - If the candidate has **no** eligible successful verification cookie **and** the platform **does** record such completion **under the historical rule**, the candidate must not be sent through
      another verification attempt: show a user-facing error that verification cannot be completed at this time, and record a diagnostic application log entry (see Observability).
- **Ownership match for return visit:** `cgid`, `ref_id`, and resolved `spgid` must match the stored invite’s ownership. If the original invite used default provider attribution (no `spgid` in the
  landing URL), resolve default `spgid` for the current landing the same way and compare to stored ownership. If `cgid` and `ref_id` match an existing invite but resolved `spgid` does not match stored
  attribution, reject with `400 Bad Request`.

### Verification configuration

- Verification campaign owns honor mode and freshness window (`X days`).
- Honor verification mode configuration is editable only in **verification campaign** edit mode **and** only when the campaign is **not archived** (AC62).
- Honor verification modes are mutually exclusive; exactly one of the canonical set is selected at a time.
- Canonical honor mode set: `same campaign only`, `always verify new`. (Cross-campaign honoring is out of scope this version.)
- Freshness window is only active for `same campaign only`; freshness window is inactive for `always verify new`.
- Honor evaluation never considers verification records issued by a different verification campaign, regardless of customer or risk.
- Risk score is computed and persisted (cookie + DB) for audit, but does not gate honor decisions.
- Honoring is single-level only: only fresh (non-honored) verifications are eligible to be honored. A previously-honored record cannot itself be honored; the candidate must complete fresh verification
  in that case.
- A **verification campaign** carries a `mandatory_data_sources` list — a strict subset of `data_sources` whose successful authorization is required for a candidate to be considered fully
  verified. Configuring `mandatory_data_sources` is editable only in **verification campaign** edit mode **and** when the campaign is **not archived** (AC62). The list may be empty (all data sources
  optional, reproducing today's behavior).
  Duplicates are rejected at save time; removing a data source from `data_sources` cascades a removal from `mandatory_data_sources`.
- **Outcome-link routing under mandatory DS** (when an invite has no per-invite `return_url` override; AC52 unchanged): if the candidate is `Verified` per the Definitions, the invite's `return_url`
  defaults to this **`(spgid, cmp)` assignment’s** **completed** outcome link; if the candidate has authorized at least one data source but `mandatory_data_sources` is non-empty and unsatisfied
  (`PartiallyVerified`), the invite's `return_url` defaults to that assignment’s **qc** outcome link. (`min_authorizations_for_return` continues to govern when the in-flow return CTA becomes visible
  to
  the candidate; mandatory DS governs **which** link they are sent to.)
- **Partial verification receipts and upgrade-in-place.** When a fresh verification flow ends with the candidate `PartiallyVerified`, the platform records a `partial` verification receipt for
  audit and analytics. While the receipt remains in `partial` state it is **not honor-eligible**. The receipt **may be upgraded in place** to `Verified` (and honor-eligible) when the same candidate
  later returns to the **same invite/session (`sgid`)** and authorizes the entries currently missing against the campaign's **current** `mandatory_data_sources` list (AC55). Coverage is evaluated
  against the **current** mandatory list at upgrade time, so demotions or removals applied between issuance and upgrade may make an earlier-incomplete receipt eligible without further candidate
  action beyond the next authorization event on the same invite.
- **Honor coverage rule (all-or-nothing).** Honor evaluation requires the prior verification's authorized sources to cover the consuming campaign's **current** `mandatory_data_sources` list in
  full. A cookie whose underlying sources do not cover the current list is **disqualified entirely**, and the candidate is routed through fresh verification of every entry in the current
  mandatory list. There is no partial-honor / top-up flow.
- **Mandatory-DS lock under honor mode:** When honor mode is `same campaign only` **and** the verification campaign has at least one **fresh** fully-verified record (a fresh `Verified` record
  where the candidate authorized every entry of the **then-current** mandatory list, or the then-current mandatory list was empty and at least one data source was authorized; honored receipts
  and `partial` receipts that have not been upgraded do **not** trigger the lock on their own), the campaign's `mandatory_data_sources` list is **locked against additions**:
  - **Forbidden under lock:** adding a data source as mandatory — both adding a brand-new entry to `data_sources` as mandatory and promoting an existing optional entry to mandatory.
  - **Allowed under lock:** adding optional data sources, removing optional data sources, demoting `mandatory → optional`, and removing data sources entirely (whether previously optional or
    previously mandatory).
  - **Lock toggle:** the lock follows the current honor mode. Switching the campaign to `always verify new` unlocks mandatory additions while in that mode; switching back to `same campaign only`
    re-engages the lock if at least one fully-verified record exists at that moment. The lock is not a one-way ratchet.
  - **Rationale:** prevents silent invalidation of prior honor-eligible verifications, since honor evaluation requires the prior verification's authorized sources to cover the consuming
    campaign's *current* `mandatory_data_sources` list.

### Ownership and pools

- `spgid` defines provider ownership for each invite/session.
- Verified candidate pool membership is constrained by both `spgid` and `cmp` (pool key is `(spgid, cmp)`). Because outcome links are **per assignment**, operational tracking of “this provider on this
  campaign” is always scoped to `(spgid, cmp)`; sharing one catalog provider across campaigns yields **one pool per campaign** that uses that provider.
- Every invite and session must belong to exactly one `spgid` at creation time.
- A verified candidate pool remains open and queryable indefinitely; **verification campaign** closure does not remove a pool or stop it from being queryable.

### Read-only verification campaign card

- The read-only verification campaign card represents **only** a **verification campaign**. Survey campaigns are a different product area (out of scope).
- Aggregate analytics and per-provider row metrics are cumulative across the entire **verification campaign** lifetime; no time-window selector applies in this version.
- Updates to displayed metrics and charts are expected **near real-time** (see Product decisions).
- **Analytics slice set:** Aggregate pie charts slice by the **verification campaign’s current** configured data sources at read time (which slices appear in the UI). This is **independent** of the *
  *historical** rule used for **return-visit data source completion** (Definitions)—that historical rule exists only to decide blocked return visits, not to redefine analytics slices.

### Cross-spec ownership

- Survey invite/session/campaign lifecycle rules are maintained in `specs/survey_invites/survey_invites_business_spec.md`. **This** specification does not define survey behavior; it defines *
  *verification campaigns**, candidate providers, and **`return_url`** handoff after verification.

## Definitions

### Candidate states (used in metrics and ACs)

- `Invited`: a candidate has an invite under `(spgid, cmp)`.
- `Attempted`: an invited candidate started the verification flow (landed and began verification).
- `Verified`: an attempted candidate is treated as fully verified for the **verification campaign** when **either** (i) `mandatory_data_sources` is non-empty AND the candidate has authorized
  **every** entry in that list, **or** (ii) `mandatory_data_sources` is empty AND the candidate has authorized at least one data source. Authorization may come from fresh verification or from a
  same-campaign honored receipt that covers the entire current mandatory list. Honor and freshness rules still apply on top of this definition. There is no partial-honor / top-up flow: a cookie
  that does not cover the current mandatory list in full is disqualified entirely.
- `PartiallyVerified`: an attempted candidate has authorized at least one data source but `mandatory_data_sources` is non-empty AND not every entry has been authorized. Such a candidate is **not**
  counted as `Verified` in per-provider row metrics or aggregate pie charts; their outcome-link routing uses the **`(spgid, cmp)` assignment’s** qc link (AC54). A `partial` receipt (AC55) is
  recorded; while the receipt remains in `partial` state it is **not honor-eligible**. The receipt **may be upgraded in place to `Verified` / honor-eligible** if the same candidate later authorizes
  the missing mandatory entries on the **same invite/session (`sgid`)** per AC55.
- `Errored`: a candidate reached a terminal failure state during verification.
- `Requested`: a candidate received an invite but never reached a terminal state (verified, errored, or otherwise resolved).

### Invite terminal state (for assignment removal and related safeguards)

- **Terminal** invite/session (for a given verification journey): the invite has reached an outcome that **closes** the verification attempt for removal-policy purposes — specifically **`Verified`**,
  **`PartiallyVerified`**, or **`Errored`** per the Definitions above.
- **Non-terminal** invite/session: any invite that is **not** terminal — including but not limited to **`Requested`** (invite exists but no terminal verification outcome yet) and any in-progress state
  the
  product defines between landing and a terminal outcome.
- **UC8 / AC51** use **non-terminal** in this sense: **removing** a provider **assignment** from a campaign is **blocked** while **any** invite for `(spgid, cmp)` is still **non-terminal**.

### Linked candidates (for soft delete)

- A candidate provider has **linked candidates** if **any** persisted invite, session, verification receipt, or other durable candidate journey record references that provider such that **hard
  delete** would orphan or destroy required audit or ownership history. When linked candidates exist, **hard delete is forbidden** (AC65). **Soft delete** is permitted only when every assignment
  for that provider is on an **archived** campaign (AC65); after soft delete, the provider and its linked candidates are filtered from **operational default views** (catalog list, invitees default
  list, campaign card per-provider row) while remaining queryable per AC25 for explicit archive-time access.

### Per-provider row metrics

For each `(spgid, cmp)` row, denominator is `Invited`:

- `Ver%` = `Verified / Invited`.
- `Try%` = `Attempted / Invited`.
- `Err/Req%` = `(Errored + Requested) / Invited`.
- `Invited` = total number of invited candidates.

### Aggregate pie chart definitions

Aggregated across all verified candidate pools for the **verification campaign** `cmp`. **Slices** follow the **verification campaign’s current** configured data sources at read time (see Read-only
verification campaign card—analytics slice set). A candidate verified via multiple data sources contributes to each corresponding slice (subject to that slice set).

- `Total Verified Invites by Data Source`: count of verified candidates per data source.
- `Success Verification % by Data Source`: percent of verified candidates per data source.
- `Attempted Verification % by Data Source`: percent of attempted-verification candidates per data source.
- `Failed/Requested Verification % by Data Source`: percent of (errored + requested) candidates per data source.

### Data source

"Data source" is the OAuth/data integration used during verification (e.g., LinkedIn, Google, Booking). Multiple data sources per verified record are counted independently in aggregate slices.

### Data source completion (return visit routing)

For a given invite/session identity (`sgid`), **data source completion** means the platform has recorded a successful verification completion for at least one **relevant** data source for that
invite/session. **Relevant** sources are determined **historically**: they reflect what was true **when that verification completed**, not necessarily the verification campaign’s **current**
`data_sources` list if it was edited later. This is evaluated from authoritative platform records (not from browser cookie presence alone).

## Observability

- When return visit routing hits the blocked path (no eligible verification cookie but data source completion exists), the platform must write an **application log** entry at error or warning level
  that includes at minimum: `customer_id`, `cmp`, `cgid`, `ref_id`, `spgid`, `sgid`, and a stable reason code (e.g., `RETURN_VISIT_NO_COOKIE_DS_COMPLETED`), plus request correlation identifier
  sufficient for support diagnosis. The candidate-facing message must not expose internal identifiers beyond what product copy allows.

## Constraints

- `cgid` is derived as `xxhash(customer_id, cmp)` and must resolve to **verification campaign** / customer context.
- `sgid` is derived as `xxhash(customer_id, cmp, ref_id)` and is globally unique for invite/session identity.
- `spgid` is derived as `xxhash(customer_id, candidate_provider_id)` and is the ownership key.
- `ref_id` must be unique per `(customer_id, cmp)` for invite identity: repeat landings with the same tuple resolve to the same `sgid` (return visit), not a second invite row.
- **Newly issued** invite links include **`cgid`** as a core parameter (see Product decisions).
- Invitees page filter criteria includes campaign filter (`cmp`) and candidate provider ownership filter (`spgid`); URL parameter names are `cmp` and `spgid`.
- Landing link format for provider routing is `/invites/new?cgid={cgid}&ref_id={ref_id}&spgid={spgid}` plus optional context query parameters.
- Core landing keys are `cgid`, `spgid`, and `ref_id`; all other keys are treated as context keys.
- Invite creation must persist all non-core context keys and make them available for placeholder substitution.
- Placeholder substitution is server-side at redirect/handoff time and unresolved placeholders must be emitted as empty values.
- **Campaign–provider assignment** outcome link URLs must be syntactically valid and use the `https://` scheme. `http://`, relative paths, or otherwise malformed values are rejected at save time for
  those
  URLs. Placeholder tokens (e.g., `{{ref_id}}`) within the URL are permitted and are not URL-validated until rendering.
- Verification cookies are encrypted using a single global symmetric service key.
- Verification cookie payload includes `sgid`, `customer_id`, `cmp`, `ref_id`, verification timestamp, and computed risk score (audit only).
- Cookie TTL equals issuing verification campaign freshness window (`X days`).
- **Product constraint:** verification honor / reuse cookies are meaningful in **first-party Taxiway** contexts; continuation for external partners relies on **`return_url`**, not on those cookies (
  see Product decisions).
- Hash-collision handling is out of scope and treated as accepted risk.

## Acceptance criteria (BDD)

### AC1 - Default provider attribution

Given a candidate lands on `/invites/new` with valid `cgid`, non-empty `ref_id`, and no `spgid`  
When the platform creates invite and session records for the landing  
Then candidate ownership is attributed to the customer default provider `spgid`.

### AC2 - Campaign context resolution

Given a candidate lands with `cgid`  
When the invite flow starts  
Then the platform resolves `cgid` to the correct `(customer_id, cmp)` context before attribution or verification decisions.

### AC3 - Provider-specific attribution override

Given a candidate lands with valid `cgid` and valid `spgid`  
When invite records are created  
Then ownership attribution uses that `spgid` regardless of other query context.

### AC4 - Invalid spgid rejection

Given a candidate lands with valid `cgid` and an `spgid` that is unknown for the resolved customer  
When invite creation is attempted  
Then the platform rejects the request with `400 Bad Request` and does not create an invite or fall back to the default provider.

### AC4a - Missing ref_id rejection

Given a candidate lands with valid `cgid` but missing or empty `ref_id`  
When invite creation is attempted  
Then the platform rejects the request with `400 Bad Request` and does not create an invite.

### AC5 - Query context forwarding

Given landing URL contains non-core query parameters  
When verification invite context is created from invite landing  
Then non-core query parameters are forwarded unchanged to verification invite context.

### AC6 - Query context capture at invite create

Given a landing URL includes core and non-core query parameters  
When invite creation executes  
Then frontend/backend persist all non-core parameters as invite context for downstream link templating.

### AC7 - Return visit (same landing triple)

Given an existing invite for resolved `(customer_id, cmp, ref_id)` with stored ownership `spgid`  
When a candidate lands with the same `cgid`, `ref_id`, and `spgid` as that invite  
Then the platform treats the request as a return visit, resolves the same `sgid`, and does not create a second invite row for the same identity.

### AC7a - Return visit spgid mismatch

Given an existing invite for `(customer_id, cmp, ref_id)` with stored ownership `spgid`  
When a candidate lands with the same `cgid` and `ref_id` but a different `spgid` than stored for that invite  
Then the platform rejects the request with `400 Bad Request` and does not start or continue verification.

### AC7b - Return visit: no cookie, no data-source completion — verify as normal

Given a return visit per AC7  
And the candidate has no eligible successful verification cookie for honor evaluation  
And the platform has **no** recorded **data source completion** for this invite/session **per the Definitions (historical rule)**  
When verification routing is decided  
Then the platform proceeds with the standard verification flow as for a candidate who still needs to complete verification.

### AC7c - Return visit: eligible cookie — honor path

Given a return visit per AC7  
And the candidate has an eligible successful verification cookie per this spec’s honor rules  
When honor evaluation runs  
Then the platform follows the same honor mode and freshness rules as for a non-return visit (e.g. AC8–AC17 as applicable).

### AC7d - Return visit: no cookie but data-source completion — block and log

Given a return visit per AC7  
And the candidate has no eligible successful verification cookie for honor evaluation  
And the platform has recorded **data source completion** for this invite/session **per the Definitions (historical rule)**  
When the platform would otherwise route the candidate into verification  
Then the platform does not start another verification attempt, shows a user-facing error that the candidate cannot be verified at this time, and writes an application log entry per the Observability
section (including `customer_id`, `cmp`, `cgid`, `ref_id`, `spgid`, `sgid`, and correlation context).

### AC8 - Same-campaign honor mode

Given verification campaign honor mode is `same campaign only`  
And candidate has at least one reusable verification cookie tied to the same `cmp` and customer  
When cookie + DB checks pass for current `cmp` and customer  
Then candidate is honored and bypasses fresh verification.

### AC9 - Cross-campaign honor exclusion

Given a candidate has a prior verification cookie that originated from a different verification campaign (different `cmp`)  
When honor eligibility is evaluated for the **current verification campaign**  
Then the cross-campaign cookie is not eligible and the candidate is routed through fresh verification.

### AC10 - Always-verify mode

Given verification campaign honor mode is `always verify new`  
When candidate lands with valid prior verification cookies (including same-campaign cookies)  
Then candidate is routed through fresh verification and prior verifications are not honored.

### AC11 - Always-verify cookie issuance

Given verification campaign honor mode is `always verify new`  
And candidate completes fresh verification  
When verification result is persisted  
Then a fresh verification cookie is still issued per AC13 (always-verify mode does not suppress cookie issuance).

### AC12 - Expiration overrules honor

Given verification campaign honor mode is `same campaign only`  
And candidate has a same-campaign prior verification that would otherwise be honorable  
When freshness exceeds the verification campaign's configured `X days`  
Then prior verification is treated as expired and fresh verification is required.

### AC13 - Verification cookie issuance

Given a candidate completes verification  
When verification result is persisted  
Then the platform writes one encrypted verification cookie containing required payload fields (including risk score for audit) and campaign-based TTL.

### AC14 - DB-authoritative anti-tamper

Given a verification cookie is present  
When no matching DB verification record exists  
Then cookie is ignored and cannot authorize honor flow.

### AC15 - Honor evaluation order

Given verification campaign honor mode is `same campaign only` and multiple verification cookies are present  
When honor eligibility is evaluated  
Then evaluation follows this order: enumerate cookies, drop cookies for any other `cmp` or other customer, drop expired against the verification campaign's freshness window, DB cross-check the
remainder, then honor if at least one remains; if none remain, route to fresh verification.

### AC16 - Multi-cookie tie-break

Given more than one cookie survives all honor-eligibility filters and DB cross-checks  
When honor decision is finalized  
Then the cookie with the most recent verification timestamp is honored.

### AC17 - Auditable honored redirect

Given candidate is honored from a prior verification  
When processing continues after honor toward invite `return_url`  
Then platform records a new verification invite marked `honored` linked to original (root) `sgid`.

### AC17a - Single-level honoring

Given a candidate's only available prior verification records are themselves honored records (not fresh verifications)  
When honor eligibility is evaluated  
Then no record qualifies as honor-eligible and the candidate is routed through fresh verification.

### AC18 - Verification return control

Given a verification invite reaches completion (state `Verified` or `PartiallyVerified`)  
When post-verification routing executes  
Then verification invite `return_url` is used for candidate continuation: an explicit per-invite override always wins (AC52); otherwise the mandatory-DS routing rule (AC54) selects the *
*`(spgid, cmp)`
assignment’s** completed or qc outcome link based on whether mandatory data sources are satisfied.

### AC19 - Verified candidate pool grouping

Given verified invites/sessions exist for multiple providers  
When candidate pools are computed  
Then pool membership is grouped by shared `(spgid, cmp)` ownership key.

### AC20 - Mandatory ownership assignment

Given any verification invite/session is created  
When persistence occurs  
Then the record must include exactly one `spgid` ownership reference and creation fails if `spgid` is absent.

### AC21 - Default candidate pool guarantee

Given a verification campaign exists for the customer (so the default provider is provisioned — Product decisions)  
When verified candidate pools are evaluated  
Then at least one `(spgid, cmp)` pool exists for the customer default provider in that campaign context, with optional additional `(spgid, cmp)` pools from custom providers.

### AC22 - Default provider non-removability

Given a customer's default provider exists  
When a user attempts to **hard-delete** the default provider catalog row, **soft-delete** it, **or unassign** the default-provider assignment from any verification campaign that uses it  
Then the operation is **rejected** and the default provider remains both in the catalog and assigned to every verification campaign that has it.

### AC23 - Same-customer provider assignment enforcement

Given a candidate provider belongs to customer A  
When a user from customer B attempts to assign that provider to a campaign  
Then assignment is rejected and the provider is not added to customer B's campaign.

### AC25 - Verified pool indefinite queryability

Given a verification campaign has closed  
When verified candidate pools for that campaign are queried  
Then pool members remain queryable and read-only campaign card analytics continue to compute against the same data.

### AC26 - Risk score non-gating

Given verification campaign honor mode is `same campaign only`  
And a candidate has a same-campaign prior verification with any computed risk score (high or low)  
When honor eligibility is evaluated  
Then risk score does not affect the honor outcome; only honor mode, freshness, and DB cross-check determine the result.

### AC27 - Per-campaign assignment outcome links

Given a candidate provider is assigned to multiple **verification campaigns**  
When each assignment is configured  
Then **completed**, **qc**, **security**, and **over-quota** outcome links are stored **per `(verification campaign, spgid)` assignment** and may **differ** per campaign.  
When an invite is created for `(spgid, cmp)`  
Then default `return_url` routing without per-invite override uses **that assignment’s** links (AC54), not another campaign’s links for the same `spgid`.

### AC28 - Mandatory-DS lock blocks new mandatory under honor

Given a **verification campaign** has honor mode `same campaign only`  
And the campaign has at least one **fresh** fully-verified record per the Definitions (a fresh `Verified` record where the candidate authorized every entry of the **then-current** mandatory list,
or the then-current mandatory list was empty and ≥ 1 source was authorized; honored receipts and `partial` receipts that have not been upgraded **do not** trigger the lock on their own)  
When a customer operations user attempts to save a campaign update that adds any data source to `mandatory_data_sources` — either by adding a new entry to `data_sources` flagged as mandatory or by
promoting an existing optional entry to mandatory  
Then the platform rejects the save with `400 Bad Request` and a structured reason code `MANDATORY_LOCKED_HONOR_ENABLED`, and `mandatory_data_sources` is not modified.

### AC28a - Mandatory-DS lock allows relaxing changes

Given a **verification campaign** has honor mode `same campaign only`  
And at least one fully-verified record exists for the campaign  
When a customer operations user saves a campaign update that (i) adds a data source as optional, (ii) removes an optional data source, (iii) demotes a mandatory entry to optional, or
(iv) removes a data source entirely (regardless of prior mandatory status)  
Then the save succeeds and the campaign's `data_sources` and `mandatory_data_sources` reflect the change.

### AC28b - Mandatory-DS lock disengages under always-verify-new

Given a **verification campaign** is currently configured with honor mode `always verify new`  
When a customer operations user saves a campaign update that adds a data source as mandatory or promotes an optional entry to mandatory  
Then the save succeeds regardless of how many verifications the campaign has on record.  
And when honor mode is later switched back to `same campaign only`, the lock re-engages based on fully-verified records that exist at that moment (subsequent additions blocked per AC28).

### AC28c - Lock trigger boundary

Given a **verification campaign** has honor mode `same campaign only`  
And the campaign has zero **fresh** fully-verified records (it may have invites, attempts, `partial` receipts that have not been upgraded, or honored receipts, but **no fresh** record where the
then-current mandatory list was fully satisfied)  
When a customer operations user saves a campaign update that adds a data source as mandatory or promotes an optional entry to mandatory  
Then the save succeeds; the lock is not yet engaged.

## Frontend acceptance criteria (BDD)

### AC30 - Campaign provider assignment UX

Given a **verification campaign** has zero or more assigned providers  
When user is in **verification campaign** edit mode (campaign **not archived** — AC62) and uses provider dropdown and confirms add  
Then selected provider appears in the **verification campaign** provider list **and** the user can configure **that campaign’s assignment** outcome links (`completed`, `qc`, optional `security` and
`over-quota`) without duplicating the catalog entity.

### AC31 - New provider modal parity

Given user opens "new candidate provider" from **verification campaign** page  
When modal renders  
Then required fields include **display name** (catalog; parity with customer-level create), plus **assignment** fields (**completed** link, **qc** link, optional **security** and **over-quota** links)
for the current verification campaign; validation rules for shared fields (display name uniqueness AC60, URLs AC32a) match the customer-level catalog create flow where applicable.

### AC32 - Outcome link edit UX

Given **campaign–provider assignment** configuration UI is open for a **verification campaign**  
When user edits any **assignment** outcome link (completed, qc, security, or over-quota) for `(spgid, cmp)`  
Then UI preserves entered `{{param}}` placeholders and saves links as entered (subject to URL validation in AC32a and optimistic concurrency AC61).

### AC32a - Outcome link URL validation

Given a user is editing a **campaign–provider assignment** outcome link  
When user attempts to save a value that is not a syntactically valid URL or does not use the `https://` scheme  
Then save is blocked with a validation error and the link is not persisted.

### AC32b - Unknown placeholder save behavior

Given a user enters an **assignment** outcome link containing a placeholder that is neither reserved nor a known captured context key  
When user saves the assignment  
Then the link saves without warning, and at redirect time the unknown placeholder renders as an empty string.

### AC33 - Unique provider assignment per campaign

Given a candidate provider is already assigned to a **verification campaign**  
When user attempts to add the same provider again to that **verification campaign**  
Then the system blocks duplicate assignment, keeps a single provider entry for that **verification campaign**, and returns a deterministic duplicate-assignment message in UI.

### AC34 - Read-only campaign card provider controls

Given verification campaign card is displayed outside edit mode  
When user views candidate providers on that card  
Then provider URLs are visible and copyable, and add/remove controls are not available.

### AC35 - Edit-mode-only provider mutation

Given verification campaign card is displayed and user is not in edit mode **or** the campaign is **archived** (AC62)  
When user attempts provider assignment mutation  
Then frontend prevents mutation and prompts user to enter **verification campaign** edit mode first when the campaign is not archived; **archived** campaigns do not allow assignment mutations
regardless of
mode.

### AC36 - Honor mode mutual exclusivity

Given user is in **verification campaign** edit mode  
When they configure honor verification policy  
Then exactly one honor mode from the canonical set can be selected at a time.

### AC36a - Honor mode editable only in edit mode

Given verification campaign card is displayed outside edit mode **or** the campaign is **archived** (AC62)  
When user attempts to change honor mode or freshness window  
Then the change is blocked; modification is allowed only after entering **verification campaign** edit mode **when** the campaign is **draft**, **active**, or **paused**.

### AC37 - Freshness window activation rule

Given user is in **verification campaign** edit mode  
When honor mode is set to `always verify new`  
Then freshness window control is inactive.  
When honor mode is set to a mode that honors prior verification  
Then freshness window control is active.

### AC37b - Data sources editor with mandatory toggle

Given user is in **verification campaign** edit mode  
When the data sources editor renders  
Then each entry in `data_sources` displays a toggle indicating whether it is mandatory or optional, and the editor presents distinct controls to (i) add a new data source as optional, (ii) add as
mandatory, (iii) promote optional → mandatory, (iv) demote mandatory → optional, and (v) remove a data source.  
And on save, the controls produce a valid `(data_sources, mandatory_data_sources)` pair per AC58 (mandatory is a subset, no duplicates, empty allowed).

### AC37a - Mandatory-DS add/promote controls disabled under lock

Given user is in **verification campaign** edit mode  
And the campaign's honor mode is `same campaign only`  
And at least one fully-verified record exists for that campaign  
When the data sources editor is rendered  
Then controls that would add a data source as mandatory or promote an optional entry to mandatory are disabled and surface a tooltip explaining that mandatory additions are locked under honor mode.  
And demote, remove, and add-as-optional controls remain enabled.  
And when the user changes honor mode to `always verify new` within the same edit session, those add/promote controls re-enable without requiring a save first.

### AC38 - Default provider editability

Given user opens default provider **catalog** configuration  
When user edits provider fields  
Then only the **display name** field is editable at catalog level; **outcome links are edited per verification campaign** on each **`(spgid, cmp)` assignment** (UC6, AC32). The default provider
remains
non-removable (AC22).

### AC39 - Read-only verification options visibility

Given verification campaign card is displayed outside edit mode  
When user views verification settings for that **verification campaign** on the card  
Then the card shows read-only values for honor mode and freshness window only (no risk threshold, no separate always-verify-new field; honor mode value covers always-verify state).

### AC40 - Read-only provider row metrics visibility

Given verification campaign card is displayed outside edit mode  
When user views assigned candidate providers  
Then every assigned provider appears in the row list regardless of activity, and each row shows read-only metrics for `Ver%`, `Try%`, `Err/Req%`, and `Invited` using the definitions in this spec.

### AC41 - Per-row metrics empty state

Given verification campaign card is displayed outside edit mode  
And a provider row has zero invited candidates  
When user views that provider row  
Then percentage metrics render as "—" and `Invited` is `0`.

### AC42 - Truncated URL with full-value copy

Given verification campaign card is displayed outside edit mode  
When a provider landing URL is visually truncated in the row  
And user clicks copy for that provider URL  
Then clipboard receives the full configured URL value, not the truncated display text.

### AC43 - Aggregate pie charts visibility

Given verification campaign card is displayed outside edit mode  
And the **verification campaign** has at least one verified candidate  
When user views **verification campaign** aggregate verification analytics  
Then the card shows pie charts by data source for `Total Verified Invites`, `Success Verification %`, `Attempted Verification %`, and `Failed/Requested Verification %`.

### AC44 - Aggregate analytics empty state

Given verification campaign card is displayed outside edit mode  
And the **verification campaign** has zero verified candidates  
When user views **verification campaign** aggregate verification analytics  
Then the entire aggregate analytics block is hidden until at least one verified candidate exists.

### AC45 - Aggregate analytics source scope

Given **verification campaign** aggregate pie charts are rendered  
When values are computed for each data source slice  
Then totals and percentages are aggregated across all verified candidate pools belonging to that **verification campaign** `cmp`, slices are limited to that **verification campaign's current**
configured data sources (see Definitions and Read-only verification campaign card), a candidate verified via multiple data sources contributes to each corresponding slice, and percentages use a
totals-based computation (sum numerators across pools / sum denominators across pools per slice).

### AC46 - Edit-mode hides analytics

Given user enters **verification campaign** edit mode  
When edit-mode UI renders  
Then aggregate pie charts and per-provider row metrics are hidden until user exits edit mode.

### AC47 - Campaign-level invitees quick navigation

Given verification campaign card is displayed outside edit mode  
When user clicks campaign-level "View Invitees" on that card  
Then user is navigated to the invitees page with URL parameter `cmp` pre-set to that **verification campaign**.

### AC48 - Provider-level invitees quick navigation

Given verification campaign card is displayed outside edit mode  
When user clicks provider-row "View Invitees" for a specific candidate provider  
Then user is navigated to the invitees page with URL parameters `cmp` and `spgid` pre-set to that **verification campaign** and provider.

### AC49 - Invitees page pre-set filter application

Given invitees page is opened with URL query params for `cmp` and optional `spgid`  
When page initializes filters  
Then `cmp` is always applied and `spgid` is additionally applied when present so results are scoped to the selected **verification campaign** and optionally a single candidate provider.

### AC50 - Default provider label default

Given the default candidate provider is **provisioned on first verification campaign creation** (AC64)  
When the default provider is first displayed  
Then its display name defaults to the customer's company/display name and remains editable by customer users at the **catalog** level (UC6).

### AC51 - Provider removal blocked while active invites exist

Given a candidate provider is assigned to a **verification campaign**  
And one or more invites for that `(spgid, cmp)` are still in **non-terminal** state (Definitions — **Invite terminal state**)  
When user attempts to remove the provider **assignment** from the **verification campaign**  
Then removal is blocked with a deterministic message indicating non-terminal invites remain; removal succeeds only after **all** invites for that `(spgid, cmp)` are **terminal**.

### AC52 - Per-invite return_url override

Given an invite is created or updated for a **verification campaign** with an assigned candidate provider  
When `return_url` is not explicitly set on the invite  
Then the invite's `return_url` defaults to the **`(spgid, cmp)` assignment’s** outcome link selected by the mandatory-DS routing rule (AC54): the assignment's **completed** link if the candidate is
`Verified`, or the assignment's **qc** link if the candidate is `PartiallyVerified`.  
When `return_url` is explicitly set on the invite  
Then the override value is used regardless of mandatory satisfaction (override always wins).

### AC53 - Legacy ownership backfill

Given invite or session rows exist without a stored `spgid` from before this model was enforced  
When migration or backfill runs for that customer  
Then each such row is assigned the **`spgid`** of that customer's **default** candidate provider (customer as own default provider), so ownership and reporting align with Product decisions.

### AC54 - Mandatory-DS outcome-link routing (no override)

Given an invite for a **verification campaign** has no per-invite `return_url` override  
And the **`(spgid, cmp)` assignment** has both completed and qc outcome links configured (qc is required per **Campaign–provider assignment** in Provider model)  
When the candidate reaches end-of-flow with at least one data source authorized  
Then the platform selects `return_url`:

- this assignment's **completed** outcome link when `mandatory_data_sources` is empty OR every entry in `mandatory_data_sources` has been authorized for this candidate (state `Verified`); or
- this assignment's **qc** outcome link when `mandatory_data_sources` is non-empty and at least one entry has not been authorized for this candidate (state `PartiallyVerified`).

### AC55 - Partial verification receipt and upgrade-in-place

Given a candidate ends a fresh verification flow in state `PartiallyVerified` (≥ 1 data source authorized but `mandatory_data_sources` is non-empty and unsatisfied)  
When verification result is persisted  
Then the platform writes a verification receipt marked `partial` for audit and analytics; while the receipt remains in `partial` state it is **not honor-eligible**.

Given that same candidate later returns to the **same invite/session (`sgid`)**  
And authorizes the entries currently missing against the campaign's **current** `mandatory_data_sources` list  
When the new authorization event is persisted  
Then the existing receipt is **upgraded in place**: state becomes `Verified`, the underlying verification cookie is reissued or its honor-eligibility flag is flipped per AC13, and the receipt
becomes honor-eligible. Eligibility is evaluated against the campaign's **current** `mandatory_data_sources` list at the moment of upgrade (so demotions or removals applied between issuance and
upgrade may bring the receipt into coverage).

### AC56 - Honor coverage rule (all-or-nothing)

Given verification campaign honor mode is `same campaign only` and an otherwise-eligible same-campaign cookie is present  
When honor eligibility is evaluated against the consuming campaign's **current** `mandatory_data_sources` list  
Then the cookie qualifies for honor only if its underlying authorized sources cover **every** entry in the current mandatory list. If even one current mandatory entry is uncovered the cookie is
disqualified in full and the candidate is routed through fresh verification of every entry in the current mandatory list. There is no partial-honor / top-up flow.  
And receipts that **remain** in `partial` state (AC55) are never honor-eligible regardless of overlap with the current mandatory list. Once a partial receipt is upgraded in place to `Verified`
per AC55 it is no longer `partial` and is evaluated under ordinary honor rules.

### AC58 - Mandatory list validation

Given a customer operations user saves a verification campaign with a `mandatory_data_sources` value  
When the value is validated  
Then the save succeeds only when every entry in `mandatory_data_sources` is present in `data_sources`, the list contains no duplicates, and the empty list is accepted (meaning "all data sources
optional"); otherwise the save is rejected with `400 Bad Request` and a validation error identifying the offending entries.

### AC59 - Data source removal cascades to mandatory

Given a verification campaign has `mandatory_data_sources` containing data source `X`  
When a customer operations user removes `X` from `data_sources` and saves  
Then `X` is also removed from `mandatory_data_sources` in the same save (no orphaned mandatory entries) and the save succeeds (subject to the Round 7 lock rule, which permits removal but not
addition under the lock).

### AC60 - Unique candidate provider display names within customer

Given two candidate providers belonging to the **same** customer  
When their display names are compared **after trimming whitespace**, **case-insensitively**  
Then names **must not** collide for **non-deleted** catalog rows; saves that would create a duplicate **must** be rejected with `400 Bad Request` and a deterministic validation error.

### AC61 - Optimistic locking on candidate-provider and assignment updates

Given a client updates a candidate provider catalog row **or** a campaign–provider assignment row  
When the update carries an expected **version** (or equivalent concurrency token)  
Then persistence applies the update **only if** the stored version matches;  
When the version **does not** match  
Then the operation **rejects** with `409 Conflict` and a structured **`VERSION_MISMATCH`** reason code—no partial write.

### AC62 - Archived verification campaigns are read-only for configuration

Given a verification campaign is **`archived`**  
When a customer operations user attempts **any** mutation covered by this spec (provider assignment add/remove, assignment outcome links, honor mode, freshness, `data_sources` /
`mandatory_data_sources`)  
Then the platform rejects the mutation per API standards and **does not** apply changes.  
And read-only analytics/navigation behavior remains allowed where otherwise specified.

### AC63 - Draft, active, and paused campaigns allow configuration edits

Given a verification campaign is **`draft`**, **`active`**, or **`paused`**  
When a customer operations user performs mutations permitted elsewhere in this spec (subject to mandatory-DS lock, invite guards, and concurrency rules)  
Then those mutations **may succeed** (they are **not** rejected solely because of lifecycle state).  
And **`archived`** remains excluded per AC62.

### AC64 - Provision default candidate provider and assignment on campaign create

Given a customer has **no** verification campaigns yet  
When the customer’s **first** verification campaign is created  
Then the platform **provisions** the non-removable **default** candidate provider catalog row if absent **and** creates a **default-provider assignment** for that new campaign with **completed**
and **qc** outcome links **supplied by the user** at create time (validated per AC32a; security and over-quota optional).

Given subsequent verification campaigns for the same customer  
When those campaigns are created  
Then they **reuse** the existing default candidate provider catalog row (no second default row is created) **and** the platform creates a **fresh default-provider assignment** for the new campaign
with its own user-supplied completed and qc links (AC32a) — each campaign carries its own assignment link set per AC27.

Given any verification campaign created via this AC  
When a user attempts to remove or unassign the default-provider assignment from that campaign  
Then the operation is **rejected** per AC22; the default-provider assignment is preserved for the campaign’s lifetime.

### AC65 - Custom provider deletion (hard forbidden when linked; soft only when all campaigns archived)

Given a **custom** candidate provider has **linked candidates** (Definitions — **Linked candidates**)  
When an operator attempts **hard delete** of that provider  
Then the operation is **rejected** and the provider row remains.

Given a **custom** candidate provider has at least one **campaign–provider assignment** on a **non-archived** verification campaign (draft, active, or paused)  
When an operator attempts **soft delete** of that provider  
Then the operation is **rejected** with a deterministic message instructing the user to archive (or otherwise resolve) the affected campaigns first.

Given a **custom** candidate provider whose every campaign–provider assignment is on an **archived** verification campaign  
When an operator requests **soft delete**  
Then the provider is marked deleted without destroying historical invite/session/verification records, and the provider plus its linked candidates are **filtered from operational default views**
(catalog list, invitees default list, campaign card per-provider row); AC25 historical pool queryability is preserved for explicit archive-time queries. **Restoration is out of scope** in this
version.

Given a request to delete the **default** provider in any form  
When the operation is attempted  
Then it is rejected per AC22.

### AC66 - List and get candidate providers

Given an authorized customer-scoped **list** request for candidate providers  
When the API responds  
Then the response includes each provider’s **catalog** attributes (identifiers, display name, soft-delete state as applicable, **version** for concurrency) and **does not** require embedding
per-campaign outcome links (those are loaded via campaign assignment APIs or campaign edit UI).

Given the list request does not opt into soft-deleted rows (`include_deleted` flag absent or false)  
When the response is built  
Then **soft-deleted providers are excluded by default**; clients that explicitly opt in receive soft-deleted rows with their `deleted` state plainly indicated.

Given an authorized **get-by-id** request  
When the provider exists for that customer (live or soft-deleted)  
Then the single-record payload matches the same contract rules as list rows; soft-deleted providers are still retrievable by id for historical / audit purposes.

## Open questions requiring PM confirmation

- None at this time. Resolved clarifications are in `specs/sample_providers/questions.md` (Clarifications, 2026-04) and reflected in **Product decisions** above.

## Related specs

- Survey product (out of scope here; cross-reference only): `specs/survey_invites/survey_invites_business_spec.md`
- Decision log and stakeholder clarifications: `specs/sample_providers/questions.md`
