# Website Rebuild and Transfer Implementation Plan

**Created:** 4 August 2026
**Status:** Superseded and preserved for audit history
**Current-state authority:** `outputs/systems/website-rebuild-transfer-current-state-2026-08-04.md`

> **Correction recorded 4 August 2026:** This plan incorrectly reopened the
> source and design of an existing live Website V2. It has not been deleted or
> truncated, but it must not be executed. The replacement is
> `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md`, governed by
> `outputs/systems/website-v2-release-manifest.md`.

## Outcome

Transfer the public marketing and editorial website to WordPress at `theevolvedgym.com.au` while retaining GHL as the CRM, workflow, communication, funnel, form and booking system. Preserve every current source and route until its replacement or retained destination is verified.

## Non-Negotiables

- Do not delete or overwrite historical plans, source pages, GHL assets, WordPress content or legacy captures.
- Do not treat the website transfer as a GHL replacement.
- Do not install redirects, change DNS, change WordPress production URLs or retire a GHL domain until the relevant approval gate passes.
- Do not use blanket URL replacement in GHL.
- Do not use the current blanket `blog.` redirect rule.
- Every retirement requires a verified destination, dependency check and rollback path.

## Source Hierarchy

1. `outputs/systems/website-rebuild-transfer-current-state-2026-08-04.md`
2. `data/private/website-migration-baselines/2026-08-03-phase1/`
3. Current system records:
   - `outputs/systems/website-architecture.md`
   - `outputs/systems/website-sitemap.md`
   - `outputs/systems/blog-catalog.md`
   - `outputs/systems/social-proof-pages.md`
4. Historical intent:
   - `plans/archive/2026-04-29-website-migration-redesign.md`
   - `plans/archive/2026-04-30-homepage-animation-redesign.md`

## Phase 1: Preservation

**Status:** Complete on 3 August 2026.

- [x] Complete local workspace snapshot.
- [x] Complete production WordPress filesystem and SQL snapshot.
- [x] WordPress content, configuration, attachment and file-hash inventories.
- [x] Accessible GHL inventory and rendered email-template capture.
- [x] Current root GHL route capture.
- [x] Legacy-site discovery and capture.
- [x] WordPress browser verification.
- [x] Checksum and sample restoration verification.
- [x] Independent owner-only backup copy.

The GHL capture is evidence, not a GHL migration. Unsupported GHL API surfaces are not website blockers unless a directly affected GHL asset is to be retired or reconstructed.

## Phase 2: Documentation Reconciliation

**Status:** Complete when the validation checklist at the end of this plan passes.

- [x] Preserve the April plans unchanged.
- [x] Establish a dated current-state authority.
- [x] Separate current live hosting from target hosting.
- [x] Record GHL as retained operational infrastructure.
- [x] Reconcile page, article and Results counts.
- [x] Restore two omitted legacy articles to the plan.
- [x] Record all known partial and unbuilt work.
- [x] Define approval-gated URL ownership and retained GHL routes.
- [x] Align architecture, sitemap, blog, Results, roadmap and workspace guidance.
- [x] Keep all live-system changes outside Phase 2.

## Phase 3A: Staging Build and Content Completion

**Authorisation:** Required before starting.

### Public-Site Structure

- [ ] Create or refresh an isolated staging copy from the protected WordPress baseline.
- [ ] Select and approve the WordPress homepage source.
- [ ] Configure a real `/blog/` archive and `/blog/[slug]/` article structure.
- [ ] Configure final root-domain canonicals in staging.
- [ ] Preserve `/results/` and every published Results story.
- [ ] Remove the Results archive's duplicate hardcoded story source after proving the database-driven replacement.
- [ ] Fix `/blog` and the old legal-page internal link.
- [ ] Replace hardcoded blog-hostname asset URLs in staging and verify every affected image, script and stylesheet.

### Missing Trainer Work

- [ ] Obtain approved Nora biography, image, specialties and testimonial material.
- [ ] Build and review Nora's trainer page.
- [ ] Obtain approved Katrina biography, image, specialties and testimonial material.
- [ ] Build and review Katrina's trainer page.
- [ ] Review and publish the corrected five-person Team page.
- [ ] Preserve Marnie's page until its destination is approved and tested.

### Blog Preservation

- [ ] Review and approve final destinations for all 23 substantive legacy articles.
- [ ] Preserve the 21 imported WordPress records.
- [ ] Import or rebuild:
  - [ ] `busting-myths-about-strength-training-for-women`
  - [ ] `how-to-lift-safely-build-confidence-in-the-gym`
- [ ] Approve slugs for the 20 imported draft articles.
- [ ] Approve slugs for the two missing imports.
- [ ] Decide destinations for five legacy category pages.
- [ ] Decide destinations for legacy Team and Our Mission.
- [ ] Verify content, metadata, images, internal links and approved references before publication.

### Results Completion and SEO

