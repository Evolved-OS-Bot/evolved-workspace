# Membership Hold System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-17 (live task-routing audit)

---

## Overview

Two parallel hold systems exist — one for **Membership (SGPT) holds** and one for **PT holds**. Both share the same pipeline, custom field group, workflows, and communications. A standard hold runs for 1–4 weeks; an extended hold runs for 5–12 weeks and requires manager approval.

The hold system is also a retention pathway offered inside the membership cancellation flow (Health/Injury and Moving/Travel reasons), meaning a contact may enter the hold pipeline directly from a cancellation form rather than via a standalone hold request.

The member journey, Stripe pause, pre-return communications, and auto-completion are automated end to end. Standard membership holds still create Admin Eve verification tasks, so the system is automated but not administration-free.

> **Bug fix 2026-07-09:** `pre_return_date` was missing from the `HS: Hold Activates` webhook body. Added `pre_return_date → {{contact.hs_prereturn_date}}` to the GHL webhook custom data. Affected contacts were reviewed and Stripe subscriptions manually corrected.

---

## Billing Policy

**All members are billed at least one week in advance.**

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

---

## Surveys (Hold Forms)

| Survey Name | ID |
|---|---|
| Membership Hold Form | `3RC2cVfVv9tX6mBOZ9bS` |
| PT Hold Form | `dXxuFDDTK6OkdvHKvurU` |
| Extended Membership Hold Form | `Q9BRXF5zpiQjDoVB1Diy` |
| Extended PT Hold Form | `bvz7PVsqRY5akgHfOHkH` |

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

`HS: PT Hold Form Submitted`, both extended-hold form-submission workflows, and `HS: Hold Activates` currently contain no Create Task actions. Any prepaid-pack or other non-subscription exception therefore requires manual review when Railway cannot find an active Stripe subscription.

The historical `PT Hold: Process` tasks were traced on 24 July 2026. The execution log for Erin Wilkinson proves that `HS: PT Hold Form Submitted` executed its former `Add An 'Admin' Task` action on 5 July at the exact creation time recorded on the task. That action has since been removed from the published builder. The nine standard PT-hold tasks and one extended PT-hold task returned by the task-title search now show completed, so they are retained history rather than an active duplicate task source.

---

## Stripe Webhook Handler

**Service:** Railway — `Billing OS` (formerly `believable-happiness`) in the `tender-comfort` project
**Endpoint:** `POST https://believable-happiness-production-9870.up.railway.app/stripe/pause-hold`
**File:** `stripe_handler/app.py` in the `Evolved-OS-Bot/evolved-workspace` GitHub repo
**Environment variable:** `STRIPE_API_KEY` (restricted key — Customers Read, Subscriptions Write only)

The handler:
1. Receives payload from GHL webhook on Pre-Hold-Start Date
2. Looks up Stripe customer by email
3. Calculates and applies overlap credit if billing period extends past hold start date
4. Pauses subscription with `behavior: void` and `resumes_at` = Pre-Return Date timestamp
5. Logs all actions

When no active Stripe subscription exists, the handler logs an alert and Admin reviews the payment pathway manually. A prepaid pack may require an access-date or booking decision, but there is no PT Minder step.

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

### Health / Injury Cancellation
When a member indicates they cannot train due to health/injury in the cancellation form, the `MC: Health/Injury` workflow presents a hold as an alternative. If accepted, they enter the Hold OS pipeline rather than continuing to the cancellation notice period.

### Moving / Travelling Cancellation
When a member indicates they are moving/travelling but may return, the `MC: Moving/Travel` workflow offers a hold. If accepted, they enter the Hold OS pipeline instead of progressing to Notice Period.

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
- Auto-completion — 3 days after return day, status → Completed, removed from pipeline
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
