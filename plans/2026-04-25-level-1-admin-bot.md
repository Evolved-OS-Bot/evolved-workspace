# Plan: Level 1 Admin Bot — Draft Replies with Discord Approval Gating

**Created:** 2026-04-25
**Status:** Draft
**Request:** Build a Level 1 admin bot that generates policy-aware draft replies for actionable GHL conversations, posts them to a Discord approval channel, and sends approved drafts via the GHL API on ✅ reaction.

---

## Overview

### What This Plan Accomplishes

The triage bot currently classifies conversations and reports them. This plan extends that system so that for every actionable conversation, a policy-compliant draft reply is generated and posted to a `#admin-drafts` Discord channel. Admin reviews each draft and reacts ✅ to send or ❌ to discard — the local Discord bot handles the reaction and fires the GHL send API.

### Why This Matters

This is the first step toward replacing manual admin messaging with AI-assisted workflows. It keeps a human in the loop (every draft is reviewed before sending) while eliminating the blank-page problem — admin never has to write from scratch. Policy accuracy is enforced at generation time, not at send time.

---

## Current State

### Relevant Existing Structure

```
triage_bot/
  triage.py             — Railway cron, classifies conversations, posts to #conversation-triage
  railway.toml          — cron: 6am AEST daily
  requirements.txt      — anthropic, requests

discord_bot/
  bot.py                — local bot, handles #evolved-os chat, daily/weekly reports
  context_loader.py     — builds system prompt from context/ files
  .env                  — bot tokens, channel IDs

context/
  policies.md           — SGPT and PT policies, Policy Decision Rules section
```

### Gaps or Problems Being Addressed

- Triage report tells admin what to do, but admin must still write every reply manually
- No policy enforcement at reply time — admin may inadvertently promise refunds, credits, or exceptions
- No structured approval workflow — replies are composed in GHL with no review step
- GHL channel (SMS/email) is not surfaced in the triage report, meaning admin must open GHL to reply

---

## Proposed Changes

### Summary of Changes

- Add draft generation to `triage_bot/triage.py` — after classification, generate a reply draft for each actionable conversation using Claude + policies.md
- Post drafts to `#admin-drafts` Discord channel via a new webhook (separate from `#conversation-triage`)
- Add `on_raw_reaction_add` handler to `discord_bot/bot.py` — watches `#admin-drafts` for ✅/❌ reactions
- Add GHL send message function to `discord_bot/bot.py` — fires on ✅ approval
- Add `ADMIN_DRAFTS_WEBHOOK_URL` to triage bot Railway env vars
- Add `ADMIN_DRAFTS_CHANNEL_ID` to local bot `.env`
- Create `#admin-drafts` channel in Discord server (manual step)

### New Files to Create

| File Path | Purpose |
|---|---|
| `discord_bot/admin_drafts.py` | GHL send message function and draft approval logic, imported by bot.py |

### Files to Modify

| File Path | Changes |
|---|---|
| `triage_bot/triage.py` | Add `generate_draft()` and `post_drafts_to_discord()` functions; call after classification |
| `discord_bot/bot.py` | Add `ADMIN_DRAFTS_CHANNEL_ID` env var; add `on_raw_reaction_add` event handler; import admin_drafts |
| `discord_bot/.env` | Add `ADMIN_DRAFTS_CHANNEL_ID` |
| `CLAUDE.md` | Document the new admin drafts channel and workflow |

---

## Design Decisions

### Key Decisions Made

1. **Draft generation runs in the Railway triage cron (6am)**: Drafts are generated at the same time as the triage report so everything is ready when admin starts their day. No manual trigger needed.

2. **Drafts posted via Discord webhook (not bot API)**: The Railway cron already uses webhooks. Consistent with existing pattern. Works without a persistent connection.

3. **Metadata embedded in Discord embed footer**: Each draft message embed includes the GHL conversation ID and channel type in the footer (`ghl_id:{id}|channel:{type}`). The local bot reads this on reaction to know where to send. Not pretty but functional and invisible to the admin in normal use.

4. **Local bot handles reactions**: Only the local bot has a persistent WebSocket connection to Discord. Railway cannot watch for reactions. The local bot watches `#admin-drafts` via `on_raw_reaction_add`.

