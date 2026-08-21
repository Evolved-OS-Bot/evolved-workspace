# Retention Plus One Operating System

**Status:** Evidence and design complete; pilot approval pending  
**Parent decision document:** `plans/2026-07-24-30-day-revenue-execution-brief.md`  
**Baseline window:** 2026-04-20 to 2026-07-19  
**Evidence cutoff:** Latest complete local reconciliation snapshot started 2026-07-23 09:04 UTC  
**Commercial objective:** One additional verified retained client per month

## Executive Decision

The retention MVP should focus on the first 90 days, direct financial and schedule friction, negative replies, booking continuity and hold returns.

It should not use attendance decline as a standalone churn predictor. The available backtest shows that most observable cancellers were still training shortly before cancellation.

The first operating version should be manual or staff-approved. No live workflow changes, member contact, billing changes or external writes are authorised by this document.

## Evidence Base

| Source | What it establishes | Limitation |
| --- | --- | --- |
| Parent revenue brief | Commercial target, guardrails and provisional ownership | Does not contain the detailed cancellation baseline |
| Membership lifecycle audit | First 7 Days is operational; Day 8 to Day 365 is incomplete or inert | Does not measure churn outcomes |
| Cancellation system audit | Forms, reasons, fields, stages, tasks and current reason workflows | No structured verified-save field |
| Hold system audit | Return tasks and dates are live | Workflow assumes completion after three days |
| Monthly member check-in SOP | Intended monthly calls, notes and red-flag escalation | No live queue, trigger, SLA or completion measure |
| Course 11 | Expanded member-care training | Downstream content is ahead of the manual and SOP |
| Reconciliation snapshot | GHL contact, cancellation, pipeline, Stripe and Trainerize state | Primarily a current snapshot, not a complete event ledger |
| Trainerize longitudinal store | Tracked workouts before cancellation | Workout tracking is incomplete for some members and is not identical to class attendance |

## Rolling 13-Week Cancellation Baseline

### Outcome Reconciliation

| Outcome at evidence cutoff | Records | Treatment |
| --- | ---: | --- |
| Completed cancellation | 18 | Included in completed-cancellation baseline |
| Notice Period (Current) | 5 | Pending; not yet counted as completed revenue loss |
| Cancellation Form Received | 1 | Stalled exception requiring investigation |
| Total requests | 24 | Gross demand to cancel |

The 18 completed cancellations comprise 15 membership cancellations and 3 PT cancellations. The five active notices comprise 4 membership and 1 PT.

Average completed cancellations were 1.38 per week, or approximately 6.0 per average month. One additional verified retained client per month represents roughly a 16.7% improvement against that count, subject to comparable volume and member mix.

This is not a churn rate. A reliable historical weekly active-member denominator is not present in the available snapshot.

### Weekly Baseline

| Week | Requests | Completed | Notice active | Stalled | Verified weekly recurring revenue lost |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20–26 Apr | 3 | 2 | 0 | 1 | $248 |
| 27 Apr–3 May | 3 | 3 | 0 | 0 | $99 |
| 4–10 May | 1 | 1 | 0 | 0 | $99 |
| 11–17 May | 2 | 2 | 0 | 0 | $99 |
| 18–24 May | 2 | 2 | 0 | 0 | $198 |
| 25–31 May | 4 | 4 | 0 | 0 | $297 |
| 1–7 Jun | 0 | 0 | 0 | 0 | $0 |
| 8–14 Jun | 3 | 3 | 0 | 0 | $248 |
| 15–21 Jun | 1 | 1 | 0 | 0 | $99 |
| 22–28 Jun | 1 | 0 | 1 | 0 | $0 |
| 29 Jun–5 Jul | 2 | 0 | 2 | 0 | $0 |
| 6–12 Jul | 0 | 0 | 0 | 0 | $0 |
| 13–19 Jul | 2 | 0 | 2 | 0 | $0 |
| **Total** | **24** | **18** | **5** | **1** | **$1,387** |

The recent weeks contain active notices because of the 30-day notice period. They should mature into a completed, saved, held or downgraded outcome before cohort comparison.

### Completed Cancellations by Tier

