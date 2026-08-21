# SOP: Membership Service Change Control

**System:** GHL, Billing OS, Stripe, Trainerize, GHL calendars, Brown & Casserly workbooks and the Evolved Operating Data Hub

**Process Owner:** Admin Eve

**Commercial and Policy Approval:** Peter Brown

**Status:** Live for internal control. Strong commitment billing, fields,
variation, onboarding copy and three GHL workflows passed controlled
acceptance and are Published. The two earlier Evolved Anywhere and Online Only
intake workflows remain Draft pending their six-surface acceptance gate.

**Version:** 1.25

**Last Updated:** 05/08/2026

---

## Purpose

This SOP governs a member's move between continuing services without treating the change as a cancellation or a new acquisition.

It preserves the old service until the approved effective boundary, then accepts the new service only when every required operating surface agrees.

---

## Current Activation Boundary

The internal control fields, immutable event contract and read-only billing verifier are live. GHL survey `zFxqvzogSZFbeGDnNM8Q` is a dedicated Evolved Anywhere form containing details, Evolved Anywhere terms and final acknowledgement.

GHL survey `XBpTy848fvJXjMtGfnu2` is a dedicated Online Only form containing details, Online Only terms and final acknowledgement. All 64 inherited cancellation-era conditions were removed from each survey.

Both public paths passed from details to the correct service terms and final acknowledgement on 31 July 2026 without submission or cross-service leakage. Peter approved both variations on 31 July 2026.

Do not send either variation or enable the automatic fulfilment trigger until the controlled request, cross-system acceptance and Admin Eve exception tests pass.

On 2 August, both controlled Trainerize definitions passed. Online Only has an Active Main Product, Full Access / one-way messaging, the approved no-equipment program, no Add-ons and no Session Credits.

The original Evolved Anywhere sale remained `Pending`, was removed through Trainerize's supported pending-purchase control and became `Expired`; the replacement on the same product and profile is now Active after the newest confirmation. Its Full Access / one-way messaging state executed, the existing personal program was preserved, and it has no Add-ons or Session Credits.

Both synthetic profiles were then moved to Deactivated and verified there. Both GHL workflows remain Draft with zero enrolments and member-facing sends remain off because no clean six-surface accepted event may be asserted before the effective boundary.

Post-boundary reconciliation on 5 August confirmed Tania's A$69 Evolved Anywhere Stripe subscription is Active and its first A$69 payment succeeded. The governed remediation corrected the canonical GHL service projection, removed the obsolete `bronze` tag, retained the same Admin Eve task as one exception and added the governed `Active Online` row. The stale `Active SGPT` row was then removed after exact workbook read-back, while the historical `Sales` record was preserved. The `Active Online` row deliberately states `Pending agreement`; GHL conversation evidence confirms Monday only, with no agreed trainer, recurring time or in-person/virtual mode, and a scan of all 30 calendars found no future appointment.

Trainerize's supported unsubscribe control removed the legacy `2026 SGPT Program`; full group-member read-back also proved Tania is no longer in `The Evolved All Stars`. Full Access / one-way messaging and the `Tania's program` container remain. Acceptance is still blocked because the profile reads `Main program expired` and `No current training plan`, and six manually added non-expiring group/class credit balances still permit app self-booking. Trainerize exposes no safe client-level revoke/edit control for those gifted credits; shared class event types must not be disabled and Tania must not be deactivated. Tania also remains split across a phone/current-service GHL contact and a separate email/marketing contact, so the approved duplicate-identity process must complete before acceptance. The immutable accepted event, workflow publication and member completion remain blocked; both intake workflows are read back as Draft and sends remain off.

Evolved Anywhere and Online Only remain retention services, not public acquisition offers. Fast Track existing-member upgrades have an approved commercial pathway but are not live in this SOP's workflows: collect an immediate A$50 first-session payment, move the recurring membership to A$149 per week on the next scheduled debit, book the first specialised PT session in the same week and create thirteen weekly specialised 30-minute bookings. The thirteen-session specialised series replaces the acquisition four-session onboarding pathway for these existing members; acquisition Fast Track onboarding remains separate. Each request must carry the Full Standards Assessment rationale, priority gap or gaps, selected next standard, initial 8–12 week focus, progression and approved specialised twelve-week Trainerize programme. PIF is out of scope. Do not send a Fast Track variation or automate this pathway until its target configuration and controlled cross-system acceptance pass.

The Evolved Anywhere review form is `https://links.theevolvedgym.com.au/widget/survey/zFxqvzogSZFbeGDnNM8Q`. The Online Only review form is `https://links.theevolvedgym.com.au/widget/survey/XBpTy848fvJXjMtGfnu2`. Both the Privacy Policy and Terms of Use link to `https://theevolvedgym.com.au/legal`.

