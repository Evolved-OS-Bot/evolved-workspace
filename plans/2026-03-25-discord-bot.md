# Plan: Discord Bot — Evolved OS on-the-go interface

**Created:** 2026-03-25
**Status:** Draft
**Request:** Build a Discord bot hosted on Railway with two channels: #evolved-os (KPI/CEO chat with full workspace context) and #daily-journal (auto-summarised daily entries that act as persistent memory written back to the workspace).

---

## Overview

### What This Plan Accomplishes

A Discord bot that gives Peter direct, context-aware access to Claude from any device. The bot injects the full Evolved workspace context (business info, strategy, live KPIs) into every message, making it feel like a briefed strategic advisor rather than a generic chatbot. A daily journal system captures conversation summaries as structured memory entries that feed back into the workspace and persist across sessions.

### Why This Matters

Peter is building toward $1M revenue and needs fast, frictionless strategic input while away from his desk. This closes the gap between his workspace intelligence and his mobile workflow — so decisions made on-the-go are grounded in the same context Claude has in a full desktop session.

---

## Current State

### Relevant Existing Structure

| File/Folder | Relevance |
|---|---|
| `context/current-data.md` | Live KPI snapshot — injected into every bot message |
| `context/business-info.md` | Org context — injected into system prompt |
| `context/strategy.md` | Strategic priorities — injected into system prompt |
| `context/personal-info.md` | Peter's role — injected into system prompt |
| `scripts/requirements.txt` | Existing Python dependencies — will be extended |
| `scripts/.env` | Credentials file — will add Discord + Anthropic API keys |
| `scripts/update_metrics.py` | Already writes `current-data.md` — bot can call this |
| `CLAUDE.md` | Workspace documentation — needs updating |

### Gaps or Problems Being Addressed

- No mobile-accessible interface to the workspace
- Conversations with Claude happen in isolated desktop sessions with no memory carry-forward
- Strategic decisions made on-the-go are disconnected from workspace context
- No structured mechanism for capturing and persisting daily insights

---

## Proposed Changes

### Summary of Changes

- Create `discord_bot/` directory with bot code, config, and Railway deployment files
- Two Discord channels: `#evolved-os` (CEO chat) and `#daily-journal` (memory log)
- Bot injects workspace context into every Claude API call
- `/journal` command summarises the day's `#evolved-os` conversation and posts to `#daily-journal`
- Journal entries also written to `context/journal/YYYY-MM-DD.md` for `/prime` to pick up
- Deployed to Railway via GitHub — live 24/7
- Update `requirements.txt`, `.env`, and `CLAUDE.md`

### New Files to Create

| File Path | Purpose |
|---|---|
| `discord_bot/bot.py` | Main bot — handles messages, calls Claude API, manages channels |
| `discord_bot/context_loader.py` | Reads workspace context files and builds system prompt |
| `discord_bot/journal.py` | Generates daily journal summaries and writes them to disk |
| `discord_bot/requirements.txt` | Bot-specific Python dependencies |
| `discord_bot/Procfile` | Railway process definition (`worker: python bot.py`) |
| `discord_bot/railway.toml` | Railway config (Python version, start command) |
| `discord_bot/.env.example` | Template for required environment variables |
| `context/journal/` | Directory for daily journal markdown files |

### Files to Modify

| File Path | Changes |
|---|---|
| `scripts/requirements.txt` | Add `anthropic` package |
| `scripts/.env` | Add `DISCORD_BOT_TOKEN`, `ANTHROPIC_API_KEY` |
| `CLAUDE.md` | Add Discord bot section to workspace structure and commands |

---

## Design Decisions

### Key Decisions Made

1. **Separate `discord_bot/` directory**: Keeps bot code isolated from KPI scripts. Clear separation of concerns — `scripts/` owns Google Sheets automation, `discord_bot/` owns the Discord interface.

2. **System prompt built from workspace files at message time**: Rather than a static system prompt, `context_loader.py` reads the current state of `context/` files each time. This means running `update-metrics` on the desktop automatically improves the bot's next response without any redeployment.

3. **Conversation history per channel session**: The bot maintains in-memory conversation history within a session (up to last 20 messages) so responses feel conversational, not stateless. History resets on bot restart — daily journal provides the persistent layer.

