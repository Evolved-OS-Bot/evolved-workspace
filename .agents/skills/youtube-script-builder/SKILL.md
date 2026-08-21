---
name: youtube-script-builder
description: Build a structured YouTube video script from workspace context — scene by scene, talking points not word-for-word, with screen directions, hero moment, thumbnail concept, SEO title options, description, and chapter timestamps. Supports four video types: skill/tool demo, educational/how-to, case study/result story, and offer/product launch. Saves output to outputs/video-scripts/. Use when preparing to record a YouTube video for the business.
---

# YouTube Script Builder

Build a complete, camera-ready YouTube video script tailored to your business — talking points, scene structure, screen directions, and SEO metadata — in one pass.

## What This Produces

- Scene-by-scene structure with talking points (not word-for-word — you speak naturally)
- Screen directions and demo notes where relevant
- The "hero moment" — the single most compelling beat in the video, clearly flagged
- 3 SEO-optimised title options
- Full YouTube description with keyword-rich copy and timestamp placeholders
- Thumbnail concept
- Saved to `outputs/video-scripts/[topic-slug].md`

---

## Configuration

```
VIDEO_TYPE:     [skill-demo | how-to | case-study | offer-launch]
TOPIC:          [What this video is about — one sentence]
TARGET_VIEWER:  [Who watches this video — be specific, e.g. "gym owners who've heard of AI but never built anything"]
CTA:            [What you want the viewer to do — e.g. "download the skill", "book a call", "subscribe"]
TARGET_LENGTH:  [e.g. 8 min, 12 min — guides pacing and scene count]
DEMO_SUBJECT:   [For skill-demo only: what is being demoed live on screen]
RESULT_DETAILS: [For case-study only: name/anonymised label, result stats, timeline]
PRODUCT_NAME:   [For offer-launch only: what is being launched]
OUTPUT_SLUG:    [Filename for the script, e.g. ai-workspace-starter-demo]
```

---

## Pre-Flight

- [ ] Read `AGENTS.md` — understand the business, brand voice, and audience before writing anything
- [ ] Read `context/business-info.md` and `context/strategy.md` — pull in current priorities and positioning
- [ ] Configuration values are filled in above
- [ ] `outputs/video-scripts/` directory exists (create it if not: `mkdir -p outputs/video-scripts`)

---

## Phase 1: Choose the Structure

Select the scene structure that matches VIDEO_TYPE. Each type has a proven sequence — do not reorder it.

---

### Structure A: Skill / Tool Demo

Use when: showing a capability, workflow, or tool in action. The demo IS the video.

**Hero moment:** The result that appears on screen and makes the viewer think "I didn't know it could do that."

```
Scene 1 — The Problem         (10% of runtime)
Scene 2 — What We're Building (8%)
Scene 3 — Demo Setup          (7%)
Scene 4 — The Demo            (40%)
Scene 5 — The Hero Moment     (15%)
Scene 6 — First Real Use      (10%)
Scene 7 — Wrap + CTA          (10%)
```

---

### Structure B: Educational / How-To

Use when: teaching something specific that the viewer can apply immediately.

**Hero moment:** The insight or technique that reframes how they think about the problem — the "I never thought of it that way" beat.

```
Scene 1 — The Hook            (10%)
Scene 2 — What You'll Learn   (5%)
Scene 3 — The Teaching        (50% — broken into steps)
Scene 4 — The Common Mistake  (15%)
Scene 5 — What Good Looks Like (10%)
Scene 6 — Wrap + CTA          (10%)
```

---

### Structure C: Case Study / Result Story

Use when: showing a real outcome — a client result, a business transformation, a before/after.

**Hero moment:** The specific result stated plainly — number, timeframe, before/after. No embellishment needed.

```
Scene 1 — The Before          (15%)
Scene 2 — The Problem         (15%)
Scene 3 — The Solution        (25%)
Scene 4 — The Result          (20%)
Scene 5 — The Insight         (15%)
Scene 6 — Wrap + CTA          (10%)
```

---

### Structure D: Offer / Product Launch

Use when: introducing a new product, skill, service, or offer.

**Hero moment:** The moment you show the output or proof — not a claim, but a demonstration that this exists and works.

```
Scene 1 — The Problem         (15%)
Scene 2 — The Gap             (10%)
Scene 3 — What This Is        (20%)
Scene 4 — Proof / Demo        (25%)
Scene 5 — What's Included     (15%)
Scene 6 — CTA                 (15%)
```

