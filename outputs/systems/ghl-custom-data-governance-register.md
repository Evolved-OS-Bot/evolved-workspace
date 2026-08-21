# GHL Custom Data Governance Register

**Verified:** 5 August 2026  
**Scope:** Contact custom fields and location custom values  
**Status:** Live governance register; field/value audit and approved cleanup complete, Lead Source first-touch enforcement live, obsolete reactivation value retired, low-population parent-system review complete, and the canonical postpartum cutover verified

## Inventory result

The initial live API audit returned 223 contact custom fields and 32 custom values. After the approved blank-value, TransformationFLIX, seminar and reactivation cleanup, 18 custom values remain. No two custom fields have the same exact case-insensitive display name.

The main governance problem is semantic fragmentation: several fields represent the same business concept with different wording, answer sets or data types. The only intentionally blank value now retained is `SA: Conversation Summary`.

The broader dependency review on 31 July returned 301 fields in the GHL interface: 277 Contact, 8 Opportunity and 10 Business fields, plus the platform's remaining system count. After the approved deletions, a fresh 1 August supported-API read returned 251 non-standard custom-field definitions across 2,796 contacts. Every remaining field with zero to five stored contact values belongs to a reviewed parent system: milestone/referral, PAR-Q, Membership Change PT, hold, cancellation, service-change, Strength Assessment, corporate, metabolic, agreement/signature or historical-event data. Population is evidence, not a deletion rule: live form fields, signatures, newly created control fields and deliberately retained future infrastructure may legitimately show zero values.

Live UI revalidation on 5 August returned 307 fields across all object types: 283 Contact, 8 Opportunity and 10 Business, plus the remaining platform/system count. Focused searches found one `Lead Source`, one canonical `Lead: Life Stage`, no custom field named Postpartum or Post Partum, four trainer-related fields with distinct purposes, and one retained weekly-debit agreement field alongside the governed Membership Service Change price controls. The apparent overlaps remain semantic and parent-system-specific; no new literal duplicate-field cleanup batch was found.

## Custom-value classification

### Retain as active infrastructure

- Business Name, Business Name (Short) and Business Email
- 30DNNC Link
- Strength & Longevity Assessment
- PAR-Q Form Link
- Google Review Link
- the six `story_*` publishing values
- Peri Menopause and Post Menopause 7 Day Reset resources
- The FitFam Cookbook

These values support retained workflows, resources or the member-story publishing system.

### Retain, but review with the parent system

| Value | Current state | Review rule |
|---|---|---|
| Metabolic Classification Assessment Link | Populated | Retain while the 2011 survey is deliberately preserved; review before any reuse. |
| [WARM] Seminar Replay and Slide Deck | Deleted 22 July 2026 | Both values were deleted after the seminar workflows, form and event workflow were retired. Three historical template consumers had already been removed during the TransformationFLIX cleanup; `TCS - Non Member`, the final remaining consumer, was then deleted and all four names were verified absent. |
| Stay On List (Reactivation) | Deleted 30 July 2026 | Its parent `2 Step Permission/Reactivation` workflow had already been unpublished and archived. A rendered-content scan checked all 271 email templates and returned zero matches for the value or its label. Peter then approved deletion of custom value `VLVX0STjrSyNnKsBhcJH`; the API returned success and an immediate inventory read-back confirmed it was absent. |
| TransformationFLIX Sign Up | Deleted 22 July 2026 | The legacy checkout value and all 16 TransformationFLIX-referencing templates were deleted after approval. A complete rescan returned zero matches. Thirteen unrelated marketing templates and the unrelated Week 8 delivery template were preserved in their mixed-content folders. |

### Blank but intentionally reserved

`SA: Conversation Summary` is blank by design. It is reserved for the planned pre-qualification agent and should not be deleted merely because it has no current value. Before that build, confirm whether the implementation should use a contact custom field rather than a location-wide custom value, because conversation summaries are contact-specific.

### Deleted blank template values

