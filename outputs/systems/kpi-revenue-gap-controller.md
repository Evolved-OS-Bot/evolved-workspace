# KPI Revenue Gap and Active Client Audit Controller

**Status:** Railway read-only shadow operation

**Canonical policy:** `reference/sops/active-client-payment-and-booking-reconciliation.md` version 1.12

**Operator worksheet:** `outputs/systems/pt-weekly-audit-run-sheet.md`

## Purpose

This controller turns the Active SGPT and Active PT audit into one repeatable process. It reads the current rosters, payment evidence, lifecycle evidence, PT booking evidence and KPI cash, then produces a client-by-client exception register and a cash bridge.

It does not charge a client, void an invoice, cancel a membership, delete an appointment, change Trainerize access, edit GHL or write to the workbook.

## What the System Produces

- A share-safe aggregate summary at `outputs/revenue-gap-control/latest-summary.md`.
- An identified client audit in the protected `data/private/revenue-gap-control/` area.
- An identified exception list with evidence checked, owner, next action and due date.
- A protected cash bridge for the selected service week.
- A durable SQLite audit history at `data/private/revenue-gap-control/revenue_gap.sqlite`.

The production service stores the equivalent protected evidence below `/data/revenue-gap-control/` on the existing Railway persistent volume.

## Evidence Hierarchy

1. Cleared bank cash, recorded in the relevant KPI cash cell, is the actual cash result.
2. Stripe successful receipts and invoices are the default proof of current collection.
3. PTMinder and EziDebit require approved evidence in the legacy-payment register.
4. Approved alternate-email links allow Stripe and legacy receipts to attach to the canonical GHL identity.
5. Owner-confirmed external-payment arrangements are time-bounded evidence and expire after 14 days without reconfirmation.
6. GHL holds, cancellation evidence and current-service markers establish lifecycle context.
7. Expanded PT calendars establish booking and delivery context.
8. Trainerize access is a supporting access signal, not proof of payment.

Identity is matched by exact normalised email first. Verified phone and approved durable legacy-email links are the only fallbacks; names alone are never used.

## Required Private Registers

Copy the controlled templates into the ignored private directory before use:

- `reference/templates/revenue-gap-legacy-payment-evidence.csv`
- `reference/templates/revenue-gap-timing-items.csv`
- the approved identity-link and account-classification registers in `data/private/integration-reporting/`

The live files should normally be:

- `data/private/revenue-gap-control/legacy-payment-evidence.csv`
- `data/private/revenue-gap-control/timing-items.csv`
- `/data/revenue-gap-control/identity-links.csv` in production
- `/data/revenue-gap-control/account-classifications.csv` in production

Each PTMinder or EziDebit row must be supported by an actual receipt check. Do not mark a member as collecting merely because an old account classification or active roster row exists.

A recurring legacy receipt expires as proof of current collection after 14 days. The next scheduled audit then returns the row to the payment-review queue until a newer completed receipt is loaded. PIF and paid-in-advance evidence use their separate entitlement controls.

Timing items are only for dated, evidenced differences between the receipt date and the service week. Every item needs an owner, next action and due date.

## Standard Run

From the workspace root, refresh all read-only evidence and run the control:

```bash
.venv/bin/python scripts/run_revenue_gap_control.py
```

The runner refreshes Stripe invoices, the membership snapshot and a local read-only PT booking snapshot. It forces booking shadow mode, disables booking email, disables KPI writes and disables all cross-system changes.

On Monday it audits the just-completed Monday-to-Sunday window. On other days it audits the current Monday-to-Sunday window.

Use `--window-start` and `--window-end` together to select a historical period. Use `--skip-source-refresh` only when the protected source snapshots have already been refreshed and checked.

When `--cleared-cash` is omitted from the underlying controller, it reads row 106 in the KPI column dated the following Monday. That value must already be the manually confirmed bank cash for the reporting week.

Use `--cleared-cash` only when the operator is intentionally supplying a separately confirmed bank figure. The cash label should state its source.

## Operating Cadence

- Within one business day: review starts, failed payments, refunds, holds, returns, cancellations, downgrades, price changes and payment-rail changes.
- Monday at 6:30 am Brisbane: Railway runs the full Active PT audit and SGPT exception review.
- Friday at 4:30 pm Brisbane: Railway closes the bridge after bank cash is confirmed and emails Peter.
- First Monday monthly: complete the full SGPT, PT pack and identity deep check.
- Quarterly: validate identity, lifecycle, current tier and KPI formulas.
- Extra full audit: trigger when the unexplained residual remains above $99 for SGPT or $120 for PT after timing items, or when lifecycle evidence is missing.

