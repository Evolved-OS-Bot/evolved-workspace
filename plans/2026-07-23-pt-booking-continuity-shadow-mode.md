# Plan: PT Booking Continuity Shadow Mode

**Created:** 2026-07-23
**Status:** Shadow Pilot Live
**Request:** Scope a complete read-only shadow system that audits active PT booking continuity weekly, reacts to relevant changes and shows what a future rolling-booking controller would do without changing GHL appointments.

---

## Overview

### What This Plan Accomplishes

Build a Railway-hosted PT booking-continuity auditor that reconciles every active PT client's expected weekly schedule against their actual GHL appointments. It will run a complete audit every Monday, perform targeted rechecks after relevant appointment, hold and cancellation changes, and send Admin Eve a concise exception-led report.

The service will remain structurally read-only during shadow mode. It can calculate and record `would create`, `would retain`, `would pause` and `would remove after cancellation` recommendations, but it will contain no callable GHL appointment write or delete methods.

### Why This Matters

PT calendar continuity currently depends on a Week 10 reminder and manual rebooking. The shadow system proves the data, pattern-inference and exception rules required to maintain a rolling 13-week booking horizon without risking duplicate sessions, overwriting legitimate reschedules or extending a client beyond an accepted cancellation.

The design separates three concerns that are currently conflated:

1. An active client's appointments should continue while PT remains active.
2. The 13-week review cadence should not determine whether appointments exist.
3. Cancellation is the only normal event that should remove future PT bookings.

---

## Current State

### Relevant Existing Structure

- `plans/2026-04-27-natural-language-appointment-rescheduler.md`
  - Defines the broader appointment-management agent, live calendar registry, recurring-series verification, idempotency, Admin Eve authority and the Anika/Kanika acceptance case.
- `outputs/systems/personal-training.md`
  - Documents the 15 active trainer-specific PT calendars, PT pipeline stages, tags, PT block fields, hold and cancellation dependencies.
- `outputs/systems/membership-hold.md`
  - Documents PT hold status, type, start date and end date fields.
- `outputs/systems/cancellation-system.md`
  - Documents PT cancellation status, notice end date, final access date and Admin Eve processing.
- `stripe_handler/`
  - Provides the existing Railway and Flask pattern for external GHL-triggered operational services.
- `triage_bot/`
  - Provides the current scheduled reporting pattern, Admin Eve email destination, Resend integration and Brisbane timezone handling.
- `scripts/.env`
  - Contains the existing GHL private integration token and location ID.
- GHL workflow `PT: Block Tracking & 13-Week Rebooking`
  - Workflow ID `280a2ca3-0f51-4f03-b5dc-c271c2ef8075`.
  - Starts a 13-week tracking period from the first qualifying PT booking and gives Admin Eve a rebooking task at Week 10.

### Gaps or Problems Being Addressed

- The Week 10 workflow cannot inspect actual future appointment coverage.
- It cannot distinguish a complete 13-week forward schedule from a short or broken series.
- It cannot identify isolated gaps, duplicates, duration changes, trainer conflicts or stale former-trainer bookings.
- It cannot reliably distinguish a permanent weekly slot from a one-off reschedule or cover session.
- It does not stop rebooking recommendations when PT cancellation has been accepted.
- It does not use the final access date as the booking-removal boundary.
- `PT Only` does not encode weekly frequency in its pipeline stage, so the frequency must come from tags or be inferred and flagged.
- A PT hold should pause booking-extension recommendations without deleting existing bookings.
- GHL may return recurring master records before all individual instances have materialised, so immediate counting can falsely report gaps.
- There is no historical ledger showing what the continuity controller would have recommended and whether Admin agreed.

---

## Proposed Changes

### Summary of Changes

