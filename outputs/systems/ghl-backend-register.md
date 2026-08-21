# GHL Backend Register

**Audit closed:** 5 August 2026  
**Status:** Live operating register; the GHL backend and Drive process audit is complete

## Audit closure

The final closure pass reconciled the material GHL asset families, live dependencies, task ownership, all seven remaining pipelines and the current Admin, Sales and Delivery process documents in Drive. Approved cleanup and supported record reconciliations were applied with preconditions and live read-back. Material workflows were revalidated across their complete canvases after the initial audit method was corrected.

The register remains the living backend source of truth. The remaining work is a governed build queue, not unfinished audit discovery:

1. Inbound conversation ownership, missed-call handling and response-time controls.
2. The trainer-contract `Full Time`/blank exception before the next trainer hire.
3. The post-Day-7 member lifecycle.
4. The separate membership service-change, Strength Assessment attendance and AI pre-qualification implementations.

## 5 August 2026 — Hold Return current-cycle hardening

The published `HS: Hold Return Journey`
(`f6dc65cb-d5e0-4ff0-90ba-b94d832b86ab`) was inspected across its complete
canvas, trigger, settings, enrolment history, Returning writes and Completed
writes. Re-entry remains enabled for later accepted cycles; Allow multiple
opportunities is now disabled.

Before each call, a contact-field action resets
`HS: Return Guard Status = Not Checked`, so webhook or transport failure cannot
reuse an older Passed result. Two standard webhook actions then call the live Billing OS endpoint
`POST /ghl/hold-return-guard`. `Guard Returning Write - Current Cycle` runs
after the two-day wait and before the Returning opportunity or status mutation.
`Guard Completed Write - Current Cycle` runs after the three-day wait and
before the Completed mutation or opportunity removal. Each is immediately
followed by an If/Else action. Only the corresponding `Passed - Returning` or
`Passed - Completed` branch continues; the None branch ends.

The guard uses the protected accepted request as current-cycle evidence. It
requires an Accepted intake, matching protected and current start dates, valid
start/end chronology, Pre-Return equal to end minus seven days, the expected
On Hold or Returning status, and the exact return or completion day. A mismatch
records the exception, attempts to remove all active executions of this
workflow, and creates one same-day deduplicated Admin Eve task. It does not
message the member or change Stripe.

Three live fields were created and read back:

- `HS: Return Guard Status` — `iU6YEszKisH5GPy1znMG`
- `HS: Return Guard Result` — `cobnePuTqEMDPrF8JAft`
- `HS: Return Guard Checked At` — `f2hmmwxlygunRXIpGcsA`

Billing OS deployment `64aa7d75-66b3-4775-a901-c861762e94ee` completed
successfully and `/health` returned HTTP 200. The Billing OS suite passed 39
tests. Disposable-contact acceptance proved
normal Returning, normal Completed, a newer-cycle mismatch, workflow removal
and one exception task after an exact retry; both test contacts were deleted.
The saved workflow was reloaded and read back as Published with both guards,
both Passed/None branches, opportunity removal and the Completed write present.

## 4 August 2026 — Cancellation contact-evidence hardening

Owner-approved control: stop treating Piper's manual `cs: contact made` tag as the sole evidence of member contact. Member replies during an active cancellation notice should write the compatibility tag automatically; call evidence fails closed unless GHL can prove an outbound connection lasting at least 60 seconds. The Day-14 path must recheck evidence and route unresolved cases to a Megan review task, with no automatic client SMS in her name. `MC: Other (Booked Call)` is excluded.

Live field creation succeeded and was read back:

- `CS: Contact Evidence Source` — `wIhH5FlD4tZlw4vrzuck`
- `CS: Contact Evidence At` — `dMZBb1wwQW9OqZ42df5d`

Published helper `CS: Contact Evidence - Member Reply`
(`06363191-7fbc-4b60-b6d9-000d521cef87`) is live and reload-verified. Its
`Customer Replied` trigger is limited to
`CS: Cancellation Status = Notice Active`; it writes
`CS: Contact Evidence Source = Member Reply` and adds `cs: contact made`.
The native `Call details` trigger has no duration filter, so no automatic call
writer was published.

All eight Piper-led reason workflows were reload-verified as Published after
their automatic `14. SMS to client from owner` action was removed and replaced
with the same-day `14. Megan review - no contact evidence` task assigned to
Megan Brown. `MC: Other (Booked Call)` remains excluded and unchanged.
The four active Notice Period opportunities were audited; Lucinda Gibson and
Sarah Loga had proven inbound replies and were backfilled with the compatibility
tag, source and first qualifying reply timestamp. Elizabeth Winter and Rachael
Kolmajer had no qualifying reply and were left untagged. No member message or
lifecycle state change was made. Full acceptance evidence:
`outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`.

**Account:** The Evolved (`6Ku1uU0Xc45zq0KlTikJ`)
**Verified:** 5 August 2026
**Source:** Live GHL browser audit plus API snapshot at `outputs/ghl-account-documentation-2026-07-20.md`

## Acquisition Rule

The Evolved does not use booked sales calls. The live acquisition conversion event is an in-person Strength & Longevity Assessment. References to calls in cancellation, retention, coaching, or internal operations are outside this sales-only rule.

## Inventory Summary

| Asset type | Count | Current reading |
|---|---:|---|
| Pipelines | 7 | Warm Sales is assessment-based; no sales-call, LT or Seminar pipeline remains. |
| Workflows | 138 | Includes published, draft, and archived workflows returned by the API. |
| Forms | 24 | The two obsolete sales-call forms were deleted on 18 July 2026. |
| Surveys | 13 | Includes the intentionally retained Metabolic Classification survey. |
| Custom fields | 248 custom in the earlier API snapshot; 307 across all object types in the 5 August live UI | The live UI currently separates 283 Contact, 8 Opportunity and 10 Business fields plus its remaining platform/system count. Twenty-two governed Membership Service Change fields were added on 30 July 2026; three Hold Return guard fields were added on 5 August 2026. |
| Custom values | 18 current, down from 32 | Approved blank placeholders, TransformationFLIX, seminar values and `Stay On List (Reactivation)` have been removed and verified absent. |
| Calendars | 36 | No Scale Session, Strategy Session, Goals Discovery Call, or Studio Appointment calendar remains. |
| Tags | 162 | The obsolete sales-call and legacy `post partum` tags were deleted. Canonical `postpartum`, `goal: postpartum` and `notify-story-postpartum` remain; other legacy lifecycle tags require separate dependency evidence before any retirement. |

## Verified Sales Architecture

