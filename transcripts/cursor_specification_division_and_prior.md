# Specification division and prioritization
_Exported on 5/1/2026 at 11:11:23 GMT+1 from Cursor (3.1.14)_

---

**User**

@specs/sample_providers/candidate_providers_business_spec.md Divide this specificaiton into 3 phases, prioritize the highest business value use cases and acceptance criteira. What is your suggestion? Ask questions if needed

---

**Cursor**

I've reviewed the spec end-to-end. Before I draft a 3-phase split, I want to confirm a couple of priorities that materially change the plan.

The spec has roughly six capability clusters:

- **A. Provider catalog & ownership foundation** — default provider, custom providers, SuperMarketer, customer-as-default backfill (UC5, UC6, UC11, UC12; AC1-AC6, AC20-AC25, AC50, AC53).
- **B. Campaign provider assignment & quick-add** — multi-provider attribution at the campaign level (UC1, UC7, UC8; AC23, AC30, AC33, AC51).
- **C. Outcome links & `return_url` handoff** — link templating, validation, per-invite override (AC18, AC27, AC32–AC32b, AC52).
- **D. Verification reuse / honor** — honor modes, freshness, cookie issuance, DB cross-check, return-visit routing (UC3, UC9, UC10; AC7–AC17a, AC26, AC36–AC37).
- **E. Read-only verification campaign card analytics** — per-provider rows, aggregate pies, near-real-time (UC4; AC34, AC39–AC46).
- **F. Invitee quick-navigation** — campaign- and provider-level deep links into invitees page (AC47–AC49).

The first decision drives everything: which of "reuse" (D) vs "analytics" (E) is the higher business priority for phase 2.

The second decision is whether each phase must be **independently shippable end-to-end** (vertical slices, each with its own UI) or whether phases can stack as **dependency-ordered foundations** (e.g., phase 1 backend-heavy, phase 3 polish/analytics).

> **Between verification reuse/honor (reduces candidate drop-off) and the read-only campaign-card analytics (operations visibility), which is higher business value and should be phase 2?**
> - Reuse/honor in phase 2, analytics in phase 3 (drop-off reduction = revenue impact) ✔
> - Analytics in phase 2, reuse/honor in phase 3 (visibility unblocks ops, validates phase 1)
> - Either is fine — pick whichever makes the cleanest dependency chain

> **How should phases be shaped?**
> - Vertical slices — every phase ships a usable end-to-end customer-visible capability ✔
> - Dependency-ordered — phase 1 lays foundation (may be mostly backend/migration), later phases add user-visible features
> - Hybrid — phase 1 must ship a minimal end-to-end capability; later phases can be more feature-focused

Good. With reuse-first and vertical-slice phasing, here's my proposed plan.

