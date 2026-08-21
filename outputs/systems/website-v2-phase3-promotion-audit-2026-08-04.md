# Website V2 Phase 3 Promotion Audit

**Date:** 4 August 2026  
**Mode:** Read-only  
**Status:** Audit, Cloudflare rollback capture and rehearsal design complete;
live promotion not authorised  
**Product authority:** `outputs/systems/website-v2-release-manifest.md`  
**Route authority:** `outputs/systems/website-v2-ghl-route-register.json`  
**Recovery point:** `data/private/website-migration-baselines/2026-08-03-phase1/`

## Outcome

Website V2 is intact. The live homepage and `homepage.js?ver=59.0` still match
the governed source mirror, and all five homepage selections route to their
intended organic GHL entry pages.

The audit also found facts that must be addressed before a root cutover:

1. GHL has a known lower bound of **85 paths**, not 19.
2. The Pregnancy organic step Publishing field exposes `/pppsa-5667`, which
   returns **404**, but the owner-confirmed live thank-you page is
   `/pppsa-page-1536`. Public metadata ties that working page to the same
   organic funnel, middle step, page and booking-confirmation next step.
   HighLevel funnel logic, not the embedded form fallback, controls the next
   step after submission.
3. All five paid life-stage pages in the protected capture embed the matching
   **organic** form rather than the separate paid form.
4. V2 and the current root use different Google analytics tags. The V2 tags
   are owned by the business in the same GA4 property, but belong to the
   separate `Evolved Blog` web stream rather than the governed historical root
   stream.
5. `/blog` and `/terms-of-use-and-privacy-policy` currently return 404.
6. `go.theevolvedgym.com.au` has neither a published DNS record nor an
   existing HighLevel domain entry.

Nothing was deleted, submitted, staged or changed in WordPress, DNS, contacts,
workflows, funnel sequencing or paid funnels during this audit. After the
owner correction, the only live GHL change was the approved standalone
`30DNNC Form - PPP` fallback redirect from `/pppsa` to
`/pppsa-page-1536`; it was saved, reloaded and read back.

## Account Read-Back Refinement

The signed-in HighLevel subaccount was inspected read-only on 4 August after
the initial audit. The root domain is currently attached to one Website and 13
Funnels. Its connected-product register also preserves `www`, `trainers`,
`links`, `mail`, `free` and `r2rtraining`; `go` is not present. The Pregnancy
organic funnel is attached to `theevolvedgym.com.au`. Its middle step has a
visible CONTROL page: the stale Publishing alias `/pppsa-5667` returns 404,
while the actual page route `/pppsa-page-1536` returns 200.

The HighLevel domain connection flow was not advanced past the point that
would begin connecting a new domain. Therefore it did not expose an
account-specific DNS target without risking provisioning. No domain was
created or connected.

The owner-authenticated Cloudflare read-back is complete. A 29-record zone
export, proxy states, nameservers, redirect surfaces, Workers routes and
SSL/TLS settings were captured without changing Cloudflare. The exact export
is protected under
`data/private/website-migration-baselines/2026-08-04-cloudflare-read-only/`;
the share-safe evidence and restore values are recorded in
`outputs/systems/website-v2-cloudflare-rollback-snapshot-2026-08-04.md`.

## Evidence Used

- the complete Phase 1 WordPress, GHL and public-route baseline;
- the governed V2 source mirror and release hashes;
- the live V2 homepage in a browser;
- the five live organic life-stage pages, without form submission;
- current public DNS and HTTP read-backs;
- the owner-authenticated Cloudflare zone export and provider-side settings;
- the captured GHL forms and workflow inventories;
- the serialized funnel-step data embedded in every captured GHL page; and
- the governed lead-generation and conversion-funnel documentation.

The local and live command below passed before the audit:

```bash
python3 scripts/check_website_v2_drift.py --live
```

It verified the nine governed source files, homepage identity, live
`homepage.js` version and byte-for-byte JavaScript parity.

## Website V2 Runtime

### Verified product identity

| Item | Live value |
|---|---|
| Runtime | `https://blog.theevolvedgym.com.au/` |
| Homepage | WordPress post 165 |
| H1 | `Brisbane's Leading Women-Only Gym` |
| Primary CTA | `Join the Waitlist` |
| Homepage sections | 17 |
| JavaScript | `homepage.js?ver=59.0` |
| Forms on homepage | None; the forms remain in GHL |
| Normal navigation | None; this is the approved V2 design |
| Canonical / Open Graph URL | `https://blog.theevolvedgym.com.au/` |
| Current title | `Home - Blog | The Evolved All Female Gym` |

