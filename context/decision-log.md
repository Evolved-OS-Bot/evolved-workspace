# Evolved Decision Log

Record material owner decisions that change canonical business rules, architecture, privacy boundaries, live-system behaviour or workstream priority.

Detailed evidence may remain in dated plans and build records. This log provides the durable decision pointer.

## Entry contract

- Date
- Decision
- Owner
- Evidence and alternatives considered
- Canonical sources affected
- Required cascade
- Verification or review date
- Links to detailed evidence

## 2026-08-05: Hold Return delayed writes fail closed to the accepted cycle

- **Decision:** Every delayed Returning or Completed mutation in `HS: Hold Return Journey` must prove that the live contact still represents the protected accepted hold cycle. Preserve re-entry for a later valid cycle, disable simultaneous workflow opportunities, and route a mismatch to one same-day deduplicated Admin Eve exception task without member messaging or a Stripe change.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** A production record proved that an older enrolment can remain active after a newer cycle is accepted and later overwrite the newer lifecycle. The intake-side one-open-hold control cannot protect an enrolment that already exists. Status-only checks were rejected because partial field overwrites can leave plausible status with impossible or cross-cycle dates.
- **Canonical sources affected:** `outputs/systems/membership-hold.md`; `outputs/systems/ghl-backend-register.md`; `plans/2026-04-13-hold-return-journey-workflow.md`; `context/roadmap.md`; `context/control-plane-status.md`.
- **Required cascade:** Reset the guard status to Not Checked before each webhook; Billing OS verifies protected/current start identity, Accepted intake, chronology, Pre-Return derivation, expected status and exact execution day; both workflow writes use explicit Passed/None branches; mismatches attempt workflow removal and create one controlled Admin exception.
- **Verification or review date:** The 39-test Billing OS suite and disposable-contact normal, completion and overlap acceptance passed on 5 August 2026. The saved published workflow was reloaded and both guard paths read back.
- **Detailed evidence:** `outputs/systems/membership-hold.md`; `scripts/verify_hold_return_guard_live.py`.

## 2026-08-04: PT appointment storage is always individual

- **Decision:** Store every PT booking block, reschedule, transfer and rolling top-up as separate GHL appointments with `isRecurring=false`. Never create a bounded or open-ended recurring master. The default horizon is 13 individual appointments per entitled weekly pattern; any owner-approved different count remains individual.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** A complete live audit found 18 PT recurring masters: ten created during the prior week's rescheduling work and eight older series. The operative rescheduler plan incorrectly endorsed bounded RRULE storage, and the first audit filter also missed a valid Piper 1:1 calendar because its displayed name did not contain `PT`. Bounded recurrence and calendar-name filtering were rejected.
- **Canonical sources affected:** `CLAUDE.md`; `reference/sops/active-client-payment-and-booking-reconciliation.md`; `plans/2026-04-27-natural-language-appointment-rescheduler.md`; `outputs/systems/pt-weekly-audit-run-sheet.md`; `outputs/systems/pt-booking-shadow-review-log.md`; `context/roadmap.md`.
- **Required cascade:** Complete. The ten prior-week series and eight explicitly approved older series were corrected into 223 verified individual appointments with notifications suppressed. Calendar discovery uses the governed current-and-retained 1:1 registry, and every affected target was checked for one individual appointment and no recurring source.
- **Verification or review date:** Final read-only audit completed 4 August 2026 across all 18 current and retained 1:1 calendars from 4 August 2026 through 2 February 2027. It found zero future recurring PT events.
- **Detailed evidence:** `outputs/systems/pt-booking-shadow-review-log.md`.

## 2026-08-04: Peach phase-one animation platform and approval controls

