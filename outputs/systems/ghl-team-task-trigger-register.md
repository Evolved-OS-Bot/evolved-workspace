# GHL Team Task Trigger Register

**Prepared:** 17 July 2026; audit closure verified 5 August 2026  
**Purpose:** Team presentation and responsibility review

## Audit Status

This register combines documented task triggers with live browser verification. Material task-producing workflows across pipeline management, Hold OS, Cancellation OS, Strength Assessment, new-member onboarding, lifecycle nurture and member experience were audited and revalidated through 5 August 2026 under the full-canvas inspection standard.

This is a curated operating register, not a transcription of every historical workflow. Lower-priority event workflows remain governed through the workflow owner register and scheduled review cadence. The audit is complete; any newly created or materially changed task action must now be added through normal change control.

Internal notifications are shown separately from GHL tasks. A notification creates awareness; a task remains in the assignee's task queue until completed.

## Presentation Summary

| Team member | Main automated responsibility | Systems |
|---|---|---|
| Piper | Cancellation retention calls, farewell-session checks, mid-notice calls, and personal follow-up on first-week member replies | Cancellation OS, Membership: First 7 Days |
| Contact's Assigned Coach | Strength Assessment goal follow-up, READY confirmation, trainer-brief review, feedback completion, and member return-from-hold follow-up | Strength Assessment, Hold OS |
| Admin Eve | Pre-qualification administration, PAR-Q summarisation, rebooking follow-up, hold processing, cancellation administration, and written response to first-week member replies | Strength Assessment, Hold OS, Cancellation OS, Membership: First 7 Days |
| Peter Brown | Extended-hold approval | Hold OS |
| Megan | Booked cancellation calls | Cancellation OS |

## Piper

| Trigger | When task appears | Task / required action | Status |
|---|---|---|---|
| Membership Cancellation Form submitted, routed by cancellation reason | After a 10-minute wait; task due in one day at 12:00 pm, weekends skipped | Review the reason-specific brief and make the retention call. | Live verified across eight published reason workflows |
| Cancelling member remains in Notice Period and reaches the farewell checkpoint | Approximately Day 5; task due in two days, weekends skipped | Check whether a complimentary farewell session was booked. If not, book a 30-minute session within two days. | Live verified across the eight reason workflows |
| Cancelling member does not reply to the mid-notice SMS within two days | Mid-notice checkpoint; task due in one day, weekends skipped | Check attendance and complete the reason-specific mid-notice call. | Live verified across the eight reason workflows |

### Cancellation branches

The initial Piper task is customised for:

1. Financial
2. Health / Injury
3. Moving / Travel
4. Schedule / Time
5. Results / Value
6. New Gym
7. New Training Style
8. Other, manager call declined

`MC: Other (Booked Call)` is a separate workflow. It sends an internal notification to the owner, but its `CANCELLATION CALL` task is assigned to Megan Brown, due in seven days at 12:00 pm with weekends skipped. It is not a Piper task or a joint owner task.

## Contact's Assigned Coach

These tasks route to whichever team member is assigned to the contact. Correct contact ownership is therefore essential.

| Trigger | When task appears | Task / required action | Status |
|---|---|---|---|
| Strength Assessment contact replies with goals | On the goals-reply path; task due in one day | Review the conversation and run the shared pre-qualification SOP. Stop injury questioning once the information is trainer-actionable, use the confidence-building transition and continue to the next incomplete stage. | Live verified in `2. Strength Assessment` |
| Strength Assessment contact has not replied `READY` | After the reminder and no-reply path; task due in one day | Follow up on appointment confirmation. Task copy says action is required within one hour. | Live verified; one-day minimum accepted, one-hour response standard retained |
| PAR-Q form submitted | Two hours after the admin summary task, due the same day | `TRAINER BRIEF READY`: currently instructs the coach to review Pre-qual Summary before the session. | Live verified in `2.1 PARQ Complete`; assigned to Contact's Assigned User. The field is staged for the future AI pre-qualification agent and is currently blank, so the task wording requires interim reconciliation. |
| Consultant feedback survey is sent | After a 30-minute wait; task due in one day | Complete the Strength Assessment consultant feedback form and record the exact appointment outcome. Railway adopts the matching open task after the attendance grace period instead of creating a duplicate. | Immediate task live in `2.4 Send Consultation Feedback Survey`; governed Railway adoption live 30 July 2026 |
| Member reaches seven days before their return-from-hold date | Immediately on the `HS: Pre-Return Date` trigger; task due in one day | Check Trainerize for the first booking back and contact the member appropriately. | Live verified in `HS: Hold Return Journey` |
| Member reaches their return-from-hold date | After the five-day and two-day waits; task due in one day | Check in with the member and confirm their first session back. | Live verified in `HS: Hold Return Journey` and observed in execution logs |

