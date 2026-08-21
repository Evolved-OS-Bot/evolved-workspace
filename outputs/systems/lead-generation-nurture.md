# Lead Generation & Nurture System Documentation
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-07-23

---

## Overview

The lead generation and nurture system captures cold prospects through segmented 30-Day Nutrition & Nutrition Course (30DNNC) opt-in forms and moves them toward a Strength Assessment. The former Metabolic Blueprint pathway has been retired from active delivery; its classification form remains available as a future tool. Warm prospects are managed through the **[WARM] Sales Pipeline**, while cold leads are tracked in the **[COLD] Marketing Pipeline** as they progress through nurture.

The system has a versioned `New Lead` workflow history (V1 through V5), indicating iterative development. All versions are now draft and sit in the Pipeline Archive; current lead handling therefore depends on the source-specific workflows and should be validated separately. The former Metabolic Blueprint pathway is also inactive, although its assessment form is retained for possible future use.

---

## Pipelines

### [COLD] Marketing Pipeline
**Pipeline ID:** `57MQJY8hc7VoOrNkNhZw`

| Position | Stage | ID |
|---|---|---|
| 0 | Signed Up \| 30DNNC | `06c02f35-3332-4068-950e-332172d599d0` |
| 1 | Opened 25% \| 30DNNC | `ef4176b0-ab28-483d-bea4-160efb815dcf` |
| 2 | Opened 50% \| 30DNNC | `22ee7001-7593-4932-99fc-38fcb6be575c` |
| 3 | Opened 75% \| 30DNNC | `691ed414-9acb-41b8-931b-fdf0526092a5` |
| 4 | Opened 100% \| 30DNNC | `c4946bdd-7b5b-43c1-a71f-8ce0dc8646b4` |
| 5 | Course Complete \| 30DNNC | `d96b895f-7330-4b63-a9b3-6ca22a38da05` |

Tracks cold leads through email engagement during the 30DNNC sequence. Stage progression is engagement-based: each stage reflects a percentage of the course emails opened. A Strength Assessment booking—not course completion—is the actual warm handoff.

### COLD opportunity-state audit: 4 August 2026

A complete supported-API snapshot found 760 COLD opportunities, one per contact and all still `Open` before reconciliation. The stage structure itself was coherent: 178 Signed Up, 83 Opened 25%, 63 Opened 50%, 44 Opened 75%, 43 Opened 100% and 349 Course Complete. New records continue to enter and progress, so the pipeline is live rather than an abandoned asset.

The historical defect was the absence of an exit rule. Before repair, the live 20/30 workflow contained an initial Create or Update Opportunity action, engagement-stage updates and a final Course Complete update, but no terminal status action; the other four life-stage delivery workflows used the same pattern. On 4 August, all five terminal Course Complete opportunity actions were changed from `Open` to `Abandoned`, saved and independently reload-verified. The Strength Assessment transition was also repaired: contacts carrying the canonical `30dnnc` tag now enter a COLD-only opportunity lookup, an existing record is changed to `Won`, and both the found and no-record paths continue into the normal `Previously Assessed?` assessment flow.

The exact 4 August classification is:

| Proposed state | Records | Evidence |
|---|---:|---|
| Won — cold-to-warm or direct client conversion | 354 | 346 have `strength assessment booked`; eight additional contacts are in the governed active-client cohort without that historical tag |
| Abandoned — course completed without assessment | 152 | Course Complete stage, no assessment-booking tag and not in the active-client cohort |
| Abandoned — stale incomplete course | 198 | No assessment-booking tag, not an active client, not Course Complete and no opportunity update for more than 45 days |
| Keep Open — current course progress | 56 | Not converted, not complete and updated within 45 days |

The 45-day boundary is deliberately wider than the approximately 30-day course plus its final waits. It is a safe stale-state classifier, not an email-engagement inference. Peter approved the exact classification on 4 August. The governed batch then set 354 records to Won and 350 to Abandoned while preserving all 56 current-course records as Open. Every one of the 704 approved records passed immediate read-back verification, and the final pipeline status count was 56 Open, 354 Won and 350 Abandoned.

Recommended operating rule:

1. Create one Open COLD opportunity when the lead enters 30DNNC.
2. Keep it Open while the course is genuinely in progress and update only its engagement stage.
3. Mark it Won when a Strength Assessment is booked or the contact otherwise becomes an active client.
4. Mark it Abandoned when the course completes without an assessment.
5. Treat the reporting hub and retained opportunity history—not permanently open cards—as the source for later re-engagement audiences.

The historical batch and all six future exit controls are complete. The terminal COLD-Abandoned control is live and reload-verified in all five delivery workflows: TEEN, PPP, POSTM, PERIM and 20/30. The published Strength Assessment workflow (`e4426f3c-fc5f-4e1e-9d34-9e4d77a088f2`) now uses `Guard existing 30DNNC COLD opportunity` to isolate contacts carrying `30dnnc`, finds only an existing opportunity in `[COLD] Marketing Pipeline`, and changes a found record to `Won`. Opportunity Found and Opportunity Not Found both rejoin `Previously Assessed?`; the guard's untagged `None` branch now uses `Direct assessment: continue normal flow` to rejoin the same point. A full reload verified the guard, lookup, `Won` update, both Go To actions, all three convergence edges and the workflow's Published state. This deliberately avoids an unguarded create/update opportunity writer, so direct assessment bookings do not receive a false COLD record.

---

### [WARM] Sales Pipeline
**Pipeline ID:** `JBVLybtIPZRIfjhzl5KV`

| Position | Stage | ID |
|---|---|---|
| 0 | Assessment Booked | `c419912e-6e51-4e83-8820-6700d12ae971` |
| 1 | Pre-Qualified | `f0db07c9-247f-41d5-ab68-8040f25e566d` |
| 2 | No Show | `e66774c3-5ee8-4924-8802-33a1fd6d6216` |
| 3 | Cancelled | `d31d88cb-fd7d-48c5-ad79-68faf382c897` |
| 4 | Show | `0aba395d-2ac7-45bc-96e1-410fbeb114c2` |
| 5 | FUM | `53f391b8-0173-4bd3-ad77-a9ced2c0b58a` |
| 6 | FUNQ | `3bb4fe17-c26c-4a48-8d2b-33aab3d7ab5d` |

This is the single active pipeline — the LT Pipeline (previously a separate sales conversion pipeline) has been consolidated here. All SA opportunities flow through: Assessment Booked → Pre-Qualified → Show (24hr Decision) → won/lost. No-shows and cancellations branch to their respective rebook stages before falling to monthly/quarterly follow-up pools.

---

---

## Workflows

### Cold Lead Capture — 30DNNC (Segmented by Audience)

Each 30DNNC audience segment has a pair of workflows: one for organic (free) sign-ups and one for paid (ads) sign-ups. Paid versions typically include additional steps (e.g. SMS, faster follow-up) or skip certain organic-only touches.

| Workflow | Status | ID |
|---|---|---|
| 30DNNC Form Submission | **published** | `b7c9a9a6-975e-4072-836e-8737ef480de9` |
| 20/30s - 30DNNC Form Submission (Organic) | **published** | `3e2ecc1b-ec12-4f44-a47b-c2cd5c0eeb59` |
| 20/30s - 30DNNC Form Submission (Paid) | **published** | `e5f80457-eb4e-49b6-b921-37669a0541b1` |
| PERIM - 30DNNC Form Submission (Organic) | **published** | `a136b4f7-9ef5-4dd2-baab-3f82fc7a09a8` |
| PERIM - 30DNNC Form Submission (Paid) | **published** | `8f11882d-5cb3-494c-8054-0f2c0c7c6614` |
| POSTM - 30DNNC Form Submission (Organic) | **published** | `95bb5ae0-4b08-471d-a8b3-48a6f05d157e` |
| POSTM - 30DNNC Form Submission (Paid) | **draft; repaired 29 July 2026** | `c28c70f8-cd2f-4725-abfa-71336e197589` |
| PPP 30DNNC Form Submission (Organic) | **published** | `7ef6051d-9125-48c0-9954-4ccd378ae8f5` |
| PPP 30DNNC Form Submission (Paid) | **published** | `bfc203d6-e0aa-4511-9c4b-ca81e5e45773` |
| Teen - 30DNNC Form Submission (Organic) | **published** | `085dcdd7-fec3-43d6-b703-dbdb31593abd` |
| Teen - 30DNNC Form Submission (Paid) | **published** | `ca68c3d3-1429-45d7-b1e6-81dac5d00218` |

