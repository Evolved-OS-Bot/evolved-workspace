# Membership Hold System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-08-05 (Hold Return guards verified; Cate Akaveka historical hold reconciled)

---

## Overview

Two parallel hold systems exist — one for **Membership (SGPT) holds** and one for **PT holds**. Both share the same pipeline, custom field group, workflows, and communications. A standard hold runs for 1–4 weeks; an extended hold runs for 5–12 weeks and requires manager approval.

The hold system is also a retention pathway offered inside the membership cancellation flow (Health/Injury and Moving/Travel reasons), meaning a contact may enter the hold pipeline directly from a cancellation form rather than via a standalone hold request.

The member journey, Stripe pause, pre-return communications, and auto-completion are automated. The live system is not currently fail-safe: GHL can continue the member-facing pause confirmation after the Billing OS webhook has failed.

> **Bug fix 2026-07-09:** `pre_return_date` was missing from the `HS: Hold Activates` webhook body. Added `pre_return_date → {{contact.hs_prereturn_date}}` to the GHL webhook custom data. Affected contacts were reviewed and Stripe subscriptions manually corrected.

> **Open control defect 2026-07-29:** the July webhook repair did not close the exception path. `HS: Hold Activates` has continued returning `400 Missing required fields`. Live contact review found two separate failure modes: a contact with no email or usable hold fields, and overlapping hold submissions merged into one impossible record with Hold End Date before Hold Start Date. The workflow still proceeds to its member SMS after the webhook error.

Until the repair is live, Admin Eve must verify the Billing OS result and the start/end chronology before treating a hold as activated. A webhook error, missing required field, overlapping request, or end date before start date is an exception: stop the automated confirmation, preserve the original valid hold, and reconcile the member, GHL, Stripe and bookings manually.

### One-open-hold policy

A contact may have only one open hold request at a time. Open means the current hold is Pending Hold, Escalated Hold, On Hold or Returning.

This rule applies even when the requested periods do not overlap. For example, a three-week hold beginning 10 August and a separate one-week hold beginning 21 September must not be submitted or processed together. The second request may be submitted only after the first hold is complete and `HS: Hold Status` has been set to Completed.

Admin must not queue a future second hold inside the contact's active hold fields. If a member tries to submit another request early, preserve the first hold unchanged, explain the one-open-hold policy, and ask the member to resubmit after the first hold is complete.

---

## Billing Policy

**All members are billed at least one week in advance.**

For reconciliation, a normal scheduled payment funds the following service week. Stripe's displayed subscription or invoice period must not override this operating policy. For example, a payment collected on 1 May covers the 5–12 May service period, even if Stripe displays 28 April–5 May.

A late retry or manually recovered arrears payment retains the original service entitlement being recovered. Apply the one-week advance rule to the original scheduled payment date, not to the later success date.

This has direct consequences for hold automation:

- A member's billing cycle will fire up to 7 days **before** their hold start date
- Stripe must be paused on **HS: Pre-Hold-Start Date** (Hold Start Date − 7 days), not on the Hold Start Date itself
- **HS: Pre-Hold-Start Date** = when payments pause
- **HS: Pre-Return Date** = Hold End Date − 7 days = when payments resume (covers the return week)
- Any overlap (days already paid that fall within the hold period) is credited to the member's Stripe customer balance and auto-reduces their first invoice after the hold

---

## Pipeline: Hold OS
**Pipeline ID:** `TRRhFP3Y8NXGggNa7eDS`

| Position | Stage | ID |
|---|---|---|
| 0 | Pending Hold | `da1a018b-8d91-44b0-b636-fc03f60656d8` |
| 1 | Escalated Hold | `2049f2ca-fb8c-4c2f-9a5c-030b57495c8d` |
| 2 | On Hold | `7acf7470-89cd-4968-b546-ed0897ad4889` |
| 3 | Returning | `b8e1fe6a-f375-4c4e-b6b4-05c0376e9f68` |

Both membership and PT holds move through this shared pipeline. `HS: Hold Type` (Membership / PT) distinguishes the two. There is no terminal Completed stage — completion is tracked via `HS: Hold Status = Completed` after the contact exits the pipeline.

---

## Tags

No dedicated hold-specific tags. Hold state is tracked entirely through pipeline stages and `HS: Hold Status`.

The hold workflow does not remove or recreate rows in `Active SGPT`. A current
member remains on the governed active roster throughout an approved hold; GHL
hold fields and Stripe pause evidence explain the temporary service and billing
state. A missing Active SGPT row is a separate roster defect and must not be
attributed to the hold workflow.

