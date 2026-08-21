# Reporting V2 Delivery Marker Review Layer

**Status:** Live review layer  
**Date:** 1 August 2026  
**Owner:** Peter Brown  
**Implementation surface:** Operating Data Hub Reporting V2 preview

## Objective

Restore the familiar service-delivery markers from the accepted CEO dashboard
inside the Reporting V2 preview so Peter can review the information in context
and decide what belongs in the final CEO surface.

This is a presentation and comparison change only. It must not publish a V2
metric, change the KPI workbook, alter a metric definition, or create a second
calculation path.

## Architecture decision

The Reporting V2 preview will receive the existing `dashboard_data()` result
from the Operating Data Hub and render a clearly labelled delivery-review
section beneath the governed V2 scorecard.

The existing hub snapshot remains the only source for these markers. The
preview must not query GHL, Stripe, PT Minder, Trainerize or Google Sheets
directly.

## Markers to restore

1. **Current client service**
   - agreed active clients;
   - Strength & Sculpt only;
   - Fast Track;
   - 1:1 PT only;
   - active PT roster;
   - active notice and downgrade periods.
2. **Assessment and onboarding delivery**
   - Strength Assessment showed, no-show, cancelled and unresolved outcomes;
   - show and cancellation rates where available;
   - sale-to-onboarding completion speed.
3. **PT delivery**
   - booked PT sessions;
   - booked PT hours;
   - trainer booking and hour split.
4. **Member outcomes**
   - four-week, 12-week, six-month and overall strength improvement;
   - top performers and workout milestones;
   - members approaching or achieving Evolved standards;
   - reassessment review count when named standards are not yet available.

## Period and confidence rule

The existing V1 delivery snapshot is not yet consistently event-level or
period-aware. The page must therefore distinguish:

- the selected completed Reporting V2 period;
- current-snapshot or current-week V1 delivery markers;
- unavailable markers whose governed calculation is not yet connected.

The period selector must not imply that a current-snapshot marker has been
recalculated for 28 or 90 days. Each restored marker must show its timing or
readiness in plain English.

## Acceptance checks

- Reporting V2 stays login protected.
- All three period selections still render.
- The page identifies the restored section as a review layer.
- The delivery layer receives values from `dashboard_data()` only.
- Empty or unavailable source data renders a clear placeholder, not a guessed
  value.
- Existing Reporting V2 acceptance and cash-goal calculations are unchanged.
- The accepted CEO dashboard and KPI workbook are unchanged.
- Automated tests cover representative client service, assessment, PT and
  member-outcome markers.
- The deployed page is visually checked on desktop and narrow layouts.

## Retirement path

This review layer is temporary. After Peter selects the useful markers, each
retained item will either:

1. become a governed period-aware Reporting V2 metric;
2. remain an explicitly current-state operating marker; or
3. be removed from the final CEO dashboard.

The V1 dashboard remains available until those decisions and metric-level
acceptance gates are complete.

## Notice-period display clarification

The CEO surface must not reduce an active notice to a name and date. The
existing governed lifecycle snapshot already distinguishes a whole-membership
cancellation from a PT cancellation and the active-client cohort already
supplies the member's current service mix. Reporting V2 will reuse those two
hub projections to show:

- the member;
- a plain-English notice type;
- the current service;
- the service or membership outcome after the notice;
- the effective date, days remaining, or missing/overdue-date warning.

This remains a current-state operating marker. It does not create a new
lifecycle definition, query a source system from the dashboard, or infer a
cancellation reason that the hub has not captured.

## Implementation result

Railway deployment `412cb27e-809b-4024-8498-5651d6aabfc0` made the review
layer live on 1 August 2026. The full Operating Data Hub suite passes at 142
tests. Production verification confirmed all four delivery sections, the
existing completed-period selector, no console errors and no horizontal
overflow at a 390-pixel mobile viewport.

Railway deployment `230927d6-d1df-4218-8197-9dc0612a23f3` then replaced the
compact notice rows with a complete current-state notice view: totals by
notice type, named members, current and future service, effective date and
days remaining. Retention Intelligence deployment
`b1e89bce-3d64-4b33-9d8b-b73d591a9577` completes the existing membership
snapshot contract with the selected GHL contact name. Read-only source run
`20260801T043702Z` republished the governed identities with Sheet writes
disabled. Production now shows Sarah Loga as a full membership cancellation,
Sezen Yaşar and Bethan Watson as Fast Track downgrades, and Elizabeth Winter
as a PT-service cancellation. The combined affected suite passes at 164
tests.

The accepted CEO dashboard, KPI workbook, Reporting V2 definitions and
publication gates were not changed.