Lead Source is now assigned separately from these eleven operational workflows. `LS: Guarded 30DNNC Website Organic` (`22ee9373-c366-4021-bdb4-fa205c34cd4a`) covers the generic and five organic forms; `LS: Guarded 30DNNC Paid Social - Meta` (`dc574784-bc9e-47e3-b1d5-6c982f3deadd`) covers the five paid forms. Both are published and write only when `Lead Source` is empty. The former direct source action was removed from all eleven workflows above on 23 July 2026 without changing their other actions or published state.

### Paid 30DNNC dependency audit: 29 July 2026

The five paid variants are a coherent dormant campaign system rather than orphaned workflows. GHL retains a matching paid form and three-step paid funnel for each audience: 20s/30s, Perimenopause, Postmenopause, PPP and Teen. The public 20s/30s funnel still resolves and displays its GHL opt-in form. Its GHL statistics screen showed no populated activity rows for 29 June to 29 July 2026, and the paid forms did not appear among the forms with current-period views.

The 20s/30s, Perimenopause, PPP and Teen workflows have audience-specific paid-form triggers and complete processing paths into the matching delivery workflow and `30DNNC | Mobile Check`. Full-canvas revalidation confirmed that all four published workflows had no enrolments in the available 30-day history. Their action paths remain structurally complete:

- 20s/30s: wait, notify, add `20/30s` and `paid`, write the spreadsheet row, then enrol in 20s/30s delivery and Mobile Check;
- Perimenopause: wait, notify, write the spreadsheet row, add `PERIM` and `paid`, then enrol in PERIM delivery and Mobile Check;
- Teen: wait, notify, write the spreadsheet row, add `Teen` and `paid`, then enrol in Teen delivery and Mobile Check;
- PPP: wait, notify, write the spreadsheet row and add `paid`, then branch by life stage before enrolment in PPP delivery and Mobile Check.

The shared PPP fallback defect was repaired and reload-verified on 29 July 2026. In both the organic and paid workflows, the unmatched `None` branch no longer adds `PREG` or enrols the contact in PPP delivery. It now creates a one-day `Admin Eve: Classify Unmatched PPP Life Stage` task instructing Admin to review the answer, correct the life-stage field, add the appropriate `PLANPREG`, `PREG` or `POSTP` tag, and enrol the contact in PPP only after classification. The paid fallback retains Mobile Check. The three valid Planning Pregnancy, Currently Pregnant and Post Partum branches remain unchanged, and both workflows remain published.

`POSTM - 30DNNC Form Submission (Paid)` contained an erroneous Perimenopause block before its correct Postmenopause block. It was unpublished and repaired on 29 July 2026. Seven duplicate or incorrect steps were removed: the first wait, first notification, spreadsheet row `#2`, `PERIM` tag, first `paid` tag, PERIM delivery enrolment and first Mobile Check enrolment.

The saved draft now contains only the intended path: Postmenopause paid-form trigger, one-minute wait, one notification, one spreadsheet row, `POSTM` tag, `paid` tag, POSTM delivery enrolment and Mobile Check enrolment. Keep it in Draft until a controlled test proves those eight outcomes, then republish only for an owned paid campaign. Keep the five forms and funnels as reusable campaign assets. For the other four workflows, require a named campaign owner, a current ad-destination check and an end-to-end test before a new campaign. Current Meta Ads Manager destinations were not verified in this audit.

### Cold Lead Nurture — 30DNNC Delivery Sequences

| Workflow | Status | ID |
|---|---|---|
| 20/30 30DNNC | **published** | `4b199bf7-b24d-4aa9-a7fb-7deeed35a031` |
| PERIM 30DNNC | **published** | `511ad13f-fcb5-4197-b70c-c88a1e66b387` |
| POSTM 30DNNC | **published** | `6e652cfe-3020-4fe0-80a4-0be081216e96` |
| PPP 30DNNC | **published** | `786341e6-b082-4ecb-89db-6167ba91a0eb` |
| TEEN 30DNNC | **published** | `cb3993b1-6984-43b5-954d-b3a15a289009` |
| 30DNNC \| Mobile Check | **published** | `bf04828a-6e96-4347-b1cf-d01ac83d5db4` |

`30DNNC | Mobile Check` checks whether the contact has a mobile number, routes message timing around reply hours, sends Strength Assessment prompts, waits for replies, and updates the opportunity where applicable. On 29 July 2026 both reply handoffs were upgraded with Admin Eve notifications, neutral acknowledgements and persistent reply-review tasks.

### Mobile Check source dependency trace: 29 July 2026

The source reconciliation confirmed that Mobile Check is intentionally fed by both the alternate-location workflows and the five paid intake workflows. The earlier location-builder inspection was incomplete because GHL's visual canvas exposed only the three currently rendered nodes and omitted off-screen actions from the accessible view.

| Intake workflow family | Enrols into Mobile Check |
|---|---|
| Bulimba Form Submission | Yes |
| Coolangatta/Tweed Form Submission | Yes |
| Newfarm Form Submission | Yes |
| Generic 30DNNC Form Submission | No |
| Five organic 30DNNC intake workflows | No |
| Five paid 30DNNC intake workflows | Yes |

The paid connections are 20s/30s Paid, PERIM Paid, POSTM Paid, PPP Paid and Teen Paid. POSTM Paid remains in Draft after its duplicate PERIM block was removed; the other four are published. PPP Paid contains Mobile Check enrolment inside its audience branches.

Each current location workflow performs the same broader intake sequence: internal notification, location tag, email, add to `30DNNC | Mobile Check`, then life-stage classification, spreadsheet capture, life-stage tag and enrolment into the matching 30DNNC delivery workflow. Katrina Morris's Bulimba execution and Erika's Newfarm execution both show the Mobile Check action succeeding before their life-stage branch. Ngarie's Coolangatta/Tweed execution produced the matching Mobile Check enrolment.

Five recent contacts were attributed directly to location workflows: Katrina Morris and Eleanor from Bulimba, Erika and Kirin from Newfarm, and Ngarie from Coolangatta/Tweed. Global workflow searches returned one workflow for each location name, so duplicate names are not the explanation.

Mobile Check has two confirmed source families: location-interest leads and the five paid 30DNNC intakes. Preserve it as part of the active location-lead and paid-lead intake architecture.

### Mobile Check activity check: 29 July 2026

Mobile Check was not dormant at the retirement gate. Its first history page showed seven enrolments:

- three contacts still waiting for a reply;
- one current execution enrolled on 28 July;
- one reply-driven execution finished at Internal Notification on 26 July;
- two older waiting executions from April and January;
- four finished executions across July.

The enrolment table displays the generic source `Another workflow action`. Action-event details identified the source workflow for all five contacts still within GHL's 30-day execution-log window: two Bulimba, two Newfarm and one Coolangatta/Tweed. Leah and Sara are outside the 30-day detail window, so their precise source cannot be recovered from this log.

Mobile Check was retained. Leah and Sara were removed from their stale January and April reply waits on 29 July 2026; their contact records and finished execution history remain. Katrina Morris was retained because her 28 July execution is current and has a scheduled 30 July continuation. Mobile Check now has one active contact.

### Live waitlist reply audit: 22 July 2026

The five life-stage delivery workflows had 396 active contacts in total at the time of inspection: 147 in `20/30 30DNNC`, 104 in `PERIM 30DNNC`, 111 in `POSTM 30DNNC`, 15 in `PPP 30DNNC` and 19 in `TEEN 30DNNC`.

All five have `Stop on response` switched off. A lead who replies to an email can therefore remain in the nurture sequence. The source-form workflows add source or life-stage tags and issue internal notifications, but they do not create an accountable reply task or assign a contact owner. This compounds the Conversations finding that unread messages can remain unassigned and that no response SLA is enabled.

