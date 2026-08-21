# Plan: Reconcile the Trainer Portal With GoHighLevel

**Created:** 2026-07-24
**Status:** Completed
**Request:** Audit the complete trainer course, align every workspace derivative, update the live GoHighLevel courses and quizzes, and install the practical sign-off pathway.

---

## Overview

### What This Plan Accomplishes

This plan reconciles the Evolved Manual, operational SOPs, trainer-course Markdown, paste-ready HTML, quiz CSVs and the live GoHighLevel course catalogue. It also adds the missing Course 13 Practical Sign-Off and makes Course 14 Congratulations conditional on approved practical competency.

### Why This Matters

Trainer readiness is the rate-limiting control for timetable expansion. Theory-only certification creates a coaching-quality and member-safety risk, while stale course instructions create inconsistent delivery.

---

## Current State

### Relevant Existing Structure

- `reference/evolved-manual/`: master coaching framework
- `reference/sops/`: operational source procedures
- `outputs/trainer-portal/*.md`: canonical trainer course copy and assessments
- `outputs/trainer-portal/html/`: paste-ready GHL lesson content
- `outputs/trainer-portal/quiz-csvs/`: native GHL assessment imports
- GHL Memberships before implementation: 13 live products, Courses 1–12 plus an unnumbered Congratulations product
- GHL Automations before implementation: the access chain certified after Course 12

### Gaps or Problems Being Addressed

- Course 13 Practical Sign-Off did not exist in GHL
- Congratulations was not numbered as Course 14
- Course 1 lacked the July injury and health-condition protocol
- Course 8 required reconciliation of the program-expectations lesson
- Course 10 required lesson and quiz reconciliation
- Course 10 and Course 11 live quizzes were missing their newest questions
- Course 9 contained a source conflict. This was resolved on 2026-07-24: Goblet Squat now progresses directly to Nexus Point Squat throughout the current course and manual sources.
- The old build guide described nine courses and a superseded assignment model

---

## Proposed Changes

### Summary of Changes

- Validate and synchronise all local course derivatives
- Resolve the Course 9 squat-progression conflict with the owner
- Update all affected live course lessons and quizzes
- Create Course 13 with one overview lesson and ten native practical assignments
- Renumber Congratulations as Course 14
- Replace the theory-only certification handoff with an approved-practical-completion gate
- Verify titles, lesson counts, assessment counts, publication state and workflow order

### New Files to Create

| File Path | Purpose |
|---|---|
| `scripts/audit_trainer_portal.py` | Checks Markdown, HTML, quiz CSV and Practical Sign-Off consistency |
| `scripts/sync_trainer_portal_derivatives.py` | Regenerates quiz CSVs and HTML quiz blocks from canonical Markdown |
| `plans/2026-07-24-trainer-portal-ghl-reconciliation.md` | Records implementation and validation criteria |

### Files to Modify

| File Path | Changes |
|---|---|
| `outputs/trainer-portal/00-build-guide.md` | Replace the obsolete nine-course model with the 14-course pathway |
| `outputs/trainer-portal/01-welcome-and-standards.md` | Add the injury protocol, correct the pathway and audit the quiz |
| `outputs/trainer-portal/html/01-welcome-and-standards.html` | Cascade Course 1 changes |
| `outputs/trainer-portal/05-evolved-pilates.md` | Correct the assessment count to nine |
| `outputs/trainer-portal/11-member-care.md` | Correct the assessment count to twelve |
| `outputs/trainer-portal/quiz-csvs/*.csv` | Regenerate from canonical Markdown |
| `outputs/trainer-portal/html/*.html` | Regenerate quiz blocks from canonical Markdown |
| `outputs/trainer-portal/13-practical-sign-off.md` | Canonical Course 13 practical assessment |
| `outputs/trainer-portal/14-congratulations.md` | Renumber the final course and change its prerequisite |
| `context/roadmap.md` | Record completion and the final live pathway |
| `CLAUDE.md` | Document the portal audit and synchronisation scripts |

### Files to Delete

No content is deleted. The former Course 13 Congratulations files are renamed to Course 14, and the unnumbered Practical Sign-Off files are renamed to Course 13.

---

## Design Decisions

### Key Decisions Made

1. **Markdown remains the canonical course derivative:** HTML and quiz CSVs are generated from it after the manual and SOP sources are reconciled.
2. **Practical competency is centralised in Course 13:** Ten native GHL assignments provide explicit evidence and management approval.
3. **Course 14 is an outcome, not an assessment:** It is released only after all practical assignments are approved.
4. **Existing learner access is preserved:** Live courses are edited in place rather than duplicated.