### Warm Sales pipeline

The `[WARM] Sales` pipeline stages are:

1. Assessment Booked
2. Pre-Qualified
3. No Show
4. Cancelled
5. Show
6. FUM
7. FUNQ

There is no sales-call stage. The current acquisition booking surface is the active 45-minute round-robin Strength & Longevity Assessment calendar `HSVEzfJH4nice96IxHem`. The similarly named 30-minute event calendar `z3cCnLnqwEO7jDrGA0HH` is inactive and is not an alternative assessment entry point.

Any trained owner, admin or coach may continue the conversation and prepare the trainer summary. Injury questioning stops once the information is trainer-actionable and no safety issue remains unresolved; the responder then uses the confidence-building transition and continues to Exercise History.

Admin Eve or another authorised admin manually moves an opportunity from Assessment Booked to Pre-Qualified only after the shared completion map is satisfied. This control remains manual until the pre-qualification bot is built and verified.

### Sales-call retirement

| Asset | Verified status | Disposition |
|---|---|---|
| Legacy sales confirmation workflow | Draft, 414 historical enrolments, 0 active | Moved to `1. Pipeline Workflows / Archive` on 18 July 2026. |
| Legacy no-attendance call rebooking workflow | Draft | Already unpublished and archived on 17 July 2026. |
| Website sales-call form `HimhqKZmS9Dc1pLx2YlI` | Deleted | Removed on 18 July 2026 after confirming zero submissions. |
| Website discovery-call form `dA75jti2i7lLFza6CocY` | Deleted | Removed on 18 July 2026 after confirming zero submissions. |
| Website register-interest form `hJohXvBZv6gn0jD3AdpR` | Retirement candidate | Zero lifetime submissions. Its on-submit action still redirects to `https://www.theevolvedgym.com.au/book-call`, and both legal links point to `example.com`. The related workflow is already unpublished and archived. |
| Obsolete sales-call action tag | Deleted | Removed on 18 July 2026 after confirming it was attached to zero of 2,768 contacts. GHL showed a two-month restoration window. |
| Old sales-call calendars | Not present | Already removed. |
| LT pipeline | Not present | Already removed. |
| `[OLD] Call Booked Emails` template folder | Deleted | Dependency check found no matching email campaign. Both April 2024 booked-call templates and their empty folder were permanently deleted on 22 July 2026; a fresh `Booked` template search returned no results. |

The empty legacy sales-call funnel folder and both undomained three-step client funnels were deleted on 18 July 2026. The later email-template audit found a separate `[OLD] Call Booked Emails` folder and two templates. No matching campaign existed, so both templates and the folder were permanently deleted on 22 July; a fresh `Booked` template search returned no results. The acquisition booked-call cleanup is complete.

The five goal-specific workflows were confirmed to nurture already-booked Strength Assessments, not sales calls. Their folder was renamed to `Booked Strength Assessment Goal Nurture`; all five remain published but disconnected because the current assessment path does not add their canonical trigger tags. Each contains only one email. The planned SA Pre-qual AI Agent supersedes this model, so do not reconnect or expand the workflows: preserve useful content, keep them dormant until the AI path is live and tested, then dependency-check and archive the family with separate approval.

The cancellation workflow `MC: Other (Booked Call)` remains published because it supports a member cancellation-manager pathway, not acquisition.

## Backend Risks and Cleanup Queue

### Priority 0: member lifecycle continuity

The 22 July live audit confirmed that only the first-week member workflow is operational. `Membership: Day 8-28` is an unfinished draft with empty goal branches and no trigger. `Membership: Day 29-90` had no trigger or enrolments in the available 30-day history and only waited 76 days before issuing GHL review requests; it was unpublished on 30 July 2026 and retained as a Draft rebuild shell. `Membership: Day 91-180` and `Membership: Day 181-365` are empty drafts.

The former `Follow Up Monthy`, renamed `FUM: Assessment Education & Reassessment Journey` and set to Draft on 30 July 2026, is not a member check-in workflow. Its retained design shell has no trigger, zero active enrolments, no recent enrolments and only creates or updates a WARM Sales opportunity in FUM. The Milestone T-Shirt form exists but has never been submitted from 1 January 2024 through 22 July 2026, has native notifications and autoresponder disabled, and has no Smart Routing workflow. Its documented satisfaction, red-flag, review, referral and fulfilment actions are specifications rather than live automation.

Do not publish the draft lifecycle shells individually. Design one coherent post-Day-7 retention system with explicit entry and exit rules, contact-frequency control around the Day 14 Google review request, reply ownership, red-flag escalation, milestone capture and measurable retention outcomes.

### Priority 0A: PT administration and staff readiness

The PT booking-field gap was repaired on 23 July 2026. `PT: Block Tracking & 13-Week Rebooking` now covers all 15 current PT calendars, contains no Marnie or Wileen dependency, uses 13-week wording throughout, assigns the task and specific notification to Admin Eve, and holds its tracking lock for the full 91 days. General re-entry and multiple-opportunity execution are disabled. The Trainer Portal certification gap was repaired on 24 July: Course 12 now grants Course 13 Practical Sign-Off, and only completion of the manually graded final practical assignment grants Course 14 Congratulations. Full-canvas revalidation on 30 July confirmed that `Send Trainer Contract` supports five of seven live Employment Type values; both full-time branches and the None fallback remain empty.

The PT booking-continuity shadow pilot was deployed to Railway on 23 July 2026. It performs a read-only Monday reconciliation, stores persistent evidence and emails Admin Eve an exception report; it cannot create, modify or delete GHL records. The first production audit read 107 contacts successfully. The existing Week 10 workflow remains the operational fallback while four reports are reviewed and the accuracy gate is measured.

The permanent owner and review view now lives in `outputs/systems/ghl-workflow-owner-review-register.md`. It separates verified live owners from proposed durable roles, sets risk-based review cadences, accounts for the three GHL Needs Review workflows and maintains the dormant published decision queue.

Treat these as governance repairs, not isolated workflow edits. Define the intended PT block data semantics and approved employment-contract matrix before changing triggers or branches. Megan is the named approval authority for the ten practical blocks in the current certification design.

### Priority 0A: membership service-change control

The Contact folder `6. Membership Service Change` is live with folder ID `6gmIZo2Eg2BQmf8f1xDH`. It contains 22 fields for request identity, prior and selected service components, timing, agreement evidence, six fulfilment surfaces, exception detail and canonical current-service projection.

The field creator at `scripts/create_service_change_control_fields.py` is idempotent and validates exact names, types, options and folder placement. A second production run skipped all 22 existing fields without creating duplicates.

