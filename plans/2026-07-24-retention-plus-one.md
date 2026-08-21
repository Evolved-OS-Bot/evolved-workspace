# Plan: Retention Plus One

**Created:** 2026-07-24
**Status:** Draft
**Request:** Establish a rolling 13-week cancellation baseline, reconcile member check-ins with the audited lifecycle, define early-risk rules, and design one accountable 30/60/90-day retention process with a saved-revenue register.

---

## Overview

### What This Plan Accomplishes

This plan creates a controlled early-retention operating system for The Evolved. It uses a rolling cancellation baseline, explicit risk rules, owned 30/60/90-day actions, and verified commercial outcomes to target one additional retained client per month.

The first version remains manual or staff-approved. It does not publish workflows, contact members, alter billing, or modify the timetable or Fast Track workstreams.

### Why This Matters

The 30-day revenue brief identifies retention as one of three commercial levers. The local 13-week evidence shows material recurring revenue loss and concentration among newer members, while the live lifecycle audit confirms that routine member care after Day 7 is not operationally implemented.

One additional verified retained client per month reduces the current completed-cancellation count by roughly one sixth if the 13-week baseline remains representative. The process must prove that result without counting routine positive check-ins, unaccepted offers, holds that do not return, or unsupported counterfactual claims.

---

## Current State

### Relevant Existing Structure

- `plans/2026-07-24-30-day-revenue-execution-brief.md`: parent commercial decision document.
- `reference/evolved-manual/07-member-journey.md`: authoritative but incomplete member-journey source.
- `reference/evolved-manual/08-retention-system.md`: authoritative retention stub.
- `reference/sops/monthly-member-checkin.md`: current operational monthly check-in SOP.
- `outputs/trainer-portal/11-member-care.md`: downstream trainer course that expands beyond the current SOP.
- `outputs/trainer-portal/html/11-member-care.html`: downstream published-course format.
- `outputs/trainer-portal/quiz-csvs/11-member-care.csv`: downstream quiz.
- `outputs/systems/membership-lifecycle.md`: live lifecycle audit.
- `outputs/systems/cancellation-system.md`: cancellation fields, workflow and task audit.
- `outputs/systems/membership-hold.md`: hold and return journey audit.
- `data/private/integration-reporting/reconciliation.sqlite`: private GHL, Stripe and Trainerize reconciliation snapshot.
- `data/private/trainerize-longitudinal-audit/trainerize_longitudinal.sqlite`: private tracked-workout history used for an attendance-signal backtest.

### Gaps or Problems Being Addressed

- Only the First 7 Days lifecycle sequence is verified as operational.
- The monthly check-in SOP says to call every member monthly, but no live queue, trigger, completion measure, due date or persistent outcome register implements it.
- Day 8 to Day 365 workflow shells are incomplete or inert.
- Cancellation data is not currently reported as a rolling baseline by tier, tenure, reason and recurring revenue lost.
- PT cancellations capture no structured reason.
- Five of 18 completed cancellations in the baseline lack verified tier, tenure and recurring-debit data.
- Historical saves cannot be measured because there is no explicit save outcome and verification field.
- A simple absence or attendance-decline rule is not supported by the available cancellation backtest.
- The trainer course contains material retention content that is not yet present in the authoritative manual or SOP.

---

## Proposed Changes

### Summary of Changes

- Maintain a weekly 13-week cancellation and revenue-loss baseline.
- Create a single risk queue with explicit evidence, owner, due date, status and commercial value.
- Run milestone care at Days 30, 60 and 90 for the controlled MVP.
- Use direct red flags and multiple supporting signals rather than an opaque risk score.
- Separate verified saves, provisional saves, holds, downgrades, pending notices and completed cancellations.
- Backfill missing tier, tenure and recurring-debit evidence before calling the baseline complete.
- Add structured PT cancellation reasons in a later approved implementation.
- Reconcile the manual, SOP, trainer course and quiz through the required source-of-truth cascade before changing trainer-facing content.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `outputs/retention-plus-one/operating-system.md` | Evidence pack, baseline, risk rules, ownership, 30/60/90 process and measurement definitions. |
| `outputs/retention-plus-one/saved-revenue-register.csv` | Blank governed register for risks, interventions and verified commercial outcomes. |

