# Plan: Five-Class Timetable and Trainer Capacity

**Created:** 2026-07-24
**Status:** In Progress
**Request:** Produce a decision-grade four-week SGPT capacity baseline, rank five expansion times, map primary and cover coaching, and model wage cost, contribution margin, launch gates and fill targets.

---

## Overview

### What This Plan Accomplishes

This child workstream converts the Five-Class Timetable outcome in the parent 30-day revenue brief into a bounded capacity decision. It establishes the evidence baseline, separates demand strength from launch readiness, identifies provisional trainer coverage, and defines the commercial and operational gates that must be approved before any live timetable change.

### Why This Matters

Timetable expansion is The Evolved's primary revenue lever, but the parent gross-value ceiling is only achievable if class demand, coaching coverage, floor capacity and wage cost all hold at the same time. A premature launch could move existing bookings without adding members, collide with PT revenue, or dilute coaching quality.

---

## Current State

### Relevant Existing Structure

- `plans/2026-07-24-30-day-revenue-execution-brief.md`: parent decision document and commercial guardrails.
- `context/strategy.md`: timetable expansion, trainer bench and peak PT protection priorities.
- `context/business-info.md`: 100 sqm usable training floor and direct PT/SGPT floor competition.
- `context/current-data.md`: 108 active SGPT members, 47 active PT clients and current revenue baseline.
- `outputs/staff-utilisation-analysis-2026-06-25.md`: stale one-week trainer-capacity study used only as historical context.
- `reference/sops/sculpt-and-strength-session.md`: delivery standard and a stated capacity of 15.
- Trainerize: live class definitions, class bookings, scheduled trainer and check-in fields.
- GHL: PT calendars, current future PT bookings and staff employment fields.

### Gaps or Problems Being Addressed

- The commercial strategy assumes 12 operational places per SGPT class, the delivery SOP says 15, and the active Trainerize class type used by the timetable is configured for 18.
- Trainerize contains four weeks of bookings but zero recorded check-ins across all 102 extracted classes.
- Trainerize's API does not expose waitlist or turn-away demand in the available class records.
- The current timetable contains 26 weekly classes, but two classes were missing in the first baseline week during a trainer transition.
- Employment hours and rates are incomplete in GHL for most trainers.
- Katrina's stored `Casual - Level 4A` rate is $30.68, which appears to be the pre-1 July 2026 Level 4A base rate rather than a current casual loaded rate.
- The canonical staff roster in workspace documentation excludes Jo, while Trainerize shows Jo delivering four current specialty classes per week.

---

## Proposed Changes

### Summary of Changes

- Create a dedicated decision output for this workstream.
- Preserve bookings, attendance, waitlist and floor-conflict evidence as separate measures.
- Rank the five candidate windows by demand and by launch readiness.
- Map provisional primary and cover trainers without assigning work.
- Model conservative wage cost and contribution margin.
- Define launch gates, staged fill targets and stop/continue/expand rules.
- Report proposed parent-brief and roadmap updates without editing those shared files.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `plans/2026-07-24-five-class-timetable-trainer-capacity.md` | Child workstream plan, evidence boundaries, decision gates and remaining actions. |
| `outputs/five-class-timetable-trainer-capacity-2026-07-24.md` | Decision-grade capacity baseline and provisional five-class launch recommendation. |

### Files to Modify

