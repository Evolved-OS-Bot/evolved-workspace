# Seminar & Event Marketing System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-01

---

## Overview

The Seminar & Event Marketing System covers all live and virtual events run by The Evolved — including transformation seminars, fitness events, corporate workshops (Strength For Industry), and the associated follow-up, attendance tracking, and conversion sequences. The system spans three distinct event types:

1. **Transformation Seminar** — The flagship warm-audience event. Registered prospects are tracked through a dedicated pipeline (Attending → Attended → Transformation Program). Post-attendance workflows capture interest and push towards membership conversion.
2. **Fitness Events** — General fitness events (including corporate activations and location-specific events) with registration, attendance management, and follow-up.
3. **Corporate / Strength For Industry** — A B2B workshop offering targeting business owners. Uses its own survey pair (Owner + Employee), gift card claim flow, and dedicated tag/workflow structure.

All three use a shared tag taxonomy (`seminar:`, `#fitnessevent`, `#corporategiftcard`, `corporate`) and feed into the broader [WARM] Sales Pipeline for conversion.

---

## Pipeline: Seminar Pipeline
**Pipeline ID:** `bwIQw694VZi6ipvVgaJW`

| Position | Stage | ID |
|---|---|---|
| 0 | Attending | `503ba654-d045-4f8f-84ba-3ae6617bc407` |
| 1 | Attended | `07dcd2b2-bf56-4a41-8b5a-fafd473b8a97` |
| 2 | Transformation Program | `a80f9ed4-9dd5-45dd-918f-3d4c9573b534` |

This is the only pipeline exclusively dedicated to seminar/event contacts. Movement through stages is managed by the Transformation Seminar workflows. "Transformation Program" is the conversion-intent stage — contacts here have attended and expressed interest in joining.

---

## Tags

| Tag | Purpose |
|---|---|
| `seminar: attending` | Contact has registered for an upcoming seminar |
| `seminar: attended` | Contact attended the seminar |
| `seminar: bought` | Contact converted to a paid product/membership post-seminar |
| `seminar: dna` | Contact registered but did not attend (Did Not Attend) |
| `#fitnessevent` | Registered for a fitness event (non-seminar) |
| `#corporategiftcard` | Received or claimed a corporate gift card |
| `corporate` | General corporate contact (Strength For Industry pathway) |
| `action: workshop opt in` | Opted into a workshop (Workshop Opt In Form) |

---

## Calendars

| Calendar | Type | ID |
|---|---|---|
| Goals Discovery Call | event | `RaANOEIyN7rN6XsT88oj` |
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` |
| Studio Appointment | event | `wumS9nYBf3k36n4WsKO2` |
| Strength & Longevity Assessment [West End] | event | `z3cCnLnqwEO7jDrGA0HH` |
| Strength & Longevity Assessment [West End] | round_robin | `HSVEzfJH4nice96IxHem` |

The Goals Discovery Call and Studio Appointment calendars are the primary post-event conversion booking points. The Strength & Longevity Assessment calendars are used in the Strength For Industry / corporate pathway to book team sessions.

---

---

# PART 1: Transformation Seminar

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Transformation Seminar: Interest | **published** | `cd33e367-9f17-42c9-a2cc-3f3bd90daada` |
| Transformation Seminar: Attending | **published** | `98f122e9-4914-4187-887e-f1b8fe8f6554` |
| 4. Attended - Interested | draft | `43286e28-71ed-4c2c-bbd6-be90568066ef` |
| RE#1 - 30DNNC & SEMINAR | **published** | `8f070c8c-647a-4912-9ac2-e3fbd3c1b471` |

> **Note:** "Transformation Seminar: Interest" and "Transformation Seminar: Attending" are both live. "4. Attended - Interested" is in **draft** — the post-attendance conversion sequence is not yet fully active. "RE#1 - 30DNNC & SEMINAR" is published and handles reactivation/re-engagement for this audience.

---

## Forms / Surveys

No standalone seminar registration form is listed (registration may be handled via a landing page or calendar booking). The post-event data capture uses the custom fields in group `7OLlEnKGr65RqbvvEh5n` below.

---

## Transformation Seminar Flow (Step by Step)

```
1. Prospect expresses interest
   → "Transformation Seminar: Interest" workflow fires
   → Tag: seminar: attending applied
   → Contact added to Seminar Pipeline: Attending stage

