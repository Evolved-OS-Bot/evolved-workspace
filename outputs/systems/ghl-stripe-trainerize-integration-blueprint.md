# GHL, Stripe and Trainerize Integration Blueprint

**Status:** Lifecycle controls established; reporting and reconciliation build in progress
**Started:** 2026-07-22
**Scope:** Membership provisioning, access lifecycle, reconciliation and active-member reporting

**Execution re-baseline:** The concurrent GHL audit owns live GHL workflow remediation. The focused API and data work now runs through `plans/2026-07-23-trainerize-reporting-reconciliation-sprint.md`, with read-only reconciliation as the default and Trainerize writes deferred until capability and notification testing pass.

## Architectural Decision

Retain the current three platforms and add a small owned integration layer. Do not make any vendor the implicit master of the entire member lifecycle.

```text
GHL lifecycle event        Stripe commercial event
          \                  /
           \                /
            Integration control layer
             | identity and state
             | mappings and rules
             | preview and approval
             | audit log and exceptions
             | reconciliation
                    |
             Trainerize delivery
```

## System Ownership

| Information | Authoritative system | Integration use |
|---|---|---|
| Lead/contact identity and communication consent | GHL | Match and route the member |
| Signed membership/PT agreement | GHL | Confirm commercial acceptance and selected offer |
| Lifecycle state and staff tasks | GHL | Trigger or receive operational exceptions |
| Payment customer, subscription and billing status | Stripe | Confirm payment state and service entitlement |
| Coaching access and client type | Trainerize | Deliver or remove app access |
| Trainer, location, program and coaching activity | Trainerize | Configure and measure delivery |
| Completed workouts and exercise results | Trainerize | Feed operational and de-identified outcome reporting |
| Cross-system IDs, event history and reconciliation | Integration layer | Prevent duplicates and provide audit evidence |

GHL pipeline stage alone is not sufficient proof of active paid membership because the current pipeline mixes Open and Won records. Stripe payment alone is not sufficient because it does not capture every coaching assignment or agreed start date.

## Proposed Canonical Lifecycle

| State | Entry evidence | Trainerize posture | Allowed next states |
|---|---|---|---|
| `assessment_access` | Trainer purchases Initial Consultation product for prospect | Full Access / 1-way; assessment program assigned; initial invitation sent | `assessment_booked`, `assessment_completed`, `exception` |
| `assessment_booked` | Valid GHL assessment appointment plus assessment account | Existing assessment access | `assessment_completed`, `assessment_cancelled` |
| `assessment_completed` | Appointment completed and sales outcome due | Existing assessment access until product end | `sale_pending`, `not_sold` |
| `assessment_expired` | Assessment access remains without a membership sale | Product ends after one day, but no Product Ends access or program-removal action now runs | `reactivation_review`, `sale_pending` |
| `sale_pending` | Offer accepted but agreement/payment requirements incomplete | No new sign-in access | `awaiting_start`, `exception`, `not_sold` |
| `awaiting_start` | Agreement signed, upfront payment successful and start date known | Existing assessment-created account; membership product state pending/active as designed | `active`, `cancelled_before_start`, `exception` |
| `active` | Approved access date reached | Correct active client type | `on_hold`, `cancelling`, `exception` |
| `on_hold` | Approved hold with dates | Policy to be confirmed | `active`, `cancelling`, `exception` |
| `cancelling` | Accepted cancellation and final service date confirmed | Remains active until final service date | `cancelled`, `exception` |
| `cancelled` | Final service date passed and billing reconciled | Deactivated | `reactivation_review` |
| `exception` | Identity, product, payment, date or remote-state conflict | No automated write | Any state after human resolution |

`reactivation_review` is deliberately manual. A former member must not be automatically returned to Basic or full access.

## Provisioning Event Contract

A provisioning candidate must contain:

| Field | Requirement |
|---|---|
| Correlation ID | Stable and unique across retries |
| GHL contact ID | Required |
| Stripe customer ID | Required when Stripe is the billing rail |
| Stripe subscription/payment evidence | Required and classified |
| Normalised email | Required for initial matching, not sufficient as the permanent key |
| Product code | Required and mapped to one current offer; legacy `limited` maps to Fit & Flexible |
| Agreement-complete timestamp | Required |
| Membership start date | Required |
| Initial invitation timestamp | Created by the pre-assessment Initial Consultation purchase; a second invitation is prohibited during normal membership conversion |
| Trainer/location assignment | Required or explicitly marked Admin-selected |
| Trainerize user ID | Added after matching or creation |
| Consent/communication state | Required before member communication |

The integration must reject incomplete events into an Admin exception queue. It must not guess a product, coach, date or identity.