The `MCHO` survey fields capture signed request evidence but must not overwrite `Member: Current Service Components`. Survey `zFxqvzogSZFbeGDnNM8Q` is the dedicated Evolved Anywhere variation and `XBpTy848fvJXjMtGfnu2` is the dedicated Online Only variation. Both use the permanent Legal-page link and are owner-approved.

GHL workflow folder `8. Membership Service Changes` was created on 4 August
2026. All five workflows with the `MSC` prefix are filed there:

| Workflow | ID | Trigger | Action | Live state |
|---|---|---|---|---|
| `MSC | Evolved Anywhere | Controlled Intake` | `f92bde55-73ba-4147-a842-ce53814540ed` | Evolved Anywhere variation submitted | POST the signed contact, request date, current-service field, target key and source survey ID to Billing OS | Draft; zero enrolled |
| `MSC | Online Only | Controlled Intake` | `dcd08689-755b-41af-9e8c-e2eccb2d8198` | Online Only variation submitted | Same controlled handoff with the Online Only target and source survey ID | Draft; zero enrolled |
| `MSC | Strong 12-Month Commitment | COMMIT Interest` | `d03f6ea9-6e16-40fe-9e16-6fdb17569922` | Exact `COMMIT` reply to new-member onboarding | Verify canonical service eligibility and send the signed variation from `admin@theevolvedgym.com.au` | Published; four total, zero active |
| `MSC | Strong 12-Month Commitment | Controlled Intake` | `e571a911-10c6-4be3-872c-dd4bcf8ead84` | Strong commitment variation submitted | POST the signed request to Billing OS for fail-closed processing | Published; one total, zero active |
| `MSC | Strong 12-Month Commitment | Continuation Reminder` | `04ed168e-49a4-4614-8260-568a5673e830` | Continuation Reminder Date | Send the required two-month notice and record reminder status | Published; zero enrolled |

The two earlier service-change intake workflows send no message. They were
live-read back on 4 August as Draft with zero total and zero active enrolments.
Online Only and Evolved Anywhere passed their controlled Trainerize executions,
and both synthetic profiles were deactivated and verified. The stuck first
Evolved Anywhere purchase remains Expired; its same-product, same-profile
replacement is Active and no duplicate product or profile was created. A
disposable contact proved the live Billing OS failure path creates one same-day
Admin Eve task and an exact retry does not duplicate it. Publishing either
workflow before the clean post-boundary six-surface accepted event would allow
Stripe scheduling without proven downstream fulfilment and is prohibited.

The 5 August post-boundary remediation corrected Tania's canonical GHL service
fields to Evolved Anywhere, removed `bronze`, added the Active Online row and
retained the existing Admin Eve task as the one deduplicated exception. The
stale Active SGPT row is now removed and the historical Sales record remains.
GHL conversation evidence confirms Monday only; the trainer, recurring time
and in-person/virtual mode remain unagreed, and a bounded scan of all 30
calendars found no future appointment. Tania also remains split across the
phone/current-service record and the email/marketing record, so identity must
be resolved before acceptance. Trainerize's supported control removed the
`2026 SGPT Program`, and full group read-back proves she is no longer in `The
Evolved All Stars`. Full Access / one-way messaging and the personal program
container remain, but the plan is expired with no current training plan and six
non-expiring group/class credit balances still permit app self-booking. The
same task and `SC: Last Error` now carry that evidence. Both workflows therefore
remain Draft; no accepted event, enrolment or member message was created.

The three Strong commitment workflows passed their separate controlled
acceptance gate and were live-read back as Published after the folder move.
Filing changed only their location; it did not change triggers, actions,
enrolments or publication state.

On 4 August 2026 the first two genuine eligible responders were reconciled and
manually enrolled because their replies pre-dated workflow publication. Both
finished on `Send Strong variation link`; the workflow generated the approved
subject and body from `admin@theevolvedgym.com.au`. The canonical
current-service field reads `Strong, Fit & Flexible` for both contacts, while
all `SC:` signed-variation fields remain absent and billing remains unchanged.

No Membership Pipeline stage or writer was changed. The pipeline remains historical evidence until onboarding, service-change event acceptance, full cross-system reconciliation and deduplicated Admin Eve exception routing pass end to end.

### Priority 0B: inbound communication ownership

`Main Incoming Call Router` currently transfers Admin Hours calls to Nora's hard-coded mobile, then Megan if unanswered; outside Admin Hours it transfers directly to Megan. The final no-answer path ends without a persistent task, callback acknowledgement or accountable owner. No workflow named for missed calls, voicemail or inbox handling exists.

Retain personal routing only while it reflects the actual roster. The durable design should route the role first, record the final call outcome, acknowledge missed callers and create one assigned callback task with a due standard.

The separate Conversations audit found five unread messages: three unassigned, one owned by Nora Silva and one by Piper Mae. SLA settings are off, there is no response-time performance data, and the Manual Actions queue had no pending items. This confirms an assignment and escalation control gap rather than a Manual Actions backlog.

### Priority 0C: lead and reactivation reply governance

The five published life-stage 30DNNC delivery workflows had 396 active contacts at inspection and all had `Stop on response` off. Their source workflows add tags, update attribution and issue internal notifications but do not create a reply task. On 29 July 2026, the owner confirmed that nurture-email replies remain in the normal inbox and do not need a dedicated workflow handoff.

`2 Step Permission/Reactivation` and `War Plan` also left `Stop on response` off. The 27 July deep audit found no enrolments or executions for either workflow in the available 30-day history. `War Plan` was inert because it had no trigger; it was unpublished and moved into `1. Pipeline Workflows / Archive` on 27 July 2026 after its three obsolete challenge emails and hard-coded Lead Connector reply notifications were confirmed.

`2 Step Permission/Reactivation` was dormant but still triggerable by the `cl` tag. Its second timeout sent contacts with one of nine protective tags to a `supress` tag, but sent all other contacts to `Delete Contact`. With zero active enrolments, it was unpublished and moved into `1. Pipeline Workflows / Archive` on 27 July 2026. Any future repermission workflow must replace deletion with a governed suppression and workflow-exit path.

Full-canvas revalidation confirmed that the five delivery sequences contain no internal reply, Strength Assessment booking, membership or Remove-from-Workflow branch. The transition gap was closed on 29 July 2026: Strength Assessment now removes the five life-stage sequences, while `3.0` and `3.1` remove those five plus Mobile Check. The exact target lists were corrected and reload-verified after the revalidation found unrelated workflows in the original multi-selects.

