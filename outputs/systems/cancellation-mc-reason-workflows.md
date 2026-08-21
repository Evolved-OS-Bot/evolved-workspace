# MC: Reason Workflows — Build Spec
**The Evolved All Female Personal Training & Gym**
**Created:** 2026-07-09
**Status:** Live in GHL; contact-evidence and owner-escalation hardening published and reload-verified 2026-08-04

> **Implementation plan:** `plans/2026-07-09-cancellation-mc-reason-workflows.md` — track progress there.

---

## Context

These 9 workflows fire in parallel with the main `Membership Cancellation Form Received` workflow when a member submits their cancellation. By the time the form is submitted, the member has already declined every automated retention offer on the form. These workflows run the human retention sequence: Piper calls within 24 hours, re-offers per reason, and books a farewell 1:1 PT session as a last resort.

**Retention coach:** Piper
**Farewell session:** 30-min 1:1 PT — booked manually by Piper into her regular PT calendar
**Farewell offer timing:** Within 7 days of form submission (workflow hits this at day 5)

---

## Trigger Setup (all 9 workflows)

| Setting | Value |
|---|---|
| Trigger type | Survey submitted |
| Survey | Membership Cancellation Form (`dzD9sXZC1CR80MRiHgB7`) |
| Additional filter | CS: Reason = [specific reason value — see each workflow] |

Each workflow has the same trigger type with a different reason filter. Workflows 8 and 9 (Other) also filter on the manager call field.

---

## Shared Skeleton

All 9 workflows follow this structure spanning the full 30-day notice period. Reason-specific content slots into Steps 2 and 3. Everything else is identical across all 9.

```
── WAVE 1 (Days 0–5) — Initial contact ──────────────────────────────

Trigger  — Survey submitted → Membership Cancellation Form + CS: Reason filter
Step 1   — Wait 10 mins
Step 2   — Create Task: Piper (reason-specific brief — pre-call prep first, then script)
Step 3   — Internal Notification: Piper (reason-specific context)
Step 3b  — Wait 1 hour (Mon–Fri 9–5)
Step 4   — SMS to member
Step 5   — Wait 24 hours (Mon–Fri 9–5)
Step 5b  — If/Else: contact evidence present? YES → END / NO → Step 6
Step 6   — Internal Notification: Piper (call reminder)
Step 7   — Wait 24 hours (Mon–Fri 9–5)
Step 7b  — If/Else: contact evidence present? YES → END / NO → Step 8
Step 8   — Internal Notification: Piper + Owner (escalation)
Step 9   — Wait 3 days (Mon–Fri 9–5)
Step 9b  — Find Opportunity (Cancellation OS) — Not Found → END (saved)
Step 10  — If/Else: contact evidence present AND Stage = Notice Period (Current)?
            YES (contacted, still cancelling) → Steps 11a + 11b → Wave 2B
            NO (not contacted, still in period) → Wave 2A

── WAVE 1 farewell ──────────────────────────────────────────────────

Step 11a — Create Task: Piper (farewell session safety net — due 2 days)
Step 11b — SMS to member ("before anything is finalised")

── WAVE 2A (Day 14) — No contact made ──────────────────────────────

Step 12  — Wait ~9 days (to reach Day 14 from form submission)
Step 12b — Find Opportunity — Not Found → END (saved in the meantime)
Step 12c — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 12d
Step 12d — Final evidence gate: contact evidence present? YES → END / NO → Step 13
Step 13  — Create Task: Megan (review conversation and decide whether personal outreach is warranted)
Step 14  — Removed. No automatic member SMS may be sent in Megan's name.
Step 15  — Wait 11 days (Mon–Fri 9–5)
Step 15b — Find Opportunity — Not Found → END
Step 15c — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 16
Step 16  — SMS to member (final — door always open) [no owner task — too late at Day 25]

── WAVE 2B (Day 14) — Contacted, still cancelling ──────────────────

Step 11c  — Wait ~9 days (to reach Day 14 from form submission)
Step 11d  — Find Opportunity — Not Found → END (saved)
Step 11e  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 11f
Step 11f  — SMS to member (mid-notice training check-in — "are you still coming in?")
Step 11g  — Wait for Reply: 2 days (Mon–Fri 9–5)
             Contact reply → 11h. Internal Notification: Piper (replied) → [Go to Step 11i]
             Time out      → 11hi. Internal Notification: Piper (no reply) → 11hii. Task: Piper (mid-notice call) → [Go to Step 11i]
Step 11i  — Wait 9 days (Mon–Fri 9–5) [both branches land here via Go to]
Step 11j  — Find Opportunity — Not Found → END
Step 11k  — If/Else: Stage = Notice Period (Current)? NO → END / YES → Step 11l
Step 11l  — SMS to member (final — door always open)
```

