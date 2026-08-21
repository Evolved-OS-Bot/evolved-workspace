# Website Rebuild and Transfer: Current-State Authority

**Snapshot date:** 4 August 2026
**Status:** Superseded and preserved for audit history
**Owner:** The Evolved
**Live changes made in Phase 2:** None

> **Correction recorded 4 August 2026:** This document incorrectly treated the
> existing WordPress V2 as a homepage candidate and reopened decisions that had
> already been implemented. It is preserved so no earlier work or evidence is
> lost, but it is not a current authority. Use
> `outputs/systems/website-v2-release-manifest.md` and
> `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`. Website V2
> is already built and live at `blog.theevolvedgym.com.au`; the active task is
> promotion of that product to the root domain, not a rebuild.

## Purpose

This document separates what is live now, what already exists in WordPress, what the approved target architecture is, and what still requires a decision or build. It is the dated authority for the next website phase.

The April plans remain unchanged as historical intent:

- `plans/archive/2026-04-29-website-migration-redesign.md`
- `plans/archive/2026-04-30-homepage-animation-redesign.md`

When those plans conflict with the 3 August preservation evidence or this document, use this document and the preservation evidence. Do not treat an old checked box or completion date as proof that a current route, asset, redirect or integration is ready.

## Non-Negotiable Interpretation

The website rebuild does not replace GoHighLevel.

- WordPress is the target public marketing, search and editorial website at `theevolvedgym.com.au`.
- GHL remains the CRM, communication, workflow, form, funnel and booking system.
- Public GHL routes that depend on the root domain are to be retained and rebound to `go.theevolvedgym.com.au`, or left on `links.theevolvedgym.com.au` where that is already their role.
- No GHL workflow, template, form, funnel, calendar or contact process is to be retired merely because WordPress takes over the public root domain.
- The Phase 1 GHL inventory is preservation and dependency evidence. Gaps in the supported GHL API are not website cutover blockers unless a specific affected GHL asset is proposed for retirement or reconstruction.

## Evidence and Preservation Boundary

The protected Phase 1 recovery point is:

`data/private/website-migration-baselines/2026-08-03-phase1/`

It contains:

- a complete 1.1 GB workspace snapshot;
- the complete 303 MB production WordPress filesystem and SQL database;
- hashes for 11,655 WordPress production files;
- 24 published WordPress pages, 1 draft page, 35 published Results stories, 1 published article, 20 draft articles and 111 registered attachments;
- read-only inventories for 143 GHL workflows and all 271 rendered GHL email templates;
- captures of 37 identified public GHL routes;
- 33 successful legacy-site captures, representing 31 unique live legacy URLs after normalising trailing-slash duplicates;
- records for 66 additional legacy URLs that returned 404;
- browser verification for 61 WordPress HTML routes.

The independent owner-only copy at `/Users/peterbrown/Documents/Evolved Website Backups/2026-08-03-phase1/` passed all 531 checksums.

No production page, GHL asset, DNS record, redirect, Git branch, stage or commit was changed during Phase 1 or Phase 2.

## Current and Target Platform Map

| Host | Current live state | Approved target | Classification |
|---|---|---|---|
| `theevolvedgym.com.au` | GHL, including the live homepage, marketing pages and operational funnel routes | WordPress public marketing and SEO site | Transfer required |
| `www.theevolvedgym.com.au` | Follows the current root/GHL arrangement | Canonicalise to the WordPress root | Cutover configuration required |
| `blog.theevolvedgym.com.au` | Live SiteGround WordPress site | Retained only long enough to support a safe hostname transition; editorial URLs move to root `/blog/` paths | Redirect and media plan required |
| `go.theevolvedgym.com.au` | No working DNS at the snapshot date | GHL funnels, forms, booking pages and post-conversion pages | Build/bind and verify before cutover |
| `links.theevolvedgym.com.au` | Live GHL short-link and QR-code host | Remains GHL | Keep |
| `evolved-woman.theevolvedgym.com.au` | Live legacy GHL blog and historical Team/Mission pages | Exact redirects after every substantive page has a verified destination | Preserve until mapping passes |

## Build Classification

### Built and Verified

