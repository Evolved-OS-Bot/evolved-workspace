# Plan: Rebuild 2. Strength Assessment Workflow
**Created:** 2026-04-02
**Status:** In Progress

---

## Objective

Rebuild the `2. Strength Assessment` GHL workflow to reflect The Evolved's current sales process — Strength & Longevity Assessment as the primary conversion channel. Fix structural issues, close compliance gaps, align with the updated [WARM] Sales Pipeline, and lay the groundwork for AI enhancements.

---

## Current Issues Being Fixed

| # | Issue | Priority |
|---|---|---|
| 1 | Timeout windows are minutes — should be hours | Critical |
| 2 | No PAR-Q form sent at booking | Compliance |
| 3 | Cancellation path ends cold — no pipeline move or rebook | High |
| 4 | SA Nurture fires simultaneously with goals SMS | High |
| 5 | Previously Assessed → hard END, no personalisation | Medium |
| 6 | Goals capture via SMS is fragile | Medium |
| 7 | "No Goals" path gets worse pre-session experience | Medium |
| 8 | Two internal notifications fire separately | Low |
| 9 | Email + SMS confirmation fire together | Low |
| 10 | Pipeline stage not explicitly set at booking | High |
| 11 | Wait 1 min at start unnecessary | Low |

---

## New Workflow Structure

### TRIGGER
- Customer Booked Appointment → Strength & Longevity Assessment calendar (both round_robin and event)

---

### PRE-BRANCH STEPS

1. Wait 1 Min
2. **Remove from Mobile Check Form** — removes the contact from the Mobile Check Form workflow. This form is part of the lead intake/lead generation system and fires before booking. Removing the contact here prevents overlap between the lead intake sequence and the SA workflow. Full documentation of this form and its workflow deferred to lead generation system documentation.

---

### BRANCH A: Previously Assessed?

**YES (returning lead) path:**
1. Remove tag: `strength assessment cancelled` (if present)
2. Internal Notification: `RETURNING: {{contact.first_name}} has booked a Strength Assessment | check previous assessment notes and pre-qual data before session.`
3. Create WARM Sales Opportunity → stage: Assessment Booked
4. Find Us Email
5. SMS Booking Confirmation (returning): `Hi {{contact.first_name}}, it's great to hear from you again. You're booked in for your Strength Assessment — looking forward to it. Can you reply YES to confirm your appointment?`
6. Add to SA Nurture Workflow
7. Wait for Reply to Booking Confirmation SMS (5min timeout)
8. → Joins shared confirmation loop (SMS Confirmed → SMS Goals → pre-qual sequence)

**NO path (new lead):**
1. Create Appointment Sheet Row
2. Add tag: `strength assessment booked`
3. Create WARM Sales Opportunity → stage: Assessment Booked
4. Internal Notification: `{{contact.first_name}} has booked a Strength Assessment | check conversation before pre-qualifying`
5. Find Us Email
6. SMS Booking Confirmation → reply YES to confirm (speed-to-lead, 5min timeout)
7. Add to SA Nurture Workflow (fires immediately — parallel email channel, intentional)
8. Wait for Reply to Booking Confirmation SMS
9. SMS Confirmed → "locked in" (on reply)
10. SMS Goals (unified copy — works for new and returning):
    `Before we see you, we'd love to make sure we're across everything. What's motivated you to come in right now? And has anything changed — goals, injuries, or anything else we should know? Just reply and we'll make sure the session is built around where you're at today.`
    - **Wait for Reply (45 min timeout)**
      - **Contact Reply** → SMS Acknowledgement → (joins step 11 below)
      - **Timeout (45 min)** → SMS Goals Follow Up 1 (second prompt)
        - **Wait for Reply (45 min timeout)**
          - **Contact Reply** → SMS Acknowledgement → (joins step 11 below)
          - **Timeout (45 min)** → **Goals Deadline path** (see below)
    - **Goals Deadline / No Engagement Path:**
      → SMS Deadline Reminder → Wait for Reply (15 min timeout)
        - **Contact Reply** → loops back to SMS Acknowledgement
        - **Timeout (15 min)** → SMS Deadline → Cancel Strength Assessment appointment
          → Update Opportunity → Cancelled (Rebook 72hrs)
          → Add tag: `strength assessment cancelled`
          → END
