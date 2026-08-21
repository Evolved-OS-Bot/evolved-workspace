# Plan: GHL Conversation Clearance Controller

**Created:** 2026-07-31
**Status:** Draft
**Request:** Transform the passive GHL conversation triage report into an accountable inbox-clearance system for Admin Eve.

---

## Overview

### What This Plan Accomplishes

This plan replaces the current twice-daily unread-conversation report with a governed Conversation Clearance Controller. GHL remains the authoritative communication record, while the Railway/Postgres operating-data hub persists each conversation case, its owner, service standard, evidence, deadline, escalation and final disposition.

The change is deliberately staged. It first repairs unsafe false-success behaviour, then establishes read-only case tracking and shadow performance measurement, then adds controlled assignment and overdue-task writes, and only later introduces policy-aware draft replies after clearance accountability is proven.

### Why This Matters

Unread messages are member-service, reputation, retention and revenue risks. A report that tells Admin what is waiting but cannot prove what was handled permits backlog growth, repeated carryover and false reassurance.

The controller reduces owner dependence by making the operating standard observable and enforceable without requiring Peter to manually inspect GHL or chase a separate end-of-day report. It also creates the governed evidence needed to decide whether the problem is workload, unclear ownership, insufficient service standards, absence cover, or execution.

---

## Current State

### Relevant Existing Structure

- `triage_bot/triage.py`
  - Railway cron currently runs at 06:00 and 18:00 Brisbane time.
  - Searches GHL for conversations with `status=unread`.
  - Fetches up to 50 conversations without pagination.
  - Fetches recent messages and contact tags.
  - Uses an AI model to classify each conversation into an importance/urgency matrix.
  - Sends a Discord report and Admin email.
  - Publishes aggregate unread and category counts to the hub.
- `triage_bot/railway.toml`
  - Owns the current twice-daily Railway schedule.
- `reporting_control/report_registry.json`
  - Registers `conversation-triage` as an ephemeral twice-daily report owned by Admin Eve.
- `operating_data_hub/app.py`, `operating_data_hub/contracts.py`, `operating_data_hub/store.py` and `operating_data_hub/service.py`
  - Provide the current protected Railway/Postgres ingestion, source-snapshot, exception and dashboard patterns.
  - Currently retain only aggregate Conversation Triage snapshots.
- `operating_data_hub/sa_attendance.py`, `operating_data_hub/sa_attendance_followup.py` and `operating_data_hub/onboarding_followup.py`
  - Provide established patterns for write gates, deduplicated GHL tasks, staged escalation, task adoption and automatic closure.
- `outputs/systems/reporting-control-plane.md`
  - Governs the hub-first architecture and already names `conversation_cases` as a canonical operational entity.
  - States that GHL remains the communication record and model classification remains a recommendation.
- `outputs/systems/inbound-communications.md`
  - Records that three of five unread conversations were unassigned during the 22 July audit.
  - Records that GHL SLA settings were disabled and no breach history was available.
- `outputs/systems/drive-process-audit.md`
  - Rejects the historical S.O.D/E.O.D and Admin Task Tracker as systems of record.
  - Calls for an exception-led Admin Eve queue with service-risk rules and recorded actions inside GHL.
- `plans/2026-07-27-evolved-reporting-control-plane.md`
  - Phase 7 requires pagination, persisted classification, recommended action, owner, due date and disposition.
- `plans/2026-04-25-level-1-admin-bot.md`
  - Draft plan for generating replies and approving them in Discord.
  - Solves reply composition but does not establish clearance ownership, service standards, stale-draft protection or durable outcome evidence.
- `context/roadmap.md`
  - Separately tracks inbox ownership, Admin reporting and the Level 1 Admin Bot.

The current HighLevel API documentation confirms supported endpoints for searching conversations, getting messages, getting and updating conversations, and sending messages. Exact update fields, pagination behaviour and installed-token scopes must still be verified through a read-only capability probe against the live sub-account before enabling any write.

### Gaps or Problems Being Addressed