- Create a standalone `pt_booking_shadow` service with one always-on Railway process.
- Add an internal weekly scheduler for Monday at 5:30 am Australia/Brisbane.
- Add authenticated webhook endpoints for targeted appointment and PT state rechecks.
- Build a read-only GHL client limited to contacts, opportunities, calendars, users and appointment/event reads.
- Build a governed registry of the current PT calendars and eligible trainers.
- Resolve the active PT cohort from PT pipeline stages and current PT tags.
- Apply explicit hold and cancellation rules before making any continuity recommendation.
- Infer canonical weekly patterns deterministically from recurring metadata, recent history and future bookings.
- Compare expected occurrences with actual GHL events across a rolling 13-week horizon.
- Debounce recurring-series changes before auditing so GHL has time to expand instances.
- Classify every client into an operational outcome with evidence and a confidence score.
- Store audit runs and targeted checks in a persistent SQLite ledger on a Railway volume.
- Send Admin Eve a weekly exception-led HTML report with a CSV attachment.
- Send immediate event alerts only for high-risk exceptions; routine event checks roll into the weekly report.
- Add comprehensive unit, fixture and acceptance tests.
- Update PT documentation and the roadmap after implementation.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `pt_booking_shadow/app.py` | Flask entry point, health endpoint, authenticated event endpoints and scheduler startup. |
| `pt_booking_shadow/config.py` | Environment parsing, Brisbane timezone, thresholds, field IDs and safety flags. |
| `pt_booking_shadow/models.py` | Typed internal records for contacts, appointments, patterns, expected occurrences, findings and reports. |
| `pt_booking_shadow/ghl_client.py` | Read-only GHL API wrapper with pagination, retries, rate-limit handling and no write methods. |
| `pt_booking_shadow/calendar_registry.py` | Synchronises and validates active PT calendars, trainers, duration and service eligibility. |
| `pt_booking_shadow/cohort.py` | Resolves active, holding, ending and cancelled PT contacts from tags, pipeline opportunities and custom fields. |
| `pt_booking_shadow/patterns.py` | Deterministic canonical-pattern inference and confidence scoring. |
| `pt_booking_shadow/reconciler.py` | Builds the 13-week expected schedule, compares it with live events and produces shadow recommendations. |
| `pt_booking_shadow/state_store.py` | SQLite schema and persistence for runs, contacts, findings, events, deduplication and Admin decisions. |
| `pt_booking_shadow/reporting.py` | HTML email, CSV export, summaries and immediate high-risk exception alerts. |
| `pt_booking_shadow/run_weekly.py` | Manually invocable weekly audit entry point for local testing and recovery runs. |
| `pt_booking_shadow/requirements.txt` | Pinned Python dependencies. |
| `pt_booking_shadow/railway.toml` | Single-worker Railway web service configuration. |
| `pt_booking_shadow/.env.example` | Required environment variable names and safe example values. |
| `pt_booking_shadow/README.md` | Operating instructions, report definitions, deployment, recovery and graduation process. |
| `pt_booking_shadow/tests/conftest.py` | Shared fixtures and deterministic Brisbane dates. |
| `pt_booking_shadow/tests/test_cohort.py` | Active, PT Only, old-client, hold and cancellation cohort tests. |
| `pt_booking_shadow/tests/test_patterns.py` | Stable pattern, reschedule, cover, frequency and ambiguity tests. |
| `pt_booking_shadow/tests/test_reconciler.py` | Horizon, gap, duplicate, hold and cancellation-boundary tests. |
| `pt_booking_shadow/tests/test_event_debounce.py` | Delayed recurring-instance and duplicate webhook tests. |
| `pt_booking_shadow/tests/test_reporting.py` | Report grouping, sensitive-data handling, links and CSV tests. |
| `pt_booking_shadow/tests/fixtures/anika_kanika.json` | Sanitised acceptance fixture based on the verified Anika/Kanika scheduling case. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `plans/2026-04-27-natural-language-appointment-rescheduler.md` | Cross-reference the implemented shadow engine as the evidence and inference layer for the future write-enabled controller. |
| `outputs/systems/personal-training.md` | Document the deployed shadow service, cohort rules, report categories, ownership and safety boundary. |
| `outputs/systems/ghl-backend-register.md` | Register any dedicated read-only webhook workflows or app webhook subscriptions created during implementation. |
| `outputs/systems/ghl-team-task-trigger-register.md` | Record Admin Eve's weekly report and any immediate high-risk exception handoff. |
| `context/roadmap.md` | Move PT Rolling Booking Continuity Controller from Scoped to In Progress when implementation begins, then mark Shadow Pilot Live after deployment and first verified run. |
| `CLAUDE.md` | Add `pt_booking_shadow/` to the workspace structure only after the service exists and is deployable. |

### Files to Delete (if any)

None. The current GHL Week 10 rebooking workflow remains published during shadow mode and provides the operational fallback.

---

## Design Decisions

### Key Decisions Made

