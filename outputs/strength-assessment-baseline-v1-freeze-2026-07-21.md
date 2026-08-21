# Women's Intake Strength Baseline: V1 Freeze Record

**Frozen:** 21 July 2026  
**Facility:** The Evolved Gym, West End  
**Cohort:** Historical operational Strength Assessments  
**Status:** Retrospective discovery cohort, not a population-representative or clinical research dataset

## Core question

> How strong are women when they first come to The Evolved?

V1 contains 226 extracted assessment records and 216 eligible women with a deterministically selected first completed assessment. All records use the historical `legacy_combined_v1` assessment structure.

## Frozen baseline coverage

| Measure | Women with usable baseline data |
|---|---:|
| Eligible baseline women | 216 |
| Clean Split Squat variation and reps | 204 |
| Split Squat external load | 204 at 0 kg |
| Any recorded Farmer Walk load | 202 |
| Assessment-date body weight | 214 |
| Farmer Walk load plus same-day body weight | 200 |
| Primary High Plank result | 177 |

The historical Split Squat was bodyweight-only. A value of 0 kg is therefore recorded when a clean Split Squat result exists. The bumper plates named in the variation modify front-foot elevation; they are not external load. A blank means there is no clean baseline Split Squat result.

## Relative Farmer Walk baseline

The weight backfill uses Trainerize `/bodystats/get` for the original assessment date. Exact same-day body weight was recovered for 214 of 216 baseline women.

| Metric | Recorded women | Average | Median |
|---|---:|---:|---:|
| Best recorded Farmer Walk load | 202 | 31.7 kg | 30.0 kg |
| Body weight at assessment | 214 | 70.7 kg | 69.0 kg |
| Farmer Walk load as body weight | 200 | 45.7% | 46.9% |

Farmer Walk percentage is calculated as:

`highest recorded Farmer Walk load ÷ assessment-date body weight`

The recorded Farmer Walk load is treated as total combined load, consistent with the current Strength Assessment SOP. The percentage does not prove that the full 60-second target was achieved because historical duration completion was not reliably stored.

## Interpretation boundaries

- This is a cohort assessed at the West End facility, not a representative sample of West End or Inner Brisbane residents.
- Age at assessment is calculated privately from Trainerize birth date and assessment date. Only age bands are exported.
- Exact body weight is included in the de-identified internal analysis workbook, but birth dates, exact ages, names, contact details and source-system IDs remain private.
- Unusually low raw Farmer Walk loads are retained. They require review rather than silent deletion.
- Historical 20%, 50% and 75% template tiers remain visible and are not rescored against current standards.
- No composite strength score or clinical risk claim is produced from V1.

## Canonical files

- Private identified database source: `data/private/strength-assessments/strength_assessments.sqlite`
- Private identified workbook: `data/private/strength-assessments/Identified Strength Assessment V1 - PRIVATE.xlsx`
- De-identified analysis workbook: `outputs/strength-assessment-v1-final-2026-07-21/De-identified Strength Assessment V1 - FINAL.xlsx`
- Historical extraction plan and provenance: `plans/2026-07-20-strength-assessment-extractor.md`

The private and de-identified workbooks have matching Summary definitions for Split Squat external load, assessment-date body weight, best Farmer Walk load and Farmer Walk load as a percentage of body weight. The identified workbook also retains names, email addresses, birth dates, exact dates and Trainerize IDs for controlled internal linkage.

The workbooks dated 20 July 2026 and the earlier 21 July draft are superseded. They remain historical working files and should not be uploaded or used for V1 analysis.

V1 should now remain immutable. Corrections should create a documented derivative or a later dataset version rather than silently overwriting these final files or this freeze record.