### Files to Modify

No existing file is modified during the evidence and design phase.

Later implementation may require the following sequence, only after Peter approves the content and live operating model:

| File Path | Changes |
| --- | --- |
| `reference/evolved-manual/07-member-journey.md` | Reconcile the Day 7 to Day 90 journey and ownership. |
| `reference/evolved-manual/08-retention-system.md` | Replace the stub with the approved retention principles, definitions and escalation model. |
| `reference/sops/monthly-member-checkin.md` | Replace the unsupported monthly-everyone process with the approved operating procedure and revision history. |
| `outputs/trainer-portal/11-member-care.md` | Cascade the approved process into Course 11. |
| `outputs/trainer-portal/html/11-member-care.html` | Cascade the updated Course 11 source. |
| `outputs/trainer-portal/quiz-csvs/11-member-care.csv` | Audit and update every affected quiz item. |
| `outputs/systems/membership-lifecycle.md` | Record the approved live implementation after it is verified. |
| `outputs/systems/cancellation-system.md` | Record any approved data-field or outcome changes after live verification. |

### Files to Delete

None.

---

## Design Decisions

### Key Decisions Made

1. **Use 13 fully completed Monday-to-Sunday weeks:** The initial window is 20 April to 19 July 2026. This aligns with the parent brief's weekly reporting convention and avoids mixing a partial week into the baseline.
2. **Separate requests, notices and completed cancellations:** A form submission is not automatically recurring revenue lost. The current pipeline state determines whether the record is stalled, in notice, or completed.
3. **Do not present a churn rate yet:** The historical weekly active-member denominator is not preserved in the available snapshot.
4. **Treat the current revenue baseline as a verified floor:** Thirteen completed records have tier and weekly-debit evidence. Five completed records remain commercially unclassified.
5. **Do not infer historical saves:** The live system has no structured save outcome. A removed or lost opportunity is not sufficient counterfactual evidence.
6. **Use direct rules, not a composite score:** Staff must understand why a member is in the queue and what action is due.
7. **Treat attendance as a supporting signal:** The backtest found that eight of nine completed cancellers with any tracked-workout history had trained within seven days of cancelling. A blunt absence rule would miss most observable cases.
8. **Target the first 90 days:** Eight of thirteen completed cancellations with known tenure occurred within three months of joining.
9. **Ask directly about financial and schedule friction:** These reasons account for eleven of fifteen completed membership cancellations with a captured reason.
10. **Verify saves after 28 days:** A claimed save remains provisional until the accepted state, active service and recurring billing remain verified for at least 28 days.
11. **Keep holds and downgrades distinct:** A hold protects revenue only after a verified return. A downgrade protects only the retained recurring amount.
12. **Reuse existing hold-return and PT-booking controls:** This plan consumes their verified signals but does not alter or duplicate their files.

### Alternatives Considered

- **Call every member every month:** Rejected for the MVP because it is not operationally implemented, creates high staff load, and does not focus effort on the concentrated early-tenure risk.
- **Automate Day 8 to Day 365 immediately:** Rejected because the audited workflows are incomplete or inert and ownership has not been proven.
- **Count every cancellation offer accepted as a save:** Rejected because acceptance alone does not prove continued active service or billing.
- **Use a points-based churn score:** Rejected because the available evidence does not support reliable weights and opaque scoring would weaken staff accountability.
- **Use attendance decline as the main trigger:** Rejected because the cancellation backtest does not support it as a standalone predictor.

### Open Questions

1. Will Peter confirm Piper as the accountable member-care owner, Admin Eve as queue controller, assigned trainers as delivery support, Megan as coaching escalation, and Peter as commercial verifier?
2. Is 28 days of verified active service and billing the accepted threshold for a verified save?
3. Should the MVP cover all new SGPT, Fast Track and PT clients, or exclude PT-only clients until PT cancellation reasons and revenue are reconciled?
4. Which system will hold the pilot queue and register: a controlled Google Sheet, GHL opportunities, or a local register reviewed manually?
5. Can the five commercially unclassified completed cancellations be manually reconciled against Stripe or other retained billing evidence?