Do not switch `Stop on response` on without first deciding whether a reply should permanently end the educational sequence. On 29 July 2026, the owner confirmed that nurture-email replies do not need a dedicated workflow handoff; they remain part of the normal inbox process. The five sequences therefore retain Stop on response off and no reply task or branch will be added.

Full builder inspection confirmed that none of the five life-stage delivery workflows contains a reply branch, booking check, membership check or Remove-from-Workflow action. The live Strength Assessment booking workflow removes only `30DNNC | Mobile Check` and then adds `Strength Assessment: Nurture`. Neither agreement workflow nor the `3.0` and `3.1` onboarding workflows removes the contact from 30DNNC or the older reactivation workflows. A prospect can therefore receive waitlist, assessment and later member communications concurrently unless another unverified external process intervenes.

### Lifecycle-exit dependency audit: 29 July 2026

At the lifecycle-exit audit checkpoint, exposure was 408 active contacts across the five delivery workflows: 149 in `20/30 30DNNC`, 109 in `PERIM 30DNNC`, 114 in `POSTM 30DNNC`, 15 in `PPP 30DNNC` and 21 in `TEEN 30DNNC`. Mobile Check then had three active contacts; its stale-contact cleanup on 29 July reduced that to one current execution. The live Strength Assessment workflow had four active contacts at the checkpoint.

Before remediation, all five life-stage workflows had `Stop on response` off, `Allow re-entry` on and `Allow multiple opportunities` on. Live builder and settings checks confirmed that they contained no booking, member or Remove-from-Workflow branch.

The source-transition trace found:

- `2. Strength Assessment` (`e4426f3c-fc5f-4e1e-9d34-9e4d77a088f2`) removes `30DNNC | Mobile Check` and adds `Strength Assessment: Nurture`, but does not remove any life-stage 30DNNC workflow.
- `Membership Agreement Form: Email` and `PT Agreement Form: Email` remove the No Sale workflow and tag, but do not remove 30DNNC.
- `3.0 New Member` and `3.1. New Personal Training Client` remove the retired Studio Appointment workflow, remove `SA: Nurture` and perform opportunity cleanup, but do not remove any 30DNNC workflow or Mobile Check.
- `30DNNC | Mobile Check` contains multiple reply waits and mirrored contact-reply branches. Both branches now produce the same neutral acknowledgement, Admin Eve notification and persistent reply-review task.

The lowest-complexity remediation was to use the existing transition workflows rather than create a second lifecycle authority.

Implemented and live-verified on 29 July 2026:

1. `2. Strength Assessment` was configured to remove the contact from all five life-stage 30DNNC workflows immediately after the existing Mobile Check removal.
2. `3.0 New Member` and `3.1. New Personal Training Client` were configured to remove all five life-stage workflows and `30DNNC | Mobile Check` immediately after their existing SA Nurture removal. These are intended as fail-safes for direct-sale, missed-booking and service-change paths.
3. The five life-stage delivery workflows now have `Allow multiple opportunities` off. `Allow re-entry` remains on and `Stop on response` remains off.
4. The agreement workflows remain unchanged because their normal paths subsequently enter `3.0` or `3.1`.

### Five-workflow full-canvas revalidation: 29 July 2026

All five published life-stage delivery workflows were revalidated under the corrected canvas-audit standard. Each workflow was fitted to screen, traversed from trigger to every end node, counted after rendering, opened through an action panel, closed and counted again.

| Workflow | Reconciled canvas nodes | Recent execution evidence | Result |
|---|---:|---|---|
| `20/30 30DNNC` | 120 before and after panel render | Active enrollment history confirmed contacts progressing through email-event waits | No reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action |
| `PERIM 30DNNC` | 120 before and after panel render | Active enrollment history confirmed direct-form and upstream-workflow entries | No reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action |
| `POSTM 30DNNC` | 120 before and after panel render | Recent execution logs confirmed email, wait, progress-check and Go To execution | No reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action |
| `PPP 30DNNC` | 134 before and after panel render | Recent execution logs present | No reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action |
| `TEEN 30DNNC` | 120 before and after panel render | Recent execution logs present | No reply, task, booking, member, Add-to-Workflow or Remove-from-Workflow action |

The additional PPP nodes are its intentional life-stage condition: Planning Pregnancy, Pregnant, Postpartum and no-match branches, followed by the matching field update and Go To controls.

All five remain published with Allow re-entry on, Allow multiple opportunities off and Stop on response off. Each contains ten email-event branches, ten timeout branches, five progress tags, six opportunity actions and one terminal end; PPP has two additional Go To actions and a second end because of its opening life-stage branch.

The revalidation also confirmed a live `Day #12 - Creatine` email in every workflow. The inspected Teen action is synchronised to a linked email template. The owner's earlier remove-creatine instruction applied only to creatine as an offer inclusion; it did not apply to educational or nurture content. These five emails remain unchanged and require no action from that decision.

### Lifecycle-handoff full-canvas revalidation: 29 July 2026

The three live transition workflows were then revalidated:

| Workflow | Reconciled canvas nodes | Confirmed controls |
|---|---:|---|
| `2. Strength Assessment` | 99 | Published; new-booking versus active-reschedule split; Mobile Check removal; five-delivery-workflow removal action; reschedule shortcut; SA Nurture; PAR-Q chase and reply paths |
| `3.0 New Member` | 58 | Published; one-time execution; plan branches; review tag; First 7 Days; pipeline actions and acquisition-removal action |
| `3.1. New Personal Training Client` | 15 | Published; one-time execution; review tag; First 7 Days; pipeline action and acquisition-removal action |

The intended lifecycle exits were present, but full-canvas revalidation found that the target selections were overbroad:

- `2. Strength Assessment` selects the five delivery workflows plus `28D$1 BLK FRI`, `POSTM - 30DNNC Form Submission (Paid)`, `PPP 30DNNC Form Submission (Organic)` and `PT Agreement Form: Email`. Mobile Check is handled by the separate preceding action.
- `3.0 New Member` and `3.1. New Personal Training Client` each select the five delivery workflows and Mobile Check, plus the same four unintended workflows and `Test - First 7 Days`.

Corrected and reload-verified on 29 July 2026:

- `2. Strength Assessment` now retains only `20/30 30DNNC`, `PERIM 30DNNC`, `POSTM 30DNNC`, `PPP 30DNNC` and `TEEN 30DNNC`. Its separate Mobile Check removal remains unchanged.
- `3.0 New Member` and `3.1. New Personal Training Client` now retain those five delivery workflows plus `30DNNC | Mobile Check`.
- `28D$1 BLK FRI`, `POSTM - 30DNNC Form Submission (Paid)`, `PPP 30DNNC Form Submission (Organic)`, `PT Agreement Form: Email` and, from the two onboarding workflows, `Test - First 7 Days` were removed from the target lists.

All three workflows remained published, and the saved selections persisted after reload.

### Mobile Check reply-path remediation: 29 July 2026

The full graph contains two mirrored timing paths, one for reply hours and one for after-hours leads. Full-canvas reconciliation verified eight reply waits, two central reply acknowledgements, two internal notifications and two persistent reply tasks.

Implemented and saved with Publish enabled:

1. Both `SMS | How Urgent?` actions were renamed `SMS | Reply Acknowledgement`.
2. Both messages now say: `Thanks for replying, {{contact.first_name}}. Our team has your message and will get back to you shortly.`
3. Both internal notifications were moved from the generic `The Evolved All Female Gym` recipient to `Admin Eve`.
4. Both reply branches now create `TASK | Review Lead Reply`, titled `LEAD REPLY: Review and respond - {{contact.first_name}} {{contact.last_name}}`.
5. The task directs the reviewer to read the actual conversation, avoid assuming urgency or positive intent, apply DND only for an explicit opt-out and continue the Strength Assessment conversation appropriately.
6. Both persistent reply-review tasks are assigned directly to `Admin Eve` and are due in one day at 12:00 am.
7. Allow multiple opportunities is off. Allow re-entry remains on and Stop on response remains off.