- A failed GHL conversation search currently returns an empty list. The bot can therefore publish a green “No unread conversations” result when the source failed.
- A failed AI response parse currently defaults every affected conversation to `Not Important Not Urgent`.
- The search stops at 50 records and does not prove extraction completeness.
- The current output is ephemeral. It does not preserve conversation-level state or carryover between runs.
- The controller cannot distinguish new, carried-over, reopened, handled, overdue, blocked or disposed conversations.
- It does not record first-seen time, latest inbound message ID, latest outbound response, assigned owner, deadline, breach, escalation or closure reason.
- “Unread” is a presentation flag rather than proof that the underlying member request was resolved.
- The importance/urgency labels can wrongly devalue marketing, sales, equipment, service and reputation enquiries.
- Contact tags are used as lifecycle truth even though the hub now has a governed canonical lifecycle model.
- Reports do not include a durable action link or a controlled case identifier.
- The 06:00 and 18:00 cadence cannot catch an in-day breach before the business day closes.
- Admin receives the report but there is no automatic escalation when it is not acted on.
- The older AI draft plan can create a second operational inbox in Discord and deletes approval messages, weakening the audit trail.

---

## Proposed Changes

### Summary of Changes

- Repair source-failure and classification-failure handling before expanding functionality.
- Paginate GHL conversation extraction and record extraction completeness.
- Replace the importance/urgency matrix with operational service-risk categories.
- Introduce a versioned conversation-case contract in the operating-data hub.
- Persist case observations and append-only case events in protected PostgreSQL.
- Link GHL contact IDs to canonical hub people without exposing identified content on executive surfaces.
- Determine case resolution from message evidence or an approved disposition, not from the unread flag alone.
- Add configurable staffed hours, service standards and absence-cover routing.
- Add protected case-detail and share-safe aggregate clearance endpoints.
- Run a read-only shadow period to baseline arrival volume, case mix, response time, carryover and backlog.
- Add separately gated GHL conversation-assignment and task/escalation writers only after shadow acceptance.
- Convert the Admin report into an exception-led work queue with direct GHL links.
- Add owner escalation only for breached or blocked cases.
- Add policy-aware drafts after control quality is proven, with human approval, stale-draft revalidation and retained audit evidence.
- Retire the legacy aggregate-only delivery after two accepted parity cycles.
- Supersede the old Level 1 Admin Bot plan rather than building a separate Discord inbox.

### New Files to Create

| File Path | Purpose |
| ----------------- | ---------------------------------- |
| `operating_data_hub/conversation_clearance.py` | Versioned case, service-risk, deadline, resolution, reopening and escalation logic with no direct I/O. |
| `operating_data_hub/ghl_conversations.py` | GHL conversation and message client with pagination, capability probing, timeouts, retries and independent read/write gates. |
| `operating_data_hub/tests/test_conversation_clearance.py` | Unit coverage for classification fallback, deadlines, resolution evidence, dispositions, reopening and escalation. |
| `operating_data_hub/tests/test_ghl_conversations.py` | Client-contract coverage for pagination, source errors, incomplete pages, timestamps and gated writes. |
| `outputs/systems/conversation-clearance-control.md` | Canonical architecture, operating model, service standards, runbook, evidence model and deployment history. |
| `outputs/reporting-control-plane/conversation-clearance-shadow-review.md` | Owner review log for shadow cases, false classifications, false closures, carryover and escalation proposals. |

### Files to Modify

