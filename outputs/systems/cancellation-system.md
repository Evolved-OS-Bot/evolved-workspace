# Cancellation System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-23 (trainer-field option lists reconciled)

---

## Overview

Two parallel cancellation systems exist — one for **SGPT/Membership cancellations** and one for **PT cancellations**. Both share the same pipeline but have separate forms, workflows, and custom fields. The membership cancellation system is the more sophisticated of the two, with 8 reason-specific branching paths and active retention offers built into the form itself.

---

## Pipeline: Cancellation OS
**Pipeline ID:** `Tl3wKQfNYnAlcgWpORMD`

| Position | Stage | ID |
|---|---|---|
| 0 | Cancellation Form Sent | `92170a18-71b5-4d16-8ef7-a9a90001303e` |
| 1 | Cancellation Form Received | `afcceae1-be81-4402-a15a-470bde16e686` |
| 2 | Notice Period (Current) | `4f133549-260c-4bb4-bbb6-3b913b185e1b` |
| 3 | Notice Period (Ended) | `7712b6ed-d860-40a7-90a5-8600679dd90c` |
| 4 | Cancelled Member | `03e01d68-a44c-429f-8770-ce4f72fa33ca` |

Both membership and PT cancellations move through this shared pipeline. `CS: Cancellation Type` (Membership / PT) distinguishes the two.

---

## Tags

| Tag | Purpose |
|---|---|
| `cancel` | General cancellation flag |
| `cancel: membership` | SGPT/Membership cancellation |
| `cancel: pt` | PT cancellation |
| `apt cancelled` | Appointment cancellation (separate use case) |

---

## Calendar

| Calendar | Type | ID |
|---|---|---|
| Cancellation Call | personal | `m6c4nbR0D4IpF64i6zXm` |

Used in the `MC: Other` pathway when a manager call is requested.

---

---

# Retention Economics

**Last updated:** 2026-07-09 — based on 10 lifetime cancellations reviewed.

| Metric | Value |
|---|---|
| Cancellations reviewed | 10 |
| Total revenue across all 10 | $26,775 |
| Average lifetime value (LTV) | $2,677 |

Every member retained by the reason workflows is worth ~$2,677 in already-demonstrated LTV — and likely more in future tenure if the underlying issue is resolved. At $99/week, the average cancelling member represents ~27 weeks of membership. Even a 30-day hold or a schedule adjustment that keeps one member is worth more than any offer cost.

This data should inform how assertively retention offers are positioned across the eight reason workflows and the separate booked-call pathway.

---

# PART 1: Membership (SGPT) Cancellation

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Send Membership Cancellation Form | **published** | `f203b01c-f7d3-486a-baf7-8981cdeda13a` |
| Membership Cancellation Form Received | **published** | `73345f90-6ca8-444c-a694-8d1b25cdfdc6` |
| MC: Financial | **published** | `cf2d159c-2704-4865-8611-d36fbddd01a7` |
| MC: Health/Injury | **published** | `df73b324-e02b-4961-b017-4c2a9f235dbb` |
| MC: Moving/Travel | **published** | `93997227-0272-4aa0-a0ec-da56938f3901` |
| MC: New Gym | **published** | `4300ef4f-7ba6-4ac2-b603-5cc45e2df495` |
| MC: New Style | **published** | `49275845-d251-4847-9254-b08a976963b4` |
| MC: Other | **published** | `4f9ec2c2-4d59-4c69-8a51-2ec3b9eccc9b` |
| MC: Other (Booked Call) | **published** | `62c34799-0de4-4281-b5e3-bab95ae70eb9` |
| MC: Results/Value | **published** | `bc2fc64e-f02c-49f9-bc60-7434fbea1588` |
| MC: Schedule/Time | **published** | `0a999c4e-2951-4670-974f-632969c37b56` |

> **Note:** All 8 `MC:` reason workflows published 2026-07-15. Build guide and confirmed merge tags at `outputs/systems/mc-reason-workflows-build-guide.md`.

