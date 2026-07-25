# SOP: Active Client Payment and Booking Reconciliation

**System:** Brown & Casserly Pty Ltd 2026, bank receipts, Stripe, PTMinder/EziDebit, GHL and Trainerize

**Process Owner:** Admin Eve

**Quality Control:** Peter Brown

**Status:** Live

**Version:** 1.8

**Last Updated:** 25/07/2026

---

## Purpose

This SOP keeps `Active PT`, `Active SGPT`, the cancellation tabs and the weekly KPI report aligned with current payment, booking and lifecycle evidence.

It prevents stale active rows, missing weekly debit values, duplicate clients, incorrect trainer assignments and the double-counting of bundled or prepaid payments.

---

## Scope

Use this procedure for:

- the weekly line-by-line Active PT review;
- the weekly Active SGPT exception review;
- the monthly line-by-line Active SGPT payment and lifecycle audit;
- any Active SGPT change that affects a PT client's package or price;
- new PT starts, renewals, holds, resumptions, cancellations and completed packs;
- new SGPT starts, refunds, holds, resumptions, cancellations, downgrades and payment changes;
- trainer, frequency, duration, session-price or payment-method changes;
- weekly PT and SGPT income reporting; and
- investigation of a gap between actual cash collected and expected recurring income.

This procedure does not replace the approved onboarding, hold or cancellation workflows. It verifies that their outcomes are reflected consistently across the operating systems and workbook.

---

## Operating Cadence

Use a layered cadence so obvious exceptions are corrected quickly without repeating a full line-by-line investigation every week.

| Frequency | Review | Required outcome |
|---|---|---|
| Event-driven, within one business day | New start, failed payment, refund, hold, return, cancellation, downgrade, price change or payment-rail change | Update every affected system and both active sheets where applicable |
| Weekly, Monday | Full line-by-line Active PT payment, booking and trainer review; exception-first SGPT review covering new rows, arrears, pauses, future starts, refunds, cancellations and unexplained cash variance | Every PT row has supported commercial fields and booking evidence; every unresolved exception has an owner and due date |
| Weekly, Friday | Cleared-cash, confirmed-current-income and scheduled-run-rate close | A named cash bridge explains timing, pauses, arrears, future starts, PIF and bundled allocations without forcing the totals to match |
| Monthly, first Monday | Full line-by-line Active SGPT audit plus PT identity, legacy-payment and prepaid-pack deep check | One supported row per current client, verified pack positions and a closed or fully owned cash bridge |
| Quarterly, first business week | Deep cross-system identity, lifecycle and formula validation | Resolve duplicate identities, legacy emails, stale historical markers, tier omissions and repeated process failures |

Run an additional full audit whenever the unexplained weekly cash variance remains above one standard client payment after timing differences are removed. Use $99 for SGPT and $120 for PT as the default escalation thresholds unless the affected product has a different approved rate.

Also run an additional full audit when a payment pause or cancellation has no approved lifecycle evidence, a prepaid pack cannot be reconciled to its session sequence, or the Active PT count changes without an evidenced start or exit.

---

## The Four Numbers That Must Stay Separate

| Measure | Definition | Included | Excluded |
|---|---|---|---|
| Actual cash collected | Money that reached the bank during the reporting week | Cleared bank receipts from all payment rails | Forecasts, unpaid invoices and future debits |
| Confirmed current weekly PT income | Weekly recurring PT debit that is collecting now | Numeric Active PT weekly debits with current, unpaused payment evidence | PIF, paused, overdue, pre-start and cancelled clients |
| Scheduled PT run-rate | Weekly PT debit expected when approved future starts and resumptions take effect | Confirmed current income plus approved future starts and resumptions | PIF and unresolved arrears |
| Prepaid PT sales | Cash received for a PT pack | Successful one-off pack receipts | Weekly recurring PT income |

