# PT Worksheet Evidence Corrections

**Date:** 29 July 2026  
**Runtime:** Railway reporting control plane  
**Workbook:** Brown & Casserly Pty Ltd 2026  
**Mode:** Owner-approved evidence-backed worksheet correction

## Result

The 29 proposed Sales worksheet completions were reviewed against the evidence
class stored by Railway.

Seventeen authoritative corrections were applied and verified:

- `Added to Trainerize` was changed to true for Anika Aquino, Beth Watson, Liz
  Winter, Janie Ting, Bec Barwick, Janet Angus, Dhruvi Karelia, Sudheshna
  Joginipally, Shaantaa Boyes, Kat Norman, Kanika Mehta, Gail Kelly, Emma
  Spowart, Grace Arnell and Vaishnavi Vakacharla.
- `Debits Set Up` was changed to true for Anika Aquino and Jody Burke.

The Trainerize changes are supported by accepted active Trainerize identities.
The debit changes are supported by accepted collecting payment accounts.
Google Sheets revision history remains the recovery path.

The post-write Railway refresh reports:

- 10 fully confirmed current PT records, up from 7;
- 12 proposed changes remaining, down from 29;
- 0 changes eligible for automatic owner-approved application;
- 12 trainer assignments requiring manual or trainer-authoritative evidence;
- 0 PT roster exceptions;
- Railway worksheet writes remain disabled.

## Remaining Trainer Assignments

| Client | Proposed trainer from Active PT | Sales row |
|---|---|---:|
| Janet Angus | Piper Mae | 92 |
| Grace Arnell | Nora Silva | 126 |
| Emma Spowart | Katrina Parsons / Piper Mae | 120 |
| Gail Kelly | Nora Silva | 117 |
| Sudheshna Joginipally | Piper Mae | 99 |
| Kanika Mehta | Nora Silva | 116 |
| Dhruvi Karelia | Nora Silva | 97 |
| Kat Norman | Piper Mae | 113 |
| Sezen Yasar | Piper Mae | 19 |
| Shaantaa Boyes | Nora Silva / Piper Mae | 103 |
| Vaishnavi Vakacharla | Piper | 132 |
| Beth Watson | Nora Silva | 73 |

These values are copied from the Active PT worksheet, which is supporting
operational evidence rather than the governed trainer-assignment authority.
They were not written to Sales.

The control plane must accept a structured GHL trainer assignment or explicit
owner confirmation before applying them. Dual-trainer values require a single
governed reporting rule before they can be projected into one Sales field.

## GHL Trainer Authority Build

Railway deployments `08c38fab-582f-4b6f-a446-eb7b0ccf7cec` for the operating
data hub and `fe539a17-1cd1-45e7-a0cc-30c3d46d1b45` for PT Booking Shadow made
the GHL trainer-authority path live.

Membership snapshot schema version 3 now carries the GHL `PT Block Trainer`
field. A populated value becomes authoritative for a Sales trainer proposal and
takes precedence over a cover coach or worksheet-only value. A blank field
continues to fail closed.

The fresh full-source reconciliation completed as membership run
`20260729T002321Z`. All 12 remaining contacts have a blank GHL block-trainer
field, so none was automatically promoted.

## Calendar Evidence Review

The current GHL PT calendars support ten strong current assignments:

| Client | Current calendar evidence | Proposed governed trainer |
|---|---|---|
| Janet Angus | 13 Piper bookings, 1 Nora booking | Piper |
| Grace Arnell | Current and future weekly pattern moves to Nora | Nora |
| Gail Kelly | 11 Nora bookings only | Nora |
| Sudheshna Joginipally | 13 Piper bookings, 3 Nora bookings | Piper |
| Kanika Mehta | 20 Nora bookings only | Nora |
| Dhruvi Karelia | 25 Nora bookings, 1 Piper booking | Nora |
| Kat Norman | 9 Piper bookings, 1 Leisa booking | Piper |
| Sezen Yasar | 14 Piper bookings, 1 Nora booking | Piper |
| Vaishnavi Vakacharla | Current and future bookings are all Nora | Nora |
| Beth Watson | Current and future weekly pattern is Nora | Nora |

Vaishnavi's calendar evidence conflicts with the current Active PT value of
Piper. That record requires a coordinated GHL, Active PT and Sales correction,
not a Sales-only projection.

Two assignments remain genuinely shared or ambiguous:

