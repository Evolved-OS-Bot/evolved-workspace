# Membership Service Change Control

**Status:** In Progress: automatic billing and recoverable hub control built locally; live cross-system activation remains gated
**Created:** 30 July 2026
**Owner:** Admin Eve for operational control; Peter Brown for offer and policy approval

## Objective

Build one governed service-change process for members who retain their relationship with The Evolved but move between service levels.

The process must convert an accepted and signed change into the correct effective service across GHL, billing, Trainerize, appointments, operating workbooks and reporting. It must fail closed when any required action is missing or ambiguous.

## Confirmed Product Intent

- Evolved Anywhere and Online Only are legitimate retention services.
- They are internal downgrade or continuity options, not current acquisition offers.
- Evolved Anywhere is A$69 per week, with one 30-minute PT session every four weeks and personalised programming.
- A member should sign a concise service-change variation that explains the new service, price and policies. They should not need to re-sign the complete original membership agreement.
- Fast Track existing-member upgrades are now an approved extension of this control: collect an immediate A$50 first-session payment, change the recurring membership to A$149 per week on the next scheduled debit, book the first PT session in the same week and create thirteen weekly specialised 30-minute PT bookings. Each request carries the assessment rationale, priority gap or gaps, selected next standard, initial 8–12 week focus, progression and approved specialised twelve-week Trainerize programme. PIF is out of scope for this release. The exact Fast Track variation, target configuration and controlled acceptance remain to be implemented.
- For an existing-member Fast Track conversion, the thirteen-session specialised series replaces the acquisition four-session onboarding pathway. It must not be represented as four generic onboarding sessions plus nine later PT sessions.
- A return or change to Strong, Fit & Flexible is now scoped as a future target of this same control, for both Fast Track downgrades and changes from another membership. It must use the canonical A$99 Strong offer, preserve the exact prior-service boundary and remove only services that end. Before it can be built or sent, Peter must approve the notice/effective-date rule and the treatment of any already-booked Fast Track PT sessions; no separate client database or generic cancellation path is permitted.
- Admin Eve owns the operational transition and exception queue.

## Evidence Reconciled

The existing cancellation system already offers Hybrid and Online Only for permanent travel and schedule-related cancellations. `reference/product-offerings.md`, the cancellation build guides and July journal entries all confirm that these are deliberate retention products.

The Hybrid/Online survey has two signed submissions:

| Submitted | Member | Selection | Current evidence |
|---|---|---|---|
| 22 May 2026 | Sue Goodwin | Hybrid at $69 per week | Already reconciled as the current Evolved Anywhere hybrid service across GHL, Stripe, Trainerize, Active Online and reporting |
| 2 July 2026 | Tania Stiles | Evolved Anywhere at $69 per week | Stripe billing completed at the 5 August boundary. Canonical GHL fields and the Active Online projection are corrected; the legacy `bronze` tag is removed. The existing Admin Eve task is reopened as the one exception for Trainerize access cleanup and an agreed, verified six-month monthly PT series. The Membership Pipeline is not a target authority. |

## Approved Offer and Policy Decisions

Peter approved the commercial and operating decisions on 30 July 2026. The published form is the final review variation; it must not receive an automatic fulfilment trigger until Peter completes that review and the controlled cross-system acceptance passes.

### Decision register before member-facing publication

The approved positions are:

| Decision | Approved operating position | Control note |
|---|---|---|
| Canonical service name | Use `Evolved Anywhere` for the A$69 service and retain `Hybrid` only as a legacy alias | Stripe and current rosters already use Evolved Anywhere, but this changes member-facing naming |
| Online Only price | A$27 per week | Replaces the old survey's A$29 wording |
| Evolved Anywhere SGPT access | No routine group access; Tania alone temporarily retains up to three Strength Group PT sessions per month under her documented historical promise | The exception is identity-specific and must not become the standard product |
| Monthly PT mode | One 30-minute session every four weeks, in person or virtual by mutual agreement | Delivery mode and booking capacity affect the commercial promise |
| Programming and support | Personalised Trainerize program, normal program modifications and normal coach support; no promise of unlimited or immediate messaging | The member-facing terms now state the support boundary |
| Missed PT session | The session expires within each four-week period; at least 24 hours is required to reschedule; late cancellation or no-show forfeits the session; no rollover, cash conversion, transfer or discretionary exception | The clause is deliberately unambiguous |
| Notice and access | Thirty paid days; the old service and access continue until the approved boundary | This matches the historical cases but needs an express policy decision |
| Holds, cancellation and later changes | Apply the standard membership hold and cancellation rules; every later service change requires a new versioned variation | These rights must be stated accurately and consistently |
| Legal links and review | Use `https://theevolvedgym.com.au/legal` for both the Privacy Policy and Terms of Use; Peter reviews the final published variation before member send | The live Legal page contains both documents |

