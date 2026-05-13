# Social Proof Pages Index — The Evolved
**Version:** 1.0
**Created:** 2026-04-30
**Status:** Template ready — pages not yet built
**URL base:** theevolvedgym.com.au/results/

---

## Purpose

Each page is a keyword-targeted WordPress custom post type (`results`) featuring one member's story. Pages serve two functions:

1. **SEO / AIO / GEO:** Long-tail keyword ranking, Testimonial schema markup, internal linking from blog cluster articles
2. **Pre-qual bot Stage 2F:** Sent as contextual social proof links during the SA pre-qualification SMS conversation, matched to the prospect's disclosed goal and life stage

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

## Page Index

> Pages to be built as content sprint. Update status and URL when each goes live.
> Add to `outputs/systems/sa-prequalification-sop.md` Social Proof Page Index as each is published.

| # | Slug | Primary Goal | Life Stage | Status | Notes |
|---|---|---|---|---|---|
| 1 | postmenopause-weight-loss-strength-training | weight-loss | postmenopause | ✅ Published | Helen — WP ID 222 |
| 2 | postmenopause-bone-health-osteoporosis | bone-health | postmenopause | ✅ Published | Eleni — WP ID 225 |
| 3 | postmenopause-strength-return-to-fitness | return-to-fitness | postmenopause | ✅ Published | Vicky — WP ID 224 |
| 4 | perimenopause-weight-loss-brisbane | weight-loss | perimenopause | ✅ Published | Tash — WP ID 223 |
| 5 | perimenopause-strength-hormonal-health | hormonal-health | perimenopause | ✅ Published | Tammy — WP ID 249 |
| 6 | perimenopause-energy-mental-health | mental-health | perimenopause | ✅ Published | Simone — WP ID 250 |
| 7 | postpartum-return-to-fitness-strength-training | return-to-fitness | postpartum | ⬜ Not built | — |
| 8 | postpartum-weight-loss-new-mum | weight-loss | postpartum | ⬜ Not built | — |
| 9 | pregnancy-safe-strength-training | strength | pregnancy | ⬜ Not built | — |
| 10 | twenties-thirties-aesthetics-glutes | aesthetics | 20s-30s | ✅ Published | Monique — WP ID 255 |
| 11 | twenties-thirties-weight-loss-strength | weight-loss | 20s-30s | ✅ Published | Alana — WP ID 251 |
| 12 | twenties-thirties-mental-health-gym | mental-health | 20s-30s | ⬜ Not built | — |
| 13 | twenties-thirties-strength-first-time | strength | 20s-30s | ✅ Published | Isabelle — WP ID 252 |
| 14 | teens-strength-training-brisbane | strength | teens | ⬜ Not built | — |
| 15 | teens-aesthetics-confidence-gym | aesthetics | teens | ⬜ Not built | — |
| 16 | teens-sports-performance-strength | strength | teens | ⬜ Not built | — |
| 17 | over-60-strength-longevity-brisbane | strength | postmenopause | ⬜ Not built | 60+ women specifically |
| 18 | over-60-bone-density-strength-training | bone-health | postmenopause | ⬜ Not built | Osteoporosis prevention |
| 19 | ivf-fertility-strength-training | hormonal-health | pregnancy | ⬜ Not built | IVF/fertility context |
| 20 | weight-loss-plateau-broken-strength | weight-loss | 20s-30s | ✅ Published | Katherine — WP ID 256 |
| 21 | return-to-fitness-after-injury | return-to-fitness | 20s-30s | ✅ Published | Charmaine — WP ID 253 |
| 22 | energy-fatigue-strength-training | energy | perimenopause | ✅ Published | Megan — WP ID 254 |

---

## Content Sprint Plan

**Target:** Build all 22 pages before DNS cutover.

**Writing approach:**
- Each page: 600–900 words following template structure
- Source material: existing member stories (collected from conversations, testimonials, questionnaires)
- Anonymise if needed — first name + age bracket + life stage is sufficient
- Photos: optional — placeholder silhouette acceptable for launch, real photos preferred

**Build order priority:**
1. Postmenopause (4 pages) — largest existing blog cluster, best internal linking opportunity
2. Perimenopause (3 pages)
3. 20s–30s (4 pages) — broadest audience
4. Postpartum (2 pages)
5. Teens (3 pages)
6. Specialist (pregnancy, IVF, injury, 60+, energy) — 6 pages

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-04-30 | Initial index created — 22 planned pages, all pre-build |
