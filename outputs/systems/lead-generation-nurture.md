# Lead Generation & Nurture System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-27

---

## Overview

The lead generation and nurture system captures cold prospects through two distinct entry points and moves them toward a booked consultation (Scale Session or Strategy Session). Cold traffic is captured via segmented 30-Day Nutrition & Nutrition Course (30DNNC) opt-in forms and a Metabolic Blueprint pathway, delivering value before asking for a commitment. Warm traffic — people who already know enough to book — enters directly through website forms (Book a Call, Register Interest, Discovery Call). All active leads flow through the **[WARM] Sales Pipeline** for sales-team management, while cold leads are tracked in the **[COLD] Marketing Pipeline** as they progress through the nurture sequence.

The system has a versioned `New Lead` workflow history (V1 through V5), indicating iterative development. V3 is currently the live/published version. V4 (3 parts) and V5 Part 1 exist in draft — likely being built to replace V3. The Metabolic Blueprint and Metabolic Classification pathways represent a parallel content-led funnel that qualifies leads through a 15-question metabolic assessment before surfacing the Scale Session offer.

---

## Pipelines

### [COLD] Marketing Pipeline
**Pipeline ID:** `57MQJY8hc7VoOrNkNhZw`

| Position | Stage | ID |
|---|---|---|
| 0 | Signed Up \| 30DNNC | `06c02f35-3332-4068-950e-332172d599d0` |
| 1 | Opened 25% \| 30DNNC | `ef4176b0-ab28-483d-bea4-160efb815dcf` |
| 2 | Opened 50% \| 30DNNC | `22ee7001-7593-4932-99fc-38fcb6be575c` |
| 3 | Opened 75% \| 30DNNC | `691ed414-9acb-41b8-931b-fdf0526092a5` |
| 4 | Opened 100% \| 30DNNC | `c4946bdd-7b5b-43c1-a71f-8ce0dc8646b4` |
| 5 | Course Complete \| 30DNNC | `d96b895f-7330-4b63-a9b3-6ca22a38da05` |

Tracks cold leads through email engagement during the 30DNNC sequence. Stage progression is engagement-based: each stage reflects a percentage of the course emails opened. Completion triggers the warm handoff.

---

### [WARM] Sales Pipeline
**Pipeline ID:** `JBVLybtIPZRIfjhzl5KV`

| Position | Stage | ID |
|---|---|---|
| 0 | New Leads | `b4b7ffbe-dfb3-4aa4-b339-78988bba1a1b` |
| 1 | Booked Call | `6fcf2a37-cfb2-48ea-8f26-849ed5948c76` |
| 2 | Assessment Booked | `c419912e-6e51-4e83-8820-6700d12ae971` |
| 3 | Pre-Qualified | *(confirm ID)* |
| 4 | No Show (Rebook 72hrs) | `e66774c3-5ee8-4924-8802-33a1fd6d6216` |
| 5 | Cancelled (Rebook 72hrs) | `d31d88cb-fd7d-48c5-ad79-68faf382c897` |
| 6 | Show (24hr Decision) | `0aba395d-2ac7-45bc-96e1-410fbeb114c2` |
| 7 | FUM - Follow Up Monthly | `53f391b8-0173-4bd3-ad77-a9ced2c0b58a` |
| 8 | FUNQ - Follow Up Next Quarter | `3bb4fe17-c26c-4a48-8d2b-33aab3d7ab5d` |

This is the single active pipeline — the LT Pipeline (previously a separate sales conversion pipeline) has been consolidated here. All SA opportunities flow through: Assessment Booked → Pre-Qualified → Show (24hr Decision) → won/lost. No-shows and cancellations branch to their respective rebook stages before falling to monthly/quarterly follow-up pools.

---

---

## Workflows

### Cold Lead Capture — 30DNNC (Segmented by Audience)

Each 30DNNC audience segment has a pair of workflows: one for organic (free) sign-ups and one for paid (ads) sign-ups. Paid versions typically include additional steps (e.g. SMS, faster follow-up) or skip certain organic-only touches.

