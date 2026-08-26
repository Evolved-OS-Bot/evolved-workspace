# Cancellation Finalizer

Railway-only, fail-closed final-access automation for Membership and PT
cancellations. GHL supplies the exact boundary request; the service persists a
stable case and performs each external step only after the previous step has a
verified receipt.

## Request

`POST /api/v1/cancellations/finalize` accepts JSON only when all three request
headers are valid:

- `X-Cancellation-Timestamp`: current Unix seconds
- `X-Cancellation-Nonce`: a unique 16-128 character URL-safe value
- `X-Cancellation-Signature`: `sha256=<hex HMAC>` over the exact bytes
  `<timestamp>.<nonce>.<request-body>`

The signature may be no more than five minutes old. A nonce is claimed once in
Postgres and a replay is rejected before any case is processed.

### Governed GHL signing relay

HighLevel does not receive the HMAC signing secret. When explicitly enabled,
its two Draft recovery workflows may instead call one service-specific relay:

- `POST /api/v1/relay/cancellations/membership`
- `POST /api/v1/relay/cancellations/pt`

Each route requires `Authorization: Bearer <service-specific relay secret>` and
exact `application/json`. The relay accepts only the documented cancellation
fields, rejects duplicate or unknown JSON keys, binds the cancellation type to
the route, canonicalises the body, creates a fresh timestamp and nonce, signs
the exact canonical bytes in memory, and passes the result through the same
signature and durable nonce boundary as the direct endpoint. It does not expose
the signing secret or provide a general-purpose forwarding URL.

The relay is disabled by default. Its bearer secrets are independent,
revocable credentials with a much narrower authority than the signing secret;
all normal finalizer source read-backs, date checks, stable idempotency and the
global write gate still apply. Each relay secret must contain at least 32
characters, the Membership and PT values must differ, and neither may reuse the
HMAC signing secret or admin secret. Invalid relay configuration fails closed.

```json
{
  "contact_id": "GHL contact ID",
  "email": "exact normalized email",
  "cancellation_type": "Membership",
  "final_access_date": "2026-08-31",
  "scope": "service_only",
  "final_task_id": "optional exact GHL task ID"
}
```

Membership and PT are the only accepted cancellation types. `scope` is
`service_only` unless an approved full-account closure explicitly supplies
`all_services`. A PT-only ending preserves Trainerize when an Active SGPT or
Active Online relationship continues.

## Required production configuration

- `DATABASE_URL`
- `CANCELLATION_WEBHOOK_SIGNING_SECRET`
- `CANCELLATION_ADMIN_SECRET`
- Relay (only when deliberately enabled): `CANCELLATION_RELAY_ENABLED=true`,
  `CANCELLATION_RELAY_MEMBERSHIP_SECRET`, `CANCELLATION_RELAY_PT_SECRET`, and
  optional `CANCELLATION_RELAY_RATE_LIMIT_PER_MINUTE` (default 10)
- `CANCELLATION_FINALIZER_WRITE_ENABLED=true`
- GHL: `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_ADMIN_EVE_USER_ID`
- Stripe: `STRIPE_RESTRICTED_KEY`
- Sheets: `GOOGLE_SPREADSHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`
- Trainerize reads: `TRAINERIZE_GROUP_ID`, `TRAINERIZE_API_TOKEN`,
  `TRAINERIZE_LOCATION_ID`, optional API base URL
- Trainerize write: the same guarded ABC Trainerize API connection invokes
  `user/setStatus` with sign-in and messaging disabled, then proves the exact
  account moved from the active roster to the deactivated roster
- Hub: `OPERATING_DATA_HUB_URL`, `OPERATING_DATA_HUB_CURRENT_PEOPLE_READ_KEY`

The public health endpoint returns only `{"status":"ok"}`. Authenticated
readiness, case status and due-job controls live under `/api/v1/admin/` and use
the separate admin secret. Writes stay disabled unless the explicit write flag
and every required connector are present.

All responses disable caching and add restrictive browser security headers.
Authentication events log only a random request ID, a one-way network
fingerprint, the outcome and a non-sensitive reason. Member identifiers,
payloads, credentials and request headers are not written to security logs.

The production image runs one non-root Gunicorn worker with four threads. The
single worker also makes the in-process rate limiter deterministic; durable
Postgres nonce claims remain authoritative across restarts.

## Processing order

1. Brisbane final-access boundary
2. GHL identity and lifecycle preflight
3. Exact Stripe terminal read-back
4. Trainerize preserve/deactivate decision and read-back
5. Exact-email active-roster removal and read-back
6. GHL terminal lifecycle, tags and Cancellation OS opportunity read-back
7. governed Hub terminal projection
8. optional exact final task completion

The worker retries delayed Hub projection hourly. An ambiguous identity,
duplicate row, continuing-service conflict or failed write creates one
deduplicated Admin Eve exception and does not falsely complete the final task.

## Local verification

```bash
.venv/bin/python -m unittest discover -s cancellation_finalizer/tests -t . -v
```
