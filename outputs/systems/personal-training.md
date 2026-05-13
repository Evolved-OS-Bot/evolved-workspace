# Personal Training Sales & Delivery System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-01

---

## Overview

The Personal Training system covers the full lifecycle of a PT client: lead capture and intro session booking, the intro session experience, agreement signing, active delivery across all trainer calendars, and client lifecycle tagging. PT sits within the Membership Pipeline (not a standalone pipeline) using dedicated PT stages. Agreement signing is handled via a separate form and workflow. Delivery is managed through per-trainer per-duration calendars for 30, 45, and 60-minute sessions. Injury triage and intro session calendars are also per-trainer.

Two parallel onboarding paths exist depending on how a client enters:
- **Intro session path** — new PT lead books an intro session, nurture fires, then converts to PT agreement
- **Membership upgrade path** — existing gym member upgrades to PT via a Membership Change: PT Agreement form

PT holds (standard and extended) are handled by separate workflows and forms — see the Hold System documentation. PT cancellations are handled by the Cancellation System documentation.

---

## Pipeline: Membership Pipeline
**Pipeline ID:** `fkEvrFkTihYkdb3bpprd`

PT clients occupy the following stages within the shared Membership Pipeline:

| Position | Stage | ID |
|---|---|---|
| 5 | PT Only | `58247f13-4a47-40f8-8289-35d62fc138b3` |
| 6 | PT 1 p.wk | `9ce28fb1-f43b-472a-ac11-1b4c147b202b` |
| 7 | PT 2 p.wk | `01d615da-4bd4-4bf3-a5c6-54332588367d` |
| 8 | PT 3 p.wk | `edf7f617-e058-438a-978a-330fa262ef8e` |

> There is no standalone PT pipeline. PT frequency (1x, 2x, 3x per week) is tracked by which Membership Pipeline stage the contact occupies. PT Only is for clients on PT without an SGPT membership.

---

## Tags

| Tag | Purpose |
|---|---|
| `personal training` | General PT client flag |
| `pt only` | PT client without a gym membership |
| `old pt client` | Previously held a PT block; no longer active |
| `pt block – 13wk tracking` | Active 13-week PT block being tracked |
| `pt block – 24wk tracking` | Active 24-week PT block being tracked |
| `1 p.wk` | PT frequency: 1 session per week |
| `2 p.wk` | PT frequency: 2 sessions per week |
| `3 p.wk` | PT frequency: 3 sessions per week |
| `intro` | Intro session booked or attended |

---

## Calendars

### Intro Session Calendars

| Calendar | Type | ID |
|---|---|---|
| Intro Session - Beth | personal | `ZGqYZun9jWcVqIo0O6u9` |
| Intro Session - Leisa | personal | `UTOhZ4UA8XDPYEZend4p` |
| Intro Session - Marnie | personal | `EvUpbuzC59WjEkbf12Ux` |
| Intro Session - Megan | personal | `tc9BC56PdRNQGQmY0CgN` |
| Intro Session - Piper | personal | `Nbzw8JiElSyeXdDqBLnQ` |

### Injury Triage Calendars

| Calendar | Type | ID |
|---|---|---|
| Injury Triage - Hannah | personal | `4asZ1oldru57moSFEKdB` |
| Injury Triage - Megan | personal | `Knee8V0fRcHxmpu3W0Fb` |

> Injury Triage is only available for Hannah and Megan. No triage calendar exists for Beth, Leisa, Marnie, or Piper.

### 30-Minute 1:1 PT Calendars

| Calendar | Type | ID |
|---|---|---|
| 30 Min 1:1 PT - Leisa | personal | `pOia47f6u6bDNvVMGWPo` |
| 30 Min 1:1 PT - Marnie | personal | `MzmH5oZEAMI83SzuTFjg` |
| 30 Min 1:1 PT - Megan | personal | `YT1U8WtmgGb5SO3BWE5n` |

> Note: Beth and Piper do not have a 30-minute PT calendar. The 30 Min 1:1 calendars for Beth, Hannah, Nora, and Piper (without "PT" in the name) appear to be non-PT session types (e.g. check-ins or coaching calls):
> - 30 Min 1:1 - Beth `CYsooQLsfZNw654fuVkW`
> - 30 Min 1:1 - Hannah `ga1masDAJAbY7Vg1p5C2`
> - 30 Min 1:1 - Piper `oSrXQVZhtv1tyL0bMFHe`
> - 30 Min 1:1 - Nora `zB8vInq5Hs44IrRKHkmx`

