---
schema_version: 1
release_id: website-v2
product: Evolved Website V2
status: built_live_pre_root_promotion
runtime_url: https://blog.theevolvedgym.com.au/
intended_root_url: https://theevolvedgym.com.au/
wordpress_homepage_post_id: 165
homepage_h1: Brisbane's Leading Women-Only Gym
homepage_primary_cta: Join the Waitlist
homepage_js_asset_version: 59.0
conversion_authority: reference/conversion-funnel.md
source_snapshot_date: 2026-08-03
live_verified_date: 2026-08-04
source_mirror: wordpress/website-v2/source
protected_baseline: data/private/website-migration-baselines/2026-08-03-phase1
active_cutover_plan: plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md
ghl_route_register: outputs/systems/website-v2-ghl-route-register.json
phase3_audit: outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md
---

# Website V2 Release Manifest

## Canonical Product Identity

Website V2 is already built and publicly live on WordPress at
`https://blog.theevolvedgym.com.au/`.

It is the approved website product to promote to
`https://theevolvedgym.com.au/`. The active work is a root-domain promotion
and cutover, not a rebuild from the current GHL website.

The homepage authority is WordPress post ID 165. Its verified live identity is:

- H1: `Brisbane's Leading Women-Only Gym`
- primary CTA: `Join the Waitlist`
- current homepage JavaScript asset query version: `59.0`
- conversion journey: Pick Your Journey, then the matching organic
  life-stage waitlist route
- presentation: single-purpose conversion page with no normal site navigation

Do not reopen the homepage source, navigation model, CTA strategy or membership
presentation merely because an older GHL page or archived plan differs. Those
are new redesign decisions and require explicit owner approval.

## Platform Boundary

Website V2 does not replace GoHighLevel.

| Surface | Current role | Intended role after root promotion |
|---|---|---|
| `theevolvedgym.com.au` | Current GHL public root | Website V2 public root |
| `blog.theevolvedgym.com.au` | Website V2 runtime | Transitional WordPress hostname with media-safe handling |
| `go.theevolvedgym.com.au` | Not working at the Phase 1 snapshot | Retained GHL funnels, forms, booking and post-conversion journeys |
| `links.theevolvedgym.com.au` | GHL short links and QR routes | Retained unchanged |
| `evolved-woman.theevolvedgym.com.au` | Legacy article site | Retained until every live route has a tested destination |

GHL remains the CRM, communications, workflows, forms, funnels, calendars and
booking system. No GHL asset is retired merely because Website V2 moves to the
root domain.

## Verified Build Inventory

The protected 3 August 2026 capture verified:

- 24 published WordPress pages and 1 draft page;
- the V2 homepage at WordPress post ID 165;
- 35 published Results stories;
- 1 published and 20 draft WordPress articles;
- 111 registered media attachments;
- the complete Blocksy child theme;
- 61 browser-accessible WordPress HTML routes; and
- a complete WordPress filesystem and SQL recovery point.

The Phase 3 read-only audit plus the owner-confirmed Pregnancy correction
established a lower bound of 85 known GHL paths. Nineteen are public root paths
that need exact redirects to `go.`, while another 50 GHL paths were absent
from the earlier redirect list. All 85 are protected by
`outputs/systems/website-v2-ghl-route-register.json`.

The source-controlled mirror at `wordpress/website-v2/source/` contains the
complete deployed child theme plus the database-owned homepage HTML exported
from post ID 165. It is a clean code/content mirror, not a full recovery
package. Uploads, the database, server configuration and secrets remain only
in the protected baseline.

## Authority Order

Website work must use this order:

1. this manifest for product identity, release state and boundaries;
2. `reference/conversion-funnel.md` for the current homepage journey and CTA;
3. `outputs/systems/website-architecture.md` for technical architecture and
   WordPress IDs;
4. `outputs/systems/website-sitemap.md` for route ownership and disposition;
5. `outputs/systems/website-v2-ghl-route-register.json` for the complete
   captured GHL preservation boundary;
6. `outputs/systems/website-v2-phase3-promotion-audit-2026-08-04.md` for the
   root-host rehearsal design and current exceptions;
7. `plans/2026-08-04-website-v2-root-domain-promotion-and-cutover.md` for active
   delivery gates;
8. `outputs/systems/website-v2-release-register.md` for verified releases;
9. the protected Phase 1 baseline for recovery and historical comparison; and
10. archived April plans for implementation history only.

Production is evidence of deployed state. If production differs from this
manifest or the source mirror, stop and record the drift before planning or
changing anything. Do not silently make the newer surface authoritative.

## Root-Promotion Blockers

The following are promotion-readiness work:

- rehearse the existing V2 on the intended root hostname without changing
  production;
- bind and verify retained GHL journeys on `go.`;
- preserve all 85 known GHL paths, not only the 19 public redirect paths;
- preserve the Pregnancy organic thank-you page `/pppsa-page-1536` and prove
  the funnel-controlled next-step journey. Keep the stale `/pppsa-5667` alias
  registered until its safe disposition is established;
- validate every homepage waitlist destination, form and thank-you path;
- correct WordPress `siteurl`, `home`, canonical and hardcoded hostname
  behaviour in the rehearsal;
- repair the current `/blog` and old legal-link failures;
- preserve media and WordPress technical paths during `blog.` handling;
- create exact route and redirect mappings with no blanket replacement;
- verify DNS, SSL, analytics, forms, assets and rollback;
- reconcile the business-owned `Evolved Blog` web stream with the governed
  historical root stream in the same GA4 property, without duplicate page
  views;
- take a fresh protected snapshot immediately before cutover; and
- obtain explicit owner approval for the live cutover.

## Protected Backlog, Not Automatic Root-Promotion Blockers

The following work remains preserved but does not delay root promotion unless
the owner explicitly changes the gate:

- Nora and Katrina trainer pages;
- the former Marnie URL destination;
- 20 draft article reviews and final slugs;
- 2 legacy articles without WordPress records;
- 5 legacy category mappings plus legacy Team and Our Mission mappings;
- remaining Results metadata, schema and featured-image improvements;
- removal of the duplicate hardcoded Results archive source after a verified
  database-driven replacement; and
- 3 teen and 1 IVF/fertility Results story archetypes without source members.

The legacy article hostname must remain live until its own mapping and
retirement gates pass.

## Change and Release Contract

Before planning any website task:

1. read this manifest, the conversion authority, architecture and active plan;
2. run `python3 scripts/check_website_v2_drift.py`;
3. compare the request with the live V2 identity and the source mirror; and
4. classify the change as root promotion, defect repair, content backlog or a
   separately approved redesign.

After every authorised live Website V2 change:

1. read back the live result;
2. refresh the clean source mirror without secrets or uploads;
3. update `wordpress/website-v2/SOURCE_SHA256SUMS.txt`;
4. append the release evidence to
   `outputs/systems/website-v2-release-register.md`;
5. update this manifest if product identity or expected live facts changed;
6. rerun the drift checker locally and against the live page; and
7. update the architecture, sitemap and roadmap when their state changed.

No release is complete when production, the source mirror, this manifest and
the release register disagree.

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.2 | 2026-08-04 | Added the owner-confirmed Pregnancy thank-you route, corrected funnel-next-step semantics and expanded the protected GHL lower bound to 85 paths |
| 1.1 | 2026-08-04 | Added the Phase 3 audit and machine-checked 84-path GHL preservation register; recorded the Pregnancy step and analytics gates |
| 1.0 | 2026-08-04 | Established Website V2 as the already-built live WordPress product and separated root-promotion blockers from the protected content backlog |
