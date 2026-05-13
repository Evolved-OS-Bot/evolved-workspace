# Plan: Story Distribution — Email, Social & Member Notification

**Created:** 2026-05-07
**Status:** Implemented
**Request:** When a new member story is published via `/add-member-story`, automatically: email matched GHL contacts, notify the featured member, post to Facebook/Instagram/LinkedIn, and ensure every story page has proper OG tags for clean social sharing. All links include UTM tracking.

---

## Overview

### What This Plan Accomplishes

Adds Phase 9 to the `/add-member-story` workflow covering four things: (1) a Python script sets story content as GHL location custom values with UTM-tagged URLs, then bulk-tags matching contacts to trigger per-life-stage GHL email workflows + social posts; (2) the featured member receives a "your story is live" email prompting her to share; (3) Facebook, Instagram, and LinkedIn posts fire automatically via GHL Social Planner; (4) every story page gets Open Graph meta tags so manual shares preview correctly on any platform.

### Why This Matters

Every new member story is a high-value trust signal. The segment email reaches warm prospects at the right life stage. The member notification turns one story into organic word-of-mouth — her network is the warmest possible audience. UTM tracking shows exactly which channel converts. OG tags ensure every share looks professional regardless of how the URL is distributed.

---

## Current State

### Relevant Existing Structure

- `scripts/document_ghl.py` — established GHL API pattern (`Bearer {GHL_API_KEY}`, `services.leadconnectorhq.com`, `Version: 2021-07-28`)
- `scripts/.env` — `GHL_API_KEY`, `GHL_LOCATION_ID` already present
- GHL Location ID: `6Ku1uU0Xc45zq0KlTikJ`
- GHL contact tags (demographic): `teen`, `20/30s`, `planning pregnancy`, `pregnant`, `post partum`, `perimenopause`, `postmenopause`
- `.claude/commands/add-member-story.md` — 8-phase command to add a story; this plan adds Phase 9

### Gaps or Problems Being Addressed

- New stories are currently published silently — no outreach to matched prospects
- Goal-based GHL tags do not exist on contacts (only demographic tags), so filtering by goal is not yet possible — demographic-only for now
- No mechanism exists to pass dynamic story content into a GHL workflow email

---

## Proposed Changes

### Summary of Changes

- Create 6 GHL location custom values (story_name, story_result, story_quote, story_url_email, story_url_social, story_url_member) — done once via script
- Build 7 GHL email templates (6 per life stage + 1 "your story is live" for the featured member)
- Build 6 GHL workflows (one per life stage) in GHL UI with email + social post actions
- Write `scripts/notify_story.py` — sets UTM-tagged custom values, searches contacts, adds trigger tags, sends member notification
- Update `single-results.php` — add Open Graph meta tags using featured image + post excerpt
- Update `.claude/commands/add-member-story.md` — add Phase 9
- Update `CLAUDE.md` — document the new script

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `scripts/notify_story.py` | Sets GHL location custom values (with UTM URLs) + bulk-tags matching contacts + sends member notification |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `.claude/commands/add-member-story.md` | Add Phase 9: run notify_story.py + set post excerpt for OG |
| `single-results.php` | Add Open Graph meta tags (og:title, og:description, og:image, og:url, twitter:card) |
| `CLAUDE.md` | Document notify_story.py in scripts section |

### Files to Delete

None.

---

## Design Decisions

### Key Decisions Made

1. **GHL location custom values for story content**: Story name, result, quote, and URL are written to GHL location-level custom values before triggering. All workflow emails reference these via `{{custom_values.story_name}}` etc. This avoids contact-level field conflicts and works because all sends fire before the next story is published.

2. **Trigger-tag pattern**: The script adds a short-lived trigger tag (e.g. `notify-story-perimenopause`) to each matching contact. The GHL workflow fires on tag-added, sends the email, then removes the trigger tag. This is idempotent and reusable — the same 6 workflows handle every future story.

3. **Demographic filtering only (for now)**: GHL contacts have life stage tags but not goal tags. Filtering by demographic alone is broader but still highly relevant — a perimenopause story goes to all perimenopause-tagged contacts regardless of their goal. Goal filtering can be layered on later if goal tags are added to contacts.

