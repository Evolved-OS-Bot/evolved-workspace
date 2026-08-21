# Reporting V2 Metric Cutover Report

**Date:** 2 August 2026  
**Owner authority:** Peter Brown  
**Status:** Cutover controls complete; metric promotion remains evidence-gated  
**Production release:** `38c0d667-b23c-4bae-865f-fecc33e1a184` — SUCCESS

## Outcome

The Operating Data Hub now controls Reporting V2 publication one exact metric
and definition at a time. Technical readiness, owner acceptance and effective
publication are separate states. Reporting V2 is the target CEO surface, while
the accepted CEO dashboard and KPI workbook remain unchanged for every metric
that has not completed cutover.

The protected preview keeps Cash & Goal first, the five pillars, completed
week/28-day/90-day controls and useful V1 delivery markers. Every metric is
labelled accepted, eligible for owner approval, shadow, legacy, unavailable or
rolled back.

## Promotion result

**Metrics promoted:** 0

No metric had the complete combination of current observation, source
freshness, required distinct scheduled comparison cycles, zero unexplained
events/cents, immutable Build 4 acceptance and Peter's exact owner acceptance.
The build therefore added no publication decision and changed no accepted CEO
or KPI workbook value.

| Metric family | Definition | Effective result | Remaining gate |
|---|---|---|---|
| Website visitors, unique subscribers and visitor-to-subscriber rate | `website-marketing-v1` | Shadow | Complete required distinct scheduled comparisons and exact acceptance |
| Subscriber-to-assessment booking | `ghl-subscriber-sa-booking-v1` | Shadow | Complete required distinct scheduled comparisons and exact acceptance |
| Strength Assessment show rate | `sa-attendance-v2` | Unavailable/blocked | Resolve terminal-outcome coverage, then pass parity |
| Unique assessment conversion | `assessment-conversion-v1` | Shadow | Complete required distinct scheduled comparisons and exact acceptance |
| Cash & Goal | `cash-goal-v1` | Legacy plus V2 shadow | Complete accounting/parity gates and exact acceptance |
| Operating expenses | `operating-expenses-v2` | Shadow | Complete scheduled Xero observations and exact acceptance |
| Cash accounting validation | `cash-accounting-validation-v1` | Validation-only | Close accounting timing/reconciliation evidence |
| SGPT delivery | `sgpt-delivery-v1` | Shadow with V1 context | Complete source coverage and two scheduled comparisons; never infer attendance |
| Membership lifecycle/attrition | lifecycle shadow contract | Unavailable where ambiguous | Build historical opening cohort and retain ambiguous-date quarantine |
| Evolved Standards | `evolved-standards-v1-shadow` | Component and complete-score shadow | Apply `evolved-standards-future-proofing-score-v1`, complete source evidence and exact metric acceptance; never invent an overall Live/Long/Perform label |
| Four downstream consumer contracts | versioned Hub-read v1 contracts | Legacy fallback | Two distinct clean scheduled reads and exact acceptance for each consumer |

## Shared consumer definitions

- `consumer_retention_intelligence_contract` / `retention-hub-read-v1`
- `consumer_conversation_triage_contract` / `conversation-triage-hub-read-v1`
- `consumer_pt_booking_continuity_contract` / `pt-booking-hub-read-v1`
- `consumer_revenue_control_contract` / `revenue-control-hub-read-v1`

Each consumer remains fail-closed to its legacy reader unless the Hub reports
`promotion_authorised=true` for the exact metric and definition.

Revenue additionally requires complete schema-v2 person-linked governed roster
relationships and current exact parity. Missing roster attributes,
classification/fingerprint disagreement or any Hub projection failure restores
the already-generated legacy report. The Hub path does not reuse legacy
email-keyed payment overrides. No fresh scheduled parity cycle was created by
the deployment.

Revenue deployment `e7547ab4-3b5c-48d1-a73d-8eb465a8c720` succeeded. Protected
manual verification result `8581398ffc1053858cc46bc69e8f7b61` compared legacy
138 with Hub 131: seven legacy-only, zero Hub-only, 130 changed and 137
unexplained events, with zero unexplained cents. Source freshness passed, but
only 132 of 145 governed roster relationships were complete. The Hub therefore
reported shadow, `promotion_authorised=false`, zero of two scheduled cycles and
no acceptance record or owner approval. This manual run is deployment evidence,
not scheduled acceptance evidence.

## Gate and evidence model

The Hub joins:

1. an immutable metric definition;
2. the current period observation and confidence;
3. source completeness and freshness;
4. the required distinct scheduled parallel cycles;
5. zero unexplained events and cents;
6. Build 4's immutable acceptance record and fingerprint; and
7. Peter's exact metric-level approval.

Only the first six can make a metric eligible. The seventh is the only route to
`v2_accepted`.

## Rollback and parity

Publication decisions are append-only. Peter is the publication and rollback
authority. Rollback is isolated to the exact metric and definition, preserving
all other accepted V2 metrics and restoring the governed V1 fallback when one
exists.

Current-gate failure is automatic and separate from rollback. If an accepted
metric later becomes stale, incomplete, low-confidence or mismatched, the CEO
surface shows it as unavailable without erasing the prior acceptance record.

## Presentation and workbook boundary

The Reporting V2 preview is the target CEO presentation. The Google board-pack
contract remains compact and non-publishing; no workbook was created or cut
over because the first three metric families have not passed. The existing KPI
workbook remains the comparison and fallback surface and received no write.

## Verification

- Local cross-service test result: 442 passed after the final lifecycle,
  current-person and Revenue schema-v2 integration.
- Instruction-drift check: passed.
- Railway deployment: `38c0d667-b23c-4bae-865f-fecc33e1a184`,
  `SUCCESS`.
- Production health: HTTP 200, `mode=shadow`, scheduler enabled, 20 sources,
  zero stale sources.
- Protected cutover, lifecycle and current-person endpoints: HTTP 401 without
  the Hub secret.
- Protected CEO preview: HTTP 302 to login without a dashboard session.
- Promotion verification: zero authorised metrics and zero workbook writes.

## Remaining decisions

There is no broad dashboard approval to make. Once Build 4 marks an exact
metric/version `ready_for_owner_acceptance`, Peter should review that immutable
evidence fingerprint and approve or decline only that metric. Peter has
resolved the Evolved Standards rule: preserve individual levels and show only
the complete six-standard 0–18 Future-Proofing Score plus its defined band.
That rule decision is not publication approval.
