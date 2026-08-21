# Plan: Strength Assessment Attendance Source of Truth

**Created:** 2026-07-29
**Status:** Pending validation
**Request:** Replace the unreliable manual Strength Assessment attendance field with a governed cross-system record that uses the existing Consultant Feedback form and accounts for GHL, Google Sheets, reporting, sales, Trainerize, staff operations and historical data.

---

## Overview

### What This Plan Accomplishes

This plan establishes one authoritative attendance record for every Strength Assessment appointment. GHL retains the appointment event and terminal status, the existing `SA: Coach Consultation Feedback` form becomes the strongest evidence that an assessment was delivered, and the Evolved Operating Data Hub reconciles the two before publishing show-rate metrics to Google Sheets, the CEO dashboard and Discord.

The design removes manual column K from the KPI calculation, preserves the existing feedback, sales and onboarding workflows, and introduces an owned exception path for elapsed appointments that remain unresolved or contain conflicting evidence.

### Why This Matters

Show rate is a core acquisition metric. The current calculation can understate or overstate sales performance because it relies on a manually toggled Y/N field with no appointment ID, timestamp, recorder or treatment of cancellations and reschedules.

A reliable attendance record improves marketing decisions, consultant performance review, no-show recovery and capacity planning. It also aligns the metric with the reporting-control principle that Google Sheets is a presentation surface, not the integration database.

---

## Current State

### Relevant Existing Structure

- `Brown & Casserly Pty Ltd 2026` contains the `Appointments` tab.
  - Column H contains the scheduled appointment time.
  - Column K is a manual `Show?` dropdown with `Y` and `N`.
  - Column L is the separately maintained `Convert?` outcome.
- `scripts/insert_formulas.py` and `scripts/patch_booking_rows.py` count only Appointments column K = `Y` as attended.
- `scripts/sheets_client.py` exposes column K as `showed` to the Discord daily brief.
- `scripts/update_metrics.py` reads the resulting KPI rows and writes `context/current-data.md` and `context/current-data.json`.
- `operating_data_hub/kpi_adapter.py` currently imports booking and show-rate metrics from the Google KPI tab.
- `operating_data_hub/` already supplies authenticated source snapshots, source lineage, metric snapshots, exceptions, the CEO dashboard and the CEO report.
- `pt_booking_shadow/ghl_client.py` already demonstrates the supported read-only GHL calendar-event extraction pattern, including event ID, contact ID, calendar ID, timestamps, assigned user and `appointmentStatus`.
- GHL's appointment record supports `Confirmed`, `Showed`, `No show`, `Cancelled` and `Invalid`.
- `2. Strength Assessment` creates an Appointments Sheet row only for the new-client path. Returning clients and some rebooks do not create equivalent rows.
- `2.2 SA: No Show Rebook` and `2.3 SA: Cancelled Rebook` depend on the corresponding GHL appointment status.
- `2.4 Send Consultation Feedback Survey` sends the existing feedback request and creates follow-up tasks.
- `2.4 Consultation Feedback Complete` is triggered by the existing `SA: Coach Consultation Feedback` form and routes the recorded Sale or No Sale outcome.
- `2.5. No Sale - Follow Up` updates the Appointments row and manages the post-assessment follow-up sequence.
- Membership and PT Agreement workflows remain the authoritative conversion and fulfilment events.
- Trainerize remains the in-session source of truth for physical Strength Assessment results.
- The attendance process is referenced through:
  - `reference/evolved-manual/02-assessment-system.md`
  - `reference/evolved-manual/scripts/assessments/strength-assessment-script.md`
  - `reference/sops/strength-assessment.md`
  - `outputs/trainer-portal/10-strength-assessment.md`
  - `outputs/trainer-portal/html/10-strength-assessment.html`
  - the live GoHighLevel Course 10.

### Gaps or Problems Being Addressed

- Column K is manual and has no evidence trail.
- Three elapsed appointments are currently blank.
- Two July rows show conversion while attendance is blank.
- All 107 elapsed appointments through February are marked `Y`, creating an implausible historical 100% show rate.
- A recent appointment marked `Y` in Google Sheets remained `Confirmed` in GHL.
- The KPI denominator counts scheduled rows without distinguishing No show, Cancelled, Invalid, rescheduled or unresolved appointments.
- Returning clients and rebooks are not represented consistently in the Appointments tab.
- Sheet-row lookup by name or email is not a stable appointment identity.
- GHL tags and opportunity stages are contact-level state and cannot identify a particular appointment.
- The Consultant Feedback form proves that a coach completed post-assessment work, but it is not currently reconciled to the GHL appointment event.
- Cover delivery can differ from appointment assignment; the owner accepts this as a manual Admin correction rather than adding a compulsory form question.
- Existing reports silently publish a show rate even when elapsed appointments have no terminal outcome.
- Historical values cannot safely be accepted as fact without a confidence-based backfill.

---

## Proposed Changes

### Summary of Changes