4. **One workflow per life stage (6 total)**: Each workflow is permanently set up once and reused forever. The story content changes via custom values — the workflow structure never needs to change.

5. **Pregnancy: two tags, one workflow**: Both `planning pregnancy` and `pregnant` contacts receive pregnancy stories. A single workflow triggers on `notify-story-pregnancy` and the script adds that trigger tag to contacts with either demographic tag.

### Alternatives Considered

- **Resend API for sending**: Rejected — contacts already in GHL, cleaner to keep email in GHL's sending infrastructure with existing deliverability setup.
- **One workflow for all life stages with conditional branches**: Rejected — harder to maintain, harder to build in GHL UI.
- **Contact-level custom fields for story content**: Rejected — race condition risk if writing to thousands of contacts simultaneously.

### Open Questions

- **Email opt-in/unsubscribe:** GHL workflows natively respect DND status — contacts with email DND enabled will not receive the email regardless of the trigger tag being added. No additional filtering needed in the script.
- **Teen workflow:** Enable from day one — contacts tagged `teen` have already enquired about teen training and a relevant story is exactly what they need.
- **Send time**: Script sends immediately on run. Should we add a `--schedule` flag to delay to a specific time (e.g. 9am Tuesday)?

---

## Step-by-Step Tasks

### Step 1: Create GHL Location Custom Values (one-time setup script)

Write a one-time setup script that creates 4 location custom values in GHL if they don't already exist.

**Actions:**

- Write `scripts/setup_story_custom_values.py`:
  ```python
  #!/usr/bin/env python3
  """One-time setup: creates GHL location custom values for story email notifications."""
  import os, requests
  from pathlib import Path
  from dotenv import load_dotenv

  load_dotenv(Path(__file__).parent / ".env")

  API_KEY     = os.environ["GHL_API_KEY"]
  LOCATION_ID = os.environ["GHL_LOCATION_ID"]
  BASE_URL    = "https://services.leadconnectorhq.com"
  HEADERS     = {"Authorization": f"Bearer {API_KEY}", "Version": "2021-07-28",
                 "Accept": "application/json", "Content-Type": "application/json"}

  FIELDS = [
      {"name": "story_name",       "value": ""},
      {"name": "story_result",     "value": ""},
      {"name": "story_quote",      "value": ""},
      {"name": "story_url_email",  "value": ""},  # UTM: utm_source=email
      {"name": "story_url_social", "value": ""},  # UTM: utm_source=social
      {"name": "story_url_member", "value": ""},  # UTM: utm_source=member (for member notification)
  ]

  for field in FIELDS:
      r = requests.post(f"{BASE_URL}/locations/{LOCATION_ID}/customValues",
                        headers=HEADERS, json=field)
      print(field["name"], r.status_code, r.json().get("customValue", {}).get("id", r.text[:80]))
  ```
- Run it: `python3 scripts/setup_story_custom_values.py`
- Save the 4 custom value IDs to `scripts/.env` as:
  ```
  GHL_CV_STORY_NAME=<id>
  GHL_CV_STORY_RESULT=<id>
  GHL_CV_STORY_QUOTE=<id>
  GHL_CV_STORY_URL_EMAIL=<id>
  GHL_CV_STORY_URL_SOCIAL=<id>
  GHL_CV_STORY_URL_MEMBER=<id>
  ```

**Files affected:**
- `scripts/setup_story_custom_values.py` (temporary — can delete after setup)
- `scripts/.env`

---

### Step 2: Build GHL Email Templates (in GHL UI — one per life stage)

In GHL > Marketing > Emails, create 6 email templates. Use the same structure for all — only the subject line varies.

**Template structure:**

```
Subject: [Member name]'s story — for women in their [life stage]

Preview text: Real results from a real member at your stage.

---

[Header: The Evolved logo]

She could be you.

{{custom_values.story_name}} — {{custom_values.story_result}}

"{{custom_values.story_quote}}"

[Button: Read her full story → {{custom_values.story_url_email}}]

---

Limited spots are available on the waitlist. If you haven't already joined,
now is a good time.

[Button: Join the Waitlist → https://theevolvedgym.com.au]

---
[Footer: unsubscribe link, address]
```

