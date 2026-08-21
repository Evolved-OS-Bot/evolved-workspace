# Staff Hiring & Recruitment System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-31 (employment fields and hiring outcomes reconciled)

---

## Overview

The Staff Hiring & Recruitment System manages the full end-to-end journey of bringing a new trainer into The Evolved — from application through to active employment. It is built around a single dedicated pipeline with 7 stages, one published workflow (`Send Trainer Contract`), a dedicated custom field group for employment data, and supporting tags. The two Strength For Industry surveys are retained corporate-programme assets, not hiring intake assets.

The system is comparatively lean: contract sending is the only workflow attached directly to the hiring pipeline. A separate published course-access chain grants Trainer Portal Courses 2–12, Course 13 Practical Sign-Off and Course 14 Congratulations. Earlier hiring stages and the operational setup required between Contract Signed, Onboarding and Hired / Commenced remain manual or undocumented.

---

## Pipeline: Staff Hiring Pipeline
**Pipeline ID:** `DIxPOs1MIDsVZ88EldP2`

| Position | Stage | ID |
|---|---|---|
| 0 | Applied | `e200ff34-bded-48a9-b293-a09faedd4151` |
| 1 | Interview | `961af937-2e54-4599-8363-97b35d55bab9` |
| 2 | Offer Sent | `285091fc-9578-4252-9806-05ca3f76f14b` |
| 3 | Contract Sent | `21739d22-b02b-49fe-b96c-20afe1a727bd` |
| 4 | Contract Signed | `8832c25b-5e24-4168-a485-046f109ff322` |
| 5 | Onboarding | `7ca97b6c-4fdd-4251-bbac-ae61c345c75b` |
| 6 | Hired / Commenced | `0848b410-490a-4261-9088-b9d3ec4ef75b` |

Each stage maps to a discrete action in the hiring process. Candidates who do not progress are presumably removed from the pipeline rather than moved to a defined rejection stage — no "Rejected" or "Declined" stage exists.

On 31 July 2026 the final stage was renamed from `Active Trainer` to `Hired / Commenced` while preserving its existing ID. This makes the pipeline a record of successful hiring rather than a misleading current-staff roster.

---

## Tags

| Tag | Purpose |
|---|---|
| `trainer` | Applied to contacts who are trainers (employed or under consideration) |
| `trainer lead` | Prospective trainer / applicant before formal entry into the pipeline |

---

## Surveys

Two surveys exist under the "Strength For Industry" umbrella. Peter confirmed on 30 July 2026 that they should be retained for possible future corporate use. They are not part of the current hiring or onboarding process.

| Survey | ID |
|---|---|
| Strength For Industry (Employee Survey) | `p5TGEOTXtbMZsGIjcsBX` |
| Strength For Industry (Owner Survey) | `DxZdvxigcS6zc4imB7Z5` |

> **Note:** No dedicated job application form or onboarding intake form is visible in the GHL Forms or Surveys lists. Application intake is either handled off-platform (e.g., email, external job board) or via a form not yet identified in this dataset.

---

## Workflows

| Workflow | Status | ID |
|---|---|---|
| Send Trainer Contract | **published** | `6758cca7-78f4-4e99-a8a9-a012b745ba3d` |

Only one workflow is attached directly to the hiring pipeline. It is named for contract delivery, which places its trigger point at the `Contract Sent` stage (position 3 in the pipeline). No automated workflows exist for:
- Application acknowledgement
- Interview scheduling or confirmation
- Offer letter delivery
- Onboarding task assignment
- Active trainer welcome/setup

These may be handled manually, or they represent gaps for future automation.

### Live contract workflow audit: revalidated 30 July 2026

`Send Trainer Contract` is published and triggers when an opportunity enters `Staff Hiring Pipeline / Contract Sent`. It branches on Employment Type, but its coverage is incomplete:

- Part Time - Hybrid sends the matching hybrid part-time contract.
- Part Time - Level 3A sends the matching part-time Level 3A contract.
- Part Time - Level 4A sends the matching part-time Level 4A contract.
- Casual Level 3A and Casual Level 4A each send their matching casual contract.
- Full Time - Level 3A and Full Time - Level 4A reach empty branches and send nothing.
- The None fallback is empty and creates no exception task.

