# Revenue Control Commercial Evidence Promotion

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

The existing Railway Revenue Control audit now publishes exact service-level
commercial evidence into the shared operating-data hub:

- 132 governed active clients;
- 143 governed SGPT/PT relationships;
- 93 clients fully covered across every governed service, up from 68;
- 39 clients with incomplete coverage, down from 64;
- 41 uncovered service relationships, down from 68;
- seven current exception buckets;
- 25 high-priority service gaps.

The former `collecting_not_shared` bucket is now empty. Of its 30 historical
service gaps, 24 gained confirmed commercial evidence and six were reclassified
from the latest audit. Three additional gaps from other historical buckets also
gained valid current evidence, producing a net reduction of 27 service gaps.

## Promotion Rules

- The canonical identity and SGPT/PT service must match exactly.
- `CLEAN_COLLECTING` promotes only when the completed audit also contains a
  current successful Stripe receipt, a current approved PT Minder/EziDebit
  receipt, or current approved external-payment evidence.
- A source limitation or incomplete invoice run blocks the entire promotion.
- Non-clean assessments publish only as pending queue context and cannot create
  entitlement.
- Duplicate same-service roster rows become pending owner review. They cannot
  block other clients or create confirmed entitlement.
- PT Minder displayed balances and its Charge function remain excluded.
- Queue cases remain evidence states and are not automatically debts.

## Production Verification

- Accepted commercial snapshot:
  `20260727T232032Z-65c36279`.
- Hub deployment:
  `d5b4c7a5-d85f-4770-a668-a9601623959f`.
- PT/Revenue deployment:
  `7c295d70-ddd2-46a6-9ef8-a9b3e492d1a8`.
- 218 connected hub and controller tests passed.
- The CEO dashboard was visually verified at 93 commercially verified clients,
  39 pending clients, 41 service gaps and seven buckets.
- Current Google roster parity remains exact.
- No client, payment, membership, booking or Google Sheet record was changed.
- No new schedule was created; the existing Railway audit remains the publisher.

## Next Build

This purpose-aware split was completed later on 28 July. The former 17-gap
bucket resolved into two PT services booked with unresolved payment and 15
services with no current authoritative payment evidence. The six PIA or
prepaid-pack gaps are the next bounded evidence-integration opportunity.
