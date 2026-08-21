# Trainerize Product Automation Audit

**Status:** Live configuration updated; controlled start-date test passed and all three membership products now default to day of purchase / after current
**Audited:** 2026-07-22 to 2026-07-23
**Changes made in Trainerize:** Membership Product Starts configured; Fit removed from All Stars; Initial Consultation changed by owner to 1-way with empty Product Ends actions

## Why This Matters

Trainerize access is created before the Strength Assessment, not after the membership sale. The trainer purchases the Initial Consultation product for the prospect, who receives app access and completes the assessment inside the same account.

The correct post-sale design is therefore an account conversion and fulfilment process. It must reuse the assessment-created Trainerize user rather than create or invite another client.

## Operational Browser Access

For Evolved Trainerize build work, enter through the Evolve Gym Trainerize login, which opens the business account directly. Do not use the Trainerize representative portal for this workflow.

## Women's Full Evolved Standards Assessment build

**Build record date:** 2026-08-03  
**Canonical authority:** `reference/evolved-manual/03b-standards-framework.md`  
**Canonical inventory:** 20 standards across 6 1RM strength rows, 7 functional-strength rows and 7 functional-fitness rows

| Asset | ID | Verified state |
|---|---:|---|
| `Women's Full Evolved Standards Assessment` | `226418512` | Shared Master Library workout; 20 canonical standards plus the canonical Performance Warm-Up represented by 23 saved exercise entries; unassigned |
| `Women's Standard Strength Assessment` | `189915686` | Acquisition workout retained unchanged; created and last updated 26 July 2025 |

The current-member workout remains in the shared Master Library. No assignment or enrolment action was taken, and no client, membership, payment, booking, product, workflow or other live asset was changed.

The completed workout contains all 20 canonical standards from Manual Section 03b. Core uses three exercise entries, High Plank, Side Plank and Strict Toes to Bar, and the separate Performance Warm-Up entry brings the saved Trainerize inventory to 23 exercise entries.

Ten selected loaded strength options use two 1–3RM attempts: attempt 1 at the Trainerize-estimated 1RM and attempt 2 adjusted up or down from the result. The other standard-specific tests retain one set; Performance Warm-Up uses three sets for 20% × 12, 60% × 6 and 100% × 1 acclimation.

Every standard entry retains its trainer-facing canonical Live, Long and Perform threshold plus the required raw evidence fields. High Plank, Side Plank, Running and Rowing use Trainerize's text target format so no misleading default 30-second target appears.

The workout instructions state that trainers choose the appropriate test for each movement pattern or modality, leave an inapplicable test blank, and record the specific skip reason in workout or session notes. Blank is explicitly not a failed result or incomplete assessment.

Track selection is recorded separately from omitted tests. The coach selects Live, Long or Perform from member goals, readiness, safety and captured evidence, with no universal composite score or fixed selection rule, then records the selected standard, 8 to 12-week focus and 6 to 12-month direction.

The corrected live library audit found safe existing options or functional equivalents for 19 canonical standards. `Dumbbell Incline Bench Row` is the video-backed equivalent for Chest Supported Row, and `Chin Up` is the supinated-grip equivalent for Reverse Grip Pull Up.

`Single Arm DB Reverse Lunge` and `Performance Warm-Up` are the two active custom exercises and were read back with complete PRIME instructions. Their two outstanding recording briefs and filenames are maintained in `outputs/fast-track-20/full-standards-custom-exercise-video-briefs.md`.

The legacy library exercise `Acclimation Set` remains unchanged and was not added. Its 60% × 6 between-exercise instruction conflicts with Manual Section 04, which requires the Performance Warm-Up once for the selected main lift.

The initially created `Chest Supported Row` and `Reverse Grip Pull Up` custom exercises were removed from the assessment after the existing equivalents were verified. They were not deleted from the exercise library.

Final live read-back confirmed the exact workout title, complete current-member instructions, 23 saved exercise entries, all 20 canonical standards, ten two-attempt loaded tests, one three-set Performance Warm-Up and every canonical threshold and recording prompt without mismatch. It also confirmed that `Dumbbell Incline Bench Row` and `Chin Up` replace the two custom duplicates.