Do not use the Active PT total as a substitute for cash collected. Timing, upfront payments, pauses, arrears and bundled products mean the two figures will rarely match exactly in a single week.

---

## Source-of-Truth Hierarchy

No single system proves every part of a client's status.

| Question | Authoritative evidence |
|---|---|
| How much cash reached the business this week? | Cleared bank receipts |
| Did this individual pay? | Successful Stripe receipt or completed PTMinder/EziDebit receipt |
| Is a Stripe debit actually collecting now? | Subscription status, `pause_collection`, latest invoice status, amount and date |
| Is the client on hold or cancelling? | GHL hold and cancellation fields, pipeline state and accepted request evidence |
| Does a PT booking exist? | Expanded events from the current GHL PT calendars |
| Who is currently delivering the PT? | Current and future GHL PT calendar ownership |
| What was sold and what is the intended service? | Signed agreement, approved service change and GHL product fields |
| Does the client have coaching-app access? | Trainerize |
| What should appear in weekly reporting? | Brown & Casserly workbook after the evidence above is reconciled |

Stripe is the default current billing rail. PTMinder/EziDebit is an approved legacy receipt source only for clients whose current payment pathway is still there.

Trainerize access is supporting evidence, not proof of payment, PT attendance or current weekly debit.

### GHL Historical Agreement Fields vs Current Service

Treat the GHL `Membership Type` and weekly-debit commencement fields as evidence of the agreement at the time the client joined. Preserve those historical values when a client later changes service.

Represent the current service through the live Membership Pipeline stage, current workbook rows, approved service-change evidence and current billing. Do not overwrite a historical Fast Track commencement field merely to make it match a later Strong or PT-only service.

If the historical agreement and current service differ, record the transition and correct the current pipeline stage or service marker. Do not report the difference as a payment contradiction when the current billing and approved transition agree.

---

## Non-Negotiable Rules

1. Match by exact normalised email first, then verified phone or an owner-approved identity link. Never declare a payment match from name alone.
2. Search approved alternate or legacy emails before classifying a client as unpaid. Record the approved identity link so the same mismatch is not investigated again.
3. A Stripe subscription labelled `active` is not enough. Check `pause_collection` and the latest invoice status, amount and date.
4. A successful receipt proves payment; a draft, void, open, incomplete or past-due invoice does not.
5. Recurring PT and membership payments are collected one week in advance. Allocate a normal scheduled payment to the following service week, even when Stripe displays an earlier subscription or invoice period.
6. A late retry or manual arrears recovery retains the original service entitlement being recovered. Do not shift it forward again merely because the successful receipt date is later.
7. A draft invoice with automatic collection disabled is an administration exception, not proof that the client refused or failed payment.
8. A GHL booking marked confirmed proves that an appointment is scheduled. It does not prove physical attendance.
9. Exclude deleted, cancelled and no-show events from future-booking coverage. For historical service and charge reconciliation, classify them under the cancellation-timing rules below before deciding whether the session was chargeable.
10. No future booking is an exception to investigate, not automatic evidence of cancellation.
11. No payment is an exception to investigate, not automatic authority to delete the client.
12. Never invent a cancellation date. Use the accepted cancellation boundary, verified final service date or final completed pack session.
13. Do not rely on spreadsheet column letters alone. Confirm the current header before editing because the workbook layout can change.
14. Every material change must be completed across all affected systems in the same work cycle.
15. Reserve `PIA` for **Paid in Advance**. Use the explicit workbook status `Active - ARREARS` for a member whose payment is overdue or under recovery; do not abbreviate payment arrears.
16. Count both `Active` and `Active - PIA` in the active-member KPI. Exclude `Active - ARREARS` from the collecting-status count until payment is recovered.

### Payment-to-Service Allocation

Use the owner-confirmed one-week-in-advance policy to map receipts to delivery. The displayed Stripe billing period is processor metadata and must not override the approved service week.

