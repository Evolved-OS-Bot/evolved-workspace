# Plan: PT Hold Appointment Clearance Controller

**Created:** 2026-08-24
**Status:** Current Billing OS candidate verified locally; dark deployment pending
**Request:** Automatically remove unpaid PT appointments scheduled during an approved hold while retaining late-cancellation evidence and a durable audit trail.

---

## Overview

### What This Plan Accomplishes

Extend the existing Hold OS and Railway billing service with a PT appointment-clearance controller. For approved PT holds whose billing pause is confirmed successful, it will delete eligible appointments more than 24 hours away, retain appointments inside the 24-hour forfeiture window as cancelled, and record every decision in a durable GHL contact note.

### Why This Matters

Members should not occupy trainer capacity for sessions that are not paid during an approved hold. The controller keeps live calendars clean while preserving evidence for late cancellations, exceptions, and every destructive action.

---

## Current State

### Relevant Existing Structure

- `stripe_handler/app.py` hosts the live Railway endpoints for hold intake, Stripe pauses, and cancellations.
- `stripe_handler/test_app.py` provides mocked unit and endpoint tests.
- `outputs/systems/membership-hold.md` documents Hold OS, PT hold forms, fields, workflows, dates, and the Railway service.
- PT hold dates are stored in `HS: Hold Start Date` and `HS: Hold End Date`; billing pause/resume dates are deliberately seven days earlier.
- Standard PT holds are automatically approved and extended PT holds require manager approval.

### Gaps or Problems Being Addressed

- The hold workflows pause billing but do not clear PT appointments.
- Unpaid appointments remain on live trainer calendars.
- Hard deletion removes the calendar record, so the system needs to write a durable audit record before/after each action.
- Repeated workflow calls and late-created appointments need safe reconciliation.

---

## Proposed Changes

### Summary of Changes

- Add a PT hold clearance endpoint to the existing Railway Flask app.
- Query an explicit allowlist of approved PT calendars over the actual hold interval.
- Filter by exact GHL contact ID and actionable appointment status.
- Delete appointments more than 24 hours away.
- Retain appointments within 24 hours by setting status to `cancelled`.
- Fail closed for ambiguous recurring events, missing fields, unapproved holds, unknown calendars, or API failures.
- Create a structured GHL contact note summarising deleted, retained, skipped, and failed events.
- Make the operation idempotent and safe to run at approval, hold start, and during reconciliation.
- Document the required GHL workflow webhooks and environment variables.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| None | The controller belongs in the existing Railway service and test suite. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `stripe_handler/app.py` | Add calendar querying, eligibility rules, delete/cancel actions, audit notes, validation, endpoint, and health configuration visibility. |
| `stripe_handler/test_app.py` | Add unit and endpoint coverage for boundaries, allowlists, contact matching, recurrence, idempotency, audit notes, and partial failures. |
| `outputs/systems/membership-hold.md` | Document the clearance controller, decision rules, workflow integration, configuration, audit model, and operating procedure. |
| `CLAUDE.md` | Add the new Railway controller to the documented scripts/services when implementation is complete. |

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Use actual hold dates:** Appointment clearance uses `[Hold Start Date, Hold End Date)` in Australia/Brisbane. It never uses Pre-Hold-Start or Pre-Return billing dates.
2. **Hard-delete advance unpaid sessions:** Eligible appointments starting more than 24 hours from execution are deleted from GHL.
3. **Retain late cancellations:** Eligible appointments at or inside 24 hours are updated to `cancelled`, preserving forfeiture evidence.
4. **Exact contact and calendar matching:** The controller requires an exact `contactId` and an environment-configured PT calendar allowlist.
5. **Durable audit in GHL:** Each run writes one structured contact note with event IDs, dates, trainer/user IDs, calendar IDs, action, reason, and timestamp.
6. **Fail closed on recurrence ambiguity:** Recurring events are not mutated until instance-only deletion behaviour is proven; they are reported for review.
7. **Idempotent reconciliation:** Missing/already-deleted events are not treated as failures, and repeated runs only act on remaining eligible events.
8. **No duplicate tracker:** Results remain attached to the existing contact/Hold OS record.

### Alternatives Considered

- Keeping all appointments as `cancelled` was rejected because it leaves unpaid advance sessions cluttering the calendar.
- Relying on HighLevel native audit logs was rejected because retention is limited and individual deleted appointments are not recoverable.
- A separate database or task tracker was rejected because GHL contact notes provide a durable member-level audit without creating another work queue.

### Open Questions (if any)

- Production PT calendar IDs were confirmed read-only against live GHL on 2026-08-24; 15 active calendars are documented.
- Confirm the GHL user ID that should author automated audit notes, or use the existing Admin Eve ID fallback.

---

## Step-by-Step Tasks

### Step 1: Add Configuration and Validation

**Actions:**

- Add `GHL_PT_CALENDAR_IDS` and `GHL_AUTOMATION_USER_ID` environment configuration.
- Validate contact ID, hold type, hold dates, approved status, and calendar configuration.
- Treat Hold End Date as the return date and therefore an exclusive boundary.

