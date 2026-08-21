# SOP: Week-5 Subscription Activation

**System:** Brown & Casserly Pty Ltd 2026, GHL and Stripe  
**Process Owner:** To confirm  
**Exception Owner:** Admin Eve  
**Status:** Live manual process; automation pending  
**Version:** 1.7  
**Last Updated:** 30/07/2026

---

## Purpose

Start each new member's recurring Stripe subscription during her fourth membership week. The first recurring debit funds her fifth week of service.

This control prevents a member from continuing beyond the four-week upfront term without a scheduled recurring subscription.

---

## Source Records

| Question | Source |
|---|---|
| Who requires review? | `Brown & Casserly Pty Ltd 2026`, `Sales` tab |
| Has the subscription been set up? | `Sales` column R, `Debits Set Up` |
| What membership is current? | GHL contact membership field and current lifecycle state |
| What weekly amount was agreed? | GHL field `Regular weekly debit amount (starts in week 4 for week 5)` |
| What date did the member choose? | GHL field `First Debit Date Is` |
| When did service actually begin? | Confirmed GHL Intro Session, onboarding or KickStart appointment and other approved start evidence |
| Is billing already scheduled or collecting? | Stripe customer, subscriptions and schedules |
| Are there holds or plan changes? | GHL hold and membership-change records |

The Sales row is the batch trigger and completion record. GHL is the authority for the member's current plan, weekly amount, first debit date and lifecycle exceptions.

Stripe is the authority for whether a subscription is already scheduled or collecting.

---

## Membership Mapping

| Sales tab value | Current membership | Current weekly debit |
|---|---|---:|
| Fit & Flexible | Fit & Flexible | $69 |
| Bronze | Strong, Fit & Flexible Membership | $99 |
| Silver | Fast Track Package | $149 |

The Sales tab may retain the historical Bronze and Silver names. Do not create a subscription from the historical label alone when GHL records a later plan change.

---

## Date Rules

### Official Membership Weeks

The four-week upfront term normally begins on the Monday following payment. Week 4 begins 21 days after that Monday.

Example: a member pays on Friday 3 July 2026. Her official weeks begin on Monday 6 July, and week 4 begins on Monday 27 July.

A confirmed Intro Session, onboarding or KickStart appointment can establish the actual service start. The calendar week containing that confirmed session counts as week 1, even when the session occurs after Monday. Week 4 therefore begins on the Monday 21 days after the Monday of the session's calendar week.

When the Intro or onboarding date alone does not establish meaningful service use, use retained past Trainerize class bookings or tracked gym workouts as supporting evidence. The calendar week containing the first confirmed meaningful use counts as week 1.

Example: Tara Berge's confirmed onboarding appointment with Piper on Monday 6 July 2026 established 6 July as her actual start. She entered week 4 on Monday 27 July, so her subscription was due for an immediate charge when reviewed on 29 July rather than a future start on 3 August.

Example: Sarah Loga's confirmed Intro Session with Piper on Tuesday 14 July 2026 means the week beginning Monday 13 July counts as week 1. Her week 4 begins Monday 3 August 2026, so her first A$99 weekly debit was scheduled for that date.

Example: Jade Wright's first confirmed meaningful gym use was her retained Sculpt & Strength class booking on Sunday 26 July 2026. That made 20–26 July her first service week. Her four prepaid weeks ended Sunday 16 August, so her first A$99 weekly debit was scheduled for Monday 17 August 2026.

### Subscription Start Date

Use the exact date stored in GHL `First Debit Date Is` when it is present and consistent with the approved membership state.

When that field is blank, check for a confirmed Intro Session, onboarding or KickStart appointment and other approved evidence of the actual service start. Count the session's calendar week as week 1. If the member is already in week 4 when reviewed, create the subscription to bill immediately on the review date unless an approved later debit date applies.

Only when the preferred debit date and actual service-start evidence are both unavailable, and there is no delayed-start, hold or plan-change exception, use the payment weekday four weeks after payment. The fallback calculation is:

`Sales payment date + 28 calendar days`

Example: Jess Michels paid on Friday 3 July 2026. With no preferred date or exception, her subscription start date is Friday 31 July 2026.

### Delayed Starts

Delayed starts are currently communicated verbally. This is not safe enough for unattended automation.

Before automation, every delayed start must be stored in a structured GHL date field or routed to a human exception queue. Do not calculate a fallback date when there is known verbal evidence of a different start.

---

## Batch Procedure

### 1. Build the Candidate List

Open the `Sales` tab and identify membership rows where column R, `Debits Set Up`, is unchecked.

Prioritise members who have entered week 4, whose preferred first debit date is approaching, or whose calculated fallback date has passed.

### 2. Reconcile the Member

