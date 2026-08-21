# Plan: GHL Workflow Governance and Curated Live Audit

**Created:** 2026-07-17  
**Status:** Complete  
**Closed:** 2026-08-05  
**Account:** The Evolved All Female Gym sub-account

## Objective

Build an accurate operating picture of GHL without turning the local workspace into a historical dump.

The audit will identify what is actively running, what materially affects members, revenue, staff workload, or risk, and what deserves a maintained source-of-truth document. Old, duplicate, test, and uncertain workflows will be quarantined outside the permanent knowledge base until a decision is made.

## What the New Browser Access Changes

The GHL API exposes workflow names, statuses, IDs, and dates, but not the actions inside workflows. The signed-in browser now allows read-only inspection of:

- Workflow triggers and filters
- Create Task actions
- Internal notifications
- Assignees and due dates
- If/Else branches and waits
- Tags, pipeline moves, forms, calendars, and linked workflows
- Published state and visible execution evidence

The browser will be used for action-level evidence. The API will remain useful for fast inventory and metadata checks.

## Governing Principle

Document the operating system, not the entire account history.

A workflow earns permanent workspace documentation only if at least one of these is true:

1. It is published and has current operational use.
2. It creates staff work or member communication.
3. It affects revenue, billing, retention, sales, compliance, or member safety.
4. It is a dependency of another active workflow, form, calendar, pipeline, or integration.
5. It represents a deliberate system we intend to maintain.

Anything else stays in a temporary audit register or a short quarantine list.

## Safety Rules

### Discovery is read-only

During the audit, do not:

- Edit workflow actions
- Publish or unpublish workflows
- Change assignees
- Delete or archive workflows
- Submit forms or create test contacts
- Complete or modify live staff tasks

Any later GHL change requires an explicit change list and user approval.

### No immediate deletion

Old-looking workflows move through this decision sequence:

`Unknown → Candidate Legacy → Dependency Check → Quarantine → Disable/Archive Decision`

Nothing is deleted during the first audit. A workflow can look dormant while still being called by a form, appointment status, tag, webhook, or Go To action.

### Protect member data

The permanent workspace will capture workflow logic, not member names, contact details, conversation content, or task instances.

## Classification Model

Every workflow inspected receives one classification:

| Class | Meaning | Workspace treatment |
|---|---|---|
| A: Critical Live | Billing, safety, sales, retention, cancellations, holds, or high-impact member communication | Full system documentation and owner |
| B: Active Operational | Used consistently and creates real team or member actions | Concise maintained documentation |
| C: Active but Low-Leverage | Running correctly but not strategically important | One-line entry in curated workflow register |
| D: Candidate Legacy | Old, duplicated, replaced, or apparently unused | Quarantine list only |
| E: Unknown | Purpose or dependency cannot yet be established | Temporary audit notes only |

## Evidence Standard

Classification will use multiple signals rather than the workflow name alone:

- Published or draft status
- Visible recent task creation or workflow execution
- Current forms, calendars, pipelines, tags, and fields referenced
- Links from or to other active workflows
- Current staff recognition of the process
- Match against existing Evolved OS documentation
- Last updated date as supporting context, not proof of use

An old update date does not make a workflow obsolete. A recently updated workflow does not automatically make it important.

## Audit Phases

### Phase 1: Portfolio Map

Create a temporary inventory of all 140 workflows using API metadata.

Capture only:

- Workflow name
- ID
- Published status
- Created date
- Updated date
- Initial folder or system grouping where visible
- Initial classification guess

This raw inventory remains temporary and is not committed as permanent workspace context.

### Phase 2: Live Task Audit

Start with workflows that create team tasks because they directly control staff workload and member follow-up.

For each Create Task action, capture:

- Workflow and business system
- Trigger and filters
- Branch conditions
- Delay before creation
- Task title and objective
- Assignee or routing rule
- Due time
- Related notification
- Exit condition or completion dependency
- Evidence that it is currently active

