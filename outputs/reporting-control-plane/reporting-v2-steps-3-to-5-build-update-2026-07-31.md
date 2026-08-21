# Reporting V2 Steps 3 to 5 Build Update

**Date:** 31 July 2026  
**State:** Deployed in shadow  
**Live reporting impact:** None

**Railway deployment:** `4b2bbef3-a4f9-4bc0-9ed7-e343f39d38d1`

**Cash contract deployment:** `9ad5ef7b-20a7-4183-aafb-423554086fac`

**Retention-to-hub deployment:** `42160443-6ae9-4efa-9ee6-4be7b5326b21`

**PT roster freshness deployment:** `7edb31ab-9819-4a0d-aeaf-a81da0fdd2d1`

**Conversation Triage 12-hour deployment:** `b6cd5586-044e-4f4d-bdca-5943f20c582f`

**Governed-control freshness deployment:** `a725fab4-a1cb-423f-b902-6d4327318a3a`

## What is now built

### 3. Acceptance and parity

- One shared completed-period contract for last week, last 28 days and last 90 days.
- Metric-level readiness: value availability, evidence confidence and legacy-versus-V2 comparison state must all pass.
- The accepted CEO dashboard and KPI workbook remain unchanged until individual metric gates pass.

### 4. Second PT Minder verification

- A preflight gate verifies that the capture is newer than cycle one.
- It checks account coverage and complete purpose-aware payment/debit history.
- It rejects undersized, incomplete or reused evidence before upload.
- A successful preflight still requires exact protected revenue parity after upload.

### 5. CEO decision surfaces

- A login-protected Reporting V2 preview has a last-week, 28-day and 90-day selector.
- The page shows plain-English metric names and why any metric is not ready.
- A rolling 365-day $1 million cash-goal surface exists, but stays unavailable until accepted event-level cash is connected.
- The accepted-cash boundary is now deployed in shadow: it requires explicit GST cents, nets refunds on their event dates, deduplicates processor events and fails unavailable when required source coverage is incomplete or stale.
- PT utilisation does not display a false percentage. It requires booked hours and approved trainer capacity for the same period.
- The trainer scorecard is staged around delivery, attendance recording, onboarding completion and member outcomes; rankings remain gated pending agreed minimum sample sizes.
- The compact Google Sheets board pack remains a summary, trend, decision and controlled-input surface. It is not an event database or calculation engine.

## Acceptance gates still open

1. Complete the independent PT Minder capture in the week beginning 3 August and retain exact parity.
2. Complete two clean Reporting V2 metric comparison cycles.

## 31 July source-freshness verification

- Membership reconciliation and Stripe commercial evidence completed a live
  read-only refresh and reached the hub as fresh observations.
- An unchanged PT roster now advances its verified observation time. The live
  result retained 133 clients and 145 service relationships without duplicate
  additions.
- The roster safety gate held two possible removals and one addition for
  review, so the accepted 134-person cohort was not silently changed. The
  removals are `banthita.kssng@gmail.com` and `eddieandjen@bigpond.com`; the
  candidate-only addition is `jodieldoran@gmail.com`.
- Conversation Triage is deployed on the 06:00 and 18:00 Brisbane schedule.
  Its existing stale marker clears after the next scheduled run publishes.
- Effective-dated owner-approved payment classification rules are treated as
  governed configuration, not as a daily source feed.
- The accepted CEO dashboard and KPI workbook remain unchanged.
- Accepted attendance snapshot `20260731T000003Z-7bd16306` ingested Jess
  Michels's owner-confirmed Showed result. The explicit showed count and
  denominator moved from seven to eight, while unresolved attendance reduced
  from 37 to 36. Her missing consultant submission remains a separate process
  exception.
3. Connect accepted event-level cash and validate GST, refunds and duplicates.
4. Approve the owner and effective-date process for trainer capacity.
5. Coordinate any later metric publication with the continuing Strength Assessment attendance-parity gates.

## Validation

All 141 Operating Data Hub and PT Minder preflight tests pass. Production verification confirms the accepted dashboard remains intact, the last-week, 28-day and 90-day preview selections render correctly, the hub is healthy and unauthorised cash ingestion is rejected.
