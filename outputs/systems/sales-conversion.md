# Sales Conversion System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-08-04 (WARM rebook and decision-stage reconciliation)

---

## Overview

The sales conversion system handles the full journey from first contact through to membership or PT purchase. The primary pipeline is the **[WARM] Sales Pipeline**, supported by goal-specific entry workflows and the active four-day No Sale follow-up. There is no governed monthly or quarterly follow-up loop after a prospect reaches FUM.

The main sales channel is the **Strength & Longevity Assessment** — an in-gym session that captures baseline fitness data, delivers a personalised War Plan, and presents the membership offer. Sales happen in person at the studio, not via phone.

> **Note:** A second pipeline (LT Pipeline — Lauren Tickner snapshot import) was present in this account and has been deleted on 2026-04-01. It was not part of The Evolved's sales process. Several workflows and calendars imported with that snapshot may also be remnants — flagged in System Notes below.

---

## Pipeline: [WARM] Sales Pipeline
**Pipeline ID:** `JBVLybtIPZRIfjhzl5KV`

| Position | Stage | ID |
|---|---|---|
| 0 | Assessment Booked | `c419912e-6e51-4e83-8820-6700d12ae971` |
| 1 | Pre-Qualified | `f0db07c9-247f-41d5-ab68-8040f25e566d` |
| 2 | No Show (Rebook 72hrs) | `e66774c3-5ee8-4924-8802-33a1fd6d6216` |
| 3 | Cancelled (Rebook 72hrs) | `d31d88cb-fd7d-48c5-ad79-68faf382c897` |
| 4 | Show (24hr Decision) | `0aba395d-2ac7-45bc-96e1-410fbeb114c2` |
| 5 | FUM - Follow Up Monthly | `53f391b8-0173-4bd3-ad77-a9ced2c0b58a` |
| 6 | FUNQ - Follow Up Next Quarter | `3bb4fe17-c26c-4a48-8d2b-33aab3d7ab5d` |

Leads enter at **Assessment Booked** when they book the live round-robin Strength & Longevity Assessment calendar. Any trained owner, admin or coach may continue the conversation and prepare the trainer summary; Admin Eve or another authorised admin manually moves the opportunity to **Pre-Qualified** only after the shared completion map is satisfied.

Unanswered material questions remain in Assessment Booked, and the stage remains human-controlled until the pre-qualification bot is built and verified.

The 22 July 2026 transition audit confirmed that booking removes the contact from `30DNNC | Mobile Check` and adds her to `Strength Assessment: Nurture`, but does not remove any of the five life-stage 30DNNC delivery workflows. Membership and PT agreement submission, `3.0 New Member` and `3.1 New Personal Training Client` also do not remove 30DNNC or the older reactivation workflows. This can create overlapping waitlist, assessment and member communications; resolve it through a canonical lifecycle-exit workflow rather than editing each email sequence independently.

Resolved 29 July 2026: Strength Assessment now removes exactly the five life-stage delivery workflows in addition to its separate Mobile Check removal. `3.0 New Member` and `3.1 New Personal Training Client` remove those five plus Mobile Check. Full-canvas revalidation found and removed unrelated campaign, intake, PT-agreement and legacy First 7 Days targets from the three multi-select actions; all three published workflows persisted after reload.

No Show and Cancelled both carry a 72hr rebook window. Show (24hr Decision) captures attended assessments, although a prospect who needs time is recorded as No Sale before leaving and may later be corrected to Sale. FUM and FUNQ hold long-term unconverted prospects in monthly and quarterly nurture loops.

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| War Plan | draft; archived 27 July 2026 | `9207ca6e-ed4f-44ab-b67e-bc98a41068de` | Retired with no trigger or active enrolments after its three obsolete 28-day challenge emails and hard-coded Lead Connector reply notifications were confirmed. |
| DNS - Rebook App | draft, legacy; unpublished 17 July 2026 | `d32bc95f-c3bd-493a-ae30-97d28bfe6ec9` |
| No Sale - Follow Up | **published** | `72820730-c4ef-44ab-8abc-a4149cbe32bf` |
| Goal: 300% Stronger | **published; disconnected and dormant** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` |
| Goal: Lose Weight | **published; disconnected and dormant** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` |
| Goal: Postpartum Glow Up | **published; disconnected and dormant** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` |
| Goal: Strength For Life | **published; disconnected and dormant** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` |
| Goal: Tone Up | **published; disconnected and dormant** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` |
| Lead Nurture: Social Proof | draft; archived 30 July 2026 | `89002ace-158a-4049-acf4-50008fc562e5` |
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` |
| 1. New Lead (V3) | draft; archived | `ed9fc3a4-1cff-44b1-bb25-4ec62c0eb517` |
| NS - Not Interested | draft | `1c923632-cda4-4614-9795-52e01c38aab0` |
| NS - Not Interested | draft | `6b37dbfa-c231-408f-8d42-3e1846049ec1` |
| 4. Attended - Interested | draft | `43286e28-71ed-4c2c-bbd6-be90568066ef` |
| Lead Nurture: 10:1 Value | draft | `3c8559c7-732a-48cf-8b76-3bdc2f2e5753` |
| 1. New Lead (V1 - Jan24-Jun24) | draft | `3a54854b-1974-4644-92e4-34be5fd01d1f` |
| 1. New Lead (V2 Jun24-Jul24) | draft | `df92a27b-8520-48f1-8502-50af00431c99` |
| 1. New Lead (V4) Part 1 (D0-D14) | draft | `79baa502-34b6-4acd-a935-be1f282b2b7e` |
| 1. New Lead (V4) Part 2 (D15-D42) | draft | `ee9456f5-38b6-4ebf-850c-5aff3e31a1c6` |
| 1. New Lead (V4) Part 3 (D43-D105) | draft | `8c7f4b4b-e01e-4f3c-bc4f-35ae907daaeb` |
| 1. New Lead (V5) Part 1 (D0-D14) | draft | `52e43175-1f42-4f17-9c53-b96de77ff2e6` |
| No Response | draft | `62df6848-0ba5-49db-83b6-6ea845979235` |

> **Note:** V1–V5 represent iteration history and none is currently published. Some draft versions still contain active contacts, so their waits and pending actions must be inspected before archival or deletion. Two separate `NS - Not Interested` drafts exist, creating an additional duplication risk.

---

## Workflow 2: Strength Assessment — Detailed Structure

**Trigger:** Customer Booked Appointment — Strength & Longevity Assessment calendar

**Booking-trigger incident and repair, 5 August 2026:** the 31 July safety change to a sole `Appointment Status = new` trigger prevented ordinary booking-widget appointments from entering this workflow because the widget creates them as `confirmed`. Three bookings after that change were identified as missed; the two cancelled records were not replayed. The live workflow now again has one `Customer Booked Appointment` trigger, filtered to contact-only enrolment and the exact active Strength & Longevity Assessment calendar. The previous Appointment Status trigger was deleted. A full server reload verified Saved and Published state, one booking trigger, zero old status triggers, and the unchanged `Rescheduled` split, five-workflow 30DNNC exit and existing-COLD-opportunity guard.

Controlled public-widget acceptance also passed on 5 August. A clean owner-controlled contact booked a real Confirmed appointment through the production page and entered the repaired workflow immediately from `Strength & Longevity Assessment - Customer Booked Appointment`. After the intentional one-minute wait, the run took the fresh-booking and direct-assessment branches, skipped only the inapplicable removal actions, added `strength assessment booked`, created exactly one WARM `Assessment Booked` opportunity and no COLD opportunity, sent the expected booking email and SMS, delivered the internal alert, wrote the appointment row and entered `Strength Assessment: Nurture`. The workflow enrolments were then stopped and the exact test appointment, opportunity, contact and Appointments-sheet row were deleted; read-back found no remaining contact match, calendar event, opportunity or sheet row. Already-delivered controlled test notifications cannot be recalled.

The affected live same-day booking was reconciled without replaying the client communication sequence: the existing COLD opportunity was moved to `[WARM] Sales Pipeline / Assessment Booked`, the booked tag was restored, the five life-stage 30DNNC workflows and Mobile Check were stopped, and one consultant-owned prep task was created. No duplicate opportunity, SMS or email was created by the repair.

### Active Booking Reschedule Guard

The appointment trigger can run again when an existing assessment is rescheduled. On 29 July 2026, a booking-state guard was published after `Update SA: Consultant field` to prevent the complete acquisition sequence from replaying.

