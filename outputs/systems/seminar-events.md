# Seminar & Event Marketing System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-08-03

---

## Overview

The Seminar & Event Marketing System covers all live and virtual events run by The Evolved — including transformation seminars, fitness events, corporate workshops (Strength For Industry), and the associated follow-up, attendance tracking, and conversion sequences. The system spans three distinct event types:

1. **Transformation Seminar** — A retired warm-audience event system. Its workflows are archived and its empty three-stage pipeline was deleted on 3 August 2026.
2. **Fitness Events** — General fitness events (including corporate activations and location-specific events) with registration, attendance management, and follow-up.
3. **Corporate / Strength For Industry** — A dormant but intentionally retained B2B workshop concept targeting business owners. Its Owner and Employee survey pair is preserved for possible future use; the retired gift-card claim path has been removed.

All three use a shared tag taxonomy (`seminar:`, `#fitnessevent`, `#corporategiftcard`, `corporate`) and feed into the broader [WARM] Sales Pipeline for conversion.

---

## Retired Pipeline: Seminar Pipeline
**Pipeline ID:** `bwIQw694VZi6ipvVgaJW`

| Position | Stage | ID |
|---|---|---|
| 0 | Attending | `503ba654-d045-4f8f-84ba-3ae6617bc407` |
| 1 | Attended | `07dcd2b2-bf56-4a41-8b5a-fafd473b8a97` |
| 2 | Transformation Program | `a80f9ed4-9dd5-45dd-918f-3d4c9573b534` |

This was the only pipeline exclusively dedicated to seminar/event contacts. It contained zero opportunity records on 20 July and again on 1 August 2026. The two now-archived Transformation Seminar workflows contain email and wait actions only; neither creates or updates an opportunity, moves a pipeline stage, or applies a seminar tag. Peter approved deletion on 3 August. The pipeline was permanently deleted, the GHL list reduced to seven pipelines, and API read-back confirmed its ID is absent.

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
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` |
| Strength & Longevity Assessment [West End] | event | `z3cCnLnqwEO7jDrGA0HH` |
| Strength & Longevity Assessment [West End] | round_robin | `HSVEzfJH4nice96IxHem` |

The active post-event acquisition and conversion booking point is the 45-minute round-robin Strength & Longevity Assessment `HSVEzfJH4nice96IxHem`. The similarly named 30-minute event calendar `z3cCnLnqwEO7jDrGA0HH` was confirmed inactive on 21 July 2026.

---

---

# PART 1: Transformation Seminar

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Transformation Seminar: Interest | draft, archived 22 July 2026 | `cd33e367-9f17-42c9-a2cc-3f3bd90daada` |
| Transformation Seminar: Attending | draft, archived 22 July 2026 | `98f122e9-4914-4187-887e-f1b8fe8f6554` |
| 4. Attended - Interested | draft, archived | `43286e28-71ed-4c2c-bbd6-be90568066ef` |
| RE#1 - 30DNNC & SEMINAR | draft, archived 22 July 2026 | `8f070c8c-647a-4912-9ac2-e3fbd3c1b471` |

> **Retirement note, 22 July 2026:** Peter approved retirement of all seminar workflows, including the shared `RE#1` reactivation sequence. Interest, Attending and `RE#1` were set to Draft and moved to `1. Pipeline Workflows / Archive`. `RE#1` retains 10 enrolled records in its history, but they will not continue through the sequence while it remains Draft.

`4. Attended - Interested` is already unpublished and stored in the `1. Pipeline Workflows / Archive` folder. It has 88 historical enrolments, zero active enrolments and no enrolments in the available 30-day history. Its only actions are the obsolete sales-call workflow removal, one SMS and a one-minute wait; it is retained solely as an archived historical asset and is not part of the live acquisition system.

---

## Forms / Surveys

No standalone seminar registration form is listed (registration may be handled via a landing page or calendar booking). The post-event data capture uses the custom fields in group `7OLlEnKGr65RqbvvEh5n` below.

---

## Verified Workflow Behaviour

`Transformation Seminar: Interest` sends seven emails separated by waits: Save The Date, Muscle, Evolve8, Vicki, 5 Signs, You're Invited, and Final Call. It does not create or update an opportunity and does not apply a seminar tag.

`Transformation Seminar: Attending` sends four emails separated by waits: Attendance Confirmed, #1 Mistake, Peter's Email, and More Proof. It does not create or update an opportunity and does not apply a seminar tag.

Both workflows had no enrolments in the available 30-day history on 20 July 2026. Builder inspection on 21 July confirmed that both displayed only `Add trigger`, meaning no native trigger was configured. Peter approved their retirement; both were unpublished and archived on 22 July.

`RE#1 - 30DNNC & SEMINAR` was not a seminar-only asset. It included a four-way split, email-open and trigger-link waits, engagement tagging, internal notifications, a check for active enrolment in 30DNNC, and Cold Lead tagging. Live inspection on 22 July confirmed 10 waiting or processing enrolments after a 15 May bulk enrolment. The `50` shown at the bottom of the history screen was the page-size selector, not an enrolment count.

