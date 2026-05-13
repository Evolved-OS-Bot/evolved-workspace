# Staff Hiring & Recruitment System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-04-01

---

## Overview

The Staff Hiring & Recruitment System manages the full end-to-end journey of bringing a new trainer into The Evolved — from application through to active employment. It is built around a single dedicated pipeline with 7 stages, one published workflow (`Send Trainer Contract`), two surveys associated with the business's industry partnership (`Strength For Industry`), a dedicated custom field group for employment data, and supporting tags.

The system is comparatively lean — there is currently one automated workflow in this system (contract sending), which suggests earlier stages (application intake, interview scheduling, offer communication) are handled manually or via a separate intake mechanism not yet reflected in GHL automation. The pipeline structure clearly anticipates a clean linear progression: Apply → Interview → Offer → Contract → Signed → Onboarding → Active.

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
| 6 | Active Trainer | `0848b410-490a-4261-9088-b9d3ec4ef75b` |

Each stage maps to a discrete action in the hiring process. Candidates who do not progress are presumably removed from the pipeline rather than moved to a defined rejection stage — no "Rejected" or "Declined" stage exists.

---

## Tags

| Tag | Purpose |
|---|---|
| `trainer` | Applied to contacts who are trainers (employed or under consideration) |
| `trainer lead` | Prospective trainer / applicant before formal entry into the pipeline |

---

## Surveys

Two surveys exist under the "Strength For Industry" umbrella. These appear to be linked to an external industry program or partnership, with separate survey versions for employees and owners.

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

Only one workflow is active in the hiring system. It is named for contract delivery, which places its trigger point at the `Contract Sent` stage (position 3 in the pipeline). No automated workflows exist for:
- Application acknowledgement
- Interview scheduling or confirmation
- Offer letter delivery
- Onboarding task assignment
- Active trainer welcome/setup

These may be handled manually, or they represent gaps for future automation.

---

## Custom Fields

**Custom Field Group ID:** `IrG8dmE2Jp3GLhlxhw3r`

These fields store the employment details of hired trainers. They are populated once a candidate progresses through the pipeline and employment terms are agreed.

| Field Name | Type | Key | ID |
|---|---|---|---|
| Employee Address | TEXT | `contact.employee_address` | `oY04FAeYxe1lXPfzOVXD` |
| Employment Hours | NUMERICAL | `contact.employment_hours` | `0N2PK6Uh9EV0p88FilPn` |
| Employment Pay Rate | NUMERICAL | `contact.employment_pay_rate` | `nYkUJACXpsE4NeKNrFf1` |
| Employment Start Date | DATE | `contact.employment_start_date` | `DynmzofeGHskNc25cVyH` |
| Employment Type | SINGLE_OPTIONS | `contact.employment_type` | `VJr2a0xjrycSifKPSedE` |

### Employment Type — Options

| Option |
|---|
| Casual - Level 3A |
| Casual - Level 4A |
| Part Time - Level 3A |
| Part Time - Level 4A |
| Full Time - Level 3A |
| Full Time - Level 4A |

> **Note on employment classifications:** Level 3A and Level 4A refer to classifications under the Fitness Industry Award (Australia). Level 3 covers fitness instructors and personal trainers with a Certificate III qualification; Level 4 covers personal trainers with a Certificate IV qualification. The three engagement types (Casual, Part Time, Full Time) combined with two qualification levels gives six possible employment configurations tracked per trainer.

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
   → Contact moved to: Active Trainer [0848b410]
   → Tag: trainer applied
   → Trainer added to relevant staff lists (coach options appear in other
     system fields, e.g. CS: Results/Value - Coach Contacted)
