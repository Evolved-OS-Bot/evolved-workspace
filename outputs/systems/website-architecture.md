# Website Architecture — The Evolved
**Version:** 1.0
**Created:** 2026-04-30
**Owner:** The Evolved — Operations

---

## Domain Map

| Domain | Platform | Purpose |
|---|---|---|
| `theevolvedgym.com.au` | WordPress / SiteGround | Homepage, blog, results (social proof) — primary SEO authority |
| `go.theevolvedgym.com.au` | GHL | All funnels, forms, booking pages, SA booking |
| `links.theevolvedgym.com.au` | GHL | Short links, QR codes — unchanged |
| `blog.theevolvedgym.com.au` | Redirects → root | 301 all traffic to `theevolvedgym.com.au/blog/` |

---

## URL Structure

### WordPress (theevolvedgym.com.au)

| Path | Type | Description |
|---|---|---|
| `/` | Page (front page) | Sniper homepage — one CTA, no navigation |
| `/blog/` | Archive | Blog article index |
| `/blog/[slug]/` | Post | Individual blog article |
| `/results/` | CPT Archive | Social proof page index |
| `/results/[goal-keyword-life-stage]/` | CPT Single | Individual member result story |

### GHL (go.theevolvedgym.com.au)

| Path | Description |
|---|---|
| `/strength-assessment` | SA booking funnel — primary CTA destination |
| All other GHL pages | Funnels, forms, automation pages |

---

## Key URL Changes (Migration)

| Before | After | Type |
|---|---|---|
| `theevolvedgym.com.au` | `go.theevolvedgym.com.au` | GHL domain change |
| `theevolvedgym.com.au/strength-assessment` | `go.theevolvedgym.com.au/strength-assessment` | GHL funnel moves to subdomain |
| `blog.theevolvedgym.com.au/[slug]/` | `theevolvedgym.com.au/blog/[slug]/` | 301 redirect, WordPress takes over |

---

## GHL Custom Value Update Required

| Custom Value | Old Value | New Value |
|---|---|---|
| `{{custom_values.strength__longevity_assessment}}` | `theevolvedgym.com.au/strength-assessment` | `go.theevolvedgym.com.au/strength-assessment` |

All homepage CTAs link to `go.theevolvedgym.com.au/strength-assessment`.

---

## Social Proof Pages (Results CPT)

**URL pattern:** `theevolvedgym.com.au/results/[primary-goal]-[life-stage]-[modifier]`

**Taxonomies:**

*Goal:*
- `weight-loss`
- `strength`
- `bone-health`
- `aesthetics`
- `mental-health`
- `energy`
- `hormonal-health`
- `return-to-fitness`

*Life Stage:*
- `teens`
- `20s-30s`
- `perimenopause`
- `postmenopause`
- `postpartum`
- `pregnancy`

**SEO configuration per page:**
- RankMath: primary keyword in title, H1, first paragraph, meta description
- Schema: `@type: Testimonial` with `author`, `reviewBody`, `itemReviewed`
- Target word count: 600–900 words

---

## Homepage Architecture

**No navigation header** — single-purpose conversion page.

| Section | Purpose |
|---|---|
| Hero | Headline + hero image (Megan coaching) + primary CTA |
| Sarcopenia Infographic | Interactive muscle loss curve by age |
| Frequency Infographic | Interactive training frequency vs results curve |
| What the SA Is | Pre-frame the assessment (SOP Stage 3 language) |
| Social Proof Teaser | 3 featured results cards |
| Final CTA | Repeat call-to-action |

**Single CTA throughout:** "Book Your Strength Assessment" → `go.theevolvedgym.com.au/strength-assessment`

---

## DNS Configuration

| Record | Type | Value |
|---|---|---|
| `theevolvedgym.com.au` | A | SiteGround WordPress hosting IP |
| `www.theevolvedgym.com.au` | CNAME | `theevolvedgym.com.au` |
| `go.theevolvedgym.com.au` | CNAME | GHL custom domain CNAME |
| `links.theevolvedgym.com.au` | CNAME | GHL (unchanged) |
| `blog.theevolvedgym.com.au` | CNAME | Redirect service → root domain |

---

## WordPress Tech Stack

| Component | Tool | Notes |
|---|---|---|
| Theme | Blocksy (+ child theme) | Already on blog, consistent design system |
| SEO | RankMath | Testimonial schema on results CPT |
| Animations | GSAP + ScrollTrigger (CDN) | Scroll-triggered section animations |
| Infographics | Chart.js (CDN) | Sarcopenia + frequency curves |
| Redirects | WordPress Redirection plugin | Manages blog subdomain 301s |
| Analytics | Google Analytics via Site Kit | Already on blog |

---

## Pre-Cutover Checklist

- [ ] WordPress configured on root domain in SiteGround (tested on staging)
- [ ] All social proof pages reviewed
- [ ] Homepage copy approved
- [ ] 301 redirect rules loaded in WordPress Redirection plugin
- [ ] GHL domain change ready (`go.theevolvedgym.com.au`)
- [ ] GHL custom value updated (`strength__longevity_assessment`)
- [ ] GHL audit complete — no other hardcoded root domain URLs
- [ ] DNS TTL reduced to 300 (5 min) before cutover
- [ ] Google Analytics updated to root domain

---

## WordPress Pages Index

**Last updated:** 2026-05-13