| Workflow | Status | ID |
|---|---|---|
| 30DNNC Form Submission | **published** | `b7c9a9a6-975e-4072-836e-8737ef480de9` |
| 20/30s - 30DNNC Form Submission (Organic) | **published** | `3e2ecc1b-ec12-4f44-a47b-c2cd5c0eeb59` |
| 20/30s - 30DNNC Form Submission (Paid) | **published** | `e5f80457-eb4e-49b6-b921-37669a0541b1` |
| PERIM - 30DNNC Form Submission (Organic) | **published** | `a136b4f7-9ef5-4dd2-baab-3f82fc7a09a8` |
| PERIM - 30DNNC Form Submission (Paid) | **published** | `8f11882d-5cb3-494c-8054-0f2c0c7c6614` |
| POSTM - 30DNNC Form Submission (Organic) | **published** | `95bb5ae0-4b08-471d-a8b3-48a6f05d157e` |
| POSTM - 30DNNC Form Submission (Paid) | **published** | `c28c70f8-cd2f-4725-abfa-71336e197589` |
| PPP 30DNNC Form Submission (Organic) | **published** | `7ef6051d-9125-48c0-9954-4ccd378ae8f5` |
| PPP 30DNNC Form Submission (Paid) | **published** | `bfc203d6-e0aa-4511-9c4b-ca81e5e45773` |
| Teen - 30DNNC Form Submission (Organic) | **published** | `085dcdd7-fec3-43d6-b703-dbdb31593abd` |
| Teen - 30DNNC Form Submission (Paid) | **published** | `ca68c3d3-1429-45d7-b1e6-81dac5d00218` |

### Cold Lead Nurture — 30DNNC Delivery Sequences

| Workflow | Status | ID |
|---|---|---|
| 20/30 30DNNC | **published** | `4b199bf7-b24d-4aa9-a7fb-7deeed35a031` |
| PERIM 30DNNC | **published** | `511ad13f-fcb5-4197-b70c-c88a1e66b387` |
| POSTM 30DNNC | **published** | `6e652cfe-3020-4fe0-80a4-0be081216e96` |
| PPP 30DNNC | **published** | `786341e6-b082-4ecb-89db-6167ba91a0eb` |
| TEEN 30DNNC | **published** | `cb3993b1-6984-43b5-954d-b3a15a289009` |
| 30DNNC \| Mobile Check | **published** | `bf04828a-6e96-4347-b1cf-d01ac83d5db4` |

`30DNNC | Mobile Check` likely handles a mobile/desktop delivery branch or checks that SMS delivery is working correctly for the nurture sequence.

### Warm Lead Capture

| Workflow | Status | ID |
|---|---|---|
| Website Register Interest Form | **published** | `ab6c54c4-c1ad-4b1c-b2c0-cf1cdc829503` |
| Meta Lead Form | **published** | `d99148b7-cde2-424a-9dfa-2f81bfa8ea1a` |
| Bulimba Form Submission | **published** | `8ffd9028-36dc-4749-abf1-14aeb129c23e` |
| Coolangatta/Tweed Form Submission | **published** | `596b86e8-f56d-4e3e-a0d5-2dd07318befe` |
| Newfarm Form Submission | **published** | `02524663-0985-46c1-a325-e93ba278a689` |
| Corporate Gift Card Form Submission | **published** | `f7e49018-d709-4efe-bf66-71f2910c0fdf` |
| BOF Comment Automation | draft | `1be5990c-e689-47a0-950e-fda770060e19` |
| BOF DM Automation | draft | `328ded6a-a749-419d-8f6b-d6e0e119c60a` |
| Email Subscribers - Meta Lead Form | draft | `4a450a05-5d18-42c0-ad28-b28dabd703e2` |

BOF (Bottom of Funnel) automations trigger from social comment or DM interactions — currently in draft. Location-specific forms (Bulimba, Coolangatta/Tweed, Newfarm) capture interest from satellite or expansion market areas.

### New Lead Response (Versioned)

| Workflow | Status | ID |
|---|---|---|
| 1. New Lead (V1 - Jan24-Jun24) | draft | `3a54854b-1974-4644-92e4-34be5fd01d1f` |
| 1. New Lead (V2 Jun24-Jul24) | draft | `df92a27b-8520-48f1-8502-50af00431c99` |
| 1. New Lead (V3) | **published** | `ed9fc3a4-1cff-44b1-bb25-4ec62c0eb517` |
| 1. New Lead (V4) Part 1 (D0-D14) | draft | `79baa502-34b6-4acd-a935-be1f282b2b7e` |
| 1. New Lead (V4) Part 2 (D15-D42) | draft | `ee9456f5-38b6-4ebf-850c-5aff3e31a1c6` |
| 1. New Lead (V4) Part 3 (D43-D105) | draft | `8c7f4b4b-e01e-4f3c-bc4f-35ae907daaeb` |
| 1. New Lead (V5) Part 1 (D0-D14) | draft | `52e43175-1f42-4f17-9c53-b96de77ff2e6` |

V3 is the current live version. V4 is a three-part sequence stretching to 105 days (indicating a much longer drip than V3). V5 Part 1 exists in draft — likely being rebuilt. The day-based naming in V4/V5 makes the timeline explicit: Part 1 = D0-D14, Part 2 = D15-D42, Part 3 = D43-D105.

### Warm Lead Nurture

