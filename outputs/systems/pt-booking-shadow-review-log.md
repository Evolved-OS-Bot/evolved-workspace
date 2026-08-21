# PT Booking Shadow Review Log

**Started:** 23 July 2026
**Purpose:** Record owner-verified findings from the read-only PT booking-continuity pilot and convert them into system rules.

## Source hierarchy

No single current system is sufficiently complete to determine PT booking continuity by itself.

1. GHL calendars are the source of truth for appointments that exist.
2. Stripe is the primary payment source for recurring PT and prepaid PT pack purchases. Approved legacy clients may instead have current receipts in PTMinder/EziDebit, which the shadow system does not read.
3. There is currently no verified structured source for prepaid-pack sessions remaining. Stripe proves purchase, but not the unused session balance.
4. Brown & Casserly Pty Ltd 2026 is a secondary operational cross-check:
   - `Active SGPT` can support membership-status and membership-tier checks.
   - `Active PT` can support PT frequency, session length and debit checks.
   - `PT Cancellations` and `SGPT Cancellations` can support cancellation and downgrade checks.
5. GHL conversation history is required when the structured sources disagree or a service change may have been agreed informally.
6. Peter's verified ruling is authoritative for the pilot review and should be used to correct the underlying systems.

The workbook must not override live calendars or Stripe. The first review found stale trainer assignments, legacy tier naming, an apparent debit-versus-pack contradiction and missing active PT records.

## Approved rolling-coverage rule

- Run the entitlement and booking-continuity check weekly.
- Trigger a top-up when an eligible recurring client's forward coverage falls below 10 weeks.
- The action is to restore every entitled weekly pattern to a full 13-week horizon, aligned to the same final service week. It is not a fixed three-appointment extension.
- Keep normal GHL appointment notifications enabled until a reliable member calendar subscription or portal replaces that delivery path.
- Do not automatically extend prepaid-pack clients. Flag them for pack-sequence review and resale or renewal instead.

## Recurring-master storage incident: 4 August 2026

A complete live scan of every governed current and retained 1:1 calendar found 18 PT recurring masters. Ten had been created during the prior week's appointment work; eight were older. The initial search understated the total because Piper's live 30-minute calendar is named `30 Min 1:1 - Piper` and does not contain the substring `PT`.

Root cause was conflicting workspace guidance: this review log and the canonical operating rule required a default 13-appointment horizon, but the appointment-rescheduler plan incorrectly instructed exact-count requests to use bounded RRULE recurrence. The permanent rule now prohibits both bounded and open-ended recurring masters for PT. Every target date must be an individual appointment with `isRecurring=false`, and calendar discovery must come from the governed 1:1 registry rather than a name filter.

Peter explicitly approved correction of the eight older masters. All 18 affected masters are now remediated with notifications suppressed: the ten prior-week series contain 121 verified individual appointments, and the eight older series contain 102, for 223 verified individual appointments in total. Exact replacements were secured before matching recurring occurrences were removed.

Historical occurrences were preserved for the open-ended series where GHL supported bounded conversion. One legacy master was non-atomically tombstoned by GHL during its rejected update; its deleted master metadata remains readable, its 13 individual future appointments were verified, and no future recurring occurrence remains.

The independent completion audit scanned all 18 governed current and retained 1:1 calendars, including `30 Min 1:1 - Piper`, from 4 August 2026 through 2 February 2027. Result: zero active future recurring PT events.

## Owner-approved 13-week top-up batch: 31 July 2026

| Client | Confirmed pattern | Restored horizon |
|---|---|---|
| Bree Coleman | Monday 6:00 am with Katrina | 19 October 2026. The apparent 10 August blank is a confirmed 6:00 am trainer-cover appointment in Megan's calendar, so no replacement is required. |
| Erica Olsen | Monday and Thursday 7:30 am with Piper | 22 October 2026. The latest $120 Stripe invoice was paid in full; the 7 and 14 July invoices remain open. |
| Gigi Umlauf | Wednesday 8:00 am with Piper | 21 October 2026 |
| Grace Arnell | Friday 9:00 am with Nora | 23 October 2026 |
| Michelle Sharp | Monday 9:30 am and Tuesday 10:15 am with Nora | 20 October 2026 |
| Rosa Valdivia | Monday and Friday 8:00 am with Piper | 23 October 2026 |

All 20 new appointments were created as confirmed with normal GHL notifications enabled. Multi-session clients were aligned to the same final service week.

## Review 1: internal gaps and cancellation boundaries