- The SiteGround WordPress installation is running WordPress 7.0.2 with the Blocksy child theme active.
- All 61 discovered WordPress HTML routes passed browser navigation in Phase 1.
- WordPress contains 24 published standard pages, including the homepage candidate, Team, three current-trainer pages, service pages, membership pages, location pages and Legal.
- WordPress contains 35 published Results stories.
- WordPress contains the pillar article as its only published standard article.
- The current GHL root homepage and 36 other identified public GHL routes were captured.
- The legacy site has 31 unique captured live URLs: the root, five category pages and 25 `/post/` pages. The 25 post pages comprise 23 substantive articles plus Team and Our Mission.

### Built but Not Serving the Intended Root URLs

- The WordPress pages and Results stories are browser-accessible on `blog.theevolvedgym.com.au`, but WordPress does not yet serve the intended root domain.
- The WordPress homepage candidate exists as post ID 165, but the public root homepage is still the GHL page.
- The local Team source removes former trainer Marnie, but that local change is not a verified live WordPress deployment.

### Partially Built

- Blog migration: WordPress has one published article and 20 draft article records, but the intended `/blog/` archive and `/blog/[slug]/` structure is not configured.
- The 20 draft article records have empty slugs in the Phase 1 database snapshot.
- The legacy site has two additional substantive articles that have no WordPress record:
  - `/post/busting-myths-about-strength-training-for-women`
  - `/post/how-to-lift-safely-build-confidence-in-the-gym`
- Results SEO: 35 stories are published, but the Results post type is absent from the captured Rank Math sitemaps, 34 of 35 stories lack a meta description, no Testimonial schema was verified, and 12 stories lack a featured image.
- WordPress URL configuration still uses the blog hostname and HTTP values expected before cutover.
- WordPress contains hardcoded `blog.theevolvedgym.com.au/wp-content/uploads/` asset URLs.
- The Results archive template contains a hardcoded story-card set in addition to the Results records in the database, creating a duplicate source-of-truth risk.
- Two known public WordPress links fail: `/blog` and `/terms-of-use-and-privacy-policy`. The current WordPress legal path is `/legal`.
- The WordPress Team and trainer set is incomplete for the current roster.

### Not Built

- Nora trainer page.
- Katrina trainer page.
- WordPress import or replacement pages for the two missing legacy articles.
- A configured and verified WordPress `/blog/` archive.
- Approved final slugs for the 20 draft articles and the two missing imports.
- A complete exact legacy-blog-to-WordPress redirect matrix.
- Media-safe `blog.` hostname transition rules.
- An approved final destination for former trainer Marnie's URL.
- A verified GHL binding and DNS record for `go.theevolvedgym.com.au`.
- A tested root-domain staging rehearsal using the final hostname and redirects.

### Planned Results Archetypes Still Without a Source Story

The original 22-page Results plan is not the complete Results library. WordPress now has 35 published Results stories. Within the original 22-row matrix, 18 are built and 4 remain without a source member:

- `teens-strength-training-brisbane`
- `teens-aesthetics-confidence-gym`
- `teens-sports-performance-strength`
- `ivf-fertility-strength-training`

These four remain in the plan. They are content opportunities, not DNS cutover blockers unless the owner specifically makes them launch requirements.

### Decisions Required Before Build Completion

- Which retained homepage source becomes the WordPress root homepage: the current GHL presentation, WordPress post 165, or an approved merge.
- Final biographies, images, specialties and page copy for Nora and Katrina.
- The redirect destination for Marnie's former trainer URL.
- Whether the existing four membership pages remain separate or are supplemented by a comparison page.
- Final URL slugs for all 23 legacy articles.
- Whether the five legacy category pages map to WordPress categories, curated guide pages or the `/blog/` archive.
- The final destination of legacy Team and Our Mission pages.
- Whether all current GHL location-interest pages stay as exact-path GHL pages on `go.`. The preservation-first recommendation is yes.

## Target Public URL Ownership

### Captured Root GHL Marketing and Technical Routes

These 18 rows, plus the 19 operational GHL rows in the next section, account for all 37 captured current-root routes.

