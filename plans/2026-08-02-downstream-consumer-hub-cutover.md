# Downstream Consumer Cutover to the Canonical Hub

**Date:** 2 August 2026  
**Status:** In progress; Revenue production shadow evidence recorded, scheduled
acceptance pending  
**Owner:** Peter Brown  
**Implementation task:** Build 6 of 7

## Decision

Retention Intelligence, Conversation Triage, PT Booking Continuity and Revenue
Control will consume the protected, versioned Hub current-person contract for
identity, lifecycle, current service, entitlement and payment evidence. They
will use the Hub reporting period supplied with that contract.

The four services keep their domain-specific source reads:

- Retention keeps governed Trainerize engagement reads until the existing
  Trainerize Performance feed supplies the required member-level usage grain.
- Conversation Triage keeps GHL unread-conversation and message reads.
- PT Booking Continuity keeps GHL calendar and appointment reads.
- Revenue Control keeps only evidence that is not yet supplied by an accepted
  Hub snapshot, including report-rendering inputs and approved manual timing
  controls.

No consumer may cut over merely because a Hub response is available. Each must
publish an exact scheduled shadow comparison to the Hub's durable parallel
results ledger. The registered gate requires two distinct equivalent scheduled
cycles, an acceptance record and explicit approval. A stale, incomplete,
blocked, version-mismatched or unapproved contract fails closed to the existing
legacy read path and records the degraded state.

## Production evidence, 2 August

The fresh Revenue schema-v2 publisher produced 145 active governed service
relationships. The Hub contract reports 132 complete and 13 incomplete:
weekly allocation is absent from seven PT and six SGPT relationships, and
contracted weekly frequency is also absent from three of those PT
relationships.

The first correctly scoped protected Revenue comparison is
`8581398ffc1053858cc46bc69e8f7b61`, from no-email run
`6fa9fae7-dddb-46da-85f8-0cef4b5d3523`. It compared 138 legacy roster people
with 131 Hub-linked people: seven legacy-only identities, zero Hub-only
identities and 130 classification differences. It therefore failed closed to
the existing legacy report. Because this was manually initiated deployment
verification, the acceptance controller correctly reports zero of two
scheduled cycles.

## Duplicate calculation and source-call inventory

| Consumer | Duplicate identity/current-state logic | Direct sources to retire after verified replacement | Domain reads/delivery to preserve |
| --- | --- | --- | --- |
| Retention Intelligence | Local identity-link loading and canonicalisation; latest reconciliation SQLite selection; Trainerize-active roster selection; GHL-active, Stripe-entitled, cancellation/final-access and membership-service projection; local Monday week start | `scripts.membership_reconciliation.run_reconciliation`; local reads of `identity_register`, `exceptions` and `trainerize_clients` for person/lifecycle/service/entitlement | Trainerize calendar engagement metrics, private Railway retention store, existing protected preview and disabled-by-default Sheet delivery |
| Conversation Triage | GHL tag rules recreate SA prequalification, active SGPT and active PT status for each contact; Brisbane extraction date is not attached to a governed reporting contract | GHL contact membership/service tag interpretation after Hub person lookup parity | GHL unread conversations and recent messages, Claude classification, Discord and email report delivery |
| PT Booking Continuity | GHL tags/pipeline stages recreate PT cohort and service; hold/cancellation fields recreate lifecycle; local email/phone aliases recreate person matching; direct Stripe, Trainerize, Google roster, PT Minder and revenue-controller evidence recreate entitlement/payment | Contact/opportunity cohort extraction for current-service authority; duplicate cross-system commercial extraction; local commercial-state joins; local week projection when the Hub period is accepted | GHL calendars and appointments, recurrence/coverage reconciliation, private findings, Admin email, existing KPI delivery gate |
| Revenue Control | Fresh membership reconciliation recreates identity/lifecycle/service/payment; local SQLite joins and email/phone fallback; Google active roster recreates service; PT Booking private database dependency; local reporting window derivation | `_membership_reconciliation`; `load_membership_evidence`; current-service and payment projections that have exact Hub replacements; private module-to-module booking-table reads after identified Hub continuity contract is available | Existing exception/cash bridge generation, private artifacts, Peter email, approved manual timing and purchased-service controls |