Before a woman selects a life stage, all six visible homepage waitlist links
anchor to `#pyj-section`. After selection, the live JavaScript updates the
waitlist links to the matching organic entry page and retains the selected
goal and decade as query parameters.

### Homepage journey destinations

| Selection | Live destination verified from the homepage |
|---|---|
| Teenager | `https://theevolvedgym.com.au/teen-30dnnc-o?goal=get-stronger&decade=20s` |
| 20s–30s | `https://theevolvedgym.com.au/20s30s-30dnnc-o?goal=get-stronger&decade=20s` |
| Pregnancy | `https://theevolvedgym.com.au/pregnancy-30dnnc-o?goal=get-stronger&decade=30s` |
| Perimenopause | `https://theevolvedgym.com.au/perimenopause-30dnnc-o?goal=get-stronger&decade=40s` |
| Postmenopause | `https://theevolvedgym.com.au/post-menopause-30dnnc-o?goal=get-stronger&decade=50s` |

All five entry pages returned 200 and visibly contained First Name, Email and
`Claim Your Free 30 Day Email Series` controls. No form was submitted.

### Current link and hostname dependencies

The homepage contains:

- four root-domain membership links that will correctly become WordPress
  routes after promotion;
- five JavaScript-defined organic GHL destinations that should become direct
  `go.` links after `go.` passes functional testing;
- a broken footer link to `/terms-of-use-and-privacy-policy`;
- a broken footer link to `/blog`;
- a GHL reviews widget;
- Google Maps;
- YouTube image/video assets; and
- WordPress-hosted media and theme assets.

The active V2 runtime source contains at least **118 hardcoded
`blog.theevolvedgym.com.au` occurrences** across the homepage post,
`homepage.js`, the Results templates and the shared page template. The
deployment helper copy `homepage-v5.html` contains another 43. The protected
database contains 465 `http://blog...` and 325 `https://blog...` string
occurrences before excluding immutable GUID history.

These are migration inputs, not permission for a blind text replacement.
Database values need a serialized-safe WordPress replacement, while theme
code should use relative or WordPress-generated URLs.

### Confirmed current route defects

| URL | Current result | Rehearsal disposition |
|---|---:|---|
| `blog.theevolvedgym.com.au/blog` | 404 | Create a WordPress Blog index page and set it as `page_for_posts` |
| `blog.theevolvedgym.com.au/terms-of-use-and-privacy-policy` | 404 | Change the footer to `/legal/`; retain a direct 301 from the old path |
| `theevolvedgym.com.au/blog` | 404 | Becomes the WordPress Blog index |
| `theevolvedgym.com.au/terms-of-use-and-privacy-policy` | 404 | Direct 301 to `/legal/` |
| `blog.theevolvedgym.com.au/legal` | 200 after one slash-normalising redirect | Preserve as WordPress `/legal/` |
| `theevolvedgym.com.au/legal` | 200 in current GHL | Root ownership passes to the existing WordPress Legal page |

Do not change the global WordPress permalink structure as part of the root
promotion. The one published WordPress article remains at
`/strength-training-for-women/`. The 20 drafts and future `/blog/[slug]`
architecture remain protected content work.

## Corrected GHL Preservation Boundary

### The undercount

The earlier 19-route list contained only the public root paths that need
redirects to `go.`. It omitted configured funnel steps that are not normally
discovered by a public crawl.

Parsing the embedded configuration in every captured GHL page produced:

| GHL surface | Count |
|---|---:|
| Captured public HTML aliases | 35 |
| Configured funnel/website step paths | 73 |
| Known configured or owner-confirmed GHL paths | **85** |
| Current public technical paths | 2 |

The 85 known paths divide into:

| Root disposition | Count | Preservation rule |
|---|---:|---|
| WordPress serves the same root path | 16 | Keep the matching GHL page on `go.` through observation; do not delete it |
| Root redirects directly to the same path on `go.` | 19 | Exact path rule; preserve query strings |
| No automatic root redirect; preserve on `go.` | 50 | Internal, confirmation, agreement, booking or legacy GHL step |
| WordPress technical response | 2 | `/robots.txt` and `/sitemap.xml` |

The complete machine-readable lists are in
`outputs/systems/website-v2-ghl-route-register.json`.

