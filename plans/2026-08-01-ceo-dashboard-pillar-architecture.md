# CEO Dashboard Pillar Architecture

**Status:** Phase 1 shadow dashboard live; metric connections in progress  
**Date:** 1 August 2026  
**Owner:** Peter Brown  
**Primary surface:** Reporting V2 CEO dashboard  
**System of record:** Railway Operating Data Hub

## Objective

Reorganise the CEO dashboard around the five operating pillars Peter uses to
judge the health of the business:

1. Marketing
2. Sales
3. Onboarding
4. Delivery
5. Attrition

Cash collected and progress toward the rolling $1 million goal remain above
the five pillars. Each pillar shows one primary health measure on the first
fold and opens into a more detailed diagnostic widget.

This architecture replaces a long undifferentiated scorecard with a decision
hierarchy:

1. How much cash did we collect, and how close are we to the rolling goal?
2. Which business pillar is unhealthy?
3. Which underlying system or cohort explains the result?

## First fold

### Cash and goal

Show first:

- cash collected in the selected completed period;
- recurring cash;
- new-sale cash;
- rolling 365-day cash excluding GST;
- progress toward $1 million;
- annualised pace based on the accepted rolling period;
- freshness and coverage warning when a processor feed is incomplete.

Cash is a separate executive measure and is not duplicated as one of the five
pillar health measures.

## Naming convention

Dashboard names must describe what happened in the business, not the name of a
worksheet row, database object or calculation.

Use:

- a clear business noun;
- an observable outcome or state;
- the reporting period only when it is not already controlled by the page;
- a short explanation beneath the number where the business meaning could
  still be misunderstood.

Do not use:

- `signal`, `canonical`, `accepted`, `governed`, `provisioning` or other
  architecture language on the CEO surface;
- `lead` for both a subscribed contact and a booked appointment;
- `sales` for both one unique new client and multiple services inside the same
  sale;
- `show` without saying which appointment;
- `conversion` without naming its start and end stages;
- source-system names in the metric title unless the source itself is the
  decision question.

### Approved dashboard terms

| Dashboard term | Exact business meaning | Legacy KPI reference |
|---|---|---|
| Website visits | Website sessions in the selected period | New governed source; not currently in the KPI tab |
| New subscribers | Unique people who completed the subscription or lead-capture form | Total Subscribes |
| Strength Assessments booked | Unique governed assessment booking lineages; this is the lead-generation result | Total Studio Bookings Made |
| Prequalified assessments | Booked assessments with prequalification completed before the appointment | New V2 measure |
| Assessment attendance rate | Attended assessments divided by attended plus no-show assessments; cancellations stay separate | Studio Booking Show Rate |
| New members | Unique people converted from an attended assessment | Sales Total, deduplicated across SGPT/PT |
| Assessment-to-member conversion | Unique new members divided by attended assessments | Sales Conversion Rate Total |
| Memberships sold | Service mix within new-member sales | SGPT Sales Total and PT Sales Total |
| New sale cash | Cash collected at the point of new sale | Total New Cash Collected |
| Member cash collected | Cleared recurring member cash in the period | Recurring portion of Cash Collected |
| Total cash collected | All accepted cleared cash in the period | Cash Collected |
| Member value per week | Accepted recurring weekly value divided by active paying members | Member value |
| Members joined | Unique clients whose service began | SGPT/PT sales adjusted to unique clients |
| Members lost | Unique clients whose final active service ended | SGPT/PT cancels adjusted to unique clients |
| Net member growth | Members joined minus members lost | SGPT/PT Members Gained/Lost |
| Members in notice | Current clients with an accepted future service-end or downgrade date | New governed lifecycle measure |
| PT sessions booked | Governed 1:1 appointments booked | PT Bookings Total |
| PT hours booked | Governed 1:1 booked hours | PT Booked Hours Total |
| SGPT sessions booked | Member class bookings in Trainerize | Class Bookings, rebuilt event-level |
| First onboarding session attended | Attended 1:1 onboarding appointment | New governed V2 measure |
| Successful first week | Onboarding attended, three completed training records and positive check-in confirmation | New governed V2 measure |
| Time to Live / Long / Perform | Time from effective membership start to first accepted achievement of each level | New governed V2 measure |

The phrase `Leads Generated` can remain as a section explanation, but the
metric itself should be titled `Strength Assessments booked`. This removes the
current ambiguity between a new subscriber, a CRM lead and a genuine booked
sales opportunity.

### Pillar health measures

