# Membership Lifecycle System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-01

---

## Overview

The Membership Lifecycle System covers the full journey of a member from the moment they sign up through their first week, first month, first 90 days, and beyond. It operates across four layers:

1. **Onboarding & Agreement** — Membership Agreement Form, Pre-Exercise Form, and initial welcome communications
2. **Lifecycle Nurture Sequences** — Time-based workflows triggered at Day 1, Day 8, Day 29, Day 91, and Day 181 to sustain engagement and reduce churn
3. **Membership Pipeline** — Tracks each member's current plan type (Online Only, Fit & Flexible, Strength & Sculpt, Fast Track, Gold, or PT tier)
4. **Membership Change Workflows** — Manages mid-lifecycle plan changes including upgrades to PT or Hybrid/Online variants

Lifecycle workflows span 365 days. Only `Membership: First 7 Days` and `Membership: Day 29-90` are currently published. The remaining windows (Day 8–28, Day 91–180, Day 181–365) are in draft.

---

## Pipeline: Membership Pipeline

**Pipeline ID:** `fkEvrFkTihYkdb3bpprd`

| Position | Stage | ID |
|---|---|---|
| 0 | Online Only | `22019d21-0efd-4604-9a83-5608c0776735` |
| 1 | Fit & Flexible | `edaf6054-486a-473d-be37-e5f9bcde0dd9` |
| 2 | Strength & Sculpt | `81aab141-2d01-4cdb-9d25-ee949f36098b` |
| 3 | Fast Track | `a1e8d561-91ec-4d95-a8ea-98ea2e129142` |
| 4 | Gold | `27bf02d9-74fd-4ee2-a1e0-b515b76fba79` |
| 5 | PT Only | `58247f13-4a47-40f8-8289-35d62fc138b3` |
| 6 | PT 1 p.wk | `9ce28fb1-f43b-472a-ac11-1b4c147b202b` |
| 7 | PT 2 p.wk | `01d615da-4bd4-4bf3-a5c6-54332588367d` |
| 8 | PT 3 p.wk | `edf7f617-e058-438a-978a-330fa262ef8e` |

Each member's pipeline stage reflects their active membership tier. Stage is set at sign-up and updated when a membership change is processed.

---

## Tags

| Tag | Purpose |
|---|---|
| `member` | Active member flag — applied at sign-up |
| `online client` | Member on Online Only plan |
| `gold` | Member on Gold plan |
| `personal training` | Member receiving PT |
| `pt only` | PT-only member (no group membership) |
| `1 p.wk` | PT frequency: 1 session per week |
| `2 p.wk` | PT frequency: 2 sessions per week |
| `3 p.wk` | PT frequency: 3 sessions per week |
| `1 p.fn` | PT frequency: 1 session per fortnight |
| `old member` | Previous member — used for win-back targeting |
| `oldmember` | Legacy version of old member tag |
| `old pt client` | Previous PT client |
| `weekly checkin` | Member is on a weekly check-in schedule |
| `irregular` | Member with irregular attendance pattern |
| `terminated` | Membership terminated |
| `trial` | Member on trial or 7-day trial |
| `7 day trial` | Specifically on 7-day trial |

---

## Calendars

| Calendar | Type | ID | Notes |
|---|---|---|---|
| On-boarding Session (30 Mins) | event | `s0C4iENvRiaYyREvTGJD` | Booked at start of membership |
| Intro Session - Megan | personal | `tc9BC56PdRNQGQmY0CgN` | Trainer-specific intro session |
| Intro Session - Leisa | personal | `UTOhZ4UA8XDPYEZend4p` | Trainer-specific intro session |
| Intro Session - Beth | personal | `ZGqYZun9jWcVqIo0O6u9` | Trainer-specific intro session |
| Intro Session - Marnie | personal | `EvUpbuzC59WjEkbf12Ux` | Trainer-specific intro session |
| Intro Session - Piper | personal | `Nbzw8JiElSyeXdDqBLnQ` | Trainer-specific intro session |
| Injury Triage - Megan | personal | `Knee8V0fRcHxmpu3W0Fb` | Used when health/injury flagged during onboarding |
| Injury Triage - Hannah | personal | `4asZ1oldru57moSFEKdB` | Used when health/injury flagged during onboarding |