```

---

## Relationship to Other Systems

The Staff Hiring pipeline feeds into the broader operational structure of the gym. Once a contact reaches `Active Trainer` status, they appear across other GHL systems:

- **Cancellation System:** Active trainers are listed as options in `CS: Results/Value - Coach Contacted` (`rxxE4BpClaV7YBrvNLWy`) — currently: Megan, Leisa, Hannah, Beth, Piper
- **Client-facing forms:** `Who is your personal trainer?` field (`YWkGI9PYbF8jP22NKpbQ`) lists active trainers — currently: Megan, Leisa, Marnie, Piper
- **Strength Assessment / Workshop fields:** `Who was your trainer today?` (`8JSzaPXo9REKsnAXcOM5`) — currently: Megan, Leisa
- **Personal calendars:** All active trainers have individual booking calendars for PT sessions (30, 45, and 60 min variants per trainer)

> These cross-system references are **hard-coded option lists** and are not dynamically linked to the hiring pipeline. When a new trainer is hired and reaches `Active Trainer`, these lists in other custom fields and forms must be manually updated.

---

## Calendars

No calendar is directly dedicated to the hiring/interview process. The following calendars are relevant to active trainers once hired:

| Calendar | Type | ID |
|---|---|---|
| 30 Min 1:1 - Beth | personal | `CYsooQLsfZNw654fuVkW` |
| 30 Min 1:1 - Hannah | personal | `ga1masDAJAbY7Vg1p5C2` |
| 30 Min 1:1 - Nora | personal | `zB8vInq5Hs44IrRKHkmx` |
| 30 Min 1:1 - Piper | personal | `oSrXQVZhtv1tyL0bMFHe` |
| 30 Min 1:1 PT - Leisa | personal | `pOia47f6u6bDNvVMGWPo` |
| 30 Min 1:1 PT - Marnie | personal | `MzmH5oZEAMI83SzuTFjg` |
| 30 Min 1:1 PT - Megan | personal | `YT1U8WtmgGb5SO3BWE5n` |
| 45 Min 1:1 - Hannah | personal | `rAV11ApEmTrpjmVorjPv` |
| 45 Min 1:1 - Nora | personal | `5lHjOoGaVFdJPNReVDeg` |
| 45 Min 1:1 PT - Beth | personal | `SAEvSLp0RBPlO4IywSUi` |
| 45 Min 1:1 PT - Leisa | personal | `xTF4OeRHi8vM8w7dcKuC` |
| 45 Min 1:1 PT - Marnie | personal | `pBmOPV2MvBbclaLF8E0w` |
| 45 Min 1:1 PT - Piper | personal | `skZi4KFJdJdoG2QqANoS` |
| 45 Minute 1:1 PT - Megan | personal | `JFVV14qlUY1QeLO62SMc` |
| 60 Min 1:1 - Hannah | personal | `u6q2Lr1V4R3y8uwY0qvA` |
| 60 Min 1:1 - Nora | personal | `U1RSfH7BhPSSXdsBl61N` |
| 60 Min 1:1 PT - Beth | personal | `b68CfIL98FnE0IyoU7OI` |
| 60 Min 1:1 PT - Leisa | personal | `HgRT8Vd7bsH2LZDeOzZz` |
| 60 Min 1:1 PT - Marnie | personal | `fphAhWDG3nA27kxTNh0r` |
| 60 Min 1:1 PT - Piper | personal | `EjHsuZD0s0vJUqPUXOMb` |
| 60 Minute 1:1 PT - Megan | personal | `UIdP5AYIwUW00hC7e5mN` |

> There is no "Interview Calendar" or "Hiring Call" calendar in the GHL account. Interview scheduling is handled outside GHL.

---

---

# System Notes & Observations

### What's built and working
- **Pipeline structure is sound** — the 7-stage progression from Applied through to Active Trainer covers the full hiring arc logically. No gaps in stage sequencing.
- **Employment Type field is well-designed** — capturing both engagement type (Casual/Part Time/Full Time) and qualification level (Level 3A/Level 4A) in a single SINGLE_OPTIONS field is efficient and aligns with Australian award compliance requirements.
- **`Send Trainer Contract` workflow is live** — at minimum, contract delivery is automated. This is the highest-leverage automation point in the process as it handles a legally important document.
- **Employment data captured on the contact record** — having `Employment Hours`, `Employment Pay Rate`, `Employment Start Date`, and `Employee Address` on the GHL contact record means trainer details are centralised alongside all other contact history.

### Current gaps to address

- **No application intake form in GHL** — there is no visible form or survey for capturing candidate applications. Applicants are likely coming in via email or an external job board, meaning their data is manually entered into GHL. A GHL application form would automate contact creation, stage entry, and initial tagging.

- **No interview booking calendar** — there is no calendar dedicated to interview scheduling. If interviewers wanted to self-schedule, this would need to be built. Currently this is a manual step.

- **No automated workflows for stages 0–2 (Applied, Interview, Offer Sent)** — the first three stages of the pipeline have no automation. Acknowledgement emails to applicants, interview confirmations, and offer communications are all manual. These are candidates for automation.

- **No rejection/disqualification stage** — the pipeline has no stage for candidates who are screened out. Contacts who don't progress presumably sit in whatever stage they reached or are manually deleted. A `Not Proceeding` stage (or equivalent) would improve pipeline hygiene and allow for future re-engagement.

- **No onboarding task automation** — there is no workflow visible for the `Onboarding` stage. Trainer setup tasks (system access, payroll setup, schedule configuration, uniform, etc.) are managed entirely outside GHL.

- **Hard-coded trainer name lists across the account** — when a new trainer is hired and reaches `Active Trainer`, their name needs to be manually added to at least four separate custom field option lists (coach assignment in cancellation, trainer attribution in client forms, and strength assessment). This is a maintenance risk as the team grows.

- **Strength For Industry surveys lack documented context** — two surveys (`Employee Survey` and `Owner Survey`) exist but their relationship to the hiring or onboarding flow is unclear. They may be part of an external industry body program rather than a direct part of the internal hiring process.

- **No off-boarding / termination workflow** — there is no pipeline or automation visible for managing a trainer leaving the business. Termination, tag removal, calendar deactivation, and client reassignment would all be manual.
