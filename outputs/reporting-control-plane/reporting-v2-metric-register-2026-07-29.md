# Reporting V2 Metric Register

**Date:** 2026-07-29  
**Status:** Shadow implementation register  
**Reporting timezone:** Australia/Brisbane  
**Currency:** AUD, stored as integer cents  
**Current workbook authority:** Unchanged until each metric passes its cutover gate

## Register Rules

- A stock metric reports the accepted state at an exact time.
- A flow metric reports accepted events inside an exact Brisbane-local period.
- Every ratio publishes its numerator and denominator.
- Missing or stale evidence publishes `Unavailable`.
- Service components do not create additional people, sales or assessment conversions.
- Google Sheets can display accepted results but cannot calculate a governed V2 metric.

## Executive Metrics

| Metric ID | CEO label | Current dependency | V2 event grain and authority | V2 definition | Initial state |
|---|---|---|---|---|---|
| `cash_collected_total` | Cash collected | KPI row 106; manual weekly components | One settled Stripe or accepted PT Minder payment, refund/reversal, or approved bank cash event | Net accepted cash events inside the period | Definition pending money-date decision |
| `cash_collected_recurring` | Recurring cash | Derived from total cash less new cash | One accepted payment allocation to an existing recurring agreement | Accepted recurring allocations inside the period | Definition pending allocation rules |
| `cash_collected_new` | New cash | Sales `Cash Taken`, KPI rows 84–89 | One accepted payment allocation to a qualifying sale | Accepted new-sale cash allocations inside the period | Definition pending allocation rules |
| `accounting_turnover` | Accounting turnover | No governed accounting feed | Future accounting-system revenue event | Unavailable until a reliable accounting-system contract exists | Deferred and excluded from dashboard |
| `cash_goal_progress` | Progress to $1m | Planned dashboard calculation | Accepted cash events excluding GST | Accepted net cash from the immediately preceding 365 days divided by $1,000,000; retain the first achieved-at timestamp | Rolling measure approved |
| `active_clients_unique` | Active clients | Active SGPT/PT rosters plus governed cohort | One canonical person with an accepted active lifecycle state | Unique accepted people active at period end | Existing canonical model; V2 history pending |
| `active_service_relationships` | Active services | Active SGPT/PT roster rows | One active person-service relationship | Accepted active relationships at period end | Existing canonical model |
| `membership_mix` | Membership mix | Current roster overlap and service labels | One mutually exclusive person classification at period end | Strength & Sculpt only, Fast Track, PT only and approved other | Existing canonical model |
| `members_joined` | Members joined | Accepted GHL sale/agreement evidence | One accepted membership activation per canonical person | Unique people whose first accepted membership activation falls inside the period; Fast Track remains one person | `membership-lifecycle-v1` shadow implemented |
| `final_membership_endings` | Final membership endings | GHL cancellation and final-access fields | One exact final-access event per canonical person whose membership service ends | Unique people whose final membership access ends inside the period; PT-only endings on continuing SGPT/Fast Track are excluded | `membership-lifecycle-v1` shadow implemented |
| `straight_cancellations` | Straight cancellations | GHL cancellation type and final-access fields | One exact final-access event classified as full membership cancellation | Unique final membership endings that do not retain another membership service | `membership-lifecycle-v1` shadow implemented |
| `downgrade_only_transitions` | Downgrade-only transitions | GHL current/post-notice service and final-access fields | One exact service-component ending while another membership service remains | Unique people whose PT component ends while SGPT/Fast Track membership continues; never member loss | `membership-lifecycle-v1` shadow implemented |
| `approved_holds` | Approved holds | GHL hold status/type/start/end fields | One accepted, exact effective hold interval | Unique people on an approved active hold; missing or malformed bounds fail closed | `membership-lifecycle-v1` shadow implemented |
| `membership_attrition_rate` | Membership attrition | Final membership endings and exact opening cohort | Accepted unique final membership endings divided by the exact person-level cohort active at period start | Numerator and denominator are both published; unavailable unless the exact opening cohort exists | `membership-lifecycle-v1` shadow implemented; historical cohort coverage incomplete |
| `net_unique_member_growth` | Net unique-member growth | Membership activations and final membership endings | Unique membership activations less unique final membership endings | One person counts once per side in the period; service components never create extra people | `membership-lifecycle-v1` shadow implemented |
| `cancellation_notice_active` | Active cancellation periods | GHL cancellation fields | One effective cancellation-notice lifecycle interval | People currently inside an accepted notice period | `membership-lifecycle-v1` shadow implemented |

## Acquisition Funnel

