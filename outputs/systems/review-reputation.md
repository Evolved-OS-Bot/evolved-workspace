# Review & Reputation Management System
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-24

---

## Overview

The live Review & Reputation workflow is a tag-triggered satisfaction and Google-review journey. A contact enters when `send review request` is added, waits 14 days, receives an SMS asking for a 1-to-5 response, and then follows a positive, negative, other-reply or no-response path.

Only a positive 4- or 5-star reply receives the Google review request. Lower ratings stay inside the feedback and service-recovery journey. The Review Pipeline records the major states, while the workflow also contains reminder, check-in and thank-you actions.

---

## Pipeline: Review Pipeline
**Pipeline ID:** `Nf20o5WaCQTpWZPAtUn6`

| Position | Stage | ID |
|---|---|---|
| 0 | Review Requested | `2cc9c164-4561-422e-b051-f36212576bc3` |
| 1 | Negative Response | `16ac1951-7ed0-4811-bdc7-8bfe6b6bc259` |
| 2 | Positive Response | `1e68e800-8ea2-4742-94a7-043da25b5120` |
| 3 | Trigger Link Clicked | `a36717f3-02e3-4d1a-95f0-4acfea4948fd` |
| 4 | Review Received | `e5ab2e8d-0b30-40a1-9c48-3ce88e5e096b` |

The pipeline uses a branching structure: after the review request is sent, contacts are routed to either Negative Response or Positive Response depending on the star rating captured. Positive contacts who click the Google Review link advance to Trigger Link Clicked, and once the review is confirmed received, they move to Review Received.

---

## Tags

| Tag | Purpose |
|---|---|
| `send review request` | Durable marker that starts the member-feedback journey. It is added during new-member onboarding, before the member supplies the 1-to-5 rating. |

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Google Review Request (4 & 5 Stars Only) | **published** | `ebbd43c1-4e39-4731-a3e3-c7e5f0bfae0b` |

Only one review-specific workflow is present. It is published and enters contacts when the `send review request` tag is added. The 4- or 5-star gate happens after the workflow asks for feedback; it is not the enrolment trigger.

The workflow contains both positive and negative handling. The live builder shows opportunity updates, an improvement-request SMS for negative responses, a Google-review SMS for positive responses, trigger-link tracking, follow-up checks and thank-you messages.

---

## Forms / Surveys

GHL contains an exit-rating field inside the **PT Cancellation Form** (Survey ID: `JnwGk9ttNxiSAuqBxuBs`), but the live review workflow does not enrol from that field or survey. It enrols from the `send review request` tag and collects the operative 1-to-5 response by SMS after the 14-day wait.

Two live onboarding workflows are confirmed upstream sources:

- `3.0 New Member`: active membership branches add the action labelled `Add 'Review Request' Tag`.
- `3.1. New Personal Training Client`: the live builder also contains `Add 'Review Request' Tag` before its First 7 Days handoff and opportunity action.

The tag can also be added manually by staff. No other automation source has been confirmed.

---

## Calendars

No dedicated calendars are associated with this system. Negative response handling does not appear to route to an escalation calendar; the separate Cancellation system has its own manager pathway.

---

## Custom Fields

### Rating / Satisfaction Fields
**Field Group:** `JwbflBU2YDUaZb9godHU`

| Field | Type | Key | ID |
|---|---|---|---|
| Overall out of 5 stars how would you rate... | RADIO | `contact.overall_out_of_5_stars_how_would_you_rate` | `pzDHsfSCxFQ1zoWDLHUf` |
| Did you achieve the result you wanted to... | RADIO | `contact.did_you_achieve_the_result_you_wanted_to_` | `muAXpBFZYKZuibhy5HLQ` |
| Have you communicated any and all struggles... | RADIO | `contact.have_you_communicated_any_and_all_struggl` | `vqk71JXGlQmLlCQrkNJ6` |
| Have you given yourself enough time to... | RADIO | `contact.have_you_given_yourself_enough_time_to_ac` | `7M8HMiRkBlgNLiAGmfys` |
| What did you achieve in your time at The... | LARGE_TEXT | `contact.what_did_you_achieve_in_your_time_at_the_` | `2IaeuOSVg61BGYKdyEOk` |
| Why are you cancelling your personal training... | LARGE_TEXT | `contact.why_are_you_cancelling_your_personal_trai` | `9fiifVeY7EhdbwKtuLrQ` |
| Other: if you're comfortable sharing please... | TEXT | `contact.other_if_yourre_comfortable_sharing_pleas` | `hzzfBiZvBy9zR3Mtefzh` |
| How long have you been a member of The... | RADIO | `contact.how_long_have_you_been_a_member_of_the_ev` | `6rExWm1aw9kuWNFuwfBW` |
| Have you utilised the Smart Meal Plan... | RADIO | `contact.have_you_utilised_the_smart_meal_plan_hig` | `S8QEHcZ7yCJJ4XuzbFUH` |

**Star Rating Field Options:**
`Overall out of 5 stars how would you rate...` (`pzDHsfSCxFQ1zoWDLHUf`)
- 1 star
- 2 stars
- 3 stars
- 4 stars
- 5 stars