- **New or rebooked assessment:** when the contact does not include `strength assessment booked`, the contact follows the complete original path beginning with `Remove from Mobile Check Form`.
- **Active booking reschedule:** when the contact already includes `strength assessment booked`, the workflow sends one acknowledgement confirming the new `{{appointment.start_time}}`. It does not ask the prospect to reply or reconfirm.
- The reschedule branch then uses `Go to existing 1-day reminder` to rejoin at `Wait 1 Day Before Appointment`. The existing one-day reminder, one-hour reminder and appointment-outcome handling remain in force.

This bypasses repeated lifecycle exits, opportunity creation, nurture enrolment, booking confirmation and pre-qualification activity. The workflow remained published, and the condition, SMS, Go To action and branch connections all persisted after a full reload.

**Cancellation and fresh-rebooking control, completed 29 July 2026:** published workflow `2.3 SA: Cancelled Rebook` now adds `strength assessment cancelled`, immediately removes `strength assessment booked`, then continues to the owner notification and rebooking sequence. The action persisted after reload and the workflow remained published. The normal full returning-client booking path was live-verified to remove the cancelled state and reapply `Strength Assessment Booked`, so a genuinely fresh booking cannot be mistaken for an active reschedule.

**Entry check:** Previously Assessed? (condition: Tags includes "strength assessment")

### Branch A — New Client (no prior SA tag)

1. Internal Notification
2. **#2 Create Appointment Sheet Row** ← Google Sheets action (new bookings only)
3. Add 'Strength Assessment Booked' Tag
4. Create WARM Sales Opportunity (Assessment Booked stage)
5. Find Us Email
6. SMS Booking Confirmation
7. Add to 'SA Nurture' Workflow
8. Wait for Reply to Booking Confirmation SMS (5-min timeout)
   - **Contact Reply** → Wait 1 min → SMS Confirmed → SMS Goals → Wait for Reply (45-min timeout) → loop
   - **Time Out** → Go To (SMS Acknowledgement path)

### Branch B — Returning Client (has SA tag)

1. Internal Notification
2. Remove 'SA Cancelled' Tag
3. Create WARM Sales Opportunity
4. Find Us Email
5. SMS Booking Confirmation
6. Add to 'SA Nurture' Workflow
7. Same reply/timeout sequence as Branch A

