# Reporting V2 Owner Decision Pack

**Date:** 2026-07-29  
**Purpose:** Decisions required before the affected V2 metrics can move beyond shadow  
**Current workbook and dashboard authority:** Unchanged

## Decisions

| ID | Decision | Recommended starting rule | Blocks |
|---|---|---|---|
| RV2-01 | Assessment-to-sale attribution window | **Approved:** attribute a qualifying agreement to the most recent attended Strength Assessment within 30 completed days; retain the original assessment cohort | Unique conversion |
| RV2-02 | Returning former members | **Approved:** report as `reactivation`, not new acquisition, unless the person has no prior accepted membership activation | Conversion and growth |
| RV2-03 | Late sale after No Sale | **Approved:** update the original attended-assessment cohort when the agreement is inside RV2-01; retain both the original No Sale feedback and later sale event | Unique conversion |
| RV2-04 | Repeated assessments | **Approved:** keep genuinely delivered repeated assessments separate; group only cancellations/rebooks and proven duplicate corrections | Booking, attendance and conversion |
| RV2-05 | Stripe cash date | Use the successful settled payment timestamp; report a later refund as a negative event on the refund date | Cash |
| RV2-06 | PT Minder cash date | Use only the successful payment transaction time captured from PT Minder; ignore Charge and displayed balance | Cash |
| RV2-07 | Bank cash | Allow only independently approved manual bank cash with a transaction reference | Cash |
| RV2-08 | Million-dollar measure | **Approved with amendment:** track accepted cash excluding GST over a continuously rolling 365-day window. There is no calendar-year or financial-year reset. Do not calculate management turnover. Keep accounting turnover off the dashboard until it can be supplied reliably by the accounting system. | Cash goal |
| RV2-09 | Active client | Count one canonical person with current paid/entitled access, including paid-in-advance, approved hold and notice-period access; future starts become active on effective date | Active clients and growth |
| RV2-10 | Historical confidence | Official board totals may use `verified` and `high`; `medium` is shown separately; `low` and `legacy_aggregate` are trend context only | Historical board pack |
| RV2-11 | Manual-input ownership | Admin Eve submits operating evidence; Peter approves financial, identity, lifecycle and target inputs; define an absence cover before production | Manual input |
| RV2-12 | Google board pack | Create a separate controlled V2 workbook after the first three metric families pass, then freeze the current workbook after full cutover | Google Sheet transition |

## Acceptance Method

Record each decision as:

- Approved;
- Approved with amendment;
- Deferred; or
- Rejected.

Every approved decision receives:

- decision date;
- decision owner;
- resulting metric-definition version;
- effective date;
- affected historical periods;
- required backfill or parallel-run reset.

No decision should be implemented by editing an old metric definition in place. A material definition change creates a new version.

## Decision Log

| Decision | Status | Decided by | Date | Result |
|---|---|---|---|---|
| RV2-01 to RV2-04 | Approved | Peter Brown | 2026-07-29 | The governed acquisition rules use a 30-day most-recent-attended-assessment window, classify returning former members as reactivations, allow a late qualifying sale to convert the original assessment cohort, group cancellations/rebooks into one appointment series and retain genuinely repeated delivered assessments separately. |
| RV2-08 | Approved with amendment | Peter Brown | 2026-07-29 | The CEO goal uses accepted cash collected excluding GST over the immediately preceding 365 days, ending at the latest accepted refresh. There is no calendar-year or financial-year reset. Refunds remain negative cash events. Internal transfers and duplicate processor records are excluded. The dashboard records the first time the rolling total reaches $1 million as an achieved milestone while continuing to display the current rolling total. Management turnover is removed; accounting turnover remains unavailable until a reliable accounting-system feed exists. |