---

## Surveys (Hold Forms)

| Survey Name | ID |
|---|---|
| Membership Hold Form | `3RC2cVfVv9tX6mBOZ9bS` |
| PT Hold Form | `dXxuFDDTK6OkdvHKvurU` |
| Extended Membership Hold Form | `Q9BRXF5zpiQjDoVB1Diy` |
| Extended PT Hold Form | `bvz7PVsqRY5akgHfOHkH` |

### Canonical hold-form presentation standard

Owner decision recorded 30 July 2026: the standard Membership Hold and PT Hold journeys are the presentation and control benchmark for the extended hold forms.

The live comparison found that all four surveys share the same basic first-page visual style. The standard forms are stronger operationally: they use a branded website wrapper, concise service-specific guidance, required reason/date/duration fields, an optional context field, and explicit automatic-approval or review wording. The extended forms currently use direct widget links, longer explanatory copy, omit the additional-context question, and do not visibly mark reason, start date or duration as required.

Extended hold parity should therefore:

1. retain the distinct extended-hold duration, approval and service rules;
2. adopt the standard form's concise layout and field order;
3. require reason, requested start date and duration;
4. add the optional `Is there anything else we should know?` field;
5. apply an approved date window and explain the review rule beside the duration field;
6. present each extended form through a branded website route with the same heading, contact and footer treatment as its standard counterpart;
7. replace the `https://www.example.com` Privacy Policy and Terms of Service links across all four hold surveys;
8. preserve current field IDs and workflow triggers where practical, then regression-test standard, extended, membership and PT submissions separately.

### Date Restriction (JS — both standard hold funnels)

Both hold funnels (`theevolvedgym.com.au/hold-membership` and `theevolvedgym.com.au/hold-pt`) have a JavaScript snippet injected in the Body Tracking Code that restricts the Hold Start Date picker:

- **Minimum:** 10 days from today
- **Maximum:** 40 days from today
- Uses `MutationObserver` targeting `td.vdpCell[data-id]` elements scoped to `data-q="hf:_hold_start_date"`

---

## Workflows

| Workflow | Type | Status | ID |
|---|---|---|---|
| HS: Membership Hold Form Submitted | Trigger: Form submission | Published | `ff5ef46c-f0c5-4405-831e-9a3823c40235` |
| HS: PT Hold Form Submitted | Trigger: Form submission | Published | `636f1b2a-ec6b-4c8b-a3a4-e03e576e7bd2` |
| HS: Extended Membership Hold Form Submitted | Trigger: Form submission | Published | `86f16393-b25c-4062-ac51-66d240bf5bfa` |
| HS: Extended PT Hold Form Submitted | Trigger: Form submission | Published | `d4603307-f977-4317-9665-02347a4cab2c` |
| HS: Hold Activates | Trigger: Custom Date Reminder → HS: Pre-Hold-Start Date | Published | `c91c012b-3204-4fc7-9bee-6a3a254469fc` |
| HS: Extended Hold Approval | Trigger: Pipeline Stage → Escalated Hold | Published | `ec6b1df8-f5a0-4e54-b7d3-d983a6d520f5` |
| HS: Hold Return Journey | Trigger: Custom Date Reminder → HS: Pre-Return Date | Published | `f6dc65cb-d5e0-4ff0-90ba-b94d832b86ab` |

> Four `Copy -` draft workflows exist for the four form submission workflows. These are inactive development copies — do not publish.

### Live Task Routing Audit: 17 July 2026

| Workflow | Task trigger | Assignee | Due | Live finding |
|---|---|---|---|---|
| `HS: Membership Hold Form Submitted` | Duplicate request while Hold Status is Pending Hold or On Hold | Admin Eve | 1 day | Follow up the member and escalate extension requests to Peter. |
| `HS: Membership Hold Form Submitted` | Applicable 1, 2, 3, or 4-week duration branch | Admin Eve | 1 day | Four equivalent `Membership Hold: Process` actions verify dates, billing pause, and Hold Status. |
| `HS: Extended Hold Approval` | Entry to Escalated Hold | Peter Brown | 1 day | Review and approve or reject the request within 24 hours. |
| `HS: Extended Hold Approval` | Approval still not actioned after two days | Admin Eve | 1 day | Chase Peter for the approval decision. |
| `HS: Hold Return Journey` | Seven days before return | Contact's Assigned User | 1 day | Check Trainerize bookings and contact the member. |
| `HS: Hold Return Journey` | Return day | Contact's Assigned User | 1 day | Confirm the member's first session back. |

