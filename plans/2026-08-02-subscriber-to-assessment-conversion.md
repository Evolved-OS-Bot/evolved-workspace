# Subscriber to Strength Assessment conversion

**Status:** Complete, live in Reporting V2 shadow mode  
**Owner:** Peter Brown  
**System:** Railway Operating Data Hub, Reporting V2 shadow dashboard

## Objective

Measure whether unique website subscribers become genuine Strength Assessment bookings without allowing repeat form submissions, rebooks, cancellations or SGPT/PT service components to inflate the result.

## Governed rule

- Denominator: unique GHL contacts whose earliest accepted `30DNNC Form` submission occurred in the selected completed Brisbane-local period.
- Numerator: denominator contacts with at least one non-deleted Strength Assessment appointment created in GHL at or after their first subscription and no more than 30 days later.
- A person counts once even when she submits the form repeatedly, reschedules, books more than one assessment, or later buys both SGPT and PT.
- Confirmed, showed, no-show and cancelled appointments prove that a booking occurred. Invalid, deleted, unknown or pre-subscription appointments do not.
- The appointment `dateAdded` field is the booking timestamp. The appointment start time remains the authority for Sales attendance and conversion reporting.
- Recent subscriber cohorts are an as-of-now conversion view and can rise during their 30-day booking window. They are labelled as such rather than presented as a mature final rate.
- GHL contact ID is the only automatic identity key. Missing or contradictory identity/timestamp evidence fails closed.

## Architecture

1. Preserve GHL appointment `dateAdded` as governed `booked_at` evidence in the existing Strength Assessment observation contract.
2. Reuse immutable website subscription events already stored in Reporting V2.
3. Calculate one `subscriber_to_sa_booking_rate` observation for each completed week, 28-day and 90-day period during the existing GHL acquisition refresh.
4. Publish only aggregate numerator, denominator and rate on the protected Reporting V2 preview. Identified matches remain inside the governed Hub.
5. Keep the accepted CEO dashboard and KPI workbook unchanged until parallel acceptance is complete.

## Acceptance gates

- Unit tests prove repeat submissions and multiple appointments count once.
- Tests prove pre-subscription, deleted and invalid appointments are excluded.
- A live read-only refresh records non-negative aggregate results for all three periods.
- The displayed numerator never exceeds the unique-subscriber denominator.
- No GHL, Google Sheet, membership, payment or workflow write occurs.

## Retirement path

The placeholder `Individual subscriber-to-booking matching is the next acceptance gate` panel is retired when the governed rate is live. No new schedule is created; the existing Railway GHL acquisition refresh remains the sole calculator.

## Live acceptance result

Railway deployment `34455711-1d8d-4ead-9f3b-c14a8cfd1e28` passed its health check. The website, Strength Assessment and GHL acquisition refreshes then completed in sequence without a source error.

The accepted shadow observations are:

| Period | Unique subscribers | Booked an assessment | Rate | Still inside 30-day window |
|---|---:|---:|---:|---:|
| Completed week | 7 | 2 | 28.6% | 7 |
| 28 completed days | 22 | 10 | 45.5% | 22 |
| 90 completed days | 68 | 32 | 47.1% | 22 |

All 173 Hub tests pass. The numerator is below the unique-subscriber denominator in every period. The accepted CEO dashboard and KPI workbook remain unchanged.