---

## Form

**Membership Cancellation Form**
**Form ID:** `dzD9sXZC1CR80MRiHgB7`

---

## Cancellation Flow (Step by Step)

```
1. Trigger → "Send Membership Cancellation Form" workflow fires
2. Contact moves to pipeline stage: Cancellation Form Sent
3. Member receives form link
4. Member completes form → selects MC: Reason
5. "Membership Cancellation Form Received" workflow fires
6. Hold Check — if HS: Hold Status is Pending Hold or On Hold:
   → Owner SMS (hold conflict alert) + Cancellation Declined Email → END
7. Cancellation Status: None path continues:
   → Update Cancellation Type → Update Cancellation Status → Add to Cancellation OS Pipeline
   → Update Date Submitted Field → Update Notice End Date +30 Days
   → Admin Notification Email → Owner SMS → Admin Eve task `Membership Cancellation: Process`, due in 30 days
   → Wait 5 mins
   → Webhook → Stripe (schedule cancel_at = end of last billing period within notice window)
   → Create SGPT Cancellation Spreadsheet Row
   → MC: Confirmation SMS → MC: Confirmation Email
   → Move to Notice Period (Current)
   → Wait 21 Days → Internal Notification → Wait 9 Days
   → Remove Member Opportunity → Move to Cancelled Member
   → Update Contact Type → Remove Member Tag → Add Old Member Tag → END
```

### Live Task Routing Audit: 17 July 2026

| Workflow group | Task path | Assignee | Due | Live finding |
|---|---|---|---|---|
| Eight `MC:` reason workflows | Initial retention call after the 10-minute wait | Piper Mae | 1 day at 12:00 pm, weekends skipped | Reason-specific brief. |
| Eight `MC:` reason workflows | Farewell-session check around Day 5 | Piper Mae | 2 days, weekends skipped | Book the complimentary 30-minute session if it was not secured on the retention call. |
| Eight `MC:` reason workflows | Mid-notice call after no reply | Piper Mae | 1 day, weekends skipped | Attendance and re-offer guidance varies by reason. |
| `MC: Other (Booked Call)` | Cancellation Call calendar booking | Megan Brown | 7 days at 12:00 pm, weekends skipped | Full cancellation-call task; owner receives a separate internal notification. |
| `Membership Cancellation Form Recieved` | Accepted membership cancellation | Admin Eve | 30 days | `Membership Cancellation: Process`, populated with reason and notice dates. |
| `PT Cancellation Form Received` | Accepted PT cancellation | Admin Eve | 1 day | `PT Cancellation: Process`; verifies Stripe and the final payment date, determines the final service week, and removes later PT bookings. |

The eight reason workflows and the separate booked-call workflow are all published. The manager-call task is assigned to Megan Brown, not Piper or a joint owner assignment.

The cancellation-processing due dates are intentionally different. The membership task is a 30-day notice-period reconciliation; the PT task is a one-day operational check because payment timing determines which future PT sessions must be retained or deleted.

---

## Cancellation Reasons & Retention Pathways

### Primary Reason Field
**CS: Reason** `contact.why_are_you_cancelling_your_membership_to` | RADIO | ID: `RJOCnTuiC7g5cewSPwzW`

Options:
- Moving away or travelling long term
- Schedule and life commitments
- Financial reasons
- Health, injury, surgery or pregnancy
- Not seeing the results or value I expected
- Training elsewhere or consolidating memberships
- Prefer a different training style or environment
- Other

---

### Reason 1: Moving / Travelling
**Workflow:** MC: Moving/Travel

| Field | Type | Options |
|---|---|---|
| CS: Moving/Travelling - Returning | RADIO | Yes / No / Unsure |
| CS: Moving/Travelling Start Date | DATE | — |
| CS: Moving/Travelling - Prefer to Cancel | RADIO | No, I prefer to cancel |

