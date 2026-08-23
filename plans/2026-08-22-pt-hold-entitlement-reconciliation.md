# Plan: PT Hold Entitlement Reconciliation Guard

**Created:** 2026-08-22
**Status:** Implemented
**Request:** Preserve SGPT hold processing while replacing PT daily-proration assumptions with a fail-closed, session-entitlement reconciliation proposal for approval in the existing GHL Conversation.

---

## Overview

### What This Plan Accomplishes

This plan separates date-based SGPT hold billing from appointment-based PT hold reconciliation. It adds a local, side-effect-free engine that maps paid and skipped PT payments to service-week appointments, detects boundary errors, and emits only a proposed one-to-one entitlement transfer for human approval in the existing GHL Conversation.

### Why This Matters

PT payments purchase discrete coached sessions, so daily Stripe proration can compensate the wrong thing and can double-credit a member. A session-aware guard protects both the member's paid entitlement and the business from duplicate cash/session compensation while keeping complaints, exceptions, and ambiguous evidence with a human.

---

## Current State

### Relevant Existing Structure

- `stripe_handler/app.py` exposes the shared `/stripe/pause-hold` endpoint and currently applies daily overlap credit to both Membership and PT holds.
- `outputs/systems/membership-hold.md` documents the shared Hold OS workflow and the current daily Stripe overlap credit.
- `outputs/systems/personal-training.md` documents PT calendars, packages, and the shared hold workflow.
- `context/policies.md` establishes that PT is paid at least one week in advance and that cancellations/forfeitures have distinct policy treatment.
- `plans/2026-04-13-hold-return-journey-workflow.md` records the original date-based design rationale.

The delegated brief also names `AGENTS.md`, `plans/2026-07-31-ghl-conversation-clearance-controller.md`, `outputs/systems/conversation-clearance-control.md`, and `outputs/systems/inbound-communications.md`. Those files are absent from this checkout and cannot be treated as verified repository instructions or implementation dependencies.

### Gaps or Problems Being Addressed

- PT holds use the SGPT daily-proration algorithm even though PT value is delivered as discrete appointments.
- The handler cannot identify a paid appointment inside a hold or a return appointment unfunded by a skipped weekly payment.
- There is no duplicate-credit guard spanning a carried session and a Stripe customer-balance credit.
- There is no structured, side-effect-free proposal that an existing GHL Conversation clearance controller can present for human approval.
- There are no automated tests for PT hold boundaries.

---

## Proposed Changes

### Summary of Changes

- Add a pure PT entitlement reconciliation module with strict input validation and deterministic classifications.
- Require an existing GHL Conversation ID and emit a note/work-item payload without creating a task or tracker.
- Route PT requests at `/stripe/pause-hold` through the proposal guard before any Stripe lookup or mutation.
- Preserve the existing SGPT date-based Stripe pause and overlap-credit path.
- Add a dedicated local `/stripe/pt-hold/reconcile` proposal endpoint for controller integration and testing.
- Fail closed on missing/irregular evidence, appointment exceptions, policy-sensitive flags, count mismatches, and prior cash/session adjustments.
- Add unit and Flask integration tests, including Jody Burke's exact boundary case.
- Update canonical hold and PT system documentation, plus `CLAUDE.md` because the workspace gains a new handler module and test suite.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `stripe_handler/pt_entitlement_reconciliation.py` | Pure validation, classification, funding allocation, duplicate-credit checks, and proposal generation. |
| `stripe_handler/tests/test_pt_entitlement_reconciliation.py` | Unit coverage for safe and fail-closed reconciliation cases. |
| `stripe_handler/tests/test_app.py` | Integration coverage for routing and the no-mutation PT boundary. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `stripe_handler/app.py` | Branch Membership and PT processing; add proposal endpoint; leave Membership mutation logic intact. |
| `outputs/systems/membership-hold.md` | Correct the automation boundary and document PT approval/reconciliation flow. |
| `outputs/systems/personal-training.md` | Document evidence inputs, classifications, transfer semantics, and exception handling. |
| `context/business-info.md` | Qualify shared billing dates as SGPT calculations and PT control dates. |
| `plans/2026-04-13-hold-return-journey-workflow.md` | Add a PT-only supersession warning to the historical daily-credit design. |
| `CLAUDE.md` | Add concise references to the reconciliation module and tests. |
| `plans/2026-08-22-pt-hold-entitlement-reconciliation.md` | Record implementation status, verification, deviations, and rollout plan. |

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Hold dates are inclusive service dates:** appointments before the start are pre-hold, dates from start through end are in-hold, and later dates are post-hold.
2. **PT never uses daily proration:** a PT request cannot reach the Stripe customer-balance credit branch.
3. **Payments fund service windows, then appointments:** a validated billing-to-service offset opens a cadence-length service window; each cadence payment must map to exactly `sessions_per_payment` appointments.
4. **Manual/pack entitlements require explicit appointment mapping:** they are not inferred from a recurring cadence.
5. **Only exact one-to-one reconciliation is safe:** the number of paid in-hold appointments must equal the number of post-hold appointments uncovered by skipped payments; mismatches are human-review-only with no transfer.
6. **Proposal, never execution:** local code returns a deterministic proposed action and GHL Conversation note payload. It cannot post a note, create a task, transfer a session, credit Stripe, pause billing, send a message, or deploy.
7. **Existing Conversation is mandatory:** a missing conversation ID fails closed, and the payload explicitly states that no new task/tracker should be created.
8. **Prior adjustment evidence is mandatory:** any existing cash credit or entitlement transfer touching a candidate blocks automatic proposal to prevent duplicate benefit.
9. **Policy-sensitive states fail closed:** cancellations, no-shows, forfeitures, makeup sessions, billing exceptions, complaints, medical/safety issues, and policy ambiguity require human judgement.