Do not apply a blanket stop-on-response change. The owner has elected to keep nurture-email replies in the normal inbox; Mobile Check retains its separate Admin Eve SMS-reply task.

### Priority 1: paused contacts inside draft or archived workflows

Resolved 20 July 2026. All 65 paused enrolments were removed from the five affected draft workflows:

- `1. New Lead (V4) Part 3 (D43-D105)`: 40
- `NS - Not Interested` (newer draft, 296 historical enrolments): 14
- `1. New Lead (V4) Part 2 (D15-D42)`: 6
- `1. New Lead (V1 - Jan24-Jun24)`: 3
- `1. New Lead (V5) Part 1 (D0-D14)`: 2

The final workflow-list check showed zero active enrolled in all five. No contact records were deleted. GHL retained each historical enrolment and changed its status from `Paused due to draft mode` to `Finished`.

### Priority 2: duplicated and unnamed automation

Revalidated under the full-canvas standard and cleaned up with Peter's approval on 4 August 2026:

- Two draft workflows shared the name `NS - Not Interested`, but they were different obsolete implementations of the same retired WARM-stage handoff. `1c923632-cda4-4614-9795-52e01c38aab0` adds the NI tag, waits five minutes, sends the former Not Interested email, waits 50 days and adds the contact to Lead Nurture; its recent history shows the 14 removed contacts as Finished and zero active. `6b37dbfa-c231-408f-8d42-3e1846049ec1` removes the contact from former New Lead and Attended–Interested workflows, adds a tag and adds Lead Nurture; it has zero active and no enrolments in the available 30-day history. Both target the same legacy `[WARM] Sales Pipeline` stage ID and have no live execution path. Both remain Draft and are now verified inside `1. Pipeline Workflows / Archive`, with their histories retained.
- The library contained three generated-name drafts rather than the previously recorded two. `706aafe0-4975-4722-9f4e-539b865ab953` was a blank 2 May 2025 shell with no trigger, actions or enrolments. `bd0ab801-e155-4e60-a588-9a953b9dbc61` was a zero-enrolment 16 April 2026 record whose builder returned `Error loading workflow`. Both were deleted from the active library at 7:42 pm AEST and verified in GHL's recoverable Deleted queue. `09ff763f-5e4c-4563-93c2-e1bb94697644` was a blank zero-enrolment shell created on 4 August 2026. All available same-day task histories were checked on 5 August; no build, plan or handoff owned it, and its creation coincided with branch-control work inside the existing Strength Assessment workflow rather than a new-workflow build. Peter approved deletion, it was removed from the active library at 10:55 am AEST, and it is verified in GHL's recoverable Deleted queue. GHL will permanently purge all three after its 30-day recovery window.
- Four copied Hold System workflows had remained Draft with zero total and zero active enrolments: Extended Membership `77894268-c509-4e0e-8e15-3b677c53d899`, Extended PT `1d354249-e1cf-4aca-b7e8-9bd5492937e3`, Membership `739e675a-d910-4d5d-a3d4-9befbdb80d8d`, and PT `af713a57-75df-4d2f-99b7-ee2d90b81f83`. All four were created at the same time on 28 February 2026 and are full intake-workflow snapshots with duplicate form triggers, cancellation checks, hold-field writes, notifications and pipeline actions. The published counterparts contain later July safety repairs, so these copies are stale and unsafe to publish. All four remain Draft and are now verified inside `1. Pipeline Workflows / Archive`; they are not approved rollback versions.
- The dormant-published decision queue did not produce a new retirement candidate. The five booked-assessment goal nurtures remain Published with zero active enrolments (historical totals 17, 64, 14, 31 and 26); the existing decision stands to leave them disconnected until the SA Pre-qual AI Agent is live and tested, then dependency-check and archive them under separate approval.

The current-day generated shell was deleted after the same-day task-history dependency check found no owner or active build. All five goal nurtures were rechecked and remain unchanged, Published but disconnected pending the SA Pre-qual AI Agent.

### Priority 3: data hygiene

- `old member`, `oldmember`, `old pt client`, `7 day trial` and `trial` all remain present. They are legacy lifecycle evidence with known downstream meaning; do not merge or delete them by name alone. Any retirement requires contact-population and workflow dependency evidence.
- The three life-stage fields are not literal duplicates: two remain form-bound capture fields and `Lead: Life Stage` is the canonical reporting field. Their inconsistent answer labels are normalised at the workflow layer; retirement is appropriate only when the source forms are rebuilt.
- Canonical `postpartum` tag `b5C5Fq9ot5P5C9j9qmIR` was created on 18 July 2026 and added to all 8 contacts carrying `post partum`; direct verification confirmed 8/8. The published `PPP 30DNNC` delivery condition reads canonical `postpartum` and has no legacy condition. San-Rene Tan's genuine 4 August intake proved the canonical route and read back `Lead: Life Stage = Postpartum` after its scheduled 6:00 am branch on 5 August. Owner-approved cleanup then removed `post partum` from the generic, organic PPP and paid PPP actions. Each workflow was saved, reloaded and verified Published with `postpartum` and `30dnnc` retained. The legacy tag was deleted successfully and a fresh search returned no result. `goal: postpartum` and `notify-story-postpartum` remain separate operational signals.
- `Stay On List (Reactivation)` custom value `VLVX0STjrSyNnKsBhcJH` was deleted on 30 July 2026 after its parent workflow was archived and a 271-template rendered-content scan returned zero consumers. The deletion succeeded and a fresh API inventory confirmed the value was absent.
- Lead-source taxonomy expanded on 23 July 2026: Website Organic, Organic Social, Referral, Walk-In, Event and Other were added while Paid Social, Paid Search and legacy Organic were preserved. The two published guarded writers require the field to be empty, the unsafe direct action was removed from all eleven 30DNNC intake workflows, and controlled testing proved a later route did not overwrite the first-touch value. This control is closed; continue monitoring completeness without reintroducing downstream overwrites.
- Trainer roster corrected on 23 July 2026 to the owner-confirmed list: Megan, Piper, Nora, Katrina and Leisa. `Who is your personal trainer?`, `CS: Results/Value - Coach Contacted` and `Who was your trainer today?` were all updated and reopened to verify the saved options; the survey also retains `I can't remember`. Live searches by both name and all eight documented Beth/Hannah calendar IDs returned no results, so those former-trainer calendars were already absent and no deletion was required. `PT Block Trainer` remains automation-fed free text pending workflow-trigger repair.
- Nora Silva's live Strength Assessment meeting location was repaired and API-verified on 24 July 2026. All three round-robin staff assignments now use `The Evolved All Female Gym, 7 Paris Street West End 4101` through GHL's current `locationConfigurations` field.
- Live inspection of `PT: Block Tracking & 13-Week Rebooking` confirmed the cover-session attribution edge case. `PT Block Trainer` is populated from `{{appointment.user.name}}`, so a temporary cover coach delivering the first qualifying appointment can be recorded as the block trainer. Peter accepted this low-frequency limitation on 24 July 2026 because rebooking is now owned by Admin Eve and is intended to become automated. No new field or workflow change is required.
- Review empty custom values: Booking Thank You Page, Claim Thank You Page, DR Offer, From Email, Logo Image URL, Notifications Email For Client, Offer Name, SA Conversation Summary, Twilio placeholders, and App Login URL.
- TransformationFLIX dependency check completed; its 16 templates and legacy checkout value were deleted and verified absent on 22 July 2026.