**Retention offer:** Hold option presented if returning. If not returning → notice period initiated.

---

### Reason 2: Schedule / Time
**Workflow:** MC: Schedule/Time

| Field | Type | Options |
|---|---|---|
| CS: Schedule/Time - Main Obstacle | CHECKBOX | Work hours, Kids/family schedule, Travel time to gym, Unpredictable routine, Energy levels after work, Struggle getting up early, Other |
| CS: Schedule/Time - Preferred Timeslots | CHECKBOX | Early morning (5-6am), Morning (7-9am), Midday (10am-1pm), Afternoon (1-4pm), Early evening (4-6pm), Later evening (6-8pm), Saturday, Sunday, None of the above |
| CS: Schedule/Time - Flexible Option | RADIO | Yes — 1:1 PT / Yes — hybrid PT + gym / Yes — online only / No, cancel |
| CS: Schedule/Time - PT Interest | RADIO | No thanks, continue with cancellation |
| CS: Schedule/Time - Online Only Continue | RADIO | No, please continue with my cancellation |
| CS: Schedule/Time - Hybrid Continue Can | RADIO | No, I'd still prefer to cancel |

**Retention offers:** 1:1 PT upgrade, hybrid plan, or online-only membership.

---

### Reason 3: Financial
**Workflow:** MC: Financial

| Field | Type | Options |
|---|---|---|
| CS: Financial - Pressure Duration | RADIO | Short-term (up to 12 weeks) / Long-term (up to 12 months) / Unsure (Indefinite) |
| CS: Financial Relief - Weeks | SINGLE_OPTIONS | 1–12 weeks |
| CS: Financial - Relief Preference | RADIO | No, I still need to cancel for now |

**Retention offer:** Financial relief (fee waiver) for 1–12 weeks based on pressure duration.

---

### Reason 4: Health / Injury
**Workflow:** MC: Health/Injury

| Field | Type | Options |
|---|---|---|
| CS: Health - Impact Level | RADIO | Can't train at all / Can still do some exercises / Not sure / Not preventing training |
| CS: Health - Description | LARGE_TEXT | — |
| CS: Health - Professional Advice | RADIO | Yes / No / Not Applicable |
| CS: Health - Hold | RADIO | No, I'd like to continue with the cancellation |
| CS: Health - Work Around - Continue Can | RADIO | No, I still want to continue with my cancellation |

**Retention offer:** Membership hold presented as alternative to cancellation.

---

### Reason 5: Results / Value
**Workflow:** MC: Results/Value

| Field | Type | Options |
|---|---|---|
| CS: Results/Value - Training Duration | RADIO | Less than 6 weeks / 6-12 weeks / 3-6 months / 6-12 months / More than 12 months |
| CS: Results/Value - Expected Outcome | LARGE_TEXT | — |
| CS: Results/Value - Missing Element | RADIO | More guidance/clarity, More accountability, More personalised adjustments, Struggled with consistency, Expected faster results, Program didn't feel right, Not sure |
| CS: Results/Value - Struggles Communicated | RADIO | Yes / No |
| CS: Results/Value - Coach Contacted | SINGLE_OPTIONS | Megan / Piper / Nora / Katrina / Leisa |
| CS: Results/Value - Reset | RADIO | Yes, I'd like a fresh plan / No, continue cancellation |
| CS: Metabolic Interest - Continue Cancel | RADIO | No, please continue with my cancellation |
| CS: - PT Interest | RADIO | No, I prefer to continue with the cancellation |
| CS: PT Package Offer - Declined | RADIO | I've paid for the Reset & I'm ready to continue with my cancellation / No thanks |

**Retention offers:** Results Reset (fresh program/direction) and PT package upgrade. The former Metabolic Blueprint offer is inactive because its delivery workflow was unpublished on 17 July 2026; redesign the Results/Value branch before presenting it again.

---

### Reason 6: Training Elsewhere / New Gym
**Workflow:** MC: New Gym

