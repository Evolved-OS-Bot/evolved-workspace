# Reporting V2 Dependency and Manual-Input Register

**Date:** 2026-07-29  
**Status:** Phase 0 baseline  
**Scope:** Current KPI workbook, hub compatibility readers and proposed governed replacements

## Current Workbook Dependencies

| Current surface | Upstream dependency | Downstream consumer | Risk | V2 replacement |
|---|---|---|---|---|
| `KPI's The Evolved` weekly columns | Fixed formulas and manual amounts | Hub KPI adapter, Discord/current-data, management review | Fixed cell contract and mixed definitions | Versioned metric observations |
| Active SGPT count | Fixed baseline plus Sales less SGPT cancellations | KPI and CEO reporting | Drift from current lifecycle state | Canonical person/service as-of projection |
| Active PT count | Fixed baseline plus Sales less PT cancellations | KPI and CEO reporting | Drift and multi-service ambiguity | Canonical person/service as-of projection |
| `Subscribes` | Worksheet rows | Subscriber KPI | No immutable event/contact ID | GHL lead/subscription event |
| `Appointments` | Workflow/manual rows | Leads, bookings, show and conversion | Manual states; no appointment ID | GHL appointment event and series ledger |
| `Sales` | Workflow/manual rows | Sales, new cash, service mix, onboarding checklist | Sale, fulfilment and cash combined | Separate sale, components, payment allocation and fulfilment events |
| Cancellation tabs | Workflow/manual rows | Cancellation and net growth formulas | Notice date and final access can be conflated | Lifecycle event intervals |
| Active roster tabs | Workflow/manual rows | Current active counts and trainer allocation | Snapshot used as history | Current projection plus immutable lifecycle history |
| Hidden lead tab | GHL/worksheet import | Supporting lead reporting | Hidden calculation dependency | Accepted lead event ledger |
| Hidden paid-ads tab | Manual/platform data | Ad metrics | Unclear authority and refresh | Platform spend event or controlled input |
| Weekly cash components | Manual amounts/formulas | Total and recurring cash | No event-level settlement lineage | Payment and manual cash events |
| PT weekly hours/sessions | GHL-derived weekly values | CEO PT cards | No identified appointment drill-down | PT appointment event ledger |
| `Consultant Performance` | Manual staff evaluation | Performance review | Subjective assessment mixed near funnel data | Separate manual coaching-assessment event |

## Compatibility Readers to Retain During Parallel Run

| Reader | Current purpose | Retirement condition |
|---|---|---|
| `operating_data_hub/kpi_adapter.py` | Imports fixed KPI cells and active rosters | Every consumed metric has a V2 Accepted replacement and rollback window has ended |
| `scripts/update_metrics.py` | Writes workspace current-data outputs | Consumers read the accepted CEO scorecard contract |
| `scripts/insert_formulas.py` | Backfills weekly formulas | Current workbook is frozen read-only |
| `scripts/patch_booking_rows.py` | Repairs worksheet lead/booking/cash formulas | Equivalent V2 metrics are accepted |
| Appointments column K reader | Legacy attendance comparison | Strength Assessment V2 passes attendance cutover |

These readers may continue operating. New metrics must not be added to them.

## Controlled Manual Inputs

| Input type | Why manual input may remain | Required evidence | Submitter | Approver | Metric use |
|---|---|---|---|---|---|
| `bank_cash` | Cash received outside an accepted processor feed | Bank statement line or transaction reference | Admin | Peter or nominated finance approver | Cash after acceptance |
| `legacy_processor_cash` | Historical settlement unavailable from API | Processor export and reconciliation note | Admin | Peter or finance approver | Historical cash with confidence |
| `ad_spend_manual` | Platform API unavailable or incomplete | Platform statement/export | Marketing/Admin | Peter | Ad spend after acceptance |
| `trainer_capacity_window` | Contracted/available hours are an operating decision | Approved roster or contract reference | Admin/Operations | Peter | PT utilisation denominator |
| `trainer_capacity_exception` | Leave, public holiday or temporary availability | Leave/roster reference | Admin/Operations | Peter or delegated operations owner | PT utilisation denominator |
| `metric_target` | Budget, million-dollar target or service goal | Approved plan/version | Peter | Independent acknowledgement where required | Target comparison only |
| `identity_decision` | Ambiguous historical person match | Exact conflicting source references | Admin/Data reviewer | Peter or data owner | Identity linkage |
| `historical_event_correction` | Legacy row has provable error | Source documents and affected event | Admin/Data reviewer | Peter | Superseding historical event |
| `lifecycle_exception` | Approved hold/future-start/notice evidence missing from source | Approved request or contract | Admin | Peter | Lifecycle after acceptance |
| `commercial_mapping` | One-time invoice needs beneficiary/service mapping | Invoice, purchaser, beneficiary and service evidence | Admin/Finance | Peter | Entitlement/payment allocation |
| `consultant_quality_review` | Human performance evaluation | Reviewed assessment reference | Sales lead | Peter | Performance only, never funnel conversion |

## Manual-Input Controls Implemented in Shadow

- Every input receives an immutable ID and payload hash.
- The effective date, value, unit, source reference, reason and submitter are required.
- A new input begins as `pending` and is not available to metrics.
- The submitter cannot approve their own input.
- Acceptance or rejection records approver, time and reason.
- A correction supersedes a prior input; it does not silently overwrite it.
- No Google Sheet edit writes directly into a metric result.

## Source Freshness Baseline

| Source | Existing maximum age | V2 direction |
|---|---:|---|
| Google KPI compatibility snapshot | 14 hours | Comparison only |
| GHL membership and attendance | 14 hours | Event source |
| Stripe commercial evidence | 14 hours | Event source |
| PT Minder authenticated capture | 192 hours | Manual authenticated ingestion |
| Trainerize performance | 14 hours | Engagement/outcomes event source |
| PT booking continuity | 192 hours | Compatibility until appointment bridge |
| Revenue control | 96 hours | Compatibility until payment ledger |

Each metric definition must name the sources it requires. A fresh unrelated source cannot hide a stale required source.

## Timezone Correction

The current workbook is configured for `Australia/Sydney`. Reporting V2 stores every source timestamp in UTC and derives reporting dates using `Australia/Brisbane`.

The original source timestamp and workbook value remain preserved during migration. No historical row is silently shifted without a reconciliation record.
