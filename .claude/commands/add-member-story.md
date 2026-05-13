# Add Member Story

Add a new member transformation to every surface across the website: individual story page, /results/ hub, homepage carousel, homepage.js personalisation data, and member-stories.md master record.

## Variables

member_input: (Paste the member details here — name, age/decade, life stage, goal, key results, quote, photo filename, YouTube URL if applicable, and any story notes or transcript)

---

## Pre-Flight: What You Need

Before running, confirm you have:
- [ ] Member's first name
- [ ] Life stage: `20s-30s` | `perimenopause` | `postmenopause` | `postpartum` | `pregnancy`
- [ ] Decade (for homepage carousel): `20s` | `30s` | `40s` | `50s` | `60s`
- [ ] Goal(s) for hub filter: `weight-loss` `aesthetics` `strength` `mental-health` `energy` `hormonal-health` `bone-health` `return-to-fitness`
- [ ] Goal for homepage carousel: `lose-weight` | `recomp` | `gain-muscle` | `get-stronger` | `bone-density`
- [ ] Photo filename (e.g. `sarah-30s-6m.png`) — or YouTube ID if video-only
- [ ] YouTube video ID (optional — e.g. `dQw4w9WgXcQ`)
- [ ] One-sentence result blurb for hub card
- [ ] Pull quote (the featured blockquote)
- [ ] 3 key result stats for the bottom of the story page

Note: The WP slug is generated from the member details — you do not need to provide it. Claude will derive a descriptive slug from life stage, goal, and name/context.

If YouTube video provided: use the `pull-video-transcripts` skill first to get a clean transcript before writing the story.

---

## Phase 1: Pull Transcript (if YouTube)

Use the `pull-video-transcripts` skill with the YouTube URL. Save clean text for story writing.

---

## Phase 2: Write the Story HTML

Write to `/tmp/story-[name-lowercase].html`. Use this exact structure:

```html
<div class="ev-pull-quote">
  <span class="ev-quote-mark">&#8220;</span>
  <blockquote>[Pull quote — compelling, specific, 1–2 sentences]</blockquote>
  <p class="attribution">[Name] &mdash; [Age/Label], Brisbane</p>
</div>

<!-- VIDEO EMBED — include only if YouTube ID available -->
<div style="background:#0a0a0a;padding:48px 32px;">
  <div style="max-width:700px;margin:0 auto;">
    <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:8px;">
      <iframe style="position:absolute;top:0;left:0;width:100%;height:100%;"
        src="https://www.youtube.com/embed/[YOUTUBE_ID]"
        frameborder="0" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
        allowfullscreen title="[Name] — The Evolved Brisbane"></iframe>
    </div>
  </div>
</div>

<div class="ev-story-body">
  <div class="ev-story-body-inner">

    <p>[Opening paragraph — who she is, what brought her in, the moment things changed]</p>

    <p>[What happened — specific results, timeline, what shifted]</p>

    <h3>[Educational H3 — explain the mechanism behind her result]</h3>

    <p>[Evidence-based paragraph — why this works, the science in plain language]</p>

    <h3>[Second H3 — a second angle, e.g. community/environment/age]</h3>

    <p>[Her direct quote + expansion]</p>

    <h3>[Third H3 — longer-term implication, e.g. bone density, independence, longevity]</h3>

    <p>[Closing insight — what she's building beyond the obvious result]</p>

  </div>
</div>

<div class="ev-key-results">
  <h2>[Name]&rsquo;s Results</h2>
  <div class="ev-key-results-grid">
    <div class="ev-result-stat">
      <span class="stat-number">[Stat 1 — e.g. 20kg lost]</span>
      <span class="stat-label">[One-line context]</span>
    </div>
    <div class="ev-result-stat">
      <span class="stat-number">[Stat 2]</span>
      <span class="stat-label">[One-line context]</span>
    </div>
    <div class="ev-result-stat">
      <span class="stat-number">[Stat 3]</span>
      <span class="stat-label">[One-line context]</span>
    </div>
  </div>
</div>
```

**Writing rules:**
- Use `&mdash;` for em dashes, `&rsquo;` for apostrophes, `&ldquo;`/`&rdquo;` for quotes
- No invented details — only what the member actually said or what's documented
- H3s should be educational/informative, not just descriptive (e.g. "Why Strength Beats Cardio After 40" not "Her Journey")
- 3–4 body paragraphs minimum, 2–3 H3 sections

---