### Strong 12-Month Commitment

Offer `strong-12-month-commitment-v1` is available only to members on the
Strong, Fit & Flexible service. Standalone Fit & Flexible and Fast Track are
excluded. The exact
`COMMIT` reply records interest only and must not change billing or membership
state.

The dedicated signed variation is
`strong-12-month-commitment-variation-v1`. It must disclose A$99 original
weekly pricing, A$89 discounted weekly pricing, the unchanged upfront payment,
12-calendar-month term, ongoing A$99 reversion, 48-hour cooling-off period and
the proportional discount-recovery policy.

Billing OS starts the A$89 price on the first successful discounted regular
weekly payment and creates an automatic A$99 phase at the first normal weekly
boundary on or after the anniversary. Holds do not extend the term. GHL must
send the ongoing-agreement reminder at least two months before the term ends.

The clawback route is quote-only. It calculates A$10 for each successful
discounted weekly payment, less refunds, capped at A$520, and records the quote
for member review. It cannot create a charge. Cancellation or downgrade may
enter the quote path; Fast Track upgrade, inability to supply, Australian
Consumer Law rights and an approved documented medical or severe-hardship
exception waive it.

The Stripe catalogue already contained one active A$89 and one active A$99
weekly price under the approved Strong product, so no price was duplicated.
The Billing OS allowlist and eleven commitment-specific GHL control fields are
live. The member-facing variation is GHL survey `8fgZo7gVs7tlXoAgKkCl`; its
public form passed the governed-terms and required-signature checks. Email #3
and Email #7 in the new-member sequence contain the approved Strong, Fit &
Flexible wording and make clear that `COMMIT` records interest only.

The exact-COMMIT interest workflow, signed-intake Billing OS workflow and
two-month continuation-reminder workflow passed controlled acceptance and are
Published. They are filed with the Evolved Anywhere and Online Only intake
workflows in GHL folder `8. Membership Service Changes`.

For a genuine `COMMIT` reply received before the workflow was published, Admin
may enrol the existing contact manually only after a complete live-record
reconciliation proves all of the following: the contact joined within the
approved 60-day window; the reply is exactly `COMMIT`; the contact is an active
customer and member; the signed membership agreement, won Strong opportunity
and authoritative A$99 weekly Strong billing evidence agree; the canonical
current-service field reads `Strong, Fit & Flexible`; and no earlier variation
or COMMIT workflow execution exists. The enrolment must finish on `Send Strong
variation link`. The operator must then confirm the approved subject and
`admin@theevolvedgym.com.au` sender, and confirm that no `SC:` signed-variation
field or billing state changed from the interest-stage action.

---

## Authorities

No single platform is the client database.

| Fact | Authority |
|---|---|
| Charge, subscription and schedule | Stripe or the approved legacy payment rail |
| Contact, consent, lifecycle and communication | GHL |
| Coaching-app account and program access | Trainerize |
| Recurring PT appointment | Current GHL calendar event |
| Operating roster and weekly reporting | Brown & Casserly workbook after reconciliation |
| Accepted cross-system service state | Evolved Operating Data Hub |
| Commercial terms and member agreement | Approved offer version plus signed variation |

The legacy Membership Pipeline is historical evidence only. Do not update it to make a service change appear current, and do not remove its existing writers until the replacement acceptance gate is complete.

---

## Required GHL Control State

Use the dedicated `6. Membership Service Change` Contact folder.

| Control group | Required fields |
|---|---|
| Identity | SC: Request ID |
| Prior and requested state | SC: Prior Service Components; SC: Selected Service Components |
| Timing | SC: Request Date; SC: Effective Date; SC: Signed Timestamp; SC: Commitment Start Date; SC: Commitment End Date; SC: Continuation Reminder Date |
| Agreement | SC: Offer Version; SC: Agreement Version; SC: Signature Document |
| Overall state | SC: Change Status; SC: Last Error; SC: Completed Timestamp |
| Commitment economics | SC: Original Weekly Price Cents; SC: Discounted Weekly Price Cents; SC: Weekly Discount Cents; SC: Maximum Clawback Cents; SC: Clawback Quote Cents; SC: Clawback Status; SC: Continuation Reminder Status |
| Surface state | SC: Billing Action Status; SC: GHL Lifecycle Status; SC: Trainerize Provisioning Status; SC: Appointment Provisioning Status; SC: Workbook Reconciliation Status; SC: Reporting Acceptance Status |
| Canonical projection | Member: Current Service Components; Member: Lifecycle Status; Member: Current Service Version; Member: Service State Updated At |

