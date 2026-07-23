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
- Calculates two Monday utilisation measures from the same retained event set:
  literal PT bookings and booked delivery hours.
- Can write the trainer split and totals to the matching Monday column in Brown
  & Casserly when `KPI_WRITE_ENABLED=true`.
- Can add read-only Stripe entitlement, Trainerize access and Brown & Casserly
  Active PT evidence to each GHL booking-continuity result.
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

## Brown & Casserly KPI write

The legacy manual trainer block is preserved. The automated blocks use the
current trainer roster: Megan Brown, Piper Mae, Nora Silva, Katrina Parsons and
Leisa Smith.

The Monday calculation:

- covers Monday 00:00 to the following Monday 00:00 in Brisbane;
- attributes delivery by the exact active PT calendar name;
- excludes deleted, cancelled and no-show appointments;
- deduplicates by event ID and then contact plus start time;
- records one booking per retained appointment;
- converts retained appointment minutes into booked hours;
- fails closed if the dated column or expected trainer rows are missing or
  duplicated;
- overwrites the same dated cells on retry rather than appending.

Google Sheets writes are disabled by default. Railway requires
`GOOGLE_SERVICE_ACCOUNT_JSON` and local runs may instead use
`GOOGLE_SHEETS_CREDENTIALS_FILE`.

## Cross-system evidence

Set `CROSS_SYSTEM_RECONCILIATION_ENABLED=true` with protected Stripe,
Trainerize and Google credentials to add source evidence to the Monday report.

Identity matching uses normalised email for Stripe and Trainerize. Brown &
Casserly uses email first and phone second. Names are never used as identity
keys.

The first exception layer reports:

- an active PT contact without an email required for deterministic matching;
- Brown & Casserly active PT without an entitled Stripe subscription;
- future GHL PT bookings without active Trainerize access;
- future GHL PT bookings without a matching Brown & Casserly Active PT row;
- a source-read failure while preserving the GHL-only booking audit.

A missing Stripe subscription is phrased as a review, not a cancellation or
debt conclusion, because prepaid packs and approved manual payments can be
valid exceptions. No Stripe, Trainerize or GHL write method is implemented.

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

Keep `KPI_WRITE_ENABLED=false` for the first deployment. Validate one live
calculation against the target workbook cells, then enable the write.

## Graduation

Shadow mode runs for at least four weekly audits. Appointment write access is a
separate phase and requires at least 95% Admin-confirmed accuracy with zero
incorrect cancellation boundaries.