## Phase 3: Upload Photo (if photo available)

```bash
scp /path/to/[photo-filename].png \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/uploads/2026/04/[photo-filename].png
```

---

## Phase 4: Create WordPress Results CPT Page

```bash
# Create the post
ssh evolved-prod "
cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
wp post create \
  --post_type=results \
  --post_status=publish \
  --post_title='[Member Name] — [Short descriptor]' \
  --post_name='[slug]' \
  --porcelain
"
# Note the post ID returned

# Upload story HTML
scp /tmp/story-[name].html \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/story-[name].html

# Write content + set taxonomies
ssh evolved-prod "
cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
wp eval '
  global \$wpdb;
  \$wpdb->update(\$wpdb->posts,
    [\"post_content\" => file_get_contents(\"story-[name].html\")],
    [\"ID\" => [POST_ID]]
  );
  wp_set_object_terms([POST_ID], [\"[goal-slug]\"], \"goal\");
  wp_set_object_terms([POST_ID], [\"[life-stage-slug]\"], \"life_stage\");
  echo \"Done\";
'
"

# Register featured image (if photo available — file must already be on server)
ssh evolved-prod "
cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
wp eval '
  \$file = \"/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/uploads/2026/04/[photo-filename].png\";
  \$upload_dir = wp_upload_dir();
  \$attachment = [
    \"guid\"           => \$upload_dir[\"url\"] . \"/[photo-filename].png\",
    \"post_mime_type\" => \"image/png\",
    \"post_title\"     => \"[Member Name] transformation\",
    \"post_content\"   => \"\",
    \"post_status\"    => \"inherit\"
  ];
  \$attach_id = wp_insert_attachment(\$attachment, \$file, [POST_ID]);
  require_once ABSPATH . \"wp-admin/includes/image.php\";
  \$data = wp_generate_attachment_metadata(\$attach_id, \$file);
  wp_update_attachment_metadata(\$attach_id, \$data);
  set_post_thumbnail([POST_ID], \$attach_id);
  echo \"Attachment ID: \" . \$attach_id;
'
"
```

---

## Phase 5: Update archive-results.php

Open `/tmp/archive-results.php` and add a new entry to `$members` in the correct life-stage group:

```php
['name'=>'[Name]', 'label'=>'[Label, e.g. "2 Kids, 30s"]', 'result'=>'[One-sentence result blurb]',
 'goals'=>'[goal-slug] [optional-second-goal]', 'stage'=>'[life-stage-slug]',
 'color'=>'[section-color]', 'photo'=>$p.'[photo-filename].png',
 'link'=>'/results/[slug]'],
```

**Section colours:**
- `20s-30s`: `#0e1628`
- `postpartum`: `#0a1820`
- `pregnancy`: `#0a1508`
- `perimenopause`: `#1a0e28`
- `postmenopause`: `#1f0a15`

**For video-only (no photo):** use YouTube thumbnail:
```php
'photo'=>'https://img.youtube.com/vi/[YOUTUBE_ID]/hqdefault.jpg',
```

Then deploy:
```bash
scp /tmp/archive-results.php \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/archive-results.php
```

---

## Phase 6: Update Homepage Carousel (homepage-v5.html)

Open `/tmp/homepage-v5.html` and add a new `carousel-card` inside `.carousel-track`.

```html
<div class="carousel-card" data-goal="[carousel-goal]" data-decade="[decade]" data-stage="[life-stage-or-omit]" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/[photo-filename].png" alt="[Name] transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">[Name], [Short label]</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">[2–3 sentence story blurb]</p>
</div>
```

**`data-stage` rules — REQUIRED for stage-based carousel sorting:**
- `pregnancy` or `postpartum` members → `data-stage="pregnancy"`
- `perimenopause` members → `data-stage="perimenopause"`
- `postmenopause` members → `data-stage="postmenopause"`
- `20s-30s` members → omit `data-stage` (decade scoring handles it)

**Carousel goal values:** `lose-weight` | `recomp` | `gain-muscle` | `get-stronger` | `bone-density`

**For video-only members:** use the YouTube thumbnail URL in place of the wp-content path.

Then deploy:
```bash
scp /tmp/homepage-v5.html \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/homepage-v5.html

ssh evolved-prod "
cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
wp eval 'global \$wpdb; \$wpdb->update(\$wpdb->posts, [\"post_content\" => file_get_contents(\"homepage-v5.html\")], [\"ID\" => 165]);'
"
```