### Examples the 19-route list missed

- ten life-stage Strength Assessment steps;
- ten life-stage booking-confirmation steps;
- ten internal life-stage opt-in step paths;
- PT agreement, menu and six confirmation paths;
- membership agreement and menu paths;
- Intro Session booking;
- Strength Assessment confirmation;
- four 7 Day Reset / 30DNNC thank-you paths;
- the GHL `/home` step; and
- the Beth and Hannah legacy trainer steps.

The protected baseline supplied 49 hidden paths. Forty-eight returned 200 and
`/pppsa-5667` returned 404. The owner-confirmed working Pregnancy route
`/pppsa-page-1536` adds a fiftieth go-only path and returns 200.

## Homepage Organic Journey Map

The workflow status comes from the 3 August GHL inventory and the
full-canvas evidence in `outputs/systems/lead-generation-nurture.md`.

| Life stage | Entry form | Intake workflow | Delivery workflow | Next SA step | Booking confirmation |
|---|---|---|---|---|---|
| Teen | `30DNNC Form - Teen` (`9KnvPrY6tEJfhaEPmkZ1`) | `Teen - 30DNNC Form Submission (Organic)` — published | `TEEN 30DNNC` — published | `/teensa` — 200 | `/teensaconfirm` — 200 |
| 20s–30s | `30DNNC Form - 20-30's` (`x7kX4iXL88xesZjZuc2y`) | `20/30s - 30DNNC Form Submission (Organic)` — published | `20/30 30DNNC` — published | `/2030sa-4923` — 200 | `/2030saconfirm-9733` — 200 |
| Pregnancy / PPP | `30DNNC Form - PPP` (`nkLAaryOhWRKn6B4ynTR`) | `PPP 30DNNC Form Submission (Organic)` — published | `PPP 30DNNC` — published | `/pppsa-page-1536` — 200 | `/pppsaconfirm-2156` — 200 |
| Perimenopause | `30DNNC Form - Perimenopause` (`yGdm5cnighkkf4TZrJTy`) | `PERIM - 30DNNC Form Submission (Organic)` — published | `PERIM 30DNNC` — published | `/perimsa-6473` — 200 | `/perimsaconfirm-7002` — 200 |
| Postmenopause | `30DNNC Form - Postmenopause` (`6KHo1LIUmUa1D5GASg98`) | `POSTM - 30DNNC Form Submission (Organic)` — published | `POSTM 30DNNC` — published | `/pmsa` — 200 | `/pmsaconfirm-592484` — 200 |

`LS: Guarded 30DNNC Website Organic` is published and documented as covering
the generic and five organic forms. It writes `Website Organic` only when Lead
Source is empty.

The table proves route, form and workflow identity. It does not replace the
Phase 4 controlled submissions needed to prove contact creation, source,
tags, spreadsheet actions, nurture enrolment, thank-you transition, calendar
booking and confirmation.

Owner confirmation resolved the apparent conflict. Public GHL metadata for
`/pppsa-page-1536` contains:

- Pregnancy organic funnel ID `uTqiHqeiuCL2wpbZqGYV`;
- middle-step ID `3321d57f-f520-49f1-8c43-85970a7d266a`;
- page ID `rfxYJSA6ZtLCFADbyTLA`; and
- booking-confirmation next-step ID
  `e9a36c56-2b66-41c8-9420-e0c13b308b4a`.

That proves `/pppsa-page-1536` is the actual page owned by the already-captured
organic middle step. `/pppsa-5667` is a stale configured alias, not a separate
missing page and not evidence that an embedded funnel submission reaches a
404.

### Owner-approved form fallback correction

When `30DNNC Form - PPP` is embedded in the Pregnancy funnel, HighLevel's
funnel next-step logic controls the destination. The form's On Submit URL is
only the fallback when the form is used outside a funnel.

The owner approved correcting that fallback. The live setting changed from
`https://theevolvedgym.com.au/pppsa` to
`https://theevolvedgym.com.au/pppsa-page-1536`. The new value was saved,
reloaded and read back. The supplied page returned 200 with title
`Thank You for Subscribing` and visible Strength Assessment booking content.

No funnel step, sequence, page, workflow, contact or paid route changed.
During the approved `go.` rehearsal:

1. Preserve `/pppsa-page-1536`, `/pppsa-5667`, `/pppsa` and both funnels.
2. Confirm the same organic page and next-step IDs resolve on `go.`.
3. Change the standalone form fallback to
   `https://go.theevolvedgym.com.au/pppsa-page-1536` only after that page
   passes.
