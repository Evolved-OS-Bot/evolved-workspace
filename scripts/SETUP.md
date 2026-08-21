# Metrics Script Setup

One-time setup. Takes approximately 10 minutes.

---

## 1. Install Python dependencies

From the workspace root:

```bash
pip install -r scripts/requirements.txt
```

---

## 2. Create a Google Cloud service account

1. Go to https://console.cloud.google.com/
2. Create a new project — name it "Evolved Metrics"
3. Enable the Google Sheets API: APIs & Services → Enable APIs → search "Google Sheets API" → Enable
4. Create a service account: APIs & Services → Credentials → Create Credentials → Service Account
   - Name: `evolved-metrics`
   - Skip optional fields → Done
5. Click the service account → Keys tab → Add Key → Create new key → JSON → download
6. Rename the downloaded file to `google_credentials.json`
7. Move it to `scripts/google_credentials.json`
8. Copy the service account email address (looks like `evolved-metrics@your-project.iam.gserviceaccount.com`)

---

## 3. Share the Google Sheet with the service account

1. Open the Brown & Casserly KPI spreadsheet
2. Click Share
3. Paste the service account email address
4. Set permission to **Editor** (needed to write formulas)
5. Click Send

---

## 4. Update scripts/.env

Copy `scripts/.env.example` to `scripts/.env` and fill in the values:

```bash
cp scripts/.env.example scripts/.env
```

Then edit `scripts/.env` — the values are already set correctly if you haven't changed the spreadsheet ID.

---

## 5. Test the connection

```bash
python scripts/test_connection.py
```

If it prints the sheet title, you're connected.

---

## 6. Insert KPI formulas (one-time)

```bash
python scripts/insert_formulas.py
```

This writes all COUNTIFS formulas into the KPI tab. Safe to re-run — it only overwrites the formula cells.

---

## 7. Set up the update-metrics alias

Add to your `~/.zshrc`:

```bash
alias update-metrics='cd ~/Downloads/claude-workspace-evolved && python scripts/update_metrics.py'
```

Then:

```bash
source ~/.zshrc
```

---

## Troubleshooting

- **"File not found: google_credentials.json"** — check the file is at `scripts/google_credentials.json`
- **"403 Forbidden"** — sheet not shared with service account email; repeat Step 3
- **"400 Bad Request on formula insert"** — check the KPI tab name matches exactly: `KPI's The Evolved`
- **"Current week column not found"** — sheet date format may differ; check row 1 of KPI tab

---

## Trainerize API access

Trainerize credentials live in the same ignored `scripts/.env` file:

```dotenv
TRAINERIZE_GROUP_ID=your_group_id
TRAINERIZE_API_TOKEN=your_api_token
TRAINERIZE_API_BASE_URL=https://api.trainerize.com/v03
TRAINERIZE_LOCATION_ID=your_location_id
```

Test access from the workspace root:

```bash
python scripts/test_trainerize_connection.py
```

Use `TrainerizeClient` from `scripts/trainerize_client.py` in future scripts. The client applies Trainerize Basic authentication and exposes a reusable JSON request method. API reference: https://trainerize-dev.readme.io/reference

### Membership transition preview

Validate a proposed assessment-to-membership handoff without calling any external system:

```bash
python scripts/preview_trainerize_membership.py /path/to/synthetic-sale-event.json
```

The JSON event must include `correlation_id`, `email`, `trainerize_user_id`, `offer`, `agreement_signed`, `upfront_payment_status` and `membership_start_date`. The preview requires an existing Trainerize user, maps current and legacy offer labels to the correct free membership product, and uses the recorded membership start date. It never creates a client, sends an invitation or writes to Trainerize.

### Strength Assessment extractor

Build or refresh the private Strength Assessment database from the active Trainerize roster:

```bash
python scripts/extract_strength_assessments.py --start-date 2026-01-01
```

The identified database is stored at `data/private/strength-assessments/strength_assessments.sqlite`. That directory is ignored by Git. Normal runs print aggregate counts only.

The `baseline_assessments` view contains one deterministic earliest tracked assessment per female, non-test client. The `baseline_component_results` view provides one analysis-ready row per baseline while keeping historical assessment formats separate through `schema_version`.

The extractor also retrieves the Trainerize body weight recorded on each assessment date and stores it in `assessment_body_weights`. The baseline view exposes assessment body weight, timing quality, the best recorded Farmer Walk load and the formula-ready load-to-body-weight ratio. Exact dates stay in the private database; de-identified exports should retain only the timing-quality label.

Backfill body weights for assessments already stored without rescanning workouts:

```bash
python scripts/extract_strength_assessments.py --start-date 2025-06-01 --body-weight-only
```

An exact assessment-date body stat is preferred. The controlled fallback uses the latest client-summary weight only when its recorded date is within 30 days, and keeps that timing visible rather than treating it as exact.

Trainerize currently allows detailed workout retrieval only for active clients. The extractor can scan deactivated calendars with `--include-deactivated`, but detailed records may be logged as HTTP 403 errors until Trainerize grants historical access or supplies an export.

### Longitudinal strength audit

The resumable longitudinal extractor stores private roster, calendar, workout-detail, exercise-result, body-stat, goal, accomplishment and training-plan records in:

`data/private/trainerize-longitudinal-audit/trainerize_longitudinal.sqlite`

Run individual phases from the workspace root:

```bash
python scripts/extract_trainerize_longitudinal.py --phase roster --status all
python scripts/extract_trainerize_longitudinal.py --phase calendar --status all
python scripts/extract_trainerize_longitudinal.py --phase details --status active
python scripts/extract_trainerize_longitudinal.py --phase extras --status active
python scripts/extract_trainerize_longitudinal.py --phase candidates --status deactivated
```