- **Decision:** Build Peach's phase-one reusable animation system in Apple Motion 6.3, use Final Cut Pro 11.0.1 for editing and template use, and use Compressor 5.3 for export presets. Build the three-quarter rig first inside the Evolved workspace. Exclude dialogue, lip-sync and interactive website animation. Use the foundation-pack review reel as the first acceptance test. Preserve approved static masters and require Peter's explicit visual approval for the visibly rebuilt source, the rig and every reusable motion before promotion.
- **Visual-target approval:** Peter Brown stated, “Approve PEACH-LAYER-three-quarter-candidate-v1 as the neutral visual target for full layered construction.” This approval is limited to the neutral visual target and excludes the completed layered source, Motion rig, motions, expressions, templates, export paths, external publication and contractor handoff.
- **Layered-source approval:** Peter Brown stated, “Approve PEACH-LAYER-three-quarter-layered-source-v10 as the editable layered source and identity base for Apple Motion rig construction. This does not approve the rig, provisional pivots, root-cover masks, motions, expressions, templates, exports, or deployment.” The exact 29-layer package is frozen under `outputs/evolved-heroine/animation/rigs/approved/`.
- **Frame-rate decision:** Peter Brown authorised **30 fps** as the canonical phase-one animation-system frame rate on 4 August 2026. This fixes project timing only; it does not approve the rig, pivots, root-cover masks, motions, expressions, templates, exports or deployment.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The project execution brief authorises a proper reusable production system rather than one-off AI animation. Apple Motion preserves the approved raster texture and is already owned; Lottie and Rive would require a separate vector reconstruction, while Moho or Adobe may be reconsidered only if later requirements exceed Motion's controlled cutout capabilities.
- **Canonical sources affected:** `reference/evolved-heroine/animation-system.md`; `plans/2026-08-04-peach-animation-project.md`; `context/roadmap.md`.
- **Required cascade:** Audit the Apple environment and approved assets; approve the neutral reconstruction and layered source; build and approve the editable rig; build and approve ten motions and eight expressions; verify five templates and export paths; complete the review reel, indexes, QA evidence, versioning and handoff.
- **Verification or review date:** Environment and source audit completed 4 August 2026. Peter approved exact-hash `PEACH-LAYER-three-quarter-candidate-v1` as the neutral visual target, later approved exact-neutral, 29-layer `PEACH-LAYER-three-quarter-layered-source-v10` as the editable layered source and animation identity base, and fixed the canonical phase-one frame rate at 30 fps on 4 August 2026. The Motion rig must still resolve the recorded leg-root cover gap and remains separately gated with every reusable motion.
- **Detailed evidence:** `outputs/evolved-heroine/animation/records/PEACH-feasibility-record-v1.md`; `outputs/evolved-heroine/animation/review/layered-reconstruction/PEACH-LAYER-three-quarter-candidate-v1-review.md`; `outputs/evolved-heroine/animation/qa/approvals/PEACH-LAYER-three-quarter-layered-source-v10-editable-source-approval-2026-08-04.json`.

## 2026-08-04: Pregnancy funnel next-step authority and fallback route

- **Decision:** Treat `/pppsa-page-1536` as the current Pregnancy organic thank-you and Strength Assessment page. HighLevel funnel next-step logic controls an embedded form submission; the form's On Submit redirect is only the fallback outside the funnel. Preserve stale alias `/pppsa-5667` until its provenance and safe disposition are tested.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** Peter identified the correct live page and clarified the HighLevel sequencing rule. The supplied route returned 200 with thank-you and Strength Assessment booking content. Its public metadata matched the already-captured Pregnancy organic funnel ID, middle-step ID, page ID and booking-confirmation next-step ID. Treating the 404 Publishing alias as proof that the embedded funnel journey fails was rejected. Redirecting the organic form fallback to paid route `/pppsa` was also rejected.
- **Canonical sources affected:** `reference/conversion-funnel.md`; `outputs/systems/website-v2-release-manifest.md`; `outputs/systems/website-v2-ghl-route-register.json`; `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`; `outputs/systems/website-sitemap.md`; `outputs/systems/website-architecture.md`; `context/roadmap.md`.
- **Required cascade:** Change only the standalone `30DNNC Form - PPP` fallback to `/pppsa-page-1536`, reload-verify it, expand the protected GHL route lower bound to 85, retain both Pregnancy aliases and both funnels, and prove the funnel-controlled journey with an owned test contact during the approved rehearsal.
- **Verification or review date:** The public page returned 200 and the saved form fallback read back on 4 August 2026. Controlled submission remains Phase 4 acceptance work.
- **Detailed evidence:** `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`; `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`.