All six task types above are published and live-verified. The four duration-specific processing actions make nine individual Create Task actions across the Hold OS family. Skip weekends is off for these audited hold tasks.

`HS: PT Hold Form Submitted` and both extended-hold form-submission workflows still rely on their existing admin routing. Billing exceptions are now written to the Billing OS status and error fields for review.

### Protected intake control: live 29 July 2026

All four published hold-form workflows now call `Protect Hold Intake` before their existing cancellation, duplicate-hold and date checks. Billing OS handles the unavoidable fact that GHL writes form answers before its submission workflow runs:

1. If `HS: Hold Status` is blank or Completed, Billing OS validates the request and snapshots the form answers into the protected `HS Request:` fields.
2. If the hold is Pending Hold, Escalated Hold, On Hold or Returning, Billing OS restores the protected first request over any canonical fields overwritten by the second submission.
3. The second workflow journey then reaches the existing duplicate-hold branch while the original dates, duration, reason, notes and signature remain intact.
4. If an open hold has no protected snapshot, Billing OS records an exception and does not invent replacement values.

The protected fields cover standard and extended membership and PT requests. They include start date, standard or extended weeks, reason, notes, extended explanation, extended-request flag, signature and intake status.

Live verification used a temporary GHL contact. The first request for 10 August and three weeks was accepted and snapshotted; a second request for 21 September and one week was rejected while status was Pending Hold; the original 10 August and three-week values were restored. The temporary contact was then deleted.

The historical `PT Hold: Process` tasks were traced on 24 July 2026. The execution log for Erin Wilkinson proves that `HS: PT Hold Form Submitted` executed its former `Add An 'Admin' Task` action on 5 July at the exact creation time recorded on the task. That action has since been removed from the published builder. The nine standard PT-hold tasks and one extended PT-hold task returned by the task-title search now show completed, so they are retained history rather than an active duplicate task source.

The intake guard depends on `HS: Hold Status = Completed` being a trustworthy
current-cycle terminal state. The Return Journey current-cycle guard below now
protects that assumption. An unexpected transition to Completed remains an
exception and is not automatic permission to accept another hold.

### Return Journey current-cycle guard: live 5 August 2026

The published `HS: Hold Return Journey` now fails closed before both delayed
lifecycle mutations. Each guard first resets `HS: Return Guard Status` to
`Not Checked`, preventing an unavailable webhook from inheriting an older
Passed value. After the two-day wait and before the Returning opportunity or
status writes, it calls Billing OS and continues only when the status becomes
`Passed - Returning`. After the three-day wait and before the Completed write
or opportunity removal, it calls Billing OS again and continues only when the
status becomes `Passed - Completed`. Each None branch terminates without a
member message or lifecycle write.

Billing OS reads the live contact and verifies all of the following:

1. the protected intake status is `Accepted`;
2. the protected accepted start equals the current Hold Start Date;
3. Hold End Date is after Hold Start Date;
4. Pre-Return Date equals Hold End Date minus seven days;
5. the expected lifecycle status is still `On Hold` before Returning or
   `Returning` before Completed; and
6. the guard is running on the exact Hold End Date or three days afterward.

A mismatch writes `Exception` plus the exact result and checked time, removes
the contact from every active execution of this Return Journey where GHL
accepts the removal, and creates one same-day deduplicated Admin Eve task named
`HOLD RETURN EXCEPTION: Cycle mismatch - review required`. The exception
instruction explicitly prohibits a member message or Stripe change merely
because the guard failed. Workflow re-entry remains enabled for later valid
cycles; `Allow multiple opportunities` is now disabled so one contact cannot
run concurrent executions of this workflow.

Disposable-contact verification passed the normal Returning and Completed
paths and a newer-cycle overlap mismatch. The mismatch stopped the workflow,
the exact retry retained one open Admin Eve task, and both temporary contacts
were deleted. The full Billing OS unit suite also passed 39 tests.

---

## Stripe Webhook Handler

**Service:** Railway — `Billing OS` (formerly `believable-happiness`) in the `tender-comfort` project
**Endpoint:** `POST https://believable-happiness-production-9870.up.railway.app/stripe/pause-hold`
**File:** `stripe_handler/app.py` in the `Evolved-OS-Bot/evolved-workspace` GitHub repo
**Environment variables:** `STRIPE_API_KEY`, `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_ADMIN_EVE_USER_ID`

