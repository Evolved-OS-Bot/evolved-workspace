# Sales Conversion System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-05-06 (Workflow 2 detailed structure documented; feedback survey fix recorded; metabolic classification split to separate file)

---

## Overview

The sales conversion system handles the full journey from first contact through to membership or PT purchase. The primary pipeline is the **[WARM] Sales Pipeline**, supported by goal-specific entry workflows, a War Plan sequence post-Strength Assessment, and monthly/quarterly follow-up loops for unconverted prospects.

The main sales channel is the **Strength & Longevity Assessment** — an in-gym session that captures baseline fitness data, delivers a personalised War Plan, and presents the membership offer. Sales happen in person at the studio, not via phone.

> **Note:** A second pipeline (LT Pipeline — Lauren Tickner snapshot import) was present in this account and has been deleted on 2026-04-01. It was not part of The Evolved's sales process. Several workflows and calendars imported with that snapshot may also be remnants — flagged in System Notes below.

---

## Pipeline: [WARM] Sales Pipeline
**Pipeline ID:** `JBVLybtIPZRIfjhzl5KV`

| Position | Stage | ID |
|---|---|---|
| 0 | Assessment Booked | `c419912e-6e51-4e83-8820-6700d12ae971` |
| 1 | Pre-Qualified | `f0db07c9-247f-41d5-ab68-8040f25e566d` |
| 2 | No Show (Rebook 72hrs) | `e66774c3-5ee8-4924-8802-33a1fd6d6216` |
| 3 | Cancelled (Rebook 72hrs) | `d31d88cb-fd7d-48c5-ad79-68faf382c897` |
| 4 | Show (24hr Decision) | `0aba395d-2ac7-45bc-96e1-410fbeb114c2` |
| 5 | FUM - Follow Up Monthly | `53f391b8-0173-4bd3-ad77-a9ced2c0b58a` |
| 6 | FUNQ - Follow Up Next Quarter | `3bb4fe17-c26c-4a48-8d2b-33aab3d7ab5d` |

Leads enter at **Assessment Booked** when they book a Strength & Longevity Assessment. Pre-Qualified captures leads who have been screened before their session. No Show and Cancelled both carry a 72hr rebook window. Show (24hr Decision) captures attended assessments — the 24hr window reflects the post-session close timeline. FUM and FUNQ hold long-term unconverted prospects in monthly and quarterly nurture loops.

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| War Plan | **published** | `9207ca6e-ed4f-44ab-b67e-bc98a41068de` | FUM monthly follow-up sequence — currently not in use. To be rebuilt as value-driven relationship nurture. |
| DNA - Rebook Call | **published** | `d8b81651-3339-4f20-8957-106deeb92418` |
| DNS - Rebook App | **published** | `d32bc95f-c3bd-493a-ae30-97d28bfe6ec9` |
| No Sale - Follow Up | **published** | `72820730-c4ef-44ab-8abc-a4149cbe32bf` |
| Goal: 300% Stronger | **published** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` |
| Goal: Lose Weight | **published** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` |
| Goal: Postpartum Glow Up | **published** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` |
| Goal: Strength For Life | **published** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` |
| Goal: Tone Up | **published** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` |
| Lead Nurture: Social Proof | **published** | `89002ace-158a-4049-acf4-50008fc562e5` |
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` |
| 1. New Lead (V3) | **published** | `ed9fc3a4-1cff-44b1-bb25-4ec62c0eb517` |
| NS - Not Interested | draft | `1c923632-cda4-4614-9795-52e01c38aab0` |
| NS - Not Interested | draft | `6b37dbfa-c231-408f-8d42-3e1846049ec1` |
| 2. Booked Call | draft | `70063b59-5d56-48f8-9faa-89501643a90e` |
| 4. Attended - Interested | draft | `43286e28-71ed-4c2c-bbd6-be90568066ef` |
| Lead Nurture: 10:1 Value | draft | `3c8559c7-732a-48cf-8b76-3bdc2f2e5753` |
| 1. New Lead (V1 - Jan24-Jun24) | draft | `3a54854b-1974-4644-92e4-34be5fd01d1f` |
| 1. New Lead (V2 Jun24-Jul24) | draft | `df92a27b-8520-48f1-8502-50af00431c99` |
| 1. New Lead (V4) Part 1 (D0-D14) | draft | `79baa502-34b6-4acd-a935-be1f282b2b7e` |
| 1. New Lead (V4) Part 2 (D15-D42) | draft | `ee9456f5-38b6-4ebf-850c-5aff3e31a1c6` |
| 1. New Lead (V4) Part 3 (D43-D105) | draft | `8c7f4b4b-e01e-4f3c-bc4f-35ae907daaeb` |
| 1. New Lead (V5) Part 1 (D0-D14) | draft | `52e43175-1f42-4f17-9c53-b96de77ff2e6` |
| No Response | draft | `62df6848-0ba5-49db-83b6-6ea845979235` |