Do not use the `MCHO` selection fields as current-service fields. The survey may capture the signed request, but only the governed accepted event may update the canonical current-service projection.

---

## Non-Negotiable Controls

1. Match the member by exact normalized email, then a verified phone or an approved identity crosswalk. A name-only match must fail closed.
2. Create one request ID for one signed request. Replaying the exact event is safe, but changing its payload or reusing its ID is an exception.
3. Allow only one pending request for a canonical member identity. A second concurrent request must not overwrite the first.
4. Keep the old service current until the exact effective timestamp in Brisbane. A future change may be scheduled, but it must not update the active roster early.
5. Verify the exact existing billing item, exact target weekly amount and exact effective boundary. A merely active subscription is insufficient.
6. Do not complete the request after a billing failure or an ambiguous Stripe schedule. Route the error to Admin Eve and retain the current service.
7. Write the canonical GHL service and lifecycle projection only after billing succeeds or is explicitly not applicable.
8. Reconcile Trainerize, appointments, every affected workbook and reporting separately. One successful system cannot mask another system's exception.
9. Create appointments exactly once. A retry must verify the existing series before creating anything.
10. Send a member completion message only after the accepted event is stored and every required surface is `Succeeded` or `Not Applicable`.

---

## Procedure

### 1. Confirm the request is authorised

Confirm that the selected service has an approved offer version and agreement version. Check that the signed document states the price, billing frequency, effective date and all material inclusions.

If an offer or policy value is unresolved, stop. Record the request as an exception and obtain Peter's decision before giving the member a promise.

### 2. Reconcile identity and current state

Check GHL, Stripe, Trainerize, GHL calendars and all active workbook tabs. Resolve duplicate contacts through the approved identity process before automated acceptance.

Record every current service component, including simultaneous SGPT and PT. Never replace a multi-service state with one single plan label.

### 3. Publish the requested event

Create a version 1 `membership_service_change_requested` event in the operating-data hub. Include the canonical identity, request and effective dates, prior and requested services, agreement evidence and every required surface status.

The requested event must show each surface as `Pending` or `Not Applicable`. Set the GHL change status to `Pending Effective Date`.

### 4. Verify billing

Use Billing OS to resolve the approved target-price allowlist and calculate the first normal weekly boundary on or after 30 paid days from the signed request. Billing OS schedules the current subscription to end and the approved target schedule to start at that identical timestamp.

An exact replay performs no Stripe mutation. A duplicate, unsupported price, paused subscription, conflicting cancellation or schedule-managed subscription sets Billing Action Status to `Exception`, creates one deduplicated Admin Eve task and stops.

### 5. Wait for the effective boundary

Do not advance the active service, workbook rows or member confirmation before the boundary. Re-run the verifier at the boundary because a schedule may have changed after the request was recorded.

Set the overall state to `Processing` only when the boundary has arrived and billing is verified.

### 6. Apply the service atomically

Update the canonical GHL service components, lifecycle, version and updated timestamp. Remove obsolete service tags only after the new state is known and preserve unrelated lifecycle, marketing and historical tags.

Exit obsolete service communications and enter the approved continuing-service journey. Do not write a Membership Pipeline opportunity.

### 7. Reconcile Trainerize and appointments

Verify that Trainerize has the approved account state, program and access. Do not deactivate an account when the new service still includes app access.

Where monthly PT is included, confirm the approved coach, delivery mode, duration, cadence and booking horizon. Verify the exact recurring events after creation and record any gap as an exception.

### 8. Reconcile operating workbooks

Move or update rows only at the effective boundary. An Evolved Anywhere or Online Only relationship belongs in `Active Online` and must not inflate the SGPT or PT KPI unless the approved service genuinely contains those service relationships.

Check `Active Online`, `Active SGPT`, `Active PT`, `Sales` and the relevant cancellation tabs. Preserve the historical sale while correcting current provisioning and service projections.

### 9. Publish the accepted event

When all required surfaces are successful, publish version 2 `membership_service_change_accepted` with the same request fingerprint. The hub rejects acceptance before the effective date.

The accepted event projects the new service relationships and closes the old active relationships. Repeating the exact accepted event is safe and creates no duplicate relationship.

### 10. Verify and close

Read back GHL, billing, Trainerize, appointments, workbooks and the hub. Set Completed Timestamp and send one completion message only after the read-back agrees.