### Alternatives Considered

- **Continue daily proration for PT:** rejected because a fraction of a billing interval is not a reliable representation of a scheduled PT session.
- **Automatically execute transfers after inference:** rejected because appointment status and policy exceptions require human approval.
- **Create a separate task or spreadsheet tracker:** rejected because the existing GHL Conversation is the required single work item.
- **Pair as many appointments as possible when counts differ:** rejected because partial reconciliation can hide missing evidence or duplicate compensation.

### Open Questions (if any)

- The absent conversation-clearance controller documents must be reconciled before live integration. The local output contract will be deliberately connector-neutral until those canonical files are available.
- The production source and schema for appointment, payment, and prior-adjustment evidence must be validated before rollout.

---

## Threat and Failure Analysis

| Threat / failure | Consequence | Local control | Rollout control still required |
| --- | --- | --- | --- |
| PT request reaches SGPT daily-proration code | Wrong cash credit; possible double benefit | Explicit hold-type branch before Stripe lookup; unknown types return 400 | Shadow-log hold-type values before enabling branch |
| Hold boundary interpreted as exclusive | Wrong source/target appointment | Inclusive date comparisons covered by Jody test | Compare shadow results with coach/admin records |
| Billing control date treated as debit/service date | Wrong payment-to-appointment mapping | Funding uses payment date + validated offset; control dates are labels only | Evidence adapter must pull actual payment status/date |
| Cadence drift or duplicated payment | False entitlement inference | Exact interval and unique ID validation | Human must resolve plan migrations and billing exceptions |
| Missing appointment around either boundary | Hidden source or target | Every relevant payment window must contain the declared session count | Evidence adapter must query a sufficiently wide boundary window |
| Manual charge or upfront pack inferred as recurring | Wrong funded sessions | Non-cadence payments require explicit appointment IDs | Operator must validate pack balance/expiry evidence |
| Cancelled, forfeited, makeup, or no-show session treated as transferable | Policy breach | Unsupported/policy-sensitive statuses fail closed | Human applies signed agreement and discretion |
| Existing Stripe credit plus proposed carried session | Duplicate compensation | Any existing adjustment evidence blocks proposal; PT never enters daily-credit branch | Query pending and completed adjustments immediately before approval/execution |
| Candidate counts differ | Partial reconciliation hides missing evidence | No partial pairing; mismatches return `review_required` | Human investigates source/target gap |
| Missing/duplicate GHL work item | Fragmented audit trail | Existing `conversation_id` required; output forbids task/tracker creation | Clearance controller must post only to that Conversation |
| Stale evidence changes after proposal | Approved action no longer matches reality | Proposal performs no mutation | Approval executor must re-read evidence and use an idempotency/version check |
| Replayed/spoofed webhook | Unauthorized billing action | PT path is non-mutating | Authenticate webhook and add request idempotency before any live execution path |
| Complaint, cancellation, medical/safety, or policy ambiguity | Harmful automated decision | `risk_flags` fail closed | Controller must source flags from the Conversation and contact state |