Update `outputs/systems/ghl-team-task-trigger-register.md` as the first operational deliverable.

### Phase 3: Critical Lifecycle Systems

Audit in this order:

1. Strength Assessment and sales conversion
2. Membership and PT holds
3. Cancellation and retention
4. Billing, failed payments, and payment recovery
5. New-member onboarding
6. Member check-ins, satisfaction, milestones, and red flags
7. Lead, waitlist, and re-engagement journeys
8. General marketing and low-risk nurture

This order prioritises revenue, member experience, staff workload, and risk.

### Phase 4: Existing Documentation Reconciliation

For each Class A or B workflow:

1. Identify the current local source document.
2. Compare live GHL logic against the document.
3. Record differences as one of:
   - Documentation stale
   - GHL implementation stale
   - Intent unclear
   - Assignment/routing mismatch
4. Update documentation only after the intended live behaviour is confirmed.
5. Add a concise revision note where the source document supports revision history.

Do not create a separate document for every workflow. Workflows belonging to one operating system should be documented together.

### Phase 5: Legacy and Duplicate Review

Candidate legacy workflows receive only a short review record:

- Name and ID
- Why it appears obsolete
- Known replacement, if any
- Dependency checks completed
- Last visible evidence of use
- Recommended action: retain, rename, disable, archive, or investigate

Only after user review should any GHL cleanup occur.

### Phase 6: Governance Setup

Introduce a lightweight standard for maintained workflows:

- Clear system prefix and workflow name
- One named business owner
- One local system document for the workflow family
- Trigger, task routing, and external dependency summary
- Last verified date
- Review cadence based on risk

Suggested review cadence:

| Workflow class | Review cadence |
|---|---|
| A: Critical Live | Quarterly and after any incident or policy change |
| B: Active Operational | Every six months |
| C: Active but Low-Leverage | Annually |
| D/E | Review during cleanup only |

## Permanent Deliverables

Only these curated outputs should remain after the audit:

1. **Team Task Trigger Register**  
   One operating view by assignee, trigger, due time, and responsibility.

2. **Curated GHL Workflow Register**  
   Class A, B, and selected C workflows only. One line per workflow with owner, purpose, status, and canonical system document.

3. **System Documentation Updates**  
   Existing files updated where live GHL differs from documented intent.

4. **Legacy Decision List**  
   A short, temporary decision document containing only workflows that need an explicit retain/archive decision.

The raw 140-workflow inventory and browser extraction notes should be discarded after reconciliation.

## Batch Method

Work in small batches so evidence remains reviewable:

- 10 to 15 workflows per batch
- Finish classification and reconciliation before starting the next batch
- End each batch with a short decision summary
- Update permanent documentation only for workflows that pass the retention test

Suggested first batch:

- Strength Assessment workflows that create Admin Eve or coach tasks
- Membership and PT hold workflows that create Admin Eve, coach, or owner tasks
- Cancellation workflows that create Piper tasks

These are already visible in current task activity and have the greatest immediate value for the team.

## Quality Checks

Before marking a system audited:

- Click `Fit to Screen`, then traverse the complete workflow canvas from trigger to every end node. Pan or scroll across all branches rather than treating the initially rendered viewport as the workflow.
- Reconcile the visible trigger, action, branch and end-node counts after the canvas has finished rendering. Repeat the snapshot after opening and closing an action panel because GHL virtualises off-screen nodes.
- Confirm every negative claim, such as “contains no task,” “does not call another workflow,” or “has only three actions,” with a second evidence source. Use execution logs, contact paths, destination workflow history, settings or an independent dependency trace.
- Record mirrored-branch parity explicitly. A workflow with two timing paths is incomplete until both branches have been checked.
- Mark the workflow `Revalidation Required`, not audited, if the full canvas cannot be traversed or the action count cannot be reconciled.
- Every Create Task action has an assignee and due time recorded
- Assigned User routing has been checked for the intended team role
- Notifications are not mislabelled as tasks
- Branch conditions that suppress or create tasks are recorded
- Dependencies on forms, calendars, fields, tags, pipelines, or other workflows are named
- Current GHL behaviour and local documentation have been reconciled
- No member-specific information has been copied into the workspace