The five parallel life-stage delivery workflows were rechecked individually. All five consistently have Allow re-entry on, Allow multiple opportunities off and Stop on response off. Mobile Check ending on reply therefore does not pause or end the educational sequence.

Admin Eve is available in GHL's Add Task assignee search. Both mirrored reply paths now notify Admin Eve immediately and create the persistent follow-up task directly for Admin Eve.

No direct handoff will be added for nurture-email replies. The owner confirmed that the normal inbox process is sufficient; this does not change Mobile Check's dedicated SMS reply tasks.

### Warm Lead Capture

| Workflow | Status | ID |
|---|---|---|
| Website Register Interest Form | draft; archived 17 July 2026 | `ab6c54c4-c1ad-4b1c-b2c0-cf1cdc829503` |
| Meta Lead Form | draft; archived 17 July 2026 | `d99148b7-cde2-424a-9dfa-2f81bfa8ea1a` |
| Bulimba Form Submission | **published** | `8ffd9028-36dc-4749-abf1-14aeb129c23e` |
| Coolangatta/Tweed Form Submission | **published** | `596b86e8-f56d-4e3e-a0d5-2dd07318befe` |
| Newfarm Form Submission | **published** | `02524663-0985-46c1-a325-e93ba278a689` |
| Corporate Gift Card Form Submission | draft; archived 17 July 2026 | `f7e49018-d709-4efe-bf66-71f2910c0fdf` |
| BOF Comment Automation | draft | `1be5990c-e689-47a0-950e-fda770060e19` |
| BOF DM Automation | draft | `328ded6a-a749-419d-8f6b-d6e0e119c60a` |
| Email Subscribers - Meta Lead Form | draft; archived 17 July 2026 | `4a450a05-5d18-42c0-ad28-b28dabd703e2` |

BOF (Bottom of Funnel) automations trigger from social comment or DM interactions and are currently in draft. The Bulimba, Coolangatta/Tweed, and Newfarm workflows are intentionally retained as a location-SEO research system: local landing pages collect and tag interest by area, provide an interest map for future location decisions, and redirect urgent prospects to West End.

### New Lead Response (Versioned)

| Workflow | Status | ID |
|---|---|---|
| 1. New Lead (V1 - Jan24-Jun24) | draft | `3a54854b-1974-4644-92e4-34be5fd01d1f` |
| 1. New Lead (V2 Jun24-Jul24) | draft | `df92a27b-8520-48f1-8502-50af00431c99` |
| 1. New Lead (V3) | draft; archived | `ed9fc3a4-1cff-44b1-bb25-4ec62c0eb517` |
| 1. New Lead (V4) Part 1 (D0-D14) | draft | `79baa502-34b6-4acd-a935-be1f282b2b7e` |
| 1. New Lead (V4) Part 2 (D15-D42) | draft | `ee9456f5-38b6-4ebf-850c-5aff3e31a1c6` |
| 1. New Lead (V4) Part 3 (D43-D105) | draft | `8c7f4b4b-e01e-4f3c-bc4f-35ae907daaeb` |
| 1. New Lead (V5) Part 1 (D0-D14) | draft | `52e43175-1f42-4f17-9c53-b96de77ff2e6` |

No generic New Lead version is currently published. V4 is a three-part historical sequence stretching to 105 days, while V5 Part 1 is also draft. Confirm that each retained source-specific workflow provides the required immediate response before relying on it as a complete replacement.

### Retained lead-source response revalidation: 30 July 2026

The retained acquisition forms no longer depend on a generic New Lead workflow. Full-canvas checks confirm that the generic and five life-stage 30DNNC forms enter their published source-specific intake and delivery system, while Bulimba, Coolangatta/Tweed Heads and Newfarm enter their published location workflows. Those location workflows send an immediate email, record and tag the location, enrol Mobile Check, classify life stage, create the reporting row and enter the matching 30DNNC delivery workflow.

Current analytics support that this is the production entry layer rather than dormant design residue. From 16 to 30 July, GHL recorded 209 form views and 50 responses; the visible active set included the generic and all five organic 30DNNC forms, Bulimba, Coolangatta/Tweed Heads, PAR-Q and the coach feedback form. Recent execution history also confirms Newfarm submissions. The five paid variants remain a separate dormant campaign system and must pass an end-to-end relaunch test before use.

Result: every retained current acquisition form has an immediate response and a deliberate Strength Assessment-oriented nurture destination. No replacement generic New Lead workflow is required. The unrelated `Corporate Gift Card Claim` form was permanently deleted on 30 July after its submission workflow had already been archived. The two Strength For Industry surveys remain intentionally preserved for possible future corporate use.

### Warm Lead Nurture

| Workflow | Status | ID |
|---|---|---|
| Lead Nurture: Social Proof | draft; archived 30 July 2026 | `89002ace-158a-4049-acf4-50008fc562e5` |
| Lead Nurture: 10:1 Value | draft | `3c8559c7-732a-48cf-8b76-3bdc2f2e5753` |
| Intro Session Nurture | **published** | `566e6e14-ce07-4f98-b198-579f801667b0` |
| Strength Assessment: Nurture | **published** | `2abf0af9-25be-40dc-935e-51c92a6798b0` |
| No Sale - Follow Up | **published** | `72820730-c4ef-44ab-8abc-a4149cbe32bf` |
| NS - Not Interested | draft | `1c923632-cda4-4614-9795-52e01c38aab0` |
| NS - Not Interested | draft | `6b37dbfa-c231-408f-8d42-3e1846049ec1` |
| No Response | draft | `62df6848-0ba5-49db-83b6-6ea845979235` |
| 2 Step Permission/Reactivation | draft; archived 27 July 2026 | `06181ca7-5d1b-4cbc-8b39-17ff87a8dd19` |

`Lead Nurture: Social Proof` has 2,056 historical enrolments but none in the available 30-day history. It had no native trigger. A complete builder check of retained New Lead V1, V2, V3, all three V4 parts and V5 Part 1 found no Social Proof or Add-to-Workflow action. Its historic source was therefore a deleted workflow, manual or bulk enrolment, API or integration, or another workflow family not named New Lead. It was unpublished and moved to `1. Pipeline Workflows / Archive` on 30 July 2026. Two `NS - Not Interested` workflows exist in draft and likely represent unresolved duplicates or audience splits.

The 30 July full-canvas revalidation corrected an earlier incomplete node count. The complete builder contains five client-spotlight emails, Tash, Karyn, Vicki, Helen and Ruth, separated by one-day waits. Allow re-entry is on; multiple opportunities, Stop on response, time window and Mark as read are off. Every email uses an `EVOLVE` reply CTA and promotes Nutrition Coaching. Several also contain pain, health, hormone or metabolism claims that require evidence and medical-copy review before reuse. The underlying stories remain useful assets: Tash, Karyn, Helen and Ruth already have canonical workspace story records and published result-page coverage. The five linked email templates were preserved as source material when the disconnected workflow was retired.

### Metabolic Blueprint Pathway

| Workflow | Status | ID |
|---|---|---|
| Metabolic Classification Form | **published** | `b2bab945-ccfc-4d34-a2f1-ff078bcab517` |
| Metabolic Classification (Leads) | **published** | `ad84dbcc-d422-4445-aaec-41b60d14dec5` |
| Metabolic Blueprint | draft; unpublished 17 July 2026 | `6059d2d1-7297-49d9-9069-2a1399d2026f` |
| Metabolic Blueprint (END) | draft; unpublished 17 July 2026 | `1ae94d16-03f5-49a2-8bb4-6f70991e6cd0` |
| Women Over 40 - Metabolic Reboot | draft | `e80f5868-3ac3-414b-939a-75bfde9eb8eb` |

The 15-question Metabolic Classification Form remains published, but its CTA was removed from the 30DNNC sequences on 16 July 2026 and the member-facing `Metabolic Blueprint` workflow was unpublished on 17 July 2026. The tool was developed in 2011 to convert training clients into full transformation packages with nutrition coaching. Those packages are not currently offered; retain the asset for future comparison against more modern diagnostic and personalisation tools.

