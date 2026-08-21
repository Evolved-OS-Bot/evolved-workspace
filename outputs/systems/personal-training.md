# Personal Training Sales & Delivery System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-23

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

> **30 July 2026 audit warning:** this describes the intended legacy design, not a reliable live roster. The Membership Pipeline currently reports 43 opportunities that are not attached to any visible stage, while all four PT stages display zero. The published PT onboarding workflow still records a successful `PT Only / Won` opportunity action, but recent contacts including Vaishnavi Vakacharla are returned by pipeline search without appearing in a visible stage. Use the governed operating-data hub and booking, payment and lifecycle evidence for current PT service until the opportunity model and orphaned records are repaired.

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

> **Live audit note, updated 23 July 2026:** The canonical current trainer roster is Megan, Piper, Nora, Katrina and Leisa. The detailed tables below are the April system snapshot and deliberately retain former or inactive configurations as historical evidence. The current GHL settings UI is authoritative for booking. Marnie's three PT calendars and all three Meroe PT calendars were deleted. Live name and ID searches also confirmed that all four documented Beth calendars and all four documented Hannah calendars are already absent; no further deletion was required. Before Meroe's final calendar was removed, Kanika's replacement schedule was created in Nora's 30-minute calendar as 26 verified recurring instances through 28 October and all 22 future Meroe event records were deleted. Removing the final calendar also removed Kanika's completed 23 June Meroe appointment from GHL's active contact-appointment feed; the audit retains the occurrence as historical evidence. Katrina's and Leisa's 30-, 45- and 60-minute PT calendars remain active; their Intro Session calendars are inactive.

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

> This April snapshot shows triage calendars for Hannah and Megan. Live verification on 23 July 2026 confirmed Hannah's calendar is already absent. Megan is the intentional sole Injury Triage owner for now.

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
| 3.1. New Personal Training Client | **published; upstream-enrolled** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` |
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
3. Workflow sends the booking-confirmation email and 24-hour SMS reminder
4. Intro session delivered by trainer
5. Post-session: client agrees to start PT
6. "PT Agreement Form: Email" workflow fires → agreement form sent
7. Client completes Personal Training Agreement Form (IYWmTQ4BxvjM4qiP0iTZ)
   - PT Agreement Date Signed field populated
   - Two initials fields signed
   - Signature captured
8. An upstream workflow enrols the contact into "3.1. New Personal Training Client"
9. Contact moves to PT stage in Membership Pipeline (PT Only / PT 1 p.wk / PT 2 p.wk / PT 3 p.wk)
10. PT block fields populated: PT Block Service, PT Block Start, PT Block Trainer
11. Contact tagged: personal training, pt block – 13wk tracking or pt block – 24wk tracking
12. Ongoing sessions booked against trainer's 30/45/60 min PT calendar
```

The live workflow history on 22 July showed nine enrolments in the available 30-day window, including four contacts still waiting for appointment-relative steps. Some completed histories name an older `After Session Check In SMS` action that is absent from the current builder. The current published workflow contains only the booking email and 24-hour SMS; it creates no post-session, no-show or staff handoff.

---

# PART 2: PT Onboarding — Membership Upgrade (Existing Member)

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| PT Agreement Form: Email | **published** | `f8c76dc6-907d-4e69-9f23-6989e2b10447` |
| 3.1. New Personal Training Client | **published; upstream-enrolled** | `b5d32a65-1983-40fb-bc35-e53dfaa482ad` |

---

## Survey

**Membership Change: PT Agreement Form**
**Survey ID:** `w8j2Hc5KRu7MCYBEnmKb`

This is the upgrade path for existing members adding PT to their current membership. It uses the MCPT fields to capture package selection and signature.

---

## Membership Upgrade to PT Flow (Step by Step)

```
1. Existing gym member agrees to add PT
2. Staff manually sends Membership Change: PT Agreement Form
3. Member completes survey:
   - MCPT: PT Choice — selects package
   - MCPT: Signature — signs agreement
4. No verified notification or fulfilment workflow fires
5. Staff must notice and manually process the change
```

### Membership-change PT survey audit: 30 July 2026

The survey has zero submissions from 1 January 2024 through 30 July 2026. Its native email notification and autoresponder are both off.

The live `PT Agreement Form: Email` workflow does not send or process this survey; it triggers only after the separate `Personal Training Agreement Form` is submitted. The survey's two package choices, `$120 p/wk` Standard Strength and `$180 p/week` Optimal Results, do not define session duration or frequency and must not be automated while the PT pricing framework remains proposed.

