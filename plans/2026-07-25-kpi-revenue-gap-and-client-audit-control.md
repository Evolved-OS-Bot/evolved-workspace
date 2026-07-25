# Plan: KPI Revenue Gap and Active Client Audit Control

**Status:** Phase 1 implemented; shadow validation in progress

**Created:** 25 July 2026

**Canonical policy:** `reference/sops/active-client-payment-and-booking-reconciliation.md` version 1.8

**Reusable audit worksheet:** `outputs/systems/pt-weekly-audit-run-sheet.md`

## Objective

Build one durable, exception-led controller that reconciles Active SGPT, Active PT, cleared cash, Stripe, approved legacy payment evidence, GHL lifecycle state, expanded PT bookings and Trainerize access.

The controller must preserve the existing source systems and reuse the current reconciliation services. It must not create a competing client-status process or infer billing, cancellation or appointment changes from weak evidence.

## Current Foundation

The following components already exist:

- `scripts/membership_reconciliation.py` creates protected GHL, Stripe and Trainerize identity and entitlement snapshots.
- `pt_booking_shadow/` reconciles expanded GHL PT calendars, booking continuity, Stripe entitlement, Trainerize access and Active PT evidence.
- Brown & Casserly contains the live Active SGPT, Active PT and KPI reporting surfaces.
- `scripts/update_metrics.py` refreshes the workspace KPI snapshot.
- The canonical SOP defines identity, payment, lifecycle, booking, Fast Track, PIA, arrears and cash-bridge rules.
- GHL tasks are already used to give unresolved exceptions an owner and due date.

The missing component is a durable audit register and bridge engine that joins these inputs, retains weekly decisions and explains the difference between roster allocations and cleared cash.

## Non-Negotiable Boundaries

1. Cleared bank cash remains the authoritative actual result and is entered or confirmed manually until an approved bank feed exists.
2. Stripe is the default current receipt source. Approved PTMinder/EziDebit evidence remains a controlled legacy input.
3. Identity matches exact normalised email first, then verified phone or an approved durable legacy-email link. Names are never identity keys.
4. Active labels and active subscription states do not prove collection without successful receipt, invoice and `pause_collection` evidence.
5. GHL commencement fields remain historical evidence. Current reporting uses the approved current service, pipeline state, billing and workbook allocation.
6. Fast Track is represented as $99 Active SGPT plus $50 Active PT, while the $149 receipt is counted once.
7. `Active` and `Active - PIA` count as active membership. `Active - ARREARS` remains on the roster but is excluded from confirmed collecting income.
8. Refunds, downgrades, holds, cancellations and payment changes must align across all affected systems.
9. Every residual mismatch must contain evidence checked, classification, financial value, owner, next action and due date.
10. Sheet writes are bounded, idempotent and followed by a range re-read and duplicate-email search.

## Architecture

```text
Membership reconciliation snapshot ─┐
PT booking continuity snapshot ─────┤
Active SGPT / Active PT sheets ─────┼─> Revenue Gap Controller
Manual bank cash confirmation ──────┤       │
Legacy payment evidence register ───┘       ├─> Protected audit database
                                            ├─> Monday exception report
                                            ├─> Friday cash bridge
                                            ├─> Aggregate KPI summary
                                            └─> Owned GHL follow-up tasks
```

## Protected Audit Register

Create `data/private/revenue-gap-control/revenue_gap.sqlite`. Identified evidence stays below `data/private/`; aggregate summaries may be written to `outputs/revenue-gap-control/`.

Required tables:

| Table | Purpose |
|---|---|
| `runs` | Audit type, window, source freshness, completion and limitations |
| `client_identity` | Canonical email, verified phones, approved legacy links and source IDs |
| `roster_snapshot` | Active-sheet row, current service, status and weekly allocation for each run |
| `payment_evidence` | Rail, receipt, invoice, subscription, pause and entitlement window |
| `booking_evidence` | Future horizon, trainer, delivered sessions and cancelled-session classification |
| `lifecycle_evidence` | GHL hold, cancellation, refund, downgrade and current-service evidence |
| `pack_ledger` | PIF purchase, beneficiary, pack size, session position, adjustments and renewal threshold |
| `cash_bridge` | Actual cash, confirmed current income, scheduled run-rate, future starts and PIF sales |
| `exceptions` | Type, evidence, value, owner, next action, due date and current state |
| `decisions` | Admin-confirmed classifications and overrides with timestamps |
| `write_evidence` | Bounded workbook or GHL task writes and their post-write verification |