The live field audit on 20 July 2026 confirmed that the apparently malformed names in the fixed-width API export are display truncation, not malformed GHL fields. The live labels and merge keys render correctly.

Three distinct life-stage fields remain:

| Field | Type and folder | Options | Reading |
|---|---|---|---|
| `Lead: Life Stage` | Multi-select; `1. Marketing OS` | Teen, 20's & 30's, Planning Pregnancy, Pregnant, Postpartum, Perimenopause, Postmenopause | Canonical reporting field. |
| `Pick the most relevant stage of life` | Radio; Contact | Teen, 20s/30s, Planning Pregnancy, Currently Pregnant, Post Partum, Peri Menopause, Post Menopause | Legacy intake field. |
| `Pick the most relevant stage of life so we can send you the right information` | Radio; `Form | 30DNNC Form` | Teen, 20-30s, Planning Pregnancy, Currently Pregnant, Postpartum, Peri Menopause, Post Menopause | Active 30DNNC capture field. |

Do not delete either form-bound radio field while its forms remain live. Normalise their answers into `Lead: Life Stage` at the workflow layer, then dependency-check retirement only when the forms themselves are rebuilt.

The initial custom-value register contained 11 blank values. Peter approved deletion of ten unused template candidates on 22 July 2026: `Booking Thank You Page`, `Claim Thank You Page`, `DR Offer`, `From Email`, `Logo Image URL`, `Notifications Email For Client`, `Offer Name`, both Twilio placeholders, and `Your App Login URL`. All ten deletions succeeded and were verified absent. `SA: Conversation Summary` remains deliberately reserved for the planned pre-qualification agent.

`TransformationFLIX Sign Up` pointed to a legacy GrooveSell checkout that remained stuck connecting to its payment server. It was absent from the five waitlist sequences and all 11 seminar emails. Peter approved full retirement on 22 July; the value and all 16 matching templates were deleted and verified absent. `The FitFam Cookbook`, by contrast, remains a verified active custom value used by the published product-purchase workflow.

Peter also approved retirement of `[WARM] Seminar - Replay` and `[WARM] Seminar - Slide Deck` on 22 July. The three dual-purpose historical consumers had already been removed during the TransformationFLIX template cleanup; the one remaining consumer, `TCS - Non Member`, was permanently deleted and verified absent. Both custom values were then deleted successfully through the GHL API and a read-back confirmed neither remains. Nineteen custom values now remain.

The field and value governance view now lives at `outputs/systems/ghl-custom-data-governance-register.md`. The live API returned no exact duplicate field names; current risk is semantic fragmentation across life-stage, trainer, lead-source and payment fields rather than literal duplicate records.

### Priority 4: forms and surveys

- Corporate Gift Card Form Submission, Meta Lead Form, Website Register Interest Form, Training Event Form Submission, and Email Subscribers - Meta Lead Form were unpublished and archived during the July 2026 cleanup.
- Keep the three location-interest forms and their workflows as an intentional location SEO and demand-mapping system.
- Keep the Metabolic Classification survey as retained reference; its 2011 logic should be benchmarked before any future reuse.
- `2.4 Consultation Feedback Complete` is already connected to `SA: Coach Consultation Feedback` and its No Sale branch already adds `no sale`, writes the Blog Topic Sheet row, and enrols the contact in `2.5. No Sale - Follow Up`. Live enrollment history verified production use on 19 July 2026. Its misleading `PARQ Form Submitted` trigger label was renamed on 20 July 2026. Late-sale recovery remains in the two published agreement workflows.
- The new assessment fields are placed on `SA: Coach Consultation Feedback`. A controlled Peter Brown submission on 20 July 2026 captured every displayed value against the intended custom-field IDs. Mobile contact verification confirmed Farmer Walk Seconds (`9`), Spinal Control Result (`Long`), Right Side Plank (`80`) and Left Side Plank (`87`) all persisted correctly. Toes-to-Bar was correctly blank because Perform was not selected. Their earlier omission from the desktop contact panel was a layout-visibility issue rather than a persistence fault.
- The Strength Assessment Survey is not currently sent. Its trainer options were aligned to the canonical roster on 23 July 2026 so the dormant asset no longer carries a stale staff list; review the survey's purpose before reactivation.

The live folder and analytics audit on 20 July 2026 accounted for all 24 forms. In the 6–20 July window, 14 forms recorded views and 12 recorded responses. Active use was concentrated in the organic 30DNNC forms, Membership and PT agreements, PAR-Q, Coach Consultation Feedback, and the three location-interest forms.

The following 10 forms recorded no views in that window: all five paid 30DNNC variants, `Corporate Gift Card Claim`, `Pre-Exercise Form`, `Website: Register Interest`, `Workshop Opt In Form`, and `Strength Assessment Calendar Form`. Zero recent views was treated as a review signal rather than deletion evidence. Later dependency checks proved `Pre-Exercise Form` was not the production onboarding dependency; Peter approved its deletion on 31 July 2026 and its historical field data was preserved.

A fresh 16–30 July analytics check recorded 209 form views and 50 responses. The visible active set included the generic and five organic 30DNNC forms, Bulimba, Coolangatta/Tweed Heads, PAR-Q and `SA: Coach Consultation Feedback`; recent execution history separately confirms Newfarm production use. Full-canvas revalidation confirms that every retained current acquisition form has an immediate source-specific response and a deliberate 30DNNC, Mobile Check and Strength Assessment-oriented destination. The generic New Lead versions are not required for coverage.

