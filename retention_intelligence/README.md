# Retention Intelligence

Read-only Railway service for explainable member-engagement and retention review.

## What it does

- Runs the established GHL, Stripe and Trainerize membership reconciliation.
- Reads only the latest 112 days of tracked Trainerize workout-calendar activity for current active accounts.
- Counts retained past `appointmentV2` group-class bookings as an operational attendance proxy. Trainers remove the booking when a client does not attend; this is not a platform check-in.
- Compares each member's latest 28-day activity with her own preceding 12-week baseline.
- Stores a dated identified snapshot in private PostgreSQL.
- Produces `Thriving`, `Stable`, `Drifting`, `At risk`, `Insufficient data`, `Operational exception` and `Excluded` classifications with plain-language reasons.
- Can populate allowlisted `Retention Radar` and `Retention KPI` tabs in Brown & Casserly.

It does not create tasks, send member communications or mutate GHL, Stripe, Trainerize or member accounts.

## V1 interpretation

This is a coach decision-support control, not a churn-prediction model.

Fit & Flexible clients use retained past class bookings as their engagement source when at least four bookings exist in the personal baseline window. Other services continue to use tracked workouts by default, with class bookings filling a sparse workout baseline.

Staff, owners, demo and approved internal accounts are excluded through the protected account-classification register.

## Schedule

The Railway scheduler runs daily at 5:45 am in Australia/Brisbane.

The first seven runs are a shadow-validation period. Google Sheets writes remain disabled during this period.

The class-attendance proxy records counts over 7, 28 and 90 days, a preceding 12-week personal baseline, recent weekly rate, percentage change, last retained class booking and days since that booking. Future bookings, personal appointments and non-class calendar items are excluded.

## Local validation

Copy `.env.example` to `.env`, use a local SQLite URL and keep Sheet writes disabled:

```sh
DATABASE_URL=sqlite:////tmp/retention_intelligence.db
SHEETS_WRITE_ENABLED=false
ENABLE_SCHEDULER=false
```

Then run:

```sh
python3 -m pytest retention_intelligence/tests
python3 -m retention_intelligence.run_once
```

## Railway configuration

Deploy this directory as a separate Railway service and link a PostgreSQL database.

Required protected variables:

- GHL API key and location ID
- Stripe restricted key
- Trainerize group ID, API token and location ID
- webhook shared secret
- PostgreSQL `DATABASE_URL`
- identity-link, authoritative-customer and account-classification JSON controls

Google credentials can be configured during shadow validation, but keep `SHEETS_WRITE_ENABLED=false`. After seven successful runs and a reviewed preview, enable writes and allow the service to create or update only `Retention Radar` and `Retention KPI`.

## Endpoints

- `GET /health`: non-identifying health status
- `POST /run?writeSheets=false`: authenticated manual run
- `GET /runs/latest`: authenticated latest run status
- `GET /preview`: authenticated identified current radar

Protected endpoints require `X-Webhook-Secret` or a matching Bearer token.

## Privacy and recovery

PostgreSQL is the identified system of record for retention snapshots. Google Sheets holds the current operating view and aggregate weekly history.

A failed source read creates a failed run and does not replace the latest successful radar. The service logs counts and run IDs, never names or emails.
