# Waitlist Nurture Email Sequences — Reference Document

**Last Updated:** 2026-07-22
**Source PDFs:** `/Users/peterbrown/Downloads/30 DNNC Email Sequences/`
**Total emails:** ~162 across 5 sequences

---

## System Overview

**Intended funnel stage:** Post email capture, pre-SA booked
**Trigger:** Contact provides email on waitlist page (before calendar shown)
**Schedule:** Daily emails at 6AM AEST, Day 0 through Day 30
**Day 2b:** A second email sent on Day 2 (12 hours after Day 2 regular) — dedicated SA CTA
**Platform:** GHL workflow

**SA CTA URL:** `www.theevolvedgym.com.au/strength-assessment`
**Metabolic Classification Assessment URL:** `https://api.leadconnectorhq.com/widget/survey/3dC0KGX0gwEjkDf5YZHx?sessionId=c07c2952-be6c-49f9-a7b5-96d897596ede&trigger_link=2JxroTHvoBtPNisYxvqD` *(no longer used in sequence — Day 21 CTA updated to SA booking 2026-07-17)*

**Five sequences (segmented by life stage at signup):**
1. Teen
2. 20s & 30s
3. Planning / Pregnant / Post-Partum
4. Perimenopause
5. Post Menopause

---

## SA CTA Pattern (all sequences)

SA CTAs appear in:
- Day 0 (soft mention in welcome email — "we've opened a few rare spots this week")
- Day 1 (P.S.)
- Day 2b (dedicated SA email — sent 12 hours after Day 2)
- Day 5 (P.S. + button)
- Day 7 (P.S. + button)
- Day 9 (P.S. + button)
- Day 12 (P.S. + button — updated 2026-07-17, was seminar replay)
- Day 15 (P.S. + button)
- Day 21 (P.S. + button — updated 2026-07-17, was Metabolic Classification Assessment)
- Day 27 (P.S. + button)
- Day 30 (button only — updated 2026-07-17, TransformationFLIX secondary CTA removed)

**Day 18 CTA removed** (2026-07-17) — was TransformationFLIX P.S., now a CTA-free educational email.

**Button format:** All SA CTAs use an HTML button element in GHL (coral/pink brand colour). Button URL: `https://www.theevolvedgym.com.au/strength-assessment`. Days 0, 1, 2b use inline SA links; all others have button elements.

---

## Sequence 1: Teen

**Source PDF:** `Teenage Email Sequence - NNC.pdf`
**Voice:** Energetic, sport-focused, confidence-driven. "Strong girl energy." References sport, school, dance.
**Anti-message framing:** "shrink this" and "diet harder"
**Sign-off:** Megan Brown, Head Coach / Founder

### Email Schedule

| Day | Subject Line | SA CTA |
|-----|-------------|--------|
| 0 | Welcome to the Strongest Start of Your Life | Yes (body) |
| 1 | Want to Look Better, Think Sharper, and Move Faster? | Yes (P.S.) |
| 2 | Dance Smarter: Spot the Gap, Nail the Move | — |
| 2b | *(See full text below)* | Yes (entire email) |
| 3 | MIT's Habit Hack (And Why You're Not Lazy) | — |
| 4 | Want to Glow, Grow, and Feel Amazing? Start Here. | — |
| 5 | Can't Sleep? Try These 10 Glow-Up Tricks Tonight | Yes (P.S.) |
| 6 | Every Meal Sends a Message. What's Yours Saying? | — |
| 7 | 10 Simple Food Fixes That Actually Make a Difference | Yes (P.S.) |
| 8 | Want to Look Stronger, Feel Better, and Stay Lean? Start Here. | — |
| 9 | Want to Get Stronger? Here's What Really Works | Yes (P.S.) |
| 10 | What's Worth Taking (And What's Just Hype) | — |
| 11 | The One Protein Powder I Actually Recommend | — |
| 12 | Creatine: The Cheapest Brain + Body Boost There Is | Yes (P.S. + button) — SA booking |
| 13 | The Oil That Helps You Think Clearer, Feel Calmer & Move Better | — |
| 14 | Hit a PB, Change Your Identity | — |
| 15 | What to Do When You Miss a Workout (Or Five) | Yes (P.S.) — SA booking |
| 16 | Carbs Aren't the Enemy. You Just Need to Time Them Right | — |
| 17 | The Fat-Burning Hack That Feels Like… Living? | — |
| 18 | Hormones, Fatigue, Cravings… Here's What's Actually Going On | — |
| 19 | Studying, Stress, and Strength: Here's How to Handle It | — |
| 20 | If You Do This One Thing Weekly, You'll Keep Going | — |
| 21 | Want to Change Long-Term? Start With Who You Are | Yes (P.S. + button) — SA booking |
| 22 | Your 20-Minute Reset That Changes the Whole Week | — |
| 23 | Don't Just Train Hard. Train Smart | — |
| 24 | Want to Know If It's Working? Track This Instead | Yes (P.S.) — soft reply CTA |
| 25 | How to Tell If You're Winning… Without a Mirror | — |
| 26 | Don't Burn Out. Build in These Breaks Instead | — |
| 27 | Muscle Gives You More Than Just a Better Body | Yes (P.S.) |
| 28 | She Started Tired. She's Finishing Powerful. | — |
| 29 | This Wasn't a Reset. This Was a Build | — |
| 30 | This Is Chapter One of Your Strongest Season Yet | Yes (button) — SA booking only |

### Day 2b SA CTA — Teen

**Subject:** *(sent as second email on Day 2)*

Hi {{contact.first_name}},

Truthfully, we really dislike the fitness industry. It is full of "shrink this" and "diet harder" messaging.

That is not what we are about.

We would rather focus on what you will gain. As a teen, building strength is not just about how you look. It is about creating confidence, performing better in sport, moving well, and having the energy to enjoy life without limits.

That is why we created our Strength Assessment.

Here is what you will get when you book one:

**Where Are We Starting?**
A short, guided strength and movement check-up. No pressure, no judgement.

**What Is Your Next Step?**
Personalised tips on improving strength, posture, and confidence in a way that fits your life.

**Do You Have Concerns?**
Bring them with you. We will answer your questions and show you how to train safely.

**Can We Fast Track This?**
Yes. You will leave with a game plan for moving forward with clarity, whether you join us or not.

And here is why it matters:

- Women begin losing muscle around age 30, up to 250g per year. Building it now means you will be stronger and healthier for decades. If you are not building it, you are losing it.
- Girls who can split squat 50% of their body weight for 10 reps build toned legs and glutes that support confidence, sport, dance, and feeling amazing in whatever they wear.
- Girls who can carry 75% of their body weight for 1 minute have the stamina for school, activities, sport, and friends without running out of energy.
- A strong core means better posture, protection from injury, and a body that feels powerful and capable.
- Muscle is not just for aesthetics. It is your engine for mood, energy, memory, and mobility.

This is not about diets or shrinking yourself. It is about building strength that will carry you for life.

We can only offer this to a handful of girls each week. Once the spots are gone, they are gone.

👉 Book your Strength Assessment here → [Calendar Link]

With strength and pride,
Megan Brown
Head Coach, The Evolved All Female Gym

---

## Sequence 2: 20s & 30s

**Source PDF:** `20's & 30's Email Sequence - NNC.pdf`
**Voice:** Aspirational, confident, body-positive but not shy about aesthetics. "Glow-up" language. References boardroom, brunch, bedroom, dance floor.
**Anti-message framing:** "lose this" and "quick fix"
**Sign-off:** Megan Brown, Head Coach / Founder

### Email Schedule

