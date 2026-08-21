# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Is

This is a **Claude Workspace Template** — a structured environment designed for working with Claude Code as a powerful agent assistant across sessions. The user will spin up fresh Claude Code sessions repeatedly, using `/prime` at the start of each to load essential context without bloat.

**This file (CLAUDE.md) is the foundation.** It is automatically loaded at the start of every session. Keep it current — it is the single source of truth for how Claude should understand and operate within this workspace.

---

## The Claude-User Relationship

Claude operates as an **agent assistant** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **User**: Defines goals, provides context about their role/function, and directs work through commands
- **Claude**: Reads context, understands the user's objectives, executes commands, produces outputs, and maintains workspace consistency

Claude should always orient itself through `/prime` at session start, then act with full awareness of who the user is, what they're trying to achieve, and how this workspace supports that.

---

## Behavioural Defaults

Claude operates as a strategic board-level partner within this workspace.

Claude should:

- Challenge assumptions when appropriate
- Pressure-test growth ideas against data
- Identify second-order consequences
- Quantify impact where possible
- Prioritise leverage and system-level improvements over surface tactics
- Default to revenue expansion and utilisation optimisation when trade-offs exist

Claude should not:

- Act as a passive summariser
- Offer generic advice disconnected from current metrics
- Reinforce assumptions without scrutiny
- Suggest discounting or price undercutting

---

## Workspace Structure