`Metabolic Blueprint (END)` is also unpublished, so the former Blueprint pathway is fully inactive while the assessment form remains preserved.

### Booked Strength Assessment Goal Nurture Sequences

| Workflow | Status | ID |
|---|---|---|
| Goal: Lose Weight | **published; disconnected and dormant** | `6488e53d-fc6e-43ec-a7b8-05c8a62f0053` |
| Goal: Tone Up | **published; disconnected and dormant** | `124d3acc-41ac-4aa0-847d-3fb3e9ad9194` |
| Goal: 300% Stronger | **published; disconnected and dormant** | `0dc2aa9b-9faa-45e4-8d82-ce55406e4903` |
| Goal: Postpartum Glow Up | **published; disconnected and dormant** | `d8d867a5-705d-4fb2-bf29-c832ce64de6d` |
| Goal: Strength For Life | **published; disconnected and dormant** | `fdd77dc4-4ea7-4bda-8abf-ffe18a764c25` |

These are historical booked Strength Assessment goal nurture sequences. Each contains one goal-specific email, but the current assessment path does not add the required trigger tag.

The planned SA Pre-qual AI Agent supersedes this fixed one-email nurture model: it begins from the goals reply, clarifies one primary goal and its motivation, captures structured goal data, selects the most relevant approved success story and produces the trainer brief. Do not reconnect or expand these workflows. Keep them dormant until the AI pre-qualification path is live and tested, reuse any worthwhile copy or story references in the AI story library, then dependency-check and archive the five workflows with separate approval.

The 29 July full-canvas revalidation confirmed that all five are published and natively tag-triggered:

| Workflow | Trigger | Complete action path |
|---|---|---|
| Goal: Lose Weight | `goal: lose weight` added | Wait 5 minutes → Lose Weight Email |
| Goal: Tone Up | `goal: tone up` added | Wait 5 minutes → Tone Up Email |
| Goal: 300% Stronger | `goal: 300% stronger` added | Wait 5 minutes → 300% Stronger Email |
| Goal: Postpartum Glow Up | `goal: postpartum` added | Wait 5 minutes → Glow Up Email |
| Goal: Strength For Life | `goal: strength for life` added | Wait 5 minutes → Strength For Life Email |

None had an enrolment in the available 30-day history on 29 July. During the same period, `2. Strength Assessment` contained many booking-triggered enrolments, including bookings from 28, 27, 25, 23, 22 and 21 July.

The upstream trace found no action in `2. Strength Assessment` or `3.0 New Member` that adds any canonical goal tag. The assessment workflow requests a free-text goal reply by SMS and later adds only `Goals Submitted`; it does not classify the reply or translate it into `goal: lose weight`, `goal: tone up`, `goal: 300% stronger`, `goal: postpartum` or `goal: strength for life`. The five nurtures are therefore valid but disconnected from the current assessment path. Before expanding their email content, define one classification point and an exception path so every eligible booked assessment receives no more than one canonical goal tag.

### Re-engagement & Reactivation

| Workflow | Status | ID |
|---|---|---|
| RE#1 - 30DNNC & SEMINAR | draft; archived 22 July 2026 | `8f070c8c-647a-4912-9ac2-e3fbd3c1b471` |
| 2 Step Permission/Reactivation | draft; archived 27 July 2026 | `06181ca7-5d1b-4cbc-8b39-17ff87a8dd19` |
| War Plan | draft; archived 27 July 2026 | `9207ca6e-ed4f-44ab-b67e-bc98a41068de` |

`RE#1` historically re-engaged cold leads who completed 30DNNC but did not convert. Live inspection on 22 July found 10 waiting or processing enrolments after a 15 May bulk enrolment; the `50` shown at the bottom of the history screen was the page-size selector, not an enrolment count. Peter subsequently approved retirement of all seminar workflows. `RE#1` was set to Draft and moved to `1. Pipeline Workflows / Archive`; its 10 enrolled records remain visible as history but will not continue receiving the sequence.

The first six of its seven emails promote a “brand-new 8 Week Transformation Challenge” and a “Muscle & Metabolism Seminar coming up next week”, with a reply instruction of `METABOLISM`. The seventh email instead uses the `FEON` reply keyword and offers the existing foods PDF. No inspected email references a seminar custom value or TransformationFLIX. These messages are now retained only as archived history.

The live settings audit on 22 July confirmed that `2 Step Permission/Reactivation` and `War Plan` have `Stop on response` switched off. A deeper builder audit on 27 July found no enrolments or executions for either workflow in the available 30-day history.

`2 Step Permission/Reactivation` was triggered by the `cl` tag and sent two permission emails three days apart. A click added `Stay`, removed cold-lead tags and added `Warm`. If neither email was clicked, a final condition protected contacts carrying `strength assessment booked`, `old member`, `old pt client`, `30dnnc`, `meta ads`, `member`, `personal training`, `reengage: opened email` or `reengage: link clicked`. Protected contacts received the misspelled `supress` tag; all other contacts were deleted from GHL. With zero active enrolments, the workflow was unpublished and moved into `1. Pipeline Workflows / Archive` on 27 July 2026. Any future repermission system must use governed suppression and preserve the contact record.

`War Plan` had no trigger. Its three two-day-spaced emails promoted an obsolete 28-day weight-loss challenge with a “lose 2 kg or it is free” guarantee. Each reply branch sent an SMS to a hard-coded mobile number telling the recipient to check the old Lead Connector app. It was unpublished and moved into `1. Pipeline Workflows / Archive` on 27 July 2026 rather than being connected to the modern reply controller.

The remaining reply-ownership risk therefore sits in the active acquisition and nurture workflows, not these dormant assets. It should be designed with the waitlist reply handoff rather than fixed independently.

### Special Campaigns & Offers

| Workflow | Status | ID |
|---|---|---|
| 28D$1 BLK FRI | **published** | `98d64b98-2bae-4ad7-b535-40f4ae3b9799` |
| GFO BLKFRI | **published** | `9ff13c3e-6f98-4d70-8c83-2d01b17974a6` |
| 6WBTC EDU | draft; unpublished 17 July 2026 | `9e772dac-c329-415e-9804-b38dcf481ba9` |
| PERIM: 7 Day Reset Purchase | **published** | `724b6d05-714b-4202-813c-9068222e0247` |
| POSTM: 7 Day Reset Purchase | **published** | `25426e71-1e56-4621-aee5-846625c4c048` |
| Fitness Event Registration | draft; archived 22 July 2026 | `41f36656-6f7d-41f9-be75-3c604dd78c6a` |
| FitFam Cookbook Purchase | **published** | `d176bd85-6e66-43de-a6d2-b889393967a5` |
| Resource: FEONs | **published** | `98b3eaf7-d189-4d63-aca6-af53a487e861` |
| Workshop Sequence | absent from current inventory | Former ID `561e8fa8-68d0-40e1-8986-a26f3c044843` |

BLK FRI = Black Friday campaigns. `6WBTC EDU` was retired because the supposed six-week sequence contained only Week 1 and Week 2 emails. 7 Day Reset = paid product for perimenopause and postmenopause segments. FEONs = Free Educational/Offer sequences (resource lead magnets).

### Seminar-Specific

| Workflow | Status | ID |
|---|---|---|
| Transformation Seminar: Attending | draft; archived 22 July 2026 | `98f122e9-4914-4187-887e-f1b8fe8f6554` |
| Transformation Seminar: Interest | draft; archived 22 July 2026 | `cd33e367-9f17-42c9-a2cc-3f3bd90daada` |

---

## Forms

### Lead Capture — 30DNNC Opt-In Forms

