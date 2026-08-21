# Strength Assessment Attendance Control

**Owner:** Peter Brown  
**Operational exception owner:** Admin Eve  
**Definition:** `sa-attendance-v2` and `sa-attendance-followup-v1`  
**Mode:** Governed collection and protected follow-up preview  
**Effective design date:** 29 July 2026

## Decision

Every Strength Assessment is identified by its GoHighLevel appointment event ID. GHL owns the scheduled event and terminal appointment status; the existing `SA: Coach Consultation Feedback` form supplies evidence that the assessment was delivered and who delivered it.

The Evolved Operating Data Hub reconciles those records, retains the evidence and decision history, and calculates the governed show rate. Google Sheets is a staff-facing mirror and KPI presentation surface, not the attendance database.

## Source authority

| Information | Authority | Permitted use |
|---|---|---|
| Appointment identity, time, calendar, assigned user and terminal status | GHL appointment event | Canonical appointment record |
| Delivered assessment | `SA: Coach Consultation Feedback` | Strong delivery evidence |
| Assigned consultant | GHL appointment assigned user | Trainer attribution and follow-up authority |
| Conversion | Membership Agreement and PT Agreement workflows | Sale and fulfilment evidence |
| Follow-up routing | Opportunity stage and tags | Supporting routing evidence only |
| Physical assessment results | Trainerize | Strength-result evidence only |
| Legacy attendance | Appointments column K | Historical comparison only |
| Reporting and reconciliation | Operating Data Hub | Governed attendance metric and exception state |

Contact names, email addresses, Sheet row numbers, opportunity stages and tags must never replace the appointment event ID.

## Status and metric contract

Normalised appointment statuses are `confirmed`, `showed`, `no_show`, `cancelled`, `invalid` and `unknown`.

Show rate is:

`Showed / (Showed + No show)`

Cancelled, Invalid and superseded reschedules are excluded and reported separately. An elapsed Confirmed appointment remains unresolved; it is never silently treated as a No show.

Weekly show rate is provisional whenever an elapsed appointment remains unresolved at period close. The report must display the unresolved count and definition version.

## Reconciliation rules

1. A feedback submission searches only the same contact's approved Strength Assessment events.
2. The event must have ended before the submission and fall within seven days.
3. Same-Brisbane-day events are preferred when a contact has repeat appointments inside the seven-day matching window.
4. Exactly one eligible event must match after that same-day preference.
5. Confirmed plus one matched feedback submission produces a `confirmed -> showed` proposal.
6. Showed plus matched feedback is `terminal_consistent`.
7. No show plus feedback is a high-priority `terminal_conflict`.
8. Zero or multiple matches create an Admin Eve exception.
9. Missing feedback never creates a No show.
10. Sale outcome, agreement completion, tags, opportunity stage and Trainerize can expose conflicts but cannot independently rewrite attendance.
11. Repeated polls and webhook deliveries are idempotent.

## Post-session operating standard

| Outcome | Consultant action |
|---|---|
| Assessment delivered | Submit the existing Consultant Feedback form and ensure the exact appointment is marked Showed |
| Prospect did not attend | Mark the exact appointment No show immediately |
| Prospect cancelled | Retain Cancelled and use the existing cancellation recovery path |
| Duplicate, test or bad booking | Use Invalid only when the booking is genuinely non-client activity |
| Cover coach delivered | Tell Admin so the exceptional attribution can be corrected manually |

The existing `2.2 SA: No Show Rebook`, `2.3 SA: Cancelled Rebook`, Sale, No Sale, agreement, onboarding and Trainerize workflows retain their current ownership.

## Exception ownership

An appointment still Confirmed 60 minutes after its end remains unresolved. The existing `2.4 Send Consultation Feedback Survey` workflow supplies the immediate coach prompt. The hub adopts that open task where its coach and due day match, adds the appointment ID and exact three-outcome instruction, and does not create a competing reminder.

The appointment's assigned coach owns the first closure. If no coach is assigned, the item routes to Admin Eve without guessing. If the outcome is still missing at 10:00 am on the next business day, one appointment-specific Admin Eve escalation is due by 5:00 pm. Hub-created or adopted tasks close automatically when matched feedback or a terminal appointment status resolves the event.

Before proposing a task, the hub performs a governed Trainerize pre-check when `TRAINERIZE_ATTENDANCE_PRECHECK_ENABLED=true`. It requires one exact GHL-to-Trainerize identity, the same Brisbane appointment date and exactly one tracked `Women's Standard Strength Assessment`. If all three match, the task executor re-reads GHL, permits only `Confirmed -> Showed`, verifies the saved status and closes any governed task. Missing credentials, source failure, a missing or duplicate identity, no matching session, multiple matching sessions, a changed GHL record or a failed write all retain the normal staff task.

