# GHL, Stripe and Trainerize 90-Day Integration Sprint

**Status:** Re-baselined and superseded for execution
**Started:** 2026-07-22
**Owner:** Peter Brown
**First implementation gate:** Test accounts only

> Re-baselined 23 July 2026: the concurrent GHL audit implemented or verified much of the lifecycle-control scope anticipated here. Continue execution through `plans/2026-07-23-trainerize-reporting-reconciliation-sprint.md`. This document remains the historical control-design record.

## Objective

Reduce post-sale administration and lifecycle errors without replacing the current operating stack.

GHL remains the source of truth for contacts, agreements, lifecycle state and communications. Stripe remains the source of truth for payments and subscriptions. Trainerize remains the source of truth for coaching access, programming and completed training. The integration layer coordinates the three systems and records every proposed and completed action.

## Day 90 Definition of Done

1. A verified sale produces one correctly matched Trainerize client with the intended access timing, trainer, location and starting delivery configuration.
2. A cancellation schedules access removal for the confirmed final service date.
3. Repeated events do not create duplicate clients, invitations, appointments or tasks.
4. Failed or ambiguous cases create an assigned Admin exception rather than silently continuing.
5. A nightly reconciliation identifies roster and lifecycle mismatches across GHL, Stripe and Trainerize.
6. Active-member workout and strength metrics refresh on a defined schedule without changing member access.
7. Every write has an audit record containing the source event, proposed action, result, timestamp and correlation ID.

## Non-Goals for This Sprint

- Replacing GHL, Stripe or Trainerize.
- Building a member-facing workout application.
- Automating Trainerize session-credit balances without a supported entitlement endpoint.
- Reading detailed historical workouts by reactivating former members.
- Changing any real account solely to test API behaviour.

## Phase 1: Integration Readiness, Days 1-14

### Work

1. Use the confirmed sale-complete rule: signed agreement, successful upfront payment and recorded membership start date.
2. Reconcile current offer names, legacy tags, pipeline stages, agreement choices and Stripe product names. The legacy `limited` branch is confirmed as Fit & Flexible.
3. Define lifecycle states and the permitted transitions between them.
4. Define invitation timing separately from client-record creation.
5. Establish persistent cross-system identifiers and duplicate-handling rules.
6. Inventory Trainerize write capabilities from official documentation, then prove only the required operations with allowlisted test accounts.
7. Define audit logging, preview mode, idempotency, exception routing and reconciliation.
8. Document the manual shadow process used before enabling each live action.
9. Use `reference/sops/post-sale-member-onboarding.md` as the canonical manual shadow procedure and measure completion of its consultant and Admin Eve controls.

### Exit Criteria

- The product mapping has no unresolved live offer branch. The confirmed `limited` to Fit & Flexible mapping must be dependency-checked before the live branch or tag is renamed.
- The sale event requires a signed agreement, successful upfront payment and recorded start date.
- The cancellation event includes a verified final service date.
- Invitation timing is explicitly defined for each product.
- Test identities are owned by The Evolved and clearly labelled as tests.
- Each proposed Trainerize write is classified as supported, unsupported or awaiting Trainerize confirmation.
- Preview mode can produce an action plan without changing any external system.

## Phase 2: Post-Sale Provisioning, Days 15-40

### Target Flow

```text
Trainerize Initial Consultation product purchase
  -> trainer purchases the product for the prospect
  -> create the Full Access / 1-way assessment client and send initial app access
  -> deliver the Strength Assessment program
  -> after one day, no Product Ends access or program-removal action runs

Verified membership sale
  -> resolve one GHL contact
  -> resolve one Stripe customer and subscription
  -> resolve the existing assessment-created Trainerize client
  -> validate product mapping, start date, trainer and location
  -> preserve the existing identity and do not send a second invitation
  -> override the assessment-expiry posture through the supported membership-product path
  -> assign supported delivery configuration
  -> write audit result
  -> create Admin exception for anything ambiguous
```

### Rollout

