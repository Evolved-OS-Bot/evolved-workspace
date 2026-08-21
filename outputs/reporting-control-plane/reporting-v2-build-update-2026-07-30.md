# Reporting V2 Build Update

**Date:** 2026-07-30  
**Overall status:** In progress, deployed protected shadow build  
**Current KPI workbook:** Unchanged and still operating  
**Current CEO dashboard figures:** Unchanged  
**Scheduling:** Railway only

## Plain-English Position

Reporting V2 now has the core machinery needed to stop using Google Sheets as the future database and calculation engine. The hub can retain source events, reconcile them, calculate versioned metrics and prove where each number came from.

The new GHL acquisition bridge is deployed to the existing Railway hub. It is read-only and has no authority to change GHL, Google Sheets or the accepted CEO dashboard.

Railway deployment `50d569f2-98e4-4c08-b2e6-1a81c4e9b80e` succeeded on 30 July 2026. Live verification returned `mode: shadow`, `publication_authority: none` and `legacy_reporting_unchanged: true`.

The first scheduled source cycle failed closed because the hub Railway service did not yet have `GHL_API_KEY` and `GHL_LOCATION_ID`. Railway-managed references to the existing PT Booking Shadow credentials were added, and deployment `c3ee08a5-fb21-4fc8-83e8-8186a192a958` restored the reviewed V2 build with those references attached.

The first owner-triggered shadow cycle then completed:

- Strength Assessment attendance accepted 109 appointments: 23 cancelled and 86 still recorded as confirmed;
- no Consultant Feedback evidence was returned, leaving 84 elapsed confirmed appointments unresolved;
- GHL acquisition read 2,791 contacts, 885 WARM opportunities, 779 prequalified records, 156 agreement-based sales and 47 reactivations;
- 3,570 acquisition source events were accepted;
- zero sales were attributed because there were no governed attended assessments;
- show rate and unique conversion remain unavailable rather than being estimated;
- no legacy dashboard figure changed and V2 publication authority remains `none`.

Peter subsequently confirmed that, before explicit attendance tracking, elapsed appointments remaining on the Strength Assessment list represented women who attended because no-shows and cancellations were deleted. Deployment `bad4101c-0f1d-47da-bd86-ea54a0559756` introduced the first protected legacy treatment. Peter then supplied the correct historical boundaries:

- listed show-rate tracking begins on 12 March 2026;
- listed sales-conversion history is valid from the first Appointments row on 19 September 2025;
- pre-12 March surviving rows are retained as `legacy_attended` for conversion only;
- from 12 March onward, conversion uses only rows explicitly listed Show?=`Y` as its attended denominator;
- listed show rate is Show?=`Y` divided by explicit Show?=`Y` plus Show?=`N`;
- a listed `N` is not guessed to mean cancellation because the list has no separate cancellation field;
- the governed event-level cancellation rate remains separate and requires an explicit cancellation event;
- the Railway hub now contains separate `sa_listed_show_rate` and `sa_listed_conversion_rate` shadow definitions and a read-only Appointments collector;
- the current workbook and accepted CEO dashboard figures remain unchanged.

Railway deployment `973d2529-5a56-4ac2-87fd-2c45c98f6d46` is healthy. The first corrected production shadow refresh recorded:

- listed show rate: 96 of 124, or 77.42%, from 12 March 2026;
- listed conversion rate: 127 of 216, or 58.80%, from 19 September 2025;
- two converted rows with blank attendance retained in the listed conversion numerator and surfaced as attendance mismatches;
- `publication_authority: none`.

Deployment `9d685d10-dafb-4dfc-a574-483c48cd7074` adds permanent parity records. All six completed-period comparisons passed with zero unexplained events. Conversion matches exactly at 2/2 for the completed week, 10/13 for 28 days and 34/54 for 90 days. Show rate differs only because the workbook includes blank attendance cells in its denominator: one blank for the week and five for both 28 and 90 days. The full evidence is in `outputs/reporting-control-plane/sa-listed-parity-2026-07-30.md`.

## Build Map