4. Use one owned, uniquely identifiable test contact to prove the funnel
   transition, source guard, intake and delivery workflows, Strength
   Assessment booking and organic confirmation step.
5. Decide the stale `/pppsa-5667` alias separately after traffic and
   dependency evidence; do not delete or republish it merely because it is
   currently 404.

### Paid-funnel exception

The protected 3 August HTML for each of the five paid life-stage landing pages
contains the matching organic form ID, not the separate paid form ID. This is
inconsistent with the documented paid workflows and paid Lead Source guard,
which trigger from the five paid forms.

The paid system is documented as dormant and requires a named campaign owner
and end-to-end test before reuse. Root promotion must preserve all paid pages
and steps, but it must not silently reactivate or point paid traffic at them.
Repairing their form bindings is a separate controlled GHL defect fix.

## GHL URL Dependencies

The Phase 1 audit found six custom-value references and 43 rendered
email-template references.

### Custom values

| Intent | Count | Cutover treatment |
|---|---:|---|
| Strength Assessment and generic 30DNNC | 2 | Change to the same path on `go.` only after `go.` passes |
| PAR-Q form on `links.` | 1 | Leave unchanged |
| Results story URLs | 3 | Leave on the root; they become valid WordPress Results URLs |

### Email templates

| Intent | Count | Cutover treatment |
|---|---:|---|
| Strength Assessment | 4 | Change to `go./strength-assessment` after validation |
| Location-interest pages | 3 | Change to the matching `go.` path after validation |
| Root homepage | 8 | Leave on the root WordPress homepage |
| Already-broken legacy resource/campaign paths | 28 | Do not guess or globally replace; review template activity and destination separately |

The 28 already-broken references include `jaw-dropping`,
`best-transformations`, `food-freedom`, `woo-hoo`, `10yrsyounger`,
`book-call`, `pmreset` and `perireset`. Their current 404 state was confirmed.
They are not evidence that the root promotion caused a loss, but they must
remain visible as a separate remediation register.

## DNS and Host Evidence

The authoritative nameservers are:

- `jim.ns.cloudflare.com`
- `zariyah.ns.cloudflare.com`

The published records observed on 4 August were:

| Host | Published result | TTL |
|---|---|---:|
| root | Cloudflare A `104.21.82.5`, `172.67.167.88` plus Cloudflare AAAA | 300 |
| `www` | same Cloudflare A/AAAA result | 300 |
| `blog` | A `35.213.240.236` | 300 |
| `go` | no A, AAAA or CNAME answer | — |
| `links` | CNAME `brand.ludicrous.cloud` | 3600 |
| `evolved-woman` | Cloudflare A/AAAA result | 300 |

The owner-authenticated provider read-back established the exact current web
restore values:

| Host | Provider record | Proxy | TTL |
|---|---|---|---|
| root | A `162.159.140.166` | Proxied | Auto |
| `www` | CNAME `sites.ludicrous.cloud` | Proxied | Auto |
| `blog` | A `35.213.240.236` | DNS only | Auto |
| `links` | CNAME `brand.ludicrous.cloud` | DNS only | 1 hour |

The complete export contains 29 records: 3 A, 9 CNAME, 8 MX and 9 TXT. `go.`
is absent. The exact mail and verification values remain in the protected
export, whose SHA-256 is
`5985a2ca2a381e5d1d2b6382089f84071f4daf2b342dfa45de36a436b8ec0885`.

The zone has zero Redirect Rules, URL Rewrite Rules, Page Rules or Workers
routes. One existing account-level `Logo Redirect` rule is enabled and
protects eight `www` image URLs through the active `logoredirects` list; it is
not part of the new root-promotion redirect set. SSL/TLS is Full (strict),
Always Use HTTPS is enabled, HSTS is disabled and the Universal certificate
is active.

The 4 August provider export is the current comparison point. A fresh export
is still mandatory immediately before any later approved Phase 4 or Phase 5
Cloudflare mutation.

The signed-in HighLevel domain register confirms `go.` does not already exist.
The root is attached to one Website and 13 Funnels; `www` is redirected and
attached to the same products. Existing `trainers`, `links`, `mail`,
`r2rtraining` and incomplete `free` product mappings remain separate and must
not be changed as part of the V2 promotion.