If any read-back fails, publish the next versioned `membership_service_change_exception`. Keep one owned Admin Eve task open until every failed surface is corrected and the next ordered accepted event can be published.

---

## Historical Acceptance Cases

### Sue Goodwin

Sue is the reconciled Evolved Anywhere acceptance example. Her current evidence is one A$69 weekly Evolved Anywhere relationship in `Active Online`, continuing Stripe entitlement and active Trainerize access, with no SGPT or PT KPI relationship.

Her stale GHL membership label and legacy plan tag remain canonical-projection cleanup items. Do not change her entitlement, billing or roster position merely to standardise the label.

### Tania Stiles

Tania's A$69 Evolved Anywhere billing boundary completed on 5 August. The canonical GHL service fields now state Evolved Anywhere, the `bronze` tag has been removed, the Active Online row is present and the stale Active SGPT row is absent. The same Admin Eve task is open as the one exception.

The legacy Trainerize SGPT programme and All Stars membership are removed. Before acceptance, resolve the split GHL identity, make the preserved personalised program current, remove the six manually added group/class credit balances through a safe client-scoped control so app self-booking is unavailable, retain only the personal cap of up to three Strength Group PT sessions monthly through staff-managed bookings, obtain the agreed trainer, recurring Monday time and delivery mode, and create and verify the six monthly 30-minute appointments exactly once. Do not publish an accepted event until each required surface is verified.

---

## Exception Standard

Each exception must identify the request ID, member, failed surface, expected state, observed state, owner and due date. Repeated checks update the same task rather than creating duplicates.

Commercial, legal or policy ambiguity belongs to Peter. Operational cross-system failures belong to Admin Eve, with Peter notified when member access or billing is at risk.

---

## Legacy Writer Retirement Gate

Keep the Membership Pipeline and its writers unchanged until all of the following pass:

1. New-member onboarding publishes canonical initial service state.
2. PT onboarding adds the PT service component without overwriting SGPT.
3. Service change publishes immutable requested and accepted events.
4. The hub reproduces the correct current multi-service state.
5. GHL, billing, Trainerize, appointments and workbooks pass one end-to-end test.
6. A failed handoff creates one deduplicated Admin Eve exception.

After the gate passes, retire writers without deleting historical opportunities. Confirm that no report, workflow or staff process still uses the pipeline as current-service authority.

---