## Classification Model

Each client receives one service-specific classification:

- `CLEAN_COLLECTING`
- `ACTIVE_PIA`
- `ACTIVE_ARREARS`
- `APPROVED_PAUSE`
- `APPROVED_FUTURE_START`
- `PIF_PACK_IN_DELIVERY`
- `PACK_RENEWAL_DUE`
- `PAYMENT_CURRENT_NO_BOOKING`
- `BOOKING_PAYMENT_UNRESOLVED`
- `REFUND_REMOVE_FROM_ACTIVE`
- `DOWNGRADE_RECONCILIATION_REQUIRED`
- `LIFECYCLE_EXCEPTION`
- `SOURCE_READ_FAILURE`

The classification must be explainable from stored evidence. No classification can authorise cancellation, billing or appointment removal by itself.

## Cash Bridge

The controller must calculate and report these separately:

1. Full numeric SGPT allocation.
2. Full numeric PT allocation.
3. PIF rows and PIF cash sales.
4. Approved future starts.
5. Approved pauses.
6. Payment arrears.
7. Confirmed current recurring income.
8. Scheduled run-rate.
9. Actual cleared cash.
10. Named timing and correction items.
11. Remaining unexplained variance.

Normal scheduled payments fund the following service week. A late retry retains the original entitlement and is not shifted forward again.

## Implementation Phases

### Phase 1: Deterministic Read-Only Controller

1. Create a `revenue_gap_control` Python package with configuration, models, database migrations and a command-line runner.
2. Read the latest complete membership reconciliation snapshot and reject incomplete or stale source runs.
3. Read the latest complete PT booking snapshot and retain its source limitations.
4. Read bounded Active SGPT and Active PT ranges with current headers and exact row numbers.
5. Load approved identity links and legacy payment evidence from controlled private registers.
6. Ingest manually confirmed cash for an explicit entitlement window.
7. Build service-specific client records and classifications.
8. Produce a protected identified exception CSV and an aggregate Markdown summary.
9. Produce the Monday PT audit worksheet and Friday cash bridge from the same stored run.

### Phase 2: Fast Track, Pack and Lifecycle Controls

1. Pair Fast Track SGPT and PT rows by canonical identity and verify the fixed $99 plus $50 allocation.
2. Count the $149 receipt once and flag missing or duplicated allocation rows.
3. Add the controlled pack ledger and compare it with qualified `Session X/Y` appointments.
4. Add refund, downgrade, long-hold, cancellation and payment-adjustment classifications.
5. Preserve historical agreement fields while checking current GHL service markers.
6. Record the one-week-in-advance service allocation for normal payments and original entitlement for late retries.

### Phase 3: Exception Ownership and Safe Writes

1. Run read-only for three weekly cycles.
2. Compare every recommendation with Admin’s final decision.
3. Require zero incorrect cancellation, billing, refund or appointment-removal recommendations.
4. Add idempotent GHL task upsert only after the exception types and task ownership are approved.
5. Add bounded workbook correction previews with an explicit approval gate.
6. After any approved batch write, re-read the changed range and search the active sheet by email for duplicates.
7. Keep Stripe, Trainerize access and appointment writes outside this controller unless separately authorised and safety-reviewed.

### Phase 4: Scheduling and Operations