2. Pre-event reminders sent (via Attending workflow)

3. Seminar day — contact attends
   → "Transformation Seminar: Attending" workflow fires
   → Tag updated: seminar: attending → seminar: attended
   → Contact moves to Seminar Pipeline: Attended stage

4. Post-event survey/form captured (custom fields group 7OLlEnKGr65RqbvvEh5n)
   → Trainer who ran session recorded
   → Membership sign-up intent recorded
   → Workshop follow-up interest recorded
   → Referral/testimonial consent captured

5. If interested in membership:
   → Contact moves to Seminar Pipeline: Transformation Program stage
   → "4. Attended - Interested" workflow fires (DRAFT — not yet active)
   → [WARM] Sales Pipeline: New Leads stage (for conversion follow-up)

6. If did not attend:
   → Tag: seminar: dna applied
   → Replay delivered via custom value: [WARM] Seminar - Replay

7. Re-engagement / reactivation:
   → "RE#1 - 30DNNC & SEMINAR" workflow handles long-term nurture
```

---

## Post-Event Custom Fields
**Field Group ID:** `7OLlEnKGr65RqbvvEh5n`

These fields are captured in the post-seminar survey/form filled out by attendees on the day.

| Field | Type | Key | ID | Options |
|---|---|---|---|---|
| Did you sign up for a membership today? | RADIO | `contact.did_you_sign_up_for_a_membership_today` | `gVnwhZcfXH4ZrzKNSc7G` | Yes, I'm pumped to get started! / Not yet, I'm still thinking / Not for me right now |
| If you didn't sign up today, what's the 1 reason? | RADIO | `contact.if_you_didnt_sign_up_today_whats_the_1_re` | `k7CS8cbIpDOLBAcKLVcF` | Price / Timing/Life's Busy / Didn't Feel Ready |
| What was the most valuable part of the seminar? | LARGE_TEXT | `contact.what_was_the_most_valuable_part_of_the_se` | `Um06lHQJGX2SPic4QAFT` | — |
| What would you change or improve next time? | LARGE_TEXT | `contact.what_would_you_change_or_improve_next_tim` | `K3iRFkx5UUpY19TNqvkT` | — |
| Who was your trainer today? | RADIO | `contact.who_was_your_trainer_today` | `8JSzaPXo9REKsnAXcOM5` | Megan / Leisa / I can't remember |
| Would you like a follow up workshop in 6 months? | RADIO | `contact.would_you_like_a_follow_up_workshop_in_6_` | `288nVH0JljFIE3BiVXaF` | Yes / No |
| How would you rate your Strength Assessment? | NUMERICAL | `contact.rating_rat584_how_would_you_rate_your_str` | `byDrhCe6GCy390V74rzw` | — |
| Free team access to Megan's Transformation (program) | RADIO | `contact.free_team_access_to_megans_transformation` | `ECAEr5FAgH2CryE0eR0U` | Yes / No |
| May we use your name, role and company in testimonials? | RADIO | `contact.may_we_use_your_name_role_and_company_in_` | `sjSjQd5MokZPHhJH2N2O` | Yes / No |
| Do you know any business owners who might benefit? | RADIO | `contact.do_you_know_any_business_owners_who_might` | `KmV5ihGgQvwMMBx0f8cd` | Yes / No |
| (If yes) How should we refer to you in referrals? | TEXT | `contact.if_yes_how_should_we_refer_to_you_in_your` | `8PWfqZAftljrQf5k4Ybs` | — |
| (If yes) Let us know how to best be introduced | LARGE_TEXT | `contact.if_yes_let_us_know_how_to_best_be_introdu` | `dnlTEO2XI5npwtOqBTwb` | — |
| (If yes) What would you say to another business owner? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_another_busi` | `q3lXDIkx4keP5NMsxgLG` | — |
| (If yes) What would you say to someone thinking of attending? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_someone_thin` | `WwnjD5JDfpllWCMqjzjS` | — |

> **Note:** The referral fields (bottom 4) and the corporate referral question suggest the seminar is positioned at least partly toward a corporate/B2B audience, or that attendees are leveraged as referral channels to business owners.

---

## Custom Values (Seminar-Specific)

| Name | Key | Value |
|---|---|---|
| [WARM] Seminar - Replay | `{{ custom_values.warm_seminar__replay }}` | https://youtu.be/YszXZrPwwS0 |
| [WARM] Seminar - Slide Deck | `{{ custom_values.warm_seminar__slide_deck }}` | https://www.canva.com/design/DAGnMc9xVFY/BBnef28QmUAvmkEfKMA |
| TransformationFLIX Sign Up | `{{ custom_values.transformationflix_sign_up }}` | https://transformationflix.groovesell.com/checkout/071078b09 |

The replay is delivered to DNA contacts and potentially to all attendees. The slide deck may be shared post-event. TransformationFLIX is an upsell/conversion offer linked from the seminar follow-up.

---

---

# PART 2: Fitness Events

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Fitness Event Registration | **published** | `41f36656-6f7d-41f9-be75-3c604dd78c6a` |
| Training Event Form Submission | draft | `adb8747b-5253-42a4-904f-fea139efec5f` |

> "Fitness Event Registration" is live. "Training Event Form Submission" is in draft — the training event variant of this flow is not yet active.

---

## Forms

| Form | Type | ID |
|---|---|---|
| Workshop Opt In Form | form | `6U0CBGMsLfRlMbCoQuWe` |

The Workshop Opt In Form is the primary capture point for fitness event / workshop registrations. Tag `action: workshop opt in` is applied on submission.

---

## Workshop Sequence

| Workflow | Status | ID |
|---|---|---|
| Workshop Sequence | draft | `561e8fa8-68d0-40e1-8986-a26f3c044843` |

> The Workshop Sequence is in **draft**. Pre/post-workshop communication automation is not yet active for this event type.

---

## Fitness Event Flow (Step by Step)

```
1. Prospect sees event promotion and opts in
   → Workshop Opt In Form submitted
   → Tag: action: workshop opt in applied
   → Tag: #fitnessevent applied