**Contact evidence**

The compatibility tag remains `cs: contact made`, but Piper is no longer the sole writer. A separate published helper workflow applies the tag automatically when a member replies during an active cancellation notice and records `CS: Contact Evidence Source = Member Reply`. The reason workflows use the same tag in Steps 5b, 7b, 10 and the final Day-14 evidence gate.

Call attempts, ringing, voicemail and generic `Completed` call status are not proof of live contact. A call may become automatic evidence only when the native GHL trigger can prove an outbound connected call with a duration of at least 60 seconds. If that condition cannot be expressed safely, calls remain review evidence for Megan and do not write the tag automatically.

---

### Step 4 — SMS to Member (shared across all 9)

```
Hi {{contact.first_name}}, it's Piper from The Evolved. I noticed you've put through your cancellation and I wanted to reach out personally. I'll give you a call within the next 24 hours to make sure we handle everything properly.
```

### Step 6 — Piper Call Reminder (shared)

**Internal notification:**
```
CALL REMINDER — {{contact.name}}
24 hours since form submission. If you haven't reached them yet, keep calling twice daily (morning and afternoon) until you make contact.
Reason: [reason — see workflow name]
Re-offer: [re-offer — see workflow name]
```

### Step 8 — Escalation (shared)

**Internal notification to Piper + Owner:**
```
ESCALATION — {{contact.name}}
48 hours since cancellation form — no contact confirmed. Please ensure at least two call attempts have been made today. Escalating to owner visibility.
```

### Step 10 — If/Else Condition

```
Condition: Tag = cs: contact made AND Pipeline Stage = Notice Period (Current) [Pipeline: Cancellation OS]
YES branch → Steps 11a and 11b (contact made, still cancelling — proceed to farewell)
NO branch  → END (member was saved, or Piper never made contact — no farewell needed)
```

### Step 11a — Farewell Session Task (shared)

**Create Task — Assign to Piper — Due: 2 days from now:**
```
FAREWELL SESSION CHECK — {{contact.name}}

SAFETY NET — this fires automatically 5 days after cancellation form submission.

Did you book the farewell session on your retention call? If yes — ignore this task and mark it complete.

If not booked yet, do it now — this is still early in their notice period, there's time to turn this around.

Book a complimentary 30-min 1:1 PT session within the next 2 days.

PRE-SESSION PREP:
- Review their original goal and reason for joining
- Pull their strength numbers and any milestones hit
- Note any medical conditions or life stage context

SESSION OBJECTIVE:
1. Run a mini strength assessment — document their current numbers
2. Walk through their progress since joining — specific lifts, milestones, physical changes
3. Reveal the gap: where they'd be in 3, 6, and 12 months if they stayed
4. Isolate the cancellation reason again in this environment
5. Re-offer: [reason-specific re-offer — see workflow name]
6. If they recommit: notify admin immediately to reverse the cancellation in GHL and Stripe.

This session is complimentary. Book it now — don't wait for them to ask.
```

### Step 11b — Farewell Session SMS (shared)

```
Hi {{contact.first_name}}, I'd love to catch up for a complimentary 30-minute session before anything is finalised. We'll look at how far you've come, where your strength is right now, and make sure you have a clear picture of your progress. Let me know if you'd like to book one.
```

---

### Wave 2B Steps (shared across all 9)

#### Step 11f — SMS to member (mid-notice training check-in)

```
Hi {{contact.first_name}}, just checking in — are you still making it in to train? We really encourage everyone to keep coming during their notice period, no hard feelings at all — we want you to get the most out of your membership while you still have it. And if anything's changed on the financial side, the offers are still there if you'd like to chat.
```

> Note: "on the financial side" is Financial-specific. Replace with reason-appropriate language for other workflows, or make generic ("if anything's changed").

