# PT Booking Shadow Review Log

**Started:** 23 July 2026
**Purpose:** Record owner-verified findings from the read-only PT booking-continuity pilot and convert them into system rules.

## Source hierarchy

No single current system is sufficiently complete to determine PT booking continuity by itself.

1. GHL calendars are the source of truth for appointments that exist.
2. Stripe is the primary payment source for both recurring PT and prepaid PT pack purchases.
3. PT Minder remains the operational source for unused sessions remaining on a prepaid pack. A Stripe payment proves purchase, but does not by itself prove the current session balance.
4. Brown & Casserly Pty Ltd 2026 is a secondary operational cross-check:
   - `Active SGPT` can support membership-status and membership-tier checks.
   - `Active PT` can support PT frequency, session length and debit checks.
   - `PT Cancellations` and `SGPT Cancellations` can support cancellation and downgrade checks.
5. GHL conversation history is required when the structured sources disagree or a service change may have been agreed informally.
6. Peter's verified ruling is authoritative for the pilot review and should be used to correct the underlying systems.

The workbook must not override live calendars, Stripe or PT Minder. The first review found stale trainer assignments, legacy tier naming, an apparent debit-versus-pack contradiction and missing active PT records.

## Review 1: internal gaps and cancellation boundaries

| Contact | Original finding | Verified position | Required system treatment | Operational follow-up |
|---|---|---|---|---|
| Bree Coleman | Internal Friday gap on 24 July and tail gap on 16 October | Active in Stripe and a Fast Track member. Booked with Katrina on 27 July, then Fridays from 7 August to 9 October. Brown & Casserly shows her active, but has stale Marnie ownership and legacy Silver naming. | Do not automatically call 24 July a missed session. Classify the Monday-to-Friday transition as a pattern-boundary ambiguity until message history or Admin confirms the intended first week. Tail coverage after 9 October remains a future top-up forecast. | Review message history and the recurrence start. Do not create an extra July session without confirmation. |
| Emma Spowart | Internal gap on 27 July and tail gap on 19 October | A four-week rush surgery hold was confirmed by SMS on 17 July, with Stripe next payment on 18 August. On 21 July Emma advised that she is returning to the UK and expects another surgery; Admin replied on 23 July that the membership will be cancelled on receipt of a medical certificate. | Reclassify as `STATUS_TRANSITION_PENDING_EVIDENCE`, suppress booking and top-up recommendations, and retain the message evidence. Do not complete a return-date-based hold record after the member has requested cancellation. | Admin is already awaiting the medical certificate. Complete the medical cancellation through the canonical cancellation system when it arrives. |
| Jody Burke | Missing Thursday session on 30 July | Active PT at two sessions per week. The live calendar contains recurring Tuesday 7:30 am and Thursday 7:00 am series through early November. Piper explicitly confirmed the one-session week of 27 July and the three-session week of 3 August by SMS on 20 July; Jody accepted both schedules. The corrected live audit now pairs the Friday 7 August surplus with the prior week's deficit. | Reclassify as healthy with one adjacent-week make-up. Treat the next week's normal sessions as protected before consuming only its surplus appointment. | Complete. No booking write or removal required. |
| Rose Heimans | Missing 23 July plus tail gaps after 10 September | Active in PT Minder and a Fast Track member. Booked with Nora every Thursday from 30 July to 10 September, then due for rebooking. Brown & Casserly contains stale Piper ownership. | Treat 23 July as a start-boundary ambiguity, not a confirmed missed session. Reclassify dates after 10 September as a future rebooking or top-up requirement. | Prompt before the 10 September booked-through date. |
| Deb Farrell | Six internal gaps from late September to October | Active prepaid PT pack. Regular Wednesday and Saturday bookings continue to 10 October, which is the end of the pack. Brown & Casserly currently looks like weekly debit, so it is not reliable for commercial mode here. | Do not extend automatically. Classify as `PACK_END_DECISION_REQUIRED`, with a lead-time prompt to resume debits or purchase another pack. | Contact before pack exhaustion and record the chosen commercial pathway. |
| Janice Ting | Three Friday gaps in October | Piper's 15 July SMS confirms that all Tuesday sessions were moved to Wednesday at 12:00 pm. The live calendar contains the recurring Wednesday noon series from 29 July through 4 November and Friday bookings through 25 September. The corrected live audit recognises both patterns and proposes Friday top-ups on 2, 9 and 16 October. | Retain the `GAP_INSIDE_SERIES` forecast. This is a genuine rolling-horizon Friday top-up, not a missing Wednesday series. | Add the next Friday block through the required horizon during the normal Admin rebooking process. |
| Bethany Watson | PT cancellation active with no final-access date | The contact was entered as Bethan Watson in the form. She decided not to cancel and was retained. Brown & Casserly shows Beth Watson active in both Active SGPT and Active PT. On 23 July the GHL contact was renamed Bethany Watson, the four stale cancellation fields were cleared and the erroneous `old pt client` tag was removed. Her recurring PT series already runs through 6 October. | Reclassify as `CANCELLATION_REVERSED`. Use stable contact ID or email matching rather than name-only matching. | Complete. |
| Cathy James | PT cancellation active with no final-access date | Downgrading from Fast Track to Bronze, which has no PT inclusion. The 24 July session is the final PT session. Brown & Casserly contains a PT cancellation row dated 10 June. On 23 July the GHL final-access field was set to 24 July; the calendar contains that session and nothing later. | Reclassify as `PT_END_CONFIRMED`. Retain the final appointment and suppress every top-up after it. | Complete. |
| Khatya da Silva Martins | PT cancellation active with no final-access date | Confirmed cancelled PT client with no future PT booking. | Classify as `CANCELLED_NO_FUTURE`. Missing final access is a lower-priority record-completeness issue when there is nothing future to protect or remove. | Clean the record when practical. |
| Melissa van der Walt | PT cancellation active with no final-access date | Confirmed cancelled PT client with no future PT booking. | Classify as `CANCELLED_NO_FUTURE`. | Clean the record when practical. |
| Renae Acton | PT cancellation active with no final-access date | Confirmed cancelled PT client with no future PT booking. | Classify as `CANCELLED_NO_FUTURE`. | Clean the record when practical. |

