# Candidate Providers - Questions and Decisions Log

This document captures breadth-first requirement questions and resolved decisions for candidate provider management + verification reuse flow.

---

## Canonical sources and scope

- **Canonical product requirements** for this initiative are in `candidate_providers_business_spec.md` (including **Product decisions**). When this log disagrees with that spec, **follow the business
  spec**. Clarifications from the table below are merged into the business spec.

- **Out of scope for this document and the candidate-provider initiative:** **survey campaigns**, **survey invites**, and **survey landing / session / completion** behavior. Those are owned by the
  survey specs (`specs/survey_invites/`, `specs/survey_management/`). Do not fold survey requirements into candidate-provider decisions here.

- **Existing production “verification” in the codebase** (today) means **session-scoped data-collection verification**: OAuth sources (`DataSource`: LinkedIn, Google, Booking, YouTube, …), portability
  file flows, async **`SessionDataEvent`** processing (`POST /v1/event/verify`), scoring and qualification (`GET /verify/score`, `/verify/scores`), fingerprints, and persisted **`Verification`** rows
  keyed by **`(customer_id, ref_id, cmp)`**. It does **not** yet implement the spec’s **honor modes**, **verification reuse cookies**, **`spgid` ownership**, or **return-visit** routing; those are *
  *target** behaviors described in the business spec, not current backend features.

---

## Clarifications (PM / stakeholder — 2026-04)

Resolved in working session; refine in business spec if anything conflicts.

| Topic                                 | Decision                                                                                                                                                                                                                                      |
|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Post-verify handoff                   | **`return_url`** carries the candidate onward; no additional Taxiway-hosted step required for this initiative.                                                                                                                                |
| Invite links                          | **`cgid`** appears on issued invite links (not only raw `cmp`).                                                                                                                                                                               |
| Landing without `spgid`               | Resolve **`spgid`** to the customer **default** candidate provider.                                                                                                                                                                           |
| SuperMarketer (Q4)                    | **REMOVED (Round 8, see D48).** SuperMarketer is no longer a concept in this initiative. Each customer has only their **default** candidate provider plus any **custom** candidate providers they add. Supersedes Q4/D15.                     |
| Verification honor cookie             | **First-party only** (Taxiway); partners rely on **`return_url`**, not cross-domain cookies.                                                                                                                                                  |
| Data source completion (return visit) | Evaluate against **historical** configured sources at verification time (not retroactive when campaign `data_sources` changes later).                                                                                                         |
| Campaign card metrics                 | **Near real-time** (low latency acceptable via short TTL cache).                                                                                                                                                                              |
| **`spgid` backfill**                  | Migrate existing invites and sessions: set **`spgid`** to the customer’s **default** candidate provider — i.e. the customer **as their own** candidate provider (**that customer’s** default-provider **`spgid`**), not an invented sentinel. |

---

## Clarifications (PM / stakeholder — 2026-05)

Synced with **`candidate_providers_business_spec.md`** (Product decisions, Definitions, AC60–AC66). If this table conflicts with that spec, **follow the business spec**.

| Topic                                | Decision                                                                                                                                                                                                                                                                                                                                                       |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Outcome link placement**           | **Completed**, **qc**, **security**, and **over-quota** URLs are stored on the **campaign–provider assignment** (`(verification_campaign, candidate_provider)`), not on the shared catalog row. Each time a provider is attached to a campaign, that relationship carries its own link set so the same catalog provider can differ per campaign.               |
| **Verified candidate pools**         | Pool key remains **`(spgid, cmp)`** (one pool per provider **per verification campaign**). Assignment outcome links configure handoff for that pool slice only.                                                                                                                                                                                                |
| **Hard vs soft delete**              | **Hard delete** of a candidate provider is **forbidden** when **linked candidates** exist (persistent invite/session/verification history). **Soft delete** is the supported path in those cases (**AC65**, Definitions — **Linked candidates**).                                                                                                              |
| **Non-terminal invites**             | **Terminal** invite/session (for removal policy): **`Verified`**, **`PartiallyVerified`**, or **`Errored`**. **Non-terminal**: anything else (e.g. **`Requested`**, in-progress). **UC8 / AC51** block removing a provider **assignment** from a campaign until **all** invites for **`(spgid, cmp)`** are terminal (Definitions — **Invite terminal state**). |
| **List / get providers**             | Customer-scoped **list** and **get-by-id** return **catalog** attributes (identifiers, display name, soft-delete state, **version**). Per-campaign outcome links are **not** embedded; they are loaded via campaign assignment APIs or campaign edit UI (**UC11**, **AC66**).                                                                                  |
| **Default provider provisioning**    | Default candidate provider is **provisioned when the customer’s first verification campaign is created** and **reused** for later campaigns—not required to exist before any campaign exists (**AC64**, **AC50**).                                                                                                                                             |
| **Campaign lifecycle / edits**       | Provider assignments, assignment links, honor mode, freshness, and `data_sources` / `mandatory_data_sources` may be edited when the verification campaign is **draft**, **active**, or **paused**. **Archived** verification campaigns reject those mutations (**AC62**, **AC63**).                                                                            |
| **Duplicate provider names**         | Display names are **unique per customer** after trim, compared **case-insensitively**, among applicable catalog rows (**AC60**).                                                                                                                                                                                                                               |
| **Optimistic locking**               | Candidate-provider catalog rows and campaign–provider assignment rows use a **version** (or equivalent). The DAO/persistence layer **rejects** updates when the client version does not match, with **`409 Conflict`** and **`VERSION_MISMATCH`** (**AC61**).                                                                                                  |
| **Default provider auto-assignment** | Every verification campaign carries a default-provider assignment, created at campaign-create with required completed and qc links supplied by the user (**AC64**). The assignment cannot be removed (**AC22**); the default catalog row cannot be hard- or soft-deleted (**D60**).                                                                            |
| **Partial receipt upgrade**          | `partial` receipts can be **upgraded in place** to `Verified` / honor-eligible when the same candidate later authorizes the missing mandatory entries on the **same invite/session** (**AC55**, **D58**). Honor-pipeline cookie evaluation remains all-or-nothing (**AC56**).                                                                                  |
| **Custom provider soft-delete**      | Allowed only when all of the provider's assignments are on **archived** campaigns; afterward the provider and its linked candidates are filtered from operational default views (**AC65**, **D59**).                                                                                                                                                           |
| **Mandatory-DS lock trigger**        | Only **fresh** `Verified` records trigger the lock; honored and partial receipts do not trigger on their own (**AC28**, **AC28c**, **D61**).                                                                                                                                                                                                                   |