5. **Individual Claude calls per draft (not batched)**: Simpler code, easier error handling. Volume is low (5–10 actionable conversations per day). Haiku cost is negligible.

6. **Drafts generated for Important Urgent, Important Not Urgent, Not Important Urgent only**: Not Important Not Urgent conversations (spam, marketing) don't need replies. These are skipped.

7. **Draft deleted from Discord after ✅ send or ❌ discard**: Keeps `#admin-drafts` clean. Admin can see at a glance what still needs actioning.

8. **SMS drafts ≤160 chars target, email drafts can be longer**: Claude is instructed to respect channel constraints. SMS drafts are concise; email drafts can include more context.

9. **Policy rules loaded from `context/policies.md`**: Single source of truth. Already exists. Draft prompt references the Policy Decision Rules section directly.

10. **Reaction must come from a non-bot user**: Guard against accidental bot reactions triggering sends.

### Alternatives Considered

- **Slash command to generate drafts on-demand**: Less friction but requires admin to remember to run it. Automatic at 6am is better UX.
- **Inline draft in `#conversation-triage`**: Would clutter the triage report. Keeping drafts in a separate channel preserves the report's scannability.
- **Store GHL ID in a local JSON map**: More complex, fails if bot restarts between cron run and reaction. Embed metadata is simpler and stateless.

### Open Questions

None — design is fully resolved.

---

## Step-by-Step Tasks

### Step 1: Create `#admin-drafts` Discord Channel (Manual)

Create a new text channel in the Evolved-OS Discord server named `admin-drafts`. Copy the channel ID. This is where draft replies will appear for review.

**Actions:**
- In Discord: Server Settings → Channels → New Channel → `admin-drafts`
- Copy the channel ID (right-click channel → Copy ID, with Developer Mode enabled)
- Create a new Discord webhook in this channel — name it "Admin Drafts Bot"
- Copy the webhook URL

**Files affected:** None (manual Discord setup)

---

### Step 2: Add Environment Variables

Add the new env vars to both the local bot and the Railway triage service.

**Actions:**

Local bot — add to `discord_bot/.env`:
```
ADMIN_DRAFTS_CHANNEL_ID=<channel_id_from_step_1>
```

Railway triage bot — add via Railway dashboard:
```
ADMIN_DRAFTS_WEBHOOK_URL=<webhook_url_from_step_1>
```

**Files affected:**
- `discord_bot/.env`
- Railway environment (manual via dashboard)

---

### Step 3: Add Draft Generation to Triage Bot

Add two functions to `triage_bot/triage.py`:

**`generate_draft(convo, cls, policies_text)`** — calls Claude Haiku with the conversation context, classification, and relevant policy rules to produce a ready-to-send reply draft.

Prompt structure:
```
You are writing a reply on behalf of The Evolved, a women's strength training gym in Brisbane.

Tone: warm, professional, concise. Use the member's first name. Sign off as "The Evolved team".
Channel: {channel} — {SMS: keep under 160 chars if possible | Email: can be longer}

Member: {contact_name} ({SGPT Member / PT Client / SA Prospect})
Intent: {action}
Their message: {quote or last_message}

Relevant policy:
{relevant_policy_excerpt}

Write ONLY the reply text. No preamble, no explanation, no quotes around it.
```

**`generate_and_post_drafts(convos, classifications)`** — iterates over actionable conversations (category != "Not Important Not Urgent"), calls `generate_draft()` for each, and posts each draft to `#admin-drafts` via the `ADMIN_DRAFTS_WEBHOOK_URL` webhook as a Discord embed.

Discord embed format:
```
Title: 📝 Draft Reply — {contact_name}
Color: category colour (red/yellow/orange)
Fields:
  - Category: {category}
  - Intent: {action}
  - Channel: {channel}
  - Draft: {draft_text}
Footer: ghl_id:{conversation_id}|channel:{channel_type_code}
  e.g. ghl_id:abc123|channel:SMS
```

Add `generate_and_post_drafts(convos, classifications)` call in `main()` after `post_to_discord()`.

Load policies from `context/policies.md` at the top of the function:
```python
POLICIES_PATH = Path(__file__).parent.parent / "context" / "policies.md"
policies_text = POLICIES_PATH.read_text() if POLICIES_PATH.exists() else ""
```