| Workflow | Status | ID |
|---|---|---|
| Lead Nurture: Social Proof | **published** | `89002ace-158a-4049-acf4-50008fc562e5` |
| Lead Nurture: 10:1 Value | draft | `3c8559c7-732a-48cf-8b76-3bdc2f2e5753` |
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` |
| Strength Assessment: Nurture | **published** | `2abf0af9-25be-40dc-935e-51c92a6798b0` |
| No Sale - Follow Up | **published** | `72820730-c4ef-44ab-8abc-a4149cbe32bf` |
| NS - Not Interested | draft | `1c923632-cda4-4614-9795-52e01c38aab0` |
| NS - Not Interested | draft | `6b37dbfa-c231-408f-8d42-3e1846049ec1` |
| No Response | draft | `62df6848-0ba5-49db-83b6-6ea845979235` |
| 2 Step Permission/Reactivation | **published** | `06181ca7-5d1b-4cbc-8b39-17ff87a8dd19` |

Two `NS - Not Interested` workflows exist in draft — likely a duplicate or audience-split version that hasn't been resolved. `2 Step Permission/Reactivation` is a re-engagement workflow for dormant leads.

### Metabolic Blueprint Pathway

| Workflow | Status | ID |
|---|---|---|
| Metabolic Classification Form | **published** | `b2bab945-ccfc-4d34-a2f1-ff078bcab517` |
| Metabolic Classification (Leads) | **published** | `ad84dbcc-d422-4445-aaec-41b60d14dec5` |
| Metabolic Blueprint | **published** | `6059d2d1-7297-49d9-9069-2a1399d2026f` |
| Metabolic Blueprint (END) | **published** | `1ae94d16-03f5-49a2-8bb4-6f70991e6cd0` |
| Women Over 40 - Metabolic Reboot | draft | `e80f5868-3ac3-414b-939a-75bfde9eb8eb` |

The Metabolic Blueprint is a complete sub-funnel: a lead completes a 15-question metabolic classification assessment, receives a personalised score and blueprint, and is then pitched the Scale Session. `Metabolic Blueprint (END)` handles the sequence termination / CTA delivery. `Women Over 40 - Metabolic Reboot` is a draft extension of this concept.

### Booked Call & Appointment Management

| Workflow | Status | ID |
|---|---|---|
| 2. Booked Call | draft | `70063b59-5d56-48f8-9faa-89501643a90e` |
| DNA - Rebook Call | **published** | `d8b81651-3339-4f20-8957-106deeb92418` |
| DNS - Rebook App | **published** | `d32bc95f-c3bd-493a-ae30-97d28bfe6ec9` |

DNA = Did Not Attend (call). DNS = Did Not Show (appointment). Both trigger rebook sequences. `2. Booked Call` is the confirmation/reminder sequence for the call itself — currently in draft.

### Goal-Based Nurture Sequences

| Workflow | Status | ID |
|---|---|---|
| Goal: Lose Weight | **published** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` |
| Goal: Tone Up | **published** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` |
| Goal: 300% Stronger | **published** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` |
| Goal: Postpartum Glow Up | **published** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` |
| Goal: Strength For Life | **published** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` |

Goal-specific nurture sequences, likely triggered from the `What are your primary fitness goals?` custom field or a form response. These deliver personalised content before the Scale Session ask.

### Re-engagement & Reactivation

| Workflow | Status | ID |
|---|---|---|
| RE#1 - 30DNNC & SEMINAR | **published** | `8f070c8c-647a-4912-9ac2-e3fbd3c1b471` |
| 2 Step Permission/Reactivation | **published** | `06181ca7-5d1b-4cbc-8b39-17ff87a8dd19` |
| War Plan | **published** | `9207ca6e-ed4f-44ab-b67e-bc98a41068de` |

`RE#1` re-engages cold leads who completed 30DNNC but didn't convert, directing them toward the seminar or next step. `War Plan` appears to be an aggressive reactivation sequence for long-dormant contacts.

### Special Campaigns & Offers

| Workflow | Status | ID |
|---|---|---|
| 28D$1 BLK FRI | **published** | `98d64b98-2bae-4ad7-b535-40f4ae3b9799` |
| GFO BLKFRI | **published** | `9ff13c3e-6f98-4d70-8c83-2d01b17974a6` |
| 6WBTC EDU | **published** | `9e772dac-c329-415e-9804-b38dcf481ba9` |
| PERIM: 7 Day Reset Purchase | **published** | `724b6d05-714b-4202-813c-9068222e0247` |
| POSTM: 7 Day Reset Purchase | **published** | `25426e71-1e56-4621-aee5-846625c4c048` |
| Fitness Event Registration | **published** | `41f36656-6f7d-41f9-be75-3c604dd78c6a` |
| FitFam Cookbook Purchase | **published** | `d176bd85-6e66-43de-a6d2-b889393967a5` |
| Resource: FEONs | **published** | `98b3eaf7-d189-4d63-aca6-af53a487e861` |
| Workshop Sequence | draft | `561e8fa8-68d0-40e1-8986-a26f3c044843` |

