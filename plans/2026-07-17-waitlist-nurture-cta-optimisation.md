# Plan: Waitlist Nurture CTA Optimisation

**Created:** 2026-07-17
**Status:** Complete — 2026-07-17

All GHL changes deployed across all 5 workflows (POSTM, PERIM, PPP, 20/30, TEEN). Workspace doc updated. Notes from implementation:
- Post Menopause Day 2b opener kept as original ("lose this" / "fat loss") — proposed replacement framing not accurate to industry reality
- Perimenopause Day 2b opener also kept as original — same reasoning, consistent across all sequences
- Day 3 undocumented Met Class Assessment P.S. found and removed across all workflows (was not in original audit)
- Day 0 and Day 1 buttons added across all workflows (not in original plan scope, applied consistently)
**Workspace doc to update:** `outputs/systems/waitlist-nurture-sequences.md`

---

## Goal

Improve SA booking click-through from the 30DNNC sequences. Current state: confirmed 0% click-through across all CTA emails despite 75–100% open rates. All CTAs are plain text P.S. links.

---

## What's Changing — Summary

| Change | Affects | Action |
|---|---|---|
| Day 12 CTA | All 5 sequences | Replace seminar replay P.S. with SA button CTA |
| Day 18 CTA | All 5 sequences | Remove TransformationFLIX P.S. entirely (email becomes CTA-free) |
| Day 21 CTA | All 5 sequences | Replace Metabolic Classification Assessment P.S. with SA button CTA |
| Day 30 CTA | All 5 sequences | Remove TransformationFLIX option, keep SA CTA only |
| Button format | All SA CTA emails | Replace every plain text SA link with an HTML button |
| Day 2b Peri opener | Perimenopause | Change anti-message framing to be Peri-specific |
| Day 2b Post-Meno opener | Post Menopause | Change anti-message framing to be Post-Meno-specific (differentiate from Peri) |
| Day 2b 20s & 30s stats | 20s & 30s | Fix tone inconsistency in standards bullet points |

**Emails to update (button + copy changes):** Days 2b, 5, 7, 9, 12, 15, 21, 27, 30 across all 5 sequences = 45 emails.
**Emails to update (copy only — remove P.S.):** Day 18 across all 5 sequences = 5 emails.
**Emails to update (button only — existing SA CTA, no copy change):** Days 5, 7, 9, 15, 27 across all 5 sequences = 25 emails.

---

## Part 1 — How to Add an HTML Button in GHL Workflow Email Builder

Do this for every email step that has an SA CTA. The process is the same each time.

### Steps

1. Open GHL > Automations > find the relevant 30DNNC workflow (TEEN 30DNNC, 20/30 30DNNC, PPP 30DNNC, PERIM 30DNNC, POSTM 30DNNC)
2. Click the email step to open the email editor
3. Find the P.S. section at the bottom of the email
4. Delete the existing plain text CTA line (e.g., "👉 [Book Your Free Strength Assessment]" or similar)
5. Keep the P.S. copy above it — only delete the link line itself
6. In the email editor toolbar/element panel, add a **Button** element below the P.S. copy
7. Set the button text to the copy specified below for that email and life stage
8. Set the button URL to: `https://www.theevolvedgym.com.au/strength-assessment`
9. Set button colour to brand colour (coral/pink — match existing brand elements)
10. Save the email step
11. Leave the workflow published — changes to steps take effect immediately

### Button text by email and life stage

Use these exact button labels:

| Day | Teen | 20s & 30s | PPP | Perimenopause | Post Menopause |
|---|---|---|---|---|---|
| 2b | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 5 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 7 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 9 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 12 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 15 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 21 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 27 | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment | Book Your Free Strength Assessment |
| 30 | Book My Free Strength Assessment | Book My Free Strength Assessment | Book My Free Strength Assessment | Book My Free Strength Assessment | Book My Free Strength Assessment |

Note: Day 30 uses "My" — it closes the 30-day arc with the subscriber as the agent. All others use "Your."

---

## Part 2 — Day 12 CTA Replacement (Seminar Replay → SA)

### What to do in GHL

1. Open the Day 12 email step in each workflow
2. Find the P.S. at the bottom — it currently links to the YouTube seminar replay
3. Delete the entire P.S. section
4. Paste the new P.S. copy below (per life stage)
5. Add a button element below the new P.S. copy (see Part 1 for button instructions)
6. Set button URL: `https://www.theevolvedgym.com.au/strength-assessment`

### New Day 12 P.S. copy — Teen

> P.S. — Creatine is one piece of the puzzle. The other piece is knowing exactly what your training should look like right now.
>
> That is what the free Strength Assessment is for. Come in, see where you are starting, and walk out with a clear next step.

**Button text:** Book Your Free Strength Assessment

---

