# Drive Process Audit: `2. The Evolved`

**Audited:** 18–22 July 2026  
**Inventory revalidated:** 5 August 2026  
**Status:** Complete; current SOP discovery and reconciliation are closed  
**Drive root:** `2. The Evolved`
**Purpose:** Identify current operational knowledge worth reconciling into the workspace without importing stale, duplicated, private, or client-sensitive material.

## Authority Rule

Drive is an intake source, not the final source of truth. Training and delivery content must be reconciled into `reference/evolved-manual/`, then `reference/sops/`, then trainer-portal Markdown and HTML. Live GHL configuration and the maintained workspace override older Drive descriptions when they conflict.

Passwords, employee and contractor records, invoices, client files, private internal folders, and personal financial documents were deliberately excluded.

## Folder Triage

| Drive area | Priority | Finding | Workspace destination |
|---|---|---|---|
| Sales | High | Current Strength Assessment script and a July 2026 Strength Assessment SOP exist alongside legacy transformation packages. | Compare with `reference/evolved-manual/02-assessment-system.md`, sales system docs, and the current offer library. |
| On-boarding | High | Four-session Fundamentals template, timetable guides, intro checklists, welcome assets, and life-stage emails overlap the member journey. | Reconcile through manual sections 02 and 07, then onboarding SOPs and trainer portal. |
| Delivery | High | Current session checklist, assessment sheet, program manual, periodisation, and movement resources overlap the delivery manual. | Reconcile through manual sections 03 to 06 and 09 before any SOP/course changes. |
| Retention | High | Retention OS v1 contains a strong five-layer framework but mixes operating rules, ideas, proposed pipelines, and named-role assumptions. | Feed approved concepts into manual sections 07 and 08 and the retention roadmap. |
| Cancellations | Medium | April 2026 “current state” documents predate the July rebuild. | Treat as historical input; the live GHL audit and current cancellation workspace docs are authoritative. |
| Team / S.O.Ps | High | Structured Admin, Sales, and Delivery folders contain the most recent operating procedures. | Compare each file against `reference/sops/`; migrate through the cascade rule. |
| Marketing | Medium | Valuable knowledge exists, but the folder is legacy-heavy and includes old campaigns and offers. | Audit by campaign when its system is next changed. |
| Brand | Low | Mostly media and design assets rather than operating processes. | Retain in Drive; import only when a specific content project needs them. |
| Adjacent Products | Low | Supplement-line material only. | No current migration. |

## Continuation Inventory: 20 July 2026

The root and priority operating folders were re-inventoried directly from Drive. The structure confirms that recency and operational authority are not aligned with the top-level folder names: the freshest procedures are generally under `7. Team / S.O.Ps`, while the older top-level Sales and Marketing folders contain a mixture of historical offers, campaigns and reference material.

| Area inspected | Current-looking material found | Audit disposition |
|---|---|---|
| Team / S.O.Ps / Admin / Strength Assessment | Pre-Qualification Conversation, trainer summary prompt, no-reply procedures, rescheduling and out-of-gym signup | High priority. Reconcile against the now-updated Strength Assessment system and live GHL before importing any remaining admin instructions. |
| Team / S.O.Ps / Admin / Calendar | Trainer availability, casual-trainer booking, PT rebooking, trainer transfer and late-cancellation procedures | High priority operational review. Validate current owners, calendars, timetable tools and payment rules. |
| Team / S.O.Ps / Admin / Enquiries | Pricing Enquiry Response | High priority because acquisition no longer routes to sales calls. Check that it directs prospects to the current Strength Assessment or appropriate nurture path. |
| Team / S.O.Ps / Admin / Membership Holds | Hold submission check and Stripe/task processing SOP | Compare with the verified live Hold OS and current workspace hold documentation. Live GHL remains authoritative where they differ. |
| Team / S.O.Ps / Admin / Membership Cancellation | May 2026 Stripe and PT-appointment processing SOP | Compare with the rebuilt July cancellation system. Treat it as staff-processing detail, not as proof of current automation behaviour. |
| Team / S.O.Ps / Sales | July-updated Strength Assessment SOP | Reconciled on 18 July 2026. This remains the strongest Drive sales source. |
| Team / S.O.Ps / Delivery | Introduction Sessions plus six service-delivery SOPs | Review after the onboarding allocation and client-facing service names are fully reconciled. `Sculpt & Strength (SGPT)` requires naming alignment with `Strong, Fit & Flexible Membership`. |
| On-boarding | Four Intro Session checklists, Fundamentals template, two timetable guides and member-email/forms folders | High-value but internally duplicated. Determine the canonical timetable guide and align the four-session material with the confirmed 0/1/4 onboarding allocation by offer. |
| Delivery | Session checklist, 2025 periodisation sheet, assessment sheet, success pathway and toolkits | Manual and evidence intake, not automatic migration. The workspace manual remains the source of truth. |
| Retention | Retention Operating System v1 | Strategy input for the Day 29–365 rebuild; proposed pipelines, scoring and roles are not live facts. |
| Cancellations | Two April 2026 current-state documents and a March 2025 email | Historical input. July live GHL and workspace documentation supersede the automation description. |
| Top-level Sales | One current-style Strength Assessment script, FAQs, goal emails, offers and several 2023–24 Evolve You package documents | Mixed. Keep the Strength Assessment script and active reference material; move legacy offer material to the existing Sales Archive after dependency review. |
| Marketing | Seminar scripts, old event/campaign folders, email banks, agents and website material | Review by live campaign dependency. Do not bulk-import or treat folder presence as evidence that a campaign is active. |