## Initial Offer Mapping Register

| Canonical offer | GHL agreement value | Historical Membership Pipeline stage | Stripe label | Legacy routing | Status |
|---|---|---|---|---|---|
| Fit & Flexible | `Fit & Flexible` | `Fit & Flexible` | To verify | Confirmed `limited / 1 p.wk` branch | Mapping confirmed; missing opportunity stage repaired 24 July 2026. Dependency-check before relabelling. |
| Strong, Fit & Flexible | `Strong, Fit & Flexible` | `Strong, Fit & Flexible Membership` | `Sculpt & Strength` | Confirmed `bronze` | Mapping confirmed; preserve explicit Stripe label mapping |
| Fast Track | `Fast Track Package` | `Fast Track` | To verify | Confirmed `silver` | GHL mapping confirmed; verify Stripe product ID/label |
| Online Only | Not in current three-choice membership field | `Online Only` | To verify | `online client` | Exception/manual until current sale path confirmed |
| PT Only and PT frequencies | Separate PT agreement/process | PT stages | To verify | `personal training`, `pt only`, frequency tags | Separate mapping tranche |

No live integration may use the provisional legacy-routing entries.

The Membership Pipeline column is retained only to interpret historical opportunities. Canonical current service now belongs in the governed GHL `Member: Current Service Components` projection after an accepted onboarding or service-change event.

## Trainerize Capability Register

| Capability | Documentation/account evidence | Sprint decision |
|---|---|---|
| Read active roster and summaries | Verified live | Supported |
| Read calendars, programs and active-client workout detail | Verified live | Supported |
| Add appointment | Public endpoint documented | Test with allowlisted account |
| Create client | Not yet confirmed for this account | Await documentation/support, then test |
| Change client access type | Browser behaviour observed; API support not confirmed | Await documentation/support, then test |
| Deactivate client | Browser behaviour observed; API support not confirmed | Await documentation/support, then test |
| Assign trainer/location | Not yet confirmed | Await documentation/support, then test |
| Assign or create training plan | Public training-plan endpoint exists; required semantics unproven | Test only after delivery design is agreed |
| Add product/package/session credits | No supported endpoint identified | Excluded pending Trainerize confirmation |
| Read detailed deactivated-client workouts | Returns HTTP 403 | Do not work around by reactivation |

## Invitation and Notification Rules

1. The intended initial invitation is sent before the assessment when the trainer purchases the Initial Consultation Trainerize Main Product for the prospect.
2. The membership-sale workflow must resolve and reuse that Trainerize user ID. It must not create a second client or deliberately send another invitation.
3. Creating or moving any client into Basic/full access may send an invitation automatically.
4. Offline accounts do not receive an app invitation.
5. Access activation and invitation sending are treated as an irreversible communication event, even if account status can later be restored.
6. The test plan must record every email, SMS, push and in-app message observed after each write.
7. No live write is approved until its communication side effects are known.

## Verified Initial Consultation Product Behaviour

The product was re-inspected on 23 July 2026 after the owner changed its automation:

- Type: Main Product.
- Price: Free.
- Duration: one day, starting on the day of purchase or after the current Main Product.
- First purchase: Full Access / 1-way messaging, Megan Brown assignment, Strength Assessment main-program subscription and the configured lead tag.
- Product end: no client-type change and no Strength Assessment program-removal action.
- The product itself still has a one-day duration. Removing Product Ends actions prevents the former 24-hour access shutdown, but it does not remove the duration setting.
- Basic is unsuitable for this product because a Basic client cannot receive a training program or track assessment workouts and results.

The conversion design therefore begins with an existing Trainerize identity. Full Access / 1-way preserves the Strength Assessment program and tracking while preventing private two-way messaging.

## Verified Membership Product Gap

The three free 52-week Trainerize Main Products were renamed live on 22 July 2026 to `Membership: Fit & Flexible`, `Membership: Strong, Fit & Flexible` and `Membership: Fast Track`. Each now has an explicit provisioning description. On 23 July, all three were live-verified as `Day of purchase / After current`; staff must override that only when an explicitly agreed future GHL membership start date applies.

Their First purchase automations set Full Access, Megan Brown, The Evolved Gym, an add-on program and The Evolved All Stars group. However, Trainerize states that this automation does not run for existing clients. All normal membership buyers already exist because of the Initial Consultation product.

On 22 and 23 July 2026, Product Starts was configured for the three membership products. Strong and Fast Track receive Full Access / 1-way messaging, the `Evolved All Female Gym` Owner, The Evolved Gym, The Evolved All Stars and their mapped program. Fit & Flexible receives Full Access / 1-way, the Owner and location, but no All Stars group and no membership program because it is attendance-only in Trainerize.

