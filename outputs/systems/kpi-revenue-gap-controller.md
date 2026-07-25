# KPI Revenue Gap and Active Client Audit Controller

**Status:** Read-only shadow operation

**Canonical policy:** `reference/sops/active-client-payment-and-booking-reconciliation.md` version 1.8

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

## Evidence Hierarchy

1. Cleared bank cash, recorded in the relevant KPI cash cell, is the actual cash result.
2. Stripe successful receipts and invoices are the default proof of current collection.
3. PTMinder and EziDebit require approved evidence in the legacy-payment register.
4. GHL holds, cancellation evidence and current-service markers establish lifecycle context.
5. Expanded PT calendars establish booking and delivery context.
6. Trainerize access is a supporting access signal, not proof of payment.

Identity is matched by exact normalised email first. Verified phone and approved durable legacy-email links are the only fallbacks; names alone are never used.

## Required Private Registers

Copy the controlled templates into the ignored private directory before use:

- `reference/templates/revenue-gap-legacy-payment-evidence.csv`
- `reference/templates/revenue-gap-timing-items.csv`

The live files should normally be:

- `data/private/revenue-gap-control/legacy-payment-evidence.csv`
- `data/private/revenue-gap-control/timing-items.csv`

Each PTMinder or EziDebit row must be supported by an actual receipt check. Do not mark a member as collecting merely because an old account classification or active roster row exists.

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
- Monday at 6:30 am Brisbane: the active `Monday active-client revenue audit` automation runs the full Active PT audit and SGPT exception review.
- Friday at 4:30 pm Brisbane: the active `Friday KPI cash close` automation closes the bridge after bank cash is confirmed.
- First Monday monthly: complete the full SGPT, PT pack and identity deep check.
- Quarterly: validate identity, lifecycle, current tier and KPI formulas.
- Extra full audit: trigger when the unexplained residual remains above $99 for SGPT or $120 for PT after timing items, or when lifecycle evidence is missing.

## Close Rules

The report is not closed merely because its arithmetic balances. Close only when:

- source snapshots are complete and fresh;
- every current payment rail has receipt evidence;
- Fast Track has $99 SGPT plus $50 PT while its $149 receipt is counted once;
- PIA, arrears, pauses, future starts and PIF packs are separated correctly;
- every remaining mismatch has evidence, an owner, a next action and a due date; and
- the unexplained residual is zero, or an expressly approved immaterial amount.

An unresolved payment classification means evidence is missing. It does not mean the member has failed to pay.

## Safety and Promotion

The controller remains read-only for at least three complete weekly cycles. Admin compares every recommendation with the final verified decision.

No write-back is enabled until those cycles produce zero unsafe cancellation, billing, refund or appointment-removal recommendations. Any later sheet-write feature must be bounded, explicitly approved, re-read after the change and followed by an exact-email duplicate search.

## Current Implementation Boundary

Stripe, GHL, Trainerize, Active SGPT, Active PT and KPI inputs are available through the existing reconciliation sources. A current PT booking snapshot must also be supplied.

The remaining operational dependency is a complete approved PTMinder and EziDebit receipt register. Until it is populated, the controller will deliberately leave those members unresolved and the cash bridge will remain open.

The first protected July shadow run reproduced the $12,735 workbook allocation and $10,927.24 KPI cash. It did not close the bridge because legacy-rail receipts were incomplete. Two later live validation retries failed closed on Google Sheet read timeouts, without changing any source or overwriting the completed evidence.