1. **Weekly full audit, not daily**: A Monday audit provides sufficient lead time while avoiding repetitive Admin Eve noise.
2. **Monday at 5:30 am Brisbane time**: The report is ready before the work week begins and does not depend on daylight-saving conversions.
3. **Event-driven targeted rechecks**: Appointment, PT hold and PT cancellation changes re-audit only the affected contact between weekly runs.
4. **Event checks are normally silent**: Findings are stored for the weekly report. Immediate email is reserved for high-risk exceptions such as an accepted PT cancellation with future bookings after the final access date or a missing final access date.
5. **Strict read-only GHL boundary**: Shadow mode has no GHL appointment POST, PUT or DELETE implementation. `SHADOW_MODE=true` is mandatory and the application refuses to start if it is absent or false.
6. **Deterministic inference, not an LLM**: Weekly slots, dates, counts and conflicts are structured data. Deterministic rules are safer, testable and explainable.
7. **13-week rolling horizon**: Every canonical weekly slot is evaluated for its next 13 occurrences.
8. **Recurring metadata has priority**: A valid recurring master or consistent future series is stronger evidence than isolated historical appointments.
9. **Reschedules do not redefine the canonical pattern**: One-off deviations remain fulfilled occurrences but do not move the permanent weekly slot.
10. **Ambiguity is an exception, not a guess**: Low-confidence or conflicting patterns are reported as `PATTERN_CONFIRMATION_REQUIRED`.
11. **Pipeline and tags validate frequency**: PT 1, 2 and 3 p.wk stages are authoritative expectations. `1 p.wk`, `2 p.wk` and equivalent tags supplement `PT Only`; otherwise the pattern is inferred and explicitly flagged.
12. **Only PT holds pause PT recommendations**: `HS: Hold Type = PT` combined with Pending Hold, Escalated Hold or On Hold pauses top-up recommendations. Membership-only holds do not silently pause PT.
13. **Holds do not produce removal recommendations**: Existing appointments remain visible and retained. The report shows the hold period and expected post-hold pattern.
14. **Accepted PT cancellation stops top-ups**: `CS: Cancellation Type = PT` with Notice Active or Cancelled prevents any extension recommendation.
15. **Final Access Date is the deletion boundary**: Only appointments strictly after `CS: Final Access Date` can be classified as `WOULD_REMOVE_AFTER_CANCELLATION`. If that field is blank, the system reports `CANCELLATION_DATE_MISSING` and never infers a removal date.
16. **Persistent single-service architecture**: One Railway web process runs Flask, APScheduler and SQLite on a mounted volume. Gunicorn runs a single worker to prevent duplicate weekly jobs.
17. **Recurring changes are debounced**: Appointment events for a contact are consolidated for 10 minutes, then re-read. Incomplete recurring expansion is polled for up to 30 minutes before a finding is finalised.
18. **Email is the primary Admin Eve surface**: The established `admin@theevolvedgym.com.au` route receives the report. Discord remains optional unless a dedicated operational webhook is approved.
19. **No GHL contact-field writes in shadow mode**: Booked-through date, confidence and proposed changes remain in the shadow ledger until the write-enabled phase is approved.
20. **Current workflow remains the fallback**: The Week 10 task is not retired until shadow accuracy has been measured and an operational replacement is live.

### Alternatives Considered

- **Daily full scans**: Rejected because PT patterns change slowly and daily reports would create duplicate noise.
- **Pure GHL workflow implementation**: Rejected because fixed waits cannot reliably inspect expanded recurring instances, infer patterns, calculate coverage or prevent duplicates.
- **Automatic appointment creation immediately**: Rejected until the inference rules have been observed against real clients.
- **Using `CS: Notice End Date` as the removal boundary**: Rejected because the documented billing calculation can produce a later final service/access date.
- **Using the contact owner as the primary recipient**: Rejected because Admin Eve is the accountable booking operator; trainers should receive only exceptions requiring delivery input.
- **Writing shadow results into GHL custom fields**: Deferred because it would mutate the live database before the model is validated and add new field governance overhead.
- **Google Sheets as the only datastore**: Rejected as the primary state store because event deduplication and transactional audit history are better served by SQLite. CSV report attachments still provide portable evidence.
- **Two Railway services, one cron and one webhook service**: Rejected because separate processes would require a shared external database and more deployment coordination.

### Open Questions (if any)

No blocking policy questions remain for shadow implementation.

The following can be confirmed after the first report without changing the engine:

- Whether Admin Eve also wants a dedicated Discord copy.
- Whether the weekly report should be delivered at 5:30 am or 6:00 am.
- Whether high-risk event alerts should also copy Peter.

---

## Detailed Functional Specification

### Active PT Cohort

Include a contact when either condition is true:

- The contact has the `personal training` tag and does not have `old pt client`.
- The contact has an open opportunity in one of the Membership Pipeline PT stages:
  - PT Only: `58247f13-4a47-40f8-8289-35d62fc138b3`
  - PT 1 p.wk: `9ce28fb1-f43b-472a-ac11-1b4c147b202b`
  - PT 2 p.wk: `01d615da-4bd4-4bf3-a5c6-54332588367d`
  - PT 3 p.wk: `edf7f617-e058-438a-978a-330fa262ef8e`

Retain ending, cancelled and holding contacts in the audit cohort so their future appointments can be checked, but classify them separately from active continuity clients.

### Status Precedence

Apply statuses in this order:

1. PT cancellation with Notice Active or Cancelled.
2. PT hold with Pending Hold, Escalated Hold or On Hold.
3. Former PT client.
4. Active PT.
5. Ambiguous status.

An accepted PT cancellation always suppresses future top-up recommendations. A PT hold suppresses top-ups only across the hold interval and does not produce deletions.

### Data Window

For each client:

- Read 8 completed weeks of historical PT events.
- Read the current week.
- Read 15 future weeks to allow 13-week coverage plus boundary verification.
- Read recurring master metadata and expanded calendar events.
- Use Australia/Brisbane for all grouping and comparisons.

### Pattern Inference Order