| Form Name | ID |
|---|---|
| 30DNNC Form | `qB8xGGwhLdSGtbc3Z0EJ` |
| 30DNNC Form - 20-30's | `x7kX4iXL88xesZjZuc2y` |
| 30DNNC Form - 20-30's - Paid | `t49zdEkAyxhmENnljsGj` |
| 30DNNC Form - PPP | `nkLAaryOhWRKn6B4ynTR` |
| 30DNNC Form - PPP - Paid | `ezzKWJemhQTKXV7uTsaj` |
| 30DNNC Form - Perimenopause | `yGdm5cnighkkf4TZrJTy` |
| 30DNNC Form - Perimenopause - Paid | `3HC0uyY3yVpxGl6nbKVH` |
| 30DNNC Form - Postmenopause | `6KHo1LIUmUa1D5GASg98` |
| 30DNNC Form - Postmenopause - Paid | `5K20hus2C7U6JdjLoF28` |
| 30DNNC Form - Teen | `9KnvPrY6tEJfhaEPmkZ1` |
| 30DNNC Form - Teen - Paid | `FmK94feHeitFIqxVvAvk` |

Each audience segment has separate organic and paid versions. Paid variants likely include additional fields or behavioural differences to sync with ad attribution. Segments: General, 20-30s, PPP (Planning/Pregnant/Postpartum), Perimenopause, Postmenopause, Teen.

### Lead Capture — Website & Direct

| Form Name | ID |
|---|---|
| Website: Register Interest | `hJohXvBZv6gn0jD3AdpR` |
| Workshop Opt In Form | `6U0CBGMsLfRlMbCoQuWe` (deleted 22 July 2026) |

### Location-Specific Lead Capture

| Form Name | ID |
|---|---|
| Bulimba | `RfRzP6RlQO4SzeTaTfLi` |
| Coolangatta/Tweed Heads | `qtA20VCAhu4DkGBbEhKb` |
| Newfarm | `JgAzRnbtYkOAwj0kqrYX` |

Used for suburb-specific campaign landing pages. All three are published with corresponding form submission workflows.

---

## Surveys

| Survey Name | ID |
|---|---|
| Metabolic Classification Form | `3dC0KGX0gwEjkDf5YZHx` |

The Metabolic Classification Survey is the primary lead qualification tool for the Metabolic Blueprint pathway. It contains 15 scored questions (metabolic blockers, diet habits, exercise history, body composition, age, sleep, etc.) and generates a `Metabolic Classification Score` (NUMERICAL custom field). Leads are categorised as Met Class A, B, or C based on score.

---

## Calendars

| Calendar | Type | ID |
|---|---|---|
| Strength & Longevity Assessment [WEST END, BRISBANE] (round_robin) | round_robin | `HSVEzfJH4nice96IxHem` |
| Strength & Longevity Assessment [WEST END, BRISBANE] (event) | event | `z3cCnLnqwEO7jDrGA0HH` |

The Strength & Longevity Assessment is the acquisition conversion event. The round-robin and event variants require a usage check before consolidation.

---

## Custom Fields

### UTM & Lead Source Tracking
**Group ID:** `9klbgmldALQR9VbYrMr8`

| Field | Type | Key | ID |
|---|---|---|---|
| utm_campaign | TEXT | `contact.utm_campaign` | `vn2xMaLsemWDevjl0aub` |
| utm_content | TEXT | `contact.utm_content` | `NEUXQAbDJnGksriffuO5` |
| utm_medium | TEXT | `contact.utm_medium` | `0fkHvHHBcE36b3Wg8sy9` |
| utm_source | TEXT | `contact.utm_source` | `1P38S69Vo9PegkkrZmdY` |
| Lead Source | SINGLE_OPTIONS | `contact.lead_source` | `PMDHTnyNEhZS4qgOhUxE` |

**Lead Source options (expanded 23 July 2026):** Paid Social - Meta / Paid Search - Google / Organic / Website Organic / Organic Social / Referral / Walk-In / Event / Other

`Lead Source` is the original, first-touch acquisition source. Once populated, downstream workflows should not overwrite it; campaign and channel detail remains available in the UTM fields and source tags. The legacy `Organic` option is retained to protect historical data and existing workflow dependencies.

The live enforcement layer is complete. A controlled dummy-contact test showed the paid guard populate a blank field with `Paid Social - Meta`; a subsequent organic guard test preserved that value rather than replacing it with `Website Organic`.

**Group ID:** `yCGIA0tMjIzAVjRjSQXq`

### Lead Qualification & Segmentation
**Group ID:** `9klbgmldALQR9VbYrMr8`

| Field | Type | Key | ID |
|---|---|---|---|
| Pick the most relevant stage of life | RADIO | `contact.pick_the_most_relevant_stage_of_life` | `gKk8C5noKS1Gs81vKafA` |
| Where do you currently live? | MULTIPLE_OPTIONS | `contact.where_do_you_currently_live` | `OzgRHzKYJmkppezLjkL4` |
| Email Opt In | CHECKBOX | `contact.email_opt_in` | `elb56bw7b0ffyU55uo67` |
| Lead: Life Stage | MULTIPLE_OPTIONS | `contact.lead_life_stage` | `ZwlSSe4KD2J4TygSzwv7` |

**Stage of Life options (form field):** Teen / 20s/30s / Planning Pregnancy / Currently Pregnant / Post Partum / Peri Menopause / Post Menopause

**Lead: Life Stage options (canonical export field):** Teen / 20's & 30's / Planning Pregnancy / Pregnant / Postpartum / Perimenopause / Postmenopause

> `Lead: Life Stage` is set in email/nurture sequences (not lead source workflows, to keep entry-point workflows simple). It is the canonical field for writing clean life stage data to Google Sheets (Pre-Qual Insights tab and Objections Log tab). Merge tag: `{{contact.lead_life_stage}}`.

**Location options:** Brisbane (or surrounding suburbs) / Gold Coast / QLD / Elsewhere in QLD / New South Wales / Victoria / Tasmania / South Australia / Northern Territory / Australian Capital Territory / Western Australia / Outside Australia

The unrelated April 2024 business-offer qualification field was created for the retired Impact Call sales path. It had zero stored values across the complete 31 July 2026 contact snapshot and was deleted with the other two orphaned Impact Call fields after owner approval; it is not part of current lead qualification.

The separate `SMS/Txt Opt In` custom field (`qGZnum0zTEiFsFvzV5AV`) was not part of the live acquisition form. A 31 July dependency check found zero contact values and no current form, survey, template or supported workflow-metadata consumer; Peter approved deletion and the API read-back verified it absent. The live 30DNNC form continues to use `Email Opt In` with combined requested email/text consent wording.

**Group ID:** `GuiXAoJoZHSIaS669O8A`

| Field | Type | Key | ID |
|---|---|---|---|
| Pick the most relevant stage of life (social) | RADIO | `contact.pick_the_most_relevant_stage_of_life_so_w` | `tGaGYawO3Q4AAPnuznF7` |

**Options:** Teen / 20-30s / Planning Pregnancy / Currently Pregnant / Postpartum / Peri Menopause / Post Menopause

> Note: Three life-stage fields exist when the canonical `Lead: Life Stage` field is included. Keep both form-bound radio fields while their forms remain live, but normalise their values into the canonical field in workflows.

Full-canvas revalidation on 30 July 2026 confirmed that this normalisation is already live. `20/30 30DNNC`, `PERIM 30DNNC`, `POSTM 30DNNC` and `TEEN 30DNNC` each write their matching canonical value. `PPP 30DNNC` writes Planning Pregnancy, Pregnant or Postpartum after its tag branch.

The generic `30DNNC Form Submission` workflow was also revalidated after using Fit to Screen. Its complete canvas retains the form trigger, all seven life-stage branches, spreadsheet writes, life-stage tags and handoffs into the five delivery workflows. Its enrollment history showed current production use through 30 July 2026. The earlier three-node view was an incomplete viewport, not the complete workflow.

The postpartum migration entered its monitored cutover stage on 30 July 2026. Full-canvas checks found the hidden `POSTP` actions in all three published intake paths, not only the initially visible first actions. `30DNNC Form Submission` (`b7c9a9a6-975e-4072-836e-8737ef480de9`), `PPP 30DNNC Form Submission (Organic)` (`7ef6051d-9125-48c0-9954-4ccd378ae8f5`) and `PPP 30DNNC Form Submission (Paid)` (`bfc203d6-e0aa-4511-9c4b-ca81e5e45773`) now add only canonical `postpartum` and `30dnnc` on their postpartum paths.