Peter approved final retirement of the gift-card asset on 30 July 2026. `Corporate Gift Card Claim` (`GbA3dlCz9L2TJfN9GwVJ`) was permanently deleted and verified absent; the root Forms library reduced from nine to eight items. Its historical submission workflow remains archived. The Strength For Industry owner and employee surveys were explicitly retained for possible future corporate use and verified present.

Peter approved retirement of the obsolete `Pre-Exercise Form` on 31 July 2026. It was deleted and verified absent through the supported forms read-back; the root Forms library reduced from eight to seven visible items. Its ten older field definitions and their historical values on three River-to-Rooftop contacts were deliberately retained: eight screening/confirmation fields plus the event goal and registration fields.

`30DNNC Form - PPP` recorded 9 views and no responses. Its public form loaded correctly in a controlled functional check, so this is not an obvious broken-form fault. Monitor a longer period and check the traffic source before changing it.

The `Employment Contracts` form folder was independently reconfirmed empty, approved for deletion, permanently removed and verified absent on 22 July 2026. The Forms library reduced from 12 items to 11 and no forms were displaced.

`Website: Register Interest` was then approved for permanent deletion and verified absent on 22 July 2026. GHL displayed its deletion confirmation and the root Forms library reduced from 11 items to 10.

`Workshop Opt In Form` was subsequently approved for permanent deletion and verified absent after reloading the Forms library on 22 July 2026. The root library reduced from 10 items to 9. Its historical ID was `6U0CBGMsLfRlMbCoQuWe`; any retained event automation that depended on this form now requires a separate trigger-dependency decision.

The follow-up dependency check found `Fitness Event Registration` published but with no enrollment trigger, no enrollments in the available 30-day history and no active workshop-form entry path. Its actions were an internal email to `info@theevolvedgym.com.au`, a generic appointment-confirmation email and an SMS referring to obsolete “r2r training,” followed by a one-minute wait. It had no task action, reply handling or re-entry. Peter approved retirement on 22 July 2026; it was set to Draft, moved from `1. Pipeline Workflows` into its `Archive` folder and verified there with four historical and zero active enrolments.

All 13 surveys were accounted for in the original audit. A fresh 16–30 July analytics check showed 26 survey views and 12 responses across the active hold, cancellation and retained Metabolic Classification surfaces. The current library presents eight top-level survey or survey-folder entries. The Strength For Industry owner and employee surveys show no current activity but are intentionally retained for possible future corporate use. Audit them again before reuse; do not connect them to a live workflow or campaign without an owner, current offer and end-to-end test.

### Priority 5: assessment roster and coach attribution

The active round-robin Strength & Longevity Assessment calendar remains `HSVEzfJH4nice96IxHem`. Its live roster is Megan Brown, Piper Mae and Nora Silva, with availability-weighted priorities of 1.0, 0.5 and 0.5 respectively.

The 2026 calendar-events audit found 220 bookings: 154 assigned to Megan, 34 to Piper and 32 to Nora. Nora's calendar-team record has a blank meeting location while Megan and Piper both use `The Evolved All Female Gym, 7 Paris Street West End 4101`. This should be fixed immediately if Nora remains an assessor; otherwise remove Nora from the round robin after checking future bookings.

`SA: Coach Consultation Feedback` is the retained delivery-evidence form. The owner decision on 30 July 2026 makes the trainer assigned to the calendar appointment authoritative for consultant attribution, so the form does not ask the consultant to repeat their name. The unused proposed `SA: Assessment Delivered By` field was deleted; exceptional cover delivery is corrected manually by Admin.

Workflow `2.4 Consultation Feedback Complete` remains the Sale and No Sale routing authority. A protected attendance webhook is designed to run after its form trigger and before outcome branching, but is not live until the hub endpoint is deployed and the authentication header and retry behaviour are verified.

The approved Strength Assessment calendar is `HSVEzfJH4nice96IxHem`. Duplicate-named calendar `z3cCnLnqwEO7jDrGA0HH` has zero recent events and is excluded from the attendance collector.

### Priority 5A: trainer calendar and staff ownership

All 36 calendars were reviewed in the live settings UI on 21 July 2026. Five zero-future-booking former-trainer calendars were then deleted and verified absent, leaving 31 calendars. The static Drive trainer-availability sheet does not match the live configuration and must not be used as the booking source of truth; its connected Drive account does not have permission to move it to the bin.

- Jo remains a GHL user, but her visible 30-, 45- and 60-minute PT calendars are inactive.
- Marnie's visible 30-, 45- and 60-minute PT calendars had no future appointments and were deleted on 21 July 2026.
- Meroe's 45- and 60-minute PT calendars had no future appointments and were deleted on 21 July 2026. Her 30-minute calendar initially contained 22 future event records for Kanika Mehta, representing 15 distinct times because seven Thursday entries were duplicated. The only Nora booking conflicts were resolved by moving Anika Aquino's 4 and 11 August appointments to 4:30–5:15 pm. Kanika was then booked into Nora's standard 30-minute calendar as two 13-appointment recurring series: Tuesdays at 5:15 pm from 4 August to 27 October and Wednesdays at 5:00 pm from 5 August to 28 October. Calendar-level verification confirmed 26 active instances, correct 30-minute duration, no missing dates and no duplicates. All 22 future Meroe records were deleted, followed by the empty 30-minute calendar. All three Meroe calendars are now absent and the account has 30 calendars. GHL no longer exposes Kanika's completed 23 June Meroe appointment in the active contact-appointment feed after its calendar was deleted; the audit record is the retained evidence of that session.
- Katrina's 30-, 45- and 60-minute PT calendars are active; her Intro Session calendar is inactive.
- Leisa's 30-, 45- and 60-minute PT calendars are active; her Intro Session calendar is inactive.
- Megan, Piper and Nora retain active PT and/or Intro Session calendars consistent with current delivery roles, subject to the separate Nora assessment-location issue above.

Calendar activation is not, by itself, proof of current employment or availability. Establish a single roster owner and a change checklist that updates My Staff, calendar ownership/status, working availability, public booking links, Trainerize ownership and the Drive contact reference together. Until then, book only through active GHL calendars and confirm exceptions with the operating owner.

### Priority 6: pipeline governance

The fresh supported-API opportunity counts on 1 August 2026 were:

| Pipeline | Records |
|---|---:|
| `[COLD] Marketing Pipeline` | 754 |
| `[WARM] Sales Pipeline` | 886 |
| `Review Pipeline` | 193 |
| `Membership Pipeline` | 135 |
| `Cancellation OS` | 114 |
| `Hold OS` | 57 |
| `Staff Hiring Pipeline` | 5 |

