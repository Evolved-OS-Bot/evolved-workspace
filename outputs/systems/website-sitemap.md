# Website Sitemap & Migration Plan
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-05-06

---

## Overview

**Current state:** `theevolvedgym.com.au` points to GHL. All pages below are GHL-hosted.
**Target state:** `theevolvedgym.com.au` → WordPress/SiteGround. GHL funnel pages move to `go.theevolvedgym.com.au`.

DNS cutover happens after all SEO pages are rebuilt in WordPress.

---

## Page Inventory

### WordPress (already built)

| URL | Status | Notes |
|---|---|---|
| `theevolvedgym.com.au/` | ✅ Built | Homepage with PYJ selector |

---

### Migrate to WordPress (SEO pages)

#### Trainer Pages

| URL | Priority | Content Notes |
|---|---|---|
| `/leisa-personal-trainer-brisbane` | High | Video, testimonials carousel, FAQ accordions |
| `/marnie-personal-trainer-brisbane` | High | Same structure |
| `/piper-personal-trainer-brisbane` | High | Highest traffic (91 sessions) |
| `/megan-personal-trainer-brisbane` | High | Owner/head trainer |
| `/nora-personal-trainer-brisbane` | High | New page — no GHL source, build fresh in WordPress |

**Team hub page:**

| URL | Priority | Content Notes |
|---|---|---|
| `/team` (new WordPress URL) | High | Currently at `evolved-woman.theevolvedgym.com.au/post/team` — move to root domain. Active trainers: Megan, Leisa, Piper, Marnie, Nora |

#### Membership Pages

| URL | Priority | Content Notes |
|---|---|---|
| `/memberships/sculptstrength` | Medium | 3-col feature layout, FAQ, testimonials, no pricing shown |
| `/memberships/fitflex` | Medium | Same structure |
| `/memberships/fasttrack` | Medium | Same structure |
| `/memberships/evolve-u-program` | Medium | Same structure |

#### Services Pages

| URL | Priority | Content Notes |
|---|---|---|
| `/services` | High | Hub page — links to sub-pages, testimonials, FAQ |
| `/services/personal-training-brisbane` | High | 1:1 PT — FAQ, testimonials, booking CTA |
| `/services/small-group-personal-training-brisbane` | High | SGPT — key product |
| `/services/nutrition-lifestyle-coaching-brisbane` | Medium | Nutrition coaching |
| `/services/strength-assessment-for-women-brisbane` | Medium | SEO landing page for SA (not the booking page — that stays in GHL) |

#### Location Pages

| URL | Priority | Content Notes |
|---|---|---|
| `/locations` | High | Hub — 4 location cards: West End (open), Bulimba/Newfarm/Coolangatta (coming soon) |
| `/coming-to-coolangatta-tweed-heads` | Low | Register Interest form (GHL iframe) |
| `/coming-to-bulimba` | Low | Register Interest form (GHL iframe) |
| `/coming-to-newfarm` | Low | Register Interest form (GHL iframe) |
| `/thank-you-location` | Low | Single shared post-submission page for all 3 location forms. Update GHL form redirect URLs to point here after DNS cutover. |

#### Other

| URL | Priority | Content Notes |
|---|---|---|
| `/legal` | Low | Static legal page — simple copy across |

---

### Stay in GHL → Redirect to `go.theevolvedgym.com.au`

These pages have GHL forms or are post-conversion. After DNS cutover, 301 redirects send any incoming traffic to the `go.` subdomain.