| Component | Position | What it does now | Next gate |
|---|---|---|---|
| Shared event ledger | Deployed in shadow | Stores immutable source-event versions with UTC time, Brisbane date, source ID, confidence and payload hash | First source cycle |
| Metric engine | Deployed in shadow | Stores definitions, periods, values, numerators, denominators and event lineage | First metric cycle |
| Week, 28-day and 90-day periods | Deployed in shadow | Uses one Brisbane reporting calendar | Source parity |
| Rolling $1m cash goal | Definition built | Measures accepted cash excluding GST over the preceding 365 days and retains first achievement time | Payment event bridge |
| Strength Assessment attendance | Built, pending live validation | Reconciles GHL appointment status with Consultant Feedback evidence | Complete shadow cycles |
| GHL leads | Bridge deployed in shadow | Creates one lead event from the GHL contact creation event | Collect and compare |
| GHL prequalification | Bridge deployed in shadow | Reads the governed WARM pipeline and records completed/current-stage evidence without inventing missing transition times | Collect and compare |
| Strength Assessment appointment series | Foundation built | Keeps immutable appointment IDs and supports rebook grouping | Historical and live series validation |
| Qualifying sales | Bridge deployed in shadow | Reads signed membership/PT agreement evidence and supporting Won WARM opportunity state | Collect and compare |
| Unique assessment conversion | Deployed in shadow | Uses the approved 30-day most-recent-attended rule; reactivations are excluded | Collect and compare |
| Fast Track sale treatment | Built and tested | One commercial sale and one conversion, with SGPT and PT service components | Live fixture |
| Historical migration | Contract built | Hashes original workbook rows and assigns visible confidence | Run bounded backfill |
| Listed assessment history | Built locally in shadow | Reads Appointments without editing it; applies the 12 Mar show and 19 Sep conversion boundaries independently | Deploy, refresh and compare |
| Manual inputs | Built, disabled | Requires source reference and independent approval | Approver/absence-cover decision |
| Google V2 board pack | Contract built, not created | Defines protected output, manual input, exception, dictionary and source-health tabs | Create after first three metric families pass |
| Cash and payment events | Existing evidence plus V2 contract | Existing hub has Stripe/PT Minder evidence, but V2 cash allocations and GST removal are not yet connected | Build payment bridge |
| Lifecycle history and growth | Current-state reconciliation exists | Current active position is governed; full event history is not yet a V2 ledger | Build lifecycle event bridge |
| Onboarding speed | Not connected | Dashboard correctly remains unavailable | Build GHL onboarding appointment bridge |
| PT capacity/utilisation | Workload available, capacity missing | Booked sessions/hours can be reported; true utilisation cannot | Approve and load trainer capacity |
| Strength outcomes/standards | Source analysis exists | Trainerize evidence exists outside full V2 metric publication | Complete governed scoring adapters |

## GHL Bridge Rules

- Contact `dateAdded` is the lead-created event.
- The WARM Sales Pipeline is the prequalification state authority.
- The exact GHL Strength Assessment appointment ID remains the appointment identity.
- Signed Membership Agreement Date or PT Agreement Date supplies commercial agreement evidence.
- A Won WARM opportunity corroborates conversion but does not replace the agreement.
- A sale converts the most recent attended assessment inside 30 days.
- Returning former members are reactivations.
- A late sale can update the original assessment cohort while retaining the original No Sale evidence.
- A Fast Track agreement is one sale with SGPT and PT components.
- Invalid or missing agreement dates do not create synthetic sales.
- Date-only agreement fields are explicitly labelled date precision, not falsely presented as exact timestamps.

## Scheduled Shadow Design

The live Railway order is:

1. Strength Assessment attendance refresh runs at 06:10 and 18:10 Brisbane.
2. GHL acquisition V2 reads contacts and the WARM pipeline at 06:18 and 18:18.
3. The Appointments historical-list bridge runs read-only at 06:22 and 18:22.
4. Hub compatibility/source health runs at 06:25 and 18:25.

The acquisition job is also available through an authenticated manual shadow-refresh endpoint. It does not publish accepted CEO metrics.

## Verification

- 92 Operating Data Hub tests pass.
- 333 non-live local regression tests pass.
- The two excluded repository collectors are pre-existing and unrelated:
  - one script performs a live GHL call during test collection;
  - the Stripe handler test requires its separate service dependency environment.

## Next Build Order

1. Deploy and run the listed-history bridge.
2. Compare listed show rate from 12 March and listed conversion from 19 September against the unchanged workbook.
3. Connect the Consultant Feedback evidence source for the governed event-level cohort.
4. Compare leads, prequalification, attendance, sales and unique conversion for the same period.
5. Resolve event-level differences without changing the workbook.
6. Collect the required clean shadow cycles.
7. Build the accepted Stripe/PT Minder/bank cash allocation bridge for the rolling $1 million measure.
8. Continue lifecycle, onboarding, PT utilisation and strength adapters.

No metric is ready for cutover merely because its code exists. Cutover requires accepted source completeness, event parity and owner sign-off.
