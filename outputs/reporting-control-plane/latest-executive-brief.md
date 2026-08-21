# Evolved Executive Reporting Brief

**Generated:** 2026-07-27T02:34:19+00:00
**Completed KPI period:** 20–26 Jul 2026

## Decision Metrics

| Metric | Value |
|---|---:|
| Unique active roster clients | 127 |
| SGPT service relationships | 94 |
| PT service relationships | 44 |
| Cross-service overlaps removed | 11 |
| Cash collected | $10,927.24 |
| Trainerize reassessments due or missing | 100 |

## Report Control

| Report | Runtime | Status | Age |
|---|---|---|---:|
| current-business-metrics | local-compatibility | fresh | 0.0h |
| daily-operations-brief | local-compatibility | external-not-synchronised | not synchronised |
| retention-intelligence | railway-retention-intelligence | external-not-synchronised | not synchronised |
| pt-booking-continuity | railway-pt-booking-shadow | external-not-synchronised | not synchronised |
| revenue-control | railway-pt-booking-shadow | external-not-synchronised | not synchronised |
| conversation-triage | railway-cron | external-not-synchronised | not synchronised |
| trainerize-performance | local-artifact-only | fresh | 0.7h |

## Architecture Alerts

- **High:** KPI refresh and Discord delivery still run as local compatibility processes. Railway replacements have not yet passed parity, so the Railway-only target is not complete.
- **Medium:** Performance reporting is restored as a snapshot-only consumer; automated transfer of the latest aggregate Railway reconciliation state is still pending.
- **Medium:** External Railway run state is not yet synchronised into this local share-safe brief.
- **Medium:** Revenue and PT share protected identity evidence, but Retention Intelligence has not yet migrated to the same PostgreSQL-backed control repository.
