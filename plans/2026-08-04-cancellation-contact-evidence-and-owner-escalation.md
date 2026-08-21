# Plan: Cancellation Contact Evidence and Owner Escalation Control

**Created:** 2026-08-04
**Status:** Ready
**Request:** Replace Piper's manual `cs: contact made` dependency with automatic reply and connected-call evidence, and prevent unsupported automated escalation messages from Megan.

---

## Overview

### What This Plan Accomplishes

This plan makes HighLevel record cancellation contact evidence from observable conversation events rather than relying on Piper to add a tag. It also converts the Day 14 Megan pathway from an automatic client SMS into a review-only internal task that fires only when no qualifying reply or connected call is evidenced.

### Why This Matters

Lucinda Gibson replied to Piper, exchanged multiple messages and completed two substantial calls, but the missing manual tag caused `MC: Financial` to classify her as not contacted and send a message in Megan's name. The replacement control prevents this false escalation while preserving early-retention follow-up and management visibility for genuine no-response cases.

---

## Current State

### Relevant Existing Structure

- `outputs/systems/cancellation-system.md` documents the published cancellation workflows and task routing.
- `outputs/systems/cancellation-mc-reason-workflows.md` is the detailed build specification for the eight Piper-led reason workflows and the separate booked-manager-call workflow.
- GHL folder `7. Cancellation System` contains nine published `MC:` workflows.
- `MC: Financial` currently has three active enrolments and uses `cs: contact made` at the 24-hour, 48-hour and Day 5/14 routing checks.
- Live GHL conversation evidence for Lucinda shows member replies, an 8-minute call and a 5-minute call, while her contact lacks `cs: contact made`.
- `context/decision-log.md` records material owner changes to live-system behaviour.
- `context/roadmap.md` currently marks cancellation core triggers Live without recording the contact-evidence defect.

### Gaps or Problems Being Addressed

- One manual tag is treated as stronger than the actual conversation record.
- GHL `Completed` call status alone can include ambiguous calls and cannot safely prove live contact.
- The Day 14 path automatically sends client-facing copy in Megan's name without a final evidence review.
- Active notice-period contacts may already be travelling through the incorrect no-contact branch.
- The current specification does not define automatic contact evidence, minimum call duration or an owner-review-only escalation.

---

## Proposed Changes

### Summary of Changes

- Add automatic member-reply evidence for active membership cancellations.
- Add conservative connected-call evidence for outgoing calls of at least 60 seconds when the live GHL trigger supports a duration condition.
- If GHL cannot express duration safely, leave call evidence out of the native writer and retain member replies as the automatic signal; ambiguous calls route to review rather than client messaging.
- Keep `cs: contact made` as a compatibility tag, but permit only automation or an explicit owner correction to write it.
- Add auditable retention-contact fields if the live field library does not already contain equivalent governed fields.
- Add a final contact-evidence gate before owner escalation.
- Replace automatic Day 14 Megan SMS actions with one internal Megan review task.
- Reconcile currently active notice-period contacts from their complete conversation histories.
- Test all branches without delivering messages to real members.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `plans/2026-08-04-cancellation-contact-evidence-and-owner-escalation.md` | Approved implementation and acceptance plan. |
| `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md` | Live build record, controlled-test evidence and final workflow identifiers. |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `outputs/systems/cancellation-system.md` | Define authoritative automatic contact evidence, the 60-second conservative call rule, the review-only owner escalation and current live status. |
| `outputs/systems/cancellation-mc-reason-workflows.md` | Replace manual-tag-only branch rules and the automatic owner SMS specification. |
| `outputs/systems/ghl-backend-register.md` | Register the new helper workflows, owner, purpose, trigger, dependencies and review rule. |
| `context/decision-log.md` | Record Peter's owner approval of automatic evidence and review-only Megan escalation. |
| `context/roadmap.md` | Move the cancellation contact-evidence repair through In Progress to Live after acceptance. |
| `context/control-plane-status.md` | Add only a share-safe completion signal if the build reaches verified Live state. |

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Observable evidence outranks a manual tag:** A member reply during an active cancellation notice is automatic contact evidence.
2. **`Completed` alone is insufficient call evidence:** Only a safely expressible completed/answered outgoing call with duration at least 60 seconds may automatically count.
3. **Compatibility without human dependency:** Existing `cs: contact made` checks remain usable, but helper workflows write the tag automatically.
4. **Absence cannot directly authorise client messaging:** The Day 14 no-contact path creates an internal Megan review task; it does not send a client SMS.
5. **Booked-manager-call remains separate:** `MC: Other (Booked Call)` already represents an explicit management-contact request and is not converted into the Piper no-contact pathway.
6. **Fail closed:** If live GHL cannot filter call duration reliably, calls do not automatically set contact evidence in the native workflow.
7. **No real-member testing:** Controlled tests must not send new client-facing messages to existing members.