### Structural risks confirmed

- Two Program Delivery Manual documents remain side by side in Team: the older manual and `2.0`. The workspace manual hierarchy is canonical; Drive versions should be labelled as intake/reference to prevent staff treating both as current.
- On-boarding contains both `How to Use The Timetable` and `PM | How to Use the Timetable at The Evolved`. Their overlap and ownership need review before either is migrated.
- The top-level Sales folder has an Archive folder, but several obsolete Evolve You transformation-package documents still sit outside it. They are not current offers and should be dependency-checked before being reorganised.
- Team contains private operational material, including credential and personnel areas. These remain deliberately excluded from workspace migration.
- Drive document recency alone does not prove live use. Every operational candidate still needs comparison with GHL, Stripe, Trainerize and the current workspace source before adoption.

## High-Value Documents Reviewed

### Strength Assessment SOP and sales script

The Drive SOP is more current than the older generic sales script and confirms an in-person consultation, physical assessment, offer presentation, and immediate sign-up process. It contains useful operational detail, but also conflicts and risks that prevent direct import:

- package names and prices must be checked against the current offer source;
- the assessment standards and health claims need evidence and manual alignment;
- the SOP contains credentials and must be sanitised before migration;
- role references such as Nora may not match current ownership;
- the Drive SOP and workspace assessment framework use overlapping but not fully identical terminology.

Decision completed 18 July 2026: the July SOP was reconciled through the manual, source SOP, verbatim script, systems SOP, trainer-course Markdown and trainer-course HTML. The Drive source was also updated with the approved offer, Admin Eve role ownership, PAR-Q gate, Trainerize/GHL data ownership, and 24-hour No Sale rule.

Decision completed 23 July 2026: `reference/sops/post-sale-member-onboarding.md` now governs the immediate post-sale handoff. It replaces historical ACR, PT Minder and old package-name instructions with the live GHL task, current Trainerize products, approved 999-credit model, package provisions, first-session booking and Admin Eve day-two quality control. The matching Drive document lives in `S.O.Ps / 3. Delivery`.

The related Pre-Qualification SOP allows any trained owner, admin or coach to continue the conversation and prepare the trainer summary. Injury questioning stops once the information is trainer-actionable and no safety issue remains unresolved; the responder then uses the confidence-building transition and continues to Exercise History.

Admin Eve or another authorised admin manually moves a fully screened opportunity from Assessment Booked to Pre-Qualified after the shared completion map is satisfied. This remains manual until the future pre-qualification bot is verified.

### Pricing Enquiry Response and framework

The one-page Admin SOP contains no sales-call booking instruction. It tells Admin to use a separate AI response framework, review the generated reply and match its length to the channel. This is directionally compatible with the current acquisition model, but it is not self-contained and does not identify the authoritative framework location or version.

The linked Pricing Response Framework routes prospects toward a Strength Assessment rather than a phone call, but it is internally contradictory and should not be treated as current without revision:

- its opening structure says to provide the correct $69–$149 weekly range, while the embedded master prompt later forbids all prices and ranges;
- one section directs a prospect to the waitlist and a conditional Strength Assessment calendar, while the direct-version prompt says not to invite immediate booking;
- it says pricing is determined after the Strength Assessment, but the offer prices are fixed. The assessment determines the recommended service, not the price of that service;
- it calls the business a high-touch personal-training studio, which does not accurately describe every active tier;
- it does not name the current Fit & Flexible, Strong, Fit & Flexible Membership and Fast Track offer set or explain the confirmed upfront and week-4 payment structure.