11. Admin (Internal) Notification + PREQUALIFY task → Admin Eve (1 day due)
12. Coach (Internal) Notification + PREQUALIFY task → Contact's Assigned User (1 day due)
    - Coach assignment is automatic via calendar setting: "Assign contacts to their respective calendar team members"
13. Owner (Internal) Notification
14. Add tag: `goals submitted`
15. **[AI INTEGRATION POINT]** Webhook → fires to SA Pre-Qual AI Agent with contact ID + goals reply
    - _Until agent is live: admin + coach run manual pre-qual SOP_
16. **Wait for tag: `pre-qual complete`** (timeout: 7 days → continue without)
17. Move pipeline stage → Pre-Qualified (on tag received)

---

### PRE-SESSION SEQUENCE (shared path)

**Trigger: 2 days before appointment**
1. Check: Goals submitted? (tag: `goals submitted`)
   - **Goals submitted:**
     - SMS: Personalised pre-session reminder referencing their goals
     - Coach internal notification: goals summary brief
   - **No goals submitted:**
     - SMS: Reminder + prompt to reply with their main goal (simple, one question)
     - Wait 2 hours for reply
       - **Replied:** Capture goal → tag → SMS acknowledgement → coach notification
       - **No reply:** Generic reminder SMS (they still get a good experience)

**Trigger: 1 day before appointment**
1. SMS: READY prompt + PAR-Q form link
   - `Hi {{contact.first_name}}, your Strength Assessment is tomorrow. Are you ready? Please complete this 2-minute health form before you come in so your trainer is fully prepared: {{ custom_values.parq_form_link }}`