1. Use a valid active recurring series when its trainer, duration and frequency agree with the contact's current PT state.
2. Otherwise derive modal weekly slots from future bookings.
3. Use recent completed history only as supporting evidence.
4. Treat isolated replacements, cover sessions, public holidays and manually moved sessions as deviations rather than permanent pattern changes.
5. Compare inferred frequency with pipeline stage and frequency tags.
6. Require a confidence score of at least 0.80 for a `WOULD_TOP_UP` recommendation.
7. Anything below 0.80 becomes `PATTERN_CONFIRMATION_REQUIRED`.

### Occurrence Matching

An expected occurrence is satisfied when an active PT appointment exists for the contact within the configured time tolerance and expected service duration.

- Default time tolerance: exact start time.
- A known rescheduled appointment can satisfy the same service week without redefining the canonical slot.
- Cancelled, invalid and no-show events do not count as future coverage.
- Completed or showed events count only in historical pattern evidence.
- Duplicate active events at the same time are reported.
- Cover-trainer appointments can satisfy the occurrence but are reported separately so they do not change the assigned trainer.

### Finding Categories

| Category | Meaning | Shadow Recommendation |
| --- | --- | --- |
| `HEALTHY` | All 13 future occurrences are covered and no conflict exists. | No action. |
| `WOULD_TOP_UP` | Pattern is high-confidence and one or more occurrences after the booked-through date are missing. | List exact proposed dates; do not create. |
| `GAP_INSIDE_SERIES` | A missing occurrence exists before later booked appointments. | Admin review; do not assume intentional absence. |
| `NO_FUTURE_BOOKINGS` | Active PT client has no valid future PT appointments. | Urgent Admin Eve exception. |
| `PATTERN_CONFIRMATION_REQUIRED` | Pattern or frequency confidence is below threshold. | Admin confirms the canonical slot pattern. |
| `FREQUENCY_MISMATCH` | GHL appointments disagree with pipeline stage or tags. | Admin checks service entitlement and schedule. |
| `TRAINER_OR_DURATION_MISMATCH` | Future appointments disagree with the current trainer or PT service. | Admin checks whether this is cover, transfer or stale data. |
| `DUPLICATE_APPOINTMENT` | Multiple active events cover the same contact and time. | Admin checks before any future automation. |
| `PT_HOLD_ACTIVE` | PT-specific hold is current or pending. | Pause top-up; retain appointments. |
| `PT_HOLD_RETURN_GAP` | No valid booking is present after the PT hold end date. | Admin plans the return pattern. |
| `PT_NOTICE_ACTIVE` | Accepted PT cancellation has a future final access date. | Stop top-up and retain through final access date. |
| `WOULD_REMOVE_AFTER_CANCELLATION` | Appointments exist strictly after the verified PT final access date. | List them for Admin; do not delete. |
| `CANCELLATION_DATE_MISSING` | Accepted PT cancellation lacks Final Access Date. | Immediate Admin Eve exception. |
| `FORMER_PT_WITH_FUTURE_BOOKINGS` | Former PT tag exists but active future PT events remain. | Admin checks whether status or appointments are stale. |
| `API_OR_DATA_ERROR` | Required records could not be loaded or reconciled. | Retry and show technical exception without making an operational recommendation. |

### Weekly Report

The HTML email should contain:

1. Run time, cohort size and data completeness.
2. Counts by category.
3. High-risk exceptions first.
4. Clients requiring Admin Eve action.
5. `WOULD_TOP_UP` proposals with exact pattern, booked-through date, count and proposed date range.
6. Holds and cancellations.
7. Healthy-client summary collapsed to counts, with details in the CSV.
8. Direct GHL contact links.
9. Clear `SHADOW MODE: NO GHL APPOINTMENTS WERE CHANGED` banner.

The CSV should include:

- Run ID
- Contact ID and contact name
- GHL contact URL
- Effective PT status
- Pipeline stage
- Expected frequency
- Trainer
- Duration
- Canonical slot or slots
- Confidence score
- Last completed appointment
- Last future appointment
- Booked-through date
- Weeks of complete coverage
- Finding category
- Proposed occurrence dates
- Hold start and end dates
- Cancellation status
- Final access date
- Evidence and reason

### Event-Driven Checks

Accept authenticated events for:

- PT appointment created.
- PT appointment updated or rescheduled.
- PT appointment cancelled or deleted.
- PT Hold Status, Hold Type, Hold Start Date or Hold End Date changed.
- PT Cancellation Status, Cancellation Type or Final Access Date changed.
- PT trainer, service, frequency tag or Membership Pipeline PT stage changed.

For appointment series:

1. Store the event and contact ID.
2. Debounce for 10 minutes.
3. Re-read expanded calendar events.
4. Poll at increasing intervals for up to 30 minutes if the recurring master exists but instances are incomplete.
5. Run a targeted reconciliation.
6. Store the result.
7. Email immediately only for high-risk cancellation or zero-future-booking exceptions.

