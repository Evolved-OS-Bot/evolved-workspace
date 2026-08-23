# PT Hold Entitlement Reconciliation — Local Completion and Deployment Gate

**Date:** 24 August 2026  
**Owner:** Evolved workspace  
**State:** Local candidate complete; production activation blocked  
**Branch:** `codex/pt-hold-entitlement-reconciliation`  
**Candidate commit:** `8b543cb`

## Outcome

The two local implementations were reconciled into one candidate on the current guarded Billing OS architecture. The obsolete handler replacement was not retained. Its pure PT entitlement engine and boundary tests were replayed onto the governed repository snapshot, then reconciled with the later canonical Billing OS service-change guards and test delta.

The candidate separates Membership/SGPT date calculations from PT session entitlement. When its protected PT gate is enabled, PT branches before any Stripe lookup, daily proration, GHL status write or exception-task creation. It can only return a deterministic proposal, `no_transfer_needed`, or `review_required`; every result performs zero mutations.

## Controls verified

- PT evidence requires an existing Conversation ID, complete governed evidence window, payment cadence, sessions per payment, validated billing-to-service offset, stable payments and appointments, prior-adjustment evidence and reviewed risk flags.
- Appointments are classified before, inside and after the inclusive service hold.
- Only exact one-to-one paid-in-hold to skipped-payment-unfunded post-hold transfers are proposed.
- Delivered in-hold sessions, irregular cadence, missing boundary coverage, missing provenance, unsupported appointment states, policy-sensitive cases, count mismatches and any existing cash/session adjustment fail closed.
- Proposals have deterministic IDs and specify no cash adjustment, no task and no tracker.
- The existing GHL Conversation remains the sole intended work item. The candidate does not post a note because that write gate is not authorised.
- `PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED` defaults to `false`; a code deployment alone cannot activate the PT branch.

## Verification

- Current Billing OS regression suite: **50/50 passed**.
- PT unit and endpoint integration suite: **18/18 passed**.
- Python compilation: passed.
- Agent instruction drift check: passed.
- `git diff --check`: passed.
- Acceptance boundary fixture: one already-paid in-hold entitlement is proposed for the otherwise-unfunded return appointment; four weekly payments are classified as hold-skipped; no cash adjustment is proposed; control dates are not treated as debit dates.
- Protected-system integration tests prove the PT branch makes no Stripe call and ambiguous PT evidence creates no Billing OS status write, exception task or tracker.

## Live read-back

Read-only production checks on 24 August 2026 returned:

- `GET /health`: HTTP 200 with the existing `{"status":"ok"}` response.
- Empty-payload `POST /stripe/pt-hold/reconcile`: HTTP 404.

This proves the current Billing OS remains healthy and the PT candidate is not deployed. No contact, Conversation, task, billing record, appointment, membership, entitlement, workflow, environment variable or member communication was changed.

## Exact deployment gate

Dark deployment was not attempted because this environment has no Railway credential or CLI and the governed local snapshot is not a deployable remote branch. Forcing the branch onto the older remote history would carry unrelated snapshot state and could regress protected Billing OS behavior.

Live PT activation also remains unauthorised and incomplete because:

1. no Hub adapter yet supplies the required complete payment, appointment, adjustment, risk and Conversation evidence;
2. Conversation clearance remains shadow-only with `promotion_authorised=false`; and
3. there is no authorised existing-Conversation internal-note handoff or freshness-bound approval executor.

## Safest continuation

1. Establish the exact Railway source/credential for Billing OS and deploy commit `8b543cb` dark with the PT gate confirmed `disabled` in live health read-back.
2. Add the read-only Hub evidence adapter and run governed proposal parity without posting or mutation.
3. Pass the immutable Conversation promotion gate and separately approve the exact internal-note handoff.
4. Add approval-time evidence re-read and proposal-ID idempotency; test rejection, staleness, retry and duplicate-credit controls.
5. Enable the PT gate only for a controlled regular-cadence pilot. Keep member messaging and unattended billing/appointment mutation disabled.