## Mandatory canvas revalidation: 29 July 2026

The initial location-workflow inspection incorrectly treated the three rendered nodes as the complete builder. Execution history later proved that the off-screen workflow also enrolled contacts into Mobile Check, classified life stage, created spreadsheet rows, applied tags and started the matching delivery workflow.

This creates a targeted revalidation requirement rather than invalidating every completed audit action. Settings checks, execution-history findings, form and field changes, calendar work, deletions verified absent, and actions that were opened and edited directly remain supported. The high-risk conclusions are negative builder assertions and exact action counts based primarily on the canvas.

Revalidate in this order:

1. Class A workflow families where a missing task, branch, exit or dependency was asserted.
2. Class B workflows where “only,” “none,” “no trigger,” or “no caller” informed an operating decision.
3. Archived workflows where a negative canvas assertion materially supported retirement.
4. Class C workflows only where the conclusion affects a live dependency.

No workflow family should retain a `Live` audit status solely from an unreconciled visual-canvas inspection.

## Progress update: 22 July 2026

Phases 2–4 now cover the critical lifecycle, task, acquisition, PT, trainer, inbound communication and Conversations families. Phase 6 has started with the permanent owner and review register at `outputs/systems/ghl-workflow-owner-review-register.md`.

At the 22 July checkpoint, the visible `Needs review (3)` count appeared to be accounted for by two draft legacy Did Not Answer workflows and the published PT booking-field workflow. That interpretation was later superseded by the 29 July execution-error revalidation below.

The custom-field/custom-value retirement review is now documented in `outputs/systems/ghl-custom-data-governance-register.md`: 223 live custom fields contain no exact duplicate display names. The initial 32 custom values included ten blank template candidates and one deliberately reserved blank SA summary value. Peter approved the ten-value cleanup batch on 22 July 2026; all ten deletions succeeded and were verified absent, leaving 22 custom values with `SA: Conversation Summary` retained.

The shared `RE#1 - 30DNNC & SEMINAR` workflow had 10 waiting or processing enrolments, not 50; `50` was the history page-size selector. The first six of seven emails contain obsolete seminar and eight-week challenge copy, while the seventh uses the retained FEON resource. Peter subsequently approved retirement of all seminar workflows. `RE#1`, Transformation Seminar Interest and Transformation Seminar Attending were set to Draft and moved to `1. Pipeline Workflows / Archive` on 22 July 2026. The 10 `RE#1` enrolments remain visible as history but will not continue through the sequence while it remains Draft.

The funnel/template continuation found a three-step Workshop Funnel on the non-resolving `free.theevolvedgym.com.au` hostname, a standalone TransformationFLIX email template that links directly to Stripe, and two residual booked-call templates inside `[OLD] Call Booked Emails`. The initial blank-value title search returned no corresponding template names and was subsequently superseded by the complete body-level scan below. Page-level inspection then confirmed that every Workshop Funnel step was copied Impact School material unrelated to The Evolved. The funnel had no page views, opt-ins or sales in the latest 30-day window, no tracking events and no operational workspace reference. Peter approved deletion on 22 July 2026; the funnel and its empty folder were permanently deleted and verified absent.

The full body-level scan then traversed 28 folders and 290 rendered email templates. None used the ten blank custom values. Sixteen templates mentioned TransformationFLIX across the Metabolic Blueprint marketing, delivery and CTA folders; none consumed the TransformationFLIX custom value. Peter approved retirement on 22 July; all 16 templates and the custom value were deleted, and a fresh rendered-template scan returned zero matches. Thirteen unrelated marketing templates and the unrelated Week 8 delivery template were preserved. Four historical marketing templates used the seminar replay or slide-deck values, and their matching campaigns were all Sent in May 2025. Three had already been removed in the overlapping TransformationFLIX batch; the remaining `TCS - Non Member` template and both seminar custom values were subsequently deleted and verified absent. The two booked-call templates had no matching campaign and were permanently deleted with their folder; a fresh search returned no results. The reusable URL audit script was corrected to read GHL's current `builders` response, recurse through folders with `parentId` and scan rendered template bodies.