### Alternatives Considered

Per-course assignments were rejected because the current roadmap defines one consolidated practical course. A single upload-only assignment was rejected because it would not give management block-level visibility.

### Open Questions

- Resolved 2026-07-24: Goblet Squat progresses directly to Nexus Point Squat.
- Resolved 2026-07-24: Course 13 will use one overview lesson plus ten native assignments approved by Megan.

---

## Step-by-Step Tasks

### Step 1: Audit Workspace Integrity

**Actions:**

- Map every course to its manual and SOP sources
- Compare Markdown, HTML and quiz CSV question sets
- Validate counts, correct answers and Practical Sign-Off blocks
- Run HTML validation

**Files affected:**

- `scripts/audit_trainer_portal.py`
- `scripts/sync_trainer_portal_derivatives.py`

### Step 2: Correct Workspace Drift

**Actions:**

- Add the missing Course 1 injury protocol and comprehension question
- Correct stale question counts
- Regenerate every quiz CSV and HTML quiz block
- Renumber Practical Sign-Off and Congratulations
- Replace the obsolete build guide

**Files affected:**

- `outputs/trainer-portal/`

### Step 3: Map the Live GHL Catalogue

**Actions:**

- Record all live product IDs
- Record every lesson and quiz
- Confirm assessment counts, pass marks, publication state and missing content
- Inspect native assignment features

**Files affected:**

- None

### Step 4: Update Live Theory Courses

**Actions:**

- Update Course 1 lessons and quiz
- Add the missing Course 8 lesson
- Resolve and apply the Course 9 progression rule
- Replace Course 10 lesson content and update its quiz
- Add the missing Course 11 question
- Verify unaffected courses against the audit

**Files affected:**

- GHL Courses 1–12

### Step 5: Install Practical Sign-Off

**Actions:**

- Create and publish Course 13
- Add the overview lesson and ten native practical assignments
- Require management approval for each block
- Require evidence and a written reflection for Block 10

**Files affected:**

- GHL Course 13

### Step 6: Repair the Completion Path

**Actions:**

- Rename Congratulations as Course 14
- Grant Course 13 after Course 12
- Grant Course 14 and issue the credential only after approved practical completion

**Files affected:**

- GHL Course 14
- GHL course-access and credential workflows

### Step 7: Validate and Document

**Actions:**

- Re-run the local audit and HTML validation
- Confirm 14 live products, assessment counts and practical assignments
- Confirm the Course 14 approval gate
- Update roadmap and system documentation

**Files affected:**

- `context/roadmap.md`
- `CLAUDE.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `outputs/systems/staff-hiring.md`
- `context/roadmap.md`
- `plans/trainer-onboarding-portal-spec.md`
- GHL grant-access workflows for Courses 2–12 and certification

### Updates Needed for Consistency

- Update the onboarding portal specification after live implementation
- Record the final Course 13 product and workflow identifiers in the staff-hiring system document
- Ensure no workflow grants Congratulations directly from Course 12

### Impact on Existing Workflows

The final path changes from theory completion to demonstrated competency: Course 12, Practical Sign-Off, Congratulations, then credential.

---

## Validation Checklist

- [x] Local Markdown, HTML and quiz CSV checks pass
- [x] All HTML files pass structural validation
- [x] All 13 current live course outlines are mapped
- [x] Course 9 progression conflict is resolved
- [x] Affected live lessons match the workspace
- [x] Courses 1–12 have the correct assessment count and 80% pass mark
- [x] Course 13 has one overview lesson and ten published practical tasks
- [x] Congratulations is numbered Course 14
- [x] Course 14 access requires completion of the manually graded final Course 13 assignment
- [x] Roadmap and system documentation reflect the verified live state

---

## Success Criteria

1. The workspace audit returns zero integrity errors.
2. GHL contains 14 correctly numbered products with no missing lessons.
3. Every theory assessment matches its canonical quiz and requires 80%.
4. A trainer cannot access Congratulations or receive certification until all ten practical blocks are approved.

---

## Notes

The live catalogue has low enrolment counts, so in-place corrections minimise disruption. Existing product IDs must be preserved because the current grant-access workflows reference them.

### Live identifiers

- Course 13 product: `15e03062-f6d2-4018-9e4b-0a980865aefc`
- Course 14 product: `36d85622-c33e-4bad-92cb-d1cf630b111a`
- Course 12 → Course 13 workflow: `238ca7f8-615e-4f81-9378-297bf04404a3`
- Course 13 → Course 14 workflow: `ET | Grant Access to 14 | Congratulations Course`, ID `f4259fb9-3e7f-406a-af3d-6bbb14257efe`
