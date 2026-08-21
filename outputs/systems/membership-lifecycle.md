# Membership Lifecycle System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-08-05 (positive-call and consent-based referral rule live in Drive, the restricted course and the published GHL workflow)

---

## Overview

The Membership Lifecycle System covers the full journey of a member from the moment they sign up through their first week, first month, first 90 days, and beyond. It operates across four layers:

1. **Onboarding & Agreement** — Membership Agreement Form, current PAR-Q, and initial welcome communications
2. **Lifecycle Nurture Sequences** — A working first-week sequence followed by incomplete or inactive lifecycle workflow shells
3. **Membership Pipeline** — Tracks membership and PT service classifications. The live middle-tier stage is now named Strong, Fit & Flexible Membership, matching the recurring client-facing offer name.
4. **Membership Change Workflows** — Manages mid-lifecycle plan changes including upgrades to PT or Hybrid/Online variants

The intended lifecycle spans 365 days, but only `Membership: First 7 Days` is verified as operational. `Membership: Day 29-90` was unpublished on 30 July 2026 after revalidation confirmed it had no trigger and no enrolments in the latest 30-day history. The remaining windows (Day 8–28, Day 91–180, Day 181–365) are unfinished drafts without triggers.

The initial operational handoff is governed by `reference/sops/post-sale-member-onboarding.md`. The assigned consultant completes it before the member leaves, and Admin Eve independently verifies the result by day two.