Peter confirmed that the free membership product is currently assigned entirely manually. The historical Drive onboarding SOP records Trainerize setup only as a generic manual checklist item and still references retired ACR/PTMinder operations, so it cannot define the future integration. The controlled calendar test confirmed that an immediate sale can start on the purchase day without shifting the All Stars weekly programming; explicit future starts still use the agreed GHL membership start date.

The legacy first-purchase templates still contain older values for direct new purchasers and should not be treated as the normal converted-member path. Product Starts is the relevant path for the existing assessment account: Fit has no group or program; Strong and Fast Track join All Stars and receive their mapped program. Product Ends remains empty.

The approved target uses Full Access / 1-way messaging and the exact live Owner account `Evolved All Female Gym`. Fit is attendance-only with Cardio and Pilates booking access. Strong and Fast Track join All Stars, receive their mapped membership program and require Smart Meal Plan setup.

Session credits in this account govern timetable bookings, not the onboarding or PT service allocation. The Evolved does not use Trainerize's personal-training credit function. Live inspection found three free 52-week Class Access Add-on Products: Cardio grants 999 non-expiring HybridFit and Metabolic Burn credits; Pilates grants 999 non-expiring Pilates credits; Strength grants 999 non-expiring Build & Balance and Sculpt & Strength credits. Each currently shows only one client, so they reveal the intended entitlement structure but are not yet the standard fulfilment route.

Fit requires Cardio plus Pilates. Strong and Fast require Cardio, Pilates and Strength; Fast's weekly PT remains outside Trainerize credits.

The 22 July synthetic test confirmed that `Class Access: Cardio` issues 999 paid, non-expiring credits for both HybridFit and Metabolic Burn. Cancelling the Add-on does not revoke those balances, but deactivating the client blocks app access. Peter approved retaining the 999-credit model to avoid the larger operational risk of active members losing booking access through expiry or missed replenishment. GHL/Stripe remains the entitlement ledger and Trainerize deactivation is the cancellation hard stop.

The published `Membership Agreement Form: Email` workflow now owns the manual point-of-sale handoff. Each package branch tells the contact's Assigned User to complete Trainerize during the same post-sale consultation before the client leaves, with a one-day due date retained as a fallback control. Admin Eve receives a two-day independent quality-check task.

The canonical staff procedure is `reference/sops/post-sale-member-onboarding.md`. It is the operational source of truth for the manual shadow phase while this integration is built.

## Continuing-Service Change Control

Membership changes reuse the existing Trainerize identity and must not issue another invitation. The service-change request records the prior and requested components, approved effective date, offer and agreement versions, then waits until billing is verified at the boundary.

Trainerize is one independently verified fulfilment surface. A continuing Evolved Anywhere or Online service must retain app access and receive only its approved product, program, group and Class Access state; a successful Stripe schedule cannot prove that Trainerize provisioning is complete.

The accepted hub event is published only after Trainerize, billing, GHL lifecycle, appointments, workbooks and reporting all succeed or are explicitly not applicable. The staff control is `reference/sops/membership-service-change-control.md`.

On 2 August 2026, the approved A$27 Online Only Stripe product and weekly price were created and the automatic exact-boundary Billing OS scheduler was deployed. The two signed GHL survey handoffs were built as Draft workflows with zero enrolments: Evolved Anywhere `f92bde55-73ba-4147-a842-ce53814540ed` and Online Only `dcd08689-755b-41af-9e8c-e2eccb2d8198`.

They remain disabled. The supported Trainerize integration cannot write Main Product or Product Starts configuration, so the authenticated live business UI at `theevolvedgym.trainerize.com` was used to create and read back both definitions. `Membership: Evolved Anywhere` preserves personalised programming while setting Full Access / one-way messaging. `Membership: Online Only` sets the same access and subscribes `At Home: Bodyweight/No Equipment Program`. Both are free 52-week Main Products, start on `Day of purchase / After current`, contain no sessions or group/class actions and are not listed on Trainerize.me.

Controlled Trainerize execution is complete. Online Only is Active with Full Access / one-way messaging, the approved no-equipment program, no Add-ons and no Session Credits. The original Evolved Anywhere pending purchase was removed through Trainerize and is Expired; its replacement on the same product and profile is Active with Full Access / one-way messaging, the existing personal program preserved, no Add-ons and no Session Credits. Both synthetic profiles were deactivated and verified. Stripe scheduling is necessary billing evidence, not proof of calendar, workbook, reporting or accepted-event completion.

