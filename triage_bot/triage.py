#!/usr/bin/env python3
"""
triage_bot/triage.py
Pulls unread GHL conversations, classifies each with Claude,
and posts a triage report to Discord.

Runs daily at 6am AEST via Railway cron.
"""

import os
import json
import requests
from datetime import datetime, timezone
from anthropic import Anthropic

GHL_API_KEY         = os.environ["GHL_API_KEY"]
GHL_LOCATION_ID     = os.environ["GHL_LOCATION_ID"]
ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
EMAIL_FROM     = "info@theevolvedgym.com.au"
EMAIL_TO       = "admin@theevolvedgym.com.au"

GHL_BASE    = "https://services.leadconnectorhq.com"
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
    """Pull all unread conversations."""
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
    return r.json().get("conversations", [])


def fetch_contact_name(contact_id):
    """Get contact full name from contact ID."""
    r = requests.get(f"{GHL_BASE}/contacts/{contact_id}", headers=GHL_HEADERS)
    if not r.ok:
        return "Unknown"
    contact = r.json().get("contact", {})
    name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()
    return name or contact.get("email", "Unknown")


def fetch_recent_messages(conversation_id, limit=6):
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
    Returns a list of dicts with category, action, and optional quote per conversation.
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
            convo_text += "Recent messages:\n"
            for msg in c["recent_messages"][-4:]:
                direction = "Member" if msg.get("direction") == "inbound" else "Staff"
                body = msg.get("body", "")[:300]
                if body:
                    convo_text += f"  {direction}: {body}\n"

    prompt = f"""You are triaging incoming conversations for The Evolved, a women's strength training gym in Brisbane.

IMPORTANT DEFINITIONS — get these right:
- SA (Strength Assessment): the initial 1-hour sales consultation for new PROSPECTS who haven't joined yet. SA Confirmations are when a prospect replies "READY" or confirms their upcoming SA appointment. These are high priority.
- Testing / Assessment for existing members: periodic performance testing sessions (strength tests, benchmarks) for current paying members. This is NOT an SA — it's a scheduling request for an existing member.
- PT: personal training sessions for existing paying members.
- SGPT: small group personal training — the main membership product.
- Hold: a member requesting to pause billing and gym access.

For each conversation return a JSON array where each object has:
- "category": one of [Important Urgent, Important Not Urgent, Not Important Urgent, Not Important Not Urgent]
  - Important Urgent: SA confirmations (prospect replies READY/confirms SA), unresolved complaints
  - Important Not Urgent: scheduling requests from existing members (PT, testing, assessments), hold requests, reschedules with 24hr+ notice, any request that needs admin action but isn't time-critical today
  - Not Important Urgent: PT reschedules under 24hrs notice
  - Not Important Not Urgent: marketing, sales pitches, spam, equipment demos, anything not member-related
- "action": short phrase — what admin needs to do (e.g. "Schedule testing session", "Confirm SA appointment", "Process hold request", "Reschedule PT — under 24hrs")
- "quote": the key inbound message verbatim, truncated to 280 chars. Include when the message content helps admin understand what action to take. Set to null if the action is completely self-evident from the name alone.

Return ONLY a valid JSON array, no other text, no code fences.

Conversations:
{convo_text}"""

    message = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        classifications = json.loads(text.strip())
        return classifications
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Classification parse error: {e}")
        raw = message.content[0].text if message.content else "(no content)"
        print(f"Raw response ({len(raw)} chars): {raw[:1000]}")
        return [{"action": "Classification failed", "category": "Not Important Not Urgent", "quote": None}] * len(convos)


CATEGORY_ORDER = {
    "Important Urgent": 0,
    "Important Not Urgent": 1,
    "Not Important Urgent": 2,
    "Not Important Not Urgent": 3,
}

CATEGORY_HEADERS = {
    "Important Urgent":         "🔴 **Important Urgent**",
    "Important Not Urgent":     "🟡 **Important Not Urgent**",
    "Not Important Urgent":     "🟠 **Not Important Urgent**",
    "Not Important Not Urgent": "🟢 **Not Important Not Urgent**",
}