| Pillar | Recommended first-fold measure | Why it is the best headline |
|---|---|---|
| Marketing | Subscribers booking a Strength Assessment | Measures whether captured interest becomes a genuine sales opportunity |
| Sales | Assessments becoming new members | Measures how effectively attended assessments become clients without SGPT/PT double-counting |
| Onboarding | New members having a successful first week | Measures whether sold clients actually began using the service successfully |
| Delivery | Time for a member to reach Live Level | Measures how quickly the delivery system produces the first meaningful client outcome |
| Attrition | Active members lost | Measures genuine client loss against the opening active-client base |

Each measure must show its numerator, denominator, target, trend and data
confidence. If the sample is too small, the card remains visible but says so.

## Pillar widgets

## Week-ahead operating view

The CEO first fold also needs a forward-looking strip that is explicitly
separate from completed-period performance.

### Assessments booked in the next seven days

- Source authority: the existing GHL Strength Assessment calendar feed;
- Window: from the current Brisbane time to the same time seven days later;
- Include: unique future confirmed assessment appointments;
- Exclude: cancelled, invalid, no-show, deleted and elapsed appointments;
- Show: total appointments, pre-qualified appointments, completion rate and
  the named appointments still awaiting pre-qualification;
- Freshness: use the existing 14-hour Strength Assessment feed gate;
- Owner: Sales;
- Consumer: protected CEO dashboard only.

Pre-qualification uses the existing governed GHL rule: the contact is in the
pre-qualified-or-later WARM stage or has the accepted pre-qualification
summary. A reschedule does not create a completed-period lead or conversion,
but every genuinely occupied future calendar slot remains visible for
week-ahead operations.

### Projected income

Reuse Revenue Control's governed `scheduled_run_rate`. Present it as
`Projected recurring income` so it cannot be mistaken for guaranteed cash:

- it is the normalised weekly value of evidenced recurring schedules;
- it excludes paid-in-advance revenue, one-off PT packs, unapproved arrears
  and speculative new sales;
- it remains separate from completed cash collected;
- stale or missing Revenue Control evidence makes the card unavailable.

### Expenses

Expenses require an accounting source, not a payment-processor inference.
Until an accounting feed or owner-approved controlled board-pack input is
connected, the dashboard must display `Accounting connection needed` and no
amount. Google Sheets may temporarily collect a controlled weekly expense
total, but it cannot become the expense database or calculation engine.

**Implemented in shadow on 1 August 2026.** Railway deployment
`203e0664-df2c-4b33-9c2b-3fdce486d733` adds the protected week-ahead strip.
The accepted GHL refresh found two Strength Assessments in the next seven days:
Heena Samreen is pre-qualified and Jody Austin still requires
pre-qualification. The governed Revenue Control bridge supplies `$9,769` of
projected weekly recurring income and `$9,203` currently confirmed. Expenses
remain unavailable with an explicit accounting-connection requirement. The
dashboard has no browser errors or horizontal overflow, and 169 relevant tests
pass.

### 1. Marketing

- Website visits;
- New subscribers;
- Strength Assessments booked;
- Visitors becoming subscribers;
- Subscribers booking a Strength Assessment;
- lead source;
- cost per subscription and cost per booked assessment when ad-spend events
  are accepted;
- trends by completed week, 28 days and 90 days.

Website sessions and identified contacts have different grains. The dashboard
must show the numerator and denominator for both conversion steps and must not
pretend an anonymous website session is a known person.

For the subscription-to-lead rate, count the unique subscribed contacts who
subsequently created a governed Strength Assessment booking. Repeated form
submissions and appointment reschedules do not create extra subscriptions or
leads.

### 2. Sales

- Strength Assessments booked;
- Prequalified assessments;
- Assessments prequalified;
- Assessments attended;
- Assessments cancelled;
- Assessment no-shows;
- unresolved elapsed assessments;
- Assessment attendance rate, calculated from attended assessments and
  no-shows while cancellations remain a separate outcome;
- New members;
- Assessments becoming new members;
- program and package breakdown across Strength & Sculpt, Fast Track and 1:1
  PT only;
- New sale cash;
- consultant conversion, with minimum sample sizes;
- lost-sale reasons.

One assessment can sell multiple service components but counts as one
conversion.

The supporting explanation may say `conversion rate`, but the visible title
should say `Assessments becoming new members`. Conversation activity and reply
handling remain a separate customer-support system.

### 3. Onboarding

Keep two separate stages and two separate clocks.

