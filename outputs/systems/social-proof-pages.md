# Social Proof Pages Index — The Evolved
**Version:** 2.0
**Created:** 2026-04-30
**Last Updated:** 2026-08-04
**Status:** 35 Results stories published in WordPress; 18 of the original 22 archetypes built; 4 original archetypes remain without a source story
**URL base:** theevolvedgym.com.au/results/
**Website authority:** `outputs/systems/website-v2-release-manifest.md`

---

## Purpose

Each page is a keyword-targeted WordPress custom post type (`results`) featuring one member's story. Pages serve two functions:

1. **SEO / AIO / GEO:** Long-tail keyword ranking, Testimonial schema markup, internal linking from blog cluster articles
2. **Pre-qual bot Stage 2F:** Sent as contextual social proof links during the SA pre-qualification SMS conversation, matched to the prospect's disclosed goal and life stage

## Story Distribution Automation

Six published GHL workflows distribute a newly published member story to contacts with the matching life-stage tag:

- `Send Story Email - 20-30's`
- `Send Story Email - Perimenopause`
- `Send Story Email - Postmenopause`
- `Send Story Email - Postpartum`
- `Send Story Email - Pregnancy`
- `Send Story Email - Teen`

These workflows are part of the member-story publishing system, not general nurture campaigns. After a story page is added to the website, `scripts/notify_story.py` updates the relevant story values and applies the life-stage trigger tag. The matching workflow then sends the story email to that audience; the featured member can also receive a separate notification that her story is live.

The website transfer does not replace these GHL workflows. Story URLs and custom values must be updated only after their destination pages work on the final WordPress root.

The 35 published stories are part of the existing Website V2 release. The
remaining archetypes and SEO improvements are protected backlog, not evidence
that the V2 website still needs to be built.

---

## Page Template

Each page follows this structure:

```
1. Header image (member photo — full width, dark overlay)
2. Member name + life stage tag + goal tag
3. Pull quote (bold, large — the key transformation statement)
4. Her story (500–800 words: goal, challenges, training approach, results)
5. Key results callouts (3 stats: e.g. "Lost 12kg", "Deadlifts 80kg", "Training 18 months")
6. Trainer quote
7. Internal link → relevant blog article
8. CTA → Book Your Strength Assessment → go.theevolvedgym.com.au/strength-assessment
```

**SEO per page (RankMath):**
- Primary keyword in: title, H1, first paragraph, meta description
- Schema: `@type: Testimonial` with `author`, `reviewBody`, `itemReviewed`
- Target: 600–900 words per page

---

## Taxonomies

### Goal
- `weight-loss`
- `strength`
- `bone-health`
- `aesthetics`
- `mental-health`
- `energy`
- `hormonal-health`
- `return-to-fitness`

### Life Stage
- `teens`
- `20s-30s`
- `perimenopause`
- `postmenopause`
- `postpartum`
- `pregnancy`

---

## Pre-Qual Bot Matching Logic

When prospect discloses a goal and/or life stage during pre-qual Stage 2, the bot selects the best-matching page from this index:

1. Match primary goal first
2. Then match life stage
3. If exact match exists — send that URL
4. If no exact match — send closest goal match
5. Only send pages that are live (status = Published)

---

## Original 22-Page Archetype Index

> This is the original planning matrix. It is not the complete current Results library.
> Add to `outputs/systems/sa-prequalification-sop.md` Social Proof Page Index as each is published.

| # | Slug | Primary Goal | Life Stage | Status | Notes |
|---|---|---|---|---|---|
| 1 | postmenopause-weight-loss-strength-training | weight-loss | postmenopause | ✅ Published | Helen — WP ID 222 |
| 2 | postmenopause-bone-health-osteoporosis | bone-health | postmenopause | ✅ Published | Eleni — WP ID 225 |
| 3 | postmenopause-strength-return-to-fitness | return-to-fitness | postmenopause | ✅ Published | Vicky — WP ID 224 |
| 4 | perimenopause-weight-loss-brisbane | weight-loss | perimenopause | ✅ Published | Tash — WP ID 223 |
| 5 | perimenopause-strength-hormonal-health | hormonal-health | perimenopause | ✅ Published | Tammy — WP ID 249 |
| 6 | perimenopause-energy-mental-health | mental-health | perimenopause | ✅ Published | Simone — WP ID 250 |
| 7 | postpartum-return-to-fitness-strength-training | return-to-fitness | postpartum | ✅ Published | Ruth — WP ID 269 |
| 8 | postpartum-weight-loss-new-mum | weight-loss | postpartum | ✅ Published | Kylie — WP ID 270 |
| 9 | pregnancy-safe-strength-training | strength | pregnancy | ✅ Published | Kerrie — WP ID 271 |
| 10 | twenties-thirties-aesthetics-glutes | aesthetics | 20s-30s | ✅ Published | Monique — WP ID 255 |
| 11 | twenties-thirties-weight-loss-strength | weight-loss | 20s-30s | ✅ Published | Alana — WP ID 251 |
| 12 | twenties-thirties-mental-health-gym | mental-health | 20s-30s | ✅ Published | Rudra — WP ID 272 |
| 13 | twenties-thirties-strength-first-time | strength | 20s-30s | ✅ Published | Isabelle — WP ID 252 |
| 14 | teens-strength-training-brisbane | strength | teens | ⬜ Not built | — |
| 15 | teens-aesthetics-confidence-gym | aesthetics | teens | ⬜ Not built | — |
| 16 | teens-sports-performance-strength | strength | teens | ⬜ Not built | — |
| 17 | over-60-strength-longevity-brisbane | strength | postmenopause | ✅ Published | Michelle — WP ID 273 |
| 18 | over-60-bone-density-strength-training | bone-health | postmenopause | ✅ Published | Jennifer — WP ID 274 |
| 19 | ivf-fertility-strength-training | hormonal-health | pregnancy | ⬜ Not built | IVF/fertility context |
| 20 | weight-loss-plateau-broken-strength | weight-loss | 20s-30s | ✅ Published | Katherine — WP ID 256 |
| 21 | return-to-fitness-after-injury | return-to-fitness | 20s-30s | ✅ Published | Charmaine — WP ID 253 |
| 22 | energy-fatigue-strength-training | energy | perimenopause | ✅ Published | Megan — WP ID 254 |