### New Day 12 P.S. copy — 20s & 30s

> P.S. — Creatine will help your training. But only if your training is pointed in the right direction.
>
> Book a free Strength Assessment and we will show you exactly what to focus on for your body and your goals.

**Button text:** Book Your Free Strength Assessment

---

### New Day 12 P.S. copy — Planning / Pregnant / Post-Partum

> P.S. — The right supplements support your training. The right training supports everything else.
>
> Book a free Strength Assessment and we will map out exactly what safe, effective training looks like for your stage.

**Button text:** Book Your Free Strength Assessment

---

### New Day 12 P.S. copy — Perimenopause

> P.S. — Creatine is one of the best tools in the perimenopausal toolkit. Knowing how to train is the other.
>
> Book a free Strength Assessment and we will show you exactly what your training should look like right now.

**Button text:** Book Your Free Strength Assessment

---

### New Day 12 P.S. copy — Post Menopause

> P.S. — Creatine matters most when your training is giving it something to work with.
>
> Book a free Strength Assessment and we will map out exactly what your training should focus on for bone density, muscle, and longevity.

**Button text:** Book Your Free Strength Assessment

---

## Part 3 — Day 18 CTA Removal (TransformationFLIX → CTA-free)

### What to do in GHL

1. Open the Day 18 email step in each workflow
2. Find the P.S. at the bottom — it links to TransformationFLIX
3. Delete the entire P.S. section
4. Do not replace with anything — the email body stands on its own
5. Save

No new copy needed. Day 18 becomes a CTA-free educational email.

---

## Part 4 — Day 21 CTA Replacement (Metabolic Classification Assessment → SA)

### What to do in GHL

1. Open the Day 21 email step in each workflow
2. Find the P.S. at the bottom — it links to the Metabolic Classification Assessment survey
3. Delete the entire P.S. section
4. Paste the new P.S. copy below (per life stage)
5. Add a button element below the new P.S. copy (see Part 1)
6. Set button URL: `https://www.theevolvedgym.com.au/strength-assessment`

The Day 21 email topic is long-term identity and who you say you are. The P.S. copy bridges from identity language to action.

### New Day 21 P.S. copy — Teen

> P.S. — The strongest version of you does not wait. She books the thing.
>
> Your free Strength Assessment is where it starts. Come in, see where you are at, and get a clear next step.

**Button text:** Book Your Free Strength Assessment

---

### New Day 21 P.S. copy — 20s & 30s

> P.S. — Identity follows action. If you see yourself as someone who trains seriously, this is your next move.
>
> Book your free Strength Assessment and we will give you a clear picture of where you are and what to focus on.

**Button text:** Book Your Free Strength Assessment

---

### New Day 21 P.S. copy — Planning / Pregnant / Post-Partum

> P.S. — The strongest version of you is already in there. The Strength Assessment is just the moment she steps forward.
>
> Come in, see where you are starting, and walk out with a plan built around your body and your stage.

**Button text:** Book Your Free Strength Assessment

---

### New Day 21 P.S. copy — Perimenopause

> P.S. — You have been building the identity. Now take the action that matches it.
>
> Book your free Strength Assessment and we will show you exactly where your strength sits right now and what to do with it.

**Button text:** Book Your Free Strength Assessment

---

### New Day 21 P.S. copy — Post Menopause

> P.S. — You have spent 21 days becoming her. The Strength Assessment is how you meet her.
>
> Come in, see where your strength sits, and walk away with a personalised plan for what comes next.

**Button text:** Book Your Free Strength Assessment

---

## Part 5 — Day 30 CTA Update (Remove TransformationFLIX, Keep SA Only)

### What to do in GHL

1. Open the Day 30 email step in each workflow
2. Find the P.S. at the bottom — it currently offers two options (SA and TransformationFLIX)
3. Delete the entire P.S. section
4. Paste the new P.S. copy below (per life stage)
5. Add a button element below (see Part 1)
6. Set button URL: `https://www.theevolvedgym.com.au/strength-assessment`

### New Day 30 P.S. copy — Teen

> P.S. — You have made it through 30 days. That says a lot about who you are.
>
> You showed up. You reflected. You started to shift. Even if it was just one small step at a time.
>
> The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away knowing precisely what your body needs and what is possible from here.

**Button text:** Book My Free Strength Assessment

---

### New Day 30 P.S. copy — 20s & 30s

> P.S. — You have made it through 30 days. That says a lot about who you are.
>
> You showed up. You reflected. You started to shift. Even if it was just one small step at a time.
>
> The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away knowing precisely what to focus on and what is possible from here.

**Button text:** Book My Free Strength Assessment

---

### New Day 30 P.S. copy — Planning / Pregnant / Post-Partum