---

## Step-by-Step Tasks

### Step 1: Define the Pure Reconciliation Contract

Create a module that parses dates and validates hold boundaries, cadence, service offset, sessions per payment, existing conversation identity, appointments, payments, and prior adjustments.

**Actions:**

- Use JSON-compatible dictionaries at the boundary and stable result codes in the output.
- Keep the module free of Stripe, GHL, network, environment, and database dependencies.
- Return `proposal_ready`, `no_transfer_needed`, or `review_required` with evidence and reasons.

**Files affected:**

- `stripe_handler/pt_entitlement_reconciliation.py`

### Step 2: Implement Funding and Boundary Classification

Classify appointments and map cadence-relevant payments to appointment windows.

**Actions:**

- Validate the combined paid/skipped schedule against the declared cadence.
- Map paid service windows and skipped service windows to appointments.
- Require exact appointment counts in every relevant payment window.
- Identify paid in-hold sources and skipped-payment-unfunded post-hold targets.
- Generate deterministic one-to-one transfers only when counts match and no exception exists.

**Files affected:**

- `stripe_handler/pt_entitlement_reconciliation.py`

### Step 3: Integrate Without Enabling Live Mutation

Separate the existing endpoint by hold type.

**Actions:**

- Keep the current Membership/SGPT Stripe path unchanged.
- Route PT to the reconciliation engine before Stripe lookup.
- Add `/stripe/pt-hold/reconcile` as a proposal-only endpoint.
- Return the existing GHL Conversation work-item payload and an explicit `mutations_performed: []` audit field.

**Files affected:**

- `stripe_handler/app.py`

### Step 4: Add Automated Tests

Cover the entitlement engine and endpoint boundary.

**Actions:**

- Test Jody's dates, four skipped payments, paid 10 September source, and 8 October target.
- Test aligned holds, partial-week safe transfer, irregular cadence, missing appointments, count mismatch, cancellation/makeup/forfeiture flags, and duplicate cash/session credit.
- Verify PT requests never call Stripe and never claim a mutation.
- Verify Membership requests retain the legacy Stripe branch.

**Files affected:**

- `stripe_handler/tests/test_pt_entitlement_reconciliation.py`
- `stripe_handler/tests/test_app.py`

### Step 5: Update Canonical Documentation

Correct the hold and PT system documentation so future operators do not apply the SGPT algorithm to PT.

**Actions:**

- Separate SGPT date-based calculations from PT session-based reconciliation.
- Document required evidence, fail-closed conditions, proposal fields, GHL Conversation ownership, approval boundary, and duplicate-credit prohibition.
- State that current local work is not deployed and no live workflow has been changed.
- Add concise workspace pointers to `CLAUDE.md`.

**Files affected:**

- `outputs/systems/membership-hold.md`
- `outputs/systems/personal-training.md`
- `CLAUDE.md`

### Step 6: Verify and Record Rollout Controls

Run syntax, unit, integration, and diff checks, then update this plan.

**Actions:**

- Run the complete local unittest suite.
- Compile the handler modules.
- Inspect the diff for secrets and unintended live-operation code.
- Record a staged rollout: shadow proposals, evidence comparison, approval UI/controller integration, test-mode execution, limited production pilot, and monitored expansion.

**Files affected:**

