# Plan: PT Hold Entitlement Reconciliation Guard

**Created:** 2026-08-22
**Status:** Local implementation verified; dark deployment candidate; live PT activation blocked at protected Conversation/evidence gates
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

- `stripe_handler/app.py` is the current guarded Billing OS. The production deployment still applies the legacy daily-overlap path to PT until the protected PT gate is separately activated.
- `outputs/systems/membership-hold.md` documents the shared Hold OS workflow and the current daily Stripe overlap credit.
- `outputs/systems/personal-training.md` documents PT calendars, packages, and the shared hold workflow.
- `context/policies.md` establishes that PT is paid at least one week in advance and that cancellations/forfeitures have distinct policy treatment.
- `plans/2026-04-13-hold-return-journey-workflow.md` records the original date-based design rationale.

The canonical Conversation controller plan and system documents are present and were reviewed. They keep GHL Conversations as the sole work item, prohibit secondary tasks, and report shadow mode with assignment and message write gates disabled. The workflow-extension registry also records `promotion_authorised=false`; therefore the local work-item payload cannot yet be posted live.

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
2. **PT never uses daily proration after guarded activation:** when the protected PT gate is enabled, a PT request cannot reach the Stripe customer-balance credit branch. The gate defaults off so a code deployment alone cannot silently change production billing behavior.
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

### Remaining Activation Gates

- The Hub evidence adapter and production schema for payments, appointment coverage, cadence/offset, prior adjustments, risk flags and the existing Conversation ID are not implemented.
- Conversation clearance remains shadow-only, with `promotion_authorised=false` and no authorised internal-note handoff.
- The PT environment gate must remain `false` until both controls pass read-only parity and Peter separately approves the exact live handoff/activation.

---

## Threat and Failure Analysis

| Threat / failure | Consequence | Local control | Rollout control still required |
| --- | --- | --- | --- |
| PT request reaches SGPT daily-proration code | Wrong cash credit; possible double benefit | Enabled PT gate branches before Stripe lookup; unknown types fail closed | Keep the gate off for dark deployment; enable only after Hub evidence and Conversation handoff acceptance |
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

The local implementation is a guard and proposal generator, not an execution path. Live evidence adapters, GHL Conversation posting, approval capture, Stripe pause execution, and appointment entitlement mutation remain separately controlled rollout work.

### Rollout / Migration Plan

1. Deploy the candidate dark with `PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED=false`; verify health and that no GHL, Stripe, appointment or Conversation behavior changes.
2. Build a read-only Hub adapter for payment status, PT appointments, cadence/offset, manual mappings, prior adjustments, risk flags and existing Conversation identity.
3. Run proposal-only parity with no Conversation post or mutation; require complete governed evidence windows and compare against human reconciliations.
4. Add an authenticated existing-Conversation internal-note handoff, exact freshness re-read, proposal ID binding and execution idempotency. Do not create a task or tracker.
5. Obtain the exact immutable Conversation promotion authority and Peter's approval for that protected handoff; keep member messaging and all execution disabled.
6. Test approval, rejection, stale-evidence, retry and duplicate-credit behavior with non-live fixtures, then pilot only regular-cadence PT holds under dual human review.
7. Enable the PT gate only after the activation evidence is recorded. Reconcile every pilot outcome and retain immediate rollback by setting the gate to `false`.

---

## Implementation Notes

**Implemented:** 2026-08-22; reconciled onto the governed Billing OS on 2026-08-24

### Summary

- Added a pure PT entitlement engine with inclusive boundary classification, cadence/service-window mapping, exact one-to-one transfer proposals, and fail-closed evidence checks.
- Added a protected, default-off gate that branches PT before Stripe lookup so activation cannot issue an SGPT daily overlap credit; unknown hold types fail before Stripe mutation.
- Added a proposal-only endpoint and existing-GHL-Conversation work-item contract with no task/tracker creation and `mutations_performed: []`.
- Added complete-evidence windows, governed provenance, deterministic proposal IDs, delivered-session rejection and duplicate-work-item tests in addition to the original boundary suite.
- Updated canonical hold/PT documentation and the workspace map.
- Qualified the shared business billing context and marked the historical hold plan's PT daily-credit logic as superseded.

### Verification Results

- Current Billing OS regression suite — **50 passed**
- PT unit and integration suite — **17 passed**
- `python3 -m py_compile ...` for the handler, engine, and tests — **passed**
- `git diff --check` — **passed**
- At this record point no live contact/workflow, billing, appointment, membership, entitlement or member communication mutation was performed.

### Reconciliation Notes

- The original PT implementation was based on an obsolete 253-line handler. It was checkpointed, replayed onto the newest governed repository snapshot, and then reconciled with the later canonical Billing OS and test delta. The current guarded Billing OS remains the base; only the pure engine, PT branch, tests and documentation were carried forward.
- The Conversation documents are available in the governed snapshot. They confirm that no substitute task or live note writer may be invented while promotion remains unauthorised.
- The local Python environment did not contain Flask/Stripe, so pinned runtime dependencies were installed only in `/tmp/pt-hold-test-venv`; no dependency lock or runtime version changed.

### Issues Encountered

- The first integration run exposed that the legacy endpoint requires an email before hold-type branching; the acceptance fixture was corrected to match the webhook contract.
- The aligned fixture initially retained Jody's skipped return-week payment, correctly producing a count mismatch. It was corrected so the aligned scenario has a paid return service week and therefore requires no transfer.