BLK FRI = Black Friday campaigns. 6WBTC = 6 Week Body Transformation Challenge (EDU = educational/lead nurture version). 7 Day Reset = paid product for perimenopause and postmenopause segments. FEONs = Free Educational/Offer sequences (resource lead magnets).

### Seminar-Specific

| Workflow | Status | ID |
|---|---|---|
| Transformation Seminar: Attending | **published** | `98f122e9-4914-4187-887e-f1b8fe8f6554` |
| Transformation Seminar: Interest | **published** | `cd33e367-9f17-42c9-a2cc-3f3bd90daada` |

---

## Forms

### Lead Capture — 30DNNC Opt-In Forms

| Form Name | ID |
|---|---|
| 30DNNC Form | `qB8xGGwhLdSGtbc3Z0EJ` |
| 30DNNC Form - 20-30's | `x7kX4iXL88xesZjZuc2y` |
| 30DNNC Form - 20-30's - Paid | `t49zdEkAyxhmENnljsGj` |
| 30DNNC Form - PPP | `nkLAaryOhWRKn6B4ynTR` |
| 30DNNC Form - PPP - Paid | `ezzKWJemhQTKXV7uTsaj` |
| 30DNNC Form - Perimenopause | `yGdm5cnighkkf4TZrJTy` |
| 30DNNC Form - Perimenopause - Paid | `3HC0uyY3yVpxGl6nbKVH` |
| 30DNNC Form - Postmenopause | `6KHo1LIUmUa1D5GASg98` |
| 30DNNC Form - Postmenopause - Paid | `5K20hus2C7U6JdjLoF28` |
| 30DNNC Form - Teen | `9KnvPrY6tEJfhaEPmkZ1` |
| 30DNNC Form - Teen - Paid | `FmK94feHeitFIqxVvAvk` |

Each audience segment has separate organic and paid versions. Paid variants likely include additional fields or behavioural differences to sync with ad attribution. Segments: General, 20-30s, PPP (Planning/Pregnant/Postpartum), Perimenopause, Postmenopause, Teen.

### Lead Capture — Website & Direct

| Form Name | ID |
|---|---|
| Website: Book A Call | `HimhqKZmS9Dc1pLx2YlI` |
| Website: Discovery Call Form | `dA75jti2i7lLFza6CocY` |
| Website: Register Interest | `hJohXvBZv6gn0jD3AdpR` |
| Scale Session Calendar Form | `hT6kTPJWfvGUgBr7bnSE` |
| Workshop Opt In Form | `6U0CBGMsLfRlMbCoQuWe` |

### Location-Specific Lead Capture

| Form Name | ID |
|---|---|
| Bulimba | `RfRzP6RlQO4SzeTaTfLi` |
| Coolangatta/Tweed Heads | `qtA20VCAhu4DkGBbEhKb` |
| Newfarm | `JgAzRnbtYkOAwj0kqrYX` |

Used for suburb-specific campaign landing pages. All three are published with corresponding form submission workflows.

---

## Surveys

| Survey Name | ID |
|---|---|
| Metabolic Classification Form | `3dC0KGX0gwEjkDf5YZHx` |

The Metabolic Classification Survey is the primary lead qualification tool for the Metabolic Blueprint pathway. It contains 15 scored questions (metabolic blockers, diet habits, exercise history, body composition, age, sleep, etc.) and generates a `Metabolic Classification Score` (NUMERICAL custom field). Leads are categorised as Met Class A, B, or C based on score.

---

## Calendars

| Calendar | Type | ID |
|---|---|---|
| Scale Session | round_robin | `0vKzaKzi0TSL1FcvPgY9` |
| Strategy Session with Impact School | round_robin | `Yfq0jSXH37U4arYHnGwp` |
| Goals Discovery Call | event | `RaANOEIyN7rN6XsT88oj` |
| Studio Appointment | event | `wumS9nYBf3k36n4WsKO2` |
| Strength & Longevity Assessment [WEST END, BRISBANE] (round_robin) | round_robin | `HSVEzfJH4nice96IxHem` |
| Strength & Longevity Assessment [WEST END, BRISBANE] (event) | event | `z3cCnLnqwEO7jDrGA0HH` |

**Scale Session** is the primary lead-to-consultation booking point — round-robin across available trainers. The **Strategy Session** is the second step in the two-step close process (Scale Session → Strategy Session). **Goals Discovery Call** is a lighter-touch entry point, likely used for online or out-of-area leads. **Studio Appointment** is used for in-person warm leads who haven't yet booked a Scale Session. The Strength & Longevity Assessment exists as both a round-robin (for direct booking) and an event version.

---

## Custom Fields

### UTM & Lead Source Tracking
**Group ID:** `9klbgmldALQR9VbYrMr8`