| Current URL | Redirects To | Reason |
|---|---|---|
| `/30dnnc` | `go.theevolvedgym.com.au/30dnnc` | Working lead gen funnel — keep in GHL |
| `/30dnnc-thankyou` | `go.theevolvedgym.com.au/30dnnc-thankyou` | Post-form submission page |
| `/teen-30dnnc-o` | `go.theevolvedgym.com.au/teen-30dnnc-o` | Life-stage landing page |
| `/teen-30dnnc-p` | `go.theevolvedgym.com.au/teen-30dnnc-p` | Life-stage landing page (paid) |
| `/20s30s-30dnnc-o` | `go.theevolvedgym.com.au/20s30s-30dnnc-o` | Life-stage landing page |
| `/20s30s-30dnnc-p` | `go.theevolvedgym.com.au/20s30s-30dnnc-p` | Life-stage landing page (paid) |
| `/pregnancy-30dnnc-o` | `go.theevolvedgym.com.au/pregnancy-30dnnc-o` | Life-stage landing page |
| `/pregnancy-30dnnc-p` | `go.theevolvedgym.com.au/pregnancy-30dnnc-p` | Life-stage landing page (paid) |
| `/perimenopause-30dnnc-o` | `go.theevolvedgym.com.au/perimenopause-30dnnc-o` | Life-stage landing page |
| `/perimenopause-30dnnc-p` | `go.theevolvedgym.com.au/perimenopause-30dnnc-p` | Life-stage landing page (paid) |
| `/post-menopause-30dnnc-o` | `go.theevolvedgym.com.au/post-menopause-30dnnc-o` | Life-stage landing page |
| `/post-menopause-30dnnc-p` | `go.theevolvedgym.com.au/post-menopause-30dnnc-p` | Life-stage landing page (paid) |
| `/thank-you-coolangatta-tweed` | `/thank-you-location` | Consolidated into single WP thank-you page |
| `/thank-you-bulimba` | `/thank-you-location` | Consolidated into single WP thank-you page |
| `/thank-you-newfarm` | `/thank-you-location` | Consolidated into single WP thank-you page |

**Note:** Before DNS cutover, duplicate these GHL pages at the `go.` subdomain (or verify GHL serves them on both domains). The 301 redirects go in WordPress's `.htaccess` or Nginx config on SiteGround.

---

## Migration Sequence

Priority order based on traffic and dependency:

| # | Pages | Approach |
|---|---|---|
| 1 | Trainer pages — Piper, Megan, Leisa, Marnie | `/migrate-ghl-page` per page |
| 2 | Team hub page | Port from `evolved-woman` subdomain |
| 3 | Services hub + 4 service sub-pages | `/migrate-ghl-page` per page |
| 4 | Membership pages (4) | `/migrate-ghl-page` per page |
| 5 | Locations hub + coming-to pages | `/migrate-ghl-page` per page |
| 6 | Legal | Manual copy — short static page |
| 7 | Beth + Hannah individual trainer pages | New content — no GHL page to migrate |
| 8 | DNS cutover | Point `theevolvedgym.com.au` → SiteGround |
| 9 | 301 redirects live | GHL funnel pages redirect to `go.` |

---

## Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Nora trainer page | Build new in WordPress | No GHL source — need bio, photo, specialties from user |
| `/30dnnc` long-term | Keep in GHL at `go.` OR rebuild in WordPress with GHL form iframe | Keep in GHL — it converts well and form logic is complex |
| Location thank-you pages | Simple WordPress pages OR stay in GHL | Stay in GHL — GHL controls post-submission experience |
| Membership page strategy | Link from homepage as-is OR consolidate into single comparison page | Worth reviewing — 4 separate pages vs 1 comparison page is a real architectural question |
| `evolved-woman` subdomain | Redirect to root after team page migrates | Yes — retire it once team page is at `theevolvedgym.com.au/team` |

---

## Page Count Summary

| Category | Count | Status |
|---|---|---|
| Already built (WordPress) | 1 | Homepage |
| To migrate (GHL → WordPress) | 16 | Trainer × 4, Team, Services × 5, Membership × 4, Locations × 4 (hub + 3 coming-to), Legal |
| New pages to build | 1 | Nora individual trainer page |
| Stay in GHL → redirect | 15 | 30DNNC, 10 life-stage pages, 3 thank-you pages, 30dnnc-thankyou |
| **Total** | **34** | |
