# Plan: Natural Language Appointment Management, Scheduling & Rescheduler
**Created:** 2026-04-27
**Revised:** 2026-08-04
**Status:** Scoped — Not Started

---

## Objective

Build a natural-language appointment operations agent with two permission modes. Member mode handles individual reschedule requests through conversational SMS. Admin Eve mode handles authorised internal instructions to inspect, create, move, transfer and cancel individual appointments, and to detect or safely clean up legacy recurring series in GHL. Both modes identify the intended end state, check policy and availability, confirm material choices, action the change and verify the resulting calendar state.

> **Superseding storage rule — 4 August 2026:** PT service lines are logical weekly patterns made from individual GHL appointments. Every PT create, reschedule, transfer and top-up must store each date separately with `isRecurring=false`. Open-ended and bounded recurring masters are prohibited. The default horizon is 13 individual appointments per entitled weekly pattern.

---

## Problem Being Solved

- Admin manually handles every reschedule request — reads the message, opens GHL, finds the appointment, checks availability, replies, then actions the change
- Requests arrive in natural language ("something came up", "can we swap Thursday?") — GHL keyword detection misses most of them
- No consistency in how reschedule policy is applied — within-24hr exceptions are made informally
- Cross-trainer availability is checked manually across 4 individual calendars
- Trainer departures and recurring-series transfers require several linked actions: compare schedules, resolve conflicts, create replacement bookings, verify the full series, delete superseded bookings and retire empty calendars
- GHL represents recurring appointments differently across endpoints, so an apparently incomplete or duplicated result can be misread without calendar-level verification

---

## Evidence-Led Design Update: Anika and Kanika Case, 21 July 2026

The live Meroe-to-Nora transfer established the minimum safe behaviour for the broader appointment-management agent:

1. The system identified all future Meroe bookings and found that 22 records represented only 15 distinct times because seven entries were duplicates.
2. It inspected Kanika's complete appointment history and recognised two different patterns rather than assuming the bookings were equivalent: Nora used Tuesday 5:15 pm and Wednesday 5:00 pm; Meroe used Tuesday and Thursday 5:00 pm.
3. It translated the requested end state into two 13-week series, producing 26 exact target instances from 4 August to 28 October.
4. It checked every calendar assigned to Nora, not only the 30-minute target calendar, and found two clashes with Anika's 45-minute appointments.
5. It moved and verified Anika's two appointments before creating Kanika's replacement series.
6. It used Nora's live calendar configuration for duration, owner, title, location, confirmation and recurring-series rules.
7. It discovered that GHL initially returns the recurring master records while the calendar-event endpoint expands the 26 instances asynchronously. Verification therefore had to poll the calendar view rather than rely only on the contact appointment feed.
8. It deleted the superseded future records only after all 26 replacements were verified.
9. It confirmed that deleting a calendar removes its completed appointments from the active contact-appointment feed. Historical evidence must therefore be exported or recorded before calendar retirement when retention matters.

This is the reference acceptance case for the Admin Eve mode.

---

## Evidence-Led Design Update: Ann, Janice and Bethany Cases, 23–25 July 2026

Three live appointment-management tasks exposed additional GHL behaviours that the agent must handle:

1. A natural-language bulk move must become an exact proposed schedule before mutation. The Ann Chang request was safely separated into read-only discovery, a concrete day/time proposal and an explicit confirmation before the series was changed.
2. Contact identity cannot be inferred from the appointment title. Bethany Watson's linked appointments were titled `Bethan Watson`; the contact ID, phone and email still resolved to the correct contact.
3. A calendar event can remain live, confirmed and linked to the correct contact while disappearing from the contact-level Appointments tab. Janice Ting's Wednesday series remained visible in Piper's calendar with Janice as attendee, but its rescheduled/deleted parent history prevented the contact feed from listing the series.
4. The calendar view, contact appointment feed and contact activity history can therefore disagree without any duplicate contact or missing live session.
5. Recreating a valid calendar-visible series solely to repair contact-tab visibility can trigger a new batch of confirmations. The correct outcome may be `RETAIN_DISPLAY_INCONSISTENCY`, with no appointment mutation.
6. A former recurring create partially succeeded. Bethany's default Nora series created 11 confirmed weekly appointments rather than the expected 13; this is historical defect evidence only and recurrence must not be used for retry or future PT storage.
7. An empty target time in the calendar view does not prove that GHL will accept it through the calendar's default free-slot rules. Booking horizon, configured availability and validation rules must be distinguished from a genuine appointment conflict.
8. Before creating or retrying a series, the agent must re-read the contact and expanded calendar events. A user may believe an attempt failed when GHL has already created all or part of the requested schedule.
9. “Use the calendar default” is a governed constraint for duration, owner, location, availability and notification behaviour, but it never authorises recurring storage. A custom-time or free-slot-validation override is not equivalent to the default and requires separate authorisation.

These cases become acceptance fixtures alongside the Anika/Kanika trainer-transfer case.