## Required Variation Agreement

Replace the current survey wording with a versioned `Membership Service Change Variation`.

It should capture:

- member identity and existing membership;
- selected new service;
- weekly price and billing frequency;
- request date and effective date;
- inclusions and exclusions;
- access during the notice period;
- PT booking and expiry rules where applicable;
- Trainerize access and coaching-support rules;
- hold, cancellation and further-change policy;
- acknowledgement that unchanged terms in the original agreement continue;
- Privacy Policy and Terms links;
- initials and signature;
- agreement version and signed timestamp.

The review variation is published at `https://links.theevolvedgym.com.au/widget/survey/zFxqvzogSZFbeGDnNM8Q`. Publication does not authorise automated fulfilment or member send before Peter's final review.

## Target Operating Flow

1. A retention owner or Admin Eve records the accepted service change and sends the correct variation.
2. Submission creates one immutable service-change request ID.
3. The workflow snapshots the prior service, selected service, commercial terms, request date, notice boundary and signed agreement.
4. The workflow validates identity, current service, active cancellation or hold state, billing record and approved offer version.
5. The request enters `Pending Service Change`. It does not immediately overwrite current service fields.
6. A clean request schedules automatically. Admin Eve receives no routine approval task.
7. At the effective boundary, Billing OS validates and applies or acknowledges the correct recurring charge.
8. Only after billing succeeds, the workflow updates:
   - canonical GHL service and lifecycle fields;
   - old and new plan tags;
   - active, cancellation and hold status;
   - old-service nurture exits and new-service enrolments;
   - Trainerize product, program and access;
   - recurring PT appointments when included;
   - Active Online, Active SGPT, Active PT and Sales records as applicable;
   - reporting-hub entitlement and service relationships;
   - one versioned accepted service-change event for downstream reconciliation and Member Growth measurement.
9. A member confirmation states the effective service, price, access and next booked action.
10. A post-write verifier checks every required surface. Any failure creates a deduplicated same-day Admin Eve task and leaves the request in `Exception`, not `Completed`.

An exception is recoverable rather than terminal. The hub keeps the original request locked, accepts versioned exception evidence, and permits a later accepted event only when the next event version is exact and every surface has recovered.

## Minimum Control Fields

- Service Change Request ID
- Prior Service
- Selected Service
- Request Date
- Effective Date
- Change Status
- Agreement Version
- Signed Timestamp
- Signature Document
- Billing Action Status
- GHL Lifecycle Status
- Trainerize Provisioning Status
- Appointment Provisioning Status
- Workbook Reconciliation Status
- Reporting Acceptance Status
- Last Error
- Completed Timestamp

## Historical Remediation

### Sue Goodwin

Retain the existing governed correction as the acceptance example. Verify that the new canonical service name can represent her without changing current entitlement or creating an SGPT/PT KPI relationship.

### Tania Stiles

The 5 August remediation completed the canonical GHL and current-roster correction. The immutable accepted event remains blocked pending the remaining controlled evidence:

1. retain the confirmed A$69 billing boundary and corrected Evolved Anywhere GHL/Active Online state;
2. retain the verified removal of the legacy Trainerize SGPT programme and All Stars membership, then make the preserved personalised program current and safely revoke the six manually added non-expiring group/class credit balances without changing shared event types or deactivating Tania;
3. resolve the split phone/current-service and email/marketing GHL identities through the approved identity process;
4. obtain agreement to the PT trainer, recurring Monday time and in-person or virtual mode, then book and verify six monthly 30-minute appointments exactly once;
5. read back every governed surface and record the completed service-change event in the reporting hub;
6. do not repair or update the legacy Membership Pipeline as part of the service change.

## Acceptance Tests

- A signed variation cannot silently stop after writing contact fields.
- A duplicate submission does not duplicate billing, appointments or roster rows.
- A second service-change request cannot overwrite an active pending request.
- The old service remains authoritative until the approved effective boundary.
- A billing failure cannot produce a completed member confirmation.
- Every required system agrees on current service after completion.
- An excluded service is not left enrolled in old member communications.
- Evolved Anywhere appointments are created exactly once and match the approved frequency.
- A manual correction is fully auditable and can be rechecked without repeating successful actions.
- Sue and Tania both reconcile without unsupported roster or KPI inflation.

