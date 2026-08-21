# SGPT Delivery Reporting

**Owner:** Peter Brown  
**Operational data owner:** Admin Eve  
**Coaching and capacity owner:** Megan Brown  
**Definition:** `sgpt-delivery-v1`  
**Mode:** Internal, read-only shadow  
**Scheduler:** Railway only  
**Decision surface:** Reporting V2  
**Metric layer:** Operating Data Hub

## Outcome

The SGPT Delivery pillar reuses the existing Trainerize performance refresh and
the Hub identity and active-service contracts. It does not create another
extractor, schedule, member record, or source-system write.

The accepted CEO dashboard and KPI workbook remain unchanged until each metric
passes the Reporting V2 metric-level acceptance gate.

## Source and identity contract

Trainerize is evidence for class bookings and explicit class outcomes. The
governed active-client cohort is authoritative for active SGPT membership. The
Hub maps Trainerize user IDs to canonical person IDs through the existing
`hub_source_identities` records.

The Trainerize API calendar day is not used as the Brisbane service date.
Trainerize start and end timestamps are interpreted as UTC and converted to
`Australia/Brisbane`. This prevents early-morning classes from being assigned
to the prior day or reporting week.

## Governed definitions

| Metric | Definition |
| --- | --- |
| Booking record | One de-duplicated Trainerize member and class-session record. |
| Booked | A scheduled or confirmed booking, an explicitly attended booking, or an explicit no-show. An explicitly cancelled record is excluded from booked fill. |
| Attended | Trainerize explicitly reports checked in, attended, complete, completed, or an accepted equivalent terminal outcome. |
| Cancelled | Trainerize explicitly reports cancelled or canceled. Absence from a later extract is not cancellation evidence. |
| No-show | Trainerize explicitly reports no-show, noshow, or missed. An elapsed booking and `checkedIn=false` are not no-show evidence. |
| Unique members booked | Distinct canonical people with a booked, attended, or no-show record in the period. |
| Unique members served | Distinct canonical people with explicit attended evidence. Unavailable when the period has no explicit terminal outcome evidence. |
| Class session | One distinct Trainerize class-session ID after Brisbane period selection. |
| Capacity places | Observed class sessions multiplied by the governed 15-place delivery capacity. |
| Booked fill rate | Booked places divided by governed capacity places. |
| Attended fill rate | Explicit attendances divided by governed capacity places. Unavailable without explicit attendance evidence. |
| No booked delivery | Active governed SGPT person IDs minus the exact set with a booked, attended, or no-show record. |
| No attended delivery | Active governed SGPT person IDs minus the exact attended set. Unavailable without explicit attendance evidence. |
| Trainer booked utilisation | Member bookings for the trainer divided by the governed capacity of that trainer's observed class sessions. |
| Trainer attended utilisation | Explicit attendances for the trainer divided by the same governed capacity. Unavailable without explicit attendance evidence. |

Class, Brisbane timetable slot, and assigned-trainer breakdowns use the same
record set and denominator rules as the headline metric. They cannot silently
recalculate their own totals.

## Capacity control

The current delivery SOPs specify 15 members for Sculpt & Strength, Metabolic
Burn, Pilates, and HybridFit. Fifteen is therefore the governed safe delivery
denominator for `sgpt-delivery-v1`.

Trainerize has an 18-place booking configuration for the active Sculpt &
Strength type. This remains a visible configuration exception. It does not
replace the safe capacity denominator or approve delivery above 15.

The timetable reconciliation reports observed, matched, and unmatched class
sessions. A match requires a Brisbane slot, a governed class name, and an
assigned trainer. It does not fabricate empty class sessions from member
bookings. The verified 26-slot timetable remains the control for detecting
offerings that have no member calendar records.

## Privacy and failure behaviour

- Aggregate endpoints contain counts, rates, source health, and reconciliation
  coverage without names.
- Protected evidence may retain stable canonical person IDs.
- Identified no-delivery lists require the protected authenticated route.
- A partial, stale, or failed Trainerize run cannot pass acceptance.
- Identity-unmatched and timetable-unmatched events increase the unexplained
  event count.