## 2026-08-04: Cancellation contact evidence and owner escalation

- **Decision:** Stop relying on Piper as the sole writer of `cs: contact made`. During an active membership-cancellation notice, a member reply automatically writes the compatibility tag and evidence source. A call counts automatically only if native GHL conditions can prove an outbound connected call lasting at least 60 seconds; otherwise it stays review-only evidence. Add a final evidence check immediately before Day-14 escalation and replace the automatic client SMS in Megan's name with a same-day Megan review task. Exclude `MC: Other (Booked Call)` because that member explicitly requested manager contact.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** A reviewed notice-period case contained multiple replies and substantive Piper calls but no manual tag, so the workflow described the member as uncontacted and sent an automatic message in Megan's name. Keeping the manual tag as the sole control was rejected. Treating `Completed`, voicemail or ringing as answered was rejected because GHL/Twilio status does not reliably prove a live conversation. A global stop-on-reply was rejected because it would also suppress useful later notice-period steps.
- **Canonical sources affected:** `outputs/systems/cancellation-system.md`; `outputs/systems/cancellation-mc-reason-workflows.md`; `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`; `outputs/systems/ghl-backend-register.md`; `context/roadmap.md`.
- **Required cascade:** Complete. The reply helper is Published; the call writer failed closed because GHL exposes no duration filter; all eight Piper-led reason workflows were reload-verified with a same-day Megan review task and no automatic owner SMS; all four active notices were reconciled without member messaging. Lucinda Gibson and Sarah Loga were the two proven-reply backfills.
- **Verification or review date:** Live build, active-notice reconciliation and read-back completed 4 August 2026; review after the next cancellation reaches each early evidence gate and the next Day-14 review task.
- **Detailed evidence:** `plans/2026-08-04-cancellation-contact-evidence-and-owner-escalation.md`; `outputs/systems/cancellation-contact-evidence-acceptance-2026-08-04.md`.

## 2026-08-04: COLD pipeline terminal-state semantics

- **Decision:** Use `Won` when a 30DNNC contact books a Strength Assessment or otherwise becomes an active client. Use `Abandoned` when the contact completes the course without an assessment or when an incomplete course opportunity remains unchanged beyond the governed 45-day stale boundary. Keep only current course progress Open.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The complete 4 August snapshot found 760 unique COLD opportunities and all were Open because the five course workflows and Strength Assessment handoff have no terminal-state control. The approved exact reconciliation is 354 Won conversions, 152 Abandoned completed non-conversions, 198 Abandoned stale incomplete records and 56 retained current-course records. Lost was rejected because a completed or disengaged course contact remains a valid future marketing prospect.
- **Canonical sources affected:** `outputs/systems/lead-generation-nurture.md`; `outputs/systems/ghl-backend-register.md`; `context/roadmap.md`.
- **Required cascade:** Complete. The exact 704-record status batch passed per-record preconditions and read-back verification, producing 354 Won, 350 Abandoned and 56 protected Open records. The terminal COLD-Abandoned control is live and independently reload-verified in all five delivery workflows. The published Strength Assessment workflow now applies the guarded COLD-Won control only to `30dnnc` contacts with an existing `[COLD] Marketing Pipeline` opportunity; found, no-record and direct-assessment paths all rejoin `Previously Assessed?`. Post-save reload verified the action settings, exact topology, Saved state and Published state without creating a false COLD opportunity for direct assessment bookings.
- **Verification or review date:** Immediate live reconciliation and workflow read-back on 4 August 2026; review new COLD entries after one complete 30DNNC cycle.
- **Detailed evidence:** `data/private/integration-reporting/cold-pipeline-audit-20260804.json`; `data/private/integration-reporting/cold-pipeline-reconciliation-result-20260804.json`; `outputs/systems/lead-generation-nurture.md`.

