# Plan: Member Advocacy & Evidence Engine

**Created:** 2026-07-27
**Status:** Draft
**Request:** Design one governed, SOP-first system that identifies appropriate Google-review, written-results and video-testimonial opportunities from existing member, training and outreach evidence, then validates it through an eight-week no-send shadow pilot.

---

## Overview

### What This Plan Accomplishes

This plan creates a single governed Member Advocacy & Evidence Engine with three strictly separated recommendation streams:

1. neutral milestone-based Google-review outreach;
2. evidence-backed written testimonial and results-asset candidates; and
3. high-story-potential video-testimonial candidates.

The engine will reuse the existing GHL–Stripe–Trainerize identity and lifecycle reconciliation, Trainerize longitudinal analysis, active-member performance reporting, Review Pipeline and member-story publishing system. It will add the governance, consent, communication suppression, human validation, feedback and outcome reporting that are currently missing.

No member message, live GHL change, Railway deployment, Google Drive write or public publication is authorised by this plan. Implementation may begin only after Peter approves the plan and its open decisions. The first operational phase is an eight-week shadow pilot with no auto-send and no public claims.

### Why This Matters

The Evolved already has valuable proof: a live Google-review journey, a large member-story library, 25,186 tracked workouts for profiles recorded as female, 539,694 exercise-result records, 118 retrospective remarkable-result screening candidates and 68 current active-member remarkable-result candidates in the latest performance report.

Those assets are not yet one controlled system. The current review journey uses a satisfaction gate before the Google link, the story library lacks structured consent and evidence provenance, and the publishing command can distribute a story without a mandatory release or claim-validation gate. A governed engine can increase credible advocacy while reducing review-manipulation, privacy, medical-claim, duplicate-contact and staff-capacity risk.

---

## Current State

### Relevant Existing Structure

| Existing asset | Current role | Reuse decision |
|---|---|---|
| `outputs/systems/review-reputation.md` | Documents the published tag-triggered rating and Google-review journey, Review Pipeline and manual fallback | Retain as the live-system record; reconcile it to the new neutral policy after approval |
| Review Pipeline | Tracks requested, negative response, positive response, link clicked and review received | Reuse the requested/clicked/received stages during transition; do not treat click as publication |
| `send review request` tag | Starts the current review workflow | Do not reuse for milestone cycles until entry, removal, cooldown and re-entry rules are rebuilt |
| `scripts/run_trainerize_reporting.py` and `scripts/trainerize_performance_reporting.py` | Produce reconciled active-member performance and remarkable-result queues | Reuse through a stable read-only evidence contract; do not duplicate extraction or movement calculations |
| `outputs/trainerize-longitudinal-audit-2026-07-21/` | Holds de-identified longitudinal outcomes, data-quality caveats and a broad remarkable-result screening queue | Reuse the methodology, caveats and candidate evidence definitions |
| `data/private/integration-reporting/` | Holds identified reconciliation, performance and candidate records | Use only as a restricted source; never copy identified rows to public outputs |
| Railway `Retention Intelligence` | Retains current cross-system identity, lifecycle and usage snapshots | Reuse through an approved read-only contract in a later deployment stage; do not launch a competing daily extractor |
| `reference/member-stories.md` | Master narrative and transcript library | Preserve content, then add evidence, consent, release, claim and publication metadata |
| `.claude/commands/add-member-story.md` | Publishes a story across WordPress, homepage, results hub, GHL email and social | Retain as the publishing executor, but place evidence, release and editorial gates before Phase 2 and all live actions |
| `scripts/notify_story.py` | Triggers life-stage story emails and member notification | Retain; make it callable only after the new publication gate is complete |
| `scripts/post_story_social.py` | Publishes story assets to Facebook and Instagram | Retain; make dry-run and approval evidence mandatory before live use |
| `outputs/systems/social-proof-pages.md` | Records results-page structure, taxonomy and story distribution workflows | Extend with evidence and consent states rather than create a second page system |
| `reference/marketing-playbook.md` | Defines success-story format and content use | Add evidence, medical-claim and consent rules |
| `outputs/systems/ghl-workflow-owner-review-register.md` | Governs live workflow owners and review cadence | Add the advocacy system only after owners are approved |
| `reference/sops/` | Canonical operational procedures | Create the advocacy SOP here before assigning any recurring staff work |

### Evidence Baseline

- The final longitudinal audit contains 529 profiles explicitly recorded as female, 484 with tracked completed workouts and 271 with detailed workout records.
- It identifies 118 broad remarkable-result screening candidates. These are review candidates, not verified transformations.
- The latest active-member performance report identifies 68 active remarkable-result candidates using at least 50 tracked workouts plus either a material movement improvement or 75 workouts in the last year.
- Most strength results are retrospective training-log proxies using estimated one-repetition maximum, not standardised tests.
- Comparable bench press and deadlift records are the most interpretable current movement evidence.
- Farmer Walk conventions, cross-variant exercise comparisons, sparse formal reassessment coverage and selected-survivor effects remain material caveats.
- The existing story file contains 46 story or transcript headings, including duplicate people and multiple versions. It does not provide a one-row-per-person asset register.
- Only 13 results pages are documented as published in `outputs/systems/social-proof-pages.md`; the story library and website page index are not currently one reconciled inventory.

### Gaps or Problems Being Addressed

1. **The current Google-review journey is sentiment gated.** A member first supplies a 1-to-5 rating and only a 4 or 5 receives the Google link. Google prohibits selectively soliciting positive reviews, and the new engine expressly requires neutral milestone eligibility.
2. **The legacy onboarding review and a new milestone cycle can collide.** The current trigger tag is retained permanently, re-entry is enabled, and there is no governed repeat-cycle rule.
3. **A link click is not a published review.** `Trigger Link Clicked` proves intent only. `Review Received` has no independently confirmed Google matching control or approved recurring owner.
4. **The story system has no mandatory consent and release gate.** The publishing command can create a WordPress page, email contacts and post to social from supplied story details without a recorded release scope.
5. **Evidence provenance is not structured per story.** `reference/member-stories.md` says every story is verified and approved, but it does not record who verified each claim, the source record, comparability, consent scope, approval date or withdrawal status.
6. **Some current story wording is not safe as a public claim.** Examples include symptoms being “completely eliminated,” an injury being “overcome,” “osteoporosis reversal,” inflammatory changes and pregnancy outcomes. A member quote can be authentic while still requiring careful context and explicit sensitive-information permission.
7. **Trainerize candidates are screening signals, not publication authority.** Current scoring can flag large percentage changes caused by low baselines, logging differences, equipment changes or incomplete histories.
8. **There is no cross-stream communication suppression.** A member could receive a review, written-story and video ask too close together.
9. **There is no common decision feedback.** Approve, snooze, decline and wrong-recommendation actions are not stored as governed evidence for improving the system.
10. **Roles and cover are incomplete.** Admin Eve, Piper, coaches and Peter have adjacent responsibilities, but this workstream has no approved RACI, absence cover or escalation rule.
11. **The existing publishing workflow duplicates a member story across many surfaces in one pass.** That is efficient after approval, but it amplifies any evidence, consent or wording error.
12. **The privacy policy is too general for this use.** It does not expressly explain using training and potentially sensitive health information to screen for public marketing stories.
13. **The current story command conflicts with forward-facing formatting rules.** It instructs use of em dashes in public story content while workspace rules prohibit them in forward-facing content.

---

## Proposed Changes

### Summary of Changes