---

## Deprecated — early inventory (do not use)

The bullet list below was an early artifact mine. **It is deprecated** because it mixed goals with stale rules (e.g. duplicate `ref_id` → `409`, pre–D40 honor modes). Use *
*`candidate_providers_business_spec.md`** and the **Decisions log** below instead.

### Terms and identifiers (historical only)

- `customer_id`
- `cmp`
- `cgid`
- `ref_id`
- `sgid`
- `candidate_provider_id`
- `spgid`
- `return_url`
- `invite_url`
- verified candidate pool
- honor mode
- freshness window (`X days`)
- honored verification
- default provider
- provider-specific landing page
- data source (OAuth/data integration used during verification)

### User-facing outcomes and rules (historical only)

- Configure verification campaign source provider(s)
- Attribute candidate ownership to provider (`spgid`)
- Reuse or re-verify using honor modes
- Reject duplicate `ref_id` per `(customer_id, cmp)` with `409` — **deprecated;** superseded by return-visit behavior (see **D44** and AC7 in the business spec)
- Forward non-core query params unchanged
- Cookie + DB cross-check before honoring
- Read-only campaign card analytics (per-provider metrics, aggregate pie charts by data source)
- Quick navigation to invitees page filtered by campaign and/or provider

---

## Decisions log (resolved)

### Scope and naming

- **Q1. Product naming.** Canonical terms: `candidate provider`, `verification campaign`. (`survey campaign` is a separate product area; see survey specs — **out of scope** for this log’s delivery
  slice.)
- **Q2. In-scope delivery slice.** Provider attribution + routing and **target** verification honor/reuse logic per `candidate_providers_business_spec.md`. Survey campaigns and survey invites are *
  *not** in scope here.

### Provider model and governance

- **Q3 / D11. Default provider editability.** ~~Display name only is editable. All other fields are locked.~~ **Superseded (Round 9 / 2026-05):** At **catalog** level, only **display name** is edited
  for the default provider; **outcome links** are configured per **campaign–provider assignment**, not on the catalog row (**D49**). Default provider remains non-removable (**AC22**).
- **Q4 / D15. SuperMarketer enablement.** ~~Auto-available to every customer by default; ownership represented per-customer via `spgid`.~~ **DEPRECATED by D48 (Round 8).** SuperMarketer concept
  removed.
- **Q5 / D12. Required provider fields v1.** ~~Display name, completed link, qc link.~~ **Superseded (Round 9 / D49):** **Catalog (custom provider):** display name only. **Campaign–provider
  assignment:** completed + qc links required when attached to a verification campaign; security + over-quota optional on the assignment.
- **Q5 / D13. Optional provider fields v1.** ~~Security link, over-quota link.~~ **Superseded (Round 9 / D49):** Security and over-quota links are **optional on the assignment**, not on the catalog
  row.
- **Q5 / D14. Provider status.** No active/inactive flag in v1. A provider is active by virtue of being assigned to a campaign and is removed when no longer needed.
- **D21. Default provider display label.** Defaults to the customer's company/display name; renameable by customer users.
- **Q6. Completion URL ownership.** ~~Provider-level only in v1; no extra campaign-layer override beyond provider configuration~~ **Superseded (Round 9 / D49).** Outcome URLs are owned by the *
  *campaign–provider assignment**. Mandatory-DS routing (**AC54**) chooses that assignment’s **completed** vs **qc** link; per-invite **`return_url`** override still wins (**AC52**). Survey-specific
  overrides remain in survey specs.

### Landing, attribution, and query context

- **Q7. Attribution precedence.** When `spgid` is present and valid, attribution uses that `spgid` regardless of other query context.
- **Q8 / D16. Invalid `spgid` behavior.** Reject with `400 Bad Request`. Do not fall back to default provider.
- **Q9. Forwarded query keys.** Core keys are `cgid`, `spgid`, `ref_id`. All other keys are forwarded unchanged.

### Verification reuse and freshness

- **Q10 / D9. Cross-campaign freshness source.** Consuming verification campaign's window decides freshness in `honor any prior verification for this customer` mode.
- **Q11 / D10. Multi-cookie tie-break.** Most recent verification wins.
- **Q12 / D1, D3. Risk threshold.** Risk threshold is removed from campaign configuration entirely. Risk score is still computed and persisted (cookie + DB) for audit only; it does not gate honor
  decisions.
- **Q13 / D3. Missing risk score handling.** Not applicable — risk score does not gate honor decisions.
- **D8. Canonical honor mode set.** `same campaign only`, `honor any prior verification for this customer`, `always verify new`.

### Read-only verification campaign card

- **D7. Card scope.** Read-only card represents a verification campaign only.
- **D2. Aggregate scope and naming.** Pie chart values are aggregated across verified candidate pools only; total panel renamed `Total Verified Invites by Data Source`.
- **D4. Data source meaning.** OAuth/data integration used during verification; multi-counted (a candidate verified via 2 sources contributes to 2 slices).
- **D20. Data source slice set.** Pie slices limited to the campaign's configured data sources.
- **D5. Per-row metric definitions.** Denominator `Invited`. `Ver% = Verified/Invited`, `Try% = Attempted/Invited`, `Err/Req% = (Errored + Requested)/Invited`. `Requested` = invites that never reached
  a terminal state.
- **D6. Time window.** No time window; metrics are cumulative all-time for the campaign.
- **D18. Empty state.** Aggregate analytics block hidden until at least one verified candidate exists; per-row metric percentages render as "—".
- **D22. Edit mode.** Aggregate charts and per-row metrics are read-only-mode only; hidden in campaign edit mode.
- **D17. Invitees URL contract.** URL parameter names are `cmp` and `spgid`.

### Error contracts