- `plans/2026-08-22-pt-hold-entitlement-reconciliation.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `context/business-info.md`
- `context/policies.md`
- `plans/2026-04-13-hold-return-journey-workflow.md`
- `outputs/systems/membership-hold.md`
- `outputs/systems/personal-training.md`
- `outputs/systems/cancellation-system.md`
- `stripe_handler/app.py`

### Updates Needed for Consistency

- Remove claims that standard PT holds are fully automated without manual review.
- Limit daily overlap credit language to Membership/SGPT holds.
- Make the GHL Conversation the sole PT review surface once the missing controller is present.

### Impact on Existing Workflows

No live workflow is changed in this task. If this code is later deployed, Membership/SGPT requests retain their existing behavior; PT requests stop before Stripe mutation and require the clearance controller/human approval path to complete billing pause and any entitlement transfer.

---

## Validation Checklist

- [x] Jody's exact case proposes only `10 Sep 2026 → 8 Oct 2026` with no cash adjustment.
- [x] Aligned, partial-week, irregular-cadence, missing-appointment, count-mismatch, and duplicate-credit tests pass.
- [x] PT endpoint tests prove zero Stripe calls and zero performed mutations.
- [x] SGPT endpoint test proves the legacy branch still performs its expected Stripe operations.
- [x] Documentation clearly separates SGPT and PT logic and identifies the human approval boundary.
- [x] No live contact, billing, appointment, membership, workflow, automation, or communication is mutated.
- [x] No deployment is performed.

---

## Success Criteria

1. The local handler cannot silently apply both a PT entitlement carry and a Stripe credit.
2. Complete, regular evidence produces deterministic boundary classification and safe one-to-one proposals.
3. Ambiguous or policy-sensitive evidence produces `review_required` and no proposed/attempted mutation.
4. The result is suitable for attachment to an existing GHL Conversation without creating another work item.
5. Automated tests and canonical documentation cover the acceptance and failure cases.

---

## Notes

The local implementation is a guard and proposal generator, not a rollout. Live evidence adapters, GHL Conversation posting, approval capture, Stripe pause execution, and appointment entitlement mutation remain separately controlled rollout work requiring Peter's approval.

### Rollout / Migration Plan

1. Restore and review the missing conversation-clearance controller plan and canonical inbound/clearance documentation; adapt the connector-neutral work-item payload to that verified contract.
2. Build read-only adapters for Stripe payment status, PT appointment records, plan cadence/offset, manual/pack mappings, prior adjustments, and Conversation risk flags.
3. Run in shadow mode with no posts or mutations; compare at least one full hold cycle against human reconciliations, including Jody-like partial boundaries.
4. Add authenticated webhook requests, evidence version/freshness checks, deterministic reconciliation IDs, and execution idempotency.
5. With Peter's separate approval, post internal proposals to the existing GHL Conversation only. Keep human approval mandatory and member communications disabled.
6. In Stripe test mode and non-live appointment fixtures, verify approval, rejection, stale-evidence recheck, retry, and duplicate-execution behavior.
7. Pilot on a small set of regular-cadence PT holds under manual dual review. Do not include packs, irregular cadence, exceptions, complaints, cancellations, or medical/safety cases.
8. Reconcile every pilot outcome against Stripe, appointments, and the Conversation audit record before expanding. Maintain an immediate rollback to the manual PT process.

---

## Implementation Notes

**Implemented:** 2026-08-22

### Summary

- Added a pure PT entitlement engine with inclusive boundary classification, cadence/service-window mapping, exact one-to-one transfer proposals, and fail-closed evidence checks.
- Branched the shared hold endpoint before Stripe lookup so PT cannot receive the SGPT daily overlap credit; unknown hold types also fail before mutation.
- Added a proposal-only endpoint and existing-GHL-Conversation work-item contract with no task/tracker creation and `mutations_performed: []`.
- Added 14 unit/integration tests, including Jody's exact boundary, aligned and partial boundaries, cadence/appointment failures, policy/billing exceptions, duplicate credit, unknown type, and Membership regression coverage.
- Updated canonical hold/PT documentation and the workspace map.
- Qualified the shared business billing context and marked the historical hold plan's PT daily-credit logic as superseded.

### Verification Results

- `STRIPE_API_KEY=sk_test_local_only /tmp/pt-hold-test-venv/bin/python -m unittest discover -s stripe_handler/tests -v` — **14 passed**
- `python3 -m py_compile ...` for the handler, engine, and tests — **passed**
- `git diff --check` — **passed**
- No deployment, live API call, contact/workflow update, billing/appointment mutation, or member communication was performed.

### Deviations from Plan

- The delegated brief's `AGENTS.md`, conversation-clearance controller plan, conversation-clearance system doc, and inbound-communications system doc do not exist in this checkout. No substitute behavior was invented. The implementation emits a connector-neutral existing-Conversation note contract that must be reconciled with those canonical documents before live integration.
- The local Python environment did not contain Flask/Stripe, so the pinned runtime dependencies were installed only in `/tmp/pt-hold-test-venv` to execute integration tests; no dependency lock or runtime version was changed.

### Issues Encountered

- The first integration run exposed that the legacy endpoint requires an email before hold-type branching; the acceptance fixture was corrected to match the webhook contract.
- The aligned fixture initially retained Jody's skipped return-week payment, correctly producing a count mismatch. It was corrected so the aligned scenario has a paid return service week and therefore requires no transfer.