## 2026-08-04: Preserve the complete captured GHL route boundary

- **Decision:** Preserve every captured GHL website and funnel path through the root-domain rehearsal and observation window. The 19 public paths are only the exact root-to-`go.` redirect set; they do not authorise omission or deletion of the other configured GHL steps. Do not use blanket root or `blog.` redirects or global URL replacements.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** Peter directed that the full system be audited before commitment and that nothing be deleted or cut off. Parsing the protected GHL pages found 84 unique configured paths; the owner-confirmed Pregnancy page added one previously omitted live alias. The known lower bound is now 85 paths: 16 paths WordPress will own on the root, 19 public paths needing exact redirects to `go.` and 50 additional internal, confirmation, agreement, booking, alias or legacy paths that still require preservation. Treating 19 as the entire boundary would omit 50 known paths.
- **Canonical sources affected:** `outputs/systems/website-v2-release-manifest.md`; `outputs/systems/website-v2-ghl-route-register.json`; `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`; `outputs/systems/website-sitemap.md`; `outputs/systems/website-architecture.md`; `CLAUDE.md`.
- **Required cascade:** Validate the 85-path register against the protected GHL capture plus registered owner correction, use it in the isolated rehearsal and cutover acceptance, preserve the source GHL pages through observation, and require exact query-safe redirects only for the 19-path redirect subset.
- **Verification or review date:** Local register and protected-capture parity to be revalidated after this documentation update; live functional acceptance remains Phase 4 work.
- **Detailed evidence:** `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`; `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`.

## 2026-08-04: Website V2 is the built product for root-domain promotion

- **Decision:** Treat the existing WordPress Website V2 live at `blog.theevolvedgym.com.au` as the product to promote to the root domain. Do not plan a reconstruction from GHL or reopen V2 homepage, navigation, CTA or membership-design decisions without separate owner approval for a redesign.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The archived April implementation records state that the WordPress homepage and supporting site were built and live. The current public runtime verifies the V2 experience, homepage post 165, personalised results curve and waitlist journey. The superseded alternative treated post 165 as one of several homepage candidates and would have recreated already completed work.
- **Canonical sources affected:** `outputs/systems/website-v2-release-manifest.md`; `reference/conversion-funnel.md`; `outputs/systems/website-architecture.md`; `CLAUDE.md`.
- **Required cascade:** Preserve the superseded documents, create a governed source mirror and release register, separate root-promotion blockers from content backlog, add read-before-action rules and run the read-only drift checker before website work.
- **Verification or review date:** Governance recovery verified locally on 4 August 2026; live root promotion remains separately approval-gated.
- **Detailed evidence:** `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`; `outputs/systems/website-v2-release-register.md`.

## 2026-08-04: Complete live-system investigation standard

- **Decision:** Individual contact, workflow, billing, booking and lifecycle investigations must reconcile the complete live record rather than rely on one field, screen or partial workflow view.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** Rabail Aisha's contact showed a four-week structured selection, a seven-week free-text request, a staff promise to extend the hold, an unrecorded approval, blank billing acknowledgement, pending tasks and a later workflow overwrite. Reviewing only the status field or submission workflow produced an incomplete diagnosis.
- **Canonical sources affected:** `CLAUDE.md`; domain evidence remains in the applicable SOP or system document.
- **Required cascade:** Apply the rule to future GHL and cross-system audits; record contradictions and distinguish discussion, approval, processing and verification.
- **Verification or review date:** Effective immediately; revalidate during the next GHL audit tranche.
- **Detailed evidence:** `outputs/systems/membership-hold.md`

## 2026-08-04: Approve the seven-week extended membership hold