- **Q14 / D23. Duplicate `ref_id` 409 payload.** Superseded by **D44**: identical `(cgid, ref_id, spgid)` return visit is not a conflict; see AC7 series. Other duplicate/conflict shapes (e.g. `ref_id`
  reuse with wrong `spgid`) remain `400` per AC7a.

### Access control

- **D24. Analytics access.** Visibility follows existing campaign OAuth scope; no new role gating introduced by this spec.

### Existing features (no spec changes)

- **D19. Bulk Invite Import.** Already exists; left unchanged. Wireframe button retained.

### Round 2 \u2014 outcome links, removal, honoring, attribution

- **D25. Required vs optional provider fields (revised).** Required: display name, completed link, qc link. Optional: security link, over-quota link. (Supersedes D12/D13.) **Further superseded by
  D49 (Round 9):** split **catalog** vs **assignment** required fields.
- **D26. Outcome link routing logic.** Out of scope this version. Default behavior: invite's `return_url` is the provider's completed link; can be overridden per invite. **Partial supersession (Round
  9 / D49):** default routing uses the **`(spgid, cmp)` assignment’s** completed/qc links per **AC54**; security/over-quota selection remains out of scope except storage on assignment.
- **D27. Provider removal lifecycle.** Removal blocked when active (non-terminal) invites exist for `(spgid, cmp)`; allowed only when no active invites remain. **Clarified (Round 9):** “active” =
  **non-terminal** per Definitions — **Invite terminal state**; applies to **assignment removal** from the campaign.
- **D28. Honored data source attribution.** Honored candidates contribute to consuming campaign's pie chart slices using the original (root) verification's data source(s).
- **D29. Wireframe alignment.** Full alignment to spec required (Always Verify New row, Max Acceptable Risk row, 'Locked' button to be removed; chart panel renamed to Total Verified Invites; analytics
  block respects empty state).
- **D30. Unknown placeholder behavior.** Save as-is, no warning. Render empty at redirect time.
- **D31. Pool lifecycle.** Pool open and queryable indefinitely; campaign closure does not affect pool semantics.
- **D32. Honoring depth.** Single-level only \u2014 already-honored records cannot themselves be honored. New audit invite always links to original (root) `sgid`.
- **D33. SuperMarketer outcome links.** ~~System-managed globally by Taxiway operations; same links across all customers.~~ **DEPRECATED by D48 (Round 8).** SuperMarketer concept removed.
- **D34. URL validation.** Outcome link URLs must be syntactically valid `https://` URLs. Reject `http://`, relative paths, or malformed values at save time.
- **D35. SuperMarketer customer-side editing.** ~~Fully locked. Customer cannot rename or edit links.~~ **DEPRECATED by D48 (Round 8).** SuperMarketer concept removed.
- **D36. Honored counts as Verified.** Honored candidates count as `Verified` in consuming campaign's per-row metrics. (Updates Definitions.)
- **D37. Default provider editability (revised).** Display name AND outcome links are editable; default provider remains non-removable. (Supersedes D11.) **Superseded (Round 9 / D49):** display name
  at **catalog**; outcome links on each **assignment** where the default provider appears.
- **D38. Aggregate computation method.** Totals-based across all pools per data source slice (sum numerator / sum denominator). Averaging per-pool percentages is not used.
- **D39. Card provider listing.** All assigned providers appear on the read-only card regardless of activity. Inactive rows show "\u2014" / 0.

### Round 3 \u2014 cross-campaign honoring removed

- **D40. Cross-campaign honoring removed.** Honor mode canonical set is reduced to two modes: `same campaign only` and `always verify new`. Verification records issued by a different verification
  campaign cannot be honored, regardless of customer or freshness. (Supersedes D8 and D9; deprecates the `honor any prior verification for this customer` mode and the consuming-campaign
  freshness-source rule.)

### Round 4 \u2014 business rules vs ACs cleanup

- **D41. Cleanup approach.** Medium scope: remove business rules that pure-duplicate behaviors covered by ACs, AND add 7 new ACs to close gaps where rules asserted untested behaviors.
- **D42. Canonical source.** ACs are canonical for behaviors. Business rules contain only declarative invariants (no Given/When/Then-style content). Definitions stay in the Definitions section.
- **New ACs added (gap closure).** AC22 default provider non-removability, AC23 same-customer assignment enforcement, AC24 SuperMarketer auto-availability, AC25 verified pool indefinite queryability,
  AC26 risk score non-gating, AC27 ~~no per-campaign outcome link override~~ (**superseded Round 9:** per-campaign **assignment** outcome links — see **D49**), AC36a honor mode editable only in edit
  mode.

### Round 5 \u2014 return visit vs duplicate ref_id

- **D43. Required landing parameters.** `ref_id` is required on landing URLs (caller-parameterized).
- **D44. Return visit behavior.** Repeat landing with the same `cgid`, `ref_id`, and `spgid` as an existing invite is a return visit (same `sgid`, no duplicate invite row). Routing: (a) eligible
  verification cookie \u2192 honor flow per spec; (b) no cookie and no data-source completion on record \u2192 proceed with verification as normal; (c) no cookie but data-source completion exists
  \u2192 user-facing error (\u201cunable to verify at this time\u201d class) plus structured application log. **Supersedes** prior **Q14 / D23** plain `409` duplicate `ref_id` behavior for identical
  triple return visits.
- **D45. Spgid mismatch on return.** Same `cgid` + `ref_id` as existing invite but different `spgid` than stored \u2192 `400 Bad Request`.

### Round 6 \u2014 mandatory data sources

