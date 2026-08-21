# Trainerize Reporting and Reconciliation

**Run:** 20260802T234314Z  
**Generated:** 2026-08-02T23:44:06+00:00  
**Mode:** Read-only

## Source Coverage

| Source | Records |
|---|---:|
| Ghl Contacts | 2,802 |
| Ghl Opportunities | 2,148 |
| Stripe Customers | 287 |
| Stripe Subscriptions | 308 |
| Stripe Invoices | 0 |
| Trainerize Active | 153 |
| Trainerize Deactivated | 426 |

## Exceptions

Total exception rows: **573**

| Severity | Count |
|---|---:|
| Critical | 1 |
| Medium | 5 |
| Low | 567 |

## Exception Types

| Severity | Type | Count |
|---|---|---:|
| Critical | Trainerize Active After Final Access | 1 |
| Medium | Ghl Member Without Stripe Entitlement | 2 |
| Medium | Trainerize Active Without Current Entitlement Signal | 2 |
| Medium | Stripe Entitled Without Ghl Member Signal | 1 |
| Low | Missing Email | 499 |
| Low | Ghl Member Without Stripe Entitlement | 45 |
| Low | Duplicate Ghl Email | 12 |
| Low | Duplicate Stripe Email | 11 |

## Interpretation

This is an exception-discovery report, not an instruction to change member access. Each identified case remains private and requires evidence review.

Trainerize product subscriptions, Class Access add-ons and credit balances remain outside automated reconciliation until reliable API reads are verified.