- **Decision:** Approve the accepted membership-hold period from 7 August 2026 through 20 September 2026 and preserve the original four-week form answers as immutable request evidence.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The structured form selected four weeks from 10 August, while the signed free-text request specified 7 August through 20 September. Admin told the member the seven-week extension had been processed, and PT Minder independently showed the six removed weekly periods and the 18 September payment-in-advance return-week debit. Keeping the original four-week calculation would contradict both the accepted request and live billing evidence.
- **Canonical sources affected:** `outputs/systems/membership-hold.md`; `context/roadmap.md`.
- **Required cascade:** Reconcile accepted-cycle and protected request fields in GHL, preserve a blank Billing OS result for the manual PT Minder action, close the obsolete exception task after read-back, and preserve date-accurate activation and return-workflow controls.
- **Verification or review date:** Accepted GHL fields and workflow eligibility read back on 4 August 2026; verify the dated On Hold activation on 7 August and Return Journey enrolment on 13 September.
- **Detailed evidence:** `outputs/systems/membership-hold.md`

## 2026-08-04: Membership service-change workflow filing

- **Decision:** Use the numbered GHL folder `8. Membership Service Changes` as the single workflow home for every workflow with the `MSC` prefix.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** Five related workflows were sitting at the GHL workflow root. A dedicated folder keeps the service-change family together without changing workflow behaviour or mixing it with the cancellation or hold systems.
- **Canonical sources affected:** `reference/sops/membership-service-change-control.md`; `outputs/systems/ghl-backend-register.md`.
- **Required cascade:** Move the two Evolved Anywhere and Online Only intake workflows and the three Strong commitment workflows into the folder; preserve each publication state; update the build record and roadmap.
- **Verification or review date:** Live read-back passed on 4 August 2026.
- **Detailed evidence:** `plans/2026-08-03-strong-12-month-commitment-control.md`

## 2026-08-04: Strength Assessment feedback fallback enrolment

- **Decision:** Preserve the normal `2. Strength Assessment` handoff into `2.4 Send Consultation Feedback Survey`, and add `strength assessment showed` as a fallback entry signal for first assessments. Disable re-entry in `2.4` so the normal handoff and fallback cannot produce two consultant prompts for the same contact.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** A cancelled appointment rescheduled in place retained its event identity. The original assessment workflow execution had already ended, no new execution reached `2.4`, and the delivered assessment therefore produced no internal consultant prompt. Replaying the complete parent workflow was rejected because it would repeat client-facing acquisition messages. An appointment-status trigger was rejected because GHL permits appointment-trigger re-entry even when workflow re-entry is disabled. The existing `strength assessment showed` tag is applied by the governed delivered-assessment path and supports duplicate suppression.
- **Canonical sources affected:** `outputs/systems/sales-conversion.md`; `outputs/systems/strength-assessment-attendance-control.md`; `context/roadmap.md`.
- **Required cascade:** Manually enrol the missed delivered assessment; publish the filtered Contact Tag trigger in `2.4`; disable re-entry; verify the contact is active in `2.4`, the trigger reads `Tag added includes "strength assessment showed"` and the workflow remains Published.
- **Verification or review date:** Live read-back passed on 4 August 2026. Review after the next delivered rescheduled assessment. Returning-member reassessments remain a separately scoped process.
- **Detailed evidence:** `outputs/systems/strength-assessment-attendance-control.md`; `outputs/systems/sales-conversion.md`.
## 2026-08-04: Restrict first-week member-reply training to the Retention Manager