---

## Evidence-Led Design Update: Ankitha Fragmented-Series Case, 28 July 2026

The live Ankitha Hakeem operation established additional requirements for recurring-series recognition and in-place bulk moves:

1. A member's logical weekly service line cannot be identified from exact day and time alone. The requested “Tuesday 5:15 am” line contained future instances at Tuesday 6:00 am, Tuesday 5:30 am, Wednesday 7:30 am and Tuesday 5:15 am because earlier appointments had already been individually rescheduled.
2. The planner must reconstruct the intended service line from contact ID, calendar, trainer, duration, recurrence context, neighbouring instances and the authenticated user's description. It must present any inferred membership in the affected series as part of the exact proposal.
3. A second weekly line can share the same contact, trainer, calendar and duration. Ankitha's Thursday PT appointments were a protected sibling pattern; they had to be snapshotted before mutation and verified unchanged afterward.
4. Display-name spelling is not identity. The internal request used `Anktiha`, while the live contact is `Ankitha Hakeem`; contact ID remained the authoritative identity and no duplicate contact was created.
5. When contact, trainer, calendar, duration and service type remain unchanged, updating the existing appointment instances is safer than creating replacements and deleting originals. The live operation preserved all 13 event IDs and their history.
6. A target can be conflict-free across every trainer calendar and still fail GHL's configured free-slot validation. All 13 Wednesday 5:15 am targets were clear, but each required `ignoreFreeSlotValidation` after Peter approved the exact first date, last date, time, trainer, duration and occurrence count.
7. A batch-notification decision is mandatory. The operation used `toNotify=false` so 13 individual appointment changes did not fire 13 separate automations or confirmations.
8. Verification must cover both changed and protected state. All 13 appointment records and all 13 expanded calendar events were verified at Wednesdays 5:15–5:45 am from 5 August through 28 October, with no gaps or duplicates, while the Thursday series was confirmed identical before and after.

This is the reference acceptance case for fragmented logical-series detection, protected sibling-series handling, in-place instance updates, authorised free-slot overrides and batch notification suppression.

---

## Evidence-Led Design Update: Kat Norman Move-and-Extend Case, 28 July 2026

The live Kat Norman operation established additional requirements for amended scope, independent source appointments and exact-count scheduling:

1. The initial request was translated into an exact proposal to move seven confirmed 30-minute Piper appointments from Tuesdays at 7:00 am to Wednesdays at 7:00 am, beginning in the week of 3 August.
2. The source pattern looked weekly but was not a GHL recurring series. All seven Tuesday appointments were independent events, so the planner could not assume a recurring master existed.
3. Peter's approval message amended the operation by adding 13 sessions after the original seven. The resolved end state therefore became 20 Wednesdays from 5 August through 16 December, while the audit meaning remained seven moved sessions plus 13 added sessions.
4. The expanded horizon exceeded the calendar's normal 90-day booking window. The exact first date, last date, time, trainer, duration and occurrence count were authorised before `ignoreDateRange` and `ignoreFreeSlotValidation` were used.
5. Preflight checked the full 20-week horizon across all active calendars and blocked time. No Piper conflict or other overlapping appointment existed at any target.
6. The first execution guard stopped safely before mutation because it treated the seven known Tuesday source events as unexpected nearby appointments. The corrected model distinguished approved source events from protected appointments, target collisions and genuinely unexpected state.
7. The replacement was originally created with `FREQ=WEEKLY;COUNT=20`; the 4 August account audit identified that storage choice as a defect. The live schedule was corrected to 20 separate appointments, and the permanent rule now requires individual storage for every exact-count request.
8. Only after all 20 Wednesday instances passed verification were the seven Tuesday events deleted. Final verification confirmed 20 unique targets, zero remaining source appointments and no duplicates.
9. Standard GHL automations remained enabled. Notification mode was part of the authorised operation and final audit result.

This remains the reference acceptance case for approval-scope amendment, source-versus-conflict classification, booking-horizon override, exact-count individual creation and replacement-before-removal verification. Its former independent-to-recurring storage choice is explicitly superseded.

---

## Operating Principles

### 1. Plan the end state, not just the command

Natural-language requests such as “move the rest to Nora for 13 weeks in the existing pattern” must be converted into an explicit proposed schedule: contact, trainer, calendar, duration, logical weekly pattern, first date, last date, day and time. The agent asks for clarification only when a genuine scheduling or policy choice remains.

### 2. Read first, mutate second

Every operation begins with a read-only preflight. Resolve the exact contact, calendar, trainer user, appointment IDs, recurrence structure, current status and requested target state before changing GHL.

### 3. Check the trainer, not only the target calendar

Availability must be checked across every active calendar assigned to the trainer and across external or blocked-time sources where the API exposes them. A clear 30-minute PT calendar is not sufficient if the same trainer has a conflicting 45-minute appointment elsewhere.

### 4. Sequence transfers safely

The default transfer order is:

1. Snapshot the source schedule and historical evidence.
2. Calculate the target schedule.
3. Check all target conflicts.
4. Resolve approved conflicts.
5. Create the replacement bookings.
6. Verify every target instance.
7. Delete superseded future bookings.
8. Verify zero remaining future bookings.
9. Delete an empty former-trainer calendar only when explicitly authorised.

Source bookings must never be deleted before replacement bookings have passed verification.

### 5. Detect legacy recurring masters; never create new ones

The contact-appointment endpoint may expose only a legacy recurring master while the calendar-event endpoint expands its instances. The agent must detect both forms so it can audit existing state safely, but every new or corrected PT date is stored as an individual appointment. No PT operation may create an RRULE or recurring master.

### 6. Make every operation idempotent

Before creating an appointment, check for an existing active event with the same contact, calendar, start time and duration. Before retrying after an ambiguous response, re-read GHL. Retries must fill genuine gaps rather than create duplicates.

### 7. Use overrides only after a stronger conflict check

GHL may reject an admin-entered slot even when no live GHL appointment conflicts with it. `ignoreFreeSlotValidation` is permitted only when the exact time has been authorised and the agent has completed a fresh cross-calendar conflict check. The override and reason must be recorded in the audit log.

### 8. Make notification behaviour explicit

Every create, move or cancellation must state whether standard GHL notifications and workflows will run. Batch operations need a notification policy so a member does not receive confusing duplicate messages. The audit record stores the `toNotify` decision.

### 9. Verify outcomes from the correct surface

After mutation, verify calendar owner, contact, start and end time, duration, status, count, missing dates and duplicate dates. Recurring-series verification uses calendar events; single-appointment verification can use the contact appointment feed and the appointment endpoint.

### 10. Preserve evidence before destructive cleanup

Deleting an event or calendar is a separate, explicitly authorised action. Before calendar deletion, record any historical appointments that must remain part of the operational record because GHL may stop returning them in the active contact feed after the calendar disappears.

### 11. Separate role authority

Member mode can move the member's own eligible appointment after confirmation. Admin Eve mode can perform bulk scheduling, trainer transfers, overrides and cleanup only from authenticated internal instructions. Admin Eve is the operational role; Nora or another staff member may be the trainer/calendar owner without becoming the bot's identity.

### 12. Keep an immutable operation ledger

Each operation records the natural-language request, resolved entities, before state, proposed state, user confirmation, API actions, notification setting, verification result, errors, retries and final state. Destructive operations also record what can and cannot be recovered.

### 13. Use a governed live calendar registry

Do not rely on a permanent four-trainer map or person-specific exclusions. Synchronise the active GHL calendars and users into a registry that records trainer status, service eligibility, duration, location and whether the calendar can be offered to members. Former-staff calendars are excluded automatically; deliberate restrictions such as management-only PT are expressed as eligibility rules attached to the user or role.

### 14. Separate PT continuity from the 13-week review cycle

An active PT client's calendar should not expire merely because a 13-week tracking period ends. A rolling controller should inspect the approved weekly pattern and booked-through date, append only genuinely missing future appointments, and route conflicts to Admin Eve rather than deleting and rebuilding a series.

Cancellation is the terminal booking-removal event. Once the final-service date has been verified, the controller stops future top-ups and removes only appointments after that date; holds pause top-ups without deleting existing bookings, and trainer transfers follow the verified replacement-before-removal sequence above.

### 15. Reconcile three GHL evidence surfaces

When auditing or correcting legacy recurring state, compare expanded calendar events, the contact-level appointment feed and contact activity history. No single surface is authoritative for every state. A disagreement is classified and explained before any repair is proposed.

### 16. Model recurring-series health explicitly

The verifier must distinguish `HEALTHY`, `EXPANSION_PENDING`, `PARTIAL_SERIES`, `CALENDAR_ONLY_LINKED_SERIES`, `CONTACT_FEED_ONLY`, `ORPHANED_PARENT` and `DUPLICATE_SERIES`. A calendar-only linked series is not automatically missing and must not be recreated without a separate repair decision.

### 17. Treat contact identity separately from display text

Resolve and deduplicate contacts by GHL contact ID, with normalised email and phone as supporting evidence. Names and appointment titles are display fields only; spelling differences must be reported but must not cause a second contact or appointment series to be created.

### 18. Treat partial individual-batch success as a first-class result

After every individual batch, compare requested, accepted and verified appointment counts and list each missing date. Determine whether the cause is a real conflict, booking horizon, configured availability or validation failure before retrying. Retries create only verified gaps and must never create a recurring master.

### 19. Prefer member-safe non-action over cosmetic repair

When live appointments are correct but a GHL display or index is inconsistent, calculate the member impact of repair. If recreating the series would send confirmations, disturb valid bookings or lose history, default to retaining the live series and recording the inconsistency unless Admin Eve explicitly authorises repair and notification handling.

### 20. Scope confirmation to the exact proposed mutation