| Contact | Original finding | Verified position | Required system treatment | Operational follow-up |
|---|---|---|---|---|
| Bree Coleman | Resolved 31 July: false 10 August gap from a trainer-specific calendar lookup | Active in Stripe and Fast Track. Her canonical pattern is Monday 6:00 am with Katrina. GHL retains a confirmed 10 August appointment at the exact time and duration in Megan's 30-minute PT calendar; it was updated after the Monday series change and is valid trainer-cover coverage. | Reclassify as healthy through 19 October. The locally validated cross-calendar exact match records the expected Katrina calendar and actual Megan cover calendar instead of proposing a duplicate appointment; Railway deployment remains pending. | Complete. A trainer-calendar-specific absence can never establish a client-level gap; search all approved PT calendars by contact ID first. |
| Emma Spowart | Internal gap on 27 July and tail gap on 19 October | A four-week rush surgery hold was confirmed by SMS on 17 July, with Stripe next payment on 18 August. On 21 July Emma advised that she is returning to the UK and expects another surgery; Admin replied on 23 July that the membership will be cancelled on receipt of a medical certificate. | Reclassify as `STATUS_TRANSITION_PENDING_EVIDENCE`, suppress booking and top-up recommendations, and retain the message evidence. Do not complete a return-date-based hold record after the member has requested cancellation. | Admin is already awaiting the medical certificate. Complete the medical cancellation through the canonical cancellation system when it arrives. |
| Jody Burke | Missing Thursday session on 30 July | Active PT at two sessions per week. The live calendar contains recurring Tuesday 7:30 am and Thursday 7:00 am series through early November. Piper explicitly confirmed the one-session week of 27 July and the three-session week of 3 August by SMS on 20 July; Jody accepted both schedules. The corrected live audit now pairs the Friday 7 August surplus with the prior week's deficit. | Reclassify as healthy with one adjacent-week make-up. Treat the next week's normal sessions as protected before consuming only its surplus appointment. | Complete. No booking write or removal required. |
| Rose Heimans | Missing 23 July plus tail gaps after 10 September | The earlier review described Rose as active in PTMinder, but the shadow service could not verify that processor. She is booked with Nora every Thursday from 30 July to 10 September, then due for rebooking. Brown & Casserly contains stale Piper ownership; payment evidence must be validated in Stripe or through a completed legacy PTMinder/EziDebit receipt. | Treat 23 July as a start-boundary ambiguity, not a confirmed missed session. Reclassify dates after 10 September as a future rebooking or top-up requirement. | Prompt before the 10 September booked-through date and verify the commercial pathway through the applicable receipt source. |
| Deb Farrell | Six internal gaps from late September to October | Stripe verifies the $2,400 prepaid pack paid 23 January. GHL descriptions show the current series reaching `Session 20/20` on 26 September, then reverting to `Session 14/20` and `Session 15/20` on 3 and 10 October. | The payment is approved and must not return to payment review. Classify the appointment evidence as `PREPAID_PACK_SEQUENCE_REVIEW_REQUIRED`; do not infer remaining entitlement or extend automatically until Admin confirms or corrects the counter sequence. | Contact before pack exhaustion, resolve the two post-terminal labels, and record whether Deb resumes debits or purchases another pack. |
| Bec Barwick | Prepaid payment review plus bookings beyond the apparent pack end | Stripe verifies the $1,800 prepaid pack paid 21 April. GHL descriptions reach `Session 20/20` on 5 August, then revert to `Session 14/20` on 7 August; later bookings through October are unnumbered. | The payment is approved and must not return to payment review. Classify as `PREPAID_PACK_SEQUENCE_REVIEW_REQUIRED`; do not treat the later bookings as paid entitlement until Admin confirms renewal or corrects the sequence. | Resolve the 7 August label and approve a renewal/payment pathway or remove unsupported post-pack bookings. |
| Janice Ting | Resolved 31 July: Friday series-boundary failure | Piper's 15 July SMS confirms that all Tuesday sessions were moved to Wednesday at 12:00 pm. Raw GHL event metadata shows the Wednesday series was created on 15 July as an open-ended recurrence, while the Friday series was created on 17 June as 13 separate one-off appointments ending 25 September. There was no hold, cancellation or member-requested frequency reduction. | Confirmed as an administrative series-boundary failure, not missed historical attendance. The four detected Friday gaps on 2, 9, 16 and 23 October were restored first. Three further Fridays on 30 October, 6 November and 13 November were then added so both weekly entitlements finish in the same service week. Normal notifications were enabled and no duplicates were created. | Complete. Active PT records both weekly patterns as aligned through the service week ending 13 November. Future multi-session top-ups must extend every entitled weekly pattern to the same final service week. |
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
- When sources disagree, use Stripe for whether and how the client paid and Brown & Casserly only as corroborating documentation. Remaining prepaid sessions are currently an unresolved operational-data gap.

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
- No current system has been verified as the remaining-session ledger. Pack exhaustion and renewal timing therefore remain manual until a governed ledger is built.
- Forty regression tests pass after this correction.
- Production run `904fb075-7f99-4da7-80f3-090c36926a25` completed for all 107 contacts with no source error.
- The generic commercial-evidence queue reduced from 17 to 12. Four same-email one-off payments moved into the more accurate `STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED` queue, while Shaanta's approved third-party payment was accepted as verified pack evidence.