Peter approved deletion of the following ten blank values on 22 July 2026. The API returned success for every deletion, a fresh inventory confirmed that none remains, and `SA: Conversation Summary` was separately verified as retained:

- Booking Thank You Page
- Claim Thank You Page
- DR Offer
- From Email
- Logo Image URL
- Notifications Email For Client
- Offer Name
- Twilio Number
- Twilio Number In link Form
- Your App Login URL

Before deletion, live form checks confirmed that `Corporate Gift Card Claim` used an inline confirmation message rather than `Claim Thank You Page`; `Strength Assessment Calendar Form` also used an inline message rather than `Booking Thank You Page`. The complete email-template scan traversed 28 folders and all 290 rendered template bodies without finding any of the ten merge keys, and the operational workspace search found no consumer.

## Custom-field control queue

| Concept | Live evidence | Classification | Required action |
|---|---|---|---|
| Life stage | Three fields remain: canonical multi-select plus two form-bound radio fields with inconsistent labels and answers. Full-canvas revalidation on 30 July confirmed that all five published 30DNNC delivery workflows write the correct canonical value to `Lead: Life Stage`, including the three Planning Pregnancy, Pregnant and Postpartum branches. A fresh 31 July contact audit found 457 historical values in legacy intake field `gKk8C5noKS1Gs81vKafA` and zero stored values in transient 30DNNC capture field `tGaGYawO3Q4AAPnuznF7`; the latter remains an active form/workflow dependency despite its zero contact population | Normalised at workflow layer; dependency revalidated 31 July 2026 | Keep both capture fields while their forms are live. Treat `Lead: Life Stage` as the reporting and personalisation field, and retire the capture fields only when the forms are rebuilt. Do not classify the zero-population 30DNNC field as unused. The remaining postpartum work is a tag migration, not a field-normalisation build. |
| Lead Source | One structured field with nine options: Paid Social - Meta, Paid Search - Google, Organic, Website Organic, Organic Social, Referral, Walk-In, Event and Other | Resolved 23 July 2026. Two published first-touch guard workflows now cover all eleven 30DNNC forms: Website Organic `22ee9373-c366-4021-bdb4-fa205c34cd4a` and Paid Social - Meta `dc574784-bc9e-47e3-b1d5-6c982f3deadd`. Both require the field to be empty. The unsafe direct source action was removed from all eleven original submission workflows, which remain published. A controlled dummy-contact test populated a blank source through the paid guard and confirmed the organic guard did not overwrite it | Govern as original first-touch source. Retain legacy `Organic` for historical records. Route new website-organic submissions to `Website Organic`; use UTM fields and tags for later campaign/channel detail. Monitor new submissions for source completeness, but do not reintroduce downstream overwrites. |
| Weekly debit amount | Renamed on 23 July 2026 to `Regular weekly debit amount (starts in week 4 for week 5)`; $69 / $99 / $149 options and `contact.weekly_debit_amount_after_30_days` merge key retained | Resolved | Keep the legacy merge key stable unless a future migration updates every dependency atomically. |
| Trainer attribution | Owner-confirmed roster: Megan, Piper, Nora, Katrina and Leisa. Both cancellation fields and the Strength Assessment survey were aligned and live-verified on 23 July 2026. All eight documented Beth/Hannah calendar IDs are already absent. `PT Block Trainer` remains free text | Structured rosters and former-trainer calendar cleanup resolved; workflow coverage remains | Treat the five-person list as canonical and update all structured trainer fields together. Retain the automation-fed PT Block field until its calendar-trigger workflow is repaired. |
| PT Block Trainer | TEXT field written by published workflow `PT: Block Tracking & 13-Week Rebooking` from `{{appointment.user.name}}` | Resolved for current operations on 23 July 2026 | Treat it as the delivering coach on the first qualifying booking of the current 13-week block. The 91-day tag lock prevents routine bookings from overwriting it; retain TEXT while the value remains calendar-derived. |
| Metabolic Classification | Score plus questionnaire fields remain attached to the deliberately preserved survey | Dormant retained dataset | Keep while the survey is retained; review the 2011 assessment before reuse rather than deleting fields piecemeal. |
| Cancellation metabolic interest | The complete `MC: Results/Value` workflow has no metabolic or Blueprint action, but the live Membership Cancellation Form contains `Step 4F - Metabolic`, both nutrition packages, live payment links and the one-option continuation field | Owner-retained branch, 31 July 2026 | Keep the slide, its routing and `CS: Metabolic Interest - Continue Cancel` intact for now. Do not delete the field while the branch remains. Reconcile the retained offer, payment links, evidence language and TransformationFLIX reference before actively promoting the packages. |
| Strength Assessment results | Newly expanded structured fields persisted successfully in a controlled submission | Active and verified | Retain. Calculated enforcement and Trainerize integration remain parked upgrades. |
| Strength Assessment consultant attribution | The trainer assigned to the GHL calendar appointment is authoritative | Resolved 30 July 2026 | Do not ask the consultant to repeat their name on the feedback form. Route follow-up and performance attribution from the immutable appointment assignment; Admin records exceptional cover corrections manually. The unused proposed field was deleted. |