- Define a versioned Strength Assessment attendance contract in the Operating Data Hub.
- Use the GHL appointment event ID as the immutable appointment identity.
- Treat `Showed` and `No show` as the only show-rate denominator statuses.
- Exclude `Cancelled` and `Invalid` from the show-rate denominator while reporting them separately.
- Treat elapsed `Confirmed` appointments as unresolved exceptions after a defined grace period.
- Reuse `SA: Coach Consultation Feedback`; do not create another feedback form.
- Use the trainer assigned to the GHL calendar appointment for consultant attribution and task routing; treat cover delivery as a manual Admin exception.
- Send a protected feedback-submission event from `2.4 Consultation Feedback Complete` to the hub.
- Match feedback evidence to exactly one recent Strength Assessment appointment by contact ID and appointment time window.
- Automatically propose, and after shadow validation apply, `Showed` to the matched appointment when the feedback form proves delivery and the appointment is still `Confirmed`.
- Preserve existing Sale, No Sale, consultant-performance, No Sale follow-up and onboarding branches.
- Use Membership Agreement, PT Agreement, `strength assessment showed`, WARM pipeline stage and Trainerize assessment evidence only as supporting or conflict evidence.
- Create an append-only attendance ledger and exception history in the hub.
- Create a staff-facing `SA Attendance` Sheet tab as a governed mirror, not a second source of truth.
- Retire Appointments column K from KPI calculations and relabel it as a legacy field after cutover.
- Publish governed attendance totals and show rate to the existing KPI rows.
- Add unresolved, cancelled, invalid and data-quality measures to the CEO system-health view.
- Update the Discord daily brief to show canonical appointment status and overdue outcome exceptions.
- Build a read-only historical backfill with exact, corroborated, ambiguous and unmatched confidence classes.
- Run two shadow parity cycles before enabling any GHL or Google Sheets write.
- Cascade the operating instruction through the manual, SOP, trainer course, HTML, quiz and live GHL course.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `operating_data_hub/sa_attendance.py` | Extract, normalise and reconcile GHL Strength Assessment appointments with feedback and supporting evidence. |
| `operating_data_hub/sa_attendance_sheet.py` | Fail-closed writer for the staff-facing attendance mirror and approved KPI cells. |
| `operating_data_hub/tests/test_sa_attendance.py` | Unit and reconciliation tests for status mapping, feedback matching, duplicates, reschedules, conflicts and weekly metrics. |
| `operating_data_hub/tests/test_sa_attendance_sheet.py` | Layout validation, idempotency and write-boundary tests for Google Sheets publication. |
| `scripts/backfill_sa_attendance.py` | Read-only historical matching tool that produces confidence-labelled evidence without modifying GHL or Google Sheets. |
| `scripts/test_backfill_sa_attendance.py` | Fixtures for exact, corroborated, ambiguous, duplicate and unmatched historical cases. |
| `outputs/systems/strength-assessment-attendance-control.md` | Architecture decision record, source authority matrix, metric definition, operating runbook and exception ownership. |
| `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md` | Dated parity results, discrepancies, owner decisions and write-activation gates. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `operating_data_hub/contracts.py` | Add the versioned `strength_assessment_attendance` source contract and strict status/evidence validation. |
| `operating_data_hub/store.py` | Add append-only appointment, attendance-evidence and reconciliation-state tables keyed by GHL event ID. |
| `operating_data_hub/service.py` | Schedule attendance refreshes, set freshness limits, reconcile exceptions and prefer governed attendance metrics over Sheet-derived show rate. |
| `operating_data_hub/app.py` | Add protected feedback ingestion, identified attendance-exception and aggregate attendance endpoints; extend CEO report output. |
| `operating_data_hub/config.py` | Add calendar ID, matching window, grace period, shadow/write gates and Sheet-publication settings. |
| `operating_data_hub/templates/dashboard.html` | Show governed booked, Showed, No show, Cancelled and unresolved measures; keep names on protected operational surfaces only. |
| `operating_data_hub/tests/test_app.py` | Test endpoint authentication, privacy boundaries, source freshness and CEO report compatibility. |
| `operating_data_hub/tests/test_contracts_and_store.py` | Test versioned ingestion, event idempotency, evidence history and source lineage. |
| `operating_data_hub/kpi_adapter.py` | Retain Google KPI compatibility but stop treating Sheet show rate as authoritative after the attendance source is accepted. |
| `reporting_control/report_registry.json` | Register the metric definition, source requirements, freshness and downstream consumers. |
| `reporting_control/executive_brief.py` | Include governed attendance and unresolved exceptions in the executive output. |
| `scripts/insert_formulas.py` | Retire K-based attendance formulas and preserve only compatibility formulas during migration. |
| `scripts/patch_booking_rows.py` | Remove K-based source attendance ownership after hub publication is enabled. |
| `scripts/sheets_client.py` | Replace manual K-based `showed` reads with the canonical attendance mirror or hub endpoint. |
| `scripts/update_metrics.py` | Add governed attendance counts, unresolved count, definition version, freshness and limitations. |
| `scripts/test_formulas.py` | Replace manual-Y attendance fixtures with canonical status publication fixtures. |
| `scripts/SETUP.md` | Document required GHL, hub and Sheet settings, shadow mode and cutover procedure. |
| `discord_bot/reports.py` | Show appointment status and overdue-outcome exceptions from the governed attendance source. |
| `outputs/systems/reporting-control-plane.md` | Add Strength Assessment appointment and attendance authority, ingestion, freshness, privacy and publication rules. |
| `outputs/systems/sales-conversion.md` | Document feedback-to-attendance reconciliation while preserving current Sale, No Sale and agreement ownership. |
| `outputs/systems/lead-generation-nurture.md` | Clarify that contact tags are routing signals, not appointment-level attendance evidence. |
| `outputs/systems/ghl-backend-register.md` | Record the final GHL workflow, form, field, webhook and status dependencies. |
| `outputs/systems/ghl-team-task-trigger-register.md` | Add the elapsed-confirmed exception and its Admin Eve ownership/deduplication rule. |
| `reference/evolved-manual/02-assessment-system.md` | Define the post-session completion and attendance-record sequence. |
| `reference/evolved-manual/scripts/assessments/strength-assessment-script.md` | Add exact trainer actions after Showed and No show outcomes. |
| `reference/sops/strength-assessment.md` | Increment revision history and define status closure, feedback submission, cover attribution and exception handling. |
| `outputs/trainer-portal/10-strength-assessment.md` | Cascade the revised post-session operating standard and audit the full quiz. |
| `outputs/trainer-portal/html/10-strength-assessment.html` | Regenerate from the updated Markdown source. |
| `context/roadmap.md` | Move the attendance source-of-truth item through In Progress, Pending and Live with measured validation results. |
| `CLAUDE.md` | Add the new hub attendance component, backfill script and operating command only if implementation introduces a reusable workflow future sessions need to know. |