- Emma Spowart: Katrina and Piper both have material booking evidence, with
  additional Nora cover.
- Shaantaa Boyes: Nora and Piper both have recurring future bookings.

## Approved Trainer Corrections

Peter approved the ten consistent assignments on 29 July 2026. The following
surfaces were updated and read back successfully:

- the official GHL `PT Block Trainer` field for all ten contacts;
- the matching Sales `Trainer Assigned` cell for all ten contacts;
- Vaishnavi Vakacharla's Active PT trainer, corrected from Piper to Nora Silva.

The Railway reconciliation completed as run
`a8214744-e86a-4f1d-bcb7-2fec0695f580`, using membership source run
`20260729T004514Z`. Fully confirmed current PT records increased from 10 to 18,
pending-term cases fell from 10 to 2, and proposed trainer patches fell from 12
to 2. The two remaining manual cases are Emma Spowart and Shaantaa Boyes.

The hub accepted snapshot `20260729T004723Z-f60bcf98`. The live CEO dashboard
and CEO report both show 18 confirmed current PT records, 2 pending terms, 2
manual proposals and 0 exceptions.

## Shared-Trainer Rule

Peter confirmed that a genuine shared assignment can be written in one cell
using both full trainer names separated by ` / `. Emma Spowart is recorded as
`Katrina Parsons / Piper Mae`; Shaantaa Boyes is recorded as
`Nora Silva / Piper Mae`.

Both GHL and Sales values were saved and read back successfully. Railway run
`a5f8dc19-22a9-4074-b477-f870e36eb0f1` used membership source run
`20260729T010730Z` and published hub snapshot
`20260729T010929Z-ef20c167`. Trainer proposals are now zero and manual trainer
decisions are zero.

That trainer decision did not itself change the commercial result. The later
prepaid-pack and purchased-service corrections below resolved Shaantaa and
Vaishnavi. Emma remains the only payment/provisioning review, and none of those
commercial states reopens trainer attribution.

## Shaantaa Pack Continuation Correction

Peter confirmed that Shaantaa's $1,800 20-pack of 45-minute sessions was her
initial purchase. Her current entitlement is a separate $2,400 20-pack of
60-minute sessions purchased on 11 July 2026.

The original Sales row remains historical evidence and was not overwritten.
The current Active PT row remains the operational expression of the 60-minute
pack. PT roster schema version 6 now consumes the existing Stripe pack evidence
and does not require recurring weekly-debit fields for a verified prepaid pack.

PT Booking Shadow deployment `366b6b9b-deee-439e-8376-7040240a8ca5` is live.
All 97 affected tests passed. Production hub snapshot
`20260729T013506Z-e233b7b9` classifies Shaantaa as confirmed current PT, reduces
pending terms from 2 to 1, reduces pending provisioning from 8 to 6, and
increases confirmed current PT records from 18 to 21. Trainer proposals and
exceptions remain zero.

## Remaining Queue Resolution

The remaining commercial queue was reconciled on 29 July 2026:

- Grace Arnell's existing four-session Fast Track purchased-service term is
  now treated as paid-in-advance PT evidence rather than a missing weekly
  debit;
- Liz Winter, Erin Wilkinson and Nim Cabraal are classified as approved holds,
  not failed provisioning;
- Kristy Hopper's exact $1,200 Stripe PaymentIntent
  `pi_3SmPMSLMsHYOAUEz0R8KJwSo`, paid 6 January 2026, is mapped to her GHL
  contact and confirms her 20-session PT pack;
- Vaishnavi Vakacharla has governed Fast Track SGPT and four-session PT terms
  from 28 July to 24 August, and Active PT cell `J48` now carries the standard
  `$50.00` PT allocation formula.

PT roster schema version 7 separates confirmed current service, paid-in-advance
service and approved holds. The hub also prefers the newest accepted source
snapshot when business observation timestamps tie.

Deployments `485bb795-cdf9-4786-89bb-ec835187e8c9` and
`b8b897f3-44a9-49da-9a5c-cf0082831313` made the corrected PT and hub paths
live. All 145 affected tests passed. PT refresh
`fd8c909f-5868-4e3e-a76a-a9e2ba48e4ff` and hub snapshot
`20260729T021040Z-daa26f7a` report 24 confirmed current PT clients, 3 approved
holds, 0 pending terms, 1 pending provisioning case, 0 exceptions and 0
proposed worksheet patches. Emma Spowart is the only remaining provisioning
review.