## Orphaned-field dependency review

### Completed batch 1: retired acquisition sales-call fields

| Field | ID | Stored contact values | Dependency finding | Recommendation |
|---|---|---:|---|---|
| We promise to be respectful of your time…showing up for your scale session… | `qnGuWaqGp0ZyfspcPnhZ` | 0 of 2,792 | Created 15 April 2024 for the retired Impact Call booking path. Its source forms, tag, funnels and email templates had already been deleted. Workspace matches were inventory or historical audit references only. | Deleted 31 July 2026; API read-back verified absent. |
| Please check this box to confirm that you currently offer, or are looking to offer a coaching/consulting service | `lV2CW17bQMK1AdbwtUmB` | 0 of 2,792 | Same retired Impact Call qualification path; no current business acquisition use. | Deleted 31 July 2026; API read-back verified absent. |
| Do you have (or are about to start) an offer that helps businesses or entrepreneurs make more revenue or income? | `KBTxAVIXSgFlmEWzBhuB` | 0 of 2,792 | Same retired Impact Call qualification path; unrelated to The Evolved's current Strength Assessment acquisition model. | Deleted 31 July 2026; API read-back verified absent. |

GHL's field-delete dialogue only warned that deletion was irreversible; it did not expose a consumer list. Peter approved the batch after three independent checks: zero population across the complete contact snapshot, confirmed retirement of the parent sales-call assets, and no forward-facing workspace consumer. All three delete calls returned success and the immediate inventory read-back found none of the three IDs.

### Zero-population fields excluded from automatic deletion

- Twenty-two Membership Service Change control fields are new governed infrastructure.
- Hold, Billing OS, cancellation, PAR-Q and signature fields remain tied to live operational forms or workflows.
- Strength Assessment result fields include deliberately optional measures.
- Strength For Industry survey fields remain because the corporate pathway is owner-retained. The one obsolete TransformationFLIX offer field is separated into proposed batch 9 below.
- Metabolic Classification fields remain attached to the deliberately preserved assessment.
- The cancellation metabolic-continuation field remains because Peter chose to keep the metabolic packages in the live cancellation form.

### Retained new build: milestone and referral fields

The initial 31 July classification was corrected after Peter confirmed this is a newly structured referral form and the complete public form was inspected from top to bottom. Zero stored values are expected before genuine submissions and do not make these fields unused or duplicated.

The public `Milestone T-Shirt Order Form` contains:

- identity fields;
- milestone, shirt/singlet and size;
- experience star rating and optional feedback;
- Google-review status; and
- `Do you have someone in mind?`, which governs the referral branch.

The fifteen `Referral 1–5 Name`, `Email` and `Mobile` fields are intentional conditional fields. They are hidden from the initial form screen and should remain unless an end-to-end test proves the conditional branch is not using them. `Milestone T-Shirt Last Ordered` and `Member Referral Count` are intended workflow-output fields rather than direct member inputs.

