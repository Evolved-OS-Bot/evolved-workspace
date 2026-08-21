# Reporting V2 Immutable Membership Lifecycle Build

**Date:** 2 August 2026  
**Contract:** `membership-lifecycle-v1`  
**Mode:** Protected, read-only, shadow only  
**Lifecycle authority:** GHL  
**History and metric authority:** Evolved Operating Data Hub  
**Scheduler:** Railway only

## Outcome

The Hub now stores immutable, versioned membership lifecycle evidence and
calculates the completed week, rolling 28 days and rolling 90 days from one
governed contract. The accepted CEO dashboard and KPI workbook were not
changed.

Protected endpoints:

- `GET /api/v2/reporting/membership-lifecycle?period=week|28d|90d`
- `POST /api/v2/reporting/membership-lifecycle/backfill`
- `GET /api/v2/reporting/current-people?period=week|28d|90d`

All endpoints use the existing Hub bearer-token protection.

## Definitions

| Measure | Governed definition |
|---|---|
| Members joined | Unique canonical people with a first accepted membership activation inside the period. Fast Track counts once. |
| Final membership endings | Unique canonical people whose exact final membership access ends inside the period. |
| Active notice | People currently inside an accepted GHL cancellation-notice interval. |
| Straight cancellations | Final membership endings that retain no continuing membership service. |
| Downgrade-only transitions | A PT component ends while SGPT or Fast Track membership continues. This is not member loss. |
| Approved holds | Unique people inside an approved, exact effective GHL hold interval. Missing or malformed bounds are rejected. |
| Attrition rate | Unique final membership endings divided by the exact person-level opening cohort at period start. |
| Net unique-member growth | Unique membership activations less unique final membership endings inside the period. |

Every metric observation includes its numerator or count, source-event lineage,
Brisbane period and confidence state. A missing exact opening cohort produces
`Unavailable`; it never substitutes a nearby stock count.

## Immutable evidence and migration

Current lifecycle evidence enters through the existing membership
reconciliation publisher. No second GHL extractor or scheduler was introduced.
Repeated identical evidence deduplicates; changed evidence creates a new source
event version rather than overwriting history.

The protected backfill builder reads:

- the existing membership reconciliation SQLite history; and
- an already accepted active-client cohort decision snapshot.

The generated private bundle contained 54 lifecycle candidates. Four had an
exact effective date and complete verified/high-confidence evidence and were
accepted. Fifty ambiguous candidates were quarantined with explicit reasons.
One complete 127-person opening cohort dated 27 July 2026 was accepted. It does
not exactly match the current week, 28-day or 90-day period starts, so the
three attrition rates remain unavailable pending exact historical evidence.

## Current-person compatibility contract

`current-person-v1` is keyed by stable Hub `person_id`. Each protected row
contains:

- nullable display email, first name and last name, never used as identity keys;
- protected GHL contact and Trainerize user IDs;
- lifecycle state, effective/as-of time, confidence and source snapshot;
- active service relationships and effective bounds;
- current entitlements;
- payment accounts and latest payment-event evidence;
- the governed Brisbane period and cohort state;
- explicit completeness, missing, stale and ambiguous sections; and
- suppression reasons for approved holds, active notice, downgrade-only,
  staff/complimentary, resolved/inactive and unresolved lifecycle.

The schema-v2 governed active-roster relationship carries product, assigned
trainer, contracted weekly frequency, service duration, weekly allocation and
currency, contract length, effective bounds and source snapshot. These fields
are linked by `person_id` on both service relationships and entitlements.
Missing fields are explicit. Revenue Control's existing roster reader remains
the sole producer, so no duplicate extractor or Trainerize booking inference
was added. Existing production rows stay incomplete until the next schema-v2
roster cycle is accepted and promoted.

## Acceptance and publication controls

The lifecycle family writes shadow metric observations only. Promotion requires:

1. exact event and person-level source parity;
2. two distinct comparison/source cycles for every required period;
3. fresh source snapshots;
4. zero unexplained events and identity ambiguity;
5. an exact opening cohort for every attrition period;
6. metric-level technical acceptance; and
7. Peter's separate publication decision.

The Hub contract has no outreach, membership-change, payment or intervention
authority. Retention intervention remains proposal-only under its separate
workflow policy even if lifecycle evidence is accepted.

## Tests and acceptance comparison

The focused combined Hub, reporting-control and Revenue suite passes **396
tests**. Coverage includes:

- Fast Track counts once;
- PT-only ending on continuing SGPT/Fast Track is downgrade-only;
- exact final-access dates;
- missing and ambiguous historical dates quarantined;
- exact opening-cohort requirement for attrition;
- approved-hold validation;
- stable person-keyed current-person responses;
- person-keyed governed roster product, trainer, frequency, duration and
  allocation lineage;
- explicit missing/stale/ambiguous sections and suppression reasons; and
- protected-route authentication.

The Reporting Acceptance task independently confirmed all 223 Hub tests pass
after requiring two distinct comparison/source cycles in every readiness
fixture.

## Railway deployment and live verification

Production service: `Evolved Operating Data Hub`  
Current combined deployment: `386e8082-7c5d-4d90-a25e-f32d03871c29`  
Roster completeness repair deployment: `42c2e21e-e32b-42e9-baf2-894b1d11e45c`

Live verification covers:

- `/health`;
- all three lifecycle periods;
- protected current-person schema and completeness;
- accepted/quarantined backfill counts;
- unique member joins after historical sale-to-person resolution; and
- explicit unavailable attrition where an exact opening cohort is absent.

Observed shadow results after deployment:

| Period | Joined | Final endings | Downgrade-only | Net unique growth | Attrition |
|---|---:|---:|---:|---:|---|
| Completed week | 2 | 1 | 1 | 1 | Unavailable — exact opening cohort absent |
| Rolling 28 days | 10 | 1 | 1 | 9 | Unavailable — exact opening cohort absent |
| Rolling 90 days | 33 | 1 | 1 | 32 | Unavailable — exact opening cohort absent |

The focused 2 August repair traced all 13 incomplete relationships through the
existing Revenue active-roster publisher. A numeric weekly allocation was not
invented for PIF/PIA services. Instead, a relationship can be allocation-complete
when the roster says prepaid and a matching current confirmed commercial
entitlement exists.

PT/Revenue deployment `0bf20893-37ee-4614-9afc-0f96912df42f` published fresh
candidate `20260802T025959Z-4c4bd442`, which promoted governed cohort
`20260802T025959Z-191ca94e`. Aggregate verification found:

- 145 active governed service relationships;
- 142 complete: 44 PT and 98 SGPT;
- 11 prepaid relationships supported by confirmed entitlement evidence with
  `weekly_allocation=null`;
- three PT relationships still missing contracted weekly frequency; and
- two of those three also missing confirmed allocation evidence.

The three genuine gaps stay explicitly incomplete and Revenue Control remains
legacy-authoritative for them. The repair introduced no extractor and used no
Trainerize delivery evidence.

No client-facing message or source-system write was made.

## Rollback

The change is additive and shadow-only. Rollback is a Railway redeploy of the
prior healthy Hub image. Existing immutable lifecycle rows can remain because
they have no publication authority; consumers should ignore unsupported
contract versions. No workbook rollback is required because neither the
accepted dashboard nor KPI workbook changed.
