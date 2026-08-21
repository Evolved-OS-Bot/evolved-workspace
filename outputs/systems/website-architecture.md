# Website Architecture — The Evolved
**Version:** 2.4
**Created:** 2026-04-30
**Last Updated:** 2026-08-04 (Cloudflare rollback boundary)
**Owner:** The Evolved — Operations

---

## Authority and Scope

The canonical product authority is
`outputs/systems/website-v2-release-manifest.md`. The approval-gated delivery
plan is
`plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`.
The complete captured GHL preservation boundary is
`outputs/systems/website-v2-ghl-route-register.json`, and the current
read-only promotion evidence and rehearsal design are in
`outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`.

Website V2 is already built and live on WordPress at
`blog.theevolvedgym.com.au`. The remaining delivery objective is to promote
that existing release to the root domain. It is not a rebuild or a choice
between the WordPress and GHL homepages.

The promotion does not replace GHL. GHL remains the CRM, communications,
workflow, funnel, form, calendar and booking system.

The April migration and animation plans remain unchanged in `plans/archive/`
as implementation history. The superseded 4 August rebuild/transfer documents
also remain preserved, but they are not current authorities.

---

## SSH Deploy Reference

**WordPress root:** `/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html`
**SSH alias:** `evolved-prod` (configured in `~/.ssh/config`)
**Homepage post ID:** 165

**Release-control warning:** Read the V2 manifest and run
`python3 scripts/check_website_v2_drift.py` before planning or deploying.
Direct production deployment is incomplete unless the clean source mirror,
hash register, release register and live read-back are updated in the same
release.

**Historical direct deploy pattern, retained for reference:**
```bash
# 1. SCP the file
scp /tmp/homepage-v5.html \
  evolved-prod:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/homepage-v5.html

# 2. Write to DB + flush caches
ssh evolved-prod "
  cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
  wp eval 'global \$wpdb; \$wpdb->update(\$wpdb->posts, [\"post_content\" => file_get_contents(\"/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/homepage-v5.html\")], [\"ID\" => 165]);'
  wp cache flush && wp transient delete --all && wp sg purge
"
```

**Note:** `scripts/.env` cannot be `source`d directly — `GOOGLE_KPI_SHEET_NAME=KPI's The Evolved` contains an unmatched single quote that breaks shell parsing.

---

## Domain Map

### Current Live State as at 4 August 2026

| Domain | Platform | Purpose |
|---|---|---|
| `theevolvedgym.com.au` | GHL through Cloudflare | Current older root site; provider A `162.159.140.166`, proxied, Auto TTL |
| `www.theevolvedgym.com.au` | GHL through Cloudflare | CNAME `sites.ludicrous.cloud`, proxied, Auto TTL |
| `go.theevolvedgym.com.au` | Unresolved | No published DNS record at the 4 August Phase 3 audit |
| `links.theevolvedgym.com.au` | GHL | Short links and QR codes |
| `blog.theevolvedgym.com.au` | WordPress / SiteGround | Complete live Website V2, pages, Results and imported article records |
| `evolved-woman.theevolvedgym.com.au` | Legacy GHL site | Legacy blog, categories, Team and Our Mission |

The complete owner-authenticated provider snapshot is
`outputs/systems/website-v2-cloudflare-rollback-snapshot-2026-08-04.md`.
It preserves the 29-record export, proxy states, current rules and SSL/TLS
settings without changing Cloudflare.

### Approved Target

| Domain | Platform | Purpose |
|---|---|---|
| `theevolvedgym.com.au` | WordPress / SiteGround | Public homepage, marketing pages, blog and Results |
| `www.theevolvedgym.com.au` | Canonical redirect | Redirect to the root WordPress hostname |
| `go.theevolvedgym.com.au` | GHL | Funnels, forms, booking pages, Strength Assessment and post-conversion pages |
| `links.theevolvedgym.com.au` | GHL | Short links and QR codes, unchanged |
| `blog.theevolvedgym.com.au` | Transitional hostname | Media-safe exact redirects after root cutover |
| `evolved-woman.theevolvedgym.com.au` | Transitional legacy host | Exact redirects only after all 31 unique live URLs have destinations |