#### Step 11g — Wait for Reply (2 days · Mon–Fri 9–5)

GHL native "Wait for Reply or X Days" step. Two branches:

**Contact reply branch — 11h. Internal Notification: Piper**
```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. If anything's changed financially, the offers are still on the table:
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold Form (pause, no charges): https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
```

Then: Go to → Step 11i (Wait 9 days)

**Time out branch — 11hi. Internal Notification: Piper**
```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

Either way, if anything's changed financially, the offers are still there.
```

Then: 11hii. Task: Piper — MID-NOTICE CALL (due 1 day)
```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed financially, the offers are still there.
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold Form: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
```

Then: Go to → Step 11i (Wait 9 days)

#### Step 11i — Wait 9 days (Mon–Fri 9–5)

Both branches land here via Go to.

#### Step 11j — Find Opportunity · Cancellation OS · Most recently created
- Not Found → END
- Found → Step 11k

#### Step 11k — If/Else: Stage = Notice Period (Current)
- NO → END
- YES → Step 11l

#### Step 11l — SMS to member (final — door always open, shared)

```
Hi {{contact.first_name}}, as your membership wraps up we just wanted to say — we've genuinely loved having you here and the door is always open if you ever want to come back. Take care of yourself.
```

---

### Wave 2A Steps (shared across all 9)

#### Step 12 — Wait 9 days (Mon–Fri 9–5)

#### Step 12b — Find Opportunity · Cancellation OS · Most recently created
- Not Found → END
- Found → Step 12c

#### Step 12c — If/Else: Stage = Notice Period (Current)
- NO → END
- YES → Step 12d

#### Step 12d — Final contact-evidence gate

- Contact evidence present → END
- No contact evidence → Step 13

This check runs immediately before owner escalation so a reply received after the earlier Wave 1 branch cannot be misclassified as “no contact”.

#### Step 13 — Create Task: Megan

```
REVIEW REQUIRED — CANCELLATION CONTACT — {{contact.name}}
[Reason — see workflow name]. The workflow has no confirmed contact evidence at the Day 14 gate.

Review the full conversation and call history first. If there has been meaningful contact, apply `cs: contact made` and close this task. If there has not, decide whether a personal message or call is appropriate. No client message is sent automatically in your name.
```

Assign to Megan Brown, due the same day. Include the reason-specific offer links only as internal review context.

#### Step 15 — Wait 11 days (Mon–Fri 9–5)

#### Step 15b — Find Opportunity · Cancellation OS · Most recently created
- Not Found → END
- Found → Step 15c

#### Step 15c — If/Else: Stage = Notice Period (Current)
- NO → END
- YES → Step 16

#### Step 16 — SMS to member (final — door always open, shared)

Same as Step 11m — no owner task at Day 25 (too late to be worth it):

```
Hi {{contact.first_name}}, as your membership wraps up we just wanted to say — we've genuinely loved having you here and the door is always open if you ever want to come back. Take care of yourself.
```

---

## Workflow 1: MC: Moving/Travel

**Trigger filter:** CS: Reason = `Moving away or travelling long term`

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Moving / Travelling

Goal: keep this member's spot held. A pause now is far better than losing them permanently.

Call within 24 hours. Call twice daily until reached.

PRE-CALL PREP:
- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Returning: {{contact.membership_cancellation_movingtravelling__returning}} ✓ confirmed
Travel start date: {{contact.membership_cancellation_movingtravelling_start_date}} ✓ confirmed

Script:
1. Acknowledge the move or travel. Ask about timeline and plans. Be genuinely interested — not transactional.

2. Isolate: is this permanent or temporary?

TEMPORARY or UNSURE → Membership Hold:
"We can put your membership on hold while you're away — your spot stays yours, your rate is locked in, and billing pauses. When you're back, you pick up exactly where you left off."
Standard Hold (1–4 weeks): https://theevolvedgym.com.au/hold-membership
Extended Hold (5–12 weeks): https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
How many weeks do you need? (max 12)

PERMANENT MOVE → Remote membership options:
Offer A — Online Only ($27/week): full programming access, training data retained, no modifications or monitoring
Offer B — Hybrid ($69/week, 1 PT session/month in person or virtual): personalised programming + fitness concierge during business hours — same price regardless of in-person or virtual