Example: a normal recurring payment collected on 1 May covers the 5–12 May service period, even if Stripe displays 28 April–5 May.

For a late retry or manual recovery, first identify the original scheduled payment or entitlement being recovered. Apply the one-week advance rule to that original schedule, not to the later date on which Stripe finally succeeded.

---

## Active PT Row Standard

Every active row must contain or resolve the following:

| Field | Rule |
|---|---|
| Client identity | Use the exact GHL email used for lifecycle management |
| Current trainer | Derive from the current future PT series; list both trainers if delivery is genuinely shared |
| Sessions per week | Record the contracted current frequency, adjusted only by an approved service change |
| Session length | Record the current booked and contracted duration |
| Session cost | Record the approved PT allocation per session |
| Weekly debit | Use a numeric weekly PT amount for recurring clients or `PIF` for prepaid packs |
| Payment pathway | Stripe recurring, Stripe pack or legacy PTMinder/EziDebit |
| Notes | Record approved exceptions, pack position, future start, hold boundary, arrears or follow-up |

Do not leave required commercial fields blank while a row remains active. If evidence is unresolved, mark the row for review and assign an owner rather than guessing.

## Active SGPT Row Standard

Every active SGPT row must contain or resolve the following:

| Field | Rule |
|---|---|
| Client identity | Match the current GHL email first, then a verified phone or recorded legacy-email link |
| Current product | Use the current approved service, not an outdated commencement product |
| Status | Use `Active`, `Active - PIA`, `Active - ARREARS` or another explicitly approved lifecycle status |
| Weekly debit | Record the current SGPT allocation actually being collected, or `PIF` where the membership was paid in advance |
| Payment pathway | Record or be able to evidence Stripe, PTMinder/EziDebit or another owner-approved rail |
| Hold or cancellation | Align the workbook status with GHL approval, payment behaviour and the final-access boundary |
| Fast Track pair | Require a matching $50 Active PT row for every current $99 Fast Track SGPT allocation |

Do not leave a refunded cooling-off client on an active sheet. Do not leave a payment pause represented as collecting income merely because the contact or subscription still carries an active label.

### Bundled Memberships

For a bundled SGPT and PT product, record only the approved PT allocation in `Active PT` and the approved membership allocation in `Active SGPT`.

Count the full bank or processor receipt once in cash collected. Never enter the full bundled receipt as both PT income and SGPT income.

For Fast Track, apply this fixed weekly allocation:

| Reporting surface | Weekly amount | Treatment |
|---|---:|---|
| `Active SGPT` | $99 | SGPT membership component |
| `Active PT` | $50 | Weekly 30-minute one-on-one PT component |
| Cash collected | $149 once | Full cleared receipt; do not add the two allocation rows again |

The $99 and $50 entries are reporting allocations of one $149 Fast Track payment, not separate customer charges.

A current Fast Track client passes the workbook audit only when both active rows are present and total $149 per week, unless an approved exception is documented. A $149 receipt paired with a $99 `Active SGPT` row is not an SGPT mismatch if the matching $50 `Active PT` row is present.

### Prepaid Packs

Enter `PIF` in the weekly debit field. Do not convert the original pack purchase into recurring weekly income.

Stripe or PTMinder/EziDebit proves that the pack was purchased. It does not by itself prove how many sessions remain.

The appointment description must use a sequential `session X/Y` label. If the sequence is stale, find the last verified label or pack start, count forward through qualified appointments and correct the sequence without inferring entitlement from payment amount alone.

When the final session is booked, create a renewal decision before that appointment. If the client does not renew, close the PT record on the verified final session date through the cancellation process.

### Future Starts

Keep the agreed future weekly amount documented, but exclude it from confirmed current weekly PT income until the first recurring debit is due.

Include it in scheduled PT run-rate only when the start date and amount are approved and evidenced.

---

## Payment Classification

