# KPI Revenue Gap and Active Client Audit

**Run:** `fa52ec2f-fa81-42ed-b0d2-092ced5dfc6f`  
**Window:** 2026-07-20 to 2026-07-26  
**Cash source:** KPI AV106 dated 2026-07-27; manually confirmed bank input  

## Control Totals

| Measure | Value |
|---|---:|
| SGPT numeric allocation | $8,957.00 |
| PT numeric allocation | $3,778.00 |
| Combined numeric allocation | $12,735.00 |
| PIF or PIA rows | 12 |
| Approved pauses | $597.00 |
| Arrears | $902.00 |
| Future starts | $50.00 |
| Confirmed current income | $8,786.00 |
| Scheduled run-rate | $9,334.00 |
| Cleared cash | $10,927.24 |
| Named timing items | $0.00 |
| Unexplained variance | $-2,141.24 |

## Classification Counts

| Classification | Clients |
|---|---:|
| ACTIVE_PIA | 1 |
| APPROVED_FUTURE_START | 1 |
| APPROVED_PAUSE | 4 |
| Active - ARREARS | 9 |
| BOOKING_PAYMENT_UNRESOLVED | 22 |
| CLEAN_COLLECTING | 94 |
| LIFECYCLE_EXCEPTION | 1 |
| PACK_RENEWAL_DUE | 3 |
| PIF_PACK_IN_DELIVERY | 8 |

## Exception Counts

| Exception | Count |
|---|---:|
| Active - ARREARS | 9 |
| BOOKING_PAYMENT_UNRESOLVED | 22 |
| LIFECYCLE_EXCEPTION | 1 |
| PACK_RENEWAL_DUE | 3 |
| SOURCE_READ_FAILURE | 1 |

## Duplicate Controls

No duplicate email exists within either active service sheet.

## Source Limitations

- Trainerize product subscriptions, Class Access add-ons and credit balances are not included because reliable API reads are not yet verified.
- GHL membership tags and pipeline stages contain known historical inconsistencies, so they are evidence signals rather than a standalone entitlement ledger.
- No automatic access, billing or lifecycle changes are permitted from this report.
- SOURCE: PT booking snapshot not found: /Users/peterbrown/evolved-workspace/data/private/revenue-gap-control/pt_booking_shadow.sqlite

## Close Status

The cash bridge remains open and requires named owned evidence.
