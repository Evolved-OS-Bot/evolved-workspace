# Strength Assessment Extractor

**Status:** Complete
**Date:** 2026-07-20

## Objective

Build a private, repeatable dataset that answers:

> How strong are women when they first come to The Evolved?

The initial benchmark represents women who completed a Strength Assessment at The Evolved's West End facility. It is an intake benchmark for the gym's observed cohort, not a population-representative benchmark for all women living in West End or Inner Brisbane.

## Confirmed source data

- Trainerize location `434308`: The Evolved Gym.
- Dedicated program `3818898`: Strength Assessment.
- Training plan `30408052`: Strength Assessment.
- Workout definition `183960272`: Women's Standard Strength Assessment.
- Active-client assessment details expose 13 exercises and set-level reps, weight and time.
- Trainerize profiles provide birth date for nearly all active clients, but city for almost none.
- GHL contact postcode and city coverage is currently insufficient for residential catchment analysis.
- Detailed workout retrieval returns HTTP 403 for deactivated clients, although their assessment calendar records remain visible.

## Analytical definition

### Cohort

- Female clients and prospects with a tracked Strength Assessment.
- Exclude Trainerize test clients.
- Baseline is the earliest valid tracked Strength Assessment per person.
- Later assessments remain available for longitudinal improvement analysis but do not enter the intake baseline.

### Measures

- Raw exercise variation, reps, weight and time.
- Single-leg capacity progression achieved.
- Farmer's Carry load and duration, plus relative load when a valid contemporaneous body weight exists.
- Plank variation and duration.
- Assessment completion and missingness.
- Age and age band at assessment when birth date is available.

Do not create a composite strength score in version 1. Report the component distributions first so an arbitrary weighting does not obscure the real baseline.

### Versioning

Historical Trainerize records use an older assessment template:

- Split-squat results are combined rather than independently recorded right and left.
- Farmer's Carry targets use older 20%, 50% and 75% bodyweight tiers.
- Current standards use independent sides and 75%, 100% and 150% carry tiers.

The extractor must retain raw fields and assign an assessment schema version. Historical data must not be silently rescored against current standards.

## Storage and privacy

- Store raw and identified data only under Git-ignored `data/private/strength-assessments/`.
- Use SQLite as the canonical local store.
- Keep client identity separate from exercise and aggregate analysis tables through stable Trainerize IDs.
- Do not print names, emails or individual results during normal runs.
- Produce aggregate outputs only when the cohort size is adequate; suppress cells smaller than five in future reporting.

## Implementation

1. Add the Trainerize location ID to private environment configuration and the non-secret environment template.
2. Extend the reusable Trainerize client with explicit location-level client listing and safe pagination.
3. Build `scripts/extract_strength_assessments.py` with:
   - active-client discovery;
   - batched profile retrieval;
   - year-chunked calendar retrieval;
   - Strength Assessment identification;
   - batched detailed workout retrieval;
   - raw exercise/stat normalization;
   - SQLite upserts and extraction error logging;
   - baseline and data-quality summary output.
4. Add unit tests for assessment identification, null statistics, first-assessment selection and schema version handling.
5. Run the extractor against active clients and validate totals without printing personal data.
6. Document the extractor and data limitations in `CLAUDE.md`, `scripts/SETUP.md` and the roadmap.

## Phase 2 dependencies

- Ask Trainerize to permit detailed historical workout reads for deactivated clients or provide a bulk export.
- Add a minimal postcode field to the assessment intake if residential West End and Inner Brisbane segmentation is required.
- Define and implement the current assessment schema in Trainerize so independent right/left and current standards are recorded consistently.
- Add GHL enrichment only after the raw Trainerize extraction is stable and reconciled against controlled assessment records.

## Success criteria

- A repeatable command creates or updates the private SQLite database.
- Every stored assessment is traceable to its source workout and extraction run.
- The earliest tracked assessment per woman is deterministically identifiable.
- Historical and current assessment schemas cannot be mixed silently.
- Errors and inaccessible deactivated records are counted and reported.
- No credential or client-identifying data is added to Git.

## Completion record

Completed 20 July 2026.

- Unit tests: 7 passing.
- Full active-location scan: 164 clients.
- Assessment records: 65 total, 64 tracked and 1 scheduled.
- Valid female first-assessment baseline: 63 women, dated 5 January to 15 July 2026.
- Schema classification: 65 legacy records, no current-schema records found.
- Exercise coverage among the baseline: a split-squat result exists for 60/63 women, with 57 single-variation and 3 ambiguous two-variation records; Farmer Walk 58/63; primary plank 56/63.
- Extraction errors: 0.
- Identified storage: Git-ignored `data/private/strength-assessments/strength_assessments.sqlite`.
- Aggregate findings and limitations: `outputs/strength-assessment-baseline-2026-07-20.md`.

Historical completeness remains a Phase 2 dependency because Trainerize returns HTTP 403 for detailed workouts belonging to deactivated clients. A follow-up calendar audit identified 61 completed blocked records: 59 confirmed women, one sex-missing profile and one male. The approved candidate workaround is temporary Offline reactivation in seat-safe batches, beginning with one controlled account; Offline clients receive no invitation email but consume coaching seats. Residential geography also remains unavailable because postcode and suburb capture is insufficient.

## V1 body-weight revision

Completed 21 July 2026.

- Added a private `assessment_body_weights` table tied to each tracked assessment.
- Added exact-date retrieval through Trainerize `/bodystats/get`, with the measurement date, day offset, source, selection method and timing-quality label retained.
- Exact same-day body weight was recovered for 214 of the 216 baseline women; two remain unavailable.
- Of 202 baseline women with a Farmer Walk load, 200 now have a same-day body weight and a formula-driven relative load.
- Added `Split Squat External Load (kg)` as 0 kg for 204 clean historical bodyweight-only results. A blank continues to mean no clean baseline result.
- Farmer Walk percentage is calculated as the highest recorded carry load divided by assessment-date body weight. The load is treated as total combined load, consistent with the current SOP.
- Raw unusually low loads remain visible and are not silently removed.
- Revised de-identified workbook: `outputs/strength-assessment-extractor-2026-07-21/evolved-strength-assessment-deidentified-v1-2026-07-21.xlsx`.