The member-facing review variation is published with Peter's approved commercial terms and permanent Legal-page link. Member send and the active GHL fulfilment workflow remain gated on Peter's final review and controlled end-to-end acceptance.

The six saved actions specify identity reuse, the exact Main Product and Class Access products, access, Owner, location and package-specific group/program rules. Strong and Fast Track setup and QA now also require the Smart Meal Plan; Fit explicitly receives no All Stars group and no membership training program.

Trainerize limits a product to two session types, while The Evolved has five timetable types. The workflow therefore instructs staff to assign the separate Class Access products: Fit receives Cardio and Pilates; Strong and Fast receive Cardio, Pilates and Strength. The redundant draft workflows `Membership: Trainerize Provisioning Task` and `Membership: Trainerize Provisioning Task - Strong` were deleted on 22 July 2026 and remain recoverable from GHL's Deleted tab for 30 days.

Automatic Membership Control is currently off, so the 52-week expiry does not auto-deactivate clients. Keep it off during the sprint, leave Product Ends empty, and use day-330/day-350 reconciliation alerts before testing a queued renewal. GHL/Stripe remains the entitlement source and cancellation remains tied to the verified final service date.

Immediate-start timing is resolved. On 23 July 2026, two Evolved-owned synthetic Full Access / 1-way clients received the Strong product with purchase-day and next-Monday starts. After accepting both confirmations, Peter inspected both calendars and verified the correct All Stars programming on the correct calendar days. All three live membership products now default to `Day of purchase / After current`; an explicitly future-dated membership must instead use its recorded GHL start date. Both synthetic clients were deactivated, permanently deleted and verified absent after the test.

## Identity Resolution

Resolution order:

1. Stored Trainerize user ID linked to the GHL contact.
2. Stored Stripe customer ID linked to the GHL contact.
3. Exact normalised email match, accepted only when it returns one record in each relevant system.
4. Otherwise, stop and create an exception.

Name-only matching, fuzzy matching and automatic merging are prohibited. Email changes must be handled as an explicit identity-maintenance event.

## Execution Modes

| Mode | External writes | Intended use |
|---|---:|---|
| `inventory` | None | Read configuration and report readiness |
| `preview` | None | Produce proposed actions and validation failures |
| `test` | Allowlisted test IDs only | Prove endpoint and notification behaviour |
| `approval_required` | One approved action at a time | Initial live shadow rollout |
| `automatic` | Approved action classes only | Mature operation after reconciliation passes |

Any missing or invalid mode must behave as `preview`.

## Audit Record

Every attempted action must store:

- correlation and idempotency keys;
- source system and source event ID;
- target system and target record ID;
- precondition state;
- redacted proposed payload;
- execution mode and approving operator, if applicable;
- result, timestamps and remote response category;
- notification side-effect classification;
- compensating action and its result, if used.

The log must never contain API tokens, full health information, payment details or unnecessary personal information.

## Exception Queue

Initial exception classes:

- duplicate contact or client;
- no matching Trainerize client where one is expected;
- conflicting GHL and Stripe product states;
- missing agreement, payment, start date or trainer;
- unmapped legacy tag;
- unexpected current Trainerize status;
- remote write failure or timeout;
- attempted former-member reactivation;
- reconciliation mismatch after execution.

Each exception must create one persistent GHL Admin task with a correlation ID and a plain-language resolution instruction.

## Controlled Test Protocol

1. Use inboxes owned by The Evolved and names containing `TEST`.
2. Add the test identities to a hard allowlist.
3. Capture the initial GHL, Stripe and Trainerize states.
4. Run preview and compare the proposed action with the expected result.
5. Approve one write operation.
6. Record the API response and all member-facing notifications.
7. Re-read the remote state and verify it matches the expected state.
8. Perform the compensating action where safe.
9. Re-read again and record any irreversible side effect.
10. Mark the capability supported only after the whole sequence passes.

## Immediate Decisions Required

1. What do the `Membership: Strong, Fit & Flexible` and `Membership: Fast Track` Master Programs actually deliver?
2. Can Trainerize Support provide a supported credit-revocation method, or must the integration use a limited replenished balance?
3. Where are the Strong/Fast meal plan and grocery list currently delivered?
4. What Trainerize access posture should apply during an approved membership hold?

## Next Build Artifact

The first preview-only harness now exists at `scripts/preview_trainerize_membership.py`. It validates synthetic sale evidence, resolves current and legacy offer labels, requires the existing Trainerize user ID, proposes the correct membership Main Product with the recorded GHL start date, and prohibits both client creation and a second invitation. It makes no external calls. The next build step is to add read-only identity/state resolution after the coach, program, group and location mappings are approved.