### Shadow Safety Enforcement

- `SHADOW_MODE` must equal `true`.
- The GHL client exposes only GET requests.
- Tests scan the service source for forbidden appointment write endpoints and HTTP verbs.
- Every report states that no live data changed.
- Webhook endpoints accept events but do not acknowledge any requested mutation.
- Failed or incomplete reads result in `API_OR_DATA_ERROR`, never a guessed recommendation.
- No member messages, trainer messages, GHL tasks, tags, fields, opportunities or appointments are created.

---

## Step-by-Step Tasks

Execute these tasks in order during implementation.

### Step 1: Verify Live Read Access and Freeze the Data Contract

Confirm the existing private integration token can read all required resources before writing application logic.

**Actions:**

- Verify scopes for contacts, custom fields, opportunities, calendars, users and calendar events.
- Fetch the 15 current PT calendars and record IDs, trainer IDs, duration and location configuration.
- Verify expanded event reads across a known recurring PT series.
- Verify contact custom fields return hold, cancellation, trainer and PT block values.
- Verify opportunities can be filtered to the four PT stages.
- Record sample payload shapes as sanitised test fixtures.
- Do not output token values or member-sensitive information.

**Files affected:**

- `pt_booking_shadow/tests/fixtures/`
- `pt_booking_shadow/README.md`

---

### Step 2: Scaffold the Service and Enforce Shadow Mode

Create the service structure, dependency pins, configuration and safe startup behaviour.

**Actions:**

- Create the files listed above.
- Use Flask, Gunicorn, APScheduler, requests, pydantic or dataclasses, tenacity, pytest and Resend-compatible HTTP calls.
- Configure one Gunicorn worker.
- Require `GHL_API_KEY`, `GHL_LOCATION_ID`, `RESEND_API_KEY`, `ADMIN_EMAIL_TO`, `WEBHOOK_SHARED_SECRET`, `SHADOW_MODE=true` and `DATABASE_PATH=/data/pt_booking_shadow.db`.
- Refuse startup if shadow mode is false.
- Add `/health` with service status, last successful full run and current shadow flag.
- Mount a Railway persistent volume at `/data`.

**Files affected:**

- `pt_booking_shadow/app.py`
- `pt_booking_shadow/config.py`
- `pt_booking_shadow/requirements.txt`
- `pt_booking_shadow/railway.toml`
- `pt_booking_shadow/.env.example`

---

### Step 3: Build the Read-Only GHL Client

Implement resilient, paginated reads without any mutation capability.

**Actions:**

- Implement contacts, opportunities, users, calendars, contact appointments and expanded calendar-event reads.
- Add pagination, timeouts, exponential retries and rate-limit handling.
- Return typed models rather than raw dictionaries outside the client boundary.
- Redact authorization headers and contact phone/email from logs.
- Add a source-level test that fails if POST, PUT, PATCH or DELETE appointment methods are introduced during shadow mode.

**Files affected:**

- `pt_booking_shadow/ghl_client.py`
- `pt_booking_shadow/models.py`
- `pt_booking_shadow/tests/`

---

### Step 4: Build and Validate the Live PT Calendar Registry

Create a governed registry rather than a permanent person-specific hard-coded map.

**Actions:**

- Synchronise calendars at startup and before every weekly run.
- Include only active 30-, 45- and 60-minute PT calendars for Megan, Piper, Nora, Katrina and Leisa.
- Store calendar ID, user ID, trainer name, duration, timezone, meeting location and active status.
- Reject former-staff and non-PT calendars.
- Flag registry changes, missing expected calendars or unexpected active trainer calendars in the weekly report.

**Files affected:**

- `pt_booking_shadow/calendar_registry.py`
- `pt_booking_shadow/tests/test_cohort.py`

---

### Step 5: Implement Cohort and Status Resolution

Resolve who should be audited and their governing PT state.

**Actions:**

- Load contacts through both PT tags and PT-stage opportunities.
- Deduplicate contacts.
- Resolve frequency from PT stage first, then tags, then inferred pattern.
- Treat PT Only without a frequency tag as frequency-unknown until inference succeeds.
- Apply the status-precedence rules.
- Distinguish PT holds from membership holds.
- Distinguish PT cancellation from membership cancellation.
- Store the evidence used to select every effective status.

**Files affected:**

- `pt_booking_shadow/cohort.py`
- `pt_booking_shadow/models.py`
- `pt_booking_shadow/tests/test_cohort.py`

---

### Step 6: Implement Deterministic Pattern Inference

Infer canonical weekly appointment patterns without allowing one-off changes to redefine them.

**Actions:**

- Prefer recurring rules and consistent future masters.
- Derive modal weekday, local time, calendar/trainer and duration slots where recurring metadata is unavailable.
- Compare inferred frequency to stage and tags.
- Score evidence from 0.00 to 1.00.
- Explain each score in human-readable evidence.
- Mark cover sessions and isolated reschedules as deviations.
- Require at least 0.80 confidence before generating `WOULD_TOP_UP`.
- Produce ambiguity and mismatch findings below threshold.

