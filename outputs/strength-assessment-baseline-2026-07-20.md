# Women's Intake Strength Baseline

**Extracted:** 20 July 2026  
**Facility:** The Evolved Gym, West End  
**Status:** Version 1 active-client baseline

> **Recovery update, 20 July 2026:** all 242 exact email-matched roster accounts are now active. A June 2025–July 2026 extraction scanned 315 active clients, found and stored 225 assessment calendar records without API errors, and expanded the private earliest-assessment baseline from 63 to 216 women. Detailed distributions below remain the original 63-woman snapshot until the refreshed 216-woman analysis is regenerated.

> **Roster update, 20 July 2026:** the two confirmed appointment tabs contain 289 completed assessment rows and 264 unique nonblank emails. Twenty-two unmatched emails require name/mobile reconciliation. After extraction, all 149 exact-match accounts marked Offline were returned to Deactivated; the 93 remaining active exact matches retain full-access roles. The verified Excel export contains a formula-driven summary, 216 baseline rows, all 226 stored assessments and 2,954 underlying exercise-result rows.

## The question

> How strong are women when they first come to The Evolved?

Version 1 contains the earliest completed Strength Assessment for 63 women who are active Trainerize clients today. The assessments run from 5 January to 15 July 2026.

This is an intake benchmark for The Evolved's observed West End facility cohort. It is not yet a population estimate for all women who live in West End or Inner Brisbane.

## Data coverage

| Measure | Usable records | Coverage |
| --- | ---: | ---: |
| First tracked assessment | 63 | 100% |
| Any split-squat variation recorded | 60 | 95% |
| One unambiguous split-squat variation | 57 | 90% |
| Farmer Walk recorded tier/load | 58 | 92% |
| Primary plank variation/time | 56 | 89% |
| Date of birth for age analysis | 63 | 100% |

The extraction found 65 assessment records in total: 64 completed and one scheduled. One woman had a later completed assessment, which is retained for future improvement analysis but excluded from the intake baseline.

## Preliminary component baseline

### Split squat

Trainerize contains 63 populated variation entries across 60 women. Fifty-seven women have one recorded variation, three have two recorded variations and three have no populated result.

| Recorded variation | Populated entries |
| --- | ---: |
| Stool + 2 x 15kg bumper plates | 22 |
| Stool | 13 |
| Stool + 3 x 15kg bumper plates | 8 |
| Stool + 4 x 15kg bumper plates | 8 |
| Floor + 2 x 15kg bumper plates | 8 |
| Floor + 1 x 15kg bumper plate | 3 |
| Floor | 1 |

These are raw entries, not mutually exclusive women. They should not be collapsed into Live, Long or Perform until the historical progression mapping and the three two-variation records have been explicitly reviewed.

### Farmer Walk

| Legacy bodyweight target recorded | Women | Share of baseline |
| --- | ---: | ---: |
| 20% bodyweight tier | 19 | 30% |
| 50% bodyweight tier | 34 | 54% |
| 75% bodyweight tier | 5 | 8% |
| Missing | 5 | 8% |

The median recorded load among the 58 populated results is 35kg. The database preserves the recorded load and target tier, but version 1 does not calculate relative strength from the client's latest bodyweight because that weight may not be contemporaneous with the assessment.

### Plank

| Primary recorded variation | Women | Share of baseline |
| --- | ---: | ---: |
| High plank | 50 | 79% |
| Bear plank | 6 | 10% |
| Missing | 7 | 11% |

The median recorded time among the 56 populated primary plank results is 60 seconds. Two assessments also contain Side Plank data; those records remain separate rather than being mixed into the legacy primary-plank distribution.

### Age coverage

| Age at assessment | Women |
| --- | ---: |
| Under 30 | 18 |
| 30–39 | 18 |
| 40–49 | 10 |
| 50–59 | 13 |
| 60+ | 4 |

Small age cells should be suppressed or combined in any public-facing benchmark until the cohort is larger.

## Material limitations

1. **Active-client survivorship bias:** a read-only deactivated-account audit found 61 completed assessment records that Trainerize blocks from detailed retrieval with HTTP 403. These cover 59 confirmed women, one profile with sex missing and one male profile. Women who did not join or later left are therefore missing from Version 1.
2. **Legacy schema only:** all 65 available records use the older combined split-squat, 20%/50%/75% Farmer Walk and legacy plank structure. They cannot be silently rescored against the current independent-side standards.
3. **Facility cohort, not residential geography:** Trainerize and GHL do not currently contain adequate suburb or postcode coverage. The result can be described as women assessed at the West End facility, not a representative baseline for West End or Inner Brisbane residents.
4. **No arbitrary composite score:** the first release reports component distributions. A single strength score would require an approved weighting and progression map.
5. **The current workout definition is not the full assessment history:** the confirmed master roster spans `Brown & Casserly Pty Ltd 2025` > `Appointments` and the corresponding 2026 tab. The 2025 tab contains 78 rows from June–October 2025; the 2026 tab contains 211 attended rows through July 2026. Together they contain 289 rows and 264 unique nonblank emails after cross-workbook de-duplication. The Trainerize scan currently begins in January 2026 and targets the current assessment workout definition, so older assessment schemas and workout IDs remain to be discovered.

## Next actions

1. Recover the 59 confirmed female historical assessments by temporarily reactivating accounts as Offline clients in seat-safe batches, extracting them, then returning them to Deactivated. Test one account first. Offline clients receive no invitation email but consume coaching seats while active.
2. Ask Trainerize for detailed deactivated-client workout access or a historical bulk export to remove the need for this workaround.
3. Add a required residential postcode at Strength Assessment intake, with explicit reporting consent and retention rules.
4. Align the live Trainerize workout definition with the current independent-side Strength Assessment standard.
5. Approve the historical split-squat progression mapping before translating raw variations into standard levels.
6. Once the historical cohort is complete, publish age-band and intake-year benchmarks with small-cell suppression.
