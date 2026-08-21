# Plan: Cancellation MC: Reason Workflows — GHL Build
**Created:** 2026-07-09
**Status:** In Progress

---

## Context

When a member submits the Membership Cancellation Form, they have already declined every automated retention offer built into the form. These 9 workflows run the human retention sequence in parallel with the main cancellation workflow.

**Retention coach:** Piper
**Farewell session:** 30-min 1:1 PT — booked manually by Piper into her regular PT calendar
**Farewell offer timing:** Within 7 days of form submission (workflow hits this at day 5)
**Average member LTV:** $2,677 — every save is worth it

**Full build spec:** `outputs/systems/cancellation-mc-reason-workflows.md`

---

## Shared Skeleton (all 9 workflows)

Full 30-day structure covering the entire notice period. Three waves.

```
── WAVE 1 (Days 0–5) — Initial contact ──────────────────────────────

Trigger  — Survey submitted → Membership Cancellation Form + CS: Reason filter
Step 1   — Wait 10 mins
Step 2   — Create Task: Piper (reason-specific brief — pre-call prep first, then script)
Step 3   — Internal Notification: Piper (reason-specific context)
Step 3b  — Wait 1 hour (Mon–Fri 9–5)
Step 4   — SMS to member
Step 5   — Wait 24 hours (Mon–Fri 9–5)
Step 5b  — If/Else: cs: contact made? YES → END / NO → Step 6
Step 6   — Internal Notification: Piper (call reminder)
Step 7   — Wait 24 hours (Mon–Fri 9–5)
Step 7b  — If/Else: cs: contact made? YES → END / NO → Step 8
Step 8   — Internal Notification: Piper + Owner (escalation)
Step 9   — Wait 3 days (Mon–Fri 9–5)
Step 9b  — Find Opportunity (Cancellation OS) — Not Found → END (saved)
Step 10  — If/Else: cs: contact made AND Stage = Notice Period (Current)?
            YES (contacted, still cancelling) → Steps 11a + 11b → Wave 2B
            NO (not contacted, still in period) → Wave 2A

── WAVE 1 farewell ──────────────────────────────────────────────────

Step 11a — Create Task: Piper (farewell session safety net — due 2 days)
Step 11b — SMS to member ("before anything is finalised")

── WAVE 2A (Day 14) — No contact made ──────────────────────────────

Step 12   — Wait ~9 days (to reach Day 14 from form submission)
Step 12b  — Find Opportunity — Not Found → END (saved in the meantime)
Step 12c  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 13
Step 13   — Internal Notification: Owner (14 days, no contact — owner to intervene directly)
Step 14   — SMS to member from Owner (personal, warmer tone)
Step 15   — Wait 11 days (Mon–Fri 9–5)
Step 15b  — Find Opportunity — Not Found → END
Step 15c  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 16
Step 16   — SMS to member (final — door always open) [no owner task — too late at Day 25]

── WAVE 2B (Day 14) — Contacted, still cancelling ──────────────────

Step 11c  — Wait ~9 days (to reach Day 14 from form submission)
Step 11d  — Find Opportunity — Not Found → END (saved)
Step 11e  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 11f
Step 11f  — SMS to member (mid-notice training check-in — "are you still coming in?")
Step 11g  — Wait for Reply: 2 days (Mon–Fri 9–5)
             Contact reply → 11h. Internal Notification: Piper (replied) → [Go to Step 11i]
             Time out      → 11hi. Internal Notification: Piper (no reply) → 11hii. Task: Piper (mid-notice call, due 1 day) → [Go to Step 11i]
Step 11i  — Wait 9 days (Mon–Fri 9–5) [both branches land here via Go to]
Step 11j  — Find Opportunity — Not Found → END
Step 11k  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 11l
Step 11l  — SMS to member (final — door always open)
```

**Key conventions confirmed during MC: Financial build:**
- Full name tag: `{{contact.name}}`
- All wait steps use advance window Mon–Fri 9am–5pm
- Call attempts are visible in GHL conversation log — no note-logging required in task
- `cs: contact made` tag applied by Piper on first live conversation (not on voicemail/no answer)
- Step 11a is a safety net — task copy acknowledges Piper may have already booked on the call
- Step 11b SMS uses "before anything is finalised" — not terminal language
- Re-notice period caveat: if offer accepted and they later cancel, new form + fresh 30 days applies
- Find Opportunity must precede any pipeline stage If/Else (GHL requirement)
- Wave 2A Day 14 SMS comes from Owner — 14 days of silence warrants owner-level outreach
- Wave 2A has no Day 25 owner task — too late to be worth it; workflow ends with final SMS
- Wave 2B mid-notice leads with training check-in ("still coming in?") before mentioning offers — softer, more human
- Wave 2B uses GHL native "Wait for Reply" step (11g) — two branches (Contact reply / Time out) rejoin via Go to at Step 11i
- GHL step labels: 11f=SMS, 11g=Wait for Reply, 11h=Notify Piper (reply), 11hi=Notify Piper (timeout), 11hii=Task MID-NOTICE CALL, 11i=Wait 9 Days, 11j=Find Opportunity, 11k=Opportunity check, 11l=SMS Final

