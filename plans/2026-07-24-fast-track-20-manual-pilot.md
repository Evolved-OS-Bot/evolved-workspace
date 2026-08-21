# Plan: Fast Track 20 Manual Pilot

**Created:** 2026-07-24
**Status:** Scoped: existing-member service-change pathway approved; implementation and capacity remain gated
**Request:** Reconcile Strong and Fast Track delivery, reserve capacity for up to 20 upgrades, define eligibility, and run a full-price manual pilot.

---

## Overview

### What This Plan Accomplishes

This plan creates a controlled Strong-to-Fast Track upgrade pilot with ten validated upgrades as the minimum result and 20 as the stretch target. It begins by repairing incumbent Fast Track fulfilment, then releases new offers only against named recurring 30-minute PT slots.

The plan is a child of `plans/2026-07-24-30-day-revenue-execution-brief.md`. It does not modify the shared parent brief, timetable files, retention files, live memberships, bookings, or member communications.

### Why This Matters

Each upgrade increases weekly revenue by $50 and consumes 30 minutes of trainer time. Ten upgrades add $500 per week and require five delivery hours; 20 add $1,000 per week and require ten delivery hours.

The live audit found that incumbent Fast Track delivery is not yet healthy enough to absorb a sales push. Three provisionally active members have no future PT booking, eight have less than a 13-week forward horizon, and only two have a complete 13-week horizon.

---

## Current State

### Relevant Existing Structure

- `plans/2026-07-24-30-day-revenue-execution-brief.md`: parent commercial decision document.
- `context/current-data.md`: 108 unique active SGPT members, 63 weekly PT bookings, and 36.5 booked PT hours.
- `reference/product-offerings.md`: Strong is $99 per week; Fast Track is $149 per week and includes one weekly 30-minute PT session.
- `outputs/systems/pt-booking-shadow-review-log.md`: current PT booking-continuity evidence and source hierarchy.
- `outputs/trainerize-reporting-reconciliation/latest-reconciliation-summary.md`: GHL, Stripe, and Trainerize reconciliation baseline.
- `data/private/integration-reporting/`: identified reconciliation and performance evidence.
- `data/private/fast-track-20/`: private identified pilot registers created for this workstream.
- `outputs/fast-track-20/readiness-brief.md`: share-safe findings, gates, economics, and proposed parent updates.

### Gaps or Problems Being Addressed

- The `Active SGPT` sheet contains 109 active rows but only 108 unique people because one Strong member is duplicated.
- The current Strong roster resolves to 88 unique operational members, not the 75 records shown by the membership pipeline.
- Seven Strong members are already in Notice Active and must not enter an upgrade campaign.
- Only 53 Strong members are currently decision-grade from the available evidence; 21 require a missing-signal review and seven require identity or status resolution.
- The `Active SGPT` sheet contains 14 Silver rows, but one member has a confirmed Fast Track end and Strong downgrade on 24 July. The current Fast Track roster is therefore provisionally 13.
- Five of the 13 provisionally active Fast Track members lack a Stripe entitlement signal in the reconciliation snapshot and require commercial-source confirmation.
- Three of the 13 have no future PT booking.
- Eight more have less than 13 weeks of forward PT coverage.
- The timetable-and-trainer capacity baseline is not yet available, so no ten-hour capacity claim can be approved.
- The existing-member Fast Track commercial and delivery rule is approved. The remaining gates are named capacity, controlled system implementation and acceptance.

### Approved Existing-Member Fast Track Service-Change Pathway: 3 August 2026

Use this pathway when a current Strong, Fit & Flexible, Fit & Flexible or other existing member accepts Fast Track at the end of a Full Standards Assessment. It is the approved current pathway, not a PIF pathway. The thirteen-session specialised series replaces the acquisition four-session onboarding pathway for this existing-member conversion: the member is already beyond initial onboarding. It does not alter the acquisition Fast Track onboarding entitlement.