The handler:
1. Receives payload from GHL webhook on Pre-Hold-Start Date
2. Looks up Stripe customer by email
3. Calculates and applies overlap credit if billing period extends past hold start date
4. Pauses subscription with `behavior: void` and `resumes_at` = Pre-Return Date timestamp
5. Writes Succeeded or Exception, the result, time and any error back to GHL
6. Creates a same-day `BILLING EXCEPTION: Hold - Manual action required` task assigned directly to Admin Eve when the hold cannot be completed
7. Uses idempotency keys so a retry does not duplicate a credit or pause, and an exception key so the same open error does not create duplicate tasks

When no active Stripe subscription exists, the handler writes an Exception and creates the Admin Eve task with the member, requested hold dates and exact error. `HS: Hold Activates` now sets the hold action to Processing, sends `contact_id`, email and the verified dates to Billing OS, and waits until `Billing OS: Hold Action Status = Succeeded` before sending the first pause confirmation. A failed or unresolved billing action therefore cannot produce a member message saying the hold has been arranged.

The live temporary-contact test on 29 July 2026 confirmed that the task is assigned to Admin Eve, due on the same Brisbane calendar day, contains the requested action and error, and is not duplicated when the same failed webhook is retried. The temporary contact was deleted after verification.

---

## Standard Hold Flow — Automated Journey with Admin Verification (1–4 Weeks)

```
Member submits Hold Form (Membership or PT)
      │
      ▼
HS: Membership/PT Hold Form Submitted workflow fires
      ├─ Duplicate hold block: if Hold Status = Pending Hold or On Hold → block, alert admin, notify member → END
      ├─ Cancellation check: if active cancellation → decline hold, reset Hold Status → END
      ├─ HS: Hold Type = Membership / PT
      ├─ HS: Hold Status = Pending Hold
      ├─ Pipeline → Pending Hold
      ├─ HS: Hold End Date calculated (Hold Start Date + weeks)
      ├─ HS: Pre-Hold-Start Date = Hold Start Date − 7 days
      ├─ HS: Pre-Return Date = Hold End Date − 7 days
      ├─ Admin Eve task: verify the selected hold branch, dates, billing pause, and Hold Status
      ├─ Email: Hold received (Level 1 — immediate)
      ├─ Wait 1 day
      ├─ Email: Hold approved + key dates (Level 2)
      └─ SMS: Hold approved + key dates (Level 2)
      │
      ▼
[Pre-Hold-Start Date — 7 days before hold start]
HS: Hold Activates workflow fires
      ├─ Webhook → Railway → Stripe subscription paused (resumes_at = Pre-Return Date)
      ├─ Overlap credit applied if applicable
      ├─ SMS: Payments now paused, gym access until Hold Start Date, return on Hold End Date (Level 3)
      ├─ Wait 7 days
      ├─ Pipeline → On Hold
      └─ HS: Hold Status = On Hold
      │
      ▼
[Pre-Return Date — 7 days before hold end]
HS: Hold Return Journey workflow fires
      ├─ Coach task: member returns in 7 days, check booking
      ├─ Wait 5 days
      ├─ SMS to member: see you in 2 days
      ├─ Wait 2 days
      ├─ Pipeline → Returning
      ├─ HS: Hold Status = Returning
      ├─ SMS: Welcome back (return day)
      ├─ Coach internal notification: member is back
      ├─ Coach task: check in
      ├─ Admin internal notification
      ├─ Wait 3 days
      ├─ Remove from Pipeline
      └─ HS: Hold Status = Completed
```

---

## Extended Hold Flow (5–12 Weeks)

```
Member submits Extended Hold Form (Membership or PT)
      │
      ▼
HS: Extended Membership/PT Hold Form Submitted workflow fires
      ├─ HS: Hold Type = Membership / PT
      ├─ HS: Hold Status = Escalated Hold
      ├─ Pipeline → Escalated Hold
      ├─ HS: Hold End Date calculated
      ├─ HS: Pre-Hold-Start Date = Hold Start Date − 7 days
      ├─ HS: Pre-Return Date = Hold End Date − 7 days
      ├─ Admin notification email
      ├─ Owner SMS
      └─ Hold received email to member
      │
      ▼
HS: Extended Hold Approval workflow fires (trigger: Pipeline → Escalated Hold)
      ├─ Peter Brown task: review within 24hrs
      ├─ Owner internal notification
      ├─ Wait 2 days
      └─ If/Else: HS: Extended Hold Approved = Yes?
            │
            ├─ YES:
            │    ├─ Pipeline → Pending Hold
            │    ├─ HS: Hold Status = Pending Hold
            │    ├─ Wait 1 day
            │    ├─ Email: Extended hold approved + key dates
            │    ├─ SMS: Extended hold approved + key dates
            │    └─ END → continues via HS: Hold Activates on Pre-Hold-Start Date
            │
            └─ NO (not actioned in 2 days):
                 ├─ Owner escalation notification
                 ├─ Admin Eve task: chase approval
                 └─ END
```

