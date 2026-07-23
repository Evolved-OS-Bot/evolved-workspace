# PT Booking Continuity Shadow

Read-only auditor for The Evolved's active personal-training calendars.

## Behaviour

- Runs a full reconciliation every Monday at 5:30 am Australia/Brisbane.
- Reads 8 historical weeks and 15 future weeks from the 15 active PT calendars.
- Infers each client's canonical weekly pattern using deterministic recurrence evidence.
- Compares the next 13 expected occurrences with actual GHL events.
- Counts a rescheduled appointment anywhere in the same ISO week against that
  week's PT entitlement.
- Counts an unmatched surplus appointment in the immediately following week as
  a make-up for the prior week's deficit. The following week's own expected
  sessions are matched first, so a normal booking cannot be consumed twice.
- Keeps unexplained extra appointments as evidence; shadow mode never removes
  them or assumes they are errors.
- Sends Admin Eve an exception-led email and CSV.
- Queues targeted checks after authenticated GHL webhook events.
- Never creates, edits or deletes GHL data.

## Safety boundary

The application refuses to start unless `SHADOW_MODE=true`. `GHLReadOnlyClient`
exposes GET operations only. No GHL mutation endpoint is implemented.

PT cancellation suppresses top-up recommendations. Only appointments strictly
after `CS: Final Access Date` can be classified as hypothetical removals.

PT holds pause top-up recommendations and retain existing bookings.

Contacts with an active PT hold or cancellation are hydrated from their full
GHL contact record before reconciliation. This prevents the bulk contact list
from omitting a status-sensitive date such as `CS: Final Access Date`.

## Local test

Use a local `.env` copied from `.env.example`. Set `REPORT_DRY_RUN=true` and
`DATABASE_PATH=/tmp/pt_booking_shadow.db`.

```sh
python3 -m pytest pt_booking_shadow/tests
python3 -m pt_booking_shadow.run_weekly
```

## Runtime endpoints

- `GET /health`
- `POST /run?sendEmail=false`
- `POST /webhooks/ghl`

Protected endpoints require `X-Webhook-Secret` or a Bearer token matching
`WEBHOOK_SHARED_SECRET`.

## Railway

Deploy as a separate service from the daily triage report. Use one Gunicorn
worker and mount a persistent volume at `/data`.

The first report must be run privately with `sendEmail=false`. Enable email only
after the contact cohort and finding categories have been reviewed.

## Graduation

Shadow mode runs for at least four weekly audits. Appointment write access is a
separate phase and requires at least 95% Admin-confirmed accuracy with zero
incorrect cancellation boundaries.