| Tier | Completed cancellations | Verified weekly recurring revenue lost | Annualised recurring revenue lost |
| --- | ---: | ---: | ---: |
| Strong, Fit & Flexible | 11 | $1,089 | $56,628 |
| Fast Track Package | 2 | $298 | $15,496 |
| Unknown | 5 | Unknown | Unknown |
| **Verified floor** | **13 of 18** | **$1,387** | **$72,124** |

The unknown group includes three PT cancellations and two membership cancellations. The $72,124 figure is a verified floor, not the full loss.

### Completed Cancellations by Tenure

| Tenure at cancellation request | Completed cancellations | Share of known-tenure records |
| --- | ---: | ---: |
| Less than 3 months | 8 | 61.5% |
| 3 to less than 6 months | 2 | 15.4% |
| 6 to less than 12 months | 3 | 23.1% |
| 12 months or more | 0 | 0.0% |
| Unknown | 5 | Not included |

Tenure uses the membership agreement signed date where available. It is missing for five records.

The strongest observable concentration is within the first three months. This supports a 30/60/90-day MVP before broader monthly lifecycle automation.

### Completed Cancellations by Reason

| Reason | Completed cancellations | Share of captured membership reasons |
| --- | ---: | ---: |
| Financial reasons | 8 | 53.3% |
| Schedule and life commitments | 3 | 20.0% |
| Moving or long-term travel | 2 | 13.3% |
| Different training style or environment | 1 | 6.7% |
| Other | 1 | 6.7% |
| PT reason not captured | 3 | Not included |

Financial and schedule friction account for 11 of 15, or 73.3%, of completed membership cancellations with a captured reason.

No completed cancellation in the window recorded Results/Value, Health/Injury, or Training Elsewhere as the primary reason. This does not prove those risks are absent; the sample is small and reason pathways changed during the period.

## Attendance Backtest

The 18 completed cancellation records were matched against tracked Trainerize workouts:

- 16 matched a Trainerize client.
- 9 had any tracked-workout history before cancellation.
- 8 of those 9 had a tracked workout within seven days of requesting cancellation.
- 1 had last trained 15 to 28 days before requesting cancellation.
- 7 matched clients had no tracked-workout history.
- 2 did not match a Trainerize client.

Decision: a simple rule such as "no attendance for 14 days" is not an evidence-backed primary trigger for this cohort. Attendance decline may support a risk assessment, but it must not independently label a member as likely to cancel.

## Reconciliation of the Existing Check-In SOP

| Current statement or dependency | Audited reality | Decision for the MVP |
| --- | --- | --- |
| Call one month after joining, then every month | No live recurring queue or trigger implements this | Operate owned Day 30, 60 and 90 milestones first |
| Try three calls, then send a text | No completion metric or contact-frequency control | One planned contact sequence per milestone with disposition and next action |
| Record notes in Trainerize | No shared outcome or revenue register | Keep coaching notes in Trainerize; record operational outcome in the controlled register |
| Email red flags to the info inbox | First 7 Days now uses assigned Admin Eve and Piper tasks | Use a persistent owned risk item; email may remain a notification, not the system of record |
| Trainer handles PT interest | Commercial and delivery capacity must be verified | Route to the separate Fast Track or PT process without duplicating its register |
| Health concern is a generic red flag in the SOP | Course 11 says modification and Injury Triage come first | Resolve in the manual and SOP cascade before changing trainer-facing content |
| Formal six-month reassessment and Future-Proofing Score appear in Course 11 | They are not established in the current retention manual or SOP | Keep outside the MVP until the source content is reconciled |
| Hold return is handled manually | Hold Return Journey already creates T-7 and return-day coach tasks | Consume its exceptions; do not create a competing hold sequence |

## Evidence-Backed Early-Risk Rules

The MVP uses three levels:

- **Red:** direct member evidence or failed critical handoff. Action due within one business day.
- **Amber:** operational friction supported by available evidence. Staff reviews context before contact.
- **Watch:** weak signal that is measured but does not create member contact by itself.