Trainerize saved the new Performance Warm-Up as the final row because its browser editor did not permit reliable row reordering through the available controls. The workout instructions explicitly direct the trainer to complete it before the selected main loaded test, but this row-position limitation remains visible and the asset should not be described as visually final until a trainer or supported authoring route moves it to the first row.

The acquisition workout `189915686` was separately opened read-only and still reports its unchanged 26 July 2025 creation and update date.

### Standards cascade control

The governed register is `outputs/systems/evolved-standards-cascade-register.json`. The local validation is:

```bash
python3 scripts/check_evolved_standards_cascade.py
```

Any canonical standard added, renamed, removed or threshold-changed must cascade to the worksheet, coach guide, Fast Track Upgrade System, assessment-release design, trainer-course Markdown, trainer-course HTML, affected quizzes, live Trainerize assessment, roadmap and this build record. A canonical table fingerprint change makes the validation fail until the registered surfaces are reviewed.

The 2026-08-03 local run passed 20 canonical rows across eight registered local surfaces with fingerprint `fae55e3aeaffd8546e968c06a38e46b3050a61fe0798ca76b489686e320802c1`. The trainer-portal audit also passed all 13 numbered course files plus Practical Sign-Off.

Courses 6 and 11 already represented all 20 exercise rows and numerical thresholds. Their Markdown and HTML were tightened to the canonical phrasing for Push Ups, Core, Running, Rowing, Pistol Squat and ATG Split Squat; the affected quiz answers remained accurate and required no question change.

No live GHL course mutation was made in this run because no numerical threshold, exercise inventory or quiz answer changed. Live GHL was not separately opened for a fresh visual read-back, so the local source/HTML/quiz parity is verified but live publication parity remains a manual verification item before the overall assessment workstream can be closed.

## Initial Consultation Product

| Setting | Live value |
|---|---|
| Type | Main Product |
| Price | Free |
| Duration | 1 day |
| Start | Day of purchase / after current Main Product |
| Self-purchase listing | Off on Trainerize.me |
| First purchase access | Full Access / 1-way messaging |
| First purchase trainer | Megan Brown |
| First purchase location | No location visibly selected in the automation |
| First purchase main program | Strength Assessment |
| First purchase tag | Configured lead tag, displayed in the UI as `High Val...` |
| Product-end access | No action |
| Product-end program action | No action |

The Main Product still lasts one day, but its Product Ends automation is now empty. This removes the former 24-hour move to Offline and Strength Assessment program removal.

Keep Full Access / 1-way. Basic cannot receive training programs or track workouts and results, so it would break the Strength Assessment workflow.

## Current Membership Fulfilment Products

All three membership products are free Trainerize Main Products lasting 52 weeks and are configured to start on `Day of purchase / After current` for self-purchases. Their role is fulfilment and app configuration, not collection of the actual membership payment. On 22 July 2026 they were renamed and given explicit provisioning descriptions. Staff must still use an explicitly agreed future membership start date when assigning a future-dated product manually.

| Product | First-purchase add-on | First-purchase group | Product Starts automation | Product Ends automation |
|---|---|---|---|---|
| `Membership: Fit & Flexible` | `Membership: Strong, Fit & Flexible` in legacy first-purchase automation; Product Starts correctly applies none | Legacy first-purchase value only | Full Access / 1-way messaging; Evolved All Female Gym; The Evolved Gym; no All Stars group; no program | Empty |
| `Membership: Strong, Fit & Flexible` | `Membership: Strong, Fit & Flexible` | The Evolved All Stars | Full Access / 1-way messaging; Evolved All Female Gym; The Evolved Gym; The Evolved All Stars; `Membership: Strong, Fit & Flexible` program | Empty |
| `Membership: Fast Track` | `Membership: Fast Track` | The Evolved All Stars | Full Access / 1-way messaging; Evolved All Female Gym; The Evolved Gym; The Evolved All Stars; `Membership: Fast Track` program | Empty |

Each first-purchase automation also sets Full Access / 2-way messaging, assigns Megan Brown and selects The Evolved Gym location.

