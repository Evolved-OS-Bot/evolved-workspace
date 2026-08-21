# Plan: GHL Backend and Drive Process Audit

**Created:** 2026-07-18
**Status:** In Progress
**Request:** Remove the obsolete booked-call sales pathway, audit the full GHL backend, and reconcile current operating processes from Drive into the workspace.

---

## Overview

### What This Plan Accomplishes

This plan removes acquisition and sales dependencies on booked phone calls, establishes a verified inventory of the GHL backend, and audits the operating documents in Drive folder `2. The Evolved`. Current, approved operational knowledge will be brought into the workspace's existing source-of-truth hierarchy without importing obsolete material wholesale.

### Why This Matters

The Evolved now converts through the in-person Strength & Longevity Assessment rather than booked sales calls. The backend and documentation must reflect that reality so inactive snapshot assets cannot be mistaken for live sales infrastructure, while current Drive-based procedures must be available to future agents and staff in the maintained workspace.

---

## Current State

### Relevant Existing Structure

- `outputs/systems/sales-conversion.md`: primary sales-system documentation.
- `outputs/systems/lead-generation-nurture.md`: lead sources, nurture workflows, forms, surveys, calendars, fields, values, tags, and flow maps.
- `outputs/ghl-account-documentation-2026-04-01.md`: historical point-in-time GHL inventory.
- `outputs/systems/`: operational system documentation by function.
- `reference/evolved-manual/` and `reference/sops/`: source-of-truth hierarchy for delivery and operational content.
- `context/roadmap.md`: current priorities, system gaps, and dependencies.
- Drive folder `2. The Evolved`: Brand, Marketing, Sales, Onboarding, Delivery, Retention, Cancellations, Team, Adjacent Products, and supporting files.

### Gaps or Problems Being Addressed

- Obsolete sales booked-call assets and references remain despite the move to Strength Assessments.
- Some local documents disagree about whether those assets are live, archived, or deleted.
- The April GHL inventory is historical and does not represent the curated July backend.
- Forms, surveys, fields, values, calendars, pipelines, tags, products, and other supporting assets have not yet received the same live governance audit as workflows.
- Operational processes remain distributed across Drive and the workspace, creating duplication and uncertain authority.

---

## Proposed Changes

### Summary of Changes

- Preserve cancellation and member-retention calls; remove only acquisition and sales booked-call assets.
- Inspect dependencies before any GHL status change.
- Unpublish and archive confirmed booked-call sales workflows.
- Record the status and disposition of related forms, calendars, fields, values, tags, and pipeline remnants.
- Create a current backend register that distinguishes live, retained-reference, inactive, and archive candidates.
- Inventory the Drive process tree, triage documents by currency and operational value, and migrate approved knowledge into existing source files.
- Update all downstream workspace documentation and the roadmap.

### New Files to Create

| File Path | Purpose |
|---|---|
| `plans/2026-07-18-ghl-backend-and-drive-process-audit.md` | Execution plan and progress record. |
| `outputs/systems/ghl-backend-register.md` | Verified current register for non-workflow GHL assets and their dependencies. |
| `outputs/systems/drive-process-audit.md` | Drive process inventory, triage decisions, source mappings, conflicts, and migration status. |

### Files to Modify

| File Path | Changes |
|---|---|
| `outputs/systems/sales-conversion.md` | Remove obsolete booked-call sales architecture and align the acquisition path to Strength Assessments. |
| `outputs/systems/lead-generation-nurture.md` | Remove booked-call sales dependencies and reconcile backend inventory. |
| `outputs/systems/membership-lifecycle.md` | Replace obsolete sales-channel language where required. |
| `outputs/systems/seminar-events.md` | Remove obsolete discovery-call conversion routes if confirmed inactive. |
| `context/roadmap.md` | Track the backend audit, Drive reconciliation, and any new operational gaps. |
| `CLAUDE.md` | Update only if the audit creates a new permanent workspace structure or operating workflow. |

### Files to Delete

No local source file will be deleted unless it is wholly obsolete and duplicated elsewhere. GHL assets will be archived rather than permanently deleted unless the user has already deleted them or a recoverable archive is unavailable.

---

## Design Decisions

### Key Decisions Made

1. **Sales-only scope:** `MC: Other (Booked Call)` and other retention/operational calls remain because they are not acquisition pathways.
2. **Strength Assessment is authoritative:** every live acquisition route should ultimately lead to the Strength & Longevity Assessment or a deliberate lead-nurture state.
3. **Dependency-first retirement:** workflows, forms, calendars, fields, values, tags, and pipeline stages are inspected for live references before retirement.
4. **Drive is an input, not automatically authoritative:** each document is compared with the workspace and live systems before migration.
5. **Migrate into existing sources:** current SOP content goes to `reference/sops/` or the relevant manual section first, then cascades downstream under the workspace integrity rules.