The **On-boarding Session** calendar is the primary onboarding touchpoint. Trainer-specific **Intro Session** calendars are used when the member is assigned to a specific coach for their first session.

---

---

# PART 1: New Member Onboarding

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| 4. New Member | **published** | `c1321609-733a-42af-8d7b-88a11945974e` |
| Membership Agreement Form: Email | **published** | `355337b6-14fc-4c00-b9e7-3b0794a391aa` |
| Membership: First 7 Days | **published** | `10f3c717-1443-427c-8264-b2348a32a448` |
| Test - First 7 Days | **published** | `d6dd7a5f-4818-4530-b17c-ffa7001b7489` |

> **Note:** `Test - First 7 Days` appears to be a test/parallel version of the live First 7 Days workflow. Both are published — confirm whether the test version should be retired or repurposed.

---

## Forms & Surveys

| Form / Survey | Type | ID |
|---|---|---|
| Membership Agreement Form | Form | `CstPVJqXXbOVTarkr7tg` |
| Pre-Exercise Form | Form | `tUmSYWgC90QLMHycVotC` |

Both forms are completed as part of the new member onboarding process. The Membership Agreement Form captures plan selection, debit details, and signature. The Pre-Exercise Form captures health screening (PAR-Q style) questions.

---

## New Member Onboarding Flow (Step by Step)

```
1. Member signs up (sale closed via intro session or scale session)
2. "4. New Member" workflow fires
3. Contact placed into Membership Pipeline at correct stage (plan type)
4. "Membership Agreement Form: Email" workflow fires → member receives agreement link
5. Member completes Membership Agreement Form → plan, debit date, signature captured
6. Member completes Pre-Exercise Form → health screening captured
7. "Membership: First 7 Days" workflow fires (Day 1 trigger)
8. Welcome sequence begins — onboarding education, gym orientation, coach introduction
9. Member books Onboarding Session via On-boarding Session calendar
```

---

## Membership Agreement: Custom Fields

**Field Group:** `e3OeSDdsc8ZCJGnBKLL0`

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Membership Type | MULTIPLE_OPTIONS | Fit & Flexible / Strong / Fit & Flexible / Fast Track Package | `1SgYibtlIuophn9FYAh8` |
| Today's Upfront Cost Is | MULTIPLE_OPTIONS | $299 / $399 / $599 | `KX6dFWysypvQ2ju5Y21g` |
| Weekly debit amount (after 30 days) | MULTIPLE_OPTIONS | $69 / $99 / $149 | `d5Ig4OX79xc90WDYbdrN` |
| First Debit Date Is | DATE | — | `4agatus8jm9HUfBaRqJE` |
| Membership Agreement Date Signed | DATE | — | `1WWilN82DxffsOdgKV2Y` |
| Acknowledgement of Terms Initial | TEXT | Member initials acknowledging terms | `YlRqSMojFrvy7xvD6VWe` |
| Signature | SIGNATURE | Member sign-off on agreement | `a9vPpSzxm4YVHF9Z5uPd` |
| PT Agreement Date Signed | DATE | Populated when PT agreement also signed | `m7XNn6iutAoI4br2QUXu` |
| PT Agreement: Initial (24hrs Notice to Reschedule) | TEXT | Member initials on PT cancellation terms | `iQfRvYyyX2uwI1m7XTx1` |
| PT Agreement: Initial (30 Days Notice to Cancel) | TEXT | Member initials on PT notice period | `apLeFgJVKLuMIe8EKBjz` |