---

## Hold as a Cancellation Retention Pathway

The hold system intersects with the cancellation system in two scenarios:

An expression of intent to cancel in a conversation is not an accepted cancellation. Do not set cancellation fields, calculate final dates, shorten the normal booking horizon or make cancellation promises until the applicable cancellation form has been submitted.

### Health / Injury Cancellation
When a member indicates they cannot train due to health/injury in the cancellation form, the `MC: Health/Injury` workflow presents a hold as an alternative. If accepted, they enter the Hold OS pipeline rather than continuing to the cancellation notice period.

### Moving / Travelling Cancellation
When a member indicates they are moving/travelling but may return, the `MC: Moving/Travel` workflow offers a hold. If accepted, they enter the Hold OS pipeline instead of progressing to Notice Period.

---

## Extending an Existing Hold

Treat an approved extension as a reconciliation of the active hold, not as a new hold submission.

1. Preserve the original Hold Request Date, Hold Start Date and Pre-Hold-Start Date.
2. Update Hold End Date, Pre-Return Date, Hold Status, Extended Hold Requested, Extended Hold Weeks, Extended Hold Approved and Extended Explanation.
3. Keep the Hold OS opportunity in `On Hold`. If the owner has already approved the extension, do not send the contact through the Escalated Hold approval workflow merely to reproduce that approval.
4. Verify that Stripe `pause_collection` remains active, the resume date matches the revised Pre-Return Date and no invoice is left open for the approved pause.
5. Remove appointments inside the medically restricted hold window. After the return date, use the normal 13-week recurring PT booking horizon unless and until a formal cancellation is received.
6. Retain the client on `Active PT` with the contractual weekly rate. Record the pause, billing restart, return date and post-return booking horizon in the Rebook field.
7. Keep Trainerize active unless separate approved evidence requires a service-access change.
8. Create an owned task for any outstanding medical certificate or supporting evidence.
9. Verify the booking-continuity controller classifies the client as `pt_hold` and does not create a false cancellation or booking exception.
10. For clients who train with more than one trainer, name the person responsible for the pre-return check. The GHL contact owner may not be one of the scheduled trainers.

When appointments are created programmatically, suppress per-appointment notifications where supported and send one clear summary message. Verify the summary was delivered, and avoid promising any cancellation outcome that has not entered the formal cancellation workflow.

---

## Communications Summary

| Level | Trigger | Channel | Content |
|---|---|---|---|
| 1 | Form submitted (immediate) | Email | Hold received — we have your request |
| 2 | Form submitted (wait 1 day) | Email + SMS | Hold approved — payment pause and resume dates |
| 3 | Pre-Hold-Start Date (same day as Stripe pause) | SMS | Payments now paused, gym access until hold start, return date |
| 4 | Pre-Return Date (7 days before hold end) | Coach task only | Member returns in 7 days — check booking |
| 5 | Pre-Return Date + 5 days (2 days before return) | SMS | See you in two days |
| 6 | Hold End Date (return day) | SMS | Welcome back |
| Coach notification | Return day | Internal | Member is back — check in |

---

## Custom Fields

**Custom Field Group ID:** `I9yvxOR5SClRM6mhguDn`