The controlled 31 July test proved the full conditional cascade: selecting `Yes` revealed Friend 1, and completing each friend name revealed the next set through Friend 5. The successful submission persisted all 22 entered milestone, rating, feedback, review and referral values to the submitting contact. No separate referral contact, tag, task, note, appointment, opportunity or conversation was created. `Milestone T-Shirt Last Ordered` and `Member Referral Count` remained blank, confirming that the missing processing workflow is the operational gap rather than the field schema.

All referral test values used reserved or non-deliverable test details. The controlled contact was deleted after verification; a fresh complete contact snapshot confirmed it absent.

### Completed batch 2: four health/event-era orphan fields

| Field | ID | Stored values | Dependency result | Recommendation |
|---|---|---:|---|---|
| Affirmation | `EfNehEGuj9XTAKoVnff5` | 0 of 2,793 | Not present on the current PAR-Q or legacy Pre-Exercise Form; workspace matches were inventory only. | Deleted 31 July 2026; API read-back verified absent. |
| Emergency Contact for Participant | `DRXF5xz4YLAUBefHVYUh` | 0 of 2,793 | Neither health form used it. The current PAR-Q uses structured field `Emergency Contact` (`wLxj7gtob8AQdgJYSE0X`), populated on 52 contacts. | Deleted 31 July 2026; API read-back verified absent. |
| Single Line 8q2w | `bWYSXObi5Ds0NCRJLKtI` | 0 of 2,793 | Generic builder remnant; no live form, workflow or operational workspace consumer found. | Deleted 31 July 2026; API read-back verified absent. |
| Would you like extra training? We are offering 7 days of free small group personal training… | `3cyRKn2OjCJY6zrKHCZd` | 0 of 2,793 | Not present on either health form. Its seven-day free-access wording belonged to a retired trial-era offer and the only operational workspace matches were stale field inventories. | Deleted 31 July 2026; API read-back verified absent. |

Peter approved the batch. All four API deletions returned success and the immediate custom-field inventory read-back found none of the IDs.

Peter approved retirement of the legacy `Pre-Exercise Form` on 31 July 2026. The form (`tUmSYWgC90QLMHycVotC`) was deleted in the GHL interface after the supported delete API rejected the operation; the Forms library reduced from eight to seven visible root items.

A fresh supported API read confirmed the old form ID is absent. All eight older screening field definitions remain present and each still retains its historical values on three contacts. The current production `PAR-Q` (`yziUG4EO90xQMtBx5xU1`) remains intact and uses the newer structured field family, including Emergency Contact on 52 contacts and Confirmation on 57 contacts.

### Reviewed batch 3: River-to-Rooftop historical dataset

The next low-population review showed that the same three contacts also hold two non-screening fields from the retired 2024 River-to-Rooftop intake:

| Field | ID | Stored values | Dependency result | Decision |
|---|---|---:|---|---|
| What are your primary fitness goals? | `HbIxBf5wqpYIQuETaemm` | 3 of 2,795 | All three contacts have source `r2r Training - Jacob's Ladder` and tag `#fitnessevent`. No current form or survey carries a River-to-Rooftop path. | Retain as historical data; do not treat it as the canonical current lead-goal field. |
| Please confirm you are registered with the River to Rooftop event by providing us with your donation page link | `kO7EdCYvJxMGHQHEajR1` | 3 of 2,795 | Same three event contacts. The only matching named workflow, `Fitness Event Registration`, is already draft/archived. | Retain as historical data unless Peter later approves event-data destruction. |

This corrects the retained legacy dataset from eight to ten fields: eight screening/confirmation fields plus the event goal and registration fields. Low population does not justify erasing the only structured record of those three historical event intakes.

### Completed batch 4: standalone consent orphan