1. Synthetic-event preview.
2. Test-account execution.
3. Real-sale shadow mode with no writes.
4. Admin-approved execution for a small live cohort.
5. Automatic execution only after reconciliation is consistently clean.

## Phase 3: Holds and Cancellations, Days 41-60

1. Read the accepted GHL cancellation record and notice-end date.
2. Reconcile the Stripe cancellation schedule and final paid service period.
3. Calculate one final service date and expose disagreements as exceptions.
4. Schedule Trainerize access removal for that date.
5. Stop member-only GHL communications and update lifecycle state.
6. Preserve the minimum records required for operational, financial and legal purposes.

No automated deletion of personal information is included. Deletion requests follow a separate reviewed process.

## Phase 4: Reporting and Reconciliation, Days 61-90

1. Compare active GHL members, active Stripe subscriptions and active Trainerize clients nightly.
2. Report missing accounts, duplicate identities, stale access, product mismatches and overdue cancellations.
3. Refresh aggregate workout, adherence and strength-progression measures for active members.
4. Keep identified operational data private and publish only approved de-identified analysis.
5. Establish alert ownership, response times and resolution evidence.

## Known Readiness Findings

- `3.0 New Member` is live and routes on legacy tags including `bronze`, `silver`, `gold`, `limited`, `1 p.wk` and `2 p.wk`.
- The `limited / 1 p.wk` branch is confirmed as Fit & Flexible. Its opportunity action was repaired on 24 July 2026 by assigning the Fit & Flexible Membership Pipeline stage; the warning cleared and the published workflow was saved.
- The Membership Agreement has three current choices: Fit & Flexible; Strong, Fit & Flexible; and Fast Track Package.
- Stripe still labels the middle membership `Sculpt & Strength`; this requires an explicit mapping rather than a rename during this sprint.
- GHL now has branch-specific consultant setup and Admin QA tasks inside `Membership Agreement Form: Email`.
- The cancellation workflow already calculates a notice-end date and calls Stripe, but Trainerize deactivation is manual.
- Trainerize Basic and full-access account changes can send an invitation. Offline clients do not receive app invitations.
- The trainer purchases the live `Initial Consultation` Main Product for the prospect. It lasts one day and now sets Full Access / 1-way messaging, assigns Megan Brown, subscribes the Strength Assessment main program and adds the configured lead tag. Product Ends now has no access or program-removal action, which removes the former 24-hour shutdown.
- Basic is not suitable for Initial Consultation because it cannot receive the Strength Assessment program or track workout results.
- Trainerize access and the first invitation are intentionally delivered before the assessment. Membership conversion must reuse that account and must not create or invite a second client.
- Fit & Flexible, Strong, Fit & Flexible and Fast Track are free 52-week Trainerize Main Products set to `Day of purchase / After current` for self-purchases. Their First purchase actions do not run for the existing assessment client. On 22 July 2026, Product Starts was configured and verified for all three; staff override the default only for an explicitly future-dated GHL membership start.
- Staff currently assign the post-sale free Trainerize membership product entirely manually. The historical Drive onboarding SOP confirms Trainerize setup was a manual checklist item, but its ACR/PTMinder references and missing current product rules make it unsuitable as the new specification.
- Explicit future starts use the recorded GHL membership start date. On 23 July, two Evolved-owned synthetic clients tested Strong with purchase-day and following-Monday starts. Both confirmations completed, and Peter verified that both calendars contained the correct All Stars programming on the correct days. The immediate-start default is approved.
- The first-purchase templates are fully mapped: all three set Full Access / 2-way messaging, Megan Brown, The Evolved Gym and The Evolved All Stars; Fit and Strong subscribe the Master Program now named `Membership: Strong, Fit & Flexible`, while Fast Track subscribes `Membership: Fast Track`. They contain no main-program, session or meal-plan action.
- Product Starts now applies access, Owner and location for all three products. Strong and Fast join All Stars and receive their mapped program; Fit is attendance-only and receives neither group nor program. Product Ends remains empty, so the 52-week product expiry cannot be treated as the cancellation or entitlement-removal event.
- The shared `Membership: Strong, Fit & Flexible` Master Program cannot prove strength-class access because Fit's legacy first-purchase rule also selects it despite Fit and Strong having different contractual inclusions. Class entitlement remains separate.
- The approved target is Full Access / 1-way messaging for all three products and `Evolved All Female Gym` as the default Owner account. Fit has no All Stars group or training program. Strong receives `Membership: Strong, Fit & Flexible`; Fast receives `Membership: Fast Track`; both require Smart Meal Plan setup.
- Automatic Membership Control is currently off. The 52-week expiry will not auto-deactivate clients, but renewal must be reconciled before day 365.
- Trainerize session credits in this account control timetable booking, not PT or onboarding delivery. Live Class Access add-ons use 999 non-expiring credits for Cardio (HybridFit and Metabolic Burn), Pilates, and Strength (Build & Balance and Sculpt & Strength). Fit maps to Cardio + Pilates; Strong and Fast map to all three. Cancelling an Add-on retains the credits, while deactivating the client blocks app access. The approved operating decision is to retain the simple 999-credit model and use deactivation as the cancellation hard stop.
- The published `Membership Agreement Form: Email` workflow now tells the Assigned User to complete Trainerize during the same post-sale consultation, with a one-day due date retained as a fallback. Admin Eve independently verifies by day two. Smart Meal Plan is required for Strong/Fast; Fit is explicitly attendance-only with Cardio and Pilates access. The start-date test passed and both synthetic clients were permanently removed; monitor the first 20 handoffs.
- The public Trainerize API documents appointment creation. Client creation, access-level change, deactivation, trainer/program assignment and entitlement writes still require controlled capability confirmation for this account.

