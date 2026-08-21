# Reporting V2 Metric-by-Metric Cutover

**Status:** Cutover controls deployed; metric promotions pending evidence  
**Date:** 2 August 2026  
**Owner:** Peter Brown  
**Implementation surface:** Railway Operating Data Hub and protected Reporting V2 CEO dashboard

## Objective

Move the accepted CEO dashboard to Reporting V2 one metric at a time without
changing the KPI workbook or granting publication authority to an unaccepted
metric.

The cutover keeps cash and the rolling goal first, preserves the five-pillar
CEO structure and completed-period controls, and retains useful V1 delivery
markers with explicit current-snapshot or current-week labels until governed
V2 replacements pass.

## Safety boundary

- Railway remains the only scheduler.
- The Hub remains the metric and publication-state authority.
- Reporting V2 and the future compact Google board pack are presentation
  surfaces.
- The KPI workbook remains unchanged and authoritative for every legacy
  metric that has not completed cutover.
- Missing, stale, low-confidence or unresolved evidence remains unavailable.
- A definition, comparison result or passing test cannot grant owner authority.
- Cutover and rollback decisions are immutable audit events.

## Metric gate

A metric is eligible for owner approval only when all of the following pass:

1. the exact metric definition version exists and remains immutable;
2. the latest selected-period observation has a value and verified or high
   confidence;
3. every required source satisfies the metric definition freshness contract;
4. at least two distinct clean comparison cycles exist;
5. each required period in those cycles has zero unexplained events and zero
   unexplained cents;
6. every variance is an exact match, timing difference, legacy defect or
   approved definition change;
7. Build 4 records technical acceptance for the exact metric and definition;
8. Peter records explicit metric-level publication approval.

The first seven gates produce `eligible_for_owner_approval`. Only gate eight
produces `v2_accepted`.

## Publication states

| State | CEO behaviour |
|---|---|
| `legacy` | Use the accepted V1 marker and label its period semantics |
| `shadow` | Show the V2 result as comparison evidence, not an accepted KPI |
| `eligible_for_owner_approval` | Show the result with the exact approval still required |
| `v2_accepted` | Use the accepted V2 result for this metric only |
| `unavailable` | Show the missing evidence or failed-gate reason |
| `rolled_back` | Restore the accepted V1 fallback or show unavailable if no valid fallback exists |

## Rollback

Rollback is metric-specific and must not change other accepted V2 metrics.
Peter or an explicitly delegated owner records a rollback reason and the last
known safe fallback. The Hub appends the decision, immediately removes V2
publication authority for that metric and preserves the prior decision history.

Automatic fail-closed behaviour is separate from an owner rollback. A stale or
invalid accepted metric becomes unavailable on the CEO surface without
destroying its accepted history.

## Implementation

1. Add an immutable publication-decision event contract to Reporting V2.
2. Add a gate evaluator that joins definitions, observations, Build 4
   acceptance/parity records and the latest owner decision.
3. Make the scorecard expose effective metric publication state, exact failed
   gates, V1 fallback availability and rollback readiness.
4. Add protected read and decision endpoints. Decision writes require the exact
   definition version, owner identity, reason and explicit approval or rollback
   action.
5. Update the CEO surface to distinguish accepted, eligible, shadow, legacy and
   unavailable measures in plain English.
6. Preserve current V1 cash, service, PT, notice-period and member-outcome
   markers until equivalent V2 metrics pass.
7. Verify period toggles, ratios, missing-data behaviour, rollback isolation,
   immutable history and no KPI workbook writes.
8. Run production read-only verification after deployment authority and owner
   acceptance exist. Do not simulate a production promotion.

## Current evidence

Final combined Railway deployment
`38c0d667-b23c-4bae-865f-fecc33e1a184` is healthy in shadow mode. The combined
local suite passes 442 tests and the instruction-drift check passes.

Build 4 reports rolling cash at two technical cycles, Xero at one of two until
the 18:24 Brisbane observation, final Marketing definitions at zero of two
until the bounded 3 August observations, Strength Assessment conversion at one
clean cycle and Strength Assessment show rate blocked by 18 unresolved events.
The SGPT, Evolved Standards and four consumer contracts also require their
exact scheduled cycles and acceptance records. No metric has Peter's exact-rule
authority or publication authority.

Therefore the cutover infrastructure and presentation are complete, but every
metric remains legacy, shadow or unavailable until its remaining evidence and
owner gates are supplied.