Open the GHL contact using the exact email address from the Sales row. Confirm the current membership, agreed weekly debit, `First Debit Date Is`, actual Intro Session, onboarding or KickStart appointment, and any hold, delayed-start, cancellation or plan-change evidence.

If the Sales row and GHL disagree, stop and resolve the current intended membership before touching Stripe.

### 3. Check for Existing Stripe Billing

Open the exact Stripe customer by email and confirm identity. Check all active, trialling, paused, scheduled and incomplete subscriptions before creating anything.

If an equivalent membership subscription already exists, do not create another one. Verify its price and start date, then resolve the Sales checkbox from evidence.

### 4. Determine the Start Date

Use `First Debit Date Is` when populated and valid. Otherwise use the confirmed actual service start to identify week 4 and charge on the approved review date when the member is already in that week.

Use the Sales payment date plus 28 calendar days only when neither a preferred debit date nor reliable actual-start evidence is available and no exception is present.

Record the date used in the batch run record.

### 5. Create the Stripe Subscription

On the verified Stripe customer, open the subscription creator from the Subscriptions section.

Complete the current classic subscription editor in this order:

1. Set the subscription start date to the approved first debit date.
2. Search for the current membership product.
3. Select the exact recurring weekly price.
4. Leave the duration as `Forever`.
5. Use the verified default payment method on file.
6. Confirm the preview shows the correct membership, weekly frequency, first invoice date and total including GST.
7. If the approved first debit date is today, confirm the preview shows `Bills immediately`, then select `Create subscription`.
8. If the approved first debit date is in the future, select `Schedule subscription`.

Stripe may show several one-time, legacy and differently timed prices under the same product. Select the exact recurring price shown in GHL, such as `A$99.00 / week`, rather than a similarly priced one-time option.

The classic Stripe editor may initially load the `Strong, Fit & Flexible Membership` product at its A$89 default price. Do not accept that default for a member whose GHL agreement records A$99 weekly. Set the row to `A$99.00 / week`, then confirm the saved schedule is weekly and A$99 before closing Sales.

For Fast Track, use the Stripe product `Fast Track Membership • Weekly` at `A$149.00 / week`. Do not select the one-time A$149 Fast Track price or another A$149 product.

The final action must match the approved debit timing. A current-date debit must show the correct immediate invoice; a future start must create a schedule. Do not proceed when the preview shows an incorrect first invoice.

### 6. Verify the Result

Reopen the Stripe customer and confirm:

- there is only one intended recurring membership subscription;
- the membership price and weekly amount are correct;
- the scheduled start or first invoice date matches the approved date;
- the default payment method is available; and
- Stripe shows no setup error requiring member action; and
- the customer page shows the saved schedule with the correct `Starts`, `Billing weekly` and next-invoice values.

Do not mark the Sales row complete from an attempted action. Completion requires a verified Stripe subscription or schedule.

### 7. Close the Sales Row

After successful verification, check column R, `Debits Set Up`, on the member's existing Sales row.

Do not add a second Sales row and do not change historical product or payment data as part of this batch.

---

## Payment and Setup Failures

If Stripe cannot create or schedule the subscription for a payment-related reason, leave `Debits Set Up` unchecked.

Create a GHL task assigned to Admin Eve containing:

- member name and exact email;
- current membership and weekly amount;
- intended first debit date;
- the Stripe error or missing-payment-method reason;
- confirmation that no duplicate subscription was created; and
- the required action to contact the member and resolve payment setup.

When the future first invoice fails after a subscription was successfully scheduled, create the same Admin Eve follow-up task. This later failure should be detected automatically through a Stripe event when the process is automated.

After the payment issue is resolved, retry the subscription setup and complete the normal Stripe verification before changing Sales. Then check `Debits Set Up` and remove the temporary Admin Eve failure task so the task queue contains only unresolved exceptions.

### Resolved-Exception Recovery Framework

Use this sequence when the original subscription start was late, missed or unsuccessful:

1. Reconstruct the member's actual service start from the confirmed Intro Session, onboarding or KickStart appointment and other approved evidence.
2. Reconfirm the current membership, weekly amount, holds, cancellations and plan changes in GHL.
3. Check Trainerize for recorded workouts and objective progress. This supports a positive member conversation but does not determine billing eligibility.
4. Agree the corrected first debit date and select a verified Stripe payment method. Do not automatically reuse the provider or method involved in the failed attempt.
5. Create or schedule the subscription and verify the saved weekly amount, start date, first invoice and payment method.
6. Check `Debits Set Up` in Sales only after Stripe verification.
7. Tell the member the exact first weekly payment date and amount. When reliable Trainerize progress exists, lead with that achievement before the payment notice.
8. Remove the temporary Admin Eve task only after the verified schedule or subscription exists.

If the scheduled first debit later fails, return the member to the payment-failure exception path and create a new owned task containing the new Stripe error.