**Files affected:**
- `triage_bot/triage.py`

---

### Step 4: Create `discord_bot/admin_drafts.py`

New module imported by `bot.py`. Contains the GHL send logic.

```python
"""
admin_drafts.py
Handles ✅/❌ reactions on #admin-drafts messages.
✅ — parse embed footer, send message via GHL API
❌ — delete the draft message
"""

import os
import re
import requests

GHL_API_KEY = os.environ["GHL_API_KEY"]
GHL_BASE    = "https://services.leadconnectorhq.com"
GHL_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}

# Map channel labels back to GHL message types
CHANNEL_TO_TYPE = {
    "SMS":        "SMS",
    "Email":      "Email",
    "WhatsApp":   "WhatsApp",
    "Facebook":   "FB",
    "Instagram":  "IG",
    "Google":     "GMB",
    "Live Chat":  "Live_Chat",
}


def parse_embed_footer(footer_text: str):
    """
    Extract GHL conversation ID and channel type from embed footer.
    Expected format: ghl_id:{id}|channel:{channel}
    Returns (conversation_id, channel) or (None, None) on failure.
    """
    match = re.search(r"ghl_id:([^\|]+)\|channel:(\S+)", footer_text or "")
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None


def get_draft_text_from_embed(embed) -> str:
    """Extract the draft text from the embed fields."""
    for field in embed.fields:
        if field.name == "Draft":
            return field.value
    return ""


def send_ghl_message(conversation_id: str, channel: str, message: str) -> bool:
    """Send a message to a GHL conversation. Returns True on success."""
    msg_type = CHANNEL_TO_TYPE.get(channel, "SMS")
    payload  = {
        "type":           msg_type,
        "conversationId": conversation_id,
        "message":        message,
    }
    r = requests.post(
        f"{GHL_BASE}/conversations/messages",
        headers=GHL_HEADERS,
        json=payload,
    )
    if r.ok:
        print(f"GHL message sent to {conversation_id} via {msg_type}")
        return True
    else:
        print(f"GHL send failed {r.status_code}: {r.text[:200]}")
        return False
```

**Files affected:**
- `discord_bot/admin_drafts.py` (new file)

---

### Step 5: Add Reaction Handler to `discord_bot/bot.py`

**Actions:**

Add `ADMIN_DRAFTS_CHANNEL_ID` env var read at the top:
```python
ADMIN_DRAFTS_CHANNEL_ID = int(os.environ.get("ADMIN_DRAFTS_CHANNEL_ID", "0"))
```

Add import:
```python
from admin_drafts import parse_embed_footer, get_draft_text_from_embed, send_ghl_message
```

Add `on_raw_reaction_add` event handler:

```python
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Only watch #admin-drafts
    if payload.channel_id != ADMIN_DRAFTS_CHANNEL_ID:
        return
    # Ignore bot's own reactions
    if payload.user_id == bot.user.id:
        return

    emoji = str(payload.emoji)
    if emoji not in ("✅", "❌"):
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    # Must be a webhook/embed message with our footer
    if not message.embeds:
        return

    embed  = message.embeds[0]
    footer = embed.footer.text if embed.footer else ""
    convo_id, channel_type = parse_embed_footer(footer)

    if not convo_id:
        return

    if emoji == "✅":
        draft_text = get_draft_text_from_embed(embed)
        if not draft_text:
            await channel.send("⚠️ Could not extract draft text from embed.")
            return
        success = await asyncio.to_thread(
            send_ghl_message, convo_id, channel_type, draft_text
        )
        if success:
            await message.delete()
            await channel.send(f"✅ Sent to {embed.title.replace('📝 Draft Reply — ', '')}.", delete_after=10)
        else:
            await channel.send("⚠️ GHL send failed — check logs.")

    elif emoji == "❌":
        await message.delete()
        await channel.send(f"❌ Draft discarded.", delete_after=5)
```

**Files affected:**
- `discord_bot/bot.py`

---

### Step 6: Add `GHL_API_KEY` to Local Bot Environment

The local bot currently doesn't have `GHL_API_KEY` — it's only in the Railway environment. The `admin_drafts.py` module needs it to call the GHL send API.

