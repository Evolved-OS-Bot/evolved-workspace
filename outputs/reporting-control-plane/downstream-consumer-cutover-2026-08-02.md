# Downstream Consumer Hub Cutover Report

**Date:** 2 August 2026  
**Build:** 6 of 7  
**Status:** Implementation complete locally; production cutover remains gated

## Outcome

Retention Intelligence, Conversation Triage, PT Booking Continuity and Revenue
Control now have strict compatibility readers for the protected Hub
`current-person-v1` contract. Each scheduled consumer can compare its existing
identity/classification result with the Hub projection and publish the exact
comparison to the durable Reporting V2 ledger.

The accepted Hub cutover matrix contains four independent metric/version
registrations. A read switch is permitted only when the exact registration has
two distinct scheduled exact cycles, a passing technical acceptance record,
Peter's acceptance reference and an explicit approve decision. A rollback,
current mismatch, blocked contract, stale source, missing status or version
change restores the legacy path.

## Consumer status

| Consumer | Implemented | Current authority | Preserved delivery |
| --- | --- | --- | --- |
| Retention Intelligence | Hub person/lifecycle/service/entitlement overlay, exact Trainerize-ID comparison, durable parity publication, approved-state switch | Legacy until accepted cycles | Private PostgreSQL, existing preview, existing Sheet gate |
| Conversation Triage | Hub GHL-contact lookup for active SGPT/PT flags, exact sampled-contact comparison, durable parity publication, approved-state switch | Legacy until accepted cycles | GHL unread/messages, Claude classification, Discord and email |
| PT Booking Continuity | Hub person/lifecycle/current-PT/commercial overlay, exact GHL-contact comparison, durable parity publication, approved-state switch | Legacy until accepted cycles | GHL calendars, recurrence/coverage, Admin email and KPI gate |
| Revenue Control | Hub person/lifecycle/service/entitlement/payment and schema-v2 governed-roster comparison; approved-state input switch with current-parity fallback | Legacy until a fresh schema-v2 roster cycle and accepted comparisons | Existing cash bridge, exceptions, protected artifacts and Peter email |

Revenue Control can now build its existing audit inputs from Hub `person_id`,
lifecycle, service, entitlement, payment and schema-v2 governed roster
relationships. Its comparison fingerprint includes product, assigned trainer,
contracted weekly frequency, service duration, weekly allocation/currency,
contract length, effective bounds and completeness. A fresh production roster
cycle now carries schema v2 on all 145 active governed relationships. Of those,
132 are complete and 13 fail closed: seven PT and six SGPT relationships lack
weekly allocation, and three of those PT relationships also lack contracted
weekly frequency. Revenue therefore remains legacy-authoritative.

`sgpt-delivery-v1` can provide person-keyed delivered class-session and trainer
evidence. It is not authority for commercial product, contracted frequency,
service duration or PT allocation, so those missing fields must be added to the
canonical service/entitlement relationship rather than inferred from bookings.

## Duplicate logic retirement

No production duplicate extraction has been retired yet. This is intentional:
the required two scheduled comparisons have not run on the new build, and a
fresh schema-v2 roster candidate has not yet been accepted and promoted. The
code now separates Hub authority from retained domain evidence so retirement
can be narrow after acceptance.

## Privacy and safety

- Hub reads require the shared secret and accept only protected GHL and
  Trainerize source identities.
- Names and email remain nullable presentation fields and are never parity or
  identity keys.
- Identified differences remain inside protected service logs and Hub evidence.
- No member message, payment change, membership change or Google Sheet write
  was performed or enabled.
- Existing report destinations and Railway schedules remain unchanged.

## Validation

The combined Operating Data Hub, Reporting Control, Retention Intelligence,
Conversation Triage, PT Booking Continuity and Revenue Control test suite passes
442 tests.

The report registry validates successfully with nine registered reports.

## Remaining production gates

1. Deploy the remaining three consumer builds through their existing Railway
   services without adding another scheduler.
2. Resolve the seven Revenue legacy identities not yet linked to a Hub
   `person_id` and the 130 protected classification differences.
3. Complete weekly allocation for seven PT and six SGPT relationships, plus
   contracted weekly frequency for three of those PT relationships.
4. Observe two distinct scheduled exact comparisons for each consumer.
5. Record technical and owner acceptance, then approve one consumer at a time.
6. Verify its existing report delivery and fail-closed rollback in production.
7. Retire only the duplicate read proven replaced for that consumer.

## Live Revenue shadow evidence

The coordinated Hub deployment
`38c0d667-b23c-4bae-865f-fecc33e1a184` was healthy before Revenue evidence was
collected. Revenue consumer deployment
`e7547ab4-3b5c-48d1-a73d-8eb465a8c720` is also healthy. It corrected two
consumer-only parity defects: duplicate legacy email aliases are collapsed to
one Hub `person_id`, and the legacy comparison population is limited to the
governed Revenue roster rather than every GHL identity retained as audit
evidence.

No-email shadow run `6fa9fae7-dddb-46da-85f8-0cef4b5d3523` completed at
12:26 Brisbane time and published comparison
`8581398ffc1053858cc46bc69e8f7b61`. The protected aggregate evidence is:

- legacy people: 138;
- Hub-linked people: 131;
- legacy-only identities: 7;
- Hub-only identities: 0;
- changed classifications: 130;
- unexplained events: 137;
- unexplained cents: 0;
- fresh Hub evidence: yes;
- complete Hub roster evidence: no.

The cutover controller remains `shadow`, `promotion_authorised=false`, with
zero of two scheduled cycles. The run was manually initiated for deployment
verification, so it is not scheduled acceptance evidence. It requested no
email, performed no source mutation and retained the existing legacy report.

## 4 August Conversation Triage deployment recovery

Deployment `0508d4b1-6878-4b6c-9149-e56fb2897b8e` crashed before application
startup because the service root contained `triage_bot` but excluded the
shared governed `reporting_control` package required by `hub_contract.py`.

Deployment `77d7b5de-f444-4753-a4ca-24f382059830` changes only the packaging
boundary: Railway builds from the repository root with
`triage_bot/Dockerfile`, copies both `triage_bot` and `reporting_control`, and
starts `python -m triage_bot.triage`. The cron remains
`0 8,20 * * *`.

The 19:51 Brisbane recovery cycle started successfully, found six unread
conversations, completed its existing Discord and Admin email delivery and
exited cleanly. The protected current-person read returned a fail-closed
`HubContractError`, so legacy contact flags remained authoritative and no Hub
parity result was published. This proves operational recovery only; it is not
one of the two required scheduled exact comparison cycles and grants no
cutover or workflow-extension authority.

Plan and full inventory:
`plans/2026-08-02-downstream-consumer-hub-cutover.md`.
