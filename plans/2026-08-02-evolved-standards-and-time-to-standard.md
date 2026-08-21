# Evolved Standards and Time-to-Standard

**Status:** Complete in shadow; technically ready for owner acceptance  
**Date:** 2 August 2026  
**Owner:** Peter Brown  
**Implementation:** Operating Data Hub and Trainerize Performance  
**Mode:** Read-only shadow

## Problem and business value

The Reporting V2 delivery pillar separates strength performance rankings and
workout milestones, but it cannot yet report Evolved Standards. Trainerize
contains assessment and performance evidence; it must not become the authority
for aliases, evidence sufficiency, classifications, confidence or reporting.

This build adds an auditable Hub-owned standards layer that:

- preserves every raw Trainerize exercise observation;
- normalises only owner-approved canonical aliases;
- scores component results against the Evolved Manual;
- withholds a result when side, duration, load, bodyweight or exercise identity
  is missing or ambiguous;
- identifies component standards being approached and newly achieved;
- measures time from the effective membership start to first component
  achievement;
- keeps Evolved Standards separate from strength rankings and workout-count
  milestones.

## Canonical rules exhausted

The source hierarchy is:

1. `reference/evolved-manual/03-strength-standards.md`;
2. `reference/evolved-manual/03b-standards-framework.md`;
3. `outputs/systems/strength-assessment-sop.md`;
4. the historical extraction and longitudinal audit decisions.

The primary assessment has four scored components:

- ATG Split Squat right;
- ATG Split Squat left;
- Farmer Walk for a verified 60 seconds;
- spinal control progression: High Plank, Side Plank, Strict Toes to Bar.

The individual assessment view continues to use the four directly assessed
components. The overall score layer also recognises the framework's exact
Deadlift, Push Up and distance-bearing Running or Rowing evidence, but it
remains unavailable unless those results and the four-test evidence together
form all six sufficient primary standards in one assessment.

The manual defines the overall view as the six-standard Future-Proofing Score.
It does not define, and this build does not invent, one overall Live, Long or
Perform member label. Those levels remain the highest fully attained result
for each individual standard.

## Options considered

### Classify inside Trainerize Performance

Rejected. Trainerize owns evidence, not Evolved definitions or reporting.

### Infer an overall Live, Long or Perform member level

Rejected. The canonical overall view is the Future-Proofing Score and band.
Turning even complete evidence into a separate overall level would create a
business rule absent from the manual.

### Publish raw evidence and classify in the Hub

Selected. This preserves authority boundaries, makes ambiguity explainable and
supports future rule changes without re-extracting source evidence.

## Selected design

Trainerize Performance extends its existing Railway refresh and report:

- assessment evidence is read from the protected assessment SQLite database;
- raw exercise name, side, target, load, reps, duration, bodyweight and source
  record identity are published to the existing protected Hub snapshot;
- no source-side level or overall classification is emitted.

The Operating Data Hub:

- owns the alias registry and versioned thresholds;
- links Trainerize user IDs to canonical people through the accepted
  membership-reconciliation source IDs;
- resolves effective membership start from the matching GHL membership or PT
  agreement sale, never from first workout or Trainerize account creation;
- calculates one evidence-sufficiency result per component and assessment;
- records the highest fully attained component level only;
- marks incomplete, ambiguous, legacy-combined-side and unsupported evidence
  unavailable;
- emits component-level approaching, newly achieved and time-to-standard views;
- calculates the Future-Proofing Score only when all six primary standards are
  sufficiently evidenced in the same assessment;
- preserves stronger-side evidence but scores paired ATG Split Squat at the
  highest level fully attained by both sides, equivalent to the lower
  sufficient side level;
- emits only the canonical 0–18 score and interpretation band, never an
  overall Live, Long or Perform label.

## Authority matrix impact

| Concern | Authority |
|---|---|
| Exercise observation and assessment result | Trainerize |
| Person identity and source-ID linkage | Operating Data Hub |
| Effective membership start | GHL agreement sale accepted by the Hub |
| Alias normalisation | Operating Data Hub governed standards rule |
| Threshold and component classification | Operating Data Hub, sourced from Evolved Manual |
| Confidence, sufficiency and reporting | Operating Data Hub |
| Schedule | Railway |

## Contract changes

The existing `trainerize_performance` summary remains backward-compatible and
adds:

- `standardsEvidenceSchemaVersion`;
- `standardsEvidence`;
- `standardsEvidenceCoverage`.

The Hub adds one dedicated standards projection. It does not change the current
accepted dashboard, KPI workbook, Reporting V2 metric definitions or
publication gates. The projection consumes Build 4's latest
`evolved_standards` acceptance record and exposes its immutable record ID,
`acceptance_fingerprint`, technical state and owner state; all evaluation and
promotion authority remain in `MetricAcceptanceController`.
The aligned controller rule is
`evolved-standards-future-proofing-score-v1`, policy fingerprint
`083c35c3b054dae1e8897523c42364d06933cf1b5c531faf43a367d24b80e988`.

## Privacy and failure behaviour

- Raw evidence and source IDs remain in the protected Hub snapshot.
- Public and executive output exposes only the minimum named internal action
  view already permitted by the authenticated dashboard.
- A missing bodyweight blocks loaded bodyweight-relative classification.
- A missing verified duration blocks Farmer Walk classification.
- A missing side blocks right/left split-squat classification.
- A legacy combined split-squat result cannot classify either side.
- A Future-Proofing Score is unavailable unless Deadlift, paired ATG Split
  Squat, DB Farmer Walk, Core, Running or Rowing, and Push Ups are all
  sufficient in the same assessment.