- No seminar or blank-value candidate has been changed without approval. The booked-call templates were deleted under Peter's existing instruction to remove acquisition booked-call references.

## Closure

The governance audit is complete. The final pass reconciled the live workflow library, forms and surveys, custom fields and values, tags, calendars, funnels, email assets, users and task ownership, opportunity pipelines, products and the current Admin, Sales and Delivery process documents in Drive. Material workflows were inspected across their complete canvases, not from the initially visible builder area alone. Approved cleanup was applied and read back in the live system, including deletion of all three empty generated workflows from the active library.

The curated registers remain living operating controls; their ongoing maintenance does not keep this audit open. The remaining work is implementation rather than discovery:

1. Build inbound conversation ownership, missed-call handling and response-time controls.
2. Resolve the trainer-contract `Full Time`/blank exception before the next trainer hire.
3. Design the post-Day-7 member lifecycle.
4. Complete the separate membership service-change, Strength Assessment attendance and AI pre-qualification builds.

These items are governed in the roadmap and their dedicated plans or tasks. They are not audit closure blockers.

## Progress: 17 July 2026

The Strength Assessment workflow family has been audited and reconciled. The work included unpublishing two confirmed legacy rebooking workflows, correcting trainer-brief routing, correcting cancellation-rebook task wording, accepting GHL's one-day minimum due date for the PREQUALIFY and READY tasks, and restoring the missing PAR-Q chase.

The chase now lives in published workflow `2.1A SA: PAR-Q Chase` (`f1b784dd-5c78-41fc-84af-0e636115a68d`). Published workflow `2. Strength Assessment` starts it immediately after the one-day-before PAR-Q link SMS. Both workflows and the complete handoff were live-verified before the local task register and sales-conversion documentation were updated.

The Hold OS and Cancellation OS task-producing workflows were then audited and reconciled. The Hold audit confirmed nine individual Create Task actions across standard membership-hold processing, extended approval, and the return journey. The Cancellation audit confirmed three Piper tasks in each of eight reason workflows, a separate Megan Brown task for booked cancellation calls, and Admin Eve processing tasks for membership and PT cancellations.

The `PT Cancellation: Process` description was completed and live-verified on 17 July 2026. Its one-day deadline is intentional: Admin Eve verifies Stripe and the final payment date, treats the following calendar week as the final PT service week, and deletes sessions after that week. The membership task remains due in 30 days because it serves a different notice-period reconciliation purpose.

Peter confirmed that billing and payment recovery do not have GHL workflows, so that area is recorded as an operating boundary rather than an undocumented workflow gap.

### 29 July 2026: Billing OS execution-error revalidation

The live `Needs review (3)` queue was reopened and fully reconciled. It no longer refers to the historical Did Not Answer trigger warnings recorded in the first owner-register pass.

`HS: Hold Activates` has repeated `400 Missing required fields` responses from Billing OS after the 9 July webhook update. Current contact evidence shows more than one cause: Rabail Aisha has no usable email or hold values in the matched record, while Tess Raby has overlapping requests merged into one impossible active record with Hold End Date before Hold Start Date. Tess received contradictory automated dates because the workflow continued after the webhook error.

`Membership Cancellation Form Recieved` has three July `400 Missing required fields` responses. Rachael Kolmajer's execution proves the submission date and Notice End Date were written successfully before the webhook, but the flow continued to confirmation and Notice Period after Billing OS failed. A fixed five-minute delay therefore does not provide a success acknowledgement.