| Classification | Evidence | Reporting treatment |
|---|---|---|
| Collecting recurring | Successful recent receipt, unpaused subscription and no unresolved overdue invoice | Include numeric weekly debit |
| Approved future start | Valid agreement and evidenced first debit date in the future | Exclude now; include in scheduled run-rate |
| Approved pause | Stripe or legacy processor pause aligns with GHL hold dates | Exclude during the pause |
| Payment recovery | Open, incomplete or past-due amount requires collection | Exclude from confirmed income; escalate |
| Billing administration failure | Draft or disabled collection prevented an attempted charge | Exclude until corrected; do not blame the client |
| PIF active | Successful pack receipt and unused session entitlement | Record `PIF`; exclude from recurring income |
| Legacy collecting | Completed PTMinder/EziDebit receipt for an approved legacy payer | Include the approved numeric weekly PT amount |
| Unverified | No successful receipt or approved entitlement found | Do not include; investigate |

Use the latest successful receipt and current billing state together. One old successful payment does not prove that a recurring client is current today.

---

## Booking and Trainer Rules

Review the expanded event ledger across all current PT calendars. Contact-level appointment lists may omit instances from a recurring series.

Use current and future appointments to update the trainer field. Preserve historical trainer evidence rather than rewriting old delivery records.

The standard forward-booking horizon is 13 weeks. A shorter horizon is a rebooking exception unless the client is approaching a pack end, approved service end, hold, cancellation or known schedule transition.

Count same-week reschedules against the weekly entitlement. A make-up in the following week may cover the prior week only after the following week's normal sessions are protected.

Keep unexplained extra appointments visible for review. Do not remove them without an accepted cancellation boundary or explicit Admin approval.

### Cancellation Timing and Session Charge Classification

Do not infer the financial treatment from the current appointment status alone. For every cancelled, deleted or no-show PT appointment in the audit period, inspect:

1. the scheduled session start;
2. the GHL appointment activity timestamp and action;
3. nearby client and staff messages or calls;
4. any approved hold, cancellation or schedule-change evidence; and
5. the applicable session price or pack entitlement.

Apply the following treatment:

| Evidence | Treatment |
|---|---|
| Client no-show or cancellation recorded within 24 hours of the scheduled start, including after the session began | Chargeable under the PT policy; consume the session or include the approved session value in the amount due |
| Client cancellation recorded at least 24 hours before the scheduled start | Non-chargeable; provide the approved make-up session or account credit |
| Appointment removed administratively because of an approved hold or accepted schedule correction | Non-chargeable when the underlying approval predates the affected session, even if staff deleted the calendar event later |
| Timing or reason cannot be established | Do not charge automatically; record an owned exception for review |

A chargeable late cancellation is delivered-equivalent for entitlement and payment reconciliation, but it is not physical attendance. Preserve that distinction in the audit notes.

Record the appointment date, action timestamp, notice interval, evidence source, charge decision and value. Where GHL emits duplicate activity records for the same appointment ID, count the appointment once.

---

## Hold Reconciliation

An approved hold must align across GHL, the payment processor and future bookings.

| Finding | Action |
|---|---|
| GHL hold and payment pause align | Retain the client as a hold exception; exclude the debit during the pause |
| Payment paused but GHL has no hold | Escalate immediately and reconstruct the approved hold evidence |
| GHL says hold but payment is collecting | Verify whether the hold is pending, stale or failed in billing |
| Bookings continue during a hold | Confirm whether sessions are intentional before changing either system |
| Stale Pending or Escalated Hold | Clear only after payment, booking and request history prove the hold is no longer valid |

Do not clear a hold field merely because it is old. Do not leave a valid payment pause hidden from the workbook and weekly-income calculation.

---

## Cancellation and Pack Completion

For an accepted recurring PT cancellation, follow the verified final-payment and final-service-week rule in the cancellation system.

For a completed prepaid pack with no renewal:

1. use the final qualified session as the PT end date;
2. remove the client from `Active PT`;
3. add or preserve the client in `PT Cancellations`;
4. remove the active `personal training` lifecycle treatment where appropriate;
5. add `old pt client`;
6. remove future PT appointments after the verified boundary; and
7. retain the commercial and session-count evidence.

Do not delete historical completed appointments. If a historical event was genuinely erroneous, retain an audit note describing what was corrected and why.

---

## Monthly Active SGPT Audit Procedure

### 1. Prepare One Audit Snapshot

1. Record the audit date, cash-reporting window and workbook version.
2. Read the complete `Active SGPT` table once and identify the current headers before editing.
3. Build one exception list covering new starts, arrears, PIA, pauses, refunds, holds, cancellations, downgrades, Fast Track members and rows changed since the prior audit.
4. Keep actual cash, expected current recurring income, future-start income and PIF sales as separate totals.

### 2. Reconcile Identity and Current Service

1. Match the workbook row to GHL and the payment rail by exact normalised email.
2. Check verified legacy or alternate emails before classifying the member as unpaid.
3. Use current approved service evidence for the live tier while preserving historical agreement fields.
4. Confirm that refunded cooling-off clients and accepted cancellations are not retained as active.
5. Confirm that downgrades have removed any no-longer-included PT row and updated the current membership tier across the workbook, GHL and Trainerize.

### 3. Reconcile Payment and Lifecycle

1. Verify the latest successful receipt, current amount, payment rail and next expected payment.
2. Check failed, open, voided or administratively disabled payments before deciding whether the member is in arrears.
3. Align every payment pause with an approved GHL hold, a stated reason and an evidenced return date.
4. Treat any hold longer than four weeks as an extended hold that requires documented manager approval.
5. Where a cancellation has been accepted, do not leave an unexplained hold active for the same service.
6. Record temporary overpayment corrections and the date and amount of the first normal recurring debit.

### 4. Reconcile Cross-Sheet Allocations

1. Match every current Fast Track SGPT row to one Active PT row by email.
2. Confirm the fixed allocation is $99 in Active SGPT and $50 in Active PT.
3. Count the $149 customer receipt once in cash collected.
4. Confirm that Strong, Fit & Flexible members do not retain a Fast Track PT allocation unless they also have a separately approved PT product.

### 5. Write and Verify

1. Apply evidenced workbook corrections in one controlled batch where practical.
2. Re-read every changed row after writing.
3. Search the active sheet again by email to confirm that no duplicate row was introduced.
4. Put each unresolved discrepancy into the exception matrix with the evidence checked, owner, next action and due date.
5. Create or update the corresponding GHL task when follow-up is required.

### 6. Close the Cash Bridge

1. Total the eligible numeric SGPT allocations.
2. Remove approved pauses, future starts and unresolved arrears from confirmed current recurring income.
3. Compare the result with cleared cash for the same entitlement window.
4. Explain the gap by named member and category.
5. Refresh KPI reporting only after the corrected workbook and cash bridge agree or every residual item is an owned exception.

---

## Lessons Applied from the July 2026 Audit