| File Path | Changes |
| ----------------- | ---------------------------- |
| `triage_bot/triage.py` | Add fail-closed source handling, pagination, explicit incomplete status, safer classification fallback and compatibility publishing during migration. |
| `triage_bot/railway.toml` | Retain the approved Railway schedule during shadow; change cadence only after the hub controller schedule is accepted. |
| `operating_data_hub/contracts.py` | Add strict versioned conversation observation, case-event, disposition and aggregate contracts. |
| `operating_data_hub/store.py` | Add protected conversation case, case event and delivery/escalation persistence with idempotent upserts and append-only history. |
| `operating_data_hub/service.py` | Add collection, reconciliation, shadow evaluation, aggregate reporting and gated execution services. |
| `operating_data_hub/app.py` | Add protected ingest, case-detail, aggregate, preview, health and separately gated action endpoints. |
| `operating_data_hub/config.py` | Add service-standard, staffed-hours, owner, cover-owner, source-freshness and independent write-gate configuration. |
| `operating_data_hub/tests/test_contracts_and_store.py` | Validate schema, idempotency, reopen behaviour, protected content and immutable event history. |
| `operating_data_hub/tests/test_app.py` | Validate authentication, redaction, write gates, failure states and aggregate/detail separation. |
| `reporting_control/report_registry.json` | Replace the aggregate-only report definition with the governed controller, owner, freshness, schedule, protected outputs, share-safe outputs and retirement path. |
| `reporting_control/tests/test_contracts.py` | Validate the updated registry contract. |
| `outputs/systems/reporting-control-plane.md` | Record authority, entity, ingestion, privacy, failure, delivery and legacy-retirement decisions. |
| `outputs/systems/inbound-communications.md` | Replace proposed written-inbox governance with the accepted controller design while preserving the separate missed-call gap. |
| `outputs/systems/drive-process-audit.md` | Point the written-inbox portion of the Admin reporting replacement to the controller. |
| `outputs/systems/ghl-workflow-owner-review-register.md` | Record Admin Eve as written-inbox owner, the absence-cover rule and review cadence once approved. |
| `outputs/systems/ghl-team-task-trigger-register.md` | Register deduplicated breach tasks and their automatic-closure evidence once the writer is enabled. |
| `plans/2026-04-25-level-1-admin-bot.md` | Mark as superseded and point draft-reply work to the controlled later phase of this plan. |
| `plans/2026-07-27-evolved-reporting-control-plane.md` | Record this plan as the implementation path for Phase 7. |
| `context/roadmap.md` | Promote the controller to In Progress, narrow the remaining missed-call work and reconcile overlapping Admin Bot/reporting items. |
| `CLAUDE.md` | Document the controller only after new production functionality is live; avoid adding implementation lookup detail. |

### Files to Delete (if any)

No file is deleted during the migration. The old Level 1 Admin Bot plan is retained as historical design context and marked superseded.

The legacy triage delivery code is removed only after the replacement has completed two accepted parity cycles and its retirement evidence is recorded.

---

## Design Decisions

### Key Decisions Made

1. **GHL is authoritative for communication evidence**: Message direction, timestamps, delivery state, conversation identity and current assignment come from GHL. The controller must never invent a reply or infer that a member request was completed from a dashboard flag.

2. **The hub is authoritative for clearance-control state**: PostgreSQL holds first-seen time, deadline, case state, classification version, escalation and disposition because the current GHL inbox does not provide the required historical SLA evidence.

3. **One case represents one unresolved inbound cycle**: The case key combines the GHL conversation ID and the latest inbound message that opened or reopened work. A new inbound message after a resolved case creates a new cycle or explicitly reopens the case without overwriting history.

4. **Unread is a signal, not a completion test**: A case closes only when a later outbound response is verified, an approved no-response disposition is recorded, or a linked owned operational task is accepted for work that cannot be completed in the conversation.

5. **No automatic mark-read action**: The controller measures and routes work. It does not hide work by changing read status.

6. **Operational categories replace subjective importance labels**: Initial categories are `immediate_service_risk`, `revenue_sensitive`, `member_administration`, `routine_response`, `no_response_required` and `manual_review`.

7. **Deterministic overrides outrank model recommendations**: Known cancellation intent, complaint language, imminent appointment changes, active Strength Assessment replies, billing/access problems and classification failures route through deterministic guards. AI may summarise and recommend but cannot downgrade a protected case.

8. **Source and model failures fail closed**: A GHL failure produces `source_failed`, never inbox clear. An incomplete extraction produces `incomplete`. A model failure produces `manual_review`, never a low-priority classification.

9. **Identified message content remains protected**: Names, message bodies, contact IDs and direct GHL links are available only through authenticated operational views and Admin delivery. The CEO dashboard and share-safe brief receive aggregate counts and service-level measures only.

10. **Writes are independently gated**: Conversation assignment, task creation, task completion and message sending each require separate production configuration and acceptance. Enabling one does not implicitly enable another.

11. **The first production write is accountability, not AI messaging**: Deduplicated assignment and overdue tasks come before draft replies. This solves the observed operating failure before optimising typing speed.

12. **Draft approval must be stale-safe and auditable**: Immediately before send, the controller re-fetches the conversation and rejects the draft if a newer inbound or staff outbound message exists. Approval, edited text, approver, send result and GHL message ID remain recorded.

13. **Railway is the only scheduler**: No local or Codex schedule is introduced. The existing triage cron remains compatibility delivery until the hub-controlled schedule passes parity.

14. **Notifications are exception-led and deduplicated**: Admin receives a work queue and threshold reminders. Peter or the cover owner sees only breached, unsafe, blocked or repeatedly carried-over cases.