## Close Rules

The report is not closed merely because its arithmetic balances. Close only when:

- source snapshots are complete and fresh;
- every current payment rail has receipt evidence;
- Fast Track has a $99 SGPT component plus PT calculated from the approved weekly session count and session rate, while the combined receipt is counted once;
- PIA, arrears, pauses, future starts and PIF packs are separated correctly;
- every remaining mismatch has evidence, an owner, a next action and a due date; and
- the unexplained residual is zero, or an expressly approved immaterial amount.

An unresolved payment classification means evidence is missing. It does not mean the member has failed to pay.

## Safety and Promotion

The controller remains read-only for at least three complete weekly cycles. Admin compares every recommendation with the final verified decision.

No write-back is enabled until those cycles produce zero unsafe cancellation, billing, refund or appointment-removal recommendations. Any later sheet-write feature must be bounded, explicitly approved, re-read after the change and followed by an exact-email duplicate search.

## Current Implementation Boundary

Stripe, GHL, Trainerize, Active SGPT, Active PT and KPI inputs are available through the existing reconciliation sources. A current PT booking snapshot must also be supplied.

The protected PTMinder/EziDebit register was populated on 25 July 2026 with 24 identity-verified rows. The 27 July hub reconciliation refreshed five stale date-only rows, verified Belinda Peters as collecting from a later successful receipt and applied Jillian Breen's approved identity link.

Peter then confirmed that Rabail Aisha returned to active service. Her live PT Minder payment schedule is an active $99 weekly Bronze recurring payment, with a $99 debit dated 24 July pending for the 24–30 July service week.

Treat her as active from 24 July and include $99 in scheduled run-rate. Do not count the pending debit as cleared cash, and do not classify her as `Active - ARREARS` or create a retry action unless the debit changes to failed. Once the debit succeeds, it becomes current completed payment evidence.

Peter confirmed Bronte Holt's current membership as $69 per week for two SGPT sessions per week. She submitted 30 days' downgrade notice on 8 June 2026; the $149 arrangement ended on 7 July and the $69 arrangement took effect on 8 July.

Peter confirmed that Bronte is fully up to date and the temporary adjustment is complete. Her controller state is therefore current, not `review_required`; the $47 pending item and PT Minder's displayed $590 balance are not exceptions.

PT Minder is payment-event evidence, not an accounts-receivable ledger. The controller must ignore PT Minder's displayed balance, amount due and internal Charge function for debt, revenue-gap, collection and lifecycle decisions. Use actual debit and payment events only. A specific failed scheduled payment outside an approved hold may create a recovery item, whose action is to retry that payment; a successful retry closes the item.

Anne Leditschke's transaction-classification exception was resolved on 27 July. Her commercial arrangement is a recurring $69 weekly Evolved Anywhere membership plus optional one-on-one PT sessions purchased as she goes. The protected evidence had incorrectly used a $120 ad-hoc PT purchase as recurring run-rate; it now uses the $69 Evolved Anywhere fee.

Revenue Audit must count the $69 as recurring run-rate and treat the one-on-one PT payments as variable cash. PT Booking Continuity must convert only each completed ad-hoc PT purchase into the corresponding session entitlement, then reconcile that entitlement against bookings and delivery. It must not infer a recurring PT commitment.

The first production run after loading the register read 143 roster rows and reproduced the $12,735 workbook allocation and $10,927.24 KPI cash. Confirmed current income increased from $7,317 to $9,380, unresolved exceptions fell from 56 to 33 and the unexplained variance reduced from $3,610.24 to $1,547.24. Cash is above confirmed current income, so the remaining variance is incomplete or differently timed evidence rather than proof of a cash shortfall.

## Railway Deployment

The controller is deployed inside the existing `PT Booking Shadow` Railway service at `https://pt-booking-shadow-production.up.railway.app`.

On 27 July 2026 deployment `e49406e8-45f2-437b-91e5-5eb2537f0adb` added the authenticated Railway hub PT Minder reader in shadow mode. The first comparison used accepted snapshot `20260727T025751Z-9d3da706`: 14 of 24 projected payment rows matched the protected legacy register exactly, nine had field differences, one was hub-only and one was legacy-only.

Deployments `f6049316-cdd9-4e77-8bfa-2c2cdee5b3de` and `b9d8bc0` added the production parity consumer and canonical identity-link handling. Hub commit `a844568` and PT Booking commit `8d70454` then added purpose-aware transaction classification; PT deployment `f67ead1b-6aaf-4094-b274-95dbc9d0fe42` completed successfully.