The complete `[COLD] Marketing Pipeline` opportunity-state audit on 4 August found 760 records, all Open and all attached to unique contacts. The stage distribution was internally coherent—178 Signed Up, 83 Opened 25%, 63 Opened 50%, 44 Opened 75%, 43 Opened 100% and 349 Course Complete—and six records had entered since the 1 August snapshot. This proved the pipeline was live but lacked terminal-state controls. On 4 August, the final Course Complete opportunity action in each of the five live delivery workflows was changed from Open to Abandoned, saved and independently reload-verified. The published Strength Assessment workflow now closes an existing COLD opportunity as Won only when the contact carries the canonical `30dnnc` tag.

The governed classification separates 354 cold-to-warm or direct-client conversions, 152 course completions without an assessment, 198 incomplete records untouched for more than 45 days and 56 current course-progress records. Peter approved the target semantics on 4 August. The exact 704-record batch was applied with per-record preconditions and immediate read-back: 354 are now Won, 350 are Abandoned and all 56 current participants remain Open. Independent final counts are therefore 56 Open, 354 Won and 350 Abandoned. Future Abandoned prevention is live and reload-verified at the terminal completion path of all five delivery workflows. Future COLD-Won prevention is also live in `2. Strength Assessment`: `Guard existing 30DNNC COLD opportunity` isolates `30dnnc` contacts, `Find opportunity` searches `[COLD] Marketing Pipeline`, and `Update opportunity` changes a found record to Won. The found, no-record and direct-assessment branches all converge on `Previously Assessed?`; the direct branch uses `Direct assessment: continue normal flow`. A full reload verified the exact edges, action settings, Published state and Saved state. The lookup does not create a COLD opportunity for a direct assessment booking.

The Membership Pipeline stage `Strength & Sculpt` was successfully renamed to `Strong, Fit & Flexible Membership` on 21 July 2026 without changing its stage ID. The required pipeline-level Save action was completed and a full reload confirmed that the new name persisted. The 20 July counts remain: Online Only 1, Fit & Flexible 1, Strong, Fit & Flexible Membership 75, Fast Track 13, PT Only 19, PT 1 p.wk 5, PT 2 p.wk 15, and zero in Gold or PT 3 p.wk. Open and Won statuses are still mixed within service-classification stages, so document whether this pipeline represents current service ownership, historical sale conversion, or both.

The 1 August full API revalidation corrects the earlier incomplete visible-stage conclusion. All 135 Membership Pipeline opportunities map to one of the nine valid current stage IDs; there are zero orphaned stage references. The complete stage counts are Online Only 2, Fit & Flexible 1, Strong, Fit & Flexible Membership 78, Fast Track 11, PT Only 21, PT 1 p.wk 6 and PT 2 p.wk 16, with zero in Gold or PT 3 p.wk. Statuses remain mixed at 95 Won, 28 Open, 2 Lost and 10 Abandoned. The structural problem is therefore semantic rather than referential: service-classification stages still mix current state, historical sales outcome and abandoned records.

The published `3.1. New Personal Training Client` workflow still finishes with a deprecated Create or Update Opportunity action configured for `Membership Pipeline / PT Only / Won`. That is a live dependency, but its outputs now resolve to the valid PT Only stage. The prior claim that Emma Spowart and Vaishnavi Vakacharla proved orphaned stage references is withdrawn; the incomplete stage count caused that false conclusion.

Do not use this pipeline as the current member or PT roster. On 30 July, Peter approved the governed operating-data hub as the future reconciliation and growth-intelligence layer rather than rebuilding this pipeline as the client database. Stripe, GHL, Trainerize and bookings remain authoritative for their own facts; the hub combines them into current service state and explainable upgrade recommendations. Preserve the existing opportunities as history, replace or remove the live PT opportunity writer only after the hub-to-GHL handoff is verified, and retire the pipeline from operational roster and candidate-discovery use. Create a new opportunity only when a genuine member upgrade conversation begins.

The wider pipeline-state audit found a substantial stale-open backlog. `[WARM] Sales Pipeline` contains 104 open Assessment Booked records, of which 98 have not been updated for more than 30 days, plus 760 open FUM records, of which 715 are 91–180 days old. `Cancellation OS` contains 28 open records already sitting in the terminal `Cancelled Member` stage. These cannot be treated as active work queues without outcome reconciliation. Hold OS also needs a current-state check: 8 Pending Hold, 6 Escalated Hold and 19 Returning records remain open, including older records that may no longer describe an active hold transition.

The 3 August contact-level reconciliation separated backlog age from actual lifecycle evidence. Peter explicitly approved the exact 393-record batch, including 19 permanent Hold-opportunity deletions. All 340 FUM opportunities carrying the explicit `not interested` outcome were set to Lost; 283 cold-history-only records were preserved for the future education/reassessment design. Eight WARM opportunities with a completed membership or PT agreement were set to Won. Twenty-five completed-cancellation opportunities already in `Cancelled Member` were set to Lost, and one older `Cancellation Form Received` record was aligned to `Cancelled Member` and set to Lost. Nineteen Hold OS opportunities whose canonical status was Completed and whose valid end date had passed were permanently removed, matching the workflow's intended pipeline-removal rule. Every record passed a live precondition guard and immediate read-back verification. An independent fresh snapshot reduced the open target queues from 969 to 576. Four additional Completed hold records remain excluded because their dates are future-facing or reversed.

The same-day Assessment Booked reconciliation then matched all 95 stale open opportunities against both Strength Assessment calendars and contact-level appointment history. Sixty had a terminal Cancelled appointment with no later booking; they were moved to `Cancelled (Rebook 72hrs)`, set to Lost and individually verified. Seventeen had no appointment history at all; they were set to Lost and verified. Eighteen had elapsed appointments still recorded as Confirmed. Trainerize supplied one exact-date tracked `Women's Standard Strength Assessment` for eight: seven active-calendar appointments were safely corrected to Showed and all eight opportunities moved to FUM. The eighth appointment belongs to the inactive legacy assessment calendar, so GHL rejected the appointment edit as `Calendar is inactive`; its exact Trainerize evidence is retained and its opportunity alone was corrected to FUM. A separate stale Assessment Booked record carrying the explicit `strength assessment showed` tag and no agreement was also moved to FUM rather than Lost.