`PT Cancellation Form Received` has one 4 July `404 Not Found` execution for Renae Acton. GHL identifies the invalid URL as an older workflow version, the current builder uses the valid `/stripe/cancel` endpoint, and the contact was already reconciled. However, the failed execution continued to the spreadsheet row, confirmation SMS and email, Notice Period and the 21-day wait. The current builder retains the same linear post-webhook structure, so its endpoint is repaired but its acknowledgement control is not.

The next critical repair is a shared fail-closed acknowledgement pattern across hold activation, membership cancellation and PT cancellation: preflight required fields and chronology, Billing OS writes success or exception status back to GHL, member confirmation and downstream state changes occur only after verified success, and Admin Eve receives a one-day exception for failure or timeout.

Peter confirmed the canonical hold policy on 29 July 2026: only one hold may be open at a time. This includes separate future periods that do not overlap; a second hold may be submitted only after the first reaches Completed. Because GHL writes form answers before the duplicate workflow branch runs, all four hold forms need temporary `HS Request:` fields. The workflow may promote those values into the canonical `HS:` record only when Hold Status is blank or Completed. Pending Hold, Escalated Hold, On Hold or Returning must preserve the original record, create an Admin Eve exception, notify the member of the policy and clear the rejected temporary values.

### 29 July 2026: Billing OS and hold-intake repair completed

Billing OS was deployed with GHL acknowledgement fields, chronology checks, Stripe idempotency and exact success or exception recording. All four published standard and extended membership/PT hold-intake workflows now call the protected intake endpoint before their existing checks.

The implementation snapshots an accepted first request into protected `HS Request:` fields. If a later form overwrites canonical fields while the first hold is Pending Hold, Escalated Hold, On Hold or Returning, the endpoint restores the protected first request before the existing duplicate branch continues. A live temporary-contact test confirmed the 10 August three-week request survived a later 21 September one-week submission; the temporary contact was deleted.

`HS: Hold Activates` now sets Billing OS Hold Action Status to Processing and waits for Succeeded before the first pause-confirmation SMS. Cancellation failures write Exception and remove the contact from the exact membership or PT cancellation workflow before spreadsheet, confirmation and Notice Period actions. The deployed build passes 15 automated tests.

The new-member onboarding family was then audited. Seven published workflows were reviewed and none contains a Create Task action. The live system handles tags, pipelines, spreadsheets, linked workflows, emails, SMS, and internal notifications, but no persistent staff handoffs. `3.0 New Member` and `3.1. New Personal Training Client` both enrol contacts into `Membership: First 7 Days`.

`Test - First 7 Days` had 82 historical enrolments, no active enrolments, no trigger, and was not the linked first-week workflow used by the verified new-client workflows. Peter confirmed it as the predecessor to the live sequence and unpublished it on 17 July 2026.

The remaining root workflows in `1. Pipeline Workflows` were then checked. Mobile Check originally contained no Create Task action; its two reply branches were upgraded on 29 July 2026 with persistent reply-review tasks, Admin Eve notifications and neutral acknowledgements. `Fitness Event Registration` was later confirmed triggerless and orphaned after its workshop form was deleted; Peter approved retirement on 22 July, and it was unpublished and moved into the Archive folder with four historical and zero active enrolments. The pipeline-folder audit is now included in the mandatory canvas revalidation tranche because earlier negative assertions were not consistently supported by complete canvas traversal.

The five published life-stage 30DNNC delivery workflows were fully revalidated on 29 July 2026. `20/30`, PERIM, POSTM and TEEN each reconciled at 120 canvas nodes before and after opening an action panel; PPP reconciled at 134 because of its intentional four-way life-stage branch. Settings, recent execution logs where retained, and active enrollment histories confirmed the live paths. None contains a reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action. The pass also confirmed a live `Day #12 - Creatine` email in all five workflows. The owner's earlier remove-creatine instruction applied only to creatine as an offer inclusion, so these nurture emails remain unchanged and require no action from that decision.