15. **The written inbox and phone routing remain separate acceptance surfaces**: This plan closes written GHL Conversations. The hard-coded call router and final missed-call handoff remain in the inbound-call workstream.

### Alternatives Considered

- **Keep improving the email report**: Rejected because a richer email still cannot prove ownership, response, disposition or carryover.
- **Create a GHL task for every unread message immediately**: Rejected because it duplicates the inbox, creates task noise and can make a large backlog harder to operate. Tasks are reserved for breaches, delegated operational work and explicit exceptions.
- **Use GHL unread status as the KPI**: Rejected because messages can be read without being resolved and may be handled without the unread flag changing predictably.
- **Build the April Discord draft bot first**: Rejected because it optimises composition without fixing accountability and creates a second queue outside GHL.
- **Make Discord the case system**: Rejected because Discord is a delivery and approval surface, not the communication system of record.
- **Enable automatic replies immediately**: Rejected because current classification quality, channel-specific send requirements and policy coverage have not passed acceptance.
- **Turn on GHL SLA settings alone**: Rejected as the complete solution because the current audit found them disabled and their historical evidence, dispositions, canonical lifecycle linkage and cross-system exceptions are insufficient for the governed control model. They may later complement the controller.
- **Create an independent database in the triage service**: Rejected by the hub-first workspace rule.

### Open Questions (if any)

These questions do not block the fail-safe repair or read-only shadow build:

1. What are Admin Eve's staffed written-inbox hours on each day of the week?
2. Who is the named absence and escalation cover when Admin Eve is unavailable?
3. What production service standards should be approved after the shadow baseline?
   - Recommended starting proposal: immediate service risk acknowledged within 30 minutes and owned within 60 minutes during staffed hours; revenue-sensitive and member-administration cases handled within four staffed hours; routine cases by the end of the next staffed block.
4. Should Peter receive each final breach individually, or one deduplicated exception digest at a fixed time?

Until these are confirmed, shadow measurement uses clearly labelled proposed standards and creates no production escalation.

---

## Step-by-Step Tasks

Execute these tasks in order during implementation.

### Step 1: Freeze the Current Contract and Add Failure Regression Tests

Capture the present report output and hub aggregate payload as compatibility fixtures before changing behaviour.

**Actions:**

- Add tests proving current successful GHL extraction and output formatting.
- Add failing regression cases for GHL timeout, non-2xx response, malformed JSON, more than 50 unread conversations and AI parse failure.
- Assert that source failure cannot produce `No unread conversations`, a green Discord message or a complete zero-count hub observation.
- Assert that classification failure cannot produce `no_response_required` or the legacy lowest-priority category.
- Record the current schema and delivery destinations as the compatibility baseline.

**Files affected:**

- `triage_bot/triage.py`
- `triage_bot/tests/test_triage.py` or the repository's accepted triage test location
- `outputs/systems/conversation-clearance-control.md`

---

### Step 2: Repair Fail-Closed Extraction and Classification

Make the current service trustworthy before adding persistent state.

**Actions:**

- Replace empty-list error handling with a typed extraction result containing `complete`, `status`, `records`, `pages`, `error_code` and `observed_at`.
- Add bounded request timeouts and retry behaviour for transient GHL failures.
- Implement supported conversation pagination and detect repeated or missing cursors.
- Preserve message and conversation IDs required for evidence and idempotency.
- Publish `source_failed` or `incomplete` to the hub without overwriting the latest complete case state.
- Send an explicit operational failure alert to the existing destinations.
- Change AI failure fallback to `manual_review`.
- Add deterministic protected-category overrides before and after model classification.
- Remove `Not Important` terminology from new outputs while retaining compatibility mapping during migration.

**Files affected:**

- `triage_bot/triage.py`
- `triage_bot/tests/test_triage.py`
- `operating_data_hub/contracts.py`
- `operating_data_hub/tests/test_app.py`

---

### Step 3: Define the Canonical Conversation Case Contract

Create the pure, versioned domain model before persistence or writes.

**Actions:**

- Define `conversation_observation_v1` with source run, conversation ID, contact ID, canonical person link when available, latest inbound and outbound message IDs/timestamps, channel, current assignment, unread signal, extraction completeness and minimal protected evidence.
- Define `conversation_case_v1` with case ID, cycle key, opened/reopened time, category, recommendation, owner, deadline, state, breach and classification provenance.
- Define append-only case events: observed, classified, assigned, acknowledged, replied, operationally delegated, disposed, breached, escalated, resolved and reopened.
- Define approved dispositions with required reasons:
  - `responded`;
  - `spam_or_solicitation`;
  - `duplicate_or_system_message`;
  - `no_response_required_approved`;
  - `delegated_to_owned_task`;
  - `blocked_and_escalated`.