| Field | Type | Key | ID |
|---|---|---|---|
| utm_campaign | TEXT | `contact.utm_campaign` | `vn2xMaLsemWDevjl0aub` |
| utm_content | TEXT | `contact.utm_content` | `NEUXQAbDJnGksriffuO5` |
| utm_medium | TEXT | `contact.utm_medium` | `0fkHvHHBcE36b3Wg8sy9` |
| utm_source | TEXT | `contact.utm_source` | `1P38S69Vo9PegkkrZmdY` |
| Lead Source | SINGLE_OPTIONS | `contact.lead_source` | `PMDHTnyNEhZS4qgOhUxE` |

**Lead Source options:** Paid Social - Meta / Paid Search - Google / Organic

**Group ID:** `yCGIA0tMjIzAVjRjSQXq`

### Lead Qualification & Segmentation
**Group ID:** `9klbgmldALQR9VbYrMr8`

| Field | Type | Key | ID |
|---|---|---|---|
| Pick the most relevant stage of life | RADIO | `contact.pick_the_most_relevant_stage_of_life` | `gKk8C5noKS1Gs81vKafA` |
| Where do you currently live? | MULTIPLE_OPTIONS | `contact.where_do_you_currently_live` | `OzgRHzKYJmkppezLjkL4` |
| Email Opt In | CHECKBOX | `contact.email_opt_in` | `elb56bw7b0ffyU55uo67` |
| SMS/Txt Opt In | CHECKBOX | `contact.smstxt_opt_in` | `qGZnum0zTEiFsFvzV5AV` |
| Do you have (or are about to start) an offer | RADIO | `contact.do_you_have_or_are_about_to_start_an_offe` | `KBTxAVIXSgFlmEWzBhuB` |
| Lead: Life Stage | SINGLE_OPTIONS | `contact.lead_life_stage` | *(created 2026-04-27)* |

**Stage of Life options (form field):** Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause

**Lead: Life Stage options (canonical export field):** Teenagers / Women in Their 20s & 30s / Pregnancy/IVF / Postpartum / Perimenopause / Postmenopause

> `Lead: Life Stage` is set in email/nurture sequences (not lead source workflows, to keep entry-point workflows simple). It is the canonical field for writing clean life stage data to Google Sheets (Pre-Qual Insights tab and Objections Log tab). Merge tag: `{{contact.lead_life_stage}}`.

**Location options:** Brisbane (or surrounding suburbs) / Gold Coast / QLD / Elsewhere in QLD / New South Wales / Victoria / Tasmania / South Australia / Northern Territory / Australian Capital Territory / Western Australia / Outside Australia

**Group ID:** `GuiXAoJoZHSIaS669O8A`

| Field | Type | Key | ID |
|---|---|---|---|
| Pick the most relevant stage of life (social) | RADIO | `contact.pick_the_most_relevant_stage_of_life_so_w` | `tGaGYawO3Q4AAPnuznF7` |

**Options:** Teen / 20-30s / Planning Pregnancy / Currently Pregnant / Postpartum / Peri Menopause / Post Menopause

> Note: Two near-identical "stage of life" fields exist in different groups — one from the main form capture, one likely from a social/BOF capture flow. Worth consolidating.

### Metabolic Classification Fields
**Group ID:** `d5MFIbXvk4dTXJ0S2kwD`

| Field | Type | Key | ID |
|---|---|---|---|
| Metabolic Classification Score | NUMERICAL | `contact.score_metabolic_classification_score` | `6SQirWtVQGGSo7W6HklT` |
| 1. Weight gain/loss concern | RADIO | `contact.1_whether_you_wish_to_gain_or_lose_weight` | `VrQDMPYspbp9AAvNN5Qb` |
| 2. Age influences metabolism | RADIO | `contact.2_yes_its_true_age_does_influence_metabol` | `Z7OBrGmrtAGrTeBFwzHI` |
| 3. Population background | RADIO | `contact.3_from_research_its_clear_that_some_popul` | `i18IGzbd5SOzvEsZkJRP` |
| 4. Diets undertaken | RADIO | `contact.4_how_many_diets_have_you_been_on` | `xfqo5tRDetZPtWY3tdWX` |
| 5. Breakfast pattern | RADIO | `contact.5_breakfast_is_a_powerful_trigger_that_ca` | `xZ9IS72OCk2UqHbb0JaR` |
| 6. Past 6 months nutrition (meal structure) | CHECKBOX | `contact.6_for_the_past_6_months_pick_the_statemen` | `92uxbyv6ge8Ard6cOiKD` |
| 6b. Right now nutrition description | RADIO | `contact.6_right_now_what_description_best_describ` | `C3xZccZrxS2zxREsU0Fg` |
| 7. Structured training history | RADIO | `contact.7_how_many_structured_12_week_body_transf` | `O4lrkKe2PEZThlfVKP2n` |
| 8. Omega 3 knowledge | RADIO | `contact.8_a_high_ratio_of_omega_3_is_essential_fo` | `FT3Jy5fXkhCcgxSt1z02` |
| 9. Resistance exercise history | RADIO | `contact.9_with_every_passing_decade_adults_lose_t` | `ZttqTyzvgfMwhzG5E0tj` |
| 10. Aerobic exercise frequency | RADIO | `contact.10_how_often_do_you_perform_aerobic_type_` | `Cf6KvIgf26qjJGYSjj8U` |
| 11. Body fat level | RADIO | `contact.11_how_much_body_fat_you_have_and_how_lon` | `g9MR18aAMemCQoc7Otfm` |
| 12. Body fat distribution | RADIO | `contact.12_where_you_store_your_body_fat_has_impo` | `ZFgG35JN5T02j94tRuZK` |
| 13. Sleep quality | CHECKBOX | `contact.13_sleep_quality_has_a_profound_effect_on` | `Y1SolIU7VWbatXBSejpl` |
| 14. Metabolic blockers | CHECKBOX | `contact.14_metabolic_blockers_are_poor_sleep_habi` | `KZG1ydSgLgVnp3ivCGOP` |
| 15. Mirror confidence | RADIO | `contact.15_when_you_stand_in_front_of_the_mirror_` | `02Ed49bwNfKCFRDZrVzp` |
| I agree to receive SMS updates | CHECKBOX | `contact.checkbox_8i12` | `e0Ex3myyRqm6QiEcXgOG` |