- **D46a. Mandatory data sources concept.** A **verification campaign** carries a `mandatory_data_sources` list \u2014 a subset of `data_sources` whose successful authorization is required for a
  candidate to be considered fully verified. Empty list = all data sources optional (today's behavior). Configured at campaign level, editable only in campaign edit mode. Strict subset of
  `data_sources`; duplicates rejected; removal from `data_sources` cascades removal from `mandatory_data_sources`.
- **D46b. Tightened `Verified` definition.** A candidate is `Verified` for the consuming campaign when (i) `mandatory_data_sources` is non-empty and the candidate has authorized **every** entry in
  that list, OR (ii) `mandatory_data_sources` is empty and the candidate has authorized at least one data source. This applies to fresh verifications and to honored verifications. (Tightens the
  prior \u2265 1-source-authorized definition.)
- **D46c. Outcome-link routing by mandatory satisfaction.** When an invite has no explicit `return_url` override (AC52 unchanged): if the candidate is `Verified` per D46b, route to the provider's
  **completed** link; otherwise (\u2265 1 source authorized but mandatory unsatisfied) route to the provider's **qc** link. When no source is authorized, the candidate has not completed
  verification at all and standard error/retry behavior applies.
- **D46d. Partial verification receipt.** When a candidate has authorized ≥ 1 source but mandatory is unsatisfied, the platform records a `partial` verification receipt for audit and analytics.
  ~~The receipt is never honor-eligible for any future landing and is never upgraded in place; it remains a historical record of partial completion only.~~ **Revised (Round 10 / D58):** While the
  receipt remains in `partial` state it is **not honor-eligible**, but it **may be upgraded in place** when the same candidate returns to the **same invite/session (`sgid`)** and authorizes the
  entries currently missing against the campaign's **current** `mandatory_data_sources` list. On upgrade the receipt becomes `Verified` and honor-eligible (per **AC55** / **AC13**). The honor
  pipeline's all-or-nothing coverage rule (**D46e**, **D46f**) governs return-visit cookie evaluation and is unchanged.
- **D46e. Honor coverage rule (all-or-nothing).** Honor evaluation requires the prior verification's authorized sources to cover the consuming campaign's **current** `mandatory_data_sources` list
  in full. A cookie whose underlying sources do not cover the current list in full is **disqualified entirely**; the candidate is routed through fresh verification of every entry in the current
  mandatory list. (Earlier draft proposed honoring partial coverage with a top-up flow; this was simplified after recognizing top-up is unreachable under steady-state Round 7 lock conditions.)
- **D46f. Top-up not implemented.** There is no partial-honor-plus-top-up flow. A same-campaign cookie either fully covers current mandatory (full bypass) or is disqualified (full re-verify of
  mandatory). This keeps the honor pipeline AC15 deterministic and avoids partial-credit receipt linkage that would only fire in narrow transitional windows (feature rollout, honor-mode toggle
  during which mandatory was grown).
- **D46g. AC7d unchanged.** Mandatory DS does not relax the AC7d block. Any historical data-source completion record blocks re-verification on a return visit, regardless of whether the historical
  mandatory list was satisfied.
- **D46h. AC52 unchanged.** Per-invite `return_url` override always wins over the mandatory-DS routing. Mandatory routing applies only when the invite has no override (i.e. defaults to a provider
  outcome link).
- **D46i. `min_authorizations_for_return` unchanged.** That field continues as a UI-visibility knob; mandatory DS is the authoritative completion gate. The two coexist.

### Round 8 \u2014 SuperMarketer removed

- **D48. SuperMarketer concept removed from this initiative.** The candidate-provider catalog is reduced to two kinds of providers per customer: (i) a **default** candidate provider (the customer
  as their own provider, non-removable, customer-editable **display name** at catalog; **outcome links on campaign–provider assignments** per **D49 / Round 9**), and (ii) zero or more **custom**
  candidate providers added by the customer. There is no system-wide globally managed provider, no per-customer SuperMarketer row, no Taxiway-operations governance flow for provider configuration,
  and no customer-side immutability rule for any provider.
  - **Supersedes:** Q4 / D15 (SuperMarketer enablement), D33 (SuperMarketer outcome links), D35 (SuperMarketer customer-side editing). Marked deprecated above.
  - **Removes from business spec:** UC11 (Manage global SuperMarketer configuration), AC24 (SuperMarketer auto-availability), AC38a (SuperMarketer customer-side immutability), the Taxiway operations
    user as a customer-facing actor in this initiative, and any "system-managed" / "globally managed" qualifier on provider model rules.
  - **Migration / existing data:** No production data exists for this concept yet — no migration is required. If any test fixtures reference SuperMarketer, they should be removed or replaced with
    a custom provider.
  - **Rationale (User, 2026-04):** The SuperMarketer governance flow added cross-organization complexity (separate Taxiway-ops UI, per-customer "ghost" provider rows mirroring a global config,
    customer-side immutability rules) without delivering customer-visible value beyond what a customer-managed custom provider already provides. Reducing to "default + custom" keeps the model
    simple and entirely within customer scope.

---

### Round 7 \u2014 mandatory-DS lock under honor mode

- **D47. Mandatory-DS lock under honor mode.** When `honor_mode = same_campaign_only` AND the verification campaign has at least one fully-verified record (per the tightened `Verified` definition,
  Round 6 / Q2), the campaign's mandatory data source list is **locked against additions**:
  - **Forbidden:** adding a data source as mandatory (whether brand-new in `data_sources` or by promoting an existing optional entry to mandatory).
  - **Allowed:** adding optional data sources, removing optional data sources, demoting mandatory \u2192 optional, and removing data sources entirely.
  - **Lock trigger:** the first record marked `Verified` per the tightened definition (partial cookies and honored receipts do not trip the lock on their own).
  - **Lock toggle:** lock follows current honor state. Switching to `always_verify_new` unlocks mandatory additions; switching back to `same_campaign_only` re-engages the lock if verifications exist.
  - **Enforcement:** authoritative at the API (reject with `400` and structured reason code `MANDATORY_LOCKED_HONOR_ENABLED`) and reflected in UI (controls disabled, tooltip explains).
  - **Rationale:** prevents silent invalidation of prior honor-eligible verifications under Round 6 / Q5 (honor must satisfy current mandatory).

### Round 10 — gap closure (2026-05)

- **D57. Default-provider auto-assignment per campaign.** Every verification campaign carries a default-provider assignment created at campaign-create time. The customer ops user **must supply
  completed and qc** outcome links during campaign create (security and over-quota optional); the platform validates per **AC32a**. The default-provider assignment **cannot be removed** from a
  verification campaign for the campaign's lifetime, and the default catalog row **cannot be hard- or soft-deleted** (**AC22**, **AC64**). Closes the gap created by **D49** (links moved to
  assignment) — under the new model the default provider needed an assignment per campaign for **AC1** / **AC54** routing to be well-defined.

