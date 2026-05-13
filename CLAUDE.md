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
├── context/               # Background context about the user and project
│   └── journal/           # Daily journal entries written by Discord bot (/journal command)
├── discord_bot/           # Discord bot — 24/7 mobile interface to workspace
│   ├── bot.py             # Main bot — handles messages, calls Claude API
│   ├── context_loader.py  # Builds system prompt from context/ files
│   ├── journal.py         # Generates daily summaries, writes to context/journal/
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile           # Railway process definition
│   └── railway.toml       # Railway deployment config
├── plans/                 # Implementation plans created by /create-plan
├── outputs/               # Work products and deliverables
├── reference/             # Templates, implementation guides, and reusable patterns
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
    ├── update_metrics.py  # Reads KPI sheet → writes context/current-data.md
    ├── sheets_client.py   # Google Sheets API auth + read helper
    ├── insert_formulas.py # Writes COUNTIFS formulas to KPI tab (run --all to backfill)
    ├── patch_booking_rows.py # Writes source-breakdown formulas to KPI tab
    ├── audit-ghl-urls.py  # Scans GHL for hardcoded domain URLs (run before DNS migration)
    ├── redirects.conf     # 301 redirect rules for blog subdomain → root domain migration
    ├── setup_story_custom_values.py # One-time setup: creates 6 GHL location custom values for story emails (run once, save IDs to .env)
    ├── notify_story.py    # Sends story email to matched GHL life-stage contacts + member "story is live" notification. Run after publishing a new story page. Requires GHL custom values + workflows set up first.
    └── post_story_social.py # Posts member story to Facebook Page + Instagram Business. Uses Meta Graph API with system user token (never expires). Run after notify_story.py.
```

**Key directories:**

| Directory       | Purpose                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| `context/`      | Who the user is, their role, current priorities, strategies. Read by `/prime`.      |
| `context/journal/` | Daily journal entries from Discord bot. Picked up by `/prime` automatically.    |
| `discord_bot/`  | Discord bot deployed on Railway. Provides 24/7 mobile access to workspace context. |
| `plans/`        | Detailed implementation plans. Created by `/create-plan`, executed by `/implement`. |
| `outputs/`      | Deliverables, analyses, reports, and work products.                                 |
| `reference/`    | Helpful docs, templates and patterns to assist in various workflows.                |
| `scripts/`      | Automation scripts. `update_metrics.py` reads the KPI sheet and writes `context/current-data.md`. Run via `update-metrics` alias. Running `update-metrics` on desktop is immediately reflected in the bot's next Discord response. |

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

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Use commands or direct Claude with tasks
3. **Plan changes**: Use `/create-plan` before significant additions
4. **Execute**: Use `/implement` to execute plans
5. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

---

## Website Architecture

**Domain map:**

| Domain | Platform | Purpose |
|---|---|---|
| `theevolvedgym.com.au` | WordPress / SiteGround | Homepage, blog (`/blog/`), social proof pages (`/results/`) |
| `go.theevolvedgym.com.au` | GHL | All funnels, booking pages, SA booking (`/strength-assessment`) |
| `links.theevolvedgym.com.au` | GHL | Short links, QR codes — unchanged |
| `blog.theevolvedgym.com.au` | 301 → root | All traffic redirects to `theevolvedgym.com.au/blog/` |

**Social proof pages:** WordPress CPT (`results`) at `/results/[goal-keyword-life-stage]`. Hub (`/results/`) uses `archive-results.php` (filterable by goal + life stage). Individual pages use `single-results.php`. Both templates in blocksy-child theme.

**Page index (WP IDs, slugs, Results CPT):** `outputs/systems/website-architecture.md`

**Still to build:** Nora trainer page. ~9 remaining results pages (see `outputs/systems/social-proof-pages.md`).

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by type/purpose in `outputs/`
- Reference materials go in `reference/` for reuse

---

## SiteGround SSH Deploy

**WordPress root:** `/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html`
**SSH alias:** `evolved-prod` · **Homepage post ID:** 165
**Deploy pattern + notes:** `outputs/systems/website-architecture.md`