The `2.1 PARQ Complete` workflow sends the coach an internal notification and assigns its `TRAINER BRIEF READY` task to Contact's Assigned User. The task routing was corrected and live-verified on 17 July 2026.

`Pre-qual Summary` is not currently an Admin Eve adoption field. It is reserved for the scoped AI pre-qualification agent, which will generate and write the governed trainer brief. Until that agent is live, reconcile the published task wording with the current screenshot/ChatGPT-assisted admin handoff so coaches are not directed to an empty field.

Both Hold Return Journey tasks assign to Contact's Assigned User. The separate coach internal notification fires on return day; it does not replace either task.

## Admin Eve

| Trigger | When task appears | Task / required action | Status |
|---|---|---|---|
| A contact replies to any Mobile Check Strength Assessment SMS | Immediately after the neutral acknowledgement and Admin Eve notification; task due in one day at 12:00 am | `LEAD REPLY: Review and respond`: read the actual conversation, do not assume urgency or positive intent, apply DND only for an explicit opt-out and continue the Strength Assessment conversation appropriately. | Live configured in both mirrored `30DNNC \| Mobile Check` reply branches and assigned directly to Admin Eve. |
| Strength Assessment contact replies with goals | On the goals-reply path; task due in one day | Run the shared pre-qualification SOP within four hours. Stop injury questioning once the information is trainer-actionable, use the confidence-building transition and continue to the next incomplete stage. | Live verified; one-day minimum accepted, four-hour response standard retained |
| Strength Assessment confirmation deadline expires | After failed confirmation; task due in one day | Contact the person whose Strength Assessment was automatically cancelled and help them rebook. | Live verified |
| Strength Assessment contact has not replied `READY` | After the reminder and no-reply path; task due in one day | Follow up on appointment confirmation. Task copy says action is required within one hour. | Live verified; one-day minimum accepted, one-hour response standard retained |
| PAR-Q form submitted | Immediately, due the same day | Use the linked SOP to write the pre-qualification summary. | Live verified in `2.1 PARQ Complete` |
| PAR-Q remains incomplete after both automated checks | Seven hours after the one-day-before PAR-Q send, following a three-hour check, reminder SMS, four-hour wait, and final check; task due in one day | `CHASE PAR-Q`: contact the member and have the health form completed before the Strength Assessment. | Live verified in published workflow `2.1A SA: PAR-Q Chase` on 17 July 2026 |
| No-show contact replies after either rebook attempt | On reply; task due in one day | Confirm that the contact has rebooked and call three times that day if they have not. Two identical task actions cover the two reply branches. | Live verified in `2.2 SA: No Show Rebook` |
| No-show contact does not reply after both rebook attempts | Final timeout; task due in one day | Call three times that day. The workflow then moves the opportunity to Abandoned and removes it. | Live verified |
| Cancelled contact replies after either rebook attempt | On reply; task due in one day | Confirm that the contact has rebooked and call three times that day if they have not. Two identical task actions cover the two reply branches. | Live verified in `2.3 SA: Cancelled Rebook` |
| Cancelled contact does not reply after both rebook attempts | Final timeout; task due in one day | Call three times that day. | Live verified; cancellation-rebook wording corrected 17 July 2026 |
| Strength Assessment attendance remains unresolved | 10:00 am on the next business day | `SA ATTENDANCE ESCALATION: Outcome still missing`: have the assigned coach submit Consultant Feedback and mark Showed, or mark the exact appointment No show or Cancelled. | Live on Railway from 30 July 2026. The workflow audit verified there is no competing two-hour feedback chase; the unrelated two-hour booking-confirmation branch remains unchanged. |
| A member submits another standard membership-hold request while already Pending Hold or On Hold | Immediately; task due in one day | Contact the member, establish why another hold was requested, and escalate an extension request to Peter. | Live verified in `HS: Membership Hold Form Submitted` |
| Standard membership hold enters any of the 1, 2, 3, or 4-week processing branches | On the applicable duration branch; task due in one day | Check the hold dates and billing pause, correct Hold Status, and escalate discrepancies to Peter. Four equivalent task actions cover the four duration branches. | Live verified in `HS: Membership Hold Form Submitted` |
| Extended-hold approval remains unactioned | Two days after escalation to Extended Hold; task due in one day | Chase Peter for an approval decision. | Live verified in `HS: Extended Hold Approval` |
| Billing OS cannot complete a hold | Immediately; due by 5:00 pm Brisbane that day, or immediately if the error occurs later | `BILLING EXCEPTION: Hold - Manual action required`: manually complete or reconcile the Stripe action, verify GHL billing status and dates, then complete the task. | Live end-to-end verified 29 July 2026; assigned directly to Admin Eve and deduplicated while the same exception task remains open |
| Membership cancellation form is accepted | Immediately; task due in 30 days | Process the membership cancellation using the submitted contact, reason, and notice dates. | Live verified in `Membership Cancellation Form Recieved` |
| PT cancellation form is accepted | Immediately; task due in one day | Verify the Stripe cancellation and final payment date, treat the following calendar week as the final PT service week, retain sessions in that week, and delete sessions scheduled after it. Escalate uncertainty to Peter before deleting appointments. | Live verified in `PT Cancellation Form Received`; full task description confirmed 17 July 2026 |
| Billing OS cannot complete a membership or PT cancellation | Immediately; due by 5:00 pm Brisbane that day, or immediately if the error occurs later | `BILLING EXCEPTION: Cancellation - Manual action required`: manually complete or reconcile the Stripe action, verify the GHL billing status and dates, then complete the task. | Live control deployed 29 July 2026; assigned directly to Admin Eve and deduplicated while the same exception task remains open |