## Delivery Sequence

1. Approve service names, prices, access and policy rules.
2. Draft and legally review the variation agreement.
3. Create canonical service-change fields and statuses.
4. Build the Admin Eve-owned fail-closed workflow and Billing OS action.
5. Connect Trainerize, appointment, workbook and reporting updates.
6. Reconcile Tania in read-only mode, then apply owner-approved corrections.
7. Test with a controlled contact.
8. Publish the form and workflow.
9. Create the staff SOP and update all workspace system documents.
10. Monitor the first three live changes with manual post-write verification.

## Legacy Opportunity Writer Dependency Gate

The Membership Pipeline is no longer the intended client database or growth-intelligence source. Preserve its existing opportunities as history.

Do not remove the legacy onboarding opportunity actions until:

1. new-member onboarding publishes the canonical initial service state;
2. PT onboarding publishes the canonical PT service component without overwriting simultaneous SGPT service;
3. this service-change workflow publishes an immutable requested and accepted service-change event;
4. the operating-data hub accepts those events and reproduces the correct current multi-service state;
5. GHL fields, billing, Trainerize, appointments and workbooks reconcile in an end-to-end test;
6. a failed handoff produces a deduplicated Admin Eve exception.

After those gates pass, remove the live Membership Pipeline writers, preserve the historical records and verify that no reporting, onboarding or staff process depends on the pipeline.

## Implementation Record: 30 July 2026

### Completed

- Reconciled Sue Goodwin as one current A$69 Evolved Anywhere service in Active Online with Stripe and Trainerize continuity, without creating an SGPT or PT KPI relationship.
- Reconciled Tania Stiles in read-only mode. Her A$99 subscription ends and the A$69 schedule starts at the exact 5 August Brisbane boundary; her old Active SGPT row correctly remains current until then.
- Identified Tania's unresolved Trainerize access and monthly PT series after the 5 August boundary; canonical GHL service fields, tag cleanup and Active Online projection were remediated under one existing exception task.
- On the 5 August post-boundary continuation, used Trainerize's supported unsubscribe control to remove Tania's legacy `2026 SGPT Program`; full group-member read-back proved she is no longer in `The Evolved All Stars`. Full Access / one-way messaging and `Tania's program` remain, but the profile reports `Main program expired` and `No current training plan`, while six manually added non-expiring group/class credit balances still permit app self-booking and expose no safe client-level revoke control.
- Re-read the live workbook and removed only Tania's stale Active SGPT row. Her A$69 Active Online row remains with `Pending agreement`, the original Sales record remains preserved, and no other roster row was changed.
- Re-read both GHL identities, the full relevant conversation, tasks and all 30 calendars. Tania agreed Monday only; trainer, recurring time and delivery mode remain unagreed, zero future monthly appointments exist, and the service-change record remains split from the email/marketing contact. The existing Admin Eve task and `SC: Last Error` were updated in place; no second task was created.
- Re-read Stripe as one exact customer with one active A$69 weekly subscription and paid latest invoice; the former A$99 subscription is cancelled at the boundary. Both intake workflows remain Draft. No accepted event, enrolment, appointment or member message was created.
- Created the live GHL Contact folder `6. Membership Service Change` and 22 governed fields. A second run proved the creator is idempotent.
- Added immutable requested, accepted and exception event contracts to the operating-data hub. Changed replays, concurrent pending requests, incomplete surface state and premature acceptance fail closed.
- Added idempotent accepted-state projection that closes old service relationships and opens the new multi-service relationships exactly once.
- Deployed the approved service-name and service-change contract build as Railway deployment `968740e7-984f-4a81-987b-941ba2ad3868`.
- Added a read-only Billing OS verifier for the exact Stripe customer, current price, target price and Brisbane effective boundary.
- Deployed Billing OS as Railway deployment `aa8b4aa7-5377-4c48-8ef1-e8fb1fa03d60`.
- Added the staff SOP at `reference/sops/membership-service-change-control.md` and removed the Membership Pipeline from current-service authority in the active-client reconciliation SOP.
- Left the Membership Pipeline and all legacy opportunity writers unchanged.
- Renamed the A$69 service to `Evolved Anywhere` across the workspace, retained WordPress homepage source, live GHL homepage, Active Online workbook and Stripe product `prod_Q4F6YgdNRNCqjM`, while preserving all Stripe price and subscription IDs.
- Published the versioned GHL `Membership Service Change Variation` at survey `zFxqvzogSZFbeGDnNM8Q` with the approved A$69 and A$27 terms, permanent Legal-page link, three initials controls and signature.
- After the combined-form route failed Peter's review, renamed survey `zFxqvzogSZFbeGDnNM8Q` to `Membership Service Change Variation - Evolved Anywhere` and reduced its saved structure to details, Evolved Anywhere terms and final acknowledgement.
- Created Online Only survey `XBpTy848fvJXjMtGfnu2` and reduced it to details, Online Only terms and final acknowledgement.
- Removed all 64 inherited cancellation-era conditions from each dedicated survey. Both saved structures reload with no service-choice slide, no cross-service terms and no hidden conditions.
- Kept member send fail closed pending Peter's final review and the governed workflow acceptance gate.
- Verified 63 active Trainerize client records contain no retired service-name occurrence.