- Create a canonical, versioned Member Advocacy & Evidence SOP before any staff responsibility or live workflow is assigned.
- Build a thin read-only shadow engine that consumes existing reconciled data and candidate outputs instead of extracting Trainerize history again.
- Create one private advocacy ledger containing recommendation, evidence, suppression, consent, decisions and outcomes.
- Generate a weekly shadow report with three visually and operationally separate recommendation tables.
- Use deterministic, sentiment-neutral Google-review eligibility and separate evidence/story scoring for written and video candidates.
- Enforce one global advocacy-ask cooldown across all three streams.
- Require coach validation before any results or video outreach recommendation can be approved.
- Require explicit, granular release before any identifiable written, photo, training-result, sensitive-health or video material is published.
- Add approve, snooze, decline and wrong-recommendation feedback with reason codes and audit history.
- Add manual Google-review matching and distinguish requested, clicked, possible match and confirmed published review.
- Reconcile the member-story library into a governed asset register without deleting the narrative source material.
- Put the existing WordPress, GHL email and social publishing system behind a fail-closed publication checklist.
- Run an eight-week no-send shadow pilot before any member outreach.
- Graduate only to human-approved, manually sent outreach. Auto-send is outside this plan and requires a later approval.

### New Files to Create

| File Path | Purpose |
|---|---|
| `reference/sops/member-advocacy-and-evidence.md` | Canonical versioned SOP covering scope, roles, evidence, eligibility, suppression, consent, exceptions, publication, feedback, reporting, absence cover and revision history |
| `reference/member-advocacy-consent-and-release.md` | Controlled member-facing written, photo, results and video release template with granular channel and sensitive-information choices |
| `outputs/systems/member-advocacy-evidence-engine.md` | Durable system runbook, data dictionary, report definitions, GHL mapping, operating cadence, recovery and graduation controls |
| `outputs/systems/member-advocacy-shadow-review-log.md` | De-identified pilot decision log and weekly accuracy/workload summary |
| `member_advocacy_shadow/__init__.py` | Package marker |
| `member_advocacy_shadow/config.py` | Safe configuration, source locations, Brisbane schedule, cooldowns, capacity ceilings and feature flags |
| `member_advocacy_shadow/models.py` | Typed recommendation, evidence, suppression, consent, decision and outcome records |
| `member_advocacy_shadow/source_contracts.py` | Read-only adapters for reconciliation, Trainerize evidence, GHL outreach state, story inventory and future Retention Intelligence contract |
| `member_advocacy_shadow/identity.py` | Exact-email and approved-crosswalk identity resolution; no fuzzy or name-only matching |
| `member_advocacy_shadow/evidence.py` | Comparable-result checks, source timestamps, claim caveats and sensitive-information masking |
| `member_advocacy_shadow/eligibility.py` | Sentiment-neutral Google-review milestones and hard eligibility/exclusion rules |
| `member_advocacy_shadow/scoring.py` | Separate written-results and video-story ranking models |
| `member_advocacy_shadow/suppression.py` | Global and stream-specific cooldown, DND, decline, prior-review and active-contact suppression |
| `member_advocacy_shadow/drafts.py` | Guardrailed personalised outreach drafts for each stream |
| `member_advocacy_shadow/state_store.py` | Private SQLite/PostgreSQL ledger schema, idempotent run storage, decisions and audit trail |
| `member_advocacy_shadow/reporting.py` | Restricted HTML/CSV or local workbook report generation with three separate queues |
| `member_advocacy_shadow/run_shadow.py` | Manual and scheduled no-send run entry point |
| `member_advocacy_shadow/.env.example` | Variable names only, with all send/write flags false |
| `member_advocacy_shadow/README.md` | Local run, privacy, review, recovery and future deployment instructions |
| `member_advocacy_shadow/tests/conftest.py` | Synthetic identities, milestones, evidence and outreach histories |
| `member_advocacy_shadow/tests/test_google_eligibility.py` | Proves eligibility is independent of sentiment and result quality |
| `member_advocacy_shadow/tests/test_evidence.py` | Comparable-result, stale-source, logging anomaly and medical-claim tests |
| `member_advocacy_shadow/tests/test_scoring.py` | Written and video ranking boundary tests |
| `member_advocacy_shadow/tests/test_suppression.py` | Same-period, prior review, DND, decline, snooze and cross-stream suppression tests |
| `member_advocacy_shadow/tests/test_identity.py` | Exact match, approved crosswalk, ambiguity and wrong-person tests |
| `member_advocacy_shadow/tests/test_drafts.py` | Honest-review wording, no incentive, no prescribed content and sensitive-data masking tests |
| `member_advocacy_shadow/tests/test_state_store.py` | Idempotency, audit history and decision-state tests |
| `member_advocacy_shadow/tests/test_reporting.py` | Required columns, capacity ceilings, private/public separation and no-send banner tests |
| `member_advocacy_shadow/tests/test_read_only_boundary.py` | Proves the pilot has no GHL, Google, Drive, Trainerize, Railway or messaging write path |

Runtime-only identified data will be created under `data/private/member-advocacy/`. That directory remains git-ignored and will contain the private ledger, source snapshots and identified reports. No member identity will be committed under `outputs/`.

### Files to Modify

| File Path | Changes |
|---|---|
| `context/roadmap.md` | Move the workstream to Scoped after this plan, then record implementation, pilot and graduation states as gates are actually passed |
| `CLAUDE.md` | After implementation exists, document the new service, SOP, private-data path and command/run pattern |
| `outputs/systems/review-reputation.md` | Replace the future-state sentiment gate with neutral review eligibility; document matching, repeat control, suppression, owner and migration/rollback |
| `outputs/systems/social-proof-pages.md` | Add evidence, release, public-claim and withdrawal states to the publishing workflow |
| `outputs/systems/ghl-workflow-owner-review-register.md` | Add the approved advocacy workflow family, owners, steward, review cadence and pilot boundary |
| `outputs/systems/ghl-team-task-trigger-register.md` | Add only approved recurring review, coach-validation, outreach and publication tasks |
| `outputs/systems/trainerize-reporting-reconciliation.md` | Document the stable evidence export consumed by the advocacy engine and prohibit duplicate Trainerize extraction |
| `outputs/systems/website-architecture.md` | Record consent/evidence metadata expectations for Results CPT pages and withdrawal handling |
| `reference/member-stories.md` | Reconcile duplicate people/versions and add structured asset, evidence, consent, claim, publication and withdrawal metadata |
| `reference/marketing-playbook.md` | Add claim hierarchy, evidence wording, sensitive-information, testimonial editing and consent rules |
| `reference/sops/privacy-policy.md` | Update only after privacy/legal review to describe the approved analytics, consent and public-marketing use accurately |
| `.claude/commands/add-member-story.md` | Add mandatory preflight gates, claim register, release ID, coach validation, Peter approval, dry runs and no-em-dash rule before any live action |
| `scripts/notify_story.py` | Add release/approval inputs, dry-run-first enforcement, immutable publication ID and fail-closed validation |
| `scripts/post_story_social.py` | Add release/approval inputs, claim-safe caption source and fail-closed live-publish guard |
| `scripts/SETUP.md` | Document the shadow run, private data, evidence refresh and future feature flags |
| `scripts/trainerize_performance_reporting.py` | Export a versioned evidence contract with raw comparison dates, movement, baseline/current values, source freshness and caveats; preserve existing calculations |
| `scripts/test_trainerize_performance_reporting.py` | Test the new contract and ensure no claim is marked publication-ready automatically |

