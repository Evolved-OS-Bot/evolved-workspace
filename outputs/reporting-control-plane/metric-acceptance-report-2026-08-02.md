# Reporting metric acceptance report — 2 August 2026

## Outcome

The acceptance controller is complete and remains fail-closed. It records
technical evidence separately from Peter's exact-rule approval and separately
again from publication. No record produced by this controller can publish a
metric, change the accepted CEO dashboard or alter the KPI workbook.

No metric in this review is ready for an owner cutover decision today:

- Marketing is waiting for its first two scheduled observations under the
  final website and subscriber definitions.
- Strength Assessment conversion has one clean comparison cycle, not two.
- Strength Assessment show rate is blocked by 18 unresolved events in its
  first comparison. Scheduled or absent evidence will not be converted into
  attendance or no-show.
- Rolling cash has two scheduled refreshes, but its aggregate-only exact
  processor-event sample and second comparison are still required.
- Xero has one of two scheduled observations. The second bounded observation
  is due at 18:24 Brisbane on 2 August.
- The four downstream consumer contracts have their exact acceptance policies
  registered and remain shadow until two distinct comparisons arrive.
- Evolved Standards' first producer observation exposed the legacy two-column
  assessment bundle and correctly failed closed. It counts as an insufficiency
  case, not as either of the two required complete post-migration observations.

The metric-level readiness records are in
`outputs/reporting-control-plane/metric-acceptance-readiness-2026-08-02.json`.

### Evolved Standards compatibility update, 3 August

Peter has resolved the canonical overall-view rule. There is no overall Live,
Long or Perform member label. Individual standard levels remain visible, and
the only overall view is the complete six-standard Future-Proofing Score from
0 to 18 plus its defined interpretation band.

The standards acceptance policy is now versioned
`evolved-standards-future-proofing-score-v1`, with policy fingerprint
`083c35c3b054dae1e8897523c42364d06933cf1b5c531faf43a367d24b80e988`.
It requires all six standard results to be sufficiently evidenced. Split Squat
uses the highest integer level fully attained by both independently sufficient
sides, so the weaker side governs, while asymmetry remains separate.

The producer retains classification ownership. Acceptance requires evidence
that exact source-sufficiency rules were applied: Deadlift needs an exact alias,
bodyweight, load and verified one-repetition maximum; Push Ups need an exact
full Push Up alias, repetitions and explicit chest-to-ground depth; running or
rowing needs an exact distance-bearing alias and duration. Generic names,
multi-repetition Deadlift sets, unspecified Push Up depth and unitless generic
distance remain insufficient. Missing or ambiguous evidence fails closed.

This compatibility change invalidates the obsolete
`overall_requires_owner_decision` guard but does not promote the metric. The
accepted dashboard and KPI workbook remain unchanged.

The bounded production acceptance completed on 3 August using the two genuine
post-migration runs
`trainerize-performance-20260802T004449+0000` and
`trainerize-performance-20260802T191754+0000`. A deterministic protected
20-person sample produced 20 exact Hub identity matches and zero unexplained
mismatches. Both distinct cycles covered all six required acceptance periods
with fresh, complete source evidence and zero unexplained events or cents.

Production record
`693fd91cedeb5501ac942f3532086121`, fingerprint
`8a2f5b6d4640e677a8fec9dd71581cb99a6d0ff40f5cd9cb5e1e2b7f86df573d`,
read back as `ready_for_owner_acceptance`, technical gates passed, 2/2 cycles,
owner approval pending, publication shadow and promotion disabled.

## Evidence checked

The read-only production check found:

- four exact scheduled GHL acquisition cycles and four Strength Assessment
  attendance cycles;
- two exact rolling-cash cycles;
- one exact Xero accounting cycle;
- no scheduled website-analytics cycle under the final deployed definition
  yet;
- one parallel comparison cycle per populated Reporting V2 metric;
- zero unexplained events and cents for the Strength Assessment conversion
  comparison;
- 18 unexplained events for `sa_show_rate / sa-attendance-v2`.

The completed-week accounting comparison remains explainable bookkeeping
timing: `$9,802.37` of collected cash excluding GST versus `$2,120.55` of Xero
income and `$7,280.57` of operating expenses. Xero income is validation
evidence only and cannot become cash.

## Controller contract

`operating_data_hub.acceptance_controller.MetricAcceptanceController` stores
immutable records in `hub_metric_acceptance_evidence`. Each latest record
includes:

- metric ID, definition version and gate version;
- technical state and a separate owner-approval state/reference;
- required and completed scheduled cycles;
- freshness, aggregate-only identity sample, period comparison and domain
  guard results;
- zero-unexplained event and cents totals;
- bounded `observation_not_before`;
- shadow publication state, `promotion_authorised=false`, and a deterministic
  `acceptance_fingerprint`.

Two distinct `comparison_cycle_id` and `source_run_id` pairs must cover every
required period. Consumer cutovers additionally require equal legacy/Hub
identity fingerprints, equal classification fingerprints, zero set
differences, fresh complete Hub sources and protected legacy fallback.

## Plain-English owner recommendations

There is no material owner decision to request yet. When a metric first
becomes technically clean, present only that exact metric ID, definition
version, acceptance fingerprint and rule reference to Peter.

Recommended order once the bounded evidence arrives:

1. Review Xero operating expenses after the 18:24 observation. Keep Xero
   income validation-only.
2. Review Strength Assessment conversion after a second clean comparison.
   Do not accept show rate while unresolved outcomes remain.
3. Review Marketing after the 06:02 and 06:18 observations on 3 August and
   the aggregate-only identity samples pass.
4. Review rolling cash only after exact processor-event sampling passes.
5. Review each downstream consumer contract independently; never batch their
   owner authority.

`hub-workflow-extension-v1` remains downstream of acceptance. Shadow or
unaccepted metrics may create preview records only. Only accepted, complete,
fresh, evidence-backed decisions under an accepted policy may queue an
`internal_task`; this introduces no public publication or source-system write.