### Files to Delete (if any)

No files are deleted initially.

After one compatibility window and two successful governed reporting cycles:

- Retire the K-based formula definitions from `scripts/insert_formulas.py` and `scripts/patch_booking_rows.py`.
- Keep historical column K values in the Sheet as labelled legacy evidence; do not delete them.
- Remove any temporary compatibility reader only after Discord, KPI, CEO report and current-data outputs all use the governed source.

---

## Design Decisions

### Key Decisions Made

1. **GHL appointment ID is the canonical event identity**: Contact names, emails, tags and Sheet row numbers can repeat or change. The event ID survives rescheduling and supports idempotent reconciliation.
2. **The existing Consultant Feedback form is reused**: A completed coach feedback submission is strong evidence that the assessment occurred. Creating another attendance form would increase duplicate work and reduce compliance.
3. **The feedback form does not independently become the database**: The form supplies delivery evidence. The GHL appointment remains the appointment record, and the hub stores the reconciliation and audit history.
4. **Calendar assignment is the consultant authority**: The trainer assigned to the immutable GHL appointment is used for follow-up and trainer attribution. Cover delivery is exceptional and corrected manually by Admin, avoiding a duplicate question on every feedback submission.
5. **Show rate uses terminal attendance outcomes only**: `Showed / (Showed + No show)`. Cancelled, Invalid and unresolved Confirmed appointments are reported separately.
6. **Elapsed Confirmed fails closed**: After appointment end plus a 60-minute grace period, Confirmed becomes an unresolved exception. It is not silently counted as a no-show.
7. **Feedback can close Confirmed as Showed only after deterministic matching**: Automatic closure requires one contact, one relevant Strength Assessment calendar event and one unambiguous time window. Ambiguous matches become Admin exceptions.
8. **No-show remains an explicit human or calendar action**: The absence of feedback is not proof of a no-show. The consultant must mark No show, which keeps `2.2 SA: No Show Rebook` authoritative.
9. **Cancelled and Invalid remain distinct**: Neither is converted to `N`, and neither enters the show-rate denominator.
10. **Agreement and sale evidence are corroborating only**: A completed agreement proves conversion, not necessarily the exact attendance event. It can expose conflicts but cannot silently rewrite attendance.
11. **Trainerize remains assessment-result authority**: A recorded assessment workout can strengthen a Showed case but is not required for every prospect and does not replace the feedback form.
12. **The hub is the reconciliation and metric authority**: Google Sheets remains the staff-facing mirror and approved KPI presentation.
13. **Writes are staged behind separate gates**: `SA_ATTENDANCE_GHL_WRITE_ENABLED` and `SA_ATTENDANCE_SHEETS_WRITE_ENABLED` default to false. Read-only collection and shadow comparison go live first.
14. **Historical data is confidence-labelled**: Exact and strongly corroborated records can be accepted after review. Ambiguous history stays unresolved rather than being converted into false certainty.
15. **No member communication is added**: This implementation changes staff operations, reconciliation and reporting only. Existing confirmation, no-show, cancellation and No Sale communications remain the governing contact journeys.

### Alternatives Considered

- **Keep column K and improve the dropdown**: Rejected because validation does not add event identity, provenance, timestamps, cancellation handling or rebook safety.
- **Make the feedback form the only source of attendance**: Rejected because a coach can omit the form, submit late or select the wrong contact, and the form does not represent cancellations or invalid bookings.
- **Use GHL status with no reconciliation**: Rejected because a recent Sheet-Y assessment still remained Confirmed in GHL and unresolved statuses would remain invisible.
- **Infer attendance from a sale or agreement**: Rejected because prospects can decide later, sign remotely or have an agreement corrected after the appointment.
- **Infer no-show from missing feedback**: Rejected because missing feedback can be a staff-process failure rather than client non-attendance.
- **Use opportunity stage or `strength assessment showed` tag as the event record**: Rejected because both are contact-level and can outlive or span multiple appointments.
- **Write directly from GHL workflows to Google Sheets**: Rejected because this repeats the current row-lookup weakness and bypasses hub lineage, reconciliation and exception handling.
- **Create a standalone attendance service outside the hub**: Rejected because the reporting control plane already owns appointment, attendance, metric definition, exceptions and Railway scheduling.
- **Rewrite all historical KPI columns immediately**: Rejected because early column K data is not sufficiently trustworthy and would create unsupported restatements.

### Open Questions (if any)

There are no blocking design questions before implementation. The following are controlled implementation gates:

1. Verify whether the live GHL workflow builder can update the triggering contact's matching appointment status. If it cannot do so deterministically, use the authenticated hub writer after event matching.
2. Verify whether GHL's webhook action can send the hub secret as a header. If not, use a dedicated signed ingestion token with rotation and replay protection.
3. Confirm the exact Strength Assessment calendar IDs at implementation time and store the approved list in configuration rather than matching by title at runtime.
4. Confirm the canonical feedback field option for a rare non-roster cover coach. Recommended default: `Approved cover / other`, which always creates an Admin attribution exception.
5. Historical KPI restatement requires a separate owner approval after the confidence-labelled backfill report. It is not part of automatic cutover.

---

## Step-by-Step Tasks

Execute these tasks in order during implementation.

### Step 1: Freeze Baselines and Verify Live Capabilities

Capture a dated, read-only baseline before changing any live workflow, form, Sheet or code.

**Actions:**

- Export or record:
  - all current Strength Assessment calendar IDs and assigned users;
  - the last 90 days of GHL appointment IDs, statuses and timestamps;
  - the current `Appointments` A:N values and validation rules;
  - KPI formulas for rows 52 to 63 across all populated weekly columns;
  - current output from `context/current-data.json`;
  - the current CEO report acquisition metrics;
  - the current Discord appointment presentation.