- Prevent `marked_read` from being a disposition.
- Define resolution precedence and reopening behaviour.
- Define Brisbane staffed-time deadline calculations as configuration, including weekends, after-hours and missing-cover failure.
- Add schema-version and classification-version fields.

**Files affected:**

- `operating_data_hub/conversation_clearance.py`
- `operating_data_hub/contracts.py`
- `operating_data_hub/tests/test_conversation_clearance.py`

---

### Step 4: Add Protected Hub Persistence

Persist exact cases and immutable evidence without exposing member content to aggregate surfaces.

**Actions:**

- Add `hub_conversation_cases` keyed by case ID and unique cycle key.
- Add `hub_conversation_case_events` with an idempotency key and immutable payload fingerprint.
- Add a small disposition/approval table only if approvals cannot be expressed safely as events.
- Store message IDs, timestamps, state and minimal excerpts needed for Admin action; do not duplicate full conversation history unnecessarily.
- Link GHL contact identity through `hub_source_identities` and canonical people when exact linkage exists.
- Retain unmatched GHL contact IDs as explicit identity exceptions rather than matching by name.
- Implement idempotent observation upserts and append-only event inserts.
- Prevent older observations from overwriting newer case state.
- Add tests for same-run replay, out-of-order events, reopened cases, conflicting classifications and concurrent reconciliation.

**Files affected:**

- `operating_data_hub/store.py`
- `operating_data_hub/contracts.py`
- `operating_data_hub/tests/test_contracts_and_store.py`

---

### Step 5: Build the Read-Only GHL Conversation Adapter

Move governed extraction into the hub path without cutting over the existing report.

**Actions:**

- Implement search, get-conversation and get-messages methods using the live supported API version.
- Perform a read-only capability probe for pagination fields, assignment fields, timestamps, channel values and token scopes.
- Normalise timestamps to UTC while retaining Brisbane calculations at the domain boundary.
- Validate page completeness, record uniqueness and message ordering.
- Fetch enough history to prove the latest unresolved inbound cycle without retaining unrelated history.
- Return typed source failures and rate-limit state.
- Add a dry-run probe for update-conversation fields without sending a mutating request if the API cannot expose a capability schema.
- Record any unsupported assignment or deep-link behaviour as a deployment limitation.

**Files affected:**

- `operating_data_hub/ghl_conversations.py`
- `operating_data_hub/tests/test_ghl_conversations.py`
- `operating_data_hub/config.py`
- `outputs/systems/conversation-clearance-control.md`

---

### Step 6: Reconcile Cases and Determine Evidence-Based Outcomes

Turn source observations into durable operational state.

**Actions:**

- Open a new case for a latest inbound message that is not covered by a resolved cycle.
- Preserve the original first-seen time across repeated observations.
- Verify `responded` only when an eligible staff outbound message occurred after the opening inbound.
- Do not treat automated workflow acknowledgements as final human handling unless the case category explicitly allows that outcome.
- Keep workflow-generated messages identifiable from staff messages where GHL evidence supports it; otherwise fail to manual review.
- Allow delegated operational work only when the linked GHL task exists, has an owner and has an appropriate due date.
- Automatically resolve a delegated case when the linked task is completed and any required member communication is present.
- Reopen a case on a later inbound message.
- Record changed classification recommendations without erasing the original.

**Files affected:**

- `operating_data_hub/conversation_clearance.py`
- `operating_data_hub/service.py`
- `operating_data_hub/tests/test_conversation_clearance.py`

---

### Step 7: Add Protected Operational and Share-Safe Views

Expose only the minimum information required by each audience.

**Actions:**

- Add an authenticated case-detail endpoint for Admin and owner review.
- Add an authenticated clearance preview containing direct GHL links when a stable supported link can be verified.
- Add aggregate endpoints for opening backlog, new, handled, within standard, overdue, unresolved at close, carryover, oldest age and rolling five-staffed-day clearance.
- Keep names, contact IDs, excerpts and links out of the CEO report and executive brief.
- Report source failure, incomplete extraction and stale state separately from a zero inbox.
- Add plain-language dashboard labels.