Confirmation records the contact, affected appointment IDs or recurrence, source and target day/time, first and last dates, occurrence count, calendar, trainer and notification mode. If any material field changes after confirmation, the proposal must be confirmed again.

### 21. Model logical service lines across fragmented instances

A weekly service line may contain one-off reschedules on different days or at different times. Grouping must use contact ID, calendar, trainer, duration, recurrence lineage where available, neighbouring cadence and the authenticated user's stated intent. The agent must show the inferred affected instances before actioning and must not silently exclude an outlier that belongs to the line.

### 22. Protect sibling recurring patterns

When a contact has multiple recurring lines on the same calendar, the planner must identify both the mutation set and the protected set. Snapshot the protected sibling instances before action, exclude them from mutation, and verify that their IDs, times, statuses, trainer and calendar remain unchanged afterward.

### 23. Prefer in-place updates when service identity is unchanged

If contact, trainer, calendar, duration and service type remain the same, update the existing individual appointments and preserve their event IDs. Use replacement creation and source deletion only when the target requires a new calendar, trainer or another field that cannot be safely changed in place.

### 24. Consolidate member communication for bulk changes

Bulk operations must never default to one notification per changed instance. The proposal must specify whether automations run, whether all instance notifications are suppressed and whether one consolidated confirmation will be sent separately. Record the final `toNotify` decision and verify that the chosen communication path behaved as intended.

### 25. Classify every observed appointment by operation role

Before mutation, label each relevant event as an approved source, intended target, protected sibling, genuine conflict or unexpected state. Approved source events must not block their own replacement, while any unclassified nearby event fails closed until its role is resolved.

### 26. Treat follow-up instructions as scope amendments

If an approval message adds dates, occurrences, trainers, notification behaviour or another material field, rebuild the exact end state and record the amended proposal. The explicit follow-up may authorise the new scope, but the ledger must retain both the original proposal and the final authorised mutation.

### 27. Store exact-count requests as individual appointments

When the user requests a fixed number of sessions, create exactly that many separate appointments with `isRecurring=false`. The default is 13. Never use `FREQ=WEEKLY`, `COUNT=N`, an open-ended recurrence or any other RRULE for PT storage.

### 28. Preserve business meaning in the individual operation ledger

The operation ledger must retain the business interpretation, such as seven moved sessions plus 13 added sessions, and map every authorised target to its individual appointment ID so later reconciliation can explain which source appointments were moved or replaced.

---

## Appointment Types in Scope

| Type | Calendar Structure | Cross-Trainer Rule | Policy |
|---|---|---|---|
| 1:1 PT | Active individual trainer calendars, grouped by duration (30/45/60min) | Any trainer marked PT-eligible in the live registry | >24hrs from session = reschedule allowed. <24hrs = forfeited, bot declines |
| Onboarding | Active individual trainer calendars, grouped by duration | Any trainer marked onboarding-eligible | >24hrs = standard reschedule. <24hrs = 1 exception allowed per appointment, tracked. Second request within 24hrs = declined |
| Strength Assessment | Round robin calendar | Any available slot | >24hrs = reschedule allowed. <24hrs = declined |

---

## Architecture

### Service
- **Language:** Python
- **Framework:** Flask
- **Deployment:** Railway — new service, separate from Stripe handler and triage bot
- **Process:** Always-on web service

### State Management
- SQLite — persistent conversation state per contact across turns
- Three core tables: `reschedule_sessions` (active member conversations), `onboarding_reschedule_history` (tracks within-24hr exception usage) and `appointment_operations` (immutable admin/member operation ledger)

### Inbound Detection
- GHL fires inbound message webhook on every incoming SMS
- Bot applies two-stage self-filter before engaging (see Detection section)
- No GHL workflow changes required

### Outbound Messaging
- GHL Conversations API — `POST /conversations/messages`
- SMS only (primary channel for all three appointment types)

### File Structure

```
reschedule_bot/
  app.py                — Flask app, inbound webhook endpoint
  conversation.py       — Claude conversation management, intent detection, response generation
  state_store.py        — SQLite CRUD for reschedule_sessions and onboarding_reschedule_history
  ghl_client.py         — GHL API wrapper (appointments, calendars, free-slots, send message)
  calendar_registry.py  — synchronised active users/calendars plus service-eligibility rules
  calendar_scanner.py   — availability scanning logic, trainer preference and eligibility filtering
  appointment_planner.py — converts the requested end state into exact individual appointment actions and logical weekly patterns
  operation_executor.py — ordered create, move, delete and calendar-retirement actions
  verification.py       — polling, instance expansion, gap/duplicate and final-state checks
  audit_log.py          — immutable before/action/after operation ledger
  policy.py             — 24hr rule, onboarding exception, type-specific rules
  config.py             — env vars, calendar IDs, trainer→calendar mapping
  requirements.txt
  railway.toml
```

---

## Detection — Two-Stage Self-Filter