### 45-Minute 1:1 PT Calendars

| Calendar | Type | ID |
|---|---|---|
| 45 Min 1:1 PT - Beth | personal | `SAEvSLp0RBPlO4IywSUi` |
| 45 Min 1:1 PT - Leisa | personal | `xTF4OeRHi8vM8w7dcKuC` |
| 45 Min 1:1 PT - Marnie | personal | `pBmOPV2MvBbclaLF8E0w` |
| 45 Min 1:1 PT - Piper | personal | `skZi4KFJdJdoG2QqANoS` |
| 45 Minute 1:1 PT - Megan | personal | `JFVV14qlUY1QeLO62SMc` |

> Hannah and Nora also have 45-minute calendars without "PT" in the name:
> - 45 Min 1:1 - Hannah `rAV11ApEmTrpjmVorjPv`
> - 45 Min 1:1 - Nora `5lHjOoGaVFdJPNReVDeg`

### 60-Minute 1:1 PT Calendars

| Calendar | Type | ID |
|---|---|---|
| 60 Min 1:1 PT - Beth | personal | `b68CfIL98FnE0IyoU7OI` |
| 60 Min 1:1 PT - Leisa | personal | `HgRT8Vd7bsH2LZDeOzZz` |
| 60 Min 1:1 PT - Marnie | personal | `fphAhWDG3nA27kxTNh0r` |
| 60 Min 1:1 PT - Piper | personal | `EjHsuZD0s0vJUqPUXOMb` |
| 60 Minute 1:1 PT - Megan | personal | `UIdP5AYIwUW00hC7e5mN` |

> Hannah and Nora also have 60-minute calendars without "PT" in the name:
> - 60 Min 1:1 - Hannah `u6q2Lr1V4R3y8uwY0qvA`
> - 60 Min 1:1 - Nora `U1RSfH7BhPSSXdsBl61N`

### Calendar Summary by Trainer

| Trainer | Intro | Triage | 30min PT | 45min PT | 60min PT |
|---|---|---|---|---|---|
| Megan | `tc9BC56PdRNQGQmY0CgN` | `Knee8V0fRcHxmpu3W0Fb` | `YT1U8WtmgGb5SO3BWE5n` | `JFVV14qlUY1QeLO62SMc` | `UIdP5AYIwUW00hC7e5mN` |
| Leisa | `UTOhZ4UA8XDPYEZend4p` | — | `pOia47f6u6bDNvVMGWPo` | `xTF4OeRHi8vM8w7dcKuC` | `HgRT8Vd7bsH2LZDeOzZz` |
| Marnie | `EvUpbuzC59WjEkbf12Ux` | — | `MzmH5oZEAMI83SzuTFjg` | `pBmOPV2MvBbclaLF8E0w` | `fphAhWDG3nA27kxTNh0r` |
| Beth | `ZGqYZun9jWcVqIo0O6u9` | — | — | `SAEvSLp0RBPlO4IywSUi` | `b68CfIL98FnE0IyoU7OI` |
| Piper | `Nbzw8JiElSyeXdDqBLnQ` | — | — | `skZi4KFJdJdoG2QqANoS` | `EjHsuZD0s0vJUqPUXOMb` |
| Hannah | — | `4asZ1oldru57moSFEKdB` | — | — | — |

---

---

# PART 1: PT Onboarding — New Client (Intro Session Path)

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` |
| 5. New Personal Training Client | **published** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` |
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` |

---

## Form / Survey

**Personal Training Agreement Form**
**Form ID:** `IYWmTQ4BxvjM4qiP0iTZ`

---

## Intro Session Flow (Step by Step)

```
1. PT lead captured → intro session booked on trainer-specific Intro Session calendar
2. "Intro Session Nurture" workflow fires
3. Contact tagged: intro
4. Intro session delivered by trainer
5. Post-session: client agrees to start PT
6. "PT Agreement Form: Email" workflow fires → agreement form sent
7. Client completes Personal Training Agreement Form (IYWmTQ4BxvjM4qiP0iTZ)
   - PT Agreement Date Signed field populated
   - Two initials fields signed
   - Signature captured
