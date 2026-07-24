# Plan: Hold Return Journey Workflow
**Created:** 2026-04-13
**Updated:** 2026-04-16
**Status:** Built — Pending Live Test
**Depends on:** `outputs/systems/membership-hold.md`

> **Superseded assumption, 24 July 2026:** PT Minder references in this historical plan are not current operating instructions. The owner confirmed that The Evolved does not use PT Minder or its remaining-pack-sessions function. Current billing evidence comes from Stripe; prepaid-pack session balances remain an unresolved operational-data gap.

---

## Objective

Complete the Hold OS automation system by building the two missing workflows that handle everything after a member enters the hold pipeline. Currently the pipeline ends at the "Returning" stage with zero automation — no return communications, no coach prompts, and no non-returner logic. This plan delivers:

1. **HS: Hold Return Journey** — date-triggered pre-return sequence, return-day actions, and a passive non-returner safety net
2. **HS: Extended Hold Approval** — pipeline-stage-triggered approval chase for extended hold requests in the Escalated Hold stage
3. **Stripe Pause Automation** — Railway webhook handler that pauses Stripe subscriptions on hold start date, calculates and credits any billing overlap, and lets Stripe auto-resume on the hold end date

---

## Key Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | **Unified workflow — not split by Membership/PT** | `HS: Hold Type` is available on every contact record. One workflow handles both hold types. Separate workflows would be duplicate maintenance with no structural benefit. |
| 2 | **No tags — use HS: Hold Status throughout** | Tags were originally planned to signal hold state, but HS: Hold Status already tracks every state (On Hold, Returning, Completed). Tags would be redundant. All conditions and smart list filters use the field instead. |
| 3 | **Assume success — auto-complete after 3 days** | There is no automated signal that a member actually returned (no session attendance integration). Rather than requiring a manual "completed" coach action, the workflow assumes return on the hold end date and auto-sets Completed after 3 days. The 7-day SMS is a passive safety net that fires regardless — it catches genuine non-returners without requiring a branch condition. |
| 4 | **Coach gets a notification, not a task** | A task adds admin overhead. A notification on return day prompts the coach to act naturally (check in, book first session). At $99/week the retention value is in the personal touch, not the process compliance. |
| 5 | **No complimentary or paid session offer** | Returning members already chose to come back — they set the return date when going on hold. Discounting a decision already made trains members to expect rewards for pausing. The coach check-in delivers the same emotional signal (you're valued) without the cost. |
| 6 | **Non-returner path ends at manual decision** | After two automated re-engagement SMS messages (7 days + 14 days), the system escalates to admin and stops. Automating a cancellation offer without human judgement is inappropriate. |
| 7 | **Extended Hold Approval triggers on pipeline stage change to Escalated Hold** | Cleaner than form submission — works regardless of whether the contact arrived via the extended hold form or the cancellation retention pathway. |
| 8 | **Stripe pause triggered on Hold Start Date, not form submission** | Members submit holds 2+ weeks in advance. Pausing immediately would block valid upcoming payments. Triggering on Hold Start Date ensures only the hold period is affected. |
| 9 | **Credit overlap rather than intercepting billing** | Member billing cycles (weekly/fortnightly/monthly) don't align with arbitrary hold start dates. Trying to intercept billing before it fires is a race condition across different cadences. Instead: pause on hold start date, calculate any days already paid but falling in the hold period, apply as a Stripe customer balance credit. Credit auto-reduces the first post-hold invoice. |
| 10 | **PT Minder holds remain manual** | No reliable API integration available. Small enough volume to process manually alongside the automated Stripe flow. |
| 11 | **One active hold at a time — enforced in workflow, not form** | GHL form-level restrictions are unreliable. Instead, the form submission workflow checks if HS: Hold Status is already Pending Hold or On Hold. If so, it blocks auto-processing, sends an admin alert, and sends the member a holding response. This prevents field overwriting and simultaneous hold abuse. |
| 12 | **HS: Pre-Return Date is a calculated field** | GHL Custom Date Reminder triggers fire ON a date, not X days before. To trigger the pre-return sequence 7 days before Hold End Date, the form submission workflow calculates Hold End Date - 7 days and saves it to a new field HS: Pre-Return Date. The Hold Return Journey triggers on this field. |
| 13 | **Pending Hold stage is preserved** | Pending Hold accurately represents the period between form submission and hold start date. The pipeline does not move to On Hold until Hold Start Date arrives (handled by HS: Hold Activates workflow). |

---

## Workflow Architecture

| Workflow | Trigger | Purpose |
|---|---|---|
| HS: Membership Hold Form Submitted *(existing — modify)* | Form submission | Cancellation check, duplicate hold block, field updates, confirmation email, calculate Hold End Date + Pre-Return Date |
| HS: PT Hold Form Submitted *(existing — modify)* | Form submission | Same as above for PT members |
| HS: Hold Activates *(new)* | Custom Date Reminder → HS: Hold Start Date | Pipeline → On Hold, Hold Status → On Hold, fire Stripe pause webhook |
| HS: Hold Return Journey *(new)* | Custom Date Reminder → HS: Pre-Return Date | Pre-return SMS sequence, return day actions, auto-complete, non-returner safety net |
| HS: Extended Hold Approval *(new)* | Pipeline Stage → Escalated Hold | Approval chase for extended holds |

---

## Build Order

| Step | Task | Status |
|---|---|---|
| 1 | Create HS: Pre-Return Date custom field in GHL | ✅ Done |
| 2 | Modify HS: Membership Hold Form Submitted workflow | ✅ Done |
| 3 | Modify HS: PT Hold Form Submitted workflow | ✅ Done |
| 4 | Build HS: Hold Activates workflow | ✅ Done |
| 5 | Build HS: Extended Hold Approval workflow | ✅ Done |
| 6 | Write all SMS messages | ✅ Done |
| 7 | Build HS: Hold Return Journey workflow | ✅ Done |
| 8 | Build Railway Stripe webhook handler | ✅ Done — live at https://believable-happiness-production-9870.up.railway.app/stripe/pause-hold |
| 9 | Test end-to-end with a live hold | ⬜ To Do |
| 10 | Update membership-hold.md documentation | ✅ Done |

---

## Step 1 — Create Calculated Date Fields in GHL

In GHL → Settings → Custom Fields → 4. Hold System group, create both:

**Field 1:**
- **Field name:** HS: Pre-Hold-Start Date
- **Type:** Date
- **Object:** Contact
- **Purpose:** Hold Start Date - 7 days. Members pay 1 week in advance — the payment covering the hold week fires ~7 days before the hold starts. Pausing on this date intercepts that payment before it fires. The Railway handler still receives the actual Hold Start Date for credit calculations on any edge-case overlap.

**Field 2:**
- **Field name:** HS: Pre-Return Date
- **Type:** Date
- **Object:** Contact
- **Purpose:** Hold End Date - 7 days. Triggers the pre-return SMS sequence at the right time.

Both fields are calculated automatically by the form submission workflow. Neither is filled in manually.

---

## Step 2 — Modify HS: Membership Hold Form Submitted

### Add at the very top (before Cancellation Check): Duplicate Hold Block

Add a new If/Else immediately after the trigger, before the existing Cancellation Check:

**Condition:** HS: Hold Status is any of `Pending Hold`, `On Hold`

- **YES path (hold already active or pending):**

  1. Internal notification to admin:
     `Hold request blocked — {{contact.first_name}} {{contact.last_name}} already has an active or pending hold (Status: {{contact.hold_status}}). New request not processed. Review manually.`

  2. Email to member:
     - Subject: `We received your hold request`
     - Body: `Hi {{contact.first_name}}, thanks for submitting your hold request. We already have an active hold on your account and can only process one at a time. Our team will be in touch to discuss your upcoming hold. The Evolved Team`

  3. END

- **NO path** → continue to existing Cancellation Check (unchanged)

### Add after existing Update Hold End Date math operations (in each hold week branch):

Add two Math Operations per branch:

**Math Operation 1 — Calculate Pre-Hold-Start Date:**
- **Action name:** Calculate Pre-Hold-Start Date
- **Select Field:** HS: Hold Start Date
- **Operator:** Subtract
- **Days:** 7
- **Save Result To:** HS: Pre-Hold-Start Date

**Math Operation 2 — Calculate Pre-Return Date:**
- **Action name:** Calculate Pre-Return Date
- **Select Field:** HS: Hold End Date
- **Operator:** Subtract
- **Days:** 7
- **Save Result To:** HS: Pre-Return Date

### Remove from each standard hold branch (1 week, 2 weeks, 3 weeks):
- Admin Notification Email ("New Standard Hold Request - Review Required")
- Add An 'Admin' Task ("Membership Hold: Process")

### Update member confirmation email (Hold Received Email):
Remove: *"Membership payments will continue as normal until your hold is officially processed. Hold requests may take up to 14 days to review and apply."*

Replace with: *"Your hold has been confirmed. Payments will automatically pause from your hold start date and resume when you return. You'll hear from us the week before your return date to get you set up for your first session back."*

### Extended Hold branch — keep as-is:
Admin notification and admin task remain for extended holds (manual approval still required).

---

## Step 3 — Modify HS: PT Hold Form Submitted

Same changes as Step 2. The duplicate hold block, Pre-Return Date calculation, removal of admin task/email for standard holds, and member email update apply equally.

---

## Step 4 — Build HS: Hold Activates Workflow

**Workflow name:** `HS: Hold Activates`

### Trigger
- **Type:** Custom Date Reminder
- **Field:** HS: Pre-Hold-Start Date
- **Time:** 7:00am
- **Filter:** HS: Hold Status = `Pending Hold` (prevents re-firing if status has been manually changed)

### Steps

**1. Update Pipeline Stage → On Hold**
- Pipeline: Hold OS
- Stage: On Hold (`7acf7470-89cd-4968-b546-ed0897ad4889`)

**2. Update HS: Hold Status → On Hold**
- Field: HS: Hold Status (`{{contact.hold_status}}`)
- Value: `On Hold`

**3. Webhook → Stripe Pause**
- Method: POST
- URL: `https://[railway-app].railway.app/stripe/pause-hold`
- Body:
```json
{
  "email": "{{contact.email}}",
  "hold_start_date": "{{contact.hf_hold_start_date}}",
  "hold_end_date": "{{contact.hf_hold_end_date}}",
  "contact_name": "{{contact.full_name}}",
  "hold_type": "{{contact.hold_type}}"
}
```

**4. END**

---

## Step 5 — Build HS: Extended Hold Approval Workflow

**Workflow name:** `HS: Extended Hold Approval`

### Trigger
- **Type:** Pipeline Stage Changed
- **Pipeline:** Hold OS (`TRRhFP3Y8NXGggNa7eDS`)
- **Stage:** Escalated Hold (`2049f2ca-fb8c-4c2f-9a5c-030b57495c8d`)

### Steps

**1. Owner Task**
- Action: Create Task
- Assigned To: Owner
- Due: 1 day
- Title: `EXTENDED HOLD REQUEST — {{contact.first_name}} {{contact.last_name}} — review and approve or reject within 24hrs`
- Notes: `Hold Type: {{contact.hold_type}} | Extended Explanation: {{contact.hf_extended_explanation}}`

**2. Owner Internal Notification**
- To: Owner
- Message: `Extended hold request from {{contact.first_name}} {{contact.last_name}}. Hold Type: {{contact.hold_type}}. Check HS: Extended Explanation field and set HS: Extended Hold Approved to Yes or No within 24 hours.`

**3. Wait 2 Days**

**4. If/Else: HS: Extended Hold Approved = Yes?**

- **YES path** → END (approval handled, staff processes hold manually)

- **NO path (not yet actioned):**

  4a. Owner Internal Notification (escalation):
  `OVERDUE — Extended hold approval for {{contact.first_name}} {{contact.last_name}} has not been actioned — 2 days have passed. Review required in Hold OS pipeline.`

  4b. Admin Task:
  - Assigned To: Admin Eve
  - Due: 1 day
  - Title: `Chase extended hold approval — {{contact.first_name}} {{contact.last_name}} — 2 days overdue`
  - Notes: `Extended hold approval not yet actioned. Contact is in Escalated Hold stage. Extended Explanation: {{contact.hf_extended_explanation}}`

  4c. END

---

## Step 6 — SMS Copy

### SMS 1: 2-Day Pre-Return

```
Hi {{contact.first_name}}, just a quick one — your hold wraps up in two days and we're looking forward to having you back.

See you soon.
```

### SMS 2: Return Day Welcome Back

```
Hi {{contact.first_name}}, welcome back — your hold ends today and we're glad to have you back at The Evolved.

Your coach will be in touch today. See you soon.
```

---

## Step 7 — Build HS: Hold Return Journey Workflow

**Workflow name:** `HS: Hold Return Journey`

### Trigger
- **Type:** Custom Date Reminder
- **Field:** HS: Pre-Return Date
- **Time:** 9:00am
- **Filter:** HS: Hold Status = `On Hold`
- **Allow re-entry:** No

### Steps

**1. Coach Task / Internal Notification**
- To: Contact's Assigned User
- Message: `{{contact.first_name}} {{contact.last_name}} returns from hold in 7 days. Check they're booked in for their first session back before you reach out.`

**2. Wait 5 Days**

**3. SMS: 2-Day Pre-Return**
- Send SMS 1

**4. Wait 2 Days**

**5. Update Pipeline Stage → Returning**
- Pipeline: Hold OS
- Stage: Returning (`b8e1fe6a-f375-4c4e-b6b4-05c0376e9f68`)

**6. Update HS: Hold Status → Returning**

**7. SMS: Welcome Back**
- Send SMS 2

**8. Internal Notification → Contact's Assigned User**
- Message: `{{contact.first_name}} {{contact.last_name}} is back from hold today. Reach out and confirm their first session back.`

**9. Coach Task**
- Assigned To: Contact's Assigned User
- Title: `{{contact.first_name}} {{contact.last_name}} is back from hold today — check in.`

**10. Internal Notification → Admin Eve**
- Message: `{{contact.first_name}} {{contact.last_name}} is back from hold today. Hold Type: {{contact.hold_type}}. Coach has been notified.`

**11. Wait 3 Days**

**12. Remove from Pipeline**

**13. Update HS: Hold Status → Completed**

**14. END**

### Design decisions
- No automated non-returner SMS sequence — coaches manage non-returners directly through their member relationships
- No cancellation pathway prompts — this is handled separately and only with human judgement
- Passive safety net removed in favour of coach ownership of return outcomes

---

## Step 8 — Build Railway Stripe Webhook Handler

**File:** `scripts/stripe_hold_pause.py` (or new Railway service — TBD based on existing bot structure)

### Endpoint

```
POST /stripe/pause-hold
```

### Payload (sent by GHL webhook action)

```json
{
  "email": "{{contact.email}}",
  "hold_start_date": "{{contact.hf_hold_start_date}}",
  "hold_end_date": "{{contact.hf_hold_end_date}}",
  "contact_name": "{{contact.full_name}}",
  "hold_type": "{{contact.hold_type}}"
}
```

### Handler Logic

```
1. Parse hold_start_date and hold_end_date from payload
2. Look up Stripe customer by email
   → If not found: log error, send internal alert to admin, return 200 (don't fail silently)
3. Get active subscription for customer
   → If no active subscription: log, alert admin
4. Get current_period_end and interval from subscription
5. Calculate overlap:
     overlap_days = max(0, (current_period_end - hold_start_date).days)
6. If overlap_days > 0:
     interval_days = 7 (weekly) / 14 (fortnightly) / 30 (monthly)
     daily_rate = subscription.amount / interval_days / 100  (amount is in pence/cents)
     credit_amount = round(overlap_days * daily_rate * 100)  (back to pence/cents)
     stripe.Customer.create_balance_transaction(
       customer_id,
       amount=-credit_amount,  (negative = credit)
       currency=subscription.currency,
       description=f"Hold overlap credit — {overlap_days} days from {hold_start_date}"
     )
7. Convert hold_end_date to Unix timestamp (resumes_at)
8. stripe.Subscription.modify(
     subscription_id,
     pause_collection={"behavior": "void", "resumes_at": resumes_at_timestamp}
   )
9. Log: contact name, hold dates, overlap days, credit applied, subscription ID
10. Return 200
```

### Environment Variables Required

Add to Railway (and local `.env`):

```
STRIPE_API_KEY=sk_live_...
```

### Error Handling

| Scenario | Behaviour |
|---|---|
| Customer not found in Stripe | Log + internal Slack/email alert to admin. Do not retry. |
| No active subscription | Log + alert. Manual intervention required. |
| Stripe API error | Return 500. GHL will retry. Log the error. |
| Hold dates missing from payload | Return 400. Log warning. |

### PT Minder members

If a member's billing is via PT Minder (no Stripe subscription), the handler will return "no active subscription" and alert admin. Admin processes the PT Minder pause manually. No further automation.

---

## Step 9 — Testing Protocol

---

## Step 9 — Testing Protocol

| Test | Steps |
|---|---|
| Duplicate hold block | Submit hold form for a contact with HS: Hold Status = Pending Hold. Confirm admin alert fires, member receives holding email, workflow ends without overwriting fields. |
| Cancellation block | Submit hold form for a contact with active cancellation status. Confirm decline email fires, Hold Status reset to None. |
| Standard hold — full automation | Submit hold form with Hold Start Date 7 days from now. Confirm: Pending Hold set, Hold End Date calculated, Pre-Return Date = Hold End Date - 7 days, no admin task created, member confirmation email sent. On Hold Start Date: confirm pipeline → On Hold, status → On Hold, Stripe pause fires. On Pre-Return Date: confirm 7-day pre-return SMS fires. Continue through return day, auto-complete, pipeline removal. |
| Hold Activates — Stripe pause | Confirm webhook fires on Hold Start Date. Check Railway logs. Confirm Stripe subscription is paused with correct resumes_at. |
| Extended Hold Approval — actioned within 2 days | Move test contact to Escalated Hold. Confirm owner task fires. Set HS: Extended Hold Approved = Yes within 2 days. Confirm clean END. |
| Extended Hold Approval — overdue | Move test contact to Escalated Hold. Do not set approval field. Wait 2 days. Confirm escalation notification and admin task fire. |
| Hold Return Journey — passive SMS net | Confirm 7-day re-engagement SMS fires at day 7 post hold end. Confirm final SMS + admin task fire at day 14. |
| Stripe — overlap credit | Set Hold Start Date = 3 days into current billing period. Confirm credit calculated and applied to customer balance in Stripe. |
| Stripe — no subscription found | Use test contact with email not in Stripe. Confirm admin alert fires, handler returns 200, workflow continues. |

---

## Step 10 — Update membership-hold.md

After workflows are built and tested, update `outputs/systems/membership-hold.md`:

1. **Workflows tables** — add `HS: Hold Return Journey` and `HS: Extended Hold Approval` with their new IDs (record after creation)
2. **System Notes — What's working well** — add return journey automation
3. **System Notes — Current gaps** — resolve: Returning→Completed undefined, no win-back logic
4. **Flow diagrams** — update Standard Hold and Extended Hold diagrams to reflect automation at Returning stage

---

## Reference: Pipeline and Field IDs

### Pipeline Stages
| Item | ID |
|---|---|
| Hold OS Pipeline | `TRRhFP3Y8NXGggNa7eDS` |
| Stage: Pending Hold | `da1a018b-8d91-44b0-b636-fc03f60656d8` |
| Stage: Escalated Hold | `2049f2ca-fb8c-4c2f-9a5c-030b57495c8d` |
| Stage: On Hold | `7acf7470-89cd-4968-b546-ed0897ad4889` |
| Stage: Returning | `b8e1fe6a-f375-4c4e-b6b4-05c0376e9f68` |

### Custom Fields (confirmed merge tags)
| Field | Merge Tag | Field ID |
|---|---|---|
| HS: Hold Request Date | `{{contact.hf_hold_request_date}}` | `DdAlYBQXPxgrLtfE9L57` |
| HS: Hold Start Date | `{{contact.hf_hold_start_date}}` | `k40qV4w0HKj5KFbMnmq8` |
| HS: Hold End Date | `{{contact.hf_hold_end_date}}` | `WOnR5XTn45YnSx9KsBGF` |
| HS: Pre-Hold-Start Date | `{{contact.hs_preholdstart_date}}` | `fbz1UvzfzqdhEPLggLhv` |
| HS: Pre-Return Date | `{{contact.hs_prereturn_date}}` | `aQS0XQcq3UYw6v5Ljtp1` |
| HS: Hold Status | `{{contact.hold_status}}` | `huVhp3xNLYJDtPA9JdFA` |
| HS: Hold Type | `{{contact.hold_type}}` | `J54g7CqeVbOHo6CoYzMA` |
| HS: Hold Reason | `{{contact.hold_reason}}` | `AQAgNHACCUmEoygFk09t` |
| HS: Hold Notes | `{{contact.hf_hold_notes}}` | `gJH5iwzbR0N6a3LUjsrT` |
| HS: Hold Weeks | `{{contact.hf_hold_weeks}}` | — |
| HS: Extended Hold Approved | `{{contact.hf_extended_hold_approved}}` | `N5nHPkwsNRHXUZh88xHR` |
| HS: Extended Explanation | `{{contact.hf_extended_explanation}}` | `K1O7kwPrzZRDqRlT9MJK` |
| HS: Extended Hold Requested | `{{contact.hf_extended_hold_requested}}` | `cfrz74CObki77ONueXcB` |
| HS: Extended Hold - Weeks | `{{contact.mc_hold__weeks}}` | `3yC0db0uh3ciZOrT7tyy` |
| HS: Signature - Hold Request Confirmation | `{{contact.eh_signature__confirmation}}` | — |

### Existing Workflows
| Workflow | ID |
|---|---|
| HS: Membership Hold Form Submitted | `ff5ef46c-f0c5-4405-831e-9a3823c40235` |
| HS: PT Hold Form Submitted | `636f1b2a-ec6b-4c8b-a3a4-e03e576e7bd2` |

---

## Notes

- **Trigger relies on HS: Hold End Date and HS: Hold Start Date being set correctly** — confirmed the existing hold form workflows write these fields. If either is blank, triggers will not fire correctly.
- **Stripe pause fires first on Hold Start Date** — the webhook action is the first step in the workflow, before any SMS. Stripe is paused before communications go out.
- **Credit is applied to Stripe customer balance** — this auto-reduces the member's first invoice after the hold ends. No manual refund or adjustment needed.
- **Stripe `pause_collection` with `behavior: void`** — invoices are voided (not created as drafts) during the hold. Stripe auto-resumes billing on `resumes_at` date.
- **PT Minder billing is manual** — the handler alerts admin when no Stripe subscription is found. Staff process PT Minder holds as before.
- **Auto-complete after 3 days assumes return** — if a member genuinely did not return, the 7-day and 14-day SMS net will catch them. Admin task at day 14 is the escalation point.
- **Passive SMS net fires for all contacts** — returners will ignore it; non-returners will respond or be escalated. This is intentional — no branch condition needed.
- **GHL date-based triggers fire at the configured time on the trigger day** — set to 9:00am so SMS messages land in business hours. Stripe webhook fires at trigger time (Hold Start Date), before Stripe's billing window.
- **Coach routing relies on Contact's Assigned User** — confirm coaches are correctly assigned to member contacts.
- **"Remove from Pipeline" on completion** — confirm the exact GHL action name in the workflow builder.
- **Four `Copy -` draft workflows exist** — do not accidentally publish these when modifying the live workflows.
- **Hold Start Date field ID** — needs to be confirmed in GHL and added to the reference table above before building the GHL trigger.
