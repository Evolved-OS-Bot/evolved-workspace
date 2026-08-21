# Plan: CEO Scorecard Data Connections, Period Controls and Million-Dollar Goal

**Date:** 2026-07-29  
**Status:** In progress; governed preview deployed in shadow  
**Owner:** Peter Brown  
**Implementation surface:** Railway operating-data hub, GHL, Trainerize, Google Sheets and CEO dashboard  
**Scheduling rule:** Railway only

## Objective

Complete the four missing CEO data connections, add accurate weekly, rolling 28-day and rolling 90-day views, and show accepted cash collected excluding GST against a $1 million goal.

The dashboard must answer:

1. How much cash did the business collect?
2. Is the member base growing?
3. Where is the acquisition funnel leaking?
4. How quickly do buyers begin receiving their service?
5. Are trainers being used effectively?
6. Are members getting stronger and reaching The Evolved standards?
7. Is the business ahead of or behind the million-dollar trajectory?

## Non-Negotiable Architecture Rules

- Railway remains the only scheduler.
- Source events are captured once and stored at their natural grain.
- Weekly, 28-day and 90-day values are calculated from the same accepted event tables.
- Ratios are recalculated from their numerators and denominators. Weekly percentages are never averaged together.
- Total cash, recurring cash and new cash remain separate measures.
- Accounting turnover remains off the dashboard until a reliable accounting-system feed exists.
- Stock measures such as active clients use an as-of date. Flow measures such as cash, leads and sessions use a start and end date.
- Every metric carries a definition version, source snapshot IDs, timezone and freshness state.
- Missing or stale evidence produces `Unavailable`, not a guessed value.
- Identified member and trainer detail remains behind the authenticated dashboard.

## Period Model

### Supported selections

| Dashboard selection | Start | End | Intended use |
|---|---|---|---|
| Week | Previous completed Monday | Previous completed Sunday | Weekly operating review |
| Last 28 days | 28 completed local dates | Yesterday, Brisbane time | Current four-week trend |
| Last 90 days | 90 completed local dates | Yesterday, Brisbane time | Stable strategic trend |

The toggle changes the whole dashboard through one `period_id`. It does not allow each card to choose its own dates.

### Metric behaviour

- Cash, leads, appointments, sales, workouts and PT hours: sum qualifying events inside the selected period.
- Show-up rate: attended Strength Assessments divided by assessments due to occur in the selected period.
- Assessment conversion: sales attributed to assessments attended in the selected period divided by attended assessments.
- Prequalification completion: eligible prequalifications completed divided by eligible prequalifications due in the selected period.
- Member growth: unique activated clients minus unique clients whose final access ended in the selected period. Service upgrades do not count as new people.
- Active clients and membership mix: latest governed state at the period end.
- PT utilisation: booked eligible PT minutes divided by governed available trainer minutes in the same period.
- Strength horizons: follow-up observations completed in the selected period, compared with each woman's governed baseline.
- Milestones: milestones first achieved in the selected period.

## Connection 1: GHL Prequalification Completion

### Source evidence

- GHL contact ID and canonical hub person ID.
- Lead-created timestamp.
- Strength Assessment booking timestamp.
- Prequalification-required timestamp.
- Prequalification-completed timestamp.
- Completion state and version.
- Explicit exclusions: test contacts, duplicate contacts, cancelled leads before prequalification became due and internal staff.

### Build

1. Add a Railway GHL prequalification extractor that reads the approved GHL fields, tags and workflow state.
2. Publish versioned events to `hub_prequalification_events`.
3. Resolve contacts through the existing canonical identity layer.
4. Persist the eligible, completed, waived and expired states separately.
5. Calculate the completion rate from completed and eligible counts for the selected period.
6. Add drill-down queues for incomplete and overdue prospects.

### Acceptance

- Exact parity with a manually reviewed GHL sample of at least 30 prospects.
- Zero duplicate prospects.
- Completed plus waived plus incomplete equals the eligible cohort.
- The dashboard numerator and denominator are visible in the metric definition.

## Connection 2: Sale-to-Onboarding Speed

### Source evidence

- Completed Strength Assessment appointment.
- Sale or membership-agreement completion timestamp.
- Purchased membership and onboarding entitlement: zero sessions for Fit & Flexible, one KickStart for Strong, four-session pathway for Fast Track.
- First eligible onboarding appointment booking timestamp.
- First completed onboarding appointment timestamp.
- Cancellation, reschedule and no-show states.

### Build

1. Add governed GHL appointment classifications for Strength Assessment, KickStart and Fast Track onboarding.
2. Link the sale to the first completed eligible onboarding session through canonical person ID.
3. Store `sale_at`, `first_onboarding_booked_at`, `first_onboarding_completed_at` and entitlement type.
4. Exclude Fit & Flexible from the onboarding-speed denominator because it has no onboarding appointment.
5. Report:
   - average days to completed onboarding;
   - median days;
   - percentage completed within three days;
   - sold members still unbooked;
   - overdue onboarding cases.
