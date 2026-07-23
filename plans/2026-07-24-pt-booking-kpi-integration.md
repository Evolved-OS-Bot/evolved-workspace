# PT Booking KPI and Brown & Casserly Integration

**Status:** Live  
**Created:** 24 July 2026

## Objective

Extend the deployed PT Booking Continuity Shadow so its Monday run:

1. keeps reconciling GHL PT appointment continuity;
2. uses Brown & Casserly as corroborating operational evidence;
3. exposes Stripe entitlement and Trainerize access disagreements without allowing either the workbook or a name-only match to override live evidence;
4. writes two weekly KPI measures to the matching Monday column:
   - PT Bookings: literal appointment count;
   - PT Booked Hours: total scheduled delivery minutes divided by 60.

## Source hierarchy

1. GHL calendar events: appointments that exist.
2. Stripe: recurring commercial entitlement.
3. Trainerize: active coaching access.
4. Brown & Casserly: documented trainer, duration, frequency, debit, cancellation and downgrade evidence.
5. GHL conversation history and owner review: structured-source conflict resolution.

The workbook is evidence and a KPI destination. It does not authorise appointment creation, removal or lifecycle changes.

## KPI rules

- Week: Monday 00:00 to the following Monday 00:00 in Australia/Brisbane.
- Trainer attribution: exact active PT calendar registry name, using Megan, Piper, Nora, Katrina and Leisa.
- Include active scheduled PT calendar events.
- Exclude deleted, cancelled, canceled, no-show and no_show events.
- Deduplicate first by event ID, then defensively by contact ID plus start time.
- Bookings: one per retained appointment.
- Booked hours: retained appointment duration in minutes divided by 60.
- Write to the column whose row-one date equals the Monday being measured.
- Update fixed cells rather than append, making retries idempotent.
- Preserve the legacy manual trainer block and all historical values.

## Implementation

1. Add deterministic weekly KPI aggregation with tests for trainer attribution, exclusions, deduplication and mixed 30/45/60-minute appointments.
2. Add a Google Sheets adapter supporting:
   - a local service-account file;
   - a protected Railway service-account JSON environment variable;
   - exact sheet, section, trainer and week validation;
   - batch write of both trainer blocks and totals.
3. Add an explicit `KPI_WRITE_ENABLED` safety switch, defaulting to false.
4. Add KPI write evidence to the persistent state database.
5. Add current-trainer KPI blocks to Brown & Casserly without altering the legacy block.
6. Extend the Monday run to write the KPI only after a successful GHL read and calculation.
7. Update the README, setup documentation, roadmap and workspace index.
8. Run the complete test suite.
9. Deploy with writes disabled, validate a private calculation against the live calendar, then enable the Monday write only after the target cells and service-account access are confirmed.

## Cross-system reconciliation follow-on

Reuse the deterministic identity register already built by `scripts/membership_reconciliation.py` rather than creating another fuzzy identity layer. The Railway service will need protected Stripe and Trainerize credentials, plus either a shared read-only reconciliation snapshot or the relevant readers packaged into the service.

This follow-on should add evidence to the Monday report before it can affect KPI inclusion. PT bookings remain counted from GHL calendars; Stripe and Trainerize disagreements become exceptions, not reasons to silently delete a booking from the utilisation figures.

## Acceptance criteria

- Both measures are reproducible from one retained appointment set.
- The current trainer roster is represented without rewriting historical trainer attribution.
- A retry updates the same dated cells and cannot shift a week.
- A missing/duplicate date, trainer row or section fails closed.
- Sheet writes remain off unless explicitly enabled.
- Existing read-only GHL boundary and all prior reconciliation tests continue to pass.

## Progress: 24 July 2026

- Added deterministic appointment-count and booked-hours aggregation.
- Added exact current-trainer attribution and cancelled/deleted/no-show exclusions.
- Added defensive event and contact/start deduplication.
- Added fail-closed Google Sheets layout validation and idempotent dated-cell updates.
- Added protected Railway JSON and local credential-file authentication options.
- Added persistent KPI write evidence.
- Preserved the legacy manual trainer block and added two current-roster automated blocks.
- Validated the week of 20 July against live GHL calendar events: 63 bookings and 36.5 booked hours.
- Seeded the verified 20 July figures into the new Brown & Casserly blocks.
- Expanded the workspace metrics reader to report both KPIs.
- Thirty-seven PT shadow tests pass.

The owner approved production credential configuration and requested Stripe
and Trainerize connection on 24 July. A read-only source check returned 215
Stripe identities with subscription history, 92 currently entitled Stripe
identities, 165 active Trainerize clients and 47 email/phone-keyed Active PT
workbook records.

The production integration is now complete. Railway holds protected Google,
Stripe and Trainerize credentials, uses a dedicated calendar-capable GHL
credential, and shares the existing protected report-email credential.
`KPI_WRITE_ENABLED=true` is live.

Production run `742317c6-1075-4160-8e38-146cf7529ede` completed across all four
sources for 107 contacts and 130 findings, with no source-unavailable errors.
The Brown & Casserly cells for the week of 20 July were verified at 63 bookings
and 36.5 booked hours after the idempotent write.