Completed 21 July 2026: the Drive framework and Admin SOP were rewritten and renamed. The canonical response now discloses the $69–$149 weekly range and $299–$599 upfront range, explains that the Strength Assessment determines the recommended membership rather than the price, and directs West End prospects to the current waitlist and Strength Assessment availability path. Location enquiries use the registration-of-interest update and West End redirect; all conflicting price-avoidance, non-booking and sales-call instructions were removed.

Extended 30 July 2026: both canonical Drive documents now govern the narrow exception of low-intent pricing emails sent to `info@theevolvedgym.com.au` to circumvent the published intake funnel. The approved range acts as an early self-selection filter for likely price-led prospects; the outward response remains neutral, states genuine capacity, reinforces the value of coaching and support, and returns the sender to the waitlist and Strength Assessment pathway. Genuine pricing questions from prospects already engaging with the intake journey remain under the normal conversation standard. The approved exception email template is also recorded in `outputs/systems/sales-conversion.md`.

### Membership hold admin SOPs

The short `Check Membership Hold Submission` document only points staff to the generic GHL survey-submissions page. That is useful as a fallback lookup, but it omits the live task-first operating path, the Hold OS pipeline, approval status and which request should be worked next.

The longer Stripe SOP is no longer safe as the default membership-hold procedure. It tells Admin to manually pause payment collection until a custom date, while the live July Hold OS now calculates Pre-Hold-Start and Pre-Return dates and uses the Railway webhook to apply overlap credit, pause the subscription and schedule resumption. Standard membership holds still create Admin Eve verification tasks, but verification is not the same as manually recreating the pause.

Completed 21 July 2026: the Drive document was renamed `SOP: Process a Membership Hold (GHL + Billing OS)` and rewritten as a task-led verification and exception runbook. The default path is now task → contact fields → Hold OS stage/status → Stripe verification. Manual intervention is limited to prepaid-pack or other non-subscription cases, a logged automation failure or an explicitly approved exception.

### Cancellation Stripe and PT-appointment SOP

The Drive procedure correctly preserves the 30-day notice intent, checks the final payment and removes future PT appointments. However, it still instructs Admin to schedule the Stripe cancellation manually. The live July Membership and PT Cancellation workflows now call the Billing OS webhook five minutes after submission and schedule `cancel_at` automatically.

The current Admin Eve role is therefore verification and exception handling: confirm the webhook result, final payment and service entitlement, then reconcile PT appointments. The maintained workspace rule keeps the calendar week immediately after the final payment as the final PT service week and deletes sessions after that week; unclear cases escalate to Peter before appointments are deleted.

Completed 21 July 2026: the Drive document was renamed `SOP: Process a Cancellation and Reconcile PT Appointments`. The manual default Stripe steps were replaced with Billing OS verification, failure handling and non-subscription exceptions. The appointment example now follows the maintained final-service-week rule, and the live cancellation workflow is the source of the Admin Eve processing task.

### Admin calendar procedures

Reviewed 21 July 2026: the Admin calendar folder contains a trainer availability sheet, a casual-trainer booking SOP, a 13-week PT rebooking placeholder, a trainer-transfer campaign and the late-cancellation procedure.

The availability sheet is neither complete nor aligned with live GHL. The user approved its deletion on 21 July 2026, but the connected Drive account cannot move it to the bin because it lacks permission. An owner or suitably authorised Drive account must delete it. In GHL, Marnie's three PT calendars and all three Meroe PT calendars were deleted. Kanika's replacement schedule was created and verified in Nora's calendar before all 22 future Meroe records and the final calendar were removed. Deleting the calendar also removed Kanika's completed 23 June session from GHL's active contact-appointment feed; this audit retains the occurrence as historical evidence.

The casual-trainer SOP contains useful operating principles: honour the minimum shift, cluster appointments back-to-back, build around anchor sessions and avoid opening another day before existing shifts have sufficient density. These principles should be retained in a person-neutral scheduling SOP after the current employment and contractor rules are confirmed. Its named-person example is not a reusable rule.

`Re-Booking PT for 13 Weeks` contains only its title and no procedure. It is not an active SOP and should either be built from the live booking system or archived after confirming that no staff process links to it.