None. The shared parent brief, roadmap, live timetable, SOPs and staff records remain unchanged.

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Use four completed Monday-to-Sunday weeks:** The baseline covers 22 June to 19 July 2026, avoiding a partial current week.
2. **Do not call bookings attendance:** Trainerize check-ins were zero across the full extract, so attendance remains an explicit missing control.
3. **Show two rankings:** Demand confidence and launch readiness are different because the strongest commercial periods currently conflict with PT.
4. **Use 12 places only as the parent-model scenario:** The capacity discrepancy must be resolved before live approval.
5. **Treat zero concurrent PT as the original conservative baseline:** Peter replaced it on 24 July with the limited pilot exception recorded in Decision 9.
6. **Use provisional coverage only:** Trainer delivery history demonstrates capability, but availability and employment terms require Peter and Megan's approval.
7. **Charge an economic wage cost even when fixed hours exist:** Reallocating paid capacity has an opportunity cost and should not be shown as free.
8. **Keep the workstream isolated:** No Fast Track candidate, retention member or shared programme file is changed.
9. **Apply Peter's temporary coexistence approval:** A newly introduced low-volume group class may run with no more than one simultaneous 1:1 PT session when different trainers deliver them. Two PT sessions plus group are outside the approval.
10. **Use a daypart workforce model:** Piper is the morning anchor; Nora is the Tuesday/Thursday afternoon and evening anchor; Megan is not recurring delivery; Leisa is not the sole evening-cover dependency.
11. **Do not wholesale-transfer Nora's morning PT to Piper:** The 13-week audit found 71 appointments, 27 exact-time conflicts and a 26.25-hour peak combined morning delivery week before non-delivery duties.
12. **Use two 30-hour weekday anchors:** Piper opens at 5:00am Monday to Friday; Nora closes at 8:00pm Monday to Thursday and 7:00pm Friday. At 60 combined paid hours, daily continuous 5:00am-to-8:00pm coverage plus crossover is impossible; use a one-hour Friday-only crossover and demand-led casual middle coverage.
13. **Retain suitable PT with Nora:** Use Nora's longer Monday and Friday afternoon spans for current clients who can move, before transferring the remaining morning book to Piper.
14. **Consolidate current classes into anchor hours first:** Where GHL is clear and coaching is approved, use Piper for Tuesday 5:30am, Tuesday 9:00am and Friday 9:00am, and Nora for Friday 5:00pm and 6:00pm, before purchasing recurring casual class hours.
15. **Use the new casual for genuine parallel delivery:** The casual should absorb PT that must run beside Nora's new 5:00pm classes and provide cover, rather than becoming the default coach while a paid anchor is already on site.

### Alternatives Considered

- Treating Trainerize bookings as completed attendance was rejected because the check-in evidence is blank.
- Ranking only by current class occupancy was rejected because it ignores future PT floor conflicts.
- Assigning all five classes to Nora was rejected because the 10:00am pair contradicts the afternoon-anchor model, Saturday sits outside the weekday pattern, and the roster would have no resilient cover layer.
- Using the stored $30.68 casual rate was rejected as the sole planning rate because it appears stale and excludes casual loading and super.
- Replacing low-booked specialty classes was excluded because the requested scope is class expansion, not a live timetable redesign.

### Open Questions (if any)

1. Is the safe operational class cap 12, 15 or 18?
2. What source will supply actual attendance, waitlist and turn-away evidence?
3. Will Piper and Nora each accept the modelled 30-hour regular pattern and one-hour Friday crossover?
4. Are Leisa and Jo current employees, and what are their classifications, rates and permitted duties?
5. What numerical class-booking threshold ends Peter's temporary low-volume coexistence approval, and when must it be reviewed?
6. Which Nora clients will accept Monday or Friday afternoon appointments, which require Piper at the same time, and which need another trainer?
7. Has payroll applied the 1 July 2026 Fitness Industry Award increase and the correct casual loading?

---

## Step-by-Step Tasks

### Step 1: Complete the Four-Week Evidence Baseline

Extract and reconcile class bookings, class check-ins, class definitions, scheduled trainers and PT delivery for 22 June to 19 July 2026.

**Actions:**

- Confirm the 26-slot weekly timetable from Trainerize.
- Aggregate 102 delivered class records by slot and week.
- Aggregate GHL PT bookings and hours by trainer and week.
- Record missing attendance and waitlist evidence as blockers.
- Reconcile capacity values of 12, 15 and 18.

**Files affected:**

- `outputs/five-class-timetable-trainer-capacity-2026-07-24.md`

**Status:** Complete.

---

### Step 2: Rank Expansion Windows

Use bookings in comparable Sculpt & Strength dayparts as demand proxies, then test each candidate against the published timetable and already-booked future PT.

