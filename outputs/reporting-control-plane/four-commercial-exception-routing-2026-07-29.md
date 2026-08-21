# Four Commercial Exception Routing

Date: 29 July 2026
Runtime: Railway only
Mode: Read-only against Stripe, PT Minder, GHL, Trainerize, bookings and
Google Sheets

## Outcome

The four-client review contained five service gaps. Three were routing defects
and two remain genuine operational conflicts.

No client was falsely promoted. Commercially verified clients remain 107 and
total service gaps remain 26.

## Corrected Cases

### Lauryn Brown

PT Minder confirms a $298 fortnightly Silver Package debit covering 16 to
29 July 2026. The package is the legacy $149 weekly Fast Track combination,
supporting both SGPT and one weekly PT component.

A failed debit recorded on 24 July was a retry for the old 12 to 25 March
period. The hub now selects the service period containing the governed date,
so that stale retry cannot override the completed current-period debit.

Both Lauryn service gaps moved from high-priority review to
`pt_minder_shadow_collecting`. They remain unverified until the second
independent PT Minder parity capture.

### Leonie Callaway

Stripe confirms a paid PT period from 28 July to 4 August 2026. The dashboard
cohort date is 27 July, so the payment correctly cannot cover that earlier
date.

The case now routes to
`confirmed_entitlement_starts_later`, a low-priority cohort-timing check rather
than a payment-purpose decision.

## Genuine Remaining Conflicts

### Emma Spowart

Stripe is paused and the last paid PT period ended on 21 July. The operational
record says a surgery hold was followed by a medical-cancellation request, but
GHL does not yet contain the completed hold or cancellation fields.

The case remains `payment_account_paused_roster_active`. Admin must obtain and
process the medical evidence or confirm payment resumption.

### Nirvana Searle

PT Minder shows a current $99 weekly product explicitly described as
`1:1 PT Leisa (2 x 30 mins)`. GHL tags Nirvana as an old PT client while the
governed roster retains active Bronze SGPT.

The PT payment cannot be transferred to SGPT. The case remains
`payment_service_mismatch` until the PT billing/service state or SGPT payment
source is corrected.

## Production Result

| Measure | Before | After |
| --- | ---: | ---: |
| Commercially verified clients | 107 | 107 |
| Clients pending evidence | 25 | 25 |
| Service gaps | 26 | 26 |
| High-priority service gaps | 13 | 9 |
| Evidence buckets | 8 | 8 |
| Owner decisions required | 0 | 0 |

## Verification

- Hub deployment:
  `a0b15bd4-a683-4bb2-8322-a72eb88846dd`.
- Reprocessed PT Minder snapshot:
  `20260728T201006Z-07091707`.
- Automated tests:
  253 passed.
- No new schedule was created.
- No Stripe, PT Minder, GHL, Trainerize, booking or Google Sheet record was
  changed.