### Files to Delete (if any)

None.

The existing Review Pipeline, story scripts and historical stories are retained. Unsafe or unproven claims are marked for review rather than silently removed. The existing live review workflow remains unchanged during the shadow pilot unless Peter separately authorises a compliance migration.

---

## Design Decisions

### Key Decisions Made

1. **One governed system, three separate asks:** Review, written-results and video recommendations share identity, suppression and consent infrastructure, but their eligibility, draft wording, decision state and outcome reporting remain separate.
2. **Google-review eligibility is deterministic and sentiment neutral:** A member becomes eligible through genuine-experience milestones and contact rules, never a satisfaction rating, retention score, predicted sentiment, strength result or coach belief that she will be positive.
3. **Capacity is a ceiling, not a review quota:** Staff will not be assigned a required number of reviews. The report limits workload and protects communication quality; it does not pressure staff or members.
4. **No review incentives:** No payment, discount, gift, free service, competition entry or other benefit may be tied to leaving, changing or removing a Google review.
5. **Ask for an honest review without scripting content:** The draft may link to Google and explain why honest feedback helps. It must not request a star rating, specified words, staff-name mention or revision/removal of a negative review.
6. **Do not reuse the current 4–5-star gate:** After approval and pilot readiness, the live review workflow must be rebuilt or replaced. The biased path is not a rollback target.
7. **Neutral Google milestones:** Initial candidate milestones are 90 days of verified membership, six, twelve and twenty-four-month anniversaries, and 50, 100 or 250 tracked workouts. A candidate needs one verified milestone, not a positive result.
8. **Milestones are eligibility events, not automatic sends:** DND, an existing review, recent outreach, a member-requested contact hold, identity ambiguity and documented policy exceptions can suppress an otherwise eligible member. Satisfaction, complaints and service-recovery outcomes cannot be used to select Google candidates.
9. **Existing onboarding review is an active suppression signal:** During shadow mode, anyone currently enrolled in, recently completed or already contacted through the legacy review journey is excluded from a milestone recommendation.
10. **One advocacy ask per member in 60 days:** A Google, written-results or video ask suppresses the other two streams for 60 days. If a member ranks in multiple streams, the report proposes one best next ask and records the deferred alternatives.
11. **Stream-specific repeat rules:** A confirmed published Google reviewer receives no automated repeat request. An unconfirmed review request has a minimum 365-day cooldown. Written or video no-response has a 180-day cooldown; a decline suppresses indefinitely until the member proactively reopens permission. Snooze options are 30, 60 or 90 days.
12. **Results and video are ranked, not auto-approved:** Objective evidence and story potential determine review order. Coach validation and explicit consent determine whether outreach and publication may proceed.
13. **Coach validation precedes results/video outreach:** The coach must verify the movement, equipment, load convention, training context and whether the proposed story is appropriate before Piper contacts the member.
14. **Comparable evidence is mandatory for public performance claims:** The same canonical exercise, compatible load convention, valid dates, plausible values and source record must exist. Cross-variant kilograms are not compared, and estimated one-repetition maximum is labelled as an estimate where relevant.
15. **Public claim hierarchy:** `Verified comparable result` may support a precise training claim; `member-reported outcome` may be quoted as personal experience with attribution; `screening signal` remains internal; `medical or causal claim` is prohibited without a separately approved evidence and legal pathway.
16. **No causal language:** Public assets may say what was recorded or what the member reports. They may not say The Evolved caused injury resolution, disease reversal, symptom elimination, pregnancy outcomes or clinical improvement.
17. **Sensitive information is opt-in by item:** Health condition, pregnancy, postpartum status, injury, mental health, DEXA result and other sensitive details require an explicit checkbox or written permission that names the detail and approved channels.
18. **Consent is granular:** Separate choices cover first name, surname, age/decade, written quote, training metrics, body-composition data, before/after images, sensitive health information, video, website, email, organic social and paid advertising.
19. **Consent can be withdrawn prospectively:** The SOP will define what The Evolved can remove from controlled channels, what may persist in third-party shares or archives, the response deadline and the publication-suppression state.
20. **Minors require guardian authority:** A teen story or video needs guardian consent plus the young person’s assent before identifiable publication.
21. **Exact identity resolution only:** Use exact normalised email plus GHL/Trainerize IDs or an owner-approved crosswalk. Name-only, Google display-name-only and fuzzy automatic matches are prohibited.
22. **Manual Google-review confirmation:** Admin Eve checks the visible Google Business Profile, records review date, display name and direct review reference where available, then classifies `confirmed`, `possible match`, `unmatched` or `not found`. Only a confirmed match advances to Review Received.
23. **The story library becomes an asset register, not a second database:** Narrative content stays in `reference/member-stories.md`; structured provenance and release references are added without copying identified training records into the file.
24. **The engine consumes existing data products:** It reads the current reconciliation, Trainerize evidence contract and story inventory. It does not call the historical Trainerize extractor or recalculate movement families independently.
25. **A separate private decision ledger is justified:** GHL is a communication and visible member-state surface, not the complete evidence store. The private ledger retains recommendation versions, evidence snapshots, feedback and consent audit history.
26. **No new GHL pipeline during shadow mode:** The existing Review Pipeline remains the live review surface. Results/video state stays in the private ledger until the pilot proves which minimal GHL fields staff actually need.
27. **Human-approved outreach is the graduation state:** Even after a successful pilot, every message is individually approved. Auto-send is explicitly outside scope.
28. **Publication reuses the existing executor:** `/add-member-story`, `notify_story.py` and `post_story_social.py` remain the downstream publication system, gated by a valid release ID, evidence record, coach validation and Peter approval.
29. **Fail closed on stale evidence:** If the Trainerize source timestamp is too old to support the stated claim, the recommendation may identify a candidate but cannot produce a public claim until refreshed and revalidated.
30. **No staff responsibility is silently assigned:** Proposed roles become operational only after Peter confirms the person, cover and expected workload.

### Recommendation Models

#### Google Review Eligibility

Google-review recommendations use hard gates, not a positivity score.

**Required:**

- verified member identity and genuine service experience;
- active member during the pilot;
- one verified neutral milestone;
- valid contact permission and no relevant DND/opt-out;
- no confirmed published Google review;
- no Google request in the previous 365 days;
- no advocacy ask of any type in the previous 60 days;
- no active legacy review-workflow enrolment or recent legacy request;
- no unresolved identity exception or member-requested, legal or safety-based nonessential-contact hold; and
- monthly capacity available.

**Ordering after eligibility:**

1. oldest unacknowledged milestone;
2. longest time since any advocacy ask;
3. higher-confidence identity and tenure evidence; and
4. deterministic contact ID as a stable tie-break.

No satisfaction, result, retention-risk, predicted churn, coach sentiment or review-likelihood input is permitted.

#### Written Results Candidate Score

Hard gates apply before ranking: verified identity, active status, source freshness, no suppression, no existing duplicate asset, and coach validation pending or complete.

| Component | Weight | Definition |
|---|---:|---|
| Comparable evidence quality | 35 | Same canonical exercise or documented measurement, plausible values, usable dates, source completeness and no convention conflict |
| Breadth and durability | 20 | Multiple validated movements, repeated milestone, assessment corroboration or sustained training history |
| Story arc grounded in records | 15 | Clear objective starting point and later state without inferring emotion or health outcomes |
| Existing proof gap | 15 | Adds an underrepresented life stage, goal or evidence type in the current published library |
| Source recency and current relevance | 10 | Recent enough to discuss accurately and member currently contactable |
| Production readiness | 5 | Approved image/video availability or a simple written-only route |

