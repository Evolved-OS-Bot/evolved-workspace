# Trainerize Longitudinal Strength Audit

**Created:** 21 July 2026  
**Status:** Complete

## Objective

Determine how completely Trainerize can describe member strength change at approximately 6, 12 and 24 months and beyond, then extract the most complete defensible historical dataset available.

## Guardrails

- Begin with read-only API discovery.
- Store identified records only under `data/private/`.
- Do not print member identities during normal runs.
- Log every Trainerize account-status change with its original state.
- Temporarily reactivate only the former members required for otherwise inaccessible workout detail.
- Use Basic access for temporary reactivation.
- Restore every temporarily reactivated account to its original deactivated state after extraction and verify the final roster.
- Preserve raw source responses and document all cleaning and exercise mappings.
- Do not describe active-only survivor data as outcomes for all members.
- Obtain member consent before any identifiable remarkable-result story is used publicly.

## Audit layers

1. Client roster, profile creation and current status
2. Calendar and completed-workout coverage
3. Detailed exercise results and recording conventions
4. Body-weight observations
5. Programs, accomplishments, goals and habits where available
6. Formal Strength Assessment linkage
7. Comparable movement and exercise trajectories
8. Training exposure and consistency
9. Coverage near 6-, 12- and 24-month windows
10. Standards transitions and remarkable-result candidates

## Outputs

- Private SQLite audit database
- Private identified working workbook if useful for review
- De-identified audit workbook and written findings
- Exercise mapping and data-quality register
- Former-member access and restoration log
- Recommendation on what can be claimed retrospectively and what must begin prospectively

## Expanded former-member pass, 22 July 2026

- Prioritised 46 deactivated accounts with at least 120 days of tracked workout history and no detailed results in the first extract.
- Temporarily reactivated each account as Basic, recovered 3,130 workouts and 79,050 exercise-result rows, then returned every account to Deactivated.
- Increased detailed-account coverage from 235 to 281 and deactivated-account coverage from 71 to 117.
- Increased paired movement-horizon observations from 794 to 898 and remarkable-result candidates from 102 to 113.
- Verified the account-change ledger contains zero unrestored changes.

## Movement-family and marketing pass, 22 July 2026

- Restricted women's outcome analysis to 529 accounts explicitly recorded as female; retained 44 male, other or missing-sex accounts only in clearly labelled all-account operational totals.
- Added an auditable movement-family map covering bilateral squat, hinge/deadlift, horizontal press, vertical pull, split squat and loaded carry exposure.
- Measured squat exercise-stage transitions separately from within-exercise load changes; cross-variant kilograms are never compared.
- After coach clarification, combined Nexus Point Squat, Barbell Front Squat and Barbell Back Squat as one canonical exercise because the latter two were unintended recording names.
- The corrected mapping identifies 22 clean observed Goblet-to-Nexus pathways and 149 broader Goblet-then-Nexus sequences; original source exercise names remain visible for audit.
- Added marketing evidence and completed-workout milestone registers: 25,186 tracked workouts, 484 women with completed training, 82 reaching 100 workouts and 17 reaching 250.
- Added recommended wording, claim status and caveats so descriptive scale facts remain separate from unvalidated transformation claims.

## Finalisation and Drive handoff, 22 July 2026

- Reconciled the workout denominator: 25,186 tracked programmed workouts belong to profiles explicitly recorded as female, while the all-account operational total is 26,304.
- Documented the 44 demographic exceptions without inference or overwriting: 34 missing, 7 male and 3 other Trainerize values, containing 1,118 programmed workouts. The owner reports these are onboarding classifications requiring verification.
- Corrected the written paired movement-horizon total to 943 and regenerated both final workbooks with zero formula errors.
- Uploaded only the de-identified workbook as a native Google Sheet to `2.Strength Assessment`, beside the frozen de-identified Strength Assessment V1 dataset.
- Kept the identified workbook and restoration ledger exclusively in the private local workspace; zero temporary account changes remain open.