| Day | Subject Line | SA CTA |
|-----|-------------|--------|
| 0 | Welcome to Your Glow-Up Era (It Starts Now) | Yes (body) |
| 1 | This Is About More Than Looking Good Naked (But Let's Start There) | Yes (P.S.) |
| 2 | Let's Find the Gap That's Holding Your Glow Back | — |
| 2b | *(See full text below)* | Yes (entire email) |
| 3 | No, You're Not Lazy. Here's the Real Reason You Keep Repeating the Same Sh*t. | — |
| 4 | Glow. Grow. Perform. But Only If You Get This Right. | — |
| 5 | Can't Sleep? Try These 10 Glow-Up Hacks Tonight | Yes (P.S.) |
| 6 | Every Meal Sends a Message. What's Yours Saying? | — |
| 7 | 10 Simple Food Fixes That Actually Make a Difference | Yes (P.S.) |
| 8 | Want to Look Stronger, Feel Better, and Stay Lean? Start Here. | — |
| 9 | The Truth About Growing Glutes (Hint: It's Not Pilates) | Yes (P.S.) |
| 10 | What's Worth Taking (And What's Just Hype) | — |
| 11 | The One Protein Powder I Actually Recommend | — |
| 12 | Creatine: The Cheapest Brain + Body Boost There Is | Yes (P.S. + button) — SA booking |
| 13 | The Oil That Helps You Think Clearer, Feel Calmer & Move Better | — |
| 14 | That Time I Lifted More Than I Ever Had… and Changed My Brain | — |
| 15 | What to Do When You Miss a Workout (Or Five) | Yes (P.S.) — SA booking |
| 16 | Carbs Aren't the Enemy. You Just Need to Time Them Right | — |
| 17 | The Fat-Burning, Brain Building Hack That Feels Like… Living? | — |
| 18 | Hormones, Fatigue, Cravings… Here's What's Actually Going On | — |
| 19 | Feeling Off? It Might Be Stress in Disguise | — |
| 20 | If You Do This One Thing Weekly, You'll Keep Going | — |
| 21 | Want to Change Long-Term? Start With Who You Are | Yes (P.S. + button) — SA booking |
| 22 | Your 20-Minute Reset That Changes the Whole Week | — |
| 23 | Don't Just Train Hard. Train Smart | — |
| 24 | Want to Know If It's Working? Track This Instead | Yes (P.S.) — soft reply CTA |
| 25 | How to Tell If You're Winning… Without a Mirror | — |
| 26 | Don't Burn Out. Build in These Breaks Instead | — |
| 27 | Muscle Gives You More Than Just a Better Body | Yes (P.S.) |
| 28 | She Didn't Just Level Up. She Became Her. | — |

| 29 | This Wasn't a Reset. This Was a Rebuild | — |
| 30 | This Is Chapter One of Your Strongest Season Yet | Yes (button) — SA booking only |

### Day 2b SA CTA — 20s & 30s

Hi {{contact.first_name}},

Truthfully, we really dislike the fitness industry. It is full of "lose this" and "quick fix" messaging.

That is not what we are about.

We would rather focus on what you will gain. In your 20s and 30s, strength is not just about getting "toned." It is about shaping a body you are proud of, building the confidence to own every room you walk into, and giving yourself the energy to take on anything life throws at you.

That is why we created our Strength Assessment.

Here is what you will get when you book one:

**Where Are We Starting?**
A short, guided strength and movement check-up. No pressure, no judgement.

**What Is Your Next Step?**
Personalised tips on improving strength, energy, and body composition.

**Do You Have Concerns?**
Bring them with you. We will give expert answers to your training or body change questions.

**Can We Fast Track This?**
Yes. You will leave with a game plan for moving forward with clarity, whether you join us or not.

And here is why it matters:

- Women begin losing muscle around age 30, up to 250g per year. Without strength training, this decline accelerates. If you are not building it, you are losing it.
- Women who can split squat 50% of their body weight for 10 reps build visible shape, real athletic endurance, and the body confidence to own every room they walk into.
- Women who can carry 75% of their body weight for 1 minute show resilience and calmness under pressure, inside and outside the gym.
- A toned waist and strong core means you will look and feel amazing, in nightwear or without, and have the endurance to savor every moment.
- Muscle is not just for aesthetics. It is your engine for energy, mood, memory, and mobility. It is the secret behind ageing powerfully, not passively.

This is not about a 6-week challenge. It is about building the body and confidence you get to carry for life.

We can only offer this to a handful of women each week. Once the spots are gone, they are gone.

👉 Book your Strength Assessment here → [Calendar Link]

With strength and pride,
Megan Brown
Head Coach, The Evolved All Female Gym

---

## Sequence 3: Planning / Pregnant / Post-Partum

**Source PDF:** `Planning, Pregnant & Post-Partum Email Sequence - NNC.pdf`
**Voice:** Warm, maternal, empowering. Acknowledges the specific physical and emotional context of each sub-stage. References prams, pelvic floor, babies/toddlers. "Queen" framing.
**Anti-message framing:** "lose this" and "bounce back"
**Sign-off:** Megan Brown, Head Coach / Founder

**Note:** Day 1 has THREE separate versions (one per sub-stage), not one generic email.

### Email Schedule

| Day | Subject Line | SA CTA |
|-----|-------------|--------|
| 0 | You Just Stepped Into Your Power, Queen | Yes (body) |
| 1a (Planning) | You Don't Have to Pause Your Life to Create One | Yes (P.S.) |
| 1b (Pregnant) | Pregnancy Doesn't Have to Mean "Pause" | Yes (P.S.) |
| 1c (Postpartum) | You Didn't Break. You Evolved. | Yes (P.S.) |
| 2 | Let's Find the Gap That's Holding Your Glow Back | — |
| 2b | *(See full text below)* | Yes (entire email) |
| 3 | No, You're Not Lazy. You're Wired This Way But Here's How to Change It | — |
| 4 | Glow. Grow. Perform. But Only If You Get This Right. | — |
| 5 | Can't Sleep? Try These 10 Glow-Up Hacks Tonight | Yes (P.S.) |
| 6 | Every Meal Sends a Message. What's Yours Saying? | — |
| 7 | 10 Simple Food Fixes That Actually Make a Difference | Yes (P.S.) |
| 8 | Want to Look Stronger, Feel Better, and Stay Lean? Start Here. | — |
| 9 | Stronger in Pregnancy, Safer in Motherhood | Yes (P.S.) |
| 10 | What's Worth Taking (And What's Just Hype) | — |
| 11 | The One Protein Powder I Actually Recommend | — |
| 12 | Creatine: The Cheapest Brain + Body Boost There Is | Yes (P.S. + button) — SA booking |
| 13 | The Oil That Helps You Think Clearer, Feel Calmer & Move Better | — |
| 14 | That Time I Lifted More Than I Ever Had… and Changed My Brain | — |
| 15 | What to Do When You Miss a Workout (Or Five) | Yes (P.S.) — SA booking |
| 16 | Carbs Aren't the Enemy. You Just Need to Time Them Right | — |
| 17 | The Power of NEAT *(pregnancy/postpartum framing — includes BDNF crosses placenta note)* | — |
| 18 | Feel Off This Week? It Might Be Hormones Talking | — |
| 19 | Feeling Off? It Might Be Stress in Disguise | — |
| 20 | If You Do This One Thing Weekly, You'll Keep Going | Yes (P.S.) — soft reply CTA ("Family Meeting" ritual) |
| 21 | Want to Change Long-Term? Start With Who You Are | Yes (P.S. + button) — SA booking |
| 22 | Your 20-Minute Reset That Changes the Whole Week | — |
| 23 | Don't Just Train Hard. Train Smart | — |
| 24 | Want to Know If It's Working? Track This Instead | Yes (P.S.) — soft reply CTA |
| 25 | How to Tell If You're Winning… Without a Mirror | — |
| 26 | The Recovery Window Strategy | — |

| 27 | Muscle = Glow, Power, and Kid-Chasing Energy | Yes (P.S.) |
| 28 | She Started Tired. She's Finishing Powerful. | — |
| 29 | This Wasn't a Reset. This Was a Rebuild | — |
| 30 | This Is Chapter One of Your Strongest Season Yet | Yes (button) — SA booking only |

### Day 2b SA CTA — Planning / Pregnant / Post-Partum

Hi {{contact.first_name}},

Truthfully, we really dislike the fitness industry. It is full of "lose this" and "bounce back" messaging.

That is not what we are about.

We would rather focus on what you will gain. In pregnancy and postpartum, strength is not about punishment or restriction.

It is about supporting your body through change, rebuilding confidence, and creating the energy to thrive in this season.

That is why we created our Strength Assessment.

Here is what you will get when you book one:

**Where Are We Starting?**
A short, guided strength and movement check-up. No pressure, no judgement.

**What Is Your Next Step?**
Personalised tips on safe training, posture, and rebuilding strength you can trust.

**Do You Have Concerns?**
Bring them with you. We will give expert answers to your questions about training, recovery, or body changes.

**Can We Fast Track This?**
Yes. You will leave with a game plan for moving forward with clarity, whether you join us or not.

And here is why it matters:

- Women begin losing muscle around age 30, up to 250g per year. In pregnancy and postpartum this loss can accelerate if you are not building it. If you are not building it, you are losing it.
- Women who can split squat 50% of their body weight for 10 reps have the leg strength to ease childbirth, support recovery, and return to exercise with confidence.
- Women who can carry 75% of their body weight for 1 minute have the strength needed to handle groceries, prams, and little ones who insist on being carried without missing a beat.
- With a solid core and pelvic floor you will lift babies and prams safely, reduce back pain, and have more energy for play and daily life.
- Muscle is not just aesthetics. It is your engine for mood, memory, energy, and mobility.

This is not about bouncing back. It is about rebuilding your body to be stronger than before.

We can only offer this to a handful of women each week. Once the spots are gone, they are gone.

👉 Book your Strength Assessment here → [Calendar Link]

For Strong Women!
Megan Brown
Head Coach, The Evolved All Female Gym

---

## Sequence 4: Perimenopause

**Source PDF:** `Perimenopause Email Sequence - NNC.pdf`
**Voice:** Direct, science-informed, hormone-aware. References brain fog, fatigue, stubborn weight, irregular cycle. "Glow" language used. Perimenopause-specific clinical context in key emails.
**Anti-message framing:** "lose this" and "fat loss"
**Sign-off:** Megan Brown, Head Coach / Founder

### Email Schedule

| Day | Subject Line | SA CTA |
|-----|-------------|--------|
| 0 | Welcome to Your Strongest Season Yet | Yes (body) |
| 1 | The Real Reason You Haven't Seen the Results You Deserve | Yes (P.S.) |
| 2 | Find the Gap That's Holding Your Power Back | — |
| 2b | *(See full text below)* | Yes (entire email) |
| 3 | No, You're Not Lazy. Your Brain's Just in a Loop. | — |
| 4 | Cravings? Fog? Stubborn Fat? It Starts with This. | — |
| 5 | Struggling to Sleep? Here's How to Glow Tomorrow | Yes (P.S.) |
| 6 | Every Meal Sends a Signal Is Yours Helping or Hurting? | — |
| 7 | 10 Tiny Nutrition Tweaks = Big Body Shifts | Yes (P.S.) |
| 8 | This Is the Workout Women Over 35 Need Most | — |
| 9 | Why Pilates Alone Won't Carry You Through Perimenopause | Yes (P.S.) |
| 10 | Supplements That Actually Work No Detox Teas, Promise | — |
| 11 | The Easiest Way to Get the Protein Your Changing Body Needs | — |
| 12 | The One Supplement Every Perimenopausal Woman Should Know About | Yes (P.S. + button) — SA booking |
| 13 | Foggy Brain? Sore Joints? This Might Be Why. | — |
| 14 | One Lift. One Shift. One New You. | — |
| 15 | The Bare-Minimum Plan for When Life Implodes | Yes (P.S.) — SA booking |
| 16 | Carbs Aren't the Problem. When You Eat Them Is. | — |
| 17 | Want to Burn More Fat Without More Stress? Start Here. | — |
| 18 | Irregular Periods? Your Body Isn't Broken It's Signaling. | — |
| 19 | Bloated? Tired? Foggy? It Might Be Stress in Disguise | — |
| 20 | One Simple Weekly Ritual That Changes Everything | Yes (P.S.) — soft reply CTA ("Family Meeting" ritual) |
| 21 | Long-Term Results Start With Who You Say You Are | Yes (P.S. + button) — SA booking |
| 22 | 20 Minutes. One Weekly Ritual. Total Control. | — |
| 23 | Still Sore Days After Training? Let's Talk. | — |
| 24 | Still Weighing Yourself? Read This First. | Yes (P.S.) — soft reply CTA |
| 25 | This 5-Point Morning Check Tells You Everything | — |
| 26 | Feeling Flat After Progress? This Is Why. | — |
| 27 | What Muscle Really Does for Women in Perimenopause | Yes (P.S.) |
| 28 | You Started Tired. You're Finishing Unstoppable. | — |
| 29 | This Wasn't a Reset. It Was a Rebuild. | — |
| 30 | This Is Chapter One of Your Strongest Season Yet | Yes (button) — SA booking only |

### Day 2b SA CTA — Perimenopause

Hi {{contact.first_name}},

Truthfully, we really dislike the fitness industry. It is full of "lose this" and "fat loss" messaging.

That is not what we are about.

We would rather focus on what you will gain. During perimenopause, strength is not just about looking toned. It is about easing symptoms, protecting your bones, and giving you the energy and confidence to feel like yourself again.

That is why we created our Strength Assessment.

Here is what you will get when you book one:

**Where Are We Starting?**
A short, guided strength and movement check-up. No pressure, no judgement.

**What Is Your Next Step?**
Personalised tips on improving energy, posture, and physical confidence.

**Do You Have Concerns?**
Bring them with you. We will give expert answers to your training or body change questions.

**Can We Fast Track This?**
Yes. You will leave with a game plan for moving forward with clarity, whether you join us or not.

And here is why it matters:

- Women begin losing muscle around age 30, up to 250g per year. In perimenopause this decline accelerates, and symptoms like fatigue, brain fog, and stubborn weight gain become harder to ignore.
- Women who can split squat 50% of their body weight for 10 reps have stronger hips, knees, and ankles, and dramatically lower their risk of injury and osteoporosis.
- Women who can carry 75% of their body weight for 1 minute are far more likely to move through perimenopause with energy, independence, and confidence.
- Strength training supports your hormones, sharpens your mood, and builds the muscle that protects your body long after this season has passed.

This is not about aesthetics. It is about moving through perimenopause with power, not passively.

We can only offer this to a handful of women each week. Once the spots are gone, they are gone.

👉 Book your Strength Assessment here → [Calendar Link]

With strength and pride,
Megan Brown
Head Coach, The Evolved All Female Gym

---

## Sequence 5: Post Menopause

**Source PDF:** `Post Menopause Email Sequence - NNC.pdf`
**Voice:** Sophisticated, longevity-focused, evidence-led. References independence, dementia risk, bone density, grandkids. More clinical depth than other sequences. Dr. Peter Attia referenced in Day 9.
**Anti-message framing:** "lose this" and "fat loss"
**Sign-off:** Megan Brown, Head Coach / Founder

### Email Schedule

| Day | Subject Line | SA CTA |
|-----|-------------|--------|
| 0 | Your Stronger Future Starts Here | Yes (body) |
| 1 | Let's Talk Looking Good Naked (And Why It Still Matters) | Yes (P.S.) |
| 2 | Find the Gap That's Holding Your Power Back | — |
| 2b | *(See full text below)* | Yes (entire email) |
| 3 | No, You're Not Lazy. Your Brain's Just in a Loop | — |
| 4 | Cravings, Fog, Belly Fat? Start Here First. | — |
| 5 | Can't Sleep? Try These 10 Glow-Up Hacks Tonight | Yes (P.S.) |
| 6 | Every Meal Sends a Signal Is Yours Helping or Hurting? | — |
| 7 | 10 Tiny Nutrition Tweaks = Big Body Shifts | Yes (P.S.) |
| 8 | The Workout Women Over 40 Need Most | — |
| 9 | Why Pilates Isn't Enough After Menopause (And What To Do Instead) | Yes (P.S.) |
| 10 | Supplements That Actually Work No Detox Teas, Promise | — |
| 11 | My #1 Supplement for Busy, Strong Women Post Menopause | — |
| 12 | The Cheapest, Smartest Supplement for Post Menopausal Women | Yes (P.S. + button) — SA booking |
| 13 | Foggy, Sore, or Just Off? This Might Be Why | — |
| 14 | One Lift. One Shift. One New You. | — |
| 15 | The Bare-Minimum Plan for Maximum Results | Yes (P.S.) — SA booking |
| 16 | Carbs Aren't the Problem. When You Eat Them Is. | — |
| 17 | Want to Burn More Fat Without Extra Gym Time? Do This. | — |
| 18 | Postmenopause Isn't the End: It's a Shift | — |
| 19 | Bloated, Tired, Off? It Might Be Hidden Stress | — |
| 20 | The 5-Minute Weekly Ritual That Changes Everything | Yes (P.S.) — soft reply CTA ("Family Meeting" ritual) |
| 21 | Long-Term Results Start With Who You Say You Are | Yes (P.S. + button) — SA booking |
| 22 | 20 Minutes. One Weekly Ritual. Total Control. | — |
| 23 | You're Not Here to Punish Your Body. You're Here to Build It. | — |
| 24 | Strong Is a Feeling Not a Number | Yes (P.S.) — soft reply CTA |
| 25 | This 5-Point Morning Check Tells You Everything | — |
| 26 | Don't Burn Out. Build in These Breaks Instead | — |
| 27 | What Muscle Actually Does for Women Post Menopause | Yes (P.S.) |
| 28 | You Started Tired. You're Finishing Unstoppable. | — |
| 29 | This Wasn't a Reset. It Was a Rebuild. | — |
| 30 | This Is Chapter One of Your Strongest Season Yet | Yes (button) — SA booking only |