1. The assessment coach records the member's assessment rationale, priority gap or gaps, coach-selected next standard, initial 8–12 week focus, session progression and nominated recurring 30-minute PT slot.
2. Take one immediate A$50 payment for the first one-to-one PT session. This is a discrete first-session payment and must receive its own exact payment reference.
3. In the same administrative session, change the recurring membership to A$149 per week. The new recurring amount takes effect on the member's next scheduled debit, not retrospectively or mid-period.
4. Book the first specialised one-to-one session as soon as possible within that same week. Give the assessment coach first priority; if they cannot supply the series, allocate the next available suitable trainer.
5. Create thirteen weekly 30-minute specialised one-to-one bookings, including the first session where it is the first occurrence of the series. They must target the recorded gaps and progress the member toward the coach-selected next standard; they are not generic PT appointments.
6. Do not offer, infer or process a PIF route in this release. A PIF Fast Track path requires a separate future owner decision.

The signed Fast Track variation must distinguish the immediate A$50 first-session payment from the A$149 weekly recurring membership, state the next scheduled debit date, confirm the specialised PT purpose and identify the first booked session. It must not imply that the A$50 payment is a credit against the recurring membership unless a future approved term expressly says so.

The change request must carry a coach handoff packet to Trainerize and the booked trainer: assessment date and assessor; assessment rationale; priority gap or gaps; selected next standard; initial 8–12 week focus; first-session goal; planned session progression; programme link or Trainerize assignment; primary trainer, alternate trainer if used, recurring slot and booked-through date. Trainerize provision is accepted only when that packet is visible to the delivery coach and the prescribed programme or first-session brief matches it.

### Specialised Programme Library Dependency

Each Fast Track change must select a reusable specialised twelve-week programme from the member's primary Full Standards Assessment gap. The initial named library includes `Improve Hinge`, `Improve Squat`, `Improve Lunge` and `Improve Fitness`; equivalent programmes may be added only when their standard or movement-gap purpose is defined. The coach selects the appropriate programme from assessment evidence, then adjusts it for the individual. The thirteen sessions are therefore not a generic PT series.

Do not invent programme content in the service-change build. Before Trainerize provisioning can be accepted, the selected programme must exist in the approved library and the handoff must record: library programme name and version; primary assessment gap; supporting raw assessment evidence; coach-selected next standard; initial 8–12 week objective; permitted individual modifications; first-session goal; progression/reassessment checkpoint; assessment coach; booked delivery trainer; and the Trainerize programme or assignment reference. If no approved programme matches the evidence, the request is an exception rather than a generic PT booking.

The change request remains idempotent: one signed variation has one request ID; an exact retry must find the first-session payment, recurring Stripe update and specialised PT series rather than create any of them again. A change in trainer, slot, first-session payment, assessment prescription or effective boundary is a changed request and must fail closed for Admin Eve review.

---

## Proposed Changes

### Summary of Changes

- Reconcile and approve the Strong and Fast Track rosters using evidence grades.
- Repair incumbent Fast Track booking continuity before making new offers.
- Import ten approved weekly trainer hours from the timetable-and-trainer capacity workstream.
- Create a 20-slot capacity ledger, with one recurring 30-minute slot per potential upgrade.
- Validate members through mandatory commercial, coaching, engagement, goal, and schedule gates.
- Release a maximum of ten offers in Wave 1.
- Review delivery before releasing up to ten more offers in Wave 2.
- Keep all member contact, booking, billing, and membership changes manual and approval-controlled.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `outputs/fast-track-20/readiness-brief.md` | Share-safe reconciliation, delivery findings, eligibility model, pilot design, and proposed parent updates. |
| `data/private/fast-track-20/incumbent-fast-track-roster-2026-07-24.csv` | Identified incumbent roster and fulfilment evidence. |
| `data/private/fast-track-20/candidate-review-register-2026-07-24.csv` | Identified objective pre-screen for coach, goal, and schedule validation. |
| `data/private/fast-track-20/capacity-and-upgrade-register.csv` | Approved slot inventory, offer decisions, fulfilment, and revenue evidence. Create only after capacity is approved. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| None during analysis | The parent brief, roadmap, timetable files, retention files, memberships, bookings, and external systems remain unchanged. |

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Incumbent delivery comes first:** Do not add Fast Track members while three incumbents have no future PT booking and only two have full 13-week coverage.
2. **The pipeline is not the roster:** Use the unique active sheet roster, deterministic identity matching, commercial entitlement, Trainerize access, cancellation state, and calendar delivery as separate evidence.
3. **Capacity is sold by exact slot:** No upgrade is offered without a trainer, weekday, start time, duration, recurring horizon, and floor-conflict check.
4. **Ten upgrades consume five hours:** Reserve the full ten-hour stretch capacity before Wave 1, but release only ten slots initially.
5. **Approved first-session payment and recurring rate:** Collect A$50 immediately for the first one-to-one session, then move the recurring membership to A$149 per week on the next scheduled debit. Do not discount, retrospectively prorate or treat the A$50 as an inferred credit.
6. **Data ranks; coaches qualify:** Objective data creates a review order. Megan or the assigned coach confirms the actual coaching need, member goal, scope, and suitability.
7. **Attendance is a readiness gate:** Default eligibility requires at least four completed workouts in the prior 30 days. A lower-attendance member enters only with a documented coach rationale.
8. **PIF is out of scope:** Do not offer or infer a paid-in-full Fast Track route in this release. It requires a separate commercial decision.
9. **Manual waves prevent overselling:** Wave 1 stops at ten accepted upgrades. Wave 2 begins only after the first ten pass the fulfilment review.
10. **Validated means delivered:** An acceptance is not a validated upgrade until billing, agreement, systems, recurring booking, and first-session delivery are verified.