The score ranks coach review only. It does not certify a claim or authorise outreach.

#### Video Testimonial Candidate Score

| Component | Weight | Definition |
|---|---:|---|
| Validated evidence strength | 30 | Coach-validated objective training or membership milestone with clear caveats |
| Story depth | 25 | Existing first-person narrative, meaningful before/after context and a clear member-owned perspective |
| Distinctiveness and representation gap | 20 | Adds a needed goal, life stage, starting point or long-term journey |
| Visual or demonstration potential | 15 | A movement, milestone or existing asset can be shown without unsafe before/after implications |
| Production practicality | 10 | Current member, contactable, and no known release or scheduling barrier |

The model must not infer camera confidence, personality, positive sentiment, health status or willingness. Those are human conversations, not prediction features.

### Required Recommendation Record

Every row in all three report sections must contain:

- immutable recommendation ID and run ID;
- member and source identity keys in the private report only;
- recommendation stream;
- eligibility milestone or candidate reason;
- supporting evidence with source date;
- evidence-confidence level and the reasons for it;
- caveats and prohibited wording;
- current suppression checks and next eligible date;
- existing Google review, story and video status;
- proposed staff owner and cover;
- personalised outreach draft;
- recommended next action;
- decision state: `pending`, `approve`, `snooze`, `decline`, `wrong recommendation`;
- decision reason, actor and timestamp; and
- eventual outcome fields without converting an outcome into a staff quota.

### Proposed Roles and Cover

These are recommended assignments, not active responsibilities until Peter confirms them.

| Role | Primary responsibility | Normal deadline | Absence/cover rule |
|---|---|---|---|
| Admin Eve | Run-control and queue hygiene; verify identity, contact history, DND, prior asks and Google-review matches; prepare the weekly exception list | Review report within two business days | Peter or a specifically nominated trained Admin cover; no unassigned queue |
| Assigned coach | Validate exercise, equipment, context, comparability and factual coaching narrative; identify sensitive or unsafe claims | Within five business days of assignment | Another coach may validate only with source access and a recorded handover; otherwise snooze |
| Piper | Member-experience owner for approved, personalised outreach and follow-up; never combine asks | Within five business days after approval | A Peter-approved member-care cover; the assigned coach does not inherit outreach automatically |
| Peter | SOP owner, policy and capacity approval, final public-claim and publication approval, exception adjudication and pilot graduation | Weekly exceptions; monthly governance review | Public claims and new policy changes pause during absence unless Peter has named an authorised delegate in writing |
| System steward | Maintain rule versions, source contracts, test evidence and shadow reports | Before each scheduled run | Peter nominates the steward; technical failure cannot silently fall to Admin Eve |

### Proposed Monthly Capacity

Capacity is intentionally conservative and is a ceiling, not a target.

| Stream | Candidate review ceiling | Approved outreach ceiling after pilot | Expected output |
|---|---:|---:|---|
| Honest Google review | 12 per month | 8–12 requests per month | Measure confirmed published matches, not star average |
| Written results asset | 6 per month | 2 member asks per month | Aim for 1–2 approved written assets per month |
| Video testimonial | 4 per month | 1 member ask per month | Aim for one usable video every one to two months |

If a member qualifies for more than one stream, only one ask may be approved in the 60-day period. Capacity is reduced rather than filling a quota with a weaker candidate.

### Expected Staff Workload

| Activity | Admin Eve | Coaches | Piper | Peter |
|---|---:|---:|---:|---:|
| Weekly shadow report review | 45–60 min | 20–40 min total | 15–20 min | 15–20 min |
| Monthly governance and capacity review | 30 min | 15 min | 20 min | 30–45 min |
| One written asset that proceeds | 15–20 min | 20–30 min | 20–30 min | 20–30 min approval |
| One video that proceeds | 15–20 min coordination | 20–30 min | 30–45 min member coordination | 20–30 min approval |

Target steady-state governance workload is approximately 2–3 Admin Eve hours, 1.5–2 coach hours, 1.5–2 Piper hours and 1–1.5 Peter hours per month, excluding filming and editing.

### Alternatives Considered

- **Extend the current 4–5-star workflow:** Rejected because the selection gate is incompatible with neutral review solicitation.
- **Use retention status or coach enthusiasm to select review candidates:** Rejected because these signals can become proxies for predicted positivity.
- **Put all three asks in one GHL workflow:** Rejected because eligibility, consent, messaging and outcomes differ, and one workflow would increase accidental multiple asks.
- **Create a second Trainerize extraction service:** Rejected because the longitudinal audit and active-member reporting already provide the required evidence layer.
- **Use an LLM to score review likelihood:** Rejected. Review eligibility must be deterministic and independent of likely sentiment.
- **Use an LLM to invent personalised evidence language:** Rejected. Drafts may assemble validated facts and member-owned quotes only.
- **Store everything in GHL:** Rejected because source snapshots, consent versions, claim evidence and model feedback need a durable restricted audit history.
- **Store everything in a Google Sheet:** Rejected as the system of record because identified evidence, audit history and concurrency controls are better handled in a private ledger. A protected Sheet may become a staff review surface only after explicit approval.
- **Auto-send after the pilot:** Rejected from this scope. The safe next state is human-approved manual sending.
- **Restore the sentiment-gated workflow if the new system fails:** Rejected. Rollback is manual-only review outreach or no outreach, not a return to selective positive solicitation.

### Open Questions Requiring Peter’s Approval

1. Confirm the proposed ownership model: Admin Eve as queue and Google-match owner, assigned coach as evidence validator, Piper as member outreach owner and Peter as final policy/publication authority.
2. Confirm named absence cover for Admin Eve and Piper. Confirm whether public claims pause during Peter’s absence or whether Megan is an authorised coaching-fact delegate.
3. Approve the 60-day global ask cooldown, 365-day unconfirmed Google-request cooldown and 180-day written/video no-response cooldown.
4. Approve the monthly capacity ceilings. They must remain capacity controls, not staff review quotas.
5. Decide whether the existing onboarding review workflow should be paused immediately after the plan is approved, or remain live until the replacement neutral workflow passes testing. The current 4–5-star public-link gate should not remain the long-term model.
6. Approve the proposed neutral milestones, particularly whether 90 days should be the earliest milestone or whether six months is more appropriate.
7. Decide whether former members can enter a later phase. The recommended eight-week pilot includes active members only.
8. Approve the consent/release scope and obtain Australian privacy/legal review before sensitive health information or paid advertising rights are used.
9. Confirm whether the pilot review surface remains a local restricted report or, after plan approval, a protected allowlisted Google Sheet. No Drive write is assumed.
10. Decide whether the production service should read the Retention Intelligence PostgreSQL database through a read-only role or consume a small authenticated evidence endpoint. Direct shared-database access is simpler; an API creates a cleaner boundary.
11. Approve whether review confirmation should remain weekly manual Google Business Profile inspection. No reliable automatic reviewer-to-member identity match has been established.
12. Decide whether Peter must approve every public asset indefinitely or only during the pilot and first three months after graduation.

---

## Step-by-Step Tasks

Execute these tasks in order during implementation.

### Step 1: Record Approval Boundaries and Freeze Live Scope

Create an implementation decision record from Peter’s answers to the open questions.

**Actions:**