- **D58. Partial verification receipt upgrade-in-place (revises D46d).** A `partial` receipt may be **upgraded in place** when the same candidate returns to the **same invite/session (`sgid`)** and
  authorizes the missing entries against the campaign's **current** `mandatory_data_sources` list. On upgrade the receipt becomes `Verified` and honor-eligible; the underlying cookie is reissued or
  its honor flag flipped per **AC13**. Coverage is evaluated against the **current** mandatory list at upgrade time. **Supersedes** the “never upgraded in place” language in **D46d**, **AC55**, and
  reaffirms Round 6 **Q4** (issue-and-upgrade option). The honor pipeline’s all-or-nothing coverage rule (**D46e**, **D46f**, **AC56**) is unchanged: it governs **return-visit cookie evaluation**,
  not same-invite upgrade.

- **D59. Custom provider deletion policy (refines D52 / AC65).**
    - **Hard delete** is forbidden whenever linked candidates exist.
    - **Soft delete** is permitted only when **every** campaign–provider assignment for that provider is on an **archived** verification campaign. Soft delete is rejected if any assignment is on a
      draft, active, or paused campaign — the user must archive the affected campaigns first.
    - After soft delete, the provider and its linked candidates are **filtered from operational default views** (catalog list, invitees default list, campaign card per-provider row); **AC25**
      historical pool queryability is preserved for explicit archive-time queries.
    - **Restoration / undelete** is **out of scope** in this version.

- **D60. Default provider locked end-to-end (refines AC22).** The default candidate provider cannot be **hard-deleted, soft-deleted, or unassigned** from any verification campaign that uses it.
  Combined with **D57**, this means every verification campaign for that customer permanently includes the default-provider assignment.

- **D61. Mandatory-DS lock trigger is fresh-only (clarifies D47 / AC28 / AC28c).** Only **fresh** `Verified` records (per the tightened Round 6 / Q2 definition, against the **then-current**
  mandatory list at the moment of completion) trigger the lock. Honored receipts and `partial` receipts that have not been upgraded do **not** trigger the lock on their own. **AC28** and **AC28c**
  are updated accordingly.

- **D62. List API soft-delete defaults (refines AC66).** **List** requests **default-exclude** soft-deleted providers; clients may opt in via `include_deleted` to receive them with `deleted` state
  plainly indicated. **Get-by-id** continues to return soft-deleted providers for historical / audit purposes.

- **D63. Provider catalog architect-doc reconciliation.** Architect doc **A2** previously placed `OutcomeLinks` as a value object on `CandidateProvider`. Per **D49**, `OutcomeLinks` belongs to the
  **`CampaignProviderAssignment`** aggregate. **`candidate_providers_architecture.md` updated 2026-05** (§2.2, §3.1, §4.1, ADR-CP-7); `CandidateProvider` retains identity, display name, soft-delete
  metadata, and version (concurrency).

---

### Round 9 — catalog vs assignment, API, lifecycle, concurrency (2026-05)

- **D49. Outcome links on campaign–provider assignment.** **Completed**, **qc** (required), **security**, **over-quota** (optional) URLs belong to the **`(verification_campaign, candidate_provider)`**
  assignment aggregate, not to the shared `CandidateProvider` catalog row. The same catalog provider reused across campaigns may have **different** link sets per campaign. Default post-verify routing
  without per-invite override uses that assignment’s links (**AC54**). **Supersedes** the “provider-level only” posture in **Q6/D21**, field placement in **D25**, **D37** (outcome links), and the
  Round 6 working assumption that provider outcome links remain provider-scoped (see Round 6 Q9 reconciliation below).

- **D50. Default provider provisioning timing.** The default candidate provider row is **provisioned when the customer’s first verification campaign is created** (**AC64**); subsequent campaigns *
  *reuse**
  it. **Supersedes** any implication that the default provider must exist before the first campaign.

- **D51. Verification campaign lifecycle mutability.** Mutations to assignments, assignment links, honor mode, freshness, and data-source configuration are **allowed** for verification campaigns in
  **draft**, **active**, or **paused** state and **rejected** for **archived** campaigns (**AC62**, **AC63**).

- **D52. Provider deletion policy.** **Hard delete** is **forbidden** when **linked candidates** exist (**AC65**). **Soft delete** is permitted as the catalog deletion path that preserves
  audit/history.

- **D53. Invite terminal semantics for removal guards.** **Terminal** = **`Verified`**, **`PartiallyVerified`**, or **`Errored`**; **non-terminal** otherwise (**Definitions**). Provider **assignment**
  removal from a campaign is blocked while **any** non-terminal invite exists for **`(spgid, cmp)`** (**AC51**, **UC8**).

- **D54. Catalog read API.** **List** and **get** candidate providers expose catalog fields including **version** for optimistic concurrency; assignment outcome URLs are loaded separately (**AC66**,
  **UC11**).

- **D55. Unique provider display names.** Within a customer, candidate provider **display names** are unique after trim, **case-insensitive** (**AC60**).

- **D56. Optimistic locking.** Updates to catalog rows and assignment rows require matching **version** at persistence; mismatch → **`409 Conflict`**, **`VERSION_MISMATCH`** (**AC61**).

---

### Round 6 reconciliation — mandatory DS vs provider links (2026-05)

- **Round 6 Q9 working assumption (line ~339)** stated `mandatory_data_sources` is campaign-level and “provider-level outcome links remain provider-scoped.” **Partial revision:** *
  *`mandatory_data_sources`**
  remains **campaign-level**. **Outcome links** are **assignment-scoped** (**D49**), not a single set per catalog provider across campaigns.

---

## Survey requirements (explicitly out of scope here)

- Survey invite/session/campaign requirements live under `specs/survey_invites/` and `specs/survey_management/`.
- **This document does not track survey decisions.** Candidate provider work must not depend on resolving survey specs.

---

## Questions for the User — Mandatory-DS lock under honor mode (2026-04, Round 7)

New business rule from User: **If any "honor previous verification" settings are enabled, no new mandatory data source can be added after the first successful verification.** Optional data sources
can still be added/removed; mandatory data sources can be made optional; existing mandatory entries can be removed; but **no new mandatory entries** may be introduced once honor is enabled and the
campaign has at least one successful verification on record.

