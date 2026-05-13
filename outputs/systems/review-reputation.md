# Review & Reputation Management System
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-01

---

## Overview

The Review & Reputation Management system captures member satisfaction via an in-house star rating at the point of exit (PT cancellation form), then routes positive responses (4 and 5 stars) into an automated Google Review request sequence. The pipeline tracks progress from initial review request through to confirmed review receipt, with branching stages for negative and positive responses.

The system is intentionally gated — only members who rate 4 or 5 stars receive the Google Review request. This protects the public rating profile and ensures that negative feedback is captured internally rather than directed to Google.

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
| `send review request` | Applied to contacts who qualify to receive a review request (4 or 5 star rating) |

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Google Review Request (4 & 5 Stars Only) | **published** | `ebbd43c1-4e39-4731-a3e3-c7e5f0bfae0b` |

Only one review-specific workflow is present. It is live/published and triggers exclusively for contacts who submit a 4 or 5 star rating. The workflow is expected to move the contact into the Review Pipeline (stage: Review Requested) and send the Google Review link.

No separate workflow exists for the negative response path — this suggests negative feedback handling is either manual or managed via pipeline stage assignment only.

---

## Forms / Surveys

The star rating that gates this system is captured inside the **PT Cancellation Form** (Survey ID: `JnwGk9ttNxiSAuqBxuBs`), not a standalone review request form. There is no dedicated review or NPS survey in the account.

The rating field sits alongside PT cancellation fields and exit feedback questions within the same custom field group (`JwbflBU2YDUaZb9godHU`).

---

## Calendars

No dedicated calendars are associated with this system. Negative response handling does not appear to route to a booked call or escalation calendar (unlike the Cancellation system's `MC: Other` pathway).

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
1. Member submits PT Cancellation Form (Survey ID: JnwGk9ttNxiSAuqBxuBs)
2. Form captures star rating → "Overall out of 5 stars how would you rate..." (pzDHsfSCxFQ1zoWDLHUf)
3. Also captures exit feedback: achievements, reason for leaving, tenure, resource utilisation

4. IF rating = 4 stars OR 5 stars:
   → Tag applied: "send review request"
   → Workflow fires: "Google Review Request (4 & 5 Stars Only)" (ebbd43c1-...)
   → Contact enters Review Pipeline → Stage: Review Requested (2cc9c164-...)
   → Contact receives message with Google Review Link ({{ custom_values.google_review_link }})

5. IF contact clicks the Google Review link:
   → Pipeline stage advances to: Trigger Link Clicked (a36717f3-...)

6. IF review is confirmed received:
   → Pipeline stage advances to: Review Received (e5ab2e8d-...)

7. IF rating = 1, 2, or 3 stars:
   → Contact moves to pipeline stage: Negative Response (16ac1951-...)
   → No automated Google Review request sent
   → Negative feedback is captured internally only

8. Positive responses that do not click the link remain:
   → Pipeline stage: Positive Response (1e68e800-...)
   → Presumably subject to follow-up or left in stage for manual review
```

---

## System Notes & Observations

### What's working well
- **Gated review request** is the right approach — only routing 4 and 5 star respondents to Google protects the public profile from unmanaged negative reviews
- **Exit feedback embedded in PT Cancellation Form** is efficient — the rating is captured at the highest-intent moment (point of departure), maximising completion rates
- **Pipeline structure clearly separates sentiment paths** — Negative Response and Positive Response are distinct stages, making it easy to see the split at a glance
- **"Trigger Link Clicked" stage** provides a measurable midpoint between intent (positive response) and action (confirmed review), enabling follow-up on drop-off
- **Tag `send review request`** enables filtering and reporting on who has been asked for a review without relying solely on pipeline stage

### Current gaps / things to review
- **Rating capture is tied solely to PT cancellation** — there is no review request pathway visible for SGPT/membership cancellations or for active members mid-lifecycle (e.g. milestone moments like 90 days, 6 months, 1 year). The majority of members who have a good experience and leave naturally may never be asked for a review
- **No negative response follow-up workflow visible** — contacts who rate 1–3 stars enter the Negative Response pipeline stage but there is no workflow handling this path. No internal notification, no manager alert, no recovery sequence. This is a significant gap for service recovery
- **Positive Response stage has no visible automation** — contacts who rate 4–5 stars but don't click the Google Review link remain in the Positive Response stage. There is no visible reminder or re-nudge sequence to recover these
- **Review confirmed (Review Received) has no visible downstream automation** — once a review is received there is no workflow that thanks the member, logs the outcome, or triggers any further action. A thank-you message would reinforce the behaviour
- **No NPS or mid-lifecycle satisfaction survey** — the system only captures satisfaction at cancellation. There is no proactive check-in for active members, no early warning system for at-risk members, and no structured mechanism to identify promoters before they decide to leave
- **Google Review Link value is truncated in documentation** — the full Place ID (`ChIJOSoY...`) should be verified to ensure the link resolves correctly
- **One workflow only, currently published** — the single `Google Review Request` workflow carries the full weight of this system. If it breaks or is accidentally paused, the entire review generation process stops with no fallback
- **No testimonial or case study capture pipeline** — highly satisfied members (5 stars) could be automatically routed into a testimonial or social proof request sequence, but no such workflow exists