The survey also displays placeholder `https://www.example.com` Privacy Policy and Terms of Service links. Resolve the intended offer, pricing, legal links and Admin Eve processing ownership before using or connecting this survey.

### Live onboarding audit: 22 July 2026

`3.1. New Personal Training Client` has no native trigger, but it is deliberately entered through Add to Workflow actions elsewhere. Recent history proves production use: Emma Spowart entered on 30 June, and Grace Arnell entered twice on 13 July with the enrolment reason `Another workflow action`.

The observed execution removed the contact from the Studio Appointment and Strength Assessment nurture workflows, attempted to remove a sales opportunity, added `personal training` and `strength assessment showed`, updated a contact field, sent an SMS, added the Review Request tag, enrolled the contact in `Membership: First 7 Days`, and created or updated a Membership Pipeline opportunity. One Remove Opportunity step returned an error because no matching opportunity existed, but the remaining onboarding actions completed.

The exact upstream source was resolved on 29 July. Grace submitted the Personal Training Agreement Form twice, at 1:22:13 pm and 1:25:09 pm on 13 July. Each `PT Agreement Form: Email` execution finished by adding her to `3.1`, producing destination executions at 1:22:24 pm and 1:30:57 pm.

`3.1. New Personal Training Client` is now reserved for one-time welcome and account setup. Allow re-entry was disabled, multiple-opportunity entry remains disabled, the workflow was saved and its published state was verified. A later legitimate PT agreement can still run its agreement-specific processing, but it cannot repeat the New PT Client SMS, lifecycle removals, review-request tag, First 7 Days enrolment or pipeline setup.

### PT agreement worksheet mapping defect: 28 July 2026

Live read-only builder inspection confirmed that `PT Agreement Form: Email` creates incomplete rows by configuration. Its Sales action maps identity, source, salesperson and attribution, but leaves Product, Trainer Assigned, Cash Taken, Added to Trainerize and Debits Set Up empty. Its Active PT action maps identity and `{{user.first_name}}` as Personal Trainer, but leaves Session Length, Sessions per week, Session Rate and Weekly Debit empty.

This is not an intermittent Sheets failure. The action is successfully appending exactly what it is configured to append. Erica Asler's 27 July rows exposed the defect: Stripe and Trainerize were correct, while the unmapped columns remained blank until owner-authorised correction on 28 July.

On 29 July, the exact duplicate cause was confirmed. Vaishnavi entered the Fast Track membership-agreement workflow once and the PT-agreement workflow once; both workflows appended Sales and Active PT rows for the same 28 July service date. The membership workflow created the complete records, while the PT workflow created the incomplete repeats.

Peter approved removal of the incomplete repeats. The published PT-agreement workflow now runs its worksheet actions only when Membership Type does not include `Fast Track Package`; Fast Track clients skip those writes but still enter `3.1. New Personal Training Client`. This preserves all onboarding functions and gives the membership workflow sole ownership of Fast Track worksheet creation.

The longer-term target remains a two-stage, idempotent write: capture structured agreed terms first, then enrich the same row only when Stripe proves the subscription or first paid invoice and Trainerize proves provisioning. Missing required terms should create an Admin exception instead of an operationally incomplete row.

The implementation-ready source authority, state model, allowlisted columns, exception reasons, rollout gates and acceptance tests are documented in `outputs/systems/pt-roster-self-mending.md`.

---

# PART 3: PT Delivery

---

## Active Session Booking

Once a client is on a PT block, all sessions are booked directly against per-trainer, per-duration calendars. All PT calendars are `personal` type.

**Session durations available per trainer:**

| Duration | Megan | Piper | Nora | Katrina | Leisa |
|---|---|---|---|---|---|
| 30 min | Yes | Yes | Yes | Yes | Yes |
| 45 min | Yes | Yes | Yes | Yes | Yes |
| 60 min | Yes | Yes | Yes | Yes | Yes |

---

## Injury Triage During Delivery

If a client sustains an injury during their PT block, the injury triage pathway applies:

```
1. Injury identified during session or reported by client
2. Triage session booked:
   - Injury Triage - Megan (Knee8V0fRcHxmpu3W0Fb)
3. Triage determines whether client can continue modified training or requires hold/cancellation
4. If hold required → PT Hold workflow initiated (see Hold System documentation)
5. If cancellation required → PT Cancellation workflow initiated (see Cancellation System documentation)
```