> **Note:** V1–V5 new lead workflows represent iteration history. Only V3 is currently published. V4 and V5 drafts suggest active development on the lead nurture sequence. Two separate `NS - Not Interested` drafts exist — this is a duplication risk.

---

## Workflow 2: Strength Assessment — Detailed Structure

**Trigger:** Customer Booked Appointment — Strength & Longevity Assessment calendar

**Entry check:** Previously Assessed? (condition: Tags includes "strength assessment")

### Branch A — New Client (no prior SA tag)

1. Internal Notification
2. **#2 Create Appointment Sheet Row** ← Google Sheets action (new bookings only)
3. Add 'Strength Assessment Booked' Tag
4. Create WARM Sales Opportunity (Assessment Booked stage)
5. Find Us Email
6. SMS Booking Confirmation
7. Add to 'SA Nurture' Workflow
8. Wait for Reply to Booking Confirmation SMS (5-min timeout)
   - **Contact Reply** → Wait 1 min → SMS Confirmed → SMS Goals → Wait for Reply (45-min timeout) → loop
   - **Time Out** → Go To (SMS Acknowledgement path)

### Branch B — Returning Client (has SA tag)

1. Internal Notification
2. Remove 'SA Cancelled' Tag
3. Create WARM Sales Opportunity
4. Find Us Email
5. SMS Booking Confirmation
6. Add to 'SA Nurture' Workflow
7. Same reply/timeout sequence as Branch A