**Actions:**
- Add `GHL_API_KEY=<your_key>` to `discord_bot/.env`
- Same value as used in the Railway triage bot

**Files affected:**
- `discord_bot/.env`

---

### Step 7: Update `triage_bot/requirements.txt`

No new dependencies needed — `requests` and `anthropic` already cover everything.

Verify the file still contains:
```
anthropic>=0.40.0
requests==2.31.0
```

**Files affected:**
- `triage_bot/requirements.txt` (verify only)

---

### Step 8: Restart Local Bot and Test

**Actions:**
- Commit and push all code changes to GitHub
- Restart local bot: `launchctl unload ~/Library/LaunchAgents/com.evolved.discord-bot.plist && sleep 2 && launchctl load ~/Library/LaunchAgents/com.evolved.discord-bot.plist`
- Trigger a manual Railway cron run for the triage bot
- Verify:
  - Drafts appear in `#admin-drafts` as Discord embeds
  - Each embed has contact name, category, intent, channel, draft text, and footer with GHL ID
  - ✅ reaction on a draft sends the message and deletes the embed
  - ❌ reaction discards and deletes
  - Confirmation message appears briefly after each action

---

### Step 9: Update CLAUDE.md

Add `#admin-drafts` channel to the Discord bot section and note the draft approval workflow.

**Files affected:**
- `CLAUDE.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `triage_bot/triage.py` — extended with draft generation
- `discord_bot/bot.py` — extended with reaction handler
- `context/policies.md` — loaded by draft generation prompt at runtime

### Updates Needed for Consistency

- `CLAUDE.md` — document new channel and workflow
- Railway dashboard — add `ADMIN_DRAFTS_WEBHOOK_URL` env var
- `discord_bot/.env` — add `ADMIN_DRAFTS_CHANNEL_ID` and `GHL_API_KEY`

### Impact on Existing Workflows

- Triage cron runtime increases by ~30–60 seconds (draft generation API calls per actionable conversation)
- No impact on `#conversation-triage` report — drafts post separately
- No impact on `#evolved-os` chat or daily/weekly reports

---

## Validation Checklist

- [ ] `#admin-drafts` Discord channel created and webhook URL obtained
- [ ] `ADMIN_DRAFTS_WEBHOOK_URL` added to Railway triage bot env vars
- [ ] `ADMIN_DRAFTS_CHANNEL_ID` added to `discord_bot/.env`
- [ ] `GHL_API_KEY` added to `discord_bot/.env`
- [ ] Triage bot manual run produces draft embeds in `#admin-drafts`
- [ ] Each embed contains: contact name, category, intent, channel, draft text, footer with `ghl_id:...|channel:...`
- [ ] ✅ reaction sends message via GHL and deletes embed
- [ ] ❌ reaction deletes embed without sending
- [ ] Confirmation message appears and auto-deletes after action
- [ ] Drafts not generated for "Not Important Not Urgent" conversations
- [ ] PT reschedule outside policy produces a decline draft (not an approval)
- [ ] PT reschedule within policy produces an approval draft directing to reschedule link
- [ ] `CLAUDE.md` updated

---

## Success Criteria

1. Admin opens `#admin-drafts` at 6am and sees a draft reply for every actionable conversation from the triage report
2. A single ✅ reaction sends a policy-compliant message to the member via GHL — no copy-pasting, no GHL login required
3. Zero messages sent without human approval — every draft requires explicit ✅ before firing

---

## Notes

**Voice and tone for drafts**: The Evolved communicates warmly but concisely. SMS drafts should feel personal, not automated. Claude should use the member's first name, avoid corporate language, and sign off naturally. Review a few early drafts and feed corrections back into the prompt if needed.

**Phase 2 (future)**: Once draft quality is trusted, specific intents (hold acknowledgements, policy declines) can be auto-approved without human reaction — add an `AUTO_SEND_INTENTS` list that bypasses the approval step for defined, low-risk reply types.

**Phase 3 (future)**: Expand to trigger GHL workflow actions — move pipeline stages, update custom fields, book SA appointments — not just send messages.

**GHL API note**: The send message endpoint (`POST /conversations/messages`) needs to be tested for each channel type (SMS, Email, WhatsApp). SMS is the primary channel and should be validated first. Email may require additional fields (`subject`, `html`).