> Megan is the intentional sole Injury Triage owner. Clients working with another trainer should be routed to Megan when triage is required.

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

### Live booking-field repair: 23 July 2026

The workflow is now named `PT: Block Tracking & 13-Week Rebooking` (`280a2ca3-0f51-4f03-b5dc-c271c2ef8075`). When one of the 15 current PT calendars receives a booking, it adds `pt block – 13wk tracking` if absent and writes:

- PT Block Start: current date
- PT Block Trainer: `{{appointment.user.name}}`
- PT Block Service: `{{calendar.name}}`

It then waits 10 weeks, notifies the contact owner, creates a `Re-book {{contact.first_name}}` task assigned to Admin Eve and sends Admin Eve a separate notification. All task and notification copy now requests the next 13 weeks. The workflow waits a further 21 days, emails the contact owner with `info@theevolvedgym.com.au` copied as the Week 13 check, then removes the tracking tag.

General re-entry and multiple-opportunity execution are disabled. Appointment triggers can still re-enter after the previous execution ends, which permits a later block to begin. The tracking tag remains in place for the full 91 days, so routine appointments during the current block cannot rewrite the block fields.

Final coverage is Megan, Piper, Nora, Katrina and Leisa at 30, 45 and 60 minutes: 15 triggers in total. All six former Marnie and Wileen dependencies were removed or converted, and the workflow remained published. The fields now explicitly describe the current 13-week PT block, beginning with the first qualifying booking while the tracking tag is absent.

### Live booking-continuity shadow pilot: 23 July 2026

`pt_booking_shadow` is deployed to Railway as a structurally read-only audit service. It reconciles the active PT cohort every Monday at 5:30 am Brisbane time against the complete 15-calendar registry, infers each client's canonical pattern, checks 13-week coverage and records evidence in persistent SQLite history.

The Admin Eve report separates healthy coverage, internal gaps, no future bookings, hypothetical top-ups, pattern-confirmation cases, active holds and cancellation-boundary exceptions. The first audit read 107 contacts and made no GHL changes.

`SHADOW_MODE=true` is enforced at startup, and the GHL client contains no appointment write or delete methods. The existing Week 10 rebooking workflow remains the live operational fallback while four weekly reports are reviewed. The authenticated targeted-recheck endpoint exists, but optional GHL event-trigger workflows are not yet connected.

### Active roster, payment and booking reconciliation: 25 July 2026

`reference/sops/active-client-payment-and-booking-reconciliation.md` is the canonical Admin procedure for reconciling `Active PT`, `Active SGPT`, payment evidence, holds, cancellations and GHL bookings.

The procedure separates actual bank cash, confirmed current weekly PT income, scheduled PT run-rate and prepaid PT sales. Stripe remains the default payment rail, while completed PTMinder/EziDebit receipts may evidence approved legacy payers through manual review because the booking-continuity controller does not connect to that processor.

Standard Fast Track is one $149 weekly payment allocated across both active-client sheets: $99 in `Active SGPT` and $50 in `Active PT`. The full receipt is counted once as cash, and a Fast Track audit is incomplete unless both allocation rows are present and the PT allocation agrees with the recorded session count and rate.

An approved Fast Track PT add-on increases only the `Active PT` component. Shelley Wilson's service from 3 August 2026 is $99 SGPT plus two weekly 30-minute PT sessions at $50 each, producing one $199 weekly receipt; GHL holds the current `Fast Track Package` and `PT 2 p.wk` service state, while booking continuity verifies both weekly appointments.

Trainerize remains Shelley's active training-program account and does not receive separate PT session credits. PT booking entitlement is governed by the Active PT row and GHL appointments, so changing Trainerize would create a competing balance.

The 25 July audit rule also requires every cancelled, deleted or no-show appointment to be checked against its scheduled start, GHL activity timestamp, nearby conversation history and any approved hold evidence. A no-show or cancellation within 24 hours remains chargeable and consumes the session; an administrative deletion for an approved hold does not become chargeable merely because staff removed the calendar event later.

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
| Who is your personal trainer? | RADIO | Megan / Piper / Nora / Katrina / Leisa | `contact.who_is_your_personal_trainer` | `YWkGI9PYbF8jP22NKpbQ` |

> Corrected 23 July 2026: both trainer option fields use the canonical roster supplied by the owner: Megan, Piper, Nora, Katrina and Leisa.

---

## PT-Related Cancellation System Fields (Reference)