6. Keep booking speed and completion speed separate.

### Acceptance

- Manual review of every sale in two completed weekly periods.
- No-show or cancelled appointments cannot count as completed onboarding.
- Existing-member PT add-ons cannot create a false new-member onboarding event.
- Fast Track session two to four cannot replace the first completed onboarding event.

## Connection 3: Trainer Capacity and PT Utilisation

### Source evidence

- Governed trainer roster.
- Available PT hours by trainer and effective date.
- Approved leave, public holidays, blocked administration time and temporary availability changes.
- Eligible GHL PT appointments, duration, trainer, status and local date.

### Build

1. Add `hub_trainer_capacity_windows` with trainer, weekday, start time, end time, effective dates and approval provenance.
2. Add exception windows for leave and one-off availability.
3. Reuse the existing deduplicated GHL PT appointment events for booked minutes.
4. Calculate, by trainer and total:
   - available hours;
   - booked hours;
   - session count;
   - utilisation percentage;
   - unfilled available hours.
5. Keep booked workload visible even when capacity is unavailable.
6. Add a capacity-maintenance screen or protected Sheet input; the hub remains authoritative after acceptance.

### Acceptance

- Trainer totals add exactly to the business total.
- Cancelled, deleted and no-show sessions do not consume booked capacity.
- Dual-calendar duplicates are counted once.
- Leave reduces the denominator, not the booked numerator.
- Two weekly manual calendar comparisons pass with zero unexplained variance.

## Connection 4: Live, Long and Perform Standards

### Source evidence

- The canonical standards definitions in `reference/evolved-manual/03-strength-standards.md` and `reference/evolved-manual/03b-standards-framework.md`.
- Trainerize assessment workout, bodyweight and canonical exercise results.
- Approved exercise aliases.
- Assessment date, completion state and version.

### Build

1. Convert every standard into a versioned machine-readable rule with movement, load basis, bodyweight rule, repetitions and required combination.
2. Canonicalise duplicate exercise names before scoring.
3. Calculate each member's current standard, next standard and percentage progress to the next threshold.
4. Create queues for:
   - standard achieved in the selected period;
   - within 10% of the next standard;
   - assessment overdue;
   - result blocked by missing bodyweight or non-standard exercise evidence.
5. Require coach review before a standard becomes an externally communicated achievement.

### Acceptance

- Coach-reviewed fixture set for every standard and boundary.
- Exact pass and fail tests immediately below and above every threshold.
- Missing bodyweight fails closed for bodyweight-relative measures.
- Historical exercise aliases produce the same result as the canonical exercise.

## Accurate Multi-Period Aggregation

### Shared event tables

Add or complete:

- `hub_cash_events`;
- `hub_lead_events`;
- `hub_prequalification_events`;
- `hub_assessment_events`;
- `hub_sale_events`;
- `hub_onboarding_events`;
- `hub_member_lifecycle_events`;
- `hub_pt_appointment_events`;
- `hub_trainer_capacity_windows`;
- `hub_strength_observations`;
- `hub_standard_achievements`.

Every event has a stable source ID, canonical person or trainer ID where applicable, occurred-at time, Brisbane local date, source snapshot ID and deduplication key.

### Reporting contract

Add:

- `GET /api/v1/ceo-scorecard?period=week`
- `GET /api/v1/ceo-scorecard?period=28d`
- `GET /api/v1/ceo-scorecard?period=90d`

Each response returns:

- the exact period;
- metric numerators and denominators;
- metric values;
- comparison with the immediately preceding equivalent period;
- source freshness;
- definition versions;
- unavailable reasons;
- identified drill-down links where authorised.

The CEO report API consumes the same scorecard response.

### Dashboard behaviour

- Segmented toggle: `Week`, `28 days`, `90 days`.
- The selected period appears beside the dashboard title.
- Cards show change versus the previous equivalent period.
- Charts and tables update from one response.
- The URL retains the selection, for example `/dashboard?period=28d`.
- Invalid periods fail to `week`; they do not create arbitrary queries.

## Million-Dollar Cash Chart

### Owner definition required

The governing measure is accepted cash collected excluding GST over the immediately preceding 365 days, ending at the latest accepted refresh. It has no calendar-year or financial-year reset.

The goal is marked achieved as soon as the rolling total reaches $1 million. The first achieved-at timestamp is retained as a milestone even if the current rolling total later falls below $1 million as older cash leaves the window.

### Proposed default

The approved first shadow build uses:

- goal period: continuously rolling 365 days;
- target: $1,000,000 accepted cash collected excluding GST;
- refunds reduce actuals on the refund date;
- internal transfers and duplicate processor records are excluded.

### Chart

Use a cumulative line chart:

- actual accepted cash excluding GST over the immediately preceding 365 days;
- straight-line target pace to $1 million;
- forecast line based on the trailing 90-day daily run rate;
- optional prior-year actual comparison once historical coverage is complete.

Show four headline values:

- accepted rolling-365-day cash excluding GST;
- target pace as of today;
- ahead or behind target in dollars;
- forecast date for first reaching the goal, when not yet achieved.

Also show:

- required weekly cash collection to reach the goal at the selected forecast horizon;
- current trailing-28-day weekly equivalent;
- remaining gap to $1 million.

Accounting turnover is not inferred from this chart and remains unavailable until a reliable accounting-system feed exists.

## Delivery Sequence

### Phase 1: Period engine and revenue goal foundation

1. Add shared period IDs and query validation.
2. Backfill accepted weekly cash and new-cash history.
3. Add event-grain accepted cash ingestion, GST treatment and deduplication.
4. Build the week, 28-day and 90-day API contract.
5. Add the period toggle and million-dollar shadow chart.

### Phase 2: GHL acquisition and onboarding

1. Build the prequalification event extractor.
2. Build sale, assessment and onboarding event classification.
3. Validate two weekly cohorts.
4. Enable the prequalification and onboarding cards.

### Phase 3: Trainer capacity

1. Approve trainer availability ownership and effective-date process.
2. Load capacity windows.
3. Validate utilisation against GHL calendars.
4. Enable utilisation percentages and unused-capacity reporting.

### Phase 4: Standards

1. Approve the machine-readable rule set.
2. Build assessment scoring and member queues.
3. Coach-review fixtures and milestone results.
4. Enable the standards card and named drill-down.

### Phase 5: Parity and cutover

1. Run two complete shadow cycles for each new source.
2. Compare dashboard values with GHL, Trainerize and the KPI Sheet.
3. Resolve all unexplained differences.
4. Promote each metric independently after its gate passes.
5. Update the CEO report and Google Sheet views to consume the same accepted metrics.

## Test Coverage

- timezone and completed-period boundary tests;
- week, leap-year, 28-day and 90-day boundaries;
- ratio numerator and denominator aggregation;
- event deduplication;
- refunds and reversals;
- lead and appointment state transitions;
- no-show and reschedule handling;
- zero-onboarding-entitlement exclusions;
- trainer leave and capacity boundaries;
- strength observation windows;
- standards threshold boundaries;
- previous-period comparisons;
- unavailable and stale-source behaviour;
- dashboard route and period query tests;
- CEO dashboard and CEO report parity.

## Definition of Done

- The three period selections reproduce accepted source totals exactly.
- No displayed ratio is produced by averaging weekly percentages.
- The four missing connections have passed their individual shadow gates.
- PT booked workload and utilisation are both visible and clearly distinguished.
- The million-dollar chart uses accepted cash collected excluding GST.
- The dashboard, CEO report and approved Google Sheet expression agree for the same period ID.
- All scheduling and refresh work runs on Railway.

## Implementation Update: 31 July 2026

- The shared Reporting V2 contract now supports one completed-period selector across week, 28 days and 90 days.
- A login-protected `/dashboard/reporting-preview` page exposes the selector without changing the accepted CEO dashboard or KPI workbook.
- Every preview metric shows its evidence/readiness state and remains unpublished until its comparison gate passes.
- The rolling 365-day $1 million cash-goal envelope is present and explicitly unavailable until accepted event-level cash has completed its first observation.
- PT utilisation displays its exact missing dependency: governed trainer available hours for the same selected period. Booked workload is not mislabelled as utilisation.
- The trainer scorecard and compact board-pack roles are shown as gated next surfaces. The board-pack contract remains summary-only and Google Sheets remains outside event storage and calculation.
- The second PT Minder capture now has a tested preflight gate for independence, account coverage and transaction-history completeness.
- Forty-eight affected Reporting V2, dashboard and PT Minder gate tests pass.

Railway deployment `4b2bbef3-a4f9-4bc0-9ed7-e343f39d38d1` published the coordinated preview after the Strength Assessment guard passed its live zero-re-enrolment test. Production verification confirmed all three period selections, the shadow warning and continued isolation of the accepted dashboard and KPI workbook.

## Owner Decisions

1. Confirm who owns and approves trainer available hours and leave changes.
2. Confirm the operational onboarding target: retain the current two-to-three-day standard or use a different CEO target.
3. Confirm whether top-performer and standards achievements require coach approval before appearing by name on the CEO dashboard, or only before member communication.