### Day 2b SA CTA — Post Menopause

Hi {{contact.first_name}},

Truthfully, we really dislike the fitness industry. It is full of "lose this" and "fat loss" messaging.

That is not what we are about.

We would rather focus on what you will gain. After menopause, your strength is not just about looking toned. It is about protecting your bones, your brain, and your independence for decades to come.

That is why we created our Strength Assessment.

Here is what you will get when you book one:

**Where Are We Starting?**
A short, guided strength and movement check-up. No pressure, no judgement.

**What Is Your Next Step?**
Personalised tips on improving energy, posture, and physical confidence.

**Do You Have Concerns?**
Bring them with you. We will give expert answers to your training or body change questions.

**Can We Fast Track This?**
Yes. You will leave with a game plan for moving forward with clarity, whether you join us or not.

And here is why it matters:

- Women begin losing muscle around age 30, up to 250g per year. After menopause, this silent decline accelerates. If you are not building it, you are losing it.
- Women who can split squat 50% of their body weight for 10 reps have stronger hips, knees, and ankles, and dramatically lower their risk of osteoporosis.
- Women who can carry 75% of their body weight for 1 minute are far more likely to stay mobile, independent, and free of frailty later in life.
- Strength training is linked to a lower risk of dementia, thanks to improved blood flow and healthier hormones.

This is not about aesthetics. It is about ageing powerfully, not passively.

We can only offer this to a handful of women each week. Once the spots are gone, they are gone.

👉 Book your Strength Assessment here → [Calendar Link]

For Strong Women!
Megan Brown
Head Coach, The Evolved All Female Gym

---

## Day 30 — 20s & 30s

**Subject:** This Is Chapter One of Your Strongest Season Yet
**Distinguishing text:** "the woman you already are"; "And you? You're one of them now"; no hormone references
**CTA type:** Button — SA booking only

---

Hey {{contact.first_name}},

You made it.

30 days.

But this? This isn't the finish line.

It's the first page of your next chapter.

What's ahead?

A stronger body

A sharper, calmer mind

A lifestyle that supports you, not restricts you

A relationship with food that feels grounded not guilt-ridden

An identity rooted in strength, not shame

You don't need a new plan tomorrow.

You just need to keep showing up like the woman you already are.

Today's action:

Save this line somewhere your wallpaper, your mirror, your notes app:

"I don't wait for permission anymore. I just keep evolving."

Because that's what strong girls do.

And you? You're one of them now.

You've built something no scale can measure.

No one can take this from you.

You are Evolved.

And this is only the beginning.

Megan Brown

P.S. — You have made it through 30 days. That says a lot about who you are.

You showed up. You reflected. You started to shift. Even if it was just one small step at a time.

The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away knowing precisely what to focus on and what is possible from here.

[Book My Free Strength Assessment]

---

## Day 30 — Post Menopause

**Subject:** This Is Chapter One of Your Strongest Season Yet
**Distinguishing text:** "Thirty days. One commitment."; "steadier. Sharper. Stronger."; "a nervous system that can finally exhale"; hormone-aware without "queen" framing
**CTA type:** Button — SA booking only

---

Hey {{contact.first_name}},

You did it.

Thirty days. One commitment.

But this isn't the end.

This is chapter one.

You haven't just completed a program.

You've built a new foundation.

What comes next?

A body that holds strength instead of tension

A mind that stays sharp and calm through hormone shifts

A routine that fits your life instead of fights against it

A nervous system that can finally exhale

A relationship with food that fuels your health not your guilt

You don't need a brand-new plan tomorrow.

You just need to keep showing up like the woman you've become.

Today's action:

Write this down and keep it somewhere visible:

"I don't wait for permission anymore. I just keep evolving."

You are not who you were 30 days ago.

You're steadier. Sharper. Stronger.

You're Evolved.

And your next season?

It's going to be your strongest one yet.

With you every step,

Megan Brown
The Evolved

P.S. — You have made it through 30 days. That says a lot about who you are.

You showed up. You reflected. You started to shift. Even if it was just one small step at a time.

The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away with a clear picture of your bone health, muscle, and what to focus on for the next season.

[Book My Free Strength Assessment]

---

## Day 30 — Perimenopause

**Subject:** This Is Chapter One of Your Strongest Season Yet
**Distinguishing text:** "Hey queen"; "stop fading and start rising"; "a rhythm that works with your hormones"; "respected your biology"
**CTA type:** Button — SA booking only

---

Hey queen,

You did it.

30 days of showing up for yourself.

But this?

This isn't the end.

It's the beginning of the season where you stop fading and start rising.

You've laid the foundation.

Now you get to build the life, the body, and the mindset that matches the woman you're becoming.

What's ahead for you?

A stronger, more capable body with muscle that protects, empowers, and carries you

A calmer, clearer mind less fog, more focus

A rhythm that works with your hormones, not against them

A relationship with food that feels like fuel, not fear or shame

An identity rooted in strength, not the pressure to shrink

You didn't need to be "fixed."

You needed a reset that respected your biology and backed your goals.

You've done that. And more.

You don't need to start over tomorrow.

You don't need a drastic new plan.

You just need to keep showing up as the woman who now knows:

"I don't wait for permission anymore. I just keep evolving."

So save that line.

Put it on your mirror.

Your journal.

Your wallpaper.

Let it remind you:

You're not going back.

You're building forward.

You're not who you were 30 days ago.

You are Evolved.

And this?

This is just the beginning of your most powerful chapter yet.

With you always,

Megan Brown
The Evolved

P.S. — You have made it through 30 days. That says a lot about who you are.

You showed up. You reflected. You started to shift. Even if it was just one small step at a time.

The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away with a clear understanding of where your body is and exactly what it needs in this season.

[Book My Free Strength Assessment]

---

## Day 30 — Teen

**Subject:** This Is Chapter One of Your Strongest Season Yet
**Distinguishing text:** "the girl you've already proven you are"; "strong girls do"; "We're proud of you"
**CTA type:** Button — SA booking only

---

Hey {{contact.first_name}},

You made it.

But this? It's not the finish line.

It's the first page of your strongest season yet.

What's ahead?

A stronger body

A calmer mind

A new way of living that's simple, powerful, and yours

A relationship with food and training that isn't based on rules or guilt

A new identity one you're proud of

You don't need a brand-new plan tomorrow.

You just need to keep showing up like the girl you've already proven you are.

Today's action:

Save this somewhere:

Your phone wallpaper

Your mirror

Your voice

"I don't wait for permission anymore. I just keep evolving."

Because that's what strong girls do.

You've built something no scale can measure.

And no one can take it from you.

We're proud of you.

But more importantly you should be proud of yourself.

You're Evolved now.

And this is only the beginning.

Megan Brown

P.S. — You have made it through 30 days. That says a lot about who you are.

You showed up. You reflected. You started to shift. Even if it was just one small step at a time.

The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment takes less than an hour. You will walk away knowing precisely what your body needs and what is possible from here.

[Book My Free Strength Assessment]

---

## Day 30 — Planning / Pregnant / Post-Partum

**Subject:** This Is Chapter One of Your Strongest Season Yet
**Distinguishing text:** "preparing for pregnancy, carrying life, or slowly rebuilding after birth"; "Women who build, not bounce back"
**CTA type:** Button — SA booking only

---

Hey {{contact.first_name}},

You made it.

30 days.

But this?

This isn't the finish line.

It's your launchpad.

You didn't just follow a program.

You reshaped the way you care for your body in one of the most demanding and powerful seasons of your life.

Here's what you've built:

A stronger body whether you're preparing for pregnancy, carrying life, or slowly rebuilding after birth

A sharper, clearer mind because you've been feeding and training for focus, not fog

Health habits that serve you not restrict you or punish you

A relationship with food and movement that feels steady, not extreme

An identity rooted in strength and self-trust not shame or pressure

You don't need to overhaul everything tomorrow.

You don't need a "next plan."

You just need to keep showing up as the woman you've already become.

Today's action:
Save this somewhere your mirror, lock screen, or notes app:

"I don't wait for permission anymore. I just keep evolving."

Because that's what strong women do.

Women who listen to their body.

Women who honour the seasons.

Women who build, not bounce back.

And you?

You are Evolved.