4. **`/journal` as manual trigger (not automatic)**: Auto-summarisation at a fixed time risks missing late-night conversations or firing at awkward times. Peter triggers `/journal` when he's done for the day — takes 2 seconds, gives him control.

5. **Journal entries written to `context/journal/YYYY-MM-DD.md`**: These files are picked up by `/prime` (context folder is fully read on prime), creating a genuine memory system. Over time this builds a searchable log of daily decisions and insights.

6. **Railway over alternatives**: Always-on, simple GitHub deploy, $5/month, no infrastructure management. Fly.io and Render are comparable but Railway has the simplest UX for a single-service bot.

7. **`claude-sonnet-4-6` model**: Matches the desktop workspace model. Consistent reasoning quality across interfaces.

8. **Only `#evolved-os` and `#daily-journal` channels**: Start minimal. Additional channels (e.g. `#metrics`, `#alerts`) can be added in V2 once the core workflow is established.

### Alternatives Considered

- **Slash commands for all interactions**: Rejected — natural language messages are faster on mobile. Only `/journal` uses a slash command since it's a distinct action.
- **Storing conversation history in a database**: Rejected for V1 — in-memory history is sufficient. If Railway restarts wipe history too frequently, SQLite can be added in V2.
- **Auto-posting journal at midnight**: Rejected — manual trigger is more reliable and gives Peter control over when the day "ends."

### Open Questions — RESOLVED

1. **Bot responds to all messages in `#evolved-os`** (not @mention only) — simpler mobile UX.
2. **`/journal` pulls fresh KPI data before summarising** — calls `update_metrics.py` first to ensure journal reflects current numbers.
3. **Fresh GitHub repo** — new private repo named `evolved-workspace` to be created during implementation.

---

## Step-by-Step Tasks

### Step 1: Create Discord server and channels

**Actions:**
- Create a new Discord server named "Evolved OS"
- Create two text channels:
  - `#evolved-os` — set topic: "CEO channel. Talk to your strategic advisor."
  - `#daily-journal` — set topic: "Daily conversation summaries. Persistent memory."
- Note the channel IDs for both (right-click channel → Copy Channel ID — requires Developer Mode: User Settings → Advanced → Developer Mode)

**Files affected:** None — external setup

---

### Step 2: Create Discord bot application

**Actions:**
- Go to https://discord.com/developers/applications
- Click "New Application" → name it "Evolved OS"
- Go to Bot tab → click "Add Bot"
- Under Token → click "Reset Token" → copy and save the token securely
- Under Privileged Gateway Intents → enable:
  - **Message Content Intent** (required to read message text)
  - **Server Members Intent**
- Go to OAuth2 → URL Generator:
  - Scopes: `bot`
  - Bot Permissions: `Send Messages`, `Read Message History`, `Add Reactions`
- Copy the generated URL → open in browser → add bot to your Evolved OS server

**Files affected:** None — external setup

---

### Step 3: Create Anthropic API key

**Actions:**
- Go to https://console.anthropic.com/
- Settings → API Keys → Create Key
- Name it "evolved-discord-bot"
- Copy and save securely

**Files affected:** None — external setup

---

### Step 4: Create `discord_bot/` directory and `context_loader.py`

**Actions:**
- Create `discord_bot/context_loader.py`:

```python
"""
context_loader.py
Reads workspace context files and builds the system prompt
injected into every Claude API call.
"""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent
CONTEXT_DIR    = WORKSPACE_ROOT / "context"

CONTEXT_FILES = [
    "business-info.md",
    "personal-info.md",
    "strategy.md",
    "current-data.md",
]


def load_journal_entries(max_entries=5):
    """Load the most recent daily journal entries."""
    journal_dir = CONTEXT_DIR / "journal"
    if not journal_dir.exists():
        return ""
    entries = sorted(journal_dir.glob("*.md"), reverse=True)[:max_entries]
    if not entries:
        return ""
    content = "\n\n---\n\n".join(f.read_text() for f in entries)
    return f"\n\n## Recent Journal Entries (last {len(entries)} days)\n\n{content}"


def build_system_prompt():
    """
    Reads all context files and journal entries,
    returns a complete system prompt string.
    """
    parts = [
        "You are Claude — a strategic advisor embedded in Peter Brown's Evolved OS workspace.",
        "You have full context about his business, role, strategy, and current KPI data.",
        "Be direct, concise, and strategically sharp. Challenge assumptions when warranted.",
        "Peter is accessing you via Discord on mobile — keep responses focused and scannable.",
        "Use markdown formatting where it helps readability.",
        "",
    ]

    for filename in CONTEXT_FILES:
        path = CONTEXT_DIR / filename
        if path.exists():
            parts.append(f"## {filename}\n\n{path.read_text().strip()}")

    parts.append(load_journal_entries())

    return "\n\n".join(filter(None, parts))
```

