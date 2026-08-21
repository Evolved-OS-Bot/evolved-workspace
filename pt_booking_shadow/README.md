# PT Booking Continuity Shadow

Read-only auditor for The Evolved's active personal-training calendars.

## Behaviour

- Runs a full reconciliation every Monday at 5:30 am Australia/Brisbane.
- Reads 8 historical weeks and 15 future weeks from the 15 active PT calendars.
- Infers each client's canonical weekly pattern using deterministic recurrence evidence.
- Compares the next 13 expected occurrences with actual GHL events.
- Matches exact contact, start-time and duration coverage across every approved
  PT calendar. A trainer-cover or calendar-reassigned occurrence is retained as
  structured evidence and is not reported as a gap.
- Counts a rescheduled appointment anywhere in the same ISO week against that
  week's PT entitlement.
- Counts an unmatched surplus appointment in the immediately following week as
  a make-up for the prior week's deficit. The following week's own expected
  sessions are matched first, so a normal booking cannot be consumed twice.
- Protects every exact recurring booking before matching same-week
  reschedules. A later booked slot can no longer be consumed by an earlier gap
  and then incorrectly reported as missing itself.
- Excludes expected occurrences inside recorded GHL hold start/end windows.
- Suppresses booking actions when the shared revenue controller confirms an
  approved payment or lifecycle pause.
- Reclassifies a no-booking contact as `GHL_ONLY_PT_RECORD_REVIEW` when GHL is
  the only active-PT signal and there is no Active PT workbook row, supported
  payment evidence or active Trainerize access.
- Keeps unexplained extra appointments as evidence; shadow mode never removes
  them or assumes they are errors.
- Sends Admin Eve an exception-led email and CSV.
- Suppresses routine `FORMER_PT` rows from the email and CSV while retaining
  `FORMER_PT_WITH_FUTURE_BOOKINGS` as an actionable cleanup exception.
- Calculates two Monday utilisation measures from the same retained event set:
  literal PT bookings and booked delivery hours.
- Can write the trainer split and totals to the matching Monday column in Brown
  & Casserly when `KPI_WRITE_ENABLED=true`.
- Can add read-only Stripe entitlement, Trainerize access and Brown & Casserly
  Active PT evidence to each GHL booking-continuity result.
- Reuses the revenue controller's latest resolved PT classification, protected
  PTMinder/EziDebit receipt register, approved Stripe-email aliases and approved
  external-payment records instead of independently reopening resolved cases.
- Reads `Session X/Y` counters from GHL appointment descriptions or notes for
  verified prepaid-pack clients.
- Prompts for renewal when a clean terminal session is approaching, flags
  bookings after a clean pack end, and fails closed when counters regress,
  duplicate or switch pack totals.
- Queues targeted checks after authenticated GHL webhook events.
- Never creates, edits or deletes GHL data.
- Runs a daily 6:20 am read-only PT roster self-mending comparison after the
  shared source refreshes. It compares Sales and Active PT rows with accepted
  lifecycle, commercial and Trainerize evidence, stores exact preconditioned
  cell proposals and publishes aggregate counts to the operating-data hub.
- Keeps PT roster writes, row creation and row deletion disabled. Identified
  proposals are available only through the protected service endpoint.

## Safety boundary

The application refuses to start unless `SHADOW_MODE=true`. `GHLReadOnlyClient`
exposes GET operations only. No GHL mutation endpoint is implemented.

PT cancellation suppresses top-up recommendations. Only appointments strictly
after `CS: Final Access Date` can be classified as hypothetical removals.

PT holds pause top-up recommendations and retain existing bookings.

Recorded hold windows are respected even when the contact's current status has
since moved on. This prevents an approved, requested or processed historical
hold from appearing as a gap inside an otherwise valid series.

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

Identity matching uses normalised email for Stripe and Trainerize, then approved
canonical-to-alternate email links. Brown & Casserly uses email first and phone
second. Names are never used as identity keys.

Commercial support can be established by direct Stripe entitlement, a verified
prepaid-pack mapping, a current protected PTMinder/EziDebit receipt, a resolved
PT classification from the revenue controller, or a current owner-approved
external-payment record. External-payment confirmations expire after 14 days
unless reconfirmed.

The first exception layer reports:

- an active PT contact without an email required for deterministic matching;
- Brown & Casserly active PT without an entitled Stripe subscription;
- future GHL PT bookings without active Trainerize access;
- future GHL PT bookings without a matching Brown & Casserly Active PT row;
- a source-read failure while preserving the GHL-only booking audit.

For an explicitly verified prepaid pack, the second exception layer reports:

- no valid `Session X/Y` counter in the active appointment series;
- a contradictory counter sequence that must be corrected or confirmed;
- future bookings after the first clean terminal `Session Y/Y`; or
- a clean terminal session inside the 21-day renewal window.

A missing Stripe subscription is phrased as a review, not a cancellation or
debt conclusion, because prepaid packs and approved manual payments can be
valid exceptions. Appointment counters do not prove payment and payment does
not prove sessions remaining; the two evidence sources are joined only after
the PaymentIntent-to-contact relationship is approved. No Stripe, Trainerize
or GHL write method is implemented.

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
- `POST /revenue/run?kind=monday&sendEmail=false`
- `POST /revenue/run?kind=friday&sendEmail=false`
- `GET /revenue/runs/latest`
- `POST /revenue/pt-roster-self-mending/refresh`
- `GET /revenue/pt-roster-self-mending/status?identified=false`
- `POST /revenue/evidence/legacy`
- `GET /revenue/evidence/legacy/status`
- `POST /revenue/evidence/identity-links`
- `POST /revenue/evidence/account-classifications`
- `GET /revenue/evidence/shared/status`

Protected endpoints require `X-Webhook-Secret` or a Bearer token matching
`WEBHOOK_SHARED_SECRET`.

The revenue controller runs Monday at 6:30 am and Friday at 4:30 pm in
Australia/Brisbane. It stores its audit database and identified evidence below
`/data/revenue-gap-control/`; scheduled reports are sent to
`REVENUE_REPORT_TO`, which defaults to Peter's business address.

The PT roster self-mending shadow runs daily at 6:20 am Brisbane time. Every
proposal carries the exact Sheet, row, column, current value, proposed value,
evidence and full-row SHA-256 precondition. No proposal is applied while the
shadow gate is active.

The evidence replacement endpoints strictly validate and atomically replace the
PTMinder/EziDebit register, approved identity links and account
classifications. Status responses expose only row counts and SHA-256
fingerprints. Use
`scripts/upload_legacy_payment_evidence.py` through `railway run` so the
production secret is never placed on the command line or printed.

## Railway

Deploy as a separate service from the daily triage report. Use one Gunicorn
worker and mount a persistent volume at `/data`.

The governed roster acceptance check runs at 6:15 am and 6:15 pm Brisbane
time. Override the comma-separated hours only through
`ROSTER_REFRESH_HOURS`; the default is `6,18`.

The first report must be run privately with `sendEmail=false`. Enable email only
after the contact cohort and finding categories have been reviewed.

Keep `KPI_WRITE_ENABLED=false` for the first deployment. Validate one live
calculation against the target workbook cells, then enable the write.

## Graduation

Shadow mode runs for at least four weekly audits. Appointment write access is a
separate phase and requires at least 95% Admin-confirmed accuracy with zero
incorrect cancellation boundaries.
