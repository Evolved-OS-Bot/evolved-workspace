# Reporting V2 Acquisition and Onboarding Acceptance Check

**Checked:** 30 July 2026  
**Mode:** Protected shadow  
**Publication authority:** None

## Outcome

The acquisition bridge is technically operating, but the full dashboard-publication gate has not passed.

- Lead and unique Strength Assessment booking collection passed the source check.
- Prequalification passed as a current-state measure, but GHL does not provide a historical completion timestamp. Historical prequalification remains confidence-labelled rather than exact event history.
- Unique conversion attribution worked without Fast Track SGPT/PT double-counting. Five sampled attributed sales matched one delivered assessment each.
- Four of five sampled unlinked sales have exact-date tracked Strength Assessments in Trainerize. The fifth, Jess Michels, is owner-confirmed as attended from direct camera evidence; the absent tracked assessment and consultant submission are an accepted historical recording gap with no further chase required.
- The first onboarding bridge missed Fast Track and PT-only sessions booked directly into normal trainer PT calendars. This was a real architecture defect and was repaired before publication.
- Six elapsed onboarding and first-PT appointments had exact-date tracked onboarding sessions in Trainerize. Their GHL outcomes were corrected to `Showed`, and onboarding completion speed is now available in protected shadow mode.

## Representative sample

Thirty cases were reviewed read-only against live GHL:

| Area | Sample | Result |
|---|---:|---|
| Prequalification | 10 assessment appointments | Five current-state completions and five incomplete states reproduced exactly; historical completion timing remains unavailable |
| Unique conversion | 10 agreement sales | Five linked to one exact assessment each; five remained unresolved due to missing terminal attendance |
| Onboarding | 10 onboarding-required sales | Missing trainer PT-calendar coverage identified and repaired; future booked, elapsed-unverified and genuinely unbooked states remained distinct |

The Fast Track fixture remained one sale and one conversion even though it carried both SGPT and PT service components.

## Calendar coverage repair

The original bridge read the generic onboarding calendar and four trainer Intro calendars. It did not include the current Nora Intro calendar or the normal 30, 45 and 60-minute trainer PT calendars used for Fast Track and PT-only starts.

Deployment `b54dfb06-2d6b-499e-b58e-1e4ab737c12e` expanded the governed calendar set and added entitlement-specific matching:

- Strong can match onboarding or Intro appointments, but not an unrelated PT session.
- Fast Track can match onboarding, Intro or the first trainer PT session after sale.
- PT-only can match Intro or the first trainer PT session after sale.
- Fit & Flexible remains outside the onboarding denominator.
- Duplicate same-contact, same-time, same-trainer appointments collapse to one operational booking.

The repair changed historical onboarding-required sales with a linked booking from 37 of 109 to 82 of 109. It reduced the unbooked group from 72 to 27 and correctly recovered a known recent Fast Track first session.

## Repaired shadow metrics

| Period | Leads | Unique SA bookings | Prequalification | Unique conversion | Sale to first onboarding booking |
|---|---:|---:|---:|---:|---:|
| Completed week, 20–26 July | 17 | 4 | 0/4 | 2/2 | 3.00 days across 2 linked sales |
| Rolling 28 days | 67 | 19 | 5/19 | 7/11 | 3.82 days across 11 linked sales |
| Rolling 90 days | 199 | 60 | 24/60 | 20/36 | 3.74 days across 31 linked sales |

These remain shadow observations. The existing KPI workbook and accepted CEO dashboard were not changed.

## Trainerize attendance corroboration

Trainerize was checked against the questioned appointments using exact client identity, exact Brisbane appointment date and a tracked session. A scheduled session alone is not sufficient.

| Appointment type | Verified as Showed | Remaining unresolved |
|---|---|---|
| Onboarding | India Armstrong, Vaishnavi Vakacharla, Vineela Velaga, Jade Wright, Grace Arnell and Hannah Hobman | None |
| Strength Assessment | Vineela Velaga, Sarah Loga, Tara Berge and Stephanie Jones; Jess Michels by owner-confirmed camera evidence | None |

The six onboarding records matched a tracked `On-boarding Session`. Four assessment records matched a tracked `Women's Standard Strength Assessment`. Jess Michels is a separate governed manual case based on Peter's direct camera observation.

Jess Michels's exact 3 July appointment was changed from Confirmed to Showed on 31 July and read back successfully. The owner-confirmed correction counts her in both the attendance/show-rate numerator and denominator. Trainerize still contains no exact-date tracked Strength Assessment and the consultant feedback is absent. Peter accepted those missing records as a permanent historical recording gap; no further chase is required and they are not contrary attendance evidence.

## Onboarding completion control

Deployment `ecec9d28-e116-48be-b443-627ad79aa8cd` activated the governed outcome follow-up:

- six recent elapsed `Confirmed` appointments had a known assigned trainer;
- six trainer tasks were created;
- zero routing exceptions occurred;
- the six Admin Eve escalations were deferred;
- an Admin escalation is created only on the next twice-daily cycle if the trainer task is still unresolved;
- the task closes automatically after GHL records `Showed`, `No show` or `Cancelled`;
- no client message is sent and no appointment outcome is inferred.