## PTMinder scope correction: 24 to 25 July 2026

- The PT Booking Shadow has never connected to or read PT Minder.
- Earlier references to Rose being active in PT Minder and Deb being on a PT pack were anecdotal case-review notes, not evidence available to the shadow system.
- The 25 July line-by-line payment audit established that approved legacy clients can still have current completed receipts in PTMinder/EziDebit.
- PTMinder is not a current onboarding or coaching-delivery system, and the shadow service remains unconnected to it.
- All current source-of-truth language assigning pack balances to PT Minder is withdrawn.
- Stripe remains the default payment source for pack purchases. PTMinder/EziDebit may prove payment for a verified legacy payer, but remaining-session balance is still a separate unresolved data requirement.

## Former PT lifecycle contradiction audit: 27 July 2026

- A live read-only GHL snapshot found 54 contacts carrying `old pt client`.
- Sixteen also retain `personal training`; eight remain in an open PT frequency stage, and two appear in both groups. This produces 22 unique GHL cleanup candidates.
- None of the 22 appears on Brown & Casserly `Active PT`.
- Current Stripe and Trainerize checks found only one commercially active candidate: Cathy James. This is not evidence that she remains a PT client. Her owner-confirmed transition is Fast Track to Bronze, so `old pt client` remains correct and `personal training` is the stale tag.
- The remaining 21 candidates have no current Stripe entitlement, verified prepaid-pack mapping or active Trainerize access.
- The owner approved the complete cleanup batch on 27 July 2026. All 16 stale `personal training` tags were removed while preserving `old pt client`; the eight obsolete PT opportunities were closed as `Abandoned`, retaining their history.
- A live post-write verification confirmed all 24 intended changes and no target drift. The private rollback evidence is stored at `data/private/integration-reporting/former-pt-cleanup-20260727T094321.json`.

## Former PT report suppression: 27 July 2026

- Routine `FORMER_PT` findings are now suppressed from the Admin email, category table, exception cards and attached CSV.
- `FORMER_PT_WITH_FUTURE_BOOKINGS` remains visible because a former client retaining future PT appointments requires operational review.
- The underlying read-only audit and retained evidence remain unchanged.
- All 41 PT Booking Shadow tests pass, including explicit email and CSV suppression coverage.
- Production deployment `678483fa-703d-4332-ad6f-b98cea2c53f4` succeeded on 27 July 2026 through a reviewed code-only Railway package.
- The live health endpoint returned `status: ok`, `schedulerEnabled: true` and `shadowMode: true`. The persistent volume mounted successfully and the runtime logs showed the scheduler and one-minute event processor starting without errors.

## Prepaid pack appointment ledger: 27 July 2026

- Deb Farrell's $2,400 and Bec Barwick's $1,800 successful Stripe PaymentIntents are now explicitly mapped to their GHL contact IDs, preserving Shaanta Boyes's existing mapping.
- These reviewed purchases now satisfy the commercial-evidence check permanently. They no longer return to `STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED` on each weekly run unless the governed mapping changes.
- The live GHL API confirms that the session counter is stored in both the appointment `description` and `notes`. The reader accepts `Session 10/20` and the shorter `10/20` format.
- Counters are read only for verified pack beneficiaries. Appointment text alone can never approve payment.
- Clean sequences can produce a 21-day renewal prompt or a bookings-after-pack-end exception. Multiple totals, duplicate counters or a backwards counter produce `PREPAID_PACK_SEQUENCE_REVIEW_REQUIRED` and no entitlement conclusion.
- Deb's series reaches `20/20` on 26 September, then reverts to `14/20` and `15/20`. Bec's reaches `20/20` on 5 August, then reverts to `14/20`, followed by unnumbered bookings. Both therefore fail closed for Admin review.
- All 47 PT Booking Shadow tests pass.
- Production deployment `060e1d6e-a0ea-458e-a141-b0fb348c3e8b` succeeded. Private no-email run `b41659b3-1e3f-49e9-80c9-a2101ca3a738` completed for 105 contacts with no source error.
- The generic prepaid-payment review queue reduced to one. Three verified pack clients now surface the more accurate sequence-review category.