**Files affected:**

- `pt_booking_shadow/patterns.py`
- `pt_booking_shadow/tests/test_patterns.py`
- `pt_booking_shadow/tests/fixtures/anika_kanika.json`

---

### Step 7: Implement the 13-Week Reconciler

Build expected occurrences and compare them with actual events.

**Actions:**

- Generate the next 13 expected occurrences for each canonical slot.
- Match existing valid appointments.
- Calculate last completed appointment, last future appointment, booked-through date and continuous weeks of coverage.
- Identify internal gaps, end-of-series top-ups, duplicates, trainer changes, duration changes and no-future-booking cases.
- Pause recommendations across PT hold intervals without deleting or hiding existing bookings.
- Resume expected occurrences after the hold end date.
- Stop top-up when PT cancellation is Notice Active or Cancelled.
- Use only Final Access Date for `WOULD_REMOVE_AFTER_CANCELLATION`.
- Return errors instead of recommendations when required data is incomplete.

**Files affected:**

- `pt_booking_shadow/reconciler.py`
- `pt_booking_shadow/tests/test_reconciler.py`

---

### Step 8: Add Persistent Audit State and Event Deduplication

Store enough history to compare runs and prevent repeated event work.

**Actions:**

- Create SQLite tables for full runs, contact snapshots, findings, incoming events, targeted runs and Admin decisions.
- Add indexes for contact ID, run time, event ID and category.
- Store the input evidence and generated recommendation as JSON.
- Retain 12 months of detailed runs and aggregate older run counts.
- Deduplicate exact webhook event IDs.
- Debounce multiple changes for one contact within 10 minutes.
- Track the last successful weekly run for restart catch-up.

**Files affected:**

- `pt_booking_shadow/state_store.py`
- `pt_booking_shadow/tests/test_event_debounce.py`

---

### Step 9: Build Weekly and Immediate Reporting

Create an exception-led Admin Eve report and portable audit evidence.

**Actions:**

- Generate the report structure and CSV columns specified above.
- Send the report to `admin@theevolvedgym.com.au`.
- Put high-risk exceptions first and collapse healthy detail into the CSV.
- Include direct GHL contact links.
- Add the shadow-mode banner.
- Send immediate alerts only for:
  - PT cancellation missing Final Access Date.
  - Active future PT appointments after Final Access Date.
  - Active PT client with zero future appointments following an appointment deletion event.
  - Registry or API failure affecting the entire audit.
- Do not send member or trainer communications.

**Files affected:**

- `pt_booking_shadow/reporting.py`
- `pt_booking_shadow/tests/test_reporting.py`

---

### Step 10: Add the Weekly Scheduler and Recovery Behaviour

Run the full audit reliably without duplicate schedules.

**Actions:**

- Schedule Monday at 5:30 am Australia/Brisbane.
- Record start, completion, failure and duration.
- Prevent overlapping full runs with a database lock.
- On service restart, run a catch-up audit only if Monday's scheduled run was missed and no successful run exists for the current week.
- Allow a protected manual run endpoint or command for recovery and testing.

**Files affected:**

- `pt_booking_shadow/app.py`
- `pt_booking_shadow/run_weekly.py`
- `pt_booking_shadow/state_store.py`

---

### Step 11: Add Event-Driven Targeted Checks

Connect appointment and PT-state changes to read-only rechecks.

**Actions:**

- Add authenticated endpoints for appointment, hold, cancellation and PT profile changes.
- Prefer official GHL app webhooks when available.
- If the private integration cannot subscribe to required webhooks, create dedicated GHL shadow-trigger workflows that only send signed webhook payloads to the service.
- Keep new workflow triggers separate from the current booking, hold and cancellation workflows where possible.
- Include contact ID, event type, event ID and occurred-at time only.
- Debounce, re-read and reconcile the affected client.
- Register every trigger or subscription in the backend register.

**Files affected:**

- `pt_booking_shadow/app.py`
- `pt_booking_shadow/state_store.py`
- `outputs/systems/ghl-backend-register.md`

---

### Step 12: Test Against Realistic and Known Cases

Validate the engine before deployment.

**Actions:**

- Test one, two and three sessions per week.
- Test PT Only with and without frequency tags.
- Test stable recurring series.
- Test isolated reschedule without pattern drift.
- Test cover trainer without trainer reassignment.
- Test a missing middle occurrence.
- Test an ended series needing a top-up.
- Test duplicate events.
- Test delayed recurring expansion.
- Test PT hold, membership-only hold and return-from-hold gap.
- Test PT cancellation with and without Final Access Date.
- Test membership cancellation while PT remains active.
- Test former PT client with future bookings.
- Run the sanitised Anika/Kanika transfer case.
- Confirm every test produces the expected category, evidence and no GHL writes.

**Files affected:**

- `pt_booking_shadow/tests/`