def format_discord_messages(convos, classifications):
    """Format triage report as a list of Discord messages (max 1950 chars each)."""
    today = datetime.now().strftime("%A, %-d %B")
    total = len(convos)

    if total == 0:
        return [{"content": f"**Triage — {today}**\n✅ No unread conversations."}]

    counts = {}
    for c in classifications:
        cat = c.get("category", "Not Important Not Urgent")
        counts[cat] = counts.get(cat, 0) + 1

    header = (
        f"**Triage — {today}**\n"
        f"{total} unread · "
        f"🔴 {counts.get('Important Urgent', 0)} · "
        f"🟡 {counts.get('Important Not Urgent', 0)} · "
        f"🟠 {counts.get('Not Important Urgent', 0)} · "
        f"🟢 {counts.get('Not Important Not Urgent', 0)}\n"
    )

    paired = list(zip(convos, classifications))
    paired.sort(key=lambda x: CATEGORY_ORDER.get(x[1].get("category", "Not Important Not Urgent"), 3))

    # Build lines grouped by category
    lines = []
    current_cat = None
    for convo, cls in paired:
        cat    = cls.get("category", "Not Important Not Urgent")
        action = cls.get("action", "Review")
        quote  = cls.get("quote")
        name   = convo["contact_name"]

        if cat != current_cat:
            lines.append(f"\n{CATEGORY_HEADERS.get(cat, cat)}")
            current_cat = cat

        entry = f"- **{name}**: {action}"
        display_quote = quote or convo.get("last_message")
        if display_quote and display_quote != "(no message body)":
            q = display_quote[:280] + "..." if len(display_quote) > 280 else display_quote
            entry += f'\n  > *"{q}"*'
        lines.append(entry)

    # Chunk into Discord messages under 1950 chars
    messages = []
    current = header
    for line in lines:
        if len(current) + len(line) + 2 > 1950:
            messages.append({"content": current})
            current = line
        else:
            current += "\n" + line
    if current:
        messages.append({"content": current})

    return messages


CATEGORY_COLORS = {
    "Important Urgent":         "#e74c3c",
    "Important Not Urgent":     "#f39c12",
    "Not Important Urgent":     "#e67e22",
    "Not Important Not Urgent": "#27ae60",
}


def format_email_html(convos, classifications):
    """Build an HTML email body matching the triage report."""
    today = datetime.now().strftime("%A, %-d %B")
    total = len(convos)

    if total == 0:
        return f"<p>No unread conversations on {today}.</p>"

    counts = {}
    for c in classifications:
        cat = c.get("category", "Not Important Not Urgent")
        counts[cat] = counts.get(cat, 0) + 1

    paired = list(zip(convos, classifications))
    paired.sort(key=lambda x: CATEGORY_ORDER.get(x[1].get("category", "Not Important Not Urgent"), 3))

    html = f"""
<html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#222;">
<h2 style="margin-bottom:4px;">Triage — {today}</h2>
<p style="color:#666;margin-top:0;">{total} unread &nbsp;·&nbsp;
🔴 {counts.get('Important Urgent', 0)} &nbsp;·&nbsp;
🟡 {counts.get('Important Not Urgent', 0)} &nbsp;·&nbsp;
🟠 {counts.get('Not Important Urgent', 0)} &nbsp;·&nbsp;
🟢 {counts.get('Not Important Not Urgent', 0)}</p>
<hr style="border:none;border-top:1px solid #eee;">
"""

    current_cat = None
    for convo, cls in paired:
        cat    = cls.get("category", "Not Important Not Urgent")
        action = cls.get("action", "Review")
        quote  = cls.get("quote") or convo.get("last_message")
        name   = convo["contact_name"]
        color  = CATEGORY_COLORS.get(cat, "#27ae60")

        if cat != current_cat:
            if current_cat is not None:
                html += "</ul>"
            html += f'<h3 style="color:{color};margin-bottom:6px;">{cat}</h3><ul style="padding-left:20px;margin-top:0;">'
            current_cat = cat

        html += f'<li style="margin-bottom:12px;"><strong>{name}</strong>: {action}'
        if quote and quote != "(no message body)":
            q = quote[:300] + "..." if len(quote) > 300 else quote
            html += f'<br><span style="color:#555;font-style:italic;">&ldquo;{q}&rdquo;</span>'
        html += "</li>"

    html += "</ul></body></html>"
    return html


def send_email(convos, classifications):
    """Send the triage report via Resend API."""
    today = datetime.now().strftime("%A, %-d %B")
    html  = format_email_html(convos, classifications)

    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": EMAIL_FROM,
            "to":   [EMAIL_TO],
            "subject": f"Conversation Triage — {today}",
            "html": html,
        },
    )
    if r.ok:
        print(f"Email sent to {EMAIL_TO}.")
    else:
        raise Exception(f"{r.status_code}: {r.text}")


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

    convos = []
    for c in raw_convos:
        contact_id = c.get("contactId", "")
        name       = fetch_contact_name(contact_id) if contact_id else "Unknown"
        channel    = CHANNEL_LABELS.get(c.get("type", ""), c.get("type", "Unknown"))
        last_msg   = c.get("lastMessageBody", "").strip() or "(no message body)"
        recent     = fetch_recent_messages(c.get("id", ""))

        convos.append({
            "id":              c.get("id"),
            "contact_name":    name,
            "channel":         channel,
            "last_message":    last_msg,
            "recent_messages": recent,
        })

    print("Classifying with Claude...")
    classifications = classify_conversations(convos)

    print("Posting to Discord...")
    messages = format_discord_messages(convos, classifications)
    post_to_discord(messages)

    print("Sending email...")
    try:
        send_email(convos, classifications)
    except Exception as e:
        print(f"Email failed: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