**Files affected:**

- `operating_data_hub/app.py`
- `operating_data_hub/service.py`
- `operating_data_hub/templates/dashboard.html`
- `operating_data_hub/tests/test_app.py`
- `outputs/systems/reporting-control-plane.md`

---

### Step 8: Run a Read-Only Shadow Baseline

Measure the actual operating problem before enabling any assignment or task write.

**Actions:**

- Deploy the case collector with all write gates false.
- Retain the current triage delivery unchanged during the shadow window.
- Run for at least ten staffed days or until at least 50 cases are reviewed, whichever is later.
- Review every proposed immediate-service-risk and manual-review case.
- Review a sample from every other category.
- Measure arrival volume, arrival time, current assignment, time to first staff response, time to final disposition, carryover, reopen rate and oldest unresolved age.
- Compare unread-based counts with evidence-based open cases.
- Identify workflow acknowledgements that must not count as human resolution.
- Record false-positive, false-negative, false-closure and missed-case results in the review log.
- Use the baseline to confirm staffed hours, absence cover and service standards with Peter.

**Files affected:**

- `outputs/reporting-control-plane/conversation-clearance-shadow-review.md`
- `outputs/systems/conversation-clearance-control.md`
- `context/roadmap.md`

---

### Step 9: Convert Delivery into an Exception-Led Admin Work Queue

Replace passive classification with action ordering while remaining read-only.

**Actions:**

- Present cases in deadline order with category, age, recommended action, current owner and direct GHL link.
- Separate new, due soon, overdue, blocked and carried-over sections.
- Remove repeated resolved cases from delivery.
- Include one extraction-health line so source failure cannot be mistaken for no work.
- Add a start-of-staffed-day queue and an end-of-staffed-day exception summary.
- Avoid sending Peter routine queue detail.
- Persist delivery keys so identical reminders are not sent repeatedly.
- Preserve Discord and email as views, not systems of record.

**Files affected:**

- `triage_bot/triage.py`
- `operating_data_hub/service.py`
- `operating_data_hub/store.py`
- `reporting_control/report_registry.json`
- `reporting_control/tests/test_contracts.py`

---

### Step 10: Add Controlled Assignment and Breach Tasks

Enable the smallest useful write layer after shadow acceptance.

**Actions:**

- Confirm the live Admin Eve user ID and approved absence-cover ID.
- Verify the exact GHL update-conversation assignment field through a temporary or already-owned safe test case before production enablement.
- Add a dedicated assignment write gate.
- Assign only unassigned written conversations; do not overwrite an intentional coach or owner assignment without an explicit routing rule.
- Add a separate breach-task write gate.
- Create one deduplicated GHL task for an overdue or blocked case, not for every new conversation.
- Include case key, latest inbound time, required action and protected GHL link in the task.
- Adopt a matching open legacy/manual task when safe rather than duplicating it.
- Auto-complete only controller-created or adopted tasks when the exact case resolves.
- Prove retry deduplication, owner assignment, due date and automatic closure using a controlled temporary-contact or owner-approved test.

**Files affected:**

- `operating_data_hub/ghl_conversations.py`
- `operating_data_hub/conversation_clearance.py`
- `operating_data_hub/service.py`
- `operating_data_hub/config.py`
- `operating_data_hub/tests/test_conversation_clearance.py`
- `outputs/systems/ghl-team-task-trigger-register.md`

---

### Step 11: Add Tiered Escalation

Escalate only when Admin ownership has not produced a timely outcome.

**Actions:**

- Notify Admin Eve at the due-soon threshold.
- Create or retain the persistent GHL task at breach.
- Route absence-period work to the approved cover owner.
- Escalate to Peter only after the approved final threshold or immediately for protected safety/reputation categories.
- Deduplicate escalation by case and threshold version.
- Suppress future reminders after verified resolution.
- Reopen escalation only when a new inbound cycle creates new work.
- Add daily and rolling aggregate performance without ranking staff on unreviewed model output.

**Files affected:**

- `operating_data_hub/conversation_clearance.py`
- `operating_data_hub/service.py`
- `operating_data_hub/store.py`
- `operating_data_hub/config.py`
- `outputs/systems/conversation-clearance-control.md`

---

### Step 12: Add Policy-Aware Draft Replies Behind a Separate Gate

Optimise response production only after the queue is consistently being cleared.

