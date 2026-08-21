# Milestone T-Shirt Order Form — GHL Build Spec

**Live status corrected 31 July 2026:** This is a newly structured form, so zero stored values across the audited fields are expected before genuine submissions and are not evidence of obsolescence. Complete public-form inspection confirmed milestone, shirt/singlet, size, experience rating, feedback, Google-review status and the referral question. The Friend 1–5 contact fields are intended to be conditional and hidden until the referral branch is selected; they are not duplicates or cleanup candidates.

No matching milestone, referral or T-shirt workflow appears in the live workflow register. The remaining work is to validate the complete conditional branch and build or locate the processing layer that owns fulfilment, staff notification, referral handling, review handoff and the workflow-output fields `Milestone T-Shirt Last Ordered` and `Member Referral Count`. The Privacy Policy and Terms links still point to `example.com` and must be corrected before distribution.

**Controlled test completed 31 July 2026:** Selecting `Yes` revealed Friend 1; entering each friend name revealed the next fields through Friend 5. A controlled submission stored all 22 entered values on the submitting contact, including milestone, style, size, 5-star rating, feedback, Google-review status and all five friends' names, emails and mobiles.

No referral contacts, tag, task, note, appointment, opportunity or conversation were created. `Milestone T-Shirt Last Ordered` and `Member Referral Count` remained blank. The test contact was deleted and a fresh complete contact read-back verified it absent.

**Location:** GHL > Forms > Member Experience > Milestone T-Shirt Order Form
**Workflow:** GHL > Workflows > Member Experience > Milestone T-Shirt — Smart Routing
**Pipeline:** GHL > Pipelines > Milestone T-Shirt Orders

---

## Step 1: Create Custom Contact Fields

The design created 23 fields through the API. Retain them while the new form and referral routing are completed and tested. Form-input fields and workflow-output fields serve different purposes, so zero population before launch is not a deletion signal.

### Milestone & Satisfaction Fields

| Field Label | GHL Field ID |
|---|---|
| Milestone T-Shirt Earned | `mSx1t7C8nl8MG4md0eg4` |
| Milestone T-Shirt Last Ordered | `oO5rodSGwrM4SHgGdO6h` |
| Milestone T-Shirt Size | `zfwzD2lWH52PUU132tZb` |
| Milestone T-Shirt Style | `FR3Jlfx7j9eWYQ5gCplV` |
| Member Satisfaction Rating | `ElQN5Sr7zMBkE4jNN5k1` |
| Member Google Review Left | `yIeZjXjFUlbBgTljFJRr` |
| Milestone Feedback Notes | `SsJ6NJS3lAJKTQzzjdm8` |
| Member Referral Count | `bHSRLKNohzm3fOCt28El` |

### Referral Fields (Friends 1–5)

| Field Label | GHL Field ID |
|---|---|
| Referral 1 Name | `1mBmbzBFmE5lg7ZpkviH` |
| Referral 1 Email | `ks9CPaeiDcKAM5xI8Yvb` |
| Referral 1 Mobile | `vqBiuYOG9zWeyuXAa1Hg` |
| Referral 2 Name | `GBrQ5eGbvSLdF7tbaRO1` |
| Referral 2 Email | `fgBI5rUFRyn05TcPlcg9` |
| Referral 2 Mobile | `WsafWD6C9bVHA9MTCgaG` |
| Referral 3 Name | `5S1x9ds4yws7OSa9US1R` |
| Referral 3 Email | `iDPMLUeW2oMrfjUQDyN9` |
| Referral 3 Mobile | `Q3Y5IsjgBodOEhbHwGUJ` |
| Referral 4 Name | `iP6KSvXiDQqw7wZtXJYi` |
| Referral 4 Email | `3AcYnX83i50AYpQQkkGJ` |
| Referral 4 Mobile | `9UfbxgXj4cXDmQa8aLFr` |
| Referral 5 Name | `zmEZnxqBh4fSa4J2zJm9` |
| Referral 5 Email | `XwlZ3QWZBHNWCdIRTB88` |
| Referral 5 Mobile | `m2lGEwHKRh4AmA4EjcEQ` |

---

## Step 2: Build the Form

Go to: Sites > Forms > New Form > Name: "Milestone T-Shirt Order Form"

