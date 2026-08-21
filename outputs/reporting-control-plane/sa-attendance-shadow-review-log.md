# Strength Assessment Attendance Shadow Review Log

**Definition:** `sa-attendance-v1`  
**Started:** 29 July 2026  
**Write mode:** GHL off; Google Sheets off  
**Acceptance owner:** Peter Brown

## Baseline freeze: 29 July 2026

| Check | Result |
|---|---|
| Approved active calendar | `HSVEzfJH4nice96IxHem` |
| Assigned assessment users | Megan Brown, Piper Mae, Nora Silva |
| 90-day GHL events | 82 |
| Elapsed events | 79 |
| Elapsed Confirmed | 60 |
| Elapsed Cancelled | 19 |
| Elapsed Showed | 0 |
| Elapsed No show | 0 |
| Missing event IDs | 0 |
| Appointments attendance control | Manual Y/N dropdown in column K |
| Sheet elapsed audit | 215 Y, 26 N, 3 blank across 244 elapsed rows |
| Sheet integrity conflicts | Two July converted rows had blank K; all 107 elapsed rows through February were Y |
| KPI ownership | Rows 57 to 63 depend on Appointments K |
| Discord ownership | Reads Appointments K as `showed` |

The baseline contains no member-identifying information.

## Capability gates

| Gate | Status | Evidence or next action |
|---|---|---|
| Exact active calendar IDs confirmed | Passed | Live API and system register agree on `HSVEzfJH4nice96IxHem` |
| GHL exact-event status update | Pending | Verify native action or exact appointment API against a controlled test event |
| Feedback webhook authentication header | Pending | Verify workflow custom-webhook header support; otherwise use a rotated signed token |
| Existing Consultant Feedback form preserved | Passed | Form `Z83KtjAPMclhe8bsFJwS` and workflow `6d3cd8f8-890d-462a-b023-89f31114d2a9` remain the operating path |
| Delivering-coach field | Pending live update | Required options: Megan, Piper, Nora, Katrina, Leisa, Approved cover / other |
| Historical KPI restatement | Not authorised | Separate owner decision required after backfill |
| Governed Sheet mirror | Prepared, writes disabled | `SA Attendance` tab ID `1446062006`; exact 15-column header, filter and warning protection verified |

## Shadow-cycle acceptance

Two complete Monday-to-Sunday cycles are required. Do not enable either writer until both rows are complete and every discrepancy has an owner decision.

| Cycle | Period | Event match | Feedback match | Elapsed unresolved | K disagreement | Duplicate/reschedule | Terminal conflicts | Incorrect Showed proposals | Accepted |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Pending | — | — | — | — | — | — | — | No |
| 2 | Pending | — | — | — | — | — | — | — | No |

## Activation checklist

- [ ] Two complete reporting cycles reviewed.
- [ ] No partial calendar run was accepted.
- [ ] Zero incorrect automatic Showed proposals.
- [ ] Controlled test appointment updated correctly.
- [ ] One reviewed production feedback event updated correctly.
- [ ] First 20 production closures monitored.
- [ ] Sale, No Sale, agreement, No Show and Cancelled workflows show no duplicate enrolment or message.
- [ ] Governed Sheet mirror and every reporting consumer agree.
- [ ] Peter Brown approves Sheet publication.
- [ ] Peter Brown approves GHL write activation.

## Historical backfill: 29 July 2026

The read-only 120-day run compared 251 legacy Sheet rows with 109 GHL appointment events. It produced 85 corroborated matches, zero ambiguous matches and 166 unmatched legacy rows; no record was promotion-eligible because column K alone cannot prove Showed.

Identified detail remains under `data/private/integration-reporting/`. No GHL record, Sheet row or historical KPI cell was changed.

## Decision log

| Date | Decision | Owner | Evidence |
|---|---|---|---|
| 29 Jul 2026 | Build and deploy the reconciliation layer in shadow mode; keep both write gates off | Peter Brown | Existing GHL status history is not reliable enough for immediate cutover |
| 29 Jul 2026 | Create the empty governed Sheet mirror but leave publication disabled | Peter Brown | Tab `SA Attendance`, ID `1446062006`; legacy Appointments K and KPI cells unchanged until two-cycle acceptance |
| 30 Jul 2026 | Listed show-rate history begins 12 Mar 2026; listed conversion history begins 19 Sep 2025 | Peter Brown | Appointments K contains the explicit listed Y/N outcome from 12 Mar. Appointments L remains the approved conversion history for the full list. Before 12 Mar, surviving rows are legacy attended for conversion only because no-shows and cancellations were deleted. K=`N` is not reclassified as cancellation. |

## Approved historical boundaries: 30 July 2026

- `sa_listed_show_rate` begins on 12 March 2026. Its numerator is K=`Y`; its denominator is K=`Y` plus K=`N`. Blank rows are excluded.
- `sa_listed_conversion_rate` begins on 19 September 2025. Before 12 March 2026, surviving rows form the legacy attended denominator. From 12 March onward, only K=`Y` rows enter the attended denominator. L=`Y` is the converted numerator.
- The listed rates are confidence-labelled historical comparison metrics. They do not replace the governed event-level show, cancellation or unique-conversion metrics without acceptance.
- Appointments K has no separate cancellation state. An `N` is never interpreted as cancellation.
- The current workbook and its formulas remain unchanged.