After correcting Anne's protected recurring evidence, the live health contract reports 22 exact matches, two mismatched rows, zero hub-only rows and zero legacy-only rows. It also reports `source_contract_incomplete` and `transactionDetailComplete=false`, so the existing V1 snapshot cannot qualify for cutover. The protected pre-reconciliation register is recoverable at `/data/revenue-gap-control/legacy-payment-evidence.pre-hub-reconcile-20260727.csv`; the pre-purpose-classification copy is `/data/revenue-gap-control/legacy-payment-evidence.pre-purpose-classification-20260727.csv`. Existing PT, revenue and cash-flow calculations continue to use the protected register until a complete purpose-aware capture and two parity cycles pass.

The complete V2 capture was accepted later on 27 July as `20260727T082105Z-5a9058f4`: 27 active accounts and 540 actual Ezidebit payment events, with PT Minder Charge entries and displayed balances excluded. An explicit normalized weekly-rate field protects fortnightly schedules and resumed pending debits from cadence distortion.

Deployments `558a2f5b-35e8-4119-b361-fca6935e9a38` for the hub and `1b6214c9-fb5b-40f5-b5e0-efcc3067bb54` for PT Booking are healthy. The first finalized V2 comparison had zero ambiguous recurring accounts, 15 exact rows, nine mismatched rows, one hub-only row and zero legacy-only rows.

The protected review identified two projection defects rather than forcing the register to match them. Historical retry dates no longer override a later successful or pending current schedule, and an explicitly paused product is excluded even when the client-level state remains collecting. PT Booking deployment `fee1b5ad-0235-4fdf-9fc4-dc523014cee1` is healthy and all 146 affected tests pass.

Seven evidence-backed rows were refreshed. The resulting live comparison is 24 of 24 exact, with zero field differences, zero hub-only or legacy-only rows and zero ambiguous recurring accounts. The protected register fingerprint is `e57ecf346f50660c96ee520ad3e6fafaa4c951fdf159f121f1d7644d60e2f549`, and its pre-change backup is `/data/revenue-gap-control/legacy-payment-evidence.pre-v2-final-reconcile-20260727.csv`.

This is clean parity cycle one. Existing PT, revenue and cash-flow calculations continue to use the protected register until a second independent V2 capture also passes; rerunning the same snapshot does not satisfy that confirmation gate.

- Deployment `18d9266d-3dda-4a72-8235-e16dc7c73441` includes the protected register, due-date controls and 14-day recurring-receipt expiry.
- The service uses one worker, Brisbane scheduling and the existing `/data` persistent volume.
- `POST /revenue/run` starts an authenticated Monday or Friday audit.
- `GET /revenue/runs/latest` returns the authenticated aggregate run state.
- `POST /revenue/evidence/legacy` atomically replaces the authenticated legacy register after strict validation.
- `GET /revenue/evidence/legacy/status` returns only the row count, update time and SHA-256 fingerprint.
- `POST /revenue/evidence/identity-links` atomically replaces the approved Stripe and legacy-email aliases.
- `POST /revenue/evidence/account-classifications` atomically replaces approved account-level exceptions such as external Stripe arrangements.
- `GET /revenue/evidence/shared/status` returns only counts and fingerprints for all three shared registers.
- The public health route exposes only run status, type and completion time.
- GitHub auto-deploy is disabled because the connected workspace repository is public. Future production releases must use a reviewed, code-only direct Railway package.
- The duplicate local Codex Monday and Friday automations are paused.

Use `scripts/upload_legacy_payment_evidence.py` through `railway run` to refresh the protected register. The command obtains the existing Railway secret without printing it, sends the register over HTTPS and receives only a count and fingerprint.

The 27 July shared-evidence deployment stores 24 legacy-payment records, 14 approved identity links and 18 account classifications on the protected production volume. PT Booking Shadow run `70d174cc-c526-4601-8acb-f4833600a001` consumed the same evidence, completed without a source error and reduced both generic commercial-evidence and unverified prepaid-payment findings to zero.

Production run `e722b7c5-81ba-4285-b09b-5a3ed8564ec4` completed with fresh membership run `20260725T073227Z` and booking run `904fb075-7f99-4da7-80f3-090c36926a25`. It read 143 roster rows, reported $9,380 confirmed current income, $9,928 scheduled run-rate, $10,927.24 cash and 33 owned exceptions. The final control assigns every residual exception a next-business-day due date.