Fast Track's product description promises one weekly 30-minute PT session, but the product contains no sessions. This confirms that session entitlement is administered elsewhere or manually.

The product list currently reports zero current clients on Fit & Flexible and Fast Track and only three on Strong, Fit & Flexible. These products are therefore not an authoritative current-member roster.

## Fulfilment Mapping Register

The following mapping separates verified live settings from the recommended post-sale target. It does not authorise a live change.

| Field | Fit & Flexible | Strong, Fit & Flexible | Fast Track | Mapping status |
|---|---|---|---|---|
| GHL agreement value | Fit & Flexible | Strong, Fit & Flexible | Fast Track Package | Confirmed |
| Legacy GHL tag | `limited` | `bronze` | `silver` | Confirmed; dependency-check before renaming |
| Trainerize Main Product | `Membership: Fit & Flexible` | `Membership: Strong, Fit & Flexible` | `Membership: Fast Track` | Renamed live 22 July 2026 |
| Product duration | 52 weeks | 52 weeks | 52 weeks | Confirmed live setting |
| Product start | Day of purchase / after current, unless explicitly future-dated | Day of purchase / after current, unless explicitly future-dated | Day of purchase / after current, unless explicitly future-dated | Verified live 23 July 2026 |
| Identity | Reuse assessment-created client | Reuse assessment-created client | Reuse assessment-created client | Confirmed |
| Client type at start | Full Access / 1-way messaging | Full Access / 1-way messaging | Full Access / 1-way messaging | Product Starts configured and verified live 22 July 2026; first-purchase templates remain legacy 2-way messaging |
| Location | The Evolved Gym | The Evolved Gym | The Evolved Gym | Product Starts configured and verified live 22 July 2026 |
| Main program | None | None | None | Confirmed current template |
| Add-on program | None | `Membership: Strong, Fit & Flexible` | `Membership: Fast Track` | Product Starts configured and verified live 22 July 2026; programs renamed live on 22 July, and Fit's legacy first-purchase rule still incorrectly selects the Strong program |
| Community group | None | The Evolved All Stars | The Evolved All Stars | Fit removed from Product Starts on 23 July; Strong/Fast unchanged |
| Trainer | Evolved All Female Gym | Evolved All Female Gym | Evolved All Female Gym | Product Starts configured and verified live 22 July 2026; this is the exact Owner-account label, without `The` |
| Smart Meal Plan | Not included | Manual setup required | Manual setup required | Added to GHL consultant and Admin QA tasks on 23 July; Product Starts has no Smart Meal Plan action |
| Class-booking entitlement | Cardio + Pilates | Cardio + Pilates + Strength | Cardio + Pilates + Strength | Approved 999-credit model; staff apply the matching Class Access add-ons and cancellation deactivates the client |
| PT/onboarding credits | None | None | None | Do not model these in Trainerize; The Evolved does not use Trainerize's PT credit function |
| Product-end actions | None | None | None | Confirmed; cancellation must be driven by the verified final service date, not 52-week expiry |

### Service-Scope Reconciliation

The current coaching manual remains the service source of truth:

- Fit & Flexible: Pilates, HIIT Cardio and Hybrid App access; no Sculpt & Strength and no onboarding session.
- Strong, Fit & Flexible: the Fit inclusion set plus Sculpt & Strength, one KickStart onboarding session, meal plan and grocery list.
- Fast Track: the Strong inclusion set plus the four-session onboarding pathway and a weekly 30-minute PT session.

The Trainerize product descriptions use a slightly different and potentially older vocabulary. Fit lists Power Moves, Evolved Pilates and Hybrid Fitness; Strong and Fast list those classes plus Strength & Sculpt. The membership Main Products currently contain no sessions.

### Service-change targets approved 2 August 2026

Peter approved two continuing-service definitions:

| Product | Program | Access | Groups/classes | Coaching |
|---|---|---|---|---|
| Evolved Anywhere | Retain personalised programming | Full Access / one-way messaging | None | Normal personalised-program support only |
| Online Only | Distinct standard program | Full Access / one-way messaging | None | None |