- Record approval date, approved owners, covers, cooldowns, milestones, capacity and pilot review surface.
- Record that no GHL, Railway, Drive, member-contact or public-system action is permitted until separately reached in the plan.
- Snapshot the current review workflow configuration, pipeline stages, tags, field values, enrolment counts and execution behaviour read-only.
- Snapshot the current story automation, published results index and member-story inventory.
- Mark the roadmap item In Progress only when Peter approves implementation.

**Files affected:**

- `plans/2026-07-27-member-advocacy-evidence-engine.md`
- `context/roadmap.md`
- `outputs/systems/member-advocacy-evidence-engine.md`

### Step 2: Create the Canonical SOP Before Staff Work

Write `reference/sops/member-advocacy-and-evidence.md` as version 1.0.

**Actions:**

- Define purpose, scope, non-goals and the three separated streams.
- Define all eligibility, exclusion, scoring and suppression rules.
- Define Admin Eve, coach, Piper, Peter and system-steward roles, deadlines and absence cover.
- Define review matching, coach validation, evidence confidence and claim wording.
- Define consent capture, release versions, withdrawal, expiry and minor/guardian rules.
- Define `approve`, `snooze`, `decline` and `wrong recommendation` actions and reason codes.
- Define no-response, DND, member-requested contact holds, complaint, cancellation, injury, medical, identity ambiguity, stale-data and system-failure exceptions. State explicitly that complaint or service-recovery sentiment cannot affect Google eligibility.
- Define the written and video production workflow, editorial approval, publication, correction and takedown procedure.
- Define weekly, monthly and quarterly reporting.
- Add related documents and a revision history table.
- Apply forward-facing formatting rules: no em dashes and no more than two sentences per paragraph.

**Files affected:**

- `reference/sops/member-advocacy-and-evidence.md`

### Step 3: Create the Consent and Release Standard

Create the controlled release template and have its privacy language reviewed before use.

**Actions:**

- Give every release a unique ID, version, member identity, date, capturing staff member and evidence/publication record link.
- Separate permission for written quote, training metric, body-composition result, image, before/after image, video and sensitive health detail.
- Separate approved channels: website, email, organic social, YouTube, paid advertising and internal training.
- State that participation is optional, does not affect service and is not rewarded.
- Let the member approve exact wording and assets before publication.
- Define withdrawal and correction handling without promising removal from third-party archives already outside The Evolved’s control.
- Include guardian consent and young-person assent for under-18 members.
- Do not expose private source IDs on the member-facing copy.

**Files affected:**

- `reference/member-advocacy-consent-and-release.md`
- `reference/sops/privacy-policy.md` only after approved privacy review

### Step 4: Reconcile Identity and Source Contracts

Define one versioned input contract without creating another source extractor.

**Actions:**

- Reuse exact email, GHL contact ID and Trainerize user ID from reconciliation.
- Reuse owner-approved identity crosswalks; fail closed on ambiguous identities.
- Add a versioned Trainerize evidence export containing source timestamp, canonical movement, raw exercise name, baseline and current result, dates, calculation method, comparable status and caveat.
- Reuse GHL member status, service, owner, membership start, review workflow state, Review Pipeline state, DND, last inbound/outbound communication and known advocacy asks.
- Use exact verified membership dates for tenure. Appointment or tracked-workout spans may support a milestone only when explicitly labelled and not represented as continuous membership.
- Reconcile story names to a stable story/asset ID. Do not automatically match duplicate names.
- Document whether production will use a read-only Retention Intelligence database role or endpoint.

**Files affected:**

- `member_advocacy_shadow/source_contracts.py`
- `member_advocacy_shadow/identity.py`
- `scripts/trainerize_performance_reporting.py`
- `scripts/test_trainerize_performance_reporting.py`
- `outputs/systems/trainerize-reporting-reconciliation.md`

### Step 5: Build the Private Advocacy Ledger

Create the local SQLite schema with PostgreSQL compatibility for a possible later Railway phase.

**Actions:**

- Create tables for runs, members, source snapshots, milestones, recommendations, evidence items, suppression decisions, consent/releases, staff feedback, outreach events, Google matches, assets and publications.
- Store immutable recommendation and evidence versions.
- Make rerunning the same source snapshot idempotent.
- Restrict local directory and file permissions.
- Keep names, emails, GHL IDs and Trainerize IDs out of logs and committed outputs.
- Add retention and deletion rules consistent with the approved privacy policy.

**Files affected:**

- `member_advocacy_shadow/state_store.py`
- `member_advocacy_shadow/models.py`
- `member_advocacy_shadow/tests/test_state_store.py`
- `data/private/member-advocacy/` at runtime only

### Step 6: Implement Neutral Google-Review Eligibility

Build the deterministic rule engine and prove that sentiment cannot affect it.

**Actions:**

- Implement required milestones and hard exclusions.
- Add legacy-review enrolment, prior request, confirmed review, global cooldown, DND, member-requested contact hold, legal/safety, identity and stale-source suppression.
- Exclude satisfaction ratings, First 7 Days sentiment, retention classification, strength improvement and coach commentary from eligibility and ordering.
- Generate an honest-review draft with no promised benefit, requested rating, prescribed text or request to change an existing review.
- Label every rejection with one or more reason codes.
- Test that changing a member from positive to negative sentiment does not change eligibility or ordering.

**Files affected:**

- `member_advocacy_shadow/eligibility.py`
- `member_advocacy_shadow/suppression.py`
- `member_advocacy_shadow/drafts.py`
- `member_advocacy_shadow/tests/test_google_eligibility.py`
- `member_advocacy_shadow/tests/test_suppression.py`
- `member_advocacy_shadow/tests/test_drafts.py`

### Step 7: Implement Results and Video Evidence Ranking

Build two distinct ranking models that output review candidates, not public claims.

**Actions:**

- Implement the approved scoring tables and version each model.
- Require comparable data for any proposed numeric training claim.
- Preserve low-baseline, stale-data, variant, estimated-1RM, selected-survivor and missing-reassessment caveats.
- Mask sensitive health details from general candidate views until explicit access and permission exist.
- Require coach validation before a recommendation can move to member outreach approval.
- Deduplicate people already represented by a published equivalent asset.
- Prefer proof-library coverage gaps without using protected or sensitive characteristics improperly.
- Add tests for extreme percentage changes, cross-exercise comparisons, Farmer Walk conventions, member-reported claims and unavailable bodyweight.

**Files affected:**

- `member_advocacy_shadow/evidence.py`
- `member_advocacy_shadow/scoring.py`
- `member_advocacy_shadow/tests/test_evidence.py`
- `member_advocacy_shadow/tests/test_scoring.py`

### Step 8: Implement Cross-Stream Suppression and Feedback

Create one member-level communication guard.

**Actions:**

- Enforce the 60-day global advocacy-ask period.
- Select one recommended next ask when a member appears in multiple streams.
- Record deferred streams and next eligible dates.
- Add approve, snooze, decline and wrong-recommendation actions.
- Use reason codes such as `already_reviewed`, `recent_ask`, `wrong_identity`, `data_not_comparable`, `coach_disagrees`, `member_not_suitable_now`, `existing_asset`, `sensitive_context`, `declined`, `capacity`, `other`.
- Require notes for wrong-recommendation and policy exceptions.
- Do not let feedback rewrite prior runs; append a decision event.

**Files affected:**

- `member_advocacy_shadow/suppression.py`
- `member_advocacy_shadow/state_store.py`
- `member_advocacy_shadow/tests/test_suppression.py`
- `member_advocacy_shadow/tests/test_state_store.py`