| Field | Type | Options |
|---|---|---|
| CS: Elsewhere - New Gym | TEXT | — |
| CS: Elsewhere - Attraction | RADIO | More flexible times, More personalised coaching, Better fit for training style, More classes/variety, Closer to home/work, Friends/partner train there, Consolidating memberships |
| CS: Elsewhere - Missing Element | RADIO | More guidance/support, More personalised adjustments, Faster results, More consistency, More variety, Progression clarity, Different training environment, Recovery/relaxation facilities, Air conditioning, Not sure |

**Retention offer:** Diagnosis of what the competitor offers vs. what adjustments could be made.

---

### Reason 7: Training Style / Preference
**Workflow:** MC: New Style

| Field | Type | Options |
|---|---|---|
| CS: Style - Primary Reason | RADIO | Need more variety, More confident in classes, Faster noticeable results, Train with friends/family, More schedule flexibility, Strength felt confusing/overwhelming, Not progressing as hoped, Not sure |
| CS: Style - Attraction | RADIO | More cardio, More classes, Outdoor/bootcamp, Pilates/barre/reformer, Home/flexible training, More variety generally |
| CS: Style - Offer | RADIO | Yes, I'd like help combining styles / No, continue with cancellation |
| CS: Style/Gym - PT Interest | RADIO | Yes please, show me the offer / No, continue with cancellation |

**Retention offer:** Hybrid style coaching combining strength with preferred modalities, PT package offer.

---

### Reason 8: Other
**Workflow:** MC: Other / MC: Other (Booked Call)

| Field | Type | Options |
|---|---|---|
| CS: Other - Description | LARGE_TEXT | — |
| CS: Other - Manager Call | RADIO | Yes, I'd like a quick call / No, please continue with the cancellation |

**Retention offer:** Manager/owner call booked via Cancellation Call calendar.

---

## Administrative Fields

| Field | Type | Options / Notes |
|---|---|---|
| CS: Cancellation Status | SINGLE_OPTIONS | None / Notice Active / Cancelled |
| CS: Cancellation Type | SINGLE_OPTIONS | Membership / PT |
| CS: Date Submitted | DATE | — |
| CS: Notice End Date | DATE | — |
| CS: Final Access Date | DATE | — |
| CS: More Info | LARGE_TEXT | Free-text additional context |
| CS: I confirm that I want to cancel my membership | SIGNATURE | Consent/compliance signature |

---

---

# PART 2: PT Cancellation

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Send PT Cancellation Form | **published** | `4f09397c-a3a8-4c1b-982b-1bbcf2090459` |
| PT Cancellation Form Received | **published** | `bdd09a42-d00d-43ba-9201-d6cd0057e3ae` |

---

## Form / Survey

**PT Cancellation Form**
**Form ID:** `JnwGk9ttNxiSAuqBxuBs`

---

## PT Cancellation Flow (Step by Step)

```
1. Trigger → "Send PT Cancellation Form" workflow fires
2. Contact moves to pipeline stage: Cancellation Form Sent
3. Member receives PT cancellation form
4. Member completes form
5. "PT Cancellation Form Received" workflow fires
6. Hold Check — if HS: Hold Status is Pending Hold or On Hold:
   → Owner SMS (hold conflict alert) + Cancellation Declined Email → END
7. Cancellation Status: None path continues:
   → Update Cancellation Type → Update Cancellation Status → Add to Cancellation OS Pipeline
   → Update Date Submitted Field → Update Notice End Date +30 Days
   → Admin Notification Email → Owner SMS → Admin Eve task `PT Cancellation: Process`, due in one day
   → Wait 5 mins
   → Webhook → Stripe (schedule cancel_at = end of last billing period within notice window)
   → Create PT Cancellation Spreadsheet Row
   → CS: Confirmation SMS → MC: Confirmation Email
   → Update Opportunity - Notice Period Current
   → Wait 21 Days → Internal Notification → Wait 9 Days
   → Remove PT Opportunity → Update Opportunity - Cancelled Member
   → Update Contact Type → Remove from Workflow → Remove PT Tag → Add Old PT Client Tag → END
```