The transition revalidation then reconciled `2. Strength Assessment` at 99 nodes, `3.0 New Member` at 58 and `3.1. New Personal Training Client` at 15. All three are published and the intended lifecycle exits are present. The pass initially found overbroad removal lists; these were corrected on 29 July 2026. Strength Assessment now selects only the five life-stage delivery workflows, while both onboarding workflows select those five plus Mobile Check. The unrelated campaign, intake, PT-agreement and legacy First 7 Days targets were removed, and all three published workflows were reload-verified. The owner also confirmed that nurture-email replies remain in the normal inbox and do not need a dedicated workflow handoff.

The account-wide Published inventory was then enumerated at 107 workflows. Peter retired Corporate Gift Card Form Submission, Meta Lead Form, Website Register Interest Form, Trial Session, Test - First 7 Days, and `Metabolic Blueprint (END)`; Training Event Form Submission and Email Subscribers - Meta Lead Form were already drafts and were archived. `Metabolic Blueprint` and the incomplete `6WBTC EDU` workflow were then unpublished with approval, reducing the Published count to 99.

The Metabolic Classification Form remains published as a preserved 2011 diagnostic asset, but it is no longer promoted from 30DNNC and both Blueprint delivery workflows are inactive. The location-specific Bulimba, Coolangatta/Tweed, and Newfarm workflows are intentionally retained as an SEO interest-mapping and West End referral system.

The six `Send Story Email` workflows are also intentionally retained. They are delivery infrastructure for the member-story publishing system: the publishing script applies the relevant life-stage trigger tag, and the matching workflow distributes the new story to that segment. They should not be assessed as generic nurture sequences.

Peter confirmed that the five `Goal:` workflows were intended booked Strength Assessment goal nurture sequences. Each contains one email. Later full-canvas revalidation established that the workflows are published but disconnected from the current assessment path because their required goal tags are not being added. On 29 July, Peter confirmed they are not currently used and accepted the conclusion that the planned SA Pre-qual AI Agent supersedes their fixed one-email model. Do not reconnect or expand them; preserve worthwhile content for the AI story library, then dependency-check and archive them after the AI path is live and tested. `Lead Nurture: Social Proof` has no recent enrolment history and appears unused, although its client-spotlight content may be reusable once a clear trigger and role are defined.

`Membership: Day 29-90` remains published but contains too little meaningful content for that retention window. It is retained for now and recorded as a rebuild opportunity. The current purchase workflows, Hold OS, Cancellation OS, and trainer-course delivery workflows were reviewed at the family level and retained as sound operating systems.

On 30 July, Peter approved retirement of `Lead Nurture: Social Proof`. It was unpublished and moved to `1. Pipeline Workflows / Archive` with 2,056 historical and zero active enrolments. Its five linked client-spotlight templates were preserved for evidence-reviewed reuse.

### 29 July 2026: Class B revalidation

The complete canvases, settings and available 30-day enrolment histories were reopened for three conclusions that had influenced retention or retirement planning:

- `Membership: Day 29-90` still has no trigger or recent enrolment and contains only Wait 76 Days, Review Request SMS and Review Request Email. The complete `Membership: First 7 Days` workflow contains no action that enrols a member into Day 29-90.
- `Follow Up Monthy` had no trigger or recent enrolment and contained only Create or Update Opportunity to `[WARM] Sales Pipeline / FUM - Follow Up Monthly`. Allow re-entry and Allow multiple opportunities were on, but the workflow remained inert without an upstream or external enrolment. A 30 July dependency check confirmed that active workflow `2.5. No Sale - Follow Up` independently moves prospects to FUM and has recent production use, including one contact still progressing. The WARM pipeline contained zero open opportunities. The FUM stage was preserved; the shell was unpublished and renamed `FUM: Assessment Education & Reassessment Journey` for a governed Draft rebuild.
- `Lead Nurture: Social Proof` still has no trigger, enrolment or execution in the available 30-day history. A second full-canvas inspection on 30 July corrected the earlier incomplete node count: it contains five client spotlights, Tash, Karyn, Vicki, Helen and Ruth, separated by one-day waits. The retained New Lead V1-V5 builders contain no caller. All five emails promote Nutrition Coaching and use the obsolete `EVOLVE` reply CTA; several include pain, health, hormone or metabolism claims that require evidence and medical-copy review.

