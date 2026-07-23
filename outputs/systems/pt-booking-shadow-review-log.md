# PT Booking Shadow Review Log

**Started:** 23 July 2026
**Purpose:** Record owner-verified findings from the read-only PT booking-continuity pilot and convert them into system rules.

## Source hierarchy

No single current system is sufficiently complete to determine PT booking continuity by itself.

1. GHL calendars are the source of truth for appointments that exist.
2. Stripe is the source of truth for active recurring billing and next-payment timing.
3. PT Minder is the source of truth for active prepaid PT packs and remaining pack entitlement.
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

## Open decisions before implementation

- Confirm whether Railway can receive the existing Google service-account credential through a protected environment variable, or whether a dedicated read-only service account should be created.
- Confirm the intended lead time for prepaid pack renewal prompts.
- Confirm which structured system should own PT commercial mode when Brown & Casserly, Stripe and PT Minder disagree.