3. If all declined: offer farewell session
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Moving / Travelling
Member: {{contact.name}}
Returning: {{contact.membership_cancellation_movingtravelling__returning}}
Travel start: {{contact.membership_cancellation_movingtravelling_start_date}}
Re-offer: Temporary/Unsure → Hold (Standard or Extended) | Permanent → Online Only ($27/wk) or Hybrid (1 PT/month)
```

### Step 11a Task Addition (farewell re-offer)

Re-offer in farewell session: "If it's a temporary move, we can still hold your spot. If it's permanent, we have remote options that keep the training going wherever you are."

---

## Workflow 2: MC: Schedule/Time

**Trigger filter:** CS: Reason = `Schedule and life commitments`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Schedule / Time
Re-offer: 1:1 PT (flexible timing), Hybrid PT + gym, or Online

Call within 24 hours. Call twice daily until reached.

Script:
1. Ask what specifically is making the schedule work — hours, kids, travel time?
2. Isolate the real constraint
3. Re-offer by fit:
   - Unpredictable schedule → 1:1 PT (book week by week, no fixed timetable)
   - Needs gym flexibility → Hybrid PT + drop-in
   - Can't get to the gym → Online membership
4. If all declined: offer farewell session

Form context:
- Main obstacle: {{contact.cs_schedule_time_main_obstacle}}
- Preferred timeslots: {{contact.cs_schedule_time_preferred_timeslots}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Schedule/Time
Member: {{contact.name}}
Main obstacle: {{contact.cs_schedule_time_main_obstacle}}
Preferred timeslots: {{contact.cs_schedule_time_preferred_timeslots}}
Re-offer: 1:1 PT / Hybrid / Online — match to obstacle
```

### Step 11a Task Addition

Re-offer in farewell session: "Is there a schedule that would actually work for you right now? Let's see if we can build something around it."

---

## Workflow 3: MC: Financial

**Trigger filter:** CS: Reason = `Financial reasons`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Financial
Re-offer: Fee waiver / financial relief

Call within 24 hours. Call twice daily until reached.

Script:
1. Lead with empathy — no pressure
2. Clarify duration: is this short-term (weeks) or longer term?
3. Re-offer: "We can pause your fees for [X] weeks to give you breathing room — your membership stays active, your spot is held, and you resume when you're ready. No catch."
4. If they decline: offer farewell session