**Files affected:**
- `discord_bot/context_loader.py` (create)

---

### Step 5: Create `discord_bot/journal.py`

**Actions:**
- Create `discord_bot/journal.py`:

```python
"""
journal.py
Generates a daily journal summary from the day's #evolved-os
conversation history and writes it to context/journal/YYYY-MM-DD.md.
"""

import anthropic
from datetime import date
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent
JOURNAL_DIR    = WORKSPACE_ROOT / "context" / "journal"

JOURNAL_PROMPT = """\
You are summarising a day's strategic conversation between Peter Brown and his AI advisor.

Create a structured daily journal entry with:
1. **Date and headline** — one sentence capturing the day's main theme
2. **Key decisions made** — bulleted list of any decisions or directions chosen
3. **Key insights** — important realisations, patterns, or strategic observations
4. **Open items** — anything left unresolved or flagged for follow-up
5. **Metrics discussed** — any specific numbers or KPIs referenced
6. **Tone / context** — brief note on what Peter was focused on (e.g. growth, ops, a specific problem)

Be specific and factual. Use Peter's actual words where they capture intent clearly.
This entry will be read by Claude in future sessions as memory — make it dense and useful.
"""


def generate_journal_entry(conversation_history: list[dict]) -> str:
    """
    Takes the day's conversation history and generates a journal entry via Claude.
    Returns the formatted markdown string.
    """
    client = anthropic.Anthropic()

    messages = conversation_history + [
        {
            "role": "user",
            "content": "Please summarise today's conversation into a journal entry using the format specified.",
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=JOURNAL_PROMPT,
        messages=messages,
    )

    today     = date.today().strftime("%Y-%m-%d")
    weekday   = date.today().strftime("%A")
    entry     = response.content[0].text

    return f"# Journal — {today} ({weekday})\n\n{entry}\n"


def save_journal_entry(entry: str) -> Path:
    """Writes the journal entry to context/journal/YYYY-MM-DD.md."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    today    = date.today().strftime("%Y-%m-%d")
    filepath = JOURNAL_DIR / f"{today}.md"
    filepath.write_text(entry)
    return filepath
```

**Files affected:**
- `discord_bot/journal.py` (create)

---

### Step 6: Create `discord_bot/bot.py`

**Actions:**
- Create `discord_bot/bot.py`:

```python
#!/usr/bin/env python3
"""
bot.py
Evolved OS Discord bot.
- #evolved-os: direct Claude chat with full workspace context
- /journal: summarises the day's conversation and posts to #daily-journal
"""

import os
import asyncio
import discord
import anthropic
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

from context_loader import build_system_prompt
from journal import generate_journal_entry, save_journal_entry

DISCORD_TOKEN        = os.environ["DISCORD_BOT_TOKEN"]
EVOLVED_OS_CHANNEL   = int(os.environ["EVOLVED_OS_CHANNEL_ID"])
JOURNAL_CHANNEL      = int(os.environ["JOURNAL_CHANNEL_ID"])
MAX_HISTORY          = 20   # messages kept in memory per session

intents                  = discord.Intents.default()
intents.message_content  = True
bot                      = commands.Bot(command_prefix="/", intents=intents)
claude                   = anthropic.Anthropic()

# In-memory conversation history (resets on restart)
conversation_history: list[dict] = []


def trim_history():
    """Keep only the last MAX_HISTORY messages."""
    global conversation_history
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]


@bot.event
async def on_ready():
    print(f"Evolved OS bot online as {bot.user}")


@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only respond in #evolved-os
    if message.channel.id != EVOLVED_OS_CHANNEL:
        await bot.process_commands(message)
        return

    # Add user message to history
    conversation_history.append({
        "role":    "user",
        "content": message.content,
    })
    trim_history()

    # Show typing indicator
    async with message.channel.typing():
        try:
            system_prompt = build_system_prompt()

            response = claude.messages.create(
                model      = "claude-sonnet-4-6",
                max_tokens = 1024,
                system     = system_prompt,
                messages   = conversation_history,
            )

            reply = response.content[0].text

            # Add assistant reply to history
            conversation_history.append({
                "role":    "assistant",
                "content": reply,
            })
            trim_history()

            # Discord has a 2000 char limit — split if needed
            if len(reply) <= 2000:
                await message.channel.send(reply)
            else:
                for i in range(0, len(reply), 2000):
                    await message.channel.send(reply[i:i+2000])

        except Exception as e:
            await message.channel.send(f"Error: {e}")

    await bot.process_commands(message)


@bot.command(name="journal")
async def journal_command(ctx):
    """Summarises today's #evolved-os conversation and posts to #daily-journal."""
    if ctx.channel.id != EVOLVED_OS_CHANNEL:
        await ctx.send("Use /journal in #evolved-os.")
        return

    if not conversation_history:
        await ctx.send("No conversation to summarise yet today.")
        return

    await ctx.send("Generating today's journal entry...")

    try:
        # Pull fresh KPI data before summarising
        import subprocess, sys
        await ctx.send("Refreshing KPI data...")
        subprocess.run([sys.executable, str(Path(__file__).parent.parent / "scripts" / "update_metrics.py")], check=True)

        entry    = generate_journal_entry(conversation_history)
        filepath = save_journal_entry(entry)

        # Post to #daily-journal channel
        journal_channel = bot.get_channel(JOURNAL_CHANNEL)
        if journal_channel:
            if len(entry) <= 2000:
                await journal_channel.send(entry)
            else:
                for i in range(0, len(entry), 2000):
                    await journal_channel.send(entry[i:i+2000])

        await ctx.send(f"Journal entry saved and posted to #daily-journal.")

    except Exception as e:
        await ctx.send(f"Journal error: {e}")


bot.run(DISCORD_TOKEN)
```

**Files affected:**
- `discord_bot/bot.py` (create)

---

### Step 7: Create deployment and config files

**Actions:**
- Create `discord_bot/requirements.txt`:
```
discord.py==2.3.2
anthropic>=0.40.0
python-dotenv==1.0.0
```

- Create `discord_bot/Procfile`:
```
worker: python bot.py
```

- Create `discord_bot/railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python bot.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

- Create `discord_bot/.env.example`:
```
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
EVOLVED_OS_CHANNEL_ID=channel_id_for_evolved_os
JOURNAL_CHANNEL_ID=channel_id_for_daily_journal
```

- Create `context/journal/` directory (add `.gitkeep` so it commits)

**Files affected:**
- `discord_bot/requirements.txt` (create)
- `discord_bot/Procfile` (create)
- `discord_bot/railway.toml` (create)
- `discord_bot/.env.example` (create)
- `context/journal/.gitkeep` (create)

---

### Step 8: Update `.env` with new credentials

**Actions:**
- Add to `scripts/.env`:
```
# Discord Bot
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
EVOLVED_OS_CHANNEL_ID=channel_id_for_evolved_os
JOURNAL_CHANNEL_ID=channel_id_for_daily_journal
```

Note: The bot reads its `.env` from `discord_bot/.env` — create that file too with the same values. Do NOT commit either `.env` file to GitHub.

**Files affected:**
- `scripts/.env` (modify)
- `discord_bot/.env` (create — gitignored)

---

### Step 9: Initialise Git repo and push to GitHub

**Actions:**
- From workspace root, confirm `.gitignore` exists and includes:
  ```
  scripts/.env
  discord_bot/.env
  scripts/google_credentials.json
  __pycache__/
  *.pyc
  ```
- Create `.gitignore` if it doesn't exist with the above content
- Initialise git if not already a repo: `git init`
- Create a new **private** GitHub repo named `evolved-workspace`:
  - Go to https://github.com/new
  - Name: `evolved-workspace`
  - Visibility: **Private**
  - Do NOT initialise with README (we're pushing existing code)
  - Click Create Repository — copy the repo URL
- Commit all files: `git add . && git commit -m "Initial commit — Evolved OS Discord bot"`
- Push: `git remote add origin <repo-url> && git push -u origin main`

**Files affected:**
- `.gitignore` (create/modify)

---

### Step 10: Deploy to Railway

**Actions:**
- Go to https://railway.app → New Project → Deploy from GitHub repo
- Select the repo and branch (`main`)
- Railway will detect the `Procfile` and build automatically
- Once deployed, go to the service → Variables tab → add all environment variables:
  - `DISCORD_BOT_TOKEN`
  - `ANTHROPIC_API_KEY`
  - `EVOLVED_OS_CHANNEL_ID`
  - `JOURNAL_CHANNEL_ID`
- Trigger a redeploy after adding variables
- Check logs to confirm: `Evolved OS bot online as Evolved OS#XXXX`