---

## Target URL Structure

### WordPress Root Domain

| Path | Type | Description |
|---|---|---|
| `/` | WordPress page | Existing Website V2 homepage, post ID 165 |
| Standard marketing routes | WordPress pages | Team, current trainers, services, memberships, locations and Legal |
| `/blog/` | Archive | Blog article index |
| `/strength-training-for-women/` | Post | Existing published article; retain its current path during root promotion |
| `/blog/[approved-slug]/` | Future post architecture | Protected article-migration work; do not change global permalinks during root promotion |
| `/results/` | CPT Archive | Social proof page index |
| `/results/[goal-keyword-life-stage]/` | CPT Single | Individual member result story |

### GHL (go.theevolvedgym.com.au)

| Path | Description |
|---|---|
| `/strength-assessment` | SA booking funnel used after waitlist entry and in re-engagement, not as the V2 homepage's direct CTA |
| 19 public root redirect paths | Same-path redirects from the WordPress root to retained GHL routes on `go.` |
| 50 additional known paths | Internal, confirmation, agreement, booking and legacy GHL steps preserved on `go.` without automatic root redirects |
| 16 paths also owned by WordPress on the root | Preserve the matching GHL source paths on `go.` through the observation window; do not delete them |

The governed register contains a known lower bound of 85 unique GHL paths.
The earlier 19-route proposal was only the public root-redirect subset, not the
complete GHL preservation boundary. None of the routes has been moved, and the
Pregnancy organic funnel's working thank-you and Strength Assessment page is
`/pppsa-page-1536`. Its public metadata matches the captured organic funnel,
middle step, page and booking-confirmation next step.

The middle step's Publishing field also exposes stale alias `/pppsa-5667`,
which returns 404. Funnel next-step logic overrides the embedded form fallback,
so that stale alias is not evidence of a broken submission journey. Preserve
both paths until the stale alias receives a separately tested disposition.
The standalone organic form fallback was owner-approved and corrected from
the paid `/pppsa` page to `/pppsa-page-1536`.

The five captured paid life-stage pages embed the matching organic form rather
than their separately documented paid form. Preserve the dormant paid pages
and steps, but do not reactivate paid traffic before a separate controlled
repair and end-to-end test.

---

## Proposed Key URL Changes

| Before | After | Type |
|---|---|---|
| GHL public marketing pages on `theevolvedgym.com.au` | Equivalent WordPress root routes | WordPress takes over public marketing and SEO |
| `theevolvedgym.com.au/strength-assessment` | `go.theevolvedgym.com.au/strength-assessment` | GHL booking funnel retained on `go.` |
| Other retained GHL operational root paths | Same path on `go.theevolvedgym.com.au` | GHL journeys retained |
| Existing WordPress page, Result or published article on `blog.` | Same current path on the WordPress root | Host-conditional exact redirect; do not force the article under `/blog/` during root promotion |
| `evolved-woman.theevolvedgym.com.au/[legacy-path]` | Approved WordPress or retained GHL destination | Exact legacy redirect |

---

## GHL Website-Dependency Classification

| Custom Value | Old Value | New Value |
|---|---|---|
| `{{custom_values.strength__longevity_assessment}}` | `theevolvedgym.com.au/strength-assessment` | Proposed: `go.theevolvedgym.com.au/strength-assessment`, only after that route passes testing |

The Phase 1 audit found six GHL custom values and 43 rendered email-template
references. Four Strength Assessment references and three location-interest
references are candidates for `go.` after testing; eight homepage references
remain on the WordPress root; three Results custom values remain on the root;
the PAR-Q value remains on `links.`; and 28 already-broken legacy or dormant
resource references require separate review. Do not perform a global
replacement, guess destinations or alter unrelated GHL workflows or templates.