> P.S. — You have made it through 30 days. That says a lot about who you are.
>
> You showed up. You reflected. You started to shift. Even if it was just one small step at a time.
>
> The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment is flexible, safe for every stage, and built around you. You will walk out with a clear picture and a personalised next step.

**Button text:** Book My Free Strength Assessment

---

### New Day 30 P.S. copy — Perimenopause

> P.S. — You have made it through 30 days. That says a lot about who you are.
>
> You showed up. You reflected. You started to shift. Even if it was just one small step at a time.
>
> The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away with a clear understanding of where your body is and exactly what it needs in this season.

**Button text:** Book My Free Strength Assessment

---

### New Day 30 P.S. copy — Post Menopause

> P.S. — You have made it through 30 days. That says a lot about who you are.
>
> You showed up. You reflected. You started to shift. Even if it was just one small step at a time.
>
> The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away with a clear picture of your bone health, muscle, and what to focus on for the next season.

**Button text:** Book My Free Strength Assessment

---

## Part 6 — Day 2b Copy Fixes

These are the three copy issues identified in the sequence audit. Make these changes in the same session as the CTA updates.

---

### Fix 1 — Perimenopause Day 2b: Update opener framing

**Problem:** Currently opens with "It is full of 'lose this' and 'fat loss' messaging" — same as Post Menopause. These two sequences are indistinguishable at the top of the most important email in the sequence.

**What to do in GHL:**
1. Open PERIM 30DNNC > Day 2b email step
2. Find the opening two paragraphs (the anti-industry framing)
3. Replace with the copy below

**Replace this:**
> Truthfully, we really dislike the fitness industry. It is full of "lose this" and "fat loss" messaging.
>
> That is not what we are about.
>
> We would rather focus on what you will gain. During perimenopause, strength is not just about looking toned. It is about easing symptoms, protecting your bones, and giving you the energy and confidence to feel like yourself again.

**With this:**
> Truthfully, we really dislike the fitness industry. It is full of "fix your hormones first" and "just try harder" messaging that completely ignores what is actually happening in your body.
>
> That is not what we are about.
>
> We would rather focus on what you can build. During perimenopause, strength is not a nice-to-have. It is the most evidence-backed tool available for managing symptoms, protecting your bones, and reclaiming your energy and confidence.

---

### Fix 2 — 20s & 30s Day 2b: Fix tone inconsistency in standards section

**Problem:** "glutes that turn heads, endurance to dance all night" is a different register to the rest of the email. The sequence voice is confident and aspirational but grounded, not nightlife-adjacent.

**What to do in GHL:**
1. Open 20/30 30DNNC > Day 2b email step
2. Find the standards bullet points section
3. Find the split squat bullet specifically
4. Replace the one bullet below — everything else in the section stays the same

**Replace this:**
> Women who can split squat 50% of their body weight for 10 reps build glutes that turn heads, endurance to dance all night, and the athleticism to outlast competition.

**With this:**
> Women who can split squat 50% of their body weight for 10 reps build visible shape, real athletic endurance, and the body confidence to own every room they walk into.

---

## Part 7 — Workspace Doc Updates

After completing all GHL changes, update `outputs/systems/waitlist-nurture-sequences.md`:

1. **CTA map table** — update Days 12 and 21 from "Seminar replay" and "Metabolic Classification Assessment" to "SA (P.S. + button)"
2. **CTA map table** — update Day 18 to "None (CTA removed)" and Day 30 to "SA button only"
3. **Email schedule tables** — update the SA CTA column for all 5 sequences for Days 12, 18, 21, 30
4. **Day 12 section** — add the new P.S. copy for all 5 life stages
5. **Day 21 section** — add the new P.S. copy for all 5 life stages
6. **Day 30 sections** — update all 5 P.S. sections to remove TransformationFLIX option
7. **Day 2b sections** — update the Peri, Post-Meno, and 20s & 30s opener/stats copy
8. **Remaining Issues** — remove items 1 and 2 (the Day 2b copy issues) once fixed
9. **Last Updated** date

---

## Recommended Order of Work

Work one workflow at a time, completing all changes for that sequence before moving to the next. Suggested order: POSTM (most stats data, easiest to verify), PERIM, PPP, 20/30, TEEN.

For each workflow:
1. Day 2b copy fix (if applicable)
2. Day 12 — replace P.S. + add button
3. Day 18 — remove P.S.
4. Day 21 — replace P.S. + add button
5. Day 30 — replace P.S. + add button
6. Days 5, 7, 9, 15, 27 — add button only (no copy change, just replace plain text link with button)

Then update the workspace doc in one pass at the end.

---

## Success Metric

Current: 0% click-through on all SA CTA emails (confirmed, tracking on).
Target: Any measurable click-through on Day 2b and Day 12 within 4 weeks of deploying changes. Day 2b with 60% open rate is the leading indicator — if the button format is working, it will show there first.
