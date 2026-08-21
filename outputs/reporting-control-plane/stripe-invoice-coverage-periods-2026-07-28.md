# Stripe Invoice Coverage Periods

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

Stripe payment events now carry exact coverage start and end dates from
positive, non-proration invoice lines. The hub counts a dated entitlement only
when the governed cohort date falls inside that window.

One-day invoice lines are retained as payment evidence but cannot create
ongoing membership entitlement.

## Production Result

| Measure | Before | After |
| --- | ---: | ---: |
| Commercially verified clients | 99 | 100 |
| Clients pending evidence | 33 | 32 |
| Service gaps | 35 | 34 |
| High-priority service gaps | 20 | 20 |
| Owner decisions required | 0 | 0 |

Julie Nina Guilhem has a paid SGPT coverage window from 22 to 29 July 2026 and
is now commercially verified for the governed 27 July cohort date.

## Seven One-Time Invoice Cases

The seven targeted $349 to $599 Stripe receipts each have invoice-line coverage
that starts and ends on the payment day. Stripe therefore proves the payment
event but does not supply an ongoing service term.

They are now labelled `One-time invoice, entitlement term missing`. Admin must
attach the purchased service term or approved access end date before any
entitlement can be promoted.

No membership duration is inferred from:

- payment amount;
- invoice status;
- a cancelled Stripe customer or subscription;
- GHL lifecycle state;
- roster membership; or
- Trainerize access.

## Controls

- Entitlement effective dates are enforced by both the CEO metric and exception
  queue calculations.
- Expired entitlements automatically stop counting.
- Future entitlements cannot count before their start date.
- Multiple conflicting invoice-line end dates fail closed.
- Proration and non-positive invoice lines cannot establish coverage.
- Same-day invoice lines remain payment events only.
- No client, payment, booking, contact or Google Sheet record was changed.
- No new schedule was created.

## Verification

- Hub deployments:
  `8b74d947-e58e-4ff3-8e6b-78bebe443689` and
  `d15b3c32-b4fa-4ee4-af53-4e0fe976c345`.
- Retention Intelligence deployments:
  `8af0c770-3cd6-45b0-a74a-a7b99c1d226b` and
  `cc4ee489-49f5-4eb0-a467-eb1af6f5950f`.
- Source reconciliation:
  `20260728T002358Z`.
- Accepted Stripe commercial snapshot:
  `20260728T002531Z-9120f060`.
- 235 automated tests passed.

## Next Build

Completed by
`outputs/reporting-control-plane/governed-purchased-service-terms-2026-07-28.md`.
The protected register is live and ready for the seven approved term records.