- Record counts for Showed, No show, Cancelled, Invalid, Confirmed-after-end and missing event IDs.
- Inspect live GHL workflow actions to determine whether an appointment status can be updated safely from `2.4 Consultation Feedback Complete`.
- Verify the GHL calendar update API endpoint, required scopes, idempotent request shape and event update timestamp if the native action is inadequate.
- Verify the feedback workflow webhook's supported authentication headers and retry behaviour.
- Store screenshots or structured notes in the shadow review log without copying member-identifying data into public outputs.
- Mark the roadmap item In Progress.

**Files affected:**

- `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md`
- `context/roadmap.md`

---

### Step 2: Write the Architecture Decision and Data Contract

Document the source hierarchy and exact metric semantics before code or live changes.

**Actions:**

- Define the source authority matrix:
  - GHL appointment event: scheduled event and terminal status;
  - Consultant Feedback: delivered-assessment evidence and coach attribution;
  - Agreement workflows: conversion evidence;
  - opportunity/tag state: routing evidence;
  - Trainerize: physical assessment evidence;
  - Google Sheets: presentation and legacy manual evidence.
- Define normalized statuses:
  - `confirmed`
  - `showed`
  - `no_show`
  - `cancelled`
  - `invalid`
  - `unknown`
- Define reconciliation states:
  - `terminal_consistent`
  - `feedback_closes_confirmed`
  - `elapsed_confirmed`
  - `feedback_without_match`
  - `ambiguous_feedback_match`
  - `terminal_conflict`
  - `reschedule_superseded`
  - `legacy_unmatched`
- Define the metric:
  - numerator: unique terminal Showed events in the completed service period;
  - denominator: unique terminal Showed plus No show events;
  - excluded but separately reported: Cancelled, Invalid and superseded reschedules;
  - unresolved: elapsed Confirmed and Unknown.
- Define event-time and observation-time handling in Australia/Brisbane while preserving GHL UTC timestamps.
- Define the 60-minute resolution grace period.
- Define data retention, identified access, aggregate publication and exception ownership.
- Assign Admin Eve as operational exception owner and the appointment's assigned trainer as the initial outcome owner.

**Files affected:**

- `outputs/systems/strength-assessment-attendance-control.md`
- `outputs/systems/reporting-control-plane.md`
- `reporting_control/report_registry.json`

---

### Step 3: Add the Hub Attendance Contract and Persistent Ledger

Extend the existing hub rather than creating another private database.

**Actions:**

- Add strict contract validation for appointment event ID, contact ID, calendar ID, start/end, status, assigned user, observed time and source-run ID.
- Add feedback evidence validation for contact ID, form submission ID, submitted time, sales outcome and delivered-by value.
- Add append-only tables for:
  - appointment-event observations;
  - feedback evidence;
  - supporting conversion and Trainerize evidence references;
  - reconciliation decisions and rule version.
- Enforce uniqueness on GHL event ID plus source observation version.
- Preserve status history rather than overwriting the prior state.
- Add exception rows keyed by event ID and exception code.
- Ensure repeated webhook or polling deliveries are idempotent.
- Add schema and store tests.

**Files affected:**

- `operating_data_hub/contracts.py`
- `operating_data_hub/store.py`
- `operating_data_hub/tests/test_contracts_and_store.py`
- `operating_data_hub/tests/test_sa_attendance.py`

---

### Step 4: Build Read-Only GHL Appointment Collection

Collect only the approved Strength Assessment calendars.

**Actions:**

- Implement the existing retry, pagination and timeout patterns used by `pt_booking_shadow/ghl_client.py`.
- Read an overlapping historical window so late status changes are captured.
- Normalize the documented `appointmentStatus` and legacy misspelling fallback.
- Persist event ID, contact ID, calendar ID, assigned user, scheduled time, update time, status, deleted flag and source observation time.
- Treat deleted events as excluded evidence, not No show.
- Detect duplicated contact/start pairs, moved appointments and superseded reschedules.
- Reject partial source runs and retain the prior complete accepted snapshot.
- Register source freshness and expose it in system health.
- Do not add GHL mutation methods in this step.

**Files affected:**

- `operating_data_hub/sa_attendance.py`
- `operating_data_hub/config.py`
- `operating_data_hub/service.py`
- `operating_data_hub/tests/test_sa_attendance.py`

---

### Step 5: Reuse the Existing Consultant Feedback Form

Retain the existing form and completion workflow; do not create a parallel form or ask the consultant to repeat data already held on the appointment.

**Actions:**

- Use the appointment's assigned trainer as the authoritative consultant.
- Route missing-attendance follow-up to that assigned trainer.
- Send missing assignment and exceptional cover cases to Admin for correction.
- Do not duplicate the existing Sales Outcome or assessment-result fields.
- Preserve the current Consultant Performance spreadsheet action.
- Preserve the current Sale and No Sale branches.
- In `2.4 Consultation Feedback Complete`, add a protected webhook after the form trigger and before the outcome branch.
- Send only the required identifiers and evidence:
  - contact ID;
  - form submission ID;
  - submitted timestamp;
  - Sales Outcome;
  - assigned appointment user ID;
  - workflow execution ID if available.
- Add a deterministic delivery key so retries cannot create duplicate evidence.
- Verify that controlled test submissions still populate every existing assessment field.
- Verify that the No Sale branch still applies `no sale`, writes the Blog Topic Sheet row and enrols `2.5. No Sale - Follow Up`.
- Verify that the Sale branch remains dependent on completed agreement workflows for fulfilment.

**Files affected:**

