# PT Sales and Active Roster Self-Mending

**Status:** In Progress: read-only shadow live with Sales-linkage reconciliation complete  
**Documented:** 28 July 2026  
**Production change:** Read-only classification live; worksheet writes remain disabled  
**Owner review gate:** Peter Brown  
**Runtime:** Railway only

## Problem

Published GHL workflow `PT Agreement Form: Email` (`f8c76dc6-907d-4e69-9f23-6989e2b10447`) successfully creates Sales and Active PT rows, but several worksheet columns have no configured value.

The live Sales action leaves these columns unmapped:

- Product
- Trainer Assigned
- Cash Taken
- Added to Trainerize
- Debits Set Up

The live Active PT action leaves these columns unmapped:

- Session Length
- Sessions per week
- Session Rate
- Weekly Debit

These are deterministic blanks, not intermittent Google Sheets failures. Erica Asler's 27 July 2026 records demonstrated the failure mode: both rows existed, Stripe billing and Trainerize access were active, but the unmapped fields stayed empty.

## Required Outcome

Every current PT client must resolve to one canonical person and no more than one current Sales row and one current Active PT row for the service start.

The system must distinguish four states:

1. `pending_terms`: the agreement exists but required commercial terms are incomplete.
2. `pending_provisioning`: structured terms exist but payment or Trainerize confirmation is still pending.
3. `confirmed_current_pt`: lifecycle, commercial entitlement and access evidence support current PT service.
4. `exception`: evidence conflicts, identity is ambiguous or a required source is unavailable.

Blank fields must never be interpreted as false. A provisional row must be labelled pending, not presented as operationally complete.

## Source Authority

| Field or decision | Authoritative source | Supporting source |
|---|---|---|
| Person identity | Operating-data hub canonical identity | GHL contact ID, email and phone |
| PT lifecycle | GHL | Won PT-only or membership opportunity |
| Cancellation or hold | GHL | Signed form, email or owner decision |
| Product and billing frequency | Stripe subscription or approved PT Minder schedule | Structured agreement terms |
| Cash received | Stripe paid invoice or specific PT Minder debit event | Sales record |
| Trainer assignment | Approved GHL structured trainer field | PT calendar booking |
| Trainerize provisioned | Successful Trainerize account/product evidence | GHL provisioning task |
| Active PT roster membership | Governed lifecycle plus entitlement | Trainerize access and bookings |

Trainerize is access evidence and must not prove payment. Stripe payment must not promote a cancelled GHL lifecycle.

## Target Architecture

### 1. Agreement intake

The GHL agreement path must capture structured values for:

- PT product
- session duration
- sessions per week
- session rate
- calculated weekly debit
- assigned trainer
- agreement date

If any required term is absent, the workflow must stop before creating an apparently complete operational row and publish a `pt_roster_incomplete_terms` exception for Admin review.

### 2. Canonical pending service

Railway ingests the agreement as a pending PT service linked to the canonical person. The idempotency key is:

`canonical_person_id + service_type + agreement_date`

Repeated workflow executions update the same pending service. They must not append another current roster row or repeat full onboarding.

### 3. Commercial confirmation

Stripe subscription creation and the first paid invoice, or a governed PT Minder schedule and debit event, enrich the pending service with:

- product
- session duration when encoded by the product
- billing frequency
- session or weekly price
- payment account ID
- immutable payment event ID

If agreement terms and payment terms disagree, the service becomes `exception`; neither source silently overwrites the other.

### 4. Provisioning confirmation

Trainerize success independently sets `trainerize_provisioned=true`. The Sales worksheet flag changes only after the canonical Trainerize identity and active access are verified.

`debits_set_up=true` changes only after Stripe or PT Minder proves the payment arrangement. It must not be set merely because the agreement workflow ran.

### 5. Idempotent worksheet projection

The Railway projector finds the existing row using canonical identity plus service-start evidence. It updates allowlisted columns on that row.

If one exact row is found, update it. If no row is found, create a pending exception rather than automatically append until owner-reviewed creation rules are approved. If multiple candidate rows are found, quarantine the case as `duplicate_roster_rows`.