1. Event-driven targeted run within one business day of starts, failures, refunds, holds, returns, cancellations, downgrades, price changes and rail changes.
2. Monday full Active PT audit and SGPT exception review after the source snapshots are complete.
3. Friday cash close after bank cash is confirmed.
4. First Monday monthly full SGPT plus PT pack and identity audit.
5. Quarterly identity, lifecycle, tier and formula validation.
6. Trigger an additional full audit when unexplained variance remains above $99 SGPT or $120 PT after timing items, when a pause or cancellation lacks approval, when a pack sequence fails, or when the Active PT count moves without an evidenced start or exit.

## Reports

### Monday Exception Report

Include:

- source freshness and limitations;
- total Active SGPT, Active PIA, Active arrears and Active PT rows;
- new, removed and changed rows since the prior run;
- payment and booking combinations;
- trainer and booking-horizon exceptions;
- pack renewal and sequence exceptions;
- Fast Track pair exceptions;
- lifecycle contradictions; and
- every owned exception with due date.

### Friday Cash Close

Include:

- full allocation;
- confirmed current income;
- scheduled run-rate;
- future starts;
- PIF sales;
- actual cash;
- named timing items;
- explained variance; and
- unexplained residual with owner and due date.

## Testing

Add unit and integration tests for:

- exact email, phone fallback and approved legacy-email links;
- rejection of name-only matches;
- active subscription with `pause_collection`;
- successful, open, void, incomplete and past-due invoices;
- one-week-in-advance allocation and late retry treatment;
- Active, Active PIA and Active arrears reporting;
- Fast Track split and cash deduplication;
- PIF receipt versus session-balance separation;
- late-cancellation charge classification;
- future booking absence without inferred cancellation;
- historical commencement versus current service;
- refunds and downgrades;
- bounded sheet writes, idempotency and duplicate detection;
- stale or incomplete source snapshots; and
- cash-bridge arithmetic.

## Acceptance Criteria

The system is ready for weekly operation when:

1. One run recreates the Active PT weekly worksheet and SGPT exception review without manual identity matching.
2. The cash bridge separates all required measures and every residual is named and owned.
3. Fast Track receipts and allocations are counted exactly once.
4. PIA and arrears are classified correctly.
5. No cooling-off refund remains active.
6. No pause or cancellation is accepted without lifecycle evidence.
7. Every changed sheet row is post-write verified.
8. Three consecutive read-only weekly runs produce zero unsafe recommendations.
9. Admin can complete the Monday and Friday controls from the generated outputs without repeating the underlying investigation.

## Implementation Record: 25 July 2026

- Phase 1 package, protected audit database, reports and safe runner are implemented.
- Live roster and automatic KPI cash reads are implemented.
- Membership, invoice, lifecycle, Trainerize and PT booking evidence are joined read-only.
- Exact email, unique verified phone and approved durable email links are supported; name-only matching is rejected.
- Fast Track, PIA, arrears, pauses, future starts, PIF packs, lifecycle contradictions and duplicate-email controls are implemented.
- Controlled legacy-payment and timing registers are ready in the ignored private directory.
- Monday 6:30 am and Friday 4:30 pm Brisbane automations are active.
- Eighty-nine combined controller, membership-reconciliation and booking-shadow tests pass.
- The first July shadow run reproduced the roster allocation and cash baseline. It remained open because approved PTMinder/EziDebit receipt evidence is incomplete.
- Two later validation retries failed closed on Google Sheet read timeouts. No connected record was changed.

Phase 1 remains in shadow validation until the legacy-payment register is complete and three consecutive weekly runs meet the safety gate.

## Current Reconciliation Baseline

The July close figures are a starting checkpoint, not a permanent fixture:

- 94 Active or Active PIA SGPT members;
- 44 Active PT clients;
- $8,957 numeric SGPT allocation;
- $3,778 numeric PT allocation;
- $12,735 combined numeric allocation;
- $11,531 known-current expected income after documented exclusions;
- $10,927.24 cleared cash in KPI column AV;
- $603.76 remaining bridge before identified timing items;
- $396 attributed to four recent $99 SGPT allocations;
- $170 attributed to net PT allocation changes; and
- $37.76 unexplained after those timing items.

Every implementation run must read fresh evidence and preserve newer verified facts rather than forcing the data back to this checkpoint.