The workflow had no enrolments in the available 30-day history. Before the next hire reaches Contract Sent, either provide an approved document for every permitted Employment Type or restrict the field to contract types the business can actually issue. Add an exception task for any blank or unsupported employment type rather than allowing the workflow to end silently.

### Live Trainer Portal progression: rebuilt 24 July 2026

The published `ET | Grant Access` workflows form a sequential chain. Completion of Course 1 grants Course 2; each subsequent completion grants the next course through Course 12.

Completion of `12 | General Duties` now triggers `ET | Grant Access to 13 | Practical Sign-Off Course`, workflow ID `238ca7f8-615e-4f81-9378-297bf04404a3`. It grants the published Course 13 offer for product `13 | Practical Sign-Off: Certified to Deliver`, product ID `15e03062-f6d2-4018-9e4b-0a980865aefc`.

Course 13 contains one overview lesson and ten published native assignments. Each assignment is manually graded by Megan; the final assignment is `Block 10: 36 Workouts`. Its completion criteria trigger the published `ET | Grant Access to 14 | Congratulations Course` workflow, ID `f4259fb9-3e7f-406a-af3d-6bbb14257efe`, which grants `14 | Congratulations: You're Certified`.

The live path is therefore Course 12 → Course 13 Practical Sign-Off → approved Block 10 completion → Course 14 Congratulations. Course 13 has no automatic completion credential.

---

## Custom Fields

**Custom Field Group ID:** `IrG8dmE2Jp3GLhlxhw3r`

These fields store the employment details of hired trainers. They are populated once a candidate progresses through the pipeline and employment terms are agreed.

| Field Name | Type | Key | ID |
|---|---|---|---|
| Employee Address | TEXT | `contact.employee_address` | `oY04FAeYxe1lXPfzOVXD` |
| Employment Hours | NUMERICAL | `contact.employment_hours` | `0N2PK6Uh9EV0p88FilPn` |
| Employment Legal Name | TEXT | `contact.employment_legal_name` | `wLtZCQqqyGVxueXWQ0gw` |
| Employment Preferred Name | TEXT | `contact.employment_preferred_name` | `zALHt57bk4U5u1AUVNfu` |
| Employment Pay Rate | NUMERICAL | `contact.employment_pay_rate` | `nYkUJACXpsE4NeKNrFf1` |
| Employment Pay Effective Date | DATE | `contact.employment_pay_effective_date` | `yFHP4G9NFEmBGcefNpg7` |
| Employment Start Date | DATE | `contact.employment_start_date` | `DynmzofeGHskNc25cVyH` |
| Employment Type | SINGLE_OPTIONS | `contact.employment_type` | `VJr2a0xjrycSifKPSedE` |

### Field population audit: 31 July 2026

The complete 2,796-contact snapshot found six historical or current staff records with employment data. Employee Address, Employment Pay Rate, Employment Start Date and Employment Type each have six populated contacts; Employment Hours, Employment Legal Name and Employment Pay Effective Date each have three; Employment Preferred Name has one.

The low counts are valid and none of the eight fields should be deleted. The single Preferred Name value correctly maps Alyssa Crighton to Piper Mae; the legal-name and pay-effective-date fields were only added in July 2026.

Employee address and pay data are sensitive. Until a dedicated payroll or HR source of truth replaces them, access to these GHL fields should be limited to staff who genuinely require employment-contract information.

### Employment Type — Options

| Option |
|---|
| Casual - Level 3A |
| Casual - Level 4A |
| Part Time - Hybrid (Clerks L3/Fitness L2) |
| Part Time - Level 3A |
| Part Time - Level 4A |
| Full Time - Level 3A |
| Full Time - Level 4A |

> **Note on employment classifications:** Level 3A and Level 4A refer to classifications under the Fitness Industry Award (Australia). The live field contains six standard engagement/classification combinations plus the separate Part Time Hybrid option, for seven permitted values in total. Employment-law interpretation and contract suitability must be confirmed by the business's qualified adviser.

### Remuneration variations

Reusable remuneration variation templates are stored in GHL under **Payments → Documents & Contracts → Templates**:

- `Trainer Remuneration Variation - Casual`
- `Trainer Remuneration Variation - Part-Time Fitness`
- `Trainer Remuneration Variation - Hybrid Fitness-Clerks`
- `Trainer Bonus Incentive Variation - Template`