2. "Fitness Event Registration" workflow fires
   → Confirmation sent to registrant
   → Internal notification to team

3. Event day
   → Attendance tracked manually or via form submission

4. Post-event
   → "Training Event Form Submission" workflow (DRAFT — not active)
   → Follow-up nurture into [WARM] Sales Pipeline
   → Workshop Sequence (DRAFT — not active)
```

---

---

# PART 3: Corporate / Strength For Industry

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Corporate Gift Card Form Submission | **published** | `f7e49018-d709-4efe-bf66-71f2910c0fdf` |

---

## Forms / Surveys

| Name | Type | ID |
|---|---|---|
| Corporate Gift Card Claim | form | `GbA3dlCz9L2TJfN9GwVJ` |
| Strength For Industry (Owner Survey) | survey | `DxZdvxigcS6zc4imB7Z5` |
| Strength For Industry (Employee Survey) | survey | `p5TGEOTXtbMZsGIjcsBX` |

---

## Corporate Custom Fields
**Field Group ID:** `7OLlEnKGr65RqbvvEh5n` (shared with Transformation Seminar post-event fields)

The following fields are specifically relevant to the corporate / Strength For Industry pathway:

| Field | Type | Key | ID | Options |
|---|---|---|---|---|
| A strength report to show your team's baseline | RADIO | `contact.a_strength_report_to_show_your_teams_base` | `bdr4mCpPoXciN7S8qn4C` | Yes / No |
| Do you know any business owners who might benefit? | RADIO | `contact.do_you_know_any_business_owners_who_might` | `KmV5ihGgQvwMMBx0f8cd` | Yes / No |
| (If yes) How should we refer to you in referrals? | TEXT | `contact.if_yes_how_should_we_refer_to_you_in_your` | `8PWfqZAftljrQf5k4Ybs` | — |
| (If yes) Let us know how to best be introduced | LARGE_TEXT | `contact.if_yes_let_us_know_how_to_best_be_introdu` | `dnlTEO2XI5npwtOqBTwb` | — |
| (If yes) What would you say to another business owner? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_another_busi` | `q3lXDIkx4keP5NMsxgLG` | — |
| (If yes) What would you say to someone thinking of attending? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_someone_thin` | `WwnjD5JDfpllWCMqjzjS` | — |
| May we use your name, role and company in marketing? | RADIO | `contact.may_we_use_your_name_role_and_company_in_` | `sjSjQd5MokZPHhJH2N2O` | Yes / No |
| Free team access to Megan's Transformation | RADIO | `contact.free_team_access_to_megans_transformation` | `ECAEr5FAgH2CryE0eR0U` | Yes / No |

---

## Corporate Flow (Step by Step)

```
1. Business owner or employee attends Strength For Industry event/workshop