> PT cancellation does not have branching reason workflows — it follows a single linear path. No reason capture or retention offers currently in place.

### PT Cancellation Admin Processing Rule

The Stripe webhook schedules the subscription cancellation. Admin Eve must then verify the cancellation in Stripe, confirm the final payment date, and reconcile future PT appointments.

The calendar week immediately after the final payment date is the client's final PT service week. Keep sessions scheduled in that week and delete every scheduled PT session after the end of that week. If the Stripe cancellation, payment date, or session entitlement is unclear, escalate to Peter before deleting appointments.

Example: if the notice end date is Wednesday 23 July and the final payment falls on Tuesday 22 July, keep sessions from Monday 28 July to Sunday 3 August. Delete sessions scheduled from Monday 4 August onward.

---

## PT Cancellation Custom Fields

The PT cancellation uses the same `CS:` administrative fields as membership:

| Field | Type | Notes |
|---|---|---|
| CS: Cancellation Type | SINGLE_OPTIONS | Set to "PT" for PT cancellations |
| CS: Cancellation Status | SINGLE_OPTIONS | None / Notice Active / Cancelled |
| CS: Date Submitted | DATE | — |
| CS: Notice End Date | DATE | — |
| CS: Final Access Date | DATE | — |
| CS: I confirm that I want to cancel my membership | SIGNATURE | Used for PT cancellation confirmation |

---

---

# System Notes & Observations

### Stripe Automation

Both workflows fire a webhook after the 5-minute wait (once Notice End Date is written):

- **Endpoint:** `POST https://believable-happiness-production-9870.up.railway.app/stripe/cancel`
- **Handler:** `stripe_handler/app.py` on Railway — `Billing OS` service (`tender-comfort` project)
- **Status:** Live — deployed 2026-07-09. Was written but undeployed (14 commits unpushed to GitHub). All existing pipeline contacts verified: either already cancelled or correctly scheduled with `cancel_at`.
- **Logic:** Finds the last scheduled billing date within the 30-day notice period → sets Stripe `cancel_at` to the end of that billing period (last payment date + billing interval)
- **Error handling:** No Stripe customer found or no active subscription → admin alert logged and a manual exception review is required. This includes prepaid-pack clients and any other non-subscription payment pathway.

**Payload sent by GHL:**
```json
{
  "email": "{{contact.email}}",
  "notice_end_date": "{{contact.mc_notice_end_date}}",
  "contact_name": "{{contact.full_name}}",
  "cancellation_type": "{{contact.cs_cancellation_type}}"
}
```

---

### What's working well
- **Stripe cancellation fully automated** — both Membership and PT workflows schedule subscription cancellation on form submission, calculated to the correct billing period end date
- **Reason-based branching** is best-in-class — each reason has a purpose-built retention pathway rather than a generic response
- **Guided radio fields** nudge members toward retention options while still allowing them to proceed with cancellation — no pressure, just structured options
- **Signature fields** on both forms provide legal protection and reduce disputes
- **Coach assignment tracking** (`CS: Results/Value - Coach Contacted`) links cancellation context to the trainer responsible
- **Financial relief weeks** (1–12) gives fine-grained control over retention offers without blanket discounting
- **Hold conflict check** on both workflows blocks cancellation if a hold is active or pending, preventing simultaneous hold/cancel scenarios

### Current gaps / things to review
- **PT cancellation has no branching logic** — unlike membership, PT cancellations follow a single path with no reason capture or retention offers. Worth considering whether this should be expanded
- **No win-back workflow visible** — once a contact reaches "Cancelled Member" there's no visible automated re-engagement sequence. Longer-term win-back (e.g. 90 days post-cancellation) may be missing
- **Cancellation Call calendar is personal type** — may limit availability/scalability if multiple staff need to handle retention calls