---

## Phase 7: Update homepage.js Personalisation Data

Open `/tmp/homepage.js`. Four objects need checking/updating. Then deploy JS with a version bump.

### 7A. PYJ_STORY_PHOTOS — Always add

This powers the photo shown in the PYJ confirm panel (Step 3) and the Results Curve "Based on Your Profile" card. **Add for every new member with a photo.**

Find `const PYJ_STORY_PHOTOS = {` and add:

```js
"[Name]": "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/[photo-filename].png",
```

For video-only members use the YouTube thumbnail:
```js
"[Name]": "https://i.ytimg.com/vi/[YOUTUBE_ID]/hqdefault.jpg",
```

### 7B. RC_PROFILE_STORIES — Update if best story for a slot

This is the "Based on your profile" card shown below the Results Curve chart. One story per goal × decade combination. **Only update if this member is a stronger example than the current entry for their goal+decade.**

Find `const RC_PROFILE_STORIES = {`, locate the matching goal block and decade key, and replace or add:

```js
"[decade]": { name: "[Name]", blurb: "[2–3 sentence blurb — specific result + emotional hook]", anchor: ".carousel-viewport" },
```

Use `anchor: ".video-viewport"` if member has a video testimonial.

### 7C. transformationCards — Update stage arrays if relevant

This controls the "MORE RESULTS FROM THIS DECADE" photo grid (always shows 3). Stage-specific arrays take priority over decade arrays when a life stage is selected.

Find `const transformationCards = {` and update the relevant array:

- Pregnancy/postpartum → add to `"pregnancy": [...]` array (keep best 3)
- Perimenopause → add to `"perimenopause": [...]` array (keep best 3)
- Post-menopause → add to `"postmenopause": [...]` array (keep best 3)
- Other decades → add to `"[decade]": [...]` array (keep best 3)

```js
{ src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/[photo-filename].png", alt: "[Name]'s transformation", caption: "[Name] — [duration]" },
```

### 7D. transformationImages — Update stage hero if this is a stronger visual

This controls the single large transformation photo shown in the "Why Muscle Matters" section when a life stage is selected. Only update if this member's photo is more compelling than the current one for their stage.

Find `const transformationImages = {` and update the relevant key:

```js
"[stage-or-decade]": { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/[photo-filename].png", alt: "[Name]'s transformation at The Evolved", caption: "[Name] — [duration]" },
```

Stage keys: `"pregnancy"` | `"perimenopause"` | `"postmenopause"`
Decade keys: `"20s"` | `"30s"` | `"40s"` | `"50s"` | `"60s"`

### Deploy homepage.js

After all JS changes, bump the version number and deploy:

```bash
scp /tmp/homepage.js \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/js/homepage.js

ssh evolved-prod "
  # Increment version number (e.g. 54.0 → 55.0)
  sed -i 's/homepage\.js\", \[\"gsap\", \"gsap-scrolltrigger\", \"chartjs\"\], \"[0-9]*\.[0-9]*/homepage.js\", [\"gsap\", \"gsap-scrolltrigger\", \"chartjs\"], \"[NEW_VERSION]/' \
  /home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/functions.php
"
```

---

## Phase 8: Update reference/member-stories.md

Add a new entry to the master record. Find the correct life-stage section and append:

```markdown
### [Name] — [Life Stage Label]

- **Decade:** [e.g. 30s]
- **Driver:** [e.g. Weight loss, postpartum recovery]
- **Duration:** [e.g. 6 months]
- **Key results:** [e.g. Lost 12kg, eliminated back pain]
- **Quote:** "[Pull quote]"
- **YouTube:** [ID or "none"]
- **Photo:** [filename or "none"]
- **WP post ID:** [ID]
- **Slug:** `/results/[slug]`
```

---

## Phase 9: Flush Caches

```bash
ssh evolved-prod "
cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
wp cache flush && wp transient delete --all && wp sg purge
"
```

---

## Phase 10: Send Story Email Notification

**Step 1 — dry run first to confirm contact count:**
```bash
python3 scripts/notify_story.py \
  --stage [life-stage-slug] \
  --name "[Member Name]" \
  --result "[One-sentence result]" \
  --quote "[Pull quote]" \
  --url "https://theevolvedgym.com.au/results/[slug]" \
  --dry-run
```

Confirm `Total unique contacts to notify: X` is > 0 before proceeding.