`PPP 30DNNC` (`786341e6-b082-4ecb-89db-6167ba91a0eb`) branches on canonical `postpartum`, then writes `Lead: Life Stage = Postpartum`; the saved full-canvas read-back contained no legacy postpartum condition. San-Rene Tan's genuine 4 August intake entered this workflow and read back `Lead: Life Stage = Postpartum` after the 6:00 am branch on 5 August. Owner-approved cleanup then removed `post partum` from all three intake actions. Each writer was saved, reloaded and verified Published with `postpartum` and `30dnnc` retained. The legacy tag was deleted and verified absent. The member-story workflow remains independent: it triggers from `notify-story-postpartum`, while the story-publishing process selects the canonical `postpartum` audience.

### Metabolic Classification Fields
**Group ID:** `d5MFIbXvk4dTXJ0S2kwD`

| Field | Type | Key | ID |
|---|---|---|---|
| Metabolic Classification Score | NUMERICAL | `contact.score_metabolic_classification_score` | `6SQirWtVQGGSo7W6HklT` |
| 1. Weight gain/loss concern | RADIO | `contact.1_whether_you_wish_to_gain_or_lose_weight` | `VrQDMPYspbp9AAvNN5Qb` |
| 2. Age influences metabolism | RADIO | `contact.2_yes_its_true_age_does_influence_metabol` | `Z7OBrGmrtAGrTeBFwzHI` |
| 3. Population background | RADIO | `contact.3_from_research_its_clear_that_some_popul` | `i18IGzbd5SOzvEsZkJRP` |
| 4. Diets undertaken | RADIO | `contact.4_how_many_diets_have_you_been_on` | `xfqo5tRDetZPtWY3tdWX` |
| 5. Breakfast pattern | RADIO | `contact.5_breakfast_is_a_powerful_trigger_that_ca` | `xZ9IS72OCk2UqHbb0JaR` |
| 6. Past 6 months nutrition (meal structure) | CHECKBOX | `contact.6_for_the_past_6_months_pick_the_statemen` | `92uxbyv6ge8Ard6cOiKD` |
| 6b. Right now nutrition description | RADIO | `contact.6_right_now_what_description_best_describ` | `C3xZccZrxS2zxREsU0Fg` |
| 7. Structured training history | RADIO | `contact.7_how_many_structured_12_week_body_transf` | `O4lrkKe2PEZThlfVKP2n` |
| 8. Omega 3 knowledge | RADIO | `contact.8_a_high_ratio_of_omega_3_is_essential_fo` | `FT3Jy5fXkhCcgxSt1z02` |
| 9. Resistance exercise history | RADIO | `contact.9_with_every_passing_decade_adults_lose_t` | `ZttqTyzvgfMwhzG5E0tj` |
| 10. Aerobic exercise frequency | RADIO | `contact.10_how_often_do_you_perform_aerobic_type_` | `Cf6KvIgf26qjJGYSjj8U` |
| 11. Body fat level | RADIO | `contact.11_how_much_body_fat_you_have_and_how_lon` | `g9MR18aAMemCQoc7Otfm` |
| 12. Body fat distribution | RADIO | `contact.12_where_you_store_your_body_fat_has_impo` | `ZFgG35JN5T02j94tRuZK` |
| 13. Sleep quality | CHECKBOX | `contact.13_sleep_quality_has_a_profound_effect_on` | `Y1SolIU7VWbatXBSejpl` |
| 14. Metabolic blockers | CHECKBOX | `contact.14_metabolic_blockers_are_poor_sleep_habi` | `KZG1ydSgLgVnp3ivCGOP` |
| 15. Mirror confidence | RADIO | `contact.15_when_you_stand_in_front_of_the_mirror_` | `02Ed49bwNfKCFRDZrVzp` |
| I agree to receive SMS updates | CHECKBOX | `contact.checkbox_8i12` | `e0Ex3myyRqm6QiEcXgOG` |

### Fitness Goals
**Group ID:** `JwbflBU2YDUaZb9godHU`

| Field | Type | Key | ID |
|---|---|---|---|
| What are your primary fitness goals? | CHECKBOX | `contact.what_are_your_primary_fitness_goals` | `HbIxBf5wqpYIQuETaemm` |

**Options:** Lose Weight / Tone Up / Improve Health / Improve Posture / Get Stronger / Injury Prevention

---

## Custom Values

