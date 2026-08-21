# Trainerize Reporting and Reconciliation Sprint

**Status:** In Progress, Phase 4 scheduled validation active  
**Re-baselined:** 2026-07-23  
**Owner:** Peter Brown  
**Target duration:** 30 to 60 days  
**Default execution mode:** Read-only

## Decision

The original GHL, Stripe and Trainerize 90-day sprint has been re-baselined. The concurrent GHL audit has already implemented or verified much of the lifecycle control work that the original plan treated as future build work.

This sprint will not redesign or repair GHL workflows. It will use the current audited GHL state and focus on the value that Trainerize API access adds: cross-system reconciliation, operational exception detection, member-performance reporting and repeatable de-identified analysis.

The original plan remains at `plans/2026-07-22-ghl-stripe-trainerize-90-day-sprint.md` as the historical control-design record.

## Current Baseline

The following controls are already live or decided:

- GHL remains the contact, agreement, lifecycle and communications source of truth.
- Stripe remains the payment and subscription source of truth.
- Trainerize remains the coaching access, programming and completed-training source of truth.
- Brown & Casserly Pty Ltd 2026 remains the staff-maintained active and cancellation roster. It is a required operational closure surface, not a substitute for billing or access evidence.
- The Initial Consultation product creates the assessment account before the Strength Assessment.
- Membership fulfilment reuses the existing Trainerize account and does not send a second invitation.
- Product Starts is configured for Fit & Flexible, Strong, Fit & Flexible and Fast Track.
- Normal memberships start on the day of purchase; explicit future starts use the recorded membership start date.
- The assigned consultant completes the manual Trainerize handoff, and Admin Eve verifies it by day two.
- The 999 non-expiring Class Access model is approved.
- Trainerize deactivation is the hard access stop on cancellation.
- The canonical manual control is `reference/sops/post-sale-member-onboarding.md`.
- GHL workflow remediation remains owned by the concurrent GHL audit.
- Read credentials were live-verified on 23 July 2026 for GHL contacts, Trainerize clients and Stripe customers, subscriptions, invoices, products, prices, Checkout Sessions and Payment Intents.

## Objectives

### 1. Membership Reconciliation

Produce a repeatable comparison of GHL, Stripe, Trainerize and the Brown & Casserly operational roster that identifies:

- active paying members missing from Trainerize;
- cancelled or ended members who retain Trainerize access;
- deactivated Trainerize clients who remain active in GHL or Stripe;
- duplicate, missing or ambiguous identities;
- account access, Owner or location mismatches where exposed by the API;
- missing expected program or group state where exposed by the API;
- overdue cancellation deactivation;
- incomplete onboarding outcomes; and
- approaching 52-week Trainerize product expiry where the required product dates can be obtained reliably.

Every exception must contain an accountable owner, evidence, severity and recommended action. Ambiguous cases must not be auto-corrected.

### 2. Member-Performance Reporting

Refresh operational reporting for:

- total workouts completed;
- workouts completed by calendar period and membership tenure;
- attendance and training consistency;
- last completed workout and inactivity risk;
- personal records and material strength improvements;
- benchmark changes at 3, 6, 12, 24 months and beyond;
- Goblet Squat to Nexus Point Squat progression;
- canonical Nexus, Bench Press and Deadlift improvement;
- relative strength where a valid body weight exists;
- members due for reassessment; and
- remarkable-results candidates for coach validation and consent-controlled marketing.

Reporting must distinguish operational counts from source-recorded female outcome cohorts. Missing or inconsistent demographic fields must remain explicit rather than being inferred.

### 3. Strength-Data Continuity

Maintain two governed output layers:

1. A private identified operational layer for coaching, follow-up and reconciliation.
2. A de-identified analytical layer for approved reporting and the Women's Strength Project.

The identified source remains local and private. Only approved de-identified outputs may be uploaded to shared analytical Drive folders.

## Scope Boundaries

### In Scope

- Read-only API inventory and capability verification.
- Cross-system identity matching.
- Snapshot creation and history.
- Exception reporting.
- Scheduled reporting refreshes.
- De-identified analytical exports.
- GHL task or notification creation for confirmed exceptions, only after the delivery design is approved.
- Trainerize deactivation testing and automation, only if the supported write path and notification behaviour are proven with allowlisted test accounts.

### Out of Scope

- General GHL workflow cleanup or taxonomy repair.
- Rebuilding controls already implemented by the concurrent GHL audit.
- Replacing GHL, Stripe or Trainerize.
- Building a member-facing training application.
- Automating the 999-credit balance without a supported entitlement endpoint.
- Reactivating former members for routine reporting.
- Automated personal-data deletion.
- Building or claiming a clinically validated Women's Strength Index.

## Coordination Rule

Before every implementation tranche, re-read:

- `context/roadmap.md`;
- the latest relevant files under `outputs/systems/`;
- `plans/2026-07-17-ghl-workflow-governance-audit.md`; and
- any newer dated GHL remediation plan.

This task may rely on GHL changes only after they are written into the shared workspace or independently verified live. Unsaved changes and conversation-only decisions in another task are not visible here.

If a required GHL change is discovered, record it as a dependency for the GHL audit. Do not make a competing change from this sprint.

## Data Contract

| Domain | Authoritative source | Minimum fields |
|---|---|---|
| Identity | GHL | Contact ID, normalised email, name, lifecycle state |
| Commercial entitlement | Stripe | Customer ID, subscription ID, status, paid-through or scheduled-end date |
| Agreement and service | GHL | Membership type, agreement date, start date, cancellation date, final service date |
| Coaching access | Trainerize | Client ID, email, active state, access level, Owner, location |
| Delivery configuration | Trainerize | Programs, groups and product state where exposed reliably |
| Activity | Trainerize | Workout ID, workout date, completion state, exercise results |
| Body measures | Trainerize | Measurement type, value, unit and effective date |
| Operational response | GHL | Exception task ID, assignee, status and resolution note |

Email may be used for deterministic matching only when one exact normalised match exists. Name-only and fuzzy automatic matching are prohibited.

Persistent GHL contact ID, Stripe customer ID and Trainerize client ID should become the durable cross-system identity keys.

## Capability Tiers

### Tier A: Verified Read Access

Build first using the already verified Trainerize reads for client rosters, client summaries, appointments, programs, group compliance, calendars, body stats, accomplishments, goals, habits and active-client workout details.

### Tier B: Requires Controlled Verification

- Product subscription and start/end dates.
- Class Access Add-ons and credit balances.
- Access-level and Owner changes.
- Program and group assignment writes.
- Client deactivation.

These capabilities must be classified as supported, unsupported or unavailable before being included in an automated control.

### Tier C: Manual Control

Anything not exposed reliably remains a GHL staff task backed by the Post-Sale Member Onboarding SOP or the relevant service-change procedure.

## Delivery Phases

### Phase 1: Read-Only Baseline, Days 1 to 7

1. Inventory the newest GHL audit outputs and freeze the initial data contract.
2. Confirm available GHL and Stripe read credentials and endpoints.
3. Pull current Trainerize client state without changing any account.
4. Build deterministic identity matching and an ambiguity report.
5. Save a timestamped private snapshot and provenance record.

**Exit criteria:** Every active record is matched, unmatched or ambiguous with a documented reason. No external writes occur.

### Phase 2: Reconciliation MVP, Days 8 to 15

1. Compare active, cancelled, held and deactivated lifecycle states.
2. Detect stale access, missing access, duplicate identities and overdue cancellation actions.
3. Separate high-confidence exceptions from capability gaps.
4. Produce a private reconciliation workbook or report with severity, owner and next action.
5. Validate a sample manually against all three systems.

**Exit criteria:** The report is reproducible and the manually checked sample contains no unexplained false positives.

### Phase 3: Performance Reporting, Days 16 to 30

1. Reuse the proven longitudinal extraction logic.
2. Add tenure-based workout and strength measures.
3. Add inactivity, reassessment-due and remarkable-results candidate views.
4. Preserve canonical exercise-name mappings and raw source labels.
5. Produce private identified and approved de-identified outputs.

**Exit criteria:** Counts reconcile to Trainerize source totals within documented API coverage limits, and all cohort exclusions are visible.

### Phase 4: Scheduled Operation, Days 31 to 45

1. Schedule snapshot and reporting refreshes.
2. Retain dated history rather than overwriting the only evidence.
3. Route confirmed operational exceptions to the approved owner.
4. Add failure alerts, run logs and last-success timestamps.
5. Publish only approved de-identified analysis to Drive.

**Exit criteria:** At least seven consecutive scheduled runs complete with clean logs or correctly raised exceptions.

### Phase 5: Optional Write Controls, Days 46 to 60

1. Confirm Trainerize's supported deactivation path and notification behaviour.
2. Test only with allowlisted Evolved-owned accounts.
3. Require the accepted GHL cancellation record and verified final service date.
4. Preview the intended action before execution.
5. Verify the resulting state and retain an audit record.

Other Trainerize writes remain deferred unless they solve a measured problem and pass the same safety gates.

## Initial Deliverables

- Cross-system identity register.
- Timestamped private roster snapshots.
- Membership reconciliation report.
- Exception register with owner and resolution status.
- Active-member workout and strength report.
- Remarkable-results candidate view.
- Reassessment-due view.
- De-identified analytical export.
- Scheduled-run log and data-quality summary.

## Safety and Privacy Gates