The first six of seven emails promote a “brand-new 8 Week Transformation Challenge” and a “Muscle & Metabolism Seminar coming up next week”, with a `METABOLISM` reply instruction. The final email uses the `FEON` keyword and offers the foods PDF. None of the seven inspected emails references the seminar replay, slide deck or TransformationFLIX custom values. The workflow is now retained only as archived history.

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
| Who was your trainer today? | RADIO | `contact.who_was_your_trainer_today` | `8JSzaPXo9REKsnAXcOM5` | Megan / Piper / Nora / Katrina / Leisa / I can't remember |
| Would you like a follow up workshop in 6 months? | RADIO | `contact.would_you_like_a_follow_up_workshop_in_6_` | `288nVH0JljFIE3BiVXaF` | Yes / No |
| How would you rate your Strength Assessment? | NUMERICAL | `contact.rating_rat584_how_would_you_rate_your_str` | `byDrhCe6GCy390V74rzw` | — |
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
| [WARM] Seminar - Replay | `{{ custom_values.warm_seminar__replay }}` | Deleted 22 July 2026 |
| [WARM] Seminar - Slide Deck | `{{ custom_values.warm_seminar__slide_deck }}` | Deleted 22 July 2026 |
| TransformationFLIX Sign Up | `{{ custom_values.transformationflix_sign_up }}` | Deleted 22 July 2026 |

Live inspection on 22 July 2026 found no reference to any of these three values in the 11 emails across `Transformation Seminar: Interest` and `Transformation Seminar: Attending`. The Interest sequence still contains fixed May 19 and May 21 event dates. The seven emails in `RE#1 - 30DNNC & SEMINAR` also contain no reference to these custom values, although six retain stale seminar copy. The complete workspace search found no operational script, configuration or current manual reference that consumes the three values.

TransformationFLIX was removed from all five current waitlist sequences on 17 July. Its GrooveSell checkout remained stuck on `Connecting To Secure Payment Server` during the live check. Peter approved full retirement on 22 July.

The complete email-template scan found 16 TransformationFLIX references across three folders: seven marketing templates, eight delivery templates and the standalone CTA offer. All 16 were permanently deleted on 22 July, followed by the `TransformationFLIX Sign Up` custom value. A fresh rendered-template scan returned zero TransformationFLIX matches. The mixed-content folders were retained because they still contain 13 unrelated marketing templates and the unrelated Week 8 delivery template.

Four Metabolic Blueprint Marketing templates historically consumed the seminar values: `TCSA - Did Not Buy`, `TCS - Did Not Sign Up For Seminar`, and `TCSA - Did Not Attend` used both replay and slide deck; `TCS - Non Member` used the replay. The first three were already absent after the overlapping TransformationFLIX cleanup. `TCS - Non Member` was permanently deleted on 22 July, all four names were verified absent, and both seminar custom values were then deleted with a successful API read-back.

The former `Workshop Funnel` contained Opt In, Confirmation and Training steps and was mapped to `free.theevolvedgym.com.au/join-masterclass`. Live inspection on 22 July returned `ERR_NAME_NOT_RESOLVED`, so the funnel had no functioning public entry point on its configured hostname. All three steps were copied Impact School assets unrelated to The Evolved: the Opt In and Training pages advertised Lauren Tickner's 2024 social-media lead-generation system, while Confirmation promoted a five-to-ten-minute Scale Session and contained an empty calendar block. The pages contained fixed February dates, broken imagery, Impact School legal links and third-party disclaimers. The funnel recorded no page views, opt-ins or sales in the 22 June to 22 July reporting window, its Events tab contained no tracking events, and no operational workspace reference pointed to it. Peter approved deletion on 22 July 2026; the funnel and its empty folder were permanently deleted and verified absent.

---

---

# PART 2: Fitness Events

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Fitness Event Registration | draft; archived 22 July 2026 | `41f36656-6f7d-41f9-be75-3c604dd78c6a` |
| Training Event Form Submission | draft; archived 17 July 2026 | `adb8747b-5253-42a4-904f-fea139efec5f` |

> `Fitness Event Registration` was unpublished and archived on 22 July 2026 after its form and trigger dependencies were retired. It retains four historical and zero active enrolments. `Training Event Form Submission` was archived on 17 July 2026 and is not part of the active event flow.

An action-level audit of `Fitness Event Registration` found an internal email to `info@theevolvedgym.com.au`, a generic appointment-confirmation email, an obsolete “r2r training” SMS and a one-minute wait. It had no Create Task action, reply handling or re-entry. The workflow is now retained only as archived history.

---

## Forms

| Form | Type | ID |
|---|---|---|
| Workshop Opt In Form | form, deleted 22 July 2026 | `6U0CBGMsLfRlMbCoQuWe` |

The Workshop Opt In Form was the former capture point for fitness event / workshop registrations. It was permanently deleted and verified absent on 22 July 2026 after the obsolete Workshop Funnel and seminar workflow family were retired. There is no longer an active form submission path applying `action: workshop opt in`; the orphaned `Fitness Event Registration` workflow is now also unpublished and archived.

---

## Workshop Sequence

