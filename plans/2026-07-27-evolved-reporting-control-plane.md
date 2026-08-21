# Plan: Evolved Reporting Control Plane

**Date:** 2026-07-27  
**Status:** In Progress  
**Owner:** Peter Brown  
**Implementation surface:** Local workspace, Railway production services and Codex task reporting

## Implementation Checkpoint: 27 July 2026

- Phase 1 complete: explicit service periods, deduplicated active clients, JSON contract and regression tests are live locally.
- Phase 2 local foundation complete: seven-report registry and share-safe executive brief are generated from completed artifacts.
- Phase 3 Railway shadow consumer live, but intentionally unscheduled: `Trainerize Performance` reproduced the protected 149-account/147-workout-detail baseline from a compact protected volume and published aggregate health to the hub. The schedule remains gated on an incremental Railway source refresh and owner review.
- Railway shadow hub deployed and healthy: PostgreSQL persistence, Railway-only scheduling, KPI collection, compatibility-health polling, authenticated CEO dashboard and CEO report API are live.
- First production hub jobs completed: fresh Google KPI, Retention Intelligence, PT Booking Continuity and Revenue Control snapshots were accepted.
- Phase 4 foundation live in shadow: the hub now projects canonical people, source identities, service relationships, lifecycle state, PT Minder payment accounts and payment events. Superseded services are retired when the next reconciliation no longer affirms them.
- Phase 5 in progress: Retention Intelligence and PT/revenue now publish the same complete membership-reconciliation contract into the hub. PT Minder is projected from the accepted V2 snapshot. Consumer read cutover remains behind parity gates.
- Active-client cohort reconciliation complete locally in shadow: the last accepted governed result is 127 confirmed clients. The former 191 hub count contained 152 real source-signal identities plus 39 cancellation-field-only identities. Anita Brown's historical email alias is approved, Eliza Lebsanft's corrected cancellation self-resolves from review, and Emma Johnson's owner-approved Active SGPT restoration is held as a timing difference until the next Railway roster snapshot. Erica Asler, Madison McKiernan and Reemi Shah are additional approved timing differences. Sue Goodwin is confirmed as one current Evolved Anywhere online client outside the SGPT/PT KPI; her stale GHL hold and membership stage, Active Online service label and Sales provisioning flag were corrected without creating an SGPT/PT row. Tsana Leatham is confirmed as an approved complimentary member outside the KPI; no roster row was added, her access was retained and her GHL surname was corrected. The live workbook contains 132 unique SGPT/PT clients and the local owner-decision queue is now zero.
- A versioned cohort contract and dashboard separation now keep active signal, confirmed active, paid/entitled and decision-required measures distinct. Paid/entitled fails closed until event-level evidence is projected.
- Phase 6 partial: all report scheduling remains in Railway; Conversation Triage now publishes its aggregate result to the hub. Durable cross-service leases, catch-up and delivery state remain to be centralised.
- Phase 7 pending.

## Objective

Replace the current collection of independently scheduled reports with a governed reporting control plane.

The owner-approved end state is a Railway-hosted operating-data hub and CEO dashboard. Stripe, PT Minder or its approved evidence feed, GHL and Trainerize are reconciled into canonical operational state. Google Sheets remains the governed expression of the current business position, not the integration database.

The corrected architecture must:

- extract source evidence once per reporting cycle where practical;
- give every report an explicit reporting period, as-of time and source snapshot;
- use one governed cross-system identity and account-classification model;
- preserve separate revenue, PT continuity, retention, performance and conversation domains;
- publish a share-safe executive brief that Codex and Discord can consume without rerunning source extraction;
- retain identified evidence privately;
- fail closed when a required source is stale or unavailable;
- avoid disrupting the existing Railway reports during migration.

## Confirmed Defects

1. `update_metrics.py` labels the KPI posting column as the service week even though the column can represent the just-completed Monday-to-Sunday period.
2. `Total Clients` adds SGPT and PT service counts and can double-count Fast Track clients.
3. Pausing the local Trainerize automation also paused strength-performance and reassessment reporting, while Railway Retention Intelligence replaced only the reconciliation and usage portions.
4. PT and revenue share some protected evidence, but Retention Intelligence still receives separate identity and classification controls.
5. Monday source reads are duplicated across PT continuity, retention, revenue, KPI refresh and Discord reporting.
6. Railway results are not exposed through one share-safe local or Codex-readable executive view.
7. Conversation Triage uses GHL tags rather than canonical lifecycle evidence and does not persist structured outcomes.
8. APScheduler jobs embedded in web services do not yet provide a central durable job lease or cross-service catch-up control, although their outcomes and freshness now report to the hub.

## Target Architecture

### Data plane

Railway PostgreSQL becomes the canonical evidence and reporting-control datastore.

The minimum shared schema is:

- `source_runs`: source, start, completion, status, record counts, limitations and freshness;
- `reporting_periods`: service window, posting date, as-of time and status;
- `canonical_people`: stable internal person ID;
- `identity_links`: source IDs, approved aliases, owner, evidence and effective dates;
- `account_classifications`: governed exclusions and exceptions with expiry;
- `service_relationships`: SGPT, PT, Fast Track, online and other current services;
- `report_runs`: report name, source snapshot IDs, period ID, status and delivery state;
- `report_metrics`: typed report measures with definition version;
- `report_exceptions`: severity, evidence, owner, due date, next action and disposition;
- `executive_briefs`: share-safe daily and weekly summaries.

The canonical operational model also includes:

- `people` and `source_identities`;
- `service_relationships`;
- `payment_accounts` and `payment_events`;
- `entitlements` and `entitlement_adjustments`;
- `appointments` and `session_consumption`;
- `conversation_cases`;
- `assessment_qualifications`;
- `source_snapshots` and `derived_state_versions`.

Existing domain-specific tables remain valid. They reference shared people, periods and source runs rather than re-establishing those concepts independently.

### Control plane

One reporting registry defines:

- report ID and purpose;
- accountable owner;
- schedule and timezone;
- required source freshness;
- reporting-period rule;
- cohort and metric-definition versions;
- identified and share-safe outputs;
- delivery destinations;
- failure and catch-up behaviour;
- upstream and downstream dependencies.

### Presentation plane

The same completed report contract feeds:

- Railway private audit evidence;
- Google Sheet operational views;
- Admin and owner email;
- Discord operational summaries;
- a share-safe Codex executive brief.

Markdown, email, Discord and Google Sheets are views, not systems of record.

The primary presentation surface becomes an authenticated Railway CEO dashboard. The CEO report is rendered from one completed dashboard snapshot and must not recompute metrics independently.

### Intelligence consumers

The shared state supplies:

- Retention Intelligence;
- Conversation Triage;
- Strength Assessment Pre-qualification;
- PT Booking Continuity;
- Revenue Audit;
- Cash Flow;
- KPI Refresh;
- CEO Dashboard and CEO Report.

Each consumer may own domain-specific rules, but none may own a competing identity, payment, entitlement or reporting-period model.

## Delivery Phases

### Phase 1: Decision-quality corrections

1. Introduce a reusable reporting-period module.
2. Correct KPI service-week labels.
3. Separate stock metrics, service relationships and unique-client measures.
4. Build the unique active-client count from the latest protected reconciliation when available.
5. Emit both `context/current-data.json` and the human-readable Markdown derivative.
6. Add freshness and limitation metadata to both outputs.
7. Add regression tests for Monday period selection, Fast Track overlap and missing-source behaviour.

### Phase 2: Registry and executive brief

1. Create `outputs/systems/reporting-control-plane.md`.
2. Create a machine-readable report registry.
3. Add a local executive-brief aggregator that reads only completed share-safe outputs.
4. Include source freshness, report status, period, core metrics and owned exception counts.
5. Add an authenticated Railway endpoint for the production share-safe executive brief.
6. Add a local fetch command for Codex that never prints secrets.

### Phase 3: Restore the orphaned performance consumer

1. Split Trainerize source refresh from performance-report generation.
2. Allow performance reporting to reuse the latest completed reconciliation and recovered workout store.
3. Schedule the performance consumer independently from Retention Intelligence.
4. Record its freshness in the reporting registry and executive brief.
5. Preserve the privacy boundary: identified output remains private and only approved aggregate output reaches the brief.

### Phase 4: Shared evidence controls

1. Add PostgreSQL-backed identity-link and account-classification repositories.
2. Import the current approved local and Railway-volume controls with fingerprints and provenance.
3. Make Retention Intelligence, PT Continuity and Revenue Control read the same repository.
4. Preserve time-bounded owner approvals and expiry.
5. Retain compatibility readers during one migration cycle.
6. Compare old and new classifications before removing compatibility paths.

### Phase 5: Source snapshot reuse

1. Persist one completed daily GHL, Stripe and Trainerize membership snapshot.
2. Make Retention Intelligence consume that snapshot.
3. Make the Monday revenue audit consume a fresh completed snapshot rather than rerunning the same extraction.
4. Let PT Continuity retain its appointment-specific reads while consuming shared commercial and identity evidence.
5. Record every consumed source run ID in each report run.

### Phase 6: Scheduling and delivery consolidation

1. Move scheduled triggers to a durable Railway schedule or a dedicated single control process.
2. Persist job leases and completion state in PostgreSQL.
3. Add missed-run catch-up and stale-report alerts.
4. Remove duplicate local KPI refreshes from Discord report execution.
5. Replace the local JSON sent ledger with an atomic or database-backed delivery ledger.
6. Publish the completed executive brief from Railway through an authenticated aggregate-only endpoint.
7. Keep local compatibility schedules disabled once their Railway replacements are verified.

### Phase 6A: PT roster self-mending