```
.
├── CLAUDE.md              # This file — core context, always loaded
├── .claude/
│   └── commands/          # Slash commands Claude can execute
│       ├── prime.md       # /prime — session initialization
│       ├── create-plan.md  # /create-plan — create implementation plans
│       └── implement.md   # /implement — execute plans
├── .agents/
│   └── skills/            # Reusable workspace skills, including the MBE West End print-request workflow
├── .github/
│   └── workflows/         # Repository validation, including the Claude/Codex instruction-drift check
├── context/               # Background context about the user and project
│   └── journal/           # Daily journal entries written by Discord bot (/journal command)
├── discord_bot/           # Discord bot — 24/7 mobile interface to workspace
│   ├── bot.py             # Main bot — handles messages, calls Claude API
│   ├── context_loader.py  # Builds system prompt from context/ files
│   ├── journal.py         # Generates daily summaries, writes to context/journal/
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile           # Railway process definition
│   └── railway.toml       # Railway deployment config
├── pt_booking_shadow/     # Railway PT continuity auditor, Admin Eve reporting, and Monday GHL-to-KPI booking/hour write-back
├── revenue_gap_control/   # Read-only active-client audit, exception register, and KPI cash bridge
├── retention_intelligence/ # Railway daily retention snapshots and explainable member-usage classifications
├── trainerize_performance/ # Railway read-only performance service plus Railway-only daily refresh worker
├── plans/                 # Implementation plans created by /create-plan
├── data/private/          # Git-ignored sensitive operational datasets and identity crosswalks; never upload directly
├── outputs/               # Work products and deliverables
├── data/private/          # Git-ignored identified operational datasets, including Strength Assessments
├── reference/             # Templates, implementation guides, and reusable patterns
│   ├── evolved-manual/                # AI-native coaching & delivery manual — single source of truth for all training content
│   │   ├── README.md                  # Index, content map, and AI instruction block
│   │   ├── 00-core-philosophy.md      # Mission, core promise, why The Evolved exists
│   │   ├── 01-strength-science.md     # Why women need strength — physiology and evidence
│   │   ├── 02-assessment-system.md    # Strength Assessment + Intro Sessions framework
│   │   ├── 03-strength-standards.md   # Live / Long / Perform standards
│   │   ├── 04-periodisation.md        # Programming principles and progressive overload
│   │   ├── 05-prime-system.md         # PRIME coaching cue system
│   │   ├── 06-life-stage-training.md  # Perimenopause, postpartum, and beyond
│   │   ├── 07-member-journey.md       # Full member journey map
│   │   ├── 08-retention-system.md     # Monthly check-ins, red flags, upgrades
│   │   ├── 09-trainer-standards.md    # Delivery standards and professional conduct
│   │   └── scripts/                   # Assessments, SOPs, case studies, templates
│   ├── evolved-heroine/               # Heroine asset production, storage, approval, and deployment rules
│   ├── sops/                          # Operational SOPs — source of truth for all service delivery
│   ├── avatar-ally.md                 # Ideal client avatar — demographics, psychographics, objections, tone guide
│   ├── brand-positioning.md           # Mission, vision, core values, differentiators, brand voice & visual identity
│   ├── product-offerings.md           # SGPT sessions, 1:1 PT, meal plans, online coaching — descriptions & USPs
│   ├── marketing-playbook.md          # Content pillars, Instagram framework, success story template, campaign workflow
│   ├── homepage-copy.md               # Approved copy for all homepage sections
│   ├── homepage-implementation.md     # WordPress/Blocksy build guide (CSS, JS, CPT setup)
│   ├── faq-library.md                 # Full FAQ library (50+ Qs, goal-tagged, live/pending status)
│   ├── member-stories.md              # 24 member stories with decades, drivers, and blurbs
│   ├── infographic-sarcopenia-data.md # Data + JS for sarcopenia muscle loss chart
│   ├── infographic-frequency-data.md # Data + JS for training frequency chart
│   └── conversion-funnel.md           # Overarching funnel strategy — waitlist flow, CTA copy rules, landing page architecture
└── scripts/               # Automation scripts
    ├── update_metrics.py  # Reads KPI + active rosters → writes governed Markdown and JSON metrics
    ├── build_executive_brief.py # Builds aggregate report health + decision brief
    ├── upload_pt_minder_snapshot.py # Validates and uploads a manual PT Minder export to the Railway hub
    ├── verify_pt_minder_capture_gate.py # Preflights the second independent purpose-aware PT Minder capture before upload and parity
    ├── run_revenue_gap_control.py # Refreshes read-only payment and booking evidence, then generates the active-client audit and KPI cash bridge
    ├── sheets_client.py   # Google Sheets API auth + read helper
    ├── insert_formulas.py # Writes COUNTIFS formulas to KPI tab (run --all to backfill)
    ├── patch_booking_rows.py # Writes source-breakdown formulas to KPI tab
    ├── run_trainerize_reporting.py # Runs read-only GHL/Stripe/Trainerize reconciliation and active-member performance reporting
    ├── build_trainerize_performance_bundle.py # Builds the bootstrap/recovery evidence bundle for the Railway performance volume
    ├── membership_reconciliation.py # Builds protected cross-system snapshots and an evidence-backed membership exception queue
    ├── build_membership_lifecycle_backfill.py # Builds confidence-labelled immutable lifecycle events and exact historical opening cohorts from existing evidence
    ├── audit-ghl-urls.py  # Scans GHL for hardcoded domain URLs (run before DNS migration)
    ├── audit_trainer_portal.py # Checks trainer-course Markdown, HTML, quiz CSV and practical sign-off consistency
    ├── sync_trainer_portal_derivatives.py # Regenerates quiz CSVs and HTML quiz blocks from canonical course Markdown
    ├── preview_trainerize_membership.py # No-write validation and action preview for existing assessment clients converting to membership
    ├── redirects.conf     # Historical redirect draft; its blanket blog-host rule is unsafe and must not be installed
    ├── setup_story_custom_values.py # One-time setup: creates 6 GHL location custom values for story emails (run once, save IDs to .env)
    ├── create_hold_billing_control_fields.py # Idempotent setup for protected hold-intake and Billing OS acknowledgement fields
    ├── create_service_change_control_fields.py # Idempotent setup for governed membership service-change and canonical current-service fields
    ├── discover_service_change_prices.py # Read-only Stripe catalogue discovery for approved service-change targets
    ├── ensure_service_change_stripe_offers.py # Explicit-apply, idempotent Stripe catalogue setup for approved service-change offers
    ├── inspect_service_change_workbook.py # Read-only Brown & Casserly workbook schema verification for service-change integration
    ├── verify_billing_exception_task_live.py # Safe live test for same-day, deduplicated Admin Eve Billing OS exception tasks
    ├── verify_hold_intake_live.py # Temporary-contact live verification for first-request preservation and duplicate-hold rejection
    ├── verify_hold_return_guard_live.py # Disposable-contact proof of normal and cross-cycle Hold Return guards
    ├── verify_service_change_billing_live.py # Read-only proof of the exact Stripe service-change amount and Brisbane effective boundary
    ├── verify_service_change_exception_live.py # Disposable-contact proof that live service-change failures create one same-day, deduplicated Admin Eve task
    ├── check_agent_instruction_drift.py # Ensures AGENTS.md remains a small Codex pointer to canonical CLAUDE.md
    ├── check_evolved_standards_cascade.py # Validates every canonical Section 03b standard across governed local assessment and trainer-course surfaces
    ├── check_website_v2_drift.py # Read-only manifest, clean-source hash and optional live homepage verification for Website V2
    ├── notify_story.py    # Sends story email to matched GHL life-stage contacts + member "story is live" notification. Run after publishing a new story page. Requires GHL custom values + workflows set up first.
    ├── post_story_social.py # Posts member story to Facebook Page + Instagram Business. Uses Meta Graph API with system user token (never expires). Run after notify_story.py.
    ├── post_session_social.py # Posts session build-in-public screenshot to Instagram. Uploads local image to imgbb (public URL), then posts via Meta Graph API. Called automatically by /log-session when an image path is provided. Requires IMGBB_API_KEY in scripts/.env (free at imgbb.com/api).
    ├── trainerize_client.py # Reusable authenticated ABC Trainerize API client. Credentials live in scripts/.env.
    ├── test_trainerize_connection.py # Non-destructive Trainerize authentication check. Reports only aggregate client count.
    ├── extract_strength_assessments.py # Builds the private, versioned SQLite intake-strength dataset and assessment-date body-weight enrichment from Trainerize.
    ├── reconcile_trainerize_assessment_roster.py # Matches confirmed assessment emails to active/deactivated Trainerize accounts.
    ├── extract_trainerize_longitudinal.py # Resumable read-only roster, calendar, workout-detail and profile-history extractor for longitudinal strength outcomes.
    ├── trainerize_account_change_log.py # Prepares and reconciles controlled temporary Basic-client audit cohorts; every changed account must be restored.
    ├── analyze_trainerize_longitudinal.py # Produces confirmed-female longitudinal outcomes, movement-family progression, standards, marketing evidence and remarkable-result audit tables.
    ├── membership_reconciliation.py # Read-only GHL, Stripe and Trainerize identity snapshots and membership exception register.
    ├── trainerize_performance_reporting.py # Builds private active-member action views and aggregate workout/strength reporting.
    ├── run_trainerize_reporting.py # Runs membership reconciliation and performance reporting together; invoices are optional audit mode.
    ├── backfill_sa_attendance.py # Read-only confidence-labelled GHL-to-legacy attendance backfill; identified detail stays private.
    ├── verify_sa_rebook_guards.py # Read-only 20-case replay of the governed GHL rebooking stop/eligible rules; identified detail stays private.
    ├── manage_sa_rebook_guard_test_contacts.py # Creates, enrols, verifies and deletes non-deliverable controlled GHL contacts for rebooking-guard acceptance.
    └── build_trainerize_audit_workbooks.mjs # Builds and visually verifies the private and de-identified longitudinal, movement-family and marketing-evidence workbooks.
```