**Step 2 — run live to tag contacts and trigger emails:**
```bash
python3 scripts/notify_story.py \
  --stage [life-stage-slug] \
  --name "[Member Name]" \
  --result "[One-sentence result]" \
  --quote "[Pull quote]" \
  --url "https://theevolvedgym.com.au/results/[slug]" \
  --member-email "[member@email.com]"
```

The script tags each matching contact with the trigger tag → GHL workflow fires the email → tag is removed after 2 minutes. Check GHL Automation → Workflows → Enrollment History to confirm contacts enrolled.

**Life stage slug → GHL tags notified:**

| Story stage | Contacts notified |
|---|---|
| `teen` | Contacts tagged `teen` |
| `20s-30s` | Contacts tagged `20/30s` |
| `pregnancy` | Contacts tagged `planning pregnancy` OR `pregnant` |
| `postpartum` | Contacts tagged `post partum` |
| `perimenopause` | Contacts tagged `perimenopause` |
| `postmenopause` | Contacts tagged `postmenopause` |

Then post to Facebook and Instagram:

```bash
python3 scripts/post_story_social.py \
  --name "[Member Name]" \
  --result "[One-sentence result]" \
  --quote "[Pull quote]" \
  --url "https://theevolvedgym.com.au/results/[slug]" \
  --image-url "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/[photo-filename].png"
```

Dry run first:
```bash
python3 scripts/post_story_social.py --name "Karyn" --result "Lost 12kg" \
  --quote "Take that first step." \
  --url "https://theevolvedgym.com.au/results/perimenopause-weight-loss-back-pain" \
  --image-url "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-photo.png" \
  --dry-run
```

**Prerequisites:** GHL custom values and workflows must be set up first (see `plans/2026-05-07-story-email-notification.md` Steps 1–3A).

---

## Validation Checklist

**Story page**
- [ ] `/results/[slug]` loads with two-column hero (photo) or full-width fallback (video-only)
- [ ] Video embed plays on the story page (if applicable)
- [ ] Pull quote, stats, and body copy render correctly

**Results hub**
- [ ] `/results/` hub shows the new card with correct photo/thumbnail
- [ ] Hub card links to `/results/[slug]`
- [ ] Goal filter shows the card under the correct goal(s)
- [ ] Life stage filter shows the card correctly

**Homepage carousel**
- [ ] Card appears in the carousel
- [ ] Selecting the matching life stage (pregnancy/perimenopause/postmenopause) surfaces this card in the top 3
- [ ] Selecting matching goal + decade surfaces this card near the top for non-stage selections

**Homepage interactive personalisation (homepage.js)**
- [ ] PYJ confirm panel shows this member's photo when their stage+goal is selected (7A)
- [ ] Results Curve "Based on your profile" card shows this member for their goal+decade (7B — if updated)
- [ ] "More results from this decade" shows 3 photos including this member for their stage (7C — if updated)
- [ ] "Why Muscle Matters" section shows this member's photo for their stage (7D — if updated)

**Records**
- [ ] `reference/member-stories.md` updated
- [ ] All caches flushed

---

## Quick Reference: Life Stage → Hub Stage Slug

| Life Stage | `stage` value in archive | `data-stage` on carousel card |
|---|---|---|
| 20s | `20s-30s` | omit |
| 30s | `20s-30s` | omit |
| Pregnancy | `pregnancy` | `pregnancy` |
| Postpartum | `postpartum` | `pregnancy` |
| Perimenopause | `perimenopause` | `perimenopause` |
| Post-menopause | `postmenopause` | `postmenopause` |

## Quick Reference: Goal → Hub Filter Slug

| Goal | `goals` value |
|---|---|
| Weight loss | `weight-loss` |
| Body recomposition | `aesthetics` |
| Get stronger | `strength` |
| Mental health | `mental-health` |
| Energy | `energy` |
| Hormonal health | `hormonal-health` |
| Bone health | `bone-health` |
| Return to fitness | `return-to-fitness` |

## Quick Reference: homepage.js Objects

| Object | What it controls | Update rule |
|---|---|---|
| `PYJ_STORY_PHOTOS` | Photo in PYJ confirm + RC profile card | Always add |
| `RC_PROFILE_STORIES` | "Based on your profile" panel below curve | If best for goal×decade slot |
| `transformationCards` | "More results" 3-photo grid (stage + decade arrays) | If in top 3 for their stage/decade |
| `transformationImages` | Single hero photo in Why Muscle Matters section | If stronger visual than current |
