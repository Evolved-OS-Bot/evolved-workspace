# Cancellation Finalizer

Railway-only, fail-closed final-access automation for Membership and PT
cancellations. GHL supplies the exact boundary request; the service persists a
stable case and performs each external step only after the previous step has a
verified receipt.

## Request

`POST /api/v1/cancellations/finalize` with header
`X-Cancellation-Secret` and JSON:

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
- `CANCELLATION_FINALIZER_SECRET`
- `CANCELLATION_FINALIZER_WRITE_ENABLED=true`
- GHL: `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_ADMIN_EVE_USER_ID`
- Stripe: `STRIPE_RESTRICTED_KEY`
- Sheets: `GOOGLE_SPREADSHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`
- Trainerize reads: `TRAINERIZE_GROUP_ID`, `TRAINERIZE_API_TOKEN`,
  `TRAINERIZE_LOCATION_ID`, optional API base URL
- Trainerize write: `TRAINERIZE_DEACTIVATE_WEBHOOK_URL` and
  `TRAINERIZE_DEACTIVATE_WEBHOOK_SECRET`; the receiver must invoke the official
  Trainerize Deactivate Client action and accept the stable idempotency key
- Hub: `OPERATING_DATA_HUB_URL`, `OPERATING_DATA_HUB_API_KEY`

The health endpoint lists missing variable names but never values. Writes stay
disabled unless the explicit write flag and every required connector are
present.

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