Historical generic GHL tasks are not bulk-closed. The controller governs new and adopted tasks carrying an exact appointment marker.

Each task or protected exception record must include the event ID, scheduled time, appointment owner, delivered-by evidence when present and one explicit corrective action. Identified details stay behind the authenticated hub endpoint or within the governed staff Sheet.

## Data handling

- GHL timestamps are retained in UTC; Brisbane time is used for service periods and operational display.
- Appointment observations, feedback evidence and reconciliation decisions are append-only.
- Aggregate CEO surfaces contain no prospect names.
- Historical matching detail is stored under `data/private/integration-reporting/`.
- Legacy column K values are preserved but cannot promote a historical Showed record by themselves.

## Write gates

`SA_ATTENDANCE_GHL_WRITE_ENABLED`, `SA_ATTENDANCE_TASK_WRITE_ENABLED`, `TRAINERIZE_ATTENDANCE_PRECHECK_ENABLED` and `SA_ATTENDANCE_SHEETS_WRITE_ENABLED` default to `false`.

Task writes are a separate permission from appointment-status writes. The protected preview can therefore be deployed and reviewed without creating, editing or completing any GHL task.

The protected controller was deployed on 30 July 2026 as Railway deployment `b250136b-b5ec-404d-bb44-1e328848915f`. Its first production preview found eight recent elapsed Confirmed appointments and proposed eight coach prompts plus eight overdue Admin Eve escalations. The task-write gate remained false, so the preview made no live task changes.

GHL write activation requires:

- two complete Monday-to-Sunday shadow cycles;
- zero incorrect automatic Showed proposals;
- deterministic exact-event updates;
- one controlled test contact;
- one reviewed live feedback event;
- a 20-case historical guard replay, controlled live branch tests and two accepted Railway refresh observations; future genuine closures remain ongoing monitoring rather than a cutover blocker.

The only permitted automated transition is `confirmed -> showed`. No reverse transition and no change from No show, Cancelled or Invalid is permitted.

Deployment `bc0d56ed-24a0-4266-9216-0eea195fcabb` activated the automatic pre-check on 30 July 2026. Its first production preview checked four unresolved appointments, verified two and retained two for staff. The live cycle changed Mariya Boycheva's 27 July and Karissa Mclaren's 24 July appointments from Confirmed to Showed using one exact tracked Trainerize assessment each. Both writes were read back successfully, no fallback task was required and the next attendance refresh increased explicit Showed assessments from four to six.

Deployment `ed90e9de-0e4a-4ef9-9ad7-c535e80e7094` expanded historical attendance identity search to active and deactivated Trainerize profiles. The matcher deduplicates by Trainerize user ID and prefers the active copy if both views return the same account. The first corrected run recovered Indie Cevallos's exact deactivated account and tracked 29 July assessment, changed GHL from Confirmed to Showed, verified the write and closed both governed tasks. Bita Gusti's 30 July appointment is confirmed Cancelled in GHL. She requires no Trainerize attendance inference and no Nora missing-attendance follow-up; the event remains part of cancellation reporting and is excluded from showed and sales-conversion denominators.

The 30 July historical corrections exposed a separate workflow defect: the published `2. Strength Assessment` workflow treated appointment-status changes as fresh bookings. Seven contacts were re-enrolled. On 31 July the live workflow was changed to a sole `new` Appointment Status trigger for the exact active Strength Assessment calendar, and the first branch used the appointment's `Rescheduled` value. That change stopped Showed corrections from entering, but later evidence proved it was not a valid booking trigger: the public booking widget creates appointments as `confirmed`, so three subsequent bookings never entered the workflow.

On 5 August the owner approved restoring the event boundary rather than filtering on a transient status. The published workflow now has one `Customer Booked Appointment` trigger for contact-only enrolment on the exact active Strength & Longevity Assessment calendar. The Appointment Status trigger was deleted. A server reload verified Saved and Published state, one correct booking trigger, zero old status triggers and the unchanged reschedule split, 30DNNC exit and existing-COLD-opportunity guard. Historical Showed, No show and Cancelled changes cannot match the booking event, while the internal `Rescheduled` branch continues to separate genuine new/rebooked assessments from active reschedules.

The repair then passed a controlled production-widget acceptance on 5 August. A clean owner-controlled booking was created as Confirmed, enrolled immediately from the exact booking trigger, completed the intentional one-minute wait and followed the fresh/direct path. The expected tag, single WARM Assessment Booked opportunity, internal alert, client confirmation email and SMS, appointment-sheet row and SA Nurture entry were observed; no COLD opportunity was created. Cleanup stopped both enrolments before later reminders and deleted the exact appointment, opportunity, contact and sheet row. Independent read-back returned no residual contact match, event, opportunity or Appointments-sheet row, while the saved workflow retained the repaired trigger and safeguards.