For strength progress, state the calculation plainly. A working-weight increase is:

`(latest weight - starting weight) / starting weight × 100`

Mention rep improvement separately when the repetition count also changed. Do not present a working-weight increase as a clinical outcome or claim that every movement has improved.

---

## Stop Rules

Stop without creating a subscription when:

- identity does not match exactly across Sales, GHL and Stripe;
- GHL membership or weekly debit is missing or contradictory;
- a delayed start is known but not recorded;
- a hold, cancellation or plan change makes the intended billing state unclear;
- an equivalent subscription may already exist;
- the Stripe price or first debit date cannot be verified; or
- Stripe reports a payment-method or setup failure.

Every stopped case remains unchecked in Sales and enters an owned exception path.

---

## Definition of Done

The member has one verified Stripe membership subscription at the current weekly amount and approved first debit date. The Sales `Debits Set Up` checkbox is checked only after verification.

Any unresolved or payment-related failure remains unchecked and has a GHL follow-up task assigned to Admin Eve with enough detail to act.

---

## Automation Requirements

The future checkout-driven system must:

1. capture the current membership, weekly amount and preferred first debit date as structured data;
2. create or schedule one Stripe subscription without charging the recurring amount during the four-week upfront term;
3. use an idempotency control to prevent duplicate subscriptions;
4. stop or queue cases with delayed starts, holds, cancellations or plan changes;
5. confirm successful creation before updating `Debits Set Up`;
6. create an Admin Eve task when setup or the first recurring payment fails; and
7. close or remove the matching exception task only after a verified recovery; and
8. run a week-4 reconciliation that finds any member missed by checkout automation.

The manual batch remains the safety net until the automated path has completed a controlled shadow period with zero incorrect dates, prices or duplicate subscriptions.

---

## Related Documents

- `reference/product-offerings.md`
- `reference/sops/post-sale-member-onboarding.md`
- `reference/sops/active-client-payment-and-booking-reconciliation.md`
- `outputs/systems/membership-lifecycle.md`

---

## Revision History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 29/07/2026 | Captured the Sales column R batch trigger, Monday-based membership weeks, preferred-date and 28-day fallback rules, legacy membership mapping, Stripe verification, Admin Eve failure task and checkout-automation requirements |
| 1.0 | 29/07/2026 | Live-validated the manual process with Jess Michels: reconciled GHL Strong membership and blank preferred date, confirmed no hold or existing Stripe subscription, scheduled A$99 weekly billing from 31 July 2026, verified the saved schedule and set Sales R122 to true |
| 1.1 | 29/07/2026 | Added confirmed onboarding or KickStart appointments as evidence of the actual service start before the 28-day fallback; clarified immediate billing for a member already in week 4 and documented Tara Berge's 29 July payment-provider decline and Admin Eve exception route |
| 1.2 | 29/07/2026 | Closed Tara Berge's exception by scheduling A$99 weekly billing from 30 July 2026 against Mastercard ending 1521, verifying schedule `sub_sched_1TyMK8LMsHYOAUEzqxYKdMAu`, setting Sales R123 to true and removing the resolved Admin Eve task; added resolved-task cleanup to the failure procedure |
| 1.3 | 29/07/2026 | Formalised the resolved-exception recovery framework: reconstruct actual start, use Trainerize progress for positive communication, select a verified payment method, verify Stripe before Sales, state the first debit clearly and remove only the matching resolved Admin task |
| 1.4 | 29/07/2026 | Clarified that the calendar week containing a confirmed Intro Session, onboarding or KickStart appointment counts as week 1; live-validated the rule with Sarah Loga by scheduling A$99 weekly billing from Monday 3 August 2026 and setting Sales R125 to true |
| 1.5 | 29/07/2026 | Live-validated Fast Track with Grace Arnell: confirmed her 17 July Intro Session made 13–19 July week 1, selected the exact `Fast Track Membership • Weekly` A$149 recurring price, scheduled billing from 3 August 2026 and set Sales R126 to true |
| 1.6 | 29/07/2026 | Live-validated an owner-approved Tuesday exception with Hannah Hobman: her 22 July Intro Session established the week beginning 20 July as week 1, A$99 weekly billing was scheduled from 11 August 2026 using Visa ending 5630, schedule `sub_sched_1TyPeDLMsHYOAUEzN7Bo0ivk` was verified and Sales R127 was set true; added the Strong-product A$89 default-price warning |
| 1.7 | 30/07/2026 | Added retained Trainerize class attendance and tracked gym workouts as supporting evidence of the first meaningful-use week; live-validated the rule with Jade Wright by scheduling A$99 weekly billing from Monday 17 August 2026, verifying schedule `sub_sched_1TyilLLMsHYOAUEzHsxmgckE` and setting Sales R129 to true |