**Actions:**

- Rank Thursday 5:00pm, Tuesday 5:00pm, Tuesday 10:00am, Thursday 10:00am and Saturday 8:00am by strategic value, demand confidence and operational readiness.
- Produce a separate launch-readiness ranking.
- Preserve the current 26-slot timetable and treat every addition as Sculpt & Strength.
- Require the first later-week Thursday addition to repeat Monday's Glute Builder workout.
- Keep Saturday 6:00am deferred and record its recurring PT conflict.
- Preserve uncertainty where no direct class exists at the proposed time.

**Files affected:**

- `outputs/five-class-timetable-trainer-capacity-2026-07-24.md`

**Status:** Complete.

---

### Step 3: Map Primary and Cover Capacity

Create a provisional coaching map using verified recent Sculpt & Strength delivery, combined class/PT load, contractual evidence and direct appointment conflicts.

**Actions:**

- Use Piper as the proposed 30-hour Monday-to-Friday morning anchor and Nora as the proposed 30-hour Monday-to-Friday afternoon and evening anchor.
- Model Friday as the only crossover day while preserving Piper's 5:00am opening, Nora's 8:00pm Monday-to-Thursday close and Nora's 7:00pm Friday finish.
- Audit every future Nora morning PT appointment against Piper's PT, assessment and current class baseline.
- Retain appropriate Nora clients in longer Monday and Friday PM windows before treating them as transfer demand.
- Re-run GHL against the exact 30/30 shift boundaries and identify the smallest set of Piper boundary changes.
- Rebuild the visible Trainerize schedule from current member bookings and identify classes that can move from casual/owner delivery into paid anchor hours.
- Separate exact-time transfer candidates from clashes and calculate the combined weekly delivery load.
- Identify a primary and cover candidate for every proposed class without counting Megan as recurring delivery or Leisa as dependable evening cover.
- Calculate the primary's average and maximum client-facing load after the class is added.
- Flag missing roster, rate and availability evidence.
- Require Peter and Megan approval before any assignment is treated as real.

**Files affected:**

- `outputs/five-class-timetable-trainer-capacity-2026-07-24.md`

**Status:** Reframed and complete provisionally; paid-hour limits, recruitment and staff confirmation remain blocked by the no-contact guardrail.

---

### Step 4: Model Unit Economics

Calculate gross weekly value, conservative employment cost, contribution margin and break-even fill.

**Actions:**

- Retain the parent formula of four incremental SGPT members per weekly class at $99 per member.
- Use a conservative planning cost of $47 per weekday paid hour and $49 per Saturday paid hour.
- Model 1.25 paid hours per delivered class for delivery plus setup and close.
- Show a three-hour isolated-shift sensitivity where the class cannot be embedded into an existing shift.
- Separate gross value from net contribution.

**Files affected:**

- `outputs/five-class-timetable-trainer-capacity-2026-07-24.md`

**Status:** Complete as a planning model; payroll validation remains open.

---

### Step 5: Run the Approval Gates

Resolve evidence and ownership gaps before launch.

**Actions:**

- Peter and Megan approve one operational capacity number.
- Admin Eve or the coaching lead repairs check-in capture and supplies waitlist/turn-away evidence.
- Payroll validates current classifications, base rates, casual loading, super, allowances and roster treatment.
- Megan signs off floor coexistence and coaching quality.
- Peter approves the primary and cover roster in writing.
- Confirm no conflicting PT remains in the selected window.

**Files affected:**

- No workspace file is changed until explicit approval is received.

**Status:** Pending.

---

### Step 6: Stage the Launch

Launch only the smallest approved tranche if all gates pass, then release later classes one at a time as PT conflicts are removed and fill targets are met.

**Actions:**