The projector may update only:

- Sales: Product, Trainer Assigned, Cash Taken, Added to Trainerize, Debits Set Up
- Active PT: Personal Trainer, Session Length, Sessions per week, Session Rate, Weekly Debit

Identity, historical payments, cancellations and unrelated worksheet columns remain protected.

### 6. Daily self-mending reconciliation

The Railway schedule runs after the shared GHL, Stripe and Trainerize snapshots are accepted.

For each incomplete PT row it:

1. resolves the canonical person;
2. checks GHL cancellation, hold and PT lifecycle state;
3. reads accepted commercial evidence;
4. verifies Trainerize access;
5. compares the governed projection with the current worksheet row;
6. proposes an exact patch or an evidence-based exception;
7. applies only allowlisted, unambiguous corrections when writes are enabled;
8. persists before and after values, evidence IDs and the idempotency key.

The first implementation remains read-only and reports proposed patches.

## Exception Reasons

- `identity_ambiguous`
- `missing_agreement_terms`
- `missing_payment_evidence`
- `payment_terms_conflict`
- `cancelled_or_final_access_ended`
- `approved_hold`
- `trainer_assignment_unknown`
- `trainerize_not_provisioned`
- `duplicate_roster_rows`
- `source_snapshot_stale`
- `write_precondition_changed`

Approved holds remain on the roster and retain their client details. A hold changes service availability and billing timing; it does not delete the Active PT row.

## Safe Rollout

### Phase 1: read-only shadow

- Detect incomplete and duplicate rows.
- Produce exact proposed patches with source evidence.
- Confirm Erica Asler as the first acceptance fixture.
- Confirm zero false cancellation or hold removals.

### Phase 2: owner-reviewed writes

- Enable only the listed worksheet columns.
- Require a fresh accepted source snapshot and unchanged-row precondition.
- Store recoverable before and after values.
- Review every applied patch with Peter.

### Phase 3: controlled production

- Require two consecutive exact shadow parity cycles.
- Require zero duplicate row creation.
- Require zero incorrect cancellation, hold or PT-only classifications.
- Keep all schedules on Railway.
- Preserve the existing GHL workflow until the replacement projector meets the gates.

Only after these gates may the blank GHL sheet mappings be removed or replaced. The current production workflow must not be edited in advance of parity.

## Acceptance Tests

1. Erica Asler resolves to one person, one PT service and one completed pair of worksheet rows.
2. A repeated agreement event does not append a duplicate row.
3. A paid Stripe invoice cannot reactivate a GHL-cancelled client.
4. Trainerize access alone cannot set cash received or debits established.
5. An approved hold retains the roster row and client details.
6. A pending debit remains pending rather than failed or cancelled.
7. A PIA or prepaid-pack client can be confirmed without a recent recurring Stripe invoice.
8. Conflicting product or rate evidence creates an exception and no write.
9. A stale source snapshot blocks the patch.
10. A worksheet row changed after proposal fails the write precondition.
11. Every write is replay-safe and retains before and after evidence.
12. Existing reports continue to function throughout shadow validation.

## Implementation Sequence

1. Add the pending PT service and exception contract to the operating-data hub.
2. Add read-only row completeness detection to the reporting control plane.
3. Reuse accepted GHL, Stripe and Trainerize snapshots rather than extracting again.
4. Add proposed-patch reporting and the acceptance fixtures above.
5. Run two owner-reviewed shadow cycles.
6. Add the allowlisted, preconditioned worksheet writer behind a disabled Railway feature flag.
7. Obtain explicit owner approval before enabling writes.
8. Retire or simplify the incomplete GHL sheet actions only after production parity.

## Phase 1 Build Result

The Railway-only read-only detector was built on 29 July 2026. It reads the
current Sales and Active PT tabs, joins them to accepted hub membership,
commercial and Trainerize evidence, and produces exact cell-level proposals
with a full-row SHA-256 precondition.

The initial live baseline reviewed 48 Active PT rows representing 47 identities:

- 7 current PT records were fully confirmed across the two workbook tabs and
  accepted system evidence;
