# Plan: Website Migration & Redesign — Unified WordPress Root + Sniper Homepage
**Created:** 2026-04-29
**Status:** Ready for DNS cutover — all build steps complete, 4 manual actions remaining (see Implementation Notes)
**Request:** Migrate from GHL root + WordPress blog subdomain to unified WordPress root. Build a sniper-style single-page homepage with one CTA (Book Strength Assessment), no navigation, smooth animations, and two interactive infographics. Social proof pages as WordPress custom post type. Blog moves to root domain. GHL moves to subdomain.

---

## Overview

### What This Plan Accomplishes

Consolidates all web content onto `theevolvedgym.com.au` under WordPress, eliminating the subdomain authority split that has been diluting SEO value since the blog launched. The homepage becomes a single-purpose conversion page — one message, one action — supported by two interactive infographics that move visitors from curiosity to conviction before they book.

### Why This Matters

Every blog article and social proof page currently published on `blog.theevolvedgym.com.au` builds authority for a subdomain, not the root domain. Consolidating onto the root means the blog, results pages, and homepage all reinforce each other — topical authority compounds. The sniper homepage removes every distraction from the one action that drives revenue: booking a Strength Assessment.

---

## Current State

### Relevant Existing Structure

```
theevolvedgym.com.au              → GHL website builder (single-page marketing site)
theevolvedgym.com.au/strength-assessment → GHL funnel page (SA booking — active in workflows)
blog.theevolvedgym.com.au         → WordPress / Blocksy theme (21+ articles, 5 categories)
links.theevolvedgym.com.au        → GHL funnels, forms, booking pages (unchanged)
```

**Hosting:** SiteGround — WordPress blog currently hosted here on blog subdomain. Root domain will move to SiteGround WordPress after migration.

**Content creation tool:** Groove.cm — used as the page builder/editor for blog content. Not a host. Unaffected by migration.