**Files affected:** None — external deployment

---

### Step 11: Update `CLAUDE.md`

**Actions:**
- Add `discord_bot/` to the workspace structure tree and table
- Add a note in the Commands section about the Discord interface

**Files affected:**
- `CLAUDE.md` (modify)

---

### Step 12: Test and validate

**Actions:**
- Send a message in `#evolved-os` — confirm bot responds with context-aware reply
- Verify response references The Evolved, Peter's role, or current KPI data
- Run `/journal` — confirm entry posts to `#daily-journal` and appears in `context/journal/`
- Run `update-metrics` on desktop, then send another message in Discord — confirm bot reflects updated KPI data in next response
- Confirm bot stays online after closing MacBook (Railway is running it)

**Files affected:** None — validation only

---

## Connections & Dependencies

### Files That Reference This Area

- `context/journal/` — written by the bot, read by `/prime` via context folder scan
- `context/current-data.md` — read by bot on every message via `context_loader.py`
- `CLAUDE.md` — needs updating to document the new directory and workflow

### Updates Needed for Consistency

- `CLAUDE.md` workspace structure table
- `shell-aliases.md` — optionally add a note that `update-metrics` now also improves Discord bot responses

### Impact on Existing Workflows

- `update-metrics` becomes more valuable — running it on desktop immediately improves on-the-go bot responses
- `/prime` will automatically pick up journal entries from `context/journal/` — desktop sessions gain awareness of mobile conversations
- No existing scripts are modified or broken

---

## Validation Checklist

- [ ] Discord server created with `#evolved-os` and `#daily-journal` channels
- [ ] Bot application created in Discord Developer Portal with correct intents
- [ ] Bot added to the server via OAuth2 invite link
- [ ] `discord_bot/` directory created with all files
- [ ] `context/journal/` directory created
- [ ] `.gitignore` includes all credential files
- [ ] Repo pushed to GitHub (private)
- [ ] Railway deployment live — bot shows online in Discord
- [ ] Environment variables set in Railway dashboard
- [ ] Message in `#evolved-os` returns context-aware Claude response
- [ ] `/journal` posts summary to `#daily-journal` and writes file to `context/journal/`
- [ ] `CLAUDE.md` updated

---

## Success Criteria

1. Sending a message in `#evolved-os` from a phone returns a strategic, context-aware response within 5 seconds
2. `/journal` generates a structured daily summary that appears in both `#daily-journal` and `context/journal/YYYY-MM-DD.md`
3. Running `update-metrics` on desktop is reflected in the bot's next response without redeployment
4. Bot remains online 24/7 without Peter's Mac being on

---

## Notes

- **V2 additions**: `#metrics` channel that auto-posts weekly KPI snapshot when `update-metrics` runs; alerting if active member count drops week-over-week; ability for bot to trigger `update-metrics` on demand via `/refresh` command
- **Context window management**: If journal entries grow large, `context_loader.py` already limits to last 5 entries. Adjust `max_entries` as needed.
- **Railway costs**: Free tier gives 500 hours/month (not enough for always-on). The $5/month Hobby plan is required for 24/7 uptime — straightforward upgrade.
- **`.env` for Railway vs local**: The bot reads from `discord_bot/.env` locally. On Railway, env vars are set in the dashboard — the `.env` file is not deployed (gitignored).
- **Message history reset on restart**: Railway restarts are infrequent but do happen. The daily journal mitigates this — the most important context is always persisted to disk.