**Did you achieve the result you wanted...** (`muAXpBFZYKZuibhy5HLQ`)
- Yes
- No

**Have you communicated any and all struggles...** (`vqk71JXGlQmLlCQrkNJ6`)
- Yes
- No

**Have you given yourself enough time...** (`7M8HMiRkBlgNLiAGmfys`)
- Yes
- No

**How long have you been a member...** (`6rExWm1aw9kuWNFuwfBW`)
- Less than 3 months
- Less than 6 months
- More than 6 months
- More than 12 months

**Have you utilised the Smart Meal Plan...** (`S8QEHcZ7yCJJ4XuzbFUH`)
- Yes
- No

> Note: These fields are housed in the same field group as PT cancellation health screening questions (PAR-Q style fields) and the MC: Reason / PT cancellation fields. The group `JwbflBU2YDUaZb9godHU` is a mixed-purpose group serving both the PT Cancellation Form and exit/satisfaction capture.

---

## Custom Values

| Name | Key | Value |
|---|---|---|
| Google Review Link | `{{ custom_values.google_review_link }}` | `https://search.google.com/local/writereview?placeid=ChIJOSoY...` |

The Google Review Link custom value stores the direct write-a-review URL for the business's Google Business Profile. This is the URL delivered to 4 and 5 star respondents via the `Google Review Request (4 & 5 Stars Only)` workflow.

The full Place ID begins with `ChIJOSoY` — the value is truncated in the source documentation.

---

## Step-by-Step Flow

```
1. Upstream process or staff action adds tag: send review request
2. Google Review Request workflow enrols the contact
3. Workflow waits 14 days
4. Workflow creates or updates the Review Pipeline opportunity
5. SMS asks the contact to reply with a rating from 1 to 5
6. Workflow waits up to 24 hours for a reply
7. Reply is classified:
   - 1, 2 or 3: negative path, opportunity update, improvement question and follow-up logic
   - 4 or 5: positive path, opportunity update and Google review request
   - other reply: separate handling path
   - no reply: timeout path
8. Positive path watches for the Google review trigger-link click
9. Workflow updates the opportunity and continues its check-in or thank-you path
10. The workflow finishes without removing `send review request`
```

Live enrollment history on 24 July 2026 confirmed ongoing production use through June and July. Several contacts were actively waiting at the initial 14-day delay, while completed contacts had progressed through later workflow actions.

`Allow re-entry` is enabled, but the trigger is specifically the tag being added. Because the workflow does not remove the tag, re-entry will only occur if staff or another controlled process first removes it and later adds it again. For the current one-time new-client review journey, this durable-tag behaviour is an effective duplicate-send control.

### Drive fallback procedure

The Drive Admin Reviews folder contains one short exception note: `Failed Review Link: Send This`. It tells Admin to manually send the Google review request when a member replies 4 or 5 and the automated message fails.

The exception purpose is valid, but the note uses a hard-coded short link and does not require checking the workflow execution log first. Retain the fallback concept, then rewrite it to: confirm the positive reply, verify the failed or skipped action in GHL, send the canonical review link, record the manual intervention and avoid sending a duplicate request.

---

## System Notes & Observations

### What's working well
- **Gated review request** keeps the public request on the positive-response path while capturing lower ratings internally.
- **The workflow is actively used** and has current contacts progressing through the initial waiting period.
- **Positive and negative handling exist in one controlled journey**, including improvement questions, reminders, link-click tracking and thank-you actions.
- **Pipeline stages provide reporting checkpoints** for requested, negative, positive, clicked and received states.
- **Tag-based entry** allows multiple upstream member moments to use the same review journey once the tag sources are governed.

### Current gaps / things to review
- **Tag provenance and current duplicate control are documented:** `3.0 New Member` and `3.1. New Personal Training Client` are the confirmed automation sources. Manual addition remains possible. The retained tag makes the current onboarding review journey effectively one-time.
- **Future repeat-review cycles need deliberate governance:** if milestone review requests are introduced, remove and re-add the tag only through a controlled workflow with a defined cooldown and eligibility rule.
- **Workflow name is misleading:** it describes only the positive branch, although the workflow first collects ratings and handles negative feedback too. A clearer name would be `Member Feedback & Google Review Journey`.
- **Drive fallback uses a hard-coded link:** replace it with the canonical GHL review-link source and an execution-log verification step.
- **Review received verification has a named owner:** a trigger-link click proves intent, not publication. Admin Eve checks the Google Business Profile once weekly and moves only visibly published reviews to `Review Received`; Piper remains the personal member-experience follow-up owner. AI sentiment and link clicks are triage signals only.
- **The existing review pipeline has a reconciliation backlog:** live inspection on 30 July 2026 found 117 opportunities at Review Requested, 3 at Negative Response, 63 at Positive Response, 0 at Trigger Link Clicked and 10 at Review Received. Reconcile this gradually through the weekly verification control; do not bulk mark positive responses as published reviews.
- **One workflow remains a concentration risk:** keep a monitoring owner and periodic test because pausing or breaking this workflow stops the whole review journey.
- **Testimonial handoff is not visible:** a verified 5-star result could feed the member-story system, subject to consent and deduplication.
