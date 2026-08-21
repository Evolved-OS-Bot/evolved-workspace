# MC: Reason Workflows — Build Guide (Workflows 2–9)
**The Evolved All Female Personal Training & Gym**
**Created:** 2026-07-10

> Use MC: Financial (fully built, published) as the template. Clone it for each workflow, then swap only the steps listed here. Everything else (Step 1, 4 shared, 5, 5b, 6, 7, 7b, 8, 9, 9b, 10, 11b, 11c structure, 11i, 11j, 11k, 11l, 12–16) is identical and requires no changes.
>
> **Merge tags:** All CS: field tags in Steps 2 and 3 must be verified live in GHL before publishing. Search in the merge tag selector — do not trust the spec naming convention. The only confirmed tags so far are `{{contact.name}}`, `{{contact.first_name}}`, and `{{contact.membership_cancellation_financial__pressure_duration}}`.

---

## What Changes Per Workflow

| Step | What changes |
|---|---|
| Trigger filter | Reason value (always) |
| Step 2 | Full task content (always) |
| Step 3 | Full notification content (always) |
| Step 11a | Re-offer line at the bottom of the farewell task |
| Step 11f | "on the financial side" → generic for non-financial workflows |
| Step 11h | Remove financial offer links → generic |
| Step 11hi | Remove financial language → generic |
| Step 11hii | Remove financial offer links → generic |
| Step 13 | Reason reference line |
| Step 14 | Owner SMS — remove financial framing |
| Step 4 | MC: Other (Booked Call) only — full override |
| Step 3 assignees | MC: Other (Booked Call) — add Owner |

---

## Generic Wave 2 Replacements (all non-financial workflows)

When cloning MC: Financial, replace the following steps with these generic versions before adding reason-specific content.

### Step 11f — SMS to member (mid-notice training check-in)

```
Hi {{contact.first_name}}, just checking in — are you still making it in to train? We really encourage everyone to keep coming during their notice period, no hard feelings at all — we want you to get the most out of your membership while you still have it. If anything's changed and you'd like to chat about your options, we're here.
```

### Step 11h — Internal Notification: Piper (contact replied)

> Include the re-offers specific to each workflow. Template below — replace the re-offer lines per workflow.

```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. Find out what's going on — if anything's changed, explore whether there's still a path forward.

Re-offers available:
[INSERT WORKFLOW-SPECIFIC RE-OFFERS]
```

### Step 11hi — Internal Notification: Piper (no reply)

> Include the re-offers specific to each workflow. Template below — replace the re-offer lines per workflow.

```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed, re-offers available:
[INSERT WORKFLOW-SPECIFIC RE-OFFERS]
```

### Step 11hii — Task: Piper (mid-notice call)

> Include the re-offers specific to each workflow. Template below — replace the re-offer lines per workflow.

```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything has changed, re-offers available:
[INSERT WORKFLOW-SPECIFIC RE-OFFERS]
```

### Step 13 — Internal Notification: Owner

Use the same structure as MC: Financial but replace the reason line and re-offer lines per workflow:

```
NO CONTACT — 14 DAYS — {{contact.name}}
[Reason — see workflow name. Update this line per workflow.] Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers available:
[INSERT WORKFLOW-SPECIFIC RE-OFFERS]
```

### Step 14 — Owner SMS

```
Hi {{contact.first_name}}, it's Megan from The Evolved — I wanted to reach out personally. I'd genuinely love to have a chat if you're open to it. No pressure at all — would you be happy to talk?
```

---

## Workflow 1: MC: Health/Injury

**GHL Draft ID:** `df73b324-e02b-4961-b017-4c2a9f235dbb`
**Trigger filter:** CS: Reason = `Health, injury, surgery or pregnancy`

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Health / Injury

Goal: keep this member training. Modification is almost always possible — cessation is the last resort.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Use this to personalise the conversation.

Impact level: {{contact.mc_health__impact_level}}
Description: {{contact.membership_cancellation_health__description}}
Professional advice received: {{contact.membership_cancellation_health__professional_advice}}

─── SCRIPT ────────────────────────────────────────────

1. Lead with genuine care. Ask how they're doing and what happened. Do not rush to an offer.