The ten evidence-incomplete elapsed-Confirmed records were resolved on 4 August after a second full-record review of conversations, notes, tasks, appointment history, agreements and Trainerize evidence. Four contacts had explicitly cancelled or requested postponement; their opportunities were moved to `Cancelled (Rebook 72hrs)` and closed Lost. Five had no defensible delivery evidence; their stale opportunities were closed Lost without changing the recorded appointment status or asserting a cancellation. One contact had strong arrival evidence plus same-day Trainerize activity but no exact tracked assessment; her opportunity was moved to FUM while the appointment remains Confirmed and the attendance uncertainty is preserved. All ten updates passed fresh preconditions and immediate read-back verification. The independent open-target snapshot is now 465: Assessment Booked contains only four recent bookings, FUM contains 139 retained follow-up or reassessment records plus 285 legacy terminal classifiers, and no staff chase was created for historical evidence that cannot now be recovered.

The remaining 13 cancellation/rebook opportunities, one No Show and two Show records were then reconciled against their complete live contact histories on 4 August. Nine terminal records were closed Lost: eight explicit or elapsed cancellations and one 8 July No Show with no later engagement. Three non-terminal prospects were moved from the expired 72-hour cancellation stage into FUM because their conversations supported later reassessment rather than immediate rebooking. Two verified Showed assessments were corrected from the cancellation stage to `Show (24hr Decision)`; their false cancellation tags were removed and `strength assessment showed` was verified. One of those assessments still lacks Coach Consultation Feedback, so one deduplicated Admin Eve exception task was created without contacting the prospect. The two genuine No Sale records already progressing through the published follow-up were left unchanged. Independent read-back passed all 19 state checks. The fresh open-target count is 456: no open cancellation/rebook or No Show opportunities remain, four Show records remain active, Assessment Booked contains four recent bookings and FUM contains 142 retained follow-up or reassessment records plus 285 owner-preserved legacy terminal classifiers.

The 4 August Hold OS reconciliation proved that the remaining stage mismatches were mostly stale lifecycle fields rather than simple pipeline-display errors. Nineteen valid past holds with no protected newer request, Billing OS outcome or open hold task were set to Completed and removed from the pipeline. Three already-Completed contacts also had their stale opportunities permanently deleted. Rabail Aisha's future hold was corrected to Pending Hold and Pending Hold stage. Five same-day tasks assigned directly to Admin Eve were created and verified for Rabail plus the four records whose dates or historical outcomes cannot be inferred safely. The independent snapshot reduced Hold OS from 39 to 17 open records and the combined open target queues from 499 to 477. Thirteen Hold records are now aligned current or future work; the remaining four are explicit, task-owned exceptions rather than silent pipeline drift.

The three previously ambiguous Cancellation OS records were resolved on 4 August. Jenny Littler and Banthita Kesrisang were false positives from the older 27 July active-cohort snapshot; newer 2 August lifecycle runs show cancelled service and live Stripe confirms only cancelled subscriptions. Chrissie Trouton also has no active service signal and five cancelled Stripe subscriptions. Their three `Cancelled Member` opportunities were set to Lost and individually verified. The independent queue refresh reduced the combined open target count from 477 to 474. Cancellation OS now contains only four open `Notice Period (Current)` records and no open terminal-stage backlog.

Only two contact/pipeline duplicate pairs existed. Jennifer Power had a Lost `Cancelled Member` opportunity and a same-time open `Cancellation Form Sent` opportunity. Her contact carries `old member`, `old pt client`, `cancel: membership` and `cancel: pt`; the open Form Sent record was stale even though her older cancellation fields still show `Notice Active`. Marie Noy had a Lost FUM opportunity and an older open `Assessment Booked` opportunity; her contact carries `strength assessment showed`, `no sale`, `not interested`, `lost` and `cold lead`. Peter approved closure on 3 August 2026. Opportunity `viXvlV3l8MEGGLHMSoxU` and opportunity `tdeUgUXIvWK8t90bEQOh` were set to Lost, and independent API read-back verified both statuses. Apply the same authoritative-outcome rule to the wider backlog rather than bulk-closing by age alone.

The Seminar Pipeline had zero records and was detached from the two Transformation Seminar email sequences. `Transformation Seminar: Interest` and `Transformation Seminar: Attending` contained email and wait actions only, applied no seminar tags, performed no opportunity actions, and showed no enrolments in the available 30-day history on 20 July 2026. A 21 July builder inspection confirmed that neither workflow had a native enrollment trigger. Peter approved retirement of all seminar workflows on 22 July; Interest, Attending and `RE#1 - 30DNNC & SEMINAR` were set to Draft and moved to `1. Pipeline Workflows / Archive`. Peter approved deletion of the empty pipeline on 3 August. It was permanently deleted in GHL, the visible pipeline list reduced from eight to seven, and independent API read-back confirmed pipeline ID `bwIQw694VZi6ipvVgaJW` is absent.

The former three-step `Workshop Funnel` was a copied Impact School funnel rather than a The Evolved asset. Its Opt In and Training pages promoted Lauren Tickner's 2024 social-media lead-generation system; its Confirmation page promoted a short Scale Session and contained an empty calendar block. All three retained Impact School branding, legal links or disclaimers, and the configured `free.theevolvedgym.com.au` hostname did not resolve. It also showed no page views, opt-ins or sales from 22 June to 22 July 2026, had no tracking events and had no operational workspace reference. Peter approved deletion on 22 July; the funnel and its empty folder were permanently deleted and verified absent.

`RE#1 - 30DNNC & SEMINAR` had 10 waiting or processing enrolments after a 15 May bulk enrolment when it was retired. Its first six emails contained obsolete “seminar coming up next week” and eight-week challenge copy; the seventh used the `FEON` resource offer. None referenced the seminar custom values or TransformationFLIX. The 10 enrolled records remain visible as history, but will not continue receiving the sequence while it remains Draft.

The live dashboard showed overdue `PT Hold: Process` and `Membership Hold: Process` tasks on 21 July. The PT task provenance was resolved on 24 July: Erin Wilkinson's workflow execution log shows `HS: PT Hold Form Submitted` executing its former `Add An 'Admin' Task` action on 5 July at the exact task-creation time. The current published builder no longer contains that action. A title search returned nine standard and one extended historical PT-hold tasks, all now completed. They are residue from the earlier workflow version, not a live duplicate source or Railway defect.

The related `4. Attended - Interested` workflow is already unpublished and stored in `1. Pipeline Workflows / Archive`. It has 88 historical enrolments, zero active enrolments and no enrolments in the available 30-day history. Its obsolete sales-call removal action is inactive and retained only as part of the archived workflow history.

## Permanent Governance Standard

Every GHL asset should have an owner, business purpose, status, primary trigger, dependencies, expected enrolment volume, last verified date, and retirement rule. Draft and archive reviews should include active-enrolment counts, not status alone.