---

## Step-by-Step Tasks

### Step 1: Approve the Measurement Contract

Approve the definitions of request, notice, completed cancellation, provisional save, verified save, hold, downgrade, gross recurring revenue lost and protected recurring revenue.

**Actions:**

- Confirm the 13-week reporting window convention.
- Confirm the 28-day verification period.
- Confirm that no churn rate is reported without an active-member denominator.
- Confirm that saved revenue uses the actual accepted recurring tier, not blended revenue.

**Files affected:**

- `outputs/retention-plus-one/operating-system.md`

### Step 2: Reconcile the Baseline Exceptions

Resolve the missing commercial data without changing live member state.

**Actions:**

- Reconcile the five completed cancellations with unknown tier, tenure or weekly recurring revenue.
- Separate membership, PT-only and Fast Track cancellation value.
- Investigate the one cancellation record stalled at Cancellation Form Received.
- Confirm whether the five Notice Period records completed, saved, held, downgraded or remain pending after their notice dates.
- Add a historical active-member denominator if an authoritative weekly snapshot exists.

**Files affected:**

- `outputs/retention-plus-one/operating-system.md`

### Step 3: Confirm the Accountable Operating Model

Obtain explicit staff acceptance before assigning recurring work.

**Actions:**

- Confirm accountable and supporting owners.
- Confirm Monday queue preparation, one-business-day red-flag SLA and Friday verification review.
- Set a maximum open caseload and escalation route.
- Confirm who may discuss holds, modifications, schedule alternatives and downgrades.

**Files affected:**

- `outputs/retention-plus-one/operating-system.md`

### Step 4: Build the Manual Pilot Queue

Create a controlled queue for the first 30/60/90-day cohort.

**Actions:**

- Enrol new members after the live First 7 Days sequence.
- Generate Day 30, Day 60 and Day 90 due actions.
- Add the approved risk triggers and evidence links.
- Exclude members in active cancellation from routine nurture.
- Route active holds through the existing Hold Return Journey.
- Use the existing PT booking continuity signal for PT future-booking gaps.
- Require owner, due date and disposition for every queue item.

**Files affected:**

- `outputs/retention-plus-one/saved-revenue-register.csv`
- Approved pilot queue location, to be selected

### Step 5: Run a Four-Week Staff-Approved Pilot

Operate manually before automating.

**Actions:**

- Complete due Day 30, Day 60 and Day 90 actions.
- Record member response, friction, action and next step.
- Escalate direct red flags within one business day.
- Review ambiguous attendance and booking signals before contact.
- Record staff time and queue volume.

**Files affected:**

- `outputs/retention-plus-one/saved-revenue-register.csv`

### Step 6: Verify Outcomes and Commercial Value

Measure outcomes without overstating saves.

**Actions:**

- Verify accepted state in GHL, Stripe and Trainerize.
- Keep saves provisional until the 28-day verification date.
- Record holds as holds until return plus 28-day verification.
- Record downgrade protected revenue at the new recurring amount.
- Record completed cancellation revenue loss at the actual prior recurring amount.
- Report missing evidence as unknown, not zero.

**Files affected:**

- `outputs/retention-plus-one/saved-revenue-register.csv`
- `outputs/retention-plus-one/operating-system.md`

### Step 7: Decide Whether to Standardise

Review effectiveness, workload and false positives after four weeks.

**Actions:**

- Compare completed cancellations with the rolling baseline.
- Report verified saves, provisional saves, holds, downgrades and completed cancellations separately.
- Calculate completion SLA, owner compliance and risk-rule precision.
- Stop weak signals, continue effective actions and propose only bounded automation.

**Files affected:**

- `outputs/retention-plus-one/operating-system.md`

### Step 8: Execute the Source-of-Truth Cascade if Approved

Update trainer-facing content only after Peter approves the operating model.

**Actions:**