The bot receives every inbound SMS. Both stages must pass before the bot engages. If either fails, the message is ignored and GHL handles it normally.

```
Inbound SMS arrives at /reschedule/inbound
      │
      ▼
Stage 1: Does this contact have an upcoming appointment in the next 30 days?
      │  GET /contacts/{contactId}/appointments
      └─ No upcoming appointments → ignore (return 200, do nothing)
      │
      ▼
Stage 2: Does Claude classify this message as a reschedule/move intent?
      │  Prompt: "Does this message indicate the person wants to reschedule,
      │  move, or change an appointment time? Reply YES or NO only."
      └─ NO → ignore
      │
      ▼
Engage rescheduler — check if contact already has an active session in SQLite
      ├─ Active session exists → continue that conversation
      └─ No active session → start new reschedule conversation
```

**Why inbound webhook over GHL workflow detection:**
GHL keyword matching misses natural language ("something came up", "can we swap?", "I won't be able to make it"). Claude detects intent accurately regardless of phrasing. The two-stage filter keeps noise low — only contacts with upcoming appointments are evaluated at all.

---

## Conversation State Machine

```
IDLE
  → IDENTIFYING        (multiple appointments found — asking which one)
  → POLICY_DECLINED    (terminal — within policy limits, bot sends decline message)
  → SCANNING           (internal — finding available slots)
  → PRESENTING         (options sent to contact, waiting for selection)
  → CONFIRMING         (selected slot confirmed back to contact, waiting for YES/NO)
  → ACTIONING          (internal — calling GHL reschedule API)
  → COMPLETE           (terminal — confirmation sent, session archived)
  → FAILED             (terminal — GHL API error, admin alert sent)
```

---

## Full Conversation Flow

```
Contact sends reschedule message
      │
      ▼
Two-stage filter passes
      │
      ▼
Fetch contact's upcoming appointments (GHL API)
      ├─ 1 appointment → "Is this the one you'd like to move?
      │                   [Type] with [Trainer] on [Day Date] at [Time].
      │                   Reply YES or NO."
      │
      └─ Multiple appointments → "Which session would you like to reschedule?
                                  1. [Type] — [Day Date] at [Time] with [Trainer]
                                  2. [Type] — [Day Date] at [Time] with [Trainer]
                                  Reply with the number."
      │
      ▼
Appointment confirmed by contact
      │
      ▼
Policy check
      ├─ Appointment type: PT or SA
      │     Is appointment > 24hrs away?
      │       YES → continue
      │       NO  → "Unfortunately we're unable to reschedule PT sessions
      │              within 24 hours. Per your agreement the session is
      │              forfeited. Call us on 0483 968 880 if you need to discuss."
      │              → POLICY_DECLINED
      │
      └─ Appointment type: Onboarding
            Is appointment > 24hrs away?
              YES → continue
              NO  → Check onboarding_reschedule_history: within-24hr exception used?
                      NOT USED → allow (record exception), continue
                      ALREADY USED → "We were able to accommodate one reschedule
                                      for your Onboarding session but are unable
                                      to reschedule again within 24 hours.
                                      Please call us on 0483 968 880."
                                      → POLICY_DECLINED
      │
      ▼
Scan availability (calendar_scanner.py)
      │
      ├─ 1:1 PT / Onboarding:
      │     1. Find assigned trainer's calendar (match duration group)
      │     2. Check free slots — next 7 days from today
      │     3. If < 3 slots found → scan other trainer calendars (same duration group)
      │        PT: exclude trainers not marked PT-eligible in the live registry
      │        Onboarding: all trainers eligible
      │     4. Collect up to 3 slots total (assigned trainer preferred)
      │
      └─ Strength Assessment:
            Check SA round robin calendar free slots — next 7 days
            Collect up to 3 slots
      │
      ▼
Slots found → present options
      "Here are the next available times:

       1. [Day Date] at [Time] — [Trainer]
       2. [Day Date] at [Time] — [Trainer]
       3. [Day Date] at [Time] — [Trainer B] (alternative trainer)

       Reply 1, 2 or 3, or let me know if none of these work."

      No slots found (7-day window exhausted) →
      "We don't have any availability in the next 7 days that works.
       Please call us on 0483 968 880 and we'll sort something out."
      → FAILED (soft — no API error, just no availability)
      │
      ▼
Contact selects option (1/2/3 or natural language — Claude interprets)
      │
      ▼
Confirm selection
      "Confirm: move your [Type] to [Day Date] at [Time] with [Trainer]?
       Reply YES to confirm or NO to see the options again."
      │
      ▼
Contact confirms YES
      │
      ▼
GHL API: PUT /calendars/events/appointments/{appointmentId}
      ├─ Success → "Done — you're booked in for [Day Date] at [Time]
      │             with [Trainer]. See you then!"
      │             → COMPLETE
      │
      └─ API Error → "Something went wrong on our end — your session hasn't
                      been moved. Please call us on 0483 968 880 and we'll
                      fix it straight away."
                      Admin alert logged → FAILED
```