1. Read-only is the default.
2. Former members are not reactivated for routine extraction.
3. Credentials and personal data never appear in source control or logs.
4. Identified outputs remain in approved private storage.
5. No automatic action uses name-only or fuzzy identity matching.
6. Every write requires an expected-state check, stable idempotency key and post-write verification.
7. Any action capable of sending member communications requires a documented notification test.
8. De-identified does not mean merely removing the name; direct identifiers and unsafe quasi-identifiers must be treated according to the approved data standard.

## Definition of Done

The sprint is complete when:

- a scheduled read-only process produces reliable cross-system membership reconciliation;
- exceptions are assigned and traceable;
- workout and strength reporting refreshes without manual historical extraction;
- approved de-identified analysis is reproducible from the private source;
- report limitations and API coverage are explicit;
- no competing GHL workflow changes were introduced; and
- any enabled Trainerize write has passed allowlisted testing, preview, idempotency, notification and reconciliation controls.

## Immediate Next Action

Resolve the remaining current-member GHL signals and duplicate-Stripe records. Then approve the recurring read-only schedule and alert destination before enabling Phase 4 and observing seven consecutive runs.

## Implementation Record

On 23 July 2026, Phases 1 to 3 were implemented as a read-only MVP:

- `scripts/membership_reconciliation.py` builds source snapshots, an exact-email identity register and an owned exception queue.
- `scripts/trainerize_performance_reporting.py` builds private active-member, remarkable-results and reassessment-due views plus an aggregate performance summary.
- `scripts/run_trainerize_reporting.py` runs both layers in one command.
- Stripe invoices are an optional 90-day audit mode; subscription status is the routine entitlement signal.
- Identified data stays in `data/private/integration-reporting/`.
- Aggregate summaries stay in `outputs/trainerize-reporting-reconciliation/`.
- Fifteen automated tests pass.
- The first refined live run completed with 2,780 GHL contacts, 2,118 GHL opportunities, 284 Stripe customers, 301 subscriptions, 168 active Trainerize clients, 404 deactivated clients and 2,348 deterministic identities.
- The private owner-confirmed identity controls now contain 13 verified email links and three source-record links without fuzzy matching.
- Paid-without-Trainerize-access and the critical/high queue are now zero. The evidence-based review queue contains 59 medium and 569 low rows. Historical inactive duplicates remain visible at low priority; low-priority legacy GHL contacts without an email remain separated from active-member access risks.
- Detailed workout history is available for 164 of the 168 active clients, through 21 July 2026.

Phase 4 scheduled validation is active through the Codex automation `daily-trainerize-reconciliation`, running daily at 5:45 am Brisbane time. It reports in Codex and has no GHL, Stripe, Trainerize, Sheet or Drive write path.

## Current Protected Baseline: 24 July 2026

The post-review baseline supersedes the initial counts for current operational decisions:

- 2,781 GHL contacts and 2,120 opportunities;
- 284 Stripe customers and 301 subscriptions;
- 149 active and 422 deactivated Trainerize clients;
- zero critical or high exceptions;
- zero critical, high or medium exceptions, plus 565 low-priority historical hygiene rows;
- 147 active clients with detailed recovered workout history;
- 68 remarkable-results candidates; and
- 102 members due for reassessment.

The reporting runner remains read-only. A separate owner-authorised allowlisted cleanup corrected approved GHL lifecycle states and Trainerize access with expected-state and post-write verification. Brown & Casserly Pty Ltd 2026 was then synchronized without inventing historical cancellation dates.

The medium queue is closed in protected run `20260725T040035Z`. Renae Acton was fast-tracked to cancellation across GHL, Trainerize and Brown & Casserly. Belinda Jones was confirmed on an indefinite Stripe `pause_collection: void` hold pending her paid 30-day cancellation period and was deactivated in Trainerize. Gigi / Giuljana Umlauf now has the missing GHL PT 1 p.wk lifecycle marker. Jo Kizu and Vavaa Mawuli were deactivated in Trainerize. Zoya Sharfuddin's and Sophie Laurence's authoritative Stripe customers were registered without deleting historical billing records.

Morrigan Moore and Brodie Tsikanaris no longer appear as false billing exceptions because their owner-approved external-payment and prepaid-credit classifications now apply consistently. Mariya Boycheva's missing `member` tag and Michelle Sharp's stale `old member` tag were corrected and post-write verified.

Alyssa Crighton is classified as staff from owner confirmation and populated GHL employment fields. Her `piper@theevolvedgym.com.au` email is not a Piper Mae identity, and the reconciliation now suppresses the false missing-Trainerize-access exception without altering Alyssa's historical zero-value PT opportunity.

The first seven scheduled runs form the Phase 4 shadow-validation gate. Each run must complete all source snapshots, retain timestamped evidence and correctly surface any material exception without automatically changing an external system.