No workflow was unpublished or archived during the original revalidation. Day 29-90 remains a lifecycle-rebuild input. Peter subsequently chose to preserve the intent of `Follow Up Monthy`: the FUM stage and workflow history were retained, while the workflow was unpublished and renamed `FUM: Assessment Education & Reassessment Journey` on 30 July for a future 12-month education and quarterly reassessment rebuild. Social Proof was retired on 30 July with its linked templates and canonical story records preserved.

The five booked Strength Assessment goal-nurture workflows were also checked at full-canvas scale. They are not callerless shells: each is published, triggers from its canonical `goal:` tag, waits five minutes and sends one matching email. All five had no enrolment in the available 30-day history.

The upstream trace is now complete. `2. Strength Assessment` had many recent booking-triggered enrolments, sends a free-text goal SMS and adds only `Goals Submitted`; it contains no action that converts the reply into one of the five canonical goal tags. `3.0 New Member` also has no canonical goal-tag action. The goal nurtures are therefore disconnected from the current assessment path. This is no longer a repair requirement: the planned SA Pre-qual AI Agent will own goal clarification, structured primary-goal capture and success-story selection.

The five paid 30DNNC intake workflows were then revalidated at full-canvas scale. Each retains its audience-specific form trigger and intended processing path; all five had no enrolments in the available 30-day history. POSTM Paid remains correctly reduced to its postmenopause-only path and remains in Draft.

One additional safety defect was found in both PPP intake workflows. The `None` branch, used when none of Planning Pregnancy, Currently Pregnant or Post Partum matched, added `PREG` and proceeded through PPP delivery.

This was repaired and reload-verified on 29 July 2026. Both unmatched branches now create a one-day Admin Eve classification task and no longer tag or enrol the contact in PPP automatically. Paid intake retains Mobile Check; organic intake ends after the Admin task. The three valid life-stage branches and both workflows' published state remain intact.

### 30 July 2026: membership-change entry audit

The two published agreement workflows were revalidated against the two membership-change surveys. `Membership Agreement Form: Email` triggers only from `Membership Agreement Form`, and `PT Agreement Form: Email` triggers only from `Personal Training Agreement Form`. Neither processes the Hybrid/Online or PT membership-change survey.

Both change surveys have their native email notification and autoresponder disabled. The Hybrid/Online survey has two all-time submissions, on 22 May and 2 July 2026, both selecting the $69 weekly Hybrid option. The PT change survey has zero submissions from 1 January 2024 through 30 July 2026.

Both surveys display `https://www.example.com` for Privacy Policy and Terms of Service. No live change was made during the initial audit.

Peter subsequently confirmed that Hybrid and Online Only are legitimate retention services. Sue Goodwin's 22 May Hybrid change is already reconciled as the governed `$69` Evolved Anywhere service. Tania Stiles's 2 July `$69` Hybrid selection and signature persist in GHL, but her legacy `bronze` tag remains and the actual billing, monthly PT bookings, Trainerize access, pipeline and roster outcome must be verified.

The solution is a versioned Membership Service Change Variation plus an Admin Eve-owned, fail-closed transition across GHL, Billing OS, Trainerize, appointments, workbooks and reporting. Required offer decisions remain: Hybrid/Evolved Anywhere naming, Online Only at `$27` versus `$29`, Hybrid group access and PT delivery rules, the 30-day effective boundary and correct legal links. PT changes remain separate while PT pricing is proposed. Implementation scope: `plans/2026-07-30-membership-service-change-control.md`.
