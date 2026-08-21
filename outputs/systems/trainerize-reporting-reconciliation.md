# Trainerize Reporting and Reconciliation

## Purpose

This control compares the current membership signals in GHL, Stripe and Trainerize, then joins the active Trainerize roster to the recovered longitudinal workout history.

It is read-only. It does not provision, deactivate, reactivate, email or otherwise change a client account.

## Run

From the workspace root:

```bash
python3 scripts/run_trainerize_reporting.py
```

Daily runs use Stripe subscription status as the automated commercial-entitlement signal. Approved legacy PTMinder/EziDebit payers require a retained manual classification because this control does not connect to that processor.

A deeper Stripe billing audit can include the latest 90 days of invoices:

```bash
python3 scripts/run_trainerize_reporting.py --include-invoices
```

Invoice mode is intentionally not the routine default because subscription status supplies the primary entitlement signal without crawling billing history.

## Source of Truth

| Question | Source |
|---|---|
| Who is the person and what is their recorded lifecycle state? | GHL |
| Is there a current commercial entitlement? | Stripe subscription by default; approved legacy PTMinder/EziDebit receipt by manual exception |
| Does the person currently have coaching-app access? | Trainerize roster |
| Is the person on the staff-maintained active or cancellation roster? | Brown & Casserly Pty Ltd 2026 |
| What training was recorded? | Trainerize longitudinal database |
| When was the last recorded Strength Assessment? | Private Strength Assessment database |

Identity matching uses exact, case-insensitive email plus a private owner-confirmed identity crosswalk. Name-only and fuzzy matching are prohibited. A cross-system email difference may be linked only after the owner confirms the identity; the evidence is retained in `data/private/integration-reporting/identity_links.csv`.

Legitimate staff, test, complimentary or externally billed accounts may be excluded from unexplained-entitlement exceptions only through the owner-approved private register at `data/private/integration-reporting/account_classifications.csv`.

Legacy PTMinder/EziDebit payment evidence must identify the client, completed receipt and covered period. It does not make PTMinder a current onboarding or coaching-delivery system.

## Outputs

Identified operational files stay in:

`data/private/integration-reporting/`

Each completed run retains a private SQLite snapshot and timestamped CSVs for:

- the cross-system identity register;
- exceptions and their evidence;
- active-member performance;
- remarkable-results candidates; and
- reassessments due.

The share-safe aggregate summaries are:

- `outputs/trainerize-reporting-reconciliation/latest-reconciliation-summary.md`
- `outputs/trainerize-reporting-reconciliation/latest-performance-summary.md`

The aggregate files contain no names, emails or Trainerize user IDs. Do not upload the private run directory to Drive.

## Current Coverage

The read-only service-change validation run `20260730T060535Z` reconciled:

- 2,790 GHL contacts;
- 2,141 GHL opportunities;
- 287 Stripe customers;
- 304 Stripe subscriptions;
- 152 active Trainerize clients; and
- 424 deactivated Trainerize clients.

Detailed recovered workout history was available for 147 of the 149 active Trainerize clients. The historical workout source was current through 21 July 2026.

The 30 July run produced 570 review rows across all severities and historical hygiene categories. It confirmed Sue Goodwin's continuing Trainerize access for Evolved Anywhere and Tania Stiles's active account, but product and program state still require direct verification before Tania's 5 August service-change acceptance.

### Membership service changes

Trainerize access is a required independent surface in `reference/sops/membership-service-change-control.md`. A service change must reuse the verified account identity, preserve access when the new service includes it and fail closed when the intended program, group or product cannot be proven.

The reporting reconciliation remains read-only and cannot accept a service change by itself. The operating-data hub accepts the new current service only after Trainerize, billing, GHL lifecycle, appointments, workbooks and reporting all agree.

## Exception Handling

Every exception includes severity, evidence, an owner, a recommended action and `auto_action_allowed=false`.

The report is a review queue, not authority to change access. In particular:

- a Stripe entitlement without Trainerize access must be checked for identity, start date and intended service;
- active Trainerize access without GHL or Stripe entitlement may represent staff, complimentary, assessment, manually paid or stale access;
- duplicate emails require approved record review;
- reviewed Stripe duplicates are suppressed only when the sole entitled subscription remains attached to the registered authoritative customer, while all historical customers remain untouched;
- a Stripe subscription with `pause_collection` is not current service entitlement even when Stripe continues to label the subscription `active`;
- GHL contacts without email are low-priority data hygiene unless they also carry an active-member signal; and
- cancellation action requires an accepted cancellation record and verified final access date.

Historical tags are service-specific. `old pt client` must not hide a valid current SGPT `member` signal, and `old member` must not by itself prove that a current PT service has ended. A generic `personal training` tag is not sufficient entitlement evidence because it remains on some former-client records.

A PT final-access date must not deactivate the whole Trainerize account when another service, such as SGPT, remains current.

### Operational workbook synchronization

Brown & Casserly Pty Ltd 2026 is the staff-maintained operational roster. Every owner-approved membership status correction must be checked against `Active SGPT`, `Active PT`, `SGPT Cancellations` and `PT Cancellations` before the review is closed.