| Field | Key | ID | Type |
|---|---|---|---|
| HS: Hold Status | `contact.hold_status` | `huVhp3xNLYJDtPA9JdFA` | SINGLE_OPTIONS |
| HS: Hold Type | `contact.hold_type` | `J54g7CqeVbOHo6CoYzMA` | SINGLE_OPTIONS |
| HS: Hold Reason | `contact.hold_reason` | `AQAgNHACCUmEoygFk09t` | RADIO |
| HS: Hold Weeks | `contact.hf_hold_weeks` | `5ehOHA3T4GgAY1tGJ5i2` | SINGLE_OPTIONS |
| HS: Hold Start Date | `contact.hf_hold_start_date` | `k40qV4w0HKj5KFbMnmq8` | DATE |
| HS: Hold End Date | `contact.hf_hold_end_date` | `WOnR5XTn45YnSx9KsBGF` | DATE |
| HS: Pre-Hold-Start Date | `contact.hs_preholdstart_date` | `fbz1UvzfzqdhEPLggLhv` | DATE |
| HS: Pre-Return Date | `contact.hs_prereturn_date` | `aQS0XQcq3UYw6v5Ljtp1` | DATE |
| HS: Hold Request Date | `contact.hf_hold_request_date` | `DdAlYBQXPxgrLtfE9L57` | DATE |
| HS: Hold Notes | `contact.hf_hold_notes` | `gJH5iwzbR0N6a3LUjsrT` | LARGE_TEXT |
| HS: Extended Hold Requested | `contact.hf_extended_hold_requested` | `cfrz74CObki77ONueXcB` | RADIO |
| HS: Extended Hold - Weeks | `contact.mc_hold__weeks` | `3yC0db0uh3ciZOrT7tyy` | SINGLE_OPTIONS |
| HS: Extended Hold Approved | `contact.hf_extended_hold_approved` | `N5nHPkwsNRHXUZh88xHR` | SINGLE_OPTIONS |
| HS: Extended Explanation | `contact.hf_extended_explanation` | `K1O7kwPrzZRDqRlT9MJK` | LARGE_TEXT |
| HS: Signature - Hold Request Confirmation | `contact.eh_signature__confirmation` | `wrf9mJ5MLMoqFjnTYIa9` | SIGNATURE |
| HS: Return Guard Status | `contact.hs_return_guard_status` | `iU6YEszKisH5GPy1znMG` | SINGLE_OPTIONS |
| HS: Return Guard Result | `contact.hs_return_guard_result` | `cobnePuTqEMDPrF8JAft` | LARGE_TEXT |
| HS: Return Guard Checked At | `contact.hs_return_guard_checked_at` | `f2hmmwxlygunRXIpGcsA` | TEXT |

### HS: Hold Status Options
`None` / `Pending Hold` / `Escalated Hold` / `On Hold` / `Returning` / `Completed`

### HS: Hold Type Options
`Membership` / `PT`

---

## System Notes

### What's automated
- Duplicate hold block — no double-processing
- Cancellation check — no holds during notice period
- Date calculations — Hold End Date, Pre-Hold-Start Date, Pre-Return Date all calculated on form submission
- Stripe pause — fires automatically on Pre-Hold-Start Date via Railway webhook handler
- Overlap credit — calculated and applied automatically
- Pre-return communications — coach task at 7 days, member SMS at 2 days
- Return day communications — member SMS + coach task + admin notification
- Auto-completion — 3 days after return day, current-cycle guard passes before status → Completed and pipeline removal
- Stale Return Journey protection — current-cycle mismatch stops the journey and creates one deduplicated Admin Eve exception task
- Extended hold approval chase — 2-day wait, escalation if not actioned

### What remains manual
- Standard membership-hold verification tasks — Admin Eve checks dates, billing pause, and Hold Status on the selected duration branch
- Prepaid-pack and other non-subscription exceptions: Admin reviews manually when Railway alerts
- Extended hold rejection — system flags but staff communicate outcome to member
- Non-returners — coaches manage directly, no automated re-engagement sequence (deliberate)

### Design decisions
- No tags — Hold Status field is source of truth throughout
- No automated non-returner sequence — coaches own return outcomes
- No cancellation pathway prompts in automation — manual human judgement only
- Passive non-returner safety net removed — coach relationships handle this
- One active hold at a time — enforced in workflow via duplicate hold block

The 3 August pipeline reconciliation found 19 open Hold OS opportunities whose canonical `HS: Hold Status` was Completed and whose start/end chronology was valid with the end date already passed. Peter explicitly approved their permanent deletion; all 19 were removed and independently verified absent. Four other opportunities still say Completed but were excluded from cleanup: one carries a future hold period and three have end dates before their start dates.

The 4 August follow-up reconciled the remaining historical Hold OS drift against canonical dates, protected intake fields, Billing OS evidence and open hold tasks. Peter explicitly approved the exact 22-record cleanup. Nineteen valid past holds were set to `HS: Hold Status = Completed`, then their opportunities were permanently deleted. Three other contacts already had Completed status, so only their stale opportunities were deleted. Every field change and deletion passed a fresh precondition and read-back check. Five same-day Admin Eve exception tasks were created and verified for Rabail Aisha, Zoya Sharfuddin, Ankitha Hakeem, Tess Raby and Cate Akaveka. The independent snapshot reduced Hold OS from 39 to 17 open opportunities: 13 correctly aligned current or future holds and four guarded exceptions with assigned Admin Eve tasks.

