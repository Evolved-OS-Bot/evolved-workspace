# SGPT Delivery Reporting V2

**Status:** Complete — live internal shadow; metric acceptance pending  
**Date:** 2 August 2026  
**Owner:** Peter Brown  
**Runtime:** Railway Trainerize Performance and Railway Operating Data Hub  
**Decision surface:** Protected Reporting V2 preview

## Objective

Complete the SGPT Delivery pillar without creating another extraction path or
changing the accepted CEO dashboard or KPI workbook. Extend the existing
Trainerize Performance calendar refresh, publish its event evidence through
the existing Hub snapshot contract, reconcile it to the governed active SGPT
cohort and calculate period-aware delivery diagnostics in Reporting V2.

## Evidence and authority

| Measure | Authority | Rule |
|---|---|---|
| Member class booking | Trainerize member calendar `appointmentV2` class event | Count one current event per member and class occurrence. |
| Attended | Explicit Trainerize check-in or terminal attended/completed status | Never infer from a retained booking. |
| Cancelled or no-show | Explicit terminal Trainerize outcome | Missing or removed history remains unavailable, not zero. |
| Class name, time and delivered trainer | Trainerize class occurrence | Preserve the source event and assigned trainer. |
| Planned slot and trainer | Governed timetable | Reconcile without overwriting source delivery evidence. |
| Governed delivery capacity | Current SGPT delivery SOP, 15 | Use 15 for operational fill; retain Trainerize's 18-place booking ceiling as a configuration exception. |
| Active SGPT member | Hub governed active-client cohort | Reuse canonical identity and current SGPT service relationships. |

The workspace contains historical values of 12 and 18, but the current SGPT
delivery SOP is the governed operating rule at 15. Fill uses 15. The
Trainerize ceiling of 18 remains a visible configuration exception because the
booking platform can currently exceed the governed delivery capacity.

## Implementation

1. Extend the existing Trainerize calendar event projection with source
   identity, explicit outcome evidence and booking capacity.
2. Add a pure Hub reconciliation that:
   - deduplicates member bookings;
   - separates booked, attended, cancelled, no-show and unresolved outcomes;
   - calculates unique members booked and attended;
   - calculates class, slot and trainer breakdowns;
   - calculates booking and attendance fill only when a governed denominator
     and qualifying outcome evidence exist;
   - identifies active SGPT members with no booking and no attendance.
3. Resolve Trainerize source identities through existing Hub identity links.
4. expose aggregate results in Reporting V2 and identified exceptions only
   through an authenticated protected endpoint.
5. Register the Railway-owned report contract and document freshness, failure,
   privacy, deduplication, acceptance and retirement behaviour.

## Acceptance gates

- A booking is never counted as attendance.
- Unknown outcome coverage is visible and does not become zero attendance.
- Replays and duplicate member-calendar rows do not inflate counts.
- Class occurrences with multiple members count once for coaching hours.
- Fill rate is unavailable when capacity is missing or inconsistent.
- Active-member exceptions use the governed SGPT cohort and shared identities.
- Selected completed week, rolling 28 days and rolling 90 days render.
- The accepted dashboard and KPI workbook remain unchanged.
- Focused and full Hub/Trainerize suites pass.
- Railway refresh and protected live preview/API are verified.

## Deployment and scheduling

No new schedule is created. Railway Trainerize Performance remains the sole
source refresh at 05:15 and 17:15 Brisbane. Reporting V2 reads the accepted Hub
snapshot. A failed or stale source leaves the SGPT widget unavailable and
retains the last accepted evidence for audit; it never publishes a guessed
replacement.

## Retirement path

This replaces the temporary booking-only SGPT review calculation in
`operating_data_hub/delivery_reporting.py`. It does not replace the accepted
dashboard or KPI workbook until each metric passes its comparison and owner
acceptance gate.

## Completion evidence

Railway deployments `87cb52d8-ba8d-4b43-93aa-69c469f97d83` (Trainerize
Performance) and `c8f1cb73-3297-4fa4-849c-293bbb93cbc5` (Operating Data Hub)
are healthy. Fresh run `trainerize-performance-20260802T003547+0000` and Hub
snapshot `20260802T003649Z-1edfe775` provide the completed-week delivery
evidence. The combined acceptance suite passes 307 tests, the protected API
and Reporting V2 decision surface are live, and the 390-pixel view has no
horizontal overflow or browser errors.

The completed week reports 159 bookings, 69 unique booked members, 26 observed
sessions, 390 governed places and 40.8% booked fill with complete identity and
timetable reconciliation. Trainerize supplied no explicit terminal outcomes,
so attended, cancelled, no-show, unique-served and attended-fill measures
remain unavailable. The build is complete in shadow mode; two complete fresh
Railway cycles and Peter's exact metric-rule acceptance remain publication
gates, not implementation defects.
