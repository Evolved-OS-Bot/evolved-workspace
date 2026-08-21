# Member Growth Intelligence Engine

**Status:** Canonical handoff
**Created:** 30 July 2026
**Owner:** Peter Brown for commercial policy; operating-data hub for governed intelligence; Admin Eve and coaches for approved execution

## Executive Decision

Build the member growth system as infrastructure for a $10 million company.

Do not use GHL opportunities as the active-client database or as the source of upsell and cross-sell candidates. Stripe, GHL, Trainerize and calendars remain authoritative for their own facts. The Evolved Operating Data Hub reconciles those facts into one governed client and service view, then produces explainable commercial recommendations.

An opportunity begins only when a genuine commercial conversation begins. Candidate discovery, eligibility, suppression, personalisation and measurement belong in the hub.

## Why This Replaces the Membership Pipeline Model

The Membership Pipeline cannot reliably represent simultaneous services. A client may have SGPT, PT, a prepaid term, an approved hold, a notice period and a future service change at the same time, while one opportunity can occupy only one stage.

The 30 July audit confirmed 135 Membership Pipeline opportunities, with 43 not attached to any visible stage. The published `3.1. New Personal Training Client` workflow still writes through a deprecated `PT Only / Won` action, and a successful 28 July execution produced a searchable but stage-invisible record.

Cleaning those records would recreate the wrong operating model. Preserve them as history, stop using the pipeline as operational truth and replace its live dependencies only after equivalent governed service-state capture is verified.

## Authority Boundaries

| Domain | Authoritative source | Hub responsibility |
|---|---|---|
| Identity and communication | GHL | Resolve canonical person identity and communication eligibility |
| Lifecycle and signed service decisions | GHL agreements, variations and approved lifecycle fields | Project effective current and future service state |
| Recurring and one-time payment | Stripe and governed PT Minder evidence | Reconcile commercial coverage without inferring service from amount alone |
| Training activity, progress and results | Trainerize | Produce quality-gated engagement and outcome evidence |
| Booked and delivered service | GHL calendars and governed appointment evidence | Reconcile entitlement, frequency, continuity and capacity |
| Current service relationship | Accepted cross-source service contract | Publish the governed multi-service view |
| Growth recommendation | Operating-data hub | Apply deterministic eligibility, exclusions and scoring |
| Outreach and response | GHL | Record human-approved execution and member response |
| Commercial opportunity | GHL opportunity pipeline | Begin only after a genuine growth conversation starts |

## Canonical Data Model

The engine should extend the existing reporting-control-plane entities with:

### Growth recommendation

- recommendation ID;
- person ID;
- current governed service relationships;
- recommended service or service change;
- recommendation type;
- deterministic eligibility result;
- supporting evidence references;
- exclusion and suppression reasons;
- confidence band;
- projected weekly and annualised recurring-revenue change;
- delivery-capacity requirement;
- margin or pricing precondition;
- generated timestamp;
- expiry timestamp;
- rule version.

### Human decision

- recommendation ID;
- reviewing coach;
- approved, rejected, deferred or adjusted outcome;
- decision reason;
- approved service;
- approved outreach owner;
- decision timestamp;
- cooldown end;
- absence-cover owner.

### Outreach event

- recommendation ID;
- GHL contact ID;
- outreach channel;
- approved message version;
- sent timestamp;
- response classification;
- human-confirmed response;
- next action;
- completed timestamp.

### Commercial outcome

- recommendation ID;
- opportunity ID, only when created;
- consultation or conversation start;
- offer made;
- won, declined, deferred or no-response outcome;
- service effective date;
- verified recurring-revenue change;
- retention status after 30, 90 and 180 days.

## Initial Recommendation Families

1. PT once weekly to PT twice weekly.
2. PT Only to Strong, Fit & Flexible.
3. Strong plus separate PT to Fast Track.
4. PT twice weekly to a governed Fast Track or Strong consolidation.
5. Fit & Flexible to Strong, Fit & Flexible.
6. Legacy or fragmented commercial arrangement to a canonical current offer.

Recommendations must not be based on revenue alone. The engine should consider goals, service use, progress, stated preferences, coach evidence, capacity and whether the proposed service is likely to improve the member's experience.

## Deterministic Guardrails

Suppress or route to review when any of the following applies:

- active cancellation notice;
- active or pending hold;
- failed or unresolved billing;
- unresolved service identity or entitlement;
- pending membership service change;
- recent onboarding or insufficient tenure;
- recent growth outreach or active cooldown;
- unresolved complaint or negative member-experience signal;
- no verified delivery capacity;
- non-canonical or unapproved pricing;
- recommendation conflicts with current goals, injury handling or coach evidence;
- missing communication consent or contactability;
- another recommendation is already active.

The rule engine decides eligibility. AI may summarise evidence and draft personalised outreach, but it must not silently override deterministic exclusions or create an opportunity.

## GHL Operating Surface

Write only approved, operationally useful projections back to GHL:

- Growth: Recommended Service;
- Growth: Recommendation Reason;
- Growth: Confidence;
- Growth: Coach Decision;
- Growth: Outreach Owner;
- Growth: Outreach Status;
- Growth: Last Outreach Date;
- Growth: Cooldown Until;
- Growth: Recommendation ID;
- Growth: Last Verified.

Create saved views for:

- PT once-weekly upgrade candidates;
- PT twice-weekly consolidation candidates;
- Strong plus PT not on a canonical Fast Track arrangement;
- PT Only candidates for Strong, Fit & Flexible;
- legacy pricing or service arrangements;
- recommendations awaiting coach review;
- approved outreach awaiting Admin Eve;
- exceptions requiring owner decision.

## Human Workflow

1. The hub publishes a weekly recommendation cohort.
2. The relevant coach reviews personal suitability.
3. Rejected and deferred recommendations record a reason and cooldown.
4. Approved recommendations receive a personalised draft grounded in current training and results evidence.
5. Admin Eve sends or coordinates the approved outreach.
6. A GHL opportunity is created only when the member expresses interest or a specific commercial conversation begins.
7. The service-change workflow owns the accepted change and its effective-date implementation.
8. The outcome feeds back into the engine for conversion and retention measurement.

## Membership Service-Change Dependency

The Member Growth Engine recommends and measures. It does not implement a service change.

The separate Membership Service Change Control must:

- create one immutable service-change request;
- preserve prior, requested and effective service state;
- capture the signed variation and commercial terms;
- apply the change only at the governed effective boundary;
- update canonical GHL fields, billing, Trainerize, appointments, workbooks and the hub;
- publish a versioned accepted service-change event;
- fail closed and create an Admin Eve exception when any required surface disagrees.

Do not remove the legacy Membership Pipeline opportunity writer until the replacement service-change event and onboarding service-state capture have passed end-to-end acceptance. This is a dependency gate, not an endorsement of the legacy pipeline.

## Shadow-Mode Acceptance

Run the engine without member contact for at least four weekly cohorts and preferably eight.

Acceptance requires:

- every candidate has a traceable recommendation ID and rule version;
- no suppressed member appears in an outreach-ready cohort;
- coach decisions are captured and comparable with engine recommendations;
- recommendation evidence matches current accepted service and activity data;
- delivery capacity is verified before approval;
- duplicate and conflicting recommendations are zero;
- projected revenue is not counted as realised revenue;
- GHL writeback is idempotent;
- no opportunity is created before a genuine conversation;
- outcome and retention measurement reconcile to accepted service-change events.

## Measures

- candidates generated;
- suppression rate and reasons;
- coach approval, rejection and adjustment rates;
- outreach completion rate;
- positive response rate;
- commercial conversations created;
- offer and conversion rates;
- verified weekly and annualised recurring-revenue change;
- delivery-capacity consumed;
- 30, 90 and 180-day retention after change;
- complaints, reversals and inappropriate-recommendation rate.

## Delivery Sequence

1. Complete the Membership Service Change Control and accepted service-change event.
2. Confirm that onboarding, reactivation, cancellation and hold events publish compatible service-state changes.
3. Freeze and document Membership Pipeline operational use.
4. Define recommendation rules, exclusions, capacity inputs and cooldown policy.
5. Extend the hub contract and protected recommendation store.
6. Publish the weekly internal shadow report.
7. Add coach-decision and Admin Eve execution surfaces.
8. Add controlled GHL writeback and saved views.
9. Validate four to eight shadow cohorts.
10. Begin a capacity-limited outreach pilot.
11. Create opportunities only for genuine conversations.
12. Remove the legacy Membership Pipeline writers after replacement parity is proven.

## Canonical References

- `outputs/systems/reporting-control-plane.md`
- `outputs/systems/ghl-backend-register.md`
- `plans/2026-07-30-membership-service-change-control.md`
- `plans/2026-07-27-member-advocacy-evidence-engine.md`
- `context/roadmap.md`
