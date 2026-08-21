# Log Session

Record today's work, notify Discord, and generate build-in-public social content.

## Variables

session_length: $ARGUMENTS (just the session length — e.g. "90 mins" or "2 hours")
image_path: optional — if the user pastes a screenshot path in their message, capture it here (e.g. "/Users/peterbrown/Desktop/screenshot.png"). Used in Step 8 to post to Instagram.

---

## Step 1: Summarise the Session

Review the current conversation and identify everything that was built, fixed, decided, or shipped. Do not ask the user — infer from context. List tasks as specific outcomes, not vague descriptions.

Examples of good task descriptions:
- Built 6 video results pages (Belinda, Orlagh, Peta, Tess, Laura, Sophie) — deployed to WP, archive, carousel, and homepage.js
- Scaffolded Hero Workspace at /Users/peterbrown/Hero Workspace with CLAUDE.md, context files, and 3 source commands
- Cleaned up evolved-workspace: archived 6 plans, removed unused skills, tightened .gitignore

---

## Step 2: Sync Roadmap

Before writing the journal, update `context/roadmap.md` to reflect the session's work:

- Any item that was completed → mark Live or move to Completed table with today's date
- Any item that advanced → update status and next action
- Any new idea mentioned in conversation → add as an Idea entry with today's date
- Update the `Last Updated` date at the top of the file

Do this with a direct file edit — do not ask the user, just apply the changes.

---

## Step 3: Write Journal Entry

Append a structured entry to `context/journal/YYYY-MM-DD.md` (use today's date). Create the file if it doesn't exist.

Format:

```markdown
## Session — [session length]

**Date:** YYYY-MM-DD
**Length:** [session length]

### Tasks Completed

[Bullet list from Step 1 — specific, outcome-oriented]

---
```

If the file already has entries from today, append below the last `---` separator.

---

## Step 4: Post to Discord

Source the `.env` file and POST the session summary to the configured Discord channel.

```bash
python3 - << 'PYEOF'
import os, json, subprocess, datetime

env_path = "scripts/.env"
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
if not url:
    print("DISCORD_WEBHOOK_URL not set — skipping Discord notification")
    exit(0)

tasks = """[TASKS_PLACEHOLDER]"""

payload = {
    "embeds": [{
        "title": f"Session Log — {datetime.date.today()}",
        "description": tasks.strip(),
        "color": 15844367,
        "fields": [
            {"name": "Length", "value": "[SESSION_LENGTH_PLACEHOLDER]", "inline": True},
            {"name": "Workspace", "value": "Evolved Workspace", "inline": True}
        ],
        "footer": {"text": "Evolved OS"}
    }]
}

result = subprocess.run(
    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", url,
     "-H", "Content-Type: application/json",
     "-d", json.dumps(payload)],
    capture_output=True, text=True
)
print(f"Discord: {result.stdout}")
PYEOF
```

**Before running:** replace `[TASKS_PLACEHOLDER]` with the task bullet list from Step 1 (as a plain string, one task per line with `- ` prefix), and `[SESSION_LENGTH_PLACEHOLDER]` with the session length argument.

If `DISCORD_WEBHOOK_URL` is not set in `scripts/.env`, this step is skipped silently.

**To set up the webhook:**
1. Discord → your server → channel settings → Integrations → Webhooks → New Webhook
2. Copy the webhook URL
3. Add to `scripts/.env`: `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...`

---

## Step 5: Generate Social Copy

Write three platform-specific drafts to the terminal (do not save to file — user will copy what they want).

**Voice:** Founder sharing real work in progress. Direct, specific, no hype. Show the system, not the outcome. First person, present tense where possible. No emojis unless the platform benefits from them.

---

### LinkedIn (300–500 words)

- Open with a specific observation or problem encountered today
- Explain what was built/solved and why it matters for the business
- Include one concrete detail (a number, a result, a pattern spotted)
- Close with a question or takeaway relevant to other business owners or founders
- No hashtag spam — max 3 relevant tags at the end

---

### Instagram Caption (150–250 words)

- Do NOT write a hook line — the script injects a rotating hook automatically. Start with the body (second paragraph onwards).
- Do NOT write a CTA line — the script injects a rotating CTA automatically (alternates between follow and bio link traffic goals).
- No hashtags — omit entirely. Instagram SEO does more work than hashtags per platform guidance.
- Describe the work in a relatable way — what problem, what solution
- One specific detail or result
- First person (My/Our, not Your)

---

### X / Twitter (under 280 characters)

- One punchy observation or result from the session
- No fluff, no filler
- Optional: thread prompt ("Thread: what I built today →")

---

## Step 6: Append Social Copy to Journal

After generating the social copy in Step 4, append it to the same journal file below the tasks entry.

Format to append:

```markdown
### Social Copy

**LinkedIn**

[full LinkedIn draft]

---

**Instagram**

[full Instagram draft]

---

**X / Twitter**

[full X draft]

---
```

---

## Step 7: Post Social Copy to Discord

Post the social copy as a second embed to the same Discord channel.

```bash
python3 - << 'PYEOF'
import os, json, subprocess, datetime

env_path = "scripts/.env"
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
if not url:
    print("DISCORD_WEBHOOK_URL not set — skipping social copy Discord post")
    exit(0)

payload = {
    "embeds": [{
        "title": f"Social Copy — {datetime.date.today()}",
        "color": 15844367,
        "fields": [
            {"name": "LinkedIn", "value": "[LINKEDIN_PLACEHOLDER]", "inline": False},
            {"name": "Instagram", "value": "[INSTAGRAM_PLACEHOLDER]", "inline": False},
            {"name": "X / Twitter", "value": "[TWITTER_PLACEHOLDER]", "inline": False}
        ],
        "footer": {"text": "Evolved OS"}
    }]
}

result = subprocess.run(
    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", url,
     "-H", "Content-Type: application/json",
     "-d", json.dumps(payload)],
    capture_output=True, text=True
)
print(f"Discord social copy: {result.stdout}")
PYEOF
```

**Before running:** replace the three `[*_PLACEHOLDER]` values with the drafts from Step 4. Keep each under ~1000 characters (Discord field limit).

---

## Step 8: Post to Instagram

If `image_path` was provided, run:

```bash
python3 /Users/peterbrown/evolved-workspace/scripts/post_session_social.py \
  --image "[IMAGE_PATH_PLACEHOLDER]" \
  --caption "[INSTAGRAM_CAPTION_PLACEHOLDER]"
```

**Before running:** replace `[IMAGE_PATH_PLACEHOLDER]` with the path from the user's message, and `[INSTAGRAM_CAPTION_PLACEHOLDER]` with the Instagram caption body generated in Step 5. Do NOT include a hook line — the script injects one automatically via rotation. Do NOT include hashtags.

If no image path was provided, skip this step silently.

If `IMGBB_API_KEY` is not set in `scripts/.env`, the script will print a setup message — add it first (free at imgbb.com/api).

---

## Step 9: Confirm

Report:
- Journal file path written and whether it was created or appended
- Discord session post status (sent / skipped)
- Discord social copy post status (sent / skipped)
- Instagram post status (posted / skipped — no image provided / skipped — IMGBB_API_KEY not set)
- Paste the three social drafts