## Shared reconciliation evidence bridge: 27 July 2026

- Root cause: PT Booking Shadow independently checked only its configured Stripe account, Trainerize and Brown & Casserly. It did not consume the revenue controller's protected PTMinder/EziDebit receipts, alternate-email links, account classifications or resolved PT commercial state.
- The production shadow now reads the shared protected evidence below `/data/revenue-gap-control/`. Direct processor credentials remain isolated; only governed evidence and resolved classifications cross the boundary.
- Current PTMinder/EziDebit evidence now supports Rose Heimans, Rebecca Clarke, Moniqua Reid, Lauryn Brown, Jillian Breen and Anne Leditschke.
- Approved alternate Stripe-email links now reconcile Janice Ting and Emma Spowart. Grace Arnell's approved future start is inherited from the revenue controller rather than reopened as missing evidence.
- Brodie Tsikanaris and Andrea Power retain their PIF or credit-delivery state without a generic missing-payment warning. Pack balance remains a separate controlled question.
- Ann Chang's owner-confirmed external Stripe arrangement is stored as `external_payment_client`. This evidence expires after 14 days unless reconfirmed, preventing an owner exception from becoming permanent stale truth.
- Erica Olsen's current arrears handling remains owned by the revenue controller and no longer becomes a contradictory “no commercial evidence” finding in the booking report.
- GHL lifecycle cleanup removed `personal training` and closed the obsolete PT opportunity for the duplicate `Megan Brown | The Mum Coach` contact. Nirvana Searle was converted to former PT while retaining her Bronze/SGPT membership. Stale `2 p.wk` tags were removed from former clients Renae Acton and Lisa Berlin. Cathy James was already correctly marked former PT after her Bronze downgrade.
- The protected production volume now contains 24 legacy-payment records, 14 identity links and 18 account classifications, each with an authenticated count and fingerprint.
- Eighty-seven combined tests pass.
- Deployment `99e296bf-0cdf-411e-9d31-4e1acb8ec6d6` is healthy. Private run `70d174cc-c526-4601-8acb-f4833600a001` completed with 107 findings and no source error.
- `COMMERCIAL_EVIDENCE_REVIEW_REQUIRED` reduced from 12 to zero. `STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED` reduced from one to zero.

## Cohort, hold and gap-matching correction: 27 July 2026

- `None None` was a malformed duplicate/test contact using `brodie@rokstarsalon.com.au`; `Pippa Mae` was a test contact using a placeholder phone number. Both had only the GHL `personal training` tag, no future PT bookings, no supported payment evidence and no active Trainerize access. The owner approved deletion and both GHL contacts were deleted.
- Sue was explicitly removed from this review and no change was made to her record.
- The active-cohort gate now uses cross-system evidence after the GHL candidate set is assembled. A no-booking contact supported only by a GHL tag or stage becomes `GHL_ONLY_PT_RECORD_REVIEW`, not `NO_FUTURE_BOOKINGS`.
- The reconciliation engine now reserves every exact canonical appointment before using surplus appointments for same-week or adjacent-week make-ups. This fixes the failure mode where a booked later session could be consumed by an earlier gap and then falsely reported missing.
- Expected occurrences inside a recorded GHL hold start/end window are excluded. A shared revenue-controller state of `APPROVED_PAUSE` also suppresses booking gaps and top-ups as `PT_HOLD_ACTIVE`.
- All 91 combined PT Booking Shadow and revenue-controller tests pass.
- Production deployment `854f7dcf-0a46-4734-b28a-70b357809a37` succeeded.
- Private no-email production run `a18adb5d-d99b-4f4a-84fa-8439650af81f` completed for 102 contacts with no source error.
- The run contains four `GHL_ONLY_PT_RECORD_REVIEW` cases: Alyssa Crighton, Holly Young, Lucy Thomas and Sumie Sagane. These require lifecycle/status confirmation, not automatic rebooking.
- `NO_FUTURE_BOOKINGS` reduced from 11 to five. Four approved pauses remain safely classified as `PT_HOLD_ACTIVE`.
- Three `GAP_INSIDE_SERIES` cases remain: Anna Scripps, Deb Farrell and Kanika Mehta. Bree Coleman's 10 August occurrence was found confirmed in Megan's calendar, and Janice Ting's Friday series boundary was repaired.
- Deb Farrell's previously false Saturday gaps on 26 September, 3 October and 10 October disappeared. Her remaining forecast contains the missing Wednesday pattern plus the genuine end-of-series tail; the separate prepaid-pack sequence conflict remains fail-closed for Admin review.