2. Understand the situation. What is the impact level? What has their GP or physio advised?

"We regularly work with allied health professionals to get the best outcome for our members. This involves working with your practitioner, with your permission. Are you open to that?"

3. Isolate: is a full pause actually needed, or could modified programming work?

"Evidence shows that training modifications have faster recovery times and better outcomes in the majority of injuries and health conditions — even in cases of pregnancy or surgery. We can be very flexible during this time to facilitate your training."

4. Primary re-offer — Injury Triage Session (complimentary 1:1):

"I'd love to book you in for a complimentary session — just us — where we map out exactly what you can do right now and build a modified program around your recovery. No pressure, no agenda. It means you stay moving and we stay connected through this."

5. If they want to pause anyway — Membership Hold:

"We can hold your membership until you're ready — billing pauses immediately. And when you come back, we'll work with you to return safely to regular strength training."

STANDARD HOLD (1–4 weeks) → https://theevolvedgym.com.au/hold-membership
EXTENDED HOLD (5–12 weeks) → https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

Match to their situation — ask, don't assume the duration.

─── IMPORTANT — ADVISE ON CALL ───────────────────────

If they accept a hold and later decide to cancel:

- They must submit a new cancellation form
- A fresh 30-day notice period applies from that date
- Make this clear so there are no surprises

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.\n\n"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.\n\nHere's what we'll do together:\n\n- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now\n- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes\n- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path\n- If there's anything we could have done differently, I want to hear it\n\nThis session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"\n\nBook it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
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

### Step 11a — Farewell Task Re-offer Line

Replace the re-offer line at the bottom of the farewell task with:
```
Re-offer: "Your body and your strength aren't going anywhere — we can hold your spot and build your return program today."
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Health/Injury cancellation. Piper hasn't been able to reach them after 14 days.
```

### Step 14 — Owner SMS

```
Hi {{contact.first_name}}, it's Megan from The Evolved — I just wanted to reach out personally. Whatever you're going through, we'd love to support you through it if we can. Would you be open to a quick chat?
```

---

## Workflow 2: MC: Moving/Travel

**GHL Draft ID:** `93997227-0272-4aa0-a0ec-da56938f3901`
**Trigger filter:** CS: Reason = `Moving away or travelling long term`

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Moving / Travelling

Goal: keep this member's spot held. A pause now is far better than losing them permanently.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Use this to personalise the conversation.

Returning: {{contact.membership_cancellation_movingtravelling__returning}} ✓ confirmed
Travel start date: {{contact.membership_cancellation_movingtravelling_start_date}} ✓ confirmed

─── SCRIPT ────────────────────────────────────────────

1. Acknowledge the move or travel. Ask about the timeline and plans. Be genuinely interested — not transactional.

2. Isolate: is this permanent or temporary?

TEMPORARY or UNSURE → Membership Hold:

"We can put your membership on hold while you're away — your spot stays yours, your rate is locked in, and billing pauses. When you're back, you pick up exactly where you left off."

STANDARD HOLD (1–4 weeks) → https://theevolvedgym.com.au/hold-membership
EXTENDED HOLD (5–12 weeks) → https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

How many weeks do you need? (max 12)

PERMANENT MOVE → Remote membership options:

OFFER A — Online Only ($27/week):
"You keep full access to all programming and your training data stays with us. No modifications or monitoring, but you have everything you need to keep training on your own."

OFFER B — Hybrid ($69/week):
"You get a 30-minute 1:1 session every four weeks plus a personalised program built around it. You still have a coach and your training stays structured — at a significantly lower cost."

Ask which fits their situation best.

─── IMPORTANT — ADVISE ON CALL ───────────────────────

If they accept a hold and later decide to cancel:

- They must submit a new cancellation form
- A fresh 30-day notice period applies from that date
- Make this clear so there are no surprises

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Moving / Travelling
Member: {{contact.name}}
Returning: {{contact.cs_moving_travelling_returning}} [VERIFY TAG]
Travel start: {{contact.cs_moving_travelling_start_date}} [VERIFY TAG]
Re-offer: Membership Hold — billing paused, spot held
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "We can still put your membership on hold — your spot is here when you get back."
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Moving/Travel cancellation. Piper hasn't been able to reach them after 14 days.
```

---

## Workflow 3: MC: Schedule/Time

**GHL Draft ID:** `0a999c4e-2951-4670-974f-632969c37b56`
**Trigger filter:** CS: Reason = `Schedule and life commitments`

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Schedule / Time

Goal: find a format that works around their life. There is almost always one.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Check their attendance pattern — are they attending at all, or has it dropped off?

Main obstacle: {{contact.mc_scheduletime__main_obstacle}}
Preferred timeslots: {{contact.membership_cancellation_scheduletime__preferred_timeslots}}

─── SCRIPT ────────────────────────────────────────────

1. Ask what's specifically creating the clash. Hours? Kids? Commute? Unpredictable roster?

2. Isolate the real constraint: "If we could fix the schedule problem, would you want to keep training here?"

3. Re-offer by fit:

UNPREDICTABLE SCHEDULE → 1:1 PT:
"1:1 PT is completely flexible — you book week by week, no fixed timetable, no commitment to recurring slots. You train when it suits you."

OFF-PEAK (before 5am or after 8pm weekdays, or daytime during the week) → $120/hr
PEAK (5am–8am or 5pm–8pm weekdays, all day weekends) → $180/hr

Ask what their schedule actually looks like — then match to the right time slot and rate.

NEEDS FLEXIBILITY + SOME GYM ACCESS → Hybrid ($69/week):
"You get a 30-minute 1:1 session every four weeks plus personalised programming built around it. You can still drop in to classes when you can make it. The cost is significantly lower than your current membership."

CAN'T GET TO THE GYM → Online Only ($27/week):
"You keep access to our full small group programming through the app — your training data stays with us, everything is tracked. No modifications or 1:1 coaching, but the full program is there."

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Schedule / Time
Member: {{contact.name}}
Main obstacle: {{contact.mc_scheduletime__main_obstacle}}
Preferred timeslots: {{contact.membership_cancellation_scheduletime__preferred_timeslots}}
Re-offer: 1:1 PT / Hybrid / Online — match to obstacle
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "Is there a schedule that would actually work for you right now? Let's see if we can build something around it."
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Schedule/Time cancellation. Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers available:
- 1:1 PT — $120/hr off-peak, $180/hr peak
- Hybrid — $69/week (30-min 1:1 every 4 weeks + personalised programming)
- Online Only — $27/week (full programming through the app, no coaching)
```

---

## Workflow 4: MC: Results/Value

**GHL Draft ID:** `bc2fc64e-f02c-49f9-bc60-7434fbea1588`
**Trigger filter:** CS: Reason = `Not seeing the results or value I expected`

> **Merge tags confirmed 2026-07-15.** All 5 tags verified in GHL.
> **Re-offer order:** PT Reset Block ($90) first → free direction session → farewell session.

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Results / Value

Goal: reconnect this member to their actual progress and give them a genuine reset. They came here for a reason — find it.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?
- Pull their actual strength numbers and training history — what have they achieved?

IMPORTANT: Check if struggles were communicated to their coach before now.
If NO — flag to the relevant coach before making this call.

Training duration: {{contact.membership_cancellation_resultsvalue__training_duration}}
Expected outcome: {{contact.membership_cancellation_resultsvalue__expected_outcome}}
Missing element: {{contact.membership_cancellation_resultsvalue__missing_element}}
Struggles communicated to coach: {{contact.membership_cancellation_resultsvalue__struggles_communicated}}
Coach: {{contact.mc_resultsvalue__coach_contacted}}

─── SCRIPT ────────────────────────────────────────────

1. Ask what they expected vs. what actually happened. Listen fully. Do not defend or dismiss.

2. Identify the root cause: was it the program, consistency, communication, or expectations?

3. Walk them through their actual progress — specific numbers, milestones, physical changes. Make it concrete.

"You started with [X]. You're now at [Y]. That's [Z] months of consistent adaptation — it's happening, even if it doesn't feel that way right now."

4. Primary re-offer — PT Reset Block:

"Before you make any final decisions, I'd love to talk you through something we put together specifically for this situation.