| Page | WP ID | URL | Template |
|---|---|---|---|
| Homepage | 165 | `/` | template-homepage.php |
| Piper (trainer) | 221 | `/piper-personal-trainer-brisbane` | template-trainer-page.php |
| Megan (trainer) | 226 | `/megan-personal-trainer-brisbane` | template-trainer-page.php |
| Marnie (trainer) | 227 | `/marnie-personal-trainer-brisbane` | template-trainer-page.php |
| Leisa (trainer) | 228 | `/leisa-personal-trainer-brisbane` | template-trainer-page.php |
| Team hub | 229 | `/team` | template-trainer-page.php |
| Services hub | 230 | `/services` | template-trainer-page.php |
| Personal Training | 231 | `/services/personal-training-brisbane` | template-trainer-page.php |
| Small Group PT | 232 | `/services/small-group-personal-training-brisbane` | template-trainer-page.php |
| Nutrition & Lifestyle | 233 | `/services/nutrition-lifestyle-coaching-brisbane` | template-trainer-page.php |
| Strength Assessment | 234 | `/services/strength-assessment-for-women-brisbane` | template-trainer-page.php |
| Memberships hub | 236 | `/memberships` | template-trainer-page.php |
| Fit & Flexible | 237 | `/memberships/fitflex` | template-trainer-page.php |
| Sculpt & Strength | 238 | `/memberships/sculptstrength` | template-trainer-page.php |
| Fast Track | 239 | `/memberships/fasttrack` | template-trainer-page.php |
| The Evolve Program | 240 | `/memberships/evolve-u-program` | template-trainer-page.php |
| Locations hub | 241 | `/locations` | template-trainer-page.php |
| West End (open) | 242 | `/locations/west-end-brisbane` | template-trainer-page.php |
| Bulimba (coming soon) | 243 | `/locations/bulimba` | template-trainer-page.php |
| New Farm (coming soon) | 244 | `/locations/new-farm` | template-trainer-page.php |
| Coolangatta (coming soon) | 245 | `/locations/coolangatta` | template-trainer-page.php |
| Townsville (coming soon) | 246 | `/locations/townsville` | template-trainer-page.php |
| Chermside (coming soon) | 247 | `/locations/chermside` | template-trainer-page.php |
| Legal (Privacy + Terms) | 248 | `/legal` | template-trainer-page.php |

**Still to build:** Nora trainer page.

**Adding a new location:** Create WP page as child of 241, copy a coming-soon HTML file, update suburb name + nearby areas + precinct in ~5 places, deploy. West End page is the template for open locations.

---

## Results CPT Pages Index

**Last updated:** 2026-05-13

| Story | WP ID | URL Slug |
|---|---|---|
| Helen — weight loss 60s | 222 | `postmenopause-weight-loss-strength-training` |
| Tash — weight loss perimenopause | 223 | `perimenopause-weight-loss-brisbane` |
| Vicky — strength/recomp 50s | 224 | `postmenopause-strength-return-to-fitness` |
| Eleni — bone density 60s | 225 | `postmenopause-bone-health-osteoporosis` |
| Tammy — hormonal health | 249 | `perimenopause-strength-hormonal-health` |
| Simone — mental health | 250 | `perimenopause-energy-mental-health` |
| Alana — weight loss 20s | 251 | `twenties-thirties-weight-loss-strength` |
| Isabelle — first gym 20s | 252 | `twenties-thirties-strength-first-time` |
| Charmaine — return to fitness | 253 | `return-to-fitness-after-injury` |
| Megan — energy/fatigue | 254 | `energy-fatigue-strength-training` |
| Monique — recomp 20s | 255 | `twenties-thirties-aesthetics-glutes` |
| Katherine — weight loss plateau | 256 | `weight-loss-plateau-broken-strength` |
| Rudra — mental health 20s | 272 | `twenties-thirties-mental-health-gym` |
| Jennifer — bone density 60s | 274 | `over-60-bone-density-strength-training` |
| Nikki — wedding weight loss | 278 | `twenties-wedding-weight-loss-confidence` |
| Emma — recomp 20s | 279 | `twenties-body-recomposition-scale-didnt-move` |
| Katrina — FIFO weight loss | 280 | `twenties-weight-loss-fifo-confidence` |
| Kat — gym confidence 30s | 281 | `thirties-mum-gym-confidence-strength` |
| Leisa — strength/recomp 30s | 282 | `thirties-strength-recomposition-marathon` |
| Emma — recomp/mindset 30s | 283 | `thirties-recomposition-mindset-eating-more` |
| Karyn — weight loss/back pain | 284 | `perimenopause-weight-loss-back-pain` |
| Jules — first time strength 40s | 285 | `perimenopause-first-time-strength-training-40s` |
| Johanna — HYROX perimenopause | 286 | `perimenopause-hyrox-strength-consistency` |
| Ruth — postpartum return | 269 | `postpartum-return-to-fitness-strength-training` |
| Kylie — postpartum weight loss | 270 | `postpartum-weight-loss-new-mum` |
| Kerrie — pregnancy strength | 271 | `pregnancy-safe-strength-training` |
| Michelle — strength 60s | 273 | `over-60-strength-longevity-brisbane` |
| Jess — recomp/HYROX 20s | 309 | `twenties-strength-recomposition-hyrox` |
| Bec — postpartum/wedding | 310 | `postpartum-wedding-weight-loss` |

**Remaining to build:** ~9 results pages (see `outputs/systems/social-proof-pages.md` for full planned index).

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.2 | 2026-05-13 | Added WP pages index + Results CPT index (moved from CLAUDE.md) |
| 1.1 | 2026-05-06 | Updated page IDs and Results CPT count |
| 1.0 | 2026-04-30 | Initial architecture documentation for root domain migration |