**Actions:**

- Reuse `context/policies.md` and approved response templates as versioned drafting inputs.
- Generate drafts only for allowlisted categories and channels.
- Require human approval for every initial production draft.
- Retain the original draft, edited draft, approver, approval time, policy version and classification version.
- Immediately re-fetch the GHL conversation before send.
- Reject a stale draft if any later inbound or staff outbound message exists.
- Add channel-specific validation for SMS, email, Facebook, Instagram, Google and live chat.
- Enable message sending through an independent gate.
- Record returned GHL conversation/message IDs and delivery result.
- Never delete the approval evidence.
- Consider auto-send only as a future owner-approved phase after a separate reviewed sample and explicit risk assessment.

**Files affected:**

- `operating_data_hub/conversation_clearance.py`
- `operating_data_hub/ghl_conversations.py`
- `operating_data_hub/store.py`
- `operating_data_hub/service.py`
- `context/policies.md`
- `plans/2026-04-25-level-1-admin-bot.md`

---

### Step 13: Complete Parity, Cutover and Legacy Retirement

Cut over only after the new controller proves completeness and delivery reliability.

**Actions:**

- Compare the complete GHL conversation identity set between legacy and new extraction for two accepted cycles.
- Require zero unexplained missing conversations.
- Require zero false inbox-clear results under simulated source failures.
- Require zero duplicate assignments, tasks or escalations.
- Require reviewed protected-category recall and false-closure rates to meet the owner-approved threshold.
- Confirm Admin can operate the queue without Discord becoming a second inbox.
- Change the report registry state to live governed controller.
- Retire aggregate-only triage ingestion and duplicate delivery.
- Preserve historical report evidence and document the retirement date.
- Mark Reporting Control Plane Phase 7 implemented.

**Files affected:**

- `triage_bot/triage.py`
- `triage_bot/railway.toml`
- `reporting_control/report_registry.json`
- `outputs/systems/reporting-control-plane.md`
- `outputs/systems/conversation-clearance-control.md`
- `plans/2026-07-27-evolved-reporting-control-plane.md`

---

### Step 14: Synchronise Workspace Documentation and Close the Workstream

Make the final operating model discoverable without bloating canonical instructions.

**Actions:**

- Update the inbound-communications system record with the accepted written-inbox model and retain the separate missed-call gap.
- Update the Drive process audit to identify the controller as the replacement for conversation portions of S.O.D/E.O.D reporting.
- Update the workflow owner and team-task registers.
- Update `CLAUDE.md` with one concise controller entry if production functionality adds a new enduring workspace surface.
- Update `context/roadmap.md` to Live only after production validation.
- Run `python3 scripts/check_agent_instruction_drift.py` if `CLAUDE.md` or `AGENTS.md` changes.
- Record deployment IDs, controlled test evidence, limitations and next review date.

**Files affected:**

