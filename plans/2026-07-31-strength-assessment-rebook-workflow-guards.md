# Strength Assessment Rebooking Workflow Guards

Date: 2026-07-31
Owner: Peter Brown
Status: Complete

## Objective

Prevent governed historical attendance corrections from enrolling an existing member, or a person whose Strength Assessment is already known to have been completed, into the live no-show or cancellation rebooking journeys.

## Live workflows in scope

- `2.2 SA: No Show Rebook` (`c531cc51-65cf-4a75-b4bf-ada7358a515a`)
- `2.3 SA: Cancelled Rebook` (`d6259817-fa44-43d1-bcbe-5f74e78f409f`)

## Confirmed platform constraint

The GHL appointment-status trigger can filter event type, calendar, appointment status and contact fields, but it cannot compare the appointment start date with the current time or express a rolling “within the last 72 hours” rule. A false date guard will not be added.

## Controlled implementation

1. Add the same first-step If/Else guard to both workflows.
2. Route contacts carrying a governed exclusion signal away from all rebooking actions:
   - `member`
   - `strength assessment showed`
3. Keep the existing rebooking journey on the no-exclusion branch.
4. Label both branches in plain English.
5. Keep both workflows published.

Historical appointment corrections remain governed source repairs. They must be applied through the attendance-control procedure, with the resulting hub acceptance refreshed and checked. The workflow guard provides a second line of defence for members and completed assessments; it does not replace that procedure.

## Completion record

Both published workflows were initially updated and reload-verified on 31 July 2026. Controlled testing on 1 August exposed an unreliable first branch, so both If/Else actions were deleted and rebuilt cleanly. Each now begins with `Guard: completed SA or existing customer`:

- `strength assessment showed` routes to `Assessment completed — stop`;
- GHL contact type `Customer` routes to `Existing customer/member — stop`;
- only the `Eligible for rebooking` none-of-the-above branch enters the original workflow.

The final controlled contacts show `No Action / Finished` in both workflow enrolment histories. The temporary contacts and their test-only records were deleted. Vaishnavi Vakacharla retained `member`, `strength assessment showed` and `personal training`; the incident-created cancellation opportunity remained deleted.

## Acceptance checks

- Both workflows remain published after saving.
- The exclusion branch contains no opportunity, tag, message, task or spreadsheet action.
- The existing rebooking actions remain attached only to the eligible branch.
- No new workflow enrolment is created by editing or publishing the guards.
- Vaishnavi retains her repaired appointment statuses, member/service tags and clean opportunity state.

## Accelerated acceptance gate

The original proposal to observe the first 20 genuine cancellations or no-shows would take approximately three to four months and would unnecessarily delay Reporting V2.

The approved replacement gate is:

1. evaluate the latest 20 historical No show and Cancelled Strength Assessment events against the exact live tag rules;
2. use controlled temporary GHL contacts to prove the Customer and `strength assessment showed` stop conditions without messaging a real client;
3. prove the eligible route through historical cases and the saved live workflow structure, without deliberately sending the live rebooking sequence to a test contact;
4. complete two accepted 12-hour attendance refresh observations;
5. retain genuine future closures as ongoing monitoring rather than a cutover blocker.

Any temporary test contact must use a non-deliverable address, contain no real phone number, create no real-client message, and be deleted after read-back.

The first controlled test found that GHL's `Tags includes member` branch did not match a temporary contact whose `member` tag was confirmed by API read-back. Both temporary enrolments were removed during their wait step before a client message could be delivered. The `strength assessment showed` branch passed in both workflows.

The historical replay established a deterministic replacement: all three current-member cases are GHL contact type `customer`, while all 17 eligible rebooking cases are contact type `lead`. The first controlled edit still failed because the original first branch object was corrupt. Both guards were therefore deleted and rebuilt with `strength assessment showed` first and `Contact type is Customer` second.

Final acceptance on 1 August 2026:

- 20 of 20 historical cases classified under `sa-rebook-guard-v1`;
- 19 Cancelled and one No show replayed;
- three existing Customers stopped and 17 Leads remained eligible;
- the completed-assessment contact stopped in both workflows;
- the Customer/member contact stopped in both workflows;
- all four final live runs show `No Action / Finished`;
- the two temporary contacts were deleted;
- the normal Railway attendance refreshes at 08:10 and 20:10 UTC both completed, with current run `20260731T201000Z-8ee01dc7`.

Future genuine closures remain ongoing monitoring and are not a Reporting V2 cutover blocker.

## Rollback

If branch routing is incorrect, unpublish the affected workflow, remove only the new first-step If/Else action, confirm the original first action is restored, then republish. Do not alter the appointment-status trigger or any pre-existing action.
