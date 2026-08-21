# PT Minder Purpose-Aware Transaction Classification

**Status:** Live  
**Date:** 27 July 2026

## Problem

The accepted PT Minder V1 snapshot stores one latest payment projection per client. That is unsafe when one client has recurring membership payments and separate pay-as-you-go PT purchases.

Anne Leditschke is the acceptance case: her recurring $69 Evolved Anywhere membership belongs in recurring run-rate, while her manual $60 or $120 PT purchases are variable cash and create only the purchased PT session entitlement.

## Design

1. Extend the PT Minder contract to accept an optional bounded transaction list per client.
2. Classify each transaction on two axes: service type (`sgpt`, `personal_training`, `other`) and cadence (`recurring`, `ad_hoc`, `other`).
3. Preserve the account-level recurring projection for revenue run-rate.
4. Build PT parity evidence only from the latest completed `personal_training` transaction.
5. Treat V1 snapshots without transaction detail as insufficient for PT cutover rather than using an unrelated latest payment.
6. Keep all existing production reports on their protected inputs until two purpose-aware parity cycles pass.

## Validation

- Contract rejects malformed, duplicated or unclassified transaction records.
- Anne fixture produces $69 recurring revenue and a separate PT entitlement.
- A membership-only payment is never consumed as PT evidence.
- Existing V1 snapshots remain readable but cannot become cutover-eligible for PT.
- Affected hub, reporting and revenue-controller tests pass.

## Deployment

Deploy the hub contract first, then the PT Booking Shadow consumer. Do not change PT Minder, payment, booking or client records. Railway remains the only scheduler.

Completed on 27 July 2026:

- Hub commit `a844568`
- PT Booking commit `8d70454`
- PT Railway deployment `f67ead1b-6aaf-4094-b274-95dbc9d0fe42`
- 115 affected tests passing
- Anne recurring evidence corrected to $69 with a protected pre-change backup
- Live parity improved to 22 exact and two explained mismatches
- V1 snapshot correctly blocked from cutover as `source_contract_incomplete`

The first complete V2 capture was accepted later on 27 July as
`20260727T082105Z-5a9058f4`. It contains 27 active accounts and 540 actual
Ezidebit payment events. PT Minder's internal Charge entries and displayed
balances are excluded.

The capture also established an explicit normalized weekly rate from the live
recurring schedule. This prevents a resumed pending debit or a fortnightly
collection interval from distorting weekly run-rate. Historical recurring
product changes no longer create a false simultaneous-stream ambiguity.

- Hub deployment `558a2f5b-35e8-4119-b361-fca6935e9a38`
- PT Booking deployment `1b6214c9-fb5b-40f5-b5e0-efcc3067bb54`
- 118 affected tests passing
- Zero ambiguous recurring accounts
- Read-only parity: 15 exact, nine mismatched, one hub-only and zero legacy-only
- Cutover remains blocked until the protected differences are individually
  inspected and resolved

The protected review completed later on 27 July. It identified two source
projection defects before any register change: a historical retry could
overwrite the real current due date, and a product explicitly marked paused
could still appear as collecting when the client record itself remained active.

PT Booking deployment `fee1b5ad-0235-4fdf-9fc4-dc523014cee1` corrects both
conditions. Seven evidence-backed protected rows were then refreshed, with the
pre-change register retained at
`/data/revenue-gap-control/legacy-payment-evidence.pre-v2-final-reconcile-20260727.csv`.
The resulting production comparison is 24 of 24 exact, with zero field
differences, zero hub-only or legacy-only rows and zero ambiguous recurring
accounts. All 146 affected tests pass.

This is the first clean V2 parity cycle. Existing calculations retain the
protected register until a second independent PT Minder capture also passes;
the next owner login and capture is due during the week beginning 3 August
2026.
