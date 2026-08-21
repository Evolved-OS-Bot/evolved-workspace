# Payment and Booking Purpose Triage

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

The former 17-service `payment_booking_unresolved` bucket is now separated by
the evidence needed for the next action:

- two PT services have future bookings while payment and entitlement remain
  unresolved;
- 15 services have no current authoritative payment evidence;
- zero services have an active contract without a current paid receipt in this
  audit cycle.

Commercial coverage is unchanged at 93 fully verified clients and 39 pending
clients with 41 service gaps. This build improves decision quality rather than
promoting uncertain evidence.

## Governed Actions

| Bucket | Clients | Service gaps | Owner | Action |
| --- | ---: | ---: | --- | --- |
| PT booked, payment unresolved | 2 | 2 | Admin Eve | Resolve payment purpose and entitlement before treating future bookings as commercially covered. |
| No current payment evidence | 15 | 15 | Admin Eve | Locate the authoritative payment rail or approved non-recurring entitlement. |

Roster state, GHL lifecycle and Trainerize access are not payment proof. PT
Minder displayed balances and its Charge function remain excluded.

## Production Verification

- Accepted commercial snapshot:
  `20260727T233558Z-bf8052d3`.
- Hub deployment:
  `bafe3fe4-ccd2-4bde-a7e1-ec4578de1ec6`.
- PT/Revenue deployment:
  `37b25759-bc05-430f-b7ce-e9f2ed2b61ef`.
- 219 connected hub and controller tests passed.
- The dashboard was visually verified with eight current buckets and 25
  high-priority service gaps.
- No client, payment, membership, booking or Google Sheet record was changed.
- No new schedule was created.

## Next Build

Completed by
`outputs/reporting-control-plane/prepaid-renewal-entitlement-promotion-2026-07-28.md`.
The next queue work is the 15 no-current-payment-evidence services and the two
booked PT services with unresolved payment purpose.