`Moving Clients Over To A New Trainer` is a one-off Leisa-to-Piper transition campaign, not a general trainer-transfer SOP. It contains dated availability, Nora-specific wording, client contact and case details, and an exposed credential. Do not migrate it into the workspace. Rotate the exposed credential, remove or relocate the sensitive material, and replace the file with a sanitised process only after the current transfer policy is approved.

The future canonical transfer procedure should cover authorisation, service-duration and availability matching, coach handover in Trainerize, member choice and confirmation, GHL ownership and recurring-appointment updates, any prepaid-pack or payroll reconciliation, and a final check that the next appointment is correctly assigned. Current GHL calendar configuration and availability must be the scheduling source of truth; Drive should explain the procedure, not duplicate a live roster.

### Admin reviews procedure

Reviewed 21 July 2026: the folder contains only `Failed Review Link: Send This`, a manual fallback for a 4- or 5-star response when the automated Google-review SMS does not run. The live published workflow is active and materially more complete than the existing workspace description: it enrols on `send review request`, waits 14 days, asks for a 1-to-5 SMS rating, branches positive and negative responses, tracks the review-link click, performs follow-ups and sends thank-you messages.

The fallback remains useful as an exception procedure, but it should not be treated as the review SOP. Rewrite it later to require an execution-log check, use the canonical GHL review-link source, record the manual intervention and prevent duplicate sends. The upstream sources that add `send review request` are now mapped. Final `Review Received` ownership remains an owner decision; the recommended control is a weekly Google Business Profile reconciliation by Admin Eve.

### Admin conversations procedures

Reviewed 21 July 2026: the folder contains an important-links list, a conversation-triage procedure and a response note for the new-member seven-day check-in.

The triage procedure has a useful core: review unread conversations, summarise the request, classify urgency, complete work covered by an approved SOP and escalate exceptions. It is not ready to be canonical because it sends unresolved items to a personal phone number, names the owner rather than an operational role, and classifies marketing, equipment and non-immediate-revenue enquiries as not important. Replace this with an Admin Eve queue, service-risk and response-time rules, named escalation roles and a record of the action taken inside GHL.

The seven-day response note corresponds to a real workflow handoff. On 22 July 2026 the Day 7, Day 8 and Day 9 reply paths in `Membership: First 7 Days` were upgraded with GHL AI Intent Detection on `{{message.body}}`. The premium action costs USD $0.01 per classified reply and routes each response to Positive, Negative or None. The workflow was saved and remained set to Publish. No automated member acknowledgement was added, which avoids duplicating a human response.

Positive and Negative branches now create separately assigned tasks for the GHL staff accounts `Admin Eve` and `Piper Mae`. Admin owns the written response and GHL detail; Piper owns a personal in-gym follow-up to reinforce a positive response or gather more information behind a negative response. Negative branches automatically remove the member from `Google Review Request (4 & 5 Stars Only)` before its Day 14 message. The separate Day 9 no-reply branch was not changed.

The None branch assigns Admin Eve a manual-classification task. Its instructions also provide the correction control: a false positive can be removed from the review workflow and routed to Piper as a negative follow-up; a false negative can be kept or re-entered in the review workflow and routed to Piper as a positive follow-up. Admin must correct both the review-workflow state and Piper ownership before completing the task. The previous single Admin notifications on all three reply paths were deleted. Injury-specific red-flag escalation still needs a confirmed owner and response standard.

The Drive document `IMPORTANT LINKS` was live-validated on 30 July 2026. All six destinations return successfully. The standard Membership Hold, PT Hold and Membership Cancellation entries use the branded website routes; the three Bitly links resolve to the current GHL Extended Membership Hold survey (`Q9BRXF5zpiQjDoVB1Diy`), Extended PT Hold survey (`bvz7PVsqRY5akgHfOHkH`) and PT Cancellation survey (`JnwGk9ttNxiSAuqBxuBs`). No broken staff link was found.

The remaining issue is governance and presentation consistency, not link functionality. Owner direction on 30 July established that staff-facing cancellation links should use the Membership Cancellation Form's progressive structure, while extended hold forms should achieve presentation and control parity with their standard hold counterparts. Do not merely replace the Bitly URLs with raw widget links. Build branded extended-hold routes first, complete the PT cancellation redesign, then update `IMPORTANT LINKS` to the maintained branded destinations. Treat the GHL form/source register as authoritative so future replacements are updated once and verified before staff documentation changes.