- `outputs/systems/sales-conversion.md`
- `outputs/systems/ghl-backend-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `outputs/systems/ghl-custom-data-governance-register.md` for the calendar-assignment authority decision.

---

### Step 6: Add Protected Feedback Ingestion and Deterministic Matching

Match each feedback submission to one appointment without relying on name or email.

**Actions:**

- Add an authenticated `/api/v1/ingest/sa-feedback` endpoint.
- Validate authentication, timestamp age, replay key and payload size.
- Resolve the canonical person from GHL contact ID.
- Search only that contact's Strength Assessment events.
- Use the nearest eligible event that ended before submission and within the approved matching window.
- Require exactly one eligible match.
- Reject future appointments, Cancelled/Invalid events and already-superseded reschedules.
- If one Confirmed event matches, create `feedback_closes_confirmed`.
- If one Showed event matches, create `terminal_consistent`.
- If a No show event has feedback, create a high-priority `terminal_conflict`.
- If there are zero or multiple candidates, create an Admin Eve exception.
- Never use Sales Outcome to determine Showed versus No show.
- Add protected identified endpoint `/api/v1/sa-attendance/exceptions` and aggregate endpoint `/api/v1/sa-attendance/summary`.

**Files affected:**

- `operating_data_hub/app.py`
- `operating_data_hub/sa_attendance.py`
- `operating_data_hub/service.py`
- `operating_data_hub/tests/test_app.py`
- `operating_data_hub/tests/test_sa_attendance.py`

---

### Step 7: Define GHL Status Closure and Exception Operations

Make terminal status completion part of the consultant's existing post-session process.

**Actions:**

- Document the standard:
  - delivered assessment: submit Consultant Feedback and ensure the appointment is Showed;
  - did not attend: mark No show immediately;
  - cancelled: retain Cancelled;
  - duplicate/test/bad booking: use Invalid only under the approved rule.
- Keep `2.2 SA: No Show Rebook` and `2.3 SA: Cancelled Rebook` attached to their existing terminal statuses.
- Do not make missing feedback trigger the No Show workflow.
- Create one deduplicated Admin Eve exception when an appointment is still Confirmed 60 minutes after its end.
- Close the exception automatically when a terminal status or matched feedback arrives.
- Avoid creating a task when an existing unresolved task for the same event ID exists.
- Include appointment owner, delivered-by evidence, scheduled time and exact corrective action in the task.
- Verify weekends and due-date handling against the team task register.

**Files affected:**

- `outputs/systems/ghl-team-task-trigger-register.md`
- `outputs/systems/sales-conversion.md`
- `outputs/systems/strength-assessment-attendance-control.md`

---

### Step 8: Run Read-Only Shadow Reconciliation

Prove that the new rule is better than column K before enabling writes.

**Actions:**

- Run the hub collector at least every 15 minutes in shadow mode.
- Compare each elapsed event with:
  - GHL terminal status;
  - feedback submission;
  - Appointments K;
  - Appointments L;
  - agreement completion;
  - WARM opportunity state;
  - `strength assessment showed` and No Show tags;
  - Trainerize assessment evidence when available.
- Report differences without changing any source system.
- Measure:
  - event-match rate;
  - feedback-match rate;
  - unresolved elapsed rate;
  - K versus canonical disagreement rate;
  - duplicate/reschedule rate;
  - terminal conflicts;
  - false or duplicate exception tasks that would have been created.
- Review every discrepancy for two completed Monday-to-Sunday cycles.
- Require zero incorrect automatic Showed proposals before write activation.

**Files affected:**

- `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md`
- `context/roadmap.md`

---

### Step 9: Enable Controlled Feedback-to-Showed Closure

Activate the safest GHL write only after shadow acceptance.

**Actions:**

- Use the native GHL action if it can update the exact appointment event deterministically.
- Otherwise implement a narrowly scoped authenticated writer for the verified appointment update endpoint.
- Allow only `confirmed -> showed`.
- Require:
  - matched form submission;
  - one exact appointment event;
  - matching contact ID;
  - event end before form submission;
  - matching window satisfied;
  - no terminal conflict;
  - no existing Showed update already recorded.
- Refuse `no_show -> showed`, `cancelled -> showed`, `invalid -> showed` and all reverse transitions.
- Store request, response, timestamp, rule version and idempotency key.
- Start with a controlled test contact, then one live consultant-feedback event, then monitor the first 20 production closures.
- Leave `SA_ATTENDANCE_GHL_WRITE_ENABLED=false` until the explicit activation gate is passed.

**30 July 2026 build update:** Railway now reads the existing Consultant Feedback form directly and matches same-Brisbane-day repeat appointments before applying the wider seven-day window. The separate `sa-attendance-followup-v1` controller adopts matching GHL coach tasks, creates appointment-specific next-business-day Admin escalations, and auto-completes its governed tasks after resolution. `SA_ATTENDANCE_TASK_WRITE_ENABLED` remains a distinct fail-closed gate. The GHL coach dropdown exists, but its required visual placement on the live form remains an activation dependency.

**Files affected:**

- `operating_data_hub/sa_attendance.py`
- `operating_data_hub/config.py`
- `operating_data_hub/tests/test_sa_attendance.py`
- `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md`

---

### Step 10: Create the Governed Google Sheets Mirror

Make the Sheet useful to staff without making it the database.

**Actions:**

- Add an `SA Attendance` tab with:
  - Appointment ID;
  - Contact ID;
  - scheduled start and end;
  - appointment owner;
  - delivered by;
  - canonical status;
  - status effective time;
  - status source;
  - feedback submitted time;
  - conversion evidence;
  - reconciliation state;
  - exception owner;
  - last observed time;
  - rule version.
- Protect provider-owned and formula columns.
- Use full-row preconditions and event-ID upserts.
- Validate the exact Sheet ID, tab ID, headers and column positions before any write.
- Write nothing when the layout does not match.
- Add human-readable filtered views for unresolved and conflicting events.
- Relabel Appointments column K as `Legacy Show? - retired <cutover date>`.
- Remove K from current KPI ownership but preserve historical values.
- Do not add another editable Show? column.

**Files affected:**

- `operating_data_hub/sa_attendance_sheet.py`
- `operating_data_hub/config.py`
- `operating_data_hub/tests/test_sa_attendance_sheet.py`
- `scripts/SETUP.md`

---

### Step 11: Migrate KPI and Reporting Consumers

Make every report use the same metric definition.

**Actions:**

- Publish weekly counts for Booked, Showed, No show, Cancelled, Invalid and unresolved.
- Publish `Showed / (Showed + No show)` only when:
  - the attendance snapshot is complete and fresh;
  - all source calendars were read;
  - the reporting period is closed;
  - unresolved count is within the approved publication rule.
- Preferred fail-closed rule: if any elapsed unresolved appointment remains at weekly close, show rate is marked provisional and the unresolved count is displayed.
- Replace rows 57 to 63 K-based calculations with governed hub values after Sheet-write activation.
- Preserve source breakdown only when Lead Source is present and valid; otherwise expose Unknown rather than forcing Organic.
- Update the hub CEO report and dashboard to use governed attendance metrics instead of Sheet-derived show rate.
- Add attendance definition version and source freshness.
- Update `context/current-data.md` and JSON output.
- Update Discord's daily brief to show canonical status and elapsed unresolved exceptions.
- Keep one compatibility cycle where old and new values are displayed in the shadow review log.
- Remove old formulas only after all consumers show the same accepted values.

**Files affected:**

- `operating_data_hub/service.py`
- `operating_data_hub/app.py`
- `operating_data_hub/templates/dashboard.html`
- `operating_data_hub/kpi_adapter.py`
- `reporting_control/executive_brief.py`
- `scripts/insert_formulas.py`
- `scripts/patch_booking_rows.py`
- `scripts/sheets_client.py`
- `scripts/update_metrics.py`
- `scripts/test_formulas.py`
- `discord_bot/reports.py`
- `context/current-data.md`
- `context/current-data.json`

---

### Step 12: Build the Historical Backfill Without Restating KPIs

Recover event identity and confidence while preserving uncertainty.

**Actions:**

- Read GHL Strength Assessment events and the legacy Appointments rows.
- Match in this order:
  1. exact event ID if later rows contain it;
  2. contact ID plus exact scheduled timestamp;
  3. canonical identity plus exact scheduled timestamp;
  4. unique canonical identity within a narrow time tolerance.
- Classify each result:
  - exact;
  - corroborated;
  - ambiguous;
  - unmatched.
- Add supporting evidence:
  - feedback form;
  - agreement;
  - Trainerize assessment record;
  - pipeline/tag history;
  - K/L values.
- Do not use K alone to promote a historical Showed status.
- Produce identified detail only in the private data area.
- Publish an aggregate, privacy-safe backfill report to the shadow log.
- Ingest exact and approved corroborated records into the hub only after owner review.
- Do not rewrite historical weekly KPI cells without a separate explicit approval and a documented restatement note.

**Files affected:**

- `scripts/backfill_sa_attendance.py`
- `scripts/test_backfill_sa_attendance.py`
- `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md`

---

### Step 13: Cascade the Staff Operating Standard

Update the source material first and carry the change through every trainer-facing surface.

**Actions:**

- Update `reference/evolved-manual/02-assessment-system.md`.
- Update `reference/evolved-manual/scripts/assessments/strength-assessment-script.md`.
- Update `reference/sops/strength-assessment.md` and increment its revision history.
- Define the exact post-session actions for Showed, No show, Cancelled and cover delivery.
- Update `outputs/trainer-portal/10-strength-assessment.md`.
- Audit all 13 Course 10 quiz questions and add or revise a question only if required to test the new operating standard.
- Regenerate `outputs/trainer-portal/html/10-strength-assessment.html`.
- Use the Browser tool to update the live GHL Course 10 lesson and quiz in the same implementation task.
- Verify visible content, question count, publication state and learner access path.
- Update the GHL team task and sales-conversion registers.

**Files affected:**

- `reference/evolved-manual/02-assessment-system.md`
- `reference/evolved-manual/scripts/assessments/strength-assessment-script.md`
- `reference/sops/strength-assessment.md`
- `outputs/trainer-portal/10-strength-assessment.md`
- `outputs/trainer-portal/html/10-strength-assessment.html`
- `outputs/systems/sales-conversion.md`
- `outputs/systems/ghl-team-task-trigger-register.md`

---

### Step 14: Validate End to End and Cut Over

Prove one event through every system before retiring column K.

**Actions:**

- Test these scenarios:
  - Showed with immediate feedback;
  - Showed with late feedback;
  - No show with no feedback;
  - Cancelled before the session;
  - Invalid/test appointment;
  - active reschedule;
  - cancellation followed by fresh rebook;
  - returning prospect;
  - cover coach;
  - duplicate feedback webhook;
  - feedback with zero matching appointments;
  - feedback with two possible appointments;
  - agreement after No Sale;
  - elapsed Confirmed resolved after the exception is created.
- Verify the same appointment ID and status in:
  - GHL appointment list;
  - hub ledger;
  - protected attendance endpoint;
  - `SA Attendance` Sheet;
  - KPI weekly values;
  - CEO dashboard;
  - CEO report;
  - Discord daily brief.
- Confirm that No Show and Cancelled rebook workflows still fire exactly once.
- Confirm that Sale/No Sale and agreement fulfilment remain unchanged.
- Confirm that no member message is added or duplicated.
- Enable Sheet publication only after the end-to-end test passes.
- Rename and protect column K.
- Record the cutover timestamp and definition version.
- Mark the roadmap item Live only after two complete governed reporting cycles agree across all consumers.

**Files affected:**

- `outputs/reporting-control-plane/sa-attendance-shadow-review-log.md`
- `outputs/systems/strength-assessment-attendance-control.md`
- `context/roadmap.md`

---

### Step 15: Close Documentation and Workspace Maintenance

Make the final architecture discoverable in future sessions.

**Actions:**

- Update `CLAUDE.md` if the new source, backfill script or operating command is reusable workspace functionality.
- Update `scripts/SETUP.md` with environment variables, Railway settings and recovery steps.
- Record the final calendar IDs, form ID, workflow IDs, Sheet tab ID and metric version in the appropriate system register, not in `CLAUDE.md`.
- Document rollback:
  - disable GHL writer;
  - disable Sheet writer;
  - retain read-only collection;
  - preserve last accepted complete snapshot;
  - display the KPI as unavailable/provisional rather than falling back silently to K.
- Record outstanding historical ambiguities separately from the live cutover.

**Files affected:**

- `CLAUDE.md` if required
- `scripts/SETUP.md`
- `outputs/systems/ghl-backend-register.md`
- `outputs/systems/reporting-control-plane.md`
- `outputs/systems/strength-assessment-attendance-control.md`
- `context/roadmap.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `scripts/sheets_client.py`
- `scripts/insert_formulas.py`
- `scripts/patch_booking_rows.py`
- `scripts/test_formulas.py`
- `scripts/update_metrics.py`
- `discord_bot/reports.py`
- `operating_data_hub/kpi_adapter.py`
- `operating_data_hub/service.py`
- `operating_data_hub/app.py`
- `reporting_control/report_registry.json`
- `reporting_control/executive_brief.py`
- `outputs/systems/sales-conversion.md`
- `outputs/systems/lead-generation-nurture.md`
- `outputs/systems/ghl-backend-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `outputs/systems/reporting-control-plane.md`
- `reference/evolved-manual/02-assessment-system.md`
- `reference/evolved-manual/scripts/assessments/strength-assessment-script.md`
- `reference/sops/strength-assessment.md`
- `outputs/trainer-portal/10-strength-assessment.md`
- `outputs/trainer-portal/html/10-strength-assessment.html`
- `context/current-data.md`
- `context/current-data.json`
- `context/roadmap.md`

### Updates Needed for Consistency

- GHL workflow documentation must distinguish appointment-level status from contact-level tag and opportunity state.
- The Consultant Feedback documentation must explain its dual role: assessment/outcome capture and Showed evidence.
- The No Show workflow must remain dependent on explicit No show status, not missing feedback.
- Agreement workflows must remain conversion and fulfilment authority.
- Trainerize documentation must remain clear that it owns physical results, not appointment administration.
- Every show-rate consumer must use the same definition version and reporting period.
- The Appointments Sheet must visibly identify column K as legacy after cutover.
- The SOP revision history and Course 10 quiz must be updated before the live course change.
- The live GHL course must be synchronised in the same implementation task.

### Impact on Existing Workflows

- **`2. Strength Assessment`**: Booking and reschedule behaviour remains unchanged. New event identity is collected by the hub rather than adding another Sheet row dependency.
- **`2.2 SA: No Show Rebook`**: Remains the no-show communication and task path. It should fire only from an explicit No show status.
- **`2.3 SA: Cancelled Rebook`**: Remains the cancellation communication and task path.
- **`2.4 Send Consultation Feedback Survey`**: Remains the feedback delivery and chase workflow.
- **`2.4 Consultation Feedback Complete`**: Gains delivered-by evidence and a protected attendance webhook while preserving Consultant Performance and outcome branches.
- **`2.5. No Sale - Follow Up`**: Continues to own the No Sale nurture and opportunity movement; it no longer needs to be treated as the source of attendance.
- **Agreement workflows**: Continue to reconcile late Sale state and own fulfilment.
- **New Member and New PT Client workflows**: No change to lifecycle ownership.
- **Trainerize**: No write or provisioning change.
- **Google Sheets**: Changes from manual attendance source to governed mirror.
- **CEO dashboard and Discord**: Gain one consistent attendance status and visible unresolved exceptions.

---

## Validation Checklist

How to verify the implementation is complete and correct:

- [x] Baseline counts, formulas and live GHL capabilities are recorded before changes.
- [x] The attendance architecture decision and source hierarchy are documented.
- [x] Every event is keyed by GHL appointment ID.
- [x] The hub stores status history, feedback evidence, reconciliation state and rule version.
- [x] Source runs fail closed when calendar coverage is incomplete.
- [x] The existing Consultant Feedback form is reused.
- [x] Consultant attribution comes from the assigned calendar trainer without a duplicate form question.
- [x] The existing feedback form remains unchanged and its fields continue to persist.
- [ ] Sale and No Sale branches still execute exactly as documented.
- [x] Feedback webhook ingestion is authenticated, replay-safe and idempotent.
- [x] Feedback matches only one past Strength Assessment event.
- [x] Missing feedback never creates a No show.
- [x] Confirmed plus matched feedback produces only a controlled Showed proposal.
- [x] No show plus feedback produces a conflict, not an automatic rewrite.
- [x] Cancelled and Invalid never enter the show-rate denominator.
- [x] Elapsed Confirmed creates one deduplicated Admin Eve exception.
- [ ] Shadow mode runs for two complete reporting cycles.
- [ ] Zero incorrect automatic Showed proposals occur before activation.
- [x] GHL writes allow only Confirmed to Showed.
- [ ] Every write has an idempotency key and audit record.
- [x] The `SA Attendance` Sheet tab validates its layout before writing.
- [ ] Column K is preserved and labelled legacy after cutover.
- [ ] KPI rows no longer depend on Appointments column K.
- [x] Show rate equals Showed divided by Showed plus No show.
- [x] Unresolved elapsed appointments are visible in every relevant report.
- [ ] CEO dashboard, CEO API, Sheet and Discord agree for the same period.
- [x] Historical backfill labels confidence and performs no unapproved restatement.
- [x] Manual, SOP, trainer course, HTML and quiz are updated in source order.
- [ ] Live GHL Course 10 is updated and publication/access are verified.
- [ ] No member message or workflow enrolment is duplicated.
- [x] Rollback disables writers without losing the accepted evidence history.
- [x] `context/roadmap.md` and `CLAUDE.md`, if applicable, reflect the completed system.

---

## Success Criteria

The implementation is complete when:

1. At least 98% of elapsed Strength Assessment appointments resolve to a terminal status within 24 hours, and every remaining appointment is an owned exception.
2. Every Showed event has either a matched Consultant Feedback submission or an explicitly reviewed exception.
3. Every No show is explicitly recorded in GHL and reaches the existing No Show rebook workflow exactly once.
4. Cancelled, Invalid and superseded reschedules are excluded from the show-rate denominator.
5. Google Sheets, the CEO dashboard, CEO report, current-data outputs and Discord publish the same versioned weekly attendance figures.
6. Column K is no longer used by any active KPI or reporting consumer.
7. Two consecutive completed reporting cycles show zero unexplained differences between the hub, GHL and the governed Sheet mirror.
8. The first 20 feedback-driven Showed closures contain zero incorrect appointment updates.
9. The Consultant Feedback, Sale, No Sale, agreement, onboarding and Trainerize processes continue without regression.
10. The live trainer course and source documentation teach the same post-session status and feedback standard.

---

## Notes

- The 60-minute grace period is an operational default, not a claim that feedback must always be completed within 60 minutes. Late feedback remains accepted and reconciles the exception.
- The hub should retain the latest complete accepted attendance snapshot if GHL or the feedback webhook is temporarily unavailable.
- The CEO dashboard should expose unresolved count and freshness but should not display prospect names. Identified exceptions belong behind the protected attendance endpoint and staff Sheet.
- Lead-source breakdown must fail to Unknown when source is blank or non-canonical. It must not silently classify missing values as Organic.
- Returning prospects and rebooks are naturally handled once event ID, rather than Sheet-row creation, defines the appointment population.
- A future Trainerize-to-GHL assessment integration can add stronger delivery evidence without changing the appointment identity or show-rate definition.

---

## Implementation Notes

**Staged:** 2026-07-29

### Summary

Implemented `sa-attendance-v1` as a shadow-only, event-ID attendance ledger in the Operating Data Hub. It includes complete-run GHL collection, append-only evidence and decision history, deterministic Consultant Feedback matching, protected aggregate and identified APIs, fail-closed reporting, a controlled Sheet publisher and a read-only confidence-labelled historical backfill.

Created and verified the empty protected `SA Attendance` Sheet tab with ID `1446062006`, exact headers and unresolved/conflict filter views. Both write gates remain false; Appointments column K and live KPI cells remain unchanged until the acceptance gates pass.

Cascaded the post-session standard through the assessment manual, verbatim script, SOP version 1.8, Course 10 Markdown, HTML and the 13-question quiz. The live GHL course and form remain unchanged pending confirmation for the external saves.

### Validation Completed

- 129 targeted automated tests passed.
- The complete trainer portal audit passed across all 13 numbered course files and Practical Sign-Off.
- Python compilation and report-registry JSON validation passed.
- The read-only 120-day backfill compared 251 legacy rows with 109 events: 85 corroborated, zero ambiguous and 166 unmatched; no KPI restatement occurred.
- The live Sheet header and tab ID were read back successfully.
- The full repository test command is not a valid offline suite because `scripts/test_ghl_email_stats.py` performs a live GHL request during test collection.

### Outstanding Acceptance Gates

- Complete two full Monday-to-Sunday shadow cycles with zero incorrect Showed proposals.
- Review the first 20 production task closures before enabling the separate appointment-status or Sheet writers.
- Relabel Appointments column K and replace live KPI rows only at cutover.

### Protected Follow-up Deployment

**Deployed:** 2026-07-30

Railway deployment `b250136b-b5ec-404d-bb44-1e328848915f` is healthy with task writes disabled. A fresh production attendance refresh returned a successful protected preview: eight recent elapsed appointments remain Confirmed, producing eight coach follow-up proposals and eight next-business-day Admin Eve escalation proposals. Four recent appointments had already resolved and are in scope for governed task closure once writes are enabled. The preview created, edited and completed zero tasks.

The full Operating Data Hub test suite passes: 102 tests. Follow-up execution is bounded to the configured recent control window so it does not re-query historical contacts on every Railway run.

### Staff-task Activation

**Activated:** 2026-07-30

The owner chose calendar assignment as the authoritative consultant, so the unused proposed `SA: Assessment Delivered By` field was deleted and the form remains unchanged. A controlled live test proved that the appointment's assigned user receives the task, and a second controlled test proved governed tasks close automatically after resolution.

The live workflow audit found no competing two-hour feedback chase; its two-hour booking-confirmation branch is unrelated and was preserved. Railway deployment `84d6bef7-c4a5-4795-bdd9-ac96d6c94f69` enabled the separate staff-task writer. The first run produced all 16 expected stages for eight unresolved appointments. An immediate repeat run retained exactly 16 open governed stages with zero missing and zero duplicate markers. The current full hub suite passes 101 tests.

### Deviations from Plan

The plan is not marked Implemented because its own acceptance criteria require time-based evidence that cannot exist on the build date. The staff-task writer is live; appointment-status, Sheet and KPI publication writes remain deliberately unchanged.

### Issues Encountered

The historical source contains no reliable GHL Showed or No show history in the baseline window. The backfill therefore preserves uncertainty instead of promoting legacy column K values.