---

## Phase 2: Generate the Script

Write the full script to `/tmp/video-script-[OUTPUT_SLUG].md` before saving to outputs.

### Generation rules

**Voice and tone — derive from AGENTS.md and context files:**
- Match the brand voice established in the workspace — if it's direct and no-fluff, write talking points that are direct and no-fluff
- Write for the TARGET_VIEWER, not a general audience — use their language, reference their situation
- First person throughout — "I", "you", "we" — never passive or corporate

**Talking points, not scripts:**
- Each scene gets 3–6 bullet points — the ideas to hit, not the words to say
- The presenter speaks naturally from the bullet points — not reading
- If a line is too good to lose, mark it `[KEY LINE — say this clearly]`

**Screen directions:**
- Mark with `[ON SCREEN]` — what the viewer sees (face to camera, screen share, specific file, demo running)
- Mark demo-specific instructions with `[DEMO NOTE]` — what to do, what to show, what to avoid

**The hero moment:**
- Identify it explicitly with `--- HERO MOMENT ---`
- Give it space in the script — slow down here, don't rush past it
- Note what makes it compelling and what to let land before moving on

**Pacing:**
- Use TARGET_LENGTH to calculate approximate scene durations
- 1 minute of talking ≈ 120–150 words of bullet points
- Demo scenes can be longer — let the demo breathe

**SEO integration:**
- Work the primary keyword naturally into Scene 1 and Scene 7
- The problem statement in Scene 1 should mirror how the TARGET_VIEWER would search for this topic

---

## Phase 3: Generate SEO Metadata

After the script, produce all of the following.

### Title options (3 variants)

Write one of each:
1. **Curiosity/problem-led** — opens a gap, e.g. "Why Your AI Keeps Forgetting Your Business (And How to Fix It)"
2. **How-to/benefit-led** — clear and searchable, e.g. "How to Set Up a Codex Workspace for Your Business in 20 Minutes"
3. **Result-led** — specific outcome, e.g. "I Built an AI Workspace That Knows My Business. Here's How."

All three should include the primary keyword naturally.

### YouTube description

Write a full description (~200 words). Structure:
- Opening hook (1–2 sentences — make the viewer want to watch)
- What they'll see (3–5 bullet points with →)
- CTA with link placeholder
- Horizontal rule `---`
- Timestamps section (scene names with `0:00` placeholders to fill in after recording)

### Thumbnail concept

One sentence describing the visual. Must communicate the video's value in a glance — include a contrast (before/after, problem/solution), a visual hook (something on screen worth pausing for), and optional text overlay.

### Tags (10–15)

Mix of: exact-match keywords, broader topic keywords, brand terms.

---

## Phase 4: Save Output

Copy the finished script from `/tmp/` to the workspace:

```bash
cp /tmp/video-script-[OUTPUT_SLUG].md \
  "[WORKSPACE_PATH]/outputs/video-scripts/[OUTPUT_SLUG].md"
```

Confirm the file exists and open it for review.

---

## Validation Checklist

- [ ] Script uses talking points, not paragraphs to read
- [ ] Every scene has an `[ON SCREEN]` direction
- [ ] Hero moment is clearly marked and given space
- [ ] CTA appears in Scene 7/wrap and once only — not repeated throughout
- [ ] Brand voice matches `AGENTS.md` and context files
- [ ] Three title options produced
- [ ] YouTube description includes timestamps section
- [ ] Thumbnail concept is a single visual idea, not a vague description
- [ ] File saved to `outputs/video-scripts/[OUTPUT_SLUG].md`

---

## Notes

- **Talking points, not scripts.** The most common failure of AI-written video scripts is they sound like they were written to be read. Every line should be a prompt for a natural sentence, not a sentence itself.
- **One hero moment per video.** If there are two equally strong moments, that is two videos.
- **The CTA drives one action.** Don't ask the viewer to subscribe, download, comment, AND share. Pick one. Make it the right one.
- **Record before refining.** The script is not final until you've spoken it aloud at least once. Talking points that read well often don't speak well — adjust after the first pass.
- **SEO title vs. creative title.** YouTube rewards click-through rate AND watch time. The how-to/benefit title typically gets more search traffic; the curiosity title typically gets more click-throughs from suggested videos. Use the how-to version as the main title and the curiosity version as the thumbnail text overlay.