#### Onboarding session attended

Requirements:

- an exact sold client;
- an attended 1:1 onboarding appointment;
- matched appointment and Trainerize identity.

Measure:

- time from sale to attended onboarding session.

#### First-week onboarding completed

Requirements:

1. the 1:1 onboarding appointment was attended;
2. the member has at least three booked and completed training records in
   Trainerize after the sale;
3. the first-week check-in received a positive reply, or a staff call recorded
   that the member was having a good first week.

Measure:

- time from sale to the final qualifying activation event.

Do not mark onboarding complete from a calendar status alone. The three
requirements remain separately visible so the widget can explain which step is
missing.

Diagnostic markers:

- sold clients awaiting onboarding booking;
- booked but not attended;
- onboarding attended but fewer than three completed training records;
- training completed but first-week confirmation missing;
- fully activated;
- average and median time to each stage;
- trainer and service breakdown.

### 4. Delivery

Retain:

- agreed active clients;
- Strength & Sculpt only;
- Fast Track;
- 1:1 PT only;
- active PT roster;
- active notice and downgrade periods.

#### PT delivery

- total PT sessions booked for the current week;
- total PT hours booked;
- completed, cancelled and missed PT sessions;
- trainer sessions and hours;
- available trainer hours;
- booked utilisation and completed utilisation;
- entitlement or booking continuity exceptions.

#### SGPT delivery

Use Trainerize class schedule and attendance events:

- SGPT bookings;
- SGPT attendances;
- cancellations and no-shows;
- unique members served;
- class capacity and fill rate;
- booked and attended delivery by class type, timetable slot and assigned
  trainer;
- active members with no booked or attended SGPT delivery.

The timetable owns planned trainer assignment. Trainerize owns member booking
and attendance evidence. The hub reconciles both and calculates the widget.

#### Progression through Evolved Standards

- average and median time from the effective membership start to first
  achieving Live Level;
- average and median time to Long Level;
- average and median time to Perform Level;
- current number and percentage of active members at each level;
- members approaching each level;
- progression by service, tenure and trainer;
- members with insufficient assessment evidence shown separately.

The first-fold Delivery card uses median time to Live because a small number of
very old or incomplete records can distort an average. The detailed widget
shows both median and average.

### 5. Attrition

- cancellations requested;
- clients currently in notice;
- completed cancellations;
- downgrade-only transitions;
- approved holds shown separately from attrition;
- opening active clients;
- client losses and attrition rate;
- net client growth;
- reason, service, tenure and trainer segments;
- preventable-risk cases before final cancellation.

Downgrades and holds must not be counted as full client loss.

## Member outcomes

Member outcomes remain a major delivery section, divided into distinct widgets.

### Strength performance

- four-week, 12-week, six-month and overall strength improvement;
- median change;
- sample size;
- movement-family view;
- outlier and confidence rules;
- performance-standard results;
- separate top-performer ranking.

### Workout milestones

- 50, 100, 150, 200 and later workout milestones;
- milestones reached in the selected period;
- upcoming milestones;
- fulfilment state where recognition or a reward is due.

Do not combine workout count milestones with strength performance rankings.

### Evolved Standards

Show two views:

1. **Overall standard:** the agreed business-level classification of each
   member as Live, Long or Perform.
2. **Standard components:** each agreed exercise or capability, with the
   member's Live, Long or Perform result for that individual component.

The first implementation must define:

- the canonical exercise list;
- normalised exercise aliases;
- whether the overall result uses a single agreed exercise, an all-components
  rule, or a minimum component threshold;
- bodyweight-relative or absolute scoring for each standard;
- valid assessment window;
- missing-data behaviour;
- members approaching a standard;
- members newly achieving a standard;
- the effective membership start used to calculate time-to-standard.

No person is classified from a partial or ambiguous exercise match.

## Automatic cash architecture

Manual bank statement entries should be an exception, not the main feed.

### Stripe

Build a governed cash adapter that:

- backfills at least 400 days of settled invoice and charge events;
- captures refunds and reversals;
- runs incrementally from processor event IDs;
- uses webhooks for prompt updates and a Railway reconciliation run to catch
  missed webhooks;
- maps GST explicitly;
- deduplicates invoices, charges and retries;
- distinguishes recurring member cash, new-sale cash and one-off PT cash;
- records a complete source run before the rolling goal is available.

The hub already has the immutable cash-event contract. The missing work is the
production Stripe event adapter and historical feed into that contract.

### PT Minder