The templates merge `contact.employment_legal_name`, `contact.employment_type`, `contact.employment_pay_rate`, and `contact.employment_pay_effective_date`. The applicable template is used to create a draft document for the employee, which is reviewed before sending for electronic signature.

The bonus incentive variation replaces the former completed-assessment incentive with a $10 Level 4 pre-qualification completion bonus and limits the $60 sales bonus to eligible $399 or $599 membership-package sales completed at the Strength Assessment. Personal training sales are excluded. Its required signature fields follow the governed template pattern: the employee signs as `Contact` and Peter Brown signs as `Sender`.

Employment documents must use `contact.employment_legal_name`. Staff-facing notifications may use `contact.employment_preferred_name` when populated, falling back to the contact's first name when it is blank.

Updating the GHL pay-rate field does not itself instruct payroll. Payroll instructions are issued only after the signed variation has been received and checked.

---

## Hiring Journey: Step-by-Step Flow

```
1. Candidate identified (via referral, job board, or direct approach)
   → Tagged: trainer lead
   → Created as contact in GHL

2. Application received / expression of interest confirmed
   → Contact moved to pipeline stage: Applied [e200ff34]
   → Manual review by owner/manager

3. Candidate progresses to interview
   → Contact moved to: Interview [961af937]
   → Interview scheduled (manually — no GHL calendar linked to this stage)

4. Interview completed, offer decision made
   → Contact moved to: Offer Sent [285091fc]
   → Offer communicated manually (no automated workflow at this stage)

5. Candidate accepts offer
   → Contact moved to: Contract Sent [21739d22]
   → "Send Trainer Contract" workflow fires [6758cca7]
   → Employment Type, Employment Hours, Employment Pay Rate, Employee Address,
     Employment Start Date populated on contact record

6. Contract signed by candidate
   → Contact moved to: Contract Signed [8832c25b]
   → (No automated confirmation workflow observed)

7. Trainer enters onboarding
   → Contact moved to: Onboarding [7ca97b6c]
   → Onboarding tasks handled manually or externally

8. Onboarding complete, trainer live in the business
   → Contact moved to: Hired / Commenced [0848b410]
   → Opportunity closed as Won
   → Tag: trainer applied
   → Trainer added to relevant staff lists (coach options appear in other
     system fields, e.g. CS: Results/Value - Coach Contacted)
```

---

## Relationship to Other Systems

The Staff Hiring pipeline records the completed hiring journey. A current trainer does not appear across other GHL systems automatically merely because their opportunity reaches `Hired / Commenced`:

- **Canonical current trainer roster:** Megan, Piper, Nora, Katrina and Leisa
- **Cancellation System:** `CS: Results/Value - Coach Contacted` (`rxxE4BpClaV7YBrvNLWy`) lists Megan, Piper, Nora, Katrina and Leisa
- **Client-facing cancellation forms:** `Who is your personal trainer?` (`YWkGI9PYbF8jP22NKpbQ`) lists Megan, Piper, Nora, Katrina and Leisa
- **Strength Assessment survey:** `Who was your trainer today?` (`8JSzaPXo9REKsnAXcOM5`) lists the same five trainers plus `I can't remember`
- **Personal calendars:** All active trainers have individual booking calendars for PT sessions (30, 45, and 60 min variants per trainer)

> These cross-system references are **hard-coded option lists** and are not dynamically linked to the hiring pipeline or GHL staff accounts. Update both live cancellation-related fields together whenever a trainer joins or leaves.

---

## Calendars

No calendar is directly dedicated to the hiring/interview process. The following calendars are relevant to active trainers once hired:

| Calendar | Type | ID |
|---|---|---|
| 30 Min 1:1 - Nora | personal | `zB8vInq5Hs44IrRKHkmx` |
| 30 Min 1:1 - Piper | personal | `oSrXQVZhtv1tyL0bMFHe` |
| 30 Min 1:1 PT - Katrina | personal | `eoL2TrbLGb8D5BA98Z7I` |
| 30 Min 1:1 PT - Leisa | personal | `pOia47f6u6bDNvVMGWPo` |
| 30 Min 1:1 PT - Megan | personal | `YT1U8WtmgGb5SO3BWE5n` |
| 45 Min 1:1 - Nora | personal | `5lHjOoGaVFdJPNReVDeg` |
| 45 Min 1:1 PT - Katrina | personal | `pLtfbopAKPgSGqDnwndF` |
| 45 Min 1:1 PT - Leisa | personal | `xTF4OeRHi8vM8w7dcKuC` |
| 45 Min 1:1 PT - Piper | personal | `skZi4KFJdJdoG2QqANoS` |
| 45 Minute 1:1 PT - Megan | personal | `JFVV14qlUY1QeLO62SMc` |
| 60 Min 1:1 - Nora | personal | `U1RSfH7BhPSSXdsBl61N` |
| 60 Min 1:1 PT - Katrina | personal | `9QkeVcyoclQuWOmNlUup` |
| 60 Min 1:1 PT - Leisa | personal | `HgRT8Vd7bsH2LZDeOzZz` |
| 60 Min 1:1 PT - Piper | personal | `EjHsuZD0s0vJUqPUXOMb` |
| 60 Minute 1:1 PT - Megan | personal | `UIdP5AYIwUW00hC7e5mN` |

> There is no "Interview Calendar" or "Hiring Call" calendar in the GHL account. Interview scheduling is handled outside GHL.

---

---

# System Notes & Observations

### What's built and working
- **Pipeline structure is sound** — the seven-stage progression from Applied through to Hired / Commenced covers the full hiring arc logically. No gaps in stage sequencing.
- **Historical hiring outcomes are reconciled**: Meroe Mozakka, Katrina Parsons, Nora Silva, Joanne McDonald and Alyssa Crighton / Piper Mae are all genuine hires. On 31 July 2026 all five were placed in Hired / Commenced and closed as Won; fresh read-back found zero open opportunities.
- **Employment Type field is well-designed** — capturing both engagement type (Casual/Part Time/Full Time) and qualification level (Level 3A/Level 4A) in a single SINGLE_OPTIONS field is efficient and aligns with Australian award compliance requirements.
- **`Send Trainer Contract` workflow is published** — contract delivery is automated for five of seven permitted Employment Type values: both casual levels, Part Time Hybrid and both part-time levels. Both full-time values and the None fallback are not safely covered.
- **Employment data captured on the contact record** — having `Employment Hours`, `Employment Pay Rate`, `Employment Start Date`, and `Employee Address` on the GHL contact record means trainer details are centralised alongside all other contact history.

### Current gaps to address

- **Hiring pipeline is not the staff roster**: Megan and Leisa are absent because the pipeline was introduced after their hiring journeys. Do not backfill them merely to force roster parity. Current employment and offboarding require a separate governed staff-lifecycle record.

- **No application intake form in GHL** — there is no visible form or survey for capturing candidate applications. Applicants are likely coming in via email or an external job board, meaning their data is manually entered into GHL. A GHL application form would automate contact creation, stage entry, and initial tagging.

- **No interview booking calendar** — there is no calendar dedicated to interview scheduling. If interviewers wanted to self-schedule, this would need to be built. Currently this is a manual step.

- **No automated workflows for stages 0–2 (Applied, Interview, Offer Sent)** — the first three stages of the pipeline have no automation. Acknowledgement emails to applicants, interview confirmations, and offer communications are all manual. These are candidates for automation.

- **No rejection/disqualification stage** — the pipeline has no stage for candidates who are screened out. Contacts who don't progress presumably sit in whatever stage they reached or are manually deleted. A `Not Proceeding` stage (or equivalent) would improve pipeline hygiene and allow for future re-engagement.

- **No onboarding task automation** — there is no workflow visible for the `Onboarding` stage. Trainer setup tasks (system access, payroll setup, schedule configuration, uniform, etc.) are managed entirely outside GHL.

- **Hard-coded trainer name lists across the account** — when a new trainer is hired and reaches `Hired / Commenced`, their name needs to be manually added to at least four separate custom field option lists (coach assignment in cancellation, trainer attribution in client forms, and strength assessment). This is a maintenance risk as the team grows.

- **Strength For Industry surveys are dormant corporate assets** — the Employee and Owner surveys are intentionally retained for possible future corporate use and are not part of staff hiring. They require a current offer, owner and workflow audit before reactivation.

- **No off-boarding / termination workflow** — there is no pipeline or automation visible for managing a trainer leaving the business. Termination, tag removal, calendar deactivation, and client reassignment would all be manual.