### Alternatives Considered

- Requiring Piper to select a call disposition was rejected because it recreates the same human dependency.
- Treating every `Completed` call as answered was rejected because short calls and voicemail routing can be misclassified.
- Enabling global Stop on Response was rejected because it may terminate useful mid-notice branches.
- A new Railway GHL writer was rejected for this build because the approved Hub workflow-extension boundary currently permits internal tasks only and has not authorised contact-field mutations.

### Open Questions (if any)

None. The owner approved the recommended automatic-evidence and review-only escalation design on 4 August 2026. Live duration-filter capability is an implementation discovery with an explicit fail-closed fallback.

---

## Step-by-Step Tasks

### Step 1: Capture the Live Baseline

Record the exact published workflow versions, active enrolments, existing `cs: contact made` branch locations, Day 14 owner actions and currently active notice-period contacts.

**Actions:**

- Read all nine `MC:` workflows in folder `7. Cancellation System`.
- Confirm that the eight Piper-led workflows share the same escalation skeleton.
- Record active enrolment counts before any change.
- Read the complete conversation, task, note, field and opportunity record for each active notice-period contact.

**Files affected:**

- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 2: Update the Canonical Specification

Define the approved evidence hierarchy and owner-review rule before changing GHL.

**Actions:**

- Add automatic member-reply evidence.
- Add the conservative 60-second outgoing connected-call rule and fail-closed fallback.
- Specify that automation owns the compatibility tag.
- Replace the automatic Megan SMS with an internal task specification.
- Record the owner decision.

**Files affected:**

- `outputs/systems/cancellation-system.md`
- `outputs/systems/cancellation-mc-reason-workflows.md`
- `context/decision-log.md`

---

### Step 3: Create or Reuse Contact-Evidence Fields

Use existing governed fields if exact equivalents exist; otherwise create the minimum new fields.

**Actions:**

- Create `CS: Retention Contact Evidence` as a single-option field with `Awaiting contact`, `Member replied`, `Call connected`, `No response - owner review`, `Saved`, and `Continuing cancellation`.
- Create `CS: Retention Contact Date` as a date field if no exact scoped date field exists.
- Re-read the field definitions and record their IDs.

**Files affected:**

- `outputs/systems/cancellation-system.md`
- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 4: Build Automatic Member-Reply Evidence

Create one helper workflow in `7. Cancellation System`.

**Actions:**

- Trigger on Customer Replied with re-entry enabled.
- Continue only for Membership cancellations whose status is Notice Active and whose Cancellation OS opportunity remains in Notice Period (Current).
- Add `cs: contact made`.
- Set evidence to `Member replied` and write the contact date.
- Do not send a client message.
- Keep the workflow Draft until controlled acceptance passes.

**Files affected:**

- Live GHL workflow `CS: Contact Evidence - Member Replied`
- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 5: Build Conservative Connected-Call Evidence

Inspect the live Call Details trigger before creating the writer.

**Actions:**

- Confirm whether direction, outcome and duration can all be filtered.
- If supported, trigger only for outgoing answered/completed calls of at least 60 seconds during an active membership cancellation notice.
- Add `cs: contact made`, set `Call connected`, and write the date.
- If duration is unavailable, do not publish a call-evidence writer and record the limitation; ambiguous calls will remain subject to Megan's internal review.

**Files affected:**

- Live GHL workflow `CS: Contact Evidence - Connected Call`, only if the safety condition is expressible
- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 6: Repair the Eight Piper-Led Reason Workflows

Update Financial first, validate the structure, then cascade the same safety gate to Moving/Travel, Schedule/Time, Health/Injury, Results/Value, New Gym, New Style and Other.

**Actions:**

- Initialise contact evidence to `Awaiting contact` without erasing later automatic evidence.
- Preserve existing automatic tag checks for compatibility.
- Add a final evidence check immediately before owner escalation.
- Replace Step 14 automatic Megan SMS with one task assigned to Megan:
  `OWNER REVIEW: No verified cancellation contact - {{contact.name}}`.
