# Website V2 Root-Domain Promotion and Cutover

**Created:** 4 August 2026  
**Status:** Phase 3 read-only audit, Cloudflare rollback capture and rehearsal
design complete; acceptance blocked by live-journey and additive `go.` checks;
live promotion not authorised  
**Product authority:** `outputs/systems/website-v2-release-manifest.md`  
**Recovery point:** `data/private/website-migration-baselines/2026-08-03-phase1/`

## Outcome

Promote the existing, live Website V2 from
`blog.theevolvedgym.com.au` to `theevolvedgym.com.au` without rebuilding it,
replacing GHL or losing any current page, asset, route, workflow or historical
source.

## Non-Negotiables

- Website V2 is already built. WordPress post ID 165 is the homepage.
- Preserve its no-navigation conversion design and current waitlist journey.
- GHL remains the CRM, communications, workflow, form, funnel, calendar and
  booking platform.
- No source or legacy hostname is retired before its destination, dependency
  and rollback evidence passes.
- No blanket domain replacement or blanket `blog.` redirect is permitted.
- Content improvements do not become root-promotion blockers without an
  explicit owner decision.
- No production, DNS, redirect or GHL change occurs without a fresh snapshot,
  passed rehearsal and explicit owner cutover approval.

## Phase 1: Preservation

**Status:** Complete on 3 August 2026.

- [x] Complete workspace recovery snapshot.
- [x] Complete production WordPress filesystem and SQL snapshot.
- [x] WordPress file hashes, content and configuration inventories.
- [x] Accessible GHL inventory and rendered template capture.
- [x] Current GHL, WordPress and legacy public-route capture.
- [x] Browser and restoration verification.
- [x] Independent checksum-verified owner copy.

The GHL capture is dependency and preservation evidence. It is not a GHL
migration package.

## Phase 2: V2 Governance Recovery

**Status:** Complete locally on 4 August 2026; no live changes.

- [x] Recover Website V2 identity from archived implementation records and the
  live WordPress product.
- [x] Establish the canonical V2 release manifest.
- [x] Establish an append-only release register.
- [x] Mirror the complete deployed child theme and homepage post source into
  the governed workspace.
- [x] Separate root-promotion blockers from the protected content backlog.
- [x] Mark the earlier rebuild/transfer decision list as superseded without
  deleting it.
- [x] Align workspace guidance, architecture, sitemap and roadmap.
- [x] Add a read-only local/live drift checker.
- [x] Preserve the April plans as historical implementation evidence.

## Phase 3: Read-Only Promotion Audit and Rehearsal Design

**Authorisation:** Read-only investigation is allowed. Staging or live mutation
requires separate approval.

- [x] Run the local and live V2 drift checks immediately before planning.
- [x] Confirm the clean source mirror still matches the deployed V2 files.
- [x] Inventory every V2 internal link and external journey by intent.
- [ ] Verify all homepage organic waitlist destinations and their GHL forms,
  workflows, thank-you pages and booking transition. All five entry pages,
  forms and workflow identities were verified read-only, but no form was
  submitted. Owner confirmation established `/pppsa-page-1536` as the
  Pregnancy organic thank-you page and confirmed that funnel next-step logic
  overrides the embedded form fallback.
- [x] Correct the standalone `30DNNC Form - PPP` fallback from paid
  `/pppsa` to the owner-confirmed organic `/pppsa-page-1536` page and
  reload-verify the saved value.
- [ ] Resolve the exact GHL custom-domain value required for `go.`. Current
  HighLevel guidance identifies `sites.ludicrous.cloud` as the manual
  subdomain CNAME candidate. The live account confirms there is no existing
  `go.` entry, but the connection flow did not expose its DNS value before the
  action that would begin provisioning.
- [x] Identify the V2 analytics tags and their owner. They belong to the
  business, use the same governed GA4 property, and represent the separate
  `Evolved Blog` web stream.
- [x] Resolve the Pregnancy route mismatch: `/pppsa-page-1536` is the working
  organic middle page; `/pppsa-5667` is a stale alias retained for later
  disposition; the paid route remains separate.
- [x] Build the root-host rehearsal procedure from an isolated copy.
- [x] Define the exact WordPress `siteurl`, `home`, canonical, media and
  serialized-data changes needed for the rehearsal.
- [ ] Repair and test `/blog` and the old legal target in the rehearsal.
- [x] Build the exact current-root GHL route disposition matrix.
- [x] Build media-safe `blog.` handling that preserves `/wp-content/`,
  `/wp-includes/`, `/wp-json/`, robots and sitemaps.
- [x] Define DNS, SSL, cache, analytics, monitoring and rollback evidence.
- [x] Capture the owner-authenticated Cloudflare 29-record zone export, proxy
  states, redirect surfaces, Workers routes and SSL/TLS restore values without
  changing Cloudflare.

