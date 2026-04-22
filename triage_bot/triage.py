#!/usr/bin/env python3
"""
triage_bot/triage.py
Pulls unread GHL conversations from the last 24 hours,
classifies each with Claude, and posts a triage report to Discord.

Runs daily at 8am AEST via Railway cron.
"""

import os
import json
import requests
from datetime import datetime, timedelta, timezone
from anthropic import Anthropic

GHL_API_KEY     = os.environ["GHL_API_KEY"]
GHL_LOCATION_ID = os.environ["GHL_LOCATION_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

GHL_BASE  = "https://services.leadconnectorhq.com"
GHL_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Accept": "application/json",
}

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

CHANNEL_LABELS = {
    "SMS": "SMS",
    "Email": "Email",
    "GMB": "Google",
    "FB": "Facebook",
    "IG": "Instagram",
    "live_chat": "Live Chat",
    "WhatsApp": "WhatsApp",
}


def fetch_unread_conversations():
    """Pull unread conversations updated in the last 24 hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    since_ts = int(since.timestamp() * 1000)

    params = {
        "locationId": GHL_LOCATION_ID,
        "status": "unread",
        "startAfterDate": since_ts,
        "limit": 50,
        "sort": "desc",
        "sortBy": "last_message_date",
    }
    r = requests.get(f"{GHL_BASE}/conversations/search", headers=GHL_HEADERS, params=params)
    if not r.ok:
        print(f"GHL conversations error {r.status_code}: {r.text[:200]}")
        return []
    data = r.json()
    return data.get("conversations", [])


def fetch_contact_name(contact_id):
    """Get contact full name from contact ID."""
    r = requests.get(f"{GHL_BASE}/contacts/{contact_id}", headers=GHL_HEADERS)
    if not r.ok:
        return "Unknown"
    contact = r.json().get("contact", {})
    name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()
    return name or contact.get("email", "Unknown")


def fetch_recent_messages(conversation_id, limit=5):
    """Get the most recent messages from a conversation."""
    r = requests.get(
        f"{GHL_BASE}/conversations/{conversation_id}/messages",
        headers=GHL_HEADERS,
        params={"limit": limit},
    )
    if not r.ok:
        return []
    return r.json().get("messages", {}).get("messages", [])


def classify_conversations(convos):
    """
    Send all conversations to Claude for classification.
    Returns a list of dicts with intent, summary, urgency per conversation.
    """
    if not convos:
        return []

    convo_text = ""
    for i, c in enumerate(convos):
        convo_text += f"\n--- Conversation {i+1} ---\n"
        convo_text += f"Contact: {c['contact_name']}\n"
        convo_text += f"Channel: {c['channel']}\n"
        convo_text += f"Last message: {c['last_message']}\n"
        if c.get("recent_messages"):
            convo_text += "Recent context:\n"
            for msg in c["recent_messages"][-3:]:
                direction = "Member" if msg.get("direction") == "inbound" else "Staff"
                body = msg.get("body", "")[:200]
                convo_text += f"  {direction}: {body}\n"

    prompt = f"""You are triaging incoming gym member conversations for The Evolved, a women's strength training gym in Brisbane.

Classify each conversation below. For each, return a JSON array with one object per conversation containing:
- "intent": one of [Enquiry, Hold Request, Booking, Complaint, Pricing, Cancellation, Returning Member, Admin, Other]
- "summary": one sentence describing what the member wants or needs
- "urgency": one of [High, Medium, Low]
  - High = complaint, upset member, time-sensitive request
  - Medium = needs a response today
  - Low = can wait 24-48hrs

Return ONLY valid JSON array, no other text.

Conversations:
{convo_text}"""

    message = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        classifications = json.loads(message.content[0].text)
        return classifications
    except (json.JSONDecodeError, IndexError):
        # Fallback if Claude returns unexpected format
        return [{"intent": "Unknown", "summary": "Classification failed", "urgency": "Medium"}] * len(convos)


def format_discord_message(convos, classifications):
    """Format the triage report as a Discord message."""
    today = datetime.now().strftime("%A, %-d %B")
    total = len(convos)

    if total == 0:
        return {
            "content": f"**Conversation Triage — {today}**\n✅ No unread conversations in the last 24 hours."
        }

    # Count by urgency
    high   = sum(1 for c in classifications if c.get("urgency") == "High")
    medium = sum(1 for c in classifications if c.get("urgency") == "Medium")
    low    = sum(1 for c in classifications if c.get("urgency") == "Low")

    lines = [
        f"**Conversation Triage — {today}**",
        f"{total} unread · 🔴 {high} high · 🟡 {medium} medium · 🟢 {low} low",
        "",
    ]

    # Sort by urgency: High first
    urgency_order = {"High": 0, "Medium": 1, "Low": 2}
    paired = list(zip(convos, classifications))
    paired.sort(key=lambda x: urgency_order.get(x[1].get("urgency", "Low"), 2))

    for convo, cls in paired:
        urgency = cls.get("urgency", "Medium")
        intent  = cls.get("intent", "Other")
        summary = cls.get("summary", "")
        name    = convo["contact_name"]
        channel = convo["channel"]
        preview = convo["last_message"][:80] + ("…" if len(convo["last_message"]) > 80 else "")

        emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(urgency, "🟡")

        lines.append(f"{emoji} **{name}** · {channel} · `{intent}`")
        lines.append(f"  _{summary}_")
        lines.append(f"  > {preview}")
        lines.append("")

    return {"content": "\n".join(lines)}


def post_to_discord(message):
    """Post the triage report to Discord."""
    r = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if not r.ok:
        print(f"Discord post failed {r.status_code}: {r.text}")
    else:
        print("Triage report posted to Discord.")


def main():
    print(f"Running conversation triage — {datetime.now().isoformat()}")

    print("Fetching unread conversations...")
    raw_convos = fetch_unread_conversations()
    print(f"Found {len(raw_convos)} unread conversations")

    if not raw_convos:
        post_to_discord(format_discord_message([], []))
        return

    # Enrich with contact names and recent messages
    convos = []
    for c in raw_convos:
        contact_id = c.get("contactId", "")
        name = fetch_contact_name(contact_id) if contact_id else "Unknown"
        channel = CHANNEL_LABELS.get(c.get("type", ""), c.get("type", "Unknown"))
        last_message = c.get("lastMessageBody", "").strip() or "(no message body)"
        recent = fetch_recent_messages(c.get("id", ""))

        convos.append({
            "id": c.get("id"),
            "contact_name": name,
            "channel": channel,
            "last_message": last_message,
            "recent_messages": recent,
        })

    print("Classifying with Claude...")
    classifications = classify_conversations(convos)

    print("Posting to Discord...")
    message = format_discord_message(convos, classifications)
    post_to_discord(message)

    print("Done.")


if __name__ == "__main__":
    main()