Rationale: under honor mode, prior honor-eligible verifications would silently fail the consuming campaign's *current* mandatory list (Round 6 / Q5 decision) if mandatory grew, degrading candidate
experience and analytics consistency.

### Open questions

1. **What counts as the "first successful verification" that triggers the lock?** — @Product_Manager
  1. **Decision (User, 2026-04):** **(a) The first fresh verification that satisfies the then-current mandatory list** — i.e. the first record marked `Verified` per the tightened Round 6 / Q2
     definition. Partial cookies and honored receipts do **not** trip the lock on their own. — @User
2. **Does the lock also forbid promoting an existing optional data source to mandatory?** — @Product_Manager
  1. **Decision (User, 2026-04):** **(a) Yes** — promoting an optional data source to mandatory is treated the same as adding a new mandatory and is forbidden once the lock engages. — @User
3. **Honor-mode toggle interaction.** — @Product_Manager
  1. **Decision (User, 2026-04):** **(a/c) The lock engages when `honor_mode = same_campaign_only` AND the campaign has ≥ 1 fully-verified record.** Switching to `always_verify_new` unlocks
     mandatory additions; switching back to `same_campaign_only` re-engages the lock based on verifications recorded at that moment. The lock is honor-state-driven, not a one-way ratchet. — @User
4. **Scope of the rule across honor mode values.** — @Product_Manager
  - **Proceeding with assumption:** Lock applies whenever any honor mode that honors prior verification is enabled. In the current canonical set (D40) that is only `same_campaign_only`. If a future
    honor mode is added, the rule extends to it by definition.
  - **If wrong**: would need to scope by enum value rather than by capability.
5. **Where the lock is enforced.** — @Product_Manager
  - **Proceeding with assumption:** Both backend validation (authoritative) and frontend disablement (UX). Backend rejects with `400` and structured reason code `MANDATORY_LOCKED_HONOR_ENABLED`;
    frontend disables "add mandatory"/promote controls and shows an explanatory tooltip.
  - **If wrong**: drop frontend-side disablement and rely on API error toast only.
6. **Removing an existing data source entirely.** — @Product_Manager
  - **Proceeding with assumption:** Allowed. Removal strictly relaxes the configuration: a mandatory entry can be removed (which is equivalent to demoting then deleting), and an optional entry can
    always be removed. Historical analytics integrity is preserved separately by the historical-snapshot rule already in the spec.
  - **If wrong**: would need to require two-step `mandatory → optional → remove` flow, or block removal entirely once verifications exist.

---

## Questions for the User — Mandatory data sources (2026-04, Round 6)

These questions cover a new requirement: defining one or more **mandatory data sources** on a verification campaign whose successful authorization gates which provider outcome link is used as the
post-verification `return_url` (completed vs qc).

### Inventory of impacted concepts (breadth-first pass)

To make sure we cover the full breadth before going deep, the new requirement touches each of these existing concepts. Each item below has at least one question against it.

1. `data_sources` (campaign-level list) — needs a new "mandatory" subset relationship.
2. Existing `min_authorizations_for_return` (CampaignData) — described by user as "suggestive, drives minimal functionality"; relationship to the new rule is unclear.
3. Definition of **"Verified"** candidate state (Definitions section) — currently includes any candidate with ≥1 successful data source authorization (fresh or honored). The new rule re-defines
   "completed verification" against the mandatory list.
4. **Per-provider row metrics** (`Ver%`, `Try%`, `Err/Req%`, `Invited`) — depends on `Verified` definition.
5. **Aggregate pie charts** by data source — depends on which slices count and on `Verified` definition.
6. **Verification cookie issuance** (AC13) — currently issued whenever verification "completes." Needs alignment with the new completed-verification definition.
7. **Honor evaluation** (AC8/AC10/AC15) — does honoring a prior verification satisfy the consuming campaign's mandatory DS list?
8. **Historical data source completion rule** (Definitions / AC7d) — when re-evaluating "data source completion" on return visits, does the historical mandatory list also apply?
9. **Provider qc outcome link** (required) — mandatory-DS routing can safely target qc because every provider must have it configured.
10. **Per-invite `return_url` override** (AC52) — does an explicit override always win, or does the mandatory-DS routing override the override?
11. **Wireframe / edit-mode UX** (AC36/AC36a) — where is the mandatory DS list configured.
12. **Data source removal from `data_sources`** — what happens to mandatory entries pointing at a removed source.

### Open questions

1. **Mandatory-DS quantity semantics.** Does "min quantity of mandatory verifications" mean (a) **all** configured mandatory data sources must be successfully authorized; (b) any **N of M** mandatory
   sources, where N is a separately configured min count; or (c) something else? — @Product_Manager
  1. **Decision (User, 2026-04):** **(a) All mandatory must be authorized.** The mandatory list itself is the threshold; "min quantity of mandatory verifications" equates to the count of items in
     the mandatory list. There is no separate min-count knob within mandatory. — @User
2. **Reconciling the "completed verification" definition.** The current spec defines `Verified` as ≥1 authorized data source (fresh or honored). The new requirement implies a candidate who has only
   authorized non-mandatory sources is **not** "completed." Three options to choose from: (A) `Verified` is redefined to require mandatory satisfaction (when a non-empty mandatory list exists); (B)
   `Verified` keeps the current definition (≥1 source) and we introduce a **new state** "Fully Verified" that gates only the return link; (C) something else. — @Product_Manager
  1. **Decision (User, 2026-04):** **(A) Tighten `Verified`.** A candidate is `Verified` only when (i) the campaign's mandatory list is non-empty and all mandatory data sources are successfully
     authorized, OR (ii) the mandatory list is empty and ≥ 1 data source is authorized. Per-provider metrics and pie charts reflect this tighter definition. — @User
3. **Impact on per-provider analytics and pies.** If we choose option (A) above, `Ver%` and pie chart slice counts will change for any candidate who only authorized optional sources. Confirm whether
   that is desired, or whether analytics should keep the looser ≥1-source meaning while only the **return link** is gated. — @Product_Manager
  1. **Resolved by Q2 decision:** analytics are gated by the tightened `Verified` definition. — @User