The correct business URL is `https://theevolvedgym.trainerize.com`. The saved Evolved business session was authenticated on 2 August 2026 and the following live configuration was created and read back:

| Main Product | Product controls | Saved Product Starts automation |
|---|---|---|
| `Membership: Evolved Anywhere` | Free; 52 weeks; `Day of purchase / After current`; no sessions; not sold on Trainerize.me; existing clients allowed | Set Full Access / one-way messaging. No program, trainer, group, class, tag or meal-plan action, preserving the member's existing personalised program and trainer relationship. |
| `Membership: Online Only` | Free; 52 weeks; `Day of purchase / After current`; no sessions; not sold on Trainerize.me; existing clients allowed | Set Full Access / one-way messaging and subscribe `At Home: Bodyweight/No Equipment Program`. No trainer, group, class, tag, meal-plan or coaching action. |

Two Evolved-owned synthetic profiles were created: `MSC EA Acceptance Test` and `MSC Online Acceptance Test`, using dated `fisiquehfp` plus-addresses. Online Only passed after confirmation: its sale and Main Product are Active through 1 August 2027, access is Full Access / one-way messaging, its main program is `At Home: Bodyweight/No Equipment Program`, and the profile has no Add-ons or Session Credits.

The original Evolved Anywhere sale remained `Pending` after Peter's first confirmation. Its profile stayed Full Access / two-way messaging with `MSC EA's program`, no current training plan and no executed Product Starts state. The pending purchase was removed through Trainerize's supported control and now reads `Expired`; the same product was re-sold to the same profile without creating a duplicate product or profile.

After Peter confirmed the replacement purchase, the new Evolved Anywhere sale and Main Product read Active through 1 August 2027. The profile read Full Access / one-way messaging, retained `MSC EA's program`, and had no Add-ons or Session Credits. Both synthetic profiles were then moved to Deactivated and found exactly once in Trainerize's Deactivated view.

The 5 August live Tania remediation used the supported program unsubscribe control to remove `2026 SGPT Program`. The full `The Evolved All Stars` member list was loaded and Tania was absent, proving the group membership was removed without deactivating her. The final client read-back preserves Full Access / one-way messaging and the `Tania's program` container. It also shows `Main program expired`, `No current training plan` and six manually added non-expiring Groups / Classes balances: 973 Sculpt & Strength, 999 Build & Balance, 995 Metabolic Burn, 995 Pilates, 999 HybridFit and a second 999 Sculpt & Strength balance. Those credits still permit app self-booking. The client UI exposes add-only gifted-credit controls and states that gifted credits cannot be edited or undone; disabling shared event types or deactivating Tania would breach scope. Current personalised programming and safe client-scoped credit revocation therefore remain exception work.

No workflow may infer success from Stripe or GHL alone. Trainerize configuration, execution and synthetic cleanup now pass, but both GHL service-change workflows must remain Draft until one clean post-boundary accepted event reconciles GHL, billing, Trainerize, appointments, workbooks and reporting.

The live class-access products resolve the current timetable terminology. `Class Access: Cardio` grants 999 non-expiring credits for HybridFit and Metabolic Burn, `Class Access: Pilates` grants 999 non-expiring Pilates credits, and `Class Access: Strength` grants 999 non-expiring credits for Build & Balance and Sculpt & Strength. Each is a free 52-week Add-on Product, but each currently shows only one client, so these products are not yet the standard membership-delivery mechanism.

The renamed `Membership: Strong, Fit & Flexible` program is not proof that Fit members receive strength access. Fit's legacy first-purchase rule still selects it even though Fit and Strong have different contractual inclusions. The integration must not use the add-on program alone to authorise class access.

### Live Product Starts Template

On 22 and 23 July 2026, the Product Starts automations were configured as follows:

1. Set Full Access / 1-way messaging.
2. Assign The Evolved Gym location.
3. Add The Evolved All Stars group for Strong and Fast Track only. Fit receives no group.
4. Assign the `Evolved All Female Gym` Owner account as the default trainer.
5. Subscribe no program for Fit, `Membership: Strong, Fit & Flexible` for Strong, and `Membership: Fast Track` for Fast Track.
6. Do not create a second client or send a second invitation.
7. Class-access products remain outside Product Starts and are applied through the branch-specific GHL consultant task.