- **Decision:** Create a standalone Retention Manager course for the Day 7–9 member-reply follow-up. Do not add this operational process to the numbered general trainer onboarding course.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The existing Course 11 teaches general monthly member care and is granted through the standard trainer sequence. Adding the first-week workflow there would expose a role-specific Admin Eve and Retention Manager handoff to every trainer and add unnecessary operational detail.
- **Canonical sources affected:** `reference/evolved-manual/07-member-journey.md`; `reference/evolved-manual/08-retention-system.md`; `reference/sops/first-week-member-reply-follow-up.md`.
- **Required cascade:** File the SOP in Drive under the Team Admin Onboarding folder; build the standalone GHL course and restricted access path; simplify the positive Day 7–9 Retention Manager tasks; leave the general trainer course unchanged.
- **Implementation evidence:** The native Google Doc was filed in `2. The Evolved > 7. Team > S.O.Ps > 1. Admin > Onboarding`. Standalone GHL product `8b37345d-fca8-4549-b979-3a47cdc5785e` now contains five published lessons and an eight-question, 80%-pass quiz. Its only offer remains Draft, and the numbered trainer pathway was not changed. The Piper Mae positive follow-up descriptions for Days 7, 8 and 9 were rewritten in plain English in published workflow `10f3c717-1443-427c-8264-b2348a32a448`.
- **Verification or review date:** Drive location, course structure, Draft access offer, all three positive task descriptions and the published workflow state were read back on 4 August 2026. Negative, unclear and timing/test changes remain separate decisions.
- **Detailed evidence:** `outputs/systems/membership-lifecycle.md`; `outputs/trainer-portal/retention-manager-first-week-follow-up/`.

## 2026-08-04: Standardise first-week reply-task completion times

- **Decision:** Keep each Day 7–9 reply task's existing number of due days, keep `Skip weekends` enabled and standardise every reply-task due time to 5:00 pm.
- **Owner:** Peter Brown
- **Operating interpretation:** A weekend rollover may place a task more than seven calendar days after creation. This is accepted and does not require disabling the weekend safeguard.
- **Canonical sources affected:** `reference/sops/first-week-member-reply-follow-up.md`.
- **Required cascade:** Apply 5:00 pm to every Admin Eve and Piper Mae positive, negative and unclear reply task on Days 7, 8 and 9; preserve due-day values and weekend skipping; save and read back the published workflow.
- **Verification or review date:** Completed 4 August 2026. All 15 task panels were reopened and verified at 5:00 pm with their original one-day or seven-day values and `Skip weekends` enabled. The saved workflow remained Published. The canonical SOP and its native Google Drive copy were updated to Version 1.1.
- **Detailed evidence:** `outputs/systems/membership-lifecycle.md`; `outputs/systems/ghl-team-task-trigger-register.md`.

## 2026-08-05: Require prompt negative-reply calls and explicit GHL notes

- **Decision:** Keep positive Retention Manager follow-up due in seven days, but require negative first-week responders to receive a prompt phone call through a one-day Piper task. Admin Eve owns the written response, review-pathway check and plain-English handoff. Piper records the result as an internal note under `Notes`, continues contact attempts when the member is not reached and escalates issues that cannot be remedied without owner intervention.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** Piper's clarification showed that the earlier wording asked the Retention Manager to interpret a corrected review-workflow status and allowed a concerning reply to wait until the next visit or seven days. Keeping that wording was rejected. Adding the process to the general trainer course was also rejected because it is restricted operational training for the main trainer/Retention Manager.
- **Canonical sources affected:** `reference/evolved-manual/07-member-journey.md`; `reference/evolved-manual/08-retention-system.md`; `reference/sops/first-week-member-reply-follow-up.md`.
- **Required cascade:** Update the native Drive SOP to Version 1.2; update and republish restricted lessons 3–5 and quiz questions 5 and 7; rewrite all Day 7–9 negative and unclear GHL tasks; change the three negative Piper task offsets from seven days to one day; retain 5:00 pm and `Skip weekends`; prepare a simple reply draft to Piper.
- **Verification or review date:** Completed 5 August 2026. The Drive document retains its native structure and a verified Aug 5, 2026 date chip. The restricted course content remains published. All nine changed task panels were reopened and verified with the expected wording, assignee timing, 5:00 pm and weekend skipping, and the workflow remained Published. GHL's test panel cannot start at Day 7, inject an inbound reply or force a sentiment branch, so no real-workflow test was submitted. Runtime acceptance remains pending a safe staging path or the next genuine Positive, Negative and None cases.
- **Detailed evidence:** `outputs/systems/membership-lifecycle.md`; `outputs/systems/ghl-team-task-trigger-register.md`; `outputs/trainer-portal/retention-manager-first-week-follow-up/`; Drive SOP `16j5ez3IzPjWMKFuMr3spBvF2hXd0aXYLOmPlRJeYTfo`; workflow `10f3c717-1443-427c-8264-b2348a32a448`.