The 4 August audit is recorded in
`outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md`. Its
machine-readable route authority contains 85 known GHL paths: 16 that
WordPress will own on the root, 19 exact root-to-`go.` redirects and 50
additional paths that remain available only on `go.`. The same-day signed-in
read-back refined the Pregnancy and analytics plans. The owner-approved form
fallback correction changed no funnel sequencing, workflow, contact,
WordPress, DNS or paid route.

The owner-authenticated Cloudflare evidence is recorded in
`outputs/systems/website-v2-cloudflare-rollback-snapshot-2026-08-04.md`.
It captures the provider-side root and `www` restore values, all 29 DNS
records, proxy states, the existing eight-item image redirect list, zero zone
redirect/Page/Worker rules and current SSL/TLS settings. A fresh export remains
mandatory immediately before any later approved Cloudflare mutation.

### Phase 3 Acceptance

- [x] No homepage redesign or source-selection question remains.
- [x] The rehearsal uses the existing V2 release.
- [ ] Every homepage waitlist route completes the intended GHL journey.
- [x] Every captured current root route has a keep, move, redirect or defer
  decision.
- [x] Assets and WordPress technical paths are protected.
- [x] The rollback procedure, provider-side DNS values, proxy states, rules and
  SSL/TLS evidence are explicit and owner-authenticated.
- [x] The content backlog remains preserved and separately classified.

## Phase 4: Isolated Root-Host Rehearsal

**Authorisation:** Explicit approval required before creating or modifying
staging.

- [ ] Restore the protected WordPress snapshot to an isolated environment.
- [ ] Disable email, callbacks, indexing and production integrations.
- [ ] Apply only the documented root-host URL changes.
- [ ] During the approved additive connection, capture the account-specific
  GHL DNS value, then bind and test all 85 registered GHL paths on `go.`.
- [ ] Prove the Pregnancy journey reaches `/pppsa-page-1536` and its existing
  confirmation step with an owned test contact; preserve `/pppsa-5667` until
  its separate disposition is approved.
- [ ] Test Website V2 homepage, pages, Results, published articles and assets.
- [ ] Test waitlist forms, thank-you transitions and Strength Assessment
  booking.
- [ ] Test exact redirects and technical-path exemptions.
- [ ] Reconcile V2's `G-W9KNRFKV5F` / `GT-TXBKBKZB` tags with the governed
  root `G-RXM7LVC0VJ` / `GTM-TMW7CS6L` setup and prove one accepted,
  non-duplicated root page view.
- [ ] Test canonicals, sitemap and robots behaviour.
- [ ] Preserve the dormant paid pages and steps, but do not reactivate paid
  traffic until the five paid pages' organic-form bindings are separately
  repaired and tested.
- [ ] Perform and time the rollback rehearsal.

### Phase 4 Acceptance

- [ ] V2 appearance and conversion behaviour match the live release.
- [ ] No current V2 route or asset is lost.
- [ ] No GHL journey is replaced or broken.
- [ ] No legacy article route is retired.
- [ ] No unintended 404, loop, multi-hop redirect or broken asset remains.
- [ ] The rollback rehearsal passes.

## Phase 5: Production Root Promotion

**Authorisation:** Explicit owner approval required after Phase 4 passes.

- [ ] Freeze Website V2 changes for the cutover window.
- [ ] Run the drift checker locally and live.
- [ ] Take and verify a fresh protected WordPress snapshot.
- [ ] Record exact current DNS, WordPress URL and redirect values.
- [ ] Apply only the rehearsed WordPress, GHL, DNS and redirect changes.
- [ ] Verify the root homepage, pages, Results, articles and assets.
- [ ] Verify all homepage waitlist and retained GHL journeys.
- [ ] Verify SSL, canonical, analytics, robots and sitemap behaviour.
- [ ] Monitor the agreed observation window.
- [ ] Roll back immediately on a critical route, asset, form or booking
  failure.

## Phase 6: Observation and Separate Legacy Retirement

- [ ] Keep the Phase 1, pre-cutover and post-cutover snapshots.
- [ ] Keep source GHL and legacy pages through the observation window.
- [ ] Update the source mirror, hashes, manifest and release register.
- [ ] Complete legacy article, category, Team and Our Mission mappings as a
  separate content-retirement workstream.
- [ ] Retire a source only after traffic, dependency, destination and rollback
  evidence passes.

## Protected Content Backlog

These items remain visible and are not discarded:

- Nora and Katrina trainer pages and final Team update;
- Marnie's former route disposition;
- 20 draft article reviews and slugs;
- 2 missing legacy article imports;
- 5 legacy category mappings plus Team and Our Mission;
- Results sitemap, meta, schema and featured-image work;
- Results archive duplicate-source repair; and
- 3 teen plus 1 IVF/fertility Results archetypes.

They are not root-promotion blockers unless Peter explicitly changes that
decision.