The seven 30 July incident enrolments remain finished; 18 exact incident-created open tasks and one duplicate opportunity were deleted, and no ambiguous historical tags or opportunities were changed. The affected same-day missed booking was reconciled without replaying client communication: the existing opportunity moved to WARM Assessment Booked, the booked tag was restored, the 30DNNC delivery paths were stopped and one consultant prep task was created. The production attendance-writer gate remains disabled.

The dedicated No Show and Cancelled rebooking workflows remain a separate side-effect boundary. On 31 July a direct historical correction of Vaishnavi Vakacharla's superseded 23 July appointment to Cancelled correctly changed the event but also enrolled the live cancellation path. It added `strength assessment cancelled` and created a new WARM cancellation-stage opportunity even though Vaishnavi had subsequently completed her 28 July assessment and become a member. The enrolment, exact incident tag and exact incident-created opportunity were removed before any client message or staff task was sent. Her genuine `member`, `personal training` and `strength assessment showed` state remained intact.

Historical No show or Cancelled corrections must therefore not be applied as an ordinary GHL status write. Before any such write, the operator must either prove that the dedicated rebooking workflow has an effective historical/member exclusion or temporarily contain the exact contact from that workflow. After the write, the operator must verify tags, WARM opportunities, tasks and client messages before refreshing the hub. When that containment cannot be proven, retain the source appointment unchanged and record the governed terminal outcome through the hub's audited historical correction path instead. This restriction does not change the permitted automatic `confirmed -> showed` transition, which remains evidence-gated and independently monitored.

The first 31 July guard was not accepted. On 1 August controlled temporary enrolments proved that its completed-assessment branch stopped correctly, but its original first branch failed with both `member` and Customer conditions. Each temporary enrolment was contained during its wait step before a client-facing rebooking message, the test-created status tags were removed, and both temporary contacts were ultimately deleted.

Both published workflows were then rebuilt cleanly with `strength assessment showed` as the first stop branch, GHL contact type `Customer` as the second stop branch and `Eligible for rebooking` as the only route into the pre-existing opportunity, tag, spreadsheet, message and task actions. The final completed-assessment and Customer/member contacts show `No Action / Finished` in both workflow histories. A read-only replay classified all 20 latest terminal events: 19 Cancelled, one No show, three existing Customers stopped and 17 Leads eligible. Two normal Railway attendance refresh observations at 08:10 and 20:10 UTC completed; the current accepted run is `20260731T201000Z-8ee01dc7`.

GHL does not provide a rolling appointment-age comparison in this trigger or If/Else action, so no false “within 72 hours” rule was added. Historical corrections still require the governed containment and post-write audit above; the live guard is a second line of defence, not permission for unrestricted historical writes. Genuine closures remain ongoing monitoring rather than a Reporting V2 cutover blocker.

On 3 August the governed Trainerize pre-check was applied to 18 stale elapsed-Confirmed Strength Assessment appointments during pipeline cleanup. It found eight exact-date tracked `Women's Standard Strength Assessment` sessions. Seven appointments on the active round-robin calendar were changed to Showed and verified; all eight associated WARM opportunities were moved from Assessment Booked to FUM. The eighth appointment is attached to the inactive legacy event calendar and GHL returned `Calendar is inactive`, so its appointment status remains Confirmed while its exact Trainerize evidence and corrected FUM opportunity preserve the operational outcome.

On 4 August a delivered first assessment exposed a separate prompt-enrolment gap. A cancellation followed by an in-place reschedule retained the original appointment identity, so the contact's initial `2. Strength Assessment` execution had already ended and no new execution reached the post-appointment `2.4 Send Consultation Feedback Survey` handoff. The appointment was later marked completed and the contact carried `strength assessment showed`, but the assigned consultant had not received the internal feedback prompt. The contact was enrolled directly into published workflow `2.4`. That workflow now has a fallback `Contact Tag` trigger filtered to `Tag added includes "strength assessment showed"`, while `Allow re-entry` is disabled. This preserves the normal parent-workflow handoff, catches future first-assessment cases that reach Showed without it and prevents the fallback from repeating the consultant prompt when the normal enrolment already occurred.