## Shared contracts

- Protected current-person read:
  `GET /api/v2/reporting/current-people?period=week|28d|90d`.
- Lifecycle read:
  `GET /api/v2/reporting/membership-lifecycle?period=...`.
- Durable comparison write:
  `POST /api/v2/reporting/parallel-results`.
- Hub cutover/acceptance status: supplied by Builds 4 and 5; it is the authority
  for promotion and rollback.
- Domain sources continue through
  `GET /api/v1/sources/<source>/latest` where a source snapshot, rather than a
  canonical-person projection, is the correct grain.
- `sgpt-delivery-v1` supplies person-keyed delivered class-session assignment,
  trainer, duration, explicit booking/outcome evidence and governed
  capacity/fill. It is not commercial roster authority and must not be used to
  infer product, contracted frequency, service duration or PT allocation.

The protected person contract carries Hub `person_id`, GHL and Trainerize source
IDs, lifecycle, service relationships, entitlements, payment accounts and
events, explicit completeness/block reasons, source freshness, and a governed
Brisbane period. Schema-v2 governed roster attributes are now person-linked,
but production remains incomplete until a fresh candidate is accepted and
promoted. Identified detail must never be copied into aggregate Hub summaries
or share-safe reports.

## Consumer comparison registrations

| Consumer | Metric ID | Definition version | Exact projection |
| --- | --- | --- | --- |
| Retention Intelligence | `consumer_retention_intelligence_contract` | `retention-hub-read-v1` | Trainerize source ID, active lifecycle, current service, entitlement confidence and operational-exception state |
| Conversation Triage | `consumer_conversation_triage_contract` | `conversation-triage-hub-read-v1` | GHL contact ID, SA prequalification, active SGPT and active PT flags, unresolved identity state |
| PT Booking Continuity | `consumer_pt_booking_continuity_contract` | `pt-booking-hub-read-v1` | GHL contact ID, lifecycle state, current PT relationship, governed hold/end state and commercial-support classification |
| Revenue Control | `consumer_revenue_control_contract` | `revenue-control-hub-read-v1` | Hub person ID, active service relationship, lifecycle class, entitlement/payment class and booking-evidence class |

Every comparison includes distinct legacy and Hub source run IDs, the scheduled
comparison cycle, exact identity/classification fingerprints and the complete
set-difference counts. Count parity without identical identities and
classifications fails.

## Cutover and fallback

1. Fetch and strictly validate the versioned current-person contract.
2. Produce the legacy result without changing delivery.
3. Produce the Hub projection.
4. Compare exact identities and classifications.
5. Publish the scheduled comparison to the Hub ledger.
6. Keep the legacy read authoritative until the Hub reports two distinct passed
   cycles plus accepted and explicitly approved cutover state.
7. Switch one consumer only; preserve its report delivery.
8. If the contract becomes missing, stale, blocked, incompatible or loses
   approval, restore the legacy read path and mark the run degraded. Never infer
   a favourable lifecycle, service or payment state.
9. Retire only the duplicate calculation or extraction proved replaced for that
   consumer.

## Acceptance

- Two distinct scheduled, complete and exact comparisons per consumer.
- Exact identity and classification parity; zero unexplained events and cents.
- Protected identified output remains protected.
- Existing report destination, schedule and deduplication remain unchanged.
- No member message, membership/payment mutation or Google Sheet write occurs.
- Railway remains the sole scheduler.
- Focused tests and the affected service suites pass.
- Production deployment and a fresh protected verification prove the cutover
  and rollback states before retirement.
- Revenue's commercial roster fields are available on canonical person-keyed
  service/entitlement relationships before its legacy enrichment is retired.
- The coordinated latest Hub deployment is confirmed before Revenue publishes
  and promotes its first fresh schema-v2 roster cycle.