**Key directories:**

| Directory | Purpose |
| --- | --- |
| `.agents/skills/` | Reusable workspace workflows. `request-mbe-west-end-printing` validates artwork, prepares friendly instructions and submits confirmed print jobs through MBE West End's upload form. |
| `context/` | Who the user is, their role, current priorities, strategies, and AI instruction rules. Read by `/prime`. |
| `context/journal/` | Daily journal entries from Discord bot. Picked up by `/prime` automatically. |
| `context/evolved-method.md` | The Evolved Method — KPH, movement patterns, trainer logic. Foundation for all training copy and coaching. |
| `context/ai-instruction-block.md` | AI behaviour rules — terminology, coaching priorities, content rules, what not to do. Loaded during `/prime`. |
| `discord_bot/` | Discord bot — runs locally via macOS launchd. Provides 24/7 mobile access to workspace context. |
| `plans/` | Detailed implementation plans. Created by `/create-plan`, executed by `/implement`. |
| `data/private/` | Sensitive identified source data, local identity crosswalks, and private working files. Git-ignored; create a fresh de-identified derivative before sharing externally. |
| `outputs/` | Deliverables, analyses, reports, and work products. |
| `outputs/marketing-assets/` | Editable campaign masters and Canva-importable creative backups. |
| `outputs/systems/` | Business system documentation: blog, sales, membership lifecycle, lead gen, SA, social proof, website architecture, the current GHL backend register, and the Drive process audit. |
| `reporting_control/` | Shared reporting-period, unique-person, report-registry, commercial-evidence, live-roster candidate and executive-brief contracts. |
| `outputs/reporting-control-plane/` | Latest aggregate, share-safe Codex reporting brief in Markdown and JSON. |
| `operating_data_hub/` | Railway/Postgres shadow hub with governed cohort, lifecycle, person-linked service and roster terms, payment, entitlement, PT roster and Strength Assessment attendance reconciliation. Reporting V2 adds immutable event versions, Brisbane period logic, metric definitions/lineage, historical confidence, unique conversion, controlled manual inputs, a governed cash-event contract, protected shadow-only parallel-comparison ingestion, a non-publishing board-pack contract and an immutable metric-level publication/rollback registry. `workflow_extensions.py` provides the guarded accepted-decision and protected internal-task outbox contract governed by `outputs/systems/workflow-extension-registry.md`. Unchanged operational feeds still publish a fresh verified observation; owner-approved rules are governed configuration whose effective dates, not elapsed feed time, control applicability. The current KPI workbook remains the comparison system until metric-level acceptance gates pass. |
| `revenue_gap_control/` | Read-only Active SGPT/PT reconciliation and KPI cash-bridge controller. Identified outputs stay under `data/private/revenue-gap-control/`. |
| `outputs/trainer-portal/` | GHL trainer onboarding portal — .md source files and /html paste-ready files for all 12 courses. |
| `wordpress/website-v2/` | Governed clean source mirror for the already-built live Website V2. Read `outputs/systems/website-v2-release-manifest.md` before website planning or deployment. |
| `data/private/` | Git-ignored identified operational datasets. Strength Assessment extraction lives under `data/private/strength-assessments/`; never commit or expose individual records. |
| `reference/` | Helpful docs, templates and patterns to assist in various workflows. |
| `reference/evolved-manual/` | AI-native coaching and delivery manual — single source of truth for all training content. Stubs built, content to be migrated and expanded. |
| `reference/evolved-heroine/` | Source of truth for Heroine production, marketing use, and animation. Read its canonical README, marketing usage guide, animation-system specification, final generation prompt template, and active production register as applicable. Local files govern brand use, prompts, motion, and production history; Drive holds approved PNG masters; websites and campaigns use channel-specific deployment copies. |
| `reference/sops/` | Operational SOPs — source of truth for all service delivery procedures. |
| `scripts/` | Automation scripts. Includes KPI refresh, Trainerize data extraction, and read-only GHL–Stripe–Trainerize reporting and reconciliation; setup and usage live in `scripts/SETUP.md`. |