- [ ] Keep all 35 published Results stories.
- [ ] Add the Results post type to the intended XML sitemap.
- [ ] Add unique meta descriptions to the 34 stories that lack them.
- [ ] Add and validate the intended Testimonial schema.
- [ ] Resolve the 12 missing featured images with approved assets or an explicit documented exception.
- [ ] Retain the four unbuilt original archetypes in the backlog:
  - [ ] three teen stories;
  - [ ] one IVF/fertility story.

The four archetypes are not cutover blockers unless the owner makes them launch requirements.

### Stage 3A Acceptance

- [ ] Every current WordPress page and Results route works in staging.
- [ ] All 23 substantive legacy articles have an approved destination.
- [ ] The two missing legacy articles exist in staging.
- [ ] No hardcoded production blog-hostname media dependency remains without an explicit exception.
- [ ] Staging crawl has no unintended 404, redirect loop or broken asset.
- [ ] Staging has no outgoing production email, payment callback or indexing.

## Phase 3B: GHL Domain Preparation

**Authorisation:** Required before making live GHL or DNS changes.

- [ ] Create the `go.theevolvedgym.com.au` DNS record with the exact value required by GHL.
- [ ] Bind and verify `go.` inside GHL.
- [ ] Make all 19 retained operational routes available on `go.`.
- [ ] Test forms, calendars, booking, thank-you transitions, mobile layout and tracking on each retained route.
- [ ] Classify the six GHL custom values found by the URL audit.
- [ ] Classify all 43 lower-bound email-template references found by the URL audit.
- [ ] Check affected GHL SMS and workflow actions manually only where a website-dependent route is involved.
- [ ] Leave unrelated GHL workflows and templates unchanged.
- [ ] Verify `links.` still resolves and every known QR/short-link use remains intact.

### Stage 3B Acceptance

- [ ] All 19 retained operational GHL paths work on `go.` before any root redirect is installed.
- [ ] Strength Assessment booking completes successfully.
- [ ] 30DNNC and life-stage forms complete successfully.
- [ ] Location-interest forms reach the correct GHL thank-you pages.
- [ ] No tested GHL path depends on the root hostname to function.

## Phase 3C: Exact Redirect and Cutover Rehearsal

**Authorisation:** Required before changing production DNS or redirects.

- [ ] Build one source-to-destination row for all 37 captured root GHL routes.
- [ ] Build one source-to-destination row for all 31 unique live legacy URLs.
- [ ] Classify all 66 retained legacy 404 records as redirect, intentional gone or no action.
- [ ] Include the former Marnie route only after destination approval.
- [ ] Preserve media and WordPress technical paths.
- [ ] Test redirects using the final hostnames in staging.
- [ ] Record expected status, final URL, chain length and content type.
- [ ] Rehearse DNS, WordPress URL and redirect rollback.
- [ ] Take a fresh pre-cutover snapshot if any production source changed after 3 August.

### Stage 3C Acceptance

- [ ] No blanket blog-host redirect affects `/wp-content/`, `/wp-includes/`, `/wp-json/`, robots or sitemaps.
- [ ] Every approved redirect is a single hop.
- [ ] Every canonical page returns the intended content.
- [ ] All images, styles, scripts, forms and videos load.
- [ ] The rollback can be completed without deleting the Phase 1 baseline.

## Phase 4: Production Cutover

**Authorisation:** Explicit owner approval required after Phases 3A to 3C pass.

- [ ] Freeze website content changes for the cutover window.
- [ ] Record current DNS values and TTLs.
- [ ] Apply final WordPress root URL configuration.
- [ ] Apply approved root and `www` DNS changes.
- [ ] Apply only the tested redirect set.
- [ ] Verify WordPress root pages, articles, Results and assets.
- [ ] Verify all retained GHL journeys on `go.` and `links.`.
- [ ] Verify analytics, search visibility controls and canonical URLs.
- [ ] Monitor logs, forms, bookings and top routes through the agreed observation window.
- [ ] Roll back immediately if a critical route, asset, form or booking flow fails.

## Phase 5: Post-Cutover Retention and Retirement Review

- [ ] Keep the Phase 1 and fresh pre-cutover snapshots.
- [ ] Keep legacy and GHL source pages through the observation window.
- [ ] Review real traffic to old routes before retiring any source.
- [ ] Retire an old page or hostname only after destination, dependency and rollback evidence is recorded.
- [ ] Update the architecture, sitemap, blog catalog, Results register and roadmap with verified live state.

## Phase 2 Validation Checklist

- [x] No April historical plan was edited.
- [x] No file, page, workflow, template or route was deleted.
- [x] No live WordPress, GHL, DNS or redirect setting was changed.
- [x] The target architecture retains GHL.
- [x] All known incomplete work remains in this plan.
- [x] The two missing legacy articles are explicit deliverables.
- [x] The current root and target root are no longer conflated.
- [x] Phase 3 and Phase 4 actions are approval-gated.