- Include the reason, notice dates and an instruction to review the complete conversation and call history before deciding whether to contact the member.
- Preserve `MC: Other (Booked Call)` as the separate explicit manager-call path.

**Files affected:**

- Eight live published `MC:` reason workflows
- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 7: Reconcile Active Notice-Period Contacts

Prevent existing in-flight contacts from receiving a false owner escalation.

**Actions:**

- Review every currently active cancellation notice.
- Set automatic-equivalent evidence only where the conversation record proves a member reply or a qualifying connected call after submission.
- For Lucinda Gibson, record `Member replied` because multiple inbound replies exist; add the compatibility tag and preserve the current notice period.
- Do not change billing, access, appointments or cancellation dates.
- Read back every changed contact.

**Files affected:**

- Live GHL contact fields/tags
- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 8: Controlled Acceptance Tests

Test without messaging real members.

**Actions:**

- Member reply evidence: verify automatic tag and field update.
- Long connected-call evidence: verify only if the safe duration rule is available.
- Short/ambiguous completed call: verify no automatic contact evidence.
- No reply/no call: verify exactly one internal Megan task and zero client messages.
- Duplicate qualifying event: verify idempotent evidence and no duplicate open review task.
- Delete or retire disposable test records after read-back.

**Files affected:**

- `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`

---

### Step 9: Publish and Verify the Cascade

Publish only controls that passed acceptance.

**Actions:**

- Publish the helper workflow or workflows.
- Publish the repaired eight reason workflows.
- Reload each workflow and verify status, trigger, branch and absence of automatic Day 14 owner SMS.
- Update the backend register, roadmap, plan status and share-safe control-plane status.
- Confirm no unrelated workflows, contacts, billing or access records changed.

**Files affected:**

- `outputs/systems/ghl-backend-register.md`
- `context/roadmap.md`
- `context/control-plane-status.md`
- `plans/2026-08-04-cancellation-contact-evidence-and-owner-escalation.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `outputs/systems/membership-lifecycle.md`
- `outputs/systems/membership-hold.md`
- `context/policies.md`
- `outputs/systems/workflow-extension-registry.md`
- `context/roadmap.md`
- `outputs/systems/ghl-backend-register.md`

### Updates Needed for Consistency

- Cancellation documentation must no longer instruct Piper to apply the tag as the primary evidence.
- Backend registration must list the helper workflow owner, trigger and retirement rule.
- The Hub workflow-extension registry remains unchanged because this build does not add a Railway writer.
- The member policy and 30-day notice rules remain unchanged.

### Impact on Existing Workflows

The eight Piper-led reason workflows retain their reason-specific offers and notice-period timing. Only contact-evidence capture and the Day 14 escalation side effect change. The main cancellation intake, Billing OS, cancellation workbook, Stripe scheduling, PT cancellation and booked-manager-call paths are not changed.

---

## Validation Checklist

- [x] Canonical documentation records automatic evidence before live mutation.
- [x] Member replies during an active membership cancellation automatically set contact evidence.
- [x] Calls count automatically only when direction, outcome and at least 60 seconds are safely expressible; GHL lacks duration, so no call writer was published.
- [x] `Completed` alone never sets contact evidence.
- [x] All eight Piper-led workflows retain the governed contact-evidence gates before owner escalation.
- [x] No Day 14 pathway sends an automatic client SMS in Megan's name.
- [x] Genuine no-contact cases create one same-day Megan review task.
- [x] Lucinda and every active notice-period contact are reconciled from complete conversation evidence.
- [x] Structural reply, ambiguous-call, no-contact and duplicate-safe controls were verified without sending a test message to a real member.
- [x] Published workflows are reloaded and verified.
- [x] Main cancellation, billing, appointments, access and reporting remain unchanged.
- [x] Decision log, backend register, roadmap, plan and share-safe status agree.

---

## Success Criteria

The implementation is complete when:

1. A member reply can suppress a false no-contact escalation without Piper taking any administrative action.
2. A call cannot suppress escalation merely because its status is `Completed`.
3. Megan receives an internal review task rather than an automated client message for genuine no-contact cases.
4. All active notice-period contacts and all affected published workflows have been read back against the approved rule.
5. No client-facing test message is delivered to a real member.

---

## Notes

This change governs evidence and escalation only. It does not decide whether a member is saved, continuing cancellation, entitled, payment-current or ready for final access closure.