Remove confirmed non-members from the active tabs. Preserve or add cancellation history without inventing cancellation dates; when the original date cannot be evidenced, leave it blank and add an audit note so monthly cancellation KPIs are not distorted.

## Known Limitations

- Trainerize product subscriptions, program/group state, Class Access add-ons and credit balances are not yet reliably exposed in this control.
- Retained past `appointmentV2` group-class bookings are treated as an operational attendance proxy because trainers remove a booking when a client does not attend. Trainerize does not provide a verified check-in signal in this response, so the proxy must remain explicitly labelled and reviewed against operating compliance.
- The performance report reuses the last recovered detailed workout database; it does not re-extract every workout during the daily reconciliation.
- Inactivity is workout-log recency, not guaranteed facility attendance.
- Strength improvement is observational and uses estimated one-repetition maximum.
- Remarkable-results candidates require coach validation and member consent before marketing use.
- The former local Codex automation named `Daily Trainerize reconciliation` is paused. The Railway `Retention Intelligence` service now owns the 5:45 am Brisbane read-only schedule, preventing duplicate extraction.
- PTMinder/EziDebit is not connected, so approved legacy payers remain a manual commercial-evidence exception.

## Validation

Run the safety and logic suite with:

```bash
python3 -m unittest \
  scripts/test_membership_reconciliation.py \
  scripts/test_trainerize_performance_reporting.py \
  scripts/test_preview_trainerize_membership.py
```

The relevant safety and logic suites pass, and the reporting runner has completed a live read-only run. It has no implemented GHL, Stripe or Trainerize write path.

On 24 July 2026, an owner-authorised, allowlisted lifecycle cleanup was performed separately from the reporting runner. Every GHL and Trainerize change used expected-state checks and post-write verification. The Brown & Casserly operational workbook was then synchronized and the identified evidence was retained privately. This controlled cleanup does not give the recurring report authority to make future changes.

API reads use bounded retries. GHL contacts are read through the supported Search Contacts endpoint using numbered pages. If the reported total changes, a page ends early or a contact ID is duplicated while contacts are changing, the partial snapshot is discarded and restarted from page one.

GHL opportunities continue to use their documented next-page URL. A failed source snapshot does not overwrite the latest completed report.

## Scheduled Validation

Phase 4 observation began on 26 July 2026 through the Railway `Retention Intelligence` service. The service retains identified daily snapshots in private PostgreSQL and exposes authenticated run/preview endpoints plus a non-identifying health endpoint.

The first production run, `20260725T224824Z-e52d390f`, completed successfully with 149 active Trainerize accounts and 141 included member records. It classified 40 Thriving, 41 Stable, 16 Drifting, 14 At risk and 30 Insufficient data.

The first seven consecutive Railway runs are a shadow-validation period. A run counts only when all required source snapshots complete and the timestamped evidence is retained. `SHEETS_WRITE_ENABLED=false` remains in force until the gate is reviewed; low-priority historical hygiene rows are summarized rather than actioned, and no exception is auto-corrected.

### Railway performance consumer

The separate Railway service `Trainerize Performance` is live in read-only shadow mode at `https://trainerize-performance-production.up.railway.app`. It reuses a checksum-verified compact evidence bundle on a protected Railway volume instead of re-extracting the 1.5 GB longitudinal database for each report.

The first Railway shadow run completed on 27 July 2026 from reconciliation run `20260725T200024Z`. It reproduced the protected coverage of 149 active Trainerize accounts and 147 accounts with recovered workout detail. It produced 100 reassessment-due signals and 68 remarkable-results candidates; both are review queues and create no member, coach, marketing or system action.

The service published an aggregate `trainerize_performance` snapshot into the operating-data hub. No identified performance rows leave the protected volume.

Hub deployment `3b4f0932-930c-441f-84ad-5872c0a79f32` exposes the accepted aggregate on the CEO dashboard and CEO report API. The view shows roster coverage, detailed-workout coverage, reassessment reviews, potential results candidates, workout-source date, run ID and freshness. Review queues are explicitly labelled as non-authoritative signals.

The incremental production shadow refresh completed on 28 July 2026. It read 151 current active accounts, refreshed 683 tracked workouts from the rolling 21-day window and retained the earlier longitudinal history. The resulting report covers 150 accounts with detailed workouts, 102 reassessment-review signals and 70 potential results candidates; the workout source is current through 27 July. The two-account increase from the seed bundle is a live Trainerize roster change, not a counting discrepancy.

Railway service `Trainerize Performance Refresh` now owns a daily 5:15 am Brisbane cron. It triggers the protected refresh endpoint, waits for a new completed refresh and exits non-zero on timeout or failure. This avoids colliding with the separate 5:45 am Retention Intelligence extraction and makes the performance aggregate available before the 6:05 am CEO KPI cycle. The report then publishes the same accepted aggregate to the CEO dashboard and CEO report API. No Codex schedule exists.

The compact bundle is retained only for bootstrap and recovery. Source freshness is based on the last completed API observation, while the separate workout-source date reports actual member activity. Roster changes greater than 25 percent, an empty roster, duplicate identities or incomplete requested workout responses fail closed before the current roster is replaced.