> **Note:** The Google Sheets row (#2 Create Appointment Sheet Row) only fires on Branch A (new clients). Returning clients who rebook do not create a new sheet row.

### Shared Post-Confirmation Sequence

After the booking confirmation reply loop resolves:

- SMS Acknowledgement / SMS Goals Follow Up 1
- Admin (Internal) Notification
- PREQUALIFY: `{{contact.first_name}}` (AI pre-qual bot fires here)
- Coach (Internal) Notification
- #2 PREQUALIFY: `{{contact.first_name}}`
- Owner (Internal) Notification
- Add 'Goals Submitted' Tag

### Live Task Routing Audit: 17 July 2026

| Live task action | Assigned to | GHL due date | Operational timing in copy |
|---|---|---|---|
| PREQUALIFY: goals reply received | Admin Eve | 1 day | Within 4 hours |
| #2 PREQUALIFY: goals reply received | Contact's Assigned User | 1 day | Within 4 hours |
| #1 REBOOK: confirmation deadline expired | Admin Eve | 1 day | Human follow-up required |
| CONFIRM: no `READY` reply | Admin Eve | 1 day | Within 1 hour |
| CONFIRM: no `READY` reply | Contact's Assigned User | 1 day | Within 1 hour |

GHL's one-day task due date is the shortest available window, so the live due dates are accepted as configured. The task descriptions remain the operational standard: PREQUALIFY follow-up within four hours and READY-confirmation follow-up within one hour.

### Shared-State Pre-Qualification Reply Standard

Admin Eve, the assigned coach, the contact owner, or another trained team member may continue a pre-qualification conversation. The conversation history, not the identity of the responder, determines what comes next.

When automation has promised a personal review, the next responder introduces themselves and explains their role in one sentence. If the newest message introduces a specific goal, injury or concern that needs connected clarification, complete that line while it is current, then return to the earliest outstanding requirement before marking Stage 2 complete.

Stop injury questioning once the information is trainer-actionable and no unresolved safety issue remains. Close the branch with a non-diagnostic confidence-building bridge, recognise trusted practitioner input as context, state what will be included in the trainer's assessment focus and continue to Stage 2D.

The following instruction is the approved target wording for every PREQUALIFY task or notification that may lead to a written reply:

> "Before replying, refresh and read the complete conversation from the original goals reply. Use the SA Pre-Qualification Conversation SOP to identify which requirements are already complete.
>
> If the newest message raises a specific goal, injury or concern that needs connected clarification, complete that line while it is current, then return to the first incomplete requirement. If another team member has progressed the conversation since this task was created, work from the newest message.
>
> Stop an injury branch once the information is trainer-actionable unless a safety issue remains unresolved. Use a non-diagnostic confidence-building transition, respect trusted practitioner input as context and continue to the next stage.
>
> Introduce yourself and your role in one sentence when joining after an automated handoff. Do not repeat answered questions, restart the sequence, reveal unprompted pricing, or present the full package-price ladder."

This documentation records the required operating standard. The live GHL task copy must be updated and verified separately before it can be reported as implemented in production.

### Cancellation Handling (parallel path)

- Add 'Strength Assessment Cancelled' Tag
- Cancel Strength Assessment (appointment cancelled in GHL)
- Admin (Internal) Notification
- #1 REBOOK: `{{contact.first_name}}` (rebook outreach sequence)
- Update Opportunity → 'Cancelled (Rebook 72hrs)'

### Pre-Appointment Reminder Sequence

- Wait 1 Day Before Appointment
- Reminder/Confirmation SMS
- Wait 4 hrs
  - **Contact Reply** → Replies 'READY' → Wait 1 hr Before Appointment → How to Find Us Video SMS → Wait 1hr → **Add to Workflow [→ 2.4 Send Consultation Feedback Survey]** → END
  - **Time Out (4 hrs)** → 'No Reply' SMS → Wait 2hrs → further reply branches → SMS Deadline Reminder

---

## Workflow 2.4: Send Consultation Feedback Survey

**Enrolled from:** Workflow 2 — added after the 1hr post-appointment wait in the READY branch.

> **No standalone trigger currently set** — workflow is enrolled programmatically from Workflow 2.

### Steps

1. Wait 30 mins
2. Consultant Feedback Form SMS (sends survey link to client)
3. #3 Add SA Feedback Task (assigned to Contact's Assigned User, due in one day)
4. Wait 2 hrs
5. Check Sales Outcome (condition: `SA: Sales Outcome` field is not empty)
   - **Filled** → END
   - **Not Filled** → Reminder: Consultant Feedback Form SMS → #4 Add Admin Task to Admin Eve, due in one day with weekends skipped → END

### Live Task Routing in Supporting SA Workflows

| Workflow | Task actions | Live finding |
|---|---|---|
| `2.1 PARQ Complete` | PAR-Q summary task; trainer brief task | The summary task is assigned to Admin Eve; the trainer brief task is assigned to Contact's Assigned User. Both are due the same day. Trainer brief routing corrected and live-verified 17 July 2026. |
| `2.1A SA: PAR-Q Chase` | Final incomplete-PAR-Q chase task | Published supporting workflow. `2. Strength Assessment` adds the contact immediately after the one-day-before `Reminder/Confirmation SMS`. The chase waits three hours, exits if the `parq complete` tag exists, sends one reminder SMS if not, waits another four hours, checks again, then creates an Admin Eve task due in one day only if the form is still incomplete. Live-verified 17 July 2026. Workflow ID: `f1b784dd-5c78-41fc-84af-0e636115a68d`. |
| `2.2 SA: No Show Rebook` | Two confirm-rebook tasks; one final no-response task | All assigned to Admin Eve, due in one day, weekends skipped. |
| `2.3 SA: Cancelled Rebook` | Two confirm-rebook tasks; one final no-response task | All assigned to Admin Eve, due in one day, weekends skipped. Final task wording corrected to cancellation rebooks and live-verified 17 July 2026. |
| `2.4 Consultation Feedback Complete` | None | No Create Task actions found. |
| `2.5. No Sale - Follow Up` | None | No Create Task actions found. |
| `Strength Assessment: Nurture` | None | No Create Task actions found. |

The PAR-Q send and chase are now connected as one live path: `2. Strength Assessment` sends the form link in `Reminder/Confirmation SMS`, then immediately starts `2.1A SA: PAR-Q Chase`. Form submission is handled separately by `2.1 PARQ Complete`, which adds the `parq complete` tag used by both chase checks and routes the summary and trainer-brief work.

### Why this is a separate workflow

Previously the feedback survey was embedded inside Workflow 2's pre-appointment sequence. Any appointment time change, even a 15-minute adjustment, triggers GHL's "Appointment Change" event, which ejects the contact from Workflow 2 mid-sequence. This caused the feedback survey to not fire for rescheduled appointments.

**Fix (implemented 2026-05-06):** Add "Add to Workflow → 2.4 Send Consultation Feedback Survey" at the end of the READY branch in Workflow 2, after "Wait 1hr". This decouples the survey from the reminder sequence. Since 29 July 2026, active reschedules bypass the one-time acquisition actions and rejoin the shared reminder path at `Wait 1 Day Before Appointment`.

The 4 August 2026 Heena Samreen incident proved that a cancelled appointment rescheduled in place can retain the same event identity without producing the fresh workflow enrolment assumed by that path. The appointment was subsequently marked completed and received `strength assessment showed`, but it never reached `2.4 Send Consultation Feedback Survey`. Heena was enrolled manually. The published `2.4` workflow now also starts when `strength assessment showed` is added, and workflow re-entry is disabled. The original parent-workflow handoff remains the normal path; the tag trigger is a first-assessment fallback that prevents a delivered assessment from missing the consultant prompt while suppressing a second enrolment when the normal path already ran. Returning-member reassessments remain outside this acquisition control and require their separately scoped process.

## Consultation Feedback Outcome Routing: Live Audit 19 July 2026

`2.4 Consultation Feedback Complete` (`6d3cd8f8-890d-462a-b023-89f31114d2a9`) is published and actively processing coach submissions. Its form-submitted trigger is correctly filtered to **SA: Coach Consultation Feedback** (`Z83KtjAPMclhe8bsFJwS`). The former **PARQ Form Submitted** display label was renamed on 20 July 2026.

The workflow first creates the existing consultant-performance row in `Brown & Casserly Pty Ltd 2026` → `Consultant Performance`, columns A:K, then evaluates `SA: Sales Outcome`.

- **Sale:** when `SA: Sales Outcome` is `Sale`, the workflow ends without further action. This is intentional because the completed Membership or PT Agreement owns fulfilment and any late-sale recovery.
- **No Sale/default:** adds the `no sale` tag, creates a second spreadsheet row in the Blog Topic Sheet, and enrols the contact in `2.5. No Sale - Follow Up` (`72820730-c4ef-44ab-8abc-a4149cbe32bf`).

Enrollment history confirms recent production use. The first visible page contained ten finished enrolments from 23 June to 14 July 2026; six visibly completed at the `Add to 'No Sale' Workflow` action.

Assessment fields placed on `SA: Coach Consultation Feedback` write directly to their linked GHL contact custom fields when the form is submitted. No additional workflow action or spreadsheet export is required to persist those values on the contact. The fields were placed and a controlled Peter Brown submission was verified on both desktop and mobile contact layouts on 20 July 2026.

`2.5. No Sale - Follow Up` is published with no standalone trigger because it is enrolled programmatically by this No Sale branch. Once enrolled it removes the SA nurture, updates the spreadsheet and opportunity, sends the Day 1 to Day 4 follow-up, waits four more days, then independently moves the opportunity to **FUM** through its own `Update Opportunity to FUM` action. The 30 July live check confirmed the action targets `[WARM] Sales Pipeline / FUM - Follow Up Monthly`, and recent production history showed four completed July contacts plus one contact still progressing through the workflow.

### Approved outcome ownership

**Consultation Feedback Complete:** the coach's submission already records the immediate Sale or No Sale outcome. The No Sale branch adds `no sale` and enrols the contact in `2.5. No Sale - Follow Up`; that workflow can then move the opportunity to FUM after four days. FUNQ should be a later aging rule, not the immediate post-assessment destination.

Do not use the Sale branch to reverse No Sale state or close the WARM Sales opportunity. A coach may submit No Sale shortly after the consultation and the prospect may decide to join up to 24 hours later, so the completed agreement is the authoritative conversion event.

**Agreement workflows:** both live agreement workflows now find the most recently created opportunity in the WARM Sales Pipeline. When found, they close it as Won, remove the contact from `2.5. No Sale - Follow Up`, remove `no sale`, and continue through the existing agreement and onboarding actions. The Opportunity Not Found branch rejoins the agreement path so a missing WARM opportunity cannot suppress fulfilment.

An Admin Eve exception for Sale without a completed agreement cannot be created inside an agreement-submission workflow because submission itself proves the agreement exists. If this control is required, build it as a separate Sale/Won audit triggered outside the agreement workflows and check for an empty applicable agreement date.

### Agreement workflows already handling fulfilment

`Membership Agreement Form: Email` (`355337b6-14fc-4c00-b9e7-3b0794a391aa`) triggers when the Membership Agreement Form is submitted. Before its existing fulfilment path, it reconciles any prior No Sale state and closes a matching WARM Sales opportunity as Won. It then records the agreement date, sends an internal notification and member email, and branches by Membership Type.

- Fit & Flexible: adds `limited`, updates appointment and sales spreadsheets, creates the Active SGPT row, and creates a Won $299 Membership Pipeline opportunity in Fit & Flexible.
- Strong, Fit & Flexible Membership: adds `bronze`, performs the equivalent spreadsheet actions, and creates a Won $399 Membership Pipeline opportunity in the `Strong, Fit & Flexible Membership` stage.
- Fast Track: adds `silver`, performs the SGPT and PT spreadsheet actions, and creates a Won $599 Membership Pipeline opportunity in Fast Track.

These plan tags are the existing intentional bridge into `3.0 New Member`; they do not need to be recreated in Consultation Feedback Complete.

`PT Agreement Form: Email` (`f8c76dc6-907d-4e69-9f23-6989e2b10447`) triggers when the Personal Training Agreement Form is submitted. Before its existing fulfilment path, it reconciles any prior No Sale state and closes a matching WARM Sales opportunity as Won. It then records the agreement date, sends an internal notification and client email, adds `personal training`, and updates the appointment.

After appointment conversion, the workflow now checks Membership Type. Non-Fast-Track PT clients continue through the Sales and Active PT worksheet actions and then enter `3.1. New Personal Training Client`. Fast Track clients skip the two worksheet actions and enter the same onboarding workflow directly because their membership-agreement branch already owns those records.

Grace Arnell's repeated onboarding was traced to two Personal Training Agreement Form submissions less than three minutes apart on 13 July 2026. Both agreement executions called `3.1`; because that workflow allowed re-entry, the one-time welcome sequence ran twice. Re-entry is now disabled in published workflow `3.1`, while multiple-opportunity entry remains off. Later agreement processing remains available, but completed clients cannot repeat the welcome, First 7 Days, review-request or pipeline setup.

Read-only builder inspection on 28 July 2026 confirmed a deterministic worksheet-mapping defect. The Sales row action leaves Product, Trainer Assigned, Cash Taken, Added to Trainerize and Debits Set Up unmapped; the Active PT row action leaves Session Length, Sessions per week, Session Rate and Weekly Debit unmapped. The rows are therefore created successfully but incomplete by design. Do not treat blank commercial or provisioning columns as evidence that Stripe or Trainerize failed.

The immediate cross-workflow duplicate was corrected on 29 July 2026. Vaishnavi Vakacharla's incomplete Sales row 133 and Active PT row 49 were removed with owner approval, while complete rows 132 and 48 were preserved. The next Railway refresh and CEO dashboard both reported zero duplicated Active PT identities.

Further remediation should remain staged and idempotent. Agreement submission may create a pending record only when structured PT terms are present; Stripe subscription creation or first successful payment should backfill authoritative product and debit evidence; Trainerize success should independently set its provisioning flag. Any required value still absent should become an Admin exception.

The governed implementation specification is `outputs/systems/pt-roster-self-mending.md`.

---

## Forms / Surveys

| Form / Survey | Type | ID |
|---|---|---|
| Website: Register Interest | Form, deleted 22 July 2026 | `hJohXvBZv6gn0jD3AdpR` |
| Metabolic Classification Form | Survey | `3dC0KGX0gwEjkDf5YZHx` |
| Strength Assessment Survey | Survey | `ub4UbCMRY1gsp7dhGLWf` |
| SA: Coach Consultation Feedback | Form | `Z83KtjAPMclhe8bsFJwS` |

Trainerize is the in-session source of truth for physical-assessment data. The coach then submits **SA: Coach Consultation Feedback** to re-capture sales, coaching and test data in GHL for marketing and remarketing; a future Trainerize-to-GHL API or custom application should remove this duplicate entry.

The client-facing Strength Assessment Survey is not currently sent and is not part of the live assessment journey. Its trainer question was nevertheless aligned on 23 July 2026 to Megan, Piper, Nora, Katrina and Leisa, plus “I can't remember”.

The Metabolic Classification survey remains a retained reference tool rather than an active acquisition CTA.

---

## Calendars

| Calendar | Type | ID |
|---|---|---|
| Strength & Longevity Assessment [WEST END, BRISBANE] | round_robin | `HSVEzfJH4nice96IxHem` |
| Strength & Longevity Assessment [WEST END, BRISBANE] | event | `z3cCnLnqwEO7jDrGA0HH` |
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` |
| Intro Session - Megan | personal | `tc9BC56PdRNQGQmY0CgN` |
| Intro Session - Leisa | personal | `UTOhZ4UA8XDPYEZend4p` |
| Intro Session - Katrina | personal | `pPu3BfzgdKgKYGlYGeAX` |
| Intro Session - Piper | personal | `Nbzw8JiElSyeXdDqBLnQ` |

The active acquisition calendar is the round-robin **Strength & Longevity Assessment [WEST END, BRISBANE]**, ID `HSVEzfJH4nice96IxHem`. The similarly named event calendar is not the live Strength Assessment booking calendar and should not be treated as an alternative assessment entry point.

The live round-robin roster was verified on 20 July 2026 as Megan, Piper and Nora. The 2026 calendar history contained 154 bookings assigned to Megan, 34 to Piper and 32 to Nora. Nora's team record has no meeting location while Megan and Piper both use the West End gym address; add the address if Nora remains an assessor or remove her only after checking future bookings.

`SA: Coach Consultation Feedback` does not explicitly ask which coach delivered the assessment, so reporting currently infers the coach from the appointment's assigned user. This is adequate only if assigned-user ownership always matches delivery. Add a short coach dropdown if cover arrangements make that inference unreliable.

---

## Custom Fields

### Sales-Specific Fields (Group: `7OLlEnKGr65RqbvvEh5n`)

This shared GHL field group contains two distinct systems. The Strength Assessment Survey (`ub4UbCMRY1gsp7dhGLWf`) uses the trainer, rating, value and membership-decision fields. The preserved Strength For Industry survey pair uses the corporate feedback, testimonial-consent and business-introduction fields.

The two corporate fields for a team strength report and follow-up workshop are not on either current corporate survey and have zero stored values. Both remain staged for a future corporate rebuild. The obsolete TransformationFLIX access field was deleted and verified absent on 31 July 2026.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Did you sign up for a membership today? | RADIO | `contact.did_you_sign_up_for_a_membership_today` | Yes, I'm pumped to get started! / Not yet, I'm still thinking / Not for me right now | `gVnwhZcfXH4ZrzKNSc7G` |
| If you didn't sign up today, what's the 1 reason? | RADIO | `contact.if_you_didnt_sign_up_today_whats_the_1_re` | Price / Timing/Life's Busy / Didn't Feel Ready | `k7CS8cbIpDOLBAcKLVcF` |
| How would you rate your Strength Assessment? | NUMERICAL | `contact.rating_rat584_how_would_you_rate_your_str` | — | `byDrhCe6GCy390V74rzw` |
| What was the most valuable part of the session? | LARGE_TEXT | `contact.what_was_the_most_valuable_part_of_the_se` | — | `Um06lHQJGX2SPic4QAFT` |
| What would you change or improve next time? | LARGE_TEXT | `contact.what_would_you_change_or_improve_next_tim` | — | `K3iRFkx5UUpY19TNqvkT` |
| Who was your trainer today? | RADIO | `contact.who_was_your_trainer_today` | Megan / Piper / Nora / Katrina / Leisa / I can't remember | `8JSzaPXo9REKsnAXcOM5` |
| A strength report to show your team's baseline | RADIO | `contact.a_strength_report_to_show_your_teams_base` | Yes / No | `bdr4mCpPoXciN7S8qn4C` |
| (If yes) How should we refer to you in your testimonial? | TEXT | `contact.if_yes_how_should_we_refer_to_you_in_your` | — | `8PWfqZAftljrQf5k4Ybs` |
| (If yes) Let us know how to best be introduced | LARGE_TEXT | `contact.if_yes_let_us_know_how_to_best_be_introdu` | — | `dnlTEO2XI5npwtOqBTwb` |
| (If yes) What would you say to another business owner? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_another_busi` | — | `q3lXDIkx4keP5NMsxgLG` |
| (If yes) What would you say to someone thinking about joining? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_someone_thin` | — | `WwnjD5JDfpllWCMqjzjS` |
| May we use your name, role and company in testimonials? | RADIO | `contact.may_we_use_your_name_role_and_company_in_` | Yes / No | `sjSjQd5MokZPHhJH2N2O` |
| Do you know any business owners who might benefit? | RADIO | `contact.do_you_know_any_business_owners_who_might` | Yes / No | `KmV5ihGgQvwMMBx0f8cd` |
| Would you like a follow up workshop in 6 months? | RADIO | `contact.would_you_like_a_follow_up_workshop_in_6_` | Yes / No | `288nVH0JljFIE3BiVXaF` |

---

### Goal / Stage of Life Fields (Group: `9klbgmldALQR9VbYrMr8`)

These fields classify leads by goal and life stage for goal-branching workflow routing.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Pick the most relevant stage of life | RADIO | `contact.pick_the_most_relevant_stage_of_life` | Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause | `gKk8C5noKS1Gs81vKafA` |

**Alternate version (Group: `GuiXAoJoZHSIaS669O8A`):**

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Pick the most relevant stage of life (so we can personalise) | RADIO | `contact.pick_the_most_relevant_stage_of_life_so_w` | Teen / 20-30s / Planning Pregnancy / Currently Pregnant / Postpartum / Peri Menopause / Post Menopause | `tGaGYawO3Q4AAPnuznF7` |

> Two versions of this field exist in different field groups — one preserves 457 historical intake answers and one is the transient 30DNNC capture field. Their option values differ slightly (Post Partum vs. Postpartum), but published delivery workflows normalise both into canonical `Lead: Life Stage` values. The zero-population 30DNNC field remains live and must not be deleted merely because its submitted value is not retained on contacts.

---

### Fitness Goal Field (Group: `JwbflBU2YDUaZb9godHU`)

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| What are your primary fitness goals? | CHECKBOX | `contact.what_are_your_primary_fitness_goals` | Lose Weight / Tone Up / Improve Health / Improve Posture / Get Stronger / Injury Prevention | `HbIxBf5wqpYIQuETaemm` |

---

### Metabolic Classification Fields (Group: `d5MFIbXvk4dTXJ0S2kwD`)

Used in the Metabolic Classification Form to score and classify leads before sessions. Feeds the `Metabolic Blueprint` workflow.

| Field | Type | Key | ID |
|---|---|---|---|
| Metabolic Classification Score | NUMERICAL | `contact.score_metabolic_classification_score` | `6SQirWtVQGGSo7W6HklT` |
| 1. Whether you wish to gain or lose weight | RADIO | `contact.1_whether_you_wish_to_gain_or_lose_weight` | `VrQDMPYspbp9AAvNN5Qb` |
| 2. Age influence on metabolism | RADIO | `contact.2_yes_its_true_age_does_influence_metabol` | `Z7OBrGmrtAGrTeBFwzHI` |
| 3. Population/genetic background | RADIO | `contact.3_from_research_its_clear_that_some_popul` | `i18IGzbd5SOzvEsZkJRP` |
| 4. How many diets have you been on? | RADIO | `contact.4_how_many_diets_have_you_been_on` | `xfqo5tRDetZPtWY3tdWX` |
| 5. Breakfast habits | RADIO | `contact.5_breakfast_is_a_powerful_trigger_that_ca` | `xZ9IS72OCk2UqHbb0JaR` |
| 6. Past 6 months meal structure | CHECKBOX | `contact.6_for_the_past_6_months_pick_the_statemen` | `92uxbyv6ge8Ard6cOiKD` |
| 6. Current eating description | RADIO | `contact.6_right_now_what_description_best_describ` | `C3xZccZrxS2zxREsU0Fg` |
| 7. Structured 12-week body transformation history | RADIO | `contact.7_how_many_structured_12_week_body_transf` | `O4lrkKe2PEZThlfVKP2n` |
| 8. Omega 3 knowledge | RADIO | `contact.8_a_high_ratio_of_omega_3_is_essential_fo` | `FT3Jy5fXkhCcgxSt1z02` |
| 9. Resistance exercise history | RADIO | `contact.9_with_every_passing_decade_adults_lose_t` | `ZttqTyzvgfMwhzG5E0tj` |
| 10. Aerobic exercise frequency | RADIO | `contact.10_how_often_do_you_perform_aerobic_type_` | `Cf6KvIgf26qjJGYSjj8U` |
| 11. Body fat level | RADIO | `contact.11_how_much_body_fat_you_have_and_how_lon` | `g9MR18aAMemCQoc7Otfm` |
| 12. Body fat storage pattern | RADIO | `contact.12_where_you_store_your_body_fat_has_impo` | `ZFgG35JN5T02j94tRuZK` |
| 13. Sleep quality | CHECKBOX | `contact.13_sleep_quality_has_a_profound_effect_on` | `Y1SolIU7VWbatXBSejpl` |
| 14. Metabolic blockers | CHECKBOX | `contact.14_metabolic_blockers_are_poor_sleep_habi` | `KZG1ydSgLgVnp3ivCGOP` |
| 15. Mirror/body confidence | RADIO | `contact.15_when_you_stand_in_front_of_the_mirror_` | `02Ed49bwNfKCFRDZrVzp` |

---

### Strength Assessment Fields (Group: `9My8zVPIm9hqJA0XqRND`)

Collected during the in-gym Strength & Longevity Assessment. Used for the War Plan personalisation.

| Field | Type | Key | ID |
|---|---|---|---|
| SA: Body Weight (kg) | NUMERICAL | `contact.sa_body_weight` | `wGaoPgkcWaGfpEi7WJKL` |
| SA: ATG Split Squat Elevation Level | RADIO | `contact.atg_split_squat_elevation_level` | `ROQU8f9sB8u0FWBJkCUM` |
| SA: ATG Split Squat Reps Performed | NUMERICAL | `contact.sa_atg_split_squat_reps_performed` | `MQCtvk4nCyH7N59Y8UUj` |
| SA: ATG Split Squat Weight Used (kg) | NUMERICAL | `contact.sa_atg_split_squat_weight_used` | `8VIQSzbbNTbtzvLlo937` |
| SA: Farmer Walk Weight Used (kg) | NUMERICAL | `contact.sa_farmer_walk_weight_used` | `TEVGkJruuFpuyYATSTFU` |
| SA: Plank Level | RADIO | `contact.sa_plank_level` | `YS1LOUYpW3GZXuxkpcwS` |
| SA: Plank Seconds Held | NUMERICAL | `contact.sa_plank_seconds_held` | `0CCKI0vy1tcPlhGXdnPC` |
| SA: Single-Leg Capacity Right Result | SINGLE_OPTIONS | `contact.sa_singleleg_capacity_right_result` | `7LV4rJJJFISrPSzNbVYb` |
| SA: Single-Leg Capacity Left Result | SINGLE_OPTIONS | `contact.sa_singleleg_capacity_left_result` | `RMR33qtVzDO9cbtdu5IP` |
| SA: ATG Split Squat Right Elevation Level | RADIO | `contact.sa_atg_split_squat_right_elevation_level` | `2ojSBnSABbPMwOnvsSE0` |
| SA: ATG Split Squat Left Elevation Level | RADIO | `contact.sa_atg_split_squat_left_elevation_level` | `4D0vJ0nE5cObjslPnrKk` |
| SA: ATG Split Squat Right Reps Performed | NUMERICAL | `contact.sa_atg_split_squat_right_reps_performed` | `Iypi4EBnIMqZUwtFQCy1` |
| SA: ATG Split Squat Left Reps Performed | NUMERICAL | `contact.sa_atg_split_squat_left_reps_performed` | `4n3kZk4NDLWzFAeBJd1D` |
| SA: ATG Split Squat Right Weight Used (kg) | NUMERICAL | `contact.sa_atg_split_squat_right_weight_used_kg` | `aLsapSrvegP0CXdGyc14` |
| SA: ATG Split Squat Left Weight Used (kg) | NUMERICAL | `contact.sa_atg_split_squat_left_weight_used_kg` | `VQaESF9gaNHSOzaKRKpd` |
| SA: Grip Endurance Result | SINGLE_OPTIONS | `contact.sa_grip_endurance_result` | `5ZdecFeWposhuKRcJHYJ` |
| SA: Farmer Walk Seconds Held | NUMERICAL | `contact.sa_farmer_walk_seconds_held` | `bMOc36E7gTQWNMdETjQr` |
| SA: Spinal Control Result | SINGLE_OPTIONS | `contact.sa_spinal_control_result` | `bF9pweHCQPm5U4crPjv0` |
| SA: Side Plank Right Seconds Held | NUMERICAL | `contact.sa_side_plank_right_seconds_held` | `MYTLwJaH5hxqp4356g0l` |
| SA: Side Plank Left Seconds Held | NUMERICAL | `contact.sa_side_plank_left_seconds_held` | `ZQJQ1cFkZcWpkIdx4DLD` |
| SA: Toes to Bar Reps | NUMERICAL | `contact.sa_toes_to_bar_reps` | `hH20HXgUcKwmt46puk2T` |

SA: Plank Level options: Half Plank (Knees) / Bear Plank (Knees Bent & Elevated) / Full Plank

SA: ATG Split Squat Elevation Level options: Stool + 4 x 15kg Bumper Plates through to Floor (8 levels descending)

Result field options: Below Live / Live / Long / Perform. The original aggregate ATG Split Squat and Plank fields remain legacy fields until the Coach Consultation Feedback form is migrated and verified against the new side-specific and raw-result fields.

---

### Lead Source Field (Group: `yCGIA0tMjIzAVjRjSQXq`)

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Lead Source | SINGLE_OPTIONS | `contact.lead_source` | Paid Social - Meta / Paid Search - Google / Organic / Website Organic / Organic Social / Referral / Walk-In / Event / Other | `PMDHTnyNEhZS4qgOhUxE` |

Governance rule: treat `Lead Source` as the original, first-touch source and do not overwrite a populated value. `Organic` remains as a legacy option for historical records and existing workflow dependencies.

---

### Membership / PT Agreement Fields (Group: `e3OeSDdsc8ZCJGnBKLL0`)

Captured at point of sale — agreement sign-off and debit setup.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Membership Type | MULTIPLE_OPTIONS | `contact.membership_type_commencement_you_are_sign` | `Fit & Flexible`; `Strong, Fit & Flexible`; `Fast Track Package` | `1SgYibtlIuophn9FYAh8` |
| Today's Upfront Cost Is | MULTIPLE_OPTIONS | `contact.todays_upfront_cost_is` | $299 / $399 / $599 | `KX6dFWysypvQ2ju5Y21g` |
| Regular weekly debit amount (starts in week 4 for week 5) | MULTIPLE_OPTIONS | `contact.weekly_debit_amount_after_30_days` | $69 / $99 / $149. Renamed in GHL on 23 July 2026; merge key preserved for dependency safety | `d5Ig4OX79xc90WDYbdrN` |
| First Debit Date Is | DATE | `contact.first_debit_date_is` | — | `4agatus8jm9HUfBaRqJE` |
| Membership Agreement Date Signed | DATE | `contact.membership_agreement_date_signed` | — | `1WWilN82DxffsOdgKV2Y` |
| PT Agreement Date Signed | DATE | `contact.pt_agreement_date_signed` | — | `m7XNn6iutAoI4br2QUXu` |
| PT Agreement: Initial (24hrs Notice to Reschedule) | TEXT | `contact.initial_i_understand_sessions_rescheduled` | — | `iQfRvYyyX2uwI1m7XTx1` |
| PT Agreement: Initial (30 Days Notice to Cancel) | TEXT | `contact.initial_i_understand_terms_of_my_cancella` | — | `apLeFgJVKLuMIe8EKBjz` |
| Acknowledgement of Terms Initial | TEXT | `contact.acknowledgement_of_terms_initial_i_unders` | — | `YlRqSMojFrvy7xvD6VWe` |
| Signature | SIGNATURE | `contact.signature` | — | `a9vPpSzxm4YVHF9Z5uPd` |

---

### Current PAR-Q / Health Screening Fields

Collected in current form `PAR-Q` (`yziUG4EO90xQMtBx5xU1`) before the physical assessment. The separate zero-submission `Pre-Exercise Form` was deleted on 31 July 2026 after confirming it was not the production dependency; its ten populated historical fields were preserved: eight screening/confirmation fields plus the River-to-Rooftop goal and registration fields.

| Field | Type | Key | ID |
|---|---|---|---|
| Emergency Contact | TEXT | `contact.emergency_contact` | `wLxj7gtob8AQdgJYSE0X` |
| PARQ: Heart Condition | RADIO | `contact.parq_heart_condition` | `q8dzu0PQanP6cOvtv5CS` |
| PARQ: Chest Pain During Activity | RADIO | `contact.parq_chest_pain_during_activity` | `DXu8HCFQNLmiawTlR5SE` |
| PARQ: Chest Pain At Rest | RADIO | `contact.parq_chest_pain_at_rest` | `lXD4wUR5TcpJ7sWhgKQM` |
| PARQ: Dizziness or Loss of Consciousness | RADIO | `contact.parq_dizziness_or_loss_of_consciousness` | `TDvFZB9Sb9Iz0EY8tvc2` |
| PARQ: Bone or Joint Problem | RADIO | `contact.parq_bone_or_joint_problem` | `RovVdadVvY0jOe3A2kTU` |
| PARQ: Blood Pressure or Heart Medication | RADIO | `contact.parq_blood_pressure_or_heart_medication` | `uLyyvozTzfv0POL93b1T` |
| PARQ: Any Other Reason | RADIO | `contact.parq_any_other_reason` | `sxMsDNfn3U5DHv7cCQ3f` |
| PARQ: Signature | SIGNATURE | `contact.parq_signature` | `LzNvvzOLV6d0mIEVpWUI` |
| PARQ: Confirmation | CHECKBOX | `contact.parq_confirmation` | `mZx7Zkb1bF4y8N7n077Q` |

---

### Post-Session Feedback Fields (Group: `JwbflBU2YDUaZb9godHU`)

Collected after a Strength & Longevity Assessment / Intro Session.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Did you achieve the result you wanted today? | RADIO | `contact.did_you_achieve_the_result_you_wanted_to_` | Yes / No | `muAXpBFZYKZuibhy5HLQ` |
| How long have you been a member of The Evolved? | RADIO | `contact.how_long_have_you_been_a_member_of_the_ev` | Less than 3 months / Less than 6 months / More than 6 months / More than 12 months | `6rExWm1aw9kuWNFuwfBW` |
| Have you communicated any and all struggles to your coach? | RADIO | `contact.have_you_communicated_any_and_all_struggl` | Yes / No | `vqk71JXGlQmLlCQrkNJ6` |
| Have you given yourself enough time to achieve your goal? | RADIO | `contact.have_you_given_yourself_enough_time_to_ac` | Yes / No | `7M8HMiRkBlgNLiAGmfys` |
| Have you utilised the Smart Meal Plan, High Protein Guide? | RADIO | `contact.have_you_utilised_the_smart_meal_plan_hig` | Yes / No | `S8QEHcZ7yCJJ4XuzbFUH` |
| Overall out of 5 stars how would you rate the session? | RADIO | `contact.overall_out_of_5_stars_how_would_you_rate` | 1 star / 2 stars / 3 stars / 4 stars / 5 stars | `pzDHsfSCxFQ1zoWDLHUf` |
| ONE TIME OFFER: Access to our Evolved Programming | RADIO | `contact.one_time_offer_access_to_our_evolved_prog` | Yes, I still need structure / No, I'll figure it out myself | `JYfea8WFcnLUkxqJqvPH` |
| What did you achieve in your time at The Evolved? | LARGE_TEXT | `contact.what_did_you_achieve_in_your_time_at_the_` | — | `2IaeuOSVg61BGYKdyEOk` |
| Other: if you're comfortable sharing please provide | TEXT | `contact.other_if_yourre_comfortable_sharing_pleas` | — | `hzzfBiZvBy9zR3Mtefzh` |
| Why are you cancelling your personal training? | LARGE_TEXT | `contact.why_are_you_cancelling_your_personal_trai` | — | `9fiifVeY7EhdbwKtuLrQ` |

---

The former seven-day free-training checkbox (`3cyRKn2OjCJY6zrKHCZd`) was removed from the active field table and deleted on 31 July 2026. It was absent from both health forms, had zero stored values and was verified absent with the other three approved health/event-era orphan fields.

## Tags

| Tag | Purpose |
|---|---|
| `new lead` | Entry into lead nurture system |
| `lead` | General lead identifier |
| `warm reactivation lead` | Previously cold lead re-engaged |
| `cold lead` | Unresponsive or unqualified lead |
| `interested` | Expressed interest |
| `intro` | Completed intro / trial session |
| `trial` | On 7-day trial |
| `7 day trial` | 7-day trial tag |
| `won` | Converted to paying member or PT client |
| `no sale` | Did not convert |
| `no sale: financial` | Non-conversion due to price objection |
| `lost` | Lost lead / churned |
| `no show` | Did not attend booked session |
| `ns - follow up` | No-show placed in follow-up sequence |
| `not interested` | Explicitly declined |
| `no answer` | No response to outreach |
| `no response` | No engagement with comms |
| `goal tone up` | Goal tag (duplicate variant) |
| `goal: 300% stronger` | Goal tag for strength-focused prospects |
| `goal: lose weight` | Goal tag for weight loss |
| `goal: postpartum` | Goal tag for postpartum leads |
| `goal: strength for life` | Goal tag for longevity-focused leads |
| `goal: tone up` | Goal tag for toning |
| `goals submitted (under 45mins)` | Goals form completed quickly (engagement signal) |
| `strength assessment booked` | SA booking confirmed |
| `strength assessment link clicked` | SA link engagement |
| `strength assessment showed` | SA attendance confirmed |
| `action: workshop opt in` | Workshop opt-in action |
| `postpartum` | Canonical postpartum life-stage tag; created 18 July 2026 |
| `post partum` | Retired legacy life-stage tag; deleted 5 August 2026 after canonical cutover verification |
| `planning pregnancy` | Life stage |
| `perimenopause` | Life stage |
| `postmenopause` | Life stage |
| `teen` | Life stage |
| `20/30s` | Life stage |
| `organic` | Organic lead source |
| `paid` | Paid lead source |
| `meta ads` | Meta/Facebook ads lead source |
| `fb organic` | Facebook organic lead source |
| `ig organic` | Instagram organic lead source |
| `landing page` | Entry via landing page |
| `website` | Entry via website |
| `referral` | Referral lead |
| `walk in` | Walk-in lead |
| `metabolic blueprint` | Enrolled in Metabolic Blueprint sequence |
| `metabolic classification` | Completed metabolic classification |
| `met class: a` | Metabolic class A |
| `met class: b` | Metabolic class B |
| `met class: c` | Metabolic class C |
| `met class a` | Duplicate of met class: a |
| `member` | Active member |
| `personal training` | PT client |
| `pt only` | PT only (no membership) |
| `strength for life` | Strength for Life program tag |
| `gold` | Gold tier member |
| `silver` | Silver tier member |
| `bronze` | Bronze tier member |
| `online client` | Online-only client |
| `old member` | Former member |
| `old pt client` | Former PT client |
| `oldmember` | Duplicate of old member |

---

## Flow Diagrams

### Primary Funnel: [WARM] Sales Pipeline

```
Lead enters (via website form, referral, organic, or Goal workflow)
        │
        ▼
[Stage 0] Assessment Booked
        │
        ├── Trained team member completes pre-qualification and trainer summary
        │       ▼
        │   [Stage 1] Pre-Qualified
        │
        ├── Did not attend
        │       ▼
        │   [Stage 2] No Show (Rebook 72hrs)
        │       └── 72hr rebook window → back to Assessment Booked
        │
        ├── Cancelled booking
        │       ▼
        │   [Stage 3] Cancelled (Rebook 72hrs)
        │       └── 72hr rebook window → back to Assessment Booked
        │
        └── Attended Strength & Longevity Assessment
                ▼
        [Stage 4] Show (24hr Decision)
                │
                ├── Sale recorded
                │       └── plan tag verified → New Member workflow
                │
                └── Does not convert
                        └── No Sale Follow Up → after 4 days → [Stage 5] FUM
                                └── later aging rule → [Stage 6] FUNQ
```

---

### Goal Branching: Entry Routing by Goal

```
Legacy forms or manual processing may add a canonical goal tag
        │
        ├── Goal: Lose Weight        → workflow: Goal: Lose Weight (`6488e53d`)
        ├── Goal: Tone Up            → workflow: Goal: Tone Up (`124d3acc`)
        ├── Goal: 300% Stronger      → workflow: Goal: 300% Stronger (`0dc2aa9b`)
        ├── Goal: Postpartum         → workflow: Goal: Postpartum Glow Up (`d8d867a5`)
        └── Goal: Strength For Life  → workflow: Goal: Strength For Life (`fdd77dc4`)

Each goal workflow delivers one tailored email after its matching tag is added. The sequence family is published but disconnected from the current Strength Assessment booking path.
```

Live revalidation on 29 July 2026 found many recent `2. Strength Assessment` enrolments but no enrolments in any of the five goal nurtures. The assessment workflow sends the prospect an SMS asking about goals and adds only the generic `Goals Submitted` tag after a reply. It has no classification branch or canonical goal-tag action, and `3.0 New Member` also contains no goal-tag action.

These fixed one-email workflows are not part of the intended future path. The planned SA Pre-qual AI Agent supersedes them by clarifying one primary goal, capturing it as structured data, selecting relevant approved social proof and creating the trainer brief. Do not add a temporary goal-tag classifier or reconnect the five workflows. Preserve useful content for the AI story library, then archive the dormant workflows after the AI path is live and dependency-tested.

### Postpartum and 30DNNC Routing

- `30dnnc` (`yBRze9OyNVwbZVAimU3d`) is the general program tag, not a postpartum tag.
- `PPP 30DNNC` branches on `planning pregnancy`, `pregnant`, and canonical `postpartum`, then writes the corresponding life-stage value.
- `Goal: Postpartum Glow Up` triggers from `goal: postpartum` (`r9xhjBwW6JMY0MDXWmcC`), not from the retired legacy tag.
- Both PPP form-submission workflows now add a life-stage tag and PPP enrolment only when Planning Pregnancy, Currently Pregnant or Post Partum matches. An unmatched answer creates a one-day Admin Eve classification task instead; paid intake still proceeds through Mobile Check.

The canonical end state is now live: intake writers use `postpartum`, delivery writes **Postpartum** to `Lead: Life Stage`, and `goal: postpartum` remains a separate nurture-enrolment signal.

Migration began 18 July 2026: canonical tag `postpartum` (`b5C5Fq9ot5P5C9j9qmIR`) was created and added to all 8 contacts carrying the legacy tag; direct verification confirmed 8/8. The cutover completed 5 August after a genuine submission proved the canonical field route, all three intake writers were reload-verified without the legacy tag, and `post partum` was deleted. `goal: postpartum` remains separate, and the local story-notification process targets the canonical tag.

---


---

### War Plan (FUM Monthly Follow-Up)

> **War Plan** was intended as the monthly follow-up sequence for unconverted prospects in the FUM - Follow Up Monthly stage, but the live workflow did not implement that design. The 27 July 2026 audit confirmed that it had no trigger and no enrolments or executions in the available 30-day history. Its three emails were two days apart and repeatedly sold an obsolete 28-day weight-loss challenge with a two-kilogram-or-free guarantee. Reply branches notified a hard-coded mobile number and referred to the old Lead Connector app. The workflow was unpublished and archived on 27 July 2026; design any future FUM nurture as a new governed system.

```
Contact reaches [Stage 5] FUM - Follow Up Monthly
        │
        └── No governed automated follow-up currently connected
                │
                └── [FUTURE BUILD] Monthly value-driven touchpoint
                        └── Relationship nurture → re-engagement → Assessment rebook
```

---

## Suspected Process-Bypass Pricing Emails to info@theevolvedgym.com.au

Use this exception only for a low-intent email sent to `info@theevolvedgym.com.au` that seeks prices or a package menu as a way to avoid the published waitlist and Strength Assessment process. A direct email or genuine pricing question by itself is not enough.

Do not apply this exception to prospects already engaging genuinely with the waitlist, pre-qualification or Strength Assessment journey. Those enquiries follow the normal pricing-response and conversation standards.

### Response rules

- Give the approved ranges early: $69 to $149 per week and $299 to $599 upfront. In this exception, their primary commercial purpose is to let price-led prospects self-select out before consuming assessment capacity.
- State that The Evolved is currently full and opens only a small number of places each month while that remains factually true.
- Explain that prospects do not self-select a package from a list. The Strength Assessment identifies the appropriate membership and level of support.
- Position the premium subtly: fees reflect the quality of coaching, programming and individual support, rather than access to gym equipment alone.
- Keep the likely price-shopping judgment internal. Do not accuse the prospect of seeking the cheapest option or acting in bad faith.
- Match the prospect's directness while remaining calm, respectful and professional.
- Return the prospect to the current website waitlist and Strength Assessment pathway.
- Do not provide an inbox-only booking route or make an exception to the intake process.

### Approved email template

> Hi [Name],
>
> Thanks for your email.
>
> Our memberships range from $69 to $149 per week, with an upfront starting payment of $299 to $599. Our fees reflect the quality of our coaching, programming and individual support, rather than simply providing access to a gym.
>
> We're currently full and only open a small number of places each month. Because the right option depends on your goals and the support you need, we don't ask prospective members to choose a package from a list.
>
> Everyone begins with a Strength & Longevity Assessment. From there, we determine whether we're the right fit for each other and, if so, explain the most suitable membership and its full costs.
>
> If you'd like to be considered, the next step is to join the waitlist through our website.
>
> Kind regards,
>
> [Name]
> The Evolved

The canonical team documents are the Drive files `THE EVOLVED PRICING ENQUIRY RESPONSE FRAMEWORK` and `Pricing Enquiry Response SOP`. Both were updated with this narrowly scoped exception and template on 30 July 2026.

---

## System Notes & Observations

### What's working well
- **Strength & Longevity Assessment as the sales channel** — in-person assessment creates high psychological investment and a personalised deliverable (War Plan) before the offer is made
- **Goal-branching entry workflows** (5 live published workflows) personalise the funnel from first contact, routing leads through tailored nurture before booking the assessment
- **FUM nurture opportunity** — the existing `War Plan` asset is obsolete and dormant. A future monthly value-driven follow-up should be designed as a new workflow with current offers, accountable reply ownership and lifecycle exits
- **Metabolic Classification** pre-qualifies leads and produces a score (`contact.score_metabolic_classification_score`) that can be used for segmentation and personalisation
- **FUM follow-up gap**: the active No Sale workflow moves prospects into FUM, but no governed automation continues from that stage. FUNQ aging is also undefined.
- **FUM backlog is now outcome-classified, not merely aged** — the 3 August live reconciliation found 340 open FUM opportunities with an explicit `not interested` outcome, 283 records carrying only legacy `cold lead` or `lost` history, and six FUM records with a later completed agreement. Peter approved the exact batch: the 340 explicit declines were set to Lost, the six converted FUM records and two converted Assessment Booked records were set to Won, and every change passed immediate verification. The 283 cold-history-only records remain open for the future education/reassessment journey unless stronger lifecycle evidence exists.
- **Post-session feedback fields** capture the single most important conversion signal: "Did you sign up today?" and if not, why — creating a structured feedback loop

### Legacy imported sales architecture cleaned up

The LT pipeline, its old sales calendars, its calendar form, and its three legacy rebooking or confirmation workflows have been removed from the active sales architecture. The final obsolete sales confirmation workflow was verified at zero active enrolments and moved to the pipeline archive on 18 July 2026. Asset IDs and historical names are retained only in the dated backend audit record.

### Mobile Check Form — Lead Intake Connection

The **2. Strength Assessment** workflow contains a "Remove from Mobile Check Form" step immediately after the booking trigger (after a 1-min wait). This removes the contact from the Mobile Check Form workflow before the SA sequence begins, preventing overlap between the lead intake system and the assessment workflow.

The Mobile Check Form is part of the lead generation/intake system — full documentation of this form, its trigger, and its workflow is deferred to lead generation system documentation.

---

### Resolved issues
- **Cancellation followed by a fresh Strength Assessment booking was classified as a reschedule** ✅ — `2.3 SA: Cancelled Rebook` now removes `strength assessment booked` immediately after recording the cancellation. The published full booking path clears the cancelled state and restores the booked tag on rebooking. Built, published and reload-verified 29 July 2026.
- **Active reschedule replayed the complete booking and confirmation sequence** ✅ — A published booking-state guard now sends one no-reply-required reschedule acknowledgement to contacts already carrying `strength assessment booked`, then rejoins at the existing one-day reminder. The original full path remains connected for contacts without the booked tag. Built, published, reloaded and graph-verified 29 July 2026.
- **Feedback survey not firing on rescheduled appointments** ✅ — Feedback survey (Workflow 2.4) moved out of Workflow 2's pre-appointment sequence and enrolled via "Add to Workflow" action after the appointment time passes. Decoupled from appointment change events.
- **Trainer brief task routed to Admin Eve** ✅ — `TRAINER BRIEF READY` in `2.1 PARQ Complete` now assigns to Contact's Assigned User. Corrected and live-verified 17 July 2026.
- **Cancellation rebook task used no-show wording** ✅ — The final task title and description in `2.3 SA: Cancelled Rebook` now refer to cancellation rebooks. Corrected and live-verified 17 July 2026.
- **PAR-Q incomplete chase missing from the live workflow family** ✅ — Published `2.1A SA: PAR-Q Chase` and connected it immediately after the form-link SMS in `2. Strength Assessment`. The live path now checks at three hours, sends a reminder if needed, checks again four hours later, and assigns Admin Eve a one-day task only when the form remains incomplete. Built and live-verified 17 July 2026.
- **Consultation trigger label was misleading** ✅ — Renamed the live trigger that watches `SA: Coach Consultation Feedback` from `PARQ Form Submitted` on 20 July 2026.
- **Paused contacts in legacy draft workflows** ✅ — Removed all 65 paused enrolments from New Lead V1, V4 Parts 2 and 3, V5 Part 1 and the newer draft NS workflow on 20 July 2026. All five now show zero active enrolled.

### Current gaps / things to review
- **Multiple legacy draft new lead nurture workflows (V1–V5)** — their paused enrolments are cleared, but the duplicate versions still need retirement and naming governance
- **Two duplicate `NS - Not Interested` workflows** — both in draft (`1c923632` and `6b37dbfa`). One should be archived before publishing
- **`4. Attended - Interested` is in draft** (`43286e28`) — post-attendance follow-up for interested-but-not-converted prospects is unautomated. High-leverage gap to address
- **Inactive survey roster corrected**: although the survey remains unused, its trainer question now contains the canonical current roster plus “I can't remember.” Review the survey's purpose before reactivation.
- **Assessment calendar location is incomplete for Nora** — Nora received 32 assessment bookings in 2026, but her round-robin team record has a blank meeting location.
- **Coach attribution is inferred** — the feedback form does not record the assessor directly; it relies on the appointment's assigned user matching the coach who delivered the session.
- **FUM-to-FUNQ aging is undefined** — the immediate No Sale handoff into `2.5. No Sale - Follow Up` is live and evidenced in enrollment history. Define a separate aging rule only if FUNQ remains a useful reporting stage after FUM.
- **Post-sale tag naming is legacy but functional** — the Membership Agreement workflow deliberately maps Fit & Flexible to `limited`, Strong, Fit & Flexible Membership to `bronze`, and Fast Track to `silver`; these tags start `3.0 New Member`. Rename only through a dependency-checked migration.
- **Two versions of the stage-of-life field** — slight option discrepancy (Post Partum vs. Postpartum) across two field groups. Could cause misrouting in the Goal: Postpartum Glow Up workflow
- **No sale reason field is limited** — only 3 options (Price / Timing / Didn't Feel Ready). Doesn't capture objections like "Needs to discuss with partner" or "Not the right program"
- **Lead Source taxonomy expanded on 23 July 2026** — referral, walk-in, website organic, organic social, event and other are now reportable without changing legacy values. A workflow-level overwrite-guard audit remains open
# Governed Strength Assessment Attendance

Attendance and sales outcome are separate facts. The exact GHL appointment status records Showed, No show, Cancelled or Invalid; `SA: Coach Consultation Feedback` records delivered-session evidence and Sale or No Sale. The trainer assigned to the GHL appointment is the governed consultant attribution; Admin corrects exceptional cover delivery manually.

Submitting feedback must not bypass or replace the existing Sale and No Sale branches. Membership Agreement and PT Agreement completion remain authoritative for fulfilment, while missing feedback never creates a No show.

After a delivered assessment, the coach marks the exact appointment Showed and submits the existing feedback form. For cover delivery, the coach records the person who actually delivered the assessment; `Approved cover / other` creates an Admin Eve exception when the roster cannot identify them.

The attendance hub can propose `confirmed -> showed` only when one feedback submission deterministically matches one elapsed event for the same contact. All other terminal states and ambiguous matches fail closed.

Historical No show and Cancelled corrections cross a live workflow boundary. A direct status change can start `2.2 SA: No Show Rebook` or `2.3 SA: Cancelled Rebook`, change tags, create or move a WARM opportunity and later create tasks or send rebooking messages. On 1 August 2026 both published workflows were cleanly rebuilt and live-tested: `strength assessment showed` and GHL contact type `Customer` each route to an immediate stop branch, while only the no-exclusion branch reaches the original rebooking actions. The final four controlled branch runs show `No Action / Finished`; a 20-case read-only replay classified three existing Customers to stop and 17 Leads as eligible. GHL cannot express a safe rolling appointment-age comparison in this trigger or If/Else action. Do not use an ordinary historical GHL status write unless the exact contact is contained from the relevant rebooking workflow and the post-write audit verifies tags, opportunities, tasks and messages. Otherwise record the governed historical outcome in the hub and leave live rebooking automation untouched.

The 3 August stale-opportunity reconciliation did not rewrite historical Cancelled appointment statuses. It used their existing terminal GHL status as evidence, moved 60 associated open opportunities from Assessment Booked to `Cancelled (Rebook 72hrs)` and closed them Lost. Seventeen false Assessment Booked opportunities with no contact-level appointment history were also closed Lost. Of 18 elapsed Confirmed appointments, exact Trainerize assessment evidence verified eight delivered sessions: seven active-calendar appointments were corrected to Showed through the governed evidence validator, all eight opportunities moved to FUM, and one inactive-calendar appointment remains Confirmed because GHL blocks writes to inactive calendars. A separate explicit `strength assessment showed` contact was moved from Assessment Booked to FUM. No agreement-bearing record was treated as an unconverted lead.

The remaining ten elapsed-Confirmed cases were resolved on 4 August through a second full-record evidence review. Four explicit cancellation or postponement conversations supported Lost outcomes in `Cancelled (Rebook 72hrs)`. Five stale opportunities with no defensible delivery evidence were closed Lost while their appointment records remained unchanged. One likely arrival had same-day activity but no exact assessment record, so the opportunity moved to FUM while the appointment remained Confirmed and the uncertainty stayed explicit. All updates were read back successfully. Assessment Booked now contains only four recent bookings.

The same-day rebook and decision-stage review then resolved all 13 open cancellation-stage records and the single open No Show. Nine terminal outcomes were closed Lost; three prospects whose conversations supported later reassessment moved to FUM; and two exact Showed appointments were corrected from the cancellation stage to `Show (24hr Decision)` with their contact tags aligned. One older delivered assessment now has an Admin Eve exception task for missing Coach Consultation Feedback. The two genuine No Sale records already inside the published Day 1 to Day 4 follow-up were deliberately left unchanged. The resulting WARM queue has no open cancellation/rebook or No Show records, four active Show records, four recent Assessment Booked records and 142 retained FUM follow-up or reassessment records. The separate 285 legacy FUM records with terminal historical tags remain preserved under the existing owner decision rather than being treated as active follow-up.