- Unknown outcomes remain unknown.
- No client message, task, calendar change, Trainerize write, or GHL write is
  enabled.

## Acceptance gates

Promotion requires all of the following for the same governed Brisbane period:

1. Two complete, fresh Railway source cycles.
2. Source snapshot ID, source run ID, observed time, completion state, age, and
   sample count present.
3. Exact identity-set sampling against the governed active SGPT cohort.
4. Zero inferred attended, cancelled, or no-show records.
5. Complete timetable assignment coverage, or every exception explained.
6. Zero unexplained event differences.
7. Metric-level definition and rule approval from Peter.
8. Explicit confirmation that the accepted dashboard and KPI workbook remain
   unchanged until promotion.

## Tests

The automated suite covers booking and session separation, strict outcomes,
Brisbane dates, capacity, fill, delivery breakdowns, exact no-delivery identity
sets, source metadata, privacy routes, and Reporting V2 compatibility.

On 2 August 2026, the focused Operating Data Hub and Trainerize performance
suite passed 243 tests. The final shared integration verification reported 434
passing tests plus a passing instruction-drift check.

## Deployment and verification

The implementation is deployed only through the existing Railway
`trainerize_performance` refresh and `operating_data_hub` service. No Codex or
local scheduler is permitted.

Final Trainerize Performance deployment
`6ca674ba-77a1-4d62-a012-3880ec584b68` and SGPT/Reporting Hub deployment
`e737a3db-a81c-40d8-a962-d107e0801a0b` succeeded on 2 August 2026. The Hub
deployment contains the protected Reporting V2 preview, metric-level
acceptance integration, cutover registry and rollback controls. A later
Build 2 contract/store change landed after this Hub archive was created and
requires the next coordinated combined Hub deployment; no duplicate deployment
was started from this workstream.

Live Trainerize run `trainerize-performance-20260802T004449+0000` completed in
read-only shadow mode and published 2,392 SGPT booking records across the
120-day refresh window. Hub snapshot `20260802T004851Z-02d9175d` is complete
and fresh.

The completed Brisbane week of 20 to 26 July reports:

- 159 booked places across 69 unique members;
- 26 observed class sessions and 390 governed capacity places;
- 40.8% booked fill;
- 98 active governed SGPT members, including 32 with no booking;
- 100.0% timetable coverage and 100.0% identity coverage;
- zero unmatched and zero inferred outcome records;
- attended, cancelled, no-show, unique served and attended fill unavailable
  because the source supplied zero explicit terminal outcomes.

The same final source cycle reports 625 booked places, 90 unique booked members,
104 sessions, 1,560 governed places and 40.1% booked fill for the completed
28-day view. The completed 90-day view reports 1,865 booked places, 106 unique
booked members, 307 sessions, 4,605 governed places and 40.5% booked fill.
Attendance-dependent measures remain unavailable in both views, with zero
inferred or unexplained outcomes.

Live verification confirmed:

1. the Trainerize refresh publishes the current `sgptBookingEvents` payload;
2. the Hub accepts a complete `trainerize_performance` snapshot;
3. `/api/v2/reporting/sgpt-delivery` returns `sgpt-delivery-v1`;
4. source and reconciliation metadata are populated;
5. attendance remains unavailable when the source has no explicit outcome;
6. all period views use Brisbane dates and the same totals;
7. the 390-pixel Reporting V2 view has no horizontal overflow and the browser
   console reports no errors;
8. the accepted dashboard and KPI workbook have not changed.

The metric remains in `shadow` state with no accepted-metric record. Promotion
requires Build 4's existing acceptance controller to observe a second distinct
complete producer cycle, reconcile the exact identity sets and comparisons,
and record separate owner authority. This workstream does not create a second
promotion mechanism.

## Retirement path

The earlier booking-only SGPT preview is replaced by this compatible,
versioned contract. The Trainerize performance extractor and Railway schedule
remain in place. No source pipeline is retired because no duplicate pipeline
was created.