| Name | Key | Value / Notes |
|---|---|---|
| 30DNNC Link | `{{ custom_values.30dnnc_link }}` | `https://www.theevolvedgym.com.au/30dnnc` |
| Metabolic Classification Assessment Link | `{{ custom_values.metabolic_classification_assessm` | `https://api.leadconnectorhq.com/widget/survey/3dC0KGX0gwEjkD` |
| Stay On List (Reactivation) | `{{ custom_values.stay_on_list_reactivation }}` | Deleted 30 July 2026 after its parent workflow was archived and a 271-template dependency scan returned zero consumers |
| Strength & Longevity Assessment | `{{ custom_values.strength__longevity_assessment }}` | `https://theevolvedgym.com.au/strength-assessment` |
| Peri Menopause: 7 Day Reset | `{{ custom_values.peri_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |
| Post Menopause: 7 Day Reset | `{{ custom_values.post_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |
| [WARM] Seminar - Replay | `{{ custom_values.warm_seminar__replay }}` | Deleted 22 July 2026 |
| [WARM] Seminar - Slide Deck | `{{ custom_values.warm_seminar__slide_deck }}` | Deleted 22 July 2026 |
| DR Offer | `{{ custom_values.dr_offer }}` | (empty) |
| Offer Name | `{{ custom_values.offer_name }}` | (empty) |
| Booking Thank You Page | `{{ custom_values.booking_thank_you_page }}` | (empty) |

---

## Tag Library (Lead & Nurture Related)

| Tag | Purpose |
|---|---|
| `cold lead` | Contact is a cold prospect (top of funnel) |
| `lead` | Generic lead flag |
| `new lead` | Recently captured, not yet contacted |
| `nurture` | In an active nurture sequence |
| `warm reactivation lead` | Previously cold/dormant, now re-engaged |
| `interested` | Has indicated intent but not yet booked |
| `30dnnc` | Enrolled in the 30DNNC sequence |
| `30dnnc: complete` | Completed the 30DNNC sequence |
| `opened: 25%` | Opened 25% of 30DNNC emails |
| `opened: 50%` | Opened 50% of 30DNNC emails |
| `opened: 75%` | Opened 75% of 30DNNC emails |
| `opened: 100%` | Opened 100% of 30DNNC emails |
| `metabolic blueprint` | In the Metabolic Blueprint funnel |
| `metabolic classification` | Completed metabolic classification quiz |
| `met class: a` | Metabolic Class A (high score) |
| `met class: b` | Metabolic Class B (medium score) |
| `met class: c` | Metabolic Class C (lower score) |
| `met class a` | Alternate/duplicate of met class: a |
| `highly engaged` | High email/SMS engagement flag |
| `no answer` | Called, no answer |
| `no response` | No response to follow-up attempts |
| `no sale` | Consultation held, not converted |
| `no sale: financial` | No sale — financial objection |
| `no show` | Did not attend booked appointment/call |
| `ns - follow up` | In no-show follow-up sequence |
| `not interested` | Explicitly declined |
| `lost` | Lost lead (closed) |
| `trust` | Trust-building content delivered |
| `action: workshop opt in` | Opted into a workshop |
| `source: bof comment` | Came from a BOF (social) comment |
| `source: bof dm` | Came from a BOF direct message |
| `landing page` | Entered via a landing page |
| `website` | Entered via the website |
| `meta ads` | Source: Meta paid advertising |
| `fb organic` | Source: Facebook organic |
| `ig organic` | Source: Instagram organic |
| `instagram` | Instagram source |
| `organic` | Organic (non-paid) source |
| `paid` | Paid advertising source |
| `referral` | Referred by an existing member/contact |
| `bark` | Source: Bark (freelancer/leads platform) |
| `walk in` | Walk-in enquiry |
| `contact us` | Used contact form |
| `trainer lead` | Lead is a potential trainer (staff pipeline) |
| `other leads` | Miscellaneous lead bucket |
| `reengage: link clicked` | Clicked a re-engagement link |
| `reengage: opened email` | Opened a re-engagement email |
| `reactivation_2026_stay` | In the 2026 reactivation campaign (stay cohort) |
| `strength assessment booked` | Has booked a Strength Assessment |
| `strength assessment link clicked` | Clicked the SA booking link |
| `strength assessment showed` | Attended the Strength Assessment |
| `goals submitted (under 45mins)` | Submitted goals form quickly (high intent indicator) |
| `7 day trial` | On a 7-day trial |
| `seminar: attending` | Registered for a seminar |
| `seminar: attended` | Attended a seminar |
| `seminar: bought` | Purchased at a seminar |
| `seminar: dna` | Did not attend seminar |
| `protein hand raiser opt in` | Opted into a protein/nutrition resource |
| `resource:food` | Received a food/nutrition resource |
| `food` | Food/nutrition context tag |
| `7 day reset` | Purchased or in 7 Day Reset program |
| `fitfam cookbook` | Purchased FitFam Cookbook |
| `perimenopause` | Perimenopause segment |
| `20/30s` | 20-30s segment |
| `teen` | Teen segment |
| `planpreg` | Planning pregnancy segment |
| `planning pregnancy` | Planning pregnancy (full tag) |
| `postpartum` | Canonical postpartum segment |
| `post partum` | Retired and deleted 5 August 2026 after the canonical branch passed a genuine submission and all three writers were migrated |
| `postmenopause` | Post-menopause segment |
| `pregnant` | Currently pregnant |
| `fit over 40` | Over-40 segment (legacy/campaign) |
| `brisbane` | Brisbane location tag |
| `gold coast` | Gold Coast location tag |
| `bulimba` | Bulimba-specific lead |
| `coolangatta/tweed` | Coolangatta/Tweed-specific lead |
| `newfarm` | Newfarm-specific lead |
| `redcliffe` | Redcliffe-specific lead |
| `nya` | Not yet assigned (internal admin flag) |
| `dnd` | Do not disturb (suppress comms) |
| `supress` | Suppress from sequences |
| `failed sms` | SMS delivery failure |

---

## Flow Diagrams

### Cold Lead Flow: 30DNNC Pathway

```
[Meta Ad / Organic Post]
        |
        v
[30DNNC Opt-In Form]
(Segmented: 20/30s / PERIM / POSTM / PPP / Teen / General)
(Organic or Paid variant)
        |
        v
[30DNNC Form Submission Workflow fires]
  → Adds to [COLD] Marketing Pipeline: "Signed Up | 30DNNC"
  → Tags: cold lead, 30dnnc, [segment tag]
  → UTM fields captured (utm_source, utm_medium, utm_campaign, utm_content)
        |
        v
[Segment-specific 30DNNC Nurture Sequence begins]
(e.g. PERIM 30DNNC, 20/30 30DNNC, TEEN 30DNNC)
  → 30-day email course delivered
  → Pipeline stage advances on email engagement:
       Opened 25% → Opened 50% → Opened 75% → Opened 100%
  → Tags reflect engagement: opened: 25% / 50% / 75% / 100%
        |
        v
[Course Complete | 30DNNC]
  → Tag: 30dnnc: complete
        |
        v
[RE#1 - 30DNNC & SEMINAR workflow]
  → CTA must lead to a Strength Assessment, seminar, or deliberate nurture state
        |
        v
[Strength Assessment booked]
  → Enters [WARM] Sales Pipeline: Assessment Booked
```

---

### Current Location-Interest Lead Flow

```
[Bulimba / Coolangatta-Tweed / Newfarm landing-page form]
        |
        v
[Location-specific capture workflow fires]
  → Lead added to [WARM] Sales Pipeline: New Leads
  → Location interest tagged for demand mapping
  → Prospect redirected toward West End when urgency is higher
```

---

### Historical Metabolic Blueprint Flow

```
[Metabolic Classification Assessment Link shared]
(formerly via 30DNNC nurture, email, or direct)
        |
        v
[Metabolic Classification Form submitted]
  → Metabolic Classification Form workflow fires
  → Score calculated → Metabolic Classification Score field populated
  → Tag: metabolic classification
  → Tag assigned: met class: a / met class: b / met class: c
        |
        v
[Metabolic Blueprint workflow fired historically]
  → Personalised blueprint delivered based on score/class
  → Value sequence with educational content
  → Former sales CTA
        |
        v
[Metabolic Blueprint (END)]
  → Final CTA / sequence close
        |
        v
[Pathway now inactive]
```

---

## System Notes & Observations

### What's working well
- **Audience segmentation** on 30DNNC is best-practice — six distinct life-stage segments each with organic and paid variants means messaging is highly relevant and ad attribution is clean
- **UTM capture** at the form level (four standard UTM fields) provides full source-medium-campaign-content tracking across all lead sources
- **Strength Assessment conversion process** creates an in-person diagnostic and sales experience rather than a phone-based close
- **Metabolic Classification** remains a retained 15-question scored tool for future comparison, while its former Blueprint delivery path is inactive
- **Goal-based nurture sequences** (5 goals, all published) personalise the pre-assessment experience after the booking
- **BOF automations** (comment + DM) are architected even if in draft — captures social intent signals that most gyms miss
- **Versioned New Lead workflows** (V1–V5) show a culture of iteration. The day-based structure in V4 (D0-D14, D15-D42, D43-D105) is a significant maturation from earlier versions

### Current gaps / things to review
- **Legacy New Lead workflows remain duplicated** — all 65 paused enrolments were removed on 20 July 2026, so V1, V4 Parts 2 and 3, V5 Part 1 and the newer NS workflow now have zero active contacts. Retirement and naming governance remain, but paused-contact risk is resolved.
- **Two duplicate NS - Not Interested workflows** (both draft) — needs deduplication or audience-split clarification before either is published
- **BOF Comment and BOF DM workflows are in draft** — social intent capture is not yet live. Once published, these should feed into the [WARM] Sales Pipeline with a `source: bof comment` / `source: bof dm` tag
- **No verified win-back path for cold leads who complete 30DNNC without an assessment** — audit `RE#1` and ensure its CTA leads to a Strength Assessment or deliberate nurture state
- **Lead Source governance completed on 23 July 2026** — Referral, Walk-In, Website Organic, Organic Social, Event and Other were added while the three existing options and values were preserved. Two published blank-field guards now cover all eleven 30DNNC forms, and the unsafe direct writes were removed from the original workflows
- **Stage of life field fragmentation** — two form-capture fields exist (`9klbgmldALQR9VbYrMr8` and `GuiXAoJoZHSIaS669O8A`), retained for form functionality. The new `Lead: Life Stage` SINGLE_OPTIONS field (`contact.lead_life_stage`) is the canonical data-export field — set in email/nurture sequences rather than lead source workflows. This is the value written to Google Sheets (Pre-Qual Insights and Objections Log tabs) and used as a merge tag in downstream content personalisation
- **`met class a` and `met class: a`** are both in the tag library — duplicate with inconsistent formatting. Standardise to colon-format (`met class: a/b/c`)
- **`DR Offer`, `Offer Name`, and `Booking Thank You Page` custom values are empty** — these appear to be template/placeholder values intended to be populated for campaigns. If not in use, they should be removed or documented as intentional placeholders
- **No Lead Score or engagement scoring field** is visible — the pipeline stage progression in [COLD] tracks email opens, but there is no single engagement score field that aggregates intent signals across both pipelines. This limits the ability to prioritise follow-up across a large cold list
# Appointment-Level Attendance Boundary

`strength assessment showed`, `strength assessment booked`, opportunity stages and other contact-level tags remain routing signals. They cannot prove which appointment event was attended and must not be used as the attendance database.

The governed attendance record is keyed by GHL appointment event ID. No Show and Cancelled recovery continue to depend on their exact GHL appointment statuses; missing consultant feedback does not trigger either path.