---

## Calendar Scanning Logic

### Trainer → Calendar Registry

Synchronised from live GHL and enriched with explicit service-eligibility rules. Calendar IDs are still stable identifiers, but the bot must not assume that every configured trainer or calendar remains active.

```python
CALENDAR_REGISTRY = {
    "pt": {
        30: {"user_id_trainer_a": {"calendar_id": "cal_id_a_30", "active": True, "eligible": True}},
        45: {"user_id_trainer_a": {"calendar_id": "cal_id_a_45", "active": True, "eligible": True}},
        60: {"user_id_trainer_a": {"calendar_id": "cal_id_a_60", "active": True, "eligible": True}},
    },
    "onboarding": {
        30: {...},
        45: {...},
        60: {...},
    }
}

PT_EXCLUDED_TRAINER_USER_IDS = ["user_id_management_only"]

SA_CALENDAR_ID = "cal_id_sa_round_robin"
```

### Slot Scanning Algorithm

```
1. Identify appointment type and duration from GHL appointment record
2. Get calendar group for that type + duration
3. Find assigned trainer's calendar via contact.assigned_user_id
4. Fetch free slots from assigned trainer's calendar (startDate=today, endDate=today+7days, timezone=Australia/Brisbane)
5. If assigned slots >= 3 → done
6. Fetch free slots from remaining eligible calendars in the group
7. Merge, deduplicate by time, sort chronologically
8. Return top 3 across all trainers (assigned trainer slots listed first)
```

### Slot Presentation Format

All times displayed in AEST (Australia/Brisbane). Format: `Tuesday 29 Apr at 9:00am`

If a slot is with a different trainer than assigned: append `— [Trainer Name] (alternative trainer)`

---

## Policy Module

```python
def check_policy(appointment, appointment_type, contact_id):
    """
    Returns: ("allowed", None) or ("declined", reason_message)
    """
    hours_until = (appointment.start_time - now()).total_seconds() / 3600

    if appointment_type in ("PT", "SA"):
        if hours_until < 24:
            return "declined", POLICY_DECLINE_PT_24HR

    if appointment_type == "Onboarding":
        if hours_until < 24:
            exception_used = check_onboarding_exception(contact_id, appointment.id)
            if exception_used:
                return "declined", POLICY_DECLINE_ONBOARDING_REPEAT
            else:
                record_onboarding_exception(contact_id, appointment.id)
                return "allowed", None

    return "allowed", None
```

---

## SQLite Schema

```sql
-- Active and completed reschedule conversations
CREATE TABLE reschedule_sessions (
    contact_id              TEXT PRIMARY KEY,
    conversation_id         TEXT,
    stage                   TEXT,
    appointment_id          TEXT,
    appointment_type        TEXT,
    appointment_start       TEXT,
    appointment_duration    INTEGER,
    assigned_trainer_user_id TEXT,
    options_json            TEXT,
    selected_slot_start     TEXT,
    selected_calendar_id    TEXT,
    selected_trainer_name   TEXT,
    created_at              TEXT,
    updated_at              TEXT
);

-- Tracks within-24hr onboarding reschedule exceptions (1 per appointment)
CREATE TABLE onboarding_reschedule_history (
    contact_id      TEXT,
    appointment_id  TEXT,
    rescheduled_at  TEXT,
    PRIMARY KEY (contact_id, appointment_id)
);

-- Immutable record of member and Admin Eve appointment operations
CREATE TABLE appointment_operations (
    operation_id         TEXT PRIMARY KEY,
    mode                 TEXT,       -- member or admin_eve
    requested_by         TEXT,
    contact_id           TEXT,
    natural_language_request TEXT,
    operation_type       TEXT,       -- create, move, transfer, cancel, delete_calendar
    before_state_json    TEXT,
    proposed_state_json  TEXT,
    confirmation_json    TEXT,
    actions_json         TEXT,
    notification_mode    TEXT,
    verification_json    TEXT,
    status               TEXT,       -- planned, actioning, verified, failed, rolled_back
    created_at           TEXT,
    completed_at         TEXT
);
```

---

## GHL API Calls

| Action | Method | Endpoint |
|---|---|---|
| Get contact's appointments | GET | `/contacts/{contactId}/appointments` |
| Get calendar free slots | GET | `/calendars/{calendarId}/free-slots?startDate=&endDate=&timezone=` |
| Get expanded calendar events | GET | `/calendars/events?locationId=&calendarId=&startTime=&endTime=` |
| Create one individual appointment; repeat for each exact PT target | POST | `/calendars/events/appointments` |
| Reschedule appointment | PUT | `/calendars/events/appointments/{appointmentId}` |
| Delete event or recurring instance | DELETE | `/calendars/events/{eventId}` |
| Delete empty calendar | DELETE | `/calendars/{calendarId}` |
| Send SMS reply | POST | `/conversations/messages` |
| Get contact (assigned user) | GET | `/contacts/{contactId}` |