It's a 4-week PT Reset Block — 1 free PT session to reset your program, technique and confidence, plus 3 more PT sessions at 50% off. A personalised plan built around your goals. Clear direction and weekly support.

Normal price is $240. It's $90, one time only, and it's designed to get you moving forward again before you make a final call."

Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h

5. If PT Reset Block declined — free direction session:

"No problem at all. What if we just started with one free session — no charge, no commitment? I'll sit down with you, we'll look at your program and your goals together, and make sure we're actually targeting what you came here for. Nothing to lose."

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Results / Value
Member: {{contact.name}}
Training duration: {{contact.membership_cancellation_resultsvalue__training_duration}}
Missing element: {{contact.membership_cancellation_resultsvalue__missing_element}}
Coach: {{contact.mc_resultsvalue__coach_contacted}}
Struggles communicated: {{contact.membership_cancellation_resultsvalue__struggles_communicated}}
Re-offer: PT Reset Block ($90, one-time: 1 free + 3 at 50% off) → free direction session if declined
Note: If struggles weren't communicated to their coach, flag to that coach before calling
Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "Let's use this session to actually look at what's changed — I think you'll be surprised. And if the program needs resetting, we can do that today."
```

### Step 11h — Internal Notification: Piper (replied)

```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. Find out what's going on — if anything's changed, explore whether there's still a path forward.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session: no charge, no commitment — sit down, reset the program, look at goals together
```

### Step 11hi — Internal Notification: Piper (no reply)

```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session: no charge, no commitment — sit down, reset the program, look at goals together
```

### Step 11hii — Task: Piper (mid-notice call)

```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything has changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session: no charge, no commitment — sit down, reset the program, look at goals together
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Results/Value cancellation. Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session: no charge, no commitment
```

---

## Workflow 5: MC: New Gym

**GHL Draft ID:** `4300ef4f-7ba6-4ac2-b603-5cc45e2df495`
**Trigger filter:** CS: Reason = `Training elsewhere or consolidating memberships`

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Training Elsewhere / New Gym

Goal: understand what they found elsewhere, re-educate on what women's bodies actually need, and offer a bridge back.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Review how long they've been a member and their recent attendance.

New gym: {{contact.membership_cancellation_elsewhere__new_gym}}
Attracted by: {{contact.membership_cancellation_elsewhere__attraction}}
What was missing here: {{contact.membership_cancellation_elsewhere__missing_element}}

─── SCRIPT ────────────────────────────────────────────

1. Ask what they were looking for that they found elsewhere. Be genuinely curious — not defensive.

2. Identify the specific gap: times? variety? price? location? social? a particular modality?

3. Acknowledge it without arguing. Then re-educate:

"I completely understand — and I'd never want to hold you back from something that feels right. Before you go, can I share something worth knowing so you can make the most informed decision?"

Use whichever fits what they're moving to:

MOVING TO PILATES / CARDIO / CLASS-BASED GYM:
"Pilates and cardio improve fitness — genuinely. But they don't build or maintain women's muscle on their own. Muscle is what protects your bone density, supports your metabolism, and reduces menopausal symptoms long-term. The strength work here is designed to be the cornerstone — even one or two quality sessions a week changes what everything else produces for your body."

MOVING TO A GENERAL GYM:
"Most general gyms aren't programmed progressively enough for women to actually build strength over time. ASCA guidelines for women require two quality strength sessions a week at 70–85% of your 1RM, reaching positive form failure 6–8 times per session. That level of intensity takes 6–12 months of structured coaching to learn safely — and most gyms don't program for it or coach it."

EITHER:
"I'm not saying don't go — I'm saying it's worth knowing where your strength sits right now before you do, so you don't lose what you've built without realising it."

4. If the gap is resolvable — address it directly:

- Consolidating memberships: "Would a hybrid membership work? You keep the strength base here, the other gym complements it."
- Times or access issues: address directly if we can genuinely match it. Do not oversell or make commitments you can't keep.

5. Re-offer — PT Reset Block:

"Before you make a final decision, I'd love to offer you a 4-week PT Reset Block — 1 free PT session to see exactly where your strength sits against women's standards right now, plus 3 more at 50% off. $90, one time only. It gives you a clear picture of what you'd be taking with you — and what you'd risk losing."

Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Training Elsewhere / New Gym
Member: {{contact.name}}
New gym: {{contact.membership_cancellation_elsewhere__new_gym}}
Attracted by: {{contact.membership_cancellation_elsewhere__attraction}}
What was missing: {{contact.membership_cancellation_elsewhere__missing_element}}
Re-offer: Re-educate on women's strength standards → address gap → PT Reset Block ($90, one-time: 1 free + 3 at 50% off) if resolvable
Note: If gap can't be closed, be honest — but still plant the seed about what they'd be losing
Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "Before you go — let's use this session to see exactly where your strength sits right now, so you know what you're taking with you."
```