1. Search every approved payment rail. An absent Stripe customer is not proof of non-payment when legacy PTMinder/EziDebit billing remains active.
2. Treat owner-supplied alternate emails as durable identity links. Record them once so future audits do not repeat the same search.
3. Use the amount actually being collected. Do not preserve a standard price when an approved current amount, temporary correction or legacy rate is evidenced.
4. Separate historical agreement data from the current service. A former Fast Track commencement field can coexist with a valid Strong, Fit & Flexible downgrade.
5. Resolve refunds immediately. A client refunded during cooling off never becomes an active member.
6. Treat long holds as high-risk exceptions. A distant resume date must have a reason, approval and aligned payment and access state.
7. Do not allow cancellation and hold records to coexist without an explicit explanation. Accepted cancellation evidence should drive the final-access treatment.
8. Record payment-recovery cases explicitly as `Active - ARREARS`. An active contact label alone must not contribute to collecting recurring income.
9. Use current bookings to identify the delivering PT trainer, but record a system-versus-owner discrepancy instead of silently choosing one.
10. Batch corrections only after evidence collection, then perform a duplicate search and bounded post-write verification.
11. Treat bank cash as the actual result and active-sheet totals as projections or allocations. Never alter a client amount merely to make the totals agree.
12. Apply the one-week-in-advance rule to the scheduled debit date. A late retry still funds the original entitlement and must not be shifted forward a second time.
13. Check Stripe `pause_collection`, invoice state and the latest successful receipt together. An active subscription label alone does not prove that cash is collecting.
14. Treat no future PT booking as an exception, not as cancellation evidence. Check holds, cancellation fields, conversations, pack completion and the last delivered session before changing lifecycle state.
15. Read expanded PT calendar events across all current trainer calendars. Contact appointment feeds may show only a recurring master and can understate the real booking horizon.
16. For every cancelled or deleted PT appointment in a charge audit, check the action timestamp and nearby messages. A client cancellation inside 24 hours is chargeable, while an approved hold or timely cancellation is not.
17. A pack receipt proves purchase but not the remaining balance. Maintain `Session X/Y` descriptions, reconstruct stale sequences from qualified appointments and create the renewal decision before the final session.
18. Allocate Fast Track once as $99 SGPT and $50 PT, while counting the $149 receipt once in cash. Require both active rows unless an approved exception is recorded.
19. Keep `PIA` for Paid in Advance and use `Active - ARREARS` for payment recovery. Count `Active - PIA` in active membership and exclude arrears from confirmed collecting income.
20. Put every unresolved case into GHL with a specific action, owner and due date. The workbook note records the evidence; the task creates accountability.

These rules convert the next audit from a full investigation into an exception-led review. Clean members should require only identity, payment and lifecycle confirmation.

---

## Weekly Reconciliation Procedure

### Monday: Active Roster and Booking Review

1. Run or read the PT Booking Continuity report after its Monday 5:30 am Brisbane run.
2. Review new or changed Active SGPT rows, payment failures, arrears, pauses, holds, cancellations, refunds and downgrades since the prior Monday.
3. Read every `Active PT` row and confirm the identity fields.
4. Verify the payment pathway and current payment classification.
5. Check GHL hold, cancellation and approved service-change evidence.
6. Confirm contracted sessions per week, session length, session cost and weekly debit or `PIF`.
7. Check future PT bookings, booked-through date and current trainer.
8. Classify every cancelled, deleted or no-show appointment in the review window using the cancellation-timing and approved-hold evidence above.
9. Update stale workbook values only when the replacement value is evidenced.
10. Put each unresolved row into the exception matrix below with an owner and due date.

### Friday: Cash and Run-Rate Close

1. Confirm actual weekly cash collected from cleared bank receipts.
2. Calculate confirmed current weekly PT income from eligible numeric Active PT rows.
3. Calculate scheduled PT run-rate separately.
4. List PIF sales separately by receipt date.
5. Reconcile bundled SGPT and PT allocations to ensure the full receipt is counted once.
6. Explain the remaining gap by timing, pause, arrears, future start, PIF, processor delay or unresolved exception.
7. Do not force the workbook total to equal bank cash.

---

## Exception Matrix

| Payment | Future booking | Classification | Required action |
|---|---|---|---|
| Current | Yes | Clean | Retain and confirm row fields |
| Current | No | Delivery exception | Rebook, verify pack end or confirm service transition |
| Not current | Yes | Finance risk | Escalate payment recovery before further unreviewed delivery |
| Not current | No | Lifecycle exception | Check hold, cancellation, completed pack and contact history |
| Paused | Yes | Hold contradiction | Confirm whether booked sessions are intentional |
| Paused | No | Likely valid hold | Confirm GHL dates and return plan |
| PIF | Yes | Pack in delivery | Maintain `session X/Y` and renewal threshold |
| PIF | No | Pack exception | Confirm unused sessions, completed pack or disengagement |