## 2026-08-05: Use positive first-week replies for rapport, reviews and consent-based referrals

- **Decision:** Positive first-week responders receive a prompt Retention Manager call. The call thanks the member, builds rapport, checks whether she has left a Google review and, when natural, mentions that a new-member spot is available for a friend or woman in her life who would benefit from getting stronger.
- **Owner:** Peter Brown
- **Consent boundary:** Ask for a warm introduction or confirm that the referred woman has agreed to be contacted before recording or using her contact details. Record the consent source in GHL and get in touch promptly once that boundary is satisfied.
- **Timing interpretation:** Change the three positive Piper tasks from seven days to one day. All 15 Day 7–9 reply tasks are therefore due in one day at 5:00 pm with `Skip weekends` enabled.
- **Canonical sources affected:** `reference/evolved-manual/07-member-journey.md`; `reference/evolved-manual/08-retention-system.md`; `reference/sops/first-week-member-reply-follow-up.md`.
- **Required cascade:** Update the native Drive SOP to Version 1.3; update and republish the positive-reply restricted lesson and affected quiz questions; rewrite all Day 7–9 positive Piper tasks; update the Piper email draft.
- **Verification or review date:** Completed 5 August 2026. The Version 1.3 native Drive SOP and saved Gmail draft were read back. Restricted lessons 2 and 5 and quiz questions 3, 4 and 7 were republished and verified; the course retains five published lessons, eight questions, an 80% pass mark and one Draft offer. The three positive Piper task descriptions and one-day timing controls were saved and read back, leaving all 15 Day 7–9 reply tasks due in one day at 5:00 pm with `Skip weekends` in the published workflow. Runtime branch acceptance remains pending because the built-in test cannot start at Day 7, inject a reply or force a sentiment branch.
- **Detailed evidence:** `outputs/systems/membership-lifecycle.md`; `outputs/systems/ghl-team-task-trigger-register.md`; `outputs/trainer-portal/retention-manager-first-week-follow-up/`; Drive SOP `16j5ez3IzPjWMKFuMr3spBvF2hXd0aXYLOmPlRJeYTfo`; workflow `10f3c717-1443-427c-8264-b2348a32a448`.

## 2026-08-05: Restore event-based Strength Assessment booking entry

- **Decision:** The published `2. Strength Assessment` workflow must enter from `Customer Booked Appointment`, contact only, filtered to the exact active Strength & Longevity Assessment calendar. Do not use `Appointment Status = new` as the booking boundary. Preserve the existing `Rescheduled` split and the COLD/30DNNC lifecycle safeguards.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The public booking widget creates appointments as `confirmed`, not `new`. Three bookings after the 31 July trigger change therefore did not enter the workflow, while earlier widget bookings entered under the historical booking event. Retaining the status trigger would continue to miss genuine bookings. Adding both triggers would create duplicate-entry risk. The exact booking event is isolated from later Showed, No show and Cancelled status corrections, and the first workflow branch already distinguishes reschedules.
- **Canonical sources affected:** `outputs/systems/sales-conversion.md`; `outputs/systems/strength-assessment-attendance-control.md`; `context/roadmap.md`; `context/control-plane-status.md`.
- **Required cascade:** Keep one exact-calendar booking trigger; retain the internal reschedule and COLD/30DNNC guards; reconcile missed bookings without replaying client messages; verify Saved and Published state after server reload.
- **Verification or review date:** Live repair, reload verification and a controlled public-widget booking acceptance passed 5 August 2026. The Confirmed booking enrolled immediately, completed the intentional one-minute wait, followed the fresh/direct branch and produced the expected single WARM opportunity, booked tag, notifications, sheet row and SA Nurture entry with no COLD opportunity. Both enrolments and all exact test records were removed and verified absent. Continue normal monitoring of genuine booking executions and historical status-correction containment.
- **Detailed evidence:** Live workflow `e4426f3c-fc5f-4e1e-9d34-9e4d77a088f2`; `outputs/systems/sales-conversion.md`; `outputs/systems/strength-assessment-attendance-control.md`.