The other ten cases received a second full-record review on 4 August. Four contained explicit cancellation or postponement messages, five contained no defensible delivery evidence, and one contained strong arrival evidence plus same-day Trainerize activity but no exact tracked assessment. The related opportunities were reconciled without rewriting any of these ten appointment statuses: four explicit cancellations became Lost in the cancellation/rebook stage, five unsupported historical bookings became Lost in their existing stage, and the one attendance-uncertain case moved to FUM. This closes the stale Assessment Booked queue while preserving source uncertainty. It does not convert weak evidence into a Showed, No show or Cancelled attendance fact.

The subsequent WARM-stage review found two exact Showed appointments still represented as cancellation-stage opportunities. Their opportunity stages and outcome tags were aligned to Show without changing appointment history. One still lacks Coach Consultation Feedback, so Admin Eve owns a single exception task to recover the internal outcome from the delivering coach or explicitly record that the historical result cannot be recovered. The prospect must not be contacted merely to reconstruct internal data. Two newer Show records with submitted No Sale data remain inside the published No Sale follow-up and were not interrupted.

Sheet publication requires exact spreadsheet ID, tab ID and header validation. A changed row must still match the reader's full-row precondition immediately before update.

## Rollback

1. Set both attendance write gates to `false`.
2. Keep read-only GHL collection and feedback evidence ingestion active.
3. Preserve the last complete accepted snapshot and all audit history.
4. Mark show rate unavailable or provisional.
5. Never fall back silently to Appointments column K.

## Current baseline

The 29 July 2026 freeze found:

- active calendar: `HSVEzfJH4nice96IxHem`;
- duplicate-named zero-event calendar: `z3cCnLnqwEO7jDrGA0HH`, excluded from the approved runtime list;
- active roster: Megan Brown, Piper Mae and Nora Silva;
- 82 appointment events in the preceding 90 days;
- 79 elapsed events: 60 Confirmed and 19 Cancelled;
- zero GHL Showed or No show statuses;
- zero missing event IDs;
- Appointments column K remains a strict manual Y/N dropdown;
- KPI rows 57 to 63 still depend on column K.

The governed `SA Attendance` tab now exists as tab ID `1446062006` with the exact 15-column contract, header protection and unresolved/conflict views. It intentionally contains no published event rows while `SA_ATTENDANCE_SHEETS_WRITE_ENABLED=false`.

The absence of terminal attendance statuses means GHL cannot become the reporting authority merely by changing the formula. Staff status closure and feedback reconciliation must be proven first.

## Operational endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/ingest/sa-feedback` | Authenticated, replay-safe feedback evidence ingestion |
| `GET /api/v1/sa-attendance/summary` | Aggregate attendance, freshness and exception counts |
| `GET /api/v1/sa-attendance/exceptions` | Protected identified reconciliation state |
| `POST /api/v1/jobs/sa-attendance-refresh` | Start a read-only GHL collection and reconciliation run |
| `GET /api/v1/sa-attendance/followup-preview` | Protected appointment-level coach and Admin task preview |
| `POST /api/v1/jobs/sa-attendance-followups` | Run the controller only when its separate task-write gate is enabled |

## Feedback collection and coach attribution

Railway reads the existing Consultant Feedback form directly every 12 hours. It stores only the submission ID, contact ID, submitted time, sales outcome and coach attribution needed for reconciliation; strength answers, notes and other form content are not copied into the attendance ledger.

The owner decision on 30 July 2026 makes the trainer assigned to the GHL calendar appointment authoritative for consultant attribution and follow-up routing. The feedback form does not ask the consultant to repeat their name. Cover delivery is an exception for Admin to correct manually. The unused proposed `SA: Assessment Delivered By` field was deleted from GHL.

An owner-confirmed observation is also permitted as governed manual attendance evidence when the owner directly observed delivery and identifies the exact appointment. On 31 July Peter confirmed that Jess Michels attended her 3 July Strength Assessment from camera evidence. Her GHL appointment is now Showed and therefore enters both the attendance/show-rate numerator and denominator. Peter accepted the absent Strength Assessment value and consultant feedback as a permanent historical recording gap because a submission is no longer expected. It requires no further chase, is not evidence of non-attendance and does not reverse or qualify the attendance outcome.

Railway deployment `84d6bef7-c4a5-4795-bdd9-ac96d6c94f69` activated the separate staff-task writer after a controlled assignment and auto-closure test. The first governed run produced all 16 expected open task stages for eight unresolved appointments: eight assigned-coach prompts and eight next-business-day Admin Eve escalations. An immediate repeat run retained exactly 16 stages with zero missing and zero duplicate markers.

## Historical recovery

Run `scripts/backfill_sa_attendance.py` in read-only mode. It classifies legacy records as exact, corroborated, ambiguous or unmatched and writes identified detail to the private integration-reporting area.

No historical KPI is restated without separate owner approval and a dated restatement note.