### Step 11h — Internal Notification: Piper (replied)

```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. Find out what's going on — if anything's changed, explore whether there's still a path forward.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Hybrid membership: strength base here, other gym complements it
```

### Step 11hi — Internal Notification: Piper (no reply)

```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Hybrid membership: strength base here, other gym complements it
```

### Step 11hii — Task: Piper (mid-notice call)

```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything has changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Hybrid membership: strength base here, other gym complements it
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
New Gym cancellation. Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Hybrid membership: strength base here, other gym complements it
```

---

## Workflow 6: MC: New Style

**GHL Draft ID:** `49275845-d251-4847-9254-b08a976963b4`
**Trigger filter:** CS: Reason = `Prefer a different training style or environment`

> **Copied from MC: New Gym.** Only the sections below differ — everything else (Steps 4, 11b–11e, 11i–11l, 12–12c, 14–16) stays identical.

### Step 2 — Create Task (Piper)

Replace the goal, pre-call prep, and script (above the farewell block) with:

```
RETENTION CALL - {{contact.name}} | Training Style / Preference

Goal: keep the strength foundation intact. Understand what they're drawn to, re-educate on what their body actually needs, and show them how to have both.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Check their training history and recent attendance — is this boredom, or a longer-term drift?
Note their life stage — style preferences often shift around perimenopause.

Primary reason: {{contact.membership_cancellation_style__primary_reason}}
Attracted to: {{contact.membership_cancellation_style__attraction}}

─── SCRIPT ────────────────────────────────────────────

1. Ask what style they want to explore. Pilates? Cardio? Outdoor? More variety? Be curious, not defensive.

2. Clarify: is this boredom with strength, or a genuine preference shift?

3. Acknowledge it without arguing. Then re-educate:

"I completely understand — wanting something different is totally normal. Before you make any changes, can I share something worth knowing so you can make the most informed decision?"

DRAWN TO PILATES / CARDIO / CLASSES:
"Pilates and cardio improve fitness — genuinely. But they don't build or maintain women's muscle on their own. Muscle is what protects your bone density, supports your metabolism, and reduces menopausal symptoms long-term. The strength work here is designed to be the cornerstone — even one or two quality sessions a week changes what everything else produces for your body."

BOREDOM / WANTING VARIETY:
"Most training styles improve fitness but don't actually build women's strength the way your body needs. ASCA guidelines for women require two quality strength sessions a week at 70–85% of your 1RM, reaching positive form failure 6–8 times per session. That level of intensity takes 6–12 months of structured coaching to learn safely — and you've already built that foundation. It would be a significant loss to walk away from it now."

EITHER:
"I'm not saying don't explore other things — I'm saying it's worth knowing where your strength sits right now before you do, so you don't lose what you've built without realising it."

4. Re-offer — PT Reset Block:

"Before you make any changes, I'd love to offer you a 4-week PT Reset Block — 1 free PT session to see exactly where your strength sits against women's standards right now, plus 3 more at 50% off. $90, one time only. It gives you a clear picture of what you'd be giving up — and whether there's a way to have both."

Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h

5. If PT Reset Block declined — 1:1 PT hybrid:

"What if you didn't have to choose? 1:1 PT gives us the flexibility to blend — we keep the compound strength work and build in [their preferred style] around it. You get the variety you're looking for without losing the foundation that's actually changing your body."
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Training Style / Environment
Member: {{contact.name}}
Primary reason: {{contact.membership_cancellation_style__primary_reason}}
Attracted to: {{contact.membership_cancellation_style__attraction}}
Re-offer: PT Reset Block ($90, one-time: 1 free + 3 at 50% off) → 1:1 PT hybrid if declined
Note: Re-educate on ASCA standards and muscle loss risk before offering
Payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "Before you go — let's use this session to see exactly where your strength sits right now, so you know what you'd be giving up. And if there's a way to blend what you're looking for with what's already working, we can map that out today."
```