## 2026-08-05: Close the GHL backend and Drive process audit

- **Decision:** Mark the GHL workflow-governance, backend and Drive process audit complete. Keep the curated backend, workflow-owner, team-task, custom-data and Drive registers as living operating controls. Treat the remaining inbound ownership, post-Day-7 lifecycle, membership service-change, Strength Assessment attendance and AI pre-qualification work as separate implementation scope rather than audit blockers.
- **Owner:** Peter Brown
- **Evidence and alternatives considered:** The audit covered the material workflow library, forms, surveys, custom fields and values, tags, calendars, funnels, email assets, products, users, task ownership, all seven remaining pipelines and current Admin, Sales and Delivery Drive folders. Supported cleanup and record reconciliations were applied with preconditions and live read-back. After the initial workflow-inspection limitation was identified, material workflows were revalidated across their complete canvases. Keeping the audit open for unrelated builds would blur discovery, remediation and product development and make roadmap status less reliable.
- **Canonical sources affected:** `plans/2026-07-17-ghl-workflow-governance-audit.md`; `context/roadmap.md`; `context/control-plane-status.md`; `outputs/systems/ghl-backend-register.md`; `outputs/systems/ghl-workflow-owner-review-register.md`; `outputs/systems/ghl-team-task-trigger-register.md`; `outputs/systems/ghl-custom-data-governance-register.md`; `outputs/systems/drive-process-audit.md`.
- **Required cascade:** Mark both roadmap audit rows complete; remove stale audit-next-step wording; record the living-register maintenance boundary; preserve unresolved improvements in the governed build queue.
- **Verification or review date:** Closure documents reconciled and locally validated 5 August 2026. No live GHL mutation was required for the closure pass.
- **Detailed evidence:** `outputs/systems/ghl-backend-register.md`; `outputs/systems/drive-process-audit.md`; `plans/2026-07-17-ghl-workflow-governance-audit.md`.

## 2026-08-24: Reconcile PT holds by session entitlement and hold activation at protected live gates

- **Owner direction:** Peter approved implementation and directed the two duplicate local implementations to be reconciled into the current Evolved hold/billing architecture, with no unsupported billing or appointment change.
- **Decision:** Retain the current guarded Billing OS as canonical. Carry forward only the pure PT entitlement engine, PT branch, tests and governed documentation from the obsolete handler implementation. Membership/SGPT remains date based; enabled PT processing branches before Stripe and proposes exact one-to-one session transfers for human approval in the existing GHL Conversation.
- **Safety boundary:** The PT environment gate defaults off. The candidate creates no task/tracker, posts no Conversation note, performs no Stripe or appointment mutation, sends no member communication and fails closed on incomplete or policy-sensitive evidence. A carried session and Stripe credit cannot both be proposed for the same boundary.
- **Deployment decision:** Production remains unchanged. Live health returned HTTP 200 and the PT proposal route returned HTTP 404. Dark deployment is blocked by the missing exact Railway source/credential; activation is additionally blocked by the missing Hub evidence adapter and `promotion_authorised=false` Conversation handoff.
- **Verification:** Current Billing OS 50/50 tests; PT unit/integration 18/18 tests; compilation, instruction drift and diff checks passed.
- **Evidence:** `plans/2026-08-22-pt-hold-entitlement-reconciliation.md`; `outputs/systems/pt-hold-entitlement-reconciliation-completion-2026-08-24.md`.