| Workflow | Status | ID |
|---|---|---|
| Workshop Sequence | absent from current inventory | Former ID `561e8fa8-68d0-40e1-8986-a26f3c044843` |

The 31 July 2026 revalidation found no matching record in the supported workflow inventory, and its direct builder route returned `Workflow not found`. Pre/post-workshop communication automation is not active.

---

## Fitness Event Flow (Step by Step)

```
1. Historical path, now retired
   → Workshop Opt In Form submitted
   → Tag: action: workshop opt in applied
   → Tag: #fitnessevent applied

2. Historical path, no longer triggerable: "Fitness Event Registration" workflow fires
   → Confirmation sent to registrant
   → Internal notification to team

3. Event day
   → Attendance tracked manually or via form submission

4. Post-event
   → Historical `Training Event Form Submission` workflow (archived, not active)
   → Follow-up nurture into [WARM] Sales Pipeline
   → Former Workshop Sequence is no longer present
```

---

---

# PART 3: Corporate / Strength For Industry

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Corporate Gift Card Form Submission | draft; archived 17 July 2026 | `f7e49018-d709-4efe-bf66-71f2910c0fdf` |

---

## Forms / Surveys

| Name | Type | ID |
|---|---|---|
| Corporate Gift Card Claim | form | Deleted 30 July 2026; former ID `GbA3dlCz9L2TJfN9GwVJ` |
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

The current Owner survey contains the workshop-improvement, owner-testimonial, marketing-consent, attribution and business-introduction questions. The Employee survey contains the employee-testimonial, marketing-consent, attribution and business-introduction questions.

`A strength report to show your team's baseline & improvements?` and `Would you like a follow up workshop in 6-12 months?` are not on either current survey and have zero stored values. Retain both as staged corporate concepts.

The obsolete TransformationFLIX access field was deleted on 31 July 2026 after owner approval. A fresh API read-back verified it absent.

---

## Corporate Flow (Step by Step)

```
1. Business owner or employee attends Strength For Industry event/workshop

2. Post-session:
   → Strength For Industry (Owner Survey) submitted by business owner
   → Strength For Industry (Employee Survey) submitted by team members
   → No current submission workflow or tag handoff is verified

3. Historical gift card offer, fully retired:
   → `Corporate Gift Card Form Submission` workflow archived 17 July 2026
   → Corporate Gift Card Claim form deleted 30 July 2026
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
- **Seminar Pipeline is retired**: its historical structure was Attending → Attended → Transformation Program. It contained zero opportunities and was permanently deleted on 3 August 2026 after the workflow layer had already been archived.
- **Transformation Seminar workflows are retired**: Interest, Attending and the shared `RE#1` sequence were set to Draft and moved to the Archive folder on 22 July 2026.
- **Replay and Slide Deck are fully retired**: both custom values and all four named historical template consumers were deleted and verified absent on 22 July 2026.
- **Post-event survey fields are rich** — 14 fields capturing NPS-style feedback, conversion intent, trainer attribution, referral opportunities, and testimonial consent. This is strong data capture.
- **Corporate pathway has its own survey pair** — Owner and Employee surveys are separate instruments, allowing distinct messaging and segmentation.
- **TransformationFLIX is fully retired**: all 16 matching templates and its legacy custom value were deleted and verified absent on 22 July 2026.
- **Tag taxonomy is clean** — four `seminar:` tags (attending, attended, bought, dna) give precise segmentation across the pipeline.

### Current gaps / things to review
- **The seminar workflow and pipeline layers are retired**: tags and any retained event-era form fields remain separate dependency decisions.
- **"4. Attended - Interested" is already retired** — it is draft in the Archive folder, with 88 historical and zero active enrolments. Its obsolete sales-call action is not operating and should remain classified as historical rather than as an active acquisition dependency.
- **Workshop Sequence is absent**: the former ID is not in the current supported workflow inventory and its builder route returns `Workflow not found`. Pre/post-workshop communication is not automated.
- **Training Event Form Submission is archived** — the training event variant is intentionally inactive.
- **No registration form is explicitly listed for the Transformation Seminar** — registration may happen via landing page, Facebook event, or direct booking, but there is no GHL form with a seminar registration ID visible in the documentation. This may mean registrations bypass GHL or come in via another form not clearly labelled.
- **DNA workflow not explicitly documented** — the `seminar: dna` tag exists, but the audited Attending workflow does not apply it or send the replay.
- **seminar tags have no verified owner** — the audited Interest and Attending workflows do not apply `seminar: attending`, `seminar: attended`, `seminar: bought`, or `seminar: dna`. Dependency-check the draft post-attendance workflow and contact usage before removal.
- **RE#1 is archived with 10 historical enrolled records**: do not interpret the retained enrolment count as a live sending queue while the workflow remains Draft.
- **The duplicate-looking assessment calendar is inactive** — the event calendar `z3cCnLnqwEO7jDrGA0HH` is inactive and should not be treated as a live booking path; the 45-minute round robin `HSVEzfJH4nice96IxHem` is the operational calendar.
- **No dedicated Seminar pipeline re-entry logic** — if a contact attends multiple seminars over time, there is no visible mechanism to reset or re-enter the pipeline stages cleanly.