- `outputs/systems/inbound-communications.md`
- `outputs/systems/drive-process-audit.md`
- `outputs/systems/ghl-workflow-owner-review-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `CLAUDE.md`
- `context/roadmap.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `triage_bot/triage.py`
- `triage_bot/railway.toml`
- `reporting_control/report_registry.json`
- `reporting_control/tests/test_contracts.py`
- `operating_data_hub/app.py`
- `operating_data_hub/contracts.py`
- `operating_data_hub/service.py`
- `operating_data_hub/store.py`
- `outputs/systems/reporting-control-plane.md`
- `outputs/systems/inbound-communications.md`
- `outputs/systems/drive-process-audit.md`
- `outputs/systems/ghl-workflow-owner-review-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `plans/2026-04-25-level-1-admin-bot.md`
- `plans/2026-07-27-evolved-reporting-control-plane.md`
- `context/policies.md`
- `context/roadmap.md`
- `CLAUDE.md`

### Updates Needed for Consistency

- Reconcile the written-inbox scope out of the broader inbound call workstream.
- Keep missed calls and phone routing as a separate unresolved operational control.
- Point Reporting Control Plane Phase 7 to this plan.
- Mark the Level 1 Admin Bot draft as superseded.
- Keep the Admin Reporting OS rebuild scoped to Tasks, WARM Sales and remaining non-conversation exceptions after this controller absorbs inbox clearance.
- Register the controller's owner, schedule, freshness, protected output, share-safe output and retirement path.
- Add the final task triggers to the team-task register only after live writes are verified.
- Add any approved staffed hours and absence cover to the canonical system record, not to `CLAUDE.md`.

### Impact on Existing Workflows

- The existing 06:00/18:00 report remains live throughout the shadow phase.
- No conversation is marked read automatically.
- No reply is sent during the first control phases.
- Existing Mobile Check and First 7 Days tasks remain valid and can be linked or adopted when they represent the same operational work.
- Nurture-email replies still enter the normal inbox, but the controller gives them owned case state instead of requiring a new GHL workflow branch.
- Discord and email change from complete reports to deduplicated work and exception views.
- Peter receives fewer routine notifications and clearer breached-case evidence.
- The call router remains unchanged.

---

## Validation Checklist

How to verify the implementation is complete and correct:

- [ ] A GHL timeout, 401, 429, 500 or malformed response cannot produce “No unread conversations.”
- [ ] AI classification failure produces `manual_review`.
- [ ] Extraction paginates to a complete unique conversation set.
- [ ] Incomplete pagination is reported as incomplete and does not replace a complete state.
- [ ] Every case has a stable cycle key, first-seen time, latest inbound evidence, owner, category, deadline and state.
- [ ] A read flag alone cannot close a case.
- [ ] A verified later staff outbound response can close an eligible case.
- [ ] Approved no-response and delegated-work dispositions retain approver and evidence.
- [ ] A later inbound message reopens or starts a new case cycle without erasing history.
- [ ] Automated acknowledgements cannot falsely prove human completion.
- [ ] Identified content is absent from the CEO dashboard, executive brief and share-safe APIs.
- [ ] Direct GHL links and excerpts require authenticated operational access.
- [ ] Shadow mode performs no GHL writes.
- [ ] Assignment, task and send writes each have independent false-by-default gates.
- [ ] Unassigned conversations route to Admin Eve without overwriting intentional ownership.
- [ ] Breach tasks are deduplicated and close only on exact resolution evidence.
- [ ] Escalations are deduplicated, thresholded and suppressed after resolution.
- [ ] Draft replies are revalidated immediately before send and stale drafts are rejected.
- [ ] Approval evidence is retained after a draft is sent or rejected.
- [ ] Two parity cycles have zero unexplained missing conversations.
- [ ] Two production action cycles have zero duplicate assignments, tasks or escalations.
- [ ] The legacy aggregate-only report is retired only after acceptance.
- [ ] `outputs/systems/reporting-control-plane.md` records the architecture decision and retirement.
- [ ] `context/roadmap.md` reflects the current workstream state.
- [ ] `CLAUDE.md` is updated only if enduring production functionality requires it.
- [ ] `python3 scripts/check_agent_instruction_drift.py` passes after any instruction-file change.

---

## Success Criteria

The implementation is complete when:

1. Every eligible GHL inbound conversation is represented by one complete, durable and evidence-backed case cycle in the protected hub.
2. Source or model failure can never be presented as an empty or low-priority inbox.
3. Admin Eve has one deadline-ordered work queue with explicit ownership and no requirement to maintain a separate manual tracker.
4. The business can report opening backlog, new work, handled work, within-standard handling, overdue work, carryover and oldest unresolved age from persistent evidence.
5. Read status alone cannot count as clearance; all closures have response, disposition or delegated-task evidence.
6. Overdue cases create at most one active controller task and one escalation per approved threshold.
7. Peter receives only approved breached, blocked, unsafe or repeated-carryover exceptions.
8. The shadow sample passes the approved classification and false-closure thresholds before writes are enabled.
9. Any AI-assisted reply is human-approved, policy-versioned, revalidated against the latest conversation and durably auditable.
10. The old Conversation Triage delivery and Level 1 Admin Bot design are retired or superseded without creating a second inbox.

---

## Notes

The primary behavioural question is whether inbox non-clearance reflects capacity, ownership, standards or execution. The controller should establish that from evidence before adding punitive staff metrics or automatic messaging.

The first implementation release should be deliberately narrow: safe extraction, manual-review fallback, persistent cases and shadow measurement. Assignment, task creation, escalation and drafting must remain separately accepted steps.

Current HighLevel public documentation verifies the existence of conversation search, message retrieval, conversation update and send-message endpoints. Exact live payload fields and permissions must be capability-tested against The Evolved's installed token because documentation rendering does not expose every request schema consistently and message-status writes may be restricted to the owning conversation-provider application.
