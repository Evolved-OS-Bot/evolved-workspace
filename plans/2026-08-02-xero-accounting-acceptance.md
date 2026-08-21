# Xero Accounting Acceptance and CEO Presentation

Status: complete and deployed in shadow; scheduled acceptance observation pending

## Purpose

Turn the connected read-only Xero feed into a useful CEO accounting view
without allowing bookkeeping timing to overwrite the governed cash-collected
metric or the rolling $1 million goal.

## Evidence already established

- Brown Casserly Pty Ltd is connected read-only.
- The Railway Xero job runs at 06:24 and 18:24 Brisbane time.
- The 06:24 refresh on 2 August 2026 completed and was accepted.
- The accepted snapshot contains complete Profit and Loss reports for the
  completed week, 28 days and 90 days.
- For 20–26 July, governed payment cash excluding GST was $9,802.37 while
  Xero accrual income was $2,120.55.
- Xero expenses for that week were $7,280.57, principally wages,
  superannuation, subcontractors and Stripe fees.

## Governing decision

1. Actual collected cash remains governed by accepted Stripe and PT Minder
   payment events.
2. Xero income is an accounting-close comparison, not a replacement cash
   figure.
3. Xero cost of sales plus operating expenses is the CEO expense measure.
4. Internal transfers, credit-card repayments and clearing movements remain
   excluded by using the Profit and Loss report.
5. A material cash-versus-Xero-income difference must be labelled as
   bookkeeping/timing review required, not as a business loss or system error.
6. Xero remains shadow until two scheduled cycles, category review and owner
   acceptance are complete.

## Implementation

1. Derive a compact expense breakdown from the accepted Profit and Loss
   account rows.
2. Show the largest expense categories on Reporting V2 so the total is
   explainable.
3. Replace accounting jargon with explicit labels:
   - Actual cash collected
   - Income currently recorded in Xero
   - Amount still requiring bookkeeping/timing reconciliation
4. Add an accounting-close status based on the size of the matched-period
   difference.
5. Preserve the primary cash cards and rolling goal without change.
6. Add tests for transfers being excluded, category totals, negative
   adjustments and material reconciliation warnings.
7. Deploy through Railway and verify all three period views.

## Build result

- Railway deployment: `b21e4725-fe99-47e0-b729-1500802d4ca5`
- Hub tests: 176 passed
- Read-only post-deployment Xero refresh: accepted
- Live week, 28-day and 90-day views: verified
- Publication state: shadow
- Remaining acceptance observation: the 18:24 scheduled Xero cycle on
  2 August 2026

## Acceptance gates

- Two consecutive scheduled Xero refreshes complete for the same period.
- Xero evidence is no older than 26 hours.
- Governed cash sources are fresh for the same period.
- Expense categories reconcile to the displayed expense total.
- Material cash-versus-income differences remain visible and cannot alter the
  cash goal.
- Peter explicitly approves promotion from shadow.