## Strength Assessment Audit Findings

The browser audit covered these published workflows:

- `2. Strength Assessment`
- `2.1 PARQ Complete`
- `2.1A SA: PAR-Q Chase`
- `2.2 SA: No Show Rebook`
- `2.3 SA: Cancelled Rebook`
- `2.4 Consultation Feedback Complete`
- `2.4 Send Consultation Feedback Survey`
- `2.5. No Sale - Follow Up`
- `Strength Assessment: Nurture`

No live Strength Assessment findings from this audit remain unresolved. The final cancellation-rebook task wording was corrected, and the missing PAR-Q chase was rebuilt, published, and connected to the main workflow on 17 July 2026.

The PREQUALIFY and READY tasks retain one-day GHL due dates because this is the shortest available task window. Their descriptions remain the operational standard: action within four hours for PREQUALIFY and within one hour for READY follow-up.

Two older workflows, `DNA - Rebook Call` and `DNS - Rebook App`, contain invalid-trigger warning indicators and no Create Task actions. Both were confirmed as legacy and unpublished on 17 July 2026; their contents have not been promoted into this task register.

## Hold and Cancellation Audit Findings

All seven documented Hold OS workflows and all eleven task-relevant Cancellation OS workflows inspected in this batch are published.

The Hold OS audit confirmed nine task actions: five Admin Eve paths in standard membership-hold intake, two Contact's Assigned User tasks in the return journey, one Peter Brown approval task, and one Admin Eve overdue-approval task. The standard PT hold intake and both extended-hold form-submission workflows contain no Create Task actions.

The Cancellation OS audit confirmed three Piper task actions in each of the eight reason workflows, one Megan Brown task in `MC: Other (Booked Call)`, one 30-day Admin Eve task in membership cancellation intake, and one one-day Admin Eve task in PT cancellation intake. The PT task now contains the complete Stripe, final-payment, and appointment-cleanup procedure.

## New-Member Onboarding Audit Findings

No Create Task actions were found in the published onboarding workflows during the original 17 July 2026 audit:

- `3.0 New Member`
- `Membership Agreement Form: Email`
- `Membership: First 7 Days`
- `Test - First 7 Days` (retired after audit)
- `3.1. New Personal Training Client`
- `PT Agreement Form: Email`
- `Intro Session Nurture`

On 22 July, `Membership: First 7 Days` was upgraded with assigned Admin Eve and Piper Mae tasks for positive and negative member replies on Days 7, 8 and 9, plus an Admin Eve task for ambiguous replies.

On 4 August, the role boundary and operating procedure were formalised in `reference/sops/first-week-member-reply-follow-up.md`, a native Drive SOP under Team Admin Onboarding, and a standalone Retention Manager GHL course. The course is deliberately outside the numbered trainer pathway and its offer remains Draft.

The approved Piper Mae positive follow-up descriptions for Days 7, 8 and 9 require a prompt rapport call. Piper thanks the member, checks review status and can make a natural referral invitation.

Piper records and uses referral details only after a warm introduction or confirmation that the referred woman has agreed to be contacted. The call outcome, review status, referral outcome, consent source and owned next action belong in an internal GHL note under `Notes`.

All 15 Day 7–9 reply tasks now use a one-day due offset, 5:00 pm and `Skip weekends`. The three positive Piper task descriptions and timing controls were saved and read back in the published workflow on 5 August 2026.