The same live audit found one incomplete opportunity action in `3.0 New Member`: Membership Pipeline was selected but the stage was blank. This was repaired on 24 July 2026 by assigning the confirmed Fit & Flexible stage. The workflow also retains a `Remove from Studio Appointment Workflow` action after that acquisition path was retired. That remaining dependency check is an onboarding-system fix, not a change to the conversation SOP.

### Admin reporting procedures

Reviewed 22 July 2026: the Drive reporting folder contains `1. S.O.D Report`, `2. E.O.D Report` and `Weekly KPI Entry`. The separate `Admin Task Tracker` has Daily Tasks and Weekly Tasks tabs. Daily Tasks contains only three undated checkboxes for the S.O.D report, message triage and E.O.D report; Weekly Tasks is empty. It has no owner, due date, recurrence history, evidence link or exception trail, so it is not a reliable accountability system.

The S.O.D and E.O.D documents require Admin to copy conversation names into historical stages `2A` to `2F`, report sales and assessments manually, email two named people, then text two personal mobile numbers to confirm the email was sent. These stages do not match the live WARM Sales stages: Assessment Booked, Pre-Qualified, No Show, Cancelled, Show, FUM and FUNQ. The process duplicates GHL rather than governing it, relies on person-specific channels, and creates no durable operational record. Do not migrate either document as a current SOP.

Any replacement daily report should be exception-led. Admin Eve should work from GHL Conversations, Tasks and the WARM Sales pipeline, record unresolved items in the system of record, and escalate only items that are overdue, unsafe, blocked or outside an approved SOP. Sales, assessment and pipeline totals should come from the maintained KPI data rather than being re-counted in an email.

The Weekly KPI date rule is still conceptually correct: each Monday-dated column reports the preceding Monday-to-Sunday period. The rest of the document is outdated. It tells Admin to count GHL contacts, calendar bookings, Sales rows and cancellation submissions manually, while the live KPI workbook already receives raw GHL rows and uses formulas for subscribes, leads, bookings, attendance, sales, new cash collected and cancellations. Current manual inputs are Cash Collected and ad spend, followed by verification and the workspace `update-metrics` refresh.

A separate workspace labelling gap was found during this comparison. The live 20 July column formulas count 13–19 July, but `update_metrics.py` renders the output as `week of 20 Jul 2026`. The values are correct; the displayed period label is misleading. Correct the generator to show `week ending 19 Jul 2026`, or an explicit `13–19 Jul 2026`, before using the label in board reporting.

### Trainerize admin procedures

Reviewed 22 July 2026: the Drive Trainerize folder contains two screenshot-led SOPs created in May 2026. Both repeatedly misname Trainerize as `TrainRise` or `TranRise`; these are transcription errors, not separate systems.

`SOP: Remove a Client from a Group Program and Assign a One-on-One PT Program` contains useful mechanics that align with current workspace knowledge: remove the member from the group, import rather than subscribe when client-level editing is required, choose the pre-built 1-, 2- or 3-session weekly PT program, align the new start date after the prior program, preserve the Foundations, Building, Performance and De-load sequence, schedule the member's actual training days, and verify the imported phases. The three frequency-specific programs and four-phase cycle are consistent with the current trainer portal and draft cycle-duplication SOP.

It is not safe to adopt wholesale. The document mixes Admin operations with programming decisions, uses a named client example, and allows exercise substitution for back aggravation without requiring the current injury documentation and escalation standard. Admin may remove or assign programs only from an approved service-change instruction. The responsible coach must choose client-level exercise changes, preserve programming variables, document the reason in Trainerize and follow the modification, stop and referral rules. Before migration, split this into an Admin service-change checklist and a coach-owned programming procedure, then complete the source-first manual and SOP cascade.

`SOP: Change a Trainer on a Class in Trainerize` accurately describes the current visible method as a week-by-week class edit, but it is incomplete governance. It does not distinguish temporary cover from permanent ownership, define the approved date range, require a source roster, record who authorised the change, update payroll or timesheet implications, or provide a reversal step for cover sessions. Its Megan-to-Nora example is not a reusable rule. Retain the mechanics as intake evidence, but rebuild the procedure around authorisation, effective dates, attendance ownership, cross-system roster checks and final verification. This directly overlaps the existing cover-session coach-attribution gap.

The Trainerize API workspace integration and longitudinal audit remain read-only evidence systems. They can verify roster, calendar and training-record coverage, but they are not presently an approved write path for program assignment or class-trainer changes.