---

## Commands

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will:

1. Read CLAUDE.md and context files
2. Summarize understanding of the user, workspace, and goals
3. Confirm readiness to assist

### /migrate-ghl-page [path-to-ghl-html]

**Purpose:** Migrate a GHL funnel page to WordPress in a single pass.

Runs a structured 5-phase process: full content extraction → WordPress setup verification → complete HTML build → SSH push → visual verification checklist. Encodes all lessons learned (wpautop gotchas, card layout patterns, reviews iframe resize, overlay-link pattern).

This is a legacy compatibility command for an explicitly approved individual
page migration. It is not the Website V2 build workflow and must never be used
to reconstruct the existing V2 homepage or replace retained GHL operational
journeys.

Example: `/migrate-ghl-page /tmp/ghl-page.html`

### /add-member-story [member details]

**Purpose:** Add a new member transformation to every surface: individual story page, /results/ hub, homepage carousel, and member-stories.md.

Works through 10 phases: transcript pull (if video) → story HTML → photo upload → WP Results CPT page → archive-results.php → homepage carousel → homepage.js personalisation data → member-stories.md → cache flush → story email + social post. Includes validation checklist and quick-reference tables for goal/stage slugs.

Example: `/add-member-story Sarah, 34, postpartum, weight loss, lost 15kg in 6 months, YouTube: abc123, photo: sarah-30s-6m.png`

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Use when adding new functionality, commands, scripts, or making structural changes. Produces a thorough plan document in `plans/` that captures context, rationale, and step-by-step tasks.

Example: `/create-plan add a competitor analysis command`

### /update-metrics

**Purpose:** Pull live KPI data from the Google Sheet and refresh `context/current-data.md`, then summarise the key numbers.

Run before or during a session when you need current numbers. Requires credentials in `scripts/.env`.

Also available as a shell alias (`update-metrics`) for use outside Claude Code sessions.

### Discord bot (`#evolved-os` and `#daily-journal`)

**Purpose:** Mobile interface to the workspace — chat with a fully briefed Claude from any device.

- **`#evolved-os`**: Send any message → bot responds with full workspace context injected
- **`/journal`**: Summarises the day's conversation and posts to `#daily-journal`, also writes to `context/journal/YYYY-MM-DD.md`
- Deployed **locally** via macOS launchd (`~/Library/LaunchAgents/com.evolved.discord-bot.plist`) — starts at login, restarts automatically on crash.
- Running `update-metrics` on desktop immediately improves the bot's next response.
- To restart: `launchctl unload ~/Library/LaunchAgents/com.evolved.discord-bot.plist && launchctl load ~/Library/LaunchAgents/com.evolved.discord-bot.plist`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Reads the plan, executes each step in order, validates the work, and updates the plan status.