| Metric ID | CEO label | Current dependency | V2 event grain and authority | V2 definition | Initial state |
|---|---|---|---|---|---|
| `leads_unique` | Leads produced | Appointments `Date Booked`; hidden lead tab | One GHL lead-created event per canonical contact | Unique eligible lead events inside the period | Event bridge required |
| `prequalification_completion` | Prequalification completion | Appointments manual Y/N | One GHL prequalification-required/completed/waived event | Completed divided by eligible, with waived separate | Event bridge required |
| `sa_bookings_unique` | Strength Assessments booked | Appointments rows | One logical appointment series first booked in the period | Unique eligible series, with reschedules counted once | Appointment-series layer required |
| `sa_attended` | Assessments attended | Appointments manual `Show?` | One terminal delivered appointment series | Unique series accepted as showed | V2 shadow implemented |
| `sa_no_show` | No-shows | Appointments manual `Show?` | One terminal appointment series | Unique series accepted as no-show | V2 shadow implemented |
| `sa_show_rate` | Show-up rate | KPI rows 60–63 | One terminal showed/no-show appointment series | Showed divided by showed plus no-show | `sa-attendance-v1` shadow implemented |
| `assessment_conversion_unique` | Conversion at assessment | Appointments `Convert?` and Sales rows | One attended appointment series linked to a qualifying sale | Most recent attended series within 30 days; returning former members excluded as reactivations; Fast Track remains one conversion | Rules approved and tested; GHL sale bridge required |
| `sales_unique` | New sales | Sales rows | One accepted commercial sale/agreement | Unique qualifying sale events inside the period | Sale ledger primitive implemented |
| `service_components_sold` | Services sold | SGPT and PT sales formulas | One service component inside one accepted sale | Components by type; Fast Track contributes SGPT 1 and PT 1 | Primitive implemented |

## Marketing

| Metric ID | CEO label | Current dependency | V2 event grain and authority | V2 definition | Initial state |
|---|---|---|---|---|---|
| `ad_spend` | Ad spend | Manual weekly KPI values and hidden paid-ads tab | One accepted platform spend or approved manual spend event | Accepted spend inside the period | Source decision required |
| `cost_per_lead` | Cost per lead | Workbook ratio | Accepted ad spend and unique attributed leads | Spend divided by attributed leads | Downstream |
| `cost_per_assessment` | Cost per assessment booked | Workbook ratio | Accepted ad spend and unique booked series | Spend divided by attributed booked series | Downstream |
| `acquisition_cash_roas` | Cash return on ad spend | Workbook ratio | Accepted attributed new cash and ad spend | Attributed new cash divided by spend | Downstream |

## Delivery and Retention

| Metric ID | CEO label | Current dependency | V2 event grain and authority | V2 definition | Initial state |
|---|---|---|---|---|---|
| `sale_to_onboarding_booked_days` | Days to onboarding booked | Sales checklist and GHL appointments | Sale plus first eligible onboarding booking | Median and average elapsed days | Event bridge required |
| `sale_to_onboarding_complete_days` | Days to onboarding completed | Sales checklist and GHL appointments | Sale plus first completed eligible onboarding | Median, average and within-target rate | Event bridge required |
| `pt_sessions_booked` | PT sessions booked | Weekly KPI value | One accepted GHL PT appointment | Eligible booked sessions inside the period | Event bridge required |
| `pt_hours_booked` | PT hours booked | Weekly KPI value | One accepted GHL PT appointment duration | Sum eligible booked minutes divided by 60 | Event bridge required |
| `pt_utilisation` | PT utilisation | No complete capacity ledger | Appointment minutes and effective trainer capacity windows | Booked eligible minutes divided by available minutes | Capacity input required |
| `workouts_completed` | Workouts completed | Trainerize reporting | One completed Trainerize workout | Accepted workouts inside the period | Existing source; V2 adapter required |
| `strength_change_4_week` | Strength improvement at 4 weeks | Trainerize longitudinal analysis | Baseline and comparable result observation | Governed change by approved lift/movement rules | Definition and cohort gate required |
| `strength_change_12_week` | Strength improvement at 12 weeks | Trainerize longitudinal analysis | Baseline and comparable result observation | Governed change by approved lift/movement rules | Definition and cohort gate required |
| `strength_change_6_month` | Strength improvement at 6 months | Trainerize longitudinal analysis | Baseline and comparable result observation | Governed change by approved lift/movement rules | Definition and cohort gate required |
| `standards_achieved` | Live, Long and Perform standards | Trainerize and manual coaching review | One coach-accepted standard achievement | First accepted achievements inside the period | Rule engine required |
| `members_near_milestone` | Upcoming milestones | Trainerize and lifecycle history | One canonical member-milestone state | Members within approved threshold | Rule decision required |

## Metric-Family Cutover Order

1. Strength Assessment attendance and show rate.
2. Leads and prequalification.
3. Unique assessment conversion, sales and service mix.
4. Cash, payment status and the million-dollar cash goal.
5. Lifecycle movement, active clients and membership mix history.
6. Onboarding, PT capacity and utilisation.
7. Strength outcomes, standards and milestones.

No metric changes from `Legacy` or `V2 Shadow` to `V2 Accepted` until its event, definition, freshness, parity and owner gates pass.