The Day 7–9 reply handoff is governed by `reference/sops/first-week-member-reply-follow-up.md` and the Drive SOP [SOP - First-Week Member Reply Follow-Up](https://docs.google.com/document/d/16j5ez3IzPjWMKFuMr3spBvF2hXd0aXYLOmPlRJeYTfo/edit?usp=drivesdk). Admin Eve owns the written reply and review-workflow state; the designated Retention Manager owns the personal follow-up and GHL outcome record. Role-specific training is kept outside the general trainer pathway in the standalone GHL course [Retention Manager: First-Week Member Follow-Up](https://app.gohighlevel.com/v2/location/6Ku1uU0Xc45zq0KlTikJ/memberships/courses/course-creator-studio?view=manager&sub_view=outline&product_id=8b37345d-fca8-4549-b979-3a47cdc5785e). Its free offer remains in Draft so access can be granted only to the named Retention Manager or approved management cover.

---

## Cross-System Membership Control

The Membership Pipeline is a CRM workflow surface, not a complete current-member register. A membership status is considered reconciled only when the applicable evidence agrees across:

| Control surface | Operational purpose |
|---|---|
| GHL | Contact identity, lifecycle tags, service classification and workflow state |
| Stripe or approved external payer | Commercial entitlement and billing evidence |
| Trainerize | Current coaching-app access |
| Brown & Casserly Pty Ltd 2026 | Staff-maintained `Active SGPT`, `Active PT`, `SGPT Cancellations` and `PT Cancellations` roster |
| Private reconciliation record | Owner decisions, identity links, exceptions and verified change evidence |

No single signal authorises account activation or deactivation. Staff, online clients, prepaid-credit clients and externally billed clients must be recorded as explicit approved exceptions rather than treated as errors.

An owner-approved cancellation or status correction is not closed until GHL lifecycle state, Trainerize access and the relevant Brown & Casserly tab have been checked. Stripe is never changed merely to make the systems agree. If a historical cancellation date cannot be evidenced, leave the date blank and retain an audit note rather than assigning the cleanup date and distorting monthly KPIs.

The manual service downgrade standard is defined in `reference/sops/active-client-payment-and-booking-reconciliation.md`. It requires one idempotent effective-date transition across billing, GHL, appointments, active and cancellation roster tabs, Trainerize and reporting, followed by a verified member confirmation sent from `admin@theevolvegym.com.au` in GHL.

The recurring Trainerize reconciliation is read-only and creates an evidence-backed review queue. Any future write action requires separate approval, an exact allowlist, expected-state checks and post-write verification.

Runbook: `outputs/systems/trainerize-reporting-reconciliation.md`

### Returning-member reactivation control

The published `3.0 New Member` workflow is reserved for first-time onboarding. On 29 July 2026, **Allow re-entry** was disabled and the saved published state was verified. Re-applying any of its legacy plan trigger tags (`limited`, `silver` or `bronze`) must not restart the workflow for a contact who has already completed it.

For a returning member, reconcile the existing contact rather than recreating onboarding:

1. Confirm identity across GHL, Stripe or the approved payer, Trainerize and the operational workbook.
2. Confirm the intended plan, price, billing start and saved payment method before creating a subscription.
3. Keep the returning-member evidence tag (`old member`) in place while the plan tag is applied.
4. Verify that `3.0 New Member` did not enrol the contact and that no welcome SMS, First 7 Days enrolment or review-request action fired.
5. Replace `old member` with `member`, update the Membership Pipeline directly to the current plan stage, reactivate Trainerize and complete the remaining reconciliation surfaces.

If the contact has no verified historical `3.0 New Member` execution, do not rely on the re-entry setting alone. Pause the workflow during the controlled tag change or add an explicit eligibility guard before proceeding.

---

## Pipeline: Membership Pipeline

**Pipeline ID:** `fkEvrFkTihYkdb3bpprd`

| Position | Stage | ID |
|---|---|---|
| 0 | Online Only | `22019d21-0efd-4604-9a83-5608c0776735` |
| 1 | Fit & Flexible | `edaf6054-486a-473d-be37-e5f9bcde0dd9` |
| 2 | Strong, Fit & Flexible Membership | `81aab141-2d01-4cdb-9d25-ee949f36098b` |
| 3 | Fast Track | `a1e8d561-91ec-4d95-a8ea-98ea2e129142` |
| 4 | Gold | `27bf02d9-74fd-4ee2-a1e0-b515b76fba79` |
| 5 | PT Only | `58247f13-4a47-40f8-8289-35d62fc138b3` |
| 6 | PT 1 p.wk | `9ce28fb1-f43b-472a-ac11-1b4c147b202b` |
| 7 | PT 2 p.wk | `01d615da-4bd4-4bf3-a5c6-54332588367d` |
| 8 | PT 3 p.wk | `edf7f617-e058-438a-978a-330fa262ef8e` |

The live audit on 20 July 2026 found 129 records in this pipeline: Online Only 1, Fit & Flexible 1, Strong, Fit & Flexible Membership 75, Fast Track 13, Gold 0, PT Only 19, PT 1 p.wk 5, PT 2 p.wk 15 and PT 3 p.wk 0.

The pipeline currently mixes Open and Won statuses inside the same service-classification stages. This weakens its value as a current-membership register. Decide whether the pipeline represents current service ownership, historical sale conversion, or both; then standardise statuses and retirement rules.

The `Strength & Sculpt` stage was renamed to `Strong, Fit & Flexible Membership` on 21 July 2026 without changing stage ID `81aab141-2d01-4cdb-9d25-ee949f36098b`. The pipeline-level Save action was completed and a full reload confirmed that the new label persisted, so existing workflows continue targeting the same stage ID.

---

## Tags

| Tag | Purpose |
|---|---|
| `member` | Active member flag — applied at sign-up |
| `online client` | Member on Online Only plan |
| `gold` | Member on Gold plan |
| `personal training` | Member receiving PT |
| `pt only` | PT-only member (no group membership) |
| `1 p.wk` | PT frequency: 1 session per week |
| `2 p.wk` | PT frequency: 2 sessions per week |
| `3 p.wk` | PT frequency: 3 sessions per week |
| `1 p.fn` | PT frequency: 1 session per fortnight |
| `old member` | Previous member — used for win-back targeting |
| `oldmember` | Legacy version of old member tag |
| `old pt client` | Previous PT client |
| `weekly checkin` | Member is on a weekly check-in schedule |
| `irregular` | Member with irregular attendance pattern |
| `terminated` | Membership terminated |
| `trial` | Member on trial or 7-day trial |
| `7 day trial` | Specifically on 7-day trial |

---

## Calendars

| Calendar | Type | ID | Notes |
|---|---|---|---|
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` | Booked at start of membership |
| Intro Session - Megan | personal | `tc9BC56PdRNQGQmY0CgN` | Trainer-specific intro session |
| Intro Session - Leisa | personal | `UTOhZ4UA8XDPYEZend4p` | Trainer-specific intro session |
| Intro Session - Katrina | personal | `pPu3BfzgdKgKYGlYGeAX` | Trainer-specific intro session |
| Intro Session - Piper | personal | `Nbzw8JiElSyeXdDqBLnQ` | Trainer-specific intro session |
| Injury Triage - Megan | personal | `Knee8V0fRcHxmpu3W0Fb` | Used when health/injury flagged during onboarding |

The **On-boarding Session** calendar is the primary onboarding touchpoint. Trainer-specific **Intro Session** calendars are used when the member is assigned to a specific coach for their first session.

Live verification on 23 July 2026 confirmed that every documented Beth and Hannah calendar ID, including `Injury Triage - Hannah`, is already absent from GHL. No deletion was required.

---

---

# PART 1: New Member Onboarding

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| 3.0 New Member | **published** | `c1321609-733a-42af-8d7b-88a11945974e` |
| Membership Agreement Form: Email | **published** | `355337b6-14fc-4c00-b9e7-3b0794a391aa` |
| Membership: First 7 Days | **published; positive, negative and unclear-reply task wording plus all Day 7–9 timing controls saved and verified 5 August 2026** | `10f3c717-1443-427c-8264-b2348a32a448` |
| Test - First 7 Days | draft; unpublished 17 July 2026 | `d6dd7a5f-4818-4530-b17c-ffa7001b7489` |

> **Note:** `Test - First 7 Days` was the predecessor to the live first-week sequence. It was confirmed as legacy and unpublished on 17 July 2026.

### Live Task Audit: updated 5 August 2026

The original 17 July review found no Create Task actions in the seven onboarding workflows reviewed. On 22 July, `Membership: First 7 Days` was upgraded with assigned Admin Eve and Piper Mae tasks on its Day 7, Day 8 and Day 9 reply paths. The other reviewed onboarding workflows still have no verified persistent operational tasks.

The broader onboarding system still relies mainly on messages, data movement and internal notifications. The first-week reply handoff is now the exception: it creates persistent team tasks so both written-response ownership and in-person follow-up are visible and accountable.

On 5 August 2026, Peter expanded the positive follow-up into a prompt phone call. The approved task wording is to thank the member, build rapport, check her Google review status and make a natural referral invitation when appropriate.

Referral details may be recorded and used only after the member provides a warm introduction or confirms that the referred woman has agreed to be contacted. The positive task remains open until the call note and any agreed referral follow-up are recorded.

All 15 Day 7–9 reply tasks now use a one-day offset, 5:00 pm and `Skip weekends`. The three positive Piper tasks were changed from seven days to one day, saved and read back in the published workflow on 5 August 2026.

All three negative Piper Mae tasks require a prompt phone call, a structured internal note under `Notes`, continuing contact attempts when the member is not reached and owner escalation when the issue cannot be remedied without owner intervention. All three unclear-reply Admin Eve tasks use plain human wording and keep the task open when management clarification is genuinely required.

GHL's built-in `Run a test` panel was inspected on 5 August. It can only select a contact and run the complete workflow from the beginning; it cannot start at Day 7, inject an inbound reply or force the Positive, Negative or None branch. A three-case branch run was therefore not submitted because it would execute real onboarding communications and waits without proving the intended branch. Configuration-level verification is complete; runtime branch acceptance remains pending the next genuine cases or a safe staging capability.

The active `3.0 New Member` workflow explicitly adds contacts to `Membership: First 7 Days`. That published workflow is the canonical first-week version; `Test - First 7 Days` is not part of the verified handoff.

### Live continuation audit: 21 July 2026

`3.0 New Member` still routes members using the internal legacy tags `bronze`, `silver`, `gold`, `2 p.wk`, `1 p.wk` and `limited`. Each live service branch sends its plan-specific SMS messages, adds the Review Request tag and enrols the member into `Membership: First 7 Days`. Recent execution logs confirmed the Bronze path successfully performed both handoffs.

Historical execution confirms that the First 7 Days workflow has processed recent contacts through its reply waits and internal notifications, so the Drive `New Member: 7 Day Check In Response` note describes a real staff handoff rather than an abandoned process. The upgraded workflow was saved on 22 July 2026 and its status remained Publish.

Implemented 22 July 2026: the Day 7, Day 8 and Day 9 reply paths each use GHL AI Intent Detection on `{{message.body}}`. The premium action costs USD $0.01 per classified reply and produces Positive, Negative and None branches. The three previous single Admin Eve notifications were removed, and no automated member acknowledgement was added.

Positive and Negative branches each create separate assigned tasks for `Admin Eve` and `Piper Mae`. Admin Eve owns the written response, review-workflow state and internal handoff note. Piper owns a prompt phone call for both outcomes. A positive call thanks the member, builds rapport, checks review status and can create a consent-based referral opportunity; a negative call listens, records the support outcome and escalates issues that require owner intervention. Negative branches also remove the contact automatically from `Google Review Request (4 & 5 Stars Only)` before its Day 14 message.

The None branch creates an Admin Eve clarification task. Admin reads what the member shared and decides the human handoff: positive experiences receive an encouraging Piper note; concerns are removed from the review pathway and handed to Piper for a prompt call. If the correct handoff is genuinely unclear, Admin leaves the task open and asks management rather than guessing. The separate Day 9 no-reply branch remains unchanged.

One mapping has now been confirmed, while the live repair remains outstanding:

- Peter confirmed on 22 July 2026 that the legacy `limited` / `1 p.wk` service branch represents the current Fit & Flexible offer. On 24 July, its incomplete `Create Or Update Opportunity` action was repaired by assigning the Fit & Flexible Membership Pipeline stage. The workflow warning cleared and the published workflow was saved. Preserve the legacy tag until a separate dependency-checked relabelling migration is approved.
- The workflow begins with `Remove from Studio Appointment Workflow`, although the Studio Appointment acquisition asset is no longer part of the live system. Dependency-check and remove or relabel that action during the onboarding rebuild.

The only failed execution in the visible 22 June to 21 July log was a `Remove Opportunity` attempt where the contact had no opportunity in the target pipeline. The remainder of that contact's onboarding continued; treat this as an idempotency/no-match condition unless repeated errors show an actual handoff failure.

---

## Forms & Surveys

| Form / Survey | Type | ID |
|---|---|---|
| Membership Agreement Form | Form | `CstPVJqXXbOVTarkr7tg` |
| PAR-Q | Form | `yziUG4EO90xQMtBx5xU1` |
| Pre-Exercise Form | Deleted legacy form; historical fields retained | `tUmSYWgC90QLMHycVotC` |

The Membership Agreement Form captures plan selection, debit details and signature. The current `PAR-Q` captures the health screen and is the form linked by the production Strength Assessment flow. The separate zero-submission `Pre-Exercise Form` was deleted on 31 July 2026 after dependency verification; it was not the current onboarding form.

---

## New Member Onboarding Flow (Step by Step)

```
1. Member signs up after a Strength & Longevity Assessment or approved direct membership pathway
2. "3.0 New Member" workflow fires
3. Contact placed into Membership Pipeline at correct stage (plan type)
4. "Membership Agreement Form: Email" workflow fires → member receives agreement link
5. Member completes Membership Agreement Form → plan, debit date, signature captured
6. Member completes current PAR-Q → health screening captured
7. "Membership: First 7 Days" workflow fires (Day 1 trigger)
8. Welcome sequence begins — onboarding education, gym orientation, coach introduction
9. Member books Onboarding Session via On-boarding Session calendar
```

---

## Membership Agreement: Custom Fields

**Field Group:** `e3OeSDdsc8ZCJGnBKLL0`

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Membership Type | MULTIPLE_OPTIONS | `Fit & Flexible`; `Strong, Fit & Flexible`; `Fast Track Package` | `1SgYibtlIuophn9FYAh8` |
| Today's Upfront Cost Is | MULTIPLE_OPTIONS | $299 / $399 / $599 | `KX6dFWysypvQ2ju5Y21g` |
| Regular weekly debit amount (starts in week 4 for week 5) | MULTIPLE_OPTIONS | $69 / $99 / $149. Renamed in GHL on 23 July 2026; the existing merge key remains unchanged for dependency safety | `d5Ig4OX79xc90WDYbdrN` |
| First Debit Date Is | DATE | — | `4agatus8jm9HUfBaRqJE` |
| Membership Agreement Date Signed | DATE | — | `1WWilN82DxffsOdgKV2Y` |
| Acknowledgement of Terms Initial | TEXT | Member initials acknowledging terms | `YlRqSMojFrvy7xvD6VWe` |
| Signature | SIGNATURE | Member sign-off on agreement | `a9vPpSzxm4YVHF9Z5uPd` |
| PT Agreement Date Signed | DATE | Populated when PT agreement also signed | `m7XNn6iutAoI4br2QUXu` |
| PT Agreement: Initial (24hrs Notice to Reschedule) | TEXT | Member initials on PT cancellation terms | `iQfRvYyyX2uwI1m7XTx1` |
| PT Agreement: Initial (30 Days Notice to Cancel) | TEXT | Member initials on PT notice period | `apLeFgJVKLuMIe8EKBjz` |

**Field Group:** `9klbgmldALQR9VbYrMr8` (General / Compliance)

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Email Opt In | CHECKBOX | Consent to receive emails | `elb56bw7b0ffyU55uo67` |
| Pick the most relevant stage of life | RADIO | Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause | `gKk8C5noKS1Gs81vKafA` |
| Where do you currently live? | MULTIPLE_OPTIONS | Brisbane / Gold Coast QLD / Elsewhere in QLD / NSW / VIC / TAS / SA / NT / ACT / WA / Outside Australia | `OzgRHzKYJmkppezLjkL4` |
| PT Block Service | TEXT | Type of PT block service | `Upyxa5ORrkYuzKmB9ikp` |
| PT Block Start | DATE | Start date of PT block | `qoSPND4o6aOmyMesj6Xs` |
| PT Block Trainer | TEXT | Assigned trainer name for PT block | `gSYaeeCF2iiRSzJhKePT` |

The three April 2024 Impact Call qualification and attendance-commitment fields were previously misclassified in this section as membership compliance fields. They had no membership purpose or stored contact values and were deleted after owner approval on 31 July 2026; an immediate GHL inventory read-back verified all three IDs absent.

---

## Current PAR-Q: Custom Fields

**Primary field group:** `gtONzqe4vAWTrnJKf6ly`

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Emergency Contact | TEXT | Name and phone | `wLxj7gtob8AQdgJYSE0X` |
| PARQ: Heart Condition | RADIO | Yes / No | `q8dzu0PQanP6cOvtv5CS` |
| PARQ: Chest Pain During Activity | RADIO | Yes / No | `DXu8HCFQNLmiawTlR5SE` |
| PARQ: Chest Pain At Rest | RADIO | Yes / No | `lXD4wUR5TcpJ7sWhgKQM` |
| PARQ: Dizziness or Loss of Consciousness | RADIO | Yes / No | `TDvFZB9Sb9Iz0EY8tvc2` |
| PARQ: Bone or Joint Problem | RADIO | Yes / No | `RovVdadVvY0jOe3A2kTU` |
| PARQ: Blood Pressure or Heart Medication | RADIO | Yes / No | `uLyyvozTzfv0POL93b1T` |
| PARQ: Any Other Reason | RADIO | Yes / No | `sxMsDNfn3U5DHv7cCQ3f` |
| PARQ: Signature | SIGNATURE | Member signature | `LzNvvzOLV6d0mIEVpWUI` |
| PARQ: Confirmation | CHECKBOX | Accuracy and participation consent | `mZx7Zkb1bF4y8N7n077Q` |

---

The former seven-day free-training checkbox (`3cyRKn2OjCJY6zrKHCZd`) was not present on either the current PAR-Q or legacy Pre-Exercise Form and had zero stored values. It was deleted with three other health/event-era orphan fields on 31 July 2026 and verified absent; it is not a current onboarding field.

The separate `SMS/Txt Opt In` custom field (`qGZnum0zTEiFsFvzV5AV`) had zero stored values and no current form, survey, template or supported workflow-metadata consumer. It was deleted on 31 July 2026 after owner approval and verified absent; it was not the live 30DNNC consent field.

The deleted legacy Pre-Exercise Form used eight older screening/confirmation fields plus two River-to-Rooftop intake fields, all populated on the same three historical event contacts. Post-deletion reads confirmed all ten definitions and their values remain intact; preserve them unless a separate data-retention decision is made.

---

# PART 2: Membership Lifecycle Nurture Sequences

---

## Workflows

| Workflow | Status | ID | Window |
|---|---|---|---|
| Membership: First 7 Days | **published; positive-call and one-day positive-task update pending authenticated live sync** | `10f3c717-1443-427c-8264-b2348a32a448` | Days 1–7 |
| Membership: Day 8-28 | draft; no trigger; unfinished | `c3587248-8934-471a-8ec1-f7b0191cee4c` | Days 8–28 |
| Membership: Day 29-90 | Draft rebuild shell; unpublished 30 July 2026 | `f0f639f9-ab49-4f7e-990b-02d8ca8dfeab` | Days 29–90 |
| Membership: Day 91-180 | draft; no trigger; empty | `151fca2f-2aca-4567-91f2-630b8d4e4766` | Days 91–180 |
| Membership: Day 181-365 | draft; no trigger; empty | `9785ee0b-c987-4816-897c-796d6c7e5273` | Days 181–365 |

Publication is not evidence of operation. The live 22 July audit found no recent enrolments in Day 29–90 and no trigger capable of enrolling contacts automatically.

### Live lifecycle audit: 22 July 2026, Class B revalidated 29 July 2026

- `Membership: Day 8-28` contains a five-minute wait and goal branches for Lose Weight, Tone Up, 300% Stronger and Postpartum, but the branches contain no messages and the workflow has no trigger. It is draft and had no enrolments in the available 30-day history.
- `Membership: Day 29-90` waits 76 days, then uses GHL Review Request actions for SMS and email. It has no trigger and had no enrolments in the available 30-day history, so these review requests are not currently being sent through this workflow.
- `Membership: Day 91-180` and `Membership: Day 181-365` each contain only an empty action placeholder and no trigger.
- At the time of the 22 July audit, `Follow Up Monthy` was published with 65 historical enrolments, zero active contacts and no enrolments in the available 30-day history. It had no trigger and only moved an opportunity to `[WARM] Sales Pipeline / FUM - Follow Up Monthly`; it did not perform a member check-in. It was set to Draft and renamed `FUM: Assessment Education & Reassessment Journey` on 30 July.
- No workflow name matching `weekly`, `satisfaction`, `milestone`, or `t-shirt` exists in the live workflow register. The `weekly checkin` tag exists, but this audit found no named automation implementing it.

The practical result is a working first-week check-in followed by no verified automated member-development sequence. Treat the Day 8–365 workflows as design shells rather than live retention infrastructure.

The 29 July Class B revalidation reopened the complete builders, settings and available 30-day enrolment histories. `Membership: Day 29-90` still contains only Wait 76 Days, Review Request SMS and Review Request Email; it has no trigger, no recent enrolments and no Add-to-Workflow handoff from the complete `Membership: First 7 Days` action set. `Follow Up Monthy` still contains only the deprecated Create or Update Opportunity action targeting `[WARM] Sales Pipeline / FUM - Follow Up Monthly`; it has no trigger and no recent enrolments. Its Allow re-entry and Allow multiple opportunities settings are both on, but cannot create enrolments without an upstream call, manual enrolment, API or integration. These settings do not change the inert classification.

The 30 July dependency check confirmed that the former `Follow Up Monthy` is not part of the live No Sale handoff. The published `2.5. No Sale - Follow Up` has its own `Update Opportunity to FUM` action targeting the same pipeline and stage. It had one contact actively progressing and several recent completed July enrolments. The WARM pipeline currently contains zero open opportunities. The FUM stage was preserved, while the separate workflow was unpublished and retained in Draft under its new assessment-education name for a governed rebuild.

---

## Supporting Workflows (Lifecycle-Adjacent)

| Workflow | Status | ID | Purpose |
|---|---|---|---|
| 3.1. New Personal Training Client | **published; upstream-enrolled; one-time** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` | Receives first-time PT onboarding contacts from another workflow; re-entry and multiple-opportunity execution are disabled |
| Google Review Request (4 & 5 Stars Only) | **published** | `ebbd43c1-4e39-4731-a3e3-c7e5f0bfae0b` | Sent to satisfied members to generate reviews |
| Goal: Lose Weight | **published; disconnected and dormant** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` | Legacy one-email asset superseded by the planned SA Pre-qual AI Agent |
| Goal: Tone Up | **published; disconnected and dormant** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` | Legacy one-email asset superseded by the planned SA Pre-qual AI Agent |
| Goal: 300% Stronger | **published; disconnected and dormant** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` | Legacy one-email asset superseded by the planned SA Pre-qual AI Agent |
| Goal: Strength For Life | **published; disconnected and dormant** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` | Legacy one-email asset superseded by the planned SA Pre-qual AI Agent |
| Goal: Postpartum Glow Up | **published; disconnected and dormant** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` | Legacy one-email asset superseded by the planned SA Pre-qual AI Agent |
| Strength Assessment: Nurture | **published** | `2abf0af9-25be-40dc-935e-51c92a6798b0` | Nurture sequence post-Strength Assessment |

---

---

# PART 3: Membership Change Workflows

---

## Overview

Membership changes are service transitions, not new acquisitions. Two form families exist:

- **Evolved Anywhere/Online Only retention change**: a member moves from an in-gym service to Evolved Anywhere or Online Only to preserve an appropriate level of training support
- **PT Agreement**: a member adds or changes a PT package

Evolved Anywhere and Online Only are confirmed legitimate retention services. The PT change path remains separate because its pricing is still proposed.

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Membership Agreement Form: Email | **published** | `355337b6-14fc-4c00-b9e7-3b0794a391aa` |
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` |

> The two Agreement Form: Email workflows do not process these membership-change surveys. Their live triggers are restricted to the standard `Membership Agreement Form` and `Personal Training Agreement Form`. No dedicated membership-change fulfilment workflow was found.

---

## Surveys (Membership Change Forms)

| Survey | ID | Purpose |
|---|---|---|
| Membership Service Change Variation | `zFxqvzogSZFbeGDnNM8Q` | Published review variation for Evolved Anywhere or Online Only; member send and automatic fulfilment remain gated |
| Membership Change: PT Agreement Form | `w8j2Hc5KRu7MCYBEnmKb` | Captures PT package choice and signature for PT upgrade/change |

---

## Membership Service Change Variation Custom Fields

**Field Group:** `AyOGhcB2nXpQBt1LsAqO`

| Field | Type | Options | ID |
|---|---|---|---|
| MCHO: Plan Choice | RADIO | Evolved Anywhere \| 1 PT every 4 weeks + Personalised Programming (A$69/week) / Online Only \| Evolved Programming Only (A$27/week) | `Vbv1EHS1IbGJKHplBHeo` |
| MCHO: Initial Online Only Terms | TEXT | Member initials confirming online-only terms | `2DNdB9zWbM2jFxnk9zmz` |
| MCHO: Signature | SIGNATURE | Member sign-off on change | `3CFg8eyc3OTWhPsnGyq0` |

The two dedicated Membership Service Change surveys now reuse the signature field, while the Online Only survey also uses the Online Only terms initial. The combined `MCHO: Plan Choice` field is no longer a live form input. It is retained as a read-only migration bridge because it holds genuine historical choices for Sue Goodwin, Tania Stiles and Peter Brown plus one controlled acceptance-test record; do not write new service changes to it.

---

## Membership Change: PT Agreement Custom Fields

**Field Group:** `wcVp5BsbhFXgkyeLpiPj`

| Field | Type | Options | ID |
|---|---|---|---|
| MCPT: PT Choice | RADIO | The Standard Strength Package ($120 p/wk) / The Optimal Results Package ($180 p/week) | `tw73Uz4jCyb4gxwCEKLy` |
| MCPT: Signature | SIGNATURE | Member sign-off on PT agreement | `lPQ96chOfOsFTCfMBcUX` |

---

## Membership Change Flow

```
Trigger and staff handoff are not implemented
   │
   ▼
Staff may manually send a change survey:
   │
   ├── Evolved Anywhere/Online Only Change
   │     → Membership Service Change Variation sent after final owner review
   │     → Member selects: Evolved Anywhere (A$69/wk) or Online Only (A$27/wk)
   │     → Member signs → MCHO fields populated
   │     → No native notification, autoresponder or verified workflow handoff
   │
   └── PT Upgrade / Change
         → Membership Change: PT Agreement Form survey sent
         → Member selects: Standard Strength ($120/wk) or Optimal Results ($180/wk)
         → Member signs → MCPT fields populated
         → No native notification, autoresponder or verified workflow handoff
```

---

### Live membership-change audit: 30 July 2026

Both survey canvases and their all-time submission histories were inspected. Native email notification and autoresponder switches are off on both surveys.

The survey retains two historical submissions. Sue Goodwin signed on 22 May 2026 and Tania Stiles signed on 2 July 2026 under the legacy `Hybrid | 1 PT p/mth + Personalised Programming ($69 p/week)` value. The PT change survey has zero submissions from 1 January 2024 through 30 July 2026.

The published `Membership Agreement Form: Email` workflow triggers only from `Membership Agreement Form`. The published `PT Agreement Form: Email` workflow triggers only from `Personal Training Agreement Form`. Neither trigger includes the membership-change surveys, so a signed change survey only writes its fields unless staff notice and process it manually.

The review variation was rebuilt and published on 30 July 2026:

- Evolved Anywhere is A$69 per week and Online Only is A$27 per week.
- Both selections have explicit routing rules, and public tests proved that each opens only its own terms.
- The Privacy Policy and Terms of Use point to `https://theevolvedgym.com.au/legal`.
- Tania alone temporarily retains up to three Strength Group PT sessions per month under her documented historical promise; that exception is not part of the standard service.
- The PT survey presents `$120 p/wk` and `$180 p/week` packages without defining session duration or frequency, while PT pricing remains proposed.

The variation states the new service, price, effective boundary, inclusions, exclusions, booking and support rules, and the policies that change while preserving unchanged terms from the original agreement.

Admin Eve owns the transition. A signed variation must fail closed across GHL, billing, Trainerize, appointments, operating workbooks and reporting before the member receives a completion confirmation.

### Historical reconciliation

- **Sue Goodwin:** her signed Hybrid change has already been reconciled as the current `$69` Evolved Anywhere service across GHL, Stripe, Trainerize, Active Online and reporting.
- **Tania Stiles:** her signed `$69` legacy selection and signature persist in GHL. Stripe now has one active paid A$69 weekly Evolved Anywhere subscription and the prior A$99 service ended at the 5 August boundary. Canonical GHL service fields, the obsolete tag and the Active Online projection are corrected, and the stale Active SGPT row is removed while Sales history remains. Trainerize's legacy SGPT programme and All Stars membership are removed, but the personal plan is expired with no current training plan and six non-expiring group/class credit balances still permit app self-booking. Monday is the only agreed appointment detail; trainer, time and delivery mode remain missing, no future monthly appointments exist, and the duplicate GHL identity remains unresolved. Acceptance stays blocked under the single open exception.

Implementation is scoped in `plans/2026-07-30-membership-service-change-control.md`.

### Service-change control build: 30 July 2026

The dedicated GHL Contact folder `6. Membership Service Change` now contains 22 governed request, agreement, surface-status and canonical-service fields. The older `MCHO` fields remain historical evidence and are not the current-service projection.

The Evolved Operating Data Hub now accepts immutable version 1 requested events and version 2 accepted or exception events. It rejects changed replays, concurrent pending requests, premature acceptance and incomplete surface state; exact retries are idempotent.

Billing OS now has a read-only service-change verifier. It proves the exact current subscription, target weekly amount and Brisbane effective boundary without mutating Stripe.

The published Membership Service Change variations remain non-authoritative for current service. The governed survey-to-request handoffs now exist as disabled GHL workflows: Evolved Anywhere `f92bde55-73ba-4147-a842-ce53814540ed` and Online Only `dcd08689-755b-41af-9e8c-e2eccb2d8198`. Online Only also has a verified A$27 AUD weekly Stripe price and the live Billing OS scheduler is deployed.

Both workflows were live-read back on 5 August as Draft. Online Only passes its controlled Trainerize execution with the approved one-way access and standard program. The stuck Evolved Anywhere pending purchase was removed through Trainerize and re-sold on the same product and profile; the replacement is Active with one-way access and the existing personal program preserved. Both synthetic profiles were deactivated and verified in the Deactivated view. Tania's exact live Stripe boundary and paid A$69 entitlement are reconfirmed; her stale Active SGPT row is removed and Active Online remains correct. The existing Admin Eve exception now records the remaining split identity, expired personalised plan, app-bookable class credits and missing trainer/time/mode agreement. Member send and automatic fulfilment remain disabled until one clean six-surface accepted event passes.

Admin Eve's operating procedure is `reference/sops/membership-service-change-control.md`.

---

---

# Full Onboarding Journey Flow

```
[Sale Closed]
      │
      ▼
[3.0 New Member workflow fires]
      │
      ├── Contact added to Membership Pipeline (correct stage)
      ├── member tag applied
      └── Service-plan branch and onboarding actions run
      │
      ▼
[Membership Agreement Form: Email workflow fires]
      │
      ▼
[Member completes Membership Agreement Form]
      │  Membership Type, Upfront Cost, Weekly Debit, First Debit Date, Signature
      │
      ▼
[Member completes current PAR-Q]
      │  PAR-Q health screening, fitness goals, trainer selection
      │
      ▼
[Onboarding Session booked]
      │  On-boarding Session (30 Mins) calendar
      │
      ▼
[Day 1–7: Membership: First 7 Days — PUBLISHED]
      │  Welcome, gym orientation, app/platform access,
      │  coach introduction, early wins, FAQs
      │
      ▼
[Day 8–28: Membership: Day 8-28 — DRAFT]
      │  Habit reinforcement, consistency prompts, early check-in
      │  (may not be active)
      │
      ▼
[Day 29–90: Membership: Day 29-90, DRAFT REBUILD SHELL]
      │  No trigger. If manually or externally enrolled, waits 76 days
      │  and sends GHL review requests by SMS and email.
      │
      ▼
[Day 91–180: Membership: Day 91-180 — DRAFT]
      │  Mid-membership engagement, goal reassessment,
      │  upgrade / add-on prompts (PT, extra sessions)
      │  (may not be active)
      │
      ▼
[Day 181–365: Membership: Day 181-365 — DRAFT]
      │  Long-term loyalty, referral prompts,
      │  anniversary recognition, review request
      │  (may not be active)
      │
      ▼
[Google Review Request (4 & 5 Stars Only)]
      │  Triggered at appropriate satisfaction point
      │
      ▼
[Decision Point]
      ├── Stays active → cycles through ongoing nurture
      ├── Membership Change → MCHO or MCPT survey sent, pipeline stage updated
      ├── Hold Request → Hold OS pipeline (see hold system documentation)
      └── Cancellation → Cancellation OS pipeline (see cancellation system documentation)
```

---

## System Notes & Observations

### What's working well
- **Agreement form captures all commercial terms in one step** — Membership Type, upfront cost, weekly debit, first debit date, and signature are all in a single form, reducing back-and-forth
- **The current PAR-Q is integrated into onboarding and the Strength Assessment flow** — health screening flags clearance requirements before physical assessment or training
- **Goal-specific nurture content already exists** — useful copy or story references from the five dormant one-email workflows can seed the planned AI pre-qualification story library
- **Membership Pipeline gives a useful CRM view of plan distribution** across all 9 membership tiers including PT frequency breakdown, but it must be reconciled against billing, Trainerize access and the operational workbook
- **MCHO and MCPT surveys standardise plan change agreements** with digital signatures, providing the same legal protection as the initial agreement
- **Stage-of-life segmentation is built in** — perimenopause, postpartum, teen, and pregnancy-planning members can receive tailored content from the moment they join

### Current gaps / things to review
- **Broader onboarding task handoffs remain incomplete** — first-week reply ownership now uses assigned tasks, but account setup, Trainerize access, coach assignment and onboarding-session booking still rely on manual practice or notifications that can be missed
- **Legacy goal nurture is intentionally not being reconnected** — the live assessment workflow captures a free-text goal reply and adds only `Goals Submitted`; the planned SA Pre-qual AI Agent will replace the five dormant one-email sequences with primary-goal clarification, structured capture, relevant story matching and a trainer brief. Archive the legacy workflows only after that path is live and dependency-tested
- **Days 8–365 are not operational retention infrastructure** — Day 8–28 is an unfinished goal-branch shell; Day 29–90 was unpublished and retained as a rebuild shell; Days 91–180 and 181–365 are empty drafts. These need a coherent lifecycle design, valid entry and exit rules, staff ownership, reply handling and measurable outcomes before any workflow is published
- **No governed Membership Service Change control exists** — Hybrid and Online Only are legitimate retention services, but the current signed survey only writes contact fields. It does not govern the effective date or reconcile GHL, billing, Trainerize, recurring appointments, workbooks and reporting. The required variation and fail-closed control are scoped in `plans/2026-07-30-membership-service-change-control.md`
- **Sue Goodwin exposed the cross-surface service-change gap on 28 July 2026** — Gmail and Stripe proved a completed change from Strong, Fit & Flexible to the A$69 Evolved Anywhere hybrid service, while GHL still showed the SGPT pipeline stage and a stale `Pending Hold`, Active Online used the generic `Online Only` label and Sales showed Trainerize provisioning as incomplete. The owner-approved correction aligned those surfaces without creating a cancellation or SGPT/PT roster row. The future self-mending controller must treat a signed service-change selection plus matching current commercial entitlement as a proposed lifecycle transition, then verify the GHL stage, hold status, service roster and provisioning flags together.
- **Membership: Day 29–90 needs rebuilding and a valid entry path** — it is now safely held in Draft with no trigger and no recent enrolments
- **No win-back or lapsed member re-engagement workflow visible** — the `old member` tag exists but there is no automated sequence targeting lapsed or churned members beyond the short-term cancellation retention pathways. A 30/60/90-day post-cancellation win-back sequence is not documented
- **PT Block fields (Service, Start, Trainer) are free-text TEXT fields** — no standardisation makes reporting on PT block performance by trainer or service type unreliable. Converting to structured field types (SINGLE_OPTIONS for Trainer, RADIO for Service) would improve reporting accuracy
- **Stage-of-life capture uses two governed variants** — `gKk8C5noKS1Gs81vKafA` (group `9klbgmldALQR9VbYrMr8`, options include "Post Partum") contains 457 historical answers. `tGaGYawO3Q4AAPnuznF7` (group `GuiXAoJoZHSIaS669O8A`, options include "Postpartum") is the transient 30DNNC capture field and had zero stored contact values on 31 July 2026, but remains a live form/workflow dependency. Both feed the canonical `Lead: Life Stage` field through workflow normalisation; neither capture field should be deleted until its source form is rebuilt.
- **Membership Type field is valid but visually ambiguous in flat exports** — the MULTIPLE_OPTIONS field (`1SgYibtlIuophn9FYAh8`) contains three options: `Fit & Flexible`, `Strong, Fit & Flexible`, and `Fast Track Package`. The comma belongs to the middle membership name; it is not a duplicate delimiter
- **Stripe retains a different internal product label** — the canonical client-facing and Membership Pipeline name is now `Strong, Fit & Flexible Membership`, while Stripe still uses `Sculpt & Strength`. The Stripe product can remain unchanged for now; preserve this explicit mapping in billing documentation.
- **Weekly debit field label corrected** — renamed in GHL on 23 July 2026 to `Regular weekly debit amount (starts in week 4 for week 5)`. The $69 / $99 / $149 values and existing `contact.weekly_debit_amount_after_30_days` merge key were preserved so dependent assets continue to resolve