---

### Step 13: Deploy in Shadow Pilot

Deploy without changing existing PT booking operations.

**Actions:**

- Create the Railway service and persistent volume.
- Configure environment variables without committing secrets.
- Verify health, registry sync and a manual dry run.
- Review the first report privately before enabling weekly delivery.
- Enable the Monday schedule.
- Enable targeted webhooks after the full weekly run is stable.
- Leave `PT: Block Tracking & 13-Week Rebooking` published.
- Record deployment and ownership.

**Files affected:**

- `pt_booking_shadow/railway.toml`
- `pt_booking_shadow/README.md`
- `outputs/systems/personal-training.md`
- `context/roadmap.md`
- `CLAUDE.md`

---

### Step 14: Run the Four-Week Shadow Evaluation

Measure whether the system is safe enough to support Admin-approved top-ups.

**Actions:**

- Review at least four weekly full audits.
- Include at least 10 to 20 active PT clients and all available pattern types.
- Have Admin Eve mark each non-healthy finding as Correct, Incorrect or Needs Context.
- Calculate precision for:
  - Canonical pattern.
  - Frequency.
  - Booked-through date.
  - Missing occurrence detection.
  - Hold treatment.
  - Cancellation boundary.
- Record every false positive and false negative.
- Adjust deterministic rules and rerun fixtures.
- Do not add GHL write access during this phase.

**Files affected:**

- `pt_booking_shadow/state_store.py`
- `pt_booking_shadow/README.md`
- `context/roadmap.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `context/roadmap.md`
- `outputs/systems/personal-training.md`
- `outputs/systems/membership-hold.md`
- `outputs/systems/cancellation-system.md`
- `outputs/systems/ghl-backend-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `plans/2026-04-27-natural-language-appointment-rescheduler.md`
- `plans/2026-07-23-pt-block-tracking-rebooking-repair.md`

### Updates Needed for Consistency

- The personal-training system must distinguish the live Week 10 reminder from the new read-only continuity auditor.
- The roadmap must treat Shadow Pilot Live and Write-Enabled Controller as separate milestones.
- Any GHL webhook workflow or app subscription must be registered with owner, trigger and purpose.
- CLAUDE.md should list the service only after the directory and deployment exist.
- The natural-language appointment plan should reuse the shadow cohort, registry, inference and reconciler rather than recreate them.

### Impact on Existing Workflows

- No existing workflow is unpublished, archived or functionally changed during the weekly shadow MVP.
- `PT: Block Tracking & 13-Week Rebooking` remains the live Admin Eve fallback.
- Dedicated event-trigger workflows may be added later, but they will only send data to the shadow service.
- The hold and cancellation systems remain authoritative for operational status and final access dates.
- No GHL appointment, contact, opportunity, task, tag or message is modified by shadow mode.

### External Dependencies

- HighLevel Calendar and Appointment read APIs.
- HighLevel Contacts, Opportunities, Users and Calendars read APIs.
- HighLevel appointment and contact-change webhooks or dedicated outbound-webhook workflows.
- Railway web service with a persistent volume.
- Resend API for Admin Eve email delivery.
- Existing GHL private integration token and location ID.

Official API references:

- `https://marketplace.gohighlevel.com/docs/ghl/calendars/calendar-events/`
- `https://marketplace.gohighlevel.com/docs/ghl/calendars/get-calendars/`
- `https://marketplace.gohighlevel.com/docs/category/webhook/`

---

## Validation Checklist

- [ ] Service refuses to start unless `SHADOW_MODE=true`.
- [ ] GHL client contains no appointment, contact, opportunity, task, tag or message write methods.
- [ ] All 15 current PT calendars resolve to the correct trainer and duration.
- [ ] Active cohort includes PT-tagged and PT-stage contacts without duplicates.
- [ ] Former PT, PT hold, membership hold and PT cancellation states resolve correctly.
- [ ] PT Only frequency ambiguity is reported rather than guessed.
- [ ] A stable recurring series produces the correct canonical weekly pattern.
- [ ] One-off reschedules and cover sessions do not redefine the pattern.
- [ ] Thirteen future occurrences are generated per weekly slot.
- [ ] Missing internal appointments and end-of-series top-ups are distinguished.
- [ ] Delayed recurring expansion does not produce duplicate or premature findings.
- [ ] PT holds pause recommendations and produce no deletion recommendation.
- [ ] PT cancellation stops top-ups.
- [ ] Only appointments after Final Access Date are marked for hypothetical removal.
- [ ] Missing Final Access Date produces an immediate exception and no inferred boundary.
- [ ] Weekly report is delivered to Admin Eve with CSV evidence and direct GHL links.
- [ ] Every report states that no GHL appointments were changed.
- [ ] Event webhooks are authenticated, deduplicated and debounced.
- [ ] API failures create technical findings instead of operational guesses.
- [ ] Anika/Kanika fixture passes without gaps or duplicates.
- [ ] Four weekly audits are reviewed before write access is considered.
- [x] Roadmap, PT documentation, backend register and CLAUDE.md are updated after deployment.