Example: `/implement plans/2026-01-28-competitor-analysis-command.md`

---

## Content Integrity Rules

These rules govern how **training content, SOPs, and trainer portal course material** are maintained. They apply when working on anything in `reference/evolved-manual/`, `reference/sops/`, or `outputs/trainer-portal/`. They do not apply to blog, marketing, GHL automation, or admin system work, which have their own independent content flows.

### Single Source of Truth

The update hierarchy is strictly:

```
reference/evolved-manual/  →  reference/sops/  →  outputs/trainer-portal/*.md  →  outputs/trainer-portal/html/  →  live GoHighLevel course
```

- Never update a course file without first updating the source SOP or manual section
- Never update an SOP without checking whether the relevant manual section needs updating
- Never update an HTML file without first updating the corresponding .md file

### Cascade Rule

Whenever an SOP or manual section is updated, Claude must:
1. Identify all downstream files that reference that content
2. Update them in sequence: SOP → .md → .html
3. Update the revision history table in the source file
4. Check all quiz questions in the affected course for accuracy

### Content Intake Rule

When new content is fed in by the user, Claude must:
1. Assess it against existing content — flag conflicts before making any changes
2. Update the source file first (manual section or SOP)
3. Cascade downstream
4. Never skip the assessment step — always confirm what's new, what conflicts, and what's being changed

### Quiz Integrity Rule

Any time course content changes, Claude must audit the quiz for that course before closing the task. No content change is complete until the quiz has been checked.

### Live GoHighLevel Synchronisation Rule

Any update to trainer portal course content, quizzes, assignments, titles, numbering, offers, prerequisites, or course-access sequencing must be applied to the front-facing GoHighLevel course in the same task.

Claude must:
1. Complete and validate the source-to-HTML cascade first
2. Immediately use the Browser tool to update the affected live GoHighLevel course, quiz, assignment, offer, or workflow
3. Save or publish the live change and verify the visible content, question or assignment count, publication state, and access path as applicable
4. Update the roadmap and relevant system documentation when the live structure or workflow changes

The task is not complete when only workspace files have been updated. The live update may be deferred only when the user explicitly requests a local-only change, or when browser access or authentication prevents the update; in that case, Claude must clearly record the outstanding live sync and must not mark the work complete.

### Revision History Rule

Every SOP in `reference/sops/` must have a revision history table at the bottom. When updating an SOP, always increment the version and add a row describing what changed and the date.

### Forward-Facing Content Formatting Rules

These rules apply to all trainer portal content, course lessons, SOPs, and any other content a trainer or member will read directly.

- **No em dashes.** Use colons, semicolons, or commas instead — chosen by context:
  - Introducing/expanding: colon
  - Joining independent clauses: semicolon
  - Parenthetical or list: comma
- **Maximum 2 sentences per paragraph.** If a paragraph exceeds 2 sentences, split it.
- **One empty line between paragraphs.** In HTML, use separate `<p>` tags with a blank line between them. Never run multiple sentences together inside a single `<p>` block.

---

## Roadmap

The master roadmap lives at `context/roadmap.md`. It is loaded automatically by `/prime`.

**Claude must update `context/roadmap.md` whenever:**
- A roadmap item changes status (e.g. Scoped → In Progress, In Progress → Live)
- Work is completed in a session — mark it Live or move to Completed
- An approved or explicitly scoped idea becomes governed work
- A dependency is resolved — update the next action for any unblocked items

Do not wait for the user to ask. Roadmap updates are part of closing any task.

Capture unapproved ideas in `context/idea-register.md`, not in the operational roadmap. An idea moves into `context/roadmap.md` only after its owner, intended outcome, canonical authority and next decision are explicit.

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change — adding commands, scripts, workflows, or modifying structure — ask:

1. Does this change add new functionality users need to know about?
2. Does it modify the workspace structure documented above?
3. Should a new command be listed?
4. Does context/ need new files to capture this?

If yes to any, update the relevant sections. This file must always reflect the current state of the workspace so future sessions have accurate context.

**Examples of changes requiring CLAUDE.md updates:**

- Adding a new slash command → add to Commands section
- Creating a new output type → document in Workspace Structure or create a section
- Adding a script → document its purpose and usage
- Changing workflow patterns → update relevant documentation

**What does NOT belong in CLAUDE.md:**

This file is loaded into every session. Keep it lean. Do NOT add:

- Page indexes, WP IDs, or slug tables — these go in `outputs/systems/website-architecture.md`
- Tables longer than ~5 rows that are only needed for specific tasks
- Data that is only relevant in fewer than half of sessions
- Anything that can be looked up on demand from `outputs/`, `reference/`, or the server

When in doubt: if it's a lookup table, it belongs in a reference file with a pointer here — not inline.

`AGENTS.md` is the Codex-compatible entry point, not a second source of truth. Keep permanent workspace guidance here in `CLAUDE.md`; keep `AGENTS.md` as a small pointer and run `python3 scripts/check_agent_instruction_drift.py` after changing either file. GitHub runs the same check on every push and pull request.

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Use commands or direct Claude with tasks
3. **Plan changes**: Use `/create-plan` before significant additions
4. **Execute**: Use `/implement` to execute plans
5. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

## Per-Request Zero-Drift Preflight

Before planning or taking action on every new user request:

1. Re-read `AGENTS.md` and `CLAUDE.md` completely, even when they were read earlier in the same session.
2. Identify the applicable canonical manual, SOP, workspace index and source hierarchy before using a downstream worksheet, course, derivative or live system as authority.
3. Compare the requested or supplied content with its upstream source. Stop and report any conflict, omission or stale derivative before making a workspace or live-system change.
4. Do not let a newer filename, recent output or user-supplied derivative silently outrank the canonical source unless the owner explicitly changes the source of truth.
5. After an approved change, cascade it through every governed derivative and live surface, update revision history and roadmap/build status, and verify that the source and downstream outputs agree.

Zero drift is the required operating standard. A task is not complete while its canonical source, trainer-facing derivatives, build documentation and verified live state disagree.

## Complete Live-System Investigation Rule

When investigating an individual contact, workflow, billing, booking or lifecycle exception, never conclude from one field, one screen or a partial workflow view. Reconcile the canonical SOP and system documentation against the complete live record: the submitted structured and free-text data, every relevant workflow branch and execution action, current fields and pipeline opportunity, pending and completed tasks, conversations and internal notes, authoritative billing evidence, and any downstream booking, access or reporting effect.

Record contradictions explicitly. A staff message promising an action is evidence that the case was discussed, not proof that the action was approved, processed or verified.

For the Evolved Standards Framework, `outputs/systems/evolved-standards-cascade-register.json` is the governed downstream register. Run `python3 scripts/check_evolved_standards_cascade.py` after any standard is added, renamed, removed or threshold-changed; the check must pass and registered live surfaces must be reverified before the change is complete.

---

## Cross-Workspace Governance

<!-- workspace-governance-standard-v1 -->

Before material work, read `.workspace-governance.json` and the Peter-owned standard at `/Users/peterbrown/peter-workspace/operating-system/workspace-governance-standard-v1.md`.

1. Classify the request as idea, research, proposal, approved implementation, live operation or status review.
2. Keep unapproved ideas in `context/idea-register.md`; they cannot change canonical references, the roadmap or a live system.
3. Record material owner rule decisions in `context/decision-log.md` and detailed domain evidence in the applicable plan or build record.
4. Complete the canonical-to-derivative-to-live cascade and domain validation before reporting completion.
5. Update `context/control-plane-status.md` after a material status change using only aggregate, share-safe information permitted by the manifest.
6. Run `python3 /Users/peterbrown/peter-workspace/tools/check-workspace-governance.py` after changing the manifest, instruction hook or registered status paths.

The Peter control plane coordinates attention and decisions. It does not own Evolved identities, payment, entitlement, lifecycle or metric calculations.

---

## Critical Instruction: Hub-First Systems

The governing architecture is `outputs/systems/reporting-control-plane.md`.

All reporting, reconciliation, intelligence, operational-control and dashboard work must target the shared Railway/Postgres operating-data hub.

Before creating or materially changing a report, automation, bot, dashboard or intelligence module, Claude must:

1. identify the canonical entities and authoritative sources;
2. confirm whether a current hub snapshot or contract already supplies the data;
3. reuse shared identity, payment, entitlement, lifecycle and reporting-period logic;
4. register the consumer, schedule, owner, freshness requirement and outputs;
5. define failure, stale-source, privacy and delivery-deduplication behaviour;
6. identify the legacy extraction, schedule or report that the change will retire;
7. create or update the architecture decision and migration plan before implementation.

Active source signal, confirmed active client, paid or entitled, and exception
or decision required are separate governed measures. GHL is authoritative for
lifecycle, payment events are authoritative for payment, and Trainerize is
access or engagement evidence only; count parity never substitutes for exact
identity-set parity.