## Required shadow-system changes

1. Add a read-only Brown & Casserly adapter keyed by normalised email first, then phone, never name alone.
2. Read `Active SGPT`, `Active PT`, `PT Cancellations` and `SGPT Cancellations`; preserve the source tab and row as evidence.
3. Treat workbook data as corroborating or conflicting evidence, not an automatic override.
4. Add classifications for:
   - `PATTERN_BOUNDARY_CONFIRMATION_REQUIRED`
   - `HOLD_DATA_INCOMPLETE`
   - `PACK_END_DECISION_REQUIRED`
   - `CANCELLATION_REVERSED`
   - `PT_END_CONFIRMED`
   - `CANCELLED_NO_FUTURE`
5. Separate included PT, recurring PT debit and prepaid PT pack pathways.
6. Apply the same-week replacement rule before proposing canonical recurring bookings.
7. Show source conflicts explicitly, including stale trainer, frequency, product and payment-mode data.
8. Do not permit any automated booking or removal from the workbook alone.
9. Continue using `GET /calendars/events` as the authoritative appointment ledger. The manual review confirmed that `GET /contacts/{contactId}/appointments` can omit expanded recurring instances, but the deployed service was already using calendar events.
10. Count same-week reschedules against weekly entitlement.
11. Allow a bounded one-week carry-over: match the following week's expected sessions first, then use only a surplus session as the prior week's make-up.
12. Keep unexplained extras visible as evidence. Do not recommend removing them without an accepted cancellation or explicit Admin review.
13. Hydrate active hold and cancellation contacts from their full GHL record before using status-sensitive dates.

## Remaining operating decisions

- Confirm the intended lead time for prepaid pack renewal prompts.
- When sources disagree, use Stripe for whether and how the client paid, PT Minder for remaining prepaid sessions, and Brown & Casserly only as corroborating documentation.

## KPI decisions completed: 24 July 2026

- Track both literal PT bookings and booked delivery hours.
- Preserve the stale trainer block as legacy historical data rather than relabelling prior values.
- Use new automated blocks for Megan, Piper, Nora, Katrina and Leisa.
- Use an idempotent snapshot in the column whose header matches the Monday being measured.
- Count only active PT calendar events; deduplicate by event ID and contact/start time; exclude deleted, cancelled and no-show appointments.
- Record the week, values and target cells in the persistent service state after every successful write.
- The first verified baseline for the week of 20 July is 63 bookings and 36.5 booked hours.

## Production integration completed: 24 July 2026

- Railway now has protected read-only credentials for Google Sheets, Stripe and Trainerize.
- The report email credential is a protected shared project variable. Reports are addressed to `admin@theevolvedgym.com.au`.
- A dedicated calendar-capable GHL credential prevents the PT service from inheriting the triage service's narrower GHL access.
- `KPI_WRITE_ENABLED=true` is live. The Monday-column write was verified in `AU115:AU130`: 63 bookings and 36.5 booked hours, with the five trainer rows matching the live calendar calculation.
- Production run `742317c6-1075-4160-8e38-146cf7529ede` completed for 107 contacts and produced 130 findings.
- The run produced no `CROSS_SYSTEM_SOURCE_UNAVAILABLE` finding, confirming that GHL, Stripe, Trainerize and Brown & Casserly were all readable.
- Cross-system findings included 17 commercial-evidence reviews, 3 Trainerize-access reviews, 2 missing workbook PT records and 1 deterministic identity review.
- The service remains read-only for contacts, appointments, Stripe, Trainerize and lifecycle state.
- Thirty-seven regression tests pass.

## Prepaid PT pack correction: 24 July 2026

- Owner correction: Stripe is the main payment processor for prepaid packs, not only recurring subscriptions.
- Shaanta Boyes's recent $2,400 pack was paid through her husband Archer Boyes's Stripe customer account.
- The successful PaymentIntent has no invoice, description or metadata. Stripe therefore cannot infer Shaanta as the beneficiary without an explicit relationship.
- The reader now includes successful non-invoice PaymentIntents from a bounded 365-day window.
- A governed mapping can link a PaymentIntent ID to the beneficiary's GHL contact ID. This is deterministic and does not weaken the rule against name-only matching.
- Verified mapped pack payments satisfy the commercial-evidence check. An unverified one-off payment on the client's own payer email produces `STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED` instead of being silently treated as a subscription failure.
- Shaanta's $2,400 PaymentIntent is mapped to her GHL contact. The live reader verified the payment at 240,000 cents AUD.
- PT Minder still owns the remaining-session balance and pack-exhaustion decision.
- Forty regression tests pass after this correction.
- Production run `904fb075-7f99-4da7-80f3-090c36926a25` completed for all 107 contacts with no source error.
- The generic commercial-evidence queue reduced from 17 to 12. Four same-email one-off payments moved into the more accurate `STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED` queue, while Shaanta's approved third-party payment was accepted as verified pack evidence.
