# Retention Intelligence Railway Service

**Status:** In Progress
**Owner:** Peter Brown
**Created:** 26 July 2026
**Operating mode:** Read-only shadow

## Decision

Build a separate Railway-ready service that turns the existing GHL, Stripe and Trainerize reconciliation into a retained member-engagement history and an explainable weekly retention review.

Google Sheets remains the staff-facing operating surface. It is not the underlying database. Identified daily snapshots are stored privately in PostgreSQL in Railway, with SQLite supported only for local development.

## V1 Outcomes

1. Run the existing read-only cross-system reconciliation each morning.
2. Fetch a bounded recent Trainerize calendar window for the current active roster.
3. Retain one member snapshot per run without overwriting prior history.
4. Classify members as `Thriving`, `Stable`, `Drifting`, `At risk`, `On hold`, `Insufficient data`, `Operational exception` or `Excluded`.
5. Store the reasons, source coverage and model version beside every classification.
6. Publish a current `Retention Radar` view and weekly aggregate `Retention KPI` view to Brown & Casserly only after an explicit write flag is enabled.
7. Expose authenticated health, latest-run and preview endpoints.
8. Send no member communications and make no GHL, Stripe or Trainerize changes.

## Data Contract

### Identity and lifecycle

- GHL contact ID and exact normalized email.
- Trainerize user ID.
- Membership type and pipeline stage.
- Commercial-entitlement, Trainerize-access and GHL-active signals.
- Cancellation and final-access evidence.
- Owner-approved account classification.

### Usage

- Tracked Trainerize workout counts for 7, 28 and 90 days.
- Personal baseline weekly workout rate from days 29 to 112.
- Recent weekly workout rate from the latest 28 days.
- Percentage change from the personal baseline.
- Last meaningful tracked workout and days since.
- Latest Trainerize sign-in, recorded separately from completed training.

### Retention output

- Status and urgency.
- Plain-language reason.
- Data-confidence level.
- Assigned action owner and review date.
- Classifier version.
- Snapshot and source timestamps.

## Classification Rules

V1 is deliberately deterministic and explainable. It does not claim to predict churn.

- Exclude staff, owner, test and approved internal accounts from member-retention KPIs.
- Mark a cross-system medium-or-higher mismatch as `Operational exception`.
- Mark new or sparsely observed clients as `Insufficient data`.
- Do not classify Fit & Flexible members as disengaged from missing strength-workout data alone. Their confidence remains low until reliable attendance evidence is connected.
- Use decline from the member's own baseline as the primary usage signal.
- Use absolute inactivity only where the service has adequate workout-data coverage.
- Preserve every reason and rule input for later validation against actual holds and cancellations.

## Google Sheets Design

### Retention Radar

One current row per included active member:

- Member
- Email
- Service
- Trainer
- Status
- Data confidence
- Workouts 7d
- Workouts 28d
- Workouts 90d
- Personal baseline per week
- Recent rate per week
- Change from baseline
- Last workout
- Days since activity
- Reason
- Action owner
- Review date
- Snapshot time

### Retention KPI

One row per weekly snapshot:

- Active members in scope
- Members with adequate usage coverage
- Thriving
- Stable
- Drifting
- At risk
- Insufficient data
- Operational exceptions
- 28-day active rate
- Material-decline rate
- Reassessments due when available

## Delivery Sequence

1. Build and test the classification engine independently of APIs.
2. Build private PostgreSQL/SQLite snapshot persistence.
3. Reuse the existing reconciliation runner for current identity and lifecycle evidence.
4. Add bounded Trainerize recent-calendar extraction.
5. Add authenticated Flask endpoints and the Brisbane scheduler.
6. Add fail-closed Google Sheets writers, disabled by default.
7. Validate locally without Sheet writes or emails.
8. Deploy to Railway when project access and protected variables are available.
9. Review the first seven daily runs before enabling Sheet writes.
10. Validate classifications against 8 to 12 weeks of actual lifecycle outcomes before creating coach tasks.

## Safety Gates

- The service refuses to start unless `SHADOW_MODE=true`.
- No connected-system mutation client is implemented.
- Sheet writes require `SHEETS_WRITE_ENABLED=true`.
- The target spreadsheet and exact tab names are allowlisted.
- A failed source run does not replace the latest successful view.
- Names and emails never appear in public aggregate outputs or application logs.
- Manual and fuzzy name matching are prohibited.
- No trainer task, email, SMS or member message is created in V1.

## Definition of Done

- Local tests cover rule boundaries, exclusions, service-specific confidence and idempotent storage.
- A live read-only run produces retained member snapshots and aggregate KPIs.
- The service can start under Railway with PostgreSQL and an authenticated health endpoint.
- The Retention Radar and Retention KPI payloads can be previewed without writing.
- Documentation, environment requirements and recovery behaviour are recorded.
- The roadmap reflects the seven-run shadow-validation gate.