### Fitness Goals
**Group ID:** `JwbflBU2YDUaZb9godHU`

| Field | Type | Key | ID |
|---|---|---|---|
| What are your primary fitness goals? | CHECKBOX | `contact.what_are_your_primary_fitness_goals` | `HbIxBf5wqpYIQuETaemm` |

**Options:** Lose Weight / Tone Up / Improve Health / Improve Posture / Get Stronger / Injury Prevention

---

## Custom Values

| Name | Key | Value / Notes |
|---|---|---|
| 30DNNC Link | `{{ custom_values.30dnnc_link }}` | `https://www.theevolvedgym.com.au/30dnnc` |
| Metabolic Classification Assessment Link | `{{ custom_values.metabolic_classification_assessm` | `https://api.leadconnectorhq.com/widget/survey/3dC0KGX0gwEjkD` |
| Stay On List (Reactivation) | `{{ custom_values.stay_on_list_reactivation }}` | `https://theevolvedgym.com.au/strength-assessment` |
| Strength & Longevity Assessment | `{{ custom_values.strength__longevity_assessment }}` | `https://theevolvedgym.com.au/strength-assessment` |
| Peri Menopause: 7 Day Reset | `{{ custom_values.peri_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |
| Post Menopause: 7 Day Reset | `{{ custom_values.post_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |
| [WARM] Seminar - Replay | `{{ custom_values.warm_seminar__replay }}` | `https://youtu.be/YszXZrPwwS0` |
| [WARM] Seminar - Slide Deck | `{{ custom_values.warm_seminar__slide_deck }}` | Canva design URL |
| DR Offer | `{{ custom_values.dr_offer }}` | (empty) |
| Offer Name | `{{ custom_values.offer_name }}` | (empty) |
| Booking Thank You Page | `{{ custom_values.booking_thank_you_page }}` | (empty) |

---

## Tag Library (Lead & Nurture Related)

| Tag | Purpose |
|---|---|
| `cold lead` | Contact is a cold prospect (top of funnel) |
| `lead` | Generic lead flag |
| `new lead` | Recently captured, not yet contacted |
| `nurture` | In an active nurture sequence |
| `warm reactivation lead` | Previously cold/dormant, now re-engaged |
| `interested` | Has indicated intent but not yet booked |
| `30dnnc` | Enrolled in the 30DNNC sequence |
| `30dnnc: complete` | Completed the 30DNNC sequence |
| `opened: 25%` | Opened 25% of 30DNNC emails |
| `opened: 50%` | Opened 50% of 30DNNC emails |
| `opened: 75%` | Opened 75% of 30DNNC emails |
| `opened: 100%` | Opened 100% of 30DNNC emails |
| `metabolic blueprint` | In the Metabolic Blueprint funnel |
| `metabolic classification` | Completed metabolic classification quiz |
| `met class: a` | Metabolic Class A (high score) |
| `met class: b` | Metabolic Class B (medium score) |
| `met class: c` | Metabolic Class C (lower score) |
| `met class a` | Alternate/duplicate of met class: a |
| `highly engaged` | High email/SMS engagement flag |
| `no answer` | Called, no answer |
| `no response` | No response to follow-up attempts |
| `no sale` | Consultation held, not converted |
| `no sale: financial` | No sale — financial objection |
| `no show` | Did not attend booked appointment/call |
| `ns - follow up` | In no-show follow-up sequence |
| `not interested` | Explicitly declined |
| `lost` | Lost lead (closed) |
| `trust` | Trust-building content delivered |
| `action: booked impact call` | Booked an impact/strategy call |
| `action: workshop opt in` | Opted into a workshop |
| `source: bof comment` | Came from a BOF (social) comment |
| `source: bof dm` | Came from a BOF direct message |
| `landing page` | Entered via a landing page |
| `website` | Entered via the website |
| `meta ads` | Source: Meta paid advertising |
| `fb organic` | Source: Facebook organic |
| `ig organic` | Source: Instagram organic |
| `instagram` | Instagram source |
| `organic` | Organic (non-paid) source |
| `paid` | Paid advertising source |
| `referral` | Referred by an existing member/contact |
| `bark` | Source: Bark (freelancer/leads platform) |
| `walk in` | Walk-in enquiry |
| `contact us` | Used contact form |
| `trainer lead` | Lead is a potential trainer (staff pipeline) |
| `other leads` | Miscellaneous lead bucket |
| `reengage: link clicked` | Clicked a re-engagement link |
| `reengage: opened email` | Opened a re-engagement email |
| `reactivation_2026_stay` | In the 2026 reactivation campaign (stay cohort) |
| `strength assessment booked` | Has booked a Strength Assessment |
| `strength assessment link clicked` | Clicked the SA booking link |
| `strength assessment showed` | Attended the Strength Assessment |
| `studio appt` | Has a studio appointment scheduled |
| `goals submitted (under 45mins)` | Submitted goals form quickly (high intent indicator) |
| `7 day trial` | On a 7-day trial |
| `seminar: attending` | Registered for a seminar |
| `seminar: attended` | Attended a seminar |
| `seminar: bought` | Purchased at a seminar |
| `seminar: dna` | Did not attend seminar |
| `protein hand raiser opt in` | Opted into a protein/nutrition resource |
| `resource:food` | Received a food/nutrition resource |
| `food` | Food/nutrition context tag |
| `7 day reset` | Purchased or in 7 Day Reset program |
| `fitfam cookbook` | Purchased FitFam Cookbook |
| `perimenopause` | Perimenopause segment |
| `20/30s` | 20-30s segment |
| `teen` | Teen segment |
| `planpreg` | Planning pregnancy segment |
| `planning pregnancy` | Planning pregnancy (full tag) |
| `post partum` | Post-partum segment |
| `postmenopause` | Post-menopause segment |
| `pregnant` | Currently pregnant |
| `fit over 40` | Over-40 segment (legacy/campaign) |
| `brisbane` | Brisbane location tag |
| `gold coast` | Gold Coast location tag |
| `bulimba` | Bulimba-specific lead |
| `coolangatta/tweed` | Coolangatta/Tweed-specific lead |
| `newfarm` | Newfarm-specific lead |
| `redcliffe` | Redcliffe-specific lead |
| `nya` | Not yet assigned (internal admin flag) |
| `dnd` | Do not disturb (suppress comms) |
| `supress` | Suppress from sequences |
| `failed sms` | SMS delivery failure |

---

## Flow Diagrams

### Cold Lead Flow: 30DNNC Pathway

```
[Meta Ad / Organic Post]
        |
        v
[30DNNC Opt-In Form]
(Segmented: 20/30s / PERIM / POSTM / PPP / Teen / General)
(Organic or Paid variant)
        |
        v
[30DNNC Form Submission Workflow fires]
  → Adds to [COLD] Marketing Pipeline: "Signed Up | 30DNNC"
  → Tags: cold lead, 30dnnc, [segment tag]
  → UTM fields captured (utm_source, utm_medium, utm_campaign, utm_content)
        |
        v
[Segment-specific 30DNNC Nurture Sequence begins]
(e.g. PERIM 30DNNC, 20/30 30DNNC, TEEN 30DNNC)
  → 30-day email course delivered
  → Pipeline stage advances on email engagement:
       Opened 25% → Opened 50% → Opened 75% → Opened 100%
  → Tags reflect engagement: opened: 25% / 50% / 75% / 100%
        |
        v
[Course Complete | 30DNNC]
  → Tag: 30dnnc: complete
        |
        v
[RE#1 - 30DNNC & SEMINAR workflow]
  → CTA: Book Scale Session or attend Seminar
        |
        v
[Scale Session booked]
  → Enters LT Pipeline: Scale Session Booked
```

---

### Warm / Direct Lead Flow

```
[Website / Meta Lead Form / BOF DM or Comment / Location Form]
        |
        v
[Capture workflow fires]
(Website Register Interest / Meta Lead Form / Bulimba / Coolangatta / Newfarm)
  → Lead added to [WARM] Sales Pipeline: New Leads
  → Tags: lead, new lead, [source tag], [segment tag]
  → UTM fields + Lead Source populated
        |
        v
[1. New Lead (V3) fires]
  → Immediate response sequence (SMS + email)
  → Goal: book Scale Session or Studio Appointment
        |
   -----+-------
   |           |
[Books Call]  [No Response / No Show]
   |           |
   v           v
[WARM Pipeline: Booked Call]    [DNA - Rebook Call / DNS - Rebook App]
   |                                    |
   v                                    v
[Scale Session held]          [NS - Follow Up / No Response workflow]
   |                                    |
   v                                    v
[LT Pipeline: Scale Session Booked]    [WARM Pipeline: NS - Follow Up]
   |                                    |
   v                                    v
[Strategy Session offered]     → [FUM - Follow Up Monthly]
   |                           → [FUNQ - Follow Up Next Quarter]
   v
[LT Pipeline: Strategy Session Booked]
   |
   v
[Deposit → Won [PIF]]
   or
[Lost Sale → Long Term Follow Up (Every Month)]
```

---

### Metabolic Blueprint Flow

```
[Metabolic Classification Assessment Link shared]
(via 30DNNC nurture, email, or direct)
        |
        v
[Metabolic Classification Form submitted]
  → Metabolic Classification Form workflow fires
  → Score calculated → Metabolic Classification Score field populated
  → Tag: metabolic classification
  → Tag assigned: met class: a / met class: b / met class: c
        |
        v
[Metabolic Blueprint workflow fires]
  → Personalised blueprint delivered based on score/class
  → Value sequence with educational content
  → CTA: Book Scale Session
        |
        v
[Metabolic Blueprint (END)]
  → Final CTA / sequence close
        |
        v
[Scale Session booked → LT Pipeline]
```

---

## System Notes & Observations

### What's working well
- **Audience segmentation** on 30DNNC is best-practice — six distinct life-stage segments each with organic and paid variants means messaging is highly relevant and ad attribution is clean
- **UTM capture** at the form level (four standard UTM fields) provides full source-medium-campaign-content tracking across all lead sources
- **Two-step consultation process** (Scale Session → Strategy Session) creates a structured close mechanism with a natural midpoint to assess intent before asking for commitment
- **Metabolic Blueprint** is a sophisticated content-led sub-funnel — the 15-question scored quiz provides genuine lead qualification and personalisation at scale
- **Goal-based nurture sequences** (5 goals, all published) allow post-capture personalisation before the Scale Session ask
- **BOF automations** (comment + DM) are architected even if in draft — captures social intent signals that most gyms miss
- **Versioned New Lead workflows** (V1–V5) show a culture of iteration. The day-based structure in V4 (D0-D14, D15-D42, D43-D105) is a significant maturation from earlier versions

### Current gaps / things to review
- **V3 is live but V4/V5 are in draft** — the new architecture (105-day V4, V5 in progress) hasn't been activated. Confirm whether V3 is intentionally retained while V4/V5 are built, or whether a migration is overdue
- **2. Booked Call workflow is in draft** — there is no published confirmation/reminder sequence for booked calls. This is a high-value gap: no-show rates will be elevated without automated reminders
- **Two duplicate NS - Not Interested workflows** (both draft) — needs deduplication or audience-split clarification before either is published
- **BOF Comment and BOF DM workflows are in draft** — social intent capture is not yet live. Once published, these should feed into the [WARM] Sales Pipeline with a `source: bof comment` / `source: bof dm` tag
- **No win-back automation visible for cold leads who complete 30DNNC but never book** — `RE#1` exists but its logic and CTA path post-completion isn't documented; confirm it actively drives to Scale Session booking
- **Lead Source field has only three options** (Paid Social / Paid Search / Organic) — doesn't capture Referral, Walk-In, Organic Social vs. Website, or Event sources that exist as tags. Consider expanding options to match tag taxonomy
- **Stage of life field fragmentation** — two form-capture fields exist (`9klbgmldALQR9VbYrMr8` and `GuiXAoJoZHSIaS669O8A`), retained for form functionality. The new `Lead: Life Stage` SINGLE_OPTIONS field (`contact.lead_life_stage`) is the canonical data-export field — set in email/nurture sequences rather than lead source workflows. This is the value written to Google Sheets (Pre-Qual Insights and Objections Log tabs) and used as a merge tag in downstream content personalisation
- **`met class a` and `met class: a`** are both in the tag library — duplicate with inconsistent formatting. Standardise to colon-format (`met class: a/b/c`)
- **`DR Offer`, `Offer Name`, and `Booking Thank You Page` custom values are empty** — these appear to be template/placeholder values intended to be populated for campaigns. If not in use, they should be removed or documented as intentional placeholders
- **No Lead Score or engagement scoring field** is visible — the pipeline stage progression in [COLD] tracks email opens, but there is no single engagement score field that aggregates intent signals across both pipelines. This limits the ability to prioritise follow-up across a large cold list