**Field Group:** `9klbgmldALQR9VbYrMr8` (General / Compliance)

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Email Opt In | CHECKBOX | Consent to receive emails | `elb56bw7b0ffyU55uo67` |
| SMS/Txt Opt In | CHECKBOX | Consent to receive transactional SMS | `qGZnum0zTEiFsFvzV5AV` |
| We promise to be respectful of your time | CHECKBOX | "I commit to showing up" — commitment checkbox | `qnGuWaqGp0ZyfspcPnhZ` |
| Please check this box to confirm | CHECKBOX | Confirmation checkbox | `lV2CW17bQMK1AdbwtUmB` |
| Do you have (or are about to start) an offer | RADIO | Yes / No | `KBTxAVIXSgFlmEWzBhuB` |
| Pick the most relevant stage of life | RADIO | Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause | `gKk8C5noKS1Gs81vKafA` |
| Where do you currently live? | MULTIPLE_OPTIONS | Brisbane / Gold Coast QLD / Elsewhere in QLD / NSW / VIC / TAS / SA / NT / ACT / WA / Outside Australia | `OzgRHzKYJmkppezLjkL4` |
| PT Block Service | TEXT | Type of PT block service | `Upyxa5ORrkYuzKmB9ikp` |
| PT Block Start | DATE | Start date of PT block | `qoSPND4o6aOmyMesj6Xs` |
| PT Block Trainer | TEXT | Assigned trainer name for PT block | `gSYaeeCF2iiRSzJhKePT` |

---

## Pre-Exercise Form: Custom Fields

**Field Group:** `JwbflBU2YDUaZb9godHU` (Health Screening / PAR-Q)

| Field | Type | Options / Notes | ID |
|---|---|---|---|
| Has your doctor ever said that you have a heart condition | SINGLE_OPTIONS | Yes / No | `Txa0fry0yfYQvUN150D2` |
| Do you feel pain in your chest when you do physical activity | SINGLE_OPTIONS | Yes / No | `8vdt9qraGjWoDAZRd4yG` |
| In the past month, have you had chest pain at rest | SINGLE_OPTIONS | Yes / No | `oWKsjvTEdBbJ05UblXbe` |
| Do you lose your balance because of dizziness | SINGLE_OPTIONS | Yes / No | `rbTCvfxgjeOoVqOylaAF` |
| Do you have a bone or joint problem that could be made worse by physical activity | SINGLE_OPTIONS | Yes / No | `jv1h8IIK8m1OdDhv6lKf` |
| Is your doctor currently prescribing drugs for blood pressure or a heart condition | SINGLE_OPTIONS | Yes / No | `sF2MyzRG0reDeFCQ0TZ7` |
| Do you know of any other reason why you should not do physical activity | SINGLE_OPTIONS | Yes / No | `zstKZoQFwtf1C4gY1usj` |
| What are your primary fitness goals? | CHECKBOX | Lose Weight / Tone Up / Improve Health / Improve Posture / Get Stronger / Injury Prevention | `HbIxBf5wqpYIQuETaemm` |
| By ticking this box I confirm all answers are true | CHECKBOX | Confirm | `gBIVOCfODK7a4ZF7ePvf` |
| Please confirm you are registered with the relevant authority | TEXT | Regulatory / insurance compliance | `kO7EdCYvJxMGHQHEajR1` |
| Who is your personal trainer? | RADIO | Megan / Leisa / Marnie / Piper | `YWkGI9PYbF8jP22NKpbQ` |
| Would you like extra training? | CHECKBOX | Yes, I want to get stronger | `3cyRKn2OjCJY6zrKHCZd` |
| How long have you been a member? | RADIO | Less than 3 months / Less than 6 months / More than 6 months / More than 12 months | `6rExWm1aw9kuWNFuwfBW` |
| Have you communicated any and all struggles | RADIO | Yes / No | `vqk71JXGlQmLlCQrkNJ6` |
| Have you given yourself enough time to achieve your goal | RADIO | Yes / No | `7M8HMiRkBlgNLiAGmfys` |
| Have you utilised the Smart Meal Plan, high protein guide etc. | RADIO | Yes / No | `S8QEHcZ7yCJJ4XuzbFUH` |
| Did you achieve the result you wanted to achieve? | RADIO | Yes / No | `muAXpBFZYKZuibhy5HLQ` |
| What did you achieve in your time at The Evolved? | LARGE_TEXT | — | `2IaeuOSVg61BGYKdyEOk` |
| Why are you cancelling your personal training? | LARGE_TEXT | — | `9fiifVeY7EhdbwKtuLrQ` |
| ONE TIME OFFER: Access to our Evolved Program | RADIO | Yes, I still need structure / No, I'll figure it out myself | `JYfea8WFcnLUkxqJqvPH` |
| Overall out of 5 stars — rating | RADIO | 1 star / 2 stars / 3 stars / 4 stars / 5 stars | `pzDHsfSCxFQ1zoWDLHUf` |