Form context:
- Pressure duration: {{contact.cs_financial_pressure_duration}}
- Relief weeks requested: {{contact.cs_financial_relief_weeks}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Financial
Member: {{contact.name}}
Pressure duration: {{contact.cs_financial_pressure_duration}}
Relief weeks selected: {{contact.cs_financial_relief_weeks}}
Re-offer: Fee waiver — match to duration selected on form
Note: If approved, flag to admin to apply Stripe credit/pause
```

### Step 11a Task Addition

Re-offer in farewell session: "If it's still a financial thing, we can look at a reduced rate or a short pause — we'd rather find a way than lose you."

---

## Workflow 4: MC: Health/Injury

**Trigger filter:** CS: Reason = `Health, injury, surgery or pregnancy`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Health / Injury
Re-offer: Injury Triage Session, Membership Hold + modified programming on return

Call within 24 hours. Call twice daily until reached.

PRE-CALL PREP:
- Review their original goal and reason for joining
- Note any medical conditions or life stage context already on file
- Check how long they've been a member and what they've achieved

Form context:
- Impact level: {{contact.mc_health__impact_level}} ✓ confirmed
- Description: {{contact.membership_cancellation_health__description}} ✓ confirmed
- Professional advice received: {{contact.membership_cancellation_health__professional_advice}} ✓ confirmed

Script:
1. Lead with genuine care — ask how they're doing and what happened
2. Understand the situation: what's the impact level and what has their GP/physio advised?
   "We regularly work with allied health professionals to get the best outcome for our members — this involves working with your practitioner with your permission. Are you open to that?"
3. Isolate: is a full membership pause actually needed, or could modified programming work?
   "Evidence shows training modifications have faster recovery times and better outcomes in the majority of injuries/health conditions, even in the cases of pregnancy or surgery. We can be very flexible during this time to facilitate your training."
4. Re-offer: "We can hold your membership until you're ready — billing pauses immediately. And when you come back, we can work with you to return safely to regular strength training."
5. If long-term unknown: extended hold option (up to 12 weeks)
6. If all declined: offer farewell session
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Health / Injury
Member: {{contact.name}}
Impact level: {{contact.mc_health__impact_level}}
Description: {{contact.membership_cancellation_health__description}}
Professional advice: {{contact.membership_cancellation_health__professional_advice}}
Re-offer: Injury Triage Session first, then membership hold — standard (1–4 weeks) or extended (5–12 weeks) depending on situation
Note: Membership Hold Form — confirm URL before the call
```

### Step 11a Task Addition

Re-offer in farewell session: "Your body and your strength aren't going anywhere — we can hold your spot and build your return program today."

---

## Workflow 5: MC: Results/Value

**Trigger filter:** CS: Reason = `Not seeing the results or value I expected`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Results / Value
Re-offer: Results Reset (fresh program + direction session with Megan)

Call within 24 hours. Call twice daily until reached.

Script:
1. Ask what they expected vs. what happened — listen fully
2. Identify: was it the program, consistency, communication, or expectations?
3. Re-offer: "I'd like to set you up with a fresh start — a full direction session with Megan to reset your program and make sure we're actually targeting what you came here for."
4. Secondary re-offer if Reset declined: PT package (more personalised guidance)
5. If all declined: offer farewell session

Form context:
- Training duration: {{contact.cs_results_training_duration}}
- Expected outcome: {{contact.cs_results_expected_outcome}}
- Missing element: {{contact.cs_results_missing_element}}
- Struggles communicated to coach: {{contact.cs_results_struggles_communicated}}
- Coach: {{contact.cs_results_coach_contacted}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Results/Value
Member: {{contact.name}}
Training duration: {{contact.cs_results_training_duration}}
Missing element: {{contact.cs_results_missing_element}}
Coach: {{contact.cs_results_coach_contacted}}
Struggles communicated: {{contact.cs_results_struggles_communicated}}
Re-offer: Results Reset with Megan — then PT package if declined
Note: Flag to relevant coach before call if struggles weren't communicated
```

### Step 11a Task Addition

Re-offer in farewell session: "Let's use this session to actually look at what's changed — I think you'll be surprised. And if the program needs resetting, we can do that today."

---

## Workflow 6: MC: New Gym

**Trigger filter:** CS: Reason = `Training elsewhere or consolidating memberships`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Moving to another gym
Re-offer: Re-educate on women's strength standards → address gap → PT Reset Block ($90) if resolvable

Call within 24 hours. Call twice daily until reached.

Script:
1. Ask what they were looking for that they found elsewhere — be curious, not defensive
2. Identify the gap: times? variety? price? location? social? modality?
3. Acknowledge without arguing. Re-educate on what women's bodies actually need:
   - Moving to pilates/cardio/class gym: these improve fitness but don't build or maintain women's muscle. Muscle protects bone density, supports metabolism, reduces menopausal symptoms. Strength is the cornerstone.
   - Moving to general gym: most aren't programmed progressively enough. ASCA guidelines require 2 quality sessions/week at 70–85% 1RM, positive form failure 6–8x/session. Takes 6–12 months of structured coaching to learn safely — most gyms don't do this.
   - Either: "I'm not saying don't go — I'm saying it's worth knowing where your strength sits right now before you do."
4. If gap is resolvable: address it directly (hybrid membership, times, etc.)
5. Re-offer: PT Reset Block — 1 free PT session to assess where their strength sits right now + 3 at 50% off. $90, one time only.
   Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
6. If all declined: offer farewell session

Form context:
- New gym: {{contact.membership_cancellation_elsewhere__new_gym}}
- Attracted by: {{contact.membership_cancellation_elsewhere__attraction}}
- What was missing here: {{contact.membership_cancellation_elsewhere__missing_element}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — New Gym
Member: {{contact.name}}
New gym: {{contact.cs_elsewhere_new_gym}}
Attracted by: {{contact.cs_elsewhere_attraction}}
What was missing: {{contact.cs_elsewhere_missing_element}}
Re-offer: Re-educate on women's strength standards → address gap → PT Reset Block ($90, one-time: 1 free + 3 at 50% off) if resolvable
Note: If gap can't be closed, be honest — but still plant the seed about what they'd be losing
Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
```

### Step 11a Task Addition

Re-offer in farewell session: "Before you go — let's use this session to see exactly where your strength sits right now, so you know what you're taking with you."

---

## Workflow 7: MC: New Style

**Trigger filter:** CS: Reason = `Prefer a different training style or environment`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Wants different training style
Re-offer: Hybrid coaching (strength + preferred style) or 1:1 PT

Call within 24 hours. Call twice daily until reached.

Script:
1. Ask what style they want to explore — cardio, pilates, outdoor, variety?
2. Clarify: is it boredom with strength, or a genuine preference shift?
3. Re-offer: "We can actually build a hybrid approach — keeping the strength foundation (which is doing the work for you) and layering in [their preferred style]. 1:1 gives us the flexibility to do that."
4. If declined: offer farewell session

Form context:
- Primary reason: {{contact.membership_cancellation_style__primary_reason}}
- Attracted to: {{contact.membership_cancellation_style__attraction}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Style/Preference
Member: {{contact.name}}
Primary reason: {{contact.cs_style_primary_reason}}
Attracted to: {{contact.cs_style_attraction}}
Re-offer: Hybrid coaching or 1:1 PT — position as complementary, not competing
```

### Step 11a Task Addition

Re-offer in farewell session: "Let's actually do a session that blends what you love about strength with what you're looking for — see how it feels."

---

## Workflow 8: MC: Other

**Trigger filter:** CS: Reason = `Other` AND CS: Other - Manager Call = `No, please continue with the cancellation`

### Step 2 — Create Task (Piper)

```
RETENTION CALL — {{contact.name}}
Reason: Other (declined manager call on form)
Re-offer: Use judgement — listen first

Call within 24 hours. Call twice daily until reached.

Script:
1. Open with genuine curiosity — "I just wanted to understand a bit more about what's going on"
2. Listen fully before offering anything
3. Identify the real reason (often different from what's written)
4. Re-offer: match to whatever surfaces on the call
5. Last resort: farewell session

Form context:
- Description: {{contact.membership_cancellation_other__description}}
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Other
Member: {{contact.name}}
Their description: {{contact.membership_cancellation_other__description}}
Note: Declined manager call on form. Call within 24hrs — listen first, identify real reason, re-offer accordingly.
```

### Step 11a Task Addition

Re-offer in farewell session: "I'd love to understand what happened — sometimes a conversation in person surfaces things a form can't."

---

## Workflow 9: MC: Other (Booked Call)

**Trigger filter:** CS: Reason = `Other` AND CS: Other - Manager Call = `Yes, I'd like a quick call`

> This member has requested a call with management. They want to talk — use it.

### Step 2 — Create Task (Piper + Owner)

```
RETENTION CALL REQUESTED — {{contact.name}}
Reason: Other — they requested a call

This member asked for a management call on the cancellation form. Call within 24 hours — they're open to a conversation.

Script:
1. Acknowledge that they reached out — "Thanks for wanting to talk this through"
2. Let them lead — ask what's going on
3. Listen fully before re-offering anything
4. Re-offer: match to whatever surfaces
5. If unresolved: book a formal Cancellation Call calendar appointment for Megan/Peter

Form context:
- Description: {{contact.membership_cancellation_other__description}}
```

### Step 3 — Internal Notification (Piper + Owner)

```
Cancellation call REQUESTED — {{contact.name}}
They ticked "Yes, I'd like a quick call" on the cancellation form.
Their reason: {{contact.membership_cancellation_other__description}}
Call within 24 hours. If Piper can't resolve: escalate to Megan/Peter and book via Cancellation Call calendar.
```

### Step 4 — SMS Override for Workflow 9

Replace the shared Step 4 SMS with:

```
Hi {{contact.first_name}}, thanks for flagging that you'd like to have a chat. Piper will give you a call within the next 24 hours to talk things through properly.
```

### Step 11a Task Addition

Re-offer in farewell session: "You reached out because you wanted to talk — let's use this session to figure out if there's a path forward."

---

## GHL Build Notes

### Trigger Filters
Add filters directly on the "Survey submitted" trigger in each workflow. For workflows 8 and 9, you'll need two filter conditions (Reason = Other AND Manager Call = [value]).

### Merge Tags to Verify
The following merge tags need to be confirmed in GHL's field library before publishing. Navigate to each workflow → SMS/task action → merge tag selector → search the field name:

| Field Name | Expected Merge Tag |
|---|---|
| CS: Moving/Travelling - Returning | `{{contact.membership_cancellation_movingtravelling__returning}}` ✓ confirmed |
| CS: Moving/Travelling Start Date | `{{contact.membership_cancellation_movingtravelling_start_date}}` ✓ confirmed |
| CS: Financial - Pressure Duration | `{{contact.cs_financial_pressure_duration}}` |
| CS: Financial Relief - Weeks | `{{contact.cs_financial_relief_weeks}}` |
| CS: Health - Impact Level | `{{contact.mc_health__impact_level}}` ✓ confirmed |
| CS: Health - Description | `{{contact.membership_cancellation_health__description}}` ✓ confirmed |
| CS: Health - Professional Advice | `{{contact.membership_cancellation_health__professional_advice}}` ✓ confirmed |
| CS: Results/Value - Training Duration | `{{contact.cs_results_training_duration}}` |
| CS: Results/Value - Expected Outcome | `{{contact.cs_results_expected_outcome}}` |
| CS: Results/Value - Missing Element | `{{contact.cs_results_missing_element}}` |
| CS: Results/Value - Struggles Communicated | `{{contact.cs_results_struggles_communicated}}` |
| CS: Results/Value - Coach Contacted | `{{contact.cs_results_coach_contacted}}` |
| CS: Elsewhere - New Gym | `{{contact.cs_elsewhere_new_gym}}` |
| CS: Elsewhere - Attraction | `{{contact.cs_elsewhere_attraction}}` |
| CS: Elsewhere - Missing Element | `{{contact.cs_elsewhere_missing_element}}` |
| CS: Style - Primary Reason | `{{contact.cs_style_primary_reason}}` |
| CS: Style - Attraction | `{{contact.cs_style_attraction}}` |
| CS: Other - Description | `{{contact.membership_cancellation_other__description}}` |

### Task Assignment
All tasks assign to Piper. Select her from the GHL user list when creating the task action. For Workflow 9, also notify the Owner (Megan/Peter) via internal notification.

### Merge Tags — Important
Spec merge tags (e.g. `{{contact.cs_financial_pressure_duration}}`) do not match actual GHL field names. Verify every merge tag live in GHL before use. Confirmed tags so far:
- Full name: `{{contact.name}}`
- Financial pressure duration: `{{contact.membership_cancellation_financial__pressure_duration}}`

### Offer Links (verified)
- Financial Relief Form (50% reduced rate / fee waiver): `https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq`
- Standard Membership Hold (1–4 weeks): `https://theevolvedgym.com.au/hold-membership`
- Extended Membership Hold (5–12 weeks, pause, no charges): `https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy`
- All other reason-specific tags: verify in GHL before building each workflow

### If/Else Condition (Step 10)
Requires a **Find Opportunity** action immediately before the If/Else (GHL cannot check pipeline stage without it).
- Find Opportunity: Pipeline = Cancellation OS (`Tl3wKQfNYnAlcgWpORMD`), Most recently created
- Opportunity Found branch → If/Else (Farewell check)
- Opportunity Not Found branch → END

Farewell check condition (AND):
- Tags includes `cs: contact made`
- Pipeline stage = Notice Period (Current) — Stage ID: `4f133549-260c-4bb4-bbb6-3b913b185e1b`

### `cs: contact made` compatibility tag

Automatic member-reply evidence is the primary writer. Piper may still apply the tag when she has a live conversation that automation cannot prove, but the workflow must not depend on her doing so. Used in four checks:
- Before Step 6: if tag exists → END, skip call reminder
- Before Step 8: if tag exists → END, skip escalation
- Step 10: tag must exist AND stage = Notice Period (Current) to proceed to farewell
- Immediately before Megan review: if tag exists → END

The separate `MC: Other (Booked Call)` manager-request workflow is excluded from this rule because the member explicitly requested the call.

### Wait Steps — Advance Window
All wait steps use advance window: Mon–Fri, 9am–5pm.

### Publishing Order
MC: Financial built and published first as test workflow (2026-07-10). Build remaining 8 using MC: Financial as the template — same skeleton, swap reason-specific content in Steps 2 and 3.