Every exception must show the evidence checked, responsible owner, next action and due date.

---

## Event-Driven Updates

Do not wait for the weekly review after any of these events:

- a new SGPT membership or Fast Track agreement;
- a new PT agreement or pack purchase;
- a changed frequency, duration, trainer, price or membership tier;
- a cooling-off refund or reversed sale;
- a hold request, hold activation or return;
- an accepted cancellation or reversed cancellation;
- the final session of a prepaid pack;
- a failed or administratively disabled payment collection;
- a temporary overpayment correction or changed next-debit amount;
- a changed primary email; or
- a recurring series being created, moved or ended.

Complete the workbook, GHL, payment exception record and booking check within one business day.

---

## Definition of Done

The active workbook contains one row per current SGPT member and PT client, complete commercial fields, the current trainer where applicable and a supported weekly debit or `PIF`.

Payment, booking, hold and cancellation evidence agree, or the disagreement is recorded as an owned exception with a due date. Actual cash, current recurring income, scheduled run-rate and PIF sales are reported separately.

Every current Fast Track member has both allocation rows, and every downgrade, refund, hold or cancellation is reflected across the workbook, GHL, payment rail and Trainerize as applicable.

---

## Related Documents

- `reference/sops/post-sale-member-onboarding.md`
- `outputs/systems/pt-weekly-audit-run-sheet.md`
- `outputs/systems/personal-training.md`
- `outputs/systems/membership-hold.md`
- `outputs/systems/cancellation-system.md`
- `outputs/systems/pt-booking-shadow-review-log.md`
- `outputs/systems/trainerize-reporting-reconciliation.md`

---

## Revision History

| Version | Date | Changes |
|---|---|---|
| 1.8 | 25/07/2026 | Established the full weekly PT audit, Friday cash close, monthly pack and identity deep check, quarterly formula validation, variance escalation thresholds and reusable July audit lessons |
| 1.7 | 25/07/2026 | Added the weekly, monthly and quarterly SGPT audit cadence; defined the Active SGPT row standard and full monthly procedure; incorporated identity, legacy-payment, refund, hold, cancellation, downgrade, amount-adjustment and post-write verification lessons from the July audit |
| 1.6 | 25/07/2026 | Added Active - PIA to the active-member KPI while retaining Active - ARREARS as an excluded payment-recovery status |
| 1.5 | 25/07/2026 | Reserved PIA for Paid in Advance and replaced the ambiguous Active - PIA status with the explicit Active - ARREARS label |
| 1.4 | 25/07/2026 | Distinguished historical GHL commencement fields from current service markers; required current Membership Pipeline, workbook, billing and approved-change evidence to represent the live service without erasing the original agreement |
| 1.3 | 25/07/2026 | Defined the fixed Fast Track allocation as $99 in Active SGPT and $50 in Active PT from one $149 weekly payment; added the cross-sheet audit requirement and cash double-counting control |
| 1.2 | 25/07/2026 | Added the mandatory appointment-action timing check for cancelled, deleted and no-show PT sessions; defined chargeable late cancellations, approved-hold deletions, evidence requirements, duplicate-event handling and delivered-equivalent treatment |
| 1.1 | 25/07/2026 | Added the owner-confirmed rule that recurring payments fund the following service week, clarified that Stripe's displayed period does not override service allocation, and preserved the original entitlement when a late retry or manual recovery succeeds |
| 1.0 | 25/07/2026 | Created the canonical active-client payment and booking reconciliation procedure; defined source ownership, legacy PTMinder/EziDebit treatment, workbook row rules, payment and booking classifications, hold and pack controls, weekly income definitions and the weekly exception-led review |