The built-in workflow test panel cannot start at Day 7, simulate an inbound reply or force the Positive, Negative or None branch. The approved three-case run was not submitted because the available test would execute the real workflow from the beginning. Runtime branch acceptance remains pending a safe staging capability or the next genuine cases.

The published `Membership Agreement Form: Email` workflow now creates the Trainerize handoff inside its existing Fit & Flex, Strong and Fast Track branches. Each branch creates a setup task assigned to the contact's Assigned User and due in one day, followed by an Admin Eve quality-check task due in two days. The six task actions specify the exact Main Product, Class Access products, membership start date, 1-way access, Owner, location, group and Bronze/Silver mapping. They also prohibit duplicate clients and invitations.

The two temporary draft provisioning workflows were deleted after their task logic was consolidated into the agreement workflow. GHL retains them in Deleted for 30 days.

`3.0 New Member` and `3.1. New Personal Training Client` both enrol contacts into `Membership: First 7 Days`. The predecessor `Test - First 7 Days` had no trigger or active enrolments and was not linked from either live workflow; Peter confirmed it as legacy and unpublished it on 17 July 2026.

Peter confirmed that billing and payment recovery are not implemented as GHL workflows. They are therefore outside this GHL task register rather than an unaudited workflow family.

## Pipeline Workflows Folder Audit Findings

The published contents of `1. Pipeline Workflows` are now fully covered. This includes the eight workflows inside `2. Strength Assessment` and these four workflows at the folder root:

- `3.0 New Member`
- `3.1. New Personal Training Client`
- `30DNNC | Mobile Check`
- `Fitness Event Registration`

`30DNNC | Mobile Check` was upgraded on 29 July 2026. Both mirrored reply branches now contain a neutral acknowledgement, an Admin Eve notification and a persistent task assigned directly to Admin Eve. `Fitness Event Registration` remains retired.

## Peter Brown

| Trigger | When task appears | Task / required action | Status |
|---|---|---|---|
| Contact enters the Escalated Hold pipeline stage | Immediately, due in one day | Review the extended-hold request and set approval to Yes or No within 24 hours. | Live verified in `HS: Extended Hold Approval`; assigned to Peter Brown |

The owner also receives internal notifications for:

- Cancellation escalation after 48 hours without contact
- Cancellation escalation around Day 14 when no live contact has been made
- Strength Assessment no-shows and cancellations
- Strength Assessment confirmation failures
- Overdue extended-hold approvals

These are notifications, not additional GHL tasks.

## Megan

| Trigger | When task appears | Task / required action | Status |
|---|---|---|---|
| Member books a Cancellation Call after selecting the manager-call pathway | On booking; task due in seven days at 12:00 pm, weekends skipped | Run the cancellation call using the full retention and farewell-session brief. | Live verified in `MC: Other (Booked Call)`; assigned to Megan Brown |

The previously documented low-satisfaction Milestone task is not live. The form has never received a submission, its native notifications are disabled, and its specified Smart Routing workflow does not exist. Low-score follow-up remains a proposed Megan responsibility only.

## Member Lifecycle and Task-Queue Audit Findings

The 22 July live audit found:

- `Membership: First 7 Days` creates separate Admin Eve and Piper Mae tasks on classified positive and negative Day 7, Day 8 and Day 9 replies. Admin owns the written response, review-pathway state and internal handoff note. Piper makes a prompt call for both positive and negative replies; the positive call includes a review check and consent-based referral invitation when natural. Ambiguous replies create an Admin clarification task that stays open when management help is required.
- The lifecycle workflows after Day 7 do not create verified member-care tasks. Day 8–28 is an unfinished draft, Day 29–90 was unpublished on 30 July and retained as a rebuild shell, and Days 91–365 are empty drafts.
- `FUM: Assessment Education & Reassessment Journey`, formerly `Follow Up Monthy`, is a Draft redesign shell rather than a member check-in sequence. Its retained action only creates or updates a WARM opportunity in FUM, and it has zero active enrolments.
- The Milestone T-Shirt form has zero historical submissions in the available full-date check, no native notification or autoresponder, and no live workflow. Its satisfaction and retention-red-flag tasks are therefore not operating.
- The dashboard showed no pending tasks assigned to Piper Mae. Admin Eve's visible pending queue contained five tasks, including overdue hold, PT-booking and PAR-Q work. Megan Brown's visible queue contained six overdue tasks from Strength Assessment and hold-return workflows. The oldest visible tasks were dated 13 July 2026.

This does not prove the total task count beyond the dashboard's visible results, but it does prove that task completion discipline is currently a material operating risk. Adding more automated tasks without an owner review cadence would increase queue debt.