---

## Environment Variables

```
GHL_API_KEY
GHL_LOCATION_ID
ANTHROPIC_API_KEY
TIMEZONE=Australia/Brisbane
CALENDAR_REGISTRY_REFRESH_MINUTES=15
PT_EXCLUDED_TRAINER_USER_IDS=user_id_1
SA_CALENDAR_ID=cal_id_sa
SUPPORT_PHONE=0483968880
```

---

## SMS Copy

### Appointment identification — single appointment
```
Hi [Name], I can see you have a [Type] with [Trainer] on [Day Date] at [Time].
Is this the session you'd like to reschedule? Reply YES or NO.
```

### Appointment identification — multiple appointments
```
Hi [Name], I can see you have a few upcoming sessions. Which one would you like to reschedule?

1. [Type] — [Day Date] at [Time] with [Trainer]
2. [Type] — [Day Date] at [Time] with [Trainer]

Reply with the number.
```

### Presenting options
```
Here are the next available times:

1. [Day] [Date] at [Time] — [Trainer]
2. [Day] [Date] at [Time] — [Trainer]
3. [Day] [Date] at [Time] — [Trainer B] (alternative trainer)

Reply 1, 2 or 3, or let me know if none of these work.
```

### Confirming selection
```
Got it — confirm you'd like to move to [Day Date] at [Time] with [Trainer]?
Reply YES to confirm or NO to see the options again.
```

### Success
```
Done — you're booked in for [Day Date] at [Time] with [Trainer]. See you then!
```

### Policy decline — PT/SA within 24hrs
```
Hi [Name], unfortunately we're unable to reschedule sessions within 24 hours of the appointment. Please call us on 0483 968 880 if you need to discuss.
```

### Policy decline — Onboarding, exception already used
```
Hi [Name], we were able to accommodate one short-notice reschedule for your Onboarding session but are unable to reschedule again within 24 hours. Please call us on 0483 968 880 and we'll sort something out.
```

### No availability
```
Hi [Name], we don't have any availability in the next 7 days that works for your session. Please call us on 0483 968 880 and we'll find something that suits.
```

### GHL error
```
Hi [Name], something went wrong on our end and your session hasn't been moved. Please call us on 0483 968 880 and we'll fix it straight away — sorry for the hassle.
```

---

## Build Order