### Step 11h — Internal Notification: Piper (replied)

```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. Find out what's going on — if anything's changed, explore whether there's still a path forward.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- 1:1 PT hybrid: blend strength with their preferred style — it doesn't have to be either/or
```

### Step 11hi — Internal Notification: Piper (no reply)

```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- 1:1 PT hybrid: blend strength with their preferred style — it doesn't have to be either/or
```

### Step 11hii — Task: Piper (mid-notice call)

```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything has changed, re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- 1:1 PT hybrid: blend strength with their preferred style — it doesn't have to be either/or
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Style/Preference cancellation. Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers available:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- 1:1 PT hybrid: blend strength with their preferred style — it doesn't have to be either/or
```

---

## Workflow 7: MC: Other

**GHL Draft ID:** `4f9ec2c2-4d59-4c69-8a51-2ec3b9eccc9b`
**Trigger filter:** CS: Reason = `Other` AND CS: Other - Manager Call = `No, please continue with the cancellation`

> Two filter conditions required on the trigger.

### Step 2 — Create Task (Piper)

```
RETENTION CALL - {{contact.name}} | Other

Goal: find the real reason. The form answer is rarely the full picture.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Read their description carefully — it may hint at the real reason.

More Info: {{contact.membership_cancellation_other__description}}

─── SCRIPT ────────────────────────────────────────────

1. Open with genuine curiosity: "I just wanted to understand a bit more about what's going on — is that okay?"

2. Let them talk. Do not offer anything until you understand the actual reason.

3. The real reason is often financial, schedule, results, or something personal. Once you identify it — match the re-offer to that reason:

FINANCIAL:
- Financial Relief Form (50% reduced rate / fee waiver): https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold (pause, no charges, up to 12 weeks): https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

HEALTH / INJURY:
- Complimentary Injury Triage Session — book as a 1:1 PT session
- Standard Hold (1–4 weeks): https://theevolvedgym.com.au/hold-membership
- Extended Hold (5–12 weeks): https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

MOVING / TRAVEL:
- Standard Hold (1–4 weeks): https://theevolvedgym.com.au/hold-membership
- Extended Hold (5–12 weeks): https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
- Online Only ($27/week) or Hybrid ($69/week) if permanent move

SCHEDULE / TIME:
- 1:1 PT — Off-peak $120/hr, Peak $180/hr (flexible, no fixed timetable)
- Hybrid — $69/week (30-min 1:1 every 4 weeks + personalised programming)
- Online Only — $27/week (full programming, no coaching)

RESULTS / VALUE OR STYLE / NEW GYM:
- PT Reset Block ($90, one-time): 1 free PT session + 3 at 50% off — payment link: https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session if Reset Block declined

4. If the reason is personal or sensitive, treat it with care. Don't push for a re-offer if the moment isn't right.

5. Last resort: farewell session.

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper)

```
New cancellation — Other
Member: {{contact.name}}
More Info: {{contact.membership_cancellation_other__description}}
Note: They declined a manager call on the form. Call within 24 hours — listen first, identify the real reason, re-offer accordingly.
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "I'd love to understand what happened — sometimes a conversation in person surfaces things a form can't."
```

### Step 11h — Internal Notification: Piper (replied)

```
{{contact.name}} replied to your day 14 check-in — respond now.
Keep it warm and conversational. Find out what's going on — match re-offer to whatever the real reason is.

Re-offers by reason:

FINANCIAL:
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

HEALTH / INJURY:
- Complimentary Injury Triage Session
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

MOVING / TRAVEL:
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
- Online Only ($27/week) or Hybrid ($69/week) if permanent

SCHEDULE / TIME:
- 1:1 PT — Off-peak $120/hr, Peak $180/hr
- Hybrid — $69/week
- Online Only — $27/week