8. "5. New Personal Training Client" workflow fires
9. Contact moves to PT stage in Membership Pipeline (PT Only / PT 1 p.wk / PT 2 p.wk / PT 3 p.wk)
10. PT block fields populated: PT Block Service, PT Block Start, PT Block Trainer
11. Contact tagged: personal training, pt block – 13wk tracking or pt block – 24wk tracking
12. Ongoing sessions booked against trainer's 30/45/60 min PT calendar
```

---

# PART 2: PT Onboarding — Membership Upgrade (Existing Member)

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` |
| 5. New Personal Training Client | **published** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` |

---

## Survey

**Membership Change: PT Agreement Form**
**Survey ID:** `w8j2Hc5KRu7MCYBEnmKb`

This is the upgrade path for existing members adding PT to their current membership. It uses the MCPT fields to capture package selection and signature.

---

## Membership Upgrade to PT Flow (Step by Step)

```
1. Existing gym member agrees to add PT
2. "PT Agreement Form: Email" workflow fires → Membership Change: PT Agreement Form sent
3. Member completes survey:
   - MCPT: PT Choice — selects package
   - MCPT: Signature — signs agreement
4. "5. New Personal Training Client" workflow fires
5. Contact stage updated to appropriate PT stage (PT 1 p.wk / PT 2 p.wk / PT 3 p.wk)
6. PT block fields populated
7. Sessions booked against trainer calendars
```

---

# PART 3: PT Delivery

---

## Active Session Booking

Once a client is on a PT block, all sessions are booked directly against per-trainer, per-duration calendars. All PT calendars are `personal` type.

**Session durations available per trainer:**

| Duration | Megan | Leisa | Marnie | Beth | Piper |
|---|---|---|---|---|---|
| 30 min | Yes | Yes | Yes | No | No |
| 45 min | Yes | Yes | Yes | Yes | Yes |
| 60 min | Yes | Yes | Yes | Yes | Yes |

---

## Injury Triage During Delivery

If a client sustains an injury during their PT block, the injury triage pathway applies:

```
1. Injury identified during session or reported by client
2. Triage session booked:
   - Injury Triage - Megan (Knee8V0fRcHxmpu3W0Fb) or
   - Injury Triage - Hannah (4asZ1oldru57moSFEKdB)