A person is fully commercially verified only when every governed SGPT or PT
service relationship has compatible confirmed evidence. Entitlement exception
queue cases are evidence gaps, not automatic debts; identified cases remain
behind the protected hub API while executive surfaces remain aggregate.
Payment triage must keep no-current-payment evidence, an active contract without
a current receipt, PT booked with unresolved payment, and payment-current
booking gaps as separate actions.

Payment-purpose routing must also keep current PT Minder evidence awaiting
parity, a recent Stripe receipt without a paid-through end date, a paused
payment account with an active roster service, and a payment/service mismatch
separate. `SGPT` must not match the `PT` substring; Bronze, Silver and Gold
package descriptions are SGPT evidence, while explicit 1:1 or PT descriptions
remain personal-training evidence.

PT Minder transaction periods must be parsed from the exact `from` and `to`
dates in the debit description. A retry for an old service period cannot
outrank a completed debit covering the governed date. The legacy $149 weekly
or $298 fortnightly `Silver Package` is the composite Fast Track service and
can support both its SGPT and included weekly PT components, but remains in
shadow until the second independent PT Minder parity capture passes.

Stripe invoice payment events carry exact positive, non-proration line coverage
start and end dates. A dated commercial entitlement counts only when the
governed cohort date falls inside its effective window. A one-day invoice line
is a one-time payment event and cannot create ongoing membership entitlement
without a separately governed purchased-service term or access end date.
Purchased-service terms live in the protected PT/revenue Railway register and
must bind a unique term ID and Stripe invoice ID to the purchaser, beneficiary,
exact SGPT or PT service, effective dates and approval provenance. Approved
terms count only inside their window; revoked, incomplete, future and expired
terms cannot silently verify the current roster.
When one purchase is funded by multiple Stripe invoices, all invoice IDs must
be stored on one governed term. A deposit or balance payment must not
independently prove the complete entitlement.

An explicit PIF or PIA marker on the governed Active SGPT roster, paired with a
current or future renewal date, is current SGPT entitlement evidence only
through that renewal boundary. Google serial dates must be normalized at the
contract boundary. This rule does not prove a historical cash receipt and does
not apply to PT packs, which still require exact payment-to-beneficiary mapping.

Do not create:

- independent source extraction when a governed snapshot exists;
- local or Codex report schedules;
- competing client, payment, entitlement or KPI definitions;
- module-to-module private-table dependencies;
- Google Sheet logic that silently becomes a system of record;
- a new system without a named owner and retirement path.

Railway is the sole scheduling platform. Google Sheets, Discord, email, the CEO dashboard and generated reports are presentation or delivery surfaces, not competing systems of record.

---

## Website Architecture

**Canonical Website V2 authority:**
`outputs/systems/website-v2-release-manifest.md`

Website V2 is already built and live on WordPress at
`blog.theevolvedgym.com.au`. WordPress post ID 165 is the homepage, the current
primary CTA is `Join the Waitlist`, and the active delivery objective is to
promote that existing release to the root domain. Do not describe this work as
a rebuild or reopen the homepage source, no-navigation design, CTA journey or
membership presentation without explicit owner approval for a new redesign.

Before planning or changing any website surface:

1. read the V2 manifest, `reference/conversion-funnel.md`,
   `outputs/systems/website-architecture.md`,
   `outputs/systems/website-v2-ghl-route-register.json`,
   `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md` and the
   active root-promotion plan;
2. run `python3 scripts/check_website_v2_drift.py`;
3. compare the request with the live V2 product and governed source mirror at
   `wordpress/website-v2/source/`; and
4. stop and record drift before action when production, documentation and the
   mirror disagree.

After every authorised live V2 change, read back production, update the clean
source mirror and hash register, append the release register, update the
manifest if expected facts changed and rerun the local and live drift checks.
A release is not complete while those surfaces disagree.

GHL is retained operational infrastructure. It remains the CRM,
communications, workflow, form, funnel, calendar and booking platform.
The governed Phase 3 register contains a known lower bound of 85 GHL
paths. Preserve all of them on `go.theevolvedgym.com.au` through rehearsal and
the observation window. The 19 public root redirects are only a subset; they
are not permission to omit or delete the other configured steps.

**Domain map:**

| Domain | Platform | Purpose |
|---|---|---|
| `theevolvedgym.com.au` | Current GHL root | Older public root pending promotion of the existing Website V2 |
| `blog.theevolvedgym.com.au` | WordPress / SiteGround | Complete live Website V2 and current release runtime |
| `go.theevolvedgym.com.au` | Intended retained GHL host | Funnels, forms, booking pages and post-conversion journeys; no published DNS record at the 4 August Phase 3 audit |
| `links.theevolvedgym.com.au` | GHL | Short links, QR codes — unchanged |
| `evolved-woman.theevolvedgym.com.au` | Legacy GHL site | Retain until every live legacy route has a verified destination |