> **Note:** The Google Sheets row (#2 Create Appointment Sheet Row) only fires on Branch A (new clients). Returning clients who rebook do not create a new sheet row.

### Shared Post-Confirmation Sequence

After the booking confirmation reply loop resolves:

- SMS Acknowledgement / SMS Goals Follow Up 1
- Admin (Internal) Notification
- PREQUALIFY: `{{contact.first_name}}` (AI pre-qual bot fires here)
- Coach (Internal) Notification
- #2 PREQUALIFY: `{{contact.first_name}}`
- Owner (Internal) Notification
- Add 'Goals Submitted' Tag

### Cancellation Handling (parallel path)

- Add 'Strength Assessment Cancelled' Tag
- Cancel Strength Assessment (appointment cancelled in GHL)
- Admin (Internal) Notification
- #1 REBOOK: `{{contact.first_name}}` (rebook outreach sequence)
- Update Opportunity → 'Cancelled (Rebook 72hrs)'

### Pre-Appointment Reminder Sequence

- Wait 1 Day Before Appointment
- Reminder/Confirmation SMS
- Wait 4 hrs
  - **Contact Reply** → Replies 'READY' → Wait 1 hr Before Appointment → How to Find Us Video SMS → Wait 1hr → **Add to Workflow [→ 2.4 Send Consultation Feedback Survey]** → END
  - **Time Out (4 hrs)** → 'No Reply' SMS → Wait 2hrs → further reply branches → SMS Deadline Reminder

---

## Workflow 2.4: Send Consultation Feedback Survey

**Enrolled from:** Workflow 2 — added after the 1hr post-appointment wait in the READY branch.

> **No standalone trigger currently set** — workflow is enrolled programmatically from Workflow 2.

### Steps

1. Wait 1hr
2. Consultant Feedback Form SMS (sends survey link to client)
3. #3 Add SA Feedback Task (creates internal task for consultant)
4. Wait 2 hrs
5. Check Sales Outcome (condition: `SA: Sales Outcome` field is not empty)
   - **Filled** → END
   - **Not Filled** → Reminder: Consultant Feedback Form SMS → #4 Add Admin Task → END

### Why this is a separate workflow

Previously the feedback survey was embedded inside Workflow 2's pre-appointment sequence. Any appointment time change — even a 15-minute adjustment — triggers GHL's "Appointment Change" event, which ejects the contact from Workflow 2 mid-sequence. This caused the feedback survey to not fire for rescheduled appointments.

**Fix (implemented 2026-05-06):** Add "Add to Workflow → 2.4 Send Consultation Feedback Survey" at the end of the READY branch in Workflow 2, after "Wait 1hr". This decouples the survey from the reminder sequence. Reschedules restart the reminder flow cleanly; the feedback survey fires reliably for all attended appointments regardless of rescheduling history.

---

## Forms / Surveys

| Form / Survey | Type | ID |
|---|---|---|
| Scale Session Calendar Form | Form | `hT6kTPJWfvGUgBr7bnSE` |
| Website: Book A Call | Form | `HimhqKZmS9Dc1pLx2YlI` |
| Website: Discovery Call Form | Form | `dA75jti2i7lLFza6CocY` |
| Website: Register Interest | Form | `hJohXvBZv6gn0jD3AdpR` |
| Metabolic Classification Form | Survey | `3dC0KGX0gwEjkDf5YZHx` |
| Strength Assessment Survey | Survey | `ub4UbCMRY1gsp7dhGLWf` |

The Scale Session Calendar Form is the primary intake for LT Pipeline entry — completion triggers booking to Stage 0 (Scale Session Booked). Website forms (Book A Call, Discovery Call, Register Interest) feed the [WARM] Sales Pipeline. The Metabolic Classification Form and Strength Assessment Survey are pre-session qualification tools that enrich lead data before the consultation.

---

## Calendars

| Calendar | Type | ID |
|---|---|---|
| Scale Session | round_robin | `0vKzaKzi0TSL1FcvPgY9` |
| Strategy Session with Impact School | round_robin | `Yfq0jSXH37U4arYHnGwp` |
| Goals Discovery Call | event | `RaANOEIyN7rN6XsT88oj` |
| Studio Appointment | event | `wumS9nYBf3k36n4WsKO2` |
| Strength & Longevity Assessment [WEST END, BRISBANE] | round_robin | `HSVEzfJH4nice96IxHem` |
| Strength & Longevity Assessment [WEST END, BRISBANE] | event | `z3cCnLnqwEO7jDrGA0HH` |
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` |
| Intro Session - Megan | personal | `tc9BC56PdRNQGQmY0CgN` |
| Intro Session - Leisa | personal | `UTOhZ4UA8XDPYEZend4p` |
| Intro Session - Beth | personal | `ZGqYZun9jWcVqIo0O6u9` |
| Intro Session - Marnie | personal | `EvUpbuzC59WjEkbf12Ux` |
| Intro Session - Piper | personal | `Nbzw8JiElSyeXdDqBLnQ` |

The **Strength & Longevity Assessment** calendars are the primary sales channel entry point. The Studio Appointment calendar is used in the [WARM] pipeline for in-person visits. Two SA calendars exist for the same location (one round_robin, one event) — likely for different booking contexts.

> **LT Pipeline remnants to review:** `Scale Session` (`0vKzaKzi0TSL1FcvPgY9`), `Strategy Session with Impact School` (`Yfq0jSXH37U4arYHnGwp`), and `Goals Discovery Call` (`RaANOEIyN7rN6XsT88oj`) were all entry points or stages in the LT Pipeline. Confirm whether these calendars are still in active use or can be archived/deleted.

---

## Custom Fields

### Sales-Specific Fields (Group: `7OLlEnKGr65RqbvvEh5n`)

These fields are collected in the Strength Assessment Survey (`ub4UbCMRY1gsp7dhGLWf`) and post-session feedback form. They capture goal alignment, session outcome, referral potential, and conversion decision.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Did you sign up for a membership today? | RADIO | `contact.did_you_sign_up_for_a_membership_today` | Yes, I'm pumped to get started! / Not yet, I'm still thinking / Not for me right now | `gVnwhZcfXH4ZrzKNSc7G` |
| If you didn't sign up today, what's the 1 reason? | RADIO | `contact.if_you_didnt_sign_up_today_whats_the_1_re` | Price / Timing/Life's Busy / Didn't Feel Ready | `k7CS8cbIpDOLBAcKLVcF` |
| How would you rate your Strength Assessment? | NUMERICAL | `contact.rating_rat584_how_would_you_rate_your_str` | — | `byDrhCe6GCy390V74rzw` |
| What was the most valuable part of the session? | LARGE_TEXT | `contact.what_was_the_most_valuable_part_of_the_se` | — | `Um06lHQJGX2SPic4QAFT` |
| What would you change or improve next time? | LARGE_TEXT | `contact.what_would_you_change_or_improve_next_tim` | — | `K3iRFkx5UUpY19TNqvkT` |
| Who was your trainer today? | RADIO | `contact.who_was_your_trainer_today` | Megan / Leisa / I can't remember | `8JSzaPXo9REKsnAXcOM5` |
| A strength report to show your team's baseline | RADIO | `contact.a_strength_report_to_show_your_teams_base` | Yes / No | `bdr4mCpPoXciN7S8qn4C` |
| (If yes) How should we refer to you in your testimonial? | TEXT | `contact.if_yes_how_should_we_refer_to_you_in_your` | — | `8PWfqZAftljrQf5k4Ybs` |
| (If yes) Let us know how to best be introduced | LARGE_TEXT | `contact.if_yes_let_us_know_how_to_best_be_introdu` | — | `dnlTEO2XI5npwtOqBTwb` |
| (If yes) What would you say to another business owner? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_another_busi` | — | `q3lXDIkx4keP5NMsxgLG` |
| (If yes) What would you say to someone thinking about joining? | LARGE_TEXT | `contact.if_yes_what_would_you_say_to_someone_thin` | — | `WwnjD5JDfpllWCMqjzjS` |
| May we use your name, role and company in testimonials? | RADIO | `contact.may_we_use_your_name_role_and_company_in_` | Yes / No | `sjSjQd5MokZPHhJH2N2O` |
| Do you know any business owners who might benefit? | RADIO | `contact.do_you_know_any_business_owners_who_might` | Yes / No | `KmV5ihGgQvwMMBx0f8cd` |
| Free team access to Megan's Transformation program | RADIO | `contact.free_team_access_to_megans_transformation` | Yes / No | `ECAEr5FAgH2CryE0eR0U` |
| Would you like a follow up workshop in 6 months? | RADIO | `contact.would_you_like_a_follow_up_workshop_in_6_` | Yes / No | `288nVH0JljFIE3BiVXaF` |

---

### Goal / Stage of Life Fields (Group: `9klbgmldALQR9VbYrMr8`)

These fields classify leads by goal and life stage for goal-branching workflow routing.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Pick the most relevant stage of life | RADIO | `contact.pick_the_most_relevant_stage_of_life` | Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause | `gKk8C5noKS1Gs81vKafA` |

**Alternate version (Group: `GuiXAoJoZHSIaS669O8A`):**

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Pick the most relevant stage of life (so we can personalise) | RADIO | `contact.pick_the_most_relevant_stage_of_life_so_w` | Teen / 20-30s / Planning Pregnancy / Currently Pregnant / Postpartum / Peri Menopause / Post Menopause | `tGaGYawO3Q4AAPnuznF7` |

> Two versions of this field exist in different field groups — one used in intake forms, one in the lead capture context. The option values differ slightly (Post Partum vs. Postpartum). This may cause inconsistent routing in goal-branching workflows.

---

### Fitness Goal Field (Group: `JwbflBU2YDUaZb9godHU`)

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| What are your primary fitness goals? | CHECKBOX | `contact.what_are_your_primary_fitness_goals` | Lose Weight / Tone Up / Improve Health / Improve Posture / Get Stronger / Injury Prevention | `HbIxBf5wqpYIQuETaemm` |

---

### Metabolic Classification Fields (Group: `d5MFIbXvk4dTXJ0S2kwD`)

Used in the Metabolic Classification Form to score and classify leads before sessions. Feeds the `Metabolic Blueprint` workflow.

| Field | Type | Key | ID |
|---|---|---|---|
| Metabolic Classification Score | NUMERICAL | `contact.score_metabolic_classification_score` | `6SQirWtVQGGSo7W6HklT` |
| 1. Whether you wish to gain or lose weight | RADIO | `contact.1_whether_you_wish_to_gain_or_lose_weight` | `VrQDMPYspbp9AAvNN5Qb` |
| 2. Age influence on metabolism | RADIO | `contact.2_yes_its_true_age_does_influence_metabol` | `Z7OBrGmrtAGrTeBFwzHI` |
| 3. Population/genetic background | RADIO | `contact.3_from_research_its_clear_that_some_popul` | `i18IGzbd5SOzvEsZkJRP` |
| 4. How many diets have you been on? | RADIO | `contact.4_how_many_diets_have_you_been_on` | `xfqo5tRDetZPtWY3tdWX` |
| 5. Breakfast habits | RADIO | `contact.5_breakfast_is_a_powerful_trigger_that_ca` | `xZ9IS72OCk2UqHbb0JaR` |
| 6. Past 6 months meal structure | CHECKBOX | `contact.6_for_the_past_6_months_pick_the_statemen` | `92uxbyv6ge8Ard6cOiKD` |
| 6. Current eating description | RADIO | `contact.6_right_now_what_description_best_describ` | `C3xZccZrxS2zxREsU0Fg` |
| 7. Structured 12-week body transformation history | RADIO | `contact.7_how_many_structured_12_week_body_transf` | `O4lrkKe2PEZThlfVKP2n` |
| 8. Omega 3 knowledge | RADIO | `contact.8_a_high_ratio_of_omega_3_is_essential_fo` | `FT3Jy5fXkhCcgxSt1z02` |
| 9. Resistance exercise history | RADIO | `contact.9_with_every_passing_decade_adults_lose_t` | `ZttqTyzvgfMwhzG5E0tj` |
| 10. Aerobic exercise frequency | RADIO | `contact.10_how_often_do_you_perform_aerobic_type_` | `Cf6KvIgf26qjJGYSjj8U` |
| 11. Body fat level | RADIO | `contact.11_how_much_body_fat_you_have_and_how_lon` | `g9MR18aAMemCQoc7Otfm` |
| 12. Body fat storage pattern | RADIO | `contact.12_where_you_store_your_body_fat_has_impo` | `ZFgG35JN5T02j94tRuZK` |
| 13. Sleep quality | CHECKBOX | `contact.13_sleep_quality_has_a_profound_effect_on` | `Y1SolIU7VWbatXBSejpl` |
| 14. Metabolic blockers | CHECKBOX | `contact.14_metabolic_blockers_are_poor_sleep_habi` | `KZG1ydSgLgVnp3ivCGOP` |
| 15. Mirror/body confidence | RADIO | `contact.15_when_you_stand_in_front_of_the_mirror_` | `02Ed49bwNfKCFRDZrVzp` |

---

### Strength Assessment Fields (Group: `9My8zVPIm9hqJA0XqRND`)

Collected during the in-gym Strength & Longevity Assessment. Used for the War Plan personalisation.

| Field | Type | Key | ID |
|---|---|---|---|
| SA: Body Weight (kg) | NUMERICAL | `contact.sa_body_weight` | `wGaoPgkcWaGfpEi7WJKL` |
| SA: ATG Split Squat Elevation Level | RADIO | `contact.atg_split_squat_elevation_level` | `ROQU8f9sB8u0FWBJkCUM` |
| SA: ATG Split Squat Reps Performed | NUMERICAL | `contact.sa_atg_split_squat_reps_performed` | `MQCtvk4nCyH7N59Y8UUj` |
| SA: ATG Split Squat Weight Used (kg) | NUMERICAL | `contact.sa_atg_split_squat_weight_used` | `8VIQSzbbNTbtzvLlo937` |
| SA: Farmer Walk Weight Used (kg) | NUMERICAL | `contact.sa_farmer_walk_weight_used` | `TEVGkJruuFpuyYATSTFU` |
| SA: Plank Level | RADIO | `contact.sa_plank_level` | `YS1LOUYpW3GZXuxkpcwS` |
| SA: Plank Seconds Held | NUMERICAL | `contact.sa_plank_seconds_held` | `0CCKI0vy1tcPlhGXdnPC` |

SA: Plank Level options: Half Plank (Knees) / Bear Plank (Knees Bent & Elevated) / Full Plank

SA: ATG Split Squat Elevation Level options: Stool + 4 x 15kg Bumper Plates through to Floor (8 levels descending)

---

### Lead Source Field (Group: `yCGIA0tMjIzAVjRjSQXq`)

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Lead Source | SINGLE_OPTIONS | `contact.lead_source` | Paid Social - Meta / Paid Search - Google / Organic | `PMDHTnyNEhZS4qgOhUxE` |

---

### Membership / PT Agreement Fields (Group: `e3OeSDdsc8ZCJGnBKLL0`)

Captured at point of sale — agreement sign-off and debit setup.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Membership Type | MULTIPLE_OPTIONS | `contact.membership_type_commencement_you_are_sign` | Fit & Flexible / Strong / Fit & Flexible / Fast Track Package | `1SgYibtlIuophn9FYAh8` |
| Today's Upfront Cost Is | MULTIPLE_OPTIONS | `contact.todays_upfront_cost_is` | $299 / $399 / $599 | `KX6dFWysypvQ2ju5Y21g` |
| Weekly debit amount (after 30 days) | MULTIPLE_OPTIONS | `contact.weekly_debit_amount_after_30_days` | $69 / $99 / $149 | `d5Ig4OX79xc90WDYbdrN` |
| First Debit Date Is | DATE | `contact.first_debit_date_is` | — | `4agatus8jm9HUfBaRqJE` |
| Membership Agreement Date Signed | DATE | `contact.membership_agreement_date_signed` | — | `1WWilN82DxffsOdgKV2Y` |
| PT Agreement Date Signed | DATE | `contact.pt_agreement_date_signed` | — | `m7XNn6iutAoI4br2QUXu` |
| PT Agreement: Initial (24hrs Notice to Reschedule) | TEXT | `contact.initial_i_understand_sessions_rescheduled` | — | `iQfRvYyyX2uwI1m7XTx1` |
| PT Agreement: Initial (30 Days Notice to Cancel) | TEXT | `contact.initial_i_understand_terms_of_my_cancella` | — | `apLeFgJVKLuMIe8EKBjz` |
| Acknowledgement of Terms Initial | TEXT | `contact.acknowledgement_of_terms_initial_i_unders` | — | `YlRqSMojFrvy7xvD6VWe` |
| Signature | SIGNATURE | `contact.signature` | — | `a9vPpSzxm4YVHF9Z5uPd` |

---

### Pre-Exercise / Health Screening Fields (Group: `JwbflBU2YDUaZb9godHU`)

Collected in the Pre-Exercise Form before any in-person session. Required for compliance.

| Field | Type | Key | ID |
|---|---|---|---|
| Has your doctor ever said that you have a heart condition? | SINGLE_OPTIONS | `contact.has_your_doctor_ever_said_that_you_have_a` | `Txa0fry0yfYQvUN150D2` |
| Do you feel pain in your chest when you do physical activity? | SINGLE_OPTIONS | `contact.do_you_feel_pain_in_your_chest_when_you_d` | `8vdt9qraGjWoDAZRd4yG` |
| In the past month, have you had chest pain at rest? | SINGLE_OPTIONS | `contact.in_the_past_month_have_you_had_chest_pain` | `oWKsjvTEdBbJ05UblXbe` |
| Do you lose your balance because of dizziness? | SINGLE_OPTIONS | `contact.do_you_lose_your_balance_because_of_dizzi` | `rbTCvfxgjeOoVqOylaAF` |
| Do you have a bone or joint problem that could be made worse by exercise? | SINGLE_OPTIONS | `contact.do_you_have_a_bone_or_joint_problem_that_` | `jv1h8IIK8m1OdDhv6lKf` |
| Is your doctor currently prescribing drugs for blood pressure or heart condition? | SINGLE_OPTIONS | `contact.is_your_doctor_currently_prescribing_drug` | `sF2MyzRG0reDeFCQ0TZ7` |
| Do you know of any other reason why you should not do physical activity? | SINGLE_OPTIONS | `contact.do_you_know_of_any_other_reason_why_you_s` | `zstKZoQFwtf1C4gY1usj` |
| By ticking this box I confirm all answers are accurate | CHECKBOX | `contact.by_ticking_this_box_i_confirm_all_answers` | `gBIVOCfODK7a4ZF7ePvf` |
| Please confirm you are registered with the gym | TEXT | `contact.please_confirm_you_are_registered_with_th` | `kO7EdCYvJxMGHQHEajR1` |

---

### Post-Session Feedback Fields (Group: `JwbflBU2YDUaZb9godHU`)

Collected after a Strength & Longevity Assessment / Intro Session.

| Field | Type | Key | Options | ID |
|---|---|---|---|---|
| Did you achieve the result you wanted today? | RADIO | `contact.did_you_achieve_the_result_you_wanted_to_` | Yes / No | `muAXpBFZYKZuibhy5HLQ` |
| How long have you been a member of The Evolved? | RADIO | `contact.how_long_have_you_been_a_member_of_the_ev` | Less than 3 months / Less than 6 months / More than 6 months / More than 12 months | `6rExWm1aw9kuWNFuwfBW` |
| Have you communicated any and all struggles to your coach? | RADIO | `contact.have_you_communicated_any_and_all_struggl` | Yes / No | `vqk71JXGlQmLlCQrkNJ6` |
| Have you given yourself enough time to achieve your goal? | RADIO | `contact.have_you_given_yourself_enough_time_to_ac` | Yes / No | `7M8HMiRkBlgNLiAGmfys` |
| Have you utilised the Smart Meal Plan, High Protein Guide? | RADIO | `contact.have_you_utilised_the_smart_meal_plan_hig` | Yes / No | `S8QEHcZ7yCJJ4XuzbFUH` |
| Overall out of 5 stars how would you rate the session? | RADIO | `contact.overall_out_of_5_stars_how_would_you_rate` | 1 star / 2 stars / 3 stars / 4 stars / 5 stars | `pzDHsfSCxFQ1zoWDLHUf` |
| ONE TIME OFFER: Access to our Evolved Programming | RADIO | `contact.one_time_offer_access_to_our_evolved_prog` | Yes, I still need structure / No, I'll figure it out myself | `JYfea8WFcnLUkxqJqvPH` |
| What did you achieve in your time at The Evolved? | LARGE_TEXT | `contact.what_did_you_achieve_in_your_time_at_the_` | — | `2IaeuOSVg61BGYKdyEOk` |
| Would you like extra training? | CHECKBOX | `contact.if_you_would_like_extra_training_we_are_o` | Yes, I want to get stronger | `3cyRKn2OjCJY6zrKHCZd` |
| Other: if you're comfortable sharing please provide | TEXT | `contact.other_if_yourre_comfortable_sharing_pleas` | — | `hzzfBiZvBy9zR3Mtefzh` |
| Why are you cancelling your personal training? | LARGE_TEXT | `contact.why_are_you_cancelling_your_personal_trai` | — | `9fiifVeY7EhdbwKtuLrQ` |

---

## Tags

| Tag | Purpose |
|---|---|
| `new lead` | Entry into lead nurture system |
| `lead` | General lead identifier |
| `warm reactivation lead` | Previously cold lead re-engaged |
| `cold lead` | Unresponsive or unqualified lead |
| `interested` | Expressed interest |
| `intro` | Completed intro / trial session |
| `trial` | On 7-day trial |
| `7 day trial` | 7-day trial tag |
| `won` | Converted to paying member or PT client |
| `no sale` | Did not convert |
| `no sale: financial` | Non-conversion due to price objection |
| `lost` | Lost lead / churned |
| `no show` | Did not attend booked session |
| `ns - follow up` | No-show placed in follow-up sequence |
| `not interested` | Explicitly declined |
| `no answer` | No response to outreach |
| `no response` | No engagement with comms |
| `goal tone up` | Goal tag (duplicate variant) |
| `goal: 300% stronger` | Goal tag for strength-focused prospects |
| `goal: lose weight` | Goal tag for weight loss |
| `goal: postpartum` | Goal tag for postpartum leads |
| `goal: strength for life` | Goal tag for longevity-focused leads |
| `goal: tone up` | Goal tag for toning |
| `goals submitted (under 45mins)` | Goals form completed quickly (engagement signal) |
| `strength assessment booked` | SA booking confirmed |
| `strength assessment link clicked` | SA link engagement |
| `strength assessment showed` | SA attendance confirmed |
| `studio appt` | Studio appointment booked |
| `action: booked impact call` | Impact call booking action |
| `action: workshop opt in` | Workshop opt-in action |
| `post partum` | Life stage — postpartum |
| `planning pregnancy` | Life stage |
| `perimenopause` | Life stage |
| `postmenopause` | Life stage |
| `teen` | Life stage |
| `20/30s` | Life stage |
| `organic` | Organic lead source |
| `paid` | Paid lead source |
| `meta ads` | Meta/Facebook ads lead source |
| `fb organic` | Facebook organic lead source |
| `ig organic` | Instagram organic lead source |
| `landing page` | Entry via landing page |
| `website` | Entry via website |
| `referral` | Referral lead |
| `walk in` | Walk-in lead |
| `metabolic blueprint` | Enrolled in Metabolic Blueprint sequence |
| `metabolic classification` | Completed metabolic classification |
| `met class: a` | Metabolic class A |
| `met class: b` | Metabolic class B |
| `met class: c` | Metabolic class C |
| `met class a` | Duplicate of met class: a |
| `member` | Active member |
| `personal training` | PT client |
| `pt only` | PT only (no membership) |
| `strength for life` | Strength for Life program tag |
| `gold` | Gold tier member |
| `silver` | Silver tier member |
| `bronze` | Bronze tier member |
| `online client` | Online-only client |
| `old member` | Former member |
| `old pt client` | Former PT client |
| `oldmember` | Duplicate of old member |

---

## Flow Diagrams

### Primary Funnel: [WARM] Sales Pipeline

```
Lead enters (via website form, referral, organic, or Goal workflow)
        │
        ▼
[Stage 0] Assessment Booked
        │
        ├── Pre-screened before session
        │       ▼
        │   [Stage 1] Pre-Qualified
        │
        ├── Did not attend
        │       ▼
        │   [Stage 2] No Show (Rebook 72hrs)
        │       └── 72hr rebook window → back to Assessment Booked
        │
        ├── Cancelled booking
        │       ▼
        │   [Stage 3] Cancelled (Rebook 72hrs)
        │       └── 72hr rebook window → back to Assessment Booked
        │
        └── Attended Strength & Longevity Assessment
                ▼
        [Stage 4] Show (24hr Decision)
                │
                ├── Signs up within 24hrs
                │       └── tag: won → New Member workflow
                │
                └── Does not convert
                        ├── [Stage 5] FUM - Follow Up Monthly
                        └── [Stage 6] FUNQ - Follow Up Next Quarter
```

---

### Goal Branching: Entry Routing by Goal

```
Lead captures goal via form (stage of life + fitness goal fields)
        │
        ├── Goal: Lose Weight        → workflow: Goal: Lose Weight (`6488e53d`)
        ├── Goal: Tone Up            → workflow: Goal: Tone Up (`124d3acc`)
        ├── Goal: 300% Stronger      → workflow: Goal: 300% Stronger (`0dc2aa9b`)
        ├── Goal: Postpartum         → workflow: Goal: Postpartum Glow Up (`d8d867a5`)
        └── Goal: Strength For Life  → workflow: Goal: Strength For Life (`fdd77dc4`)

Each goal workflow delivers tailored nurture content, then routes to Scale Session booking.
```

---


---

### War Plan (FUM Monthly Follow-Up)

> **War Plan** is the monthly follow-up sequence for unconverted prospects in the FUM - Follow Up Monthly stage. It is currently **not in use**. The intent is to rebuild this as a value-driven, relationship-building nurture sequence rather than a sales push — sending genuinely useful content, member stories, and relevant education to keep The Evolved top of mind until the prospect is ready to commit.

```
Contact reaches [Stage 5] FUM - Follow Up Monthly
        │
        └── War Plan workflow fires (currently inactive)
                │
                └── [TO BE REBUILT] Monthly value-driven touchpoint
                        └── Relationship nurture → re-engagement → Assessment rebook
```

---

## System Notes & Observations

### What's working well
- **Strength & Longevity Assessment as the sales channel** — in-person assessment creates high psychological investment and a personalised deliverable (War Plan) before the offer is made
- **Goal-branching entry workflows** (5 live published workflows) personalise the funnel from first contact, routing leads through tailored nurture before booking the assessment
- **War Plan workflow** — monthly follow-up sequence for FUM stage. Currently not in use. Earmarked for rebuild as a value-driven relationship nurture sequence
- **Metabolic Classification** pre-qualifies leads and produces a score (`contact.score_metabolic_classification_score`) that can be used for segmentation and personalisation
- **FUM / FUNQ follow-up loops** keep unconverted prospects alive indefinitely without manual effort
- **Post-session feedback fields** capture the single most important conversion signal: "Did you sign up today?" and if not, why — creating a structured feedback loop

### LT Pipeline contamination — ✅ fully cleaned up (2026-04-02)
- ✅ **LT Pipeline** — deleted 2026-04-01
- ✅ **Scale Session calendar** (`0vKzaKzi0TSL1FcvPgY9`) — deleted (auto-removed with pipeline)
- ✅ **Strategy Session with Impact School calendar** (`Yfq0jSXH37U4arYHnGwp`) — deleted
- ✅ **Goals Discovery Call calendar** (`RaANOEIyN7rN6XsT88oj`) — deleted
- ✅ **Scale Session Calendar Form** (`hT6kTPJWfvGUgBr7bnSE`) — deleted
- ✅ **DNA - Rebook Call** (`d8b81651`) — archived (noted as Evolved 1.0 system)
- ✅ **DNS - Rebook App** (`d32bc95f`) — archived (noted as Evolved 1.0 system)
- ✅ **2. Booked Call** (`70063b59`) — archived

### Mobile Check Form — Lead Intake Connection

The **2. Strength Assessment** workflow contains a "Remove from Mobile Check Form" step immediately after the booking trigger (after a 1-min wait). This removes the contact from the Mobile Check Form workflow before the SA sequence begins, preventing overlap between the lead intake system and the assessment workflow.

The Mobile Check Form is part of the lead generation/intake system — full documentation of this form, its trigger, and its workflow is deferred to lead generation system documentation.

---

### Resolved issues
- **Feedback survey not firing on rescheduled appointments** ✅ — Feedback survey (Workflow 2.4) moved out of Workflow 2's pre-appointment sequence and enrolled via "Add to Workflow" action after the appointment time passes. Decoupled from appointment change events.

### Current gaps / things to review
- **Multiple draft new lead nurture workflows (V1–V5)** — only V3 is published. Confirm which version is intended to be live and archive stale drafts
- **Two duplicate `NS - Not Interested` workflows** — both in draft (`1c923632` and `6b37dbfa`). One should be archived before publishing
- **`4. Attended - Interested` is in draft** (`43286e28`) — post-attendance follow-up for interested-but-not-converted prospects is unautomated. High-leverage gap to address
- **Two Strength & Longevity Assessment calendars** for same location (round_robin `HSVEzfJH4nice96IxHem` + event `z3cCnLnqwEO7jDrGA0HH`) — clarify which is in active use for each booking context
- **Two versions of the stage-of-life field** — slight option discrepancy (Post Partum vs. Postpartum) across two field groups. Could cause misrouting in the Goal: Postpartum Glow Up workflow
- **No sale reason field is limited** — only 3 options (Price / Timing / Didn't Feel Ready). Doesn't capture objections like "Needs to discuss with partner" or "Not the right program"
- **Lead Source field has only 3 options** — doesn't capture referral, walk-in, or event sources that appear in the tag list