The V2 homepage's primary CTAs remain the waitlist journey defined in
`reference/conversion-funnel.md`: pre-selection CTAs anchor to Pick Your
Journey, and post-selection CTAs route to the matching organic life-stage page.
Do not redirect them directly to Strength Assessment.

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

**Product:** Existing Website V2

**Live runtime:** `https://blog.theevolvedgym.com.au/`

**Editing authority:** WordPress post ID 165 plus the governed mirror at
`wordpress/website-v2/source/`.

**No normal navigation header:** This is an implemented V2 conversion-design
decision, not an unresolved architecture question.

**Primary CTA:** `Join the Waitlist`

**Journey authority:** `reference/conversion-funnel.md`

| Section | Purpose |
|---|---|
| Hero | V2 positioning and waitlist entry |
| Pick Your Journey | Life-stage and goal selection |
| Personalised Results Curve | Profile-based 12-month outcome journey |
| Member and Results sections | Contextual proof |
| Memberships and timetable | Current offer and delivery context |
| Reviews and FAQ | Objection handling and trust |
| Waitlist blocks and sticky CTA | Profile-aware organic GHL waitlist routing |

The V2 source was live-verified on 4 August 2026 with 17 homepage sections and
`homepage.js?ver=59.0`. A proposal to replace it with the older GHL homepage,
merge the two homepages or restore the direct Strength Assessment CTA is a new
redesign and requires explicit owner approval.

---

## Target DNS and Host Configuration

This table is a requirement map, not a record of current DNS and not approval to change it.

| Host | Required outcome |
|---|---|---|
| `theevolvedgym.com.au` | Serve the approved SiteGround WordPress root |
| `www.theevolvedgym.com.au` | Canonicalise to `theevolvedgym.com.au` |
| `go.theevolvedgym.com.au` | The signed-in GHL register confirms there is no existing `go.` entry. During the separately approved additive connection, capture the account-specific DNS value, use a DNS-only Cloudflare CNAME and pass all 85 registered paths before root cutover; current HighLevel documentation gives `sites.ludicrous.cloud` as the manual candidate, not an account-verified value |
| `links.theevolvedgym.com.au` | Remain on GHL |
| `blog.theevolvedgym.com.au` | Preserve media and technical paths, then apply tested exact redirects |
| `evolved-woman.theevolvedgym.com.au` | Remain available until every live route has a tested destination |

---

## WordPress Tech Stack

| Component | Tool | Notes |
|---|---|---|
| Theme | Blocksy (+ child theme) | Already on blog, consistent design system |
| SEO | Rank Math | Installed; Results sitemap, meta and schema work remains |
| Animations | GSAP + ScrollTrigger (CDN) | Scroll-triggered section animations |
| Infographics | Chart.js (CDN) | Sarcopenia + frequency curves |
| Redirects | Not yet selected or installed | The captured plugin inventory contains no Redirection plugin; use only tested, media-safe exact rules |
| Analytics | Historical GA4 property `www.theevolvedgym.com.au` (`429372468`) under `info@theevolvedgym.com.au`, plus GHL form evidence | The current GHL root uses `G-RXM7LVC0VJ` and `GTM-TMW7CS6L`; V2 uses the separate business-owned `Evolved Blog` stream `G-W9KNRFKV5F` and Google tag `GT-TXBKBKZB` in the same property. Preserve the V2 stream record, disable only its front-end placement in rehearsal and prove exactly one governed root page view |

---

## Pre-Cutover Checklist