- Confirm Nora's proposed Tuesday and Thursday 5:00pm, 6:00pm and 7:00pm block, then transfer or move Anika, Kanika and Rose where Nora cannot coach class and PT simultaneously.
- Confirm the 30/30 anchor roster, including Monday and Friday Nora PT spans, the Friday-only Piper/Nora crossover and the intentional Monday-to-Thursday middle gaps.
- Recruit or appoint a dependable evening casual before publishing the 5:00pm pair; do not make Megan recurring delivery or Leisa the sole cover dependency.
- Verify Piper's actual paid hours and approve a protected delivery ceiling before transferring only the first tranche of exact-time-clear morning PT.
- Recruit or appoint a morning-capable casual or second part-time trainer before publishing the Tuesday and Thursday 10:00am pair.
- Launch Thursday 5:00pm first, followed by Tuesday 5:00pm only after its client-transfer and cover gates are clear.
- Hold Saturday 8:00am until 8 August or verify and resolve the apparent two-client Leisa booking at 8:30am on 1 August.
- Measure bookings, unique members, actual attendance, displaced bookings and net SGPT member growth weekly.
- Do not release a blocked class merely because the first two perform.
- Apply the stop, continue and expand thresholds in the output.

**Files affected:**

- Live systems only after Peter's explicit approval.

**Status:** Pending approval.

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-07-24-30-day-revenue-execution-brief.md`
- `context/roadmap.md`
- `context/strategy.md`
- `context/business-info.md`
- `outputs/staff-utilisation-analysis-2026-06-25.md`
- `reference/sops/sculpt-and-strength-session.md`

### Updates Needed for Consistency

Proposed only, not applied:

- Parent brief: replace “five launchable classes” with five staged Sculpt & Strength candidates and separate strategic-priority and operational-readiness rankings.
- Parent brief: add the later-week Glute Builder repeat and defer Saturday 6:00am as a future shared-floor option requiring a separate coach from Deb's PT.
- Parent scorecard: distinguish bookings, check-ins, attendance, waitlist and turn-away demand.
- Roadmap: move this workstream from Scoped to In Progress and record the capacity/check-in/payroll gates.
- Strategy and SOP: reconcile the 12, 15 and 18 class-capacity values.
- Staff register: reconcile Jo's active delivery and complete current employment fields.

### Impact on Existing Workflows

No live workflow changes occur in this phase. Any approved class would create a new Trainerize class record and require a published staffing roster, but no such write is authorised by this plan.

---

## Validation Checklist

- [x] Parent brief read and treated as controlling.
- [x] Four completed weeks extracted.
- [x] Current 26-slot timetable verified.
- [x] Class bookings kept separate from attendance.
- [x] PT utilisation extracted by trainer.
- [x] Five candidate windows checked against future PT.
- [x] Primary and cover map marked provisional.
- [x] Wage model includes loading, super and paid-time sensitivity.
- [x] Gross revenue separated from contribution margin.
- [x] Fill targets include net-member and anti-cannibalisation measures.
- [x] No live timetable, staff contact or external write completed.
- [x] Parent brief and roadmap left unchanged.
- [ ] Operational class capacity approved.
- [ ] Attendance and waitlist evidence repaired.
- [ ] Employment terms and payroll rates approved.
- [ ] Primary and cover availability confirmed.
- [ ] Floor-capacity rule approved.

---

## Success Criteria

The workstream is complete when:

1. Peter and Megan approve the operational class capacity, low-volume coexistence threshold and review condition.
2. Four weeks of actual attendance and a usable waitlist/turn-away measure exist.
3. Every proposed class has an approved primary, approved cover and no unresolved PT conflict.
4. Payroll validates the wage assumptions and roster treatment.
5. Piper's paid-hour ceiling and the staged Nora-to-Piper transfer list are approved.
6. The two-part-time, two-deployable-casual operating structure is staffed without counting Megan as recurring coverage.
7. The first two classes meet their launch gates and staged fill targets without reducing coaching quality.
8. Remaining classes launch only after their specific blockers are cleared.

---

## Notes

The output is decision-grade for class bookings, published class delivery, PT utilisation and future PT conflicts. It is not yet decision-grade for actual attendance, waitlists, turn-away demand, operational capacity or final employment cost; those are explicit approval gates rather than hidden assumptions.