## Revision History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 30/07/2026 | Created the fail-closed service-change control, authority hierarchy, immutable event process, effective-boundary rules, cross-system acceptance gate, Sue acceptance example, Tania pending-boundary case and legacy writer retirement gate |
| 1.1 | 30/07/2026 | Recorded Peter's approved Evolved Anywhere and Online Only terms, published review variation and permanent Legal link, explicit GHL routing, cross-surface service-name cascade and the remaining member-send and fulfilment gates |
| 1.2 | 30/07/2026 | Blocked member use after Peter's public review exposed that the Evolved Anywhere path continued to the Online Only terms; requires a structural GHL route repair and clean two-path retest |
| 1.3 | 31/07/2026 | Split the live build into a dedicated Evolved Anywhere survey and an Online Only duplicate; retained the send gate because an inherited hidden Evolved Anywhere condition and the unfinished Online Only duplicate still prevent clean two-path acceptance |
| 1.4 | 31/07/2026 | Removed 64 inherited cancellation-era conditions from each dedicated survey, reduced both forms to linear three-step paths and passed public acceptance to final acknowledgement without cross-service leakage or submission |
| 1.5 | 31/07/2026 | Recorded Peter's final approval of both member-facing variations; retained the member-send and fulfilment gate until controlled workflow acceptance passes |
| 1.6 | 02/08/2026 | Recorded the automatic exact-boundary Billing OS design, allowlisted target pricing, recoverable exception events, ordered retries and exception-only Admin Eve operating model; live cross-system activation remains gated |
| 1.7 | 02/08/2026 | Recorded the live Online Only Stripe price, deployed hub and Billing OS controls, the two disabled exact-survey GHL workflows, approved Trainerize fulfilment definitions, 204 passing tests and the remaining Trainerize authentication and controlled-acceptance gate |
| 1.8 | 02/08/2026 | Recorded the authenticated `theevolvedgym.trainerize.com` build, both live Main Products and Product Starts rules, the Online Only no-equipment standard program, live configuration read-back, synthetic confirmation dependency and continued Draft/send gate |
| 1.9 | 02/08/2026 | Recorded that the confirmed Evolved Anywhere sale still reads Pending and has not run Product Starts, the Online Only controlled confirmation was sent, and the fail-closed Draft/send gate remains in force |
| 1.10 | 02/08/2026 | Recorded the passing Online Only execution, supported removal and same-profile retry of the stuck Evolved Anywhere purchase, exact live Stripe and workbook rechecks, deduplicated live service-change exception task and continued Draft/send gate |
| 1.11 | 02/08/2026 | Recorded both passing Trainerize execution read-backs, same-profile Evolved Anywhere recovery, verified synthetic deactivation and the remaining post-boundary six-surface accepted-event gate |
| 1.12 | 03/08/2026 | Recorded the approved existing-member Fast Track pathway: A$50 first-session payment, A$149 recurring debit from the next scheduled payment, same-week first session, thirteen specialised weekly 30-minute bookings and an assessment-to-Trainerize programme handoff; PIF excluded pending a separate owner decision |
| 1.13 | 03/08/2026 | Added the Strong-only 12-month A$89 commitment, Queensland cooling-off, fee-disclosure and ongoing-agreement reminder controls, automatic A$99 reversion, quote-only proportional discount recovery, live Stripe allowlist/Billing OS deployment and GHL commitment fields; retained the member-send gate pending signed-in GHL variation/workflow build and synthetic acceptance |
| 1.14 | 04/08/2026 | Ran the controlled COMMIT path with Peter's non-Stripe test contact, detected and corrected the variation email being attached to the ineligible branch, proved `Eligible` then `Send Strong variation link` execution, restored the contact's original service field and returned the workflow to Draft pending the recipient's synthetic signed-variation submission |
| 1.15 | 04/08/2026 | Replaced the COMMIT variation email's inherited location sender with the explicit governed sender `admin@theevolvedgym.com.au`; read-back confirmed the saved sender and the workflow remained Draft |
| 1.16 | 04/08/2026 | Made phone optional on the Strong commitment variation after Australian local-number validation created avoidable friction; public preview acceptance advanced from page one with name and email only and no phone error |
| 1.17 | 04/08/2026 | Reformatted page two of the Strong commitment variation to the canonical member-facing writing rules: regular-weight body copy, short paragraphs, visible section spacing, no em dashes and no more than two sentences per paragraph; removed an inherited duplicate bold terms block without changing the approved terms |
| 1.18 | 04/08/2026 | Removed the duplicate page-three signature field from the Strong commitment variation; retained the single required signature pad bound directly to the full acceptance statement and verified the public path without submission |
| 1.19 | 04/08/2026 | Enabled the page-one phone country picker with Australia (+61) as the default while keeping phone optional; public testing accepted local mobile number `0420863721` exactly as entered and advanced without a format error |
| 1.20 | 04/08/2026 | Passed the Strong commitment end-to-end acceptance gate: captured Peter's signed variation and generated signature document, ran the controlled intake, confirmed Billing OS failed closed for the non-Stripe test contact, verified and completed the same-day Admin Eve exception task, and published the COMMIT Interest, Controlled Intake and Continuation Reminder workflows |
| 1.21 | 04/08/2026 | Created GHL workflow folder `8. Membership Service Changes` and moved all five `MSC` workflows into it; live read-back confirmed the three Strong workflows remained Published and the Evolved Anywhere and Online Only workflows remained Draft |
| 1.22 | 04/08/2026 | Added the retrospective exact-COMMIT reconciliation rule and recorded the first two genuine eligible production enrolments; both completed the governed variation-link action with no signed-variation fields or billing change |
| 1.23 | 05/08/2026 | Recorded Tania's clean Stripe boundary but failed post-boundary six-surface acceptance, leaving both Evolved Anywhere and Online Only workflows Draft; recorded that existing-member Fast Track uses the thirteen-session specialised series instead of acquisition onboarding and scoped a future Strong, Fit & Flexible return/change target |
| 1.24 | 05/08/2026 | Corrected Tania's canonical GHL service projection and legacy tag, added the governed Active Online row, and reopened the same Admin Eve task as one exception. Trainerize access cleanup and an agreed, verified monthly PT series remain the only member-specific acceptance blockers; both Evolved Anywhere and Online Only workflows remain Draft. |
| 1.25 | 05/08/2026 | Removed Tania's legacy Trainerize SGPT programme and All Stars membership, removed the stale Active SGPT workbook row while preserving Sales history, and recorded the verified remaining blockers: split GHL identity, expired/no-current personalised plan, six non-expiring app-bookable class-credit balances, and the missing trainer/time/mode agreement. The same exception remains open; both intake workflows remain Draft and no accepted event or member send was authorised. |