**Trigger (all workflows):** Survey submitted → Membership Cancellation Form (`dzD9sXZC1CR80MRiHgB7`) + CS: Reason filter per workflow

**If/Else IDs:**
- Pipeline: `Tl3wKQfNYnAlcgWpORMD`
- Stage (Notice Period Current): `4f133549-260c-4bb4-bbb6-3b913b185e1b`

**Tag: `cs: contact made`**
Piper applies this tag manually (from GHL mobile) the moment she makes live contact with the member, regardless of outcome.

Used in three If/Else checks across all 9 workflows:
- **Before Step 6 (call reminder):** Tag does NOT exist → send reminder. Tag EXISTS → skip.
- **Before Step 8 (escalation):** Tag does NOT exist → send escalation. Tag EXISTS → skip.
- **Step 10 (farewell):** Tag EXISTS AND Pipeline Stage = Notice Period (Current) → definitely still cancelling → proceed to farewell. Either condition false → END.

---

## Tasks

### Phase 1 — Build & Test (MC: Financial first)

- [x] Open draft workflow: **MC: Financial** (`cf2d159c-2704-4865-8611-d36fbddd01a7`)
- [x] Set trigger: Survey submitted → Membership Cancellation Form, filter CS: Reason = `Financial reasons`
- [x] Build 11 steps per shared skeleton with Financial-specific content (see spec + material changes below)
- [x] Verify merge tags: confirmed `{{contact.membership_cancellation_financial__pressure_duration}}` (NOT `{{contact.cs_financial_pressure_duration}}` — spec was wrong). All other workflow merge tags need to be verified in GHL before use — spec naming convention is incorrect.
- [ ] Submit test cancellation form with Financial selected → confirm task fires to Piper, SMS sends, If/Else evaluates
- [x] Publish MC: Financial
- [x] Add Wave 2B steps to MC: Financial — built 2026-07-10. Uses GHL native "Wait for Reply" pattern. Both reply/timeout branches rejoin via Go to at Wait 9 days (Step 11j).
- [x] Add Wave 2A steps to MC: Financial — built 2026-07-10. No owner task at Day 25 — ends with final SMS.
- [ ] Submit test cancellation form with Financial selected → confirm full workflow fires correctly end-to-end
- [ ] Use MC: Financial as template for remaining 8 workflows

#### Material changes to MC: Financial Step 2 (vs. original spec)

**Offers clarified (two specific offers with action links):**
- Financial Relief Form (50% reduced rate / fee waiver) → `https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq`
- Extended Membership Hold Form (pause, no charges) → `https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy`
- Duration is not assumed — Piper asks how many weeks (max 12 for both)

**Script structure (replaces generic spec):**
1. Lead with empathy, no pressure
2. Isolate: is financial the only reason?
3. Clarify objection type: affordability vs. value
   - Value conversation: strength 1x/week > nothing; 1hr 1:1 PT = $120/session externally; option to downgrade to 30-min 1:1 PT at $60
4. Ask: "If money wasn't a factor, is this the right gym/program?" — prep with initial goal, medical notes, reason for joining
5. If yes: "We never want money to be the limiting factor" → make offer
6. Offers with ask-don't-assume framing on duration

**Re-notice period caveat added:**
If offer accepted and they later cancel: new form required, fresh 30-day notice period applies.

**Farewell session expanded:**
- Book on the spot before hanging up — within 3 days
- Session covers: mini strength assessment, progress review, 3/6/12 month gap reveal, open debrief
- Complimentary, no agenda framing

**Pre-call prep moved to top of description (before script)**

#### Material changes to MC: Financial Step 3 (vs. original spec)

- Notification reflects specific offers (50% rate / pause) not generic "fee waiver"
- Directs Piper to check the task for full pre-call prep and script
- Highlights value conversation as a required step before making offers
- Reminds Piper of re-notice period caveat to advise on call
- Reminds Piper to book farewell session on the spot if all offers declined

---

### Phase 2 — Build remaining 8 workflows

Each workflow: open draft → set trigger filter → build steps using MC: Financial as template → verify merge tags in GHL → publish.

**Important:** All merge tags listed below are from the original spec and may be incorrect. Verify each one live in GHL before use (search in merge tag selector). Do not trust spec naming convention.

