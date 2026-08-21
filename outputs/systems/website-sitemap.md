# Website V2 Sitemap & Root-Promotion Register
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-08-04
**Authority:** `outputs/systems/website-v2-release-manifest.md`

---

## Overview

**Current state:** `theevolvedgym.com.au` points to the older GHL site.
Website V2 is already built and live on WordPress at
`blog.theevolvedgym.com.au`. The legacy article site remains live on
`evolved-woman.theevolvedgym.com.au`. `go.theevolvedgym.com.au` did not
resolve at the Phase 1 snapshot.

**Target state:** Promote that existing Website V2 release to
`theevolvedgym.com.au`. GHL remains the operational CRM, workflow,
communication, form, funnel, calendar and booking system on `go.` and
`links.`.

DNS cutover happens only after the V2 reproduction, GHL journey,
exact-redirect and rollback gates in
`plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md` pass.

---

## Page Inventory

### WordPress Route Groups

| Route group | Snapshot count | Status | Notes |
|---|---|---|
| Standard pages | 24 published, 1 draft | Built and browser verified as Website V2 on `blog.` | Includes authoritative homepage post 165, Team, trainers, services, memberships, locations and Legal |
| Results | 35 published | Built and browser verified on `blog.` | SEO and duplicate-source repairs remain |
| Articles | 1 published, 20 drafts | Partial | `/blog/` architecture not configured; draft slugs are empty |
| Missing legacy imports | 2 | Not built | Two live legacy articles have no WordPress record |

The full WordPress page and Results indexes are retained in `outputs/systems/website-architecture.md`.

---

### WordPress Marketing Routes

#### Trainer Pages

| URL | Status | Content Notes |
|---|---|---|
| `/leisa-personal-trainer-brisbane` | Built on WordPress | Retain and review |
| `/piper-personal-trainer-brisbane` | Built on WordPress | Retain and review |
| `/megan-personal-trainer-brisbane` | Built on WordPress | Retain and review |
| `/marnie-personal-trainer-brisbane` | Built, former trainer | Preserve until the redirect destination is approved and tested |
| `/nora-personal-trainer-brisbane` | Not built | Requires approved bio, image, specialties and copy |
| `/katrina-personal-trainer-brisbane` | Not built | Requires approved bio, image, specialties and copy |

**Team hub page:**

| URL | Status | Content Notes |
|---|---|---|
| `/team` | Built; roster update pending | WordPress page exists; local source is corrected to Megan, Piper, Nora, Katrina and Leisa but is not a verified live deployment |

#### Membership Pages

| URL | Status | Content Notes |
|---|---|---|
| `/memberships` | Built on WordPress | Membership hub |
| `/memberships/sculptstrength` | Built on WordPress | Retain pending membership-architecture decision |
| `/memberships/fitflex` | Built on WordPress | Retain |
| `/memberships/fasttrack` | Built on WordPress | Retain |
| `/memberships/evolve-u-program` | Built on WordPress | Retain |

#### Services Pages

| URL | Status | Content Notes |
|---|---|---|
| `/services` | Built on WordPress | Hub page |
| `/services/personal-training-brisbane` | Built on WordPress | 1:1 PT marketing page |
| `/services/small-group-personal-training-brisbane` | Built on WordPress | SGPT marketing page |
| `/services/nutrition-lifestyle-coaching-brisbane` | Built on WordPress | Nutrition coaching marketing page |
| `/services/strength-assessment-for-women-brisbane` | Built on WordPress | SEO page; booking stays in GHL |

#### Location Pages

| URL | Status | Content Notes |
|---|---|---|
| `/locations` | Built on WordPress | Location hub |
| `/locations/west-end-brisbane` | Built on WordPress | Open location |
| `/locations/bulimba` | Built on WordPress | Coming-soon marketing page |
| `/locations/new-farm` | Built on WordPress | Coming-soon marketing page |
| `/locations/coolangatta` | Built on WordPress | Coming-soon marketing page |
| `/locations/townsville` | Built on WordPress | Coming-soon marketing page |
| `/locations/chermside` | Built on WordPress | Coming-soon marketing page |

The separate GHL `/coming-to-*` form pages and their thank-you pages remain GHL operational routes. They are not replaced by the WordPress location pages.

#### Other

| URL | Status | Content Notes |
|---|---|---|
| `/legal` | Built on WordPress | Canonical current WordPress legal page |
| `/terms-of-use-and-privacy-policy` | Broken old internal target | Repair the link and decide whether this old path redirects to `/legal` |

---

### Retain in GHL on `go.theevolvedgym.com.au`

These are the 19 **public root paths that require exact redirects**. They are
not the complete GHL preservation boundary. After `go.` works and every route
passes functional testing, the matching old root path can redirect to the same
path on `go.`.