- 12 require worksheet terms or projections;
- 8 require payment or provisioning evidence;
- 20 are quarantined exceptions, including 19 historical/current Active PT
  rows without an exact same-start-date Sales row and one duplicated Active PT
  identity;
- 27 exact cell proposals were generated: 11 Sales trainer assignments, 14
  Trainerize flags and 2 debit-setup flags;
- zero row creations, row deletions or live writes were proposed.

Erica Asler's current Sales row 131 and Active PT row 47 are now complete and
resolve to one canonical identity, one current PT service and accepted Stripe
and Trainerize evidence. She produces zero patches and is the clean acceptance
fixture.

The first implementation deliberately does not back-create the 19 missing
Sales rows. Those remain exceptions until owner-reviewed creation rules
distinguish legitimate historical clients from missing onboarding records.

## Phase 1 Exception Classification

The first owner-review pass on 29 July 2026 split the 20 exceptions without
changing any source row:

- 17 Active PT identities have no Sales history in the current Sales tab;
- 2 Active PT identities have Sales history, but not for the same service-start
  date;
- 1 identity has two Active PT rows for the same service-start date and remains
  a genuine duplicate-row exception.

Schema version 2 now records `sales_linkage` on every protected identified case
and publishes four non-identifying aggregate measures: exact Sales links,
historical-only Sales links, absent Sales history and duplicated Active PT
identities. The CEO dashboard and report receive the same aggregate split.

Railway deployments `c11cebe7-5897-4083-99ff-cf9813a3a8b4` for PT Booking
Shadow and `ac48b3a8-85b7-4729-bc1d-c2d8c71dc7f0` for the operating-data hub
published the split. The fresh production cycle at 7:57 am Brisbane reported
27 exact links, 2 historical-only links, 17 absent histories and 1 duplicated
Active PT identity. The dashboard and CEO report returned the same values.

All 20 remain quarantined. Historical-only evidence is not silently attached
to the current service, and an absent historical Sales row is not automatically
created. This preserves the Sales tab as an event record while the governed
hub remains authoritative for current lifecycle and entitlement.

## Proposal Safety Gate

The first proposal review found 27 cell changes across 16 clients:

- 14 `Added to Trainerize` proposals are backed by an accepted exact Trainerize
  identity;
- 2 `Debits Set Up` proposals are backed by an accepted collecting payment
  account;
- 11 `Trainer Assigned` proposals are copied from the matching Active PT row.

The first 16 are eligible for explicit owner approval. The 11 trainer
assignments require manual authoritative evidence and are not writer-eligible;
an Active PT worksheet value cannot become authoritative merely by being copied
to the Sales worksheet. This is especially important where an Active PT row
lists two trainers.

Every protected proposal now carries `evidence_class` and `approval_status`.
The executive aggregate separately reports proposals eligible for owner
approval and proposals requiring manual evidence. All writes remain disabled.

Railway deployments `26577813-995d-4d46-a740-d0a2fcebb48b` for PT Booking
Shadow and `103eafdc-696e-4507-a6c2-2bc5a6233e35` for the hub published this
gate. The production refresh reported 16 owner-approval-eligible proposals and
11 manual-evidence proposals; the live dashboard returned the same fresh split.

## Duplicate Resolution Candidate

Schema version 3 adds a strict dominance check for duplicate pairs. It requires
the same identity and service-start date, no conflicting populated values and
one row to contain a strict superset of the other's operational fields.

The live check identifies one unambiguous pair for Vaishnavi Vakacharla:

- preserve Active PT row 48; quarantine incomplete repeat row 49;
- preserve Sales row 132; quarantine incomplete repeat row 133.

Both pairs share the 28 July 2026 service date and have no conflicting populated
fields. Active PT row 48 contains the session terms missing from row 49; Sales
row 132 contains the Silver product and $599 cash value missing from row 133.
This is a read-only resolution candidate. No row has been deleted, cleared,
moved or rewritten.

Railway deployments `6c18bde5-e136-47d5-8155-58cfcf78108f` for PT Booking
Shadow and `9c17f106-a4e3-4185-9303-a997b141395e` for the hub made the check
live. The protected case and CEO dashboard both report one duplicated identity
with one strict preserve/quarantine pair.