3. Triage determines whether client can continue modified training or requires hold/cancellation
4. If hold required → PT Hold workflow initiated (see Hold System documentation)
5. If cancellation required → PT Cancellation workflow initiated (see Cancellation System documentation)
```

> Only Megan and Hannah have injury triage calendars. Clients with other trainers must be routed to one of these two for triage.

---

## PT Block Tracking

Active PT blocks are tracked via tags and custom fields:

**Tags:**
- `pt block – 13wk tracking` — for 13-week PT packages
- `pt block – 24wk tracking` — for 24-week PT packages

**Custom fields used during delivery:**

| Field | Type | Key | ID |
|---|---|---|---|
| PT Block Service | TEXT | `contact.pt_block_service` | `Upyxa5ORrkYuzKmB9ikp` |
| PT Block Start | DATE | `contact.pt_block_start` | `qoSPND4o6aOmyMesj6Xs` |
| PT Block Trainer | TEXT | `contact.pt_block_trainer` | `gSYaeeCF2iiRSzJhKePT` |

---

---

# Custom Fields

---

## PT Agreement Fields
**Field Group ID:** `e3OeSDdsc8ZCJGnBKLL0`

| Field | Type | Key | ID |
|---|---|---|---|
| PT Agreement Date Signed | DATE | `contact.pt_agreement_date_signed` | `m7XNn6iutAoI4br2QUXu` |
| PT Agreement: Initial (24hrs Notice to reschedule) | TEXT | `contact.initial_i_understand_sessions_rescheduled` | `iQfRvYyyX2uwI1m7XTx1` |
| PT Agreement: Initial (30 Days Notice to cancel) | TEXT | `contact.initial_i_understand_terms_of_my_cancella` | `apLeFgJVKLuMIe8EKBjz` |
| Signature | SIGNATURE | `contact.signature` | `a9vPpSzxm4YVHF9Z5uPd` |

> These fields are populated when the client signs the Personal Training Agreement Form (IYWmTQ4BxvjM4qiP0iTZ). The two initials fields confirm the client understands (1) the 24-hour reschedule notice requirement and (2) the 30-day cancellation notice terms.

---

## PT Block Tracking Fields
**Field Group ID:** `9klbgmldALQR9VbYrMr8`

| Field | Type | Key | ID |
|---|---|---|---|
| PT Block Service | TEXT | `contact.pt_block_service` | `Upyxa5ORrkYuzKmB9ikp` |
| PT Block Start | DATE | `contact.pt_block_start` | `qoSPND4o6aOmyMesj6Xs` |
| PT Block Trainer | TEXT | `contact.pt_block_trainer` | `gSYaeeCF2iiRSzJhKePT` |

---

## Membership Change: PT Agreement Fields (Upgrade Path)
**Field Group ID:** `wcVp5BsbhFXgkyeLpiPj`

| Field | Type | Options | Key | ID |
|---|---|---|---|---|
| MCPT: PT Choice | RADIO | The Standard Strength Package ($120 p/wk) / The Optimal Results Package ($180 p/week) | `contact.mc_pt_choice` | `tw73Uz4jCyb4gxwCEKLy` |
| MCPT: Signature | SIGNATURE | — | `contact.mc_signature` | `lPQ96chOfOsFTCfMBcUX` |

---

## Trainer Assignment Field
**Field Group ID:** `6K5Faoqa02Be82SKmLv2`

| Field | Type | Options | Key | ID |
|---|---|---|---|---|
| Who is your personal trainer? | RADIO | Megan / Leisa / Marnie / Piper | `contact.who_is_your_personal_trainer` | `YWkGI9PYbF8jP22NKpbQ` |

> Note: Beth and Hannah are absent from this field's options. This may be an oversight or reflect their current role (e.g. Hannah as triage-only, Beth as newer to the roster).

---

## PT-Related Cancellation System Fields (Reference)

These fields are part of the Cancellation System but are referenced within PT workflows:

| Field | Type | Options | Key | ID |
|---|---|---|---|---|
| CS: - PT Interest | RADIO | No, I prefer to continue with the cancellation | `contact.mc__pt_interest` | `16T3kQEDKwi8rKB0HXv3` |
| CS: PT Package Offer - Declined | RADIO | I've paid for the Reset & I'm ready to continue with my cancellation / No thanks, I'll continue without help | `contact.mc_pt_package_offer__declined` | `sl0xCbukOJzcgvwGALEz` |
| CS: Schedule/Time - PT Interest | RADIO | No thanks, continue with cancellation | `contact.mc_scheduletime__pt_interest` | `IzejdzAxvG64C320Mldv` |
| CS: Style/Gym - PT Interest | RADIO | Yes please, show me the offer / No, continue with my cancellation | `contact.mc_rescue_package` | `3rTck8l7mW1UmhN4x1Hj` |
| CS: Results/Value - Coach Contacted | SINGLE_OPTIONS | Megan / Leisa / Hannah / Beth / Piper | `contact.mc_resultsvalue__coach_contacted` | `rxxE4BpClaV7YBrvNLWy` |

> PT upsell offers appear in three membership cancellation reason pathways: Schedule/Time, Results/Value, and New Style/New Gym. These use MCPT package pricing to present PT as a retention alternative to cancellation.

---

## PT Hold System Fields (Reference)
**Field Group ID:** `I9yvxOR5SClRM6mhguDn`

The hold fields are shared between membership and PT holds. The `HS: Hold Type` field distinguishes them:

| Field | Type | Options | Key | ID |
|---|---|---|---|---|
| HS: Hold Type | SINGLE_OPTIONS | Membership / PT | `contact.hold_type` | `J54g7CqeVbOHo6CoYzMA` |

See Hold System documentation for full field reference.

---

---

# Forms & Surveys

| Name | Type | ID |
|---|---|---|
| Personal Training Agreement Form | Form | `IYWmTQ4BxvjM4qiP0iTZ` |
| Membership Change: PT Agreement Form | Survey | `w8j2Hc5KRu7MCYBEnmKb` |
| PT Hold Form | Survey | `dXxuFDDTK6OkdvHKvurU` |
| Extended PT Hold Form | Survey | `bvz7PVsqRY5akgHfOHkH` |
| PT Cancellation Form | Survey | `JnwGk9ttNxiSAuqBxuBs` |
| Pre-Exercise Form | Form | `tUmSYWgC90QLMHycVotC` |

> The Pre-Exercise Form captures PAR-Q health screening questions (chest pain, dizziness, bone/joint problems, medication, etc.). It is likely completed prior to or at the intro session. See the custom fields group `JwbflBU2YDUaZb9godHU` for the full question set.

---

---

# Full Workflow Reference

| Workflow | Status | ID | Purpose |
|---|---|---|---|
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` | Fires when intro session is booked; nurtures lead through to PT conversion |
| 5. New Personal Training Client | **published** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` | Fires when PT agreement is signed; onboards new PT client |
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` | Sends the Personal Training Agreement Form to the client |
| HS: PT Hold Form Submitted | **published** | `636f1b2a-ec6b-4c8b-a3a4-e03e576e7bd2` | Handles standard PT hold submissions |
| HS: Extended PT Hold Form Submitted | **published** | `d4603307-f977-4317-9665-02347a4cab2c` | Handles extended PT hold submissions (5–12 weeks) |
| Copy - HS: PT Hold Form Submitted | draft | `af713a57-75df-4d2f-99b7-ee2d90b81f83` | Draft copy — likely in development |
| Copy - HS: Extended PT Hold Form Submitted | draft | `1d354249-e1cf-4aca-b7e8-9bd5492937e3` | Draft copy — likely in development |
| Send PT Cancellation Form | **published** | `4f09397c-a3a8-4c1b-982b-1bbcf2090459` | Sends PT cancellation form (see Cancellation System) |
| PT Cancellation Form Received | **published** | `bdd09a42-d00d-43ba-9201-d6cd0057e3ae` | Processes PT cancellation submission (see Cancellation System) |