### Alternatives Considered

- **Offer Fast Track to all 88 Strong members:** Rejected because roster confidence, capacity, coaching fit, and schedule compatibility vary materially.
- **Use the 75 Strong and 13 Fast Track pipeline counts:** Rejected because the pipeline mixes service history and status and misses current operational records.
- **Use Nora's stale 12 unused hours as the ten-hour reservation:** Rejected because the evidence covers one late-June week and does not account for class expansion.
- **Launch ten upgrades while capacity for the second ten remains unknown:** Rejected because the parent programme requires the ten-hour stretch capacity to be identified before scale.
- **Automate outreach or membership changes:** Rejected until the manual pilot proves member response, staff ownership, and fulfilment.

### Open Questions (if any)

1. Resolved 5 August: the thirteen-session specialised weekly PT series replaces the acquisition four-session Fast Track onboarding pathway for existing-member assessment conversions. Acquisition Fast Track members retain their separate four-session onboarding pathway.
2. Which payment source explains the five provisionally active Fast Track members without a Stripe entitlement signal?
3. Are the three incumbents with no future PT booking true fulfilment failures, holds, commercial transitions, or stale tier records?
4. Which ten weekly trainer hours are approved after class expansion, wage cost, floor use, and cover requirements are included?
5. What minimum contribution margin must the pilot protect after wage and payroll on-cost?

---

## Step-by-Step Tasks

Execute these tasks in order during implementation.

### Step 1: Approve the Roster Evidence Rules

Use deterministic email matching first. Name-only matching is prohibited.

**Actions:**

- Confirm the one duplicated Strong row and the two Strong records without email.
- Resolve the seven Notice Active Strong members and exclude them.
- Review the 21 two-signal Strong members and the seven weak-identity or weak-status records.
- Confirm the 13-member Fast Track roster after the 24 July downgrade.
- Verify commercial entitlement for the five Fast Track members without a Stripe signal.
- Record Peter-approved rulings in the private registers.

**Files affected:**

- `data/private/fast-track-20/incumbent-fast-track-roster-2026-07-24.csv`
- `data/private/fast-track-20/candidate-review-register-2026-07-24.csv`

---

### Step 2: Repair Incumbent Fast Track Fulfilment

No upgrade offers may be released until each true incumbent has a valid delivery disposition.

**Actions:**

- Resolve the three members with no future PT booking.
- Extend, confirm, or correctly classify the eight partial booking horizons.
- Confirm that holds and cancellations are current rather than stale.
- Verify weekly entitlement, trainer, session length, and booked-through date for all 13.
- Require 13 weeks of forward coverage or an approved exception with a dated rebooking owner.

**Files affected:**

- `data/private/fast-track-20/incumbent-fast-track-roster-2026-07-24.csv`
- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 3: Import and Approve Ten Weekly Trainer Hours