### Duplicate removed and upstream cause fixed: 29 July 2026

Peter approved removal of the two incomplete repeats. Active PT row 49 and
Sales row 133 were deleted through the Google Sheets API; the complete Active PT
row 48 and Sales row 132 were preserved. Google revision history remains the
recovery path.

The duplicate was created by overlapping GHL workflow responsibilities, not by
Google Sheets or Railway. Vaishnavi Vakacharla entered `Membership Agreement
Form: Email` once at 8:25 am and `PT Agreement Form: Email` once at 8:28 am on
28 July. The Fast Track branch in the membership workflow created the complete
Sales and Active PT records, then the PT agreement workflow appended its own
incomplete Sales and Active PT records.

The published `PT Agreement Form: Email` workflow now branches after appointment
conversion:

- when Membership Type does not include `Fast Track Package`, the existing
  Sales and Active PT writes run, followed by `3.1. New Personal Training Client`;
- otherwise, the two worksheet writes are skipped and the contact still enters
  `3.1. New Personal Training Client`.

This preserves PT-only onboarding and Fast Track onboarding while giving the
membership workflow sole ownership of Fast Track worksheet creation. The live
workflow was saved with Publish enabled.

The post-correction Railway refresh reviewed 47 Active PT rows across 47
identities. It reports zero duplicated Active PT identities, zero strict
preserve/quarantine pairs, 28 exact Sales links, two historical-only links, 17
absent Sales histories and 19 exceptions. The CEO dashboard returned the same
fresh aggregate.

## Sales-Linkage Reconciliation Complete: 29 July 2026

The 19 remaining cases were reconciled against the date the Sales ledger began,
existing Sales history, future service dates and accepted PT Minder payment
events. Schema version 5 prevents these different facts from being presented as
the same error.

The fresh production result is:

- 28 exact Sales links;
- 2 valid PT or Fast Track continuation links to earlier Sales records;
- 15 Active PT services that began before the Sales ledger started on 1 October
  2025;
- 1 future service start: Shelley Wilson's two-session PT service begins on
  3 August 2026;
- 1 PT service paid through PT Minder without a Sales row: Anne Leditschke's
  $120 PT purchase on 30 June 2026;
- 0 unexplained Sales-history gaps;
- 0 duplicate Active PT identities;
- 0 quarantined Sales-linkage exceptions.

Shelley's Active PT effective date was corrected from 6 July to 3 August using
the owner-confirmed service date. Anne's source row was not fabricated: the
system retains the missing Sales row as a visible reporting distinction and
links the service to the authoritative completed PT Minder transaction.

The CEO dashboard now reports these categories separately. No Sales row was
created, no member system was changed and Railway worksheet writes remain
disabled.

## First Evidence-Backed Worksheet Corrections: 29 July 2026

Peter approved review of the 29 proposed worksheet completions. Seventeen
authoritative corrections were applied through the Google Sheets API:

- 15 `Added to Trainerize` checkboxes were set to true from accepted active
  Trainerize identities;
- 2 `Debits Set Up` checkboxes were set to true from accepted collecting
  payment accounts.

All 17 cells were read back as true with their Boolean validation intact. The
post-write Railway refresh increased fully confirmed current PT records from 7
to 10 and reduced proposed patches from 29 to 12.

The remaining 12 proposals are all `Trainer Assigned` values copied from Active
PT. They remain behind the manual-evidence gate because one worksheet cannot
make another worksheet value authoritative. Two also contain dual-trainer
values that cannot be projected into one governed assignment without a rule.

Schema version 5 now preserves Boolean false as `FALSE` in proposal audit
records instead of displaying it as blank. Railway writes remain disabled.
The reviewed case list is stored at
`outputs/reporting-control-plane/pt-worksheet-evidence-corrections-2026-07-29.md`.

## GHL Trainer Authority Live: 29 July 2026

Membership snapshot schema version 3 carries the existing GHL `PT Block
Trainer` field into the governed hub. When populated, it becomes the
authoritative trainer source for Sales projection and takes precedence over
worksheet copies or temporary cover-session evidence.