These fields are part of the Cancellation System but are referenced within PT workflows:

| Field | Type | Options | Key | ID |
|---|---|---|---|---|
| CS: - PT Interest | RADIO | No, I prefer to continue with the cancellation | `contact.mc__pt_interest` | `16T3kQEDKwi8rKB0HXv3` |
| CS: PT Package Offer - Declined | RADIO | I've paid for the Reset & I'm ready to continue with my cancellation / No thanks, I'll continue without help | `contact.mc_pt_package_offer__declined` | `sl0xCbukOJzcgvwGALEz` |
| CS: Schedule/Time - PT Interest | RADIO | No thanks, continue with cancellation | `contact.mc_scheduletime__pt_interest` | `IzejdzAxvG64C320Mldv` |
| CS: Style/Gym - PT Interest | RADIO | Yes please, show me the offer / No, continue with my cancellation | `contact.mc_rescue_package` | `3rTck8l7mW1UmhN4x1Hj` |
| CS: Results/Value - Coach Contacted | SINGLE_OPTIONS | Megan / Piper / Nora / Katrina / Leisa | `contact.mc_resultsvalue__coach_contacted` | `rxxE4BpClaV7YBrvNLWy` |

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
| PAR-Q | Current health-screening form | `yziUG4EO90xQMtBx5xU1` |

> The current PAR-Q captures health screening before the physical assessment. The obsolete zero-submission Pre-Exercise Form (`tUmSYWgC90QLMHycVotC`) was deleted on 31 July 2026; its ten historical field definitions and the values held on three River-to-Rooftop contacts were preserved.

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
- **Injury triage ownership is intentionally clear**: Megan is the sole triage owner for now, and the former Hannah calendar is already absent

### Current gaps / things to review
- **Membership Pipeline opportunity records are orphaned:** 43 of 135 pipeline opportunities are not attached to a visible stage. The published `3.1. New Personal Training Client` action targets `PT Only / Won`, but a 28 July successful execution still produced a search-visible, stage-invisible result. Decide whether the pipeline is historical sale classification or current service ownership before repairing the action and reconciling records. Current PT service must come from the governed operating-data hub, payment, booking and lifecycle evidence.
- **No dedicated PT pipeline** — PT clients sit in Membership Pipeline stages (PT Only, PT 1 p.wk, PT 2 p.wk, PT 3 p.wk). There is no pipeline tracking intro session → agreement → active → renewal → churn specifically for PT. This makes it difficult to see where PT prospects are in the sales process before they sign
- **PT Block Trainer remains an automation-fed TEXT field**: retain it while the repaired block-tracking workflow writes `{{appointment.user.name}}` from the first qualifying booking of each 13-week block. The field itself is not the governed staff roster
- **Cover-session attribution is an accepted low-frequency limitation**: live inspection on 24 July 2026 confirmed that `PT Block Trainer` is written from `{{appointment.user.name}}`. If the first qualifying appointment after the 91-day lock clears is delivered by a temporary cover coach, that coach becomes the recorded block trainer. Rebooking now belongs to Admin Eve and is intended to become continuity-controller automation, so this rare attribution edge case does not justify another ownership field or a published-workflow change
- **Trainer option inconsistency resolved on 23 July 2026**: both cancellation fields and the Strength Assessment survey now contain Megan, Piper, Nora, Katrina and Leisa; the survey also retains `I can't remember`
- **Beth and Hannah calendar cleanup is closed**: live searches by name and all eight documented IDs returned no calendars on 23 July 2026; no deletion was required
- **Live fulfilment remains reminder-led while continuity is audited in shadow mode**: `PT: Block Tracking & 13-Week Rebooking` remains the operational fallback. The Railway shadow pilot now inspects booked-through dates, future coverage, holds and cancellation boundaries, but deliberately creates, changes and deletes nothing until its accuracy gate is met
- **No PT client retention/check-in sequence visible** — unlike SGPT members who have Day 8-28, Day 29-90, Day 91-180 sequences, there is no equivalent ongoing engagement workflow for PT clients
- **Draft hold workflow copies** — `Copy - HS: PT Hold Form Submitted` and `Copy - HS: Extended PT Hold Form Submitted` are both in draft. Purpose unclear — may be testing new versions or may be abandoned
- **Health-screening dependency resolved**: the production Strength Assessment path uses current `PAR-Q` (`yziUG4EO90xQMtBx5xU1`). The unrelated legacy Pre-Exercise Form was deleted after zero-submission and dependency verification.
