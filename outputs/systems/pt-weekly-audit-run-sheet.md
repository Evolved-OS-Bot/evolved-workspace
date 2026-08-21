# PT Weekly Audit Run Sheet

Use this worksheet for the Monday Active PT review and Friday cash close. Copy it into the weekly audit record and retain only the evidence needed to explain decisions and exceptions.

The governing procedure is `reference/sops/active-client-payment-and-booking-reconciliation.md`.

## Audit Details

| Field | Entry |
|---|---|
| Week beginning | |
| Audit date and time | |
| Auditor | |
| Workbook column and date | |
| Cleared-cash window | |
| Previous audit record | |

## Opening Control Totals

| Control | Value |
|---|---:|
| Active PT rows | |
| Numeric Active PT allocation | |
| PIF Active PT rows | |
| New or changed rows since last audit | |
| Rows without future bookings | |
| Payment-recovery rows | |
| Approved pauses | |
| Future starts | |

## Line-by-Line PT Review

Complete one row for every Active PT client on Monday. Use `Clean` only when identity, payment or approved PIF entitlement, commercial fields, lifecycle state and booking evidence agree.

| Client | GHL email | Payment rail | Latest successful receipt | Subscription and pause state | Sessions per week | Length | Session cost | Weekly debit or PIF | Future booked through | Current trainer | Hold or cancellation evidence | Pack position | Classification | Next action | Owner | Due |
|---|---|---|---|---|---:|---|---:|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | | | | |

## Required Evidence Checks

- Match the exact GHL email first, then a verified phone or recorded legacy-email link.
- Search Stripe and approved PTMinder/EziDebit records before classifying a client as unpaid.
- Check the latest successful receipt, current subscription status, `pause_collection`, invoice state and next debit.
- Apply the one-week-in-advance rule to the scheduled payment being assessed.
- Confirm sessions per week, duration, session cost, weekly PT allocation and payment pathway.
- Read expanded future appointments across all current PT calendars and derive the current trainer from those bookings.
- Discover calendars from the governed 1:1 registry, including retained or active calendars whose displayed name does not contain `PT`.
- Build one contact-level event ledger across every approved PT calendar before identifying a gap. Never treat absence from one trainer calendar as proof that the client is unbooked.
- Match exact contact, start time and duration across all approved PT calendars before checking same-week reschedules or next-week make-ups. Record an alternate trainer/calendar as cover evidence rather than creating a replacement.
- Confirm every PT booking block and top-up is stored as separate appointments with `isRecurring=false`. The default is 13 individual appointments per entitled weekly pattern; an approved different count is still individual.
- Fail the audit if any future PT recurring master or recurring instance remains. Before closing a write, verify exactly one active individual appointment at each authorised target, zero duplicates and the authorised notification setting.
- Check GHL hold, cancellation, conversation and approved service-change evidence.
- For a hold extension, preserve the original request and start dates, then verify the revised end date and pre-return date across GHL, Hold OS and billing.
- Remove sessions inside the approved hold window, but retain the normal 13-week post-return horizon until a formal cancellation form is submitted.
- Retain the Active PT row and contractual weekly rate during the hold. Record the pause, billing restart, return date and booked-through date in Rebook.
- Confirm outstanding medical evidence has an owned task and dual-trainer clients have a named return-check owner.
- Verify the booking controller recognises the client as `pt_hold`.
- For PIF packs, verify the purchase receipt and the `Session X/Y` sequence separately.
- For Fast Track, require the matching $99 Active SGPT row, calculate PT from approved weekly sessions multiplied by the recorded session rate, and count the combined customer receipt once.
- For cancelled, deleted or no-show sessions, determine the action time and whether the 24-hour charge rule applies.

## Exception Register

| Client | Exception type | Evidence checked | Financial value | Required decision or action | Owner | Due date | GHL task ID | Status |
|---|---|---|---:|---|---|---|---|---|
| | | | | | | | | |

Use these standard classifications:

- `Clean`
- `Active - PIA`
- `Active - ARREARS`
- `Approved pause`
- `Approved future start`
- `PIF pack in delivery`
- `Pack renewal due`
- `Payment current, no booking`
- `Booking exists, payment unresolved`
- `Lifecycle exception`

## Friday Cash Bridge

| Bridge item | Amount |
|---|---:|
| Full numeric Active PT allocation | |
| Less approved pauses | |
| Less unresolved arrears | |
| Less future starts not yet due | |
| Confirmed current weekly PT income | |
| Plus or minus named payment-timing items | |
| Cleared PT-attributable cash | |
| Remaining unexplained variance | |

List every timing item by client:

| Client | Amount | Receipt date | Service week funded | Reason for timing difference |
|---|---:|---|---|---|
| | | | | |

Do not include PIF pack sales in recurring weekly PT income. Report those receipts separately:

| Client | Pack receipt | Receipt date | Pack size | Current session position | Renewal action |
|---|---:|---|---:|---|---|
| | | | | | |

## Close Checklist

- [ ] Every Active PT row was reviewed.
- [ ] Every changed row was re-read after writing.
- [ ] No duplicate Active PT email exists.
- [ ] Trainer fields match current future bookings.
- [ ] Every proposed booking gap was checked across all approved PT calendars by stable contact ID.
- [ ] Holds and payment pauses agree.
- [ ] Hold extensions preserve original dates and align GHL, Hold OS, billing, bookings, Active PT, Trainerize and controller state.
- [ ] Conversational cancellation intent has not been treated as formal notice.
- [ ] Every medical-evidence follow-up and dual-trainer return check has an owner and due date.
- [ ] Cancellations use an evidenced final-service boundary.
- [ ] Pack sequences and renewal thresholds are current.
- [ ] Every unresolved exception has a GHL owner and due date.
- [ ] Confirmed current income, scheduled run-rate, PIF sales and actual cash are reported separately.
- [ ] The remaining cash variance is zero or explained by named owned exceptions.

## Audit Sign-Off

| Field | Entry |
|---|---|
| Monday review completed | |
| Friday cash close completed | |
| Exceptions carried forward | |
| Quality-control reviewer | |
| Final status | Clean / Clean with owned exceptions / Re-open required |