**Social proof pages:** WordPress CPT (`results`) at `/results/[goal-keyword-life-stage]`. Hub (`/results/`) uses `archive-results.php` (filterable by goal + life stage). Individual pages use `single-results.php`. Both templates in blocksy-child theme.

**Page index (WP IDs, slugs, Results CPT):** `outputs/systems/website-architecture.md`

**Root-promotion plan:**
`plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`

**Protected backlog:** Nora and Katrina trainer pages, the former Marnie
destination, legacy article imports/mappings, Results SEO repairs and the four
original unbuilt Results archetypes remain visible work. They are not automatic
root-promotion blockers unless Peter explicitly changes the gate.

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by type/purpose in `outputs/`
- Reference materials go in `reference/` for reuse
- PT appointment storage is non-negotiable: every booking block, reschedule and top-up uses separate GHL appointments with `isRecurring=false`; never create an open-ended or bounded recurring master. The default is 13 individual appointments per entitled weekly pattern, and any approved different count remains individual. Discover calendars from the governed registry of every current and retained 1:1 calendar, never from a displayed-name substring such as `PT`. Close a write only after proving exactly one individual appointment per target, zero duplicates and zero future recurrence for the affected service line.
- For active SGPT and PT payment audits, use `reference/sops/active-client-payment-and-booking-reconciliation.md` and the reusable worksheet at `outputs/systems/pt-weekly-audit-run-sheet.md`. Version 1.11 requires event-driven updates, a full line-by-line PT audit each Monday, a Friday cash bridge, a monthly SGPT plus PT pack and identity deep check, and quarterly formula validation. Fast Track retains a $99 SGPT component; its PT allocation is calculated from the approved weekly session count and recorded session rate, and the combined customer receipt is counted once. The read-only controller runs on Railway inside `PT Booking Shadow`; its production state and direct-deployment safety rule are documented in `outputs/systems/kpi-revenue-gap-controller.md`. The booking and revenue controllers share protected PTMinder/EziDebit evidence, approved identity links, account classifications and resolved PT commercial states from `/data/revenue-gap-control/`; do not independently recreate these decisions. PT Minder is payment-event evidence, not an accounts-receivable ledger: ignore displayed balances and its internal Charge function, and create only a retry action for a specific failed scheduled debit outside an approved hold. An open-ended hold contributes neither confirmed current nor scheduled income and retains only a periodic lifecycle follow-up. The complete V2 contract carries an explicit normalized weekly rate from the live schedule, so fortnightly collections, holds and pending adjustment debits cannot distort run-rate. Historical retry dates cannot replace a later current schedule, and products explicitly marked paused do not contribute collecting run-rate. PT Minder transaction evidence has separate service-type and cadence classifications: recurring revenue, variable cash and session entitlements must never be inferred from one another. Immutable PT Minder product labels must remain raw source evidence; when an owner-approved service correction is required, use the hub's agreement/account-keyed payment-service override register so every consumer receives the same audited projection. The first clean V2 parity cycle completed on 27 July 2026 at 24 of 24 exact; retain the protected input until a second independent owner-assisted capture also passes. Verified prepaid-pack beneficiaries use an explicit Railway-managed Stripe PaymentIntent-to-GHL-contact map before commercial entitlement reaches the hub; same-email one-off payments remain review evidence only. Effective governed purchased-service terms count as paid-in-advance and do not require recurring debit setup; evidence-backed approved pauses are reported separately from both confirmed collecting service and failed provisioning. `Session X/Y` evidence from GHL appointment descriptions or notes governs delivery review; contradictory sequences fail closed for Admin review and are not treated as a sessions-remaining balance. PT booking reconciliation protects exact recurring bookings before matching make-ups, excludes recorded hold windows, inherits approved pauses, and treats GHL-only active-PT signals as lifecycle review rather than automatic rebooking. Never infer a client-level booking gap from one trainer calendar: an exact contact, start time and duration in any approved PT calendar is valid coverage, with the expected and actual trainer calendars retained as audit evidence.

---

## SiteGround SSH Deploy

**WordPress root:** `/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html`
**SSH alias:** `evolved-prod` · **Homepage post ID:** 165
**Mandatory release authority:** `outputs/systems/website-v2-release-manifest.md`
**Deploy pattern + notes:** `outputs/systems/website-architecture.md`