The Evolved All Stars group already has an attached main program. Fit & Flexible is deliberately excluded and has no Trainerize workout tracking; it uses only Cardio and Pilates timetable access.

The one-day Initial Consultation product now also uses Full Access / 1-way messaging. Basic was rejected because it cannot deliver the Strength Assessment program or record workout results.

### Controlled Start-Date Test: Passed, 23 July 2026

Two Evolved-owned synthetic Full Access / 1-way clients were created using plus-address aliases of `fisiquehfp@gmail.com`: `TZ Purchase Test` and `TZ Monday Test`. The live `Membership: Strong, Fit & Flexible` product was sold manually to the first client starting on 23 July 2026 and to the second starting on Monday 27 July 2026.

Both subscription confirmations were accepted and independently verified in Trainerize on 23 July. Both clients now appear as active Full Access / 1-way accounts owned by `Evolved All Female Gym` at `The Evolved Gym`.

The initial list-level summary was misleading because it showed no current plan before the client calendars were inspected. Peter then opened both client calendars and confirmed that each account contained the correct All Stars programming on the correct calendar days. The master-program dates remain aligned rather than shifting a Monday workout onto the product purchase day.

The start rule is therefore approved: normal same-day memberships start on the day of purchase, while an explicitly future-dated membership uses its agreed GHL membership start date. On 23 July, all three membership products were changed and live-verified as `Day of purchase / After current`. Both synthetic clients were then deactivated, permanently deleted and verified absent from the Coaching and Deactivated lists.

The 52-week product expiry must not deactivate a paying member. Nightly reconciliation should flag active GHL/Stripe members whose Trainerize Main Product is approaching expiry, while cancellation separately removes access on the verified final service date.

## Class Session Credit Decision

In this account, Trainerize session credits govern timetable bookings. The Evolved does not use Trainerize's personal-training credit function, so KickStart, onboarding and Fast Track PT delivery must not be converted into Trainerize credits.

The approved service-to-class mapping is:

| Membership | Class access | Live event types represented |
|---|---|---|
| Fit & Flexible | Cardio + Pilates | HybridFit, Metabolic Burn and Pilates |
| Strong, Fit & Flexible | Cardio + Pilates + Strength | Fit events plus Build & Balance and Sculpt & Strength |
| Fast Track | Cardio + Pilates + Strength | Same class access as Strong; weekly PT remains outside Trainerize credits |

The live Class Access add-ons use 999 credits per included event type with `Do not Expire`. That is the account's proxy for unlimited timetable access.

### Cancellation Safety Gate and Approved Operating Decision: 22 July 2026

A controlled test used a synthetic Full Access / 1-way client and the live `Class Access: Cardio` Add-on Product. After email confirmation, Trainerize activated the product and issued 999 paid, non-expiring HybridFit credits plus 999 paid, non-expiring Metabolic Burn credits.

Cancelling the active Add-on Product removed the product from the client but did **not** revoke either credit balance. The client immediately showed `No Add-ons` while still showing both 999-credit paid balances.

The separate deactivation test confirmed that a deactivated client cannot access the app or book sessions. Peter therefore approved retaining the existing 999 non-expiring credit model because it avoids the greater operational risk of a bulk expiry or missed replenishment stopping active members from booking. Cancellation deactivation is the hard access stop; removing an Add-on alone is not a cancellation control. The synthetic client was deactivated and permanently deleted after testing.

For the current manual phase, a GHL task tells the assigned staff member which Main Product and Class Access add-ons to apply. Downgrades, upgrades and moves to PT-only must create a separate staff task to reconcile the Main Product and Class Access add-ons; a client leaving all class access must be deactivated when her service ends.

## 52-Week Expiry Decision

The live account has Automatic Membership Control set to **Off: manage client status and app access manually**. Therefore, expiry does not currently auto-deactivate the client. It does, however, leave the member with an expired product and makes the product unreliable as the long-term membership ledger.

Recommended treatment for the first 90-day sprint:

1. Keep Automatic Membership Control off.
2. Keep Product Ends empty; cancellation remains driven by GHL's verified final service date.
3. Treat the Trainerize Main Product as the initial fulfilment trigger, not the billing source of truth.
4. Add reconciliation alerts before day 330 and day 350 for members whose GHL/Stripe membership is still active.
5. Queue another 52-week Main Product only after testing that renewal does not send an invitation, duplicate group/program setup or disrupt access.

Do not simply extend the product to an arbitrary multi-year duration. That would reduce administration but allow stale access to survive much longer when a cancellation workflow fails.

## Root Cause of the Manual Handoff

Trainerize explicitly states that the **First purchase** automation does not run when an existing client buys a product. Every normal membership buyer is already an existing Trainerize client because she bought Initial Consultation first.

Before 22 July 2026, Fit & Flexible, Strong, Fit & Flexible and Fast Track all had empty **Product Starts** automations. Their first-purchase access, trainer, program and group actions therefore did not handle the normal assessment-to-member path. This gap is now closed for access, Owner, location, group and Bronze/Silver program assignment; Class Access products and the Main Product assignment remain controlled staff tasks.

This is the central post-sale fulfilment gap:

```text
Initial Consultation bought
  -> existing Trainerize client created
  -> assessment access and program applied
  -> membership sold
  -> membership product assigned or queued
  -> First purchase automation skipped because client already exists
  -> Product Starts applies the package-specific membership configuration
  -> consultant applies the package-specific Class Access products
  -> consultant sets up Smart Meal Plan for Strong or Fast Track
  -> Admin Eve verifies the complete setup on day two
```

Peter confirmed on 22 July 2026 that staff currently assign the post-sale Trainerize membership product entirely manually. The historical Drive document [ONBOARDING - BACK END PROCESS - Evolved](https://docs.google.com/document/d/1DwJ9GLa5f8po3tVW37igHQLT-npSn4furDAgYqFM5PU) supports that finding: it includes Trainerize setup as a manual signing/onboarding checklist item. It is not a safe current specification because it still references ACR and PTMinder and does not identify the current membership products, mappings or start-date rule.

The current staff procedure is now defined in `reference/sops/post-sale-member-onboarding.md`. It supersedes the historical Drive checklist and combines the sale gate, account reuse, package fulfilment, first-session booking, consultant completion and Admin Eve day-two quality control.

## Recommended Design

Use the Trainerize membership Main Product as the fulfilment object, while GHL and Stripe prove the sale.

1. GHL confirms signed agreement, successful upfront payment and start date.
2. The integration matches the existing Trainerize assessment client by stored user ID or one exact email match.
3. The correct free Trainerize membership product is assigned once. Normal memberships start on the day of purchase; explicit future starts use the recorded GHL membership start date.
4. Product Starts performs the approved member configuration for existing clients.
5. The integration verifies the resulting client type, location, program/group access and product dates.
6. Any mismatch becomes an Admin task.

The GHL sale mapping is confirmed: Fit & Flexible adds `limited`, Strong, Fit & Flexible adds `bronze`, and Fast Track adds `silver`. Product Starts now uses the approved package mapping rather than copying the legacy first-purchase rules. The First purchase settings remain unchanged and should be normalised separately only after confirming the effect on genuinely new direct purchasers.

## Immediate Follow-Ups

1. Inspect the contents and operational purpose of the renamed `Membership: Strong, Fit & Flexible` and `Membership: Fast Track` programs; do not infer class access from their names.
2. Ask Trainerize API Support for a supported way to revoke product-issued class credits, or confirm that none exists; the live cancellation test retained all 999-credit balances.
3. Monitor for any unexpected member-start or calendar-alignment exception during the first 20 live handoffs.
4. Monitor staff use of the new canonical Post-Sale Member Onboarding SOP and retire the outdated Drive checklist from operational use.
5. Use `scripts/preview_trainerize_membership.py` to validate synthetic sale events before any write-capability test.
6. Monitor the first 20 GHL consultant and Admin QA handoffs using the confirmed purchase-day / recorded-future-date start rule.