---

---

# PART 2: Membership Lifecycle Nurture Sequences

---

## Workflows

| Workflow | Status | ID | Window |
|---|---|---|---|
| Membership: First 7 Days | **published** | `10f3c717-1443-427c-8264-b2348a32a448` | Days 1–7 |
| Membership: Day 8-28 | draft | `c3587248-8934-471a-8ec1-f7b0191cee4c` | Days 8–28 |
| Membership: Day 29-90 | **published** | `f0f639f9-ab49-4f7e-990b-02d8ca8dfeab` | Days 29–90 |
| Membership: Day 91-180 | draft | `151fca2f-2aca-4567-91f2-630b8d4e4766` | Days 91–180 |
| Membership: Day 181-365 | draft | `9785ee0b-c987-4816-897c-796d6c7e5273` | Days 181–365 |

> Only **First 7 Days** and **Day 29-90** are published. Days 8–28, 91–180, and 181–365 are in draft and may not currently be running.

---

## Supporting Workflows (Lifecycle-Adjacent)

| Workflow | Status | ID | Purpose |
|---|---|---|---|
| 5. New Personal Training Client | **published** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` | Fires when a member adds PT to their membership |
| Google Review Request (4 & 5 Stars Only) | **published** | `ebbd43c1-4e39-4731-a3e3-c7e5f0bfae0b` | Sent to satisfied members to generate reviews |
| Goal: Lose Weight | **published** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` | Goal-specific nurture for weight loss members |
| Goal: Tone Up | **published** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` | Goal-specific nurture for tone up members |
| Goal: 300% Stronger | **published** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` | Goal-specific nurture for strength-focused members |
| Goal: Strength For Life | **published** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` | Longevity / lifestyle strength goal nurture |
| Goal: Postpartum Glow Up | **published** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` | Postpartum-specific goal nurture |
| Strength Assessment: Nurture | **published** | `2abf0af9-25be-40dc-935e-51c92a6798b0` | Nurture sequence post-Strength Assessment |

---

---

# PART 3: Membership Change Workflows

---

## Overview

Membership Change workflows handle mid-lifecycle plan transitions. Two documented change types exist:

- **Hybrid/Online upgrade** — member moves to or between Hybrid PT + programming or Online-only plan
- **PT Agreement** — member adds or changes their PT package (Standard or Optimal Results)

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Membership Agreement Form: Email | **published** | `355337b6-14fc-4c00-b9e7-3b0794a391aa` |
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` |

> No dedicated "Membership Change" trigger workflow is visible in the workflow list. Changes may be initiated manually or via a broader workflow. The two Agreement Form: Email workflows serve as the delivery mechanism once a change decision is made.

---

## Surveys (Membership Change Forms)

| Survey | ID | Purpose |
|---|---|---|
| Membership Change: Hybrid/Online Option | `zFxqvzogSZFbeGDnNM8Q` | Captures plan selection and signature for Hybrid or Online-only change |
| Membership Change: PT Agreement Form | `w8j2Hc5KRu7MCYBEnmKb` | Captures PT package choice and signature for PT upgrade/change |

---

## Membership Change: Hybrid/Online Custom Fields

**Field Group:** `AyOGhcB2nXpQBt1LsAqO`

| Field | Type | Options | ID |
|---|---|---|---|
| MCHO: Plan Choice | RADIO | Hybrid \| 1 PT p/mth + Personalised Programming ($69 p/week) / Online \| Evolved Programming Only ($29 p/week) | `Vbv1EHS1IbGJKHplBHeo` |
| MCHO: Initial Online Only Terms | TEXT | Member initials confirming online-only terms | `2DNdB9zWbM2jFxnk9zmz` |
| MCHO: Signature | SIGNATURE | Member sign-off on change | `3CFg8eyc3OTWhPsnGyq0` |

---

## Membership Change: PT Agreement Custom Fields

**Field Group:** `wcVp5BsbhFXgkyeLpiPj`

| Field | Type | Options | ID |
|---|---|---|---|
| MCPT: PT Choice | RADIO | The Standard Strength Package ($120 p/wk) / The Optimal Results Package ($180 p/week) | `tw73Uz4jCyb4gxwCEKLy` |
| MCPT: Signature | SIGNATURE | Member sign-off on PT agreement | `lPQ96chOfOsFTCfMBcUX` |

---

## Membership Change Flow

```
Trigger (manual or automated — not documented explicitly)
   │
   ▼
Staff selects relevant change type:
   │
   ├── Hybrid/Online Change
   │     → Membership Change: Hybrid/Online Option survey sent
   │     → Member selects: Hybrid ($69/wk) or Online Only ($29/wk)
   │     → Member signs → MCHO fields populated
   │     → Membership Pipeline stage updated → Online Only or Fit & Flexible
   │
   └── PT Upgrade / Change
         → Membership Change: PT Agreement Form survey sent
         → Member selects: Standard Strength ($120/wk) or Optimal Results ($180/wk)
         → Member signs → MCPT fields populated
         → "5. New Personal Training Client" workflow fires
         → PT frequency tag applied (1 p.wk / 2 p.wk / 3 p.wk)
         → Membership Pipeline stage updated → PT 1 p.wk / PT 2 p.wk / PT 3 p.wk
```

---

---

# Full Onboarding Journey Flow

```
[Sale Closed]
      │
      ▼
[4. New Member workflow fires]
      │
      ├── Contact added to Membership Pipeline (correct stage)
      ├── member tag applied
      ├── Goal tag applied (goal: lose weight / tone up / 300% stronger etc.)
      └── Stage-of-life tag applied (perimenopause / post partum / teen etc.)
      │
      ▼
[Membership Agreement Form: Email workflow fires]
      │
      ▼
[Member completes Membership Agreement Form]
      │  Membership Type, Upfront Cost, Weekly Debit, First Debit Date, Signature
      │
      ▼
[Member completes Pre-Exercise Form]
      │  PAR-Q health screening, fitness goals, trainer selection
      │
      ▼
[Onboarding Session booked]
      │  On-boarding Session (30 Mins) calendar
      │
      ▼
[Day 1–7: Membership: First 7 Days — PUBLISHED]
      │  Welcome, gym orientation, app/platform access,
      │  coach introduction, early wins, FAQs
      │
      ▼
[Day 8–28: Membership: Day 8-28 — DRAFT]
      │  Habit reinforcement, consistency prompts, early check-in
      │  (may not be active)
      │
      ▼
[Day 29–90: Membership: Day 29-90 — PUBLISHED]
      │  Progress framing, milestone celebration, social proof,
      │  goal-specific content, community activation
      │
      ▼
[Day 91–180: Membership: Day 91-180 — DRAFT]
      │  Mid-membership engagement, goal reassessment,
      │  upgrade / add-on prompts (PT, extra sessions)
      │  (may not be active)
      │
      ▼