- [x] Phase 1 preservation baseline and independent checksum-verified copy complete
- [x] Website V2 identity, source mirror, release register and corrected promotion plan established
- [x] Existing Website V2 homepage selected: WordPress post ID 165
- [x] Owner-authenticated Cloudflare zone export, proxy states, rules and SSL/TLS rollback values captured
- [ ] Local and live V2 drift checks pass immediately before rehearsal
- [ ] WordPress configured on root domain in SiteGround (tested on staging)
- [ ] All 35 existing social proof pages reviewed and preserved
- [ ] Current V2 homepage appearance and waitlist behaviour match in rehearsal
- [ ] Create and test the `/blog` index without changing the global `/%postname%/` structure, and make the old legal target redirect once to `/legal/`
- [ ] Exact, media-safe redirects pass a staging crawl
- [ ] Account-specific GHL DNS value is captured during the approved additive connection and all 85 registered GHL paths are preserved on `go.theevolvedgym.com.au`
- [ ] All 19 operational root paths redirect once to the same path on `go.` and preserve query strings
- [ ] The Pregnancy funnel reaches `/pppsa-page-1536`, continues to its existing confirmation step and passes a controlled submission; `/pppsa-5667` remains preserved pending a separate disposition
- [ ] Every V2 waitlist route, form, thank-you page and booking transition passes
- [ ] Website-dependent GHL custom values and template references are classified and tested
- [ ] WordPress internal links, canonicals and hardcoded media URLs repaired in staging
- [x] V2 analytics ownership, property, web stream and Google tag destination are recorded
- [ ] The isolated root records one governed historical-stream page view without duplication
- [ ] DNS TTL reduced to 300 (5 min) before cutover
- [ ] Root DNS and redirect rollback rehearsed
- [ ] Fresh pre-cutover snapshot taken if production changed after 3 August
- [x] Business-owned Google Analytics connected to the root GHL website and 30DNNC subscriber page
- [x] Google Analytics Data API enabled for project `evolved-os`; first accepted Railway refresh completed
- [ ] Observe two complete 12-hour collections before promoting website conversion cards beyond shadow

### Protected post-promotion backlog

Nora and Katrina pages, the Marnie redirect, legacy article imports and
mappings, Results metadata/schema/images, duplicate archive-source repair and
the four unbuilt Results archetypes remain governed work. They are not
automatic root-promotion blockers unless the owner changes that gate. The
legacy article hostname remains live until its separate retirement checks pass.

### Governed website reporting

- The canonical GA4 measurement ID is `G-RXM7LVC0VJ` in the historical `info@theevolvedgym.com.au` account. Exact root-host history begins 23 October 2024.
- The temporary `G-HHTMC6J261` tag was removed after read-only access to the historical property was verified. The existing `GTM-TMW7CS6L` container remains unchanged.
- Railway reads only property `429372468` and exact host `theevolvedgym.com.au`.
- Page views, visitors and sessions come from GA4. A subscriber is one unique GHL contact whose earliest accepted submission is from the live `30DNNC Form` (`qB8xGGwhLdSGtbc3Z0EJ`).
- Repeated form submissions by the same contact count once. Completed reporting periods before 23 October 2024 remain unavailable rather than showing a false zero.
- The Operating Data Hub refreshes this source at 06:02 and 18:02 Brisbane. No Codex or ChatGPT schedule exists.
- The original subscriber ingestion on 2 August 2026 found 330 form submissions representing 304 unique subscribers. The first historical-property refresh populated 148 page views, 60 visitors and 7 subscribers for the completed week; 619, 261 and 22 for the completed 28 days; and 1,977, 858 and 68 for the completed 90 days.
- The historical-property switch also corrected the GA4 totals request so valid traffic cannot be represented as zero when Google returns an aggregate result row without a totals row. The regression is covered by the Hub test suite.
- Reporting V2 now connects the earliest accepted subscription for each GHL contact to the first qualifying Strength Assessment appointment created within 30 days. The live shadow rates are 28.6% for the completed week, 45.5% for 28 days and 47.1% for 90 days. Repeat forms, rebooks and SGPT/PT components count once at person level.

---

## WordPress Pages Index

**Inventory snapshot:** 2026-08-03 Phase 1 database capture

All 24 published pages below are part of the built Website V2 and were
browser-accessible on the current WordPress runtime hostname during Phase 1.
They do not yet serve the intended root hostname.