2. AI Summarize → source: contact conversation history → output to custom value: `SA: Conversation Summary`
3. Create Task (Contact's Assigned User): `TRAINER BRIEF — {{contact.first_name}} — session tomorrow at {{appointment.only_start_time}}: {{custom_values.sa_conversation_summary}}`
   - Auto-generated from conversation — no manual writing needed
   - When pre-qual AI agent is live, summary becomes significantly richer
4. PAR-Q automated chase sequence:
   - Wait 3 hours → Check: tag `parq complete`?
     - YES → proceed
     - NO → SMS: `Just a reminder to complete your health form before tomorrow: {{ custom_values.parq_form_link }}`
     - Wait 4 hours → Check: tag `parq complete`?
       - YES → proceed
       - NO → Create Task (Admin Eve): `Chase PAR-Q — {{contact.first_name}} hasn't completed health form, session tomorrow. Call if needed.`
   - Note: `parq complete` tag is added automatically via PAR-Q form post-submission action
5. Wait for READY reply (timeout: 4 hours)
   - **Replied:** SMS: `Perfect — see you tomorrow!`
   - **No reply:** SMS nudge: `Just checking you're still on for tomorrow — reply YES to confirm`
   - Wait 2 more hours → **Still no reply:** Internal notification to owner (manual outreach decision)

**Trigger: 1 hour before appointment**
1. SMS: How to Find Us video (ALL contacts — both paths get this)

---

### NO SHOW / CANCELLATION HANDLING

**Deadline path (goals not submitted — auto-cancel):**
Handled inline in the main workflow. Sequence: Add `strength assessment cancelled` tag → Cancel Strength Assessment → Admin Notification → #1 REBOOK task → Update Opportunity → END.
Note: tag is added **before** the cancel action so the Cancelled Rebook workflow filter works correctly.

---

**`SA: No Show Rebook` workflow** *(to be built as separate workflow)*

Trigger: Appointment Status Changed → No Show | Calendar: Strength & Longevity Assessment

```
1. Update Opportunity → [WARM] Sales Pipeline: No Show (Rebook 72hrs)
2. Add tag: strength assessment no show
3. Internal Notification → Owner: "{{contact.first_name}} no-showed their SA. Rebook SMS fires in 2 hours."
4. Internal Notification → Assigned User: same heads-up
5. Wait 2 Hours
6. SMS No Show 1
7. Wait for Reply — 24hr timeout
   Contact Reply → SMS Rebook Link → Task (Admin Eve: confirm rebooked) → END
   Timeout → SMS No Show 2
8. Wait for Reply — 24hr timeout
   Contact Reply → SMS Rebook Link → Task (Admin Eve: confirm rebooked) → END
   Timeout → Task (Admin Eve, due 1 day): "{{contact.first_name}} hasn't responded to no-show rebooks — call or close" → END
```

---

**`SA: Cancelled Rebook` workflow** *(to be built as separate workflow)*

Trigger: Appointment Status Changed → Cancelled | Calendar: Strength & Longevity Assessment
Filter: Tag `strength assessment cancelled` is NOT present (excludes deadline-path auto-cancels)

```
1. Update Opportunity → [WARM] Sales Pipeline: Cancelled (Rebook 72hrs)
2. Add tag: strength assessment cancelled
3. Internal Notification → Owner: "{{contact.first_name}} cancelled their SA."
4. Internal Notification → Assigned User: "rebook SMS fires in 1 hour"
5. Wait 1 Hour
6. SMS Cancelled 1
7. Wait for Reply — 24hr timeout
   Contact Reply → SMS Rebook Link → Task (Admin Eve: confirm rebooked) → END
   Timeout → SMS Cancelled 2
8. Wait for Reply — 24hr timeout
   Contact Reply → SMS Rebook Link → Task (Admin Eve: confirm rebooked) → END
   Timeout → Task (Admin Eve, due 1 day): "{{contact.first_name}} cancelled SA and hasn't responded — call or close" → END
```

---

### POST-SESSION (show)

**Lives in a separate workflow: `3. Post Assessment`** — not in this workflow. Strength Assessment workflow ends at How to Find Us SMS.

**Trigger:** Appointment status = Showed / Completed

```
Wait 2 hours (buffer for in-person close / immediate follow-up)
→ Check: tag = member OR won?
  YES → END (new member workflow handles)
  NO  → Add tag: no sale
       → Move pipeline → Show (24hr Decision)
       → Enrol in Post Assessment nurture sequence
       → Create Task (Contact's Assigned User): "Follow up {{contact.first_name}} — 24hr decision window open"
```

Time-based logic preferred over manual `no sale` tagging — reduces reliance on coach/admin remembering to tag. Anyone who signs within 2hrs of session completion is captured on the tag check.

**Status:** To be built as separate plan — `3. Post Assessment` workflow.

---

## Build Order

| Step | Task | Status |
|---|---|---|
| 1 | Agree on workflow structure with Peter | ✅ Done |
| 2 | Fix timeout windows in existing workflow | ✅ Done — 5min / 45min / 15min |
| 3 | Update SMS copy with first name + clean text | ✅ Done |
| 4 | Move PAR-Q to 24hr READY prompt — remove from booking sequence | ✅ Decided |
| 5 | Fix pipeline stage assignment at booking | ✅ Done — Assessment Booked stage confirmed, value $500 |
| 6 | Fix cancellation/no-show paths → pipeline move | ✅ Done — Cancelled (Rebook 72hrs) + cancel: assessment tag |
| 7 | Update SMS Goals — keep as is, health bullets serve manual pre-qual | ✅ Decided — no change |
| 8 | Decouple SA Nurture from goals SMS | ✅ Decided — keep SA Nurture at booking confirmation. Emails are separate channel, parallel run is intentional. Every booked contact gets 4 trust-building touchpoints regardless of outcome. Gap: None demographic branch hits END — untagged contacts get no nurture. |
| 9 | Build returning lead (Previously Assessed) path | ✅ Done — Remove SA Cancelled tag, Create Opportunity, Find Us Email, returning SMS, SA Nurture, joins shared confirmation loop. Internal notification flags as returning. |
| 10 | Internal notifications + tasks | ✅ Done — Admin task → Admin Eve. Coach task → Contact's Assigned User (calendar auto-assigns coach). Owner SMS notification kept. Coach (Internal) Notification kept. All tools used intentionally. |
| 11 | Build 24hr READY prompt + PAR-Q send step | ✅ Done — PAR-Q link in both Reminder/Confirmation SMS steps. PAR-Q chase automated (tag-based, 3hr + 4hr checks, escalates to admin task only if needed). `parq complete` tag set via form post-submission action. |
| 12 | AI Summarize — deferred | ✅ Decided — AI Summarize removed until pre-qual AI agent is built. GHL native AI (GPT-3.5 tier) lacks conversation quality needed for nuanced pre-qual. Claude webhook chosen for pre-qual agent: better reasoning, structured script execution, medical/injury branching. Trade-off: native field write-back requires API build. SA: Conversation Summary custom value exists (ID: c8Utnc7JjfCDeZlUNvgK) ready for when agent is live. |
| 13 | Pre-session reminder sequence simplified | ✅ Done — removed Goals/No Goals conditional, single Reminder/Confirmation SMS to all. READY reply path → Wait 1hr → How to Find Us → END. No Reply path → nudge → 2hr wait → escalate to tasks/notifications → Wait 1hr → How to Find Us → END. Go To on late reply loops back to READY path. |
| 14 | 2. Strength Assessment workflow — structurally complete | ✅ Done |
| 15 | Build SA: PAR-Q Received (2.1 PARQ Complete) workflow | ✅ Done — Trigger: PAR-Q form submitted → Add tag `parq complete` → Admin task (Admin Eve): write pre-qual summary to contact field → Admin internal notification → Wait 2hrs → Coach task (Assigned User): check Pre-qual Summary field → Coach internal notification. Pre-qual Summary custom field created (ID: j5eRYc16qSm49xE8VOx3, key: contact.prequal_summary) in 2. Strength Assessment folder. |
| 16 | Post-session Show path → separate workflow `3. Post Assessment` | ✅ Decided — not building. `2.4 Consultation Feedback Complete` is the authoritative trigger for no-sale follow-up (form-driven, consultant has the outcome). Time-based backstop adds complexity without meaningful coverage gain. Trust consultant to complete feedback form. |
| 17 | Build No Show rebook sequence | ✅ Done — `2.2 SA: No Show Rebook` built and published. Final timeout: Abandoned Opportunity → Remove Opportunity → END |
| 18 | Build Cancelled rebook sequence | ✅ Done — `2.3 SA: Cancelled Rebook` built and published. Filter blocks deadline-path auto-cancels (tag present → END). Final timeout: Update Opportunity → FUM → END |
| 19 | Add webhook step + wait for `pre-qual complete` tag (AI integration point) | ⬜ Blocked — depends on Pre-Qual AI Agent service being live first. Wire in as final step of that build. |
| 20 | Pre-qualification AI agent — see separate plan: `2026-04-02-sa-prequalification-ai-agent.md` | ⬜ Future |
| 21 | Create consultation feedback fields in `2. Strength Assessment` folder | ✅ Done — 12 fields: SA: Sales Outcome (SINGLE_OPTIONS), SA: Main Objection (TEXT), SA: Secondary Objection 1-3 (TEXT), SA: Discovery, SA: Qualification, SA: Presentation Fit, SA: Objection Handling, SA: The Ask (all SINGLE_OPTIONS: Yes/Partially/No) |
| 22 | Build SA consultation feedback form | ✅ Done — Form ID: `Z83KtjAPMclhe8bsFJwS`. 3 sections: Who did you assess (First Name, Last Name, Email), What was the result (Sales Outcome, Main Objection, Secondary Objection 1), How did they perform (benchmarks), How did you go (Discovery, Qualification, Presentation Fit, Objection Handling, The Ask, Help Needed). Workflow sends pre-filled link: `?email={{contact.email}}&first_name={{contact.first_name}}&last_name={{contact.last_name}}` |
| 23 | Add consultation feedback steps to end of `2. Strength Assessment` workflow | ✅ Done — after "How to Find Us Video SMS": Wait 2hr 15min → Consultant Feedback Form SMS ({{appointment.user.phone}}) + Task → Wait 2hrs → Check SA: Sales Outcome → Filled: END / Not Filled: Reminder SMS + Admin Chase Task → END. Form URL: https://links.theevolvedgym.com.au/widget/form/Z83KtjAPMclhe8bsFJwS |
| 24 | Build `SA: Consultation Feedback Received` workflow | ✅ Done — `2.4 Consultation Feedback Complete`. Trigger: SA: Coach Consultation Feedback form submitted → Append row to Consultant Performance sheet → If SA: Sales Outcome = Sale → END / No Sale → Add `no sale` tag → Enrol in `2.3 No Sale - Follow Up` → END |
| 24b | Document `2.5 No Sale - Follow Up` workflow (V1) | ✅ Done — see workflow structure below |
| 25 | Add two tabs to Blog Topic Queue Google Sheet — Pre-Qual Insights and Objections Log | ✅ Done — tabs created via API with headers. Sheet ID: `1HU1O_U547pTLgA2977YPpNcVcxOdrujamUVWCwOU_Sw` |
| 26 | Add No Sale branch in `2.4 Consultation Feedback Complete` → append row to Objections Log | ✅ Done — Create Spreadsheet Row action on No Sale branch: Date, First Name, Life Stage (`{{contact.lead_life_stage}}`), Main Objection (`{{contact.sa_main_objection}}`), Secondary Objection 1 (`{{contact.sa_secondary_objection_1}}`). Secondary Objection 2 column reserved but not used yet. |
| 27 | Build GHL workflow triggered by `goals submitted` tag → append row to Pre-Qual Insights tab | ⬜ Deferred — raw SMS reply is unstructured. Build when pre-qual AI agent is live to capture structured field data. |

---

### `2.5 No Sale - Follow Up` workflow (V1)

**Trigger:** Enrolled by `2.4 Consultation Feedback Complete` → No Sale branch (SA: Sales Outcome ≠ Sale)

```
1. Remove from 'SA: Nurture' Workflow
2. #1 Lookup Spreadsheet Row (Appointments sheet — find contact row by email/name)
3. #2 Update Spreadsheet Row using Lookup (write outcome to Appointments sheet)
4. Create Or Update Opportunity → [WARM] Sales Pipeline: Show (24hr Decision)
5. Wait 5 Mins
6. NSFU #D1 Email
7. Wait 1 Day
8. NSFU #D2 Email
9. Wait 1 Day
10. NSFU #D3 Email
11. Wait 1 Day
12. NSFU #D4 Email
13. Wait 4 Days
14. Update Opportunity → FUM
15. END
```

**Email sequence:** 4 emails over ~7 days (D1 immediate, D2 +1d, D3 +2d, D4 +3d), then cold at FUM after 4 more days.

**Note:** Trigger is enrollment from `2.4 Consultation Feedback Complete` — not a tag trigger. The original `2.3 No Sale - Follow Up` has been superseded by this workflow (now `2.5`).

---

## SMS Copy

- [x] Booking confirmation SMS
- [x] SMS Confirmed
- [x] SMS Goals — unified (new + returning)
- [x] Returning lead confirmation SMS
- [x] 24hr READY prompt + PAR-Q link
- [x] 24hr nudge SMS (No Reply SMS — in workflow)
- [x] How to Find Us Video SMS (in workflow)
- [x] No Show 1 — "Hi {{contact.first_name}}, we missed you today for your Strength Assessment. Life happens — we'd love to find a time that works for you. Just reply and we'll get you sorted."
- [x] No Show 2 — "Hi {{contact.first_name}}, just checking in. We have spots available this week if you'd like to rebook — just reply and we'll lock something in."
- [x] Cancelled 1 — "Hi {{contact.first_name}}, no problem at all — your Strength Assessment has been cancelled. If you'd like to find another time, just reply and we'll sort it out."
- [x] Cancelled 2 — "Hi {{contact.first_name}}, just leaving the door open — happy to find another time for your Strength Assessment whenever you're ready."
- [x] Rebook link SMS — "Perfect — here's the link to book a time that suits you: {{custom_values.strength__longevity_assessment}}. Looking forward to seeing you."
- [ ] Post-session feedback form SMS — Future (part of 3. Post Assessment workflow)
- [ ] 24hr decision follow-up SMS — Future (part of 3. Post Assessment workflow)

**SA Booking Link custom value:** `{{custom_values.strength__longevity_assessment}}` → https://theevolvedgym.com.au/strength-assessment

## Email Copy

- [x] Booking confirmation email (new lead)
- [x] Returning lead confirmation email

---

## AI Integration Points Summary

Two hooks are built into this workflow to allow the SA Pre-Qual AI Agent to plug in without requiring a workflow rebuild:

| Point | Location in workflow | What fires | What it replaces |
|---|---|---|---|
| 1 | After SMS Goals reply received | Webhook POST → agent endpoint (contact ID + reply) | Manual admin pre-qual conversation |
| 2 | PAR-Q form submission (2.1 PARQ Complete workflow) | Webhook POST → agent generates richer trainer brief + writes SA: custom fields | Admin manual summary task (interim until agent is live) |

**Tag contract — workflow branches on these:**
- `pre-qual complete` — added by AI agent on conversation completion. Workflow waits on this (7-day timeout → continues without).
- `pre-qual skipped` — added manually if pre-qual done by phone or in person.

**Custom values the agent writes to (must exist in GHL before agent goes live):**
See `plans/2026-04-02-sa-prequalification-ai-agent.md` for full field list and IDs.

**Until agent is live:** admin runs manual pre-qual SOP, then adds `pre-qual complete` tag manually to release the workflow.

---

## Notes

- Both SA calendars (round_robin + event) should be triggers
- Calendar setting enabled: "Assign contacts to their respective calendar team members" — coach auto-assigned at booking
- PAR-Q `parq complete` tag: must be configured in GHL Forms → PAR-Q → post-submission action
- AI Summarize output custom value: `SA: Conversation Summary` — must be created before step 12
- Post-session logic moved to separate `3. Post Assessment` workflow (to be planned separately)
- GHL AI Actions (AI Summarize, AI Intent Detection) are Crown/premium tier — confirm subscription covers these
- PAR-Q form ID: `tUmSYWgC90QLMHycVotC`
- [WARM] Sales Pipeline ID: `JBVLybtIPZRIfjhzl5KV`
- Stages (all in [WARM] Sales Pipeline — LT Pipeline no longer exists):
  - Assessment Booked: `c419912e-6e51-4e83-8820-6700d12ae971`
  - No Show (Rebook 72hrs): `e66774c3-5ee8-4924-8802-33a1fd6d6216`
  - Cancelled (Rebook 72hrs): `d31d88cb-fd7d-48c5-ad79-68faf382c897`
  - Show (24hr Decision): `0aba395d-2ac7-45bc-96e1-410fbeb114c2`