### Step 9: Build the Three-Part Shadow Report

Generate a restricted report every Monday without sending it automatically during local validation.

**Actions:**

- Show `SHADOW MODE: NO MEMBER CONTACT OR LIVE SYSTEM CHANGE` prominently.
- Create separate Google review, written results and video sections.
- Include all required recommendation fields, confidence, caveats, suppression and draft.
- Put suppressed candidates in a separate audit appendix rather than mixing them with actionable recommendations.
- Apply monthly capacity ceilings after eligibility and suppression.
- Show source freshness and report completeness.
- Create a de-identified aggregate summary for the workspace review log.
- Do not send the report to Admin Eve or write it to Drive until Peter approves the delivery surface.

**Files affected:**

- `member_advocacy_shadow/reporting.py`
- `member_advocacy_shadow/run_shadow.py`
- `member_advocacy_shadow/tests/test_reporting.py`
- `outputs/systems/member-advocacy-shadow-review-log.md`

### Step 10: Reconcile the Existing Story Library

Turn the current narrative file into a governed asset register without discarding useful stories.

**Actions:**

- Create one stable asset ID per unique member/story arc.
- Link duplicate transcript and story versions.
- Record source type, current public surfaces, Trainerize-evidence status, coach validator, claim status, consent/release ID, approved channels, approval date and withdrawal status.
- Mark legacy records `consent evidence to verify` when explicit release documentation is absent.
- Mark medical, causal, injury-resolution and sensitive-health wording for review.
- Reconcile the story library with the published Results CPT index and YouTube/video list.
- Do not unpublish or contact a member during the inventory step.

**Files affected:**

- `reference/member-stories.md`
- `outputs/systems/social-proof-pages.md`
- `outputs/systems/website-architecture.md`
- `outputs/systems/member-advocacy-evidence-engine.md`

### Step 11: Gate the Existing Publishing System

Update the publishing command and scripts only after the SOP, release and evidence records exist.

**Actions:**

- Add preflight requirements for asset ID, release ID/version, evidence record, coach validation, member wording approval and Peter publication approval.
- Stop before story writing when any gate is missing.
- Replace public em-dash instructions with compliant punctuation.
- Require dry runs for email and social distribution.
- Pass an immutable publication ID into notification and social scripts.
- Refuse live execution if the release does not cover the requested channel.
- Refuse captions containing unapproved numeric or sensitive claims.
- Record WordPress, email and social publication outcomes in the private ledger.
- Add correction and withdrawal handling across Results CPT, homepage, email templates and controllable social assets.

**Files affected:**

- `.claude/commands/add-member-story.md`
- `scripts/notify_story.py`
- `scripts/post_story_social.py`
- `reference/marketing-playbook.md`
- `outputs/systems/social-proof-pages.md`
- `outputs/systems/member-advocacy-evidence-engine.md`

### Step 12: Design the Future GHL State Without Applying It

Prepare a change specification and test fixtures, but do not mutate GHL during the shadow pilot.

**Actions:**

- Define minimal future contact fields: last advocacy ask date, last advocacy ask type, do-not-ask-until, Google review status, story consent status and video consent status.
- Reuse the current Review Pipeline for Google states where semantics remain valid.
- Define neutral workflow entry, exit, reply, re-entry and exception rules.
- Define Admin Eve’s weekly published-review match task only after ownership approval.
- Define Piper’s manually approved outreach task with the exact draft and one-ask warning.
- Define coach validation tasks with evidence links and no sensitive details in general task titles.
- Produce a live migration checklist, test contacts, expected-state checks and rollback.
- Do not remove/re-add `send review request`, publish workflows or create fields in this step.

**Files affected:**

- `outputs/systems/member-advocacy-evidence-engine.md`
- `outputs/systems/review-reputation.md`
- `outputs/systems/ghl-workflow-owner-review-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`

### Step 13: Run the Eight-Week Shadow Pilot

The pilot starts only after local tests pass and Peter confirms the pilot roster and review process.

**Actions:**

- Week 0: freeze rule versions, source contracts, capacity and reviewers.
- Weeks 1–8: generate one weekly report from current data without contact or live writes.
- Admin Eve reviews identity, prior outreach, review status and suppression.
- Coaches validate the highest-ranked written and video candidates.
- Piper reviews tone and member suitability but sends nothing.
- Peter reviews exceptions, proposed public wording and workload.
- Record approve, snooze, decline and wrong-recommendation feedback as shadow decisions only.
- At Weeks 2, 4, 6 and 8, calculate accuracy, duplicate prevention, data coverage, workload and candidate-yield metrics.
- Do not count hypothetical star rating or predicted positivity as a success metric.

**Files affected:**

- `data/private/member-advocacy/` runtime evidence
- `outputs/systems/member-advocacy-shadow-review-log.md`
- `context/roadmap.md`

### Step 14: Evaluate Pilot Gates

Produce a decision paper at the end of Week 8.

**Actions:**

- Compare every recommendation with human decisions and reason codes.
- Confirm zero same-period multiple asks and zero sentiment-based Google eligibility.
- Review false positives, identity ambiguity, stale evidence and staff workload.
- Confirm the projected live volume fits approved capacity.
- Decide `stop`, `revise and repeat shadow`, `graduate Google only`, or `graduate all three streams`.
- Obtain Peter’s explicit approval before any live system or member-contact stage.

**Files affected:**

- `outputs/systems/member-advocacy-shadow-review-log.md`
- `outputs/systems/member-advocacy-evidence-engine.md`
- `context/roadmap.md`

### Step 15: Apply Approved Live Changes in Controlled Stages

This step is future-authorised only. It cannot be inferred from plan approval alone.

**Actions:**

- Stage A: create approved GHL fields and manual tasks with send flags disabled.
- Stage B: migrate the Google-review workflow from the sentiment gate to neutral milestone recommendations on test contacts.
- Stage C: enable individually approved manual Google-review sends.
- Stage D: enable individually approved written/video outreach tasks.
- Stage E: enable publication execution after valid release and evidence approval.
- Verify every workflow state, field, task owner, suppression and test-contact outcome.
- Update live-system documentation immediately.
- Keep auto-send disabled.

**Files affected:**

