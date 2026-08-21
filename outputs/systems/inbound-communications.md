# Inbound Communications System Audit

**Verified:** 22 July 2026

## Live phone workflow

The published `Main Incoming Call Router` workflow (`f85ae25e-6c12-4c50-a606-df888ea5ca4b`) is triggered by calls to `+61 483 968 880`.

During its configured Admin Hours, the workflow transfers the call to Nora's hard-coded mobile number. If Nora does not answer, it transfers to Megan. Outside Admin Hours, it transfers directly to Megan.

The workflow has 64 historical enrolments and zero active. Its available 30-day history showed no enrolments.

## Confirmed gaps

- The primary destination is attached to Nora as a person rather than the durable Admin Eve role.
- The final no-answer path ends without a callback task or another accountable handoff.
- There is no automatic SMS acknowledging the missed call or setting an expected response time.
- No workflow name matching `missed`, `voicemail` or `inbox` exists in the live workflow register.
- Written inbox assignment, collision control, response-time standards and escalation are not proven by this workflow audit.

## Required future design

Keep the live router unchanged until the operating roster and callback owner are confirmed. A future rebuild should use one maintained role-to-person mapping, record the final outcome, send a concise missed-call acknowledgement where appropriate, and create a single assigned callback task with a due time and escalation rule.

## Live Conversations audit

The 22 July 2026 live Conversations audit found five unread conversations. Three were unassigned, one was owned by Nora Silva and one was owned by Piper Mae. This is a small snapshot rather than a historical service-level measure, but it proves that unread messages can enter the shared inbox without an accountable owner.

Conversation SLA settings are off. GHL therefore has no response-time target, breach escalation or SLA performance data for this location. The Manual Actions queue contained no pending calls or SMS actions, so the present gap is inbox assignment and escalation rather than a Manual Actions backlog.

The durable operating design should:

- assign every new inbound conversation to Admin Eve or an explicit channel owner;
- define a response-time target for staffed and unstaffed hours;
- escalate unread or unreplied conversations that breach the target;
- preserve Piper Mae as a follower or second-level owner where an in-person member response is useful;
- avoid two staff members replying simultaneously by making one person accountable for the written response.

No GHL settings were changed during this audit.