Current HighLevel documentation identifies `sites.ludicrous.cloud` as the
manual CNAME target for a funnel/website subdomain and requires Cloudflare to
be DNS-only. The account flow did not reveal a DNS value before the action
that would begin connection, so that value must still be captured during the
explicitly approved additive `go.` connection:

<https://help.gohighlevel.com/support/solutions/articles/48001153720>

Do not infer the `go.` target from `links.`. `brand.ludicrous.cloud` is the
existing branded-link product, not the website/funnel domain target.

## Analytics Cutover Risk

| Surface | Tags observed |
|---|---|
| Current GHL root | `G-RXM7LVC0VJ`, `GTM-TMW7CS6L` |
| Website V2 | `G-W9KNRFKV5F`, `GT-TXBKBKZB` |

The governed reporting system reads the historical root GA4 property
associated with `G-RXM7LVC0VJ`. Promoting V2 without reconciling these tags can
make root traffic disappear from governed reporting or create duplicate page
views.

The protected WordPress configuration resolves the V2 ownership question:

- GA4 account `304070158`;
- GA4 property `429372468`, the same property used by governed reporting;
- web data stream `13172967030`, named `Evolved Blog`;
- measurement ID `G-W9KNRFKV5F`;
- Google tag ID `GT-TXBKBKZB`, with the V2 measurement ID as its destination;
  and
- business profile owner `info@theevolvedgym.com.au`.

This is a same-property, two-stream reconciliation problem, not an unknown
third-party tag. The governed root stream remains `G-RXM7LVC0VJ`; the existing
root Tag Manager container remains `GTM-TMW7CS6L`.

The Phase 4 target is one accepted root `page_view` in the historical root
stream. In the isolated clone:

1. Preserve the V2 stream and ownership record; do not delete the stream,
   Site Kit or its historical data.
2. Disable only the V2 front-end tag placement in the clone.
3. Reproduce the governed root analytics setup using the existing root stream
   and Tag Manager container;
4. use Tag Assistant, browser network evidence and GA4 Realtime/DebugView to
   prove one—and only one—accepted root page view with exact host
   `theevolvedgym.com.au`; and
5. prove the Operating Data Hub receives the root hostname before the
   production promotion is proposed.

If the governed container itself emits more than one GA4 configuration/page
view, stop and repair it in the isolated rehearsal. Do not carry both V2 and
root page-view sources into production.

## Isolated Root-Host Rehearsal

### Isolation

1. Restore a fresh copy of the Phase 1 WordPress filesystem and SQL snapshot.
2. Place the clone behind an allowlist and authentication.
3. Disable outbound email, cron-driven callbacks, webhooks, indexing and
   production form submission.
4. Present `https://theevolvedgym.com.au` and
   `https://blog.theevolvedgym.com.au` only inside the test runner through a
   private host override and TLS-terminating proxy. Public DNS remains
   unchanged.
5. Capture the clone's file hashes, database hash and starting options before
   changing it.

The rehearsal must use the existing V2 release. It must not rebuild the
homepage or use the GHL homepage as source material.

### WordPress change set

1. Change cloned `siteurl` and `home` from
   `http://blog.theevolvedgym.com.au` to
   `https://theevolvedgym.com.au`.
2. Run serialized-safe, dry-run-first WordPress replacements for both
   `http://blog.theevolvedgym.com.au` and
   `https://blog.theevolvedgym.com.au`, excluding immutable GUID history.
3. Replace hardcoded theme media hosts with relative or WordPress-generated
   URLs; do not rely on the transitional `blog.` hostname.
4. After `go.` passes, change the five homepage waitlist destinations directly
   to `https://go.theevolvedgym.com.au/[same-path]`. Keep the 19 root
   redirects for old emails, ads, bookmarks and external links.
5. Change the homepage footer to `/legal/` and `/blog/`.
6. Create a WordPress page with slug `blog` and set it as `page_for_posts`.
   Do not change `/%postname%/` during root promotion.
7. Confirm root canonical, Open Graph URL, sitemap URLs, media URLs and the
   homepage title. The current `Home - Blog` title is not acceptable for the
   root release.
8. Reconcile analytics without duplicate page views.
9. Flush WordPress, SiteGround and edge caches only inside the rehearsal.

Every changed row, file and generated URL must be included in the rehearsal
evidence. A global SQL text replacement or a search-replace that modifies GUID
history is not accepted.

### GHL change set for Phase 4 approval