Use `--user-id` repeatedly or `--user-ids-file` to constrain detail and extra extraction. The extractor is read-only and never changes a Trainerize account state.

Any temporary browser-based former-member reactivation must be prepared and reconciled through `trainerize_account_change_log.py`. Do not start another cohort while the database contains an unrestored change.

Build the analysis tables and workbooks with:

```bash
python scripts/analyze_trainerize_longitudinal.py
```

The de-identified deliverables live under `outputs/trainerize-longitudinal-audit-2026-07-21/`. The identified workbook and restoration evidence stay under `data/private/trainerize-longitudinal-audit/` and must not be uploaded or shared as part of the de-identified package.

### Membership reconciliation and performance reporting

The combined read-only control compares GHL lifecycle state, Stripe subscription entitlement and Trainerize access, then builds active-member workout, strength, inactivity, reassessment and remarkable-results reporting:

```bash
python3 scripts/run_trainerize_reporting.py
```

Routine runs do not fetch invoices. Use the following only for a deeper 90-day billing audit:

```bash
python3 scripts/run_trainerize_reporting.py --include-invoices
```

Required credentials in the ignored `scripts/.env` are:

```dotenv
GHL_API_KEY=your_location_api_key
GHL_LOCATION_ID=your_location_id
GHL_ADMIN_EVE_USER_ID=your_admin_eve_user_id
STRIPE_RESTRICTED_KEY=your_read_only_restricted_key
TRAINERIZE_GROUP_ID=your_group_id
TRAINERIZE_API_TOKEN=your_api_token
TRAINERIZE_LOCATION_ID=your_location_id
```

Identified snapshots and action lists stay under `data/private/integration-reporting/`. Share-safe aggregate summaries are written to `outputs/trainerize-reporting-reconciliation/`.

The report never changes a source system. Review the operating notes and limitations in `outputs/systems/trainerize-reporting-reconciliation.md` before acting on an exception.

### Strength Assessment attendance shadow control

The Operating Data Hub collects the approved GHL Strength Assessment calendar, matches the existing Consultant Feedback form evidence and exposes governed attendance summaries. Configure Railway with:

```dotenv
GHL_API_KEY=your_location_api_key
GHL_LOCATION_ID=your_location_id
GHL_ADMIN_EVE_USER_ID=your_admin_eve_user_id
SA_ATTENDANCE_CALENDAR_IDS=HSVEzfJH4nice96IxHem
SA_ATTENDANCE_GRACE_MINUTES=60
SA_ATTENDANCE_MATCHING_DAYS=7
SA_ATTENDANCE_LOOKBACK_DAYS=120
SA_ATTENDANCE_GHL_WRITE_ENABLED=false
SA_ATTENDANCE_SHEETS_WRITE_ENABLED=false
REPORTING_V2_MANUAL_INPUTS_ENABLED=false
SA_ATTENDANCE_SHEET_TAB=SA Attendance
SA_ATTENDANCE_SHEET_TAB_ID=1446062006
```

Keep both write gates false through two complete Monday-to-Sunday shadow cycles. If rollback is needed, disable both writers, keep collection running, retain the last complete snapshot and mark show rate unavailable or provisional; never fall back to Appointments column K.

Keep `REPORTING_V2_MANUAL_INPUTS_ENABLED=false` until the controlled input surface, independent approver and first accepted input fixture have passed review. Reporting V2 shadow event and metric storage does not require this input gate to be enabled.

The read-only historical audit is:

```bash
.venv/bin/python scripts/backfill_sa_attendance.py
```

Identified detail stays under `data/private/integration-reporting/`. Historical weekly KPI cells are not restated without separate approval.

### KPI revenue-gap and active-client audit

The standard runner refreshes the protected membership and PT booking evidence, then combines it with the current Active SGPT and Active PT rosters, approved legacy-payment evidence and confirmed KPI cash:

```bash
.venv/bin/python scripts/run_revenue_gap_control.py
```

On Monday the runner audits the just-completed week; on other days it audits the current service week. Explicit historical dates can be supplied with `--window-start` and `--window-end`.

The controller reads the KPI cash cell dated the Monday after the service window unless a separately confirmed `--cleared-cash` amount is supplied to the underlying module.

Copy the controlled CSV templates from `reference/templates/` into the ignored `data/private/revenue-gap-control/` directory. PTMinder and EziDebit clients remain unresolved until the legacy-payment register contains current approved receipt evidence.

The aggregate summary is written to `outputs/revenue-gap-control/latest-summary.md`. Identified client evidence, exceptions and the durable audit database stay under `data/private/revenue-gap-control/`.

This system does not edit the workbook, GHL, Stripe, Trainerize or appointments. The operating cadence, close rules and promotion gate are documented in `outputs/systems/kpi-revenue-gap-controller.md`.

Before uploading the second independent PT Minder V2 capture, run the aggregate-only completeness gate:

```bash
.venv/bin/python scripts/verify_pt_minder_capture_gate.py \
  data/private/revenue-gap-control/pt-minder-snapshot.json \
  --prior-observed-at 2026-07-27T08:21:05Z
```

The gate expects a new observation, approximately 27 accounts and at least 500 accepted payment/debit events. A pass means the capture is complete enough to upload; it does not promote the feed. Upload with `scripts/upload_pt_minder_snapshot.py`, rerun protected revenue parity and promote only if every governed comparison is exact. PT Minder Charge entries and displayed balances remain excluded.