| Field | ID | Stored values | Dependency result | Recommendation |
|---|---|---:|---|---|
| SMS/Txt Opt In | `qGZnum0zTEiFsFvzV5AV` | 0 of 2,795 | Absent from all 20 current forms and 14 current surveys. A complete scan found no match in 271 rendered email templates, SMS templates or supported workflow metadata. The current 30DNNC form uses `Email Opt In` (`elb56bw7b0ffyU55uo67`) with combined requested email/text consent instead. | Deleted 31 July 2026; API read-back verified absent. |

Neighbouring zero-population fields were excluded after live dependency verification. `How would you rate your experience at The Evolved?` is active on the Milestone T-Shirt Order Form; `Signature` is active on both current agreement forms; `PARQ: Signature` is active on the current PAR-Q; and `FR: Signature - Confirmation` is active on the Financial Relief Form.

Peter approved the deletion. The API returned success and an immediate custom-field inventory read-back confirmed the field ID is absent.

### Reviewed batch 5: membership-change and PT-package fields

| Field family | Live evidence | Decision |
|---|---|---|
| `MCHO: Signature` and `MCHO: Initial Online Only Terms` | The signature is active on both dedicated Membership Service Change surveys; the Online Only terms initial is active on the Online Only survey. | Retain as current form dependencies. |
| `MCPT: PT Choice` and `MCPT: Signature` | Both are active on the current `Membership Change: PT Agreement Form`. | Retain as current form dependencies. |
| `MCHO: Plan Choice` | No longer present on a current form because Evolved Anywhere and Online Only now use dedicated surveys. It retains four values: genuine service-choice history for Sue Goodwin, Tania Stiles and Peter Brown, plus one controlled acceptance-test contact. | Retain as a historical migration bridge until Membership Service Change acceptance and current-service projection are complete. Do not write new records to it. |

Low population is expected for the current service-change and PT-package forms. The old combined plan field should be reconsidered only after genuine records have been reconciled into the governed current-service fields and the acceptance-test contact has been handled separately.

### Reviewed batch 6: Strength Assessment staged context fields

No deletion is recommended in this tranche.

| Field family | Population | Dependency result | Decision |
|---|---:|---|---|
| `Pre-qual Summary` | 0 | Reserved for the scoped SA Pre-qual AI Agent, which will generate the trainer brief and populate this governed field. The reporting hub is already prepared to read it. | Retain as staged infrastructure. Zero population is expected until the agent is live. |
| `SA: Website Goal`, `SA: Website Decade`, `SA: Website Experience` | 0 each | Reserved by the scoped SA Pre-qual AI Agent as low-friction website context. No live website or GHL writer has been implemented yet. | Retain as staged infrastructure; do not treat them as authoritative until the writer and normalisation rules are built. |
| `SA: Side Plank Left Seconds Held`, `SA: Side Plank Right Seconds Held` | 1 each | Present on the live Coach Consultation Feedback form and conditionally revealed for Long or Perform. | Retain; optional low use is expected. |
| `SA: Toes to Bar Reps` | 0 | Present on the live Coach Consultation Feedback form and conditionally revealed for Perform. | Retain; optional low use is expected. |

The newer structured assessment-result fields already have seven populated contacts, confirming adoption has begun. The older combined result fields remain the historical baseline and should not be removed while reporting spans both schemas.

### Reviewed batch 7: membership and PT hold controls

No deletion is recommended in this tranche.

| Field family | Live evidence | Decision |
|---|---|---|
| Canonical `HS:` intake fields | Hold reason and start date are present on all four current hold surveys. Standard weeks, extended weeks, notes and extension fields appear on the relevant standard or extended variants. | Retain as live form and operational dependencies. |
| Protected `HS Request:` fields | Deliberately absent from member-facing surveys. Billing OS writes these after validating the first request, then uses them to restore the accepted hold if a later submission overwrites canonical fields. | Retain as active concurrency-control infrastructure. |
| Canonical and protected signature fields | `HS: Signature - Hold Request Confirmation` is used by all four surveys. `HS Request: Signature - Hold Request Confirmation` is the protected snapshot counterpart. | Retain both; they are not accidental duplicates. |
| Billing OS hold status | One populated contact and a verified live exception path. | Retain as active billing control and Admin Eve fallback evidence. |
| Extended protected fields | Zero current population. No accepted extended request has populated the protected snapshot since this layer went live. | Retain; zero population is expected and not deletion evidence. |