**Files affected:**

- `stripe_handler/app.py`

### Step 2: Build Calendar Discovery and Decision Logic

**Actions:**

- Query HighLevel calendar events for each approved PT calendar over the Brisbane hold interval.
- Normalise event fields and filter by exact contact ID.
- Ignore already-cancelled, completed, invalid, past, blocked, or unrelated events.
- Classify eligible events as `delete`, `retain_cancelled`, or `manual_review`.

**Files affected:**

- `stripe_handler/app.py`

### Step 3: Execute Mutations Safely

**Actions:**

- Delete advance eligible events through `DELETE /calendars/events/:eventId`.
- Update inside-24-hour events to `appointmentStatus=cancelled` without triggering unrelated automations.
- Stop remaining mutations after an unexpected API failure and report the partial result.

**Files affected:**

- `stripe_handler/app.py`

### Step 4: Persist the Audit Trail

**Actions:**

- Create one GHL contact note after each run containing the hold interval, threshold, each appointment snapshot, action, reason, success/failure, and run key.
- Keep application logs structured enough for Railway operational review.
- Return a machine-readable response for GHL workflow branching.

**Files affected:**

- `stripe_handler/app.py`

### Step 5: Add Endpoint and Tests

**Actions:**

- Add `POST /ghl/pt-hold-clearance`.
- Test valid deletion, 24-hour retention, exact boundaries, wrong contact, non-PT calendars, cancelled events, recurring events, duplicate runs, empty results, and partial failure.
- Run the complete existing Stripe handler test suite.

**Files affected:**

- `stripe_handler/app.py`
- `stripe_handler/test_app.py`

### Step 6: Document GHL Workflow Integration

**Actions:**

- Add an optional Preview call after standard PT approval and extended PT manager approval.
- Add the destructive Apply call only after Billing OS confirms the Stripe or manually reconciled PT Minder pause succeeded.
- Add a second Apply call on Hold Start Date and a daily reconciliation path during active PT holds.
- Document exact payload, success/exception branches, required scopes, environment variables, and rollout procedure.
- Update the workspace service summary.

**Files affected:**

- `outputs/systems/membership-hold.md`
- `CLAUDE.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-04-13-hold-return-journey-workflow.md`
- `scripts/create_hold_date_fields.py`
- `context/policies.md`
- `stripe_handler/railway.toml`
- `stripe_handler/requirements.txt`

### Updates Needed for Consistency

- The Hold OS documentation must no longer describe appointment clearance as manual or absent.
- Workflow documentation must distinguish actual hold dates from shifted billing dates.
- Production configuration must use IDs from the live approved PT calendars only.

### Impact on Existing Workflows

The change does not alter Stripe pause calculations, membership holds, ownership, tags, pipelines, billing schedules, or return communications. It adds a PT-only clearance webhook after approval and reconciliation triggers.

---

## Validation Checklist

- [x] Existing Stripe handler tests still pass.
- [x] Advance unpaid PT appointments are deleted.
- [x] Appointments inside 24 hours remain with status `cancelled`.
- [x] Hold end/return-day appointments are not touched.
- [x] Only exact contact IDs and approved calendar IDs are acted on.
- [x] SGPT and assessment appointments are untouched by the allowlist.
- [x] Recurring ambiguity fails closed.
- [x] Every destructive/review run creates or updates one complete contact audit note.
- [x] Repeated calls with nothing remaining are idempotent and create no note clutter.
- [x] Documentation contains deployment, configuration and workflow instructions.
- [x] Read-only live dry run against Ankitha's PT hold returned no remaining events after her manual clearance.
- [ ] Deploy the Railway code and configure the three production variables.
- [ ] Run a controlled test appointment through Preview and Apply.
- [ ] Publish the GHL workflow calls after the controlled test succeeds.

---

## Success Criteria

1. A valid approved PT hold with a confirmed successful billing pause clears every eligible unpaid PT appointment in its actual hold interval without touching anything else.
2. The live calendar remains clean while late-cancellation evidence and deletion history remain accessible on the contact.
3. Exceptions stop safely and produce enough detail for a human to reconcile without reconstructing the event.

---

## Notes

The controller should initially be deployed with a test contact and a narrow calendar allowlist. Live workflow publication should follow a successful dry run and one controlled destructive test appointment.

### 24 August integration update

- The controller was reconciled onto commit `daec8b6`, the current guarded Billing OS candidate containing the newer PT entitlement-reconciliation boundary. The obsolete handler base was not deployed.
- The current Billing OS suite passes 66 tests and the separate PT entitlement suite passes 18 tests: 84 tests in total.
- `python3 -m py_compile`, `git diff --check`, and the agent-instruction drift check pass.
- Peter approved the dedicated GHL test contact name `Evolved Automated Tests` for the silent acceptance run.
- Member workflow calls remain unpublished. Production activation is still gated on dark deployment, exact environment read-back, one controlled Preview/Apply test, and verification of the deleted appointment plus durable GHL note.
