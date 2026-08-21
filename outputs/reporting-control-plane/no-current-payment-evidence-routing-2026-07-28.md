# No-Current-Payment Evidence Routing

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

The former 15-client `no_current_payment_evidence` bucket has been eliminated.
Every case now follows the payment rail and corrective action supported by its
current evidence.

| Evidence route | Clients | Priority | Required action |
| --- | ---: | --- | --- |
| PT Minder collecting, parity pending | 5 | Medium | Retain in shadow until the second independent capture passes exact parity. |
| Recent Stripe receipt, paid-through date unresolved | 7 | High | Add the covered service-period or final-access end date before entitlement promotion. |
| Payment retry in progress | 1 | High | Track the specific failed debit and retry outcome. |
| Payment paused, roster active | 1 | High | Confirm the approved hold window or payment resumption. |
| Payment purpose does not match roster service | 1 | High | Correct the payment purpose or governed service; do not transfer evidence across services. |

## Material Dashboard Change

- Commercially verified clients remain 99.
- Pending clients remain 33.
- Service gaps remain 35.
- High-priority service gaps fall from 25 to 20.
- Action buckets increase from seven to ten because one ambiguous bucket is now
  separated into operationally distinct routes.
- Owner decisions required remain zero.

The five PT Minder cases are not promoted yet. Their evidence is current, but
the architecture requires a second independent capture before the protected
register can be replaced.

## Classifier Correction

The shared purpose classifier now prevents `SGPT` from matching the `PT`
substring. Explicit SGPT descriptions and Bronze, Silver or Gold package
descriptions map to SGPT; explicit PT, 1:1 and personal-training descriptions
remain personal training.

This correction affects evidence routing only. It does not infer entitlement
from payment amount, displayed PT Minder balances or PT Minder Charge entries.

## Verification

- Hub deployment:
  `dd9635f7-92d4-4bc2-a1e8-45cf5cd516fa`.
- Governed cohort:
  132 active clients and 143 service relationships.
- Commercial state:
  99 verified, 33 pending and 35 service gaps.
- 233 automated tests passed.
- No member, payment, booking, contact or Google Sheet record was changed.
- No new schedule was created.

## Next Build

Completed by
`outputs/reporting-control-plane/stripe-invoice-coverage-periods-2026-07-28.md`.
The seven receipts are one-time invoices with no ongoing Stripe coverage term;
the next build is a governed purchased-service-term record.