**6 segment templates (name them clearly):**
- `Story Notification — Teen`
- `Story Notification — 20s & 30s`
- `Story Notification — Pregnancy`
- `Story Notification — Postpartum`
- `Story Notification — Perimenopause`
- `Story Notification — Postmenopause`

Note the template ID for each — needed when building workflows.

**Files affected:** GHL UI only

---

### Step 3: Build GHL Workflows (in GHL UI — one per life stage)

In GHL > Automation > Workflows, create 6 workflows. Structure for each:

```
Workflow name: Story Email — [Life Stage]

Trigger:
  Contact Tag Added
  Tag = notify-story-[stage]  (e.g. notify-story-perimenopause)

Actions:
  1. Send Email
     Template: Story Notification — [Life Stage]
     From: The Evolved <hello@theevolvedgym.com.au>

  2. Wait: 2 minutes

  3. Remove Contact Tag
     Tag: notify-story-[stage]
```

**Note:** Social post is NOT included in these 6 workflows. Because the workflow fires once per contact, a social post action here would publish once per contact in the segment (potentially 100+ duplicate posts). Social posts are handled by a dedicated single-trigger workflow — see Step 3A.

**6 workflows:**

| Workflow name | Trigger tag | Email template |
|---|---|---|
| Story Email — Teen | `notify-story-teen` | Story Notification — Teen |
| Story Email — 20s & 30s | `notify-story-2030s` | Story Notification — 20s & 30s |
| Story Email — Pregnancy | `notify-story-pregnancy` | Story Notification — Pregnancy |
| Story Email — Postpartum | `notify-story-postpartum` | Story Notification — Postpartum |
| Story Email — Perimenopause | `notify-story-perimenopause` | Story Notification — Perimenopause |
| Story Email — Postmenopause | `notify-story-postmenopause` | Story Notification — Postmenopause |

**Important:** Publish and enable all 6 workflows including Teen.

**Files affected:** GHL UI only

---

### Step 3A: Social Post — Single-Trigger Workflow (GHL UI)

Social posts cannot go inside the 6 life-stage workflows because those fire once per contact — adding a social post action there would publish a duplicate post for every contact in the segment.

Instead, create a **7th workflow** that fires once via a dedicated dummy contact:

**Setup (one-time):**
- In GHL Contacts, create or identify a staff/dummy contact (e.g. the gym's own email address)
- Note that contact's ID — you'll add a tag to it manually after each story publish

**Workflow:**
```
Workflow name: Story Social Post

Trigger:
  Contact Tag Added
  Tag = story-post-now

Actions:
  1. Create Social Media Post
     Accounts: Facebook Page, LinkedIn Page
     Body:
       "{{custom_values.story_quote}}"

       {{custom_values.story_name}} — {{custom_values.story_result}}

       Read her full story: {{custom_values.story_url_social}}

       Spots at The Evolved are by waitlist only. If this sounds like your story, join us.

       #TheEvolvedGym #WomensStrengthTraining #Brisbane #RealResults #StrengthTraining

  2. Create Social Media Post (Instagram — separate action or per-platform toggle)
     Body:
       "{{custom_values.story_quote}}"

       {{custom_values.story_name}} — {{custom_values.story_result}}

       Link in bio — read her full story.

       #TheEvolvedGym #WomensStrengthTraining #Brisbane #RealResults #StrengthTraining

  3. Wait: 1 minute

  4. Remove Contact Tag
     Tag: story-post-now
```

**How to use after each story publish:**
1. Run `notify_story.py` (sets custom values + tags email contacts)
2. In GHL > Contacts, find the dummy contact → manually add tag `story-post-now`
3. Workflow fires once → posts to Facebook, Instagram, LinkedIn → removes tag

**Files affected:** GHL UI only

---

### Step 3B: Build "Your Story Is Live" Email Template (GHL UI)

Create a 7th email template in GHL > Marketing > Emails named `Story Live — Member Notification`. This is sent directly to the featured member by the script (not via a workflow — sent via GHL Conversations API).

**Template structure:**

```
Subject: Your story is live, {{custom_values.story_name}}

Preview text: We've just published your transformation on our website.

---

[Header: The Evolved logo]

Your story is live.

{{custom_values.story_name}}, we've just published your transformation story on The Evolved website.

"{{custom_values.story_quote}}"

[Button: See your story → {{custom_values.story_url_member}}]

If you'd like to share it with friends or family, we'd love that — it might be exactly what someone close to you needs to hear.

Thank you for being part of The Evolved community.

— The Evolved Team
```

Note the template ID — needed in `notify_story.py` as `GHL_TEMPLATE_MEMBER_NOTIFY`.

Add to `scripts/.env`:
```
GHL_TEMPLATE_MEMBER_NOTIFY=<template-id>
```

**Files affected:** GHL UI only + `scripts/.env`

---

### Step 4: Write notify_story.py

**Actions:**

- Write `scripts/notify_story.py` with this logic:

```python
#!/usr/bin/env python3
"""
notify_story.py
Triggers a GHL story email notification to contacts matching a life stage tag.

Usage:
  python3 scripts/notify_story.py \
    --stage perimenopause \
    --name "Karyn" \
    --result "Lost 12kg and eliminated chronic back pain" \
    --quote "Take that first step. The change will be more profound than you imagine." \
    --url "https://theevolvedgym.com.au/results/perimenopause-weight-loss-back-pain"
"""

import os, sys, time, argparse, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
CV_IDS      = {
    "story_name":       os.environ["GHL_CV_STORY_NAME"],
    "story_result":     os.environ["GHL_CV_STORY_RESULT"],
    "story_quote":      os.environ["GHL_CV_STORY_QUOTE"],
    "story_url_email":  os.environ["GHL_CV_STORY_URL_EMAIL"],
    "story_url_social": os.environ["GHL_CV_STORY_URL_SOCIAL"],
    "story_url_member": os.environ["GHL_CV_STORY_URL_MEMBER"],
}
MEMBER_TEMPLATE_ID = os.environ["GHL_TEMPLATE_MEMBER_NOTIFY"]

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS  = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Accept":        "application/json",
    "Content-Type":  "application/json",
}

# Maps story life stage slug → (GHL demographic tags, trigger tag)
STAGE_MAP = {
    "teen":          (["teen"],                                   "notify-story-teen"),
    "20s-30s":       (["20/30s"],                                 "notify-story-2030s"),
    "pregnancy":     (["planning pregnancy", "pregnant"],         "notify-story-pregnancy"),
    "postpartum":    (["post partum"],                            "notify-story-postpartum"),
    "perimenopause": (["perimenopause"],                          "notify-story-perimenopause"),
    "postmenopause": (["postmenopause"],                          "notify-story-postmenopause"),
}


def set_custom_value(cv_id, value):
    r = requests.put(
        f"{BASE_URL}/locations/{LOCATION_ID}/customValues/{cv_id}",
        headers=HEADERS,
        json={"value": value},
    )
    if not r.ok:
        print(f"  WARN: failed to set custom value {cv_id}: {r.text[:120]}")


def search_contacts_by_tag(tag, limit=100):
    """Returns list of contact IDs with the given tag and a non-empty email."""
    contacts = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE_URL}/contacts/search",
            headers=HEADERS,
            params={"locationId": LOCATION_ID, "query": "", "tags": tag,
                    "limit": limit, "page": page},
        )
        if not r.ok:
            print(f"  WARN: search failed for tag '{tag}': {r.text[:120]}")
            break
        data = r.json()
        batch = [c for c in data.get("contacts", []) if c.get("email")]
        contacts.extend(batch)
        if len(data.get("contacts", [])) < limit:
            break
        page += 1
    return contacts


def add_tag(contact_id, tag):
    r = requests.post(
        f"{BASE_URL}/contacts/{contact_id}/tags",
        headers=HEADERS,
        json={"tags": [tag]},
    )
    return r.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage",        required=True, choices=list(STAGE_MAP.keys()))
    parser.add_argument("--name",         required=True)
    parser.add_argument("--result",       required=True)
    parser.add_argument("--quote",        required=True)
    parser.add_argument("--url",          required=True, help="Base story URL (no UTM)")
    parser.add_argument("--member-email", default=None,  help="Featured member's email for 'story is live' notification")
    parser.add_argument("--dry-run",      action="store_true", help="Preview contacts without sending")
    args = parser.parse_args()

    demographic_tags, trigger_tag = STAGE_MAP[args.stage]

    # Build UTM-tagged URLs
    name_slug = args.name.lower().replace(" ", "-")
    base = args.url.rstrip("/")
    url_email  = f"{base}?utm_source=email&utm_medium=crm&utm_campaign=story-{name_slug}"
    url_social = f"{base}?utm_source=social&utm_medium=organic&utm_campaign=story-{name_slug}"
    url_member = f"{base}?utm_source=member&utm_medium=email&utm_campaign=story-{name_slug}"

    # Step 1: Set location custom values
    print(f"Setting story custom values...")
    set_custom_value(CV_IDS["story_name"],       args.name)
    set_custom_value(CV_IDS["story_result"],     args.result)
    set_custom_value(CV_IDS["story_quote"],      args.quote)
    set_custom_value(CV_IDS["story_url_email"],  url_email)
    set_custom_value(CV_IDS["story_url_social"], url_social)
    set_custom_value(CV_IDS["story_url_member"], url_member)
    print(f"  Done.")

    # Step 2: Collect matching contacts (union of all demographic tags)
    all_contacts = {}
    for tag in demographic_tags:
        print(f"Searching contacts with tag: '{tag}'...")
        batch = search_contacts_by_tag(tag)
        for c in batch:
            all_contacts[c["id"]] = c
        print(f"  Found {len(batch)} contacts.")

    total = len(all_contacts)
    print(f"\nTotal unique contacts to notify: {total}")

    if args.dry_run:
        print("\nDRY RUN — no tags added. Contacts that would be notified:")
        for c in list(all_contacts.values())[:10]:
            print(f"  {c.get('firstName','')} {c.get('lastName','')} <{c.get('email','')}>")
        if total > 10:
            print(f"  ... and {total - 10} more.")
        return

    # Step 3: Add trigger tag to each contact
    print(f"\nAdding trigger tag '{trigger_tag}' to {total} contacts...")
    success = 0
    for i, contact in enumerate(all_contacts.values()):
        ok = add_tag(contact["id"], trigger_tag)
        if ok:
            success += 1
        else:
            print(f"  WARN: failed for {contact.get('email', contact['id'])}")
        # Rate limit: GHL API allows ~10 req/s
        if (i + 1) % 10 == 0:
            time.sleep(1)

    print(f"\nDone. {success}/{total} contacts tagged — GHL workflows will send emails.")
    print(f"Story: {args.name} — {args.url}")

    # Step 4: Send "your story is live" to the featured member
    if args.member_email:
        print(f"\nSending member notification to {args.member_email}...")
        r = requests.get(
            f"{BASE_URL}/contacts/search",
            headers=HEADERS,
            params={"locationId": LOCATION_ID, "query": args.member_email, "limit": 1},
        )
        contacts_found = r.json().get("contacts", []) if r.ok else []
        if contacts_found:
            contact_id = contacts_found[0]["id"]
            send_r = requests.post(
                f"{BASE_URL}/conversations/messages",
                headers=HEADERS,
                json={
                    "type":       "Email",
                    "contactId":  contact_id,
                    "templateId": MEMBER_TEMPLATE_ID,
                },
            )
            if send_r.ok:
                print(f"  Member notification sent.")
            else:
                print(f"  WARN: member send failed: {send_r.text[:120]}")
        else:
            print(f"  WARN: no GHL contact found for {args.member_email} — skipping member notification.")


if __name__ == "__main__":
    main()
```

**Files affected:**
- `scripts/notify_story.py`

---

### Step 5: Update /add-member-story Command

Add Phase 9 to `.claude/commands/add-member-story.md` after the current Phase 8 (flush caches):

```markdown
## Phase 9: Send Story Email Notification

Run the notify script to email matched contacts in GHL:

\`\`\`bash
python3 scripts/notify_story.py \
  --stage [life-stage-slug] \
  --name "[Member Name]" \
  --result "[One-sentence result]" \
  --quote "[Pull quote]" \
  --url "https://theevolvedgym.com.au/results/[slug]" \
  --member-email "[member@email.com]"
\`\`\`

**Dry run first to preview recipients:**
\`\`\`bash
python3 scripts/notify_story.py --stage perimenopause --name "Karyn" \
  --result "Lost 12kg and eliminated chronic back pain" \
  --quote "Take that first step." \
  --url "https://theevolvedgym.com.au/results/perimenopause-weight-loss-back-pain" \
  --member-email "karyn@example.com" \
  --dry-run
\`\`\`

**Life stage slug → GHL tags notified:**

| Story stage | Contacts notified |
|---|---|
| `teen` | Contacts tagged `teen` |
| `20s-30s` | Contacts tagged `20/30s` |
| `pregnancy` | Contacts tagged `planning pregnancy` OR `pregnant` |
| `postpartum` | Contacts tagged `post partum` |
| `perimenopause` | Contacts tagged `perimenopause` |
| `postmenopause` | Contacts tagged `postmenopause` |
```

**Files affected:**
- `.claude/commands/add-member-story.md`

---

### Step 6: Update CLAUDE.md

Add `notify_story.py` to the scripts section in CLAUDE.md.

**Files affected:**
- `CLAUDE.md`

---

### Step 7: Add Open Graph Tags to single-results.php

Every story page needs proper OG meta tags so that when anyone shares the URL — on WhatsApp, in an email, on social — it previews with the member's photo, name, and result rather than a generic site thumbnail.

The post excerpt is used as the OG description. **Update the `/add-member-story` command** to set the post excerpt to the pull quote when creating the WP post (add `--post_excerpt="[pull quote]"` to the `wp post create` call, or a follow-up `wp post update [ID] --post_excerpt="..."`).

**Add to `single-results.php` inside `<head>`, before `wp_head()`:**

```php
<?php
// Open Graph meta tags for story pages
$og_title       = get_the_title() . ' | The Evolved Brisbane';
$og_description = get_the_excerpt();
$og_image       = get_the_post_thumbnail_url(get_the_ID(), 'large');
$og_url         = get_permalink();

// Fallback description from post content if no excerpt set
if (!$og_description) {
    $content = get_the_content();
    preg_match('/<blockquote[^>]*>(.*?)<\/blockquote>/s', $content, $m);
    $og_description = $m[1] ? wp_strip_all_tags($m[1]) : get_bloginfo('description');
}

// Fallback image to site logo if no featured image
if (!$og_image) {
    $og_image = 'https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/evolved-og-default.png';
}
?>
<meta property="og:type"               content="article">
<meta property="og:title"              content="<?php echo esc_attr($og_title); ?>">
<meta property="og:description"        content="<?php echo esc_attr($og_description); ?>">
<meta property="og:image"              content="<?php echo esc_url($og_image); ?>">
<meta property="og:url"                content="<?php echo esc_url($og_url); ?>">
<meta property="og:site_name"          content="The Evolved All Female Gym">
<meta name="twitter:card"              content="summary_large_image">
<meta name="twitter:title"             content="<?php echo esc_attr($og_title); ?>">
<meta name="twitter:description"       content="<?php echo esc_attr($og_description); ?>">
<meta name="twitter:image"             content="<?php echo esc_url($og_image); ?>">
```

This block goes in the `<head>` of `single-results.php`, after the `<title>` tag and before `<?php wp_head(); ?>`.

Deploy `single-results.php` to the theme via SCP after editing.

**Files affected:**
- `/tmp/single-results.php` (edit locally, then SCP to blocksy-child theme)

---

## Connections & Dependencies

### Files That Reference This Area

- `.claude/commands/add-member-story.md` — Phase 9 added here
- `scripts/.env` — needs 4 new `GHL_CV_STORY_*` keys after Step 1 setup

### Updates Needed for Consistency

- GHL UI: 6 email templates + 6 workflows must exist before script is used
- `scripts/.env` must have custom value IDs populated before first run

### Impact on Existing Workflows

None — purely additive. Existing story publishing is unaffected if Phase 9 is skipped.

---

## Validation Checklist

- [ ] `setup_story_custom_values.py` runs without error, 6 IDs saved to `.env`
- [ ] GHL location shows 6 custom values: `story_name`, `story_result`, `story_quote`, `story_url_email`, `story_url_social`, `story_url_member`
- [ ] 6 segment email templates exist in GHL > Marketing > Emails (one per life stage)
- [ ] 1 member notification template exists: `Story Live — Member Notification`
- [ ] 6 workflows exist in GHL > Automation > Workflows (one per life stage), all published and active
- [ ] `python3 scripts/notify_story.py --stage perimenopause ... --dry-run` lists contacts correctly
- [ ] Test send: run without `--dry-run` for a single small-tag segment; verify email arrives with UTM-tagged URL, trigger tag removed after workflow completes
- [ ] Email URL contains `utm_source=email` — confirm in browser on receipt
- [ ] Social URL contains `utm_source=social` — confirm in published post
- [ ] Featured member receives "your story is live" email with `utm_source=member` link
- [ ] Social posts publish to Facebook, Instagram, LinkedIn after workflow completes
- [ ] Instagram caption uses "link in bio" (no raw URL in caption)
- [ ] Facebook and LinkedIn posts include `story_url_social` with UTM params
- [ ] Story page shows correct OG preview when URL is pasted into Facebook debugger (developers.facebook.com/tools/debug)
- [ ] OG image is the member's featured photo (not a generic placeholder)
- [ ] `/add-member-story` command updated with Phase 9 including `--member-email` arg
- [ ] `single-results.php` deployed to blocksy-child theme

---

## Success Criteria

1. Running `notify_story.py` sends a personalised UTM-tagged email to all matched GHL contacts, publishes to Facebook/Instagram/LinkedIn, and sends a "your story is live" notification to the featured member — all from a single command.
2. The trigger tag is automatically removed after sending — workflows are ready for the next story with no manual reset.
3. The `--dry-run` flag previews recipients safely before committing to a live send.
4. Every story page previews correctly when its URL is shared on any platform — correct member photo, name, and result blurb pulled automatically.
5. All traffic from each channel is trackable via UTM parameters in GA4/analytics from day one.

---

## Notes

- **Goal-tag filtering**: Not possible yet — GHL contacts have demographic tags only. If goal tags are added to contacts in future (`weight-loss`, `aesthetics`, etc.), the `STAGE_MAP` in the script can be extended to a combined filter.
- **Rate limiting**: The script pauses 1 second per 10 contacts to stay within GHL's API limits (~10 req/s). For large segments this may take a few minutes — that's fine, the emails send asynchronously via GHL workflows.
- **Duplicate protection**: If a contact already has the trigger tag (e.g. from a failed workflow), GHL silently ignores the duplicate tag-add. The workflow fires once per tag-added event, so no double sends.
- **Email deliverability**: Emails send from GHL's infrastructure using your existing sending domain — same deliverability profile as your current GHL campaigns.
- **Future: schedule flag**: Could add `--schedule "2026-05-08 09:00"` to delay the tag-add to a specific time. Not in scope for v1.

---

## Implementation Notes

**Implemented:** 2026-05-07

### Summary

- Created `scripts/setup_story_custom_values.py` — one-time GHL setup script
- Created `scripts/notify_story.py` — full notification script with UTM URLs, contact tagging, and member email
- Added Phase 9 to `.claude/commands/add-member-story.md`
- Added OG meta tags to `single-results.php` (reusing existing `$title`, `$content`, `$thumb_url` variables) and deployed to SiteGround
- Updated `CLAUDE.md` to document both new scripts

### Deviations from Plan

- OG tags use the already-computed `$thumb_url` (fetched as 'full' size at the top of the template) rather than re-fetching as 'large' — equivalent result, avoids redundant DB query.

### Issues Encountered

None — single-results.php was not in the local workspace so was fetched from SiteGround via SCP before editing.