The accepted PT Minder capture already contains actual completed debit events.
Project those completed payments into the same cash-event contract:

- completed debits count;
- pending and failed debits do not;
- internal Charge entries and displayed balances never count;
- corrections create a new event version;
- processor identity and payment-purpose rules prevent Stripe double-counting.

PT Minder currently requires Peter's authenticated browser capture. This can
support a reliable weekly rolling goal if its eight-day freshness gate is
visible, but it cannot support truly real-time cash until PT Minder or its debit
provider exposes an approved automated feed.

### Non-processor cash

Use one of:

1. an accounting or bank-feed adapter as validation and exception evidence; or
2. a controlled approved manual cash event for genuinely exceptional receipts.

Do not make bank statements the primary calculation source. The processor
event remains the cash authority for normal card and debit collections. An
accounting feed validates settlement and catches off-platform receipts without
silently replacing processor detail.

### Reliability controls

- Stripe freshness: within 14 hours;
- PT Minder freshness: within eight days until automated;
- complete-run watermark for every required source;
- negative refunds on the refund date;
- GST excluded;
- no pending or failed receipts;
- no duplicate invoice, charge, retry or transfer;
- source coverage and event count shown beside the rolling goal;
- unavailable rather than estimated when a required feed is stale or
  incomplete.

## Source and entity map

| Data | Authority | Hub entity |
|---|---|---|
| Lead, contact, lifecycle and first-week reply | GHL | person, lifecycle event, conversation outcome |
| Assessment and onboarding appointment | GHL appointment | appointment event |
| Trainer assigned to assessment or PT | GHL calendar | delivery assignment |
| Trainer assigned to SGPT class | governed timetable | class assignment |
| Training record and class booking/attendance | Trainerize | training delivery event |
| Stripe cash and refunds | Stripe | cash event |
| Legacy debit cash | PT Minder completed payment event | cash event |
| Current service and entitlement | governed hub reconciliation | service relationship |
| Notice, cancellation and downgrade | GHL plus accepted effective date | lifecycle transition |
| Targets and limited exceptions | controlled input | governed manual input |

## Implementation phases

### Phase 1: Dashboard information architecture

- Add cash and rolling goal above the five pillars.
- Add one first-fold health card per pillar.
- Move current V1 delivery markers into the correct pillar widget.
- Keep unavailable measures visible with their missing-source explanation.
- Add period, confidence and source freshness labels.

**Implemented 1 August 2026.** Railway deployment
`5a115cef-d4c9-4dcb-b0b4-e2bf9bbddeb6` reorganises the Reporting V2 preview
as one coherent CEO surface:

- cash, recurring member cash and new-sale cash appear first;
- Marketing, Sales, Onboarding, Delivery and Attrition each have one
  plain-English health card and an anchored detail section;
- current delivery markers are grouped under the correct pillar;
- strength performance and workout milestones are separate;
- unavailable measures say which evidence is missing instead of displaying a
  substitute calculation;
- the accepted dashboard and KPI workbook remain unchanged.

All 142 Operating Data Hub tests pass. The live preview was verified at
desktop and 390-pixel mobile width with five pillar links, no horizontal
overflow and no browser errors.

**First-fold readability refinement, 1 August 2026.** The cash-goal progress
bar remains the primary target visual. Sales and Onboarding now use the same
compact visual language to show the actual observed rate from zero to 100%,
with the exact numerator and denominator written underneath. These are result
tracks, not invented targets. Marketing, Delivery and Attrition instead show
the specific missing connection or governance decision, so an unavailable or
provisional measure cannot look complete. Railway deployment
`faab3397-ed07-4703-93b2-a74ffdfd90e7` passed its health check; the week,
28-day and 90-day views have no browser errors or horizontal overflow.

### Phase 2: Automatic cash

- Build the Stripe 400-day backfill and incremental adapter.
- Project accepted PT Minder completed debits into the cash contract.
- Run duplicate, GST, refund and source-completeness tests.
- Compare to the KPI workbook and available accounting close.

**Implemented 1 August 2026.** Railway deployment
`5378f639-fdc2-40b6-9577-065bda458e8a` completes the shadow automatic-cash
layer:

- the initial Stripe run reads 400 days of successful AUD PaymentIntents,
  their invoices, settled charges and dated refunds;
- normal Stripe refreshes use a three-day overlap after the accepted backfill;
- accepted PT Minder completed and refunded debits are projected from the
  existing governed snapshot; pending, failed, Charge and balance entries are
  excluded;