Treat the timetable-and-trainer capacity baseline as a blocking dependency.

**Actions:**

- Import named availability from the timetable-and-trainer capacity workstream.
- Exclude slots that conflict with SGPT delivery, setup, close-down, cover, leave, or floor capacity.
- Prefer contiguous off-peak blocks where member demand supports them.
- Record trainer, weekday, time, duration, peak status, primary owner, cover owner, start date, and 13-week horizon.
- Calculate wage and payroll on-cost per hour.
- Approve exactly 20 recurring 30-minute slots before Wave 1.

**Files affected:**

- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 4: Resolve the Existing-Member Commercial and Onboarding Path

Create a manual, staff-readable path without changing the general sales or onboarding SOPs during the pilot.

**Actions:**

- Use the approved A$50 immediate first-session payment and A$149 weekly recurring debit on the next scheduled debit.
- Confirm whether the thirteen-session specialised series is the complete existing-member pathway or whether defined onboarding work is embedded in its first four sessions.
- Confirm the exact signed variation, Stripe payment and recurring-update actions, GHL canonical fields, Trainerize programme-library assignment, tags and booking steps.
- Exclude PIF from this release.
- Require the assessment handoff packet and an approved twelve-week programme selection before creating the PT series; confirm no discount, trial rate, retrospective proration or temporary concession is used.

**Files affected:**

- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 5: Complete Coach Eligibility Review

The initial data pre-screen contains 36 members; the private register gives an initial 25-member review order.

**Actions:**

- Confirm a real coaching need: assessment gap, technique limitation, injury or condition within scope, stalled progression, or a specific strength goal.
- Confirm at least four workouts in the prior 30 days, or document why weekly PT is the appropriate attendance intervention.
- Confirm the member wants individual coaching and faster or more specific progression.
- Confirm the member can attend one exact recurring slot for at least 13 weeks.
- Exclude active holds, notice periods, current PT clients, unresolved billing, and unresolved roster identities.
- Require a final score of at least 10 out of 15 and every mandatory gate.

**Files affected:**

- `data/private/fast-track-20/candidate-review-register-2026-07-24.csv`
- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 6: Release Wave 1

Release no more than ten approved slots.

**Actions:**

- Peter explicitly approves member contact before outreach begins.
- Use one-to-one coach conversations, preferably after a reassessment or documented coaching review.
- Present the A$50 first-session payment and the A$149 weekly membership that begins on the next scheduled debit, with the first specialised PT session booked in the same week.
- Record offer date, coach, slot, response, objection, follow-up date, and outcome.
- Hold only one approved slot per live offer and release it after the approved response window.
- Stop Wave 1 when ten upgrades are accepted or the approved offer list is exhausted.

**Files affected:**

- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 7: Fulfil and Validate the First Ten

An upgrade counts only after fulfilment.

**Actions:**

- Verify the signed variation, the cleared A$50 first-session payment and the A$149 recurring Stripe change at the next scheduled debit.
- Verify the GHL membership type, stage, and current status.
- Verify the existing Trainerize identity is reused and the approved specialised twelve-week programme is assigned with its handoff record visible to the delivery trainer.
- Assign and verify the thirteen weekly specialised PT sessions, prioritising the assessment coach and recording any alternative suitable trainer.
- Deliver the first specialised PT session within the same week as acceptance.
- Confirm no gym-caused missed session, duplicate booking, class-floor conflict, or unowned delivery issue.

**Files affected:**

- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 8: Review and Release Wave 2

Wave 2 can add no more than the remaining capacity up to 20 total upgrades.

**Actions:**

- Review the first ten for billing, booking, first-session delivery, member response, trainer workload, and floor conflict.
- Continue only if every upgrade has a recurring slot and no unresolved gym-caused fulfilment failure.
- Release up to ten additional slots using the same eligibility and approval rules.
- Stop at 20 accepted and validated upgrades.

**Files affected:**

- `data/private/fast-track-20/capacity-and-upgrade-register.csv`

---

### Step 9: Report Results and Proposed Shared Updates

Keep shared files untouched until Peter coordinates the parent programme close.

