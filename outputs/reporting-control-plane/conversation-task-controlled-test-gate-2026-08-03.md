# Conversation Internal-Task Controlled Test Gate

**Date:** 3 August 2026  
**Approval:** Peter Brown approved one reversible temporary-contact test  
**Test authority:** `build7-conversation-controlled-test-2026-08-03`  
**Result:** Not executed; cutover gate correctly blocked it  
**External changes:** None

## Exact owner

- Task owner: Admin Eve, GHL user `EtONSa9U2pTpyOpX1hX8`.
- Scope: one unread or unassigned Conversation internal task.
- No client message, assignment change, conversation reply or unrelated source mutation is authorised.

## Protected cutover evidence

Build 6 queried the exact contract on 3 August 2026:

- metric: `consumer_conversation_triage_contract`;
- definition: `conversation-triage-hub-read-v1`;
- effective state and publication: `legacy`;
- `promotion_authorised=false`;
- technical readiness: false;
- owner accepted: false;
- acceptance record ID: absent;
- scheduled comparison cycles: zero of two;
- immutable acceptance fingerprint: absent;
- protected legacy fallback: available.

The explicit blockers are no scheduled Hub-versus-legacy comparison, unverified confidence, no Build 4 technical acceptance, no exact parity record and no Peter metric-level acceptance reference.

## Safeguard verification

The controlled-test contract now requires all of the following before it can queue:

- exact test authority reference and Peter approval;
- a non-deliverable `.invalid` test contact explicitly marked as temporary;
- exact Admin Eve assignment;
- deterministic idempotency and cooldown;
- complete, fresh and evidence-backed decision input;
- consent and suppression checks;
- two distinct exact parity cycles;
- matching immutable cutover record ID and fingerprint;
- `promotion_authorised=true`;
- reversible cleanup and dispatch audit evidence.

Because the cutover gate failed, no GHL contact or task was created. This is the expected safe result. The approval remains recorded for one future test after the exact gate passes.