4. **Verification cookie issuance with mandatory unmet.** When a candidate has authorized ≥1 source but **not** satisfied mandatory DS, should the platform still (a) issue a verification cookie
   (AC13), (b) suppress cookie issuance until mandatory is satisfied, or (c) issue a "partial" cookie that is not honor-eligible? — @Product_Manager
1. **Decision (User, 2026-04):** **(c) Issue a "partial" cookie that is recorded but is NOT honor-eligible. It can be upgraded to a fully honor-eligible cookie when the candidate later
   satisfies mandatory.** — @User
2. **Reaffirmed (User, 2026-05, Round 10 / D58):** Upgrade is performed **in place** on the **same invite/session (`sgid`)** when the candidate authorizes the entries currently missing against
   the campaign's **current** mandatory list. **AC55** / **D46d** updated accordingly; the temporary "never upgraded in place" wording from a 2026-04 simplification draft is reverted. — @User
5. **Honoring vs mandatory DS.** When a candidate is **honored** (UC3, AC8) into the consuming campaign, does the prior verification's **historical** data source set need to satisfy the consuming
   campaign's **current** mandatory DS list, or does honoring always treat the candidate as "completed" regardless? — @Product_Manager
  1. **Decision (User, 2026-04):** Honoring is allowed only if the prior verification's authorized sources cover the consuming campaign's **current** mandatory list. Otherwise honor cannot
     complete the verification on its own. — @User
     5b. **Honor partial coverage.** When a same-campaign cookie covers SOME of the current mandatory list but not all, what happens? — @Product_Manager
  1. **Initial decision (User, 2026-04):** Honor what's covered, top-up the rest. — @User
  2. **Revised decision (User, 2026-04, after Round 7 lock analysis):** **Disqualify the cookie entirely; candidate must complete fresh verification of all mandatory sources.** Top-up was
     removed because, under the Round 7 lock, the only paths that produce a partial-coverage cookie are narrow transitional cases (feature rollout, honor-mode toggle); the additional partial-
     honor receipt + linkage machinery isn't justified by the candidate experience benefit in those cases. — @User
6. **Return-visit blocked path (AC7d) interaction.** AC7d blocks a return visit when historical data source completion exists but no eligible cookie is present. With mandatory DS configured, should
   a return visitor whose **historical completion did not satisfy the historical mandatory list** be allowed back into verification to finish mandatory sources, or remain blocked per AC7d? —
   @Product_Manager
  1. **Decision (User, 2026-04):** **AC7d is unchanged.** Any historical data-source completion blocks re-verification on a return visit, regardless of whether the historical mandatory list was
     satisfied. The blocked path remains the single exit; mandatory DS does not relax this guard. — @User
7. **Provider qc link missing.** **Resolved by updated required-fields policy:** qc link is mandatory for providers, so this branch is invalid by configuration and does not need runtime fallback
   logic.
   — @Product_Manager
8. **Relationship to existing `min_authorizations_for_return`.** That field today is described as suggestive UI behavior (controls when the return button is visible). Do we (a) keep it as a separate
   UI-visibility knob unchanged, (b) deprecate it in favor of the new mandatory-DS rule, or (c) merge them into a single concept? — @Product_Manager
  - **Proceeding with assumption:** **Keep as a separate UI-visibility knob unchanged.** `min_authorizations_for_return` continues to control when the in-flow return CTA becomes visible to the
    candidate (suggestive). Mandatory DS is a separate authoritative concept that governs **which** outcome link (completed vs qc) the candidate is routed to and the campaign's `Verified`
    definition. Both can coexist; if the user wants to deprecate `min_authorizations_for_return`, that is a separate cleanup decision.
  - **If wrong**: would deprecate `min_authorizations_for_return` and use mandatory-list cardinality (all-or-nothing) as the only completion gate.
9. **Where mandatory DS is configured.** Confirm that the mandatory DS list is configured at the **verification campaign** level (alongside `data_sources`), is editable only in campaign edit mode
   (AC36a), and is **not** per-provider. — @Product_Manager

- **Proceeding with assumption:** Confirmed. `mandatory_data_sources` is a campaign-level field, edited only in campaign edit mode (AC36a-style gate), and is not per-provider. ~~Provider-level~~
  **Campaign–provider assignment** outcome links are **per `(spgid, cmp)`** (**D49**, supersedes D33/D37 link placement); mandatory DS sits at the campaign layer because it is a property of the
  verification job, not the provider identity row.
10. **Validation rules for the mandatory list.** Confirm: (a) mandatory list must be a strict subset of `data_sources`; (b) the empty list is allowed and means "all optional"; (c) duplicates rejected;
    (d) when a data source is removed from `data_sources`, any matching entry is also removed from mandatory. — @Product_Manager
  - **Proceeding with assumption:** All four rules confirmed. (a) Subset of `data_sources` enforced at save time. (b) Empty list = all optional = today's behavior. (c) Duplicates rejected at save
    time. (d) Removing a source from `data_sources` cascades a removal from `mandatory_data_sources` (no orphan mandatory entries).
11. **Per-invite `return_url` override (AC52) precedence.** Today an invite-level `return_url` override always wins over the provider's completed link. With the new rule, does an explicit override
    (a) always win regardless of mandatory satisfaction, (b) win only when mandatory is satisfied (otherwise route to provider qc link), or (c) be ignored entirely so the mandatory-DS rule always
    chooses between provider completed/qc links? — @Product_Manager
  1. **Decision (User, 2026-04):** **(a) Per-invite override always wins.** AC52 is unchanged. Callers that set an explicit `return_url` are responsible for their own post-verification routing
     beyond Taxiway's completed-vs-qc selection; Taxiway does not second-guess explicit overrides. The mandatory-DS routing rule applies only when the invite has no `return_url` override (i.e.
     defaults to a provider outcome link). — @User
12. **All-optional behavior re-confirm.** When the mandatory list is empty, the return link is the provider's **completed** link iff at least one data source has been successfully authorized. Confirm
    this matches the existing behavior and there is no change for that case. — @Product_Manager
  - **Proceeding with assumption:** Confirmed. Empty mandatory list reproduces today's behavior verbatim (≥ 1 authorized source ⇒ provider completed link). No regression for campaigns that don't
    adopt mandatory DS.

