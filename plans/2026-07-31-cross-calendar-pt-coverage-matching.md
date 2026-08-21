# Plan: Cross-Calendar PT Coverage Matching

**Created:** 2026-07-31
**Status:** Complete
**Request:** Prevent false PT booking gaps when a valid occurrence has been moved to another approved trainer calendar.

## Verified failure mode

Bree Coleman's canonical pattern is Monday at 6:00 am with Katrina. A manual calendar-specific review treated 10 August as missing because the occurrence was absent from Katrina's calendar.

The GHL appointment still exists at the exact date, time and duration as a confirmed booking in Megan's active 30-minute PT calendar. The gap was therefore a lookup failure, not a booking failure.

The production reconciler already reads every active PT calendar and permits same-week reschedules, but an exact occurrence on another trainer calendar is not classified or evidenced explicitly. It currently falls through to the generic same-week matching pass.

## Changes

1. Match an expected occurrence by contact, exact start and duration across all approved PT calendars before using the broader same-week reschedule rule.
2. Prefer the canonical calendar when both canonical and alternate-calendar records exist.
3. Record every alternate-calendar exact match as structured evidence, including the expected and actual calendars and trainers.
4. Add a Bree-style regression test proving that a trainer-cover occurrence is healthy and does not generate a proposed booking.
5. Preserve duplicate detection when two active appointments exist at the same time.
6. Update the reconciliation SOP and manual review instructions: a calendar-specific absence can never establish a client-level gap.
7. Correct Bree's review-log classification and remove her from the unresolved-gap roadmap count.

## Validation

- Run the full `pt_booking_shadow` test suite.
- Confirm the new regression test returns `HEALTHY`, 13 weeks of coverage and one cross-calendar evidence record.
- Confirm the existing middle-gap and duplicate tests still fail closed correctly.
- Keep the service read-only; no GHL appointment mutation capability is added.

## Implementation result

Completed 31 July 2026.

- The reconciler prefers the canonical calendar, then accepts an exact contact, start-time and duration match in any other approved PT calendar.
- Alternate-calendar matches retain the appointment ID, expected and actual calendar IDs, and expected and actual trainers as structured evidence.
- Bree's trainer-cover failure mode is protected by a regression test.
- All 57 `pt_booking_shadow` tests pass.
- All 115 combined `pt_booking_shadow` and `revenue_gap_control` tests pass.
- The operating SOP, weekly audit run sheet, review log, roadmap, README and workspace instructions carry the same rule.
- Bree's Active PT note now records the confirmed Megan cover occurrence and no longer describes 10 August as an unresolved blank.
- Railway deployment is intentionally separate from this workspace implementation and remains pending.