| Captured current route | Target owner | Proposed disposition |
|---|---|---|
| `/` | WordPress | Serve the approved homepage |
| `/legal` | WordPress | Serve `/legal` |
| `/leisa-personal-trainer-brisbane` | WordPress | Preserve the same path |
| `/locations` | WordPress | Preserve the same path |
| `/marnie-personal-trainer-brisbane` | Decision required | Preserve until the approved destination works |
| `/megan-personal-trainer-brisbane` | WordPress | Preserve the same path |
| `/memberships/evolve-u-program` | WordPress | Preserve the same path |
| `/memberships/fasttrack` | WordPress | Preserve the same path |
| `/memberships/fitflex` | WordPress | Preserve the same path |
| `/memberships/sculptstrength` | WordPress | Preserve the same path |
| `/piper-personal-trainer-brisbane` | WordPress | Preserve the same path |
| `/services` | WordPress | Preserve the same path |
| `/services/nutrition-lifestyle-coaching-brisbane` | WordPress | Preserve the same path |
| `/services/personal-training-brisbane` | WordPress | Preserve the same path |
| `/services/small-group-personal-training-brisbane` | WordPress | Preserve the same path |
| `/services/strength-assessment-for-women-brisbane` | WordPress | Preserve the same path; booking remains a separate GHL route |
| `/robots.txt` | WordPress technical route | Regenerate for the final root site; do not redirect to GHL |
| `/sitemap.xml` | WordPress technical route | Regenerate for the final root site; do not redirect to GHL |

### WordPress at the Root

WordPress owns the public marketing and editorial routes after cutover:

- `/`
- `/team`
- `/megan-personal-trainer-brisbane`
- `/piper-personal-trainer-brisbane`
- `/leisa-personal-trainer-brisbane`
- `/nora-personal-trainer-brisbane` after build
- `/katrina-personal-trainer-brisbane` after build
- `/services` and its four existing service child pages
- `/memberships` and its four existing membership child pages
- `/locations` and the six existing WordPress location child pages
- `/legal`
- `/blog/`
- `/blog/[approved-article-slug]/`
- `/results/`
- `/results/[story-slug]/`

Marnie's former route is preserved until an approved redirect exists. It is not silently removed.

### GHL on `go.`

The following website-dependent operational routes remain in GHL and are proposed to retain their exact path on `go.theevolvedgym.com.au`:

| Current root path | Proposed retained GHL path |
|---|---|
| `/strength-assessment` | `https://go.theevolvedgym.com.au/strength-assessment` |
| `/30dnnc` | `https://go.theevolvedgym.com.au/30dnnc` |
| `/30dnnc-thankyou` | `https://go.theevolvedgym.com.au/30dnnc-thankyou` |
| `/teen-30dnnc-o` | `https://go.theevolvedgym.com.au/teen-30dnnc-o` |
| `/teen-30dnnc-p` | `https://go.theevolvedgym.com.au/teen-30dnnc-p` |
| `/20s30s-30dnnc-o` | `https://go.theevolvedgym.com.au/20s30s-30dnnc-o` |
| `/20s30s-30dnnc-p` | `https://go.theevolvedgym.com.au/20s30s-30dnnc-p` |
| `/pregnancy-30dnnc-o` | `https://go.theevolvedgym.com.au/pregnancy-30dnnc-o` |
| `/pregnancy-30dnnc-p` | `https://go.theevolvedgym.com.au/pregnancy-30dnnc-p` |
| `/perimenopause-30dnnc-o` | `https://go.theevolvedgym.com.au/perimenopause-30dnnc-o` |
| `/perimenopause-30dnnc-p` | `https://go.theevolvedgym.com.au/perimenopause-30dnnc-p` |
| `/post-menopause-30dnnc-o` | `https://go.theevolvedgym.com.au/post-menopause-30dnnc-o` |
| `/post-menopause-30dnnc-p` | `https://go.theevolvedgym.com.au/post-menopause-30dnnc-p` |
| `/coming-to-bulimba` | `https://go.theevolvedgym.com.au/coming-to-bulimba` |
| `/coming-to-coolangatta-tweed-heads` | `https://go.theevolvedgym.com.au/coming-to-coolangatta-tweed-heads` |
| `/coming-to-newfarm` | `https://go.theevolvedgym.com.au/coming-to-newfarm` |
| `/thank-you-bulimba` | `https://go.theevolvedgym.com.au/thank-you-bulimba` |
| `/thank-you-coolangatta-tweed` | `https://go.theevolvedgym.com.au/thank-you-coolangatta-tweed` |
| `/thank-you-newfarm` | `https://go.theevolvedgym.com.au/thank-you-newfarm` |