### Alternatives Considered

- Deleting every asset containing the word “call” was rejected because cancellation, retention, and staff calls remain valid.
- Copying the whole Drive folder into the workspace was rejected because it would import stale and duplicated material without resolving authority.
- Treating the April GHL export as current was rejected because several live statuses changed on 17 July 2026.

### Open Questions

No blocking questions at the start. Ambiguous assets will be retained and flagged rather than retired without evidence.

---

## Step-by-Step Tasks

### Step 1: Establish the booked-call dependency map

- Search local workspace references and the live GHL account.
- Separate sales/acquisition assets from cancellation, retention, coaching, and internal operational calls.
- Identify all workflow, form, calendar, pipeline, field, value, tag, email, SMS, funnel, and webpage dependencies.

### Step 2: Retire booked-call sales workflows

- Confirm exact workflow status and enrolment history.
- Unpublish any published sales booked-call workflow.
- Move confirmed obsolete workflows into the appropriate archive folder.
- Verify the status after each change.

### Step 3: Audit the complete GHL backend

- Inventory workflows, forms, surveys, calendars, opportunity pipelines and stages, custom fields, custom values, tags, products, payments, funnels/websites, email templates, trigger links, integrations, users, and task ownership where accessible.
- Classify each asset as Critical Live, Supporting Live, Retained Reference, Archive Candidate, or Unknown.
- Record dependencies, owner, evidence, and recommended action.

### Step 4: Audit Drive processes

- Traverse every direct subfolder of `2. The Evolved` and its operational subfolders.
- Record title, type, modification date, purpose, probable owner, and workspace counterpart.
- Prioritise Sales, Onboarding, Delivery, Retention, Cancellations, and Team procedures.
- Compare candidate content with live GHL behaviour and current workspace sources.

### Step 5: Reconcile and migrate current knowledge

- Flag conflicts before editing source material.
- Update the relevant manual or SOP source first.
- Cascade into trainer-portal Markdown and HTML when training content changes.
- Audit affected quizzes and revision histories under the content-integrity rules.

### Step 6: Clean workspace references

- Remove obsolete sales booked-call language and diagrams.
- Preserve factual history only in the audit record where necessary for traceability.
- Ensure no active acquisition documentation routes prospects to a phone call.

### Step 7: Close governance gaps

- Define the current owner and review cadence for critical GHL asset families.
- Update the roadmap with confirmed gaps, priorities, and dependencies.
- Decide whether `CLAUDE.md` needs a lean pointer to the new backend and Drive registers.

---

## Connections & Dependencies

### Files That Reference This Area

- `outputs/systems/sales-conversion.md`
- `outputs/systems/lead-generation-nurture.md`
- `outputs/systems/seminar-events.md`
- `outputs/systems/membership-lifecycle.md`
- `outputs/systems/review-reputation.md`
- `context/roadmap.md`
- `plans/2026-07-17-ghl-workflow-governance-audit.md`

### Updates Needed for Consistency

- Strength Assessment terminology must replace obsolete sales-call language.
- Historical IDs and retirement evidence belong in the audit register, not in forward-facing operating flows.
- Drive content changes must follow manual to SOP to trainer-portal Markdown to HTML order where applicable.

### Impact on Existing Workflows

No live Strength Assessment, cancellation, membership hold, story-distribution, purchase, or trainer-course workflow will be changed solely because it includes a legitimate non-sales call action.

---

## Validation Checklist

- [x] No active sales/acquisition workflow is triggered by or routes to a booked phone call.
- [x] Confirmed obsolete booked-call workflows are unpublished and archived.
- [x] Cancellation booked-call pathway remains published and unchanged.
- [x] Major GHL backend asset types have a current inventory and first-pass risk register.
- [ ] Every Drive process document has at least a triage disposition; the root and priority operational folders are mapped, with deeper document-by-document review queued.
- [ ] Migrated knowledge has passed source hierarchy, revision-history, downstream cascade, and quiz checks where applicable.
- [x] Workspace search finds no forward-facing booked-call sales instructions.
- [x] Roadmap and primary system documentation match live evidence.

---

## Success Criteria

1. Strength Assessment is the only documented primary acquisition appointment.
2. The current GHL backend can be understood without relying on the April snapshot export.
3. Current Drive processes are either represented in the workspace or explicitly mapped for migration, update, retention, or archive.
4. Critical assets have clear status, dependency, ownership, and next action.

---

## Notes

The phrase “booked call” may remain only where it describes the valid cancellation manager-call pathway or where the audit record needs to document a retired sales asset. It must not appear as an active acquisition recommendation.