| Step | Task | Status |
|---|---|---|
| 1 | Build the live calendar registry: synchronise active calendars/users and add explicit service-eligibility rules | ⬜ To Do |
| 2 | Railway service skeleton — Flask app, health check, `requirements.txt`, `railway.toml` | ⬜ To Do |
| 3 | Build `state_store.py` — SQLite init, CRUD for both tables | ⬜ To Do |
| 4 | Build `ghl_client.py` — appointments, free-slots, reschedule, send message, get contact | ⬜ To Do |
| 5 | Build `policy.py` — 24hr check, onboarding exception logic | ⬜ To Do |
| 6 | Build `calendar_scanner.py` — slot fetching, trainer preference ordering, Megan exclusion, AEST formatting | ⬜ To Do |
| 7 | Build `conversation.py` — Claude intent detection, response generation, state transitions | ⬜ To Do |
| 8 | Build `/reschedule/inbound` endpoint in `app.py` — two-stage filter, session routing | ⬜ To Do |
| 9 | Register inbound message webhook in GHL Settings → Integrations → Webhooks | ⬜ To Do |
| 10 | Test: single appointment identification | ⬜ To Do |
| 11 | Test: multiple appointment identification | ⬜ To Do |
| 12 | Test: PT within 24hrs — confirm decline fires | ⬜ To Do |
| 13 | Test: Onboarding within 24hrs — confirm first exception allowed, second declined | ⬜ To Do |
| 14 | Test: cross-trainer scan fires when assigned trainer has no availability | ⬜ To Do |
| 15 | Test: PT cross-trainer scan excludes inactive and non-eligible trainers | ⬜ To Do |
| 16 | Test: GHL reschedule API — confirm appointment updates correctly in GHL | ⬜ To Do |
| 17 | Build `appointment_planner.py` — exact end-state calculation for single, recurring and trainer-transfer requests | ⬜ To Do |
| 18 | Build `operation_executor.py`, `verification.py` and immutable `appointment_operations` audit log | ⬜ To Do |
| 19 | Test: conflict detection scans every calendar assigned to the trainer, not only the target calendar | ⬜ To Do |
| 20 | Test: two weekly patterns create 26 individual appointments with `isRecurring=false`, no gaps and no duplicates | ⬜ To Do |
| 21 | Test: a partially completed individual batch is re-read before retry and creates only verified missing dates | ⬜ To Do |
| 22 | Test: transfer sequence creates and verifies replacements before deleting source appointments | ⬜ To Do |
| 23 | Test: slot-validation override is blocked without exact authorisation and a fresh cross-calendar check | ⬜ To Do |
| 24 | Test: notification-on and notification-off batch modes behave as documented | ⬜ To Do |
| 25 | Test: calendar deletion requires zero future events and records historical evidence before deletion | ⬜ To Do |
| 26 | Run the Anika/Kanika case as an end-to-end acceptance test in a sandbox or test calendar | ⬜ To Do |
| 27 | Monitor first 10 live reschedules and first 5 Admin Eve operations; tune intent, verification and escalation rules | ⬜ To Do |
| 28 | Test: appointment title spelling differs from the linked contact, but no duplicate contact or series is created | ⬜ To Do |
| 29 | Test: linked recurring instances remain in calendar events but are absent from the contact appointment feed after parent reschedule/deletion | ⬜ To Do |
| 30 | Test: valid calendar-only series is classified and retained when repair would trigger fresh confirmations | ⬜ To Do |
| 31 | Test: default 13-occurrence request materialises only 11 because of booking horizon; verifier reports the two exact missing dates | ⬜ To Do |
| 32 | Test: retry after partial success creates only verified missing occurrences and never duplicates the existing 11 | ⬜ To Do |
| 33 | Test: “calendar default” blocks custom-time and free-slot-validation overrides without separate authorisation | ⬜ To Do |
| 34 | Test: changing any material field after Admin confirmation invalidates the confirmation and requires a new approval | ⬜ To Do |
| 35 | Test: reconstruct Ankitha's logical Tuesday service line when its 13 instances include Tuesday 6:00 am, Tuesday 5:30 am, Wednesday 7:30 am and Tuesday 5:15 am appointments | ⬜ To Do |
| 36 | Test: isolate the fragmented Tuesday line while snapshotting, excluding and preserving the sibling Thursday line on the same contact, trainer, calendar and duration | ⬜ To Do |
| 37 | Test: same-service bulk move updates all 13 existing instances in place and preserves every event ID | ⬜ To Do |
| 38 | Test: 13 conflict-free exact targets rejected by configured free-slot validation are overridden only after exact approval and a fresh all-calendar conflict check | ⬜ To Do |
| 39 | Test: bulk move with `toNotify=false` changes all instances without firing one automation or confirmation per appointment | ⬜ To Do |
| 40 | Run the Ankitha fragmented-series case end to end: verify 13 individual records, 13 expanded calendar events, zero gaps or duplicates and an unchanged protected Thursday series | ⬜ To Do |
| 41 | Test: a follow-up approval expands Kat's proposal from seven moved sessions to a 20-session end state and records both the original proposal and amended authorised scope | ⬜ To Do |
| 42 | Test: seven independent Tuesday source appointments are classified as approved sources rather than unexpected nearby conflicts | ⬜ To Do |
| 43 | Test: a 20-week request beyond the 90-day calendar horizon requires exact approval before date-range and free-slot overrides are enabled | ⬜ To Do |
| 44 | Test: exactly 20 individual Wednesday appointments with `isRecurring=false` are verified before any of the seven source appointments are removed | ⬜ To Do |
| 45 | Run the Kat move-and-extend case end to end: verify 20 Wednesdays from 5 August through 16 December, zero remaining Tuesdays, no duplicates and standard notifications enabled | ⬜ To Do |

---

## Dependencies

- GHL API Private Integration Token — already in `scripts/.env`
- Anthropic API key — already used by triage bot
- Railway account — already active
- All calendar IDs and trainer GHL user IDs (Step 1 — required before build starts)

---

## Notes

- **Inbound webhook conflict with SA Pre-Qual agent** — when the pre-qual agent is built, both services will receive every inbound SMS. Each service must check its own SQLite state before engaging. A contact in an active pre-qual session should not trigger the rescheduler, and vice versa. Long term, a single conversation router service handles this cleanly — but for now, each service's two-stage filter (appointment check + intent check) naturally prevents overlap: a contact mid-pre-qual has no reschedule intent, and a contact requesting a reschedule is not mid-pre-qual.
- **7-day availability window** — if no slots found, bot hands off to phone rather than expanding the window. Keeps conversations short and avoids presenting times too far out.
- **Claude model** — `claude-haiku-4-5` for intent detection (simple yes/no classification, low cost). `claude-sonnet-4-6` for response generation (natural language, policy-aware). Two separate calls per turn.
- **Round robin SA rescheduling** — GHL's round robin assignment logic does not apply on reschedule. The bot passes the specific slot and calendar ID to the PUT endpoint directly, bypassing round robin. Trainer shown to client is whoever owns that slot.
- **Trainer eligibility** — controlled through the live registry rather than a permanent named-person rule. If a management trainer should not receive transferred PT sessions, mark that user non-eligible and verify the exclusion in tests.
- **Contact's assigned user** — used only to determine first-preference trainer. If the assigned user has no matching calendar in the config (e.g. they don't take that session type), the bot skips to alternative trainers.
- **No GHL workflow changes required** — the entire system runs off the inbound message webhook. Existing GHL workflows are untouched.