2. Post-session:
   → Strength For Industry (Owner Survey) submitted by business owner
   → Strength For Industry (Employee Survey) submitted by team members
   → Tag: corporate applied

3. Gift card offer (if applicable):
   → Corporate Gift Card Claim form shared
   → "Corporate Gift Card Form Submission" workflow fires
   → Tag: #corporategiftcard applied
   → Gift card holder routed to membership onboarding

4. B2B referral capture:
   → "Do you know any business owners who might benefit?" field captured
   → Referral introduction details recorded

5. Follow-up:
   → Strength & Longevity Assessment booked (calendars: z3cCnLnqwEO7jDrGA0HH / HSVEzfJH4nice96IxHem)
   → Conversion to membership or team package
```

---

---

# System Notes & Observations

### What's in place
- **Seminar Pipeline** is purpose-built with a clear three-stage conversion funnel: Attending → Attended → Transformation Program. This is the most structured part of the event system.
- **Transformation Seminar workflows are live** — both Interest and Attending workflows are published, meaning registration and day-of triggers are active.
- **Replay and Slide Deck are custom values** — DNA contacts and post-event nurture can receive the replay link automatically via any workflow referencing `{{ custom_values.warm_seminar__replay }}`.
- **Post-event survey fields are rich** — 14 fields capturing NPS-style feedback, conversion intent, trainer attribution, referral opportunities, and testimonial consent. This is strong data capture.
- **Corporate pathway has its own survey pair** — Owner and Employee surveys are separate instruments, allowing distinct messaging and segmentation.
- **TransformationFLIX** is present as a conversion offer linked from the seminar system (GrooveSell checkout).
- **Tag taxonomy is clean** — four `seminar:` tags (attending, attended, bought, dna) give precise segmentation across the pipeline.

### Current gaps / things to review
- **"4. Attended - Interested" is in draft** — the post-attendance conversion sequence for interested attendees is not yet live. Contacts reaching the "Transformation Program" stage may not be receiving automated follow-up. This is a conversion gap.
- **Workshop Sequence is in draft** — pre/post-workshop communication for fitness events is not automated. These registrants are likely receiving manual or no follow-up.
- **Training Event Form Submission is in draft** — the training event variant form workflow is not active.
- **No registration form is explicitly listed for the Transformation Seminar** — registration may happen via landing page, Facebook event, or direct booking, but there is no GHL form with a seminar registration ID visible in the documentation. This may mean registrations bypass GHL or come in via another form not clearly labelled.
- **DNA workflow not explicitly documented** — the `seminar: dna` tag exists but no dedicated DNA re-engagement workflow is visible. The replay may be sent manually or via an undocumented branch inside the Attending workflow.
- **seminar: bought tag** — it is unclear which workflow applies this tag or what conversion event triggers it. This may need to be confirmed in the Transformation Seminar: Attending or 4. Attended - Interested workflow logic.
- **Strength & Longevity Assessment has two calendar entries** (event `z3cCnLnqwEO7jDrGA0HH` and round_robin `HSVEzfJH4nice96IxHem`) — it is unclear when each is used. The event type may be for scheduled group sessions; the round_robin for individual bookings.
- **No dedicated Seminar pipeline re-entry logic** — if a contact attends multiple seminars over time, there is no visible mechanism to reset or re-enter the pipeline stages cleanly.
