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
    """Pull all unread conversations regardless of age."""
    params = {
        "locationId": GHL_LOCATION_ID,
        "status": "unread",
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

    prompt = f"""You are triaging incoming conversations for The Evolved, a women's strength training gym in Brisbane.

Classify each conversation. For each, return a JSON array with one object containing:
- "intent": one of [SA Confirmation, SA Pre-Qualification, SA Summary, PT Reschedule (policy), PT Reschedule (outside policy), Hold Request, Cancellation, Complaint, Marketing/Sales, Other]
- "summary": one sentence — contact name, topic, what they want
- "category": one of [Important Urgent, Important Not Urgent, Not Important Urgent, Not Important Not Urgent]
  - Important Urgent: SA Confirmations (READY replies), SA Pre-Qualification follow-ups, complaints
  - Important Not Urgent: PT reschedules with 24hr+ notice, hold requests
  - Not Important Urgent: PT reschedules with less than 24hr notice
  - Not Important Not Urgent: marketing, sales, equipment demos, anything not revenue-generating

Return ONLY a valid JSON array, no other text, no code fences.

Conversations:
{convo_text}"""

    message = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = message.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        classifications = json.loads(text.strip())
        return classifications
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Classification parse error: {e}")
        print(f"Raw response: {message.content[0].text[:500]}")
        return [{"intent": "Unknown", "summary": "Classification failed", "urgency": "Medium"}] * len(convos)


CATEGORY_EMOJI = {
    "Important Urgent": "🔴",
    "Important Not Urgent": "🟡",
    "Not Important Urgent": "🟠",
    "Not Important Not Urgent": "🟢",
}

CATEGORY_ORDER = {
    "Important Urgent": 0,
    "Important Not Urgent": 1,
    "Not Important Urgent": 2,
    "Not Important Not Urgent": 3,
}


def format_discord_messages(convos, classifications):
    """Format triage report as a list of Discord messages (max 2000 chars each)."""
    today = datetime.now().strftime("%A, %-d %B")
    total = len(convos)

    if total == 0:
        return [{"content": f"**Conversation Triage — {today}**\n✅ No unread conversations."}]

    # Count by category
    counts = {}
    for c in classifications:
        cat = c.get("category", "Not Important Not Urgent")
        counts[cat] = counts.get(cat, 0) + 1

    header = (
        f"**Conversation Triage — {today}**\n"
        f"{total} unread · "
        f"🔴 {counts.get('Important Urgent', 0)} · "
        f"🟡 {counts.get('Important Not Urgent', 0)} · "
        f"🟠 {counts.get('Not Important Urgent', 0)} · "
        f"🟢 {counts.get('Not Important Not Urgent', 0)}\n"
    )

    # Sort by category priority
    paired = list(zip(convos, classifications))
    paired.sort(key=lambda x: CATEGORY_ORDER.get(x[1].get("category", "Not Important Not Urgent"), 3))

    # Build entry lines
    entries = []
    for convo, cls in paired:
        cat     = cls.get("category", "Not Important Not Urgent")
        intent  = cls.get("intent", "Other")
        summary = cls.get("summary", "")
        name    = convo["contact_name"]
        channel = convo["channel"]
        emoji   = CATEGORY_EMOJI.get(cat, "🟢")

        entry = f"{emoji} **{name}** · {channel} · `{intent}`\n  _{summary}_\n"
        entries.append(entry)

    # Split into messages under 2000 chars
    messages = []
    current = header
    for entry in entries:
        if len(current) + len(entry) + 1 > 1950:
            messages.append({"content": current})
            current = entry
        else:
            current += "\n" + entry
    if current:
        messages.append({"content": current})

    return messages


def post_to_discord(messages):
    """Post one or more messages to Discord."""
    for message in messages:
        r = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if not r.ok:
            print(f"Discord post failed {r.status_code}: {r.text}")
        else:
            print("Discord message posted.")


def main():
    print(f"Running conversation triage — {datetime.now().isoformat()}")

    print("Fetching unread conversations...")
    raw_convos = fetch_unread_conversations()
    print(f"Found {len(raw_convos)} unread conversations")

    if not raw_convos:
        post_to_discord(format_discord_messages([], []))
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
    messages = format_discord_messages(convos, classifications)
    post_to_discord(messages)

    print("Done.")


if __name__ == "__main__":
    main()