The 29 July controlled test already proved that a second submitted period cannot overwrite the accepted first hold. The test contact was deleted afterward, explaining why some protected-field populations returned to zero.

### Completed batch 8: superseded cancellation rescue fields

| Field | ID | Stored values | Dependency result | Recommendation |
|---|---|---:|---|---|
| CS: Results/Value - Reset | `26MDfYt5HHuo1zy0Uj31` | 0 of 2,795 | Absent from the current Membership Cancellation Form. The live survey now uses the `CS: - PT Interest` field in `Step 4A - PT Reset`. Full-canvas inspection of the published `MC: Results/Value` workflow found routing by reason, contact-made tags and cancellation opportunity state, not this field. | Deleted 31 July 2026; fresh API read-back verified it absent. |
| CS: Style - Offer | `9YERw2bZYc9uTEknzsZi` | 0 of 2,795 | Absent from the current Membership Cancellation Form. The live style path uses `CS: Style/Gym - PT Interest`. Full-canvas inspection of the published `MC: New Style` workflow found no routing dependency on this field. | Deleted 31 July 2026; fresh API read-back verified it absent. |

`CS: More Info` was excluded from deletion. It is no longer present on a current survey but retains a meaningful historical cancellation note for Eliza Lebsanft; preserve it unless that note is first migrated into another governed record.

All other low-population cancellation fields remain current conditional survey inputs, workflow-owned cancellation state or Billing OS evidence. Low counts reflect branch frequency and the recency of the rebuilt form, not obsolescence.

### Completed batch 9: dormant corporate field reconciliation

The 31 July 2026 parent-system review covered all fifteen low-population fields in shared field group `7OLlEnKGr65RqbvvEh5n`. The live Strength Assessment Survey uses its five assessment-feedback fields, with one or two populated contacts each. The preserved Strength For Industry Owner and Employee surveys use seven corporate feedback, testimonial-consent and referral-introduction fields; zero population is expected because both surveys remain dormant.

Three corporate fields have zero values across 2,796 contacts and are absent from both preserved Strength For Industry surveys:

| Field | ID | Dependency result | Recommendation |
|---|---|---|---|
| A strength report to show your team's baseline & improvements? | `bdr4mCpPoXciN7S8qn4C` | Not on either preserved survey, but still aligned with the owner-retained corporate concept and potential reporting-hub assessment output. | Retain as staged infrastructure until the corporate offer is rebuilt or retired. |
| Would you like a follow up workshop in 6-12 months? | `288nVH0JljFIE3BiVXaF` | Not on either preserved survey, but remains a sensible future corporate follow-up signal. | Retain as staged infrastructure until the corporate offer is rebuilt or retired. |
| Free team access to Megan's TransformationFLIX platform for 14 days? | `ECAEr5FAgH2CryE0eR0U` | Not on either preserved survey. TransformationFLIX templates and its custom value were already retired and deleted. The field was person-specific, offer-obsolete and had no stored history. | Deleted 31 July 2026; fresh API read-back verified it absent. |

No current workflow implements the Strength For Industry survey handoff. `Corporate Gift Card Form Submission` remains a separate archived Draft, while the former `Workshop Sequence` ID is absent from the current supported workflow inventory and its direct builder route returns `Workflow not found`. Preserve the two surveys, but treat them as design assets rather than an operating corporate system.

The shared field group mixes corporate workshop fields with Strength Assessment feedback fields. Split them into clearly named parent groups before corporate relaunch; moving fields for taxonomy must preserve their existing IDs and keys.

### Retained batch 10: staff employment fields