- [x] **MC: Health/Injury** (`df73b324-e02b-4961-b017-4c2a9f235dbb`) — COMPLETE 2026-07-13
  - Confirmed merge tags: `{{contact.mc_health__impact_level}}`, `{{contact.membership_cancellation_health__description}}`, `{{contact.membership_cancellation_health__professional_advice}}`
  - Offers: Injury Triage Session → Standard Hold (https://theevolvedgym.com.au/hold-membership) → Extended Hold (fzIicX... survey)

- [x] **MC: Moving/Travel** (`93997227-0272-4aa0-a0ec-da56938f3901`) — COMPLETE 2026-07-13
  - Confirmed merge tags: `{{contact.membership_cancellation_movingtravelling__returning}}`, `{{contact.membership_cancellation_movingtravelling_start_date}}`
  - Offers: Temporary/Unsure → Standard or Extended Hold | Permanent → Online Only ($27/wk) or Hybrid Remote ($69/wk)

- [ ] **MC: Schedule/Time** (`0a999c4e-2951-4670-974f-632969c37b56`) — IN PROGRESS 2026-07-13
  - Step 2 built. Steps 3, 6, 11a, 11f, 11h, 11hi, 11hii, 13, 14 remaining.
  - Merge tags to verify in GHL: main obstacle, preferred timeslots
  - Offers: 1:1 PT (flexible timing), Hybrid PT + drop-in, Online coaching — match to obstacle

- [ ] **MC: Results/Value** (`bc2fc64e-f02c-49f9-bc60-7434fbea1588`)
  - Filter: CS: Reason = `Not seeing the results or value I expected`
  - Merge tags to verify: training duration, expected outcome, missing element, struggles communicated, coach contacted
  - Offers: Results Reset (fresh program + direction session with Megan), PT package upgrade
  - Note: flag to relevant coach before call if struggles weren't communicated

- [ ] **MC: New Gym** (`4300ef4f-7ba6-4ac2-b603-5cc45e2df495`)
  - Filter: CS: Reason = `Training elsewhere or consolidating memberships`
  - Merge tags to verify: new gym name, attracted by, missing element
  - Offers: Address the gap directly — use judgement on what can be matched

- [ ] **MC: New Style** (`49275845-d251-4847-9254-b08a976963b4`)
  - Filter: CS: Reason = `Prefer a different training style or environment`
  - Merge tags to verify: primary reason, attracted to
  - Offers: Hybrid coaching (strength + preferred style), 1:1 PT

- [ ] **MC: Other** (`4f9ec2c2-4d59-4c69-8a51-2ec3b9eccc9b`)
  - Filter: CS: Reason = `Other` AND CS: Other - Manager Call = `No, please continue with the cancellation`
  - Merge tags to verify: other description
  - Offers: Listen first — identify real reason on the call, match offer accordingly

- [ ] **MC: Other (Booked Call)** (`62c34799-0de4-4281-b5e3-bab95ae70eb9`)
  - Filter: CS: Reason = `Other` AND CS: Other - Manager Call = `Yes, I'd like a quick call`
  - Merge tags to verify: other description
  - Offers: Match to whatever surfaces — escalate to Megan/Peter if Piper can't resolve
  - Note: Step 4 SMS differs — acknowledges they requested the call. Step 2 task + Step 3 notification also go to Owner.

---

### Phase 3 — Final verification

- [ ] All 9 workflows published
- [ ] Update `outputs/systems/cancellation-system.md` — change MC: reason workflows status from `draft` to `published`
- [ ] Update `context/roadmap.md` — mark "Cancellation MC: Reason Workflows" as Live

---

### Phase 4 — MC: Email Nurture (separate workflow, next session)

**Architecture decision (2026-07-09):** Email sequences run in a separate workflow layer to keep the 9 reason workflows clean and independently editable.

One workflow — triggers on same form submission (Survey submitted → Membership Cancellation Form), branches by reason for email content, then shared tail.

**Email cadence during notice period:**

| Day | Email |
|---|---|
| Day 1 | Educational: muscle loss / strength importance — life-stage specific (branch on life stage tag before sending) |
| Day 4 | Social proof: member story matched to life stage + goal |
| Day 8 | Re-offer: reason-specific framing ("still time to change your mind") |
| Day 12 | "We'll miss you" — warm, no pressure, door always open |

- [ ] Map full skeleton with email briefs per reason
- [ ] Build MC: Email Nurture workflow in GHL
- [ ] Publish and test

---

### Phase 5 — MC: Post-Cancellation Follow-up (separate workflow, after Phase 4)

**Trigger:** Contact moves to Cancelled stage in Cancellation OS pipeline (`Tl3wKQfNYnAlcgWpORMD`)

| Day | Action |
|---|---|
| Day 30 | Piper internal task (check in) + email ("how's life since leaving?") |
| Day 60 | Piper internal task + email (soft re-engagement, new result/story) |
| Day 90 | Piper internal task + final email (re-join offer or close the loop) |

- [ ] Build MC: Post-Cancellation Follow-up workflow in GHL
- [ ] Publish and test