Rabail's billing hold was manually processed in PT Minder on 31 July 2026. The live Bronze Package (Weekly) schedule shows six consecutive $99 periods removed by The Evolved All Female Gym: 7–13 August, 14–20 August, 21–27 August, 28 August–3 September, 4–10 September and 11–17 September. PT Minder reports the next payment as 18 September 2026, and the 18–24 September period remains active. The 18 September debit is payment in advance for the week ahead and is consistent with a 20 September service return; it is not evidence that the hold ends on 18 September. The 31 July–6 August debit remains Pending and is the final pre-hold period.

Peter approved the seven-week extension on 4 August 2026. The accepted GHL cycle now reads Hold Start 7 August 2026, Hold End 20 September 2026, Pre-Hold-Start 31 July 2026 and Pre-Return 13 September 2026. `HS: Extended Hold - Weeks = 7`, `HS: Extended Hold Approved = Yes`, the original four-week structured submission is preserved in the protected `HS Request:` fields, and the intake is recorded as Accepted. Billing OS remains blank because the payment change was completed manually in PT Minder rather than by Railway/Stripe. An internal GHL note records the approval, manual PT Minder evidence and payment-in-advance interpretation. The obsolete data-exception task is complete.

The published `HS: Hold Return Journey` has Allow re-entry enabled. Its live trigger is `HS: Pre-Return Date` with `HS: Hold Status = On Hold`; after the 20 September return it waits three days, removes the Hold OS opportunity and writes `HS: Hold Status = Completed`, so the expected completion date is 23 September 2026. Rabail's older 24 July Return Journey enrolment is Finished and no older enrolment remains active. Because the corrected 31 July Pre-Hold-Start date was already past when the accepted cycle was reconciled, she must not be re-run through `HS: Hold Activates` or falsely marked as a Billing OS success. A verified Admin Eve task is due 7 August to move the Hold OS opportunity and status from Pending Hold to On Hold; this is the required activation safeguard that makes the 13 September return trigger eligible.

## Operational Case Log

### Ankitha Hakeem: 4 August 2026

Ankitha's March medical PT hold remained as a stale `Returning` Hold OS opportunity. Her later signed request on 21 May for a one-week PT hold from 22–28 June then overwrote only part of the contact record, leaving a June start date paired with the old 6 April end date and a blank operational status.

The complete investigation confirmed no GHL appointments during either historical hold window. The June pause was not applied on time: Stripe collected the $120 invoice on 23 June. On 30 June, staff created a $120 customer-balance adjustment labelled `Missed two sessions`; Stripe applied it to the 7 July invoice, reducing that invoice to $0 and delivering the promised reimbursement. The current $120 weekly subscription remains active and was not changed.

The canonical GHL record now reflects the latest completed cycle: request 21 May 2026, Hold Start 22 June, Hold End 29 June, Pre-Hold-Start 15 June, Pre-Return 22 June, PT, one week, Work Travel and `Completed`. A verified internal note records the booking and Stripe evidence. The stale Returning Hold OS opportunity was permanently deleted and independently verified absent, and the Admin Eve data-exception task was completed after read-back.

### Tess Raby: 4 August 2026

Tess submitted two membership-hold requests in succession on 22 July, before
the protected-intake control went live on 29 July. The first request was a
one-week cycle beginning 3 August: its calculated Hold End Date is 10 August,
Pre-Hold-Start Date is 27 July and Pre-Return Date is 3 August. Her conversation
also describes this as a one-week hold, while noting that she expected to be
away until 12 August. The second request was for two weeks from the end of
August. It overwrote the canonical Hold Start Date and Hold Weeks but did not
replace the first request's calculated dates, leaving the impossible live
combination of 31 August to 10 August.

Admin correctly told Tess that the second request must be resubmitted only
after the first hold is complete. The first lifecycle nevertheless progressed
to `On Hold`, its 3 August return trigger created a return-booking task, and
member messages mixed the two cycles. No GHL appointments or internal
reconciliation notes were present.

The live Return Journey review confirmed that Tess is the only active
enrolment. She entered on 3 August and is waiting at `5 Days` until 8 August at
08:04 AEST. That timing belongs to the accepted one-week cycle: the 8 August
message is two days before the 10 August return, followed by completion on 13
August. She should remain in the journey. Her canonical and protected fields
must be restored around that enrolment; the enrolment must not be removed,
advanced or restarted. The current-cycle guard should allow its later actions
only while the accepted start is 3 August, end is 10 August, Pre-Return is 3
August and the expected status is still `On Hold`.

