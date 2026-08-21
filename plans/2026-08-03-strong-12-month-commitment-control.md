# Strong 12-Month Commitment Control

**Owner:** Peter Brown  
**Operator:** Admin Eve  
**Status:** Live — controlled acceptance passed and all three Strong workflows are Published  
**Started:** 2026-08-03

## Outcome

Allow a member on the eligible Strong, Fit & Flexible service to reply exactly `COMMIT`,
review and sign a dedicated variation, and receive a governed A$10 weekly
discount for 12 calendar months. Billing returns to the member's original
A$99 weekly price at the first normal weekly billing boundary on or after the
anniversary.

## Locked commercial rules

- Strong, Fit & Flexible is the only eligible service.
- Fast Track and Fit & Flexible are excluded.
- The four-week upfront payment is unchanged.
- Discounted weekly price is A$89; original weekly price is A$99.
- The term begins with the first successful discounted weekly payment.
- Existing weekly members start on their next normal weekly payment; there is
  no backdating or refund.
- Holds do not extend the term.
- The ongoing membership continues at A$99 after the discount term unless a
  new signed variation is entered into.
- Early cancellation or downgrade may recover only the discount actually
  received: A$10 for each successful discounted weekly payment, less refunds,
  capped at A$520.
- A Fast Track upgrade ends the discount without clawback.
- No clawback applies where The Evolved cannot supply the service, Australian
  Consumer Law rights apply, or Peter approves documented medical or severe
  hardship.
- The member must see the calculated clawback before collection.

## Legal control

The signed variation must provide the Queensland 48-hour cooling-off right,
plain-English fee and discount disclosure, early termination circumstances,
the maximum termination amount, and the ongoing-agreement acknowledgement.
GHL must issue the statutory written continuation reminder at least two months
before the initial term ends.

## System plan

1. Publish the offer and agreement versions in the canonical reference layer.
2. Add GHL commitment dates, prices, clawback and reminder fields.
3. Create an idempotent Stripe A$89 weekly price under the existing Strong
   product.
4. Extend Billing OS to create a two-phase Stripe schedule: A$89 for the
   governed term, then A$99 ongoing.
5. Add a read-only clawback quote route; collection remains a separately
   approved action after the member sees the quote.
6. Build the Strong-only GHL email, exact-COMMIT intake, signed variation and
   reminder workflow.
7. Prove the complete path with a synthetic contact before touching Jodie
   Doran or Rene Van der Spuy.

## Live build status — 4 August 2026

- GHL survey `8fgZo7gVs7tlXoAgKkCl`, **Strong 12-Month Commitment
  Variation**, contains the governed terms, final acknowledgement and required
  member signature.
- Page-one phone collection is optional and the country picker is enabled with
  Australia (+61) as the default. Public acceptance confirmed that local mobile
  number `0420863721` is accepted exactly as entered and advances without a
  phone-format error; name and email remain the only required fields.
- Public review URL:
  `https://links.theevolvedgym.com.au/widget/survey/8fgZo7gVs7tlXoAgKkCl?notrack=true`.
- Published workflow `e571a911-10c6-4be3-872c-dd4bcf8ead84` receives only that
  signed survey and calls Billing OS with target
  `strong_12_month_commitment` and the exact survey ID.
- Published workflow `d03f6ea9-6e16-40fe-9e16-6fdb17569922` accepts only an exact
  `COMMIT` reply to the `3.0 New Member` onboarding workflow, then requires the
  canonical current-service field to contain `Strong` before sending the
  variation link.
- Published workflow `04ed168e-49a4-4614-8260-568a5673e830` runs on
  `SC: Continuation Reminder Date`, sends the written two-month continuation
  notice and records `SC: Continuation Reminder Status = Sent`.
- GHL onboarding templates Email #3 and Email #7 now use the exact eligible
  Strong, Fit & Flexible service name, exclude standalone Fit & Flexible and
  Fast Track, and state that `COMMIT` records interest only.
- The COMMIT workflow's variation-link action uses the explicit sender
  `admin@theevolvedgym.com.au`; it must not inherit the location default sender.
- Synthetic public-form testing confirmed the required signature blocks
  submission. The two auxiliary text acknowledgements are explicitly optional;
  the signed final acknowledgement is the binding acceptance control.
- Controlled contact `peter@thefitmummethod.com` had no Stripe customer or
  subscription. Its canonical service field was temporarily set to Strong,
  Fit & Flexible and restored to its original blank value after testing.
- The first controlled COMMIT execution exposed that the variation-link email
  action was connected to the ineligible branch. The action was moved to the
  eligible branch and the corrected workflow was rerun.
- The corrected read-back recorded `Eligible — Executed`, followed by
  `Send Strong variation link — Executed`, then normal end-of-workflow
  completion. The test email was sent to the controlled address.
- Peter submitted the controlled variation with the Australian mobile stored as
  `+61420863721`, both optional text acknowledgements captured and the required
  signature document generated. Jodie Doran and Rene Van der Spuy remained
  untouched during acceptance testing.
- Page two of the public variation was rewritten to the canonical member-facing
  writing rules: regular-weight body copy, short paragraphs, visible space
  between sections, no em dashes and no more than two sentences per paragraph.
  An inherited duplicate bold terms block was removed without changing the
  approved commercial or legal meaning.
- Page three now contains one signature field only. The retained required field
  binds the member's signature directly to the full acceptance statement; the
  shorter duplicate `Member signature` field was removed and public preview
  verification reached the single signature pad without submitting the form.
- The controlled signed-intake test reached Billing OS and failed closed with
  `Expected exactly one Stripe customer with the exact email`, as required for
  Peter's non-Stripe contact. No billing mutation occurred; one same-day Admin
  Eve exception task was created, verified and then completed as test cleanup.
- The acceptance gate passed and the COMMIT Interest, Controlled Intake and
  Continuation Reminder workflows were published. GHL read-back showed all
  three as `Published` on 4 August 2026.
- GHL folder `8. Membership Service Changes` was created on 4 August 2026. All
  five `MSC` workflows were moved into it; live read-back confirmed the three
  Strong workflows remained Published and the Evolved Anywhere and Online Only
  workflows remained Draft.
- Jodie Doran and Rene Van der Spuy were reconciled on 4 August 2026 before
  production enrolment. Both joined within the prior 60 days, had an exact
  `COMMIT` reply, a signed membership agreement, active customer/member state,
  a won Strong, Fit & Flexible opportunity and authoritative A$99 weekly Strong
  billing evidence. Their previously blank canonical current-service values
  were corrected to `Strong, Fit & Flexible`.
- Both contacts were then enrolled through the published COMMIT Interest
  workflow. Each execution finished on `Send Strong variation link`, and each
  outbound email used subject `Your Strong 12-month commitment variation` and
  the governed `admin@theevolvedgym.com.au` sender. No `SC:` signed-variation
  field was populated and no membership or billing change occurred from the
  interest-stage enrolment.

## Stop rules

- Do not fulfil from a `COMMIT` reply alone.
- Do not enrol Fast Track or Fit & Flexible members.
- Do not mutate an ambiguous, paused, cancelled or already schedule-managed
  Stripe subscription.
- Do not collect a clawback automatically.
- Do not process a service change unless the exact signed variation reaches the
  published controlled-intake workflow and Billing OS accepts the request.