- Deadlift needs verified 1RM evidence; Push Ups need explicit chest-to-ground
  evidence; work capacity needs an exact distance-bearing run or row alias and
  duration.
- Exercise aliases are exact after punctuation and case normalisation; fuzzy
  matches remain unresolved.
- Stale or incomplete Trainerize evidence makes the standards projection
  unavailable.
- No member message or source-system write is created.

## Migration and shadow-parity plan

1. Add the raw evidence contract without removing existing summary fields.
2. Unit-test exact aliases, thresholds, ambiguity and insufficiency.
3. Unit-test effective-start resolution and component transition clocks.
4. Render results only in the protected Reporting V2 preview.
5. Deploy both Railway services through their existing deployment paths.
6. Verify health, source freshness, evidence coverage and responsive rendering.
7. Keep accepted reporting unchanged until metric-level comparison and owner
   acceptance pass.

## Acceptance gates

- Existing Trainerize strength-improvement and workout-milestone tests pass.
- Performance rankings, workout milestones and standards are separate fields
  and widgets.
- Exact component evidence is traceable to its raw source observation.
- Partial or ambiguous evidence never yields a component or overall level.
- Bodyweight-relative thresholds use bodyweight near the assessment with its
  timing quality retained.
- Right and left split squat are independent.
- Approaching means a complete, below-threshold result within the documented
  threshold margin; missing evidence is not approaching.
- Newly achieved requires a prior sufficient lower result and a later
  sufficient higher result.
- Time-to-standard starts at the effective GHL agreement date and is unavailable
  when identity or start evidence is unresolved.
- Live, Long and Perform remain per-standard results.
- The 0–18 Future-Proofing Score uses Below Live 0, Live 1, Long 2 and Perform
  3 across all six required standards and publishes no partial score.
- Score bands are exactly 0–5, 6–9, 10–13, 14–17 and 18 as defined by Section
  03b and the Member Care course.
- Railway is the only scheduler.
- The accepted CEO dashboard and KPI workbook are unchanged.

## Legacy component and retirement

The existing `standardsMilestones` placeholder and “Definition required”
widget are replaced by the governed shadow projection. No accepted report is
retired in this build. The compatibility path is removed only after standards
acceptance and dashboard cutover.

## Review

No further overall-label decision is required. Review only narrower source
evidence gaps that prevent one of the six canonical standard results from
being sufficient.

## Implementation result

The rule-independent layer is complete:

- the existing Trainerize refresh captures recent Strength Assessment exercise
  rows and nearby bodyweight evidence without a new schedule;
- the existing protected Hub summary remains backward-compatible and carries
  raw evidence rather than source-side classifications;
- `operating_data_hub/evolved_standards.py` owns exact aliases, component
  results, insufficiency reasons, confidence, approaching and newly achieved
  transitions, identity resolution, component time-to-standard and the
  complete-only Future-Proofing Score;
- the protected local evidence sample checked 152 active accounts, 90 members
  with 92 assessments and 1,207 observations;
- 74 spinal-control results were sufficiently recorded;
- 92 Farmer Walk records were withheld because duration was not recorded;
- historical split-squat results were withheld because right and left were
  combined;
- the first live producer observation exposed the legacy two-column assessment
  bundle schema and correctly reported standards coverage unavailable;
- the refresh now migrates that legacy table in place, preserves its historical
  dates as `legacy_date_only`, creates the full raw-evidence tables, and future
  recovery bundles carry the full evidence schema;
- 320 combined Hub, reporting-control and Trainerize tests pass, including the
  controller rule and fingerprint compatibility coverage.

Trainerize Performance deployment
`87cb52d8-ba8d-4b43-93aa-69c469f97d83` proved the contract, health, read-only
mode and Railway-only scheduling. A follow-up producer deployment is required
for the legacy-schema bootstrap fix. Corrected Trainerize deployment
`6ca674ba-77a1-4d62-a012-3880ec584b68` and read-only run
`trainerize-performance-20260802T004449+0000` completed with 39 assessments,
507 raw exercise observations and 38 active members with assessment evidence.
SGPT/Reporting Hub archive deployment
`e737a3db-a81c-40d8-a962-d107e0801a0b` is healthy and stored snapshot
`20260802T004851Z-02d9175d`. It predates Build 2's final lifecycle contract
hunks and is not the ultimate combined Hub deployment.

The second distinct scheduled producer run,
`trainerize-performance-20260802T191754+0000`, completed with the same complete
standards coverage: 39 assessments, 507 raw observations and 38 members with
assessment evidence. The coordinated combined Hub deployment
`564d33e0-17d5-41b6-8746-36a3be7cf712` is healthy in shadow mode with Railway
scheduling enabled, 20 sources and zero stale sources. Production acceptance
record `693fd91cedeb5501ac942f3532086121` binds both post-migration run IDs to
the canonical rule and passed its deterministic sample at 20/20 exact with
zero unexplained mismatches. Protected readback reports 2/2 scheduled cycles,
all technical gates passed and effective state
`eligible_for_owner_approval`. Owner approval remains pending, promotion is
disabled, accepted metric count remains zero, and the accepted dashboard and
KPI workbook remain unchanged. No accepted report, source system or workflow
changed.