This is only the beginning.

Megan Brown

P.S. — You have made it through 30 days. That says a lot about who you are.

You showed up. You reflected. You started to shift. Even if it was just one small step at a time.

The most natural next step is to come in and see exactly where your strength sits now. The free Strength Assessment is flexible, safe for every stage, and built around you. You will walk out with a clear picture and a personalised next step.

[Book My Free Strength Assessment]

---

## Mid-Sequence Emails with SA CTAs

*These emails contain SA CTAs not captured in the original audit. Documented as they are confirmed from GHL.*

---

## Day 12 P.S. Copy — New SA CTA (Replaces Seminar Replay)

*Updated 2026-07-17. Replaces the seminar replay P.S. across all 5 sequences. Button format: "Book Your Free Strength Assessment" → `https://www.theevolvedgym.com.au/strength-assessment`*

### Day 12 P.S. — Teen

P.S. — Creatine is one piece of the puzzle. The other piece is knowing exactly what your training should look like right now.

That is what the free Strength Assessment is for. Come in, see where you are starting, and walk out with a clear next step.

[Book Your Free Strength Assessment]

---

### Day 12 P.S. — 20s & 30s

P.S. — Creatine will help your training. But only if your training is pointed in the right direction.

Book a free Strength Assessment and we will show you exactly what to focus on for your body and your goals.

[Book Your Free Strength Assessment]

---

### Day 12 P.S. — Planning / Pregnant / Post-Partum

P.S. — The right supplements support your training. The right training supports everything else.

Book a free Strength Assessment and we will map out exactly what safe, effective training looks like for your stage.

[Book Your Free Strength Assessment]

---

### Day 12 P.S. — Perimenopause

P.S. — Creatine is one of the best tools in the perimenopausal toolkit. Knowing how to train is the other.

Book a free Strength Assessment and we will show you exactly what your training should look like right now.

[Book Your Free Strength Assessment]

---

### Day 12 P.S. — Post Menopause

P.S. — Creatine matters most when your training is giving it something to work with.

Book a free Strength Assessment and we will map out exactly what your training should focus on for bone density, muscle, and longevity.

[Book Your Free Strength Assessment]

---

### Day 27 — Post Menopause

**Subject:** What Muscle Actually Does for Women Post Menopause
**CTA type:** P.S. — SA booking

---

Yes, muscle looks good.

But after menopause? That's only the surface.

The real power of muscle is what it does inside your body where ageing and hormones try to take the biggest toll.

Here's what strength training gives you beyond appearance:

It helps your body burn more energy at rest

It stabilises your joints, spine, and bones to reduce injury and fracture risk

It slows aging at the cellular level by protecting your lean tissue

It supports hormone health, brain clarity, and emotional balance

It keeps you agile, steady, and able to do the things you love with confidence

Muscle is not just about definition. It's about independence.

It means fewer injuries.

Less fear of falling.

More strength to carry your own groceries, keep up with the grandkids, and stay active long into the future.

Actually enjoy travelling and sight seeing without being riddled with pain

Say yes to bowling with your girlfriends (real example from one of our members)

This month, you didn't just show up for workouts.

You trained with purpose.

And every rep you've done is protecting your future self.

You're not slowing down.

You're just getting powerful.

Megan Brown
The Evolved

P.S. — If you've been thinking "maybe it's too late to change" let this be your proof that it's not.

The free Strength Assessment is built to meet you where you're at. No judgment. Just real support and a smart, strength-based plan.
👉 [Book Your Free Strength Assessment]

---

### Day 27 — Perimenopause

**Subject:** What Muscle Really Does for Women in Perimenopause
**CTA type:** P.S. — SA booking

---

Muscle looks great no question.

Strong arms, a tighter waist, legs that carry you (and five grocery bags) like a boss.

But in perimenopause, muscle becomes so much more than a "look."

It's your shield.

Your support system.

Your hormonal ally.

Here's what building muscle actually gives women in their 40s and beyond:

Burns fat, even at rest & especially as metabolism slows

Protects your joints, spine, and bones (goodbye, osteoporosis risk)

Slows aging at the cellular level, think stronger skin, better brain

Supports hormone balance and eases mood swings, brain fog, and fatigue

Improves sleep quality and stress resilience

Muscle isn't just about looking good.

It's about living well with more energy, more ease, and less fear of physical decline.

It gives you the strength to carry your kids, lift your suitcase, hold a yoga pose, or reclaim your body when it feels unfamiliar.

This month, every rep you did was more than exercise.

It was a vote for your future.

You didn't just train.

You built resilience.

You built freedom.

You built the version of you who handles whatever comes next, strong, steady, and unshakeable.

And you're just getting started.

Megan Brown
The Evolved

P.S. — If you've been nodding along, thinking "this sounds like me"… now's your moment to act.

This free Strength Assessment is where it all starts, no pressure, just clarity, support, and a plan that works with your body.
👉 [Book Your Free Strength Assessment]

---

### Day 21 — Teen

**Subject:** Want to Change Long-Term? Start With Who You Are
**CTA type:** P.S. + button — SA booking ("Met Class Assessment")
**Note:** ATAR/Year 12 framing; "strong girl" identity language; brain/focus emphasis alongside physical

---

Hey {{contact.first_name}},

Most girls try to change with willpower alone.

It works… for a little while.

But then school gets hectic.

Assignments pile up.

Exams creep closer.

You're tired.

You're stressed about your ATAR.

And suddenly, motivation just... fades.

That's normal.

But there's a smarter way to stay consistent even when life gets crazy.

Anchor your habits in your identity.

Instead of saying:

"I just want to look better."

Say:

"I'm the kind of girl who trains 3x/week to fuel my body and my brain."

Instead of saying:

"I need to sleep more."

Say:

"I'm the kind of girl who protects her energy, so she can crush her goals."

It's not about motivation anymore.

It's about becoming someone new, one smart choice at a time.

Try this today:

"I'm the kind of girl who builds strength, focus, and resilience."

Because every time you show up for a workout, for yourself, for your goals you're proving it's true.

Your body will get stronger.

Your brain will get sharper.

And your confidence will start carrying you through the tough days like exams, sports, and everything after.

You're building a foundation now that will serve you way beyond Year 12.

Megan Brown

P.S. — The strongest version of you does not wait. She books the thing.

Your free Strength Assessment is where it starts. Come in, see where you are at, and get a clear next step.

[Book Your Free Strength Assessment]

---

### Day 21 — 20s & 30s

**Subject:** Want to Change Long-Term? Start With Who You Are
**CTA type:** P.S. + button — SA booking
**Note:** Iced coffee/assignment framing; "woman" language (vs Teen "girl"); burnout framing specific to this age group

---

Willpower is cute… until it isn't.

Until the assignment is due.

Until work dumps 47 emails on your brain.

Until you're running on iced coffee and anxiety.

Trying to "just push harder" when life's already heavy?

It's a recipe for burnout, not breakthroughs.

Here's the smarter way:

Identity over willpower.

You don't need to force yourself harder.

You need to become someone different, bit by bit.

Try this:

Instead of "I want to look better."
Try "I'm the kind of woman who trains 3x/week and fuels her body."

Instead of "I need to sleep more."
Try "I'm the kind of woman who protects her energy and recovery."

This isn't manifestation fluff.

It's neuroscience.

Your brain rewires faster when your habits match who you believe you are.

So here's your new identity:

"I'm the kind of woman who builds strength, confidence, and consistency."

Say it.

Act like it.

Grow into it.

Because she's already inside you.

Waiting.

Let's bring her out.

Megan Brown
The Evolved

P.S. — Identity follows action. If you see yourself as someone who trains seriously, this is your next move.

Book your free Strength Assessment and we will give you a clear picture of where you are and what to focus on.

[Book Your Free Strength Assessment]

---

### Day 21 — Planning / Pregnant / Post-Partum

**Subject:** Want to Change Long-Term? Start With Who You Are
**CTA type:** P.S. + button — SA booking
**Note:** Teething/reheating coffee framing; adapts identity script across all three sub-stages (fertility, pregnancy, postpartum)

---

Hey {{contact.first_name}},

Willpower works…

Until the baby's teething, your brain is fried, and the only quiet moment is while you're reheating your coffee for the third time.

Suddenly, "just try harder" doesn't cut it.

So let's stop relying on motivation to carry you through this season.

Let's build something that actually sticks.

It's called identity.

Instead of trying to force the habit, you become the kind of woman who lives it.

Try this shift:

Instead of "I want to look better."
Try "I'm the kind of woman who trains 3x/week and fuels her body."

Instead of "I need to sleep more."
Try "I'm the kind of woman who protects her recovery because her energy is sacred."

This isn't fluff.

It's neuroscience. Your brain builds habits faster when they align with your self-image.

So here's your identity for today:

"I'm the kind of woman who builds strength, confidence, and consistency."

Even if you're trying to fall pregnant.

Even if you're pregnant and exhausted.

Even if your body still doesn't quite feel like yours yet after birth.

Say it. Act like it. Repeat it.

She's already in you.

You're just activating her.

Megan Brown

P.S. — The strongest version of you is already in there. The Strength Assessment is just the moment she steps forward.

Come in, see where you are starting, and walk out with a plan built around your body and your stage.

[Book Your Free Strength Assessment]

---

### Day 21 — Perimenopause

**Subject:** Long-Term Results Start With Who You Say You Are
**CTA type:** P.S. + button — SA booking
**Note:** Cycle/energy fluctuation framing; "cycle gets weird" language; otherwise mirrors Post-Meno identity/neuroscience structure

---

Hey {{contact.first_name}},

Let's be honest willpower?

It's great... until your energy tanks, your cycle gets weird, or work and family chaos hits like a freight train.

What works better?

Identity.

You don't need to "try harder."

You need a new default setting.

Try this:

Instead of "I want to look better."
Try "I'm the kind of woman who trains consistently and nourishes her strength."

Instead of "I need to fix my sleep."
Try "I'm the kind of woman who protects her recovery because her goals depend on it."

This isn't just motivation talk.

It's neuroscience.

Your brain fast-tracks habits when they match your self-image.

So let's upgrade the script:

"I'm the woman who builds muscle, protects her hormones, and leads herself with strength."

Say it. Repeat it. Live it.

Because she's not in the distance she's already inside you.

Megan Brown
The Evolved

P.S. — You have been building the identity. Now take the action that matches it.

Book your free Strength Assessment and we will show you exactly where your strength sits right now and what to do with it.

[Book Your Free Strength Assessment]

---

### Day 21 — Post Menopause

**Subject:** Long-Term Results Start With Who You Say You Are
**CTA type:** P.S. + button — SA booking
**Note:** Identity/neuroscience framing; hot flush/brain fog language; "age powerfully" theme

---

Hey {{contact.first_name}},

Willpower works…

Until it doesn't.

Until the hot flush hits at 2am.

Until your energy crashes halfway through the day.

Until your body feels foreign, and your brain forgets what it walked into the room for.

That's when most women give up because they think they just need to try harder.

But what actually works long term?

Identity.

You don't need to push harder.

You need to shift who you believe you are.

Try this:

Not "I want to look better."

But, "I'm the kind of woman who lifts her bones and eats to fuel her future."

Not "I need to fix my sleep."

But, "I'm the kind of woman who protects her recovery — because she knows everything depends on it."

This isn't positive thinking.

It's neuroscience.

Your brain wires new habits faster when they match your self-image.

If you want to age powerfully, you need to become the kind of woman who acts that way before the results show up.

So say this to yourself today:

"I'm the woman who builds strength, protects her hormones, and leads herself with calm, grounded confidence."

Say it. Believe it. Then live in alignment with it.

Because that version of you?

She's not some future ideal.

She's already inside you waiting to lead.

Megan Brown
The Evolved

P.S. — You have spent 21 days becoming her. The Strength Assessment is how you meet her.

Come in, see where your strength sits, and walk away with a personalised plan for what comes next.

[Book Your Free Strength Assessment]

---

### Day 24 — Teen

**Subject:** Want to Know If It's Working? Track This Instead
**CTA type:** P.S. — soft reply CTA
**Note:** Sophie testimonial; "strong girls don't chase skinny"; no hormone content; teen-appropriate metrics

---

Hey {{contact.first_name}},

The number on the scale?

It doesn't tell you the full story.

You could gain 2kg of muscle and look way leaner.

You could lose 4kg but still feel weak or sluggish.

So here's what to focus on instead:

Performance markers.

Can you…

Squat more than last month?

Do 10 real push-ups?

Hang from a bar for a full minute?

Run a lap faster than before?

These signs mean your body is getting stronger, leaner, and more powerful even if the scale doesn't budge.

Strong girls don't chase skinny.

They chase progress they can feel.

Keep tracking what matters.

Your transformation is happening from the inside out.

Megan Brown

"I've never been a gym person before, but The Evolved has changed my mind. The classes are great as they are varied and challenging. Adjustments are made individually to suit our different bodies and different injuries." — Sophie

P.S. — If that sounds like your story… or the direction you want to go, just reply and tell me. I'll send you the first step we usually take with women just like Sophie.

---

### Day 24 — 20s & 30s

**Subject:** Want to Know If It's Working? Track This Instead
**CTA type:** P.S. — soft reply CTA
**Note:** Jess testimonial; aesthetic/performance framing for this age group — squat, push-ups, hang, lap time; "chase progress they can feel"

---

Hey {{contact.first_name}},

That number on the scale?

It's a moment.

It's not the full story.

Because you can gain 2kg of muscle and look tighter, stronger, and more athletic.

Or lose 4kg and still feel weak.

Here's what actually tells you the truth:

Performance markers.

Can you…

Squat more than last month?

Do 10 real push-ups?

Hang from a bar for 60 seconds?

Run a lap faster than before?

These are signs of strength. Of glow-up. Of real transformation.

Strong women don't chase skinny.

They chase progress they can feel.

Keep tracking what actually matters.

The scale is a tool. It's not your worth.

Megan Brown

"I used to try every workout under the sun, hoping for results. Now I lift 3x a week, eat properly, and my body finally reflects my effort." — Jess

P.S. — If that sounds like your story… or the direction you want to go, just reply and tell me. I'll send you the first step we usually take with women just like Jess.

---

### Day 24 — Planning / Pregnant / Post-Partum

**Subject:** Want to Know If It's Working? Track This Instead
**CTA type:** P.S. — soft reply CTA; "just reply and tell me, I'll send you the first step"
**Note:** Kerri-Lee testimonial (pregnancy, diabetes, 10kg post-baby); postpartum-specific metrics — car seat, toddler carry, "building trust with my body again"

---

Hey {{contact.first_name}},

Let's talk about the scale.

That number?

It's a snapshot, not a story.

It doesn't know what your body's been through.

It doesn't measure your strength, your mood, your sleep, your sanity.

You could gain 2kg of lean muscle and look tighter, stronger, more confident in your skin.

Or lose 4kg and still feel weak, foggy, or flat.

So what actually tells you it's working?

Performance.

Ask yourself:

Can I squat more than I could a month ago?

Can I hit 10 push-ups in a row — or even 3, with great form?

Can I hang from a bar for 60 seconds?

Can I carry the groceries, the car seat, or my toddler with ease?

Or maybe it's this:

I feel clearer.

I sleep deeper (even with interruptions).

I walk taller.

I'm building trust with my body again.

That's real progress.

That's your glow-up.

That's the truth, not just a number.

Especially when you're preparing for pregnancy, growing life, or coming back from birth…

The scale is the least interesting thing about you.

Your strength is telling a story.

Let it be louder than the number on the scale.

You're evolving.

Measure it accordingly.

Megan Brown

"Despite pregnancy, business, and a husband away, I made progress. I mastered meal prep, exercised, managed diabetes, and reached 37 weeks without pre-eclampsia. I lost 10kg post-baby and fit into a size 10 swimsuit by focusing on efficiency." — Kerri-Lee

P.S. — If that sounds like your story… or the direction you want to go, just reply and tell me. I'll send you the first step we usually take with women just like Kerri-Lee.

---

### Day 24 — Perimenopause

**Subject:** Still Weighing Yourself? Read This First.
**CTA type:** P.S. — soft reply CTA (not direct SA link); "just reply and tell me, I'll send you the first step"
**Note:** Tania testimonial; perimenopause-specific — hormone fluctuation, water retention, "old rules don't apply"; plank/hang bar metrics

---

Want to know if your training is working?

Stop staring at the scale.

Especially during perimenopause when hormones are shifting, water is fluctuating, and the old "rules" don't apply.

Here's the truth:

You can gain 2kg of muscle, lose fat, shrink your waistline, and feel 10x stronger…

…and the scale might not budge.

Or it might even go up.

Why? Because weight is just one number.

It doesn't tell the whole story, not about your strength, your mood, or your hormonal wins.

Here's what actually tells you you're getting stronger:

Can you lift heavier than last month?

Can you hold a plank longer without shaking?

Can you take the stairs without feeling puffed?

Can you hang from a bar for 30–60 seconds?

These are your real glow-up metrics.

They tell the story of a woman who's building strength, resilience, and control in a body that's changing.

Strong women don't chase smaller.

They chase power, performance, and progress they can feel.

Let the scale be one tiny footnote in your much bigger, bolder story.

You're not here to shrink.

You're here to evolve.

Megan Brown
The Evolved

"I thought weight gain and exhaustion were just part of getting older. This flipped everything, turns out I needed muscle, not more cardio." — Tania

P.S. — If that sounds like your story… or the direction you want to go, just reply and tell me. I'll send you the first step we usually take with women just like Tania.

---

### Day 24 — Post Menopause

**Subject:** Strong Is a Feeling Not a Number
**CTA type:** P.S. — soft reply CTA (not direct SA link); "just reply and tell me, I'll send you the first step"
**Note:** Karen testimonial (61yo, deadlift, sleep, confidence); scale vs. capability framing

---

Wondering if all this is actually working?

Here's the truth:

Don't just look at the scale.

Look at your life.

Because the scale doesn't measure what really matters, especially after menopause.

You could gain two kilograms of muscle, lose two kilograms of fat, and the number on the scale may not change.

But your shape, your posture, your strength, and your confidence?

Completely different.

The number on the scale is one data point.

It is not the full picture.

Try tracking these instead:

Can you lift heavier this month than you did last month

Do your clothes fit better, even if the weight is the same

Are stairs easier to climb

Is your sleep deeper, your energy steadier

Can you carry your shopping bags with less effort

Push a sled or move with more control in the gym

Do you feel stronger in your own skin, not just physically, but mentally

These are your real indicators of progress.

These are the signs that your training is working.

Strong women don't chase smaller.

They chase capability.

Resilience.

Independence.

They train for their future, not just a number.

Let the scale be background noise.

You've got far more powerful things to measure.

Megan Brown
The Evolved

"At 61, I can deadlift, sleep better, and feel more confident in my clothes than I did in my 40s. This isn't about age, it's about action." — Karen

P.S. — If that sounds like your story… or the direction you want to go, just reply and tell me. I'll send you the first step we usually take with women just like Karen.

---

### Day 27 — Teen

**Subject:** Muscle Gives You More Than Just a Better Body
**CTA type:** P.S. — SA booking
**Note:** Teen-specific framing — "teenage girls", confidence/sport/energy focus, no hormone content

---

Let's be honest, muscles look amazing.

It shapes your arms, tightens your core, and gives you that athletic glow.

But the real magic of muscle?

It's what it does on the inside.

Here's what no one tells teenage girls:

Muscle helps you burn fat, even when you're sitting

It protects your joints and spine from injury

It slows down aging and keeps your body strong

It balances hormones and helps handle stress better

More strength = more confidence.

More muscle = more freedom. More energy. More options.

You're not just building a body that looks strong.

You're building a body that can handle life.

This month, you've been laying the foundation.

Brick by brick. Rep by rep.

And the best part?

You're just getting started.

Megan Brown

P.S. — If you've been reading these and thinking "I want to feel strong, but I'm not sure where to start"… here's your next step.

The free Strength Assessment is a simple way to see where you're at, no pressure, no performance required.

Just support, guidance, and a clear next move.
👉 [Book Your Free Strength Assessment]

---

### Day 27 — Planning / Pregnant / Post-Partum

**Subject:** Muscle = Glow, Power, and Kid-Chasing Energy
**CTA type:** P.S. — SA booking
**Note:** Opens "Hey queen"; includes pelvic floor / postpartum-specific framing; "mum-safe" in P.S.

---

Hey queen,

Yes, muscles look good.

Strong glutes. Sculpted arms. A tighter waist that fits better in everything.

But the real flex?

Is what it's doing inside your body every single day.

And here's what most women were never taught (especially not during pregnancy, fertility prep, or postpartum):

Muscle burns fat even while you're sitting or feeding your baby

Protects your joints, spine, and core stability critical when you're carrying life or carrying everything

Slows aging, improves insulin sensitivity, and supports bone density

Regulates stress, stabilizes mood, and smooths hormonal shifts