- Assess the approved process against Sections 07 and 08 of the manual.
- Update the manual first.
- Update the monthly-member-check-in SOP and increment its revision history.
- Cascade to Course 11 Markdown and HTML.
- Audit and update the Course 11 quiz.
- Render or inspect downstream content and verify formatting rules.

**Files affected:**

- `reference/evolved-manual/07-member-journey.md`
- `reference/evolved-manual/08-retention-system.md`
- `reference/sops/monthly-member-checkin.md`
- `outputs/trainer-portal/11-member-care.md`
- `outputs/trainer-portal/html/11-member-care.html`
- `outputs/trainer-portal/quiz-csvs/11-member-care.csv`

### Step 9: Consider Bounded Live Automation

No automation is authorised by this plan.

**Actions:**

- Draft entry, exit, re-entry, contact-frequency and failure rules.
- Preserve a named staff owner for every member conversation.
- Test in a non-member or staff-approved environment.
- Obtain Peter's explicit approval before publishing or contacting members.

**Files affected:**

- To be determined after pilot approval

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-07-24-30-day-revenue-execution-brief.md`
- `context/strategy.md`
- `context/roadmap.md`
- `reference/evolved-manual/07-member-journey.md`
- `reference/evolved-manual/08-retention-system.md`
- `reference/sops/monthly-member-checkin.md`
- `outputs/trainer-portal/11-member-care.md`
- `outputs/trainer-portal/html/11-member-care.html`
- `outputs/trainer-portal/quiz-csvs/11-member-care.csv`
- `outputs/systems/membership-lifecycle.md`
- `outputs/systems/cancellation-system.md`
- `outputs/systems/membership-hold.md`

### Updates Needed for Consistency

No shared files are changed in this planning tranche.

Proposed later updates:

- Add the verified baseline and measurement limitations to the parent revenue brief.
- Mark Retention Plus One In Progress in the roadmap when Peter approves owners and pilot launch.
- Record final pilot outcomes in the parent brief and roadmap after the operating window.
- Update `CLAUDE.md` only if the process becomes a recurring workspace command, script or permanent structural component.

### Impact on Existing Workflows

The design consumes evidence from the First 7 Days reply routing, Hold Return Journey, cancellation pipeline and PT booking continuity controller. It does not alter them.

Any future lifecycle automation must replace or formally retire the inert Day 8 to Day 365 shells rather than publishing another overlapping sequence.

---

## Validation Checklist

- [ ] The baseline covers exactly 13 completed Monday-to-Sunday weeks.
- [ ] Requests, notices, stalled records and completed cancellations reconcile to source records.
- [ ] Tier, tenure, reason and revenue coverage are reported with unknowns visible.
- [ ] No churn rate is shown without a denominator.
- [ ] Risk rules distinguish direct evidence from provisional operational thresholds.
- [ ] Every risk has an owner, due date, evidence, action and disposition.
- [ ] Saves, holds, downgrades and completed cancellations are separate outcomes.
- [ ] Every verified save has 28-day billing and active-service evidence.
- [ ] The pilot does not duplicate timetable, Fast Track or PT booking files.
- [ ] No live workflow, member contact or external write occurs without Peter's approval.
- [ ] Any later trainer-content change follows manual to SOP to Markdown to HTML and quiz cascade.
- [ ] The shared parent brief and roadmap remain unchanged during concurrent workstreams.

---

## Success Criteria

The implementation is complete when:

1. A decision-grade rolling 13-week baseline exists with no hidden unknowns.
2. At least 90% of due 30/60/90 actions are completed on time.
3. Every direct red flag is owned within one business day.
4. Every claimed save passes the 28-day verification standard.
5. The process produces one additional verified retained client per month over a sufficiently comparable operating period.
6. Staff workload and member experience remain acceptable without blanket concessions.

---

## Notes

The first 13-week baseline is documented in `outputs/retention-plus-one/operating-system.md`. It is a reproducible starting point from the latest complete local reconciliation snapshot, not a final lifetime retention analysis.

The shared parent brief and roadmap were deliberately not modified because other commercial workstreams may be active.
