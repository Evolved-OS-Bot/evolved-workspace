# Plan: Instagram Story Repurposer
**Created:** 2026-04-27
**Status:** Scoped — Not Started

---

## Objective

Build an automated pipeline that captures Instagram Stories from the gym account before they expire, filters for Reel-worthy content, surfaces candidates to Discord for human approval, and posts approved stories as Reels — with optional burned-in captions. Target output: 3–5 Reels per week. No bulk posting, no slop. Curation is human; distribution is automated.

---

## Why This Works

Stories and Reels share the same vertical format (9:16). A story that performs — a technique clip, a client moment, a behind-the-scenes — is already a Reel. The only things missing are discoverability (Reels reach non-followers, stories don't), captions (for watch-without-sound viewers), and a good caption + hashtags. This system adds all three with minimal friction.

---

## Content Worth Repurposing

Claude filters for these categories:

| Category | Examples |
|---|---|
| Workout demos | Exercise execution, form cues, movement patterns |
| Technique clips | Coaching corrections, mobility tips, progressions |
| Client moments | Milestones, PRs, transformations (with consent implied by story post) |
| Behind the scenes | Gym culture, trainer moments, session energy |
| Tips | Nutrition, training, mindset, recovery |

Filtered out: promotional stories, text-only graphics, low-quality footage, stories under 5 seconds.

---

## Architecture

### Two-Component System

**Component 1 — Railway Cron (`story_repurposer/`)**
- Runs every 3 hours
- Fetches new stories from Instagram Graph API
- Downloads video files to temporary storage
- Claude quality filter — scores and categorises each story
- Worthy stories posted to `#reel-candidates` Discord channel via webhook
- Claude generates suggested Reel caption + hashtags

**Component 2 — Local Discord Bot extension**
- Watches `#reel-candidates` for reactions (same bot.py pattern as admin drafts)
- ✅ = queue story as-is
- 🎬 = transcribe audio → burn captions → queue
- ❌ = discard
- Queue manager schedules posting into 3–5 optimal slots per week
- Whisper API transcription + ffmpeg caption burning (runs locally on Mac)
- Instagram Graph API: upload video → wait for processing → publish Reel
- Posts confirmation to `#reel-published`

### File Structure

```
story_repurposer/              — Railway service
  app.py                       — Flask app (also serves video files for Instagram pull)
  story_fetcher.py             — Instagram Graph API: fetch stories, download videos
  quality_filter.py            — Claude quality assessment and categorisation
  discord_poster.py            — Post candidates + captions to #reel-candidates webhook
  token_manager.py             — Instagram long-lived token storage and refresh
  requirements.txt
  railway.toml                 — cron: every 3 hours

discord_bot/
  story_approver.py            — Reaction handler for #reel-candidates (new module)
  reel_queue.py                — Queue management, scheduling, posting trigger
  caption_processor.py         — Whisper transcription + ffmpeg caption burning
  (bot.py)                     — Add imports + on_raw_reaction_add for reel-candidates
```

---

## Instagram API Setup (Manual Prerequisite — Step 1)

This must be completed before any code is written.

**Required:**
1. Create a Meta Developer App at developers.facebook.com
2. Add Instagram product (Graph API)
3. Connect the gym's Instagram account (must be linked to a Facebook Page)
4. Request permissions:
   - `instagram_basic` — read profile and media
   - `instagram_manage_insights` — access stories endpoint
   - `instagram_content_publish` — publish Reels
5. Generate a User Access Token with all three permissions
6. Exchange for a Long-Lived Token (valid 60 days, auto-refreshed by `token_manager.py`)

**Notes:**
- Since we're accessing only the gym's own account (owner = app admin), no Meta App Review required — Basic Access covers single-account use
- The Facebook Page link is required even for Creator accounts to use the Graph API
- Token refresh must be automated — manual renewal every 60 days is a failure point

**Instagram Reel video specs (stories already meet these):**
- Format: MP4 (H.264), AAC audio
- Aspect ratio: 9:16 (vertical — stories already are)
- Duration: 3–90 seconds
- Max file size: 1GB

---

## Full Pipeline Flow

```
Railway cron fires (every 3 hours)
      │
      ▼
story_fetcher.py
  GET /me/stories (Instagram Graph API)
  Filter: only new stories since last run (track last_fetched timestamp in SQLite)
  Filter: VIDEO type only (images skipped)
  Filter: duration > 5 seconds
  Download video files to /tmp on Railway
      │
      ▼
quality_filter.py (Claude)
  For each story video:
    - Analyse story caption/text (if present)
    - Analyse video thumbnail (multimodal — Claude vision)
    - Classify into content category (workout demo / technique / client moment / BTS / tip)
    - Score Reel-worthiness (worthy / not worthy)
    - Generate rationale (shown in Discord for context)
  Filter: not worthy → discard, log
      │
      ▼
For worthy stories:
  Claude generates:
    - Reel caption (2–3 lines, The Evolved tone, no hashtags in caption body)
    - 5–8 hashtags (mix of niche + broad fitness)
  Story video now served at:
    https://[railway-app].railway.app/media/{story_id}.mp4
      │
      ▼
discord_poster.py
  POST to #reel-candidates webhook:
    Embed:
      Title: "📹 Reel Candidate — [Category] — [Date Time AEST]"
      Fields:
        - Duration: [X]s
        - Category: [Workout Demo / Technique / etc.]
        - Why it works: [Claude rationale]
        - Suggested caption: [caption text]
        - Hashtags: [hashtag list]
      Footer: story_id:{id} (parsed by bot on reaction)
    Video: attached or linked
    Reactions key: "✅ Post as-is   🎬 Burn captions   ❌ Skip"
      │
      ▼
Peter reacts in Discord
      │
      ├─ ❌ → Bot deletes message. Done.
      │
      ├─ ✅ → story_approver.py
      │         Download video from Railway URL
      │         Add to reel_queue (status: queued, no_captions)
      │         Bot replies: "Queued — posts [Day] at [Time] AEST"
      │         Message deleted from #reel-candidates
      │
      └─ 🎬 → story_approver.py
                Download video from Railway URL
                caption_processor.py:
                  1. Whisper API → transcribe audio → SRT file
                  2. ffmpeg → burn subtitles into video (white text, black outline, bottom third)
                Add to reel_queue (status: queued, has_captions)
                Bot replies: "Captioned and queued — posts [Day] at [Time] AEST"
                Message deleted from #reel-candidates
      │
      ▼
reel_queue.py scheduler (checks every 30 mins)
  Is a Reel due now?
    NO → wait
    YES → pull next from queue
      │
      ▼
instagram_publisher.py
  1. POST /me/media (create Reel container)
     video_url: [public URL of processed video]
     media_type: REELS
     caption: [suggested caption + hashtags]
  2. Poll GET /{media_id}?fields=status_code until FINISHED (max 5 min)
  3. POST /me/media_publish
     creation_id: {media_id}
  4. Mark queue item as posted
  5. Post to #reel-published: "✅ Reel posted — [caption preview]"
  6. Cleanup: delete local video file
      │
      ▼
DONE
```

---

## Scheduling Logic

**Target:** 3–5 Reels per week, minimum 1 day apart, no more than 1 per day.

**Optimal posting slots (AEST):**

| Day | Time | Rationale |
|---|---|---|
| Tuesday | 7:00am | Start of week, morning scroll |
| Wednesday | 12:00pm | Midweek lunchtime |
| Thursday | 6:00pm | Post-work browse |
| Friday | 7:00am | Pre-weekend motivation |
| Saturday | 9:00am | Weekend leisure scroll |

When a Reel is approved:
1. Check how many Reels posted this week (Mon–Sun)
2. If week count < 5: assign next available optimal slot
3. If week is full: assign to first available slot next week
4. If queue is backing up (> 5 items pending): bot notifies Peter in Discord

---

## Caption Burning (🎬 path)

**Transcription:** OpenAI Whisper API
- Model: `whisper-1`
- Output: SRT subtitle file
- Cost: ~$0.006/minute — negligible for short clips

**Burning:** ffmpeg subtitles filter
```
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='
  FontName=Arial,FontSize=18,PrimaryColour=&Hffffff,
  OutlineColour=&H000000,Outline=2,Alignment=2'" output.mp4
```

Style: white text, black outline, bottom-centre, clean sans-serif. Readable on any background. No animations or effects.

**When captions aren't needed:**
Clips with clear on-screen text, music-only, or content that works silent (pure movement demos) are better posted raw. This is the ✅ path — same quality, less processing.

---

## SQLite Schema

```sql
-- Reel posting queue
CREATE TABLE reel_queue (
    id                  TEXT PRIMARY KEY,
    story_id            TEXT,
    video_path          TEXT,
    caption             TEXT,
    hashtags            TEXT,
    has_burned_captions INTEGER DEFAULT 0,
    status              TEXT,     -- queued, processing, posted, failed
    approved_at         TEXT,
    scheduled_for       TEXT,
    posted_at           TEXT,
    instagram_media_id  TEXT
);

-- Tracks last story fetch to avoid re-processing
CREATE TABLE fetch_state (
    key     TEXT PRIMARY KEY,
    value   TEXT
);

-- Instagram token storage
CREATE TABLE instagram_token (
    id          INTEGER PRIMARY KEY DEFAULT 1,
    access_token TEXT,
    expires_at  TEXT,
    updated_at  TEXT
);
```

---

## Instagram API Calls

| Action | Method | Endpoint |
|---|---|---|
| Fetch stories | GET | `/me/stories?fields=id,media_type,media_url,timestamp,caption` |
| Create Reel container | POST | `/{ig-user-id}/media` |
| Check processing status | GET | `/{ig-media-id}?fields=status_code` |
| Publish Reel | POST | `/{ig-user-id}/media_publish` |
| Refresh long-lived token | GET | `/refresh_access_token?grant_type=ig_refresh_token&access_token={token}` |

---

## Token Management

Long-lived tokens expire after 60 days. `token_manager.py` refreshes automatically:
- Refresh window: token is refreshed when < 10 days from expiry
- Railway cron checks token expiry on every run
- New token stored in SQLite `instagram_token` table
- Alert posted to Discord if refresh fails (manual intervention required before expiry)

---

## Environment Variables

**Railway (story_repurposer service):**
```
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_USER_ID
ANTHROPIC_API_KEY
DISCORD_REEL_CANDIDATES_WEBHOOK_URL
RAILWAY_PUBLIC_URL    — base URL for serving video files to Instagram
```

**Local bot (discord_bot/.env):**
```
REEL_CANDIDATES_CHANNEL_ID
REEL_PUBLISHED_CHANNEL_ID
OPENAI_API_KEY        — for Whisper transcription
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_USER_ID
```

---

## Discord UX

### #reel-candidates embed
```
📹 Reel Candidate — Technique Clip — Mon 27 Apr at 9:14am

Duration: 28s
Category: Technique Clip
Why it works: Clear coaching cue on hip hinge with good contrast and lighting.
              High watch-without-sound value.

Suggested caption:
The hinge is everything. Getting this right transfers to every pull,
every squat, and every lift that follows.

Hashtags: #strengthtraining #hippinge #personaltraining #theevolvedgym
          #womenswholifts #brisbanegym #strengthcoach #movementcoach

✅ Post as-is   🎬 Burn captions   ❌ Skip
```

### After approval (bot reply, auto-deletes after 10s)
```
✅ Queued — scheduled for Thursday 1 May at 6:00pm AEST
```

### #reel-published confirmation
```
✅ Reel posted — "The hinge is everything..."
Thursday 1 May at 6:00pm AEST
```

---

## Build Order

| Step | Task | Status |
|---|---|---|
| 1 | Meta Developer App setup — create app, connect Instagram, get permissions, generate long-lived token | ⬜ To Do (manual) |
| 2 | Confirm Facebook Page is linked to gym Instagram account | ⬜ To Do (manual) |
| 3 | Create `#reel-candidates` and `#reel-published` Discord channels, copy channel IDs, create webhook | ⬜ To Do (manual) |
| 4 | Railway service skeleton — Flask app, health check, `/media/{id}` file serving endpoint | ⬜ To Do |
| 5 | `token_manager.py` — token storage in SQLite, refresh logic, Discord alert on failure | ⬜ To Do |
| 6 | `story_fetcher.py` — fetch stories, filter VIDEO + duration, download to /tmp, track last_fetched | ⬜ To Do |
| 7 | `quality_filter.py` — Claude multimodal quality assessment, category classification, rationale | ⬜ To Do |
| 8 | `discord_poster.py` — build embed, attach video, post to webhook | ⬜ To Do |
| 9 | Railway cron wired up — schedule every 3 hours | ⬜ To Do |
| 10 | Local bot: `caption_processor.py` — Whisper API transcription + ffmpeg subtitle burn | ⬜ To Do |
| 11 | Local bot: `reel_queue.py` — SQLite queue CRUD, scheduling logic, weekly count tracking | ⬜ To Do |
| 12 | Local bot: `story_approver.py` — reaction handler (✅/🎬/❌), queue insertion, bot reply | ⬜ To Do |
| 13 | `instagram_publisher.py` — create container, poll status, publish, cleanup | ⬜ To Do |
| 14 | Wire `story_approver` into `bot.py` — import + `on_raw_reaction_add` for reel-candidates channel | ⬜ To Do |
| 15 | Test: story fetch and quality filter — confirm worthy stories surface in Discord | ⬜ To Do |
| 16 | Test: ✅ path — approve a story, confirm it queues and posts correctly | ⬜ To Do |
| 17 | Test: 🎬 path — confirm Whisper transcribes, ffmpeg burns captions, Reel posts with captions | ⬜ To Do |
| 18 | Test: scheduling — approve 6 stories, confirm 5th and 6th push to following week | ⬜ To Do |
| 19 | Test: token refresh — manually expire token, confirm refresh fires and Discord alert works | ⬜ To Do |
| 20 | Monitor first 2 weeks — review Claude quality filter decisions, tune prompt if needed | ⬜ To Do |

---

## Dependencies

- Meta Developer App + Instagram Graph API access (Step 1 — blocks everything)
- Facebook Page linked to gym Instagram (Step 2 — blocks API access)
- OpenAI API key — for Whisper transcription (new, not currently in use)
- ffmpeg — must be installed on local Mac (`brew install ffmpeg`)
- Anthropic API key — already in use
- Railway account — already active

---

## Notes

- **3-hour cron cadence** captures stories well within the 24-hour window even if posted at night. A story posted at 11pm is captured by the 2am run.
- **Video served from Railway for Instagram pull** — Instagram's API fetches video from a public URL during container creation. Railway Flask serves the file, Instagram pulls it, then it's deleted after successful publish. No additional cloud storage needed at current volume.
- **Claude vision for quality filter** — thumbnail analysis lets the filter assess lighting, framing, and content type even when the story has no caption. This catches the majority of gym content which is visual rather than text-based.
- **Whisper runs as API call, not locally** — keeps local bot dependencies simple. At ~30 clips/week average duration 20s, cost is < $0.05/month.
- **ffmpeg runs locally on Mac** — no Railway compute cost, no file size concerns, processes in seconds.
- **Trainer-tagged stories** — trainers tagging the gym account creates a mention notification. Tapping "Add to your story" on that notification reshares it to the gym account's own story feed, which the pipeline captures within the next 3-hour window. The reshare decision is a natural first-pass quality filter — only stories worth resharing enter the pipeline at all. Claude's quality filter is then a second pass. No extra steps needed beyond what is likely already normal behaviour.
- **Future: auto-schedule by performance** — once Reel insights are available via API, the scheduler could learn which days/times perform best and optimise slot selection automatically.
- **Future: image stories** — some tip graphics or quote cards work well as Reel cover images paired with music. Not in scope now but the filter is already classifying content type.