The 31 July 2026 review covered all eight fields in employment group `IrG8dmE2Jp3GLhlxhw3r`.

| Field | Populated contacts | Decision |
|---|---:|---|
| Employee Address | 6 | Retain; historical employment and contract data. |
| Employment Hours | 3 | Retain; valid for part-time arrangements and contract generation. |
| Employment Legal Name | 3 | Retain; required where a staff member's legal and working names differ. |
| Employment Preferred Name | 1 | Retain; the single value correctly links Alyssa Crighton to the working name Piper Mae. |
| Employment Pay Rate | 6 | Retain; current or historical contract evidence. |
| Employment Pay Effective Date | 3 | Retain; the field was added in July 2026 and low population reflects staged adoption. |
| Employment Start Date | 6 | Retain; current or historical contract evidence. |
| Employment Type | 6 | Retain; it controls the published `Send Trainer Contract` workflow. |

None of these fields is a cleanup candidate. Low counts reflect a small staff cohort, newer legal-name and pay-effective-date fields, and historical staff records.

The related Staff Hiring pipeline originally contained five open opportunities in inconsistent stages. Nora Silva, Alyssa Crighton / Piper Mae and Joanne McDonald were at `Active Trainer`; Katrina Parsons and former trainer Meroe Mozakka remained at `Contract Sent`.

Peter confirmed that Meroe no longer works for the business and approved reconciliation on 31 July 2026. The final stage was renamed, without changing its ID, from `Active Trainer` to `Hired / Commenced`. All five genuine hires now occupy that stage and are closed as Won; a fresh API read-back found zero open Staff Hiring opportunities.

Treat the pipeline as a hiring journey rather than the current staff roster. Later employment status belongs in a separate staff lifecycle or secure HR record. Do not delete historical employment values merely because the staff member has left. Employee address and pay data are sensitive and should eventually move to a least-privilege payroll or HR system, with GHL retaining only the minimum fields required for controlled contract automation.

## Decisions that are safe now

- There is no exact duplicate-name custom-field deletion batch.
- The 14 Strength Assessment fields are working and are not cleanup candidates.
- The apparent malformed field labels in the earlier fixed-width export were truncation, not broken live names.
- The ten blank template values were deleted as an approved cleanup batch on 22 July 2026.
- `SA: Conversation Summary` should be separated from that cleanup batch.
- `The FitFam Cookbook` is an active dependency. The published order-submitted workflow uses it in the product-delivery email and must retain it.
- `Website: Register Interest` was permanently deleted and verified absent on 22 July 2026. It had zero submissions, redirected to the retired `/book-call` path and used `example.com` Privacy Policy and Terms links.

## Next dependency checks

1. Canonical trainer roster confirmed 23 July 2026: Megan, Piper, Nora, Katrina and Leisa. Remaining work is field-purpose and workflow/calendar dependency cleanup, not roster definition.
2. Implement life-stage normalisation before deleting any form-bound life-stage field.
3. Postpartum cleanup completed 5 August 2026: San-Rene Tan's genuine intake proved the canonical tag and `Lead: Life Stage = Postpartum` branch. `post partum` was then removed from all three live writers, the workflows were reload-verified as Published, and the legacy tag was deleted and verified absent. `postpartum`, `goal: postpartum` and `notify-story-postpartum` remain.
4. The cancellation metabolic branch and its continuation field are retained by owner decision. Revisit only when the package offer is reviewed or retired.
5. Revisit the correct data type for the future per-contact pre-qualification conversation summary.
6. Build or locate the milestone/referral processing workflow. The form and all five conditional referral levels now pass; remaining requirements are staff fulfilment ownership, approved referral handling, review-system coordination, Last Ordered and Referral Count updates, and corrected legal links. Do not delete any milestone or referral field during this build.
7. The low-population parent-system review is complete as at 1 August 2026. No remaining zero-to-five-population field is an unclassified deletion candidate. Reopen a field only when its parent form, workflow or retained programme is rebuilt or retired.