## Questions for the architect

### @Architect — DDD / bottom-up domain model (answered)

- **Deliverable:** `candidate_providers_architecture.md` — bounded contexts, ubiquitous language, bottom-up aggregates (existing Session/Invite/Campaign/Verification → extensions), new
  `CandidateProvider` and honor/cookie/return-visit services, read-model notes for the verification campaign card, survey explicitly excluded.
- **Bottom-up anchor:** Today’s production verification = session-scoped **`DataSource`** flows + **`SessionDataEvent`** + **`Verification`** rows; the spec adds **`spgid`**, honor policy,
  verification cookie, return-visit routing, and analytics — modeled as extensions and new roots, not a replacement stack.
- **PM-facing invariant:** Survey campaigns and survey invites remain **out of scope** for this feature’s bounded contexts; handoff is **`return_url`** only.

---

## Architect answers — 2026-04 (round 1)

Recorded in `candidate_providers_architecture.md` (canonical). Summary of decisions for traceability.

> **Reconciliation note (Round 8 / D48):** Items below that reference **SuperMarketer**, the **`SuperMarketerGlobalConfig`** singleton, the `super_marketer_global_config` table, the
> `/admin/super-marketer-config` endpoint, the **Taxiway Operations Governance** bounded context as it pertains to SuperMarketer, the M2 supermarketer provisioning step, and the internal
> Taxiway-ops SuperMarketer admin UI are **superseded by D48** and must be removed from `candidate_providers_architecture.md`. Backfill (UC12 / `/admin/customers/{id}/backfill-spgid`) and the
> default-provider provisioning portions of M2 remain in scope. — @Product_Manager

### A1. Bounded contexts (Architect)

Six contexts: **Candidate Provider Catalog**, **Verification Campaign** (extends `Campaign`), **Invite & Landing** (extends `Invite`/`Session`), **Verification Reuse** (new — receipt + cookie +
honor), **Verification Campaign Analytics** (new read-model), **Taxiway Operations Governance** (SuperMarketer + backfill).

### A2. New aggregates (Architect)

- `CandidateProvider` (root) with value object `OutcomeLinks` (https-only, server-side templated; AC32a/AC32b).
- `SuperMarketerGlobalConfig` (singleton) — Option A: per-customer SuperMarketer rows project shared display/links from this singleton (ADR-CP-7).
- `VerificationReceipt` (root) — **separate** from existing AI-Q&A `Verification` table to keep concerns clean (ADR-CP-1). Anchors anti-tamper (AC14), historical snapshots (AC45), honored-from-fresh
  links (AC17/AC17a).
- Domain services: `HonorEvaluator` (AC15 ordered pipeline) and `ReturnVisitRouter` (AC7 series).

### A3. Reused aggregates (Architect)

- `Campaign` extended with `honor_mode`, `honor_freshness_days`, derived `cgid` column (ADR-CP-2, ADR-CP-4).
- `Invite` extended with denormalized `spgid`/`cgid` columns; `customer_id NOT NULL`.
- `Session` extended with `completion_snapshot` value object (ADR-CP-5) for AC7d/AC45 historical truth without join under landing latency.
- Existing `Verification` (AI) untouched.

### A4. Data model (Architect)

New tables: `candidate_providers`, `super_marketer_global_config`, `campaign_provider_assignments` (ADR-CP-3 — separate table for AC51/analytics joins), `verification_receipts`. Migration order M1–M8
covers M2 default+supermarketer provisioning per existing customer (AC22/AC24) and M5 `spgid` backfill on legacy invites/sessions to default-provider `spgid` (UC12, AC53).

### A5. API contract (Architect)

- Customer scope: `/providers` CRUD; `/campaign/{cmp}/providers` assign / quick-add / unassign; `/campaign/{cmp}/verification-card` projection; `PUT /campaign/{cmp}` extended with honor fields;
  `POST /invite` accepts optional `spgid` (default-provider fallback).
- New canonical landing: `GET /invites/new?cgid&ref_id&spgid&…context` — single handler implements AC1–AC7d. Legacy `/session/new` remains during transition.
- Operations scope: `/admin/super-marketer-config` (UC11) and `/admin/customers/{id}/backfill-spgid` (UC12) — separate from customer OAuth scope.
- Internal: `POST /v1/event/verify` extended to write `VerificationReceipt(mode=fresh)`, capture `completion_snapshot`, issue cookie (AC11/AC13).

### A6. Event contract (Architect)

Three new event types on existing `DataEventPublisher` topology:

- `CandidateProviderEvent`
- `CampaignAssignmentEvent`
- `VerificationReceiptEvent` (incl. `verification_completed`, `verification_honored`, `return_visit_blocked`)

`return_visit_blocked` additionally writes structured application log per Observability section / AC7d.

### A7. Frontend reconciliation (Architect)

- Customer UI: provider catalog page (UC5/UC6), campaign edit extensions (UC1/UC7/UC8 + honor controls — AC36/AC36a/AC37), read-only verification campaign card (UC4 — AC34/AC39–AC50), invitees page
  extension (AC49). Server returns `editable` / `removable` flags so UI controls follow the model (AC38/AC38a).
- Internal Taxiway-ops UI (new, separate scope): SuperMarketer admin form (UC11) reusing the same outcome-link form component.

### A8. Constraints, ADRs and trade-offs (Architect)

ADR-CP-1..8 captured in architecture document. Key trade-offs:

- Extra `verification_receipts` table (clear separation from AI Q&A — ADR-CP-1).
- Materialized `cgid` column on `campaigns` (O(1) landing lookup — ADR-CP-2).
- Separate assignments table (efficient AC51/analytics joins — ADR-CP-3).
- Reuse `Campaign` aggregate, no new `VerificationCampaign` (ADR-CP-4).
- Server-owned outcome-link rendering per brainstorm Option A (ADR-CP-8).

### A9. Out-of-scope flags reaffirmed (Architect)

Hash-collision mitigation, query-param size governance, partner cookie reuse, deprecation calendar for legacy `/session/new` links — all remain out of scope per business spec.