| Rule | Level | Trigger | Evidence and rationale | Required action |
| --- | --- | --- | --- | --- |
| Negative or cancellation-intent reply | Red | Any direct negative reply, cancellation language or unresolved complaint | Direct member evidence; already routed in First 7 Days | Admin Eve records context; Piper owns member follow-up; escalate coaching or commercial issue |
| Ambiguous First 7 Days reply unresolved | Red | Manual-classification task remains open after one business day | Existing workflow creates a persistent task | Resolve intent, correct review routing and assign follow-up |
| Hold return booking failure | Red | T-7 return task incomplete after one business day, or no first return booking by T-2 | Existing Hold Return Journey expects a booking check | Assigned coach contacts member and records confirmed return, extension request or escalation |
| Explicit financial friction | Red | Member says current recurring payment may cause cancellation | Financial reasons are 53.3% of captured completed membership cancellations | Clarify duration and affordability versus value; route only approved hold, relief or plan options |
| Explicit schedule friction | Red | Member says available times prevent continued training | Financial plus schedule account for 73.3% of captured reasons | Identify the exact time constraint and route to the capacity-aware service option |
| No future booking | Amber | No confirmed SGPT booking in the next 7 days, or no valid next PT booking | Required by parent brief; future commitment is operationally actionable, but not yet backtested as causal | Review hold, travel, roster and booking context before member contact |
| Meaningful attendance decline | Amber | Latest 28 days at or below 50% of the prior 28 days, with at least two fewer attended sessions | Conservative operational threshold; attendance alone performed weakly in the backtest | Combine with response, booking or stated-friction evidence before escalation |
| No attendance for 14 days | Watch | No recorded attendance and not on hold, in notice, away or medically modified | Observable absence, but not supported as a primary cancellation predictor | Add to staff review only; do not automate member contact from this signal alone |
| Milestone action overdue | Red | Day 30, 60 or 90 action is more than one business day overdue | Process failure prevents early detection | Queue controller escalates to accountable owner |
| Multiple amber signals | Red | Two or more amber rules occur in the same seven-day period | Combined friction is more decision-useful than one weak signal | Assign a named owner and direct check-in |

Risk rules are operational starting thresholds. Their precision must be measured during the pilot, and weak rules must be stopped.

## Accountable 30/60/90-Day Process

### Provisional Ownership

No recurring responsibility is assigned until Peter confirms it with the staff member.

| Responsibility | Accountable | Support |
| --- | --- | --- |
| Queue completeness and due dates | Admin Eve | Peter |
| Member-care follow-up | Piper | Assigned trainer |
| Coaching, health and modification escalation | Megan | Assigned trainer |
| Commercial outcome verification | Peter | Admin Eve |
| Data-quality exceptions | Peter | Admin Eve |

### Entry and Exit

**Entry:** Member completes the live First 7 Days sequence and remains an active service client.

**Pause:** Active hold. The existing Hold Return Journey becomes the controlling path.

**Exit:**

- completed Day 90 action with no open risk;
- accepted cancellation enters Cancellation OS;
- verified service termination;
- approved transfer to another governed process; or
- duplicate or non-member record confirmed.

Routine lifecycle messaging must stop when a member enters an active cancellation notice.

### Day 30

Purpose: identify early expectation, financial and schedule mismatch.

1. Confirm current tier, assigned trainer, active billing and service access.
2. Review First 7 Days reply disposition.
3. Review last 28 days of attendance and the next seven days of bookings.
4. Ask about progress, enjoyment, schedule fit, affordability and missing support.
5. Record one outcome: healthy, support needed, red flag, hold consideration, service-fit referral or cancellation intent.
6. Assign a due next action for every non-healthy outcome.

### Day 60

Purpose: verify that the member has a repeatable training pattern and understands progress.

1. Compare the latest 28 days with the previous 28 days.
2. Check future bookings and unresolved Day 30 actions.
3. Ask what is making consistency easier or harder.
4. Address financial or schedule friction directly.
5. Use a specific progress measure where valid.
6. Record disposition and next action.

### Day 90

Purpose: consolidate the member's continuation plan.

