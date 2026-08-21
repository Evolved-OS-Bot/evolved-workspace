# Plan: Governed Purchased-Service Terms

**Date:** 2026-07-28
**Status:** Complete
**Owner:** Peter Brown
**Runtime:** Railway only

## Objective

Create a protected, auditable record that binds a one-time Stripe invoice to
the beneficiary, service type and exact entitlement dates.

## Controls

- Do not infer service or duration from payment amount.
- Require a unique term ID, Stripe invoice ID, purchaser, beneficiary, service,
  start date, end date, approval owner and approval date.
- Reject invalid, duplicate, incomplete or backwards-dated records.
- Preserve revoked terms without allowing them to create entitlement.
- Count approved terms only inside their exact effective window.
- Keep future and expired terms visible as distinct exception states.
- Keep all member, booking, contact, payment and Google Sheet systems
  read-only.
- Reuse the existing Railway report cycle; create no Codex or additional
  reporting schedule.

## Implementation

1. Add the protected purchased-service-term register and authenticated
   replacement endpoint to the PT/revenue Railway service.
2. Publish approved terms through the existing commercial-evidence contract.
3. Preserve the Stripe invoice reference in the canonical entitlement audit
   metadata.
4. Route future, expired and missing terms separately on the CEO dashboard.
5. Add contract, runtime, publisher and queue regression tests.
6. Deploy the affected Railway services, refresh commercial evidence and
   verify the production dashboard.
7. Update the reporting architecture, roadmap and acceptance record.

## Production Completion: 29 July 2026

- Seven clients were reconciled from exact Stripe invoices, GHL membership
  agreements and product descriptions.
- Eight term records were loaded because Fast Track includes both SGPT and one
  weekly 30-minute PT session.
- Tara Berge's $50 deposit and $349 balance are retained as one split-payment
  purchase.
- The CEO dashboard moved from 100 to 107 commercially verified clients, 32
  to 25 pending clients, 34 to 26 service gaps and 20 to 13 high-priority
  gaps.