[Day 181–365: Membership: Day 181-365 — DRAFT]
      │  Long-term loyalty, referral prompts,
      │  anniversary recognition, review request
      │  (may not be active)
      │
      ▼
[Google Review Request (4 & 5 Stars Only)]
      │  Triggered at appropriate satisfaction point
      │
      ▼
[Decision Point]
      ├── Stays active → cycles through ongoing nurture
      ├── Membership Change → MCHO or MCPT survey sent, pipeline stage updated
      ├── Hold Request → Hold OS pipeline (see hold system documentation)
      └── Cancellation → Cancellation OS pipeline (see cancellation system documentation)
```

---

## System Notes & Observations

### What's working well
- **Agreement form captures all commercial terms in one step** — Membership Type, upfront cost, weekly debit, first debit date, and signature are all in a single form, reducing back-and-forth
- **PAR-Q (Pre-Exercise Form) is fully integrated into onboarding** — health screening provides liability coverage and flags injury risk before a member trains for the first time
- **Goal tagging at sign-up enables personalised lifecycle sequences from Day 1** — members can be routed to goal-specific workflows (Lose Weight, Tone Up, Strength For Life etc.) immediately
- **Membership Pipeline gives a clean, real-time view of plan distribution** across all 9 membership tiers including PT frequency breakdown
- **MCHO and MCPT surveys standardise plan change agreements** with digital signatures, providing the same legal protection as the initial agreement
- **Stage-of-life segmentation is built in** — perimenopause, post partum, teen, and pregnancy-planning members can receive tailored content from the moment they join

### Current gaps / things to review
- **Days 8–28, 91–180, and 181–365 are in draft** — the full 365-day lifecycle is architecturally complete but largely inactive. Three of the five lifecycle windows are dark. If these workflows have not been intentionally paused, publishing them would be the single highest-leverage retention improvement available
- **No automated trigger for Membership Change workflows is visible** — the MCHO and MCPT surveys exist and the Agreement Form: Email workflows are published, but no explicit trigger initiating a membership change request appears in the workflow list. Changes are likely initiated manually by staff, which creates a process dependency and a risk of inconsistent delivery
- **"Test - First 7 Days" is published alongside the live First 7 Days workflow** — both are active (`10f3c717` and `d6dd7a5f`). Confirm whether contacts are being double-enrolled or whether the test version is being used for a specific segment. The test version should be reviewed and either retired or formalised
- **No win-back or lapsed member re-engagement workflow visible** — the `old member` tag exists but there is no automated sequence targeting lapsed or churned members beyond the short-term cancellation retention pathways. A 30/60/90-day post-cancellation win-back sequence is not documented
- **PT Block fields (Service, Start, Trainer) are free-text TEXT fields** — no standardisation makes reporting on PT block performance by trainer or service type unreliable. Converting to structured field types (SINGLE_OPTIONS for Trainer, RADIO for Service) would improve reporting accuracy
- **Stage-of-life field exists in two variants** — `gKk8C5noKS1Gs81vKafA` (group `9klbgmldALQR9VbYrMr8`, options include "Post Partum") and `tGaGYawO3Q4AAPnuznF7` (group `GuiXAoJoZHSIaS669O8A`, options include "Postpartum") have slightly different option sets and keys. Dual population risk — consolidation should be reviewed
- **Membership Type field options include "Fit & Flexible" listed twice** — the MULTIPLE_OPTIONS field (`1SgYibtlIuophn9FYAh8`) lists: `Fit & Flexible, Strong, Fit & Flexible, Fast Track Package`. The duplication appears to be a data entry error in the field configuration and should be audited and corrected
- **No explicit "strong" pipeline stage** — the Membership Agreement form includes "Strong" as a Membership Type option, but the Membership Pipeline has "Strength & Sculpt" (stage 2) as its equivalent. Confirm these are the same product and that the agreement form and pipeline stage are mapped consistently