## Safety Gates

1. **Allowlist:** Write-capability tests may target only explicit test Trainerize user IDs.
2. **Preview by default:** A missing execution flag must result in no external write.
3. **Former-member deny rule:** Deactivated real accounts cannot be reactivated for extraction or testing.
4. **Expected-state check:** The integration must confirm the current remote state immediately before a write.
5. **Idempotency:** Every event and action receives a stable key; replaying it must not repeat the side effect.
6. **Notification classification:** Any action capable of sending email, SMS, push or in-app communication requires a documented test result and explicit rollout approval.
7. **Exception first:** Ambiguous identity, product, dates or ownership must stop automation and create a human task.
8. **No secret exposure:** Credentials and personal data must not appear in logs, source control or de-identified outputs.

## Immediate Blockers and Owners

| Blocker | Owner | Resolution |
|---|---|---|
| Dependency-check and relabel the confirmed `limited` Fit & Flexible branch | Integration build | Preserve the underlying live trigger until all dependencies are known; repair the missing Fit & Flexible opportunity stage |
| Authoritative sale-complete event | Confirmed | Signed agreement + successful upfront payment + recorded start date |
| Intended Trainerize invitation point | Confirmed | Initial Consultation purchase before the assessment; no second membership-sale invitation |
| Configure the existing-client membership transition | Integration build | Product Starts configured: 1-way Full Access, Evolved All Female Gym Owner and The Evolved Gym; Fit has no group/program; Strong/Fast use All Stars and mapped programs |
| Provide controlled test inboxes | Peter | Use addresses owned by The Evolved and clearly labelled as tests |
| Confirm immediate product start rule | Complete | Both synthetic Strong calendars showed the correct programming dates. All three products now use day of purchase / after current; future-dated memberships retain their recorded GHL start date |
| Confirm account-write endpoints | Integration build | Documentation review followed by allowlisted tests only |
| Confirm program/trainer/location mapping | Coaching + Admin | Trainer, location, group and add-on targets approved; inspect Bronze/Silver, trace class access and map credit-required appointment types |
| Preview-only sale-event validation | Complete | `scripts/preview_trainerize_membership.py` validates sale evidence and proposes an existing-client product transition without external writes |

## Change Control

Each phase requires a short go/no-go review. A successful technical request is not enough to enable a live workflow; notification behaviour, rollback limits, staff ownership and reconciliation must also pass.