- Live GHL only under separate explicit authorisation
- Future Railway service or Retention Intelligence contract only under separate explicit authorisation
- Approved Google Drive review surface only under separate explicit authorisation
- `outputs/systems/review-reputation.md`
- `outputs/systems/member-advocacy-evidence-engine.md`
- `outputs/systems/ghl-workflow-owner-review-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `CLAUDE.md`
- `context/roadmap.md`

### Step 16: Validate the Full Documentation Cascade

Close the task only when source, staff workflow, technical runbook and live records agree.

**Actions:**

- Verify the SOP version and revision history.
- Verify all downstream documents use the same roles, cooldowns, milestones, statuses and claim definitions.
- Verify the story command cannot bypass consent or evidence gates.
- Audit any affected trainer-portal content and quiz only if the SOP is added to staff course material.
- If trainer-portal content changes, complete the required Markdown, HTML, quiz and live GHL course cascade in the same authorised task.
- Update CLAUDE.md only for functionality that actually exists.
- Update the roadmap to the accurate final state.

**Files affected:**

- All files listed above
- Relevant trainer-portal sources only if Peter approves course inclusion

---

## Eight-Week Shadow Pilot Specification

### Pilot Scope

- Active members only.
- No auto-send and no manually sent pilot outreach.
- No GHL, Trainerize, Google Business Profile, Drive, Railway, WordPress, email or social writes.
- Weekly recommendation generation with monthly capacity ceilings.
- Two complete monthly capacity cycles observed within eight weeks.
- Existing live review journey treated as an input and suppression source, not changed by the pilot.

### Weekly Cadence

| Day | Activity | Owner |
|---|---|---|
| Monday | Generate restricted shadow report and source-health summary | System steward |
| Tuesday | Identity, DND, prior ask and Google status review | Admin Eve |
| Wednesday–Thursday | Validate top written/video evidence and caveats | Assigned coaches |
| Thursday | Review drafts, timing and member suitability | Piper |
| Friday | Decide approve/snooze/decline/wrong in shadow and resolve exceptions | Peter |

Unreviewed items carry forward as pending or snoozed. They do not disappear and are not replaced merely to fill a capacity ceiling.

### Pilot Success Metrics

#### Safety and Policy

- 100% of Google-review recommendations are produced without satisfaction, sentiment, result, retention or coach-positivity inputs.
- 100% of Google drafts ask for an honest review and contain no incentive, requested rating or requested content.
- 0 members appear as approved for more than one advocacy ask in a 60-day period.
- 0 identified member records appear in committed outputs or application logs.
- 0 public claims are marked ready without comparable evidence, coach validation and release scope.
- 0 live writes, member contacts or publications occur.

#### Recommendation Quality

- At least 95% of Google eligibility decisions are confirmed correct by Admin Eve.
- At least 80% of the top written-results candidates are confirmed as worthwhile evidence reviews by coaches.
- At least 70% of the top video candidates are confirmed as plausible story conversations by coach and Piper review.
- Fewer than 10% of all rows are `wrong recommendation` because of identity or already-known review/story state by Week 8.
- 100% of wrong recommendations have a reason code that can change a rule, source or inventory.

#### Data and Operations

- At least 95% of in-scope active members resolve to one unambiguous GHL–Trainerize identity or an explicit exception.
- 100% of recommendations show source freshness, confidence, caveats, owner, cover, suppression and draft.
- Weekly Admin Eve review remains within 60 minutes after Week 2.
- Total combined coach review remains within 40 minutes weekly at the proposed capacity.
- No failed source run overwrites the latest successful report.

#### Capacity and Expected Yield

- The engine can surface up to 12 compliant review candidates, six written candidates and four video candidates per month without weakening evidence thresholds.
- The human-approved live projection does not exceed 8–12 review asks, two written asks and one video ask per month.
- A shortage of valid candidates is treated as a healthy constraint, not a model failure.

### Post-Launch Outcome Metrics

These are defined now but not measured in the no-send pilot:

- honest review requests approved, sent and delivered;
- confirmed published Google reviews matched;
- unmatched and possible-match reviews;
- opt-outs, complaints and duplicate-contact incidents;
- written/video outreach accepted, declined, snoozed and unanswered;
- consent completion and withdrawal;
- coach-validated claims converted into approved assets;
- time from candidate to publication;
- approved written assets and usable videos produced;
- publication corrections or takedowns; and
- staff time per completed asset.

Google star average, positive-review rate and “reviews per staff member” are not staff success metrics.

---

## Communication, Consent and Publication Workflow

### Google Review

1. Neutral milestone eligibility passes.
2. Global and Google-specific suppression passes.
3. Admin Eve verifies identity, no known existing review and no legacy-review collision.
4. Peter or the authorised approver approves the individual draft during early live operation.
5. Piper sends the honest-review request through the approved channel.
6. Admin Eve records sent date and workflow evidence.
7. Admin Eve checks the public Google profile weekly.
8. A visible, defensibly matched review becomes `confirmed`; ambiguity remains `possible match`.
9. The result does not automatically trigger a written or video ask. The 60-day global cooldown applies.

### Written Results Asset

1. Evidence score places the member in coach review.
2. Coach validates the source record, comparability, context and proposed caveats.
3. Admin Eve confirms suppression and existing asset state.
4. Piper sends a separate optional conversation request.
5. If the member is interested, capture the approved release and story interview.
6. Draft only from verified records and member-owned statements.
7. The member approves exact wording, statistics, images and channels.
8. Peter approves the final public asset.
9. `/add-member-story` publishes and distributes under the release scope.
10. Publication IDs and URLs are recorded; withdrawal handling remains available.

### Video Testimonial

1. Video ranking places the member in coach review.
2. Coach validates facts and confirms a distinct story worth exploring.
3. Admin Eve confirms suppression and no conflicting asset request.
4. Piper makes a separate optional video conversation request.
5. Capture video-specific release before filming and final asset approval after editing.
6. Avoid coaching the member to state medical, causal or guaranteed outcomes.
7. Member approves the final edit and channels.
8. Peter approves public use.
9. Publish through the existing story and social system only within the release scope.

---

## Google Review Matching

### Statuses

| Status | Definition |
|---|---|
| `unknown` | No reliable request or public-review evidence |
| `eligible_not_requested` | Neutral eligibility passes, no request sent |
| `requested` | Approved request was sent with date and channel |
| `link_clicked` | GHL link-click evidence exists; publication not proven |
| `possible_match` | Public review resembles the member identity but cannot be confirmed safely |
| `confirmed` | Admin Eve can defensibly match the visible public review to the member |
| `not_found` | Checked after the defined window and no match found |
| `declined_or_opted_out` | Member declined or requested no further review outreach |

### Matching Rules

- Prefer an exact public display-name match plus compatible timing and a known request.
- A common first name, initials or narrative similarity alone is not enough for automatic confirmation.
- Do not use review text to infer sensitive health identity.
- Do not ask a member to prove a review was positive.
- Do not move `link_clicked` to `confirmed` without visible publication evidence.
- Keep an audit note of who matched the review and when.

---

## Exceptions and Stop Rules

- **Identity ambiguity:** Stop all outreach and assign Admin Eve review.
- **Existing review:** Suppress Google outreach. Do not ask for revision or removal.
- **Recent advocacy ask:** Suppress all streams until the next eligible date.
- **DND or opt-out:** Suppress the affected channel or all outreach according to the recorded request.
- **Complaint, cancellation or service recovery:** These may make a written or video story conversation inappropriate, but they cannot determine Google eligibility. Only a general member-requested contact hold or documented legal/safety restriction can defer the neutral Google ask.
- **Stale Trainerize evidence:** Candidate may remain visible, but no numeric public claim proceeds.
- **Exercise convention conflict:** Remove the disputed claim or obtain source and coach resolution.
- **Medical or causal wording:** Stop publication and rewrite to recorded fact or clearly attributed member experience; seek explicit sensitive-information permission.
- **No consent evidence for an existing asset:** Mark for verification. Do not expand it to new channels.
- **Withdrawal:** Stop new distribution, remove controllable surfaces within the SOP deadline and record any third-party limitations.
- **Staff absence:** Route to the named cover. If no cover is named, snooze rather than leave a hidden queue.
- **Capacity exceeded:** Defer lower-ranked candidates; do not weaken thresholds.
- **Source failure:** Retain the last successful report, mark it stale and produce no new recommendations.

---

## Rollback and Recovery Controls

### Shadow Mode

- `SHADOW_MODE=true` is mandatory.
- No GHL, Trainerize, Google, Drive, Railway, email, SMS, WordPress or social mutation client is implemented.
- All future send/write flags default false and the application refuses unsafe combinations.
- A failed run cannot replace the latest completed run.
- Disable the local schedule to stop the pilot; retain the ledger for audit.

### Future Live Mode

- Use separate flags for `GHL_STATE_WRITE_ENABLED`, `REVIEW_SEND_ENABLED`, `ASSET_OUTREACH_ENABLED`, `DRIVE_REVIEW_SURFACE_ENABLED` and `PUBLICATION_ENABLED`.
- Allowlist the exact GHL location, fields, workflows, Sheet and publication channels.
- Use expected-state checks before any GHL state transition.
- Keep an export of the pre-migration review workflow and pipeline state.
- If a live defect occurs, disable sends and return to manual-only operation.
- Do not restore the 4–5-star selective public-link gate as rollback.
- Do not delete consent, decision or publication evidence during rollback.
- Correct or withdraw affected public assets through the SOP rather than hiding the audit trail.

---

## Connections & Dependencies

### Files That Reference This Area

- `CLAUDE.md`
- `.claude/commands/add-member-story.md`
- `context/roadmap.md`
- `reference/member-stories.md`
- `reference/marketing-playbook.md`
- `reference/sops/privacy-policy.md`
- `outputs/systems/review-reputation.md`
- `outputs/systems/social-proof-pages.md`
- `outputs/systems/website-architecture.md`
- `outputs/systems/ghl-workflow-owner-review-register.md`
- `outputs/systems/ghl-team-task-trigger-register.md`
- `outputs/systems/membership-lifecycle.md`
- `outputs/systems/drive-process-audit.md`
- `outputs/systems/trainerize-reporting-reconciliation.md`
- `plans/2026-07-21-trainerize-longitudinal-strength-audit.md`
- `plans/archive/2026-05-07-story-email-notification.md`
- `scripts/notify_story.py`
- `scripts/post_story_social.py`
- `scripts/setup_story_custom_values.py`
- `scripts/trainerize_performance_reporting.py`
- `scripts/run_trainerize_reporting.py`
- `scripts/SETUP.md`

### External Policy Dependencies

- Google Maps contributed-content policy prohibits incentives, selective solicitation of positive reviews and requested review content.
- ACCC guidance requires reviews to reflect genuine independent opinion and warns against misleading review manipulation.
- OAIC guidance treats health information as sensitive and requires consent for direct-marketing use.
- The consent and privacy wording should receive Australian legal/privacy review before the engine uses sensitive information publicly or for paid advertising.

Official references:

- https://support.google.com/contributionpolicy/answer/7400114
- https://support.google.com/contributionpolicy/answer/16597558
- https://www.accc.gov.au/consumers/advertising-and-promotions/online-reviews-for-product-and-services
- https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/organisations/direct-marketing
- https://www.oaic.gov.au/privacy/your-privacy-rights/health-information/handling-health-information

### Updates Needed for Consistency

- The review system, roadmap and GHL owner register must use the same neutral eligibility rule and review-match semantics.
- The SOP, release, marketing playbook and story command must use the same claim hierarchy and channel permissions.
- The Trainerize reporting contract and advocacy evidence checks must share canonical movement mapping and caveats.
- The member-story register, Results CPT index, homepage assets and videos must share stable asset IDs.
- Staff-facing trainer-portal material must be cascaded only if the process is added to training.
- CLAUDE.md must be updated only after the system is implemented.

### Impact on Existing Workflows

- The current review journey remains a live input during shadow mode but cannot be the long-term Google-request path.
- First 7 Days satisfaction and service recovery remain valuable member-care processes, but they are separated from public-review eligibility.
- The existing story publication and distribution system remains intact, with new fail-closed gates before execution.
- Retention Intelligence remains the current identity/lifecycle/usage producer. The advocacy engine is a downstream consumer, not a second retention classifier.
- The Review Received verification ownership item can be resolved inside this workstream once Peter approves Admin Eve’s responsibility and cover.

---

## Validation Checklist

- [ ] Peter’s approved decisions, owners, covers, cooldowns, milestones and capacity are recorded.
- [ ] No implementation begins before plan approval.
- [ ] The canonical SOP exists at version 1.0 with revision history, roles, cover, exceptions and consent rules.
- [ ] The consent/release template is reviewed and supports granular channels and sensitive information.
- [ ] The engine consumes existing reconciliation and Trainerize evidence contracts without a duplicate extractor.
- [ ] Identified data stays under `data/private/member-advocacy/`.
- [ ] Google eligibility has no satisfaction, sentiment, result, retention or coach-positivity feature.
- [ ] Tests prove positive and negative satisfaction values produce the same Google eligibility.
- [ ] Every review draft asks for an honest review and offers no incentive.
- [ ] Every recommendation contains evidence, confidence, caveats, suppression, owner, cover and a draft.
- [ ] One global 60-day advocacy cooldown prevents multiple asks.
- [ ] Written and video candidates cannot reach outreach approval without coach validation.
- [ ] Public numeric claims require comparable source records.
- [ ] Medical and causal claims fail closed.
- [ ] Sensitive information remains masked until explicit permission exists.
- [ ] Google link clicks remain distinct from confirmed published reviews.
- [ ] Approve, snooze, decline and wrong-recommendation feedback is append-only and reason coded.
- [ ] The story library is reconciled to stable asset IDs and public surfaces.
- [ ] The story command refuses to publish without release, evidence and approval.
- [ ] Email and social scripts refuse channels not covered by the release.
- [ ] Shadow reports are clearly separated into three recommendation streams.
- [ ] The pilot produces no live write or member contact.
- [ ] Eight weekly runs are reviewed and retained.
- [ ] Pilot metrics and staff workload meet the graduation gates.
- [ ] Peter gives a separate explicit approval before each live stage.
- [ ] GHL, Railway, Drive and public-system documentation is updated immediately after any authorised live change.
- [ ] CLAUDE.md and the roadmap reflect only completed reality.

---

## Success Criteria

The implementation is complete when:

1. A canonical SOP and approved consent/release govern every staff action, exception, claim and publication.
2. The shadow engine produces three separate, evidence-backed recommendation queues with no sentiment-based Google eligibility.
3. Every recommendation is explainable, suppressible, owned, covered and auditable.
4. The same-period communication guard prevents any member from receiving multiple advocacy asks.
5. The engine reuses existing Trainerize analysis, reconciliation and story publication systems without duplicating them.
6. The eight-week shadow pilot completes with zero live writes or contacts and meets the defined safety, accuracy and workload gates.
7. Peter explicitly decides whether to stop, revise or graduate each stream.
8. Any graduated live workflow remains human-approved, consent-controlled and auto-send disabled.
9. Google reviews are matched to visible publication evidence rather than link clicks.
10. Public results and videos use comparable evidence, coach validation, member approval and valid release scope, with no unsupported medical or causal claims.

---

## Notes

This plan deliberately separates “a good candidate to review” from “a claim ready to publish.” Trainerize can identify where human attention is valuable, but it cannot determine consent, member meaning, clinical causality or editorial appropriateness.

The most important immediate decision is the current Google-review workflow. The existing sentiment gate conflicts with the proposed neutral model and current Google policy. Shadow design can proceed without changing it, but a compliant future-state migration should not be deferred indefinitely once Peter approves the workstream.

The current member-story library is commercially valuable but needs a retrospective provenance and consent audit. Existing public material should not be presumed unsafe, yet the statement that every story is verified and approved is not sufficiently evidenced by the current file structure.

Auto-send, automated public review scraping, automated member-story publication and predictive positive-review scoring are explicitly excluded.