### Test evidence

- Full operating-data hub regression suite: 121 tests passed.
- Combined service-change regression selection across the hub, Stripe handler, revenue-gap control, PT booking and reconciliation: 295 tests passed.
- Billing OS suite: 22 tests passed.
- Live GHL field creator: 22 created, then 22 skipped on an exact idempotency rerun.
- Live Tania Stripe verification: one scheduled A$69 weekly phase begins at the exact boundary and no Stripe mutation was performed.
- Public GHL route acceptance: Evolved Anywhere passed details to Evolved Anywhere terms to final acknowledgement without Online Only terms. Online Only passed details to Online Only terms to final acknowledgement without Evolved Anywhere terms. Both stopped at `SUBMIT`; neither test form was submitted.
- Active Online rename: three exact cells changed and read back as Evolved Anywhere for Anne Leditschke, Tammy Harper and Sue Goodwin.
- Stripe catalogue read-back: active product `prod_Q4F6YgdNRNCqjM` is `Evolved Anywhere` with the approved limited-support description.
- Live homepage read-back: the public root domain contains `Evolved Anywhere` and no retired service-name occurrence.
- Railway deployment `968740e7-984f-4a81-987b-941ba2ad3868` reached `SUCCESS`; `/health` returned `status: ok`.

### Still gated

- Peter approved both dedicated member-facing variations on 31 July 2026. Member send remains gated on the controlled request, accepted-event and deduplicated Admin Eve exception tests.
- Active GHL fulfilment workflow and immutable request handoff from the survey.
- A controlled-contact test proving Billing OS, GHL lifecycle, Trainerize, appointments, workbooks, hub acceptance and one deduplicated Admin Eve exception.
- Tania's 5 August effective-boundary processing.
- Canonical initial-service capture from onboarding.
- Retirement of legacy Membership Pipeline writers.

## Implementation Record: 2 August 2026

### Completed locally

- Replaced the read-only Billing OS service-change path with an allowlisted automatic scheduler for approved target services.
- The scheduler computes the first normal weekly Stripe boundary on or after 30 paid days from the signed request. It writes the old subscription end and new schedule start at the same exact timestamp.
- Added deterministic Stripe idempotency keys, exact replay verification, duplicate-schedule rejection, paused and schedule-managed subscription guards, and rollback of a newly created future schedule if ending the current subscription fails.
- Made the immutable hub request a prerequisite to Stripe mutation. Billing failure after request acceptance appends a recoverable exception event and creates the existing deduplicated Admin Eve task.
- Added exact `effective_at` evidence to the hub while retaining the Brisbane effective date projection.
- Corrected the hub state machine so exception evidence does not permanently block a repaired request. Event versions must advance by exactly one.
- Verified the Brown & Casserly workbook schema read-only. `Active Online` is the target current-service roster; SGPT and PT KPI rows remain separate and are not inferred from the Evolved Anywhere inclusion.
- Scrubbed the retired service name from the remaining ignored private workspace snapshots.

### Automated evidence

- Billing OS: 29 tests passed.
- Operating Data Hub: 228 tests passed in the latest 2 August regression run.
- Combined Billing OS plus hub control evidence: 257 tests passed in the latest 2 August regression run.
- Stripe tests cover exact-boundary scheduling, exact replay without mutation and rollback after a partial write failure.
- Hub tests cover duplicate and concurrent requests, exact boundary acceptance, ordered event versions, recoverable exception evidence and later acceptance.