RESULTS / VALUE OR STYLE / NEW GYM:
- PT Reset Block ($90): https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session if declined
```

### Step 11hi — Internal Notification: Piper (no reply)

```
No reply from {{contact.name}} to the day 14 check-in.

Check their attendance — have they been coming in during their notice period?

Call them:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

If anything's changed, re-offers by reason:

FINANCIAL:
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

HEALTH / INJURY:
- Complimentary Injury Triage Session
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

MOVING / TRAVEL:
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
- Online Only ($27/week) or Hybrid ($69/week) if permanent

SCHEDULE / TIME:
- 1:1 PT — Off-peak $120/hr, Peak $180/hr
- Hybrid — $69/week
- Online Only — $27/week

RESULTS / VALUE OR STYLE / NEW GYM:
- PT Reset Block ($90): https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session if declined
```

### Step 11hii — Task: Piper (mid-notice call)

```
MID-NOTICE CALL — {{contact.name}}
No reply to day 14 SMS.

Check their attendance, then call:
- Still attending: "Just wanted to say we love seeing you in here — make sure you're making the most of it while you have it."
- Stopped coming: "We'd really encourage you to keep coming in — no hard feelings, we just want you to get the most out of your membership while you still have it."

Re-offers by reason:

FINANCIAL:
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

HEALTH / INJURY:
- Complimentary Injury Triage Session
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

MOVING / TRAVEL:
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
- Online Only ($27/week) or Hybrid ($69/week) if permanent

SCHEDULE / TIME:
- 1:1 PT — Off-peak $120/hr, Peak $180/hr
- Hybrid — $69/week
- Online Only — $27/week

RESULTS / VALUE OR STYLE / NEW GYM:
- PT Reset Block ($90): https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session if declined
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Other (declined manager call) cancellation. Piper hasn't been able to reach them after 14 days.

Your message will carry more weight now. The Day 14 SMS fires after this — reach out personally on top of that if you can.

Re-offers by reason:

FINANCIAL:
- Financial Relief Form: https://links.theevolvedgym.com.au/widget/survey/fzIicXBKjm0CrJfXwgLq
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

HEALTH / INJURY:
- Complimentary Injury Triage Session
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy

MOVING / TRAVEL:
- Standard Hold: https://theevolvedgym.com.au/hold-membership
- Extended Hold: https://links.theevolvedgym.com.au/widget/survey/Q9BRXF5zpiQjDoVB1Diy
- Online Only ($27/week) or Hybrid ($69/week) if permanent

SCHEDULE / TIME:
- 1:1 PT — Off-peak $120/hr, Peak $180/hr
- Hybrid — $69/week
- Online Only — $27/week

RESULTS / VALUE OR STYLE / NEW GYM:
- PT Reset Block ($90): https://pay.theevolvedgym.com.au/b/28EaEYbjS3A35FR6gzgbm1h
- Free direction session if declined
```

---

## Workflow 8: MC: Other (Booked Call)

**GHL Draft ID:** `62c34799-0de4-4281-b5e3-bab95ae70eb9`
**Trigger filter:** CS: Reason = `Other` AND CS: Other - Manager Call = `Yes, I'd like a quick call`

> Two filter conditions required on the trigger.
> This member actively requested a call — use it. Steps 2, 3, and 4 differ from all other workflows.

### Step 2 — Create Task (Piper AND Owner)

> Assign task to Piper. Also send a copy of the notification to Owner (Step 3).