1. Confirm training cadence, bookings and service fit.
2. Review progress against the member's original goal.
3. Resolve any open support, schedule, financial or coaching issue.
4. Confirm the next 90-day training focus.
5. Close the MVP cohort only when no red risk remains.

### Service Levels

| Item | Service level |
| --- | --- |
| Red risk assigned | Same business day |
| First owner action | Within one business day |
| Amber review | Within two business days |
| Milestone completion | By due date, target at least 90% |
| Unresolved member reply | Escalate after one business day |
| Commercial verification | Friday review |
| Save verification | 28 days after accepted intervention |

## Outcome and Revenue Definitions

### Completed Cancellation

The service is terminated and the member reaches the verified cancelled state. Record actual prior weekly recurring revenue as lost.

### Notice Active

The member has submitted an accepted cancellation and remains within the notice period. Revenue is at risk, not yet counted as completed loss.

### Provisional Save

All of the following are present:

1. material cancellation risk is documented;
2. an intervention occurred;
3. the member accepted a continued-service state; and
4. the cancellation did not immediately complete.

No protected revenue is reported as verified yet.

### Verified Save

All provisional-save requirements are met, plus:

1. the member remains in the accepted service state for at least 28 days;
2. active service is verified;
3. the expected recurring payment is verified; and
4. evidence is linked in the register.

### Hold

A hold is reported separately. It becomes a verified save only after the member returns, remains active for 28 days and recurring billing resumes as expected.

### Downgrade

A downgrade is reported separately. Protected recurring revenue equals the accepted lower weekly amount. The difference from the previous tier is recorded as revenue lost.

### Gross Recurring Revenue

- **Weekly revenue at risk:** actual current weekly recurring amount before intervention.
- **Annualised revenue at risk:** weekly amount multiplied by 52.
- **Protected weekly revenue:** actual accepted weekly recurring amount.
- **Protected annualised revenue:** protected weekly amount multiplied by 52.

Do not use the blended $94.49 value when actual member billing is available.

## Saved-Revenue Register

The companion CSV is intentionally blank. Each risk receives one row and a stable record ID.

Required fields:

| Field group | Required evidence |
| --- | --- |
| Identity | Stable record ID, GHL contact ID, tier and tenure band |
| Risk | Trigger date, risk rule, direct evidence, level, weekly revenue at risk |
| Ownership | Owner, due date, first-action timestamp |
| Intervention | Action, member response and accepted state |
| Outcome | Pending, provisional save, verified save, hold, downgrade, completed cancellation or false positive |
| Verification | GHL state, billing state, Trainerize state and verification date |
| Commercial | Protected weekly and annualised revenue; lost weekly and annualised revenue |

Names should not be copied into summary reports. Operational access to the identified register must be limited to the staff who need it.

## Weekly Operating Cadence

### Monday: Queue

- Roll the 13-week window.
- Add due Day 30, 60 and 90 actions.
- Add new red and amber signals.
- Reconcile active notices and hold returns.
- Assign every item.

### Wednesday: Constraints

- Review overdue risks.
- Resolve booking, coach, health, schedule and service-fit blockers.
- Escalate ambiguous or unsupported actions.

### Friday: Verification

- Verify service and billing states.
- Mature provisional saves that pass 28 days.
- Report completed cancellations, active notices, saves, holds and downgrades separately.
- Review false positives and staff workload.

## Scorecard

| Metric | Definition | Initial baseline or target |
| --- | --- | --- |
| Completed cancellations | Verified completed state in rolling 13 weeks | 18 |
| Cancellation requests | All form-submitted requests | 24 |
| Active notices | Accepted and not yet completed | 5 |
| Stalled requests | Accepted form not advanced correctly | 1 |
| Verified annualised recurring revenue lost | Known actual debit multiplied by 52 | At least $72,124 |
| Unknown-value completed cancellations | Completed with no verified recurring value | 5 |
| 30/60/90 completion | Due actions completed by due date | At least 90% |
| Red flags without owner | Red items with no accountable owner | 0 |
| Verified saves | Passes risk, intervention and 28-day verification standard | 1 additional per month |
| False-positive rate by rule | Closed healthy or data error divided by reviewed signals | Measure during pilot |
| Staff time per verified outcome | Total handling time divided by verified saves | Measure during pilot |