Build fields in this exact order. Fields marked HIDDEN start hidden — conditional logic reveals them.

---

### Section: Your Milestone

| # | Field Label | Field Type | Options / Notes | Required |
|---|---|---|---|---|
| 1 | Which milestone have you hit? | Dropdown | 100 / 200 / 350 / 500 / 750 / 1000 workouts | Yes |
| 2 | Shirt or singlet? | Dropdown | Shirt / Singlet | Yes |
| 3 | Size | Dropdown | XS / S / M / L / XL / XXL | Yes |

---

### Section: Your Experience

| # | Field Label | Field Type | Options / Notes | Required |
|---|---|---|---|---|
| 4 | How would you rate your experience at The Evolved? | Star Rating (1-5) | — | Yes |
| 5 | Tell us more | Text Area | Always visible | No |
| 6 | Have you left us a Google review? | Dropdown | Yes / Not yet | Yes |

---

### Section: Gift a Strength Assessment

Add a text block above field 7:
> "Do you have a friend who would love to try strength training? We would love to give you a Strength Assessment voucher to pass on — it is worth $150 and gets them a full one-on-one session with one of our coaches."

| # | Field Label | Field Type | Options / Notes | Required |
|---|---|---|---|---|
| 7 | Would you like to gift a voucher to a friend? | Dropdown | Yes — I'd love to / Not right now | Yes |

---

### Friend 1 — HIDDEN by default

| # | Field Label | Field Type | Required |
|---|---|---|---|
| 8 | Friend 1 — Name | Text | No |
| 9 | Friend 1 — Email | Email | No |
| 10 | Friend 1 — Mobile | Phone | No |

---

### Friend 2 — HIDDEN by default

| # | Field Label | Field Type | Required |
|---|---|---|---|
| 11 | Friend 2 — Name | Text | No |
| 12 | Friend 2 — Email | Email | No |
| 13 | Friend 2 — Mobile | Phone | No |

---

### Friend 3 — HIDDEN by default

| # | Field Label | Field Type | Required |
|---|---|---|---|
| 14 | Friend 3 — Name | Text | No |
| 15 | Friend 3 — Email | Email | No |
| 16 | Friend 3 — Mobile | Phone | No |

---

### Friend 4 — HIDDEN by default

| # | Field Label | Field Type | Required |
|---|---|---|---|
| 17 | Friend 4 — Name | Text | No |
| 18 | Friend 4 — Email | Email | No |
| 19 | Friend 4 — Mobile | Phone | No |

---

### Friend 5 — HIDDEN by default

| # | Field Label | Field Type | Required |
|---|---|---|---|
| 20 | Friend 5 — Name | Text | No |
| 21 | Friend 5 — Email | Email | No |
| 22 | Friend 5 — Mobile | Phone | No |

---

## Step 3: Conditional Logic Rules

Go to: Form builder > Conditional Logic tab. Add rules in this order.

### Rule 1 — Show Friend 1 fields
- IF: Field 7 (Gift a voucher?) is equal to "Yes — I'd love to"
- THEN: Show fields 8, 9, 10 (Friend 1 Name, Email, Mobile)

### Rule 2 — Show Friend 2 fields
- IF: Field 8 (Friend 1 Name) is not empty
- THEN: Show fields 11, 12, 13 (Friend 2 Name, Email, Mobile)

### Rule 3 — Show Friend 3 fields
- IF: Field 11 (Friend 2 Name) is not empty
- THEN: Show fields 14, 15, 16 (Friend 3 Name, Email, Mobile)

### Rule 4 — Show Friend 4 fields
- IF: Field 14 (Friend 3 Name) is not empty
- THEN: Show fields 17, 18, 19 (Friend 4 Name, Email, Mobile)

### Rule 5 — Show Friend 5 fields
- IF: Field 17 (Friend 4 Name) is not empty
- THEN: Show fields 20, 21, 22 (Friend 5 Name, Email, Mobile)

---

## Step 4: Build the Workflow

Go to: Workflows > New Workflow > Name: "Milestone T-Shirt — Smart Routing"

**Trigger:** Form submitted — select "Milestone T-Shirt Order Form"

---

### Branch A: Update submitting member's contact record

