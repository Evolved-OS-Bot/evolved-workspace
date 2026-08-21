# Seven One-Time Invoice Reconciliation

Date: 29 July 2026
Runtime: Railway only
Mode: Read-only against Stripe, GHL, Trainerize, booking and Google Sheet
systems

## Outcome

All seven one-time Stripe invoice cases were reconciled from exact payment,
agreement and service evidence. Eight purchased-service terms were loaded into
the protected PT/revenue Railway register.

The eighth term is intentional: Grace Arnell's Fast Track purchase includes
both unlimited SGPT and one weekly 30-minute PT session during the four-week
onboarding period.

## Evidence Rule

The GHL membership agreement records:

- the membership selected;
- the agreement date;
- today's upfront cost; and
- that the regular weekly debit begins in week 4 to pay for week 5.

Stripe independently confirms the paid invoice, customer, product and service
description. These records establish a four-week onboarding term without
inferring duration from price.

## Approved Terms

| Client | Service | Effective period | Payment evidence |
| --- | --- | --- | --- |
| Grace Arnell | SGPT | 13 July to 9 August | $599 Fast Track invoice |
| Grace Arnell | Four 30-minute PT sessions | 13 July to 9 August | Same $599 Fast Track invoice |
| Hannah Hobman | SGPT | 14 July to 10 August | $399 membership invoice |
| India Armstrong | SGPT | 20 July to 16 August | $399 membership invoice |
| Jade Wright | SGPT | 20 July to 16 August | $399 membership invoice |
| Jess Michels | SGPT | 3 July to 30 July | $399 membership invoice |
| Tara Berge | SGPT | 6 July to 2 August | $50 deposit plus $349 balance |
| Vineela Velaga | SGPT | 15 July to 11 August | $399 membership invoice |

Tara's two invoices are stored on one governed term. Neither partial payment
can independently prove the full onboarding entitlement.

## Production Result

| Measure | Before | After |
| --- | ---: | ---: |
| Commercially verified clients | 100 | 107 |
| Clients pending evidence | 32 | 25 |
| Service gaps | 34 | 26 |
| High-priority service gaps | 20 | 13 |
| Evidence buckets | 10 | 8 |
| Owner decisions required | 0 | 0 |

Eight service gaps cleared across seven clients because Fast Track contained
both the SGPT and PT service components.

## Verification

- Split-payment support deployment:
  `42906eda-5c60-4464-aafd-0c091a52ab3e`.
- Protected term register:
  eight rows accepted.
- Term register fingerprint:
  `989e7b935299c4b9f197b8435aa6b21855e2afcc3e1e3cdce895c2a5060582ea`.
- Accepted commercial snapshot:
  `20260728T200040Z-3471db6d`.
- Automated tests:
  250 passed.
- No new schedule was created.
- No Stripe, GHL, Trainerize, booking or Google Sheet record was changed.

## Next Work

The highest-leverage remaining commercial exceptions are:

1. one paused payment account with an active roster service;
2. one payment-purpose mismatch; and
3. two PT services with future bookings but unresolved payment purpose.