The fresh full-source reconciliation confirmed that all 12 legacy cases have a
blank GHL block-trainer value. Railway therefore left all 12 quarantined.

A read-only calendar review found ten consistent current assignments and two
genuinely shared arrangements. Peter approved the ten clear assignments on 29
July 2026.

All ten GHL `PT Block Trainer` fields and matching Sales trainer cells were
updated and read back successfully. Vaishnavi Vakacharla's Active PT trainer was
also corrected from Piper to Nora Silva so all three surfaces agree.

Railway run `a8214744-e86a-4f1d-bcb7-2fec0695f580` increased fully confirmed
current PT records from 10 to 18 and reduced the trainer proposal queue from 12
to 2. Emma Spowart and Shaantaa Boyes remain manual because both have genuine
multi-trainer evidence. The live hub, CEO dashboard and CEO report agree on 18
confirmed records, 2 pending terms, 2 manual proposals and 0 exceptions.

## Shared-Trainer Projection Rule

A genuine shared PT assignment is stored in both GHL `PT Block Trainer` and
Sales `Trainer Assigned` as the two full trainer names separated by ` / `. The
value remains one governed field and must not be split into duplicate client or
service rows.

The approved live values are:

- Emma Spowart: `Katrina Parsons / Piper Mae`;
- Shaantaa Boyes: `Nora Silva / Piper Mae`.

Railway run `a5f8dc19-22a9-4074-b477-f870e36eb0f1` reduced the trainer proposal
queue and manual trainer decisions to zero. Remaining pending-term or
provisioning states are commercial controls and do not invalidate the trainer
assignment.

## Prepaid-Pack Continuation Rule

An exact, beneficiary-mapped Stripe prepaid-pack entitlement is authoritative
commercial evidence for the current PT pack. It does not replace or rewrite an
earlier Sales purchase row.

For a verified prepaid pack:

- `Personal Trainer`, `Session Length` and the `PIF` marker remain required in
  Active PT;
- weekly session frequency, weekly debit and recurring debit setup are not
  required merely to confirm the pack;
- the current pack payment comes from the commercial evidence layer, while the
  original Sales row remains historical sales evidence.

This rule resolves Shaantaa Boyes correctly: her original $1,800 45-minute
20-pack is preserved, while her 11 July $2,400 60-minute 20-pack governs the
current entitlement. Schema version 6 also connects
`commercial_evidence_stripe_pack` directly into PT roster reconciliation.

Deployment `366b6b9b-deee-439e-8376-7040240a8ca5` and hub snapshot
`20260729T013506Z-e233b7b9` increased confirmed current PT records from 18 to
21, reduced pending terms from 2 to 1 and reduced pending provisioning from 8
to 6. No source row was added, removed or overwritten.

## Paid-In-Advance and Approved-Hold Rule

Schema version 7 treats an effective governed purchased-service term as
paid-in-advance evidence. It does not require `Debits Set Up` to be true while
the purchased term is effective.

An evidence-backed `APPROVED_PAUSE` is a separate `approved_hold` state. It is
not counted as confirmed collecting service and is not reported as failed
provisioning.

Only `Pending Hold`, `Escalated Hold`, `On Hold` and `Returning` are open hold
states. `Completed` is terminal history and must not suppress PT booking
continuity or create an approved-hold classification.

The original schema-version-7 snapshot resolved Grace Arnell's four-session
Fast Track term, classified Liz Winter and Erin Wilkinson as approved holds,
linked Kristy Hopper's verified $1,200 pack, and completed Vaishnavi
Vakacharla's four-week Fast Track term and $50 weekly PT allocation. Nim
Cabraal's completed May hold was subsequently identified as terminal history,
not a current approved hold.

The live result is 24 confirmed current PT clients, 3 approved holds, 0 pending
terms, 1 pending provisioning review, 0 exceptions and 0 proposed patches.
Emma Spowart is the only remaining provisioning review.

The protected purchased-service register can be read through authenticated
`GET /revenue/evidence/purchased-service-terms` before a full-register
replacement. This prevents an append from accidentally overwriting existing
terms.