1. Read the exact domain records displayed by the account connection flow.
2. Connect `go.theevolvedgym.com.au` as a funnel/website domain without
   removing the current root binding.
3. Link all captured funnels and the main GHL website so all 85 registered
   paths remain available on `go.`.
4. Verify the Pregnancy organic funnel resolves through
   `/pppsa-page-1536`, then decide the stale `/pppsa-5667` alias separately.
5. Test the five organic forms with owned test contacts and uniquely
   identifiable values.
6. Verify the matching intake, Lead Source guard, delivery workflow, thank-you
   page, calendar and confirmation for each test.
7. Test paid pages only under a separately approved dormant-campaign test;
   do not activate campaigns.
8. Update only the seven intentional GHL custom-value/template destinations
   after the matching `go.` pages pass.

### Root route rules

- The 16 WordPress paths are served by WordPress with no redirect.
- The 19 operational paths redirect once to the same path on `go.` and
  preserve query strings.
- The two technical paths are served by WordPress.
- `/terms-of-use-and-privacy-policy` redirects once to `/legal/`.
- No catch-all root-to-`go.` rule is allowed.

### `blog.` rules

The existing `scripts/redirects.conf` wildcard is unsafe and must not be
installed.

The rehearsal must use host-conditional rules that:

- redirect the `blog.` homepage to the root homepage;
- redirect an existing WordPress page or Results URL to the same path on the
  root;
- redirect the published article to the same current root-level article path;
- preserve `/wp-content/`, `/wp-includes/`, `/wp-json/`, administration and
  login behavior until hardcoded dependencies and non-GET requests are clear;
- redirect sitemap requests directly to the matching root sitemap;
- provide deliberate `robots.txt` behavior; and
- leave any unmapped URL available for review rather than forcing it under
  `/blog/`.

There must be no blanket
`blog.theevolvedgym.com.au/(.*) → theevolvedgym.com.au/blog/$1` rule.

## Rehearsal Acceptance

The isolated rehearsal passes only when:

- all governed V2 files match the release baseline except the documented
  hostname, link, Blog, legal and analytics repair set;
- the homepage and all 61 captured WordPress routes render on the private root
  host;
- all 35 Results stories and the published article remain accessible;
- all 85 GHL paths are present on `go.` or have an explicit, approved
  exception;
- all five organic submissions complete their exact workflows and booking
  transitions;
- the Pregnancy journey reaches `/pppsa-page-1536` and continues to the
  existing booking-confirmation step;
- `/blog/`, `/legal/` and the old legal redirect pass;
- assets, API, sitemap and robots behavior pass on both root and `blog.`;
- redirects are single hop, query-safe and loop-free;
- governed analytics records one root page view without duplication;
- no production integration fires from the WordPress clone; and
- rollback is completed and timed successfully.

## Rollback Contract

The rehearsal and production cutover use the same rollback order:

1. Stop further traffic changes.
2. Restore the exact provider-side root and `www` DNS configuration captured
   immediately before the change.
3. Restore the GHL root-domain association if it was removed; keep `go.` only
   if it is additive and healthy.
4. Remove only the new root and `blog.` redirect rules.
5. Restore WordPress `siteurl` and `home` to their exact pre-cutover values.
6. Restore the pre-cutover WordPress database and files if any content,
   serialized data or runtime behavior differs.
7. Purge relevant caches.
8. Verify the old GHL root, the live V2 `blog.` runtime, all five organic
   pages, Strength Assessment and `links.`.
9. Record elapsed time, DNS answers, HTTP results and recovery hashes.

The Phase 1 snapshot is not overwritten. A fresh pre-cutover snapshot is an
additional recovery point.

## Gates Remaining Before Phase 4

Phase 4 still requires explicit owner approval because it creates an isolated
staging surface and changes GHL/DNS configuration for `go.`.

Before that approval is exercised:

- capture the account-specific HighLevel DNS value during the separately
  approved additive `go.` connection;
- prove the owner-confirmed Pregnancy funnel route with an owned test contact
  and preserve the stale `/pppsa-5667` alias until its separate disposition is
  approved;
- apply the documented same-property analytics reconciliation only inside the
  approved isolated rehearsal;
- preserve the paid-page form mismatch as a separate controlled defect; and
- preserve every existing HighLevel domain, funnel, form, workflow and route.

The protected trainer, article, legacy-host and Results improvement backlogs
remain intact and are not absorbed into root promotion.