| Page | WP ID | URL | Template |
|---|---|---|---|
| Homepage | 165 | `/` | template-homepage.php |
| Piper (trainer) | 221 | `/piper-personal-trainer-brisbane` | template-trainer-page.php |
| Megan (trainer) | 226 | `/megan-personal-trainer-brisbane` | template-trainer-page.php |
| Marnie (former trainer; retire/redirect) | 227 | `/marnie-personal-trainer-brisbane` | template-trainer-page.php |
| Leisa (trainer) | 228 | `/leisa-personal-trainer-brisbane` | template-trainer-page.php |
| Team hub | 229 | `/team` | template-trainer-page.php |
| Services hub | 230 | `/services` | template-trainer-page.php |
| Personal Training | 231 | `/services/personal-training-brisbane` | template-trainer-page.php |
| Small Group PT | 232 | `/services/small-group-personal-training-brisbane` | template-trainer-page.php |
| Nutrition & Lifestyle | 233 | `/services/nutrition-lifestyle-coaching-brisbane` | template-trainer-page.php |
| Strength Assessment | 234 | `/services/strength-assessment-for-women-brisbane` | template-trainer-page.php |
| Memberships hub | 236 | `/memberships` | template-trainer-page.php |
| Fit & Flexible | 237 | `/memberships/fitflex` | template-trainer-page.php |
| Strong, Fit & Flexible Membership | 238 | `/memberships/sculptstrength` | template-trainer-page.php |
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

**Canonical current trainer roster:** Megan, Piper, Nora, Katrina and Leisa.

**Still to build:** Nora and Katrina trainer pages. The local Team hub source no longer includes Marnie, but the live WordPress state must be verified after any future deployment. Preserve Marnie's former page until the destination is approved and tested.

**Adding a new location:** Create WP page as child of 241, copy a coming-soon HTML file, update suburb name + nearby areas + precinct in ~5 places, deploy. West End page is the template for open locations.

---

## Results CPT Pages Index

**Inventory snapshot:** 2026-08-03 Phase 1 database capture

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
| Belinda — frozen shoulder 50s | 313 | `fifties-strength-frozen-shoulder-rehabilitation` |
| Orlagh — first timer 20s | 314 | `twenties-strength-first-timer-safe-space` |
| Peta — recomp/daily ritual 40s | 315 | `forties-strength-recomposition-daily-ritual` |
| Tess — desk worker/deadlift 30s | 316 | `thirties-strength-deadlift-desk-worker` |
| Laura — martial arts/mental health 20s | 317 | `twenties-strength-martial-arts-mental-health` |
| Sophie — career change/landscaping 40s | 318 | `forties-strength-career-change-landscaping` |

WordPress has 35 published Results stories. Within the original 22-row archetype plan, 18 are built and 4 remain without source members: teens ×3 and IVF ×1. The four remain in the content backlog but are not automatic DNS cutover blockers.

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 2.4 | 2026-08-04 | Added the owner-authenticated Cloudflare zone export, provider-side root and `www` restore values, rule boundary and SSL/TLS rollback state |
| 2.3 | 2026-08-04 | Added the owner-confirmed Pregnancy thank-you route, corrected funnel-next-step semantics and expanded the protected GHL lower bound to 85 paths |
| 2.2 | 2026-08-04 | Replaced the 19-route undercount with the 84-path GHL preservation register and added the Phase 3 rehearsal, Pregnancy-route and analytics gates |
| 2.1 | 2026-08-04 | Restored Website V2 as the existing live WordPress product, made post 165 authoritative, restored the waitlist CTA journey and separated root-promotion blockers from the protected backlog |
| 2.0 | 2026-08-04 | Separated current and target hosting, retained GHL as the operational system, corrected WordPress/blog/Results state and added preservation gates |
| 1.3 | 2026-07-30 | Recorded GHL as the live root-homepage authority and retained WordPress for blog/results content |
| 1.2 | 2026-05-13 | Added WP pages index + Results CPT index (moved from CLAUDE.md) |
| 1.1 | 2026-05-06 | Updated page IDs and Results CPT count |
| 1.0 | 2026-04-30 | Initial architecture documentation for root domain migration |