## PT Administration, Trainer Onboarding and Communications Audit Findings

The 22 July continuation found:

- `PT: Block Tracking & 13-Week Rebooking` adds the PT block tracking tag and writes PT Block Start, Trainer and Service from the first qualifying booking. It waits 10 weeks, notifies the contact owner, creates an Admin Eve rebooking task, sends Admin Eve a specific notification, waits 21 days and emails the contact owner with the business inbox copied at Week 13 before removing the tag. All wording now says 13 weeks. Final coverage is all 15 current PT calendars: Megan, Piper, Nora, Katrina and Leisa at 30, 45 and 60 minutes. General re-entry and multiple-opportunity execution are disabled.
- The Railway PT booking-continuity shadow pilot sends Admin Eve one exception-led email after its Monday 5:30 am Brisbane reconciliation. It creates no GHL task, message, appointment or database change. The existing Week 10 task remains the operational handoff during the four-report validation period.
- `Intro Session Nurture` sends a booking email and 24-hour SMS from its calendar-group trigger, but creates no current post-session, no-show or staff handoff. Its available 30-day history showed nine enrolments, including four waiting contacts. Historical completions reference an older `After Session Check In SMS` action that is absent from the current builder.
- `Send Trainer Contract` sends documents for five of seven permitted Employment Type values. The Full Time Level 3A and Full Time Level 4A branches are empty, and the None fallback creates no exception task. Unsupported candidates can reach Contract Sent and finish without a contract or exception task.
- The Trainer Portal progression gap was repaired on 24 July 2026. Courses 2–12 remain sequential; Course 12 now grants Course 13 Practical Sign-Off, ten native assignments require Megan's grading, and completion of the final `Block 10: 36 Workouts` assignment grants Course 14 Congratulations. The Course 13 template completion credential was removed.
- `Main Incoming Call Router` uses a hard-coded personal number for Nora during Admin Hours and Megan as fallback and after-hours recipient. If the final transfer is unanswered, the workflow ends without a callback task, SMS acknowledgement or assigned missed-call handoff. No workflow name matching `missed`, `voicemail` or `inbox` exists in the live register.
- Conversations had five unread messages at inspection: three unassigned, one owned by Nora Silva and one owned by Piper Mae. SLA settings are off and the Manual Actions queue was empty, so neither a response target nor breach escalation is currently operating.
- The five live 30DNNC delivery workflows had 396 active contacts and all had `Stop on response` off. Their source workflows issue notifications and tags but do not create a reply task or assign a contact owner. On 29 July 2026, the owner confirmed that nurture-email replies remain in the normal inbox process and do not need a dedicated workflow handoff.
- `2 Step Permission/Reactivation` and `War Plan` leave `Stop on response` off, extending the same inbox and sequence-suppression risk into older-lead reactivation. `RE#1 - 30DNNC & SEMINAR` no longer contributes to this live risk because it is Draft and archived.
- None of the five life-stage 30DNNC builders contains a reply, booking, member or Remove-from-Workflow branch. The corrected transition controls now remove all five sequences at Strength Assessment booking and remove those five plus Mobile Check in `3.0` and `3.1`. Nurture-email replies remain governed by the normal inbox rather than a dedicated task.

## Known Coverage Gaps

### Strength Assessment attendance exception

An exact Strength Assessment appointment still Confirmed 60 minutes after its end creates one deduplicated Admin Eve exception keyed by event ID. The task must name the assigned appointment trainer, scheduled time and precise correction required; exceptional cover delivery is corrected manually.

The appointment coach owns the first correction. Terminal status or deterministic matched feedback closes the exception; missing feedback alone must never create a No Show task or trigger the No Show workflow.

The current register does not prove whether additional tasks exist in legacy or unrelated workflows, including:

- Account setup, Trainerize access, coach assignment and onboarding-session booking
- Exact reply-pause, resume and exit rules for waitlist and reactivation sequences
- Older archived or duplicated workflows

## Decisions to Make With the Team

1. Confirm every active member contact has the correct Assigned User so coach tasks route correctly.
2. Establish a daily task-queue review and overdue escalation standard for Admin Eve, coaches and managers.
3. Decide which remaining onboarding actions require persistent staff tasks rather than SMS or in-app notifications.
4. Confirm the future owner of low-satisfaction member follow-up before building the Milestone routing workflow.

## Recommended Team Message

GHL tasks are the operating handoffs that require completion. Notifications are supporting alerts only. Each person should work from their assigned task queue, complete tasks when actioned, and raise incorrect routing immediately. Coach-owned tasks depend on the member having the correct Assigned User in GHL.