- explicit Stripe invoice tax is used where available; direct fully taxable
  Evolved payments use the approved GST-inclusive divisor and partial
  settlements inherit tax proportionally from their invoice;
- immutable processor IDs deduplicate replays and preserve corrections;
- incomplete, stale, non-AUD or tax-unresolved source runs keep the rolling
  goal unavailable;
- the Railway-only job runs at 06:20 and 18:20 Brisbane time.

The accepted 400-day source run processed 4,105 Stripe records into 3,805
settled or refund events and projected 511 PT Minder events with zero source
errors. The rolling 365-day window contains 4,169 accepted events and totals
`$468,729.75` excluding GST, or `46.9%` of the rolling `$1,000,000` goal. A
subsequent three-day incremental run completed in 5.5 seconds without changing
the result. The figure remains shadow-only pending accounting-close comparison
and owner cutover acceptance. All 152 hub tests pass.

### Phase 3: Onboarding activation

- Reconcile sale, 1:1 onboarding attendance, Trainerize identity, three
  completed training records and GHL first-week confirmation.
- Produce both sale-to-onboarding-session and sale-to-full-activation clocks.
- Keep each missing component explainable.

**Implemented in shadow on 1 August 2026.** Hub deployment
`e9954fd0-59cc-40f1-ae13-0d4744327541` reconciles each qualifying sale with
GHL Showed onboarding or an exact-date tracked Trainerize onboarding session,
three distinct tracked Trainerize training records and a completed verified
positive-reply or controlled staff-call task. Sales fewer than nine days old
remain pending rather than depressing the rate. The first accepted 120-day
evidence window contains 44 eligible sales: 33 with onboarding attendance, 36
with three training records, three with verified first-week confirmation and
three satisfying all requirements. The previous completed week contains two
mature sales, one fully activated, producing a 50.0% shadow rate and an
eight-day average sale-to-full-activation clock. Two Trainerize identities
remain unresolved. The sale-to-first-onboarding clock remains separate.

### Phase 4: PT and SGPT delivery

- Convert GHL PT appointments and Trainerize SGPT bookings/attendance into one
  delivery-event contract.
- Add current-week totals, trainer deployment, completion and utilisation.
- Capture approved trainer capacity for the same reporting period.

**Partially implemented in shadow on 1 August 2026.** Trainerize deployment
`a15c62fa-c4f4-4641-bb89-ec292c035ee1` adds a self-mending calendar-event
table to the existing performance volume and publishes de-identified SGPT
booking events to the hub. The controlled refresh updated 5,393 calendar
records and supplied 495 class-booking events. The previous completed week now
shows 160 member bookings, 70 unique members, 26 scheduled class sessions and
26.0 scheduled coaching hours, with the trainer breakdown calculated from the
same events. PT sessions and hours retain their existing governed source.
Trainerize does not yet expose reliable attended, cancelled or no-show class
outcomes in this feed, and approved trainer capacity is still required before
utilisation can be published.

### Phase 5: Member outcomes and standards

- Separate top performance from workout milestones.
- Approve the canonical Evolved Standard exercise and overall-classification
  rules.
- Calculate component and overall Live, Long and Perform results.

### Phase 6: Attrition

- Build the event-level opening cohort, notice, downgrade, hold and completed
  cancellation measures.
- Publish rolling 28-day attrition and period net growth.

**Provisional diagnostic implemented on 1 August 2026.** The hub now counts
unique final membership endings still represented in the latest lifecycle
state and keeps PT-only downgrades out of member loss. The previous completed
week shows zero recorded final membership endings and two PT-only downgrades.
The card is explicitly provisional: immutable lifecycle events and the
historical opening active cohort are still required before attrition rate or
net member growth can be accepted.

## Acceptance gates

- No KPI workbook or accepted dashboard change until metric-level parity
  passes.
- Every first-fold card has one versioned definition.
- Every rate exposes its numerator and denominator.
- Every period toggle recalculates from event-level data; current-state measures
  remain explicitly labelled.
- Cash is unavailable when required source coverage is incomplete.
- Onboarding completion cannot be satisfied by appointment status alone.
- SGPT and PT delivery remain separate but share one person and trainer model.
- Fast Track service components never create duplicate clients or conversions.
- Standards do not publish until exercise aliases and overall-classification
  rules are owner approved.
- Google Sheets remains a compact board pack and controlled input surface only.

The implementation now passes 167 relevant automated tests. The accepted CEO
dashboard and KPI workbook remain unchanged.