### Live activation state

- Stripe has one verified active Evolved Anywhere A$69 weekly price, `price_1T8qw9LMsHYOAUEzfyEKLxyC`.
- The approved Online Only product `prod_UzmDLNJzNPbQ0c` and active A$27 AUD weekly price `price_1Tzmf1LMsHYOAUEz4acEj4EA` were created idempotently and read back on 2 August.
- Operating Data Hub deployment `28a1f6fc-b636-41a1-83fb-c46d0bce311c` is healthy in shadow mode. It has 20 sources and no stale source.
- Billing OS deployment `77c83831-fd0d-4337-9f05-31d0fd6bc505` is healthy. Its live service-change route rejects an empty request with the expected fail-closed `400` response.
- GHL workflow `f92bde55-73ba-4147-a842-ce53814540ed`, `MSC | Evolved Anywhere | Controlled Intake`, is saved as Draft with the Evolved Anywhere survey trigger and allowlisted Billing OS handoff.
- GHL workflow `dcd08689-755b-41af-9e8c-e2eccb2d8198`, `MSC | Online Only | Controlled Intake`, is saved as Draft with the Online Only survey trigger and allowlisted Billing OS handoff.
- Both workflows have zero enrolments and contain no client-facing send. Draft status is intentional.
- Peter approved the Trainerize fulfilment definitions. Evolved Anywhere retains personalised programming, Full Access with one-way messaging, and no group or class access. Online Only receives a distinct standard program, Full Access with one-way messaging, no group or class access, and no coaching.
- The correct live business URL is `https://theevolvedgym.trainerize.com`. The saved Evolved business session was authenticated and used on 2 August.
- Created free 52-week Main Product `Membership: Evolved Anywhere`. It starts on `Day of purchase / After current`, is not sold on Trainerize.me, includes no sessions, and its saved Product Starts rule sets Full Access / one-way messaging only. It intentionally adds no program, group or class action so an existing personalised program is retained.
- Created free 52-week Main Product `Membership: Online Only` with the same start and visibility controls. Its saved Product Starts rule sets Full Access / one-way messaging and subscribes the distinct standard `At Home: Bodyweight/No Equipment Program`; it adds no group, class or coaching action.
- Read-back of both Product Starts configurations passed in the live UI.
- Controlled Trainerize acceptance passed for both approved definitions. Online Only is Active with Full Access / one-way messaging, Main Product `Membership: Online Only`, standard program `At Home: Bodyweight/No Equipment Program`, no Add-ons and no Session Credits. The original Evolved Anywhere attempt remained `Pending` after email confirmation, so it was removed using Trainerize's supported pending-purchase control and became `Expired`. The same existing product was re-sold to the same existing profile; after the newest confirmation, the replacement became Active with Full Access / one-way messaging, Main Product `Membership: Evolved Anywhere`, the existing `MSC EA's program` preserved, no Add-ons and no Session Credits. No duplicate product or profile was created.
- Both synthetic acceptance profiles were moved from Coaching to Deactivated after their execution read-backs and were found exactly once in Trainerize's Deactivated view.
- Live GHL read-back reconfirmed both intake workflows are Draft with zero total and zero active enrolments. No member-facing send or automatic fulfilment was enabled.
- Live read-only Stripe verification reconfirmed Tania's current A$99 subscription and future A$69 schedule meet at the exact `2026-08-05 00:00:00 AEST` boundary with mutation `none`. She is not accepted before that boundary.
- Corrected the workbook verifier's cancellation-tab names from singular to the live `SGPT Cancellations` and `PT Cancellations`. Read-only live verification now finds all six required tabs: Active Online, Active SGPT, Active PT, Sales and both cancellation tabs.
- A disposable non-deliverable GHL contact proved the live service-change exception path creates one same-day Admin Eve task and an exact retry does not duplicate it. The test contact was deleted after verification.
- The currently deployed task title renders `Service_Change`; the local Billing OS correction renders the staff-readable `Service Change` and is covered by the 29 passing Billing OS tests. It is not deployed while the overall activation gate remains closed.
- Trainerize execution and cleanup, the exact Stripe boundary, all six workbook tabs and the deduplicated Admin Eve exception gate now pass. Do not publish either GHL workflow or enable member send until one clean six-surface accepted event verifies GHL, billing, Trainerize, appointments, workbooks and reporting after its effective boundary.
- Tania remains pending. Her accepted event and roster move are prohibited before `2026-08-05 00:00:00 AEST`.