```
RETENTION CALL REQUESTED - {{contact.name}} | Other — Call Requested

Goal: this member asked for this conversation. They're open. Use it.

Call within 24 hours. Call twice daily until reached.

─── PRE-CALL PREPARATION ─────────────────────────────

Before calling, check their contact record:

- What was their initial goal?
- Any medical conditions or life stage notes?
- What was their reason for joining?

Read their description carefully — it may surface the real concern.
Prepare to hand off to Megan/Peter if the call surfaces something beyond your remit.

Description: {{contact.cs_other_description}} [VERIFY TAG IN GHL]

─── SCRIPT ────────────────────────────────────────────

1. Acknowledge that they reached out: "Thanks for flagging that you wanted to chat — I really appreciate that."

2. Let them lead. Ask what's going on and listen fully before offering anything.

3. Match the re-offer to whatever surfaces — financial, schedule, results, style. Follow the relevant script framework.

4. If the situation is beyond your scope to resolve, or needs an owner decision: book a formal Cancellation Call appointment with Megan or Peter on the spot. Do not leave it open.

─── IF ALL OFFERS DECLINED — FAREWELL SESSION ─────────

Do not let the call end without booking this. It is your last opportunity.

"Before your membership wraps up, I'd love to offer you a complimentary 30-minute session — just you and me, no agenda, no pitch.

Here's what we'll do together:

- Run through a mini strength assessment so you leave knowing exactly where your fitness is right now
- Walk through everything you've achieved since you joined — specific lifts, milestones, physical changes
- Show you exactly where you'd be in 3, 6, and 12 months if you stayed on this path
- If there's anything we could have done differently, I want to hear it

This session is on us, completely complimentary. I want to book it before we hang up — what does your schedule look like in the next 3 days?"

Book it on the spot as a 1:1 30 Min PT Session. Do not leave it as an open invitation.
```

### Step 3 — Internal Notification (Piper + Owner)

> Send to both Piper and Owner (Megan/Peter).

```
Cancellation call REQUESTED — {{contact.name}}
They ticked "Yes, I'd like a quick call" on the cancellation form.
Their reason: {{contact.cs_other_description}} [VERIFY TAG]
Piper: Call within 24 hours. If you can't resolve it: escalate to Megan/Peter and book via the Cancellation Call calendar.
```

### Step 4 — SMS to Member (OVERRIDE — differs from shared Step 4)

> Replace the shared Step 4 SMS entirely:

```
Hi {{contact.first_name}}, thanks for letting us know you'd like to chat — we really appreciate that. Piper will give you a call within the next 24 hours to talk things through properly.
```

### Step 11a — Farewell Task Re-offer Line

```
Re-offer: "You reached out because you wanted to talk — let's use this session to figure out if there's a path forward."
```

### Step 13 — Owner Notification Reason Line

```
NO CONTACT — 14 DAYS — {{contact.name}}
Other (requested call) cancellation. Piper hasn't been able to reach them after 14 days. This member specifically asked for a call — worth a direct owner reach-out.
```

---

## Build Order & Checklist

Work through these in order. Each should take ~20–30 minutes once the template is cloned.

- [x] MC: Health/Injury (`df73b324-e02b-4961-b017-4c2a9f235dbb`)
- [x] MC: Moving/Travel (`93997227-0272-4aa0-a0ec-da56938f3901`)
- [x] MC: Schedule/Time (`0a999c4e-2951-4670-974f-632969c37b56`)
- [x] MC: Results/Value (`bc2fc64e-f02c-49f9-bc60-7434fbea1588`)
- [x] MC: New Gym (`4300ef4f-7ba6-4ac2-b603-5cc45e2df495`)
- [x] MC: New Style (`49275845-d251-4847-9254-b08a976963b4`)
- [x] MC: Other (`4f9ec2c2-4d59-4c69-8a51-2ec3b9eccc9b`)
- [x] MC: Other (Booked Call) (`62c34799-0de4-4281-b5e3-bab95ae70eb9`)

**For each workflow:**
1. Open the draft workflow in GHL using the ID above
2. Set the trigger filter (CS: Reason = value above; dual filter for workflows 7 and 8)
3. Swap Steps 2 and 3 with content above
4. Apply the generic Wave 2 replacements (Steps 11f, 11h, 11hi, 11hii, 14)
5. Update Step 11a farewell re-offer line
6. Update Step 13 reason line
7. Verify all merge tags in GHL before publishing (search in merge tag selector)
8. Publish

**Workflow 8 only:** Also swap Step 4 SMS and confirm Step 3 notification goes to both Piper and Owner.

---

## After All 8 Are Published

- [x] Update `outputs/systems/cancellation-system.md` — MC: reason workflows status → `published` (2026-07-15)
- [x] Update `context/roadmap.md` — "Cancellation MC: Reason Workflows" → Live (2026-07-15)
- [ ] Test MC: Financial end-to-end (still pending) — do this before testing others