Actions (run for all submissions):

1. Update Contact Field: `milestone_tshirt_earned` — append value from Field 1
2. Update Contact Field: `milestone_tshirt_last_ordered` — set to today
3. Update Contact Field: `milestone_tshirt_size` — value from Field 3
4. Update Contact Field: `milestone_tshirt_style` — value from Field 2
5. Update Contact Field: `member_satisfaction_rating` — value from Field 4
6. Update Contact Field: `milestone_feedback_notes` — value from Field 5
7. Add Tag: `tshirt-order-pending`
8. Internal notification to Megan: "New t-shirt order — [Contact Name], [Milestone], [Style], [Size]"

---

### Branch B: Satisfaction routing (add If/Else branch after Branch A)

**IF rating (Field 4) is greater than or equal to 4 AND Field 6 = "Not yet":**
- Send email/SMS: Google review request
- Subject: "One more thing — would you mind sharing your experience?"
- Body: Include Google review link. Lead with their milestone achievement, not a generic ask.

**IF rating = 3:**
- Add Tag: `feedback-neutral`
- Internal note to Megan: "Neutral score — [Contact Name] — check in at next session"

**IF rating is less than or equal to 2:**
- Add Tag: `feedback-flagged`
- Add Tag: `retention-red-flag`
- Internal alert to Megan: "Low score — [Contact Name] — [their feedback notes] — follow up urgently"
- Create Task: "Follow up [Contact Name] — low satisfaction score"

---

### Branch C: Referral contact creation (run once per friend whose name is not empty)

For each friend, add an If/Else branch:

**Friend 1 — IF Field 8 (Friend 1 Name) is not empty:**
1. Create Contact:
   - First Name: Friend 1 Name (Field 8)
   - Email: Friend 1 Email (Field 9)
   - Phone: Friend 1 Mobile (Field 10)
   - Tag: `sa-referral`
   - Source: Milestone Referral
   - Custom note: "Referred by [submitting member name]"
2. Trigger: SA Referral email sequence (first email references referring member by name)
3. Update submitting member: `member_referral_count` +1

Repeat this block for Friends 2, 3, 4, 5 using their respective fields (11-13, 14-16, 17-19, 20-22).

---

### Branch D: Pipeline (optional — for fulfilment tracking)

Add to Pipeline: Milestone T-Shirt Orders
- Stage: Order Received
- Opportunity Name: [Contact Name] — [Milestone] [Style] [Size]

When t-shirt is fulfilled:
- Move to Stage: Fulfilled
- Update Contact Field: `tshirt-order-pending` tag removed, add tag `tshirt-order-fulfilled`

---

## Step 5: SA Referral Email Sequence

Create a separate workflow or email template triggered when a referral contact is created with tag `sa-referral`.

**Email 1 — sent immediately:**
- From: The Evolved
- Subject: "[Referring Member Name] wanted you to have this"
- Body: Lead with the referring member's name. Frame it as a gift from someone they know. Include SA booking link. Do not open with The Evolved's branding.

**Email 2 — sent 3 days later if no booking made:**
- Gentle reminder. Mention the voucher expires in [X] days.

**Email 3 — sent 7 days later if still no booking:**
- Final nudge. Offer to answer any questions.

---

## Notes

- All referral fields are optional — they must not block form submission if left empty.
- The form should be accessible via a direct GHL link sent to the member when their milestone is recorded (or via QR code at the gym).
- The SA referral email must lead with the referring member's name, not The Evolved branding, to avoid feeling like a cold marketing email.
- Google review gating (only sending happy members to Google) is technically against Google's ToS. Frame the Google step as an additional optional action rather than a gate.

## Current completion gate

Before distributing the form:

1. **Completed:** the controlled referral-branch submission proved all five conditional levels reveal and all 22 entered values persist.
2. Confirm or build the matching workflow and its exact trigger.
3. Assign the T-shirt fulfilment handoff and referral follow-up to named staff accounts.
4. Verify `Milestone T-Shirt Last Ordered` and `Member Referral Count` are updated by workflow logic rather than left stale.
5. Reconcile Google-review handling with the governed review system so the milestone form does not create repetitive or sentiment-gated messaging.
6. Replace both `example.com` footer links with the approved legal destinations.