Oh and stronger pelvic floor muscles? Better orgasms. (You're welcome.)

Muscle isn't vanity.

It's vitality.

It gives you:

Freedom to move how you want without pain or fear

Confidence to show up in your body, no matter the season

Security to eat without guilt

Strength to play now and 30 years from now

Pleasure that reminds you your body is more than just a checklist

You're not building a "bikini body."

You're building a resilient, radiant life-force one lift at a time.

And every rep this month?

It wasn't just for muscle.

It was for mood, metabolism, mobility… and yes, better moments in the bedroom too.

You're not just stronger.

You're more powerful, more playful, and more you.

Megan Brown

P.S. — If you've been following along while juggling everything else, you're doing amazing.

If you're ready to take one gentle, empowering step toward feeling strong again, book your free Strength Assessment today.
It's flexible, mum-safe, and built around you.
👉 [Book Your Free Strength Assessment]

---

### Day 27 — 20s & 30s

**Subject:** Muscle Gives You More Than Just a Better Body
**CTA type:** P.S. — SA booking

---

Hey {{contact.first_name}},

Yeah, muscle looks insane: sculpted arms, tighter waist, stronger thighs.

But the real flex?

It's what muscle does for you on the inside.

Here's what no one teaches us growing up:

Muscle burns fat, even when you're just chilling

It protects your joints, spine, and posture

It balances your hormones + helps you handle stress like a queen

It boosts your skin, hair, and nails by fuelling your body from the inside out

And yes... stronger muscles = stronger orgasms (you're welcome 😉)

Muscle = freedom.

Freedom to move how you want.

Freedom to eat without obsessing.

Freedom to feel confident every time you walk past a mirror or hit the sheets.

You're not just chasing a "fit" body.

You're building a resilient, radiant, powerful one.

And every lift, every squat, every set this month?

It laid a brick in that foundation.

You're not finished.

You're just getting dangerous.

Megan Brown
The Evolved

P.S. — If you've been sitting with this and thinking "I just need a plan"… now's the time.

This free Strength Assessment will show you exactly where you're at and what to focus on, no guesswork, no gym pressure, just a smart starting point.
👉 [Book Your Free Strength Assessment]

---

## Structural Analysis & Audit Notes

*(Assessed 2026-07-16)*

### What's Working

- **Life-stage segmentation is correct** — each sequence uses life-stage-specific proof points, vocabulary, and framing throughout
- **Day 2b structure is consistent** — 4-section format (Where Are We Starting / Next Step / Concerns / Fast Track) works well across all sequences
- **Standards-based proof points are strong** — split squat 50% BW / carry 75% BW / strong core specifics differentiate from generic fitness content
- **Opening/closing arcs** — Days 28-30 close well with identity language ("I'm not getting back to anything, I'm building forward")

### CTA Map — Updated (2026-07-17 optimisation)

The original audit (2026-07-16) identified a "21-day gap" with no CTAs after Day 9. This was incorrect — the full sequence audit (2026-07-17) revealed well-distributed CTAs throughout all 30 days. Updated same date: Days 12 and 21 now SA CTAs (was seminar replay / Metabolic Classification Assessment); Day 18 CTA removed; Day 30 reduced to SA-only; all SA CTAs converted to button format.

**Confirmed CTA days:**

| Day | CTA Type | Notes |
|---|---|---|
| 0 | SA (body) | All sequences |
| 1 | SA (P.S.) | All sequences |
| 2b | SA (entire email) | All sequences — life-stage specific copy |
| 5 | SA (P.S.) | All sequences |
| 7 | SA (P.S.) | All sequences |
| 9 | SA (P.S.) | All sequences |
| 12 | SA (P.S. + button) | All sequences — life-stage specific copy |
| 15 | SA (P.S.) | All sequences — life-stage specific copy |
| 18 | None (CTA removed) | All sequences |
| 20 | Soft reply ("Family Meeting" ritual) | Peri, Post-Meno, PPP only |
| 21 | SA (P.S. + button) | All sequences |
| 24 | Soft reply (member testimonial) | All sequences — life-stage specific copy |
| 27 | SA (P.S.) | All sequences — life-stage specific copy |
| 30 | SA button only | All sequences — life-stage specific copy |

**CTA-free days (confirmed):** 3, 4, 6, 8, 10, 11, 13, 14, 16, 17, 18, 19, 22, 23, 25, 26, 28, 29

**Note (2026-07-17):** Day 3 in POSTM had an undocumented Metabolic Classification Assessment P.S. not captured in the original audit. Removed — too close to Day 2b SA email, and Met Class is no longer part of the CTA strategy. Check other sequences for the same on Day 3.

Maximum consecutive gap: 2 days. The sequences are well-structured.

### Remaining Issues

1. **No post-Day 30 re-engagement sequence** — sequence ends after Day 30 with no follow-up for non-bookers.
2. **No internal reply branch** — all five delivery workflows retain `Stop on response` off and contain no reply action. By owner decision, nurture-email replies remain in the normal inbox and do not need a dedicated workflow task.
3. **Lifecycle exits resolved** — Strength Assessment removes all five life-stage sequences; `3.0 New Member` and `3.1 New Personal Training Client` remove those five plus Mobile Check. The exact multi-select targets were corrected and reload-verified on 29 July 2026.

### Future Optimisation (not yet scheduled)

- Build post-Day 30 re-engagement sequence (Days 32, 37, 45)

### Shared Content Structure (Days 3–30)

Days 3–30 are largely shared across all sequences with life-stage-specific framing adjustments. Core topics in order:
- Days 3-4: Habit loops + sleep science
- Days 5: 10 sleep hacks
- Days 6-7: Nutrition signal framework + 10 tweaks
- Days 8-9: Strength training case + 3-day plan
- Days 10-13: Supplements (WPI, Creatine, Omega-3)
- Day 14: PB identity shift
- Day 15: Bare minimum baseline
- Days 16-17: Carb timing + NEAT
- Day 18: Hormonal cycle
- Day 19: Stress as physical
- Days 20-22: Weekly reset + identity + Sunday ritual
- Days 23-26: Training smart + performance markers + recovery scorecard + deload
- Day 27: Muscle beyond aesthetics
- Days 28-30: Identity consolidation + closing arc

---

## Progress Check Email System

**Trigger:** Contact does not open the regular email within 1 day
**Subject:** IMPORTANT: Progress Check (all sequences, all days)
**Purpose:** Re-engagement prompt sent in parallel branch — nudges non-openers back into the sequence and references a "gift" at Day 30 to incentivise completion
**Applies to:** Days 7, 14, 21, 28, 30 (all 5 sequences)

These emails are conditional branches inside the GHL workflow — if the contact's email was not opened within the wait window, the progress check fires before the sequence continues.

### Day 7 Progress Check

> I noticed you didn't open 'Day #7 10 Simple Food Fixes'.
>
> To move to the strength training component of the course, you need to complete the nutrition component.
>
> So make sure you go back and open that email first.
>
> Also, if you haven't already heard, at the end of the course there is a little gift for you.
>
> Make sure you open all 30 of my emails to get your gift. Don't miss out!
>
> Megan Brown

### Day 14 Progress Check

> I noticed you didn't open 'Day #14 One Lift. One Shift. One New You.'.
>
> To move to the stress & recovery component of the course, you need to complete the strength training component.
>
> So make sure you go back and open that email first.
>
> Also, if you haven't already heard, at the end of the course there is a little gift for you.
>
> Make sure you open all 30 of my emails to get your gift. Don't miss out!
>
> Megan Brown

### Day 21 Progress Check

> I noticed you didn't open 'Day #21 - Long-Term Results Start With Who You Say You Are'.
>
> To move to the stress & recovery component of the course, you need to complete the identity component.
>
> So make sure you go back and open that email first.
>
> Also, if you haven't already heard, at the end of the course there is a little gift for you.
>
> Make sure you open all 30 of my emails to get your gift. Don't miss out!
>
> Megan Brown

### Day 28 Progress Check

> I noticed you didn't open 'Day #28 You Started Tired. You're Finishing Unstoppable'.
>
> You're so close to finishing the course now.
>
> At the end of the course is a little gift to you.
>
> Make sure you open all 30 of my emails to get your gift. Don't miss out!
>
> Megan Brown

### Day 30 Progress Check

> So close to finishing the course now.
>
> At the end of the course is a little gift to you.
>
> Make sure you open all 30 of my emails to get your gift.
>
> Megan Brown

**Note:** The "gift" referenced throughout is the Gift Email that fires after Day 30 (confirmed in POSTM stats — 100% open rate). Contacts are incentivised to open every email in the sequence to receive it.

---

## POSTM 30DNNC — Email Performance Stats

**Sequence:** Post Menopause 30DNNC
**Source:** GHL Builder stats view (screenshots, 2026-07-17)
**Note:** Small sample sizes in later days — treat percentages directionally, not as statistically significant

| Day | Email Name | Opened | Clicked |
|---|---|---|---|
| 0 | Welcome | 80% | 0% |
| 1 | Look Good Naked | 80% | 0% |
| 2 | Find The Gap | 54.55% | 0% |
| 2b | Strength Assessment Email | 60% | 0% |
| 3 | MIT's Habit Hack | 40% | 30% |
| 4 | Want to Glow | 70% | 10% |
| 5 | 10 Sleep Hacks | 70% | 0% |
| 6 | Every Meal Sends a Message | 63.64% | 0% |
| 7 | 10 Simple Food Fixes | 63.64% | 0% |
| 7 (PC) | Progress Check Email | 3.08% | 0% |
| 8 | Why Strength Training | 100% | 0% |
| 9 | 3 Day Strength Plan | 100% | 0% |
| 10 | Supplements That Actually Work | 100% | 0% |
| 11 | WPI | 100% | 0% |
| 12 | Creatine | 100% | 0% |
| 13 | Omega 3 | 80% | 0% |
| 14 | Hit a PB | 80% | 0% |
| 14 (PC) | Progress Check Email | 0% | 0% |
| 15 | When Life's A Mess | 75% | 0% |
| 16 | Carb Timing | 100% | 0% |
| 17 | NEAT | 100% | 0% |
| 18 | Cycle | 75% | 0% |
| 19 | Stress | 100% | 0% |
| 20 | Make Things Stick | 100% | 0% |
| 21 | Long Term Change | 100% | 0% |
| 21 (PC) | Progress Check Email | 4.76% | 0% |
| 22 | Sunday Reset | 75% | 0% |
| 23 | Train Smart | 80% | 0% |
| 24 | Performance Not Scale | 83.33% | 0% |
| 25 | Morning Routine | 66.67% | 0% |
| 26 | Recovery Window | 33.33% | 0% |
| 27 | Muscle Is Power | 50% | 0% |
| 28 | Not The Same Woman | 66.67% | 0% |
| 28 (PC) | Progress Check Email | 0% | 0% |
| 29 | You Built Her | 75% | 0% |
| 30 | Your Evolution | 75% | 0% |
| 30 (PC) | Progress Check Email | 0% | 0% |
| Gift | Gift Email | 100% | 0% |

### Key Observations

- **Open rates are strong for a 30-day sequence** — many days in the 75–100% range, especially Days 8–21
- **Click tracking and UTM tracking are confirmed on for every email step** — the 0% click rates are real, not a tracking gap
- **SA CTAs are not being clicked** — contacts are reading at high open rates but not acting on P.S. booking links throughout the sequence
- **Day 3 (30%) and Day 4 (10%) clicks** — the only real click activity in the sequence; these are body content links, not SA CTAs
- **Progress check emails have near-zero open rates** (3%, 0%, 4.76%, 0%, 0%) — they are not driving re-engagement. Non-openers are churning, not returning
- **Drop-off pattern:** Open rates track down from Days 24–27 (83% → 66% → 33% → 50%) then recover at Days 29–30 (75%). The recovery is likely the "gift" incentive pulling contacts back
- **Gift Email achieves 100% open rate** — the gift mechanic works; contacts who reach Day 30 open it

### Implications

- **The conversion bottleneck is CTA format, not open rate.** Contacts are engaged and reading — they're just not clicking through to book the SA
- P.S. links are the weakest CTA format. Soft text links buried at the bottom of educational emails are easy to read past without acting on
- The sequence has done its job building warmth and trust — but it relies on contacts self-initiating a booking decision from a low-friction nudge. Most don't
- **The case for a post-Day 30 re-engagement sequence is stronger than it looks** — if 75% are still opening at Day 30 but 0% are clicking, there's a large pool of warm, engaged non-bookers who need a different type of prompt (direct offer, urgency, or personal outreach trigger)
- Progress check emails should be reviewed: near-zero open rates suggest non-openers are churning, not returning. The current mechanic (referencing a missed email) is not compelling enough to re-engage
