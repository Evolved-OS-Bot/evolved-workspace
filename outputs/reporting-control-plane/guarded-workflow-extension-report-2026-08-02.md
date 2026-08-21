# Guarded Workflow Extension Build Report

**Date:** 2 August 2026  
**Contract:** `hub-workflow-extension-v1`  
**Status:** Safe framework complete locally; activation decisions remain  
**Production impact:** None

## Delivered

- One versioned Hub decision envelope for retention, conversation support, PT booking continuity, revenue exceptions, onboarding outcomes and Strength Assessment outcomes.
- One durable protected outbox and append-only audit ledger.
- Deterministic idempotency, same-person and same-scope cooldown, suppression, consent, source freshness and completeness controls.
- Exact owner role and GHL user ID requirement before queue eligibility.
- Separate decision authority: technical readiness, metric acceptance and publication authority cannot queue a task.
- Protected policy, preview, decision-ingestion and outbox endpoints.
- A hard side-effect boundary that allows only internal staff tasks and rejects client messages and source-system changes.

## Live workflow inventory

- Onboarding outcome closure and Strength Assessment outcome closure already have accepted, controlled internal GHL task executors. The new common dispatcher has not replaced them, so no duplicate task path exists.
- Retention Intelligence remains read-only and creates no task.
- Conversation Triage retains its current internal report delivery and creates no new GHL task.
- PT Booking Continuity and Revenue Control retain their current Railway reports and Admin review paths.
- Existing Billing OS exception tasks remain inside their separately accepted workflow scope and were not broadened into general revenue automation.

## Acceptance state

| Policy | Current result |
| --- | --- |
| Onboarding outcome follow-up | Internal task allowed through existing executor |
| Strength Assessment outcome follow-up | Internal task allowed through existing executor |
| Retention intervention review | Owner accepted: Member Experience, operationally Piper with Megan oversight; proposal only until cutover |
| Conversation support routing | One controlled test approved, but gate-blocked at legacy and zero of two parity cycles |
| PT booking continuity | Proposal only |
| Revenue exception review | Proposal only |

Build 2's final lifecycle contract is live in Hub deployment `38c0d667-b23c-4bae-865f-fecc33e1a184`. It supplies stable Hub person IDs, lifecycle source snapshots, immutable event lineage and the accepted suppression codes `approved_hold`, `active_cancellation_notice`, `downgrade_only_not_member_loss`, `staff_or_complimentary`, `resolved_or_inactive` and `lifecycle_unresolved`. This remains evidence only and does not authorise retention intervention. Build 4 confirmed that technical readiness remains separate from Peter's workflow decision authority. Build 6 has the final contract and endpoint names for downstream migration.

Build 6 completed its framework without promotion authority. Retention Intelligence, Conversation Triage and PT Booking Continuity still require two distinct Railway parity cycles plus Peter's exact-rule and cutover approval. Successful combined Hub deployment `38c0d667-b23c-4bae-865f-fecc33e1a184` makes Revenue Control's formerly missing person-keyed roster delivery attributes live through `current-person-v1` schema v2. Build 6 is authorised to run the fresh Revenue comparison cycle, but that permission is evidence collection only. Revenue remains gated until the exact immutable cutover-status record returns `promotion_authorised=true` and its fingerprint matches. The workflow contract validates promotion authority, schema version, fresh exact parity, status record ID and fingerprint.

## Verification

- Guarded workflow unit, persistence, exact-owner, controlled-test, cutover-promotion and dispatch-evidence tests: 23 passed.
- Complete Operating Data Hub suite after exact Retention ownership and controlled Conversation test authority: 232 passed.
- Claude and Codex instruction drift check: passed.
- Diff whitespace validation: passed.

No client message was sent. No membership, payment, appointment, Trainerize account, Google Sheet or source record was changed. No schedule was created; Railway remains the sole scheduler.

## Exact owner decisions still required

1. Retention intervention ownership is resolved: Member Experience owns the review, Alyssa Crighton, operationally Piper, is the current assignee, and Megan oversees the function. Piper absence fails closed to preview and explicit escalation.
2. Conversation test approval is resolved, but the test cannot run until the exact contract has two distinct scheduled parity cycles and a matching immutable cutover record with `promotion_authorised=true`.
3. PT and revenue task activation: after `/api/v2/reporting/cutover-status` returns `promotion_authorised=true` for the exact consumer, approve one reversible internal-task test for each exact exception family. Revenue's data contract is live and its comparison cycle is authorised, but the task test remains blocked until the exact cutover record and fingerprint pass.

Retention and Conversation owner authority is now recorded, but both remain proposal-only until their cutover gates pass. PT and Revenue test authority remains unapproved.