After the Trainerize verification:

- all six trainer tasks were completed automatically;
- no Admin escalation was created;
- zero onboarding outcome tasks remain open for this group;
- the rolling 28-day onboarding completion speed is 4.33 days across six verified completions;
- the completed week is 3.00 days across two verified completions.

Railway deployment `93b2689c-3646-4af4-9f0f-935ee5e0902f` also made concurrent attendance refreshes idempotent after the verification run exposed a duplicate-decision race. The repaired refresh completed successfully.

The initial refreshed rolling 28-day unique Strength Assessment conversion was 9 of 13, or 69.2%. These observations remain shadow metrics and have not replaced the accepted CEO dashboard.

## Permanent Trainerize pre-check

Railway deployment `bc0d56ed-24a0-4266-9216-0eea195fcabb` made the evidence check automatic before either Strength Assessment or onboarding outcome tasks are created.

The controller now:

1. matches the GHL contact to one active or deactivated Trainerize client by exact email, or by one unique exact full name when email is unavailable;
2. requires the same Brisbane appointment date;
3. requires exactly one tracked session with the governed session name;
4. re-reads the live GHL appointment immediately before changing it;
5. permits only `Confirmed` to `Showed`;
6. verifies that GHL retained `Showed`;
7. creates the normal staff task if identity, evidence, source availability or the GHL write is missing or ambiguous.

The first live automatic cycle found two additional exact Strength Assessment matches:

- Mariya Boycheva, 27 July, Trainerize session `1143436541`;
- Karissa Mclaren, 24 July, Trainerize session `1141679327`.

Both GHL appointments were changed to `Showed`, no fallback task was needed, and stale governed tasks were closed. Two unresolved current cases retained normal staff follow-up. The accepted attendance refresh then recorded six explicit Showed assessments, up from four, with 39 wider unresolved historical or current events.

Because Mariya and Karissa did not add attributed sales, the rolling 28-day conversion denominator increased from 13 to 15 while the numerator remained nine. The current protected shadow conversion is therefore 9 of 15, or 60.0%. This is the correct event-level result rather than a deterioration caused by duplicate counting.

Deployment `ed90e9de-0e4a-4ef9-9ad7-c535e80e7094` corrected the original active-account-only scope. Historical attendance now searches both active and deactivated Trainerize profiles, deduplicates by Trainerize user ID and prefers the active copy when the same account appears in both views.

The first corrected run recovered Indie Cevallos's exact deactivated account and tracked 29 July Strength Assessment, session `1145161709`. Her GHL appointment was changed from Confirmed to Showed, the write was verified and both governed follow-up tasks closed. Bita Gusti's 30 July appointment is confirmed Cancelled in GHL. It requires no Trainerize attendance inference or trainer follow-up and remains in cancellation reporting, leaving no current assessment unanswered.

The live GHL source now contains eight explicit Showed assessments after Jess's owner-confirmed correction. The accepted attendance refresh includes her in both the attendance/show-rate numerator and denominator. Her missing consultant submission is an accepted historical recording gap, not an open process or attendance exception.

## First funnel comparison cycle: 31 July 2026

The current GHL acquisition and onboarding source completed successfully as
snapshot `20260731T022715Z-f6180343`. The approved 30-case sample now has zero
unexplained event differences.

The hub recorded protected legacy-versus-V2 comparisons for the completed
week, rolling 28 days and rolling 90 days. Six of the seven CEO funnel metrics
passed in all three periods:

- new leads;
- unique Strength Assessment bookings;
- prequalification completion;
- unique Strength Assessment conversion;
- sale-to-onboarding booking speed;
- sale-to-onboarding completion speed.

The legacy differences are explained definition changes rather than hidden
tolerances. Reporting V2 counts GHL contact creation instead of source-filtered
Appointments rows, excludes cancelled and invalid appointments, uses governed
GHL prequalification state, counts one appointment series and one qualifying
sale, and does not double-count Fast Track through its SGPT and PT components.
The two onboarding-speed measures have no legacy workbook equivalent.

Matched consultant feedback now counts as delivery evidence for the shadow
show-rate metric, consistently with the existing conversion rule. This changed
the shadow showed numerators to 3 for the completed week, 17 for 28 days and 43
for 90 days without enabling GHL status writes.

Show rate remains failed and unavailable for acceptance because one elapsed
appointment in the completed week, two in the rolling 28 days and 15 in the
rolling 90 days still lack a governed terminal outcome. These are not treated
as no-shows. Railway deployments `4f06b973-303d-4d3c-b38f-5409da217774` and
`3160da25-6e9b-4928-a7a8-41cd915ca879` made the evidence alignment and
authenticated shadow-only comparison ingestion live. All 139 hub tests pass.

The current KPI workbook and accepted CEO dashboard remain unchanged.

## Remaining acceptance gates

1. Close or explicitly classify the remaining elapsed attendance outcomes.
2. Complete the second clean comparison cycle and the scheduled attendance-parity cycle.
3. Obtain owner acceptance before publishing any passed metric to the CEO dashboard.