These are proposed mappings, not implemented redirects. Each route must be present and functionally tested on `go.` before its old root path redirects.

`robots.txt` and `sitemap.xml` are technical routes. They are to be regenerated by the WordPress root site, not redirected to GHL.

## Asset Disposition Register

| Asset group | Preserved source | Phase 3 disposition |
|---|---|---|
| WordPress production filesystem | Complete 303 MB archive plus 11,655 file hashes | Build from an isolated staging copy; do not overwrite the protected archive |
| WordPress database | Complete SQL export plus content/configuration inventories | Restore only to isolated staging unless a separate rollback decision requires production restore |
| WordPress media | Filesystem archive plus 111 registered attachments | Preserve every file; repair hostname references in staging and verify image delivery |
| WordPress theme and templates | Full production child theme plus local workspace sources | Compare before deployment; preserve local Team and former-trainer sources |
| Results stories | 35 database records plus archive and single templates | Keep all records; remove duplicate hardcoded archive data only after the database-driven replacement passes |
| Current GHL pages and funnels | Live GHL assets plus 37 rendered public captures | Keep in GHL until retained `go.` routes and WordPress replacements pass |
| GHL workflows and templates | 143-workflow inventory and 271 rendered email bodies | Keep operational; change only classified website-dependent URLs |
| Legacy blog | 31 unique live URL captures and 66 retained 404 records | Keep host live until exact destination and redirect checks pass |
| Homepage sources | Captured live GHL homepage and WordPress post 165 | Retain both until the owner approves the final WordPress homepage |

## Redirect and Asset Safety Rules

The existing `scripts/redirects.conf` is not safe to install as written. Its blanket `blog.` rule would turn a media URL such as `/wp-content/uploads/...` into `/blog/wp-content/uploads/...`, breaking images and other assets.

Before any redirect is installed:

1. Finalise one source-to-destination row for every current root GHL route and every unique legacy URL.
2. Exempt or correctly preserve WordPress technical and media paths, including `/wp-content/`, `/wp-includes/`, `/wp-json/`, robots and sitemap resources.
3. Replace hardcoded blog-hostname asset references with approved root-hostname equivalents in a staging copy.
4. Test every redirect for status, final URL, chain length, content type and asset integrity.
5. Keep an immediate rollback procedure for DNS, WordPress URLs and redirect rules.

No blanket redirect is approved by this document.

## GHL Dependency Boundary

The Phase 1 URL audit found a lower bound of 49 website-domain references across six GHL custom values and 43 rendered email-template references. Those references require classification, not a blind global replacement.

For each reference:

- keep links to retained GHL journeys on `go.` or `links.`;
- point true website content links to the new WordPress root;
- preserve PAR-Q, story, booking and short-link intent;
- test the receiving route before changing the source reference.

The unsupported SMS-template endpoint, incomplete public workflow action detail and unavailable native funnel-builder source remain documented preservation limitations. They become blocking only if a directly affected GHL asset is proposed for retirement, replacement or destructive editing.

## Approval Gates Before Any Live Change

- [ ] Owner accepts this current-state classification.
- [ ] Homepage source is selected.
- [ ] Nora and Katrina content and assets are approved.
- [ ] All 23 legacy article destinations are approved, including the two missing imports.
- [ ] Legacy category, Team and Our Mission destinations are approved.
- [ ] Marnie redirect destination is approved.
- [ ] `go.` is configured in GHL and all 19 retained operational routes pass functional testing.
- [ ] GHL custom values and template references are classified by destination.
- [ ] WordPress blog structure, Results SEO, internal links, canonicals and hardcoded media URLs pass staging checks.
- [ ] Exact redirects pass a media-safe staging crawl.
- [ ] Root-domain cutover and rollback procedures are rehearsed.
- [ ] A fresh pre-cutover snapshot is taken if production has changed since Phase 1.

## Phase 2 Outcome

Phase 2 resolves the planning conflict without authorising Phase 3 implementation:

- GHL is retained as an operational system.
- The April plans remain preserved as historical intent.
- Current and target states are separated.
- All known incomplete work is retained in the implementation plan.
- Two previously omitted legacy articles are now explicit preservation items.
- No content, route, workflow, template, file or system has been retired.
