#!/usr/bin/env python3
"""
pt_utilisation.py
Pull GHL appointments for a date range and display PT utilisation:
client, date/time, duration, trainer, calendar.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
BASE_URL    = "https://services.leadconnectorhq.com"
HEADERS     = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Accept":        "application/json",
}
TZ = ZoneInfo("Australia/Brisbane")  # AEST, no DST

# ── Date range ─────────────────────────────────────────────────────────────────
START = datetime(2026, 6, 29, 0, 0, 0, tzinfo=TZ)
END   = datetime(2026, 7,  4, 23, 59, 59, tzinfo=TZ)

start_ms = int(START.timestamp() * 1000)
end_ms   = int(END.timestamp()   * 1000)


def get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
    if not r.ok:
        print(f"  WARN {r.status_code} {path}: {r.text[:300]}", file=sys.stderr)
        return None
    return r.json()


def fetch_calendars():
    data = get("/calendars/", params={"locationId": LOCATION_ID})
    return data.get("calendars", []) if data else []


def fetch_events(calendar_id):
    """Fetch all events for a calendar in the date window."""
    events = []
    params = {
        "locationId":  LOCATION_ID,
        "calendarId":  calendar_id,
        "startTime":   start_ms,
        "endTime":     end_ms,
    }
    data = get("/calendars/events", params=params)
    if not data:
        return []
    events.extend(data.get("events", []))
    # Paginate if needed
    meta = data.get("meta", {})
    total = meta.get("total", len(events))
    while len(events) < total:
        params["skip"] = len(events)
        data = get("/calendars/events", params=params)
        if not data:
            break
        chunk = data.get("events", [])
        if not chunk:
            break
        events.extend(chunk)
    return events


def fetch_contact(contact_id):
    data = get(f"/contacts/{contact_id}")
    if not data:
        return None
    return data.get("contact", data)


def fetch_user(user_id):
    data = get(f"/users/{user_id}")
    if not data:
        return None
    return data.get("user", data)


def parse_dt(val):
    """Accept epoch ms (int) or ISO string and return a timezone-aware datetime."""
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val / 1000, tz=timezone.utc)
    s = str(val)
    # Try fromisoformat first (handles +HH:MM offsets, Python 3.7+)
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    # Fallback: strip trailing Z
    s = s.rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {val!r}")


def fmt_time(val):
    dt = parse_dt(val).astimezone(TZ)
    return dt.strftime("%a %-d %b  %I:%M %p")


def fmt_duration(start_val, end_val):
    start_dt = parse_dt(start_val)
    end_dt   = parse_dt(end_val)
    mins = int((end_dt - start_dt).total_seconds() // 60)
    if mins >= 60:
        h, m = divmod(mins, 60)
        return f"{h}h {m}m" if m else f"{h}h"
    return f"{mins}m"


def sort_key(val):
    return parse_dt(val).timestamp()


def main():
    print(f"\nFetching appointments {START.strftime('%-d %b')} – {END.strftime('%-d %b %Y')} (AEST)\n")

    calendars = fetch_calendars()
    if not calendars:
        print("No calendars found.")
        return

    # Cache users + contacts to avoid repeat API calls
    user_cache    = {}
    contact_cache = {}

    all_appts  = []
    seen_ids   = set()
    seen_slots = set()  # fallback dedup: (contact_id, start_time)

    for cal in calendars:
        cal_id   = cal.get("id", "")
        cal_name = cal.get("name", "Unknown calendar")
        events   = fetch_events(cal_id)
        for e in events:
            # Deduplicate by event ID
            event_id = e.get("id") or e.get("_id")
            if event_id and event_id in seen_ids:
                continue
            if event_id:
                seen_ids.add(event_id)

            # Deduplicate by contact + start time (catches duplicate GHL records with distinct IDs)
            contact_id_raw = e.get("contactId")
            start_raw      = e.get("startTime") or e.get("start_time")
            slot_key = (contact_id_raw, str(start_raw))
            if slot_key in seen_slots:
                continue
            seen_slots.add(slot_key)

            # Skip cancelled/no-show
            status = (e.get("appointmentStatus") or e.get("status") or "").lower()
            if status in ("cancelled", "canceled", "no_show", "noshow"):
                continue

            start = e.get("startTime") or e.get("start_time")
            end_t = e.get("endTime")   or e.get("end_time")

            # Resolve trainer (assignedUserId)
            user_id = e.get("assignedUserId") or e.get("userId")
            if user_id and user_id not in user_cache:
                u = fetch_user(user_id)
                user_cache[user_id] = (
                    f"{u.get('firstName','')} {u.get('lastName','')}".strip()
                    if u else "Unknown"
                )
            trainer = user_cache.get(user_id, "Unassigned") if user_id else "Unassigned"

            # Resolve contact (client)
            contact_id = e.get("contactId")
            if contact_id and contact_id not in contact_cache:
                c = fetch_contact(contact_id)
                contact_cache[contact_id] = (
                    f"{c.get('firstName','')} {c.get('lastName','')}".strip()
                    if c else "Unknown"
                )
            client = contact_cache.get(contact_id, "Unknown") if contact_id else e.get("title", "Unknown")

            all_appts.append({
                "start":    start,
                "client":   client,
                "trainer":  trainer,
                "duration": fmt_duration(start, end_t) if end_t else "?",
                "time":     fmt_time(start),
                "calendar": cal_name,
                "status":   status,
            })

    if not all_appts:
        print("No appointments found in this window.")
        return

    # Sort by start time
    all_appts.sort(key=lambda x: sort_key(x["start"]))

    # ── Print utilisation report ───────────────────────────────────────────────
    print(f"{'DATE / TIME':<24} {'CLIENT':<28} {'DURATION':<10} {'TRAINER':<22} {'CALENDAR'}")
    print(f"{'-'*24} {'-'*28} {'-'*10} {'-'*22} {'-'*30}")

    current_day = None
    trainer_mins = {}

    for a in all_appts:
        day = parse_dt(a["start"]).astimezone(TZ).strftime("%A %-d %b")
        if day != current_day:
            print(f"\n── {day} ──")
            current_day = day

        print(f"  {a['time']:<22} {a['client']:<28} {a['duration']:<10} {a['trainer']:<22} {a['calendar']}")

        # Accumulate trainer minutes for summary
        t = a["trainer"]
        try:
            dur_str = a["duration"]
            mins = 0
            if "h" in dur_str and "m" in dur_str:
                parts = dur_str.split("h")
                mins = int(parts[0]) * 60 + int(parts[1].replace("m","").strip())
            elif "h" in dur_str:
                mins = int(dur_str.replace("h","").strip()) * 60
            elif "m" in dur_str:
                mins = int(dur_str.replace("m","").strip())
            trainer_mins[t] = trainer_mins.get(t, 0) + mins
        except Exception:
            pass

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n\n── UTILISATION SUMMARY (29 Jun – 4 Jul) ──────────────────────────────")
    print(f"  Total sessions: {len(all_appts)}")
    print()
    print(f"  {'TRAINER':<25} {'SESSIONS':<10} {'TOTAL TIME'}")
    print(f"  {'-'*25} {'-'*10} {'-'*12}")

    # Count sessions per trainer
    trainer_sessions = {}
    for a in all_appts:
        trainer_sessions[a["trainer"]] = trainer_sessions.get(a["trainer"], 0) + 1

    for trainer in sorted(trainer_sessions, key=lambda t: trainer_sessions[t], reverse=True):
        mins = trainer_mins.get(trainer, 0)
        h, m = divmod(mins, 60)
        time_str = f"{h}h {m}m" if m else f"{h}h"
        print(f"  {trainer:<25} {trainer_sessions[trainer]:<10} {time_str}")

    print()


if __name__ == "__main__":
    main()
