# Trainer Onboarding Portal — Specification

**Status:** In progress — Course 1 complete in GHL, Courses 2–9 content ready to paste
**Platform:** GoHighLevel (Memberships → Courses)
**Build method:** GHL course builder — content, quizzes, assignments, and certificates all native
**Cost:** $0 additional — already on GHL plan

---

## Purpose

A structured onboarding portal for new employee trainers at The Evolved All Female Gym. Tracks individual progress through SOPs, comprehension, and physical sign-off. Issues branded certificates on full completion.

---

## Access

- Each trainer gets an individual GHL contact/login
- Admin access: Peter and Megan
- Delivered via GHL Client Portal — not publicly accessible

---

## Completion Requirements Per Course

Each course requires all three components to be complete before a certificate is issued:

1. **Content** — read the SOP (tracked by TalentLMS)
2. **Comprehension quiz** — minimum 80% pass mark
3. **Physical sign-off** — assignment submission or ILT session approved by management

---

## Course Structure

### Onboarding Path (sequential — must complete in order)

| Order | Course | SOP Source | Physical Sign-Off |
|---|---|---|---|
| 1 | Welcome & Standards | `professional-standards-and-policies.md` + `privacy-policy.md` + `emergency-procedures.md` | Sign employment agreement (upload scan) |
| 2 | Making Women Strong | — | Educate a mock client on the Key Performance Habits with Peter or Megan |
| 3 | Metabolic Burn (HIIT) | `metabolic-burn-hiit.md` | Deliver one supervised class |
| 4 | Hybrid Fitness Racing | `hybrid-fitness-racing.md` | Deliver one supervised class |
| 5 | Evolved Pilates | `evolved-pilates-session.md` | Deliver one supervised class |
| 6 | Sculpt & Strength | `sculpt-and-strength-session.md` | Complete 36 workouts recorded in Trainerize + deliver one supervised class |
| 7 | 1:1 Personal Training | `1-1-personal-training.md` | Deliver a supervised mock PT session |
| 8 | Intro Sessions | `intro-sessions.md` | Deliver a supervised mock intro session with Megan |
| 9 | Strength Assessment | `strength-assessment.md` + `objection-handling.md` | Deliver a supervised mock assessment with Peter or Megan |
| 10 | Member Care | `monthly-member-checkin.md` | Role-play a monthly check-in call with Peter or Megan |
| 11 | General Duties | `open-close-checklist.md` + `no-show-checklist.md` | Complete a supervised open or close shift |
| 12 | Congratulations | — | None — certificate issued automatically on completion |

---

## Certificate Design

- Issued per course on full completion (content + quiz + physical sign-off)
- Branded with The Evolved All Female Gym logo
- Certificate name format: `[Course Name] — Certified Delivery`
- Example: `Sculpt & Strength — Certified Delivery`
- PDF — trainer can download and keep

---

## Quiz Design

- Minimum pass mark: 80%
- Retakes allowed (unlimited)
- Questions drawn from SOP content — factual and scenario-based
- ~5–10 questions per course

---

## Physical Sign-Off Methods

| Method | Used For |
|---|---|
| **Assignment upload** | Contractor agreement, Trainerize workout screenshots |
| **ILT (in-person session)** | Supervised class delivery, mock assessments, mock check-in calls |

ILT sessions logged in TalentLMS by Peter or Megan with pass/fail outcome.

---

## Build Steps

### In GHL (Claude builds course content, Peter publishes)
- [x] Create all 12 courses under Memberships → Courses
- [x] Write all 12 courses as HTML files — ready to paste into GHL source editor (`outputs/trainer-portal/html/`)
- [x] Course 1 (Welcome & Standards) — lessons pasted in GHL
- [x] Course 2 (Making Women Strong) — lessons pasted in GHL
- [x] Course 3 (Metabolic Burn HIIT) — lessons pasted in GHL
- [x] Course 4 (Hybrid Fitness Racing) — lessons pasted in GHL
- [x] Course 5 (Evolved Pilates) — lessons pasted in GHL
- [x] Course 6 (Sculpt & Strength) — lessons pasted in GHL
- [x] Course 7 (1:1 Personal Training) — lessons pasted in GHL
- [x] Course 8 (Intro Sessions) — lessons pasted in GHL
- [x] Course 9 (Strength Assessment) — lessons pasted in GHL
- [x] Course 10 (Member Care) — lessons pasted in GHL
- [x] Course 11 (General Duties) — lessons pasted in GHL
- [x] Course 12 (Congratulations) — lessons pasted in GHL
- [ ] Add comprehension quiz to each course (pass mark 80%) — questions in each `.md` file in `outputs/trainer-portal/` — all questions audited and correct
- [ ] Add assignment lesson for physical sign-off (file upload enabled)
- [ ] Set course prerequisites (sequential path)
- [ ] Design certificate template under Memberships → Credentials
- [ ] Configure automation: send certificate on course completion

### GHL Automation (trigger on course completion)
- Certificate issued automatically via Credentials
- Optional: notify Peter/Megan when a physical assignment is submitted for review