## Deployment Record

The shadow pilot was deployed to Railway on 23 July 2026 at `https://pt-booking-shadow-production.up.railway.app`. Production is locked to `SHADOW_MODE=true`, the weekly scheduler is enabled for Monday at 5:30 am Australia/Brisbane, reports are enabled for Admin Eve and SQLite history is mounted at `/data/pt_booking_shadow.db`.

The production health endpoint and an authenticated no-email audit were verified after the persistent volume was attached. The first full audit read 107 contacts and produced findings only: 45 former PT contacts, 14 with no future bookings, 14 requiring pattern confirmation, 12 hypothetical top-ups, 8 active holds, 6 internal series gaps, 5 cancellations missing a final access date and 3 healthy records.

No GHL appointment, contact, opportunity, task, tag or message was changed. The optional GHL event-trigger workflows remain deferred; the weekly production reconciliation is the live pilot.

### First owner-review findings

The first owner review is recorded in `outputs/systems/pt-booking-shadow-review-log.md`. It demonstrated that GHL appointment evidence alone cannot distinguish all active recurring PT, included Fast Track PT, prepaid pack expiry, rush holds, retained cancellations and intentional downgrades.

### Reschedule and make-up upgrade: 23 July 2026

The reconciler now counts any valid PT appointment of the correct duration in
the same ISO week as coverage for that week's entitlement. After all canonical
appointments in the following week are protected, one unmatched surplus
appointment may cover one deficit from the immediately preceding week.

The carry-over is deliberately limited to one week. An extra appointment more
than one week later cannot hide an earlier gap, and unexplained surplus
appointments remain visible as evidence without producing an automatic removal
recommendation.

Status-sensitive hold and cancellation contacts are hydrated from their full
GHL contact records before reconciliation. This closed the observed case where
the bulk contact list supplied Cathy James's cancellation state but omitted her
new final-access date.

Twenty-seven regression tests pass. A private no-email audit confirmed Jody
Burke as healthy with one adjacent-week make-up and Cathy James as
`PT_NOTICE_ACTIVE` with final access on 24 July. The upgrade was deployed to
Railway from commit `629d93a`; the production health endpoint returned healthy
with shadow mode and the weekly scheduler enabled.

Add a read-only Brown & Casserly workbook adapter before the first report is treated as an operational action list. Match by normalised email first and phone second. Use `Active SGPT`, `Active PT`, `PT Cancellations` and `SGPT Cancellations` as secondary evidence only because the workbook also contains stale trainer assignments, legacy membership naming, missing active records and at least one debit-versus-pack contradiction.

The next implementation pass must add pattern-boundary, incomplete-hold, pack-end, reversed-cancellation, confirmed-PT-end and cancelled-with-no-future classifications. It must also apply same-week replacement logic before proposing recurring series and show source conflicts rather than silently choosing a value.

---

## Success Criteria

The shadow implementation is complete when:

1. A Monday audit reliably reconciles the complete active PT cohort and sends Admin Eve an exception-led report.
2. Relevant appointment, PT hold and PT cancellation changes can trigger a debounced targeted recheck.
3. Every recommendation includes the source evidence, canonical pattern, confidence, booked-through date and exact hypothetical action.
4. The service has no capability to mutate GHL.
5. Hold and cancellation rules match the documented live systems.
6. At least four weekly audits covering 10 to 20 active PT clients have been reviewed.
7. Canonical pattern, booked-through date and missing-occurrence recommendations achieve at least 95% Admin-confirmed accuracy, with zero incorrect cancellation-removal boundaries.
8. No member, trainer or Admin receives duplicate or unnecessary operational messaging.
9. The existing Week 10 workflow remains available until a separately approved write-enabled phase replaces it.

---

## Graduation Gate for Admin-Approved Top-Ups

Write access must not be added merely because the service is technically functioning.

The next phase can be scoped only when:

- Four weekly audits are complete.
- The 95% accuracy threshold is met.
- No incorrect cancellation deletion boundary has occurred.
- All pattern ambiguities have a defined Admin Eve resolution process.
- GHL recurring expansion and event polling have behaved consistently.
- Admin Eve confirms the report is usable and not noisy.
- A separate approval and rollback design exists for every proposed appointment creation.

The first write-enabled phase should remain Admin-approved. Fully automatic top-ups require a further measured pilot.

---

## Notes

- The shadow auditor is not the future natural-language bot itself. It is the structured state, inference and verification layer that the bot can later call.
- A future write-enabled controller should create and verify replacements before deleting anything.
- Cancellation remains the only normal removal pathway. Trainer departures and transfers are separately authorised operational changes, not client cancellations.
- The current 13-week GHL workflow contains a Week 13 email whose body still refers to Week 10. That copy defect can be corrected independently and does not block shadow implementation.