**Actions:**

- Report offers, acceptances, validated upgrades, weekly revenue added, annualised revenue added, reserved hours, delivered sessions, missed sessions, and objections.
- Calculate contribution margin using the approved wage and payroll on-cost.
- Report roster exceptions separately from pilot results.
- Prepare proposed updates for the parent brief and roadmap without applying them.

**Files affected:**

- `outputs/fast-track-20/readiness-brief.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-07-24-30-day-revenue-execution-brief.md`
- `context/strategy.md`
- `context/current-data.md`
- `reference/product-offerings.md`
- `reference/sops/post-sale-member-onboarding.md`
- `reference/evolved-manual/07-member-journey.md`
- `reference/evolved-manual/08-retention-system.md`
- `outputs/systems/membership-lifecycle.md`
- `outputs/systems/pt-booking-shadow-review-log.md`
- `outputs/systems/trainerize-product-automation-audit.md`

### Updates Needed for Consistency

Propose, but do not apply during concurrent workstreams:

- Replace pipeline candidate counts with approved roster counts in the parent brief.
- Add incumbent Fast Track delivery remediation as an exit gate.
- Add the approved existing-member upgrade commercial treatment.
- Add actual capacity, wage cost, and contribution margin when the dependency is complete.
- Update the roadmap only after Peter confirms pilot status and outcomes.

### Impact on Existing Workflows

The pilot uses existing read-only reconciliation and calendar evidence. It does not change the timetable, retention workflows, sales automation, membership workflows, booking logic, or Trainerize automation unless Peter separately approves implementation.

---

## Validation Checklist

- [ ] The 108 unique SGPT members reconcile to 88 Strong, 13 Fast Track, six Limited, and one approved transition or exception as applicable.
- [ ] Every Strong candidate has a stable identity, active commercial state, active Trainerize access, and no notice or hold.
- [ ] Every incumbent Fast Track member has a verified commercial entitlement and delivery disposition.
- [ ] The three no-future-booking cases are resolved.
- [ ] All true incumbents have 13-week coverage or an approved dated exception.
- [ ] Twenty recurring 30-minute slots are approved with named trainers and cover.
- [ ] The ten hours do not conflict with approved class expansion.
- [ ] Wage and payroll on-cost are included in contribution margin.
- [x] The approved A$50 first-session payment and next-debit A$149 recurring rule are recorded.
- [ ] The sole remaining onboarding-path decision is recorded: whether the specialised thirteen-session series replaces or embeds the acquisition onboarding pathway.
- [ ] PIF is absent from the variation, checkout, staff instructions and workflow target.
- [ ] The assessment handoff packet, approved twelve-week programme reference and delivery-trainer acknowledgement are present before the first session.
- [ ] Every offered member passes mandatory eligibility gates.
- [ ] No member is contacted without Peter's explicit approval.
- [ ] No upgrade is counted before agreement, billing, systems, booking, and first delivery are verified.
- [ ] Wave 2 is not released before the first-ten review.
- [ ] Shared parent and roadmap changes remain proposed rather than applied.

---

## Success Criteria

The implementation is complete when:

1. The Strong and Fast Track rosters are decision-grade and every exception has an owner.
2. Incumbent Fast Track delivery is healthy or each exception has an approved dated resolution.
3. Ten weekly trainer hours are reserved as 20 real recurring 30-minute slots.
4. At least ten full-price upgrades are validated, adding $500 per week and $26,000 annualised.
5. Up to 20 upgrades are validated only if the first ten are fulfilled cleanly, adding up to $1,000 per week and $52,000 annualised.
6. No upgrade compromises SGPT capacity, coaching quality, member safety, or incumbent delivery.

---

## Notes

At the current 63 weekly PT bookings and 36.5 booked hours, ten upgrades would lift the simple booking baseline to 73 bookings and 41.5 hours. Twenty would lift it to 83 bookings and 46.5 hours, before changes in incumbent top-ups, cancellations, holds, reschedules, or class expansion.

The gross incremental yield is $100 per reserved trainer hour before wage and payroll on-cost: two $50 weekly upgrade increments are supported by one trainer hour. This is not contribution margin until employment cost is included.