Stripe confirms an active $99 weekly subscription. The 30 July invoice was
paid, so the payment that should have been skipped for the original one-week
hold was not paused. The live subscription is instead paused through 12 August,
which will void the 6 August invoice and resume before the 13 August billing
run. No customer-balance credit exists. This produces one skipped collection
in total if left unchanged, but it skips the return-week payment rather than
the 30 July payment required by the payment-in-advance policy. The open Admin
Eve data-exception task must remain open until the accepted cycle, Stripe
payment treatment and member-facing return date are reconciled.

On 5 August 2026, the live GHL contact was repaired with strict preconditions
and read back after the write. The canonical cycle now records Hold Start
3 August 2026, Hold End 10 August 2026, one week, Work Travel and `On Hold`.
The protected request snapshot now carries the same start, duration, reason,
extended-request answer and original signature, with
`HS Request: Intake Status = Accepted`. The existing Return Journey enrolment
and its return-booking task were left unchanged. An internal note records the
accepted cycle, the rejected later request and the separate Stripe verification
requirement. The resolved `HOLD DATA EXCEPTION` task was completed only after
the live field read-back passed.

### Cate Akaveka: 5 August 2026

Cate's historical GHL record had merged two separate hold episodes. Her March
request remained open after billing was deferred and subsequently began on 15
April. That stale lifecycle caused GHL to reject her signed 20 May travel
request as a concurrent hold, even though the first cycle had already ended.

Staff later retained Cate after a June cancellation-form submission by manually
adjusting Stripe. The authoritative billing evidence shows that the $99
payments dated 3 and 10 June were refunded; the 17 June, 24 June and 1 July
invoices were voided; and normal weekly billing resumed successfully on 8
July. Her current Strong, Fit & Flexible subscription remains active at $99
weekly and was not changed.

The live GHL contact now records the latest arrangement as a completed
five-week membership hold: request 20 May 2026, Hold Start 3 June, Hold End 8
July, Pre-Hold-Start 27 May, Pre-Return 1 July, Work Travel and `Completed`.
The contradictory standard four-week and extended eight-week values were
replaced by an approved five-week historical extended-hold record. A verified
internal note preserves the March lifecycle defect, the rejected May request
and the complete Stripe evidence. The stale open Hold OS opportunity was
permanently deleted and independently verified absent, and the Admin Eve
`HOLD DATA EXCEPTION` task was completed after the contact-field and note
read-back passed.

### Zoya Sharfuddin: 4 August 2026

Zoya's declined June request remained incorrectly open as `Pending Hold`. Her signed 14 July request for a four-week membership hold from 7 September to 5 October 2026 was consequently treated as a concurrent request and blocked. The live record merged the September start with the old 14 June end date; Stripe remained active, and the audit found no GHL bookings inside the proposed September hold.

The open `Membership Hold: Follow Up - Zoya Sharfuddin` task assigned to Admin Eve now contains the exact correction procedure. Admin must confirm that Zoya still wants the September hold, explain the erroneous duplicate-hold message, correct and read back the dates and Hold OS state, and verify eligibility for the 31 August activation and 28 September return triggers. Billing must not be paused early. If Zoya declines the hold, Admin must complete the stale lifecycle cleanly instead of leaving `Pending Hold`. The task and separate data-exception task remain open until the chosen path is verified.

### Andrea Cracknell: 30 July 2026

The owner approved Andrea's signed membership hold for 7–21 August 2026. Her form was submitted on 28 July with Work Travel selected and the note: `I am away from 3/8 to 14/8. I couldn’t select 3/8 below`.

The 14-day notice period remains the member-facing expectation and 10 days remains the hard cutoff. This was an approved inside-14-day exception, so the scheduled $99 debit on 31 July must complete before Stripe is paused so that the next payment is 21 August.

The stale February request date, end date, Returning opportunity and On Hold status were replaced by the current protected request and a Pending Hold card. The stale follow-up was completed, an Admin Eve billing task was set for 31 July, and no GHL appointments existed within 7–21 August.

The 14 August Pre-Return Date is the seven-day lifecycle and booking check only; it is not the billing resume date. Andrea may return earlier simply by attending, she does not need to contact the gym, and no member reply was sent while the owner reviewed the response.