---

## Additional Published Results

These 17 stories were added beyond the original 22-row matrix. Together with the 18 built archetypes above, they make the 35 published Results records in the Phase 1 database snapshot.

| Story | WP ID | Slug |
|---|---|---|
| Nikki — wedding weight loss | 278 | `twenties-wedding-weight-loss-confidence` |
| Emma — body recomposition in her 20s | 279 | `twenties-body-recomposition-scale-didnt-move` |
| Katrina — FIFO weight loss | 280 | `twenties-weight-loss-fifo-confidence` |
| Kat — gym confidence in her 30s | 281 | `thirties-mum-gym-confidence-strength` |
| Leisa — strength and recomposition | 282 | `thirties-strength-recomposition-marathon` |
| Emma — recomposition and mindset | 283 | `thirties-recomposition-mindset-eating-more` |
| Karyn — weight loss and back pain | 284 | `perimenopause-weight-loss-back-pain` |
| Jules — first-time strength training | 285 | `perimenopause-first-time-strength-training-40s` |
| Johanna — HYROX and consistency | 286 | `perimenopause-hyrox-strength-consistency` |
| Jess — strength, recomposition and HYROX | 309 | `twenties-strength-recomposition-hyrox` |
| Bec — postpartum and wedding weight loss | 310 | `postpartum-wedding-weight-loss` |
| Belinda — frozen-shoulder rehabilitation | 313 | `fifties-strength-frozen-shoulder-rehabilitation` |
| Orlagh — first-time gym experience | 314 | `twenties-strength-first-timer-safe-space` |
| Peta — strength and daily ritual | 315 | `forties-strength-recomposition-daily-ritual` |
| Tess — strength and deadlifting | 316 | `thirties-strength-deadlift-desk-worker` |
| Laura — martial arts and mental health | 317 | `twenties-strength-martial-arts-mental-health` |
| Sophie — career change and strength | 318 | `forties-strength-career-change-landscaping` |

## Current Quality and SEO Work

- Preserve all 35 published Results records.
- Add the Results post type to the intended XML sitemap.
- Add unique meta descriptions to the 34 stories that lack them.
- Add and validate the intended Testimonial schema.
- Resolve the 12 missing featured images with approved assets or a documented exception.
- Remove the duplicate hardcoded story-card source from the archive template only after the database-driven replacement is verified.

## Remaining Content Sprint

**Original matrix status:** 18 of 22 built; 4 remain.

The remaining four planned archetypes are:

- three teen stories;
- one IVF/fertility story.

They remain in the plan but are not automatic DNS cutover blockers unless the owner makes them launch requirements.

**Writing approach:**
- Each page: 600–900 words following template structure
- Source material: existing member stories (collected from conversations, testimonials, questionnaires)
- Anonymise if needed — first name + age bracket + life stage is sufficient
- Photos: optional — placeholder silhouette acceptable for launch, real photos preferred

**Remaining build order:**
1. Teen strength
2. Teen confidence/aesthetics
3. Teen sports performance
4. IVF/fertility strength

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 2.0 | 2026-08-04 | Reconciled the original matrix against the Phase 1 database: 35 published stories, 18 original archetypes built, 4 remaining; recorded 17 additional stories and SEO gaps |
| 1.1 | 2026-07-17 | Documented the six life-stage story-email workflows and their role in the publishing system |
| 1.0 | 2026-04-30 | Initial index created — 22 planned pages, all pre-build |
