# Governed Purchased-Service Terms

Date: 28 July 2026
Runtime: Railway only
Mode: Read-only against member, payment, booking, contact and Google Sheet
systems

## Outcome

The PT/revenue Railway service now owns a protected purchased-service-term
register for one-time Stripe invoices.

An approved record must bind:

- a unique term ID;
- the Stripe invoice ID;
- purchaser and beneficiary email;
- exact SGPT or personal-training service;
- optional quantity and unit;
- effective start and end dates;
- approved or revoked state; and
- approval owner and approval date.

The same existing Railway commercial-evidence refresh publishes approved terms
to the hub. The hub retains the Stripe invoice reference in the entitlement
audit metadata.

## Fail-Closed Behaviour

- Invalid, duplicate, incomplete or backwards-dated records are rejected.
- Quantity and unit must be supplied together.
- Revoked terms cannot confirm entitlement.
- Future terms do not count before their start date.
- Expired terms stop counting after their end date.
- Future and expired terms have separate CEO-dashboard action buckets.
- No duration is inferred from invoice amount, payment status, roster state,
  GHL lifecycle state or Trainerize access.

## Production Verification

- Hub deployment:
  `11d9b957-7d0f-4f26-9b85-bf45b3b799ec`.
- PT/revenue deployment:
  `bd62a547-5f4d-4d75-a1f8-7e1bd9e39150`.
- Accepted commercial snapshot:
  `20260728T043939Z-53b2d6a5`.
- Protected purchased-service-term register:
  live and currently empty.
- Automated tests:
  249 passed.

The empty register is deliberate. No client is promoted until the exact
service terms are confirmed.

## Dashboard State

| Measure | Live value |
| --- | ---: |
| Confirmed active clients | 132 |
| Active service relationships | 143 |
| Commercially verified clients | 100 |
| Clients pending evidence | 32 |
| Service gaps | 34 |
| High-priority service gaps | 20 |
| Owner decisions required | 0 |

The seven one-time invoices remain in
`one_time_invoice_entitlement_term_missing`. This proves that deploying the
register did not infer or fabricate entitlement.

## Next Action

Completed by
`outputs/reporting-control-plane/seven-one-time-invoice-reconciliation-2026-07-29.md`.
The register now contains eight terms for the seven purchases.