---

---

# System Notes & Observations

### What's working well
- **Per-trainer per-duration calendars** give complete scheduling granularity — every trainer/duration combination has its own bookable calendar with its own ID
- **PT Agreement initials fields** enforce client acknowledgement of the two most critical terms (24hr reschedule, 30-day cancellation notice) at the point of signing — strong legal foundation
- **Dual onboarding paths** (new client intro session vs. existing member upgrade) are handled by separate forms and surveys, keeping flows clean
- **PT upsell built into membership cancellation** — three cancellation reason pathways (Schedule/Time, Results/Value, Style/New Gym) actively present PT packages as alternatives, with specific MCPT package options and pricing embedded in the offer
- **Block tracking tags** (13wk, 24wk) provide a lightweight way to monitor block progress without a dedicated PT pipeline
- **Injury triage pathway exists** with dedicated calendars — but only for Megan and Hannah, creating a coverage gap

### Current gaps / things to review
- **No dedicated PT pipeline** — PT clients sit in Membership Pipeline stages (PT Only, PT 1 p.wk, PT 2 p.wk, PT 3 p.wk). There is no pipeline tracking intro session → agreement → active → renewal → churn specifically for PT. This makes it difficult to see where PT prospects are in the sales process before they sign
- **PT Block Trainer is a TEXT field** — not a dropdown or linked record, so trainer assignment is free-text and prone to inconsistency. Compare to `Who is your personal trainer?` which is a RADIO field with four options (Megan, Leisa, Marnie, Piper)
- **Trainer options inconsistency** — `Who is your personal trainer?` has four options (Megan, Leisa, Marnie, Piper). `CS: Results/Value - Coach Contacted` has five options (Megan, Leisa, Hannah, Beth, Piper). Beth and Hannah are missing from the trainer assignment field but present in the coach contacted field
- **Injury triage coverage gap** — only Megan and Hannah have triage calendars. Clients training with Beth, Leisa, Marnie, or Piper must be routed to Megan or Hannah for any triage assessment
- **Beth and Piper have no 30-minute PT calendar** — these trainers can only offer 45 or 60-minute sessions. If a package requires 30-minute sessions, they cannot fulfil it
- **No PT renewal workflow visible** — there is no workflow for approaching the end of a 13-week or 24-week PT block to prompt renewal. The tracking tags exist but there is no automated trigger documented
- **No PT client retention/check-in sequence visible** — unlike SGPT members who have Day 8-28, Day 29-90, Day 91-180 sequences, there is no equivalent ongoing engagement workflow for PT clients
- **Draft hold workflow copies** — `Copy - HS: PT Hold Form Submitted` and `Copy - HS: Extended PT Hold Form Submitted` are both in draft. Purpose unclear — may be testing new versions or may be abandoned
- **Pre-Exercise Form linkage unclear** — the PAR-Q form (tUmSYWgC90QLMHycVotC) exists but no workflow is visible that explicitly sends or triggers it as part of PT onboarding