**GHL root site structure (confirmed via crawl):**
- Single-page design — no subpages exist except `/strength-assessment`
- Sections: Hero, About, Services, Pricing, Testimonials
- Colour scheme: dark backgrounds, pink (#e43388) accents
- Typography: PT Serif Caption (headings), Lato (body)
- Hero visual: photo of Megan coaching women in the gym (retain in new design)
- No sitemap, no robots.txt
- Current homepage headline: "Brisbane's Leading Women-Only Gym" (performing well — retain)

**WordPress blog (blog.theevolvedgym.com.au):**
- Blocksy theme v2.1.22
- Categories: Teens, 20s & 30s, Pre/Post Natal, Perimenopause, Post Menopause
- 21 published articles (80% migrated from Groove.cm — admin completing remaining 20%)
- Google Analytics via Site Kit

**Related workspace files:**
- `outputs/systems/blog-doctrine.md` — content philosophy and standards
- `outputs/systems/blog-catalog.md` — full article index with SEO hierarchy
- `outputs/systems/sa-prequalification-sop.md` — references social proof page index (to be created)
- `plans/2026-04-02-sa-prequalification-ai-agent.md` — pre-qual bot sends social proof links (depends on pages existing)
- `plans/2026-04-27-blog-bot.md` — blog content pipeline (depends on root domain consolidation)
- GHL workflows: `custom_values.strength__longevity_assessment` links to booking page (unchanged)

### Gaps or Problems Being Addressed

- Blog authority is split across subdomain — all SEO value is fragmented
- Social proof pages don't exist yet — pre-qual bot Stage 2F cannot be automated
- GHL homepage has no interactivity, no infographics, weak conversion architecture
- No `/results/[keyword]` URL structure exists anywhere
- Homepage has navigation — dilutes the single conversion goal

---

## Proposed Changes

### Summary of Changes

- WordPress takes over `theevolvedgym.com.au` (root domain)
- GHL moves to `go.theevolvedgym.com.au`
- `blog.theevolvedgym.com.au` redirects to `theevolvedgym.com.au/blog/`
- New sniper homepage built in WordPress/Blocksy — no navigation, one CTA
- Two interactive infographics built in JavaScript (Chart.js + GSAP)
- Social proof custom post type created at `/results/[keyword]`
- 22 existing social proof stories migrated to new page template
- All GHL workflow hardcoded URLs audited and updated
- Google Search Console updated with root domain property

### New Files to Create

| File Path | Purpose |
|---|---|
| `outputs/systems/website-architecture.md` | Documents the new URL structure, page types, and redirect map |
| `outputs/systems/social-proof-pages.md` | Social proof page index — URL, goal tags, life stage tags, story summary |
| `reference/homepage-copy.md` | Final approved copy for all homepage sections |
| `reference/infographic-sarcopenia-data.md` | Data points and annotation copy for sarcopenia curve |
| `reference/infographic-frequency-data.md` | Data points and annotation copy for training frequency curve |
| `scripts/audit-ghl-urls.py` | Scans GHL workflows via API for hardcoded theevolvedgym.com.au URLs |
| `scripts/redirects.conf` | Apache/Nginx 301 redirect rules for blog subdomain migration |

### Files to Modify

| File Path | Changes |
|---|---|
| `outputs/systems/sa-prequalification-sop.md` | Populate Social Proof Page Index table once pages are live |
| `outputs/systems/blog-catalog.md` | Update all blog URLs from blog.theevolvedgym.com.au to theevolvedgym.com.au/blog/ |
| `CLAUDE.md` | Add website architecture section, note social proof page system |

---

## Design Decisions

### Key Decisions Made

1. **WordPress on root, GHL on subdomain:** Full SEO control, Testimonial schema markup, RankMath, internal linking between blog and results pages. GHL funnels work identically on a subdomain — booking flow is unaffected.

2. **Retain Blocksy theme, evolve it:** Blocksy is already running on the blog. Consistent theme across root means one design system, one set of global styles. Blocksy Companion (confirmed active) handles the companion features. Full-width sections and custom JS injection work via child theme in Blocksy free — no Pro licence required for this build.

3. **No navigation on homepage:** Single-purpose sniper page. The only exit is the CTA or the browser back button. Blog, results, and team pages exist at their own URLs but are not linked from the homepage. This is a deliberate conversion architecture decision.

4. **GSAP for animations, Chart.js for infographics:** GSAP is the industry standard for smooth, performant scroll-triggered animations. Chart.js is lightweight (~60KB), well-documented, and produces clean interactive charts without the complexity of D3.js. Together they give professional motion without bloat.

5. **Social proof as WordPress custom post type:** Allows RankMath SEO per story, Testimonial schema markup, taxonomy filtering by goal and life stage, and future programmatic generation by the blog bot. Not just pages — a proper content type.

6. **Keyword-based URLs for social proof:** `/results/postmenopause-weight-loss-strength-training` ranks for long-tail searches and can be sent as a contextual link in the pre-qual SMS bot.

7. **Price sensitivity escalation to admin (not auto-cancel):** Documented in SOP. Bot flags, admin decides.

### Alternatives Considered

- **Build social proof in GHL:** Rejected — limited schema markup, no RankMath, no programmatic generation.
- **New theme (not Blocksy):** Rejected — Blocksy already installed on blog, migration would require full redesign of 21 articles.
- **D3.js for infographics:** Rejected — significant complexity overhead for two charts. Chart.js achieves the same result with a fraction of the code.
- **Keep blog on subdomain:** Rejected — the entire point of this migration is authority consolidation.

### Open Questions

1. **SiteGround domain setup:** Add `theevolvedgym.com.au` as the primary domain in SiteGround for the existing WordPress install (currently on blog subdomain). SiteGround supports this via Site Tools → Domains → Add Domain. SSL auto-provisioned via Let's Encrypt.
2. **GHL main domain change:** GHL → Settings → Business Profile → Website → change from `theevolvedgym.com.au` to `go.theevolvedgym.com.au`.
3. **`/strength-assessment` page:** Stays in GHL — moves to `go.theevolvedgym.com.au/strength-assessment` with all other funnels. WordPress does not serve this page. Update `{{custom_values.strength__longevity_assessment}}` from `theevolvedgym.com.au/strength-assessment` → `go.theevolvedgym.com.au/strength-assessment`. All homepage CTAs link to `go.theevolvedgym.com.au/strength-assessment`. ✅ Resolved.
4. **Blocksy Companion vs Pro:** Companion plugin is confirmed active. Full-width page templates are available in Blocksy free — no Pro requirement for the homepage layout. Confirm custom JS injection is available (it is in free via child theme). ✅ Resolved.
5. **GHL scope:** All funnels, forms, and booking pages stay on GHL under `go.theevolvedgym.com.au`. WordPress serves only: homepage, blog, results pages. Clean separation of concerns.

---

## Step-by-Step Tasks

### Step 1: Pre-Migration Audit

Before touching anything, map every URL and dependency that will change.

**Actions:**
- Run `scripts/audit-ghl-urls.py` to find all hardcoded `theevolvedgym.com.au` and `blog.theevolvedgym.com.au` URLs across GHL workflows, emails, and SMS templates
- The one confirmed URL requiring update: `{{custom_values.strength__longevity_assessment}}` → change from `theevolvedgym.com.au/strength-assessment` to `go.theevolvedgym.com.au/strength-assessment`
- Audit may surface additional blog subdomain links in email templates — these get 301 redirect coverage but proactive updates are cleaner
- GHL funnels and booking pages: no changes needed — they move wholesale to `go.theevolvedgym.com.au` with the domain change
- List all external backlinks to blog.theevolvedgym.com.au (Google Search Console → Links report)
- Confirm Groove.cm supports root domain hosting or identify new host

**Files affected:**
- `scripts/audit-ghl-urls.py` (to be created)
- `outputs/systems/website-architecture.md` (to be created — document findings here)

---

### Step 2: Write Audit Script

Create a Python script that calls the GHL API to scan all workflows, emails, and SMS templates for hardcoded domain references.

**Actions:**
- Script queries GHL workflows API for all workflow actions containing `theevolvedgym.com.au` or `blog.theevolvedgym.com.au`
- Outputs a list: workflow name, action type, matched URL
- Uses existing GHL API credentials from `scripts/.env`

**Files affected:**
- `scripts/audit-ghl-urls.py` (new)

---

### Step 3: Prepare 301 Redirect Rules

Write the redirect configuration before DNS changes so it can be dropped in immediately on cutover.

**Actions:**
- Create `scripts/redirects.conf` with Apache/Nginx rules:
  - `blog.theevolvedgym.com.au` → `theevolvedgym.com.au/blog/` (all paths preserved)
  - Any GHL root pages that had real URLs → equivalent WordPress URLs
- Format depends on Groove.cm hosting environment (Apache = .htaccess, Nginx = server block)
- Include wildcard rule: `blog.theevolvedgym.com.au/(.*)` → `theevolvedgym.com.au/blog/$1` (301)

**Files affected:**
- `scripts/redirects.conf` (new)

---

### Step 4: WordPress Root Domain Setup (Manual — You Action)

Configure WordPress to serve from theevolvedgym.com.au.

**Actions (your steps):**
1. In SiteGround Site Tools → Domains → Add Domain: add `theevolvedgym.com.au` as addon domain pointing to the WordPress install directory
2. In WordPress admin → Settings → General: update Site URL and WordPress URL to `https://theevolvedgym.com.au`
3. SSL: SiteGround → Security → SSL Manager → Let's Encrypt → issue for `theevolvedgym.com.au` (auto, free)
4. Do NOT change DNS yet — test on staging/preview URL first
5. No `/strength-assessment` page needed in WordPress — this stays in GHL at `go.theevolvedgym.com.au/strength-assessment`

**Files affected:** None (WordPress admin)

---

### Step 5: Install Required WordPress Plugins

**Actions:**
- Confirm RankMath SEO is installed and configured (likely already on blog)
- Install GSAP via CDN reference in theme (no plugin needed)
- Install Chart.js via CDN reference in theme
- Confirm Blocksy Companion plugin is active (already confirmed) — full-width templates and custom JS handled via child theme
- Install Redirection plugin (manages 301 redirects from within WordPress)

---

### Step 6: Create Social Proof Custom Post Type

Register a `results` custom post type in WordPress with goal and life stage taxonomies.

**Actions:**
- Add to Blocksy child theme's `functions.php`:

```php
// Custom post type: Results (Social Proof)
function evolved_register_results_cpt() {
    register_post_type('results', [
        'labels'      => ['name' => 'Results', 'singular_name' => 'Result'],
        'public'      => true,
        'has_archive' => true,
        'rewrite'     => ['slug' => 'results'],
        'supports'    => ['title', 'editor', 'thumbnail', 'custom-fields'],
        'show_in_rest' => true,
    ]);
    // Goal taxonomy
    register_taxonomy('goal', 'results', [
        'label'   => 'Goal',
        'rewrite' => ['slug' => 'results/goal'],
        'public'  => true,
    ]);
    // Life stage taxonomy
    register_taxonomy('life_stage', 'results', [
        'label'   => 'Life Stage',
        'rewrite' => ['slug' => 'results/life-stage'],
        'public'  => true,
    ]);
}
add_action('init', 'evolved_register_results_cpt');
```

- Configure RankMath to index `results` post type
- Add Testimonial schema markup via RankMath custom schema on results template

**Files affected:** WordPress child theme `functions.php`

---

### Step 7: Build Social Proof Page Template

Create a Blocksy-compatible page template for individual result stories.

**Page structure per story:**
```
Header image (member photo — full width, dark overlay)
Member name + life stage tag + goal tag
Pull quote (bold, large — the key transformation statement)
Her story (500-800 words — goal, challenges, training approach, results)
Key results callouts (3 stats: e.g. "Lost 12kg", "Deadlifts 80kg", "Training 18 months")
Trainer quote
Internal link → relevant blog article
CTA → Book Your Strength Assessment
```

**SEO per page (RankMath):**
- Primary keyword in title, H1, first paragraph, meta description
- Testimonial schema: `@type: Testimonial`, `author`, `reviewBody`, `itemReviewed`
- Target: 600-900 words per page (substantive enough for AIO)

**URL structure:** `theevolvedgym.com.au/results/[goal-keyword-life-stage]`
Examples:
- `/results/postmenopause-weight-loss-strength-training`
- `/results/perimenopause-bone-health-brisbane`
- `/results/postpartum-strength-training-return`

**Files affected:**
- WordPress: `results-single.php` template
- `outputs/systems/social-proof-pages.md` (index populated as pages are built)

---

### Step 8: Migrate 22 Social Proof Stories

For each of the 22 existing stories:

**Actions:**
- Create a new `results` post in WordPress
- Assign goal taxonomy tag(s): weight-loss / strength / bone-health / aesthetics / mental-health / energy / hormonal-health / return-to-fitness
- Assign life stage taxonomy tag(s): teens / 20s-30s / perimenopause / postmenopause / postpartum / pregnancy
- Write the page to template (from existing story content)
- Set keyword-based slug
- Configure RankMath primary keyword and meta description
- Add to Social Proof Page Index in `outputs/systems/social-proof-pages.md`

**Files affected:**
- `outputs/systems/social-proof-pages.md` (index built out)
- `outputs/systems/sa-prequalification-sop.md` (Social Proof Page Index populated)

---

### Step 9: Write Homepage Copy

Before any design work, finalise all copy. The homepage has no menu — every word must earn its place.

**Homepage sections:**

**1. Hero**
- Headline: "Brisbane's Leading Women-Only Gym" (retain — performing well)
- Subheadline: One sentence on what the Strength Assessment reveals and why it matters.
- CTA button: "Book Your Strength Assessment" → links to `/strength-assessment`
- Visual: Full-screen hero — photo of Megan coaching women in the gym (current asset, retain). Dark overlay for text legibility. GSAP fade-in on load.

**2. The Science (Sarcopenia Infographic)**
- Heading: "After 30, you're losing muscle every year. Most women don't know how much."
- Infographic: Interactive sarcopenia curve (see Step 10)
- Supporting copy: 2-3 sentences connecting muscle loss to their goals (strength, metabolism, longevity, aesthetics)
- CTA: "Find out exactly where you stand → Book Your Strength Assessment"

**3. Why Frequency Matters (Training Frequency Infographic)**
- Heading: "The difference between 1x and 3x per week isn't 3x the results — it's 9x."
- Infographic: Interactive training frequency vs results curve (see Step 11)
- Supporting copy: Barbells and dumbbells as the cornerstone. Everything else is complimentary — Pilates, cardio, yoga supplement but cannot replace progressive strength training.
- CTA: "Your trainer will prescribe the right frequency → Book Your Strength Assessment"

**4. What the Strength Assessment Is**
- 3-column layout: What happens / What you discover / What comes next
- Pre-frame copy from SOP Stage 3: "This is not a gym tour. Not a free trial. It's a structured evaluation..."
- Duration, location, what to expect

**5. Social Proof Teaser**
- 3 featured results cards (pull quote + name + life stage + goal)
- "See more results →" links to `/results/` archive page

**6. Final CTA**
- Full-width dark section
- Repeat headline variant
- Single CTA button

**Files affected:**
- `reference/homepage-copy.md` (finalised copy stored here)

---

### Step 10: Build Sarcopenia Curve Infographic

Interactive Chart.js visualisation showing muscle mass decline by age, with and without strength training.

**Data points (based on published sarcopenia research):**

| Age | No Training (% of peak) | With Strength Training (% of peak) |
|-----|------------------------|-------------------------------------|
| 20  | 100% | 100% |
| 30  | 97%  | 99%  |
| 40  | 91%  | 97%  |
| 50  | 82%  | 93%  |
| 60  | 70%  | 88%  |
| 70  | 56%  | 80%  |
| 80  | 42%  | 70%  |

**Interaction design:**
- Two curves rendered on load (No Training = muted/grey, With Training = pink)
- User selects their age bracket via button group (20s / 30s / 40s / 50s / 60s+)
- On selection: dot appears on both curves at their age, annotation appears:
  - "At your age, without strength training you may have already lost X% of your peak muscle mass"
  - "Women who train consistently maintain significantly more — the gap widens every decade"
- GSAP animates the dot appearing and the annotation fading in
- Below chart: "The Strength Assessment measures exactly where you are on this curve."
- CTA button pulses (GSAP keyframe) after selection

**Technical implementation:**
```javascript
// Chart.js config skeleton
const sarcopeniaChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['20', '30', '40', '50', '60', '70', '80'],
    datasets: [
      {
        label: 'Without strength training',
        data: [100, 97, 91, 82, 70, 56, 42],
        borderColor: '#666',
        borderDash: [5, 5],
      },
      {
        label: 'With consistent strength training',
        data: [100, 99, 97, 93, 88, 80, 70],
        borderColor: '#e43388',
      }
    ]
  },
  options: { responsive: true, interaction: { mode: 'index' } }
});
```

**Files affected:**
- `reference/infographic-sarcopenia-data.md` (data + annotation copy)
- WordPress: custom block or shortcode in homepage template

---

### Step 11: Build Training Frequency Infographic

Interactive Chart.js visualisation showing cumulative results by training frequency over 52 weeks.

**Design concept:**
- X-axis: Weeks (0–52)
- Y-axis: Relative strength/results index (0–100)
- Three curves: 1x/week, 2x/week, 3x/week
- Curves show compounding — the gap widens non-linearly over time

**Interaction design:**
- On load: all three curves visible, labelled
- Hover/click on any curve: highlights that line, shows annotation for that frequency
- "Minimum effective dose" threshold line (dotted, labelled) — shows 1x/week barely clears it
- Below chart: "Barbells and dumbbells are the cornerstone. Pilates, cardio, and yoga are complimentary — they support your training but cannot replace it."
- CTA: "Your trainer recommends the right frequency for your goals after your assessment."

**Files affected:**
- `reference/infographic-frequency-data.md` (data + annotation copy)
- WordPress: custom block or shortcode in homepage template

---

### Step 12: Build the Homepage in WordPress

Assemble all sections into a single Blocksy page with no navigation header.

**Actions:**
- Create new WordPress page: "Home" — set as front page
- Set page template to full-width (no header navigation, no footer nav)
- Keep footer minimal: address, phone, ABN — no nav links
- Add custom CSS to `style.css` (child theme):
  - Evolve existing colour palette: keep dark backgrounds (#0a0a0a / #111), keep primary pink (#e43388), add warm off-white (#f5f0eb) for text contrast
  - Smooth scroll behaviour: `scroll-behavior: smooth`
  - Section transitions: GSAP ScrollTrigger fires animations as sections enter viewport
- Animations per section:
  - Hero: fade-in headline, slide-up subheadline, pulse on CTA button
  - Infographic sections: slide in from left on scroll
  - Social proof cards: stagger fade-in
  - Final CTA: scale-up on enter

**GSAP ScrollTrigger skeleton:**
```javascript
gsap.registerPlugin(ScrollTrigger);

gsap.from('.hero-headline', {
  opacity: 0, y: 40, duration: 1, ease: 'power3.out'
});

gsap.from('.section-infographic', {
  opacity: 0, x: -60, duration: 0.8,
  scrollTrigger: { trigger: '.section-infographic', start: 'top 80%' }
});
```

**Files affected:**
- WordPress homepage
- Child theme `style.css`
- Child theme `custom.js`

---

### Step 13: DNS Cutover (Manual — You Action, I Provide Exact Steps)

**Pre-cutover checklist:**
- [ ] WordPress on root domain tested and working on staging/preview
- [ ] All 22 social proof pages built and reviewed
- [ ] Homepage copy approved
- [ ] 301 redirect rules loaded into WordPress Redirection plugin
- [ ] GHL domain change confirmed (go.theevolvedgym.com.au ready)
- [ ] GHL audit complete — all hardcoded URLs updated in workflows
- [ ] Google Analytics tracking code updated to root domain

**DNS changes (at your registrar):**
1. Change A record for `theevolvedgym.com.au` → WordPress hosting IP
2. Add CNAME for `go.theevolvedgym.com.au` → GHL custom domain
3. Keep `links.theevolvedgym.com.au` CNAME unchanged
4. Add CNAME for `www.theevolvedgym.com.au` → `theevolvedgym.com.au` (if not already)
5. TTL: set to 300 (5 min) before cutover, restore to 3600 after

**GHL change:**
- GHL → Settings → Business Profile → Website → change from `theevolvedgym.com.au` to `go.theevolvedgym.com.au`

---

### Step 14: Post-Migration Checks

**Actions:**
- Verify all blog URLs resolve correctly at `theevolvedgym.com.au/blog/`
- Verify `blog.theevolvedgym.com.au/[article]` redirects to `theevolvedgym.com.au/blog/[article]` (301)
- Verify `go.theevolvedgym.com.au` loads GHL site correctly
- Verify `links.theevolvedgym.com.au` forms/booking pages still work (should be unaffected)
- Test SA booking CTA from homepage end-to-end
- Test all 22 social proof pages load correctly
- Check Google Search Console — add `theevolvedgym.com.au` as new property, submit sitemap
- Check Google Analytics — confirm traffic is tracking on root domain
- Run Screaming Frog (or equivalent) crawl to catch any broken internal links

---

### Step 15: Update Workspace Documentation

**Actions:**
- Update `outputs/systems/blog-catalog.md` — replace all `blog.theevolvedgym.com.au` URLs with `theevolvedgym.com.au/blog/`
- Populate `outputs/systems/social-proof-pages.md` with full index of 22 pages
- Populate Social Proof Page Index in `outputs/systems/sa-prequalification-sop.md`
- Update `CLAUDE.md` — add website architecture section

**Files affected:**
- `outputs/systems/blog-catalog.md`
- `outputs/systems/social-proof-pages.md`
- `outputs/systems/sa-prequalification-sop.md`
- `CLAUDE.md`

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-04-02-sa-prequalification-ai-agent.md` — pre-qual bot Stage 2F sends social proof links (unblocked when pages are live)
- `plans/2026-04-27-blog-bot.md` — blog content pipeline depends on root domain consolidation for internal linking to work correctly
- `outputs/systems/sa-prequalification-sop.md` — Social Proof Page Index populated in Step 8
- GHL workflows: SA booking link (`custom_values.strength__longevity_assessment`) — confirm URL is on `links.` subdomain (unaffected) or root (needs update)

### Updates Needed for Consistency

- `outputs/systems/blog-catalog.md` — all blog URLs update from subdomain to root
- `outputs/systems/sa-prequalification-sop.md` — Social Proof Page Index populated
- All GHL email and SMS templates containing hardcoded blog URLs

### Impact on Existing Workflows

- SA booking flow: unaffected if booking page is on `links.theevolvedgym.com.au`
- GHL conversation triage: unaffected
- Discord bot / daily reports: unaffected
- Hold system, Stripe webhook: unaffected

---

## Validation Checklist

- [ ] `theevolvedgym.com.au` serves WordPress homepage (not GHL)
- [ ] Homepage has no navigation menu
- [ ] Single CTA (Book Strength Assessment) present in hero, after each infographic, and final section
- [ ] Sarcopenia infographic interactive — age selection updates chart and annotation
- [ ] Training frequency infographic interactive — hover/click highlights curves
- [ ] GSAP scroll animations fire correctly on all sections
- [ ] All 22 social proof pages live at `/results/[keyword]`
- [ ] RankMath configured on all results pages with Testimonial schema
- [ ] `blog.theevolvedgym.com.au/[article]` → `theevolvedgym.com.au/blog/[article]` (301, not 302)
- [ ] `go.theevolvedgym.com.au` serves GHL site
- [ ] `links.theevolvedgym.com.au` forms and booking pages unaffected
- [ ] Google Search Console root domain property verified and sitemap submitted
- [ ] No broken links found in post-migration crawl
- [ ] `outputs/systems/social-proof-pages.md` populated with all 22 pages
- [ ] `outputs/systems/blog-catalog.md` URLs updated
- [ ] CLAUDE.md updated with website architecture

---

## Success Criteria

1. `theevolvedgym.com.au` homepage loads in under 3 seconds, serves WordPress, displays the sniper page with working interactive infographics and a single visible CTA
2. All 21+ blog articles accessible at `theevolvedgym.com.au/blog/[slug]` with zero content loss
3. All 22 social proof pages live at `theevolvedgym.com.au/results/[keyword]` with RankMath + Testimonial schema configured
4. Zero broken links — all `blog.theevolvedgym.com.au` URLs redirect correctly with 301
5. GHL booking funnels fully operational on `go.theevolvedgym.com.au` and `links.theevolvedgym.com.au`
6. Pre-qual bot Stage 2F can be activated — social proof page index is complete

---

## Notes

---

## Implementation Notes

**Implemented:** 2026-04-30

### Summary
- Created `outputs/systems/website-architecture.md` — full domain map, URL structure, DNS config, pre-cutover checklist
- Created `scripts/audit-ghl-urls.py` — scans GHL workflows, email/SMS templates, and custom values for hardcoded domain URLs
- Created `scripts/redirects.conf` — Apache, Nginx, and Cloudflare redirect rules for blog subdomain → root domain migration
- Created `reference/homepage-copy.md` — finalised copy for all 6 homepage sections
- Created `reference/infographic-sarcopenia-data.md` — data points, interaction design, full Chart.js + GSAP implementation code, HTML structure
- Created `reference/infographic-frequency-data.md` — data points, interaction design, full Chart.js + GSAP implementation code, HTML structure
- Created `reference/homepage-implementation.md` — Blocksy child theme setup (style.css, functions.php, homepage.js), WordPress page setup, RankMath config, CDN URLs, testing checklist
- Created `outputs/systems/social-proof-pages.md` — 22-page index with slugs, goal/life-stage taxonomy, pre-qual bot matching logic, content sprint priority order
- Updated `CLAUDE.md` — added website architecture section and updated workspace structure to include new scripts and reference files

### Current status (2026-05-07)

Everything is built and ready. 27 results pages live (exceeded 22 target). Homepage live at WP ID 165. RankMath installed. Results CPT active.

**4 actions remaining for DNS cutover — do these in order:**

1. **SiteGround Site Tools → Domains** — add `theevolvedgym.com.au` as primary domain pointing to the existing WordPress install. SSL will auto-provision via Let's Encrypt.

2. **WordPress Admin → Settings → General** — update both Site URL and Home URL from `http://blog.theevolvedgym.com.au` to `https://theevolvedgym.com.au`

3. **GHL → Settings → Business Profile → Website** — change from `theevolvedgym.com.au` to `go.theevolvedgym.com.au`

4. **DNS registrar** — flip these records:
   - A record `theevolvedgym.com.au` → SiteGround WordPress IP
   - CNAME `go.theevolvedgym.com.au` → GHL custom domain
   - CNAME `blog.theevolvedgym.com.au` → `theevolvedgym.com.au` (triggers 301 redirects)
   - Set TTL to 300 before cutover, restore to 3600 after

**After cutover — verify:**
- `theevolvedgym.com.au` loads WordPress homepage
- `blog.theevolvedgym.com.au/[article]` redirects to `theevolvedgym.com.au/blog/[article]`
- `go.theevolvedgym.com.au` loads GHL site
- SA booking CTA works end-to-end
- Add `theevolvedgym.com.au` property to Google Search Console + submit sitemap

### Deviations from Plan
- `blog-catalog.md` URL update (Step 15) not needed — no `blog.theevolvedgym.com.au` URLs were found in that file (articles were catalogued without full URLs)

---

**Phase sequencing recommendation:**
Build and review the social proof pages and homepage copy (Steps 6–12) before touching DNS. The cutover (Step 13) should be a clean 30-minute switch, not a build-in-production situation.

**Infographic data source:** Sarcopenia data references published research (Baumgartner et al., Janssen et al.). Exact figures should be reviewed against the most current meta-analyses before publication — the blog doctrine references Dr Stacy Sims, Dr Gabrielle Lyon, and Dr Vonda Wright as approved experts.

**Blocksy Companion:** Confirmed active. No Pro licence required — full-width templates and custom JS injection handled via Blocksy child theme.

**Social proof page content creation:** 22 stories need to be written to the template format (500-800 words each). This is a content sprint — could be partially automated by blog bot when live, but initial set should be human-written and reviewed.

**Future:** Once social proof pages are live and the pre-qual bot is operational, the Pre-Qual Insights tab begins receiving structured goal data. The blog bot can then suggest new results page topics from real member language — the content flywheel becomes self-feeding.