1. Implement the pending PT service and exception contract defined in `outputs/systems/pt-roster-self-mending.md`.
2. Detect incomplete Sales and Active PT rows from accepted hub snapshots without repeating GHL, Stripe or Trainerize extraction.
3. Resolve the existing row through canonical identity and service-start evidence; never append when zero or multiple candidates are found.
4. Produce exact, read-only proposed patches for the allowlisted PT worksheet columns.
5. Validate Erica Asler as the first acceptance fixture and add cancellation, hold, PIA, pending-debit, duplicate-event and conflicting-rate fixtures.
6. Pass two owner-reviewed shadow parity cycles with zero duplicate rows and zero incorrect lifecycle changes.
7. Add a disabled Railway-only writer with unchanged-row preconditions and recoverable before and after evidence.
8. Obtain explicit owner approval before enabling writes or changing the published GHL workflow.

### Phase 7: Conversation intelligence integration

1. Resolve lifecycle through the canonical person and service model.
2. Paginate unread conversations.
3. Persist classification, recommended action, owner, due date and later disposition.
4. Publish conversation events as retention and service signals without treating model output as authoritative state.
5. Retain human review for urgent or ambiguous classifications.

## Safety and Migration Gates

- No existing Railway production schedule is removed before its replacement has completed two equivalent shadow runs.
- No source report is overwritten by a failed or incomplete run.
- No member, payment, appointment or lifecycle record is changed by the reporting control plane.
- Identified data stays in private PostgreSQL, protected Railway volumes or ignored local private storage.
- The executive brief contains aggregates and operational counts only.
- Identity migration requires exact identity-set, count, fingerprint and classification parity.
- The two remaining owner-decision identities must be resolved before lifecycle read cutover. Resolved historical cases remain in the immutable audit baseline and are retired from the queue only when current authoritative source state proves the correction.
- Paid/entitled remains unavailable until Stripe events, specific PT Minder events and governed timing exceptions are projected.
- A production consumer cutover requires two equivalent shadow cycles after owner review; the current local implementation is not a cutover.
- Google Sheet writes remain allowlisted and fail closed.
- Production packages exclude `.env`, credentials, private data, report extracts and unrelated workspace files.

## Validation

Required automated coverage:

- period-selection and label tests;
- unique-person deduplication tests;
- source-freshness and failed-run tests;
- registry validation;
- executive-brief redaction tests;
- identity-control parity tests;
- exact cohort-set difference and exclusive-bucket invariant tests;
- GHL-authoritative lifecycle and final-access boundary tests;
- pending, PIA, hold, future-start, PT-only, legacy PT Minder and staff-exclusion tests;
- report snapshot lineage tests;
- scheduler idempotency and catch-up tests;
- existing PT, revenue and retention suites.

Required production checks:

- current Railway health endpoints remain healthy;
- no duplicate email or Discord delivery occurs;
- Monday revenue totals remain reproducible;
- PT findings remain classification-compatible;
- Retention classifications are compared against the prior implementation;
- the Codex executive brief matches the same production report IDs;
- the orphaned Trainerize performance report refreshes on schedule.

## Definition of Done

The architecture is corrected when:

1. Every active report appears in the governed registry.
2. Every report declares its service period and source snapshot IDs.
3. Unique active clients are not calculated by summing overlapping services.
4. Active signal, confirmed active, paid/entitled and exception are separate versioned measures.
5. Revenue, PT and retention consume one governed identity model.
6. Trainerize performance reporting is scheduled and fresh.
7. Monday duplicate source extraction is materially reduced.
8. Railway, email, Discord, Google Sheets and Codex show views of the same completed evidence.
9. Failed or stale sources are visible centrally and cannot silently publish a current-looking report.
10. Exact identity parity and owner review pass before any production consumer cutover.
11. Legacy duplicate schedules are removed only after shadow parity is proven.

## Owner Architecture Decision: Railway-Only Scheduling

Recorded 27 July 2026:

- Railway is the sole scheduler for all reports and report views.
- No Codex heartbeat, Codex cron automation or harness-local report schedule is permitted.
- The four existing Codex report automations were deleted.
- Performance reporting remains unscheduled until its protected data dependency is available in Railway.
- Existing non-Codex local compatibility processes must migrate to Railway and then be disabled after shadow parity.

## Owner Architecture Decision: PT Minder Human-Assisted Feed

Recorded 27 July 2026:

- Peter will authenticate to PT Minder locally through the browser once each week.
- PT Minder capture is manually initiated and read-only.
- The browser submits one validated source snapshot to an authenticated Railway endpoint.
- No PT Minder credentials, report schedules or business calculations are retained locally.
- Railway owns snapshot acceptance, freshness, reconciliation, stale-source alerting and all downstream reporting.
- PT Minder snapshots expire as current evidence after eight days.
- Failed or partial capture cannot replace the last complete snapshot.
- Revenue Audit, Cash Flow and PT Booking Continuity must consume the same accepted PT Minder snapshot.