## Weekly Baseline Refresh Contract

Refresh the baseline after each completed Sunday using the latest complete, non-partial reconciliation snapshot.

### Window

- `window_end`: most recent completed Sunday.
- `window_start`: the Monday 12 weeks before `window_end`.
- Include a cancellation when `CS: Date Submitted` falls from `window_start` through `window_end`.
- Keep partial current-week records outside the reported baseline.

### Source Fields

| Measure | Source |
| --- | --- |
| Submitted date | GHL custom field `4fplhpVamf3fnFf40xsA` |
| Cancellation type | GHL custom field `VhxR2hI4B1GfvcZJiD9j` |
| Reason | GHL custom field `RJOCnTuiC7g5cewSPwzW` |
| Tier | GHL membership type field `1SgYibtlIuophn9FYAh8` |
| Tenure start | Membership agreement signed field `1WWilN82DxffsOdgKV2Y` |
| Weekly debit | GHL weekly debit field `d5Ig4OX79xc90WDYbdrN` |
| Pipeline | Cancellation OS `Tl3wKQfNYnAlcgWpORMD` |
| Form received stage | `afcceae1-be81-4402-a15a-470bde16e686` |
| Notice current stage | `4f133549-260c-4bb4-bbb6-3b913b185e1b` |
| Cancelled member stage | `03e01d68-a44c-429f-8770-ce4f72fa33ca` |

### Calculation Rules

1. Use the most recently updated Cancellation OS opportunity for each contact.
2. Count Cancelled Member as completed, Notice Period (Current) as pending, and earlier stages as stalled.
3. Preserve Membership and PT as separate cancellation types.
4. Calculate tenure from agreement signed date to cancellation submitted date.
5. Use bands of less than 3 months, 3 to less than 6 months, 6 to less than 12 months, and 12 months or more.
6. Use the actual weekly debit only when the value is present and maps unambiguously to the cancelled service.
7. Report missing tier, tenure, reason or revenue as Unknown.
8. Calculate annualised recurring revenue as verified weekly recurring revenue multiplied by 52.
9. Do not count active notices as completed revenue lost.
10. Reconcile prior active notices every week so each matures into a completed, saved, held, downgraded or data-error outcome.

### Quality Checks

- Requests equal completed plus active notices plus stalled and other exceptions.
- Every completed cancellation appears once.
- Membership reason coverage and PT reason coverage are shown separately.
- Revenue totals reconcile to member-level verified debits.
- Unknown counts never silently fall between reporting periods.
- A failed or partial source extraction cannot replace the last complete baseline.

## Immediate Exceptions

1. Reconcile the five completed cancellations with unknown tier, tenure and recurring value.
2. Investigate the one record stalled at Cancellation Form Received.
3. Mature the five active notices into a verified outcome when their notice periods complete.
4. Add structured PT cancellation reasons in a later approved change.
5. Establish a historical active-member denominator before reporting churn rate.
6. Create an explicit save outcome before claiming a historical save baseline.

## Approval Gates

Peter's explicit approval is required before:

- assigning recurring responsibilities to staff;
- contacting members through this pilot;
- creating or editing live GHL workflows, tasks, fields or opportunities;
- changing billing, holds, cancellations or member state;
- updating the manual, SOP, trainer course, HTML or quiz; or
- writing to external systems.

## Proposed Parent and Roadmap Updates

These changes are proposed but were not made:

1. Add the 13-week baseline: 24 requests, 18 completed, 5 active notices and 1 stalled request.
2. Add the verified recurring-revenue-loss floor of $1,387 per week and $72,124 annualised, with five completed records still unclassified.
3. State that the current count baseline is approximately 6.0 completed cancellations per month.
4. State that one additional verified save per month is roughly a 16.7% improvement against the current count.
5. Add the evidence concentration: 61.5% of known-tenure cancellations occurred before three months; 73.3% of captured membership reasons were financial or schedule-related.
6. Add the measurement limitation that no churn rate can be reported without a historical active-member denominator.
7. Change Retention Plus One from Scoped to In Progress only after Peter approves operating owners and the pilot.