### Fundamentals onboarding template

The template describes four intro sessions covering goals, app setup, squat and hinge assessment, nutrition, bracing, follow-up messages, and coach handoff. It is operationally valuable, but it also includes old pricing, a nutrition-coaching model that may no longer match the current offer, and several steps that appear manual or tool-specific.

Decision: extract the four-session structure and handoff requirements during the member-journey rebuild. Validate all nutrition, pricing, measurement, photo-consent, and Trainerize steps before adoption.

### Retention Operating System v1

The strongest reusable model is the five-layer framework: Identity, Connection, Experience, Intelligence, and Behaviour. It also proposes milestone recognition, named greetings and farewells, member-profile enrichment, pattern-disruption alerts, and single-habit interventions.

The document is partly strategy and partly speculation. The proposed Retention OS pipeline, Trainerize integration, Strength Circles, role allocations, scoring model, and milestone taxonomy are not confirmed live.

Decision: add the five-layer framework and early-risk concepts to the retention rebuild backlog. Do not describe the proposed pipeline or automation as current state.

### Program Delivery Manual 2.0 and session checklist

The Program Delivery Manual 2.0 is largely a detailed table of contents and vision for a complete method. The workspace `reference/evolved-manual/` already implements this structure as the maintained source hierarchy.

The session checklist adds practical behaviours: preparation, personalised greetings, attendance reconciliation, member introductions, three coaching touchpoints, session wrap-up recognition, and named farewells. Some tool and social-media instructions require current policy review.

Decision: map checklist behaviours into trainer standards during a dedicated content-intake task. The workspace manual remains authoritative.

## Conflicts to Resolve Before Migration

1. Current offer names, inclusions, pricing, and cancellation terms.
2. The exact four-session onboarding model and whether nutrition coaching remains included.
3. Strength-test standards and claims used during sales consultations.
4. Current software ownership between GHL, Trainerize and Stripe, including the missing prepaid-pack session ledger.
5. Remaining named-person ownership outside the reconciled Strength Assessment documents; assessment administration now uses the person-neutral Admin Eve role.
6. Photo/video capture consent and social-media expectations.
7. Whether milestone tiers and Strength Circles are approved operating systems or ideas.

## Recommended Migration Order

1. Strength Assessment SOP content intake and evidence check. Completed 18 July 2026; live GHL outcome-routing repairs remain open.
2. New-member onboarding and Days 1 to 90 journey.
3. Retention system, including early-risk detection and milestone recognition.
4. Session-delivery checklist and trainer standards.
5. Admin SOP folders, beginning with Strength Assessment, enquiries, calendar, holds, reviews, and cancellations.
6. Marketing and legacy sales archive review only after live operating systems are reconciled.

The Pricing Enquiry Response, hold, cancellation, Admin calendar, Admin reviews, Admin conversations, Admin reporting and Trainerize folders are complete. The trainer-transfer SOP, 13-week PT rebooking procedure, daily reporting replacement and Trainerize service-change governance remain controlled rebuild decisions rather than Drive discovery gaps. Nora's assessment location, cover-session attribution, review-tag provenance and the incomplete `3.0 New Member` opportunity action were closed on 24 July 2026. Subsequent GHL ownership and task-provenance work was reconciled in the backend and workflow-owner registers before final audit closure on 5 August 2026.

This audit brings the usable knowledge map into the workspace now. Content that changes delivery or trainer-facing instructions remains queued for a formal source-first cascade so the workspace does not create a second conflicting SOP library.

## 5 August 2026 closure revalidation

The connected Drive inventory was reread across `7. Team / S.O.Ps / 1. Admin`,
`2. Sales` and `3. Delivery`. The current folder contents match the audit above:
the Strength Assessment, pricing, hold, cancellation, calendar, review,
conversation, reporting, Trainerize, onboarding and service-delivery sources
are all represented in this register. No unreviewed current-looking SOP appeared
in those folders.

`Trainers Availability and Contact Details` and its Admin-folder shortcut remain
present because the connected account still cannot delete the owner-controlled
source. They remain explicitly non-canonical; live GHL calendars are the
scheduling source of truth. The incomplete 13-week rebooking placeholder,
trainer-transfer campaign, daily reporting replacement and Trainerize
service-change governance remain documented rebuilds rather than audit gaps.
Accordingly, the Drive-process discovery and reconciliation tranche is closed.