| Current URL | Redirects To | Reason |
|---|---|---|
| `/strength-assessment` | `go.theevolvedgym.com.au/strength-assessment` | GHL booking funnel |
| `/30dnnc` | `go.theevolvedgym.com.au/30dnnc` | GHL lead-generation funnel |
| `/30dnnc-thankyou` | `go.theevolvedgym.com.au/30dnnc-thankyou` | GHL post-form page |
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
| `/coming-to-coolangatta-tweed-heads` | `go.theevolvedgym.com.au/coming-to-coolangatta-tweed-heads` | GHL location-interest form |
| `/coming-to-bulimba` | `go.theevolvedgym.com.au/coming-to-bulimba` | GHL location-interest form |
| `/coming-to-newfarm` | `go.theevolvedgym.com.au/coming-to-newfarm` | GHL location-interest form |
| `/thank-you-coolangatta-tweed` | `go.theevolvedgym.com.au/thank-you-coolangatta-tweed` | GHL post-form page |
| `/thank-you-bulimba` | `go.theevolvedgym.com.au/thank-you-bulimba` | GHL post-form page |
| `/thank-you-newfarm` | `go.theevolvedgym.com.au/thank-you-newfarm` | GHL post-form page |

**Note:** Before DNS cutover, bind these exact GHL pages to `go.` and test forms, calendars, thank-you transitions, tracking and mobile behaviour. No redirect mechanism has been selected or installed.

### Complete captured GHL path surface

The Phase 3 read-only audit extracted every public page alias and configured
funnel step from the protected GHL HTML. The owner-confirmed Pregnancy route
raises the known lower bound to **85 unique GHL paths**, governed by
`outputs/systems/website-v2-ghl-route-register.json`.

| Disposition | Count | Rule |
|---|---:|---|
| WordPress serves the root path | 16 | Preserve the old matching GHL page on `go.` through observation |
| Root redirects to the same path on `go.` | 19 | Exact single-hop rule with query preservation |
| Preserve on `go.` without an automatic root redirect | 50 | Internal, confirmation, agreement, booking or legacy GHL step |
| WordPress technical path | 2 | `/robots.txt` and `/sitemap.xml` |

The 50-path group includes life-stage Strength Assessment and booking
confirmation steps, PT and membership agreement pages, confirmation pages,
Intro Session booking and other GHL steps that the public crawl did not expose.
It must not be discarded because it was absent from the earlier 19-route
table.

The Pregnancy organic funnel's owner-confirmed thank-you and Strength
Assessment page is `/pppsa-page-1536`. It returns 200, and its public metadata
matches the captured organic funnel, middle step, page and existing
booking-confirmation next step. Funnel next-step logic overrides the embedded
form fallback.

The same middle step's Publishing field exposes stale alias `/pppsa-5667`,
which returns 404. Preserve it until its separate disposition is tested. The
standalone organic form fallback was corrected from paid route `/pppsa` to
`/pppsa-page-1536`; neither funnel sequence nor paid route changed.

---

## Approval-Gated Root-Promotion Sequence

This is the delivery sequence. It does not authorise live changes.

| # | Work | Gate |
|---|---|---|
| 1 | Confirm the governed source mirror matches the live V2 release | Local and live drift checks |
| 2 | Design and run an isolated root-host rehearsal of the existing V2 | V2 appearance and behaviour parity |
| 3 | Repair `/blog`, the old legal target, canonicals and hardcoded hostname behaviour in rehearsal | Clean staging crawl |
| 4 | Bind and test all retained GHL routes on `go.`, including every V2 homepage waitlist journey | GHL functional acceptance |
| 5 | Build exact current-root and media-safe `blog.` route rules | Redirect review |
| 6 | Rehearse cutover and rollback using final hostnames | Rehearsal acceptance |
| 7 | Take a fresh snapshot, then change production only with explicit approval | Owner cutover approval |

Article imports, trainer pages and Results SEO remain protected work, but they
do not enter this sequence unless Peter explicitly changes the root-promotion
gate.

---

## Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Nora and Katrina trainer pages | Build new in WordPress | Need approved bios, photos and specialties from user |
| Former Marnie trainer URL | Redirect after removing live team links | Choose the Team hub or Personal Training service page as the canonical destination |
| `/30dnnc` long-term | Keep in GHL at `go.` or rebuild in WordPress | Keep in GHL |
| Location-interest and thank-you pages | Stay in GHL or rebuild | Keep in GHL on exact `go.` paths |
| 23 legacy article slugs | Preserve legacy slug or approve improved `/blog/` slug | Decide row by row before publication |
| Five legacy categories | WordPress categories, curated guide pages or `/blog/` | Decide by search intent and content match |
| Legacy Team and Our Mission | Team page, homepage or another approved destination | Exact mapping required |
| `evolved-woman` subdomain | Retire after exact mappings pass | Keep live until all 31 unique live URLs are covered |

---

## Page Count Summary

| Category | Count | Status |
|---|---|---|
| Website V2 standard pages | 24 published, 1 draft | Built on `blog.`; root promotion and hostname verification remain |
| WordPress Results | 35 published | Preserve all; SEO repairs remain |
| WordPress articles | 1 published, 20 drafts | Blog structure and slug work remain |
| Legacy substantive articles | 23 live | 21 have WordPress records; 2 are missing imports |
| New trainer pages | 2 | Nora and Katrina |
| Original Results archetypes still unbuilt | 4 | Teens ×3, IVF ×1; retained backlog |
| GHL known path lower bound retained on `go.` | 85 | 19 public root redirects, 50 additional go-only paths and 16 preserved GHL copies of WordPress-owned paths |
| Unique captured legacy live URLs | 31 | Exact destinations required |
| Captured legacy 404 records | 66 | Classify before retirement |

The former 34-page estimate and the superseded rebuild/transfer decision list
are retained for history, but neither is an authority for V2 delivery.
