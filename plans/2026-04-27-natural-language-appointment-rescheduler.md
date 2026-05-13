# Plan: Natural Language Appointment Rescheduler
**Created:** 2026-04-27
**Status:** Scoped — Not Started

---

## Objective

Build a Claude-powered conversational SMS bot that handles appointment reschedule requests in natural language. When a contact sends any message indicating they want to move, change, or reschedule an appointment, the bot identifies the appointment, checks policy, scans trainer availability (assigned trainer first, alternatives if needed), presents options, confirms the selection, and actions the change in GHL — with zero admin involvement.

---

## Problem Being Solved

- Admin manually handles every reschedule request — reads the message, opens GHL, finds the appointment, checks availability, replies, then actions the change
- Requests arrive in natural language ("something came up", "can we swap Thursday?") — GHL keyword detection misses most of them
- No consistency in how reschedule policy is applied — within-24hr exceptions are made informally
- Cross-trainer availability is checked manually across 4 individual calendars

---

## Appointment Types in Scope

| Type | Calendar Structure | Cross-Trainer Rule | Policy |
|---|---|---|---|
| 1:1 PT | 4 individual trainer calendars, grouped by duration (30/45/60min) | Any trainer except Megan | >24hrs from session = reschedule allowed. <24hrs = forfeited, bot declines |
| Onboarding | 4 individual trainer calendars, grouped by duration | Any trainer | >24hrs = standard reschedule. <24hrs = 1 exception allowed per appointment, tracked. Second request within 24hrs = declined |
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
- Two tables: `reschedule_sessions` (active conversations) and `onboarding_reschedule_history` (tracks within-24hr exception usage)

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
  calendar_scanner.py   — availability scanning logic, trainer preference, Megan exclusion
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
      │        PT: exclude Megan's calendar IDs
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

### Trainer → Calendar Mapping

Stored in `config.py` (populated from env vars). Maps GHL user IDs to their calendar IDs per duration group:

```python
TRAINER_CALENDAR_MAP = {
    "pt": {
        30: {"user_id_trainer_a": "cal_id_a_30", "user_id_trainer_b": "cal_id_b_30", ...},
        45: {"user_id_trainer_a": "cal_id_a_45", ...},
        60: {"user_id_trainer_a": "cal_id_a_60", ...},
    },
    "onboarding": {
        30: {...},
        45: {...},
        60: {...},
    }
}

MEGAN_CALENDAR_IDS = ["cal_id_megan_30", "cal_id_megan_45", "cal_id_megan_60"]

SA_CALENDAR_ID = "cal_id_sa_round_robin"
```

### Slot Scanning Algorithm

```
1. Identify appointment type and duration from GHL appointment record
2. Get calendar group for that type + duration
3. Find assigned trainer's calendar via contact.assigned_user_id
4. Fetch free slots from assigned trainer's calendar (startDate=today, endDate=today+7days, timezone=Australia/Brisbane)
5. If assigned slots >= 3 → done
6. Fetch free slots from remaining calendars in group (exclude Megan for PT)
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
```

---

## GHL API Calls

| Action | Method | Endpoint |
|---|---|---|
| Get contact's appointments | GET | `/contacts/{contactId}/appointments` |
| Get calendar free slots | GET | `/calendars/{calendarId}/free-slots?startDate=&endDate=&timezone=` |
| Reschedule appointment | PUT | `/calendars/events/appointments/{appointmentId}` |
| Send SMS reply | POST | `/conversations/messages` |
| Get contact (assigned user) | GET | `/contacts/{contactId}` |

---

## Environment Variables

```
GHL_API_KEY
GHL_LOCATION_ID
ANTHROPIC_API_KEY
TIMEZONE=Australia/Brisbane
MEGAN_CALENDAR_IDS=cal_id_1,cal_id_2,cal_id_3
PT_30_CALENDARS=cal_id_a,cal_id_b,cal_id_c,cal_id_d
PT_45_CALENDARS=cal_id_a,cal_id_b,cal_id_c,cal_id_d
PT_60_CALENDARS=cal_id_a,cal_id_b,cal_id_c,cal_id_d
ONBOARDING_30_CALENDARS=...
ONBOARDING_45_CALENDARS=...
ONBOARDING_60_CALENDARS=...
SA_CALENDAR_ID=cal_id_sa
TRAINER_USER_CALENDAR_MAP=user_id_1:cal_30_1:cal_45_1:cal_60_1,...
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
| 1 | Collect all calendar IDs and trainer user IDs from GHL — populate config | ⬜ To Do |
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
| 15 | Test: PT cross-trainer scan excludes Megan's calendars | ⬜ To Do |
| 16 | Test: GHL reschedule API — confirm appointment updates correctly in GHL | ⬜ To Do |
| 17 | Monitor first 10 live reschedules — tune intent detection prompt if needed | ⬜ To Do |

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
- **Megan's calendar exclusion** — enforced by filtering `MEGAN_CALENDAR_IDS` from the PT cross-trainer scan. Megan's calendars are never presented as an option for PT reschedules regardless of availability.
- **Contact's assigned user** — used only to determine first-preference trainer. If the assigned user has no matching calendar in the config (e.g. they don't take that session type), the bot skips to alternative trainers.
- **No GHL workflow changes required** — the entire system runs off the inbound message webhook. Existing GHL workflows are untouched.
